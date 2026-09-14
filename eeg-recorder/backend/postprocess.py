#!/usr/bin/env python3
"""postprocess.py -- what happens after a recording stops: QC, strip, upload.

ONE WORKER, ONE RUN AT A TIME. Stripping reads the whole recording and hashes it
twice; two of those at once would compete for the same NVMe the amplifiers write
to. The queue is the point, not a limitation.

THE ORDER IS NOT NEGOTIABLE, AND THE REASON IS SCIENTIFIC, NOT TECHNICAL

    QC BUNDLE  ->  STRIP  ->  UPLOAD

    `core/criteria.py` derives every verdict in this project against WIRE-FREE
    AMPLIFIER INPUTS RECORDED IN THE SAME FILE -- sites /3../16 and /35../48 in a
    two-role cohort. The strip keeps only the wired channels, so it DELETES THAT
    FLOOR, and `compute_features` afterwards exits with "N expected sites are not
    in this file's biointerface_map". Demonstrated on 2026-09-11, not assumed.

    So the cached features are the ONLY surviving record of the floor, and they
    must be computed BEFORE the strip and travel WITH it. A stripped recording
    that reaches the NAS without its bundle can never be QC'd again by this
    project's own criterion. That is why a missing bundle is a refusal by default
    rather than a warning.

EVERY STAGE IS RESUMABLE AND NOTHING IS EVER DELETED LOCALLY. A service restart
mid-upload continues; it does not start over. The original 262-channel recording
stays where Allego wrote it, and removing it is a human decision taken after
reading the manifest.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from typing import Callable

import runs as R
import nas_upload
import naming


def _cfg():
    import presets as _P
    return _P.load()

ANALYSIS = Path(os.environ.get(
    "EEG_ANALYSIS_DIR",
    Path(__file__).resolve().parents[2] / "eeg-emg-analysis"))
# The only interpreter that has BOTH numpy and radiens. The stripper itself is
# numpy+stdlib, but keeping one interpreter for every stage avoids a second
# environment drifting out of step.
PYTHON = os.environ.get("EEG_RECORDER_PYTHON",
                        "/opt/neurosurveillance/venv/bin/python3")


class PostprocessError(RuntimeError):
    pass


def qc_cache_path(base_name: str) -> Path:
    from importlib import import_module
    sys.path.insert(0, str(ANALYSIS))
    paths = import_module("core.paths")
    return Path(paths.CACHE_ROOT) / f"{base_name}.npz"


def has_qc_bundle(base_name: str) -> bool:
    return qc_cache_path(base_name).exists()


def layout_of(run):
    """The RigLayout this run declared, or None for a run made before layouts."""
    import presets as _P
    import layout as _L
    d = getattr(run, "layout", None) or {}
    if not d.get("setting"):
        return None
    try:
        # from_dict reads the roles the RUN carries, so a run whose setting was
        # custom -- or has since been renamed or deleted -- still resolves.
        return _L.from_dict(_P.load(), d)
    except Exception:
        return None


def roles_for_run(run) -> tuple[str, ...] | None:
    """The role list the QC engine needs, in site order.

    cards/ladder.py takes only `roles` from a manifest to build the spec; every
    animal id and placement field exists to LABEL the output, not to compute it.

    Returns None when this project's ladder does not describe the layout -- the
    unipolar case -- so the chain records `qc_not_applicable` rather than
    demanding an override nobody can satisfy.
    """
    lay = layout_of(run)
    if lay is not None:
        if not lay.setting.qc_applies:
            return None
        return tuple(sorted(lay.setting.roles, key=lambda r: lay.setting.roles[r]))

    # A run recorded before layouts existed. Its `preset` still names a template.
    import presets as _P
    try:
        cfg = _P.load()
        st = cfg.setting(cfg.template(run.preset).setting)
    except Exception:
        return None
    return None if not st.qc_applies else tuple(
        sorted(st.roles, key=lambda r: st.roles[r]))


def qc_applies_to_run(run) -> bool:
    """Does this project's verdict ladder describe this run's layout at all?

    False is not a waiver. It says the recording was never judgeable by this
    project's criterion, which is a different claim from "we chose to skip the
    check". Before this existed the chain asked for a manual override on EVERY
    unipolar run -- a guard that could never be satisfied, and therefore one
    people would learn to click past on the runs where it matters.

    Unknown layouts return True, so a config typo fails closed.
    """
    lay = layout_of(run)
    if lay is not None:
        return lay.setting.qc_applies
    import presets as _P
    try:
        cfg = _P.load()
        return cfg.setting(cfg.template(run.preset).setting).qc_applies
    except Exception:
        return True


def write_run_manifest(run, roles: tuple[str, ...], out_dir: Path | None = None) -> Path:
    """Build a cohort manifest FROM THE RUN ITSELF. No human step.

    WHY THIS EXISTS. The first real 24 h recording was blocked because its eight
    mice were a new batch with no hand-written cohort manifest. That was a design
    error: a mouse id is an arbitrary label that people invent constantly, and
    requiring an identity document before quality control can run makes every new
    animal a blocker. The console already knows the layout (from the preset) and
    the identities (from the slots the operator filled in), so the manifest is
    generated rather than demanded.

    Husbandry is deliberately absent. It is not known here, and an invented
    surgery date is worse than a missing one.
    """
    import yaml as _yaml
    out_dir = Path(out_dir) if out_dir else (
        Path(os.environ.get("EEG_RECORDER_STATE",
                            Path.home() / ".local" / "state" / "eeg-recorder")) / "cohorts")
    out_dir.mkdir(parents=True, exist_ok=True)
    # LOCAL date, from the uid in the recording's own name. run.actual_start is
    # UTC and would date an 08:55 KST recording to the previous day.
    from nas_upload import local_date_from_base
    date = local_date_from_base(run.base_name or "", run.actual_start)
    cohort_id = f"auto-{run.run_id}"
    # 🔑 THE MANIFEST SPEAKS THE ANALYSIS SIDE'S VOCABULARY. A port without a
    # splitter is slot `A` to the operator and position `A1` everywhere
    # downstream -- ladder.find_processed and figs_common.pos_to_file both parse
    # position[1]. Translate once, here, and record BOTH names so nobody has to
    # infer the mapping from a card six months from now.
    import layout as _L
    animals = []
    for slot, v in sorted((run.slots or {}).items()):
        mid = (v or {}).get("mouse_id")
        if not mid:
            continue
        pos = _L.RigLayout.to_position(slot)
        animals.append({
            "animal_id": mid, "batch_id": cohort_id,
            "placements": [{"from": date, "position": pos, "console_slot": slot,
                            "source": "recording-console"}],
            "recordings": [{"base": run.base_name, "date": date,
                            "position": pos, "role": "animal"}],
        })
    lay = layout_of(run)
    doc = {
        "cohort_id": cohort_id,
        "title": f"auto-generated from run {run.run_id} ({run.owner})",
        "project_id": "neurosurveillance-eeg",
        "description": (
            "GENERATED BY THE RECORDING CONSOLE, not hand-written. Animal ids and "
            "positions are exactly what the operator entered before the run; "
            "husbandry is absent because it is not known here. The QC engine uses "
            "only `roles` from this file -- everything else labels the cards."),
        "roles": list(roles),
        # How many amplifier chips each port carries: 2 behind a splitter, 1
        # without. Absent on runs made before layouts existed, which then get
        # the historical four-ports-of-two assumption.
        **({"ports": lay.cohort_ports()} if lay is not None else {}),
        **(lay.cohort_extras() if lay is not None else {}),
        "criterion": "slope",
        "animals": animals,
        "recordings": [{"base": run.base_name, "date": date}],
    }
    path = out_dir / f"{cohort_id}.yaml"
    path.write_text(_yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))
    return path


def compute_qc_bundle(run, *, progress=None) -> tuple[bool, str]:
    """Compute the QC bundle for a run, with no human step. (ok, detail)."""
    say = progress or (lambda m: None)
    roles = roles_for_run(run)
    if roles is None:
        return False, (
            f"layout {run.preset!r} has no floor model, so CohortSpec's floor "
            "model does not apply to it and a QC bundle cannot be computed "
            "automatically without risking the wrong control sites.")
    manifest = write_run_manifest(run, roles)
    cache = qc_cache_path(run.base_name)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cmd = [PYTHON, "cards/ladder.py", run.base_path or run.base_name,
           "--cohort", str(manifest), "--cache", str(cache)]
    # SCORE ONLY THE SLOTS THAT HOLD AN ANIMAL. Without this, ladder.py falls back
    # to `spec.positions()` -- all eight, whatever the operator filled in -- and a
    # four-mouse run comes back with four extra `UNKNOWN@B2` cards built from
    # amplifier inputs with nothing plugged into them. Measured 2026-09-13: such a
    # card can read PASS at rung 2, so the noise is not self-evidently noise.
    # Empty slots never contaminate the floor itself (floor sites are /3../16 and
    # /35../48, which no slot occupies), so this only removes false cards.
    if run.occupied:
        import layout as _L
        cmd += ["--positions",
                ",".join(sorted(_L.RigLayout.to_position(s) for s in run.occupied))]
    say(f"  computing QC bundle: roles={roles}, manifest={manifest.name}, "
        f"positions={','.join(sorted(run.occupied)) or 'all'}")
    env = dict(os.environ, PYTHONPATH=str(ANALYSIS))
    r = subprocess.run(cmd, cwd=ANALYSIS, env=env, capture_output=True, text=True)
    if r.returncode != 0 or not cache.exists():
        return False, (f"cards/ladder.py exited {r.returncode} and no cache was "
                       f"written:\n{(r.stderr or r.stdout)[-1500:]}")
    return True, f"computed from the run's own preset ({', '.join(roles)})"


def _duration_s(run) -> float | None:
    """Recorded duration in seconds, or None if the run never really started."""
    from datetime import datetime
    try:
        a = datetime.fromisoformat(run.actual_start.replace("Z", "+00:00"))
        b = datetime.fromisoformat(run.actual_stop.replace("Z", "+00:00"))
        return (b - a).total_seconds()
    except Exception:
        return None


def strip(run: R.Run, *, out_dir: str | Path | None = None,
          progress: Callable[[str], None] | None = None) -> dict:
    """Run the stripper as a subprocess and return its report.

    A subprocess rather than an import: the stripper is a long CPU+IO job, and
    keeping it out of the service's address space means a crash in it cannot take
    the API down mid-recording.
    """
    say = progress or (lambda m: None)
    if not run.base_path:
        raise PostprocessError(f"run {run.run_id} has no recorded base_path")
    cmd = [PYTHON, "-m", "convert.strip_channels", run.base_path,
           "--keep-labels", ",".join(run.keep_labels),
           "--verify", "full", "--require-idle"]
    if run.with_gpio:
        cmd.append("--with-gpio")
    if out_dir:
        cmd += ["--out", str(out_dir)]
    say(f"  {' '.join(cmd[:4])} ... ({len(run.keep_labels)} labels)")
    env = dict(os.environ, PYTHONPATH=str(ANALYSIS))
    p = subprocess.run(cmd, cwd=ANALYSIS, env=env, capture_output=True, text=True)
    if p.returncode != 0:
        raise PostprocessError(
            f"strip_channels exited {p.returncode}:\n{(p.stderr or p.stdout)[-2000:]}")
    from importlib import import_module
    sys.path.insert(0, str(ANALYSIS))
    paths = import_module("core.paths")
    root = Path(out_dir) if out_dir else Path(paths.STRIPPED_ROOT)
    report = root / f"{run.base_name}.strip-report.json"
    if not report.exists():
        raise PostprocessError(f"strip reported success but {report} is missing")
    return json.loads(report.read_text())


class Worker:
    """The post-stop chain, on one background thread."""

    def __init__(self, store: R.RunStore, *,
                 require_qc_bundle: bool = True,
                 auto_compute_qc: bool = True,
                 on_event: Callable[[str], None] | None = None):
        self.store = store
        self.require_qc_bundle = require_qc_bundle
        self.auto_compute_qc = auto_compute_qc
        self.log = on_event or (lambda m: print(f"[postprocess] {m}", flush=True))
        self._q: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.current: str | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="postprocess",
                                        daemon=True)
        self._thread.start()
        # Anything left waiting from a previous life goes back in the queue. A
        # NAS outage across a restart must not strand a finished run.
        for state in (R.STOPPED, R.QC, R.STRIPPED, R.UPLOAD_PENDING):
            for run in self.store.list(states=(state,), limit=50):
                self.submit(run.run_id)
        self.log("worker armed")

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        self._q.put(None)
        if self._thread:
            self._thread.join(timeout)

    def submit(self, run_id: str) -> None:
        self._q.put(run_id)

    def _loop(self) -> None:
        while not self._stop.is_set():
            run_id = self._q.get()
            if run_id is None:
                return
            self.current = run_id
            try:
                self.process(run_id)
            except Exception:
                self.log(f"{run_id}: chain raised:\n{traceback.format_exc()}")
            finally:
                self.current = None

    # ---- the chain ------------------------------------------------------ #
    def process(self, run_id: str) -> R.Run:
        run = self.store.get(run_id)

        if run.state == R.STOPPED:
            run = self._qc(run)
        if run.state == R.QC:
            run = self._strip(run)
        if run.state == R.STRIPPED:
            run = self.store.transition(run.run_id, R.UPLOAD_PENDING,
                                        detail="ready to upload")
        if run.state == R.UPLOAD_PENDING:
            run = self._upload(run)
        return run

    def _qc(self, run: R.Run) -> R.Run:
        """Check the feature cache exists. This does NOT compute it.

        Computing the ladder cache takes tens of minutes on a 24 h recording and
        needs a cohort spec that only a person can supply, so it is not something
        to do silently behind someone's back. The chain refuses and says exactly
        which command to run.

        THE OVERRIDE IS PER-RUN AND RECORDED ON THE RUN. An earlier version
        flipped `self.require_qc_bundle` on the shared worker, which silently
        disabled the guard for EVERY subsequent run until the service restarted,
        and left no trace that it had happened. A guard that one click can switch
        off for the whole lab, invisibly, is not a guard. The override now lives
        in the run's own results, so it applies to exactly one recording and the
        run record says plainly that the data travelled without its floor.
        """
        present = has_qc_bundle(run.base_name or "")
        if present:
            self.log(f"{run.run_id}: QC bundle present")
            return self.store.transition(run.run_id, R.QC, detail="QC bundle present",
                                         results={"qc_bundle": str(qc_cache_path(run.base_name))})

        # NO CRITERION FOR THIS LAYOUT. Distinct from a waiver, and recorded as
        # such: `qc_not_applicable` says the recording was never judgeable by
        # this project's criterion, where `qc_bundle_skipped` says a person chose
        # to send data without its floor. Reading the second as the first later
        # would turn a deliberate exception into an apparent routine.
        if not qc_applies_to_run(run):
            self.log(f"{run.run_id}: preset {run.preset!r} declares no QC "
                     "criterion -- no bundle is expected or possible")
            return self.store.transition(
                run.run_id, R.QC,
                detail=(f"layout {run.preset!r} declares `qc: none`: this "
                        "project's floor model does not describe its layout, so "
                        "no bundle exists to lose"),
                results={"qc_bundle": None, "qc_not_applicable": True})

        # NO BUNDLE YET: compute it, rather than blocking on a human.
        # A new mouse id must never stop the pipeline -- people introduce animals
        # constantly, and the QC engine does not care what they are called.
        if self.auto_compute_qc:
            self.log(f"{run.run_id}: no QC bundle, computing one")
            ok, detail = compute_qc_bundle(run, progress=self.log)
            if ok:
                self.log(f"{run.run_id}: QC bundle {detail}")
                return self.store.transition(
                    run.run_id, R.QC, detail=f"QC bundle computed -- {detail}",
                    results={"qc_bundle": str(qc_cache_path(run.base_name)),
                             "qc_bundle_auto": True})
            self.log(f"{run.run_id}: could not compute a QC bundle -- {detail}")

        override = bool((run.results or {}).get("skip_qc_bundle"))
        if override or not self.require_qc_bundle:
            self.log(f"{run.run_id}: WARNING, proceeding WITHOUT a QC bundle. This "
                     "recording's wire-free floor will not survive the strip.")
            return self.store.transition(
                run.run_id, R.QC,
                detail="no QC bundle -- EXPLICITLY OVERRIDDEN for this run",
                results={"qc_bundle": None, "qc_bundle_skipped": True})

        # A recording too short to clear rung 2's unbroken-block bar cannot
        # produce a meaningful ladder anyway, so say so rather than sending
        # someone off to run a command that will not help them.
        short = ""
        dur_s = _duration_s(run)
        if dur_s is not None and dur_s < 15 * 60:
            short = (f" NOTE: this recording is only {dur_s / 60:.1f} min long, which "
                     "is below the 15 min unbroken-block bar the verdict ladder gates "
                     "on, so a QC bundle for it would not be meaningful. If this was a "
                     "test, either abandon the run or strip it with the override.")
        msg = (
            f"no QC bundle for {run.base_name}. Stripping removes the in-file "
            "wire-free floor, after which core/criteria.py can never judge this "
            "recording again, so the cached features are the only surviving "
            f"record of it.{short} Compute it with:\n"
            f"  cd {ANALYSIS} && PYTHONPATH=. {PYTHON} cards/ladder.py "
            f"{run.base_name} --cohort <id> --cache {qc_cache_path(run.base_name)}")
        self.log(f"{run.run_id}: HELD -- {msg}")
        return self.store.fail(run.run_id, "QC", msg)

    def _strip(self, run: R.Run) -> R.Run:
        self.log(f"{run.run_id}: stripping {run.base_name} "
                 f"-> {len(run.keep_labels)} channels")
        self.store.transition(run.run_id, R.STRIPPING, detail="strip_channels")
        try:
            rep = strip(run, progress=self.log)
        except Exception as exc:
            self.log(f"{run.run_id}: STRIP FAILED -- {exc}")
            return self.store.fail(run.run_id, "STRIP", str(exc))
        plan = rep.get("plan", {})
        self.log(f"{run.run_id}: stripped, {plan.get('saving_pct')}% smaller")
        return self.store.transition(
            run.run_id, R.STRIPPED, detail="verified bit-exact",
            results={"strip": {"dst_base": rep.get("dst_base"),
                               "saving_pct": plan.get("saving_pct"),
                               "bytes_out": plan.get("bytes_out"),
                               "dataset_checksum": rep.get("dataset_checksum")}})

    def _upload(self, run: R.Run) -> R.Run:
        st = nas_upload.nas_status()
        if not st["ok"]:
            # NOT a failure. The run rests here and the next sweep retries.
            self.log(f"{run.run_id}: NAS unavailable ({st.get('hint')}); "
                     "staying in UPLOAD_PENDING")
            return run
        dst = (run.results.get("strip") or {}).get("dst_base")
        if not dst:
            return self.store.fail(run.run_id, "UPLOAD",
                                   "no stripped output recorded for this run")
        # THE FOLDER NAME IS CHOSEN ONCE AND THEN FROZEN ON THE RUN. A resumed
        # upload must land in the folder it started in; recomputing the free name
        # every attempt would walk a half-uploaded run into `-2`, `-3`, ... and
        # leave partial copies scattered behind it.
        try:
            names = naming.run_names(run, _cfg())
            if run.nas_dir:
                folder = run.nas_dir
                stem = names["file_base"]
                if names["renamed"]:
                    # keep the file base consistent with the frozen folder,
                    # including any collision suffix it picked up
                    stem = f"{folder}_{naming.n_mice(run.slots)}mice"
            elif names["renamed"]:
                folder, n = nas_upload.free_dir_name(run.owner, names["folder"])
                stem = f"{folder}_{naming.n_mice(run.slots)}mice"
                if n > 1:
                    self.log(f"{run.run_id}: {names['folder']!r} already exists on "
                             f"the NAS; using {folder!r}")
                run = self.store.transition(run.run_id, run.state, nas_dir=folder,
                                            detail=f"NAS folder reserved: {folder}")
            else:
                folder, stem = names["folder"], names["file_base"]
        except (naming.NamingError, nas_upload.UploadRefused) as exc:
            self.log(f"{run.run_id}: cannot name the destination -- {exc}")
            return self.store.fail(run.run_id, "UPLOAD", str(exc))

        self.store.transition(run.run_id, R.UPLOADING, detail=f"uploading to {folder}")
        qc = run.results.get("qc_bundle")
        try:
            summary = nas_upload.upload_recording(
                dst, run.owner, run_json=run.to_dict(),
                qc_bundle=[qc] if qc else (),
                dest_name=folder, file_base=stem, progress=self.log)
        except nas_upload.UploadRefused as exc:
            self.log(f"{run.run_id}: upload refused ({exc}); back to UPLOAD_PENDING")
            return self.store.transition(run.run_id, R.UPLOAD_PENDING,
                                         detail=f"refused: {exc}")
        except Exception as exc:
            self.log(f"{run.run_id}: UPLOAD FAILED -- {exc}")
            return self.store.fail(run.run_id, "UPLOAD", str(exc))
        if summary["status"] != "VERIFIED":
            return self.store.fail(
                run.run_id, "UPLOAD",
                f"{summary['files_size_only']} file(s) were SIZE_ONLY, not verified")
        self.log(f"{run.run_id}: DONE -> {summary['dest']}")
        return self.store.transition(run.run_id, R.DONE, detail="uploaded and verified",
                                     results={"upload": summary})

#!/usr/bin/env python3
"""postprocess.py -- what happens after a recording stops: QC, strip, per-mouse
CSV export, upload.

ONE WORKER, ONE RUN AT A TIME. Stripping reads the whole recording and hashes it
twice; two of those at once would compete for the same NVMe the amplifiers write
to. The queue is the point, not a limitation.

THE ORDER IS NOT NEGOTIABLE, AND THE REASON IS SCIENTIFIC, NOT TECHNICAL

    QC BUNDLE  ->  STRIP  ->  PER-MOUSE CSV  ->  UPLOAD

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

WHAT REACHES THE NAS (since 2026-09-29) is one CSV + info.json per mouse, in
02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSEID>_<B|R>/.
The analysis reads the CSV; the stripped xdat stays on this machine and the raw
goes off-site to S3 and the bilab NAS (see 02-procedures/backup-architecture).

EVERY STAGE IS RESUMABLE. A service restart mid-upload continues; it does not
start over. The ONE thing deleted locally is the per-mouse CSVs this worker made,
and only after every one of a run's CSVs verified on the NAS: about 58 GB per
36 h run, regenerable from the stripped file. The original 262-channel recording
and the stripped copy stay where they are, and removing either is a human
decision.
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
PER_MOUSE_ROOT = Path(os.environ.get(
    "EEG_PER_MOUSE_ROOT", Path.home() / "radix" / "per-mouse"))


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


def export_spec(run: R.Run, cfg=None) -> dict:
    """What the CSV exporter needs: for each occupied slot, its file name and the
    site label carrying each role.

    Built from the run's OWN layout record (`run.layout["roles"]`), not from the
    current config, so a run stays exportable after its setting is renamed or
    deleted -- the reason the layout is stored self-describing in the first place.
    """
    import layout as LY
    cfg = cfg or _cfg()
    roles = (run.layout or {}).get("roles") or {}
    if not roles:
        raise PostprocessError(f"run {run.run_id} has no role map in its layout record")
    names = naming.mouse_folders(run, cfg)
    pairing = (run.results or {}).get("pairing") or {}
    mice = []
    for slot, e in names.items():
        base = LY.RigLayout.base_of(slot)
        port = slot[0]
        cols = {role: f"{port}/{base - 1 + int(off)}"
                for role, off in sorted(roles.items(), key=lambda kv: int(kv[1]))}
        mice.append({"slot": slot, "position": LY.RigLayout.to_position(slot),
                     "mouse_id": e["mouse_id"], "recording_type": e["recording_type"],
                     "condition": e["condition_dir"], "batch": e["batch"],
                     "file_base": e["file_base"], "columns": cols,
                     **({"pairing": pairing[slot]} if slot in pairing else {})})
    window = (run.results or {}).get("window")
    return {"mice": mice, **({"window": window} if window else {}),
            "meta": {"run_id": run.run_id, "owner": run.owner, "batch": run.batch_name,
                     "layout_setting": (run.layout or {}).get("setting"),
                     "headstage": (run.layout or {}).get("headstage"),
                     "raw_base_path": run.base_path}}


def export_csv(run: R.Run, *, out_root: Path | None = None,
               progress: Callable[[str], None] | None = None) -> dict:
    """Run export/per_mouse_csv.py as a subprocess and return its report."""
    say = progress or (lambda m: None)
    dst = (run.results.get("strip") or {}).get("dst_base")
    if not dst:
        raise PostprocessError(f"run {run.run_id} has no stripped output recorded")
    spec = export_spec(run)
    out = Path(out_root or PER_MOUSE_ROOT) / run.base_name
    out.mkdir(parents=True, exist_ok=True)
    spec_path = out / "spec.json"
    spec_path.write_text(json.dumps(spec, indent=2))
    cmd = [PYTHON, "-m", "export.per_mouse_csv", dst, "--spec", str(spec_path),
           "--out", str(out), "--require-idle"]
    if run.base_path:
        cmd += ["--source-base", run.base_path]
    say(f"  export.per_mouse_csv {run.base_name} ({len(spec['mice'])} mice)")
    env = dict(os.environ, PYTHONPATH=str(ANALYSIS))
    p = subprocess.run(cmd, cwd=ANALYSIS, env=env, capture_output=True, text=True)
    if p.returncode != 0:
        raise PostprocessError(
            f"per_mouse_csv exited {p.returncode}:\n{(p.stderr or p.stdout)[-2000:]}")
    report = out / f"{run.base_name}.per-mouse-report.json"
    if not report.exists():
        raise PostprocessError(f"export reported success but {report} is missing")
    rep = json.loads(report.read_text())
    want = {m["file_base"] for m in spec["mice"]}
    got = {m["file_base"] for m in rep.get("mice", [])}
    if want != got:
        raise PostprocessError(f"export report covers {sorted(got)}, spec asked for {sorted(want)}")
    return {"report": str(report), "out_dir": str(out), "spec": spec, "rep": rep}


def card_path(run: R.Run, position: str) -> Path:
    """Where compute_qc_bundle's ladder run left this animal's card."""
    return ANALYSIS / "cards" / "out" / f"auto-{run.run_id}" / f"{run.base_name}__{position}_card.json"


def mouse_qc(run: R.Run, position: str) -> dict:
    """The ladder's verdict for one mouse, for its info.json. Never raises: a
    missing card is recorded as NOT ASSESSED, with the reason."""
    import qc_info
    p = card_path(run, position)
    card = qc_info.load_card(p)
    if card is None:
        why = ("this layout declares `qc: none`" if (run.results or {}).get("qc_not_applicable")
               else "the QC bundle was waived for this run" if (run.results or {}).get("qc_bundle_skipped")
               else f"no card at {p}")
        return {"verdict": "NOT ASSESSED", "why": why, "how_to_read": qc_info.HOW_TO_READ}
    return qc_info.qc_block(card, card_path=str(p), judged_on="whole recording")


def mouse_info(rep: dict, row: dict, spec_mouse: dict, entry: dict,
               qc: dict | None = None) -> dict:
    """The info.json for one mouse, before its upload section is added."""
    return {
        "mouseID": spec_mouse["mouse_id"], "batch": entry["batch"],
        "condition": entry["condition_dir"], "recording_type": spec_mouse["recording_type"],
        "folder": entry["folder"], "position": spec_mouse["position"],
        "slot": spec_mouse["slot"], "port": spec_mouse["slot"][0],
        "channels": spec_mouse["columns"], "csv_columns":
            ["timestamp_raw", "timestamp_sec", "datetime_kst", *row["roles"]],
        "units": "uV", "samplingRate": rep["samplingRate"],
        "startTime_utc": rep["startTime_utc"], "startTime_kst": rep["startTime_kst"],
        "n_samples": rep["n_samples"], "duration_h": rep["duration_h"],
        "timestamp_raw_first": rep["timestamp_raw_first"],
        "timestamp_raw_last": rep["timestamp_raw_last"],
        "csv_sha256": row["sha256"], "csv_bytes": row["bytes"], "csv_verify": row["verify"],
        "allego_base": rep["allego_base"],
        "stripped_dataset_checksum": rep["stripped_dataset_checksum"],
        "source": rep["source"], "run": rep.get("meta") or {},
        "exporter": {"tool": rep["tool"], "version": rep["version"],
                     "git_commit": rep["git_commit"], "utc": rep["utc"]},
        "window": rep.get("window"),
        "recording_file": rep.get("file"),
        **({"pairing": spec_mouse["pairing"]} if spec_mouse.get("pairing") else {}),
        **({"qc": qc} if qc else {}),
        **({"suffix_reason": entry["suffix_reason"]} if entry.get("suffix_reason") else {}),
    }


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
        for state in (R.STOPPED, R.QC, R.STRIPPED, R.EXPORTED, R.UPLOAD_PENDING):
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
            run = self._export(run)
        if run.state == R.UPLOAD_PENDING and not (run.results or {}).get("export"):
            # left here by the pre-2026-09-29 service, which uploaded the xdat
            run = self._export(run)
        if run.state == R.EXPORTED:
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
        auto_failed = ""        # why the automatic computation could not run
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
            # Keep WHY on the run. Without this the operator sees only the
            # generic hold message and the actual cause -- "duplicate animal_id
            # dfdf" -- lives in the journal, where nobody looks first.
            auto_failed = detail

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
        why = auto_failed or ""
        if why:
            why = ("\n\nAUTOMATIC COMPUTATION FAILED, and this is the reason:\n  "
                   + why.strip().replace("\n", "\n  ") + "\n")
        dur_s = _duration_s(run)
        if dur_s is not None and dur_s < 15 * 60:
            short = (f" NOTE: this recording is only {dur_s / 60:.1f} min long, which "
                     "is below the 15 min unbroken-block bar the verdict ladder gates "
                     "on, so a QC bundle for it would not be meaningful. If this was a "
                     "test, either abandon the run or strip it with the override.")
        msg = (
            f"no QC bundle for {run.base_name}.{why} Stripping removes the in-file "
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

    def _export(self, run: R.Run) -> R.Run:
        self.log(f"{run.run_id}: exporting per-mouse CSVs from {run.base_name}")
        self.store.transition(run.run_id, R.EXPORTING, detail="per_mouse_csv")
        try:
            ex = export_csv(run, progress=self.log)
        except (PostprocessError, naming.NamingError) as exc:
            self.log(f"{run.run_id}: EXPORT FAILED -- {exc}")
            return self.store.fail(run.run_id, "EXPORT", str(exc))
        rep = ex["rep"]
        total = sum(m["bytes"] for m in rep["mice"])
        self.log(f"{run.run_id}: exported {len(rep['mice'])} mice, {total / 1e9:.1f} GB")
        return self.store.transition(
            run.run_id, R.EXPORTED, detail=f"{len(rep['mice'])} CSVs verified",
            results={"export": {"report": ex["report"], "out_dir": ex["out_dir"],
                                "n_mice": len(rep["mice"]), "bytes": total}})

    def _upload(self, run: R.Run) -> R.Run:
        st = nas_upload.nas_status()
        if not st["ok"]:
            # NOT a failure. The run rests here until a retry or a restart.
            self.log(f"{run.run_id}: NAS unavailable ({st.get('hint')}); "
                     "staying in UPLOAD_PENDING")
            return run
        ex = (run.results or {}).get("export") or {}
        try:
            rep = json.loads(Path(ex["report"]).read_text())
            spec = json.loads((Path(ex["out_dir"]) / "spec.json").read_text())
        except Exception as exc:
            return self.store.fail(run.run_id, "UPLOAD",
                                   f"the per-mouse export record is unreadable: {exc}")
        by_fb = {m["file_base"]: m for m in rep["mice"]}

        # THE FOLDER NAMES ARE CHOSEN ONCE AND THEN FROZEN ON THE RUN. A resumed
        # upload must land in the folders it started in; recomputing the free name
        # every attempt would walk a half-uploaded mouse into `-2`, `-3`...
        dirs = (run.results or {}).get("nas_mouse_dirs")
        if not dirs:
            try:
                names = naming.mouse_folders(run, _cfg())
                dirs = {slot: nas_upload.free_mouse_folder(run.owner, e)
                        for slot, e in names.items()}
            except (naming.NamingError, nas_upload.UploadRefused) as exc:
                self.log(f"{run.run_id}: cannot name the destination -- {exc}")
                return self.store.fail(run.run_id, "UPLOAD", str(exc))
            for e in dirs.values():
                if e.get("suffix_reason"):
                    self.log(f"{run.run_id}: {e['suffix_reason']}; using {e['folder']}")
            run = self.store.transition(
                run.run_id, run.state, results={"nas_mouse_dirs": dirs},
                detail="NAS folders reserved: " + ", ".join(e["rel"] for e in dirs.values()))

        self.store.transition(run.run_id, R.UPLOADING,
                              detail=f"uploading {len(dirs)} mice")
        uploaded = []
        try:
            for sm in spec["mice"]:
                entry = dirs[sm["slot"]]
                row = by_fb[sm["file_base"]]
                info = mouse_info(rep, row, sm, entry, qc=mouse_qc(run, sm["position"]))
                out = nas_upload.upload_mouse(
                    Path(ex["out_dir"]) / row["csv"], run.owner, entry, info,
                    expect_sha256=row["sha256"], progress=self.log)
                uploaded.append({"slot": sm["slot"], "mouse_id": sm["mouse_id"],
                                 "rel": entry["rel"], **out["upload"]})
        except nas_upload.UploadRefused as exc:
            self.log(f"{run.run_id}: upload refused ({exc}); back to UPLOAD_PENDING")
            return self.store.transition(run.run_id, R.UPLOAD_PENDING,
                                         detail=f"refused: {exc}")
        except Exception as exc:
            self.log(f"{run.run_id}: UPLOAD FAILED -- {exc}")
            return self.store.fail(run.run_id, "UPLOAD", str(exc))

        weak = [u for u in uploaded if u["status"] != "VERIFIED"]
        if weak:
            return self.store.fail(
                run.run_id, "UPLOAD",
                f"{len(weak)} CSV(s) were not verified: {[u['rel'] for u in weak]}")
        removed = self._remove_local_csvs(ex["out_dir"], rep)
        summary = {"status": "VERIFIED", "root": str(nas_upload.user_dir(run.owner)),
                   "mice": uploaded, "bytes": sum(u["bytes"] or 0 for u in uploaded),
                   "local_csvs_removed": removed}
        self.log(f"{run.run_id}: DONE -> {len(uploaded)} mice under {summary['root']}")
        return self.store.transition(run.run_id, R.DONE, detail="uploaded and verified",
                                     results={"upload": summary})

    def _remove_local_csvs(self, out_dir: str, rep: dict) -> list[str]:
        """Delete ONLY the CSVs this run's export wrote, now that all verified.

        Names come from the export report, never from a glob, so nothing else in
        the directory can be caught. The report and spec stay: they are small and
        they say what was made and where it went.
        """
        gone = []
        for m in rep.get("mice", []):
            p = Path(out_dir) / m["csv"]
            if p.is_file() and p.suffix == ".csv":
                p.unlink()
                gone.append(p.name)
        self.log(f"removed {len(gone)} local CSV(s) from {out_dir}")
        return gone

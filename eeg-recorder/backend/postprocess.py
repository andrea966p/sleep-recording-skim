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
goes off-site to S3 and the bilab NAS (see 20-areas/data-storage/backup-architecture).

ONE RUN, SEVERAL FILES (Allego 4, `split_files_by_port=True`, since 2026-10-28).
Each port now writes its own recording, `<base>_port<X>_<N>__uid<...>`, holding
that port's amplifier channels plus aux_1, din_1, dout_1 (35 channels on the
2026-10-28 bench files). The run carries them in `run.port_files`
({port: {"base_name", "data_path"}}). Every stage runs once PER PORT FILE:

    QC bundle   per file. Each chip's wire-free floor sits on its own port, so
                it is all inside that port's file; the manifest names only that
                port, otherwise `compute_features` would ask for floor sites on
                ports this file does not hold.
    strip       per file, to the run's keep_labels ON THAT PORT. The stripped
                twin is named after the per-port base name.
    CSV export  per file, for the mice on that port (slot[0] is the port).
    upload      per mouse, as before; each info.json names its own port file.

The run's state advances only when EVERY port's file has passed the stage, and
per-file results sit in run.results under the port letter (`qc_bundle`,
`strip.ports`, `export.ports`). A port that already passed is not redone on a
retry. Runs made before 2026-10-28 have an empty `port_files` and one combined
`data_path`; they take exactly the old path, one "port" called None.

A BUSY RIG IS A WAIT, NOT A FAILURE (2026-10-28). Since two runs on disjoint
ports may record at once, the strip or export of a finished run can meet
another run's live recording. Both tools refuse with `--require-idle` (the
rule: no heavy disk work while the rig records), and the chain now steps the
run back to its last resting state and tries again after `EEG_PP_DEFER_S`
seconds (default 600), instead of marking it FAILED and waiting for a human.

QC AND THE STRIP OF A PER-PORT RUN NO LONGER WAIT FOR OTHER PORTS (Andrea,
2026-10-29). Per-port files are about 7.5x smaller than the old combined file,
so their QC and strip may share the disk with another port's live recording;
they only wait for their own files to stop growing (`may_share_disk`). The
export still waits for an idle rig.

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
# Where the ladder writes each run's animal cards (`auto-<run_id>/`). The default
# is where they have always gone; the variable exists (2026-10-28) so a second
# console instance used for testing keeps its cards out of the real ones.
CARDS_ROOT = Path(os.environ.get("EEG_CARDS_ROOT", ANALYSIS / "cards" / "out"))


# How long a strip or export that met a live recording waits before it tries
# again. Ten minutes: long enough not to spin, short enough that a run whose
# neighbour stops at 09:00 is on the NAS soon after.
# Clamped to 30 s: a value of 0 would resubmit in a tight loop and hammer the
# disk with idle checks for as long as the neighbour records (review 2026-10-28).
DEFER_S = max(30.0, float(os.environ.get("EEG_PP_DEFER_S", "600")))
# A run that has waited this long for an idle rig gets ONE ntfy, so a stall
# behind a neighbour that never stops is seen by a person, not only in a log.
DEFER_ALERT_S = 12 * 3600.0
# Same notifier the scheduler and the recording watchdog use.
NOTIFY_SH = (Path(__file__).resolve().parents[2]
             / "neurosurveillance" / "deploy" / "nvr-notify.sh")


def _notify(level: str, title: str, body: str) -> None:
    """Fire and forget; a broken notifier must not stop the chain."""
    def work():
        try:
            subprocess.run([str(NOTIFY_SH), level, title, body],
                           capture_output=True, timeout=90)
        except Exception as exc:
            print(f"[postprocess] ntfy failed: {exc}", flush=True)
    threading.Thread(target=work, name="ntfy", daemon=True).start()


def rig_busy(srcs: list[dict], *, own_only: bool = False) -> str | None:
    """Is another recording being written? The same test the stripper and the
    exporter apply with `--require-idle` (convert.strip_channels.rig_is_busy),
    with every file of THIS run judged by growth. None when idle. `own_only`
    judges this run's files only (see `may_share_disk`)."""
    from importlib import import_module
    sys.path.insert(0, str(ANALYSIS))
    sc = import_module("convert.strip_channels")
    return sc.rig_is_busy(source_base=[x["base_path"] for x in srcs if x.get("base_path")],
                          own_only=own_only)


def may_share_disk(run) -> bool:
    """QC and the strip of a PER-PORT run may run while another port records
    (Andrea, 2026-10-29): its files are about 7.5x smaller than the old combined
    file. The export still waits for an idle rig, and runs made before per-port
    recording (one combined file) keep the old rule."""
    return bool(getattr(run, "port_files", None))


def extra_port_files(run, srcs: list[dict]) -> dict:
    """{port: [file, ...]} for every port that left MORE THAN ONE file in this
    run's window. Empty when each port has exactly its one file.

    A port stopped and restarted mid-run writes `<base>_port<X>_1__uid...`
    beside `_port<X>_0__uid...` (measured 2026-10-28), and `port_files` holds
    only one of them. The other would be dropped without a word, so the chain
    refuses instead. Merging two files is not attempted: the gap between them is
    real and has to be decided by a person.

    A file belongs to the run when its own start_time falls between the run's
    actual_start (less 120 s: the file can be stamped before the run records its
    start) and actual_stop. Files of other runs on the same port cannot fall
    there, because two runs never record the same port at once.
    """
    import glob
    from datetime import datetime, timedelta

    def when(iso):
        try:
            t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
            return t if t.tzinfo else None
        except (TypeError, ValueError):
            return None

    a, b = when(run.actual_start), when(run.actual_stop)
    if a is None or b is None:
        return {}
    out = {}
    for src in srcs:
        port, name = src.get("port"), src.get("base_name") or ""
        if not port or f"_port{port}_" not in name:
            continue
        stem = name.split(f"_port{port}_")[0]
        d = os.path.dirname(src["base_path"])
        hits = []
        for f in sorted(glob.glob(os.path.join(glob.escape(d),
                                               f"{glob.escape(stem)}_port{port}_*__uid*_data.xdat"))):
            base = f[: -len("_data.xdat")]
            try:
                st = json.loads(Path(base + ".xdat.json").read_text())["status"]["start_time"]
                t = when(st)
            except Exception:
                t = None
            if t is None:
                from datetime import timezone
                t = datetime.fromtimestamp(os.path.getmtime(f), timezone.utc)
            if a - timedelta(seconds=120) <= t <= b:
                hits.append(os.path.basename(f))
        if len(hits) > 1:
            out[port] = hits
    return out


class PostprocessError(RuntimeError):
    pass


class RigBusy(PostprocessError):
    """A tool refused because another recording is being written. Not a failure:
    the stage is retried later."""


# What the two tools print when `--require-idle` refuses. Matched on the text
# because both exit with the same code for every refusal.
_BUSY_MARKERS = ("the rig looks busy", "the rig is busy",
                 "a recording started while exporting")


def _is_busy(text: str) -> bool:
    return any(m in (text or "") for m in _BUSY_MARKERS)


def port_sources(run) -> list[dict]:
    """The recording files of a run, one dict per file, in port order.

    Each dict: {"port", "base_name", "base_path", "data_path", "slots",
    "keep_labels"}. `slots` are the occupied slots on that port and
    `keep_labels` the run's labels on that port.

    A run made before per-port recording (empty `port_files`) gives ONE entry
    with port None, the run's own base, every occupied slot and every label --
    so the old single-file chain is the same code with a list of one.

    Refuses, rather than guessing, when a mouse or a kept label sits on a port
    that has no file: carrying on would upload a run with an animal missing and
    no error anywhere. The exception is a port in `results.skipped_ports`: it
    enumerated nothing at the start, so it was deliberately not recorded and the
    run already carries that warning (scheduler.py); it is skipped with a log line.
    """
    pf = getattr(run, "port_files", None) or {}
    if not pf:
        return [{"port": None, "base_name": run.base_name, "base_path": run.base_path,
                 "data_path": run.data_path, "slots": list(run.occupied),
                 "keep_labels": list(run.keep_labels)}]
    out = []
    for port in sorted(pf):
        f = pf[port] or {}
        data_path = f.get("data_path") or ""
        if not data_path.endswith("_data.xdat"):
            raise PostprocessError(
                f"run {run.run_id}: port {port} has no usable data_path ({data_path!r})")
        base_path = data_path[: -len("_data.xdat")]
        name = os.path.basename(base_path)
        if f.get("base_name") and f["base_name"] != name:
            raise PostprocessError(
                f"run {run.run_id}: port {port} names base {f['base_name']!r} but its "
                f"data file is {data_path}; refusing to guess which is the recording")
        out.append({"port": port, "base_name": name, "base_path": base_path,
                    "data_path": data_path,
                    "slots": [sl for sl in run.occupied if sl[0] == port],
                    "keep_labels": [lb for lb in run.keep_labels
                                    if lb.split("/")[0] == port]})
    have = set(pf)
    skipped = set((getattr(run, "results", None) or {}).get("skipped_ports") or []) - have
    if skipped:
        print(f"[postprocess] run {run.run_id}: port(s) {sorted(skipped)} enumerated "
              "nothing at the start and were not recorded; skipping them", flush=True)
    have |= skipped
    orphan_slots = sorted(sl for sl in run.occupied if sl[0] not in have)
    orphan_labels = sorted(lb for lb in run.keep_labels if lb.split("/")[0] not in have)
    if orphan_slots or orphan_labels:
        raise PostprocessError(
            f"run {run.run_id} has no recording file for port(s) "
            f"{sorted({x[0] for x in orphan_slots + orphan_labels})}, but "
            f"slots {orphan_slots} / labels {orphan_labels} are on them. The files "
            f"it has are for {sorted(have)}.")
    return out


def _single(srcs: list[dict]) -> bool:
    """True for a pre-2026-10-28 run: one combined file, no port."""
    return len(srcs) == 1 and srcs[0]["port"] is None


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


def write_run_manifest(run, roles: tuple[str, ...], out_dir: Path | None = None,
                       *, src: dict | None = None) -> Path:
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

    PER PORT (`src` from `port_sources`, since 2026-10-28). The manifest then
    describes ONE file: `ports:` names only that port, and only the animals on
    it are listed. The cohort id stays `auto-<run_id>` so every port's cards
    land in one folder; the file name carries the port.
    """
    import yaml as _yaml
    out_dir = Path(out_dir) if out_dir else (
        Path(os.environ.get("EEG_RECORDER_STATE",
                            Path.home() / ".local" / "state" / "eeg-recorder")) / "cohorts")
    out_dir.mkdir(parents=True, exist_ok=True)
    # LOCAL date, from the uid in the recording's own name. run.actual_start is
    # UTC and would date an 08:55 KST recording to the previous day.
    from nas_upload import local_date_from_base
    port = (src or {}).get("port")
    base_name = (src or {}).get("base_name") or run.base_name
    date = local_date_from_base(base_name or "", run.actual_start)
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
        if not mid or (port and slot[0] != port):
            continue
        pos = _L.RigLayout.to_position(slot)
        animals.append({
            "animal_id": mid, "batch_id": cohort_id,
            "placements": [{"from": date, "position": pos, "console_slot": slot,
                            "source": "recording-console"}],
            "recordings": [{"base": base_name, "date": date,
                            "position": pos, "role": "animal"}],
        })
    lay = layout_of(run)
    ports_key = lay.cohort_ports() if lay is not None else None
    if port and ports_key is not None:
        if port not in ports_key:
            raise PostprocessError(
                f"port {port} holds a recording but the run's layout does not use "
                f"it (layout ports: {sorted(ports_key)})")
        ports_key = {port: ports_key[port]}
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
        **({"ports": ports_key} if ports_key is not None else {}),
        **(lay.cohort_extras() if lay is not None else {}),
        "criterion": "slope",
        "animals": animals,
        "recordings": [{"base": base_name, "date": date}],
    }
    path = out_dir / (f"{cohort_id}-port{port}.yaml" if port else f"{cohort_id}.yaml")
    path.write_text(_yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))
    return path


def compute_qc_bundle(run, *, progress=None, src: dict | None = None) -> tuple[bool, str]:
    """Compute the QC bundle for a run, with no human step. (ok, detail).

    `src` (one entry of `port_sources`) computes it for ONE port file; without
    it, for the run's single combined file, exactly as before 2026-10-28.
    """
    say = progress or (lambda m: None)
    if src is None:
        if getattr(run, "port_files", None):
            raise PostprocessError("a per-port run needs a port file to compute QC for")
        src = port_sources(run)[0]
    roles = roles_for_run(run)
    if roles is None:
        return False, (
            f"layout {run.preset!r} has no floor model, so CohortSpec's floor "
            "model does not apply to it and a QC bundle cannot be computed "
            "automatically without risking the wrong control sites.")
    try:
        manifest = write_run_manifest(run, roles, src=src)
    except PostprocessError as exc:
        return False, str(exc)
    cache = qc_cache_path(src["base_name"])
    cache.parent.mkdir(parents=True, exist_ok=True)
    cmd = [PYTHON, "cards/ladder.py", src["base_path"] or src["base_name"],
           "--cohort", str(manifest), "--cache", str(cache),
           "--out", str(CARDS_ROOT / f"auto-{run.run_id}")]
    # SCORE ONLY THE SLOTS THAT HOLD AN ANIMAL. Without this, ladder.py falls back
    # to `spec.positions()` -- all eight, whatever the operator filled in -- and a
    # four-mouse run comes back with four extra `UNKNOWN@B2` cards built from
    # amplifier inputs with nothing plugged into them. Measured 2026-09-13: such a
    # card can read PASS at rung 2, so the noise is not self-evidently noise.
    # Empty slots never contaminate the floor itself (floor sites are /3../16 and
    # /35../48, which no slot occupies), so this only removes false cards.
    if src["slots"]:
        import layout as _L
        cmd += ["--positions",
                ",".join(sorted(_L.RigLayout.to_position(s) for s in src["slots"]))]
    say(f"  computing QC bundle: roles={roles}, manifest={manifest.name}, "
        f"positions={','.join(sorted(src['slots'])) or 'all'}")
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
          progress: Callable[[str], None] | None = None, cfg=None,
          src: dict | None = None, siblings: list[str] = ()) -> dict:
    """Run the stripper as a subprocess and return its report.

    A subprocess rather than an import: the stripper is a long CPU+IO job, and
    keeping it out of the service's address space means a crash in it cannot take
    the API down mid-recording.

    `src` strips ONE port file to the labels on that port; `siblings` are the
    run's other port files, which the idle check judges by growth rather than
    mistaking them for a live recording. Raises RigBusy when another recording
    is being written.
    """
    say = progress or (lambda m: None)
    if src is None:
        src = {"base_path": run.base_path, "keep_labels": list(run.keep_labels)}
    if not src["base_path"]:
        raise PostprocessError(f"run {run.run_id} has no recorded base_path")
    if not src["keep_labels"]:
        raise PostprocessError(
            f"run {run.run_id}: no kept label on port {src.get('port')}, so its file "
            "would strip to nothing")
    cmd = [PYTHON, "-m", "convert.strip_channels", src["base_path"],
           "--keep-labels", ",".join(src["keep_labels"]),
           "--verify", "full", "--require-idle"]
    if may_share_disk(run):
        cmd.append("--ignore-other-recordings")
    for sib in siblings:
        cmd += ["--also-source", sib]
    if run.with_gpio:
        cmd.append("--with-gpio")
    elif not (cfg or _cfg()).gpio_header_connected:
        # 🔴 GATE B ON AN EMPTY GPIO HEADER CAN ONLY FAIL ON NOISE. Run
        # ee0263bffeaa (2026-10-08) went FAILED_STRIP on din_1: 6 single-ms
        # glitches on a floating input, nothing wired (Andrea, 10-09). It was
        # finished by hand with this flag, which the retry could not pass. The
        # claim comes from the config, not the run, and the strip report records
        # it as `gate_b_override`. Set `rig.gpio_header_connected: true` the day
        # the XDAQ -> Pi sync is wired, or a real sync line will be dropped.
        cmd.append("--gpio-never-connected")
    if out_dir:
        cmd += ["--out", str(out_dir)]
    say(f"  {' '.join(cmd[:4])} ... ({len(src['keep_labels'])} labels)")
    env = dict(os.environ, PYTHONPATH=str(ANALYSIS))
    p = subprocess.run(cmd, cwd=ANALYSIS, env=env, capture_output=True, text=True)
    if p.returncode != 0:
        tail = (p.stderr or p.stdout or "")[-2000:]
        if _is_busy(tail):
            raise RigBusy(tail.strip())
        raise PostprocessError(f"strip_channels exited {p.returncode}:\n{tail}")
    from importlib import import_module
    sys.path.insert(0, str(ANALYSIS))
    paths = import_module("core.paths")
    root = Path(out_dir) if out_dir else Path(paths.STRIPPED_ROOT)
    # The stripper names its output after the SOURCE file, so for a per-port run
    # the report carries the per-port base name.
    report = root / f"{os.path.basename(src['base_path'])}.strip-report.json"
    if not report.exists():
        raise PostprocessError(f"strip reported success but {report} is missing")
    return json.loads(report.read_text())


def export_spec(run: R.Run, cfg=None, *, src: dict | None = None) -> dict:
    """What the CSV exporter needs: for each occupied slot, its file name and the
    site label carrying each role.

    Built from the run's OWN layout record (`run.layout["roles"]`), not from the
    current config, so a run stays exportable after its setting is renamed or
    deleted -- the reason the layout is stored self-describing in the first place.

    With `src` (one port file) only the mice on that port are listed, and the
    meta names that file as the raw source.
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
        if src is not None and src.get("port") and slot[0] != src["port"]:
            continue
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
                     "raw_base_path": (src or {}).get("base_path") or run.base_path,
                     **({"port": src["port"]} if src and src.get("port") else {})}}


def export_csv(run: R.Run, *, out_root: Path | None = None,
               progress: Callable[[str], None] | None = None,
               src: dict | None = None, all_sources: list[str] = ()) -> dict:
    """Run export/per_mouse_csv.py as a subprocess and return its report.

    With `src` (one port file): exports the mice on that port from that port's
    stripped twin, into `<PER_MOUSE_ROOT>/<per-port base name>/`. `all_sources`
    are every raw file of the run, for the idle check. Raises RigBusy when
    another recording is being written.
    """
    say = progress or (lambda m: None)
    strip_rec = run.results.get("strip") or {}
    if src is not None and src.get("port"):
        dst = ((strip_rec.get("ports") or {}).get(src["port"]) or {}).get("dst_base")
        base_name, raw_base = src["base_name"], src["base_path"]
    else:
        dst = strip_rec.get("dst_base")
        base_name, raw_base = run.base_name, run.base_path
    if not dst:
        raise PostprocessError(
            f"run {run.run_id} has no stripped output recorded"
            + (f" for port {src['port']}" if src and src.get("port") else ""))
    spec = export_spec(run, src=src)
    if not spec["mice"]:
        raise PostprocessError(f"run {run.run_id}: no mouse to export from {base_name}")
    out = Path(out_root or PER_MOUSE_ROOT) / base_name
    out.mkdir(parents=True, exist_ok=True)
    spec_path = out / "spec.json"
    spec_path.write_text(json.dumps(spec, indent=2))
    cmd = [PYTHON, "-m", "export.per_mouse_csv", dst, "--spec", str(spec_path),
           "--out", str(out), "--require-idle"]
    for b in (list(all_sources) or ([raw_base] if raw_base else [])):
        cmd += ["--source-base", b]
    say(f"  export.per_mouse_csv {base_name} ({len(spec['mice'])} mice)")
    env = dict(os.environ, PYTHONPATH=str(ANALYSIS))
    p = subprocess.run(cmd, cwd=ANALYSIS, env=env, capture_output=True, text=True)
    if p.returncode != 0:
        tail = (p.stderr or p.stdout or "")[-2000:]
        if _is_busy(tail):
            raise RigBusy(tail.strip())
        raise PostprocessError(f"per_mouse_csv exited {p.returncode}:\n{tail}")
    # The exporter names its report after the STRIPPED base, which is the source
    # file's own name -- the per-port name for a per-port run.
    report = out / f"{os.path.basename(dst)}.per-mouse-report.json"
    if not report.exists():
        raise PostprocessError(f"export reported success but {report} is missing")
    rep = json.loads(report.read_text())
    want = {m["file_base"] for m in spec["mice"]}
    got = {m["file_base"] for m in rep.get("mice", [])}
    if want != got:
        raise PostprocessError(f"export report covers {sorted(got)}, spec asked for {sorted(want)}")
    return {"report": str(report), "out_dir": str(out), "spec": spec, "rep": rep}


def card_path(run: R.Run, position: str) -> Path:
    """Where compute_qc_bundle's ladder run left this animal's card.

    The card is named after the recording it was judged on: the port's own
    file for a per-port run (position[0] is the port), the run's file otherwise.
    """
    pf = (getattr(run, "port_files", None) or {}).get(position[:1]) or {}
    base = run.base_name
    if pf.get("data_path", "").endswith("_data.xdat"):
        base = os.path.basename(pf["data_path"][: -len("_data.xdat")])
    elif pf.get("base_name"):
        base = pf["base_name"]
    return CARDS_ROOT / f"auto-{run.run_id}" / f"{base}__{position}_card.json"


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


def _strip_summary(done: dict) -> dict:
    """results["strip"] for a per-port run. Per-file facts sit under `ports`;
    the totals at the top are what the console's run list shows. There is
    deliberately no top-level `dst_base`: one would name a single port's file
    as if it were the whole run."""
    b_in = sum(d.get("bytes_in") or 0 for d in done.values())
    b_out = sum(d.get("bytes_out") or 0 for d in done.values())
    gate = {p: d["gate_b_override"] for p, d in done.items() if d.get("gate_b_override")}
    return {"ports": done, "bytes_out": b_out,
            "saving_pct": round(100 * (1 - b_out / b_in), 2) if b_in else None,
            "gate_b_override": gate or None}


def _export_still_valid(run, src: dict, prev: dict) -> bool:
    """May a per-port export recorded on the run be reused on a retry?

    Only if its report still exists, every CSV it names is on disk at the size
    it recorded, and it was made for the SAME analysis window the run asks for
    now (the spec.json written beside it). Anything else re-runs the exporter,
    which itself resumes verified CSVs, so being wrong here costs time, never data.
    """
    try:
        rep = json.loads(Path(prev["report"]).read_text())
        out = Path(prev["out_dir"])
        for m in rep.get("mice") or []:
            if (out / m["csv"]).stat().st_size != m["bytes"]:
                return False
        if not rep.get("mice"):
            return False
        used = json.loads((out / "spec.json").read_text()).get("window")
        return used == export_spec(run, src=src).get("window")
    except Exception:
        return False


def _export_summary(done: dict) -> dict:
    """results["export"] for a per-port run: per-file records under `ports`,
    totals on top (the run list reads `n_mice` and `bytes`)."""
    return {"ports": done, "n_mice": sum(d["n_mice"] for d in done.values()),
            "bytes": sum(d["bytes"] for d in done.values())}


class Worker:
    """The post-stop chain, on one background thread."""

    def __init__(self, store: R.RunStore, *,
                 require_qc_bundle: bool = True,
                 auto_compute_qc: bool = True,
                 on_event: Callable[[str], None] | None = None,
                 notify: Callable[[str, str, str], None] | None = None):
        self.store = store
        self.require_qc_bundle = require_qc_bundle
        self.auto_compute_qc = auto_compute_qc
        self.log = on_event or (lambda m: print(f"[postprocess] {m}", flush=True))
        self.notify = notify or _notify          # (level, title, body)
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

    def _defer(self, run_id: str) -> None:
        """Put a run back in the queue after DEFER_S seconds.

        The FIRST deferral is stamped on the run (`results.deferred_since`), and
        after DEFER_ALERT_S of waiting one ntfy goes out (`deferred_alerted`).
        """
        try:
            run = self.store.get(run_id)
            res = run.results or {}
            now = R.utcnow()
            if not res.get("deferred_since"):
                self.store.transition(run_id, run.state, detail="waiting for an idle rig",
                                      results={"deferred_since": now})
            elif not res.get("deferred_alerted"):
                from datetime import datetime
                t0 = datetime.fromisoformat(res["deferred_since"].replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(now.replace("Z", "+00:00"))
                waited = (t1 - t0).total_seconds()
                if waited >= DEFER_ALERT_S:
                    self.notify(
                        "warn", f"EEG run {run_id}: post-processing waiting {waited / 3600:.0f} h",
                        f"Run {run_id} ({run.owner}) has waited since {res['deferred_since']} "
                        "for the rig to be idle; another port is still recording. Its "
                        "data is safe; QC, strip and upload resume when the rig is idle.")
                    self.store.transition(run_id, run.state, detail="ntfy: long wait",
                                          results={"deferred_alerted": now})
        except Exception as exc:          # bookkeeping must never stop the retry
            self.log(f"{run_id}: deferral bookkeeping failed: {exc}")
        if self._stop.is_set():
            return
        t = threading.Timer(DEFER_S, self.submit, args=(run_id,))
        t.daemon = True
        t.start()

    def _qc_must_wait(self, run: R.Run, srcs: list[dict]) -> bool:
        """Computing a QC bundle reads the whole recording, so it waits until
        this run's own files have stopped growing (review 2026-10-28), and for a
        run made before per-port recording also until no other recording is
        being written. The run stays in STOPPED and is resubmitted later."""
        try:
            busy = rig_busy(srcs, own_only=may_share_disk(run))
        except Exception as exc:
            self.log(f"{run.run_id}: idle check failed ({exc}); computing anyway")
            return False
        if not busy:
            return False
        self.log(f"{run.run_id}: QC bundle DEFERRED, the rig is recording -- {busy}; "
                 f"retrying in {DEFER_S:.0f} s")
        self._defer(run.run_id)
        return True

    def _wait(self, run_id: str, back: str, what: str, exc: Exception) -> R.Run:
        """A tool refused because another recording is live. Step back to the
        resting state the stage starts from and try again later. NOT a failure:
        the data is fine and nobody needs to act."""
        why = str(exc).strip().splitlines()[-1][:300] if str(exc).strip() else "rig busy"
        self.log(f"{run_id}: {what} DEFERRED, the rig is recording -- {why}; "
                 f"retrying in {DEFER_S:.0f} s")
        run = self.store.transition(
            run_id, back, detail=f"waiting: {what} deferred, rig busy ({why}); "
                                 f"retry in {DEFER_S:.0f} s")
        self._defer(run_id)
        return run

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
        try:
            srcs = port_sources(run)
        except PostprocessError as exc:
            self.log(f"{run.run_id}: {exc}")
            return self.store.fail(run.run_id, "QC", str(exc))
        if not _single(srcs):
            extra = extra_port_files(run, srcs)
            if extra:
                msg = ("more than one recording file per port in this run's window, "
                       "so a port was stopped and restarted mid-run: "
                       + "; ".join(f"port {p}: {', '.join(fs)}" for p, fs in sorted(extra.items()))
                       + ". The run records only one file per port, so the others would "
                       "be dropped silently. They are NOT merged automatically: the gap "
                       "between them is real. Process them by hand, or abort the run.")
                self.log(f"{run.run_id}: HELD -- {msg}")
                return self.store.fail(run.run_id, "QC", msg)
            return self._qc_ports(run, srcs)

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
            if self._qc_must_wait(run, srcs):
                return self.store.get(run.run_id)
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
        try:
            srcs = port_sources(run)
        except PostprocessError as exc:
            return self.store.fail(run.run_id, "STRIP", str(exc))
        if not _single(srcs):
            return self._strip_ports(run, srcs)
        self.log(f"{run.run_id}: stripping {run.base_name} "
                 f"-> {len(run.keep_labels)} channels")
        self.store.transition(run.run_id, R.STRIPPING, detail="strip_channels")
        try:
            rep = strip(run, progress=self.log)
        except RigBusy as exc:
            return self._wait(run.run_id, R.QC, "strip", exc)
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
                               "dataset_checksum": rep.get("dataset_checksum"),
                               "gate_b_override": rep.get("gate_b_override")}})

    def _export(self, run: R.Run) -> R.Run:
        try:
            srcs = port_sources(run)
        except PostprocessError as exc:
            return self.store.fail(run.run_id, "EXPORT", str(exc))
        if not _single(srcs):
            return self._export_ports(run, srcs)
        self.log(f"{run.run_id}: exporting per-mouse CSVs from {run.base_name}")
        self.store.transition(run.run_id, R.EXPORTING, detail="per_mouse_csv")
        try:
            ex = export_csv(run, progress=self.log)
        except RigBusy as exc:
            return self._wait(run.run_id, R.STRIPPED, "export", exc)
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
        # One (out_dir, report, spec) per exported FILE: one for a combined
        # recording, one per port for a per-port run (2026-10-28).
        try:
            recs = ([ex["ports"][p] for p in sorted(ex["ports"])] if ex.get("ports")
                    else [ex])
            parts = [(rec["out_dir"], json.loads(Path(rec["report"]).read_text()),
                      json.loads((Path(rec["out_dir"]) / "spec.json").read_text()))
                     for rec in recs]
        except Exception as exc:
            return self.store.fail(run.run_id, "UPLOAD",
                                   f"the per-mouse export record is unreadable: {exc}")

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
            for out_dir, rep, spec in parts:
                by_fb = {m["file_base"]: m for m in rep["mice"]}
                for sm in spec["mice"]:
                    entry = dirs[sm["slot"]]
                    row = by_fb[sm["file_base"]]
                    info = mouse_info(rep, row, sm, entry,
                                      qc=mouse_qc(run, sm["position"]))
                    out = nas_upload.upload_mouse(
                        Path(out_dir) / row["csv"], run.owner, entry, info,
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

        # EVERY MOUSE OR NOT DONE. DONE removes the local CSVs, so a run whose
        # exports covered fewer slots than it reserved folders for must stop here.
        got = {u["slot"] for u in uploaded}
        if got != set(dirs):
            return self.store.fail(
                run.run_id, "UPLOAD",
                f"uploaded slots {sorted(got)} but the run has folders for "
                f"{sorted(dirs)}; refusing to mark it DONE")
        weak = [u for u in uploaded if u["status"] != "VERIFIED"]
        if weak:
            return self.store.fail(
                run.run_id, "UPLOAD",
                f"{len(weak)} CSV(s) were not verified: {[u['rel'] for u in weak]}")
        removed = [name for out_dir, rep, _spec in parts
                   for name in self._remove_local_csvs(out_dir, rep)]
        summary = {"status": "VERIFIED", "root": str(nas_upload.user_dir(run.owner)),
                   "mice": uploaded, "bytes": sum(u["bytes"] or 0 for u in uploaded),
                   "local_csvs_removed": removed}
        self.log(f"{run.run_id}: DONE -> {len(uploaded)} mice under {summary['root']}")
        return self.store.transition(run.run_id, R.DONE, detail="uploaded and verified",
                                     results={"upload": summary})

    # ---- per-port runs (Allego 4, since 2026-10-28) ---------------------- #
    def _qc_ports(self, run: R.Run, srcs: list[dict]) -> R.Run:
        """`_qc` for a run recorded as one file per port.

        One bundle per FILE, each from that file's own wire-free inputs. The
        guards are the same as for a combined file -- a layout with no criterion
        is `qc_not_applicable`, a waiver is per run and recorded, a missing
        bundle holds the run -- and they apply to the run as a whole: one port
        without its floor holds every port, because the run is uploaded as one.
        A port whose bundle already exists is not recomputed on a retry.
        """
        ports = [s["port"] for s in srcs]
        if not qc_applies_to_run(run):
            self.log(f"{run.run_id}: preset {run.preset!r} declares no QC criterion")
            return self.store.transition(
                run.run_id, R.QC,
                detail=(f"layout {run.preset!r} declares `qc: none`: this "
                        "project's floor model does not describe its layout, so "
                        "no bundle exists to lose"),
                results={"qc_bundle": {p: None for p in ports},
                         "qc_not_applicable": True})

        if (self.auto_compute_qc and any(not has_qc_bundle(x["base_name"]) for x in srcs)
                and self._qc_must_wait(run, srcs)):
            return self.store.get(run.run_id)
        bundles: dict = {}
        auto: dict = {}
        failed: dict = {}
        for src in srcs:
            port, name = src["port"], src["base_name"]
            if has_qc_bundle(name):
                self.log(f"{run.run_id}: port {port}: QC bundle present")
                bundles[port] = str(qc_cache_path(name))
                continue
            if not self.auto_compute_qc:
                failed[port] = "no bundle, and automatic computation is off"
                continue
            self.log(f"{run.run_id}: port {port}: no QC bundle for {name}, computing one")
            ok, detail = compute_qc_bundle(run, progress=self.log, src=src)
            if ok:
                bundles[port] = str(qc_cache_path(name))
                auto[port] = True
            else:
                self.log(f"{run.run_id}: port {port}: could not compute a QC bundle -- {detail}")
                failed[port] = detail

        if not failed:
            return self.store.transition(
                run.run_id, R.QC,
                detail=f"QC bundle present for every port ({', '.join(ports)})",
                results={"qc_bundle": bundles,
                         **({"qc_bundle_auto": auto} if auto else {})})

        override = bool((run.results or {}).get("skip_qc_bundle"))
        if override or not self.require_qc_bundle:
            self.log(f"{run.run_id}: WARNING, proceeding WITHOUT a QC bundle for "
                     f"port(s) {', '.join(sorted(failed))}. Their wire-free floor "
                     "will not survive the strip.")
            return self.store.transition(
                run.run_id, R.QC,
                detail=(f"no QC bundle for port(s) {', '.join(sorted(failed))} -- "
                        "EXPLICITLY OVERRIDDEN for this run"),
                results={"qc_bundle": {**bundles, **{p: None for p in failed}},
                         "qc_bundle_skipped": True,
                         "qc_bundle_skipped_ports": sorted(failed),
                         **({"qc_bundle_auto": auto} if auto else {})})

        short = ""
        dur_s = _duration_s(run)
        if dur_s is not None and dur_s < 15 * 60:
            short = (f" NOTE: this recording is only {dur_s / 60:.1f} min long, below "
                     "the 15 min unbroken-block bar the verdict ladder gates on, so a "
                     "QC bundle for it would not be meaningful. If this was a test, "
                     "abandon the run or strip it with the override.")
        why = "".join(
            f"\n\nPORT {p}, {next(s['base_name'] for s in srcs if s['port'] == p)}:\n  "
            + str(d).strip().replace("\n", "\n  ")
            for p, d in sorted(failed.items()))
        cmds = "".join(
            f"\n  cd {ANALYSIS} && PYTHONPATH=. {PYTHON} cards/ladder.py "
            f"{s['base_path']} --cohort <id> --cache {qc_cache_path(s['base_name'])}"
            for s in srcs if s["port"] in failed)
        msg = (f"no QC bundle for port(s) {', '.join(sorted(failed))} of run "
               f"{run.run_id}.{why}\n\nStripping removes the in-file wire-free "
               "floor, after which core/criteria.py can never judge these files "
               f"again.{short} Compute them with:{cmds}")
        self.log(f"{run.run_id}: HELD -- {msg}")
        # The ports that DID get a bundle are on disk, so a retry finds them.
        return self.store.fail(run.run_id, "QC", msg)

    def _strip_ports(self, run: R.Run, srcs: list[dict]) -> R.Run:
        """`_strip` for a per-port run: each file to the labels on its port.

        Each finished port is written to the run before the next starts, so a
        failure or a restart on port C does not redo A and B.
        """
        self.store.transition(run.run_id, R.STRIPPING,
                              detail=f"strip_channels, {len(srcs)} port file(s)")
        done = dict(((run.results or {}).get("strip") or {}).get("ports") or {})
        bases = [s["base_path"] for s in srcs]
        for src in srcs:
            port = src["port"]
            prev = done.get(port) or {}
            if (prev.get("dst_base") and prev.get("keep_labels") == src["keep_labels"]
                    and Path(prev["dst_base"] + ".xdat.json").exists()):
                self.log(f"{run.run_id}: port {port} already stripped")
                continue
            self.log(f"{run.run_id}: stripping port {port} {src['base_name']} "
                     f"-> {len(src['keep_labels'])} channels")
            try:
                rep = strip(run, progress=self.log, src=src,
                            siblings=[b for b in bases if b != src["base_path"]])
            except RigBusy as exc:
                return self._wait(run.run_id, R.QC, f"strip of port {port}", exc)
            except Exception as exc:
                self.log(f"{run.run_id}: STRIP FAILED on port {port} -- {exc}")
                return self.store.fail(run.run_id, "STRIP", f"port {port}: {exc}")
            plan = rep.get("plan", {})
            done[port] = {"dst_base": rep.get("dst_base"), "src_base": src["base_path"],
                          "keep_labels": src["keep_labels"],
                          "saving_pct": plan.get("saving_pct"),
                          "bytes_in": plan.get("bytes_in"),
                          "bytes_out": plan.get("bytes_out"),
                          "dataset_checksum": rep.get("dataset_checksum"),
                          "gate_b_override": rep.get("gate_b_override")}
            self.log(f"{run.run_id}: port {port} stripped, {plan.get('saving_pct')}% smaller")
            self.store.transition(run.run_id, R.STRIPPING,
                                  detail=f"port {port} verified bit-exact",
                                  results={"strip": _strip_summary(done)})
        return self.store.transition(
            run.run_id, R.STRIPPED,
            detail=f"{len(done)} port file(s) verified bit-exact",
            results={"strip": _strip_summary(done)})

    def _export_ports(self, run: R.Run, srcs: list[dict]) -> R.Run:
        """`_export` for a per-port run: one exporter call per port file, for
        the mice on that port. Finished ports are recorded as they finish."""
        self.store.transition(run.run_id, R.EXPORTING,
                              detail=f"per_mouse_csv, {len(srcs)} port file(s)")
        done = dict(((run.results or {}).get("export") or {}).get("ports") or {})
        bases = [s["base_path"] for s in srcs]
        for src in srcs:
            port = src["port"]
            if _export_still_valid(run, src, done.get(port) or {}):
                self.log(f"{run.run_id}: port {port} already exported")
                continue
            self.log(f"{run.run_id}: exporting port {port} from {src['base_name']}")
            try:
                ex = export_csv(run, progress=self.log, src=src, all_sources=bases)
            except RigBusy as exc:
                return self._wait(run.run_id, R.STRIPPED, f"export of port {port}", exc)
            except (PostprocessError, naming.NamingError) as exc:
                self.log(f"{run.run_id}: EXPORT FAILED on port {port} -- {exc}")
                return self.store.fail(run.run_id, "EXPORT", f"port {port}: {exc}")
            rep = ex["rep"]
            done[port] = {"report": ex["report"], "out_dir": ex["out_dir"],
                          "n_mice": len(rep["mice"]),
                          "bytes": sum(m["bytes"] for m in rep["mice"])}
            self.store.transition(run.run_id, R.EXPORTING,
                                  detail=f"port {port}: {len(rep['mice'])} CSVs verified",
                                  results={"export": _export_summary(done)})
        summary = _export_summary(done)
        self.log(f"{run.run_id}: exported {summary['n_mice']} mice from "
                 f"{len(done)} port file(s), {summary['bytes'] / 1e9:.1f} GB")
        return self.store.transition(
            run.run_id, R.EXPORTED,
            detail=f"{summary['n_mice']} CSVs verified ({len(done)} port files)",
            results={"export": summary})

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

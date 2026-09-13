#!/usr/bin/env python3
"""app.py -- the local recording console: one Flask app, one page, one rig.

Binds to 127.0.0.1 only. This drives amplifiers with animals attached; it is not
something to expose to the lab network, and there is no authentication because
there is no remote access.

SEPARATE FROM THE VIDEO DAEMON, DELIBERATELY. `neurosurveillance` polls Radiens
and declares observe-only as an invariant (`radiens_poller.py:7`), and the vault
records keeping the EEG scheduling path separate as a decision rather than an
accident. A bug in recording control must not be able to take video recording
down, and vice versa. Different port, different unit, different process.

    GET  /api/state              everything the page polls: allego, storage, nas, active run
    GET  /api/users              users + presets, for the setup form
    GET  /api/presets/<name>     resolved slots and labels
    POST /api/runs               create a run (draft, or scheduled if given instants)
    GET  /api/runs               history
    GET  /api/runs/<id>          one run plus its event log
    POST /api/runs/<id>/start    start now
    POST /api/runs/<id>/stop     stop now
    POST /api/runs/<id>/schedule {start_at, stop_at}
    POST /api/runs/<id>/postprocess   re-run QC/strip/upload for a stuck run
    POST /api/runs/<id>/abort    abandon a draft or scheduled run
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, str(Path(__file__).resolve().parent))

import allego
import nas_upload
import postprocess
import presets as P
import runs as R
import naming
import scheduler as SCH
import storage as ST

HOST = os.environ.get("EEG_RECORDER_HOST", "127.0.0.1")
PORT = int(os.environ.get("EEG_RECORDER_PORT", "8600"))
RAW_ROOT = Path(os.environ.get("EEG_RAW_ROOT", "/home/skimlab/radix/data"))
# The UI is a single self-contained page, served straight from here. No build
# step, no node_modules, nothing to go stale on a machine whose real job is
# recording. Edit the file, reload the browser.
DIST = Path(__file__).resolve().parent.parent / "frontend"

# Same rule as the existing daemon (api.py:85): a mouse id reaches the filesystem
# and the NAS path, so anything outside this set is rejected rather than escaped.
SAFE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")

app = Flask(__name__, static_folder=None)
cfg = P.load()
store = R.RunStore()
worker = postprocess.Worker(store)
# The scheduler hands a stopped run straight to the post-processing worker. Both
# stop paths -- scheduled and manual -- go through this one callback, so an
# unattended stop cannot silently skip QC, strip and upload.
sched = SCH.Scheduler(store, dest_dir=RAW_ROOT, on_stopped=lambda rid: worker.submit(rid))


def _err(msg: str, code: int = 400):
    return jsonify({"error": str(msg)}), code


# --------------------------------------------------------------------------- #
# state
# --------------------------------------------------------------------------- #
@app.get("/api/state")
def api_state():
    active = store.active()
    out = {
        "utc": R.utcnow(),
        "local": datetime.now().astimezone().isoformat(timespec="seconds"),
        "allego": allego.status(),
        "storage": ST.status(RAW_ROOT),
        "nas": nas_upload.nas_status(),
        "active_run": active.to_dict() if active else None,
        "worker_busy": worker.current,
        "pending_upload": [r.run_id for r in store.list(states=(R.UPLOAD_PENDING,),
                                                        limit=20)],
    }
    if active and active.data_path:
        out["active_run"]["bytes_on_disk"] = allego.bytes_now(active.data_path)
    return jsonify(out)


@app.get("/api/users")
def api_users():
    return jsonify({
        "users": {u: {"default_preset": d["default_preset"]}
                  for u, d in cfg.users.items()},
        "recording_types": list(cfg.recording_types),
        "presets": {n: {"label": p.label, "slots": p.slot_names,
                        "channels_per_animal": p.channels_per_animal,
                        "roles": p.roles, "sites": list(p.sites),
                        "with_gpio": p.with_gpio, "qc": p.qc,
                        "total_channels": len(p.labels())}
                    for n, p in cfg.presets.items()},
    })


@app.get("/api/presets/<name>")
def api_preset(name):
    try:
        p = cfg.preset(name)
    except P.PresetError as exc:
        return _err(exc, 404)
    return jsonify({
        "name": p.name, "label": p.label, "with_gpio": p.with_gpio, "qc": p.qc,
        "slots": {s: {"labels": p.labels_for_slot(s),
                      "roles": [p.role_of(s, l) for l in p.labels_for_slot(s)]}
                  for s in p.slot_names},
        "all_labels": p.labels(),
    })


# --------------------------------------------------------------------------- #
# runs
# --------------------------------------------------------------------------- #
def _validate_slots(preset: P.Preset, slots: dict) -> dict:
    clean = {}
    for slot, v in (slots or {}).items():
        if slot not in preset.slots:
            raise ValueError(f"{slot!r} is not a slot in preset {preset.name!r}")
        mouse = str((v or {}).get("mouse_id", "")).strip()
        rtype = str((v or {}).get("recording_type", "")).strip()
        if not mouse:
            continue                        # slot left empty, fine
        if not SAFE.match(mouse):
            raise ValueError(
                f"mouse id {mouse!r} in slot {slot}: letters, digits, hyphen and "
                "underscore only, max 32 characters. It becomes part of a path.")
        if rtype and rtype not in cfg.recording_types:
            raise ValueError(
                f"recording type {rtype!r} in slot {slot}; known types are "
                f"{', '.join(cfg.recording_types)}")
        clean[slot] = {"mouse_id": mouse, "recording_type": rtype or "basal"}
    if not clean:
        raise ValueError("no slot has a mouse id, so nothing could be attributed "
                         "to an animal afterwards")
    return clean


@app.post("/api/naming/preview")
def api_naming_preview():
    """What the NAS folder and files will be called, BEFORE anything is recorded.

    The console shows this under the slot grid. A name people only discover after
    a 24 h run is a name they cannot fix.
    """
    body = request.get_json(silent=True) or {}
    from datetime import datetime
    today = datetime.now().astimezone().strftime("%Y%m%d")
    when = str(body.get("date") or "").strip()
    source = "explicit"
    if not when:
        # The date the recording will CARRY, which is the date it STARTS -- not
        # the date this form was filled in. The console pre-fills Start at with
        # the next 09:00, so after 09:00 the scheduled date is TOMORROW while a
        # "Start now" run would be dated today. Both answers are right for their
        # button; saying which one this is keeps the preview from promising a
        # name the uploader will not produce.
        st = body.get("start_at")
        try:
            when = SCH.parse_instant(st).strftime("%Y%m%d") if st else today
            source = "scheduled start" if st else "today"
        except Exception:
            when, source = today, "today"
    try:
        pname = body.get("preset") or ""
        preset = cfg.preset(pname) if pname else None
        slots = _validate_slots(preset, body.get("slots")) if preset else {}
        out = naming.preview(batch_name=body.get("batch_name"), slots=slots,
                             cfg=cfg, date_yyyymmdd=when)
    except (P.PresetError, naming.NamingError, ValueError) as exc:
        return _err(exc)
    out["user"] = body.get("owner")
    out["date"] = when
    out["date_source"] = source
    out["today"] = today
    if out.get("folder") and when != today and source == "scheduled start":
        out["if_started_now"] = out["folder"].replace(when, today, 1)
    return jsonify(out)


@app.post("/api/runs")
def api_create_run():
    body = request.get_json(silent=True) or {}
    owner = str(body.get("owner", "")).strip()
    if owner not in cfg.users:
        return _err(f"unknown user {owner!r}; known users are "
                    f"{', '.join(cfg.users)}")
    pname = body.get("preset") or cfg.users[owner]["default_preset"]
    try:
        preset = cfg.preset(pname)
        slots = _validate_slots(preset, body.get("slots"))
        labels = preset.labels(list(slots))
    except (P.PresetError, ValueError) as exc:
        return _err(exc)

    try:
        batch = naming.clean_batch(body.get("batch_name"))
    except naming.NamingError as exc:
        return _err(exc)

    try:
        run = store.create(owner=owner, preset=pname, slots=slots, batch_name=batch,
                           keep_labels=labels, with_gpio=preset.with_gpio,
                           scheduled_start=body.get("start_at"),
                           scheduled_stop=body.get("stop_at"),
                           note=body.get("note"), dest_dir=str(RAW_ROOT))
    except R.RunError as exc:
        return _err(exc)
    return jsonify(run.to_dict()), 201


@app.get("/api/runs")
def api_runs():
    limit = min(int(request.args.get("limit", 50)), 500)
    states = request.args.getlist("state") or None
    return jsonify({"runs": [r.to_dict() for r in store.list(states=states,
                                                             limit=limit)]})


@app.get("/api/runs/<run_id>")
def api_run(run_id):
    try:
        run = store.get(run_id)
    except R.RunError as exc:
        return _err(exc, 404)
    d = run.to_dict()
    d["events"] = store.events(run_id)
    return jsonify(d)


@app.post("/api/runs/<run_id>/start")
def api_start(run_id):
    try:
        return jsonify(sched.start_now(run_id).to_dict())
    except R.RunError as exc:
        return _err(exc, 409)
    except allego.PreflightFailed as exc:
        return _err(f"preflight failed: {exc}", 409)
    except Exception as exc:
        return _err(f"{type(exc).__name__}: {exc}", 500)


@app.post("/api/runs/<run_id>/stop")
def api_stop(run_id):
    try:
        run = sched.stop_now(run_id)
    except R.RunError as exc:
        return _err(exc, 409)
    except Exception as exc:
        return _err(f"{type(exc).__name__}: {exc}", 500)
    # No worker.submit() here: sched.stop_now() already fired the on_stopped
    # callback. One handoff, one code path, no double submission.
    return jsonify(run.to_dict())


@app.post("/api/runs/<run_id>/schedule")
def api_schedule(run_id):
    body = request.get_json(silent=True) or {}
    start_at, stop_at = body.get("start_at"), body.get("stop_at")
    if not start_at:
        return _err("start_at is required")
    try:
        s = SCH.parse_instant(start_at)
        e = SCH.parse_instant(stop_at) if stop_at else None
    except ValueError as exc:
        return _err(f"could not parse an instant: {exc}")
    if e and e <= s:
        return _err("stop_at must be after start_at")
    try:
        run = store.get(run_id)
        if run.state not in (R.DRAFT, R.SCHEDULED):
            return _err(f"run is {run.state}, not schedulable", 409)
        run = store.transition(run_id, R.SCHEDULED,
                               detail=f"scheduled {s.isoformat()}"
                                      + (f" -> {e.isoformat()}" if e else ""),
                               scheduled_start=s.isoformat(),
                               scheduled_stop=e.isoformat() if e else None)
    except R.RunError as exc:
        return _err(exc, 409)
    return jsonify(run.to_dict())


@app.post("/api/runs/<run_id>/abort")
def api_abort(run_id):
    try:
        run = store.get(run_id)
        if run.state not in (R.DRAFT, R.SCHEDULED) and not run.state.startswith("FAILED_"):
            return _err(f"run is {run.state}; only a draft, a scheduled or a "
                        "failed run can be abandoned", 409)
        return jsonify(store.transition(run_id, R.ABORTED,
                                        detail="abandoned by the user").to_dict())
    except R.RunError as exc:
        return _err(exc, 409)


@app.post("/api/runs/<run_id>/postprocess")
def api_postprocess(run_id):
    try:
        run = store.get(run_id)
    except R.RunError as exc:
        return _err(exc, 404)
    retry = R.RETRY_TARGET          # one definition, in runs.py, tested against LEGAL
    if run.state in retry:
        force = bool((request.get_json(silent=True) or {}).get("skip_qc_bundle"))
        extra = {}
        if run.state == "FAILED_QC" and force:
            # Recorded ON THE RUN, never on the shared worker. Flipping the
            # worker's flag would disable the guard for every later run, silently
            # and with no trace of who did it or when.
            extra = {"results": {"skip_qc_bundle": True}}
        run = store.transition(run_id, retry[run.state],
                               detail="retry requested"
                                      + (" (QC bundle waived for this run)" if force else ""),
                               **extra)
    elif run.state not in (R.STOPPED, R.QC, R.STRIPPED, R.UPLOAD_PENDING):
        return _err(f"run is {run.state}; nothing to post-process", 409)
    worker.submit(run_id)
    return jsonify({"queued": run_id, "state": run.state})


@app.get("/api/nas")
def api_nas():
    return jsonify(nas_upload.nas_status())


# --------------------------------------------------------------------------- #
# the page
# --------------------------------------------------------------------------- #
@app.get("/")
def index():
    if not (DIST / "index.html").exists():
        return ("<h1>eeg-recorder</h1><p>The page is missing: expected "
                f"<code>{DIST / 'index.html'}</code>.</p>"
                "<p>The API is live at <code>/api/state</code>.</p>", 200)
    return send_from_directory(DIST, "index.html")


@app.get("/<path:path>")
def static_files(path):
    if (DIST / path).is_file():
        return send_from_directory(DIST, path)
    return send_from_directory(DIST, "index.html")


def main() -> int:
    sched.start()
    worker.start()
    print(f"eeg-recorder on http://{HOST}:{PORT}  (raw -> {RAW_ROOT})", flush=True)
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

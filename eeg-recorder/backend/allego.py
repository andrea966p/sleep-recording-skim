#!/usr/bin/env python3
"""allego.py -- start, stop and inspect the Allego recorder, safely, per port.

WHAT THIS WRAPS, AND WHY IT IS NOT JUST AllegoClient

Since 2026-10-28 this talks to Allego 4.1.2 (server (5, 8, 0)) through
`radiens_core.AllegoClient` 0.1.2. The old `radiens` 4.0.0 client cannot
authenticate to Allego 4 (`RpcException ... Error code: 16`), and the two
packages cannot be loaded in one process (`duplicate file name common.proto`),
so nothing here may import `radiens`. Each fact below says what was true for
radiens 4.0.0 and what was measured on the rig on 2026-10-28.

1. THE RECORDING CONFIG CAN ONLY BE SET WHILE NO PORT RECORDS.
   radiens 4.0.0: `set_recording_config()` was broken (it never set the required
   `recordingType` enum) and a failed config SILENTLY LEFT THE OLD PATH IN PLACE,
   so `configure()` built the protobuf by hand.
   2026-10-28: `update_recording_config()` works, but it is REFUSED while any
   port records (`recorder::No setting file name while recording is on`). Base
   path, base name and `split_files_by_port` are shared by every port, so
   `ensure_config()` sets them only when the whole rig is idle, and otherwise
   VERIFIES that the current config is exactly what this start needs and refuses
   if not. Either way the config is read back: a recording is never started on
   a path we did not check.

2. THE STATUS DOES NOT SAY WHERE THE FILE IS.
   radiens 4.0.0: `get_status().recording.path` reported the CALLING PROCESS'S
   CWD, not the output directory.
   2026-10-28: there is no path on the status at all, and
   `recording.active_filename` is ONE name for the whole rig, not per port, so
   it cannot find a port's file either. The file is found on disk: the NEW
   `<dest>/<base>_port<X>_<N>__uid<MMDD-HH-MM-SS>_data.xdat` that was not there
   before this start. The only proof a recording is real is bytes on disk.

3. RECORDING IS PER PORT.
   radiens 4.0.0: recording was GLOBAL -- no `start_recording(port=...)`, one
   press recorded all four ports into one 262-channel file, and per-user
   separation happened afterwards, by stripping.
   2026-10-28: `start_recording(port="a")` / `stop_recording(port="a")` work.
   Ports A and B recorded concurrently into separate files; stopping A froze A's
   file while B kept growing. With `split_files_by_port=True` (the permanent
   setting, Andrea 2026-10-28) each port gets its own 35-channel file (32 amp +
   aux_1, din_1, dout_1) and N increments per port. Two hazards follow, and
   both are guarded here:
     - `stop_recording()` WITHOUT a port stops EVERY port, i.e. somebody else's
       run. Nothing in this module calls it without a port.
     - a second `start_recording(port=X)` on a port that is already ON is
       silently accepted and makes NO new file, so preflight refuses it.
   Streaming is shared too: it is started only if it is off (and only then do
   the amplifiers get a settle), and stopped only when no port records any more.

4. THE FILE SIZE LAGS ~30 SECONDS. Measured on the rig 2026-09-11: after a
   perfectly healthy start the file EXISTS immediately but `os.path.getsize()`
   returns 0 for a full 30 s, then jumps straight to ~31 MB (30,208 samples =
   30.2 s at 1 kHz). Allego flushes metadata in ~30 s blocks. Still true on
   Allego 4.1.2 (2026-10-28: per-port data file 0 bytes at +3 s, 4.2 MB at +43 s).

   This is the single easiest way to get this wrong. An 11-second growth check
   declares a healthy recording dead -- I wrote one and it did exactly that. So
   verification is TWO STAGES:
       start()            file exists and the port's mode is ON  -- immediate
       confirm_growing()  size increased                         -- needs >= 35 s
   and any code that asserts on growth MUST stop the recorder in a `finally`,
   or a false negative leaves the amplifiers running.

5. A FRESH OR RESTARTED ALLEGO RUNS AT THE WRONG RATE. Preflight therefore checks
   the MODE and SAMPLE RATE, not just that something answers.
   radiens 4.0.0: the mode was `XDAQ_ONE_REC` and a fresh launch came up at
   30 kHz in SMARTBOX_PRO.
   2026-10-28: the mode is `XDAQ_CORE_REC` (read from
   `get_core_config().backbone_mode`; `XDAQ_ONE_REC` is wrong on Allego 4). A
   FRESH LAUNCH of Allego 4.1.2 came up at 30000 Hz with
   split_files_by_port=False (neither is kept across launches), and `restart()`
   also RESETS THE RATE TO 30000 Hz. `status()` flags both; `ensure_config()`
   enforces split=True at every start; `restart()` sets 1000 Hz back.
   🔴 Setting the rate is NOT enough on its own (2026-10-28): after
   `update_core_config(samp_freq=1000.0)` then `start_streaming()` the stream
   was DEAD -- `primary_cache_t_range` stayed [0.0, 0.0] and allegoserver logged
   `raklib::getSignals API error: Too few amp signals allocated in stream_array`
   every 200 ms. `stop_streaming()`, `scan_ports()`, `start_streaming()` fixed it
   (0.998x). So a rate change is always: not streaming, samp_freq, scan_ports,
   re-assert the recording config, start streaming, measure.
   The enums are IntEnum (`str(RecordMode.ON) == "1"`), so every comparison
   below uses `.name`; the old string compares against "R_ON"/"XDAQ_ONE_REC"
   would fail silently.
   The rate label itself can lie (2026-09-30: said 1000 Hz, streamed 30 kHz),
   and a stream can be ON and dead (above), so `status()` measures the stream
   clock against the wall clock: `measured_rate` is a RATIO, stream seconds per
   wall second, ~1.0 when honest, ~0 when dead. Not Hz.

6. IMPEDANCE AND RESTART NEED THE WHOLE RIG IDLE. 2026-10-28:
   `get_intan_impedance()` is REFUSED while streaming (`Z_measure attempted
   during data acq`), and `restart()` and `update_core_config()` fail while
   streaming. Streaming is shared by every port, so both refuse unless NO port
   records, and put streaming back the way they found it.
"""
from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

EXPECT_MODE = "XDAQ_CORE_REC"
EXPECT_FS = 1000.0
PORT_LETTERS = "ABCDEFGH"

# Measured: the .xdat size updates in ~30 s blocks. Anything under this is a
# false negative. Do NOT tune it down without re-measuring on the rig.
SIZE_FLUSH_S = 30.0
GROWTH_WINDOW_S = 40.0

# measured_rate: stream seconds per wall second. Honest is ~1.0; the 2026-09-30
# fault was 30x. Polls closer together than RATE_MIN_WINDOW_S keep the previous
# value rather than dividing by a tiny interval.
RATE_OK = (0.9, 1.1)
RATE_MIN_WINDOW_S = 5.0


class AllegoError(RuntimeError):
    """Something is wrong with the recorder. Never swallowed, never guessed past."""


class PreflightFailed(AllegoError):
    """A precondition for starting was not met. Nothing was started."""


# --------------------------------------------------------------------------- #
# the client: one per process, it is a gRPC channel pool
# --------------------------------------------------------------------------- #
_CLIENT = None
_CLIENT_LOCK = threading.Lock()


def _client():
    global _CLIENT
    with _CLIENT_LOCK:
        if _CLIENT is None:
            from radiens_core import AllegoClient
            _CLIENT = AllegoClient()
        return _CLIENT


def _drop_client() -> None:
    """Forget the client after a failure, so the next call reconnects (Allego may
    have been relaunched under us).

    NEVER close() it: other threads (a restart, an impedance measurement, a
    stop) may still hold the same object, and a closed ChannelPool makes every
    one of their later calls raise "ChannelPool is closed" -- part-way through,
    with streaming not restored. The old pool is left to the garbage collector."""
    global _CLIENT
    with _CLIENT_LOCK:
        _CLIENT = None


def _port_mode(rec, port: str) -> str | None:
    """'ON'/'OFF' for one port, None if the server does not report it."""
    m = getattr(rec, f"record_mode_port_{port.lower()}", None)
    return m.name if m is not None else None


def _any_recording(s) -> bool:
    return s.recording.record_mode.name == "ON"


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #

def server_running() -> bool:
    """Process-level check. Genuinely different from gRPC-reachable: the server
    can be up while the client cannot authenticate, and the GUI can be gone while
    the server keeps running (and spinning a core -- see the vault).

    Allego 3 ran `allegoserver hardware`; Allego/Videre 4.1.2 (2026-10-28) runs
    `/opt/videre/resources/radix/allegoserver/radiensserver`. Either counts."""
    try:
        return subprocess.run(
            ["pgrep", "-f", "allegoserver( hardware|/radiensserver)"],
            capture_output=True, timeout=5).returncode == 0
    except Exception:
        return False


_RATE: dict = {}
_RATE_LOCK = threading.Lock()


def _track_rate(streaming_on: bool, t_range) -> float | None:
    """Stream clock vs wall clock, from consecutive status() calls.

    Costs nothing: it reuses the `primary_cache_t_range` the poll already read,
    so /api/state never sleeps to measure. The first poll after streaming starts
    returns None; a value appears once two polls are RATE_MIN_WINDOW_S apart.
    """
    with _RATE_LOCK:
        if not streaming_on or not t_range or len(t_range) < 2:
            _RATE.clear()
            return None
        now, end = time.monotonic(), float(t_range[1])
        if "wall" not in _RATE or end < _RATE["end"]:     # first poll, or stream restarted
            _RATE.update(wall=now, end=end, rate=None)
        elif now - _RATE["wall"] >= RATE_MIN_WINDOW_S:
            _RATE.update(rate=round((end - _RATE["end"]) / (now - _RATE["wall"]), 3),
                         wall=now, end=end)
        return _RATE.get("rate")


def _measure_rate(c, window_s: float = 10.0) -> float:
    """The same ratio, measured now, blocking. For restart(), not for the poll."""
    e0, t0 = float(c.get_status().streaming.primary_cache_t_range[1]), time.monotonic()
    time.sleep(window_s)
    e1, t1 = float(c.get_status().streaming.primary_cache_t_range[1]), time.monotonic()
    return round((e1 - e0) / (t1 - t0), 3)


def port_counts(st: dict) -> dict:
    """{port: channel_count}, the shape layout.check() and the scheduler's
    missing-headstage check take."""
    return {p: int(i.get("channels") or 0) for p, i in (st.get("ports") or {}).items()}


def status() -> dict:
    """Everything the UI needs for the Allego pill, plus why it is unhappy.

    `ports` is {port: {channels, recording, run_id, owner, file, bytes}}; this
    module knows nothing about runs, so run_id/owner/file/bytes are None here and
    app.py fills them in. Use `port_counts()` for the old {port: n} shape.
    """
    out = {"server_running": server_running(), "reachable": False,
           "recording": None, "streaming": None, "system_mode": None,
           "sample_freq": None, "measured_rate": None,
           "split_files_by_port": None, "base_path": None, "base_name": None,
           "recording_type": None, "server_version": None, "ports": {}, "problems": [],
           "healthy": False, "error": None}
    try:
        c = _client()
        s = c.get_status()
        cc = c.get_core_config()
        rc = c.get_recording_config()
        ver = c.server_version
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        _drop_client()
        _track_rate(False, None)
        return out

    streaming = s.streaming.stream_mode.name
    out.update(
        reachable=True,
        recording=s.recording.record_mode.name,
        streaming=streaming,
        system_mode=cc.backbone_mode.name,
        sample_freq=float(cc.base_samp_freq),
        measured_rate=_track_rate(streaming == "ON", s.streaming.primary_cache_t_range),
        split_files_by_port=bool(rc.split_files_by_port),
        base_path=rc.base_file_path, base_name=rc.base_file_name,
        recording_type=rc.recording_type.name,
        server_version=".".join(str(v) for v in ver),
        ports={pc.port.name: {"channels": int(pc.channel_count),
                              "recording": _port_mode(s.recording, pc.port.name) == "ON",
                              "run_id": None, "owner": None, "file": None,
                              "bytes": None}
               for pc in (s.ports or [])},
    )

    problems = []
    if out["system_mode"] != EXPECT_MODE:
        problems.append(
            f"system mode is {out['system_mode']}, expected {EXPECT_MODE}. The "
            "mode is fixed at launch; restart() keeps whatever mode is in use.")
    if out["sample_freq"] != EXPECT_FS:
        problems.append(
            f"sample rate is {out['sample_freq']} Hz, expected {EXPECT_FS}. A "
            "fresh launch or a restart() comes up at 30 kHz.")
    r = out["measured_rate"]
    if r is not None and r < 0.1:
        problems.append(
            f"streaming is ON but the stream is not advancing ({r:.2f}x real "
            "time): a dead stream records nothing. 2026-10-28 fix: stop "
            "streaming, scan_ports(), start streaming (Restart Allego does this).")
    elif r is not None and not RATE_OK[0] <= r <= RATE_OK[1]:
        problems.append(
            f"the stream runs {r:.2f}x real time; the {out['sample_freq']} Hz "
            "label can lie (2026-09-30). Restart Allego before recording.")
    if not out["split_files_by_port"]:
        problems.append(
            "split_files_by_port is False: every port would go into ONE file. It "
            "can only be changed while no port records; the next start sets it.")
    if not any(i["channels"] for i in out["ports"].values()):
        problems.append("no ports enumerate any channels -- is a headstage connected?")
    out["problems"] = problems
    out["healthy"] = out["reachable"] and out["server_running"] and not problems
    return out


# --------------------------------------------------------------------------- #
# configuration
# --------------------------------------------------------------------------- #

def _config_diff(rc, dest: Path, base_name: str) -> list[str]:
    """What in the live recording config differs from what a start needs."""
    diff = []
    if Path(rc.base_file_path).resolve() != dest.resolve():
        diff.append(f"base path is {rc.base_file_path}, need {dest}")
    if rc.base_file_name != base_name:
        diff.append(f"base name is {rc.base_file_name!r}, need {base_name!r}")
    if not rc.split_files_by_port:
        diff.append("split_files_by_port is False, need True")
    if not rc.time_stamp:
        diff.append("time_stamp is False, need True (the __uid in the name)")
    if rc.recording_type.name != "CONTINUOUS":
        diff.append(f"recording type is {rc.recording_type.name}, need CONTINUOUS")
    return diff


def ensure_config(dest_dir: str | Path, base_name: str = "allego") -> None:
    """Make sure the next recording is written where we think. Raises if not.

    Rig idle: set path, name, split=True, continuous, and read it back.
    Some port recording: the config cannot be changed (fact 1), so verify it is
    already exactly this, and refuse otherwise. A silent mismatch is the
    dangerous case -- the recording would land wherever the config points.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)          # Allego refuses a missing path
    c = _client()
    rc = c.get_recording_config()
    if _any_recording(c.get_status()):
        diff = _config_diff(rc, dest, base_name)
        if diff:
            raise PreflightFailed(
                "another port is recording, so the recording config cannot be "
                "changed, and it is not what this start needs: " + "; ".join(diff))
        return
    from radiens_core.models.status import DataRecordingType
    try:
        c.update_recording_config(rc.model_copy(update={
            "base_file_path": str(dest), "base_file_name": base_name,
            "split_files_by_port": True, "time_stamp": True,
            "recording_type": DataRecordingType.CONTINUOUS,
            "datasource_idx": 0}))           # not reported by get, so set it explicitly
    except Exception as exc:
        raise AllegoError(f"update_recording_config failed: {exc}. The recording "
                          "path was NOT changed.") from exc
    diff = _config_diff(c.get_recording_config(), dest, base_name)
    if diff:
        raise AllegoError("recording config did not take: " + "; ".join(diff))


# --------------------------------------------------------------------------- #
# preflight
# --------------------------------------------------------------------------- #

def preflight(dest_dir: str | Path, ports=None, *, min_free_gb: float = 150.0) -> dict:
    """Everything that must be true before starting `ports`. Raises PreflightFailed.

    `ports=None` means every port that enumerates channels (standalone tools).
    Another port recording is NOT a reason to refuse -- that is the point of
    per-port recording. A requested port that enumerates nothing is not a refusal
    either, as long as one requested port does: it is returned in `missing`, not
    recorded, and the scheduler warns about it (a missing headstage warns, it
    never blocks -- scheduler.py).
    """
    st = status()
    fails = []
    if not st["server_running"]:
        fails.append("allegoserver is not running")
    if not st["reachable"]:
        fails.append(f"Allego is not reachable over gRPC ({st['error']})")
        raise PreflightFailed("; ".join(fails))
    if st["system_mode"] != EXPECT_MODE:
        fails.append(f"system mode is {st['system_mode']}, expected {EXPECT_MODE}")
    if st["sample_freq"] != EXPECT_FS:
        fails.append(f"sample rate is {st['sample_freq']} Hz, expected {EXPECT_FS}")
    r = st["measured_rate"]
    if r is not None and not RATE_OK[0] <= r <= RATE_OK[1]:
        fails.append(f"the stream runs {r:.2f}x real time; restart Allego")

    live = st["ports"]
    want = sorted(ports) if ports else sorted(p for p, i in live.items() if i["channels"])
    present = [p for p in want if (live.get(p) or {}).get("channels")]
    missing = [p for p in want if p not in present]
    if not present:
        fails.append(f"none of ports {', '.join(want) or '(none)'} enumerates any "
                     "channels -- is a headstage connected?")
    for p in present:
        if live[p]["recording"]:
            fails.append(f"port {p} is ALREADY recording -- refusing; a second start "
                         "on a recording port is accepted silently and makes no file")

    dest = Path(dest_dir)
    try:
        dest.mkdir(parents=True, exist_ok=True)
        vfs = os.statvfs(dest)
        free_gb = vfs.f_bavail * vfs.f_frsize / 1e9
        if free_gb < min_free_gb:
            fails.append(f"only {free_gb:.0f} GB free at {dest}, need {min_free_gb:.0f}")
    except OSError as exc:
        fails.append(f"cannot use destination {dest}: {exc}")
        free_gb = 0.0

    if fails:
        raise PreflightFailed("; ".join(fails))
    return {"ok": True, "free_gb": round(free_gb, 1), "status": st,
            "ports": present, "missing": missing}


# --------------------------------------------------------------------------- #
# start / stop
# --------------------------------------------------------------------------- #

def stop(ports, *, settle_s: float = 2.0, stop_streaming: bool = True) -> dict:
    """Stop recording on `ports`, one port at a time, and verify each is OFF.

    `ports` is REQUIRED and names exactly the ports the caller started. Never
    calls `stop_recording()` without a port: that stops EVERY port, i.e. other
    people's runs (fact 3). Every port is tried even if an earlier one raised,
    and the errors are raised together at the end, so one bad port cannot leave
    the others running. Streaming is stopped only when no port records any more.

    Safe to call when the ports are already stopped; that is deliberate, because
    this is what error paths call in their `finally`.
    """
    if not ports:
        raise ValueError("stop() needs the ports to stop; it never stops every port")
    c = _client()
    s = c.get_status()
    ports = sorted(ports)
    before = {p: _port_mode(s.recording, p) for p in ports}
    errors = []
    for p in ports:
        if before[p] != "OFF":                      # ON, or not reported
            try:
                c.stop_recording(port=p)
            except Exception as exc:
                errors.append(f"port {p}: {type(exc).__name__}: {exc}")
    time.sleep(settle_s)
    s = c.get_status()
    after = {p: _port_mode(s.recording, p) for p in ports}
    streaming_stopped = False
    if stop_streaming and not _any_recording(s):
        try:
            c.stop_streaming()
            streaming_stopped = True
        except Exception:
            pass
    still = [p for p in ports if after[p] == "ON"]
    if still:
        errors.append(f"stop_recording did not take on port(s) {', '.join(still)}")
    if errors:
        raise AllegoError("; ".join(errors))
    return {"ports": ports, "before": before, "after": after,
            "streaming_stopped": streaming_stopped}


def _port_glob(base_name: str, port: str) -> str:
    return f"{base_name}_port{port}_*__uid*_data.xdat"


def newest_port_files(dest_dir: str | Path, ports, since: float,
                      base_name: str = "allego") -> dict:
    """{port: {base_name, data_path}}: each port's newest file written at or
    after `since` (epoch s). For adopting a start the service died in the
    middle of; a port with no such file is left out."""
    out = {}
    for p in ports:
        new = [f for f in Path(dest_dir).glob(_port_glob(base_name, p))
               if f.stat().st_mtime >= since]
        if new:
            f = max(new, key=lambda f: f.stat().st_mtime)
            out[p] = {"base_name": f.name[:-len("_data.xdat")], "data_path": str(f)}
    return out


def start(dest_dir: str | Path, ports=None, *, base_name: str = "allego",
          settle_s: float = 20.0, min_free_gb: float = 150.0,
          progress: Callable[[str], None] | None = print) -> dict:
    """Configure, stream, record `ports`. Returns as soon as each port's file
    EXISTS and its mode is ON.

    Returns {"port_files": {port: {base_name, data_path}}, ...} plus the old keys
    (base_name/base_path/data_path of the FIRST port, mode, started_at, dest, and
    `ports` = the live {port: channel_count} enumeration) so existing callers and
    the scheduler's missing-headstage check keep working. Ports that enumerate
    nothing are skipped and listed in `skipped_ports`.

    Growth is NOT checked here -- the size lags ~30 s, so checking now would
    always fail. Call `confirm_growing()` per file afterwards.

    If anything raises after a port was told to start, ONLY the ports this call
    started are stopped before the exception propagates. A half-started port left
    ON is how a false negative turns into an unattended recording nobody knows
    about; stopping a port this call did not start would end someone else's run.
    """
    say = progress or (lambda _m: None)
    dest = Path(dest_dir)
    pf = preflight(dest, ports, min_free_gb=min_free_gb)
    st, todo = pf["status"], pf["ports"]
    ensure_config(dest, base_name)
    say(f"configured -> {dest} (split by port)")

    c = _client()
    if c.get_status().streaming.stream_mode.name != "ON":
        c.start_streaming()
        say("streaming on; letting the amplifiers settle")
        time.sleep(settle_s)
    else:
        say("streaming already on (another port may be recording); not touching it")
    # The poll measures the rate only once two polls are 5 s apart, so a start
    # can arrive with none: measure it now rather than record on a stream that
    # may be dead or 30x (fact 5). Nothing is engaged yet.
    rate = st["measured_rate"]
    if rate is None:
        rate = _measure_rate(c, 5.0)
        if not RATE_OK[0] <= rate <= RATE_OK[1]:
            raise PreflightFailed(f"the stream runs {rate:.2f}x real time (measured "
                                  "over 5 s); refusing to record. Restart Allego.")

    before = {p: set(dest.glob(_port_glob(base_name, p))) for p in todo}
    engaged: list[str] = []
    started_at = time.time()
    try:
        for p in todo:
            # Re-read right before engaging: if the port went ON since preflight
            # (someone else's start), refuse WITHOUT adding it to `engaged`, so
            # the cleanup below never stops another person's port.
            if _port_mode(c.get_status().recording, p) == "ON":
                raise PreflightFailed(f"port {p} went ON since preflight; not touching it")
            engaged.append(p)               # before the call: a raise may still have engaged it
            c.start_recording(port=p)
        time.sleep(3.0)
        s = c.get_status()
        off = [p for p in todo if _port_mode(s.recording, p) != "ON"]
        if off:
            raise AllegoError(f"start_recording did not take on port(s) {', '.join(off)}")
        files: dict = {}
        for _ in range(20):                 # the files appear within a second
            for p in todo:
                new = set(dest.glob(_port_glob(base_name, p))) - before[p]
                if new and p not in files:
                    files[p] = max(new, key=lambda f: f.stat().st_mtime)
            if len(files) == len(todo):
                break
            time.sleep(0.5)
        lost = [p for p in todo if p not in files]
        if lost:
            raise AllegoError(
                f"port(s) {', '.join(lost)} report ON but no new "
                f"{_port_glob(base_name, lost[0])} appeared in {dest}. The "
                "recording config may not be what we think.")
        port_files = {p: {"base_name": f.name[:-len("_data.xdat")], "data_path": str(f)}
                      for p, f in files.items()}
        first = port_files[todo[0]]
        say("started: " + ", ".join(f"{p} {v['base_name']}" for p, v in port_files.items()))
        return {"port_files": port_files, "base_name": first["base_name"],
                "base_path": str(dest / first["base_name"]),
                "data_path": first["data_path"], "mode": "ON",
                "started_at": started_at, "dest": str(dest),
                "ports": port_counts(st), "skipped_ports": pf["missing"],
                "measured_rate": rate}
    except BaseException:
        if engaged:
            say(f"start failed after port(s) {', '.join(engaged)} were engaged -- "
                "stopping ONLY those")
            try:
                stop(engaged)
            except Exception as exc:
                say(f"WARNING: could not stop cleanly: {exc}")
        raise


# --------------------------------------------------------------------------- #
# rig-wide operations: impedance, restart. Whole rig idle only (fact 6).
# --------------------------------------------------------------------------- #

def _ntv_labels(md) -> dict:
    """{ntv_chan_idx: "A/1"} from the live channel metadata.

    Read 2026-10-28: ntv 0..127 run A, B, C, D in blocks of 32, and the
    metadata's `site_nums` are 1..32 WITHIN each port (ntv 32 = port_B_32 is
    site 1). The console and the vault name channels `<port>/<site>` 1-based
    (A/1, A/2, A/33 for the second chip on a splitter), so the label is
    `<port>/<site_num>`. Taken from the metadata, not from ntv // 32, so a
    port with a splitter (64 channels) still maps right.
    """
    from radiens_core.models.signals import SignalType
    amp = SignalType.AMP
    return {int(n): f"{p.name}/{int(site)}"
            for n, p, site in zip(md.sig_map[amp].ntv, md.ports[amp], md.site_nums[amp])
            if p is not None}


def selected_counts() -> dict:
    """{port: number of SELECTED amp channels}, from the live channel metadata.
    Read-only; {} if Allego cannot answer. Not part of status(): /api/state
    polls, /api/ports is asked."""
    try:
        from radiens_core.models.signals import SignalType
        md = _client().get_channel_metadata()
        port_of = dict(zip(md.sig_map[SignalType.AMP].ntv, md.ports[SignalType.AMP]))
        out: dict = {}
        for n in md.selected_sig_map[SignalType.AMP].ntv:
            if port_of.get(n) is not None:
                out[port_of[n].name] = out.get(port_of[n].name, 0) + 1
        return out
    except Exception:
        return {}


def impedance(port: str) -> dict:
    """Measure one port's impedance. Refuses unless no port records.

    Stops streaming (the measurement is refused while streaming), measures
    (~31 s on 2026-10-28), and puts streaming back if it was on. The server
    returns 128 values for all ports; only the requested port's are kept.
    """
    port = str(port).upper()
    c = _client()
    s = c.get_status()
    if _any_recording(s):
        raise PreflightFailed("a port is recording; impedance needs streaming off, "
                              "and streaming is shared by every port")
    labels = _ntv_labels(c.get_channel_metadata())
    was_streaming = s.streaming.stream_mode.name == "ON"
    t0 = time.time()
    if was_streaming:
        c.stop_streaming()
        time.sleep(1.0)
    try:
        imp = c.get_intan_impedance(port.lower())
    finally:
        if was_streaming:
            c.start_streaming()
    chans = [{"ntv_chan_idx": v.ntv_chan_idx, "label": labels[v.ntv_chan_idx],
              "kohm": round(v.magnitude_ohm / 1e3, 1), "phase_deg": round(v.phase_deg, 1)}
             for v in imp.measurements
             if labels.get(v.ntv_chan_idx, "").startswith(f"{port}/")]
    return {"port": port,
            "measured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration_s": round(time.time() - t0, 1), "channels": chans}


def restart() -> dict:
    """Restart Allego in the mode ALREADY in use, and put 1000 Hz back.

    🛑 The mode is read from the server, never taken from a caller: restarting
    into another mode is a licence question (contract, 2026-10-28). Refuses
    unless no port records. Sequence, each step named in the error if it fails:
    stop streaming, restart(mode), samp_freq 1000 (restart resets it to
    30 kHz), scan_ports() (without it the stream comes back DEAD, fact 5),
    re-assert split_files_by_port=True, start streaming, measure the stream
    rate over ~10 s and fail loudly unless it is ~1.0x. Returns before/after.
    """
    c = _client()
    s = c.get_status()
    if _any_recording(s):
        raise PreflightFailed("a port is recording; restart would end it")
    cc, rc = c.get_core_config(), c.get_recording_config()
    mode = cc.backbone_mode
    before = {"system_mode": mode.name, "sample_freq": float(cc.base_samp_freq),
              "streaming": s.streaming.stream_mode.name,
              "split_files_by_port": bool(rc.split_files_by_port)}
    t0 = time.time()
    step = "stop streaming"
    try:
        if before["streaming"] == "ON":
            c.stop_streaming()
            time.sleep(1.0)
        step = f"restart(mode={mode.name})"
        c.restart(mode=mode)
        time.sleep(3.0)
        step = f"set sample rate {EXPECT_FS} Hz"
        c.update_core_config(samp_freq=EXPECT_FS)
        step = "scan_ports()"
        c.scan_ports()
        step = "re-assert split_files_by_port=True"
        c.update_recording_config(rc.model_copy(update={"split_files_by_port": True,
                                                        "datasource_idx": 0}))
        step = "start streaming"
        c.start_streaming()
        time.sleep(2.0)
        step = "measure the stream rate"
        rate = _measure_rate(c, 10.0)
        cc2, rc2 = c.get_core_config(), c.get_recording_config()
    except Exception as exc:
        raise AllegoError(f"restart failed at step '{step}': {type(exc).__name__}: "
                          f"{exc}. Allego may be at 30 kHz or not streaming: check "
                          "it before any recording.") from exc
    after = {"system_mode": cc2.backbone_mode.name, "sample_freq": float(cc2.base_samp_freq),
             "streaming": c.get_status().streaming.stream_mode.name,
             "split_files_by_port": bool(rc2.split_files_by_port), "measured_rate": rate}
    bad = []
    if after["system_mode"] != before["system_mode"]:
        bad.append(f"mode changed {before['system_mode']} -> {after['system_mode']}")
    if after["sample_freq"] != EXPECT_FS:
        bad.append(f"sample rate is {after['sample_freq']} Hz")
    if not RATE_OK[0] <= rate <= RATE_OK[1]:
        bad.append(f"stream runs {rate:.2f}x real time")
    if not after["split_files_by_port"]:
        bad.append("split_files_by_port is False")
    if bad:
        raise AllegoError("restart finished but the rig is not right: " + "; ".join(bad)
                          + f". before={before} after={after}")
    return {"before": before, "after": after, "duration_s": round(time.time() - t0, 1)}


# --------------------------------------------------------------------------- #
# growth, per file
# --------------------------------------------------------------------------- #

def confirm_growing(data_path: str | Path, *, window_s: float = GROWTH_WINDOW_S,
                    progress: Callable[[str], None] | None = print) -> dict:
    """Prove bytes are landing in ONE file. Needs a window longer than the ~30 s flush.

    Returns {'growing': bool, ...}. Does NOT raise on "not growing" -- the caller
    decides, because the right response depends on whether an animal is on the rig.
    """
    say = progress or (lambda _m: None)
    p = Path(data_path)
    if window_s < SIZE_FLUSH_S + 5:
        raise ValueError(
            f"window_s={window_s} is shorter than the measured ~{SIZE_FLUSH_S:.0f} s "
            "size-flush interval; it would report a healthy recording as dead")
    a = p.stat().st_size if p.exists() else -1
    t0 = time.time()
    time.sleep(window_s)
    b = p.stat().st_size if p.exists() else -1
    dt = time.time() - t0
    gb_h = (b - a) / dt * 3600 / 1e9 if b > a else 0.0
    say(f"  {a:,} -> {b:,} bytes in {dt:.0f} s ({gb_h:.2f} GB/h)")
    return {"growing": b > a >= 0, "bytes_start": a, "bytes_end": b,
            "window_s": round(dt, 1), "gb_per_h": round(gb_h, 2)}


def bytes_now(data_path: str | Path) -> int:
    p = Path(data_path)
    return p.stat().st_size if p.exists() else -1


if __name__ == "__main__":
    print(json.dumps(status(), indent=2))

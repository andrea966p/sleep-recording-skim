#!/usr/bin/env python3
"""allego.py -- start, stop and inspect the Allego recorder, safely.

WHAT THIS WRAPS, AND WHY IT IS NOT JUST AllegoClient

1. `set_recording_config()` IS BROKEN in radiens 4.0.0. `allego.ConfigRecording`
   has a required `recordingType` enum that `radiens/api/api_allego.py` never
   sets, so the message fails to serialise. Worse, a failed config SILENTLY
   LEAVES THE OLD PATH IN PLACE, so the next recording lands wherever the last
   one did. `configure()` builds the protobuf directly, the way
   `eeg-emg-analysis/qc/set_recording_config_fixed.py` does.

2. `get_status().recording.path` LIES -- it reports the CALLING PROCESS'S CWD,
   not the output directory. Never trust it. The destination is whatever we
   configured, and the only proof a recording is real is bytes on disk.

3. RECORDING IS GLOBAL. radiens 4.0.0 exposes no `start_recording(port=...)`
   whatever the upstream docs say; the installed client has `set_recording(mode)`
   and `RecordMode` is {OFF, ON}. One press records all four ports into one file.
   Per-user separation happens afterwards, by stripping.

4. THE FILE SIZE LAGS ~30 SECONDS. Measured on the rig 2026-09-11: after a
   perfectly healthy start the file EXISTS immediately but `os.path.getsize()`
   returns 0 for a full 30 s, then jumps straight to ~31 MB (30,208 samples =
   30.2 s at 1 kHz). Allego flushes metadata in ~30 s blocks.

   This is the single easiest way to get this wrong. An 11-second growth check
   declares a healthy recording dead -- I wrote one and it did exactly that. So
   verification is TWO STAGES:
       started()          file exists and mode == R_ON      -- immediate
       confirm_growing()  size increased                    -- needs >= 35 s
   and any code that asserts on growth MUST stop the recorder in a `finally`,
   or a false negative leaves the amplifiers running.

5. A fresh Allego can come up at 30 kHz in SMARTBOX_PRO. Preflight therefore
   checks the MODE and SAMPLE RATE, not just that something answers.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Callable

ALLEGO_GRPC = "127.0.0.1:50051"
EXPECT_MODE = "XDAQ_ONE_REC"
EXPECT_FS = 1000.0

# Measured: the .xdat size updates in ~30 s blocks. Anything under this is a
# false negative. Do NOT tune it down without re-measuring on the rig.
SIZE_FLUSH_S = 30.0
GROWTH_WINDOW_S = 40.0


class AllegoError(RuntimeError):
    """Something is wrong with the recorder. Never swallowed, never guessed past."""


class PreflightFailed(AllegoError):
    """A precondition for starting was not met. Nothing was started."""


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #

def server_running() -> bool:
    """Process-level check. Genuinely different from gRPC-reachable: the server
    can be up while the client cannot authenticate, and the GUI can be gone while
    `allegoserver` keeps running (and spinning a core -- see the vault)."""
    try:
        return subprocess.run(["pgrep", "-f", "allegoserver hardware"],
                              capture_output=True, timeout=5).returncode == 0
    except Exception:
        return False


def status() -> dict:
    """Everything the UI needs for the Allego pill, plus why it is unhappy."""
    out = {"server_running": server_running(), "reachable": False,
           "recording": None, "streaming": None, "system_mode": None,
           "sample_freq": None, "ports": {}, "base_name": None, "error": None}
    try:
        from radiens import AllegoClient
        s = AllegoClient().get_status()
        out.update(
            reachable=True,
            recording=str(s.recording.mode),
            streaming=str(s.stream.mode),
            system_mode=str(s.system_mode).replace("SystemMode.", ""),
            sample_freq=float(s.sample_freq),
            base_name=s.recording.base_name,
            ports={str(p).replace("Port.", ""): n
                   for p, n in (s.port_num_channels or {}).items()},
        )
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    problems = []
    if out["system_mode"] != EXPECT_MODE:
        problems.append(
            f"system mode is {out['system_mode']}, expected {EXPECT_MODE}. A "
            "freshly launched Allego comes up in SMARTBOX_PRO; the mode is fixed "
            "at launch and cannot be changed from the API.")
    if out["sample_freq"] != EXPECT_FS:
        problems.append(
            f"sample rate is {out['sample_freq']} Hz, expected {EXPECT_FS}. A "
            "fresh launch comes up at 30 kHz.")
    if not out["ports"]:
        problems.append("no ports enumerate any channels -- is a headstage connected?")
    out["problems"] = problems
    out["healthy"] = out["reachable"] and out["server_running"] and not problems
    return out


# --------------------------------------------------------------------------- #
# configuration
# --------------------------------------------------------------------------- #

def configure(dest_dir: str | Path, base_name: str = "allego",
              *, datasource_idx: int = 0) -> None:
    """Set where the next recording is written. Raises if it does not take.

    Builds `ConfigRecording` directly because the client's own
    `set_recording_config()` never sets the required `recordingType` enum. A
    silent failure here is the dangerous case -- the recording would go to
    whatever path was configured last -- so this raises rather than returning a
    status.
    """
    import grpc
    import radiens.utils.interceptors as itc
    from radiens.allego_client import AllegoClient
    from radiens.grpc_radiens import allegoserver_pb2 as ap, allegoserver_pb2_grpc as ag

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)

    c = AllegoClient()
    c.get_status()                     # populates the session token
    chan = grpc.intercept_channel(
        grpc.insecure_channel(ALLEGO_GRPC),
        itc.MetadataClientInterceptor(
            id_token=itc.SessionMetaData._instance._id_token))
    try:
        ag.AllegoCoreStub(chan).SetConfigRecording(
            ap.ConfigRecording(baseFileName=base_name, baseFilePath=str(dest),
                               dataSourceIdx=datasource_idx, timeStamp=True,
                               splitFilesByPort=False, forceStartAtTStamp0=False,
                               recordingType=ap.continuous),
            timeout=60)
    except Exception as exc:
        raise AllegoError(
            f"SetConfigRecording failed: {exc}. The recording path was NOT "
            "changed, and a recording started now would land wherever the "
            "previous one did.") from exc


# --------------------------------------------------------------------------- #
# preflight
# --------------------------------------------------------------------------- #

def preflight(dest_dir: str | Path, *, min_free_gb: float = 150.0) -> dict:
    """Everything that must be true before starting. Raises PreflightFailed.

    Mirrors `deploy/scheduled-recording.sh`, plus the mode and rate checks it
    does not have.
    """
    st = status()
    fails = []
    if not st["server_running"]:
        fails.append("allegoserver is not running")
    if not st["reachable"]:
        fails.append(f"Allego is not reachable over gRPC ({st['error']})")
    fails.extend(st.get("problems", []))
    if st.get("recording") == "R_ON":
        fails.append("a recording is ALREADY running (R_ON) -- refusing to disturb it")

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
    return {"ok": True, "free_gb": round(free_gb, 1), "status": st}


# --------------------------------------------------------------------------- #
# start / stop
# --------------------------------------------------------------------------- #

def _client():
    from radiens import AllegoClient
    return AllegoClient()


def stop(*, settle_s: float = 2.0, stop_streaming: bool = True) -> dict:
    """Stop recording. Verified 2026-09-11 on the rig: R_ON -> R_OFF first call.

    Safe to call when nothing is recording; that is deliberate, because this is
    what error paths call in their `finally`.
    """
    c = _client()
    before = str(c.get_status().recording.mode)
    c.set_recording("off")
    time.sleep(settle_s)
    after = str(c.get_status().recording.mode)
    if stop_streaming:
        try:
            c.set_streaming("off")
        except Exception:
            pass
    if after != "R_OFF":
        raise AllegoError(f"set_recording('off') did not take: mode is still {after}")
    return {"before": before, "after": after}


def start(dest_dir: str | Path, *, base_name: str = "allego",
          settle_s: float = 20.0, min_free_gb: float = 150.0,
          progress: Callable[[str], None] | None = print) -> dict:
    """Configure, stream, record. Returns as soon as the file EXISTS and R_ON.

    Growth is NOT checked here -- the size lags ~30 s, so checking now would
    always fail. Call `confirm_growing()` afterwards.

    If anything raises after the recorder was told to start, the recorder is
    STOPPED before the exception propagates. A half-started rig left in R_ON is
    how a false negative turns into an unattended recording nobody knows about.
    """
    say = progress or (lambda _m: None)
    dest = Path(dest_dir)
    preflight(dest, min_free_gb=min_free_gb)
    configure(dest, base_name)
    say(f"configured -> {dest}")

    c = _client()
    c.set_streaming("on")
    time.sleep(min(settle_s, 3.0) if settle_s < 3.0 else 3.0)
    say("streaming on; letting the amplifiers settle")
    remaining = max(0.0, settle_s - 3.0)
    if remaining:
        time.sleep(remaining)

    started_at = time.time()
    c.set_recording("on")
    try:
        time.sleep(3.0)
        s = c.get_status()
        name = s.recording.file_name
        mode = str(s.recording.mode)
        path = dest / f"{name}_data.xdat"
        if mode != "R_ON":
            raise AllegoError(f"set_recording('on') did not take: mode is {mode}")
        for _ in range(20):                     # the file appears within a second
            if path.exists():
                break
            time.sleep(0.5)
        if not path.exists():
            raise AllegoError(
                f"recorder reports R_ON but {path} was never created. The "
                "configured path may not be what we think -- note that "
                "get_status().recording.path reports this process's cwd, not the "
                "output directory, so it cannot be used to check.")
        say(f"started: {name} (mode {mode})")
        return {"base_name": name, "base_path": str(dest / name),
                "data_path": str(path), "mode": mode,
                "started_at": started_at, "dest": str(dest)}
    except Exception:
        say("start failed after the recorder was engaged -- stopping it")
        try:
            stop()
        except Exception as exc:
            say(f"WARNING: could not stop cleanly: {exc}")
        raise


def confirm_growing(data_path: str | Path, *, window_s: float = GROWTH_WINDOW_S,
                    progress: Callable[[str], None] | None = print) -> dict:
    """Prove bytes are landing. Needs a window longer than the ~30 s flush.

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

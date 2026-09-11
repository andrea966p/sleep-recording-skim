#!/usr/bin/env python3
"""storage.py -- how much room is left, and how long that lasts.

FREE GIGABYTES ARE THE WRONG NUMBER TO PUT IN FRONT OF SOMEONE ABOUT TO START A
24 HOUR RECORDING. "801 GB free" and "8.9 days at the current rate" are the same
fact, but only the second one answers the question being asked. So this reports
hours remaining, computed from the rate this rig actually writes.

The rate is measured, not assumed: 262 channels x 1000 Hz x 4 bytes = 1.048 MB/s
= 90.6 GB/day, and a 20 h run really does produce ~75 GB. When a recording is
live the rate is measured from the file instead, so a different channel count or
sample rate corrects itself.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

BYTES_PER_SAMPLE = 4
DEFAULT_CHANNELS = 262
DEFAULT_FS = 1000


def nominal_bytes_per_s(channels: int = DEFAULT_CHANNELS, fs: int = DEFAULT_FS) -> float:
    return channels * fs * BYTES_PER_SAMPLE


def disk(path: str | Path = "/") -> dict:
    st = os.statvfs(path)
    total = st.f_blocks * st.f_frsize
    free = st.f_bavail * st.f_frsize
    return {"path": str(path), "total_bytes": total, "free_bytes": free,
            "used_bytes": total - free,
            "used_percent": round(100 * (total - free) / total, 1) if total else 0.0}


def status(raw_root: str | Path = "/home/skimlab/radix/data",
           *, channels: int = DEFAULT_CHANNELS, fs: int = DEFAULT_FS,
           reserve_gb: float = 150.0) -> dict:
    d = disk(raw_root if Path(raw_root).exists() else "/")
    rate = nominal_bytes_per_s(channels, fs)
    usable = max(0.0, d["free_bytes"] - reserve_gb * 1e9)
    d.update(
        gb_per_hour=round(rate * 3600 / 1e9, 2),
        gb_per_day=round(rate * 86400 / 1e9, 1),
        reserve_gb=reserve_gb,
        hours_remaining=round(usable / rate / 3600, 1) if rate else None,
        days_remaining=round(usable / rate / 86400, 2) if rate else None,
        channels=channels, fs=fs,
    )
    d["level"] = ("critical" if d["hours_remaining"] is not None and d["hours_remaining"] < 24
                  else "warn" if d["hours_remaining"] is not None and d["hours_remaining"] < 72
                  else "ok")
    return d


def measure_rate(data_path: str | Path, window_s: float = 5.0) -> float | None:
    """Bytes per second from a live file. Returns None if it cannot tell.

    NOTE the size only updates every ~30 s, so a short window usually reports 0.
    That is why this returns None rather than 0.0 when nothing moved -- a caller
    must not render "0 GB/h" for a perfectly healthy recording.
    """
    p = Path(data_path)
    if not p.exists():
        return None
    a = p.stat().st_size
    time.sleep(window_s)
    b = p.stat().st_size
    return (b - a) / window_s if b > a else None


if __name__ == "__main__":
    import json
    print(json.dumps(status(), indent=2))

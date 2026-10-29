#!/usr/bin/env python3
"""Record ONE short trial block for the noise series, the same way every time.

Replaces the scratch `rec5.py` that made every 09-30/10-01 noise-series recording (2026-10-02).
Plan and protocol: vault 05-experiments/active/2026-10-02-noise-troubleshooting-plan.md.

usage (the console's interpreter, it has radiens-core):
  /opt/neurosurveillance/venv/bin/python3 qc/record_block.py DEST_DIR NAME MINUTES [--note "text"]
    DEST_DIR  e.g. ~/radix/noise-tests/2026-10-03   (NEVER ~/radix/data: the console, NAS and S3 jobs own it)
    NAME      e.g. T1-A1_direct-usb   (letters, digits, - and _; Allego appends _0__uidMMDD-HH-MM-SS)

It REFUSES, before touching Allego, when
  * the recording console has a run that is not finished (STARTING ... UPLOADING), or a SCHEDULED run that starts
    before this block would end + 15 min: a start or stop with no port acts on EVERY port of Allego 4
    (per-port recording exists since 2026-10-28, this block does not use it), so a console run must never
    have its file or its post-processing (strip, upload) overlap a trial;
  * the console cannot be asked (pass --ignore-console only when the console is deliberately stopped);
  * DEST_DIR is inside ~/radix/data.
Then `allego.preflight` (Allego up, XDAQ_CORE_REC, 1000 Hz, not already recording, free space), then the stream is
measured against the wall clock (0.9-1.1x required: on 2026-09-30 it ran 30x real time while Allego said 1000 Hz).
The recorder is stopped in a `finally`. One line per block goes to DEST_DIR/TRIAL_LOG.tsv.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

CONSOLE = "http://127.0.0.1:8600"
DATA_ROOT = Path("~/radix/data").expanduser()
BUSY = {"STARTING", "RECORDING", "STOPPING", "STOPPED", "QC", "STRIPPING", "STRIPPED",
        "EXPORTING", "EXPORTED", "UPLOAD_PENDING", "UPLOADING"}
MARGIN_MIN = 15.0
RATE_OK = (0.9, 1.1)
KST = dt.timezone(dt.timedelta(hours=9))
NAME_RE = re.compile(r"[A-Za-z0-9_-]{1,60}")


def parse_when(s: str | None) -> dt.datetime | None:
    """Console times come in three spellings: '...Z' (UTC), '...+09:00', and naive local (KST)."""
    if not s:
        return None
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=KST)


def console_conflicts(runs: list[dict], now: dt.datetime, minutes: float) -> list[str]:
    """Reasons this block must not record now (empty list = clear)."""
    out, end = [], now + dt.timedelta(minutes=minutes + MARGIN_MIN)
    for r in runs:
        st = r.get("state", "")
        if st in BUSY:
            out.append(f"console run {r.get('run_id')} is {st}")
        elif st == "SCHEDULED":
            start = parse_when(r.get("scheduled_start"))
            if start is None or start <= end:
                out.append(f"console run {r.get('run_id')} is SCHEDULED for {r.get('scheduled_start')}, "
                           f"inside this block + {MARGIN_MIN:.0f} min")
    return out


def check_dest(dest: Path) -> Path:
    d = dest.expanduser().resolve()
    if d == DATA_ROOT.resolve() or DATA_ROOT.resolve() in d.parents:
        raise SystemExit(f"refusing: {d} is inside {DATA_ROOT} (console/NAS/S3 territory); use ~/radix/noise-tests/<date>")
    return d


def stream_rate(client, window_s: float = 10.0) -> float:
    """Seconds of stream per second of wall clock."""
    a = client.get_status().streaming.primary_cache_t_range[1]; t0 = time.monotonic()
    time.sleep(window_s)
    b = client.get_status().streaming.primary_cache_t_range[1]
    return (b - a) / (time.monotonic() - t0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dest"); ap.add_argument("name"); ap.add_argument("minutes", type=float)
    ap.add_argument("--note", default="")
    ap.add_argument("--ignore-console", action="store_true", help="only when the console is deliberately stopped")
    a = ap.parse_args(argv)
    if not NAME_RE.fullmatch(a.name):
        raise SystemExit(f"refusing: NAME {a.name!r} must be letters, digits, - or _ (max 60)")
    if not 0.75 <= a.minutes <= 120:
        raise SystemExit("refusing: MINUTES must be 0.75-120 (growth is confirmed over the last 40 s)")
    dest = check_dest(Path(a.dest))

    # ---- 1. the console: nothing of its own may overlap this block (no Allego call yet)
    if not a.ignore_console:
        try:
            with urllib.request.urlopen(f"{CONSOLE}/api/runs?limit=50", timeout=10) as resp:
                runs = json.load(resp).get("runs") or []
        except Exception as exc:
            raise SystemExit(f"refusing: cannot ask the recording console ({exc}); --ignore-console only if it is stopped")
        why = console_conflicts(runs, dt.datetime.now(KST), a.minutes)
        if why:
            raise SystemExit("refusing: " + "; ".join(why))

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "eeg-recorder" / "backend"))
    import allego                                                     # noqa: E402  (needs radiens-core)

    # ---- 2. Allego state, read-only
    pf = allego.preflight(dest, min_free_gb=50)
    print(f"preflight ok: {pf['status']['system_mode']} {pf['status']['sample_freq']:.0f} Hz, {pf['free_gb']} GB free", flush=True)

    # ---- 3. stream against the wall clock
    c = allego._client()
    c.start_streaming(); time.sleep(5)
    rate = stream_rate(c)
    print(f"stream rate {rate:.3f}x real time", flush=True)
    if not RATE_OK[0] <= rate <= RATE_OK[1]:
        raise SystemExit(f"refusing: stream runs {rate:.2f}x real time (Allego's 1000 Hz label can lie); restart Allego")

    # ---- 4. record, always stop
    t_start = dt.datetime.now(KST); r = None; grow = {}; err = ""
    try:
        r = allego.start(dest, base_name=a.name, settle_s=10.0, min_free_gb=50)
        print(json.dumps(r), flush=True)
        time.sleep(max(0.0, a.minutes * 60 - 40 - 13))                # start() already used ~13 s
        grow = allego.confirm_growing(r["data_path"], window_s=40)
    except BaseException as exc:                                      # KeyboardInterrupt too: still stop
        err = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        # Stop ONLY a recording this block started. If start() raised, it already stopped anything it engaged;
        # calling stop() here could end a console run that started in between (stop with no port ends every port).
        if r is not None:
            try:
                print(allego.stop(list(r["port_files"]), stop_streaming=False), flush=True)
            except Exception as exc:
                err = (err + "; " if err else "") + f"STOP FAILED: {exc}"
                print(f"WARNING: stop failed, check Allego NOW: {exc}", flush=True)
        log = dest / "TRIAL_LOG.tsv"; new = not log.exists()
        with open(log, "a") as fh:
            if new:
                fh.write("start\tstop\tname\tbase_name\tgrowing\tgb_per_h\tstream_rate\tnote\terror\n")
            fh.write("\t".join([f"{t_start:%F %T}", f"{dt.datetime.now(KST):%F %T}", a.name,
                                (r or {}).get("base_name", "-"), str(grow.get("growing", "-")),
                                str(grow.get("gb_per_h", "-")), f"{rate:.3f}", a.note.replace("\t", " "),
                                err.replace("\t", " ")]) + "\n")
    print(f"done: {r['base_path'] if r else '-'}  growing={grow.get('growing')}  logged in {dest / 'TRIAL_LOG.tsv'}")
    return 0 if grow.get("growing") else 1


if __name__ == "__main__":
    sys.exit(main())

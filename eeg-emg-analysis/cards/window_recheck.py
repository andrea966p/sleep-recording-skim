#!/usr/bin/env python3
"""window_recheck.py -- run the verdict ladder on an analysis WINDOW of a recording.

WHY. The animal cards in cards/out/ judge whole files. The per-mouse CSVs on the
NAS (2026-09-29) are cut to fixed windows -- baseline 09:00 -> 09:00, SD recovery
13:00 -> 09:00, SL recovery 09:00 -> 09:00 -- so "is this mouse scoreable" has
to be answered on exactly those hours, not on a 36 h file that includes an extra
night.

HOW, WITHOUT TOUCHING THE RAW FILE OR THE LADDER.
  rung 2  The recording's cached 10 s QC features (~/eeg-qc-cache/<base>.npz,
          computed on the FULL 262-channel original, wire-free floor included)
          are sliced to the epochs lying wholly inside the window and handed to
          cards/ladder.py as its --cache. The per-chip floor is then the floor
          OF THE WINDOW, which is the honest comparison.
  rung 3+ The stage 2 per-mouse files (~/eeg-processed/<day>/port*.npz, 250 Hz,
          4 s epochs) are sliced the same way into a SEPARATE root and stage 3
          is run there. The ladder is pointed at that root through
          EEG_PROCESSED_ROOT, so the whole-file results are never overwritten.
  cards   Written to cards/out-windows/<cohort>/, each carrying a `window` block.

A position with no stage 2 file (stage 1 did not keep it) reads INSUFFICIENT at
rung 3 if it passes rung 2 in the window -- that is reported, not papered over.

    python3 cards/window_recheck.py <base> --cohort S-SL \\
        --start "2026-09-21 09:00" --end "2026-09-22 09:00"
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import paths as PATHS                  # noqa: E402
from core import qc_thresholds as T              # noqa: E402
from pipeline import pipeline_common as P        # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
WIN_PROCESSED = Path(os.environ.get("EEG_WINDOW_PROCESSED_ROOT",
                                    Path.home() / "eeg-processed-windows"))
WIN_CACHE = PATHS.CACHE_ROOT / "windows"
WIN_CARDS = ROOT / "cards" / "out-windows"


def _kst(s: str) -> dt.datetime:
    t = dt.datetime.fromisoformat(str(s).strip().replace(" ", "T"))
    return t.replace(tzinfo=KST) if t.tzinfo is None else t


def epoch_range(t0: dt.datetime, epoch_s: float, n: int, ws: dt.datetime,
                we: dt.datetime) -> tuple[int, int]:
    """Epochs [a, b) lying WHOLLY inside [ws, we)."""
    a = max(0, math.ceil((ws - t0).total_seconds() / epoch_s - 1e-9))
    b = min(n, math.floor((we - t0).total_seconds() / epoch_s + 1e-9))
    if b <= a:
        raise SystemExit(f"window {ws} -> {we} does not overlap this recording")
    return a, b


def slice_cache(base: str, t0: dt.datetime, ws, we, tag: str) -> tuple[Path, dict]:
    src = PATHS.CACHE_ROOT / f"{base}.npz"
    z = np.load(src, allow_pickle=True)
    es, n, fs = int(z["epoch_s"]), int(z["n_epochs"]), int(z["fs"])
    a, b = epoch_range(t0, es, n, ws, we)
    out = WIN_CACHE / f"{base}__{tag}.npz"
    out.parent.mkdir(parents=True, exist_ok=True)
    arrays = {k: z[k][a:b] for k in ("hum", "rms", "rail", "slope", "delta", "lfhf")}
    np.savez_compressed(out, fs=fs, epoch_s=es, n_epochs=b - a,
                        n_samples=(b - a) * es * fs, sites=z["sites"], **arrays)
    return out, {"cache_source": str(src), "qc_epochs": [a, b], "qc_epoch_s": es,
                 "hours": round((b - a) * es / 3600, 4)}


def slice_stage2(base: str, ws, we) -> list[Path]:
    """Slice every stage 2 file of this recording into WIN_PROCESSED/<window day>/."""
    written = []
    import re
    for npz in sorted(glob.glob(str(PATHS.PROCESSED_ROOT / "20*" / "port*.npz"))):
        # ONLY the plain day folders. `2026-09-10-lightphase`, `-darkmatch` and
        # the like hold derived subsets of the same recording (a 12 h light-only
        # copy has the same meta.recording) and slicing them would judge a
        # subset twice. Found on the first run, 2026-09-30.
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", Path(npz).parent.name):
            continue
        z = np.load(npz, allow_pickle=True)
        meta = json.loads(str(z["meta"]))
        if meta.get("recording") != base:
            continue
        es, fs = int(meta.get("epoch_s", T.EPOCH_S)), int(z["fs"])
        t0 = dt.datetime.fromisoformat(meta["start_local"])
        ok = z["epoch_ok"]
        a, b = epoch_range(t0, es, len(ok), ws, we)
        s0, s1 = a * es * fs, b * es * fs
        ok_w = ok[a:b]
        blks = np.array([bl for bl in P.blocks_of(ok_w) if bl[1] - bl[0] >= T.MIN_BLOCK],
                        dtype=np.int64).reshape(-1, 2)
        start_w = t0 + dt.timedelta(seconds=a * es)
        hours = (b - a) * es / 3600
        m = dict(meta, start_local=start_w.isoformat(),
                 start_utc=start_w.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                 hours=hours,
                 window={"start_kst": ws.isoformat(), "end_kst": we.isoformat(),
                         "source_file": os.path.basename(npz), "epochs": [a, b]})
        day = WIN_PROCESSED / f"{start_w:%Y-%m-%d}"
        day.mkdir(parents=True, exist_ok=True)
        fn = P.mouse_filename(meta["port"], meta["slot"], start_w, hours, ".npz")
        out = day / fn
        np.savez_compressed(out, eeg=z["eeg"][s0:s1], emg=z["emg"][s0:s1], fs=np.int32(fs),
                            epoch_ok=ok_w, blocks=blks, zt=z["zt"][a:b],
                            is_light=z["is_light"][a:b] if "is_light" in z.files
                            else P.is_light(z["zt"][a:b]),
                            meta=json.dumps(m, default=P.jsafe))
        written.append(out)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("base", help="Allego base name, e.g. allego_0__uid0921-00-17-34")
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--start", required=True, help="window start, KST, e.g. '2026-09-21 09:00'")
    ap.add_argument("--end", required=True, help="window end, KST")
    # /usr/bin/python3, not the recorder venv: stage 3 needs scipy, and the venv
    # pairs NumPy 2 with the system scipy built for NumPy 1 (ImportError).
    ap.add_argument("--python", default="/usr/bin/python3")
    a = ap.parse_args(argv)

    base = Path(a.base).name
    raw = PATHS.RAW_ROOT / base
    st = json.loads(Path(str(raw) + ".xdat.json").read_text())["status"]
    t0 = dt.datetime.fromisoformat(st["start_time"].replace("Z", "+00:00")).astimezone(KST)
    ws, we = _kst(a.start), _kst(a.end)
    tag = f"{ws:%Y%m%dT%H%M}-{we:%Y%m%dT%H%M}"

    cache, cinfo = slice_cache(base, t0, ws, we, tag)
    print(f"rung 2 cache: {cinfo['hours']} h of 10 s epochs {cinfo['qc_epochs']} -> {cache}")
    s2 = slice_stage2(base, ws, we)
    print(f"stage 2: {len(s2)} per-mouse file(s) sliced -> {WIN_PROCESSED}")
    env = dict(os.environ, PYTHONPATH=str(ROOT), EEG_PROCESSED_ROOT=str(WIN_PROCESSED))
    if s2:
        subprocess.run([a.python, "pipeline/stage3_features.py", *map(str, s2)],
                       cwd=ROOT, env=env, check=True, stdout=subprocess.DEVNULL)
    outdir = WIN_CARDS / a.cohort
    subprocess.run([a.python, "cards/ladder.py", str(raw), "--cohort", a.cohort,
                    "--cache", str(cache), "--out", str(outdir)],
                   cwd=ROOT, env=env, check=True)

    # Stamp the window on every card the ladder just wrote for this recording.
    win = {"start_kst": ws.isoformat(), "end_kst": we.isoformat(), **cinfo,
           "note": "rung 2 judged on the window's own epochs and floor; rung 3+ on "
                   "stage 2 files sliced to the window. File-level rung 0 is the "
                   "whole file."}
    for f in outdir.glob(f"{base}__*_card.json"):
        c = json.loads(f.read_text())
        c["window"] = win
        c["duration_h"] = cinfo["hours"]
        f.write_text(json.dumps(c, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

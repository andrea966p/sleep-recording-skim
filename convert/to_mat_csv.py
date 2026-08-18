#!/usr/bin/env python3
"""to_mat_csv.py -- export STAGE 2 per-animal signals to MATLAB .mat and/or CSV.

REWRITTEN 2026-08-10. The previous version read the raw XDAT and derived its own
"bipolar" signals by subtracting native rows, on the model that each mouse owns
four consecutive rows (EEG+, EEG-, EMG+, EMG-). THAT MODEL IS WRONG ON THIS RIG
and the export it produced was not EEG and not EMG:

    old "EEG" = row(+0) - row(+1) = the EEG site minus the EMG site
    old "EMG" = row(+2) - row(+3) = one empty pad minus another empty pad

The RHD2216 is a bipolar chip. `/1` is EEG and `/2` is EMG, each ALREADY a
difference computed in hardware before the ADC; `/3` and `/4` are empty pads with
no wire attached. Nothing may be subtracted offline. See
core/qc_thresholds.py "CHANNEL MAP" and pipeline/stage2_split.py, which writes
its metadata with `bipolar=True, subtract_anything=False` for exactly this
reason.

So this module no longer touches raw files or derives anything. It reads the
stage 2 per-animal .npz, which is the same array every card, verdict and figure
in this project is computed from, and simply re-containers it. If a number
disagrees between MATLAB and a card, it is now a bug rather than a second
opinion.

    eeg, emg   float32, microvolts, ALREADY BIPOLAR, at meta.fs_out (250 Hz)
    epoch_ok   per-epoch QC mask (EPOCH_S seconds per entry)
    blocks     [start_epoch, end_epoch) of unbroken usable contact
    zt         Zeitgeber hours per epoch; is_light its light-phase flag

Outputs
    .mat   struct `animals`, one entry per npz, plus top-level `meta`.
           MATLAB:  S = load('day.mat');  S.animals(1).eeg
    --csv  one file per animal: time_s, EEG_uV, EMG_uV [, epoch_ok, zt_h]

Usage
    python to_mat_csv.py <stage2_day_dir_or_npz> [--mat] [--csv] [--out FILE]
    (default: --mat)
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.io import savemat

ROOT = Path(__file__).resolve().parent.parent

from core import qc_thresholds as T      # noqa: E402

# Excel's hard row cap. A 24 h recording at 250 Hz is 21.6 M rows, so CSV is for
# tooling, never for a spreadsheet, and we say so rather than truncating.
EXCEL_ROW_CAP = 1_048_576


def npz_paths(target: str) -> list[str]:
    """Accept either one .npz or a stage 2 day directory."""
    if target.endswith(".npz"):
        return [target]
    found = sorted(glob.glob(os.path.join(target, "port*-slot*.npz")))
    if not found:
        raise SystemExit(f"no stage 2 per-animal .npz under {target}")
    return found


def payload(path: str) -> dict:
    z = np.load(path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    if not meta.get("bipolar", False) or meta.get("subtract_anything", True):
        # stage 2 stamps these; a file without them predates the channel-law fix
        raise SystemExit(
            f"{os.path.basename(path)} was not written by the current stage 2 "
            "(missing bipolar/subtract_anything stamp). Re-run stage 2 rather "
            "than exporting it -- the older file may hold derived signals.")
    return dict(
        name=meta.get("name", ""),
        port=meta.get("port", ""),
        slot=int(meta.get("slot", 0)),
        recording=meta.get("recording", ""),
        start_local=meta.get("start_local", ""),
        fs=float(meta["fs_out"]),
        epoch_s=float(meta.get("epoch_s", T.EPOCH_S)),
        units="microvolt",
        # THE POINT OF THIS FILE: these two are copied, never combined.
        eeg=np.asarray(z["eeg"], dtype=np.float32),
        emg=np.asarray(z["emg"], dtype=np.float32),
        epoch_ok=np.asarray(z["epoch_ok"]).astype(np.uint8),
        blocks=np.asarray(z["blocks"], dtype=np.int64),
        zt_h=np.asarray(z["zt"], dtype=np.float32),
        is_light=np.asarray(z["is_light"]).astype(np.uint8),
        eeg_native_col=int(meta.get("eeg_native_col", -1)),
        emg_native_col=int(meta.get("emg_native_col", -1)),
        provenance=("already-bipolar RHD2216 sites, copied from stage 2; "
                    "nothing subtracted, re-referenced or derived"),
    )


def write_csv(p: dict, out: str, with_qc: bool) -> int:
    n = min(len(p["eeg"]), len(p["emg"]))
    t = np.arange(n) / p["fs"]
    cols = {"time_s": t, "EEG_uV": p["eeg"][:n], "EMG_uV": p["emg"][:n]}
    if with_qc:
        # per-epoch values, expanded onto the sample grid so every row carries
        # the QC state that applies to it. No interpolation: it is a step.
        per_ep = int(round(p["epoch_s"] * p["fs"]))
        idx = np.minimum(np.arange(n) // per_ep, len(p["epoch_ok"]) - 1)
        cols["epoch_ok"] = p["epoch_ok"][idx]
        cols["zt_h"] = p["zt_h"][idx]
    arr = np.column_stack([np.asarray(v, dtype=np.float64) for v in cols.values()])
    np.savetxt(out, arr, delimiter=",", header=",".join(cols), comments="",
               fmt="%.4f")
    return n


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Stage 2 per-animal signals -> .mat / .csv. Copies the "
                    "already-bipolar channels; derives nothing.")
    ap.add_argument("target", help="stage 2 day directory, or one port*-slot*.npz")
    ap.add_argument("--mat", action="store_true", help="write .mat (default)")
    ap.add_argument("--csv", action="store_true", help="one CSV per animal")
    ap.add_argument("--with-qc", action="store_true",
                    help="add epoch_ok and zt_h columns to the CSV")
    ap.add_argument("--out", default=None, help="explicit .mat path")
    a = ap.parse_args()
    if not (a.mat or a.csv):
        a.mat = True

    paths = npz_paths(a.target)
    payloads = [payload(p) for p in paths]
    stem = (a.target[:-4] if a.target.endswith(".npz")
            else os.path.join(a.target.rstrip("/"),
                              os.path.basename(a.target.rstrip("/"))))

    if a.mat:
        out = a.out or (stem + ".mat")
        savemat(out, dict(
            animals=payloads,
            meta=dict(
                source=os.path.basename(a.target.rstrip("/")),
                n_animals=len(payloads),
                units="microvolt",
                channel_law=("RHD2216 is bipolar: /1 EEG and /2 EMG are each "
                             "already a hardware difference; /3 and /4 are "
                             "empty pads. Never subtract these from each other."),
                thresholds_file="core/qc_thresholds.py",
            )), do_compression=True)
        print(f"wrote {out}  ({len(payloads)} animals, "
              f"{os.path.getsize(out) / 1e9:.3f} GB)")

    if a.csv:
        biggest = 0
        for p, src in zip(payloads, paths):
            out = src[:-4] + ".csv"
            n = write_csv(p, out, a.with_qc)
            biggest = max(biggest, n)
            print(f"wrote {out}  rows={n} @ {p['fs']:g} Hz")
        if biggest > EXCEL_ROW_CAP:
            print(f"NOTE  {biggest:,} rows exceeds Excel's {EXCEL_ROW_CAP:,} "
                  "row cap. Open in pandas or MATLAB, not Excel.")


if __name__ == "__main__":
    main()

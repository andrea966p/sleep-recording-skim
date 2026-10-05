#!/usr/bin/env python3
"""DIAGNOSTIC-ONLY ladder run with ONE threshold changed in memory. Never a verdict of record.

Written 2026-10-02 for B1 of run cfdf8ebde0c6: the chip-floor ground gate (FLOOR_MIN_HUM_UV, 800 uV)
is expected to call B1 UNJUDGEABLE although its EEG and EMG look physiological, and the floor turned
out to be set by a few collapsed input pairs on its adapter board (vault noise-series page). This shows
what the ladder WOULD say with that one gate moved, so the decision about the gate is informed by the
consequence, without the consequence ever being published as a result.

Safety:
  * the threshold is changed only in this process (core.qc_thresholds is a module; nothing is edited);
  * the feature cache is COPIED first and the copy is used, so the official cache is never rewritten;
  * cards go to OUTDIR, which must contain the word "shadow", never to cards/out/<cohort>.
Run it only after the console's post-processing has finished (no competing heavy job, no live run).

usage (same interpreter as the console's QC step):
  cd eeg-emg-analysis && PYTHONPATH=$PWD /opt/neurosurveillance/venv/bin/python3 qc/shadow_ladder.py \
      BASE ~/.local/state/eeg-recorder/cohorts/auto-<run_id>.yaml ~/eeg-qc-cache/<base>.npz \
      ~/radix/noise-tests/2026-10-02/shadow-B1 --positions B1 [--floor-min 0]
"""
import argparse, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

ap = argparse.ArgumentParser()
ap.add_argument("base"); ap.add_argument("manifest"); ap.add_argument("cache"); ap.add_argument("outdir")
ap.add_argument("--positions", required=True)
ap.add_argument("--floor-min", type=float, default=0.0, help="FLOOR_MIN_HUM_UV for this run only")
a = ap.parse_args()
if "shadow" not in os.path.basename(os.path.normpath(a.outdir)).lower():
    sys.exit("OUTDIR must be named *shadow*: these cards must never be mistaken for the official ones")
os.makedirs(a.outdir, exist_ok=True)
cache_copy = os.path.join(a.outdir, "features_COPY_" + os.path.basename(a.cache))
shutil.copy2(a.cache, cache_copy)

from core import qc_thresholds as T
official = T.FLOOR_MIN_HUM_UV
T.FLOOR_MIN_HUM_UV = a.floor_min
with open(os.path.join(a.outdir, "README_SHADOW.txt"), "w") as fh:
    fh.write(f"DIAGNOSTIC ONLY. FLOOR_MIN_HUM_UV changed in memory {official} -> {a.floor_min} uV for this run.\n"
             f"Recording {a.base}\nCohort manifest {a.manifest}\nFeature cache COPY {cache_copy}\n"
             "These cards are not verdicts of record and must not be uploaded, cited or merged.\n")
print(f"SHADOW RUN: FLOOR_MIN_HUM_UV {official} -> {a.floor_min} (in memory only); cards -> {a.outdir}")
from cards import ladder as L
raise SystemExit(L.main([a.base, "--cohort", a.manifest, "--cache", cache_copy,
                         "--positions", a.positions, "--out", a.outdir]))

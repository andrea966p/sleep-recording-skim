"""Duty-cycle statistics for an impedance sweep block, scored against the free in-file floor.

The floor control is the set of REAL amplifier inputs that carry NO WIRE, recorded in the same
sweep. A mouse uses only the first few of its chip's 16 active sites, so the rest are unwired.

  2-channel cohort (EEG /1 /2, /33 /34):        floor = /3-/16  and /35-/48
  3-channel ECG cohort (EEG/EMG/ECG /1 /2 /3):  floor = /4-/16  and /36-/48

NEVER include /17-/32 or /49-/64. Those are inactive slots, internally tied, ~96% of them read
below 0.5 MOhm and they would destroy the control.

A channel is "connected" in a sweep if |Z| < THRESH. Report the duty cycle over the whole block
and a one-sided binomial test against the pooled floor rate. A single sweep proves nothing:
contact flips within minutes.

Usage:
  python block_duty_cycle.py BLOCKDIR [--roles eeg,emg,ecg] [--thresh 0.5]
"""
import argparse, csv, glob, os, re
import numpy as np
from scipy.stats import binomtest

ap = argparse.ArgumentParser()
ap.add_argument("blockdir")
ap.add_argument("--roles", default="eeg,emg,ecg")
ap.add_argument("--thresh", type=float, default=0.5, help="MOhm; 0.5, NOT 2.0 (22%% FPR)")
args = ap.parse_args()

ROLES = [r.strip().lower() for r in args.roles.split(",")]
N = len(ROLES)
FLOOR_LO = N + 1  # first unwired site in the low bank

files = sorted(glob.glob(os.path.join(args.blockdir, "imp_*.csv")))
if not files:
    raise SystemExit(f"no imp_*.csv in {args.blockdir}")

Z = {}  # site -> list of |Z| across sweeps
for path in files:
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            Z.setdefault(row["SITE"], []).append(float(row["MAGNITUDE (MΩ)"]))

nsweep = len(files)
print(f"block {os.path.basename(args.blockdir)}: {nsweep} sweeps, {len(Z)} sites, "
      f"threshold {args.thresh} MOhm, roles {'/'.join(ROLES)}")

# ---- floor control -------------------------------------------------------
floor = []
for site, vals in Z.items():
    n = int(site.split("/")[1])
    if FLOOR_LO <= n <= 16 or (32 + FLOOR_LO) <= n <= 48:
        floor += vals
floor = np.asarray(floor)
p_floor = float((floor < args.thresh).mean())
print(f"FLOOR: n={floor.size} sweep-channels, {100*p_floor:.1f}% below {args.thresh} MOhm, "
      f"min {floor.min():.3f}, median {np.median(floor):.3f}")
if p_floor > 0.10:
    print("WARNING: floor rate above 10% - the threshold is too loose, results are not "
          "interpretable")

# ---- per animal ----------------------------------------------------------
print(f"\n{'mouse':<7}{'role':<5}{'site':<7}{'duty%':>7}{'med_Z':>9}{'min_Z':>9}"
      f"{'flips':>7}{'p_vs_floor':>12}")
for port in "ABCD":
    for slot, base in ((1, 1), (2, 33)):
        for k, role in enumerate(ROLES):
            site = f"{port}/{base + k}"
            v = np.asarray(Z[site])
            conn = v < args.thresh
            duty = float(conn.mean())
            flips = int((np.diff(conn.astype(int)) != 0).sum())
            p = binomtest(int(conn.sum()), nsweep, p_floor, alternative="greater").pvalue
            star = " *" if p < 0.05 else ""
            print(f"{port}{slot:<6}{role.upper():<5}{site:<7}{100*duty:7.1f}"
                  f"{np.median(v):9.3f}{v.min():9.3f}{flips:7d}{p:12.2g}{star}")
    print()
print("* = beats an unwired amplifier input at p < 0.05. No star means the channel is "
      "indistinguishable from a wire that is not attached to anything.")
print("REMINDER: impedance SCREENS. Only a multi-hour recording is an OUTCOME.")

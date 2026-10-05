"""Duty-cycle statistics for an impedance sweep block, scored against the free in-file floor.

Slot-aware, port-agnostic version of qc/block_duty_cycle.py (2026-10-01; hardened 2026-10-02).

The floor control is the set of REAL amplifier inputs that carry NO WIRE, recorded in the same
sweep. A mouse uses only the first few of its chip's 16 active sites, so the rest are unwired.

  2-channel cohort (EEG /1 /2, /33 /34):        floor = /3-/16  and /35-/48
  3-channel ECG cohort (EEG/EMG/ECG /1 /2 /3):  floor = /4-/16  and /36-/48

NEVER include /17-/32 or /49-/64. Those are inactive slots, internally tied, ~96% of them read
below 0.5 MOhm and they would destroy the control.

A channel is "connected" in a sweep if |Z| < THRESH. Report the duty cycle over the whole block
and a one-sided binomial test against the floor rate OF THE ANIMAL'S OWN CHIP (port + slot),
which is the project's rule for every floor (core/qc_thresholds.py FLOOR_SCOPE = "chip"). The
pooled-floor p is printed beside it for comparison with older reports. A single sweep proves
nothing: contact flips within minutes.

What changed on 2026-10-02 (code review of the 10-01 copy):
  * n comes from the block's _census_log.tsv, never from a folder glob. Only CSVs that match a
    log row (census number AND hhmmss) are scored, and a stray file is reported and ignored.
    A loose single sweep in a block folder once cost a number (register, 2026-08-05 arm C).
  * Non-finite magnitudes (a partial RPC reply) are dropped and counted per site, instead of
    silently counting as "open".
  * --slots entries are validated (A-H then 1 or 2), so "A3" or "B12" cannot alias another slot.

Usage:
  python qc/block_duty_cycle_slots.py BLOCKDIR [--roles eeg,emg] [--slots A1,A2,B1,B2] [--thresh 0.5]
"""
import argparse, csv, glob, os, re, sys
import numpy as np
from scipy.stats import binomtest

ap = argparse.ArgumentParser()
ap.add_argument("blockdir")
ap.add_argument("--roles", default="eeg,emg,ecg")
ap.add_argument("--slots", default="A1,A2,B1,B2,C1,C2,D1,D2", help="occupied slots")
ap.add_argument("--thresh", type=float, default=0.5, help="MOhm; 0.5, NOT 2.0 (22%% FPR)")
args = ap.parse_args()

ROLES = [r.strip().lower() for r in args.roles.split(",")]
N = len(ROLES)
FLOOR_LO = N + 1  # first unwired site in the low bank
SLOTS = []
for lab in args.slots.split(","):
    m = re.fullmatch(r"([A-H])([12])", lab.strip().upper())
    if not m:
        sys.exit(f"bad slot {lab!r}: expected a port letter A-H and slot 1 or 2, e.g. A1,B2")
    SLOTS.append((m.group(1), int(m.group(2))))

# ---- n comes from the log ------------------------------------------------------------------
logp = os.path.join(args.blockdir, "_census_log.tsv")
if not os.path.exists(logp):
    sys.exit(f"no _census_log.tsv in {args.blockdir}: n cannot be established, refusing to guess "
             "from a folder glob")
with open(logp, encoding="utf-8") as fh:
    log_rows = [r for r in csv.DictReader(fh, delimiter="\t")]
keys = [(int(r["sweep"]), r["clock"].replace(":", "")) for r in log_rows]
if len({k[0] for k in keys}) != len(keys):
    sys.exit("the log has repeated sweep numbers: it spans more than one run. Split the folder.")
wanted = {k: None for k in keys}
pat = re.compile(r"^imp_\d{4}-\d{2}-\d{2}_(\d{6})_.+_census-(\d+)\.csv$")
stray = []
for path in sorted(glob.glob(os.path.join(args.blockdir, "imp_*.csv"))):
    m = pat.match(os.path.basename(path))
    k = (int(m.group(2)), m.group(1)) if m else None
    if k in wanted and wanted[k] is None:
        wanted[k] = path
    else:
        stray.append(os.path.basename(path))
missing = [k for k, p in wanted.items() if p is None]
if missing:
    sys.exit(f"{len(missing)} logged sweep(s) have no CSV (first: census {missing[0][0]} at {missing[0][1]}); "
             "the block is incomplete")
files = [wanted[k] for k in keys]
nsweep = len(files)

Z = {}  # site -> list of |Z| across sweeps (NaN kept here, dropped per site below)
for path in files:
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            Z.setdefault(row["SITE"], []).append(float(row["MAGNITUDE (MΩ)"]))
bad_len = [s for s, v in Z.items() if len(v) != nsweep]
if bad_len:
    sys.exit(f"{len(bad_len)} site(s) do not appear once per sweep (e.g. {bad_len[0]}): refusing")
Z = {s: np.asarray(v, dtype=float) for s, v in Z.items()}
nonfinite = {s: int((~np.isfinite(v)).sum()) for s, v in Z.items() if (~np.isfinite(v)).any()}

print(f"block {os.path.basename(os.path.normpath(args.blockdir))}: n = {nsweep} sweeps (from _census_log.tsv), "
      f"{len(Z)} sites, threshold {args.thresh} MOhm, roles {'/'.join(ROLES)}")
if stray:
    print(f"⚠️  {len(stray)} CSV(s) in the folder match no log row and were IGNORED: {', '.join(stray[:3])}"
          + (" ..." if len(stray) > 3 else ""))
if nonfinite:
    print(f"⚠️  non-finite magnitudes dropped on {len(nonfinite)} site(s), "
          f"{sum(nonfinite.values())} values (partial RPC replies)")


def floor_sites(port, slot):
    base = 0 if slot == 1 else 32
    return [f"{port}/{base + n}" for n in range(FLOOR_LO, 17)]


def rate(values):
    v = values[np.isfinite(values)]
    return (float((v < args.thresh).mean()) if v.size else float("nan")), v


# ---- floor control: per chip (the rule) and pooled (for comparison) -------------------------
pooled = np.concatenate([Z[s] for p, sl in SLOTS for s in floor_sites(p, sl) if s in Z]) if SLOTS else np.array([])
p_pool, pool_f = rate(pooled)
print(f"FLOOR pooled over the {len(SLOTS)} occupied chips: n={pool_f.size} sweep-channels, "
      f"{100*p_pool:.1f}% below {args.thresh} MOhm, min {pool_f.min():.3f}, median {np.median(pool_f):.3f}")
chip_rate = {}
for port, slot in SLOTS:
    fs_ = [s for s in floor_sites(port, slot) if s in Z]
    pr, fv = rate(np.concatenate([Z[s] for s in fs_])) if fs_ else (float("nan"), np.array([]))
    chip_rate[(port, slot)] = pr
    flag = "  ⚠️ above 10%: threshold too loose for this chip" if pr > 0.10 else ""
    print(f"  chip {port}{slot}: floor n={fv.size} ({len(fs_)} sites), {100*pr:.1f}% below{flag}")

print(f"\n{'mouse':<7}{'role':<5}{'site':<7}{'n':>4}{'duty%':>7}{'med_Z':>9}{'min_Z':>9}"
      f"{'flips':>7}{'p_chip':>10}{'p_pooled':>10}")
for port, slot in SLOTS:
    base = 1 if slot == 1 else 33
    for k, role in enumerate(ROLES):
        site = f"{port}/{base + k}"
        if site not in Z:
            print(f"{port}{slot:<6}{role.upper():<5}{site:<7}  site not in the sweep files"); continue
        v = Z[site][np.isfinite(Z[site])]
        conn = v < args.thresh
        flips = int((np.diff(conn.astype(int)) != 0).sum())
        pc = binomtest(int(conn.sum()), v.size, chip_rate[(port, slot)], alternative="greater").pvalue
        pp = binomtest(int(conn.sum()), v.size, p_pool, alternative="greater").pvalue
        star = " *" if pc < 0.05 else ""
        print(f"{port}{slot:<6}{role.upper():<5}{site:<7}{v.size:4d}{100*conn.mean():7.1f}"
              f"{np.median(v):9.3f}{v.min():9.3f}{flips:7d}{pc:10.2g}{pp:10.2g}{star}")
    print()
print("* = beats its OWN chip's unwired inputs at p < 0.05 (p_chip). No star means the channel is "
      "indistinguishable from a wire that is not attached to anything on that chip.")
print("REMINDER: impedance SCREENS. Only a multi-hour recording is an OUTCOME.")

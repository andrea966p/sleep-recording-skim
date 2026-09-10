#!/usr/bin/env python3
"""Is the QC gate throwing away epochs in a way that correlates with sleep state?

The council's most serious finding (2026-08-07): the gate rejects epochs on
electrode CONTACT, contact is MOVEMENT-driven, and movement IS state. If true,
surviving epochs are enriched for quiet states and every architecture number
inherits a bias correlated with the dependent variable.

The obvious test -- rejection rate as a function of scored state -- is impossible
as stated, because a rejected epoch HAS no state. So we test the mechanism
instead, two ways that need no human scoring:

  1. **How much is even at stake.** If almost nothing was rejected, the bias
     cannot be large whatever its direction.
  2. **Is rejection movement-linked?** EMG is a separate channel and often
     survives when the EEG gate fails. If rejected epochs carry systematically
     HIGHER EMG than accepted ones, rejection is preferentially removing
     movement, which is the bias the council predicted. If EMG is the same or
     lower, the mechanism is not operating.

Reports Cliff's delta as the effect size, because the EMG distributions are
skewed and non-normal.

Usage
    python3 selection_bias_test.py <npz> [<npz> ...]
"""
import json
import sys

import numpy as np


def cliffs_delta(a, b, cap=4000, seed=0):
    """P(a>b) - P(a<b). Subsampled for tractability on large arrays."""
    rng = np.random.default_rng(seed)
    if len(a) > cap:
        a = rng.choice(a, cap, replace=False)
    if len(b) > cap:
        b = rng.choice(b, cap, replace=False)
    gt = (a[:, None] > b[None, :]).sum()
    lt = (a[:, None] < b[None, :]).sum()
    return float(gt - lt) / (len(a) * len(b))


def band(d):
    a = abs(d)
    return ("negligible" if a < 0.147 else "small" if a < 0.33
            else "medium" if a < 0.474 else "large")


def run(npz_path):
    z = np.load(npz_path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    fs = int(z["fs"])
    emg = z["emg"]
    ok = np.asarray(z["epoch_ok"], dtype=bool)
    name = f"{meta.get('port','?')}{meta.get('slot','?')}"

    spe = fs * 4
    n = min(len(ok), len(emg) // spe)
    ok = ok[:n]
    rms = emg[:n * spe].reshape(n, spe).std(axis=1)

    n_rej = int((~ok).sum())
    pct_rej = 100.0 * n_rej / max(n, 1)
    print(f"\n{name}  ({npz_path.split('/')[-1]})")
    print(f"  epochs {n}   rejected {n_rej} = {pct_rej:.1f}%")

    if n_rej == 0:
        print("  ✅ nothing was rejected, so the gate CANNOT have biased this recording")
        return dict(animal=name, pct_rejected=0.0, delta=None, verdict="no rejection")
    if ok.sum() == 0:
        print("  ⚠️ everything was rejected, nothing to compare")
        return dict(animal=name, pct_rejected=100.0, delta=None, verdict="all rejected")

    acc, rej = rms[ok], rms[~ok]
    d = cliffs_delta(rej, acc)
    print(f"  EMG rms  accepted median {np.median(acc):8.1f} µV   "
          f"rejected median {np.median(rej):8.1f} µV")
    print(f"  Cliff's delta (rejected vs accepted) = {d:+.3f}  ({band(d)})")
    if d > 0.147:
        print("  🔴 rejected epochs carry HIGHER EMG => rejection is preferentially")
        print("     removing movement, i.e. WAKE. The predicted bias IS operating.")
        v = "bias present"
    elif d < -0.147:
        print("  ⚠️ rejected epochs carry LOWER EMG => rejection is preferentially")
        print("     removing quiet epochs, a bias in the opposite direction.")
        v = "reverse bias"
    else:
        print("  ✅ no meaningful EMG difference => rejection is not movement-linked")
        v = "no bias detected"
    if pct_rej < 5:
        print(f"  NOTE: only {pct_rej:.1f}% was rejected, so the maximum possible")
        print("        distortion of any percentage is small regardless of direction.")
    return dict(animal=name, pct_rejected=round(pct_rej, 2),
                delta=round(d, 3), verdict=v)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    out = [run(p) for p in sys.argv[1:]]
    print("\n" + "=" * 62)
    print(f"{'animal':8}{'% rejected':>12}{'Cliff d':>10}   verdict")
    for r in out:
        print(f"{r['animal']:8}{r['pct_rejected']:>12}"
              f"{str(r['delta']):>10}   {r['verdict']}")


if __name__ == "__main__":
    main()

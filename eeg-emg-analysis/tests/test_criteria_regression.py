#!/usr/bin/env python3
"""REGRESSION TEST: the consolidated criteria engine must reproduce the numbers
already published in the vault, exactly.

This refactor collapsed three copies of the usable-fraction loop into one. The
only acceptable proof that it did so faithfully is that it returns the same
numbers the vault already reports. ANY MOVEMENT HERE IS A BUG, NOT AN
IMPROVEMENT.

Reference values, with their sources:

  allego_1__uid0806-16-57-38, 23.66 h, 8,517 epochs of 10 s, HUM criterion
  05-experiments/completed/2026-08-07-overnight-recording-two-animals-work.md
      B1  EEG 100.0%  EMG  99.6%  both 99.6%  longest both-block 215.8 min
      D2  EEG  87.9%  EMG  98.6%  both 86.5%  longest both-block  87.3 min
      C1  EEG   0.0%  EMG  37.8%  both  0.0%
      C2  EEG   0.1%  EMG  15.2%  both  0.0%
      A1  EEG   0.0%  EMG   7.6%  both  0.0%
      B2, D1, A2 (no mouse)  0.0% everywhere
      floor controls 0.00%, A2 no-mouse 0.0%
      floor threshold: 60 Hz below 415.0 uV, from 953,904 floor-control epochs

  The audit at 03-troubleshooting/symptoms/figure-and-analysis-audit-2026-08-08.md
  recorded that every published usable fraction reproduces exactly EXCEPT C2 EEG,
  which moved 0.0 -> 0.1 percent. So the tolerance is one tenth of a point.

Run:  ~/eeg-analysis-venv/bin/python tests/test_criteria_regression.py
      ~/eeg-analysis-venv/bin/python tests/test_criteria_regression.py --quick
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

from core import criteria as C           # noqa: E402
from core import paths as PATHS          # noqa: E402
from core import qc_thresholds as T      # noqa: E402

RECORDING = "allego_1__uid0806-16-57-38"
# Resolved through core/paths.py rather than written out, so this suite runs on
# any machine that sets EEG_RAW_ROOT. It previously hardcoded one laptop's home
# directory, which meant THE CONTRACT COULD NOT BE CHECKED BY ANYONE ELSE --
# including a reviewer, and including this project's own professor.
BASE = PATHS.recording(RECORDING)
CACHE = PATHS.cache(f"regression_{RECORDING.split('__')[-1]}.npz")

# position -> (eeg %, emg %, both %, longest both-block minutes or None)
EXPECTED = {
    "B1": (100.0, 99.6, 99.6, 215.8),
    "D2": (87.9, 98.6, 86.5, 87.3),
    "C1": (0.0, 37.8, 0.0, None),
    "C2": (0.1, 15.2, 0.0, None),
    "A1": (0.0, 7.6, 0.0, None),
    "B2": (0.0, 0.0, 0.0, None),
    "D1": (0.0, 0.0, 0.0, None),
    "A2": (0.0, 0.0, 0.0, None),        # holds no mouse
}
TOL_PCT = 0.15          # one tenth of a point, plus rounding slack
TOL_MIN = 0.6           # longest block, minutes

FAILURES: list[str] = []


def check(label: str, got: float, want: float, tol: float, unit: str = "%") -> None:
    ok = abs(got - want) <= tol
    mark = "ok  " if ok else "FAIL"
    print(f"  {mark}  {label:<28} got {got:8.2f}{unit}   vault {want:8.2f}{unit}")
    if not ok:
        FAILURES.append(f"{label}: got {got}, vault {want}, tolerance {tol}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="first 2 h only; checks the machinery, not the vault numbers")
    ap.add_argument("--rebuild", action="store_true", help="ignore the feature cache")
    args = ap.parse_args()

    if not Path(BASE + "_data.xdat").exists():
        # A skip must never read like a pass. This suite is the project's claim
        # that its published numbers are reproducible, so saying nothing and
        # exiting 0 is the one failure mode that would go unnoticed.
        print("=" * 70)
        print("SKIPPED -- NOTHING WAS VERIFIED.")
        print(f"  wanted : {BASE}_data.xdat")
        print(f"  raw root currently resolves to: {PATHS.RAW_ROOT}")
        print("  set EEG_RAW_ROOT to the directory holding the recording, e.g.")
        print("      EEG_RAW_ROOT=/path/to/data python tests/test_criteria_regression.py")
        print("=" * 70)
        # 2, not 0. Exiting 0 here made a suite that verified nothing
        # indistinguishable from one that passed.
        return 2

    spec = C.CohortSpec(roles=("eeg", "emg"))

    print(f"\nrecording : {Path(BASE).name}")
    integrity = C.file_integrity(BASE)
    print(f"rung 0    : {integrity['verdict']} -- {integrity['reason']}")
    print(f"cohort    : {len(spec.roles)} roles, {len(spec.floor_sites())} floor sites")

    t0 = time.time()
    if CACHE.exists() and not args.rebuild and not args.quick:
        print(f"features  : cached {CACHE}")
        z = np.load(CACHE, allow_pickle=True)
        feat = C.EpochFeatures(
            base=BASE, fs=int(z["fs"]), epoch_s=int(z["epoch_s"]),
            n_epochs=int(z["n_epochs"]), n_samples=int(z["n_samples"]),
            sites=list(z["sites"]), spec=spec, hum=z["hum"], rms=z["rms"],
            rail=z["rail"], slope=z["slope"], delta=z["delta"], lfhf=z["lfhf"],
            # optional: absent from caches written before 2026-08-10, in which
            # case the band-limit guard reports "unknown" rather than passing
            slope_lo=z["slope_lo"] if "slope_lo" in z.files else None,
            slope_hi=z["slope_hi"] if "slope_hi" in z.files else None)
    else:
        print("features  : computing (single pass, this takes a few minutes)")
        feat = C.compute_features(BASE, spec,
                                  max_hours=2.0 if args.quick else None)
        if not args.quick:
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                CACHE, fs=feat.fs, epoch_s=feat.epoch_s, n_epochs=feat.n_epochs,
                n_samples=feat.n_samples, sites=np.array(feat.sites), hum=feat.hum,
                rms=feat.rms, rail=feat.rail, slope=feat.slope, delta=feat.delta,
                lfhf=feat.lfhf, slope_lo=feat.slope_lo, slope_hi=feat.slope_hi)
    print(f"            {feat.n_epochs} epochs of {feat.epoch_s}s = "
          f"{feat.hours:.2f} h   ({time.time() - t0:.0f}s)")

    floor = C.floor_stats(feat)
    print(f"\nfloor     : {floor.n_sites} wire-free inputs x {feat.n_epochs} epochs "
          f"= {floor.n_samples:,} measurements")
    print(f"            60 Hz  p1={floor.hum_p1:.1f}  p5={floor.hum_p5:.1f}  "
          f"median={floor.hum_median:.1f} uV")
    print(f"            slope  p1={floor.slope_p1:.2f}  median={floor.slope_median:.2f}")

    if not args.quick:
        print("\nfloor threshold (vault says 415.0 uV from 953,904 epochs)")
        check("60 Hz threshold", floor.hum_p1, 415.0, 3.0, " uV")
        check("floor measurements", floor.n_samples, 953904, 1, "")

    print("\nfalsification: wire-free inputs scored with their own criterion")
    fals = C.falsification_check(feat, floor, "hum")
    print(f"  {'ok  ' if fals['passes'] else 'FAIL'}  mean usable across "
          f"{fals['n_floor_sites']} floor sites = "
          f"{100 * fals['mean_usable_fraction']:.2f}%  (max "
          f"{100 * fals['max_usable_fraction']:.2f}%)")
    if not fals["passes"]:
        FAILURES.append("falsification check failed: the floor scores as usable")

    print("\nper-position usable fraction, HUM criterion")
    results = {}
    for pos in spec.positions():
        eeg_site = spec.site_of(pos, "eeg")
        emg_site = spec.site_of(pos, "emg")
        m_eeg = C.usable(feat, eeg_site, floor, "hum", allow_refused=True)
        m_emg = C.usable(feat, emg_site, floor, "hum", allow_refused=True)
        m_both = m_eeg & m_emg
        s = C.summarise(feat, m_both)
        results[pos] = {
            "eeg_pct": 100 * float(m_eeg.mean()),
            "emg_pct": 100 * float(m_emg.mean()),
            "both_pct": 100 * float(m_both.mean()),
            "longest_both_min": s["longest_block_minutes"],
        }

    if args.quick:
        for pos, r in results.items():
            print(f"  {pos}  EEG {r['eeg_pct']:6.1f}%  EMG {r['emg_pct']:6.1f}%  "
                  f"both {r['both_pct']:6.1f}%  longest {r['longest_both_min']:7.1f} min")
        print("\n--quick run: machinery exercised, vault numbers NOT checked "
              "(they need the full recording)")
        return 0

    for pos, (e, m, b, longest) in EXPECTED.items():
        r = results[pos]
        check(f"{pos} EEG", r["eeg_pct"], e, TOL_PCT)
        check(f"{pos} EMG", r["emg_pct"], m, TOL_PCT)
        check(f"{pos} both", r["both_pct"], b, TOL_PCT)
        if longest is not None:
            check(f"{pos} longest both block", r["longest_both_min"], longest,
                  TOL_MIN, " min")

    print("\nhum-criterion validity guard (should NOT fire on this cohort)")
    fired = []
    for pos in spec.positions():
        v = C.check_hum_validity(feat, spec.site_of(pos, "eeg"), floor)
        if v["contradiction"]:
            fired.append(pos)
    if fired:
        print(f"  FAIL  guard fired on {fired}, but this cohort's hum criterion "
              "is the one the vault validated")
        FAILURES.append(f"hum guard fired unexpectedly on {fired}")
    else:
        print("  ok    guard silent on all 8 positions, as expected")

    print("\nslope criterion refuses non-EEG roles")
    try:
        C.usable(feat, spec.site_of("B1", "emg"), floor, "slope", role="emg")
        print("  FAIL  slope on an EMG channel did not raise")
        FAILURES.append("slope criterion accepted an EMG channel")
    except C.CriterionRefused:
        print("  ok    slope on an EMG channel raised CriterionRefused")

    out = PATHS.CACHE_ROOT / "regression_result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"base": BASE, "criterion": "hum", "floor": floor.as_dict(),
         "results": results, "failures": FAILURES}, indent=2))
    print(f"\nwrote {out}")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S) -- the refactor changed a published number")
        for f in FAILURES:
            print("  " + f)
        return 1
    print("all regression checks pass: the consolidated engine reproduces the vault")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

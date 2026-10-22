#!/usr/bin/env python3
"""The ladder's verdicts must agree with the vault's own scoreability record.

This is the second regression suite. `test_criteria_regression.py` checks that
the consolidated criterion reproduces published NUMBERS; this one checks that
the ladder turns those numbers into the right VERDICTS.

It exists because two design bugs got as far as a rendered card, and both of
them would have quietly mislabelled the best animals this project has:

  BUG 1  The hum-contradiction guard was applied to EMG channels. It fires on
         "quiet and spectrally flat", which is the floating-no-ground signature
         ON AN EEG CHANNEL and a perfectly HEALTHY EMG channel. It scored C1's
         muscle channel at 0.0% when it is usable in 97.6% of epochs.

  BUG 2  Rung 2 was gated on the total usable FRACTION. C1 on 2026-07-31 is
         usable in only 31.3% of epochs and contains a single 485.7 minute
         unbroken block: the 8.1 hours that produced the only real sleep data
         this project held. A fraction gate called it FAIL.

Ground truth, from 30-resources/meetings/2026-08-03-data-quality-report-for-professor.md
and 2026-08-07-overnight-recording-two-animals-work.md:

  uid0731-18-06-37   C1 and C2 scoreable, everything else not. D2 correctly rejected.
  uid0806-16-57-38   B1 and D2 scoreable, everything else not.

Run:  ~/eeg-analysis-venv/bin/python tests/test_ladder_verdicts.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

from core import criteria as C          # noqa: E402
from core import qc_thresholds as T     # noqa: E402

from core.paths import CACHE_ROOT           # noqa: E402

# NOT /tmp. `tmpfiles.d` empties /tmp on every boot, so a hardcoded
# /tmp/eeg_pipeline_cache guarantees this suite finds nothing and skips.
CACHE = CACHE_ROOT

# recording -> {position: should rung 2 PASS}
EXPECTED_CONNECTION = {
    "feat_allego_1__uid0731-18-06-37.npz": {
        "C1": True, "C2": True,
        "A1": False, "A2": False, "B1": False, "B2": False, "D1": False, "D2": False,
    },
    "regression_uid0806-16-57-38.npz": {
        "B1": True, "D2": True,
        "A1": False, "A2": False, "B2": False, "C1": False, "C2": False, "D1": False,
    },
}

FAILURES: list[str] = []
SKIPPED: list[str] = []


def load(cache_name: str) -> C.EpochFeatures:
    p = CACHE / cache_name
    z = np.load(p, allow_pickle=True)
    spec = C.CohortSpec(roles=("eeg", "emg"))
    return C.EpochFeatures(
        base=str(p), fs=int(z["fs"]), epoch_s=int(z["epoch_s"]),
        n_epochs=int(z["n_epochs"]), n_samples=int(z["n_samples"]),
        sites=list(z["sites"]), spec=spec, hum=z["hum"], rms=z["rms"],
        rail=z["rail"], slope=z["slope"], delta=z["delta"], lfhf=z["lfhf"])


def check(label: str, got, want) -> None:
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {got!r:<8} want {want!r}")
    if not ok:
        FAILURES.append(f"{label}: got {got!r}, want {want!r}")


print("\n=== BUG 1: the hum guard must not fire on EMG ===")
print("A healthy EMG channel is quiet and broadband-flat, which is exactly what")
print("the floating-no-ground guard looks for on an EEG channel.")
have_0731 = (CACHE / "feat_allego_1__uid0731-18-06-37.npz").exists()
if have_0731:
    feat = load("feat_allego_1__uid0731-18-06-37.npz")
    floor = C.floor_stats(feat)
    site = feat.spec.site_of("C1", "emg")
    v = C.check_hum_validity(feat, site, floor)
    print(f"  C1 EMG {site}: hum {100 * v['hum_fraction']:.1f}% usable, "
          f"slope {100 * v['slope_fraction']:.1f}% usable, "
          f"guard would fire = {v['contradiction']}")
    m = C.usable(feat, site, floor, "hum", role="emg")
    check("C1 EMG usable with role='emg' (guard skipped)", round(float(m.mean()), 3), 0.976)
    m_eeg = C.usable(feat, feat.spec.site_of("C1", "eeg"), floor, "hum", role="eeg")
    check("C1 EEG longest block, epochs -> min",
          round(C.longest_run(m_eeg) * feat.epoch_s / 60, 1), 485.7)
else:
    print("  SKIP: no cached features for uid0731")

print("\n=== BUG 2: rung 2 is gated on the longest unbroken block ===")
print("C1 on 2026-07-31 is usable in only 31.3% of epochs and is the animal that")
print("produced this project's only 8.1 hour unbroken sleep block.")
if have_0731:
    both = (C.usable(feat, feat.spec.site_of("C1", "eeg"), floor, "hum", role="eeg")
            & C.usable(feat, feat.spec.site_of("C1", "emg"), floor, "hum", role="emg"))
    s = C.summarise(feat, both)
    print(f"  C1 both roles: {100 * s['usable_fraction']:.1f}% usable, longest "
          f"unbroken {s['longest_block_minutes']:.1f} min")
    check("a fraction gate at 0.5 would reject C1",
          s["usable_fraction"] < 0.5, True)
    check("the block gate accepts C1",
          s["longest_block_minutes"] >= T.MIN_BLOCK_MINUTES, True)

print("\n=== the ladder's rung 2 verdict against the vault's scoreable set ===")
for cache_name, expected in EXPECTED_CONNECTION.items():
    if not (CACHE / cache_name).exists():
        print(f"  SKIP {cache_name}: not cached")
        SKIPPED.append(cache_name)
        continue
    feat = load(cache_name)
    floor = C.floor_stats(feat)
    print(f"\n  {cache_name}   {feat.n_epochs} epochs of {feat.epoch_s}s")
    for pos, should_pass in expected.items():
        masks = {}
        for role in feat.spec.roles:
            masks[role] = C.usable(feat, feat.spec.site_of(pos, role), floor,
                                   "hum", role=role, allow_refused=True)
        both = np.ones(feat.n_epochs, dtype=bool)
        for m in masks.values():
            both &= m
        s = C.summarise(feat, both)
        passes = s["longest_block_minutes"] >= T.MIN_BLOCK_MINUTES
        check(f"{pos} connection PASS "
              f"({100 * s['usable_fraction']:5.1f}%, "
              f"{s['longest_block_minutes']:6.1f} min)", passes, should_pass)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S)")
    for f in FAILURES:
        print("  " + f)
    sys.exit(1)
if SKIPPED:
    # A suite that verified nothing must not print that it passed. Both source
    # recordings live only in S3 now, so their feature caches cannot be rebuilt
    # on this machine without pulling the raw files back.
    print(f"VERIFIED NOTHING: {len(SKIPPED)} of {len(EXPECTED_CONNECTION)} "
          f"recordings have no feature cache under {CACHE}")
    for c in SKIPPED:
        print("  uncached: " + c)
    print("The rung 2 comparison above did NOT run. This is not a pass.")
    sys.exit(2)
print("all ladder verdict tests pass: the ladder agrees with the vault's "
      "scoreable set on both recordings")

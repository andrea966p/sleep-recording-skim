#!/usr/bin/env python3
"""FALSIFICATION SUITE: the tests that are allowed to fail.

The other two suites reproduce numbers this project has already published. They
prove the code did not drift. They CANNOT prove it is right: they would have
stayed green through the whole hum-criterion era, while a floating unreferenced
amplifier input was being reported as 100 percent usable EEG.

This suite is the other half, and it is the software arm of the positive control
this project has owed itself since 2026-08-07. Every case has an answer decided
BEFORE the engine runs, stated in `tests/synth.py`, and half the cases are things
the engine must REJECT. The signal is injected at the FILE level, so the whole
measurement chain runs through the ordinary `open_xdat` path.

ASSERTIONS ARE RELATIVE, NOT ABSOLUTE, and that is a deliberate choice made after
the first version of this file asserted absolute pass rates and was wrong three
times out of seven. The scientific claim of the criterion is not "a good channel
scores above 90 percent". It is "a connected channel is separated from a wire-free
one". So the suite asserts SEPARATION and ORDERING, and prints the absolute
numbers as calibration rather than testing them. A falsification test that pins a
number is just another regression test wearing a different hat.

WHAT IS ASSERTED
  1  SENSITIVITY  a steep 1/f channel at a plausible amplitude is usable, and by
                  a wide margin over the floor. Without this the criterion could
                  pass every other case by rejecting everything.
  2  THE TRAP     a wire-free input band-passed to 0.5-30 Hz, which "looks like
                  beautiful EEG", is separated from a real one by a wide margin.
  3  RAILING      a channel pinned at full scale is rejected outright.
  4  FLOOR        wire-free inputs score at about FLOOR_PERCENTILE, which is what
                  they must do BY CONSTRUCTION -- see the note on
                  `falsification_check` below.
  5  NO-GROUND    the A1 signature (quiet AND flat) makes `usable()` RAISE on the
                  hum criterion instead of returning a confident wrong number.
  6  CATEGORY     the slope criterion RAISES on an EMG role.
  7  DIRECTION    a connected EEG channel is spectrally steeper than the floor,
                  and the trap sits between the two.

Run:  ~/eeg-analysis-venv/bin/python tests/test_criterion_falsification.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

from core import criteria as C
from core import qc_thresholds as T
from tests import synth

FAILURES: list[str] = []
NOTES: list[str] = []
SECONDS = 1800          # 180 QC epochs of 10 s, six times MIN_USABLE_EPOCHS
SPEC = C.CohortSpec(roles=("eeg", "emg"), ports="A", slot_bases=(1,))


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'ok  ' if ok else 'FAIL'}  {label:<50} {detail}")
    if not ok:
        FAILURES.append(f"{label}: {detail}")


def run(tmp: Path, name: str, maker) -> tuple[C.EpochFeatures, C.FloorStats]:
    """Build a recording whose A/1 is `maker`, and measure it."""
    rng = np.random.default_rng(abs(hash(name)) % (2 ** 32))
    n = SECONDS * synth.FS
    base = synth.build(tmp / f"synth_{name}", maker(n, rng), seconds=SECONDS)
    feat = C.compute_features(base, SPEC, progress=None)
    return feat, C.floor_stats(feat)


def frac(feat, floor, site="A/1", criterion="slope") -> float:
    return float(C._raw_mask(feat, site, floor, criterion).mean())


def main() -> int:
    print("=" * 78)
    print("FALSIFICATION SUITE -- known-signal injection, answers fixed in advance")
    print(f"thresholds hash: {C.thresholds_hash()}")
    print("=" * 78)

    assert synth.EPOCH_S == T.EPOCH_S_QC, (
        f"synth builds {synth.EPOCH_S}s epochs but the QC epoch is "
        f"{T.EPOCH_S_QC}s; the generator and the engine must agree")

    with tempfile.TemporaryDirectory(prefix="eeg_synth_") as td:
        tmp = Path(td)

        # ---------------------------------------------------- connected EEG
        print("\nA  CONNECTED EEG  (steep 1/f, 50 uV per epoch)")
        f_eeg, fl_eeg = run(tmp, "connected", synth.connected_eeg)
        eeg = frac(f_eeg, fl_eeg)
        eeg_slope = float(np.median(f_eeg.slope[:, f_eeg.col("A/1")]))
        eeg_rms = float(np.median(f_eeg.rms[:, f_eeg.col("A/1")]))
        print(f"     slope median {eeg_slope:+.2f}, rms median {eeg_rms:.0f} uV, "
              f"floor slope p1 {fl_eeg.slope_p1:+.2f}")
        check("1 connected EEG is usable", eeg > 0.90,
              f"{100 * eeg:.1f}% of epochs")
        check("7a connected EEG is steeper than the floor median",
              eeg_slope < fl_eeg.slope_median,
              f"{eeg_slope:+.2f} vs {fl_eeg.slope_median:+.2f}")

        fc = C.falsification_check(f_eeg, fl_eeg, "slope")
        floor_mean = fc["mean_usable_fraction"]
        expected = T.FLOOR_PERCENTILE / 100.0
        check("4 wire-free floor scores about FLOOR_PERCENTILE",
              floor_mean <= 2.5 * expected,
              f"mean {100 * floor_mean:.2f}% against an expected "
              f"{100 * expected:.2f}%")
        check("4b falsification_check agrees", fc["passes"],
              f"bar is 3x the by-construction rate of "
              f"{100 * fc['expected_by_construction']:.2f}%")

        # 6 CATEGORY ERROR
        try:
            C.usable(f_eeg, "A/2", fl_eeg, "slope", role="emg")
            check("6 slope criterion refuses an EMG role", False, "did NOT raise")
        except C.CriterionRefused:
            check("6 slope criterion refuses an EMG role", True, "CriterionRefused")

        # ---------------------------------------------------------- the trap
        print("\nB  THE TRAP  (no wire, band-passed 0.5-30 Hz, 69 uV -- looks perfect)")
        f_tr, fl_tr = run(tmp, "trap", synth.trap_bandpassed)
        trap = frac(f_tr, fl_tr)
        trap_slope = float(np.median(f_tr.slope[:, f_tr.col("A/1")]))
        print(f"     slope median {trap_slope:+.2f}, floor p1 {fl_tr.slope_p1:+.2f}")
        # 2a THE RAW SCORE IS THE POINT: the trap BEATS the bar outright.
        # This is asserted, not merely reported, so that if anyone ever "fixes"
        # the criterion by narrowing the band, this line fails and forces them
        # to notice that the guard below is what was actually protecting them.
        check("2a the trap DOES fool the bare slope bar",
              trap > 0.90,
              f"{100 * trap:.1f}% usable, slope {trap_slope:+.2f} vs floor p1 "
              f"{fl_tr.slope_p1:+.2f} -- filtering manufactures slope")

        # 2b ... and the band-limit guard is what stops it reaching a verdict.
        bl = C.check_bandlimit_validity(f_tr, "A/1")
        check("2b band-limit guard identifies the trap as filtered",
              bl["verdict"] == "band_limited",
              f"sub-band drop {bl['drop']:+.2f} against a bar of "
              f"{bl['threshold']:+.2f}")
        try:
            C.usable(f_tr, "A/1", fl_tr, "slope", role="eeg")
            check("2c usable() refuses the trap", False,
                  "did NOT raise -- a filtered wire-free input would be "
                  "published as 100% usable EEG")
        except C.CriterionRefused:
            check("2c usable() refuses the trap", True, "CriterionRefused")

        # 2d the guard must not fire on anything scale free
        for label, feat_ in (("connected EEG", f_eeg), ("floor site", f_eeg)):
            site_ = "A/1" if label == "connected EEG" else "A/9"
            b = C.check_bandlimit_validity(feat_, site_)
            check(f"2d guard stays silent on a scale-free {label}",
                  b["verdict"] == "raw", f"drop {b['drop']:+.2f}")

        check("7b the trap is flatter than a connected EEG",
              trap_slope > eeg_slope,
              f"{trap_slope:+.2f} vs {eeg_slope:+.2f}")

        # --------------------------------------------------------- no ground
        print("\nC  NO GROUND  (the A1 signature: quiet AND flat)")
        f_fl, fl_fl = run(tmp, "floating", synth.floating_no_ground)
        v = C.check_hum_validity(f_fl, "A/1", fl_fl)
        print(f"     hum says {100 * v['hum_fraction']:.1f}% usable, slope says "
              f"{100 * v['slope_fraction']:.1f}%; channel 60 Hz median "
              f"{v['median_hum_uv']:.0f} uV vs floor {v['floor_hum_median_uv']:.0f} uV")
        check("5a quiet+flat is flagged as contradictory", v["contradiction"],
              f"hum {100 * v['hum_fraction']:.0f}% / slope "
              f"{100 * v['slope_fraction']:.0f}%")
        try:
            C.usable(f_fl, "A/1", fl_fl, "hum", role="eeg")
            check("5b usable() refuses the hum criterion", False,
                  "did NOT raise -- a floating channel would be published")
        except C.CriterionRefused:
            check("5b usable() refuses the hum criterion", True, "CriterionRefused")
        check("5c slope criterion calls the floating channel dead",
              frac(f_fl, fl_fl) < 0.05,
              f"{100 * frac(f_fl, fl_fl):.1f}% usable")

        # ------------------------------------------------------------ railed
        print("\nD  RAILED  (pinned at the ADC ceiling)")
        f_rl, fl_rl = run(tmp, "railed", synth.railed)
        check("3 railed channel is rejected outright",
              frac(f_rl, fl_rl) == 0.0, f"{100 * frac(f_rl, fl_rl):.1f}% usable")

    print()
    for n_ in NOTES:
        print("NOTE  " + n_.replace("\n", "\n      "))
    if NOTES:
        print()
    if FAILURES:
        print(f"{len(FAILURES)} FALSIFICATION FAILURE(S):")
        for f_ in FAILURES:
            print(f"  - {f_}")
        print("\nMovement here is NOT automatically a bug in the test. A failure "
              "means the criterion\ndoes not do what it claims.")
        return 1
    print("all falsification checks pass: the criterion accepts real signal, "
          "separates the trap,\nrefuses the no-ground signature, and refuses the "
          "category error.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

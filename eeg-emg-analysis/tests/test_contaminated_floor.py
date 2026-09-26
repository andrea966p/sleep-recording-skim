#!/usr/bin/env python3
"""A grounded floor that carries signal must yield NO slope verdict -- never FAIL.

`floor_stats()` used to validate the floor only on hum: a chip with a ground
reference was trusted. But a grounded chip's wire-free inputs can still pick up
real signal. Their slope threshold then lands at -2.4 to -3.5, past anything real
EEG reaches, and a healthy electrode reads `0.0% usable`. That happened on 11
cards across S-SL, W-SL and S-SD and produced a retracted S-SL conclusion on
2026-09-26. See 03-troubleshooting/symptoms/contaminated-floor-rejects-good-eeg.

🔑 THE CENTRAL CASES ARE THE TWO THAT A WRONG FIX GETS BACKWARDS.
  - A healthy EEG on a contaminated floor must be UNJUDGEABLE, not FAIL.
  - A DEAD EEG on a CLEAN floor must still FAIL. A detector that compares the
    floor with the animal's own EEG calls every dead electrode's floor
    contaminated, because a dead electrode is as flat as the floor. That is the
    detector proposed on 2026-08-27, and it scores 1.00 on the three genuinely
    open electrodes on this rig.

Features are built directly, not from a synthetic raw file: the question is what
the ladder does with a given floor, not how the floor is measured.

    PYTHONPATH=. ~/eeg-test-venv/bin/python3 tests/test_contaminated_floor.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import criteria as C
from core import qc_thresholds as T
from cards import ladder as L

PASS, FAIL = [], []
N_EPOCHS = 1000              # 10 s epochs = 2.8 h, far above the 15 min block bar
SPEC = C.CohortSpec(roles=("eeg", "emg"), ports="A", slot_bases=(1,))


def check(name, fn):
    try:
        fn()
    except Exception:
        FAIL.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}")
    else:
        PASS.append(name)
        print(f"  ok    {name}")


def _feat(*, eeg_slope: float, eeg_rms: float, n_steep_floor: int,
          floor_hum: float = 2000.0, seed: int = 20260926) -> C.EpochFeatures:
    """One 2-role chip. `n_steep_floor` of its 14 floor sites carry EEG-like signal.

    Clean floor sites: slope ~ N(-0.1, 0.15), the flat spectrum of an unwired
    input, matching the +0.10 to -0.61 typical-site range measured on this rig.
    Steep floor sites: slope ~ N(-2.0, 0.3), as on uid0921's contaminated chips.
    """
    rng = np.random.default_rng(seed)
    animal = SPEC.animal_sites()["A1"]
    floor = C.floor_sites_of(SPEC, "A1")
    sites = [animal["eeg"], animal["emg"]] + floor
    n = len(sites)
    slope = np.empty((N_EPOCHS, n))
    rms = np.empty((N_EPOCHS, n))
    hum = np.empty((N_EPOCHS, n))
    slope[:, 0] = rng.normal(eeg_slope, 0.1, N_EPOCHS)
    rms[:, 0] = rng.normal(eeg_rms, 3.0, N_EPOCHS)
    hum[:, 0] = rng.normal(10.0, 1.0, N_EPOCHS)
    slope[:, 1] = rng.normal(-0.2, 0.1, N_EPOCHS)       # EMG is broadband: flat
    rms[:, 1] = rng.normal(40.0, 3.0, N_EPOCHS)
    hum[:, 1] = rng.normal(10.0, 1.0, N_EPOCHS)
    for j in range(len(floor)):
        mu = -2.0 if j < n_steep_floor else -0.1
        sd = 0.3 if j < n_steep_floor else 0.15
        slope[:, 2 + j] = rng.normal(mu, sd, N_EPOCHS)
        rms[:, 2 + j] = rng.normal(80.0, 5.0, N_EPOCHS)
        hum[:, 2 + j] = rng.normal(floor_hum, floor_hum * 0.1, N_EPOCHS)
    # a rail value above zero only where the channel is actually railing
    rail = np.zeros((N_EPOCHS, n))
    if eeg_rms > T.RMS_HI_UV:
        rail[:, 0] = 0.01
    z = np.zeros((N_EPOCHS, n))
    return C.EpochFeatures(base="synthetic", fs=1000, epoch_s=T.EPOCH_S_QC,
                           n_epochs=N_EPOCHS,
                           n_samples=N_EPOCHS * T.EPOCH_S_QC * 1000,
                           sites=sites, spec=SPEC, hum=hum, rms=rms, rail=rail,
                           slope=slope, delta=z, lfhf=z)


def _rung2(feat, criterion="slope"):
    return L.rung2_connection(feat, "A1", SPEC, C.floor_stats(feat, "A1"), criterion)


# --------------------------------------------------------------------------- #
def t_constant_sits_in_the_measured_gap():
    """-0.61 is the steepest CLEAN typical site measured, -1.12 the flattest bad one."""
    assert -1.12 < T.FLOOR_MAX_SITE_MEDIAN_SLOPE < -0.61, T.FLOOR_MAX_SITE_MEDIAN_SLOPE


def t_clean_floor_is_flat():
    f = C.floor_stats(_feat(eeg_slope=-1.5, eeg_rms=75, n_steep_floor=0), "A1")
    assert f.grounded and f.slope_flat, f.as_dict()
    assert f.slope_validity_reason == ""
    assert "slope_flat" in f.as_dict() and "site_median_slope" in f.as_dict()


def t_healthy_eeg_on_clean_floor_passes():
    """SENSITIVITY. Without it the fix could pass by refusing everything."""
    r = _rung2(_feat(eeg_slope=-1.5, eeg_rms=75, n_steep_floor=0))
    assert r.verdict == "PASS", (r.verdict, r.reason)


def t_healthy_eeg_on_contaminated_floor_is_unjudgeable():
    """THE BUG. 9 of 14 floor sites steep, as on uid0921 chip A1."""
    feat = _feat(eeg_slope=-1.5, eeg_rms=75, n_steep_floor=9)
    f = C.floor_stats(feat, "A1")
    assert f.grounded, "the chip IS grounded; hum alone would trust it"
    assert not f.slope_flat, f.as_dict()
    assert f.slope_p1 < -1.5, "the floor must demand more than the EEG delivers"
    r = _rung2(feat)
    assert r.verdict == "UNJUDGEABLE", (r.verdict, r.reason)
    assert r.verdict != "FAIL"
    assert "not flat" in r.headline, r.headline
    assert "%" not in f"{r.headline} {r.reason}", "no fraction may be reported"
    assert "floor" in r.detail, "render_card indexes detail['floor']"


def t_before_the_fix_this_was_a_zero_percent_fail():
    """Pins the defect: judged anyway, the same animal reads ~0% usable."""
    feat = _feat(eeg_slope=-1.5, eeg_rms=75, n_steep_floor=9)
    f = C.floor_stats(feat, "A1")
    frac = float(C.usable(feat, "A/1", f, "slope", role="eeg").mean())
    assert frac < 0.05, f"expected the contaminated threshold to reject, got {frac:.1%}"


def t_dead_eeg_on_clean_floor_still_fails():
    """🔑 THE CIRCULARITY GUARD. uid0912 D2: slope -0.08, rms 30 uV, clean floor."""
    r = _rung2(_feat(eeg_slope=-0.08, eeg_rms=30, n_steep_floor=0))
    assert r.verdict == "FAIL", (r.verdict, r.reason)


def t_railing_eeg_on_clean_floor_still_fails():
    """uid0825 D1 / uid0826 D1: slope ~0, rms 2700 uV. A real open electrode."""
    r = _rung2(_feat(eeg_slope=-0.05, eeg_rms=2700, n_steep_floor=0))
    assert r.verdict == "FAIL", (r.verdict, r.reason)


def t_a_minority_of_steep_sites_does_not_trip_it():
    """One or two coupled sites are the estimator's job, not this guard's."""
    feat = _feat(eeg_slope=-1.5, eeg_rms=75, n_steep_floor=3)
    assert C.floor_stats(feat, "A1").slope_flat


def t_hum_criterion_is_not_gated_by_the_slope_floor():
    """The new gate is scoped to the slope criterion and must not fire on hum.

    ⚠️ KNOWN GAP, NOT PINNED AS CORRECT. On this input the hum card still reads
    FAIL, through a different door: `check_hum_validity` cross-checks hum against
    the SLOPE threshold, which a contaminated floor makes unbeatable, and refuses
    the hum criterion. No card in the four affected recordings is hum-judged
    (all 32 hum cards are the pooled-floor HLB-fem cohort), so it is left open.
    """
    r = _rung2(_feat(eeg_slope=-1.5, eeg_rms=75, n_steep_floor=9), criterion="hum")
    assert "not flat" not in (r.headline or ""), (r.verdict, r.headline)


def t_ungrounded_is_still_reported_as_ungrounded():
    """Both faults at once: the ground is the more basic one and is named first."""
    r = _rung2(_feat(eeg_slope=-1.5, eeg_rms=75, n_steep_floor=9, floor_hum=200.0))
    assert r.verdict == "UNJUDGEABLE"
    assert "60 Hz" in r.headline, r.headline


def main() -> int:
    print("THE CONTAMINATED-FLOOR PATH")
    for fn in (t_constant_sits_in_the_measured_gap, t_clean_floor_is_flat,
               t_healthy_eeg_on_clean_floor_passes,
               t_healthy_eeg_on_contaminated_floor_is_unjudgeable,
               t_before_the_fix_this_was_a_zero_percent_fail,
               t_dead_eeg_on_clean_floor_still_fails,
               t_railing_eeg_on_clean_floor_still_fails,
               t_a_minority_of_steep_sites_does_not_trip_it,
               t_hum_criterion_is_not_gated_by_the_slope_floor,
               t_ungrounded_is_still_reported_as_ungrounded):
        check(fn.__name__, fn)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

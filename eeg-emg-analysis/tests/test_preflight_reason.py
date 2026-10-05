"""The pre-flight's OPEN reason must name the channel that is open (fixed 2026-10-02).

Before the fix an open EMG beside a working EEG was reported as
"60 Hz 16 uV vs 150 uV limit: not connected" -- the EEG's harmless number under an
OPEN verdict. The verdicts themselves must not change; only the reason text did.
"""
import numpy as np

from core import qc_thresholds as T
from qc.preflight_screen import verdict

N = 40
GOOD, BAD = np.full(N, 10.0), np.full(N, 3000.0)
RMS, CLIP = np.full(N, 60.0), np.zeros(N)
GROUNDED = 2 * T.FLOOR_MIN_HUM_UV


def _v(eeg, emg, floor=GROUNDED):
    return verdict(eeg, emg, RMS, CLIP, floor)[1:]


def test_open_emg_is_named_and_eeg_is_not():
    tag, why = _v(GOOD, BAD)
    assert tag == "OPEN"
    assert "EMG 60 Hz 3000" in why and "EEG" not in why


def test_open_eeg_is_named():
    tag, why = _v(BAD, GOOD)
    assert tag == "OPEN" and "EEG 60 Hz 3000" in why and "EMG" not in why


def test_both_open_are_both_named():
    tag, why = _v(BAD, BAD)
    assert tag == "OPEN" and "EEG 60 Hz" in why and "EMG 60 Hz" in why


def test_clean_is_still_clean():
    assert _v(GOOD, GOOD) == ("CLEAN", "")


def test_ungrounded_floor_still_wins_over_open():
    tag, _ = _v(GOOD, BAD, floor=T.FLOOR_MIN_HUM_UV / 2)
    assert tag == "UNJUDGEABLE"


def test_chip_floor_is_on_the_gate_scale():
    """A 1000 uV-peak 60 Hz line on every wire-free input must read ~1000, as core/criteria.py
    reads it -- not ~707, the rms the screen used to report (fixed 2026-10-02)."""
    from qc.preflight_screen import chip_floor
    fs, secs = 1000, 60
    t = np.arange(fs * secs) / fs
    rng = np.random.default_rng(0)
    X = np.vstack([1000 * np.sin(2 * np.pi * 59.98 * t + k) + rng.normal(0, 20, t.size) for k in range(32)])
    floor, n = chip_floor(X, fs, {i: i for i in range(32)}, 0)
    assert n == 14
    assert 950 < floor < 1010, floor

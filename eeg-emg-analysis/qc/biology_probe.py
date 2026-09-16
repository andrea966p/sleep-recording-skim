#!/usr/bin/env python3
"""Does the live stream carry BIOLOGY, or only a working connection?

qc/preflight_screen.py answers rung 1: is the electrode electrically connected.
A connected electrode sitting in saline would pass it. This asks the next
question on a few minutes of live stream -- does the signal have the shape of
neural tissue -- using the same spectral-slope measurement as core/criteria.py.

    /usr/bin/python3 -m qc.biology_probe [--secs 300] [--npz FILE] [--keep]

WHAT IT MEASURES

    slope     log-log spectral slope over SLOPE_BAND_HZ. Real EEG is steep
              (working animals -1.5 to -2.1); a wire-free input is flat
              (-1.29 to -0.07).
    drop      the band-limit guard: slope(25-45) - slope(1-25). A power law is
              scale free, a filter corner is not. Below BANDLIMIT_MAX_DROP the
              input is filtered and the slope reading is not entitled to a
              verdict.
    delta_fr  share of 1-40 Hz power inside BAND_DELTA. High in NREM.
    r(E,M)    correlation between the animal's OWN filtered EEG and EMG. Working
              animals sit at 0.07-0.08; a fault in a path shared by both drives
              it up past SHARED_PATH_CORR.

🛑 SLOPE TRACKS VIGILANCE STATE AS WELL AS ELECTRODE QUALITY. The -1.5 to -2.1
reference range comes from full recordings dominated by sleep. Awake EEG is
genuinely flatter because there is less delta in it, so a short sample taken in
the dark phase will read flat on a perfectly good electrode. The banner prints
the circadian time for exactly this reason. A flat reading at ZT13 means
"inconclusive, look again in the light phase", NOT "bad electrode".

This is a diagnostic, not a verdict. Scorability is a property of a multi-hour
recording -- see cards/ and the verdict ladder -- and no few-minute capture can
stand in for it.
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys
import tempfile

import numpy as np
import scipy.signal as sg

from core import qc_thresholds as T
from qc.preflight_screen import capture, layout


def _slope(P, freqs, edges):
    """Least-squares log-log slope over one band, per epoch."""
    m = (freqs >= edges[0]) & (freqs <= edges[1])
    centred = np.log10(freqs[m]) - np.log10(freqs[m]).mean()
    return (np.log10(P[:, m] + 1e-20) * centred).sum(1) / (centred ** 2).sum()


def _zeitgeber():
    """Hours since lights-on, and which phase that is."""
    now = datetime.datetime.now()
    zt = (now.hour + now.minute / 60 - T.LIGHTS_ON_HOUR) % 24
    dark = (T.LIGHTS_OFF_HOUR - T.LIGHTS_ON_HOUR) % 24
    return zt, "DARK / active" if zt >= dark else "LIGHT / rest"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--secs", type=float, default=300.0,
                    help="seconds of stream to capture (default 300)")
    ap.add_argument("--npz", help="probe this capture instead of taking a new one")
    ap.add_argument("--keep", action="store_true", help="do not delete the capture")
    args = ap.parse_args()

    path, temporary = args.npz, False
    if path is None:
        fd, path = tempfile.mkstemp(suffix=".npz", prefix="biology-")
        os.close(fd)
        temporary = not args.keep
        capture(args.secs, path)

    try:
        cap = np.load(path, allow_pickle=False)
        X, sites, ntv, fs = cap["signals"], cap["sites"], cap["ntv"], float(cap["fs"])
    finally:
        if temporary and os.path.exists(path):
            os.unlink(path)

    animals = layout(sites, ntv)
    if not animals:
        sys.exit("no EEG/EMG pairs in the selection - select /1 /2 /33 /34 per port")

    ep = int(T.EPOCH_S * fs)
    nep = X.shape[1] // ep
    if nep < 1:
        sys.exit("captured less than one %d s epoch" % T.EPOCH_S)

    freqs = np.fft.rfftfreq(ep, 1 / fs)
    win = np.hanning(ep)
    wgain = win.sum() / 2
    in_delta = (freqs >= T.BAND_DELTA[0]) & (freqs <= T.BAND_DELTA[1])
    in_band = (freqs >= T.SLOPE_BAND_HZ[0]) & (freqs <= T.SLOPE_BAND_HZ[1])

    sos_eeg = sg.butter(4, list(T.FILT_EEG), btype="band", fs=fs, output="sos")
    sos_emg = sg.butter(4, [T.FILT_EMG[0], min(T.FILT_EMG[1], fs / 2 - 1)],
                        btype="band", fs=fs, output="sos")

    zt, phase = _zeitgeber()
    print("\n%d epochs of %d s, fs %g Hz | ZT%.1f, %s"
          % (nep, T.EPOCH_S, fs, zt, phase))
    print("slope band %g-%g Hz | working animals -1.5 to -2.1 | wire-free floor "
          "-1.29 to -0.07" % T.SLOPE_BAND_HZ)
    print("band-limit bar %+.2f | shared-path bar %.2f (working 0.07-0.08)\n"
          % (T.BANDLIMIT_MAX_DROP, T.SHARED_PATH_CORR))
    print("%-7s %8s %8s %9s %8s  %s"
          % ("animal", "slope", "drop", "delta_fr", "r(E,M)", "reading"))
    print("-" * 78)

    for a in animals:
        v = X[a["eeg"], :nep * ep].astype(np.float64).reshape(nep, ep)
        P = (np.abs(np.fft.rfft(v * win, axis=1)) / wgain) ** 2
        slope = float(np.median(_slope(P, freqs, T.SLOPE_BAND_HZ)))
        drop = float(np.median(_slope(P, freqs, T.BANDLIMIT_HI_BAND))
                     - np.median(_slope(P, freqs, T.BANDLIMIT_LO_BAND)))
        delta_fr = float(np.median(P[:, in_delta].sum(1) / P[:, in_band].sum(1)))

        eeg_f = sg.sosfiltfilt(sos_eeg, X[a["eeg"]].astype(np.float64))
        emg_f = sg.sosfiltfilt(sos_emg, X[a["emg"]].astype(np.float64))
        r = float(np.corrcoef(eeg_f, emg_f)[0, 1])

        if drop < T.BANDLIMIT_MAX_DROP:
            note = "BAND LIMITED - slope not valid on filtered input"
        elif slope <= -1.5:
            note = "steep 1/f: neural tissue"
        elif slope > -1.3:
            note = "flat - wire-free, or simply awake"
        else:
            note = "between the populations"
        if abs(r) > T.SHARED_PATH_CORR:
            note += "; SHARED-PATH FAULT (r %.2f)" % r

        print("%-7s %8.2f %8.2f %9.3f %8.3f  %s"
              % (a["name"], slope, drop, delta_fr, r, note))

    if phase.startswith("DARK"):
        print("\n⚠️  Captured in the dark phase, when mice are active and EEG is "
              "legitimately flat.\n   Treat a flat slope here as inconclusive, not as a "
              "failed electrode.")
    print("\nBiology is not scorability: that needs a block of at least %.0f min and "
          "state\nvariation this capture cannot contain." % T.MIN_BLOCK_MINUTES)


if __name__ == "__main__":
    main()

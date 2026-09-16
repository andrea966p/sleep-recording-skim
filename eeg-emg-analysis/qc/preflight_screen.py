#!/usr/bin/env python3
"""PRE-FLIGHT -- is this rig worth pressing record on, right now?

Runs the stage 1 QC measurement against a few minutes of LIVE stream instead of
a finished .xdat, so a dead or open channel is found while the animal is still
on the bench rather than three weeks later in the hypnogram.

Every threshold comes from core.qc_thresholds. Nothing is defined here: a
pre-flight that used its own numbers could pass a channel the real gate will
later reject, which is worse than no pre-flight at all.

🛑 THIS IS A SMOKE TEST, NOT A VERDICT. It shares stage 1's measurement but not
its evidence base. Contact state flips within minutes, so a clean screen does
not promise a clean 20 h recording, and a channel that screens badly may recover.
It answers one question: is something grossly wrong that I can still fix?

Usage
    /usr/bin/python3 -m qc.preflight_screen [--secs 300] [--npz FILE] [--keep]

With no --npz it captures fresh data by calling qc/preflight_grab.py under the
radiens venv (see that file for why the work is split across two interpreters).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile

import numpy as np
import scipy.signal as sg

from core import qc_thresholds as T

# radiens lives only here; this interpreter has scipy but not radiens.
RADIENS_PYTHON = "/opt/neurosurveillance/venv/bin/python3"
GRAB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preflight_grab.py")


# --------------------------------------------------------------------------- #
def capture(secs: float, path: str) -> None:
    print("capturing %.0f s of live stream ..." % secs)
    subprocess.run([RADIENS_PYTHON, GRAB, path, str(secs)], check=True)


def layout(sites, ntv):
    """Group the captured channels into animals, mirroring derive_layout().

    /1 = EEG and /2 = EMG for the first animal on a port, /33 and /34 for the
    second. Both are already bipolar; they are used directly and never
    subtracted from one another.
    """
    by_port = {}
    for row, (site, n) in enumerate(zip(sites, ntv)):
        port = str(site).split("_")[1]
        by_port.setdefault(port, {})[int(n)] = row

    animals = []
    for port in sorted(by_port):
        rows = by_port[port]
        base = min(rows)
        for slot, off in enumerate((0, 32), start=1):
            eeg, emg = rows.get(base + off), rows.get(base + off + 1)
            if eeg is None or emg is None:
                continue
            animals.append(dict(name="%s%d" % (port, slot), eeg=eeg, emg=emg))
    return animals


def measure(X, fs):
    """Per-epoch features, computed exactly as pipeline/stage1_qc.py does."""
    sos_eeg = sg.butter(4, list(T.FILT_EEG), btype="band", fs=fs, output="sos")
    sos_emg = sg.butter(4, [T.FILT_EMG[0], min(T.FILT_EMG[1], fs / 2 - 1)],
                        btype="band", fs=fs, output="sos")
    sos_mn = sg.butter(4, list(T.FILT_MAINS), btype="band", fs=fs, output="sos")

    spe = int(T.EPOCH_S_QC * fs)                 # samples per QC epoch
    nep = X.shape[1] // spe
    if nep < 1:
        sys.exit("captured less than one %d s QC epoch" % T.EPOCH_S_QC)
    raw = X[:, :nep * spe].astype(np.float64)

    band = lambda sos: sg.sosfiltfilt(sos, raw, axis=1).reshape(X.shape[0], nep, spe)
    return dict(
        nep=nep,
        rms_eeg=band(sos_eeg).std(2),
        rms_emg=band(sos_emg).std(2),
        mains_eeg=band(sos_mn).std(2),
        mains_emg=band(sos_mn).std(2),
        clip=(np.abs(raw.reshape(X.shape[0], nep, spe)) >= T.RAIL_UV_EFF).mean(2),
    )


def verdict(eeg_mains, emg_mains, eeg_rms, clip):
    """Stage 1's gate and its failure names, for one animal."""
    not_open = (eeg_mains < T.OPEN_UV) & (emg_mains < T.OPEN_UV)
    not_flat = eeg_rms >= T.FLAT_UV
    not_clip = clip <= T.CLIP_FRAC
    ok = not_open & not_flat & not_clip

    med_rms = float(np.median(eeg_rms))
    if med_rms < T.DEAD_CHANNEL_UV:
        return ok, "DEAD", "median EEG rms %.1f < %.0f uV: never carried EEG" % (
            med_rms, T.DEAD_CHANNEL_UV)
    if not_open.mean() < 0.5:
        return ok, "OPEN", "60 Hz %.0f uV vs %.0f uV limit: not connected" % (
            float(np.median(eeg_mains)), T.OPEN_UV)
    if not_clip.mean() < 0.5:
        return ok, "CLIPPED", "amplifier at the rail (%.0f uV)" % T.RAIL_UV_EFF
    if ok.mean() < 0.5:
        return ok, "DIRTY", "only %.0f%% of epochs pass the gate" % (100 * ok.mean())
    return ok, "CLEAN", ""


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--secs", type=float, default=300.0,
                    help="seconds of stream to capture (default 300)")
    ap.add_argument("--npz", help="screen this capture instead of taking a new one")
    ap.add_argument("--keep", action="store_true", help="do not delete the capture")
    args = ap.parse_args()

    path, temporary = args.npz, False
    if path is None:
        fd, path = tempfile.mkstemp(suffix=".npz", prefix="preflight-")
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

    m = measure(X, fs)
    mins = m["nep"] * T.EPOCH_S_QC / 60.0
    print("\n%d channels, %.1f min, %d QC epochs of %d s, fs %g Hz"
          % (X.shape[0], mins, m["nep"], T.EPOCH_S_QC, fs))
    print("thresholds from core/qc_thresholds.py: open %.0f, dead %.0f, flat %.0f, "
          "rail %.0f uV" % (T.OPEN_UV, T.DEAD_CHANNEL_UV, T.FLAT_UV, T.RAIL_UV_EFF))

    # OPEN_UV is a 55-65 Hz amplitude test, so a mains notch anywhere at the
    # Hardware or Data stage removes the very quantity it measures and every
    # channel then passes "not open" whether or not it is connected.
    # A low median alone is not evidence: with the ground correctly pinned, hum on
    # connected channels is genuinely small. What a notch cannot do is leave ANY
    # channel with mains in the connected band, so the maximum is the real test.
    all_mains = np.concatenate([m["mains_eeg"], m["mains_emg"]])
    hum = np.median(all_mains)
    if hum < T.CONNECTED_HUM_BAND_UV[0] and all_mains.max() < T.CONNECTED_HUM_BAND_UV[0]:
        print("\n⚠️  median 60 Hz across all channels is %.1f uV, under the %.0f uV floor of "
              "CONNECTED_HUM_BAND_UV.\n   Connected channels have also been reported at "
              "6-20 uV, so this is not proof of\n   anything on its own -- but a mains notch "
              "or bandstop would produce exactly this,\n   and OPEN_UV is a 55-65 Hz test, so "
              "the verdicts below would be meaningless.\n   Check Signal Processing for a "
              "notch before believing this screen.\n   The vault rule is NEVER add a 60 Hz "
              "notch at any stage: see\n   06-references/radiens-software-reference.md"
              % (hum, T.CONNECTED_HUM_BAND_UV[0]))

    if m["nep"] < T.MIN_USABLE_EPOCHS:
        print("\n⚠️  %d epochs is under MIN_USABLE_EPOCHS (%d = %.0f min). Treat every "
              "row below as indicative only." % (m["nep"], T.MIN_USABLE_EPOCHS,
                                                 T.MIN_USABLE_EPOCHS * T.EPOCH_S_QC / 60))

    print("\n%-7s %9s %9s %9s %9s %7s  %-9s %s"
          % ("animal", "EEG rms", "EMG rms", "EEG 60Hz", "EMG 60Hz", "pass%",
             "verdict", "reason"))
    print("-" * 96)
    for a in animals:
        eeg_rms = m["rms_eeg"][a["eeg"]]
        emg_rms = m["rms_emg"][a["emg"]]
        eeg_mn = m["mains_eeg"][a["eeg"]]
        emg_mn = m["mains_emg"][a["emg"]]
        ok, tag, why = verdict(eeg_mn, emg_mn, eeg_rms, m["clip"][a["eeg"]])
        print("%-7s %9.1f %9.1f %9.1f %9.1f %6.0f%%  %-9s %s"
              % (a["name"], np.median(eeg_rms), np.median(emg_rms),
                 np.median(eeg_mn), np.median(emg_mn), 100 * ok.mean(), tag, why))

    print("\nA clean screen is not a promise: contact state flips within minutes.")


if __name__ == "__main__":
    main()

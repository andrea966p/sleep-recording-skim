#!/usr/bin/env python3
"""PRE-FLIGHT -- is this rig worth pressing record on, right now?

Runs the stage 1 QC measurement against a few minutes of LIVE stream instead of
a finished .xdat, so a dead or open channel is found while the animal is still
on the bench rather than three weeks later in the hypnogram.

Every threshold comes from core.qc_thresholds. Nothing is defined here: a
pre-flight that used its own numbers could pass a channel the real gate will
later reject, which is worse than no pre-flight at all.

🛑 IT CANNOT CHECK GROUNDING UNDER THE NORMAL MONTAGE. The per-chip floor lives on
the 14 wire-free inputs of each chip, `get_signals()` returns only SELECTED channels,
and radiens 4.0.0 has no setter for the selection. With 16 channels selected the
screen reports NO FLOOR rather than CLEAN, because a floating chip looks perfect on
its animal channels -- on 2026-09-17 this tool passed A2, C1 and D1 as CLEAN while
their floors were 454, 7 and 5 uV.

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
            animals.append(dict(name="%s%d" % (port, slot), eeg=eeg, emg=emg,
                                ntv=base + off))
    return animals


# An RHD2216 presents 16 real inputs, and the animal uses the first two of them.
# The other 14 are wire-free and are the in-file control. The remaining 16 slots of
# each 32-slot block have no amplifier behind them at all and read 3-8 uV, so they
# must NOT be counted as floor sites -- including them drags a grounded chip's floor
# down by a factor of ~20 and calls every chip ungrounded.
CHIP_REAL_SLOTS = 16


def chip_floor(X, fs, ntv_to_row, eeg_ntv):
    """Ground floor for the chip carrying `eeg_ntv`: 60 Hz line amplitude on its wire-free inputs.

    Returns (floor_uv, n_sites); NaN when too few of those inputs were captured.

    🛑 THE FLOOR IS ONLY VISIBLE IF THE MONTAGE SELECTS IT. `get_signals()` returns
    the SELECTED channels and nothing else, `get_metrics()` computes only those too
    (verified 2026-09-18: exactly 16 of 256 non-zero), and radiens 4.0.0 exposes no
    way to change the selection. So with the normal 16-channel montage this cannot
    be measured at all, and the screen says so instead of passing the chip.
    """
    rows = [ntv_to_row[n] for n in range(eeg_ntv + 2, eeg_ntv + CHIP_REAL_SLOTS)
            if n in ntv_to_row]
    if len(rows) < T.FLOOR_MIN_SITES:
        return float("nan"), len(rows)
    # ON THE GATE'S SCALE (fixed 2026-10-02). FLOOR_MIN_HUM_UV is applied by core/criteria.py to
    # the PEAK amplitude of the 59-61 Hz line in 10 s Hann epochs, median over epochs x sites.
    # This used to take the std of a 55-65 Hz band-pass, an rms that is sqrt(2) smaller for a
    # line, so the screen called chips "ungrounded" that the real gate would call grounded
    # (B1 on 2026-10-01: 591 here vs ~835 on the gate's scale).
    ep = int(T.EPOCH_S_QC * fs); nep = X.shape[1] // ep
    if nep < 1:
        return float("nan"), len(rows)
    blk = X[rows, :nep * ep].astype(np.float64).reshape(len(rows), nep, ep)
    blk -= blk.mean(2, keepdims=True)
    win = np.hanning(ep); f = np.fft.rfftfreq(ep, 1 / fs); m60 = (f >= 59) & (f <= 61)
    P = np.abs(np.fft.rfft(blk * win, axis=2)) / (win.sum() / 2)
    return float(np.median(P[:, :, m60].max(2))), len(rows)


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


def verdict(eeg_mains, emg_mains, eeg_rms, clip, floor):
    """Stage 1's gate and its failure names, for one animal.

    The floor is checked FIRST. Every other test on this chip is measured against
    its own wire-free inputs, so once those are floating nothing on the chip means
    anything -- and the channel still looks entirely normal. An ungrounded chip is
    UNJUDGEABLE, never FAIL.
    """
    not_open = (eeg_mains < T.OPEN_UV) & (emg_mains < T.OPEN_UV)
    not_flat = eeg_rms >= T.FLAT_UV
    not_clip = clip <= T.CLIP_FRAC
    ok = not_open & not_flat & not_clip

    if np.isnan(floor):
        return ok, "NO FLOOR", ("wire-free inputs not in the montage; "
                                "grounding cannot be checked")
    if floor < T.FLOOR_MIN_HUM_UV:
        return ok, "UNJUDGEABLE", ("chip floor %.0f uV < %.0f: ungrounded, nothing on "
                                   "this chip is measurable" % (floor, T.FLOOR_MIN_HUM_UV))

    med_rms = float(np.median(eeg_rms))
    if med_rms < T.DEAD_CHANNEL_UV:
        return ok, "DEAD", "median EEG rms %.1f < %.0f uV: never carried EEG" % (
            med_rms, T.DEAD_CHANNEL_UV)
    if not_open.mean() < 0.5:
        # Name the channel that is open. Until 2026-10-02 this printed the EEG's 60 Hz
        # whatever tripped, so an open EMG beside a good EEG read "60 Hz 16 uV vs 150 uV
        # limit: not connected" -- a reason that contradicts itself.
        parts = ["%s 60 Hz %.0f uV" % (name, float(np.median(mn)))
                 for name, mn in (("EEG", eeg_mains), ("EMG", emg_mains))
                 if np.mean(mn >= T.OPEN_UV) >= 0.5]
        if not parts:       # each open in under half the epochs, but rarely both fine
            parts = ["EEG %.0f / EMG %.0f uV 60 Hz, open in alternating epochs"
                     % (float(np.median(eeg_mains)), float(np.median(emg_mains)))]
        return ok, "OPEN", "%s vs %.0f uV limit: not connected" % (
            ", ".join(parts), T.OPEN_UV)
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

    ntv_to_row = dict((int(n), row) for row, n in enumerate(ntv))
    animals = layout(sites, ntv)
    if not animals:
        sys.exit("no EEG/EMG pairs in the selection - select /1 /2 /33 /34 per port")

    m = measure(X, fs)
    mins = m["nep"] * T.EPOCH_S_QC / 60.0
    print("\n%d channels, %.1f min, %d QC epochs of %d s, fs %g Hz"
          % (X.shape[0], mins, m["nep"], T.EPOCH_S_QC, fs))
    print("thresholds from core/qc_thresholds.py: open %.0f, dead %.0f, flat %.0f, "
          "rail %.0f, floor %.0f uV"
          % (T.OPEN_UV, T.DEAD_CHANNEL_UV, T.FLAT_UV, T.RAIL_UV_EFF, T.FLOOR_MIN_HUM_UV))

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

    print("\n%-7s %9s %9s %9s %9s %8s %7s  %-11s %s"
          % ("animal", "EEG rms", "EMG rms", "EEG 60Hz", "EMG 60Hz", "floor",
             "pass%", "verdict", "reason"))
    print("-" * 108)
    disputed = []
    for a in animals:
        eeg_rms = m["rms_eeg"][a["eeg"]]
        emg_rms = m["rms_emg"][a["emg"]]
        eeg_mn = m["mains_eeg"][a["eeg"]]
        emg_mn = m["mains_emg"][a["emg"]]
        floor, n_sites = chip_floor(X, fs, ntv_to_row, int(a["ntv"]))
        ok, tag, why = verdict(eeg_mn, emg_mn, eeg_rms, m["clip"][a["eeg"]], floor)
        if T.FLOOR_MIN_HUM_UV <= floor < 2000:
            disputed.append((a["name"], floor))
        print("%-7s %9.1f %9.1f %9.1f %9.1f %8s %6.0f%%  %-11s %s"
              % (a["name"], np.median(eeg_rms), np.median(emg_rms),
                 np.median(eeg_mn), np.median(emg_mn),
                 "-" if np.isnan(floor) else "%.0f" % floor,
                 100 * ok.mean(), tag, why))

    if disputed:
        print("\n⚠️  floor between %.0f and 2000 uV on %s. FLOOR_MIN_HUM_UV is %.0f.\n"
              "   A 2000 uV line was proposed (weak-chip-ground-hides-as-electrode-failure)\n"
              "   but the 2026-10-01 overnight contradicts it: after the rig geometry changed,\n"
              "   chips under 2000 uV (gate scale) carried EEG. The floor scale depends on the wiring;\n"
              "   see 05-experiments/completed/2026-10-02-noise-series-method-audit.md (C1)."
              % (T.FLOOR_MIN_HUM_UV,
                 ", ".join("%s %.0f uV" % d for d in disputed), T.FLOOR_MIN_HUM_UV))

    if any(np.isnan(chip_floor(X, fs, ntv_to_row, int(a["ntv"]))[0]) for a in animals):
        print("\n🛑 NO GROUNDING CHECK WAS POSSIBLE. The chip's wire-free inputs are its "
              "only\n   in-file control, and they are not in the montage, so a floating "
              "chip reads\n   completely normal here -- that is how A2, C1 and D1 passed "
              "this screen as CLEAN\n   on 2026-09-17 while their floors were 454, 7 and "
              "5 uV.\n   To check it: select ALL channels in Allego (System -> Signals), "
              "screen, then\n   re-select the montage. Never during a recording. "
              "Otherwise rely on stage 1.")

    print("\nA clean screen is not a promise: contact state flips within minutes.")


if __name__ == "__main__":
    main()

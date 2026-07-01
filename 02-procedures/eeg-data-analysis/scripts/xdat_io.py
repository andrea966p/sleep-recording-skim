"""
xdat_io.py  --  Read NeuroNexus Allego XDAT recordings (numpy only).

An Allego recording is a 3-file set sharing one base name:
    <base>_data.xdat        float32, already in microvolts (uV), interleaved
                            sample-major: [s0c0 s0c1 ... s0cN  s1c0 s1c1 ...]
    <base>_timestamp.xdat   int64 sample indices (usually 0..N-1)
    <base>.xdat.json        metadata under ["status"]: samp_freq, num_smpl,
                            signals.total / .pri / .aux / .din / .dout, start_time

Signal order in each sample = [ 32 pri (amplifier) , aux , din , dout ] = "total".
With a passthrough_32 map, primary channel index == C3410 pad == native index.

This module has NO heavy deps (numpy + json) so it loads fast and never breaks
on a scipy/matplotlib mismatch. Use it everywhere.

Usage (as a library):
    from xdat_io import load_xdat, CHANNEL_MAPS, bipolar
    rec = load_xdat("/home/skimlab/radix/data/allego_1__uid0629-12-05-09")
    eeg = bipolar(rec.data, 0, 1)        # left frontal - left parietal
"""
import json
import os
from types import SimpleNamespace
import numpy as np

# native-channel (== pad, passthrough) -> human label, per rig config.
# See vault: grounding-reference-noise-concepts.md (single-mouse definitive map)
# and signal-mapping-guide.md (2mice32).
CHANNEL_MAPS = {
    # single-mouse 8-pin slip-ring rig (2026-06 onward)
    "single_mouse": {
        0: "EEG_F_L",   # left frontal  (+)
        1: "EEG_P_L",   # left parietal (-)   -> EEG bipolar = 0 - 1
        2: "EMG_L",     # neck EMG left  (+)
        3: "EMG_R",     # neck EMG right (-)  -> EMG bipolar = 2 - 3
        4: "dura_FR",   # right-frontal dura (spare / re-reference)
        6: "copper",    # cut cable shield = environmental-noise reference
        # native 5 = purple = nothing (deselect); 7-31 = unwired
    },
    # 2-mice-per-headstage map (validated 2026-07-01: impedance sweep good on
    # all 8 electrode sites; grid rows 1 & 3 = M1 / M2, natives 0-3 / 8-11).
    # M1 = chip-1 natives 0-3, M2 = chip-1 natives 8-11 (both share one GND bus).
    # Each mouse's green ground -> brass bus -> C3410 GND (shared ground).
    "2mice32": {
        0: "M1_EEG_F", 1: "M1_EEG_P", 2: "M1_EMG_L", 3: "M1_EMG_R",
        8: "M2_EEG_F", 9: "M2_EEG_P", 10: "M2_EMG_L", 11: "M2_EMG_R",
        12: "M2_EEG_FR",   # brown = right-frontal dura (spare / re-reference)
    },
}

# default bipolar derivations per config: (label, plus_native, minus_native)
BIPOLAR_DERIVATIONS = {
    "single_mouse": [("EEG_bip", 0, 1), ("EMG_bip", 2, 3)],
    "2mice32": [("M1_EEG_bip", 0, 1), ("M1_EMG_bip", 2, 3),
                ("M2_EEG_bip", 8, 9), ("M2_EMG_bip", 10, 11)],
}


def load_xdat(base):
    """Load an XDAT recording. `base` is the path WITHOUT the _data.xdat suffix.
    Returns a SimpleNamespace with:
        fs (int), n_samples (int), n_total (int), n_pri (int),
        data  -> float32 array, shape (n_total, n_samples), channel-first, uV
        time  -> float64 seconds, shape (n_samples,)
        start_time (str ISO), meta (dict)
    """
    base = base[:-10] if base.endswith("_data.xdat") else base
    base = base[:-9] if base.endswith(".xdat.json") else base
    meta = json.load(open(base + ".xdat.json"))
    st = meta["status"]
    fs = int(st["samp_freq"])
    n = int(st["num_smpl"])
    tot = int(st["signals"]["total"])
    flat = np.fromfile(base + "_data.xdat", dtype="<f4")
    if flat.size != n * tot:
        raise ValueError(f"size mismatch: {flat.size} floats != num_smpl*total ({n}*{tot})")
    data = flat.reshape(n, tot).T          # (channel, sample)
    return SimpleNamespace(
        base=base, fs=fs, n_samples=n, n_total=tot,
        n_pri=int(st["signals"]["pri"]),
        data=data,
        time=np.arange(n, dtype=np.float64) / fs,
        start_time=st.get("start_time"),
        meta=meta,
    )


def bipolar(data, plus_native, minus_native):
    """Bipolar derivation = plus channel - minus channel (uV)."""
    return data[plus_native].astype(np.float64) - data[minus_native].astype(np.float64)


def labeled_channels(rec, config="single_mouse", include_bipolar=True):
    """Yield (label, signal_uV) for the wired channels of a config, in order.
    Raw single-ended channels first, then bipolar derivations.
    """
    out = []
    for ntv, lab in CHANNEL_MAPS[config].items():
        out.append((f"{lab}_n{ntv}", rec.data[ntv].astype(np.float64)))
    if include_bipolar:
        for lab, p, m in BIPOLAR_DERIVATIONS[config]:
            out.append((lab, bipolar(rec.data, p, m)))
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python xdat_io.py <recording_base_path>")
        sys.exit(1)
    rec = load_xdat(sys.argv[1])
    print(f"fs={rec.fs} Hz  samples={rec.n_samples} ({rec.n_samples/rec.fs/60:.1f} min)")
    print(f"total signals={rec.n_total}  pri={rec.n_pri}  start={rec.start_time}")
    print("wired channel RMS (uV):")
    for lab, x in labeled_channels(rec):
        print(f"  {lab:14s} RMS={x.std():8.1f}  pkpk={x.max()-x.min():9.1f}")

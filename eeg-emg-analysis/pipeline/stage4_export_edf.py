#!/usr/bin/env python3
"""STAGE 4 -- export a per-mouse file to EDF+ so a HUMAN can score it.

This is the hand-off step. Everything before this is machine QC; this produces
the file a scorer opens in EDFbrowser / SleepSign / an equivalent viewer.

No third-party dependency. EDF is a simple, fully specified format and the
production machine should not grow a package just to write one.
(The archived `xdat_to_edf.py` needed pyedflib AND computed bipolar derivations,
which is the retracted pre-2026-08-01 model -- do not resurrect it.)

Design decisions, and why:

  * **Two signals per file: EEG and EMG.** That is the whole montage. They are
    already bipolar, so nothing is derived, subtracted or re-referenced.
  * **Physical range is fixed at the true ADC rail, +/- 6389.6 uV**, so the EDF
    digital step equals the hardware LSB of 0.195 uV exactly and no requantising
    error is introduced.
  * **The automatic hypnogram is NOT written into the file.** A scorer who sees
    our labels cannot un-see them, and this project's whole problem has been
    believing its own automatic output. Score blind, then compare against
    `*_hypnogram.csv` afterwards.
  * **Excluded epochs are NOT deleted.** Cutting them would splice
    discontinuous time into a continuous file and destroy the scorer's sense of
    bout length -- the exact class of error as the persistence bug. Bad epochs
    stay in place and are listed in the companion `.txt`.

Usage
    python3 stage4_export_edf.py <day_dir_or_npz> [...]
"""
import argparse
import glob
import json
import os
import sys
import datetime as dt

import numpy as np

from core import qc_thresholds as T
from pipeline import pipeline_common as P

PHYS_MAX = 6389.56
# The true ADC full scale is 6389.565 uV. EDF header fields are 8 ASCII chars,
# so "-6389.565" does not fit and gets truncated to "-6389.56" while the positive
# field keeps all its digits -- an asymmetric range, and every sample comes back
# biased by a fraction of an LSB. Rounding to 6389.56 makes both fields fit
# exactly and keeps the step at 0.195 uV.
DIG_MIN, DIG_MAX = -32768, 32767
REC_SEC = 1                          # one-second data records
ANNOT_WORDS = 60                     # int16 words reserved for the EDF+ TAL


def _fld(text, n):
    """ASCII field, left justified, space padded, hard truncated to n bytes."""
    b = str(text).encode("ascii", "replace")[:n]
    return b + b" " * (n - len(b))


def write_edf(path, sigs, fs, start, patient, recording):
    """Write a minimal, compliant EDF+C file.

    sigs: list of (label, transducer, dimension, prefilter, float array uV)
    """
    n_rec = min(len(s[4]) for s in sigs) // (fs * REC_SEC)
    ns = len(sigs) + 1                                   # + annotations signal
    hdr = bytearray()
    hdr += _fld(0, 8)
    hdr += _fld(patient, 80)
    hdr += _fld(recording, 80)
    hdr += _fld(start.strftime("%d.%m.%y"), 8)
    hdr += _fld(start.strftime("%H.%M.%S"), 8)
    hdr += _fld(256 * (ns + 1), 8)
    hdr += _fld("EDF+C", 44)
    hdr += _fld(n_rec, 8)
    hdr += _fld(REC_SEC, 8)
    hdr += _fld(ns, 4)

    labels = [s[0] for s in sigs] + ["EDF Annotations"]
    trans = [s[1] for s in sigs] + [""]
    dims = [s[2] for s in sigs] + [""]
    pmin = [-PHYS_MAX] * len(sigs) + [-1]
    pmax = [PHYS_MAX] * len(sigs) + [1]
    dmin = [DIG_MIN] * ns
    dmax = [DIG_MAX] * ns
    pref = [s[3] for s in sigs] + [""]
    nsamp = [fs * REC_SEC] * len(sigs) + [ANNOT_WORDS]

    for arr, width in ((labels, 16), (trans, 80), (dims, 8), (pmin, 8),
                       (pmax, 8), (dmin, 8), (dmax, 8), (pref, 80), (nsamp, 8)):
        for v in arr:
            hdr += _fld(v, width)
    hdr += b" " * (32 * ns)

    scale = DIG_MAX / PHYS_MAX
    data = [np.clip(np.rint(np.asarray(s[4], dtype=np.float64) * scale),
                    DIG_MIN, DIG_MAX).astype("<i2") for s in sigs]

    with open(path, "wb") as fh:
        fh.write(bytes(hdr))
        for r in range(n_rec):
            a, b = r * fs * REC_SEC, (r + 1) * fs * REC_SEC
            for d in data:
                fh.write(d[a:b].tobytes())
            tal = f"+{r * REC_SEC}\x14\x14\x00".encode("ascii")
            fh.write(tal + b"\x00" * (ANNOT_WORDS * 2 - len(tal)))
    return n_rec


def export(npz_path):
    z = np.load(npz_path, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    fs = int(z["fs"])
    start = dt.datetime.fromisoformat(meta["start_local"]).replace(tzinfo=None)

    pre_eeg = f"HP:{T.FILT_EEG[0]}Hz LP:{T.FILT_EEG[1]}Hz"
    pre_emg = f"HP:{T.FILT_EMG[0]}Hz LP:{T.FILT_EMG[1]}Hz"
    sigs = [("EEG", "bipolar frontal-L/parietal-L dura pin", "uV", pre_eeg, z["eeg"]),
            ("EMG", "bipolar neck L/R muscle wire", "uV", pre_emg, z["emg"])]

    out = npz_path[:-4] + ".edf"
    n_rec = write_edf(out, sigs, fs, start,
                      patient=f"X X X {meta['name']}_port{meta['port']}_slot{meta['slot']}",
                      recording=f"Startdate {start.strftime('%d-%b-%Y').upper()} "
                                f"X X {meta['recording']}")

    # companion note: what the scorer must know, in plain language
    ok = z["epoch_ok"]
    blocks = [tuple(map(int, b)) for b in z["blocks"]]
    lines = [
        f"{os.path.basename(out)}",
        "=" * 70,
        f"animal          {meta['name']}  (port {meta['port']}, slot {meta['slot']})",
        f"recording       {meta['recording']}",
        f"start (local)   {meta['start_local']}",
        f"duration        {meta['hours']:.2f} h at {fs} Hz",
        f"light cycle     on {T.LIGHTS_ON_HOUR:02d}:00, off {T.LIGHTS_OFF_HOUR:02d}:00 KST"
        f"  (ZT0 = {T.LIGHTS_ON_HOUR:02d}:00)",
        f"stage 1 QC      {meta['qc']['verdict']} -- {meta['qc']['reason']}",
        "",
        "SIGNALS",
        "  EEG = left frontal-parietal, ALREADY BIPOLAR (chip did the subtraction)",
        "  EMG = neck left-right, ALREADY BIPOLAR",
        "  Do not re-reference or subtract these from each other.",
        "",
        "SCORE ONLY INSIDE THESE WINDOWS",
        f"  Outside them the electrode is not in contact and the trace is mains hum,",
        f"  not brain. {100*float(ok.mean()):.1f}% of epochs pass QC.",
        "",
        f"  {'from (h:mm:ss)':>16}  {'to (h:mm:ss)':>16}  {'minutes':>9}",
    ]
    fmt = lambda s: str(dt.timedelta(seconds=int(s)))
    for a, b in blocks:
        t0, t1 = a * T.EPOCH_S, b * T.EPOCH_S
        lines.append(f"  {fmt(t0):>16}  {fmt(t1):>16}  {(t1-t0)/60:>9.1f}")
    if not blocks:
        lines.append("  (none -- nothing in this file is scoreable)")
    lines += [
        "",
        "NOT INCLUDED ON PURPOSE",
        "  The automatic sleep staging is deliberately NOT written into this EDF.",
        "  Score blind first, then compare with the companion *_hypnogram.csv.",
        "  Excluded epochs are left in place rather than cut out, so that bout",
        "  lengths and the time axis stay honest.",
        "",
        f"records written  {n_rec} x {REC_SEC}s",
        f"physical range   +/- {PHYS_MAX} uV (the true ADC rail; step = {T.LSB_UV} uV)",
    ]
    open(npz_path[:-4] + "_SCORER-README.txt", "w").write("\n".join(lines) + "\n")
    return out, n_rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="day folder(s) or .npz file(s)")
    a = ap.parse_args()
    targets = []
    for p in a.paths:
        targets += (sorted(glob.glob(os.path.join(p, "port*.npz")))
                    if os.path.isdir(p) else [p])
    if not targets:
        raise SystemExit("no per-mouse .npz found -- run stage 2 first")
    for t in targets:
        out, n = export(t)
        print(f"  wrote {os.path.basename(out)}  ({n} s, "
              f"{os.path.getsize(out)/1e6:.0f} MB) + _SCORER-README.txt")


if __name__ == "__main__":
    main()

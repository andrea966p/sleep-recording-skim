"""Before / after the electrician's work of 2026-10-07 (isolated-earth socket + XDAQ bonded to the rack), same 4 mice.

usage: python3 qc/electrician_before_after_2026_10_07.py BEFORE_BASE T0 DUR AFTER_BASE T0 DUR OUT.png [BEFORE_LABEL AFTER_LABEL]

One row per mouse (A1, A2, B1, B2):
  EEG spectrum | EMG spectrum | 2 s of raw EMG | spectrum of the mouse's chip floor (median over its 14 wire-free inputs)
Spectra are Welch over 4 s segments of the whole window, with nothing removed (rail-touching segments included),
so a railing open input shows its clipping harmonics as they are. Default comparison in the vault: the 10-02
light-phase run at 14:55 (same clock time, ZT6) against the first block after the work.
"""
import sys
import numpy as np, scipy.signal as sg
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "/home/skimlab/sleep-recording-skim/eeg-emg-analysis")
from core.criteria import open_xdat
from core import qc_thresholds as T

BEFORE_C, AFTER_C = "#2a78d6", "#eb6834"       # categorical slots 1 and 2 (validated, light surface)
MICE = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}

def load(base, t0, dur):
    X, labels, fs, n = open_xdat(base)
    li = {l: i for i, l in enumerate(labels)}
    a, b = int(t0 * fs), min(n, int((t0 + dur) * fs))
    want = []
    for p, s in MICE.values():
        want += [f"{p}/{s}", f"{p}/{s+1}"] + [f"{p}/{q}" for q in range(s + 2, s + 16)]
    D = np.asarray(X[a:b, [li[w] for w in want]], dtype=np.float64).T
    return dict(zip(want, D)), fs

def psd(x, fs):
    f, P = sg.welch(x - x.mean(), fs=fs, nperseg=4 * fs)
    return f, P

def main(argv):
    bb, bt, bd, ab, at, ad, out = argv[:7]
    lab_b, lab_a = (argv[7], argv[8]) if len(argv) > 8 else ("before", "after")
    B, fs = load(bb, float(bt), float(bd)); A, fs2 = load(ab, float(at), float(ad))
    assert fs == fs2
    fig, ax = plt.subplots(4, 4, figsize=(17, 13), constrained_layout=True)
    for r, (mouse, (p, s)) in enumerate(MICE.items()):
        eeg, emg = f"{p}/{s}", f"{p}/{s+1}"
        floors = [f"{p}/{q}" for q in range(s + 2, s + 16)]
        for c, title, chans in ((0, f"{mouse} EEG ({eeg})", [eeg]), (1, f"{mouse} EMG ({emg})", [emg]),
                                (3, f"{mouse} chip floor, median of 14 wire-free inputs", floors)):
            a_ = ax[r, c]
            for data, col, lab in ((B, BEFORE_C, lab_b), (A, AFTER_C, lab_a)):
                Ps = [psd(data[ch], fs) for ch in chans]
                f = Ps[0][0]; P = np.median([q for _, q in Ps], axis=0)
                m = (f >= 0.5) & (f <= 450)
                a_.loglog(f[m], np.sqrt(P[m]), color=col, lw=1.2, label=lab)
            a_.set_title(title, fontsize=10); a_.grid(True, which="major", color="#e4e3df", lw=0.6)
            a_.set_xlabel("Hz", fontsize=9); a_.set_ylabel("µV/√Hz", fontsize=9)
            for v in (60, 120, 180):
                a_.axvline(v, color="#a8a7a2", lw=0.6, ls=":")
        # raw EMG, 2 s from 60 s into each window
        a_ = ax[r, 2]
        t = np.arange(2 * fs) / fs
        for data, col, lab in ((B, BEFORE_C, lab_b), (A, AFTER_C, lab_a)):
            x = data[emg][60 * fs: 62 * fs]
            a_.plot(t, x - np.median(x), color=col, lw=0.8, label=lab)
        a_.axhline(T.RAIL_UV, color="#a8a7a2", lw=0.6, ls="--"); a_.axhline(-T.RAIL_UV, color="#a8a7a2", lw=0.6, ls="--")
        lim = max(np.abs(B[emg][60 * fs: 62 * fs] - np.median(B[emg])).max(),
                  np.abs(A[emg][60 * fs: 62 * fs] - np.median(A[emg])).max()) * 1.1
        a_.set_ylim(-min(lim, 7000), min(lim, 7000))
        a_.set_title(f"{mouse} EMG raw, 2 s (dashed = amplifier rail ±{T.RAIL_UV/1000:.1f} mV)", fontsize=10)
        a_.set_xlabel("s", fontsize=9); a_.set_ylabel("µV", fontsize=9); a_.grid(True, color="#e4e3df", lw=0.6)
    ax[0, 0].legend(loc="lower left", fontsize=9, frameon=False)
    fig.suptitle(f"Same 4 mice, {lab_b} (blue) vs {lab_a} (orange). Dotted lines: 60, 120, 180 Hz", fontsize=12)
    fig.savefig(out, dpi=110)
    print("wrote", out)

if __name__ == "__main__":
    main(sys.argv[1:])

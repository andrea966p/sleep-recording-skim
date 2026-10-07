"""Mains share of the stager's EMG measure, per mouse, in short recording windows.

usage: python3 qc/emg_mains_share_windows.py LABEL=BASE:T0:DUR [LABEL=BASE:T0:DUR ...]

Stage 3 calls WAKE from the log rms of the EMG in 4 s epochs, band 10-124 Hz (FILT_EMG 10-300 Hz on the 250 Hz
stage-2 data), with no mains removal (audit C3). Here, per 4 s epoch at the native rate: rms of the EMG band-passed
10-124 Hz, raw and with 60 + 120 Hz notched (Q 30, as in the validated notch test). Mains share = 1 - notched^2 / raw^2.
Reported per mouse: the median share, and the raw and notched epoch rms at p10 (quiet, mostly sleep) and p90 (active).
Epochs touching the rail are dropped (open inputs rail; the share is meaningless there).
"""
import sys
import numpy as np, scipy.signal as sg
sys.path.insert(0, "/home/skimlab/sleep-recording-skim/eeg-emg-analysis")
from core.criteria import open_xdat
from core import qc_thresholds as T

MICE = {"A1": "A/2", "A2": "A/34", "B1": "B/2", "B2": "B/34"}

def run(label, spec):
    base, t0, dur = spec.rsplit(":", 2)
    X, labels, fs, n = open_xdat(base); li = {l: i for i, l in enumerate(labels)}
    a, b = int(float(t0) * fs), min(n, int((float(t0) + float(dur)) * fs))
    D = np.asarray(X[a:b, [li[c] for c in MICE.values()]], dtype=np.float64).T
    bp = sg.butter(4, [10, 124], btype="band", fs=fs, output="sos")
    ep = 4 * fs; ne = D.shape[1] // ep
    print(f"{label}: {base.split('/')[-1]} {float(t0):.0f}+{(b - a) / fs:.0f} s, {ne} epochs")
    for (mouse, ch), x in zip(MICE.items(), D):
        y = sg.sosfiltfilt(bp, x)
        z = y.copy()
        for f0 in (60.0, 120.0):
            bq, aq = sg.iirnotch(f0, 30, fs); z = sg.filtfilt(bq, aq, z)
        E = x[: ne * ep].reshape(ne, ep); keep = np.abs(E).max(1) < T.RAIL_UV_EFF
        r = y[: ne * ep].reshape(ne, ep).std(1)[keep]; q = z[: ne * ep].reshape(ne, ep).std(1)[keep]
        if keep.sum() < 5:
            print(f"   {mouse} {ch:5s} {keep.sum()} of {ne} epochs off the rail: not judged"); continue
        share = 1 - q ** 2 / r ** 2
        p = lambda v, k: np.percentile(v, k)
        print(f"   {mouse} {ch:5s} mains share median {np.median(share) * 100:5.1f} %  | rms raw p10 {p(r, 10):7.1f} p90 {p(r, 90):7.1f}"
              f"  | notched p10 {p(q, 10):7.1f} p90 {p(q, 90):7.1f} µV  | raw p90/p10 {p(r, 90) / p(r, 10):5.2f}"
              f"  notched p90/p10 {p(q, 90) / p(q, 10):5.2f}  ({keep.sum()}/{ne} epochs off the rail)")

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        lab, spec = arg.split("=", 1); run(lab, spec)

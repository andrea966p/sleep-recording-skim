"""How often would a wireless headstage with a fixed input range flat-top our signals?

Reads the console's unipolar 1 kHz CSVs (columns EMG_L,LFP_TGT,LFP_REF,EMG_R,EEG_P,EEG_F, uV) and reports,
per derived signal, |x| percentiles and the share of samples / 1-s windows beyond each candidate range.
465 uV = Pinnacle 8274-HR fixed range (brochure 2025). EEG high-pass 0.5 Hz and EMG high-pass 10 Hz mimic
Pinnacle's hardware filters. See vault 06-references/2026-10-16-pinnacle-wireless-16-mice-evaluation.md.

usage: /usr/bin/python3 -I wireless_range_clip_check.py <csv> [<csv> ...]
ponytail: whole-file stats, no state split; pass REM-only CSV slices to test P-wave clipping."""
import sys
import numpy as np
from scipy import signal

FS = 1000.0
RANGES_UV = [465, 930, 1250, 2500]


def load(path):
    cols = open(path).readline().strip().split(",")[3:]
    x = np.loadtxt(path, delimiter=",", skiprows=1, usecols=range(3, 3 + len(cols)), dtype=np.float32)
    return cols, x.T


def hp(x, fc=0.5):
    sos = signal.butter(2, fc, "highpass", fs=FS, output="sos")
    return signal.sosfiltfilt(sos, x)


def notch_mains(x):
    for f0 in (60, 120, 180, 240, 300, 360, 420):
        if f0 < FS / 2:
            b, a = signal.iirnotch(f0, 30, FS)
            x = signal.filtfilt(b, a, x)
    return x


def mains_uv(x):
    f, p = signal.welch(x, FS, nperseg=4096)
    band = (f > 59) & (f < 61)
    return np.sqrt(np.trapezoid(p[band], f[band])) * 2 * np.sqrt(2)  # p2p of the 60 Hz sinusoid


def row(name, x):
    a = np.abs(x)
    p = np.percentile(a, [50, 99, 99.9, 99.99])
    over = [100 * np.mean(a > r) for r in RANGES_UV]
    # 1 s windows containing any sample beyond 465 uV
    w = a[: len(a) // 1000 * 1000].reshape(-1, 1000).max(1)
    win = 100 * np.mean(w > 465)
    print(f"  {name:22s} |x| p50 {p[0]:7.1f}  p99 {p[1]:7.1f}  p99.9 {p[2]:7.1f}  p99.99 {p[3]:7.1f}  max {a.max():8.1f} | "
          + "  ".join(f">{r}:{o:6.3f}%" for r, o in zip(RANGES_UV, over)) + f" | 1s-win>465: {win:5.1f}%")


for path in sys.argv[1:]:
    cols, X = load(path)
    d = dict(zip(cols, X))
    print(f"\n{path.split('/')[-1]}  n={X.shape[1]}  ({X.shape[1] / FS / 60:.1f} min)")
    print("  60 Hz p2p uV: " + "  ".join(f"{c}={mains_uv(hp(d[c])):.0f}" for c in cols))
    derived = {
        "LFP_TGT (single-end)": d["LFP_TGT"],
        "LFP_TGT-LFP_REF": d["LFP_TGT"] - d["LFP_REF"],
        "EEG_F (single-end)": d["EEG_F"],
        "EEG_P (single-end)": d["EEG_P"],
        "EEG_F-EEG_P": d["EEG_F"] - d["EEG_P"],
        "EMG_L-EMG_R": d["EMG_L"] - d["EMG_R"],
    }
    emg = d["EMG_L"].astype(np.float64) - d["EMG_R"]
    print(" [Pinnacle EMG high-pass 10 Hz]")
    row("EMG_L-EMG_R HP10", hp(emg, 10))
    for tag, fn in (("raw + HP0.5", hp), ("HP0.5 + mains notch", lambda v: notch_mains(hp(v)))):
        print(f" [{tag}]")
        for k, v in derived.items():
            row(k, fn(v.astype(np.float64)))

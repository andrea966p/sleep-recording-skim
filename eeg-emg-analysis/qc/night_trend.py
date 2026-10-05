"""Live-file trend: 60 s every 15 min (mains, broadband, per chip floor + animals), plus a look at given event times.
60 Hz / 120 Hz numbers are the QC gate's line PEAK (median of 10 s Hann epochs), comparable with FLOOR_MIN_HUM_UV (2026-10-02).
Light: reads ~32 MB per window, page cache dropped. usage: night_trend.py BASE [event_s ...]"""
import os, sys, json, numpy as np, scipy.signal as sg
base = sys.argv[1]; ev = [float(x) for x in sys.argv[2:]]
meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; nsamp = os.path.getsize(path) // (nch * 4)
fd = os.open(path, os.O_RDONLY)
def read(t0, dur):
    a = int(t0 * fs); n = int(dur * fs)
    x = np.fromfile(path, dtype=np.float32, count=n * nch, offset=a * nch * 4).reshape(n, nch)
    os.posix_fadvise(fd, a * nch * 4, n * nch * 4, os.POSIX_FADV_DONTNEED); return x.astype(np.float64).T
chips = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}
def bp(lo, hi): return sg.butter(4, [lo, hi], btype="band", fs=fs, output="sos")
assert fs % 20 == 0 and fs >= 500, f"fs={fs}: comb/epochs assume a 1 kHz-class rate"
EPQ = 10 * fs; WIN = np.hanning(EPQ); FQ = np.fft.rfftfreq(EPQ, 1 / fs)
def line_peak(Xr, f0):
    """QC gate's estimator: per 10 s epoch the Hann |rfft| peak within f0+-1 Hz scaled to line amplitude, median over epochs."""
    n = Xr.shape[-1] // EPQ; B = Xr[..., :n * EPQ].reshape(*Xr.shape[:-1], n, EPQ); B = B - B.mean(-1, keepdims=True)
    P = np.abs(np.fft.rfft(B * WIN, axis=-1)) / (WIN.sum() / 2); m = (FQ >= f0 - 1) & (FQ <= f0 + 1)
    return np.median(P[..., m].max(-1), axis=-1)
def comb(x): return x[:, fs // 20:] - x[:, :-(fs // 20)]   # 3-cycle (50 ms) comb: kills 60 Hz + all harmonics, no ringing
print("clock  | " + " | ".join(f"{c}: fl60 fl120 flBB | EEG60 EEGrms EMG60 EMGrms" for c in chips))
import datetime as dt
st = os.path.basename(base).split("uid")[1]; t_start = dt.datetime(2026, int(st[:2]), int(st[2:4]), *map(int, st[5:].split("-")))
for t0 in np.arange(30, nsamp / fs - 70, 900):
    X = read(t0, 60); row = []
    for c, (p, b) in chips.items():
        fl = [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)]; e, g = ix[f"{p}/{b}"], ix[f"{p}/{b+1}"]
        f60 = np.median(line_peak(X[fl], 60)); f120 = np.median(line_peak(X[fl], 120))     # gate scale (line PEAK)
        fbb = np.median(sg.sosfiltfilt(bp(1, 45), comb(X[fl]), axis=1).std(1)) / np.sqrt(2)
        e60 = float(line_peak(X[e], 60)); g60 = float(line_peak(X[g], 60))
        erms = sg.sosfiltfilt(bp(1, 30), X[e]).std(); grms = sg.sosfiltfilt(bp(30, 200), comb(X[g][None])[0]).std() / np.sqrt(2)
        row.append(f"{f60:5.0f} {f120:4.0f} {fbb:5.1f} | {e60:5.1f} {erms:5.1f} {g60:6.0f} {grms:6.1f}")
    print((t_start + dt.timedelta(seconds=float(t0))).strftime("%H:%M") + "  | " + " | ".join(row))
for t in ev:
    X = read(t - 2, 4); Y = sg.sosfiltfilt(bp(1, 450), comb(X), axis=1)
    m = Y.shape[1] // 2; w = slice(m - 300, m + 300); out = []
    for c, (p, b) in chips.items():
        fl = [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)]; e, g = ix[f"{p}/{b}"], ix[f"{p}/{b+1}"]
        pk = lambda r: np.abs(Y[r, w] - np.median(Y[r], -1, keepdims=True) if np.ndim(r) else Y[r, w] - np.median(Y[r])).max(-1)
        base_fl = np.median(np.abs(Y[fl, :m - 400]).max(1))
        out.append(f"{c}: floor pk {np.median(pk(fl)):6.0f} (pre-event max {base_fl:5.0f})  EEG {pk(e):5.0f}  EMG {pk(g):6.0f}")
    print(f"\nevent t={t:.1f}s ({(t_start + dt.timedelta(seconds=t)).strftime('%H:%M:%S')}):  " + "\n   ".join(out))

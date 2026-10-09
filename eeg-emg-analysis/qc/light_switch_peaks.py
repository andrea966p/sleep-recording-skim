"""Size of the room-light switching spike on every chip and mouse, in µV, so runs can be compared directly.

usage: python3 qc/light_switch_peaks.py BASE "YYYY-MM-DD HH:MM:SS[.s]" [...]
For each given clock time (the expected switch, +-90 s searched): the signal is the 50 ms comb (x[t] - x[t-50 ms], which
cancels 60 Hz and every harmonic without ringing) band-passed 1-450 Hz, as in qc/allchip_scan_file.py. A chip's floor
trace is the median over its 14 wire-free inputs of |y|, taken as the max per 100 ms window (the window is clipped at the file ends). The event is the 100 ms
window where the sum over chips of floor/baseline is largest; reported per chip: peak floor µV, baseline (median of
the 100 ms maxima over the 180 s, i.e. the ordinary background) and their ratio; per mouse: EEG and EMG peak |y| within
+-0.3 s of the event, and their own baselines. Light reads (~47 MB per event), page cache dropped.
"""
import os, sys, json, datetime as dt
import numpy as np, scipy.signal as sg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import noise_mice_markers_2026_10_02 as MK

MICE = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}
RAW = os.path.expanduser("~/radix/data")


def main(base, times):
    meta = json.load(open(os.path.join(RAW, base + ".xdat.json"))); bm = meta["sapiens_base"]["biointerface_map"]
    lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab); ix = {l: i for i, l in enumerate(lab)}
    t0, fs, n, _ = MK.file_origin(base); fs = int(fs)
    path = os.path.join(RAW, base + "_data.xdat"); fd = os.open(path, os.O_RDONLY)
    sos = sg.butter(4, [1, 450], btype="band", fs=fs, output="sos"); lag = fs // 20; w = fs // 10
    print(f"{base}  start {t0:%Y-%m-%d %H:%M:%S.%f}"[:-3])
    for tc in times:
        tt = MK.clock(tc); c = (tt - t0).total_seconds()
        a = max(0, int((c - 90) * fs)); m = min(n - 5 * fs, int((c + 90) * fs)) - a    # clipped to the file
        if m < 60 * fs or not (a / fs < c < (a + m) / fs):
            print(f"  {tc}: outside the file"); continue
        x = np.fromfile(path, dtype=np.float32, count=m * nch, offset=a * nch * 4).reshape(m, nch).T.astype(np.float64)
        os.posix_fadvise(fd, a * nch * 4, m * nch * 4, os.POSIX_FADV_DONTNEED)
        y = sg.sosfiltfilt(sos, x[:, lag:] - x[:, :-lag], axis=1); nw = y.shape[1] // w
        Y = np.abs(y[:, :nw * w]).reshape(nch, nw, w).max(2)              # 100 ms maxima per channel
        fl = {k: np.median(Y[[ix[f"{p}/{q}"] for q in range(s + 2, s + 16)]], 0) for k, (p, s) in MICE.items()}
        base_fl = {k: np.median(v) for k, v in fl.items()}
        score = sum(v / base_fl[k] for k, v in fl.items()); e = int(np.argmax(score))
        te = t0 + dt.timedelta(seconds=(a + lag + (e + .5) * w) / fs)
        print(f"  {tc} -> event {te:%H:%M:%S.%f}"[:-5] + f"  (score {score[e]:.0f}, background score {np.median(score):.1f})")
        for k, (p, s) in MICE.items():
            sl = slice(max(0, e - 3), e + 4)
            eeg, emg = Y[ix[f"{p}/{s}"]], Y[ix[f"{p}/{s + 1}"]]
            print(f"     {k}: floor {fl[k][e]:8.1f} µV (bg {base_fl[k]:6.1f}, x{fl[k][e] / base_fl[k]:6.1f}) | "
                  f"EEG {eeg[sl].max():8.1f} (bg {np.median(eeg):6.1f}) | EMG {emg[sl].max():8.1f} (bg {np.median(emg):6.1f})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])

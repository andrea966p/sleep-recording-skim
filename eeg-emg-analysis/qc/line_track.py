"""Track given narrow lines through a whole (even live) .xdat, per 300 s chunk.

For each chunk: Welch PSD (10 s segments, 0.1 Hz) of each chip's floor (median PSD over its 14 wire-free inputs)
and of each animal channel; for every target frequency report the peak frequency within +-1 Hz and its height
over the +-2 Hz running median (x). Shows when a line appears/disappears, whether it drifts, and which
channels carry it. Reads 300 s at a time with posix_fadvise(DONTNEED); run at nice/ionice idle.
usage: python3 qc/line_track.py BASE OUT.csv f1 [f2 ...]
"""
import os, sys, json, csv, datetime as dt, numpy as np, scipy.signal as sg, scipy.ndimage as nd
base, out = sys.argv[1], sys.argv[2]; targets = [float(x) for x in sys.argv[3:]]
meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; fd = os.open(path, os.O_RDONLY)
nsamp = os.path.getsize(path) // (nch * 4) - 5 * fs
st = os.path.basename(base).split("uid")[1]; t_start = dt.datetime(2026, int(st[:2]), int(st[2:4]), *map(int, st[5:].split("-")))
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = {f"{p}{k}": (p, b) for p in ports for k, b in ((1, 1), (2, 33))}
series = {}
for c, (p, b) in chips.items():
    series[f"{c}_floor"] = [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)]
    series[f"{c}_EEG"] = [ix[f"{p}/{b}"]]; series[f"{c}_EMG"] = [ix[f"{p}/{b+1}"]]
cols = sorted({i for v in series.values() for i in v}); P_ = {c: k for k, c in enumerate(cols)}
CH = 300 * fs; rows = []
for c0 in range(0, nsamp - CH, CH):
    X = np.fromfile(path, dtype=np.float32, count=CH * nch, offset=c0 * nch * 4).reshape(CH, nch)
    os.posix_fadvise(fd, c0 * nch * 4, CH * nch * 4, os.POSIX_FADV_DONTNEED)
    f, P = sg.welch(X[:, cols].astype(np.float64).T, fs=fs, nperseg=10 * fs, axis=1); del X
    row = {"clock": (t_start + dt.timedelta(seconds=c0 / fs)).strftime("%H:%M")}
    for name, ch in series.items():
        ps = np.median(P[[P_[i] for i in ch]], 0); r = ps / nd.median_filter(ps, size=41, mode="nearest")
        for ft in targets:
            m = (f >= ft - 1) & (f <= ft + 1); k = np.argmax(np.where(m, r, 0))
            row[f"{name}@{ft:g}"] = round(float(r[k]), 1); row[f"{name}@{ft:g}_f"] = round(float(f[k]), 1)
    rows.append(row)
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
show = [n for n in series if n.endswith("floor")] + ["A2_EEG", "A2_EMG", "B1_EEG", "B1_EMG"]
for ft in targets:
    print(f"\n--- {ft:g} Hz: height over local median (x), per 5 min chunk; peak freq of the A2 floor in ()")
    print("clock  " + " ".join(f"{n:>9s}" for n in show))
    for r in rows:
        print(f"{r['clock']}  " + " ".join(f"{r[f'{n}@{ft:g}']:9.1f}" for n in show) + f"   ({r[f'A2_floor@{ft:g}_f']})")

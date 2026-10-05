"""Chip-floor flicker over a whole (even live) .xdat: is a low floor STEADY or INTERMITTENT?

Per 10 s window: median over each chip's 14 wire-free inputs of the 59-61 Hz line PEAK (Hann, |rfft|/(sum(win)/2)), i.e.
exactly the QC gate's hum feature (core/criteria.py; until 2026-10-02 this was a 55-65 Hz band std, an rms sqrt(2) small),
each animal's EEG/EMG line amplitude (same estimator), and EMG 30-200 Hz rms after the 3-cycle comb (movement proxy). Summary per chip: median,
CV, p95/p5, and the correlation of the floor with the same position's EMG activity and with the other
chips' floors (a room-field change moves every floor together; an intermittent ground moves one).
Reads in 300 s chunks with posix_fadvise(DONTNEED); safe at nice/ionice idle during a recording.

usage: python3 qc/floor_flicker.py BASE OUT.csv
Reference for flicker classes (tether conductors, not grounds): [[flicker-discriminates-bend-from-break]]
"""
import os, sys, json, csv, numpy as np, scipy.signal as sg
base, out = sys.argv[1], sys.argv[2]
meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; nsamp = os.path.getsize(path) // (nch * 4) - 5 * fs
fd = os.open(path, os.O_RDONLY)
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = {f"{p}{k}": (p, b) for p in ports for k, b in ((1, 1), (2, 33))}
fl = {c: [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)] for c, (p, b) in chips.items()}
an = {c: (ix[f"{p}/{b}"], ix[f"{p}/{b+1}"]) for c, (p, b) in chips.items()}
cols = sorted({i for c in chips for i in fl[c] + list(an[c])}); P = {c: k for k, c in enumerate(cols)}
SM = sg.butter(4, [30, 200], btype="band", fs=fs, output="sos")
assert fs % 20 == 0 and fs >= 500, f"fs={fs}: 10 s windows / comb assume a 1 kHz-class rate"
W, CH, PAD = 10 * fs, 300 * fs, 2 * fs
rows = []
for c0 in range(2 * fs, nsamp - W, CH):
    a, b = c0 - PAD, min(nsamp, c0 + CH) + PAD
    X = np.fromfile(path, dtype=np.float32, count=(b - a) * nch, offset=a * nch * 4).reshape(b - a, nch)
    os.posix_fadvise(fd, a * nch * 4, (b - a) * nch * 4, os.POSIX_FADV_DONTNEED)
    D = X[:, cols].astype(np.float64).T; del X
    Dc = D[:, PAD:-PAD]                                          # unfiltered, aligned with M
    M = sg.sosfiltfilt(SM, D[:, 150:] - D[:, :-150], axis=1)[:, PAD - 150:-PAD] / np.sqrt(2)
    n = Dc.shape[1] // W
    B_ = Dc[:, :n * W].reshape(len(cols), n, W); B_ = B_ - B_.mean(2, keepdims=True)
    win = np.hanning(W); fq = np.fft.rfftfreq(W, 1 / fs); m60 = (fq >= 59) & (fq <= 61)
    h = (np.abs(np.fft.rfft(B_ * win, axis=2)) / (win.sum() / 2))[:, :, m60].max(2)     # gate's hum, per window
    m = M[:, :n * W].reshape(len(cols), n, W).std(2)
    for w in range(n):
        r = {"t_s": round((c0 + w * W) / fs, 1)}
        for c in chips:
            r[f"floor_{c}"] = float(np.median(h[[P[i] for i in fl[c]], w]))
            r[f"eeg60_{c}"] = float(h[P[an[c][0]], w]); r[f"emg60_{c}"] = float(h[P[an[c][1]], w])
            r[f"emgact_{c}"] = float(m[P[an[c][1]], w])
        rows.append(r)
with open(out, "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
T = {k: np.array([r[k] for r in rows]) for k in rows[0]}
print(f"{len(rows)} windows of 10 s = {len(rows)/360:.2f} h -> {out}\n")
print("chip  floor median   CV%   p95/p5  max/min | r(floor, own EMG activity) | r(floor, other chips' floors)")
for c in chips:
    f = T[f"floor_{c}"]; others = [T[f"floor_{o}"] for o in chips if o != c]
    ro = " ".join(f"{o}:{np.corrcoef(f, T[f'floor_{o}'])[0,1]:+.2f}" for o in chips if o != c)
    print(f"{c}    {np.median(f):8.0f}   {100*f.std()/f.mean():5.1f}   {np.percentile(f,95)/np.percentile(f,5):5.2f}  {f.max()/f.min():6.2f} | "
          f"{np.corrcoef(f, T[f'emgact_{c}'])[0,1]:+.2f}                       | {ro}")

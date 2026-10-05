"""Narrow spectral lines that are NOT mains: digital/periodic injection hunt.

Welch PSD (10 s segments, 0.1 Hz bins) on each chip's floor (median PSD over its 14 wire-free inputs) and on
each animal's EEG/EMG. A line = bin > 10x its +-2 Hz running median. Each line is classed:
  mains   : a harmonic 60*k (k = 1..8), allowing for mains drift
  alias   : a harmonic 60*k (k = 9..60) folded back below Nyquist (|60k - m*fs|). The mains frequency drifts by
            about +-0.01 Hz and the k-th harmonic carries k times that, so the tolerance grows with k:
            0.15 + 0.012*k Hz (the 39th harmonic folds to ~340 Hz and wanders 339.7-340.3 Hz overnight)
  OTHER   : everything else -> candidate non-mains injection
usage: python3 qc/line_scan.py BASE t0_s dur_s [t0_s dur_s ...]
"""
import os, sys, json, numpy as np, scipy.signal as sg, scipy.ndimage as nd
base = sys.argv[1]; W = [(float(sys.argv[i]), float(sys.argv[i + 1])) for i in range(2, len(sys.argv), 2)]
meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; fd = os.open(path, os.O_RDONLY)
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = {f"{p}{k}": (p, b) for p in ports for k, b in ((1, 1), (2, 33))}
FOLD = []
for k in range(1, 61):
    fa = (60.0 * k) % fs; fa = fs - fa if fa > fs / 2 else fa      # fold into 0..fs/2
    FOLD.append((k, fa, 0.15 + 0.012 * k))
def cls(f):
    for k, fa, tol in FOLD:
        if abs(f - fa) <= tol: return "mains" if k <= 8 else "alias"
    return "OTHER"
for t0, dur in W:
    a, n = int(t0 * fs), int(dur * fs)
    nsamp = os.path.getsize(path) // (nch * 4)
    if a + n > nsamp:
        print(f"\n=== window {t0:.0f}-{t0+dur:.0f} s: SKIPPED, file has only {nsamp/fs:.0f} s"); continue
    X = np.fromfile(path, dtype=np.float32, count=n * nch, offset=a * nch * 4).reshape(n, nch).astype(np.float64).T
    os.posix_fadvise(fd, a * nch * 4, n * nch * 4, os.POSIX_FADV_DONTNEED)
    f, P = sg.welch(X, fs=fs, nperseg=10 * fs, axis=1); del X
    print(f"\n=== window {t0:.0f}-{t0+dur:.0f} s: lines > 10x local median (1-499 Hz)")
    for c, (p, b) in chips.items():
        series = {"floor": np.median(P[[ix[f"{p}/{q}"] for q in range(b + 2, b + 16)]], 0),
                  "EEG": P[ix[f"{p}/{b}"]], "EMG": P[ix[f"{p}/{b+1}"]]}
        for name, ps in series.items():
            base_ = nd.median_filter(ps, size=41, mode="nearest")
            ratio = ps / base_; ok = (f >= 1) & (f <= 499)
            pk, _ = sg.find_peaks(np.where(ok, ratio, 0), height=10, distance=3)
            other = [(f[k], ratio[k]) for k in pk if cls(f[k]) == "OTHER"]
            nm = sum(cls(f[k]) == "mains" for k in pk); na = sum(cls(f[k]) == "alias" for k in pk)
            o = ", ".join(f"{fr:.1f} Hz x{r:.0f}" for fr, r in sorted(other, key=lambda z: -z[1])[:6])
            print(f"  {c} {name:5s}: mains {nm:2d}, folded mains {na:2d}, OTHER {len(other):2d}" + (f"  [{o}]" if o else ""))

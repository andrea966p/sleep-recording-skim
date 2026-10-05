import os, sys, json, numpy as np, scipy.signal as sg
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
base, out = sys.argv[1], sys.argv[2]; ev = [float(x) for x in sys.argv[3:]]
meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; fd = os.open(path, os.O_RDONLY)
sos = sg.butter(4, [1, 450], btype="band", fs=fs, output="sos")
chips = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}
fig, ax = plt.subplots(len(ev), 2, figsize=(15, 4.2 * len(ev)), squeeze=False)
for r, t in enumerate(ev):
    a = int((t - 3) * fs); n = 6 * fs
    X = np.fromfile(path, dtype=np.float32, count=n * nch, offset=a * nch * 4).reshape(n, nch).astype(float).T
    os.posix_fadvise(fd, a * nch * 4, n * nch * 4, os.POSIX_FADV_DONTNEED)
    Dc = fs // 20                                              # the documented 3-cycle (50 ms) comb
    Y = sg.sosfiltfilt(sos, X[:, Dc:] - X[:, :-Dc], axis=1)     # comb then 1-450 Hz; NOTE: adds an inverted echo +50 ms
    tt = np.arange(Y.shape[1]) / fs + (t - 3) + Dc / fs - t
    sel = (tt > -1.0) & (tt < 1.0); off = 0
    for c, (p, b) in chips.items():
        fl = [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)]
        ax[r, 0].plot(tt[sel], np.median(Y[fl][:, sel], 0) - off, lw=.7, label=f"{c} floor (median of 14)"); off += 800
    ax[r, 0].set_title(f"event {t:.1f} s: wire-free floors (offset 800 uV)", loc="left", fontsize=10); ax[r, 0].legend(fontsize=7, loc="lower left")
    off = 0
    for c in ("A2", "B1", "A1"):
        p, b = chips[c]
        for role, k, col in (("EEG", 0, "C0"), ("EMG", 1, "C3")):
            if c == "A1" and role == "EMG": continue
            ax[r, 1].plot(tt[sel], Y[ix[f"{p}/{b+k}"], sel] - off, lw=.6, color=col); ax[r, 1].text(-1, -off + 120, f"{c} {role}", fontsize=7); off += 700
    ax[r, 1].set_title("animals (offset 700 uV)", loc="left", fontsize=10)
    for a_ in ax[r]: a_.axvline(0, color="k", lw=.5, ls=":"); a_.set_xlabel("s from detection")
fig.suptitle("50 ms comb + 1-450 Hz (removes mains and every harmonic); each transient also shows an inverted copy 50 ms later", fontsize=10)
fig.tight_layout(); fig.savefig(out, dpi=85)

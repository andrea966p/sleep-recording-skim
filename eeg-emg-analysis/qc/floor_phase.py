"""60 Hz lock-in on each chip's wire-free inputs: amplitude AND phase relative to one reference chip.

A floor is |V(open input) - V(chip reference)| at 60 Hz. Chips whose floors share a phase are dominated by
the same thing (open-input pickup); a chip whose floor sits near 180 deg from the rest is dominated by its
REFERENCE side, i.e. its reference picks up more of the field than its open inputs do. Exploratory: this
reads geometry, it does not certify a ground.
usage: python3 qc/floor_phase.py BASE REF_CHIP t0_s [t0_s ...]   (60 s per window, 1 s lock-in blocks)
"""
import os, sys, json, numpy as np
base, ref = sys.argv[1], sys.argv[2]; T0 = [float(x) for x in sys.argv[3:]]
meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; fd = os.open(path, os.O_RDONLY)
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = {f"{p}{k}": (p, b) for p in ports for k, b in ((1, 1), (2, 33))}
fl = {c: [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)] for c, (p, b) in chips.items()}
an = {c: (ix[f"{p}/{b}"], ix[f"{p}/{b+1}"]) for c, (p, b) in chips.items()}
for t0 in T0:
    a, n = int(t0 * fs), 60 * fs
    X = np.fromfile(path, dtype=np.float32, count=n * nch, offset=a * nch * 4).reshape(n, nch).astype(np.float64).T
    os.posix_fadvise(fd, a * nch * 4, n * nch * 4, os.POSIX_FADV_DONTNEED)
    X -= X.mean(1, keepdims=True)
    blk = fs; nb = n // blk; tt = np.arange(blk) / fs; e = np.exp(-2j * np.pi * 60 * tt)
    Z = (X[:, :nb * blk].reshape(nch, nb, blk) * e).sum(2) * 2 / blk          # complex 60 Hz amplitude per 1 s block
    zref = np.median(np.abs(Z[fl[ref]]), 0) * np.exp(1j * np.angle(np.sum(Z[fl[ref]], 0)))
    rel = lambda zz: np.angle(np.mean(zz * np.conj(zref) / np.abs(zref)))    # circular mean phase vs reference chip
    print(f"\nwindow t0={t0:.0f} s, phase reference = {ref} floor; amplitudes = 60 Hz PEAK (gate scale), phases circular (code review 2026-10-02)")
    for c in chips:
        zf = Z[fl[c]]; ph = np.array([rel(zf[k]) for k in range(len(fl[c]))])        # radians, per site
        R = np.mean(np.exp(1j * ph)); cmean = np.degrees(np.angle(R)); Rlen = np.abs(R)
        csd = np.degrees(np.sqrt(-2 * np.log(max(Rlen, 1e-12))))                       # circular SD
        ee, gg = Z[an[c][0]], Z[an[c][1]]
        print(f"  {c}: floor {np.median(np.abs(zf).mean(1)):7.0f} uV peak  circular mean {cmean:+7.1f} deg, "
              f"R {Rlen:.2f}, circ SD {csd:5.1f} deg | EEG {np.abs(ee).mean():6.1f} uV {np.degrees(rel(ee)):+7.1f} | "
              f"EMG {np.abs(gg).mean():7.1f} uV {np.degrees(rel(gg)):+7.1f}")

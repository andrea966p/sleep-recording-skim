"""Scan a whole Allego .xdat for ALL-CHIP transients: events that hit the wire-free
floor inputs of >= 75% of chips in the same 100 ms. Wire-free inputs carry no biology,
so an event on all of them at once is electrical and system-wide (e.g. a light switch).

usage: python3 -m qc.allchip_scan_file BASE OUT.csv
Reads in 300 s chunks with np.fromfile + posix_fadvise(DONTNEED) so the page cache is
not flooded. Threshold per chunk: 100 ms max |x| (1-450 Hz, 60 Hz comb notched) > 5x
that channel's chunk median, median over a chip's floor inputs.
"""
import os, sys, csv, json, datetime as dt
import numpy as np, scipy.signal as sg

base, out = sys.argv[1], sys.argv[2]
meta = json.load(open(base + ".xdat.json"))
bm = meta["sapiens_base"]["biointerface_map"]; fs = int(meta["status"]["samp_freq"])
lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
ix = {l: i for i, l in enumerate(lab)}
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = [(p, s) for p in ports for s in (1, 33)]
names = [f"{p}{1 if s == 1 else 2}" for p, s in chips]
fl = {c: [ix[f"{c[0]}/{q}"] for q in range(c[1] + 2, c[1] + 16)] for c in chips}
an = {c: [ix[f"{c[0]}/{c[1]}"], ix[f"{c[0]}/{c[1] + 1}"]] for c in chips}
cols = sorted({i for c in chips for i in fl[c] + an[c]}); pos = {c: i for i, c in enumerate(cols)}
stamp = os.path.basename(base).split("uid")[1]            # MMDD-HH-MM-SS
start = dt.datetime(2026, int(stamp[:2]), int(stamp[2:4]), *map(int, stamp[5:].split("-")))
path = base + "_data.xdat"; nsamp = os.path.getsize(path) // (nch * 4)
sos = np.vstack([sg.tf2sos(*sg.iirnotch(60 * k, 20, fs)) for k in range(1, 9)]
                + [sg.butter(4, [1, 450], btype="band", fs=fs, output="sos")])   # comb + band, one pass
need = max(2, int(np.ceil(0.75 * len(chips))))
CH, PAD, W = 300 * fs, 2 * fs, fs // 10
fd = os.open(path, os.O_RDONLY)
rows, last = [], -10**9
with open(out, "w", newline="") as fh:
    wr = csv.writer(fh)
    wr.writerow(["t_s", "clock", "n_chips_hit"] + [f"floorZ_{n}" for n in names]
                + [f"EEG_uV_{n}" for n in names] + [f"EMG_uV_{n}" for n in names])
    for c0 in range(0, nsamp, CH):
        a, b = max(0, c0 - PAD), min(nsamp, c0 + CH + PAD)
        raw = np.fromfile(path, dtype=np.float32, count=(b - a) * nch, offset=a * nch * 4).reshape(b - a, nch)
        os.posix_fadvise(fd, a * nch * 4, (b - a) * nch * 4, os.POSIX_FADV_DONTNEED)
        D = np.ascontiguousarray(raw[:, cols].T, dtype=np.float64); del raw
        D = sg.sosfiltfilt(sos, D, axis=1)
        nw = D.shape[1] // W
        E = np.abs(D[:, :nw * W]).reshape(len(cols), nw, W).max(2)
        Z = E / (np.median(E, 1, keepdims=True) + 1e-9)
        fz = np.array([np.median(Z[[pos[i] for i in fl[c]]], 0) for c in chips])
        hit = (fz > 5).sum(0)
        lo, hi = (c0 - a) // W, (min(nsamp, c0 + CH) - a) // W    # drop the pads
        for w in range(lo, min(hi, nw)):
            if hit[w] < need: continue
            t = (a + w * W) / fs
            if t < 2 or t > nsamp / fs - 2: continue   # file-edge filter artefact
            if t - last < 0.5: continue
            last = t
            wr.writerow([f"{t:.1f}", (start + dt.timedelta(seconds=t)).strftime("%m-%d %H:%M:%S.%f")[:-5], int(hit[w])]
                        + [f"{v:.0f}" for v in fz[:, w]]
                        + [f"{E[pos[an[c][0]], w]:.0f}" for c in chips] + [f"{E[pos[an[c][1]], w]:.0f}" for c in chips])
        fh.flush()
        print(f"{(start + dt.timedelta(seconds=c0 / fs)):%m-%d %H:%M}  {100 * min(nsamp, c0 + CH) / nsamp:5.1f}%", flush=True)

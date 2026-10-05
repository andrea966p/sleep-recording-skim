"""Per-site floor on the QC gate's scale (59-61 Hz line peak, 10 s Hann, median over epochs) for two recordings.

Splits each chip's wire-free inputs into socket pads (/3-/8: sockets soldered, empty) and bare pads (/9-/16),
and prints the ratio file2/file1 per chip and per group. Used to ask whether connecting a mouse lowers one
chip's floor uniformly (geometry/reference) or on particular sites.
usage: python3 qc/site_floor_compare.py BASE1 t1 dur1 BASE2 t2 dur2
"""
import os, sys, json, numpy as np
def gate_sites(base, t0, dur):
    meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
    fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
    ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; fd = os.open(path, os.O_RDONLY)
    ep = 10 * fs; win = np.hanning(ep); fq = np.fft.rfftfreq(ep, 1 / fs); m60 = (fq >= 59) & (fq <= 61)
    want = [f"{p}/{q}" for p in "AB" for b in (1, 33) for q in range(b + 2, b + 16)]
    cols = [ix[w] for w in want]; out = {w: [] for w in want}
    for a in range(int(t0 * fs), int((t0 + dur) * fs) - ep + 1, ep):
        X = np.fromfile(path, dtype=np.float32, count=ep * nch, offset=a * nch * 4).reshape(ep, nch)[:, cols].astype(float)
        os.posix_fadvise(fd, a * nch * 4, ep * nch * 4, os.POSIX_FADV_DONTNEED)
        X -= X.mean(0); P = np.abs(np.fft.rfft(X * win[:, None], axis=0)) / (win.sum() / 2)
        for w, v in zip(want, P[m60].max(0)): out[w].append(v)
    return {w: float(np.median(v)) for w, v in out.items()}
b1, t1, d1, b2, t2, d2 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], float(sys.argv[5]), float(sys.argv[6])
S1, S2 = gate_sites(b1, t1, d1), gate_sites(b2, t2, d2)
print(f"file1 = {os.path.basename(b1)}  file2 = {os.path.basename(b2)}  (uV peak, gate scale)")
for p, b, name in (("A", 1, "A1"), ("A", 33, "A2"), ("B", 1, "B1"), ("B", 33, "B2")):
    sock = [f"{p}/{q}" for q in range(b + 2, b + 8)]; bare = [f"{p}/{q}" for q in range(b + 8, b + 16)]
    m = lambda S, g: np.median([S[s] for s in g])
    print(f"{name}: socket pads {m(S1,sock):6.0f} -> {m(S2,sock):6.0f} (x{m(S2,sock)/m(S1,sock):4.2f}) | bare pads {m(S1,bare):6.0f} -> "
          f"{m(S2,bare):6.0f} (x{m(S2,bare)/m(S1,bare):4.2f}) | chip floor {m(S1,sock+bare):6.0f} -> {m(S2,sock+bare):6.0f} "
          f"(x{m(S2,sock+bare)/m(S1,sock+bare):4.2f})")
    print("      per site file2: " + " ".join(f"{s.split('/')[1]}:{S2[s]:.0f}" for s in sock + bare))

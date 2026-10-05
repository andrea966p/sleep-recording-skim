"""Chip floor ON THE QC GATE'S OWN SCALE, from a (live or finished) .xdat, sampled sparsely.

Replicates core/criteria.py exactly for the hum feature: 10 s epochs (EPOCH_S_QC), mean removed,
Hann window, |rfft| / (sum(win)/2), maximum over 59-61 Hz = the PEAK amplitude of the mains line;
the chip floor is the median over (epochs x the chip's wire-free sites), compared with
FLOOR_MIN_HUM_UV. Use THIS, not a 55-65 Hz band-pass std: that is an rms, sqrt(2) smaller for a line,
and on quiet channels it is mostly broadband signal, not the line (code review 2026-10-02).
Reads one epoch every STEP_S seconds, so a whole night costs a few hundred MB at idle priority.

usage: python3 qc/gate_floor.py BASE [STEP_S=180]
"""
import os, sys, json, datetime as dt, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from core import qc_thresholds as T
base = sys.argv[1]; step = float(sys.argv[2]) if len(sys.argv) > 2 else 180.0
meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
fs = int(meta["status"]["samp_freq"]); lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab)
ix = {l: i for i, l in enumerate(lab)}; path = base + "_data.xdat"; fd = os.open(path, os.O_RDONLY)
nsamp = os.path.getsize(path) // (nch * 4) - 5 * fs
st = os.path.basename(base).split("uid")[1]; t_start = dt.datetime(2026, int(st[:2]), int(st[2:4]), *map(int, st[5:].split("-")))
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = {f"{p}{k}": (p, b) for p in ports for k, b in ((1, 1), (2, 33))}
ep = int(T.EPOCH_S_QC * fs); win = np.hanning(ep); wgain = win.sum() / 2
freqs = np.fft.rfftfreq(ep, 1 / fs); m60 = (freqs >= 59) & (freqs <= 61)
cols = {c: ([ix[f"{p}/{q}"] for q in range(b + 2, b + 16)], ix[f"{p}/{b}"], ix[f"{p}/{b+1}"]) for c, (p, b) in chips.items()}
H = {c: [] for c in chips}; E = {c: [] for c in chips}; G = {c: [] for c in chips}; tt = []
for a in range(0, nsamp - ep, int(step * fs)):
    X = np.fromfile(path, dtype=np.float32, count=ep * nch, offset=a * nch * 4).reshape(ep, nch).astype(np.float64)
    os.posix_fadvise(fd, a * nch * 4, ep * nch * 4, os.POSIX_FADV_DONTNEED)
    X -= X.mean(0)
    P = np.abs(np.fft.rfft(X * win[:, None], axis=0)) / wgain
    hum = P[m60].max(0)
    for c, (fl, e, g) in cols.items():
        H[c].append(hum[fl]); E[c].append(hum[e]); G[c].append(hum[g])
    tt.append(a / fs)
tt = np.array(tt)
print(f"{len(tt)} epochs of {T.EPOCH_S_QC:.0f} s, one every {step:.0f} s, {tt[-1]/3600:.2f} h; gate FLOOR_MIN_HUM_UV = {T.FLOOR_MIN_HUM_UV:.0f} uV (peak)")
print("chip  floor(gate)  vs 800 | EEG line  EMG line (peak uV, same estimator)")
for c in chips:
    f = np.median(np.array(H[c])); verdict = "grounded" if f >= T.FLOOR_MIN_HUM_UV else "UNJUDGEABLE"
    print(f"{c}    {f:8.0f}    {verdict:11s} | {np.median(E[c]):7.1f}  {np.median(G[c]):8.1f}")
print("\nhalf-hour medians of the gate floor (uV peak):")
hh = (tt // 1800).astype(int)
print("from   " + "  ".join(f"{c:>6}" for c in chips))
for k in np.unique(hh):
    s = hh == k; t0 = t_start + dt.timedelta(seconds=float(k * 1800))
    print(f"{t0:%H:%M}  " + "  ".join(f"{np.median(np.array(H[c])[s]):6.0f}" for c in chips))

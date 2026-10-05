"""System-wide events in one window of a recording, with the SAME detector and vote as qc/allchip_scan_file.py.

usage: python3 qc/allchip_events.py BASE T0_S DUR_S
T0_S, DUR_S are file seconds. Detector: 100 ms max |y|, y = 50 ms comb x[t] - x[t-50 ms] band-passed 1-450 Hz,
over that channel's median in the window; a chip is hit when its 14 floor inputs' median exceeds 5x. Vote:
>= 75 % of the voting chips and at least one voting chip on every port; chips whose hit rate IN THE WINDOW is
> 10x the cleanest chip's do not vote (for a short window this is noisier than the file-level rule of the full scan).
Events = runs merged within 0.5 s, reported at the peak window. Rewritten 2026-10-02 after review: the old version
used an 8-notch IIR chain that rang ahead of sharp transients, had no contaminated-chip exclusion (a visit with
two railing chips gave 28 "all-chip events" with B1 at 1x), and merged within 0.2 s, unlike the full scan.
"""
import os, sys, datetime as dt
import numpy as np, scipy.signal as sg
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..")); sys.path.insert(0, HERE)
from core.criteria import open_xdat
from allchip_scan_file import need_of, events_of, qualify, contamination, peak_window, shift_null, MERGE_S, ZHIT, SHIFT_S

base, t0, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
X, lab, fs, n = open_xdat(base); ix = {l: i for i, l in enumerate(lab)}
assert fs % 20 == 0 and fs >= 500, f"fs={fs}: the 50 ms comb and 100 ms windows assume a 1 kHz-class rate"
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = [(p, s) for p in ports for s in (1, 33) if f"{p}/{s + 15}" in ix]; port_of = np.array([p for p, _ in chips])
names = [f"{p}{1 if s == 1 else 2}" for p, s in chips]
fl = {c: [ix[f"{c[0]}/{q}"] for q in range(c[1] + 2, c[1] + 16)] for c in chips}
an = {c: [ix[f"{c[0]}/{c[1]}"], ix[f"{c[0]}/{c[1] + 1}"]] for c in chips}
cols = sorted({i for c in chips for i in fl[c] + an[c]}); pos = {c: i for i, c in enumerate(cols)}
W, DC = fs // 10, fs // 20
a = max(int(t0 * fs) - 2 * fs, DC); b = min(int((t0 + dur) * fs) + 2 * fs, n)
D = np.asarray(X[a - DC:b, cols], float).T
Y = sg.sosfiltfilt(sg.butter(4, [1, 450], btype="band", fs=fs, output="sos"), D[:, DC:] - D[:, :-DC], axis=1)
nw = Y.shape[1] // W; E = np.abs(Y[:, :nw * W]).reshape(len(cols), nw, W).max(2)
lo, hi = max(0, -(-(int(t0 * fs) - a) // W)), min(nw, (min(int((t0 + dur) * fs), n) - a) // W)   # whole windows inside [T0, T0+DUR)
if hi - lo < 10:
    sys.exit(f'window {t0}+{dur} s holds fewer than 10 windows of data')
Z = E / (np.median(E[:, lo:hi], 1, keepdims=True) + 1e-9)
FZ = np.array([np.median(Z[[pos[i] for i in fl[c]]], 0) for c in chips]); hit = FZ > ZHIT
hit[:, :lo] = False; hit[:, hi:] = False
rate = hit[:, lo:hi].mean(1); vote, warn = contamination(rate, port_of, hi - lo)
need = need_of(int(vote.sum())); mw = int(round(MERGE_S * fs / W)); evs = events_of(qualify(hit, vote, port_of, need), mw)
chance = shift_null(hit[:, lo:hi], vote, port_of, need, mw, int(SHIFT_S[0] * fs / W), int(SHIFT_S[1] * fs / W), np.random.default_rng(0))
for w_ in warn:
    print("WARNING: " + w_)
print(f"{os.path.basename(base)} {t0:.0f}+{dur:.0f}s: {len(evs)} system-wide events (>= {need} of {int(vote.sum())} voting chips, "
      f"every port; not voting: {'+'.join(nm for nm, v in zip(names, vote) if not v) or 'none'}); chance (ports shifted "
      f"{SHIFT_S[0]:g}-{SHIFT_S[1]:g} s): {chance:.2f}")
for s, e in evs:
    pk = peak_window(FZ[vote].sum(0), s, e); t = (a + pk * W) / fs
    print(f"  t={t:9.1f}s  floor x-baseline per chip (max over the event): " + " ".join(f"{v:5.0f}" for v in FZ[:, s:e + 1].max(1))
          + " | EEG uV: " + " ".join(f"{E[pos[an[c][0]], s:e + 1].max():5.0f}" for c in chips)
          + " | EMG uV: " + " ".join(f"{E[pos[an[c][1]], s:e + 1].max():5.0f}" for c in chips))

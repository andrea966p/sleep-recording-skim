import sys, json, numpy as np, scipy.signal as sg
sys.path.insert(0, "/home/skimlab/sleep-recording-skim/eeg-emg-analysis")
from core.criteria import open_xdat
base, t0, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
X, lab, fs, n = open_xdat(base); ix = {l: i for i, l in enumerate(lab)}
ports = sorted({l.split("/")[0] for l in lab if l.split("/")[0] in "ABCD"})
chips = [(p, s) for p in ports for s in (1, 33)]
fl = {c: [ix[f"{c[0]}/{q}"] for q in range(c[1]+2, c[1]+16)] for c in chips}
an = {c: [ix[f"{c[0]}/{c[1]}"], ix[f"{c[0]}/{c[1]+1}"]] for c in chips}
cols = sorted({i for c in chips for i in fl[c] + an[c]})
pos = {c: i for i, c in enumerate(cols)}
a = int(t0 * fs); b = int((t0 + dur) * fs)
D = np.asarray(X[a:b, cols], float).T
for k in range(1, 9):
    bb, aa = sg.iirnotch(60 * k, 20, fs); D = sg.filtfilt(bb, aa, D, axis=1)
D = sg.sosfiltfilt(sg.butter(4, [1, 450], btype="band", fs=fs, output="sos"), D, axis=1)
w = 100; nw = D.shape[1] // w
E = np.abs(D[:, :nw * w]).reshape(len(cols), nw, w).max(2)
Z = E / np.median(E, 1, keepdims=True); Z[:, :20] = 0; Z[:, -20:] = 0
flhit = np.array([np.median(Z[[pos[i] for i in fl[c]]], 0) > 5 for c in chips])
ev = np.where(flhit.sum(0) >= max(2, int(0.75 * len(chips))))[0]
ev = [e for j, e in enumerate(ev) if j == 0 or e - ev[j - 1] > 2]
print(f"{base.split('/')[-1]} {t0:.0f}+{dur:.0f}s: {len(ev)} all-chip events")
for e in ev:
    print(f"  t={t0 + e/10:9.1f}s  floor x-baseline per chip: " + " ".join(f"{np.median(Z[[pos[i] for i in fl[c]], e]):5.0f}" for c in chips)
          + " | EEG uV: " + " ".join(f"{E[pos[an[c][0]], e]:5.0f}" for c in chips) + " | EMG uV: " + " ".join(f"{E[pos[an[c][1]], e]:5.0f}" for c in chips))

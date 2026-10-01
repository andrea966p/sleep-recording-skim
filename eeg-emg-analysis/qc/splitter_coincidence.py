import sys, itertools, numpy as np, scipy.signal as sg
sys.path.insert(0, "/home/skimlab/sleep-recording-skim/eeg-emg-analysis")
from core.criteria import open_xdat
base, t0, dur = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
X, lab, fs, n = open_xdat(base); ix = {l: i for i, l in enumerate(lab)}
chips = [(p, s) for p in "ABCD" for s in (1, 33)]; names = [f"{p}{1 if s==1 else 2}" for p, s in chips]
cols = [ix[f"{p}/{s+k}"] for p, s in chips for k in (0, 1)] + [ix[f"{p}/{q}"] for p, s in chips for q in range(s+2, s+16)]
W = 100; win = {}
hitE, hitM, hitF = [], [], []
for c0 in np.arange(t0, t0 + dur, 300):
    D = np.asarray(X[int(c0*fs)-1000:int((c0+300)*fs)+1000, cols], float).T
    y = D[:, 50:] - D[:, :-50]
    y = sg.sosfiltfilt(sg.butter(4, [1, 100], btype="band", fs=fs, output="sos"), y, axis=1)[:, 950:-950]
    med = np.median(np.abs(y), 1, keepdims=True) * 1.4826 + 1e-9
    nw = y.shape[1] // W; Z = (np.abs(y[:, :nw*W]) / med).reshape(len(cols), nw, W).max(2) > 8
    hitE.append(Z[0:16:2]); hitM.append(Z[1:16:2])
    fl = Z[16:].reshape(8, 14, nw).mean(1) > 0.5; hitF.append(fl)
E = np.concatenate(hitE, 1); M = np.concatenate(hitM, 1); F = np.concatenate(hitF, 1)
sysw = F.sum(0) >= 6                                   # drop all-chip electrical events
print(f"{E.shape[1]} windows of 100 ms; all-chip windows removed: {sysw.sum()}")
E[:, sysw] = False; M[:, sysw] = False
A = E | M                                              # any event in that animal
rate = A.mean(1); print("event rate per animal (% of windows):", " ".join(f"{nm} {r*100:.1f}" for nm, r in zip(names, rate)))
same, cross = [], []
for i, j in itertools.combinations(range(8), 2):
    obs = (A[i] & A[j]).sum(); exp = rate[i] * rate[j] * A.shape[1]
    ratio = obs / exp if exp > 0 else np.nan
    (same if names[i][0] == names[j][0] else cross).append((names[i] + "-" + names[j], obs, exp, ratio))
print("\nSAME port (share a splitter):")
for nm, o, e, r in same: print(f"  {nm}: observed {o}, chance {e:.1f}, ratio {r:.1f}")
print("\nDIFFERENT ports, median ratio %.1f (range %.1f-%.1f)" % (np.nanmedian([c[3] for c in cross]), np.nanmin([c[3] for c in cross]), np.nanmax([c[3] for c in cross])))

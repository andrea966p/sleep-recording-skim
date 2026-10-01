"""Noise scan of an Allego .xdat chunk: per-chip floor, mains + harmonics, transients.

usage: python3 noise_scan.py BASE [t0_s] [dur_s]
"""
import sys, json
import numpy as np
import scipy.signal as sg
sys.path.insert(0, "/home/skimlab/sleep-recording-skim/eeg-emg-analysis")
from core.criteria import open_xdat
from core import qc_thresholds as T

base = sys.argv[1]
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
dur = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
X, labels, fs, n = open_xdat(base)
a, b = int(t0 * fs), min(n, int((t0 + dur) * fs))
amp = [i for i, l in enumerate(labels) if l.split("/")[0] in "ABCD"]
D = np.asarray(X[a:b, amp], dtype=np.float64).T          # (ch, samples)
lab = [labels[i] for i in amp]
print(f"{base.split('/')[-1]}  fs={fs}  chunk {t0:.0f}-{b/fs:.0f} s ({(b-a)/fs:.0f} s), {len(lab)} amp ch")

def bp(lo, hi):
    return sg.butter(4, [lo, min(hi, fs / 2 - 1)], btype="band", fs=fs, output="sos")
mains = sg.sosfiltfilt(bp(*T.FILT_MAINS), D, axis=1).std(1)
f, P = sg.welch(D, fs=fs, nperseg=int(4 * fs), axis=1)
def bandrms(lo, hi):
    m = (f >= lo) & (f < hi); return np.sqrt(P[:, m].sum(1) * (f[1] - f[0]))
harm = {k: bandrms(60 * k - 1.5, 60 * k + 1.5) for k in range(1, 8) if 60 * k < fs / 2 - 5}
# broadband excluding mains lines
mask = np.ones_like(f, bool)
for k in range(1, 9): mask &= np.abs(f - 60 * k) > 2.5
def clean_rms(lo, hi):
    m = mask & (f >= lo) & (f < hi); return np.sqrt(P[:, m].sum(1) * (f[1] - f[0]))
bb = clean_rms(1, 45); hf = clean_rms(100, 450)
clip = (np.abs(D) >= T.RAIL_UV_EFF).mean(1)

idx = {l: i for i, l in enumerate(lab)}
ports = sorted({l.split("/")[0] for l in lab})
print("\n== per chip (floor = median 55-65 Hz rms of wire-free inputs; grounded chip ~2000-5000 uV) ==")
chips = []
for p in ports:
    nsite = max(int(l.split("/")[1]) for l in lab if l.startswith(p + "/"))
    for base_site in ([1, 33] if nsite > 32 else [1]):
        fl = [idx[f"{p}/{s}"] for s in range(base_site + 2, base_site + 16) if f"{p}/{s}" in idx]
        eeg, emg = idx.get(f"{p}/{base_site}"), idx.get(f"{p}/{base_site+1}")
        name = f"{p}{1 if base_site == 1 else 2}"
        floor = np.median(mains[fl]); fl_bb = np.median(bb[fl]); fl_hf = np.median(hf[fl])
        chips.append((name, eeg, emg, fl, floor))
        print(f"{name}: floor60={floor:7.0f}  floor_bb(1-45)={fl_bb:6.1f}  floor_hf(100-450)={fl_hf:6.1f}  "
              f"harm2..4 floor={np.median(harm[2][fl]):.0f}/{np.median(harm[3][fl]):.0f}/{np.median(harm[4][fl]):.0f}")
        for role, c in (("EEG", eeg), ("EMG", emg)):
            if c is None: continue
            hs = " ".join(f"{harm[k][c]:6.1f}" for k in sorted(harm))
            print(f"   {role} {lab[c]:5s} 60Hz={mains[c]:7.1f} ratio={mains[c]/floor:5.3f}  "
                  f"bb1-45={bb[c]:6.1f} hf100-450={hf[c]:6.1f} clip={clip[c]*100:4.1f}%  harm1..: {hs}")

# ---- transients: 1-s windows, per-channel robust z of 1-45 Hz (mains-notched) envelope
print("\n== transients (|x| > 8 robust SD in 1-100 Hz, mains notched) ==")
Y = sg.sosfiltfilt(bp(1, 100), D, axis=1)
for k in (1,):
    bn, an = sg.iirnotch(60 * k, 30, fs); Y = sg.filtfilt(bn, an, Y, axis=1)
med = np.median(Y, 1, keepdims=True); mad = np.median(np.abs(Y - med), 1, keepdims=True) * 1.4826 + 1e-9
Z = np.abs(Y - med) / mad
win = int(0.1 * fs); nw = Z.shape[1] // win
hit = (Z[:, :nw * win].reshape(len(lab), nw, win).max(2) > 8)   # (ch, 100 ms windows)
hit[:, :30] = False; hit[:, -30:] = False                      # 3 s filter edges
groups = {}
for name, eeg, emg, fl, _ in chips:
    groups[name + ":animal"] = [c for c in (eeg, emg) if c is not None]
    groups[name + ":floor"] = fl
gh = {g: hit[cs].any(0) for g, cs in groups.items() if cs}
for g, h in gh.items():
    print(f"  {g:12s} windows with event: {h.sum():5d} / {nw}  ({h.mean()*100:.2f}%)")
anim = [g for g in gh if g.endswith(":animal")]; flo = [g for g in gh if g.endswith(":floor")]
A = np.array([gh[g] for g in anim]); F = np.array([gh[g] for g in flo])
print(f"  windows where >=2 ANIMALS hit at once: {(A.sum(0) >= 2).sum()}   all animals: {(A.sum(0) == len(anim)).sum()}")
print(f"  windows where >=2 FLOOR groups hit at once: {(F.sum(0) >= 2).sum()}   all floors: {(F.sum(0) == len(flo)).sum()}")
print(f"  animal events that coincide with a floor event (same chip): "
      + ", ".join(f"{a.split(':')[0]} {int((gh[a] & gh[a.replace('animal','floor')]).sum())}/{int(gh[a].sum())}" for a in anim))
# within-animal EEG+EMG coincidence
for name, eeg, emg, fl, _ in chips:
    if eeg is None or emg is None: continue
    he, hm = hit[eeg], hit[emg]
    print(f"  {name}: EEG events {he.sum()}, EMG events {hm.sum()}, both same 100 ms {int((he & hm).sum())}")
out = dict(base=base, t0=t0, dur=dur, labels=lab, mains=mains.tolist(), bb=bb.tolist(), hf=hf.tolist(),
           harm={k: v.tolist() for k, v in harm.items()}, clip=clip.tolist())
json.dump(out, open(sys.argv[4] if len(sys.argv) > 4 else "/dev/null", "w"))

# ---- system-wide events: floor inputs of most chips hit in the same 100 ms
print("\n== system-wide events (>= 75% of chips' FLOOR inputs hit in the same 100 ms) ==")
need = max(2, int(np.ceil(0.75 * len(flo))))
ev = np.where(F.sum(0) >= need)[0]
# merge adjacent windows
evs = [w for i, w in enumerate(ev) if i == 0 or w - ev[i - 1] > 1]
print(f"  {len(evs)} events in {nw/10:.0f} s  ({len(evs)/(nw/10)*60:.1f}/min)")
Yraw = Y   # 1-100 Hz, 60 Hz notched
for w in evs[:25]:
    s0, s1 = max(0, (w - 1) * win), min(D.shape[1], (w + 2) * win)
    pk = np.abs(Yraw[:, s0:s1] - np.median(Yraw[:, s0:s1], 1, keepdims=True)).max(1)
    fl_pk = [np.median(pk[cs]) for g, cs in groups.items() if g.endswith(":floor")]
    an_pk = [pk[idx[f"{c[0]}/{1 if c[1]=='1' else 33}"]] for c in [g.split(':')[0] for g in groups if g.endswith(':animal')]]
    print(f"  t={t0 + w*0.1:8.1f}s  floor pk uV (median per chip): " + " ".join(f"{v:5.0f}" for v in fl_pk)
          + " | EEG pk: " + " ".join(f"{v:5.0f}" for v in an_pk))
if evs:
    # shape of the average event on the floor inputs
    seg = []
    for w in evs:
        c0 = w * win + win // 2
        if c0 - 200 >= 0 and c0 + 300 <= D.shape[1]:
            fl_all = [c for g, cs in groups.items() if g.endswith(':floor') for c in cs]
            seg.append(Yraw[fl_all, c0 - 200:c0 + 300])
    if seg:
        S = np.array(seg)                       # (ev, ch, t)
        # dominant frequency of the event on floor inputs
        ff, pp = sg.welch(S.reshape(-1, S.shape[-1]), fs=fs, nperseg=S.shape[-1], axis=1)
        print("  mean event spectrum peak (floor inputs): %.1f Hz" % ff[np.argmax(pp.mean(0)[1:]) + 1])

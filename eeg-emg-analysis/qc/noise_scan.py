"""Noise scan of an Allego .xdat chunk: per-chip floor, mains + harmonics, transients.

usage: python3 noise_scan.py BASE [t0_s] [dur_s] [OUT.json]

Units and rules (revised 2026-10-02 after a code review of the 10-01 version):
  floor / 60 Hz : the QC gate's own estimator, the PEAK amplitude of the 59-61 Hz line in 10 s Hann
                  epochs, median over epochs (core/criteria.py; directly comparable with FLOOR_MIN_HUM_UV).
                  The old number, the std of a 55-65 Hz band-pass, is still written to the JSON as "mains"
                  (band rms, legacy): it is sqrt(2) smaller for a line and, on quiet channels, mostly
                  broadband signal rather than the line. The JSON's "mains_peak" is the gate-scale number.
  harmonics     : Welch band rms within +-1.5 Hz of 60k (rms, labelled as such).
  bb / hf       : Welch band rms with every mains harmonic AND every harmonic folded back by the 1 kHz
                  sampling (60k mod fs, k <= 60, tolerance growing with k) masked out. The first version
                  masked only 60k +- 2.5 Hz, so folded lines at 140, 200, 220, 340 Hz ... counted as noise.
  transients    : 1-100 Hz with notches at every 60k below Nyquist (not just 60 Hz: the band edge passes
                  120 Hz at ~17 %, which made each channel's robust SD track its own 120 Hz pickup). A chip's
                  FLOOR is hit when the MEDIAN of its wire-free inputs' window z exceeds 8 (it used to be ANY
                  one input). System-wide events: >= 75 % of the chips that may vote; a chip whose floor fires
                  > 10x the lower-quartile chip rate and in > 1 % of windows (a railing input) does not vote.
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
assert fs % 10 == 0 and fs >= 500, f"fs={fs}: windows and notches assume a 1 kHz-class rate"
a, b = int(t0 * fs), min(n, int((t0 + dur) * fs))
amp = [i for i, l in enumerate(labels) if l.split("/")[0] in "ABCD"]
D = np.asarray(X[a:b, amp], dtype=np.float64).T          # (ch, samples)
lab = [labels[i] for i in amp]
print(f"{base.split('/')[-1]}  fs={fs}  chunk {t0:.0f}-{b/fs:.0f} s ({(b-a)/fs:.0f} s), {len(lab)} amp ch")

def bp(lo, hi):
    return sg.butter(4, [lo, min(hi, fs / 2 - 1)], btype="band", fs=fs, output="sos")
mains = sg.sosfiltfilt(bp(*T.FILT_MAINS), D, axis=1).std(1)          # legacy band rms, JSON only

# the gate's estimator: 10 s Hann epochs, |rfft| / (sum(win)/2), max over 59-61 Hz, median over epochs
ep = int(T.EPOCH_S_QC * fs); nep = D.shape[1] // ep
if nep < 1:
    sys.exit(f"need at least one {T.EPOCH_S_QC:.0f} s epoch")
win = np.hanning(ep); fq = np.fft.rfftfreq(ep, 1 / fs); m60 = (fq >= 59) & (fq <= 61)
peak = np.empty(D.shape[0])
for i in range(D.shape[0]):                                         # per channel: bounded memory
    Bk = D[i, :nep * ep].reshape(nep, ep); Bk = Bk - Bk.mean(1, keepdims=True)
    peak[i] = np.median((np.abs(np.fft.rfft(Bk * win, axis=1)) / (win.sum() / 2))[:, m60].max(1))

f, P = sg.welch(D, fs=fs, nperseg=int(4 * fs), axis=1)
def bandrms(lo, hi):
    m = (f >= lo) & (f < hi); return np.sqrt(P[:, m].sum(1) * (f[1] - f[0]))
harm = {k: bandrms(60 * k - 1.5, 60 * k + 1.5) for k in range(1, 8) if 60 * k < fs / 2 - 5}
# broadband excluding mains lines AND their folded images (k-th harmonic drifts by k x the mains drift)
mask = np.ones_like(f, bool)
for k in range(1, 61):
    fa = (60.0 * k) % fs; fa = fs - fa if fa > fs / 2 else fa
    mask &= np.abs(f - fa) > max(2.5 if k <= 8 else 0.5, 0.15 + 0.012 * k)
def clean_rms(lo, hi):
    m = mask & (f >= lo) & (f < hi); return np.sqrt(P[:, m].sum(1) * (f[1] - f[0]))
bb = clean_rms(1, 45); hf = clean_rms(100, 450)
clip = (np.abs(D) >= T.RAIL_UV_EFF).mean(1)

idx = {l: i for i, l in enumerate(lab)}
ports = sorted({l.split("/")[0] for l in lab})
print(f"\n== per chip: floor = median line PEAK (59-61 Hz, 10 s Hann; the QC gate's scale, "
      f"FLOOR_MIN_HUM_UV = {T.FLOOR_MIN_HUM_UV:.0f}) of the wire-free inputs ==")
chips = []
for p in ports:
    nsite = max(int(l.split("/")[1]) for l in lab if l.startswith(p + "/"))
    for base_site in ([1, 33] if nsite > 32 else [1]):
        fl = [idx[f"{p}/{s}"] for s in range(base_site + 2, base_site + 16) if f"{p}/{s}" in idx]
        eeg, emg = idx.get(f"{p}/{base_site}"), idx.get(f"{p}/{base_site+1}")
        name = f"{p}{1 if base_site == 1 else 2}"
        floor = np.median(peak[fl]); fl_bb = np.median(bb[fl]); fl_hf = np.median(hf[fl])
        chips.append((name, eeg, emg, fl, floor))
        gate = "grounded" if floor >= T.FLOOR_MIN_HUM_UV else "UNJUDGEABLE (< gate)"
        print(f"{name}: floor60={floor:7.0f} peak [{gate}]  floor_bb(1-45)={fl_bb:6.1f}  floor_hf(100-450)={fl_hf:6.1f} rms  "
              f"harm2..4 floor rms={np.median(harm[2][fl]):.0f}/{np.median(harm[3][fl]):.0f}/{np.median(harm[4][fl]):.0f}")
        for role, c in (("EEG", eeg), ("EMG", emg)):
            if c is None: continue
            hs = " ".join(f"{harm[k][c]:6.1f}" for k in sorted(harm))
            print(f"   {role} {lab[c]:5s} 60Hz={peak[c]:7.1f} peak ratio={peak[c]/floor:5.3f}  "
                  f"bb1-45={bb[c]:6.1f} hf100-450={hf[c]:6.1f} rms clip={clip[c]*100:4.1f}%  harm1.. rms: {hs}")

# ---- transients: 100 ms windows, per-channel robust z of 1-100 Hz with every mains harmonic notched
print("\n== transients (|x| > 8 robust SD in 1-100 Hz, every 60k Hz notched; floor = chip MEDIAN rule) ==")
Y = sg.sosfiltfilt(bp(1, 100), D, axis=1)
for k in range(1, 9):
    if 60 * k < fs / 2 - 5:
        bq, aq = sg.iirnotch(60 * k, 30, fs); Y = sg.filtfilt(bq, aq, Y, axis=1)
med = np.median(Y, 1, keepdims=True); mad = np.median(np.abs(Y - med), 1, keepdims=True) * 1.4826 + 1e-9
Z = np.abs(Y - med) / mad
wn = int(0.1 * fs); nw = Z.shape[1] // wn
Zw = Z[:, :nw * wn].reshape(len(lab), nw, wn).max(2)              # (ch, 100 ms windows)
edge = int(3 / 0.1)
Zw[:, :edge] = 0; Zw[:, -edge:] = 0                                # 3 s filter edges
groups, gh = {}, {}
for name, eeg, emg, fl, _ in chips:
    groups[name + ":animal"] = [c for c in (eeg, emg) if c is not None]
    groups[name + ":floor"] = fl
for g, cs in groups.items():
    if not cs: continue
    gh[g] = (np.median(Zw[cs], 0) > 8) if g.endswith(":floor") else (Zw[cs] > 8).any(0)
for g, h in gh.items():
    print(f"  {g:12s} windows with event: {h.sum():5d} / {nw}  ({h.mean()*100:.2f}%)")
anim = [g for g in gh if g.endswith(":animal")]; flo = [g for g in gh if g.endswith(":floor")]
A = np.array([gh[g] for g in anim]); F = np.array([gh[g] for g in flo])
print(f"  windows where >=2 ANIMALS hit at once: {(A.sum(0) >= 2).sum()}   all animals: {(A.sum(0) == len(anim)).sum()}")
print(f"  animal events that coincide with a floor event (same chip): "
      + ", ".join(f"{a.split(':')[0]} {int((gh[a] & gh[a.replace('animal','floor')]).sum())}/{int(gh[a].sum())}" for a in anim))
for name, eeg, emg, fl, _ in chips:
    if eeg is None or emg is None: continue
    he, hm = Zw[eeg] > 8, Zw[emg] > 8
    print(f"  {name}: EEG windows {he.sum()}, EMG windows {hm.sum()}, both same 100 ms {int((he & hm).sum())}")
out = dict(base=base, t0=t0, dur=dur, labels=lab, mains=mains.tolist(), mains_peak=peak.tolist(), bb=bb.tolist(),
           hf=hf.tolist(), harm={k: v.tolist() for k, v in harm.items()}, clip=clip.tolist(),
           units={"mains": "55-65 Hz band rms (legacy)", "mains_peak": "59-61 Hz line peak, QC gate scale",
                  "bb": "rms, folded mains masked", "hf": "rms, folded mains masked", "harm": "rms"})
json.dump(out, open(sys.argv[4] if len(sys.argv) > 4 else "/dev/null", "w"))

# ---- system-wide events: floors of >= 75 % of the VOTING chips hit in the same 100 ms
rate = F.mean(1)
bad = (rate > 10 * np.percentile(rate, 25)) & (rate > 0.01)
if bad.sum() > len(flo) - 2:
    bad[:] = False
vote = ~bad; need = max(2, int(np.ceil(0.75 * vote.sum())))
excl = [g.split(":")[0] for g, b_ in zip(flo, bad) if b_]
print(f"\n== system-wide events (>= {need} of the {int(vote.sum())} voting chips' floors in the same 100 ms"
      + (f"; not voting, floor fires on its own: {', '.join(excl)}" if excl else "") + ") ==")
ev = np.where(F[vote].sum(0) >= need)[0]
evs = [w for i, w in enumerate(ev) if i == 0 or w - ev[i - 1] > 1]      # merge adjacent windows
d = np.zeros(int(vote.sum()) + 1); d[0] = 1.0
for p_ in rate[vote]:
    d[1:] = d[1:] * (1 - p_) + d[:-1] * p_; d[0] *= (1 - p_)
print(f"  {len(evs)} events in {nw/10:.0f} s  ({len(evs)/(nw/10)*60:.1f}/min); chance ~{d[need:].sum() * nw:.2f} windows")
for w in evs[:25]:
    s0, s1 = max(0, (w - 1) * wn), min(D.shape[1], (w + 2) * wn)
    pk = np.abs(Y[:, s0:s1] - np.median(Y[:, s0:s1], 1, keepdims=True)).max(1)
    fl_pk = [np.median(pk[cs]) for g, cs in groups.items() if g.endswith(":floor")]
    an_pk = [pk[idx[f"{c[0]}/{1 if c[1]=='1' else 33}"]] for c in [g.split(':')[0] for g in groups if g.endswith(':animal')]]
    print(f"  t={t0 + w*0.1:8.1f}s  floor pk uV (median per chip): " + " ".join(f"{v:5.0f}" for v in fl_pk)
          + " | EEG pk: " + " ".join(f"{v:5.0f}" for v in an_pk))

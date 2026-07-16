"""state_scan.py — does a recording contain REAL SLEEP, not just variance?

Layout derived from JSON sensors_by_port (never hardcoded).
Scorer-style: bipolar -> 60Hz comb -> bandpass (0.5-30 EEG / 10-100 EMG), per 4s epoch.

VERDICT is based on SLEEP-SPECIFIC tests, not "does it vary" (any noise varies):
  td_sep   Cliff's delta of theta/delta between LOW-EMG and HIGH-EMG epochs.
           Real sleep: low EMG = NREM = delta-rich = LOW theta/delta -> STRONGLY NEGATIVE.
           This is the biology test: noise has no reason to produce it.
  bimod    bimodality coefficient of log EMG (>0.555 => two states, sleep vs wake).
  persist  autocorrelation of log EMG at ~5 min (sleep bouts last minutes; noise flickers).
  circ     for >=24h: fraction of log-EMG spectral power at 20-28 h period (circadian).
           A real mouse over >=24h MUST show a day/night rhythm.
  rail     clipping % (irreversible; high => epochs must be rejected)

Usage: state_scan.py BASE [--interval 60] [--slots-per-port 2] [--tag NAME]
"""
import json, sys, argparse
import numpy as np
from scipy import signal, stats

ap = argparse.ArgumentParser()
ap.add_argument("base"); ap.add_argument("--interval", type=float, default=60.0)
ap.add_argument("--slots-per-port", type=int, default=2)
ap.add_argument("--tag", default=None)
ap.add_argument("--start-h", type=float, default=0.0, help="analyse from this hour into the file")
ap.add_argument("--end-h", type=float, default=None, help="stop at this hour into the file (e.g. chewed tether, lights-on)")
ap.add_argument("--png", action="store_true")
a = ap.parse_args()
base = a.base
for suf in ("_data.xdat", ".xdat.json"):
    if base.endswith(suf): base = base[:-len(suf)]

J = json.load(open(base + ".xdat.json")); m = J["status"]
fs = int(m["samp_freq"]); n = int(m["num_smpl"]); tot = int(m["signals"]["total"])
mm = np.memmap(base + "_data.xdat", dtype="<f4", mode="r", shape=(n, tot))
S0 = int(a.start_h*3600*fs)
S1 = n if a.end_h is None else min(n, int(a.end_h*3600*fs))
dur_h = (S1 - S0)/fs/3600

sp = J["sapiens_base"]["sensors_by_port"]
SLOTS = []
for P in sorted(sp):
    nc = sp[P]["num_channels"]; c0 = sp[P]["connection_ntv_idx"]
    for s in range(max(1, min(a.slots_per_port, nc // 32))):
        if c0 + 32*s + 3 < tot: SLOTS.append((f"{P}{s+1}", c0 + 32*s))

DEC = 4; fsd = fs//DEC; EP = 4.0; ep = int(EP*fsd); PAD = 4.0
sos_eeg = signal.butter(4, [0.5, 30], btype="band", fs=fsd, output="sos")
sos_emg = signal.butter(4, [10, 100], btype="band", fs=fsd, output="sos")
NOTCH = []
h = 60.0
while h < fsd/2 - 1:
    NOTCH.append(signal.iirnotch(h, 30, fsd)); h += 60.0

def clean(x, sos):
    for b, aa in NOTCH: x = signal.filtfilt(b, aa, x)
    return signal.sosfiltfilt(sos, x)
def bp(f, P, lo, hi):
    k = (f >= lo) & (f < hi); return np.trapezoid(P[k], f[k])

win = int((EP + 2*PAD)*fs); step = int(a.interval*fs)
starts = np.arange(S0, S1 - win, step)
tag = a.tag or base.split("__")[-1]
print(f"\n########## {tag}  {dur_h:.2f} h  {len(starts)} epochs @1/{a.interval:.0f}s  slots={[l for l,_ in SLOTS]}")

R = {l: dict(d=[], t=[], r=[], e=[], rail=[]) for l, _ in SLOTS}
for i, s0 in enumerate(starts):
    seg = np.asarray(mm[s0:s0+win, :]).astype(np.float64)
    for lab, b in SLOTS:
        F, P, EL, ER = seg[:, b], seg[:, b+1], seg[:, b+2], seg[:, b+3]
        R[lab]["rail"].append(100*np.mean((np.abs(F) > 0.98*6390) | (np.abs(P) > 0.98*6390)))
        be = clean(signal.decimate(F-P, DEC, ftype="fir", zero_phase=True), sos_eeg)
        bm = clean(signal.decimate(EL-ER, DEC, ftype="fir", zero_phase=True), sos_emg)
        k0 = int(PAD*fsd); be = be[k0:k0+ep]; bm = bm[k0:k0+ep]
        f, Px = signal.welch(be, fs=fsd, nperseg=ep)
        R[lab]["d"].append(bp(f, Px, 0.5, 4)); R[lab]["t"].append(bp(f, Px, 6, 9))
        R[lab]["r"].append(be.std()); R[lab]["e"].append(bm.std())

def cliffs(x, y):
    """Cliff's delta: -1..+1, robust effect size."""
    u = stats.mannwhitneyu(x, y, alternative="two-sided").statistic
    return 2*u/(len(x)*len(y)) - 1

print(f"{'slot':4s} {'rail%':>6s} {'keep%':>6s} {'EEGuV':>6s} {'EMGuV':>6s} | {'td_sep':>7s} {'bimod':>6s} {'persist':>7s} {'circ':>6s} | VERDICT")
out = {}
for lab, _ in SLOTS:
    d = np.array(R[lab]["d"]); t = np.array(R[lab]["t"]); r = np.array(R[lab]["r"])
    e = np.array(R[lab]["e"]); rl = np.array(R[lab]["rail"])
    # REJECT clipped epochs: a railed amp is non-linear, its spectrum is meaningless.
    # Scorers drop these; computing td_sep over them measures the artifact, not the brain.
    keep = rl < 1.0
    frac_keep = keep.mean()
    enough = keep.sum() > 60
    if enough: d, t, r, e = d[keep], t[keep], r[keep], e[keep]
    td = t/(d+1e-12); le = np.log10(e+1e-12)

    # 1) BIOLOGY TEST: theta/delta in low-EMG vs high-EMG epochs (real: low EMG => low th/d)
    q1, q3 = np.percentile(e, [33, 67])
    lo, hi = td[e <= q1], td[e >= q3]
    td_sep = cliffs(lo, hi) if (len(lo) > 20 and len(hi) > 20) else np.nan

    # 2) EMG bimodality
    sk = stats.skew(le); ku = stats.kurtosis(le, fisher=False)
    bimod = (sk**2 + 1)/(ku + 1e-9)

    # 3) bout persistence: autocorrelation of log EMG at ~5 min
    lag = max(1, int(300/a.interval))
    x = le - le.mean()
    persist = (np.dot(x[:-lag], x[lag:])/((len(x)-lag)*x.var()+1e-12)) if len(x) > lag+10 else np.nan

    # 4) circadian: power at 20-28h period, only meaningful >=24h
    circ = np.nan
    if dur_h >= 24 and len(le) > 100:
        y = le - le.mean()
        f2, P2 = signal.welch(y, fs=1.0/a.interval, nperseg=min(len(y), int(len(y)/2)))
        per_h = 1.0/(f2[1:]*3600); Pp = P2[1:]
        k = (per_h >= 20) & (per_h <= 28)
        circ = np.trapezoid(Pp[k], f2[1:][k])/(np.trapezoid(Pp, f2[1:]) + 1e-12) if k.any() else 0.0

    ok_bio = (not np.isnan(td_sep)) and td_sep < -0.25
    ok_state = (bimod > 0.45) or (not np.isnan(persist) and persist > 0.3)
    ok_circ = True if dur_h < 24 else (not np.isnan(circ) and circ > 0.05)
    # A slot with too few clean epochs cannot be verdicted at all. Never fall back to
    # railed data and print a biology call from it - that reports the artifact as sleep.
    if not enough:
        v = f"UNSCOREABLE (only {keep.sum()} clean epochs)"
    elif ok_bio and ok_state and ok_circ:
        v = "SLEEP-LIKE"
    elif not ok_bio:
        v = "no sleep biology"
    elif not ok_circ:
        v = "no circadian"
    else:
        v = "weak"
    cs = f"{circ*100:5.1f}%" if not np.isnan(circ) else "   n/a"
    print(f"{lab:4s} {np.median(rl):5.1f}% {frac_keep*100:5.0f}% {np.median(r):6.0f} {np.median(e):6.0f} | "
          f"{td_sep:+7.2f} {bimod:6.2f} {persist:+7.2f} {cs:>6s} | {v}")
    out[lab] = v
print("  (td_sep must be NEGATIVE = low-EMG epochs are delta-rich = NREM. bimod>0.555 bimodal. "
      "persist=EMG autocorr @5min. circ=% power at 20-28h period, needs >=24h.)")

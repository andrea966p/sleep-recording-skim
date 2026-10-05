"""Did the facility air shower show on the free inputs or the mice? Light-phase run 8f84e3e62af6, 2026-10-02.

Reads [START, END) of allego_0__uid1002-09-16-58 only (about 0.5 GB per 15 min), at idle priority, page cache dropped.
Time origin = the file's status.start_time (09:16:58.153 KST), not the name. ON is the reported switch-on; CLOCK says
whose clock: `andrea` (her clock ran >= 8 s AHEAD of e10, so the true switch-on is at or before ON - 8 s) or `e10`.
Per 1 s (1 s Hann, 1 Hz bins): 60 Hz line (peak) and non-mains band rms for 1-45 and 100-450 Hz. "Non-mains" drops
every bin within 2 Hz of a multiple of 20 Hz: at fs = 1000 every mains harmonic, folded or not, sits on a multiple of
20 Hz, and a 1 s Hann main lobe spans +-2 bins (a +-1 exclusion leaked mains, review 2026-10-02).
Per 50 ms: switching-step detector = peak |d/dt| of the 50 ms comb x[t] - x[t-50 ms], which cancels 60 Hz and every
harmonic first. On a floor carrying 2 mV of mains the raw |dx| is the slope of the 60 Hz line and hides steps below
~1-2 mV; after the comb a 0.1 mV step is detected (synthetic test, review 2026-10-02).
A2 EMG arousal: first 100 ms bin of 100-450 Hz rms above 5x the 30 s quiet level after ON - 5 s, and the chance of a
burst from quiet in a random window of the same length, from 16:40 to ON with every disturbed window of the canonical
markers and the minute before ON left out.
usage: nice -n 19 ionice -c3 python3 qc/air_shower_2026_10_02.py START END FIG.png ON [andrea|e10]
   e.g. 17:12:00 17:27:30 figI.png 17:22:14 andrea ;  17:28:00 17:38:00 figJ.png 17:35:50 andrea
"""
import os, sys, json, textwrap, datetime as dt
import numpy as np, scipy.signal as sg
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import noise_mice_markers_2026_10_02 as MK

START, END, FIG, ON_S = sys.argv[1:5]; CLOCK = sys.argv[5] if len(sys.argv) > 5 else "andrea"
AHEAD_S = 8.0 if CLOCK == "andrea" else 0.0          # lower bound on how far ahead the reported clock ran
BASE = os.path.join(MK.RAW, MK.RUNS["lightphase"]); T0a, fs, N, _ = MK.file_origin(MK.RUNS["lightphase"])
T0 = T0a.replace(tzinfo=None); fs = int(fs); assert fs == 1000
c = lambda s: dt.datetime.combine(T0.date(), dt.time.fromisoformat(s))
ON = c(ON_S); ON_TRUE_LATEST = ON - dt.timedelta(seconds=AHEAD_S)
meta = json.load(open(BASE + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; nch = len(lab); ix = {l: i for i, l in enumerate(lab)}
path = BASE + "_data.xdat"; fd = os.open(path, os.O_RDONLY)
CH = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}
FL = {k: [ix[f"{p}/{q}"] for q in range(b + 2, b + 16)] for k, (p, b) in CH.items()}
ANI = {"A2 EEG": "A/33", "A2 EMG": "A/34", "B1 EEG": "B/1", "B1 EMG": "B/2", "A1 EEG": "A/1", "B2 EEG": "B/33",
       "A1 EMG (open)": "A/2", "B2 EMG (open)": "B/34"}
COLS = sorted({i for v in FL.values() for i in v} | {ix[s] for s in ANI.values()}); P_ = {col: k for k, col in enumerate(COLS)}

a0 = int(round((c(START) - T0).total_seconds() * fs)); a1 = min(int(round((c(END) - T0).total_seconds() * fs)), N)
nsec = (a1 - a0) // fs
if nsec < 120 or not (c(START) <= ON_TRUE_LATEST - dt.timedelta(seconds=60) and ON < c(END)):
    sys.exit(f"window {START}-{END} must start >= 60 s before the latest true switch-on ({ON_TRUE_LATEST:%H:%M:%S}) and hold ON")
raw = np.fromfile(path, dtype=np.float32, count=nsec * fs * nch, offset=a0 * nch * 4).reshape(-1, nch)
os.posix_fadvise(fd, a0 * nch * 4, nsec * fs * nch * 4, os.POSIX_FADV_DONTNEED)
X = raw[:, COLS].astype(np.float64); del raw
col = lambda chans: [P_[q] for q in chans]
t = np.array([T0 + dt.timedelta(seconds=a0 / fs + k + .5) for k in range(nsec)])

f = np.fft.rfftfreq(fs, 1 / fs); w = np.hanning(fs); g = w.sum() / 2
keep = np.abs((f + 10) % 20 - 10) > 2
lo, hi = keep & (f >= 1) & (f <= 45), keep & (f >= 100) & (f <= 450)
def per_sec(cols):
    Y = X[:, cols].reshape(nsec, fs, len(cols)); Y = Y - Y.mean(1, keepdims=True)
    S = np.fft.rfft(Y * w[None, :, None], axis=1); A = np.abs(S) / g; P = np.abs(S) ** 2 / (fs * (w ** 2).sum()) * 2
    return dict(l60=A[:, 60], lo=np.sqrt(P[:, lo].sum(1)), hi=np.sqrt(P[:, hi].sum(1)))
DC = fs // 20                                            # 50 ms comb
def per_50ms(cols):
    Y = X[:, cols]; Y = np.vstack([np.zeros((DC, len(cols))), Y[DC:] - Y[:-DC]])
    D = np.abs(np.diff(Y, axis=0, prepend=Y[:1])); D[:2 * DC] = 0; m = D.shape[0] // 50
    return D[: m * 50].reshape(m, 50, len(cols)).max(1)
R, Q = {}, {}
for k, chans in FL.items():
    r = per_sec(col(chans)); R[k + " floor"] = {q: np.median(v, 1) for q, v in r.items()}; Q[k + " floor"] = np.median(per_50ms(col(chans)), 1)
for name, site in ANI.items():
    r = per_sec(col([ix[site]])); R[name] = {q: v[:, 0] for q, v in r.items()}; Q[name] = per_50ms(col([ix[site]]))[:, 0]
t50 = np.array([T0 + dt.timedelta(seconds=a0 / fs + k * .05 + .025) for k in range(len(Q["A1 floor"]))])

# ---- electrical: the minute after vs before, and steps above the window's own pre-ON maximum
pre_s, post_s = (t >= ON_TRUE_LATEST - dt.timedelta(seconds=60)) & (t < ON_TRUE_LATEST - dt.timedelta(seconds=5)), (t >= ON_TRUE_LATEST - dt.timedelta(seconds=5)) & (t < ON + dt.timedelta(seconds=60))
ratio = {k: float(np.median(R[k + " floor"]["l60"][post_s]) / np.median(R[k + " floor"]["l60"][pre_s])) for k in CH}
b50 = (t50 < ON_TRUE_LATEST - dt.timedelta(seconds=10)) & (t50 > t50[0] + dt.timedelta(seconds=2))
a50 = (t50 >= ON_TRUE_LATEST - dt.timedelta(seconds=10)) & (t50 < ON + dt.timedelta(seconds=60))
steps, Z = {}, {}
for k in CH:
    v = Q[k + " floor"]; med = np.median(v[b50]); mad = np.median(np.abs(v[b50] - med)) * 1.4826 + 1e-9
    z = (v - med) / mad; zb = z[b50].max(); Z[k] = z; steps[k] = (int((a50 & (z > max(8, zb))).sum()), float(zb), float(med))
print(f"{t[0]:%H:%M:%S}-{t[-1]:%H:%M:%S} ({nsec} s); ON {ON:%H:%M:%S} by the {CLOCK} clock, true switch-on <= {ON_TRUE_LATEST:%H:%M:%S}")
print("floor 60 Hz, minute after / minute before: " + ", ".join(f"{k} x{v:.3f}" for k, v in ratio.items()))
print("comb step detector, 50 ms windows from ON-10 s to ON+60 s above max(8, the pre-ON maximum z): "
      + ", ".join(f"{k} {n} (pre-ON max z {zb:.1f}, baseline {med:.0f} uV)" for k, (n, zb, med) in steps.items()))
for k, (n, zb, med) in steps.items():                   # where, how big, and what the other chips did at that instant
    for i in np.where(a50 & (Z[k] > max(8, zb)))[0][:12]:
        print(f"   {k} step {t50[i]:%H:%M:%S.%f}"[:-4] + f": {Q[k + ' floor'][i]:.0f} uV (z {Z[k][i]:.0f}); other chips z "
              + " ".join(f"{o} {Z[o][i]:.1f}" for o in CH if o != k)
              + f"; own mouse EMG |d/dt comb| {Q[{'A1': 'A1 EMG (open)', 'A2': 'A2 EMG', 'B1': 'B1 EMG', 'B2': 'B2 EMG (open)'}[k]][i]:.0f} uV")

# ---- A2 EMG onset at 100 ms
sos = sg.butter(4, [100, 450], "bandpass", fs=fs, output="sos")
e = sg.sosfiltfilt(sos, X[:, P_[ix["A/34"]]]); m10 = len(e) // 100; env = np.sqrt((e[: m10 * 100].reshape(m10, 100) ** 2).mean(1))
t10 = np.array([T0 + dt.timedelta(seconds=a0 / fs + k * .1 + .05) for k in range(m10)])
quiet = (t10 > ON_TRUE_LATEST - dt.timedelta(seconds=35)) & (t10 < ON_TRUE_LATEST - dt.timedelta(seconds=5))
qlev = float(np.median(env[quiet])) if quiet.any() else np.nan
cand = np.where((t10 >= ON_TRUE_LATEST - dt.timedelta(seconds=5)) & (env > 5 * qlev))[0]
onset = None
if cand.size:
    k_on = cand[0]; lat_rep = (t10[k_on] - ON).total_seconds()
    onset = dict(t=t10[k_on], lat_reported=lat_rep, lat_true_min=lat_rep + AHEAD_S, peak=float(env[k_on:k_on + 30].max()))
    print(f"A2 EMG 100-450 Hz, 100 ms rms: quiet {qlev:.1f} uV; first bin > 5x quiet {onset['t']:%H:%M:%S.%f}"[:-3]
          + f", {lat_rep:+.1f} s from the reported ON ({onset['lat_true_min']:+.1f} s or later from the true switch-on); peak {onset['peak']:.0f} uV")
else:
    print(f"A2 EMG: no 100 ms bin above 5x quiet ({qlev:.1f} uV) from ON-5 s to {END}")

# ---- chance of a burst from quiet: 16:40 -> ON, disturbed windows and the minute before ON excluded
B0, B1_ = max(c("16:40:00"), T0 + dt.timedelta(seconds=60)), ON_TRUE_LATEST - dt.timedelta(seconds=60)
excl = [(T0 + dt.timedelta(seconds=a), T0 + dt.timedelta(seconds=b)) for a, b, _ in MK.disturbed("lightphase")]
b0 = int(round((B0 - T0).total_seconds() * fs)); nb = int((B1_ - B0).total_seconds())
hi_s = {s: [] for s in ("A/34", "B/2")}
if nb < 600:
    print(f"chance baseline {B0:%H:%M:%S}-{B1_:%H:%M:%S} is shorter than 10 min: chance not computed")
for k0 in range(0, nb if nb >= 600 else 0, 300):
    m = min(300, nb - k0); off = (b0 + k0 * fs) * nch * 4
    Y = np.fromfile(path, dtype=np.float32, count=m * fs * nch, offset=off).reshape(m, fs, nch); os.posix_fadvise(fd, off, m * fs * nch * 4, os.POSIX_FADV_DONTNEED)
    for s in hi_s:
        y = Y[:, :, ix[s]].astype(float); y -= y.mean(1, keepdims=True); S = np.fft.rfft(y * w, axis=1)
        hi_s[s].append(np.sqrt((np.abs(S) ** 2 / (fs * (w ** 2).sum()) * 2)[:, hi].sum(1)))
WIN_S = max(3, int(np.ceil(onset["lat_true_min"])) + 1) if onset else 3     # window long enough to hold the observed latency
chance = {}
for s, name in (("A/34", "A2 EMG"), ("B/2", "B1 EMG")) if nb >= 600 else ():
    h = np.concatenate(hi_s[s]); q = np.percentile(h, 20); tb = np.array([B0 + dt.timedelta(seconds=k + .5) for k in range(len(h))])
    clean = np.ones(len(h), bool)
    for a, b in excl:
        clean &= ~((tb >= a) & (tb < b))
    k = np.arange(10, len(h))
    elig = np.array([clean[i - 10:i + 1].all() and h[i - 10:i].max() < 2 * q for i in k]); ons = (h[k] >= 5 * q) & elig
    r = ons.sum() / max(elig.sum(), 1); p_win = 1 - (1 - r) ** WIN_S
    hit = R[name]["hi"]; kON = int(np.argmin(np.abs([(x - ON_TRUE_LATEST).total_seconds() for x in t])))
    pre_q = bool(kON >= 10 and hit[kON - 10:kON].max() < 2 * q)
    chance[name] = dict(q=q, n_elig=int(elig.sum()), n_on=int(ons.sum()), p_win=p_win, quiet_before=pre_q)
    print(f"{name}: baseline 16:40-{B1_:%H:%M:%S} minus disturbed windows: quiet level {q:.1f} uV, {elig.sum()} quiet-preceded s, "
          f"{ons.sum()} onsets -> chance of an onset within {WIN_S} s of a random time {100 * p_win:.1f} %; quiet before ON: {pre_q}")

# ---- figure
fig, ax = plt.subplots(5, 1, figsize=(13, 13), sharex=True)
COL = {"A1": "0.55", "A2": "tab:blue", "B1": "tab:red", "B2": "tab:purple"}
for k in CH: ax[0].plot(t, R[k + " floor"]["l60"], lw=.8, color=COL[k], label=f"{k} floor")
for k in CH: ax[1].plot(t50, Q[k + " floor"], lw=.5, color=COL[k], label=f"{k} floor")
for key, cl in [("A2 EMG", "tab:blue"), ("B1 EMG", "tab:red"), ("A1 EMG (open)", "0.55"), ("B2 EMG (open)", "tab:purple")]:
    ax[2].plot(t, R[key]["l60"], lw=.8, color=cl, label=key)
for key, cl in [("A2 EMG", "tab:blue"), ("B1 EMG", "tab:red")]: ax[3].plot(t, R[key]["hi"], lw=.8, color=cl, label=key)
for key, cl in [("A2 EEG", "tab:blue"), ("B1 EEG", "tab:red"), ("A1 EEG", "0.55"), ("B2 EEG", "tab:purple")]:
    ax[4].plot(t, R[key]["lo"], lw=.8, color=cl, label=key)
lbl = ["floor 60 Hz line\n(uV peak, 1 s)", "floor switching-step detector\n|d/dt| of the 50 ms comb (uV)", "EMG 60 Hz line\n(uV peak, 1 s)",
       "EMG muscle band\n100-450 non-mains (uV rms)", "EEG 1-45 Hz\nnon-mains (uV rms)"]
others = [r for r in MK.rows("lightphase") if r["kind"] == "disturbance"]
for a_, l in zip(ax, lbl):
    a_.axvline(ON, color="tab:orange", lw=1.5)
    if AHEAD_S:
        a_.axvline(ON_TRUE_LATEST, color="tab:orange", lw=1, ls="--")
    for r in others:
        tc = dt.datetime.fromisoformat(r["clock_kst"])
        if t[0] < tc < t[-1] and abs((tc - ON).total_seconds()) > 1:
            a_.axvline(tc, color="tab:orange", lw=.8, ls=":")
    a_.set_ylabel(l); a_.set_yscale("log"); a_.grid(alpha=.25); a_.legend(fontsize=7.5, ncol=4, loc="upper left")
ax[0].set_title(f"orange = reported switch-on {ON:%H:%M:%S} ({CLOCK}'s clock)" + (f"; dashed = latest true time {ON_TRUE_LATEST:%H:%M:%S} "
                f"(that clock ran >= {AHEAD_S:.0f} s ahead)" if AHEAD_S else "") + "; dotted = other reported air-shower times", loc="left", fontsize=9)
ax[4].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M")); ax[4].set_xlabel("clock time 2026-10-02 KST (file clock)")
over = np.array([a50 & (Z[k] > max(8, steps[k][1])) for k in CH])          # chip x window: above its own pre-ON maximum
def n_events(mask):            # the comb's inverted echo lands in the next 50 ms window: adjacent windows = one step (review round 3)
    idx = np.flatnonzero(mask); return int(len(idx) and 1 + (np.diff(idx) > 1).sum())
n_sys = n_events(over.sum(0) >= 2)                                            # a building transient reaches every chip at once
single = {k: n_events(over[j] & (over.sum(0) == 1)) for j, k in enumerate(CH)}
thr_uv = {k: steps[k][2] + max(8, steps[k][1]) * float(np.median(np.abs(Q[k + " floor"][b50] - steps[k][2])) * 1.4826) for k in CH}
print("step-detector thresholds (|d/dt| comb, uV): " + ", ".join(f"{k} {v:.0f}" for k, v in thr_uv.items()))
sing_txt = ", ".join(f"{k} {v}" for k, v in single.items() if v) or "none"
print(f"switching steps on >= 2 chips in the same 50 ms: {n_sys}; single-chip steps (adjacent windows merged): {sing_txt}")
el = (f"Floors: 60 Hz x{min(ratio.values()):.2f}-{max(ratio.values()):.2f} in the minute after vs before; switching steps on >= 2 chips "
      f"at once: {n_sys} (comb detector; a step on two chips must clear the second-lowest chip threshold, "
      f"{sorted(thr_uv.values())[1]:.0f} uV: " + ", ".join(f"{k} {v:.0f}" for k, v in thr_uv.items()) + f"); single-chip steps: {sing_txt} "
      "(a chip alone = that mouse moving). ")
a2 = ((f"A2 EMG: first burst {onset['lat_reported']:+.1f} s from the reported time = {onset['lat_true_min']:+.1f} s or later from the true "
       f"switch-on, peak x{onset['peak'] / qlev:.0f} its quiet level" + (f"; quiet before: {chance['A2 EMG']['quiet_before']}; chance of a burst "
       f"from quiet within {WIN_S} s: {100 * chance['A2 EMG']['p_win']:.0f} %." if "A2 EMG" in chance else "."))
      if onset else "A2 EMG: no burst after the switch-on.")
fig.suptitle(textwrap.fill(f"Facility air shower {ON:%H:%M:%S} ({CLOCK}) vs the rig, light-phase run 8f84e3e62af6. " + el + a2, 165), fontsize=9.5)
fig.tight_layout(); fig.savefig(FIG, dpi=105); print("figure ->", FIG)

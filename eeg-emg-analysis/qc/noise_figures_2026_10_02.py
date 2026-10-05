"""Figures for the 2026-10-02 noise-series findings (vault: 05-experiments/attachments). Diagnostic, not QC.

Every 60 Hz number is the QC gate's own estimator (core/criteria.py, as in qc/gate_floor.py): 10 s epochs, mean
removed, Hann window, |rfft| / (sum(win)/2), maximum over 59-61 Hz = the PEAK amplitude of the mains line.
A chip floor is the median over (epochs x the chip's 14 wire-free inputs, /3-/16 or /35-/48), compared with
FLOOR_MIN_HUM_UV (800 uV).

  fig A  overnight trend: chip floors, EEG and EMG 60 Hz line, one 10 s epoch every STEP_S (default 180 s)
  fig B  the lights-ON at 08:59:51: floors and animals, 20 s around it (50 ms comb + 1-450 Hz)
  fig C  per-site floors of B2, B1 and A2: before the B boards were refitted (16:29, no mice) vs with mice (19:50, overnight)
  fig D  chip floors of every noise-series recording against the 800 uV gate (audit C1)

Reads at idle priority with the page cache dropped: ~1.3 GB of the overnight file, plus the short 09-30/10-01 recordings.
usage: nice -n 19 ionice -c3 python3 qc/noise_figures_2026_10_02.py FIGDIR DATADIR [STEP_S]
"""
import os, sys, json, csv, datetime as dt
import numpy as np, scipy.signal as sg
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from core import qc_thresholds as T

FIG, DATA = sys.argv[1], sys.argv[2]
STEP = float(sys.argv[3]) if len(sys.argv) > 3 else 180.0
os.makedirs(FIG, exist_ok=True); os.makedirs(DATA, exist_ok=True)
NT = os.path.expanduser("~/radix/noise-tests")
NIGHT = os.path.expanduser("~/radix/data/allego_0__uid1001-21-00-07")
CHIPS = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}
COL = {"A1": "0.55", "A2": "tab:blue", "B1": "tab:red", "B2": "tab:purple"}
RUNS = [  # (short label, base, what was on the chips)
    ("09-30 15:50\nno mice", f"{NT}/2026-09-30/noise_baseline_0__uid0930-15-50-52", "empty"),
    ("09-30 16:45\nno mice, taped", f"{NT}/2026-09-30/noise_e2_tape_multitap_0__uid0930-16-45-25", "empty"),
    ("10-01 15:40\ndirect USB", f"{NT}/2026-10-01/iso_before_0__uid1001-15-40-40", "empty"),
    ("10-01 16:09\nUSB isolator", f"{NT}/2026-10-01/iso_after_0__uid1001-16-09-23", "empty"),
    ("10-01 16:29\ndirect again", f"{NT}/2026-10-01/direct_again_0__uid1001-16-29-42", "empty"),
    ("10-01 16:48\nB boards off", f"{NT}/2026-10-01/Bboards_off_Cunipolar_0__uid1001-16-48-09", "Boff"),
    ("10-01 19:50\n4 mice", f"{NT}/2026-10-01/mice4_A1A2B1B2_first_0__uid1001-19-50-31", "mice"),
    ("10-01 20:36\nbaseline 1", f"{NT}/2026-10-01/mice4_baseline1_untouched_0__uid1001-20-36-33", "mice"),
    ("10-01 20:42\nbaseline 2", f"{NT}/2026-10-01/mice4_baseline2_untouched_0__uid1001-20-42-41", "mice"),
    ("overnight\n21:00-09:02", NIGHT, "mice"),
]


class Rec:
    def __init__(self, base):
        meta = json.load(open(base + ".xdat.json")); bm = meta["sapiens_base"]["biointerface_map"]
        self.fs = int(meta["status"]["samp_freq"]); assert self.fs == 1000, f"{base}: fs={self.fs}"
        self.lab = [f"{p}/{s}" for p, s in zip(bm["port"], bm["site_num"])]; self.nch = len(self.lab)
        self.ix = {l: i for i, l in enumerate(self.lab)}; self.path = base + "_data.xdat"
        self.n = os.path.getsize(self.path) // (self.nch * 4)
        # the file's own start (UTC, ms) in KST; the uid in the name is rounded to the second (review 2026-10-02)
        self.t0 = (dt.datetime.fromisoformat(meta["status"]["start_time"].replace("Z", "+00:00"))
                   + dt.timedelta(hours=9)).replace(tzinfo=None)
        self.fd = os.open(self.path, os.O_RDONLY)

    def read(self, a, n):                               # samples a .. a+n, all channels, float64 (n, nch)
        x = np.fromfile(self.path, dtype=np.float32, count=n * self.nch, offset=a * self.nch * 4).reshape(n, self.nch)
        os.posix_fadvise(self.fd, a * self.nch * 4, n * self.nch * 4, os.POSIX_FADV_DONTNEED)
        return x.astype(np.float64)


def line_peaks(rec, step_s, chans):
    """Gate estimator per epoch: array (n_epochs, len(chans)) of 59-61 Hz line peaks, and epoch start times (s)."""
    ep = int(T.EPOCH_S_QC * rec.fs); win = np.hanning(ep); g = win.sum() / 2
    m60 = (np.fft.rfftfreq(ep, 1 / rec.fs) >= 59) & (np.fft.rfftfreq(ep, 1 / rec.fs) <= 61)
    cols = [rec.ix[c] for c in chans]; out, tt = [], []
    for a in range(0, rec.n - ep - 5 * rec.fs, int(step_s * rec.fs)):
        X = rec.read(a, ep)[:, cols]; X -= X.mean(0)
        out.append((np.abs(np.fft.rfft(X * win[:, None], axis=0)) / g)[m60].max(0)); tt.append(a / rec.fs)
    return np.array(out), np.array(tt)


def floor_sites(p, b):
    return [f"{p}/{q}" for q in range(b + 2, b + 16)]


ALL_SITES = [s for p, b in CHIPS.values() for s in floor_sites(p, b)]
ANIMAL = [f"{p}/{b + k}" for p, b in CHIPS.values() for k in (0, 1)]

# ---------------------------------------------------------------- data: per recording, per epoch, per channel
rows_chip, rows_site, night = [], [], None
for label, base, state in RUNS:
    rec = Rec(base); chans = ALL_SITES + ANIMAL
    P, tt = line_peaks(rec, STEP if base == NIGHT else T.EPOCH_S_QC, chans)
    k = {c: i for i, c in enumerate(chans)}
    for chip, (p, b) in CHIPS.items():
        fl = [k[s] for s in floor_sites(p, b)]
        rows_chip.append(dict(run=label.replace("\n", " "), base=os.path.basename(base), state=state, chip=chip,
                              n_epochs=len(tt), floor_gate_uV=float(np.median(P[:, fl])),
                              eeg_line_uV=float(np.median(P[:, k[f"{p}/{b}"]])), emg_line_uV=float(np.median(P[:, k[f"{p}/{b+1}"]]))))
        for s in floor_sites(p, b):
            rows_site.append(dict(run=label.replace("\n", " "), chip=chip, site=s, floor_gate_uV=float(np.median(P[:, k[s]]))))
    if base == NIGHT:
        night = (rec, P, tt, k)
    print(f"{label.replace(chr(10), ' '):34s} {len(tt):4d} epochs  " +
          "  ".join(f"{r['chip']} {r['floor_gate_uV']:6.0f}" for r in rows_chip[-4:]), flush=True)

for name, rows in (("chip_floors.csv", rows_chip), ("site_floors.csv", rows_site)):
    with open(os.path.join(DATA, name), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

rec, P, tt, k = night
clock = [rec.t0 + dt.timedelta(seconds=float(t)) for t in tt]
with open(os.path.join(DATA, "overnight_trend.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["t_s", "clock"] + [f"floor_{c}" for c in CHIPS] + [f"eeg_{c}" for c in CHIPS] + [f"emg_{c}" for c in CHIPS])
    for i, t in enumerate(tt):
        fl = [np.median(P[i, [k[s] for s in floor_sites(*CHIPS[c])]]) for c in CHIPS]
        w.writerow([f"{t:.0f}", f"{clock[i]:%m-%d %H:%M:%S}"] + [f"{v:.1f}" for v in fl]
                   + [f"{P[i, k[f'{p}/{b}']]:.2f}" for p, b in CHIPS.values()]
                   + [f"{P[i, k[f'{p}/{b+1}']]:.2f}" for p, b in CHIPS.values()])

# ---------------------------------------------------------------- fig A: overnight trend
LON_FILE_S = 43184.2                     # the all-chip lights-ON event, file seconds (allchip_scan_file.py t_s; canonical markers)
LON = rec.t0 + dt.timedelta(seconds=LON_FILE_S)
fig, ax = plt.subplots(3, 1, figsize=(11, 9.5), sharex=True)
hh = np.array([(c - clock[0]).total_seconds() // 1800 for c in clock])
for chip, (p, b) in CHIPS.items():
    fl = np.median(P[:, [k[s] for s in floor_sites(p, b)]], axis=1)
    ax[0].plot(clock, fl, ".", ms=2.5, color=COL[chip], alpha=.35)
    hc = [clock[int(np.median(np.where(hh == h)[0]))] for h in np.unique(hh)]
    ax[0].plot(hc, [np.median(fl[hh == h]) for h in np.unique(hh)], "-", lw=2, color=COL[chip],
               label=f"{chip}  gate value {np.median(P[:, [k[s] for s in floor_sites(p, b)]]):.0f}")
    ax[1].plot(clock, P[:, k[f"{p}/{b}"]], "-", lw=.9, color=COL[chip], label=f"{chip} EEG")
    ax[2].plot(clock, P[:, k[f"{p}/{b+1}"]], "-", lw=.9, color=COL[chip],
               label=f"{chip} EMG" + ("  (OPEN, implant side)" if chip in ("A1", "B2") else ""))
ax[0].axhline(T.FLOOR_MIN_HUM_UV, color="k", ls="--", lw=1)
ax[0].text(clock[2], T.FLOOR_MIN_HUM_UV * 1.04, f"QC ground gate {T.FLOOR_MIN_HUM_UV:.0f} uV: below = UNJUDGEABLE", fontsize=8)
ax[0].set_yscale("log"); ax[0].set_ylabel("chip floor, 60 Hz line\n(uV peak, gate scale)")
ax[0].set_title(f"Wire-free floor of each chip. Dots: median of the 14 inputs in one 10 s epoch every {STEP / 60:g} min; line: half-hour median of the dots.\n"
                "Legend: the gate's own value (core/criteria.py: median over ALL epochs x inputs; differs from the dots when the inputs split in two groups, e.g. A1)",
                loc="left", fontsize=8.5)
ax[1].set_ylabel("EEG 60 Hz line (uV peak)"); ax[1].set_ylim(0, None)
ax[1].set_title("EEG hum: small and flat all night", loc="left", fontsize=10)
ax[2].set_yscale("log"); ax[2].set_ylabel("EMG 60 Hz line (uV peak)")
a2e = P[:, k["A/34"]]
ax[2].set_title(f"EMG hum: A2 carries {np.percentile(a2e, 5):.0f}-{np.percentile(a2e, 95):.0f} uV (5th-95th percentile; the size of its quiet "
                "muscle tone, see C3); A1/B2 EMG are open inputs", loc="left", fontsize=10)
for a in ax:
    a.axvline(LON, color="goldenrod", lw=1.2); a.legend(fontsize=7.5, ncol=4, loc="upper left"); a.grid(alpha=.25)
ax[1].text(LON, ax[1].get_ylim()[1] * .55, f"lights ON {LON:%H:%M:%S} ", ha="right", fontsize=8, color="goldenrod")
import matplotlib.dates as mdates
ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M")); ax[2].set_xlabel("clock time, 2026-10-01 21:00 -> 10-02 09:02 KST (lights OFF 21:00)")
fig.suptitle("Overnight 2026-10-01/02, 4 mice (A1 A2 B1 B2): hum and chip floors are steady, no slow ground decay", fontsize=11)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "2026-10-02-noise-figA-overnight-trend.png"), dpi=110); plt.close(fig)

# ---------------------------------------------------------------- fig B: lights-ON event
t_ev = (LON - rec.t0).total_seconds(); a = int((t_ev - 12) * rec.fs); n = 24 * rec.fs
X = rec.read(a, n).T
Dc = rec.fs // 20                                                 # 50 ms comb: nulls 60 Hz and every (folded) harmonic
Y = sg.sosfiltfilt(sg.butter(4, [1, 450], btype="band", fs=rec.fs, output="sos"), X[:, Dc:] - X[:, :-Dc], axis=1)
tt_e = np.arange(Y.shape[1]) / rec.fs + (t_ev - 12) + Dc / rec.fs - t_ev
traces = [(f"{c} floor\n(median of 14)", np.median(Y[[rec.ix[s_] for s_ in floor_sites(*CHIPS[c])]], 0), COL[c]) for c in CHIPS]
traces += [(f"{c} {role}", Y[rec.ix[f"{CHIPS[c][0]}/{CHIPS[c][1] + kk}"]], COL[c])
           for c in ("A2", "B1", "A1", "B2") for role, kk in (("EEG", 0), ("EMG", 1)) if not (c in ("A1", "B2") and role == "EMG")]
fig, ax = plt.subplots(len(traces), 2, figsize=(13, 13), sharex="col", gridspec_kw=dict(width_ratios=[2.2, 1]))
for r, (lab, y, c) in enumerate(traces):
    for col, (lo, hi) in enumerate(((-10, 10), (-.3, .8))):
        m = (tt_e > lo) & (tt_e < hi)
        ax[r, col].plot(tt_e[m], y[m], lw=.6 if col == 0 else .9, color=c)
        ax[r, col].axvline(0, color="goldenrod", lw=.8, ls=":"); ax[r, col].tick_params(labelsize=7)
        if col == 0:
            ax[r, col].set_ylabel(lab + "\nuV", fontsize=8)
        pk = np.abs(y[(tt_e > -.2) & (tt_e < .8)]).max()
        if col == 1:
            ax[r, col].text(.98, .9, f"peak {pk:.0f} uV", transform=ax[r, col].transAxes, ha="right", va="top", fontsize=7)
ax[0, 0].set_title("20 s around the light timer (each row on its own scale)", loc="left", fontsize=9)
ax[0, 1].set_title("zoom: the same instant on every chip", loc="left", fontsize=9)
ax[-1, 0].set_xlabel(f"s from the all-chip event, {LON:%H:%M:%S.%f}"[:-5] + " (file clock)"); ax[-1, 1].set_xlabel("s from the event")
fig.suptitle("Lights-ON 2026-10-02: the night's largest system-wide event, the only one above 5x on all four chips' floors\n"
             "50 ms comb + 1-450 Hz (removes mains and every harmonic; each transient also leaves an inverted copy 50 ms later). "
             "B2's floor bursts before it are its own chip (open EMG), not system-wide.", fontsize=9.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "2026-10-02-noise-figB-lights-on-event.png"), dpi=105); plt.close(fig)

# ---------------------------------------------------------------- fig C: per-site floors, B1 vs B2 vs A2
S = {}
for r in rows_site:
    S[(r["run"], r["site"])] = r["floor_gate_uV"]
cmp_runs = [("10-01 16:29 direct again", "16:29 no mice, B boards ON (before the refit)", "k", "o"),
            ("10-01 19:50 4 mice", "19:50 boards refitted, mice on", "tab:green", "s"),
            ("overnight 21:00-09:02", f"overnight median (every {STEP / 60:g} min)", "tab:orange", "D")]
fig, ax = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
for a_, chip in zip(ax, ("B1", "B2", "A2")):
    p, b = CHIPS[chip]; sites = floor_sites(p, b); x = np.arange(len(sites))
    for j, (run, lab, c, m) in enumerate(cmp_runs):
        a_.plot(x + (j - 1) * .18, [S[(run, s)] for s in sites], m, color=c, ms=5, label=lab, ls="none")
    a_.set_xticks(x); a_.set_xticklabels([s.split("/")[1] for s in sites], fontsize=8)
    a_.axhline(T.FLOOR_MIN_HUM_UV, color="k", ls="--", lw=.8); a_.set_yscale("log"); a_.grid(alpha=.25)
    pre = np.array([S[(cmp_runs[0][0], s_)] for s_ in sites]); post = np.array([S[(cmp_runs[2][0], s_)] for s_ in sites])
    rr = post / pre; d5 = [s_.split("/")[1] for s_, v_ in zip(sites, rr) if v_ <= .2]
    a_.set_title(f"{chip}" + {"B1": " (board refitted)", "B2": " (board refitted)", "A2": " (board NOT touched)"}[chip]
                 + f": {len(d5)}/14 inputs drop >=5x" + (f" (/{' /'.join(d5)})" if d5 else "")
                 + f"\nchip floor {np.median(pre):.0f} -> {np.median(post):.0f} uV, median input ratio {np.median(rr):.2f}",
                 loc="left", fontsize=9)
    a_.set_xlabel(f"wire-free input ({p}/...)")
ax[0].set_ylabel("60 Hz line on the input (uV peak, gate scale)"); ax[0].legend(fontsize=8, loc="lower left")
fig.suptitle("Per-input floors, 16:29 (no mice) vs after the B boards were refitted AND the mice connected (both changed, so they cannot be separated).\n"
             "B1's chip floor falls under 800 because several of its inputs collapse while others do not move: site-specific, not a weak ground "
             "(which would scale the whole chip)", fontsize=9.5)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "2026-10-02-noise-figC-B1-site-floors.png"), dpi=110); plt.close(fig)

# ---------------------------------------------------------------- fig D: chip floor per recording vs the gate
fig, ax = plt.subplots(figsize=(13, 5.6))
labels = [lab for lab, _, _ in RUNS]
for i, (label, base, state) in enumerate(RUNS):
    for j, chip in enumerate(CHIPS):
        r = next(r for r in rows_chip if r["run"] == label.replace("\n", " ") and r["chip"] == chip)
        if state == "mice":
            face = COL[chip] if chip in ("A2", "B1") else "white"     # filled = working EEG + EMG; open = EEG only
            mk = "o"
        elif state == "Boff" and chip in ("B1", "B2"):
            face, mk = "white", "v"
        else:
            face, mk = "white", "s"
        ax.plot(i + (j - 1.5) * .12, r["floor_gate_uV"], mk, mfc=face, mec=COL[chip], mew=1.4, ms=8,
                label=chip if i == len(RUNS) - 1 else None)
ax.axhline(T.FLOOR_MIN_HUM_UV, color="k", ls="--", lw=1)
ax.text(-.4, T.FLOOR_MIN_HUM_UV * 1.05, f"gate {T.FLOOR_MIN_HUM_UV:.0f} uV: at or above = 'grounded', below = UNJUDGEABLE", fontsize=8)
ax.axhline(2000, color="0.5", ls=":", lw=1); ax.text(-.4, 2000 * 1.05, "2000 uV proposal (falsified 10-01)", fontsize=8, color="0.4")
ax.axvspan(5.5, 9.5, color="tab:green", alpha=.06)
for i_ in (0, 1):                                                  # B1 is the third chip: offset (2 - 1.5) * .12
    r_ = next(r for r in rows_chip if r["run"] == labels[i_].replace("\n", " ") and r["chip"] == "B1")
    ax.annotate("B1 on 09-30: slip-ring wires touched by hand in the\nfirst run (Entry 1); the second run is not explained" if i_ == 0 else "",
                xy=(i_ + .06, r_["floor_gate_uV"]), xytext=(2.2, 420), fontsize=7.5, arrowprops=dict(arrowstyle="->", lw=.7))
ax.set_xticks(range(len(RUNS))); ax.set_xticklabels(labels, fontsize=7.5)
ax.set_yscale("log"); ax.set_ylabel("chip floor, 60 Hz line (uV peak, gate scale)"); ax.grid(alpha=.25, axis="y")
ax.legend(title="chip", fontsize=8, loc="lower left")
ax.set_title("Audit C1: the ground gate measures wiring geometry. Squares = EMPTY headstage (no mouse, no ground) reading 'grounded'; "
             "filled circles = working mouse (A2, B1);\nopen circles = mouse with EEG only (A1, B2: EMG open); triangles = B boards removed. "
             "B1 with a working mouse falls under the line.", loc="left", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "2026-10-02-noise-figD-gate-floor-vs-config.png"), dpi=110); plt.close(fig)
print("figures ->", FIG, "| data ->", DATA)

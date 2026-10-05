"""Figures for the 2026-10-02 post-run chain (no data reads beyond small CSV/log files).

K: qc/emg_mains_staging_test.py over every ~/eeg-processed day folder: r@1min and WAKE %, as published vs EMG notched.
L: system-wide events through the overnight (uid1001-21-00-07) and light-phase (uid1002-09-16-58) runs: events on both ports
   (qc/allchip_scan_file.py, 2026-10-02 rewrite: comb detector, file-level contamination, every port must be hit) and A2-B1 floor coincidences (qc/night_spikes.py), with the rig session and air showers marked.
usage: python3 qc/fullscan_figures_2026_10_02.py FULLSCANS_DIR FIGDIR [MAINS_TEST_ROOT] [OFFICIAL_ROOT]
Every number in a title is computed here. Fig K's method check compares each 'orig' features.json of
qc/emg_mains_staging_test.py (MAINS_TEST_ROOT/orig/<day>/) with the official one in OFFICIAL_ROOT/<day>/.
"""
import csv, json, os, re, sys, datetime as dt
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, matplotlib.dates as mdates

L, FIGD = sys.argv[1], sys.argv[2]
MT = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser("~/radix/noise-tests/2026-10-02/emg-mains-test-all")
OFFI = sys.argv[4] if len(sys.argv) > 4 else os.path.expanduser("~/eeg-processed")
import glob


# ---- K
rows = [l.split() for l in open(os.path.join(L, "emg_mains_all_days.log")) if re.match(r"^20\d\d-", l)]
rows = [r for r in rows if len(r) >= 9]
num = lambda x: float(x) if x not in ("nan", "None") else np.nan
r0, r1 = np.array([num(r[3]) for r in rows]), np.array([num(r[7]) for r in rows])
w0, w1 = np.array([num(r[4]) for r in rows]), np.array([num(r[8]) for r in rows])
s0, s1 = np.array([r[2] == "SCOREABLE" for r in rows]), np.array([r[6] == "SCOREABLE" for r in rows])
cat = [("both SCOREABLE", s0 & s1, "tab:green"), ("REJECT -> SCOREABLE", ~s0 & s1, "tab:orange"),
       ("SCOREABLE -> REJECT", s0 & ~s1, "tab:red"), ("REJECT both", ~s0 & ~s1, "0.6")]
fig, ax = plt.subplots(1, 2, figsize=(13, 5.6))
for name, m, col in cat:
    ax[0].scatter(np.nan_to_num(r0[m], nan=-0.1), np.nan_to_num(r1[m], nan=-0.1), s=22, color=col, label=f"{name} ({m.sum()})")
    ax[1].scatter(w0[m], w1[m], s=22, color=col)
ax[0].axhline(.3, color="k", ls="--", lw=.8); ax[0].axvline(.3, color="k", ls="--", lw=.8); ax[0].plot([-.1, 1], [-.1, 1], color="k", lw=.5)
ax[0].set_xlabel("r@1min as published (nan plotted at -0.1)"); ax[0].set_ylabel("r@1min, EMG notched 60/120 Hz"); ax[0].legend(fontsize=8)
ax[1].plot([0, 100], [0, 100], color="k", lw=.5); ax[1].set_xlabel("WAKE % as published"); ax[1].set_ylabel("WAKE %, EMG notched")
for a in ax: a.grid(alpha=.25)
same = differ = missing = 0
for fo in glob.glob(os.path.join(MT, "orig", "*", "*_features.json")):
    day, name = fo.split(os.sep)[-2], os.path.basename(fo); off = os.path.join(OFFI, day, name)
    if not os.path.exists(off):
        missing += 1; continue
    vo, vf = json.load(open(fo))["verdict"].split(":")[0], json.load(open(off))["verdict"].split(":")[0]
    same, differ = same + (vo == vf), differ + (vo != vf)
up, down = int((~s0 & s1).sum()), int((s0 & ~s1).sum())
print(f"method check: {same}/{same + differ} official verdicts reproduced ({missing} with no official features.json)")
fig.suptitle(f"Stage 3 with the EMG mains notched, every ~/eeg-processed day folder ({len(rows)} animal-recordings; the unnotched run reproduces "
             f"{same}/{same + differ} official verdicts, {missing} without one):\nSCOREABLE {s0.sum()} -> {s1.sum()} ({up} up, {down} down). Diagnostic only, NOT adopted: "
             f"it would re-score published numbers", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(FIGD, "2026-10-02-noise-figK-emg-notch-all-days.png"), dpi=105); plt.close(fig)

# ---- L
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import noise_mice_markers_2026_10_02 as MK
def allchip(fn, run):
    t0 = MK.file_origin(MK.RUNS[run])[0].replace(tzinfo=None)              # t_s is file seconds: exact clock from start_time
    return [(t0 + dt.timedelta(seconds=float(r["t_s"])), int(r["n_chips_hit"]), r["excluded"]) for r in csv.DictReader(open(os.path.join(L, fn)))]
def coinc(fn):                                                              # night_spikes prints on the file's start_time clock
    t = re.findall(r"(\d\d-\d\d \d\d:\d\d:\d\d)\.\d", open(os.path.join(L, fn)).read())
    return [dt.datetime.strptime("2026-" + x, "%Y-%m-%d %H:%M:%S") for x in t]
mk = {run: [dict(r, t=MK.file_origin(MK.RUNS[run])[0].replace(tzinfo=None) + dt.timedelta(seconds=r["file_s"])) for r in MK.rows(run)] for run in MK.RUNS}
visit = [(dt.datetime.fromisoformat(f"2026-10-02 {x}"), dt.datetime.fromisoformat(f"2026-10-02 {y}")) for x, y in (("15:19:00", "16:40:00"),)]
ends = {run: (MK.file_origin(MK.RUNS[run])[0].replace(tzinfo=None),
              MK.file_origin(MK.RUNS[run])[0].replace(tzinfo=None) + dt.timedelta(seconds=MK.file_origin(MK.RUNS[run])[2] / MK.file_origin(MK.RUNS[run])[1])) for run in MK.RUNS}
runs = [("overnight", "overnight uid1001-21-00-07 (10-01 21:00 -> 10-02 09:02)", allchip("allchip_allego_0__uid1001-21-00-07.csv", "overnight"),
         coinc("night_spikes_allego_0__uid1001-21-00-07.log"), []),
        ("lightphase", "light phase uid1002-09-16-58 (10-02 09:17 -> 21:02)", allchip("allchip_allego_0__uid1002-09-16-58.csv", "lightphase"),
         coinc("night_spikes_allego_0__uid1002-09-16-58.log"), visit)]
fig, ax = plt.subplots(2, 1, figsize=(14, 6.5)); txt = []
for a, (run, title, ac, co, spans) in zip(ax, runs):
    for s_, e_ in spans: a.axvspan(s_, e_, color="tab:orange", alpha=.2, label="Andrea at the rig (from the data)")
    a.vlines([t for t, _, _ in ac], 0, [k for _, k, _ in ac], color="tab:blue", lw=1.5, label="system-wide event (both ports; height = voting chips hit)")
    a.plot(co, [4.4] * len(co), "v", color="tab:red", ms=7, label="A2 + B1 floors hit together")
    for r in mk[run]:
        if r["kind"] in ("lights",) or (r["kind"] == "disturbance" and "air shower" in r["event"]):
            a.axvline(r["t"], color="k", ls=":", lw=1)
            a.text(r["t"], 4.7, " lights" if r["kind"] == "lights" else "", fontsize=8, va="top")
    a.set_xlim(*ends[run]); a.set_ylim(0, 5); a.set_ylabel("voting chips hit"); a.set_title(title, loc="left", fontsize=9.5)
    a.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M")); a.grid(alpha=.25); a.legend(fontsize=7.5, loc="upper left")
    inv = lambda t: any(s_ <= t < e_ for s_, e_ in spans)
    lights = [t for t, _, _ in ac if any(abs((t - r["t"]).total_seconds()) < 2 for r in mk[run] if r["kind"] == "lights")]
    out = sorted({t.replace(microsecond=0) for t, _, _ in ac if not inv(t) and t not in lights})
    cx = [t for t in co if not inv(t) and not any(abs((t - L_).total_seconds()) < 2 for L_ in lights)]
    txt.append(f"{run}: {len(ac)} system-wide events ({sum(inv(t) for t, _, _ in ac)} in the visit, {len(lights)} = lights"
               + (f"; others {', '.join(f'{t:%H:%M:%S}' for t in out)}" if out else "; no others")
               + f"); A2+B1 floor coincidences outside the visit and the lights: {len(cx)}" + (f" ({', '.join(f'{t:%H:%M:%S}' for t in cx)})" if cx else ""))
print("\n".join(txt))
import textwrap
fig.suptitle(textwrap.fill("System-wide events over both runs, full resolution. " + ". ".join(txt) + ". Dotted = lights and air showers.", 170), fontsize=9.5)
fig.tight_layout(); fig.savefig(os.path.join(FIGD, "2026-10-02-noise-figL-system-events-both-runs.png"), dpi=105); plt.close(fig)
print("K + L written")

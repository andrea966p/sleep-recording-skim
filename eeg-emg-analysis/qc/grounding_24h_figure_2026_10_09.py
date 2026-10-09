"""Fig R of the noise series: the same 4 mice over 24 h before (10-01/02) and after (10-07/08) the grounding fix.

usage: python3 qc/grounding_24h_figure_2026_10_09.py OUT.png
Inputs (all already on disk, no raw read):
  ~/radix/noise-tests/2026-10-09/out/hourly_hum_before_after.csv   (qc/hourly_hum_bundle.py, QC-bundle hum per hour)
  ~/radix/noise-tests/2026-10-02/analysis-24h/hourly.csv            (before: wake % per hour, stage 3 as published)
  ~/radix/noise-tests/2026-10-09/diag-emgtest/orig/2026-10-07/      (after: stage 3 as published, --all-verdicts split)
x = hours from lights-OFF (21:00 = 0). Shaded = dark phase. Wake % = WAKE share of in-block 4 s epochs per clock hour.
"""
import csv, glob, os, sys, datetime as dt
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

BEFORE_C, AFTER_C = "#2a78d6", "#eb6834"
H = os.path.expanduser("~/radix/noise-tests")
rows = list(csv.DictReader(open(f"{H}/2026-10-09/out/hourly_hum_before_after.csv")))
OFF = {"before": dt.datetime(2026, 10, 1, 21), "after": dt.datetime(2026, 10, 7, 21)}


def cond(r):
    return "after" if "1007" in r["run"] else "before"


def x_of(c, hour_start):
    return (dt.datetime.strptime(hour_start, "%Y-%m-%d %H:%M") - OFF[c]).total_seconds() / 3600 + 0.5


def series(key):
    out = {}
    for c in ("before", "after"):
        rr = [r for r in rows if cond(r) == c]
        out[c] = (np.array([x_of(c, r["hour_start_kst"]) for r in rr]), np.array([float(r[key]) for r in rr]))
    return out


def wake_after(pos):
    h = glob.glob(f"{H}/2026-10-09/diag-emgtest/orig/2026-10-07/{pos}_*_hypnogram.csv")[0]
    t0 = dt.datetime(2026, 10, 7, 15, 28, 38, 649000)
    acc = {}
    for r in csv.DictReader(open(h)):
        if r["in_block"] not in ("1", "True", "true"):
            continue
        t = t0 + dt.timedelta(seconds=float(r["t_s"]) + 2)
        k = t.replace(minute=0, second=0, microsecond=0)
        a = acc.setdefault(k, [0, 0]); a[0] += r["state"] == "WAKE"; a[1] += 1
    ks = sorted(k for k in acc if acc[k][1] >= 150)                       # >= 10 min of in-block epochs
    return (np.array([(k - OFF["after"]).total_seconds() / 3600 + 0.5 for k in ks]),
            np.array([100 * acc[k][0] / acc[k][1] for k in ks]))


def wake_before(mouse):
    rr = [r for r in csv.DictReader(open(f"{H}/2026-10-02/analysis-24h/hourly.csv"))
          if r["mouse"] == mouse and r["wake_pct_orig"] not in ("", None)]
    return (np.array([x_of("before", r["hour_start_kst"]) for r in rr]), np.array([float(r["wake_pct_orig"]) for r in rr]))


fig, ax = plt.subplots(3, 2, figsize=(14, 10.5), sharex=True, constrained_layout=True)
panels = [(0, 0, "A2_floor", "A2 chip floor, 60 Hz (µV, log)", True), (0, 1, "B1_floor", "B1 chip floor, 60 Hz (µV, log)", True),
          (1, 0, "A2_emg60", "A2 EMG, 60 Hz (µV, log)", True), (1, 1, "B1_emg60", "B1 EMG, 60 Hz (µV, log)", True)]
for r_, c_, key, title, logy in panels:
    a = ax[r_, c_]; S = series(key)
    for c, col in (("before", BEFORE_C), ("after", AFTER_C)):
        a.plot(*S[c], color=col, lw=2, marker="o", ms=4, label=f"{c} (10-0{1 if c == 'before' else 7}/0{2 if c == 'before' else 8})")
    if logy:
        a.set_yscale("log")
    a.set_title(title, fontsize=11)
for c_, (mouse, pos) in enumerate((("A2", "portA-slot2"), ("B1", "portB-slot1"))):
    a = ax[2, c_]
    a.plot(*wake_before(mouse), color=BEFORE_C, lw=2, marker="o", ms=4, label="before")
    a.plot(*wake_after(pos), color=AFTER_C, lw=2, marker="o", ms=4, label="after")
    a.set_title(f"{mouse} wake % per hour, scoring as published (no notch)", fontsize=11); a.set_ylim(0, 100)
for a in ax.flat:
    a.axvspan(0, 12, color="#e9e8e4", zorder=0); a.grid(True, color="#e4e3df", lw=0.6)
    a.set_xlim(-6.5, 24.5); a.set_xticks(range(-6, 25, 3))
    a.set_xticklabels([f"{(21 + h) % 24:02d}:00" for h in range(-6, 25, 3)], fontsize=9)
ax[0, 0].legend(frameon=False, fontsize=9, loc="center left")
ax[2, 0].set_xlabel("clock time (shaded = lights off, 21:00-09:00)"); ax[2, 1].set_xlabel("clock time (shaded = lights off, 21:00-09:00)")
fig.suptitle("Same 4 mice, 24 h before (blue, 10-01/02) vs after (orange, 10-07/08) the grounding fix. Hourly medians from the QC bundles.",
             fontsize=12)
fig.savefig(sys.argv[1], dpi=110)
print("wrote", sys.argv[1])

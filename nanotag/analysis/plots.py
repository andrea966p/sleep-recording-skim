#!/usr/bin/env python3
"""Figures for the nanotag sleep/activity analysis. Reads the .nta CSV exports
directly and reuses the scoring in nta_qc.py. Writes PNG + PDF into figs/.

    ../.venv/bin/python plots.py "<data dir>"/*_trial.csv
"""
import os, sys, statistics as st
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nta_qc import (parse, rebin, sleep_score, bouts, merge_wake, is_light,
                    LIGHTS_ON, LIGHTS_OFF, SKIP_FIRST_MIN, SLEEP_MIN_BINS)

MERGE = 2          # bridge wake gaps <= 2 bins (24 s); see bout-merging table
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
COL = ["#1f77b4", "#d62728"]

def load(path):
    """-> (name, hdr, act, temp) with the handling window dropped"""
    hdr, act, temp = parse(path)
    cut = act[0][0] + timedelta(minutes=SKIP_FIRST_MIN)
    name = os.path.basename(path).replace("_trial.csv", "").split("_", 1)[1]
    return name, hdr, [x for x in act if x[0] >= cut], [x for x in temp if x[0] >= cut]

def shade_dark(ax, t0, t1):
    """Grey out the dark phases across the axis span."""
    d = t0.replace(hour=0, minute=0, second=0)
    while d < t1 + timedelta(days=1):
        a, b = d.replace(hour=LIGHTS_OFF), d.replace(hour=LIGHTS_ON) + timedelta(days=1)
        ax.axvspan(max(a, t0), min(b, t1), color="0.85", lw=0, zorder=0)
        # the dark phase before the first lights-on, too
        a2, b2 = d - timedelta(days=1) + timedelta(hours=LIGHTS_OFF), d.replace(hour=LIGHTS_ON)
        ax.axvspan(max(a2, t0), min(b2, t1), color="0.85", lw=0, zorder=0)
        d += timedelta(days=1)
    ax.set_xlim(t0, t1)
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d\n%H:%M"))

def phase_split(pairs):
    return ([x for x in pairs if is_light(x[0])], [x for x in pairs if not is_light(x[0])])

def save(fig, stem):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/{stem}.{ext}", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT}/{stem}.png")

# ---------------------------------------------------------------- figures
def fig_actogram(data):
    fig, axes = plt.subplots(len(data), 1, figsize=(11, 2.1 * len(data)),
                             sharex=True, sharey=True)
    for ax, (name, hdr, act, temp) in zip(np.atleast_1d(axes), data):
        one = [(t, v) for t, v, ok in rebin(act, hdr["act_res"], 1) if ok]
        shade_dark(ax, act[0][0], act[-1][0])
        # fill_between, not bar: ~1900 bars over 32 h alias into fake tall spikes
        ax.fill_between([t for t, _ in one], [v for _, v in one],
                        step="mid", color=COL[0], lw=0)
        ax.set_ylabel(f"{name}\ncross count / min")
        ax.margins(y=0)
    np.atleast_1d(axes)[-1].set_xlabel("date / clock time  (grey = dark phase, lights off 21:00)")
    fig.suptitle("Activity actogram, 1-min bins", y=0.99)
    save(fig, "fig1_actogram")

def fig_sleep(data):
    fig = plt.figure(figsize=(11, 8.5))
    gs = fig.add_gridspec(4, 2, height_ratios=[1.1, 1.1, 1.9, 1.9], hspace=0.55, wspace=0.25)

    # (a) sleep raster, one strip per animal
    for i, (name, hdr, act, temp) in enumerate(data):
        ax = fig.add_subplot(gs[i, :])
        sc = merge_wake(sleep_score(act, SLEEP_MIN_BINS), MERGE)
        arr = np.array([[s for _, s in sc]], dtype=float)
        t0, t1 = mdates.date2num(sc[0][0]), mdates.date2num(sc[-1][0])
        # antialiased, not nearest: ~9700 bins into ~1300 px, so let matplotlib
        # area-average -- grey level then reads as local sleep density
        ax.imshow(arr, aspect="auto", cmap="Greys", vmin=0, vmax=1,
                  extent=[t0, t1, 0, 1], interpolation="antialiased")
        ax.set_yticks([]); ax.set_ylabel(name, rotation=0, ha="right", va="center")
        ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d\n%H:%M"))
        for x in (LIGHTS_ON, LIGHTS_OFF):
            d = sc[0][0].replace(hour=0, minute=0, second=0)
            while d < sc[-1][0] + timedelta(days=1):
                ax.axvline(d.replace(hour=x), color="tab:orange", lw=1.2)
                d += timedelta(days=1)
        ax.set_xlim(t0, t1)          # axvline above widens the limits otherwise
        if i == 0:
            ax.set_xticklabels([])
            ax.set_title(f"(a) sleep raster, black = asleep  (IDS >={SLEEP_MIN_BINS*hdr['act_res']}s, "
                         f"wake gaps <={MERGE*hdr['act_res']}s bridged); orange = lights on/off")

    # (b) hourly % asleep
    ax = fig.add_subplot(gs[2, 0])
    for i, (name, hdr, act, temp) in enumerate(data):
        sc = merge_wake(sleep_score(act, SLEEP_MIN_BINS), MERGE)
        hrs, pct = [], []
        for h in list(range(LIGHTS_ON, 24)) + list(range(0, LIGHTS_ON)):
            sel = [s for t, s in sc if t.hour == h]
            if sel:
                hrs.append(len(hrs)); pct.append(100 * sum(sel) / len(sel))
        ax.plot(hrs, pct, "o-", color=COL[i], label=name, ms=4)
    ax.axvspan(LIGHTS_OFF - LIGHTS_ON - 0.5, 23.5, color="0.85", lw=0, zorder=0)
    ax.set_xticks(range(0, 24, 3))
    ax.set_xticklabels([f"{(LIGHTS_ON+h)%24:02d}" for h in range(0, 24, 3)])
    ax.set_xlabel("hour of day (from lights on)"); ax.set_ylabel("% of bins asleep")
    ax.set_ylim(0, 100); ax.legend(frameon=False, fontsize=8)
    ax.set_title("(b) hourly sleep profile", fontsize=10)

    # (c) sleep bout duration survival, light vs dark
    ax = fig.add_subplot(gs[2, 1])
    for i, (name, hdr, act, temp) in enumerate(data):
        sc = merge_wake(sleep_score(act, SLEEP_MIN_BINS), MERGE)
        for ph, sel, ls in (("light", phase_split(sc)[0], "-"), ("dark", phase_split(sc)[1], "--")):
            b = sorted(n * hdr["act_res"] / 60 for _, n in bouts(sel, True))
            if b:
                ax.step(b, 100 * (1 - np.arange(len(b)) / len(b)), ls,
                        color=COL[i], lw=1.4, label=f"{name} {ph}")
    ax.set_xscale("log"); ax.set_xlabel("sleep bout duration (min)")
    ax.set_ylabel("% of bouts longer"); ax.legend(frameon=False, fontsize=7)
    ax.set_title("(c) bout duration survival", fontsize=10)

    # (d) between-animal synchrony, 30-min % asleep
    ax = fig.add_subplot(gs[3, :])
    series = []
    for i, (name, hdr, act, temp) in enumerate(data):
        sc = dict(merge_wake(sleep_score(act, SLEEP_MIN_BINS), MERGE))
        w = int(30 * 60 / hdr["act_res"])
        ks = sorted(sc)
        t = [ks[j] for j in range(0, len(ks) - w + 1, w)]
        v = [100 * sum(sc[x] for x in ks[j:j + w]) / w for j in range(0, len(ks) - w + 1, w)]
        series.append((t, v))
        ax.plot(t, v, "o-", color=COL[i], ms=3, lw=1.3, label=name)
    shade_dark(ax, series[0][0][0], series[0][0][-1])
    n = min(len(series[0][1]), len(series[1][1]))
    r = np.corrcoef(series[0][1][:n], series[1][1][:n])[0, 1]
    ax.set_ylabel("% asleep / 30 min"); ax.set_ylim(0, 100)
    ax.set_xlabel("date / clock time")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    ax.set_title(f"(d) the two animals co-vary in real time:  r = {r:.3f}  (30-min bins, "
                 f"n={n}) -- shared disturbance, not a clock-locked rhythm", fontsize=10)
    save(fig, "fig2_sleep")

def fig_temp(data):
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), width_ratios=[2.4, 1])
    ax = axes[0]
    for i, (name, hdr, act, temp) in enumerate(data):
        ax.plot([t for t, _ in temp], [v for _, v in temp], "-", color=COL[i], lw=1, label=name)
    shade_dark(ax, data[0][2][0][0], data[0][2][-1][0])
    ax.set_ylabel("tag case temp (degC)"); ax.set_xlabel("date / clock time")
    ax.legend(frameon=False, fontsize=8)
    ax.set_title("tag temperature, 5-min samples (subcutaneous flank, not core)", fontsize=10)

    ax = axes[1]
    box, labs = [], []
    for i, (name, hdr, act, temp) in enumerate(data):
        sc = dict(merge_wake(sleep_score(act, SLEEP_MIN_BINS), MERGE))
        for lab, want in (("asleep", True), ("awake", False)):
            box.append([v for t, v in temp if sc.get(t) is want])
            labs.append(f"{name}\n{lab}")
    bp = ax.boxplot(box, tick_labels=labs, widths=0.6, patch_artist=True, showfliers=False)
    for p, c in zip(bp["boxes"], [COL[0], COL[0], COL[1], COL[1]]):
        p.set_facecolor(c); p.set_alpha(0.45)
    ax.set_ylabel("degC"); ax.tick_params(labelsize=8)
    ax.set_title("temp by scored state", fontsize=10)
    save(fig, "fig3_temperature")

if __name__ == "__main__":
    data = [load(p) for p in sys.argv[1:]]
    if not data:
        raise SystemExit(__doc__)
    fig_actogram(data)
    fig_temp(data)
    if len(data) == 2:
        fig_sleep(data)
    else:
        print("  skipped fig2 panel (d): needs exactly 2 animals")

#!/usr/bin/env python3
"""HLBNSL cohort (NS-SL SOD1 vs NW-SL water): sleep amounts per mouse, plus a
check on whether the tag temperature channel is worth keeping.

    /usr/bin/python3 nanotag/analysis/cohort.py ~/Desktop/Andrea/nanotag/"nanotag recording data/HLBNSL"

Reads every nanotagViewer CSV export in the FOLDERS below: the homecage
baseline, and the treatment period as Run 1 + Run 2 merged (2026-10-05, user:
"merge as a whole, excluding the handling windows"). Each file is scored with
nta_qc (Pack immobility-defined sleep) on its own contiguous series, the
EXCLUDE windows are removed, and the files of one mouse and period are then
joined. Writes tables + figures to analysis/out/HLBNSL/.
"""
import csv, itertools, os, re, sys, statistics as st
from collections import defaultdict
from datetime import date, datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nta_qc import (parse, gaps, sleep_score, merge_wake, bouts, is_light,
                    LIGHTS_ON, SLEEP_MIN_BINS)

# --- cohort facts, from HLB_SOD1_Intake_Monitoring_SDSLNANO (Drive), read 2026-09-28, 10-05
SOD1 = {41, 42, 43, 44, 49}                  # NS-SL: SOD1 6.8 U/mL in drinking water
WATER = {45, 46, 47, 48, 50}                 # NW-SL: UV-sterilised water
SURGERY = {**{m: date(2026, 9, 11) for m in SOD1 | WATER},
           49: date(2026, 9, 1), 50: date(2026, 9, 1)}
NOTE = {}
# nanotag ID (last 5 digits of the header's "nanotag ID") -> mouse. The mouse is
# taken from the tag, not the file name: every Run 2 file is named HLBNSSL_<n>,
# the water mice 45-48 and 50 included.
TAG = {20641: 41, 20645: 42, 20643: 43, 20646: 44, 20640: 49,
       20639: 45, 20648: 46, 20644: 47, 20647: 48, 20642: 50}
# data subfolder -> (period, run). Run 1 stopped itself at the 8-day memory limit
# (09-20 10:00 -> 09-28 08:59:48); Run 2 was started at the tag read, 09-28 10:00
# (SOD1 mice) / 11:00 (water mice), and ran past sampling.
FOLDERS = {"260917_HLBNSSL_homecage_baseline": ("baseline", 0),
           "260917_HLBNWSL_homecage_baseline": ("baseline", 0),
           "260927_HLBNSSL_8days_part1": ("treatment", 1),
           "260917_HLBNWSL_8days_part1": ("treatment", 1),
           "261002_HLBNSSL": ("treatment", 2)}
# HLBNSSL43 died 2026-09-28 during restraint for the tag read; user: discard all
# of its data. Part 1 is therefore n=4 SOD1 vs n=5 water.
DROP = {43}
# 49 and 50 have a 1-day baseline only (09-15). User: leave them out of the
# baseline and judge baseline group differences on the 3-day mice. They stay in
# the treatment period; their change-from-baseline is therefore undefined and skipped.
SHORT_BASELINE = {49, 50}
# Mice handled or out of the recording room. Rule: whole room, first logged
# start rounded down to the hour, last logged end rounded up (user, 2026-10-05).
# Source: NANOTAG behavioral tab, read 2026-10-05.
EXCLUDE = [
           # Tag read 2026-09-28 (user, 2026-09-28): logged reads 08:30 (41) to 09:10
           # (46); 47/48/50 logged "PM Session" but their .nta files were saved by
           # 09:59-10:36, so read in the morning; 43 died ~10:00. Covers
           # the end of Run 1 (08:45-08:59:48) and the first hour of Run 2 in the
           # SOD1 mice (10:00-11:00); the water mice's Run 2 starts at 11:00.
           (datetime(2026, 9, 28, 8, 45), datetime(2026, 9, 28, 11, 0), "tag read (NFC) + 43 died; first Run 2 hour of SOD1 mice"),
           # handling-habituation sessions, all mice in the room (NANOTAG behavioral
           # tab): 09-26 first 14:14 (41), last ended 15:56 (48); 09-27 first 16:00
           # (41), last ended 17:25 (50). Only these windows are removed; the rest
           # of both days is kept (user, 2026-10-01).
           (datetime(2026, 9, 26, 14, 0), datetime(2026, 9, 26, 16, 0), "handling habituation Day -4"),
           (datetime(2026, 9, 27, 16, 0), datetime(2026, 9, 27, 18, 0), "handling habituation Day -3"),
           # Day -1 handling, 16:03 (41) to 17:15 (50)
           (datetime(2026, 9, 29, 16, 0), datetime(2026, 9, 29, 18, 0), "handling habituation Day -1"),
           # Day 0 Y-maze: all cages in the test room 14:00-17:00
           (datetime(2026, 9, 30, 14, 0), datetime(2026, 9, 30, 17, 0), "Day 0 Y-maze, cages in test room"),
           # Day 1 NOR habituation: test room from 14:00, back at 17:25
           (datetime(2026, 10, 1, 14, 0), datetime(2026, 10, 1, 18, 0), "Day 1 NOR habituation, cages in test room"),
           # Day 2: test room from 14:00, NOR T1/T2, then sampling. Everything
           # after is cut, including the post-mortem tail the tags kept logging
           # (temperature out of range from ~19:45).
           (datetime(2026, 10, 2, 14, 0), datetime(2026, 10, 3, 9, 0), "Day 2 NOR test + sampling; post-mortem tail")]
# Tag site: implanted s.c. at the neck, pushed right, migrated to the right
# dorsolateral flank in every mouse. Threshold 170 is Kissei's mouse-neck value,
# not validated for the flank: counts are relative units within this study.
# Daily handling habituation began 2026-09-26 in both groups. Its sessions are
# removed via EXCLUDE; the days themselves count like any other. Kept only to
# flag those days in the per-day table.
HANDLING_FROM = date(2026, 9, 26)
# Test days (ZT dates): their windows are removed, the rest of each day is kept
# and flagged in the per-day table.
TEST_DAYS = {date(2026, 9, 30), date(2026, 10, 1), date(2026, 10, 2)}
# A light or dark phase with less recorded time than this is left out of the
# means (only the 5 h stub of 10-02 falls under it; every other phase has >= 8 h).
MIN_PHASE_H = 6
# Start of SOD1 administration (6.8 U/mL in drinking water; the water group got
# its UV-water bottle at the same time): intake grids Day 1 = 2026-09-17, bottles
# placed 14:00-17:00 (user, 2026-09-29). It falls in the unrecorded gap between
# baseline and Run 1. The treatment period (09-20 10:00 -> 10-02 14:00) is 2.8 to
# 15.0 days after the start: treatment days 3-15.
SOD1_START = (datetime(2026, 9, 17, 14), datetime(2026, 9, 17, 17))
DAYS = "3–15"
LIQ = "#7c3aed"      # marker colour, distinct from both group colours
MERGE = 2            # bridge wake gaps <= 2 bins (24 s) for bout statistics only
K = SLEEP_MIN_BINS   # 4 bins = 48 s immobility

GCOL = {"SOD1": "#c2410c", "water": "#1d4ed8"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "HLBNSL")
FMT = "%Y-%m-%d %H:%M"

def group(m):
    return "SOD1" if m in SOD1 else "water"

def zt_day(ts):
    """ZT0 = lights on. A ZT day runs 09:00 -> 09:00 next morning."""
    return (ts - timedelta(hours=LIGHTS_ON)).date()

# ------------------------------------------------------------------ loading
def excluded(t):
    return any(a <= t < b for a, b, _ in EXCLUDE)

def files(folder):
    """-> [(period, run, mouse, path, (hdr, act, temp))] for every export in FOLDERS"""
    out = []
    for sub, (period, run) in FOLDERS.items():
        d = os.path.join(folder, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(x for x in os.listdir(d) if x.endswith(".csv")):
            hdr, act, temp = parse(os.path.join(d, f))
            mouse = TAG[int(hdr["nanotag ID"][-5:])]
            assert int(re.search(r"(\d+)(_bas)?\.csv$", f).group(1)) == mouse, f"{f}: name vs tag ID"
            assert not gaps(act, hdr["act_res"]), f"{f}: activity gaps, sleep_score assumes none"
            out.append((period, run, mouse, os.path.join(d, f), (hdr, act, temp)))
    return out

def load(folder):
    """Score each file on its own contiguous series, drop the EXCLUDE windows,
    then join a mouse's files per period. Bout and IV code below split at the
    resulting holes."""
    recs = {}
    for period, run, mouse, path, (hdr, act, temp) in files(folder):
        if mouse in DROP:
            continue
        r = recs.setdefault((mouse, period), dict(
            mouse=mouse, group=group(mouse), period=period, files=[], hdr=hdr,
            act=[], temp=[], scored=[]))
        assert r["hdr"]["act_res"] == hdr["act_res"] and r["hdr"]["temp_res"] == hdr["temp_res"]
        r["files"].append(os.path.basename(path))
        r["act"] += [x for x in act if not excluded(x[0])]
        r["temp"] += [x for x in temp if not excluded(x[0])]
        r["scored"] += [x for x in sleep_score(act, K) if not excluded(x[0])]
    for r in recs.values():
        for k in ("act", "temp", "scored"):
            r[k].sort()
        print(f"  {r['mouse']} {r['period']:9s} {r['act'][0][0]} -> {r['act'][-1][0]}  "
              f"{len(r['act'])} bins  {' + '.join(r['files'])}")
    return sorted(recs.values(), key=lambda r: (r["period"], r["mouse"]))

# ------------------------------------------------------------------ sleep tables
def daily_rows(r):
    """one row per ZT day: sleep % and minutes in light and dark"""
    res = r["hdr"]["act_res"] / 60
    acc = defaultdict(lambda: [0, 0, 0, 0, 0, 0])   # light n, sleep, counts, dark n, sleep, counts
    counts = dict(r["act"])
    for ts, s in r["scored"]:
        o = 0 if is_light(ts) else 3
        a = acc[zt_day(ts)]
        a[o] += 1; a[o + 1] += s; a[o + 2] += counts[ts]
    rows = []
    need = MIN_PHASE_H * 3600 / r["hdr"]["act_res"]
    for i, (d, (ln, ls, lc, dn, ds, dc)) in enumerate(sorted(acc.items()), 1):
        lp = 100 * ls / ln if ln >= need else float("nan")
        dp = 100 * ds / dn if dn >= need else float("nan")
        rows.append(dict(mouse=r["mouse"], group=r["group"], period=r["period"],
                         zt_date=d.isoformat(), day=i,
                         days_post_surgery=(d - SURGERY[r["mouse"]]).days,
                         handling=int(d >= HANDLING_FROM), test_day=int(d in TEST_DAYS),
                         light_rec_min=round(ln * res), dark_rec_min=round(dn * res),
                         light_sleep_pct=round(lp, 2), dark_sleep_pct=round(dp, 2),
                         # normalised to a full 12 h phase so a clipped first day is comparable
                         light_sleep_min=round(lp * 7.2, 1), dark_sleep_min=round(dp * 7.2, 1),
                         total_sleep_min=round((lp + dp) * 7.2, 1),
                         light_counts=lc, dark_counts=dc))
    return rows

def phase_bouts(r):
    """merged sleep bout lengths (min) per phase, split at every ZT-day/phase
    boundary and at every removed window, so a bout never joins across a gap"""
    res = r["hdr"]["act_res"] / 60
    step = timedelta(seconds=r["hdr"]["act_res"])
    seg, piece, prev = defaultdict(list), 0, None
    for ts, s in merge_wake(r["scored"], MERGE):
        if prev is not None and ts - prev > step:
            piece += 1                       # hole from an EXCLUDE window
        prev = ts
        seg[(zt_day(ts), is_light(ts), piece)].append((ts, s))
    out = {True: [], False: []}
    hours = {True: 0.0, False: 0.0}
    for (d, light, _), x in seg.items():
        out[light] += [n * res for _, n in bouts(x, True)]
        hours[light] += len(x) * res / 60
    return out, hours

def mean(xs):
    """mean over the phases that met MIN_PHASE_H (NaN = too little recorded)"""
    return st.mean(x for x in xs if x == x)

def summarise(recs, days):
    rows = []
    for r in recs:
        dd = [d for d in days if d["mouse"] == r["mouse"] and d["period"] == r["period"]]
        b, h = phase_bouts(r)
        rows.append(dict(
            mouse=r["mouse"], group=r["group"], period=r["period"], n_days=len(dd),
            light_sleep_pct=round(mean(d["light_sleep_pct"] for d in dd), 2),
            dark_sleep_pct=round(mean(d["dark_sleep_pct"] for d in dd), 2),
            total_sleep_min_per_day=round(mean(d["total_sleep_min"] for d in dd), 1),
            light_bout_mean_min=round(st.mean(b[True]), 2),
            dark_bout_mean_min=round(st.mean(b[False]), 2),
            light_bouts_per_h=round(len(b[True]) / h[True], 2),
            dark_bouts_per_h=round(len(b[False]) / h[False], 2),
            **rhythm(r),
            # k=2 (24 s) is the Nagai et al. 2020 nanotag criterion, 12 s bins
            total_sleep_k2_24s=sleep_k(r, 2),
            total_sleep_k3_36s=sleep_k(r, 3), total_sleep_k5_60s=sleep_k(r, 5),
            note=NOTE.get(r["mouse"], "")))
    return rows

def rhythm(r):
    """Nonparametric actigraphy rhythm metrics (van Someren et al. 1999,
    Chronobiol Int 16:505) on hourly cross-count sums; hours cut by a removed
    window are dropped.
    IS = day-to-day stability of the 24 h pattern (0-1), IV = hour-to-hour
    fragmentation (0 ~ smooth, 2 ~ noise), RA = (M10-L5)/(M10+L5); M10/L5 =
    most active 10 h / least active 5 h of the mean 24 h profile, given as ZT
    of window start."""
    tot, n = defaultdict(int), defaultdict(int)
    for ts, c in r["act"]:
        h = ts.replace(minute=0, second=0)
        tot[h] += c; n[h] += 1
    full = 3600 // r["hdr"]["act_res"]
    hs = sorted(h for h in tot if n[h] == full)
    x = np.array([tot[h] for h in hs], float)
    zt = np.array([(h.hour - LIGHTS_ON) % 24 for h in hs])
    prof = np.array([x[zt == z].mean() for z in range(24)])
    # IV only from truly consecutive hours, never across a removed window
    consec = np.array([(b - a) == timedelta(hours=1) for a, b in zip(hs, hs[1:])])
    iv = np.mean(np.diff(x)[consec] ** 2) / x.var()
    win = lambda w: [prof[np.arange(z, z + w) % 24].mean() for z in range(24)]
    m10, l5 = win(10), win(5)
    M, L = max(m10), min(l5)
    light, dark = prof[:12].mean(), prof[12:].mean()
    return dict(counts_per_h_light=round(light), counts_per_h_dark=round(dark),
                dark_activity_fraction=round(dark / (light + dark), 3),
                IS=round(prof.var() / x.var(), 3), IV=round(iv, 3),
                RA=round((M - L) / (M + L), 3),
                M10_start_ZT=int(np.argmax(m10)), L5_start_ZT=int(np.argmin(l5)))

def sleep_k(r, k):
    """total sleep min/day for an alternative immobility cutoff.
    ponytail: rescored on the masked series, so an immobile run cut by a removed
    window counts from its remaining part; cutoff sensitivity only."""
    sel = [s for t, s in sleep_score(r["act"], k)]
    return round(1440 * sum(sel) / len(sel), 1)

def perm_p(a, b):
    """exact two-sided permutation test on the difference of means"""
    obs = abs(st.mean(a) - st.mean(b))
    pool, n = a + b, len(a)
    hits = tot = 0
    for idx in itertools.combinations(range(len(pool)), n):
        x = [pool[i] for i in idx]
        y = [pool[i] for i in range(len(pool)) if i not in idx]
        hits += abs(st.mean(x) - st.mean(y)) >= obs - 1e-12
        tot += 1
    return hits / tot

# ------------------------------------------------------------------ temperature
def temp_fit(r):
    """Predict each 5-min temperature from the activity of the preceding ~15 min
    (exponential memory; best fit among 5-120 min) with a straight line.
    -> (times, 5-min activity, measured T, predicted T). The share of T's
    variance the prediction captures (R²) says how much of the temperature
    channel is just a lagged copy of activity."""
    res = timedelta(seconds=r["hdr"]["temp_res"])
    step = r["hdr"]["temp_res"] // r["hdr"]["act_res"]
    blk, nb = defaultdict(int), defaultdict(int)
    t0 = r["temp"][0][0]
    for ts, c in r["act"]:
        k = t0 + (ts - t0) // res * res
        blk[k] += c; nb[k] += 1
    # ponytail: the smoother below runs across the holes; its ~15 min memory
    # barely reaches past the edge of a removed window.
    temp = [(t, v) for t, v in r["temp"] if nb[t] == step]
    n = len(temp)
    a5 = np.array([blk[t] for t, _ in temp], float)
    T = np.array([v for _, v in temp])
    s = np.empty(n); s[0] = a5[0]
    for i in range(1, n):
        s[i] = s[i - 1] + (a5[i] - s[i - 1]) / 3
    X = np.c_[np.ones(n), s]
    beta = np.linalg.lstsq(X, T, rcond=None)[0]
    return [t for t, _ in temp], a5, T, X @ beta

def temp_check(r):
    """how much of the 5-min tag temperature is explained by recent activity"""
    t, a5, T, pred = temp_fit(r)
    resid = T - pred
    light = np.array([is_light(x) for x in t])
    return dict(mouse=r["mouse"], group=r["group"], period=r["period"],
                mean_C=round(T.mean(), 2), min_C=round(T.min(), 2), max_C=round(T.max(), 2),
                light_C=round(T[light].mean(), 2), dark_C=round(T[~light].mean(), 2),
                dark_minus_light_C=round(T[~light].mean() - T[light].mean(), 2),
                r2_from_activity=round(1 - resid.var() / T.var(), 2),
                resid_sd_C=round(resid.std(), 2),
                resid_dark_minus_light_C=round(resid[~light].mean() - resid[light].mean(), 2),
                missing=0)

# ------------------------------------------------------------------ figures
def save(fig, stem):
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/{stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT}/{stem}.png")

def mice():
    return sorted(SOD1 - DROP) + sorted(WATER - DROP)

def fig_actograms(recs):
    """Single-plotted: one 24 h row per day, starting at lights on, 10-min bins.
    Baseline and treatment share one calendar so the gap between them shows.
    Double plotting is for drifting rhythms (free-run, phase shifts); these
    mice are entrained to 12:12 LD, so each day once reads more plainly."""
    fig, axes = plt.subplots(2, 5, figsize=(16, 9), sharex=True)
    first = min(zt_day(r["act"][0][0]) for r in recs)
    last = max(zt_day(r["act"][-1][0]) for r in recs)
    nrow = (last - first).days + 1
    for ax in axes.flat[len(mice()):]:
        ax.axis("off")
    for ax, m in zip(axes.flat, mice()):
        bins = defaultdict(int)
        for r in recs:
            if r["mouse"] == m:
                for ts, c in r["act"]:
                    bins[ts.replace(minute=ts.minute // 10 * 10, second=0)] += c
        top = np.percentile(list(bins.values()), 99) or 1
        for row in range(nrow):
            day = first + timedelta(days=row)
            t0 = datetime.combine(day, datetime.min.time()) + timedelta(hours=LIGHTS_ON)
            xs = np.arange(0, 24, 1 / 6)
            ys = np.array([bins.get(t0 + timedelta(hours=float(x)), np.nan) for x in xs])
            y0 = nrow - row - 1
            ax.fill_between(xs, y0, y0 + 0.9 * np.clip(np.nan_to_num(ys) / top, 0, 1),
                            step="post", color=GCOL[group(m)], lw=0)
            for wa, wb, _ in EXCLUDE:               # removed windows: hatched, so a blank is not read as rest
                a, b = ((t - t0).total_seconds() / 3600 for t in (wa, wb))
                if a < 24 and b > 0:             # clipped to this row: 09-28 08:45-11:00 spans two
                    ax.fill_between([max(a, 0), min(b, 24)], y0, y0 + 0.9, facecolor="none",
                                    edgecolor="0.45", hatch="////", lw=0)
            if day == zt_day(SOD1_START[0]):
                a, b = ((t - t0).total_seconds() / 3600 for t in SOD1_START)
                ax.fill_between([a, b], y0 - 0.05, y0 + 0.95, color=LIQ, alpha=0.45, lw=0)
                ax.plot((a + b) / 2, y0 + 0.95, marker="v", color=LIQ, ms=7)
        ax.axvspan(12, 24, color="0.88", lw=0, zorder=0)
        ax.set_yticks([nrow - i - 0.55 for i in range(nrow)])
        ax.set_yticklabels([(first + timedelta(days=i)).strftime("%m-%d") for i in range(nrow)],
                           fontsize=6.5)
        ax.set_xticks([0, 6, 12, 18, 24]); ax.set_xlim(0, 24); ax.set_ylim(0, nrow)
        ax.set_title(f"{m}  {group(m)}" + ("  (1-day baseline)" if m in SHORT_BASELINE else ""),
                     fontsize=10, color="0.1")
    fig.supxlabel("hours from lights on (09:00 = ZT0; lights off at ZT12)", y=0.04)
    fig.suptitle("Actograms, 10-min cross counts, one day per row (grey = dark; violet ▼ = start of SOD1, "
                 "or water bottle in the water group, 09-17 14:00-17:00;\nhatched = removed "
                 "(handling 09-26, 09-27, 09-29; tag read 09-28; tests 09-30, 10-01; 10-02 from 14:00); "
                 "mouse 43 excluded)", y=0.995)
    save(fig, "fig1_actograms")

def fig_daily(days):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharex=True)
    keys = (("total_sleep_min", "total sleep (min / 24 h)"),
            ("light_sleep_pct", "light phase % asleep"),
            ("dark_sleep_pct", "dark phase % asleep"))
    for ax, (k, lab) in zip(axes, keys):
        for m in mice():
            dd = [d for d in days if d["mouse"] == m]
            for per in ("baseline", "treatment"):
                x = [date.fromisoformat(d["zt_date"]) for d in dd if d["period"] == per]
                y = [d[k] for d in dd if d["period"] == per]
                ax.plot(x, y, "-", color=GCOL[group(m)], alpha=0.35, lw=1,
                        marker="x" if m in NOTE else "o", ms=3)
        for g in ("SOD1", "water"):
            for per in ("baseline", "treatment"):
                by = defaultdict(list)
                for d in days:
                    if d["group"] == g and d["period"] == per and d[k] == d[k]:
                        by[d["zt_date"]].append(d[k])
                if by:
                    x = sorted(by)
                    mu = [st.mean(by[i]) for i in x]
                    se = [st.stdev(by[i]) / len(by[i]) ** .5 if len(by[i]) > 1 else 0 for i in x]
                    xd = [date.fromisoformat(i) for i in x]
                    ax.errorbar(xd, mu, se, color=GCOL[g], lw=2.2, capsize=2,
                                label=g if per == "treatment" else None)
        # x is the ZT day's date, so a clock time maps to date + (hours after 09:00)
        a, b = (t - timedelta(hours=LIGHTS_ON) for t in SOD1_START)
        ax.axvspan(a, b, color=LIQ, alpha=0.6, lw=0)
        ax.axvline(a, color=LIQ, ls="--", lw=1)
        ax.text(b, 0.98, " SOD1 start\n 09-17", color=LIQ, fontsize=8, va="top",
                transform=ax.get_xaxis_transform())
        ax.set_ylabel(lab); ax.tick_params(axis="x", labelrotation=45, labelsize=8)
    axes[0].legend(frameon=False, title="group mean ± SEM", loc="lower right")
    fig.suptitle("Daily sleep per mouse (thin) and group (thick); handling, tag-read and test windows "
                 f"removed; phases with < {MIN_PHASE_H} h recorded not plotted", y=1.01)
    fig.tight_layout()
    save(fig, "fig2_daily_sleep")

def fig_zt(recs):
    """Hourly % asleep across the 24 h day, group mean ± SEM, one panel per period.
    Lines, so the axis is the natural 0-100 % scale rather than bars from 0."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True, layout="constrained")
    for ax, per, ttl in ((axes[0], "baseline", "Baseline, pre-treatment (surgery day +3 to +6)"),
                         (axes[1], "treatment", f"Treatment days {DAYS}")):
        for g in ("SOD1", "water"):
            prof = []
            for r in recs:
                if r["group"] != g or r["period"] != per:
                    continue
                h = defaultdict(list)
                for ts, sl in r["scored"]:
                    h[(ts.hour - LIGHTS_ON) % 24].append(sl)
                prof.append([100 * st.mean(h[z]) for z in range(24)])
            p = np.array(prof)
            mu, se = p.mean(0), p.std(0, ddof=1) / len(p) ** .5
            ax.fill_between(range(24), mu - se, mu + se, color=GCOL[g], alpha=0.15, lw=0)
            ax.plot(range(24), mu, "-", color=GCOL[g], lw=2, marker="o", ms=5, mec="white", mew=1,
                    label=f"{g} (n = {len(p)})")
        ax.axvspan(11.5, 23.5, color="0.93", lw=0, zorder=0)
        ax.text(17.5, 97, "dark", ha="center", va="top", fontsize=9, color="0.4")
        ax.set_xticks(range(0, 24, 3)); ax.set_xlim(-0.5, 23.5); ax.set_ylim(0, 100)
        ax.set_xlabel("ZT (h after lights on, 09:00)", fontsize=9.5, color="0.2")
        ax.set_title(ttl, loc="left", fontsize=10.5, color="0.1")
        ax.legend(frameon=False, fontsize=9, loc="lower left")
        style(ax)
    axes[0].set_ylabel("% of hour asleep (mean ± SEM)", fontsize=9.5, color="0.2")
    fig.suptitle("Sleep across the day, SOD1 vs water", x=0.01, ha="left", fontsize=12, color="0.1")
    save(fig, "fig3_zt_profile")

SLEEP_KEYS = (("total_sleep_min_per_day", "total sleep (min/day)"),
              ("light_sleep_pct", "light % asleep"), ("dark_sleep_pct", "dark % asleep"),
              ("light_bout_mean_min", "light bout mean (min)"),
              ("dark_bout_mean_min", "dark bout mean (min)"))
RHYTHM_KEYS = (("counts_per_h_dark", "dark activity (counts/h)"),
               ("dark_activity_fraction", "fraction of activity in dark"),
               ("IS", "interdaily stability"), ("IV", "intradaily variability"),
               ("RA", "relative amplitude"), ("M10_start_ZT", "M10 onset (ZT)"))

def style(ax):
    """Recessive chrome: hairline solid y-grid, no top/right spines, muted ticks."""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("0.7"); ax.spines[side].set_linewidth(0.8)
    ax.yaxis.grid(True, color="0.9", lw=0.8); ax.set_axisbelow(True)
    ax.tick_params(colors="0.3", labelsize=9)

def stars(p):
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."

# (key, panel title, y-limits). Bounded measures get their full scale and the
# rest start at 0, so a group difference is drawn at its true size instead of
# being zoomed into the spread between mice.
COMPARE_SLEEP = (("total_sleep_min_per_day", "Total sleep (min/day)", (0, None)),
                 ("light_sleep_pct", "Light phase, % of time asleep", (0, 100)),
                 ("dark_sleep_pct", "Dark phase, % of time asleep", (0, 100)),
                 ("light_bout_mean_min", "Light phase, mean sleep bout (min)", (0, None)),
                 ("dark_bout_mean_min", "Dark phase, mean sleep bout (min)", (0, None)))
COMPARE_RHYTHM = (("counts_per_h_light", "Light-phase activity (counts/h)", (0, None)),
                  ("counts_per_h_dark", "Dark-phase activity (counts/h)", (0, None)),
                  ("RA", "Rhythm amplitude (RA, 0–1)", (0, 1)),
                  ("IS", "Day-to-day stability (IS, 0–1)", (0, 1)),
                  ("IV", "Hour-to-hour fragmentation (IV, 0–2)", (0, 2)),
                  ("dark_activity_fraction", "Share of activity in the dark (0–1)", (0, 1)))

PERIODS = (("baseline", "Baseline\n(pre-treatment)"), ("treatment", f"Treatment\n(days {DAYS})"))

def group_panel(ax, rows, k, lab, lo, hi, bars=True):
    """SOD1 vs water for one measure, baseline and treatment side by side.
    bar = mean (or a mean tick when bars=False, for interval scales such as °C
    where a bar from 0 means nothing), whisker = SEM, dots = mice. Bracket =
    exact two-sided permutation test between groups within the period."""
    dx, bw = 0.21, 0.34
    pairs, tops, bots = [], [], []
    for pi, (per, _) in enumerate(PERIODS):
        vals = {}
        for g in ("SOD1", "water"):
            v = [r[k] for r in rows if r["group"] == g and r["period"] == per]
            vals[g] = v
            x = pi + (-dx if g == "SOD1" else dx)
            mu, se = st.mean(v), st.stdev(v) / len(v) ** .5
            if bars:
                ax.bar(x, mu, bw, color=GCOL[g], alpha=0.28, lw=0, zorder=1)
            else:
                ax.plot([x - bw / 2, x + bw / 2], [mu, mu], color=GCOL[g], lw=2.5, zorder=2)
            ax.errorbar(x, mu, se, fmt="none", ecolor="0.2", elinewidth=1.4, capsize=4, zorder=4)
            jit = (np.arange(len(v)) - (len(v) - 1) / 2) * 0.05
            ax.plot(x + jit, sorted(v), "o", color=GCOL[g], ms=6.5, mec="white", mew=1.3, zorder=3)
            tops.append(max(max(v), mu + se)); bots.append(min(min(v), mu - se))
        pairs.append((pi, perm_p(vals["SOD1"], vals["water"]),
                      max(max(x) for x in vals.values()),
                      max(st.mean(x) + st.stdev(x) / len(x) ** .5 for x in vals.values())))
    if lo is None:                                   # interval scale: fit around the data
        pad = (max(tops) - min(bots)) * 0.25
        lo = np.floor((min(bots) - pad) * 2) / 2
    top = hi if hi is not None else lo + (max(tops) - lo) * 1.25
    span = top - lo
    for pi, p, ymax, ysem in pairs:
        yb = max(ymax, ysem) + 0.05 * span
        ax.plot([pi - dx, pi - dx, pi + dx, pi + dx], [yb - 0.02 * span, yb, yb, yb - 0.02 * span],
                color="0.25", lw=1)
        ax.text(pi, yb + 0.012 * span, stars(p), ha="center", va="bottom", fontsize=9.5, color="0.1")
    ax.set_ylim(lo, top)
    ax.set_xticks([0, 1], [lbl for _, lbl in PERIODS])
    ax.set_xlim(-0.6, 1.6)
    ax.set_title(lab, loc="left", fontsize=10.5, color="0.1")
    style(ax)

def group_legend(fig, rows, bars=True):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    n = {(g, per): len([r for r in rows if r["group"] == g and r["period"] == per])
         for g in ("SOD1", "water") for per in ("baseline", "treatment")}
    handles = [Patch(color=GCOL[g], alpha=0.5, label=f"{g} (baseline n = {n[g, 'baseline']}, "
                                                        f"treatment n = {n[g, 'treatment']})")
               for g in ("SOD1", "water")]
    handles += [Line2D([], [], color="0.4", marker="o", ls="", ms=6.5, mec="white", label="one mouse"),
                Line2D([], [], color="0.2", lw=1.4, label="mean ± SEM")]
    fig.legend(handles=handles, loc="outside lower center", ncol=4, frameon=False, fontsize=9.5)

def fig_groups(summ, keys, stem, title):
    """SOD1 vs water, one group_panel per measure (* p<0.05, ** p<0.01, *** p<0.001, n.s.)."""
    ncol = 3
    nrow = -(-len(keys) // ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(12, 3.9 * nrow), layout="constrained")
    for ax, (k, lab, (lo, hi)) in zip(axes.flat, keys):
        group_panel(ax, summ, k, lab, lo, hi)
    for ax in axes.flat[len(keys):]:
        ax.axis("off")
    group_legend(fig, summ)
    fig.suptitle(title, x=0.01, ha="left", fontsize=12, color="0.1")
    save(fig, stem)

COMPARE_CHANGE = (("total_sleep_min_per_day", "Total sleep\n(min/day)"),
                  ("light_sleep_pct", "Light phase\n(% asleep)"),
                  ("dark_sleep_pct", "Dark phase\n(% asleep)"),
                  ("dark_bout_mean_min", "Dark sleep bout\n(min)"),
                  ("counts_per_h_light", "Light activity\n(counts/h)"),
                  ("RA", "Rhythm amplitude\n(RA)"))

def perm_ci(a, b, alpha=0.05):
    """mean(a) - mean(b) with a CI from inverting the exact permutation test: the
    set of shifts d for which (a - d) vs b is not rejected. Same method as every p
    in this analysis, so the CI crosses 0 exactly when p > alpha.
    ponytail: grid search (4001 shifts); fine at n = 3-5, slow for large n."""
    d0 = st.mean(a) - st.mean(b)
    scale = (max(a + b) - min(a + b)) or 1
    grid = np.linspace(d0 - 4 * scale, d0 + 4 * scale, 4001)
    ok = [d for d in grid if perm_p([x - d for x in a], b) > alpha]
    return d0, min(ok), max(ok)

def fig_change(summ):
    """Estimation plot (Cumming layout; Ho et al. 2019, Nat Methods 16:565), one
    column per measure, read top to bottom.
    Top: each mouse's change (treatment - baseline), group mean as a line;
    0 = no change. Bottom, same units: the SOD1 effect = mean change SOD1 - mean
    change water, with the 95% CI from inverting the exact permutation test that
    gives p (so the CI crosses 0 exactly when p > 0.05). Mice without a usable
    baseline (49, 50) have no change and are absent."""
    ch, base = defaultdict(dict), {}
    for k, _ in COMPARE_CHANGE:
        base[k] = st.mean(r[k] for r in summ if r["period"] == "baseline")
        for g in ("SOD1", "water"):
            b = {r["mouse"]: r[k] for r in summ if r["group"] == g and r["period"] == "baseline"}
            t = {r["mouse"]: r[k] for r in summ if r["group"] == g and r["period"] == "treatment"}
            ch[g][k] = [t[m] - b[m] for m in sorted(set(b) & set(t))]
    ncol = len(COMPARE_CHANGE)
    fig, axes = plt.subplots(2, ncol, figsize=(13, 8.2), layout="constrained",
                             gridspec_kw={"height_ratios": [1.15, 1]})
    for c, (k, lab) in enumerate(COMPARE_CHANGE):
        a, b = ch["SOD1"][k], ch["water"][k]
        # ---- top: the mice
        ax = axes[0, c]
        for xi, (g, v) in enumerate((("SOD1", a), ("water", b))):
            jit = (np.arange(len(v)) - (len(v) - 1) / 2) * 0.09
            ax.plot(xi + jit, sorted(v), "o", color=GCOL[g], ms=7, mec="white", mew=1.3, zorder=3)
            ax.plot([xi - 0.28, xi + 0.28], [st.mean(v)] * 2, color=GCOL[g], lw=2.5, zorder=2)
        vals = a + b + [0]
        span = max(vals) - min(vals)
        ax.set_ylim(min(vals) - 0.12 * span, max(vals) + 0.12 * span)
        ax.axhline(0, color="0.35", lw=1, zorder=1)
        ax.set_xticks([0, 1], ["SOD1", "water"]); ax.set_xlim(-0.6, 1.6)
        ax.set_title(lab, loc="left", fontsize=10, color="0.1")
        style(ax); ax.tick_params(labelsize=8.5)
        # ---- bottom: the SOD1 effect, same units
        ax = axes[1, c]
        d, lo, hi = perm_ci(a, b)
        p = perm_p(a, b)
        lim = max(abs(lo), abs(hi)) * 1.15
        ax.axhline(0, color="0.35", lw=1, zorder=1)
        ax.plot([0, 0], [lo, hi], color="0.55", lw=7, solid_capstyle="round", alpha=0.55, zorder=2)
        ax.plot(0, d, "o", color="0.1", ms=9, mec="white", mew=1.5, zorder=3)
        ax.set_title(f"{stars(p)}   (p = {p:.2f})", fontsize=10.5, color="0.1")
        ax.set_xlabel((f"{100 * d / base[k]:+.0f}% of baseline\n95% CI [{100 * lo / base[k]:+.0f}%, "
                       f"{100 * hi / base[k]:+.0f}%]").replace("-", "−"), fontsize=8.5, color="0.3")
        ax.set_ylim(-lim, lim); ax.set_xlim(-1, 1); ax.set_xticks([])
        style(ax); ax.tick_params(labelsize=8.5)
        ax.spines["bottom"].set_visible(False)
    axes[0, 0].set_ylabel("change from baseline\n(treatment − baseline)", fontsize=9.5, color="0.2")
    axes[1, 0].set_ylabel("SOD1 effect\n(SOD1 change − water change)", fontsize=9.5, color="0.2")
    axes[1, 0].text(0.22, 0, "0 = no effect", va="bottom", fontsize=8, color="0.35")
    n = {g: len(ch[g][COMPARE_CHANGE[0][0]]) for g in ("SOD1", "water")}
    fig.suptitle(f"Change from baseline to treatment (top: one dot per mouse, line = group mean; "
                 f"SOD1 n = {n['SOD1']}, water n = {n['water']}) and the SOD1 effect with its 95% CI (bottom)",
                 x=0.01, ha="left", fontsize=11.5, color="0.1")
    save(fig, "fig7_change")

def fig_daily_mean(days):
    """Daily sleep, group mean ± SEM only (the per-mouse version is fig2_daily_sleep)."""
    # Lines, not bars: the axis need not start at 0. Fit it to the plotted
    # means ± SEM with padding, rounded to a clean step, same for both groups.
    keys = (("total_sleep_min", "Total sleep (min/day)", 50),
            ("light_sleep_pct", "Light phase, % of time asleep", 5),
            ("dark_sleep_pct", "Dark phase, % of time asleep", 5))
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.3), layout="constrained", sharex=True)
    for ax, (k, lab, step) in zip(axes, keys):
        ext = []
        a, b = (t - timedelta(hours=LIGHTS_ON) for t in SOD1_START)
        ax.axvspan(a, b, color=LIQ, alpha=0.6, lw=0)
        ax.text(b, 0.03, " SOD1 start", color="0.2", fontsize=8.5, transform=ax.get_xaxis_transform())
        for g, off in (("SOD1", -3), ("water", 3)):      # hours: keep whiskers apart
            for per in ("baseline", "treatment"):
                by = defaultdict(list)
                for d in days:
                    if d["group"] == g and d["period"] == per and d[k] == d[k] and not (
                            d["mouse"] in SHORT_BASELINE and per == "baseline"):
                        by[d["zt_date"]].append(d[k])
                if not by:
                    continue
                xs = sorted(by)
                x = [datetime.combine(date.fromisoformat(i), datetime.min.time()) + timedelta(hours=off)
                     for i in xs]
                mu = [st.mean(by[i]) for i in xs]
                se = [st.stdev(by[i]) / len(by[i]) ** .5 if len(by[i]) > 1 else 0 for i in xs]
                ext += [m - e for m, e in zip(mu, se)] + [m + e for m, e in zip(mu, se)]
                ax.errorbar(x, mu, se, color=GCOL[g], lw=2, marker="o", ms=6, mec="white", mew=1.2,
                            elinewidth=1.2, capsize=0, label=g if per == "treatment" else None)
        pad = (max(ext) - min(ext)) * 0.15
        ax.set_ylim(np.floor((min(ext) - pad) / step) * step, np.ceil((max(ext) + pad) / step) * step)
        ax.set_title(lab, loc="left", fontsize=10.5, color="0.1")
        ax.tick_params(axis="x", labelrotation=45)
        style(ax)
    axes[0].legend(frameon=False, loc="lower right", title="group mean ± SEM", fontsize=9)
    fig.suptitle("Daily sleep by group. Violet = SOD1 start (09-17); gap = no recording; handling, "
                 "tag-read and test windows removed", x=0.01, ha="left", fontsize=12, color="0.1")
    save(fig, "fig2b_daily_sleep_mean")

def fig_temp(recs, tc):
    """(a, b) One mouse, treatment: measured tag temperature against the temperature
    predicted from activity alone, with that activity underneath on its own axis
    (no dual y axis). (c) Temperature across the day by group. (d) Mean tag
    temperature per mouse, SOD1 vs water, dots and mean tick (°C is an interval
    scale, so no bars from 0)."""
    fig = plt.figure(figsize=(13, 9), layout="constrained")
    gs = fig.add_gridspec(3, 2, height_ratios=[1.25, 0.7, 1.35])
    r = next(x for x in recs if x["mouse"] == 45 and x["period"] == "treatment")
    t, a5, T, pred = temp_fit(r)
    r2 = 1 - np.var(T - pred) / np.var(T)
    axT = fig.add_subplot(gs[0, :])
    axA = fig.add_subplot(gs[1, :], sharex=axT)
    for ax in (axT, axA):
        d = zt_day(t[0])
        while d <= zt_day(t[-1]):
            a = datetime.combine(d, datetime.min.time()) + timedelta(hours=LIGHTS_ON + 12)
            ax.axvspan(a, a + timedelta(hours=12), color="0.93", lw=0, zorder=0)
            d += timedelta(days=1)
    axT.plot(t, T, color="#b91c1c", lw=1, label="measured tag temperature")
    axT.plot(t, pred, color="0.15", lw=1.2, alpha=0.8, label="predicted from activity alone")
    axT.set_ylabel("°C", fontsize=9.5, color="0.2")
    axT.set_title(f"(a) Mouse 45, treatment period: temperature predicted from activity alone "
                  f"captures {100 * r2:.0f}% of the temperature variance", loc="left", fontsize=10.5,
                  color="0.1")
    axT.legend(frameon=False, fontsize=9, loc="upper left", ncol=2)
    axA.fill_between(t, 0, a5, color="0.45", step="post", lw=0)
    axA.set_ylabel("counts / 5 min", fontsize=9.5, color="0.2")
    axA.set_title("(b) Activity of the same mouse (grey bands = dark phase)", loc="left", fontsize=10.5,
                  color="0.1")
    axA.set_xlim(t[0], t[-1]); axA.set_ylim(0, None)
    plt.setp(axT.get_xticklabels(), visible=False)
    for ax in (axT, axA):
        style(ax)

    ax = fig.add_subplot(gs[2, 0])
    for g in ("SOD1", "water"):
        prof = []
        for x in recs:
            if x["group"] == g and x["period"] == "treatment":
                h = defaultdict(list)
                for ts, v in x["temp"]:
                    h[(ts.hour - LIGHTS_ON) % 24].append(v)
                prof.append([st.mean(h[z]) for z in range(24)])
        p = np.array(prof)
        mu, se = p.mean(0), p.std(0, ddof=1) / len(p) ** .5
        ax.fill_between(range(24), mu - se, mu + se, color=GCOL[g], alpha=0.15, lw=0)
        ax.plot(range(24), mu, "-", color=GCOL[g], lw=2, marker="o", ms=5, mec="white", mew=1,
                label=f"{g} (n = {len(p)})")
    ax.axvspan(11.5, 23.5, color="0.93", lw=0, zorder=0)
    ax.set_xticks(range(0, 24, 3)); ax.set_xlim(-0.5, 23.5)
    ax.set_xlabel("ZT (h after lights on, 09:00)", fontsize=9.5, color="0.2")
    ax.set_ylabel("°C (mean ± SEM)", fontsize=9.5, color="0.2")
    ax.set_title(f"(c) Tag temperature across the day, treatment days {DAYS}", loc="left", fontsize=10.5,
                 color="0.1")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    style(ax)

    ax = fig.add_subplot(gs[2, 1])
    group_panel(ax, tc, "mean_C", "(d) Mean tag temperature per mouse (°C)", None, None, bars=False)
    fig.suptitle("Tag temperature (inside the tag case, under the skin of the flank; not core temperature)",
                 x=0.01, ha="left", fontsize=12, color="0.1")
    save(fig, "fig5_temperature")

# ------------------------------------------------------------------ main
def write(name, rows):
    with open(f"{OUT}/{name}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"  wrote {OUT}/{name}")

def main(folder):
    os.makedirs(OUT, exist_ok=True)
    all_recs = load(folder)          # actograms show the 1-day baselines of 49 and 50 too
    recs = [r for r in all_recs if not (r["mouse"] in SHORT_BASELINE and r["period"] == "baseline")]
    print(f"loaded {len(recs)} recordings, {len({r['mouse'] for r in recs})} mice")
    days = [row for r in recs for row in daily_rows(r)]
    summ = summarise(recs, days)
    tc = [temp_check(r) for r in recs]
    write("daily_sleep.csv", days)
    write("summary_per_mouse.csv", summ)
    write("temperature_check.csv", tc)

    print(f"\nper-mouse means (handling windows removed), IDS >= {K * 12}s; mean ± SEM, exact permutation p")
    for k in [k for k, _ in SLEEP_KEYS + RHYTHM_KEYS] + [
            "counts_per_h_light", "L5_start_ZT", "light_bouts_per_h", "dark_bouts_per_h",
            "total_sleep_k2_24s", "total_sleep_k3_36s", "total_sleep_k5_60s"]:
        line = f"  {k:26s}"
        for per in ("baseline", "treatment"):
            vs = {g: [s[k] for s in summ if s["group"] == g and s["period"] == per]
                  for g in ("SOD1", "water")}
            for g, v in vs.items():
                line += f" {per[:4]} {g:5s} {st.mean(v):7.4g}±{st.stdev(v) / len(v) ** .5:<6.2g}"
            line += f" p={perm_p(vs['SOD1'], vs['water']):.2f} |"
        dl = {s["mouse"]: s[k] for s in summ if s["period"] == "treatment"}
        db = {s["mouse"]: s[k] for s in summ if s["period"] == "baseline"}
        ch = {m: dl[m] - db[m] for m in dl if m in db}
        a, b = [ch[m] for m in sorted(SOD1) if m in ch], [ch[m] for m in sorted(WATER) if m in ch]
        line += f" change SOD1 {st.mean(a):+7.3g} water {st.mean(b):+7.3g} p={perm_p(a, b):.3f}"
        print(line)

    # Dark-phase sleep climbs once daily handling starts (09-26) and again on the
    # test days, in both groups, so the merged treatment mean blends two regimes.
    # Show them apart: per-mouse means over each subset of ZT days.
    split = []
    for lab, keep in (("undisturbed", 0), ("handling+test", 1)):
        for m in sorted({d["mouse"] for d in days if d["period"] == "treatment"}):
            dd = [d for d in days if d["mouse"] == m and d["period"] == "treatment" and d["handling"] == keep]
            split.append(dict(subset=lab, mouse=m, group=group(m), n_days=len(dd),
                              **{k: round(mean(d[k] for d in dd), 2)
                                 for k in ("total_sleep_min", "light_sleep_pct", "dark_sleep_pct")}))
    write("treatment_split.csv", split)
    print("\ntreatment days split: undisturbed (09-20 to 09-25) vs handling + test (09-26 to 10-01)")
    for lab in ("undisturbed", "handling+test"):
        for k in ("total_sleep_min", "light_sleep_pct", "dark_sleep_pct"):
            vs = {g: [s[k] for s in split if s["subset"] == lab and s["group"] == g] for g in ("SOD1", "water")}
            print(f"  {lab:14s} {k:16s} " + " ".join(
                f"{g} {st.mean(v):7.4g}±{st.stdev(v) / len(v) ** .5:<6.2g}" for g, v in vs.items())
                + f" p={perm_p(vs['SOD1'], vs['water']):.2f}")

    fig_actograms(all_recs)
    fig_daily(days)
    fig_zt(recs)
    fig_daily_mean(days)
    fig_groups(summ, COMPARE_SLEEP, "fig4_summary", "Sleep, SOD1 vs water")
    fig_groups(summ, COMPARE_RHYTHM, "fig6_rhythm", "Activity and daily rhythm, SOD1 vs water")
    fig_change(summ)
    fig_temp(recs, tc)
    export_for_report()

REPORT_ORDER = (("fig2b_daily_sleep_mean", "Figure1_daily_sleep"),
                ("fig3_zt_profile", "Figure2_sleep_across_day"),
                ("fig4_summary", "Figure3_sleep_SOD1_vs_water"),
                ("fig7_change", "Figure4_change_from_baseline"),
                ("fig6_rhythm", "Figure5_rhythm_SOD1_vs_water"),
                ("fig1_actograms", "Figure6_actograms"),
                ("fig5_temperature", "Figure7_temperature"))

def export_for_report():
    """Copy the report's figures under their report numbers, PNG (300 dpi) + PDF."""
    import shutil
    dst = os.path.join(OUT, "figures_for_report")
    os.makedirs(dst, exist_ok=True)
    for src, name in REPORT_ORDER:
        for ext in ("png", "pdf"):
            shutil.copy(f"{OUT}/{src}.{ext}", f"{dst}/{name}.{ext}")
    print(f"  exported {len(REPORT_ORDER)} figures to {dst}")

def demo():
    assert zt_day(datetime(2026, 9, 21, 8, 59)) == date(2026, 9, 20)
    assert zt_day(datetime(2026, 9, 21, 9, 0)) == date(2026, 9, 21)
    assert perm_p([1, 2, 3], [1, 2, 3]) == 1.0
    assert perm_p([10, 11, 12, 13, 14], [0, 1, 2, 3, 4]) == 2 / 252
    t0 = datetime(2026, 9, 1, 9)                     # 3 days, dark (ZT12-24) active
    act = [(t0 + timedelta(seconds=12 * i), 10 if ((i * 12 // 3600) % 24) >= 12 else 0)
           for i in range(3 * 7200)]
    m = rhythm(dict(act=act, hdr={"act_res": 12}))
    assert m["IS"] == 1.0 and m["RA"] == 1.0 and m["dark_activity_fraction"] == 1.0, m
    assert 12 <= m["M10_start_ZT"] <= 14 and m["L5_start_ZT"] <= 7, m
    d, lo, hi = perm_ci([10, 11, 12, 13, 14], [0, 1, 2, 3, 4])     # p = 2/252, CI excludes 0
    assert d == 10 and 0 < lo < 10 < hi, (d, lo, hi)
    d, lo, hi = perm_ci([1, 2, 3], [1, 2, 3])                       # no difference: CI spans 0
    assert lo < 0 < hi
    # 10-02 is cut from 14:00; its 5 h light stub is NaN and left out of the means
    assert excluded(datetime(2026, 10, 2, 20)) and not excluded(datetime(2026, 10, 2, 13, 59, 48))
    t1 = datetime(2026, 10, 2, 9)
    stub = [(t1 + timedelta(seconds=12 * i), 0) for i in range(5 * 300)]
    row = daily_rows(dict(mouse=41, group="SOD1", period="treatment", hdr={"act_res": 12},
                          act=stub, scored=[(t, 1) for t, _ in stub]))[0]
    assert row["light_sleep_pct"] != row["light_sleep_pct"] and mean([1.0, float("nan"), 3.0]) == 2.0
    # temperature pairs with its own 5 min of activity across a removed hour
    act = [(t1 + timedelta(seconds=12 * i), i % 7) for i in range(3 * 300) if not 300 <= i < 600]
    temp = [(t1 + timedelta(minutes=5 * j), 36.0 + j % 3) for j in range(36) if not 12 <= j < 24]
    t, a5, T, _ = temp_fit(dict(hdr={"act_res": 12, "temp_res": 300}, act=act, temp=temp))
    assert len(t) == 24 and t[12] == t1 + timedelta(hours=2) and a5[12] == sum(i % 7 for i in range(600, 625))
    print("demo ok")

if __name__ == "__main__":
    if sys.argv[1:2] == ["--demo"]:
        demo()
    elif len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        raise SystemExit(__doc__)

#!/usr/bin/env python3
"""Lab meeting deck v2 (2026-11-05), section nanotag_ns: nanotag sleep and activity with NORMAL sleep.

    python3 nanotag/analysis/report/labmtg/nanotag_ns.py [HLBNSL data folder] [NS-SD Run 1 folder]

Two cohorts, analysed separately and never pooled:
  HLBNSL  SOD1 41 42 44 49 vs water 45 46 47 48 50 (43 died, dropped); baseline 3 days (49, 50: 1 day, no
          usable baseline, so they are absent from every change-from-baseline value); treatment days 3-15 with
          handling / tag-read / test windows removed (cohort.EXCLUDE).
  NS-SD   Run 1 only: SOD1 51-55 vs water 56-60, baseline 10-22 -> 10-24, SOD1 / water days 1-6, before any SD.

Every number comes from nanotag/analysis/cohort.py (+ cohort_sd.py for NS-SD): sleep = >= 4 consecutive zero-count
12 s bins (>= 48 s immobility), per-mouse means, exact permutation p, 95 % CI by inverting that permutation test.
This script only re-runs those functions on the raw tag exports, checks the result against the existing tables in
nanotag/analysis/out/, and redraws in the deck style (water = blue, left; SOD1 = orange, right).
Writes /home/andrea/hlb_meeting_deck/v2/fig/nanotag_ns_NN_*.png + .pdf and prints every number it shows.
"""
import csv, os, sys, statistics as st
from collections import defaultdict
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from style import *                                    # noqa: F401,F403  (WATER, SOD1, save, sizes, rcParams)
sys.path.insert(0, ANALYSIS)
import numpy as np
import cohort as C                                     # cohort.py sets no rcParams (checked), so the deck style holds
from nta_qc import bouts
from scipy import stats

NSL_DIR = "/home/andrea/Desktop/nanotag data HLBNSSL/nanotag recording data"
NSSD_DIR = "/home/andrea/Desktop/261030_HLBNSSD"
FIG = "/home/andrea/hlb_meeting_deck/v2/fig"
GC = {"water": WATER, "SOD1": SOD1}
SLEEP_SHADE = "#8E7CC3"            # scored sleep: violet, distinct from both group hues
SHOULDER = 59                      # NS-SD water mouse whose tag sits at the shoulder: drawn hollow
# method example: water mouse 45, HLBNSL treatment, an undisturbed late-light-phase window (ZT10-12)
EX_MOUSE, EX_T0, EX_H = 45, datetime(2026, 9, 21, 19), 2
GROUPS = {}                        # cohort -> {mouse: group}, filled in main
M = lambda s: s.replace("-", "−")  # unicode minus for figure text


# ------------------------------------------------------------------ analysis (cohort.py functions)
def run_cohort(load):
    """recs, daily rows, per-mouse summary, as cohort.main / cohort_sd.main build them"""
    recs = load()
    recs = [r for r in recs if not (r["mouse"] in C.SHORT_BASELINE and r["period"] == "baseline")]
    days = [row for r in recs for row in C.daily_rows(r)]
    return recs, days, C.summarise(recs, days)


def check_against(summ, path, tag):
    """every numeric cell of the recomputed summary vs the table already in nanotag/analysis/out/"""
    with open(path) as f:
        old = {(int(r["mouse"]), r["period"]): r for r in csv.DictReader(f)}
    diff = 0
    for r in summ:
        o = old[(r["mouse"], r["period"])]
        for k, v in r.items():
            if isinstance(v, (int, float)) and abs(float(o[k]) - v) > 1e-9:
                diff += 1
                print(f"  DIFF {tag} {r['mouse']} {r['period']} {k}: table {o[k]} vs recomputed {v}")
    print(f"  {tag}: recomputed summary vs {os.path.relpath(path, ANALYSIS)}: {diff} differing cells "
          f"of {len(summ)} rows")


def hourly_profile(recs):
    """{(mouse, period): 24 values of % asleep by ZT hour}, as cohort.fig_zt computes it"""
    out = {}
    for r in recs:
        h = defaultdict(list)
        for ts, s in r["scored"]:
            h[(ts.hour - C.LIGHTS_ON) % 24].append(s)
        out[(r["mouse"], r["period"])] = np.array([100 * st.mean(h[z]) for z in range(24)])
    return out


def hedges(a, b):
    """Hedges g, SOD1 - water (pooled SD, small-sample correction), as meeting_figures.hedges"""
    a, b = np.asarray(a, float), np.asarray(b, float)
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1)) / (n1 + n2 - 2))
    return (a.mean() - b.mean()) / sp * (1 - 3 / (4 * (n1 + n2) - 9))


def mde80(a, b):
    """smallest SOD1 - water difference a two-sample t test would detect with 80 % power at alpha 0.05,
    from the observed pooled SD (sensitivity analysis, approximate at these n)"""
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1 - 1) * np.var(a, ddof=1) + (n2 - 1) * np.var(b, ddof=1)) / (n1 + n2 - 2))
    df = n1 + n2 - 2
    return (stats.t.ppf(0.975, df) + stats.t.ppf(0.80, df)) * sp * np.sqrt(1 / n1 + 1 / n2)


def changes(summ, k):
    """{group: [(mouse, treatment - baseline)]} for the mice with both periods"""
    b = {r["mouse"]: r[k] for r in summ if r["period"] == "baseline"}
    t = {r["mouse"]: r[k] for r in summ if r["period"] == "treatment"}
    grp = {r["mouse"]: r["group"] for r in summ}
    out = {"water": [], "SOD1": []}
    for m in sorted(set(b) & set(t)):
        out[grp[m]].append((m, t[m] - b[m]))
    return out


def estimate(summ, k):
    ch = changes(summ, k)
    a, b = [v for _, v in ch["SOD1"]], [v for _, v in ch["water"]]
    d, lo, hi = C.perm_ci(a, b)
    return dict(ch=ch, d=d, lo=lo, hi=hi, p=C.perm_p(a, b), g=hedges(a, b), mde=mde80(a, b),
                ma=st.mean(a), mb=st.mean(b))


def group_line(summ, k, per):
    vs = {g: [r[k] for r in summ if r["group"] == g and r["period"] == per] for g in ORDER}
    s = "  ".join(f"{g} {st.mean(v):8.4g} ± {st.stdev(v) / len(v) ** .5:<7.3g}(n={len(v)})" for g, v in vs.items())
    return f"{per:9s} {s}  p={C.perm_p(vs['SOD1'], vs['water']):.2f}"


MEASURES = (("total_sleep_min_per_day", "Total sleep", "min/day", 0),
            ("light_sleep_pct", "Light phase asleep", "% points", 1),
            ("dark_sleep_pct", "Dark phase asleep", "% points", 1),
            ("light_bout_mean_min", "Light sleep bout", "min", 1),
            ("dark_bout_mean_min", "Dark sleep bout", "min", 1),
            ("light_bouts_per_h", "Light bouts per h", "/h", 1),
            ("dark_bouts_per_h", "Dark bouts per h", "/h", 1),
            ("counts_per_h_light", "Light activity", "counts/h", 0),
            ("counts_per_h_dark", "Dark activity", "counts/h", 0),
            ("dark_activity_fraction", "Share of activity in dark", "", 3),
            ("RA", "Rhythm amplitude RA", "", 3),
            ("IS", "Interdaily stability IS", "", 3),
            ("IV", "Intradaily variability IV", "", 3),
            ("total_sleep_k2_24s", "Total sleep, 24 s cutoff", "min/day", 0),
            ("total_sleep_k5_60s", "Total sleep, 60 s cutoff", "min/day", 0))


def report(name, summ):
    print(f"\n=== {name}: per-mouse means, group mean ± SEM, exact permutation p; change = treatment - baseline")
    est = {}
    for k, lab, unit, nd in MEASURES:
        e = est[k] = estimate(summ, k)
        print(f"{lab} ({k})")
        for per in ("baseline", "treatment"):
            print("   " + group_line(summ, k, per))
        print(f"   change   water {e['mb']:+.{nd + 1}f}  SOD1 {e['ma']:+.{nd + 1}f}  SOD1 - water {e['d']:+.{nd + 1}f} "
              f"95% CI [{e['lo']:+.{nd + 1}f}, {e['hi']:+.{nd + 1}f}]  p={e['p']:.3f}  Hedges g {e['g']:+.2f}  "
              f"MDE80 ±{e['mde']:.{nd + 1}f}  (n water {len(e['ch']['water'])}, SOD1 {len(e['ch']['SOD1'])})")
        print("   per mouse " + ", ".join(f"{m}:{v:+.{nd + 1}f}" for g in ORDER for m, v in e["ch"][g]))
    return est


# ------------------------------------------------------------------ figure helpers
def shade_dark(ax, a=12, b=24):
    ax.axvspan(a, b, color=DARK_BG, lw=0, zorder=0)


def dots(ax, x, vals, color, mice=(), hollow=None, ms=9):
    jit = (np.arange(len(vals)) - (len(vals) - 1) / 2) * 0.07
    order = np.argsort(vals)
    for j, i in enumerate(order):
        m = mice[i] if mice else None
        open_ = m is not None and m == hollow
        ax.plot(x + jit[j], vals[i], "o", ms=ms, color=color, mfc="white" if open_ else color,
                mec=color if open_ else "white", mew=1.8 if open_ else 1.2, zorder=3)


def change_panel(ax, e, title, unit, nd, hollow=None, ann=True, small=False, show_g=False):
    """water (left) and SOD1 (right) per-mouse change, mean ± SEM; third column = SOD1 - water with 95 % CI"""
    allv = [0, e["lo"], e["hi"]]
    for x, g in enumerate(ORDER):
        ms, v = zip(*e["ch"][g])
        dots(ax, x, list(v), GC[g], list(ms), hollow)
        mu, se = st.mean(v), st.stdev(v) / len(v) ** .5
        ax.errorbar(x + 0.3, mu, se, fmt="_", ms=18, mew=3, color=INK, elinewidth=2, capsize=0, zorder=4)
        allv += list(v)
    ax.axhline(0, color=CHANCE, lw=1.2, zorder=1)
    ax.plot([2.2, 2.2], [e["lo"], e["hi"]], color=INK, lw=3, solid_capstyle="round", zorder=3)
    ax.plot(2.2, e["d"], "D", ms=10, color=INK, mec="white", mew=1.2, zorder=4)
    n = {g: len(e["ch"][g]) for g in ORDER}
    ax.set_xticks([0, 1, 2.2], [f"water\nn={n['water']}", f"SOD1\nn={n['SOD1']}", "SOD1 −\nwater"],
                  fontsize=12 if small else None)
    for t, g in zip(ax.get_xticklabels()[:2], ORDER):
        t.set_color(GC[g]); t.set_fontweight("bold")
    ax.set_xlim(-0.5, 2.6)
    span = max(allv) - min(allv) or 1
    ax.set_ylim(min(allv) - 0.08 * span, max(allv) + (0.42 if ann else 0.1) * span)
    ax.set_title(title, fontsize=15)
    ax.set_ylabel(M(f"change ({unit})") if unit else "change")
    ax.yaxis.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    if ann:
        g = f", g = {e['g']:+.2f}" if show_g else ""
        ax.text(0.98, 0.98, M(f"{e['d']:+.{nd}f} [{e['lo']:+.{nd}f}, {e['hi']:+.{nd}f}]\np = {e['p']:.2f}{g}"),
                transform=ax.transAxes, ha="right", va="top", fontsize=12 if small else 13,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=GRID))


def row_label(fig, ax, text):
    ax.annotate(text, xy=(0, 0.5), xycoords="axes fraction", xytext=(-95, 0), textcoords="offset points",
                rotation=90, ha="center", va="center", fontsize=16, fontweight="bold")


# ------------------------------------------------------------------ 01 method
def fig_method(r):
    sc = [(t, s) for t, s in r["scored"] if EX_T0 <= t < EX_T0 + timedelta(hours=EX_H)]
    act = dict(r["act"])
    t = np.array([(x - EX_T0).total_seconds() / 60 for x, _ in sc])     # minutes
    c = np.array([act[x] for x, _ in sc]); s = np.array([v for _, v in sc])
    # zoom: first short immobile run (2-3 zero bins, scored wake) followed within 15 bins by a >= 8-bin sleep run
    runs, i = [], 0
    while i < len(c):
        j = i
        while j < len(c) and c[j] == 0:
            j += 1
        if j > i:
            runs.append((i, j)); i = j
        else:
            i += 1
    z0 = next(a for (a, b), (a2, b2) in zip(runs, runs[1:]) if 2 <= b - a <= 3 and a2 - b <= 15 and b2 - a2 >= 8
              and a > 5)
    z = slice(z0 - 5, z0 + 35)
    fig, (ax, az) = plt.subplots(2, 1, figsize=(12, 6.2), layout="constrained", gridspec_kw={"height_ratios": [1, 1]})
    for axx, sl, w in ((ax, slice(None), 0.2), (az, z, 0.2)):
        tt, cc, ss = t[sl], c[sl], s[sl]
        for (k, n) in bouts(list(zip(range(len(ss)), ss)), True):
            axx.axvspan(tt[k], tt[k] + n * 0.2, color=SLEEP_SHADE, alpha=0.28, lw=0, zorder=0)
        axx.bar(tt, cc, width=w, align="edge", color=INK, lw=0, zorder=2)
        axx.set_ylabel("counts / 12 s")
        axx.set_ylim(0, max(c) * 1.08 if axx is ax else max(c[z]) * 1.35 + 1)
    ax.set_xlim(0, EX_H * 60)
    ax.set_xticks(range(0, EX_H * 60 + 1, 20),
                  [f"{(EX_T0 + timedelta(minutes=m)):%H:%M}" for m in range(0, EX_H * 60 + 1, 20)])
    ax.axvspan(t[z][0], t[z][-1] + 0.2, fill=False, ec=CHANCE, lw=1.5, ls="--", zorder=3)
    frac = 100 * s.mean()
    ax.set_title(f"(a) Water mouse {EX_MOUSE}, {EX_T0:%m-%d %H:%M}–{EX_T0 + timedelta(hours=EX_H):%H:%M} (ZT10–12): "
                 f"activity per 12 s bin, violet = scored asleep ({frac:.0f} % of the 2 h)", fontsize=14)
    zt = t[z]
    az.set_xlim(zt[0], zt[-1] + 0.2)
    zc, zs = c[z], s[z]
    for k in range(len(zt)):                         # zero bins drawn as squares on the axis
        if zc[k] == 0:
            az.plot(zt[k] + 0.1, 0.02 * az.get_ylim()[1], "s", ms=7, color=SLEEP_SHADE if zs[k] else "white",
                    mec=SLEEP_SHADE if zs[k] else INK, mew=1.2, zorder=4, clip_on=False)
    a, b = runs[[ra for ra, _ in runs].index(z0)]
    az.annotate(f"{b - a} zero bins = {12 * (b - a)} s\n< 48 s → wake", xy=(t[a] + 0.1 * (b - a), 0.06 * az.get_ylim()[1]),
                xytext=(t[a] - 0.2, 0.62 * az.get_ylim()[1]), fontsize=13, ha="center",
                arrowprops=dict(arrowstyle="->", color=INK))
    a2, b2 = next((ra, rb) for ra, rb in runs if ra > z0 and rb - ra >= 8)
    az.annotate(f"{b2 - a2} zero bins ≥ 4 (≥ 48 s)\n→ sleep", xy=(t[a2] + 0.4, 0.06 * az.get_ylim()[1]),
                xytext=(t[a2] + 1.6, 0.62 * az.get_ylim()[1]), fontsize=13, ha="left",
                arrowprops=dict(arrowstyle="->", color=INK))
    az.set_xlabel("clock time (min:s shown as minutes after window start)")
    ticks = np.arange(np.ceil(zt[0]), zt[-1] + 0.2, 1)
    az.set_xticks(ticks, [f"{(EX_T0 + timedelta(minutes=float(m))):%H:%M}" for m in ticks])
    az.set_xlabel("")
    az.set_title("(b) Zoom (dashed box): each bar is one 12 s bin; squares = zero-count bins", fontsize=14)
    save(fig, f"{FIG}/nanotag_ns_01_method")
    print(f"\n01 method: mouse {EX_MOUSE} {EX_T0} + {EX_H} h, {len(sc)} bins, {frac:.1f} % scored asleep, "
          f"max {max(c)} counts/bin; zoom short run {b - a} bins at {sc[a][0]:%H:%M:%S}, "
          f"sleep run {b2 - a2} bins at {sc[a2][0]:%H:%M:%S}")


# ------------------------------------------------------------------ 02 measures
def fig_measures(r, row):
    fig, (ax, ap) = plt.subplots(1, 2, figsize=WIDE, layout="constrained", gridspec_kw={"width_ratios": [1.25, 1]})
    # (a) bouts: 45 min of the example that starts and ends awake, so no bout is cut by the window
    t0, W = EX_T0 + timedelta(minutes=13), 45
    sc = [(t, s) for t, s in r["scored"] if t0 <= t < t0 + timedelta(minutes=W)]
    assert not sc[0][1] and not sc[-1][1], "bout window must start and end awake"
    mg = C.merge_wake(sc, C.MERGE)
    for y, ser, lab in ((1.0, sc, "scored\n(≥ 48 s still)"), (0.0, mg, "sleep bouts\n(wake ≤ 24 s\nbridged)")):
        for k, n in bouts(list(zip(range(len(ser)), [v for _, v in ser])), True):
            ax.broken_barh([(k * 0.2, n * 0.2)], (y - 0.32, 0.64), color=SLEEP_SHADE, alpha=0.9 if y == 0 else 0.45)
            if y == 0:
                ax.text(k * 0.2 + n * 0.1, y, f"{n * 0.2:.1f}", ha="center", va="center", color="white",
                        fontsize=12 if n * 0.2 >= 2 else 10, fontweight="bold", rotation=0 if n * 0.2 >= 2 else 90)
    nb = len(bouts(mg, True))
    ax.set_yticks([1, 0], ["scored\n(≥ 48 s still)", "bouts\n(gaps ≤ 24 s\nbridged)"])
    ax.set_ylim(-0.6, 1.6); ax.set_xlim(0, W)
    ax.set_xticks(range(0, W + 1, 15), [f"{(t0 + timedelta(minutes=m)):%H:%M}" for m in range(0, W + 1, 15)])
    ax.set_title(f"(a) Sleep bouts, mouse {EX_MOUSE}, {W} min: {nb} bouts (length, min)", fontsize=14)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    # (b) mean 24 h activity profile of the same mouse (treatment), M10 / L5 as cohort.rhythm
    tot, n = defaultdict(int), defaultdict(int)
    for ts, c in r["act"]:
        h = ts.replace(minute=0, second=0); tot[h] += c; n[h] += 1
    hs = sorted(h for h in tot if n[h] == 3600 // r["hdr"]["act_res"])
    x = np.array([tot[h] for h in hs], float)
    zt = np.array([(h.hour - C.LIGHTS_ON) % 24 for h in hs])
    prof = np.array([x[zt == z].mean() for z in range(24)])
    shade_dark(ap)
    ap.bar(np.arange(24) + 0.5, prof, width=0.85, color=WATER, lw=0, zorder=2)
    m10, l5 = row["M10_start_ZT"], row["L5_start_ZT"]
    for s0, w, lab, yy in ((m10, 10, "M10", 1.07), (l5, 5, "L5", 1.07)):
        ap.plot([s0, s0 + w], [yy * prof.max()] * 2, color=INK, lw=3, solid_capstyle="butt", clip_on=False)
        ap.text(s0 + w / 2, yy * prof.max() * 1.02, lab, ha="center", va="bottom", fontsize=13, fontweight="bold")
    ap.set_xlim(0, 24); ap.set_xticks([0, 6, 12, 18, 24]); ap.set_xlabel("ZT (h after lights on, 09:00)")
    ap.set_ylabel("counts / h"); ap.set_ylim(0, prof.max() * 1.22)
    ap.set_title(f"(b) Mean 24 h activity, mouse {EX_MOUSE}", fontsize=14)
    ap.text(0.3, prof.max() * 0.8, f"RA = (M10 − L5) / (M10 + L5)\n     = {row['RA']:.3f}", fontsize=13)
    save(fig, f"{FIG}/nanotag_ns_02_measures")
    print(f"\n02 measures: mouse {EX_MOUSE} treatment, {W} min from {t0:%H:%M}: {len(bouts(sc, True))} scored runs, "
          f"{nb} bouts after bridging, lengths " + ", ".join(f"{n * 0.2:.1f}" for _, n in bouts(mg, True)) + f" min; M10 start ZT{m10}, L5 start ZT{l5}, RA {row['RA']}, IS {row['IS']}, "
          f"IV {row['IV']}, light {row['counts_per_h_light']} / dark {row['counts_per_h_dark']} counts/h, "
          f"dark fraction {row['dark_activity_fraction']}")


# ------------------------------------------------------------------ 03 24 h profile
def fig_profile(cohorts):
    fig, axes = plt.subplots(2, 2, figsize=TALL, layout="constrained", sharex=True, sharey=True)
    print("\n03 profile: % asleep by ZT hour, group mean; light ZT0-11 / dark ZT12-23 means")
    for i, (name, sub, recs, prof) in enumerate(cohorts):
        for j, g in enumerate(ORDER):
            ax = axes[i, j]
            shade_dark(ax)
            for per, col, ls, lab in (("baseline", CHANCE, "--", "baseline"), ("treatment", GC[g], "-", f"on {g}")):
                p = np.array([v for (m, pp), v in prof.items() if pp == per and GROUPS[name][m] == g])
                mu, se = p.mean(0), p.std(0, ddof=1) / len(p) ** .5
                xs = np.arange(24) + 0.5
                ax.fill_between(xs, mu - se, mu + se, color=col, alpha=0.2, lw=0)
                ax.plot(xs, mu, ls, color=col, lw=2.6 if per == "treatment" else 2, label=f"{lab} (n={len(p)})")
                print(f"  {name:7s} {g:5s} {per:9s} n={len(p)} light {mu[:12].mean():5.1f} % dark {mu[12:].mean():5.1f} %")
            ax.set_ylim(0, 100); ax.set_xlim(0, 24); ax.set_xticks([0, 6, 12, 18, 24])
            ax.legend(loc="lower left", fontsize=12, handlelength=1.6)
            ax.text(18, 97, "dark", ha="center", va="top", fontsize=13, color="#555555")
            ax.set_title(f"{name}: {g}", color=GC[g], fontsize=15)
            if j == 0:
                ax.set_ylabel("% of hour asleep")
            if i == 1:
                ax.set_xlabel("ZT (h after lights on, 09:00)")
    save(fig, f"{FIG}/nanotag_ns_03_profile")


# ------------------------------------------------------------------ 04-06 change figures
def fig_change(est_by_cohort, keys, stem, size, show_g=False):
    ncol = len(keys)
    fig, axes = plt.subplots(2, ncol, figsize=size, layout="constrained")
    for i, (name, est, hollow) in enumerate(est_by_cohort):
        for j, (k, lab, unit, nd) in enumerate(keys):
            change_panel(axes[i, j], est[k], f"{name}: {lab}" if ncol <= 3 else lab, unit, nd, hollow,
                         small=ncol > 3, show_g=show_g)
            if j:
                axes[i, j].set_ylabel(M(f"change ({unit})") if unit else "")
        if ncol > 3:
            row_label(fig, axes[i, 0], name)
    save(fig, f"{FIG}/{stem}")


# ------------------------------------------------------------------ 07 interpretation
def fig_interpret(days_nsl, est_nsl, est_sd):
    fig, (ax, af) = plt.subplots(1, 2, figsize=WIDE, layout="constrained", gridspec_kw={"width_ratios": [1.35, 1]})
    # (a) HLBNSL dark-phase sleep by ZT day
    ax.axvspan(datetime(2026, 9, 25, 12), datetime(2026, 10, 2, 12),
               color=DARK_BG, lw=0, zorder=0)
    ax.text(datetime(2026, 9, 29), 52, "handling + test days", ha="center", fontsize=13)
    ax.text(datetime(2026, 9, 22, 12), 52, "undisturbed", ha="center", fontsize=13)
    print("\n07a HLBNSL dark-phase % asleep by ZT day, group mean ± SEM")
    for g, off in (("water", -3), ("SOD1", 3)):
        for per in ("baseline", "treatment"):
            by = defaultdict(list)
            for d in days_nsl:
                if d["group"] == g and d["period"] == per and d["dark_sleep_pct"] == d["dark_sleep_pct"]:
                    by[d["zt_date"]].append(d["dark_sleep_pct"])
            xs = sorted(by)
            x = [datetime.combine(date.fromisoformat(i), datetime.min.time()) + timedelta(hours=off) for i in xs]
            mu = [st.mean(by[i]) for i in xs]
            se = [st.stdev(by[i]) / len(by[i]) ** .5 for i in xs]
            ax.errorbar(x, mu, se, color=GC[g], lw=2.2, marker="o", ms=7, mec="white", capsize=0,
                        label=g if per == "treatment" else None)
            print(f"  {g:5s} {per:9s} " + " ".join(f"{i[5:]}:{m:.1f}" for i, m in zip(xs, mu)))
    ax.set_ylim(0, 56); ax.set_ylabel("dark phase, % asleep")
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%m-%d"))
    ax.xaxis.set_major_locator(mpl.dates.DayLocator(bymonthday=[14, 20, 26, 2]))
    ax.legend(loc="lower left", ncol=2)
    ax.set_title("(a) HLBNSL dark-phase sleep, by day (mean ± SEM)", fontsize=14)
    # (b) what the n can detect: total sleep change, SOD1 - water
    for y, (name, e) in enumerate((("NS-SD\n5 vs 5", est_sd), ("HLBNSL\n3 vs 4", est_nsl))):
        af.fill_betweenx([y - 0.3, y + 0.3], -e["mde"], e["mde"], color=GRID, lw=0)
        af.plot([e["lo"], e["hi"]], [y, y], color=INK, lw=3, solid_capstyle="round")
        af.plot(e["d"], y, "D", ms=11, color=INK, mec="white")
        af.text(e["hi"] + 8, y + 0.12, M(f"{e['d']:+.0f} [{e['lo']:+.0f}, {e['hi']:+.0f}]"), fontsize=13, va="bottom")
        af.text(e["hi"] + 8, y - 0.12, M(f"MDE ±{e['mde']:.0f}"), fontsize=13, va="top", color="#555555")
    for v in (-60, 60):
        af.axvline(v, color=CHANCE, ls="--", lw=1.2)
    af.text(60, 1.55, " 1 h/day", fontsize=12, color="#555555")
    af.axvline(0, color=INK, lw=1)
    af.set_yticks([0, 1], ["NS-SD\n5 vs 5", "HLBNSL\n3 vs 4"]); af.set_ylim(-0.6, 1.8)
    af.set_xlim(-200, 330)
    af.set_xlabel(M("SOD1 − water, change in total sleep (min/day)"))
    af.set_title("(b) What this n can detect", fontsize=14)
    af.spines["left"].set_visible(False); af.tick_params(axis="y", length=0)
    save(fig, f"{FIG}/nanotag_ns_07_interpretation")


# ------------------------------------------------------------------ main
def handling_split(days):
    """treatment days split as cohort.main does (handling flag = ZT date >= 09-26)"""
    print("\nHLBNSL treatment split, per-mouse means: undisturbed 09-20..09-25 vs handling+test 09-26..10-02")
    for lab, keep in (("undisturbed", 0), ("handling+test", 1)):
        for k in ("total_sleep_min", "light_sleep_pct", "dark_sleep_pct"):
            vs = {g: [C.mean(d[k] for d in days if d["mouse"] == m and d["period"] == "treatment"
                             and d["handling"] == keep)
                      for m in sorted({d["mouse"] for d in days if d["group"] == g and d["period"] == "treatment"})]
                  for g in ORDER}
            print(f"  {lab:14s} {k:16s} " + "  ".join(f"{g} {st.mean(v):6.1f} ± {st.stdev(v) / len(v) ** .5:4.1f} "
                                                       f"(n={len(v)})" for g, v in vs.items())
                  + f"  p={C.perm_p(vs['SOD1'], vs['water']):.2f}")


def main(nsl_dir, nssd_dir):
    os.makedirs(FIG, exist_ok=True)
    rc = dict(mpl.rcParams)
    # --- HLBNSL with cohort.py's own facts. On this PC the Run 2 folder is named 261002_HLBNSSL_7days_part2;
    # cohort.py expects 261002_HLBNSSL and skips a missing folder silently (2026-10-31 note), so map it here.
    if not os.path.isdir(os.path.join(nsl_dir, "261002_HLBNSSL")):
        C.FOLDERS["261002_HLBNSSL_7days_part2"] = C.FOLDERS.pop("261002_HLBNSSL")
    print("HLBNSL load")
    recs_nsl, days_nsl, summ_nsl = run_cohort(lambda: C.load(nsl_dir))
    check_against(summ_nsl, os.path.join(ANALYSIS, "out", "HLBNSL", "summary_per_mouse.csv"), "HLBNSL")
    groups_nsl = {r["mouse"]: r["group"] for r in summ_nsl}
    prof_nsl = hourly_profile(recs_nsl)
    ex = next(r for r in recs_nsl if r["mouse"] == EX_MOUSE and r["period"] == "treatment")
    ex_row = next(r for r in summ_nsl if r["mouse"] == EX_MOUSE and r["period"] == "treatment")
    est_nsl = report("HLBNSL (SOD1 41 42 44 [49]; water 45 46 47 48 [50]; 43 dropped)", summ_nsl)
    handling_split(days_nsl)
    fig_method(ex)
    fig_measures(ex, ex_row)

    # --- NS-SD Run 1: importing cohort_sd rewrites cohort.py's globals with the NS-SD facts (HLBNSL is done)
    import cohort_sd as S
    print("\nNS-SD Run 1 load")
    recs_sd, days_sd, summ_sd = run_cohort(lambda: S.load(nssd_dir))
    check_against(summ_sd, os.path.join(ANALYSIS, "out", "HLBNSSD", "summary_per_mouse.csv"), "NS-SD")
    groups_sd = {r["mouse"]: r["group"] for r in summ_sd}
    est_sd = report("NS-SD Run 1 (SOD1 51-55; water 56-60), before SD", summ_sd)
    print("\nNS-SD without 59 (shoulder tag), change SOD1 - water:")
    for k in ("total_sleep_min_per_day", "counts_per_h_dark", "counts_per_h_light"):
        e = estimate([r for r in summ_sd if r["mouse"] != SHOULDER], k)
        print(f"  {k:24s} {e['d']:+.1f} [{e['lo']:+.1f}, {e['hi']:+.1f}] p={e['p']:.3f} g={e['g']:+.2f}")
    assert dict(mpl.rcParams) == rc, "an import changed the matplotlib style"

    GROUPS.update({"HLBNSL": groups_nsl, "NS-SD": groups_sd})
    fig_profile([("HLBNSL", "baseline: SOD1 3, water 4 (3 days); treatment days 3–15, handling/test windows removed",
                  recs_nsl, prof_nsl),
                 ("NS-SD", "baseline 2 days; SOD1 / water days 1–6, before SD", recs_sd, hourly_profile(recs_sd))])
    coh = [("HLBNSL", est_nsl, None), ("NS-SD", est_sd, SHOULDER)]
    fig_change(coh, MEASURES[0:3], "nanotag_ns_04_sleep_change", TALL)
    fig_change(coh, MEASURES[3:7], "nanotag_ns_05_bouts_change", TALL)
    fig_change(coh, (MEASURES[7], MEASURES[8], MEASURES[10]), "nanotag_ns_06_activity_change", TALL, show_g=True)
    fig_interpret(days_nsl, est_nsl["total_sleep_min_per_day"], est_sd["total_sleep_min_per_day"])
    print(f"\nwrote {FIG}/nanotag_ns_0[1-7]_*.png + .pdf")


if __name__ == "__main__":
    main(*(sys.argv[1:3] if len(sys.argv) >= 3 else (NSL_DIR, NSSD_DIR)))

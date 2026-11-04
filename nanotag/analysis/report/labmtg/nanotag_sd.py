#!/usr/bin/env python3
"""Lab meeting deck v2, section nanotag_sd: NS-SD / NW-SD nanotag, sleep deprivation (SD) and recovery.

    python3 nanotag/analysis/report/labmtg/nanotag_sd.py

Cohort HLBNSSD51-55 (SOD1) vs HLBNWSD56-60 (water). Run 1 (10-22 -> 10-30) = baseline + treatment days 1-6;
Run 2 (10-30 19:00 -> 11-04) = undisturbed days 8-10, SD day 1 (11-03 09-15), recovery, SD day 2 (11-04 09:00 ->
own Y-maze). Every window, score and test comes from cohort_sd.py / cohort.py (imported, not rewritten); this
script only draws the deck figures and prints every number they show. Sleep = immobility >= 48 s, 12 s bins.
HLBNWSD59 wears its tag at the shoulder: read its change, not its level (hollow marker everywhere).
Run 2 raw is read from RUN2, a local copy of the NAS folder 02_Data_Sleep/andrea/HLBNSD_raw/261104_HLBNSSD
(10 CSVs; 57 = HLBNSSD_57_2_redone.csv, the corrupted first export left out).
"""
import os, sys, statistics as st
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))           # nanotag/analysis
from style import *                                           # noqa: F401,F403  (shared deck style)
import cohort_sd as SD                                        # sets the NS-SD cohort facts on cohort
C = SD.C
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from scipy import stats, optimize

RUN1 = os.path.expanduser("~/Desktop/261030_HLBNSSD")
RUN2 = "/home/andrea/hlb_meeting_deck/v2/data/261104_HLBNSSD"
FIG = "/home/andrea/hlb_meeting_deck/v2/fig"
NAN = float("nan")
HUE = {"water": WATER, "SOD1": SOD1}
TINT = {"water": WATER_SD, "SOD1": SOD1_SD}
SH = SD.SHOULDER
H = timedelta(hours=1)
# ZT days (09:00 -> 09:00) of normal, undisturbed sleep: baseline, treatment days 1-6, days 8-10
BASE = [date(2026, 10, 22), date(2026, 10, 23)]
DAYS16 = [date(2026, 10, 24) + timedelta(days=i) for i in range(6)]
DAYS810 = [date(2026, 10, 31) + timedelta(days=i) for i in range(3)]
SD1, SD2 = date(2026, 11, 3), date(2026, 11, 4)


def out(name):
    return os.path.join(FIG, f"nanotag_sd_{name}")


def at(d, h):
    """clock hour h on ZT day d (h >= 24 rolls into the next calendar day)"""
    return datetime.combine(d, datetime.min.time()) + timedelta(hours=h)


# ------------------------------------------------------------------ data
def series(recs1, r2):
    """{mouse: (times datetime64, asleep 0/1)}: Run 1 (scored whole, as cohort_sd) then Run 2 (cut at the Y-maze)"""
    ser = {}
    for m in C.mice():
        sc = sorted(x for r in recs1 if r["mouse"] == m for x in r["scored"])
        if r2 and m in r2:
            sc += r2[m][2]
        ser[m] = (np.array([t for t, _ in sc], dtype="datetime64[s]"), np.array([s for _, s in sc], float))
    return ser


def frac(ser, a, b, cover=0.95):
    """% asleep of the 12 s bins in [a, b); NaN if less than 95 % of the window was recorded"""
    T, S = ser
    i, j = np.searchsorted(T, np.datetime64(a)), np.searchsorted(T, np.datetime64(b))
    return 100 * S[i:j].mean() if j - i >= cover * (b - a).total_seconds() / 12 else NAN


def day_table(ser):
    """per mouse and ZT day: % asleep 09-15 (SD hours), minutes asleep 15-21 (ZT6-12), 21-09 (dark), 15-09"""
    rows = []
    for m in C.mice():
        d = date(2026, 10, 22)
        while d <= SD2:
            p915 = frac(ser[m], at(d, 9), at(d, 15))
            z = frac(ser[m], at(d, 15), at(d, 21))
            dk = frac(ser[m], at(d, 21), at(d, 33))
            rows.append(dict(mouse=m, group=C.group(m), day=d, p915=p915, zt612=z * 3.6, dark=dk * 7.2,
                             m1509=z * 3.6 + dk * 7.2))
            d += timedelta(days=1)
    return rows


def dval(dt, m, d, k):
    return next(r[k] for r in dt if r["mouse"] == m and r["day"] == d)


def mde(a, b, power=0.8):
    """smallest true SOD1 - water difference a two-sided t-test (alpha .05) finds with 80 % power at these n,
    in the measure's units (pooled SD x d). An approximation for the exact permutation test used for p."""
    n1, n2 = len(a), len(b)
    sp = (((n1 - 1) * np.var(a, ddof=1) + (n2 - 1) * np.var(b, ddof=1)) / (n1 + n2 - 2)) ** .5
    df, tc = n1 + n2 - 2, stats.t.ppf(0.975, n1 + n2 - 2)
    f = lambda d: (1 - stats.nct.cdf(tc, df, d * (n1 * n2 / (n1 + n2)) ** .5)) - power
    return optimize.brentq(f, 0.01, 10) * sp, optimize.brentq(f, 0.01, 10)


def eff(rows, k, sel=lambda r: True):
    a, b, d, lo, hi, p = SD.effect(rows, k, sel)
    return dict(sod1=a, water=b, d=d, lo=lo, hi=hi, p=p, mde=mde(a, b)[0])


def show(k, e, unit=""):
    f = ".3f" if max(abs(x) for x in e["water"] + e["sod1"]) < 2 else ".1f"          # RA lives in 0-1
    ms = lambda v: f"{st.mean(v):{f}} ± {st.stdev(v) / len(v) ** .5:{f}} (n={len(v)})"
    print(f"  {k:34s} water {ms(e['water'])}  SOD1 {ms(e['sod1'])}  SOD1 − water {e['d']:+{f}} "
          f"[95% CI {e['lo']:+{f}}, {e['hi']:+{f}}] p={e['p']:.3f}  MDE(80%) ±{e['mde']:{f}} {unit}")


# ------------------------------------------------------------------ drawing helpers
def mouse_marker(ax, x, y, g, m, fill, ms=8, z=3):
    """one dot per mouse; 59 hollow (shoulder tag: read its change, not its level)"""
    ax.plot(x, y, "o", ms=ms, mfc="white" if m == SH else fill, mec=HUE[g] if m == SH else "white",
            mew=1.6 if m == SH else 1, zorder=z)


def mean_sem(ax, x, v, g, w=0.22):
    v = [y for y in v if y == y]
    mu, se = st.mean(v), st.stdev(v) / len(v) ** .5
    ax.plot([x - w, x + w], [mu, mu], color=HUE[g], lw=3, zorder=4, solid_capstyle="butt")
    ax.errorbar(x, mu, se, color=HUE[g], lw=2, capsize=5, capthick=2, zorder=4)


def dots(ax, rows, keys, labels, tint, n_label=True):
    """per key: water dots left, SOD1 right; mean ± SEM; tint[i] = SD/recovery condition (light hue)"""
    for i, k in enumerate(keys):
        for g, dx in (("water", -0.2), ("SOD1", 0.2)):
            sel = [r for r in rows if r["group"] == g and r[k] == r[k]]
            jit = (np.arange(len(sel)) - (len(sel) - 1) / 2) * 0.035
            for j, r in zip(jit, sel):
                mouse_marker(ax, i + dx + j, r[k], g, r["mouse"], TINT[g] if tint[i] else HUE[g])
            mean_sem(ax, i + dx, [r[k] for r in sel], g, w=0.13)
    ax.set_xticks(range(len(keys)), labels)
    ax.set_xlim(-0.6, len(keys) - 0.4)


def forest(ax, es, labels, unit, title):
    """SOD1 - water difference with its exact-permutation 95 % CI, one row per measure"""
    for i, e in enumerate(es):
        y = len(es) - 1 - i
        ax.plot([e["lo"], e["hi"]], [y, y], color=INK, lw=3, solid_capstyle="round")
        ax.plot(e["d"], y, "o", color=INK, ms=10, mec="white", mew=1.5)
        ax.text(1.02, y, f"{e['d']:+.0f} [{e['lo']:+.0f}, {e['hi']:+.0f}]\np = {e['p']:.2f}".replace("-", "−"),
                transform=ax.get_yaxis_transform(), va="center", fontsize=12)
    ax.axvline(0, color=CHANCE, lw=1.2, ls="--")
    ax.set_yticks(range(len(es)), labels[::-1])
    ax.set_ylim(-0.6, len(es) - 0.4)
    ax.set_xlabel(f"SOD1 − water ({unit})")
    ax.set_title(title)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)


def legend_59(fig, extra=(), ncol=None):
    """one legend under the figure, so it never covers data"""
    h = list(extra) + [Line2D([], [], ls="", marker="o", ms=8, mfc="white", mec=INK, mew=1.6,
                              label=f"hollow = {SH}, tag at the shoulder (read its change, not its level)")]
    fig.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 0), ncol=ncol or len(h), fontsize=12)


ARM_PATCH = [Patch(fc=WATER, label="water"), Patch(fc=SOD1, label="SOD1")]
SD_PATCH = [Patch(fc=WATER_SD, label="water, SD / recovery"), Patch(fc=SOD1_SD, label="SOD1, SD / recovery")]


# ------------------------------------------------------------------ figures
def fig_protocol(ymaze):
    """time axis of the whole NS-SD nanotag study with light/dark shading and the analysis windows"""
    t0, t1 = datetime(2026, 10, 22, 9), datetime(2026, 11, 5, 9)
    hrs = lambda t: (t - t0).total_seconds() / 3600
    fig, (ax, az) = plt.subplots(2, 1, figsize=TALL, layout="constrained", gridspec_kw={"height_ratios": [1, 1.15]})

    def shade(a, lo, hi):
        t = datetime(2026, 10, 21, 21)
        while t < hi:
            a.axvspan(hrs(max(t, lo)), hrs(min(t + 12 * H, hi)), color=DARK_BG, lw=0, zorder=0)
            t += 24 * H

    def bar(a, y, s, e, col, txt="", tcol=INK, fs=12, h=0.62, hatch=None, ec="none"):
        a.add_patch(Rectangle((hrs(s), y - h / 2), hrs(e) - hrs(s), h, fc=col, ec=ec, hatch=hatch, lw=1, zorder=2))
        if txt:
            a.text((hrs(s) + hrs(e)) / 2, y, txt, ha="center", va="center", fontsize=fs, color=tcol, zorder=3)

    def sd_bar(a, y, s, e, txt, fs=12):     # both arms are deprived: water tint over SOD1 tint
        a.add_patch(Rectangle((hrs(s), y), hrs(e) - hrs(s), 0.31, fc=WATER_SD, lw=0, zorder=2))
        a.add_patch(Rectangle((hrs(s), y - 0.31), hrs(e) - hrs(s), 0.31, fc=SOD1_SD, lw=0, zorder=2))
        if txt:
            a.text((hrs(s) + hrs(e)) / 2, y, txt, ha="center", va="center", fontsize=fs, color=INK, zorder=3,
                   fontweight="bold")

    yend = max(ymaze.values()) if ymaze else datetime(2026, 11, 4, 17, 15)
    # --- top: the whole study
    shade(ax, t0, t1)
    bar(ax, 2, t0, SD.BASE_END, "#BDBDBD", "Baseline\n2 days")
    bar(ax, 2, SD.BASE_END, datetime(2026, 10, 30, 9), "#8C8C8C", "SOD1 or water, days 1-6", "white")
    bar(ax, 2, datetime(2026, 10, 30, 19), SD.RUN2_PRE[0], "#D9D9D9")
    bar(ax, 2, *SD.RUN2_PRE, "#8C8C8C", "days 8-10", "white")
    sd_bar(ax, 2, *SD.SD[0][1:], "")
    bar(ax, 2, SD.RECOVERY[0][1], SD.RECOVERY[1][2], "#5E5E5E")
    sd_bar(ax, 2, SD.SD[1][1], yend, "")
    for t, lab in ((SD.SD[0][1], "SD 1"), (SD.SD[1][1], "SD 2")):
        ax.text(hrs(t) + 2, 2.42, lab, ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.text(hrs(datetime(2026, 10, 30, 14)), 1.5, "tag\nread", ha="center", va="center", fontsize=10, color="0.35")
    bar(ax, 1, t0, datetime(2026, 10, 30, 9), "white", "Tag Run 1  (10-22 09:00 → 10-30 09:00)", ec=INK, h=0.5)
    bar(ax, 1, datetime(2026, 10, 30, 19), yend, "white", "Tag Run 2 (10-30 19:00 → Y-maze)", ec=INK, h=0.5)
    ax.annotate("Y-maze,\nsampling", (hrs(yend), 2), (hrs(yend) + 8, 2), fontsize=12, va="center",
                arrowprops=dict(arrowstyle="<-", color=INK))
    days = [t0 + 24 * H * i for i in range(15)]
    ax.set_xticks([hrs(d) for d in days], [f"{d:%m-%d}" for d in days], fontsize=12)
    ax.set_yticks([1, 2], ["recording", "analysis\nwindow"])
    ax.set_xlim(0, hrs(t1)); ax.set_ylim(0.6, 2.75)
    ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
    ax.set_title("NS-SD nanotag study: 5 water + 5 SOD1 mice, both arms deprived on the same days")
    ax.set_xlabel("tick = 09:00 = lights on (ZT0); grey = dark phase 21:00-09:00", fontsize=12, color="0.35")
    # --- bottom: the two SD days, zoomed
    z0, z1 = datetime(2026, 11, 2, 21), datetime(2026, 11, 5, 0)
    shade(az, z0, z1)
    bar(az, 1, z0, SD.RUN2_PRE[1], "#8C8C8C", "day 10\n(undisturbed)", "white")
    sd_bar(az, 1, *SD.SD[0][1:], "SD day 1\n09:00-15:00")
    bar(az, 1, *SD.RECOVERY[0][1:], "#8C8C8C", "recovery\nZT6-12", "white")
    bar(az, 1, *SD.RECOVERY[1][1:], "#5E5E5E", "recovery,\ndark phase", "white")
    sd_bar(az, 1, *SD.SD[1][1:], "SD day 2\n09:00-15:00")
    sd_bar(az, 1, SD.SD[1][2], yend, "")
    bar(az, 1, yend, datetime(2026, 11, 4, 20), "white", ec=INK, hatch="//")
    az.text(hrs(datetime(2026, 11, 4, 20)) + 0.4, 1, "awake after\nY-maze →\nsampling\n~20:00", va="center",
            fontsize=11)
    az.text(hrs(SD.SD[1][2]) - 0.2, 0.55, "15:00 → own Y-maze:\nstill awake (SD)", fontsize=11, va="center")
    for m, t in ymaze.items():
        az.plot(hrs(t), 1.47, "v", color=HUE[C.group(m)], ms=9, mec="white")
    az.text(hrs(SD.SD[1][2]) - 0.2, 1.62, "Y-maze starts,\n15-min slots", fontsize=11, va="bottom")
    ticks = [z0 + 3 * H * i for i in range(10)] + [datetime(2026, 11, 4, 3) + 3 * H * i for i in range(8)]
    az.set_xticks([hrs(t) for t in ticks], [f"{t:%H}" if t.hour else f"{t:%m-%d}" for t in ticks], fontsize=12)
    az.set_xlabel("clock hour (KST)")
    az.set_xlim(hrs(z0), hrs(z1)); az.set_ylim(0.35, 1.95); az.set_yticks([])
    az.spines["left"].set_visible(False)
    az.set_title("Zoom on 11-03 and 11-04: one recovery window; no sleep exists after SD day 2")
    az.legend(handles=[Patch(fc=WATER_SD, label="SD, water"), Patch(fc=SOD1_SD, label="SD, SOD1"),
                       Patch(fc=DARK_BG, label="dark phase")], loc="upper left", ncol=3, fontsize=11)
    save(fig, out("01_protocol"))


def fig_sd(rows, e):
    fig, ax = plt.subplots(1, 3, figsize=WIDE, layout="constrained", gridspec_kw={"width_ratios": [1.5, 1, 1.15]})
    keys, labs = ["base_sd1_hours_pct", "sd1_pct", "sd2_pct"], ["Base-\nline", "SD\nday 1", "SD\nday 2"]
    a = ax[0]
    for g, x0 in (("water", 0), ("SOD1", 3.5)):
        x = np.arange(3) + x0
        for r in [r for r in rows if r["group"] == g]:
            a.plot(x, [r[k] for k in keys], "-", color=HUE[g], alpha=0.45, lw=1.2, zorder=2)
            for xi, k, tint in zip(x, keys, (False, True, True)):
                mouse_marker(a, xi, r[k], g, r["mouse"], TINT[g] if tint else HUE[g])
        for xi, k in zip(x, keys):
            mean_sem(a, xi, [r[k] for r in rows if r["group"] == g], g, w=0.25)
        a.text(x0 + 1, -24, f"{g} (n = {sum(r['group'] == g for r in rows)})", ha="center", fontsize=14,
               color=HUE[g], fontweight="bold")
    a.set_xticks(list(range(3)) + list(np.arange(3) + 3.5), labs * 2, fontsize=12)
    a.set_ylim(0, 100); a.set_xlim(-0.5, 6)
    a.set_ylabel("% of 09:00-15:00 asleep\n(immobile ≥ 48 s)")
    a.set_title("A  Sleep in the SD hours")
    b = ax[1]
    dots(b, rows, ["sd1_sleep_lost_min", "sd2_sleep_lost_min"], ["SD day 1", "SD day 2"], [True, True])
    b.set_ylim(0, 300); b.set_ylabel("sleep lost vs baseline hours (min)")
    b.axhline(0, color=CHANCE, lw=1)
    b.set_title("B  Sleep lost")
    forest(ax[2], [e["sd1_sleep_lost_min"], e["sd2_sleep_lost_min"]], ["SD day 1", "SD day 2"], "min lost",
           "C  SOD1 − water")
    legend_59(fig, ARM_PATCH + SD_PATCH)
    save(fig, out("02_sd_efficacy"))


def fig_recovery(rows, e):
    for r in rows:
        r["base_1509"] = r["base_ZT6-12_min"] + r["base_dark_min"]
        r["rec_1509"] = r["rec_ZT6-12_min"] + r["rec_dark_min"]
    fig, ax = plt.subplots(1, 3, figsize=WIDE, layout="constrained", gridspec_kw={"width_ratios": [1.1, 1.3, 1.15]})
    a = ax[0]
    for g, x0 in (("water", 0), ("SOD1", 2.3)):
        x = np.array([0, 1]) + x0
        for r in [r for r in rows if r["group"] == g]:
            a.plot(x, [r["base_1509"], r["rec_1509"]], "-", color=HUE[g], alpha=0.45, lw=1.2)
            mouse_marker(a, x[0], r["base_1509"], g, r["mouse"], HUE[g])
            mouse_marker(a, x[1], r["rec_1509"], g, r["mouse"], TINT[g])
        for xi, k in zip(x, ("base_1509", "rec_1509")):
            mean_sem(a, xi, [r[k] for r in rows if r["group"] == g], g)
        a.text(x0 + 0.5, 0.02, f"{g}\n(n = {sum(r['group'] == g for r in rows)})", ha="center", fontsize=13,
               color=HUE[g], fontweight="bold", transform=a.get_xaxis_transform())
    a.set_xticks([0, 1, 2.3, 3.3], ["base-\nline", "after\nSD 1"] * 2, fontsize=12)
    a.set_xlim(-0.5, 3.8); a.set_ylim(250, 800)
    a.set_ylabel("minutes asleep, 15:00 → 09:00\n(of 1,080 min)")
    a.set_title("A  After SD day 1")
    b = ax[1]
    keys = ["rebound_ZT6-12_min", "rebound_dark_min", "rebound_total_min"]
    dots(b, rows, keys, ["ZT6-12", "dark", "total"], [True] * 3)
    b.axhline(0, color=CHANCE, lw=1.2, ls="--")
    b.set_ylabel("rebound = recovery − baseline (min)")
    b.set_title("B  Rebound")
    forest(ax[2], [e[k] for k in keys], ["ZT6-12", "dark", "total"], "min", "C  SOD1 − water")
    legend_59(fig, ARM_PATCH + SD_PATCH)
    save(fig, out("03_recovery"))


def fig_course(dt):
    """normal sleep vs SD, day by day: SD hours (09-15) and the hours after them (15-09), per arm"""
    days = sorted({r["day"] for r in dt})
    fig, ax = plt.subplots(2, 2, figsize=TALL, layout="constrained", sharex=True, sharey="row")
    spec = (("p915", "% of 09:00-15:00 asleep", (0, 100)), ("m1509", "minutes asleep\n15:00 → 09:00", (250, 800)))
    for row, (k, lab, yl) in enumerate(spec):
        for col, g in enumerate(ORDER):
            a = ax[row, col]
            for d in (SD1, SD2) if k == "p915" else (SD1,):
                a.axvspan(at(d, -12), at(d, 12), color=TINT[g], alpha=0.35, lw=0)
            ms = [m for m in C.mice() if C.group(m) == g]
            ref = st.mean(dval(dt, m, d, k) for m in ms for d in BASE)
            a.axhline(ref, color=HUE[g], lw=1, ls=":")
            for m in ms:
                y = [dval(dt, m, d, k) for d in days]
                a.plot(days, y, "-", color=HUE[g], alpha=0.35, lw=1)
                for d, v in zip(days, y):
                    if v == v:
                        sdday = d in ((SD1, SD2) if k == "p915" else (SD1,))
                        mouse_marker(a, d, v, g, m, TINT[g] if sdday else HUE[g], ms=5, z=3)
            mu = [np.nanmean([dval(dt, m, d, k) for m in ms]) for d in days]
            a.plot(days, mu, "-", color=HUE[g], lw=3, zorder=4)
            a.set_ylim(*yl)
            if col == 0:
                a.set_ylabel(lab)
            if row == 0:
                a.set_title(f"{g} (n = {len(ms)})", color=HUE[g])
                a.text(SD1, 3, " SD", fontsize=12, fontweight="bold", ha="center", va="bottom")
                a.text(SD2, 3, " SD", fontsize=12, fontweight="bold", ha="center", va="bottom")
            else:
                a.text(SD1, 262, "after\nSD 1", fontsize=11, fontweight="bold", ha="center", va="bottom")
                a.text(SD2, 262, "no\ndata", fontsize=10, ha="center", va="bottom", color="0.4")
            a.text(date(2026, 10, 30), yl[0] + 0.03 * (yl[1] - yl[0]), "tag\nread", fontsize=10, ha="center",
                   va="bottom", color="0.4")
            a.set_xticks(days[::2], [f"{d:%m-%d}" for d in days[::2]], fontsize=12)
    ax[1, 0].set_xlabel("ZT day (09:00 → 09:00)"); ax[1, 1].set_xlabel("ZT day (09:00 → 09:00)")
    legend_59(fig, [Line2D([], [], color=INK, lw=3, label="arm mean"),
                    Line2D([], [], color=INK, lw=1, ls=":", label="arm baseline mean (10-22, 10-23)")])
    save(fig, out("04_normal_vs_sd_by_day"))


def fig_change(rc, band):
    """change from own baseline in the same clock hours: normal days vs SD / recovery"""
    fig, ax = plt.subplots(1, 2, figsize=WIDE, layout="constrained", gridspec_kw={"width_ratios": [4, 3]})
    for a, keys, labs, tint, bd, unit, ttl in (
            (ax[0], ["n16_915", "n810_915", "sd1_915", "sd2_915"],
             ["normal\ndays 1-6", "normal\ndays 8-10", "SD\nday 1", "SD\nday 2"], [0, 0, 1, 1], band["915"],
             "change in % of 09:00-15:00 asleep\n(points vs own baseline)", "A  SD hours, 09:00-15:00"),
            (ax[1], ["n16_1509", "n810_1509", "rec_1509"], ["normal\ndays 1-6", "normal\ndays 8-10", "after\nSD day 1"],
             [0, 0, 1], band["1509"], "change in minutes asleep, 15:00 → 09:00\n(vs own baseline)",
             "B  The hours after, 15:00 → 09:00")):
        a.axhspan(*bd, color="0.85", lw=0, zorder=0)
        a.axhline(0, color=CHANCE, lw=1.2, ls="--")
        dots(a, rc, keys, labs, tint)
        a.set_ylabel(unit); a.set_title(ttl)
        a.text(len(keys) - 0.45, bd[0], "grey = range of every single\nnormal day, all mice", ha="right",
               va="bottom", fontsize=11, color="0.35")
    legend_59(fig, ARM_PATCH + SD_PATCH, ncol=3)
    save(fig, out("05_normal_vs_sd_change"))


def fig_hourly(ser):
    """hour by hour, 11-03 09:00 -> 11-04 15:00 against the same clock hours of undisturbed days 8-10"""
    hs = range(30)
    fig, ax = plt.subplots(1, 2, figsize=WIDE, layout="constrained", sharey=True)
    for a, g in zip(ax, ORDER):
        ms = [m for m in C.mice() if C.group(m) == g]
        sdv = np.array([[frac(ser[m], at(SD1, 9 + h), at(SD1, 10 + h)) for h in hs] for m in ms])
        nrm = np.array([[np.mean([frac(ser[m], at(d, 9 + h % 24), at(d, 10 + h % 24)) for d in DAYS810])
                         for h in hs] for m in ms])
        for v, col, lab, mk in ((nrm, HUE[g], "normal: days 8-10, same clock hours", None),
                                (sdv, TINT[g], "SD day 1 → recovery → SD day 2", "o")):
            mu, se = v.mean(0), v.std(0, ddof=1) / len(v) ** .5
            a.fill_between(np.array(hs) + 0.5, mu - se, mu + se, color=col, alpha=0.25, lw=0)
            a.plot(np.array(hs) + 0.5, mu, "-", color=col, lw=2.8, marker=mk, ms=5, mec="white", label=lab)
        a.axvspan(12, 24, color=DARK_BG, lw=0, zorder=0)
        for s, e_ in ((0, 6), (24, 30)):
            a.axvspan(s, e_, ymin=0.93, ymax=1, color=TINT[g], lw=0)
            a.text((s + e_) / 2, 96, "SD", ha="center", va="center", fontsize=12, fontweight="bold")
        a.text(9, 96, "recovery", ha="center", va="center", fontsize=12)
        a.text(18, 96, "recovery, dark", ha="center", va="center", fontsize=12)
        a.set_xticks(range(0, 31, 3), [f"{(9 + h) % 24:02d}" for h in range(0, 31, 3)])
        a.set_xlim(0, 30); a.set_ylim(0, 100)
        a.set_xlabel("clock hour, 11-03 09:00 → 11-04 15:00")
        a.set_title(f"{g} (n = {len(ms)})", color=HUE[g])
        print(f"  hourly {g:5s} SD/rec: " + " ".join(f"{v:3.0f}" for v in sdv.mean(0)))
        print(f"  hourly {g:5s} normal: " + " ".join(f"{v:3.0f}" for v in nrm.mean(0)))
    ax[0].set_ylabel("% of hour asleep (mean ± SEM)")
    fig.legend(handles=[Line2D([], [], color=c, lw=2.8, marker=mk, mec="white", label=f"{g}, {lab}")
                        for g, c, mk, lab in (("water", WATER, None, "normal: days 8-10, same clock hours"),
                                              ("SOD1", SOD1, None, "normal: days 8-10, same clock hours"),
                                              ("water", WATER_SD, "o", "SD day 1 → recovery → SD day 2"),
                                              ("SOD1", SOD1_SD, "o", "SD day 1 → recovery → SD day 2"))],
               loc="upper center", bbox_to_anchor=(0.5, 0), ncol=2, fontsize=12)
    save(fig, out("06_hourly_sd_vs_normal"))


def fig_days(ch, es):
    """normal sleep under SOD1 or water: change from baseline on days 1-6 and days 8-10"""
    spec = (("total", "Total sleep\n(min/day)"), ("light", "Light phase\n(% asleep)"),
            ("dark", "Dark phase\n(% asleep)"), ("darkact", "Dark activity\n(counts/h)"))
    fig, ax = plt.subplots(1, 4, figsize=WIDE, layout="constrained")
    for a, (k, lab) in zip(ax, spec):
        dots(a, ch, [f"{k}_16", f"{k}_810"], ["days\n1-6", "days\n8-10"], [False, False])
        a.axhline(0, color=CHANCE, lw=1.2, ls="--")
        a.set_title(lab, fontsize=15)
        txt = "\n".join(f"{p}: {es[f'{k}_{p}']['d']:+.0f} [{es[f'{k}_{p}']['lo']:+.0f}, {es[f'{k}_{p}']['hi']:+.0f}]"
                        for p in ("16", "810"))
        a.text(0.5, -0.24, "SOD1 − water, 95 % CI\n" + txt.replace("16:", "1-6:").replace("810:", "8-10:"),
               transform=a.transAxes, ha="center", va="top", fontsize=11)
        if k == "darkact":
            a.ticklabel_format(axis="y", style="plain")
    ax[0].set_ylabel("change from own baseline")
    legend_59(fig, ARM_PATCH)
    save(fig, out("07_normal_sleep_days"))


def fig_actograms(recs1, r2, ymaze):
    """single-plotted, one ZT day per row, 10-min cross counts scaled per mouse (99th percentile)"""
    first, last = date(2026, 10, 22), SD2
    nrow = (last - first).days + 1
    fig, axes = plt.subplots(2, 5, figsize=(12.5, 7.4), layout="constrained", sharex=True, sharey=True)
    for row, g in enumerate(ORDER):
        for a, m in zip(axes[row], [m for m in C.mice() if C.group(m) == g]):
            act = [x for r in recs1 if r["mouse"] == m for x in r["act"]] + (r2[m][1] if m in r2 else [])
            bins = {}
            for t, c in act:
                k = t.replace(minute=t.minute // 10 * 10, second=0)
                bins[k] = bins.get(k, 0) + c
            top = np.percentile(list(bins.values()), 99) or 1
            for i in range(nrow):
                d = first + timedelta(days=i)
                y0 = nrow - i - 1
                xs = np.arange(0, 24, 1 / 6)
                ys = np.array([bins.get(at(d, 9 + x), np.nan) for x in xs])
                a.fill_between(xs, y0, y0 + 0.9 * np.clip(np.nan_to_num(ys) / top, 0, 1), step="post",
                               color=HUE[g], lw=0)
                if d in (SD1, SD2):
                    a.add_patch(Rectangle((0, y0 - 0.05), 6 if d == SD1 else 6, 1, fc=TINT[g], alpha=0.45, lw=0,
                                          zorder=0))
                if d == SD2 and m in ymaze:
                    x = (ymaze[m] - at(d, 9)).total_seconds() / 3600
                    a.plot(x, y0 + 0.5, "|", color=INK, ms=12, mew=2.5)
            a.axvspan(12, 24, color=DARK_BG, lw=0, zorder=-1)
            a.set_title(f"{m}" + ("  (shoulder tag)" if m == SH else ""), fontsize=13, color=HUE[g])
            a.set_xticks([0, 6, 12, 18, 24]); a.set_xlim(0, 24); a.set_ylim(0, nrow)
            a.set_yticks([nrow - i - 0.55 for i in range(0, nrow, 2)],
                         [f"{first + timedelta(days=i):%m-%d}" for i in range(0, nrow, 2)], fontsize=10)
            a.tick_params(axis="x", labelsize=11)
        axes[row, 0].set_ylabel(f"{g}\nZT day", color=HUE[g], fontweight="bold")
    fig.supxlabel("hours from lights on (ZT0 = 09:00; grey = dark phase; tint = SD hours; | = Y-maze start)",
                  fontsize=13)
    save(fig, out("08_actograms"))


# ------------------------------------------------------------------ main
def main():
    os.makedirs(FIG, exist_ok=True)
    ymaze = SD.ymaze_starts()
    print(f"Y-maze starts from {SD.YMAZE_SHEET}: {len(ymaze)} of 10 "
          f"({', '.join(f'{m} {t:%H:%M}' for m, t in sorted(ymaze.items(), key=lambda x: x[1]))})")
    fig_protocol(ymaze)
    print("\nRun 1:", RUN1)
    recs1 = SD.load(RUN1)
    csvs = sorted(f for f in os.listdir(RUN2) if f.endswith(".csv"))
    assert len(csvs) == 10, f"{RUN2}: expected the 10 Run 2 CSVs (57 = the re-export), found {csvs}"
    print("\nRun 2:", RUN2)
    r2 = SD.load_run2(RUN2, ymaze)
    ser = series(recs1, r2)
    dt = day_table(ser)
    base = {r["mouse"]: r for r in recs1 if r["period"] == "baseline"}

    # --- self-check: the day table reproduces cohort_sd's baseline window (same bins, same half-open windows)
    for m in C.mice():
        ref = SD.pct(base[m]["scored"], SD.at_baseline(*SD.SD[0][1:]))
        mine = st.mean(dval(dt, m, d, "p915") for d in BASE)
        assert abs(ref - mine) < 1e-9, (m, ref, mine)

    print("\nPer mouse, % of 09:00-15:00 asleep by ZT day (NaN = not recorded)")
    days = sorted({r["day"] for r in dt})
    print("  mouse " + " ".join(f"{d:%m-%d}" for d in days))
    for m in C.mice():
        print(f"  {m:5d} " + " ".join(f"{dval(dt, m, d, 'p915'):5.1f}" for d in days))
    print("Per mouse, minutes asleep 15:00 -> 09:00 by ZT day")
    for m in C.mice():
        print(f"  {m:5d} " + " ".join(f"{dval(dt, m, d, 'm1509'):5.0f}" for d in days))

    # --- normal days vs own baseline (same clock hours), and the SD / recovery change
    normal = BASE + DAYS16 + DAYS810
    rc = []
    for m in C.mice():
        b915 = st.mean(dval(dt, m, d, "p915") for d in BASE)
        b1509 = st.mean(dval(dt, m, d, "m1509") for d in BASE)
        r = dict(mouse=m, group=C.group(m),
                 n16_915=st.mean(dval(dt, m, d, "p915") for d in DAYS16) - b915,
                 n16_1509=st.mean(dval(dt, m, d, "m1509") for d in DAYS16) - b1509,
                 sd_day_915=st.stdev(dval(dt, m, d, "p915") for d in normal),
                 sd_day_1509=st.stdev(dval(dt, m, d, "m1509") for d in normal))
        r.update({f"_{d}_915": dval(dt, m, d, "p915") - b915 for d in DAYS16 + DAYS810})
        r.update({f"_{d}_1509": dval(dt, m, d, "m1509") - b1509 for d in DAYS16 + DAYS810})
        r.update(n810_915=st.mean(dval(dt, m, d, "p915") for d in DAYS810) - b915,
                 n810_1509=st.mean(dval(dt, m, d, "m1509") for d in DAYS810) - b1509,
                 sd1_915=dval(dt, m, SD1, "p915") - b915, sd2_915=dval(dt, m, SD2, "p915") - b915,
                 rec_1509=dval(dt, m, SD1, "m1509") - b1509)
        # the same SD / recovery change, measured against the undisturbed days 8-10 just before
        r.update(sd1_vs810=r["sd1_915"] - r["n810_915"], rec_vs810=r["rec_1509"] - r["n810_1509"])
        rc.append(r)
    single = {w: [r[f"_{d}_{w}"] for r in rc for d in DAYS16 + DAYS810
                  if r[f"_{d}_{w}"] == r[f"_{d}_{w}"]] for w in ("915", "1509")}
    band = {w: (min(v), max(v)) for w, v in single.items()}
    print("\nNormal day-to-day variation, change from own baseline in the same clock hours, every single normal day "
          f"({len(single['915'])} mouse-days):")
    print(f"  09-15 window: range {band['915'][0]:+.1f} to {band['915'][1]:+.1f} points; "
          f"per-mouse SD across normal days median {st.median(r['sd_day_915'] for r in rc):.1f} points "
          f"(range {min(r['sd_day_915'] for r in rc):.1f}-{max(r['sd_day_915'] for r in rc):.1f})")
    print(f"  15-09 window: range {band['1509'][0]:+.0f} to {band['1509'][1]:+.0f} min; "
          f"per-mouse SD median {st.median(r['sd_day_1509'] for r in rc):.0f} min "
          f"(range {min(r['sd_day_1509'] for r in rc):.0f}-{max(r['sd_day_1509'] for r in rc):.0f})")
    for k in ("n16_915", "n810_915", "sd1_915", "sd2_915", "sd1_vs810", "n16_1509", "n810_1509", "rec_1509",
              "rec_vs810"):
        show(k, eff(rc, k), "min" if "1509" in k or k.startswith("rec") else "points")
    z = lambda k, s: [r[k] / r[s] for r in rc]
    print(f"  SD day 1 drop in units of each mouse's own normal day-to-day SD: median "
          f"{st.median(z('sd1_915', 'sd_day_915')):.1f} (range {min(z('sd1_915', 'sd_day_915')):.1f} to "
          f"{max(z('sd1_915', 'sd_day_915')):.1f})")
    print(f"  Recovery night in the same units: median {st.median(z('rec_1509', 'sd_day_1509')):.1f} "
          f"(range {min(z('rec_1509', 'sd_day_1509')):.1f} to {max(z('rec_1509', 'sd_day_1509')):.1f})")
    print(f"  mice whose SD day 1 change lies below the normal band: "
          f"{sum(r['sd1_915'] < band['915'][0] for r in rc)} of {len(rc)}; SD day 2: "
          f"{sum(r['sd2_915'] < band['915'][0] for r in rc)} of {len(rc)}; recovery above the band: "
          f"{sum(r['rec_1509'] > band['1509'][1] for r in rc)} of {len(rc)}")
    fig_course(dt)
    fig_change(rc, band)

    # --- normal sleep under SOD1 / water: days 1-6 (Run 1) and days 8-10 (Run 2), cohort.summarise
    days1 = [row for r in recs1 for row in C.daily_rows(r)]
    summ = C.summarise(recs1, days1)
    per = {"16": {(s["mouse"], s["period"]): s for s in summ}}
    inpre = lambda x: SD.RUN2_PRE[0] <= x[0] < SD.RUN2_PRE[1]
    pre = [dict(mouse=m, group=C.group(m), period="treatment", files=["run2"], hdr=h, temp=[],
                act=[x for x in act if inpre(x)], scored=[x for x in sc if inpre(x)])
           for m, (h, act, sc) in sorted(r2.items())]
    d810 = [row for r in list(base.values()) + pre for row in C.daily_rows(r)]
    per["810"] = {(s["mouse"], s["period"]): s for s in C.summarise(list(base.values()) + pre, d810)}
    kmap = {"total": "total_sleep_min_per_day", "light": "light_sleep_pct", "dark": "dark_sleep_pct",
            "darkact": "counts_per_h_dark", "RA": "RA"}
    ch = []
    for m in C.mice():
        r = dict(mouse=m, group=C.group(m))
        for p in ("16", "810"):
            for k, src in kmap.items():
                r[f"{k}_{p}"] = per[p][(m, "treatment")][src] - per[p][(m, "baseline")][src]
        ch.append(r)
    print("\nNormal sleep under SOD1 / water, change from baseline (cohort.summarise, mean ± SEM, exact permutation)")
    es = {}
    for p in per:
        for k in kmap:
            es[f"{k}_{p}"] = eff(ch, f"{k}_{p}")
            show(f"{k} days {'1-6' if p == '16' else '8-10'}", es[f"{k}_{p}"])
        for k in ("total", "dark", "darkact"):
            show(f"{k} days {'1-6' if p == '16' else '8-10'} without {SH}", eff(ch, f"{k}_{p}", lambda r: r["mouse"] != SH))
    fig_days(ch, es)

    # --- SD efficacy and recovery: cohort_sd.window_rows, the analysis behind the vault note
    rows = SD.window_rows(base, r2, ymaze)
    keys = ["sd1_change_pts", "sd2_change_pts", "sd1_sleep_lost_min", "sd2_sleep_lost_min",
            "rebound_ZT6-12_min", "rebound_dark_min", "rebound_total_min"]
    e = {k: eff(rows, k) for k in keys}
    print("\nSD efficacy, 09:00-15:00, against the same mouse's baseline hours (10-22, 10-23)")
    print("  mouse group base% SD1% SD2% lost1 lost2 ymaze real_h wait% | ZT6-12 base rec | dark base rec | rebound")
    for r in rows:
        print(f"  {r['mouse']:5d} {r['group']:5s} {r['base_sd1_hours_pct']:5.1f} {r['sd1_pct']:4.1f} {r['sd2_pct']:4.1f} "
              f"{r['sd1_sleep_lost_min']:5.0f} {r['sd2_sleep_lost_min']:5.0f} {r['ymaze_start']:>5s} "
              f"{r['sd2_real_h']:4.2f} {r['wait_pct']:5.1f} | {r['base_ZT6-12_min']:5.0f} {r['rec_ZT6-12_min']:5.0f} | "
              f"{r['base_dark_min']:5.0f} {r['rec_dark_min']:5.0f} | {r['rebound_total_min']:+5.0f}")
    for k in ("base_sd1_hours_pct", "sd1_pct", "sd2_pct", "sd2_real_h", "wait_pct",
              "base_ZT6-12_min", "rec_ZT6-12_min", "base_dark_min", "rec_dark_min"):
        a, b, d, _, _, p = SD.effect(rows, k, ci=False)
        print(f"  {k:24s} water {st.mean(b):6.1f} ± {st.stdev(b) / 5 ** .5:4.1f}  SOD1 {st.mean(a):6.1f} ± "
              f"{st.stdev(a) / 5 ** .5:4.1f}  SOD1 − water {d:+.1f} p={p:.2f}")
    for k in keys:
        show(k, e[k], "points" if k.endswith("pts") else "min")
    for i in (1, 2):
        for g in ORDER:
            v = [r[f"sd{i}_change_pts"] for r in rows if r["group"] == g]
            print(f"  SD day {i} {g:5s}: {sum(x < 0 for x in v)} of {len(v)} below baseline")
    for g in ORDER:
        v = [r["rebound_total_min"] for r in rows if r["group"] == g]
        print(f"  rebound total {g:5s}: {sum(x > 0 for x in v)} of {len(v)} above baseline")
    print(f"  without {SH}:")
    for k in keys:
        show(k, eff(rows, k, lambda r: r["mouse"] != SH))
    fig_sd(rows, e)
    fig_recovery(rows, e)
    fig_hourly(ser)
    fig_actograms(recs1, r2, ymaze)
    print("\nfigures in", FIG)


if __name__ == "__main__":
    main()

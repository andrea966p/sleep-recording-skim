#!/usr/bin/env python3
"""HLB SOD1 progress meeting (2026-11-05): one consistent figure set, re-plotted from existing results.

    ~/hlb-eeg-venv/bin/python nanotag/analysis/report/meeting_figures.py [01 02 ...]

Writes vault/_attachments/2026-11-05-hlb-meeting-figNN-<name>.png. No analysis is redone here: every value
comes from a results file or a result note (source named at each function). Slot 09 (intake) and 10-11
(NS-SD Run 2, Y-maze after SD) are left for later figures.

Inputs that are not in git:
- HLBNSL nanotag tables and per-mouse bins on the SKIM NAS (NAS below).
- Tissue per-mouse values: nanotag/analysis/out/tissue/, made by the tissue analysis itself:
    python tissue/cayman_extract.py tissue/raw/SOD1-biochem_raw_data.xlsx out/tissue   (needs openpyxl)
    python tissue/cayman_analyse.py out/tissue   (writes hippoSOD_cayman.csv, heartSOD_cayman.csv)
"""
import sys
from datetime import datetime as dt, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

REPO = Path(__file__).resolve().parents[3]
ATT = REPO / "vault" / "_attachments"
NAS = Path("/mnt/skimnas/02_Data_Sleep/andrea")
HLBNSL = NAS / "HLBNSL_nanotag_ANALYSIS_2026-10-05"
EEG = REPO / "eeg-emg-analysis" / "rescore_2026_11" / "results" / "per_mouse_segments.csv"
TISSUE = REPO / "nanotag" / "analysis" / "out" / "tissue"

# ---------------- shared style ----------------
WATER, SOD1 = "#4a4a4a", "#2b8c9e"          # water = dark grey, SOD1 = muted teal, everywhere
COL = {"water": WATER, "SOD1": SOD1}
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"], "font.size": 14,
    "axes.labelsize": 15, "xtick.labelsize": 14, "ytick.labelsize": 13, "legend.fontsize": 13,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 1.1,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "savefig.dpi": 300, "legend.frameon": False,
})
SLIDE = (10, 5.4)                             # 16:9-ish, one figure per slide


def save(fig, n, name):
    p = ATT / f"2026-11-05-hlb-meeting-fig{n}-{name}.png"
    fig.savefig(p, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", p.name)


def dots(ax, x, v, color, open_=False, ms=9):
    """Individual mice (jittered) plus mean ± SEM; one value = a single point, no error bar."""
    v = np.asarray(v, float)
    jit = (np.arange(len(v)) - (len(v) - 1) / 2) * min(0.07, 0.36 / max(len(v) - 1, 1))
    ax.plot(x + jit, v, "o", ms=ms, mfc="white" if open_ else color, mec=color, mew=1.6, alpha=0.9, zorder=3)
    if len(v) > 1:
        m, se = v.mean(), v.std(ddof=1) / np.sqrt(len(v))
        ax.errorbar(x + 0.33, m, yerr=se, fmt="_", ms=22, mew=2.6, color=color, elinewidth=2.2, capsize=0, zorder=4)


def pair_axis(ax, labels_n, xs=(0, 1)):
    ax.set_xticks(list(xs), [f"{g}\nn = {n}" for g, n in labels_n])
    for t, (g, _) in zip(ax.get_xticklabels(), labels_n):
        t.set_color(COL.get(g.split()[0], "black"))
    ax.set_xlim(min(xs) - 0.6, max(xs) + 0.8)


def hedges(a, b):
    """Hedges g (SOD1 − water, pooled SD, small-sample correction) and a normal-approximation 95 % CI."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1)) / (n1 + n2 - 2))
    g = (a.mean() - b.mean()) / sp * (1 - 3 / (4 * (n1 + n2) - 9))
    se = np.sqrt((n1 + n2) / (n1 * n2) + g * g / (2 * (n1 + n2)))
    return g, g - 1.96 * se, g + 1.96 * se


# ---------------- per-mouse values taken from result notes (tables there, no CSV in the repo) ----------------
# NS-SD Run 1, total sleep and dark activity, baseline -> treatment: 2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1
NSSD = pd.DataFrame([  # mouse, group, total sleep base, treat (min/day), dark counts/h base, treat
    (51, "SOD1", 758, 789, 3323, 3656), (52, "SOD1", 760, 753, 3508, 4372), (53, "SOD1", 768, 760, 3316, 4303),
    (54, "SOD1", 778, 779, 2780, 3294), (55, "SOD1", 605, 677, 4468, 4852),
    (56, "water", 770, 781, 2997, 3198), (57, "water", 788, 789, 3121, 3388), (58, "water", 797, 784, 3330, 3429),
    (59, "water", 605, 595, 7982, 8467), (60, "water", 675, 694, 5836, 6110)],
    columns=["mouse", "group", "ts_b", "ts_t", "dark_b", "dark_t"])
# HLBNSL behaviour: Y-maze 2026-10-25-HLBNSL-ymaze-hand-scored-results, OFT 2026-10-25-HLBNSL-oft-day1-results,
# NOR d2 (pose model2, 2026-10-25 rule) 2026-10-25-HLBNSL-nor-pose-results. Order 41 42 44 49 | 45 46 47 48 50.
BEH = {
    "sa": ([63.2, 64.7, 60.5, 53.8], [66.7, 62.2, 69.4, 58.8, 56.7]),
    "entries": ([59, 53, 40, 41], [47, 39, 38, 36, 32]),
    "dist": ([74.1, 68.7, 60.4, 52.5], [49.5, 55.1, 52.9, 52.8, 45.1]),
    "d2": ([0.35, -0.11, 0.10, 0.62], [0.30, 0.31, 0.37, 0.44, 0.06]),
}


# ---------------- 01 design timeline ----------------
def fig01():
    """Dates: SOD1 sheet `Registry` (tethering = liquid start, CSD start, recovery start, sampling; read 2026-11-03),
    EEG 24 h windows from the NAS info.json start times, hlb-sod1-design, 2026-10-05-HLBNSL-nanotag-merged-analysis,
    2026-10-30-NS-SD-two-day-SD-y-maze-only. Sampling of S-SL slipped 09-21 -> 09-22 (2026-09-23-S-SL-connection-audit)."""
    D = lambda s, h=0: dt.strptime(f"2026-{s}", "%Y-%m-%d") + timedelta(hours=h)
    eeg = [  # label, drink, liquid start, SD (start, end) or None, baseline day, recovery day, sampling
        ("W-SD\nwater + SD", "water", D("08-10"), (D("08-21", 9), D("08-27", 13)), D("08-20", 9), D("08-27", 13), D("08-28", 11)),
        ("S-SD\nSOD1 + SD", "SOD1", D("08-16"), (D("08-27", 9), D("09-02", 13)), D("08-25", 9), D("09-02", 13), D("09-03", 13)),
        ("W-SL\nwater", "water", D("08-31"), None, D("09-10", 9), D("09-17", 9), D("09-18", 13)),
        ("S-SL\nSOD1", "SOD1", D("09-03"), None, D("09-12", 9), D("09-20", 9), D("09-22", 12)),
    ]
    fig, ax = plt.subplots(figsize=(12, 5.6))
    h = 0.5
    for i, (lab, drink, s, sd, b, r, end) in enumerate(eeg):
        y = 6 - i
        ax.barh(y, end - s, left=s, height=h, color=COL[drink], alpha=0.85)
        if sd:
            ax.barh(y, sd[1] - sd[0], left=sd[0], height=h * 1.25, color="black")
        for w in (b, r):
            ax.barh(y, timedelta(hours=24), left=w, height=h * 0.62, color="white", ec="black", lw=1.1)
        ax.plot(end, y - 0.45, "X", ms=12, color="black")
    # nanotag cohorts: SOD1 and water side by side (two half bars)
    nano = [("HLBNSL\nSOD1 4, water 5", D("09-14", 9), D("09-17", 14), [], [D("09-30", 15), D("10-01", 15), D("10-02", 15)],
             "Y-maze, open field, NOR", D("10-02", 17)),
            ("NS-SD\nSOD1 5, water 5", D("10-22", 9), D("10-24", 9), [(D("11-03", 9), D("11-03", 15)), (D("11-04", 9), D("11-04", 15))],
             [D("11-04", 15)], "Y-maze", D("11-04", 16))]
    for i, (lab, b0, t0, sds, tests, tlab, end) in enumerate(nano):
        y = 1.2 - 1.2 * i
        ax.barh(y, t0 - b0, left=b0, height=h, color="#d9d9d9")
        ax.barh(y + h / 4, end - t0, left=t0, height=h / 2, color=SOD1, alpha=0.85)
        ax.barh(y - h / 4, end - t0, left=t0, height=h / 2, color=WATER, alpha=0.85)
        for a, z in sds:
            ax.barh(y, z - a, left=a, height=h * 1.25, color="black")
        ax.plot(tests, [y + 0.45] * len(tests), "v", ms=9, color="black")
        ax.text(tests[0] - timedelta(days=1.5), y + 0.45, tlab, fontsize=12, ha="right", va="center")
        ax.plot(end, y - 0.45, "X", ms=12, color="black")
    ax.axhline(2.25, color="0.6", lw=1, ls=(0, (4, 3)))
    ax.text(D("11-08"), 6.5, "EEG/EMG cohorts, one group each", ha="right", fontsize=12, color="0.35")
    ax.text(D("11-08"), 2.1, "Nanotag cohorts, SOD1 and water together", ha="right", va="top", fontsize=12, color="0.35")
    ax.set_yticks([6, 5, 4, 3, 1.2, 0], [e[0] for e in eeg] + [n[0] for n in nano], fontsize=13)
    ax.set_ylim(-0.75, 6.75)
    ax.set_xlim(D("08-01"), D("11-08"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
    ax.tick_params(axis="x", which="major", pad=18, labelsize=14)
    ax.tick_params(axis="x", which="minor", labelsize=10, colors="0.4")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("2026 (minor ticks: Mondays)")
    leg = [Patch(color=SOD1, alpha=0.85, label="SOD1 6.8 U/mL in drinking water"),
           Patch(color=WATER, alpha=0.85, label="UV water"),
           Patch(color="#d9d9d9", label="baseline, plain water"),
           Patch(color="black", label="sleep deprivation (EEG 4 h/day, NS-SD 6 h/day)"),
           Patch(facecolor="white", edgecolor="black", label="EEG 24 h window (baseline, recovery)"),
           Line2D([], [], marker="v", ls="", color="black", ms=9, label="behaviour test"),
           Line2D([], [], marker="X", ls="", color="black", ms=12, label="tissue sampling")]
    ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=3, fontsize=11.5)
    save(fig, "01", "design-timeline")


# ---------------- 02 nanotag total sleep, change from baseline ----------------
def fig02():
    """HLBNSL: summary_per_mouse.csv (treatment − baseline; 49 and 50 have no usable baseline, so 3 vs 4).
    NS-SD: per-mouse table of the 2026-10-31 note. Effect and CI text: the two result notes."""
    s = pd.read_csv(HLBNSL / "summary_per_mouse.csv").pivot_table(
        index=["mouse", "group"], columns="period", values="total_sleep_min_per_day").dropna().reset_index()
    s["ch"] = s.treatment - s.baseline
    NSSD["ch"] = NSSD.ts_t - NSSD.ts_b
    fig, axes = plt.subplots(1, 2, figsize=SLIDE, sharey=True)
    for ax, (title, d, txt) in zip(axes, [("HLBNSL (normal sleep)", s, "SOD1 − water +11 min/day\n95 % CI −130 to +156"),
                                         ("NS-SD, before SD (days 1-6)", NSSD, "SOD1 − water +16 min/day\n95 % CI about −18 to +58")]):
        lab = []
        for x, g in enumerate(("water", "SOD1")):
            v = d.loc[d.group == g, "ch"]
            dots(ax, x, v, COL[g])
            lab.append((g, len(v)))
        pair_axis(ax, lab)
        ax.axhline(0, color="0.5", lw=1, zorder=1)
        ax.set_title(title, fontsize=15, loc="left")
        ax.text(0.98, 0.97, txt, transform=ax.transAxes, ha="right", va="top", fontsize=12.5, color="0.25")
    axes[0].set_ylabel("Total sleep, treatment − baseline\n(min/day)")
    axes[0].set_ylim(-60, 230)
    fig.tight_layout()
    save(fig, "02", "nanotag-sleep")


# ---------------- 03 hourly sleep profile on treatment ----------------
def fig03():
    """HLBNSL only: per-mouse treatment bins exported to the NAS (12 s, `sleep` = 48 s immobility score,
    `excluded` = handling/test windows), averaged per ZT hour per mouse, then mean ± SEM, as cohort.fig_zt.
    NS-SD Run 1 bins are on the office PC only (out/HLBNSSD), so its panel is not drawn here."""
    prof = {}
    for g, sub in (("SOD1", "HLBNSSL"), ("water", "HLBNWSL")):
        rows = []
        for f in sorted((NAS / sub / "Treatment").glob("*/*.csv")):
            if "HLBNSSL43" in f.name:            # died 09-28, dropped from every analysis (cohort.DROP)
                continue
            d = pd.read_csv(f, usecols=["time_kst", "excluded", "sleep"], parse_dates=["time_kst"])
            d = d[d.excluded == 0]
            rows.append(d.groupby((d.time_kst.dt.hour - 9) % 24).sleep.mean().reindex(range(24)) * 100)
        prof[g] = np.array(rows)
    fig, ax = plt.subplots(figsize=SLIDE)
    zt = np.arange(24) + 0.5
    for g in ("water", "SOD1"):
        p = prof[g]
        m, se = p.mean(0), p.std(0, ddof=1) / np.sqrt(len(p))
        ax.fill_between(zt, m - se, m + se, color=COL[g], alpha=0.2, lw=0)
        ax.plot(zt, m, "-o", color=COL[g], lw=2.4, ms=5, label=f"{g} (n = {len(p)})")
    ax.add_patch(plt.Rectangle((0, -6), 12, 4, color="white", ec="black", lw=1, clip_on=False))
    ax.add_patch(plt.Rectangle((12, -6), 12, 4, color="black", clip_on=False))
    ax.text(6, -4, "lights on", ha="center", va="center", fontsize=11)
    ax.text(18, -4, "lights off", ha="center", va="center", fontsize=11, color="white")
    ax.set_xlim(0, 24); ax.set_ylim(-6, 100)
    ax.spines["bottom"].set_bounds(0, 24); ax.spines["left"].set_bounds(0, 100)
    ax.set_xticks(range(0, 25, 3))
    ax.set_xlabel("ZT (h after lights on at 09:00)")
    ax.set_ylabel("Time asleep (% of hour)")
    ax.legend(loc="upper right", title="HLBNSL, on treatment", title_fontsize=13)
    fig.tight_layout()
    save(fig, "03", "nanotag-24h-profile")


# ---------------- 04 EEG baseline sleep ----------------
def fig04():
    """per_mouse_segments.csv, rule staging (tiers A/B), baseline window (already on treatment), all four batches."""
    e = pd.read_csv(EEG)
    e = e[(e.source == "rule") & (e.tp == "B")]
    fig, ax = plt.subplots(figsize=SLIDE)
    for k, seg in enumerate(("24h", "light", "dark")):
        for j, g in enumerate(("water", "SOD1")):
            v = e.loc[(e.segment == seg) & (e.liquid == g), "sleep_pct"]
            assert len(v) == {"water": 11, "SOD1": 10}[g]
            dots(ax, k * 2.6 + j, v, COL[g], ms=8)
    ax.set_xticks([0.5, 3.1, 5.7], ["24 h", "Light phase", "Dark phase"])
    ax.set_xlim(-0.6, 7.0); ax.set_ylim(0, 100)
    ax.set_ylabel("Sleep (NREM + REM, % of usable time)")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=WATER, ms=9, label="water (n = 11)"),
                       Line2D([], [], marker="o", ls="", color=SOD1, ms=9, label="SOD1 (n = 10)")], loc="upper right")
    fig.tight_layout()
    save(fig, "04", "eeg-baseline")


# ---------------- 05 EEG recovery − baseline ----------------
def fig05():
    """per_mouse_segments.csv, rule staging, ZT4-24, recovery − baseline in the same mouse (paired A/B windows).
    HLBSSD18 with its EMG-rail artefact epochs counted as wake: +1.5 points (hlb-eeg-sleep-overview, not in a CSV)."""
    e = pd.read_csv(EEG)
    e = e[(e.source == "rule") & (e.segment == "ZT4-24")].pivot_table(index=["mouse", "batch"], columns="tp", values="sleep_pct").dropna()
    ch = (e.R - e.B).reset_index()
    order = [("HLBWSL", "water", 0), ("HLBSSL", "SOD1", 1), ("HLBWSD", "water", 2.6), ("HLBSSD", "SOD1", 3.6)]
    fig, ax = plt.subplots(figsize=SLIDE)
    ticks = []
    for b, g, x in order:
        v = ch.loc[ch.batch == b, 0]
        dots(ax, x, v, COL[g], ms=9 if len(v) > 1 else 12)
        ticks.append((x, f"{g}\nn = {len(v)}"))
    assert [len(ch[ch.batch == b]) for b, _, _ in order] == [7, 6, 1, 1]
    ax.plot(3.6, 1.5, "o", ms=12, mfc="white", mec=SOD1, mew=2, zorder=3)
    ax.annotate("", xy=(3.6, 3.2), xytext=(3.6, 16.4), arrowprops=dict(arrowstyle="->", color="0.45", lw=1.3))
    ax.text(3.78, 1.5, "artefact epochs\ncounted as wake", va="center", fontsize=11.5, color="0.3")
    ax.text(2.78, 9.3, "HLBWSD08", va="center", fontsize=11.5, color="0.3")
    ax.text(3.78, 18.1, "HLBSSD18", va="center", fontsize=11.5, color="0.3")
    ax.axhline(0, color="0.5", lw=1, zorder=1)
    ax.set_xticks([t for t, _ in ticks], [l for _, l in ticks])
    for t, (_, g, _) in zip(ax.get_xticklabels(), order):
        t.set_color(COL[g])
    ax.text(0.5, 1.02, "Normal sleep", transform=ax.get_xaxis_transform(), ha="center", fontsize=14)
    ax.text(3.1, 1.02, "Sleep deprivation (single cases)", transform=ax.get_xaxis_transform(), ha="center", fontsize=14)
    ax.axvline(1.8, color="0.75", lw=1, ls=(0, (4, 3)))
    ax.set_xlim(-0.6, 4.9)
    ax.set_ylabel("Sleep, recovery − baseline\n(% points, ZT4-24)")
    fig.tight_layout()
    save(fig, "05", "eeg-recovery")


# ---------------- 06 behaviour ----------------
def fig06():
    panels = [("sa", "Y-maze alternation (%)", 50, (40, 80)),
              ("entries", "Y-maze arm entries", None, (0, 70)),
              ("dist", "Open-field distance (m)", None, (0, 85)),
              ("d2", "NOR discrimination index d2\n(pose model2)", 0, (-0.4, 0.8))]
    fig, axes = plt.subplots(1, 4, figsize=(12, 5))
    for ax, (k, lab, ref, ylim) in zip(axes, panels):
        a, w = BEH[k]
        dots(ax, 0, w, WATER, ms=8)
        dots(ax, 1, a, SOD1, ms=8)
        if ref is not None:
            ax.axhline(ref, color="0.5", lw=1.2, ls=(0, (4, 3)), zorder=1)
            if k == "sa":
                ax.text(1.75, ref - 0.6, "chance", fontsize=11, color="0.4", ha="right", va="top")
        pair_axis(ax, [("water", 5), ("SOD1", 4)])
        ax.set_ylim(*ylim)
        ax.set_ylabel(lab)
    fig.tight_layout(w_pad=1.5)
    save(fig, "06", "behaviour")


# ---------------- 07 activity forest plot ----------------
def fig07():
    # p: the exact rank / permutation tests of the result notes (Y-maze, OFT, NS-SD), not recomputed
    rows = [("Y-maze arm entries", "HLBNSL, 4 vs 5", "0.063", *BEH["entries"]),
            ("Open-field distance", "HLBNSL, 4 vs 5", "0.11", *BEH["dist"]),
            ("Dark-phase tag activity,\nchange from baseline", "NS-SD, 5 vs 5", "0.040",
             (NSSD.dark_t - NSSD.dark_b)[NSSD.group == "SOD1"], (NSSD.dark_t - NSSD.dark_b)[NSSD.group == "water"])]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    f = lambda x: f"{x:+.2f}".replace("+0.00", "0.00").replace("-0.00", "0.00").replace("-", "−")
    for i, (lab, coh, p, a, w) in enumerate(rows):
        g, lo, hi = hedges(a, w)
        y = len(rows) - 1 - i
        ax.plot([lo, hi], [y, y], color=SOD1, lw=3, solid_capstyle="round")
        ax.plot(g, y, "o", ms=12, color=SOD1, mec="white", mew=1.5)
        ax.text(hi + 0.15, y, f"g = {f(g)}  [{f(lo)}, {f(hi)}]\nexact p = {p}", va="center", fontsize=12)
        print(f"  {lab.splitlines()[0]}: g {g:+.2f} [{lo:+.2f}, {hi:+.2f}]")
    ax.set_yticks(range(len(rows))[::-1], [f"{l}\n{c}" for l, c, *_ in rows], fontsize=13)
    ax.axvline(0, color="0.5", lw=1.2)
    ax.set_xlim(-1.6, 5.0); ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel("Hedges g, SOD1 − water (95 % CI)")
    ax.text(0.15, -0.55, "SOD1 more active →", fontsize=11.5, color="0.4", va="bottom")
    ax.text(-0.15, -0.55, "← less active", fontsize=11.5, color="0.4", va="bottom", ha="right")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    save(fig, "07", "activity-signal")


# ---------------- 08 tissue ----------------
def fig08():
    """SOD: Cayman 706002 method, per mouse from cayman_analyse.py (hippoSOD_cayman.csv, heartSOD_cayman.csv).
    MDA: per mouse = (mean OD − intercept) / slope of the linear standard fit, cayman_analyse.mda_values('sheet')."""
    hip = pd.read_csv(TISSUE / "hippoSOD_cayman.csv")
    hea = pd.read_csv(TISSUE / "heartSOD_cayman.csv")
    s = pd.read_csv(TISSUE / "samples.csv"); st_ = pd.read_csv(TISSUE / "standards.csv")
    mda = s[s.assay == "MDA"].copy()
    std = st_[st_.assay == "MDA"]
    b, a = np.polyfit(std.conc, std[["od1", "od2"]].mean(axis=1), 1)
    mda["y"] = (mda[["od1", "od2"]].mean(axis=1) - a) / b
    panels = [(hip, "Hippocampal total SOD\n(U/mL homogenate)"), (mda, "Hippocampal MDA\n(nmol/well)"),
              (hea, "Heart total SOD\n(U/mL homogenate)")]
    order = [("W-SL", "water", 0), ("S-SL", "SOD1", 1), ("W-SD", "water", 2.5), ("S-SD", "SOD1", 3.5)]
    fig, axes = plt.subplots(1, 3, figsize=(12, 5.2))
    for ax, (d, lab) in zip(axes, panels):
        for grp, g, x in order:
            v = d.loc[d.group == grp, "y"]
            dots(ax, x, v, COL[g], ms=7)
            print(f"  {lab.splitlines()[0]} {grp}: {v.mean():.2f} (n {len(v)})")
        ax.set_xticks([x for *_, x in order], [f"{g}\n{len(d[d.group == grp])}" for grp, g, _ in order], fontsize=12)
        for t, (_, g, _) in zip(ax.get_xticklabels(), order):
            t.set_color(COL[g])
        for xc, txt in ((0.5, "Normal\nsleep"), (3.0, "SD")):
            ax.text(xc, -0.2, txt, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=13)
        ax.set_xlim(-0.6, 4.2)
        ax.set_ylim(0, None)
        ax.set_ylabel(lab)
    fig.text(0.01, 0.01, "n under each group", fontsize=10.5, color="0.4")
    fig.tight_layout(w_pad=2)
    save(fig, "08", "tissue")


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08}

if __name__ == "__main__":
    for k in sys.argv[1:] or FIGS:
        FIGS[k]()

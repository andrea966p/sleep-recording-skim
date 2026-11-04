#!/usr/bin/env python3
"""Behaviour section of the 2026-11-05 lab meeting deck (v2): HLBNSL battery and NS-SD Y-maze after SD.

    uv run -q --no-project --with openpyxl --with numpy --with scipy --with matplotlib \
        python nanotag/analysis/report/labmtg/behaviour.py

(openpyxl only because behavior/ymaze_report.py imports it.) Writes
/home/andrea/hlb_meeting_deck/v2/fig/behaviour_NN_*.png/.pdf and prints every number the figures show.

Sources (no re-tuning, methods as documented in BEHAVIOR_SOP.md):
- HLBNSL Y-maze SA % / entries: re-scored here from the hand sequences in the vault note
  2026-10-25-HLBNSL-ymaze-hand-scoring (ymaze_report.read_hand + hand_scores = metrics.py), checked
  against the per-mouse table of 2026-10-25-HLBNSL-ymaze-hand-scored-results (lines 37-45).
  EthoVision distance: that table, copied below (raw EthoVision export is on kaist-bilab-win).
- NS-SD Y-maze: re-scored from behavior/NSSD_ymaze_hand_scoring.csv (ymaze_nssd.read_sheet + score),
  checked against out/HLBNSSD/ymaze/NSSD_ymaze_results.csv.
- HLBNSL open field: per-mouse table of 2026-10-25-HLBNSL-oft-day1-results (lines 73-81, pose model2),
  copied below (raw pose tracks are on kaist-bilab-win).
- HLBNSL NOR: ~/nor-scoring/.pose/forepaws_count/nor_results_model{1,2}.csv (revised forepaw rule,
  2026-11-02), the files behind 2026-11-02-HLBNSL-nor-hand-validation-and-calibration.

Statistics (BEHAVIOR_SOP section 5): per group exact Wilcoxon vs chance; SOD1 vs water exact
Mann-Whitney U, mean difference with Welch 95 % CI, Hedges g (ymaze_report.hedges_g / welch_ci).
Added for the deck: normal-approximation 95 % CI of g, and the minimum detectable effect (two-sample
t, alpha 0.05 two-sided, power 0.8) as a sensitivity statement, never as observed power.
"""
import csv, os, statistics as st, sys
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.optimize import brentq

REPO = Path(__file__).resolve().parents[4]
BEH = REPO / "nanotag" / "analysis" / "behavior"
sys.path.insert(0, str(BEH))
from ymaze_report import read_hand, hand_scores, hedges_g, welch_ci  # noqa: E402
from ymaze_nssd import read_sheet, score                              # noqa: E402
from metrics import spontaneous_alternation, discrimination_index    # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from style import *  # noqa: F401,F403,E402  (imported last so its rcParams win over cohort.py's)
import matplotlib.pyplot as plt                                       # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon  # noqa: E402

OUT = Path("/home/andrea/hlb_meeting_deck/v2/fig")
VAULT = REPO / "vault" / "10-projects" / "hlb-sod1"
NOR_DIR = Path.home() / "nor-scoring" / ".pose" / "forepaws_count"
NSSD_CSV = REPO / "nanotag" / "analysis" / "out" / "HLBNSSD" / "ymaze" / "NSSD_ymaze_results.csv"
CHANCE_SA = 50.0
ANN = 12              # annotation font size

# 2026-10-25-HLBNSL-ymaze-hand-scored-results.md lines 37-45: EthoVision distance (m), velocity (cm/s),
# and the hand SA % / entries used only as a check of the re-scoring.
YM_TABLE = {"HLBNSSL41": (63.2, 59, 41.9), "HLBNSSL42": (64.7, 53, 39.0), "HLBNSSL44": (60.5, 40, 29.3),
            "HLBNSSL49": (53.8, 41, 30.3), "HLBNWSL45": (66.7, 47, 34.8), "HLBNWSL46": (62.2, 39, 32.3),
            "HLBNWSL47": (69.4, 38, 30.3), "HLBNWSL48": (58.8, 36, 28.8), "HLBNWSL50": (56.7, 32, 25.8)}
# 2026-10-25-HLBNSL-oft-day1-results.md lines 73-81 (pose model2, 600 s, 50 x 50 cm):
# distance m, speed cm/s, immobile s, centre %, centre entries, thigmotaxis %
OFT = {"HLBNSSL41": (74.1, 12.35, 26.2, 17.6, 59, 33.4), "HLBNSSL42": (68.7, 11.44, 22.7, 27.5, 65, 27.0),
       "HLBNSSL44": (60.4, 10.07, 95.8, 19.4, 48, 30.4), "HLBNSSL49": (52.5, 8.74, 117.7, 10.1, 41, 28.2),
       "HLBNWSL45": (49.5, 8.26, 156.8, 13.6, 43, 37.5), "HLBNWSL46": (55.1, 9.18, 87.7, 14.3, 39, 25.8),
       "HLBNWSL47": (52.9, 8.82, 126.1, 24.3, 42, 28.7), "HLBNWSL48": (52.8, 8.80, 142.8, 7.6, 27, 59.9),
       "HLBNWSL50": (45.1, 7.51, 160.7, 19.6, 36, 37.4)}
OFT_KEYS = ("distance_m", "speed_cms", "immobile_s", "centre_pct", "centre_entries", "thigmo_pct")


def grp(mouse):
    """HLBNS.. = SOD1, HLBNW.. = water (cohort naming)"""
    return {"S": "SOD1", "W": "water"}[mouse[4]]


def split(d):
    """{mouse: value} -> {'water': [...], 'SOD1': [...]} in mouse order"""
    return {g: [v for m, v in sorted(d.items()) if grp(m) == g] for g in ORDER}


# ---------------------------------------------------------------- statistics

def sem(v):
    return st.stdev(v) / len(v) ** .5


def compare(a_sod1, b_water):
    """SOD1 - water: diff, Welch CI, Hedges g (+ approx CI), exact Mann-Whitney p"""
    a, b = a_sod1, b_water
    lo, hi = welch_ci(a, b)
    g = hedges_g(a, b)
    n1, n2 = len(a), len(b)
    se_g = ((n1 + n2) / (n1 * n2) + g * g / (2 * (n1 + n2))) ** .5
    p = stats.mannwhitneyu(a, b, method="exact").pvalue
    return dict(diff=st.mean(a) - st.mean(b), lo=lo, hi=hi, g=g, glo=g - 1.96 * se_g, ghi=g + 1.96 * se_g, p=p,
                ma=st.mean(a), mb=st.mean(b), sa=sem(a), sb=sem(b), na=n1, nb=n2)


def vs_chance(v, c):
    return stats.wilcoxon([x - c for x in v], method="exact").pvalue


def mde_d(n1, n2, power=0.8, alpha=0.05):
    """smallest standardised difference a two-sided two-sample t-test detects with this power"""
    df, k = n1 + n2 - 2, (n1 * n2 / (n1 + n2)) ** .5
    tc = stats.t.ppf(1 - alpha / 2, df)
    # the lower tail is ~0 and scipy returns NaN for it at large noncentrality
    f = lambda d: stats.nct.sf(tc, df, d * k) + np.nan_to_num(stats.nct.cdf(-tc, df, d * k)) - power
    return brentq(f, 0.01, 6)


def pooled_sd(a, b):
    return (((len(a) - 1) * st.variance(a) + (len(b) - 1) * st.variance(b)) / (len(a) + len(b) - 2)) ** .5


def line(tag, c, unit=""):
    s = (f"{tag}: SOD1 {c['ma']:.2f} ± {c['sa']:.2f} (n={c['na']}) vs water {c['mb']:.2f} ± {c['sb']:.2f} "
         f"(n={c['nb']}); diff {c['diff']:+.2f}{unit} (Welch 95% CI {c['lo']:+.2f} to {c['hi']:+.2f}), "
         f"Hedges g {c['g']:+.2f} (approx CI {c['glo']:+.2f} to {c['ghi']:+.2f}), Mann-Whitney exact p={c['p']:.3f}")
    print("  " + s)


# ---------------------------------------------------------------- plotting helpers

def fmt_p(p):
    return f"p = {p:.3f}"


def sg(x, dp):
    """signed number with a true minus sign"""
    return f"{x:+.{dp}f}".replace("-", "\u2212")


def group_dots(ax, x, v, colour, marker="o", hollow=False, edge=None, seed=0):
    """dots = mice (deterministic jitter), black mean ± SEM bar"""
    jit = (np.arange(len(v)) - (len(v) - 1) / 2) * 0.075
    order = np.argsort(v)
    ax.scatter(x + jit, np.asarray(v)[order], s=95, marker=marker, zorder=3,
               facecolor="white" if hollow else colour, edgecolor=edge or colour, linewidth=1.8)
    mu, se = st.mean(v), sem(v)
    ax.hlines(mu, x - 0.27, x + 0.27, color=INK, lw=2.6, zorder=4)
    ax.errorbar(x, mu, se, fmt="none", ecolor=INK, elinewidth=1.8, capsize=7, capthick=1.8, zorder=4)


def two_group(ax, d, title, ylabel, ylim, chance=None, unit="", dp=1, cond="NS", marker="o", xs=(0, 1),
              chance_lab=None):
    """water left, SOD1 right; annotation = difference (95 % CI), exact Mann-Whitney p, Hedges g"""
    c = compare(d["SOD1"], d["water"])
    labels = []
    for x, g in zip(xs, ORDER):
        group_dots(ax, x, d[g], COL[(g, cond)], marker=marker,
                   edge=None if cond == "NS" else (WATER if g == "water" else SOD1))
        labels.append(f"{g}\nn = {len(d[g])}")
        if chance is not None:
            ax.text(x, ylim[0] + 0.03 * (ylim[1] - ylim[0]),
                    f"vs {chance_lab or chance}\n{fmt_p(vs_chance(d[g], chance))}", ha="center", va="bottom",
                    fontsize=11.5, color="#444444")
    if chance is not None:
        ax.axhline(chance, color=CHANCE, ls="--", lw=1.4, zorder=0)
        ax.text(xs[0] - 0.55, chance, "chance", ha="left", va="bottom", fontsize=11.5, color="#555555")
    ax.set_ylim(*ylim)
    ax.set_xticks(xs, labels)
    ax.set_xlim(xs[0] - 0.6, xs[1] + 0.6)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    span = ylim[1] - ylim[0]
    top = ylim[1] - 0.04 * span
    ax.text((xs[0] + xs[1]) / 2, top,
            f"SOD1 − water {sg(c['diff'], dp)}{unit}\n95 % CI {sg(c['lo'], dp)} to {sg(c['hi'], dp)}\n"
            f"{fmt_p(c['p'])}, g = {sg(c['g'], 2)}", ha="center", va="top", fontsize=ANN, linespacing=1.25)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    return c


# ---------------------------------------------------------------- data

def load_ymaze():
    seqs = read_hand(VAULT / "2026-10-25-HLBNSL-ymaze-hand-scoring.md")
    assert len(seqs) == 9, seqs.keys()
    rested = {}
    for m, s in seqs.items():
        pct, n, *_ = hand_scores(s)
        rested[m] = (round(pct, 1), n)      # 1 decimal, as in the vault tables and ymaze_nssd.score
        t_sa, t_n, _ = YM_TABLE[m]
        assert round(pct, 1) == t_sa and n == t_n, f"{m}: re-scored {pct:.1f}/{n} vs vault {t_sa}/{t_n}"
    sd_rows = score(read_sheet(BEH / "NSSD_ymaze_hand_scoring.csv"))
    with open(NSSD_CSV, newline="") as fh:
        ref = {r["mouse"]: r for r in csv.DictReader(fh)}
    for r in sd_rows:
        assert abs(r["sa_pct"] - float(ref[r["mouse"]]["sa_pct"])) < 0.05 and \
            r["arm_entries"] == int(ref[r["mouse"]]["arm_entries"]), r["mouse"]
    return rested, {r["mouse"]: r for r in sd_rows}


def load_nor(model):
    with open(NOR_DIR / f"nor_results_{model}.csv", newline="") as fh:
        rows = {r["mouse"]: {k: (v if k in ("mouse", "group", "exclusions") else float(v)) for k, v in r.items()}
                for r in csv.DictReader(fh)}
    assert len(rows) == 9 and not any(r["exclusions"] for r in rows.values())
    for r in rows.values():
        assert grp(r["mouse"]) == r["group"]
        assert abs(discrimination_index(r["T2_novel_s"], r["T2_familiar_s"]) - r["d2"]) < 0.002
        r["T1_lowright"] = r["T1_B_s"] / r["T1_total_s"]   # T1 object B = lower-right spot (nor_explore.py:124)
        r["T2_novel_share"] = r["T2_novel_s"] / r["T2_total_s"]
    return rows


# ---------------------------------------------------------------- figures

def fig01_battery():
    """schematic: test days, what each test measures, who/what scores it"""
    fig = plt.figure(figsize=TALL)
    ax = fig.add_axes([0.005, 0.005, 0.99, 0.99])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    def box(x, y, w, h, title, body, fc, ec):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=fc, ec=ec, lw=1.6))
        ax.text(x + 0.12, y + h - 0.12, title, ha="left", va="top", fontsize=14, fontweight="bold")
        ax.text(x + 0.12, y + h - 0.55, body, ha="left", va="top", fontsize=12.5, linespacing=1.3)

    ax.text(0, 6.05, "HLBNSL, normal sleep (water 5, SOD1 4): tests from 15:00 (ZT6), one mouse at a time, "
            "all SOD1 mice tested first", fontsize=14.5, fontweight="bold", va="top")
    y, h = 3.35, 2.3
    box(0.0, y, 3.7, h, "Day 0, 09-30: Y-maze",
        "8 min; working memory: spontaneous\nalternation (SA %), arm entries\n"
        "SA %, entries: hand-scored letters\n(all four paws), Andrea\n"
        "distance: EthoVision XT 11.5", "#F4F8FB", WATER)
    box(4.05, y, 3.7, h, "Day 1, 10-01: open field",
        "10 min, 50 x 50 cm: locomotion (distance,\nimmobility), anxiety-like (centre,\nwall time); = NOR habituation\n"
        "YOLO pose model2 (primary),\nmodel1 cross-check (r ≥ 0.995)", "#F4F8FB", WATER)
    box(8.1, y, 3.9, h, "Day 2, 10-02: NOR",
        "recognition memory: T1 two red pyramids\n(10 min), 2 h home cage, T2 pyramid +\n"
        "blue prism = novel (10 min), sampling\n"
        "YOLO pose model1 (headline) and model2;\nBORIS blinded hand check, 6 clips", "#F4F8FB", WATER)
    for x0 in (3.7, 7.75):
        ax.annotate("", (x0 + 0.33, y + h / 2), (x0 + 0.02, y + h / 2),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.5))

    ax.text(0, 2.95, "NS-SD, after sleep deprivation (water 5, SOD1 5): NOR dropped (2026-10-30 decision)",
            fontsize=14.5, fontweight="bold", va="top")
    y2, h2 = 0.55, 1.95
    box(0.0, y2, 3.7, h2, "11-03: SD 09:00-15:00",
        "gentle handling;\nrecovery sleep that night", "#FDF6EE", SOD1_SD)
    box(4.05, y2, 3.7, h2, "11-04: SD 09:00 to test",
        "kept awake until each mouse's\nY-maze: 6.0 to 8.25 h (approx.)", "#FDF6EE", SOD1_SD)
    box(8.1, y2, 3.9, h2, "11-04, 15:00: Y-maze",
        "8 min, order 51, 56, 52, 57 ... interleaved\nhand-scored letters, same rules;\nthen sampling", "#FDF6EE", SOD1_SD)
    for x0 in (3.7, 7.75):
        ax.annotate("", (x0 + 0.33, y2 + h2 / 2), (x0 + 0.02, y2 + h2 / 2),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.5))
    ax.text(0, 0.22, "Validation: Y-maze hand vs EthoVision SA % r = +0.88 (EthoVision lower in 8/9, mean |Δ| 5.3 pts)\n"
            "NOR: two blinded raters frame kappa 0.76; pose vs hand d2 within 0.01-0.06 (model1)",
            fontsize=12.5, va="center", color="#444444", linespacing=1.35)
    save(fig, OUT / "behaviour_01_battery")


def fig02_methods():
    """how each endpoint is computed: Y-maze triplets, open-field zones, NOR d2"""
    seq = "ABCACBAAB"
    alts, n, pct = spontaneous_alternation(list(seq))
    assert (alts, n, round(pct, 1)) == (4, 9, 57.1)
    fig, axs = plt.subplots(1, 3, figsize=WIDE, layout="constrained", gridspec_kw=dict(width_ratios=[1.1, 1, 1]))
    for a in axs:
        a.set_aspect("equal")
        a.axis("off")
    # Y-maze
    a = axs[0]
    a.set_xlim(-1.6, 1.6)
    a.set_ylim(-2.75, 1.5)
    for ang, lab in ((90, "A"), (210, "B"), (330, "C")):
        r = np.deg2rad(ang)
        a.plot([0, np.cos(r)], [0, np.sin(r)], color=INK, lw=14, solid_capstyle="butt", alpha=0.15)
        a.text(1.22 * np.cos(r), 1.22 * np.sin(r), lab, ha="center", va="center", fontsize=16, fontweight="bold")
    a.set_title("Y-maze (8 min)", loc="center")
    xs = np.linspace(-1.45, 1.45, len(seq))
    for i, ch in enumerate(seq):
        a.text(xs[i], -1.35, ch, ha="center", va="center", fontsize=15, family="DejaVu Sans Mono")
    for i in range(n - 2):
        ok = len(set(seq[i:i + 3])) == 3
        a.plot([xs[i], xs[i + 2]], [-1.6 - 0.1 * (i % 2)] * 2, color="#009E73" if ok else "#BBBBBB", lw=3)
    a.text(0, -1.9, f"green = 3 different arms in a row\n{alts} alternations / ({n} entries − 2) = {pct:.0f} %\nchance = 50 %",
           ha="center", va="top", fontsize=13)
    # open field
    a = axs[1]
    a.set_xlim(-5, 55)
    a.set_ylim(-14, 58)
    a.add_patch(Rectangle((0, 0), 50, 50, fc="#EEF4F8", ec=INK, lw=1.8))
    a.add_patch(Rectangle((5, 5), 40, 40, fc="white", ec=WATER, lw=1.2, ls="--"))
    a.add_patch(Rectangle((12.5, 12.5), 25, 25, fc="#DCEFE6", ec="#009E73", lw=1.5))
    a.text(25, 25, "centre\n25 x 25 cm", ha="center", va="center", fontsize=12.5)
    a.text(25, 2.3, "wall band 5 cm", ha="center", va="center", fontsize=11.5)
    a.set_title("Open field (10 min)", loc="center")
    a.text(25, -3, "distance, immobility\n(< 2 cm/s for ≥ 2 s),\ncentre time %, wall-band %",
           ha="center", va="top", fontsize=12.5)
    # NOR
    a = axs[2]
    a.set_xlim(-5, 55)
    a.set_ylim(-14, 58)
    a.add_patch(Rectangle((0, 0), 50, 50, fc="#FBF3EC", ec=INK, lw=1.8))
    a.add_patch(Polygon([[11, 34], [17, 34], [14, 41]], fc="#C0392B", ec=INK))
    a.add_patch(Polygon([[33, 13], [39, 13], [36, 20]], fc="#2E86C1", ec=INK))
    a.add_patch(Circle((14, 37), 5.3, fc="none", ec=INK, ls=":", lw=1.2))
    a.text(14, 47, "familiar", ha="center", fontsize=12.5)
    a.text(36, 25, "novel (T2)", ha="center", fontsize=12.5)
    a.set_title("NOR test trial (T2)", loc="center")
    a.text(25, -3, "d2 = (N − F) / (N + F)\nN, F = s exploring novel, familiar\nchance = 0", ha="center", va="top", fontsize=12.5)
    save(fig, OUT / "behaviour_02_methods")


def fig03_ymaze(rested):
    print("\n[fig 03] HLBNSL Y-maze (hand-scored; distance EthoVision)")
    sa = split({m: v[0] for m, v in rested.items()})
    en = split({m: v[1] for m, v in rested.items()})
    dist = split({m: v[2] for m, v in YM_TABLE.items()})
    fig, axs = plt.subplots(1, 3, figsize=WIDE, layout="constrained")
    c1 = two_group(axs[0], sa, "Spontaneous alternation", "SA (%)", (0, 112), chance=CHANCE_SA, unit=" pts",
                   chance_lab="50 %")
    c2 = two_group(axs[1], en, "Arm entries (8 min)", "entries", (0, 85))
    c3 = two_group(axs[2], dist, "Distance (EthoVision)", "distance (m)", (0, 60), unit=" m")
    for g in ORDER:
        print(f"  SA% {g}: n={len(sa[g])} mean {st.mean(sa[g]):.2f} ± {sem(sa[g]):.2f}, "
              f"vs 50 % Wilcoxon exact p={vs_chance(sa[g], 50):.4f}, mice above 50: {sum(x > 50 for x in sa[g])}")
    line("SA%", c1, " pts")
    line("arm entries", c2)
    line("distance (m)", c3, " m")
    r = stats.pearsonr([v[1] for v in rested.values()], [v[0] for v in rested.values()])
    print(f"  control check entries vs SA%: Pearson r={r.statistic:+.2f} p={r.pvalue:.2f}")
    save(fig, OUT / "behaviour_03_ymaze_rested")
    return c1, c2


def fig04_oft():
    print("\n[fig 04] HLBNSL open field (pose model2)")
    col = {k: split({m: v[i] for m, v in OFT.items()}) for i, k in enumerate(OFT_KEYS)}
    fig, axs = plt.subplots(1, 4, figsize=WIDE, layout="constrained")
    cs = {}
    cs["distance_m"] = two_group(axs[0], col["distance_m"], "Distance", "m in 10 min", (0, 100), unit=" m")
    cs["immobile_s"] = two_group(axs[1], col["immobile_s"], "Immobility", "s in 10 min", (0, 260), unit=" s", dp=0)
    cs["centre_pct"] = two_group(axs[2], col["centre_pct"], "Centre time", "% of 10 min", (0, 50), unit=" pts")
    cs["thigmo_pct"] = two_group(axs[3], col["thigmo_pct"], "Wall band (5 cm)", "% of 10 min", (0, 100), unit=" pts")
    cs["speed_cms"] = compare(col["speed_cms"]["SOD1"], col["speed_cms"]["water"])
    cs["centre_entries"] = compare(col["centre_entries"]["SOD1"], col["centre_entries"]["water"])
    for k in OFT_KEYS:
        line(k, cs[k])
    save(fig, OUT / "behaviour_04_openfield")
    return cs


def fig05_nor(n1, n2):
    print("\n[fig 05] HLBNSL NOR (pose, revised forepaw rule)")
    d1 = split({m: r["d2"] for m, r in n1.items()})
    d2 = split({m: r["d2"] for m, r in n2.items()})
    fig, axs = plt.subplots(1, 4, figsize=WIDE, layout="constrained",
                            gridspec_kw=dict(width_ratios=[1.15, 1.15, 1.1, 1.0]))
    c1 = two_group(axs[0], d1, "d2, model1", "discrimination index d2", (-1, 1.25), chance=0, dp=2,
                   chance_lab="0")
    c2 = two_group(axs[1], d2, "d2, model2", "", (-1, 1.25), chance=0, dp=2, chance_lab="0")
    for a in axs[:2]:
        a.set_yticks([-1, -0.5, 0, 0.5, 1])
    # exploration totals, model1, T1 and T2
    a = axs[2]
    for k, (key, off) in enumerate((("T1_total_s", 0), ("T2_total_s", 2.6))):
        v = split({m: r[key] for m, r in n1.items()})
        for x, g in zip((off, off + 1), ORDER):
            group_dots(a, x, v[g], COL[(g, "NS")])
        c = compare(v["SOD1"], v["water"])
        a.text(off + 0.5, 92, f"{key[:2]}: {sg(c['diff'], 1)} s\n{fmt_p(c['p'])}", ha="center", va="top", fontsize=ANN)
        line(f"{key} model1", c, " s")
    a.axhline(20, color=CHANCE, ls=":", lw=1.3)
    a.text(4.2, 21, "20 s minimum", ha="right", va="bottom", fontsize=11, color="#555555")
    a.set_xticks([0.5, 3.1], ["T1", "T2"])
    a.set_xlim(-0.6, 4.2)
    a.set_ylim(0, 95)
    a.set_ylabel("exploration (s), model1")
    a.set_title("Exploration")
    a.yaxis.grid(True, color=GRID, lw=0.8)
    a.set_axisbelow(True)
    # side check, model1: share at the lower-right spot, T1 (identical objects) -> T2 (novel there)
    a = axs[3]
    t1 = [r["T1_lowright"] for r in n1.values()]
    t2 = [r["T2_novel_share"] for r in n1.values()]
    for r in n1.values():
        cc = COL[(r["group"], "NS")]
        a.plot([0, 1], [r["T1_lowright"], r["T2_novel_share"]], color=cc, lw=1.6, marker="o", ms=8, mfc=cc,
               mec="white", alpha=0.9)
    w = stats.wilcoxon(np.array(t2) - np.array(t1), method="exact").pvalue
    a.axhline(0.5, color=CHANCE, ls="--", lw=1.4, zorder=0)
    a.set_xticks([0, 1], ["T1\nidentical", "T2\nnovel here"])
    a.set_xlim(-0.35, 1.35)
    a.set_ylim(0.3, 1.0)
    a.set_ylabel("share at lower-right spot")
    a.set_title("Spot check")
    rose = sum(b > x for x, b in zip(t1, t2))
    a.text(0.5, 0.98, f"{st.mean(t1):.2f} → {st.mean(t2):.2f}\n{rose}/9 rose, {fmt_p(w)}",
           ha="center", va="top", fontsize=ANN)
    a.plot([], [], color=WATER, lw=2, label="water")
    a.plot([], [], color=SOD1, lw=2, label="SOD1")
    a.legend(loc="lower right", fontsize=12)
    for g in ORDER:
        print(f"  d2 model1 {g}: mean {st.mean(d1[g]):+.3f} ± {sem(d1[g]):.3f}, vs 0 Wilcoxon p={vs_chance(d1[g], 0):.3f}; "
              f"model2 {st.mean(d2[g]):+.3f} ± {sem(d2[g]):.3f}, vs 0 p={vs_chance(d2[g], 0):.3f}")
    line("d2 model1", c1)
    line("d2 model2", c2)
    for nm, rows in (("model1", n1), ("model2", n2)):
        allv = [r["d2"] for r in rows.values()]
        s1 = [r["T1_lowright"] for r in rows.values()]
        s2 = [r["T2_novel_share"] for r in rows.values()]
        print(f"  {nm} pooled d2 {st.mean(allv):+.3f}, {sum(x > 0 for x in allv)}/9 > 0, Wilcoxon p={vs_chance(allv, 0):.4f};"
              f" novel share {st.mean(s2):.3f}; side check {st.mean(s1):.3f} -> {st.mean(s2):.3f}, "
              f"{sum(b > a_ for a_, b in zip(s1, s2))}/9 rose, p={stats.wilcoxon(np.array(s2) - np.array(s1), method='exact').pvalue:.4f}")
    print(f"  model1 vs model2 d2 per mouse: Pearson r={stats.pearsonr([n1[m]['d2'] for m in n1], [n2[m]['d2'] for m in n1]).statistic:+.3f}")
    save(fig, OUT / "behaviour_05_nor")
    return c1, c2


def fig06_sd(rested, sd):
    print("\n[fig 06] Y-maze after SD (NS-SD) next to rested (HLBNSL); descriptive, different batches")
    r_sa = split({m: v[0] for m, v in rested.items()})
    r_en = split({m: v[1] for m, v in rested.items()})
    s_sa = split({m: r["sa_pct"] for m, r in sd.items()})
    s_en = split({m: r["arm_entries"] for m, r in sd.items()})
    fig, axs = plt.subplots(1, 2, figsize=WIDE, layout="constrained")
    out = {}
    for a, (rv, sv, ttl, yl, ylim, ch, unit) in zip(axs[:2], (
            (r_sa, s_sa, "Spontaneous alternation", "SA (%)", (0, 118), CHANCE_SA, " pts"),
            (r_en, s_en, "Arm entries (8 min)", "entries", (0, 88), None, ""))):
        cr = two_group(a, rv, ttl, yl, ylim, chance=ch, unit=unit, xs=(0, 1), chance_lab="50 %")
        cs = two_group(a, sv, ttl, yl, ylim, chance=ch, unit=unit, cond="SD", marker="^", xs=(2.8, 3.8),
                       chance_lab="50 %")
        a.set_xticks([0, 1, 2.8, 3.8], [f"{g}\nn = {len(v[g])}" for v in (rv, sv) for g in ORDER])
        a.set_xlim(-0.6, 4.4)
        a.axvline(1.9, color=GRID, lw=1.5)
        for xc, lab in ((0.5, "rested\nHLBNSL, 09-30"), (3.3, "after 2 d SD\nNS-SD, 11-04")):
            a.text(xc, -0.2, lab, transform=a.get_xaxis_transform(), ha="center", va="top", fontsize=13.5,
                   fontweight="bold")
        out[ttl] = (cr, cs)
    save(fig, OUT / "behaviour_06_ymaze_sd_vs_rested")
    # backup figure: SA % vs SD length (approximate: 15:00 + 15 min x test position)
    fig, a = plt.subplots(figsize=HALF, layout="constrained")
    for g in ORDER:
        rows = [r for r in sd.values() if r["group"] == g]
        a.scatter([r["sd_h"] for r in rows], [r["sa_pct"] for r in rows], s=95, marker="^",
                  facecolor=COL[(g, "SD")], edgecolor=WATER if g == "water" else SOD1, lw=1.8, label=g, zorder=3)
    xs_ = [r["sd_h"] for r in sd.values()]
    ys_ = [r["sa_pct"] for r in sd.values()]
    pr = stats.pearsonr(xs_, ys_)
    a.axhline(CHANCE_SA, color=CHANCE, ls="--", lw=1.4, zorder=0)
    a.set_ylim(0, 118)
    a.set_xlim(5.8, 8.45)
    a.set_xticks([6, 6.5, 7, 7.5, 8])
    a.set_xlabel("SD length on 11-04 (h, approx.)")
    a.set_ylabel("SA (%)")
    a.set_title("NS-SD: SA vs SD length")
    a.text(7.1, 114, f"r = {sg(pr.statistic, 2)}, {fmt_p(pr.pvalue)}\nn = 10", ha="center", va="top", fontsize=ANN)
    a.legend(loc="lower right", fontsize=12)
    a.yaxis.grid(True, color=GRID, lw=0.8)
    a.set_axisbelow(True)
    for tag, rv, sv in (("SA%", r_sa, s_sa), ("entries", r_en, s_en)):
        for g in ORDER:
            print(f"  {tag} {g}: rested {st.mean(rv[g]):.2f} ± {sem(rv[g]):.2f} (n={len(rv[g])}) | "
                  f"SD {st.mean(sv[g]):.2f} ± {sem(sv[g]):.2f} (n={len(sv[g])})"
                  + (f"; vs 50 %: rested p={vs_chance(rv[g], 50):.3f}, SD p={vs_chance(sv[g], 50):.3f}"
                     if tag == "SA%" else ""))
    line("NS-SD SA%", out["Spontaneous alternation"][1], " pts")
    line("NS-SD entries", out["Arm entries (8 min)"][1])
    line("HLBNSL SA%", out["Spontaneous alternation"][0], " pts")
    line("HLBNSL entries", out["Arm entries (8 min)"][0])
    print(f"  NS-SD SD length vs SA%: Pearson r={pr.statistic:+.3f} p={pr.pvalue:.3f}, n={len(xs_)}")
    # descriptive rested-minus-SD per arm (different batches: NOT a test of SD)
    for g in ORDER:
        lo, hi = welch_ci(r_sa[g], s_sa[g])
        print(f"  descriptive only, {g}: rested − SD SA% {st.mean(r_sa[g]) - st.mean(s_sa[g]):+.1f} pts "
              f"(Welch 95% CI {lo:+.1f} to {hi:+.1f}); different batches, not a causal SD estimate")
    save(fig, OUT / "behaviour_08_sa_vs_sd_length")
    return out


def fig07_forest(rows):
    """Hedges g (SOD1 − water) with approx. 95 % CI per endpoint, against the MDE at that n"""
    print("\n[fig 07] effect sizes and what each n can detect (two-sample t sensitivity, power 0.8)")
    fig, ax = plt.subplots(figsize=TALL, layout="constrained")
    ys = np.arange(len(rows))[::-1]
    for y, (lab, c, cond, raw, unit) in zip(ys, rows):
        colr = "#444444" if cond == "NS" else SOD1_SD
        ax.plot([c["glo"], c["ghi"]], [y, y], color=colr, lw=2.4)
        ax.plot(c["g"], y, "o" if cond == "NS" else "^", color=colr, ms=11, mec="white", mew=1.2)
        m = mde_d(c["na"], c["nb"])
        ax.plot([-m, m], [y, y], "|", color="#999999", ms=16, mew=2)
        ax.text(5.25, y, f"{sg(c['diff'], 2 if 'd2' in lab else 1)}{unit}   {fmt_p(c['p'])}", va="center",
                ha="left", fontsize=12.5)
        raw_mde = m * raw
        print(f"  {lab}: g {c['g']:+.2f} ({c['glo']:+.2f} to {c['ghi']:+.2f}), n {c['nb']} vs {c['na']}, "
              f"MDE d {m:.2f} = {raw_mde:.2f}{unit} at pooled SD {raw:.2f}")
    ax.axvline(0, color=INK, lw=1.2)
    ax.set_yticks(ys, [r[0] for r in rows])
    ax.set_xlim(-5, 5)
    ax.set_xlabel("Hedges g, SOD1 − water (dot), approx. 95 % CI (line); grey ticks = ± MDE at this n")
    ax.text(5.25, len(rows) - 0.55, "difference, Mann-Whitney", fontsize=12.5, fontweight="bold", va="bottom")
    ax.set_title("SOD1 − water, every endpoint (● rested, ▲ after SD)")
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, OUT / "behaviour_07_effect_sizes")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rested_y, sd = load_ymaze()
    rested = {m: (v[0], v[1], YM_TABLE[m][2]) for m, v in rested_y.items()}
    n1, n2 = load_nor("model1"), load_nor("model2")
    print("Behaviour section, numbers as shown in the figures (SOD1 − water throughout)")
    fig01_battery()
    fig02_methods()
    ysa, yen = fig03_ymaze(rested)
    oft = fig04_oft()
    d1, _ = fig05_nor(n1, n2)
    sdc = fig06_sd(rested, sd)
    sp = lambda d: pooled_sd(d["SOD1"], d["water"])
    r_sa = split({m: v[0] for m, v in rested.items()})
    r_en = split({m: v[1] for m, v in rested.items()})
    s_sa = split({m: r["sa_pct"] for m, r in sd.items()})
    s_en = split({m: r["arm_entries"] for m, r in sd.items()})
    o = {k: split({m: v[i] for m, v in OFT.items()}) for i, k in enumerate(OFT_KEYS)}
    nd = split({m: r["d2"] for m, r in n1.items()})
    fig07_forest([
        ("Y-maze SA %, rested", ysa, "NS", sp(r_sa), " pts"),
        ("Y-maze SA %, after SD", sdc["Spontaneous alternation"][1], "SD", sp(s_sa), " pts"),
        ("NOR d2 (model1), rested", d1, "NS", sp(nd), ""),
        ("Y-maze entries, rested", yen, "NS", sp(r_en), ""),
        ("Y-maze entries, after SD", sdc["Arm entries (8 min)"][1], "SD", sp(s_en), ""),
        ("OFT distance, rested", oft["distance_m"], "NS", sp(o["distance_m"]), " m"),
        ("OFT immobility, rested", oft["immobile_s"], "NS", sp(o["immobile_s"]), " s"),
        ("OFT centre time, rested", oft["centre_pct"], "NS", sp(o["centre_pct"]), " pts"),
        ("OFT wall band, rested", oft["thigmo_pct"], "NS", sp(o["thigmo_pct"]), " pts"),
    ])
    print(f"\nMann-Whitney exact: smallest two-sided p at 4 vs 5 = {2 / 126:.4f}, at 5 vs 5 = {2 / 252:.4f}; "
          f"Wilcoxon vs chance: smallest p at n=4 0.125, n=5 0.0625")
    for n in (4, 5):
        print(f"  MDE (two-sample t, power 0.8): n {n} vs 5 -> d {mde_d(n, 5):.2f}")
    for d in (0.8, 1.0, 1.5):
        nn = next(k for k in range(3, 200) if mde_d(k, k) <= d)
        print(f"  n per group to detect d = {d} at power 0.8 (t-test approx): {nn}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()

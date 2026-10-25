#!/usr/bin/env python3
"""Y-maze results, statistics and figures from an EthoVision XT statistics export.

    ymaze_report.py <Statistics-*.xlsx> <out_dir> [--alt "Zone alternation 3"] [--tag HLBNSL]
                    [--trials 10-18] [--hand <hand-scoring note.md>]

--alt names the Zone alternation variable to score (EthoVision numbers the copies;
for HLBNSL "Zone alternation 3" = zone exit threshold 3 cm). Every other Zone
alternation variable in the file is drawn as a threshold-sensitivity panel.
--trials keeps only those EthoVision trials (one per mouse).
--hand takes SA% and arm entries from the hand-scored sequences in a vault note
(a "## HLBN..." heading followed by a ``` block of arm letters), scored by metrics.py;
EthoVision then gives distance and velocity, and its SA% is shown against the hand SA%.

Statistics follow BEHAVIOR_SOP.md section 5: per group, exact Wilcoxon signed-rank
of SA% against 50 %; between groups, exact Mann-Whitney U with the mean difference,
a Welch 95 % CI and Hedges' g; Pearson r between total arm entries and SA%.
Figures follow cohort.py (style, colours, mean ± SEM, dots = mice).

Needs openpyxl, numpy, scipy, matplotlib.
"""
import argparse, csv, os, re, statistics as st, sys

import numpy as np
import openpyxl
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cohort import GCOL, style, stars, plt  # noqa: E402  (lab plotting convention)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import spontaneous_alternation  # noqa: E402

GROUPS = ("water", "SOD1")          # control first: plotted left
CHANCE = 50.0


def read_stats(path):
    """-> list of rows {mouse, group, (variable, subvariable, statistic): value}."""
    rows = [r for r in openpyxl.load_workbook(path, data_only=True).worksheets[0].iter_rows(values_only=True)
            if any(c is not None for c in r)]
    var, sub, stat = rows[0], rows[1], rows[2]
    out = []
    for r in rows[4:]:
        d = {"mouse": r[3], "group": r[2], "trial": int(str(r[1]).split()[-1])}
        for i in range(4, len(r)):
            d[(str(var[i]).strip(), str(sub[i]).strip(), str(stat[i]).strip())] = r[i]
        out.append(d)
    return out


def sa(d, alt):
    """-> (SA%, arm entries). Both None below 3 entries: SA% is undefined there
    (SOP) and Max alternations = 0 cannot tell 0, 1 or 2 entries apart."""
    a = d[(alt, "center-point / Alternations", "Frequency")]
    m = d[(alt, "center-point / Max alternations", "Frequency")]
    return (100.0 * a / m, m + 2) if m else (None, None)


def defined(v):
    return [x for x in v if x is not None]


def read_hand(path):
    """vault note -> {mouse: "ABCAB..."}: each "## HLBN..." heading, then its ``` block."""
    txt = open(path, encoding="utf-8").read()
    return {m: s.upper() for m, s in
            re.findall(r"^#{2,3} (HLBN\w+)[^\n]*\n.*?```\s*\n\s*([abcABC]+)\s*\n```", txt, re.M | re.S)}


def hand_scores(seq):
    """arm letters -> (SA%, entries, alternations, direct revisits, indirect revisits)."""
    alts, n, pct = spontaneous_alternation(list(seq))
    direct = sum(seq[i] == seq[i + 1] for i in range(n - 1))
    indirect = sum(seq[i] == seq[i + 2] != seq[i + 1] for i in range(n - 2))
    return pct, n, alts, direct, indirect


def hedges_g(a, b):
    na, nb = len(a), len(b)
    sp = (((na - 1) * st.variance(a) + (nb - 1) * st.variance(b)) / (na + nb - 2)) ** .5
    return (st.mean(a) - st.mean(b)) / sp * (1 - 3 / (4 * (na + nb) - 9))


def welch_ci(a, b):
    va, vb = st.variance(a) / len(a), st.variance(b) / len(b)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    h = stats.t.ppf(0.975, df) * (va + vb) ** .5
    d = st.mean(a) - st.mean(b)
    return d - h, d + h


def panel(ax, vals, title, lo, hi, chance=None):
    """bar = mean, whisker = SEM, dots = mice, bracket = exact Mann-Whitney U."""
    for i, g in enumerate(GROUPS):
        v = vals[g]
        mu, se = st.mean(v), st.stdev(v) / len(v) ** .5
        ax.bar(i, mu, 0.6, color=GCOL[g], alpha=0.28, lw=0, zorder=1)
        ax.errorbar(i, mu, se, fmt="none", ecolor="0.2", elinewidth=1.4, capsize=4, zorder=4)
        jit = (np.arange(len(v)) - (len(v) - 1) / 2) * 0.07
        ax.plot(i + jit, sorted(v), "o", color=GCOL[g], ms=6.5, mec="white", mew=1.3, zorder=3)
    top = hi if hi is not None else max(max(v) for v in vals.values()) * 1.3
    if chance is not None:
        ax.axhline(chance, color="0.45", ls="--", lw=1, zorder=0)
        ax.text(1.42, chance, "chance", va="bottom", ha="right", fontsize=8, color="0.4")
    p = stats.mannwhitneyu(vals["SOD1"], vals["water"], method="exact").pvalue
    yb = max(max(v) for v in vals.values()) + 0.06 * (top - lo)
    ax.plot([0, 0, 1, 1], [yb - 0.02 * (top - lo), yb, yb, yb - 0.02 * (top - lo)], color="0.25", lw=1)
    ax.text(0.5, yb + 0.01 * (top - lo), f"{stars(p)} (p = {p:.2f})", ha="center", va="bottom",
            fontsize=9, color="0.1")
    ax.set_ylim(lo, top)
    ax.set_xlim(-0.6, 1.6)
    ax.set_xticks([0, 1], [f"{g}\nn = {len(vals[g])}" for g in GROUPS])
    ax.set_title(title, loc="left", fontsize=10.5, color="0.1")
    style(ax)


def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("stats_xlsx")
    pa.add_argument("out_dir")
    pa.add_argument("--alt", default="Zone alternation 3")
    pa.add_argument("--tag", default="HLBNSL")
    pa.add_argument("--trials", help="first-last EthoVision trial to keep, e.g. 10-18")
    pa.add_argument("--hand", help="vault note with the hand-scored arm sequences")
    a = pa.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    data = read_stats(a.stats_xlsx)
    if a.trials:
        lo_t, hi_t = map(int, a.trials.split("-"))
        data = [d for d in data if lo_t <= d["trial"] <= hi_t]
    mice = [d["mouse"] for d in data]
    if len(set(mice)) != len(mice):
        sys.exit("a mouse appears in more than one trial: pick one set with --trials")
    hand = read_hand(a.hand) if a.hand else {}
    if hand and set(hand) != set(mice):
        sys.exit(f"hand sequences {sorted(hand)} do not match the mice {sorted(mice)}")
    if not any((a.alt, "center-point / Alternations", "Frequency") in d for d in data):
        sys.exit(f"{a.alt!r} not in {a.stats_xlsx}")
    alts = sorted({k[0] for k in data[0] if isinstance(k, tuple) and k[0].startswith("Zone alternation")})

    res = []
    for d in data:
        s, n = sa(d, a.alt)
        res.append({"mouse": d["mouse"], "group": d["group"],
                    "sa_pct": None if s is None else round(s, 1), "arm_entries": n,
                    "alternations": d[(a.alt, "center-point / Alternations", "Frequency")],
                    "direct_revisits": d[(a.alt, "center-point / Direct revisits", "Frequency")],
                    "indirect_revisits": d[(a.alt, "center-point / Indirect revisits", "Frequency")],
                    "distance_m": round(d[("Distance moved", "center-point", "Total")] / 100, 2),
                    "velocity_cm_s": round(d[("Velocity", "center-point", "Mean")], 2)})
        if hand:
            r = res[-1]
            r["ev_sa_pct"], r["ev_arm_entries"] = r["sa_pct"], r["arm_entries"]
            s, n, alt_n, dr, ir = hand_scores(hand[d["mouse"]])
            r.update(sa_pct=None if s is None else round(s, 1), arm_entries=n if s is not None else None,
                     alternations=alt_n, direct_revisits=dr, indirect_revisits=ir)
    with open(os.path.join(a.out_dir, f"{a.tag}_ymaze_results.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0]))
        w.writeheader()
        w.writerows(res)

    by = {k: {g: defined(r[k] for r in res if r["group"] == g) for g in GROUPS}
          for k in ("sa_pct", "arm_entries", "distance_m", "velocity_cm_s")}
    src = "hand-scored sequences" if hand else f"EthoVision {a.alt!r}"
    lines = [f"Y-maze {a.tag}, SA% and arm entries from {src}"
             + (f"; EthoVision trials {a.trials}" if a.trials else ""), ""]
    low = [r["mouse"] for r in res if r["sa_pct"] is None]
    if low:
        lines += [f"fewer than 3 arm entries, left out of SA% and entries: {', '.join(low)}", ""]
    for g in GROUPS:
        v = by["sa_pct"][g]
        w = stats.wilcoxon([x - CHANCE for x in v], method="exact")
        lines.append(f"SA% {g}: n={len(v)} mean {st.mean(v):.1f} ± {st.stdev(v) / len(v) ** .5:.1f} SEM, "
                     f"vs 50 %: Wilcoxon W={w.statistic:.0f} p={w.pvalue:.3f} "
                     f"(smallest p possible with n={len(v)}: {2 / 2 ** len(v):.3f})")
    lines.append("")
    for k, lab in (("sa_pct", "SA%"), ("arm_entries", "arm entries"), ("distance_m", "distance (m)"),
                   ("velocity_cm_s", "velocity (cm/s)")):
        s_, w_ = by[k]["SOD1"], by[k]["water"]
        u = stats.mannwhitneyu(s_, w_, method="exact")
        lo, hi = welch_ci(s_, w_)
        lines.append(f"{lab}: SOD1 {st.mean(s_):.2f} vs water {st.mean(w_):.2f}; "
                     f"diff {st.mean(s_) - st.mean(w_):+.2f} (95% CI {lo:+.2f} to {hi:+.2f}), "
                     f"Hedges g {hedges_g(s_, w_):+.2f}, Mann-Whitney U={u.statistic:.0f} p={u.pvalue:.3f}")
    ok = [x for x in res if x["sa_pct"] is not None]
    r = stats.pearsonr([x["arm_entries"] for x in ok], [x["sa_pct"] for x in ok])
    lines += ["", f"control check, entries vs SA% (all mice): Pearson r={r.statistic:+.2f} p={r.pvalue:.3f}"]
    sens = {alt: {g: defined(sa(d, alt)[0] for d in data if d["group"] == g) for g in GROUPS} for alt in alts}
    lines += ["", "threshold sensitivity, mean SA% (SOD1 / water):"]
    lines += [f"  {alt}: {st.mean(v['SOD1']):.1f} / {st.mean(v['water']):.1f}" for alt, v in sens.items()]
    both = [x for x in ok if x["ev_sa_pct"] is not None] if hand else []
    if both:
        lines += ["", f"hand vs EthoVision {a.alt!r} (EthoVision minus hand):"]
        lines += [f"  {x['mouse']}: entries {x['ev_arm_entries'] - x['arm_entries']:+d}, "
                  f"SA {x['ev_sa_pct'] - x['sa_pct']:+.1f} points" for x in both]
        lines.append(f"  mean |SA difference| {st.mean(abs(x['ev_sa_pct'] - x['sa_pct']) for x in both):.1f} points, "
                     f"Pearson r (SA) {stats.pearsonr([x['sa_pct'] for x in both], [x['ev_sa_pct'] for x in both]).statistic:+.2f}")
    txt = "\n".join(lines)
    open(os.path.join(a.out_dir, f"{a.tag}_ymaze_stats.txt"), "w").write(txt + "\n")
    print(txt)

    # figure 1: endpoints
    fig, ax = plt.subplots(1, 4, figsize=(13, 4.2), layout="constrained")
    panel(ax[0], by["sa_pct"], "Spontaneous alternation (%)", 0, 100, chance=CHANCE)
    panel(ax[1], by["arm_entries"], "Total arm entries", 0, None)
    panel(ax[2], by["distance_m"], "Distance moved (m)", 0, None)
    panel(ax[3], by["velocity_cm_s"], "Mean velocity (cm/s)", 0, None)
    fig.suptitle(f"Y-maze, {a.tag} (8 min; mean ± SEM, dots = mice; Mann-Whitney U)",
                 x=0.01, ha="left", fontsize=12, color="0.1")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out_dir, f"{a.tag}_ymaze_fig1_endpoints.{ext}"), dpi=300)
    plt.close(fig)

    # figure 2: control check and threshold sensitivity
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.2), layout="constrained")
    for g in GROUPS:
        xs = [x["arm_entries"] for x in ok if x["group"] == g]
        ys = [x["sa_pct"] for x in ok if x["group"] == g]
        ax[0].plot(xs, ys, "o", color=GCOL[g], ms=7, mec="white", mew=1.3, label=g)
    ax[0].axhline(CHANCE, color="0.45", ls="--", lw=1)
    ax[0].set_ylim(0, 100)
    ax[0].set_xlim(0, max(x["arm_entries"] for x in ok) * 1.2)
    ax[0].set_xlabel("Total arm entries", fontsize=9.5, color="0.2")
    ax[0].set_ylabel("Spontaneous alternation (%)", fontsize=9.5, color="0.2")
    ax[0].set_title(f"Entries vs SA%  (r = {r.statistic:+.2f}, p = {r.pvalue:.2f})", loc="left",
                    fontsize=10.5, color="0.1")
    ax[0].legend(frameon=False, fontsize=9)
    style(ax[0])
    if both:                                          # hand scores are primary: show the agreement
        for g in GROUPS:
            ax[1].plot([x["sa_pct"] for x in both if x["group"] == g],
                       [x["ev_sa_pct"] for x in both if x["group"] == g],
                       "o", color=GCOL[g], ms=7, mec="white", mew=1.3, label=g)
        ax[1].plot([0, 100], [0, 100], color="0.45", ls="--", lw=1)
        ax[1].set_xlim(30, 80)
        ax[1].set_ylim(30, 80)
        ax[1].set_xlabel("Hand-scored SA (%)", fontsize=9.5, color="0.2")
        ax[1].set_ylabel(f"EthoVision SA (%), {a.alt}", fontsize=9.5, color="0.2")
        ax[1].set_title("EthoVision vs hand scoring (dashed = equal)", loc="left", fontsize=10.5, color="0.1")
    else:
        # the un-numbered original variable has no known threshold, so it stays off the curve
        numbered = [alt for alt in alts if re.search(r"\d+$", alt)]
        xs = list(range(len(numbered)))
        for g in GROUPS:
            mu = [st.mean(sens[alt][g]) for alt in numbered]
            se = [st.stdev(sens[alt][g]) / len(sens[alt][g]) ** .5 for alt in numbered]
            ax[1].errorbar(xs, mu, se, color=GCOL[g], lw=2, marker="o", ms=6, mec="white", mew=1.2,
                           capsize=3, label=g)
        ax[1].axhline(CHANCE, color="0.45", ls="--", lw=1)
        ax[1].set_xticks(xs, [re.sub(r"^Zone alternation\s*", "", s) for s in numbered])
        ax[1].set_ylim(0, 100)
        ax[1].set_xlabel("Zone alternation variable (number = exit threshold, cm)", fontsize=9.5, color="0.2")
        ax[1].set_title("SA% vs zone exit threshold", loc="left", fontsize=10.5, color="0.1")
    ax[1].legend(frameon=False, fontsize=9)
    style(ax[1])
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out_dir, f"{a.tag}_ymaze_fig2_checks.{ext}"), dpi=300)
    plt.close(fig)
    print(f"-> {a.out_dir}")


if __name__ == "__main__":
    assert abs(hedges_g([1, 2, 3], [1, 2, 3])) < 1e-12
    k = ("Zone alternation 3", "center-point / {}", "Frequency")
    row = {(k[0], k[1].format(s), k[2]): 0 for s in ("Alternations", "Max alternations")}
    assert sa(row, k[0]) == (None, None)             # a mouse with < 3 entries must not crash
    lo, hi = welch_ci([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0, 5.0])
    assert lo < -0.5 < hi
    # ABCAB: 3 triplets, all alternations; ABA is an indirect revisit, AA a direct one
    assert hand_scores("ABCAB")[:3] == (100.0, 5, 3)
    assert hand_scores("AABAC")[3:] == (1, 1)
    main()

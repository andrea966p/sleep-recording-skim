#!/usr/bin/env python3
"""NOR day 1 (open field) results, statistics and figures from oft_features.py output.

    oft_report.py <features_model2.csv> <out_dir> [--check features_model1.csv] [--tag HLBNSL]

Group comes from the mouse ID: HLBNS... = SOD1, HLBNW... = water.
Statistics follow BEHAVIOR_SOP.md section 5 (between groups: exact Mann-Whitney U,
mean difference with a Welch 95 % CI, Hedges' g); figures and helpers are the
Y-maze report's (ymaze_report.panel), so both tests look alike.
--check: a second model's features; per-mouse agreement goes in the stats text.
"""
import argparse, csv, os, statistics as st, sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ymaze_report import GROUPS, GCOL, hedges_g, panel, plt, style, welch_ci  # noqa: E402

ENDPOINTS = [  # (column, label, axis floor, axis top or None)
    ("distance_m", "Distance moved (m)", 0, None),
    ("mean_speed_cm_s", "Mean speed (cm/s)", 0, None),
    ("immobile_s", "Immobility (s)", 0, None),
    ("centre_time_pct", "Centre time (%)", 0, 100),
    ("centre_entries", "Centre entries", 0, None),
    ("thigmotaxis_pct", "Thigmotaxis, < 5 cm from wall (%)", 0, 100),
    ("habituation_ratio_last3_first3", "Distance, last 3 / first 3 min", 0, None),
    ("object_spot_bias", "Object-spot bias (0.5-1)", 0, 1),
]


def group(mouse):
    return "SOD1" if mouse.startswith("HLBNS") else "water" if mouse.startswith("HLBNW") else None


def load(path):
    rows = list(csv.DictReader(open(path, newline="")))
    for r in rows:
        r["group"] = group(r["mouse"])
        r["distance_m"] = float(r["distance_cm"]) / 100
    return {r["mouse"]: r for r in rows}


def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("features")
    pa.add_argument("out_dir")
    pa.add_argument("--check", help="second model's features CSV")
    pa.add_argument("--tag", default="HLBNSL")
    a = pa.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    d = load(a.features)
    assert all(r["group"] for r in d.values()), "a mouse ID is neither HLBNS nor HLBNW"
    val = lambda k, g: [float(r[k]) for r in d.values() if r["group"] == g and r[k] not in ("", "nan")]

    lines = [f"NOR day 1 open field, {a.tag}, {d[next(iter(d))]['model']} (n = "
             + ", ".join(f"{len(val('distance_m', g))} {g}" for g in GROUPS) + ")", ""]
    lines.append("tracking QC (min over mice): on floor {:.2f} %, body tracked {:.2f} %; "
                 "top detection rejected (off floor) max {:.2f} %".format(
                     min(float(r["mouse_on_floor_pct"]) for r in d.values()),
                     min(float(r["body_tracked_pct"]) for r in d.values()),
                     max(float(r["top_detection_rejected_pct"]) for r in d.values())))
    lines.append("")
    for k, lab, *_ in ENDPOINTS + [("wall_rear_proxy_n", "wall-rear proxy (unvalidated)", 0, None)]:
        s_, w_ = val(k, "SOD1"), val(k, "water")
        u = stats.mannwhitneyu(s_, w_, method="exact")
        lo, hi = welch_ci(s_, w_)
        lines.append(f"{lab}: SOD1 {st.mean(s_):.2f} ± {st.stdev(s_) / len(s_) ** .5:.2f} vs water "
                     f"{st.mean(w_):.2f} ± {st.stdev(w_) / len(w_) ** .5:.2f} (mean ± SEM); diff "
                     f"{st.mean(s_) - st.mean(w_):+.2f} (95% CI {lo:+.2f} to {hi:+.2f}), Hedges g "
                     f"{hedges_g(s_, w_):+.2f}, Mann-Whitney U={u.statistic:.0f} p={u.pvalue:.3f}")
    # habituation within the session, per group: Spearman of distance against minute, pooled over mice
    mins = [f"dist_min{i:02d}_cm" for i in range(1, 11)]
    lines.append("")
    for g in GROUPS:
        m = np.array([[float(r[c]) / 100 for c in mins] for r in d.values() if r["group"] == g])
        slopes = [np.polyfit(range(1, 11), row, 1)[0] for row in m]
        w = stats.wilcoxon(slopes, method="exact")
        lines.append(f"habituation {g}: distance min 1 {m[:, 0].mean():.2f} m -> min 10 {m[:, -1].mean():.2f} m; "
                     f"per-mouse slope {st.mean(slopes):+.3f} m/min, {sum(s < 0 for s in slopes)}/{len(slopes)} "
                     f"negative, Wilcoxon vs 0 p={w.pvalue:.3f}")
    if a.check:
        c = load(a.check)
        both = sorted(set(d) & set(c))
        lines += ["", f"model agreement ({c[both[0]]['model']} minus {d[both[0]]['model']}, {len(both)} mice):"]
        for k in ("distance_m", "centre_time_pct", "thigmotaxis_pct", "immobile_s"):
            x = [float(d[m][k]) for m in both]
            y = [float(c[m][k]) for m in both]
            r = stats.pearsonr(x, y).statistic if len(both) > 2 else float("nan")
            lines.append(f"  {k}: mean diff {st.mean(np.subtract(y, x)):+.2f}, "
                         f"max |diff| {max(abs(np.subtract(y, x))):.2f}, Pearson r {r:+.3f}")
    txt = "\n".join(lines)
    open(os.path.join(a.out_dir, f"{a.tag}_oft_stats.txt"), "w", encoding="utf-8").write(txt + "\n")
    with open(os.path.join(a.out_dir, f"{a.tag}_oft_results.csv"), "w", newline="") as fh:
        cols = ["mouse", "group"] + [k for k, *_ in ENDPOINTS] + ["wall_rear_proxy_n"]
        w = csv.writer(fh)
        w.writerow(cols)
        for r in sorted(d.values(), key=lambda r: (r["group"] != "SOD1", r["mouse"])):
            w.writerow([r["mouse"], r["group"]] + [round(float(r[k]), 3) for k in cols[2:]])
    print(txt)

    # figure 1: endpoints
    fig, ax = plt.subplots(2, 4, figsize=(14, 8), layout="constrained")
    for axx, (k, lab, lo, hi) in zip(ax.flat, ENDPOINTS):
        panel(axx, {g: val(k, g) for g in GROUPS}, lab, lo, hi, chance=0.5 if k == "object_spot_bias" else None)
    fig.suptitle(f"Open field, NOR day 1, {a.tag} (10 min; mean ± SEM, dots = mice; Mann-Whitney U)",
                 x=0.01, ha="left", fontsize=12, color="0.1")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out_dir, f"{a.tag}_oft_fig1_endpoints.{ext}"), dpi=300)
    plt.close(fig)

    # figure 2: habituation curve and quadrant occupancy
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), layout="constrained")
    for g in GROUPS:
        m = np.array([[float(r[c]) / 100 for c in mins] for r in d.values() if r["group"] == g])
        ax[0].errorbar(range(1, 11), m.mean(0), m.std(0, ddof=1) / len(m) ** .5, color=GCOL[g], lw=2,
                       marker="o", ms=5, mec="white", mew=1.2, capsize=3, label=f"{g} (n = {len(m)})")
    ax[0].set_ylim(0, None)
    ax[0].set_xticks(range(1, 11))
    ax[0].set_xlabel("Minute", fontsize=9.5, color="0.2")
    ax[0].set_ylabel("Distance (m)", fontsize=9.5, color="0.2")
    ax[0].set_title("Within-session habituation", loc="left", fontsize=10.5, color="0.1")
    ax[0].legend(frameon=False, fontsize=9)
    style(ax[0])
    qs = ["q_UL_pct", "q_UR_pct", "q_LL_pct", "q_LR_pct"]
    for i, g in enumerate(GROUPS):
        m = np.array([[float(r[q]) for q in qs] for r in d.values() if r["group"] == g])
        ax[1].bar(np.arange(4) + (i - 0.5) * 0.38, m.mean(0), 0.38, yerr=m.std(0, ddof=1) / len(m) ** .5,
                  color=GCOL[g], alpha=0.6, capsize=3, label=g)
    ax[1].axhline(25, color="0.45", ls="--", lw=1)
    ax[1].set_xticks(range(4), ["upper left\n(object)", "upper right", "lower left", "lower right\n(object)"])
    ax[1].set_ylim(0, 50)
    ax[1].set_ylabel("Time in quadrant (%)", fontsize=9.5, color="0.2")
    ax[1].set_title("Quadrant occupancy (dashed = even)", loc="left", fontsize=10.5, color="0.1")
    ax[1].legend(frameon=False, fontsize=9)
    style(ax[1])
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out_dir, f"{a.tag}_oft_fig2_habituation.{ext}"), dpi=300)
    plt.close(fig)
    print(f"-> {a.out_dir}")


if __name__ == "__main__":
    assert group("HLBNSSL41") == "SOD1" and group("HLBNWSL50") == "water" and group("X") is None
    main()

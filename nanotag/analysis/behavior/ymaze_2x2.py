#!/usr/bin/env python3
"""Y-maze, normal sleep (HLBNSL) next to sleep deprivation (NS-SD): the SOD1 x sleep layout.

    ymaze_2x2.py <rested> <deprived> <out_dir> [--run2 out/HLBNSSD/run2/sd_and_recovery_per_mouse.csv]

<rested> and <deprived> are either a ymaze_report.py results CSV or a vault results note whose
per-mouse table has the columns Mouse | Group | SA % | Arm entries | ... | Distance (m) | Velocity (cm/s)
(as in 2026-10-25-HLBNSL-ymaze-hand-scored-results). The two arms are different batches (mice,
treatment length, date), so the SD contrast is "consistent with", never "caused by" (2026-10-30 decision).

Statistics, estimation first (draft section 8): per cell mean ± SEM and SA% vs 50 % (exact Wilcoxon);
SOD1 - water within each sleep condition and deprived - rested within each treatment, as a difference with
the exact permutation 95 % CI and p (cohort.perm_ci, the nanotag method); the SOD1 x sleep interaction
(difference of the two SOD1 effects) by shuffling the four cell labels, 20000 times, as in the tissue
analysis. With --run2, each deprived mouse's Y-maze is also drawn against its tag sleep from Run 2.
"""
import argparse, csv, os, re, statistics as st, sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from cohort import GCOL, style, stars, plt, perm_p, perm_ci  # noqa: E402

GROUPS = ("water", "SOD1")
SLEEP = ("rested", "deprived")
KEYS = (("sa_pct", "Spontaneous alternation (%)", 100), ("arm_entries", "Total arm entries", None),
        ("distance_m", "Distance moved (m)", None), ("velocity_cm_s", "Mean velocity (cm/s)", None))


def read(path):
    """-> [{mouse, group, sa_pct, arm_entries, distance_m, velocity_cm_s}]"""
    if path.endswith(".csv"):
        with open(path, newline="") as fh:
            rows = list(csv.DictReader(fh))
    else:                                            # vault note: the first table whose header names Mouse
        lines = [x.strip() for x in open(path, encoding="utf-8")]
        i = next(i for i, x in enumerate(lines) if re.match(r"\|\s*Mouse\s*\|", x))
        head = [c.strip() for c in lines[i].strip("|").split("|")]
        col = {"Mouse": "mouse", "Group": "group", "SA %": "sa_pct", "Arm entries": "arm_entries",
               "Distance (m)": "distance_m", "Velocity (cm/s)": "velocity_cm_s"}
        rows = []
        for x in lines[i + 2:]:
            if not x.startswith("|"):
                break
            cells = [c.strip() for c in x.strip("|").split("|")]
            rows.append({col[h]: c for h, c in zip(head, cells) if h in col})
    out = []
    for r in rows:
        if r["sa_pct"] in ("", None):               # < 3 entries: SA% undefined (SOP), left out
            continue
        out.append(dict(mouse=r["mouse"], group=r["group"],
                        **{k: float(r[k]) for k, _, _ in KEYS}))
    assert out and {r["group"] for r in out} == set(GROUPS), f"{path}: need both groups"
    return out


def cell(rows, k, g):
    return [r[k] for r in rows if r["group"] == g]


def interaction_p(data, k, n=20000):
    """(SOD1 - water | deprived) - (SOD1 - water | rested), label shuffle across the 4 cells"""
    y = np.array([r[k] for s in SLEEP for r in data[s]])
    lab = np.array([f"{s}/{r['group']}" for s in SLEEP for r in data[s]])

    def est(lb):
        m = {c: y[lb == c].mean() for c in set(lb)}
        return (m["deprived/SOD1"] - m["deprived/water"]) - (m["rested/SOD1"] - m["rested/water"])
    obs = est(lab)
    rng = np.random.default_rng(0)
    null = np.array([est(rng.permutation(lab)) for _ in range(n)])
    return obs, ((np.abs(null) >= abs(obs) - 1e-12).sum() + 1) / (n + 1)


def fmt(v):
    return f"{st.mean(v):.1f} ± {st.stdev(v) / len(v) ** .5:.1f} (n = {len(v)})"


def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("rested")
    pa.add_argument("deprived")
    pa.add_argument("out_dir")
    pa.add_argument("--run2", help="cohort_sd.py --run2 sd_and_recovery_per_mouse.csv, for the per-mouse sleep panels")
    a = pa.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    data = {"rested": read(a.rested), "deprived": read(a.deprived)}

    lines = ["Y-maze, rested (HLBNSL) and after SD (NS-SD); different batches. Mean ± SEM;",
             "differences with exact permutation 95 % CI and p; interaction by label shuffle (20000).", ""]
    for k, lab, _ in KEYS:
        lines.append(lab)
        for s in SLEEP:
            for g in GROUPS:
                v = cell(data[s], k, g)
                extra = ""
                if k == "sa_pct":
                    w = stats.wilcoxon([x - 50 for x in v], method="exact")
                    extra = f", vs 50 %: Wilcoxon p = {w.pvalue:.3f}"
                lines.append(f"  {s:8s} {g:5s} {fmt(v)}{extra}")
        for s in SLEEP:
            d, lo, hi = perm_ci(cell(data[s], k, "SOD1"), cell(data[s], k, "water"))
            lines.append(f"  SOD1 - water, {s:8s}: {d:+.2f} ({lo:+.2f} to {hi:+.2f}), "
                         f"p = {perm_p(cell(data[s], k, 'SOD1'), cell(data[s], k, 'water')):.3f}")
        for g in GROUPS:
            d, lo, hi = perm_ci(cell(data["deprived"], k, g), cell(data["rested"], k, g))
            lines.append(f"  deprived - rested, {g:5s}: {d:+.2f} ({lo:+.2f} to {hi:+.2f}), "
                         f"p = {perm_p(cell(data['deprived'], k, g), cell(data['rested'], k, g)):.3f}")
        ie, ip = interaction_p(data, k)
        lines += [f"  SOD1 x sleep interaction: {ie:+.2f}, p = {ip:.3f}", ""]
    txt = "\n".join(lines)
    open(os.path.join(a.out_dir, "ymaze_2x2_stats.txt"), "w").write(txt + "\n")
    print(txt)

    fig, axes = plt.subplots(1, 4, figsize=(15, 4.4), layout="constrained")
    dx, bw = 0.21, 0.34
    for ax, (k, lab, hi) in zip(axes, KEYS):
        top = hi or max(r[k] for s in SLEEP for r in data[s]) * 1.35
        for si, s in enumerate(SLEEP):
            for g in GROUPS:
                v = cell(data[s], k, g)
                x = si + (-dx if g == "water" else dx)
                mu, se = st.mean(v), st.stdev(v) / len(v) ** .5
                ax.bar(x, mu, bw, color=GCOL[g], alpha=0.28, lw=0, zorder=1)
                ax.errorbar(x, mu, se, fmt="none", ecolor="0.2", elinewidth=1.4, capsize=4, zorder=4)
                jit = (np.arange(len(v)) - (len(v) - 1) / 2) * 0.05
                ax.plot(x + jit, sorted(v), "o", color=GCOL[g], ms=6.5, mec="white", mew=1.3, zorder=3)
            p = perm_p(cell(data[s], k, "SOD1"), cell(data[s], k, "water"))
            yb = max(r[k] for r in data[s]) + 0.05 * top
            ax.plot([si - dx, si - dx, si + dx, si + dx], [yb - 0.02 * top, yb, yb, yb - 0.02 * top],
                    color="0.25", lw=1)
            ax.text(si, yb + 0.01 * top, f"{stars(p)} (p = {p:.2f})", ha="center", va="bottom", fontsize=8.5)
        if k == "sa_pct":
            ax.axhline(50, color="0.45", ls="--", lw=1, zorder=0)
        ax.set_ylim(0, top)
        ax.set_xlim(-0.6, 1.6)
        ax.set_xticks([0, 1], ["Normal sleep\n(HLBNSL)", "After 2 days SD\n(NS-SD)"])
        ax.set_title(lab, loc="left", fontsize=10.5, color="0.1")
        style(ax)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=GCOL[g], alpha=0.5, label=g) for g in GROUPS], loc="outside lower center",
               ncol=2, frameon=False, fontsize=9.5)
    fig.suptitle("Y-maze with normal sleep and after SD, SOD1 vs water (mean ± SEM, dots = mice; brackets: exact "
                 "permutation test within batch; the two batches are different mice)", x=0.01, ha="left",
                 fontsize=11.5, color="0.1")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out_dir, f"ymaze_2x2_fig1.{ext}"), dpi=300)
    plt.close(fig)

    if a.run2:                                       # per deprived mouse: tag sleep vs Y-maze
        with open(a.run2, newline="") as fh:
            tag = {int(r["mouse"]): r for r in csv.DictReader(fh)}
        dep = data["deprived"]
        num = lambda r: int(re.search(r"\d+$", r["mouse"]).group())
        assert all(num(r) in tag for r in dep), "a Y-maze mouse is missing from sd_and_recovery_per_mouse.csv"
        xs = (("rebound_total_min", "Recovery rebound 11-03 → 11-04 (min)"),
              ("sd2_pct", "Sleep during SD day 2, 09-15 (%)"),
              ("wait_pct", "Sleep from 15:00 to the Y-maze (%)"))
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), layout="constrained")
        out = ["", "per deprived mouse, tag sleep vs SA% (Pearson, all mice):"]
        for ax, (kx, lab) in zip(axes, xs):
            pts = [(float(tag[num(r)][kx]), r["sa_pct"], r) for r in dep if tag[num(r)][kx] not in ("", "nan")]
            for g in GROUPS:
                ax.plot([x for x, _, r in pts if r["group"] == g], [y for _, y, r in pts if r["group"] == g], "o",
                        color=GCOL[g], ms=7, mec="white", mew=1.3, label=g)
            for x, y, r in pts:
                ax.annotate(str(num(r)), (x, y), xytext=(4, 3), textcoords="offset points", fontsize=7.5,
                            color="0.35")
            ax.axhline(50, color="0.45", ls="--", lw=1)
            ax.set_ylim(0, 100)
            ax.set_xlabel(lab, fontsize=9.5, color="0.2")
            ax.set_ylabel("Spontaneous alternation (%)", fontsize=9.5, color="0.2")
            if len(pts) > 2:
                rr = stats.pearsonr([x for x, _, _ in pts], [y for _, y, _ in pts])
                ax.set_title(f"r = {rr.statistic:+.2f}, p = {rr.pvalue:.2f}", loc="left", fontsize=10.5)
                out.append(f"  {kx}: r = {rr.statistic:+.2f}, p = {rr.pvalue:.3f}, n = {len(pts)}")
            style(ax)
        axes[0].legend(frameon=False, fontsize=9)
        fig.suptitle("NS-SD: each mouse's tag sleep against its Y-maze alternation (numbers = mouse)", x=0.01,
                     ha="left", fontsize=12, color="0.1")
        for ext in ("png", "pdf"):
            fig.savefig(os.path.join(a.out_dir, f"ymaze_2x2_fig2_tag_sleep.{ext}"), dpi=300)
        plt.close(fig)
        open(os.path.join(a.out_dir, "ymaze_2x2_stats.txt"), "a").write("\n".join(out) + "\n")
        print("\n".join(out))
    print(f"-> {a.out_dir}")


if __name__ == "__main__":
    obs, p = interaction_p({"rested": [dict(group=g, v=x) for g in GROUPS for x in (1.0, 2.0, 3.0)],
                            "deprived": [dict(group=g, v=x) for g in GROUPS for x in (1.0, 2.0, 3.0)]}, "v", 200)
    assert obs == 0 and p == 1.0                     # identical cells: no interaction
    main()

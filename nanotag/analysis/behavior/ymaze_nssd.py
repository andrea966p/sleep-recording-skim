#!/usr/bin/env python3
"""NS-SD / NW-SD Y-maze (11-04, after 2 days of SD), hand-scored, shown next to HLBNSL (rested, 09-30).

    ymaze_nssd.py [--sheet NSSD_ymaze_hand_scoring.csv] [--hlbnsl <HLBNSL hand-scoring note>] <out_dir> [--vault]

SA% and arm entries from the arm-letter sequences in the sheet (same rules and
scoring as HLBNSL: all four paws, re-entries kept, metrics.py via ymaze_report),
real SD length = 09:00 to the mouse's Y-maze start. Different cohorts: each is
tested SOD1 vs water on its own (BEHAVIOR_SOP section 5), never pooled.
Needs numpy, scipy, matplotlib, openpyxl (ymaze_report imports it).
"""
import argparse, csv, os, shutil, statistics as st, sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scipy import stats
from ymaze_report import (GROUPS, CHANCE, GCOL, style, plt, read_hand, hand_scores, hedges_g,
                          welch_ci, panel)

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "NSSD_ymaze_hand_scoring.csv")
HLBNSL = os.path.join(HERE, "..", "..", "..", "vault", "10-projects", "hlb-sod1",
                      "2026-10-25-HLBNSL-ymaze-hand-scoring.md")
VAULT = os.path.join(HERE, "..", "..", "..", "vault", "_attachments", "2026-11-04-NSSD-run2-ymaze.png")
SD_START = "09:00"


def sd_hours(t):
    """09:00 -> Y-maze start, in hours; None when the start is not logged"""
    f = lambda x: datetime.strptime(x, "%H:%M")
    return round((f(t) - f(SD_START)).total_seconds() / 3600, 2) if t else None


def score(seqs):
    """{mouse: (group, sequence, ymaze_start)} -> result rows"""
    rows = []
    for m, (g, seq, t) in seqs.items():
        s, n, alts, dr, ir = hand_scores(seq)
        rows.append(dict(mouse=m, group=g, sa_pct=None if s is None else round(s, 1), arm_entries=n,
                         alternations=alts, direct_revisits=dr, indirect_revisits=ir,
                         ymaze_start=t, sd_h=sd_hours(t)))
    return rows


def read_sheet(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if not r["sequence"].strip():
            print(f"  {r['mouse']}: no sequence yet, left out")
    return {r["mouse"]: (r["group"], r["sequence"].strip().upper(), r["ymaze_start"].strip())
            for r in rows if r["sequence"].strip()}


def lines_for(tag, res):
    out = [f"{tag}:"]
    for g in GROUPS:
        v = [r["sa_pct"] for r in res if r["group"] == g and r["sa_pct"] is not None]
        w = stats.wilcoxon([x - CHANCE for x in v], method="exact")
        out.append(f"  SA% {g}: n={len(v)} mean {st.mean(v):.1f} ± {st.stdev(v) / len(v) ** .5:.1f} SEM, "
                   f"vs 50 %: Wilcoxon p={w.pvalue:.3f}")
    for k, lab in (("sa_pct", "SA%"), ("arm_entries", "arm entries")):
        a = [r[k] for r in res if r["group"] == "SOD1" and r[k] is not None]
        b = [r[k] for r in res if r["group"] == "water" and r[k] is not None]
        lo, hi = welch_ci(a, b)
        u = stats.mannwhitneyu(a, b, method="exact")
        out.append(f"  {lab}: SOD1 {st.mean(a):.1f} vs water {st.mean(b):.1f}; diff {st.mean(a) - st.mean(b):+.1f} "
                   f"(95% CI {lo:+.1f} to {hi:+.1f}), Hedges g {hedges_g(a, b):+.2f}, Mann-Whitney p={u.pvalue:.3f}")
    return out


def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("out_dir")
    pa.add_argument("--sheet", default=SHEET)
    pa.add_argument("--hlbnsl", default=HLBNSL)
    pa.add_argument("--vault", action="store_true", help="copy the figure to vault/_attachments")
    a = pa.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    sd = score(read_sheet(a.sheet))
    rested = score({m: ("SOD1" if m.startswith("HLBNSSL") else "water", s, "")
                    for m, s in read_hand(a.hlbnsl).items()})
    if min(sum(r["group"] == g for r in sd) for g in GROUPS) < 2:
        sys.exit("fewer than 2 scored NS-SD mice in a group: fill in the sheet first")
    with open(os.path.join(a.out_dir, "NSSD_ymaze_results.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sd[0]))
        w.writeheader()
        w.writerows(sd)
    txt = ["Y-maze, hand-scored SA% and arm entries; cohorts tested separately, not pooled", ""]
    txt += lines_for("NS-SD / NW-SD (2 days SD, 11-04)", sd) + [""]
    txt += lines_for("HLBNSL (rested, 09-30; from the hand-scoring note)", rested)
    timed = [r for r in sd if r["sd_h"] is not None and r["sa_pct"] is not None]
    if len(timed) >= 3:
        r = stats.pearsonr([x["sd_h"] for x in timed], [x["sa_pct"] for x in timed])
        txt += ["", f"NS-SD: real SD length (09:00 -> Y-maze start) vs SA%, n={len(timed)}: "
                    f"Pearson r={r.statistic:+.2f} p={r.pvalue:.3f}"]
    txt = "\n".join(txt)
    open(os.path.join(a.out_dir, "NSSD_ymaze_stats.txt"), "w").write(txt + "\n")
    print(txt)

    vals = lambda res, k: {g: [r[k] for r in res if r["group"] == g and r[k] is not None] for g in GROUPS}
    top = max(r["arm_entries"] for r in sd + rested) * 1.3
    fig, ax = plt.subplots(1, 5, figsize=(19, 4.4), layout="constrained")
    panel(ax[0], vals(rested, "sa_pct"), "SA %, HLBNSL (rested)", 0, 100, chance=CHANCE)
    panel(ax[1], vals(sd, "sa_pct"), "SA %, NS-SD (2 days SD)", 0, 100, chance=CHANCE)
    panel(ax[2], vals(rested, "arm_entries"), "Arm entries, HLBNSL", 0, top)
    panel(ax[3], vals(sd, "arm_entries"), "Arm entries, NS-SD", 0, top)
    for g in GROUPS:
        ax[4].plot([r["sd_h"] for r in timed if r["group"] == g], [r["sa_pct"] for r in timed if r["group"] == g],
                   "o", color=GCOL[g], ms=7, mec="white", mew=1.3, label=g)
    ax[4].axhline(CHANCE, color="0.45", ls="--", lw=1)
    ax[4].set_ylim(0, 100)
    ax[4].set_xlabel("real SD length, 09:00 → Y-maze start (h)", fontsize=9.5, color="0.2")
    ax[4].set_title("NS-SD: SA % vs SD length", loc="left", fontsize=10.5, color="0.1")
    ax[4].legend(frameon=False, fontsize=9)
    style(ax[4])
    fig.suptitle("Y-maze, hand-scored (8 min; mean ± SEM, dots = mice; Mann-Whitney U within each cohort; "
                 "different mice, ages and SOD1 days: side by side, not pooled)",
                 x=0.01, ha="left", fontsize=11.5, color="0.1")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(a.out_dir, f"NSSD_ymaze_fig.{ext}"), dpi=300)
    plt.close(fig)
    if a.vault:
        shutil.copy(os.path.join(a.out_dir, "NSSD_ymaze_fig.png"), VAULT)
        print(f"  copied {os.path.normpath(VAULT)}")
    print(f"-> {a.out_dir}")


if __name__ == "__main__":
    assert sd_hours("15:30") == 6.5 and sd_hours("") is None
    assert score({"X": ("SOD1", "ABCAB", "15:00")})[0]["sa_pct"] == 100.0
    main()

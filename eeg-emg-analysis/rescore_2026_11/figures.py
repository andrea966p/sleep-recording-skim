"""Cohort figures of the 2026-11 HLB EEG re-score, from the backbone only. Usage: figures.py BACKBONE OUTDIR

fig1 tiers: every mouse-window, old verdict vs new tier
fig2 sleep by ZT hour, baseline, SOD1 vs water (tier A/B, each mouse thin, arm mean thick)
fig3 recovery minus baseline sleep by ZT hour (ZT4-24), per arm
fig4 NREM delta by ZT hour, % of the mouse's baseline 24-h NREM mean, baseline vs recovery, per arm
     (mice whose baseline is tier A/B only)
fig5 EEG spectra per state (baseline, 24 h), each normalised to the mouse's NREM 1-30 Hz total
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ARMS = [("HLBWSD", "W-SD"), ("HLBSSD", "S-SD"), ("HLBWSL", "W-SL"), ("HLBSSL", "S-SL")]
LIQ = {"water": "#4477aa", "SOD1": "#cc6677"}
TIER_C = {"A": "#228833", "B": "#66ccee", "C": "#ccbb44", "D": "#ee7733", "X": "#bbbbbb"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def main(B: Path, O: Path):
    O.mkdir(parents=True, exist_ok=True)
    rec = pd.read_csv(B / "recordings.csv")
    h = pd.read_csv(B / "hourly.csv")
    ok = rec[rec.tier.isin(["A", "B"])][["mouse", "tp"]]
    h = h.merge(ok).query("usable_min >= 30").copy()
    h["sleep"] = 100 * (h.NR_min + h.R_min) / h.usable_min
    pre = "2026-11-03-hlb-eeg"

    # fig1: tier map
    fig, ax = plt.subplots(1, 4, figsize=(11, 3.4))
    for a, (b, name) in zip(ax, ARMS):
        r = rec[rec.batch == b]
        mice = sorted(r.mouse.unique())
        for i, m in enumerate(mice):
            for j, tp in enumerate(("B", "R")):
                q = r[(r.mouse == m) & (r.tp == tp)]
                if q.empty:
                    a.text(j, i, "—", ha="center", va="center"); continue
                q = q.iloc[0]
                a.add_patch(plt.Rectangle((j - 0.45, i - 0.4), 0.9, 0.8, color=TIER_C[q.tier]))
                old = {"SCOREABLE": "old ✓", "NOT SCOREABLE": "old ✗", "NO VERDICT": "old ?"}.get(q.old_qc, "old –")
                a.text(j, i, f"{q.tier}  {old}", ha="center", va="center", fontsize=7.5)
        a.set_xlim(-0.6, 1.6); a.set_ylim(len(mice) - 0.5, -0.5)
        a.set_xticks([0, 1], ["baseline", "recovery"]); a.set_yticks(range(len(mice)), mice); a.set_title(name)
        for s in a.spines.values():
            s.set_visible(False)
    fig.suptitle("Re-score tiers (A/B: W/NR/R; C: EEG-alone NREM; D: EMG-alone sleep; X: none) vs the old verdict", fontsize=9)
    fig.tight_layout(); fig.savefig(O / f"{pre}-fig1-tiers.png", dpi=110); plt.close(fig)

    # fig2: baseline sleep by ZT hour, SOD1 vs water
    fig, ax = plt.subplots(figsize=(7, 3.4))
    hb = h[h.tp == "B"]
    for liq, g in hb.groupby("liquid"):
        for _, gm in g.groupby("mouse"):
            ax.plot(gm.zt_hour + 0.5, gm.sleep, color=LIQ[liq], lw=0.5, alpha=0.4)
        mean = g.groupby("zt_hour").sleep.mean()
        ax.plot(mean.index + 0.5, mean.values, color=LIQ[liq], lw=2.2, label=f"{liq} (n={g.mouse.nunique()})")
    ax.axvspan(12, 24, color="0.9", zorder=0); ax.set_xlim(0, 24); ax.set_ylim(0, 100)
    ax.set_xlabel("ZT (h); dark from ZT12"); ax.set_ylabel("sleep, % of usable time"); ax.legend(frameon=False)
    ax.set_title("Baseline (on treatment, before deprivation): sleep by hour, tier A/B mice")
    fig.tight_layout(); fig.savefig(O / f"{pre}-fig2-baseline-sleep-by-hour.png", dpi=110); plt.close(fig)

    # fig3: recovery - baseline by ZT hour, per arm, paired mice
    fig, ax = plt.subplots(1, 4, figsize=(12, 3.2), sharey=True)
    for a, (b, name) in zip(ax, ARMS):
        g = h[h.batch == b].pivot_table(index=["mouse", "zt_hour"], columns="tp", values="sleep").reindex(columns=["B", "R"]).dropna()
        g = g[g.index.get_level_values("zt_hour") >= 4]
        if len(g):
            d = (g.R - g.B).rename("d").reset_index()
            for _, gm in d.groupby("mouse"):
                a.plot(gm.zt_hour + 0.5, gm.d, lw=0.8, alpha=0.6, label=gm.mouse.iloc[0])
            a.legend(frameon=False, fontsize=7)
        a.axhline(0, color="k", lw=0.5); a.axvspan(12, 24, color="0.9", zorder=0); a.set_xlim(4, 24)
        a.set_title(f"{name} (paired n={g.index.get_level_values('mouse').nunique() if len(g) else 0})"); a.set_xlabel("ZT (h)")
    ax[0].set_ylabel("sleep, recovery − baseline (pts)")
    fig.tight_layout(); fig.savefig(O / f"{pre}-fig3-recovery-minus-baseline.png", dpi=110); plt.close(fig)

    # fig4: NREM delta time course
    sw = pd.read_csv(B / "nrem_delta_hourly.csv").merge(ok).query("n_nrem_epochs >= 30")
    sw = sw[sw.mouse.isin(ok[ok.tp == "B"].mouse)]                     # the reference baseline must be A/B too
    fig, ax = plt.subplots(1, 4, figsize=(12, 3.2), sharey=True)
    for a, (b, name) in zip(ax, ARMS):
        g = sw[sw.batch == b]
        for k, (m, gm) in enumerate(g.groupby("mouse")):
            for tp, ls in (("B", ":"), ("R", "-")):
                q = gm[gm.tp == tp]
                a.plot(q.zt_hour + 0.5, q.nrem_delta_pct_baseline, ls=ls, lw=1, color=f"C{k}", label=m if tp == "B" else None)
        a.axhline(100, color="k", lw=0.5); a.axvspan(12, 24, color="0.9", zorder=0); a.set_xlim(0, 24)
        a.set_title(name); a.set_xlabel("ZT (h)"); a.legend(frameon=False, fontsize=6.5)
    ax[0].set_ylabel("NREM δ, % of own baseline mean")
    fig.suptitle("NREM δ by hour: dotted = baseline, solid = recovery (tier A/B windows)", fontsize=9)
    fig.tight_layout(); fig.savefig(O / f"{pre}-fig4-nrem-delta-time-course.png", dpi=110); plt.close(fig)

    # fig5: spectra per state, baseline 24 h
    sp = pd.read_csv(B / "spectra.csv").merge(ok)
    sp = sp[(sp.tp == "B") & (sp.phase == "24h")]
    ref = sp[(sp.stage == "NR") & (sp.hz <= 30)].groupby("mouse").power_uv2.sum()
    sp = sp.assign(rel=sp.power_uv2 / sp.mouse.map(ref))
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
    for a, stg in zip(ax, ("W", "NR", "R")):
        for liq, g in sp[sp.stage == stg].groupby("liquid"):
            m = g.groupby("hz").rel.mean()
            for _, gm in g.groupby("mouse"):
                a.plot(gm.hz, gm.rel, color=LIQ[liq], lw=0.4, alpha=0.4)
            a.plot(m.index, m.values, color=LIQ[liq], lw=2, label=f"{liq} (n={g.mouse.nunique()})")
        a.set_yscale("log"); a.set_xlim(1, 30); a.set_title(f"{stg}, baseline 24 h"); a.set_xlabel("Hz")
    ax[0].set_ylabel("power / own NREM 1–30 Hz total"); ax[0].legend(frameon=False)
    fig.tight_layout(); fig.savefig(O / f"{pre}-fig5-state-spectra.png", dpi=110); plt.close(fig)
    print("figures ->", O)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))

"""EEG section of the 2026-11-05 lab meeting deck v2 (HLB SOD1 study): figures + every number they show.

Reads only the small results of the 2026-11 re-score (no NAS, no backbone):
  eeg-emg-analysis/rescore_2026_11/results/{recordings.csv, per_mouse_segments.csv, final_tiers.json,
  nrem_delta_zt4_8_pct_baseline.csv, handscore_check_hlbssl33_r_to19028.txt, review_result.json}
  vault/_attachments/2026-11-03-hlb-eeg-<mouse>-<b|r>-overview.png  (cropped for the examples slide)
Statistics reuse the project's own helpers (exact permutation p, Hedges g, MDE) from
eeg-emg-analysis/qc/sod_sleep_2x2_2026_10_06.py, the same ones stats.py uses; CI = Welch 95 %.
Every recomputed number is checked against stats.txt (assert) so the slides cannot drift from the vault.

Figures -> /home/andrea/hlb_meeting_deck/v2/fig/eeg_NN_*.png (+ .pdf)
Usage: python3 nanotag/analysis/report/labmtg/eeg.py
"""
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats as st

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "eeg-emg-analysis" / "qc"))
from style import *  # noqa: E402,F403
from sod_sleep_2x2_2026_10_06 import perm, hedges_g, mde_d  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

RES = REPO / "eeg-emg-analysis" / "rescore_2026_11" / "results"
ATT = REPO / "vault" / "_attachments"
OUT = Path("/home/andrea/hlb_meeting_deck/v2/fig")
OUT.mkdir(parents=True, exist_ok=True)

COHORTS = [("HLBWSD", "W-SD", "water", "SD"), ("HLBSSD", "S-SD", "SOD1", "SD"),
           ("HLBWSL", "W-SL", "water", "NS"), ("HLBSSL", "S-SL", "SOD1", "NS")]

# Main reason each non-usable window (tier C, D or X) was lost. Shortcut: my one-label summary of the agent
# review's `concerns` text (results/review_result.json) checked against the screen metrics in recordings.csv
# (eeg_median_log10_delta, eeg_line60_med_uv, eta_gap, auc_delta_recording, hours_both_ok); a window can have
# more than one problem, the label names the one that decided it. Upgrade: a `loss_reason` column in score.py.
CAUSE = {
    # EEG dead or disconnected: median log10 delta 0.3-0.9 (cortical EEG 2.3-3.3)
    "HLBSSL38_B": "EEG dead", "HLBWSD01_R": "EEG dead", "HLBWSD02_R": "EEG dead",
    "HLBWSD09_R": "EEG dead", "HLBWSL21_R": "EEG dead",
    # EEG swamped by mains or railed: 2-6 mV of 60 Hz on the EEG, 60-100 % artefact epochs (grounding)
    "HLBSSD14_B": "EEG mains / railed", "HLBWSD03_R": "EEG mains / railed", "HLBWSD04_R": "EEG mains / railed",
    "HLBWSD07_B": "EEG mains / railed", "HLBWSD07_R": "EEG mains / railed", "HLBSSD19_B": "EEG mains / railed",
    "HLBWSD09_B": "EEG mains / railed", "HLBWSD06_B": "EEG mains / railed",
    # EEG good in parts, drops out or fades: too few hours with both signals usable
    "HLBSSD15_R": "EEG contact intermittent", "HLBSSD16_R": "EEG contact intermittent",
    "HLBSSD12_R": "EEG contact intermittent", "HLBSSL31_B": "EEG contact intermittent",
    "HLBWSD03_B": "EEG contact intermittent", "HLBSSD14_R": "EEG contact intermittent",
    # EEG connected but delta does not separate sleep from wake (AUC 0.25-0.60)
    "HLBSSD11_R": "EEG does not follow state", "HLBSSD17_R": "EEG does not follow state",
    "HLBWSD06_R": "EEG does not follow state",
    # EMG technical: no sleep floor, flat plateaus, eta < 0.70 or mV of mains (open lead)
    "HLBSSD16_B": "EMG technical (open lead)", "HLBSSD19_R": "EMG technical (open lead)",
    "HLBWSD04_B": "EMG technical (open lead)", "HLBSSD13_B": "EMG technical (open lead)",
}
CAUSE_ORDER = ["EEG dead", "EEG mains / railed", "EEG contact intermittent", "EEG does not follow state",
               "EMG technical (open lead)"]
CAUSE_COL = ["#4D4D4D", "#CC79A7", "#E69F00", "#009E73", "#56B4E9"]
CAUSE_HATCH = ["", "//", "..", "xx", "\\\\"]

STATS_TXT = (RES / "stats.txt").read_text()


def rows(name):
    with open(RES / name) as fh:
        return list(csv.DictReader(fh))


def stats_line(prefix):
    """The stats.txt line that starts with this label (for the cross-check)."""
    for ln in STATS_TXT.splitlines():
        if ln.strip().startswith(prefix):
            return ln
    raise KeyError(prefix)


def compare(a: dict, b: dict):
    """a vs b ({mouse: value}): diff, Welch 95 % CI, exact permutation p, Hedges g, MDE in points."""
    va, vb = list(a.values()), list(b.values())
    obs, p, pmin = perm(va, vb)
    ci = st.ttest_ind(va, vb, equal_var=False).confidence_interval()
    sp = np.sqrt(((len(va) - 1) * np.var(va, ddof=1) + (len(vb) - 1) * np.var(vb, ddof=1)) / (len(va) + len(vb) - 2))
    return dict(ma=np.mean(va), mb=np.mean(vb), na=len(va), nb=len(vb), diff=obs, p=p, pmin=pmin,
                lo=ci.low, hi=ci.high, g=hedges_g(va, vb), mde=mde_d(len(va), len(vb)) * sp)


def dots(ax, x, vals, color, marker="o", hollow=False, seed=0, mean=True, size=80):
    """Dots = mice (small fixed jitter), black mean +/- SEM bar beside them."""
    v = np.asarray(vals, float)
    jit = np.random.default_rng(seed).uniform(-0.12, 0.12, len(v)) if len(v) > 1 else np.zeros(1)
    ax.scatter(x + jit, v, s=size, marker=marker, facecolor="white" if hollow else color, edgecolor=color if hollow else INK,
               linewidth=1.6 if hollow else 0.7, zorder=3)
    if mean and len(v) > 1:
        m, se = v.mean(), v.std(ddof=1) / np.sqrt(len(v))
        ax.errorbar(x + 0.3, m, yerr=se, fmt="_", color=INK, ms=22, mew=2.5, elinewidth=2, capsize=6, zorder=4)


# ---------------------------------------------------------------- data
REC = rows("recordings.csv")
TIERS = json.loads((RES / "final_tiers.json").read_text())
for r in REC:
    assert TIERS[f"{r['mouse']}_{r['tp']}"]["tier"] == r["tier"], r["mouse"]
SEG = rows("per_mouse_segments.csv")


def seg(tp, segment, metric="sleep_pct", source="rule", **kw):
    q = [s for s in SEG if s["tp"] == tp and s["segment"] == segment and s["source"] == source
         and all(s[k] == v for k, v in kw.items())]
    return {s["mouse"]: float(s[metric]) for s in q}


# ======================================================== 01 cohorts: what survived, and why the rest was lost
def fig01():
    print("\n== eeg_01 cohort flow (final tiers, results/final_tiers.json + recordings.csv)")
    usable = {(r["mouse"], r["tp"]) for r in REC if r["tier"] in ("A", "B")}
    oldok = {(r["mouse"], r["tp"]) for r in REC if r["old_qc"] == "SCOREABLE"}
    lost = [r for r in REC if r["tier"] not in ("A", "B")]
    assert {f"{r['mouse']}_{r['tp']}" for r in lost} == set(CAUSE), "every lost window needs a cause"
    summ = {}
    for b, name, *_ in COHORTS:
        mice = sorted({r["mouse"] for r in REC if r["batch"] == b})
        nb = sum(1 for r in REC if r["batch"] == b and r["tp"] == "B")
        nr = sum(1 for r in REC if r["batch"] == b and r["tp"] == "R")
        ub = sum(1 for m in mice if (m, "B") in usable)
        ur = sum(1 for m in mice if (m, "R") in usable)
        pa = [m for m in mice if (m, "B") in usable and (m, "R") in usable]
        po = [m for m in mice if (m, "B") in oldok and (m, "R") in oldok]
        causes = {c: sum(1 for r in lost if r["batch"] == b and CAUSE[f"{r['mouse']}_{r['tp']}"] == c) for c in CAUSE_ORDER}
        summ[name] = dict(nb=nb, nr=nr, ub=ub, ur=ur, paired=pa, old=po, causes=causes)
        print(f"  {name}: baseline windows {nb}, usable (A/B) {ub}; recovery windows {nr}, usable {ur}; "
              f"paired {len(pa)} {pa}; old pipeline paired {len(po)} {po}; lost by cause {causes}")
    tot_new = sum(len(s["paired"]) for s in summ.values()); tot_old = sum(len(s["old"]) for s in summ.values())
    print(f"  paired total: re-score {tot_new}, old pipeline {tot_old}")
    assert (tot_new, tot_old) == (15, 3)
    gained = [r for r in REC if r["tier"] in ("A", "B") and r["old_qc"] != "SCOREABLE"]
    r2 = sum(r["old_qc_why"].startswith("rung 2") for r in gained); r3 = sum(r["old_qc_why"].startswith("rung 3") for r in gained)
    print(f"  windows usable now but not SCOREABLE in the old screen: {len(gained)} (old rung 2 chip-floor test {r2}, "
          f"old rung 3 r@1min on 10-124 Hz EMG {r3})")
    print(f"  lost windows (tier C/D/X): {len(lost)} of {len(REC)}; by cause, all cohorts: "
          + ", ".join(f"{c} {sum(s['causes'][c] for s in summ.values())}" for c in CAUSE_ORDER))
    for c in CAUSE_ORDER:
        print(f"    {c}: " + ", ".join(sorted(k for k, v in CAUSE.items() if v == c)))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.6, 5.6), gridspec_kw=dict(width_ratios=[1.35, 1]))
    names = [c[1] for c in COHORTS]
    y = np.arange(4)[::-1]
    h = 0.24
    for i, (b, name, liq, cond) in enumerate(COHORTS):
        s, col = summ[name], COL[(liq, cond)]
        for k, (val, of, lab, alpha) in enumerate(((s["ub"], s["nb"], "baseline usable", 0.45),
                                                   (s["ur"], s["nr"], "recovery usable", 0.70),
                                                   (len(s["paired"]), None, "paired", 1.0))):
            yy = y[i] + (1 - k) * h
            a1.barh(yy, val, height=h * 0.92, color=col, alpha=alpha, edgecolor=INK, linewidth=0.8)
            a1.text(val + 0.12, yy, f"{val}" + (f" / {of}" if of else ""), va="center", fontsize=13)
            a1.text(-0.15, yy, lab if k < 2 else "paired (both)", ha="right", va="center", fontsize=11,
                    color="#555555" if k < 2 else INK, fontweight="bold" if k == 2 else None)
            if k == 2:
                a1.text(val + 0.75, yy, f"(old screen: {len(s['old'])})", va="center", fontsize=12, color="#555555")
        a1.text(-3.3, y[i], name, ha="right", va="center", fontsize=16, fontweight="bold", color=col)
    a1.set_xlim(0, 9.4); a1.set_ylim(-0.55, 3.55); a1.set_yticks([])
    a1.set_xlabel("windows (one mouse, one 24 h recording)")
    a1.spines["left"].set_visible(False)
    a1.set_title(f"What survived: {tot_new} paired mice (old screen: {tot_old})", loc="left", x=-0.3)

    left = np.zeros(4)
    for c, colr, hat in zip(CAUSE_ORDER, CAUSE_COL, CAUSE_HATCH):
        v = np.array([summ[n]["causes"][c] for n in names])
        a2.barh(y, v, left=left, color=colr, hatch=hat, edgecolor="white", linewidth=0.8, label=c, height=0.6)
        for yy, vv, ll in zip(y, v, left):
            if vv:
                a2.text(ll + vv / 2, yy, str(vv), ha="center", va="center", fontsize=13,
                        color="white" if colr in ("#4D4D4D", "#009E73") else INK, fontweight="bold")
        left += v
    for yy, n in zip(y, names):
        a2.text(left[names.index(n)] + 0.2, yy, f"{int(left[names.index(n)])} lost", va="center", fontsize=12)
    a2.set_yticks(y, names); a2.set_xlim(0, 15)
    for t, (_, _, liq, cond) in zip(a2.get_yticklabels(), COHORTS):
        t.set_color(COL[(liq, cond)]); t.set_fontweight("bold")
    a2.set_xlabel("lost windows (tier C, D or X)")
    a2.set_title("Why the rest was lost (main cause)")
    a2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=11.5)
    fig.tight_layout()
    save(fig, OUT / "eeg_01_cohorts_survival")


# ======================================================== 02 good vs bad, cropped from the overview figures
EXAMPLES = [  # (stem, title line, reason line)
    ("hlbssl33-r", "HLBSSL33 recovery: tier A (usable)",
     "δ and EMG alternate together; hand-checked by Andrea"),
    ("hlbwsd03-r", "HLBWSD03 recovery: tier X (lost)",
     "~5 mV of 60 Hz on EEG and EMG: no sleep-wake pattern (ground)"),
    ("hlbwsd01-r", "HLBWSD01 recovery: tier D (EMG only)",
     "EEG dead (δ ~200x below normal); EMG still shows sleep-wake"),
    ("hlbssd15-r", "HLBSSD15 recovery: tier D (EMG only)",
     "EEG drops to a flat line again and again: only 5 h usable"),
]


def fig02():
    print("\n== eeg_02 examples (crops of vault/_attachments/2026-11-03-hlb-eeg-*-overview.png)")
    for stem, *_ in EXAMPLES:
        m, tp = stem.split("-"); r = next(x for x in REC if x["mouse"] == m.upper() and x["tp"] == tp.upper())
        print(f"  {m.upper()}_{tp.upper()}: tier {r['tier']}, log10 delta {r['eeg_median_log10_delta']}, "
              f"EEG 60 Hz {r['eeg_line60_med_uv']} uV, EMG 60 Hz {r['emg_line60_med_uv']} uV, eta {r['eta_gap']}, "
              f"delta AUC {r['auc_delta_recording']}, hours both usable {r['hours_both_ok']}, artefact {r['artifact_pct']} %")
    fig, axs = plt.subplots(2, 2, figsize=(13.0, 8.4))
    for ax, (stem, title, why) in zip(axs.flat, EXAMPLES):
        im = plt.imread(ATT / f"2026-11-03-hlb-eeg-{stem}-overview.png")
        assert im.shape[:2] == (880, 1280), im.shape     # crop rows are fixed to that layout
        # spectrogram + log delta / theta-delta + EMG rows, then the hour-usable bar with the time axis
        crop = np.vstack([im[28:640, :1240], im[778:868, :1240]])
        ax.imshow(crop, interpolation="lanczos"); ax.set_axis_off()
        ax.set_title(title, fontsize=14, loc="left")
        ax.text(0.0, -0.02, why, transform=ax.transAxes, va="top", fontsize=12, color="#444444")
    fig.text(0.01, 0.005, "Rows: EEG spectrogram 0-30 Hz; log δ (black) and θ/δ (green); EMG 70-470 Hz between the 60 Hz "
             "harmonics, log scale; hours usable (green) or not (red). x = hours from window start.",
             fontsize=11, color="#555555")
    fig.subplots_adjust(left=0.005, right=0.995, top=0.95, bottom=0.07, wspace=0.03, hspace=0.22)
    save(fig, OUT / "eeg_02_good_vs_bad_examples")


# ======================================================== 03 how it was scored + check against Andrea
def fig03():
    print("\n== eeg_03 scoring check (results/handscore_check_hlbssl33_r_to19028.txt, the last and fullest check)")
    txt = (RES / "handscore_check_hlbssl33_r_to19028.txt").read_text()
    blocks = re.split(r"\n== ", txt)[1:]
    want = {"re-score (final)": "re-score", "HMM (no rule input)": "HMM (no rule input)",
            "EEG alone, NREM vs not": "EEG alone (NREM vs not)"}
    K = {}
    for bl in blocks:
        head = bl.split(":")[0]
        n = re.search(r"(\d+) epochs reviewed", bl).group(1)
        for k in want:
            K[(head, k)] = float(re.search(re.escape(k) + r"\s+kappa ([0-9.]+)", bl).group(1))
        print(f"  {head}: {n} epochs; " + ", ".join(f"{k} kappa {K[(head, k)]:.3f}" for k in want))
    labels = {"1-8441": "light\nZT0-9.4", "10801-13624": "early dark\nZT12-15", "16201-19028": "late dark\nZT18-21",
              "all reviewed": "all 14,077\nepochs"}
    assert set(labels) == {b.split(":")[0] for b in blocks}

    fig = plt.figure(figsize=(13.0, 6.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1])
    a0 = fig.add_subplot(gs[0]); a0.set_axis_off(); a0.set_xlim(-0.2, 10.4); a0.set_ylim(-0.2, 10.4)
    a0.set_title("How sleep was scored (4-s epochs)", loc="left")

    def box(x, y, w, h, text, fc="#F2F2F2", ec=INK, fs=12.5, bold=False):
        a0.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15", fc=fc, ec=ec, lw=1.3))
        a0.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight="bold" if bold else None)

    def arrow(x0, y0, x1, y1):
        a0.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", lw=1.6, color=INK))

    box(0.0, 7.6, 2.8, 2.2, "EEG\nspectrum\n(1-s Welch)", bold=True)
    box(0.0, 4.4, 2.8, 2.6, "EMG\n70-470 Hz,\nnotch at each\n60 Hz harmonic", bold=True, fs=12)
    box(3.5, 7.6, 3.0, 2.2, "δ power 1-4 Hz\nθ/δ, θ 6-9 Hz")
    box(3.5, 4.4, 3.0, 2.6, "EMG RMS + tone;\ncut fitted on\neach recording\n(Otsu)", fs=12)
    arrow(2.9, 8.7, 3.4, 8.7); arrow(2.9, 5.7, 3.4, 5.7)
    box(7.2, 4.4, 3.1, 5.4, "rule, per epoch\n\nEMG above cut\n→ Wake\n\nelse θ/δ high\nand δ low\n→ REM\n\nelse → NREM",
        fc="#FFF4E0", fs=12)
    arrow(6.6, 8.7, 7.1, 8.0); arrow(6.6, 5.7, 7.1, 6.2)
    box(0.0, 0.0, 4.7, 3.7, "artefact epochs (rail, flat,\n> 6 robust SD): no cut,\nno statistic\n\n"
        "2nd scorer: 3-state HMM,\nno labels, flags\ndisagreements", fc="#EEF4FA", fs=11.5)
    box(5.2, 0.0, 5.1, 3.7, "usable hours (no labels):\nEMG separable, η ≥ 0.70\nEEG sees state, δ AUC ≥ 0.75\n"
        "EEG level 2-4 log10 µV²\n\ntier A ≥ 20 h, B ≥ 6 L + 6 D h", fc="#EEF4FA", fs=11.5)

    a1 = fig.add_subplot(gs[1])
    order = list(labels)
    x = np.arange(len(order)); w = 0.26
    cols = ["#333333", "#999999", "#DDDDDD"]
    for j, (k, lab) in enumerate(want.items()):
        v = [K[(o, k)] for o in order]
        bars = a1.bar(x + (j - 1) * w, v, w, color=cols[j], edgecolor=INK, linewidth=0.7, label=lab)
        if j == 0:
            for xx, vv in zip(x, v):
                a1.text(xx - w, vv + 0.008, f"{vv:.2f}", ha="center", fontsize=12, fontweight="bold")
    a1.set_xticks(x, [labels[o] for o in order], fontsize=12.5)
    a1.set_ylim(0.7, 1.0); a1.set_ylabel("Cohen's κ vs Andrea's review")
    a1.axhline(0.8, color=CHANCE, lw=1, ls=":"); a1.text(3.55, 0.803, "0.8", color=CHANCE, fontsize=11)
    a1.set_title("Check: Andrea's review of HLBSSL33 R", loc="left")
    a1.legend(loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=3, fontsize=11, handlelength=1.2, columnspacing=0.8)
    a1.text(0, -0.36, "y axis starts at 0.7. Not blind: she corrected the rule's first pass.", transform=a1.transAxes,
            fontsize=11, color="#555555")
    fig.tight_layout()
    save(fig, OUT / "eeg_03_scoring_and_check")


# ======================================================== 04 normal sleep: baseline SOD1 vs water
def fig04():
    print("\n== eeg_04 baseline sleep % of usable time, tier A/B, all four cohorts (on treatment, before any SD)")
    SDB = {"HLBWSD", "HLBSSD"}
    fig, axs = plt.subplots(1, 3, figsize=(12.6, 5.6), sharey=False)
    for ax, segm, ttl, key in zip(axs, ("24h", "light", "dark"), ("24 h", "light (ZT0-12)", "dark (ZT12-24)"),
                                  ("all batches, 24h", "all batches, light", "all batches, dark")):
        w = seg("B", segm, liquid="water"); s = seg("B", segm, liquid="SOD1")
        c = compare(s, w)
        ref = stats_line(f"[rule sleep_pct] {key}")
        assert f"SOD1 n={c['na']}" in ref and f"{c['ma']:5.1f} vs water n={c['nb']} {c['mb']:5.1f}" in ref, ref
        assert f"CI [{c['lo']:+.1f}, {c['hi']:+.1f}]" in ref and f"MDE {c['mde']:.0f} pts" in ref, ref
        print(f"  {segm}: water {c['mb']:.1f} (n={c['nb']}) vs SOD1 {c['ma']:.1f} (n={c['na']}); SOD1-water {c['diff']:+.1f} pts, "
              f"95 % CI [{c['lo']:+.1f}, {c['hi']:+.1f}], exact p={c['p']:.3f}, g={c['g']:+.2f}, MDE {c['mde']:.1f} pts  (matches stats.txt)")
        for i, (liq, d, colr) in enumerate((("water", w, WATER), ("SOD1", s, SOD1))):
            sl = [v for m, v in d.items() if m[:6] not in SDB]; sd = [v for m, v in d.items() if m[:6] in SDB]
            dots(ax, i, sl, colr, "o", seed=i, mean=False)
            dots(ax, i, sd, colr, "s", seed=10 + i, mean=False)
            v = np.array(list(d.values()))
            ax.errorbar(i + 0.32, v.mean(), yerr=v.std(ddof=1) / np.sqrt(len(v)), fmt="_", color=INK, ms=22, mew=2.5,
                        elinewidth=2, capsize=6, zorder=4)
            ax.text(i, -0.1, f"n = {len(v)}", transform=ax.get_xaxis_transform(), ha="center", fontsize=13)
        ax.set_xticks([0, 1], ["water", "SOD1"]); ax.set_xlim(-0.6, 1.7)
        lo, hi = {"24h": (35, 75), "light": (55, 90), "dark": (10, 55)}[segm]
        ax.set_ylim(lo, hi); ax.set_title(ttl)
        ax.text(0.5, 0.97, f"Δ {c['diff']:+.1f} pts [{c['lo']:+.1f}, {c['hi']:+.1f}]\np = {c['p']:.2f} · MDE {c['mde']:.0f} pts",
                transform=ax.transAxes, ha="center", va="top", fontsize=12.5)
    axs[0].set_ylabel("sleep, % of usable time")
    axs[0].scatter([], [], marker="o", s=70, facecolor="white", edgecolor=INK, label="SL cohort")
    axs[0].scatter([], [], marker="s", s=70, facecolor="white", edgecolor=INK, label="SD cohort, before SD")
    axs[0].legend(loc="lower left", fontsize=11.5)
    # NREM and EEG-only sensitivity, printed for the bullets
    for lab, src, metric, n in (("NREM %", "rule", "nrem_pct", "[rule nrem_pct] all batches, 24h"),
                                ("EEG-alone NREM % (tiers A/B/C)", "eeg_only", "nrem_pct", "[eeg_only nrem_pct] all batches, 24h")):
        c = compare(seg("B", "24h", metric, src, liquid="SOD1"), seg("B", "24h", metric, src, liquid="water"))
        assert f"CI [{c['lo']:+.1f}, {c['hi']:+.1f}]" in stats_line(n)
        print(f"  {lab} 24 h: water {c['mb']:.1f} (n={c['nb']}) vs SOD1 {c['ma']:.1f} (n={c['na']}); {c['diff']:+.1f} pts, "
              f"CI [{c['lo']:+.1f}, {c['hi']:+.1f}], p={c['p']:.3f}, MDE {c['mde']:.1f}")
    c = compare(seg("B", "24h", liquid="SOD1", protocol="SL"), seg("B", "24h", liquid="water", protocol="SL"))
    print(f"  SL cohorts only, sleep 24 h: water {c['mb']:.1f} (n={c['nb']}) vs SOD1 {c['ma']:.1f} (n={c['na']}); "
          f"{c['diff']:+.1f} pts, CI [{c['lo']:+.1f}, {c['hi']:+.1f}], p={c['p']:.3f}, MDE {c['mde']:.1f}")
    fig.tight_layout()
    save(fig, OUT / "eeg_04_baseline_sleep_sod1_vs_water")


# ======================================================== 05 SD vs normal sleep: recovery - baseline, and SWA
HLBSSD18_ARTEFACT_AS_WAKE = 1.5   # vault hlb-eeg-sleep-overview.md:25,82 (not in a results file, see the spec)


def fig05():
    print("\n== eeg_05 recovery - baseline (same mouse, ZT4-24, tier A/B in both) and NREM delta ZT4-8")
    groups = [("W-SL", "HLBWSL", "water", "NS"), ("W-SD", "HLBWSD", "water", "SD"),
              ("S-SL", "HLBSSL", "SOD1", "NS"), ("S-SD", "HLBSSD", "SOD1", "SD")]
    D = {}
    for name, b, *_ in groups:
        bb, rr = seg("B", "ZT4-24", batch=b), seg("R", "ZT4-24", batch=b)
        D[name] = {m: rr[m] - bb[m] for m in bb if m in rr}
        print(f"  {name} change in sleep %: " + ", ".join(f"{m} {v:+.1f}" for m, v in D[name].items())
              + (f"; mean {np.mean(list(D[name].values())):+.1f}" if len(D[name]) > 1 else ""))
    c = compare(D["S-SL"], D["W-SL"])
    ref = stats_line("SL: SOD1 vs water change")
    assert f"CI [{c['lo']:+.1f}, {c['hi']:+.1f}]" in ref, ref
    print(f"  SL, SOD1 vs water: {c['ma']:+.1f} vs {c['mb']:+.1f}, diff {c['diff']:+.1f} pts, CI [{c['lo']:+.1f}, {c['hi']:+.1f}], "
          f"p={c['p']:.3f}, MDE {c['mde']:.1f}  (matches stats.txt)")
    for name in ("W-SD", "S-SD"):
        sl = "W-SL" if name[0] == "W" else "S-SL"
        (m, v), = D[name].items()
        print(f"  {name} {m}: {v:+.1f} vs {sl} mean {np.mean(list(D[sl].values())):+.1f} (range "
              f"{min(D[sl].values()):+.1f} to {max(D[sl].values()):+.1f}); difference {v - np.mean(list(D[sl].values())):+.1f}: a case")
    print(f"  HLBSSD18 with EMG-rail artefact epochs counted as wake: {HLBSSD18_ARTEFACT_AS_WAKE:+.1f} (vault overview note)")

    sw = {r["mouse"]: float(r["0"]) for r in rows("nrem_delta_zt4_8_pct_baseline.csv")}
    SW = {name: {m: v for m, v in sw.items() if m.startswith(b)} for name, b, *_ in groups}
    for name in SW:
        v = list(SW[name].values())
        print(f"  NREM delta ZT4-8, % own baseline, {name}: " + ", ".join(f"{m} {x:.1f}" for m, x in SW[name].items())
              + (f"; mean {np.mean(v):.1f}" if len(v) > 1 else ""))
    c2 = compare(SW["S-SL"], SW["W-SL"])   # not in stats.txt: exploratory, not pre-specified, cohort = group
    print(f"  NREM delta ZT4-8, no SD, SOD1 vs water (exploratory, not in stats.txt): {c2['ma']:.1f} vs {c2['mb']:.1f}, "
          f"diff {c2['diff']:+.1f} pts, CI [{c2['lo']:+.1f}, {c2['hi']:+.1f}], exact p={c2['p']:.4f} (min {c2['pmin']:.4f}), g={c2['g']:+.2f}")
    assert abs(np.mean(list(SW["W-SL"].values())) - 107.2) < 0.05 and abs(np.mean(list(SW["S-SL"].values())) - 92.7) < 0.05

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.6, 5.8))
    xs = [0, 1, 2.4, 3.4]
    for ax, data, yl, ref0 in ((a1, D, "sleep, recovery − baseline (pts)", 0), (a2, SW, "NREM δ, ZT4-8, % of own baseline", 100)):
        ax.axhline(ref0, color=CHANCE, lw=1, ls="--", zorder=0)
        for x, (name, b, liq, cond) in zip(xs, groups):
            v = list(data[name].values()); colr = COL[(liq, cond)]
            if cond == "SD":
                ax.scatter([x], v, s=150, facecolor=colr, edgecolor=INK, linewidth=1.0, zorder=3)
                ax.annotate(list(data[name])[0], (x, v[0]), xytext=(10, 0), textcoords="offset points", va="center", fontsize=11.5)
            else:
                dots(ax, x, v, colr, seed=int(x * 10))
            ax.text(x, -0.2, f"n = {len(v)}", transform=ax.get_xaxis_transform(), ha="center", fontsize=13)
        ax.set_xticks(xs, ["water\nno SD", "water\nSD", "SOD1\nno SD", "SOD1\nSD"])
        ax.set_xlim(-0.6, 4.3); ax.set_ylabel(yl)
    a1.scatter([3.4], [HLBSSD18_ARTEFACT_AS_WAKE], s=150, facecolor="white", edgecolor=SOD1_SD, linewidth=2.2, zorder=3)
    a1.plot([3.4, 3.4], [D["S-SD"]["HLBSSD18"], HLBSSD18_ARTEFACT_AS_WAKE], ls=":", color=SOD1_SD, lw=1.5, zorder=2)
    a1.annotate("same mouse,\nartefact epochs\ncounted as wake", (3.4, HLBSSD18_ARTEFACT_AS_WAKE), xytext=(0, -16),
                textcoords="offset points", ha="center", va="top", fontsize=10.5, color="#555555")
    a1.set_ylim(-13, 26); a2.set_ylim(84, 124)
    a1.set_title("Sleep gained after SD (ZT4-24)")
    a1.text(0.02, 0.98, f"no SD: SOD1 − water {c['diff']:+.1f} pts [{c['lo']:+.1f}, {c['hi']:+.1f}], p = {c['p']:.2f}",
            transform=a1.transAxes, ha="left", va="top", fontsize=12)
    a2.set_title("Slow-wave rebound, first 4 h")
    a2.text(0.02, 0.98, "SD arms: one mouse each, a case", transform=a2.transAxes, ha="left", va="top", fontsize=12)
    fig.tight_layout()
    save(fig, OUT / "eeg_05_sd_vs_normal_sleep")


if __name__ == "__main__":
    fig01(); fig02(); fig03(); fig04(); fig05()
    print("\nfigures ->", OUT)

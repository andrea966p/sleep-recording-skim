"""Figure 8: statistics behind the hardware claims.
Figure 9: statistics behind the sleep claims.

Changes from the first version, all forced by the audit:
  * Holm and Benjamini-Hochberg adjusted p values, because 16 channels are
    tested against one shared comparison group.
  * A port level permutation p beside the Fisher p, because the 2,240 floor
    readings are clustered in 4 ports and are not 2,240 independent draws.
  * Risk difference with an interval, because a p value alone does not say how
    much better a channel is than a bare wire.
  * The tether comparison shown at BOTH pass marks. At 2 MOhm it is the headline
    the project has been quoting; at the corrected 0.5 MOhm pass mark the EEG
    half of it reverses. That reversal was found while rebuilding this figure.
  * The rank correlation gets an exact permutation p, because with this many
    ties the asymptotic p value is not trustworthy.
"""
from __future__ import annotations

import csv
import glob
from pathlib import Path

import numpy as np
from scipy import stats

from figs_common import *   # noqa: F401,F403
from core import paths as PATHS

D = derived("inputs.json")
rng = np.random.default_rng(SEED)
N_PERM = 10000


def read_sweep(path):
    out = {}
    with open(path, encoding="utf-8") as fh:
        rd = csv.reader(fh)
        next(rd)
        for row in rd:
            if len(row) >= 2 and row[0]:
                try:
                    out[row[0]] = float(row[1])
                except ValueError:
                    pass
    return out


# ------------------------------------------------------------------ Figure 8
C = D["census"]
fk, fn = C["floor_k"], C["floor_n"]
floor_pct = 100 * fk / fn
by_port = C["floor_by_port"]

rows = []
for name, rec in C["channels"].items():
    k, n = rec["k"], rec["n"]
    _, p = stats.fisher_exact([[k, n - k], [fk, fn - fk]], alternative="greater")
    lo, hi = stats.beta.ppf([0.025, 0.975], k + 0.5, n - k + 0.5)
    # risk difference against the floor, Newcombe style interval from the two
    # Jeffreys intervals: how much MORE often than a bare wire, in points
    flo, fhi = stats.beta.ppf([0.025, 0.975], fk + 0.5, fn - fk + 0.5)
    rd_lo = (k / n - flo) - np.sqrt((k / n - lo) ** 2 + (fhi - fk / fn) ** 2)
    rd_hi = (k / n - fk / fn) + np.sqrt((hi - k / n) ** 2 + (fk / fn - flo) ** 2)
    # cluster aware alternative: compare against the four PORT level floor rates
    port_rates = np.array([v[0] / v[1] for v in by_port.values()])
    p_cluster = (1 + np.sum(port_rates >= k / n)) / (1 + len(port_rates))
    rows.append(dict(name=name, k=k, n=n, pct=100 * k / n, lo=100 * lo, hi=100 * hi,
                     p=p, rd=100 * (k / n - fk / fn), rd_lo=100 * rd_lo,
                     rd_hi=100 * rd_hi, p_cluster=p_cluster))
holm, bh = holm_bh([r["p"] for r in rows])
for r, h, b in zip(rows, holm, bh):
    r["holm"], r["bh"] = h, b
rows.sort(key=lambda r: (-r["pct"], r["name"]))
for r in rows:
    print(f"  {r['name']:8} {r['k']:2d}/{r['n']}  p={r['p']:.3g}  holm={r['holm']:.3g} "
          f" BH={r['bh']:.3g}  RD={r['rd']:+.1f} [{r['rd_lo']:+.1f}, {r['rd_hi']:+.1f}] "
          f" port-perm p={r['p_cluster']:.2f}")

# tether comparison at both pass marks, recomputed from the CSVs
IMP05 = PATHS.IMPEDANCE_ROOT / "2026-08-05"
arms = {}
for label, site in (("B1 EEG", "B/1"), ("B1 EMG", "B/2"),
                    ("D2 EEG, control", "D/1"), ("D2 EMG, control", "D/2")):
    entry = {}
    for thr in (2.0, 0.5):
        vals = {}
        for arm, folder in (("A", "armA-original"), ("B", "armB-short-soldered")):
            ds = [read_sweep(f) for f in sorted(glob.glob(str(IMP05 / folder / "*.csv")))]
            k = sum(1 for d in ds if site in d and d[site] < thr)
            n = sum(1 for d in ds if site in d)
            vals[arm] = (k, n)
        _, p = stats.fisher_exact([[vals["B"][0], vals["B"][1] - vals["B"][0]],
                                   [vals["A"][0], vals["A"][1] - vals["A"][0]]])
        entry[thr] = dict(a=vals["A"], b=vals["B"], p=p)
    arms[label] = entry
for k, v in arms.items():
    print(f"  {k:18} 2.0 MOhm {v[2.0]['a'][0]}/{v[2.0]['a'][1]} -> {v[2.0]['b'][0]}/{v[2.0]['b'][1]}"
          f" p={v[2.0]['p']:.4f}   0.5 MOhm {v[0.5]['a'][0]}/{v[0.5]['a'][1]} -> "
          f"{v[0.5]['b'][0]}/{v[0.5]['b'][1]} p={v[0.5]['p']:.4f}")

with style_context(STYLE, palette_name=PALETTE):
    fig, (ax1, ax2), cap = figure_with_caption(1, 2, figsize=(12.4, 5.6),
                                               caption_frac=0.28,
                                               width_ratios=[1.55, 1])
    y = np.arange(len(rows))[::-1]
    for i, r in zip(y, rows):
        sig = r["holm"] < 0.05
        colr = C_WORK if sig else C_FLOOR
        ax1.plot([r["lo"], r["hi"]], [i, i], color=colr, lw=2.2,
                 solid_capstyle="butt")
        ax1.plot(r["pct"], i, "o" if sig else "x", color=colr, ms=5.5)
        ax1.text(103, i, f"{r['k']}/{r['n']}", fontsize=6.6, va="center")
        ax1.text(118, i, ("<0.001" if r["p"] < 0.001 else f"{r['p']:.3f}"),
                 fontsize=6.6, va="center",
                 color="#111111" if sig else "#999999")
        ax1.text(140, i, ("<0.001" if r["holm"] < 0.001 else f"{r['holm']:.3f}"),
                 fontsize=6.6, va="center", fontweight="bold" if sig else "normal",
                 color="#111111" if sig else "#999999")
        ax1.text(162, i, f"{r['p_cluster']:.2f}", fontsize=6.6, va="center",
                 color="#111111" if r["p_cluster"] < 0.3 else "#999999")
    for xx, lab in ((110, "k/n"), (128, "p"), (150, "Holm"), (168, "port")):
        ax1.text(xx, len(rows) - 0.4, lab, fontsize=6.8, ha="center",
                 fontweight="bold", color="#333333")
    ax1.axvline(floor_pct, color=C_FAIL, lw=1.4, ls="--")
    ax1.annotate(f"wire free inputs, {fk} of {fn} = {floor_pct:.1f} percent",
                 xy=(floor_pct, 4.4), xytext=(26, 3.4), color=C_FAIL, fontsize=7,
                 arrowprops=dict(arrowstyle="->", color=C_FAIL, lw=1.0))
    ax1.set_yticks(y)
    ax1.set_yticklabels([r["name"] for r in rows], fontsize=7)
    ax1.set_xlim(-2, 178)
    ax1.set_xticks([0, 25, 50, 75, 100])
    ax1.set_xlabel("percent of sweeps below 0.5 MOhm, 95 percent interval")
    ax1.set_title("Every channel against a wire that goes nowhere", loc="left",
                  fontsize=8.8)

    labels = list(arms)
    yy = np.arange(len(labels))[::-1]
    for i, name in zip(yy, labels):
        for thr, dy, mk in ((2.0, 0.16, "o"), (0.5, -0.16, "s")):
            v = arms[name][thr]
            a = 100 * v["a"][0] / v["a"][1]
            b = 100 * v["b"][0] / v["b"][1]
            ctrl = "control" in name
            ax2.annotate("", xy=(b, i + dy), xytext=(a, i + dy),
                         arrowprops=dict(arrowstyle="-|>", lw=1.3,
                                         color="#BBBBBB" if ctrl else "#777777"))
            ax2.plot(a, i + dy, mk, color=C_FLOOR, ms=6, zorder=3)
            ax2.plot(b, i + dy, mk, color=(C_FAIL if ctrl else C_WORK), ms=6,
                     zorder=3)
            ptxt = f"p={v['p']:.4f}" if v["p"] >= 0.0001 else "p<0.0001"
            ax2.text(104, i + dy, f"{thr:.1f} MOhm  {ptxt}", fontsize=6.5,
                     va="center",
                     color="#111111" if v["p"] < 0.05 else "#999999")
    ax2.set_yticks(yy)
    ax2.set_yticklabels(labels, fontsize=7.5)
    ax2.set_xlim(-4, 150)
    ax2.set_xticks([0, 25, 50, 75, 100])
    ax2.set_xlabel("percent of sweeps connected")
    ax2.set_title("Original tether to rebuilt tether, at BOTH pass marks",
                  loc="left", fontsize=8.8)
    fig.suptitle("Figure 8.  Statistics behind the hardware claims",
                 fontsize=10.5, fontweight="bold")
    n_sig = sum(1 for r in rows if r["holm"] < 0.05)
    caption(cap,
        f"LEFT. Each channel measured {C['n_sweeps']} times over 11 minutes on 6 August, against every amplifier input "
        f"on the same chips with no wire attached, read in the same sweeps: {fn} readings. Fisher exact, one sided, "
        "with Jeffreys 95 percent intervals. Holm adjusts for the 16 tests against one shared comparison group; only "
        f"{n_sig} channels survive it, and three of those are muscle channels, so exactly ONE animal had a usable EEG "
        "that day. The final column is a cluster aware check: the observed rate compared against the four PORT level "
        "floor rates, since 2,240 readings from 4 ports are not 2,240 independent draws. It has no power at four "
        "clusters and is shown so the reader can see that, not as a second opinion. RIGHT. The tether comparison of "
        "5 August at both pass marks. At 2 MOhm, the threshold in use that day, B1's EEG goes 9 of 20 to 20 of 20. At "
        "the corrected 0.5 MOhm pass mark, adopted the next day once a cut cable was found to pass 22 percent of the "
        "time at 2 MOhm, the SAME BLOCKS give 5 of 20 to 2 of 20: the EEG improvement disappears and reverses, while "
        "the muscle channel still improves. The tether conclusion therefore rests on the RECORDING, where D2 went from "
        "0.0 to 87.9 percent usable, not on this impedance block.")
    save(fig, "2026-08-09-fig08-hardware-statistics",
         alt=("Left: forest plot of 16 channels with confidence intervals and adjusted p values against a wire free "
              "floor of 3.1 percent; four channels are significant after Holm adjustment. Right: arrows from original "
              "to rebuilt tether at two pass marks, showing that the EEG improvement present at 2 MOhm reverses at "
              "0.5 MOhm while the muscle channel improvement holds."),
         provenance={"raw_data": "impedance sweep CSVs, 6 August census and 5 August arms",
                     "transformations": "connected defined as magnitude below the stated pass mark",
                     "uncertainty": "Jeffreys 95 percent intervals; Fisher exact; Holm and BH adjustment",
                     "missing_data": "none"})

# ------------------------------------------------------------------ Figure 9
SETS = [("B1 overnight", "B1", OVERNIGHT, C_WORK),
        ("D2 overnight", "D2", OVERNIGHT, C_WORK2),
        ("B1 afternoon", "B1", AFTERNOON, "#7FB3D5")]
CODE = {"WAKE": 2, "NREM": 1, "REM": 0}


def blocks_of(pos, tag):
    rows_ = load_hypno(pos, tag)
    lab = np.array([CODE.get(r["state"], -1) for r in rows_])
    inb = np.array([r["in_block"] == "1" for r in rows_])
    segs, i = [], 0
    while i < len(inb):
        if inb[i]:
            j = i
            while j < len(inb) and inb[j]:
                j += 1
            segs.append(lab[i:j])
            i = j
        else:
            i += 1
    return segs


def r_at(segs, lag, mu=None):
    num = den = 0.0
    for s in segs:
        if len(s) < lag + 1:
            continue
        seg = ((s == 1) | (s == 0)).astype(float)
        x = seg - (seg.mean() if mu is None else mu)
        if not np.any(x):
            continue
        num += float((x[:-lag] * x[lag:]).sum())
        den += float((x * x).sum())
    return num / den if den > 0 else np.nan


def grand_mean(segs):
    a = np.concatenate([((s == 1) | (s == 0)).astype(float) for s in segs])
    return float(a.mean())


def rem_order(segs, n_perm=2000):
    def count(seqs):
        e = p_ = 0
        for s in seqs:
            for a, b in zip(s[:-1], s[1:]):
                if b == 0 and a != 0:
                    e += 1
                    p_ += (a == 1)
        return e, p_
    e, p_ = count(segs)
    obs = 100.0 * p_ / e
    runs_per = []
    for s in segs:
        runs, i = [], 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            runs.append((s[i], j - i))
            i = j
        runs_per.append(runs)
    null = []
    for _ in range(n_perm):
        seqs = []
        for runs in runs_per:
            idx = rng.permutation(len(runs))
            seqs.append(np.concatenate([np.full(runs[k][1], runs[k][0]) for k in idx]))
        ee, pp = count(seqs)
        null.append(100.0 * pp / ee if ee else np.nan)
    null = np.asarray(null, float)
    pval = (1 + np.sum(null >= obs)) / (1 + len(null))
    return obs, null, pval, (obs - np.nanmean(null)) / np.nanstd(null)


lags, lagnames = [15, 75, 150], ["1 min", "5 min", "10 min"]
with style_context(STYLE, palette_name=PALETTE):
    fig, (axA, axB, axC), cap = figure_with_caption(
        1, 3, figsize=(13.4, 5.2), caption_frac=0.30, width_ratios=[1.15, 1.15, 1])
    w = 0.26
    for i, (lbl, pos, tag, colr) in enumerate(SETS):
        segs = blocks_of(pos, tag)
        mu = grand_mean(segs)
        obs = [r_at(segs, L, mu=mu) for L in lags]
        raw = load_features(pos, tag)["persistence"]
        raw_v = [raw[k]["r"] for k in ("1min", "5min", "10min")]
        xpos = np.arange(3) + (i - 1) * w
        axA.bar(xpos, obs, width=w, color=colr, label=lbl)
        for xp, L in zip(xpos, lags):
            nd = np.array([r_at([rng.permutation(s) for s in segs], L, mu=mu)
                           for _ in range(300)])
            axA.plot([xp, xp], [np.percentile(nd, 2.5), np.percentile(nd, 97.5)],
                     color="#111111", lw=3.0, solid_capstyle="butt", zorder=5)
        axA.plot(xpos, raw_v, "_", color="#111111", ms=11, mew=1.8, zorder=6,
                 label="headline value, raw labels" if i == 0 else None)
    axA.axhline(0.510, color=C_ACCENT, lw=1.1, ls="--")
    axA.text(2.44, 0.53, "4 minute bouts, +0.510", fontsize=6.7, color=C_ACCENT,
             ha="right")
    axA.axhline(0.0, color="#444444", lw=0.8)
    axA.set_xticks(np.arange(3))
    axA.set_xticklabels(lagnames)
    axA.set_ylabel("state autocorrelation")
    axA.set_title("Persistence against a within block permutation null",
                  loc="left", fontsize=8.8)
    axA.legend(loc="upper right", fontsize=6.6)
    axA.set_ylim(-0.05, 0.80)

    for i, (lbl, pos, tag, colr) in enumerate(SETS):
        obs, null, pval, z = rem_order(blocks_of(pos, tag))
        print(f"  {lbl}: REM order {obs:.1f}  p={pval:.5f}  z={z:.1f}")
        axB.hist(null, bins=28, bottom=i, color="#CCCCCC", zorder=2,
                 weights=np.full(len(null), 0.85 / max(np.histogram(null, bins=28)[0])))
        axB.plot([obs, obs], [i, i + 0.9], color=colr, lw=2.2, zorder=4)
        axB.text(obs + 0.6, i + 0.55,
                 f"{obs:.1f} percent\nz = {z:.1f}, p < {1 / len(null):.4f}\n"
                 f"raw labels: {load_features(pos, tag)['rem_from_nrem_pct']:.1f}",
                 fontsize=6.9, color=colr, va="center")
        axB.text(50.6, i + 0.05, lbl, fontsize=7.5, fontweight="bold")
    axB.set_yticks([])
    axB.set_xlim(50, 94)
    axB.set_xlabel("percent of REM episodes entered from NREM")
    axB.set_title("REM order against 2,000 run order permutations", loc="left",
                  fontsize=8.8)

    # impedance against yield, animals only: A2 holds no animal and cannot belong
    # in a correlation about animals
    duty = {r["name"].split()[0]: r["pct"] for r in rows if r["name"].endswith("EEG")}
    usable = {k: v["eeg_pct"] for k, v in D["usable"]["animals"].items()}
    pos_list = [p for p in usable if p != "A2"]
    xs = np.array([duty[p] for p in pos_list])
    ys = np.array([usable[p] for p in pos_list])
    rho = stats.spearmanr(xs, ys).statistic
    perm = np.array([stats.spearmanr(xs, rng.permutation(ys)).statistic
                     for _ in range(N_PERM)])
    p_exact = (1 + np.sum(np.abs(perm) >= abs(rho))) / (1 + N_PERM)
    print(f"  Spearman rho={rho:.2f} exact permutation p={p_exact:.3f} n={len(xs)}")
    for p_, x_, y_ in zip(pos_list, xs, ys):
        colr = C_WORK if y_ > 50 else C_FLOOR
        axC.scatter(x_, y_, color=colr, s=48, zorder=3)
        if y_ > 50:
            axC.annotate(p_, (x_, y_), textcoords="offset points",
                         xytext=(7, 5), fontsize=7.5)
    # the five failing channels sit on top of one another at the origin, so they
    # are named once rather than drawn as overlapping labels
    axC.annotate("A1, B2, C1, C2, D1\nall at or below 5 percent connected\n"
                 "and all producing nothing",
                 (float(np.median(xs[ys < 50])), 0.0), textcoords="offset points",
                 xytext=(14, 6), fontsize=6.8, color="#333333",
                 arrowprops=dict(arrowstyle="->", color="#777777", lw=0.8))
    axC.scatter(duty["A2"], usable["A2"], color="#111111", marker="x", s=48, zorder=3)
    axC.annotate("A2, no animal,\nexcluded from the test", (duty["A2"], usable["A2"]),
                 textcoords="offset points", xytext=(8, 8), fontsize=6.6)
    axC.set_xlabel("percent of impedance sweeps connected")
    axC.set_ylabel("percent of the recording that is usable")
    axC.set_title("Impedance against what was recorded", loc="left", fontsize=8.8)
    axC.text(2, 44, f"Spearman rho = {rho:.2f}\nexact permutation p = {p_exact:.3f}, "
                    f"n = {len(xs)}\nNOT significant.\n\n"
                    "D2 was connected in ONE sweep of 20\nand produced 87.9 percent usable EEG.",
             fontsize=6.9, color="#333333")
    axC.set_xlim(-4, 108)
    axC.set_ylim(-6, 112)
    fig.suptitle("Figure 9.  Statistics behind the sleep claims, and the limit of "
                 "impedance as a predictor", fontsize=10.5, fontweight="bold")
    caption(cap,
        "LEFT. Autocorrelation of the asleep indicator, pooled across unbroken blocks. Bars come from the stored "
        "hypnogram, whose labels have been through the 12 second minimum bout rule; black dashes are the HEADLINE "
        "values, computed on RAW labels before that rule, and the gap between them is itself a finding, because "
        "smoothing inflates this statistic by construction. Thick black bars are the 95 percent range of 300 within "
        "block permutations. NO CONFIDENCE INTERVAL IS QUOTED ON THE MAGNITUDE, deliberately: the best recording is a "
        "single unbroken block, so there is no independent replicate to resample and a block bootstrap interval would "
        "largely report the chunk length chosen. A block bootstrap was built during this rebuild, produced intervals "
        "that did not bracket their own point estimate, and was discarded rather than tuned. MIDDLE. Run order "
        "permuted 2,000 times within blocks, preserving run lengths and composition. RIGHT. Rank correlation between "
        "impedance duty cycle and usable fraction across the seven positions that hold an animal, with an EXACT "
        f"permutation p from {N_PERM:,} relabellings, because five of seven values are tied and the asymptotic p "
        f"value is not trustworthy there. Seed {SEED} throughout.")
    save(fig, "2026-08-09-fig09-sleep-statistics",
         alt=("Three panels. Left: persistence bars far above their permutation nulls, with headline raw label values "
              "marked lower than the plotted smoothed values. Middle: observed REM ordering far to the right of every "
              "permutation null. Right: scatter of impedance duty cycle against usable fraction showing no significant "
              "rank correlation across seven animals."),
         provenance={"raw_data": "pipeline hypnograms and features files; 6 August impedance census",
                     "transformations": "see caption",
                     "uncertainty": f"permutation nulls, {N_PERM} relabellings for the correlation",
                     "missing_data": "A2 excluded from the correlation, it holds no animal"})

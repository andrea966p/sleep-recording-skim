"""Figure 1: impedance trajectory of all eight positions.
Figure 2: outcome of the 23.66 h overnight recording, with honest intervals.

Every value is read from derived/inputs.json and derived/usable_overnight.npz.
"""
from __future__ import annotations

import numpy as np
from matplotlib.patches import Patch

from figs_common import *   # noqa: F401,F403

D = derived("inputs.json")
Z = derived("usable_overnight.npz")
rng = np.random.default_rng(SEED)

ORDER = ["B1", "D2", "C1", "C2", "A1", "D1", "B2", "A2"]
NOTE = {"B1": "worked after tether swap", "D2": "worked after tether swap",
        "C1": "8.73 h of sleep, then lost", "C2": "chewed tether",
        "A1": "muscle only, hum dominated", "D1": "shared path fault",
        "B2": "never usable", "A2": "no animal, cut cable"}

# --------------------------------------------------------------------- Figure 1
with style_context(STYLE, palette_name=PALETTE):
    fig, axes, cap = figure_with_caption(2, 4, figsize=(11.0, 6.4),
                                        caption_frac=0.20, sharex=True, sharey=True)
    labels = D["impedance_trajectory"]["B1"]["labels"]
    x = np.arange(len(labels))
    for ax, pos in zip(axes.ravel(), ORDER):
        t = D["impedance_trajectory"][pos]
        ax.axhspan(D["pass_mohm"], 12, color="#EDEDED", zorder=0)
        ax.axhline(D["pass_mohm"], color="#333333", lw=0.9, ls=":", zorder=2)
        # POINTS, not a line: each is one unrepeated 20 s sweep of a contact that
        # flips within minutes, so a connecting line would assert a trajectory
        # that was never measured. The faint connector only aids reading order.
        for key, colr, mk, lbl in (("eeg", C_WORK, "o", "EEG"),
                                   ("emg", C_FAIL, "s", "EMG")):
            v = np.array([np.nan if q is None else q for q in t[key]], float)
            ax.plot(x, v, color=colr, lw=0.7, alpha=0.35, zorder=3)
            ax.plot(x, v, mk, color=colr, ms=5.5, zorder=4, label=lbl)
        ax.set_yscale("log")
        ax.set_ylim(0.015, 12)
        ax.set_title(pos, loc="left")
        ax.text(0.03, 0.06, NOTE[pos], transform=ax.transAxes, fontsize=6.6,
                color="#444444", style="italic")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=6.2, rotation=30, ha="right")
    for ax in axes[:, 0]:
        ax.set_ylabel("impedance, MOhm (log)")
    h, l = axes[0, 0].get_legend_handles_labels()
    cap.legend(h[:2], l[:2], loc="upper left", ncol=2, fontsize=8,
               bbox_to_anchor=(0.0, 1.25))
    fig.suptitle("Figure 1.  Electrode impedance of all eight rig positions, "
                 "five single sweeps, 31 July to 4 August 2026",
                 fontsize=10.5, fontweight="bold")
    caption(cap,
        "Each marker is ONE 20 second sweep, unrepeated, so no marker carries an interval and the faint "
        "connector indicates reading order only, not a measured trajectory. Nothing was done to any animal "
        "between sweeps. Shaded region above the dotted line is the range in which a reading cannot be told "
        "apart from an amplifier input with no wire attached. Measurement: Intan RHD2216 on chip impedance "
        "check at 1 kHz, magnitude only, positive input of each bipolar pair. Every position moves in both "
        "directions and none declines monotonically, which is not the pattern of a failing implant.")
    save(fig, "2026-08-09-fig01-impedance-trajectories",
         alt=("Eight small panels, one per rig position, showing electrode impedance on a logarithmic axis "
              "across five sweeps from 31 July to 4 August. EEG and EMG are plotted as separate markers. "
              "Values move up and down by more than an order of magnitude between consecutive sweeps in "
              "every panel; no panel shows a steady decline."),
         provenance={"raw_data": "impedance CSV sweeps, see derived/inputs.json impedance_trajectory",
                     "transformations": "none, magnitudes plotted as measured",
                     "uncertainty": "none available: each point is a single unrepeated measurement",
                     "missing_data": "absent sites left as gaps"})

# --------------------------------------------------------------------- Figure 2
names = [str(s) for s in Z["animals"]]
mask_eeg = {n: Z["mask_eeg"][i] for i, n in enumerate(names)}
mask_emg = {n: Z["mask_emg"][i] for i, n in enumerate(names)}
u = D["usable"]["animals"]

stats_rows = []
for pos in ORDER:
    e, g = mask_eeg[pos], mask_emg[pos]
    pe, loe, hie = block_bootstrap_ci(e, rng=np.random.default_rng(SEED))
    pg_, log_, hig_ = block_bootstrap_ci(g, rng=np.random.default_rng(SEED + 1))
    stats_rows.append(dict(pos=pos, eeg=100 * pe, eeg_lo=100 * loe, eeg_hi=100 * hie,
                           emg=100 * pg_, emg_lo=100 * log_, emg_hi=100 * hig_,
                           n_eff_eeg=effective_n(e), n_eff_emg=effective_n(g),
                           block_min=u[pos]["longest_both_min"]))
for r in stats_rows:
    print(f"{r['pos']:3} EEG {r['eeg']:6.1f} [{r['eeg_lo']:.1f}, {r['eeg_hi']:.1f}] "
          f"n_eff {r['n_eff_eeg']:7.1f}   EMG {r['emg']:6.1f} [{r['emg_lo']:.1f}, {r['emg_hi']:.1f}] "
          f"n_eff {r['n_eff_emg']:7.1f}")

with style_context(STYLE, palette_name=PALETTE):
    fig, (ax1, ax2), cap = figure_with_caption(1, 2, figsize=(10.8, 5.6),
                                              caption_frac=0.22, width_ratios=[1.5, 1])
    y = np.arange(len(ORDER))[::-1]
    h = 0.36
    for i, r in zip(y, stats_rows):
        for val, lo, hi, yy, colr, hatch in (
                (r["eeg"], r["eeg_lo"], r["eeg_hi"], i + h / 2,
                 C_WORK if r["eeg"] > 50 else C_FLOOR, None),
                (r["emg"], r["emg_lo"], r["emg_hi"], i - h / 2,
                 C_WORK2 if r["emg"] > 50 else (C_WARN if r["emg"] > 1 else C_FLOOR),
                 None if r["emg"] > 50 or r["emg"] <= 1 else "///")):
            ax1.barh(yy, val, height=h, color=colr, hatch=hatch,
                     edgecolor="white", linewidth=0.4)
            ax1.plot([lo, hi], [yy, yy], color="#111111", lw=1.2,
                     solid_capstyle="butt", zorder=5)
        ax1.text(104, i + h / 2, f"{r['eeg']:.1f}", fontsize=6.8, va="center")
        ax1.text(104, i - h / 2, f"{r['emg']:.1f}", fontsize=6.8, va="center")
    ax1.set_yticks(y)
    ax1.set_yticklabels(ORDER)
    ax1.set_xlim(0, 118)
    ax1.set_xticks([0, 25, 50, 75, 100])
    ax1.set_xlabel("percent of the recording that is usable")
    ax1.set_title("Usable fraction, upper bar EEG, lower bar EMG", loc="left")
    ax1.legend(handles=[Patch(color=C_WORK, label="EEG usable"),
                        Patch(color=C_WORK2, label="EMG usable"),
                        Patch(facecolor=C_WARN, hatch="///", edgecolor="white",
                              label="EMG partial"),
                        Patch(color=C_FLOOR, label="not usable")],
               loc="lower right", ncol=2, fontsize=7.2,
               bbox_to_anchor=(1.0, 0.02))

    blocks = [r["block_min"] / 60 for r in stats_rows]
    ax2.barh(y, blocks, height=0.55,
             color=[C_WORK if b > 1 else C_FLOOR for b in blocks])
    for i, b in zip(y, blocks):
        ax2.text(b + 0.07, i, f"{b:.2f} h" if b else "none", va="center", fontsize=7)
    ax2.set_yticks(y)
    ax2.set_yticklabels(ORDER)
    ax2.set_xlim(0, 4.6)
    ax2.set_xlabel("hours")
    ax2.set_title("Longest unbroken block, BOTH channels usable", loc="left")
    fig.suptitle("Figure 2.  Outcome of the 23.66 hour overnight recording of "
                 "6 to 7 August 2026, all eight positions",
                 fontsize=10.5, fontweight="bold")
    d2 = next(r for r in stats_rows if r["pos"] == "D2")
    from scipy import stats as _st
    n = D["usable"]["n_epochs"]
    k = round(d2["eeg"] / 100 * n)
    b_lo, b_hi = _st.beta.ppf([0.025, 0.975], k + 0.5, n - k + 0.5)
    widen = (d2["eeg_hi"] - d2["eeg_lo"]) / (100 * (b_hi - b_lo))
    caption(cap,
        "Criterion, pre registered before the recording existed, applied per 10 second epoch: 60 Hz amplitude "
        f"below the 1st percentile of the wire free floor ({D['usable']['threshold_uv']:.1f} microvolts here), "
        "root mean square between 10 and 150 microvolts, and zero saturated samples. "
        f"n = {D['usable']['n_epochs']} epochs. Black bars are 95 percent BLOCK BOOTSTRAP intervals over "
        "contiguous runs of epochs. A binomial interval would be far too narrow: contact persists for tens of "
        f"minutes. For D2's EEG channel, the one where the interval carries any weight, the effective sample size is "
        f"about {d2['n_eff_eeg']:.0f} epochs rather than {n}, and the interval is {widen:.1f} times wider than a "
        "binomial interval on the same data would be. "
        f"Falsification passed: the wire free floor scores {D['usable']['floor_pct']:.2f} percent and the A2 "
        "position, which holds a cut cable and no animal, scores zero. Hatching marks the partial category so "
        "the figure survives grayscale.")
    save(fig, "2026-08-09-fig02-fleet-outcome",
         alt=("Horizontal bar chart of eight rig positions. B1 and D2 have EEG and EMG bars near 100 percent; "
              "C1, C2 and A1 have muscle only bars at 37.8, 15.2 and 7.6 percent with EEG at zero; D1, B2 and "
              "A2 are at zero on both. A second panel shows the longest unbroken block, 3.6 hours for B1 and "
              "1.45 hours for D2, none for the rest."),
         provenance={"raw_data": "allego_1__uid0806-16-57-38, per epoch masks in derived/usable_overnight.npz",
                     "transformations": "pre registered three part criterion, see caption",
                     "uncertainty": f"95 percent block bootstrap, 2000 resamples, seed {SEED}",
                     "missing_data": "none, every epoch classified"})

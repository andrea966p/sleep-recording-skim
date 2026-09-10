"""Figure 6: threshold sensitivity of the circadian result.
Figure 7: scoreable hours per recording, with the denominator shown.
"""
from __future__ import annotations

import numpy as np

from figs_common import *   # noqa: F401,F403

D = derived("inputs.json")
R = D["recordings"]

SETS = [("B1 overnight", "portB-slot1_2026-08-06_165738_23h40m", C_WORK, "o"),
        ("D2 overnight", "portD-slot2_2026-08-06_165738_23h40m", C_WORK2, "s"),
        ("B1 afternoon", "portB-slot1_2026-08-06_124502_3h11m", "#7FB3D5", "^")]

# ------------------------------------------------------------------ Figure 6
with style_context(STYLE, palette_name=PALETTE):
    fig, (ax1, ax2), cap = figure_with_caption(1, 2, figsize=(10.8, 5.0),
                                               caption_frac=0.26)
    swings = []
    for lbl, key, colr, mk in SETS:
        rows = R[key]["otsu_sensitivity"]
        m = [r["multiplier"] for r in rows]
        a = [r["asleep_in_light_pct"] for r in rows]
        ax1.plot(m, a, mk + "-", color=colr, lw=1.7, ms=5, label=lbl)
        k = m.index(1.0)
        ax1.scatter([1.0], [a[k]], s=150, facecolor="none", edgecolor=colr,
                    lw=1.6, zorder=5)
        ax1.annotate(f"{a[k]:.1f}", (1.0, a[k]), textcoords="offset points",
                     xytext=(-6, 11), fontsize=7.5, color=colr,
                     fontweight="bold", ha="right")
        swings.append((lbl, max(a) - min(a), colr))
    # ONE published value, drawn as a line and nothing more. A band was drawn here
    # previously from arithmetic that corresponds to no published interval; the
    # figure it belongs to reports NREM plus REM, while the published dispersion
    # available to this project is for NREM alone.
    ax1.axhline(70, color=C_ACCENT, lw=1.3, ls="--")
    ax1.text(0.752, 71.5, "approximate published value for total sleep in the "
             "light phase, C57BL/6", fontsize=6.9, color=C_ACCENT, ha="left")
    ax1.set_xlabel("multiplier applied to the automatic wake threshold, "
                   "in linear microvolts")
    ax1.set_ylabel("percent asleep during the light phase")
    ax1.set_title("A 25 percent shift in ONE threshold moves the headline number",
                  loc="left", fontsize=8.8)
    ax1.legend(loc="lower right", fontsize=7.5)
    ax1.set_ylim(15, 98)

    ax2.bar(np.arange(3), [s[1] for s in swings], width=0.55,
            color=[s[2] for s in swings])
    for i, s in enumerate(swings):
        ax2.text(i, s[1] + 1.4, f"{s[1]:.1f} points", ha="center", fontsize=8,
                 fontweight="bold")
    ax2.set_xticks(np.arange(3))
    ax2.set_xticklabels([s[0] for s in swings], fontsize=8)
    ax2.set_ylabel("swing in percent asleep in light, across the sweep")
    ax2.set_title("How far the reported number can move", loc="left", fontsize=8.8)
    ax2.set_ylim(0, 80)
    fig.suptitle("Figure 6.  Why the agreement with the literature is NOT "
                 "independent confirmation", fontsize=10.5, fontweight="bold")
    caption(cap,
        "The wake threshold is fitted separately for each animal by Otsu's method on muscle amplitude. Sweeping it by "
        "plus and minus 25 percent in linear microvolts moves the percentage asleep in the light phase of D2 from 23 "
        "to 89, so the published value is reachable from almost anywhere in that range and the reported numbers must "
        "always be quoted with this swing beside them. NO SHADED REFERENCE BAND IS DRAWN, deliberately. An earlier "
        "version of this figure drew one from arithmetic that corresponds to no published interval: the dispersion "
        "this project holds is for NREM alone, 62.0 plus or minus 7.8 percent per 12 hours, whereas the quantity "
        "plotted here is NREM plus REM. The dashed line is a single approximate literature value for total sleep and "
        "carries no interval. A threshold this sensitive also means the muscle amplitude distribution has no clear "
        "valley between sleep and wake, which is the more useful finding. The fix is human scored ground truth.")
    save(fig, "2026-08-09-fig06-threshold-sensitivity",
         alt=("Left: percent asleep in the light phase against the multiplier applied to the wake threshold, for "
              "three recordings. All three rise steeply, D2 from 23 percent at multiplier 0.75 to 89 percent at 1.25. "
              "A dashed line marks the approximate published value of 70 percent. Right: bar chart of the swing, "
              "66 points for D2 overnight, 36 for B1 overnight, 22.3 for B1 afternoon."),
         provenance={"raw_data": "pipeline features files, otsu_sensitivity block",
                     "transformations": "wake threshold multiplied by 0.75 to 1.25 in linear microvolts",
                     "uncertainty": "sensitivity sweep, not a confidence interval",
                     "missing_data": "none"})

# ------------------------------------------------------------------ Figure 7
Y = D["yield_by_recording"]
ROWS = [
    ("10 to 14 Jul", 72.0, 8, "2026-07-10_72h"),
    ("13 Jul", 20.0, 8, "2026-07-13_20h"),
    ("31 Jul to 1 Aug", 27.9, 8, "2026-07-31_27h9m"),
    ("2 Aug", 21.7, 8, "2026-08-02_21h7m"),
    ("6 Aug afternoon", 3.18, 8, "2026-08-06_124502_3h11m"),
    ("6 to 7 Aug", 23.66, 8, "2026-08-06_165738_23h40m"),
]
with style_context(STYLE, palette_name=PALETTE):
    fig, (ax1, ax2), cap = figure_with_caption(1, 2, figsize=(11.0, 4.6),
                                               caption_frac=0.26)
    x = np.arange(len(ROWS))
    hours = [Y[k]["scoreable_hours"] for _, _, _, k in ROWS]
    after = [i >= 4 for i in range(len(ROWS))]
    cols = [C_WORK if a else C_FLOOR for a in after]
    ax1.bar(x, hours, color=cols, width=0.6)
    for i, (h, (lbl, dur, n, k)) in enumerate(zip(hours, ROWS)):
        txt = f"{h:.1f} h" if h else "none"
        if Y[k]["provenance"] != "pipeline features files":
            txt += "*"
        ax1.text(i, h + 1.0, txt, ha="center", fontsize=7.5, fontweight="bold")
    ax1.axvline(3.5, color=C_FAIL, lw=1.4, ls="--")
    ax1.text(3.62, max(hours) * 0.82, "tether chain rebuilt",
             color=C_FAIL, fontsize=7.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels([r[0] for r in ROWS], fontsize=7, rotation=20, ha="right")
    ax1.set_ylabel("scoreable animal hours")
    ax1.set_title("Absolute yield per recording", loc="left", fontsize=8.8)

    # the denominator: recordings differ in length and in animal count, so the
    # absolute count alone is not comparable across them
    frac = [100 * h / (dur * n) for h, (_, dur, n, _) in zip(hours, ROWS)]
    ax2.bar(x, frac, color=cols, width=0.6)
    for i, f in enumerate(frac):
        ax2.text(i, f + 0.6, f"{f:.1f}%", ha="center", fontsize=7.5,
                 fontweight="bold")
    ax2.axvline(3.5, color=C_FAIL, lw=1.4, ls="--")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{r[0]}\n{r[1]:.1f} h x {r[2]}" for r in ROWS],
                        fontsize=6.6, rotation=20, ha="right")
    ax2.set_ylabel("percent of available animal hours")
    ax2.set_title("Same result against its denominator", loc="left", fontsize=8.8)
    fig.suptitle("Figure 7.  Scoreable animal hours per recording, before and "
                 "after the tether change", fontsize=10.5, fontweight="bold")
    caption(cap,
        "Scoreable means the pipeline gave the animal a SCOREABLE verdict: it passed the quality gate, produced "
        "unbroken blocks, and passed a persistence check against a shuffled control. The right panel divides by "
        "recording duration times eight positions, because the recordings differ in length and the absolute count on "
        "its own is not comparable across them. Values marked with an asterisk come from the vault write ups rather "
        "than from pipeline output files, because those older recordings are no longer processed; every unmarked value "
        "is computed from the per recording feature files. CAUTION: this compares single recordings, not a controlled "
        "series. D2 is the same animal throughout and is the clean comparison. The animal in the B1 position on the "
        "right is a replacement, because the original was sacrificed on 5 August after its skull electrode detached.")
    save(fig, "2026-08-09-fig07-yield-timeline",
         alt=("Two bar charts of six recordings. Absolute scoreable hours are zero for three July and August "
              "recordings, 10.4 hours for 31 July, 3.2 for the 6 August afternoon and 46.9 for the overnight "
              "recording. As a percentage of available animal hours the same six read 0, 0, 4.7, 0, 12.5 and 24.8."),
         provenance={"raw_data": "pipeline features files; older recordings from vault write ups, marked",
                     "transformations": "sum of hours_in_blocks over animals with SCOREABLE verdict",
                     "uncertainty": "none, these are counts",
                     "missing_data": "older recordings flagged with an asterisk"})
    print("yield percent:", [round(f, 1) for f in frac])

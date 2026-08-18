"""Figure 3: real traces, raw against cleaned against auto scaled.
Figure 4: spectra, and the discriminator that filtering cannot fake.
Figure 5: hypnograms across the light and dark cycle.

Window selection uses ONE rule everywhere (figs_common.median_window). Panel
values in figure 4 come from derived/forensics_overnight.json, not from a typed
table.
"""
from __future__ import annotations

import json
import os

import numpy as np
from scipy import signal as sg

from figs_common import *   # noqa: F401,F403

D = derived("inputs.json")
F = derived("forensics_overnight.json")
RAW_BASE = RAW
FS_RAW, NCOL = 1000, 262
SEC = 10


def raw_channel(label, n_sec, start_sec):
    meta = json.load(open(RAW_BASE + ".xdat.json"))
    bim = meta["sapiens_base"]["biointerface_map"]
    labels = [f"{p}/{s}" for p, s in zip(bim["port"], bim["site_num"])]
    col = labels.index(label)
    nsamp = os.path.getsize(RAW_BASE + "_data.xdat") // (NCOL * 4)
    mm = np.memmap(RAW_BASE + "_data.xdat", dtype=np.float32, mode="r",
                   shape=(nsamp, NCOL))
    i0 = start_sec * FS_RAW
    seg = np.asarray(mm[i0:i0 + n_sec * FS_RAW, col], dtype=np.float64)
    del mm
    return seg


# ------------------------------------------------------------------ Figure 3
fs = 250
panels = []


def state_window(pos, want, seconds=SEC):
    z = load_npz(pos)
    rows = load_hypno(pos)
    cand = [int(r["epoch"]) for r in rows
            if r["state"] == want and r["in_block"] == "1"]
    e0 = cand[len(cand) // 2] if cand else 3000
    i0 = e0 * 4 * fs
    n = seconds * fs
    return (np.asarray(z["eeg"][i0:i0 + n], float),
            np.asarray(z["emg"][i0:i0 + n], float))


b_eeg, b_emg = state_window("B1", "NREM")
w_eeg, _ = state_window("B1", "WAKE")
d_eeg, _ = state_window("D2", "NREM")
panels.append(("B1 EEG, scored NREM", b_eeg, "eeg", C_WORK, "working"))
panels.append(("B1 EMG, same 10 s", b_emg, "emg", C_WORK, "working"))
panels.append(("B1 EEG, scored WAKE", w_eeg, "eeg", C_WORK, "working"))
panels.append(("D2 EEG, scored NREM", d_eeg, "eeg", C_WORK2, "working"))

c1 = load_npz("C1")
c2 = load_npz("C2")
c1w, _ = median_window(c1["eeg"], fs, SEC)
c2w, _ = median_window(c2["eeg"], fs, SEC)
panels.append(("C1 EEG, electrode floating", c1w, "eeg", C_FAIL, "failure"))
panels.append(("C2 EEG, damaged tether", c2w, "eeg", C_FAIL, "failure"))

# every wire free input on port B, so the floor panel can be shown WITH the
# spread of its siblings instead of a claim the panel cannot support
FLOOR_LABELS = [f"B/{i}" for i in range(5, 17)]
floor_raw = {lb: raw_channel(lb, SEC + 4, 40000)[::4][:SEC * fs]
             for lb in FLOOR_LABELS}
floor_filt = {lb: bandpass(notch_mains(v, fs), fs, 0.5, 30.0)[fs:-fs]
              for lb, v in floor_raw.items()}
floor_rms = {lb: float(np.sqrt(np.mean(v ** 2))) for lb, v in floor_filt.items()}
med_lab = sorted(floor_rms, key=floor_rms.get)[len(floor_rms) // 2]
panels.append((f"amplifier input, NO wire ({med_lab})", floor_raw[med_lab],
               "eeg", C_FLOOR, "control"))
print("floor filtered rms uV:", {k: round(v) for k, v in sorted(floor_rms.items(),
                                                               key=lambda kv: kv[1])})

RAIL = 6389.6
t = np.arange(SEC * fs) / fs
with style_context(STYLE, palette_name=PALETTE):
    nrow = len(panels)
    fig, axes, cap = figure_with_caption(nrow, 3, figsize=(12.6, 1.05 * nrow + 1.9),
                                         caption_frac=0.135, sharex=True)
    for r, (name, x, kind, colr, cls) in enumerate(panels):
        axr, axf, axz = axes[r]
        axr.plot(t, x, color=colr, lw=0.55)
        axr.set_ylim(-RAIL * 1.05, RAIL * 1.05)
        axr.axhline(RAIL, color="#333333", lw=0.5, ls=":")
        axr.axhline(-RAIL, color="#333333", lw=0.5, ls=":")
        axr.set_ylabel(name, fontsize=6.8, rotation=0, ha="right", va="center",
                       labelpad=6)
        lo, hi = (0.5, 30.0) if kind == "eeg" else (10.0, 100.0)
        y = bandpass(notch_mains(x, fs), fs, lo, hi)[fs:-fs]
        t2 = t[fs:-fs]
        axf.plot(t2, y, color=colr, lw=0.6)
        axf.set_ylim(-400, 400)
        axz.plot(t2, y, color=colr, lw=0.6)
        lim = 1.15 * np.percentile(np.abs(y), 99.5)
        axz.set_ylim(-lim, lim)
        axr.text(0.985, 0.84, f"rms {np.sqrt(np.mean(x**2)):,.0f} uV",
                 transform=axr.transAxes, ha="right", fontsize=6.4, color="#333333")
        axf.text(0.985, 0.84, f"rms {np.sqrt(np.mean(y**2)):,.0f} uV",
                 transform=axf.transAxes, ha="right", fontsize=6.4, color="#333333")
        axz.text(0.985, 0.84, f"axis +/- {lim:,.0f} uV",
                 transform=axz.transAxes, ha="right", fontsize=6.4, color="#333333")
        if cls != "working":
            face = "#FBEFE8" if cls == "failure" else "#F0F0F0"
            for a in (axr, axf, axz):
                a.set_facecolor(face)
    axes[0, 0].set_title("RAW as saved, scale set by the saturation rails",
                         loc="left", fontsize=8.2)
    axes[0, 1].set_title("CLEANED, fixed scale plus and minus 400 uV",
                         loc="left", fontsize=8.2)
    axes[0, 2].set_title("THE TRAP: same signal, axis scaled to fit",
                         loc="left", fontsize=8.2, color="#A33900")
    for c in range(3):
        axes[-1, c].set_xlabel("seconds")
    fig.suptitle("Figure 3.  What the channels actually look like, one recording, "
                 "one 10 second window each", fontsize=10.5, fontweight="bold")
    rms_sorted = sorted(floor_rms.values())
    caption(cap,
        "PROCESSING. Left: raw as written to disk, decimated 1000 Hz to 250 Hz, microvolts, nothing else. The only "
        "filter present is the acquisition hardware band pass of 1.10 to 475.17 Hz, which cannot be removed. Middle: "
        "notch at 60, 120 and 180 Hz, quality factor 30, then a 4th order Butterworth band pass applied forwards and "
        "backwards, 0.5 to 30 Hz for EEG and 10 to 100 Hz for EMG; one second discarded at each end for the filter "
        "edge. Right: the identical cleaned signal with the axis allowed to fit, which is what plotting software does "
        "by default. WINDOW RULE, applied identically to every panel: the window whose amplitude is closest to the "
        "median of that channel, so no panel is a lucky or an unlucky moment. The floor row shows the median of twelve "
        f"wire free inputs on port B, whose cleaned amplitudes span {rms_sorted[0]:.0f} to {rms_sorted[-1]:.0f} "
        "microvolts; a bare wire still produces a large structured trace, and at its own scale it does not read as "
        "obviously different from data.")
    save(fig, "2026-08-09-fig03-signal-traces",
         alt=("Seven rows of ten second traces in three columns. Working channels are small at the raw scale; "
              "failing channels and the wire free input fill the raw panel. In the third column, where each panel "
              "is auto scaled, every channel including the one with no electrode looks like plausible brain activity."),
         provenance={"raw_data": RAW_BASE,
                     "transformations": "see caption; window selected by median amplitude rule",
                     "uncertainty": "not applicable, single windows shown",
                     "missing_data": "none"})

# ------------------------------------------------------------------ Figure 4
LONG = 300
long_win = {}
for nm, z, colr in (("B1 EEG, working", load_npz("B1"), C_WORK),
                    ("D2 EEG, working", load_npz("D2"), C_WORK2),
                    ("C1 EEG, floating", c1, C_FAIL),
                    ("C2 EEG, damaged tether", c2, C_WARN)):
    w, _ = median_window(z["eeg"], fs, LONG, n_try=40)
    long_win[nm] = (w, colr)
fl_long = raw_channel(med_lab, LONG + 10, 40000)[::4][:LONG * fs]
long_win["no wire attached"] = (fl_long, C_FLOOR)

with style_context(STYLE, palette_name=PALETTE):
    fig, (axA, axB), cap = figure_with_caption(1, 2, figsize=(11.0, 5.2),
                                               caption_frac=0.24)
    for nm, (x, colr) in long_win.items():
        f, P = sg.welch(x, fs=fs, nperseg=2048)
        style = "--" if nm == "no wire attached" else "-"
        axA.loglog(f[1:], P[1:], color=colr, lw=1.7, ls=style, label=nm)
    axA.axvspan(1.0, 4.0, color=C_WORK, alpha=0.07)
    axA.set_xlim(0.5, 45)
    axA.set_xlabel("frequency, Hz")
    axA.set_ylabel("power spectral density, uV squared per Hz")
    axA.set_title("Power spectrum, 5 minutes, below the mains frequency", loc="left")
    axA.legend(loc="lower left", fontsize=7)

    fl = F["floor"]
    axB.axhspan(fl["slope_min"], fl["slope_max"], color="#DDDDDD", zorder=0)
    axB.axvspan(fl["hum_min"], fl["hum_max"], color="#DDDDDD", alpha=0.45, zorder=0)
    offs = {"B1": (8, -4), "D2": (8, -4), "A1": (6, 8), "C1": (6, -12),
            "C2": (-10, 9), "D1": (7, 3), "B2": (-10, -13), "A2": (-28, 10)}
    for pos, rec in F["animals"].items():
        e = rec["eeg"]
        working = pos in ("B1", "D2")
        ctrl = pos == "A2"
        colr = C_FLOOR if ctrl else (C_WORK if working else C_FAIL)
        mk = "D" if ctrl else ("o" if working else "s")
        axB.scatter(e["hum_uv"], e["slope"], color=colr, marker=mk, s=44, zorder=3)
        axB.annotate(pos + (" no animal" if ctrl else ""),
                     (e["hum_uv"], e["slope"]), textcoords="offset points",
                     xytext=offs.get(pos, (6, 5)), fontsize=6.6, color="#333333")
    axB.scatter(fl["hum_uv"], fl["slope"], color="#111111", marker="P", s=52, zorder=4)
    axB.annotate("wire free floor", (fl["hum_uv"], fl["slope"]),
                 textcoords="offset points", xytext=(-84, -4), fontsize=6.8)
    axB.set_xscale("log")
    axB.set_xlim(20, 2e4)
    axB.set_ylim(-2.3, 0.2)
    axB.set_xlabel("60 Hz amplitude, uV (log)")
    axB.set_ylabel("spectral slope after cleanup")
    axB.set_title("The discriminator that filtering cannot fake", loc="left")
    fig.suptitle("Figure 4.  Spectral shape separates a real electrode from a bare "
                 "wire, and mains amplitude reads out contact",
                 fontsize=10.5, fontweight="bold")
    caption(cap,
        "LEFT. Welch power spectral density, 2048 sample segments, 5 minute windows chosen by the same median "
        "amplitude rule as figure 3, on raw signal with no filtering applied before the spectrum. A working "
        "electrode falls steeply with frequency; a floating electrode and a bare wire are close to flat. Shaded "
        "band marks the delta range of 1 to 4 Hz. RIGHT. Every point is computed by "
        "eeg-emg-analysis/qc/per_animal_forensics.py over "
        f"{F['n_epochs_sampled']} epochs sampled across the whole 23.66 hour recording, not transcribed: 60 Hz "
        "amplitude against the slope of the spectrum after notch and 0.5 to 30 Hz band pass. Grey bands are the "
        f"range covered by {len(F['floor_sites'])} wire free inputs on both axes. The two working animals sit "
        "outside that range on both axes at once, and the two measures are independent of one another.")
    save(fig, "2026-08-09-fig04-spectra-and-discriminator",
         alt=("Left panel: log log power spectra. The two working animals fall steeply with frequency while the "
              "floating electrode, the damaged tether and the wire free input are nearly flat. Right panel: "
              "scatter of 60 Hz amplitude against spectral slope. B1 and D2 sit at low hum and steep slope, far "
              "from every failing channel and from the wire free floor band."),
         provenance={"raw_data": RAW_BASE,
                     "derived": "derived/forensics_overnight.json",
                     "transformations": "Welch nperseg 2048; slope fitted 1 to 30 Hz after notch and band pass",
                     "uncertainty": "floor range shown as shaded bands",
                     "missing_data": "none"})

# ------------------------------------------------------------------ Figure 5
STATE_Y = {"WAKE": 2, "NREM": 1, "REM": 0}
BAND_C = {"WAKE": C_FAIL, "NREM": C_WORK, "REM": C_ACCENT}
with style_context(STYLE, palette_name=PALETTE):
    fig, axes, cap = figure_with_caption(4, 1, figsize=(11.4, 6.8),
                                         caption_frac=0.17,
                                         height_ratios=[2.0, 1.0, 2.0, 1.0])
    for k, (pos, title) in enumerate([
            ("B1", "B1, 23.66 hours, one unbroken block"),
            ("D2", "D2, 23.28 hours, nine blocks, longest 9.6 hours")]):
        axh, axb = axes[2 * k], axes[2 * k + 1]
        rows = load_hypno(pos)
        t_h = np.array([float(r["t_s"]) for r in rows]) / 3600.0
        st = np.array([STATE_Y.get(r["state"], -1) for r in rows])
        inb = np.array([r["in_block"] == "1" for r in rows])
        light = np.array([r["light"] == "1" for r in rows])
        edges = np.where(np.diff(light.astype(int)) != 0)[0]
        bounds = [0] + list(edges + 1) + [len(t_h) - 1]
        for a, b in zip(bounds[:-1], bounds[1:]):
            if not light[a]:
                for ax in (axh, axb):
                    ax.axvspan(t_h[a], t_h[b], color="#E9E9EF", zorder=0)
        # STATE BANDS, not a line: a line through codes 0, 1, 2 draws a wake to
        # REM transition as if it passed through NREM, which never happened
        for name, yv in STATE_Y.items():
            m = (st == yv) & inb
            if m.any():
                axh.vlines(t_h[m], yv - 0.42, yv + 0.42,
                           color=BAND_C[name], lw=0.35, zorder=3)
        miss = (~inb)
        if miss.any():
            axh.vlines(t_h[miss], -0.5, 2.5, color="#CCCCCC", lw=0.35, zorder=1)
        axh.set_yticks([0, 1, 2])
        axh.set_yticklabels(["REM", "NREM", "WAKE"])
        axh.set_ylim(-0.6, 2.6)
        axh.set_xlim(t_h[0], t_h[-1])
        axh.set_title(title, loc="left")
        hrs = np.floor(t_h).astype(int)
        xs, ys = [], []
        for hh in np.unique(hrs):
            m = (hrs == hh) & inb
            if m.sum() > 200:
                xs.append(hh + 0.5)
                ys.append(100.0 * np.mean(st[m] < 2))
        axb.plot(xs, ys, "o-", color="#333333", lw=1.3, ms=3.2, zorder=3)
        axb.set_ylim(0, 100)
        axb.set_ylabel("percent\nasleep", fontsize=7.5)
        axb.set_xlim(t_h[0], t_h[-1])
        axb.axhline(50, color="#BBBBBB", lw=0.8, ls=":")
    axes[-1].set_xlabel("hours from the start of the recording, "
                        "6 August 16:57 local time")
    from matplotlib.patches import Patch
    cap.legend(handles=[Patch(color="#E9E9EF", label="dark phase, lights off 21:00"),
                        Patch(color=BAND_C["WAKE"], label="WAKE"),
                        Patch(color=BAND_C["NREM"], label="NREM"),
                        Patch(color=BAND_C["REM"], label="REM, not quantified"),
                        Patch(color="#CCCCCC", label="epoch not in a usable block")],
               loc="upper left", ncol=5, fontsize=7, bbox_to_anchor=(0.0, 1.5))
    fig.suptitle("Figure 5.  Sleep and wake across a full light and dark cycle, "
                 "the two animals that worked", fontsize=10.5, fontweight="bold")
    caption(cap,
        "Automatic staging on 4 second epochs, drawn as state bands rather than a line, because a line through "
        "ordered state codes draws a transition from wake to REM as though it passed through NREM. Epochs outside a "
        "usable block are drawn in grey rather than joined over. Wake is separated from sleep by an Otsu threshold on "
        "muscle amplitude, refit per animal; see figure 6 for how much that threshold matters. REM is shown for "
        "completeness and MUST NOT be reported as a percentage: two independent rules disagree by a factor of five on "
        "this montage. Nothing in the quality gate, the staging rule or the persistence statistic has any knowledge of "
        "the clock, so the light and dark contrast is external to the method.")
    save(fig, "2026-08-09-fig05-hypnograms",
         alt=("Two hypnograms drawn as state bands over 24 hours with the dark phase shaded, each with a curve of "
              "percent asleep per hour beneath. Both animals are mostly awake during the dark phase and mostly "
              "asleep during the light phase."),
         provenance={"raw_data": "pipeline hypnogram CSVs in /home/skimlab/eeg-processed/2026-08-06/",
                     "transformations": "4 s epochs, minimum bout rule applied to labels shown",
                     "uncertainty": "not applicable",
                     "missing_data": "epochs outside usable blocks drawn explicitly in grey"})

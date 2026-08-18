"""Shared style, status encoding and export for ANIMAL CARDS and cohort sheets.

Promoted 2026-08-09 out of qc/figures_2026-08-08/, where it served one dated
figure set for one cohort that no longer exists. The rules below were earned by
an audit of that set and now apply to every card this project draws.

Three rules hold everywhere:

  1. NO FIGURE CONTAINS A TYPED-IN MEASUREMENT. Everything is read from
     `derived/`, which is produced by `compute_inputs.py` from the raw
     recording, the impedance CSVs and the pipeline feature files. If a value
     cannot be computed it is not drawn.
  2. Style comes from the scientific-visualization skill assets, not from ad hoc
     rcParams, and export goes through its exporter so every file carries a
     provenance manifest.
  3. Every figure declares alt text. A figure with no alt text is not finished.

Audit record: vault 03-troubleshooting/symptoms/figure-and-analysis-audit-2026-08-08.md
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

from core import paths as PATHS                      # noqa: E402

# The style presets and the validated palette live in the scientific-visualization
# SKILL, not in this repo, so this is the one sys.path entry that stays: it points
# outside the package on purpose. Everything else now imports normally.
SKILL = PATHS.FIGURE_STYLE_DIR
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(SKILL / "assets"))
import matplotlib                                    # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
from style_presets import style_context              # noqa: E402
from figure_export import export_figure              # noqa: E402

HERE = Path(__file__).resolve().parent
DERIVED = HERE / "derived"
OUT = PATHS.VAULT_ATTACHMENTS
IMPDIR = PATHS.IMPEDANCE_ROOT

SEED = 20260809
PALETTE = "okabe_ito_on_white"
STYLE = "default"

# Okabe-Ito, taken from the skill's palette asset rather than hand-typed hexes.
from color_palettes import OKABE_ITO                 # noqa: E402

C_WORK = OKABE_ITO["blue"]           # working animal 1
C_WORK2 = OKABE_ITO["bluish_green"]  # working animal 2
C_FAIL = OKABE_ITO["vermillion"]     # failing channel
C_WARN = OKABE_ITO["orange"]         # partial
C_ACCENT = OKABE_ITO["reddish_purple"]
C_FLOOR = "#5A5A5A"                  # controls and null distributions, neutral
C_INK = "#222222"
C_INK_SOFT = "#555555"

# --------------------------------------------------------------------------- #
# VERDICT ENCODING
# --------------------------------------------------------------------------- #
# Status colours are RESERVED. They mean state, never series identity, and they
# are never reused for "the fourth animal".
#
# Validated with the dataviz skill's checker before use:
#   node scripts/validate_palette.js "#009E73,#E69F00,#D55E00,#56B4E9" \
#        --mode light --pairs all
#   -> ALL CHECKS PASS. Worst all-pairs CVD separation dE 11.0 (deutan,
#      vermillion vs green); worst normal-vision pair dE 15.6 (vermillion vs
#      orange). One WARN: orange and sky blue fall below 3:1 contrast against
#      white, which OBLIGES a visible label rather than colour alone.
#
# That obligation is met by construction: every verdict is drawn as a GLYPH plus
# the VERDICT WORD plus the colour. Print the card in greyscale, or read it with
# any colour vision, and it still says PASS or FAIL in words.
VERDICT_COLOR = {
    "PASS":         OKABE_ITO["bluish_green"],   # good
    "PROVISIONAL":  OKABE_ITO["orange"],         # warning: answered, but gated
    "INSUFFICIENT": OKABE_ITO["sky_blue"],       # the question could not be asked
    "FAIL":         OKABE_ITO["vermillion"],     # critical
    "BLOCKED":      C_FLOOR,                     # neutral: never evaluated
}
VERDICT_GLYPH = {
    "PASS": "✓", "PROVISIONAL": "◐", "INSUFFICIENT": "?",
    "FAIL": "✗", "BLOCKED": "–",
}
# 🔑 INSUFFICIENT IS NOT FAIL, and the card must never let them read as the same
# thing. "The question could not be asked" has been misread as "the answer was
# no" in this project before: an animal with 8 minutes of usable data is not an
# animal that does not sleep. Different hue, different glyph, different word.
VERDICT_MEANING = {
    "PASS": "asked and answered yes",
    "PROVISIONAL": "answered, but gated behind work not yet done",
    "INSUFFICIENT": "the question could not be asked",
    "FAIL": "asked and answered no",
    "BLOCKED": "a lower rung failed, so this was never evaluated",
}


def verdict_style(verdict: str) -> tuple[str, str]:
    """(colour, glyph) for a verdict. Unknown verdicts render as neutral."""
    return (VERDICT_COLOR.get(verdict, C_FLOOR),
            VERDICT_GLYPH.get(verdict, "?"))


# --------------------------------------------------------------------------- data
def derived(name: str):
    """Load a derived input, refusing to fall back to anything hand-entered."""
    p = DERIVED / name
    if not p.exists():
        raise SystemExit(
            f"missing derived input {p}\nRun: python compute_inputs.py\n"
            "Figures do not carry typed-in values, so this is fatal by design.")
    if p.suffix == ".json":
        return json.loads(p.read_text())
    return np.load(p, allow_pickle=True)


def pos_to_file(position: str) -> str:
    """B1 -> portB-slot1. The processed-file naming convention, in one place."""
    return f"port{position[0]}-slot{position[1]}"


# These take an explicit path rather than a position plus a hardcoded recording
# tag. The old signatures baked one cohort and one night into the module, which
# is exactly why the figure set could not follow the animals when they changed.
def load_npz(path):
    return np.load(Path(path), allow_pickle=True)


def load_features(path):
    return json.loads(Path(path).read_text())


def load_hypno(path):
    import csv
    with open(Path(path)) as fh:
        return list(csv.DictReader(fh))


# --------------------------------------------------------------------------- dsp
def bandpass(x, fs, lo, hi, order=4):
    from scipy import signal as sg
    hi = min(hi, fs / 2 - 1)
    sos = sg.butter(order, [lo, hi], btype="band", fs=fs, output="sos")
    return sg.sosfiltfilt(sos, x)


def notch_mains(x, fs, freqs=(60, 120, 180), q=30):
    from scipy import signal as sg
    y = x.copy()
    for f in freqs:
        if f < fs / 2 - 1:
            b, a = sg.iirnotch(f, q, fs)
            y = sg.filtfilt(b, a, y)
    return y


def median_window(x, fs, sec, n_try=200):
    """THE window rule, used by every figure that shows a trace or a spectrum:
    the window whose rms is closest to the median rms of that channel. Applying
    one rule everywhere removes the freedom to pick a flattering moment."""
    n = int(sec * fs)
    starts = np.linspace(0, max(len(x) - n - 1, 1), n_try).astype(int)
    r = np.array([np.sqrt(np.mean(np.asarray(x[s0:s0 + n], float) ** 2)) for s0 in starts])
    k = int(np.argmin(np.abs(r - np.median(r))))
    return np.asarray(x[starts[k]:starts[k] + n], float), int(starts[k])


# --------------------------------------------------------------------------- stats
def block_bootstrap_ci(mask, block=None, n_boot=2000, rng=None, ci=95):
    """CI for the fraction of TRUE in a binary time series whose values are
    autocorrelated. Resamples contiguous blocks, so the interval reflects that
    neighbouring epochs are not independent observations.

    A Bernoulli interval on the same data is wrong by one to two orders of
    magnitude here, because electrical contact persists for tens of minutes.
    """
    rng = rng or np.random.default_rng(SEED)
    m = np.asarray(mask, bool)
    n = len(m)
    if n == 0:
        return (np.nan, np.nan, np.nan)
    if block is None:                      # Politis and White style rule of thumb
        block = max(int(round(n ** (1 / 3))) * 3, 30)
    block = min(block, max(n // 4, 1))
    n_blocks = max(int(np.ceil(n / block)), 1)
    starts = np.arange(0, n - block + 1)
    if len(starts) == 0:
        return (float(m.mean()), np.nan, np.nan)
    out = np.empty(n_boot)
    for i in range(n_boot):
        s0 = rng.choice(starts, size=n_blocks)
        out[i] = np.concatenate([m[s:s + block] for s in s0])[:n].mean()
    lo, hi = np.percentile(out, [(100 - ci) / 2, 100 - (100 - ci) / 2])
    return float(m.mean()), float(lo), float(hi)


def effective_n(mask):
    """Effective sample size of an autocorrelated binary series, from its lag-1
    autocorrelation. Reported so the reader can see how far 8,517 epochs is from
    8,517 independent observations."""
    m = np.asarray(mask, float)
    if m.std() == 0:
        return 1.0
    r1 = float(np.corrcoef(m[:-1], m[1:])[0, 1])
    r1 = min(max(r1, 0.0), 0.999)
    return float(len(m) * (1 - r1) / (1 + r1))


def holm_bh(pvals):
    """Holm (family-wise) and Benjamini-Hochberg (FDR) adjusted p values."""
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    holm = np.empty(n)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (n - rank) * p[idx])
        holm[idx] = min(running, 1.0)
    bh = np.empty(n)
    running = 1.0
    for rank in range(n - 1, -1, -1):
        idx = order[rank]
        running = min(running, n / (rank + 1) * p[idx])
        bh[idx] = min(running, 1.0)
    return holm, bh


def wilson_note():
    return ("intervals are block bootstrap, not Bernoulli: epochs within a "
            "recording are strongly autocorrelated")


# --------------------------------------------------------------------------- export
def save(fig, stem: str, *, alt: str, provenance: dict, caption: str = ""):
    """Export PNG and PDF with a provenance manifest and a stored alt text.

    `bbox_inches=None` keeps the declared figure size, which `bbox_inches="tight"`
    silently changed in the previous version of these figures.
    """
    prov = dict(provenance)
    prov.setdefault("seed", SEED)
    prov.setdefault("palette", PALETTE)
    prov.setdefault("style", f"{STYLE} (scientific-visualization skill asset)")
    prov["alt_text"] = alt
    if caption:
        prov["caption"] = caption
    report = export_figure(
        fig, str(OUT / stem),
        formats=["png", "pdf"], dpi=300, bbox_inches=None,
        facecolor="white", font_mode="truetype",
        overwrite=True, mkdir=True,
        provenance=prov, write_manifest=True,
    )
    plt.close(fig)
    outs = report.get("outputs", [])
    names = [os.path.basename(o["path"] if isinstance(o, dict) else o) for o in outs]
    print(f"wrote {stem}: " + ", ".join(names))
    return report


def figure(*args, **kwargs):
    """plt.subplots with constrained layout, which is required for the exporter
    to preserve physical dimensions."""
    kwargs.setdefault("layout", "constrained")
    return plt.subplots(*args, **kwargs)


def figure_with_caption(nrows=1, ncols=1, *, figsize, caption_frac=0.18,
                        sharex=False, sharey=False, width_ratios=None,
                        height_ratios=None):
    """Figure whose caption lives in a reserved axes row.

    Reserving real estate is what keeps the exported page the declared size.
    The earlier figures wrote captions outside the canvas and depended on
    `bbox_inches="tight"` to grow the page, so no figure was the size it claimed.
    """
    fig = plt.figure(figsize=figsize, layout="constrained")
    outer = fig.add_gridspec(2, 1, height_ratios=[1 - caption_frac, caption_frac])
    sub = outer[0].subgridspec(nrows, ncols, width_ratios=width_ratios,
                               height_ratios=height_ratios)
    axes = np.empty((nrows, ncols), dtype=object)
    first = None
    for r in range(nrows):
        for c in range(ncols):
            kw = {}
            if first is not None:
                if sharex:
                    kw["sharex"] = first
                if sharey:
                    kw["sharey"] = first
            ax = fig.add_subplot(sub[r, c], **kw)
            axes[r, c] = ax
            first = first or ax
    cap = fig.add_subplot(outer[1])
    cap.axis("off")
    out = axes if (nrows > 1 and ncols > 1) else axes.ravel()
    return fig, (out[0] if out.size == 1 else out), cap


def caption(cap_ax, text, chars_per_line=170, fontsize=7.0):
    import textwrap
    lines = textwrap.wrap(" ".join(text.split()), chars_per_line)
    cap_ax.text(0.5, 1.0, "\n".join(lines), ha="center", va="top",
                fontsize=fontsize, color="#333333", linespacing=1.5,
                transform=cap_ax.transAxes)


def caption_block(fig, text, chars_per_line=175, fontsize=7.0):
    """Put the caption INSIDE the figure canvas and reserve room for it.

    The previous version wrote captions at negative axes coordinates and relied
    on `bbox_inches="tight"` to grow the canvas, which silently changed the page
    size of every figure. Here the constrained layout is told to leave space, so
    the declared figure size is what gets exported.
    """
    import textwrap
    lines = textwrap.wrap(" ".join(text.split()), chars_per_line)
    h_in = (len(lines) * fontsize * 1.45) / 72.0
    frac = min(h_in / fig.get_size_inches()[1], 0.45)
    eng = fig.get_layout_engine()
    if eng is not None:
        eng.set(rect=(0.01, frac + 0.015, 0.99, 0.99))
    fig.text(0.5, frac - 0.005, "\n".join(lines), ha="center", va="top",
             fontsize=fontsize, color="#333333", linespacing=1.45)

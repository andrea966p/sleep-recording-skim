#!/usr/bin/env python3
"""Render one ANIMAL CARD from a card JSON produced by cards/ladder.py.

    ~/eeg-analysis-venv/bin/python cards/render_card.py <card.json> [...]

LAYOUT, and why it is this way
-----------------------------
    row 1   IDENTITY BAR      who this is, one line
    row 2   STATE LINE        where it was in its life at this recording
    row 3   LIFE TIMELINE     the whole animal on an axis of AGE IN WEEKS
    left    VERDICT LADDER    six rungs, top to bottom, with the deciding number
    right   EVIDENCE PANELS   drawn ONLY for rungs that passed
    footer  PROVENANCE        source files, criterion, thresholds hash, notes

The verdict ladder is the point of the card. A reader who looks at nothing else
still gets the right answer, and the panels beside it can never imply more than
the ladder allows, because a panel for a blocked rung is not drawn at all.

Every verdict is a GLYPH plus a WORD plus a colour, so the card survives
greyscale printing and any colour vision.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent

from cards import figs_common as F                 # noqa: E402
from cards.figs_common import plt             # noqa: E402
from core import qc_thresholds as T     # noqa: E402

NOT_RECORDED = "not recorded"

TIMELINE_STYLE = {
    "arrival":      ("o", F.C_INK_SOFT, 34),
    "surgery":      ("P", F.C_ACCENT, 60),
    "tether":       ("D", F.C_WORK, 42),
    "tether-arm":   ("d", F.C_WORK, 28),
    "recording":    ("s", F.C_WORK2, 44),
    "intervention": ("^", F.C_WARN, 46),
    "sacrifice":    ("X", F.C_FAIL, 60),
    "sampling":     ("v", F.C_FAIL, 44),
}


def _fmt(value, unit="", decimals=None):
    if value is None or value == "":
        return NOT_RECORDED
    if decimals is not None and isinstance(value, (int, float)):
        return f"{value:.{decimals}f}{unit}"
    return f"{value}{unit}"


# --------------------------------------------------------------------------- #
def draw_identity(fig, card: dict) -> None:
    age = card.get("age_weeks")
    age_txt = (f"{age} wk" + (" (derived)" if card.get("age_is_derived") else "")
               if age is not None else NOT_RECORDED)
    # Two short lines beat one long one: a single line of fifteen fields ran off
    # the page and truncated the tether arm, which is the experimental variable.
    bits = [card.get("animal_id") or "?",
            (card.get("sex") or "sex " + NOT_RECORDED),
            f"age {age_txt}",
            f"position {card.get('position', '?')}",
            f"tether arm {card.get('tether_arm') or NOT_RECORDED}"]
    fig.text(0.012, 0.988, "   ·   ".join(bits), fontsize=9.0, fontweight="bold",
             color=F.C_INK, va="top", ha="left")
    fig.text(0.988, 0.988,
             f"{card.get('project_id') or NOT_RECORDED}  ·  "
             f"{card.get('batch_id') or NOT_RECORDED}",
             fontsize=6.6, color=F.C_INK_SOFT, va="top", ha="right")
    fig.text(0.012, 0.970, card.get("recording", ""), fontsize=7.0,
             color=F.C_INK_SOFT, va="top", ha="left", family="monospace")

    dps = card.get("days_post_surgery")
    dpt = card.get("days_post_tether")
    bw = card.get("body_weight_g")
    bw_txt = (f"{bw:.1f} g ({card.get('body_weight_occasion') or 'occasion unknown'})"
              if bw is not None else f"body weight {NOT_RECORDED}")
    zt = ""
    if card.get("zt_start") is not None:
        zt = f"ZT {card['zt_start']:.1f} to {card.get('zt_end', float('nan')):.1f}"
    state = [
        f"day {dps} post-surgery" if dps is not None else f"post-surgery day {NOT_RECORDED}",
        f"day {dpt} post-tether" if dpt is not None else f"post-tether day {NOT_RECORDED}",
        bw_txt,
        f"{card['duration_h']:.2f} h" if card.get("duration_h") else "duration unknown",
        zt or "ZT span unknown",
        f"criterion {card.get('criterion', '?').upper()}",
        f"QC epoch {card.get('epoch_s_qc', '?')} s",
        # the thresholds hash lives in the footer; repeating it here overflowed
        # the line on animals whose husbandry fields read "not recorded"
    ]
    fig.text(0.012, 0.955, "   ·   ".join(state), fontsize=6.4,
             color=F.C_INK_SOFT, va="top", ha="left")
    if card.get("role") and card["role"] != "animal":
        fig.text(0.988, 0.970, card["role"].upper(), fontsize=8.4,
                 fontweight="bold", color=F.C_WARN, va="top", ha="right")


def draw_timeline(ax, card: dict) -> None:
    """The animal's life on one axis of AGE IN WEEKS, with body weight on it."""
    ax.set_facecolor("white")
    events = card.get("timeline", [])
    weighings = [w for w in card.get("weighings", [])
                 if w.get("date") and w.get("grams") is not None]

    if not events:
        ax.axis("off")
        ax.text(0.5, 0.5,
                "LIFE TIMELINE NOT AVAILABLE — no dated events are recorded for "
                "this animal.\nArrival, surgery, tethering and body weights were "
                "never written down for this cohort.\nAdd them to the cohort "
                "manifest or a husbandry sheet and this strip fills itself in.",
                ha="center", va="center", fontsize=7.2, color=F.C_FAIL,
                transform=ax.transAxes, linespacing=1.6)
        return

    dob_known = card.get("age_weeks") is not None and not card.get("age_is_derived")
    rec_date = card.get("recording_date")
    dates = [dt.date.fromisoformat(e["date"]) for e in events]
    # x axis: age in whole weeks when we can, else days from the first event
    if card.get("age_weeks") is not None and rec_date:
        anchor_date = dt.date.fromisoformat(rec_date)
        anchor_age = card["age_weeks"]

        def to_x(d):
            return anchor_age + (d - anchor_date).days / 7.0
        xlabel = ("age (weeks)" +
                  ("" if dob_known else ", derived from age at arrival"))
    else:
        anchor_date = min(dates)

        def to_x(d):
            return (d - anchor_date).days / 7.0
        xlabel = f"weeks from {anchor_date.isoformat()} (age not recorded)"

    seen: set[str] = set()
    for e in events:
        d = dt.date.fromisoformat(e["date"])
        marker, colour, size = TIMELINE_STYLE.get(e["kind"], ("o", F.C_FLOOR, 30))
        is_this = (e["kind"] == "recording" and e["label"] == card.get("recording"))
        ax.scatter([to_x(d)], [0], marker=marker, s=size * (1.9 if is_this else 1.0),
                   color=colour, zorder=4 if is_this else 3,
                   edgecolor="white", linewidth=0.8,
                   label=e["kind"] if e["kind"] not in seen else None)
        seen.add(e["kind"])
        if is_this:
            ax.annotate("THIS RECORDING", (to_x(d), 0), textcoords="offset points",
                        xytext=(0, 13), ha="center", fontsize=6.4,
                        fontweight="bold", color=F.C_WORK2)
        elif e["kind"] in ("surgery", "tether", "sacrifice", "intervention"):
            # Stagger alternate labels so events days apart do not overprint.
            below = -15 if (len(seen) % 2 == 0) else -25
            ax.annotate(e["label"], (to_x(d), 0), textcoords="offset points",
                        xytext=(0, below), ha="center", fontsize=6.0,
                        color=F.C_INK_SOFT)

    ax.axhline(0, color=F.C_FLOOR, lw=1.0, zorder=1)

    if weighings:
        wx = [to_x(dt.date.fromisoformat(w["date"])) for w in weighings]
        wy = [w["grams"] for w in weighings]
        ax2 = ax.twinx()
        ax2.plot(wx, wy, "-o", color=F.C_ACCENT, lw=1.4, ms=3.5, zorder=5)
        ax2.set_ylabel("body weight (g)", fontsize=6.2, color=F.C_ACCENT)
        ax2.tick_params(labelsize=5.8, colors=F.C_ACCENT)
        for s in ("top", "left"):
            ax2.spines[s].set_visible(False)
    else:
        ax.text(0.995, 1.30, "no body weight recorded", transform=ax.transAxes,
                ha="right", va="top", fontsize=6.0, color=F.C_FAIL)

    if card.get("timeline") and not any(e["kind"] == "sacrifice" for e in events):
        ax.text(0.995, 1.14, "no end date recorded", transform=ax.transAxes,
                ha="right", va="top", fontsize=6.0, color=F.C_INK_SOFT)

    ax.set_yticks([])
    ax.set_ylim(-0.55, 0.55)
    ax.set_xlabel(xlabel, fontsize=6.6)
    ax.tick_params(labelsize=6.0)
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=12))
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.02), fontsize=5.6,
              ncol=len(seen), frameon=False, handletextpad=0.2,
              columnspacing=1.0, borderpad=0.0)
    ax.set_title("LIFE TIMELINE", fontsize=7.2, loc="left", color=F.C_INK,
                 fontweight="bold", pad=18)


def draw_ladder(ax, card: dict) -> None:
    ax.axis("off")
    rungs = card["rungs"]
    n = len(rungs)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n)
    ax.set_title("VERDICT LADDER", fontsize=7.6, loc="left",
                 color=F.C_INK, fontweight="bold", pad=6)

    # Fixed line positions inside each unit-height row. Earlier versions placed
    # these by eye and the headline sat on top of the question.
    Y_TITLE, Y_QUESTION, Y_HEADLINE, Y_DETAIL = 0.80, 0.62, 0.45, 0.34
    import textwrap
    for i, r in enumerate(rungs):
        y = n - i - 1
        colour, glyph = F.verdict_style(r["verdict"])
        ax.add_patch(plt.Rectangle((0.0, y + 0.06), 1.0, 0.88,
                                   facecolor=colour, alpha=0.10,
                                   edgecolor=colour, linewidth=1.0))
        ax.add_patch(plt.Rectangle((0.0, y + 0.06), 0.020, 0.88,
                                   facecolor=colour, edgecolor="none"))
        ax.text(0.040, y + Y_TITLE, f"{glyph}  {r['number']} {r['name']}",
                fontsize=8.4, fontweight="bold", color=colour, va="center")
        ax.text(0.988, y + Y_TITLE, r["verdict"], fontsize=8.4, fontweight="bold",
                color=colour, va="center", ha="right")
        ax.text(0.040, y + Y_QUESTION, r["question"], fontsize=6.0,
                color=F.C_INK_SOFT, va="center", style="italic")
        if r.get("headline"):
            ax.text(0.040, y + Y_HEADLINE, r["headline"], fontsize=7.0,
                    color=F.C_INK, va="center", fontweight="bold")
        detail = r.get("threshold") or ""
        reason = r.get("reason") or ""
        # HARD CAP AT TWO LINES. An uncapped reason on rung 4 overflowed into
        # rung 5's box and made one rung's text look like another's verdict.
        lines = []
        if detail:
            lines.append(textwrap.shorten("vs " + detail, 138, placeholder=" ..."))
        if reason:
            lines.append(textwrap.shorten(reason, 138, placeholder=" ..."))
        if lines:
            ax.text(0.040, y + Y_DETAIL, "\n".join(lines[:2]), fontsize=5.4,
                    color=F.C_INK_SOFT, va="top", linespacing=1.5)

    ax.text(0.0, -0.30,
            "A rung is not evaluated if the rung below it failed: it reads "
            "BLOCKED.    ?  INSUFFICIENT means the question could not be asked, "
            "which is NOT the same as  ✗  FAIL.",
            fontsize=5.6, color=F.C_INK_SOFT, va="top")


def _mask_from_runs(n, spans):
    m = np.zeros(n, dtype=bool)
    for a, b in spans:
        m[int(a):int(b)] = True
    return m


def draw_connection(ax, card: dict, rung: dict) -> None:
    """Usable-epoch ribbon per role, with the lights-off band behind it."""
    per_role = rung["detail"]["per_role"]
    roles = list(per_role)
    epoch_s = card.get("epoch_s_qc", T.EPOCH_S_QC)
    hours = card.get("duration_h") or (
        rung["detail"]["combined"]["n_epochs_total"] * epoch_s / 3600)

    ax.set_title("RUNG 2 evidence — usable epochs against the in-file wire-free floor",
                 fontsize=7.2, loc="left", color=F.C_INK, fontweight="bold", pad=3)
    # The bar axis stops at the recording length. Annotations live in AXES
    # fraction beyond it, so a bar can never appear to exceed the recording.
    y = 0
    labels = []
    entries = [(r, per_role[r], False) for r in roles]
    entries.append(("all roles", rung["detail"]["combined"], True))
    for name, s, is_combined in entries:
        frac = s["usable_fraction"]
        colour = (F.C_WORK if is_combined else
                  (F.C_WORK2 if frac >= 0.5 else (F.C_WARN if frac > 0 else F.C_FAIL)))
        ax.barh(y, hours, height=0.58, color=F.C_FLOOR, alpha=0.12, zorder=0)
        ax.barh(y, hours * frac, height=0.58, color=colour, alpha=0.9)
        label = (f"{100 * frac:.1f}%   {s['n_epochs_usable']:,} of "
                 f"{s['n_epochs_total']:,} epochs   ·   longest unbroken "
                 f"{s['longest_block_minutes']:.0f} min")
        # A long bar carries its label inside in white; a short one carries it
        # outside in ink. Either way the label never leaves the axes.
        if frac >= 0.45:
            ax.text(hours * frac - hours * 0.012, y, label, ha="right",
                    va="center", fontsize=6.1, color="white",
                    fontweight="bold" if is_combined else "normal")
        else:
            ax.text(max(hours * frac, 0) + hours * 0.012, y, label, ha="left",
                    va="center", fontsize=6.1, color=F.C_INK,
                    fontweight="bold" if is_combined else "normal")
        labels.append("ALL ROLES\ntogether" if is_combined
                      else f"{name.upper()}  {s['site']}\n[{s['criterion']}]")
        y += 1

    fals = rung["detail"].get("falsification", {})
    floor = rung["detail"]["floor"]
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=5.8)
    ax.set_xlabel("hours of recording", fontsize=6.4)
    ax.set_xlim(0, hours)
    ax.set_ylim(-0.75, len(labels) - 0.35)
    ax.tick_params(labelsize=6.0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.text(0.0, -0.30,
            f"falsification: the same criterion scores the "
            f"{fals.get('n_floor_sites', '?')} wire-free inputs in this file at "
            f"{100 * fals.get('mean_usable_fraction', 0):.2f}% usable, and must be "
            f"near zero   ·   floor 60 Hz p1 {floor.get('hum_p1', 0):.0f} uV, "
            f"1-40 Hz slope p1 {floor.get('slope_p1', 0):.2f}",
            transform=ax.transAxes, ha="left", va="top", fontsize=5.5,
            color=F.C_INK_SOFT)


def draw_architecture(ax, card: dict, rung: dict) -> None:
    """The Otsu sensitivity sweep: the honest form of the circadian claim."""
    rows = rung["detail"].get("otsu_sensitivity") or []
    swing = rung["detail"].get("asleep_in_light_swing_pts")
    title = "RUNG 4 evidence — how much the wake threshold moves the answer"
    if swing is not None:
        title += (f"\nthe light-phase sleep figure moves {swing:.1f} points across "
                  "a +/-25% sweep of that one threshold")
    ax.set_title(title, fontsize=7.2, loc="left", color=F.C_INK,
                 fontweight="bold", pad=4)
    if not rows:
        ax.axis("off")
        ax.text(0.5, 0.5, "no threshold sweep in this animal's stage 3 output",
                ha="center", va="center", fontsize=6.4, color=F.C_INK_SOFT,
                transform=ax.transAxes)
        return
    mult = [r["multiplier"] for r in rows]
    light = [r.get("asleep_in_light_pct") for r in rows]
    wake = [r.get("wake_pct") for r in rows]

    ax.plot(mult, light, "-o", color=F.C_WORK, lw=1.6, ms=4,
            label="asleep in the light phase")
    ax.plot(mult, wake, "-s", color=F.C_WARN, lw=1.4, ms=3.5, label="wake")
    ax.axvline(1.0, color=F.C_FLOOR, ls=":", lw=1.0)
    ax.axhline(70.0, color=F.C_FLOOR, ls="--", lw=1.0)
    ax.annotate("literature ~70%", (mult[0], 70.0), textcoords="offset points",
                xytext=(2, 3), fontsize=5.6, color=F.C_INK_SOFT)
    ax.annotate("Otsu cut", (1.0, ax.get_ylim()[0]), textcoords="offset points",
                xytext=(3, 4), fontsize=5.6, color=F.C_INK_SOFT)

    ax.set_xlabel("multiplier on the per-animal wake threshold (uV)", fontsize=6.4)
    ax.set_ylabel("percent", fontsize=6.4)
    ax.tick_params(labelsize=6.0)
    ax.legend(fontsize=5.8, frameon=False, loc="lower right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)



def draw_caveats(ax, rung: dict) -> None:
    """The full rung-4 caveats, beside the evidence rather than truncated in it.

    These belong ON the card, not in a covering note, because every one of them
    has previously been dropped somewhere between an analysis and a slide.
    """
    import textwrap
    ax.axis("off")
    caveats = rung.get("detail", {}).get("caveats") or []
    if not caveats:
        return
    ax.text(0, 1.0, "READ WITH THE PANEL ON THE LEFT", fontsize=6.4,
            fontweight="bold", color=F.C_WARN, va="top", transform=ax.transAxes)
    # Three fit the panel. The fourth is on the card in the JSON and in the
    # vault page; crowding it in here would overprint the animal notes.
    text = "\n\n".join(
        "\n".join(textwrap.wrap("•  " + c, 74, subsequent_indent="    "))
        for c in caveats[:3])
    ax.text(0, 0.90, text, transform=ax.transAxes, va="top", ha="left",
            fontsize=5.4, color=F.C_INK_SOFT, linespacing=1.6)


def draw_blocked_panel(ax, rung: dict) -> None:
    ax.axis("off")
    colour, glyph = F.verdict_style(rung["verdict"])
    ax.text(0.5, 0.62, f"{glyph}  RUNG {rung['number']} {rung['name']}: "
            f"{rung['verdict']}",
            ha="center", va="center", fontsize=8.4, fontweight="bold",
            color=colour, transform=ax.transAxes)
    import textwrap
    ax.text(0.5, 0.34, "\n".join(textwrap.wrap(rung.get("reason", ""), 92)),
            ha="center", va="center", fontsize=6.4, color=F.C_INK_SOFT,
            transform=ax.transAxes, linespacing=1.5)
    ax.text(0.5, 0.08, "NO PANEL IS DRAWN FOR A RUNG THAT DID NOT PASS.",
            ha="center", va="center", fontsize=6.0, color=F.C_INK_SOFT,
            transform=ax.transAxes, style="italic")


def render(card_path: Path, outdir: Path | None = None) -> dict:
    card = json.loads(Path(card_path).read_text())
    rungs = {r["number"]: r for r in card["rungs"]}

    with F.style_context(F.STYLE):
        fig = plt.figure(figsize=(8.27, 11.69))     # A4 portrait
        # The ladder gets the most room because it is the point of the card.
        gs = fig.add_gridspec(
            4, 1, height_ratios=[0.62, 2.75, 1.00, 1.00],
            top=0.898, bottom=0.105, left=0.085, right=0.965, hspace=0.62)

        draw_identity(fig, card)
        draw_timeline(fig.add_subplot(gs[0]), card)
        draw_ladder(fig.add_subplot(gs[1]), card)

        ax_conn = fig.add_subplot(gs[2])
        if rungs[2]["verdict"] in ("PASS", "FAIL", "INSUFFICIENT") and \
                rungs[2].get("detail", {}).get("per_role"):
            draw_connection(ax_conn, card, rungs[2])
        else:
            draw_blocked_panel(ax_conn, rungs[2])

        if rungs[4]["verdict"] == "PROVISIONAL":
            sub = gs[3].subgridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.18)
            draw_architecture(fig.add_subplot(sub[0]), card, rungs[4])
            draw_caveats(fig.add_subplot(sub[1]), rungs[4])
        else:
            draw_blocked_panel(fig.add_subplot(gs[3]), rungs[4])

        notes = []
        if card.get("notes"):
            notes.append(card["notes"].strip())
        if card.get("surgery_notes"):
            notes.append("Surgery: " + card["surgery_notes"].strip())
        if card.get("sampling_notes"):
            notes.append("Sampling: " + card["sampling_notes"].strip())
        prov = card.get("provenance", {})
        footer = (
            f"{card['cohort_id']}  ·  card schema v{card['schema_version']}  ·  "
            f"generated {card.get('generated', '')}  ·  git {prov.get('git_rev', '?')}  ·  "
            f"thresholds {card.get('thresholds_hash', '?')} "
            f"({Path(prov.get('thresholds_file', '')).name})  ·  "
            f"criterion {card.get('criterion', '?').upper()} at "
            f"{card.get('epoch_s_qc')} s epochs.  "
            f"{prov.get('criterion_note', '')}")
        import textwrap
        if notes:
            fig.text(0.085, 0.072, "\n".join(textwrap.wrap(" ".join(notes), 168)[:4]),
                     fontsize=5.6, color=F.C_INK_SOFT, va="top", linespacing=1.5)
        fig.text(0.085, 0.026, "\n".join(textwrap.wrap(footer, 182)[:3]),
                 fontsize=5.0, color=F.C_INK_SOFT, va="top", linespacing=1.4)

        stem_dir = outdir or (ROOT / "cards" / "out" / card["cohort_id"] / "figures")
        stem_dir.mkdir(parents=True, exist_ok=True)
        stem = (f"{card['recording']}__{card['position']}"
                f"__{card.get('animal_id', 'unknown')}_card")

        top = card.get("top_rung", -1)
        alt = (
            f"Animal card for {card.get('animal_id')} in rig position "
            f"{card.get('position')} during recording {card.get('recording')}. "
            f"The verdict ladder reads: "
            + "; ".join(f"rung {r['number']} {r['name']} {r['verdict']}"
                        for r in card["rungs"])
            + f". The highest rung passed is {top}. "
            + (f"Connection: {rungs[2].get('headline', '')}. "
               if rungs[2].get("headline") else "")
            + "The life timeline strip shows this animal's dated events on an "
              "axis of age in weeks.")

        report = F.export_figure(
            fig, str(stem_dir / stem), formats=["png", "pdf"], dpi=300,
            bbox_inches=None, facecolor="white", font_mode="truetype",
            overwrite=True, mkdir=True, write_manifest=True,
            provenance={
                "seed": F.SEED, "palette": F.PALETTE,
                "style": f"{F.STYLE} (scientific-visualization skill asset)",
                "alt_text": alt,
                "card_json": str(card_path),
                "source_files": prov.get("processed_files", {}),
                "recording_base": card.get("recording_base"),
                "criterion": card.get("criterion"),
                "thresholds_hash": card.get("thresholds_hash"),
                "git_rev": prov.get("git_rev"),
                "verdicts": {r["name"]: r["verdict"] for r in card["rungs"]},
            })
        plt.close(fig)
    print(f"  {stem}.png / .pdf   top rung {top}")
    return report


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cards", nargs="+", help="card JSON files, or a directory of them")
    ap.add_argument("--out", help="output directory")
    args = ap.parse_args(argv)

    paths: list[Path] = []
    for t in args.cards:
        p = Path(t).expanduser()
        paths.extend(sorted(p.glob("*_card.json")) if p.is_dir() else [p])
    if not paths:
        raise SystemExit("no card JSON found")

    print(f"rendering {len(paths)} card(s)")
    for p in paths:
        render(p, Path(args.out) if args.out else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

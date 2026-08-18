#!/usr/bin/env python3
"""COHORT SHEET: every animal-recording as one row, every rung as one column.

    ~/eeg-analysis-venv/bin/python cards/render_cohort_sheet.py \
        cards/out/HLB-fem-profsurgery-troubleshooting

This is the one-page answer to "how is the rig doing", and it is GENERATED, not
drawn. Nobody types a verdict into it, so it cannot disagree with the cards.

Reading it: find the column where a row stops being green. That column is the
thing to fix for that animal. Read down a column instead and you see whether the
cohort shares a failure, which is how the tether chain was identified.

Colour never carries meaning alone: every cell holds a glyph and every verdict
appears in the legend as a word.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from cards import figs_common as F                 # noqa: E402
from cards.figs_common import plt             # noqa: E402

# Two lines each: on one line, "3 SCOREABILITY" and "4 ARCHITECTURE" collide.
RUNG_NAMES = ["0\nFILE", "1\nIDENTITY", "2\nCONNECTION", "3\nSCOREABILITY",
              "4\nARCHITECTURE", "5\nEXPORT"]

# The three tether builds this cohort was testing. Written out in full on the
# sheet, because "arm A" is lab shorthand and the reader is not in the lab.
TETHER_NAME = {
    "A": "original tether",
    "B": "short 19.5 cm, soldered joints, resin encapsulated",
    "C": "long, soldered joints, direct to headstage, no slip ring",
}
# Short tag for the row label; the full name goes in the legend below the sheet.
TETHER_SHORT = {"A": "original", "B": "short soldered", "C": "no slip ring"}


def load_cards(indir: Path) -> list[dict]:
    cards = [json.loads(p.read_text()) for p in sorted(indir.glob("*_card.json"))]
    if not cards:
        raise SystemExit(f"no card JSON in {indir}")
    cards.sort(key=lambda c: (c.get("recording_date", ""), c.get("recording", ""),
                              c.get("position", "")))
    return cards


def render(cards: list[dict], out_stem: Path, cohort_id: str) -> dict:
    n = len(cards)
    height = max(3.4, 2.2 + 0.34 * n)

    with F.style_context(F.STYLE):
        fig = plt.figure(figsize=(11.69, height))        # A4 landscape
        ax = fig.add_axes([0.275, 0.17, 0.435, 0.68])
        ax.set_xlim(-0.5, len(RUNG_NAMES) - 0.5)
        ax.set_ylim(-0.5, n - 0.5)
        ax.invert_yaxis()

        for row, card in enumerate(cards):
            by_num = {r["number"]: r for r in card["rungs"]}
            for col in range(len(RUNG_NAMES)):
                r = by_num.get(col, {"verdict": "BLOCKED"})
                colour, glyph = F.verdict_style(r["verdict"])
                ax.add_patch(plt.Rectangle((col - 0.46, row - 0.42), 0.92, 0.84,
                                           facecolor=colour, alpha=0.18,
                                           edgecolor=colour, linewidth=0.9))
                ax.text(col, row, glyph, ha="center", va="center",
                        fontsize=11, color=colour, fontweight="bold")

        ax.set_xticks(range(len(RUNG_NAMES)))
        ax.set_xticklabels(RUNG_NAMES, fontsize=7.0, fontweight="bold")
        ax.xaxis.set_ticks_position("top")
        ax.set_yticks(range(n))
        # Spell the tether out on the row. "arm A" means nothing to a reader who
        # was not in the room when the arms were named.
        ax.set_yticklabels(
            [f"{c.get('position', '?')}  {c.get('animal_id', '?')}"
             f"   {TETHER_SHORT.get(c.get('tether_arm', ''), 'tether ?')}"
             for c in cards], fontsize=6.6)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)

        # right-hand columns: what the animal actually yielded
        for row, card in enumerate(cards):
            by_num = {r["number"]: r for r in card["rungs"]}
            conn = by_num.get(2, {})
            comb = conn.get("detail", {}).get("combined", {})
            frac = comb.get("usable_fraction")
            longest = comb.get("longest_block_minutes")
            score = by_num.get(3, {}).get("detail", {}) or {}
            usable_txt = ("—" if frac is None else f"{100 * frac:5.1f}%")
            long_txt = ("—" if not longest else f"{longest:6.0f} min")
            hours = score.get("hours_in_blocks")
            score_txt = ("—" if hours is None else f"{hours:5.2f} h")
            r1 = score.get("r_1min")
            r_txt = "—" if r1 is None else f"{r1:+.3f}"
            for x, txt in ((1.10, usable_txt), (1.26, long_txt),
                           (1.40, score_txt), (1.55, r_txt)):
                ax.text(x, row, txt, transform=ax.get_yaxis_transform(),
                        ha="right", va="center", fontsize=6.6, family="monospace")

        for x, label in ((1.10, "usable"), (1.26, "longest block"),
                         (1.40, "scoreable"), (1.55, "persistence")):
            ax.text(x, -0.5, label, transform=ax.get_yaxis_transform(),
                    ha="right", va="bottom", fontsize=6.4, fontweight="bold")

        # Group the rows by recording. Without this the sheet is 32 rows with no
        # indication that they come from four different nights, and the same
        # animal appears four times with no way to tell which row is which.
        seen_rec: dict[str, list[int]] = {}
        for row, card in enumerate(cards):
            seen_rec.setdefault(card.get("recording", "?"), []).append(row)
        for rec, rows_ in seen_rec.items():
            top, bot = min(rows_), max(rows_)
            if top > 0:
                ax.axhline(top - 0.5, color=F.C_INK, lw=0.8, alpha=0.45,
                           xmin=-0.30, clip_on=False)
            label = rec.replace("allego_", "").replace("__uid", "  uid")
            date = cards[rows_[0]].get("recording_date", "")
            ax.text(-0.30, (top + bot) / 2, f"{date}\n{label}",
                    transform=ax.get_yaxis_transform(), ha="right", va="center",
                    fontsize=6.4, fontweight="bold", color=F.C_INK,
                    linespacing=1.5)

        recordings = sorted({c.get("recording", "") for c in cards})
        criteria = sorted({c.get("criterion", "") for c in cards})
        fig.text(0.02, 0.965, f"COHORT SHEET   {cohort_id}", fontsize=11,
                 fontweight="bold", color=F.C_INK, va="top")
        n_rec = len(recordings)
        fig.text(0.02, 0.928,
                 f"{n} mouse recordings from {n_rec} "
                 f"{'night' if n_rec == 1 else 'nights'}. "
                 "Every mouse is checked by the same six questions, in order. "
                 "A question is only asked if the one before it passed.",
                 fontsize=7.2, color=F.C_INK, va="top")
        fig.text(0.02, 0.900,
                 "READ EACH ROW LEFT TO RIGHT. The first red box is what went "
                 "wrong for that mouse. Read a column downwards to see whether "
                 "the whole cohort failed the same way.",
                 fontsize=7.0, color=F.C_INK_SOFT, va="top")

        legend = "      ".join(
            f"{F.VERDICT_GLYPH[v]} {v} = {F.VERDICT_MEANING[v]}"
            for v in ("PASS", "PROVISIONAL", "INSUFFICIENT", "FAIL", "BLOCKED"))
        fig.text(0.02, 0.088, legend, fontsize=6.2, color=F.C_INK_SOFT, va="bottom")

        arms = [c.get("tether_arm", "") for c in cards]
        used = [k for k in ("A", "B", "C") if k in arms]
        if used:
            fig.text(0.02, 0.070,
                     "Tethers tested in this cohort:   "
                     + "      ".join(f"{TETHER_SHORT[k]} = {TETHER_NAME[k]}"
                                     for k in used),
                     fontsize=6.2, color=F.C_INK_SOFT, va="bottom")

        fig.text(0.02, 0.020,
                 '"Usable" means the mouse channel is measurably different from '
                 "amplifier inputs with no wire attached, recorded at the same "
                 "moment in the same file.\n"
                 '"Persistence" is how strongly the sleep or wake state at one '
                 "minute predicts the state a minute later; shuffled data scores "
                 "about zero.\n"
                 "The sleep column stays PROVISIONAL for every mouse until a "
                 "person has blind scored a set of clips and we can measure how "
                 "closely the automatic scoring matches a human.",
                 fontsize=6.0, color=F.C_INK_SOFT, va="bottom", linespacing=1.7)

        fig.text(0.98, 0.008,
                 f"method: {', '.join(c.upper() for c in criteria)} criterion, "
                 f"thresholds {cards[0].get('thresholds_hash', '?')}",
                 fontsize=5.0, color="#999999", va="top", ha="right")

        alt = (f"Cohort sheet for {cohort_id}: a matrix of {n} animal-recordings "
               f"by six verdict rungs. "
               + "; ".join(
                   f"{c.get('position')} {c.get('animal_id')} reaches rung "
                   f"{c.get('top_rung')}" for c in cards))

        report = F.export_figure(
            fig, str(out_stem), formats=["png", "pdf"], dpi=300,
            bbox_inches=None, facecolor="white", font_mode="truetype",
            overwrite=True, mkdir=True, write_manifest=True,
            provenance={"seed": F.SEED, "palette": F.PALETTE,
                        "style": f"{F.STYLE} (scientific-visualization skill asset)",
                        "alt_text": alt, "cohort": cohort_id,
                        "n_animal_recordings": n, "recordings": recordings,
                        "cards": [c.get("recording", "") + "__" + c.get("position", "")
                                  for c in cards]})
        plt.close(fig)
    print(f"wrote {out_stem}.png / .pdf   ({n} animal-recordings)")
    return report


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("indir", help="directory of card JSON files")
    ap.add_argument("--out", help="output stem")
    ap.add_argument("--recording", help="restrict to one recording")
    args = ap.parse_args(argv)

    indir = Path(args.indir)
    cards = load_cards(indir)
    if args.recording:
        cards = [c for c in cards if c.get("recording") == args.recording]
        if not cards:
            raise SystemExit(f"no cards for recording {args.recording}")
    cohort_id = cards[0].get("cohort_id", indir.name)
    stem = Path(args.out) if args.out else (
        indir / "figures" / f"{cohort_id}-cohort-sheet")
    render(cards, stem, cohort_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

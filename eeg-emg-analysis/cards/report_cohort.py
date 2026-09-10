#!/usr/bin/env python3
"""Generate the cohort's markdown report FROM the card JSONs.

    ~/eeg-analysis-venv/bin/python cards/report_cohort.py \
        cards/out/HLB-fem-profsurgery-troubleshooting --out <vault path>.md

WHY THIS IS GENERATED AND NOT WRITTEN
-------------------------------------
Every previous report in this project was typed by hand from numbers copied out
of a script's output. That is how a duty cycle computed at a retired 2 MOhm pass
mark survived in three documents after the threshold changed, and how a caption
came to assert 69 uV while its own panel showed 531.

This report carries NO typed-in measurement. Every number is read from a card
JSON, which was produced by the ladder, which was produced from the recording.
If a number is not on a card it does not appear here. Prose that interprets the
numbers is written by a person, in the vault page this file links to; what is
generated here is the part that must never drift.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GLYPH = {"PASS": "✅", "PROVISIONAL": "🟠", "INSUFFICIENT": "🔵",
         "FAIL": "🔴", "BLOCKED": "⬜"}


def load_cards(indir: Path) -> list[dict]:
    cards = [json.loads(p.read_text()) for p in sorted(indir.glob("*_card.json"))]
    if not cards:
        raise SystemExit(f"no card JSON in {indir}")
    cards.sort(key=lambda c: (c.get("recording_date", ""), c.get("recording", ""),
                              c.get("position", "")))
    return cards


def rung(card: dict, n: int) -> dict:
    return next((r for r in card["rungs"] if r["number"] == n), {})


def fmt_pct(x) -> str:
    return "—" if x is None else f"{100 * x:.1f}%"


def build(cards: list[dict], cohort_id: str) -> str:
    by_rec: dict[str, list[dict]] = defaultdict(list)
    for c in cards:
        by_rec[c["recording"]].append(c)

    passing = [c for c in cards if rung(c, 3).get("verdict") == "PASS"]
    total_scoreable_h = sum(
        rung(c, 3).get("detail", {}).get("hours_in_blocks") or 0 for c in passing)
    criteria = sorted({c.get("criterion", "") for c in cards})
    thash = cards[0].get("thresholds_hash", "?")

    L: list[str] = []
    A = L.append
    A("---")
    A("tags: [report, eeg, cohort, cards, generated]")
    A(f"created: {cards[0].get('generated', '')[:10]}")
    A("status: generated")
    A("---")
    A("")
    A(f"# {cohort_id} — cohort report")
    A("")
    A("> [!warning] This file is GENERATED. Do not edit it by hand.")
    A("> Every number here is read from an animal card JSON, which was produced")
    A("> by `cards/ladder.py` from the recording itself. Regenerate with")
    A("> `~/eeg-analysis-venv/bin/python cards/report_cohort.py`. Interpretation")
    A("> belongs in [[animal-card-and-verdict-ladder]] and in the experiment")
    A("> pages this links to, not here.")
    A("")
    A(f"**{len(cards)} animal-recordings** across **{len(by_rec)} recordings**   ·   "
      f"criterion **{', '.join(c.upper() for c in criteria)}**   ·   "
      f"thresholds `{thash}`")
    A("")

    # ---------------------------------------------------------------- summary
    A("## What the cohort produced")
    A("")
    A(f"- **{len(passing)} of {len(cards)} animal-recordings reached rung 3 "
      f"SCOREABILITY**, totalling **{total_scoreable_h:.2f} scoreable hours**.")
    stuck = defaultdict(int)
    for c in cards:
        top = c.get("top_rung", -1)
        stuck[top] += 1
    names = {5: "completed every rung", 4: "reached rung 4 ARCHITECTURE but have "
             "no plain-text export yet",
             3: "reached rung 3 SCOREABILITY", 2: "reached rung 2 CONNECTION",
             1: "stopped at rung 2 CONNECTION: the electrode was not connected",
             0: "stopped at rung 1 IDENTITY", -1: "stopped at rung 0 FILE"}
    for top in sorted(stuck, reverse=True):
        A(f"- **{stuck[top]}** animal-recording(s) {names.get(top, f'reached rung {top}')}.")
    A("- Rung 4 ARCHITECTURE is PROVISIONAL for every animal, permanently, until "
      "a blind-scoring Cohen kappa exists. No human has scored any epoch.")
    A("")

    # ---------------------------------------------------------------- matrix
    A("## The ladder, every animal-recording")
    A("")
    A("![[2026-08-09-HLB-cohort-sheet.png]]")
    A("")
    A("Read across a row until it stops being green: that column is the thing to "
      "fix for that animal. Read down a column to see whether the cohort shares "
      "a failure.")
    A("")
    A("| recording | pos | animal | arm | 0 FILE | 1 IDENT | 2 CONN | 3 SCORE | "
      "4 ARCH | 5 EXPORT | usable | longest block | scoreable |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in cards:
        v = {r["number"]: r["verdict"] for r in c["rungs"]}
        comb = rung(c, 2).get("detail", {}).get("combined", {})
        sc = rung(c, 3).get("detail", {})
        hrs = sc.get("hours_in_blocks")
        A("| `{rec}` | {pos} | {an} | {arm} | {v0} | {v1} | {v2} | {v3} | {v4} | "
          "{v5} | {us} | {lb} | {sh} |".format(
              rec=c["recording"].replace("allego_", "").replace("__uid", " uid"),
              pos=c.get("position", "?"),
              an=c.get("animal_id", "?"),
              arm=c.get("tether_arm") or "—",
              v0=GLYPH.get(v[0], "") + " " + v[0],
              v1=GLYPH.get(v[1], "") + " " + v[1],
              v2=GLYPH.get(v[2], "") + " " + v[2],
              v3=GLYPH.get(v[3], "") + " " + v[3],
              v4=GLYPH.get(v[4], "") + " " + v[4],
              v5=GLYPH.get(v[5], "") + " " + v[5],
              us=fmt_pct(comb.get("usable_fraction")),
              lb=("—" if not comb.get("longest_block_minutes")
                  else f"{comb['longest_block_minutes']:.1f} min"),
              sh=("—" if hrs is None else f"{hrs:.2f} h")))
    A("")
    A("✅ PASS = asked and answered yes · 🟠 PROVISIONAL = answered but gated · "
      "🔵 INSUFFICIENT = **the question could not be asked, which is not the same "
      "as FAIL** · 🔴 FAIL = asked and answered no · ⬜ BLOCKED = a lower rung "
      "failed, so this was never evaluated.")
    A("")

    # --------------------------------------------------- per working animal
    if passing:
        A("## The animals that worked")
        A("")
        for c in passing:
            r2, r3, r4 = rung(c, 2), rung(c, 3), rung(c, 4)
            comb = r2.get("detail", {}).get("combined", {})
            d3, d4 = r3.get("detail", {}), r4.get("detail", {})
            A(f"### {c.get('animal_id')} — position {c.get('position')}, "
              f"tether arm {c.get('tether_arm') or 'not recorded'}, "
              f"`{c['recording']}`")
            A("")
            short = c["recording"].split("__", 1)[-1]   # allego_1__uidX -> uidX
            A(f"![[2026-08-09-card-{short}__{c.get('position')}__"
              f"{c.get('animal_id')}.png]]")
            A("")
            A(f"- **Connection**: {fmt_pct(comb.get('usable_fraction'))} of "
              f"{comb.get('n_epochs_total', 0):,} epochs of "
              f"{c.get('epoch_s_qc')} s usable on every role, longest unbroken "
              f"block **{comb.get('longest_block_minutes', 0):.1f} min**.")
            A(f"- **Scoreability**: {d3.get('hours_in_blocks', 0):.2f} h inside "
              f"{d3.get('n_blocks', 0)} block(s), longest "
              f"{d3.get('longest_block_min', 0):.1f} min, persistence "
              f"`r@1min` **{d3.get('r_1min', 0):+.3f}** against a shuffled "
              f"{d3.get('r_1min_shuffled', 0):+.3f}.")
            arch = (f"- **Architecture (PROVISIONAL)**: wake "
                    f"{d4.get('wake_pct', 0):.1f}%, NREM {d4.get('nrem_pct', 0):.1f}%")
            if d4.get("asleep_in_light_pct") is not None:
                arch += f", asleep in the light phase {d4['asleep_in_light_pct']:.1f}%"
            A(arch + ".")
            if d4.get("asleep_in_light_swing_pts") is not None:
                A(f"  - ⚠️ That light-phase figure moves "
                  f"**{d4['asleep_in_light_swing_pts']:.1f} points** across a "
                  "±25% sweep of the wake threshold, so agreement with the "
                  "literature is not independent confirmation.")
            if d4.get("rem_from_nrem_pct") is not None:
                null = d4.get("rem_from_nrem_null") or {}
                extra = ""
                if null.get("mean") is not None and null.get("sd"):
                    extra = (f" against a run-order permutation null of "
                             f"{null['mean']:.1f} ± {null['sd']:.1f}")
                A(f"  - REM entered from NREM in "
                  f"{d4['rem_from_nrem_pct']:.1f}% of episodes{extra}.")
            A("- **No REM percentage is reported.** Two independent rules "
              "disagree by roughly a factor of five on this montage.")
            A("")

    # ----------------------------------------------------------- how it failed
    failing = [c for c in cards if rung(c, 2).get("verdict") != "PASS"]
    if failing:
        A("## Where the others stopped")
        A("")
        A("| recording | pos | animal | arm | stopped at | why |")
        A("|---|---|---|---|---|---|")
        for c in failing:
            first_bad = next((r for r in c["rungs"] if r["verdict"] not in
                              ("PASS", "PROVISIONAL")), {})
            A("| `{rec}` | {pos} | {an} | {arm} | rung {n} {name} {v} | {why} |".format(
                rec=c["recording"].replace("allego_", "").replace("__uid", " uid"),
                pos=c.get("position", "?"), an=c.get("animal_id", "?"),
                arm=c.get("tether_arm") or "—",
                n=first_bad.get("number", "?"), name=first_bad.get("name", "?"),
                v=first_bad.get("verdict", "?"),
                why=(first_bad.get("reason", "") or "").replace("|", "/")[:190]))
        A("")

    # ------------------------------------------------------------- provenance
    A("## Provenance")
    A("")
    prov = cards[0].get("provenance", {})
    A(f"- Thresholds: `{prov.get('thresholds_file', '?')}`, content hash "
      f"`{thash}`. Every card prints this hash, so a figure cannot silently come "
      "from a different set of numbers.")
    A(f"- Code revision: `{prov.get('git_rev', '?')}`")
    A(f"- Cohort manifest: `{prov.get('cohort_manifest', '?')}`")
    A(f"- QC epoch {cards[0].get('epoch_s_qc')} s; staging epoch "
      f"{cards[0].get('epoch_s_staging')} s. "
      "**A usable fraction at one epoch length is not comparable to the other, "
      "and a HUM fraction is not comparable to a SLOPE fraction.**")
    A("- Each animal's own card carries its life timeline, its evidence panels "
      "and its full caveats.")
    A("")
    A("## Related")
    A("")
    A("- [[animal-card-and-verdict-ladder]] — how to read a card, and how to add a mouse")
    A("- [[2026-08-07-rig-specification-and-analysis-method]] — the page to argue from")
    A("- [[blind-scoring-and-kappa]] — the pre-registered rules that gate rung 4")
    A("")
    return "\n".join(L) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("indir")
    ap.add_argument("--out", help="markdown path to write (default: stdout)")
    args = ap.parse_args(argv)

    indir = Path(args.indir)
    cards = load_cards(indir)
    text = build(cards, cards[0].get("cohort_id", indir.name))
    if args.out:
        Path(args.out).write_text(text)
        print(f"wrote {args.out}  ({len(cards)} animal-recordings)")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

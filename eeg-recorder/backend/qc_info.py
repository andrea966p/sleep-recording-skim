#!/usr/bin/env python3
"""qc_info.py -- the QC verdict that travels INSIDE each mouse's info.json.

WHY. The per-mouse CSV on the NAS holds EEG and EMG only. The wire-free control
inputs this project judges every channel against were in the 262-channel raw file
and are gone from the CSV by design, so anyone reading the CSV alone cannot check
the connection. The verdict the ladder reached -- against that mouse's own chip's
wire-free floor, on the same hours -- is therefore written next to the data.

The block is a SUMMARY of an animal card (cards/ladder.py), never a second
computation: every number here is copied from the card, whose path is recorded.

    info.json["qc"] = {
      "verdict": "SCOREABLE" | "NOT SCOREABLE" | "NO VERDICT" | "NOT ASSESSED",
      "why": one sentence,
      "rungs": [{number, name, verdict, headline}, ...],
      "connection": strict EEG+EMG fraction, longest block, per-role fractions,
      "floor": the chip's wire-free control: grounded? valid? threshold,
      "sleep_structure": r@1min, hours in blocks  (rung 3),
      "stage3": staging result when the ladder could not reach rung 3,
      "card": path, generated, thresholds_hash, git_rev, judged_on
    }
"""
from __future__ import annotations

import json
from pathlib import Path

HOW_TO_READ = (
    "SCOREABLE = passed file, identity, connection (EEG and EMG usable in the same "
    "10 s epochs, judged against this chip's own wire-free inputs, with an unbroken "
    "block of at least 15 min) and scoreability (within-block r@1min > 0.30). "
    "NOT SCOREABLE = a rung failed. NO VERDICT = the chip's wire-free control was "
    "itself unusable (ungrounded, or carrying signal), so the connection could not be "
    "judged; this is NOT a failure of the animal -- see `stage3`.")


def _pct(x):
    return None if x is None else round(100.0 * float(x), 1)


def qc_block(card: dict, *, card_path: str | None = None, judged_on: str = "",
             stage3: dict | None = None) -> dict:
    rungs = {r["number"]: r for r in card.get("rungs", [])}
    r2, r3 = rungs.get(2, {}), rungs.get(3, {})
    d2 = r2.get("detail") or {}
    comb, per = d2.get("combined") or {}, d2.get("per_role") or {}
    fl = d2.get("floor") or card.get("floor") or {}

    v2, v3 = r2.get("verdict"), r3.get("verdict")
    first_bad = next((r for n, r in sorted(rungs.items())
                      if n <= 3 and r.get("verdict") not in ("PASS",)), None)
    if v3 == "PASS":
        verdict, why = "SCOREABLE", r3.get("headline", "")
    elif first_bad and first_bad.get("verdict") == "UNJUDGEABLE":
        verdict = "NO VERDICT"
        why = f"rung {first_bad['number']} {first_bad['name']}: {first_bad.get('headline', '')}"
    elif first_bad:
        verdict = "NOT SCOREABLE"
        why = (f"rung {first_bad['number']} {first_bad['name']} {first_bad.get('verdict')}: "
               f"{first_bad.get('headline') or first_bad.get('reason', '')}")
    else:
        verdict, why = "NOT ASSESSED", "no rung verdicts on the card"

    out = {
        "verdict": verdict,
        "why": why,
        "top_rung": card.get("top_rung"),
        "rungs": [{"number": n, "name": r.get("name"), "verdict": r.get("verdict"),
                   "headline": r.get("headline", "")} for n, r in sorted(rungs.items())],
        "connection": {
            "verdict": v2,
            "eeg_and_emg_usable_pct": _pct(comb.get("usable_fraction")),
            "usable_hours": comb.get("usable_hours"),
            "longest_unbroken_block_min": comb.get("longest_block_minutes"),
            "eeg_usable_pct": _pct((per.get("eeg") or {}).get("usable_fraction")),
            "emg_usable_pct": _pct((per.get("emg") or {}).get("usable_fraction")),
            "epoch_s": comb.get("epoch_s"),
            "criterion": comb.get("criterion") or card.get("criterion"),
            "threshold": r2.get("threshold"),
        },
        "floor": {
            "what": "wire-free amplifier inputs on this mouse's own chip, recorded in the "
                    "same file -- the negative control every channel is judged against",
            "n_wire_free_inputs": fl.get("n_sites"),
            "grounded": fl.get("grounded"),
            "hum_60hz_median_uv": fl.get("hum_median"),
            "slope_threshold_p1": fl.get("slope_p1"),
            "slope_valid": fl.get("slope_valid"),
            "problem": fl.get("validity_reason") or fl.get("slope_validity_reason") or "",
        },
        "sleep_structure": {
            "verdict": v3,
            "r_1min": (r3.get("detail") or {}).get("r_1min"),
            "hours_in_blocks": (r3.get("detail") or {}).get("hours_in_blocks"),
            "wake_pct": (r3.get("detail") or {}).get("wake_pct"),
            "threshold": r3.get("threshold"),
            "reasons": (r3.get("detail") or {}).get("reasons", []),
        },
        "how_to_read": HOW_TO_READ,
        "card": {"path": card_path, "generated": card.get("generated"),
                 "thresholds_hash": card.get("thresholds_hash"),
                 "git_rev": (card.get("provenance") or {}).get("git_rev"),
                 "judged_on": judged_on,
                 "window": card.get("window")},
    }
    if stage3 is not None:
        p = (stage3.get("persistence") or {}).get("1min") or {}
        out["stage3"] = {
            "what": "sleep staging on stage 1's own absolute QC gate (no wire-free floor); "
                    "reported because the ladder could not reach rung 3",
            "verdict": stage3.get("verdict"), "r_1min": p.get("r"),
            "hours_in_blocks": stage3.get("hours_in_blocks"),
            "wake_pct": stage3.get("wake_pct")}
    return out


def load_card(path: str | Path) -> dict | None:
    p = Path(path)
    return json.loads(p.read_text()) if p.is_file() else None

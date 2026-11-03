"""Final tiers of the 2026-11 HLB re-score: the screen's tier, demoted where the agent review gave evidence.

Review evidence only ever DEMOTES a window (a promotion needs a re-fit in score.py, not a hand edit).
An override applies only if the screen still gives its `from` tier; otherwise it is reported and skipped.
Usage: final_tiers.py BACKBONE OUT_JSON   (BACKBONE built without final tiers, so `tier` = the screen's)
"""
import json, sys
from pathlib import Path

import pandas as pd

OVERRIDES = {  # stem: (from, to, why) -- evidence in REVIEW/review_result.json
    "HLBSSD12_B": ("A", "B", "exactly 20 h; dark ZT18-24 EEG railed, ZT23 kept only by the all-wake exemption (skeptic + critic)"),
    "HLBSSL38_R": ("A", "B", "exactly 20 h; tier B with the ss60 EMG; weakest delta separation of the A set, AUC 0.79-0.80 (skeptic + critic)"),
    "HLBWSL26_B": ("A", "B", "A only through the ss60 switch at exactly 20 h; the primary gap EMG gives B; EEG carries 124 uV mains (reviewer + skeptic + critic)"),
    "HLBSSD11_R": ("C", "X", "EEG does not track state: 1-min log delta vs EMG r = -0.02 (baseline -0.74); EEG-only HMM calls 39 % of EMG wake NREM (skeptic)"),
    "HLBSSD12_R": ("C", "X", "C rests on exactly 6 light hours incl. ZT6/8/9 with flat 400-500 uV EMG plateaus and a 16-20 Hz technical band (skeptic)"),
    "HLBSSD16_R": ("C", "X", "intermittent EEG contact (lost ZT7-8, mostly lost ZT15-18, 16-20 Hz band ZT6.8-9); C exactly on its 6-light-hour bar (skeptic)"),
    "HLBSSD17_R": ("C", "X", "EEG-only HMM split off the delta-railing cluster (NR state ln delta 11.3 vs 7.0), not NREM (reviewer + skeptic)"),
}


def main(B: Path, out: Path):
    rec = pd.read_csv(B / "recordings.csv")
    final = {}
    for r in rec.itertuples():
        stem = f"{r.mouse}_{r.tp}"
        final[stem] = {"tier": r.tier, "why": "screen"}
        if stem in OVERRIDES:
            frm, to, why = OVERRIDES[stem]
            if r.tier == frm:
                final[stem] = {"tier": to, "why": f"review: {frm} -> {to}: {why}"}
            else:
                print(f"{stem}: override {frm}->{to} skipped, screen now gives {r.tier}")
    out.write_text(json.dumps(final, indent=1))
    moved = {k: v for k, v in final.items() if v["why"] != "screen"}
    print(f"{len(final)} windows, {len(moved)} moved by review:", ", ".join(f"{k} {v['tier']}" for k, v in moved.items()))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))

"""Markdown tables for the vault overview note, from the backbone and the final tiers. Usage:
overview_tables.py BACKBONE FINAL_TIERS_JSON > tables.md"""
import json, sys
from pathlib import Path

import pandas as pd

ARMS = [("HLBWSD", "W-SD: water + sleep deprivation"), ("HLBSSD", "S-SD: SOD1 + sleep deprivation"),
        ("HLBWSL", "W-SL: water, ad libitum"), ("HLBSSL", "S-SL: SOD1, ad libitum")]
OLD = {"SCOREABLE": "✅", "NOT SCOREABLE": "❌", "NO VERDICT": "❔"}
EMO = {"A": "🟢 A", "B": "🟢 B", "C": "🟡 C", "D": "🟠 D", "X": "🔴 X", None: "–"}


def main(B: Path, F: Path):
    rec = pd.read_csv(B / "recordings.csv")
    final = json.loads(F.read_text())
    out = []
    tot = {"old": 0, "new": 0}
    for b, title in ARMS:
        r = rec[rec.batch == b]
        out += [f"### {title}", "",
                "| mouse | rig | baseline | recovery | paired W/NR/R | old (B / R) | usable h, B / R (L+D) | EMG |",
                "|---|---|---|---|---|---|---|---|"]
        for m in sorted(r.mouse.unique()):
            q = {tp: r[(r.mouse == m) & (r.tp == tp)] for tp in ("B", "R")}
            t = {tp: final.get(f"{m}_{tp}", {}).get("tier") for tp in ("B", "R")}
            paired = t["B"] in ("A", "B") and t["R"] in ("A", "B")
            oldp = all(not q[tp].empty and q[tp].iloc[0].old_qc == "SCOREABLE" for tp in ("B", "R"))
            tot["old"] += oldp; tot["new"] += paired
            def hrs(tp):
                if q[tp].empty: return "–"
                x = q[tp].iloc[0]; return f"{x.hours_both_ok} ({x.hours_both_ok_light}+{x.hours_both_ok_dark})"
            src = "/".join(sorted({q[tp].iloc[0].emg_source for tp in ("B", "R") if not q[tp].empty}))
            pos = (q["B"] if not q["B"].empty else q["R"]).iloc[0].position
            out.append(f"| [[hlb-eeg-{m.lower()}\\|{m}]] | {pos} | {EMO[t['B']]} | {EMO[t['R']]} | {'**yes**' if paired else 'no'} | "
                       f"{OLD.get(q['B'].iloc[0].old_qc, '–') if not q['B'].empty else '–'} / "
                       f"{OLD.get(q['R'].iloc[0].old_qc, '–') if not q['R'].empty else '–'} | {hrs('B')} / {hrs('R')} | {src} |")
        out.append("")
    out.append(f"Paired W/NR/R mice: old pipeline {tot['old']}, re-score {tot['new']}.")
    print("\n".join(out))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))

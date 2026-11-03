"""Writes one vault note per HLB EEG mouse from the re-score (2026-11-03), plus its overview figures.

Inputs: BACKBONE/recordings.csv, REVIEW/review_result.json (the agent review: scorer reviews, skeptic
verdicts), REVIEW/<MOUSE>_<B|R>_overview.png. Outputs: VAULT/10-projects/hlb-sod1/eeg-sleep/mice/hlb-eeg-<mouse>.md
and VAULT/_attachments/2026-11-03-hlb-eeg-<mouse>-<b|r>-overview.png. The `decision` line of each note is
computed here from the final tier (after the review), so the notes and the overview table never disagree.
Usage: mouse_notes.py BACKBONE REVIEW VAULT
"""
import json, shutil, sys
from pathlib import Path

import pandas as pd

ARM = {"HLBWSD": "W-SD (water, sleep deprivation)", "HLBSSD": "S-SD (SOD1, sleep deprivation)",
       "HLBWSL": "W-SL (water, ad libitum)", "HLBSSL": "S-SL (SOD1, ad libitum)"}
USE = {"A": "W / NR / R, whole window", "B": "W / NR / R on the usable hours", "C": "NREM from the EEG alone",
       "D": "sleep vs wake from the EMG alone", "X": "nothing", None: "no recording"}


TABLE = [("screen tier (before review)", "tier_screen", 0), ("hours usable, EEG + EMG", "hours_both_ok", 0),
         ("… of them light", "hours_both_ok_light", 0), ("… of them dark", "hours_both_ok_dark", 0),
         ("hours usable, EEG alone", "hours_eeg_ok", 0), ("hours usable, EMG alone", "hours_emg_ok", 0),
         ("EMG separability η (gap; ≥ 0.70)", "eta_gap", 3), ("η, SleepStager 20–90 Hz EMG", "eta_ss60", 3),
         ("δ AUC, NR vs W (≥ 0.75)", "auc_delta_recording", 3), ("EEG median log10 δ (2–4)", "eeg_median_log10_delta", 2),
         ("EEG-alone state changes / h (≥ 5)", "eeg_only_switches_per_h", 1), ("κ rule vs HMM", "kappa_rule_hmm", 2),
         ("κ NREM, rule vs EEG alone", "kappa_nrem_rule_vs_eeg_only", 2), ("κ rule, gap vs 20–90 Hz EMG", "kappa_gap_ss60", 2),
         ("artifact epochs %", "artifact_pct", 1), ("EEG 60 Hz, median µV", "eeg_line60_med_uv", 0),
         ("EMG 60 Hz, median µV", "emg_line60_med_uv", 0), ("wake % light (rule)", "wake_pct_light", 1),
         ("wake % dark (rule)", "wake_pct_dark", 1), ("NREM % light, EEG alone", "nrem_pct_light_eeg_only", 1),
         ("NREM % dark, EEG alone", "nrem_pct_dark_eeg_only", 1), ("sleep % light, EMG alone", "sleep_pct_light_emg_only", 1),
         ("sleep % dark, EMG alone", "sleep_pct_dark_emg_only", 1), ("r@1min (project definition)", "r_1min", 3),
         ("old verdict reason", "old_qc_why", 0)]


def fmt(v, d=1):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "–"
    return f"{v:.{d}f}" if isinstance(v, float) else str(v)


def main(B: Path, RV: Path, V: Path):
    rec = pd.read_csv(B / "recordings.csv")
    rv = json.loads((RV / "review_result.json").read_text())
    reviews = {(r["mouse"], r["tp"]): r for r in rv["reviews"]}
    verdicts = {(v["mouse"], v["tp"]): v for v in rv["verdicts"]}
    final = json.loads((RV / "final_tiers.json").read_text())       # {"MOUSE_B": {"tier":..,"why":..}}
    outdir = V / "10-projects/hlb-sod1/eeg-sleep/mice"; outdir.mkdir(parents=True, exist_ok=True)
    for mouse, g in rec.groupby("mouse"):
        r0 = g.iloc[0]
        rows = {tp: g[g.tp == tp].iloc[0] if (g.tp == tp).any() else None for tp in ("B", "R")}
        ft = {tp: final.get(f"{mouse}_{tp}", {}) for tp in ("B", "R")}
        tiers = {tp: ft[tp].get("tier") for tp in ("B", "R")}
        paired = all(tiers[tp] in ("A", "B") for tp in ("B", "R"))
        lines = [
            "---", "type: reference", "area: hlb-sod1", "status: active", "created: 2026-11-03",
            f'summary: "{mouse}: EEG re-score 2026-11, baseline tier {tiers["B"] or "–"}, recovery tier {tiers["R"] or "–"}"',
            f"tags: [eeg, hlb, mouse, {r0.batch.lower()}]", "---", "",
            f"# {mouse}: {ARM[r0.batch]}, rig {r0.position}", "",
            "> [!abstract] Decision (2026-11-03 re-score)",
            f"> - **Baseline:** tier **{tiers['B'] or '–'}** → {USE[tiers['B']]}. {ft['B'].get('why', '')}",
            f"> - **Recovery:** tier **{tiers['R'] or '–'}** → {USE[tiers['R']]}. {ft['R'].get('why', '')}",
            f"> - **Paired W/NR/R (both windows A or B):** {'yes' if paired else 'no'}.",
            "> - Old pipeline: baseline " + (f"{rows['B'].old_qc}" if rows['B'] is not None else "–")
            + ", recovery " + (f"{rows['R'].old_qc}" if rows['R'] is not None else "–") + ".",
            "", "Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]", "",
            "## Numbers", "",
            "| | baseline | recovery |", "|---|---|---|",
        ]
        for label, key, d in TABLE:
            vals = [fmt(rows[tp].get(key), d) if rows[tp] is not None else "–" for tp in ("B", "R")]
            lines.append(f"| {label} | {vals[0]} | {vals[1]} |")
        lines += ["", "REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.", ""]
        for tp, name in (("B", "Baseline"), ("R", "Recovery")):
            if rows[tp] is None:
                continue
            fig = f"2026-11-03-hlb-eeg-{mouse.lower()}-{tp.lower()}-overview.png"
            src = RV / f"{mouse}_{tp}_overview.png"
            if src.exists():
                shutil.copyfile(src, V / "_attachments" / fig)
            lines += [f"## {name}", "", f"![[{fig}]]", ""]
            rw = reviews.get((mouse, tp))
            if rw:
                lines += ["*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*", ""]
                lines += [f"**Agent scorer:** EEG {rw['eeg_quality']}, EMG {rw['emg_quality']}; rule follows the EEG: "
                          f"{rw['rule_follows_eeg']}; tier {'agreed' if rw['tier_agree'] else 'disputed → ' + rw['proposed_tier']}.",
                          f"Plausibility: {rw['plausibility']}", f"Concerns: {rw['concerns'] or 'none'}", ""]
                if rw["epochs"]:
                    lines += ["| panel | epoch | agent call | conf. | agrees with | why |", "|---|---|---|---|---|---|"]
                    for e in rw["epochs"]:
                        lines.append(f"| {e['panel']} | {e['epoch']} | {e['call']} | {e['confidence']} | {e['agrees_with']} | "
                                     f"{e['reason'].replace('|', '/')} |")
                    lines += ["", f"Traces: `~/sleep-data/hlb-rescore-2026-11/review/{mouse}_{tp}_epochs.png`.", ""]
            vd = verdicts.get((mouse, tp))
            if vd:
                lines += [f"**Skeptic (tried to refute the rescue):** {vd['verdict'].replace('_', ' ')}, tier {vd['recommended_tier']}. "
                          f"Strongest objection: {vd['strongest_objection']} Checked: {vd['evidence_checked']}", ""]
        (outdir / f"hlb-eeg-{mouse.lower()}.md").write_text("\n".join(lines) + "\n")
    print(f"{rec.mouse.nunique()} mouse notes -> {outdir}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))

---
name: hlb-eeg-rescore-2026-11
description: "2026-11-03 HLB EEG re-score supersedes the 09-30 scoreable counts and the 10-06 2x2: 15 paired mice; where it lives and the rules for touching it"
metadata:
  type: project
---

2026-11-03: all 64 HLB EEG windows re-scored (SleepStager rule on the gap EMG, HMM second scorer,
tiers A-X, agent review). Vault: `hlb-eeg-sleep-overview` (results, every mouse), method
`hlb-eeg-scoring-method-2026-11`, backbone `hlb-eeg-data-backbone`, runbook `hlb-eeg-compute-runbook`.
Code `eeg-emg-analysis/rescore_2026_11/`; data `~/sleep-data/hlb-rescore-2026-11/` on the ThinkPad only.

**Why:** the old rung 2 / stage 3 screen rejected good mice (60 Hz EMG); paired went 3 -> 15.

**How to apply:**
- Quote paired counts and SOD1 results from the overview, not from [[s-sl-has-sleep-data-n3]] or [[sod1-sleep-eeg-2x2-2026-10-06]].
- Review evidence may only DEMOTE a tier (`final_tiers.py` OVERRIDES); a promotion needs a re-fit in `score.py`.
- HLBSSD18 R's recovery gain (+18 pts) is +1.5 with EMG-rail epochs as wake: never present S-SD vs W-SD.
- Human check (11-03, workstation backup drive PCBACKUP): HLBSSL33 R reviewed to 8441 (light only, rule-anchored) gives κ 0.952, HMM 0.930; dark ZT12–15 (10801–13624) κ 0.941, HMM 0.886; late dark 16201–19028 κ 0.932 (re-score sleep % +2 pts there). Rule-vs-HMM list caught 1/3 of dark corrections: don't recommend it. Blind scoring still unchecked.

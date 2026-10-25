---
name: hlbnsl-behavior-videos-pointer
description: "HLBNSL behaviour videos (Y-maze/OFT/NOR, EthoVision) - frozen rules live in nanotag/analysis/behavior/BEHAVIOR_SOP.md; state as of 2026-10-24"
metadata:
  node_type: memory
  type: project
  originSessionId: e1750394-a24d-4741-8e59-ba1a27f08264
  modified: 2026-10-24T13:02:49.349Z
---

Behaviour video analysis for the nanotag batches is governed by `nanotag/analysis/behavior/BEHAVIOR_SOP.md`
(written 2026-10-20 on the workstation; `prep.py`, `metrics.py` beside it). Read it before any EthoVision/BORIS step.

State 2026-10-24 (later): on `kaist-bilab-win` the 36 originals in `Desktop\Nanotag videos\` are renamed to mouse IDs
(undo: `rename_log.csv`); upright CFR copies with ID names for all 36 (verified) in
`Desktop\Nanotag videos upright\<test>\videos\` (Y-maze libx264, OFT/NOR h264_nvenc). Y-maze cut
to 480 s from door closed in `Y-maze\trial_8min\`; OFT/NOR (600 s) not cut yet.
🛑 Run order is 41,42,44,49,45,46,47,48,50 (SOD1 first), NOT ascending: the first rename was wrong
for 45-49 and was fixed 10-24 (Andrea read the mouse cards). Never assume run order from IDs.
(`prep.py convert --keep-names`). EthoVision tracking is deliberately NOT blinded (Andrea); BORIS NOR still blinded.
Not trimmed yet. Clicking guide: vault `ethovision-11-5-y-maze-tracking`.
Workstation (in repair) Claude memory + transcripts copied to `~/workstation-backup/` on e10 (videos excluded).

**Why:** the workstation's own memory (`hlbnsl-behavior-videos`) is not on e10, and the SOP is easy to miss.
**How to apply:** batch 2 (HLBNSD) Y-maze is 2026-10-31: SOP says pull the camera back so all arm ends are in frame.
Keep behaviour findings separate from EEG and nanotag ([[feedback-sod1-eeg-nanotag-separate]]).

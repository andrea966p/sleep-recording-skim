---
name: hlbnsl-behavior-videos-pointer
description: "HLBNSL behaviour videos (Y-maze/OFT/NOR, EthoVision) - frozen rules live in nanotag/analysis/behavior/BEHAVIOR_SOP.md; state as of 2026-10-24"
metadata:
  node_type: memory
  type: project
  originSessionId: e1750394-a24d-4741-8e59-ba1a27f08264
  modified: 2026-10-24T08:59:22.176Z
---

Behaviour video analysis for the nanotag batches is governed by `nanotag/analysis/behavior/BEHAVIOR_SOP.md`
(written 2026-10-20 on the workstation; `prep.py`, `metrics.py` beside it). Read it before any EthoVision/BORIS step.

State 2026-10-24: all 36 HLBNSL videos are on Andrea's office Windows PC (EthoVision). Rotation (-90 in metadata)
not baked in, not trimmed, not blinded; `prep.py convert` never ran on the batch. EthoVision settings table still blank.
Workstation (in repair) Claude memory + transcripts copied to `~/workstation-backup/` on e10 (videos excluded).

**Why:** the workstation's own memory (`hlbnsl-behavior-videos`) is not on e10, and the SOP is easy to miss.
**How to apply:** batch 2 (HLBNSD) Y-maze is 2026-10-31: SOP says pull the camera back so all arm ends are in frame.
Keep behaviour findings separate from EEG and nanotag ([[feedback-sod1-eeg-nanotag-separate]]).

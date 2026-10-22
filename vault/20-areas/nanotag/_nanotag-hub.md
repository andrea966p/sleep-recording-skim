---
type: hub
area: nanotag
status: active
created: 2026-10-22
summary: "The Kissei nanotag method: device facts, programming, NFC read-out, NAS upload and sleep analysis; the studies that use it live in project hlb-sod1"
tags: [hub, nanotag, kissei, activity]
---

# Nanotag

## What this is

The second recording method of the lab: a 2.7 g Kissei nano tag (VSMN 210) implanted under the skin, logging 12 s activity
cross counts (and optionally temperature), read out by NFC, with sleep inferred from immobility. No EEG, no rig.
This area holds the device facts and the procedure; the studies (HLBNSL, NS-SD / NW-SD) are in project [[_hlb-sod1-hub]].

## Current state

- 2026-10-22: The NS-SD / NW-SD batch (10 mice, tags 51-60, 12 s activity, no temperature) is scheduled to start tag Run 1 on 2026-10-22 09:00; sampling is Thu 2026-11-05; no data read yet. [[2026-10-19-NS-SD-NW-SD-nanotag-study]]
- 2026-10-16: 12 s activity without temperature holds 9 days, not 20: the English manual misprints it, the Japanese manual and nanotagViewer say 9. [[nanotag-recording-and-analysis]]
- 2026-10-05: HLBNSL Run 1 + Run 2 merged: no detectable SOD1 effect on sleep (793 ± 21 vs 768 ± 39 min/day, p = 0.61). [[2026-10-05-HLBNSL-nanotag-merged-analysis]]
- 2026-10-05: The nanotag code moved into the repo (`nanotag/analysis/`) and HLBNSL's 98 files were uploaded and verified on the SKIM NAS; no off-site copy was recorded. [[nanotag-recording-and-analysis]]

## Start here

1. [[nanotag-recording-and-analysis]]: the workflow from programming the tag to the report (canonical)
2. [[nanotag-kissei-device-and-literature]]: what the tag measures, its limits, the English-manual errors, the literature
3. [[2026-10-19-NS-SD-NW-SD-nanotag-study]]: the running study and its schedule
4. [[2026-10-05-HLBNSL-nanotag-merged-analysis]]: the finished study, as the worked example
5. [[sod1-sheet-change-log-workflow]]: how changes to the study sheet are requested

## Rules that must not be broken

- 🛑 Report nanotag findings on their own, never pooled with EEG and never "the nanotag agrees". [[2026-10-06-eeg-and-nanotag-findings-reported-separately]]
- 🛑 Starting a recording or setting a reservation erases the tag; reading never does. Read first. [[nanotag-kissei-device-and-literature]]
- 🛑 Never restrain a mouse on the metal grid for a read; read from the open hand and stop if it will not settle (HLBNSSL43 died 2026-09-28). [[nanotag-recording-and-analysis]]
- Plan every read before the memory is full (8 days with temperature, 9 days without). [[nanotag-recording-and-analysis]]
- Claude Code never edits the study sheet; changes go through the `Pending changes instructions` tab. [[sod1-sheet-change-log-workflow]]
- The SKIM NAS is a working copy, not a backup. [[backup-architecture]]

## Open items

- Raw nanotag data exists only on the workstation Desktop and the SKIM NAS; no off-site copy is recorded. [[nanotag-recording-and-analysis]]
- `cohort.py` still needs the NS-SD blocks and an `SD` window list before analysis (cohort.py has no SD block as of 2026-10-22). [[2026-10-16]]
- Anchor the tag next time: HLBNSL tags migrated from the neck to the right flank, a site Kissei has not validated. [[nanotag-recording-and-analysis]]
- Nobody has validated the nanotag against EEG in mice. [[nanotag-kissei-device-and-literature]]

## Everything here

![[area.base]]

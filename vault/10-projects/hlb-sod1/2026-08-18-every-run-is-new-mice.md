---
type: decision
area: hlb-sod1
status: active
created: 2026-10-22
summary: "Every recording is a new cohort of mice unless Andrea says otherwise; a rig position is not an animal; hardware facts carry across runs, animal facts do not (Andrea, 2026-08-18)"
tags: [decision, eeg, cohort, identity]
---

# Every run is new mice unless Andrea says otherwise

> [!abstract] TL;DR
> 🛑 **Default assumption: every run has new mice.** A recording is a fresh cohort of freshly operated animals unless
> Andrea explicitly says an animal is the same one (stated 2026-08-18, when the 8 W-SD mice went on the rig:
> [[2026-08-18]], [[2026-08-18-W-SD-cohort-first-screen]]).
> 🛑 **A rig position is not an animal.** `A1`, `B2`, `D2` name a port and slot on the amplifier. Two recordings both
> labelled "D2" are two different mice by default. Name animals by batch + position (W-SD A1) or by registry ID.
> 🛑 **No cross-run carry-over of animal facts.** Never open a new run's analysis with "A2 is the good control" or
> "D2 was fixed by the arm C tether": those statements belong to the cohort they were measured on.

## What does carry across runs
The hardware, not the animals: wire-free amplifier inputs, per-chip 60 Hz floor, headstage grounding, tether arms,
channel law, thresholds and criteria are rig properties and are comparable between files. That is why a per-chip floor
comparison across recordings with different mice is legitimate: it measures headstage grounding, not biology.

## Why
Cohorts have been replaced wholesale after a few days, and treating a position label as an animal has already
published two mice as one (the B1a/B1b case in `eeg-emg-analysis/cohorts/HLB-fem-profsurgery-troubleshooting.yaml`;
[[2026-08-09-HLB-cohort-report-generated]] lists them as HLB-B1a and HLB-B1b). Within one batch an animal can also
change under a position: W-SD B1 chewed its tether on 2026-08-19 and a different mouse went into the slot
([[2026-08-18-W-SD-cohort-first-screen]]); S-SD B1 changed from HLBSSD13 to HLBSSD17 on 2026-08-26
([[2026-08-27-B1-swap-baseline-20h-run]]).

## How to apply
- At the start of any analysis treat the file's animals as unknown and unrelated to anything earlier.
- Judge every channel against the wire-free floor in that same file.
- Ask Andrea for animal IDs, surgery dates and tether arms, or read them from the registry / cohort manifest
  (`eeg-emg-analysis/cohorts/<batch>.yaml`); never infer them from a previous manifest.
- Merge two runs into one animal's history only when Andrea says they are the same animal.

## Source
Andrea's statement of 2026-08-18, held until 2026-10-22 as a Claude memory rule; promoted into the vault 2026-10-22.

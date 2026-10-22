---
type: hub
area: eeg-analysis
status: active
created: 2026-06-30
updated: 2026-10-22
summary: "Offline EEG/EMG analysis: animal card and verdict ladder, pipeline, per-mouse CSV, analysis windows, methods, artefact policy, QC symptoms, audits"
tags: [procedure, eeg, analysis, hub, onboarding, python]
---

# EEG analysis

## What this is

Everything that happens after a recording exists on disk: is each animal connected (the six-rung
verdict ladder), split per mouse, staged, exported for a human scorer, and how to defend each step.
The code is `~/sleep-recording-skim/eeg-emg-analysis/`; every threshold is in `core/qc_thresholds.py`
and the connection criterion, wire-free floor and filter chain are in `core/criteria.py`, nowhere else.

## Current state

- 2026-10-22: The code runs from `~/sleep-recording-skim/eeg-emg-analysis/` with `PYTHONPATH=.`; `~/eeg-analysis-venv`'s editable install and the `core/paths.py` figure-style default still point at the deleted `~/Monitoring_project` (the vault default was fixed in 90f7847). [[eeg-analysis-quickstart]]
- 2026-10-14: After the 2026-10-07 grounding fix the 800 µV ground gate cannot judge the rig, and the −1.90 floor-slope gate keeps A1, A2 and B2 of uid1007 UNJUDGEABLE; option (c) (keep 800 before 2026-10-07 14:34, no hum gate after) is recommended and is Andrea's decision, not taken. [[2026-10-14]]
- 2026-10-06: A mains-free EMG measure (power between the 60 Hz harmonics, raw 1000 Hz) reproduces the notched staging (κ median 0.95 over 33 windows); not adopted. [[2026-10-06-S-SD-EMG-rescue-between-harmonics]]
- 2026-10-02: Notching 60/120 Hz in the stage 3 EMG turns SCOREABLE 44 → 69 of 100 animal-recordings and passes its shuffle control; not adopted, because it re-scores published numbers. [[2026-10-02-noise-series-4mice-24h-analysis]]
- 2026-09-29: Every console recording is exported as one CSV per mouse on the SKIM NAS; scoring and cohort analyses read the CSV, while pipeline stages 1-4 (QC ladder, split, features, EDF) still read the xdat. [[per-mouse-csv-format]]
- 2026-09-26: A grounded floor steeper than −1.90 now gives UNJUDGEABLE instead of a false 0.0 % (`2cc5892`). [[contaminated-floor-rejects-good-eeg]]
- 2026-09-26: The two regression suites exit 2 "VERIFIED NOTHING" on e10: their source recordings are only in S3. [[analysis-test-suites]]
- 2026-09-26: Rung 2 can pass an EMG with no muscle-band activity; rung 3 catches it; not fixed. [[emg-without-muscle-band-activity-passes-rung-2]]
- 2026-09-29: Analysis windows set: baseline 09:00 → 09:00 (24 h); recovery 09:00 → 09:00 (ad lib, 24 h) or 13:00 → 09:00 (SD, 20 h). The 2026-09-23 shapes (24 h from 13:00, 28 h from 09:00) are recording windows. [[CANONICAL-recording-windows-and-protocol]]
- 2026-08-26: Each animal is judged against its own chip's wire-free floor; an ungrounded chip is UNJUDGEABLE, not FAIL. [[2026-08-26-per-chip-floor-fix]]
- 2026-08-08: No human-scored kappa exists, so rung 4 (architecture) is PROVISIONAL for every animal. [[blind-scoring-and-kappa]]

## Start here

1. [[animal-card-and-verdict-ladder]]: read before checking a mouse or making any figure
2. [[eeg-analysis-quickstart]]: the four commands, the verdicts, where outputs land
3. [[eeg-pipeline-manual]]: every stage and threshold in detail
4. [[analysis-methods-and-justification]]: standard versus ours, with citations
5. [[eeg-analysis-problems]]: when a step misbehaves (terms: [[eeg-analysis-glossary]])

## Rules that must not be broken

- In the bipolar EEG/EMG layout the signals are already bipolar on the chip: never subtract EEG from EMG or re-reference. Unipolar recordings are differenced by design. [[CANONICAL-allego-channel-selection]]
- Analyse inside unbroken blocks, never across them; lagged statistics across gaps produced `r = +0.854` on pure wake. [[scripts-contact-state-2026-07-31-readme]]
- Never report a REM percentage: the percentile rule fixes it by construction. [[animal-card-and-verdict-ladder]]
- Every constant lives in `core/qc_thresholds.py`; after changing one, re-run stage 1 with `--force`. [[eeg-analysis-problems]]
- Never choose a threshold that maximises `r@1min`; it is the validity statistic. [[blind-scoring-and-kappa]]
- Never judge contact from a filtered trace: a wire-free input band-passed 0.5-30 Hz looks like EEG (median 69 µV). [[2026-08-07-rig-specification-and-analysis-method]]
- UNJUDGEABLE is not PASS, and INSUFFICIENT is not a negative result. [[contaminated-floor-rejects-good-eeg]] [[animal-card-and-verdict-ladder]]
- Never test the floor against the animal: a dead electrode is as flat as the floor (circular). [[contaminated-floor-rejects-good-eeg]]
- Test EMG state-dependence on absolute delta power, never the delta ratio. [[2026-08-21-39h-run-score]]
- Reject at epoch level, never repair; railed epochs are missing data. [[eeg-artefact-and-railing-rejection-policy]]

## Open items

- Replace or retire the 800 µV ground gate and decide how floors are judged after the grounding fix (Andrea). [[2026-10-14]]
- Decide whether to adopt the EMG mains notch or the between-harmonics EMG measure (pre-register, falsification suite, re-score). [[2026-10-02-noise-series-4mice-24h-analysis]]
- Re-point `~/eeg-analysis-venv` (`pip install -e`) and the `core/paths.py` defaults at `~/sleep-recording-skim`; `pipeline/run_pipeline.sh` calls the stages without `PYTHONPATH`. [[eeg-analysis-quickstart]]
- Blind human scoring and Cohen's kappa: packs are built, no epoch scored. [[blind-scoring-and-kappa]]
- Positive control (known signal through a spare headstage): specified, not scheduled. [[positive-control-known-signal-injection]]
- Restore the regression fixtures (from S3) or replace them. [[analysis-test-suites]]

## Everything here

![[area.base]]

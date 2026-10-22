---
name: analysis-stack-audit-2026-08-11
description: "2026-08-11 council audit of the analysis stack: backwards offline-subtract pipeline deleted, 'filtering cannot manufacture slope' FALSE (guard added), slope fractions carry +-20 pts floor error. Two lines in the old memory are out of date."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5a89f8f2-b656-4a31-927c-b16a644cf89f
  modified: 2026-08-11T00:58:02.113Z
---

**Audit 2026-08-10/11.** Key results: (1) "Filtering cannot manufacture slope" is FALSE: white noise band-passed 0.5-30 Hz reads slope -1.08 and scores 100 % usable; a scale-free guard (slope(25-45) - slope(1-25), bar -1.0) was added, band NOT narrowed. (2) A second, backwards pipeline (4 rows per mouse, EEG-EMG subtracted offline) was live in the repo and was DELETED; `core/criteria.py` is now the only usable-fraction engine. (3) Floor sampling error is huge on slope (interim 57.5/71.6/70.3/63.7 % carry about +-20 pts) and zero on hum. (4) `FLAT_UV` is inert; `BAND_DELTA_STAGING` still starts at 0.5 Hz (below the 1.10 Hz hardware high-pass), deliberately not changed. (5) `tests/test_criterion_falsification.py` is the software positive control.

Details: [[2026-08-11-analysis-stack-audit-measurements]] and [[2026-08-11-analysis-stack-consolidation]]

⚠️ Do NOT repeat two stale lines of the original memory: "the EMG gate fails for every experimental animal" (corrected 2026-08-21: B2 passes per-chip) and "the repo has zero git commits" (settled: eeg-emg-analysis is in the sleep-recording-skim history). Envelope variability (burst_cv) does NOT validate EMG here.

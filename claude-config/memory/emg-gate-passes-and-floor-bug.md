---
name: emg-gate-passes-and-floor-bug
description: "2026-08-21 EMG gate on the 39.7 h run: 3 animals survive (A1, A2, D2), C1 and C2 withdrawn on absolute delta; pooled-floor bug fixed 2026-08-26. Rules: always absolute delta not the ratio, per-chip null, strong number vs physiology is a warning."
metadata:
  type: project
---

**2026-08-21 scoring of `allego_1__uid0819-17-25-20` (39.674 h):** the pooled floor in `criteria.floor_stats()` was a bug (chip B1's floor slope -2.079 vs -0.68...-1.35 elsewhere; pooled -1.633) and made every position fail the 15-min gate; per-chip, five pass (FIXED 2026-08-26, [[2026-08-26-per-chip-floor-fix]]). EMG state dependence then passes for A1, A2, D2 only (C1 and C2 WITHDRAWN: against ABSOLUTE delta C1 collapsed -0.733 to -0.009 and C2 reversed to +0.595); B2 is EEG-only (EMG open); D1 degraded mid-run; B1 dead. The 08-11 "no experimental animal passes" is false (B2 passes per-chip).

Details: [[2026-08-21-39h-run-score]]; literature check [[is-our-qc-approach-sound]]

🛑 ALWAYS test state-dependence on ABSOLUTE delta power (µV²), NOT the delta ratio (its denominator carries EMG-band power). The fixed `r <= -0.30` bar is crossable by interference (16/112 wire-free channels reach it): use a PER-CHIP NULL. Shared-path check by SIGN: r(rms_eeg, rms_emg) negative = physiological, positive = shared artefact. 🔑 A strong number that disagrees with basic physiology is a WARNING, not a puzzle (the best number was the artefact). 🛑 STILL NOT A SLEEP RESULT (no hypnogram, no human kappa). 🔴 Real risk is effort allocation: 5/8 channels failed for HARDWARE reasons, so fixing a ground beats floor refinement. 🛑 The user does NOT want to write a methods paper: the goal is only to avoid wasting time and getting wrong answers.

---
name: w-sd-batch-closeout-2026-08-28
description: "W-SD batch closed, sampled 2026-08-28: the per-chip recomputed pre-CSD baseline is the best full-cohort data this rig has made, four grounds collapsed over the 7 days of CSD, and the recovery comparison ended at n=1"
metadata:
  node_type: memory
  type: project
---

🏁⭐⭐⭐ **BATCH `W-SD` CLOSED — ALL TEN SAMPLED 2026-08-28.** Nothing re-measurable.
Close-out: vault `05-experiments/completed/2026-08-28-W-SD-cohort-closeout.md`.
Manifest `cohorts/W-SD.yaml` has all 6 recordings + per-animal verdicts.
Design: **UV WATER arm (0 U), the control against S-SD's SOD1**; CSD Fri 08-21 → sampling Fri 08-28,
daily bouts ending 13:00.
⚠️ **The rebound file is the recovery window after the PENULTIMATE SD day — Thu 08-27 13:00 → Fri
08-28 09:00 — with the protocol STILL RUNNING. Not a post-protocol endpoint.**
Positions (confirmed): **A1 01 · A2 02 · B1 09 · B2 04 · C1 03 · C2 06 · D1 07 · D2 08**;
05 sacrificed 08-21 (**electrode INTACT at post mortem**), 10 in the chamber untethered.

## ✅ THE PRE-CSD BASELINE IS THE BEST FULL-COHORT DATA THIS RIG HAS MADE
`allego_1__uid0819-17-25-20`, 39.672 h, **recomputed per-chip 2026-08-29**
(`~/eeg-processed/2026-08-19/feat_uid0819-17-25-20.npz`):
| pos | mouse | EEG% | longest | h in ≥15min | BOTH% |
|---|---|---|---|---|---|
| **A1** | CSD01 | 99.9 | **7.6 h** | **39.49** | **96.1** |
| **D2** | CSD08 | 98.5 | 1.4 h | 34.32 | **92.8** |
| **A2** | CSD02 | 99.1 | 4.2 h | 36.05 | **82.2** |
| **C1** | CSD03 | 98.8 | **8.9 h** | 36.47 | **66.4** |
| B2 | CSD04 | 92.4 | 4.4 h | 22.38 | EMG open |
**FIVE with real EEG, FOUR pass strict rung 2** — the 08-21 report said THREE because it used the
POOLED floor. That report is now annotated, not deleted.
🔑 **C1 PASSES RUNG 2 AND IS STILL WITHDRAWN — that was a RUNG 4 call** (EMG state dependence
collapsed under falsification, −0.733 → −0.009). Different rungs; both true. Don't quote a rung-4
withdrawal as "the channel was bad".
🔴 **B1/CSD09 was NEVER good** — floor already 1275 µV at baseline, EEG at 1.487× its own floor.

## 🔴🔴 THE 7 DAYS OF CSD COLLAPSED FOUR GROUNDS
Floor 60 Hz baseline → recovery: **A1 4976→1347 (−73%) · A2 4396→1575 (−64%) · D1 4441→1814 (−59%)
· B1 1275→593**. B2/C2/D2 unchanged, C1 −34%.
**A1 AND A2 — the two BEST animals — were lost to a GROUND fault, not an electrode fault.**
⇒ pre-CSD 4 scoreable, post-CSD **1** ⇒ 🔴 **PAIRED RECOVERY COMPARISON = n = 1 (D2 only).**
Case report, never a group result. D2 pre→post: EEG 98.5→74.2%, BOTH 92.8→73.0%, slope −1.45 both.
🛑 Architecture still PROVISIONAL — the kappa is the gate.
⚠️ Tissue endpoints unaffected; all 10 carry the treatment.

## LESSONS THAT OUTLIVE THE BATCH
1. [[weak-chip-ground-hides-as-electrode-failure]] — the fault class + the 800→2000 µV gate proposal.
2. ⭐ **Working EMG exonerates that implant and tether** (shared cable).
3. ⭐⭐ **`02-procedures/pre-flight-connection-screen.md`: a screen must GATE an unrepeatable run.**
   The first hour already said 1 of 8 worked; the connector fix landed AFTER the 20 h run ended.
4. ⭐ **Tether wear is the dominant failure mode of a long deprivation protocol** — 2 tethers eaten,
   2 animals found missing with theirs, 4 grounds degraded over 7 days, 1 electrode intact at necropsy.

## STILL OPEN
🔴 B1's chip hardware (20 h monotonic ground decay 825→469 µV, did NOT recover) before the next
batch · 🔴 the `FLOOR_MIN_HUM_UV` decision · 🟡 D2's paired hypnogram · 🟡 fold the pre-flight screen
into the operator manual · the kappa.
⏭️ **S-SD samples 2026-09-03** — same protocol, same chewing cages. Its D2 has passed strict rung 2
three runs running; protect it.

Related: [[w-sd-recovery-sleep-run-2026-08-27]] · [[weak-chip-ground-hides-as-electrode-failure]] ·
[[recording-2026-08-26-b1-swap-20h-baseline]] · [[cohort-identity-every-run-is-new-mice]]

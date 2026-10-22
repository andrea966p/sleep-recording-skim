---
name: w-sd-recovery-sleep-run-2026-08-27
description: "W-SD recovery sleep in the window after the PENULTIMATE CSD day, Thu 13:00 to Fri 09:00: only D2 is usable so the paired comparison is n=1, four chip grounds were weak all run, B1's ground DECAYED, and a check recording after the run showed A1 and A2 fully recoverable"
metadata:
  node_type: memory
  type: project
---

🔴⭐⭐⭐ **`allego_2__uid0827-12-58-32`, 2026-08-27 12:58:32 → 2026-08-28 09:05 KST. 20.119 h,
RUNG 0 PASS** (72,435,328 data = timestamp, remainders 0/0), zero watchdog stalls. Cohort `W-SD`.
**RECOVERY SLEEP after 7 days of CSD, sampled straight afterwards ⇒ THE TIMEPOINT CANNOT BE
REPEATED.** Features `~/eeg-processed/2026-08-27/feat_uid0827-12-58-32.npz`. Report:
`10-projects/hlb-sod1/2026-08-27-W-SD-recovery-sleep.md`. Manifest `cohorts/W-SD.yaml`.

✅ **POSITION MAP CONFIRMED BY THE USER 2026-08-28 — it IS the registry `XDAQ position` map:**
**A1 CSD01 · A2 CSD02 · B1 CSD09 · B2 CSD04 · C1 CSD03 · C2 CSD06 · D1 CSD07 · D2 CSD08**;
CSD05 sacrificed 08-21, CSD10 untethered in the chamber. ✅ The 08-24/08-25/08-26 runs **stay
S-SD** (HLBSSD11-19) — that was checked, not assumed.

## VERDICTS, 20.1 h, per-chip floor
| pos | mouse | EEG rms/slope/lfhf | floor lfhf p99 | sep | EEG % | longest | h≥15min | EMG % | BOTH % |
|---|---|---|---|---|---|---|---|---|---|
| **D2** | CSD08 | **139 / −1.45 / 15.89** | 2.50 | ✅ | **74.2** | **45.3 min** | **2.90** | **98.5** | **73.0 ✅ PASS** |
| C2 | CSD06 | 1537 / −0.73 / 3.32 | 3.79 | ❌ | 40.1 | 11.2 min | 0.00 | 65.6 | 38.2 🛑 unusable |
| A2 | CSD02 | 67 / −0.07 / 1.21 | 5.66 | ❌ | 3.2 | — | 0 | **99.2** | — |
| A1 | CSD01 | 55 / −0.10 / 1.25 | 5.06 | ❌ | 0.3 | — | 0 | **98.4** | — |
| D1 | CSD07 | 2087 / −0.03 | 3.51 | ❌ | 0.7 | — | 0 | 5.6 | — |
| B2 | CSD04 | 4002, railing 100% | — | ❌ | 0.0 | — | 0 | 0.0 | — |
| C1 | CSD03 | 3901, **both** railing 100% | — | ❌ | 0.0 | — | 0 | 0.0 | — |
| B1 | CSD09 | 🔴 **UNJUDGEABLE**, chip never grounded | | | | | | | |
D2 is threshold-proof (74.2/74.2/74.1% across a ±25% sweep). C2 moves 45→24% and its longest block
by 4.5× **and** fails separation ⇒ 🛑 **C2 enters no result.**

## 🔴🔴 THE PAIRED RECOVERY COMPARISON IS n = 1
Pre-CSD baseline `allego_1__uid0819-17-25-20` (same batch) had **three** scoreable animals —
A1 r@1min 0.495, A2 0.592, D2 0.446. **A1 and A2 give NO EEG here.** Only D2 exists on both sides
of the deprivation. 🛑 Report it as a case, never as a group result.

## ⭐ EMG PROVED A1/A2 WERE A TETHER FAULT, NOT AN IMPLANT FAULT
A1 98.4% at 30 µV with **dark/light 2.73×**, A2 99.2% at 51 µV. Real state dependence ⇒ retires my
earlier caution that a quiet "EMG 100%" might itself be a floating input. EEG side of the chain
failed while EMG through the same tether kept working. (C2 4.32×, D2 3.60× also strong.)

## 🔑 FOUR WEAK GROUNDS PERSISTED ALL 20 h — and B1's DECAYED
Floor 60 Hz vs the 08-26 run: **A1 4314→~1300 · A2 4606→~1550 · D1 3425→~1800**, flat and never
self-recovering ⇒ **not settling after handling.** **B1 825 → 469 µV falling in nearly every hourly
bin.** ⭐⭐ **FIRST RECORDED GROUND DECAY.** Every previous floating chip here was flat from first
epoch to last; a 20 h monotonic decline looks like a **conductor working loose**, not a mis-seat.

## ✅ THE 80 s CHECK AFTER THE RUN — `allego_3__uid0828-09-26-12`, rung 0 PASS
A1 floor **1347 → 5026**, A2 **1575 → 4490**, and **A1/A2/C2/D2 all separate** (lf/hf 13.75/1.88,
10.73/3.48, 8.38/2.25, 10.05/1.59). 🔴 **B1 still ungrounded at 485 µV — did NOT recover ⇒ the one
physical fault.** The fix was found ~20 h too late.
🛑 **8 EPOCHS ONLY. Quote the lf/hf separation and NOTHING else from that file** — a p1 from eight
numbers per site is effectively a minimum, which is why D2 scores 0.0% there while plainly carrying
EEG.

## ✅ THE RE-MATE IS CONFIRMED ON 50 MIN, NOT 80 s — `allego_4__uid0828-10-08-34`
1.802 h, 10:08→11:56 08-28, rung 0 PASS. Found unlogged on 2026-08-29 and now in `cohorts/W-SD.yaml`
+ both vault pages. **A1 62-87% usable EEG, A2 68-95%, per 10 min, for the 50 min they stayed
connected** (91-104 and 136-143 µV). D2 whole file 42.1% EEG / 97.1% EMG.
🔑🔑 **THE TRAP — I fell in first: its whole-file medians (A1 slope −0.49, 33.3%) LOOK LIKE A
RELAPSE AND ARE NOT.** At minute 50 **EEG AND EMG go open together on both port-A positions AND the
chip floors step down** (EEG 96→2092, 140→2093; EMG 104→3164, 85→2991; floor 5319→3334, 3852→3150).
Animals unplugged for sampling. ⭐ **A signal fault cannot kill two roles on two chips in one block,
and it cannot move the floor. To tell "channel died" from "animal left", read the FLOOR and the
OTHER ROLE, never the channel alone.** 🛑 Longest block 10.7 min ⇒ nothing passes rung 2; connection
check, not a scoring file. 🔴 B1 still ungrounded 559 µV.
⚠️ **`allego_5__uid0828-19-10-50`** (08-28 19:10, 0.592 h) = **EMPTY RIG, NOT OURS, NOT W-SD** — all
8 positions 101-153 µV and steep, incl. B1 (floor 113 µV) and C1 (669) which have NO ground ⇒
drifting unterminated inputs, not EEG.

## 🔑 THE PROCESS LESSON
The first-hour screen already said 1 of 8 positions worked. It was run and then annotated instead
of acted on. ⭐ **A first-hour connection screen must GATE the start of an unrepeatable endpoint
recording.** 20 min of checking against 20 h of one-animal data.

Related: [[recording-2026-08-26-b1-swap-20h-baseline]] · [[cohort-identity-every-run-is-new-mice]] ·
[[movement-dependent-contact-root-cause]] · [[ecg-cohort-ground-miswired]]

## From the memory index, trimmed there 2026-09-11 (kept here verbatim)

- 🔴⭐⭐⭐ **[W-SD RECOVERY SLEEP, 7 d CSD — 2026-08-27/28](w-sd-recovery-sleep-run-2026-08-27.md). NEWEST, READ FIRST.** **Thu 12:58 → Fri 09:05, 20.121 h, RUNG 0 PASS. = recovery window after the PENULTIMATE SD day, protocol STILL RUNNING (not a post-protocol endpoint)**; sampling followed ⇒ **unrepeatable**. 🔴🔴 **ONLY D2 usable (73.0% both roles, 45 min block) ⇒ the paired pre/post comparison is n=1** (baseline had A1+A2+D2). ⭐ A1/A2 EMG worked all run (98%, dark/light 2.73×) ⇒ **EEG-side tether fault, not implant**. 🔑 **B1's ground DECAYED 825→469 µV over 20 h — first recorded decay, = conductor working loose.** ✅ Re-mate confirmed on **50 min, not 80 s** (`allego_4__uid0828-10-08-34`, 1.8 h): A1 62-87%, A2 68-95%; floors 1347→5026, 1575→4490; B1 still dead. 🔑 **Its whole-file medians look like a RELAPSE and are not — the animals were UNPLUGGED at min 50** (EEG+EMG open together on 2 chips AND the floor stepped down). ⚠️ `allego_5__uid0828-19-10-50` = EMPTY RIG, not ours. 🛑 quote only lf/hf separation from an 8-epoch file. 🔑 **A first-hour screen must GATE an unrepeatable run, not annotate it.** ✅ Map confirmed = registry XDAQ; 08-24/25/26 stay S-SD.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐⭐⭐ **[W-SD RECOVERY SLEEP — 2026-08-27/28](w-sd-recovery-sleep-run-2026-08-27.md).** B1 ground DECAYED 825→469 µV over 20 h = conductor working loose.

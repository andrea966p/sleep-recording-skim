---
name: recording-2026-09-09-8core-tether-screen
description: The 83 min screen of the new 8-mouse batch on the thicker 8-core tether, 2026-09-09 - the best screen this rig has ever produced.
metadata:
  type: project
---

**`allego_1__uid0909-21-17-52`, Wed 2026-09-09 21:17:52 → 22:40:54 KST, 1.383 h, 498 QC epochs
(10 s), fs 1000, 64 sites per port so all 8 positions present. Rung 0 INTACT, remainder 0/0.**
New batch of 8 mice, **new thicker tether built from 8-core wire**. Ids not yet in a manifest.

## 🎉 BEST SCREEN THIS RIG HAS EVER PRODUCED
**7 of 8 chips grounded, floors 3441-4658 µV, tight.** Every previous cohort had 2-6 chips under
the gate and a floor spread of 246-5609. **7 of 8 EEG channels 96.6-100% usable**, longest unbroken
blocks 20.5-83.0 min, and each beats **its own chip's floor lf/hf p99 in 96-100% of epochs**
(slope margin −0.30 to −1.08). This is not a floating input flattered by a filter.

| pos | floor µV | EEG usable / longest | EMG |
|---|---|---|---|
| A1 | **69, UNGROUNDED** | UNJUDGEABLE | real, cv 42% |
| A2 | 3733 | 99.6% / 77.7 min | real, 49% of epochs >150 µV |
| B1 | 4352 | 99.6% / 41.5 min | real, strict rung 2 **94.6%** |
| B2 | 4170 | 96.6% / 29.0 min | real, strict 78.5% |
| C1 | 3738 | **100.0% / 83.0 min** | ❌ dead, fixed 693 µV |
| C2 | 4658 | 98.4% / 35.3 min | real, 66% of epochs >150 µV |
| D1 | 4379 | 97.8% / 20.5 min | real, strict 79.1% |
| D2 | 3441 | 99.8% / 75.2 min | real, strict 90.6% |

## The two faults
🔧 **A1 chip floor 69 µV ⇒ UNJUDGEABLE, NOT a dead animal.** No lf/hf separation (41% above p99)
and slope margin +0.10 — exactly [[weak-chip-ground-hides-as-electrode-failure]]. Its **EMG moves
(cv 41.9%, max/min 9.4) ⇒ implant and tether are fine** ⇒ **bench connector re-mate, no
isoflurane**, then re-record.
❌ **C1 EMG is a broken conductor**: locked at 693 µV, cv 4.6%, max/min 1.25, hum ÷ own floor
**0.245** = partially conducting. Its EEG is the best channel in the file. Same EMG-only tether
break C1 showed on 2026-08-26, and **C1 is one of the two chewing cages**.

## 🔴 `RMS_HI_UV = 150` NOW CLIPS REAL EMG — new problem, owed a decision
A2 **49%** and C2 **66%** of epochs sit above 150 µV, so their strict rung-2 numbers (51%, 34%) are
an **amplitude-gate artefact, not a connection failure**. Every EMG p95 is 152-380 µV. Either the
8-core tether delivers more EMG or the animals were simply awake (recording is entirely in the dark
phase, lights off 21:00). **Do not quote A2/C2 strict rung 2 until this is settled.**

## Cross-checks that passed
- ⭐ **Flicker cv 4.7-17.6%, max/min 1.4-2.4 on every position** ⇒ per
  [[flicker-discriminates-bend-from-break]], **no bending or torsion signature on any tether.**
- |r| between each position's own EEG and EMG 0.015-0.181 ⇒ no shared path anywhere.
- Railing 0.0% everywhere except C2 EMG 0.4%. EEG rms 58-105 µV across all 8.
- Per-10-min time course flat: no intermittency, no decay over the 83 min.

## ⚠️ WHAT THIS FILE CANNOT SAY
🛑 **83 min, entirely dark phase, one file.** [[recording-2026-08-25-24h-zt0-S-SD]] showed EEG
usability dropping 15-34 points in the dark, so a dark-phase result near 100% is encouraging rather
than inflated — but a 1 h snapshot still overstates a 24 h run.
🛑 **The tether is CONFOUNDED with a fresh re-mate.** The 2026-09-01 bench re-seat also fixed all
eight grounds with the OLD tether ([[s-sd-recovery-sleep-run-2026-09-02]]). Credit for the 8-core
wire needs the floors to still be 3400-4700 µV after days of wear, not on day one.
🔑 Adds a 9th chip-recording to the `FLOOR_MIN_HUM_UV` evidence: 69 µV gave nothing, everything else
was ≥3441. Still nothing between 800 and 2186, still **not applied**.

## Unlogged files found while catching up
- ⚠️ **`allego_0__uid0904-08-55-25`, 30.0 h, 09-04 08:55 → 09-05 14:55, 57.9 GB.** Only **32 sites
  per port = 4 positions**, so it is not an 8-mouse run. Nothing in the vault or any journal.
- ⚠️ `allego_0__uid0829-08-34-39` (59.2 h, 223 GB, "not ours") is **still on disk**. 886 GB free.

Screen scripts were ad hoc against `core/criteria.py`; no cohort manifest exists for this batch yet.

## 🔴 CORRECTION, 2026-09-10 — A1 IS A GROUND-ELECTRODE FAULT, AND ITS EEG IS FINE
**I told Andrea to re-mate A1's connector. That was wrong and he corrected me: every connector is
mated correctly, and the fault is surgical — poor contact between pin and dura after implantation.**
He is right about the mechanism. What the data adds is **WHICH electrode**:

🔑 **The thing that failed on A1 is the chip's 14 WIRE-FREE inputs (56 µV vs 2897-4951 µV on the
other seven). No electrode is attached to those, so no EEG electrode's dura contact can move them.**
What sets that level is the **ground / reference return** ⇒ the fault is the **CEREBELLUM GROUND
screw's contact**, not the EEG electrode. A surgical contact fault, as he said, on the ground.

✅ **A1's EEG electrode is making GOOD contact.** Measured on 5.5 h of `allego_0__uid0910-09-00-00`,
against the SEVEN OTHER chips' floors (valid controls): A1 EEG lf/hf **26.53** — the joint highest in
the file, working range 19.9-26.6 — slope **−1.78** (working −1.70 to −1.80), rms 84 µV, and it beats
those chips' floor lf/hf p99 in **99.9% of epochs**. Delta share 0.41-0.48 with the same
epoch-to-epoch sd as A2 and D2. **Indistinguishable from the seven working EEG channels.**
⭐ A1's floor is FLAT over 5.5 h (56→53 µV), so this is a stable missing connection, not the
working-loose decay B1 showed on 08-27.
🟡 **OPEN: A1's EEG is probably scoreable but the code says UNJUDGEABLE**, because rung 2 needs a
valid control ON ITS OWN CHIP. Rescuing it means judging it against a floor pooled from the other
seven chips — the opposite direction from the 08-18 pooled-floor disaster, and it must be LABELLED
as a different control. Needs a decision.

## THE RUN: `allego_0__uid0910-09-00-00`, started 09:00:00.05 KST, ZT0
Cron one-shot fired 08:50, `RECORDING CONFIRMED GROWING` 2.86 GB/h, hourly watchdog `OK growing`.
⚠️ Rung 0 reads **TRUNCATED mid-run** (data lags timestamp by ~16 k samples) — that is the LIVE FILE
being written, not a fault. Re-run rung 0 after it stops.

**At 5.5 h (all light phase): 7 of 8 EEG at 99.3-100%, longest blocks 107-330 min (A2 and D2 unbroken
for the WHOLE file), and FIVE animals pass strict rung 2 — B1 97.9% (89.8 min block), D2 96.8%,
B2 95.1%, D1 93.5%, A2 89.1%.** Best channel count this rig has produced; the W-SD baseline's best
was 4 passing, and that was over 39.5 h, so duration is not yet comparable.

✅ **Retract yesterday's `RMS_HI_UV=150` alarm as a tether property.** In the light phase EMG rms is
27-51 µV and the gate clips nothing. Last night's 49-66% over-150 epochs were **wake in the dark
phase**, not the 8-core wire. The threshold question is now only about dark-phase EMG.

🔴 **NEW FAULT: C2's EMG broke overnight** (worked at 22:40, dead at 09:00). Locked at 1157-1412 µV,
hum ÷ own floor 0.261, 2.6% railing, dead from the first epoch of the run. **C1 EMG identical
signature** (921-1019 µV, ratio 0.287, flat). ⚠️ **Both slots of port C, EMG only, both EEGs perfect.**
A shared C-branch fault is a HYPOTHESIS, not a finding — per [[b-slot1-was-the-tether-not-the-port]]
a recurrence argument is not a swap test. **Swap the C tether/splitter branch with a known-good one
before naming a cause.**

## From the memory index, trimmed there 2026-09-11 (kept here verbatim)

- 🎉⭐⭐⭐ **[8-CORE TETHER, 8 NEW MICE, 83 min SCREEN — 2026-09-09](recording-2026-09-09-8core-tether-screen.md). NEWEST, READ FIRST.** **Best screen this rig ever made: 7 of 8 chips grounded (floors 3441-4658 µV), 7 of 8 EEG at 96.6-100%, longest blocks 20-83 min**, all beating their OWN floor's lf/hf p99. 🔧 A1 floor 69 µV ⇒ UNJUDGEABLE + its EMG moves ⇒ **bench re-mate, no surgery.** ❌ C1 EMG a broken conductor (fixed 693 µV, ratio 0.245); its EEG is the file's best. 🔴 **`RMS_HI_UV=150` now CLIPS REAL EMG** — A2 49%, C2 66% of epochs above it ⇒ their strict rung 2 is an artefact, do not quote. ⚠️ 83 min, ALL dark phase, and the tether is CONFOUNDED with a fresh re-mate. 🔴 **CORRECTED 09-10: A1 is a GROUND-screw contact fault, NOT a re-mate** — its EEG is indistinguishable from the 7 working channels (lf/hf 26.5, slope −1.78, beats the other chips' floor p99 in 99.9% of epochs). ✅ **Run `allego_0__uid0910-09-00-00` started 09:00:00 sharp; at 5.5 h SEVEN EEG at 99.3-100% and FIVE pass strict rung 2** (B1 97.9%/89.8 min). ❌ C2's EMG broke overnight — port C now dead on BOTH EMGs, EEGs perfect, swap test owed.

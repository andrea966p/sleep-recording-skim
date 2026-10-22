---
name: b-slot1-was-the-tether-not-the-port
description: "2026-08-26 swap test: putting a new mouse with an intact tether into B slot 1 restored the chip ground, falsifying the 'B1 is a port fault' conclusion — HLBSSD13's tether had been chewed through"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-26T03:55:26.885Z
---

🔴⭐⭐⭐ **RETRACTION. I CONCLUDED "B SLOT 1 IS A PORT FAULT, NOT A MOUSE". THAT WAS WRONG.**
Stated in [[recording-2026-08-24-new-8-mice]] and [[recording-2026-08-25-24h-zt0-S-SD]]. A direct
swap on 2026-08-26 falsified it.

## THE SWAP TEST
Andrea pulled the B1 animal (HLBSSD13) on 2026-08-26 **because its tether was chewed**, and plugged
a spare animal, **HLBSSD17**, into the same slot. Same port, same slot, same cable, same XDAQ input,
same splitter branch. Only the animal and its tether changed.

| recording | animal in B1 | chip floor 60 Hz | grounded? | EEG rms | slope | lf/hf |
|---|---|---|---|---|---|---|
| `allego_0__uid0825-09-00-00` | HLBSSD13 | **246 µV** | ❌ no | 486 µV | −1.58 | 11.0 |
| `allego_1__uid0826-12-50-16` | **HLBSSD17** | **2338 µV** | ✅ yes | 84 µV | −1.23 | 10.0 |

✅✅ **THE FAULT FOLLOWED THE ANIMAL, NOT THE POSITION. B slot 1, its cable, its splitter branch and
its XDAQ input are all GOOD.** A chewed tether severing the ground conductor produces exactly the
floating-chip signature ([[ecg-cohort-ground-miswired]]), and that is the parsimonious explanation
for HLBSSD13's whole run.

## WHY I GOT IT WRONG — the reasoning error worth remembering
The evidence I had was real: B slot 1 had failed in several cohorts, its floor was the lowest on the
rig, and the animal sitting there had no adverse surgical note. But **"the fault recurs at position
X" does not imply "position X causes it"** when the thing being swapped in and out at X is a
consumable that keeps breaking. 🔑 **B1 may simply be the cage position where animals can reach and
chew the tether.** That is a behavioural/mechanical explanation at that location, not an electrical
one, and it predicts the same recurrence.
🛑 **A recurrence argument is not a swap test. Do the swap before naming a root cause** — and note
that this swap changed BOTH animal and tether at once, so it exonerates the PORT but does not by
itself separate "animal ground wire" from "tether conductor".

## HLBSSD17 — the extra baseline animal
Batch `S-SD`, male, DOB 2026-05-04, surgery 2026-08-11 (Andrea), tethered 2026-08-18, BW
30.0 → 30.6 g, no adverse surgical note. Registry had **XDAQ position `/`** — operated and tethered
but never on the rig; it was **sitting outside, still tethered**, and is now in B1. Update
`cohorts/S-SD.yaml`, which records it as having no position.
⭐ First minutes look genuine: **EEG 84 µV, slope −1.23, lf/hf 10.0 against a floor p99 of 2.78 ⇒
separated**; EMG 103 µV, both roles ~76% usable. 🛑 Only ~20 epochs at first look — not a verdict.

## COHORT STATE AT THE START OF THIS RUN (`allego_1__uid0826-12-50-16`, from 12:50:16)
lf/hf, animal vs its own chip floor p99 — separated = real EEG:
**C1 35.25/2.20 ✅ · A1 16.85/9.82 ✅ · D2 15.80/2.44 ✅ · B1 10.00/2.78 ✅ · A2 5.08/3.85 ⚠️ marginal
· B2 1.97/3.48 ❌ · C2 1.69/2.97 ❌ · D1 1.59/7.53 ❌**
🔴 **A2 and C2 have DEGRADED since the 24 h run** (A2 was 79.7% EEG with a 3.62 h block, C2 50.3%;
A2's EEG rms is now ~2549 µV). A2's decline was already visible in the last 5 h of the 24 h run.
✅ All 8 chips now read grounded (2872-5164 µV) — no floating chip anywhere on the rig.

Related: [[recording-2026-08-25-24h-zt0-S-SD]] · [[recording-2026-08-24-new-8-mice]] ·
[[floor-threshold-fixed-per-chip]] · [[movement-dependent-contact-root-cause]]


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐⭐⭐ **[B SLOT 1 WAS THE TETHER, NOT THE PORT](b-slot1-was-the-tether-not-the-port.md).** A recurrence argument is not a swap test.

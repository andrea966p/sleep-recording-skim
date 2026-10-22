---
name: recording-2026-08-26-b1-swap-20h-baseline
description: "2026-08-26 20.3 h S-SD baseline with HLBSSD17 newly in B1: the swap works, D2 passes strict rung 2 with 18.2 h, C1's tether damage is on the EMG conductor only, and A1's 0.0% is a contaminated floor not a dead animal"
metadata:
  node_type: memory
  type: project
---

⭐⭐⭐ **`allego_1__uid0826-12-50-16`, 2026-08-26 12:50:15 → 2026-08-27 09:09 KST. 20.326 h,
71.4 GiB, RUNG 0 PASS** (73,173,248 data = timestamp, remainders 0/0). 608 watchdog checks,
**zero stalls**. Cohort `S-SD`. Features `~/eeg-processed/2026-08-26/feat_uid0826-12-50-16.npz`.
Report: vault `05-experiments/completed/2026-08-27-B1-swap-baseline-20h-run.md`.
✅ Manifest `cohorts/S-SD.yaml` NOW UPDATED with all three runs and the B1 placement change.

## VERDICTS, per-chip floor, 7317 epochs
| pos | mouse | EEG rms/slope/lfhf | EEG % | longest | h in ≥15 min blocks | EMG rms | EMG % | BOTH % |
|---|---|---|---|---|---|---|---|---|
| **D2** | HLBSSD18 | 92 / −1.51 / 14.3 | **99.3** | **185 min** | **18.20** | **52** | 81.1 | **81.0 ✅ PASS** |
| C1 | HLBSSD15 | 103 / −1.48 / 15.3 | 92.2 | 91.8 min | 12.26 | 458 | 0.0 | 0.0 |
| **B1** | **HLBSSD17** | **93 / −1.47 / 17.3** | 77.8 | 12.8 min | 0.00 | **44** | **94.9** | 75.0 |
| C2 | HLBSSD16 | 3284 / −0.43 / 3.0 | 42.8 | 24.5 min | 2.42 | 1010 | 0.0 | 0.0 |
| A2 | HLBSSD12 | 3856 / −0.39 / 3.4 | 26.6 | 28.5 min | 0.73 | 554 | 0.2 | 0.0 |
| D1 | HLBSSD19 | 2701 / −0.02 / 1.8 | 3.9 | — | 0.00 | 1124 | 0.0 | 0.0 |
| A1 | HLBSSD11 | **94 / −1.33 / 13.5** | **0.0 🔴** | — | — | 48 | **93.9** | 0.0 |
| B2 | HLBSSD14 | 4394 / −0.11 / 1.6 | 0.0 | — | — | 104 | 68.2 | 0.0 |

**Strict rung 2 (EEG AND EMG, same epoch, ≥15 min block): D2 ONLY, third run running.** D2 is the
blind-scoring pack. ✅ All 8 chips grounded (2186-5215 µV) for the first time this cohort.

## ✅ THE B1 SWAP WORKED — port exonerated
HLBSSD17 into HLBSSD13's slot: floor **246 → 2186 µV**, EEG **486 → 93 µV**, EMG **2761 → 44 µV**,
lf/hf 11.0 → **17.34 against a floor p99 of 3.81** (widest separation on the rig), **zero railing**.
Confirms [[b-slot1-was-the-tether-not-the-port]].
🔴 **DO NOT QUOTE B1's PERCENTAGE.** ±25% threshold sweep: **99.1% / 210 min ↔ 77.8% / 12.8 min ↔
37.6% / 5.7 min.** Failing epochs miss by a median slope margin of **0.091**; 747 blocks, median
20 s, so nothing reaches 15 min. Cause: chip B1's floor has 3 quiet sites (68-165 µV rms) that
steepen its p1. **Say CONNECTED, give no number.** C1/C2/D2/A2 all move <1.5 pts — they are robust.

## 🔴 C1's TETHER: the break is on the EMG conductor, NOT the EEG one
Andrea reported the C1 tether failed structurally at its **centre**, with railing when not held
straight. **C1's EEG railed in 0 of 7,317 epochs** (max rms 297 µV vs a 6377 µV rail) and was the
rig's 2nd-best channel. **C1's EMG** = 599 µV of 60 Hz against a 5215 µV floor, 0.08% railing =
the documented **damaged/partially-conducting cable** signature. **EEG↔EMG |r| = 0.091** = the
working-animal value, not the 0.5-0.75 of a shared-path fault (D1 is 0.208, p75 0.51 — D1 IS one).
🔑 **The bench railing is NOT in this file.** The only channel with brief rail hits on a
healthy-amplitude EEG is **A1** (6.11% of epochs, median railed fraction 0.0022, clustered
22:50-02:50). 🛑 **Confirm which cage that observation came from before replacing a tether.**

## 🔴🔴 THE PER-CHIP FLOOR FIX KILLED THE FALSE PASS, NOT THE FALSE FAIL
A1 is unchanged between runs (**rms 94→94, slope −1.36→−1.33, lf/hf 14.67→13.46**) yet went
**31.0% → 0.0%**, because chip A1's own floor steepened **slope p1 −1.523 → −2.437**. Seven of its
14 wire-free sites now sit below −2.4 and the floor's lf/hf p99 is **27.78** vs the animal's 13.46.
Every other chip moved <0.25. **A1 must read UNJUDGEABLE, like an ungrounded chip.**
🔑 **OWED: a second rung-2 validity guard for a GROUNDED BUT SPECTRALLY CONTAMINATED floor** —
e.g. refuse when floor lf/hf p99 > animal median, or >⅓ of sites have p1 slope < −2.
Supersedes nothing in [[floor-threshold-fixed-per-chip]]; it is the missing other half.

## 🔴 A2 AND C2 HAVE GENUINELY FAILED (not thresholds)
A2 rms 124→3856, slope −1.49→−0.39, lf/hf 13.91→3.42, 68.7% railing. C2 124→3284, 9.52→2.99,
54.0% railing. Both flip open/connected **at whole-hour scale**. Both read ~100% on the 1 h screen
of 08-24. 🛑 Third demonstration that **an hour screen overstates a long run**.

## LIGHT/DARK — do NOT treat as a replication
Run is ZT3.8 → ZT0.15: **41% light, ONE dark phase**, unequal weighting. Drops: D2 −0.9, A2 −1.1,
C2 −6.8, C1 −10.0, B1 −14.1. ⚠️ A2/C2's small drops are only because they had already collapsed by
daylight (27%, 47%). EMG dark/light amplitude: **A1 4.40×** (reproduces its 4.29×), D2 2.15×,
B1 1.64×, B2 1.53×.

## ⭐ B1 AND C1 ARE THE CHEWING CAGES
Four tether events, two positions, two cohorts: W-SD B1 cut 08-19; W-SD B1+C1 animals found missing
with their tethers 08-22; S-SD B1 chewed 08-26; S-SD C1 failed at centre 08-27. **Mechanical
property of those CAGE LOCATIONS, not electrical property of those PORTS** — the swap proved the
port good. Fix the cages, not the wiring.

Related: [[b-slot1-was-the-tether-not-the-port]] · [[recording-2026-08-25-24h-zt0-s-sd]] ·
[[recording-2026-08-24-new-8-mice]] · [[floor-threshold-fixed-per-chip]] ·
[[movement-dependent-contact-root-cause]] · [[animal-card-verdict-ladder]]

## From the memory index, trimmed there 2026-09-11 (kept here verbatim)

- ⭐⭐⭐ **[20.3 h B1-SWAP BASELINE — 2026-08-26](recording-2026-08-26-b1-swap-20h-baseline.md). NEWEST, READ FIRST.** ✅ Swap confirmed: HLBSSD17 in B1 gives real EEG+EMG, floor 246→2186 µV, zero railing — **port good**. ✅ **D2 passes strict rung 2 a 3rd time, 18.20 h in ≥15 min blocks** ⇒ the scoring pack. 🔴 **C1's tether break is on the EMG conductor only** — its EEG railed **0 of 7317 epochs**; the bench railing is NOT in the file (A1 is the one with rail hits). 🔴🔴 **The per-chip fix killed the false PASS, not the false FAIL** — A1 unchanged yet 31%→0.0% because ITS FLOOR steepened; owed: an UNJUDGEABLE guard for a contaminated floor. 🔴 A2+C2 genuinely dead now. ⚠️ **Never quote B1's %** (±25% sweep: 99.1↔37.6). ⭐ **B1 and C1 are the CHEWING CAGES** — 4 events, 2 positions, 2 cohorts.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐⭐⭐ **[20.3 h B1-SWAP BASELINE — 2026-08-26](recording-2026-08-26-b1-swap-20h-baseline.md).** B1+C1 are the CHEWING CAGES. Never quote B1 %.

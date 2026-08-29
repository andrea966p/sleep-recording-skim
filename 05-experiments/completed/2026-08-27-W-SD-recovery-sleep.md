---
tags: [experiment, eeg, emg, W-SD, sleep-deprivation, completed]
created: 2026-08-28
status: complete
batch_status: SAMPLED 2026-08-28
recording: allego_2__uid0827-12-58-32
cohort: W-SD
---

# Recovery sleep on the penultimate SD day, Thursday 13:00 to Friday 09:00, batch W-SD

> [!important] What this timepoint is, stated precisely (corrected 2026-08-29)
> This is the **recovery-sleep window that follows the sleep-deprivation bout on the SECOND TO LAST
> day of the CSD protocol**: from **13:00 Thursday 2026-08-27**, the moment that day's deprivation
> ended, through to **09:00 Friday 2026-08-28**. The protocol was still running; this is not a
> post-protocol endpoint. An earlier version of this page called it "recovery sleep after 7 days of
> CSD", which reads as though deprivation had finished. **It had not.** Seven days had *elapsed*
> since CSD began on Friday 2026-08-21, and Thursday was the penultimate day.
> The measurements on this page are unaffected — the file analysed is and always was
> `allego_2__uid0827-12-58-32`, Thursday 12:58:30 to Friday 09:05:45 KST, 20.121 h.

> [!note] The batch was sampled on 2026-08-28. Nothing here can be re-measured.
> Batch close-out, covering everything W-SD produced from first screen to sampling:
> [[2026-08-28-W-SD-cohort-closeout]].

> [!abstract] TL;DR
> `allego_2__uid0827-12-58-32`, **2026-08-27 12:58:32 → 2026-08-28 09:05 KST, 20.119 h, 66.2 GiB,
> RUNG 0 PASS** (72,435,328 data = timestamp samples, remainders 0 and 0). Cohort `W-SD`, the UV
> water arm, recorded from the moment the SD day ended at 13:00 through to sampling.
>
> 🔴 **ONE ANIMAL CARRIES THIS TIMEPOINT. D2 / HLBCSD08:** EEG 74.2% with a 45.3 min longest block
> and **2.90 h inside blocks of 15 min or more**, EMG 98.5%, **both roles in the same epoch 73.0%
> with a 45.0 min block**, and it does not move under a ±25% threshold sweep. Everything else fails.
>
> 🔴🔴 **THE PAIRED RECOVERY COMPARISON IS n = 1.** The pre-CSD baseline on this same batch, the
> 39.7 h run of 19 August, had **three** scoreable animals: A1, A2 and D2. A1 and A2 give **no EEG
> at all** here. Only D2 appears in both files, so "sleep after 7 days of deprivation versus before
> it" rests on a single mouse.
>
> ⚠️ **A1 and A2 are not dead animals — their EEG was floating and their EMG worked the whole time**
> (98.4% and 99.2%, and A1's muscle amplitude is 2.73× higher in the dark, which is real state
> dependence). Whatever was wrong was on the EEG side of the tether chain, not the implant.
>
> ✅⭐ **THE 1 MINUTE CHECK AT 09:26 THIS MORNING SHOWS A1 AND A2 BACK.** Their chip grounds jumped
> from 1347 and 1575 µV to **5026 and 4490 µV**, and A1, A2, C2 and D2 all now produce EEG that
> separates cleanly from their own wire-free floors. **The fault was recoverable, and it was found
> 20 hours too late.**

## Rung 0 — FILE: PASS

| | |
|---|---|
| Recording | `allego_2__uid0827-12-58-32` |
| Start | **Thursday 2026-08-27 12:58:30 KST**, as that day's deprivation bout ended at 13:00 |
| Stop | **Friday 2026-08-28 09:05:45 KST**, by hand, before sampling |
| What the window is | the **recovery sleep after the penultimate SD day**, not a post-protocol endpoint |
| Duration | 20.119 h, 7,243 epochs of 10 s |
| Samples | 72,435,328 at 1000 Hz, 262 channels |
| Data vs timestamps | equal, remainder 0 and 0 |
| Watchdog | ran throughout, **zero stalls** until the hand stop |

Features at `~/eeg-processed/2026-08-27/feat_uid0827-12-58-32.npz`.

## The design

| | |
|---|---|
| Batch | `W-SD`, HLBCSD01 to HLBCSD10, male C57BL/6J (B6J-BomTac) |
| Drinking arm | **UV-sterilised water, 0 U** — this is the water control arm, not the SOD1 arm |
| Sleep condition | chronic sleep deprivation, **CSD 2026-08-21 → 2026-08-28, seven days** |
| This recording | the **recovery-sleep** window, the endpoint the arm exists for |
| Sampling | 2026-08-28, straight after |
| Pre-CSD baseline | `allego_1__uid0819-17-25-20`, 39.674 h, same batch, before CSD started |

Positions, from the registry's `XDAQ position` column and confirmed at the bench on 2026-08-28:

| A1 | A2 | B1 | B2 | C1 | C2 | D1 | D2 |
|---|---|---|---|---|---|---|---|
| HLBCSD01 | HLBCSD02 | HLBCSD09 | HLBCSD04 | HLBCSD03 | HLBCSD06 | HLBCSD07 | HLBCSD08 |

HLBCSD05 was sacrificed on 08-21 and HLBCSD10 sits in the deprivation chamber untethered, so
neither is on the rig. ⚠️ **B1 has held HLBCSD09 only since 2026-08-19 17:20**, when the previous,
unidentified B1 animal chewed and cut its tether. Nothing from before that carries.

## Rung 2 — CONNECTION, 20.119 h

| pos | mouse | EEG rms | slope | lf/hf | floor lf/hf p99 | separated | EEG % | longest | h in ≥15 min blocks | EMG rms | EMG % | BOTH % | longest BOTH | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **D2** | **HLBCSD08** | **139 µV** | **−1.45** | **15.89** | 2.50 | ✅ | **74.2** | **45.3 min** | **2.90** | **38** | **98.5** | **73.0** | **45.0 min** | ✅ **PASS** |
| C2 | HLBCSD06 | 1537 | −0.73 | 3.32 | 3.79 | ❌ | 40.1 | 11.2 min | 0.00 | 40 | 65.6 | 38.2 | 11.2 min | ⚠️ not separated |
| A2 | HLBCSD02 | 67 | −0.07 | 1.21 | 5.66 | ❌ | 3.2 | 1.2 min | 0.00 | **51** | **99.2** | 3.2 | 1.2 min | EMG only |
| A1 | HLBCSD01 | 55 | −0.10 | 1.25 | 5.06 | ❌ | 0.3 | 0.3 min | 0.00 | **30** | **98.4** | 0.3 | 0.3 min | EMG only |
| D1 | HLBCSD07 | 2087 | −0.03 | 2.14 | 3.51 | ❌ | 0.7 | 0.3 min | 0.00 | 1248 | 5.6 | 0.1 | — | FAIL |
| B2 | HLBCSD04 | 4002 | +0.04 | 1.70 | 2.70 | ❌ | 0.0 | — | 0.00 | 736 | 0.0 | 0.0 | — | FAIL, EEG railing 100% |
| C1 | HLBCSD03 | 3901 | −0.07 | 0.98 | 5.38 | ❌ | 0.0 | — | 0.00 | 3599 | 0.0 | 0.0 | — | FAIL, **both** railing 100% |
| **B1** | HLBCSD09 | — | — | — | — | — | — | — | — | — | — | — | — | 🔴 **UNJUDGEABLE**, chip never grounded |

Threshold sensitivity, ±25% on the floor slope threshold:

| pos | −25% | point | +25% |
|---|---|---|---|
| **D2** | **74.2% / 45.3 min** | **74.2% / 45.3 min** | **74.1% / 45.3 min** |
| C2 | 45.4 / 50.2 | 40.1 / 11.2 | 24.3 / 9.5 |
| A2 | 9.8 / 2.0 | 3.2 / 1.2 | 1.1 / 0.7 |
| A1, B2, C1, D1 | ≤1.6 | ≤0.7 | ≤0.3 |

**D2 does not move at all.** C2's longest block moves by a factor of 4.5, which is on top of it
failing the separation test, so C2 does not enter any result.

## 🔴 The paired comparison this experiment exists for is n = 1

| pos | mouse | pre-CSD, 39.7 h run of 08-19 | recovery, this run |
|---|---|---|---|
| **D2** | HLBCSD08 | ✅ scoreable, hypnogram r@1min 0.446 | ✅ **73.0% both roles, 45 min block** |
| A1 | HLBCSD01 | ✅ scoreable, r@1min 0.495 | 🔴 **no EEG** (floating) |
| A2 | HLBCSD02 | ✅ scoreable, r@1min 0.592, the best on the rig | 🔴 **no EEG** (floating) |
| C2 | HLBCSD06 | ❌ hypnogram rejected, r@1min 0.11 | ⚠️ not separated |
| D1 | HLBCSD07 | ❌ hypnogram rejected, r@1min 0.001 | ❌ |
| B2 | HLBCSD04 | EEG good, EMG open, no states | ❌ |
| C1 | HLBCSD03 | withdrawn under falsification | ❌ both channels open |
| B1 | HLBCSD09 | — | 🔴 unjudgeable |

🛑 **Only D2 has rung-2-passing data on both sides of the seven days of deprivation.** A
before-and-after recovery-sleep statement from this batch is a statement about one mouse. That is
worth reporting as a case, and it is not worth reporting as a group result.

## 🔴 Four chips ran the whole 20 h with a weak ground

Chip floor 60 Hz, hourly median. The chips are rig hardware and did not move; the ground reference
arrives through the animal and its tether.

| pos | 08-26 run | 12:00 | 16:00 | 20:00 | 00:00 | 04:00 | 08:00 |
|---|---|---|---|---|---|---|---|
| **A1** | 4314 | 1294 | 1285 | 1392 | 1587 | 1322 | 1358 |
| **A2** | 4606 | 1634 | 1479 | 1605 | 1570 | 1666 | 1736 |
| **B1** | 2186 | **825** | 650 | 642 | 548 | **485** | **469** |
| **D1** | 3425 | 1804 | 1807 | 1713 | 1965 | 1868 | 1953 |
| B2 | 4371 | 4639 | 4450 | 4506 | 4351 | 4475 | 4207 |
| C1 | 5215 | 3566 | 3480 | 3723 | 3527 | 3483 | 3433 |
| C2 | 4964 | 4457 | 4755 | 4129 | 4538 | 4339 | 5534 |
| D2 | 3175 | 4802 | 4704 | 4772 | 4753 | 4848 | 4820 |

⭐ **B1's ground did not fail, it DECAYED**: 825 → 469 µV, falling in nearly every hourly bin across
the run. Every previous floating chip in this project has been flat-floating from the first epoch
to the last. **This is the first time the decay itself has been recorded**, and a monotonic decline
over 20 h is what a conductor working loose looks like, not what a mis-seated connector looks like.

A1, A2 and D1 sat at a third to a half of normal for the entire run and **never recovered on their
own.** That rules out settling after handling.

## ✅ The 1 minute check at 09:26, after the run — A1 and A2 came back

`allego_3__uid0828-09-26-12`, 83,328 samples, 80 s, rung 0 PASS.

| pos | mouse | floor 60 Hz, 20 h run → check | EEG rms | slope | lf/hf vs floor p99 | separated |
|---|---|---|---|---|---|---|
| **A1** | HLBCSD01 | **1347 → 5026** | 91 µV | −1.43 | **13.75** vs 1.88 | ✅ |
| **A2** | HLBCSD02 | **1575 → 4490** | 134 | −1.53 | **10.73** vs 3.48 | ✅ |
| C2 | HLBCSD06 | 4501 → 5377 | 70 | −1.11 | **8.38** vs 2.25 | ✅ |
| D2 | HLBCSD08 | 4761 → 4547 | 155 | −1.41 | **10.05** vs 1.59 | ✅ |
| D1 | HLBCSD07 | 1814 → 1654 | 1151 | −0.02 | 1.61 vs 6.85 | ❌ |
| C1 | HLBCSD03 | 3524 → 3195 | 4015 | −0.12 | 1.94 vs 3.67 | ❌ both railing |
| B2 | HLBCSD04 | 4434 → 4622 | 4346 | −0.05 | 1.50 vs 2.97 | ❌ |
| **B1** | HLBCSD09 | **593 → 485** | — | — | — | 🔴 still ungrounded |

> [!warning] Read the separation, not the percentages
> Eighty seconds is **eight epochs**. A 1st-percentile threshold estimated from eight numbers per
> site is essentially a minimum and cannot be trusted, which is why D2 scores 0.0% here while
> plainly carrying EEG. **The lf/hf separation against the same file's own wire-free floor is a
> shape comparison and survives the short record; the usable fractions do not.** Quote the
> separation column and nothing else from this file.

✅ **A1 and A2 are recoverable and were recovered.** Their grounds went back to full strength and
their EEG reappeared with a −1.4 to −1.5 slope and an lf/hf 4 to 7 times their own floor.
🔴 **B1 did not recover** and is the one position where something is physically broken.

## A1 and A2 in detail — the EEG was never intermittent, and the electrodes were never broken

Added 2026-08-29, after the batch was sampled.

**Neither channel carried anything at any point in the twenty hours.** This is not a degraded or
flickering channel; it is a flat line that never moved.

| | A1 (HLBCSD01) | A2 (HLBCSD02) | D2 (HLBCSD08), for contrast |
|---|---|---|---|
| EEG rms, full range across 21 hourly bins | **47-57 µV** | **62-72 µV** | 129-151 µV |
| slope, every hourly bin | −0.03 to −0.17 | +0.09 to −0.30 | −1.45 |
| lf/hf, every hourly bin | 1.07-1.50 | 1.03-1.39 | 15.89 |
| its own chip floor's lf/hf p99 | 5.06 | 5.66 | 2.50 |
| **epochs beating that p99** | **4 / 7,243 (0.06%)** | **2 / 7,243 (0.03%)** | **7,239 / 7,243 (99.94%)** |
| **epochs with slope steeper than −1.0** | **9 (0.12%)** | **6 (0.08%)** | **7,069 (97.6%)** |

An amplitude that varies by ±3 µV across twenty hours is not a biological signal. Real EEG changes
with behavioural state; D2's does. The last twenty-five minutes of the recording look the same as
the first.

### The ratio that shows the electrodes were fine

Each EEG channel's own 60 Hz, as a fraction of its chip's wire-free floor:

| pos | EEG 60 Hz ÷ chip floor | reading |
|---|---|---|
| **A1** | **0.032** | proportionally normal |
| **A2** | **0.045** | proportionally normal |
| **D2** (real EEG) | **0.032** | the reference value |
| C2 | 0.039 | proportionally normal, intermittent |
| D1 | 0.215 | partial |
| B1 | 0.482 | partial |
| B2 | 1.207 | **at/above the floor = open input riding the rail** |
| C1 | 1.446 | **open** |

🔑 **A1 sits at exactly D2's value.** Relative to its own chip, nothing was wrong with that channel.
What collapsed was the **chip's whole reference** — floor 4314 → 1347 µV — which scales everything
on that chip down by a factor of three or four, so the EEG arrived at 55 µV and spectrally flat.

The EMG on those same two positions ran at 98.4% and 99.2% all night through the **same tether**,
and A1's muscle amplitude was 2.73× higher in the dark, which is genuine state dependence. Signal
was reaching the headstage. The reference was not.

### 🔴 The verdict engine called this a FAIL, and it should have refused

`FLOOR_MIN_HUM_UV = 800`, so A1 at 1347, A2 at 1575 and D1 at 1814 all cleared the grounded gate and
were scored **FAIL**. Across the 32 chip-recordings available from the four runs of 24 to 27 August,
**six chips sat below 2000 µV and not one produced EEG**, while the lowest floor that ever produced
EEG was **2186 µV**. There is no overlap. A bar of 2000 µV would have returned **UNJUDGEABLE** here,
which is the difference between "this animal's electrode is bad, plan a tether change under
anaesthesia" and "the rig could not answer, re-mate the connector at the bench".

The evidence table, the proposed change and the check order are written up in
[[weak-chip-ground-vs-open-electrode]]. ⚠️ **The constant has not been changed** — it rewrites
verdicts already published in three reports and is waiting on a decision.

## What this run cost, and the one process change that would have prevented it

The first hour of this recording already contained everything above: A1, A2 and D1 quiet and flat,
four chip grounds at a third of normal, C1 and B2 railing. **That screen was run and it said one of
eight positions was working.** The intervention that fixed A1 and A2 was made after the run ended.

🔑 **A first-hour connection screen should gate the start of any endpoint recording, not annotate it
afterwards.** For a timepoint that cannot be repeated because the animals are sampled the next
morning, twenty minutes of checking is cheap and twenty hours of one-animal data is not.

## Still open

1. 🔴 **B1's chip is physically failing** — a 20 h monotonic ground decay, and it did not come back
   after whatever fixed A1 and A2. That hardware needs looking at before the next batch goes on.
2. 🟡 **Sleep architecture from D2** — the recovery hypnogram against its own pre-CSD hypnogram from
   `allego_1__uid0819-17-25-20`. 🛑 Still PROVISIONAL: no human has scored an epoch and the blind
   scoring **kappa** remains the gate on every rung 4 statement.
3. 🟡 A1 and A2 have working EMG across the whole run. EMG-only data cannot stage sleep here, but
   A1's 2.73× dark/light muscle amplitude is a usable activity measure if one is wanted.
4. 🟡 The **contaminated floor** guard is still unwritten. It did not bite in this run, but it did
   on 08-24 and 08-26.

## Provenance

- Raw: `~/radix/data/allego_2__uid0827-12-58-32{_data,_timestamp}.xdat`, and
  `allego_3__uid0828-09-26-12` for the check
- Features: `~/eeg-processed/2026-08-27/feat_uid0827-12-58-32.npz`, 7,243 × 128
- Engine: `core/criteria.py`, `core/qc_thresholds.py` as of 2026-08-28
- Cohort: `eeg-emg-analysis/cohorts/W-SD.yaml`; husbandry from
  `HLB_SOD1_Intake_Monitoring.xlsx`, sheets `Registry` (header row 5) and `W-SD`
- Related: [[2026-08-21-39h-run-score]] · [[2026-08-27-B1-swap-baseline-20h-run]]

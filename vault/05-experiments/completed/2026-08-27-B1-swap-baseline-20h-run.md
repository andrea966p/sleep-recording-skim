---
tags: [experiment, eeg, emg, S-SD, tether, completed]
created: 2026-08-27
status: complete
recording: allego_1__uid0826-12-50-16
cohort: S-SD
---

# The B1 swap baseline, 20.3 hours, cohort S-SD

> [!abstract] TL;DR
> `allego_1__uid0826-12-50-16`, **2026-08-26 12:50:15 → 2026-08-27 09:09 KST, 20.326 h,
> 71.4 GiB, RUNG 0 PASS**, 608 watchdog checks with **zero stalls**. Cohort `S-SD`, eight rig
> positions, **B slot 1 now holds a different animal (HLBCSD17)** after the previous B1 mouse
> chewed through its tether.
>
> ✅ **THE B1 SWAP WORKED.** HLBCSD17 gives real EEG and real EMG through the same port, the same
> cable and the same XDAQ input that read floating a day earlier. Chip floor 60 Hz went
> **246 → 2186 µV**, EEG 486 → 93 µV, lf/hf 11.0 → 17.3 against a floor p99 of 3.8, the widest
> separation on the rig. **B slot 1 is a good port. The previous failure was the tether.**
> ⚠️ **Do not quote B1's usable percentage.** It is 77.8% at the point threshold, 99.1% if the
> threshold is loosened 25% and 37.6% if it is tightened 25%. The channel is connected; the number
> is not stable.
>
> 🔴 **C1's tether damage IS in the data, but on the EMG conductor, not the EEG one.** Andrea saw
> the C1 tether fail structurally at its centre and saw railing when it was not held straight.
> **In this 20.3 h recording C1's EEG railed in 0 of 7,317 epochs** and was the second best channel
> on the rig (92.2% usable, one unbroken 91.8 min block, 12.26 h inside blocks of 15 min or more).
> C1's **EMG** meanwhile sits at 599 µV of 60 Hz against a 5215 µV floor with 0.08% railing, which
> is this project's documented **damaged / partially conducting cable** signature, and its two
> channels correlate at 0.091, the working-animal value rather than the 0.5 to 0.75 of a shared
> path fault. So the break has reached one conductor and not the other, as of 09:09 on 27 August.
>
> 🔴🔴 **A1 IS NOT A FAILED ANIMAL, IT IS A CONTAMINATED FLOOR.** A1's EEG numbers are the same as
> in the 24 h run to within noise (rms 94 → 94 µV, slope −1.36 → −1.33, lf/hf 14.67 → 13.46) yet
> its usable fraction fell from 31.0% to **0.0%**, because chip A1's own wire-free floor steepened
> from slope p1 −1.523 to −2.437. **Half of that chip's wire-free sites are now steeper than the
> animal's own EEG.** The slope criterion has no discriminating power there and A1 should read
> **UNJUDGEABLE**, exactly as an ungrounded chip does. See the open item at the bottom.
>
> **Strict rung 2, EEG and EMG usable in the SAME epoch inside a block of 15 min or more: D2 only,
> again.** D2 is outstanding: 99.3% EEG, one unbroken 185 min block, 18.20 h inside long blocks.

## Rung 0 — FILE: PASS

| | |
|---|---|
| Recording | `allego_1__uid0826-12-50-16` |
| Start | 2026-08-26 12:50:15 KST (03:50:15 UTC) |
| Stop | 2026-08-27 09:09 KST, stopped by hand |
| Duration | 20.326 h, 7,317 epochs of 10 s |
| Samples | 73,173,248 at 1000 Hz, 262 channels |
| Data vs timestamps | 73,173,248 = 73,173,248, remainder 0 and 0 |
| Size | 76,685,563,904 bytes |
| Watchdog | 608 checks, **zero stalls**, `allegoserver` up throughout, write rate 100.6 to 100.7% of nominal |

Features cached at `~/eeg-processed/2026-08-26/feat_uid0826-12-50-16.npz`.
Watchdog log at `~/eeg-processed/2026-08-26/watchdog_uid0826-12-50-16.log`.

## What changed since the 24 h run

The 24 h ZT0-to-ZT0 run `allego_0__uid0825-09-00-00` ended at 09:16 on 26 August. Between then and
12:50 the B1 animal, **HLBCSD13, was pulled because its tether was chewed**, and the spare
**HLBCSD17** was plugged into the same slot. HLBCSD17 had been operated on 2026-08-11 and tethered
on 2026-08-18 with the rest of the batch but had never been on the rig. Nothing else on the rig was
touched. **This is a single-variable swap at the position, and it is the reason the earlier "B1 is
a port fault" reading is retracted.**

## The floor, per chip

Every threshold below comes from the 14 wire-free amplifier inputs on the **same chip** as the
animal, in this same file, with the `site_p1_median` estimator.

| pos | mouse | floor 60 Hz median | floor 60 Hz p1 | floor slope p1 | grounded |
|---|---|---|---|---|---|
| A1 | HLBCSD11 | 4314 µV | 2343 | **−2.437** | yes |
| A2 | HLBCSD12 | 4606 | 3596 | −0.746 | yes |
| **B1** | **HLBCSD17** | **2186** | 1953 | −1.266 | **yes** |
| B2 | HLBCSD14 | 4371 | 1753 | −1.290 | yes |
| C1 | HLBCSD15 | 5215 | 4784 | −0.963 | yes |
| C2 | HLBCSD16 | 4964 | 3310 | −1.021 | yes |
| D1 | HLBCSD19 | 3425 | 1116 | −1.721 | yes |
| D2 | HLBCSD18 | 3175 | 1527 | −0.861 | yes |

✅ **All eight chips read grounded.** There is no floating headstage anywhere on the rig for the
first time in this cohort. B1 is the lowest at 2186 µV but is far above the 800 µV bar and is
stable to within ±150 µV across all 21 hourly bins.

## Rung 2 — CONNECTION, whole run

EEG is judged on the **slope** criterion, EMG on **hum plus amplitude**. Never the other way round:
real muscle is broadband and therefore spectrally flat, so a slope test calls a working EMG dead.

| pos | mouse | EEG rms | slope | lf/hf | EEG % | longest EEG block | EMG rms | EMG % | BOTH % | longest BOTH | EEG railing | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **D2** | HLBCSD18 | 92 µV | −1.51 | 14.29 | **99.3** | **3.09 h** | 52 µV | 81.1 | **81.0** | **0.61 h** | 0.03% | ✅ **PASS** |
| **C1** | HLBCSD15 | 103 | −1.48 | 15.32 | **92.2** | **1.53 h** | 458 | 0.0 | 0.0 | — | **0.00%** | EEG only |
| **B1** | **HLBCSD17** | **93** | **−1.47** | **17.34** | 77.8 | 0.21 h | **44** | **94.9** | 75.0 | 0.21 h | **0.00%** | connected, ⚠️ not robust |
| C2 | HLBCSD16 | 3284 | −0.43 | 2.99 | 42.8 | 0.41 h | 1010 | 0.0 | 0.0 | — | 54.0% | EEG only, intermittent |
| A2 | HLBCSD12 | 3856 | −0.39 | 3.42 | 26.6 | 0.47 h | 554 | 0.2 | 0.0 | — | 68.7% | EEG only, **degraded** |
| D1 | HLBCSD19 | 2701 | −0.02 | 1.75 | 3.9 | 0.02 h | 1124 | 0.0 | 0.0 | — | 75.4% | FAIL |
| A1 | HLBCSD11 | **94** | **−1.33** | **13.46** | **0.0** | — | 48 | **93.9** | 0.0 | — | 6.1% | 🔴 **EEG UNJUDGEABLE**, EMG excellent |
| B2 | HLBCSD14 | 4394 | −0.11 | 1.56 | 0.0 | — | 104 | 68.2 | 0.0 | — | 99.1% | EEG open, EMG good |

"Usable fraction" is this project's own term: the percentage of 10 s epochs in which the channel's
spectrum beats the 1st percentile of **amplifier inputs with no wire attached**, recorded through
the same chip in the same file. It is a **connection** measure, not a data quality score and not a
sleep result.

### Block structure — why 77.8% can still fail a 15 minute bar

| pos | usable % | blocks | median block | longest | gaps that are a single epoch | time inside blocks ≥ 15 min |
|---|---|---|---|---|---|---|
| D2 | 99.3 | 43 | 710 s | **185.2 min** | 83.3% | **18.20 h** |
| C1 | 92.2 | 281 | 40 s | **91.8 min** | 51.8% | **12.26 h** |
| C2 | 42.8 | 209 | 40 s | 24.5 min | 41.8% | 2.42 h |
| A2 | 26.6 | 243 | 30 s | 28.5 min | 26.9% | 0.73 h |
| **B1** | **77.8** | **747** | **20 s** | **12.8 min** | **55.5%** | **0.00 h** |
| D1 | 3.9 | 164 | 10 s | 1.3 min | 38.7% | 0.00 h |

🔑 **B1 is connected three quarters of the time and never for a quarter of an hour at a stretch.**
Read the sensitivity section before concluding anything from that.

## ✅ The B1 swap: the fault followed the animal and its tether

| | 24 h run, HLBCSD13 | this run, HLBCSD17 |
|---|---|---|
| chip floor 60 Hz | **246 µV** (floating) | **2186 µV** (grounded) |
| EEG rms | 486 µV | **93 µV** |
| EEG slope | −1.58 | −1.47 |
| EEG lf/hf | 11.01 | **17.34** |
| lf/hf of the chip's own floor, p99 | — | 3.81 |
| EEG usable | 1.0% | 77.8% |
| EMG rms | 2761 µV | **44 µV** |
| EMG usable | 0.0% | **94.9%** |
| railing, either channel | — | **0.00%** |

Same port, same slot, same cable, same splitter branch, same XDAQ input. Only the animal and its
tether changed. **B slot 1, its cable and its XDAQ input are exonerated.** The remaining ambiguity
is that the swap changed the animal AND the tether at once, so it separates the position from the
consumable but not the animal's ground wire from the tether's conductor.

⚠️ **B1 and C1 are the two cage positions where animals reach their tethers.** On 2026-08-19 the
W-SD B1 animal chewed and cut its tether; on 2026-08-22 both the B1 and C1 animals were found
missing with their tethers; on 2026-08-26 the S-SD B1 animal's tether was chewed; and now the S-SD
C1 tether has failed at its centre. That is four events at two positions across two cohorts. The
explanation is mechanical and behavioural at those cage locations, not electrical at those ports.

### ⚠️ B1's number is not robust

Sensitivity of the EEG usable fraction and longest block to a ±25% move in the floor slope
threshold:

| pos | threshold | −25% | point | +25% |
|---|---|---|---|---|
| **B1** | −1.266 | **99.1% / 210.7 min** | **77.8% / 12.8 min** | **37.6% / 5.7 min** |
| C1 | −0.963 | 92.6% / 92.7 min | 92.2% / 91.8 min | 83.8% / 24.8 min |
| C2 | −1.021 | 43.0% / 24.5 min | 42.8% / 24.5 min | 41.3% / 20.2 min |
| D2 | −0.861 | 99.4% / 185.2 min | 99.3% / 185.2 min | 97.5% / 89.0 min |
| A2 | −0.746 | 26.6% / 28.5 min | 26.6% / 28.5 min | 26.5% / 28.5 min |

C1, C2, D2 and A2 move by less than 1.5 points. **B1 moves by 61 points and its longest block moves
by a factor of 37.** The reason is that the failing epochs miss by a median slope margin of only
**0.091**, and chip B1's floor p1 is unusually steep for a chip whose wire-free sites are partly
quiet: `B/14`, `B/15` and `B/16` sit at 107, 165 and 68 µV rms where the rest of that chip's floor
sits at 890 to 4317 µV.

🔑 **Report B1 as CONNECTED, on the amplitude, slope, lf/hf separation and zero railing, and do not
attach a usable percentage to it in any figure or any report to the professor.**

## 🔴 C1 — the tether IS damaged, and the data says which conductor

Andrea's observation: the C1 tether failed structurally at its **centre**, and railing was visible
when the tether was not held straight.

What the recording contains:

| | C1 EEG (`C/1`) | C1 EMG (`C/2`) |
|---|---|---|
| epochs with any railed sample | **0 of 7,317** | 6 of 7,317 (0.08%) |
| max rms over the whole run | **297 µV** | — |
| railing threshold | 6,376.8 µV (99.8% of ADC full scale) | |
| 60 Hz median | 62 µV | **599 µV** |
| its chip's wire-free floor | 5,215 µV | 5,215 µV |
| ratio to floor | 0.01 | **0.11** |
| rms | 103 µV | 458 µV |
| slope | −1.48 | −0.62 |
| usable | 92.2% | **0.0%** |
| signature | **connected** | **damaged / partially conducting cable** |

And the shared-path discriminator, |r| between an animal's own two channels, sampled over 200
epochs spread across the run:

| pos | A1 | A2 | B1 | B2 | **C1** | C2 | D1 | D2 |
|---|---|---|---|---|---|---|---|---|
| median &#124;r&#124; | 0.074 | 0.116 | 0.076 | 0.128 | **0.091** | 0.171 | **0.208** | 0.059 |

Working animals sit at 0.07 to 0.09. One damaged cable feeding both channels sits at 0.5 to 0.75.
**C1 is at 0.091.** D1 at 0.208, with a 75th percentile of 0.51, is the one that looks like a
shared path fault, which agrees with HLBCSD19's registry note about a tether damaged by climbing.

> [!warning] What this means, stated carefully
> C1's EMG conductor is damaged and has been since at least the 24 h run of 25 August, where it read
> 455 µV against the same floor. That is consistent with a tether failing at its centre.
> **C1's EEG conductor was still intact and still delivering the second best signal on the rig at
> 09:09 on 27 August, and it did not rail once in 20.3 hours.**
> So the railing seen on the bench was **not captured in this file**. Three possibilities, in order
> of how likely they look: the break progressed after the recording was stopped; the railing was
> seen while handling the tether outside the recording window; or the position label needs
> checking, because **A1 is the one channel in this run that shows brief rail hits on an otherwise
> healthy-amplitude EEG** (see below). This is worth resolving before the tether is replaced.

### The only intermittent-railing channel in this run is A1

| pos | EEG rms median | % epochs with clean amplitude | % epochs with any railed sample | median railed fraction when it happens |
|---|---|---|---|---|
| **A1** | **94 µV** | 89.1 | **6.11** | **0.0022** |
| A2 | 3856 | 26.6 | 68.74 | — |
| B2 | 4394 | 0.0 | 99.11 | — |
| C2 | 3284 | 43.0 | 54.02 | — |
| D1 | 2701 | 21.6 | 75.41 | — |
| B1, C1, D2 | 93, 103, 92 | 100, 92.6, 99.5 | **0.00, 0.00, 0.03** | — |

A2, B2, C2 and D1 rail because they are **open**: their rms sits at 3000 to 4400 µV, riding the
rail continuously. **A1 is different.** Its EEG sits at 94 µV, the amplitude of real EEG, and 6.11%
of its epochs contain a brief rail hit lasting a median of 22 samples in 10,000. Those hits cluster
in the dark phase (22:50 to 02:50) and in one burst at 07:50. **That is the signature of a
mechanical contact transient on a working channel**, which is what "railing when the tether is not
straight" would look like in a file.

## 🔴🔴 A1's 0.0% is a threshold artefact, not an animal

The animal did not change between the two runs. The floor did.

| | 24 h run `uid0825` | this run `uid0826` |
|---|---|---|
| A1 EEG rms | 94 µV | **94 µV** |
| A1 EEG slope | −1.36 | **−1.33** |
| A1 EEG lf/hf | 14.67 | **13.46** |
| **chip A1 floor slope p1** | **−1.523** | **−2.437** |
| A1 EEG usable | 31.0% | **0.0%** |

Per-site p1 slopes of chip A1's fourteen wire-free inputs this run: −0.948, −0.977, −1.176, −1.285,
−1.308, −1.623, **−2.421, −2.452, −2.743, −2.758, −2.819, −2.874, −2.969, −3.436**. The median of
those is the threshold, −2.437, so **half of that chip's wire-free inputs are spectrally steeper
than the animal's own EEG**. The same chip's floor reaches an lf/hf 99th percentile of **27.78**
against the animal's 13.46.

Compare every other chip, whose floor slope p1 moved by less than 0.25 between the two runs:

| pos | floor slope p1, 0825 | 0826 | shift |
|---|---|---|---|
| **A1** | −1.523 | **−2.437** | **−0.914** |
| A2 | −0.768 | −0.746 | +0.022 |
| B1 | −2.056 | −1.266 | +0.789 (the swap) |
| B2 | −1.505 | −1.290 | +0.216 |
| C1 | −1.065 | −0.963 | +0.102 |
| C2 | −1.179 | −1.021 | +0.158 |
| D1 | −1.728 | −1.721 | +0.007 |
| D2 | −0.973 | −0.861 | +0.112 |

> [!danger] The per-chip floor fix removed the false PASS. It did not remove the false FAIL.
> `floor_stats()` was made per-chip on 2026-08-26 and the `site_p1_median` estimator was added so
> that one bad site could not set a chip's bar. That works: no single site drives A1's threshold
> here, **seven of them do**. The guard that exists refuses a verdict when a chip is **ungrounded**.
> There is no guard for a chip whose floor is grounded but **spectrally contaminated**, and on that
> chip the slope criterion cannot discriminate in either direction.
> **A1's EEG should read UNJUDGEABLE for this recording, not 0.0%.** It is quoted as 0.0% in the
> table above only because that is what the current code returns.

A1's **EMG is excellent and unaffected**: 48 µV, 93.9% usable, and the strongest circadian
amplitude ratio on the rig.

## Light and dark

The run starts at 12:50, which is ZT3.8, and ends at ZT0.15. It covers **one full dark phase and
two partial light phases**: 2,997 light epochs (41.0%) against 4,320 dark. Light and dark are
therefore **not** equally weighted, and this is one dark phase, so nothing here replicates the 24 h
result.

| pos | EEG usable, light | dark | drop | same drop in the 24 h run |
|---|---|---|---|---|
| D2 | 99.9% | 99.0% | **−0.9** | −2.7 |
| A2 | 27.2 | 26.1 | −1.1 | −32.1 |
| C2 | 46.8 | 40.0 | −6.8 | −34.1 |
| C1 | 98.0 | 88.1 | −10.0 | −15.7 |
| B1 | 86.2 | 72.1 | −14.1 | — |

⚠️ **A2 and C2's drops shrank only because they had already collapsed by daylight.** Their light
phase figures are 27% and 47%, so there is little left to lose in the dark. D2 is immune for the
second run running.

EMG amplitude, median rms, descriptive only and **not** a sleep result:

| pos | light | dark | dark/light |
|---|---|---|---|
| **A1** | 17.7 µV | 77.7 µV | **4.40×** |
| D2 | 35.3 | 76.0 | 2.15× |
| B1 | 38.6 | 63.2 | 1.64× |
| B2 | 94.2 | 143.7 | 1.53× |

A1 reproduces its 4.29× from the 24 h run and stays the closest match to the 48 h control's
31 µV light / 73 µV dark.

## 🔴 A2 and C2 have genuinely degraded

The warning written on 26 August is confirmed. These are real electrode failures, not thresholds:

| | A2 (HLBCSD12) 0825 → 0826 | C2 (HLBCSD16) 0825 → 0826 |
|---|---|---|
| EEG rms | 124 → **3856 µV** | 124 → **3284 µV** |
| EEG slope | −1.49 → **−0.39** | −1.27 → **−0.43** |
| EEG lf/hf | 13.91 → **3.42** | 9.52 → **2.99** |
| EEG usable | 79.5% → **26.6%** | 48.8% → **42.8%** |
| railing | — → **68.7%** | — → **54.0%** |

Both now flip between open (≈4,500 µV) and connected (≈110 µV) **at whole-hour scale**: C2's hourly
EEG rms this run reads 4462, 4438, 111, 4445, 136, 103, 121, 110, 107, 4568, … That is the
movement-dependent contact pattern, at a slower cadence than usual.

## What this run is good for

- **D2 (HLBCSD18)** is a genuine 18.2 h scoreable EEG+EMG animal and the obvious candidate for the
  blind-scoring pack. It has now passed strict rung 2 on three consecutive recordings.
- **C1 (HLBCSD15)** gives 12.26 h of EEG inside long blocks and is EEG-only. Usable for spectral
  work, not for anything that needs muscle tone.
- **A1 (HLBCSD11)** gives excellent EMG with the rig's strongest circadian amplitude ratio, and its
  EEG is probably fine but currently unjudgeable.
- **B1 (HLBCSD17)** is a working new animal whose number cannot yet be trusted.

## Still open

1. 🔴 **Add a second rung-2 validity guard for a spectrally contaminated floor.** Same shape as the
   ungrounded guard: if the chip's wire-free floor is itself as steep as, or steeper than, real EEG
   — for instance the floor's lf/hf p99 exceeding the animal's median, or more than a third of its
   sites having a p1 slope below −2 — refuse the verdict and return **UNJUDGEABLE**. Without it the
   pipeline can now manufacture a FAIL as easily as it once manufactured a PASS.
2. 🔴 **Resolve the C1 railing report before replacing the tether.** The file contains zero railed
   epochs at C1 and 447 at A1. Confirm which physical cage the observation came from.
3. 🟡 **Replace the C1 tether** — its EMG conductor is already gone and the EEG conductor is the
   only thing still working on that animal. Tether change means isoflurane, so it is a scheduling
   decision, not a bench job. **No surgery is implied.**
4. 🟡 **B1's flicker.** Decide whether a 0.091 slope margin is a real dropout or a bar artefact.
   The cheapest test is another recording on the same animal once the cohort is otherwise stable.
5. 🟡 **A2 and C2 are failing.** They were the two best 1 h channels on 24 August. Decide whether
   they stay on the rig.
6. The blind-scoring **kappa** is still the gate on every rung 4 statement.

## Provenance

- Raw: `~/radix/data/allego_1__uid0826-12-50-16{_data,_timestamp}.xdat` + `.xdat.json`
- Features: `~/eeg-processed/2026-08-26/feat_uid0826-12-50-16.npz`, 7,317 × 128, 10 s epochs
- Engine: `~/Monitoring_project/eeg-emg-analysis/core/criteria.py` and `core/qc_thresholds.py`
- Cohort: `~/Monitoring_project/eeg-emg-analysis/cohorts/S-SD.yaml`
- Related: [[2026-08-21-39h-run-score]] · [[03-troubleshooting/symptoms/per-animal-failure-signatures|per-animal failure signatures]] · [[02-procedures/eeg-artefact-and-railing-rejection-policy|artefact and railing policy]]

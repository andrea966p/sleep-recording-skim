---
tags: [experiment, eeg, emg, W-SD, sleep-deprivation, active]
created: 2026-08-27
status: RUNNING
recording: allego_2__uid0827-12-58-32
cohort: W-SD
---

# Recovery sleep after 7 days of chronic sleep deprivation, batch W-SD

> [!warning] 🔴 THIS RUN IS IN TROUBLE. FIRST-HOUR SCREEN: 1 OF 8 POSITIONS GIVES EEG.
> Only **D2** produces real EEG. The other seven give nothing usable on EEG. If the run is left as
> it is, the recovery-sleep endpoint rests on a single animal, and the animals are sampled
> tomorrow, so **there is no second chance at this timepoint.**

## What this recording is

| | |
|---|---|
| Recording | `allego_2__uid0827-12-58-32` |
| Started | 2026-08-27 12:58:32 KST, as the SD day ended at 13:00 |
| Planned stop | 2026-08-28 09:00 KST, ~20.0 h |
| Cohort | `W-SD`, HLBCSD01 to HLBCSD10, UV water arm, chronic sleep deprivation |
| CSD window | start 2026-08-21, end 2026-08-28 = **7 days** |
| Sampling | 2026-08-28, immediately after this recording |
| Format | 1000 Hz, 262 channels, mode verified correct |
| Watchdog | running, `~/eeg-processed/2026-08-27/watchdog_uid0827-12-58-32.log` |

This is the **recovery-sleep timepoint**: the sleep rebound after a week of deprivation, recorded
in the last 20 h before the animals are sampled. It is the endpoint the whole W-SD arm exists for.

> [!caution] The position map is assumed, not confirmed
> The animal names below come from the `XDAQ position` column of the registry, which holds one
> current value per animal and was last saved on 2026-08-24, while this batch was **off** the rig
> and S-SD was on it. **Confirm the map at the bench before any animal name goes into a result.**
> The measurements themselves are position-level and stand regardless.

## First-hour screen, 12:58 to 13:58

Per-chip wire-free floor, this file, `site_p1_median` estimator.

| pos | mouse (assumed) | chip floor 60 Hz | EEG rms | slope | lf/hf | floor lf/hf p99 | EEG % | EEG rail | EMG rms | EMG % | EMG rail | BOTH % | reading |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **D2** | HLBCSD08 | 4802 µV | **148** | **−1.89** | **30.69** | 1.98 | **53.1** | 0.0% | **20** | **98.6** | 0.0% | **52.5** | ✅ **real EEG + real EMG** |
| C2 | HLBCSD06 | 4457 | 4181 | +0.13 | 1.31 | 2.95 | 0.8 | **98.3%** | 17 | 95.0 | 2.5% | 0.8 | EEG open, EMG works |
| B2 | HLBCSD04 | 4639 | 4125 | +0.13 | 1.30 | 3.32 | 0.0 | **100%** | 762 | 0.0 | 1.9% | 0.0 | EEG open |
| C1 | HLBCSD03 | 3566 | 3855 | −0.03 | 1.09 | 4.12 | 0.0 | **100%** | 3336 | 0.0 | **100%** | 0.0 | 🔴 both open |
| B1 | HLBCSD09 | **825** | 277 | −0.18 | 1.46 | 2.56 | 0.0 | 0.0% | 4364 | 0.0 | **100%** | 0.0 | 🔴 EEG floating, EMG open |
| A1 | HLBCSD01 | **1294** | 50 | −0.08 | 1.27 | 5.22 | 0.0 | 0.0% | 20 | 99.7 | 0.0% | 0.0 | EEG floating |
| A2 | HLBCSD02 | **1634** | 69 | −0.08 | 1.15 | 5.50 | 3.3 | 0.0% | 48 | 100.0 | 0.0% | 3.3 | EEG floating |
| D1 | HLBCSD07 | **1804** | 124 | +0.05 | 0.95 | 3.26 | 3.6 | 0.8% | 159 | 43.1 | 14.2% | 1.7 | EEG floating |

**Only D2 separates on lf/hf** — 30.69 against its own chip's wire-free 99th percentile of 1.98.
Every other position sits below its own floor, which is the definition of not connected.

> [!note] "EMG 100%" on A1 and A2 is not evidence of a working muscle channel
> The EMG criterion is "quiet, and quieter than the wire-free floor". A **floating** input is also
> quiet. The hum guard that catches this exists for EEG only. A1 and A2 read 99.7% and 100% EMG at
> 20 and 48 µV on chips whose ground is down; treat those as unproven until they show amplitude
> that tracks behaviour across the dark phase.

## 🔴 Four chips lost most of their ground reference overnight

Floor 60 Hz median, the 20 h run that ended this morning against the first hour of this one. The
chips are rig hardware and did not move; what changed is the animals and their tethers.

| pos | 2026-08-26 run | 2026-08-27 first hour | |
|---|---|---|---|
| **A1** | 4314 µV | **1294** | 🔴 down 70% |
| **A2** | 4606 | **1634** | 🔴 down 65% |
| **B1** | 2186 | **825** | 🔴 down 62%, barely over the 800 µV bar |
| **D1** | 3425 | **1804** | 🔴 down 47% |
| B2 | 4371 | 4639 | normal |
| C1 | 5215 | 3566 | normal |
| C2 | 4964 | 4457 | normal |
| D2 | 3175 | 4802 | normal |

A weak floor means the headstage has a poor ground reference, and the ground reference arrives
through the animal and its tether. **Four weak grounds plus three open channels, after seven days
in a deprivation chamber, points at the tether chain rather than at eight simultaneous implant
failures.** HLBCSD05, sacrificed on 08-21, had its **electrode found intact at post mortem**, which
is direct evidence for the same conclusion.

## What can still be done tonight

1. **Check the headstage seating and the tether connectors at A1, A2, B1 and D1.** Those four are
   quiet and flat with a weak chip ground, which is the reseat-and-recheck signature, not an
   electrode failure. A connector re-mate needs no anaesthesia.
2. **B1, C1 and B2 carry open, railing channels.** B1 and C1 are the chewing cages and both of
   those animals have "ate the tether" in the registry already.
3. 🛑 **Do not stop and restart the recording for a marginal gain.** D2 is producing the endpoint
   and a restart splits it. If anything is re-seated, note the wall-clock time here so the file can
   be cut at that boundary.
4. **Re-screen an hour after any intervention** rather than trusting the Allego display.

## Owed after the run

- Rung 0, then rung 2 with the per-chip floor, the same as the S-SD runs.
- The **recovery-sleep** comparison this experiment exists for: this file against the 39.7 h
  baseline `allego_1__uid0819-17-25-20` taken on the same batch before CSD started on 08-21.
  🛑 Only positions that pass rung 2 in **both** files can enter that comparison, and on today's
  first hour that is **D2 alone**.
- 🛑 Everything about sleep architecture stays PROVISIONAL until the blind-scoring kappa exists.

## Related

[[2026-08-21-39h-run-score]] · [[2026-08-27-B1-swap-baseline-20h-run]] ·
[[2026-08-24-S-SD-first-hour-screen]] · [[2026-08-25-S-SD-24h-ZT0-run]] ·
manifest `eeg-emg-analysis/cohorts/W-SD.yaml`

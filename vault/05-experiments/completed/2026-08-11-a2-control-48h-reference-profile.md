---
title: A2, the control mouse, 48 hours, two complete circadian cycles
date: 2026-08-11
status: completed
tags: [eeg, emg, control, circadian, recording, reference]
---

# A2 over 48 hours: the reference profile for what a working animal looks like

> [!abstract] TL;DR for non-technical readers
> **What this is.** A2 is our control mouse, the old B1 animal, sitting in port A slot 2 on a
> short soldered and resin encapsulated tether. It is the one animal that has always worked. We
> recorded it for **48 hours straight** and this page is what its signal looks like.
>
> **Why it exists.** Every other page in this vault is about things being broken. This one is the
> opposite: it is the **reference profile**, the thing a good channel should be compared against.
> It also happens to be the strongest physiological evidence the project has produced.
>
> **How to read it.** The headline is that **47.09 of 48.19 hours are usable**, the
> electromyogram (EMG) tracks sleep properly, and **the whole thing repeats almost exactly on the
> second day**. Read § "Day to day" if you read nothing else.

Recording **`allego_0__uid0809-09-00-00`**, started 2026-08-09 09:00:00 KST, stopped by andrea on
2026-08-11 at about 09:11. Related: [[2026-08-09]], [[2026-08-08-ground-fix-post-repin-night]].


> [!note] ✅ CHECKED AGAINST THE 2026-08-21 FLOOR BUG — THIS PAGE'S NUMBERS SURVIVE
> The usable fractions here were computed with the pooled wire-free floor, which was later found to
> contradict the project's own "same chip" definition. On **this** recording the pooled value
> (-1.352) is **harsher** than the A2 chip's own floor (-0.976), so the 47.09 of 48.19 h usable is a
> **conservative** figure: correcting the floor can only raise it, not lower it.
>
> ⚠️ Two caveats. The **D1** chip is the one exception in this file (own floor -1.666, harsher than
> pooled), so any D1 number here may be flattered. And the fractions have **not** been recomputed —
> this is a statement about the direction of the error, not a re-measurement.
> Detail: [[05-experiments/completed/2026-08-21-39h-run-score]].

## The recording

| | |
|---|---|
| duration | **48.19 h** |
| size | **181.8 GB** |
| data samples | 173,496,576 |
| timestamp samples | 173,496,576 |
| remainder bytes | **0 and 0** |
| error string | empty |

✅ **The file is intact**: data and timestamp agree to the sample and neither has a partial record.

⭐⭐ **IT STARTED AND ENDED AT ZT0.** Lights come on at 09:00, so the recording covers **exactly
two complete circadian cycles**, 24.2 h of light phase and 24.0 h of dark phase. That balance is
what makes the day-to-day comparison below possible, and the previous run, which started at 16:17
part way through a light phase, could not support it.

> [!important] ⭐ Start long runs at ZT0
> This is the first recording we have that begins at lights on. It cost nothing and it made the
> light and dark phases equal in length, which removes an awkward correction from every circadian
> number. **Make a ZT0 start the default for any run longer than a day.** Helper:
> `eeg-emg-analysis/qc/start_recording_at.py HH:MM:SS`.

## Signal quality, scored against 26 unwired inputs inside the same file

Script: **`eeg-emg-analysis/qc/animal_signal_report.py`**, new for this. The floor control is the
set of real amplifier inputs on port A that carry no wire, `/4`-`/16` and `/36`-`/48`, recorded
simultaneously. ⚠️ **Never include `/17`-`/32` or `/49`-`/64`**, they are inactive slots, are
internally tied, and would destroy the control.

Floor in this file: slope 1st percentile **-1.11**, median -0.14, median 60 Hz amplitude
**2754 µV**.

| | EEG `A/33` | EMG `A/34` | floor |
|---|---:|---:|---:|
| median 1-40 Hz spectral slope | **-1.52** | -1.06 | -0.14 |
| median root mean square | 69.8 µV | 59.7 µV | — |
| median 60 Hz amplitude | **36.0 µV** | 32.6 µV | **2754 µV** |
| **railed epochs** | **0.0%** | **0.0%** | — |

✅ **Falsification check passed: the floor channels score 0.00 percent usable.**

**EEG usable 97.7 percent of 48.19 h, which is 47.09 hours.** Longest unbroken block 96.3 min
(1.61 h). Light phase **99.1 percent**, dark phase **96.3 percent**.

⭐⭐⭐ **ZERO RAILED EPOCHS IN 17,349.** This animal does not drop out. For comparison, on the old
cohort railing was the open-electrode signature and several animals railed in 100 percent of
their epochs.

> [!quote] Paper-ready
> Continuous recording from a single chronically implanted mouse yielded 47.1 of 48.2 hours
> (97.7 percent) of electroencephalogram meeting a spectral-slope criterion derived from
> simultaneously recorded unwired amplifier inputs, with no railed epochs.

## Physiology on the usable epochs

| band | fraction of 1-40 Hz power |
|---|---:|
| delta 1-4 Hz | 0.351 |
| theta 6-9 Hz | 0.211 |
| sigma 10-15 Hz | 0.079 |

### The EMG works, and it is the only one on the rig that does

The real test for an electromyogram is **state dependence**: muscle tone must fall when the animal
sleeps. Correlating 1-minute EMG amplitude against the same animal's delta fraction, over 2836
usable minutes:

| | r | n minutes |
|---|---:|---:|
| whole recording | **-0.645** | 2836 |
| light phase alone | **-0.514** | 1440 |
| dark phase alone | **-0.492** | 1396 |

**Negative in both phases separately**, so this is not an artefact of the light/dark difference
driving both variables. ⚠️ **Sign convention: I correlate delta against EMG amplitude, so a
working pair is NEGATIVE.** The vault's older `r@1min +0.603` for this animal uses the opposite
convention. **The magnitudes are comparable, the metrics are not identical, do not table them
together.**

⭐ **And the raw amplitude says the same thing with no scoring at all: median EMG is about 31 µV
through the light phase and about 73 µV through the dark phase.** It more than doubles when the
animal should be active. That is an independent confirmation from a different channel and a
different measure, and it needs no threshold whatsoever.

## Circadian, with the mandatory threshold sweep

Otsu split on the delta fraction = 0.386. The council established that our circadian check is
**threshold-dependent**, so quoting a single percentage is not allowed here. The ±25 percent
sweep:

| threshold | × Otsu | asleep LIGHT | asleep DARK | gap, points |
|---:|---:|---:|---:|---:|
| 0.289 | 0.75 | 85.5% | 51.8% | 33.7 |
| 0.347 | 0.90 | 72.3% | 29.6% | 42.7 |
| **0.386** | **1.00** | **61.6%** | **19.8%** | **41.8** |
| 0.424 | 1.10 | 50.5% | 13.6% | 36.9 |
| 0.482 | 1.25 | 32.9% | 7.4% | 25.5 |

> [!important] ⭐⭐ This is the important paragraph on this page
> **The absolute number is still threshold-dependent and must not be quoted as a fact**: "asleep
> in the light phase" moves from 85.5 to 32.9 percent across the sweep. That limitation stands
> and this page does not repair it.
> **But light is above dark at EVERY threshold, by 25.5 to 42.7 points, always in the same
> direction.** The *ordering and the size of the separation are threshold-INDEPENDENT even though
> the value is not.* ⭐ **The pipeline knows nothing about the clock**, so a light/dark difference
> of this size is genuine **external validation**, and it is the strongest form of it we have.

🛑 **NOTE THE TRAP AND DO NOT FALL INTO IT.** The 0.90× row lands on 72.3 percent, which sits
right on the literature value of roughly 70 percent for a mouse. **Choosing that threshold because
it matches the number we are validating against would be circular** and is banned by
[[blind-scoring-and-kappa]]. The Otsu value is the one that was derived without looking at the
answer, and it is the one reported.

## Per ZT hour, ZT0 = lights on, both cycles pooled

| ZT | phase | usable | asleep | med delta | med EMG µV |
|---:|---|---:|---:|---:|---:|
| 0 | LIGHT | 99% | 56% | 0.405 | 53.1 |
| 1 | LIGHT | 99% | **76%** | 0.480 | 30.3 |
| 2 | LIGHT | 99% | 67% | 0.451 | 30.8 |
| 3 | LIGHT | 99% | 73% | 0.467 | 30.8 |
| 4 | LIGHT | 100% | 65% | 0.430 | 31.3 |
| 5 | LIGHT | 99% | 71% | 0.464 | 30.1 |
| 6 | LIGHT | 100% | 57% | 0.410 | 33.1 |
| 7 | LIGHT | 98% | 62% | 0.425 | 30.7 |
| 8 | LIGHT | 99% | 57% | 0.406 | 32.4 |
| 9 | LIGHT | 99% | 56% | 0.406 | 31.0 |
| 10 | LIGHT | 99% | 49% | 0.381 | 35.7 |
| 11 | LIGHT | 99% | 52% | 0.392 | 32.2 |
| 12 | dark | 96% | 45% | 0.374 | 47.4 |
| 13 | dark | 94% | 14% | 0.289 | 76.5 |
| 14 | dark | 97% | 10% | 0.277 | 80.2 |
| 15 | dark | 96% | 18% | 0.292 | 69.7 |
| 16 | dark | 96% | **8%** | 0.271 | 74.0 |
| 17 | dark | 97% | 8% | 0.269 | 72.7 |
| 18 | dark | 97% | 10% | 0.271 | 75.9 |
| 19 | dark | 99% | **30%** | 0.305 | 68.9 |
| 20 | dark | 97% | **32%** | 0.320 | 67.5 |
| 21 | dark | 96% | 18% | 0.298 | 75.0 |
| 22 | dark | 97% | 26% | 0.305 | 72.5 |
| 23 | dark | 95% | 19% | 0.300 | 76.1 |

Three features, and all three are what a mouse is supposed to do:

1. **Sleep pressure decays across the light phase**, 76 percent asleep at ZT1 falling to 49
   percent by ZT10, with delta following it down from 0.480 to 0.381.
2. **A sharp transition at lights off.** ZT12 is 45 percent and ZT13 is 14 percent, and the EMG
   jumps from 47 to 77 µV across the same boundary.
3. ⭐ **A mid-dark rest bout at ZT19-20**, 30 and 32 percent asleep against 8 to 18 percent either
   side. **It shows on both channels at once**: delta rises to 0.305 and 0.320 while the EMG falls
   to 68.9 and 67.5 µV. Two independent measures moving together is what a real behavioural state
   looks like, as opposed to a scoring artefact.

## ⭐⭐⭐ Day to day: the measurement replicates on itself

Each 24 hour cycle scored separately, **using the Otsu threshold from the whole file applied
unchanged to both**, so neither cycle was fitted on its own data.

| cycle | hours | usable | asleep LIGHT | asleep DARK | EMG light | EMG dark | r(delta, EMG) |
|---:|---|---:|---:|---:|---:|---:|---:|
| **1** | 0-24 | 98% | **62.5%** | 17.6% | **31.0 µV** | 76.8 µV | -0.673 |
| **2** | 24-48 | 98% | **61.1%** | 22.1% | **31.1 µV** | 70.1 µV | -0.618 |

⭐⭐⭐ **THIS IS THE STRONGEST NUMBER ON THE PAGE. Asleep in the light phase differs by 1.4
points between two consecutive days, and the median light-phase EMG differs by 0.1 µV.** A
within-animal replication of the entire measurement, on a rig whose whole history is
irreproducibility.

⚠️ **The dark phase replicates less tightly**, 17.6 against 22.1 percent, a 4.5 point difference.
Same direction, same order of magnitude, but do not present the dark phase as being as stable as
the light phase. Two cycles is also **n = 2 days on n = 1 animal**, and a replication is not a
population.

## What this page does and does not establish

| ✅ Established | ❌ Not established |
|---|---|
| A single animal on this rig can give **47 h of usable EEG in 48**, with zero railing | That any other animal can. **A2 is one mouse and it is the old, long-implanted one** |
| The **EMG is genuinely state-dependent**, in both phases separately | That the EMG works on any re-pinned mouse. It does not, see below |
| The **light/dark separation survives the whole ±25% threshold sweep** | The **absolute** percentage asleep. Still threshold-dependent |
| The whole measurement **replicates across two consecutive days** | Accuracy. **There is still no kappa against a human scorer** |
| A **ZT0 start** makes the phases equal and costs nothing | Anything about REM. No REM claim is made anywhere on this page |

## Still open

- 🔴 **The kappa.** Nothing here measures whether our staging agrees with a human. Packs are built
  and the decision rules are pre-registered in [[blind-scoring-and-kappa]]. **Every accuracy claim
  is still gated behind it**, including everything on this page that uses the word "asleep".
- 🔴 **A positive control.** Every control we have is negative: they prove we do not invent signal,
  not that we find it. [[positive-control-known-signal-injection]], specified and not scheduled.
- 🔴 **The rest of the cohort.** A2 looks like this. On 2026-08-08 the six re-pinned mice gave
  57 to 72 percent usable EEG at best, **their EMG showed no state dependence**, and **the
  electrocardiogram was dead on 7 of 7**. This page is the control, not the fleet.
- 🔴 **The dark phase of `allego_0__uid0808-16-17-36` is still unscored.**
- **A1's ground wiring** is still not fixed. Excellent control, one animal producing no data.
- **No video** since the cameras were removed on 2026-08-04, so nothing here can be checked
  against behaviour.
- The **1.10 Hz hardware high-pass** still eats the bottom of delta, and every delta number on
  this page inherits that.

Per-epoch arrays saved to `allego_0__uid0809-09-00-00_A33_report.npz` for re-analysis without
re-reading 182 GB.

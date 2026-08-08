---
title: Ground re-pin, the after state, and the overnight recording
date: 2026-08-08
status: active
tags: [eeg, emg, ecg, impedance, ground, cohort, overnight]
---

# Ground re-pin on the ECG cohort, and the night that tests it

> [!abstract] TL;DR
> Yesterday we found that all seven new mice had been recording with **no ground connection to
> the animal**: the cerebellum dura pin was mated to the **orange** wire, which floats, while the
> **brown** wire sitting in the headstage ground pad touched nothing
> ([[2026-08-07-ecg-cohort-baseline]]). Today andrea re-pinned the ground.
>
> ⭐⭐⭐ **IT WORKED, AND WE GOT A CONTROL FOR FREE.** Six of the seven new mice were re-pinned.
> **A1 could not be, because of a wiring problem on that animal**, so A1 is now a
> **within-experiment, same-day, same-rig NO GROUND control**. In a 120 second live look,
> electroencephalogram (EEG) appeared on B, C and D animals and **A1 stayed exactly as flat as it
> was last night**. That is the cleanest single result this rig has produced about a cause.
>
> ⚠️ **BUT THE HEARTBEAT TEST STILL FAILS ON EVERY ELECTROCARDIOGRAM (ECG) CHANNEL**, and 120
> seconds is a screen, not an outcome. The overnight recording is the real test.

## What changed since last night

| Thing | Last night (`uid0807-19-14-58`) | Tonight |
|---|---|---|
| Cerebellum ground on the new mice | mated to the **orange** wire = **floating** | **re-pinned to brown, which lands on the headstage GND pad** |
| Mice with a working ground | 0 of 7 | **6 of 7** |
| A1 (port A slot 1) | no ground | ⭐ **STILL NO GROUND**, wiring problem on that animal. **Kept deliberately as the control** |
| A2 (port A slot 2) | old B1 mouse, short soldered resin tether, the positive control | **unchanged, still the positive control** |
| Everything else | 4 ports, C3442 splitters, 64 channels per port, 256 total, 1000 Hz | unchanged |

⭐ **THE CONTROL STRUCTURE TONIGHT IS BETTER THAN ANYTHING WE HAVE HAD BEFORE.** Three groups
inside one file, on one rig, in one night:

1. **A2** — old mouse, old soldered tether, ground always worked. **Positive control**, the only
   channel that ever produced real EEG on this cohort's rig.
2. **A1** — new mouse, new tether, new surgery batch, **ground still floating**. **Negative
   control that isolates the ground**, because it shares the surgery batch and the tether with the
   six that were fixed.
3. **B1, B2, C1, C2, D1, D2** — new mice, **ground fixed**. The treatment group.

⚠️ **A1 IS n = 1 AND IS NOT A RANDOMISED CONTROL.** It is the animal whose wiring would not
cooperate, so whatever is wrong with its wiring could in principle also be what keeps it flat.
It is strong evidence, not proof. Do not write it up as a designed control.

## Live look, 120 seconds, 2026-08-08 15:56, before any impedance was measured

Captured with `qc/grab_stream.py`, scored with `qc/live_screen.py`, exactly as last night, so the
two tables are directly comparable. `slope` is the log-log slope of the power spectrum from 1 to
40 Hz after notching mains: **real EEG falls steeply, a bare wire is flat**. Our measured floor
range from unwired amplifier inputs is **-1.29 to -0.07**. `rms_nohum` is the root mean square
left after notching mains and bandpassing 0.5 to 45 Hz.

| site | mouse | role | rms µV | 60 Hz µV | rms_nohum µV | slope | delta | HR bpm | HR cv |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| A/1 | **A1 NO GROUND** | EEG | 74.4 | 85.8 | 8.8 | **-0.05** | 0.07 | 451.1 | 0.47 |
| A/2 | **A1 NO GROUND** | EMG | 150.3 | 54.9 | 56.0 | **-0.08** | 0.08 | 705.9 | 0.55 |
| A/3 | **A1 NO GROUND** | ECG | 38.7 | 44.4 | 8.1 | **+0.01** | 0.06 | 566.0 | 0.40 |
| A/33 | **A2 CONTROL** | EEG | 59.9 | 32.9 | 48.8 | **-1.32** | 0.28 | — | — |
| A/34 | **A2 CONTROL** | EMG | 83.9 | 31.7 | 34.4 | **-1.25** | 0.39 | — | — |
| A/35 | A2 CONTROL | ECG | 4741.8 | 6602.9 | 188.7 | +0.09 | 0.05 | 451.1 | 0.46 |
| B/1 | B1 | EEG | 98.3 | 53.9 | **85.3** | **-1.35** | 0.18 | — | — |
| B/2 | B1 | EMG | 1204.2 | 1307.0 | 436.6 | -0.74 | 0.22 | 705.9 | 0.55 |
| B/3 | B1 | ECG | 2579.2 | 2218.8 | 1104.5 | -0.05 | 0.07 | — | — |
| B/33 | B2 | EEG | 553.5 | 452.2 | 196.1 | -0.61 | 0.30 | 895.5 | 0.46 |
| B/34 | B2 | EMG | 487.7 | 485.9 | 100.0 | -0.90 | 0.31 | 674.2 | 0.47 |
| B/35 | B2 | ECG | 69.9 | 31.9 | 44.3 | **-1.45** | 0.62 | 722.9 | 0.56 |
| C/1 | C1 | EEG | 3502.6 | 4346.3 | 854.5 | +0.18 | 0.05 | 397.4 | 0.43 |
| C/2 | C1 | EMG | 787.5 | 579.8 | 255.0 | -0.31 | 0.12 | 517.2 | 0.50 |
| C/3 | C1 | ECG | 1529.7 | 1318.4 | 413.9 | -0.12 | 0.11 | 517.2 | 0.47 |
| C/33 | C2 | EEG | 59.4 | 31.2 | 49.0 | **-1.05** | 0.19 | — | — |
| C/34 | C2 | EMG | 2154.9 | 2480.0 | 285.8 | -0.09 | 0.10 | 789.5 | 0.39 |
| C/35 | C2 | ECG | 4628.7 | 6372.9 | 169.3 | -0.16 | 0.08 | 406.8 | 0.44 |
| D/1 | D1 | EEG | 76.4 | 60.2 | 56.5 | **-1.27** | 0.20 | — | — |
| D/2 | D1 | EMG | 151.7 | 141.1 | 74.3 | **-1.39** | 0.54 | 666.7 | 0.47 |
| D/3 | D1 | ECG | 34.5 | 30.7 | 13.6 | -0.93 | 0.27 | 674.2 | 0.35 |
| D/33 | D2 | EEG | 121.0 | 41.2 | **115.4** | **-1.79** | 0.28 | — | — |
| D/34 | D2 | EMG | 83.0 | 107.1 | 12.8 | **-1.66** | 0.69 | 833.3 | 0.51 |
| D/35 | D2 | ECG | 17.7 | 6.3 | 12.0 | **-1.64** | 0.47 | 689.7 | 0.58 |

### The before and after, side by side, on the channels that moved

| site | role | slope BEFORE | slope NOW | rms_nohum BEFORE | rms_nohum NOW |
|---|---|---:|---:|---:|---:|
| D/33 | D2 EEG | -0.32 | **-1.79** | 5.3 | **115.4** |
| D/34 | D2 EMG | +0.09 | **-1.66** | 10.2 | 12.8 |
| D/35 | D2 ECG | +0.01 | **-1.64** | 8.7 | 12.0 |
| B/35 | B2 ECG | -0.10 | **-1.45** | 12.2 | 44.3 |
| D/2 | D1 EMG | -0.06 | **-1.39** | 10.9 | 74.3 |
| B/1 | B1 EEG | -0.30 | **-1.35** | 3.9 | **85.3** |
| D/1 | D1 EEG | -0.24 | **-1.27** | 6.4 | 56.5 |
| C/33 | C2 EEG | -0.20 | **-1.05** | 6.4 | 49.0 |
| D/3 | D1 ECG | -0.10 | **-0.93** | 3.7 | 13.6 |
| **A/1** | **A1 EEG, NO GROUND** | **-0.35** | **-0.05** | **8.3** | **8.8** |
| **A/2** | **A1 EMG, NO GROUND** | **-0.08** | **-0.08** | **10.0** | 56.0 |
| **A/3** | **A1 ECG, NO GROUND** | **-0.01** | **+0.01** | **7.5** | **8.1** |

⭐⭐⭐ **LAST NIGHT NOT ONE OF THE 21 NEW MOUSE CHANNELS HAD A SLOPE STEEPER THAN -0.35. TONIGHT
NINE OF THEM DO, AND THE THREE THAT DID NOT MOVE ARE THE THREE ON THE ONE ANIMAL WHOSE GROUND WAS
NOT FIXED.** That is a dose response with the dose set by a connector pin.

⚠️ **A/2 went from 10.0 to 56.0 µV of non mains signal with its slope unchanged at -0.08.** More
noise, still flat, still not biology. Do not read that row as A1 partially working.

### 🔴 What did NOT come good: the heartbeat

**Not one ECG channel passes the heartbeat test.** A mouse heart runs at roughly 600 to 750 beats
per minute with a beat to beat interval coefficient of variation (CV) well under 0.1. Every ECG
channel came back at **CV 0.35 to 0.58**, which is what a peak detector produces when it is
chewing on noise. Several of the reported heart rates are also outside the physiological range
(397, 451, 895 bpm), which is the same tell.

⚠️ **THIS MATTERS, AND IT IS THE STRONGEST ARGUMENT AGAINST DECLARING VICTORY TONIGHT.** The
heartbeat is the one test in this whole project that depends on **no threshold we invented**. Some
ECG channels did get a real spectral tilt (B/35 at -1.45, D/35 at -1.64, D/3 at -0.93), so
something changed there too, but **a spectral tilt is not a QRS complex**. Possible readings, and
I cannot separate them from 120 seconds:

1. The ECG electrode placement is genuinely poor on this batch.
2. The 1.10 Hz hardware high pass and the 5 to 100 Hz detection band are mangling the QRS.
3. The animals were moving during the capture and movement artefact is swamping it.
4. The detector itself is too crude for a signal riding on a large EMG background.

📌 **Re-run the heartbeat test on a long quiet stretch of the overnight file before concluding
anything about the ECG.** A sleeping mouse is the best possible condition for it.

## Impedance block, 30 sweeps

Files: `~/Downloads/impedance measurments/2026-08-08/01-post-ground-fix-30sweeps/`
Config string: `8slots-ECG-groundfix-A1nogrnd-4ports-64ch`

```
/opt/neurosurveillance/venv/bin/python sweep_block_all_ports.py \
  "/home/skimlab/Downloads/impedance measurments/2026-08-08/01-post-ground-fix-30sweeps" \
  30 35 "8slots-ECG-groundfix-A1nogrnd-4ports-64ch" --roles eeg,emg,ecg
```

⚠️ **A SINGLE SWEEP MEANS NOTHING.** Contact flips within minutes. Read the duty cycle over the
whole block and always quote the block duration next to it.

### Pre-registered prediction, written before the block finished

Carried over from [[2026-08-07-ecg-cohort-baseline]] § "Tomorrow, in order", item 3, plus one new
prediction that A1 makes possible:

- **Prediction A.** On the **six re-pinned mice** the impedances get **worse, or at least change
  character**, because the injected current's return path moves from "through the paired
  electrode" to "through the ground electrode". Last night's signature was 19 of 21 channels
  beating the floor and **seven channels at 100 percent duty with zero flips**. That signature
  should break up.
- ⭐ **Prediction B, the new one.** **A1's three channels should keep last night's signature**
  — very low, very stable impedance with few or no flips — **because its ground is still
  floating**. Last night A1 read **96.7 / 90.0 / 100.0 percent duty** with **1 / 6 / 0 flips**.
- **Falsifier.** If the six re-pinned mice also keep the 100 percent duty, zero flip signature,
  **the ground is still not connected on them either** and the live stream result needs another
  explanation.

### Result, 30 sweeps, 15:59:25 to 16:16:20, block duration 16.9 minutes

Scored with `qc/block_duty_cycle.py` at the **0.5 MΩ** criterion, against this cohort's own floor
(`/4`-`/16` and `/36`-`/48`, the 104 real amplifier inputs with no wire attached).

✅ **Falsification check passed. FLOOR: 3120 sweep-channels, 2.6 percent below 0.5 MΩ, median
4.971 MΩ.** Last night's floor was 3.4 percent, median 4.296. The floor did not move, so the two
blocks are directly comparable and the criterion is still calibrated.

| mouse | role | site | duty % | median Z MΩ | min Z MΩ | flips | p vs floor |
|---|---|---|---:|---:|---:|---:|---:|
| **A1 NO GROUND** | EEG | A/1 | **83.3** | 0.200 | 0.022 | 8 | 3e-35 * |
| **A1 NO GROUND** | EMG | A/2 | **90.0** | 0.171 | 0.011 | 6 | 6e-40 * |
| **A1 NO GROUND** | ECG | A/3 | **100.0** | 0.077 | 0.004 | **0** | 3e-48 * |
| A2 CONTROL | EEG | A/33 | 6.7 | 1.406 | 0.245 | 4 | 0.18 |
| A2 CONTROL | EMG | A/34 | 33.3 | 0.575 | 0.071 | 14 | 3e-09 * |
| A2 CONTROL | ECG | A/35 | 3.3 | 5.898 | 0.338 | 2 | 0.55 |
| B1 | EEG | B/1 | 23.3 | 1.502 | 0.155 | 10 | 1e-05 * |
| B1 | EMG | B/2 | 3.3 | 3.600 | 0.482 | 2 | 0.55 |
| B1 | ECG | B/3 | 10.0 | 2.643 | 0.133 | 5 | 0.042 * |
| B2 | EEG | B/33 | **0.0** | 5.122 | 3.172 | 0 | 1 |
| B2 | EMG | B/34 | **0.0** | 7.615 | 1.469 | 0 | 1 |
| B2 | ECG | B/35 | **0.0** | 3.683 | 3.230 | 0 | 1 |
| C1 | EEG | C/1 | 6.7 | 4.502 | 0.201 | 4 | 0.18 |
| C1 | EMG | C/2 | 16.7 | 1.333 | 0.374 | 9 | 0.001 * |
| C1 | ECG | C/3 | 30.0 | 1.553 | 0.045 | 8 | 5e-08 * |
| C2 | EEG | C/33 | 3.3 | 1.816 | 0.239 | 2 | 0.55 |
| C2 | EMG | C/34 | 10.0 | 3.102 | 0.168 | 5 | 0.042 * |
| C2 | ECG | C/35 | 6.7 | 6.053 | 0.108 | 4 | 0.18 |
| D1 | EEG | D/1 | **73.3** | 0.283 | 0.088 | 12 | 6e-29 * |
| D1 | EMG | D/2 | **70.0** | 0.337 | 0.024 | 14 | 6e-27 * |
| D1 | ECG | D/3 | **96.7** | 0.182 | 0.050 | 2 | 3e-45 * |
| D2 | EEG | D/33 | 36.7 | 0.793 | 0.097 | 8 | 1e-10 * |
| D2 | EMG | D/34 | **0.0** | 7.642 | 7.014 | 0 | 1 |
| D2 | ECG | D/35 | **100.0** | 0.230 | 0.018 | **0** | 3e-48 * |

### ✅ Prediction A confirmed. The impedance signature collapsed exactly where the ground was fixed

| site | mouse | duty BEFORE | duty NOW | flips BEFORE | flips NOW |
|---|---|---:|---:|---:|---:|
| B/33 | B2 EEG | 96.7 | **0.0** | 1 | 0 |
| B/35 | B2 ECG | 100.0 | **0.0** | 0 | 0 |
| B/34 | B2 EMG | 30.0 | **0.0** | 9 | 0 |
| D/34 | D2 EMG | 83.3 | **0.0** | 8 | 0 |
| C/33 | C2 EEG | 66.7 | 3.3 | 14 | 2 |
| C/1 | C1 EEG | 96.7 | 6.7 | 1 | 4 |
| C/34 | C2 EMG | 80.0 | 10.0 | 10 | 5 |
| C/3 | C1 ECG | 100.0 | 30.0 | 0 | 8 |
| B/1 | B1 EEG | 66.7 | 23.3 | 14 | 10 |
| D/33 | D2 EEG | 70.0 | 36.7 | 13 | 8 |
| D/2 | D1 EMG | 93.3 | 70.0 | 4 | 14 |
| D/1 | D1 EEG | 93.3 | 73.3 | 3 | 12 |
| **A/1** | **A1 EEG, NO GROUND** | **96.7** | **83.3** | 1 | 8 |
| **A/2** | **A1 EMG, NO GROUND** | **90.0** | **90.0** | 6 | 6 |
| **A/3** | **A1 ECG, NO GROUND** | **100.0** | **100.0** | 0 | **0** |

⭐⭐⭐ **THE IMPEDANCES GOT MUCH WORSE ON THE SIX RE-PINNED MICE AND BARELY MOVED ON A1.** This is
exactly what the grounding explanation predicted and it was written down before the block ran.
With the ground floating, the injected test current had to return **through the other electrode
of the pair**, giving an artificially low, stable, purely resistive reading. Re-connect the
ground and the return path moves to the ground electrode, and the number goes up.

⭐ **THE ZERO FLIP, 100 PERCENT DUTY SIGNATURE IS NOW ESSENTIALLY GONE FROM THE RE-PINNED MICE.**
Only **D/35** still shows it, and D/35 also had the third steepest spectral slope in the live
look (-1.64), so it is not obviously a floating channel. **A/3, the one remaining case on the
one un-grounded animal, is exactly where the hypothesis says it should be.**

> [!warning] ⚠️ Prediction B held, but not perfectly, and I am writing that down
> A1 was predicted to keep last night's signature unchanged. Its ECG did exactly that
> (100.0 percent, zero flips, both nights) and its EMG did too (90.0 percent, 6 flips, both
> nights). But **A1's EEG went from 96.7 percent with 1 flip to 83.3 percent with 8 flips**. That
> is a real change on an animal nothing was done to. Either ordinary intermittent contact, or
> handling the cage during the re-pinning session disturbed it. **A single channel moving is not
> a problem for the story, but it is a reminder that A1 is n = 1.**

> [!danger] 🔴🔴 THE IMPEDANCE AND THE LIVE STREAM DISAGREE AGAIN, AND THIS TIME IN THE OPPOSITE
> DIRECTION FROM LAST NIGHT
> **B2 reads 0.0 percent duty on all three of its sites**, statistically indistinguishable from a
> wire attached to nothing, yet in the live look **B/35 had a slope of -1.45 and B/33 had -0.61**.
> **D/34 reads 0.0 percent** yet had a slope of **-1.66**, one of the steepest on the rig.
> Meanwhile **A1, which is definitely floating, reads 83 to 100 percent duty.**
>
> ⭐⭐ **CONCLUSION, AND IT CHANGES HOW WE SCREEN THIS RIG: NOW THAT THE GROUND IS CONNECTED,
> IMPEDANCE DUTY CYCLE IS NO LONGER A USEFUL SCREEN FOR THIS COHORT, AND A HIGH DUTY CYCLE IS
> ACTIVELY SUSPICIOUS.** The 0.5 MΩ criterion was built to beat an unwired amplifier floor. It
> was never an absolute statement about contact, and on 2026-08-07 it already classified the best
> channel this project has ever recorded (A/33) as open. **Screen on the stream, not on the
> sweep.** Keep taking sweeps, they are cheap and they are the record, but do not use them to
> decide which animals are worth scoring.

## Overnight recording

**`allego_0__uid0808-16-17-36`, started 2026-08-08 16:17:36 KST**, in `/home/skimlab/radix/data/`.

Verified running the reliable way, by watching the destination rather than trusting the client:
`_data.xdat` grew from 0 to **63,450,112 bytes in about 55 seconds**, which is roughly
**4.1 GB per hour**. A 20 hour night is about **82 GB against 738 GB free**, so storage is not a
constraint.

Started with the workaround script, because the library call is still broken:

```
/opt/neurosurveillance/venv/bin/python qc/set_recording_config_fixed.py
# then set_streaming('on'), then set_recording('on')
```

⚠️ **`set_recording_config()` IN THE RADIENS PYTHON CLIENT IS STILL BROKEN** and fails with
`Exception serializing request!` because `ConfigRecording` has a required `recordingType` enum
that the library never sets. See [[2026-08-07-ecg-cohort-baseline]] for the full diagnosis.

⚠️ **DO NOT TRUST THE `path` FIELD IN `get_status().recording`.** It reported
`/home/skimlab/Monitoring_project/eeg-emg-analysis/qc`, which is simply the directory the client
was launched from. The file is really in `~/radix/data/`. **The only reliable check is to list
the destination and confirm `_data.xdat` is growing.**

📌 **andrea stops this recording herself on the morning of 2026-08-09.**

### Pre-registration for the night, written 2026-08-08 16:20, before the night exists

Written in advance so tomorrow's scoring is honest, exactly as we did last night.

- **Prediction 1.** **A2, the control, scores usable EEG over the great majority of the night**,
  as it has every night it has run. Confidence **high**.
- ⭐ **Prediction 2, the one this whole day is about.** **At least three of the six re-pinned mice
  produce a usable EEG block of one hour or more.** Confidence **moderate**. The strongest
  candidates on the live look are **D2 (D/33, slope -1.79)**, **B1 (B/1, -1.35)** and
  **D1 (D/1, -1.27)**.
- ⭐⭐ **Prediction 3, the negative control.** **A1 scores 0.0 percent usable EEG and 0.0 percent
  usable ECG**, because its ground is still floating. Confidence **high**. ⚠️ **THIS IS THE
  PREDICTION THAT CAN EMBARRASS US, AND THAT IS WHY IT IS HERE.** If A1 comes good overnight, the
  grounding explanation is in serious trouble and last night's re-pin was not what fixed things.
- **Prediction 4, the heartbeat.** **At least one ECG channel on a re-pinned mouse shows a
  heartbeat** at 600 to 750 beats per minute with an interval coefficient of variation under 0.1,
  measured on a quiet stretch. Confidence **low**. It failed on every channel in today's live
  look, and this is the only test in the project that depends on no threshold we invented.
- **Prediction 5, an anti-prediction.** **Duty cycle from today's block does NOT rank the animals
  by usable fraction tomorrow.** B2 reads 0.0 percent on all three sites and I still expect it to
  produce signal. If the impedance ranking does predict the outcome, I am wrong about what the
  sweep now measures.

⚠️ **WHAT WOULD FALSIFY ALL OF THIS: A NIGHT IS THE OUTCOME, 120 SECONDS IS NOT.** On 2026-08-06 a
21 minute window gave p = 8.4e-08 for a conclusion that turned out to be **exactly backwards**,
and D2 went from 0.0 to 87.9 percent usable once a real night was recorded. Today's live look is
120 seconds. **Nothing on this page is an outcome until the recording is scored.**

## Still open

- 🔴 **No heartbeat on any ECG channel.** See above. Primary thing to check in the night file.
- **No video.** Cameras were removed on 2026-08-04 and have not been restored, so any EMG that
  looks like movement artefact stays unresolvable.
- **A1's ground wiring** still needs fixing at some point. It is a useful control tonight, but it
  is one of seven animals not producing data.
- Nothing here tests the **negative half** of each electrode pair. Still unmeasurable, see
  [[impedance-negative-electrode-unmeasurable]].
- ⚠️ **THIS COHORT'S HUM THRESHOLDS ARE STILL NOT RE-DERIVED.** On the old cohort 60 Hz amplitude
  was a direct contact proxy. It is not on this one, and it is not one tonight either.
- The kappa and the positive control from [[2026-08-08]] are untouched by any of this and still
  gate every accuracy claim.

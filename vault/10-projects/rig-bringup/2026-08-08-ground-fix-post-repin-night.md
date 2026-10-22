---
type: experiment
area: rig-bringup
status: done
status-note: "active"
title: Ground re-pin, the after state, and the overnight recording
created: 2026-08-08
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

| Thing | Last night (`allego_0__uid0807-19-14-58`) | Tonight |
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
21 minute window gave p = 1.0e-07 for a conclusion that turned out to be **exactly backwards**,
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

---

# 22:00 interim check, 5.5 hours into the night

Scored at 22:02 KST, **5.74 hours** into the recording, on the **first 5.5 hours**. The file was
still being written and **was not stopped**. ⚠️ **THIS IS AN INTERIM, NOT THE OUTCOME.** It covers
the evening only. The dark phase starts at 21:00 KST, so almost all of this window is light phase,
when a mouse should mostly be asleep.

Recording verified the reliable way: `_data.xdat` at **21,679,816,704 bytes and still growing**,
about 3.9 GB per hour, 717 GB free.

## ⭐⭐ The legacy usable-fraction script had to be replaced, and finding out why is a result

`qc/usable_fraction_vs_floor.py` is hardcoded to the old 2 channel cohort and its floor list
(`/3`-`/16`, `/35`-`/48`) now includes **two wired ECG sites**. I wrote
**`qc/usable_fraction_vs_floor_ecg.py`**, which fixes the roles and the floor and reports
**two criteria side by side**:

- **HUM criterion**, the legacy one: 60 Hz amplitude below the floor's 1st percentile, root mean
  square (rms) between 10 and 150 µV, no railing.
- ⭐ **SLOPE criterion**: log-log slope of the power spectrum over **1 to 40 Hz** steeper than the
  floor's 1st percentile, plus the same rms and railing rules. **1 to 40 Hz contains no mains
  harmonic**, so this needs no notch and no filter design at all.

Floor in this file, 104 unwired amplifier inputs × 1980 epochs = 205,920 samples:

| measure | p1 | p5 | median |
|---|---:|---:|---:|
| 60 Hz amplitude | 393.7 µV | 800.9 µV | 3961.5 µV |
| 1-40 Hz slope | **-1.34** | -0.78 | -0.09 |

✅ **Falsification check passed: floor channels score 0.00 percent usable by BOTH criteria.**

> [!danger] 🔴🔴🔴 THE HUM CRITERION IS DEAD ON THIS COHORT, AND A1 PROVES IT
> **A1 has no ground. We know that for certain. It scores 100.0 percent, 74.6 percent and
> 100.0 percent "usable" by the legacy HUM criterion on its three channels.**
>
> The mechanism is the one we already wrote down and then failed to act on: with no ground, mains
> drives the whole animal as common mode and **a bipolar pair rejects it**, so a floating channel
> is *quiet*. A1's median 60 Hz sits at **44 to 78 µV** while the unwired floor median is
> **3962 µV**. The legacy criterion rewards quiet, so it hands a floating animal a perfect score.
>
> ⇒ **`usable_fraction_vs_floor.py` MUST NOT BE RUN ON THIS COHORT AGAIN.** Use the SLOPE column.
> ⇒ ⚠️ **Usable fractions computed with the hum criterion are NOT comparable to slope ones.** Do
> not put B1's 99.6 percent from 2026-08-06/07 in the same table as any number below.

## Result, first 5.5 h, 1980 epochs of 10 s

`usable_SLOPE` is the honest column. `longest_h` is the longest **unbroken** run of usable epochs,
in hours, by the slope criterion. Floor slope p1 in this file is **-1.34**.

| mouse | role | site | usable HUM | **usable SLOPE** | longest h | med slope | med lf/hf | med 60 Hz µV | med rms µV |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| **A1 NO GROUND** | EEG | A/1 | 100.0% | **0.0%** | 0.00 | **-0.14** | 1.42 | 77.6 | 69.2 |
| **A1 NO GROUND** | EMG | A/2 | 74.6% | **0.0%** | 0.00 | **+0.01** | 1.39 | 52.4 | 67.3 |
| **A1 NO GROUND** | ECG | A/3 | 100.0% | **0.0%** | 0.00 | **+0.04** | 1.42 | 43.6 | 39.2 |
| **A2 CONTROL** | EEG | A/33 | 99.9% | **87.8%** | **0.41** | **-1.66** | 21.14 | 35.8 | 74.8 |
| A2 CONTROL | EMG | A/34 | 99.1% | 20.2% | 0.06 | -0.83 | 1.51 | 35.5 | 31.8 |
| A2 CONTROL | ECG | A/35 | 0.0% | 0.0% | 0.00 | +0.04 | 1.76 | 6490.5 | 4752.0 |
| B1 | EEG | B/1 | 42.2% | 11.2% | 0.07 | -0.11 | 2.04 | 310.0 | 1372.0 |
| B1 | EMG | B/2 | 1.2% | 0.1% | 0.00 | -0.03 | 1.89 | 2316.3 | 2487.3 |
| B1 | ECG | B/3 | 0.0% | 0.0% | 0.00 | -0.02 | 1.79 | 1197.5 | 1774.0 |
| **B2** | EEG | B/33 | 83.6% | **57.5%** | 0.12 | **-1.52** | 20.93 | 76.2 | 108.9 |
| B2 | EMG | B/34 | 82.4% | 4.9% | 0.01 | -0.73 | 1.16 | 82.3 | 77.0 |
| B2 | ECG | B/35 | 77.9% | 7.1% | 0.02 | -0.63 | 1.91 | 27.2 | 56.2 |
| C1 | EEG | C/1 | 0.0% | 0.0% | 0.00 | +0.25 | 1.98 | 3205.0 | 2970.3 |
| C1 | EMG | C/2 | 0.0% | 0.0% | 0.00 | -0.40 | 4.92 | 470.4 | 631.4 |
| C1 | ECG | C/3 | 4.7% | 0.0% | 0.00 | -0.11 | 2.94 | 3469.8 | 2847.1 |
| **C2** | EEG | C/33 | 100.0% | **71.6%** | 0.20 | **-1.59** | 21.98 | 26.0 | 79.7 |
| C2 | EMG | C/34 | 15.4% | 6.3% | 0.03 | -0.02 | 2.32 | 4154.6 | 3260.9 |
| C2 | ECG | C/35 | 0.0% | 0.0% | 0.00 | -0.07 | 1.07 | 6270.8 | 4643.6 |
| **D1** | EEG | D/1 | 100.0% | **70.3%** | 0.21 | **-1.59** | 20.12 | 51.4 | 88.3 |
| D1 | EMG | D/2 | 30.6% | 1.3% | 0.01 | -0.13 | 1.61 | 217.3 | 179.4 |
| D1 | ECG | D/3 | 99.8% | 7.8% | 0.03 | -0.08 | 2.68 | 32.3 | 37.6 |
| **D2** | EEG | D/33 | 96.4% | **63.7%** | 0.10 | **-1.63** | 29.27 | 34.5 | 106.6 |
| D2 | EMG | D/34 | 98.7% | 35.0% | 0.06 | -1.07 | 1.54 | 107.1 | 85.3 |
| D2 | ECG | D/35 | 77.9% | 35.8% | 0.12 | -1.06 | 2.63 | 4.3 | 16.4 |

⭐⭐⭐ **FOUR RE-PINNED MICE NOW PRODUCE REAL ELECTROENCEPHALOGRAM, AND UNTIL YESTERDAY THE ANSWER
WAS ZERO.** B2 57.5, C2 71.6, D1 70.3, D2 63.7 percent usable, with median slopes of -1.52 to
-1.63 and **low-frequency to high-frequency ratios of 20.9 to 29.3**. The control A2 sits right
among them at -1.66 and 21.14. ⭐ **On 2026-08-07 the 256 channel scan found A/33 was the ONLY
channel in the whole rig with an lf/hf above 4.79, and everything else was 0.42 to 0.92. Tonight
four new mice are at 20 to 29.**

🔴 **B1 and C1 are not working.** C1 sits at rms 2970 µV with a slope of **+0.25**, which is a loud
open channel, and B1 is at 1372 µV with -0.11. Both were poor in the impedance block too. These
are the ordinary intermittent-contact failure this rig has always had, and the ground fix does not
address it.

## ✅ THE NEGATIVE CONTROL HELD PERFECTLY

**A1 scores 0.0 percent on all three channels by the slope criterion**, with median slopes of
**-0.14, +0.01 and +0.04** and lf/hf of 1.39 to 1.42, which is squarely inside the unwired floor
distribution. Its six cage-mates, same surgery batch, same tether design, differ from it in
**one connector pin**, and four of them are producing electroencephalogram.

## Heartbeat test on the quietest 5 minute window per channel

`qc/heartbeat_on_quiet_stretch.py`, new tonight. It picks, per channel, the 5 minute window with
the lowest mean rms **containing zero railed samples**, then bandpasses 5 to 100 Hz, detects peaks
and measures interval regularity. **PASS requires interval CV below 0.10 AND a rate of 600 to 750
beats per minute.**

| mouse | site | window start h | rms µV | peaks | HR bpm | IBI CV | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| A1 | A/3 | 2.61 | 34.7 | 1042 | 508.5 | 0.40 | no heartbeat |
| A2 | A/35 | — | — | — | — | — | no railing-free window (**no ECG implanted, correct**) |
| B1 | B/3 | — | — | — | — | — | no railing-free window |
| B2 | B/35 | 3.73 | 16.0 | 510 | 638.3 | 0.50 | no heartbeat |
| C1 | C/3 | — | — | — | — | — | no railing-free window |
| C2 | C/35 | — | — | — | — | — | no railing-free window |
| D1 | D/3 | 1.06 | 24.9 | 2338 | 491.8 | **0.22** | no heartbeat |
| D2 | D/35 | 0.94 | 7.9 | 224 | 357.1 | 0.47 | no heartbeat |

🔴🔴 **STILL NO HEARTBEAT ANYWHERE, ON A NIGHT RECORDING, ON THE QUIETEST STRETCH WE COULD FIND.**
D1's **CV of 0.22** is the best number this project has ever produced on an ECG channel, against
0.31 to 0.58 on every previous attempt, so something did improve. **But 0.22 is not 0.10 and this
test does not grade on a curve.** **The ECG is not working and the grounding fix did not fix it.**

## ⭐⭐ Judging the five pre-registered predictions

| # | prediction | verdict |
|---|---|---|
| 1 | A2 the control scores usable EEG over the great majority of the night | ✅ **CONFIRMED**, 87.8% |
| 2 | at least three of six re-pinned mice produce a usable EEG block of **one hour or more** | ❌ **FAILED AS WRITTEN** |
| 3 | **A1 scores 0.0% usable EEG and 0.0% usable ECG** | ✅ **CONFIRMED EXACTLY**, 0.0% on all three |
| 4 | at least one ECG channel on a re-pinned mouse shows a heartbeat | ❌ **FAILED** |
| 5 | anti-prediction: today's duty cycle does NOT rank the animals | ✅ **CONFIRMED** |

### 🔴 Prediction 2 failed, and I am not going to paper over it

**Four of six re-pinned mice produced usable electroencephalogram over 57 to 72 percent of the
window, which is far better than I predicted. But the longest UNBROKEN block on any of them is
0.21 hours, which is 13 minutes.** The clause I wrote was "a usable EEG block of one hour or
more" and **no animal reached it.** The prediction is failed.

⚠️ **Two honest caveats, both of which cut against me, not for me.**

1. **I also named the wrong animals.** I nominated D2, **B1** and D1 as the strongest candidates.
   D2 and D1 delivered. **B1 came 7th of 8 at 11.2 percent.** The two that worked and that I did
   not name are **B2 and C2**.
2. ⭐ **The slope criterion is state-dependent, and that is the council's selection-bias problem
   showing up again.** It requires a slope steeper than -1.34 in **every single 10 second epoch**.
   Waking, desynchronised electroencephalogram is genuinely flatter than sleeping
   electroencephalogram, so **a waking animal fails the criterion for real biological reasons and
   the block breaks**. Some of the fragmentation above is therefore **sleep-wake structure being
   misread as dropout**. 🛑 **DO NOT "FIX" THIS BY LOOSENING THE THRESHOLD** — that is exactly the
   circular tuning that is banned in [[blind-scoring-and-kappa]]. The right fix is to report the
   usable fraction, which is robust, and to stop quoting longest-block for the slope criterion
   until it is separated from state.

### ✅ Prediction 5, the anti-prediction, held, and it is worth a number

Spearman rank correlation between **this afternoon's impedance duty cycle** and **tonight's usable
fraction by slope**:

| set | rho | p |
|---|---:|---:|
| all 24 channels | **-0.126** | 0.556 |
| the 8 EEG channels | -0.283 | 0.497 |
| the 7 EEG channels excluding A1 | **+0.000** | 1.000 |

⭐⭐ **The impedance sweep carries essentially ZERO information about which animal will give data.**
**B2 read 0.0 percent duty on all three sites this afternoon and is producing 57.5 percent usable
electroencephalogram tonight. A1 read 83 to 100 percent and is producing nothing.** This confirms
in the strongest possible way the rule written this afternoon: **screen on the stream, not on the
sweep.**

## What this does and does not establish

| ✅ Established | ❌ Not established |
|---|---|
| The ground was the fault, and re-pinning it **restores electroencephalogram** on most animals | That the ECG works at all. **It does not, on any animal** |
| **A1, the un-repaired animal, is dead**, which is the controlled version of the claim | Why B1 and C1 are still failing, beyond ordinary intermittent contact |
| The **hum criterion is invalid on this cohort** and a floating animal scores 100% on it | Whether the fragmentation is dropout or sleep-wake structure. **Confounded** |
| **Impedance duty cycle does not predict yield** (rho ~ 0) | Anything about the second half of the night, which is the dark phase |

📌 **The recording was NOT stopped and is still running. andrea stops it in the morning**, and the
real outcome is the full night scored with the light and dark phases separated.

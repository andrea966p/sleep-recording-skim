---
title: ECG cohort baseline, 7 new mice plus the B1 control
date: 2026-08-07
status: active
tags: [eeg, emg, ecg, impedance, tether, cohort]
---

# ECG cohort, first baseline

> [!danger] READ THIS FIRST, the answer is at the bottom of the page
> This note is written **in the order the evening actually happened**, so the early sections
> record hypotheses that were later **withdrawn**. The conclusion is
> [§ THE GROUND WIRE WAS CONNECTED TO THE WRONG PIN](#-the-ground-wire-was-connected-to-the-wrong-pin).
>
> **All seven new mice were recording with no ground connection to the animal.** The cerebellum
> dura pin was mated to the **orange** wire, which floats, while the **brown** wire sitting in
> the headstage GND pad touches nothing on the mouse.
>
> 🔴 **Withdrawn below, do not act on them:** the tether short hypothesis, the fluid bridge under
> the cement, and the suggestion to spend an isoflurane episode moving one mouse to an old style
> tether. ✅ **The fix is a connector re-mate and needs no anaesthesia.**

## TL;DR, where we are right now

We pulled every mouse off the rig and put on **7 brand new mice**, each implanted with
**three bipolar channels: electroencephalogram (EEG), electromyogram (EMG) and
electrocardiogram (ECG)**. The old **B1 mouse stays as a control** in port A slot 2, still on
its short soldered and resin encapsulated tether, because it gave the cleanest recording this
project has ever produced (99.6 percent usable over 23.66 hours on 2026-08-06/07).

I looked at 120 seconds of the live stream before doing anything else. Two things came out of it:

1. ⭐ **The 60 Hz mains hum collapsed across the whole fleet.** On the old cohort the open
   channels sat at 800 to 5500 microvolts (µV). Now only 4 channels of 24 are high, and the
   rest sit between 20 and 210 µV. That is a genuine, new, fleet wide change.
2. 🔴 **The biology did not come with it.** After notching the mains and bandpassing 0.5 to
   45 Hz, 22 of the 24 channels sit at 2 to 6 µV median amplitude, which is the amplifier's own
   input noise, not tissue. **The only channel with real signal is the control, A/33.**

⚠️ **THIS IS A SCREEN, NOT AN OUTCOME.** It is 120 seconds, taken right after the animals were
connected, and we already know from 2026-08-07 that contact flips on a minutes timescale and
that **only a multi hour recording is an outcome**. Do not write the new cohort off from this.

⭐⭐ **NEW WARNING FOR THIS COHORT: LOW HUM IS NO LONGER A CONTACT PROXY.** On the old cohort
the 60 Hz amplitude was cleanly bimodal and told you directly whether an electrode was making
contact. On this cohort you can have 20 µV of hum and 3 µV of nothing underneath it.
**Every hum threshold we have must be re-derived from this cohort's own floor channels.**

## What changed, hardware

| Thing | Old cohort | This cohort |
|-------|-----------|-------------|
| Channels per mouse | 2, EEG + EMG | **3, EEG + EMG + ECG** |
| Channel map, slot 1 | `/1` EEG, `/2` EMG | **`/1` EEG, `/2` EMG, `/3` ECG** |
| Channel map, slot 2 | `/33` EEG, `/34` EMG | **`/33` EEG, `/34` EMG, `/35` ECG** |
| Tether | 22 cm, 6 conductor, various | **22 cm, 8 conductor, thicker, wires NOT soldered, thin heatshrink** |
| Ground / reference tissue wire | right parietal | **cerebellum** |
| Sample rate | 1000 Hz | 1000 Hz, unchanged |
| Port A slot 2 | no mouse, cut tether control | **the old B1 mouse, kept as a positive control** |

Ports and channel count are unchanged: 4 ports, C3442 splitters, 64 channels per port,
**256 total**. `remap_channels.py` re-run on 2026-08-07 and the map is **unchanged**,
native index `ntv i` maps to `SITES[i]` with A = 0 to 63, B = 64 to 127, C = 128 to 191,
D = 192 to 255.

🔴 **WE NO LONGER HAVE THE EMPTY A2 CUT TETHER CONTROL.** All 8 slots are occupied now. The
free floor control still exists but **its channel list has changed**, because `/3` and `/35`
are now real wired channels:

- **OLD floor control:** `/3` to `/16` and `/35` to `/48`
- ⭐ **NEW floor control for this cohort: `/4` to `/16` and `/36` to `/48`**, which is
  13 + 13 = 26 unwired amplifier inputs per port, **104 floor channels** recorded simultaneously.
- ⚠️ **STILL NEVER USE `/17` to `/32` OR `/49` to `/64`.** Those are inactive slots, internally
  tied, and they would destroy the control.

## Live stream screen, 120 seconds, 2026-08-07 evening

Captured through the Radiens Python client while Allego was streaming, 24 selected channels
(exactly the 8 slots times 3 roles), 1000 Hz. Scripts now live in `eeg-emg-analysis/qc/`:
**`grab_stream.py`** (captures N seconds of the live stream to `.npy` plus a labels file) and
**`live_screen.py`** (the table below, including the heartbeat test).

Columns: `rms` is raw root mean square. `60Hz` is the mains amplitude. `rms_nohum` is the RMS
left after notching 60/120/180/240/300 Hz and bandpassing 0.5 to 45 Hz, so it is roughly
"how much non mains signal is there". `slope` is the log-log slope of the power spectrum from
1 to 40 Hz, real EEG falls steeply, a bare wire is flat. `delta` is the fraction of 1 to 40 Hz
power sitting in 1 to 4 Hz.

| site | mouse | role | rms µV | 60 Hz µV | rms_nohum µV | slope | delta |
|------|-------|------|-------:|---------:|-------------:|------:|------:|
| A/1  | A m1 | EEG |   43.6 |   49.6 |   8.3 | -0.35 | 0.07 |
| A/2  | A m1 | EMG |   98.6 |  108.6 |  10.0 | -0.08 | 0.08 |
| A/3  | A m1 | ECG |   47.3 |   44.8 |   7.5 | -0.01 | 0.07 |
| **A/33** | **A m2 CONTROL** | **EEG** | **90.5** | **33.4** | **85.2** | **-1.93** | **0.46** |
| A/34 | A m2 CONTROL | EMG |   28.6 |   34.4 |   7.4 | -0.86 | 0.50 |
| A/35 | A m2 CONTROL | ECG | 4737.2 | 6593.7 | 181.7 | -0.02 | 0.07 |
| B/1  | B m1 | EEG |   48.6 |   48.5 |   3.9 | -0.30 | 0.10 |
| B/2  | B m1 | EMG |  631.2 |  554.1 | 110.2 | -0.27 | 0.13 |
| B/3  | B m1 | ECG | 1172.4 | 1013.2 | 389.6 | -0.03 | 0.07 |
| B/33 | B m2 | EEG |   52.9 |   59.8 |   5.8 | -0.19 | 0.06 |
| B/34 | B m2 | EMG |  206.4 |  204.8 |  15.9 | -0.05 | 0.06 |
| B/35 | B m2 | ECG |  185.5 |  210.2 |  12.2 | -0.10 | 0.08 |
| C/1  | C m1 | EEG |   29.9 |   29.7 |   5.1 | -0.28 | 0.08 |
| C/2  | C m1 | EMG |  460.8 |  178.9 |  41.2 | -0.17 | 0.15 |
| C/3  | C m1 | ECG |   29.5 |   33.6 |   6.2 | -0.10 | 0.07 |
| C/33 | C m2 | EEG |   77.4 |   81.2 |   6.4 | -0.20 | 0.07 |
| C/34 | C m2 | EMG |   38.5 |   21.0 |  11.4 | -0.01 | 0.08 |
| C/35 | C m2 | ECG | 1036.9 |  314.4 | 259.2 | -0.15 | 0.09 |
| D/1  | D m1 | EEG |   93.5 |  112.9 |   6.4 | -0.24 | 0.06 |
| D/2  | D m1 | EMG |  114.6 |  139.7 |  10.9 | -0.06 | 0.08 |
| D/3  | D m1 | ECG |   85.5 |  108.5 |   3.7 | -0.10 | 0.07 |
| D/33 | D m2 | EEG |   61.2 |   79.3 |   5.3 | -0.32 | 0.11 |
| D/34 | D m2 | EMG |   37.5 |   21.0 |  10.2 |  0.09 | 0.06 |
| D/35 | D m2 | ECG |   29.1 |   22.9 |   8.7 |  0.01 | 0.06 |

**Three independent checks all say the same thing.**

1. **Spectral shape.** Our floor range, measured from unwired amplifier inputs on previous
   runs, is a slope between -1.29 and -0.07. Everything in the table above is between -0.0 and
   -0.35, i.e. **inside the bare wire range**, except **A/33 at -1.93 with a delta fraction of
   0.46**, which is far outside it and is real EEG. A/34 at -0.86 is intermediate.
2. ⭐⭐ **A heartbeat test, which is brand new and only possible now that we have ECG.** A mouse
   heart runs at roughly 600 to 750 beats per minute and the beat to beat interval is very
   regular, coefficient of variation (CV) well under 0.1. I bandpassed 5 to 100 Hz, detected
   peaks, and measured the interval regularity on every channel. **Every single ECG channel
   came back with a CV between 0.31 and 0.46**, which is what you get when a peak detector is
   chewing on noise. **NOT ONE CHANNEL HAS A DETECTABLE HEARTBEAT.** This is a much harder,
   more falsifiable test than anything we had before, because a heartbeat is unmistakable and
   it does not depend on any threshold we invented.
3. **Cross correlation of the residuals.** If real biology were present, channels on the same
   animal, and especially EEG against EMG during movement, would share large transients. The
   maximum absolute correlation anywhere in the 24 by 24 matrix is 0.48 and almost everything
   is under 0.3. **No shared biological signal.**

⭐ **The control passing is the important part.** A/33 behaves exactly as it did in the 23.66
hour run, slope -1.93 now against -1.81 then, delta 0.46 against 0.32. So the amplifiers, the
splitters, the ports, the acquisition chain and my analysis are all fine. **Whatever is wrong
is on the animal side of the connector, not the rig side.**

⚠️ Four channels are loudly open in the classic way, high hum: **A/35 (6594 µV), B/3 (1013),
B/2 (554), C/35 (314)**. Note A/35 is the control mouse's ECG site, and **the control mouse has
no ECG implanted**, so A/35 being open is expected and correct. Treat A/35 as a second free
"nothing attached" control.

## Impedance block, 30 sweeps

Files: `~/Downloads/impedance measurments/2026-08-07/01-ecg-cohort-baseline-30sweeps/`
Config string: `8slots-ECG-Actrl-4ports-64ch`

Run with the canonical script, which I generalised today so it understands three channels per
mouse:

```
/opt/neurosurveillance/venv/bin/python sweep_block_all_ports.py \
  "/home/skimlab/Downloads/impedance measurments/2026-08-07/01-ecg-cohort-baseline-30sweeps" \
  30 35 "8slots-ECG-Actrl-4ports-64ch" --roles eeg,emg,ecg
```

Changes to `eeg-emg-analysis/qc/sweep_block_all_ports.py`:

- takes a `--roles` argument, so `eeg,emg` reproduces the old 2 channel cohort and
  `eeg,emg,ecg` covers this one
- the config string and the date are now arguments / derived from the clock instead of
  hardcoded to 2026-08-06
- ⭐ the live console summary now uses the **0.5 MΩ** criterion, not 2 MΩ. The 2 MΩ criterion
  was shown on 2026-08-06 to have a **22 percent false positive rate against an empty cable**
  and must not be used again.

⚠️ **A SINGLE SWEEP MEANS NOTHING.** Contact flips within minutes. Read the duty cycle over the
whole block, and always quote the block's duration next to it.

### Result, 30 sweeps, 18:55:55 to 19:13:19, block duration 17.4 minutes

Scored with the new `eeg-emg-analysis/qc/block_duty_cycle.py` against this cohort's own floor.

✅ **Falsification check passed. FLOOR: 3120 sweep-channels from the 104 unwired amplifier
inputs, 3.4 percent below 0.5 MΩ, median 4.296 MΩ.** That is the same 2 to 3 percent we got on
the old cohort, so the 0.5 MΩ criterion is still calibrated and the block is interpretable.

| mouse | role | site | duty % | median Z MΩ | min Z MΩ | flips | p vs floor |
|---|---|---|---:|---:|---:|---:|---:|
| A1 | EEG | A/1 | **96.7** | 0.122 | 0.009 | 1 | 7e-42 * |
| A1 | EMG | A/2 | **90.0** | 0.245 | 0.015 | 6 | 8e-37 * |
| A1 | ECG | A/3 | **100.0** | 0.084 | 0.008 | 0 | 9e-45 * |
| **A2 CONTROL** | EEG | A/33 | **0.0** | 1.639 | 0.666 | 0 | 1 |
| **A2 CONTROL** | EMG | A/34 | **0.0** | 0.650 | 0.515 | 0 | 1 |
| **A2 CONTROL** | ECG | A/35 | 0.0 | 5.011 | 0.565 | 0 | 1 |
| B1 | EEG | B/1 | 66.7 | 0.358 | 0.021 | 14 | 9e-23 * |
| B1 | EMG | B/2 | 10.0 | 2.640 | 0.088 | 5 | 0.081 |
| B1 | ECG | B/3 | 16.7 | 3.693 | 0.285 | 9 | 0.0032 * |
| B2 | EEG | B/33 | **96.7** | 0.209 | 0.018 | 1 | 7e-42 * |
| B2 | EMG | B/34 | 30.0 | 0.661 | 0.084 | 9 | 5e-07 * |
| B2 | ECG | B/35 | **100.0** | 0.159 | 0.016 | 0 | 9e-45 * |
| C1 | EEG | C/1 | **96.7** | 0.155 | 0.019 | 1 | 7e-42 * |
| C1 | EMG | C/2 | 50.0 | 0.458 | 0.022 | 12 | 9e-15 * |
| C1 | ECG | C/3 | **100.0** | 0.156 | 0.016 | 0 | 9e-45 * |
| C2 | EEG | C/33 | 66.7 | 0.365 | 0.056 | 14 | 9e-23 * |
| C2 | EMG | C/34 | 80.0 | 0.330 | 0.013 | 10 | 3e-30 * |
| C2 | ECG | C/35 | 10.0 | 2.135 | 0.112 | 4 | 0.081 |
| D1 | EEG | D/1 | **93.3** | 0.195 | 0.014 | 3 | 3e-39 * |
| D1 | EMG | D/2 | **93.3** | 0.183 | 0.024 | 4 | 3e-39 * |
| D1 | ECG | D/3 | **100.0** | 0.114 | 0.004 | 0 | 9e-45 * |
| D2 | EEG | D/33 | 70.0 | 0.291 | 0.026 | 13 | 2e-24 * |
| D2 | EMG | D/34 | 83.3 | 0.357 | 0.014 | 8 | 2e-32 * |
| D2 | ECG | D/35 | **100.0** | 0.185 | 0.011 | 0 | 9e-45 * |

⭐⭐⭐ **BY IMPEDANCE THIS IS THE BEST THE RIG HAS EVER LOOKED. 19 of the 21 new mouse channels
beat an unwired amplifier input, and seven of them sit at 100 percent duty with ZERO flips.**
For comparison, on 2026-08-06 only **4 of 14** channels beat the floor at all.

🔴🔴 **AND YET THE IMPEDANCE AND THE RECORDING POINT IN OPPOSITE DIRECTIONS.**

- Every channel that reads beautifully connected produced **flat amplifier noise with no
  heartbeat** in the live stream.
- The **control, A2, reads 0.0 percent duty on all three sites**, and it is the **only slot on
  the rig producing real electroencephalogram**.

The control part of that is explainable and is not a surprise: B1's EEG median was **0.813 MΩ**
back on 2026-08-06, which is already above the 0.5 MΩ line. ⚠️ **THE 0.5 MΩ CRITERION
CLASSIFIES THE BEST CHANNEL THIS PROJECT HAS EVER RECORDED AS OPEN.** It was only ever built
to beat an unwired floor, it is **not** an absolute statement about contact, and it must never
be quoted as one.

⭐⭐ **The new mice are the worrying half, and there is a hypothesis that explains all three
observations at once: THE BIPOLAR PAIRS MAY BE SHORTED SOMEWHERE IN THE UNSOLDERED 8 CONDUCTOR
TETHER.** A short would give you, simultaneously:

1. **Very low impedance**, because the measured site now has a metal path to a large electrode.
   Note several minimum readings of **0.004 to 0.020 MΩ, that is 4 to 20 kΩ**, at or below the
   published range for epidural electrodes, which is 10 to 50 kΩ. Real tissue interfaces should
   not go that low.
2. **Almost no 60 Hz hum**, because a short is a low impedance path and rejects common mode
   pickup very well. This is exactly the fleet wide hum collapse we measured.
3. **No differential signal at all**, because if the two members of a bipolar pair are tied
   together their difference is zero by construction.

⚠️ **THIS IS A HYPOTHESIS, NOT A RESULT.** The wires being crimped under thin heatshrink
instead of soldered is precisely the construction that produces conductor to conductor shorts,
and both tether chains that ever worked on this rig, arm B on B1 and arm C on D2, were
**soldered and resin encapsulated**. But 120 seconds of stream cannot settle it. **The
overnight recording is the test.** If it comes back flat with low hum across the whole new
cohort while A/33 stays clean, the short hypothesis becomes the leading explanation and the
next step is a bench continuity check of a spare 8 conductor tether, pin to pin, before
touching any animal.

⚠️ Note sweep 30 at 19:12:50: **six of the eight slots flipped their EEG site to open in the
same sweep**. Single sweep, could easily be coincidence or someone walking past the rack, but
worth remembering if it repeats.

⚠️ **NEVER SWEEP FROM THE ALLEGO GRAPHICAL INTERFACE.** It does not save the result anywhere
recoverable, we lost a sweep that way on 2026-08-06. Always use this script, which writes one
comma separated values (CSV) file per sweep. **Re-run `remap_channels.py` first after any port
or headstage change.**

## Overnight recording

**`allego_0__uid0807-19-14-58`, started 2026-08-07 19:14:58 KST**, in
`/home/skimlab/radix/data/`. Verified running: 1000 Hz, **262 channels (256 primary, 2 aux,
2 digital in, 2 digital out)**, and the `_data.xdat` file confirmed growing on disk at the
expected rate. **andrea stops it tomorrow morning.** Roughly 3.8 GB per hour, so a 24 hour run
is about 90 GB against 748 GB free.

🔴⭐⭐ **BUG FOUND IN THE RADIENS PYTHON CLIENT, AND THE WORKAROUND.**
`AllegoClient.set_recording_config(...)` **DOES NOT WORK.** It fails with

```
grpc.RpcError: StatusCode.INTERNAL  details = "Exception serializing request!"
```

The reason: the `allego.ConfigRecording` protobuf message has a **required** `recordingType`
enum field, and `radiens/api/api_allego.py::set_recording_config` never sets it, so the message
cannot be serialised. **This is a library bug, not a rig problem, and it will bite again.**

⚠️ **IF THE RECORDING CONFIG IS SET AND NOTHING HAPPENS, CHECK THAT YOU ACTUALLY GOT AN
EXCEPTION. A FAILED CONFIG LEAVES THE OLD PATH IN PLACE SILENTLY.**

Workaround, build the message yourself (script kept at
`eeg-emg-analysis/qc/set_recording_config_fixed.py`, worth promoting into `qc/` if we need it again):

```python
from radiens.grpc_radiens import allegoserver_pb2 as ap, allegoserver_pb2_grpc as ag
req = ap.ConfigRecording(baseFileName="allego", baseFilePath="/home/skimlab/radix/data",
                         dataSourceIdx=0, timeStamp=True, splitFilesByPort=False,
                         forceStartAtTStamp0=False, recordingType=ap.continuous)
stub.SetConfigRecording(req, timeout=60)
```

⚠️ **DO NOT TRUST THE `path` FIELD IN `get_status().recording`.** It reports the **client
process's current working directory**, not the actual output directory. I watched it change
from `.../eeg-emg-analysis/qc` to `/home/skimlab/Monitoring_project` to `/home/skimlab` purely
because I ran the query from different folders. **The only reliable check is to `ls` the
destination and confirm `_data.xdat` is growing.**

⭐ `set_recording('on')` turns streaming on by itself if it is off, but I set streaming on
explicitly first anyway, because the sweep required streaming to be off.

## Still open

> [!warning] Written before the ground wiring error was found. The first three bullets are
> **answered or withdrawn**, kept only to show the order of reasoning. The last three still stand.

- ~~Is the new cohort actually dead, or is this just intermittent contact in a bad window?~~
  **ANSWERED: neither. The animals were floating.**
- ~~Why did the hum collapse without any signal appearing? Leading guess is the cerebellar ground
  giving a better common mode reference.~~ 🔴 **WRONG, AND IT WAS THE BIGGEST CLUE.** The correct
  answer is the opposite: **there was no ground at all**, so mains drove the whole animal as
  common mode and **the bipolar channels rejected it**. Low hum and absent signal, one cause.
- ~~The 8 conductor tether wires are not soldered, that is the first suspect.~~ 🔴 **WITHDRAWN.**
  The tethers passed a multimeter continuity check and the wiring error explains everything
  without them.
- We have lost the empty cut tether control. The unwired amplifier floor still works and is
  free, and **A/35 is a bonus "implanted mouse, unwired site" control**, but write down that
  the dedicated one is gone.
- Nothing here tests the negative half of each electrode pair. Still unmeasurable, see
  [[impedance-negative-electrode-unmeasurable]].
- **No video.** Cameras were removed on 2026-08-04 and have not been restored, so any EMG that
  looks like movement artefact stays unresolvable.

---

## Pre-registration, written 2026-08-07 ~21:45, BEFORE the night exists

Recorded in advance so tomorrow's scoring is honest. At this point I have read **144 minutes**
of the running recording and scanned **all 256 amplifier channels**.

**Prediction 1.** A2, the control, scores **usable EEG over the great majority of the night**,
with a longest unbroken block of hours. Confidence **high**.

**Prediction 2.** The seven new mice score **0.0% usable EEG and 0.0% usable ECG**. Confidence
**moderate**, NOT high, see the falsifier below.

**Prediction 3.** **No ECG channel shows a heartbeat** at 600 to 750 beats per minute with an
interval coefficient of variation under 0.1. Confidence **high**. ⭐ This is the primary test
because it needs no threshold we invented.

**Prediction 4.** The most likely single exception, if there is one, is **A/2**, the only new
mouse channel with real spectral tilt (slope -0.91). Weak prediction.

⚠️ **WHAT WOULD FALSIFY PREDICTION 2, AND WHY I AM NOT CONFIDENT.** On 2026-08-06 a 21 minute
window gave p = 1.0e-07 for a conclusion that turned out to be **exactly backwards**, and D2
went from 0.0% to 87.9% usable once a real night was recorded. 144 minutes is better than 21 but
**it is still not a night**. A channel that is open now can come good for a multi hour block
later. **If any new mouse produces a multi hour clean block, prediction 2 is dead and the
"nothing is connected" reading of tonight goes with it.**

## What the 256 channel scan settled

Method: Welch power spectrum per channel, **mains bins excluded** (±2.5 Hz around every harmonic
to 480 Hz), so nothing here depends on filter design. Discriminator is the ratio of 1 to 40 Hz
amplitude over 100 to 300 Hz amplitude, because biology is low frequency heavy and noise is flat.

| channel | lf 1-40 | hf 100-300 | slope | lf/hf |
|---|---:|---:|---:|---:|
| **A/33 CONTROL EEG** | **52.9** | **11.0** | **-1.52** | **4.79** |
| A/34 CONTROL EMG | 34.1 | 43.1 | -1.37 | 0.79 |
| all 21 new mouse sites | 5.4 to 456 | 10 to 597 | -0.01 to -0.91 | 0.42 to 0.92 |
| 104 floor channels | median 166 | | | 0.78 to 2.89 |

⭐⭐ **A/33 IS UNIQUE ACROSS ALL 256 CHANNELS.** Nothing else has that signature.

✅ **PINOUT MISMAPPING IS RULED OUT.** The top 20 channels by low frequency content are **all
floor channels**, i.e. loud open inputs. No biological signal is hiding on a site we were not
looking at. Impedance says the same thing independently: `/1`,`/2`,`/3` read 0.08 to 0.36 MΩ
while `/4`-`/16` read 4.3 MΩ.

✅ **THE LOUD vs QUIET SPLIT AMONG THE NEW MICE IS MEANINGLESS.** B/2, B/3, B/33 and C/35 are
loud (330 to 456) and A/1, C/1, D/1, D/35 are quiet (5 to 10), but **both groups have slope near
zero and lf/hf near 0.6**. Loud noise and quiet noise. Neither is signal.

## The short hypothesis, revised after the multimeter result

> [!warning] 🔴 **SUPERSEDED ~30 MINUTES LATER BY THE GROUNDING ERROR.** Candidates 1 and 2 below
> are **withdrawn**. Candidate 3, the ground, is the answer, and note it was already on the list
> here and I ranked it last. Kept because the reasoning about beep testers is still useful.

🔴 **andrea reports every tether was checked with a multimeter before use and NO conductor beeps
against any other.** That kills the metallic short in the tether. ⚠️ **BUT A CONTINUITY BEEPER
FIRES BELOW ROUGHLY 30 TO 50 Ω, AND THE IMPEDANCES WE MEASURE ARE 4 TO 20 kΩ AT MINIMUM AND
84 TO 360 kΩ AT MEDIAN. A RESISTIVE LEAK OF TENS OF kΩ IS COMPLETELY SILENT ON A BEEP TEST AND
WOULD STILL NULL A BIPOLAR PAIR.** The bench test also checks the tether unmated, so it says
nothing about the implant head, the pins under compression, or fluid at the connector.

⭐⭐ **REVISED READING: the new mice's channels are quiet, low impedance and low hum, which is
what a WELL CONNECTED electrode looks like. What they lack is a potential difference.
Good contact, no differential.** Surviving candidates, all animal side:

1. **A conductive bridge across each pair at the implant**, fluid or saline under the cement.
   Two tips in one conductive pool give low impedance to everything and no voltage between them.
2. **The pair members sit at the same potential** for a placement reason.
3. **The cerebellar ground**, the other thing that changed for all seven and not for the control.

⭐ **THE ECG IS THE STRONGEST ANOMALY.** A thoracic electrocardiogram is a whole body dipole and
any two points across the chest give hundreds of microvolts of QRS almost regardless of placement
detail. **Seven of seven ECG channels show nothing.** That is hard to explain by placement and
easy to explain by a bridged pair.

## The discriminator worth running next

> [!danger] 🔴 **WITHDRAWN. DO NOT RUN THIS. IT COSTS AN ISOFLURANE EPISODE AND ANSWERS A
> QUESTION THAT IS ALREADY ANSWERED.** The fault is the ground wiring, and the fix is a connector
> re-mate with no anaesthesia. Kept only as a record of what I was about to propose.

The control shares the rig with the seven but shares **neither the surgery batch, nor the
8 conductor unsoldered tether, nor the cerebellar ground**. So the fault is in one of those
three, and no amount of further analysis of this recording separates them.

⭐ **Cheapest discriminator: put ONE new mouse on a spare old style short soldered tether.**
Comes alive means tether. Stays flat means surgery or ground, and then the ground site is the
next thing to vary. ⚠️ **This costs one isoflurane episode on one animal**, so it is andrea's
call, not mine, and it should wait until the night is scored.

---

## 🔴⭐⭐⭐ THE GROUND WIRE WAS CONNECTED TO THE WRONG PIN

**andrea's hypothesis, 2026-08-07 ~22:00, and it explains the whole night.**

The cerebellum dura pin should mate to the **brown** wire, which runs through the brown slip ring
line and lands on the **GND pad of the headstage adapter board**. Instead the cerebellum pin was
mated to the **orange** wire, which is floating at the far end, and the brown wire sitting in the
headstage GND pad **is not connected to the mouse at all**.

⇒ **ALL SEVEN NEW MICE HAVE BEEN RECORDING WITH NO GROUND / REFERENCE CONNECTION TO THE ANIMAL.**
The control is untouched because it is the old mouse on the old tether.

### Why this explains every single thing we saw

1. ⭐⭐ **THE FLEET WIDE HUM COLLAPSE, WHICH NOTHING ELSE EXPLAINED.** With no ground, mains
   drives the **whole animal** as a common mode signal, and **a genuinely bipolar channel rejects
   common mode**. So the differential hum goes DOWN. ⚠️ **The "lose the ground and get enormous
   hum" intuition is for SINGLE ENDED referential recording, not for a differential pair.**
   **Low hum and absent signal come from the same cause.**
2. ⭐⭐ **IMPEDANCE EXCELLENT, PURELY RESISTIVE, AND PERFECTLY STABLE WITH ZERO FLIPS.** With GND
   floating the injected current has to return through **the other electrode of the pair**, so
   the measurement is electrode → tissue → electrode. That is a real and stable tissue path,
   resistive, 100 to 360 kΩ. ⭐ **The stability is the tell: every failure this rig has ever had
   was intermittent. Seven channels at 100% duty with ZERO flips is not how electrodes fail, it
   is how a wiring error behaves.**
3. **Seven of seven identical, no intermittency.** Deterministic, as a mis-pin must be.
4. **The control is unaffected** on the same port, splitter and amplifier.
5. **No heartbeat on any ECG channel**, which electrode placement cannot explain.
6. ⭐ **The three channels of each new mouse carry substantially the SAME waveform**, mean
   broadband |r| 0.38 and **D1 at 0.79**, while the control's three channels are independent at
   0.13. Skull EEG and thoracic ECG have nothing in common unless everything is riding one shared
   floating potential. ⚠️ Partly confounded: a channel with real signal is automatically less
   correlated with its neighbours, so some of the control's 0.13 is *because* it works.

### What does NOT fit, keep it in view

⚠️ A missing bias return should push the amplifier out of its linear range, and we measured
**zero railing**. A soft loss of sensitivity on an AC coupled Intan front end is plausible but
was **not demonstrated** from this data.
⚠️ 🔴 **A PREDICTION WAS MADE AND FAILED TONIGHT.** I predicted the impedance phase would sit
near **-90°** if the path were tether capacitance. It came back **~2° or ~178°, purely
resistive**. The capacitive coupling idea is dead. Weight the rest accordingly.

### Superseded by this

🔴 **The "bipolar pairs are shorted in the unsoldered 8 conductor tether" hypothesis is
WITHDRAWN.** andrea's multimeter check already showed no conductor beeps against any other, and
the grounding error explains the same observations without needing a short.
⚠️ The point about **beep testers firing below roughly 30 to 50 Ω, so a tens of kΩ leak is
silent**, remains true and worth keeping, it just is not what happened here.
🔴 **The "conductive bridge / fluid under the cement" idea is also withdrawn**, and with it the
suggestion to spend an isoflurane episode moving one mouse onto an old style tether.
✅ **NO ANAESTHESIA IS NEEDED. This is a connector re-mate, not the implanted electrode**, so it
is NOT the "never reseat an electrode" case.

## Decision taken 2026-08-07 22:01

andrea **stopped the recording** and will **re-pin the ground on all seven mice tomorrow**, then
start a fresh recording. I had suggested fixing them one at a time inside the running file;
**her call, and it costs nothing**, because the control already has its 23.66 h night from
2026-08-06/07 and the pre-fix baseline is fully captured.

🗂️ **PRE-FIX BASELINE FILE, KEEP IT: `allego_0__uid0807-19-14-58`**, 19:14:58 to 22:01,
**2.768 h**, 10.44 GB, `~/radix/data/`. Verified intact on stop: data and timestamp files agree
to the sample (9,964,672 each), zero remainder bytes, no error string. **This is the before state
for all seven animals AND 2.8 h of the working control under the identical floor**, which is what
tomorrow's after state gets compared against.

## Tomorrow, in order

1. **Re-pin the cerebellum ground to the brown wire on all seven.** Confirm brown lands on the
   headstage GND pad and that the orange wire is no longer carrying the dura pin.
2. ⭐ **Watch the live stream BEFORE committing to a night.** If the hypothesis is right, EEG
   appears within seconds:
   ```
   /opt/neurosurveillance/venv/bin/python qc/grab_stream.py /tmp/check 60
   ~/eeg-analysis-venv/bin/python qc/live_screen.py /tmp/check
   ```
   ⚠️ **Two different interpreters, and neither can do both jobs**: `radiens` only exists in
   `/opt/neurosurveillance/venv`, and `scipy` only works in `~/eeg-analysis-venv`. ⚠️ Remember
   `get_signals()` returns **only the GUI selected channels**, 24 of them here.
3. **Run a fresh impedance block** with the ground correct. ⭐ **PREDICTION: the impedances
   should get WORSE, or at least change character**, because the return path moves from
   "through the paired electrode" to "through the ground electrode". **If the numbers stay
   identical at 100% duty with zero flips, the ground is still not connected.**
4. **Start the overnight recording.** ⚠️ `set_recording_config()` is broken, use
   `eeg-emg-analysis/qc/set_recording_config_fixed.py`, and confirm `_data.xdat` is growing in `~/radix/data`.
5. Score against the floor `/4`-`/16`, `/36`-`/48`, ⭐ **with the heartbeat as the primary
   yes/no test**, and compare directly against this pre-fix file.

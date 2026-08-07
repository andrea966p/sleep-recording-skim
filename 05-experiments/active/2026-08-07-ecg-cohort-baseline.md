---
title: ECG cohort baseline, 7 new mice plus the B1 control
date: 2026-08-07
status: active
tags: [eeg, emg, ecg, impedance, tether, cohort]
---

# ECG cohort, first baseline

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
(exactly the 8 slots times 3 roles), 1000 Hz. Scripts in the session scratchpad,
`grab_stream.py`, `look_live.py`, `look_live2.py`, `look_live3.py`.

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

⚠️ **NEVER SWEEP FROM THE ALLEGO GRAPHICAL INTERFACE.** It does not save the result anywhere
recoverable, we lost a sweep that way on 2026-08-06. Always use this script, which writes one
comma separated values (CSV) file per sweep. **Re-run `remap_channels.py` first after any port
or headstage change.**

## Overnight recording

Started right after the sweep block, to be stopped by andrea tomorrow morning. Roughly 3.8
gigabytes per hour, so a 24 hour run is about 90 GB, and there was 748 GB free when I checked.

## Still open

- Is the new cohort actually dead, or is this just the usual intermittent contact caught in a
  bad 120 second window? **The overnight recording is the only thing that can answer this.**
  Score it against the new `/4`-`/16`, `/36`-`/48` floor.
- **Why did the hum collapse without any signal appearing?** My leading guess is the cerebellar
  ground giving a better common mode reference, so mains rejection improved even where the
  signal electrodes are not in contact. That would mean the change is real and good, but
  independent of the contact problem. Not tested.
- **The 8 conductor tether wires are NOT soldered, they use thin heatshrink.** Both chains that
  ever worked on this rig, the arm B tether on B1 and the arm C tether on D2, were
  **soldered and resin encapsulated**. This cohort is the opposite. If the overnight recording
  is bad, that is the first suspect, and it is the same suspect we already had.
- We have lost the empty cut tether control. The unwired amplifier floor still works and is
  free, and **A/35 is a bonus "implanted mouse, unwired site" control**, but write down that
  the dedicated one is gone.
- Nothing here tests the negative half of each electrode pair. Still unmeasurable, see
  [[impedance-negative-electrode-unmeasurable]].
- **No video.** Cameras were removed on 2026-08-04 and have not been restored, so any EMG that
  looks like movement artefact stays unresolvable.

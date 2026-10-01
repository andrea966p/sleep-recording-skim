---
tags: [experiment, noise, grounding, ground-loop, usb, xdaq, mains, 60hz, 120hz, series]
created: 2026-09-30
status: active
---

# XDAQ noise series: power, cabling, grounding (started 2026-09-30)

> [!abstract] TL;DR
> A new series of rig-only tests (no mice) to find where our noise comes from, changing ONE thing at
> a time: rack layout, USB data cable, USB isolator, PC location, power brick. Background and the
> choices already made are in the handover `xdaq-power-grounding-handover.md` (Downloads, 2026-09-30).
> **Entry 1 (today) is NOT a usable baseline.** No mice were on the rig and every input ended in the
> free animal-side wires of a slip ring, so it measured antenna pickup, not the noise a mouse would see. It did show that
> **port A picks up a strong 120 Hz field that port B does not**, which gives a first source to hunt.

## Rig state at entry 1 (2026-09-30)

- **No mice, no tethers.** Chain = XDAQ > SPI cable > headstage + adapter board > 8ch slip ring. The slip-ring
  wires into the adapter-board sockets are not coiled/twisted; the slip ring's animal-side wires hang free.
- Recording rack: XDAQ alone with its own earthed multitap, KonteX original USB-PD brick (JHX-AC2032,
  ungrounded, fixed 12 V PDO), ASUS mini PC. Everything else (Dell PC, white noise generator, speakers,
  router) on the other rack, on another multitap.
- **XDAQ chassis GND wired to the socket earth (building).** Confirmed by Andrea 2026-09-30. This
  corrects the 07-16 vault claim that the Gen-1 Core has no chassis GND.
- Ferrite on the SPI cables near the headstages; headstages covered in foil. **No ferrite on the USB
  cable, no USB isolator yet.** Stock USB data cable.
- Only ports A and B enumerated (64 ch each = A1, A2, B1, B2).
- USB link: `usb 2-4`, **5000M** SuperSpeed (expected without an isolator; it should read 480M after).
- Software: radiens 4.0.0, kernel 7.0.0-28-generic, Allego 1 kHz `XDAQ_ONE_REC`.

## Entry 1: 5.5 min, no mice, slip-ring wires free

File: `~/radix/noise-tests/2026-09-30/noise_baseline_0__uid0930-15-50-52` (kept out of `radix/data` on
purpose, so the NAS and S3 jobs skip it). Analysis: `eeg-emg-analysis/qc/noise_scan.py`.
Comparison: `allego_0__uid0921-00-17-34` at 55900 s (2026-09-21 ~15:50, old layout, mice on).
Figure: `~/radix/noise-tests/2026-09-30/figures/psd_compare.png`.

During the recording Andrea was **touching the free wires of the B1 slip ring**. That bridges the inputs
through skin, so B1 is a hand-shorted input, not an open one.

| | 09-21, mice on | 09-30, no mice |
|---|---|---|
| EEG delta (1-4 Hz) | 500-980 | 1-45 |
| EEG 60 Hz / own chip floor | 0.002-0.02 | A: 0.59-0.75 (open wire), B2: 2.3 (open), B1: 0.23 (hand) |
| EEG 60 Hz | 8-11 uV | A: 1600-1800, **B2: 4176 (16% clipped)**, B1: 66 |
| 120 Hz on animal inputs | 1-5 uV | **port A: 1450-2740 uV (as large as or larger than the 60 Hz)**, B2: 170-1018 |
| 120 Hz / 60 Hz on the FLOOR inputs | 0.03-0.13 | **A1 0.59, A2 0.31**, B2 0.03 |
| B1 EEG broadband 1-45 Hz | 83 | **2.5 uV** (inputs shorted by hand: about the amplifier's own floor) |
| Transients hitting >=75% of chips at once | 0 in 5 min | 1 in 5.5 min |

- The 60 Hz and 120 Hz levels were **flat over the whole 5.5 min**. That is steady field pickup, not bursts.
- The PSDs have lines at **20 Hz spacing**. These are mains harmonics above 500 Hz folded back by the
  1 kHz sampling, so the interference has sharp edges.
- B/2 has a small comb at **9.77 Hz spacing** (1 per 102.4 ms). It is periodic, not mains, and looks digital.

## Entry 2: 3 min, free slip-ring wires taped, XDAQ multitap + brick moved away (2026-09-30 16:45)

File: `~/radix/noise-tests/2026-09-30/noise_e2_tape_multitap_0__uid0930-16-45-25`. Two changes at once (black
electrical tape on the free slip-ring wires, and the XDAQ multitap + KonteX brick moved further from A1, where
it sat just above), so any steady-state difference cannot be pinned on either one. Andrea also **toggled the
room lights from the wall switch** during the run.

### ⭐ Result: a light switch puts a spike on EVERY chip at the same instant

Four events at **39.9, 49.2, 168.3 and 172.0 s**. Each is one ~100 ms spike of **3-9 mV**, on the wire-free
floor inputs and the slip-ring inputs of **all four chips on both ports at once**. Between them the steady 60 and
120 Hz levels did not change, so the **lights are NOT the source of port A's steady 120 Hz**. They are a source of
**transients**.

### ⭐ The same thing happens with mice on: the automatic light timer, `uid0921`

Searched the 2026-09-21/22 run (8 mice) for events on >=75% of chips' floors in the same 100 ms, at the timer times:

| window | all-chip events | what the mice saw |
|---|---|---|
| 09-22 09:00 (lights ON), event at 08:59:53 | **1** | EEG 89-1056 uV, **EMG 117-4216 uV**, all 8 mice at once |
| 09-21 21:00 (lights OFF), event at 21:01:08 | **1** | EEG 124-326 uV, EMG 68-939 uV, all 8 |
| 09-21 09:00 (lights ON) | 0 | switching does not always spike (it depends on where in the mains cycle the contact closes) |
| 09-21 12:48 control, 2 min | 0 | |

So the "coordinated spike across EEG/EMG in the same mouse" has at least one confirmed cause that is NOT the
mouse: **switching events on the building supply, seen by every mouse at once**. The handover's section 4.4
mechanism (shared-circuit transients) is now measured, not assumed. Light switching is only 2 events a day. Other
switching loads in the building (compressors, HVAC, the Dell PC, the noise generator) would do the same.

### ⭐ Whole-run scan: all-chip events are RARE (2026-09-30)

`eeg-emg-analysis/qc/allchip_scan_file.py` over the whole S-SL endpoint run, `uid0920` + `uid0921`
(09-20 09:00 to 09-22 12:57, **52 h, 8 mice**). Criterion: floor inputs of >= 6 of 8 chips above 5x their
chunk median in the same 100 ms. Positive control: it finds all 4 of today's wall-switch events at the right
times. Output: `~/radix/noise-tests/allchip-scan/*.csv`.

**8 events in 52 h (0.15 per hour).**

| clock | chips | biggest on the mice | likely cause |
|---|---|---|---|
| Sun 09-20 15:38:50 | 6 | EEG 243, EMG 308 uV | unknown |
| Sun 09-20 15:54:44 | 6 | EEG 160, EMG 291 uV | unknown |
| Mon 09-21 18:22:48 | 8 | EEG 256, EMG 453 uV | unknown (evening cluster) |
| Mon 09-21 18:23:23 | 8 | EEG 241 uV | unknown (evening cluster) |
| Mon 09-21 18:31:49 | 8 | **EMG 3462 uV (A1)**, EEG 343 | unknown (evening cluster) |
| Mon 09-21 21:01:08 | 6 | EMG 939, EEG 326 uV | **light timer OFF** |
| Tue 09-22 08:59:53 | 8 | **EMG 3.2-4.2 mV on 6 mice**, EEG up to 1056 | **light timer ON** |
| Tue 09-22 10:08:32 | 6 | EEG 190 uV | unknown |

The timer made a spike on 2 of its 4 switchings in this run (none at 09-20 21:00 or 09-21 09:00).

**What this means.** Building or room switching reaches every mouse at once, but only about 4 times a day, and
usually at EEG-sized amplitudes (100-350 uV peaks). Only the lights-ON event is large. So **if coordinated
EEG/EMG/ECG spikes inside ONE mouse are frequent, most of them are NOT building transients.** They are
within-mouse (movement, chewing, the ground pin or connector). The wire-free floor inputs are high impedance and
more sensitive to room pickup than a connected mouse, so a transient the floors miss is unlikely to reach the mice.

**Discriminating test for a specific spike:** give the clock time of a coordinated spike seen in Allego. If the
other chips' floor inputs spike in the same 100 ms, it is electrical and system-wide; if not, it belongs to that mouse.

### What the all-chip events look like (waveform + spectrum, 2026-10-01)

Plotted with a 3-cycle comb (x[t] - x[t-50 ms]); it removes 60 Hz and every harmonic and cannot ring. The
60-120 Hz "ringing" in a first notch-filtered plot was the notch filters' own ringing, not the signal.
Figure: `~/radix/noise-tests/2026-09-30/figures/event_waveforms_comb.png`.

- **No characteristic frequency.** With mice on (09-21 18:31:49, 09-22 08:59:53 lights ON) each event is ONE sharp
  STEP: edge under 2 ms, broadband up to the 500 Hz Nyquist limit. On the mouse channels the step then decays over
  about 100-150 ms. That decay is the amplifier's own ~1.1 Hz high-pass settling, so in EEG it looks like a slow wave.
- **Manual wall switch (today, open wires):** a BURST of 5-10 sharp spikes over 50-100 ms, about 8-12 ms apart.
  That is close to half a mains cycle (8.3 ms), consistent with the switch contact arcing and re-striking. Not proven.
- **Rate, revised after looking at each waveform:** 3 of the 8 detections (09-20 15:38 and 15:54, 09-22 10:08)
  have a FLAT floor, so they are probably false detections from mouse activity. **Real: 5 in 52 h (about 2.3 a day);
  large, mV-level on the mice: 2 (about 1 a day).**

### Steady state vs entry 1 (confounded, read with care)

Port A 120 Hz roughly halved (A2 EEG 2743 -> 1300 uV, A1 floor 763 vs 1433) but A1 EEG 60 Hz went UP
(1786 -> 2750) and B2 120 Hz went up. The slip-ring wires were handled for the tape, which moves the antennas,
so none of this can be attributed to the multitap move.

### Next for this thread

- Whole-file scan of archived runs: count all-chip events per hour and match them to the light timer and other
  known switching times. That tells how much of the coordinated-spike problem is building transients.
- Route test: is the spike conducted (mains/earth, via the XDAQ earth wire and the PC's earth through the USB
  shield) or radiated? The isolator removes one conducted path, so repeat the light toggle before and after.

## Entry 3: USB isolator, before vs after (2026-10-01)

Same rig as entry 2 (no mice, free slip-ring wires taped), with the light switch flipped in both runs. One change:
**DFRobot FIT1019 USB isolator** inserted, PC > isolator > data cable > XDAQ. Allego closed and `allegoserver`
confirmed gone before the swap; relaunched without `--disable-gpu`.

- Before: `~/radix/noise-tests/2026-10-01/iso_before_0__uid1001-15-40-40` (link 5000M, bus 2).
- After: `~/radix/noise-tests/2026-10-01/iso_after_0__uid1001-16-09-23` (link **480M**, bus 3, as expected).
- Allego kept `XDAQ_ONE_REC`, 1 kHz, A+B at 64 ch. **Zero dropped samples** in both (223104/223104, timestamp step always 1).
- Figure: `~/radix/noise-tests/2026-10-01/iso_psd.png`.

Median over each chip's 16 open inputs, a quiet 70 s stretch (uV):

| chip | | 60 Hz | 120 Hz | 180 Hz | 1-45 Hz (between lines) | 100-450 Hz | slots with no amplifier |
|---|---|---|---|---|---|---|---|
| A1 | before / after | 2263 / 1996 | 1053 / 1117 | 335 / 286 | 19.6 / **38.8** | 43.1 / **69.0** | 30.3 / 29.6 |
| A2 | before / after | 1597 / 1583 | 818 / 925 | 359 / 347 | 17.4 / **29.1** | 43.4 / **55.2** | 30.8 / 30.9 |
| B1 | before / after | 1708 / 1906 | 372 / 497 | 104 / 111 | 9.1 / **21.0** | 16.8 / **34.6** | 31.8 / 31.9 |
| B2 | before / after | 2147 / 2033 | 717 / 859 | 298 / 288 | 19.1 / **31.5** | 32.6 / **46.4** | 29.8 / 29.0 |

1. **Mains unchanged.** The USB-shield loop was NOT driving the 60/120 Hz pickup on these inputs.
2. **Light-switch spikes NOT reduced** (floor peaks 0.6-3.5 mV after vs 0.2-3.1 mV before). The spike does not
   travel through the USB cable; it arrives through the air or the power/earth wiring.
3. 🔴 **The broadband floor between the mains lines went UP**: power x4-12 across 1-500 Hz, flat (white), and
   steady through the whole run (1-45 Hz: 20 uV before, 40 uV after, every 10 s window). Slots with no amplifier
   are unchanged, so the digital path is clean and the extra noise enters at the amplifier inputs.
   Leading hypothesis: high-frequency noise from the isolator's own isolated power converter, or a less firm
   high-frequency reference for the XDAQ now that the USB shield no longer ties it to the PC, either way picked up
   by the open inputs and folded into band by the sampling. **Not tested yet.**
4. Open inputs are extremely sensitive and this is one A/B pair 30 min apart, so (3) needs an A/B/A check
   (direct cable back for 3 min) and then a dummy-load test before anyone decides to keep the isolator for mice.

### ✅ A/B/A check: the isolator DOES raise the floor (2026-10-01 16:29)

Run 3, `direct_again_0__uid1001-16-29-42`: isolator removed, direct USB cable back (ferrite on the cable), link
5000M. Quiet stretches 5-40 s and 140-210 s, median over the 64 open inputs (uV):

| run | 60 Hz | 120 Hz | 1-45 Hz between lines | 100-450 Hz | slots with no amplifier |
|---|---|---|---|---|---|
| 1 direct 15:40 | 1991 | 863 | 21.3 | 36.8 | 30.5 |
| 2 isolator 16:09 | 1931 | 849 | **31.9** | **53.0** | 30.3 |
| 3 direct 16:29 | 2023 | 893 | 16.6 | 41.9 | 29.8 |

The 10 s time course of 1-45 Hz reads about 20, then 40, then 19 uV. **The rise follows the isolator in and out.**
Mains is identical in all three. Light-switch spikes are the same size in all three (direct again: 0.2-1.9 mV).

**Verdict for now:** the isolator buys nothing measurable (no change in mains or in switch spikes) and costs about 2x
broadband noise on open inputs. **Record with the direct cable.** The isolator is parked until the dummy-load test
shows whether the rise survives on mouse-like inputs. Figure: `~/radix/noise-tests/2026-10-01/aba_psd.png`.

## Entry 4: adapter boards OFF on B1/B2, unipolar headstages on C1/C2 (2026-10-01 16:48)

File `~/radix/noise-tests/2026-10-01/Bboards_off_Cunipolar_0__uid1001-16-48-09`. Question (Andrea): is the
mV-level pickup on /1-/16 our soldering, given the sockets sit on pads 0-15? Predictions were written down
BEFORE the data. Andrea's hand came near B1 once during the run; the 10 s traces show nothing measurable. Compared
against run 3 (16:29, board on), 60 Hz in uV, median per group:

| chip | /1-/8 (socket pads 0-15) | /9-/16 (bare pads 16-31) | /17-/32 (no amplifier) |
|---|---|---|---|
| A1, unchanged control | 2940 -> 2946 | 1759 -> 1766 | 3 -> 3 |
| A2, unchanged control | 2805 -> 2794 | 1235 -> 1271 | 3 -> 3 |
| **B1, board removed** | **2574 -> 186** | **1287 -> 217** | 4 -> 3 |
| **B2, board removed** | **3039 -> 248** | **1756 -> 313** | 3 -> 2 |

- Control port A did not move, so conditions were stable.
- Prediction "still hundreds to thousands, maybe less": **only partly right.** The open headstage pins still pick up
  about 200 uV, but **the board plus the slip ring carries 6-12x more.** Both the socket channels AND the bare-pad
  channels drop, so it is not the solder joints on pads 0-15 specifically. The sockets add only about 2x on top.
  With the board on, every input is a GOhm open input sitting beside the slip-ring wires and the slip-ring GND wire
  (the far end is free), and pF of coupling is enough for mV of 60 Hz. It is the antenna size, not a defect.
- **No sign of a solder fault in the data.** Run 3 and run 1 (board on): no input pair reads like a short
  (a bridged + / - pair would read near 0 at 60 Hz), and no two channels track each other. Adjacent-channel
  correlation is at most 0.33. The one B2 pair at r 0.66-0.81 is a DIFFERENT pair in different runs (B/36-B/39,
  then B/37-B/47), so it is not a fixed bridge. The quietest B1 site, B/16, still carries 450 uV of 60 Hz, so it is not shorted.
  A DMM check with the boards off (pad to socket continuity, socket to socket and socket to GND open) would settle it.
- **Port C, unipolar headstages:** only sites **/9-/24 and /41-/56** float (3.7-4.6 mV of 60 Hz). The rest read about
  4 uV with almost no 60 Hz, like amplifiers with their input tied to the reference. That fits Intan's 16-channel
  unipolar headstage, which (from memory, not checked against the datasheet) wires RHD2132 amplifier channels 8-23
  to the connector and ties the rest. It also matches the vault's note that the unipolar layout's unused inputs are tied
  to ground. With nothing attached, the unipolar open inputs pick up ~15-20x more than the bipolar headstage's bare pins.

## Splitter check from archived data (2026-10-01)

Question: do the two mice on one SPI splitter (shared cable ground + supply) share spikes? Script
`eeg-emg-analysis/qc/splitter_coincidence.py`, `uid0921`, two 1 h blocks (01:57-02:57 night, 15:47-16:47 day).
Per 100 ms window, any EEG or EMG event above 8 robust SD (mains removed with the 3-cycle comb), all-chip
windows removed. Observed coincidences vs chance (product of the two animals' rates):

| pair | night | day |
|---|---|---|
| A1-A2 | 0.8x | 2.0x |
| B1-B2 | 0.8x | 0.4x |
| C1-C2 | 1.2x | 1.4x |
| D1-D2 | 0.7x | 0.4x |
| mice on DIFFERENT ports, median (range) | 0.9x (0.3-2.4) | 0.9x (0.3-2.3) |

**Splitter partners coincide at chance, inside the range of unrelated pairs.** No sign that the splitter couples
the two mice. Swapping it out is not worth an experiment. It also means each mouse's spikes are its own (within-mouse),
which fits the whole-run scan.

## 🗂️ Recordings in this series and where they are

Packaged as `XDAQ_noise_series_2026-09-30_to_10-01/` (built in `~/radix/noise-tests/_nas_package/`, hard links to the
originals). Each folder holds the renamed Allego set plus a `README.txt` with why, conditions, what changed, the light
flips, the findings and how they were measured. `INDEX.csv` has the same notes as one table; `scripts/` and `figures/` sit beside them.
**On the SKIM NAS (2026-10-01):** `SKIM_DATA/02_Data_Sleep/andrea/noise-tests/XDAQ_noise_series_2026-09-30_to_10-01/`
(`/mnt/skimnas/...` on e10). 39 files, 855 MB, every one SHA-256 verified by reading back from the share with the cache
dropped. Andrea first asked for `/home/Andrea_E10`; that folder exists on neither NAS, and she chose this location instead.

| folder | original Allego name | what it tests | headline |
|---|---|---|---|
| `NOISE01_2026-09-30_1550_open-inputs-first-look` | `noise_baseline_0__uid0930-15-50-52` | first look, open inputs, hand on B1 | no biology; port A 120 Hz; B1 hand-shorted = amp floor |
| `NOISE02_2026-09-30_1645_tape-multitap-moved-light-switch` | `noise_e2_tape_multitap_0__uid0930-16-45-25` | tape + multitap moved, light flips | **light switch spikes every chip at once** |
| `NOISE03_2026-10-01_1540_direct-cable-BEFORE-isolator` | `iso_before_0__uid1001-15-40-40` | isolator BEFORE | reference |
| `NOISE04_2026-10-01_1609_USB-isolator-FIT1019` | `iso_after_0__uid1001-16-09-23` | isolator IN | mains + spikes unchanged, **broadband 2x up** |
| `NOISE05_2026-10-01_1629_direct-cable-AFTER-isolator-ABA` | `direct_again_0__uid1001-16-29-42` | isolator OUT again | broadband back down: A/B/A confirmed |
| `NOISE06_2026-10-01_1648_B-boards-off-C-unipolar` | `Bboards_off_Cunipolar_0__uid1001-16-48-09` | boards off B, unipolar on C | board + slip ring = 6-12x antenna, not solder |
| `ANALYSIS_allchip-events_S-SL-run_2026-09-20to22` | (results only; source `uid0920` + `uid0921`) | whole-run all-chip events + splitter | 5 real events / 52 h; splitter at chance |

Local originals are still in `~/radix/noise-tests/2026-09-30/` and `2026-10-01/` (plus the hard-linked package). Deleting them is Andrea's call.

## Next steps (as of 2026-10-01)

1. **Foil bonded to the XDAQ chassis GND** (one wire, foil never touching animal, implant or headstage GND). Possible
   now that the chassis GND is known to exist. Should cut capacitive pickup on open inputs and shows whether the
   light-switch spike is radiated. 3 min before / after with the same light flips.
2. **Dummy loads** (100-500 kOhm per pin to GND, one slot per port): first baseline that predicts what a mouse sees;
   fair test for the isolator.
3. **Twist and shorten the slip-ring-to-board wires**; measure with the dummy loads (magnetic pickup).
4. **Within-mouse coordinated spikes:** check a specific spike time from Allego against the other chips' floors, or
   census EEG+EMG coincident events against movement and the light phase.
5. **Analysis safeguard:** flag all-chip events in QC (light timer 09:00 / 21:00).
Declined by Andrea 2026-10-01: battery-powered XDAQ test, moving the XDAQ multitap to another wall socket. SPI splitter swap not needed (archived-data check).

## Hypotheses (written 2026-09-30; status as of 2026-10-01)

> [!check] Status
> 1. Port A 120 Hz source: OPEN. Not the room lights (entry 2).
> 2. Coordinated spikes are within-mouse: SUPPORTED (whole-run scan: ~2.3 real all-chip events/day; splitter partners coincide at chance).
> 3. USB-shield ground loop: TESTED, no measurable effect on mains or switch spikes (entry 3); the isolator raised broadband instead.
> 4. 9.77 Hz comb on B/2: seen before the isolator, absent after it; not followed up.


1. **Port A sits near a harmonic-rich 120 Hz source.** Plain mains pickup is mostly 60 Hz. A strong
   120 Hz with its harmonics comes from rectifiers and switch-mode supplies: LED ceiling lights and
   drivers (120 Hz flicker, lights ON 09:00-21:00), the ASUS PC brick, the KonteX brick, the multitap.
2. **The reported coordinated spikes (EEG/EMG/ECG in ONE mouse) are a shared-path event in that mouse
   (ground pin, connector, slip-ring wiring) or movement, not building power.** A building transient would reach
   every chip, including the wire-free floor inputs of the other mice. In the 09-21 5 min piece the
   floors never spiked together. Test: scan full archived recordings for events that hit all chips'
   floors at once, and compare against events that hit only one mouse.
3. **A ground loop through the USB shield** (handover section 4.2) is confirmed physically but not yet
   shown to matter. Test with the earth-wire lift and then the isolator.
4. **The 9.77 Hz comb is digital**, tied to the acquisition block timing. Watch it across the USB cable and isolator changes.

## Next tests as planned on 2026-09-30 (SUPERSEDED by "Next steps" above; kept for the record)

1. **Dummy load, so the tests measure what a mouse would see.** On one slot per port, resistors of
   about 100-500 kOhm from EEG+ and EEG- (and EMG+/-) to GND, about the size of a good electrode
   (see [[positive-control-known-signal-injection]]). Every later entry uses the same load.
2. **Source hunt with the free slip-ring wires as antennas.** Record continuously; switch one thing off for 60 s at
   a time and write down the clock time: room lights, the multitap, the XDAQ brick. Chart 60 and 120 Hz per 10 s.
3. **Lights at 21:00.** Record 20:50-21:10. If the 120 Hz on port A drops at 21:00, the lights are the source.
4. ~~Earth-wire lift~~ **DROPPED 2026-09-30.** The earth wire has ring terminals screwed down at both ends, so it cannot
   be lifted for 2 min without tools. The loop is tested from the other side instead: the USB isolator breaks the USB-shield
   path while the earth wire stays (the manual's required path). Record before/after the isolator with the same load.
5. **Twist the slip-ring to adapter-board wires.** Foil blocks electric fields but not magnetic ones.
6. **Then:** USB cable swap, then the isolator (`lsusb -t` should read 480M), then move the ASUS PC.
   Do NOT move the PC to another outlet before the isolator is in (handover section 5).

## Open items

- ✅ **ASUS PC power (answered 2026-09-30):** on a DIFFERENT multitap from the XDAQ, but both multitaps go into the
  **same wall socket**, so there is one earth point and no circuit-to-circuit bridge. The loop still exists:
  XDAQ chassis > earth wire > multitap 1 > wall socket < multitap 2 < PC chassis < USB shield < XDAQ.
  Its size is set by the two multitap cords plus the USB cable. The PC brick's leakage current flows down
  multitap 2's earth wire, so the PC chassis can sit a little off the XDAQ chassis, and the USB shield
  carries that difference. Still no USB isolator.
- The 2026-09-23 13:42 `usb 2-4` disconnect happened with no recording running (the last one ended
  09-22 13:00), so it was an unplug during setup, not a dropout. The XDAQ was re-plugged 2026-09-30 15:03.

---
tags: [experiment, noise, grounding, ground-loop, usb, xdaq, mains, 60hz, 120hz, series]
created: 2026-09-30
status: active
---

# XDAQ noise series: power, cabling, grounding (started 2026-09-30)

> [!abstract] TL;DR
> A series of tests (rig-only from 09-30, with 4 mice from 10-01 evening) to find where our noise comes from, changing ONE thing at
> a time: rack layout, USB data cable, USB isolator, PC location, power brick. Background and the
> choices already made are in the handover `xdaq-power-grounding-handover.md` (Downloads, 2026-09-30).
> **Entry 1 (today) is NOT a usable baseline.** No mice were on the rig and every input ended in the
> free animal-side wires of a slip ring, so it measured antenna pickup, not the noise a mouse would see. It did show that
> **port A picks up a strong 120 Hz field that port B does not**, which gives a first source to hunt.
>
> **⭐⭐⭐ 2026-10-09: CONFIRMED OVER 24 h** (Entry 12, run `ee0263bffeaa`, 29.5 h):
> - every hour: chip floors under 240 µV (before 664-2965), A2 EMG 60 Hz 0.5-2.3 µV (before 14-27);
> - **A2 now scores WITHOUT the notch** (r@1min 0.615, before REJECT 0.19/0.29), and B1 at 0.587;
> - wake is 2-3x higher in the dark than in the light;
> - building events: 1 unexplained in 29.5 h, against 6 in 24 h;
> - the light-switch spikes are unchanged (rare, rejected per epoch);
> - a lab member's visit on 10-08 (16:41-17:37) is marked and set aside.
>
> **⭐⭐ 2026-10-07: THE GROUNDING FIX COLLAPSED THE MAINS** (Entry 11). The isolated-earth socket and the XDAQ bonded to the earthed rack:
> - chip floors at 60 Hz are 12-60x lower, and the EEG 60 Hz is about 2 µV on all four mice (A1 was 20);
> - A2's EMG 60 Hz went from 26-33 to 1 µV, B1's from 4-5 to 0.5 µV, and A2's EMG measure is now 12 % mains instead of 93-97 %;
> - A1's and B2's EMGs no longer rail, but they are still not EMG (implant side);
> - 🔴 the 800 µV ground gate now calls every chip UNJUDGEABLE: replace it before the next real recording;
> - a 29.5 h confirmation run, `ee0263bffeaa`, records until 10-08 21:02.
>
> **⭐ Verdict, 2026-10-06: with the per-mouse faults set aside, the room's noise is mostly a ghost** ([[2026-10-06-noise-hunt-verdict]]).
> - The EEG mains never reaches the staging, which reads 0.5–30 Hz.
> - The one real problem is the EMG mains, and a validated 60/120 Hz notch removes it. Not yet adopted: that is Andrea's decision.
> - Building spikes are rare and are rejected epoch by epoch.
> - Recommended: the cheap electrician work (Entry 10), then stop the hunt and put the effort into per-mouse reliability.
>
> **State of knowledge, 2026-10-03: 24 h with 4 mice, fully analysed** ([[2026-10-02-noise-series-4mice-24h-analysis]]; NAS
> `noise-tests/ANALYSIS_2026-10-01_to_10-02_4mice_24h/`):
> - **Nothing electrical reaches the connected EEG/EMG.** Hands, people, a wireless receiver and the facility air showers move
>   only the open inputs; the mice's own spikes are their own. All 4 EEGs are connected.
> - **Building-level events reach both ports a few times a day:** 4 overnight (the lights-ON + 01:59:56, 07:27:42, 08:41:14) and
>   3 in the light phase outside Andrea's visit (17:10:08, 18:12:11, 20:56:36). Causes unknown.
> - **The damage is mains in the EMG.** It is a median 68 % of the stager's EMG measure. Notching it is validated: shuffle 0/100,
>   dark > light wake 47/49 recordings vs 41/49 as published. NOT adopted: it would re-score published numbers (a decision).
> - **The ground gate cannot judge this rig** (audit C1). B1 flipped UNJUDGEABLE → PASS (floor 702 → 971 µV) with nothing touched.
>   B1's light phase is the only official SCOREABLE.
> - **A wire on a headstage foil feeds mains into that mouse's EMG** (A2: floor x2.1, EMG 60 Hz x1.15). Foils and shields need a
>   solid bond (plan T2a-c, grounding first): [[2026-10-02-noise-troubleshooting-plan]].
>
> **State of knowledge, 2026-10-02 02:00** (first overnight with 4 mice, run `cfdf8ebde0c6`, 21:00 → 09:02; kept as written,
> superseded where the 10-03 block above differs, e.g. the night was not free of floor coincidences):
> - **No electrical injection reaches the mice.** The clean positions A2 and B1 carry no narrow spectral line but 60 Hz itself, and their
>   floors never fire together (0 against a chance level of ≈0). Building switching reaches every chip only ~2 times a day (5 real all-chip events in 52 h of the S-SL run).
>   Coordinated EEG+EMG spikes are rare (A2 3 in 4 h) and never coincide with a floor event, so they are within-mouse.
> - **Hum is small and steady**: the EEG line itself is 2-8 µV peak on A2/B1/B2 (A1 ~20). Port A's 120 Hz from 09-30 is gone.
> - **USB isolator: no**. It raised broadband 2x (A/B/A). Splitter: no coupling. Board + slip ring = antenna on open inputs.
> - **QC problem**: B1 (good EEG and EMG) sits at ~740 µV on the 800 µV ground gate, because **six of its input pairs collapsed after
>   its board was re-seated and the mice were connected** (both on the same afternoon, so the data cannot separate them; Fig C), not because its ground is weak. The gate is mis-calibrated for the current wiring:
>   [[2026-10-02-noise-series-method-audit]].
> - **Rig side, to check**: the B1 adapter board seating / foil (pads ~10-11, 18-31). A1 and B2 EMG are open (implant side): EEG only.

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
Figure 1 (source `~/radix/noise-tests/2026-09-30/figures/psd_compare.png`):

![[2026-09-30-noise-fig1-psd-open-inputs-vs-mice.png]]

**Figure 1.** Spectra of the 8 animal inputs, 09-30 with no mice (orange, open inputs) vs 09-21 with mice on in the old layout (blue); dotted = that chip's wire-free floor. With nothing connected every input is an antenna: the mains lines sit 10^4-10^6 higher. B1 is low in orange because the slip-ring wires were being touched by hand (inputs bridged through skin).

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
Figure 2 (source `~/radix/noise-tests/2026-09-30/figures/event_waveforms_comb.png`):

![[2026-09-30-noise-fig2-allchip-event-waveforms.png]]

**Figure 2.** Six all-chip events: floor median (black) and the A/1, A/2 inputs, 50 ms comb (so each transient also shows an inverted copy 50 ms later). Top: the 8-mice run (09-21 18:31:49, the lights-ON 09-22 08:59:53, the lights-OFF 09-21 21:01:08). Bottom: the wall switch on 09-30 with no mice, mV-size bursts on every chip at once.

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
shows whether the rise survives on mouse-like inputs. Figure 3 below (source `~/radix/noise-tests/2026-10-01/aba_psd.png`).

![[2026-10-01-noise-fig3-usb-isolator-ABA.png]]

**Figure 3.** Median spectrum of the 64 open inputs: direct cable 15:40 (blue), USB isolator 16:09 (orange), direct cable again 16:29 (green). The mains lines are identical; the floor between them rises with the isolator in and falls when it comes out. No mice.

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

## Entry 5: FIRST RUN WITH MICE, 4 mice on A1 A2 B1 B2, 8-core tether (2026-10-01 19:50)

File `~/radix/noise-tests/2026-10-01/mice4_A1A2B1B2_first_0__uid1001-19-50-31` (3.3 min, light phase, mice just
connected). Rig as at the end of entry 4: direct USB cable with ferrite, boards back on B1/B2, unipolar headstages off,
only ports A and B attached. Stream checked before recording: 1000 Hz, 1.01x real time. Figure `mice4_first_look.png` in the same folder.
Script: `qc/mice_first_look.py` + `qc/noise_scan.py` (t 3-193 s).

![[2026-10-01-noise-fig4-mice4-first-look.png]]

**Figure 4.** First look with mice, 10 s per mouse (EEG 1-30 Hz blue, EMG 30-200 Hz red, offset -400 uV) and spectra (right). A2 and B1: EEG with a 1/f spectrum, EMG muscle-like (B1 shows a burst). A1 and B2: the EMG is an open input railing at about +-6 mV; bottom, 2 s of the two raw open EMGs, nearly identical, as two open inputs in the same field would be.

| mouse | EEG 1-30 Hz rms | EEG 60 Hz | EEG 60 / floor | EEG slope 2-40 | EMG 60 Hz | EMG 60 / floor | EMG clip | chip floor 60 Hz |
|---|---|---|---|---|---|---|---|---|
| A1 | 56 uV | 16 uV | 0.008 | -1.76 | **3468 uV** | **1.7** | **13.7 %** | 1999 |
| A2 | 78 uV | 6 uV | 0.004 | -2.07 | 24 uV | 0.016 | 0 | 1517 |
| B1 | 65 uV | 9 uV | 0.018 | -1.76 | 7 uV | 0.014 | 0 | 509 |
| B2 | 56 uV | 8 uV | 0.006 | -1.70 | **3577 uV** | **2.6** | **14.0 %** | 1351 |

- (Floors and 60 Hz in this table are `noise_scan` band rms: floors ×√2 for the gate's scale, and the EEG/EMG "60 Hz" is largely broadband
  signal. See the scale correction in Entry 6.)
- **All 4 EEGs are connected and look like EEG**: 60 Hz under 20 uV, 1/f spectra, delta 33-39 %. A1, B1, B2 carry
  22-24 % theta (awake, just connected); A2 has less theta and a steeper slope (probably resting).
- **A1 EMG (A/2) and B2 EMG (B/34) read like OPEN inputs**: 3.5 mV of 60 Hz, ratio over 1 to their own floor, and they
  hit the negative rail on 14 % of samples (offset plus hum). The two waveforms are almost identical, as two open inputs
  in the same field would be. Not yet known where the break is: rig side (slip-ring wire into the adapter-board socket),
  the tether/headcap connector, or the electrode. Impedance on A/2 and B/34 plus a socket check is the first step.
- **Those two railing EMGs also disturb their own chip**: on A1 and B2 the wire-free inputs carry 280-540 uV of 1-45 Hz
  (8-19 uV on A2/B1) and every A1/B2 EMG event coincides with a floor event. Hypothesis, untested: an input driven into
  the rail injects into the chip's shared reference. Until fixed, **A1 and B2 floors cannot be used as noise meters**.
- Good EMGs (A2, B1) are muscle-like: power rising above 80 Hz, B1 envelope p95/p5 6.5 with a visible burst.
- The 3 "system-wide" detections (t 21.8, 43.0, 46.9 s) are A1-floor-driven and tiny on B1 (34 uV), not light-switch-type events.
- B1 floor 509 uV is under the proposed 2000 uV line, but its EEG is plainly working; the 2000 line came from the old
  set-up and is not applied. Note only.
- EEG 60 Hz is already 6-16 uV, below the 50-100 uV target, so the remaining tests can only win on transients, EMG and broadband, not on EEG hum.
- **Andrea, 2026-10-01 20:05: tethers were checked and are fine; the A1 and B2 EMG faults are most likely from the
  surgical implantation and cannot be fixed.** These mice carry EEG only. Under the strict rung 2 (EEG AND EMG in the
  same epoch) they cannot be scored. For the noise tests, use the A2 and B1 chips as meters.
- **Monitor as Andrea set it (display only):** `Fields`, `Anti-Alias`, `Chan height` 40 px, `AMP Range` 500 uV,
  `AIN range` 1.5 V, `Window` 10 s, Viz band 1-40 Hz, plus the usual 60 Hz notch.
  ✅ **Checked that the notch does NOT reach the file** (`mice4_notchcheck_0__uid1001-20-09-32`, 1 min, recorded
  right after): wire-free floors still 558-2012 uV of 60 Hz and the open EMGs still 3.5 mV, the same as at 19:50. So the
  notch sits in the Visualization stage. The .xdat.json in radiens 4.0.0 files carries no filter spec, so this
  data check is the only way to confirm it. On screen, the 1-40 Hz band and the notch both hide the 60 Hz and most EMG.

## Entry 6: pre-overnight checks + repeatability baselines, then the first overnight with mice (2026-10-01 20:15-21:00)

Same 4 mice and rig as Entry 5, nothing touched by anyone between the checks. Andrea at dinner; run by Claude.

**1. Impedance block** (full detail in [[impedance-sweep-register]]): 20 sweeps, 20:18-20:29, streaming OFF
(impedance refuses with the stream on: `Z_measure attempted during data acq`). Floor 1.6 % < 0.5 MΩ, median 5.8 MΩ.
A/2 and B/34 read 5 % duty at ~4.8 MΩ, the same as an unwired input (p 0.28), which matches the stream. A2 and
B1 EMG 100 % connected. EEG duty 10-60 % around the 0.5 MΩ line while all four EEGs carry normal 1/f signal:
screen on the stream, not on the sweep. After restreaming, rate 0.998x real time.

**2. Allego's own Signal Metrics** (read through the API, nothing changed; packets 0.2 s, 30 samples over 60 s,
broadband so 60 Hz included). It only computes the SELECTED channels: wire-free inputs read 0, so it cannot
show the floor. Median RMS: EEG 58-69 uV on all four; EMG A2 39, B1 55 uV; A/2 and B/34 3.7-3.8 mV RMS with
~9.9 mV peak-to-peak, which is the rail.

**3. `qc.preflight_screen` + `qc.biology_probe`** on one 5-min live grab (20:30-20:35, ZT11.6, light):
A2 and B1 pass 100 %; A1 and B2 0 %, both on the open EMG only (EEG rms 59-72 uV, EEG 60 Hz 7-17 uV). Pre-flight
reports NO FLOOR (only the montage is selected). That does not matter here because the floor is measured from the
recorded files, which hold every channel (509-2035 uV per chip). Biology: A2 -1.64 and B2 -1.80, read as neural.
A1 -1.50 and B1 -1.43, "between the populations". Awake animals at ZT11.6 read flatter than the sleep-dominated
reference, as the probe warns, and Entry 5's spectra show theta. Not a fault. r(E,M) about 0 on all four, so no
shared-path fault.

**4. Repeatability: 3 untouched runs** (19:50 first look 3 min, `mice4_baseline1_untouched_0__uid1001-20-36-33`
5 min, `mice4_baseline2_untouched_0__uid1001-20-42-41` 5 min). Script `qc/baseline_compare.py` on the `noise_scan` JSONs (metrics read by `qc/allego_signal_metrics.py`).
Max/min across the 3 runs:

| metric (median of the chip's wire-free inputs unless EEG/EMG) | A2 chip | B1 chip | A1 / B2 chips |
|---|---|---|---|
| floor 60 Hz | **1.00** (1513-1517 uV) | 1.18 (509-599) | 1.02 / 1.01 |
| floor 120 Hz | 1.03 | 1.27 | 1.19 / 1.18 |
| floor broadband 1-45 Hz | **1.07** (18-19 uV) | 1.09 (8-9) | **2.56 / 3.07** |
| floor 100-450 Hz | **1.02** (6.2-6.3 uV) | 1.10 (12-13) | **3.81 / 2.98** |
| EEG 60 Hz | 1.15 (6-7 uV) | 1.28 (9-12) | 1.01 / 1.23 |
| EMG 100-450 Hz (biology) | 1.54 | 1.47 | - |

(Band-rms numbers; ratios unaffected by the scale. **On the gate's peak scale** (`noise_scan` v2, 02:20): A2 2130/2128/2068, A1 2798/2826/2770,
B2 1892/1878/1812, **B1 740/839/808**, so B1 sits right on the 800 µV line across the three evening runs.) ⇒ **The A2 chip is the noise meter**: its floor holds within 2-7 % run to run, so a hardware change that moves
it by more than ~1.15x is real. B1 needs about 1.3x. **A1 and B2 floors swing 2.5-3.8x on their own**, driven
by the railing EMG, so they cannot judge any test. EMG high-band power moves 1.5x with the animal's state and is not a noise metric.
Baseline 1 has 3 "system-wide" detections (t 60, 61, 74 s), all driven by the A1/B2 floors and only 43-46 uV
on B1, so they are not light-switch-type events. Baseline 2 has none.

**5. Overnight scheduled through the recording console**: run `cfdf8ebde0c6`, owner andrea, batch `noise-tests`,
setting `eeg_emg`, ports A+B with splitters, 4 slots, keep_labels `A/1 A/2 A/33 A/34 B/1 B/2 B/33 B/34`.
**Start 2026-10-01 21:00:00 (ZT12, lights off), stop 2026-10-02 09:00:00 (ZT0)** = the whole 12 h dark phase. ⚠️ Stop later moved to **09:02** (see below).
🔴 **Mouse IDs were not given**: slots carry placeholders `POS-A1 POS-A2 POS-B1 POS-B2`, stated in the run note.
The NAS copy lands at `02_Data_Sleep/andrea/noise-tests/Baseline/20261001_POS-<slot>_B/` after the 09:00 stop
(QC bundle → strip → upload → verify, automatic). Rename once the IDs are known. The raw file on the rig keeps all channels.
Expect: A2 and B1 scoreable candidates; A1 and B2 EEG only (open EMG), so not scoreable under the strict rung 2.

**Start, verified (2026-10-01 21:00):** console started at 21:00:03 (4 s late, inside the 3 min grace), file
**`~/radix/data/allego_0__uid1001-21-00-07`**, R_ON at 1000 Hz. Console "growth confirmed" at 21:00:50.
Checked independently: 0 → 48.6 MB in 70 s (this includes the 30 s flush lag), then +16.2 MB in the next 45 s,
and the stream at 1.000x real time. 🔴 **A console run does not arm the hourly `recording-watchdog-cron.sh`**, so it
was armed by hand (`current-recording.txt` = the basename, `watchdog-lastsize.txt` removed). First armed check
21:05:04: `mode=R_ON size=145723392 ... OK growing`. The watchdog sends a "Recording has STOPPED" ntfy at 09:05
after the scheduled stop and then disarms itself. That message is expected.
The light timer is due to switch off at 21:00, in the first seconds of the file, so an all-chip event may sit
there. The timer spiked on only 2 of its 4 switchings in the 09-20/22 run.

### Mid-run check, 2026-10-01 23:42 (first 2.7-2.8 h, 21:00-23:46, dark phase)

Read from the LIVE file at the lowest CPU and disk priority (`nice 19`, `ionice -c3`), in 300 s chunks with the page cache
dropped and at most 0.9 GB of RAM, and the growth was checked before and after each pass. Scripts: `qc/allchip_scan_file.py`,
`qc/night_trend.py` (60 s every 15 min), `qc/night_spikes.py` (per 100 ms), `qc/night_events_plot.py`.
Figure 5 below (`qc/night_events_plot.py`; regenerated 10-02 with readable titles as `overnight_events_2134_2223_v3.png`).

![[2026-10-01-noise-fig5-overnight-port-A-events.png]]

**Figure 5.** The two 3-of-4-chip detections of the first hours (21:34:11 = 2044.5 s, 22:23:04 = 4977.5 s), 50 ms comb + 1-450 Hz. Left: the port A floors (A1, A2) wobble 100-200 uV, B1's floor is flat, B2's floor is busy on its own (open EMG). Right: A2's EMG shows the mouse moving. Local to port A and movement-linked, not injection.

- **Zero dropped samples**: 9,720,192 timestamps, every step exactly 1. That includes the period after about 23:30, when the
  Allego GUI froze (see below).
- **Mains steady all night**: EEG 60 Hz A1 15-17, A2 6-9, B1 8-13, B2 7-10 uV (band rms, mostly broadband EEG; the line itself, gate
  estimator: A1 ~20, A2 3-5, B1 6-8, B2 4-5 uV peak) in all 11 windows. A2 chip floor
  1516-1531 uV (±1 %), B1 455-589 uV. Ground contact is not drifting. The open EMGs stay at 3.44-3.53 mV.
- **No system-wide electrical event.** The all-chip scan found 2 detections (21:34:11, 22:23:04) at the 3-of-4-chip
  bar, but the waveforms show a small wobble of 100-200 uV, a few hundred ms long (the plot's 150 ms comb adds an echo, so part of that length is the filter), on the port A floors only (A1 + A2).
  **B1's floor is flat in both**, nothing appears on any EEG, and at 22:23 the A2 mouse was moving hard. So the events are
  local to port A and movement-linked, not injection. Over the night the clean floors hit A2 77x and B1 6x and **never in the same 100 ms**. ⚠️ Those were window counts with a 150 ms comb, which double-counts
  (code review); **re-counted as events (`qc/night_spikes.py` v2, 4.04 h): A2 41 events (10.1/h), B1 4 (1.0/h), overlap 0 (chance ≈ 0.00)**.
  A2 and A1 floor hits coincide at chance (7 vs 5.0 expected). No event at the file start, so the 21:00 light timer either switched
  before 21:00:07 or made no spike.
- **Within-mouse spikes are rare and not electrical**: EEG spikes (> 8 robust SD) A2 2.9/h, B1 0.7/h, A1 and B2 0.
  EEG+EMG in the same 100 ms: **A2 7 in 2.8 h, none on the other three**. ⚠️ Re-counted as events with the documented 50 ms comb (v2, 4.04 h):
  EEG spike events A1 2.2/h, A2 1.7/h, B1 0.2/h, B2 0.2/h; **EEG+EMG events A2 3 in 4 h, none elsewhere, none on any floor hit**. Same conclusion, fewer events; and **none of the 7 lines up with a floor hit**
  on its own chip or the other port, so they are the mouse's own (movement), not the rig. EMG "spikes" in the thousands
  per hour are ordinary muscle bursts on A2/B1 (and junk on the open A1/B2 EMGs), not noise.
- **Allego GUI froze around 23:30** (Andrea could not interact, though the traces kept moving). Two warnings flood
  `allegoserver.log` from 20:17 on, when the stream was restarted after the impedance block: about 54,500
  `resample_antialias ... using raw decimation` (the Monitor's Anti-Alias view mode) and about 5 per minute of `[HAL] unable to
  send to listener '0','1','2'`. The GUI renderer sat at 108 % CPU and 11-14 GB RSS, while allegoserver stayed at 0.23 GB / 4 %.
  Data unaffected (above). Left alone: app death may end the recording. `allego_mem_watch.sh` logs renderer RAM every 5 min
  and sends ntfy if available RAM < 3 GB; it falls back to 7.3 GB on its own by 23:43.

### Stop moved to 09:02, and the B1 floor caveat (2026-10-01 23:59)

> [!danger] 🔴 SCALE CORRECTION, 2026-10-02 01:45 (code review): the QC gate reads the line PEAK, these notes mostly gave the band RMS
> `FLOOR_MIN_HUM_UV` is applied in `core/criteria.py` to the **peak** amplitude of the 59-61 Hz line (10 s Hann epochs, median over
> epochs × floor sites). `noise_scan.py`, `floor_flicker.py`, `night_trend.py` and the pre-flight reported the **std of a 55-65 Hz band-pass**,
> an rms that is √2 smaller for a pure line. On quiet channels (EEG, good EMG) it is mostly broadband signal, not the line.
> **On the gate's scale** (`qc/gate_floor.py`, one 10 s epoch every 3 min, 21:00-01:00): floors **A1 2594, A2 2057, B1 742, B2 1820 µV**.
> B1's half-hour medians are 632-745, and it read **808 at 20:42** (baseline, just above 800) and 804 at 21:10. EEG line amplitude: A1 20,
> A2 3-5, B1 6-8, B2 4-5 µV peak. Consequences: B1 is still below 800 all night, so UNJUDGEABLE is still the likely verdict, but **by ~7 %, not ~38 %**.
> Its verdict flips with a 10 % drift. Against 2000 µV, B2 (1820) and B1 (742) carry EEG while A2 (2057) is above it. Ratios, CVs and correlations
> in these notes are unaffected by the scale. Every rms floor below should be read × √2. The pre-flight is fixed (`chip_floor` now uses the gate's estimator).


- **Andrea: the recording started right after the lights went off** (so the 21:00 switch-off is not in the file). At
  her request the scheduled stop was moved **09:00 → 09:02** so the 09:00 lights-ON switching is inside the file
  (the timer has fired up to 7 s early, `08:59:53` on 09-22). The console has no API to edit a RECORDING run's
  stop (`/schedule` only takes DRAFT/SCHEDULED), so it was done with the store's own `RunStore.transition()` as a
  same-state RECORDING → RECORDING update with `scheduled_stop`, which leaves an audit event on the run. DB backed up
  first with SQLite's backup API (`~/.local/state/eeg-recorder/runs.db.bak-20261002-stop0902`). The console API then
  reported `2026-10-02T09:02:00+09:00`, and the scheduler re-reads RECORDING runs from the DB every 5 s.
- 🔴 **B1's chip floor reads 455-599 uV (band rms; 632-808 on the gate's peak scale, see the correction above) all night, under `FLOOR_MIN_HUM_UV` = 800.** The threshold comment gives a grounded chip's
  floor as 1138-5609 uV and a floating one as 82-466 uV. B1 sits in the gap, just above the floating population, while
  A1 2000, A2 1520 and B2 1350 sit in the grounded one. ⇒ **expect the automatic QC to grade B1 UNJUDGEABLE at rung 2**, and
  B1's low hum cannot be read as proof of good contact, because a chip with a weak ground also reads quiet. B1's EEG
  does carry biology (1/f, theta). Rig-side suspect after the run: the B1 GND path (slip-ring GND wire into the B1
  adapter-board socket). That board was taken off and put back at 16:48 today for Entry 4; B2's was too, and B2 reads
  grounded. Position B1 also had a ground decay on 2026-08-27/28 (825 → 469 uV), with a different mouse and tether.
- Hum on the clean mice: present at the rig's normal residual and steady. The only notable one is **A2's EMG at
  14-20 uV of 60 Hz**, about the size of its quiet muscle tone. Stage 3's `emg_rms` (10-300 Hz band-pass, no mains
  removal) includes it, which compresses A2's EMG range a little. B1 EMG 60 Hz 4-10 uV.

- **Andrea, 2026-10-02 00:10: A2 and B1 are the good mice.** That matches the channels: the working EMGs are `A/34`
  (A2) and `B/2` (B1), and the open ones are `A/2` (A1) and `B/34` (B2). Port B's orientation was already proven by the 09-30 hand test
  on B1. If Andrea's call comes from her own knowledge of the mice, it also confirms port A's splitter orientation
  (physical A2 = `A/33…`), so no touch test is needed. B1's caveat is the CHIP floor (QC), not the mouse.

### QC gate re-think: why B1 would be UNJUDGEABLE, and what to do (proposal 2026-10-02, NOT applied)

**What the gate is for.** `FLOOR_MIN_HUM_UV = 800` (2026-08-26) asks whether the chip's wire-free inputs are a valid
negative control. It was built to stop a hardware fault being published as a dead mouse (B1/HLBSSD13, floor 246 uV, read as
FAIL for days), so it answers UNJUDGEABLE, not FAIL. That fail-safe direction is right and should stay.

**Why it misfires now.** It treats 60 Hz pickup on open inputs as a stand-in for "has a ground". That pickup also
depends on antenna geometry, and this series changed the geometry. Measured in the current configuration:
- **No animal, no ground**: empty headstages read **1200-3000 uV band rms, ~1750-4300 on the gate's scale** (Entry 4: socket pads 2574-3039, bare pads 1235-1759 rms) ⇒
  the gate would call them GROUNDED.
- **Working animal**: B1 reads **632-745 uV on the gate's scale** all night (455-599 band rms), while its EEG is 1/f (slope -1.43 to -1.76), at normal scale
  (53-90 uV, not the 3-4x shrink of the old weak-ground cases), and its EMG tracks behaviour (p95/p5 6.5) ⇒ the gate calls it UNGROUNDED.
- The 800 line sat in an "empty gap" (grounded 1138-5609, floating 82-466, all pre-09-30). B1 is the first chip
  inside the gap. By the code's own rule for the sister slope guard, that is a reason to re-measure, not to move the number until B1 passes.
- The pending **2000 uV proposal is falsified** here: on the gate's scale B2 (1820) and B1 (742) carry EEG. A2 is 2057, above the line.
- Bias risk: a geometry-dependent gate excludes mice by cage position or wiring rather than by signal. That is a
  selection bias in the scored sample.

**Proposal (decision for Andrea; nothing changed in code):**
1. **Tonight: no change.** The 09:02 QC runs on the current rules, so B1 goes UNJUDGEABLE. The raw file keeps every channel,
   and re-carding later has precedent (11 cards on 2026-09-26).
2. **Re-derive the gate in today's geometry with dummy loads** (Next steps #2): on each headstage, the same resistor load with
   GND connected vs GND lifted, and measure both floor populations. If they separate, set the line in the new gap and tie it
   to a recorded rig-configuration id. Any geometry change (tape, boards, tethers, cage moves) means re-measuring. If they do
   not separate, the floor cannot test ground in this rig, and the gate must be replaced rather than retuned.
3. **Pre-register an independent ground-evidence route**: a low-floor chip becomes judgeable when its EMG proves itself by
   behaviour-tracking amplitude (envelope range plus sleep/wake or light/dark dependence). The rule is fixed on PAST data before
   B1's result is looked at, and it must reject open EMGs (tonight A/2 and B/34: p95/p5 1.01-1.02), wire-free inputs and empty
   headstages in the falsification suite.
4. **Tomorrow: a shadow verdict for B1** (gate bypassed, labelled diagnostic-only, never published as the verdict) beside
   the official UNJUDGEABLE, so the decision is informed but not tuned.
5. Rig side, independent of all this: B1 reads 3x below its neighbours in the same geometry, so check the B1 GND path anyway.

### Overnight investigation, 2026-10-02 00:10-01:00 (light reads of the live file, nice/ionice idle)

**B1's low floor: steady, not intermittent** (`qc/floor_flicker.py`, 10 s windows, 21:00-00:35, 1261 windows;
CSV `~/radix/noise-tests/2026-10-01/floor_flicker_uid1001-21-00-07_to0010.csv`):

| chip | floor median | CV | p95/p5 | max/min | r(floor, own EMG activity) |
|---|---|---|---|---|---|
| A1 | 2057 uV | 1.5 % | 1.03 | 1.25 | -0.34 |
| A2 | 1524 uV | **0.4 %** | 1.01 | 1.04 | -0.02 |
| B1 | **495 uV** | 6.8 % | 1.25 | 1.35 | **-0.08** |
| B2 | 1366 uV | 1.7 % | 1.06 | 1.11 | -0.27 |

- No intermittent-contact signature: B1 does not flicker and does not follow its own movement (r -0.08). Half-hour medians
  went 555 → 540 → 493 → 468 → 463 → 494 → 499 → 490 uV, a 17 % fall over the first 2 h and then flat. That is not the slow
  slide of 2026-08-27 (825 → 469 over 20 h).
- Oddity, unexplained: A1, A2 and B2 floors rise and fall together (r +0.27 to +0.32), and **B1's moves against them (r -0.21 to -0.34)**.
- 60 Hz lock-in phase vs A2 (`qc/floor_phase.py`, 3 windows). ~~chip medians A1 -35 deg, A2 +11, B1 +47 to +58, B2 ~0; "B1 is NOT
  ~180 deg"~~ **RETRACTED 01:45**: those were linear medians of wrapped angles (code review). With circular statistics the resultant
  length is **R 0.11-0.24 on every chip**, so the sites' phases are spread almost evenly around the circle, no chip has a defined floor
  phase, and the test cannot support or reject "reference-dominated". Uninformative.

**No non-mains injection anywhere on the clean mice** (`qc/line_scan.py`, `qc/line_track.py`, 0.1 Hz resolution):
- A2 and B1 EEG/EMG carry **no narrow line except 60 Hz itself**, in both windows checked (21:30, 23:30).
- Every line on the floors is mains: harmonics 1-8, plus **high harmonics up to at least the 39th (2340 Hz) folded back
  below 500 Hz**. They are identified by their wander: the k-th harmonic carries k times the mains drift. The 39th folds to ~340 Hz
  and wanders 339.7-340.3 Hz all night (100-2000x on the floors), the 37th to ~220, the 20th to 200, the 19th to 140. So the pickup on the open
  inputs has very sharp edges (switching-type current pulses), and the chip's 475 Hz anti-alias filter does not remove it on those
  high-impedance inputs. It does not reach the connected mice (A2/B1 ≤ 2-4x at those bins, i.e. no line).
- The only non-mains lines (46, 74, 106, 134, 286, 434 Hz) are on **B2's open EMG**, which is on the rail ~14 % of the
  time. Most likely clipping intermodulation of the folded harmonics; not seen on any other channel.
- First line-scan pass misclassified the folded harmonics as "OTHER" (it assumed exactly 60.000 Hz); fixed with a
  drift tolerance that grows with harmonic order (0.15 + 0.012 k Hz).

### ⭐ B1's low floor is a few input PAIRS collapsing, not a weak ground (2026-10-02 01:30)

`qc/site_floor_compare.py` (gate scale, per site, 120 s each). B1's 14 wire-free sites across today's conditions:

| B1 site | /3 | /4 | /5 | **/6** | /7 | /8 | /9 | **/10** | **/11** | /12 | /13 | **/14** | **/15** | **/16** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:29 no mice, board on (before the boards-off test) | 286 | 4996 | 4788 | **2853** | 4274 | 1093 | 1422 | **2269** | **2884** | 5285 | 5795 | **717** | **899** | **671** |
| 16:48 board OFF | 245 | 794 | 248 | 289 | 109 | 115 | 101 | 312 | 578 | 269 | 965 | 295 | 332 | 114 |
| 19:50 mice on, board back on | 382 | 6132 | 2814 | **105** | 3245 | 440 | 759 | **757** | **744** | 5678 | 1386 | **26** | **192** | **203** |
| 23:30 overnight | 388 | 6218 | 5640 | **103** | 3211 | 2275 | 936 | **432** | **468** | 6179 | 983 | **14** | **146** | **146** |

![[2026-10-02-noise-figC-B1-site-floors.png]]

**Figure C.** Per-input floors at 16:29 (no mice, boards on) vs after the B boards were refitted AND the mice connected (19:50, overnight median). Inputs dropping 5x or more: B1 6 of 14 (/6 /10 /11 /13 /14 /15), B2 0 (same handling), A2 1 (/37; port A, board not touched), A1 0. Median input ratio B1 0.45, A2 and B2 0.72. Connecting a mouse moves an input or two on any chip, but B1 loses many inputs and keeps others, which is site-specific, not a weak ground. Refit and mice changed together, so the data cannot separate them. Made by `eeg-emg-analysis/qc/noise_figures_2026_10_02.py`, data in `~/radix/noise-tests/2026-10-02/figdata/`.

- After the board went back on and the mice were connected, **sites /6, /14, /15, /16 dropped 5-50x** (to 14-146 µV) and /10, /11 dropped
  5x, while /4, /5, /7, /12 are unchanged or higher. It is stable between 19:50 and 23:30. **A weak or absent ground scales the WHOLE chip**
  ([[weak-chip-ground-vs-open-electrode]]: "scales the whole chip down 3-4x"). This is site-specific.
- B2's board went through the same off/on handling and keeps its 16:29 pattern within about 0.5-2x per site. Per-site ratio 23:30 / 16:29,
  sites below x0.2: **A1 0, A2 1 (/37, x0.11), B1 6, B2 0**; chip medians x0.98, x0.72, **x0.44**, x0.75. Connecting a mouse moves a site
  or two on any chip (A2's board was never re-seated), but B1's six collapsed pairs are unique to B1.
- A site is the DIFFERENCE of two adjacent pads, so ~14 µV at /14 means pads 26/27 now see the same 60 Hz potential: a bridge between
  them, or both pressed against or coupled to the same conductor. Candidates, **rig side only**: the B1 adapter board not seated as before,
  a bent socket pin or solder/flux bridge, a slip-ring wire or the (floating) **foil touching the pad area** (the vault rule: the shield must
  not touch anything inside it). Not separable from the data: no recording exists with the board back on and no mice.
- **Why it matters for QC:** the gate's floor is the median of these 14 values. B1's sorted values have a gap in the middle (…468 | 936…), so
  the median sits in the gap and swings ~2x with tiny changes, which is why B1 hovers at 632-839 around the 800 line. The verdict is being
  set by the pickup of a few pads, not by the animal's ground.
- **Morning check (Andrea, rig side, after 09:02):** look at the B1 adapter board seating and the pad area under the foil (pads ~10-11 and
  ~18-31) for contact with foil, wires or bridges. Then, if possible, a 3 min recording before and after reseating or clearing.

## Entry 7: the overnight's outcome, sleep staging, and the light-phase run (2026-10-02 morning)

> [!info] Mouse identities for the 10-01/10-02 runs (Andrea, 2026-10-02; not used for experiments)
> A1: B6/J BomTac female, DOB 2026-04-12, surgery ~July (23 g), tethered 2026-10-01 (25.2 g). A2: **HLBWSL30** (W-SL; registry sheet
> `HLB_SOD1_Intake_Monitoring_SDSLNANO`). B1: **HLBSSD20** (S-SD; same sheet). B2: same strain, sex and DOB as A1. NAS folders keep the
> `POS-<slot>` placeholders (not re-filed: these recordings are noise-series tests, not experimental data).

**Overnight run `cfdf8ebde0c6` (`allego_0__uid1001-21-00-07`)**: stopped 09:02:04 (2 s late), **12.032 h, every one of 43,314,688
timestamp steps == 1 (zero dropped samples)**. The **lights-ON is in the file**: one all-chip event at **08:59:51** (the timer fires ~9 s early,
as on 09-22; floors ×84/86/20/9 on A1/A2/B1/B2, EEG peaks 83-183 µV). Post-processing: QC 09:03, strip bit-exact 09:05, per-mouse export, **upload
verified 09:14:47** → `02_Data_Sleep/andrea/noise-tests/Baseline/20261001_POS-<slot>_B/`.

![[2026-10-02-noise-figB-lights-on-event.png]]

**Figure B.** The lights-ON at 08:59:51.0 on the file clock, the night's only event above 5x on every chip's floor at once (⚠️ corrected 2026-10-02 23:30: an earlier caption said the transient came 0.25 s after the timer contact. That was the fraction of a second lost to the file-name clock, not a measured delay; three smaller events reached both clean floors, see Entry 9): 3.3 and 4.1 mV on the A1 and A2 floors, 0.5 and 0.8 mV on B1 and B2. On the animals it is a step on B1's EMG (~0.6 mV) at the same instant; on the EEGs it does not stand out from the ongoing EEG. About 0.3 s later the A2, B1 and A1 EEGs all swing together while the floors are flat again, possibly the mice's response to the light (not tested). The EMG bursts 5-10 s later are the mice waking up. B2's floor bursts before the event are its own chip (open EMG, Entry 5). Made by `eeg-emg-analysis/qc/noise_figures_2026_10_02.py`, data in `~/radix/noise-tests/2026-10-02/figdata/`.

**Official QC (rung 2): all four UNJUDGEABLE, so rung 3 is blocked for every mouse.**
- B1: hum gate, floor 702 µV < 800 (as predicted, by ~12 %).
- A1, A2, B2: the contaminated-floor guard: floor slope thresholds -3.24, **-2.54 (A2)**, -3.44, steeper than -1.90. Even the "clean" A2
  chip's wire-free inputs carry enough low-frequency signal in this geometry to fail the "empty floor" test. Both floor guards misfire with the
  current wiring (audit C1).

![[2026-10-02-noise-figD-gate-floor-vs-config.png]]

**Figure D.** The chip floor (gate scale) of every recording in the series against the 800 uV gate. Empty headstages (squares: no mouse, no ground) read "grounded"; B1 with a working mouse (red filled) sits on the line: 692, 834, 807 and 707 uV in the four recordings with mice, and the official whole-night value was 702, so UNJUDGEABLE. Connecting the mice lowered every chip's floor (green band). The floor follows the wiring geometry, so in this rig it cannot certify a ground (audit C1). Made by `eeg-emg-analysis/qc/noise_figures_2026_10_02.py`, data in `~/radix/noise-tests/2026-10-02/figdata/`.

**Diagnostic sleep staging (labelled diagnostic, NOT a result)**: stages 1-3 of the pipeline run unchanged, outputs under
`~/radix/noise-tests/2026-10-02/diag-*`, stage 2 with `--all-verdicts`. Stage 1: **A2 CLEAN 99.97 %, B1 CLEAN 100 %** (12.03 h usable, longest
blocks 336 and 722 min); A1/B2 OPEN (EMG). (Stage 1's OPEN reason prints the EEG's 60 Hz, the same misleading-reason bug as the pre-flight had;
not fixed, it is in `pipeline/`.) Stage 3, dark phase 21:00-09:02: **B1 SCOREABLE, r@1min 0.304, wake 29.5 %**; **A2 REJECT, r@1min 0.19,
wake 18.6 %**. Both wake shares look low for a dark phase.

### ⭐⭐ Mains in the EMG corrupts sleep staging (2026-10-02 09:20)
Stage 3 stages WAKE by an Otsu split of log EMG rms over 10-124 Hz (stage 2 stores 250 Hz). That band **includes the 60 Hz line**, and A2's EMG
carries 13-28 µV of it, about its quiet muscle tone. Test: stage 3 UNCHANGED, the EMG notched at 60 and 120 Hz (Q 30) in memory only
(`qc/emg_mains_staging_test.py`; official stage-2 files symlinked, outputs in the scratch folder; the unchanged run reproduces every official verdict):

| set | before (official) | EMG mains notched |
|---|---|---|
| 10-01 overnight A2 | REJECT, r@1min 0.19, wake 18.6 % | **SCOREABLE, 0.323, 29.7 %** |
| 10-01 overnight B1 | SCOREABLE, 0.304, 29.5 % | SCOREABLE, 0.308, 30.4 % (its line is only 4-5 µV) |
| W-SL 09-17 light phase, 7 mice | 5 scoreable; r 0.10-0.70; wake 1.9-62.3 % | **7/7 scoreable; r 0.60-0.68; wake 22.5-30.0 %** |
| W-SL 09-10 light phase, 6 mice | 3 scoreable; r 0.23-0.44; wake 7.7-19.2 % | **6/6 scoreable; r 0.59-0.69; wake 23.1-35.8 %** |

![[2026-10-02-noise-figE-emg-mains-staging-effect.png]]

**Figure E.** Stage 3 with nothing changed except 60/120 Hz notched out of the EMG, 15 animal-recordings (10-01 night red, 09-17 light blue, 09-10 light green). Left: r@1min (state persistence), dashed = the scoreable bar 0.30. Right: WAKE %. Diagnostic only, not adopted. `qc/emg_mains_staging_test.py`, outputs `~/radix/noise-tests/2026-10-02/emg-mains-test/`.

- Light-phase wake converges on the 22-30 % this lab has seen before; the implausible 1.9 %, 7.7 %, 52 % and 62 % disappear.
- **Negative control passes**: with the notched EMG's 4 s epochs SHUFFLED in time (muscle-tone persistence destroyed, EEG kept), r@1min collapses
  to -0.004..0.009 and all three animals tested are REJECTED. The notch does not manufacture persistence.
- Not yet tested: dark-phase and full-day sets, and the other ~10 GB of stage-2 files (scheduled after 21:02, when nothing records), plus the
  falsification suite. **Adopting it is a pre-registered pipeline change that re-scores published numbers (wake %, r@1min): Andrea's decision.**

**Coverage of the overnight review, stated plainly (asked 2026-10-02):** integrity (every timestamp), the console's QC and the diagnostic
staging covered the WHOLE night. The noise scans at full resolution (all-chip events, floor/animal spikes, narrow lines, flicker) covered only
**21:00-01:05**, plus **08:50-09:02** for the lights-ON. **01:05-08:50 had no full-resolution injection scan.** It is scheduled after 21:02, when
nothing records. Done at 09:40 instead, sampled and light (`qc/gate_floor.py` every 3 min, `qc/night_trend.py` every 15 min, whole night): EEG
60 Hz line A2 2.2-5.0, B1 5.5-9.4, B2 3.1-4.9, A1 17-22 µV peak, flat 21:00-09:00. Floors A2 1979-2159, **B1 577-804** (half-hour medians
623-787, whole-night median 707), A1 2559-2954, B2 1810-2017. Clean-floor broadband steady (A2 13-24, B1 7-9 µV). No slow ground decay, no hum drift.

![[2026-10-02-noise-figA-overnight-trend.png]]

**Figure A.** The whole night, sampled (one 10 s epoch every 3 min, the gate's estimator). Top: chip floors; B1 under the 800 uV gate in 95 % of epochs (half-hour medians 639-798), A1, A2, B2 flat at 1.8-2.9 mV. Middle: EEG 60 Hz line, A2 2.0-4.9, B2 2.7-5.5, B1 4.9-8.9, A1 18.5-21.8 uV peak (5th-95th percentile). Bottom: EMG 60 Hz line; A2's 13-26 uV (26 in the first hour, 17 later) is about the size of its quiet muscle tone, which is why it corrupts staging (C3); B1 3.6-5.7 uV; A1 and B2 are open inputs at 4.5-5 mV. Made by `eeg-emg-analysis/qc/noise_figures_2026_10_02.py`, data in `~/radix/noise-tests/2026-10-02/figdata/`.

**Light-phase run `8f84e3e62af6` (`allego_0__uid1002-09-16-58`)**, started 09:16:58 (ZT0 + 17 min), stop 21:02 (keeps the 21:00 lights-OFF).
Same 4 mice, same placeholders. **Allego GUI restarted cleanly first** (overnight renderer 238 % CPU / 9.7 GB → 0.3 GB fresh); Monitor in
`Spikes` mode, so 0 Anti-Alias warnings. ⚠️ `allegoserver` was NOT restarted: it is the same process (up 16 h 50 min, parent `systemd --user`), so
the `[HAL] unable to send to listener` warnings (~5/min) continue; the stream runs at 0.998x and the file grows. Watchdog armed by hand,
RAM watcher on the new renderer (`~/radix/noise-tests/2026-10-02/allego_mem_watch.log`).

## Entry 8: at the rig during the light-phase run (2026-10-02 15:35-16:35)

> [!info] All interventions with times, figures F-H and the marker file: [[2026-10-02-light-phase-run-rig-session]]

Andrea at the rig, the light-phase run `8f84e3e62af6` recording (so no separate files, no Allego restarts; T1 isolator waits).
No wire was at hand, so the foil bonding (T2) did not happen. What was measured, from the live file (gate estimator, idle priority):
- **Baseline 15:30-15:35** (`noise_scan`, `~/radix/noise-tests/2026-10-02/trials/A0_live_1535.json`): floor 60 Hz A1 2889, A2 2087,
  B2 1904 µV; A2 EMG 60 Hz 19.0, A2 EEG 3.1 µV peak; open EMGs 4.7-4.8 mV.
- ⭐ **B1's floor creeps up through the light phase with nothing touched**: half-hour medians 732 (09:16), 840, 815, 826, 867, 857,
  838, 991, 893, 911, **1028 (14:16)**, 955, 947 µV, while A1, A2, B2 hold within ±3 %. B1 sat at 702 (official) / 707 overnight, so
  **the same mouse on the same hardware may read UNJUDGEABLE at night and "grounded" (>800) in the light phase.** Check the official
  light-phase QC at 21:09. If it flips, that is direct evidence for audit C1 (the gate is not a property of the ground).
- **AC volts, foil ↔ chassis lug (Harden 661002, `V~` 200): 0.0 every time.** Inconclusive: 0.1 V resolution, and the meter loads the foil.
- ⭐ **A person at the rig moves the floors more than any untouched run does.** During the probe contact (~15:50:50-15:51:25):
  A1 -8 %, B1 and B2 -5 to -10 %, A2 +20 % for one 10 s epoch, A2 EMG 60 Hz 21 → 15-16 µV. Afterwards A2 settled about 6 % higher
  relative to its neighbours (A2/A1 0.731 → 0.772, A2/B2 1.09 → 1.17), as if its foil had moved. The ratio A2/A1 is a good
  common-mode-free meter: 0.729-0.735 for the 10 min before. **Protocol change: step away to the same spot before every block** (plan updated).
- For the light-phase staging: treat **15:35 to Andrea's departure** as disturbed.

### ⭐ Presence / hand / wireless-receiver test (2026-10-02 16:00-16:08, Andrea's log)
16:00-16:03 absent · **16:03 standing 50 cm in front of the headstages, hand brought close to each (no touching)** · 16:04 absent ·
**16:05 in front, waving hands** · **16:06 waving a powered custom wireless EEG/EMG receiver (4 antennas, on the Dell PC, no transmitter
active)** near the headstages · 16:07 after. Script `qc/presence_test_2026_10_02.py` (1 s steps; non-mains bands drop every bin within
2 Hz of a multiple of 20 Hz). Most extreme 1 s value in each window, relative to the absent-before median.

> [!note] Re-run 2026-10-02 23:00 after the first code review
> Three fixes: the time origin now comes from the file's `status.start_time` (+0.153 s), the non-mains bands drop ±2 bins instead
> of ±1 (±1 leaked mains), and the read stops at 16:09.
> - Conclusions unchanged.
> - Single-second extremes move with the 1 s grid, e.g. B1 x0.61 → x0.51.
> - The receiver-vs-waving comparison now also flags B1's EEG at 3.25 Hz (x5) and 9 Hz (x4). Those are delta/theta, so B1's brain state changed between the two minutes; it is not radio pickup.

| channel | hand near each headstage | waving hands | wireless receiver |
|---|---|---|---|
| A1 / A2 / B1 / B2 floor, 60 Hz | **x0.58 / x0.69 / x0.51 / x0.97** (first run: x0.58 / x0.72 / x0.61 / x0.95) | x0.69 / x0.88 / x0.79 / x0.95 | x0.98 / x0.99 / x0.97 / x1.01 (nothing) |
| floor non-mains 100-450 Hz, max | A1 x39, A2 x16, B2 x61 (B1 x1.1) | A1 x18, A2 x16, B2 x94 | x1.0-2.7 (as when absent) |
| open EMGs A/2, B/34 (implant-side open) | 60 Hz x1.02 / x1.05 | **60 Hz x1.28** / x1.06, HF x31 / x19 | nothing (one 88.75 Hz bin x3 on A/2, see below) |
| **the mice's EEG and EMG (A2, B1)** | within the spread of the empty-room minutes | same | same |

![[2026-10-02-noise-figF-presence-test.png]]

**Figure F.** The presence test at 1 s resolution. Shaded: hand near each headstage (orange), waving hands (green), waving the wireless
receiver (red). Floors dip for the seconds a hand is near (top), the open EMGs rise while waving (bottom), and the mice's own 60 Hz line
(second panel) does not move. EMG bursts in the third panel also happen in the empty-room minutes: they are the mice.

- **A person or a hand near the headstages is detectable on the wire-free floors and the open inputs, NOT on the connected EEG/EMG.**
  A connected leg ties the input to the animal through kΩ-MΩ, and the chip measures the DIFFERENCE between two such legs, so a nearby
  field puts almost the same voltage on both and it cancels. The floors are GΩ open pads: any nearby charge or conductor changes their pickup.
- Standing still at 50 cm between the hand moments: no change. The dips last only the seconds the hand is near.
- **The wireless receiver showed nothing** on any floor, any mouse channel, or B2's open EMG. The only trace is one Welch bin at
  **88.75 Hz on A1's open EMG, x2.9 its neighbours** (the other windows x0.5-1.9). Weak, and that input rails 13 % of the time (spurious
  products), so not convincing. Andrea had seen it on inputs WITHOUT mice: open long wires act as antennas, terminated legs do not.
- **The 15:51 changes were the meter at the headstages** (hands right at them), the same effect as the hand test, not presence as such.
### ⭐ Meter-probe repeat: hover vs touch on A2's foil (2026-10-02 16:22-16:23)
Black probe fixed on the XDAQ chassis GND lug, meter ON (`V~` 200), red tip alternating ~10 s hover (1 cm) / ~10 s light touch on
A2's foil, hand in the same place. Per 1 s, gate-style 60 Hz line on the floors:
- **Every touch raised A2's floor only**: hover 2066-2105 µV → touch 2600-2920 µV (**+25 to +40 %**; median over the four contacts x1.22 on the re-run), four clean on/off cycles
  (touches ~16:22:16-23, :35-40, :49-56, 16:23:05-12). A1 (same port), B1 and B2 did not move at all on the touches.
- The mouse's channels did not follow: A2 EMG 60 Hz touch/hover x1.05, A1 EEG x1.03, open A/2 x1.00, B1 EMG x1.03 (A2 EEG x1.26 on
  3 µV, inside its normal 1 s scatter).
- Just having the hand and body there lowered every floor ~3-7 % (A1 2880 → 2825, B1 955 → 870, B2 1900 → 1815). They stepped back
  up at 16:23:13, when the hand left. After the series, A2 sat ~5 % higher than before (A2/A1 0.751 → 0.760), the same small
  lasting shift as at 15:51: touching the foil nudges it.
- **Reading:** the red lead (~1 m of wire in the room's field) connected to the foil acts as an ANTENNA feeding mains into it. The
  meter's 10 MΩ to the chassis is far too weak to pin the foil to earth. So this is NOT a preview of T2 (a real low-ohm bond): it
  shows the foil couples straight into its own chip's open pads, and that **a wire on the foil that is not solidly grounded makes it worse.**
- ✅ **Meter OFF repeat (16:27:01-16:27:11, red tip on A2's foil, black still on the chassis):** A2 floor 2266 → **4550-4800 µV
  (x2.1; median x2.09 on the re-run)**, and **A2's EMG 60 Hz 29.5 → 33.5-35.4 µV (x1.17; x1.15 re-run)** for exactly those seconds (the first time a mouse channel followed).
  Other chips unchanged. Ordering: floating lead (x2.1) > lead with 10 MΩ to chassis (x1.25-1.4) > foil alone. **The lead is an
  antenna onto the foil, the foil's potential reaches the connected EMG of its own mouse, and a firmer path to earth lowers it**,
  which is what T2 (a solid low-ohm bond) should test. Rule: never leave a loose wire or probe touching a headstage foil.
- **Was the EMG rise the mouse moving? No** (Andrea's question; 1 s spectra of A/34). During the meter-OFF touch the EMG's 60 Hz line
  went x1.16 while its muscle band (100-450 Hz non-mains) did NOT rise: x0.83 (5.4 → 4.5 µV) on the corrected re-run. (⚠️ The first
  version said x0.42 and "the bins beside 60 Hz x0.48": its ±1-bin exclusion let mains leak into the band, review 2026-10-02.) The mouse
  did not get busier while the line got bigger. The ADDED 60 Hz component kept the same phase every second (consistency R = 0.97 over 9 s) and a fixed angle to the
  floor pad's added pickup (-104°, IQR -105..-99), which random muscle activity cannot do. Caveat: one 9 s event in one mouse; the meter-ON
  touches were too weak to say (x1.05, R = 0.37). The floor jumps are not biology anyway (no animal on those pads). T2 will repeat it.

- **For the trials:** the floors are the noise meters, so during a block keep hands away from the headstages and do not move near the
  rig (plan updated). For the mice's data and the staging, an experimenter in the room is a behavioural disturbance (they may wake), not an electrical one.

## Entry 9: light-phase stop, official QC, full-resolution scans of both runs (2026-10-02 21:02-21:45)

**Stop, verified.** Console run `8f84e3e62af6` stopped 21:02:04 (scheduled, 3 s late, `R_ON → R_OFF`), QC 21:02:52, strip
verified bit-exact 21:04, 4 per-mouse CSVs 21:07, **uploaded and verified (sha256 both ends) → DONE 21:11:30**. File
`allego_0__uid1002-09-16-58`: **11.751 h** (42,304,256 samples), **timestamp steps all == 1** (zero dropped samples). Watchdog
saw `R_OFF` at 21:05 and disarmed itself.

**Lights-OFF is in the file, at 21:01:11.5, but below the all-chip bar**: floors A1 x3.8, A2 x4.4, B2 x5.1, B1 x1.2 (bar
x5 on 3 of 4). Timing matches 09-21's lights-OFF (21:01:08); the timer runs ~70 s late at OFF and ~9 s early at ON.

**Official QC flipped B1.** Same mouse, same hardware, nothing touched between the runs:

| chip | gate floor overnight → light (µV) | rung 2 overnight | rung 2 light phase |
|---|---|---|---|
| A1 | 2590 → 2591 | UNJUDGEABLE (slope −3.24) | UNJUDGEABLE (−3.19) |
| A2 | 2061 → 2117 | UNJUDGEABLE (slope −2.54) | UNJUDGEABLE (−2.39) |
| **B1** | **702 → 971** | **UNJUDGEABLE (< 800)** | **PASS, 93.7 % usable, longest block 47.3 min** |
| B2 | 1767 → 1748 | UNJUDGEABLE (slope −3.44) | UNJUDGEABLE (−3.38) |

The gate's verdict on B1 followed a slow drift of its pickup through the day (Fig H), not a change in its ground. Audit C1 is now
confirmed by the official pipeline itself.

**Diagnostic stages 1-3 on the light-phase file** (as for the overnight, outputs `~/radix/noise-tests/2026-10-02/diag-processed/2026-10-02`,
notch test `diag-emgtest-lightphase/`):

| mouse | as published | EMG notched 60/120 Hz |
|---|---|---|
| A2 | REJECT, r@1min 0.290, wake 11.7 % | **SCOREABLE, 0.440, wake 21.7 %** |
| B1 | SCOREABLE, 0.407, wake 17.7 % | SCOREABLE, 0.426, wake 18.9 % |
| A1, B2 | REJECT (EMG open) | REJECT |

A2 repeats the overnight (0.19 → 0.323): its EMG mains, not the mouse, sinks it.

**Notch test over every `~/eeg-processed` day folder** (100 animal-recordings, 21 folders, idle priority, 9 min). The unnotched run
reproduces **99/99 official verdicts** (one has no official summary). **SCOREABLE 44 → 69: 27 up, 2 down.** Among the 42 scoreable both
ways r@1min changes by a median +0.027 (−0.070 to +0.279). The 2 that drop fail a physiology check after the notch, not r:
**07-31 C2** (0.708 → 0.553, `nrem_largest_amplitude`; one of the only two old real-sleep recordings) and 08-19 C1 (`nrem_has_most_delta`,
`nrem_largest_amplitude`). Some notched WAKE % are high (up to 72-88 % in dark sets). The epoch-shuffle negative control was NOT re-run at
this scale. Still diagnostic, still not adopted: it would re-score published numbers.

![[2026-10-02-noise-figK-emg-notch-all-days.png]]

**Figure K.** Every animal-recording in `~/eeg-processed`, stage 3 as published vs with the EMG's 60/120 Hz notched. Left r@1min (bar 0.30),
right WAKE %. Orange = REJECT → SCOREABLE (27), red = SCOREABLE → REJECT (2, both on a physiology check). `qc/fullscan_figures_2026_10_02.py`.

**Full-resolution scans of both whole files.**

> [!warning] Corrected 2026-10-02 23:30 after the second code review
> The first version of this block came from `allchip_scan_file.py` v3, and its "all-chip" counts were wrong in both
> directions. The vote let a port-local disturbance plus one noisy chip pass. The 8-notch IIR chain rang ahead of sharp
> transients, and the chance levels used whole-file rates. The tool was rewritten:
> - 50 ms comb;
> - contamination decided once per file;
> - **both ports required**;
> - each event reported at its peak;
> - per-chunk circular-shift chance.
>
> Positive control: NOISE02 gives all 4 switch flips. Logs and CSVs are in `~/radix/noise-tests/2026-10-02/fullscans-v2/`.
> The superseded numbers are kept at the end of this callout.

- **Overnight, all 12.03 h: 4 system-wide events, chance 0.01** (local null: the ports shifted 2-30 s against each other).
  - The lights-ON at 08:59:51.0.
  - Three smaller events that reached **both clean floors (A2 and B1, different ports)**: 01:59:56.5, 07:27:42.5, 08:41:13.8.
  - Their cause is unknown: no video, and building loads at night are possible. So 01:05-08:50 was NOT silent.
  - A2-B1 floor coincidences: 4, chance 0.06 (per 30 s stratum).
- **Light phase, all 11.75 h: 13 system-wide events.**
  - 10 fall inside Andrea's visit, which **began at 15:19:33 by the data** (we had 15:35), at the probe and meter tests. Their chance is 2.58 there because both ports were busy, so most are co-activity, not one building transient.
  - Outside the visit: **17:10:08** (all 4 chips x61-115, the strongest of the day), **18:12:11** (B2 x108, A2 x38, B1 x12) and **20:56:36** (A2 x6, B1 x12), against a chance of 0.03. All three are real and unexplained.
  - The lights-OFF at 21:01:11.5 stays under the bar, and the air showers left nothing.
  - A2-B1 coincidences: 10, chance 8.7 per 30 s stratum (not 0.08): the floors were busy together during the visit.
- **Within-mouse EEG+EMG events** (same 100 ms, > 8 robust SD): A2 0.7/h in both runs, B1 0.0 → 0.3/h, A1/B2 ≤ 0.1/h. Of A2's events, 1 of 9 (overnight) and 4 of 8 (light) touch its own floor; the light ones are the rig session. So the mice's own spikes stay their own.
- EMG events/h are 300-675 on every mouse: muscle, as expected.

Superseded (v3 tool):
- overnight "one all-chip event, nothing system-wide 01:05-08:50";
- light phase "32 all-chip rows, chance 1.33, A2-B1 chance 0.08".

![[2026-10-02-noise-figL-system-events-both-runs.png]]

**Figure L.** System-wide events (both ports in the same 100 ms; height = voting chips hit). Red marks the A2 and B1 floors hit in the same event; orange is Andrea at the rig (start from the data); dotted lines are the lights and air showers.

**Splitter check re-run on `uid0921`**, with chance computed per 30 s stratum over the windows kept (whole-block rates were too low when two animals' rates co-vary):

| pair | night 01:57-02:57 (10-01 value) | day 15:47-16:47 (10-01 value) |
|---|---|---|
| A1-A2 | 1.1x (0.8x) | 0.9x (2.0x) |
| B1-B2 | 0.7x (0.8x) | 0.4x (0.4x) |
| C1-C2 | 1.1x (1.2x) | 0.9x (1.4x) |
| D1-D2 | 0.9x (0.7x) | 0.8x (0.4x) |
| different ports, median (range) | 1.0x (0.6-1.4) | 1.0x (0.4-2.0) |

**Unchanged conclusion: splitter partners coincide at chance, inside the range of unrelated pairs.**

> [!success] The full 24 h analysis of these four mice is now one page: [[2026-10-02-noise-series-4mice-24h-analysis]]
> It covers:
> - the official verdicts (B1 light phase **SCOREABLE**);
> - signal quality, sleep-wake and EEG slow-wave power over 24 h (Figs M, N, O);
> - the disturbance windows;
> - the archive-wide validation of the EMG notch (Fig P): shuffle 0/100; dose-response; dark > light WAKE in 47/49 vs 41/49 recordings;
> - every number the two code reviews corrected.
>
> NAS: `02_Data_Sleep/andrea/noise-tests/ANALYSIS_2026-10-01_to_10-02_4mice_24h/`.

Still open: `MARKERS.tsv` into the run's NAS folders (not done: it writes to the shared NAS, waiting for Andrea's OK); what happened
at 17:10:08 and 18:12:10; the epoch-shuffle control for the all-days notch test.

## Entry 10: building electrician's inspection, and what he will change (2026-10-06)

Inspection only, no recording. The 4 mice stayed on the rig. The XDAQ was unplugged for his checks and then plugged back in.
Andrea: nothing changed with the mice connected. e10 reads `XDAQ_ONE_REC`, 1000 Hz, USB 5000M.
Source: Andrea's voice recording, AI-transcribed in Korean (`~/Downloads/Electrician 10_06 e10_original.txt`, UTF-16).

**What he said about this room**
- **One shared earth.** The sandwich-panel walls, the room earth and every socket's earth pin are all bonded together.
  Noise from heavy motor loads can travel along this shared earth into the rig.
  - the HVAC/refrigeration plant on the 2nd floor (his guess: its housing is bonded to the panels; he has not checked);
  - the AHU room in front of the elevator, by the clean room;
  - equipment on the 3rd floor.
- **The neutral is shared too.** It carries other loads' current even when we draw nothing, and it cannot be separated here.
- **The July earth wire to the XDAQ** uses a generic shop ring terminal, not the maker's part, and he thinks its contact is poor.
- **Same socket for the XDAQ and the PC:** he agrees this is a possible loop. Separate lines are best.
- **The USB isolator:** "very hard", it covers only the USB line. This agrees with Entry 3 (it doubled the broadband).
- The rack is steel and conducts.

**What will be done**
1. ⭐ **The rig socket will be replaced with an isolated-earth socket** (its earth separate from the shared panel earth).
   - The electricians switch the breaker off and do the work themselves.
   - Cost: only the socket itself. The quote and the date are arranged by our lab.
   - ⚠️ The breaker cut takes down e10 and the XDAQ. Nothing may be recording, and e10 must be shut down cleanly first.
   - Record a 10 min block (`qc/record_block.py`) before the work and another after it. A' (going back) is impossible,
     so judge the change against the untouched spread in [[2026-10-02-noise-troubleshooting-plan]] and repeat the block on a second day.
   - Ask on the day: does the isolated earth terminal get its own insulated wire back to the distribution panel? If it lands on
     the same shared earth, nothing changes.
2. **The headstage foils will be joined to one earth busbar** (screw terminals: one for the main earth, one per foil) = plan T2b.
   - Each foil can be added to or removed from the busbar by us, so foil-bonded vs floating can be tested A/B/A whenever we want.
   - Never connect the animal or headstage GND to it.

**His further steps, only if the socket is not enough** (cheapest first; not decided)
- A second earth wire in parallel, screwed into the rack and panel at several points. ⚠️ This ties the rig more firmly into the
  shared earth, which is the opposite of what the isolated socket does, and it adds earth paths (our rule is one ground point).
- A thicker earth wire to a large busbar.
- An earth brought from the 3rd floor, if nothing large with motors runs there. (His reason was "gravity pulls noise down",
  which is not physics. The only valid reason is fewer motor loads sharing that path.)
- A dedicated circuit, one breaker for this socket only.
- Last resort, which he advises against: a new dedicated earth rod. It costs 10-20x more, digging is hard (concrete, a main
  line nearby), and an outside earth can bring lightning in even with a surge protector (SPD).
- The lab is due to move to E7 (delayed), so he advises spending little here.

**How this fits our data**
- The July earth work changed nothing measurable (2026-07-31). People, hands, the wireless receiver and the air showers do not reach
  the connected EEG/EMG (Entries 8-9); only light switching and the rare building events do.
  The socket is therefore expected to matter, if at all, for the **EMG mains** (A2 13-33 µV) and the chip floors.
- His motor-leakage idea fits the **unexplained building-wide events** (01:59:56, 07:27:42, 08:41:14, 17:10:08, 18:12:11,
  20:56:36). Next: ask facilities for the AHU/chiller on/off log for 10-01 and 10-02.

## Entry 11: the electrician's work, and the first block after it (2026-10-07)

**What was changed** (before 13:43; e10 was shut down cleanly at 13:43 and came back at 14:34 on kernel 7.0.0-28):
- **The socket.** The rig wall socket was replaced with an isolated-earth socket.
  - Its earth pin no longer touches the sandwich panel through the mounting screws (in the old socket the screws were shorted to earth).
  - Its earth terminal is still the same shared building earth wire, so the isolation is only partial (the electrician; Andrea confirmed).
- **The XDAQ** now sits on the top shelf of the metal rack, screwed to it, with a short wire from its chassis GND lug to the shelf.
- **The rack** is earthed by the old XDAQ earth wire, now kept short and soldered to a thicker wire on the shelf. That wire is one of three
  earth wires coming out of a hole in the wall beside the socket, from the building's main line, not from the socket.
- **Not changed:**
  - the PC, on another, unearthed rack;
  - one double wall socket feeding two multitaps (1: the XDAQ brick only, 2-prong; 2: the ASUS PC and everything else);
  - the 4 mice and their tethers.

  Nothing else was reported as changed.
- ⚠️ **THE SOCKET AND THE RACK BOND CHANGED TOGETHER**, so the effect cannot be split between them. Don't undo either, and copy both at E7.

**How it was measured:**
- **The block:** `E1-after-socket-rack_0__uid1007-15-04-18`, 15:04:18-15:14:10, ZT6. Recorded with `qc/record_block.py`, stream 0.998x.
  Same 4 mice, Andrea away from the headstages.
- **The comparison:** the same mice before the work, using `qc/noise_scan.py` + `qc/baseline_compare.py`:
  - the untouched blocks of 10-01 at 19:50, 20:36 and 20:42;
  - the 10-02 light-phase run at 14:55 and 15:05, the same ZT6.
- **Stability:** the two halves of the new block (0:30-5:30 and 5:30-9:30) agree within 1-6 %.
- **Recording-side causes are excluded.** The metadata show only the standard hardware band-pass (1.10-475 Hz), the DSP notch off and no
  software filters. The open EMGs also still carry millivolts of 60 Hz, which a notch would have removed.

| 60 Hz line peak, QC gate scale | before (5 windows) | after (2 windows) | change |
|---|---|---|---|
| chip floor A1 | 2758-2943 µV | 232-235 µV | x12 lower |
| chip floor A2 | 2057-2133 µV | 36 µV | x58 lower |
| chip floor B1 | 712-1106 µV | 41-43 µV | x17-27 lower |
| chip floor B2 | 1809-2008 µV | 41-42 µV | x45 lower |
| chip floors at 120 Hz (rms) | 43-82 µV | 0.4-3.1 µV | x20-120 lower |
| EEG A1 / A2 / B1 / B2 | 19-21 / 2.7-5.7 / 5.0-7.5 / 3.3-4.1 µV | 2.0-2.1 / 1.9-2.4 / 2.0-2.6 / 1.9-2.3 µV | A1 x10 lower |
| **EMG A2** | **26-33 µV** | **1.0-1.4 µV** | **x20-30 lower** |
| **EMG B1** | **4.0-4.7 µV** | **0.4-0.5 µV** | **x10 lower** |
| open EMG A1 (A/2): 60 Hz, time on the rail | 4.65-4.85 mV, 13.4-13.7 % | 3.22-3.25 mV, 0.03-0.79 % | rail gone |
| open EMG B2 (B/34): 60 Hz, time on the rail | 4.71-4.99 mV, 13.9-14.0 % | 0.57 mV, 0.03-0.08 % | rail gone |
| A2 floor broadband 1-45 / 100-450 Hz (rms) | 15.6-17.8 / 3.9-4.1 µV | 13.7-18.1 / 3.5-3.8 µV | unchanged |

**This is far outside the normal drift.** Over the whole 10-01/02 24 h (hourly values):
- A2's EMG 60 Hz never went below 14 µV;
- the A2 floor stayed within 2077-2174 µV;
- the B1 floor stayed within 664-1154 µV.

**What the stager sees** (`qc/emg_mains_share_windows.py`): 4 s epochs, the EMG band-passed 10-124 Hz (the stage 3 band), raw and with
60 + 120 Hz notched.

| | before (10-01 20:36/20:42, 10-02 14:55/15:05) | after (10-07, 140 epochs) |
|---|---|---|
| A2: mains share of the EMG measure, median | 92.8-97.4 % | **12.1 %** |
| A2: quiet EMG (p10), raw | 19.0-23.3 µV | **2.6 µV** |
| A2: quiet EMG (p10), notched | 2.8-5.3 µV | 2.3 µV |
| B1: mains share, median | 11.3-12.8 % | 7.3 % |

- **A2:** its real quiet muscle tone (2-5 µV) was buried under about 20 µV of mains. Now the raw signal shows it.
  **For new recordings the hardware does what the validated notch did.**
- **B1** slept through the whole block (EMG p10-p90 4.6-5.3 µV, high EEG), so its sleep/wake EMG range is not judged yet.
- **The brain signal itself is unchanged:** the EEG spectra lie on top of each other below 60 Hz (Fig Q).

**A1 and B2, the open EMGs (implant side):** they no longer rail, but they are still not EMG.
- What Andrea now sees in Allego is a slow wave at 3.0-3.8 Hz (180-230 per min), 430-890 µV rms in 1-8 Hz, plus the remaining mains.
- It does not follow the mouse's own EEG (|r| ≤ 0.13) or the other open EMG (r ≈ 0).
- The rate fits a resting mouse's breathing, so it is most likely the broken lead moving with each breath.
- There is no muscle band. A1 and B2 stay EEG-only mice (surgical, per Andrea).
- **The A1 position still sees about 6x the field of the others:** floor 232 vs 36-43 µV; open EMG 3.2 vs 0.57 mV.

> [!warning] 🔴 The ground gate now calls EVERY chip UNJUDGEABLE
> `FLOOR_MIN_HUM_UV` = 800 µV, and the floors are now 36-235 µV. All four chips read "grounded" on 10-02 14:55.
> Audit C1 predicted this ([[2026-10-02-noise-series-method-audit]]). Until the gate is replaced, the official QC will reject every mouse
> at rung 2. **DECIDE BEFORE THE NEXT REAL RECORDING** (Andrea).

**My prediction was wrong.** On 10-06 (Entry 10) I expected "a small effect at most", because the July earth work had changed nothing
measurable. The effect was large. Two likely reasons, which cannot be separated:
- the July wire may never have made a good contact (the electrician blamed the generic ring terminal);
- the old socket's screws joined the PC's earth to the panel, which could carry building noise onto the USB shield.

![[2026-10-07-noise-figQ-grounding-fix-before-after.png]]

**Figure Q.** The same 4 mice at the same time of day (ZT6): 10-02 14:55 (blue, before) vs 10-07 15:05 (orange, after).
- Columns: EEG spectrum, EMG spectrum, 2 s of raw EMG, and the chip floor (median of the 14 wire-free inputs).
- The 60 Hz spikes and their harmonics are gone from every EEG, the clean EMGs and the floors. Everything else overlaps.
- The orange A2 EMG is busier because A2 was awake in that window.
- The open EMGs (A1, B2) no longer clip, and now show the slow breathing-rate wave instead.
- Made by `eeg-emg-analysis/qc/electrician_before_after_2026_10_07.py`.

**Now recording (confirmation):**
- Console run `ee0263bffeaa`, `allego_0__uid1007-15-28-38`, 10-07 15:28:38 → 10-08 21:02, about 29.5 h.
- It covers the rest of this light phase, a full dark phase and a full light phase, with both lights-OFF switchings and the lights-ON.
- Same settings as the 10-01/02 runs (batch `noise-tests`, `POS-<slot>`, ports A+B, 8 labels). The watchdog was armed by hand.
- **Questions it answers:**
  - Does the drop hold over a whole day and night, through the light switching and the building events?
  - How does staging compare with the 10-01/02 24 h? Same mice, ZT12 to ZT12.

**Files:**
- Data: `~/radix/noise-tests/2026-10-07/`, the block plus `out/` (JSONs, scan text, figure).
- Scripts: `qc/electrician_before_after_2026_10_07.py`, `qc/emg_mains_share_windows.py`.

## Entry 12: the 29.5 h confirmation run after the grounding fix (2026-10-07 15:28 → 10-08 21:02)

**The run:**
- Console run `ee0263bffeaa`, `allego_0__uid1007-15-28-38`, 29.56 h, stopped at 21:02:03 (1 s late).
- Same 4 mice and the same settings as the 10-01/02 runs. Analysed on 10-09 on e10, with the rig idle.
- It covers the rest of the 10-07 light phase, a full dark phase and a full light phase.
- **Before** = the 10-01/02 24 h of the same mice ([[2026-10-02-noise-series-4mice-24h-analysis]]), measured with the same estimators.

**A disturbance to set aside:** a lab member was at the racks on the afternoon of 10-08 (Andrea's note):
- recording rack (cage setting): 16:41-16:43, 16:45, 16:59-17:03, 17:10-17:14 and 17:24-17:32;
- habituation rack: 17:35-17:37.

The third window was written "17:3" and read as 17:03. Markers, with seconds from the file start:
[[2026-10-08-noise-MARKERS-visit-uid1007-15-28-38.tsv]]. Anything odd inside these windows is not investigated.

**Pass bar, written on 10-07 before the data came in, and the result:**

| check | bar | after | before |
|---|---|---|---|
| chip floors at 60 Hz, every hour | < 300 µV | ✅ A1 224-239, A2 32-36, B1 34-53, B2 40-44 µV | 664-2965 µV |
| A2 EMG 60 Hz, every hour | < 3 µV | ✅ 0.5-2.3 µV (B1 0.6-2.7) | A2 14-27, B1 4.2-4.7 µV |
| light-switch spikes | smaller | ❌ **not smaller**: lights-ON floors A1/A2/B1/B2 3137/5190/1694/2031 µV | 4322/5491/1615/1315 µV |
| building-wide events | fewer or smaller | ✅ 1 unexplained (10-08 01:08:09.5, small) in 29.5 h | 6 unexplained in 24 h |
| scoring without the notch | A2 and B1 SCOREABLE, wake dark > light | ✅ (table below) | A2 REJECT |

- **Hum:** read from the runs' QC bundles (`qc/hourly_hum_bundle.py`, the 10 s gate estimator, hourly medians).
  - The EEG 60 Hz is 2.0-3.2 µV on all four mice, in every hour.
  - B1's EMG "60 Hz" is highest at 23:00-03:00, when B1 is 85-95 % awake. With the mains this low, that bin now partly
    measures real muscle activity.
- **Light switching** (`qc/light_switch_peaks.py`: 50 ms comb, 1-450 Hz, µV): the lights-ON spike is as big as before.
  - Lights-OFF is small in both periods. The 10-07 lights-OFF was detected at 21:01:47.6 (A2 floor x66); the 10-02 and 10-08 ones
    stayed under the bar.
  - The grounding fixed the steady pickup but not the switching transient, which probably reaches the rig by another route
    (most likely the light wiring itself).
  - Cost: about 2 events a day, rejected per epoch.
- **System-wide events** (`qc.allchip_scan_file`): the voting chips are A2 + B1 in all three files, with A1 and B2 excluded for
  their open EMGs, so the counts compare directly. After, 4 events in 29.5 h (chance 0.04):
  - 21:01:47.6, lights-OFF;
  - 01:08:09.5, small and unexplained;
  - 08:59:50.7, lights-ON;
  - 17:31:24.8, inside the visit.

  Before: 01:59:56, 07:27:42, 08:41:14, 17:10:08, 18:12:11 and 20:56:36, plus the lights.

**Scoring (diagnostic: the official QC calls every chip UNJUDGEABLE because of the 800 µV gate):**
- Stage 2 `--all-verdicts` into `~/radix/noise-tests/2026-10-09/diag-processed/`. Stage 1: A2 and B1 CLEAN, A1 and B2 OPEN.
- Stage 3 as published and with the EMG notched (`qc/emg_mains_staging_test.py`).

| mouse | verdict, as published | r@1min (shuffled) | notched r@1min | wake % light / dark | before, as published |
|---|---|---|---|---|---|
| A2 | **SCOREABLE** | **0.615** (-0.003) | 0.630 | **26.9 / 55.6** | REJECT, r 0.19 night / 0.29 day; wake 11.3 / 17.8 |
| B1 | **SCOREABLE** | **0.587** (-0.011) | 0.589 | **20.6 / 61.1** | SCOREABLE, r 0.30 / 0.41; wake 17.6 / 30.1 |

- The notch now changes almost nothing: the mains is gone at the source.
- Wake is 2-3x higher in the dark than in the light, as expected for nocturnal mice. Before, A2's EMG was 93-97 % mains and
  flattened that contrast.
- During the visit windows, B1 was awake 57.6 % of the time and A2 14.2 %.
- **A1 and B2 (open EMGs):**
  - they rail in 0-3.6 % of 10 s epochs per hour, against about 14 % before;
  - their 60 Hz is 1.6-3.4 mV (A1) and 0.45-0.57 mV (B2);
  - they are still not EMG.

**Post-processing:**
- **Why it failed:** the console stopped at FAILED_STRIP. The strip's GATE B saw `din_1` move: 6 single 1 ms samples at 10-07 18:40:41,
  21:57:59, and 10-08 07:57:51, 13:50:40, 13:51:10 and 13:56:14. None of them falls on a light switch or the visit, so it is a
  floating input picking up noise.
- **The fix:** Andrea confirmed on 10-09 that nothing is connected to the XDAQ GPIO header. The strip was re-run by hand with
  `--gpio-never-connected`, which is recorded in the strip report. The run was then moved to STRIPPED, and the console finished the
  export and the NAS upload: **DONE 2026-10-09 ~21:00**: 4 per-mouse CSVs (24.9 GB), sha256-verified on the SKIM NAS at `02_Data_Sleep/andrea/noise-tests/Baseline/20261007_POS-<slot>_B/`; the trimmed file (8 channels, 4.26 GB, bit-exact over 106.4 M samples) stays in `~/radix/stripped/`. The run record still carries the old strip text in its `error` field (not cleared on retry); its state is DONE.
- **Left over:** the failed attempt's partial output (`allego_0__uid1007-15-28-38.REJECTED.20261008T120617Z_*.part`, 4.2 GB) is
  still in `~/radix/stripped/`. Deleting it is Andrea's call.
- 🔴 **When the XDAQ → Pi hardware sync is wired, GATE B becomes load-bearing.** Never use the override after that.

![[2026-10-09-noise-figR-grounding-24h-before-after.png]]

**Figure R.** The same mice over 24 h, before (blue, 10-01/02) and after (orange, 10-07/08) the grounding fix. The shaded band is
lights-off (21:00-09:00).
- Top: chip floors at 60 Hz (log scale).
- Middle: EMG 60 Hz (log scale).
- Bottom: wake % per hour, scored as published, with no notch.
- The floors and the EMG mains sit 10-60x lower all day. Wake now follows the light cycle, especially B1 (95 % in the early dark).
- Made by `eeg-emg-analysis/qc/grounding_24h_figure_2026_10_09.py`.

**Verdict:**
- **The grounding fix holds over a full day and night.** The steady mains is gone at the source, and both clean mice score without
  the notch, with a normal day/night pattern.
- **What it did not fix:** the light-switch spikes, which are rare and rejected per epoch.

**Still open:**
- replace the 800 µV ground gate (it blocks the official QC);
- test the Raspberry Pi cameras A/B/A (off → on, with the IR lights if any → off) with `qc/record_block.py` before adding them for good.

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

**2026-10-02: full RAW overnight on the SKIM NAS** for workstation analysis (Andrea's request):
`02_Data_Sleep/andrea/noise-tests/RAW_20261001_2100_overnight_4mice_cfdf8ebde0c6/`. It holds the complete 134-channel Allego set
(23.2 GB data, timestamps, json), every file SHA-256 verified by read-back with the cache dropped (copied at idle I/O priority during the
light-phase recording, whose file kept growing normally throughout). Also: README.txt (what, why, mice, rig state, findings, the exact
workstation commands), `scripts/` (the 2026-10-02 qc copies) and `analysis/` (figures, diagnostic staging). The per-mouse CSVs are in
`../Baseline/20261001_POS-<slot>_B/`. Purpose: the full-resolution scans of 01:05-08:50 on the workstation instead of the rig.

## Next steps and open decisions (as of 2026-10-02 11:10)

**Running / scheduled (no action needed):**
- Light-phase run `8f84e3e62af6` until 21:02 (keeps the 21:00 lights-OFF); health checks at :17 until 19:17.
- 21:09 job: stop + lights-OFF check; once the console is DONE, full-resolution scans of the overnight and light-phase files; light-phase
  stages 1-3 with and without the EMG notch; notch test over every `~/eeg-processed` day folder; splitter re-run on `uid0921`.

**Waiting on Andrea:**
1. **Full scans of 01:05-08:50 on the workstation** (raw + README commands on the NAS, `RAW_20261001_2100_overnight_4mice_cfdf8ebde0c6/`), run
   by hand or driven from here over Tailscale SSH (one browser approval). If they finish first, the 21:09 job's overnight scans are dropped.
   **AWS was considered and deferred (2026-10-02):** the raw is not in S3 until the 10-03 01:30 archive run (it defers while recording), an
   upload now is a heavy read on the recording disk, and EC2 needs set-up with no budget alerts. AWS is the venue for **archive-wide**
   reprocessing later (C1/C3 re-derivations over ~1 TB already in S3).
2. **B1 board check after 21:02**: the collapsed wire-free pairs (/6, /14-/16), board seating, wires or foil on the pads.
3. **Floor guards** (audit C1) and the **EMG mains notch** (audit C3): both are pre-registered pipeline decisions.
4. **Deploy the console/watchdog fixes** in the worktree, only after the run is DONE.
5. Still open from 10-01 (below): foil bonded to the chassis GND, twisted slip-ring wires. Dummy loads declined for now (Andrea, 10-01).

### ⭐ Troubleshooting plan for the next trials (written 2026-10-02): [[2026-10-02-noise-troubleshooting-plan]]
Andrea's list turned into an ordered, A/B/A plan with the same measurement block as the no-mice series, each trial judged against the
spread of three untouched runs (A2 floor x1.03, EMG 60 Hz x1.07, so a change must beat that):
- **Prerequisites:** B1 board check; DMM checks (foil floating? amplifier ground tied to chassis?); **where the slip-ring wires land**
  (only to confirm /3-/16 are wire-free; the tether's copper shield was never on any pad, Andrea 10-02).
- **Phase 1, now, nothing to build:** T1 USB isolator with mice, T2 foil bonded to the chassis GND, T3 tether shield to ground at the board end.
- **Phase 2, build:** T4 aluminium box, T5 box grounded, T6 tether copper shield coiled onto the box, T7 Faraday cage around the home cage.
- **Phase 3, tether change + 12-24 h runs, concurrent control + crossover:** T8 counterbalance arm (tether), T9 arm for slip ring + tether,
  T10 new slip ring, T11 slip ring as the tether.
- Main target: **the 60 Hz in the EMG** (it corrupts staging, C3, and we do not notch). New recorder `qc/record_block.py` (refuses during
  console runs, checks the stream rate, logs every block); Session 1 is written out as commands.

## Next steps (as of 2026-10-01; superseded by the list above)

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
> 1. Port A 120 Hz source: OPEN. Not the room lights (entry 2). **2026-10-02: absent with 4 mice on and the free wires taped**: floor 120/60 Hz = 0.03 on A1 and A2 overnight (41-66 uV of 120 Hz) vs 0.31-0.59 on 09-30. Port B reads the same, so it rode on the open slip-ring wires / antenna of the no-mice set-up. Which change removed it (tape, multitap move, mice) is not separated.
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

---
tags: [experiment, eeg, S-SD, recovery-sleep, endpoint]
date: 2026-09-02
created: 2026-09-01
updated: 2026-09-14
status: completed
---

# S-SD recovery sleep, Wednesday 13:00 to Thursday 09:00, the terminal endpoint

> [!abstract] TL;DR
> **Wednesday 2026-09-02 13:00 KST to Thursday 2026-09-03 09:00 KST, 20.0 hours**, on the eight
> S-SD animals, immediately after the LAST chronic sleep deprivation (CSD) bout ends. The animals
> are **sampled at 13:00 on Thursday**, four hours after the recording stops. **This recording
> cannot be repeated.** We score it on the Thursday.
>
> Pre-flight connection screen ran on Tuesday 2026-09-01, twice, and the verdict is **AMBER**:
> two positions are solid, three flicker, three read as continuous breaks.
> Expect **n = 2 guaranteed, up to n = 5 if the mechanical faults settle.**
> Write the final go / no-go line in the 2026-09-02 journal before pressing record. (No entry was ever written for that date.)

> [!info] Recording file, found 2026-09-14
> The run happened but was never catalogued here — this page sat in `active/` at `status: planned`
> for 12 days after the animals were sampled. Confirmed present on `e10ubuntu` at
> `/home/skimlab/radix/data/`:
>
> - `allego_2__uid0902-13-00-28_data.xdat` — **75,749,372,928 bytes (75.7 GB)**
> - `allego_2__uid0902-13-00-28_timestamp.xdat` — 578,239,488 bytes
> - `allego_2__uid0902-13-00-28.xdat.json` — metadata, 139,846 bytes
>
> File start (`13-00-28`) and mtime (2026-09-03 09:05) match the 20.0 h window as run.
> ⚠️ Superseded in part — see the 2026-09-23 update below.

> [!success] Updated 2026-09-23 — it is now stripped, archived and carded
> The text above said this recording had "not been scored, moved to the NAS, or
> written up". Two of those three are now done.
>
> - **On the SKIM NAS** as `20260902_HLBSSD_RSR/`, stripped to 16 channels,
>   bit-exact, with its QC bundle. Raw is in S3 too, so it has three copies.
> - **Carded.** Eight verdict cards under `cards/out/S-SD/`.
>   ⚠️ Until 2026-09-23 every one read `animal_id: UNKNOWN@<position>` — the
>   recording was missing from `cohorts/S-SD.yaml` entirely, so nothing could
>   resolve who sat in which position. Fixed; the identities below are real.
> - **Still not staged.** Rung 3 is INSUFFICIENT throughout, so no sleep
>   architecture exists for this recording and "What we do with it on Thursday"
>   remains open work.
>
> **Outcome: n = 1 at rung 2.**
>
> | pos | animal | rung 2 CONNECTION |
> |---|---|---|
> | D2 | HLBSSD18 | ✅ **PASS** — 60.6% usable, longest unbroken block 19.7 min |
> | B1 | HLBSSD17 | ⚠️ UNJUDGEABLE — chip floor 769 µV, under the 800 µV gate |
> | B2 | HLBSSD14 | ⚠️ UNJUDGEABLE — chip floor 124 µV |
> | A1 A2 C1 C2 D1 | SSD11 12 15 16 19 | ❌ FAIL, 0.0–0.9% usable |
>
> 🔴 **It is also 3 h 55 m SHORT of the protocol window.** The standard for a
> sleep-deprivation recovery is 13:00 → 13:00, 24 h, ending at sampling. This
> stopped at 09:05, so the four hours immediately before the terminal endpoint
> were never recorded. The animals were sampled; it cannot be repeated. The
> protocol was only written down on 2026-09-23, after this run:
> [[CANONICAL-recording-windows-and-protocol]].

## The protocol state, written out so it cannot be misread

The 2026-08-29 lesson was that "after N days of CSD" is ambiguous and I read it the wrong way on
W-SD. So, explicitly:

| | |
|---|---|
| deprivation ends | Wednesday 2026-09-02, 13:00 KST |
| recording window | Wednesday 13:00 → Thursday 09:00, **20.0 h** |
| sampling | Thursday 2026-09-03, 13:00 KST |
| protocol state across the window | **CSD is FINISHED.** This is the terminal recovery window |
| repeatable? | **No.** The animals are gone four hours after it stops |

⚠️ **This is NOT the same thing as the W-SD recording of 2026-08-27.** That one was the recovery
window after the *penultimate* deprivation bout with the protocol still running. This one is after
the last bout, so it is a true post-protocol endpoint. The window and the weekday are written above
precisely so nobody has to infer it later. See [[2026-08-27-W-SD-recovery-sleep]].

## Pre-flight connection screen, Tuesday 2026-09-01

Run per [[pre-flight-connection-screen]]. Two short recordings, before and after Andrea re-seated
every connector.

- `allego_0__uid0901-12-24-03` — 12:24:03, **115.7 s**, 1000 Hz, 262 ch. Taken right after replugging.
- `allego_1__uid0901-12-38-53` — 12:38:53, **84.6 s**, 1000 Hz, 262 ch. Taken after the re-seat.

🛑 **Both files are far too short for a usable percentage.** 84 s is 8 QC epochs, and a 1st-percentile
threshold estimated from 8 numbers per site is effectively a minimum. Everything below is chip floor,
lf/hf separation against each chip's OWN wire-free floor, and epoch-to-epoch flicker. No fractions.

### The re-seat fixed every chip ground

| chip floor, 60 Hz, µV | A1 | A2 | B1 | B2 | C1 | C2 | D1 | D2 |
|---|---|---|---|---|---|---|---|---|
| 12:24, after replugging | 5213 | 4324 | 2435 | **117** | 2825 | 4432 | 2691 | **1052** |
| 12:38, after the re-seat | 5361 | 4707 | 2710 | **2486** | 2916 | 4569 | **3793** | **4541** |
| floor variability across epochs | 3.7% | 0.2% | 6.8% | 2.0% | 24.4% | 10.5% | 5.0% | 1.1% |

B2 went 117 → 2486 µV and D2 1052 → 4541 µV, and D1's floor stopped swinging between 1734 and 4106.
**All eight chips are now grounded and steady.** That matters more than any single channel: an
ungrounded chip makes every statistic on it meaningless, so until this was fixed six of the eight
positions were UNJUDGEABLE rather than failing. See [[weak-chip-ground-vs-open-electrode]].

⭐ **The ground was the fixable half, and re-seating fixed it in fifteen minutes.** This is the
second time in two batches that a bench re-mate recovered chips that the code would otherwise have
reported as dead animals.

### D2 came back on both roles

`HLBSSD18` at D2 had a collapsing ground at 12:24 (floor 684-2014 µV, sagging, EEG flat at 22 µV)
and after the re-seat reads **EEG rms 114-153 µV, slope −1.73, lf/hf 24 to 38 against its own floor
99th percentile of 3.33, above it in 21 of 21 epochs**, with **EMG locked at 50 µV and 69 µV of
60 Hz**, inside the 9 to 90 µV connected band. Both roles, cleanly.

D2 has now passed the strict rung 2 gate on three consecutive full-length recordings and is the
animal to protect. A2 (`HLBSSD12`) is the other solid EEG, lf/hf 9.8 → 38.8, above its floor in
21 of 21 epochs.

## 🔑 The failures split in two, and only one half is torsion

Andrea's reading is that the tethers are failing from torsion and torque accumulated over time,
bending rather than hanging straight. **The data supports that for exactly three positions and
contradicts it for three others**, and the discriminator is simple: a conductor that bends in and
out of contact must FLICKER. A severed one sits still.

Measured over the 21 four-second epochs of the 12:38 file, with the chip floor stable throughout:

| pos | animal | EEG rms variability | rms max/min | lf/hf range | epochs above own floor p99 | read |
|---|---|---|---|---|---|---|
| **A1** | HLBSSD11 | **150%** | **49×** | 1.3 – 15.4 | 16/21 | 🔧 **FLICKER** |
| **C2** | HLBSSD16 | **80%** | **55×** | 1.3 – 27.3 | 13/21 | 🔧 **FLICKER** |
| **C1** | HLBSSD15 | **101%** | 7.3× | 1.1 – 18.5 | 3/21 | 🔧 **FLICKER** |
| D1 | HLBSSD19 | 13.6% | 1.8× | 1.5 – 2.2 | 0/21 | ❌ STATIC |
| B2 | HLBSSD14 | 4.3% | 1.1× | 2.1 – 2.7 | 0/21 | ❌ STATIC |
| B1 | HLBSSD17 | 4.0% | 1.2× | 2.6 – 3.2 | 0/21 | ❌ STATIC |
| A2 | HLBSSD12 | 11.1% | 1.6× | 9.8 – 38.8 | 21/21 | ✅ working |
| D2 | HLBSSD18 | 17.7% | 2.1× | 6.3 – 38.2 | 21/21 | ✅ working |

### The three that flicker

- **C2 is the cleanest example this rig has produced.** In 84 seconds it goes open (rms 4558 µV,
  lf/hf 1.4) → **closed for 40 seconds** (rms falls to 90-159 µV, lf/hf climbs to 27.3, real EEG) →
  open again (rms 4900 µV). **Its EMG tracks it in lockstep**, 1375 → 880 → 1363 µV. Two conductors
  in one bundle making and breaking together, twice, while the chip floor does not move.
- **A1** flips seven times in 84 s between rms 62-78 µV with good EEG and rms 410-3050 µV open. Its
  floor sits at 5500 µV the whole time.
- **C1** was flat at 29 µV for 68 s, then at epoch 17 its EEG jumped to rms 189 µV and lf/hf 18.5,
  **its EMG jumped 99 → 567 µV and its chip floor jumped 2917 → 4476 µV, all in the same epoch.**
  Two roles and the floor moving together is the tether BODY moving, not an electrode. The identical
  event appears in the 12:24 file at t ≈ 68 s. C1's tether is already logged as having failed
  structurally at its centre on 2026-08-27.

⭐ This is the same phenomenon as [[movement-dependent-contact-root-cause]]: contact flips fast and
reversibly, so a single short sweep can neither rank nor classify these channels.

### The three that do not

B1, B2 and D1 hold a fixed open value for the full 84 seconds — variability of 4.0%, 4.3% and 13.6%,
with max/min ratios of 1.2, 1.1 and 1.8 — on chips that are now properly grounded. **A bent conductor
that intermittently touches cannot hold a level that steady.** These read as continuous breaks, and
straightening the tether will not recover them.

⚠️ **Honest limit: 84 seconds cannot rule out a SLOW intermittent.** A channel with a period of
minutes would look static in this file. That is what the ten minute re-screen below is for.

## The test that would settle it

Record continuously and **rotate and straighten one tether at a time**, A1 first because it flips
most often. If a channel closes when the tether is straight and opens when it is twisted, torsion is
proven per position and the fix is a swivel or a shorter tether. If B1, B2 or D1 do not respond in
any position, they are severed and no handling recovers them.

## 🔴 Go / no-go: AMBER, with a mandatory re-screen

| | positions | n |
|---|---|---|
| ✅ solid now | A2, D2 (D2 on both roles) | **2** |
| ⚠️ carry real EEG part of the time | A1, C2, C1 | up to **5** |
| ❌ read as continuous breaks | B1, B2, D1 | — |

Per [[pre-flight-connection-screen]] this is **AMBER, not green**: the run is worth taking but it is
under-powered, and that is being recorded here rather than discovered at analysis time. It is not
RED, because unlike 2026-08-27 the chip grounds are all healthy and two animals are unambiguous.

**Before pressing record on Wednesday:**

1. Do the tether manipulation test above.
2. Take a **10 minute** recording — the shortest file that gives defensible usable fractions — and
   score it. Every chip floor must read **≥ 2000 µV**.
3. Confirm the file is **1000 Hz and 262 channels**. A fresh Allego launch comes up at 30 kHz in
   `SMARTBOX_PRO` mode. Launch with `--disable-gpu`. See [[allego-mesa-gpu-crash-and-log-storm]].
4. Write the go / no-go line into the 2026-09-02 journal with the positions started and the positions
   knowingly started without.
5. Start the 20 h run and arm the byte-rate watchdog on the new file.
6. Kill any `allegoserver` thread left spinning after the GUI closes, it costs +10 W and +11 °C.
   See [[allegoserver-runaway-thread-thermal]].

## What we do with it on Thursday

Score to rung 2 with the per-chip floor, then D2's hypnogram against its own pre-CSD baseline from
`allego_1__uid0826-12-50-16`. **State the block duration on every number quoted**, and the strict
rung 2 figure is EEG and EMG usable in the SAME epoch — say which one is being quoted.

## Still open

- 🔴 `FLOOR_MIN_HUM_UV` is still 800 µV. At 12:24 D2 read 1052 µV and PASSED that gate while being
  physically ungrounded. **This run is the fourth recording where 800 is demonstrably too low.**
  Proposed 2000. Still not applied. See [[weak-chip-ground-vs-open-electrode]].
- ⚠️ A2's EMG reads rms 352-354 µV, dead constant, with 479 µV of 60 Hz. That is a fixed artefact
  level, not muscle. A2 is EEG-only unless it changes.
- ⚠️ D1's own wire-free floor is CONTAMINATED — its lf/hf 99th percentile ran 18 to 29 while other
  chips sat at 2 to 7. Judge D1 on rms and slope, never on its ratio. ✅ The contaminated-floor
  validity guard for rung 2 was written on 2026-09-26 (`2cc5892`); it does not fire on this
  recording.
- ⚠️ An unattributed 223 GB file sits in the raw directory, see [[2026-09-01]]. Not adopted here.

## Added 2026-09-26 — stage 3 run for the first time: S-SD has no scoreable sleep at any timepoint

Stage 2 and stage 3 had never been run on any S-SD recording. Run on 2026-09-26 on the 24 h
baseline, the B1-swap baseline and this endpoint; all three were then re-carded (rung 2 unchanged
on every card).

| recording | mice split by stage 2 | stage 3 SCOREABLE | ladder rung 3 PASS |
|---|---|---|---|
| `allego_0__uid0825-09-00-00` 24 h baseline | A1, B1, D2 | A1 (r 0.409) | **none** — A1 fails rung 2 |
| `allego_1__uid0826-12-50-16` B1-swap baseline | A1, B1, D2 | A1 (0.360), B1 (0.386) | **none** — A1 UNJUDGEABLE, B1 fails rung 2 |
| `allego_2__uid0902-13-00-28` **this endpoint** | B2, D2 | **none** | **none** |

🔴🔴 **The endpoint has no scoreable animal, by either engine. S-SD recovery sleep is n = 0,
and this recording cannot be repeated.**

🔑 **D2/HLBSSD18, the only S-SD animal to pass rung 2 at every timepoint, has an EMG that
cannot stage sleep.** Stage 3 rejects it on all three days for implausibly low wake (1.6%, 0.9%,
0.2%) and r@1min 0.029, 0.025, −0.023. In the muscle band stage 3 uses (10–300 Hz band-pass,
`FILT_EMG`), its EMG never drops toward atonia and never rises at night:

| | EMG rms p5 | p95 / p5 | EMG light → dark |
|---|---|---|---|
| S-SD D2, all three days | 27–33 µV | **1.41–1.75** | 30.9 → 32.3 µV, flat |
| working EMGs (W-SD D2 twice, S-SD A1) | 7–9 µV | 4.1–6.0 | roughly doubles |

⚠️ **CORRECTED 2026-09-26 after independent verification: this is NOT proof the EMG is dead.**
The raw, broadband EMG does change: its 10 s rms rises from about 33 to 75 µV at night, and on
raw 10 s rms its p95/p5 (14.4, 11.6) does not separate from working EMGs (13.2, 9.0). The raw
site `D/34` also has a steep, EEG-like spectral slope (−1.27, −1.38), so that nightly rise is
low-frequency content. Whether it is volume-conducted brain signal, movement artefact or
something else is **not established**. What IS established is narrower: **there is no
state-dependent activity in the muscle band**, which is the band stage 3 stages on. The
pre-flight screen above recorded "EMG locked at 50 µV" and read it as healthy.

Rung 2 passes it because EMG is judged on hum and amplitude only. Rung 3 is where it is caught.
Logged as an open defect: [[emg-without-muscle-band-activity-passes-rung-2]].

⚠️ **The two baseline SCOREABLEs do not rescue the batch.** A1 fails or is unjudgeable at rung 2
on both baselines and is OPEN at the endpoint. B1/HLBSSD17's EMG is as flat as D2's (p95/p5 1.7),
and its Otsu split is unstable (94% wake at a 0.75× threshold), so its 0.386 is fragile as well as
blocked.

Outputs: `~/eeg-processed/2026-08-25`, `2026-08-26`, `2026-09-02` (not in the repo).

## Related

[[pre-flight-connection-screen]] · [[weak-chip-ground-vs-open-electrode]] ·
[[2026-08-27-W-SD-recovery-sleep]] · [[2026-08-28-W-SD-cohort-closeout]] ·
[[2026-08-27-B1-swap-baseline-20h-run]] · [[movement-dependent-contact-root-cause]] ·
[[animal-card-and-verdict-ladder]] · [[2026-09-01]]

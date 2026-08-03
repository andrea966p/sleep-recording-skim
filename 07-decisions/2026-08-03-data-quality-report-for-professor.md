---
tags: [report, eeg, emg, data-quality, scoring, impedance, noise, methods]
created: 2026-08-03
status: current
audience: PI / lab meeting
---

# EEG/EMG Data Quality — Full Report

**Prepared 2026-08-03.** Covers every recording made to date (33 files, 566 GB, 8 substantive recordings), the two analysis errors we found and corrected, how data quality is defined and measured, what the impedance screen does and does not tell us, where the noise comes from, and what we actually have.

---

> [!important] ADDENDUM, same day — read this before the numbers below
> Four things changed after this report was first written. **The conclusions
> below all survive**, but some numbers shifted slightly and two claims are now
> stronger, one weaker.
>
> **1. The light schedule was recorded: lights ON 09:00, OFF 21:00 KST, ZT0 =
> 09:00.** This unlocked a check that is *completely independent of every
> threshold we chose*, because nothing in the analysis knows about the clock.
>
> **2. C1 now has external validation.** In the light phase C1 is **66.9%
> asleep**; published C57BL/6 values are **~70% asleep in the light phase (NREM
> 62.0 ± 7.8 %/12 h)**. It is inside one standard deviation, and the light/dark
> contrast runs the right way (33.1% wake in the light, 82.2% in the dark).
> Three independent lines — persistence, physiology, circadian timing — now rank
> the animals identically: C1 strong, C2 real, D2 fails.
>
> **3. The 06-29 animal is explained.** That recording sits entirely in the light
> phase, when a mouse should be ~70% asleep, and the animal was 95% awake on
> technically flawless data. That is not an artefact — it is an animal that was
> not sleeping, consistent with first-tethering acclimatisation.
>
> **4. The thresholds in §5 were partly guesses and have been re-derived from
> 1,137,955 pooled epochs.** `RAIL` is now 6389.6 µV (= 0.195 µV/LSB × 32767,
> measured identical on all 8 channels — the ADC full scale); `OPEN` moved
> 300 → 150 µV (the mains distribution is bimodal with its valley at 134 µV);
> and the old 25 µV "shorted" rule **was wrong** — it discarded 9.5% of all
> epochs including real low-amplitude wake, and it was the only constant whose
> value moved a verdict. It is now split into an epoch-level dropout test
> (11 µV) and a channel-level dead-electrode test (20 µV median). A full
> sensitivity sweep confirms **C1 is invariant** — `r = 0.74`, 8.7 h, in every
> variant tested.
>
> **5. Weaker claim: do not report a REM percentage at all.** §5 already warned
> that the 80th-percentile rule fixes REM by construction. An independent Otsu
> cut gives 24–48% of sleep, and the literature value for mice is **<10%**. Both
> rules land far above it, so **REM is not reliably separable with this
> montage.** Report WAKE vs NREM, plus REM's *order* (entered from NREM).
>
> The analysis path is now a documented three-stage pipeline —
> [[pipeline/README]] — replacing the ad-hoc scripts this report describes.

---

## 1. Executive summary

> [!abstract] The one-paragraph version
> We have **one recording that contains real, defensible mouse sleep**: 2026-07-31, animals **C1 and C2**, together about **10.4 scoreable mouse-hours**, with C1 contributing a single **8.1-hour unbroken stretch** of good contact. Everything else we have ever recorded — including a 72-hour run and a 20-hour run — contains **no scoreable sleep**. The limiting factor is not noise, not grounding, not the amplifier, and not the analysis: it is that **the EEG electrodes are electrically disconnected most of the time**. In 41 animal-recordings, the EEG channel was electrically open for the entire session in 36 of them.

**Three things changed in this analysis round, and all three matter:**

1. **The channel map was wrong until 2026-08-01.** We were computing EEG as the difference between two channels that are *already* differential, i.e. EEG minus EMG, and we were treating two empty solder pads as failed EMG surgeries. Corrected.
2. **The persistence statistic was wrong until today.** It measured correlation across time gaps, which both hid real sleep and invented fake sleep. Corrected, and validated against synthetic data.
3. **After both corrections, the 2026-08-01 "first real sleep" result in C1 survives and is stronger than we thought** — and a second animal, C2, now also qualifies. Meanwhile six apparent "recoveries" that the buggy statistic produced are false and have been discarded.

---

## 2. What the rig records, and the physical chain

Understanding the failure requires knowing what is in series with the electrode.

```
mouse skull screw / EMG wire   <- implanted, CANNOT be changed without surgery
        |
   head connector               <- animal side
        |
     tether                     <- changing this needs isoflurane
        |
    slip ring                   <- allows the animal to rotate
        |
  C3410 adapter board pads      <- solder joints, RIG SIDE, free to inspect
        |
  RHD2216 headstage             <- 16-channel BIPOLAR amplifier chip
        |
  HDMI/SPI cable -> XDAQ Core   <- digitiser, 1000 Hz
        |
   Allego (Radiens) -> .xdat    <- 32-bit float, sample-interleaved
```

**The RHD2216 is a bipolar chip.** Each channel reports the voltage difference across *its own* pin pair. This single fact caused error #1 below.

Per animal we use **two channels only**:

| Allego label | native index | what it is |
| --- | --- | --- |
| `/1` | port base + 0 | **EEG**, frontal vs parietal, already a difference |
| `/2` | port base + 1 | **EMG**, neck muscle pair, already a difference |
| `/3`, `/4` | base + 2, 3 | **empty pads — no wire is attached to them at all** |

A 64-channel port carries a splitter with **two animals**: the second sits at `base+32`/`base+33` (`/33`, `/34`). A 32-channel port carries one animal. **Recordings exist in both layouts, and in mixed layouts** such as `A:64@0 B:32@64 C:64@96 D:64@160`, so the layout must always be read from the file rather than assumed.

---

## 3. The two errors we found

### 3.1 Error one — the channel map (found 2026-08-01, corrected)

The old pipeline computed `EEG = native0 − native1`.

Because the chip is already bipolar, `native0` **is** the EEG and `native1` **is** the EMG. Subtracting them produced **EEG minus EMG**: a mixture with muscle activity subtracted out of the brain signal. At the same time, the pipeline looked for EMG on `/3`,`/4`, which are bare pads, and recorded **24 "failed EMG surgeries" that never existed**.

> [!check] How we proved `/3`,`/4` carry no wire
> Their impedance is statistically indistinguishable from channels with **no wire attached at all**. From the 2026-08-02 sweep: empty pads `/3,/4` median **6.28 MΩ**, no-wire control `/5–/16` median **4.56 MΩ** — both sit in the open range, whereas a genuinely tied channel (`/17–/32`, shorted to ground) reads **0.038 MΩ**, i.e. ~150× lower. There is nothing on those pads to fail.

**Consequence:** every scoring result produced before 2026-08-01 is invalid, in both directions. That is why re-examining the old recordings was worth doing.

### 3.2 Error two — the persistence statistic (found today, corrected)

Sleep scoring needs a check that the state sequence is *real* and not noise. Ours was: sleep should **persist** — if the animal is asleep now, it is probably still asleep a minute from now. We measured this as the autocorrelation of the sleep indicator at a lag of 15 epochs (= 60 s).

**The bug:** the statistic was computed on the array of *epochs that passed quality control*, which is not continuous in time. Because electrode contact is intermittent, that array is a concatenation of fragments. Index *k* and index *k+15* can be **hours** apart in reality.

It failed in **both directions**:

| case | old value | truth |
| --- | --- | --- |
| Run 2, animal C2 | `r = +0.078` → "NO STRUCTURE" | 250 fragments, median length **4 s**. The test was *impossible to pass*, not failed. |
| 2026-07-13, animal D2 | `r = +0.854` → best number ever recorded | Its longest continuous stretch is **39 minutes of 100% WAKE**. The correlation came from stitching fragments across hours. |

**The fix:** compute the autocorrelation **strictly inside each unbroken block of contact**, then combine across blocks as a weighted mean. Blocks shorter than the lag contribute nothing instead of silently contributing a cross-gap pair. The shuffle control permutes labels *within* each block, preserving block structure and sleep fraction, so it isolates temporal ordering alone.

> [!check] The corrected statistic was calibrated against synthetic data before use
> Alternating states with a known mean bout length, scored by the same code:
>
> | true mean bout | measured `r@1min` |
> | --- | --- |
> | pure noise (4 s) | **−0.035** |
> | 30 s | +0.112 |
> | 2 min | +0.214 |
> | 4 min | +0.510 |
> | 10 min | +0.703 |
>
> It does not fire on noise, and it rises monotonically with bout length. Our threshold `r > 0.30` therefore corresponds to consolidated bouts of roughly **3 minutes or longer**, which is the right scale for real rodent sleep.

---

## 4. Definitions — when is data usable?

These are the exact rules the code applies. Every one exists because of a specific past failure.

### 4.1 The unit of analysis

The recording is cut into **4-second epochs** (standard for rodent sleep staging). Every judgement below is made per epoch, per animal.

### 4.2 The three-part quality gate

An epoch is **usable** only if it passes **all three** tests.

| # | name | rule | what it catches | why the threshold |
| --- | --- | --- | --- | --- |
| 1 | **OPEN** | 55–65 Hz amplitude **< 300 µV** on both EEG and EMG | electrode not connected | An open electrode is a floating antenna. Connected channels sit at **9–90 µV** of mains; open ones sit at **1000–4700 µV**. The separation is ~100× and cleanly bimodal, so 300 µV sits in an empty valley. |
| 2 | **SHORTED** | EEG rms **≥ 25 µV** | dead or shorted channel | A shorted channel sits at 16–21 µV, scores ~100% WAKE, and has zero persistence. Without this test it looks like valid data. This is what wrongly passed animal D2 on 2026-08-01. |
| 3 | **CLIPPED / RAILED** | fraction of samples beyond ±6300 µV **< 0.001** | amplifier saturation | A railed amplifier is a flat-topped waveform. It destroys the band-power ratios that all staging depends on. This caused the **2026-07-15 retraction**, where a "result" came from 1 clean epoch out of 493. |

**Vocabulary, plainly:**

- **Clean** — passes all three. Mains typically < 100 µV, EEG rms 30–150 µV, no railing.
- **Dirty** — passes but marginal: mains 100–300 µV, or occasional railing below the threshold. Usable, treat conclusions cautiously.
- **Open** — no electrical connection. Huge mains. **The dominant failure mode in this project by a wide margin.**
- **Shorted** — connection exists but to the wrong thing (or two electrodes touching). Abnormally *low* amplitude.
- **Clipped / railed** — signal exceeds the amplifier's range and is flat-topped. "Railed" refers to hitting the supply rail; the two words mean the same thing here.

### 4.3 When is a *mouse* scoreable?

Passing the gate is necessary but **not sufficient**. A mouse is scoreable only if **all four** hold:

1. **Enough usable data** — at least 15 minutes, *and* at least 15 minutes inside blocks long enough to test persistence (≥ 124 s each).
2. **Persistence** — within-block `r@1min > 0.30` against a within-block shuffle control. This is the test that says the state sequence is real.
3. **Physiology** — the staging must obey biology, or the labels are meaningless:
   - WAKE has the **highest EMG**
   - NREM has the **most delta power** and the **largest EEG amplitude**
   - REM has the **highest theta/delta ratio** and **low EMG**
4. **Plausible balance** — wake fraction between 15% and 90%. A mouse that scores 97% wake or 5% wake over hours is reporting an artifact.

Plus one order-based check used as supporting evidence: **REM must be entered from NREM**, not from WAKE. No amplitude threshold can manufacture a correct sequence, so this is strong independent confirmation.

> [!warning] The REM *percentage* is not a measurement — do not quote it
> The scorer defines REM as the top 20% of theta/delta among non-wake epochs (`np.percentile(td, 80)`). The REM **share is therefore fixed by construction**. What is real evidence is the REM **entry pattern** (76–96% from NREM in our good animals). The REM percentage is not.

---

## 5. The impedance screen

### 5.1 What it is

Before and after a run we sweep electrode impedance in Allego and read **only the real channels** (`/1`, `/2`, and `/33`, `/34` for the second animal on a splitter). Threshold: **Z < 2 MΩ = connected**, **> 3 MΩ = open**.

Values wobble between sweeps, so we **classify, never quote**: the classification is stable even when the number moves.

### 5.2 Every sweep to date

| sweep | EEG connected | EMG connected | **both** |
| --- | --- | --- | --- |
| 2026-07-31 17:34 | 3/8 (B1, C1, D2) | 5/8 | **2** (C1, D2) |
| 2026-08-02 01:44 (pre-run 2) | 2/8 (B1, C2) | 5/8 | **1** (C2) |
| 2026-08-02 23:34 (post-run 2) | 1/8 (B1) | 6/8 | **0** |

**Per-animal EEG impedance over time (MΩ, `*` = connected):**

| mouse | 07-31 17:34 | 08-02 01:44 | 08-02 23:34 |
| --- | --- | --- | --- |
| A1 | 6.757 | 4.446 | 8.284 |
| A2 | 7.644 | 5.962 | 6.917 |
| B1 | 1.717* | 0.133* | 0.732* |
| B2 | 7.110 | 5.771 | 7.336 |
| C1 | 0.465* | 5.720 | 7.929 |
| C2 | 4.418 | 1.146* | 2.507 |
| D1 | 6.300 | 3.980 | 7.504 |
| D2 | 0.660* | 2.114 | 9.200 |

Two facts leap out:

- **Contact moves on its own, in both directions, over days, with nothing done to the animal.** B1 improved 13× (1.717 → 0.133); C1 went from our best EEG to open (0.465 → 5.720); C2 recovered then lost it again.
- **Across the 21.7-hour Run 2, all 8 EEG channels degraded without exception**, while EMG went 5 better / 3 worse. That asymmetry is not random flipping and points at something systematic in the EEG path over a long run.

### 5.3 What the screen predicts — and what it does not

Tested against Run 2 by pre-registering predictions *before* analysis:

| what was predicted | result |
| --- | --- |
| **which channel works on which animal** (classification) | ✅ correct every time (3 of 3 predictions) |
| **how many usable hours** (yield) | ❌ wrong (ρ = −0.45, degenerate) |

**The screen is a good connectivity classifier and a poor yield predictor.** The clearest counterexample is B1 in Run 2: resting impedance **0.133 MΩ**, the best in the fleet, yet its in-data mains was **2802 µV**, i.e. open-level, for the entire run.

> [!important] Resting impedance is not contact under load
> A channel can measure well at rest and still chatter into uselessness once the animal moves. Use the sweep to decide *which animals are worth running*, not to promise how much data you will get.

Correlation of resting impedance against in-data hum is real but moderate: **ρ = +0.667**.

---

## 6. Noise, hum, grounding, and the rig

### 6.1 Where the 60 Hz comes from

Mains hum enters as a **common-mode** signal — the same voltage on both inputs of the differential pair. A differential amplifier rejects common-mode signals *provided both inputs see the same impedance*. The governing relation we measured earlier:

```
differential_60Hz  ≈  common_mode_level  ×  electrode_impedance_imbalance
```

This was confirmed directly: a 53× impedance ratio produced a 53× hum ratio.

**The practical consequence is the single most useful diagnostic we have:** hum level *is* a readout of contact state.

| state | 55–65 Hz amplitude |
| --- | --- |
| well connected | **9 – 90 µV** |
| open | **1000 – 4700 µV** |

There is almost nothing in between. An open electrode has effectively infinite impedance on one side, the imbalance term explodes, and the channel becomes an antenna.

### 6.2 What we measured across the whole dataset

Median EEG hum across **41 animal-recordings**:

- median **3379 µV**
- below the 300 µV usable threshold: **5 of 41**
- below 100 µV (genuinely quiet): **4 of 41**
- below 30 µV (excellent): **2 of 41**

### 6.3 What has been ruled out

This is important, because it tells us where *not* to spend effort:

| suspect | verdict | evidence |
| --- | --- | --- |
| mains earth / building ground | **exonerated** | no benefit on direct test, twice |
| the splitter | **exonerated** | tested directly without it |
| slip-ring rotation | **exonerated** | hum does not track rotation |
| grounded power brick | **exonerated** | direct test |
| animal ground electrodes | **good, 8/8** | measured |
| the environment generally | **exonerated** | no-wire control pins read **2.8 µV** with zero drift across a full light/dark cycle |
| aluminium foil shielding | **works** | dropped the floor to 12–89 µV per leg. **Do not ground the foil** — that was tried 2026-07-16 and made things worse; the Gen-1 XDAQ Core has no chassis terminal. |

> [!check] The rig itself is capable of excellent data — this is proven
> Recording `allego_1__uid0629-12-05-09` (2026-06-29, one animal): EEG hum **9 µV**, **100% of epochs passed all three gates**, zero open, zero shorted, zero clipped, across **4.55 hours of unbroken contact**. That is a technically flawless recording.
>
> It is not scoreable — the animal was 96.7% awake with a **2.56-hour continuous wake bout**, almost certainly acclimatisation after first tethering — but it settles the engineering question. **When the electrode is connected, this rig produces clean EEG.** The problem is upstream of everything we build.

### 6.4 The remaining open question on noise

> [!danger] The paragraph below used the retracted frontal-vs-parietal framing. Corrected 2026-08-03.
> There is no frontal-vs-parietal asymmetry. That reading came from the wrong
> channel map. What is actually open is the **EEG channel `/1`**, while the
> **EMG channel `/2`** works. The frontal-sinus hypothesis was built on the
> mis-mapping and **has no evidence behind it**; it should not be repeated.

The **EEG channel is open on nearly every animal, while the EMG channel on the same connector works**. There are now **three** candidate explanations, and our data does not yet separate them:

1. **A cold solder joint on C3410 pads 0/1**, or a broken EEG slip-ring wire. Free to test, not yet done.
2. **The dura pins have dislodged.** This is the literature's default expectation: Hsieh et al. (*eNeuro* 2024) report that **82% of epidural preparations lose at least one electrode within three weeks**, with peak dislodgement in week 1. Our measured one-way, irreversible degradation (EEG impedance rose on 8 of 8 animals across Run 2, none improved) is exactly that failure's shape.
3. Some combination of the two.

Animals A1, C1 and D1 are the ideal test cases — their EMG works perfectly through the *same* tether, slip ring, board, headstage and port, which proves that **shared infrastructure** is good.

> [!warning] What that proof does and does not buy us
> It isolates the fault to the EEG-specific segment. It does **not** identify the
> solder, because EEG and EMG do not share an electrode: **EEG is a dura pin, EMG
> is a wire anchored in muscle**, and only the former has a published failure rate
> — a very high one. The bench test is still the right next step, but treat it as
> a **discriminator between hypotheses 1 and 2**, not as confirmation of 1.
> Full analysis: [[2026-08-03-literature-check-impedance-and-electrode-failure]].

---

## 7. The analysis code — what each piece does and why

All scripts live in the vault under `02-procedures/eeg-data-analysis/scripts/`.

### 7.1 `rescore-v2-2026-08-03/rescore_v2.py` — **the current scorer, use this one**

Single self-contained tool, two passes.

**Pass 1, feature extraction** (the expensive part — it must read the whole file):

- Reads layout from the recording's own metadata (`sensors_by_port`), so 32-ch, 64-ch and mixed layouts are all handled correctly. **It never assumes 64 channels per port.**
- Applies the corrected map: `/1` = EEG, `/2` = EMG, used directly with no subtraction.
- Filters: EEG 0.5–30 Hz, EMG 10–300 Hz, mains 55–65 Hz (all 4th-order Butterworth, zero-phase).
- Per 4-second epoch, computes: delta (0.5–4 Hz), theta (6–9 Hz), total (0.5–30 Hz) band power; EEG and EMG rms; EEG and EMG mains amplitude; fraction of railed samples.
- Caches results, so re-scoring is instant and only the first pass touches the 566 GB.

> [!danger] `NPERSEG = 2048`. Do not lower it.
> This sets the frequency resolution to 0.49 Hz. At `nperseg = 512` the resolution becomes 1.95 Hz, the theta band 6–9 Hz spans a **single FFT bin**, and integrating over one point returns **exactly zero** — silently destroying every REM measurement without raising an error.

**Pass 2, gating and scoring:**

- Applies the three-part gate (§4.2).
- Finds unbroken blocks of good contact.
- **WAKE threshold: Otsu's method on log EMG rms, computed per animal.** Otsu finds the split that best separates two populations by maximising between-class variance. **Never reuse one animal's threshold on another** — doing so is what wrongly passed D2 on 2026-08-01.
- REM: top 20% of theta/delta among non-wake (constructed — see §4.3 warning).
- **Within-block persistence** at 1, 5 and 10 minutes, each with its own shuffle control.
- Physiology check, REM-entry order, bout-length statistics.
- Emits a verdict with the **reason** for rejection, and a machine-readable JSON.

### 7.2 Supporting scripts

| script | purpose |
| --- | --- |
| `contact-state-2026-07-31/longrun_coarse.py` | Duty-cycle survey. Samples 10 s every 60 s, so it can cross 100 GB quickly. ⚠️ Flip counts from it are **lower bounds** — a flip inside the unobserved 50 s is invisible. |
| `contact-state-2026-07-31/gate_and_score_all.py` | **Superseded.** Contains the persistence bug of §3.2. Kept only for reproducing historical numbers. |
| `frame_integrity_check.py` (backend/scripts) | Video-side integrity: confirms no frames are lost between camera and file. |

### 7.3 Reproducing everything in this report

```bash
cd Monitoring_project_obsidian_vault/02-procedures/eeg-data-analysis/scripts/rescore-v2-2026-08-03
export RESCORE_CACHE=/tmp/rescore_cache/
python3 rescore_v2.py allego_1__uid0731-18-06-37 --json out.json
```

First run reads the file (minutes to ~15 min depending on size); subsequent runs are instant from cache.

---

## 8. How to read your results

A decision tree for the output table.

**`INSUFFICIENT`** — under 15 minutes of usable data, or the usable data is too fragmented to test. *This is not a negative result. It means the electrode was not connected long enough to ask the question.* Check the gate columns to see which of the three tests rejected the epochs.

**`REJECT: within-block r ≤ 0.3`** — there is enough data, but the state sequence does not persist. The animal's apparent state is flipping faster than biology allows, which means the staging is tracking noise, not sleep. Almost always caused by chattering contact.

**`REJECT: physiology FAIL`** — the states do not obey biology (e.g. NREM does not have more delta than WAKE). The labels are not meaning what they claim.

**`REJECT: implausible wake`** — >90% or <15% wake. Usually a misplaced EMG threshold, or a genuinely unusual animal state (as in the 2026-06-29 acclimatisation recording).

**`SCOREABLE`** — passed all four criteria. Only then may state percentages be reported.

**Cross-checks worth doing every time:**

- **Longest block** should be tens of minutes. If it is 4 seconds, no timing statistic on that animal means anything.
- **`r` should decay smoothly** from 1 min to 5 min to 10 min. C1 shows +0.744 → +0.583 → +0.435, which is what genuine sleep architecture looks like. If `r@1min` is high but `r@5min` collapses to zero, suspect short-timescale noise.
- **Shuffle control should be ≈ 0.** Ours are all within ±0.05, which confirms the statistic is not structurally biased.
- **REM entries from NREM** should be well above 70%.

---

## 9. Findings — the complete table

Every substantive recording, scored with the corrected map and the corrected statistic.

| recording | date | hours | animals | scoreable |
| --- | --- | --- | --- | --- |
| `allego_1__uid0629-12-05-09` | 06-29 | 4.55 | 1 | 0 (perfect signal, awake animal) |
| `allego_0__uid0702-19-06-53` | 07-02 | 14.23 | 2 | 0 |
| `allego_0__uid0710-08-53-31` | 07-10 | **72.22** | 8 | **0** |
| `allego_0__uid0713-12-59-49` | 07-13 | 20.05 | 8 | 0 |
| `allego_0__uid0715-18-58-54` | 07-15 | 2.74 | 7 | 0 |
| `allego_1__uid0715-22-47-21` | 07-15 | 10.99 | 7 | 0 |
| **`allego_1__uid0731-18-06-37`** | **07-31** | **27.90** | 8 | **2 — C1 and C2** |
| `allego_2__uid0802-01-46-57` | 08-02 | 21.74 | 8 | 0 |

### 9.1 The data we actually have

**C1 — the strongest result in the project**

| | |
| --- | --- |
| usable data | **8.73 h**, essentially all of it in one block |
| longest unbroken block | **485.7 min = 8.1 hours** |
| persistence | **r@1min +0.744**, r@5min +0.583, r@10min +0.435 (shuffle ≈ 0.00) |
| physiology | **PASS** |
| WAKE / NREM / REM | 64.4 / 31.2 / 4.4 % |
| bout lengths | NREM median 8 s, max **348 s**; WAKE max **2208 s** |
| REM entries | 178, of which **76.4% from NREM** |

The physiology ordering is textbook: WAKE EMG 49.2 > NREM 15.5; NREM delta 41.0% > WAKE 26.5%; NREM EEG amplitude 68.0 > WAKE 50.5; REM theta/delta 1.85 > NREM 0.32.

**C2 — genuine independent replication**

| | |
| --- | --- |
| usable data | 4.02 h gated, **1.69 h** inside testable blocks |
| longest unbroken block | 62.1 min |
| persistence | **r@1min +0.532**, r@5min +0.517 (shuffle ≈ 0.00) |
| physiology | **PASS** |
| WAKE / NREM / REM | 56.3 / 35.7 / 8.1 % |
| REM entries | 102, of which **78.4% from NREM** |

**D2 — correctly rejected**, independently confirming the 2026-08-02 withdrawal: `r@1min = 0.250` (below threshold) *and* physiology fails, because NREM delta (42.1%) is indistinguishable from WAKE delta (41.6%) and WAKE EEG amplitude exceeds NREM's.

### 9.2 Six false recoveries, discarded

Using the buggy statistic, re-examining the old recordings appeared to recover **~5.6 mouse-hours** across five animals, including sleep in the 72-hour and 20-hour runs. **All of it evaporated** under the corrected statistic:

| recording / animal | old `r@1min` | corrected | why it was fake |
| --- | --- | --- | --- |
| 07-13 D2 | **+0.854** | **−0.064** | longest real block is 39 min of 100% WAKE |
| 07-13 D1 | +0.713 | −0.058 | NREM bouts median 12 s — chattering, not sleep |
| 07-10 D2 (72 h run) | +0.677 | −0.004 | 177 fragments |
| 07-15 A2 | +0.385 | +0.167 | below threshold once gaps removed |
| 07-15 D1 | +0.446 | +0.095 | also fails REM-entry order (only 71% from NREM) |
| 07-02 A2 | +0.383 | +0.231 | below threshold |

This is the clearest possible demonstration of why the statistic had to be fixed: it would have produced a paper-level claim of sleep in the 72-hour run that is not there.

### 9.3 Why the failures failed

Dominant rejection reason, per animal-recording (n = 41):

- **OPEN electrode — 36 of 41.** Median hum 3379 µV against a 300 µV limit.
- SHORTED — 3
- Everything else — 2

**The bottleneck is electrical connection, and nothing else is close.**

---

## 10. What this means

1. **We can record sleep.** C1 and C2 prove the whole chain works end to end — surgery, tether, amplifier, digitiser, and analysis — when contact holds.
2. **The rig is not the problem.** 9 µV hum and 100% gate pass on 2026-06-29 settles that. Environmental causes are closed.
3. **Contact is the problem, and it is intermittent, not static.** It changes over days without intervention, in both directions, and degrades within a long run.
4. **Yield is currently ~10.4 scoreable mouse-hours out of roughly 174 animal-hours recorded**, i.e. about **6%**. Every improvement in contact reliability converts almost linearly into data.
5. **Two of eight animals gave data on the one good day.** That is not a hopeless yield if contact can be stabilised — it is the difference between one usable run in eight and most runs being usable.

---

## 11. Recommendations, in cost order

**Tier 1 — free, no animal contact, not yet done.** Bench-test the accessible chain on A1, C1 and D1. Their EMG works perfectly through the same tether, slip ring, board, headstage and port, which proves that shared path is good. So:
- DMM continuity from **C3410 pads 0 and 1** back through the slip-ring wiring, compared against pads 2 and 3, which are known good.
- Inspect and reflow the pad 0/1 solder joints under magnification.
- Swap the headstage to a known-good one and re-sweep.
- Swap the port and re-sweep.

Only if all four come back clean is the fault upstream of the slip ring.

**Tier 1 — free, procedural.** Take an impedance sweep before **and** after every run. Two sweeps bracketing a recording is what distinguishes progressive degradation from random flipping, and it is how we discovered that all 8 EEG channels declined across Run 2.

**Tier 1 — free, analytical.** Report `INSUFFICIENT` honestly rather than as a negative result, and never report state percentages without persistence, physiology and plausibility all passing.

**Tier 2 — expensive.** Changing a tether requires isoflurane, stresses the animal, and ruins a batch mid-experiment. Only with a specific, pre-argued reason.

**Tier 3 — impossible for existing animals.** Implanted wires and electrodes cannot be reseated. Changing them means new mice.

> [!danger] "Reseating an electrode" is not a thing
> Once implanted, electrodes and EMG wires cannot be reseated. Any plan that depends on it is invalid. This was a genuine misconception in our own notes until 2026-08-02.

---

## 12. Limitations and open questions

- **Animal identity is positional.** "D2" in the 07-10 run is not necessarily the same animal as "D2" on 07-13. Cross-run statements need the cage records, which are not in the vault.
- **The frontal-sinus hypothesis is unconfirmed** and has a cheaper competing explanation (§6.4) that has not been excluded.
- **We have no light-phase sleep data from a living EEG.** The animal-room light schedule is still undocumented, and Run 2 (21.7 h) was too short for the pre-registered light-phase test, which required ~29 h.
- **`r > 0.30` is a threshold, not a law.** Calibration (§3.2) shows it corresponds to ~3-minute bouts. An animal with genuinely fragmented sleep would be rejected. We accept that conservatism deliberately, given two prior retractions.
- **The 96.7%-wake recording of 2026-06-29 is unexplained** beyond "probably acclimatisation". It would be worth repeating a first-tethering recording to see whether that pattern is systematic.
- **Only C2 has been measured for pre/post impedance against yield.** One run is not enough to characterise the screen properly.

---

## 13. Note on the video system

Separate from the EEG chain, but it affects the experiment. Video is recorded by Frigate on the NVR from Raspberry Pi cameras.

- **Frame integrity is proven.** A 14.97-hour overnight recording produced **808,365 frames across 5388 segments with zero frame loss** and no timestamp gaps.
- **The camera clock drifts +204 ppm**, i.e. **+8.8 s per 12-hour night**. This is measured, not assumed. It is ~18× the ±0.5 s alignment budget, so video-EEG synchronisation requires hardware sync pulses, not timestamps.
- **A recording bug is fixed but not yet live.** Frigate deletes 10–20 s from the end of every recording when recording is switched off. The fix is written and unit-tested; it activates on the next daemon restart. Full detail in [[2026-07-27-video-eeg-sync-recording-architecture]].
- **Three EEG runs have no video at all**, because automatic video start is still disabled pending that fix.

---

## Appendix — key file locations

| what | where |
| --- | --- |
| current scorer | `02-procedures/eeg-data-analysis/scripts/rescore-v2-2026-08-03/rescore_v2.py` |
| superseded scorer | `02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31/gate_and_score_all.py` |
| raw recordings | `~/radix/data/*.xdat` + `.xdat.json` metadata |
| impedance sweeps | `~/Downloads/impedance measurments/*.csv` |
| per-recording results | `/tmp/rescore_cache/json/*.json` |
| channel-map correction | [[2026-08-01-channel-mapping-correction-first-sleep]] |
| contact intermittency | [[2026-07-31-contact-intermittency-no-wire-control]] |
| Run 2 pre-registration | [[2026-08-02-run2-preregistration]] |

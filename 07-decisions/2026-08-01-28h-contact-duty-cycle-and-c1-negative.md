---
tags: [decision, eeg, contact-intermittency, duty-cycle, sleep-scoring, negative-result, methods, critical]
created: 2026-08-01
status: active
priority: critical
---

# 2026-08-01 — 27.9 h run: grounds perfect, 78 % of leg-time OPEN, and C1's clean EEG shows NO sleep structure

> [!danger] ⚠️ MAJOR RETRACTION 2026-08-01 — THE CHANNEL MAP USED HERE WAS WRONG
> This document was written using `EEG = native0 − native1` and `EMG = native2 − native3`. **Both are wrong.** The RHD2216 is BIPOLAR: `native0` (Allego `/1`) is ALREADY the EEG, `native1` (`/2`) is ALREADY the EMG, and natives 2/3 (`/3`,`/4`) are **empty pads with no wire on them by design**.
>
> **What is RETRACTED from this document:**
> - ❌ "EMG failed 23/24 / 16/16 legs" — those were **empty pads**, never electrodes. **EMG works on 5 of 8 mice.** The surgeries were fine.
> - ❌ "ZERO scoreable mice / zero scoreable data" — there are **21.0 scoreable mouse-hours** (C1 8.7 h, C2 7.0 h, D2 5.3 h).
> - ❌ "C1 shows NO sleep structure" — C1 shows **textbook sleep architecture**: WAKE 66.8 %, NREM 29.3 %, REM 3.9 %, all physiology correct, persistence r=+0.80 at 1 min.
> - ❌ Duty cycle "78.7 % open" — **61.6 %** on the 16 real channels.
> - ❌ The "frontal vs parietal" framing — it was **EEG vs EMG channels**.
>
> **What STANDS:** the no-wire control method, the grounds result (2.8 µV, no drift over 27.9 h), environmental causes closed, and contact intermittency / one-way degradation — though it is the **EEG** channel that fails, on 8 of 8 mice.
>
> Full correction: [[2026-08-01-channel-mapping-correction-first-sleep]]

> [!warning] SECOND-LAYER UPDATE 2026-08-03 — the retraction above is right in direction, but its replacement numbers are themselves superseded
> The title of this document is still wrong and the corrected figures quoted in
> the retraction have since changed again.
>
> - ❌ "21.0 scoreable mouse-hours (C1 8.7, C2 7.0, D2 5.3)" → the persistence
>   statistic was measured **across contact gaps**. Correct total is **~11.1 h**:
>   **C1 8.73 h and C2 2.34 h. D2 is rejected** (`r = 0.25`).
> - ❌ "persistence r = +0.80 at 1 min" → computed within unbroken blocks only,
>   C1 is **r@1min = +0.761** (shuffle +0.011), decaying smoothly to +0.493 at
>   10 min. Still a strong positive, just not that number.
> - ❌ "REM 3.9 %" → **never quote a REM percentage.** It is fixed by
>   construction; REM is not reliably separable with this montage.
> - ✅ **"C1 shows NO sleep structure" remains firmly retracted, and C1 is now
>   the best-validated result in the project** — it additionally matches
>   published C57BL/6 circadian norms (66.9 % asleep in the light phase vs
>   ~70 % expected), a check that uses none of our thresholds.
>
> Current numbers and the two-run comparison: [[2026-08-03-two-8-mouse-runs]].
> Method: [[pipeline/README]].


> [!abstract] TL;DR
> First multi-hour run since the contact problem was understood. `allego_1__uid0731-18-06-37`, **27.9 h**, 105 GB, 8 mice, 32 legs, started 2026-07-31 18:06 KST.
>
> - ✅ **Animal grounds and amplifier floor were FLAWLESS for 27.9 h.** 16 control pins, median 2.8 µV, max 5.3. Zero drift across a full light/dark cycle. The rig and the room are settled, permanently.
> - 🔴 **78.7 % of all leg-time was OPEN.** Every frontal leg and all 16 EMG legs spent most or all of the run disconnected.
> - 🔴 **TWO failure modes**, and the quiet one is more worrying: **one-way degradation** (C1 frontal connected 0 → 8.73 h then open for the remaining 19 h, never recovers; D2 frontal the same at 5.30 h) versus **chattering** (B1 frontal flipped 372 times).
> - ⚠️ **C1's 8.7 h window is genuinely clean — 99.9 % of epochs have ZERO clipped samples — but it shows NO SLEEP STRUCTURE.** No bimodality, bout lengths identical to random, flat hourly profile. **The project still has ZERO scoreable data.**
> - **Yield: 8.7 usable EEG-pair hours out of 223 mouse-hours recorded. Zero scoreable mice**, because no animal had a working EMG pair at any moment.

---

## 1. Why this run existed

[[2026-07-31-contact-intermittency-no-wire-control]] established that electrode legs are OPEN rather than high-impedance, and that contact state flips on its own. What it could not establish was **how often**. Intermittency is a time-domain phenomenon and every measurement to that point was a snapshot of 60 to 101 seconds.

This run was designed to answer four questions:
1. What fraction of time is each leg actually usable (duty cycle)?
2. How often does state flip, and do flips cluster (shared cause) or scatter (independent)?
3. Do the animal grounds hold for a full day?
4. Does C1's clean EEG pair survive for hours, or was 101 s a lucky interval?

It answered all four. Question 4's answer is the bad one.

---

## 2. The data

| | |
| --- | --- |
| file | `~/radix/data/allego_1__uid0731-18-06-37` |
| start | 2026-07-31T18:06:37 KST (`09:06:37Z`) |
| duration | **100 444.16 s = 27.90 h** |
| size | 105 276 613 632 bytes (105 GB) |
| shape | 100 444 160 samples × 262 channels, `<f4` little-endian |
| sample rate | 1000 Hz |
| channels | 256 primary + 2 aux + 2 din + 2 dout |
| ports | A, B, C, D each `hstg__passthrough_64` / `probe__default_8x8`, 64 ch |
| selected | 32 legs, natives 0-3 and 32-35 within each port's 64-channel block |

Config verified from the file's own metadata before any analysis, not assumed. All 32 legs present at the correct natives.

---

## 3. METHODS — and why each choice was made

> [!important] The analysis code is IN THE VAULT
> `02-procedures/eeg-data-analysis/scripts/contact-state-2026-07-31/`
> - `longrun_coarse.py` — pass 1, extracts the state timeline from the 105 GB file
> - `summarize_states.py` — duty-cycle table, state segments, threshold sensitivity
> - `c1_window.py` — pass 2, full-rate epoch table for C1's connected window
> - `c1_sleep_structure.py` — the four sleep-structure tests
>
> Intermediates (`longrun_coarse.npz`, `c1_window.npz`) are in the session scratchpad and are cheap to regenerate.

### 3.1 Reading a 105 GB file: why SAMPLED, not continuous

**First attempt failed.** I wrote a continuous pass computing 1-second band power on every second of all 48 channels of interest. It reached **0.6 % in 90 seconds**, implying roughly **4 hours** to finish. Killed it.

The bottleneck is unavoidable I/O: `.xdat` is sample-interleaved, so reading any subset of columns still pulls every byte of all 105 GB off disk (measured ~630 MB/s).

**The fix: sample instead of stream.** `longrun_coarse.py` analyses a **10 s window every 60 s**, giving 1674 windows over 27.9 h and reading about 1/6 of the file.

**Why this is legitimate for THIS question, and where it is not:**
- ✅ Duty cycle: a 10 s sample every minute is an unbiased estimator of the fraction of time in each state. This is the headline number and it is sound.
- ✅ Long segments: transitions lasting minutes to hours are resolved exactly.
- ⚠️ **Flip COUNTS are a LOWER BOUND.** Any flip that starts and ends inside the unobserved 50 s is invisible. B1 frontal's "372 flips" means **at least** 372. This limitation is stated wherever a flip count appears.
- ❌ Sub-second transitions cannot be timed. That is why pass 2 exists: once a window of interest is identified, re-read it at full 1 kHz.

This two-pass design (cheap survey, then targeted full-rate zoom) is the reusable pattern for files this size.

### 3.2 Measuring "is this leg connected"

**Mains hum as the 55-65 Hz BAND, never a single 60.00 Hz bin.** Mains is not exactly 60.00 Hz and drifts, so energy smears across bins. I made the single-bin error earlier in this investigation and it understated hum by 4 to 5×.

Filters are 4th-order Butterworth as SOS, applied with `sosfiltfilt` (zero-phase, so no group-delay smearing of transition times). Bands: 55-65 Hz (mains), 0.5-45 Hz (biology). Each 10 s window is padded by 5 s on each side before filtering and the pad is discarded, so filter transients never enter a reported number.

**Why hum works as a connection test:** an open input is a floating antenna terminating a ~36 cm analog run, so it collects mains hum at hundreds to thousands of µV. A connected electrode is a low-impedance path to tissue and collects almost none. The physics is in [[floating-cm-vs-contact-reconciliation]]; the calibration against physically-unconnected pads is in [[electrode-connection-state-test]].

### 3.3 The OPEN threshold, and how sensitive the verdict is to it

`OPEN_UV = 300 µV` on 55-65 Hz band RMS. Chosen because the 2026-07-31 distribution was sharply **bimodal** — legs landed either below 150 µV or above 500 µV, with exactly one value in between (525) — so 300 sits in an empty gap.

**I checked rather than asserted this.** Sweeping the threshold:

| threshold | % of all leg-windows OPEN |
| --- | --- |
| 150 µV | 80.3 % |
| 200 µV | 79.6 % |
| **300 µV** | **78.7 %** |
| 400 µV | 78.0 % |
| 600 µV | 76.8 % |
| 1000 µV | 67.5 % |

⚠️ **HONEST QUALIFICATION.** The headline is robust (78.7 % vs 76.8 % across a 4× threshold change), and legs with clean binary behaviour do not move at all — C1 frontal reads 68.8 / 68.8 / 68.7 % at 150 / 300 / 600 µV, A1 parietal 0.0 % at every threshold. **But five legs ARE threshold-sensitive**, because they spend their time near the boundary by nature. These are exactly the chattering legs:

| leg | @150 | @300 | @600 |
| --- | --- | --- | --- |
| B1/front | 66.1 | 61.8 | 54.7 |
| B2/EMG+ | 57.1 | 44.4 | 30.7 |
| B2/EMG− | 97.9 | 88.0 | 68.9 |
| C2/front | 84.5 | 74.4 | 61.4 |
| D2/pariet | 11.5 | 0.1 | 0.0 |

**Do not quote a duty cycle for those five to better than about ±15 percentage points.** For all other legs the number is threshold-independent.

### 3.4 "Not open" does NOT mean "usable"

A second threshold, `BIO_UV = 25 µV` on 0.5-45 Hz band RMS, gates the `%bio` column. This exists because of a trap found on 2026-07-31: **a leg shorted to ground is QUIETER than a good one** and would otherwise score as the best channel on the rig. Usable requires low hum **and** signal present.

### 3.5 Control channels, carried through the whole run

16 internally-tied floor pins (2 per headstage, natives 20, 26, 52, 58 within each port block) were analysed identically alongside the legs. They are the running check that the amplifier and the animal grounds have not drifted. **A control set that runs for the whole experiment is what turns "the numbers look odd" into "the numbers are odd and here is proof it is not the instrument".**

### 3.6 Pass 2 and the anti-2026-07-15 gate

`c1_window.py` re-reads C1's frontal and parietal (natives 128, 129) at full 1 kHz for 0 → 8.70 h, builds the bipolar `front − pariet`, and computes 10 s epochs: Welch PSD (`nperseg=1024`), band powers for delta 0.5-4, theta 5-9, sigma 10-15, total 0.5-45 Hz, plus rms, mains, and **clipped-sample fraction against the ±6390 µV rail**.

> [!danger] GATE 0 — clipped epochs are excluded BEFORE anything is computed
> This is the 2026-07-15 lesson, encoded. A railed amplifier is non-linear and its spectrum is meaningless. Every downstream statistic is conditioned on clean epochs, and **the clean fraction is reported alongside every result**. `c1_sleep_structure.py` exits with `UNSCOREABLE` below 60 clean epochs rather than falling back to dirty data.

---

## 4. RESULTS

### 4.1 The grounds were flawless for 27.9 hours

| | |
| --- | --- |
| 16 control pins, median | **2.8 µV** |
| p99 | 4.0 µV |
| max over 27.9 h | 5.3 µV |
| per-headstage medians | 2.5, 2.6, 2.6, 2.6, 2.6, 2.7, 2.7, 2.7, 2.7, 2.8, 2.9, 3.0, 3.0, 3.0, 3.1, 3.1 |

All eight headstages identical, no drift across a full light/dark cycle.

> [!quote] Paper-ready
> Amplifier noise floor and animal ground integrity were monitored continuously via internally tied unused inputs across a 27.9 h recording, yielding a median 55-65 Hz band amplitude of 2.8 µV (maximum 5.3 µV) with no drift, confirming that observed channel failures were not attributable to instrumentation or grounding.

**This closes the environmental question for good.** Earth, room, splitter, grounding: all exonerated, now over a full day rather than a minute.

### 4.2 Duty cycle, all 32 legs

`%OPEN` = fraction of windows above 300 µV. `%bio` = fraction both connected and carrying signal. `flips` = **lower bound** (see §3.1).

| leg | med µV | %OPEN | %bio | flips | clip% |
| --- | --- | --- | --- | --- | --- |
| A1/front | 3990 | 100.0 | 0.0 | 0 | 14.98 |
| **A1/pariet** | **6** | **0.0** | 42.5 | 0 | 0.00 |
| A1/EMG+ | 4017 | 100.0 | 0.0 | 0 | 1.30 |
| A1/EMG− | 3431 | 100.0 | 0.0 | 0 | 5.19 |
| A2/front | 4267 | 100.0 | 0.0 | 0 | 8.58 |
| A2/pariet | 4041 | 100.0 | 0.0 | 0 | 18.62 |
| A2/EMG+ | 4580 | 100.0 | 0.0 | 0 | 6.47 |
| A2/EMG− | 3882 | 100.0 | 0.0 | 0 | 8.54 |
| B1/front | 789 | 61.8 | 38.2 | **372** | 1.00 |
| B1/pariet | 4165 | 99.3 | 0.7 | 8 | 8.91 |
| B1/EMG+ | 1631 | 100.0 | 0.0 | 0 | 0.00 |
| B1/EMG− | 1010 | 100.0 | 0.0 | 0 | 0.00 |
| B2/front | 4177 | 100.0 | 0.0 | 0 | 5.42 |
| B2/pariet | 3940 | 95.8 | 1.5 | 58 | 10.97 |
| B2/EMG+ | 209 | 44.4 | 37.5 | 147 | 0.18 |
| B2/EMG− | 933 | 88.0 | 11.5 | 110 | 0.17 |
| **C1/front** | 4252 | **68.8** | 31.2 | 3 | 5.65 |
| **C1/pariet** | **6** | **0.0** | 35.4 | 0 | 0.00 |
| C1/EMG+ | 958 | 100.0 | 0.0 | 0 | 0.00 |
| C1/EMG− | 951 | 100.0 | 0.0 | 0 | 0.00 |
| C2/front | 916 | 74.4 | 22.9 | 165 | 0.20 |
| C2/pariet | 25 | 4.2 | 46.1 | 80 | 0.00 |
| C2/EMG+ | 1052 | 100.0 | 0.0 | 0 | 0.00 |
| C2/EMG− | 4475 | 100.0 | 0.0 | 0 | 2.68 |
| D1/front | 4613 | 100.0 | 0.0 | 0 | 5.48 |
| **D1/pariet** | **8** | **0.0** | 52.5 | 0 | 0.00 |
| D1/EMG+ | 2932 | 100.0 | 0.0 | 0 | 0.00 |
| D1/EMG− | 4246 | 100.0 | 0.0 | 0 | 6.12 |
| D2/front | 2722 | 81.1 | 16.5 | 11 | 4.67 |
| **D2/pariet** | 63 | 0.1 | 60.2 | 2 | 0.00 |
| D2/EMG+ | 3764 | 100.0 | 0.0 | 0 | 6.79 |
| D2/EMG− | 3457 | 100.0 | 0.0 | 0 | 10.34 |

**Frontal versus parietal, reproduced over 27.9 h on 8 animals:** parietal legs 0.0 to 4.2 % open, frontal legs 62 to 100 % open, **all 16 EMG legs 88 to 100 % open**.

### 4.3 TWO failure modes

**Mode A — one-way degradation. This is the new and more worrying finding.**

```
C1/front   CONN   0.00h ->  8.10h   (486 min)
           CONN   8.12h ->  8.73h   ( 37 min)
           OPEN   8.73h -> 27.88h   (1149 min, NEVER RECOVERS)

D2/front   CONN   0.00h ->  4.23h   (254 min)
           CONN   4.37h ->  5.30h   ( 56 min)
           OPEN   5.30h -> 27.88h   (~1350 min, NEVER RECOVERS)
```

Two independent legs on two animals, both connected → open, both irreversible. **Random mechanical make/break would go both ways. This is directional**, which suggests something progressive: drying, creep, or fatigue.

**Mode B — chattering.** B1 frontal ≥372 flips in segments of 4 to 44 min; C2 frontal ≥165; B2 EMG+ ≥147.

**The two modes are not the same fault and probably need different fixes.**

### 4.4 C1's window is clean — the cleanest data this project has produced

3131 epochs of 10 s over 8.70 h:

| | |
| --- | --- |
| **clean epochs (0 % clipped)** | **3129 / 3131 = 99.9 %** |
| mains on bipolar | median 10.8 µV, p90 13.1 |
| rms 0.5-45 Hz | median 62.5 µV (p10 53.8, p90 81.7) |
| delta as % of 0.5-45 | 33.3 % |
| delta/theta | median 1.76 (p10 0.90, p90 3.76) |

> [!success] Compare with the 2026-07-15 retraction
> That result died because only **1 of 493** epochs was clean. Here it is **3129 of 3131**. This window is not that failure mode.

### 4.5 🔴 But it shows NO SLEEP STRUCTURE

Four tests, three negative, one positive.

**TEST 1 — bimodality: NEGATIVE.** log10(delta/theta) is a single smooth peak centred near +0.2, mildly right-skewed. Sleep/wake should produce two modes.

**TEST 2 — temporal persistence: REAL BUT WRONG SCALE.**

| lag | r |
| --- | --- |
| 10 s | +0.410 |
| 30 s | +0.314 |
| 60 s | +0.212 |
| 120 s | +0.086 |
| 300 s | +0.036 |
| 600 s | +0.001 |
| shuffle control, 10 s | **+0.011** |

Structure is far above the shuffle control, so it is real. But it decays to nothing within ~10 min, and mouse NREM bouts last minutes.

**TEST 3 — bout length: NEGATIVE, and this is the decisive one.**

```
high-delta runs: n=508  median 20 s  max 540 s
low-delta  runs: n=509  median 20 s  max 240 s
RANDOM EXPECTATION:     median 20 s
```

**Bout lengths are exactly what random epoch-to-epoch switching produces.** There are no states here.

**TEST 4 — amplitude/delta covariation: POSITIVE.**

| d/t quartile | rms | delta % |
| --- | --- | --- |
| 1 | 58.7 µV | 23.7 |
| 2 | 59.1 µV | 30.3 |
| 3 | 63.1 µV | 36.6 |
| 4 | **75.2 µV** | **46.5** |

Amplitude rises with delta content, the correct physiological direction — synchronised cortical activity is both slower and bigger. **Noise does not do this.** So the channel is plausibly real EEG even though it shows no states.

**Hourly profile: FLAT.** Across 8.7 h, rms 59.9-69.1 µV, delta 29.2-38.3 %, delta/theta 1.42-2.23. No trend, no circadian modulation.

### 4.6 Verdict on the biology

**Clean, physiological-looking EEG. NOT a demonstration of sleep. The project still has ZERO scoreable data.**

Two honest caveats on the negative:
1. **C1's EMG legs were open 100 % of the run.** Sleep cannot be scored from EEG alone; delta/theta by itself is a weak classifier. The montage ([[allego-electrode-setup-sleep64]], Iwasaki/Funato/Yanagisawa 2021) requires EEG **and** EMG.
2. **18:06 → 02:50 is the dark phase**, when mice are largely awake, so few NREM epochs is partly expected.

⚠️ **But the complete absence of bout structure is more than those two caveats explain.** A mouse awake in the dark phase still has sleep bouts. I am recording this as a negative result, not as "inconclusive pending EMG".

---

## 5. Decisions

1. ✅ **Environmental causes are CLOSED.** 27.9 h of flat 2.8 µV control pins across a full light/dark cycle. Do not revisit earth, room, splitter or grounding without new evidence.
2. ➡️ **One-way degradation (Mode A) is the priority lead.** Two independent legs degraded connected → open over hours and never returned. Inspect C1's and D2's frontal connections physically while the failure is fresh.
3. ➡️ **EMG needs its own bench investigation.** 16/16 open over 27.9 h, on top of 23/24 on 2026-07-31. Nothing in the EEG story explains it, and **it alone guarantees zero scoreable animals**.
4. 🛑 **Still NO new surgeries.** Nothing here re-implicates the implants.
5. ⏳ **Validate the Allego impedance check against a known 1 MΩ resistor.** Carried over from 2026-07-31, still not done, still 5 minutes.
6. 📉 **Record the real yield: 8.7 usable EEG-pair hours from 223 mouse-hours = 3.9 %. Zero scoreable mice.**

---

## 6. Questions this run CLOSED

- ✅ *Do the grounds hold for a full day?* Yes, flawlessly.
- ✅ *Does C1 hold for hours?* **No.** 8.7 h, then permanent failure.
- ✅ *Do flips cluster or scatter?* Both, and they are two distinct modes.
- ✅ *What is the duty cycle?* 78.7 % of leg-time open; 3.9 % scoreable-pair yield.

## 7. Still open

- **What drives Mode A one-way degradation.** Directional and irreversible over hours. Drying, creep and fatigue are all consistent; nothing distinguishes them yet.
- **Whether Mode A and Mode B share a cause.**
- **Why EMG fails at 16/16.**
- **Whether C1's clean window contains sleep that a proper EEG+EMG scorer would find.** My delta/theta test is weak; the bout-length result argues no, but a scorer with EMG is the real test and we cannot run one.
- **Is the Allego impedance check itself trustworthy?** Never validated.
- Flip counts are lower bounds; a full-rate pass on a selected hour would tighten them if the number ever matters.

## Related

- [[2026-07-31-contact-intermittency-no-wire-control]] — the run this tests
- [[electrode-connection-state-test]] — OPEN/SHORTED/WORKING method and thresholds
- [[2026-08-01]] — day journal
- [[60hz-mains-hum-discovery]], [[floating-cm-vs-contact-reconciliation]]
- [[experiment-pad7-floating-input-B1]] — B1 is the chattering animal, still not run

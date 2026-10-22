---
type: experiment
area: rig-bringup
status: done
status-note: "active"
tags: [decision, eeg, emg, channel-mapping, correction, sleep-architecture, breakthrough, critical]
created: 2026-08-01
priority: critical
---

# 2026-08-01 — ⭐ THE CHANNEL MAP WAS WRONG. EMG always worked. C1 has real sleep architecture.

> [!danger] THIS SUPERSEDES A LOT. READ BEFORE TRUSTING ANY EARLIER EEG/EMG ANALYSIS.
> Every analysis in this project used `EEG = native0 − native1` and `EMG = native2 − native3`. **Both are wrong.** The RHD2216 is a BIPOLAR amplifier, so `native0` is ALREADY the EEG and `native1` is ALREADY the EMG, while natives 2 and 3 are **empty pads with no wire on them by design**.
>
> Consequences: our "EEG" was actually `EEG − EMG` (meaningless); we measured empty pads and reported them as **24 failed EMG surgeries**; and we declared **zero scoreable data** when we in fact had **21 scoreable mouse-hours** and textbook sleep architecture sitting in the file.

> [!warning] NUMBERS ON THIS PAGE ARE SUPERSEDED — the headline conclusion is not
> Two later corrections change every hour-count and every REM figure below.
> **The core finding (the channel map was wrong; C1 has real sleep) survives and
> is now stronger.** What changed:
>
> 1. **2026-08-03, persistence bug.** `r@1min` was computed across contact gaps,
>    so it both hid real sleep and invented fake sleep. Recomputed within
>    unbroken blocks only. **"21.0 scoreable mouse-hours" is wrong — the correct
>    total is ~11.1 h** (C1 8.73 h + C2 2.34 h), and **D2 is rejected**.
> 2. **2026-08-03, thresholds re-derived** from 1,137,955 pooled epochs. C1's
>    figures under the current gate: **WAKE 65.9 / NREM 29.8 %, r@1min +0.761**.
>
> 🔴 **Do not quote any REM percentage from this page.** REM is fixed by
> construction (the 80th-percentile rule forces 20% of sleep); an independent
> Otsu cut gives 24–48%; the literature value for mice is **<10%**. REM is not
> reliably separable with this montage. Report WAKE vs NREM and REM's *order*
> (entered from NREM) only.
>
> Current numbers: [[2026-08-03-two-8-mouse-runs]] · method: [[eeg-pipeline-manual]].

## TL;DR

- ⭐ **REAL SLEEP ARCHITECTURE — replication n=2 after the full 8-mouse rescore (§3c).** C1 (8.73 h): WAKE 64.4 / NREM 31.2 / REM 4.4 %, physiology PASS. C2 (4.02 h): 56.3 / 35.7 / 8.1 %, PASS. ⚠️ **D2 WITHDRAWN — physiology FAIL under the stricter gate.** 5 of 8 mice have ZERO scoreable EEG time. The project's **first genuine sleep result**, on C1 strongly and C2 moderately.
- ✅ **EMG was never broken. It works on 5 of 8 mice** (A1, C1, C2, D1, D2 at 0.0-4.2 % open). The surgeries were fine.
- 🔴 **The real problem is the EEG channel (`/1`), open 61.8-100 % on every mouse.** One failing channel type, not two.
- 📈 **21.0 scoreable mouse-hours**, not zero: C1 8.7 h, C2 7.0 h, D2 5.3 h.
- 🐛 Second bug found and fixed: `nperseg=512` at 1 kHz gave 1.95 Hz resolution, so the 6-9 Hz theta band held **one FFT bin** and `np.trapz` returned **exactly zero** for every epoch.

## 1. How this was caught

Not by the analysis. **By someone refusing to accept an implausible result.**

The 2026-07-31 and 2026-08-01 analyses concluded that 23 of 24, then 16 of 16, EMG legs were electrically open across every animal. The objection raised was simple and correct: *the professor did these surgeries; it is not credible that every single EMG implant failed, so the error is on our end and we are looking at the data wrong.*

That was right. **A result too implausible to be true usually is.** The no-wire control built on 2026-07-31 had actually already contained the answer — natives 2/3 matched the no-wire controls perfectly **because they ARE no-wire channels** — and it was read backwards.

## 2. The correct channel map

The RHD2216 is **bipolar**: each channel has its own `+` and `−` pin and reports the difference. The 4 wires per mouse land on the pins of **two** channels, not four.

| native | Allego site, mouse A | Allego site, mouse B | carries |
| --- | --- | --- | --- |
| 0 / 32 | **`/1`** | **`/33`** | **EEG** (frontal vs parietal), already bipolar |
| 1 / 33 | **`/2`** | **`/34`** | **EMG** (neck pair), already bipolar |
| 2, 3 / 34, 35 | `/3`, `/4` | `/35`, `/36` | **empty pads, no wire by design** |

```
EEG = native0      (do NOT subtract anything)
EMG = native1      (do NOT subtract anything)
natives 2, 3       IGNORE
```

> [!tip] In Allego select only `/1, /2` and `/33, /34` per port
> 16 channels for 8 mice, not 32. Selecting `/3, /4, /35, /36` records empty pads.

### Evidence — four independent tests, no assumption about pin wiring needed

| test | result | interpretation |
| --- | --- | --- |
| **correlation `/1` vs `/2`** | **r = −0.003 raw, +0.000 in 0.5-45 Hz** | Two single-ended electrodes mm apart on one hemisphere, sharing a reference, would correlate strongly. Zero ⇒ **independent differential pairs**. Subtracting them was never a bipolar montage. |
| **burstiness, 70-300 Hz envelope** | `/1` CV 0.21, p95/p50 1.45 · `/2` CV **0.79**, p95/p50 **4.48** | EEG is stationary, muscle activity comes in bursts. |
| **`/2` muscle power vs `/1` delta** | **ρ = −0.285** (n=180 epochs) | Muscle tone up ⇒ delta down. The fundamental sleep/wake relationship. Can only appear if these are EMG and EEG. |
| **`/3`,`/4` vs no-wire controls** | statistically identical | They have no wire attached. |

Chip metadata is empty in the `.xdat` (`port_map` all null, no `input_mode`), so this had to be settled from the signals. It is settled.

⚠️ **Still worth confirming physically.** The evidence is strong but inferential. A look at the actual headstage wiring, or confirmation from whoever wired it, would close it properly.

## 3. ⭐ C1 sleep architecture — the first real result

8.70 h, 7829 epochs of 4 s, **99.9 % clean**. EEG = `C/1` filtered 0.5-30 Hz, EMG = `C/2` filtered 10-300 Hz, theta 6-9 Hz, delta 0.5-4 Hz (SOP parameters).

**WAKE 66.8 % · NREM 29.3 % · REM 3.9 %** — wake-dominant, correct for the dark phase.

### Physiology check — every direction correct

| state | EMG | EEG rms | delta % | theta/delta |
| --- | --- | --- | --- | --- |
| WAKE | **48.3 µV** | 50.6 | 26.5 | 0.74 |
| NREM | 15.1 | **68.9 µV** | **41.6** | 0.31 |
| REM | **13.2 µV** | 51.7 | 18.0 | **1.90** |

NREM: highest delta, biggest amplitude, low muscle tone. REM: highest theta/delta, lowest muscle tone. WAKE: highest muscle tone. Canonical. Noise does not produce this table.

### Persistence — the test that failed before now passes decisively

| lag | r (corrected) | r (old wrong mapping) |
| --- | --- | --- |
| 4 s | **+0.898** | — |
| 60 s | **+0.803** | +0.212 |
| 300 s | **+0.636** | +0.036 |
| 600 s | **+0.484** | +0.001 |
| 1800 s | +0.158 | — |
| **shuffle control** | **+0.014** | +0.011 |

Sleep-scale persistence, exactly what was missing before.

### Bout structure

| state | n | median | mean | max |
| --- | --- | --- | --- | --- |
| WAKE | 178 | 8 s | 117.5 s | 2284 s |
| NREM | 266 | 12 s | 34.5 s | 236 s |
| REM | 143 | 4 s | 8.6 s | 68 s |

Random expectation is 8 s. WAKE and NREM clearly exceed it.

### Hourly profile — NOT flat

| hour | WAKE % | NREM % | REM % |
| --- | --- | --- | --- |
| 0 | 21.2 | 69.4 | 9.3 |
| 1 | 65.6 | 28.0 | 6.4 |
| 2 | 14.6 | 76.3 | 9.1 |
| 3 | 81.4 | 15.8 | 2.8 |
| 4 | 97.9 | 1.9 | 0.2 |
| 5 | 81.3 | 17.2 | 1.4 |
| 6 | 61.0 | 36.1 | 2.9 |
| 7 | 97.7 | 1.7 | 0.7 |
| 8 | 86.6 | 11.8 | 1.6 |

Sleep-rich at hours 0 and 2, near-continuous wake at 4 and 7. Real structure.

> [!warning] Honest caveats — do NOT let this become another 2026-07-15
> - ~~n = 1 mouse~~ **REPLICATED on n=3 (C1, D2, C2)** — but all from ONE recording, and all from the DARK phase.
>   ⚠️ **Precisely:** the recording spans 27.9 h and DOES cover a full light phase. But every window in which the EEG channel was alive falls in the dark phase (C1 18:06→02:50, D2 18:06→23:24, C2 20:01→21:07). The EEG electrodes had already failed before the light phase began. **A light-phase test is still owed** — NREM should dominate, which is a strong independent check.
>
> > [!success] ✅ SUPERSEDED 2026-08-03 — THE LIGHT-PHASE TEST IS DONE AND C1 PASSES
> > The claim above is **wrong**, because the light schedule was unknown when it
> > was written and the phase boundary was guessed. The cycle is **lights ON
> > 09:00, OFF 21:00 KST (ZT0 = 09:00)**. The recording starts at **18:06**, so
> > its first **2.9 hours are LIGHT phase**, not dark.
> >
> > C1's alive window therefore straddles both phases, and the split is textbook:
> >
> > | phase | duration | WAKE | NREM |
> > | --- | --- | --- | --- |
> > | light (18:06–21:00) | 2.89 h | **33.1%** | 58.1% |
> > | dark (21:00–02:50) | 5.84 h | **82.2%** | 15.9% |
> >
> > **C1 is 66.9% asleep in the light phase. Published C57BL/6 values are ~70%
> > asleep in the light phase, NREM 62.0 ± 7.8 %/12 h — C1 lands inside one
> > standard deviation**, with the light/dark contrast in the correct direction.
> >
> > This is the strongest evidence in the project, because **nothing in the QC
> > gate or the persistence statistic knows about the clock** — it is a genuinely
> > external check. See [[2026-08-03-two-8-mouse-runs]] and [[eeg-pipeline-manual]].
>   ⚠️ **A connection filter based on hum ALONE is not sufficient to select scoreable windows.** C2 appeared "connected" at 18:00-19:00 the next evening and at 05:21-05:57, but those windows are SHORTED: EEG rms 20.9 and 16.1 µV against 68.7 µV when genuinely working, WAKE 99.7-99.8 %, and persistence r = −0.003 / −0.002 (no structure at all). **Gate scoreable windows on EEG amplitude AND temporal structure, not just low mains.** This is the "shorted looks quieter than good" trap from [[electrode-connection-state-test]], and it caught me a second time.
> - ⚠️ **THE ANIMAL ROOM LIGHT SCHEDULE IS NOT DOCUMENTED ANYWHERE IN THIS VAULT.** Every circadian claim depends on it. Record lights-on/lights-off in `00-config/production-values.md`.
> - **Thresholds are data-driven** (EMG dip at 25 µV; theta/delta at the 80th percentile), **not validated against a human scorer**. The state percentages carry real uncertainty.
> - **REM bouts average only 8.6 s**, which suggests the REM threshold is catching transitional epochs a human scorer would merge. Treat REM % as provisional.
> - The positive-control validation demanded by the [[2026-08-07-council-review-of-the-analysis-pipeline|council]] is still owed: run the pipeline on a public, human-scored mouse dataset and confirm it detects sleep there.
> - What is NOT threshold-dependent: the physiology table and the persistence numbers.

## 3b. ⭐ REPLICATION — n=3, all physiology correct

Same script, same parameters, two more animals:

| mouse | window | clean | WAKE | NREM | REM |
| --- | --- | --- | --- | --- | --- |
| **C1** | 8.70 h | 99.9 % | 66.8 % | 29.3 % | 3.9 % |
| **D2** | 5.20 h | 99.8 % | 80.8 % | 18.6 % | 0.6 % |
| **C2** | 3.00 h | 83.0 % | 37.9 % | 52.2 % | 9.9 % |

**Physiology check — the ordering is correct in ALL THREE, independently:**

| mouse | | EMG | EEG rms | delta % | theta/delta |
| --- | --- | --- | --- | --- | --- |
| **D2** | WAKE | **87.2** | 56.9 | 28.2 | 0.55 |
| | NREM | 10.0 | **72.6** | **41.3** | 0.32 |
| | REM | **7.8** | 54.8 | 17.6 | **1.69** |
| **C2** | WAKE | **68.3** | 69.3 | 14.9 | 1.21 |
| | NREM | 16.7 | **86.2** | **21.8** | 0.69 |
| | REM | **16.1** | 80.2 | 9.6 | **3.45** |

In every animal: WAKE has the highest muscle tone, NREM the most delta and the biggest amplitude, REM the highest theta/delta and the lowest muscle tone.

**Persistence, all three well above shuffle:**

| mouse | 1 min | 10 min | shuffle |
| --- | --- | --- | --- |
| C1 | +0.803 | +0.484 | +0.014 |
| D2 | +0.702 | +0.258 | −0.025 |
| C2 | +0.738 | +0.198 | +0.032 |

**n=3. The result replicates.** State percentages differ between animals and windows, as expected for different mice at different times of night, but the physiological structure is identical every time. That is what a real signal looks like.


## 3c. ⚠️ FULL 8-MOUSE RESCORE (2026-08-02) — D2 WITHDRAWN, replication is n=2

Rescored all 8 mice over the full 27.9 h with the corrected map, a **three-part gate** (not open AND not shorted AND not clipped), **Otsu-derived** per-animal EMG thresholds instead of a hand-picked 25 µV, and a **structure check before any hypnogram is reported**. Scripts `score_all_mice.py` + `gate_and_score_all.py`.

| mouse | scoreable | WAKE | NREM | REM | r@1min | shuffle | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **C1** | **8.73 h** | 64.4 % | 31.2 % | 4.4 % | +0.746 | −0.003 | **SCOREABLE, physiology PASS** |
| **C2** | **4.02 h** | 56.3 % | 35.7 % | 8.1 % | +0.648 | +0.015 | **SCOREABLE, physiology PASS** |
| D2 | 4.22 h | 64.0 % | 30.5 % | 5.4 % | +0.538 | +0.005 | ⚠️ **physiology FAIL — states NOT reported** |
| A1, A2, B1, B2, D1 | 0.00-0.07 h | — | — | — | — | — | INSUFFICIENT |

> [!warning] ⚠️ D2 IS WITHDRAWN FROM THE REPLICATION — the 2026-08-01 "n=3" was optimistic
> D2's WAKE epochs have HIGHER EEG amplitude than its NREM (75.9 vs 72.3 µV) and essentially the SAME delta (41.6 % vs 42.1 %), and its REM has HIGHER muscle tone than NREM (27.4 vs 12.4 µV). That ordering is physiologically wrong.
>
> On 2026-08-01 D2 looked like a clean replication because it was scored on a hand-picked window with C1's hand-picked 25 µV EMG threshold. Under a per-animal Otsu threshold plus the amplitude gate it does not hold. **The replication is n=2 (C1 strong, C2 moderate), not n=3.**
>
> C2 passes but its NREM/WAKE delta separation is weak (19.6 % vs 17.9 %). **C1 remains the only strong case.**

### Physiology check

| mouse | state | EMG | EEG rms | delta % | th/de | |
| --- | --- | --- | --- | --- | --- | --- |
| **C1** | WAKE | 49.2 | 50.5 | 26.5 | 0.74 | **PASS** |
| | NREM | 15.5 | **68.0** | **41.0** | 0.32 | |
| | REM | 14.4 | 52.2 | 17.8 | **1.85** | |
| **C2** | WAKE | 72.2 | 64.3 | 17.9 | 0.61 | **PASS** |
| | NREM | 26.5 | **85.7** | **19.6** | 0.59 | |
| | REM | 20.0 | 80.8 | 9.7 | **2.35** | |
| D2 | WAKE | 105.1 | **75.9** | 41.6 | 0.29 | **FAIL** |
| | NREM | 12.4 | 72.3 | 42.1 | 0.30 | |
| | REM | **27.4** | 51.4 | 19.5 | 1.41 | |

### ⭐ Why the other five failed — and where the lost data is

| mouse | EEG OPEN | EEG shorted | **EEG good** | EMG ok |
| --- | --- | --- | --- | --- |
| A1 | 27.9 h | 0 | **0.0 h** | **27.9 h** |
| A2 | 27.9 h | 0 | 0.0 h | 0.0 h |
| **B1** | 16.1 h | 0 | **11.8 h** ⭐ | **0.2 h** ⚠️ |
| B2 | 27.9 h | 0 | 0.0 h | 1.4 h |
| C1 | 19.2 h | 0 | 8.7 h | 27.9 h |
| C2 | 20.5 h | 3.2 h | 4.2 h | 26.8 h |
| D1 | 27.9 h | 0 | 0.0 h | 27.9 h |
| D2 | 22.6 h | 1.1 h | 4.2 h | 27.8 h |

> [!important] ⭐ B1 HAS THE BEST EEG IN THE FLEET AND IS UNSCOREABLE FOR WANT OF AN EMG
> **B1: 11.8 h of good EEG at a median 66.7 µV** — more than C1 — **blocked by a dead EMG channel (0.2 h).** That is 11.8 hours of usable data sitting on disk behind ONE channel.
>
> The complementary pattern is the actionable one: **A1 and D1 have PERFECT EMG for the full 27.9 h and ZERO EEG. B1 has excellent EEG and no EMG.** Fix either side on those three animals and scoreable time roughly DOUBLES.

- EEG failures are almost entirely **OPEN**, not shorted (shorted totals only 4.3 h across all 8 mice) ⇒ a disconnection problem.
- **28.9 h of good EEG exists** across 4 mice; only **17.0 h** overlaps working EMG; **12.75 h** passes physiology.
- **Every scoreable window lies between 18:06 and 02:50.** Still NO light-phase data with a living EEG.

### Method hardening applied in this rescore

1. **Three-part gate** — not open (mains <300 µV both channels) AND not shorted (EEG rms ≥25 µV) AND not clipped. Hum alone let shorted windows through on 2026-08-01.
   ⚠️ *Thresholds superseded 2026-08-03: open is now **150 µV** (the measured valley of the bimodal distribution is 134 µV), and the single 25 µV "shorted" rule is split into an epoch-level dropout test (**11 µV**) and a channel-level dead-electrode test (**20 µV** median), because a short is a property of the channel rather than of an epoch. See [[analysis-methods-and-justification]].*
2. **Otsu threshold per animal** on the log-EMG histogram, replacing the hand-picked 25 µV constant the council flagged as arbitrary.
3. **Structure verified BEFORE reporting states.** If persistence at 1 min is not clearly above a shuffle control, the animal is reported as "NO STRUCTURE", not given a hypnogram. A dead channel will always yield *some* split if you insist on asking.
4. **Automatic physiology PASS/FAIL** per animal. This is what caught D2.


## 3d. ✅ IMPEDANCE RE-READ (2026-08-02) — it was working all along

The 2026-07-31 verdict "impedance snapshots are NOT a go/no-go gate" is **REVERSED**. It was an artifact of the wrong channel map: half the "electrodes" being scored were bare pads.

Re-read using only `/1`=EEG and `/2`=EMG, against hours-of-usable-data from the 27.9 h recording:

| mouse | EEG `/1` | pred | actual | | EMG `/2` | pred | actual | |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 6.757 | OPEN | 0.0 h | ✅ | 0.087 | CONN | 27.9 h | ✅ |
| A2 | 7.644 | OPEN | 0.0 h | ✅ | 5.849 | OPEN | 0.0 h | ✅ |
| B1 | 1.717 | OPEN | 11.8 h | ✗ | 5.465 | OPEN | 0.2 h | ✅ |
| B2 | 7.110 | OPEN | 0.0 h | ✅ | 5.663 | OPEN | 1.4 h | ✗ |
| C1 | 0.465 | CONN | 8.7 h | ✅ | 0.190 | CONN | 27.9 h | ✅ |
| C2 | 4.418 | OPEN | 4.2 h | ✗ | 0.139 | CONN | 26.8 h | ✅ |
| D1 | 6.300 | OPEN | 0.0 h | ✅ | 0.335 | CONN | 27.9 h | ✅ |
| D2 | 0.660 | CONN | 4.2 h | ✅ | 0.286 | CONN | 27.8 h | ✅ |

**Spearman ρ = −0.941, p = 5.7e-08**, from a sweep taken ~2 h BEFORE recording started. The three "misses" are marginal: B2's EMG (1.4 h of 27.9) and C2's EEG (4.2 h of 27.9) were mostly open, so the snapshot had the dominant state right. Only B1's EEG at 1.717 MΩ is a true threshold miss.

**Use Z < 2 MΩ (14/16) rather than the 0.9 MΩ proposed on 2026-07-31 (13/16).**

**Empty pads `/3,/4` median 5.902 MΩ vs no-wire control 5.557 MΩ** — independent impedance-side confirmation of the bipolar map.

> [!tip] ⭐ PRE-FLIGHT CHECK — do this BEFORE every recording
> Sweep impedance, read ONLY `/1, /2, /33, /34`:
> - **Z < 2 MΩ → connected**, expect usable data
> - **Z > 3 MΩ → open**, that channel will give nothing
> - A mouse needs **BOTH** `/1` and `/2` under threshold to be scoreable
>
> This predicts yield in advance instead of after 28 hours.


## 4. Corrected fleet numbers

| | previously reported | actually |
| --- | --- | --- |
| open time | 78.7 % | **61.6 %** (n2/n3 were never electrodes) |
| EMG failures | 23/24, then 16/16 | **3 of 8 mice** |
| scoreable mouse-hours | **0** | **21.0** |

**Per mouse, on the 16 real channels:**

| mouse | EEG `/1` % open | EMG `/2` % open | scoreable |
| --- | --- | --- | --- |
| A1 | 100.0 | **0.0 ✅** | — |
| A2 | 100.0 | 100.0 | — |
| B1 | 61.8 | 99.3 | — |
| B2 | 100.0 | 95.8 | — |
| **C1** | 68.8 | **0.0 ✅** | **8.7 h** |
| **C2** | 74.4 | **4.2 ✅** | **7.0 h** |
| D1 | 100.0 | **0.0 ✅** | — |
| **D2** | 81.1 | **0.1 ✅** | **5.3 h** |

**EMG works on 5 of 8. EEG fails on 8 of 8 (61.8-100 % open).** The problem is a single channel type, not the whole implant.

## 5. What survives from the earlier work

- ✅ **The no-wire control method** ([[electrode-connection-state-test]]) is sound — it is what exposed this.
- ✅ **Grounds are excellent**: 16 tied control pins, median 2.8 µV, no drift over 27.9 h.
- ✅ **Environmental causes remain closed**: earth, room, splitter, grounding.
- ✅ **Contact intermittency is real** — but it is the **EEG** channel that fails. C1's EEG died at 8.73 h and never returned; D2's at 5.30 h. One-way degradation stands.
- ❌ **Retracted**: "EMG failed 23/24", "16/16 EMG open", "zero scoreable mice", "C1 shows no sleep structure", and the framing of failures as "frontal vs parietal" (it was EEG vs EMG channels).

## 6. Decisions

1. ⭐ **C1's sleep architecture is the project's first real result.** Log it, replicate it, do not over-claim it.
2. ✅ **EMG surgery is exonerated. Stop treating EMG as a problem.**
3. ➡️ **All hardware effort goes to the EEG channel (`/1`)** — open on every mouse, and the only thing standing between this rig and scoreable data.
4. 🛑 **Still no new surgeries** — the implants are not implicated; this is a connection and a mapping problem.
5. ➡️ **Re-analyse C2 (7.0 h) and D2 (5.3 h)** with the corrected map. If their sleep architecture matches C1's, n=3 and the result is solid.
6. ⏳ Still owed: positive-control validation on a public scored dataset; the 1 MΩ resistor check of the Allego impedance function.

## 7b. Why this survived so long — the post-mortem

Six causes stacked. None alone would have done it.

1. **The error was written down as TRUE.** [[eight-mouse-acquisition-setup]] (2026-07-04) says *"EEG signal = pad 0 − pad 1"*. That sentence is **correct** — it describes what the CHIP does internally — but it was implemented as a SOFTWARE subtraction. The phrasing reads correctly under both interpretations, which is exactly why it survived every review.
2. **Everything downstream inherited it.** Once `EEG = native0 − native1` entered [[04-processing-guidelines]], no later analysis re-derived it from the hardware.
3. **The chip metadata is EMPTY in the `.xdat`** (`port_map` all null, no `input_mode`, no chip name), so nothing ever contradicted the assumption automatically.
4. **The 60 Hz crisis masked it.** With the EEG channel open and railing, everything looked broken, so "EMG is broken too" FITTED the prevailing story rather than contradicting it.
5. **The key fact was known and never followed through.** The project memory recorded "chip = RHD2216 **bipolar**, REF empty by design" from early on. Nobody joined it to "therefore two pads make one channel". **The empty `REF` pin was itself the clue** — bipolar channels do not need a shared reference.
6. **The vault was taken at face value** rather than verified against the signals, despite a standing instruction to verify operational details rather than assume.

**What would have caught it in ten seconds:** correlate two adjacent channels. Frontal and parietal electrodes millimetres apart CANNOT give r = 0.000.

**And the uncomfortable part: the rigour made it worse.** The no-wire controls, duty-cycle tables, threshold sensitivity sweeps and a 5-advisor council review were all methodologically sound, and all built on an unverified premise. Careful work on a wrong assumption produces a wrong conclusion that looks thoroughly evidenced. **The only thing that broke it was a human saying "that cannot be true".**

> [!danger] THE STANDING RULE THIS BUYS
> **Before any analysis of a new rig or montage, VERIFY THE CHANNEL MAP AGAINST THE SIGNALS:**
> 1. **Correlate adjacent channels.** Electrodes physically near each other must correlate. r ≈ 0 means they are independent channels, not a montage pair.
> 2. **Count wires against channels.** A bipolar chip channel consumes TWO wires. 4 wires per mouse = 2 channels, not 4.
> 3. **Check the spectral character.** EEG is stationary and delta-dominant; EMG is bursty with 70-300 Hz power.
> 4. **Test the EEG/EMG relationship.** Muscle power must ANTI-correlate with delta. If it does not, one of the two channels is not what you think.


## 7. The lesson worth keeping

**An implausible result is a bug report about your own method.** "Every EMG failed on every mouse" should have triggered a mapping audit immediately, not a fleet-wide hardware investigation. The controls were right, the physics was right, the code ran correctly — and the conclusion was still wrong, because the channel map was assumed rather than verified. Verify the map against the signals before trusting anything downstream.

## Related

- [[04-processing-guidelines]] — the mapping, now corrected at source
- [[2026-08-01-28h-contact-duty-cycle-and-c1-negative]] — superseded conclusions, corrected in place
- [[2026-07-31-contact-intermittency-no-wire-control]] — EMG conclusions retracted
- [[electrode-connection-state-test]] — control method, still valid
- [[eight-mouse-acquisition-setup]], [[allego-electrode-setup-sleep64]] — channel selection updated
- [[2026-08-01]] — day journal

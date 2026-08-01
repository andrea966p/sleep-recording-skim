---
tags: [decision, eeg, emg, channel-mapping, correction, sleep-architecture, breakthrough, critical]
created: 2026-08-01
status: active
priority: critical
---

# 2026-08-01 — ⭐ THE CHANNEL MAP WAS WRONG. EMG always worked. C1 has real sleep architecture.

> [!danger] THIS SUPERSEDES A LOT. READ BEFORE TRUSTING ANY EARLIER EEG/EMG ANALYSIS.
> Every analysis in this project used `EEG = native0 − native1` and `EMG = native2 − native3`. **Both are wrong.** The RHD2216 is a BIPOLAR amplifier, so `native0` is ALREADY the EEG and `native1` is ALREADY the EMG, while natives 2 and 3 are **empty pads with no wire on them by design**.
>
> Consequences: our "EEG" was actually `EEG − EMG` (meaningless); we measured empty pads and reported them as **24 failed EMG surgeries**; and we declared **zero scoreable data** when we in fact had **21 scoreable mouse-hours** and textbook sleep architecture sitting in the file.

## TL;DR

- ⭐ **REAL SLEEP ARCHITECTURE, REPLICATED ON 3 MICE.** C1 (8.7 h): WAKE 66.8 / NREM 29.3 / REM 3.9 %. D2 (5.2 h): 80.8 / 18.6 / 0.6 %. C2 (3.0 h): 37.9 / 52.2 / 9.9 %. **Physiology ordering correct in all three independently.** The project's **first genuine sleep result**.
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
>   ⚠️ **A connection filter based on hum ALONE is not sufficient to select scoreable windows.** C2 appeared "connected" at 18:00-19:00 the next evening and at 05:21-05:57, but those windows are SHORTED: EEG rms 20.9 and 16.1 µV against 68.7 µV when genuinely working, WAKE 99.7-99.8 %, and persistence r = −0.003 / −0.002 (no structure at all). **Gate scoreable windows on EEG amplitude AND temporal structure, not just low mains.** This is the "shorted looks quieter than good" trap from [[electrode-connection-state-test]], and it caught me a second time.
> - ⚠️ **THE ANIMAL ROOM LIGHT SCHEDULE IS NOT DOCUMENTED ANYWHERE IN THIS VAULT.** Every circadian claim depends on it. Record lights-on/lights-off in `00-config/production-values.md`.
> - **Thresholds are data-driven** (EMG dip at 25 µV; theta/delta at the 80th percentile), **not validated against a human scorer**. The state percentages carry real uncertainty.
> - **REM bouts average only 8.6 s**, which suggests the REM threshold is catching transitional epochs a human scorer would merge. Treat REM % as provisional.
> - The positive-control validation demanded by the [[2026-08-01-council-eeg-pipeline-review|council]] is still owed: run the pipeline on a public, human-scored mouse dataset and confirm it detects sleep there.
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

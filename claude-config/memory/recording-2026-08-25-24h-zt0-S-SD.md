---
name: recording-2026-08-25-24h-zt0-s-sd
description: "2026-08-25 24 h ZT0-to-ZT0 run on the S-SD cohort: only D2 passes strict rung 2, EEG usability collapses in the dark phase, and B slot 1 reads floating (cause later found to be a chewed tether, not the port)"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-26T00:25:01.086Z
---

⭐⭐ **`allego_0__uid0825-09-00-00`, 2026-08-25 09:00:00 → 2026-08-26 09:16:34 KST.
24.276 h, 91.59 GB, RUNG 0 PASS** (87,393,408 data = 87,393,408 timestamp samples, remainders 0/0).
Started at **ZT0 and stopped at ZT0**, so light and dark get equal weight. Cohort `S-SD`, see
[[recording-2026-08-24-new-8-mice]]. Features cached at
`~/eeg-processed/2026-08-25/feat_uid0825-09-00-00.npz`.

✅⭐ **THE RIG HELD.** 726 watchdog checks over 24 h: **zero stalls, zero slow periods,
`allegoserver` up throughout**, write rate 100.7% of nominal. A single `--disable-gpu` instance ran
37 h+ without a wobble, after two Allego deaths the day before
([[allego-mesa-gpu-crash-and-log-storm]]). 🔑 **Watchdog pattern worth reusing: check bytes on disk
every 120 s and log rate as a % of `262*4*fs`.** Script kept in the session scratchpad.

## 🔴🔴 B SLOT 1 IS STILL FLOATING **AFTER THE USER CONFIRMED CORRECT SEATING**
Floor 60 Hz, whole run: **B1 = 246 µV** against **2700-5100 µV on all seven other chips**, and flat
across all 24 hourly bins (91-466 µV, **no jump anywhere**) ⇒ it never changed during the run.
5 of its 14 wire-free floor sites are quiet+steep = the floating signature.
⭐⭐ **THE DECISIVE COMPARISON — the two slots of the SAME port:**
```
B slot 1: floor 60 Hz   246 uV    floor rms   243 uV     <- floating
B slot 2: floor 60 Hz  4896 uV    floor rms  3723 uV     <- normal
```
**Same port, same cable, same XDAQ input, opposite results ⇒ port B, its cable and the XDAQ input
are INNOCENT.** The fault is in the slot-1 branch only.
🔴🔴 **MY CAUSAL READING OF THIS IS RETRACTED.** I called it "the ground PIN POSITION in the
connector housing" and "a standing PORT fault across four cohorts". On 2026-08-26 the B1 animal
was pulled (**its tether was CHEWED**) and the spare HLBSSD17 put in the **same slot**: the floor
went **246 → 2338 µV, grounded, with real EEG**. The fault followed the ANIMAL AND ITS TETHER.
The measurements above stand; the causal claim does not. See [[b-slot1-was-the-tether-not-the-port]].

## ✅ D1's CHIP IS FINE — its failure is the TETHER, not the ground
D1 floor 60 Hz **3189 µV, normal all 24 h** ⇒ that chip is properly grounded and seating was never
D1's problem. But D1's own channels are open: **EEG rms 2760 µV, slope −0.10, 1.4% usable, zero
recovery in any hourly bin; EMG 1167 µV.** Matches HLBSSD19's registry note *"might have tether
damaged due to climbing"*. 🔑 **A floating CHIP and an open ELECTRODE look nothing alike — separate
them with the chip's own wire-free floor before blaming anything.**

## VERDICTS, 24.28 h, per-chip trimmed floor (8739 epochs)
| pos | mouse | EEG rms/slope | EEG % | longest | EMG rms | EMG % | BOTH % | longest |
|---|---|---|---|---|---|---|---|---|
| **D2** | HLBSSD18 | 86 / −1.53 | 96.2 | 0.94 h | **49** | 79.3 | **77.3** | **0.35 h ✅ PASS** |
| A2 | HLBSSD12 | 124 / −1.49 | 79.5 | **3.62 h** | 492 | 0.7 | 0.7 | — |
| C1 | HLBSSD15 | 102 / −1.51 | 85.2 | 0.47 h | 455 | 0.0 | 0.0 | — |
| C2 | HLBSSD16 | 124 / −1.27 | 48.8 | 0.62 h | 877 | 0.0 | 0.0 | — |
| A1 | HLBSSD11 | 94 / −1.36 | 31.0 | 0.09 h | **47** | **94.5** | 30.4 | 0.09 h |
| B2 | HLBSSD14 | 4425 / −0.23 | 0.0 | — | 107 | 68.5 | 0.0 | — |
| D1 | HLBSSD19 | 2760 / −0.10 | 1.4 | — | 1167 | 0.0 | 0.0 | — |
| B1 | HLBSSD13 | 486 / −1.58 | 1.0 | — | 2761 | 0.0 | 0.0 | — |

**Only D2 passes strict rung 2** (EEG AND EMG in the same epoch, ≥15 min block: 21 min).
EEG-only ≥15 min: **A2, D2, C2, C1**. 🛑 **A1 has EXCELLENT EMG and failing EEG** — do not describe
it as a working animal without saying which role.

## 🔴⭐⭐ EEG USABILITY COLLAPSES IN THE DARK PHASE — a design problem, not a bug
| pos | light h0-11 | dark h12-23 | drop |
|---|---|---|---|
| A2 | 96.3% | 64.2% | **−32.1** |
| C2 | 66.3% | 32.3% | **−34.1** |
| A1 | 40.0% | 21.9% | −18.1 |
| C1 | 93.0% | 77.3% | −15.7 |
| **D2** | 97.5% | 94.8% | **−2.7 (immune)** |

Animals are active in the dark, movement flips the contact
([[movement-dependent-contact-root-cause]]). 🔑 **Dark-phase EEG yield is materially lower, and the
dark phase is where most WAKE lives — so a 24 h run does NOT give 24 h of scoreable data, and the
loss is biased toward one behavioural state.** ⚠️ **A2 degrades progressively over the last 5 h**
(hours 19-23: 14/10/21/38/41%) — watch whether that animal is failing for good.
🛑 **1 h snapshots badly overstate a 24 h run:** on 08-24 A2 and C2 both read ~100% EEG over an
hour; across 24 h they are 79.5% and 48.8% with longest blocks of 3.62 h and 0.62 h.

## ⭐ EMG CIRCADIAN AMPLITUDE (descriptive, not a sleep result)
| pos | light | dark | dark/light |
|---|---|---|---|
| **A1** | 17.2 µV | 74.0 µV | **4.29x** |
| D2 | 32.7 µV | 52.6 µV | 1.61x |
| B2 | 92.7 µV | 105.5 µV | 1.14x (EMG itself degrades in dark, weak) |

**A1's 4.29x sits squarely in the range recorded for genuinely state-dependent EMG** and closely
matches the old 48 h control's raw figures (31 µV light / 73 µV dark,
[[a2-control-48h-reference-profile]]). 🛑 Still NOT a sleep result — the kappa remains the gate.

Related: [[recording-2026-08-24-new-8-mice]] · [[animal-card-verdict-ladder]] ·
[[emg-gate-passes-and-floor-bug]] · [[test-suite-two-of-four-verify-nothing]]

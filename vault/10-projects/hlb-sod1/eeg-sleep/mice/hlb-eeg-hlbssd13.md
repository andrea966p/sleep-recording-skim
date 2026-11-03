---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD13: EEG re-score 2026-11, baseline tier X, recovery tier –"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD13: S-SD (SOD1, sleep deprivation), rig B1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **X** → nothing. screen
> - **Recovery:** tier **–** → no recording. 
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NO VERDICT, recovery –.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | X | – |
| hours usable, EEG + EMG | 8 | – |
| … of them light | 6 | – |
| … of them dark | 2 | – |
| hours usable, EEG alone | 22 | – |
| hours usable, EMG alone | 9 | – |
| EMG separability η (gap; ≥ 0.70) | 0.714 | – |
| η, SleepStager 20–90 Hz EMG | 0.788 | – |
| δ AUC, NR vs W (≥ 0.75) | 0.863 | – |
| EEG median log10 δ (2–4) | 2.99 | – |
| EEG-alone state changes / h (≥ 5) | 16.0 | – |
| κ rule vs HMM | 0.30 | – |
| κ NREM, rule vs EEG alone | 0.16 | – |
| κ rule, gap vs 20–90 Hz EMG | 0.52 | – |
| artifact epochs % | 60.9 | – |
| EEG 60 Hz, median µV | 627 | – |
| EMG 60 Hz, median µV | 2785 | – |
| wake % light (rule) | 57.8 | – |
| wake % dark (rule) | 90.8 | – |
| NREM % light, EEG alone | – | – |
| NREM % dark, EEG alone | – | – |
| sleep % light, EMG alone | 42.3 | – |
| sleep % dark, EMG alone | 28.7 | – |
| r@1min (project definition) | 0.175 | – |
| old verdict reason | rung 2 CONNECTION: chip floor is 246 uV of 60 Hz (grounded chips show >800) -- no verdict can be drawn | – |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssd13-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG partial; rule follows the EEG: no; tier agreed.
Plausibility: Not judgeable. The EEG trace is almost flat with broadband stripes and wild delta swings. The EMG is genuine only in about the first 5 h. After that it switches between flat plateaus (at 200-800 uV) for hours, which is technical. The 91% dark wake is just the plateau sitting above the cut.
Concerns: The rule hypnogram follows the EMG plateaus, not the EEG. Rule, HMM and EEG-only disagree (kappa 0.30 and 0.16), and the EEG-only run puts NREM where the EMG plateaus. Only hours 0-5, 7-8 and a few others pass the screen (8 h, 6L/2D), which is not enough for tier B. Keep X. The first 5 light hours may be usable for a light-only look, but nothing supports a daily pattern.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 470 | W | high | rule | EMG burst fills most of the epoch (2x cut, from about 0.6 s to the end). It is genuine muscle in the early good hours, and EEG is flat. |
| 2 | 491 | W | low | rule | A 4-s lull (0.44x) between two wake bursts a few seconds either side. Quiet wake inside a bout. The EEG is flat, so it cannot confirm. |
| 3 | 717 | W | high | rule | EMG is continuously raised with bursts (1.4x cut). The HMM's R contradicts the muscle. |
| 4 | 747 | W | medium | rule | A burst of about 2 s and another bout just before it, tone above cut (1.5x). Flat EEG gives no counter-evidence. |
| 5 | 4040 | uncertain | low | neither | EEG trace is essentially flat (noise-level) and the EMG is a constant-amplitude plateau (0.39x), so NR versus R cannot be separated. Theta/delta is raised over several epochs but delta and theta are not credible on this EEG. |
| 6 | 6505 | uncertain | low | neither | Constant 0.35x EMG plateau and a flat EEG: a technical two-level signal, not muscle. The HMM and rule labels rest on noise. |
| 7 | 13148 | W | high | rule | EMG is high throughout (4x cut) with EEG artefact spikes. Clearly active wake, so the HMM's R is wrong. |
| 8 | 13397 | W | high | rule | Dense EMG bursts for most of the epoch (about 3x cut), movement artefacts in the EEG. Wake. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD13_B_epochs.png`.


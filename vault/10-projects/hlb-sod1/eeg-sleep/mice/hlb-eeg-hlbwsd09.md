---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSD09: EEG re-score 2026-11, baseline tier X, recovery tier X"
tags: [eeg, hlb, mouse, hlbwsd]
---

# HLBWSD09: W-SD (water, sleep deprivation), rig B1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **X** → nothing. screen
> - **Recovery:** tier **X** → nothing. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NO VERDICT.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | X | X |
| hours usable, EEG + EMG | 0 | 0 |
| … of them light | 0 | 0 |
| … of them dark | 0 | 0 |
| hours usable, EEG alone | 3 | 0 |
| hours usable, EMG alone | 9 | 17 |
| EMG separability η (gap; ≥ 0.70) | 0.701 | 0.736 |
| η, SleepStager 20–90 Hz EMG | 0.772 | 0.487 |
| δ AUC, NR vs W (≥ 0.75) | 0.588 | 0.386 |
| EEG median log10 δ (2–4) | 3.05 | 0.26 |
| EEG-alone state changes / h (≥ 5) | 22.3 | 64.4 |
| κ rule vs HMM | 0.11 | 0.44 |
| κ NREM, rule vs EEG alone | 0.19 | 0.09 |
| κ rule, gap vs 20–90 Hz EMG | 0.92 | 0.09 |
| artifact epochs % | 85.3 | 12.3 |
| EEG 60 Hz, median µV | 2252 | 290 |
| EMG 60 Hz, median µV | 1754 | 3421 |
| wake % light (rule) | – | – |
| wake % dark (rule) | – | – |
| NREM % light, EEG alone | 98.4 | – |
| NREM % dark, EEG alone | 63.5 | – |
| sleep % light, EMG alone | 64.0 | 70.8 |
| sleep % dark, EMG alone | 50.2 | 88.8 |
| r@1min (project definition) | – | – |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.3 min | rung 2 CONNECTION: chip floor is 593 uV of 60 Hz (grounded chips show >800) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsd09-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG bad; rule follows the EEG: not applicable; tier agreed.
Plausibility: Not plausible: 55% EEG and 69% EMG artefact; EMG is a flat ~1000 uV plateau except ZT7-15.5, EEG spectrogram is saturated broadband with delta 4-5 log10 (rails). ZT0-7 and ZT15.5-24 carry no signal; EEG delta in the late hours drops to near zero (disconnection).
Concerns: The EMG variability in ZT7-15.5 might hold some wake/sleep structure but the EEG there is still broadband noise (AUC 0.59, kappa rule-HMM 0.11), so nothing is scoreable. Old rejection and tier X agree. No contested epochs were drawn for this recording.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsd09-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG bad; rule follows the EEG: no; tier agreed.
Plausibility: Rule says NR for about 14 h and wake 13%, HMM says R for 5 h: not physiological. Wake is higher in the light than the dark (opposite direction), no wake bouts after hour 5.
Concerns: EMG is an amplitude-modulated sinusoid at a nearly constant 0.5-0.7x cut (mains hum), flat with slow drift and no bursts, which is technical, not muscle. The EEG trace is flat (delta ~0.2) with a 20 Hz line. The screen kept 15 h as 'both ok' only because a flat EMG sits under the cut; those hours should be dropped. Rule vs EEG-only kappa 0.09, AUC 0.39. X is right.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 9105 | uncertain | low | neither | EMG is a constant mains-like sine (0.49x cut) and the EEG is flat; theta/delta 0.36 and sigma are noise, nothing to stage. |
| 2 | 9106 | uncertain | low | neither | Same constant EMG hum and flat EEG; the R label comes from a theta/delta of 1.48 on noise. |
| 3 | 9395 | uncertain | low | neither | EMG hum without bursts, flat EEG (delta 0.36); no physiological state can be read. |
| 4 | 9983 | uncertain | low | neither | Constant EMG hum at 0.69x cut, EEG flat; neither NR nor R is supported. |
| 5 | 10898 | uncertain | low | neither | No bursts, no slow waves, EEG flat; label is set by noise ratios. |
| 6 | 11798 | uncertain | low | neither | Same flat EEG and sinusoidal EMG; HMM R and rule NR are both artefact. |
| 7 | 12517 | uncertain | low | neither | Flat EEG with delta near zero and mains-like EMG; no basis for NR or R. |
| 8 | 13884 | uncertain | low | neither | Constant EMG hum at 0.73x cut, no EEG signal visible; cannot be staged. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD09_R_epochs.png`.


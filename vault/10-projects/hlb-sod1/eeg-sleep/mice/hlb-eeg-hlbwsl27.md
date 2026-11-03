---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSL27: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbwsl]
---

# HLBWSL27: W-SL (water, ad libitum), rig D1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** yes.
> - Old pipeline: baseline SCOREABLE, recovery NO VERDICT.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | A |
| hours usable, EEG + EMG | 24 | 24 |
| … of them light | 12 | 12 |
| … of them dark | 12 | 12 |
| hours usable, EEG alone | 24 | 24 |
| hours usable, EMG alone | 24 | 24 |
| EMG separability η (gap; ≥ 0.70) | 0.779 | 0.785 |
| η, SleepStager 20–90 Hz EMG | 0.659 | 0.683 |
| δ AUC, NR vs W (≥ 0.75) | 0.900 | 0.898 |
| EEG median log10 δ (2–4) | 3.22 | 3.23 |
| EEG-alone state changes / h (≥ 5) | 45.7 | 44.3 |
| κ rule vs HMM | 0.88 | 0.90 |
| κ NREM, rule vs EEG alone | 0.81 | 0.82 |
| κ rule, gap vs 20–90 Hz EMG | 0.88 | 0.93 |
| artifact epochs % | 0.1 | 0.1 |
| EEG 60 Hz, median µV | 33 | 8 |
| EMG 60 Hz, median µV | 32 | 56 |
| wake % light (rule) | 27.7 | 27.0 |
| wake % dark (rule) | 74.0 | 71.8 |
| NREM % light, EEG alone | 54.3 | 57.7 |
| NREM % dark, EEG alone | 24.0 | 23.4 |
| sleep % light, EMG alone | 72.4 | 72.5 |
| sleep % dark, EMG alone | 27.1 | 30.3 |
| r@1min (project definition) | 0.615 | 0.665 |
| old verdict reason | 24.00 h in 1 block(s), r@1min 0.443 | rung 2 CONNECTION: chip floor is 5 uV of 60 Hz (grounded chips show >800) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsl27-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Strongly nocturnal: wake 28% light vs 74% dark (high but consistent with the EMG-only 45-point dark/light difference), delta bands in the light and at ZT17-20, low-floor bursty EMG, all 24 hours kept.
Concerns: EMG eta is the lowest of the batch (0.78) but the traces are fine. Several contested epochs in ZT7-9 have EMG at 0.8-0.95x cut with no atonia and low-ish delta, where quiet wake vs light NREM is a judgment call. Old verdict SCOREABLE agrees with tier A.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 383 | W | low | rule | Moderate EMG burst for about 2.3 s (epoch mean 1.25x cut, tone 1.10) with slow waves still present, probably movement; HMM NR relies on the EEG delta 3.48 which is artefact in movement. |
| 2 | 4983 | W | low | rule | Tail of a big burst, mean 1.06x cut, delta 3.22 reduced and sigma 2.40 low; just over the W boundary right after a clear W epoch. |
| 3 | 6929 | uncertain | low | neither | EMG noisy at 0.92x cut without atonia, delta 3.04 below NR median 3.55, no spindles; quiet wake vs light NR, long ambiguous stretch. |
| 4 | 7795 | NR | low | rule | EMG drops to a flat 0.65x with heartbeat spikes after a large burst, theta/delta 0.59, sigma 2.64, delta 3.16; sleep, though delta is below the NR median. |
| 5 | 8157 | NR | medium | rule | Sigma 2.77 high with spindle-like waves, delta 3.29, theta/delta 0.81; REM only begins the next epoch (theta/delta 2.65). |
| 6 | 9502 | W | high | rule | EMG active throughout (1.44x cut), delta 3.13 reduced, theta/delta 0.51 (rule and HMM both W). |
| 7 | 9922 | NR | low | rule | Sigma 3.09 and delta 3.57 near NR median despite theta/delta 1.80, irregular larger waves not a regular theta rhythm; EMG 0.60x at sleep floor with heartbeat. |
| 8 | 10378 | NR | medium | hmm | Single burst of about 1.2 s (under half) inside strong slow-wave NREM, delta 3.45 near NR median 3.55, theta/delta 0.31; microarousal. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL27_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsl27-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 31.6 % in the light and 71.8 % in the dark (a long wake stretch from ZT12), with delta bands alternating with wake. A sleep rebound around ZT18 to ZT19 and ZT21 to ZT22 is seen. Rule vs HMM kappa is 0.90. This mouse has the lowest EMG separability of the batch (eta 0.785), so some of the long dark wake could have quiet-wake or tonic stretches.
Concerns: Hours 6 to 7 and 8 to 9 were dropped. They look sleep-rich in the overview with a clean EMG floor, so they may be wrongly dropped on the EEG-agreement test; the impact is 2 h. The ss60 EMG gives tier C (EMG separability is poor on that version), so the A depends on the gap EMG, which looks clean in the traces. Tonic EMG epochs just below the cut (0.7 to 0.9x) in the dark, for example at ZT16, are hard to separate from NR. Old 'NO VERDICT' was a chip floor check.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 3509 | NR | medium | rule | EMG is flat at 0.39x, the EEG shows slow waves with spindles, delta 3.16 and sigma 2.59. Theta/delta 1.21 is not enough for REM. |
| 2 | 6344 | R | medium | hmm | EMG is atonic (0.37x) with heartbeat only, delta 3.05 is below the NR median, sigma has dropped to 2.13, and theta/delta 1.48. It sits inside an R run (R in neighbours), so the rule's NR looks like an island error. |
| 3 | 6918 | W | medium | rule | EMG is continuously active with small bursts through the epoch (0.78x the cut), between clear wake epochs. Delta and the EEG are not NR-like enough to override this. |
| 4 | 9936 | NR | medium | rule | EMG is flat at 0.27x, the EEG shows slow waves and spindles (sigma 2.59), and theta/delta 0.68 is not REM-like. Delta 3.06 is a little low. |
| 5 | 11777 | NR | low | rule | There are a few short EMG bursts (about 1 s in total) in the epoch, under half. Delta 3.15 and theta/delta 0.77 are NR-like. The big wake bout starts in the next epoch, so this is a pre-arousal NR. |
| 6 | 14420 | W | low | hmm | EMG is raised and continuous (0.82x the cut, sustained for over 12 s) with no sleep floor, delta 3.01 is below the NR median, and the neighbours are quiet wake. It looks like quiet wake, not NR. |
| 7 | 18218 | NR | low | rule | EMG is flat and atonic for the first 2.7 s, then a burst for about 1.3 s, under half. Delta 3.24 and theta/delta 0.51 make NR more likely than REM. It could also be the end of a REM bout. |
| 8 | 20917 | W | high | rule | EMG bursts through the whole epoch among wake neighbours (1.2x to 2.5x), with low delta. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL27_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: This has the lowest EMG separability of the A set (eta 0.785), and ss60 drops it to C. In the dark the floor rises (hourly p10 16 to 23 uV at ZT13 and ZT15 to 18, vs cut 28), so tonic quiet wake sits close to the cut and the wake/NR boundary there is soft. The dropped hours 6 and 8 are again sleep-rich (wake 0.066 and 0.047), so the reported light wake (31.6 %) is inflated against all hours (27.1 %). The A tier itself holds at 22 h, and rule vs HMM kappa is 0.90. Checked: Brief; previous reviewer's notes; score.json; blocks_1h.csv. From the parquets: hourly p10 and p90; EMG NR 13.7 / W 58.6 uV; NR-W delta gap 0.43; 5 % of NR epochs below the W delta median; 85 % agreement with EEG-only NR; 1-min rho -0.50; wake on all vs kept hours. Comb share at chance (0.13); EMG mains 56 uV.


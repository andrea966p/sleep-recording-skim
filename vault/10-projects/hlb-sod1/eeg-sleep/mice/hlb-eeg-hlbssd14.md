---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD14: EEG re-score 2026-11, baseline tier D, recovery tier D"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD14: S-SD (SOD1, sleep deprivation), rig B2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Recovery:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NO VERDICT.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | D | D |
| hours usable, EEG + EMG | 0 | 11 |
| … of them light | 0 | 6 |
| … of them dark | 0 | 5 |
| hours usable, EEG alone | 0 | 13 |
| hours usable, EMG alone | 24 | 17 |
| EMG separability η (gap; ≥ 0.70) | 0.846 | 0.799 |
| η, SleepStager 20–90 Hz EMG | 0.736 | 0.607 |
| δ AUC, NR vs W (≥ 0.75) | – | 0.799 |
| EEG median log10 δ (2–4) | 2.26 | 3.22 |
| EEG-alone state changes / h (≥ 5) | – | 38.1 |
| κ rule vs HMM | – | 0.45 |
| κ NREM, rule vs EEG alone | – | 0.64 |
| κ rule, gap vs 20–90 Hz EMG | – | 0.50 |
| artifact epochs % | 100.0 | 31.9 |
| EEG 60 Hz, median µV | 6020 | 99 |
| EMG 60 Hz, median µV | 94 | 49 |
| wake % light (rule) | – | 19.8 |
| wake % dark (rule) | – | 53.8 |
| NREM % light, EEG alone | – | – |
| NREM % dark, EEG alone | – | – |
| sleep % light, EMG alone | 73.7 | 79.4 |
| sleep % dark, EMG alone | 31.8 | 41.6 |
| r@1min (project definition) | – | 0.166 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min | rung 2 CONNECTION: chip floor is 126 uV of 60 Hz (grounded chips show >800) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssd14-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG good; rule follows the EEG: not applicable; tier agreed.
Plausibility: The EMG alone is plausible: a low sleep floor (about 10 uV) with sharp bursty wake, more wake in the dark and more sleep in the light (EMG-only sleep 74% light, 32% dark). The EEG cannot support any staging.
Concerns: EEG has persistent narrowband stripes (about 17-20 Hz and about 10 Hz) over all 24 h, with low-amplitude delta and no alternation. The old verdict agrees. The rule produced no hypnogram (all X), and no contested epochs were drawn for this baseline. Tier D (EMG only, wake/sleep) is right. Narrowband interference may be removable by a notch, but that is a separate decision.

## Recovery

![[2026-11-03-hlb-eeg-hlbssd14-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG good; rule follows the EEG: mostly; tier agreed.
Plausibility: Light wake 20% vs dark 54%, with sleep recovery early: plausible. EMG shows a clean low floor and bursty wake.
Concerns: EEG is poor (chip floor 126 uV, ungrounded-looking; 21% artefact). Hours 9-20 show delta rails (log delta 5-6) and broadband bright columns that are artefact or movement, so EEG is not independent there. Light hours (0-3, 5-8) show real slow-wave structure. EMG is the working channel, with heartbeat spikes on the floor that are not tone. Tier D is right. Rule follows the EMG; where EEG is usable it agrees. The HMM goes grey/R in the dark and is unreliable.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1146 | NR | medium | rule | Single short EMG burst (about 0.4 s) inside an otherwise quiet epoch; EEG irregular slow, theta/delta only 0.54; microarousal in NREM. |
| 2 | 4735 | NR | high | rule | Clear slow waves, EMG burst about 1 s only (< half) amid a quiet floor with heartbeat spikes. |
| 3 | 11489 | NR | medium | rule | EMG at floor with heartbeat spikes only (no tone), theta/delta 0.29, delta near NR median; wake burst starts in the next epoch. |
| 4 | 12349 | W | high | rule | EMG burst from the start through the whole epoch (2.6x cut). |
| 5 | 15440 | W | medium | rule | EMG bursts over more than half of the epoch (about 0.8-3 s), 2.1x cut, wake bout on both sides; HMM R not supported. |
| 6 | 15816 | W | high | rule | Repeated strong EMG bursts across about 3.5 s of the epoch. |
| 7 | 16567 | W | medium | rule | Continuous noisy EMG at about 1.1x cut for the whole epoch and the neighbours; no atonia, so HMM R is wrong. |
| 8 | 17158 | NR | medium | rule | EMG at floor with small spikes only, delta near NR median, theta/delta 0.42; arousal island with NREM EEG. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD14_R_epochs.png`.


---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSD07: EEG re-score 2026-11, baseline tier X, recovery tier X"
tags: [eeg, hlb, mouse, hlbwsd]
---

# HLBWSD07: W-SD (water, sleep deprivation), rig D1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **X** → nothing. screen
> - **Recovery:** tier **X** → nothing. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | X | X |
| hours usable, EEG + EMG | 0 | 0 |
| … of them light | 0 | 0 |
| … of them dark | 0 | 0 |
| hours usable, EEG alone | 1 | 0 |
| hours usable, EMG alone | 13 | 20 |
| EMG separability η (gap; ≥ 0.70) | 0.865 | 0.737 |
| η, SleepStager 20–90 Hz EMG | 0.723 | 0.733 |
| δ AUC, NR vs W (≥ 0.75) | 0.794 | 0.106 |
| EEG median log10 δ (2–4) | 3.26 | 4.64 |
| EEG-alone state changes / h (≥ 5) | 47.7 | 31.4 |
| κ rule vs HMM | 0.09 | 0.47 |
| κ NREM, rule vs EEG alone | 0.38 | -0.20 |
| κ rule, gap vs 20–90 Hz EMG | 0.55 | 0.78 |
| artifact epochs % | 79.7 | 23.5 |
| EEG 60 Hz, median µV | 5757 | 525 |
| EMG 60 Hz, median µV | 1324 | 815 |
| wake % light (rule) | – | – |
| wake % dark (rule) | – | – |
| NREM % light, EEG alone | 72.5 | – |
| NREM % dark, EEG alone | – | – |
| sleep % light, EMG alone | 31.0 | 18.2 |
| sleep % dark, EMG alone | 53.3 | 10.9 |
| r@1min (project definition) | – | – |
| old verdict reason | rung 2 CONNECTION FAIL: 2.7% usable, longest unbroken block 2.5 min | rung 2 CONNECTION FAIL: 0.1% usable, longest unbroken block 0.2 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsd07-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG bad; rule follows the EEG: not applicable; tier agreed.
Plausibility: Not plausible: 75% EEG artefact, 60 Hz 5757 uV in the EEG and 1324 uV in the EMG, broadband bright spectrogram all day with delta flat (~3.8-4.0 log10) and no alternation, no light/dark difference (EMG-only wake dark minus light -17), rule and HMM disagree (kappa 0.09).
Concerns: EMG is two-level (flat ~500-1000 uV plateau vs 2-3 uV floor) with no bursts, which is technical, so the rule's 'wake' is mostly signal loss. The old rejection and tier X agree and I see no hours worth rescuing. No contested epochs were drawn for this recording.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsd07-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG bad; rule follows the EEG: not applicable; tier agreed.
Plausibility: Rule scores 98.7% wake (99.7% light, 97.8% dark): not physiological, no light/dark difference (+7 pts) and no sleep after SD. This is a recording failure, not behaviour.
Concerns: EEG is railed (log10 delta flat at ~4.8 for most of the 20 h) or flat/dead (delta ~0) in short blocks, with no wake/sleep alternation; AUC 0.11. EMG gap RMS sits at 300-600 uV almost permanently, above its own cut (142), and raw EMG has ~815 uV of mains: a noisy open lead, not tone. The 7 'both_ok' hours (3 light, 4 dark) are false passes and should be dropped. NR calls come from flat EEG segments (NR median delta 0.2), not slow waves. X is right.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 7559 | W | low | rule | EMG sustained at 1.2x cut across the epoch, no atonia; the EEG is flat so the HMM NR has no sleep evidence. Low because EMG on this mouse is noisy. |
| 2 | 8078 | W | high | rule | EMG saturates the row at 4x cut for the whole epoch, EEG shows irregular activity; HMM R is impossible with this muscle activity. |
| 3 | 10550 | uncertain | low | neither | EEG is a flat line (delta 0.04), which is a lost signal rather than NREM; EMG is continuously active at 0.7x cut without atonia. |
| 4 | 10559 | W | high | rule | Dense EMG at 3.8x cut throughout; HMM NR depends on a flat EEG. |
| 5 | 10799 | W | medium | rule | EMG burst train over more than half the epoch, tone 2.0x cut; EEG flat so HMM NR is unsupported. |
| 6 | 14489 | uncertain | low | neither | EEG flat (delta 0.26), EMG 0.83x cut with one short burst and no clean atonia; neither staging has real evidence. |
| 7 | 14659 | W | high | rule | EMG 3.3x cut and dense; EEG irregular fast activity; HMM R impossible without atonia. |
| 8 | 14831 | W | high | rule | EMG fills the row at 3.8x cut, EEG desynchronised and irregular, no atonia. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD07_R_epochs.png`.


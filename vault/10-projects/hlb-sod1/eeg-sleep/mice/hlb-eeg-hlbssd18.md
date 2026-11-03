---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD18: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD18: S-SD (SOD1, sleep deprivation), rig D2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** yes.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | A |
| hours usable, EEG + EMG | 24 | 19 |
| … of them light | 12 | 8 |
| … of them dark | 12 | 11 |
| hours usable, EEG alone | 24 | 20 |
| hours usable, EMG alone | 24 | 19 |
| EMG separability η (gap; ≥ 0.70) | 0.892 | 0.846 |
| η, SleepStager 20–90 Hz EMG | 0.732 | 0.708 |
| δ AUC, NR vs W (≥ 0.75) | 0.932 | 0.947 |
| EEG median log10 δ (2–4) | 3.11 | 3.11 |
| EEG-alone state changes / h (≥ 5) | 29.3 | 35.0 |
| κ rule vs HMM | 0.78 | 0.83 |
| κ NREM, rule vs EEG alone | 0.86 | 0.81 |
| κ rule, gap vs 20–90 Hz EMG | 0.96 | 0.96 |
| artifact epochs % | 0.2 | 27.3 |
| EEG 60 Hz, median µV | 72 | 113 |
| EMG 60 Hz, median µV | 40 | 49 |
| wake % light (rule) | 34.1 | 16.4 |
| wake % dark (rule) | 68.2 | 53.0 |
| NREM % light, EEG alone | 49.9 | 62.3 |
| NREM % dark, EEG alone | 25.5 | 29.9 |
| sleep % light, EMG alone | 65.1 | 82.4 |
| sleep % dark, EMG alone | 31.3 | 45.9 |
| r@1min (project definition) | 0.682 | 0.046 |
| old verdict reason | rung 3 SCOREABILITY FAIL: 23.96 h in 21 block(s), r@1min 0.028 | rung 3 SCOREABILITY FAIL: 10.60 h in 77 block(s), r@1min -0.023 |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssd18-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible: wake 34% in the light and 68% in the dark, clean alternation of delta bands and theta bouts, and a sharp EMG sleep floor (about 4 uV) versus wake. All 24 h usable.
Concerns: The old rung-3 verdict (r@1min 0.028) looks wrong for this animal. EMG separation is excellent (eta 0.89), and rule, HMM and EEG-only agree (kappa 0.78/0.86). Only issues are a single narrowband spike around hour 2.7 and a few seconds of flat or noisy EMG in the dark. HMM tends to over-call R at transitions after wake.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 5129 | uncertain | low | neither | EMG burst for about the second half of the epoch (1.0x cut) that continues into the next epoch, while the EEG keeps slow waves (delta 3.24). It could be a microarousal in NR or a brief wake onset. The HMM's R is wrong. |
| 2 | 5897 | W | high | rule | A sustained EMG burst covers nearly the whole epoch (2x cut). |
| 3 | 5900 | NR | low | rule | EMG is atonic, delta is a little below NR median and theta is not dominant, 12 s after a wake bout. It looks like light NREM. REM would not follow wake directly, and no regular theta is visible. |
| 4 | 8646 | NR | low | rule | Atonic EMG after a wake burst a few epochs earlier, delta lowish and sigma low, theta/delta under 1. Light NREM rather than REM, but the transition is soft. |
| 5 | 9641 | NR | medium | rule | A burst in the previous epoch, then EMG back at floor (0.54x) with slow waves and delta 3.21. Post-arousal NREM. |
| 6 | 9839 | R | medium | rule | Inside a clear REM bout: regular theta and low delta in the neighbours, EMG at floor. Fading theta in this single epoch does not end REM (rule R*). |
| 7 | 13548 | NR | low | rule | EMG at floor (0.6x), delta a little below median and theta/delta only about 0.6, much lower than this mouse's REM epochs (1.2-1.7). Light NREM, so the HMM's R is not supported. |
| 8 | 17317 | NR | high | rule | Large slow waves, delta above NR median (3.66), theta/delta 0.4 and a flat EMG. Clear NREM. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD18_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The old verdict was a rung-3 fail with r@1min 0.028, while the new score gives 0.682 on the same data. The new r is the within-block sleep persistence computed on the new labels. It agrees with whole-record persistence (0.77), and the old value came from the 10-124 Hz EMG band, which on this rig is mostly mains. I found nothing that refutes the window. The EMG has a sleep floor of 3.6-5 uV against a wake median of 39 uV (ratio 7.8). 1-min delta-EMG r is -0.73. The EEG-only HMM calls 1% of EMG-wake epochs NREM. There are no EMG artifacts and 0.17% EEG artifacts. Wake is 34/68% light/dark. Checked: score.json (eta 0.892, AUC 0.932, 24/24 h, kappa 0.78/0.86); features/hypnogram: delta-EMG alternation, EMG floor vs wake, EEG-only vs EMG cross-check, whole-record r@1min recomputed (0.77), artifact census (none).

## Recovery

![[2026-11-03-hlb-eeg-hlbssd18-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible: light wake 16% vs dark 53%, clear delta bursts in the light, sleep-rich early recovery, REM concentrated in light. The old verdict (rung 3 fail) was wrong for this mouse.
Concerns: Hour 16-17 is dropped because of flat EMG plateaus at about 400 uV (and a grey HMM); this is probably a grooming/feeding wake or a technical stretch, so dropping it is fine. A few flat EMG plateaus in the dark are technical-looking but are scored W anyway with no harm. The rule's wake/REM islands right after wake bursts need care: when the EMG sits at 0.5-0.85x the cut (3-4x the sleep floor of 0.18x) while theta is regular, it looks like quiet wake with theta rather than REM (see epochs 8895 and 15811).

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 3525 | R | low | hmm | Flat atonic EMG at the end of an R bout, sigma low, delta below NR median; theta/delta has faded to 0.6, but delta has not returned and tone only returns in the next epoch. |
| 2 | 3545 | uncertain | low | neither | Atonic, theta/delta 0.94 at the R-to-NR boundary with sigma rising and delta returning in the next epoch; NR and R both fit. |
| 3 | 4113 | W | high | rule | EMG continuously raised (0.75x, about 4x this mouse's floor) between large wake bursts, no slow waves or spindles; quiet wake. |
| 4 | 6056 | R | high | rule | Atonic flat EMG (0.24x), theta/delta 1.2, delta below NR median, in a sustained R bout. |
| 5 | 8895 | W | low | rule | Immediately after heavy bursts, EMG stays at 0.5x (about 3x the sleep floor) with regular theta and no spindles: quiet wake with theta; not atonic enough for REM, but the neighbouring epochs are scored sleep at the same EMG, so it is a close call. |
| 6 | 15638 | NR | medium | rule | Irregular slow waves with delta near NR median, EMG 0.35x with no burst in the epoch; one burst 7 s earlier. |
| 7 | 15739 | NR | medium | rule | Delta near NR median, EMG quiet (0.4x), theta/delta 0.7; small bursts are in the neighbours only. |
| 8 | 15811 | W | low | hmm | After two burst epochs, EMG stays at 0.7-0.86x cut (3-4x the sleep floor) for 20+ s with regular theta and low delta: quiet wake, not atonic REM; rule's W-to-R switch is questionable. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD18_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: Usable, but the reported numbers are biased. 27% of epochs are EMG rail-touch 'artifact' (38% of dark epochs, 0% at baseline). These are flat ~400 uV plateaus during vigorous wake (85% EEG-only WR). Excluding them pushes wake down: light/dark wake 16.4/53.0% becomes 25.4/69.7% if they are counted as wake. The same fragmentation drives the score.json r@1min of 0.046: within-block persistence is computed on blocks broken at every movement, while the whole record gives 0.72. Neither point removes usability. 19 of 20 h pass (17 needed). The EMG floor is 2.9-4.9 uV against a wake median of 42 uV, 1-min delta-EMG r is -0.73, AUC is 0.947, the EEG-only call takes only 9% of EMG-wake epochs, and the early recovery is sleep-rich with clear delta banding. Quote wake percentages with the artifact caveat, or recompute them with rail epochs counted as wake. Checked: score.json (eta 0.846, AUC 0.947, both ok 19 h = 8L/11D, kappa 0.83/0.81, EMG artifact 27.2%); blocks_1h (ZT20 dropped, dark clean counts ~525-650/900); overview.png (clean delta/theta alternation, rail plateaus in the dark); artifact census (100% rail, median 361 uV, 85% EEG-only WR); wake % recomputed with artifact epochs counted; whole-record r@1min recomputed (0.72); P(EEG-only NR | EMG W) 0.09.


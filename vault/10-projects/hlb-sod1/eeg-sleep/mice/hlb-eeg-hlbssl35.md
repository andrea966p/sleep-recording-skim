---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSL35: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbssl]
---

# HLBSSL35: S-SL (SOD1, ad libitum), rig C1

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
| EMG separability η (gap; ≥ 0.70) | 0.839 | 0.839 |
| η, SleepStager 20–90 Hz EMG | 0.729 | 0.732 |
| δ AUC, NR vs W (≥ 0.75) | 0.940 | 0.937 |
| EEG median log10 δ (2–4) | 3.28 | 3.22 |
| EEG-alone state changes / h (≥ 5) | 30.8 | 32.5 |
| κ rule vs HMM | 0.89 | 0.69 |
| κ NREM, rule vs EEG alone | 0.86 | 0.86 |
| κ rule, gap vs 20–90 Hz EMG | 0.94 | 0.96 |
| artifact epochs % | 0.0 | 0.0 |
| EEG 60 Hz, median µV | 84 | 12 |
| EMG 60 Hz, median µV | 5 | 5 |
| wake % light (rule) | 27.5 | 30.5 |
| wake % dark (rule) | 61.5 | 69.2 |
| NREM % light, EEG alone | 57.3 | 53.3 |
| NREM % dark, EEG alone | 32.0 | 26.4 |
| sleep % light, EMG alone | 72.6 | 69.5 |
| sleep % dark, EMG alone | 39.1 | 31.3 |
| r@1min (project definition) | 0.743 | 0.774 |
| old verdict reason | 23.99 h in 1 block(s), r@1min 0.677 | rung 2 CONNECTION: chip floor is carrying signal: its slope threshold is -3.07 (valid floors are flatter than -1.90) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssl35-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 27.5 % light vs 61.5 % dark, long EMG plateaus in the dark, delta alternation clean, 24 of 24 h usable. Rule and HMM agree (kappa 0.89).
Concerns: No technical problems; heartbeat spikes on the floor are handled by the tone measure. A few contested NR/R calls are borderline (theta/delta near 1 with sigma still high, i.e. spindle-theta mixtures), which affects only REM labelling.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2135 | W | high | rule | Continuous raised EMG (tone 1.0x cut) between huge bursts of a wake bout (3-4x cut in neighbours); delta at wake level. |
| 2 | 5130 | NR | medium | rule | Decaying arousal fuzz in the first ~1 s then floor (tone 0.46x), delta 3.38, theta/delta 0.31; sleep after a brief wake, below the cut. |
| 3 | 6382 | NR | low | rule | Theta/delta flips between 0.4 and 1.0 across neighbours, sigma stays 2.7-3.0 (spindles) and delta 3.2-3.5; no sustained theta, so no clear REM bout. |
| 4 | 7528 | uncertain | low | neither | Theta/delta 1.07-1.28 for three epochs with delta 3.2 but sigma still 2.96-3.06 and a mixed trace; REM-onset or NR with spindles cannot be decided. |
| 5 | 8736 | R | low | hmm | Follows an R bout, delta still low (3.19), sigma low 2.37, EMG atonic 0.28x; theta fades but delta has not returned and W only arrives later. |
| 6 | 13605 | uncertain | low | neither | Sits inside a theta-rich run (neighbours theta/delta 1.2 and 1.6, sigma low) but this epoch has theta/delta 0.73 and delta 3.43 close to NR; EMG atonic, trace mixed. |
| 7 | 16139 | W | low | hmm | Continuous raised EMG fuzz (0.93x cut, tone 0.61x versus a ~0.4x floor) with a burst at the end, preceded by W-like epochs; theta/delta 1.08 with low delta is wake theta, not atonic REM. |
| 8 | 19990 | R | low | hmm | Sigma drops to 2.39, EMG atonic at 0.45x, theta/delta rising (0.68, 0.71, 0.46 on the following epochs the rule itself calls R); onset of a short bout, delta 3.29 not high. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL35_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbssl35-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake 30.5 % light vs 69.2 % dark, clear alternation of bright delta and wake, bursty EMG with low sleep floor. Rule vs EEG-only NR kappa 0.86 and AUC 0.94.
Concerns: The HMM is unreliable in the dark phase: it labels many long, high-EMG stretches (EMG 1.5-6x the cut, saturated rows) as R, which is physiologically impossible and explains the low rule-HMM kappa (0.70). Those are HMM errors, not rule errors. I would not use the HMM here, or the rule-HMM disagreement as a quality flag. EMG is the weakest of the recordings in eta_ss60 (0.73) but the gap-EMG eta 0.84 is fine. All 24 h usable; old NO VERDICT was floor-slope only.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 4488 | W | medium | rule | EMG bursts fill most of the 4 s at 1.6x cut (tone 1.6x) with active-wake theta (theta/delta 1.59, delta low); HMM R ignores the muscle. |
| 2 | 8019 | NR | low | rule | EMG very flat 0.24x, low-amplitude EEG with delta 3.00, sigma 2.42, theta/delta 0.63; could also be light R but there is no theta regularity, and rule and HMM both say NR. |
| 3 | 10639 | NR | low | rule | EMG flat 0.40x, delta 3.00 below NR median and sigma 2.59, theta/delta 0.77, in a run of NR epochs with delta 3.4 either side; light NR near REM onset, not clearly R. |
| 4 | 10980 | W | medium | rule | EMG active throughout with a large burst in the last 0.9 s, RMS 1.78x, neighbours 0.8-2.1x in a wake bout, theta/delta 0.92 with delta low; HMM R wrong. |
| 5 | 14274 | W | high | rule | EMG bursts cover most of the epoch at 1.9x cut, tone 1.8x; HMM R is wrong. |
| 6 | 16394 | W | high | rule | EMG continuously above the cut (2.5x, tone 2.3x) for the whole row. |
| 7 | 16529 | W | high | rule | EMG saturated at 4-6x cut across the whole row; an R label is impossible. |
| 8 | 21142 | W | medium | rule | EMG bursts through most of the epoch, RMS 1.5x, tone 1.1x, neighbours 2-2.7x, fast low-amplitude EEG with delta 2.79 and low sigma. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL35_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The second scorer fails in the dark. The HMM labels 22-41 % of dark-hour epochs R (ZT12-23), while the rule gives 0-4 %, mostly on high-EMG stretches. That is why rule-HMM kappa is only 0.695. The ss60 EMG eta (0.73) is also close to the 0.70 bar. Neither problem touches the rule or the EEG: the rule's NR follows delta in every hour (per-hour AUC 0.87-0.97, light 0.91, dark 0.95; rule vs EEG-only NR kappa 0.86). Checked: I read score.json, blocks_1h.csv and features/hypnogram parquet and recomputed per-hour stats. EEG total power and 60 Hz (12 uV) are flat for all 24 h, so there is no step change. Rule-NR EMG sits at 0.34x the cut (median) in the light and 0.50x in the dark (p90 0.55/0.78). Delta and EMG are anti-correlated in every hour (r -0.14 to -0.71). Wake is 30.5 % light vs 69.2 % dark, and EMG-only wake is 38 points higher in the dark. Median bouts are NR 17 and R 7 epochs. Only 0.1-0.2 % of W epochs carry NR-level delta with EMG under 1.5x the cut. Old NO VERDICT came only from the floor-slope gate.


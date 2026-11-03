---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSL34: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbssl]
---

# HLBSSL34: S-SL (SOD1, ad libitum), rig B2

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
| hours usable, EEG + EMG | 24 | 24 |
| … of them light | 12 | 12 |
| … of them dark | 12 | 12 |
| hours usable, EEG alone | 24 | 24 |
| hours usable, EMG alone | 24 | 24 |
| EMG separability η (gap; ≥ 0.70) | 0.839 | 0.860 |
| η, SleepStager 20–90 Hz EMG | 0.698 | 0.775 |
| δ AUC, NR vs W (≥ 0.75) | 0.929 | 0.899 |
| EEG median log10 δ (2–4) | 3.21 | 3.25 |
| EEG-alone state changes / h (≥ 5) | 24.5 | 33.2 |
| κ rule vs HMM | 0.86 | 0.83 |
| κ NREM, rule vs EEG alone | 0.86 | 0.84 |
| κ rule, gap vs 20–90 Hz EMG | 0.92 | 0.97 |
| artifact epochs % | 0.0 | 0.0 |
| EEG 60 Hz, median µV | 93 | 12 |
| EMG 60 Hz, median µV | 67 | 202 |
| wake % light (rule) | 25.0 | 24.0 |
| wake % dark (rule) | 65.5 | 65.3 |
| NREM % light, EEG alone | 56.0 | 56.3 |
| NREM % dark, EEG alone | 27.4 | 27.9 |
| sleep % light, EMG alone | 75.4 | 75.6 |
| sleep % dark, EMG alone | 36.3 | 35.0 |
| r@1min (project definition) | 0.769 | 0.761 |
| old verdict reason | rung 3 SCOREABILITY FAIL: 23.99 h in 1 block(s), r@1min 0.225 | rung 2 CONNECTION FAIL: 19.4% usable, longest unbroken block 5.5 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssl34-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG partial; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 25 % light vs 59 % dark, bouts consistent with the EMG, delta alternation clear. Hours 18-19 and 21-22 are screened out (wake-dominated dark hours).
Concerns: EMG has strong regular heartbeat spikes on the sleep floor and the floor sits at about 0.5x the wake cut, so there is less margin than in other mice (eta_ss60 0.698 gives tier C with the other EMG estimator). Tier A under the gap EMG is therefore somewhat fragile, but the EEG independently agrees (kappa NR rule vs EEG-only 0.86), so the A call is supported. Old rejection (r@1min 0.225, EMG band mostly mains) looks wrong. Several W-vs-NR contested epochs are near the cut (tone 0.7-0.9x); they are quiet wake inside wake bouts.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1410 | W | medium | rule | EMG active throughout the epoch (bursts at 1 s and 3.4 s over a raised baseline, 0.84x cut) inside a bout of 1.4-2.5x cut; low-amplitude EEG, no slow waves. |
| 2 | 3221 | W | medium | hmm | Continuous bursting EMG at 0.75x cut over the whole epoch and in all neighbours, low-amplitude desynchronised EEG, no spindles or slow waves; well above this mouse's sleep floor (~0.47x). |
| 3 | 4019 | uncertain | low | neither | Theta/delta 3.18 and delta 3.14 low with atonic EMG favour REM, but sigma rises to 3.18 and the waxing 10-12 Hz burst looks like a spindle; isolated single epoch between NR epochs. |
| 4 | 4440 | R | medium | hmm | Within a REM-like run (theta/delta 1.05, 2.17, 1.14), flat EMG with heartbeat spikes only; the W burst starts in the next epoch, so this is the end of the bout. |
| 5 | 9999 | R | medium | hmm | First epoch with theta/delta 1.41 after NR (0.5-0.8), delta drops to 3.10, sigma drops 3.10 to 2.59, atonic; next epoch continues. |
| 6 | 10665 | R | medium | hmm | Three of four epochs with theta/delta 1.1-1.3 and delta about 3.0 below NR median, low sigma, EMG at floor (fuzz slightly raised, 0.51x). |
| 7 | 11183 | W | medium | rule | Quiet wake inside a wake bout: continuous EMG at 0.78x, tone just under the cut, delta below NR median, no spindles (sigma 2.49); neighbours 1.5-1.9x. |
| 8 | 15668 | W | medium | hmm | Theta-dominant EEG (theta/delta 4.1, delta 2.63) but EMG not atonic (0.93x, tone 0.85x, activity throughout) and preceded by W; REM is not entered from wake, so quiet or theta wake. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL34_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The tier depends on the estimator: eta_ss60 is 0.698, just under the 0.70 gate, which gives tier C under the other EMG estimator, and the sleep floor sits at about 0.45x the cut with heartbeat spikes, the narrowest margin of the baselines. That is a threshold edge on a recording-level statistic, not a hypnogram difference: the gap and ss60 hypnograms agree (kappa 0.92), and the EEG independently confirms (delta AUC 0.93, NR rule vs EEG-only kappa 0.86, 0.4 % of W epochs at NR-level delta). The 60 Hz amplitude is anti-correlated with wake (AUC 0.23). The 2 dropped hours (ZT18, ZT21) are 96-97 % wake with wake-level delta. They are excluded because the screen cannot test an all-wake hour, not because they are bad, so 22-24 h are usable. Checked: score.json (eta_gap 0.839 vs eta_ss60 0.698, kappa_gap_ss60 0.919), blocks_1h.csv, overview PNG, per-hour delta, EMG floor and wake level, 60 Hz correlation and AUC, W epochs with NR delta, previous reviewer's epoch calls

## Recovery

![[2026-11-03-hlb-eeg-hlbssl34-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake 24.0 % light vs 62.5 % dark, NREM bright delta in the first 8 h, REM-like theta episodes, two-level EMG with bursty wake and a low sleep floor with heartbeat. Kappa rule-HMM 0.84, rule vs EEG-only NR 0.84.
Concerns: The old verdict NOT SCOREABLE (19.4 % usable) was a wrong rejection: the raw EMG is dominated by 60 Hz (202 uV), which the old 10-124 Hz band could not handle; with the notched EMG the recording is clean (eta 0.86). The one hour dropped, ZT22, is 96 % wake (floor test and delta AUC cannot be computed with 1 % NREM), so it is a genuinely wake hour that the screen drops by construction, not a bad one; the EEG alone is fine there.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 96 | R | medium | rule | Mid-REM epoch: EMG flat 0.37x with heartbeat; delta 3.53 and theta/delta 0.66 here look NREM-like because of one large wave, but both neighbours on each side are clear R (delta about 2.9, theta/delta 1.7-2.6); a single dip does not end the bout. |
| 2 | 2441 | R | medium | hmm | EMG flat 0.30x, delta 2.95 low, theta/delta 2.04, sigma 2.57, regular fast theta in the trace; rule NR is too conservative. |
| 3 | 3103 | uncertain | low | neither | Wake EMG decays into the start of the epoch, then flat 0.45x with low delta 2.95 and theta/delta 0.86; this is the first quiet epoch after wake, R directly from wake is unlikely but it is not clearly NR either. |
| 4 | 3834 | NR | medium | rule | EMG flat 0.35x but sigma 3.02 (spindle range high, same in neighbours), delta 3.23, theta/delta 0.69; no sigma drop so not R yet. |
| 5 | 12065 | NR | medium | rule | EMG burst only in the last 1.2 s (under half the epoch), tone 0.47x spike-free, EEG still sleep-like (delta 3.10, sigma 2.68) with NREM neighbours: microarousal. |
| 6 | 12676 | W | medium | rule | Quiet wake in a wake bout: EMG fuzz continuous at 0.8x with neighbours 1.1-1.6x, delta 3.16 below NR level, no spindles; rule and HMM agree. |
| 7 | 14260 | NR | medium | rule | Delta 3.52 at NR median, theta/delta 0.36, sigma 2.69, EMG flat 0.53x; the surrounding R-like epochs do not extend into this one. |
| 8 | 14273 | NR | low | rule | Sigma high at 2.91, delta 3.30, theta/delta 0.76, EMG 0.49x flat; the burst is in the previous epoch, and theta is not regular enough for R. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL34_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: Its EEG contrast is the weakest of the A tiers (delta AUC 0.90). NR delta sags in ZT12-17 (log10 3.29-3.50 against 3.5-3.6 in the light), leaving only about 0.3 log units of W/NR separation in the early dark. Raw EMG mains is 202 uV. The mains objection fails: 60 Hz is anti-correlated with wake (AUC 0.14), and only 2 % of W epochs reach NR-level delta. The one dropped hour, ZT22, is 96 % wake with wake-level delta, so it is excluded by construction, not because it is bad. The old 19.4 %-usable rejection came from the mains-dominated 10-124 Hz band. Checked: score.json (auc 0.899, eta 0.86, kappa_gap_ss60 0.967), blocks_1h.csv, overview PNG, per-hour NR and W delta (dark sag), EMG floor, 60 Hz correlation and AUC, W epochs with NR delta


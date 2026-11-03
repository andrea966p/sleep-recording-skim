---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSL40: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbssl]
---

# HLBSSL40: S-SL (SOD1, ad libitum), rig D1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** yes.
> - Old pipeline: baseline NOT SCOREABLE, recovery NO VERDICT.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | A |
| hours usable, EEG + EMG | 24 | 23 |
| … of them light | 12 | 12 |
| … of them dark | 12 | 11 |
| hours usable, EEG alone | 24 | 24 |
| hours usable, EMG alone | 24 | 23 |
| EMG separability η (gap; ≥ 0.70) | 0.843 | 0.843 |
| η, SleepStager 20–90 Hz EMG | 0.711 | 0.760 |
| δ AUC, NR vs W (≥ 0.75) | 0.943 | 0.919 |
| EEG median log10 δ (2–4) | 3.26 | 3.28 |
| EEG-alone state changes / h (≥ 5) | 27.9 | 37.1 |
| κ rule vs HMM | 0.73 | 0.94 |
| κ NREM, rule vs EEG alone | 0.89 | 0.87 |
| κ rule, gap vs 20–90 Hz EMG | 0.92 | 0.91 |
| artifact epochs % | 0.0 | 0.0 |
| EEG 60 Hz, median µV | 25 | 8 |
| EMG 60 Hz, median µV | 51 | 9 |
| wake % light (rule) | 35.2 | 38.5 |
| wake % dark (rule) | 73.4 | 58.9 |
| NREM % light, EEG alone | 52.1 | 51.2 |
| NREM % dark, EEG alone | 22.8 | 33.2 |
| sleep % light, EMG alone | 65.0 | 61.6 |
| sleep % dark, EMG alone | 27.4 | 41.7 |
| r@1min (project definition) | 0.803 | 0.772 |
| old verdict reason | rung 2 CONNECTION FAIL: 66.4% usable, longest unbroken block 13.7 min | rung 2 CONNECTION: chip floor is carrying signal: its slope threshold is -2.88 (valid floors are flatter than -1.90) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssl40-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 35 % light vs 73 % dark, very consolidated dark wake (ZT12-19), strong delta alternation in the light. Rule follows EMG and EEG; EEG-only agrees on NR (kappa 0.89).
Concerns: The rule/HMM kappa of 0.74 is low only because the HMM calls many wake epochs R (theta-rich wake with low delta, e.g. epochs 2970, 9373, 15221, 16197) while EMG is 2-5x above the cut. The rule is right there; the HMM is the one to distrust in this mouse. Old rung-2 rejection (66 % usable) looks wrong. High EMG wake bouts versus a flat floor are clean.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1455 | NR | high | rule | Large slow waves, delta 3.54, sigma 2.79; a single ~0.3 s EMG blip only (microarousal); HMM agrees. |
| 2 | 2970 | W | high | rule | EMG at 2.8x cut, active most of the epoch; HMM R is a theta-rich wake artefact. |
| 3 | 5601 | W | medium | rule | Lower but continuous EMG (0.91x, tone 0.72x) between bursts of a wake bout (4.5x next epoch), delta 3.22, no spindles: quiet wake. |
| 4 | 9373 | W | high | rule | EMG bursts fill most of the epoch (3.8x cut); HMM R is wrong, muscle is clearly active. |
| 5 | 15221 | W | high | rule | Sustained EMG 2.3x cut with bursts across the epoch; theta is wake theta. |
| 6 | 15515 | W | high | rule | Continuous strong EMG (2.1x cut) all epoch long, not atonic; HMM R rejected. |
| 7 | 16197 | W | high | rule | EMG 4.9x cut, bursts across most of the epoch. |
| 8 | 17891 | NR | low | rule | Short sleep island between wake: EMG flat at 0.44x tone with no burst for the full 4 s, delta 3.30, sigma 2.41, moderate slow waves; wake resumes in the next epoch (2x cut). |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL40_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The second scorer disagrees (rule-HMM kappa 0.735, the lowest of the A tiers): the HMM labels many dark-phase wake epochs as R. Checked: those epochs carry EMG at 2-5x the cut, and the HMM's W share in dark hours (40-66 %) is far below the bursty EMG's 88-100 %, so the HMM is wrong and the rule is right. The independent EEG check is strong (AUC 0.94, NR rule vs EEG-only kappa 0.89, 0.4 % of W epochs at NR delta). A smaller oddity: ZT0-1 is 67 % / 53 % wake at lights-on, unusual for a baseline, probably a disturbance at the window start. That is a reason to check the room log, not a signal fault. Checked: score.json, blocks_1h.csv, overview PNG (HMM green R inside dark wake plateaus), per-hour rule W vs HMM W, EMG wake level, delta NR/W, 60 Hz AUC 0.30, previous reviewer's epoch panels

## Recovery

![[2026-11-03-hlb-eeg-hlbssl40-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake 38.5 % light vs 58.9 % dark; the light-phase wake is the highest of the batch but with a normal alternation of delta bands, and the dark phase is mostly wake with a few NREM blocks. Rule-HMM kappa 0.94.
Concerns: The one dropped hour (ZT18) is an all-wake hour that the screen drops by construction; not bad signal. A thin vertical stripe at ZT12 in the spectrogram is a one-minute transient. Several epochs in the light phase sit in a long run of EMG at 0.8-1.1x cut (ZT6, ZT9-11), where rule and HMM differ about microarousals; this is a boundary-sensitivity issue, not a quality problem. Old NO VERDICT was floor-slope only.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2249 | NR | medium | rule | EMG very flat 0.20x, sigma 3.07 high (spindles) and delta 3.40 close to NR median; theta/delta 1.19 is not enough for R with sigma still up. |
| 2 | 2382 | W | high | rule | Continuous bursty EMG at about 1.0x cut with tone 0.84x, neighbours 1.0-1.4x, low-amplitude EEG with no slow waves; quiet wake in a wake bout. |
| 3 | 5774 | NR | low | rule | Slow waves with delta 3.50 at NR level and theta/delta 0.24, while the EMG sits near the cut (tone 0.79x) with a couple of small bursts; one-sided muscle arousal inside NREM, but a close call. |
| 4 | 8118 | R | medium | hmm | EMG flat at 0.44x with heartbeat, delta 3.05 low, theta/delta 1.10 after 1.28, sigma 2.65 lowered; REM-like, the rule's NR is the more conservative call. |
| 5 | 8432 | NR | medium | rule | One tiny burst in the first 0.3 s after a wake bout (tone without spikes 0.41x), then flat EMG; the burst is well under half the epoch; delta 3.07, theta/delta 0.72, sigma 2.57 so NR (not R) at this point. |
| 6 | 10382 | W | low | hmm | Slow waves of the previous epochs have gone: low-amplitude fast EEG with sigma 2.18 and delta 3.14, EMG has a burst at the start and a raised fuzz after, and a larger burst follows (3.1x) in the next epoch; both channels activated, start of a wake bout. |
| 7 | 13744 | W | low | hmm | EMG bursts build from -2 s through most of the epoch (0.93x, tone 0.79x), delta falling (3.20) and sigma low (2.44), with wake epochs following; likely an arousal into wake but still a close call. |
| 8 | 17982 | NR | high | rule | EMG flat 0.38x with heartbeat, delta 3.42, sigma 3.05 (spindles); theta/delta 1.16 is only the prelude to R in the following epochs. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL40_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: Light-phase wake is the highest of the A recordings (38.5 %). It comes in a regular alternation of wake-heavy hours: ZT0, 2, 4, 6, 8 and 11 are 48-60 % wake. That could be handling or disturbance rather than spontaneous behaviour, but the signals themselves give no reason to reject it. Rule NR follows the EEG in those hours (per-hour AUC 0.86-0.94). Checked: I read score.json, blocks_1h.csv and parquet stats. EEG and EMG 60 Hz are flat (8-10 uV) with no step. Rule-NR EMG sits at 0.34-0.37x the cut (p90 0.59-0.65). Delta AUC is 0.90 light and 0.94 dark; rule vs EEG-only kappa is 0.87, rule-HMM 0.94. The one dropped hour (ZT18) is 91 % wake, with an EMG p10 of 26 uV that sits at the cut. Wake is 38.5 % light vs 58.9 % dark; median bouts are NR 17 and R 8 epochs.


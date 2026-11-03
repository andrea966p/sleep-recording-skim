---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSL39: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbssl]
---

# HLBSSL39: S-SL (SOD1, ad libitum), rig C2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** yes.
> - Old pipeline: baseline NOT SCOREABLE, recovery SCOREABLE.

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
| EMG separability η (gap; ≥ 0.70) | 0.816 | 0.814 |
| η, SleepStager 20–90 Hz EMG | 0.784 | 0.769 |
| δ AUC, NR vs W (≥ 0.75) | 0.927 | 0.910 |
| EEG median log10 δ (2–4) | 3.27 | 3.29 |
| EEG-alone state changes / h (≥ 5) | 28.5 | 33.7 |
| κ rule vs HMM | 0.91 | 0.91 |
| κ NREM, rule vs EEG alone | 0.85 | 0.84 |
| κ rule, gap vs 20–90 Hz EMG | 0.96 | 0.96 |
| artifact epochs % | 0.2 | 0.3 |
| EEG 60 Hz, median µV | 43 | 10 |
| EMG 60 Hz, median µV | 76 | 10 |
| wake % light (rule) | 24.0 | 27.1 |
| wake % dark (rule) | 70.2 | 63.5 |
| NREM % light, EEG alone | 56.0 | 55.3 |
| NREM % dark, EEG alone | 26.0 | 28.5 |
| sleep % light, EMG alone | 75.6 | 72.1 |
| sleep % dark, EMG alone | 30.2 | 37.1 |
| r@1min (project definition) | 0.623 | 0.643 |
| old verdict reason | rung 3 SCOREABILITY FAIL: 23.84 h in 31 block(s), r@1min 0.090 | 23.83 h in 32 block(s), r@1min 0.546 |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssl39-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG partial; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 24 % light vs 70 % dark, consolidated dark wake plateaus, NR/R cycling in the light; rule, HMM and EEG-only mostly agree (kappa 0.91 / 0.85).
Concerns: EMG sleep floor is noisier and higher (tone 0.45-0.6x cut, fuzzy baseline, small bursts) than in the cleanest mice, so quiet wake vs light sleep is harder in the hours after arousals (epochs 1431, 4290, 15138). The EEG supports the hypnogram, so tier A holds. Old rejection (r@1min 0.09 with mains-dominated EMG band) looks wrong. EMG artefact 0.2 %.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1431 | W | low | hmm | Raised, continuous EMG fuzz (0.56x, tone 0.54x, 0.87x in the next epoch) after a W bout, delta 3.05 below NR median, low sigma 2.47, no slow waves: quiet wake. |
| 2 | 2288 | NR | medium | rule | Slow irregular waves with spindle-range activity (sigma 2.77), EMG at floor 0.52x with no bursts, delta 3.23; the wake burst only comes ~6 s later. |
| 3 | 4290 | W | low | hmm | Right after a large wake bout; EMG fuzz at 0.67x (floor ~0.5x), small burst at the start, delta 3.23 low, sigma 2.35 low, no slow waves or spindles: quiet wake or transition. |
| 4 | 4801 | R | low | hmm | Atonic EMG (0.49x, heartbeat only) after a wake bout, theta/delta 1.04, and the next two epochs are R in the rule; probable REM onset, trace not clearly regular theta. |
| 5 | 4931 | NR | low | hmm | Slow waves, delta 3.39, theta/delta 0.11 and low raised-EMG fraction, but several bursts add up to roughly 40 % of the epoch (1.57x cut): microarousal in NREM, near the half-epoch limit. |
| 6 | 10279 | NR | medium | rule | One burst of ~0.6 s plus a short tail (<half epoch) with NREM EEG (delta 3.28, theta/delta 0.27, slow waves); microarousal stays NR. |
| 7 | 15138 | W | medium | hmm | Continuous EMG activity throughout (0.95x cut, tone 0.93x) following a big wake bout (3.6x, 1.4x); delta 3.13 low, no spindles: quiet wake. |
| 8 | 17274 | NR | high | rule | Large slow waves, delta 3.63 above NR median, sigma 2.97; only a ~0.7 s EMG burst at the start, microarousal. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL39_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The EMG sleep floor is about 0.25-0.4x the cut in the light but rises to 0.54-0.76x in the dark (ZT13-22), so the margin between quiet wake and sleep shrinks just where the dark-phase wake percentage is measured. The rule's W/sleep boundary in the dark therefore carries more error than in the light. Against that: the EEG agrees (delta AUC 0.93, NR rule vs EEG-only kappa 0.85, 0.8 % of W epochs at NR-level delta), and the 60 Hz amplitude is anti-correlated with wake (AUC 0.17). The old r@1min 0.09 rejection was made on a mains-dominated EMG band. Treat dark quiet-wake boundaries as the soft spot, not grounds for a lower tier. Checked: score.json, blocks_1h.csv, overview PNG, per-hour EMG floor (median non-W gap/cut and p10), delta NR/W per hour, 60 Hz correlation and AUC, W epochs with NR-level delta, previous reviewer's epoch calls

## Recovery

![[2026-11-03-hlb-eeg-hlbssl39-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake 27.1 % light vs 63.5 % dark, long NREM blocks in the light and clear REM episodes ending in EMG bursts. Rule-HMM kappa 0.91. Old verdict SCOREABLE agrees.
Concerns: The EMG separation is the lowest of the batch (eta 0.81) and the dark-phase REM candidates sit on a slightly raised EMG floor (0.5-0.85x cut with twitch bursts). Several rule R vs HMM W disagreements in the dark (ZT11-22) are probably wake with theta rather than REM, because the muscle is not atonic; the rule may over-call REM there. Not a reason to change the tier.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 5771 | W | medium | rule | EMG burst from 1.5 s to the end (about 2.5 s of 4, more than half) at 2.4x cut, ending a clear R bout before it; neighbours W. |
| 2 | 8245 | W | low | rule | End of a clear R bout; EMG atonic for the first 1.5 s then bursting (large burst 3.2-4 s) with RMS 1.5x, EEG already activated (theta/delta 0.67, sigma 2.28); near half the epoch is active, so a close call. |
| 3 | 8255 | uncertain | low | neither | EMG 0.54x slightly raised and steady, sigma 2.93 high, delta 3.21, theta/delta 0.74; next epochs look R (theta/delta 1.4) but this one still has NREM-like sigma. |
| 4 | 10577 | R | medium | rule | Preceded by strong R theta, EMG shows brief twitch bursts (under half the epoch) on a mostly flat baseline at 0.84x, delta low; twitches in REM rather than wake. |
| 5 | 15631 | uncertain | low | neither | Arousal 4-8 s earlier, EMG 0.61x with one small burst, delta 3.19, theta/delta 0.82, sigma 2.66, next epochs theta/delta 1.3; unclear whether R has begun. |
| 6 | 19376 | W | medium | rule | EMG bursts cover about 3 of the 4 s (1.66x cut) and continue into the next epoch (1.8x); a 8-s arousal, not a microarousal, even though delta 3.38 stays highish. |
| 7 | 20087 | W | low | hmm | EMG tone about 1.0x cut with continuous activity, not atonic, in a run of 0.6-0.9x epochs; theta/delta high in neighbours looks like active-wake theta, and R requires atonia. |
| 8 | 20272 | W | medium | hmm | Continuous EMG activity at 0.85x, tone 0.89x, neighbours 0.7-2.0x with a big burst just after; EEG has no slow waves or spindles (delta 3.07, theta/delta 0.98): quiet wake. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL39_R_epochs.png`.


---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSL33: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbssl]
---

# HLBSSL33: S-SL (SOD1, ad libitum), rig B1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** yes.
> - Old pipeline: baseline SCOREABLE, recovery SCOREABLE.

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
| EMG separability η (gap; ≥ 0.70) | 0.887 | 0.861 |
| η, SleepStager 20–90 Hz EMG | 0.855 | 0.847 |
| δ AUC, NR vs W (≥ 0.75) | 0.947 | 0.927 |
| EEG median log10 δ (2–4) | 3.26 | 3.24 |
| EEG-alone state changes / h (≥ 5) | 31.9 | 39.0 |
| κ rule vs HMM | 0.91 | 0.92 |
| κ NREM, rule vs EEG alone | 0.88 | 0.85 |
| κ rule, gap vs 20–90 Hz EMG | 0.98 | 0.97 |
| artifact epochs % | 0.2 | 0.1 |
| EEG 60 Hz, median µV | 70 | 9 |
| EMG 60 Hz, median µV | 20 | 5 |
| wake % light (rule) | 26.8 | 27.7 |
| wake % dark (rule) | 69.9 | 63.5 |
| NREM % light, EEG alone | 56.8 | 57.1 |
| NREM % dark, EEG alone | 25.3 | 28.3 |
| sleep % light, EMG alone | 72.2 | 71.4 |
| sleep % dark, EMG alone | 30.0 | 36.1 |
| r@1min (project definition) | 0.747 | 0.702 |
| old verdict reason | 23.96 h in 12 block(s), r@1min 0.550 | 23.99 h in 5 block(s), r@1min 0.718 |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssl33-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 27 % light vs 70 % dark, long consolidated dark wake bouts with EMG plateaus, NR/R cycling in light. Rule and HMM agree (kappa 0.91).
Concerns: Nothing technical. Sleep floor is very low and steady with regular heartbeat-like spikes that the spike-proof tone handles. Several contested epochs are REM-end transitions where a burst starts at the epoch edge; the rule handled these sensibly. The old pipeline was SCOREABLE too, so no disagreement in verdict.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 6214 | R | medium | rule | After a clear REM bout (theta/delta 3.3, 5.1) the EMG burst starts only in the last third of the epoch (<half), delta still low 2.83, theta/delta 1.19; W starts in the next epoch. |
| 2 | 7414 | NR | low | rule | Post-wake transition: EMG burst only in the first ~0.5 s, then a low-level floor (tone 0.42x), delta 3.33 with slow waves, next epochs are NR. |
| 3 | 7673 | R | medium | rule | Atonic EMG with only heartbeat spikes, regular theta in a bout of several epochs with theta/delta 1-1.5 and delta well below NR median; HMM agrees. |
| 4 | 7738 | R | low | hmm | Theta/delta near 1 for 3-4 epochs, EMG flat at 0.30x cut, but delta 3.3 is not far below NR median so the bout is short and borderline. |
| 5 | 8913 | R | medium | hmm | Short EMG twitch (<1.5 s) inside an ongoing REM bout (neighbours R, theta/delta 0.8-1.2, delta low, tone 0.30x); a twitch does not end REM. |
| 6 | 9024 | R | high | rule | Epoch is atonic with theta/delta 2.2 and delta 2.91; the EMG burst begins only at the very end (3.8 s), so W starts next epoch. |
| 7 | 16227 | W | low | hmm | EMG active across the whole epoch (1.02x cut, continuous after a large burst in the previous epoch); delta 3.44 looks NREM-like, so a muscle-only arousal could be argued, but muscle is active more than half the epoch. |
| 8 | 16264 | W | medium | rule | About 1 s burst plus continuing activity, 1.47x cut, EMG baseline already raised, next epoch 2.4x cut; delta 3.31 and no spindles. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL33_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbssl33-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake 27.7 % light vs 63.5 % dark, long NREM blocks early, kappa rule-HMM 0.92, old verdict SCOREABLE agrees with tier A. Starts at ZT0 with a short wake bout.
Concerns: A few thin vertical stripes in the spectrogram (single-minute transients, probably movement or cable) do not matter. One thing to check: around ZT18 (03:14) there are several epochs of continuous uniform EMG fuzz just above the cut (1.15-1.27x, not bursty) together with large slow waves; the rule calls them wake and the HMM calls them NREM, so some dark-phase sleep may be scored as wake. This is a small block, not a reason to change the tier.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 152 | NR | medium | hmm | Only one short EMG burst (about 1 s of the 4 s, under half) inside large high-amplitude slow waves, delta 3.89 above NR median, theta/delta 0.16, tone 0.58x once spikes are removed: microarousal in NREM. |
| 2 | 2963 | R | medium | hmm | EMG very flat 0.19x, theta/delta 1.59 rising from 1.04 into 1.53 and 1.90, delta 3.17 and sigma 2.55 falling; regular theta-looking EEG. |
| 3 | 3135 | NR | medium | rule | Big slow waves, delta 3.60 above NR median, theta/delta 0.43, sigma 2.67; EMG tone raised at 0.7x after the wake bout but no bursts, one-sided so it stays NR. |
| 4 | 7933 | R | medium | hmm | EMG flat 0.18x, theta/delta 1.42, delta 3.32 and sigma 2.32 low, same as the two preceding R-labelled-by-HMM epochs; ends with a clear wake burst. |
| 5 | 12746 | uncertain | low | neither | EEG looks R-like (delta 2.97, theta/delta 1.82) with EMG 0.38x, but a wake burst ended about 2 s earlier and the next epochs return to delta 3.25-3.42 with theta/delta 0.5; could be a brief R or a post-arousal light NR. |
| 6 | 14495 | R | low | hmm | EMG 0.40x with small twitches (typical of REM), theta/delta 1.04 after 1.45, delta 3.10 low, sigma 2.64; short bout, theta not very regular. |
| 7 | 16422 | uncertain | low | neither | EMG is a uniform fuzz at 1.15x cut, no bursts, over many epochs, while the EEG shows large slow waves (delta 3.73, theta/delta 0.29, sigma 2.93); rule 1 says W by muscle but a tonic EMG plateau with clear NREM EEG may be technical or posture-related. |
| 8 | 18000 | NR | high | rule | Delta 3.55 at NR median, sigma 2.93, EMG 0.58x without bursts, slow-wave EEG; rule and HMM agree. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL33_R_epochs.png`.


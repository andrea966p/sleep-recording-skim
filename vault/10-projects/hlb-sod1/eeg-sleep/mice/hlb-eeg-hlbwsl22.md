---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSL22: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbwsl]
---

# HLBWSL22: W-SL (water, ad libitum), rig A2

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
| EMG separability η (gap; ≥ 0.70) | 0.835 | 0.830 |
| η, SleepStager 20–90 Hz EMG | 0.684 | 0.699 |
| δ AUC, NR vs W (≥ 0.75) | 0.959 | 0.953 |
| EEG median log10 δ (2–4) | 3.02 | 3.02 |
| EEG-alone state changes / h (≥ 5) | 32.5 | 26.7 |
| κ rule vs HMM | 0.78 | 0.86 |
| κ NREM, rule vs EEG alone | 0.88 | 0.88 |
| κ rule, gap vs 20–90 Hz EMG | 0.92 | 0.95 |
| artifact epochs % | 0.0 | 0.0 |
| EEG 60 Hz, median µV | 59 | 12 |
| EMG 60 Hz, median µV | 26 | 102 |
| wake % light (rule) | 25.7 | 26.3 |
| wake % dark (rule) | 61.8 | 64.0 |
| NREM % light, EEG alone | 58.3 | 57.5 |
| NREM % dark, EEG alone | 31.0 | 28.9 |
| sleep % light, EMG alone | 74.3 | 73.3 |
| sleep % dark, EMG alone | 38.7 | 36.7 |
| r@1min (project definition) | 0.789 | 0.785 |
| old verdict reason | 24.00 h in 1 block(s), r@1min 0.384 | rung 2 CONNECTION: chip floor is 689 uV of 60 Hz (grounded chips show >800) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsl22-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Clear delta bands in the light, long wake blocks in the dark (26% vs 62% wake), sleep floor EMG about 8-12 uV and bursty wake; all 24 hours kept and they look good. Rule follows the EEG; HMM paints more R in the dark (kappa 0.78), which the EEG does not support.
Concerns: The HMM over-calls R in dark NREM stretches with theta/delta around 0.5-1.5; here the rule is closer to the EEG. Several contested epochs sit next to wake bursts where NR vs brief arousal is a judgment call. Old verdict SCOREABLE agrees.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1160 | uncertain | low | neither | EMG burst begins about 2.5 s into the epoch (under half) and leads into a long wake bout; delta 2.91 well below NR median, theta/delta 0.46, sigma low; arousal onset, NR vs W undecided, R excluded by the burst. |
| 2 | 5632 | uncertain | low | neither | EMG continuously active at about 0.8x cut with no atonia (HMM R impossible), between W epochs, delta 3.04, theta/delta 0.53; quiet wake vs light NR. |
| 3 | 8456 | W | medium | rule | EMG burst covers about half the epoch, epoch mean 3.5x cut, delta 3.06 reduced; consistent with the previous W epoch (rule and HMM both W). |
| 4 | 8997 | NR | low | rule | Atonic but sigma is the highest in this series (2.90, spindle-like), delta 3.04, theta/delta 1.74 is borderline; sigma up argues NR over R. |
| 5 | 9426 | R | medium | hmm | Atonic EMG 0.44x, regular 7 Hz theta in the trace, theta/delta 2.97, delta 2.73 far below NR median 3.38, sigma dropped. |
| 6 | 10242 | NR | low | rule | Follows an EMG burst that ends at the epoch start; theta/delta 0.47, delta 3.07, no theta dominance, low-amplitude EEG; post-arousal NR. |
| 7 | 14874 | NR | medium | rule | Short EMG burst only in the last 1.5 s (under half) inside NREM, theta/delta 0.23, slow waves with delta high in neighbours; microarousal, not REM. |
| 8 | 18742 | R | high | rule | Atonic EMG 0.38x, regular theta, theta/delta 1.63 rising to 4.5 in the next epochs, delta 2.91, sigma 2.33 dropped (rule and HMM both R). |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL22_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsl22-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Convincing: 24 h all usable, delta bands alternate sharply with wake in the spectrogram, and theta/delta rises in REM. EMG has a low steady sleep floor of about 5 to 10 uV and bursty high wake. Wake is 26 % in the light and 64 % in the dark, as expected. The rule's NREM matches the EEG-only HMM (kappa 0.88) and the rule-HMM kappa is 0.86. Sleep in the early light hours is consolidated in long NR blocks.
Concerns: The old verdict (NO VERDICT, chip floor 689 uV) was about a ground check, not about the signal, so this mouse was not wrongly rejected on the data. Tier is A under the gap EMG but C under the ss60 EMG (eta 0.699, just under 0.70), so the tier depends on the EMG method. Choose the gap EMG, since the traces show a clean EMG floor and heartbeat spikes without mains. Raw EMG 60 Hz is 101 uV before filtering. The contested epochs are mostly NR where the HMM wrongly says R or W; the rule is mostly right.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 5768 | NR | high | rule | EMG is flat apart from heartbeat spikes (a burst ends about 1 s before the epoch). Slow waves are present, delta 3.18 is near the NR median 3.40, and sigma is high. Both labels are NR. |
| 2 | 6856 | NR | low | rule | EMG bursts are scattered and below the cut (0.87x), covering less than half the epoch. Delta 3.14 is near NR level and slow waves persist, so this is a microarousal inside NREM, though it is close to wake. |
| 3 | 7478 | NR | high | rule | EMG is quiet at 0.34x with heartbeat only, slow waves are large with spindles, delta 3.14 is near the NR median, and theta/delta is low. |
| 4 | 9003 | NR | medium | rule | EMG is flat at 0.55x. Delta 3.14 is near the NR median, and the EEG is a mix of slow waves and spindles, not regular 6 to 9 Hz theta, so the HMM's R is unsupported. |
| 5 | 9472 | NR | medium | rule | A single brief EMG burst (about 0.4 s) inside an otherwise flat EMG. Slow waves are present and delta 3.04 is near the NR level. Neighbouring epochs are NR. |
| 6 | 9614 | NR | high | rule | EMG is flat at 0.37x, delta 3.39 is at NR level, and large slow waves are visible. Theta is not regular. |
| 7 | 9991 | W | low | hmm | EMG is just under the cut (0.90x) with bursts across several seconds and wake neighbours (1.18x before, 1.76x after). Delta 2.97 is below the NR median and the EEG is low-amplitude. This looks like waking up, though it is borderline. |
| 8 | 14808 | NR | medium | rule | EMG is quiet at 0.55x with heartbeat spikes. Theta/delta 1.93 is high, but sigma stays high (2.74) and the epoch follows NR epochs with delta 3.2, so it is more likely light NR than REM. A wake bout ended earlier. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL22_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The tier depends on the EMG method: the ss60 EMG gives eta 0.699, just under 0.70, and tier C. But gap is the pre-specified primary, and the wake/sleep calls barely move between methods (kappa gap vs ss60 0.948). Raw EMG mains is 101 uV, but the gap band has the comb at chance (0.14) and a 5 to 14 uV floor. The old NO VERDICT was a chip-floor ground check, not a judgement of this signal. Checked: Brief; previous reviewer's epoch calls; score.json; blocks_1h.csv (24/24 hours, AUC 0.92 to 0.97). From the parquets: EMG NR 11.6 / W 69 uV; NR-W delta gap 0.56; 2.7 % of NR epochs below the W delta median; 88 % of rule NR also NR by EEG-only; 1-min rho -0.62; EMG anti-correlated with the 60 Hz line (rho -0.55). Comb share at chance; EEG PSD has a normal 1/f shape. Wake light/dark 26.3 / 64.0 %.


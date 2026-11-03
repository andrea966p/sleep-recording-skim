---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSL29: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbwsl]
---

# HLBWSL29: W-SL (water, ad libitum), rig D2

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
| hours usable, EEG + EMG | 24 | 24 |
| … of them light | 12 | 12 |
| … of them dark | 12 | 12 |
| hours usable, EEG alone | 24 | 24 |
| hours usable, EMG alone | 24 | 24 |
| EMG separability η (gap; ≥ 0.70) | 0.836 | 0.844 |
| η, SleepStager 20–90 Hz EMG | 0.815 | 0.792 |
| δ AUC, NR vs W (≥ 0.75) | 0.955 | 0.947 |
| EEG median log10 δ (2–4) | 3.09 | 3.14 |
| EEG-alone state changes / h (≥ 5) | 37.0 | 36.5 |
| κ rule vs HMM | 0.89 | 0.90 |
| κ NREM, rule vs EEG alone | 0.88 | 0.87 |
| κ rule, gap vs 20–90 Hz EMG | 0.95 | 0.93 |
| artifact epochs % | 0.0 | 0.0 |
| EEG 60 Hz, median µV | 60 | 13 |
| EMG 60 Hz, median µV | 63 | 14 |
| wake % light (rule) | 34.0 | 33.5 |
| wake % dark (rule) | 67.6 | 64.1 |
| NREM % light, EEG alone | 55.5 | 55.0 |
| NREM % dark, EEG alone | 28.4 | 31.3 |
| sleep % light, EMG alone | 65.5 | 65.3 |
| sleep % dark, EMG alone | 32.4 | 35.5 |
| r@1min (project definition) | 0.771 | 0.777 |
| old verdict reason | rung 3 SCOREABILITY FAIL: 24.00 h in 1 block(s), r@1min 0.177 | rung 2 CONNECTION: chip floor is carrying signal: its slope threshold is -2.14 (valid floors are flatter than -1.90) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsl29-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible. Wake 34% light vs 68% dark, strong delta bands, EMG sleep floor very low and flat (about 4 uV) with clean bursts, all 24 hours kept; rule, HMM and EEG-only agree (kappa 0.885). Best-quality recording of those I reviewed.
Concerns: With a very low atonic floor, many NR/R boundary epochs are decided by theta/delta alone; the HMM calls more R in light-hour NREM (theta/delta 0.8-1.3) where the rule keeps NR, and several of these look like genuine ambiguity rather than a rule error. Old NOT SCOREABLE is clearly wrong for this animal.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 4167 | R | low | hmm | Atonic EMG 0.23x, theta/delta 1.33, sigma fell to 2.42 from 2.70, delta 3.10 below NR median; first R-like epoch of a short run, but a lone epoch (neighbours NR) so low confidence. |
| 2 | 5393 | R | medium | hmm | Atonic 0.25x, regular 6-7 Hz theta, theta/delta 2.22, delta 3.05 low, sigma 2.41. |
| 3 | 6055 | uncertain | low | neither | Atonic EMG 0.32x but theta/delta only 0.83, delta 3.09, sigma 2.61 not dropped; ambiguous NR/R, neighbours the same. |
| 4 | 6080 | R | low | hmm | Inside a REM bout (previous epoch R, theta/delta 2.08), EMG atonic 0.23x, theta/delta 1.07, delta 3.16 and sigma 2.65 returning slightly; fading theta alone does not end REM, so the NR* island is not supported. |
| 5 | 8161 | NR | low | rule | Sigma 2.72 high, delta 3.34 near NR median, theta/delta 1.05; REM begins in the next epochs (theta/delta 3.6). |
| 6 | 8539 | W | low | hmm | EMG elevated 0.72x cut for several epochs versus a 0.25x sleep floor and then clear W; delta 3.05 low, sigma 2.39, no spindles; quiet wake preceding a wake bout. |
| 7 | 16721 | W | medium | rule | Continuous bursts through the epoch (0.96x cut) in the middle of a dark-phase wake bout, delta 2.84 low, theta/delta 1.00 (wake theta), no atonia. |
| 8 | 19355 | W | high | rule | Bursts across most of the epoch, mean 1.45x cut, delta 2.95 low (rule and HMM both W). |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL29_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The old pipeline rejected this window at rung 3 (r@1min 0.177), not at the connection rung. So it must be explained, not just overridden. The likely cause is that the old 10-124 Hz EMG band includes the 60 Hz line (63 uV raw), which swamps a 4 to 6 uV sleep floor and flattens the EMG's relation to the EEG. Two dark hours (ZT15 to 17) are about 99 % wake, and the hour tests exempt all-wake hours, so they count as usable without being tested. Neither point undermines the staging. Checked: Brief; overview and epochs PNGs (clean delta bands that alternate with a low EMG floor; contested epochs are arousals and NR/R borders); score.json; blocks_1h.csv (24/24 hours, AUC 0.85 to 0.97). From the parquets: EMG NR 5.75 / W 53 uV (9x); NR-W delta gap 0.55; only 1.9 % of NR epochs below the W delta median; 91.6 % of rule NR is also NR by EEG-only; 1-min rho -0.67; hourly p10 3.6 to 7 uV in mixed hours. From psd_emg.npy: comb share at chance (0.15). Wake light/dark 34.0 / 67.6 %; r@1min is now 0.771 vs a shuffled 0.006.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsl29-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very convincing: all 24 h usable, the strongest delta bands (up to about 3.8) alternating with wake, a clean low EMG floor of about 4 to 8 uV, wake 33.5 % in the light and 64 % in the dark, and a rebound at ZT19 to ZT22. AUC delta NR vs W is 0.95 and the EEG-only HMM agrees with the rule (kappa 0.87). The best recording of the batch.
Concerns: The old verdict (NO VERDICT, floor slope -2.14) was about a chip-floor property, not about the signal, so this mouse was not wrongly rejected on the data; it is a good rescue. The contested epochs are the usual mix of arousals and post-wake epochs. The last tonic-EMG epoch near ZT22 with very high delta is ambiguous.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 7267 | NR | high | rule | EMG is flat at 0.31x, the EEG has large slow waves and spindles (sigma 2.88), and delta 3.14 is a bit below the NR median. The HMM's R is not supported by any regular theta. |
| 2 | 7440 | uncertain | low | neither | EMG is atonic and flat (0.22x), delta 2.95 is below the NR median, and the EEG shows a moderate regular rhythm, but sigma is 2.53 and theta/delta 1.2 is not high. An arousal follows 2 s after the epoch. It could be REM or late NR. |
| 3 | 9561 | NR | medium | rule | EMG is flat (0.24x). The EEG has large amplitude with spindle-like bursts, sigma 2.71, delta 3.07, and theta/delta 1.22 is modest. It looks NR, with REM probably starting in the next epochs. |
| 4 | 10612 | W | medium | hmm | EMG bursts cover about 0 to 2.5 s (a strong burst, then smaller ones), which is more than half of the epoch, and the previous epoch is also active. Delta 3.07 is not decisive during movement. |
| 5 | 14631 | uncertain | low | neither | A wake bout ended about 4 s before the epoch and EMG is now flat (0.29x). Delta 2.84, sigma 2.61 and theta/delta 1.29 give mixed signs of light NR and early REM. |
| 6 | 15241 | NR | high | rule | EMG is flat at 0.27x, the EEG has large slow waves and spindles, delta 3.35 is near the NR median, and sigma is high at 3.02. Wake bursts begin only in the next epoch. |
| 7 | 18358 | W | medium | rule | EMG is raised and not at the sleep floor (0.73x the cut) with a burst at about 3.1 s, and large wake bursts just before. Delta 2.88 is below the NR median. It looks like quiet wake. |
| 8 | 19985 | uncertain | low | neither | EMG is tonic and continuous at about 1.0x the cut with no bursts, while the EEG has large slow waves and delta 3.73 is above the NR median. Muscle suggests wake and the EEG suggests NREM, so the traces do not decide it. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL29_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: I found nothing substantive. Hour 23 and the near all-wake hours (ZT13, 17 and 18) pass the hour tests partly through the all-wake exemption rather than by being tested. Contested epochs near ZT22, with tonic EMG at 1.0x the cut and high delta, are ambiguous. The old NO VERDICT came from a chip-floor slope criterion (-2.14), not from this signal. Checked: Brief; previous reviewer's notes; score.json; blocks_1h.csv (24/24 hours, AUC 0.82 to 0.98). From the parquets: EMG NR 5.1 / W 53 uV (10x); NR-W delta gap 0.54; 2.0 % of NR epochs below the W delta median; 91 % agreement with EEG-only NR; 1-min rho -0.68; EMG mains only 14.5 uV; comb share at chance (0.13); EEG PSD normal. Wake light/dark 33.5 / 64.1 %.


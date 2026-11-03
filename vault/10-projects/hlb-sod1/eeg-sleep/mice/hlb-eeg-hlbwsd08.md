---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSD08: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbwsd]
---

# HLBWSD08: W-SD (water, sleep deprivation), rig D2

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
| hours usable, EEG + EMG | 24 | 20 |
| … of them light | 12 | 8 |
| … of them dark | 12 | 12 |
| hours usable, EEG alone | 24 | 20 |
| hours usable, EMG alone | 24 | 20 |
| EMG separability η (gap; ≥ 0.70) | 0.863 | 0.861 |
| η, SleepStager 20–90 Hz EMG | 0.820 | 0.857 |
| δ AUC, NR vs W (≥ 0.75) | 0.940 | 0.938 |
| EEG median log10 δ (2–4) | 3.18 | 3.19 |
| EEG-alone state changes / h (≥ 5) | 31.0 | 40.6 |
| κ rule vs HMM | 0.76 | 0.72 |
| κ NREM, rule vs EEG alone | 0.87 | 0.86 |
| κ rule, gap vs 20–90 Hz EMG | 0.95 | 0.95 |
| artifact epochs % | 0.1 | 0.1 |
| EEG 60 Hz, median µV | 28 | 154 |
| EMG 60 Hz, median µV | 12 | 18 |
| wake % light (rule) | 36.3 | 25.6 |
| wake % dark (rule) | 73.9 | 61.9 |
| NREM % light, EEG alone | 49.4 | 60.1 |
| NREM % dark, EEG alone | 23.6 | 31.1 |
| sleep % light, EMG alone | 63.4 | 73.9 |
| sleep % dark, EMG alone | 26.2 | 38.2 |
| r@1min (project definition) | 0.535 | 0.512 |
| old verdict reason | 23.98 h in 18 block(s), r@1min 0.487 | 17.91 h in 48 block(s), r@1min 0.402 |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsd08-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible: bright delta bands alternating with wake, theta/delta rises with REM, wake 36% in light vs 74% in dark, clean EMG floor and bursty wake, all 24 h usable (eta 0.86, AUC 0.94).
Concerns: No hours wrongly kept or dropped. HMM (kappa 0.76 with the rule) paints R over many NREM epochs that have slow waves and low-level EMG; the rule is the better scorer there. Contested epochs are mostly REM boundaries. Old verdict SCOREABLE stands.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1629 | R | medium | rule | Inside an R bout (neighbouring epochs strong theta/delta 3.0), delta low 2.84, phasic twitch-like EMG below the cut (0.8x, tone 0.76x), theta/delta 1.91; wake begins in the next epoch. |
| 2 | 3900 | uncertain | low | neither | Between an R stretch and wake: tone 0.48x cut, delta 3.22 still below NR median (3.56), theta/delta 0.58; the EEG shows neither clear regular theta nor full slow waves. |
| 3 | 7540 | R | low | hmm | Atonic with heartbeat spikes, delta 2.91 low, theta/delta 0.55, sits between R epochs (theta/delta 1.5); a lone NR island has no clear reason, but theta is weaker here. |
| 4 | 9815 | NR | medium | rule | Flat atonic EMG but large slow waves with spindle-like bursts, delta 3.56 equal to the NR median; HMM R is not supported. |
| 5 | 10043 | W | medium | rule | EMG bursts through most of the epoch with tone 0.97x (just under cut) between epochs at 1.2-1.9x; quiet wake inside a wake bout, delta low 3.18. |
| 6 | 15224 | NR | high | rule | High-amplitude slow waves, delta 3.49 near NR median, EMG 0.6x with no large burst; HMM R wrong. |
| 7 | 17113 | NR | medium | rule | Slow waves with delta 3.74 above median, EMG only low continuous activity (0.8x cut, no big burst); wake starts in the next epoch, but this one stays NREM. |
| 8 | 17885 | NR | medium | rule | Single ~1 s EMG burst (<quarter of the epoch), tone 0.64x cut, slow waves and spindles visible: microarousal in NREM. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD08_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsd08-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible for a 20 h SD recovery from ZT4: wake ~26% in the light and ~62% in the dark, sleep concentrated early, clear delta bands alternating with wake, theta bouts at NR to R transitions. Rule vs EEG-only NREM kappa 0.86, AUC delta 0.94, all 20 h pass both screens.
Concerns: Best recording in the batch and the only one I would use for NR/R. Minor: EMG tone in some NR epochs sits around 0.5-0.6x cut (light NR or low-level activity), and a few wake-like runs with tone just under the cut are labelled NR* by the rule (see panel 3). The old pipeline also called this mouse scoreable, so no rescue is involved. Rule and HMM disagree mainly on R vs NR where the HMM over-calls R on low delta.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 4082 | NR | medium | rule | One EMG burst of about 1.5 s (under half the epoch) inside NREM with slow waves around it, delta 3.26 near NR median, theta/delta 0.56: microarousal, stays NR; HMM R is wrong. |
| 2 | 5307 | NR | high | rule | Large slow waves, EMG quiet at 0.45x cut, delta near NR median, sigma 2.84, theta/delta 0.48; rule and HMM agree. |
| 3 | 10654 | W | medium | neither | Repeated EMG bursts across the whole epoch (tone 0.96x cut, just under), flanked by W epochs at 1.17x, delta 3.07 low and sigma 2.48 low: quiet wake inside a wake bout; HMM R impossible without atonia. |
| 4 | 11121 | NR | medium | rule | EMG moderately raised but steady at 0.53x cut with no bursts, delta near NR level (3.22), sigma 2.97 high (spindle range); no atonia and no regular theta, so not R. |
| 5 | 13562 | W | medium | rule | Trains of EMG bursts through most of the epoch, flanked by clear wake (1.35x, 1.61x, 2.45x cut), low-amplitude EEG with no spindles; rule and HMM agree. |
| 6 | 14050 | NR | low | rule | EMG burst from about 1.6 s to the end of the epoch (about half, peak 3.4x cut) but tone 0.88x and EEG still NR-like (delta 3.39, slow waves); borderline microarousal; HMM R wrong. |
| 7 | 14335 | R | low | hmm | Flat EMG at 0.26x cut with only heartbeat ticks, regular theta-like oscillation, theta/delta 1.26 and delta 3.20 identical to the next two rule-R epochs; likely the first R epoch. |
| 8 | 16442 | NR | medium | rule | Slow waves visible, delta 3.32 near NR median, sigma 3.17 high, no atonia (EMG 0.59x steady); HMM R is not supported. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD08_R_epochs.png`.


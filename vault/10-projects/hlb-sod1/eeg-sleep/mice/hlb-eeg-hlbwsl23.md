---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSL23: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbwsl]
---

# HLBWSL23: W-SL (water, ad libitum), rig B1

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
| hours usable, EEG + EMG | 22 | 23 |
| … of them light | 10 | 11 |
| … of them dark | 12 | 12 |
| hours usable, EEG alone | 22 | 23 |
| hours usable, EMG alone | 24 | 24 |
| EMG separability η (gap; ≥ 0.70) | 0.828 | 0.822 |
| η, SleepStager 20–90 Hz EMG | 0.776 | 0.792 |
| δ AUC, NR vs W (≥ 0.75) | 0.825 | 0.860 |
| EEG median log10 δ (2–4) | 3.25 | 3.24 |
| EEG-alone state changes / h (≥ 5) | 51.7 | 39.8 |
| κ rule vs HMM | 0.90 | 0.92 |
| κ NREM, rule vs EEG alone | 0.76 | 0.82 |
| κ rule, gap vs 20–90 Hz EMG | 0.93 | 0.95 |
| artifact epochs % | 0.1 | 0.0 |
| EEG 60 Hz, median µV | 82 | 14 |
| EMG 60 Hz, median µV | 30 | 4 |
| wake % light (rule) | 30.3 | 24.0 |
| wake % dark (rule) | 65.6 | 60.5 |
| NREM % light, EEG alone | 53.9 | 57.4 |
| NREM % dark, EEG alone | 34.4 | 34.7 |
| sleep % light, EMG alone | 69.4 | 73.0 |
| sleep % dark, EMG alone | 34.1 | 38.8 |
| r@1min (project definition) | 0.641 | 0.629 |
| old verdict reason | rung 3 SCOREABILITY FAIL: 23.99 h in 3 block(s), r@1min 0.289 | 24.00 h in 1 block(s), r@1min 0.636 |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsl23-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake 33% in light vs 66% in dark; sleep floor EMG low and bursty wake; delta amplitude a bit smaller than in the other mice but the delta/theta alternation is clear, and 21 of 24 hours kept (9 light, 12 dark, above tier A).
Concerns: Hours about ZT3-6 and ZT8-9 were dropped. Epochs from hour 3-4 show an EMG floor lifted to about the cut (1.0x) with no bursts while the EEG has clear large slow waves, so that is a technical EMG floor rise, not wake; the rule hypnogram in those hours (mostly NR) matches the EEG, so the drop is conservative rather than wrong. EEG 60 Hz is a little higher (81 uV) than in the other mice. The old NOT SCOREABLE looks wrong for this animal.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2159 | uncertain | low | neither | EMG burst about 0.8-2.5 s (under half) then fading, epoch mean 1.34x cut, but delta 3.09 and sigma 2.55 are still NREM-ish inside NR neighbours; microarousal vs short wake. |
| 2 | 3333 | NR | medium | rule | Large slow waves, delta 3.65 above NR median, sigma 2.55; EMG is a lifted noisy floor (about 1.0x) without bursts, so tone is technical (rule and HMM both NR). |
| 3 | 3421 | W | low | rule | Movement burst covers roughly the last 2.5 s right after a REM bout, EMG mean 1.22x cut; delta 3.26 is partly movement artefact; HMM NR ignores the muscle. |
| 4 | 3477 | NR | high | rule | Two very short twitches (under 0.3 s) on a lifted EMG floor, delta 3.60, sigma 2.78, big slow waves (rule and HMM both NR). |
| 5 | 5934 | R | medium | hmm | Atonic EMG 0.30x, theta/delta 1.70, delta 2.92 low, sigma 2.36 dropped, inside a REM-like run (theta/delta 2.39 and 1.43 before); rule NR looks like a miss. |
| 6 | 10433 | uncertain | low | neither | Several short EMG bursts across the epoch (0.96x cut), delta dropped to 3.13 from 3.7, followed by two clear W epochs; transition into wake, NR vs W not decidable. |
| 7 | 13654 | W | low | hmm | Steady muscle tone 0.86-0.88x cut with no atonia, delta 2.87 at wake level, directly after wake bouts; quiet wake (sigma 2.80 slightly high). |
| 8 | 16816 | NR | medium | rule | Delta 3.37 close to NR median 3.44 and sigma 2.88 high (spindles), theta/delta only 1.29; EMG at sleep floor after a wake burst, post-arousal NREM rather than REM. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL23_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: Light-phase EEG separation is modest: AUC 0.79 and NR minus W delta only 0.25 log. Three light hours (ZT4, 5, 8) fail the AUC bar (0.65-0.73), and 15 % of rule NR has wake-level delta and sigma. For stretches, the NREM EMG floor rises to the cut. In the panels for epochs 3333 and 3477 (ZT3.7-3.9), runs at 0.9-1.08x the cut are scored NR only through tone-island marks. So light-phase W/NR there depends on the smoothing passes. The old r@1min 0.289 sat just under its 0.30 bar. Checked: I read the overview, the epochs image, score.json and blocks_1h.csv, recomputed per-hour stats and AUC by phase, and split rule-only from EEG-agreed NR. It still holds: 21 of 24 h are usable (9 L / 12 D), which also satisfies tier B. Dark AUC is 0.86; rule vs EEG-only kappa 0.76, rule-HMM 0.90, and the two EMG pipelines agree at kappa 0.93. Wake is 32.7 % light vs 65.6 % dark. EEG 60 Hz is about 80 uV but stable. Median bouts are NR 12 and R 8 epochs.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsl23-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 24 % in the light and 60.5 % in the dark. Delta and EMG alternate cleanly, with large delta bands in the light and a long wake stretch from ZT12. A strong sleep rebound is visible around ZT18 to ZT19.5, where delta is high, then wake returns. EMG line60 is only 3.6 uV, so the EMG is the cleanest of the batch. Old verdict SCOREABLE agrees with the new tier.
Concerns: Hour 11 (ZT11 to ZT12) was dropped although the traces look like ordinary sleep with a clean EMG floor. This is probably the EEG-agreement test failing because the hour has little wake, and it is low impact (1 h). Between about ZT2.5 and ZT4.7 the rule calls W where the EMG sits steadily just above the cut (1.0 to 1.4x) with no bursts, while the EEG has large slow waves with delta above the NR median. That could be a sustained raised EMG floor during NREM, so some W could be overcalled in the light. Rule vs HMM kappa is 0.915.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2565 | uncertain | low | neither | EMG is tonic at 1.07x the cut with no bursts, while the EEG has large slow waves with delta 3.63 above the NR median. EMG says wake only barely and the EEG says NREM clearly, so the traces do not decide. |
| 2 | 4200 | uncertain | low | neither | The same ambiguity: continuous EMG at 1.01x the cut (a burst 7 s earlier), with moderate slow waves, delta 3.25 and theta/delta 0.81. |
| 3 | 7788 | R | medium | rule | EMG is completely flat (0.15x, the lowest in this recording), the EEG is a regular theta-like rhythm, theta/delta 1.37, and delta is below the NR median. It follows NR epochs and is followed by more R. |
| 4 | 9271 | NR | medium | rule | EMG tone is falling from the previous wake (0.96x) to 0.72x, so it is not atonic. The EEG has spindles and delta 3.20 is near the median, with theta/delta 0.56. It looks like NR just after an arousal. |
| 5 | 11184 | NR | medium | rule | EMG is flat until a burst at about 3.6 s, so only about 0.4 s lies inside the epoch. Delta 3.16 and the slow waves are NR-like. The wake begins in the next epoch, so this is a microarousal onset. |
| 6 | 11223 | NR | low | rule | EMG is tonic at 0.66x (not atonic) with no burst, delta 2.80 is low, and slow waves are small. It is not REM since it is not atonic. NR vs quiet wake is hard, and the next epoch is a clear wake burst. |
| 7 | 18746 | uncertain | low | neither | EMG tone is decaying (0.32x) but is not as flat as true REM here (0.15x). Theta/delta 1.13 is weak, delta 2.90 is low, and sigma has not dropped. Whether this is REM onset or late NR cannot be decided. |
| 8 | 20395 | NR | medium | rule | EMG is quiet at 0.40x, delta 3.25 is at NR level, slow waves and spindles are visible, and theta is not regular. The wake burst comes only in the next epoch. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL23_R_epochs.png`.


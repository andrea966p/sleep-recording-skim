---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSD06: EEG re-score 2026-11, baseline tier D, recovery tier D"
tags: [eeg, hlb, mouse, hlbwsd]
---

# HLBWSD06: W-SD (water, sleep deprivation), rig C2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Recovery:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | D | D |
| hours usable, EEG + EMG | 7 | 3 |
| … of them light | 7 | 3 |
| … of them dark | 0 | 0 |
| hours usable, EEG alone | 7 | 3 |
| hours usable, EMG alone | 23 | 20 |
| EMG separability η (gap; ≥ 0.70) | 0.842 | 0.748 |
| η, SleepStager 20–90 Hz EMG | 0.933 | 0.894 |
| δ AUC, NR vs W (≥ 0.75) | 0.900 | 0.253 |
| EEG median log10 δ (2–4) | 3.19 | 3.31 |
| EEG-alone state changes / h (≥ 5) | 48.4 | 12.6 |
| κ rule vs HMM | 0.82 | 0.43 |
| κ NREM, rule vs EEG alone | 0.82 | -0.42 |
| κ rule, gap vs 20–90 Hz EMG | 0.96 | 0.86 |
| artifact epochs % | 60.2 | 36.3 |
| EEG 60 Hz, median µV | 2745 | 260 |
| EMG 60 Hz, median µV | 485 | 14 |
| wake % light (rule) | 13.3 | 1.8 |
| wake % dark (rule) | – | – |
| NREM % light, EEG alone | 72.2 | – |
| NREM % dark, EEG alone | – | – |
| sleep % light, EMG alone | 68.7 | 85.3 |
| sleep % dark, EMG alone | 36.2 | 58.5 |
| r@1min (project definition) | 0.048 | -0.060 |
| old verdict reason | rung 3 SCOREABILITY FAIL: 7.77 h in 55 block(s), r@1min -0.013 | rung 2 CONNECTION FAIL: 38.0% usable, longest unbroken block 11.2 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsd06-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG partial; rule follows the EEG: no; tier disputed → X.
Plausibility: Not plausible as scored. About 60% of the EEG is artefact (60 Hz 2745 uV, broadband rails, saturated spectrogram); delta and theta/delta swing with the noise rather than with state. EMG is two-level: clean sleep floor (3-8 uV, with heartbeat spikes) alternating with a flat ~500 uV plateau without bursts, which is technical loss of contact. Wake 13% in the light and the plateau dominating ZT12-24 would give an implausible dark-phase hypnogram.
Concerns: Pipeline tier D (ss60 gives X) overrates it: EMG-only wake in the dark is just the plateau. Only a few clean stretches (ZT0-2, ZT3-5, ZT8-9, ZT10-12) are credible. In the epoch figure the EEG row is a flat line (off-scale from railing), so I could not read the waveform in any contested epoch and scored from EMG and the numbers only, with low confidence. Old NOT SCOREABLE stands; propose X.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1200 | uncertain | low | neither | EEG waveform not visible (flat row); EMG burst only in the last ~1.3 s (<half) at the start of a wake bout, tone 0.30x cut but next epoch 1.2x; onset epoch not decidable. |
| 2 | 2888 | NR | low | rule | EMG 0.7x cut with one small burst at ~3 s (<half), tone 0.53x, delta 3.13 near NR median; no atonia for R. EEG row unreadable. |
| 3 | 7475 | R | low | hmm | Atonic EMG with heartbeat spikes (0.49x), delta 3.02 well below median (3.42), theta/delta 1.38 high; EEG row unreadable and the EEG in this hour is noisy. |
| 4 | 7564 | R | low | hmm | Inside an R stretch (R on both sides by rule), atonic, delta 2.73 low; the rule's NR island has no visible reason (EEG row unreadable). |
| 5 | 7861 | uncertain | low | neither | Atonic, but theta/delta 3.89 with sigma 3.62 in a lone epoch between NR epochs looks like noise as much as REM; EEG row unreadable. |
| 6 | 7907 | NR | low | rule | Atonic, delta 3.11 near NR level, theta/delta 0.49 low; the clear theta/delta rise (3.5) is in the next epoch, so this is the pre-REM epoch. EEG row unreadable. |
| 7 | 9024 | NR | low | rule | Atonic with heartbeat spikes, delta 3.07 slightly low, theta/delta 0.84 not elevated, neighbours NR; no evidence of R. EEG row unreadable. |
| 8 | 10001 | NR | medium | rule | One ~1 s EMG burst at the start (<quarter), tone 0.67x cut, delta 3.26 near median, theta/delta 0.19 low: microarousal in NREM. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD06_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsd06-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG partial; rule follows the EEG: no; tier agreed.
Plausibility: EMG-only sleep ~85% light and ~58% dark is plausible for an SD recovery. The rule's 0.7% wake is only the 2 kept hours. The EEG-derived R/NR split is not reliable.
Concerns: EEG has about 34% artefact epochs and ~260 uV of mains; hour 0 is broadband noise. Delta is higher in wake (movement artefact) than in NREM (per-hour AUC 0.03-0.74, mostly low), rule vs EEG-only NREM kappa -0.42, so the EEG cannot validate the rule. In the epochs drawn, EEG traces are too small to see waveforms and several R/NR decisions rest on theta/delta alone. EMG has a clean ~5 uV floor and real bursts, but the wake level sits as flat plateaus at ~500 uV with sharp edges (possibly clipped or tether noise), and eta is borderline (0.75). Only 2 light hours pass both screens; EMG-only W vs sleep is the defensible output (D).

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1012 | R | medium | rule | EMG atonic at 0.08x cut, theta/delta 1.93, delta 2.78 well below the NR median 3.42, inside an R run (rule and HMM agree); EEG waveform too small to confirm theta. |
| 2 | 1022 | uncertain | low | neither | Atonic with one <1 s twitch, but theta/delta 0.89 is below the values in R runs and delta 2.85 is low for NR; no clear spindles or theta visible. |
| 3 | 1251 | uncertain | low | neither | Atonic, theta/delta only 0.70 but sigma dropped to 2.21 just before an R run: possible early R onset or light NR, traces do not decide. |
| 4 | 1390 | NR | low | rule | Atonic, theta/delta 1.08 rising but still under the 1.5-2.0 of the following R epochs and sigma unchanged (2.38); last epoch of a transition before R. |
| 5 | 1585 | W | low | neither | Not atonic: continuous grainy EMG with bursts (0.53x cut, 1.09x in the next epoch), delta 2.94 below NR median, theta/delta 0.53; HMM R is impossible with this muscle activity, rule NR rests on a tone just under the cut. |
| 6 | 3204 | R | low | hmm | Flat EMG at 0.06x cut, theta/delta 1.83, sigma fell from 3.09 to 2.56 and the next epoch is R: likely the first R epoch. |
| 7 | 3249 | R | medium | rule | Atonic EMG, lowest delta here (2.47 vs NR median 3.42), theta/delta 2.59, sigma low, inside an R run (rule and HMM agree); earlier epochs show electrode pops but this one is clean. |
| 8 | 3468 | NR | medium | rule | Atonic, theta/delta 0.46 and stable at 0.3-0.75 over the whole window with no theta rise; HMM R follows the low delta only. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD06_R_epochs.png`.


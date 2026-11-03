---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSD01: EEG re-score 2026-11, baseline tier A, recovery tier D"
tags: [eeg, hlb, mouse, hlbwsd]
---

# HLBWSD01: W-SD (water, sleep deprivation), rig A1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | D |
| hours usable, EEG + EMG | 24 | 0 |
| … of them light | 12 | 0 |
| … of them dark | 12 | 0 |
| hours usable, EEG alone | 24 | 0 |
| hours usable, EMG alone | 24 | 20 |
| EMG separability η (gap; ≥ 0.70) | 0.883 | 0.858 |
| η, SleepStager 20–90 Hz EMG | 0.825 | 0.822 |
| δ AUC, NR vs W (≥ 0.75) | 0.953 | 0.338 |
| EEG median log10 δ (2–4) | 3.30 | 0.87 |
| EEG-alone state changes / h (≥ 5) | 32.1 | 23.8 |
| κ rule vs HMM | 0.66 | 0.58 |
| κ NREM, rule vs EEG alone | 0.89 | -0.21 |
| κ rule, gap vs 20–90 Hz EMG | 0.95 | 0.92 |
| artifact epochs % | 0.0 | 1.2 |
| EEG 60 Hz, median µV | 57 | 45 |
| EMG 60 Hz, median µV | 16 | 16 |
| wake % light (rule) | 30.7 | – |
| wake % dark (rule) | 71.5 | – |
| NREM % light, EEG alone | 55.5 | – |
| NREM % dark, EEG alone | 25.2 | – |
| sleep % light, EMG alone | 68.8 | 74.3 |
| sleep % dark, EMG alone | 28.9 | 39.7 |
| r@1min (project definition) | 0.756 | – |
| old verdict reason | 24.00 h in 2 block(s), r@1min 0.475 | rung 2 CONNECTION FAIL: 0.3% usable, longest unbroken block 0.3 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsd01-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible: bright delta bands alternating with wake all 24 h, wake 31% in light vs 72% in dark, EMG with a low steady sleep floor and bursty wake, all 24 h usable (eta 0.88, AUC 0.95).
Concerns: The HMM is the outlier here (kappa rule-HMM 0.66): in the dark it paints long runs of R where the EMG is clearly above the cut. EEG 60 Hz is 57 uV but sleep structure is unaffected. No hours wrongly kept or dropped. Old verdict SCOREABLE stands.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1626 | NR | high | rule | EMG 0.5x cut and flat, large slow waves with delta near NR median (3.47 vs 3.63); the burst falls in the next epoch. |
| 2 | 5945 | W | high | rule | EMG burst runs from ~0.7 s to the end of the epoch (>half), 3x cut, EEG goes low amplitude/fast, followed by more wake. |
| 3 | 6309 | W | high | rule | EMG fills the row (2.3x cut, tone 2.4x) with no atonia, so not REM despite theta/delta 1.07; HMM R is wrong. |
| 4 | 8973 | W | high | rule | Continuous strong EMG (3.9x cut, tone 3.3x) through the whole epoch, EEG desynchronised; no atonia for R. |
| 5 | 8988 | W | high | rule | EMG 4.9x cut with sustained bursts across the epoch; theta-ish EEG is waking theta, not REM. |
| 6 | 11800 | W | high | rule | EMG far above cut for nearly the whole epoch (3.5x, tone 2.4x), delta at wake level (2.98); HMM R rejected. |
| 7 | 13853 | W | high | rule | EMG active across the epoch (2.5x cut, tone 2.1x) with only brief pauses; no atonia, so wake not REM. |
| 8 | 20155 | NR | medium | rule | Only a ~0.5 s EMG burst at the very end (<half); tone 0.62x cut, delta 3.41 near NR median, slow waves present: microarousal in NREM. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD01_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsd01-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG good; rule follows the EEG: no; tier disputed → D.
Plausibility: EMG alone is plausible for a 20 h SD recovery starting ZT4: low floor (~6 uV) with real bursts, more sleep in the light (EMG sleep ~74%) than in the dark (~40%). The EEG-based NREM share is not trustworthy.
Concerns: Tier C (EEG only) is the wrong way round: the EMG is the usable channel, the EEG is not. log10 delta sits at ~0-1.5 (2-3 orders below the good mouse HLBWSD08), and per-hour AUC(delta NR vs W) is below 0.5 in all 20 h (0.08-0.44), so delta is higher when the muscle is active (movement and crosstalk), not in sleep. Rule vs EEG-only NREM kappa is -0.21. Bright broadband stripes coincide with EMG bursts. A constant ~20 Hz line is present. The EEG-only HMM 'passes' only because it splits on that artefact-driven power. Use W vs sleep from EMG; do not trust rule NR/R split or the HMM R. No contested epochs were drawn for this recording.

**Skeptic (tried to refute the rescue):** partially usable, tier D. Strongest objection: Tier C is backwards. The EEG carries no sleep signal: log10 delta is 0.5-1.3, about 2-2.5 orders below working EEG (3.0-3.6). Per-hour AUC of delta for NR vs W is 0.08-0.44 in all 20 hours. Delta correlates positively with EMG (r +0.17 to +0.67), so the 'EEG' picks up movement or crosstalk. There is also a constant 20 Hz line. Tier C only passed because eeg_alone_ok is unconditionally True. All 20 hours fail the both-channel screen. Checked: I read the overview, score.json and blocks_1h.csv, and recomputed per-hour delta, total power, AUC and delta-EMG correlation. Rule vs EEG-only NR kappa is -0.21. The EMG is credible on its own: floor 4-8 uV with real bursts to about 80-90 uV, eta 0.86. EMG-only sleep is 74 % light vs 40 % dark, and ZT4-7 is 65-96 % sleep, which fits SD recovery. Usable for W vs sleep from the EMG only; no NR/R split.


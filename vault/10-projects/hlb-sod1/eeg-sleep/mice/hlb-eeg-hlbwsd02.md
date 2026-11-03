---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSD02: EEG re-score 2026-11, baseline tier A, recovery tier D"
tags: [eeg, hlb, mouse, hlbwsd]
---

# HLBWSD02: W-SD (water, sleep deprivation), rig A2

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
| EMG separability η (gap; ≥ 0.70) | 0.880 | 0.877 |
| η, SleepStager 20–90 Hz EMG | 0.845 | 0.819 |
| δ AUC, NR vs W (≥ 0.75) | 0.943 | 0.262 |
| EEG median log10 δ (2–4) | 3.18 | 0.37 |
| EEG-alone state changes / h (≥ 5) | 35.2 | 32.7 |
| κ rule vs HMM | 0.94 | 0.56 |
| κ NREM, rule vs EEG alone | 0.88 | -0.35 |
| κ rule, gap vs 20–90 Hz EMG | 0.95 | 0.90 |
| artifact epochs % | 0.1 | 0.0 |
| EEG 60 Hz, median µV | 124 | 74 |
| EMG 60 Hz, median µV | 8 | 60 |
| wake % light (rule) | 27.1 | – |
| wake % dark (rule) | 74.4 | – |
| NREM % light, EEG alone | 58.7 | – |
| NREM % dark, EEG alone | 22.1 | – |
| sleep % light, EMG alone | 72.5 | 79.2 |
| sleep % dark, EMG alone | 25.6 | 41.6 |
| r@1min (project definition) | 0.651 | – |
| old verdict reason | 23.99 h in 5 block(s), r@1min 0.548 | rung 2 CONNECTION FAIL: 3.2% usable, longest unbroken block 1.2 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsd02-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible: clear delta/wake alternation, wake 27% light vs 74% dark, clean low EMG floor with bursty wake, all 24 h usable, rule and HMM nearly identical (kappa 0.94).
Concerns: EEG 60 Hz is high (124 uV) but delta bands and theta are still clean, so no hours lost. Contested epochs are mostly brief-burst and sleep-transition cases that a 4-s rule cannot settle. Old verdict SCOREABLE stands.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2402 | uncertain | low | neither | EMG burst occupies only the first ~1.3 s (<half) with decaying tone afterwards (tone 0.63x cut) and delta at NR median (3.51), but EEG is flat/low amplitude right after a real wake bout; arousal tail, not decidable. |
| 2 | 6066 | NR | medium | rule | One ~1.4 s EMG burst (<half), tone 0.77x cut, delta 3.05 reduced only briefly, slow waves return in the next epoch: microarousal inside NREM. |
| 3 | 7432 | R | low | hmm | EMG atonic and flat (0.24x), delta well below NR median (3.05 vs 3.50), theta/delta 1.74 vs 0.2-0.7 in neighbours; but a one-epoch R is unusual and the EEG row is only mildly regular. |
| 4 | 9559 | NR | medium | hmm | Atonic but delta at NR median (3.53) and theta/delta only 0.57; the clear theta/delta rise (2.1) starts in the next epoch. The rule's one-epoch-early REM onset looks one epoch too early here. |
| 5 | 13158 | NR | medium | rule | EMG bursts only ~1.5 s of the epoch, tone 0.71x cut (below cut), delta 3.37 close to NR median with slow waves; one-sided/short arousal stays NR. |
| 6 | 13198 | uncertain | low | neither | Atonic flat EMG (0.36x), delta 3.16 below median, theta/delta 0.99 intermediate, and R starts by rule in the next epoch; transition epoch, traces do not clearly show regular theta yet. |
| 7 | 15135 | uncertain | low | neither | Follows two wake epochs; low-amplitude bursting for ~2 s with a larger burst (tone 0.76x just under cut), delta 3.30 below NR median, EEG low amplitude: quiet wake versus microarousal cannot be separated. |
| 8 | 19821 | NR | medium | hmm | Slow-wave EEG with delta 3.61 above NR median, tone 0.44x cut; the only EMG burst is the last ~0.5 s (<half) and belongs to the following wake onset. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD02_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsd02-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG good; rule follows the EEG: no; tier disputed → D.
Plausibility: EMG-only picture is plausible: floor ~7 uV with bursts, sleep ~79% in the light vs ~42% in the dark, long wake bouts in the dark. Nothing from the EEG supports the NR/R split.
Concerns: Same problem as HLBWSD01. Tier C is wrong, D is right. log10 delta is -0.4 to 1.5 (tiny), per-hour AUC(delta NR vs W) 0.07-0.44, i.e. delta follows muscle activity, not sleep. Rule vs EEG-only NREM kappa -0.35 (anti-correlated); EEG-only calls NR in the bright broadband hour 0.3-1.5 and not in the quiet EMG-floor hours 1.7-3.5. The HMM R epochs in the dark are not credible without a usable EEG. Constant 20 Hz line. Keep EMG W/sleep only. No contested epochs drawn.

**Skeptic (tried to refute the rescue):** partially usable, tier D. Strongest objection: Same failure as HLBWSD01: tier C is wrong. Log10 delta is 0.1-0.9, about 2.5-3 orders below working EEG. Per-hour delta AUC for NR vs W is 0.07-0.44, and delta correlates positively with EMG (r +0.18 to +0.71). EEG-only NREM shows no light-dark contrast (43 % vs 38 %, a 5-point difference), and rule vs EEG-only kappa is -0.35. The C tier came from the always-True eeg_alone_ok, not from the EEG. Checked: I read score.json and blocks_1h.csv and recomputed per-hour EEG power, AUC, delta-EMG correlation and EMG percentiles. EMG raw 60 Hz is about 60 uV, but the gap EMG floor is 6-7 uV with real bursts to about 70-75 uV, and eta is 0.88. EMG-only sleep is 79 % light vs 42 % dark, and ZT4-11 is 66-95 % sleep, which fits SD recovery. Keep EMG W vs sleep only.


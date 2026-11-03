---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD17: EEG re-score 2026-11, baseline tier –, recovery tier X"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD17: S-SD (SOD1, sleep deprivation), rig B1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **–** → no recording. 
> - **Recovery:** tier **X** → nothing. review: C -> X: EEG-only HMM split off the delta-railing cluster (NR state ln delta 11.3 vs 7.0), not NREM (reviewer + skeptic)
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline –, recovery NO VERDICT.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | – | C |
| hours usable, EEG + EMG | – | 4 |
| … of them light | – | 3 |
| … of them dark | – | 1 |
| hours usable, EEG alone | – | 4 |
| hours usable, EMG alone | – | 19 |
| EMG separability η (gap; ≥ 0.70) | – | 0.708 |
| η, SleepStager 20–90 Hz EMG | – | 0.856 |
| δ AUC, NR vs W (≥ 0.75) | – | 0.580 |
| EEG median log10 δ (2–4) | – | 3.08 |
| EEG-alone state changes / h (≥ 5) | – | 30.7 |
| κ rule vs HMM | – | 0.33 |
| κ NREM, rule vs EEG alone | – | -0.11 |
| κ rule, gap vs 20–90 Hz EMG | – | 0.91 |
| artifact epochs % | – | 33.1 |
| EEG 60 Hz, median µV | – | 97 |
| EMG 60 Hz, median µV | – | 1060 |
| wake % light (rule) | – | 2.9 |
| wake % dark (rule) | – | 35.5 |
| NREM % light, EEG alone | – | 9.1 |
| NREM % dark, EEG alone | – | 4.5 |
| sleep % light, EMG alone | – | 85.6 |
| sleep % dark, EMG alone | – | 76.4 |
| r@1min (project definition) | – | 0.066 |
| old verdict reason | – | rung 2 CONNECTION: chip floor is 766 uV of 60 Hz (grounded chips show >800) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Recovery

![[2026-11-03-hlb-eeg-hlbssd17-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG partial; rule follows the EEG: mostly; tier disputed → D.
Plausibility: Recovery after SD with 86% sleep in light and 36% wake in dark is in the right direction, but light wake of 1.7% is surprisingly low given the multi-hour wake blocks at hours 0-1.3 and 4.7-6.4. Wake share is partly the rule's EMG cut at 144 uV, which is high.
Concerns: EEG: delta rails (log delta 5+) and broadband stripes at the start, then low-amplitude EEG with weak delta contrast (AUC 0.58); the EEG-only HMM gives 6% NREM and kappa -0.11 against the rule, so the EEG cannot confirm any staging. Only 3 h pass the EEG test. EMG: two-level with flat plateaus (about 1000 uV at hours 0-1.3 and 4.5-6.4, about 30 uV floor at hours 1.5-4) that look technical, but later hours show a real bursty wake pattern, with atonic flat floor in sleep. EMG passes 19 h, so this is an EMG-only recording and tier D fits better than C (C needs a working EEG). Treat REM calls as unverified: theta/delta is present in the traces, but without a reliable EEG contrast.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1944 | R | medium | hmm | Flat atonic EMG (0.18x), theta/delta rises to 1.4 with delta below NR median after NR epochs and flows into R epochs (2.4, 2.1); first epoch of REM. |
| 2 | 2622 | R | medium | rule | Atonic EMG, theta/delta 2.4, delta below NR median, regular theta, bout continues on both sides. |
| 3 | 2637 | NR | medium | rule | EMG burst in the first 1.5 s only (< half), theta/delta 0.5 and slow EEG, next epochs show NR slow waves. |
| 4 | 2786 | NR | medium | rule | Short bursts (< half), EEG irregular slow, theta/delta 0.6; microarousals in NREM. |
| 5 | 2823 | uncertain | low | neither | Mostly atonic, theta/delta 1.5 and delta low, but between NR epochs and EMG burst begins at the end; lone odd epoch before an arousal. |
| 6 | 2935 | W | medium | rule | EMG bursts from about 1.5 s to the end (> half), wake bout follows. |
| 7 | 3134 | R | medium | rule | Flat atonic EMG inside a bout whose neighbours have theta/delta 1.2-2.9; delta back near median only briefly, which does not end REM by itself. |
| 8 | 15403 | R | low | hmm | Atonic EMG; the neighbouring epochs have theta/delta 2.3-3.0 and delta 2.6-2.7 (REM-like) while this one dips to delta at the median; looks like one bout the rule split. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD17_R_epochs.png`.

**Skeptic (tried to refute the rescue):** not usable, tier X. Strongest objection: The EEG-only HMM, which is the sole basis for tier C, split off the delta-railing artifact cluster instead of NREM. Its 'NR' state has a median ln delta of 11.33 against 7.02 for 'not NR' (a 4.3-nat gap, far beyond any physiological NREM/wake contrast). It calls NREM in only 1% of EMG-sleep epochs but in 21-25% of EMG-wake epochs, and 95% of the top-5% delta epochs are EMG-wake. The result is 9% NREM in a post-SD light phase, which is impossible. d' = 4.02 passed only because it measures the artifact split. The 19 'EEG-alone' hours just mean the EEG was not flagged. Only 3 h pass the real EEG test (AUC 0.58 overall, 0.38-0.78 per hour). D also fails by its own gate: EMG-only dark-minus-light wake is 7.6 points, under 10. In addition, ZT6-7 show 0-4% EMG wake for two whole hours on a flat floor, and there are ~900-1000 uV EMG plateaus at ZT4 and ZT8-10. Neither EEG nor EMG supports staging. Checked: score.json (EEG-only NREM 6.3%, kappa NREM rule vs EEG-only -0.11, AUC 0.58, hours EEG ok 3, emg_only_wake_dark_minus_light 7.6, eeg_only_dprime 4.02); blocks_1h (nrem_eeg 0.00-0.20 every hour, wake_frac_emg 0.0 at ZT6); hypnogram: EEG-only state delta medians, P(EEG-only NR | EMG W vs sleep), EMG state of top-delta epochs; hourly delta p90 (11.6-12.0 at ZT4-5), EEG RMS 1851 uV at ZT4; score.py tier logic (d' and light>dark gates).


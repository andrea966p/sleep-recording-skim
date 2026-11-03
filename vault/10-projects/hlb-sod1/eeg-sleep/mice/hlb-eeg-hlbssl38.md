---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSL38: EEG re-score 2026-11, baseline tier D, recovery tier B"
tags: [eeg, hlb, mouse, hlbssl]
---

# HLBSSL38: S-SL (SOD1, ad libitum), rig D2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Recovery:** tier **B** → W / NR / R on the usable hours. review: A -> B: exactly 20 h; tier B with the ss60 EMG; weakest delta separation of the A set, AUC 0.79-0.80 (skeptic + critic)
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NO VERDICT.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | D | A |
| hours usable, EEG + EMG | 0 | 20 |
| … of them light | 0 | 11 |
| … of them dark | 0 | 9 |
| hours usable, EEG alone | 0 | 22 |
| hours usable, EMG alone | 24 | 22 |
| EMG separability η (gap; ≥ 0.70) | 0.814 | 0.859 |
| η, SleepStager 20–90 Hz EMG | 0.782 | 0.788 |
| δ AUC, NR vs W (≥ 0.75) | 0.617 | 0.811 |
| EEG median log10 δ (2–4) | 0.52 | 3.34 |
| EEG-alone state changes / h (≥ 5) | 39.0 | 64.8 |
| κ rule vs HMM | 0.55 | 0.88 |
| κ NREM, rule vs EEG alone | 0.36 | 0.74 |
| κ rule, gap vs 20–90 Hz EMG | 0.94 | 0.96 |
| artifact epochs % | 0.1 | 0.2 |
| EEG 60 Hz, median µV | 26 | 8 |
| EMG 60 Hz, median µV | 71 | 195 |
| wake % light (rule) | – | 30.6 |
| wake % dark (rule) | – | 60.4 |
| NREM % light, EEG alone | – | 53.1 |
| NREM % dark, EEG alone | – | 28.1 |
| sleep % light, EMG alone | 72.8 | 68.3 |
| sleep % dark, EMG alone | 37.7 | 37.1 |
| r@1min (project definition) | – | 0.718 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.2 min | rung 2 CONNECTION: chip floor is carrying signal: its slope threshold is -3.53 (valid floors are flatter than -1.90) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssl38-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG good; rule follows the EEG: not applicable; tier disputed → D.
Plausibility: EMG-only picture is plausible: bursty wake with a low sleep floor, more wake in the dark (76 %). The EEG shows no credible sleep structure, so NR vs REM staging is meaningless. Rule NR is effectively 'sleep by EMG' and the HMM R episodes (hours 0.5-3, 7-9, 18-22) are artefact.
Concerns: EEG amplitude is about 20 times below the other mice (log10 delta ~0.5 versus ~3.3), traces are essentially flat with broadband vertical stripes, delta barely changes between W and NR (AUC 0.62). This looks like a disconnected or shorted EEG channel, not a recording of cortical activity. Tier C does not fit; EMG alone is usable, which is D (EMG good, more wake in dark). The EEG-only HMM calling NR for hours 0-8 is spurious, so do not use EEG-only or HMM R in this mouse. Only 1 usable hour. The old rung-2 'connection fail' verdict for the EEG looks right; the EMG was not wrongly rejected here, only not scoreable for sleep stage.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 11893 | W | low | rule | EEG flat and uninformative; EMG 0.68x cut with small bursts inside a wake bout (7x, 2.7x, 1.2x, 1.6x neighbours), a brief quiet stretch in wake. |
| 2 | 11969 | W | low | hmm | EEG uninformative; EMG continuously active at 0.7x cut (floor ~0.3x) with bursts, and 1.2-1.5x cut right after: quiet wake. |
| 3 | 12136 | W | medium | rule | Continuous bursting EMG around the cut (0.96x), neighbours 4-5x and 1.1x; wake bout. |
| 4 | 12484 | W | low | hmm | Stationary EMG at 0.93x cut for minutes, well above this mouse's sleep floor; EEG flat so no sleep evidence; no bursts, so could be technical plateau. |
| 5 | 12519 | W | low | hmm | Same stationary EMG at 0.98x cut, no sleep floor, EEG uninformative; likely quiet wake. |
| 6 | 12524 | W | low | hmm | Same stationary EMG at 0.91x cut, no sleep floor, EEG flat. |
| 7 | 12564 | W | low | hmm | EMG 0.88x cut and flat plateau with no bursts, EEG flat; tone far above floor so sleep is unlikely. |
| 8 | 12566 | uncertain | low | neither | EMG 0.81x and slowly declining toward the next NR epochs, EEG flat, no bursts; cannot separate quiet wake from sleep onset. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL38_B_epochs.png`.

**Skeptic (tried to refute the rescue):** partially usable, tier D. Strongest objection: Tier C is refuted: the EEG is not cortical signal. Median delta power is 3.3 uV^2 against 1726 in HLBSSL32 (about 500x lower). The spectrum rises with frequency (delta 3.3 < theta 4.5 < sigma 5.2 < beta 11.9 < low gamma 16.8 uV^2), which is the opposite of cortical EEG. Of the 30 uV EEG RMS, 26 uV is 60 Hz mains, and W/NR delta separation is AUC 0.62. This is an open or shorted lead, so the 83 % EEG-only NREM in the light and every NR/R call mean nothing. The old rung-2 rejection was right for the EEG. The EMG is the only usable channel, with one caveat: its gap RMS correlates with 60 Hz amplitude (r 0.45 within sleep, positive in most hours). But the wake/sleep split survives regressing out the 60 Hz term (AUC 0.99 -> 0.98), wake is bursty, and EMG-only wake is higher in the dark (+35 pts), so D holds. A few minutes-long flat EMG plateaus at 0.9x cut around ZT13.9 are likely technical, so treat dark quiet-wake vs sleep as uncertain. Checked: score.json (med_logdelta W 1.13 / NR 1.78 vs ~7-8 in other mice, auc 0.617, hours_both_ok 1), blocks_1h.csv (eeg_alone_ok True for all 24 h, so that screen is defective), overview PNG, median band powers vs HLBSSL32, eeg_rms vs eeg_line60, EMG vs 60 Hz correlation within each hour, EMG W/S AUC after residualising on line60, per-hour EMG floor

## Recovery

![[2026-11-03-hlb-eeg-hlbssl38-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: mostly; tier agreed.
Plausibility: Plausible. Wake 30.6 % light vs 60.4 % dark, long NREM blocks in the light, but the first 0.9 h is wake and the dark phase has a very long, almost continuous wake stretch. Delta separation of NREM vs wake is weaker than in the others (AUC 0.81, EEG-only d' 2.17), and rule vs EEG-only NR kappa is the lowest of the batch (0.74).
Concerns: Tier A is at the threshold: exactly 20 of 24 h usable (tier B by the ss60 EMG). Dropped hours: ZT12, ZT15, ZT23 and ZT4 (and ZT22, 17 are retained). ZT12 and ZT23 are 92-98 % wake and fail the EMG floor test only because they are almost all wake, so they are real wake hours, not bad signal. ZT4 (AUC 0.69, 38 % wake, 53 % NREM) looks like a real sleep hour that is only just under the 0.75 AUC bar and is probably wrongly dropped. ZT15 is 82 % wake with AUC 0.72, also borderline. The raw EMG 60 Hz is large (195 uV) but handled by the notch. Dark-phase EEG is low in delta so the NR/W boundary there relies on EMG.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2912 | uncertain | low | neither | First quiet epoch after a wake bout, EMG flat 0.31x, delta 3.05 below NR median, theta/delta 0.61 and sigma 2.47; neither slow waves nor regular theta. |
| 2 | 5518 | uncertain | low | neither | Flat EMG 0.34x after wake, theta/delta 1.29 with delta 3.08 and sigma 2.62, then back to 0.84; short and mixed, too ambiguous between a brief R and light NR. |
| 3 | 5987 | NR | low | rule | EMG flat 0.29x, sigma 2.92 (spindle-range up), delta 3.13, theta/delta 0.91 intermediate, in a run of ambiguous epochs that ends in clear NR (delta 3.46, sigma 3.03). |
| 4 | 8851 | NR | medium | rule | EMG 0.47x with a single short burst at the very end (about 0.3 s), delta 3.14, theta/delta 0.46, sigma 2.89; microarousal within NR. |
| 5 | 10474 | uncertain | low | neither | Follows an R-looking stretch (theta/delta 1.3-1.5); here theta/delta 0.51 but delta 3.02 has not returned and EMG shows small twitches at 0.48x; theta fading alone does not end REM, so R or NR cannot be decided. |
| 6 | 12969 | uncertain | low | neither | theta/delta 1.15 with delta 3.08 and sigma 2.70, EMG a bit raised (0.55x) with twitches, EMG floor not as flat as in the light phase; R vs NR undecided. |
| 7 | 13032 | W | medium | rule | Quiet wake in a wake bout: EMG activity continuous at 0.74x with bursts, neighbours 3.8x, 1.3x, 1.1x, no slow waves; rule and HMM agree. |
| 8 | 19758 | W | low | hmm | Inside a wake bout (neighbours 2.2-2.4x), EMG 0.87x with continuous activity through the epoch; delta 3.43 is somewhat high but there are no clear slow waves or spindles, and a lone NR epoch in a wake bout needs a reason. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL38_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier B. Strongest objection: Tier A is not robust. It sits exactly on the bar (20/24 h with the gap EMG) and drops to B with the ss60 EMG. Delta separation is the weakest of the A recordings: AUC 0.79 light and 0.80 dark, NR minus W delta only 0.28 log. In the dark, 24 % of rule-NR epochs are not NR for the EEG-only scorer. Those epochs have wake-level delta (3.24 vs W 3.21) and wake-level sigma (2.67 vs 2.63), with EMG at 0.53x the cut. They could be quiet wake under a low EMG, which would inflate dark NR: rule 36.9 % vs EEG-only 28.1 %. Dark-phase NR/W comparisons from this mouse need that caveat. Checked: I read score.json, blocks_1h.csv and the overview, and recomputed per-hour AUC, EMG percentiles and 60 Hz. EMG 60 Hz is 170-250 uV raw but the gap EMG floor is 6-10 uV against a 28 uV cut, so the notch handles it. Dropped hours: ZT12, 15 and 23 are 84-99 % wake, and ZT4 has AUC 0.69, a borderline call. I split rule NR into EEG-agreed and rule-only epochs and compared delta, theta/delta, sigma and EMG for each, by phase. 70 % of the rule-only NR epochs lie inside NR runs, so they are not isolated. Wake is 30.6 % light vs 60.4 % dark; rule-HMM kappa 0.88.


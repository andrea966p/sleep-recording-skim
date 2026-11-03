---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD19: EEG re-score 2026-11, baseline tier X, recovery tier X"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD19: S-SD (SOD1, sleep deprivation), rig D1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **X** → nothing. screen
> - **Recovery:** tier **X** → nothing. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | X | X |
| hours usable, EEG + EMG | 3 | 19 |
| … of them light | 2 | 7 |
| … of them dark | 1 | 12 |
| hours usable, EEG alone | 5 | 20 |
| hours usable, EMG alone | 15 | 19 |
| EMG separability η (gap; ≥ 0.70) | 0.795 | 0.639 |
| η, SleepStager 20–90 Hz EMG | 0.799 | 0.775 |
| δ AUC, NR vs W (≥ 0.75) | 0.769 | 0.807 |
| EEG median log10 δ (2–4) | 3.04 | 3.30 |
| EEG-alone state changes / h (≥ 5) | 9.4 | 66.7 |
| κ rule vs HMM | 0.27 | 0.46 |
| κ NREM, rule vs EEG alone | 0.41 | 0.52 |
| κ rule, gap vs 20–90 Hz EMG | 0.69 | 0.77 |
| artifact epochs % | 85.3 | 28.1 |
| EEG 60 Hz, median µV | 2755 | 113 |
| EMG 60 Hz, median µV | 1403 | 1338 |
| wake % light (rule) | 52.7 | 6.4 |
| wake % dark (rule) | 39.8 | 38.4 |
| NREM % light, EEG alone | – | – |
| NREM % dark, EEG alone | – | – |
| sleep % light, EMG alone | 97.3 | 94.2 |
| sleep % dark, EMG alone | 79.4 | 64.6 |
| r@1min (project definition) | 0.195 | 0.007 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssd19-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG bad; rule follows the EEG: no; tier agreed.
Plausibility: Not plausible. EEG trace is flat with broadband saturation in the spectrogram, so delta and theta numbers are meaningless. EMG shows technical two-level plateaus (about 400 and 80 uV, constant) for hours in the light, so EMG-only sleep of 97% in the light is an artefact of the cut.
Concerns: Rule, HMM and EEG-only disagree (kappa 0.27). Only 3 h pass (2L/1D). The dark EMG has some real bursts, but without EEG nothing can be staged reliably. The rule hypnogram is mostly W, driven by the plateaus. Keep X. The old verdict agrees.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 4566 | uncertain | low | neither | EEG is flat and the EMG is a constant-amplitude plateau (1.21x), which is technical, not muscle. No evidence for wake or sleep. |
| 2 | 4624 | uncertain | low | neither | Same flat EEG and constant EMG plateau (1.19x). The HMM's R rests on meaningless theta/delta numbers. |
| 3 | 10738 | uncertain | low | neither | Constant EMG plateau at 0.86x and a flat EEG, so the NR/R labels have no support. |
| 4 | 10792 | uncertain | low | neither | Plateau EMG (0.86x) with one small burst at the end of the epoch, and a flat EEG. No decision possible. |
| 5 | 13054 | W | low | rule | Real EMG bursts cover roughly half the epoch and a long bout before it (tone 0.94x), in the dark. The EEG is flat, so this rests on the EMG alone. |
| 6 | 13300 | W | medium | rule | Continuous raised, bursty EMG throughout (1.44x cut). The HMM's R is unsupported. The EEG is flat. |
| 7 | 13383 | uncertain | low | neither | EMG is flat at 0.71x after a wake burst a few epochs earlier, but the EEG is flat so atonia alone cannot show REM versus NREM. The rule's W to R transition is unsupported. |
| 8 | 13463 | W | medium | rule | Dense, continuous EMG bursts (1.44x cut) across the window. The EEG is flat, so wake rests on the EMG. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD19_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbssd19-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG partial; rule follows the EEG: mostly; tier disputed → C.
Plausibility: Light wake 6% vs dark 38% in a recovery after SD is plausible and the delta bands alternate with wake as expected; wake blocks in the dark (hours 12.5-15, 16-19) are real in the EEG as well.
Concerns: EEG looks usable: clear delta bursts with W/NR alternation, delta AUC 0.81 (flagged only by the pipeline's recording-level EEG test). EMG is the weak channel: the sleep floor sits at 0.8-0.9x of the wake cut for hours (flat plateau at 0.9x in epoch 943), eta 0.64, so tone cannot cleanly separate quiet wake from sleep in the light and the cut is only just above the floor. The rule's light-phase NREM (82%) may include quiet wake; the EEG-only reading is safer there. I would propose C (EEG reading) rather than X, while flagging that the rule's W/R boundaries depend on a marginal EMG. Hours kept (19) are fine; hour 5-6 dropped looks justified by the grey HMM.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 943 | NR | medium | rule | Flat constant EMG plateau at 0.9x cut with no bursts (the floor in this mouse); delta above NR median, sigma raised (3.0) with slow waves; clear NREM EEG. |
| 2 | 7399 | NR | low | rule | Two short EMG bursts (about 1.5 s total, < half) with delta a little below the NR median and theta/delta 0.6; lights-off onset, next epochs wake, so arousal in NR versus wake is close. |
| 3 | 7809 | W | medium | rule | Continuous bursting EMG at 1.07x cut across the whole epoch and neighbours, delta low, theta/delta 1.3; HMM R not supported. |
| 4 | 9308 | W | medium | rule | Dense EMG burst from about 1.4 s to the end (about 65%), wake bout continues in the following epochs. |
| 5 | 10351 | W | low | neither | EMG stays at 0.9x cut for several epochs (about 2x the dark-phase floor of 0.45x) after wake; regular theta (theta/delta 2.4) with low delta looks like quiet wake with theta, not atonic REM; rule and HMM both say R. |
| 6 | 11654 | W | low | rule | Repeated bursts (about 40% of the epoch) between wake bouts with tone 0.67x and no slow waves; a quiet-wake island. |
| 7 | 12552 | uncertain | low | neither | Moderate EMG with a strong burst only in the last 0.3 s, delta near NR median (3.19), theta/delta 0.6, but the neighbouring epochs are wake and the floor is marginal. |
| 8 | 14538 | NR | medium | rule | Burst of about 1.5 s (< half) with tone otherwise at the sleep floor (0.49x) and delta near median; microarousal in NREM. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD19_R_epochs.png`.


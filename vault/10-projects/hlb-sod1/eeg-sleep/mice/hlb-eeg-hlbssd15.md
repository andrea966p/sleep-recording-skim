---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD15: EEG re-score 2026-11, baseline tier A, recovery tier D"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD15: S-SD (SOD1, sleep deprivation), rig C1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | D |
| hours usable, EEG + EMG | 24 | 5 |
| … of them light | 12 | 3 |
| … of them dark | 12 | 2 |
| hours usable, EEG alone | 24 | 5 |
| hours usable, EMG alone | 24 | 20 |
| EMG separability η (gap; ≥ 0.70) | 0.803 | 0.794 |
| η, SleepStager 20–90 Hz EMG | 0.835 | 0.689 |
| δ AUC, NR vs W (≥ 0.75) | 0.953 | 0.622 |
| EEG median log10 δ (2–4) | 3.23 | 3.15 |
| EEG-alone state changes / h (≥ 5) | 30.8 | 22.5 |
| κ rule vs HMM | 0.76 | 0.58 |
| κ NREM, rule vs EEG alone | 0.82 | 0.07 |
| κ rule, gap vs 20–90 Hz EMG | 0.91 | 0.91 |
| artifact epochs % | 0.1 | 0.2 |
| EEG 60 Hz, median µV | 62 | 117 |
| EMG 60 Hz, median µV | 595 | 509 |
| wake % light (rule) | 27.7 | 18.3 |
| wake % dark (rule) | 60.3 | 54.5 |
| NREM % light, EEG alone | 55.0 | – |
| NREM % dark, EEG alone | 28.9 | – |
| sleep % light, EMG alone | 72.8 | 79.0 |
| sleep % dark, EMG alone | 43.5 | 51.1 |
| r@1min (project definition) | 0.696 | 0.615 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min | rung 2 CONNECTION FAIL: 0.9% usable, longest unbroken block 0.5 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssd15-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible. Clean delta bands alternate with wake all 24 h, clear theta bouts (REM) after NREM, wake 28% light and 60% dark. All 24 h pass the screen.
Concerns: The EMG floor in the light (about 35 uV) sits fairly close to the cut (49) and is slightly elevated, with tone 0.9x in some NREM epochs, so EMG-only decisions in the light are less secure than the EEG ones. The old rung-2 NOT SCOREABLE verdict was clearly wrong for this animal. Dark-phase wake/REM boundaries are the main grey zone.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1789 | uncertain | low | neither | EMG is near the cut (0.97x) with small spikes and delta is below this mouse's NR median (3.34 vs 3.68) with theta/delta about 0.8. It could be NREM with twitches or quiet wake. Not atonic, so the HMM's R is wrong. |
| 2 | 2423 | R | high | rule | EMG is flat at 0.63x, delta is low (3.07) and the EEG shows regular theta. Theta/delta rises through the bout and the run is consistent. |
| 3 | 4918 | R | medium | hmm | Flat atonic EMG (0.73x), delta low (3.09) and regular theta over the epoch and neighbours, then an EMG burst follows. The rule's NR misses a short REM bout. |
| 4 | 12158 | W | high | rule | EMG bursts fill more than half the epoch (1.95x cut), no NREM EEG. |
| 5 | 13172 | R | low | rule | Mostly quiet EMG (tone 0.52x) with small twitches, delta 2.91 and theta present, then a large burst only in the last 0.2 s. A REM bout ending in arousal. The HMM's W is driven by the burst edge. |
| 6 | 13182 | W | low | hmm | EMG shows continuous low-level activity with bursts through the whole window and is not atonic (0.70x tone, similar to the adjacent W epochs). Theta/delta is only 0.7, so the rule's R lacks the atonia. |
| 7 | 13241 | NR | medium | rule | Large slow waves, delta 3.40, sigma up (3.0) and a flat EMG. Plain NREM, so the HMM's R is wrong. |
| 8 | 17538 | W | medium | hmm | EMG is busy with bursts across the epoch (tone 0.85x), not atonic, and a sustained burst bout follows. The rule's R is a mislabel at a wake onset. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD15_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: This has the weakest EMG contrast of the four baselines. The NREM EMG p10/p50 is 21/30 uV against a cut of 49 uV and a wake median of 79 uV (W/NR ratio 2.6), and the EMG line60 median is 595 uV. Light-phase W/NR calls that rest on EMG alone are therefore less secure. This does not refute the window. The EMG split does not follow mains (r between EMG gap and EMG line60 is -0.43, negative). The EEG independently confirms the split: 1-min delta-EMG r is -0.76 (gap) and -0.81 (ss60), AUC is 0.953, the EEG-only HMM calls 0-1% of EMG-wake epochs NREM, and 100% of the top-5% delta epochs are EEG-only NR with only 1% EMG-wake. All 24 h pass, and there are no EEG artifacts. Checked: score.json (eta 0.803, AUC 0.953, 24/24 h, wake L/D 27.7/60.3, kappa 0.76/0.82); features/hypnogram: 1-min delta-EMG correlation, EMG floor percentiles, P(EEG-only NR | EMG W), EMG vs 60 Hz residue correlation, top-delta epochs' EMG state.

## Recovery

![[2026-11-03-hlb-eeg-hlbssd15-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG good; rule follows the EEG: mostly; tier agreed.
Plausibility: Light wake 18% vs dark 55%, more sleep early: plausible. EMG floor is low and steady with clear bursts; r@1min 0.62 shows delta and EMG agree when the EEG is connected.
Concerns: The EEG repeatedly drops to a flat line (log delta about 0, hours about 0-0.8, 4.2-5.3, 6.5-8, 9-11 and several shorter ones, with epochs 10277 and 10438 as examples). During dropouts the rule uses EMG alone; some happen with a quiet EMG, so those hours are scored NR with no EEG support. When connected the EEG is excellent (delta clearly bimodal). Rule gives 0% REM across the whole recording: the theta/delta cut and veto are computed on a distribution polluted by flat-EEG epochs, so REM is probably suppressed and 'no REM' should not be reported. Tier D is right; most of the 5 usable EEG hours are real. The quick hours at the start (epochs 1107, 1130) have theta-like EEG on a flat, non-bursting EMG plateau at 0.75-0.8x cut, which is technical.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1107 | uncertain | low | neither | EEG shows regular theta-like activity with delta low (theta/delta 2.5) but EMG is a flat constant plateau at 0.8x cut with no bursts (technical), so atonia cannot be judged; REM possible. |
| 2 | 1130 | uncertain | low | neither | Same flat EMG plateau, EEG theta/delta 3.3 with low delta: REM-like EEG but no usable EMG; rule NR and HMM W both unsupported. |
| 3 | 2420 | NR | high | rule | Large slow waves, delta at NR median; only a short burst (about 0.8 s) at the end of the epoch. |
| 4 | 2798 | NR | high | rule | EMG at floor, clear slow waves, no burst inside the epoch. |
| 5 | 3283 | NR | low | rule | Low-amplitude small bursts throughout but below the cut; EEG still slow with delta near median, theta/delta 0.7. Transition to wake in the next epoch. |
| 6 | 10277 | W | high | rule | EMG continuously active (1.9x cut) for the whole epoch; EEG is flat (dropout), so the HMM R is an artefact of the flat trace. |
| 7 | 10307 | W | medium | rule | Wake bout with 2.5x EMG on both sides; this epoch drops to about 0.8x with regular theta (theta/delta 2.6, delta low) and no spindles: quiet wake with theta. |
| 8 | 10438 | W | high | rule | Continuous EMG at 1.5x cut with flat EEG dropout; wake by EMG, HMM R is an artefact. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD15_R_epochs.png`.


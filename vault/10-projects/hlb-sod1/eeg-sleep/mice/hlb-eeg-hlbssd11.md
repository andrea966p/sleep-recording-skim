---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD11: EEG re-score 2026-11, baseline tier A, recovery tier X"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD11: S-SD (SOD1, sleep deprivation), rig A1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **X** → nothing. review: C -> X: EEG does not track state: 1-min log delta vs EMG r = -0.02 (baseline -0.74); EEG-only HMM calls 39 % of EMG wake NREM (skeptic)
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | C |
| hours usable, EEG + EMG | 23 | 20 |
| … of them light | 11 | 8 |
| … of them dark | 12 | 12 |
| hours usable, EEG alone | 23 | 20 |
| hours usable, EMG alone | 24 | 20 |
| EMG separability η (gap; ≥ 0.70) | 0.867 | 0.610 |
| η, SleepStager 20–90 Hz EMG | 0.806 | 0.864 |
| δ AUC, NR vs W (≥ 0.75) | 0.952 | 0.601 |
| EEG median log10 δ (2–4) | 3.13 | 3.32 |
| EEG-alone state changes / h (≥ 5) | 28.1 | 82.4 |
| κ rule vs HMM | 0.80 | 0.38 |
| κ NREM, rule vs EEG alone | 0.88 | 0.34 |
| κ rule, gap vs 20–90 Hz EMG | 0.95 | 0.88 |
| artifact epochs % | 2.9 | 14.8 |
| EEG 60 Hz, median µV | 52 | 34 |
| EMG 60 Hz, median µV | 11 | 1488 |
| wake % light (rule) | 28.4 | 8.4 |
| wake % dark (rule) | 67.2 | 17.7 |
| NREM % light, EEG alone | 52.5 | 66.4 |
| NREM % dark, EEG alone | 30.6 | 54.4 |
| sleep % light, EMG alone | 68.2 | 92.6 |
| sleep % dark, EMG alone | 31.0 | 83.6 |
| r@1min (project definition) | 0.494 | -0.073 |
| old verdict reason | rung 2 CONNECTION FAIL: 36.0% usable, longest unbroken block 6.2 min | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssd11-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake is about 28% in the light and 67% in the dark. Bright delta bands alternate with theta bursts, and the EMG shows a low steady sleep floor (about 6 uV) against bursty wake. Dark sleep is fragmented but present.
Concerns: Hour 8-9 has gross EMG excursions (up to about 500 uV) and a broadband EEG stripe, so dropping it is right. Short broadband stripes near hours 1.8 and 3 are brief movement artefacts. The rule, HMM and EEG-only hypnograms agree closely (kappa 0.80). The old rung-2 NOT SCOREABLE verdict looks wrong for this animal. The isolated 'R' calls in the dark are the weakest part (see epochs 4 and 8).

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 3053 | R | medium | hmm | EMG flat at 0.31x cut, delta below its NR median (3.09 vs 3.50), theta/delta high for several consecutive epochs (rule NR* is an island, HMM R). Reads as a short REM bout, not NREM. |
| 2 | 9112 | R | medium | hmm | EEG shows regular theta, delta low (3.14 vs 3.50), theta/delta about 1.9 in a run of raised epochs, and the EMG is flat at 0.38x. The rule's NR has no spindle or slow-wave support. |
| 3 | 9640 | NR | high | rule | EMG burst lasts about 1.5 s (under half the epoch) on a flat floor, and EEG stays NREM (delta 3.35, low theta/delta). That is a microarousal inside NREM. |
| 4 | 10824 | uncertain | low | neither | Lone epoch with theta/delta about 3.1 and flat EMG (0.34x) between NR epochs, at lights-off. The EEG looks theta-like but a single REM epoch needs a reason, so I cannot decide between R and NR. |
| 5 | 12391 | NR | medium | rule | Two short EMG bursts (about 1 s each, under half the epoch) with NREM EEG (delta 3.23, theta/delta about 1.1). Microarousal, stays NR. |
| 6 | 15312 | NR | medium | rule | EMG is flat (0.54x) in this epoch, with the burst in the previous epoch. Delta is 3.35 with sigma up and theta/delta only about 1.3. No sustained theta, so NR. |
| 7 | 15843 | W | medium | rule | EMG bursting for more than half the epoch (1.10x cut) inside a run of bursts. Delta is below NR level, so the HMM's R is wrong. |
| 8 | 17509 | uncertain | low | neither | One burst of about 1.4 s on a raised tone (0.6-0.9x), with delta near NR level (3.57) and theta/delta low. This is either a microarousal in NR or the start of quiet wake. The HMM's R is clearly wrong. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD11_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The gap EMG correlates with the EMG's own 60 Hz residue (r = +0.54 over clean epochs), so the wake/sleep split could in principle be mains-driven. It is not: the EMG median line60 is only 11 uV, 1-min log delta anti-correlates with the EMG at r = -0.74 (gap) and -0.72 (ss60), the EEG-only HMM calls only 2% of EMG-wake epochs NREM, and 90% of the top-5% delta epochs are EMG-sleep. The likely cause is muscle broadband power leaking into the 60 Hz bin, not residue. The old rung-2 rejection does not survive. Hour ZT8 drop is correct. The isolated dark R calls are the weakest part, but they do not affect W/NR. Checked: score.json (eta 0.867, AUC 0.952, 23/24 h both ok, kappa rule-HMM 0.80, NREM rule vs EEG-only 0.88); blocks_1h; features/hypnogram: 1-min delta vs EMG correlation, P(EEG-only NR | EMG W) = 0.02, EMG NR p10/p50 6/9 uV vs W 58 uV (ratio 6.2), artifact epochs are 100% rail touches at ~424 uV, light/dark wake 29.5/68.4% with artifact epochs counted (unchanged).

## Recovery

![[2026-11-03-hlb-eeg-hlbssd11-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG partial; rule follows the EEG: mostly; tier agreed.
Plausibility: Recovery after SD (starts ZT4): mostly sleep early is expected. Wake 8% light / 18% dark is plausible in direction, but the dark wake share is low for a mouse in its active phase, so some quiet wake is probably being scored as NR.
Concerns: EEG is low amplitude with a nearly flat delta (AUC about 0.60), so slow-wave contrast between W and NR is weak even though wake stripes in the spectrogram are clear. The EMG sleep floor sits at about 0.67 of the wake cut all night (cut only about 1.4x the floor, eta 0.61), so atonia cannot be used to separate REM from quiet wake. REM calls here rest on theta/delta alone. Rule says 79% NREM against 59% for the EEG-only HMM, so the rule may be keeping some quiet wake as sleep. Hours are all kept; I see no technical dropout. Tier C is acceptable but B is arguable if the EMG eta threshold is relaxed.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2558 | uncertain | low | neither | Theta/delta 1.46 and delta below the NR median, but EEG is low amplitude without a clear regular theta; EMG at the floor level (0.7x cut), uninformative; next epoch already shows rising tone. |
| 2 | 3305 | R | medium | hmm | Five consecutive epochs with regular 6-9 Hz theta, theta/delta 2-5 and delta below the NR median, EMG flat with no bursts; rule NR is not supported by the EEG. |
| 3 | 7263 | NR | medium | rule | Slow waves with raised sigma (spindle band), theta/delta low, EMG 0.58x cut; the wake burst only starts in the next epoch. |
| 4 | 8243 | W | medium | rule | EMG about 1.0x cut with continuous moderate bursting over about 3.5 s of the 4 s, inside a wake bout; EEG low amplitude with no slow waves. |
| 5 | 8588 | uncertain | low | neither | EMG floor with small twitches, theta/delta 1.55, delta low, but the floor is not truly atonic in this mouse and neighbours alternate NR-like and R-like; lone epoch. |
| 6 | 13077 | R | medium | rule | Inside a run of R epochs: theta/delta 1.8, delta below NR median, EMG at floor with small twitches only. |
| 7 | 16951 | W | low | neither | Sustained EMG 0.8-1.0x cut for five epochs (above this mouse's 0.67 floor), flat EEG with no slow waves or spindles: quiet wake rather than NR; not atonic so HMM R is unlikely. |
| 8 | 17710 | uncertain | low | neither | Single epoch of theta/delta 2.8 with low delta between wake epochs with movement artefact; quiet wake with theta and a one-epoch REM both fit. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD11_R_epochs.png`.

**Skeptic (tried to refute the rescue):** not usable, tier X. Strongest objection: The EEG does not track state at epoch scale, so the tier-C readout (NREM from the EEG alone) is contaminated by movement artifact. 1-min log delta is uncorrelated with the EMG (r = -0.02 gap, -0.06 ss60; the same mouse at baseline gave -0.74). The EEG-only HMM calls 39% of EMG-wake epochs NREM (baselines 1-2%). 89% of the top-5% delta epochs fall in EMG-wake, which means the highest 'delta' is movement artifact (hourly delta p90 jumps to 10-11 at ZT12, 16 and 22, the most active hours). That inflates EEG-only NREM, which explains the implausible 54% dark NREM. The recording-level AUC is 0.60 under both EMG measures. The C gate passed only because the d' test is computed on the HMM's own delta split (self-fulfilling) and light-minus-dark NREM only has to be > 0. The EMG cannot rescue the window: eta_gap 0.61, the floor drifts with a W/NR ratio of 2.2, and rule dark wake is 17.7% (28% with artifact epochs counted), which is implausible for an active-phase mouse 8+ h after SD. Checked: score.json (auc_delta 0.601, eta_gap 0.61 / ss60 0.864, kappa NREM rule vs EEG-only 0.34, EEG-only NREM L/D 66/54); overview.png (delta trace nearly flat with no banding, broadband stripes coinciding with EMG bursts, drifting EMG floor 50-90 uV); hourly delta/p90/EEG RMS; 1-min delta-EMG correlation; P(EEG-only NR | EMG W) = 0.39; EMG state of top-5% delta epochs; AUC recomputed with ss60 (0.604).


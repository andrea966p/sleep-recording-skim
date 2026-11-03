---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD16: EEG re-score 2026-11, baseline tier X, recovery tier X"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD16: S-SD (SOD1, sleep deprivation), rig C2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **X** → nothing. screen
> - **Recovery:** tier **X** → nothing. review: C -> X: intermittent EEG contact (lost ZT7-8, mostly lost ZT15-18, 16-20 Hz band ZT6.8-9); C exactly on its 6-light-hour bar (skeptic)
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | X | C |
| hours usable, EEG + EMG | 13 | 9 |
| … of them light | 9 | 3 |
| … of them dark | 4 | 6 |
| hours usable, EEG alone | 13 | 12 |
| hours usable, EMG alone | 24 | 17 |
| EMG separability η (gap; ≥ 0.70) | 0.667 | 0.703 |
| η, SleepStager 20–90 Hz EMG | 0.749 | 0.652 |
| δ AUC, NR vs W (≥ 0.75) | 0.807 | 0.671 |
| EEG median log10 δ (2–4) | 3.31 | 3.26 |
| EEG-alone state changes / h (≥ 5) | 55.8 | 85.8 |
| κ rule vs HMM | 0.60 | 0.41 |
| κ NREM, rule vs EEG alone | 0.55 | 0.43 |
| κ rule, gap vs 20–90 Hz EMG | 0.57 | 0.57 |
| artifact epochs % | 44.0 | 38.9 |
| EEG 60 Hz, median µV | 91 | 83 |
| EMG 60 Hz, median µV | 1153 | 1443 |
| wake % light (rule) | 15.7 | 31.1 |
| wake % dark (rule) | 33.3 | 31.6 |
| NREM % light, EEG alone | 60.7 | 60.9 |
| NREM % dark, EEG alone | 40.6 | 50.9 |
| sleep % light, EMG alone | 63.9 | 40.5 |
| sleep % dark, EMG alone | 53.0 | 53.1 |
| r@1min (project definition) | 0.129 | 0.083 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssd16-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG bad; rule follows the EEG: mostly; tier agreed.
Plausibility: Not plausible as staged. The rule gives 73% NREM and only 20% wake (33% in the dark) for a 24 h baseline, so wake is under-called. The EMG floor never separates from the cut (eta 0.67). Delta is shallow and the EMG sits at a constant amplitude in many epochs.
Concerns: EMG has no clear sleep floor: the floor is about 45-50 uV against a cut of 63, with long constant-amplitude (technical) stretches at 0.8-0.9x, so the rule's W/NR call is fragile. EEG shows weak delta structure and a narrowband stripe near 18-20 Hz. Hours 16-24 are dropped for EEG disagreement. The EEG-only run has many grey (X) stretches. Only about 13 h pass (9L/4D), so tier B fails. EEG-only (C) could be argued for the light hours, but I would keep X.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 835 | NR | low | rule | EMG at the floor (0.83x, no bursts) between wake stretches, delta near NR level (3.42 vs 3.37) with a slow wave in the previous epoch. A weak call that could also be quiet wake. |
| 2 | 5231 | uncertain | low | neither | EMG is a constant-amplitude plateau (0.88x), which is technical rather than muscle. The EEG is low amplitude with delta slightly below NR level and mixed theta, so NR, R and quiet wake are all possible. |
| 3 | 8216 | uncertain | low | neither | Same constant EMG plateau (0.79x) and a long run of HMM R against rule NR with similar EEG on both sides. No regular theta or slow waves, so no decision. |
| 4 | 8308 | W | medium | rule | EMG bursts through about half or more of the epoch (1.25x cut) with a movement artefact in the EEG, in a run of W epochs. |
| 5 | 9513 | R | medium | hmm | EMG flat and lower than this mouse's usual floor (0.65x), delta low (2.83) and theta/delta raised and rising over several epochs. REM-like. The rule's NR* disagrees with its own R* mark. |
| 6 | 10301 | NR | low | rule | One burst of about 1.5 s then low chatter (tone 0.90x), with delta near NR level (3.32). A short burst inside NREM, but the raised tone leaves some doubt. |
| 7 | 11078 | W | medium | rule | Just after lights-off in a run of chatter and bursts, with high theta/delta (2.4, active-wake theta), low delta (2.72) and tone about 0.8x. Active wake. |
| 8 | 11731 | W | low | neither | EMG chatter and bursts over the epoch (not atonic) in the dark, theta/delta 1.8 with low delta, bordering a W epoch. Looks like active wake, so neither NR nor R. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD16_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbssd16-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG partial; rule follows the EEG: mostly; tier agreed.
Plausibility: Rule wake is 31% in both light and dark, which is flat for a mouse; the cause is the first 5 h scored W. Recovery after SD should be mostly sleep early, so those hours are suspect. After hour 5 the pattern is plausible.
Concerns: For hours 0-5 the EMG sits at about 60-70 uV, just above the wake cut of 53 and with no sleep floor, so the rule scores a 5 h W block that is probably wrong (EMG offset, not muscle); EEG in the same stretch is dull with a constant 16-20 Hz band (technical) and the HMM/EEG-only mark it X. EEG artefact is 39%. EMG after hour 5 looks usable (floor about 40, clear bursts in the dark), but the cut is only slightly above the floor, and dark minus light wake from EMG alone is negative, so a D reading would fail. C is acceptable but only for hours 5-20; EEG quality is borderline and I would treat the first 5 h as unscoreable rather than as wake.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 4563 | uncertain | low | neither | EMG dense and continuous at about the cut (1.0x), the same plateau as the first 5 h, with no clear bursts; EEG low amplitude; cannot tell tone from offset. |
| 2 | 6911 | W | high | rule | EMG 1.9x cut and continuous for the whole epoch; HMM R unsupported. |
| 3 | 6927 | W | high | rule | EMG 1.9x cut, dense bursts throughout the epoch and neighbours. |
| 4 | 7365 | uncertain | low | neither | EMG 0.84x cut, small bursts only, theta/delta 0.8, no spindles; just after the lights-off wake and this mouse's floor is high, so NR and quiet wake both fit. |
| 5 | 7494 | R | low | hmm | Following epochs show rising theta/delta (1.75, 2.2, 2.4), delta low, sigma dropped and EMG flat under the cut after an NR epoch with spindles; first epoch of a REM bout, though the EMG floor is high. |
| 6 | 14059 | NR | medium | rule | EMG 0.6x flat, delta at NR median, irregular slow waves; theta/delta only 1.0. |
| 7 | 14078 | W | high | rule | Sustained EMG bursts across the epoch and a movement artefact in the EEG (delta 4.8). |
| 8 | 15066 | W | high | rule | EMG 1.9x cut dense throughout; wake theta (theta/delta 4.7), so the HMM R is wrong. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD16_R_epochs.png`.

**Skeptic (tried to refute the rescue):** partially usable, tier X. Strongest objection: Intermittent EEG contact, and the C gate sits exactly on its threshold (6 light hours). The EEG is entirely lost at ZT7-8 (0 and 39 clean epochs), carries a technical 16-20 Hz band from about ZT6.8 to ZT9, and is mostly lost at ZT15-18 (125-405 clean). The rest is cut by frequent broadband stripes, with delta spiking to 5+ log10. The excluded EEG epochs are biased toward wake (P(ss60 W) is 0.74 in EEG-artifact epochs against 0.34 in clean ones). EEG-only NREM is therefore computed on a sleep-enriched sample, which inflates the 51% dark NREM. The EEG-only call also takes 13% (ss60) to 41% (gap) of EMG-wake epochs. eeg_recording_ok is false (AUC 0.67 under gap EMG). The gap EMG has a 5-h plateau (ZT4-9) at 60-70 uV above the cut with no sleep floor, the EMG W/NR ratio is 1.8, and EMG-only dark-minus-light wake is negative (-18). The 9 both-ok hours (ZT9-14 and ZT19-21, hourly AUC 0.76-0.85) are readable, but they fall short of B on light hours (3). Checked: score.json (eeg_recording_ok false, AUC 0.671 gap / 0.818 ss60, EEG artifact 38.9%, hours EEG-alone 6L/7D, both ok 3L/6D); blocks_1h (EEG clean counts per hour, ZT4-5 EMG floor above cut); overview.png (16-20 Hz band, EMG plateau, dense stripes); P(EEG-only NR | EMG W); EEG-artifact vs EMG-state bias; 1-min delta-EMG r -0.30/-0.48.


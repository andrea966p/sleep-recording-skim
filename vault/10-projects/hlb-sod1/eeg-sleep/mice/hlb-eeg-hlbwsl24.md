---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSL24: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbwsl]
---

# HLBWSL24: W-SL (water, ad libitum), rig B2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** yes.
> - Old pipeline: baseline SCOREABLE, recovery SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | A |
| hours usable, EEG + EMG | 24 | 24 |
| … of them light | 12 | 12 |
| … of them dark | 12 | 12 |
| hours usable, EEG alone | 24 | 24 |
| hours usable, EMG alone | 24 | 24 |
| EMG separability η (gap; ≥ 0.70) | 0.845 | 0.840 |
| η, SleepStager 20–90 Hz EMG | 0.740 | 0.725 |
| δ AUC, NR vs W (≥ 0.75) | 0.900 | 0.875 |
| EEG median log10 δ (2–4) | 3.11 | 3.11 |
| EEG-alone state changes / h (≥ 5) | 30.8 | 30.6 |
| κ rule vs HMM | 0.89 | 0.91 |
| κ NREM, rule vs EEG alone | 0.85 | 0.83 |
| κ rule, gap vs 20–90 Hz EMG | 0.94 | 0.94 |
| artifact epochs % | 0.0 | 0.0 |
| EEG 60 Hz, median µV | 50 | 8 |
| EMG 60 Hz, median µV | 32 | 6 |
| wake % light (rule) | 27.0 | 25.1 |
| wake % dark (rule) | 65.2 | 67.7 |
| NREM % light, EEG alone | 56.3 | 56.2 |
| NREM % dark, EEG alone | 30.6 | 28.5 |
| sleep % light, EMG alone | 72.8 | 74.6 |
| sleep % dark, EMG alone | 35.4 | 33.1 |
| r@1min (project definition) | 0.753 | 0.767 |
| old verdict reason | 24.00 h in 3 block(s), r@1min 0.460 | 24.00 h in 1 block(s), r@1min 0.682 |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsl24-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible. Wake 29% light vs 65% dark, strong delta bands in the light and early dark, low EMG sleep floor with bursty wake, 23 of 24 hours kept. All three hypnograms agree (kappa rule-HMM 0.89).
Concerns: The single dropped hour (ZT3-4) looks fine on the overview (no obvious artefact), may be a borderline EEG agreement score; not a real loss. A few brief EMG bursts inside NREM are called arousal-W by the HMM; the rule treats the shorter ones correctly as microarousals. Old verdict SCOREABLE agrees.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1753 | NR | medium | rule | One burst of about 1.5 s (under half) then flat, delta 3.24 near NR median 3.33, theta/delta 0.29, NR neighbours; microarousal. |
| 2 | 4241 | W | low | rule | Epoch begins with the tail of a big burst (mean 1.95x cut) after a strong W epoch, delta 2.81 low, sigma 2.08 dropped; boundary with NR, burst about half the epoch. |
| 3 | 4476 | uncertain | low | neither | Atonic EMG 0.24x, delta low 2.94 and sigma low 2.16 but theta/delta only 0.33; long run of similar epochs, could be weak REM or deep quiet sleep, theta not dominant. |
| 4 | 4957 | NR | low | rule | Atonic EMG 0.44x, theta/delta 1.11 but sigma 2.74 not dropped and delta 3.11; REM starts the next epoch, this one is the NR edge. |
| 5 | 5300 | NR | low | rule | Between two bursty wake episodes, EMG 0.50x cut with only small activity, delta 3.10, theta/delta 0.43; HMM W unsupported but quiet wake cannot be excluded. |
| 6 | 6160 | NR | medium | rule | Only a brief burst at about 3.6 s, EMG tone 0.31x cut for the rest, delta 3.03, sigma 2.61, theta/delta 0.27; sleep after the wake bout ended. |
| 7 | 6532 | uncertain | low | neither | Strong EMG burst of about 2.2 s (a bit over half) inside NREM, but delta 3.19 slow waves persist, sigma 2.07 dropped, theta/delta 0.18; brief arousal borderline between W and NR. |
| 8 | 8400 | R | medium | rule | Flat atonic EMG 0.21x, theta/delta 0.61 at the start of a bout that rises to 1.47, delta 3.01, regular theta in trace (rule and HMM both R). |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL24_B_epochs.png`.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsl24-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 26.8 % in the light and 67.7 % in the dark, delta bands alternate with wake bursts, and the EMG has a clear floor with bursts. Light-phase sleep is consolidated and the last light hours turn to wake. A strong NR block at about ZT20 to ZT22 is seen in both delta and the rule.
Concerns: Hour 8 (ZT8 to ZT9) was dropped, probably on EEG-agreement because the hour is mixed wake and NR. In the overview it looks like an ordinary transition hour and the loss is small. Several contested epochs sit just after wake bouts, where EMG bursts cover about half the epoch and the rule's NR/W call is borderline. Rule vs HMM kappa is 0.91. Old verdict SCOREABLE.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 8102 | uncertain | low | neither | An EMG burst covers about 0 to 2.3 s, which is borderline half the epoch (gapped, so under half of the time is active). The EEG still has NR slow waves with delta 3.13 and the neighbours are NR. This could be a brief arousal. |
| 2 | 11851 | NR | high | rule | EMG is flat at 0.31x, delta 3.29 is near the NR median, and slow waves are present. Wake bursts are in other epochs. |
| 3 | 12532 | NR | medium | rule | A wake bout ended about 2 s before the epoch, and EMG is now quiet at 0.43x with heartbeat spikes. The EEG is moderate-amplitude with delta 2.84, and slow waves return in the next epochs. REM cannot start straight after wake, so this is light NR, not R. |
| 4 | 15188 | uncertain | low | neither | EMG is quiet at 0.45x and the EEG is low-amplitude mixed activity with delta 2.84 (below the NR median). It follows a quiet-wake epoch. It could be light NR, REM or quiet wake, and theta is not clearly regular. |
| 5 | 16670 | uncertain | low | neither | Small scattered EMG bursts increase through the epoch (0.74x the cut), delta 3.01 has dropped, and a clear wake bout follows. It may already be over half active, but it is not clear. |
| 6 | 19513 | NR | low | rule | EMG bursts are brief, with roughly 1.5 s active out of 4 s, and sit between a wake bout and quiet NR. EEG slow waves and delta 3.15 are NR-like. This is a microarousal-type epoch. |
| 7 | 20780 | W | low | hmm | EMG has continuous moderate bursting through the whole epoch (0.99x the cut) between wake neighbours (1.3x to 1.5x). The EEG is low-amplitude with delta only 3.18. Muscle is active most of the epoch, so it is more likely wake. |
| 8 | 21222 | W | high | rule | EMG is bursting continuously across the whole epoch among strongly active neighbours (1.9x to 3.6x). Delta 3.12 is not decisive during movement. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL24_R_epochs.png`.


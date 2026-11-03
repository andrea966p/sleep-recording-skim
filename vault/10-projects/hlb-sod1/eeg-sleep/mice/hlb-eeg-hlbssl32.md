---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSL32: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbssl]
---

# HLBSSL32: S-SL (SOD1, ad libitum), rig A2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** yes.
> - Old pipeline: baseline NOT SCOREABLE, recovery NO VERDICT.

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
| EMG separability η (gap; ≥ 0.70) | 0.881 | 0.873 |
| η, SleepStager 20–90 Hz EMG | 0.799 | 0.793 |
| δ AUC, NR vs W (≥ 0.75) | 0.950 | 0.947 |
| EEG median log10 δ (2–4) | 3.24 | 3.24 |
| EEG-alone state changes / h (≥ 5) | 27.4 | 27.2 |
| κ rule vs HMM | 0.91 | 0.94 |
| κ NREM, rule vs EEG alone | 0.89 | 0.89 |
| κ rule, gap vs 20–90 Hz EMG | 0.98 | 0.92 |
| artifact epochs % | 0.0 | 0.1 |
| EEG 60 Hz, median µV | 69 | 12 |
| EMG 60 Hz, median µV | 730 | 99 |
| wake % light (rule) | 26.5 | 26.4 |
| wake % dark (rule) | 72.2 | 68.8 |
| NREM % light, EEG alone | 56.7 | 57.1 |
| NREM % dark, EEG alone | 23.6 | 27.2 |
| sleep % light, EMG alone | 73.5 | 73.4 |
| sleep % dark, EMG alone | 28.7 | 31.7 |
| r@1min (project definition) | 0.786 | 0.775 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min | rung 2 CONNECTION: chip floor is carrying signal: its slope threshold is -2.61 (valid floors are flatter than -1.90) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssl32-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible: strong alternation of bright-delta NR and wake, REM-like theta episodes, wake concentrated in the dark (long EMG plateaus ZT12-18, 20-23) and sleep in the light. Rule, HMM and EEG-only agree (kappa 0.91 / 0.89).
Concerns: The old rejection (rung 2 'connection fail', EMG 60 Hz of 730 uV) was about mains in the old EMG band; with the mains-free EMG the sleep floor is low and steady and wake is bursty, so the old rejection looks wrong. All 24 h usable. The rule seems to miss some REM bouts where theta/delta is 1-1.5 but delta is only moderately low (epochs 6596, 7575, 21462); REM share is not a result anyway.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 3231 | W | low | hmm | EMG burst covers roughly 2.5 s of the 4 s (1.14x cut), more than half; EEG stays NREM-like (delta 3.50) and both neighbours are NR, so this is a microarousal that could equally stay NR. |
| 2 | 6596 | R | medium | hmm | Part of a multi-epoch bout with theta/delta 1.0-1.5 and delta 3.2-3.3 below NR median, EMG flat at floor, no spindles. |
| 3 | 7575 | R | low | hmm | Bout of five epochs with theta/delta 0.7-1.0, delta 3.1-3.3 low, atonic EMG; trace is only moderately regular theta. |
| 4 | 9307 | R | low | hmm | Delta drops from 3.62 to 3.19 and theta/delta rises (next epoch 1.39) after NR, sigma falls, EMG floor: likely REM onset, one epoch early. |
| 5 | 14587 | W | medium | rule | Continuous raised EMG across the whole epoch (0.78x cut, tone 0.75x) inside a wake bout with big bursts on both sides; quiet wake, delta at wake level. |
| 6 | 17341 | R | low | hmm | Delta 3.07 low, theta/delta 1.14, regular-looking theta, EMG floor, but only a 2-3 epoch bout; the next epoch returns to NR (delta 3.77). |
| 7 | 18562 | NR | medium | rule | Only a short EMG blip (<1 s) in a 4 s epoch, EEG delta 3.40 with theta/delta 0.43; microarousal inside NREM stays NR (HMM also NR). |
| 8 | 21462 | R | low | hmm | Four consecutive epochs with theta/delta 0.8-1.5 and delta 3.2-3.4 below NR median, EMG at floor; delta is not fully low, so REM is likely but not certain. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL32_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The raw EMG carries 730 uV of 60 Hz, which is extreme, so the wake split could in principle be mains residue. Tested and rejected: 60 Hz amplitude is LOWER in rule-W epochs (AUC 0.17, r -0.56), so it cannot be producing the wake calls. The EEG independently agrees (delta AUC NR vs W 0.95; 0.4 % of W epochs have NR-level delta). ZT13-16 pass the floor test only through the all-wake exemption, but delta there sits at wake level (3.05) with no NR epochs, so the wake is real. The rule probably misses some short low-contrast REM bouts. That does not affect the tier, and REM share is not a result. Checked: score.json, blocks_1h.csv, overview PNG, per-hour delta NR/W/all, eeg_rms, EMG floor and wake level, EMG gap vs line60 correlation and AUC, fraction of W epochs with NR-level delta, gap vs ss60 kappa 0.98

## Recovery

![[2026-11-03-hlb-eeg-hlbssl32-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake 26.4 % in the light vs 68.8 % in the dark, long consolidated NREM blocks in the first 8 h, strong delta contrast (AUC 0.95, EEG-only d' 2.8). Rule-HMM kappa 0.94.
Concerns: Raw 60 Hz in the EMG is large (about 99 uV) but the mains-free EMG shows a clean sleep floor with heartbeat spikes and clear bursts, so the notch works. All 24 h are usable and I would not drop any. Old verdict NO VERDICT (floor slope) is not evidence of bad signal. The R/NR calls at transitions are the weak point, as in every recording.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2256 | NR | high | rule | Large slow waves, delta 3.66 above NR median, theta/delta 0.61, sigma high, EMG flat at 0.29x with heartbeat only; rule and HMM agree. |
| 2 | 4146 | uncertain | low | neither | Atonic EMG but sigma 2.90 has not dropped and delta 3.41 is near NR level, theta/delta 0.80; this looks like the transition epoch before an obvious R bout (next epochs theta/delta 1.7, delta 3.0), so the rule's one-epoch-earlier R is plausible but not shown by this epoch itself. |
| 3 | 5114 | W | medium | hmm | EMG 0.86x with continuous bursts through the epoch, neighbours 0.9-1.6x, low-amplitude fast EEG (delta 3.11, sigma 2.87), sits inside a wake bout; rule's NR is not supported. |
| 4 | 9505 | uncertain | low | neither | Flat EMG 0.32x right after a wake burst, delta 3.18, theta/delta 0.60 with 1.09 before and 0.81 after, sigma 2.41 low; could be early R or light NR, traces do not decide. |
| 5 | 9732 | NR | low | rule | Wake burst ended 2 s before the previous epoch, EMG 0.36x flat, delta 3.29 near NR level, theta/delta 0.81 and sigma 2.76 not dropped; REM straight after wake is unlikely. |
| 6 | 12301 | NR | high | rule | Delta 3.50 at NR level with big slow waves, EMG flat 0.29x with heartbeat, only a tiny twitch; rule and HMM agree. |
| 7 | 17310 | NR | low | rule | Delta 3.42 near NR median, sigma 2.58, theta/delta 0.71, EMG flat; the preceding epoch looks R-like (theta/delta 1.86) but this one has not clearly left NR. |
| 8 | 18245 | R | low | hmm | EMG flat 0.36x, sigma low at 2.48 and EEG fast low-amplitude with theta/delta 0.89, sitting between epochs with theta/delta 1.98 and 1.09-1.63; a continuous R bout with a dip is plausible. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL32_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: Raw EMG mains is about 99 uV, so a mains-driven split is possible in principle. Tested: 60 Hz is uncorrelated with the wake calls (AUC 0.54, r 0.05). The EMG shows a clean 0.2-0.4x floor and 2-3x bursty wake, and the EEG agrees (delta AUC 0.95, rule-HMM kappa 0.94, NR rule vs EEG-only kappa 0.89). The only real weakness is NR/R calls at transitions, the same as in every recording. The old NO VERDICT was a floor-slope condition, not evidence of a bad signal. Checked: score.json, blocks_1h.csv, overview PNG, per-hour delta, EMG floor and wake level, 60 Hz correlation and AUC, W epochs with NR delta


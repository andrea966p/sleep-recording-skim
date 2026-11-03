---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSL25: EEG re-score 2026-11, baseline tier A, recovery tier A"
tags: [eeg, hlb, mouse, hlbwsl]
---

# HLBWSL25: W-SL (water, ad libitum), rig C1

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
| hours usable, EEG + EMG | 24 | 23 |
| … of them light | 12 | 12 |
| … of them dark | 12 | 11 |
| hours usable, EEG alone | 24 | 24 |
| hours usable, EMG alone | 24 | 23 |
| EMG separability η (gap; ≥ 0.70) | 0.814 | 0.849 |
| η, SleepStager 20–90 Hz EMG | 0.766 | 0.784 |
| δ AUC, NR vs W (≥ 0.75) | 0.874 | 0.889 |
| EEG median log10 δ (2–4) | 3.25 | 3.23 |
| EEG-alone state changes / h (≥ 5) | 53.2 | 50.8 |
| κ rule vs HMM | 0.76 | 0.87 |
| κ NREM, rule vs EEG alone | 0.75 | 0.79 |
| κ rule, gap vs 20–90 Hz EMG | 0.95 | 0.95 |
| artifact epochs % | 0.0 | 0.1 |
| EEG 60 Hz, median µV | 32 | 9 |
| EMG 60 Hz, median µV | 941 | 100 |
| wake % light (rule) | 24.2 | 26.5 |
| wake % dark (rule) | 62.2 | 65.3 |
| NREM % light, EEG alone | 57.1 | 56.1 |
| NREM % dark, EEG alone | 32.0 | 30.0 |
| sleep % light, EMG alone | 76.2 | 73.0 |
| sleep % dark, EMG alone | 40.5 | 34.9 |
| r@1min (project definition) | 0.644 | 0.719 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min | rung 2 CONNECTION: chip floor is 5 uV of 60 Hz (grounded chips show >800) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsl25-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG partial; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. Wake 24% light vs 62% dark, clear delta bands, EMG two-level with bursts, all 24 hours kept; the rule tracks the EEG closely.
Concerns: EMG is partial: 60 Hz on the EMG is huge (941 uV, which killed the old rung 2) and the mains-free sleep floor is high (about 20 uV, double other mice), so tone separation is narrower and absolute EMG ratios near 0.5x are the sleep floor, not partial wake. Even so the EMG is clearly bimodal with real bursts, so the tier A is deserved and the old NOT SCOREABLE is wrong. HMM (kappa 0.755) marks wake in the light period around ZT2.5-6 where the EEG still shows NREM; the rule is better there.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1332 | W | low | hmm | Continuous EMG at 0.64x cut for many epochs after a big wake burst, delta 2.72 very low (NR median 3.48), sigma 2.27 low; looks like quiet wake rather than NREM. |
| 2 | 1982 | NR | low | rule | Delta 3.30 near NR level, theta/delta 0.77, EMG at sleep floor; previous epoch looked R-like but here delta has returned, so REM has ended. |
| 3 | 2207 | NR | medium | rule | Sigma 2.93 high with spindle-like waxing waves, delta 3.24, theta/delta 0.94 not dominant; EMG at sleep floor. |
| 4 | 10420 | uncertain | low | neither | Scattered short EMG twitches (under half), delta 3.19 reduced, sigma 2.59; right before lights-off wake, NR vs early W not decidable. |
| 5 | 13486 | R | medium | hmm | EMG flat at 0.48x (sleep floor), regular theta, theta/delta 2.50, delta 2.84 low, sigma 2.57; follows a W/NR stretch, so entry from wake is odd but the traces are REM-like. |
| 6 | 13789 | W | high | rule | EMG burst covers about 55% of the epoch, epoch mean 2.7x cut, delta lowered 3.00 (rule and HMM both W). |
| 7 | 15504 | W | medium | rule | Irregular muscle activity throughout the epoch (0.93x cut) inside a dark-phase wake bout with big bursts either side, no atonia; quiet wake. |
| 8 | 17798 | NR | high | rule | Large slow waves, delta 3.53 above NR median 3.48, sigma 2.85, theta/delta 0.61; HMM R unsupported. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL25_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: Most of the sleep EMG floor is technical, not muscle. In NR, 65 % of the gap-band (70-470 Hz) power sits in a 20 Hz comb of interference lines (460 Hz at 273x the band median, also 340 Hz). These lines are not multiples of 60, so the notches leave them in. The chance level for those bins is about 0.13. So the about 20 uV floor (0.5x the cut) is mostly interference, raw EMG mains is 941 uV, and no heartbeat shows on the floor. The rule-HMM kappa is the lowest of the set (0.755): the HMM calls ZT2.5 to 4.5 wake while delta is high. In the light the rule's NR is 11 points above the EEG-only NR (68.2 vs 57.1 %), so some quiet wake may be scored NR. I accept A anyway, because the wake/sleep split does not depend on the interference. The gap and ss60 EMG agree on wake/sleep for 97.2 % of epochs, and the ss60 band has the comb near chance (0.20). The hourly EMG p10 is stable at 17 to 20 uV, so there is no step change. EMG RMS is anti-correlated with the 60 Hz line (rho -0.36), so mains does not create the wake calls. Checked: Brief; overview and epochs PNGs; score.json; blocks_1h.csv (24/24 hours, AUC per hour 0.80 to 0.93). From features.parquet and hypnogram.parquet: medians by stage (EMG NR 19.8 / W 70.3 uV; log10 delta NR 3.48 / W 3.08); NR-W delta gap 0.40; 7.3 % of NR epochs below the W median delta; 1-min Spearman logEMG vs delta -0.57; hourly EMG p10, p90 and 60 Hz line; gap vs ss60 wake/sleep agreement. From psd_emg.npy: share of 20 Hz comb power in the NR and W EMG bands. Wake light/dark 24.2 / 62.2 %. Old rung-2 CONNECTION FAIL came from mains on the EMG, not from the signal.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsl25-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 26.5 % in the light and 65.3 % in the dark, with delta bands in the light and a dark rebound at about ZT20. The EMG shows a low floor with heartbeat spikes and wake plateaus. The EEG-only HMM agrees with the rule's NREM, with kappa 0.79.
Concerns: Hour 12 (ZT12 to ZT13) was dropped. It is the lights-off hour, mixed sleep and wake, and the loss is probably an EEG-agreement or floor test failing on a transitional hour; one hour only. The old 'NO VERDICT' (chip floor 5 uV) was not a judgement of signal quality. Raw EMG 60 Hz is 100 uV before the notch, but the filtered EMG looks clean. A few thin vertical stripes in the spectrogram (around ZT10 and ZT14) are brief artefacts.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 395 | NR | medium | rule | A wake burst occurred about 4 s earlier, and EMG is quiet at 0.47x. Delta 2.94 is low but slow waves return in the next epochs. There is no regular theta, so the HMM's R is unsupported. |
| 2 | 2091 | R | low | rule | It follows clear atonic REM (theta/delta 1.7 to 1.9 before) and EMG is still low at 0.28x apart from a blip at the very end. Delta 3.15 and theta/delta 0.49 show fading theta, which alone does not end REM. The wake bursts only start in the next epoch. |
| 3 | 3427 | NR | medium | rule | EMG is flat at 0.33x, delta 3.36 is near the NR median, and sigma is high at 2.76. Slow waves are large. Theta/delta 0.72 is not REM-like. |
| 4 | 4225 | NR | low | rule | A wake bout ended less than 1 s before the epoch. EMG is 0.56x with one small burst at about 2 s (less than half the epoch). The EEG is low-amplitude and mixed, so this is light NR or quiet wake, but it cannot be REM straight after wake. |
| 5 | 5106 | NR | high | rule | EMG is flat at 0.37x, delta 3.20 is near the NR median, and sigma is high at 3.11, with large waves and spindles. It does not look like REM. |
| 6 | 6014 | R | medium | rule | EMG is flat at 0.35x with heartbeat spikes, delta 2.98 is below the NR median, theta/delta 2.26, and the EEG shows regular theta. It sits inside an R run (R in neighbours). |
| 7 | 10045 | uncertain | low | neither | EMG is flat at 0.37x with heartbeat spikes. The EEG is regular and moderate-amplitude, but sigma is high (2.77), delta 3.18 is not low, and theta/delta is only 0.96. NR vs R is not decided. |
| 8 | 11972 | NR | medium | rule | EMG is tonic at 0.55x (not atonic) with no bursts, delta 2.95 and theta/delta 0.64. It is light NR just before a wake bout, so not REM. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL25_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: Hour 12 (lights off) failed the EMG floor test. Its p10 floor is above the cut (floor_rel +0.34) while EEG-only calls 19 % of it NREM, so in that hour the EMG and EEG disagree about sleep. Hours 16, 17 and 19 also have raised floors (p10 13.9 / 13.2 / 38.2 uV vs cut 26) in the dark, where the quiet-wake vs NR boundary is soft. It is one hour of 24, and the light/dark wake split is the same on all hours and on kept hours (26.6 %). This does not change the tier. Checked: Brief; previous reviewer's notes; score.json; blocks_1h.csv. From the parquets: EMG NR 9.7 / W 71.5 uV; NR-W delta gap 0.43; 5.4 % of NR epochs below the W delta median; 85 % agreement with EEG-only NR; 1-min rho -0.49; hourly floors; wake share on all vs kept hours. Comb share at chance (0.13). The old NO VERDICT (chip floor 5 uV) was not a judgement of the signal.


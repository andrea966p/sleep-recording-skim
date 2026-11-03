---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSL21: EEG re-score 2026-11, baseline tier A, recovery tier D"
tags: [eeg, hlb, mouse, hlbwsl]
---

# HLBWSL21: W-SL (water, ad libitum), rig A1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **A** → W / NR / R, whole window. screen
> - **Recovery:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NO VERDICT, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | D |
| hours usable, EEG + EMG | 23 | 0 |
| … of them light | 12 | 0 |
| … of them dark | 11 | 0 |
| hours usable, EEG alone | 23 | 0 |
| hours usable, EMG alone | 24 | 24 |
| EMG separability η (gap; ≥ 0.70) | 0.832 | 0.745 |
| η, SleepStager 20–90 Hz EMG | 0.630 | 0.665 |
| δ AUC, NR vs W (≥ 0.75) | 0.945 | 0.372 |
| EEG median log10 δ (2–4) | 3.11 | 0.41 |
| EEG-alone state changes / h (≥ 5) | 33.5 | 109.5 |
| κ rule vs HMM | 0.89 | 0.46 |
| κ NREM, rule vs EEG alone | 0.86 | -0.07 |
| κ rule, gap vs 20–90 Hz EMG | 0.85 | 0.76 |
| artifact epochs % | 0.0 | 0.8 |
| EEG 60 Hz, median µV | 46 | 95 |
| EMG 60 Hz, median µV | 41 | 491 |
| wake % light (rule) | 23.4 | – |
| wake % dark (rule) | 72.4 | – |
| NREM % light, EEG alone | 59.9 | – |
| NREM % dark, EEG alone | 20.4 | – |
| sleep % light, EMG alone | 76.0 | 85.9 |
| sleep % dark, EMG alone | 27.3 | 49.5 |
| r@1min (project definition) | 0.768 | – |
| old verdict reason | rung 2 CONNECTION: chip floor is 66 uV of 60 Hz (grounded chips show >800) -- no verdict can be drawn | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsl21-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Very plausible. Bright delta bands alternate with theta/wake all day; wake 23% in light vs 72% in dark; EMG shows a low steady sleep floor (about 8-12 uV) and high bursty wake, strongest wake consolidation in the dark, a sleepy phase through ZT0-12 and again ZT20-22. Rule, HMM and EEG-only hypnograms agree closely (kappa rule-HMM 0.89).
Concerns: The only dropped hour (about ZT18-19) looks like an almost all-wake hour where the EEG delta test has nothing to compare (NR vs W AUC undefined), so it is probably dropped wrongly; keep it if the EMG test passes. The old verdict NO VERDICT came from a 66 uV chip-floor rule, not from signal quality, so this mouse was wrongly left unjudged. Rule vs HMM disagreement is mostly the REM/NR boundary (HMM calls more R in atonic low-delta stretches); rule NR vs HMM R at epochs 4483 looks like the rule missing real REM.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 563 | NR | medium | rule | EMG flat at 0.27x cut after a wake bout, delta 3.35 near the NR median (3.46), sigma 2.70 up, no regular theta (rule and HMM both NR). |
| 2 | 1306 | NR | low | rule | EMG is bursty and about 0.8x cut so not atonic (HMM R impossible); theta/delta only 0.33, delta 3.18; could be quiet wake or light NREM, no spindles seen. |
| 3 | 2140 | R | high | rule | Atonic EMG 0.43x with heartbeat spikes only, regular 6-7 Hz theta, theta/delta 1.78, delta 2.88 below NR median, sigma dropped (rule and HMM both R). |
| 4 | 4079 | uncertain | low | neither | Atonic EMG (0.22x) but theta/delta only 0.76, delta 3.07, sigma 2.40; ambiguous between late NR and REM onset, sits just before a wake burst. |
| 5 | 4483 | R | medium | hmm | Atonic EMG 0.38x, regular 7 Hz theta visible, theta/delta 1.88, delta 2.95 well below NR median; the rule's NR looks like a miss. |
| 6 | 8065 | uncertain | low | neither | Atonic EMG, sigma dropped (2.36), but theta/delta 0.43 and delta 3.13 not clearly low; flanked by clear R epochs, probably the REM edge but theta is not dominant. |
| 7 | 11204 | W | medium | rule | EMG 1.19x cut with continuous muscle activity through most of the epoch after a burst at its start, delta 3.10 reduced; lights-off onset in a wake bout, HMM NR ignores the muscle. |
| 8 | 13242 | NR | low | rule | EMG 0.61x cut is not atonic at this dark-phase floor, theta/delta 0.98 and delta 3.32 near NR median; not REM, but could be quiet wake. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL21_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The tier depends on the EMG preprocessing. With the ss60 EMG, eta is 0.63, below the 0.70 bar, and the tier falls to C. Gap vs ss60 kappa is the lowest of these recordings (0.85). The sleep EMG floor is largely heartbeat (ECG spikes visible in the epoch panels) and varies 0.2-0.6x the cut within minutes. Rule-NR EMG reaches 0.56x (median) and 0.75x (p90) in the dark, so the W/NR boundary leans on the gap filter that removes those spikes. Checked: I read the overview, the epochs image, score.json and blocks_1h.csv, and recomputed stats per hour and per phase. The EEG is excellent: delta AUC 0.92 light and 0.95 dark, per-hour 0.86-0.99, NR minus W delta 0.43-0.61 log, rule vs EEG-only kappa 0.87, rule-HMM 0.89. EEG 60 Hz is flat at about 45 uV with no step. Wake is 23.4 % light vs 72.4 % dark. The one dropped hour (ZT18) is 86 % wake. The contested epochs I inspected are mostly ECG-floor NR/R that the HMM calls R, which is defensible either way. Old NO VERDICT was the chip-ground gate, not the signal.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsl21-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG partial; rule follows the EEG: no; tier disputed → D.
Plausibility: EEG has no sleep structure: log10 delta stays about 0.4 to 0.6 for 24 h (other mice 2.5 to 3.8), there is a fixed 20 Hz stripe in the spectrogram, and AUC delta NR vs W is 0.37, so it is below chance. The EMG gap RMS does show a day-night pattern, with a steady floor near 65 to 70 uV and bursty plateaus that become denser after ZT12. That is the only usable axis. Rule NR/R labels follow noise, and kappa between the rule's NREM and the EEG-only HMM is -0.07.
Concerns: Tier C (EEG only) is wrong because the EEG is not neural. The 'eeg_alone_ok' pass looks like a criterion artefact: 24 h EEG-alone usable despite AUC 0.37 and NR delta at the noise floor. Raw EMG 60 Hz is 491 uV and EEG 60 Hz is 95 uV, so this animal is badly contaminated. EMG-only wake/sleep (Otsu) is the only defensible output, which is tier D (more wake in dark by 36 points). Treat even that with caution: the EMG floor is near the cut (about 0.75x) and the sleep-side trace in the contested panels is a regular, constant-amplitude oscillation, which looks technical. NR vs R must not be reported. The rule's 1.4 % wake and 91 % NR in the light is not believable as sleep staging. Whether this is a real animal signal or an artefact of a bad connection cannot be settled from these images.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 4072 | uncertain | low | neither | EEG is a near-flat trace, so there is no delta or theta to read. EMG is a constant-amplitude oscillation at 0.74x the cut, which is probably a technical floor. Asleep by EMG, but NR vs R is undecidable. |
| 2 | 4114 | uncertain | low | neither | EEG flat and EMG constant at 0.74x the cut. The theta/delta of 1.8 and delta of 0.22 come from noise, not from visible theta. |
| 3 | 4167 | uncertain | low | neither | No visible EEG rhythm and no EMG burst. A theta/delta of 3.5 on a flat trace is not evidence of REM. |
| 4 | 6310 | uncertain | low | neither | EEG flat, EMG regular and constant at 0.76x the cut. Rule and HMM split NR/R on noise features. |
| 5 | 6461 | uncertain | low | neither | EEG shows only a slow drift, with no waves. EMG is a flat plateau at 0.73x the cut. NR vs R cannot be told. |
| 6 | 7030 | uncertain | low | neither | EEG flat, EMG constant at 0.77x the cut, so the label rests only on noise-level delta and theta/delta. |
| 7 | 7056 | uncertain | low | neither | No EEG signal to separate NR from R. The rule flips R, NR, R across neighbours with identical EMG, which is a sign of noise-driven labels. |
| 8 | 7176 | uncertain | low | neither | Rule and HMM both say R, but the EEG is flat and the EMG is not atonic beyond its usual 0.75x floor. There is no theta to see. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL21_R_epochs.png`.

**Skeptic (tried to refute the rescue):** not usable, tier X. Strongest objection: The EEG carries no neural signal. Its NR power spectrum is flat white noise at about 1 uV^2/Hz from 2 to 45 Hz (0.73 at 2 Hz vs 720 to 900 in the good mice), and log10 delta is about 0.4 vs 3.0 to 3.5 elsewhere. Delta is positively correlated with EMG (1-min rho +0.33), which is movement artefact, the opposite of physiology. AUC is 0.37 and NREM kappa vs EEG-only is -0.07. Tier C is a criterion bug: score.py checks eeg_alone_ok (HMM d' 1.69) independently of eeg_recording_ok, which is False here. The EMG does not justify D either. 92 % of the sleep-floor EMG power is 20 Hz comb interference (400 Hz at 3280x the band median, plus 280, 460 and 160 Hz, none notched). The floor sits at a constant 58 to 75 uV in every hour, 0.75x the cut, and the epoch traces show it as a regular constant-amplitude oscillation. Quiet wake cannot be seen under that floor: EMG-only sleep is 86 % in the light, which is not believable. The bursts are denser in the dark (hourly p90 65 to 108 in the light vs 112 to 138 uV in the dark), so at most a crude activity index is left, not sleep. Checked: Brief; overview (fixed 20 Hz stripe, flat delta trace) and epochs PNG (flat EEG, periodic EMG floor); score.json (eeg_recording_ok false, but tier C); blocks_1h.csv (AUC 0.25 to 0.47 in every hour); score.py tier logic. From the parquets: medians by stage (EMG NR 64 / W 97 uV, only 1.5x); hourly p10 and p90; 1-min delta-EMG rho +0.33. From psd_emg.npy: non-60 Hz spectral lines and comb share 0.92 NR vs 0.42 W. From psd_eeg.npy: flat EEG spectrum in all states. The previous reviewer's D is too generous for the same reasons.


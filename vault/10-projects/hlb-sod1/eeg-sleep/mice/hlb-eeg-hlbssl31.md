---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSL31: EEG re-score 2026-11, baseline tier D, recovery tier A"
tags: [eeg, hlb, mouse, hlbssl]
---

# HLBSSL31: S-SL (SOD1, ad libitum), rig A1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline SCOREABLE, recovery NO VERDICT.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | D | A |
| hours usable, EEG + EMG | 22 | 24 |
| … of them light | 12 | 12 |
| … of them dark | 10 | 12 |
| hours usable, EEG alone | 22 | 24 |
| hours usable, EMG alone | 24 | 24 |
| EMG separability η (gap; ≥ 0.70) | 0.889 | 0.856 |
| η, SleepStager 20–90 Hz EMG | 0.828 | 0.790 |
| δ AUC, NR vs W (≥ 0.75) | 0.693 | 0.940 |
| EEG median log10 δ (2–4) | 3.10 | 3.24 |
| EEG-alone state changes / h (≥ 5) | 0.1 | 33.0 |
| κ rule vs HMM | 0.37 | 0.85 |
| κ NREM, rule vs EEG alone | -0.23 | 0.87 |
| κ rule, gap vs 20–90 Hz EMG | 0.92 | 0.93 |
| artifact epochs % | 0.0 | 0.0 |
| EEG 60 Hz, median µV | 70 | 8 |
| EMG 60 Hz, median µV | 17 | 4 |
| wake % light (rule) | 30.7 | 32.6 |
| wake % dark (rule) | 49.6 | 63.7 |
| NREM % light, EEG alone | – | 51.5 |
| NREM % dark, EEG alone | – | 31.5 |
| sleep % light, EMG alone | 68.0 | 67.0 |
| sleep % dark, EMG alone | 47.4 | 36.2 |
| r@1min (project definition) | 0.776 | 0.769 |
| old verdict reason | 23.98 h in 2 block(s), r@1min 0.532 | rung 2 CONNECTION: chip floor is carrying signal: its slope threshold is -2.35 (valid floors are flatter than -1.90) -- no verdict can be drawn |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssl31-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG good; rule follows the EEG: mostly; tier disputed → B.
Plausibility: Light: clear NR/W alternation with brighter delta in NR and delta down / theta-over-delta up in the REM-like stretches. Dark: long EMG plateaus (ZT12-17, ZT17-19.5) with low delta and higher theta/delta, which fits sustained active-phase wake. Then ZT19.6-24 is low-EMG sleep. Overall plausible.
Concerns: EEG amplitude fades steadily from about hour 20 (log10 delta falls from ~3.5 to ~2.4, >10 Hz goes black). That is a gradual technical drift, not physiology, so NR vs R is unknowable in the last ~4 h. It also breaks the EEG-only 2-state HMM, which fits the drift (NR for 0-20.5 h, 'not NR' after), hence kappa -0.23. EEG-only is not a valid check here. The rule badly under-calls REM (15 onsets, ~0.2 %) although hours 0-8 show many delta-down / theta/delta-up episodes, and the REM-like epoch 2471 is unambiguous. HMM R calls in light are often right. The screen drops dark hours 12-16 probably because they are nearly all wake and the delta AUC is undefined, not because they are bad. I would keep light 12 h plus the credible dark wake hours 12-20 and drop only the faded tail, which argues for B rather than C. Old pipeline called it SCOREABLE; EMG is good.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 271 | R | medium | hmm | Tail of a REM bout (previous epochs theta/delta 2.1 and 1.6), delta 2.89 still below the NR median 3.27, EMG flat at 0.23x cut; fading theta alone does not end REM. |
| 2 | 535 | uncertain | low | neither | Delta 3.16 near NR level, theta/delta 0.75 intermediate, irregular trace with no clear regular 6-9 Hz and no spindles; EMG atonic. Could be NR or REM onset. |
| 3 | 2471 | R | high | rule | Regular 6-9 Hz theta, theta/delta 2.95, delta 2.61 well below NR median, flat EMG at 0.19x cut; the HMM agrees. |
| 4 | 2975 | NR | medium | rule | Delta 3.52 above the NR median with large irregular slow waves, theta/delta 0.69 only a transient rise, EMG at sleep floor. |
| 5 | 5580 | W | high | rule | EMG bursts fill most of the epoch (2.2x cut), delta low; both scorers agree. |
| 6 | 15777 | NR | medium | rule | Delta 3.41 above NR median, slow waves visible, theta/delta 0.28, EMG 0.28x cut with only small heartbeat-like spikes; no theta. |
| 7 | 16164 | NR | medium | rule | Delta 3.39, theta/delta 0.35, irregular slow EEG; EMG tone 0.39x is slightly raised versus the light period but below the cut and without bursts. |
| 8 | 18012 | NR | high | rule | Large slow waves, delta 3.54 above NR median, theta/delta 0.13, EMG at floor; no theta rhythm, HMM R is not supported. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL31_B_epochs.png`.

**Skeptic (tried to refute the rescue):** partially usable, tier D. Strongest objection: Tier C (NREM from the EEG alone) is refuted. The EEG-only HMM calls 100 % NREM in every hour from ZT0 to 19, including ZT13-15, which are 98-100 % wake by EMG and where log10 delta stays at wake level (3.03 against an NR median of 3.4). It split on the EEG amplitude fade after ZT20 (eeg_rms 87 -> 60 uV, log10 delta 3.4 -> 2.45, ZT20-24), not on sleep. The same fade breaks the rule's REM detection for the whole recording: veto_cut ln(delta) = 6.10 sits below the 5th percentile of light-phase sleep delta (6.54), so only 1.5 % of light sleep epochs can pass the 'delta low' test, which is why REM is 0.2 %. The HMM is broken the other way: it calls 94 % of light sleep R, because its 'NR' state is the faded tail. So no NR-vs-R output from this recording can be trusted as delivered. What does hold is W vs sleep from the EMG for ZT0-20. The EMG is bursty with a low floor (eta 0.89). The EEG confirms the W/NR contrast hour by hour (AUC 0.72-0.96, only 4.6 % of W epochs reach NR-level delta). The 4.8 h dark wake plateau has continuous 6-10 Hz theta with no NR delta, so it is credible active wake, not a technical plateau. ZT20.5-24 cannot be staged beyond W vs sleep (rule says 93 % sleep in the late dark, with EEG contrast gone, AUC 0.50-0.61). If the rule is re-run on ZT0-20.5 with the tail excluded, the recording could reach tier B (12 h light plus about 7 h dark, counting the all-wake ZT13-15). It is not B as scored. Pairing note: this baseline cannot be paired with HLBSSL31_R for NR or REM measures. Checked: score.json (veto_cut 6.10 below med_logdelta_W 6.96; kappa NR rule vs EEG-only -0.23; nrem_pct_light_eeg_only 100), blocks_1h.csv (eeg_alone_ok True for all 24 h despite nrem_eeg 1.0 in all-wake hours), overview PNG (fade after ZT20, dark theta band), per-hour features (log10 delta in NR vs W, eeg_rms, EMG floor, EMG CV), percentiles of light-phase sleep delta against the veto cut, HMM R fraction per segment, EMG vs 60 Hz correlation (sleep r -0.50, so mains is not driving the split)

## Recovery

![[2026-11-03-hlb-eeg-hlbssl31-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible. 24 h ad lib recovery from ZT0: wake 32.6 % in the light vs 63.7 % in the dark, NREM bouts follow bright delta bands, EMG shows a low steady sleep floor and a bursty wake level (eta 0.86, AUC 0.94). Rule, HMM and EEG-only hypnograms agree closely (kappa rule-HMM 0.85, NR rule vs EEG-only 0.87).
Concerns: None serious. All 24 h kept, and I see no hour that should have been dropped. The old pipeline gave NO VERDICT only because of a floor-slope condition, so there is no sign it was wrongly rejected for signal reasons. Remaining disagreements are the usual NR vs R borderline epochs, several of them immediately after a wake bout, where the HMM says R but sigma is still high.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 2663 | NR | low | rule | First sleep epoch right after a wake bout ended about 2 s earlier, EMG 0.37x flat, delta 3.29 below NR median, theta/delta only 0.53 and sigma 2.41; no regular theta, and REM is not entered from wake. |
| 2 | 5190 | uncertain | low | neither | One epoch with theta/delta 1.10 and delta 2.99 inside NR neighbours (theta/delta 0.3-0.7), EMG 0.44x flat; EEG mixed slow plus fast, a lone R epoch needs more than this. |
| 3 | 6066 | W | low | hmm | EMG 0.89x with continuous raised activity and a burst at the end, neighbours 0.85-1.0x cut; low-amplitude fast EEG (delta 2.91, theta/delta 1.5), looks like quiet wake inside a wake bout. |
| 4 | 6658 | NR | medium | rule | EMG 0.57x with only one brief twitch, sigma 3.03 is the highest of the row (spindles), theta/delta 0.72, delta 3.28 near NR level. |
| 5 | 7521 | W | medium | rule | Quiet wake in the middle of a wake bout: repeated EMG bursts at 0.7 s and 2 s inside the epoch, neighbours 3-5x cut, EEG delta below NR level and no spindles. |
| 6 | 8132 | R | high | rule | EMG flat at 0.28x for the whole row, regular theta-looking EEG, theta/delta 0.98 with 1.2-1.7 in the neighbours, sigma low; rule and HMM agree. |
| 7 | 9053 | NR | medium | rule | EMG 0.46x flat, theta/delta only 0.43, delta 3.37 close to NR median and sigma 2.92 high (spindles); HMM R is driven by the neighbouring higher theta/delta epochs. |
| 8 | 18834 | NR | low | rule | First quiet epochs after a wake burst ended about 4.5 s before the previous epoch; theta/delta 1.14 but delta 3.04 and sigma 2.76 have not dropped enough, and REM is not entered directly from wake. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSL31_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: This is the only recording where 60 Hz amplitude rises with wake (AUC 0.91, r 0.78), which raises the question of whether mains leaks into the wake calls. That is unlikely: raw mains is only 3-5 uV against a gap-EMG cut of 15.4 uV, and the notched EMG has a 0.2-0.3x floor with 2.4-3.8x bursts. The EEG confirms independently (delta AUC 0.94, NR rule vs EEG-only kappa 0.87, 0.5 % of W epochs at NR delta), so the rise is more likely movement-related pickup. Also, ZT0 is 73 % wake at lights-on (possibly handling), and no hour shows a recovery-like rebound. Do not read this window as 'recovery' physiology without checking what preceded it. Its paired baseline (HLBSSL31_B) is not valid for NR/REM, so any paired analysis for this mouse is limited to wake vs sleep. Checked: score.json, blocks_1h.csv, overview PNG, meta.json (window ZT0-24 on 09-21, partner baseline), per-hour W/NR/R, delta, EMG floor, 60 Hz correlation and AUC, W epochs with NR delta


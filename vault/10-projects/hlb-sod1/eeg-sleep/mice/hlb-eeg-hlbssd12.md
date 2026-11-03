---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBSSD12: EEG re-score 2026-11, baseline tier B, recovery tier X"
tags: [eeg, hlb, mouse, hlbssd]
---

# HLBSSD12: S-SD (SOD1, sleep deprivation), rig A2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **B** → W / NR / R on the usable hours. review: A -> B: exactly 20 h; dark ZT18-24 EEG railed, ZT23 kept only by the all-wake exemption (skeptic + critic)
> - **Recovery:** tier **X** → nothing. review: C -> X: C rests on exactly 6 light hours incl. ZT6/8/9 with flat 400-500 uV EMG plateaus and a 16-20 Hz technical band (skeptic)
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | C |
| hours usable, EEG + EMG | 20 | 8 |
| … of them light | 12 | 3 |
| … of them dark | 8 | 5 |
| hours usable, EEG alone | 20 | 17 |
| hours usable, EMG alone | 24 | 10 |
| EMG separability η (gap; ≥ 0.70) | 0.811 | 0.818 |
| η, SleepStager 20–90 Hz EMG | 0.758 | 0.767 |
| δ AUC, NR vs W (≥ 0.75) | 0.920 | 0.919 |
| EEG median log10 δ (2–4) | 3.27 | 3.21 |
| EEG-alone state changes / h (≥ 5) | 32.7 | 41.3 |
| κ rule vs HMM | 0.84 | 0.84 |
| κ NREM, rule vs EEG alone | 0.82 | 0.76 |
| κ rule, gap vs 20–90 Hz EMG | 0.88 | 0.87 |
| artifact epochs % | 18.7 | 59.5 |
| EEG 60 Hz, median µV | 119 | 152 |
| EMG 60 Hz, median µV | 568 | 1187 |
| wake % light (rule) | 27.9 | 18.8 |
| wake % dark (rule) | 80.5 | 51.6 |
| NREM % light, EEG alone | 55.8 | 44.7 |
| NREM % dark, EEG alone | 15.9 | 36.9 |
| sleep % light, EMG alone | 72.2 | 66.1 |
| sleep % dark, EMG alone | 30.5 | 47.8 |
| r@1min (project definition) | 0.223 | -0.022 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.7% usable, longest unbroken block 1.2 min | rung 2 CONNECTION FAIL: 0.3% usable, longest unbroken block 1.7 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbssd12-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG good; rule follows the EEG: mostly; tier agreed.
Plausibility: Plausible. Light is mostly sleep (about 28% wake) and the dark is wake dominated (80%, a little high), with a few consolidated dark sleep bouts. EMG has a clean low floor in the light and a higher, noisier floor in the dark.
Concerns: EEG amplitude is low throughout (delta range narrow), and the dark has almost no delta structure. Hours 19-23 are broadband railed or clipped EEG and correctly dropped, so the dark has only 8 usable hours (tier A is borderline at 20 h). The dark EMG floor (about 80-100 uV) sits close to the cut (45), so quiet-wake versus NR calls in the dark depend on EEG. Dark NR (18%) should be treated with caution.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1473 | W | low | hmm | Repeated EMG bursts around the epoch (the burst in it lasts about 1.2 s) with low-amplitude desynchronised EEG, delta well under NR level (3.02 vs 3.65) and no spindles. This is wake with fidgeting, not NREM with a microarousal. |
| 2 | 4115 | W | medium | rule | Inside a run of EMG bursts with only a short lull, delta at wake level (3.02) and no spindles. Quiet wake in a bout. |
| 3 | 5667 | R | low | hmm | EMG flat with no bursts, delta low (3.0 vs 3.65) and theta/delta raised for several epochs after NREM. The EEG is low amplitude, so the theta is weak and the call is soft. |
| 4 | 9225 | W | low | neither | Right after a long burst bout, with a burst in the next epoch. Tone is quiet (0.5x) but delta is at wake level and there are no spindles or slow waves, so quiet wake. Not NR (no slow waves) and not R (REM does not follow wake directly). |
| 5 | 11483 | W | high | rule | Rhythmic EMG bursts (chewing or grooming) through the epoch and its neighbours, tone about 0.8-1.0x, no NREM EEG. |
| 6 | 13311 | NR | medium | rule | Only brief twitch bursts of about 1 s on an otherwise flat EMG, with NREM EEG (delta 3.35, large slow waves in the previous epoch). Twitches in NREM, not wake. |
| 7 | 13357 | NR | low | rule | EMG is flat after a wake bout and the next epochs have clear slow waves (delta 3.4). Theta/delta is not dominant, so this is NREM entry rather than REM. |
| 8 | 21082 | W | high | rule | EMG is high for the whole epoch (about 2x cut) and the EEG is railed or clipped. This is gross movement, so the HMM's NR is an artefact. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD12_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier B. Strongest objection: Tier A rests on exactly 20 h, and two of the dark hours are kept by a circular test. From about ZT18.7 to ZT24 the EEG spectrogram is saturated broadband (railing or clipping). ZT23 (EMG floor 0.44 log above the cut) and ZT18 (+0.06) fail the EMG floor test. They are rescued only by the 'all wake' exception, which uses the EEG-only HMM reading <10% NREM from that broken EEG (ZT23 has only 522 unflagged epochs). If ZT23 is dropped the window has 19 h and A fails. The ss60 sensitivity run already gives B. With 12 light hours and 6-7 sound dark hours, B holds. The dark EMG steps up from about 25 to about 100 uV at lights-off. This is physiological, not a technical step: delta drops at the same moment, dark sleep bouts show matching EMG dips and delta rises, and 1-min delta-EMG r = -0.56. Checked: score.json (tier_gap A, tier_ss60 B, hours both ok 20 = 12 L + 8 D, eeg artifact 28% of dark); blocks_1h (ZT18 floor_rel +0.06, ZT23 +0.44, both kept via nrem_eeg < 0.10); overview.png (EEG broadband from ~ZT18.7); hourly EEG RMS/delta; delta-EMG r -0.56/-0.53; AUC 0.92 (gap) / 0.88 (ss60); EMG NR 23 vs W 90 uV.

## Recovery

![[2026-11-03-hlb-eeg-hlbssd12-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG partial; rule follows the EEG: mostly; tier agreed.
Plausibility: Dark wake 52% vs light 19% fits the day pattern. The first 6 h of the recovery are mostly scored W, which is unlikely right after SD, and they coincide with technical EMG plateaus.
Concerns: EMG has flat plateaus at about 400-500 uV with no bursts (hours about 1.8-3, 3.7-6, 9-10) that are technical, not muscle; the rule turns them into long W blocks. In the same hours the EEG is dull with low delta, which looks like poor contact rather than wake. Good stretches (hours 0-1, 6-7, 9-11, 16-19) are the kept ones. Tier C is right: 8 usable hours with both channels (3 light, 5 dark) does not meet B. Hours dropped are fair; the red hours around 1.8-6 should not be quoted for wake time.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 450 | NR | high | rule | Large slow waves, delta above NR median, EMG at floor with only tiny spikes. |
| 2 | 2907 | R | medium | hmm | Short EMG burst in the first second only (< half), then atonic; delta low, theta/delta 1.26, flat low-amplitude EEG; likely a twitch/arousal inside REM. |
| 3 | 2983 | NR | low | rule | Delta near NR median and theta/delta 0.44, EMG at floor; EEG low amplitude so little to see by eye. |
| 4 | 8255 | W | medium | rule | EMG bursts cover about 70% of the epoch and the bout is W on both sides; EEG shows a movement artefact (delta 5.1). |
| 5 | 9409 | R | medium | hmm | Atonic EMG (0.33x) after twitches, delta below NR median, theta/delta 1.16 with regular theta visible, following epochs also theta-rich. |
| 6 | 9787 | W | low | rule | Quiet gap between two heavy EMG bursts (tone 0.53x) inside a wake bout; no slow waves. Could be a brief rest, but a lone sleep epoch needs more evidence. |
| 7 | 9790 | NR | low | rule | Two epochs after a wake burst, EMG quiet (0.51x), theta/delta 0.7 only; REM cannot follow wake directly. |
| 8 | 16605 | NR | low | rule | EMG at floor with small spikes, theta/delta 1.7 but a wake burst 1.5 epochs earlier and NR after; a lone R epoch needs a reason. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBSSD12_R_epochs.png`.

**Skeptic (tried to refute the rescue):** partially usable, tier X. Strongest objection: The C light-hour count (exactly 6, the minimum) includes technical hours. At ZT6 and ZT9 (also ZT8) the EMG sits on flat 400-500 uV plateaus with no bursts, and the EEG shows a constant 16-20 Hz band with collapsed delta. The hourly median EEG RMS there is about 2360 uV, against about 120 uV in good hours, yet those epochs were not flagged as artifact because a third of the recording is like this and the median/MAD threshold rises with them. The EEG-only HMM labels those hours 'not NREM' and counts them as light wake, which is why EEG-only light NREM is only 44.7% in a post-SD light phase. Without ZT6 and ZT9 the light phase has 4 EEG hours and C fails. The EEG-only NREM call also absorbs 15-17% of EMG-wake epochs, and 70% of the top-5% delta epochs are EMG-wake (movement artifact). Only about 8 both-ok hours (3 L / 5 D, AUC 0.85-0.97) are trustworthy. They can be used as hour-level descriptive data, but not as a light/dark tier. Checked: score.json (artifact 59.5%, EEG artifact 34.8%, hours both ok 3L/5D, EEG-alone 6L/11D); blocks_1h (EMG clean epochs 0, 25 and 103 at ZT6, 8 and 9); overview.png (16-20 Hz band and flat EMG plateaus at hours ~1.8-2.7 and ~3.7-6; EEG-only marks them red); hourly EEG RMS/beta fraction/delta; P(EEG-only NR | EMG W) 0.15-0.17; top-delta EMG state.


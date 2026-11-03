---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSD04: EEG re-score 2026-11, baseline tier C, recovery tier D"
tags: [eeg, hlb, mouse, hlbwsd]
---

# HLBWSD04: W-SD (water, sleep deprivation), rig B2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **C** → NREM from the EEG alone. screen
> - **Recovery:** tier **D** → sleep vs wake from the EMG alone. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | C | D |
| hours usable, EEG + EMG | 24 | 0 |
| … of them light | 12 | 0 |
| … of them dark | 12 | 0 |
| hours usable, EEG alone | 24 | 0 |
| hours usable, EMG alone | 24 | 20 |
| EMG separability η (gap; ≥ 0.70) | 0.686 | 0.742 |
| η, SleepStager 20–90 Hz EMG | 0.623 | 0.653 |
| δ AUC, NR vs W (≥ 0.75) | 0.916 | – |
| EEG median log10 δ (2–4) | 3.23 | – |
| EEG-alone state changes / h (≥ 5) | 30.9 | – |
| κ rule vs HMM | 0.41 | – |
| κ NREM, rule vs EEG alone | 0.74 | – |
| κ rule, gap vs 20–90 Hz EMG | 0.86 | – |
| artifact epochs % | 5.6 | 100.0 |
| EEG 60 Hz, median µV | 83 | 5429 |
| EMG 60 Hz, median µV | 534 | 955 |
| wake % light (rule) | 40.7 | – |
| wake % dark (rule) | 64.2 | – |
| NREM % light, EEG alone | 41.5 | – |
| NREM % dark, EEG alone | 22.7 | – |
| sleep % light, EMG alone | 62.7 | 64.5 |
| sleep % dark, EMG alone | 41.0 | 47.8 |
| r@1min (project definition) | 0.162 | – |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsd04-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG partial; rule follows the EEG: mostly; tier agreed.
Plausibility: EEG side is plausible: delta bands alternating with wake all day, more wake in the dark (EEG-only NREM 42% light vs 23% dark). EMG side is not clean: the sleep floor sits at ~25-40 uV, right at the wake cut (35.7), with a constant ripple and high mains in the EMG (534 uV at 60 Hz); eta 0.69 below the 0.70 bar.
Concerns: Tier C (EEG only) is right, and the old CONNECTION FAIL rejection was wrong for the EEG: sleep/wake can be scored from the EEG. Because the EMG floor is near the cut, the rule's W/NR calls are partly decided by noise: rule vs EEG-only NREM agreement is only moderate (kappa 0.74), and HMM paints R in many places where EMG is not atonic (kappa rule-HMM 0.41). REM calls here depend on theta alone and are weak. Use EEG-based NREM vs not-NREM only.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 4149 | NR | high | rule | Large slow waves, delta 3.60 at NR median (3.65); the EMG is a constant low ripple at 0.75x cut with no bursts (floor of this mouse), not wake. |
| 2 | 5106 | W | medium | rule | EMG continuous at 1.4x cut like the surrounding wake epochs, not atonic, EEG low-amplitude fast; HMM R is excluded by the lack of atonia (quiet wake). |
| 3 | 11201 | R | medium | rule | Tone 0.73x cut with only phasic twitch bursts, delta low (3.09 vs 3.65), regular theta visible, theta/delta 1.24; rule and HMM both R. |
| 4 | 14398 | W | medium | rule | Large EMG bursts through most of the epoch (1.54x cut, tone 1.3x), not atonic; theta/delta 1.05 is waking theta; HMM R rejected. |
| 5 | 15603 | W | low | rule | Phasic bursts across roughly half the epoch, tone 1.08x just above cut, between epochs of clear wake; quiet wake inside a wake bout, but near the EMG noise floor. |
| 6 | 18554 | R | medium | rule | EMG flat at 0.45x cut with no bursts, regular theta in the EEG, delta 3.01 low, theta/delta 1.65, and R continues in the next epochs; HMM W unjustified. |
| 7 | 19852 | W | high | rule | Follows a full wake epoch, EMG bursts across most of the epoch (1.6x cut, tone 1.4x), no atonia; HMM R rejected. |
| 8 | 21222 | W | medium | rule | EMG burst for the first ~2.5 s (>half), tone 1.26x cut, in a wake stretch; theta/delta 0.83 low. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD04_B_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier C. Strongest objection: The EMG cannot be trusted for W/NR. Eta is 0.686, raw 60 Hz is 534 uV, and in ZT0-6 the sleep floor sits at about 0.7x the cut (25 vs 35.7 uV), then drifts down to about 0.4x. 41 % of light W epochs sit under 1.3x the cut, and median NR bouts are only 5 epochs. Rule-only NR epochs (23-32 %) have wake-level delta and sigma. So only EEG-based NREM vs not-NREM holds. The EEG-only HMM is conservative (NREM 32 % vs rule 45 %), so absolute NREM % is threshold-bound. Use it for relative comparisons; no REM. Checked: I read the overview, score.json and blocks_1h.csv, and computed per-hour EMG p10/p50/p90 relative to the cut, AUC by phase, and rule-only vs EEG-agreed NR delta, theta/delta, sigma and EMG. The EEG is real: delta bands alternate all day, AUC is 0.92 light and 0.90 dark, NR minus W delta is 0.46-0.57 log, and per-hour delta-EMG correlation is -0.5 to -0.7 in mixed hours. EEG-only NREM is 41.5 % light vs 22.7 % dark, so the phase pattern is right. There is no step change; one broadband transient near ZT7. The old CONNECTION FAIL was wrong for the EEG.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsd04-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG partial; rule follows the EEG: not applicable; tier agreed.
Plausibility: EMG-only sleep ~65% light vs ~48% dark: direction right, but the light-dark difference (+16.7 pts wake) is about half that of the good EMG mice. Marginal.
Concerns: EEG: ~5.4 mV of mains, 100% artefact, no delta pattern; unusable. EMG shows a sleep floor and bursts up to ~500 uV, so it carries some behaviour, but the floor is high (~35-40 uV vs 5-10 in other mice), eta is only 0.742, the Otsu cut was not computed (emg_cut null), and the mains-contaminated variant (ss60) gives X. D is defensible but weak: treat as EMG-only sleep/wake with low confidence, no R/NR. No contested epochs drawn.


---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSD03: EEG re-score 2026-11, baseline tier X, recovery tier X"
tags: [eeg, hlb, mouse, hlbwsd]
---

# HLBWSD03: W-SD (water, sleep deprivation), rig C1

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **X** → nothing. screen
> - **Recovery:** tier **X** → nothing. screen
> - **Paired W/NR/R (both windows A or B):** no.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | X | X |
| hours usable, EEG + EMG | 18 | 0 |
| … of them light | 11 | 0 |
| … of them dark | 7 | 0 |
| hours usable, EEG alone | 18 | 0 |
| hours usable, EMG alone | 24 | 0 |
| EMG separability η (gap; ≥ 0.70) | 0.856 | – |
| η, SleepStager 20–90 Hz EMG | 0.870 | – |
| δ AUC, NR vs W (≥ 0.75) | 0.468 | – |
| EEG median log10 δ (2–4) | 2.99 | – |
| EEG-alone state changes / h (≥ 5) | 0.4 | – |
| κ rule vs HMM | 0.41 | – |
| κ NREM, rule vs EEG alone | -0.37 | – |
| κ rule, gap vs 20–90 Hz EMG | 0.93 | – |
| artifact epochs % | 0.0 | 100.0 |
| EEG 60 Hz, median µV | 110 | 5170 |
| EMG 60 Hz, median µV | 35 | 4568 |
| wake % light (rule) | 65.1 | – |
| wake % dark (rule) | 25.9 | – |
| NREM % light, EEG alone | – | – |
| NREM % dark, EEG alone | – | – |
| sleep % light, EMG alone | 35.8 | – |
| sleep % dark, EMG alone | 73.5 | – |
| r@1min (project definition) | 0.721 | – |
| old verdict reason | rung 3 SCOREABILITY FAIL: 23.99 h in 7 block(s), r@1min 0.411 | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsd03-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG partial; rule follows the EEG: no; tier disputed → X.
Plausibility: Not plausible as a whole. The first ~7 h look like real sleep/wake (delta bands vs EMG), but from ~ZT7 delta is flat around 3.0 while EMG alternates, and from ~ZT16 the EEG collapses to a flat, low-power trace (delta ~2.3, no fast power) while the EMG goes low with sparse huge spikes. Light-dark pattern is inverted (wake 48% light, 43% dark; EMG-only wake dark minus light -38).
Concerns: Tier C (EEG-only OK all 24 h) is wrong: AUC delta NR vs W is 0.47 and 'EEG usable 24 h' counts the dead last 8 h. Rule NR from ZT16 to the end follows the EMG floor of a dead channel, not sleep; HMM/EEG-only NR there is the same artefact. EMG after ~ZT19 (low floor plus periodic huge spikes) looks technical. I would keep, at most, the first ~7 h (and ZT12-16 with caution) for a partial analysis; the recording does not support a 24 h tier. Old NOT SCOREABLE is closer to the truth than tier C.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 836 | NR | high | rule | EMG flat 0.35x cut, large slow waves with a sharp transient, delta 3.65 far above this mouse's NR median 2.82; HMM R unjustified. |
| 2 | 2137 | NR | high | rule | Atonic EMG (0.18x) but delta 3.50 high with big slow waves and low theta/delta 0.38: NREM, not REM. |
| 3 | 5122 | W | medium | rule | EMG burst starts ~2.3 s and continues into the next epoch (mean 5.6x cut), EEG low-amplitude fast, delta 3.07; wake-bout onset, burst a bit under half the epoch hence medium. |
| 4 | 5772 | W | high | rule | EMG burst from ~1.4 s to beyond the epoch end (>half, 7.4x cut), EEG desynchronised. |
| 5 | 9694 | W | high | rule | Bursty EMG through the whole epoch (3.15x cut, tone 3.1x), delta low 2.65; theta/delta 1.43 is waking theta, not REM (no atonia). |
| 6 | 10188 | NR | medium | rule | Single ~1.2 s EMG burst (<half), tone 0.70x cut, delta 3.39 above NR median; microarousal in NREM (caveat: EEG in this hour is poorly discriminating). |
| 7 | 10335 | uncertain | low | neither | EMG low with only small phasic twitches (0.35x) and theta/delta 1.12 is the highest around, delta 2.95 slightly above the NR median; could be REM or NR but this EEG hour is flat and non-informative. |
| 8 | 13439 | NR | medium | rule | EMG atonic floor (0.22x), slow-wave EEG with delta 3.31 above median and low theta/delta 0.19; no theta for R. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSD03_B_epochs.png`.

**Skeptic (tried to refute the rescue):** partially usable, tier X. Strongest objection: Tier C rests on eeg_alone_ok, which is True in every hour of every recording I checked, so it tests nothing. The EEG-only HMM has split the recording at a step change, not at sleep. It calls 100 % NREM in ZT0-14, including ZT8-9 where the EMG is 97-99 % wake, and 0 % NREM in ZT16-23. At about ZT15.3 both channels change together. EEG total power falls by about 0.8 log and beta by about 1 log. EMG p90 falls from about 146 uV to 4-6 uV, with no movement for ZT15-19 in the dark. Then a low floor with periodic spikes follows. A common-mode change like this points to a connection or headstage event, not to sleep. The rule also scores 0 % REM in 24 h (2 REM-onset events), and the HMM's 54-88 % R in ZT0-3 is nonsense. Checked: I read score.json and blocks_1h.csv and recomputed per-hour EEG total, delta and beta power, EEG and EMG 60 Hz (EEG rises 40 -> 180 uV), EMG percentiles, stage fractions and AUC. Recording AUC is 0.47 and rule vs EEG-only kappa -0.37; EEG-only NREM is 100 % light vs 32 % dark. Before the step (ZT0-14) per-hour AUC is 0.75-0.93 in 11 of 15 hours and delta tracks the EMG. So only W vs NR in the light phase (about 12 L + 3 D h) could be salvaged, with no REM and not as a 24 h window.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsd03-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG bad, EMG bad; rule follows the EEG: not applicable; tier agreed.
Plausibility: No staging was produced (all grey), appropriately.
Concerns: Mains of ~5 mV on the EEG and ~4.6 mV on the EMG, 100% artefact epochs. The EMG gap RMS is a smooth slow drift between ~85 and 300 uV with no bursts and no floor, which is technical, not muscle. The EEG spectrogram is stripes with no delta/wake alternation. X is right; no hours should be kept.


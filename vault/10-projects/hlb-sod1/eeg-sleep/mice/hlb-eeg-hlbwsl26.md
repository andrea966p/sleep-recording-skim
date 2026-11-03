---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "HLBWSL26: EEG re-score 2026-11, baseline tier B, recovery tier A"
tags: [eeg, hlb, mouse, hlbwsl]
---

# HLBWSL26: W-SL (water, ad libitum), rig C2

> [!abstract] Decision (2026-11-03 re-score)
> - **Baseline:** tier **B** → W / NR / R on the usable hours. review: A -> B: A only through the ss60 switch at exactly 20 h; the primary gap EMG gives B; EEG carries 124 uV mains (reviewer + skeptic + critic)
> - **Recovery:** tier **A** → W / NR / R, whole window. screen
> - **Paired W/NR/R (both windows A or B):** yes.
> - Old pipeline: baseline NOT SCOREABLE, recovery NOT SCOREABLE.

Method: [[hlb-eeg-scoring-method-2026-11]] · all mice: [[hlb-eeg-sleep-overview]] · data: [[hlb-eeg-data-backbone]]

## Numbers

| | baseline | recovery |
|---|---|---|
| screen tier (before review) | A | A |
| hours usable, EEG + EMG | 20 | 24 |
| … of them light | 11 | 12 |
| … of them dark | 9 | 12 |
| hours usable, EEG alone | 20 | 24 |
| hours usable, EMG alone | 24 | 24 |
| EMG separability η (gap; ≥ 0.70) | 0.850 | 0.879 |
| η, SleepStager 20–90 Hz EMG | 0.772 | 0.790 |
| δ AUC, NR vs W (≥ 0.75) | 0.787 | 0.863 |
| EEG median log10 δ (2–4) | 2.88 | 2.84 |
| EEG-alone state changes / h (≥ 5) | 51.5 | 32.8 |
| κ rule vs HMM | 0.84 | 0.91 |
| κ NREM, rule vs EEG alone | 0.73 | 0.83 |
| κ rule, gap vs 20–90 Hz EMG | 0.97 | 0.96 |
| artifact epochs % | 2.1 | 0.4 |
| EEG 60 Hz, median µV | 124 | 17 |
| EMG 60 Hz, median µV | 1200 | 180 |
| wake % light (rule) | 19.1 | 29.5 |
| wake % dark (rule) | 53.2 | 66.0 |
| NREM % light, EEG alone | 54.9 | 53.0 |
| NREM % dark, EEG alone | 32.1 | 26.1 |
| sleep % light, EMG alone | 79.0 | 69.9 |
| sleep % dark, EMG alone | 40.1 | 34.1 |
| r@1min (project definition) | 0.357 | 0.595 |
| old verdict reason | rung 2 CONNECTION FAIL: 0.0% usable, longest unbroken block 0.0 min | rung 3 SCOREABILITY FAIL: 23.78 h in 39 block(s), r@1min 0.504 |

REM % is not given (partly fixed by the rule's cut). Shares are % of usable time.

## Baseline

![[2026-11-03-hlb-eeg-hlbwsl26-b-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG partial, EMG partial; rule follows the EEG: mostly; tier disputed → B.
Plausibility: Broadly plausible: wake 20% light vs 58% dark, delta bands alternate with wake, EMG (ss60 version) has a clean low floor with bursts. But EEG delta amplitude is low (about 3.0 vs 3.5 in other mice), r@1min is only 0.37, artefact spikes are frequent (2.1% of epochs), and 4 of 24 hours (ZT4-5, 6-7, 12-13, 22-23) are dropped.
Concerns: EEG has large mains pickup (124 uV) and low slow-wave amplitude, so delta/theta separation is weak; many contested epochs have flat low-amplitude EEG (delta about 2.6-2.8) with EMG sitting at 0.8-1.0x the cut for long stretches, which the rule calls NR and the HMM calls W: these are quiet wake or light sleep and cannot be separated reliably. EMG source switched to ss60 (mains-subtracted) because the gap EMG tier is only B, a sign that the EMG is also mains-dependent. Exactly 20 usable hours is at the A cut; I would call B (sleep vs wake usable, REM and fine NR staging not trustworthy). Old NOT SCOREABLE is too harsh for sleep vs wake but fine for REM.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 1048 | uncertain | low | neither | EEG nearly flat (delta 2.73), EMG steady at 0.52x without bursts, theta/delta 0.86; could be desynchronised REM or light NR, no clear theta rhythm. |
| 2 | 1581 | W | low | hmm | EMG continuously active about 1x cut across the epoch inside a W run, delta 2.77 low, sigma 2.14 low, flat EEG; quiet wake. |
| 3 | 1796 | W | low | hmm | Muscle tone 0.73-0.85x cut with continuous activity after a big burst, delta 2.65 low, sigma 2.02 low; not atonic so the R* mark is wrong, quiet wake more likely than NREM. |
| 4 | 4557 | W | medium | hmm | EMG bursts through the whole epoch (1.05x cut), delta 2.88 low (NR median 3.02), sigma 2.19, flat EEG; this stretch (an hour the screen dropped) is quiet wake, not NR. |
| 5 | 8603 | uncertain | low | neither | EMG quieter (0.61x) between bursts, delta 2.52 at wake level, flat EEG; quiet wake vs light NR not decidable. |
| 6 | 15864 | W | medium | rule | Continuous muscle activity 0.94x cut in the dark, delta 2.67, sigma 1.89 low, neighbours clear W (rule and HMM both W). |
| 7 | 16720 | uncertain | low | neither | EMG 0.64x with heartbeat spikes, theta/delta 0.85, delta 2.85 close to NR median; low-amplitude EEG gives no clear theta, possible REM but not provable. |
| 8 | 21038 | NR | medium | rule | Delta 2.99 at NR median 3.02, theta/delta 0.30, EMG quiet 0.67x with heartbeat, slow waves visible (rule and HMM both NR). |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL26_B_epochs.png`.

**Skeptic (tried to refute the rescue):** partially usable, tier B. Strongest objection: Tier A comes only from switching the EMG source after the fact. The primary gap EMG gives tier B. The ss60 fallback rule (score.py, added 2026-11-03) replaces it only when ss60 gives the better tier, and then lands exactly on the 20 h threshold (10L + 10D). The gap EMG's sleep floor is 71 % 20 Hz comb interference, and that share varies from 0.25 to 0.85 by hour. This is also the weakest EEG of the set. NR vs W log10 delta differs by only 0.25, and 13.5 % of rule-NR epochs have delta below the W median (1.9 % in 29_B). AUC is 0.789, the 1-min delta-EMG rho is only -0.39, and EEG 60 Hz is 124 uV. Several contested epochs (1581, 1796, 4557) are scored NR with continuous tone at 0.85 to 1.05x the cut and wake-level delta (2.4 to 2.8 vs NR median 3.02), which is quiet wake under the handbook. In the light the rule's NR exceeds the EEG-only NR by 14.5 points (69.4 vs 54.9 %). Staging is still usable: the gap and ss60 EMG agree on wake/sleep for 98.2 % of epochs, EMG bursts are muscle-like and anti-correlated with mains (rho -0.64), and wake light/dark is 19.7 / 57.7 %. Use B, and expect NR to be inflated by quiet wake. Checked: Brief; overview and epochs PNGs; score.json (tier_gap B, tier_ss60 A, emg_source ss60); score.py source-selection code (use_ss60 when ss60 gives a better A/B tier); blocks_1h.csv (dropped hours 4, 6, 12, 22; hour 6 is about 96 % sleep with AUC 0.53). From the parquets: medians by stage, NR-W delta gap, NR epochs below the W delta median, EEG-only agreement with rule NR (79.8 %), 1-min rho, gap vs ss60 agreement, hourly floor. From psd_emg.npy: comb share in the gap and ss60 bands, and a rising 80 to 90 Hz floor from 120 Hz leakage in ss60. From psd_eeg.npy: NR 2 Hz power 322 vs about 850 in good mice.

## Recovery

![[2026-11-03-hlb-eeg-hlbwsl26-r-overview.png]]

*The agents read the first screen, before the review fixes; a tier they dispute may already have moved.*

**Agent scorer:** EEG good, EMG good; rule follows the EEG: yes; tier agreed.
Plausibility: Plausible: wake 38 % in the light (higher than the rest of the batch) and 66 % in the dark. Delta bands alternate with wake, there is a clear EMG floor, and a sleep block appears at ZT18 to ZT19.5. EEG delta is lower overall (NR median 3.06) than other mice, which probably reflects electrode or animal differences, not noise. The old rung-3 rejection (r@1min 0.50) came from an EMG band that is mostly mains here (raw EMG 60 Hz 180 uV), and the mains-free EMG gives a clear bimodal signal (eta 0.88). So it was rejected wrongly.
Concerns: Three light hours (ZT2 to 3, ZT4 to 5, ZT8 to 9) were dropped. They look wake-heavy in the overview, so they may fail the EEG-agreement test for lack of NR rather than for bad signal; the loss is 3 h of mostly wake and is not critical. Delta range is narrower, so choose cuts per mouse (already done). Sleep in the light is more fragmented than in other mice, which may be real.

| panel | epoch | agent call | conf. | agrees with | why |
|---|---|---|---|---|---|
| 1 | 808 | NR | medium | rule | A burst starts about 2.8 s into the epoch and runs on into the next one, so under 1.5 s (less than half) lies inside it. Before that EMG is flat and the EEG is NR-like. The HMM's W comes from the burst's RMS. |
| 2 | 5332 | uncertain | low | neither | EMG is flat (0.43x, the same as the NR floor), delta 2.87 is below the NR median and theta/delta 1.39, but the EEG is a mixed moderate rhythm. REM follows in the next epochs. It is not clear if this is the REM onset or the last NR. |
| 3 | 5919 | R | medium | hmm | EMG is atonic with heartbeat spikes only (0.31x), delta 2.87 is below the NR median, sigma has dropped to about 2.0, and the EEG is regular theta-like. It sits between R epochs. Delta has not returned and tone is not back, so REM should continue. |
| 4 | 10717 | W | medium | rule | Two EMG bursts (about 0.6 to 2.3 s and 3.4 s onwards) cover over half the epoch. Delta 2.36 is low, theta/delta 0.32, and the neighbours are wake. |
| 5 | 15011 | R | medium | hmm | EMG is flat (0.30x), delta 2.72 is low, theta/delta 1.38, sigma 2.09 has dropped, and the EEG is a regular fast rhythm. It leads into several R epochs. |
| 6 | 17145 | R | medium | rule | EMG is atonic with heartbeat spikes (0.37x), delta 2.84 is low, theta/delta 1.36 and sigma is low. The neighbours are R. |
| 7 | 19013 | uncertain | low | neither | EMG is flat (0.41x) but theta/delta is only 0.50 and delta 2.93 is near the middle. R run starts in the next epochs. It could be the end of NR or fading theta in REM. |
| 8 | 20359 | W | medium | hmm | EMG has continuous bursts across the epoch (0.85x tone, 1.02x RMS), delta is 2.53 (wake level), and sigma has dropped to about 1.9. It sits between wake neighbours. The rule's NR is not supported. |

Traces: `~/sleep-data/hlb-rescore-2026-11/review/HLBWSL26_R_epochs.png`.

**Skeptic (tried to refute the rescue):** usable, tier A. Strongest objection: The three dropped light hours (ZT2, 4 and 8) are consolidated sleep, not wake as the previous reviewer read them. Their EMG wake fractions are 0.050, 0.063 and 0.036, and the overview shows high delta with a low EMG floor. They fail only because the delta AUC test is ill-posed when an hour holds a handful of W epochs (AUC 0.70 to 0.73), while all-wake hours are exempt from it. As a result the reported light wake (38.1 %, kept hours) is biased up by 8.6 points against all 12 light hours (29.6 %). Light-phase summaries must be computed on all hours, or the test must exempt hours that are more than 90 % sleep. The EEG separation is moderate (NR-W delta gap 0.35, 8 % of NR below the W median), and raw EMG mains is 180 uV. Checked: Brief; overview PNG (re-viewed: the red hours are sleep blocks); previous reviewer's epoch calls; score.json (21 h, 9L/12D); blocks_1h.csv (wake_frac_emg and AUC of the dropped hours); score.py hour-test logic. From the parquets: wake % on all vs kept hours; EMG NR 12.4 / W 100 uV; 1-min rho -0.48; EMG anti-correlated with the 60 Hz line (rho -0.58). Comb share at chance (0.15). The old rung-3 rejection (r@1min 0.504 on a mains-dominated 10-124 Hz band) is consistent with a wrong rejection.


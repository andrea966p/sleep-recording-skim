---
type: reference
area: hlb-sod1
status: active
created: 2026-11-03
summary: "How the four HLB EEG batches were re-scored on 2026-11-03: the professor's SleepStager rule on a mains-free EMG, an HMM second scorer, label-free usability tiers, agent review"
tags: [eeg, emg, sleep-scoring, method, sleepstager, hlb]
---

# HLB EEG re-score (2026-11): the scoring method

> [!abstract] TL;DR
> - **Staging** is the professor's SleepStager rule, **unchanged** (`rule.apply_rule`, physio passes,
>   4-s epochs, every cut fitted on the recording itself). It was validated at κ ≈ 0.89 against
>   seven human scorers on 4-s sheets. The one input we change is the **EMG**: our rig's EMG carries
>   60 Hz mains (up to mV on open leads), so the rule reads EMG power **between the harmonics**
>   (70–470 Hz, notches at every 60 Hz multiple). SleepStager's own 20–90 Hz EMG with a 60 Hz notch
>   is run beside it as a sensitivity.
> - **A second, independent scorer** (a per-recording 3-state Gaussian HMM, no labels) and two
>   single-signal scorers (EEG alone, EMG alone) say where the rule can be trusted.
> - **Usability** is judged without labels, per hour and per recording, by tests that look at the
>   animal's own signals (the professor's EMG separability and floor tests, and whether the EEG
>   sees the state the EMG sees). The old rung 2 (wire-free amplifier inputs) is **not** used: it
>   needs the 262-channel file, and it rejected good animals ([[contaminated-floor-rejects-good-eeg]]).
> - Recordings fall in **tiers A–X**; tier A and B give W / NR / R, C gives NREM from the EEG alone,
>   D gives sleep vs wake from the EMG alone.
> - No human labels were reachable (the workstation holding Andrea's 8,441 hand-scored HLBSSL33 R
>   epochs is under repair), so agreement is measured between methods, and contested epochs were
>   **reviewed by agents reading the traces** against the handbook.
>
> Results: [[hlb-eeg-sleep-overview]]. Data layout: [[hlb-eeg-data-backbone]]. Rerun: [[hlb-eeg-compute-runbook]].

## Why a re-score

The 2026-09-30 screen ([[2026-09-30-scoreable-mice-on-the-24h-windows]]) left 1, 0, 1 (2) and 1 (3)
paired mice per batch. Three of its criteria are now known to be wrong for this rig:

| old criterion | what was wrong | evidence |
|---|---|---|
| rung 2, EEG/EMG judged against the chip's wire-free inputs | the floor itself carried signal on many chips, so good EEG read UNJUDGEABLE or FAIL | [[contaminated-floor-rejects-good-eeg]], [[2026-08-26-per-chip-floor-fix]] |
| stage 3 EMG = RMS over 10–124 Hz | on open or high-impedance leads that band is 90–100 % mains: the measure read hum, not muscle | [[2026-10-06-S-SD-EMG-rescue-between-harmonics]], [[2026-10-02-noise-series-4mice-24h-analysis]] |
| r@1min > 0.30 on that EMG | a persistence of the hum-driven staging, so it failed animals whose muscle was fine | same |

## Pipeline

Code: `eeg-emg-analysis/rescore_2026_11/` (`ingest.py` → `features.py` → `score.py` → `backbone.py`,
`review_pack.py` for the figures). Venv `~/hlb-eeg-venv` (Python 3.12). Every stage reads the
per-mouse CSV ([[per-mouse-csv-format]]); nothing reads the xdat.

1. **Ingest.** Each CSV is copied from the SKIM NAS while hashing; the sha256 must equal
   `info.json` `upload.sha256_remote`. EEG and EMG are kept as float32 µV; the sample counter is
   checked for gaps (none in any recording).
2. **Features per 4-s epoch.**
   - EEG: SleepStager's `batch_spectral` (1-s Hann Welch, 1-Hz bins; δ 1–4, θ 6–9, σ 10–15,
     β 15–30, low γ 30–50 Hz, θ/δ, γ fraction, peaks). The 1–50 Hz spectrum of every epoch is kept.
   - EMG `gap` (primary): 4th-order 70–470 Hz band-pass, IIR notch (≈12 Hz wide) at 60, 120 … 420 Hz;
     RMS and spike-proof tone (median of the 0.5-s sliding RMS, 0.1-s hop), as SleepStager defines it.
   - EMG `ss60` (sensitivity): SleepStager's `batch_emg_features` / `batch_emg_tone_median`, 20–90 Hz,
     notch moved from 50 to 60 Hz.
   - EMG `gapw` (parity with 2026-10-06): Blackman-Harris Welch power in the bins ≥ 7 Hz from every
     60 Hz multiple, 67–470 Hz.
   - Diagnostics: 60 Hz line amplitude on both channels, rail contact (SleepStager's `rail_levels`,
     read off the recording), flat EEG (< 2 µV sd).
3. **Artifact epochs.** EEG: rail, flat, or log total power > 6 robust SD above the median. EMG:
   rail, or log gap RMS > 6 robust SD. They enter no cut and no statistic; the rule labels them from
   their clean neighbours, as it does in the viewer.
4. **Staging.** `rule.apply_rule(emg_rms_gap, theta_delta, delta_power, epoch_s=4,
   emg_tone_med=emg_tone_gap, exclude=artifact)`; the same with `ss60`.
5. **Second scorer.** 3-state Gaussian HMM (diagonal covariance, sticky start, best of 3 seeds) on
   log EMG, log δ, log θ/δ, robust-z, fitted per recording; W = highest EMG state, R = highest θ/δ of
   the other two. Per-recording HMM scoring is a published label-free method (Huffman et al. 2021,
   κ > 0.75 vs manual, PMID 33403714).
6. **Single-signal scorers.** EEG alone: 2-state HMM (NREM vs not) on log δ, log θ/δ, log σ,
   logit γ fraction. EMG alone: the rule's own Otsu midpoint on the clean EMG (wake vs sleep).

## Usability: the tests and the tiers

Written 2026-11-03 before the cohort was screened; calibrated only on the positive control
HLBSSL33 Recovery (the hand-scored mouse) and on HLBSSD19 Baseline (a known-dead EEG), see the
calibration note below.

| level | test | pass | source |
|---|---|---|---|
| recording, EMG | Otsu separability η of log gap EMG | ≥ 0.70 | professor, SleepStager notes 5.8 and `reports/EMG_UNUSABLE.md` (2026-10-22): η < 0.70 flagged 2 of 112 reference recordings, both failures |
| hour, EMG | p10 of log EMG minus the log cut | ≤ 0, unless the hour is all wake (EEG-alone NREM < 10 %, or without a readable EEG, EMG-alone wake ≥ 90 %) | professor: 7 of 7 blocks with the floor above the cut were failures, 0 false alarms; his test was defined on blocks with 10–90 % wake |
| recording and hour, EEG | AUC of log δ, rule NR vs W (W/NR is split by the EMG alone) | ≥ 0.75 | ours: the EEG must see the state the muscle sees |
| recording, EEG alone | 2-state EEG HMM: d′ of log δ between states, and more NREM in the light than in the dark | d′ ≥ 1.5 and light − dark > 0 | ours |
| recording, EMG alone | EMG-alone wake, dark − light | ≥ 10 points | ours: a technical two-level EMG passes η but has no day–night pattern (HLBSSD19 B) |

| tier | meaning | what it can give |
|---|---|---|
| **A** | EEG and EMG usable in ≥ 20 of 24 h (≥ 17 of 20 h for an SD recovery) | W / NR / R, bouts, spectra, the full window |
| **B** | both usable in ≥ 6 light hours and ≥ 6 dark hours | the same, on the usable hours only (shares of usable time) |
| **C** | EEG usable, EMG not | NREM vs not-NREM from the EEG alone; REM merges with wake |
| **D** | EMG usable and nocturnal, EEG not | wake vs sleep from the EMG alone |
| **X** | neither | nothing |

> [!note] Calibration, disclosed
> The first draft of two tests failed 6 of the 24 hours of the positive control, all of them
> single-state hours: the δ AUC compared EMG-wake with EMG-sleep **including REM** (low δ), and the
> floor test was applied to all-wake hours, where a floor above the cut is normal. Both were fixed
> on that one recording before any other was screened. The EMG-alone nocturnal test was added after
> HLBSSD19 Baseline showed a step-switching EMG with η 0.91 and 97 % "sleep" in the light.

> [!note] Two EMG measures, one tier (added 2026-11-03 after the S-SD batch was screened, disclosed)
> The whole screen (rule, HMM, hour tests, tier) runs twice: once on the gap EMG, once on
> SleepStager's own 20–90 Hz EMG with the 60 Hz notch. The gap result is used unless the 20–90 Hz
> one reaches tier A or B and the gap one does not; `emg_source` in every table says which carried
> the recording. Why: HLBSSD11 Recovery had η 0.61 on the gap EMG and 0.86 on 20–90 Hz, so a single
> pre-set band could throw away an EMG that works in the band the professor's tool reads. Choosing
> between two bands by η and the EEG agreement uses no sleep outcome. Tier C is judged on the
> EEG-alone hours, so it no longer depends on which EMG passed.

> [!warning] Bugs found by the independent code review (2026-11-03), fixed before the cohort run
> The gap filter's notch list started at 120 Hz, so 60 Hz itself was only attenuated by the
> band-pass (13.5 dB): HLBSSD15's EMG floor read 100 µV of hum. Fixed (notch at 60 Hz too) and
> every recording recomputed. Also fixed: the per-hour EEG test used EMG-split labels when the EMG
> was dead (tier C was unreachable); `r_1min` now uses the project's definition
> (`pipeline_common.within_block_persistence`, lag 15 epochs, within usable runs).

> [!warning] Fixes from the agent review (2026-11-03, before any SOD1 outcome was read)
> Eight Sonnet scorers read every overview and 456 contested epochs. Four Opus skeptics then tried to
> refute every newly usable window, and a critic checked for gaps. They found three screen flaws.
> All three were fixed in `score.py` and all 64 windows re-scored.
>
> 1. **Tier C tested nothing.** The EEG-alone hour flag was true in every hour of every recording, so
>    six windows reached C on dead EEG. **Fix: EEG level gate.** The median log10 δ of the clean
>    epochs must lie in 2–4 (log10 µV²), per recording and per hour, for tiers A, B and C. Dead or
>    disconnected channels sat at 0.3–0.9, cortical EEG at 2.3–3.3 and one railed channel at 4.6, so
>    the gate sits in a physical gap and was not tuned to which mice pass.
> 2. **The EEG-alone HMM split at technical steps.** In HLBSSL31 B and HLBWSD03 B it split at an
>    amplitude collapse, with 0.1–0.4 state changes per hour against ≥ 9 in every other window.
>    **Fix:** C now also requires ≥ 5 changes per hour.
> 3. **Asymmetric hour test.** The δ AUC was applied to near all-sleep hours. There it fails on too
>    few wake epochs, so kept hours were enriched for wake (+8.6 points of light wake in HLBWSL26 R).
>    **Fix:** the AUC is judged only in mixed hours (10–90 % EMG wake), the domain the professor
>    defined his floor test on.
>
> Windows that sit exactly on a tier bar were moved by review evidence, not by code. The table, with
> the reason for each move, is in [[hlb-eeg-sleep-overview#Review decisions]].

## What is reported, and what is not

- W, NR and sleep (NR + R) shares, per ZT hour, light and dark, bouts, NREM δ (SWA) time course,
  EEG spectra per state. Shares are of **usable** time.
- **REM % is not reported as a result**: the rule calls R only above the 82nd percentile of θ/δ and
  under the 15th percentile of δ of this recording's sleep, so REM's share is partly fixed by
  construction (the same caveat as stage 3, [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]]).
- n = 1 per arm is a case, not a result. EEG and nanotag findings stay separate
  ([[2026-10-06-eeg-and-nanotag-findings-reported-separately]]).
- No conventions were changed. The handbook's C1–C12 ([[sleep-scoring-handbook]]) are what the agent
  reviewers applied to the contested epochs; the professor still has to confirm them.

## Literature (checked 2026-11-03, PubMed metadata)

- Per-recording, label-free scoring: Huffman et al. 2021, J Sleep Res 30:e13262, PMID 33403714
  (HMM, κ > 0.75); Barger et al. 2019 AccuSleep, PMID 31834897 (per-recording mixture z-scoring);
  Brodersen et al. 2024 Somnotate, PMID 38232122 (LDA + HMM, per-epoch certainty).
- Supervised state of the art (needs labels we do not have): Miladinović 2019 SPINDLE, PMID 30998681;
  Yamabe 2019 MC-SleepNet, PMID 31672998 (κ 0.94); Wang 2023 IntelliSleepScorer, PMID 36922536 (κ 0.91).
- EEG alone: Tezuka et al. 2021, PMID 34045518 (90 % accuracy, single channel). Published as a
  methods result, not as a primary outcome: our tier C is a labelled fallback.
- No published numeric threshold exists for EMG bimodality, minimum usable hours or mains handling
  in rodent EMG (Rayan et al. review, PMID 36479908): every bar above is the lab's own.

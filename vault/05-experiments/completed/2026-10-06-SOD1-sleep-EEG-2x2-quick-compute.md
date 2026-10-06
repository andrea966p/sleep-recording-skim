---
tags: [experiment, eeg, emg, sod1, sleep, W-SD, S-SD, W-SL, S-SL, hlb, analysis, completed]
created: 2026-10-06
status: complete
recordings: [allego_1__uid0819-17-25-20, allego_2__uid0827-12-58-32, allego_0__uid0825-09-00-00, allego_2__uid0902-13-00-28, allego_0__uid0910-09-00-00, allego_0__uid0917-09-00-09, allego_0__uid0912-08-55-18, allego_0__uid0921-00-17-34]
---

# Did SOD1 change sleep? The four EEG/EMG batches as a 2x2 (quick compute, 2026-10-06)

> [!abstract] TL;DR
> Andrea asked: compare sleep deprivation with normal sleep, SOD1 against water, and say whether SOD1
> did anything to sleep. Outcome: % of time asleep (NREM + REM) from the stage-3 hypnograms of the
> 24 h analysis windows.
> - **Without deprivation, no SOD1 effect is detectable.** After about a week on treatment and before any
>   deprivation, SOD1 mice slept **61.1 % of 24 h against 60.6 %** for water mice (n = 3 vs 6, +0.5 points,
>   exact p = 0.96). With the EMG mains notch the result is **56.2 vs 53.7 %** (n = 6 vs 8, +2.5 points,
>   p = 0.24, 95 % CI −1.8 to +6.9 points, i.e. −26 to +99 min/day).
> - **After deprivation, the EEG cannot answer it.** S-SD has **no scoreable mouse at recovery**, under the
>   official staging and with the notch. The only connected one, HLBSSD18, has an EMG with no wake
>   contrast at recovery even when notched (wake 12.8 %, r@1min 0.02).
> - **The measurement does see deprivation.** The one paired W-SD mouse, HLBWSD08, slept **+11.9 points**
>   more from 13:00 to 09:00 after CSD than at its own baseline (+16.3 notched, mostly in the dark phase).
>   The ad libitum water controls moved +0.9 and +4.0 (notched). n = 1, so this is a case, not a result.
> - So, from the EEG, the SOD1 × deprivation question stays open.
> - ⏩ **Update, same day: one S-SD mouse rescued with EMG.** With EMG power measured between the 60 Hz harmonics
>   from the raw 1000 Hz file, HLBSSD15 is scoreable at both timepoints. Its rebound is +6.6 points against HLBWSD08's
>   +16.1, an interaction of −13.8 points with one mouse per arm. See [[2026-10-06-S-SD-EMG-rescue-between-harmonics]].
> - Side finding: the official W-SL baseline shows 44–64 % sleep in the dark phase, which is not
>   plausible. Notched, it is 26–41 %. The official "W-SL lost 8 points" is the EMG mains artefact
>   ([[2026-10-02-noise-series-4mice-24h-analysis]]), not biology.

## The design as it ran

SOD1 or water is given from **tethering, Day 1 of liquid monitoring** (S-SD intake grid: Day 1 = 08-18,
about 20–40 U/day). So every EEG **baseline is already on treatment**, about a week in, and before any
deprivation. Two consequences:
- **Baseline, SOD1 vs water** (all four batches) is the test of SOD1 without deprivation.
- **Recovery − baseline** is the effect of CSD in the SD batches, and of time alone in the SL batches.

| batch | liquid | sleep | baseline window | recovery window |
|---|---|---|---|---|
| W-SD | water | CSD 09:00–13:00 daily | 08-20 09:00 → 08-21 09:00 | 08-27 13:00 → 08-28 09:00 (after bout 7 of 8) |
| S-SD | SOD1 6.8 U/mL | CSD 09:00–13:00 daily | 08-25 09:00 → 08-26 09:00 | 09-02 13:00 → 09-03 09:00 (after the last bout) |
| W-SL | water | ad libitum | 09-10 09:00 → 09-11 09:00 | 09-17 09:00 → 09-18 09:00 |
| S-SL | SOD1 6.8 U/mL | ad libitum | 09-12 09:00 → 09-13 09:00 | 09-21 09:00 → 09-22 09:00 |

**Matched hours.** Both SD recoveries exist only from 13:00 to 09:00 (ZT4–24), so every change from
baseline uses ZT4–24 in both windows: light ZT4–12 (8 h), dark ZT12–24 (12 h). See
[[02-procedures/CANONICAL-recording-windows-and-protocol]].

## Method

- **Outcome.** Sleep % = NREM + REM epochs ÷ all scored 4 s epochs inside contact blocks, from the
  stage-3 hypnograms in `~/eeg-processed-windows/` (e10). REM's share is fixed by construction, so only
  sleep vs wake is used. The recomputed wake % matches every `features.json`.
- **Who is in.** Official: rung 3 PASS on the window cards ([[2026-09-30-scoreable-mice-on-the-24h-windows]]).
  Sensitivity A adds HLBSSL31 and HLBSSL35 at recovery (stage 3 only, contaminated floor) and HLBWSL23 at
  baseline (r@1min 0.289). Sensitivity B is the **EMG 60/120 Hz notch**, validated 2026-10-02 but not adopted.
  It keeps the ladder: rung 2 PASS, then notched stage 3 SCOREABLE.
- **The notch run.** `qc/emg_mains_staging_test.py` on the eight window folders, output in
  `~/eeg-notch-windows-2026-10-06/` (e10). Its `orig` pass reproduces **42/42** official verdicts.
- **Statistics.** Exact permutation test of the difference in means (every relabelling, two-sided), Welch
  95 % CI, Hedges' g, and the smallest effect a two-sample t-test finds at 80 % power (MDE). There is no
  multiplicity correction: about 30 tests were run and none reached p < 0.05.
- **Script.** `eeg-emg-analysis/qc/sod_sleep_2x2_2026_10_06.py HYP_DIR [NOTCH_DIR]`. Per-mouse values for
  both stagings: [[2026-10-06-SOD1-sleep-2x2-per-mouse.tsv]].

## Who could be used

B = baseline, R = recovery, P = paired.

| batch | official B / R / P | notched B / R / P | paired mice (notched) |
|---|---|---|---|
| W-SD | 3 / 1 / **1** | 3 / 1 / **1** | HLBWSD08 |
| S-SD | 0 / 0 / **0** | 1 / 0 / **0** | none. HLBSSD18 is scoreable at baseline only |
| W-SL | 3 / 2 / **1** | 5 / 3 / **2** | HLBWSL23, HLBWSL24 |
| S-SL | 3 / 2 / **1** | 5 / 2 / **2** (4 with A) | HLBSSL33, HLBSSL39 (+31, 35) |

## Results

### 1. SOD1 vs water without deprivation (baseline, about a week on treatment)

| staging | n SOD1 / water | SOD1 | water | difference | p (exact) | Welch 95 % CI | g | MDE (80 %) |
|---|---|---|---|---|---|---|---|---|
| official, 24 h | 3 / 6 | 61.1 | 60.6 | **+0.5** | 0.96 | −9.8 to +10.8 | 0.06 | 18 pts |
| official, light | 3 / 6 | 77.4 | 79.6 | −2.2 | 0.68 | −10.2 to +5.8 | −0.31 | 15 pts |
| official, dark | 3 / 6 | 44.8 | 41.6 | +3.3 | 0.67 | −15.3 to +21.8 | 0.27 | 25 pts |
| notched, 24 h | 6 / 8 | 56.2 | 53.7 | **+2.5** | 0.24 | −1.8 to +6.9 | 0.62 | 6 pts |
| notched, light | 6 / 8 | 75.1 | 74.4 | +0.7 | 0.76 | −4.1 to +5.5 | 0.15 | 7 pts |
| notched, dark | 6 / 8 | 37.3 | 33.0 | +4.3 | 0.24 | −3.8 to +12.4 | 0.63 | 10 pts |
| notched, 24 h, SL batches only | 5 / 5 | 57.1 | 55.6 | +1.5 | 0.48 | −3.4 to +6.4 | 0.41 | 7 pts |

The SL-only row compares two runs recorded two days apart (09-10 and 09-12), so it is the least
confounded by batch. Official SOD1 at baseline comes from S-SL alone; the notch adds HLBSSD18.

### 2. SOD1 vs water at the ad libitum endpoint (ZT4–24)

Official: S-SL 53.7 vs W-SL 55.3 % (n = 2 vs 2, −1.5 points; p cannot go below 0.33 at this n). Notched:
53.6 vs 53.9 % (n = 2 vs 3, −0.3). Notched with A: 51.9 vs 53.9 % (n = 4 vs 3, −2.0, p = 0.49). Its light
phase, −5.8 points with p = 0.057, is one of about 30 tests, so it is read as noise.

### 3. Change from baseline, 13:00 → 09:00, per mouse

| mouse | batch | official Δ ZT4–24 (light / dark) | notched Δ ZT4–24 (light / dark) |
|---|---|---|---|
| **HLBWSD08** | W-SD | **+11.9** (+6.1 / +13.4) | **+16.3** (+7.5 / +20.1) |
| HLBWSL24 | W-SL | −8.2 (−4.4 / −10.7) | +0.9 (+4.7 / −1.6) |
| HLBWSL23 | W-SL | −17.7 (−11.5 / −21.8), A only | +4.0 (+3.7 / +4.3) |
| HLBSSL33 | S-SL | +0.5 (+0.7 / +0.4) | +6.6 (+5.1 / +7.6) |
| HLBSSL39 | S-SL | not paired | +3.7 (−3.4 / +8.4) |
| HLBSSL31 | S-SL | −9.3 (0.0 / −15.5), A only | −5.2 (+4.3 / −11.5), A only |
| HLBSSL35 | S-SL | −4.2 (+0.2 / −7.1), A only | −3.7 (+0.6 / −6.6), A only |
| S-SD | — | none | none |

- **CSD in water:** HLBWSD08 +11.9 against W-SL −8.2 officially. Notched, +16.3 against +2.5 (n = 1 vs 2).
  The extra sleep after deprivation sits mostly in the dark phase.
- **SOD1 without deprivation:** S-SL vs W-SL change, +2.7 points notched (n = 2 vs 2), −2.1 with A (n = 4 vs 2, p = 0.67).
- **SOD1 under deprivation:** not estimable. S-SD has no recovery data.

## Why the notch matters for this question

Each arm is a different batch, recorded on a different date, while the rig's mains pickup changed.
Stage 3 splits wake from sleep with an Otsu cut on EMG rms that still contains 60 Hz. So mains differs by
batch, and that alone can produce a group difference. W-SL shows it:

| W-SL baseline, dark-phase sleep % | HLBWSL22 | HLBWSL23 | HLBWSL24 | HLBWSL27 |
|---|---|---|---|---|
| official | 59.8 | 64.3 | 45.7 | 44.2 |
| notched | 41.4 | 37.8 | 36.8 | 25.9 |

Notched, these fall to 26–41 %, in line with the W-SD baselines (29–41 %). The official values are too
high, so the official W-SL baseline is inflated and its "−8 points at the endpoint" is that artefact. The
SOD1 answer is the same either way, and this is one more piece of evidence for adopting the notch. That
decision is still open: [[2026-10-02-noise-series-4mice-24h-analysis]].

The notch also turns **HLBWSL23** and **HLBSSL39** into mice scoreable at both timepoints. That extends
the 2026-09-30 list, but only once the notch is adopted.

## Limitations

- **Batch equals group.** No arm shares a recording session with its comparator. The SL-only baseline
  comparison is the cleanest.
- **Tiny n.** At 3 vs 6 the official baseline comparison can only detect a difference of about 18 points
  (4 h/day). Notched, at 6 vs 8, about 6 points (1.5 h/day). A null here rules out large effects, not modest ones.
- **Automated staging, no human kappa.** The sleep/wake split is provisional. NREM/REM is not reported.
- **SD recoveries are 20 h, not 24.** Both stopped at 09:05. The W-SD window followed bout 7 of 8 with the
  protocol still running; the S-SD window followed the last bout.

> [!quote] Paper-ready
> In the EEG/EMG cohorts, oral SOD1 did not detectably change the amount of sleep without deprivation:
> after about one week of treatment, SOD1-treated mice slept 61.1 % of 24 h, against 60.6 % for
> water-treated mice (n = 3 vs 6; exact permutation p = 0.96). The effect of SOD1 on recovery sleep after
> chronic sleep deprivation could not be assessed, because no SOD1-treated, deprived mouse yielded a
> scoreable recovery recording.

## Files

- Script: `eeg-emg-analysis/qc/sod_sleep_2x2_2026_10_06.py`. It self-checks the permutation test and the MDE
  on start.
- Per-mouse table, both stagings: `05-experiments/attachments/2026-10-06-SOD1-sleep-2x2-per-mouse.tsv`.
- Official hypnograms: `~/eeg-processed-windows/<day>/` on e10. Notched: `~/eeg-notch-windows-2026-10-06/notch/<day>/`
  on e10, with the run log in `~/eeg-notch-windows-2026-10-06.log`.

## Related

[[_HLB-SOD1-project-hub]] · [[2026-09-30-scoreable-mice-on-the-24h-windows]] ·
[[2026-08-28-W-SD-cohort-closeout]] ·
[[2026-09-02-S-SD-recovery-sleep]] · [[2026-09-18-W-SL-light-phase-sleep]]

---
type: experiment
area: hlb-sod1
status: done
created: 2026-10-31
summary: "NS-SD / NW-SD tag Run 1 (10-22 → 10-30): baseline vs SOD1 / water days 1-6, same sleep, bout and rhythm analysis as HLBNSL. No detectable SOD1 effect; HLBNSL's RA signal not repeated; 59's shoulder tag reads as a restless mouse"
cohort: NS-SD + NW-SD (HLBNSSD51-55, HLBNWSD56-60)
tags: [experiment, nanotag, sod1, sleep, analysis, ns-sd, nw-sd]
---

# NS-SD / NW-SD, tag Run 1: before and after SOD1 (2026-10-31)

> [!abstract] TL;DR
> **What this is:** the first read of the SD nanotag batch ([[2026-10-19-NS-SD-NW-SD-nanotag-study]]), Run 1 only:
> 2 days of baseline (10-22 09:00 → 10-24 09:00) and the first 6 days on SOD1 or UV water (10-24 09:00 → 10-30 09:00).
> No SD yet: SD is in Run 2, read after sampling on 11-04. Same code and measures as HLBNSL
> ([[2026-10-05-HLBNSL-nanotag-merged-analysis]]), 5 SOD1 vs 5 water.
>
> **Results, in order of weight:**
> 1. **No detectable effect of SOD1 on sleep.** Change from baseline in total sleep: SOD1 +18 vs water +1 min/day
>    (p = 0.39); SOD1 effect +16 min/day, 95% CI about −18 to +58. Light and dark phase, bout length and every
>    immobility cutoff (24-60 s) agree.
> 2. **HLBNSL's rhythm-amplitude signal did not repeat.** RA change +0.045 vs +0.030, p = 0.24. The one shared
>    direction: SOD1 mice were quieter in the light phase (−113 vs +77 counts/h, p = 0.17).
> 3. **Dark-phase activity rose more in SOD1** (+616 vs +265 counts/h, p = 0.040; 0.024 without 59). One p under
>    0.05 among ~20 change tests, not pre-registered, sleep did not move with it: a lead at most.
> 4. **59's tag (shoulder, not flank) reads as a restless mouse:** dark activity about 2x the others (7,982 / 8,467
>    counts/h vs 2,780-6,110), dark sleep 15-16 % vs 23-37 %. Its own change is in range, so change from baseline is
>    usable; its absolute values are not comparable. Without 59 nothing changes in the conclusions.
> 5. **Groups matched at baseline:** every baseline p ≥ 0.31.

## What was done

| Step | Result |
|---|---|
| Data | `~/Desktop/261030_HLBNSSD/` (office PC), 10 CSV + 10 `.nta`, one file per mouse. All `2026-10-22 09:00:00 → 2026-10-30 08:59:48`, 57,600 bins, no gaps. Tag IDs match the registry (51 = 20639 … 60 = 20648) |
| Code | New `nanotag/analysis/cohort_sd.py` reuses `cohort.py` (scoring, tables, figures, permutation tests) with the NS-SD facts. `nta_qc.parse` now accepts activity-only files (`Temperature,None` header). `cohort.py` figure titles that named HLBNSL dates became constants (`BASELINE_NOTE`, `SOD1_WHEN`, `REMOVED_NOTE`, `REMOVED_SHORT`); `cohort.py --demo` passes. The HLBNSL Run-2-withheld regression was not re-run (raw data not on the office PC) |
| Scoring | Each file scored whole (48 s immobility = sleep), then split at 10-24 09:00, so no bout is cut at a file edge |
| Windows | From the sheet (`NANOTAG behavioral`, `NANOTAG recordings`): no handling or tests in Run 1, so **nothing removed**. Daily bottle weighing is kept, as in HLBNSL |
| Outputs | `nanotag/analysis/out/HLBNSSD/` (git-ignored): `daily_sleep.csv`, `summary_per_mouse.csv`, `console_output.txt`, 7 figures (PNG + PDF) |

> [!warning] SOD1 start time not logged
> Liquid monitoring Day 1 is 10-24, but the time the bottles went in is not in the sheet. Treatment is counted from the
> end of the logged baseline, 10-24 09:00. Dropping 10-24 entirely changes nothing (total sleep change +18 vs 0,
> p = 0.43). The actograms show a burst at ZT0 on 10-24 in 55, 58 and 59 that fits a 09:00 bottle change; **not used
> to set any window.** Andrea: log the time if you remember it.

## Group means (mean ± SEM, exact permutation p)

| Measure | Baseline SOD1 | Baseline water | p | Treatment SOD1 | Treatment water | p | Change SOD1 | Change water | p |
|---|---|---|---|---|---|---|---|---|---|
| Total sleep (min/day) | 734 ± 32 | 727 ± 37 | 0.98 | 752 ± 20 | 728 ± 38 | 0.70 | +18 | +1 | 0.39 |
| Light phase, % asleep | 70.8 ± 2.9 | 72.2 ± 1.6 | 0.75 | 73.6 ± 1.6 | 72.9 ± 1.9 | 0.75 | +2.8 | +0.7 | 0.29 |
| Dark phase, % asleep | 31.1 ± 2.5 | 28.8 ± 4.1 | 0.69 | 30.8 ± 1.3 | 28.3 ± 3.6 | 0.58 | −0.3 | −0.5 | 0.92 |
| Light sleep bout (min) | 10.9 | 11.9 | 0.48 | 11.5 | 12.2 | 0.29 | +0.5 | +0.3 | 0.86 |
| Dark sleep bout (min) | 5.3 | 6.1 | 0.48 | 5.1 | 5.7 | 0.63 | −0.1 | −0.4 | 0.67 |
| Light activity (counts/h) | 748 | 720 | 0.91 | 635 | 797 | 0.56 | −113 | +77 | 0.17 |
| Dark activity (counts/h) | 3,479 | 4,653 | 0.33 | 4,095 | 4,918 | 0.51 | +616 | +265 | **0.040** |
| Share of activity in dark | 0.833 | 0.865 | 0.33 | 0.870 | 0.864 | 0.81 | +0.037 | −0.001 | 0.08 |
| Rhythm amplitude (RA) | 0.789 | 0.801 | 0.71 | 0.834 | 0.832 | 0.99 | +0.045 | +0.030 | 0.24 |
| Day-to-day stability (IS) | 0.79 | 0.83 | 0.31 | 0.74 | 0.75 | 0.87 | −0.05 | −0.09 | 0.55 |
| Hour-to-hour fragmentation (IV) | 1.09 | 1.09 | 0.99 | 0.94 | 0.95 | 0.96 | −0.14 | −0.14 | 1.00 |

Baseline is 2 days, so per-mouse baselines are noisier than HLBNSL's 3. Power as for HLBNSL: about 20 mice per group
for 1 h/day.

![[2026-10-31-NSSD-run1-daily-sleep.png]]
*Daily sleep by group. SOD1 total sleep drifts up over the last three days (779 vs 723 min on 10-29), inside the
spread.*

![[2026-10-31-NSSD-run1-change-from-baseline.png]]
*Change from baseline and the SOD1 effect with its 95% CI. Every interval crosses 0. The SOD1 total-sleep mean is
pulled up by 55 (+71 min), the mouse with the lowest baseline (605 min).*

![[2026-10-31-NSSD-run1-zt-profile.png]]
*Sleep across the day. The two groups overlap at every hour on treatment. The ZT0 dip in both groups on treatment is the
daily room entry for bottle weighing.*

![[2026-10-31-NSSD-run1-sleep-summary.png]]
*Sleep measures, baseline and treatment.*

![[2026-10-31-NSSD-run1-rhythm.png]]
*Activity and rhythm measures.*

![[2026-10-31-NSSD-run1-actograms.png]]
*Actograms, one day per row. 59 (water) is active through most of every dark phase.*

## Per mouse

| Mouse | Group | Total sleep base → treat (min/day) | Dark % base → treat | Dark counts/h base → treat | Note |
|---|---|---|---|---|---|
| 51 | SOD1 | 758 → 789 | 27.4 → 32.8 | 3,323 → 3,656 | |
| 52 | SOD1 | 760 → 753 | 35.8 → 32.5 | 3,508 → 4,372 | |
| 53 | SOD1 | 768 → 760 | 31.8 → 29.5 | 3,316 → 4,303 | sprayed urine 10-30 |
| 54 | SOD1 | 778 → 779 | 37.0 → 33.1 | 2,780 → 3,294 | |
| 55 | SOD1 | 605 → 677 | 23.5 → 26.1 | 4,468 → 4,852 | BW −6.6 % at 6 d post surgery |
| 56 | water | 770 → 781 | 36.1 → 34.6 | 2,997 → 3,198 | |
| 57 | water | 788 → 789 | 36.0 → 35.5 | 3,121 → 3,388 | |
| 58 | water | 797 → 784 | 32.9 → 31.3 | 3,330 → 3,429 | BW −10.2 % |
| 59 | water | 605 → 595 | 14.8 → 16.3 | 7,982 → 8,467 | tag at the shoulder |
| 60 | water | 675 → 694 | 24.0 → 23.5 | 5,836 → 6,110 | BW −10.0 % |

## Reading it

- **Group comparison:** valid. Nothing was removed, both groups had the same room entries, and baseline is matched.
- **Same answer as HLBNSL** on sleep amount: no detectable SOD1 effect, interval wide. HLBNSL's RA lead was flagged as
  a target for this batch; on these 6 days it does not separate the groups.
- **59:** keep it in the change analyses, flag it in any absolute figure. Decide before Run 2 whether to show it on
  the SD figures (an SD-efficacy measure based on immobility will read 59 as awake more often).
- 🛑 Report on its own: not pooled with the EEG batches, never "the nanotag agrees"
  ([[2026-10-06-eeg-and-nanotag-findings-reported-separately]]).

## Still open
- [ ] Run 2 (10-30 19:00 → 11-04): undisturbed window 10-31 → 11-03, SD efficacy, recovery 11-03 15:00 → 11-04
  09:00, wait before Y-maze. Needs the SD windows and each mouse's Y-maze start in `cohort_sd.py`.
- [ ] SOD1 bottle time on 10-24 (Andrea).
- [ ] **To do (Andrea, 2026-10-31: another time):** report + methods pages and `.docx` for this read, as for HLBNSL
  (`nanotag/report/build.sh`).
- [x] 2026-10-31: HLBNSL regression after the `cohort.py` / `nta_qc.py` edits, on the office PC copy
  (`~/Desktop/nanotag data HLBNSSL/`): git HEAD code and edited code give byte-identical tables, console output and
  figures, and match [[2026-10-05-HLBNSL-nanotag-merged-analysis]] (793 vs 768 min/day, p = 0.61; RA change p = 0.029).
  The Run 2 folder there is `261002_HLBNSSL_7days_part2`, but `cohort.py` expects `261002_HLBNSSL` and skips a
  missing folder silently: link or rename it before running `cohort.py` on that copy.

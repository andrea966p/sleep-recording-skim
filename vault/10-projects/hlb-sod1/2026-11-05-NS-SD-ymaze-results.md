---
type: experiment
area: hlb-sod1
status: active
created: 2026-11-05
summary: "NS-SD Y-maze after 2 days of SD, hand-scored: SA% SOD1 54.6 vs water 55.3, no detectable difference (CI -15 to +14); arm entries equal (35.6 vs 35.2); neither group above chance; n = 5 vs 5"
cohort: NS-SD + NW-SD (HLBNSSD51-55, HLBNWSD56-60)
tags: [behaviour, y-maze, sleep-deprivation, ns-sd, nw-sd]
---

# 2026-11-05: NS-SD Y-maze after sleep deprivation, hand-scored results

> [!abstract] TL;DR
> - **SOD1 vs water after 2 days of SD (5 vs 5):** spontaneous alternation (SA) 54.6 vs 55.3 %, difference −0.7 points
>   (95 % CI −15.4 to +14.0, Mann-Whitney p = 1.00). No detectable SOD1 difference; the CI is wide.
> - **Arm entries** 35.6 vs 35.2 (p = 0.55). The extra activity of SOD1 mice in the rested HLBNSL cohort
>   (48.2 vs 38.4, p = 0.063) is not seen here.
> - **Neither group alternates above chance** after SD (Wilcoxon vs 50 %: water p = 0.44, SOD1 p = 0.31), where the
>   rested HLBNSL mice were at 60-63 %. Different cohorts, so this is consistent with an SD effect on working memory,
>   not proof of one.
> - SA % does not follow the real SD length (r = +0.05, n = 10), but the start times are 15-min slots, not clock reads.

## Data
- Clips: 480 s from the moment the hand is out of view, cut 2026-11-04 (BEHAVIOR_SOP changelog), office PC
  `~/ymaze_nssd/trial_8min/`.
- Sequences hand-scored by Andrea (same rules as HLBNSL, all four paws, re-entries kept):
  [[2026-11-04-NS-SD-ymaze-hand-scoring]]. HLBNWSD57 was typed with `n` for `b` throughout and corrected on Andrea's
  request.
- Test order 51, 56, 52, 57, 53, 58, 54, 59, 55, 60 from 15:00, about 15 min per mouse (60 last, Andrea 11-05).
  Start times and so SD length are approximate.
- Code: `nanotag/analysis/behavior/ymaze_nssd.py nanotag/analysis/out/HLBNSSD/ymaze --vault`; the sheet
  `NSSD_ymaze_hand_scoring.csv`; outputs `NSSD_ymaze_results.csv`, `NSSD_ymaze_stats.txt`.
- Check: the HLBNSL block reproduces [[2026-10-25-HLBNSL-ymaze-hand-scored-results]] (SA 60.5 vs 62.8, p = 0.73;
  entries g +1.19, p = 0.063).

![[2026-11-04-NSSD-run2-ymaze.png]]

## Per mouse

| Mouse | Group | SA % | Arm entries | Alternations | Direct revisits | Indirect revisits | Start | SD h |
|---|---|---|---|---|---|---|---|---|
| HLBNSSD51 | SOD1 | 44.8 | 31 | 13 | 2 | 12 | 15:00 | 6.0 |
| HLBNWSD56 | water | 57.5 | 42 | 23 | 5 | 9 | 15:15 | 6.25 |
| HLBNSSD52 | SOD1 | 62.5 | 34 | 20 | 2 | 8 | 15:30 | 6.5 |
| HLBNWSD57 | water | 45.5 | 35 | 15 | 0 | 18 | 15:45 | 6.75 |
| HLBNSSD53 | SOD1 | 59.4 | 34 | 19 | 2 | 10 | 16:00 | 7.0 |
| HLBNWSD58 | water | 70.6 | 36 | 24 | 1 | 8 | 16:15 | 7.25 |
| HLBNSSD54 | SOD1 | 58.6 | 31 | 17 | 2 | 8 | 16:30 | 7.5 |
| HLBNWSD59 | water | 42.3 | 28 | 11 | 1 | 13 | 16:45 | 7.75 |
| HLBNSSD55 | SOD1 | 47.8 | 48 | 22 | 7 | 11 | 17:00 | 8.0 |
| HLBNWSD60 | water | 60.6 | 35 | 20 | 2 | 9 | 17:15 | 8.25 |

## Statistics (SOP section 5, each cohort on its own, never pooled)

| Cohort | Measure | water | SOD1 | SOD1 − water (95 % CI) | Hedges g | p (Mann-Whitney) |
|---|---|---|---|---|---|---|
| NS-SD (SD) | SA % | 55.3 ± 5.2 (n = 5) | 54.6 ± 3.5 (n = 5) | −0.7 (−15.4 to +14.0) | −0.06 | 1.000 |
| NS-SD (SD) | Arm entries | 35.2 | 35.6 | +0.4 (−8.7 to +9.5) | +0.06 | 0.548 |
| HLBNSL (rested) | SA % | 62.8 ± 2.4 (n = 5) | 60.5 ± 2.4 (n = 4) | −2.2 (−10.2 to +5.8) | −0.39 | 0.730 |
| HLBNSL (rested) | Arm entries | 38.4 | 48.2 | +9.9 (−4.0 to +23.7) | +1.19 | 0.063 |

SA % against 50 % (exact Wilcoxon): NS-SD water p = 0.438, SOD1 p = 0.312; HLBNSL water p = 0.062, SOD1 p = 0.125.

## Interpretation
- No detectable SOD1 effect on alternation after SD. With 5 vs 5 and SDs of 8-12 points, only a difference of about
  15 points could have been excluded, so this is not evidence of no effect.
- SD and rested arms are different batches (mice, treatment length, date): the lower SA after SD is "consistent
  with", never "caused by" SD (2026-10-30 decision, [[2026-10-30-NS-SD-two-day-SD-y-maze-only]]).
- Activity: arm entries do not support the HLBNSL activity trend after SD; that trend stays a trend.

## Still open
- [ ] Distance and speed from pose (`ymaze_pose.py`, runbook step 4), after validation on HLBNSL.
- [ ] `ymaze_2x2.py` (SOD1 x sleep interaction) needs the NS-SD distance column, so it waits for the pose step.
- [ ] Copy the clips to the NAS `Y_maze_HLBNSSD/trial_8min/`.

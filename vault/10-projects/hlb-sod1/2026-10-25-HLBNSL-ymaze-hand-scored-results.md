---
type: experiment
area: hlb-sod1
status: done
created: 2026-10-25
summary: "HLBNSL Y-maze final, hand-scored: SA% SOD1 60.5 vs water 62.8, no detectable difference; SOD1 more arm entries (g 1.2, p = 0.06); n = 4 vs 5"
tags: [behaviour, y-maze, nanotag, hlbnsl]
---

# 2026-10-25: HLBNSL Y-maze, hand-scored results (final)

> [!abstract] TL;DR
> - Both groups alternate above chance: SOD1 60.5 ± 2.4 %, water 62.8 ± 2.4 % (mean ± SEM).
> - No detectable SOD1 vs water difference in alternation: −2.2 points (95 % CI −10.3 to +5.8).
> - SOD1 mice made more arm entries (48.3 vs 38.4, Hedges g +1.19, p = 0.063), with more distance
>   and speed in the same direction: an activity trend, not a memory effect. It also held in the
>   EthoVision-only analysis.
> - Sleep-normal half of the 2x2 only; reported separately from EEG and nanotag sleep data.
> - Replaces the provisional EthoVision-only note [[2026-10-25-HLBNSL-ymaze-results]].

## Method
- Same 9 mice and videos as [[2026-10-25-HLBNSL-ymaze-results]] (480 s from door closed).
- **SA% and arm entries: hand-scored** by Andrea (all four paws in the arm, re-entries counted),
  sequences in [[2026-10-25-HLBNSL-ymaze-hand-scoring]], scored with `metrics.py`.
  Andrea's decision 2026-10-25: EthoVision SA% per mouse moved by up to 13 points when the zones
  were redrawn, so it is not used as the endpoint.
- **Distance and velocity: EthoVision**, trials 10-18 (arenas `…b`: centre triangle plus arm zones
  starting about 3 cm into each arm), gray scaling 0-82, centre-point, no smoothing. Distance uses
  the 35 cm design arm length (not measured).
- `nanotag/analysis/behavior/ymaze_report.py --trials 10-18 --hand <hand-scoring note>`, output in
  `Desktop\Nanotag videos upright\Y-maze\export\report_hand\` on `kaist-bilab-win`.

## Results

| Mouse | Group | SA % | Arm entries | Alternations | Direct / indirect revisits | Distance (m) | Velocity (cm/s) |
|---|---|---|---|---|---|---|---|
| HLBNSSL41 | SOD1 | 63.2 | 59 | 36 | 3 / 15 | 41.9 | 8.73 |
| HLBNSSL42 | SOD1 | 64.7 | 53 | 33 | 2 / 14 | 39.0 | 8.12 |
| HLBNSSL44 | SOD1 | 60.5 | 40 | 23 | 2 / 11 | 29.3 | 6.10 |
| HLBNSSL49 | SOD1 | 53.8 | 41 | 21 | 2 / 14 | 30.3 | 6.32 |
| HLBNWSL45 | water | 66.7 | 47 | 30 | 1 / 13 | 34.8 | 7.25 |
| HLBNWSL46 | water | 62.2 | 39 | 23 | 2 / 10 | 32.3 | 6.73 |
| HLBNWSL47 | water | 69.4 | 38 | 25 | 0 / 11 | 30.3 | 6.32 |
| HLBNWSL48 | water | 58.8 | 36 | 20 | 1 / 12 | 28.8 | 6.01 |
| HLBNWSL50 | water | 56.7 | 32 | 17 | 0 / 13 | 25.8 | 5.37 |

Statistics (BEHAVIOR_SOP section 5):
- SA% vs 50 % (exact Wilcoxon): SOD1 p = 0.125, water p = 0.062, the smallest p possible at
  n = 4 and n = 5. Every mouse is above 50 %.
- SOD1 vs water (exact Mann-Whitney U; mean difference, Welch 95 % CI, Hedges g):
  - SA%: −2.21 points (−10.25 to +5.83), g −0.39, p = 0.73
  - arm entries: +9.85 (−3.97 to +23.67), g +1.19, p = 0.063
  - distance: +4.7 m (−4.6 to +14.0), g +0.86, p = 0.41
  - velocity: +0.98 cm/s (−0.96 to +2.93), g +0.86, p = 0.41
- Control check, arm entries vs SA%: Pearson r = +0.38, p = 0.32.

![[2026-10-25-HLBNSL-ymaze-hand-fig1-endpoints-v2.png]]
![[2026-10-25-HLBNSL-ymaze-hand-fig2-checks-v2.png]]

Figures v2 (2026-10-25): control (water) on the left; same data as the first version.

## EthoVision against the hand scores (gap zones, 3 cm exit threshold)
- Entries: EthoVision +0 to +7 per mouse (mean +2.9).
- SA%: EthoVision **lower in 8 of 9 mice**, mean |difference| 5.3 points, up to 11.2; Pearson r +0.88.
  The mouse ranking agrees, the per-mouse value does not. The EthoVision group means
  (57.4 vs 55.7) stay above chance with no group difference, so the conclusion is the same.

## Reading
- Spontaneous alternation is normal in both groups (about 60 %, every mouse above chance).
  SOD1 did not change it in sleep-normal mice; the CI still allows a difference of about
  10 points either way, so this is "none detectable at n = 4 vs 5", not "shown equal".
- Andrea's impression while scoring that water mice alternate a little better matches the
  direction (−2.2 points) but is well inside the noise.
- The arm-entry difference is the largest effect and goes with distance and speed. It held in
  both the EthoVision-only and the hand-scored analysis, so it is worth checking in batch 2,
  where it can be tested in the 2x2. HLBNSSL41 and 42 are the most active mice.
- Notes from scoring: 42 seemed to avoid arm A, 44 spent a lot of time in the centre, 49 looked
  like a weak performer (lowest SOD1 SA%, 53.8 %).

## Still open
- Batch 2 (HLBNSD): fixed overhead camera, hand-score SA% and entries the same way, EthoVision
  with gap zones for distance and velocity. Then the two-way ANOVA on both batches.
- Measure the real arm length (distance and velocity are scaled to the 35 cm design value).

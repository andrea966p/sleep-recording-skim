---
type: experiment
area: hlb-sod1
status: active
created: 2026-10-25
summary: "HLBNSL Y-maze (2026-09-30), EthoVision, zone exit threshold 3 cm (provisional): both groups alternate about 60 %, no SOD1 vs water difference; n = 4 vs 5"
tags: [behaviour, ethovision, y-maze, nanotag, hlbnsl]
---

# 2026-10-25: HLBNSL Y-maze results (provisional)

> [!abstract] TL;DR
> - Both groups alternate above chance: SOD1 61.6 ± 2.0 %, water 58.6 ± 2.2 % (mean ± SEM).
> - No detectable SOD1 vs water difference in alternation (diff +3.0 points, 95 % CI −4.1 to +10.0).
> - SOD1 mice made more arm entries (57.5 vs 48.6, Hedges g +1.23, p = 0.06): a locomotor
>   trend, not a cognitive one; distance and speed point the same way.
> - **Provisional**: the 3 cm zone exit threshold is not yet validated by hand scoring.
> - This is the sleep-normal half of the 2x2. It cannot answer the SOD1 x sleep-deprivation
>   question alone. Reported separately from EEG and nanotag sleep data.

## What was done
- Mice: HLBNSSL41, 42, 44, 49 (SOD1) and HLBNWSL45, 46, 47, 48, 50 (water); 43 died 2026-09-28.
  Run order on 2026-09-30 was 41, 42, 44, 49, 45, 46, 47, 48, 50 (mouse cards, Andrea 2026-10-24).
- Videos cut to 480 s from door closed (Andrea's times), upright 30 fps, tracked in EthoVision XT
  11.5.1026, gray scaling 0-82, centre-point, one arena per video. Procedure:
  [[ethovision-11-5-y-maze-tracking]]. Rules: `nanotag/analysis/behavior/BEHAVIOR_SOP.md`.
- Tracking: 0.0 % subject not found and 0 missed samples in all 9 trials.
- Scoring: EthoVision **Zone alternation** on arms A, B, C with **zone exit threshold 3 cm**.
  SA% = Alternations / Max alternations x 100; arm entries = Max alternations + 2.
- Report: `nanotag/analysis/behavior/ymaze_report.py`, output in
  `Desktop\Nanotag videos upright\Y-maze\export\report_3cm\` on `kaist-bilab-win`.

## Why a 3 cm threshold
The arm zones were drawn touching the centre triangle (no gap, unlike the SOP), and arenas 41
and 50 have no centre zone. With no threshold, the centre-point flickering across the arm
border counts as 36-44 extra same-arm re-entries per mouse, and SA% falls to about 20 %, which
is what random choice gives. EthoVision's zone exit threshold is Noldus's documented remedy.
Mean SA% by threshold (SOD1 / water): 1 cm 44.5 / 44.6, 2 cm 56.6 / 55.1, **3 cm 61.6 / 58.6**,
4 cm 62.6 / 59.0. It plateaus from 3 cm, and direct revisits drop from 6-14 to 0-3 per mouse.
The centre zone does not enter the alternation calculation.

## Results (threshold 3 cm)

| Mouse | Group | SA % | Arm entries | Direct revisits | Distance (m) | Velocity (cm/s) |
|---|---|---|---|---|---|---|
| HLBNSSL41 | SOD1 | 67.2 | 63 | 1 | 40.8 | 8.51 |
| HLBNSSL42 | SOD1 | 58.3 | 62 | 1 | 37.6 | 7.84 |
| HLBNSSL44 | SOD1 | 62.0 | 52 | 3 | 28.2 | 5.87 |
| HLBNSSL49 | SOD1 | 58.8 | 53 | 0 | 29.7 | 6.19 |
| HLBNWSL45 | water | 56.4 | 57 | 1 | 34.1 | 7.10 |
| HLBNWSL46 | water | 66.0 | 49 | 2 | 30.7 | 6.40 |
| HLBNWSL47 | water | 58.7 | 48 | 2 | 30.1 | 6.27 |
| HLBNWSL48 | water | 59.2 | 51 | 0 | 28.0 | 5.84 |
| HLBNWSL50 | water | 52.8 | 38 | 0 | 25.2 | 5.26 |

Statistics (BEHAVIOR_SOP section 5):
- SA% vs 50 % (exact Wilcoxon): SOD1 p = 0.125, water p = 0.062. These are the **smallest p
  values possible** with n = 4 and n = 5: every mouse is above 50 %, but the test cannot reach
  0.05 at this n.
- SOD1 vs water (exact Mann-Whitney U; mean difference, Welch 95 % CI, Hedges g):
  - SA%: +2.96 points (−4.10 to +10.01), g +0.58, p = 0.41
  - arm entries: +8.9 (−1.1 to +18.9), g +1.23, p = 0.063
  - distance: +4.5 m (−4.7 to +13.6), g +0.84, p = 0.41
  - velocity: +0.93 cm/s (−0.97 to +2.83), g +0.84, p = 0.41
- Control check, arm entries vs SA%: Pearson r = +0.48, p = 0.19.

![[2026-10-25-HLBNSL-ymaze-fig1-endpoints.png]]
![[2026-10-25-HLBNSL-ymaze-fig2-checks.png]]

## Reading
- Working memory as measured by spontaneous alternation looks normal in both groups (about 60 %,
  every mouse above chance, typical for C57BL/6). SOD1 did not change it in sleep-normal mice;
  the CI still allows a difference of up to about 10 points either way, so "no difference" here
  means "none detectable at n = 4 vs 5", not "shown to be equal".
- The arm-entry difference is the largest effect (g 1.2) and goes with more distance and speed,
  so it is activity, not memory. Two SOD1 mice (41, 42) drive it. Treat it as a hypothesis for
  batch 2, not a finding.
- HLBNWSL50 is the least active (38 entries) and closest to chance (52.8 %).
- Distance and velocity use the 35 cm design arm length, not a measured one (secondary endpoints).

## Still open
- Hand-score the arm sequence of 3 videos (41, 46, 50) and confirm or change the 3 cm threshold;
  then this note loses "provisional".
- Batch 2 (HLBNSD, Y-maze 2026-10-31 onward): fixed overhead camera, one arena, same threshold, so the
  2x2 two-way ANOVA can run on both batches.
- Measure the real arm length.

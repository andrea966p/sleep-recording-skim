---
type: experiment
area: hlb-sod1
status: active
created: 2026-10-25
summary: "HLBNSL NOR day 1 open field (2026-10-01), YOLO pose model2: SOD1 mice moved more (64 vs 51 m, g +1.7, p = 0.11) and stayed still less; no difference in centre time or thigmotaxis. Provisional: model1 cross-check and floor size pending"
tags: [behaviour, oft, nor, pose, hlbnsl]
---

# 2026-10-25: HLBNSL open field (NOR day 1) results (provisional)

> [!abstract] TL;DR
> **Question.** Did SOD1 change locomotion, anxiety-like behaviour or habituation in the 10 min
> open field on NOR day 1, and is anything there that the NOR day 2 results must account for?
> **Answer (provisional).**
> - **Locomotion: SOD1 mice were more active.** Distance 63.9 vs 51.1 m (g +1.66, p = 0.11),
>   immobility 66 vs 135 s (g −1.59, p = 0.06), centre entries 53 vs 37 (p = 0.06). Same direction
>   as the Y-maze arm entries ([[2026-10-25-HLBNSL-ymaze-hand-scored-results]]).
> - **Anxiety-like behaviour: no detectable difference.** Centre time 18.6 vs 15.9 % (p = 0.73),
>   thigmotaxis 29.8 vs 37.9 % (p = 0.41; the water mean is pulled up by HLBNWSL48).
> - **Habituation:** both groups dropped from minute 1 to minute 2, then held a plateau. SOD1
>   started higher (9.9 vs 7.3 m in minute 1) and ended level with water (5.6 vs 5.4 m).
> - **No arena position preference:** the time near the future object spots is close to even
>   in both groups (bias 0.61 vs 0.62).
> - With n = 4 vs 5 nothing reaches p < 0.05, and the smallest p possible is 0.016.
>   Provisional until model1 agrees and the floor size is measured.

> [!warning] 2026-10-25 (later): object spots re-measured, object-spot bias updated
> Andrea confirmed the box is a standard 50 x 50 cm, so the distances and speeds stand.
> The object spots were taken from one frame of HLBNSSL41 NOR-T1. They are now the mean of the
> 9 NOR-T1 clips (`nor_objects.py`): (14.1, 13.4) and (35.7, 37.0) cm. Only the object-spot bias
> changes: 41 0.71, 42 0.60, 44 0.53, 49 0.59, 45 0.67, 46 0.54, 47 0.63, 48 0.63, 50 0.59;
> SOD1 0.61 vs water 0.61, g −0.08, p = 0.73. The reading (no arena side preference) holds.
> Object geometry: [[2026-10-25-nor-day1-oft-feature-set]].

> [!warning] 2026-10-25 (night): "no arena position preference" was a misreading
> The object-spot bias is the share of the MORE-visited spot (0.5-1), so 0.61 says each mouse
> preferred one spot by about 61:39, whichever side it was. It is not evidence of no preference.
> By direction: share of object-spot time at the lower-right spot (where the novel object stood in
> every T2) is 0.54 on average; 6 of 9 mice above 0.5 (41 0.71, 42 0.60, 44 0.47, 49 0.59,
> 45 0.67, 46 0.46, 47 0.37, 48 0.37, 50 0.59). So a mild group pull to the lower right existed
> before any object was in the box. Consequence for NOR: [[2026-10-25-HLBNSL-nor-pose-results]].

> [!success] 2026-10-25 (night): model1 cross-check passed
> model1 (YOLOv12-small, 1440 px) on the same 9 clips agrees with model2 per mouse:
> Pearson r +1.000 distance, +0.999 centre time, +0.995 thigmotaxis, +0.996 immobility.
> model1 runs slightly offset in the same way for every mouse: distance +1.3 m (max 1.65 m,
> about 2 %), thigmotaxis +2.6 points (max 4.1), immobility −9.7 s (max 16.6 s), centre time
> −0.1 points (max 0.6). No mouse disagrees enough to need a look by eye.
> Every conclusion above holds under model1 (distance SOD1 65.4 vs water 52.3 m, g +1.68, p = 0.11;
> immobility p = 0.063; centre time p = 0.73; thigmotaxis p = 0.56). Centre entries reach p = 0.032
> under model1 (0.063 under model2): that depends on the tracker, so it is not treated as a finding.
> model2 stays the primary source (SOP changelog). The open check left is the floor scale
> ([[2026-10-25-nor-day1-oft-feature-set]]); the wall-rear proxy differs by up to 8 events per mouse
> between the models and stays unvalidated.
> Outputs: `OFT\features_model1.csv`, `OFT\report_model1\`, agreement in `OFT\report_model2\HLBNSL_oft_stats.txt`.

## Setup
- Mice: HLBNSSL41, 42, 44, 49 (SOD1) and HLBNWSL45, 46, 47, 48, 50 (water); 43 died 2026-09-28.
  Tested 2026-10-01 in the run order 41, 42, 44, 49, 45, 46, 47, 48, 50.
- Window: 600 s from the release of the mouse (Andrea's times, `OFT\door_times.csv`).
- Tracking: YOLO pose model2 (labmate, Ultralytics), body centre, 30 fps, floor mapped to
  50 x 50 cm per clip. Procedure: [[hlbnsl-oft-nor-pose-tracking]]. Feature definitions and
  why: [[2026-10-25-nor-day1-oft-feature-set]].
- Tracking quality: mouse on the floor in ≥ 99.97 % of frames in every clip; the model's top
  detection was the ring light outside the box in up to 5.4 % of frames (HLBNSSL42), all replaced
  by the on-floor detection.

## Result

| Mouse | Group | Distance (m) | Speed (cm/s) | Immobile (s) | Centre (%) | Centre entries | Thigmotaxis (%) | Last 3 / first 3 min | Object-spot bias |
|---|---|---|---|---|---|---|---|---|---|
| HLBNSSL41 | SOD1 | 74.1 | 12.35 | 26.2 | 17.6 | 59 | 33.4 | 0.68 | 0.71 |
| HLBNSSL42 | SOD1 | 68.7 | 11.44 | 22.7 | 27.5 | 65 | 27.0 | 0.86 | 0.61 |
| HLBNSSL44 | SOD1 | 60.4 | 10.07 | 95.8 | 19.4 | 48 | 30.4 | 0.87 | 0.54 |
| HLBNSSL49 | SOD1 | 52.5 | 8.74 | 117.7 | 10.1 | 41 | 28.2 | 0.75 | 0.57 |
| HLBNWSL45 | water | 49.5 | 8.26 | 156.8 | 13.6 | 43 | 37.5 | 0.88 | 0.69 |
| HLBNWSL46 | water | 55.1 | 9.18 | 87.7 | 14.3 | 39 | 25.8 | 1.05 | 0.57 |
| HLBNWSL47 | water | 52.9 | 8.82 | 126.1 | 24.3 | 42 | 28.7 | 0.77 | 0.62 |
| HLBNWSL48 | water | 52.8 | 8.80 | 142.8 | 7.6 | 27 | 59.9 | 1.54 | 0.63 |
| HLBNWSL50 | water | 45.1 | 7.51 | 160.7 | 19.6 | 36 | 37.4 | 1.08 | 0.59 |

SOD1 vs water (exact Mann-Whitney U; mean difference with Welch 95 % CI; Hedges g):
- distance +12.8 m (−1.5 to +27.1), g +1.66, p = 0.11
- mean speed +2.14 cm/s (−0.25 to +4.52), g +1.66, p = 0.11
- immobility −69 s (−141 to +3), g −1.59, p = 0.063
- centre time +2.8 points (−8.3 to +13.8), g +0.37, p = 0.73
- centre entries +15.9 (−0.2 to +31.9), g +1.64, p = 0.063
- thigmotaxis −8.1 points (−24.6 to +8.3), g −0.70, p = 0.41
- last 3 / first 3 min −0.27 (−0.63 to +0.09), g −1.06, p = 0.063
- object-spot bias −0.01 (−0.12 to +0.09), g −0.22, p = 0.56
- wall-rear proxy (unvalidated) 69 vs 61 events, p = 0.91

Habituation (per-mouse slope of distance per minute): SOD1 −0.23 m/min, 4 of 4 negative
(Wilcoxon vs 0 p = 0.125, the smallest possible at n = 4); water +0.005 m/min, 3 of 5 negative (p = 1.0).

![[2026-10-25-HLBNSL-oft-fig1-endpoints.png]]
![[2026-10-25-HLBNSL-oft-fig2-habituation.png]]

Body-centre track of HLBNSSL41 over the 600 s (red), centre zone (green), 5 cm wall band (inside
blue). Excursions just past the floor edge are rears against the wall:
![[2026-10-25-HLBNSL-oft-fig3-track-HLBNSSL41.png]]

## What it means / what it does not mean
- For NOR day 2, the SOD1 mice are more active. A larger total object exploration in SOD1 could be
  locomotor, not cognitive, so total exploration must be read against day 1 distance. d2 is a ratio
  and less exposed.
- No sign that SOD1 changed anxiety-like behaviour in the open field.
- The plateau after minute 2 in both groups means the arena was still being explored at the end of
  day 1; that is normal for a 10 min session and is the same for both groups.
- Day 1 shows no place preference for either object spot, so a T1 side bias on day 2 would not come
  from the arena itself.
- HLBNWSL48 spent 60 % of the session at the wall and 7.6 % in the centre, the most wall-bound mouse.
  Not an exclusion (the SOP has none for the OFT); note it if 48 is an outlier on NOR day 2.
- This is the sleep-normal half of the 2x2. Reported separately from EEG and nanotag sleep data.
- Distances in cm assume the inner floor is 50 x 50 cm. If the box is different, every distance
  and speed scales by the same factor, and the group comparison and the zone percentages do not change.

## Still open
- [ ] model1 cross-check on the same 9 clips (running 2026-10-25): agreement per mouse on distance and centre time.
- [ ] Measure the box floor (is it 50 x 50 cm?). [[2026-10-25-nor-day1-oft-feature-set]]
- [ ] Optional: track one OFT clip in EthoVision and compare the distance.
- [ ] Wall-rear proxy: validate on 3 hand-scored videos or drop it.

## Data
- `kaist-bilab-win`: `Desktop\Nanotag videos upright\OFT\` (`trial_10min\` clips, `arena\` floor
  corners and overlays, `pose\` model outputs, `features_model2.csv`, `report_model2\` with the
  stats text, per-mouse CSV and figures as PNG and PDF).
- Code: `nanotag/analysis/behavior/` `pose_infer.py`, `oft_arena.py`, `oft_features.py`, `oft_report.py`
  (uncommitted on 2026-10-25).

---
type: experiment
area: hlb-sod1
status: active
created: 2026-10-25
summary: "HLBNSL NOR (2026-10-02) scored from YOLO pose, provisional until hand scoring: d2 water +0.30, SOD1 +0.24, no group difference; the novel object stood in every T2 on the spot the mice already favoured, so most of d2 is side preference"
tags: [behaviour, nor, pose, hlbnsl]
---

# 2026-10-25: HLBNSL NOR from pose (provisional)

> [!abstract] TL;DR
> **Question.** Did the mice recognise the familiar object in T2 (d2 > 0), and did SOD1 change that?
> **Answer (provisional, pose scoring not yet validated against hand scoring).**
> - d2 water +0.30 ± 0.06, SOD1 +0.24 ± 0.16 (mean ± SEM); no group difference (p = 0.91).
>   No mouse is excluded under the SOP rules.
> - **Caveat that changes the reading:** the novel object stood at the lower-right spot in all 9 T2
>   trials, and the mice already favoured that spot: 54 % of day 1 object-spot time with no objects
>   in the box, 57 % of T1 exploration (two identical objects). In T2 the novel object got 64 %.
>   So most of d2 is a pre-existing side preference. The part that is recognition is the rise from
>   T1 to T2 at the same spot: 7 of 9 mice rose (water 5/5, SOD1 2/4), paired p = 0.074.
> - The SOP's d2 vs 0 tests therefore overstate recognition in this batch. The T1 → T2 change at the
>   same spot is the fairer test, and it is weak at n = 9.
> - Total exploration did not differ between groups in T1 (53 vs 48 s) or T2 (41 vs 47 s), and all
>   mice explored ≥ 35 s per trial (SOP minimum 20 s).

> [!warning] 2026-10-25 (night): model1 disagrees on the novel object
> model1 on the same 18 clips: T1 totals agree (r +0.996, model1 +3.3 s), the familiar object agrees
> (+0.6 s), but **model1 gives the novel blue prism +6.3 s per mouse** (max 8.7 s). So d2 is higher
> (water +0.36, SOD1 +0.33; per mouse r +0.98, +0.08 on average) and the T1 → T2 side check becomes
> 9/9 mice, p = 0.004 (model2: 7/9, p = 0.074). Group comparisons are unchanged (d2 p = 0.73).
> Where the gap comes from: the time with the nose within 2 cm of the prism is +10.4 s per mouse with
> model1, against +0.9 s at the red pyramid; the paw rule adds only 0.6 s. In 10 frames rendered where
> the two disagree (HLBNWSL46, 50), model1's nose sat off the snout toward the prism in about 8. The
> median nose-to-ears distance near the prism does not differ from elsewhere for either model, so the
> error is in a minority of frames. Reading: model1's nose may be pulled toward the blue prism; model2
> stays primary, and **the recognition result (side check) depends on the model** until the hand
> scoring decides. Outputs: `NOR-results\nor_*_model1.*`.

## Setup
- Mice: HLBNSSL41, 42, 44, 49 (SOD1) and HLBNWSL45, 46, 47, 48, 50 (water). 2026-10-02, T1 (two red
  pyramids) then T2 (lower-right pyramid replaced by a blue prism), run order 41, 42, 44, 49, 45,
  46, 47, 48, 50 (assumed the same as day 1, per the SOP changelog).
- Clips: 600 s from Andrea's start times (`NOR-T1|NOR-T2\door_times.csv`).
- Scoring: `nanotag/analysis/behavior/nor_explore.py` on YOLO pose model2, applying the SOP section 3 rule
  frame by frame: nose within 2 cm of the object's outline and the head (ear midpoint → nose) within
  45° of the object, or the nose within 0.5 cm; frames with the body centre on the object or a paw
  well inside its outline are excluded. Chewing cannot be seen from above and is not excluded.
  Procedure: [[hlbnsl-oft-nor-pose-tracking]]. Object geometry: [[2026-10-25-nor-day1-oft-feature-set]].
- Object outlines per clip from the colour of the objects (`nor_objects.py`), grown to include the
  blue prism's grey side face:
  ![[2026-10-25-HLBNSL-nor-fig3-object-outlines.png]]

## Result

| Mouse | Group | T1 total (s) | T1 lower-right share | T2 total (s) | T2 novel share | d2 | Novel latency (s) | Familiar latency (s) |
|---|---|---|---|---|---|---|---|---|
| HLBNSSL41 | SOD1 | 46.7 | 0.45 | 36.2 | 0.68 | +0.35 | 32.0 | 15.0 |
| HLBNSSL42 | SOD1 | 52.2 | 0.52 | 39.5 | 0.45 | −0.11 | 25.8 | 103.2 |
| HLBNSSL44 | SOD1 | 41.1 | 0.62 | 40.4 | 0.55 | +0.10 | 26.2 | 43.7 |
| HLBNSSL49 | SOD1 | 71.0 | 0.58 | 47.9 | 0.81 | +0.62 | 3.4 | 15.9 |
| HLBNWSL45 | water | 57.8 | 0.65 | 49.7 | 0.65 | +0.30 | 3.0 | 10.2 |
| HLBNWSL46 | water | 51.0 | 0.56 | 35.5 | 0.65 | +0.31 | 1.9 | 6.3 |
| HLBNWSL47 | water | 59.2 | 0.66 | 49.7 | 0.69 | +0.37 | 49.1 | 105.8 |
| HLBNWSL48 | water | 35.2 | 0.62 | 50.1 | 0.72 | +0.44 | 88.1 | 185.6 |
| HLBNWSL50 | water | 38.6 | 0.42 | 49.5 | 0.53 | +0.06 | 42.8 | 62.0 |

- d2 vs 0 (exact Wilcoxon): water p = 0.062 (the smallest possible at n = 5), SOD1 p = 0.375.
- SOD1 vs water (exact Mann-Whitney U): d2 p = 0.91; T1 total p = 0.73; T2 total p = 0.19;
  T1 location bias 0.57 vs 0.62, p = 0.19; distance in T1 and T2 the same (about 44 m, p = 0.91).
- Side check, lower-right share T1 → T2, all 9 mice: 0.565 → 0.636, paired Wilcoxon p = 0.074, 7/9 rose.
- Day 1 distance vs T2 total exploration: Spearman rho −0.63, p = 0.067 (more active mice on day 1
  explored the objects less in T2); vs T1 total: rho −0.05.

![[2026-10-25-HLBNSL-nor-fig1-endpoints.png]]
![[2026-10-25-HLBNSL-nor-fig2-side-check.png]]

## What it means / what it does not mean
- Not a SOD1 effect: d2, exploration and the T1 → T2 rise do not separate the groups at n = 4 vs 5.
- Not clean evidence of recognition either: d2 > 0 is mostly where the mice already went. Batch 2
  (HLBNSD) should put the novel object on the left for half of the mice (counterbalance), or the 2x2
  inherits the same confound.
- The day 1 lower-right pull (54 %) is weaker than in T1 (57 %), so the objects themselves, or
  something at that corner on day 2, may add to it.
- This is the sleep-normal half of the 2x2. Reported separately from EEG and nanotag sleep data.

## How this was checked
- Contact sheets of scored frames on 3 clips (2026-10-25): two rules were relaxed after looking (nose
  touching within 0.5 cm counts whatever the head angle; a paw must be 0.5 cm inside an outline to count
  as on the object).
- Independent code review on real data: 10/10 frames counted as exploration agreed with the rule by eye,
  8/10 near-object rejections agreed (the 2 misses were sniffs at 47-49° head angle, just past the 45°
  cut). It found two bugs that inflated novel exploration, both fixed before these numbers: an "ears
  over the object" rule that counted climbing over the low prism, and a prism outline missing its grey
  side face.
- No frame is counted for both objects; frame times match video time in every clip.

## Still open
- [ ] Hand-score the validation subset blind in BORIS (`NOR-blind\score_these_first.txt`, 4 clips),
  then compare per bout and per clip (exploration seconds, d2). Until then BORIS stays the SOP endpoint.
- [x] 2026-10-25 night: model1 cross-check done; disagrees on the novel object (callout above). The
  hand-scored subset must include T2 clips to settle which model to trust there (it does: 2 of 4).
- [ ] Counterbalance the novel side in batch 2.

## Data
- `kaist-bilab-win`: `Desktop\Nanotag videos upright\NOR-results\` (`nor_results_model2.csv`,
  `nor_bouts_model2.csv` with every bout, `nor_stats_model2.txt`, figures as PNG and PDF);
  `NOR-T1|NOR-T2\pose\`, `arena\objects.csv`.
- Code: `nanotag/analysis/behavior/nor_explore.py`, `nor_objects.py` (uncommitted on 2026-10-25).

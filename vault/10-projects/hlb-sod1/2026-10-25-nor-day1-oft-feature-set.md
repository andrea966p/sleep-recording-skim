---
type: decision
area: hlb-sod1
status: active
created: 2026-10-25
summary: "Which features the HLBNSL NOR day 1 (open field / arena habituation, 10 min) gives, how each is defined, and which ones the NOR day 2 results need"
tags: [behaviour, oft, nor, pose, hlbnsl]
---

# 2026-10-25: NOR day 1 (open field) feature set

> [!abstract] TL;DR
> - Day 1 of the NOR protocol is a 10 min open field in the empty NOR box (2026-10-01). It
>   habituates the mouse to the arena and doubles as the open-field test.
> - Day 1 gives **locomotion** (distance, speed, immobility), **anxiety-like behaviour** (centre
>   time and entries, thigmotaxis), **habituation** (distance per minute) and **arena position
>   preference** (quadrants, time near the spots where the day 2 objects will stand).
> - The NOR results need day 1 for interpretation, not for exclusion: the SOP exclusions
>   (< 20 s exploration, > 80 % T1 bias) stay the only ones.
> - Tracking is by the labmate's YOLO pose models, not EthoVision: [[hlbnsl-oft-nor-pose-tracking]].

## Decided
Rules already frozen in `nanotag/analysis/behavior/BEHAVIOR_SOP.md` section 2 and kept as they are:
10 min, 50 x 50 cm, centre zone = inner 25 x 25 cm, thigmotaxis = within 5 cm of a wall,
computed from the raw track (`metrics.thigmotaxis`). Code: `nanotag/analysis/behavior/oft_features.py`.

| Feature | Definition | Unit | NOR needs it? |
|---|---|---|---|
| Total distance | Body-centre path over 600 s, gaps not bridged | cm | Yes: locomotor covariate for T1/T2 total exploration (d2 is a ratio, so it is less exposed) |
| Mean speed | Distance / tracked time | cm/s | Yes, with distance |
| Immobility | Speed < 2 cm/s held ≥ 2 s; speed = body displacement across a centred 1 s window | s, bouts | Secondary: tells sedation or freezing from low drive |
| Centre time | Body centre in the inner 25 x 25 cm | s, % | Yes: anxiety-like read-out; the objects stand in the arena |
| Centre entries | Into the centre square with 1 cm hysteresis; the release position is not an entry | n | Yes, with centre time |
| Thigmotaxis | Tracked samples within 5 cm of a wall | % | Yes: the primary anxiety-like index |
| Distance per minute | 10 bins of 1 min, slope, last 3 / first 3 minutes | cm | Yes: habituation adequacy. A flat profile means the arena was still novel on day 2 |
| Quadrant occupancy | Share of tracked time per quadrant | % | Yes: reads a T1 side bias against a pre-existing place preference |
| Object-spot time | Nose within 5 cm of each future T1 object centre | s, bias 0.5-1 | Yes, same purpose |
| Wall-rear proxy | Nose projected > 1.5 cm outside the floor for ≥ 0.3 s (the head is raised against a wall) | n, s | No. **Unvalidated**: report only after hand-scoring rears on 3 videos |
| Tracking quality | Mouse found, body point confident, top detection rejected as off the floor | % | QC only |

Not extracted: **centre latency** (the mouse is released near the centre, so it is about 0 by
design); **grooming and unsupported rearing** (a top-down camera cannot see them reliably from
keypoints, and the NOR does not need them).

Object positions: in HLBNSSL41 NOR-T1 the two red pyramids stand on the diagonal at about
(14.2, 13.4) cm and (35.8, 35.9) cm from the top-left floor corner, measured by eye on one
frame (2026-10-25). The other 17 NOR videos are not measured yet.

> [!note] 2026-10-25 (later): all 18 NOR clips measured, and the box size confirmed
> Andrea: the box is a standard 50 x 50 cm, and the objects were placed 10 cm from each nearer wall.
> `nor_objects.py` (colour blob on the median frame, floor homography) finds, in every clip:
> | Object | Centre (cm) | Footprint edge to the two nearer walls (cm) |
> |---|---|---|
> | T1 upper left, red | 13.9-14.2, 13.2-13.6 | 12.2-12.5 / 12.0-12.4 |
> | T1 lower right, red | 35.6-35.9, 36.6-37.1 | 12.4-12.7 / 11.6-12.2 |
> | T2 upper left, red (familiar) | 14.2-14.3, 13.3-13.4 | 12.5-12.6 / 12.2 |
> | T2 lower right, blue (novel) | 37.2-37.3, 37.4-37.6 | 11.2-11.3 / 10.7-10.9 |
>
> So the footprint edges sit about 11-12.5 cm from the walls, not 10. The detected footprint is
> 2.9-3.5 cm across; shaded faces may fall outside the colour mask, which would put the true edge
> up to about 0.5 cm closer to the wall, still not 10. Perspective cannot explain
> it: a raised point projects outward, toward the wall, which would make the measured distance
> smaller. Whether "10 cm" means the edge or the centre, and how it was measured, is open with
> Andrea. It does not affect the features, which use the measured positions. The novel prism
> stands about 1.5 cm further into the corner than the red pyramid it replaced.
> Per-clip values: `<NOR-T1|NOR-T2>\arena\objects.csv`. Day 1 object spots now use the T1 means.

> [!note] 2026-10-25 (later): the 10 cm is to the object's edge (Andrea)
> A zoom on HLBNSSL41 NOR-T1 shows the colour mask covers each whole pyramid, so the 11-12.5 cm
> is not a detection artefact. Two explanations remain, not separable from these videos:
> placement tolerance (objects set at about 10 cm, landed 1-2.5 cm further in), or a scale error
> (the visible floor square smaller than 50 cm, which would overstate every distance by one
> factor; the group comparison and the zone percentages would not change).
> Check on batch 2 (HLBNSD, from 2026-10-31): put a ruler on the floor in one frame before the
> first trial, and measure the object-to-wall distance in the box.

## How the NOR results use day 1
- With n = 4 vs 5, no ANCOVA. Report day 1 group means with CIs, and Spearman correlations of
  day 1 distance and thigmotaxis against T1/T2 total exploration.
- The Y-maze already shows a SOD1 locomotor trend (more arm entries, g 1.2, p = 0.06:
  [[2026-10-25-HLBNSL-ymaze-hand-scored-results]]), so day 1 distance is needed before reading any
  difference in total object exploration as cognitive.
- Day 1 of batch 2 (HLBNSD) will be scored the same way, so the 2x2 has a matching baseline.

## Open decisions (needs Andrea)
- [x] 2026-10-25: Andrea, the box is a standard 50 x 50 cm. **Is the floor 50 x 50 cm?** All distances assume the inner floor square is the 50 cm
  side. The walls are tall and the camera close (rim about 785 px, floor about 532 px in
  HLBNSSL41), so the rim and the floor cannot both be used for scale. Measure the box.
- [ ] Immobility threshold 2 cm/s for ≥ 2 s is our default, not taken from a source.
- [ ] Wall-rear proxy: keep (and validate on 3 hand-scored videos) or drop.
- [ ] Fecal boli: countable on the last frame (`OFT\arena\end\`), but boli near the walls and under
  the mouse are missed by the automatic count; hand-count if wanted.

## References
Checked to exist by a search agent on 2026-10-25; only abstracts were read, and the link
between these papers and "OFT features as NOR covariates" is our reasoning.
- Leger et al. 2013, Nat Protoc 8:2531-2537, https://doi.org/10.1038/nprot.2013.155
- Antunes & Biala 2012, Cogn Process 13:93-110, https://pmc.ncbi.nlm.nih.gov/articles/PMC3332351
- Denninger, Smith & Kirby 2018, JoVE 141:e58593, https://www.jove.com/v/58593
- Seibenhener & Wooten 2015, JoVE 96:52434, https://pmc.ncbi.nlm.nih.gov/articles/PMC4354627
- Lueptow 2017, JoVE e55718, https://pmc.ncbi.nlm.nih.gov/articles/PMC5614391
- Ennaceur 2010, Behav Brain Res 215:244-254, https://doi.org/10.1016/j.bbr.2009.12.036

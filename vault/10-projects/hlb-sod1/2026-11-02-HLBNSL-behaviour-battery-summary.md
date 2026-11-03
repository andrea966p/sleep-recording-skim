---
type: experiment
area: hlb-sod1
status: active
created: 2026-11-02
summary: "HLBNSL (normal sleep) behaviour battery in one place: Y-maze, open field (NOR day 1) and NOR (2 h retention, 2-day protocol), with the reasons for the 2-day design and the 2 h interval; no detectable SOD1 effect on any cognitive measure, SOD1 more active, n = 4 vs 5"
tags: [behaviour, y-maze, oft, nor, hlbnsl]
---


> [!info] 2026-11-04, Andrea: the HLBNSL NOR is taken as a valid recognition test
> The 57 % T1 share at the later novel spot (7/9 mice above 50 %, not significant) is not a preference at n = 9, and the
> spot share rose T1 → T2 in 9/9 mice (model 1, p = 0.004). Report wording updated in [[2026-11-03-hlb-sod1-report-draft-v02]];
> object identity not counterbalanced stays as a limitation.

# 2026-11-02: HLBNSL behaviour battery, methods and results

> [!abstract] TL;DR
> - **Battery (normal sleep arm, no SD):** Day 0 Y-maze, Day 1 open field (which is also the NOR
>   habituation), Day 2 NOR training (T1) and test (T2) 2 h apart, then sampling.
> - **Why 2 days and 2 h, not the usual 3 days and 24 h:** the 2-day form is a standard variant
>   (Leger et al. 2013); 2 h tests short-term recognition memory, keeps T1, T2 and sampling in one
>   afternoon at matched clock time, and keeps the post-training sleep out of the test, which matters
>   for the sleep-deprived arm of the 2x2 (Palchykova et al. 2006). Reasons below.
> - **Results:** no detectable SOD1 effect on Y-maze alternation or NOR d2; SOD1 mice were more active
>   in both the Y-maze and the open field (trend, p 0.06-0.11). Mice explored the novel object more
>   (9/9, p = 0.004), but novelty is confounded with object identity and side in this batch.
> - n = 4 SOD1 vs 5 water: every comparison is underpowered. Reported separately from EEG and
>   nanotag sleep data.

## Mice and schedule
- HLBNSSL41, 42, 44, 49 (SOD1) and HLBNWSL45, 46, 47, 48, 50 (water); HLBNSSL43 died 2026-09-28.
  Normal sleep: undisturbed from 09:00 until the move to the holding room. Lights 09:00-21:00 (ZT0 = 09:00).
- Each test day: cages to the holding room at 14:30 (30 min), tests from 15:00 (ZT6), one mouse at a
  time. Protocol: `Acute_SD_Behavioral_Protocol` (Day 0 to Day 2), the same schedule as the SD arm.

| Day | Date | Test | Duration, setup |
|---|---|---|---|
| 0 | 2026-09-30 | Y-maze spontaneous alternation | 8 min free exploration, 35 cm arms, 70 % ethanol between mice |
| 1 | 2026-10-01 | Open field = NOR habituation | 10 min, empty 50 x 50 cm arena, 20 lux |
| 2 | 2026-10-02 | NOR T1 → 2 h in the home cage → NOR T2 → sampling | T1 10 min, two identical red pyramids; T2 10 min, one pyramid + a blue prism (novel) at the same spots; sampling straight after each mouse's T2 |

## Why NOR runs over 2 days with a 2 h retention interval
The 2 h interval and the 2-day layout come from the lab protocol (`Acute_SD_Behavioral_Protocol`,
also used for the SD arm). The reasons below are ours, with the literature that supports each one.

1. **Two days is a standard variant, not a shortcut.** The common NOR protocol runs over 3 days:
   habituation, training, then a test 24 h later (Lueptow 2017). Leger et al. (2013) standardised three
   variants that differ only in habituation (3 days, 1 day or none). With a short interval between
   sessions, the 1-day-habituation variant takes 2 days: habituation on day 1, training and test on
   day 2. That is our design.
2. **The habituation session is our open field.** The 10 min in the empty arena on day 1 is scored as an
   open field test (locomotion, centre time, thigmotaxis). So one session gives both NOR habituation and
   a locomotor and anxiety-like readout, with no extra handling day.
3. **2 h tests short-term recognition memory.** Shortening the retention interval tests short-term
   memory; lengthening it tests long-term memory (Lueptow 2017). So our NOR measures whether the mice
   encode the familiar object and recognise it a few hours later. It does not test memory consolidated
   overnight.
4. **T1, T2 and sampling fit in one afternoon at matched clock time.** Tissue is taken straight after
   each mouse's T2 (about ZT8-10), so every mouse is sampled at a similar time of day and in the same
   state after the test. This matters for the oxidative-stress assays. A 24 h interval would add a day
   and a night before sampling.
5. **The 2 h keep post-training sleep out of the test, which keeps the 2x2 comparable.** Sleep after
   training consolidates object recognition memory. In mice, 6 h of SD right after training abolished
   recognition 24 h later, while the same SD 6 h later did not (Palchykova et al. 2006). With a 24 h
   interval, the sleep after T1, and in the SD arm where each mouse's SD fell relative to its own T1,
   would become part of what is measured. With 2 h, both arms are tested on encoding and short-term
   retention after their sleep history, with the 2 h spent resting in the home cage (no SD, Andrea
   2026-10-19).
6. **Limitation that comes with it:** a deficit only in long-term, sleep-dependent consolidation
   would be missed by a 2 h test. If that question matters, it needs a separate 24 h cohort.

## Scoring
- **Y-maze:** spontaneous alternation (SA %) and arm entries hand-scored by Andrea (all four paws in the
  arm, re-entries counted); distance and speed from EthoVision XT 11.5.
  [[2026-10-25-HLBNSL-ymaze-hand-scored-results]]
- **Open field:** YOLO pose model2, cross-checked with model1 (r ≥ 0.995 per mouse). Centre = inner
  25 x 25 cm; thigmotaxis = within 5 cm of a wall. [[2026-10-25-HLBNSL-oft-day1-results]]
- **NOR:** exploration = snout directed at the object and within 2 cm, sniffing, whisking or touching,
  including with the forepaws resting on it; on top of it, climbing over it, and rearing with the head
  above or past it are excluded (`BEHAVIOR_SOP.md` section 3, revised 2026-11-02,
  [[2026-11-02-nor-forepaw-rule-literature-review]]). Scored by two YOLO pose models and validated
  against blinded hand scoring in BORIS (6 clips, 2 raters, 2 clips scored by both, frame kappa between
  raters 0.76). d2 = (novel − familiar) / (novel + familiar).
  [[2026-11-02-HLBNSL-nor-hand-validation-and-calibration]]

## Results
| Test | Measure | SOD1 (n = 4) | Water (n = 5) | SOD1 vs water |
|---|---|---|---|---|
| Y-maze | SA % | 60.5 ± 2.4 | 62.8 ± 2.4 | −2.2 points (95 % CI −10.3 to +5.8) |
| Y-maze | arm entries | 48.3 | 38.4 | g +1.19, p = 0.063 |
| Open field | distance (m) | 63.9 | 51.1 | g +1.66, p = 0.11 |
| Open field | immobility (s) | 66 | 135 | g −1.59, p = 0.06 |
| Open field | centre time (%) | 18.6 | 15.9 | p = 0.73 |
| Open field | thigmotaxis (%) | 29.8 | 37.9 | p = 0.41 |
| NOR | d2, model1 | +0.34 ± 0.13 | +0.37 ± 0.05 | p = 0.73 |
| NOR | d2, model2 | +0.25 ± 0.16 | +0.31 ± 0.06 | p = 0.91 |

Mean ± SEM; Mann-Whitney exact unless stated; numbers from the linked result notes. No mouse was
excluded from NOR (all explored at least 20 s per trial).

**Reading.**
- **Working memory (Y-maze):** both groups alternate above chance (50 %); no detectable SOD1 effect.
- **Activity:** SOD1 mice entered more arms, moved further and stayed still less. Two tests point the
  same way, but neither reaches p < 0.05 at n = 4 vs 5. Anxiety-like measures do not differ.
- **Recognition memory (NOR):** pooled, the mice explored the novel object more (model1 9/9 mice,
  p = 0.004; model2 8/9, p = 0.020; about two thirds of T2 time). But the novel object was the blue prism
  at the lower-right spot in every T2, a spot the mice already favoured in T1. The share of time at that
  spot rose from T1 to T2 (model1 9/9, p = 0.004; model2 7/9, p = 0.074), so the spot alone does not
  explain it, but novelty cannot be separated from an intrinsic preference for the prism.
- **SOD1 vs water:** no difference in d2 detected, robust to model and scoring rule; the 95 % CI is about
  ±0.45 in d2, so this is underpowered, not "no effect".

## Still open
- Batch 2 with NOR, if it runs: counterbalance the novel object's identity and side across mice and
  groups.
- Pool batches for the SOD1 comparison, n from a power calculation.

## References
- Leger M, et al. Object recognition test in mice. Nat Protoc 2013;8:2531-7. doi:10.1038/nprot.2013.155
  (abstract read: the three habituation variants, 4, 2 or 1 day with a short intersession interval).
- Lueptow LM. Novel object recognition test for the investigation of learning and memory in mice.
  J Vis Exp 2017;(126):55718. doi:10.3791/55718 (abstract read: 3-day standard; shorter interval for
  short-term memory, longer for long-term).
- Palchykova S, et al. Sleep deprivation impairs object recognition in mice. Neurobiol Learn Mem
  2006;85:263-71. doi:10.1016/j.nlm.2005.11.005 (abstract read).

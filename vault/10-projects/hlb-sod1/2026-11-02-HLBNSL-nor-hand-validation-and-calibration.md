---
type: experiment
area: hlb-sod1
status: active
created: 2026-11-02
summary: "HLBNSL NOR: pose scoring checked against blinded hand scoring (6 clips, 2 raters, 2 clips by both) under the revised forepaw rule; raters agree (frame kappa 0.76); d2 agrees, absolute seconds under-count; no SOD1 effect detected (underpowered); recognition not established (novel object confounded with object and side); independent review included"
tags: [behaviour, nor, validation, pose, hlbnsl]
---

# 2026-11-02: HLBNSL NOR, hand validation, calibration and final analysis

> [!abstract] TL;DR
> **Question.** Does the YOLO pose scoring of NOR agree with blinded hand scoring, and what does the
> batch then say about recognition and SOD1?
> **Answer.**
> - **d2 agrees:** pose vs hand d2 within 0.02-0.08 on the hand-scored T2 clips (model1).
> - **Seconds do not:** pose counts 4-6 s less per object than the hand (10-25 %). A fitted gap-fill
>   correction did not transfer to the second rater (−4 s left) and is not stable, so it stays a
>   sensitivity analysis. Published seconds stay rule-based.
> - **Hand presses lag the model by 0.53 s (rater 1) and 0.60 s (rater 2).** The model's timing is kept.
> - **SOD1 vs water d2: no difference detected** (model1 +0.34 vs +0.37, p = 0.73; model2 p = 0.91),
>   but the 95 % CI is about ±0.45: underpowered, not "no effect".
> - **Recognition is not established:** the novel object was always the blue prism, always at the
>   lower-right spot the mice already preferred. The location-corrected test depends on the model.
> - **Raters agree (added later on 2026-11-02):** on the 2 clips both scored, frame kappa 0.76, ICC(A,1) 0.93,
>   rater 2 +3.3 s per object; hand d2 +0.32 vs +0.42 on the one T2 clip.
> - **The novel object got more exploration, pooled:** 9/9 mice d2 > 0 (model1, p = 0.004; model2 8/9,
>   p = 0.020), about 2/3 of T2 time. Per group (n = 4, 5) no test can reach p < 0.05.
>   What this preference is (novelty, the prism, the spot) is the confound below.
> - An independent reviewer agent checked the workflow; its findings are folded in below.

## Data
- Hand scoring (BORIS 9.15.0, blinded codes, revised forepaw rule of BEHAVIOR_SOP.md section 3):
  rater 1 (Andrea) NOR_247, 685, 899, 936; rater 2 (another lab member) NOR_238, 554. Rater 2 did not
  score the planned overlap clips NOR_247 and NOR_685 at first; they scored them later the same day (see
  [[#Agreement between raters (added 2026-11-02, later)]]).
- Pose: model1 and model2 re-scored 2026-11-02 under the revised rule (`~/nor-scoring/.pose/forepaws_count/`).
- Code: `nor_hand_vs_pose.py` (comparison), `nor_calibrate.py` (lag, gap fill, final statistics).
  Outputs on the office PC: `~/nor-scoring/.compare_2026-11-02/`, `~/nor-scoring/.calibration_2026-11-02/`
  (not in git; they name mice).

## Hand vs pose
| | model1 | model2 |
|---|---|---|
| rater 1, 4 clips: ICC(A,1) of seconds per object, as scored | 0.82 | 0.73 |
| rater 1: bias (pose − hand) | −4.0 s | −5.5 s |
| rater 2, 2 clips: bias | −7.8 s | −9.0 s |
| frame kappa at lag 0 / with each rater's lag removed (rater 1) | 0.46 / 0.71 | 0.45 / 0.70 |
| hand lag, rater 1 / rater 2 | 0.53 / 0.60 s | 0.53 / 0.60 s |
| d2 difference on hand-scored T2 clips | +0.01 to +0.06 | −0.11 to +0.00 |

- **Lag.** The lag that maximises frame kappa is the same at both gap settings, so it is not confounded
  with the gap; it does not change seconds. It was chosen on the same data, so the lag-corrected kappa
  is optimistic; whether the hand presses late or the pose leads (counting the approach) is untested.
- **Under-count.** Hand bouts are fewer and longer (median 0.7-1.3 s, against 0.4-0.7 s for model2).
  Hand scorers bridge short pauses the frame rule does not count.
- **Gap fill (sensitivity only).** Joining same-object bouts closer than 1.7-1.8 s and counting the gap
  as exploration raises ICC on the fit clips to 0.95 (model1) / 0.91 (model2), but leaves −4.1 / −4.3 s
  on rater 2's clips, and leave-one-clip-out moves the best gap to the grid edge (3.0 s). On 4 or 8
  points ICC mostly reflects the spread between objects, so report bias and limits of agreement, not ICC.
- **Rater vs clip.** With no clip scored by both raters, the −4 s on the test clips cannot be split into
  rater and clip effects.

## Final NOR analysis (9 mice, no exclusions, rule-based seconds)
| | model1 | model2 |
|---|---|---|
| d2 water (n = 5) | +0.37 ± 0.05 | +0.31 ± 0.06 |
| d2 SOD1 (n = 4) | +0.34 ± 0.13 | +0.25 ± 0.16 |
| d2 SOD1 vs water, Mann-Whitney | p = 0.73 | p = 0.91 |
| side check: lower-right share T1 → T2 (novel) | 0.56 → 0.68, 9/9 rose, p = 0.004 | 0.57 → 0.64, 7/9 rose, p = 0.074 |
| side check with gap fill 1.7-1.8 s | 7/9, p = 0.027 | 6/9, p = 0.055 |

(mean ± SEM; Wilcoxon exact; minimum possible p is 0.0625 at n = 5 and 0.125 at n = 4, so the
per-group tests against 0 cannot reach 0.05.)

## What can and cannot be claimed (from the independent review)
- **Can:** pose d2 tracks blinded hand d2; the SOD1 vs water d2 comparison is robust to model, rule
  and gap (p 0.73-1.0); no SOD1 difference detected at n = 4 vs 5, wide CI (difference −0.03,
  Welch 95 % CI −0.48 to +0.41).
- **Cannot:** that either group shows recognition memory (novel = blue prism = lower-right spot in every
  T2; the location-corrected test ranges p 0.004-0.30 across model and gap; an intrinsic preference for
  the low blue prism cannot be corrected for); that SOD1 "does not affect" recognition; that the pose
  seconds are validated in absolute terms.
- Circularity to state: the forepaw rule was revised after rater 1 had already scored that way.

> [!note] 2026-11-02, later: Andrea counted forepaw contact from the first clip, so all hand scoring
> was done under the final rule; the SOP text was revised to match what the scorer already did, it
> did not change the scoring. State it that way in the methods.

## Agreement between raters (added 2026-11-02, later)
Rater 2 scored NOR_247 (T2) and NOR_685 (T1), already scored by rater 1. Computed inline with the
functions of `nor_hand_vs_pose.py` (`hand_bouts`, `frames`, `kappa`, `agreement`).

| | value |
|---|---|
| frame kappa, 30 Hz, none / object 1 / object 2 | 0.76 (best shift 1 frame: no lag between raters) |
| seconds per object (4 points): ICC(A,1), r | 0.93, 0.99 |
| bias rater 2 − rater 1, limits of agreement | +3.3 s, −6.2 to +12.8 s |
| bouts, rater 1 / rater 2 | 46 / 51 (NOR_247), 38 / 44 (NOR_685) |
| hand d2 on NOR_247, rater 1 / rater 2 | +0.32 / +0.42 |

Rater 2 counts more on the B / novel object (+5.8 and +8.9 s), not on the other object. Pose vs rater 2
on all 4 of their clips: bias −8.3 s (model1), −9.6 s (model2), frame kappa 0.47 / 0.46; d2 within
−0.14 to +0.08 of hand on the 2 T2 clips. So pose under-counts against both raters, more against rater 2.
Kappa 0.76 between raters is the ceiling the pose kappa (0.46-0.47 as scored, about 0.7 lag-corrected)
should be read against. n = 2 clips: indicative only.

## Novel preference, pooled (added 2026-11-02, later)
All 9 mice, rule-based pose seconds (revised rule), d2 against 0, Wilcoxon exact:
model1 d2 +0.35, 9/9 > 0, p = 0.004, novel share 0.68; model2 +0.28, 8/9 > 0, p = 0.020, share 0.64.
The mice did explore the novel object more. The per-group tests cannot reach 0.05 (smallest p 0.0625
and 0.125), which is why the group lines above show none. The rise in lower-right share from T1
(same spot, two identical objects, so spot preference only) to T2 (spot + novelty + blue prism) is
what novelty plus the prism adds over the spot: 9/9 (model1) and 7/9 (model2). Novelty and an intrinsic
preference for the prism cannot be separated in this batch.

## Still open
1. ~~Rater 2 scores NOR_247 and NOR_685~~ done 2026-11-02 (kappa 0.76). Ideally a second blinded rater scores
   all 18 clips and hand d2 becomes the endpoint, pose as support.
2. Freeze the gap a priori (0.2 s, rule-based) and show 0.2-2.5 s as a sensitivity table.
3. Make the change in lower-right share the primary recognition endpoint for batch 1.
4. Batch 2: counterbalance the novel object's **identity and side** across mice and groups (only the
   side is planned so far).
5. SOD1 comparison: pool batches; fix n from a power calculation (d2 SD about 0.15 water, 0.30 SOD1).

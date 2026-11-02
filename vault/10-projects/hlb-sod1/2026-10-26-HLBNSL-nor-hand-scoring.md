---
type: experiment
area: hlb-sod1
status: active
created: 2026-10-26
summary: "Blinded hand scoring of the HLBNSL NOR clips (BORIS): the scoring rules, and one section per clip for Andrea's scores; validates the pose scoring"
tags: [behaviour, nor, validation, hlbnsl]
---

# 2026-10-26: HLBNSL NOR hand scoring (blinded)

> [!abstract] TL;DR
> Andrea scores object exploration by eye on the blinded clips, using the rules below. The 4
> validation clips come first. Claude then unblinds and compares the hand scores, bout by bout and
> per clip, with the pose scoring of both models: [[2026-10-25-HLBNSL-nor-pose-results]].
> The hand scores are the SOP endpoint (BEHAVIOR_SOP.md section 3).

> [!warning] Keep this note blind
> Only clip codes go here: no mouse, group or trial next to a code. The key is
> `Desktop\Nanotag videos upright\NOR_blind_key.csv` on `kaist-bilab-win`. Leave it closed until
> all your scores are in.

## Scoring rules

### What counts as exploration
1. **The snout is directed at the object and within 2 cm of it.** This is the SOP rule (section 3),
   and it is the definition most NOR protocols use. Sniffing, and touching the object with the nose
   or the whiskers, count.
2. **2 cm by eye:** each object is about 3.3 cm wide, so 2 cm is about two-thirds of an object's
   width. (This landmark is a suggestion; the SOP leaves it for you to fill in.)
3. **Rearing beside the object** counts if the snout points at the object and the forepaws are not on it.

### What does not count
4. Sitting or standing on the object.
5. Climbing onto it, or rearing with the forepaws on it, **even while sniffing**. The SOP excludes it,
   although some labs count it.
6. Chewing or biting the object.
7. Passing the object, or turning near it, with the snout pointing elsewhere.
8. Grooming, resting or sitting next to the object without sniffing it. (2026-11-02: except sitting within
   2 cm **facing** the object, which counts; see Decisions. Grooming or resting with the snout elsewhere does not.)
9. The head held over the object while the snout points past it (seen on the low blue prism).

### Edge cases (decide once, apply to every clip)
- The mouse sits facing the object within 2 cm but does not sniff: rule 8 says no. Strictly, the SOP
  says "directed and within 2 cm" (yes). Choose one, and write it under "Decisions" below.
- A bout ends when the snout turns away or moves beyond 2 cm. Don't merge two sniffs separated by a
  clear turn away.

### Where to score (office PC, Ubuntu side, set up 2026-10-31)
- The 18 blinded clips were copied from the Windows side of the same PC
  (`Desktop\Nanotag videos upright\NOR-blind\videos\`) to `~/nor-scoring/videos/` on Ubuntu,
  sha256 checked (18/18 identical). `score_these_first.txt` is beside them. **The blind key was
  not copied**, and the Windows partition was unmounted afterwards.
- BORIS is installed as a uv tool (`uv tool install boris-behav-obs`, launch with `boris`). It
  plays video through libmpv: `sudo apt install -y libmpv2 ffmpeg` was run 2026-10-31.
- BORIS project: `~/nor-scoring/NOR_HLBNSL.boris` (BORIS 9.15.0), one observation per clip
  (named by its code), media and ethogram already set; it passed BORIS's own integrity check.
  Keys: `a` = explore_A, `b` = explore_B (T1), `f` = explore_familiar, `n` = explore_novel (T2).
  The four are mutually exclusive, so pressing one stops another; press the same key again to stop it.
  Save the project (Ctrl+S) after each clip. No export is needed: the comparison reads the project.
- Back up the project file when done (it is the only copy of the scores): copy it into
  `nanotag/analysis/behavior/` results or back to the Windows folder. `~/nor-scoring` is not in git.
- After all scores are in, Claude runs `nanotag/analysis/behavior/nor_hand_vs_pose.py` (reads the
  key from the Windows side at run time): per-object seconds (r, ICC(A,1), bias, limits of
  agreement), frame-level Cohen's kappa and precision / recall at 30 Hz, and d2 per mouse, hand
  vs model1 vs model2. Dry run 2026-10-31 with model2's bouts injected as fake hand scores gave
  kappa 1.000 against model2, as it should.

### Procedure
- Score the whole clip (600 s, it already starts at the release of the mouse). No cut-off at a
  fixed amount of exploration.
- Score the objects as **state events** in BORIS, one key each, so every bout has a start and a stop:
  - T1 (two red pyramids): `explore_A` = the **upper-left** object, `explore_B` = the **lower-right** one.
  - T2 (one red pyramid, one blue prism): `explore_familiar` = the red pyramid, `explore_novel` = the blue prism.
- Export the events per observation (tabular events, CSV) into `Desktop\Nanotag videos upright\NOR-blind\boris_export\`.
- Slow playback (0.5x) helps near the objects. Rewind whenever unsure.
- The SOP asks for a second rater on a random 20 % of clips, to report agreement between raters. It cannot be added later.

### What the scores feed (computed by Claude, not by hand)
- d2 = (novel − familiar) / (novel + familiar), from −1 to +1.
- T1 location bias: the share of T1 exploration on the more-visited object.
- Exclusions (SOP section 4): total exploration < 20 s in T1 or T2, or T1 location bias > 80 %.
- Agreement with the pose scoring: seconds per object, d2, and per-bout overlap.

> [!warning] 2026-10-31: NOR_152 and NOR_173 were partly unblinded
> One of Claude's tool outputs printed their key rows (mouse and group) during setup. Score them
> last or by a second rater, and note it with their scores.

> [!warning] 2026-11-02: forepaw rule changed (Andrea)
> Sniffing with the forepaws resting on the object now **counts**: rules 3 and 5 below are replaced by
> the revised rule in BEHAVIOR_SOP.md section 3 ([[2026-11-02-nor-forepaw-rule-literature-review]]).
> No `paws_on` key (Andrea: paws-on is too fast to mark on top of the bout). NOR_247 and NOR_685 were
> already scored counting forepaw contact (Andrea, 2026-11-02), so no clip needs revisiting.

## Methods text (draft, 2026-11-02)
For the paper's methods. The bracketed landmark is still open; the rest restates BEHAVIOR_SOP.md section 3 and the rules above.

> Object exploration was scored manually from the overhead video by one experimenter blind to group,
> mouse and trial identity (clips renamed to random codes), using BORIS v9.15.0 (Friard and Gamba,
> 2016) with each object coded as a state event. The whole 10 min trial was scored, from the
> release of the mouse. Exploration was defined as the snout directed at the object and within
> 2 cm of it [judged by eye, taking the object's width, about 3.3 cm, as reference], sniffing,
> whisking or touching it, also with one or both forepaws resting on the object. Sitting within
> 2 cm with the snout directed at the object was counted even without visible sniffing. Not
> counted: sitting or standing on top of the object, climbing over it, rearing or leaning on it with
> the head raised above it or looking past it, chewing or biting it, passing or turning near it with
> the snout pointing elsewhere, and grooming or resting beside it with the snout pointing elsewhere.
> A bout started when the snout came within 2 cm directed at the object and ended when the snout
> turned away, moved beyond 2 cm or lifted above the object, or the mouse climbed on top. Labs differ
> on forepaw contact (Akkerman et al., 2012); excluding it changed the automated scores by at most
> 0.02 in d2. The discrimination index was d2 = (T_novel − T_familiar) / (T_novel + T_familiar).
> Mice with less than 20 s of total exploration in either trial, or more than 80 % of T1
> exploration on one object, were to be excluded.

Missing before it can be used: the second-rater agreement (SOP: random 20 % of clips, ICC), and
the note that the objects differ in shape and colour but not texture (SOP section 1).

## Decisions
- Sitting facing the object without sniffing: **counts** as exploration (Andrea, 2026-11-02, before any
  clip was scored). Follows the SOP definition literally (snout directed at and within 2 cm); the pose
  scoring has no sniffing test either, so hand and pose apply the same rule here.
- Forepaws resting on the object while the snout is on it: **counts** (Andrea, 2026-11-02); NOR_247
  and NOR_685 were already scored this way. [[2026-11-02-nor-forepaw-rule-literature-review]]
- Anything else decided while scoring:

## Validation result (2026-11-02, 4 clips, revised forepaw rule)
> [!note] 2026-11-02: superseded by the 6-clip analysis with calibration and independent review:
> [[2026-11-02-HLBNSL-nor-hand-validation-and-calibration]]. Rater 2 scored NOR_238 and NOR_554 only;
> NOR_247 and NOR_685 (overlap) are still owed.

Computed by `nor_hand_vs_pose.py` against the pose scoring re-run under the revised rule
(`~/nor-scoring/.pose/forepaws_count/`, office PC, not in git). Output in
`~/nor-scoring/.compare_2026-11-02/` (names mice: keep closed while other clips are still scored).

| | model1 vs hand | model2 vs hand |
|---|---|---|
| seconds per object (8 objects): r | +0.94 | +0.94 |
| ICC(A,1) | 0.80 | 0.69 |
| bias (model − hand) | −4.3 s | −6.0 s |
| limits of agreement | −10.3 to +1.8 s | −12.5 to +0.5 s |
| frame kappa, as scored | 0.46 | 0.45 |
| frame kappa, hand shifted by its lag (model2 only) | not computed | 0.65-0.79 per clip |
| d2 bias, 2 T2 clips | +0.05 | −0.04 |

- **Hand key presses lag the model by 0.5-0.6 s** in all 4 clips (best kappa at +0.5 to +0.6 s,
  model2). This is reaction time at 1x playback. It shifts bouts and costs frame agreement, but
  barely changes total seconds, because both start and stop lag.
- **The models give 10-25 % less time than the hand** on most objects: hand bouts are fewer and longer
  (median 0.7-1.3 s against 0.4-0.7 s for model2), so the hand bridges short gaps and keeps the
  approach the model drops. The exception is model1 on the novel prism of NOR_936 (+1.4 s over hand),
  in line with its known pull toward the blue prism.
- Agreement on totals is good (r 0.94), on the absolute level moderate (ICC 0.69-0.80, a consistent
  under-count). Model1 is closer than model2 here, the reverse of the earlier choice of model2 as
  primary; with 4 clips (2 per trial type) this is not yet a basis to switch.
- Not yet done: the second rater (SOP: random 20 %), and whether a calibration (lag, gap merging) brings
  the models within the agreement the literature reports (r 0.92-0.98, ICC ≥ 0.9). Andrea decides
  whether to hand-score more clips.

## Validation subset (score these first)

### NOR_247
- Scored on (date), BORIS file: 2026-11-02, `~/nor-scoring/NOR_HLBNSL.boris` (office PC; snapshot `~/nor-scoring/.compare_2026-11-02/scored_snapshot.boris`)
- Object 1 (A or familiar), seconds: 23.1
- Object 2 (B or novel), seconds: 44.3
- Bouts (object 1 / object 2): 19 / 27
- Unsure moments (time, what):
- Notes:

### NOR_685
- Scored on (date), BORIS file: 2026-11-02, `~/nor-scoring/NOR_HLBNSL.boris` (office PC; snapshot `~/nor-scoring/.compare_2026-11-02/scored_snapshot.boris`)
- Object 1 (A or familiar), seconds: 16.0
- Object 2 (B or novel), seconds: 27.9
- Bouts (object 1 / object 2): 13 / 25
- Unsure moments (time, what):
- Notes:

### NOR_899
- Scored on (date), BORIS file: 2026-11-02, `~/nor-scoring/NOR_HLBNSL.boris` (office PC; snapshot `~/nor-scoring/.compare_2026-11-02/scored_snapshot.boris`)
- Object 1 (A or familiar), seconds: 25.1
- Object 2 (B or novel), seconds: 31.1
- Bouts (object 1 / object 2): 20 / 24
- Unsure moments (time, what):
- Notes:

### NOR_936
- Scored on (date), BORIS file: 2026-11-02, `~/nor-scoring/NOR_HLBNSL.boris` (office PC; snapshot `~/nor-scoring/.compare_2026-11-02/scored_snapshot.boris`)
- Object 1 (A or familiar), seconds: 23.8
- Object 2 (B or novel), seconds: 22.0
- Bouts (object 1 / object 2): 15 / 18
- Unsure moments (time, what):
- Notes:

## Other clips (if there is time)

| Code | Scored on | Object 1 (A or familiar) s | Object 2 (B or novel) s | Notes |
|---|---|---|---|---|
| NOR_152 | | | | |
| NOR_173 | | | | |
| NOR_238 | | | | |
| NOR_300 | | | | |
| NOR_330 | | | | |
| NOR_472 | | | | |
| NOR_488 | | | | |
| NOR_518 | | | | |
| NOR_534 | | | | |
| NOR_554 | | | | |
| NOR_792 | | | | |
| NOR_806 | | | | |
| NOR_836 | | | | |
| NOR_884 | | | | |

## Next clips and second rater (plan 2026-11-02, revised the same day)
- A second person (not Andrea) scores **NOR_238 and NOR_554** (one T1 and one T2, drawn at random with
  seed 20261102, skipping the partly unblinded NOR_152 and NOR_173). The model calibration (lag, gap
  merging) is fitted on Andrea's 4 clips and tested on these 2, which it never saw. Each rater's lag is
  corrected separately.

## Second rater (SOP: random 20 %)
- The same person also scores **NOR_247 and NOR_685** (Andrea's, one T2 and one T1), for the
  agreement between raters. 4 clips of 18 = 22 %.
- Project: `~/nor-scoring/rater2/NOR_HLBNSL_rater2.boris` (empty; NOR_238, NOR_554, NOR_247, NOR_685;
  same ethogram and keys). The second rater scores from this file only, with the rules above, and must
  not open Andrea's project or this note's score sections.
- Rater, date:

## References
The rules above follow BEHAVIOR_SOP.md section 3, and the NOR protocols listed in
[[2026-10-25-nor-day1-oft-feature-set#References]] (Leger et al. 2013, Antunes & Biala 2012,
Lueptow 2017, Denninger et al. 2018, Ennaceur 2010). Where labs differ (forepaws on the object while
sniffing, sitting nearby without sniffing), the SOP choice or the Decisions section above governs.

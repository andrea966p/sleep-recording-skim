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
8. Grooming, resting or sitting next to the object without sniffing it.
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

## Decisions
- Sitting facing the object without sniffing:
- Anything else decided while scoring:

## Validation subset (score these first)

### NOR_247
- Scored on (date), BORIS file:
- Object 1 (A or familiar), seconds:
- Object 2 (B or novel), seconds:
- Bouts (object 1 / object 2):
- Unsure moments (time, what):
- Notes:

### NOR_685
- Scored on (date), BORIS file:
- Object 1 (A or familiar), seconds:
- Object 2 (B or novel), seconds:
- Bouts (object 1 / object 2):
- Unsure moments (time, what):
- Notes:

### NOR_899
- Scored on (date), BORIS file:
- Object 1 (A or familiar), seconds:
- Object 2 (B or novel), seconds:
- Bouts (object 1 / object 2):
- Unsure moments (time, what):
- Notes:

### NOR_936
- Scored on (date), BORIS file:
- Object 1 (A or familiar), seconds:
- Object 2 (B or novel), seconds:
- Bouts (object 1 / object 2):
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

## Second rater (SOP: random 20 %)
- Rater, date, clips:

## References
The rules above follow BEHAVIOR_SOP.md section 3, and the NOR protocols listed in
[[2026-10-25-nor-day1-oft-feature-set#References]] (Leger et al. 2013, Antunes & Biala 2012,
Lueptow 2017, Denninger et al. 2018, Ennaceur 2010). Where labs differ (forepaws on the object while
sniffing, sitting nearby without sniffing), the SOP choice or the Decisions section above governs.

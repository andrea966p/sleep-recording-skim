# Behavioural scoring SOP — HLB SOD1 project

Frozen scoring rules for the Y-maze / OFT / NOR battery. The HLBNSL
(sleep-normal) and HLBNSD (sleep-deprived) cohorts form one 2x2 design, so
**both batches must be scored under the rules below, unchanged.** Any edit to a
threshold or zone definition requires re-deriving both batches; record the date
and the reason in the changelog at the end.

Source protocol: `Acute_SD_Behavioral_Protocol.pdf` (KAIST / HLB SOD1).

| | |
|---|---|
| Batch 1 | HLBNSL — NS-SL (SOD1, n=5) vs NW-SL (water, n=5), **minus mouse 43** (died 2026-09-28) → n=5 vs n=4 |
| Batch 1 testing | Y-maze 2026-09-30, OFT/NOR habituation 2026-10-01, NOR T1+T2 and sampling 2026-10-02 |
| Batch 2 | HLBNSD — NS-SD (51-55, SOD1) vs NW-SD (56-60, water), sampling 2026-11-02 |
| Capture | Phone camera, top-down overhead |
| Tracking | EthoVision XT on the Windows PC (night sessions) |
| Object exploration | Manual, blinded, in BORIS on the Linux workstation |

---

## 1. Video preparation (Linux workstation)

Phone video is variable frame rate; EthoVision assumes a constant time base, and
Noldus guarantees import only for files their own encoders wrote. Every file is
transcoded to CFR 30 fps H.264, 1080p, rotation baked in, **before** it reaches
the Windows PC.

```bash
B=nanotag/analysis/behavior/prep.py
/usr/bin/python3 $B inventory <raw_dir> -o inventory.csv   # QC: VFR? rotation? resolution?
/usr/bin/python3 $B convert   <raw_dir> <cfr_dir>          # transcode + blind
/usr/bin/python3 $B verify    <raw_dir> <cfr_dir>          # CFR 30, duration unchanged
```

`convert` writes `blind_key.csv` **in the parent of `<cfr_dir>`**, so the key does
not sit in the folder the scorer opens. Fill the `mouse`, `group`, `test`, `trial`
columns by hand, then keep the key closed until the stats step.

Originals are never modified. A duration drift > 0.1 s between original and
converted file means frames were dropped — that file is re-converted, not used.

### Checks before any batch processing (Phase 0 gate)
- [ ] Camera fixed, not handheld, for the whole trial (drift breaks arena calibration)
- [ ] Whole arena in frame, with a known length visible for scale calibration
- [ ] 1x lens, not ultrawide (barrel distortion inflates path length near the walls)
- [ ] Mouse/floor contrast adequate, no hard shadows crossing the arena

Answers for batch 1 (HLBNSL), checked 2026-10-20 from mid-trial frames:

| Check | Y-maze | OFT / NOR |
|---|---|---|
| Camera fixed during a trial | yes | yes |
| Framing identical across videos | **no — drifted between mice** | yes |
| Whole apparatus in frame | **no, see below** | yes, with margin |
| Lens | 1x, no ultrawide | 1x, no ultrawide |
| Mouse/floor contrast | excellent (black on white) | excellent |
| View | **oblique — arm inner walls visible** | near-overhead |

Capture format, all 36 files: 1440x1440 square, H.264, **already constant 30 fps**
(not VFR), **rotation -90 in metadata on every file**. So the CFR conversion is not
needed for the time base, but the rotation still has to be baked in before EthoVision.

**Y-maze framing, per video** (distal arm end out of frame = that arm's tip is not
recorded):

| Mouse | Truncated arm | Margin at the tightest edge |
|---|---|---|
| HLBNSSL41 | left arm | top arm has ~85 px |
| HLBNSSL42 | **top arm** | — |
| HLBNSSL44 | **top arm** | — |
| HLBNSSL49 | none | ~10 px |
| HLBNWSL45 | none | ~10 px |
| HLBNWSL46 | none | ~10 px |
| HLBNWSL47 | **top arm** | — |
| HLBNWSL48 | none | ~20 px |
| HLBNWSL50 | none | ~15 px |

> **2026-10-24: the mouse labels in this table are wrong for 45-49.** They came from the
> "ascending ID" run order, but the mice ran SOD1 first: 41, 42, 44, 49, 45, 46, 47, 48, 50
> (checked against the mouse cards in the videos). Read the rows as: HLBNWSL45 here = true
> **HLBNSSL49**, 46 = **45**, 47 = **46**, 48 = **47**, HLBNSSL49 here = true **HLBNWSL48**.
> So the truncated top arms are 42, 44 (SOD1) and **46** (water); still not confounded with group.

Decided with the experimenter 2026-10-20: **the mouse is in frame throughout every trial**,
which is the criterion that matters. The truncation affects only the apparatus outline, so:

- Y-maze videos are **rotated to align the maze** and each gets its **arena and zones set
  manually, per video**. They do not share one arena definition.
- **Arm entries and SA% are the primary Y-maze endpoints** and are unaffected: entries are
  scored at the arm's proximal threshold near the centre triangle, in frame in every video.
- **Distance and speed in cm are secondary.** Rotation is an in-plane transform, so it
  aligns the maze but does not remove the wide-angle parallax that makes one scale factor
  slightly position-dependent across the frame. Report them as relative/secondary, or
  calibrate per video and state the method.
- **The in-frame assumption is verified for free during tracking:** EthoVision reports
  missed/unreliable samples per trial. A trial with an unusual missed-sample count gets
  looked at before its data is used.
- Truncation is not confounded with treatment group (42, 44 are SOD1; 47 is water).
- NOR/OFT videos are **cropped** to the arena before tracking, which also removes the
  second empty compartment at the left edge.

Video durations exceed the protocol windows (Y-maze 548-730 s for an 8 min test;
OFT 664-757 s and NOR 642-857 s for 10 min tests), so every file carries handling
before and after the trial and **must be trimmed to the trial window** before tracking.
HLBNWSL50's NOR-T2 is the outlier at 857 s.

Checked and cleared: no escapes and no experimenter hands inside the apparatus in the
frames sampled from HLBNWSL45 and HLBNWSL48 Y-maze.

**NOR objects:** T1 used two identical **red pyramids** (triangular, point apex).
T2 kept one red pyramid in place and replaced the other with a **blue triangular prism**
(flat top ridge instead of an apex), confirmed by zooming on the objects 2026-10-20. So
the novelty differs in **both shape and colour**, which is an acceptable NOR pair.

Two caveats that remain:
- The objects are **small and low** — roughly the size of the mouse's head. Confirm they
  were fixed to the floor; an object the mouse can shift or topple invalidates that trial.
  Small, low objects are also easy to climb and sit on, which is exactly what the manual
  scoring rule in section 3 has to exclude.
- Both are smooth plastic, so they differ in shape and colour but **not in texture**.
  Note it in the methods; no action needed.

**Batch 2 (testing 2026-10-31 to 11-02) should fix the Y-maze camera framing** so all
three arm ends clear the frame with margin.

---

## 2. EthoVision settings

One experiment per test type, so the arena and zones are defined once.
Sample rate **30/s**, matching the converted video. Record the exact version used.

| Setting | Value |
|---|---|
| EthoVision version | XT 11.5.1026 |
| Detection method | Y-maze batch 1: **Gray scaling, range 0-82**, contour erosion 1 px + dilation 1 px (erode first), subject size 517-15533 px, track noise reduction off (2026-10-24). Dynamic subtraction also detected well; gray scaling chosen |
| Subject points | Centre-point (nose-point additionally, if licensed) |
| Sample rate | 30/s |

### Y-maze (8 min)
- Scale calibrated on: **35 cm, maze centre to arm end**, one line per arm along the arm's
  centre line at floor level. This is the **design** value (Andrea 2026-10-24), not measured on
  the maze; measure it before batch 2 and correct if it differs. Affects distance/speed only.
- Zones: 3 arm zones + centre triangle. Arm zone boundary pulled **_(fill in)_ cm**
  into the arm from the centre triangle, so a centre-point crossing approximates
  the protocol's all-four-paws criterion.
- **Known deviation:** the protocol defines an entry as all four paws crossing the
  threshold; EthoVision scores the centre-point. Validated against hand-scored
  entry sequences on 3 videos — agreement: _(fill in)_ %.
  Batch 1 (2026-10-25, HLBNSSL41, HLBNWSL46, HLBNWSL50, zone exit threshold 3 cm): SA% within
  3.8-4.0 points of hand scoring (mean 3.9), mouse order preserved; EthoVision arm entries
  7-26 % above the four-paw count (partial entries). Sequence-level agreement not computed
  (EthoVision does not export the per-threshold sequence). Vault: `2026-10-25-HLBNSL-ymaze-hand-scoring`.
  All 9 after redrawing with a gap (trials 10-18): entries +0 to +7, SA% mean |difference| 5.3
  points, EthoVision lower in 8 of 9, r +0.88. Hence hand scoring is the Y-maze endpoint.
- Export: raw centre-point XY track **and** the zone-visit sequence.

### Open field / NOR habituation (10 min, 50 x 50 cm, 20 lux)
- Scale calibrated on the 50 cm wall.
- Centre zone: inner **25 x 25 cm** = 25% of the arena area. Periphery = remainder.
- Thigmotaxis band: within **5 cm** of any wall (computed here from the raw track,
  not in EthoVision — see `metrics.thigmotaxis`).
- Export: total distance, mean velocity, centre time/entries, raw XY track.

### NOR T1 / T2 (10 min each)
- Tracked for locomotion and as a sanity check only.
- **EthoVision nose-point zone time is NOT the exploration endpoint.** Contour
  tracking loses the animal against objects and walls, and zone dwell does not
  exclude climbing. Exploration comes from BORIS (section 3).

Always export raw track data, not only the summary statistics — summaries can be
recomputed, tracks cannot be recovered.

---

## 3. Manual NOR scoring (BORIS, blinded)

Scored from `<cfr_dir>` on the blinded codes alone. The scorer must not have the
key open.

Ethogram — state events, one key each:

| Trial | Events |
|---|---|
| T1 | `explore_A`, `explore_B` (the two identical objects, by position) |
| T2 | `explore_familiar`, `explore_novel` |

**Scoring rule (verbatim):**

> Exploration = the snout is directed at and within 2 cm of the object.
> Excluded: sitting on the object; climbing or rearing with the forepaws on the
> object; chewing or gnawing the object; and passing the object with the snout
> oriented elsewhere.

- Judge the 2 cm distance against a landmark of known size in frame, decided once
  per arena setup and written here: _(fill in)_
- Second rater independently scores a random 20% of videos. Report the intraclass
  correlation on exploration durations — this cannot be collected later.
- The same session also hand-scores arm-entry sequences for 3 Y-maze videos, to
  validate the EthoVision entry definition above.

Export per-behaviour total duration, latency and bout count to CSV.

---

## 4. Derived measures and exclusions

Implemented in `metrics.py`; run it to execute its asserts.

| Endpoint | Definition |
|---|---|
| Spontaneous alternation % | `alternations / (total_entries - 2) * 100`, overlapping triplets of three different arms. Undefined below 3 entries. |
| Total arm entries | Arm entries including re-entries into the same arm (`collapse_repeats=False`) |
| d2 | `(T_novel - T_familiar) / (T_novel + T_familiar)`, range -1 to +1 |
| T1 location bias | Share of T1 exploration on the more-visited object, 0.5 to 1.0 |
| Thigmotaxis | Fraction of tracked samples within 5 cm of a wall |

**NOR exclusions** (logged with counts in the output; they do **not** remove the
mouse from Y-maze or OFT):
1. Total exploration < 20 s across both objects in T1 **or** T2
2. T1 location bias > 80%

---

## 5. Statistics

With n=5 vs n=4 in batch 1, the between-group tests are underpowered; the output
says so explicitly rather than implying otherwise.

- **Per group:** one-sample test of d2 against 0, and of SA% against 50% chance.
  These are the primary questions — did the group recognise the novel object,
  did it alternate above chance.
- **Between groups:** Mann-Whitney U per endpoint, reporting effect size and CI
  rather than leaning on the p-value.
- **Headline 2x2 (SOD1 x SD):** held until batch 2 is scored, then two-way ANOVA
  on the pooled four groups. **Batch 1 alone cannot answer the project question**;
  it supplies the sleep-normal half of the design.
- **Protocol control check:** Pearson correlation between total arm entries and
  SA%, to show any cognitive drop is not locomotor.

Figures follow the lab convention already used in `analysis/cohort.py`: reuse
`style(ax)`, bar charts start at 0, bounded measures span their full scale,
SOD1 `#c2410c` / water `#1d4ed8`, mean ± SEM with per-mouse dots and a
significance bracket.

---

## Changelog

| Date | Change | Reason | Batches re-derived |
|---|---|---|---|
| 2026-10-20 | Initial version, before any video was scored | — | — |
| 2026-10-24 | Batch 1 prepared on the Windows EthoVision PC, not the workstation: originals renamed to mouse IDs (`rename_videos.py`, log `rename_log.csv`), upright copies made with `prep.py convert --keep-names` (ffmpeg 9.0.2), so **EthoVision tracking is not blinded**. BORIS NOR scoring still uses blinded copies. EthoVision version: XT 11.5. Clicking guide: vault note `ethovision-11-5-y-maze-tracking` | Andrea's decision: tracking is automated; arenas are drawn per video by the experimenter anyway | none (nothing scored yet) |
| 2026-10-24 | Encoder: batch 1 Y-maze with `libx264 -crf 18 -preset slow` (CPU); batch 1 OFT/NOR with `h264_nvenc -preset p7 -tune hq -rc vbr -cq 18` (GPU, RTX 3080 Ti, new `--encoder` flag). Trial window: Andrea crops each video by hand from door closed to door opened. Batch 2 must use the same encoder per test as batch 1 | CPU at 90 % for ~2 h; same window rule Andrea timed during testing | none |
| 2026-10-25 | **Y-maze SA% and arm entries are hand-scored** (all four paws, re-entries kept, `metrics.py`), from the 480 s clips; EthoVision gives distance and velocity only, with arm zones starting about 3 cm into each arm and a centre triangle (batch 1 trials 10-18, arenas `…b`). Supersedes the 3 cm EthoVision row below. Batch 2 is scored the same way | Redrawing the zones moved EthoVision SA% per mouse by up to 13 points; with gap zones it still ran 5.3 points below hand scoring on average (r +0.88) | batch 1 Y-maze |
| 2026-10-25 | **Y-maze entries scored with EthoVision Zone alternation, zone exit threshold 3 cm (provisional)**, arms A/B/C only, instead of a gap strip between centre and arm zones: the batch 1 arm zones touch the centre triangle and arenas 41/50 lack a centre zone, so border flicker made 36-44 false re-entries per mouse at 0 cm. SA% plateaus from 3 cm (1/2/3/4 cm: 44.5/56.6/61.6/62.6 SOD1). Batch 2 uses the same threshold. Validate on 3 hand-scored videos before final | Noldus's documented remedy for false re-entries; no re-tracking needed | batch 1 Y-maze |
| 2026-10-24 | **Mouse order corrected**: run order is 41, 42, 44, 49, 45, 46, 47, 48, 50, not ascending. All 36 originals and copies renamed (log `Desktop\Nanotag videos\rename_fix_log_2026-10-24.csv`); `rename_videos.py` ORDER fixed; framing table above annotated. Checked on the mouse cards for Y-maze and OFT; NOR assumed the same order (Andrea). Y-maze trial clips: door closed + 480 s, cut from the originals with `h264_nvenc` (`Y-maze\trial_8min\`, times in `Y-maze\door_times.csv`); 8 files 14400 frames, HLBNWSL45 14399 (source drops a frame, within 0.1 s) | Andrea saw the mouse cards in the videos | none (nothing scored yet) |

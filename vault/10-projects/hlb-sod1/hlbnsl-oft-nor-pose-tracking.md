---
type: procedure
area: hlb-sod1
status: active
created: 2026-10-25
summary: "Cut the HLBNSL OFT / NOR videos to the 600 s trial and track them with the labmate's YOLO pose models on the kaist-bilab-win GPU, then compute the day 1 open-field features"
tags: [behaviour, oft, nor, pose, yolo, nanotag]
---

# HLBNSL OFT / NOR: trial clips and YOLO pose tracking

> [!abstract] TL;DR
> **What this does.** Cuts each OFT (NOR day 1) and NOR T1/T2 video to the 600 s trial, finds
> the box floor in each clip, runs a pose model that marks the mouse's body parts in every
> frame, and turns the body-centre track into the open-field features.
> **When to use it.** Day 1 (OFT) features for HLBNSL now; HLBNSD (batch 2) the same way.
> Features and why: [[2026-10-25-nor-day1-oft-feature-set]]. If this page and
> `nanotag/analysis/behavior/BEHAVIOR_SOP.md` disagree, the SOP wins.

## What the models are
Two pose-estimation networks trained by a labmate with Ultralytics on hand-labelled mouse
frames, given to Andrea on 2026-10-25 (repo `model1/`, `model2/`, each with a `.txt` keypoint index).
They are mouse trackers: per frame, a box around the mouse and x, y + confidence for each body part.
They do not score behaviour.

| | model1 | model2 |
|---|---|---|
| Network | YOLOv12-small pose | YOLOv8-small pose |
| Keypoints | 12 (nose, ears, thoracic centre, 4 limbs, tail base/middle/tip, body centre) | 11 (nose, ears, 4 paws, tail base/middle/tip, body centre) |
| Input size | 1440 | 544 |
| Speed on the RTX 3080 Ti | about 18 frames/s | about 56 frames/s |

Unknown, ask the labmate: how many frames were labelled, from which setups, and the held-out accuracy.

### Where the weights live (not in git)
`model1/` and `model2/` are in `.gitignore` (Andrea, 2026-10-25): binaries from a labmate, not ours
to version. The only copy in this workspace is on `kaist-bilab-win`, in the repo folder
`C:\Users\Andrea\sleep-recording-skim\model1\` and `model2\`; the labmate has the originals.
`pose_infer.py` loads them from there, so on any other machine copy both folders into the repo root
first and check the hashes:

| File | Bytes | sha256 |
|---|---|---|
| `model1/model1.pt` | 19,854,145 | `3e2bf29a934f2e3f47eff43a97819901b6adda1a2b77235635b56bfaae010020` |
| `model2/model2.pt` | 23,305,432 | `648a24f8ed7186af8928e478f1e60b30cebcb0b7d97b79b8927bee43cb52dc0f` |

Each folder also holds the labmate's `.txt` keypoint index and inference settings; the keypoint
lists are in the table above.

## Before you start
- Machine: `kaist-bilab-win` (RTX 3080 Ti, Git Bash, ffmpeg 9.0.2 with NVENC).
- Python environment `C:\Users\Andrea\behav-venv` (Python 3.12, torch 2.11.0+cu128, ultralytics
  8.4.189, outside the repo). To rebuild it:
  `py -3.12 -m venv behav-venv`, then
  `behav-venv/Scripts/python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128`,
  then `behav-venv/Scripts/python -m pip install ultralytics pandas scipy matplotlib`.
- Originals: `Desktop\Nanotag videos\NOR\` (`NOR_day1_OFT`, `NOR_day2\NOR_day2_part1` = T1,
  `NOR_day2\NOR_day2_part2_novel` = T2). Never modified.
- Trial start per mouse (Andrea, 2026-10-25) in `Desktop\Nanotag videos upright\<OFT|NOR-T1|NOR-T2>\door_times.csv`.
  The start is the moment the mouse is released; the experimenter's hand is out of frame within 1 s
  in all 9 OFT clips.

## Steps
1. **Cut the trial clips** (GPU): for each mouse, `ffmpeg -hwaccel cuda -ss <start> -i <original>
   -t 600 -vf "scale=-2:'min(1080,ih)',fps=30" -c:v h264_nvenc -preset p7 -tune hq -rc vbr -cq 18
   -pix_fmt yuv420p -an` into `<test>\trial_10min\<original name>_trial600s.mp4`. Same encoder as the
   Y-maze clips; the phone's rotation flag is applied by ffmpeg.
2. **Find the floor in each clip**:
   `behav-venv/Scripts/python nanotag/analysis/behavior/oft_arena.py <test>\trial_10min <test>\arena`.
   Writes `corners.csv` (inner floor corners, TL TR BR BL) and an overlay PNG per clip.
   **Look at every overlay.** The framing shifts by tens of pixels between videos, so each clip has
   its own floor. Fix a wrong corner by editing `corners.csv`.
3. **Track**: `behav-venv/Scripts/python nanotag/analysis/behavior/pose_infer.py model2 <test>\trial_10min <test>\pose`
   (then `model1` the same way). One `.npz` per clip and model; existing files are skipped, so a
   stopped run resumes.
4. **Features (OFT)**: `behav-venv/Scripts/python nanotag/analysis/behavior/oft_features.py <OFT>\pose
   <OFT>\arena\corners.csv <OFT>\features_model2.csv --model model2`.
   Running `oft_features.py` with no arguments runs its self-test.
5. **NOR object positions**: run step 2 on `NOR-T1` / `NOR-T2`, then
   `behav-venv/Scripts/python nanotag/analysis/behavior/nor_objects.py <test>\trial_10min <test>\arena\corners.csv <test>\arena\objects.csv`.
   One row per object: colour, centre, footprint-edge distance to the walls in cm and the footprint
   outline. It warns when a clip does not show exactly two objects.
6. **NOR exploration (provisional until validated against hand scoring)**:
   `behav-venv/Scripts/python nanotag/analysis/behavior/nor_explore.py <NOR-T1> <NOR-T2> <NOR-results> --model model2 --oft <OFT>\features_model2.csv`.
   Writes `nor_bouts_<model>.csv` (every exploration bout: mouse, trial, object, start/end s),
   `nor_results_<model>.csv` (per mouse: T1/T2 exploration, d2, T1 location bias, exclusions) and
   `nor_stats_<model>.txt`. The rule and its parameters are in the script's docstring.
   Decision and status: [[2026-10-25-HLBNSL-nor-pose-results]].

## Hand scoring for validation (BORIS)
Scoring rules and the per-clip score sheet: [[2026-10-26-HLBNSL-nor-hand-scoring]]. BORIS exports go
to `NOR-blind\boris_export\`.
- Blinded copies of all 18 NOR clips: `Desktop\Nanotag videos upright\NOR-blind\videos\NOR_<code>.mp4`.
  The key is `Desktop\Nanotag videos upright\NOR_blind_key.csv`, outside the folder the scorer opens:
  keep it closed until the comparison.
- `NOR-blind\score_these_first.txt` lists the 4-clip validation subset (2 T1 + 2 T2, one SOD1 and one
  water each, 4 different mice, drawn at random with seed 20261025).
- Ethogram and rule: BEHAVIOR_SOP.md section 3 (state events; T1 objects by position, T2 familiar /
  novel). Use **A = upper-left object, B = lower-right object** in T1, as `nor_explore.py` does.
  In T2 the novel object is the blue prism (lower right). So T1 vs T2 is visible in the blinded
  clips, and so is the novel object; only the mouse and the group are hidden.
- The SOP still asks for a 2 cm landmark. Suggestion (Andrea to decide): the objects' footprint is
  about 3.3 cm across in every clip (`objects.csv`), so 2 cm is about two-thirds of an object's width. Score each object as a state event so BORIS exports start and stop times; export the
  events per observation, so they can be compared bout by bout with `nor_bouts_model2.csv`.

## Check it worked
- Every clip is 18000 frames at 30 fps. 2026-10-25, 27 clips checked: 17999 in OFT HLBNSSL42,
  NOR-T1 HLBNSSL49, HLBNWSL45, 46, 47, 48, 50 and NOR-T2 HLBNWSL45 (the phone dropped a frame,
  within the SOP's 0.1 s).
- `mouse_on_floor_pct` close to 100 and `top_detection_rejected_pct` small in the features CSV.
- Distance for a 10 min open field is typically 20-60 m; check any mouse outside that by eye.
- model1 and model2 agree on distance and centre time per mouse. Batch 1 reference (2026-10-25):
  r ≥ 0.995 on every endpoint; model1 runs +2 % on distance, +2.6 points on thigmotaxis, −10 s on
  immobility. Get the agreement with `oft_report.py <features_model2.csv> <out> --check <features_model1.csv>`.

## If it goes wrong
| Symptom | Cause | Fix |
|---|---|---|
| Distance about twice the expected, big single-frame jumps | The model takes the ring light outside the box for the mouse (model2, HLBNSSL41: 2.4 % of frames at box confidence about 0.84) | Already handled: `pose_infer.py` keeps the 3 best detections (`max_det` 3, the labmate's setting was 1) and `oft_features.py` keeps the best one whose body point lies within 15 cm of the floor (rears against a wall project about 5 cm out, the ring light about 60 cm) |
| Immobility near 0 | Keypoint jitter in per-frame steps | Already handled: speed is the displacement across a 1 s window |
| Centre entries in the hundreds | Track flicker across the centre edge | Already handled: 1 cm hysteresis |
| `decoded N of M frames` assertion | The video lost more than one frame | Re-cut the clip from the original |
| Overlay outline off the floor edge | `oft_arena.py` search bands miss a shifted frame | Edit `corners.csv` by hand, or widen `BANDS` |

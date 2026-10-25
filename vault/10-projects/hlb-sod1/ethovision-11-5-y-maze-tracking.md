---
type: procedure
area: hlb-sod1
status: active
created: 2026-10-24
summary: "Step by step from scratch: track and analyse the HLBNSL Y-maze videos in EthoVision XT 11.5 on kaist-bilab-win, per the frozen behaviour SOP"
tags: [behaviour, ethovision, y-maze, nanotag]
---

# EthoVision XT 11.5: Y-maze tracking (HLBNSL)

> [!abstract] TL;DR
> **What this does.** Turns the 9 HLBNSL Y-maze trial clips into arm entries, spontaneous
> alternation (SA%), distance and speed, with EthoVision XT 11.5 on `kaist-bilab-win`.
> **When to use it.** Y-maze first; OFT and NOR follow the same pattern (last section).
> Frozen rules (zones, exports, statistics): `nanotag/analysis/behavior/BEHAVIOR_SOP.md`.
> If this page and the SOP disagree, the SOP wins.

Menu names are from the EthoVision XT 11.5 Quick Start Guide and Reference Manual
(`Desktop\ethovision XT\Documentation\`). Tutorial videos for each step:
`Desktop\ethovision XT\program files\Noldus\EthoVision XT 11\Video Tutorial\`.

## Before you start
- **Track these:** `Desktop\Nanotag videos upright\Y-maze\trial_8min\`: 9 files, each exactly
  the 480 s trial (door closed, times in `Y-maze\door_times.csv`, to +8 min), upright, 30 fps,
  1080x1080. HLBNWSL45 is one frame short (the phone dropped a frame).
- Mouse = file name. Run order was 41, 42, 44, 49, 45, 46, 47, 48, 50 (SOD1 first), not ascending;
  files renamed again 2026-10-24 after Andrea checked the mouse cards.
  SOD1: 41, 42, 44, 49 (HLBNSSL). Water: 45, 46, 47, 48, 50 (HLBNWSL). 43 died 2026-09-28.
- Measure the arm length of the Y-maze in cm (floor level, centre edge to arm end).
- The maze is tilted and the view oblique in every video, by a different amount. That is fine:
  each video gets its own arena, drawn on its own image.

## Part A: set up the experiment (once)

### A1. New experiment
1. Start EthoVision XT. Startup window → **New default experiment** (not a template: you need
   your own arena per video anyway).
2. Name `HLBNSL_Ymaze`. Location: the default
   `C:\Users\Public\Public Documents\Noldus\EthoVision XT\Experiments\` is fine. OK.
3. **Experiment Settings** opens:
   - Video Source: **From video file**.
   - Number of Arenas: **1**. Number of subjects per arena: **1**.
   - Tracked Features: **Center-point detection** (nose/tail needs the Multiple body points
     module; the SOP endpoints use the centre-point).
   - Analysis Options: leave Activity analysis off.
   - Units: **cm**, **s**.
4. Version on `kaist-bilab-win`: **11.5.1026** (Help → About, 2026-10-24; recorded in the SOP).

### A2. Trial List (plan the 9 trials)
*Tutorial: `APP_TrialList.mp4`.*
1. **Setup → Trial List.**
2. **Add Variable** twice:
   - `Mouse`, Type Text (e.g. `HLBNSSL41`), Scope: trial.
   - `Group`, Type Text, predefined values `SOD1`, `water`, Scope: trial.
3. **Add Trials** → 9.
4. For each row set `Mouse`, `Group` and the **Video File** (browse to the matching clip in
   `trial_8min\`). Double-check: file name = Mouse value = Group from the registry.
5. Click **Show/Hide → Variables** and tick **Arena Settings**, **Trial Control Settings**,
   **Detection Settings**, and the detection statistics **Missed samples** and **Subject not
   found**. You fill the Arena column after Part B.

## Part B: one Arena Settings per video (9 times)
*Tutorial: `APP_ArenaSettings.mp4`.*

Do video 41 carefully; for the next ones **duplicate** `Arena_41` and move the shapes onto the
new image (faster, and the zones keep the same size).

1. **Setup → Arena Settings.** Rename `Arena Settings 1` to `Arena_41` (or right-click → Duplicate
   for the next mouse, rename `Arena_42` ...).
2. **Browse** → that mouse's clip. **Grab** a background image at a frame where the mouse is in
   an arm end, not in the centre.
3. **Adjust aspect ratio** if the image looks squashed: it must be square (1080 x 1080).
4. **1. Draw Scale to Calibrate** → Calibrate Scale tool → draw a line along one arm at
   floor level, from the centre edge to the arm end → type the arm length in cm. Repeat on the
   other two arms (EthoVision averages). Use the same arms in every video.
   Drawing a line = press the mouse button on the first point, drag, release (manual p. 95).
   A warning "Calibration scale substantially larger or smaller" (> 20 % from the others) is
   likely here because of the oblique view: check the line, and note it if it stays.
5. **2. Select Shape and Draw Arena** → press **Y** (Closed Polyline) → click each corner, then
   **double-click** the last one to close (manual p. 118). Click around the whole Y at **floor level**
   (the inner floor edges, not the top of the walls; the visible inner wall faces stay outside).
   The `Arena` label must sit inside.
6. **3. Select Shape and Draw Zones** → one zone group with four zones, polygon tool:
   - `centre`: the triangle where the three arms meet.
   - `A`, `B`, `C`: the three arms, each starting a fixed distance **into** the arm from the
     triangle (SOP: the centre-point crossing then approximates "all four paws in"). Choose the
     distance on video 41 (start with about 3 cm, roughly a mouse body length without tail),
     write it in the SOP, keep it for all 9. The small strip between the triangle and each arm
     zone belongs to no zone.
   - Letters by the **room**, not the screen: e.g. A = the arm pointing to the ceiling vent, then
     clockwise B, C. Same letters in every video.
   - Truncated arm ends (video top or left edge): draw the arm zone to the frame edge.
7. **4. Validate Setup.** Must pass. Save.
8. Repeat for the other 8 mice. Then go back to the **Trial List** and set the **Arena Settings**
   column: `Arena_41` for HLBNSSL41, etc.

## Part C: Detection Settings (one for all)
*Tutorials: `DS_Introduction.mp4`, `DS_MethodSettings.mp4`, `DS_DetectionSettings.mp4`,
`DS_SubjectSizeSettings.mp4`.*
1. **Setup → Detection Settings** → `Detection Settings 1`.
2. Under Video, **Select Video** → clip 41.
3. **Automated Setup**: play until the mouse is in an arm, drag a rectangle around it. If the body
   is yellow and the tail mostly not, click **Yes**.
4. Then **Advanced** and check:
   - Method: **Gray scaling** (black mouse on white floor). Set the gray range to the dark end:
     the whole body yellow, shadows and wall seams not.
   - Video → **Sample rate: 30** per second (SOP; the clips are 30 fps).
   - Subject size → **Edit**: min and max so specks are ignored; enable the tail erosion /
     removal option if the centre-point drifts along the tail.
   - Smoothing: leave **Track noise reduction off** (smooth after acquisition if needed).
5. Press Play and watch 2 to 3 minutes. The **Detection Performance** pane must keep
   **Subject not found** low (Noldus: < 5 to 10 %). Watch the far arm ends especially.
6. Check the same settings on clips 46 and 50 (different framing). Save.
   Only if one video fails, duplicate to `Detection Settings 2` for it and note which.
7. Trial List: set **Detection Settings 1** for all 9.

## Part D: Trial Control (stop at 8:00)
*Tutorial: `APP_TrialControlSettings.mp4`.*
1. **Setup → Trial Control Settings** → `Trial Control Settings 1`.
2. The clips already start at door closed, so tracking starts with the trial:
   **delete the Start track condition box** (the "subject in arena for 1 s" one). Reconnect
   Rule Begin → Start track.
3. Click **Settings** in the Time condition before **Stop track** → **After a delay of**
   `00:08:00`.
4. Keep at least one condition between Start and Stop (the 8:00 one), or no data is recorded.
5. Trial List: set **Trial Control Settings 1** for all 9.

## Part E: Acquisition
*Tutorials: `APP_Acquisition.mp4`, `VL_BatchAcquisition.mp4`.*
1. **Acquisition → Open Acquisition.**
2. First a single test: Method **Track next planned trial**. In Playback Control tick
   **DDS (Detection Determines Speed)** so every sample is analysed. **Start trial** (Ctrl+F5).
   Watch the track follow the mouse; the trial stops at 8:00.
3. Then Method **Track all planned trials** → Start. The remaining 8 run unattended.
   Do not stop a trial by hand: batch acquisition stops.
4. After acquisition the Arena, Detection and Trial Control settings become **read-only**.
   To change them later, duplicate and re-track.

## Part F: check the tracks
1. Trial List: compare **Missed samples** and **Subject not found** across the 9 trials. One clearly
   higher than the rest = look at that video before using it (SOP: this is the check that the
   mouse stayed in frame).
2. **Analysis → Results → Plot Integrated Data**: play each track with its video.
3. Only obvious single-frame jumps (a reflection): **Acquisition → Edit Tracks** → select the point →
   **Delete and interpolate**. Set a **Restore Point** first. Note every edit. Many errors = fix the
   detection settings instead.
4. SOP validation: write down by eye the arm-entry sequence (A, B, C ...) for **3 videos** and
   compare with EthoVision's. Agreement % goes in the SOP.

## Part G: analysis and export
*Tutorials: `APP_Analysis.mp4`, `APP_IntegratedVisualization.mp4`, `HMP_Heatmaps.mp4`.*
1. **Data Profile**: the default (Start → Result 1) uses all 9 tracks; that is what you want.
   Optional: two Result boxes with a Filter on `Group` for SOD1 and water group means.
2. No track smoothing for these numbers (Acquisition → Track Smoothing Profile: both off).
3. **Analysis → Analysis Profile → New** `Ymaze`. Add (button next to each Dependent Variable):
   - **In zone**: zones `A`, `B`, `C`, `centre`; statistics **Frequency** (= entries) and
     **Cumulative Duration**.
   - **Zone alternation**: zones `A`, `B`, `C` only (not `centre`); tick **Alternations**,
     **Max alternations**, **Direct revisits**, **Indirect revisits**. Zone exit threshold: leave 0
     (the gap strip already prevents false re-entries; write the value in the SOP if you change it).
     SA% = Alternations / Max alternations x 100 (Reference Manual p. 565).
   - **Distance moved**: Total. **Velocity**: Mean. (Secondary endpoints, SOP section 1.)
4. **Analysis → Results → Statistics & Charts → Calculate.** Trial Statistics tab = per mouse.
5. **Analysis → Export → Statistics** → Excel. Save in
   `Desktop\Nanotag videos upright\Y-maze\export\`.
6. **Analysis → Export → Raw Data** → Excel, tick the per-sample dependent variables (In zone).
   One file per trial. Always export this: summaries can be recomputed, tracks cannot.
7. **File → Make Backup** → `.evz` copy of the whole experiment, keep it with the exports.
8. Give the exports to Claude: `metrics.py` recomputes SA% from the raw zone sequence as a
   cross-check of EthoVision's Zone alternation. The two must agree.

## Check it worked
- 9 tracks, 480 s each, Missed samples and Subject not found low and similar.
- Track plots reach the far end of every arm.
- Hand-scored sequences on 3 videos match.
- EthoVision SA% = `metrics.py` SA% for every mouse.
- SOP table filled: version, detection method, arm length, zone offset, agreement %.

## If it goes wrong
| Symptom | Cause | Fix |
|---|---|---|
| Video opens black or not at all | No DirectShow H.264 decoder for EthoVision 11.5 | Install LAV Filters (free DirectShow decoder), or ask Claude to re-encode to MPEG-4 / MJPEG AVI |
| Image squashed | Aspect ratio | Arena Settings → Adjust aspect ratio → 1080 x 1080 |
| Centre-point jumps onto walls | Shadows or wall seams in the gray range | Narrow the gray range; arena at floor level; try Static subtraction |
| Tracking stops at once | No condition between Start track and Stop track | Keep the 8:00 Time condition |
| Cannot edit settings | A track was acquired | Duplicate the setting, edit the copy, re-track |
| SA% differs from `metrics.py` | Re-entries around the arm border | Check the zone offset; compare the entry sequences |

## OFT and NOR (after the Y-maze)
Same steps, separate experiments (`HLBNSL_OFT`, `HLBNSL_NOR`), uncut upright copies in
`Desktop\Nanotag videos upright\OFT\videos\`, `NOR-T1\videos\`, `NOR-T2\videos\` (GPU encoded,
verified). They still need cutting to 600 s from door closed: send the times to Claude.
- Framing did not drift: **one** Arena Settings for all videos of a test (no duplicates per mouse).
- Arena = the 50 x 50 cm floor only. Calibrate on the 50 cm wall. Centre zone = inner 25 x 25 cm.
- Stop track after 10:00.
- NOR: EthoVision is for locomotion only. **Exploration is scored by hand in BORIS on blinded
  copies** (SOP section 3), not from EthoVision zones.

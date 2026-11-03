---
type: procedure
area: hlb-sod1
status: active
created: 2026-11-03
cohort: NS-SD + NW-SD (HLBNSSD51-55, HLBNWSD56-60)
tags: [procedure, nanotag, sod1, sleep-deprivation, y-maze, ns-sd, nw-sd]
---

# NS-SD / NW-SD: Run 2 tags and Y-maze, the commands for 2026-11-04

> [!abstract] TL;DR
> **What this does.** Turns the Run 2 tag files (10-30 19:00 → 11-04) and the hand-scored Y-maze into tables and
> figures for the professor meeting on Thu 2026-11-05: undisturbed treatment days 8-10, SD efficacy on both SD days,
> recovery after SD day 1, and Y-maze SA % and arm entries next to HLBNSL.
> **When to use it.** Evening of 2026-11-04, once the tags are read after sampling and the Y-maze videos are on
> `kaist-bilab-win`. Code ready and dry-run on synthetic files on 2026-11-03; it has **not** seen real Run 2 data.
> Study: [[2026-10-19-NS-SD-NW-SD-nanotag-study]]. Schedule: [[2026-10-30-NS-SD-two-day-SD-y-maze-only]].
> Run 1: [[2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1]].

## Before you start
- **Machine:** where Run 1 lives, the office PC (`~/Desktop/261030_HLBNSSD/`), or copy that folder next to Run 2.
  Python needs numpy and matplotlib for the tags, plus scipy and openpyxl for the Y-maze. On the ThinkPad use
  `~/.venvs/sleepstager/bin/python` instead of `python3` (it has all four).
- **Run 2 tag files:** export each tag to CSV with nanotagViewer (raw, not summarized), one file per mouse, all ten
  in one folder, for example `~/Desktop/261104_HLBNSSD/`. The mouse is read from the header tag ID, not the file name;
  a name that does not contain the mouse number only prints a warning. The `.nta` file time is the save time, not
  the data time: nothing reads it.
- **Y-maze sheet:** `nanotag/analysis/behavior/NSSD_ymaze_hand_scoring.csv`, one row per mouse in test order
  (51, 56, 52, 57, 53, 58, 54, 59, 55, 60). Fill in:
  - `ymaze_start`: the time the mouse went into the maze, `HH:MM`, KST, 11-04. This is the end of that mouse's SD
    and of its home-cage tag data. Blank = data cut at 15:00 and no wait window.
  - `sequence`: the arm letters, e.g. `CABACB…`, scored on the whole 480 s clip.
  - `video_file`, `scorer`, `notes`; `sd_deviation` for anything that differed from gentle handling 09:00-15:00 on
    11-03 and 11-04 (a mouse handled late, left alone, fell asleep and was woken, …).
- **Scoring rules (unchanged from HLBNSL, [[2026-10-25-HLBNSL-ymaze-hand-scoring]], `BEHAVIOR_SOP.md`):** an entry =
  all four paws in the arm; a return into the same arm counts again only if all four paws went into the centre
  first; arm **A** fixed for the session (name the landmark in `notes` on the first row), then **B** and **C**
  clockwise. Unsure: decide before you run the script, the sheet takes letters only.
- Videos: `kaist-bilab-win` (Git Bash, EthoVision); trim each to the 480 s trial as for HLBNSL
  ([[ethovision-11-5-y-maze-tracking]]). EthoVision distance and speed are optional and not part of these commands.

## Steps
1. Self-checks (seconds):
   ```bash
   python3 nanotag/analysis/cohort_sd.py --demo
   python3 nanotag/analysis/behavior/metrics.py
   ```
   Expected: `demo ok`, `metrics selftest ok`.
2. Tags, Run 2 against the Run 1 baseline (about 4 min, most of it the permutation CIs):
   ```bash
   mkdir -p nanotag/analysis/out/HLBNSSD
   python3 nanotag/analysis/cohort_sd.py ~/Desktop/261030_HLBNSSD --run2 ~/Desktop/261104_HLBNSSD --vault \
       | tee nanotag/analysis/out/HLBNSSD/run2_console.txt
   ```
   Console sections: **1** days 8-10 vs baseline, **2** SD efficacy (+ wait to the Y-maze), **3** recovery,
   **4** the note that no sleep after SD day 2 exists; each with a "without 59" repeat.
3. Y-maze, NS-SD next to HLBNSL (seconds):
   ```bash
   python3 nanotag/analysis/behavior/ymaze_nssd.py nanotag/analysis/out/HLBNSSD/ymaze --vault
   ```
   It stops with "fill in the sheet first" while fewer than 2 mice per group have a sequence.

## What the code does
| Endpoint | Window (KST) | Compared with | Output |
|---|---|---|---|
| Undisturbed treatment, days 8-10 | ZT days 10-31, 11-01, 11-02 (10-31 09:00 → 11-03 09:00) | baseline 10-22 → 10-24, change per mouse | total / light / dark sleep, dark and light counts/h, bouts, RA |
| SD efficacy | 09:00-15:00 on 11-03 and on 11-04 | same mouse, 09:00-15:00 on 10-22 and 10-23 | % asleep, change (points), sleep lost (min); "n of 5 below baseline" per group |
| Wait before the Y-maze | 11-04 15:00 → own `ymaze_start` | none (still SD) | real SD length (h), % asleep |
| Recovery after SD day 1 | 11-03 15:00-21:00 (ZT6-12) and 11-03 21:00 → 11-04 09:00 (dark) | same clock hours at baseline | minutes asleep, rebound (min, points), total rebound |
| Y-maze | 480 s trial | SOD1 vs water within each cohort | SA %, arm entries, SA % vs real SD length |

- Sleep = immobility ≥ 48 s, each file scored whole before any window is cut (as Run 1). 🛑 The SD hours are the
  treatment: they are analysed, never removed.
- SOD1 vs water: exact permutation p and the 95 % CI from inverting it, mouse = unit (as Run 1). Y-maze: exact
  Mann-Whitney U, Welch CI, Hedges g, Wilcoxon vs 50 % (SOP section 5, as HLBNSL). Cohorts side by side, never pooled.
- **HLBNWSD59** (tag at the shoulder): read its change from baseline, not its level. Drawn hollow in the SD and
  recovery figures; every change endpoint is repeated without it.
- **Not available:** sleep after SD day 2. Each mouse went from SD to its Y-maze and straight to sampling; tag data
  after the Y-maze start are cut (the tag keeps logging after death).
- **10-30 09:00-19:00 is not recorded** (tag read 18:00-19:00). It is light phase on ZT day 10-30, which no window
  uses; nothing from 19:00 on is affected.
- Windows live in one place: `RUN2_PRE`, `SD`, `RECOVERY` at the top of `cohort_sd.py`. Change them there if a
  logged time differs.

## Outputs
- `nanotag/analysis/out/HLBNSSD/run2/` (git-ignored): `sd_and_recovery_per_mouse.csv`, `daily_sleep_days_8_10.csv`,
  `summary_days_8_10.csv`, every figure as PNG + PDF; `run2_console.txt` one level up.
- `nanotag/analysis/out/HLBNSSD/ymaze/`: `NSSD_ymaze_results.csv`, `NSSD_ymaze_stats.txt`, `NSSD_ymaze_fig.png/.pdf`.
- `--vault` copies these to `vault/_attachments/`:

| File | Shows |
|---|---|
| `2026-11-04-NSSD-run2-sd-efficacy.png` | % of 09:00-15:00 asleep, baseline → SD day 1 → SD day 2, one line per mouse; change and SOD1 − water with CI |
| `2026-11-04-NSSD-run2-recovery.png` | ZT6-12 and dark after SD day 1 against baseline; rebound per mouse with CI |
| `2026-11-04-NSSD-run2-daily-sleep.png` | daily sleep from baseline through Run 1 to day 10 (continuation of Run 1) |
| `2026-11-04-NSSD-run2-change-days-8-10.png` | change from baseline to days 8-10, the Run 1 estimation layout |
| `2026-11-04-NSSD-run2-zt-profile-days-8-10.png` | sleep across the day, baseline vs days 8-10 |
| `2026-11-04-NSSD-run2-actograms.png` | all days 10-22 → each mouse's Y-maze start, SD days visible as activity |
| `2026-11-04-NSSD-run2-ymaze.png` | SA % and arm entries, HLBNSL and NS-SD side by side; SA % vs real SD length |

## Check it worked
- Every mouse prints a `run2` line `used to 11-04 HH:MM` matching its `ymaze_start`; no `WARNING … does not cover`.
- `Y-maze start times in …: 10 of 10`.
- SD efficacy: every mouse below its baseline on both SD days, or you know which one was not and why.
- The HLBNSL block of the Y-maze stats reproduces [[2026-10-25-HLBNSL-ymaze-hand-scored-results]] (SA 60.5 vs 62.8,
  p = 0.73; entries g +1.19, p = 0.063). It did in the dry run.
- Then write the result note (experiment, `hlb-sod1`), add a dated Current state bullet in [[_hlb-sod1-hub]] and a line
  in the 11-04 journal.

## If it goes wrong
| Symptom | Cause | Fix |
|---|---|---|
| `KeyError` on a tag number | a tag not in the 51 = 20639 … 60 = 20648 map | check the registry; `C.TAG` in `cohort_sd.py` |
| `activity gaps` assertion | the export has a hole | re-export; if real, tell Claude (scoring assumes contiguous files) |
| `a second Run 2 file for N` | two CSVs from one tag in the folder | keep one |
| `no Run 2 file` warning | a tag was not read | that mouse drops out of SD and recovery; n = 4 in its arm |
| SD % for one mouse near baseline | not handled, or the tag stopped | check `sd_deviation` and the actogram before reading the group result |
| Y-maze `ZeroDivisionError` in `welch_ci` | every mouse in one group has the same entry count | report entries without the CI |

## Dry run, 2026-11-03
Synthetic Run 1 + Run 2 CSVs in the nanotagViewer layout (10 mice, SD made 10 % asleep, ZT6-12 rebound, 59 with
double dark counts, a post-mortem zero tail after each Y-maze) and a mock Y-maze sheet, all under the session
scratchpad, outside the repo. Both commands ran end to end and every figure rendered; the post-mortem tail was cut
at each Y-maze start, the planted SD effect and rebound came back, 51 (Y-maze at 15:00) correctly had no wait
window. The unchanged Run 1 path also ran on the mock set. Nothing from the dry run is in the repo or the vault.

## Needs Andrea before the run
- [ ] Each mouse's Y-maze start time (`ymaze_start`), and whether the first mouse started at 15:00.
- [ ] Any SD deviation per mouse on 11-03 or 11-04 (late start, early stop, a mouse left alone, bottle change time).
- [ ] Did anything happen in the room on 11-03 between 15:00 and 11-04 09:00 (recovery window), and when were the
  bottles weighed on the SD days? A room entry inside the recovery window would show as wake there.
- [ ] Which landmark is arm A in the new camera view.

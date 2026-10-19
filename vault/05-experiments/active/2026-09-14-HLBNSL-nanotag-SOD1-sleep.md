---
tags: [experiment, nanotag, sod1, sleep, activity, NS-SL, NW-SL, cohort]
created: 2026-10-05
status: active
cohort: HLBNSL (NS-SL + NW-SL)
---

# HLBNSL: oral SOD1 vs water, home-cage sleep by implanted nanotag (NS-SL / NW-SL)

> [!abstract] TL;DR
> - **What:** the first nanotag batch of the HLB SOD1 project ([[_HLB-SOD1-project-hub]]), and the project's second recording method beside the EEG rig. **No EEG**: sleep is scored from immobility on an implanted accelerometer ([[nanotag-kissei-device-and-literature]]).
> - **Arms:** **NS-SL**, SOD1 6.8 U/mL in drinking water (HLBNSSL41, 42, 43†, 44, 49), and **NW-SL**, UV-sterilised water (HLBNWSL45–48, 50). Both sleep ad libitum. Male C57BL/6J, DOB 2026-05-28, sampled 2026-10-02 at 18.1 weeks.
> - **Status:** recordings and sampling done. Analysis (Run 1 + Run 2 merged) done 2026-10-05: [[2026-10-05-HLBNSL-nanotag-merged-analysis]]. **No detectable effect of SOD1 on sleep.**
> - **Next:** the sleep-deprivation batch **NS-SD / NW-SD** (HLBNSSD51–55, HLBNWSD56–60). Surgery 2026-10-12, single housing 10-19, tag recording from 2026-10-22, SOD1 from 2026-10-24, 4-day SD 11-05 → 11-08, sampling **2026-11-08** (re-planned 2026-10-19: [[_HLB-SOD1-project-hub#NS-SD / NW-SD: current schedule (re-planned 2026-10-19)]]). It reuses [[nanotag-recording-and-analysis]].
> - **Registry:** Google Sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO` (Drive id `1jgQpYiUGzEwFpjAhy8SvCamGoeMFZEycLFpzwgfgxhs`), tabs NANOTAG registry / recordings / History / sampling / behavioral. Pending sheet edits: [[2026-10-05-HLBNSL-sheet-handover-run2]]. From 2026-10-19 all sheet changes go through the `Pending changes instructions` tab: [[sod1-sheet-change-log-workflow]].

## Mice and tags

| Mouse | Arm | Tag | Surgery | Baseline | Run 1 | Run 2 | Note |
|---|---|---|---|---|---|---|---|
| HLBNSSL41 | SOD1 | 20641 | 09-11 | 09-14 → 09-17 | ✔ | from 09-28 10:00 | |
| HLBNSSL42 | SOD1 | 20645 | 09-11 | 09-14 → 09-17 | ✔ | 10:00 | |
| HLBNSSL43 | SOD1 | 20643 | 09-11 | 09-14 → 09-17 | ✔ | — | **Died 2026-09-28 ~10:00** in restraint for the tag read; all data discarded; tag explanted and kept |
| HLBNSSL44 | SOD1 | 20646 | 09-11 | 09-14 → 09-17 | ✔ | 10:00 | |
| HLBNSSL49 | SOD1 | 20640 | 09-01 | 09-15 only (1 d) | ✔ | 10:00 | Baseline left out (1 day) |
| HLBNWSL45 | water | 20639 | 09-11 | 09-14 → 09-17 | ✔ | 11:00 | |
| HLBNWSL46 | water | 20648 | 09-11 | 09-14 → 09-17 | ✔ | 11:00 | |
| HLBNWSL47 | water | 20644 | 09-11 | 09-14 → 09-17 | ✔ | 11:00 | Sutured with lights off |
| HLBNWSL48 | water | 20647 | 09-11 | 09-14 → 09-17 | ✔ | 11:00 | |
| HLBNWSL50 | water | 20642 | 09-01 | 09-15 only (1 d) | ✔ | 11:00 | Baseline left out (1 day) |

The tag was implanted s.c. at the neck, pushed right, and in every mouse migrated to the **right dorsolateral flank**. Threshold 170/170 (Kissei's mouse-neck value). Tags 20640 and 20642 had a pilot recording on 2026-09-09 before going into 49 and 50 (NAS `andrea/nanotag-pilot/`).

## Timeline (KST; lights 09:00–21:00, ZT0 = 09:00)

| Date | Event |
|---|---|
| 09-01 / 09-11 | Surgery: 49 and 50 / everyone else |
| 09-12 | Single housing, mice moved to the recording room |
| 09-14 09:00 → 09-17 09:00 | **Homecage baseline**, 3 days (49, 50: 09-15 → 09-16 only) |
| 09-17 14:00–17:00 | **SOD1 (or UV-water) bottles start**, treatment day 1 |
| 09-20 10:00 | **Run 1** starts (delayed start) |
| 09-26, 09-27 | Handling habituation (Day −4, −3), afternoon sessions |
| 09-28 08:30 → ~10:40 | Tag reads (Day −2); Run 1 ended 08:59:48 at the 8-day memory limit. **43 dies ~10:00.** **Run 2** starts 10:00 (SOD1) / 11:00 (water) |
| 09-29 | Handling Day −1, 16:03–17:15 |
| 09-30 | Day 0 **Y-maze**: cages in the test room 14:00–17:00 |
| 10-01 | Day 1 **NOR habituation**: test room 14:00 → back 17:25 |
| 10-02 | Day 2 **NOR T1 (from 14:55) → T2 (+2 h 20 min) → sampling** (dissection after T2, until ~19:35). The tags kept logging post-mortem until read (~20:50–21:40) |

The behavioural times per mouse are in the sheet's `NANOTAG behavioral` tab and are the source of every excluded window ([[2026-10-05-HLBNSL-nanotag-merged-analysis]], "What was removed"). The protocol is `Acute_SD_Behavioral_Protocol.pdf` (NAS analysis folder).

## Where everything is

| What | Where |
|---|---|
| Raw reads (.nta + .csv) | Workstation `~/Desktop/Andrea/nanotag/nanotag recording data/HLBNSL/`; SKIM NAS `02_Data_Sleep/andrea/HLBNSSL`, `HLBNWSL` (each mouse's `raw/`) |
| Per-mouse merged CSV + info.json | SKIM NAS `02_Data_Sleep/andrea/<HLBNSSL|HLBNWSL>/<Baseline|Treatment>/` |
| Report, methods, figures, tables | SKIM NAS `02_Data_Sleep/andrea/HLBNSL_nanotag_ANALYSIS_2026-10-05/`; locally `nanotag/analysis/out/HLBNSL/` (git-ignored) |
| Code | repo `nanotag/analysis/` (`cohort.py`, `nta_qc.py`, `export_nas.py`), `nanotag/report/` (docx/pptx build) |
| Procedure | [[nanotag-recording-and-analysis]] |
| Device and literature | [[nanotag-kissei-device-and-literature]] |

🛑 There is **no off-site copy** of the nanotag raw data yet. The SKIM NAS is a working copy ([[backup-architecture]]); the S3 job runs on e10 and covers the rig only.

## Decisions taken (Andrea)

- **2026-09-28:** mouse 43 is discarded entirely. Mice 49 and 50 are left out of the baseline. Only handling windows are removed; the rest of each day is kept.
- **2026-09-28:** Run 2 discarded, because it overlaps the behavioural tests. **Reversed 2026-10-05:** Run 2 is merged with Run 1 as one treatment period, cutting only the logged handling and test windows (whole room, rounded out to the hour) and everything from 10-02 14:00.
- **2026-10-05:** NAS layout per mouse, like the EEG data, under `andrea/`. Sheet edits are delivered as a checklist, not applied by Claude.

## History

> [!history]
> - **2026-10-05** — Page created when the nanotag work moved into the vault (it previously lived only on the workstation Desktop and in `HANDOVER_sheet_fixes_2026-09-28.md` there).

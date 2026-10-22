---
type: procedure
area: hlb-sod1
status: active
tags: [handover, nanotag, sheet, NS-SL, NW-SL]
created: 2026-10-05
---

# Sheet handover, 2026-10-05: Run 2 is now analysed (HLBNSL nanotag tabs)

> [!warning] Updated 2026-10-22: Sheet edits listed here were not confirmed applied; since 2026-10-19 sheet changes go through the `Pending changes instructions` tab. [[sod1-sheet-change-log-workflow]]

> [!abstract] TL;DR
> The 2026-09-28 sheet text says **"Run 2 discarded"**. Since 2026-10-05 Run 2 is **merged with Run 1 and analysed up to 10-02 14:00** ([[2026-10-05-HLBNSL-nanotag-merged-analysis]]). This page lists the cell edits that bring the NANOTAG tabs in line. **Nothing has been applied.** Andrea, or a sheet session, applies them by hand in the Google Sheet.
>
> Sheet: `HLB_SOD1_Intake_Monitoring_SDSLNANO`, Drive id `1jgQpYiUGzEwFpjAhy8SvCamGoeMFZEycLFpzwgfgxhs`. Values read 2026-10-05.

## Rules (same as the 2026-09-28 handover)

- Edit the sheet in place. Never export to .xlsx and re-upload: that destroys the formulas.
- `NANOTAG recordings` columns **G and M** and `NANOTAG History` **C:E** of the summary are **array formulas**. Never type into them.
- Do not delete rows in `NANOTAG behavioral`; clear contents instead.
- Row map for `NANOTAG recordings`: 9 = 41, 10 = 42, 11 = 43, 12 = 44, 13 = 49, 14 = 45, 15 = 46, 16 = 47, 17 = 48, 18 = 50.

## 1. `NANOTAG recordings`

| Cell | Now | Change to |
|---|---|---|
| G4 | Analysed: homecage baseline 3 d + Run 1 8 d. Run 2 recorded, discarded | Analysed: homecage baseline 3 d + treatment Run 1 (8 d) + Run 2 to 10-02 14:00, merged (2026-10-05) |
| E6 | …Run 2 = from 1 h after extraction handling until auto-stop Sun 10-04 ~13:00; discarded because it overlaps behavioural testing (Day 0 to Day 2). | …Run 2 = from 09-28 10:00 (NS-SL) / 11:00 (NW-SL), read after sampling on 10-02. Analysed to 10-02 14:00 and merged with Run 1 (2026-10-05); logged handling and test windows removed. |
| M7 | (Run 1 8 d analysed · Run 2 discarded) | (Run 1 + Run 2 merged, analysed 2026-10-05) |
| P8 | Run 2 Status (discarded) | Run 2 Status |
| R9:U10, R12:U18 | Run 1 analysed 2026-09-28; Run 2 discarded | Run 1 + Run 2 merged, analysed 2026-10-05 |
| X9, X10, X12, X13 | Pending CSV export (~1h post-extraction ~09:xx) | 2026-09-28 10:00 (header Start date_Activity) |
| X14:X18 | Pending CSV export (… / PM Session) | 2026-09-28 11:00 (header Start date_Activity) |
| Y9:Y18 (not 11) | 2026-10-04 ~13:00 (auto) | Analysed to 2026-10-02 14:00; last bin (read after sampling): see below |
| Z9:Z18 (not 11) | 2026-09-28 08:45–11:00, tag extraction handling (…) | 09-26 14–16, 09-27 16–18, 09-28 08:45–11, 09-29 16–18, 09-30 14–17, 10-01 14–18, 10-02 14:00 → end (handling, tag read, Y-maze, NOR, sampling; whole room, rounded out to the hour) |

Last bins of Run 2, for Y if wanted: 41 20:51:24, 42 21:00:36, 44 20:56:36, 49 21:32:00, 45 21:38:00, 46 21:28:36, 47 21:40:24, 48 21:26:24, 50 21:34:00 (all 10-02). Temperature goes `Out of range` from 19:45–20:40, as the tags cooled after sampling.

Row 11 (43) stays as it is.

## 2. `NANOTAG History`, deployment log

Append one row per tag below the last log row. Do not touch the summary's array formulas.

| Nanotag ID | Mouse ID | Batch | Recording Phase | Start Date | End Date | Session Notes | Days Used |
|---|---|---|---|---|---|---|---|
| 20641 | HLBNSSL41 | NS-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | Run 2 from 10:00; analysed to 10-02 14:00, merged with Run 1 (2026-10-05) | ? |
| 20645 | HLBNSSL42 | NS-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | same | ? |
| 20646 | HLBNSSL44 | NS-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | same | ? |
| 20640 | HLBNSSL49 | NS-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | same | ? |
| 20639 | HLBNWSL45 | NW-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | Run 2 from 11:00; analysed to 10-02 14:00, merged with Run 1 (2026-10-05) | ? |
| 20648 | HLBNWSL46 | NW-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | same | ? |
| 20644 | HLBNWSL47 | NW-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | same | ? |
| 20647 | HLBNWSL48 | NW-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | same | ? |
| 20642 | HLBNWSL50 | NW-SL | Activity & Sleep Run 2 | 2026-09-28 | 2026-10-02 | same | ? |

**Days Used is Andrea's call.** About 4.5 if the recording was stopped at the post-sampling read. If it was not stopped, the tag kept recording to its auto-stop (planned 10-04 ~13:00), about 6.1 days, and that is what the battery spent.

## 3. `NANOTAG behavioral`

- **47, 48, 50, Day −2 (09-28) Time = "PM Session".** Their Run 1 `.nta` files were **saved** at 09:59 (47), 10:30 (50) and 10:36 (48), and their Run 2 was programmed to start at 11:00, so the reads were in the **morning**. Enter the actual read times if known; otherwise "AM, before 10:00 / 10:30 / 10:36". (File save times run 30–80 min after the logged read for the other mice, so they are an upper bound only.)
- **43 block, Day 1 (10-01) and Day 2 (10-02) rows** (B32:G33 if the layout is as in the 09-28 handover): they still read "Scheduled … / Pending". Change them like the Day 0 row: Time "—", Stage "—", Notes "Excluded: animal died on Day −2 (2026-09-28)", Score "Excluded".

## 4. Check only, do not change

- `NANOTAG sampling`: the value after the Organ cell in each row (41: 4, 42: 3.3, 44: 33.8, 49: 32.2, 45: 33, 46: 32.2, 47: 31.6, 48: 33.5, 50: 32.3) looks like body weight at sampling, not a note or a **dissection time**. The dissection times matter for the oxidative-stress assays (09-28 handover, point 12). Check which column they are in, and fill in `P` (Dissection time) from the day's notes.

## History

> [!history]
> - **2026-10-05** — Written alongside the merged analysis. Supersedes the "Run 2 discarded" parts of [[2026-09-28-HLBNSL-sheet-handover]] (points 10 and 11 and the run-2 notes); every other point of that handover stands.

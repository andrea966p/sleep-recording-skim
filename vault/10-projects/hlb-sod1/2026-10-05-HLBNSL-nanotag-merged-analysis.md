---
tags: [experiment, nanotag, sod1, sleep, analysis, NS-SL, NW-SL, completed]
created: 2026-10-05
status: complete
cohort: HLBNSL (NS-SL + NW-SL)
---

# HLBNSL nanotag: Run 1 + Run 2 merged, full re-analysis (2026-10-05)

> [!abstract] TL;DR
> **What this is:** the second analysis of the nanotag SOD1 batch ([[2026-09-14-HLBNSL-nanotag-SOD1-sleep]]). The first (2026-10-01) used Run 1 only. This one joins Run 2, cuts only the logged handling and test windows, and re-runs everything. The full report and methods live in the NAS analysis folder (`02_Data_Sleep/andrea/HLBNSL_nanotag_ANALYSIS_2026-10-05/`).
>
> **Results, in order of weight:**
> 1. **No detectable effect of SOD1 on sleep.** Treatment days 3–15: SOD1 793 ± 21 vs water 768 ± 39 min/day (p = 0.61). Change from baseline +99 vs +87 (p = 0.77). SOD1 effect +11 min/day, 95% CI −130 to +156. The result is the same at every immobility cutoff (24–60 s).
> 2. **Handling and testing raise sleep in both groups.** Dark-phase sleep is **30.4 vs 30.4%** on the undisturbed days (09-20 → 09-25) and **41.1 vs 39.1%** on the handling and test days (09-26 → 10-01). The merged treatment means blend the two; for an undisturbed estimate use the first six days.
> 3. **One consistent pattern, still a hypothesis.** SOD1 mice are quieter in the light phase, so their rhythm amplitude rose: RA change +0.06 vs −0.03, **p = 0.029** (3 vs 4, complete separation, the floor p for that n). The direction holds on the undisturbed days (p = 0.09). But SOD1 RA was already lower at baseline (p = 0.03), and about 35 tests were run.
> 4. **The merge is clean.** With Run 2 withheld, the new code reproduces the 2026-10-01 tables exactly (0 differences in 125 rows), and the exported per-mouse CSVs match the analysis bin for bin.
> 5. **Power:** detecting 1 h/day would take about 20 mice per group.

## What was done

| Step | Result |
|---|---|
| Code moved into the repo | `nanotag/analysis/` (Desktop path symlinked), runs under `/usr/bin/python3`; unchanged code reproduces the 2026-10-01 tables byte for byte on this machine |
| Run 2 read | 9 files, 09-28 10:00 (SOD1) / 11:00 (water) → 10-02 20:51–21:40, no gaps. 🔴 **All named `HLBNSSL_<n>`, water mice included**, so mice are now identified by header tag ID. 🔴 **Temperature `Out of range`** from 19:45–20:40 on 10-02 (post-mortem cooling) crashed the parser; now skipped and counted |
| Windows | 7 windows from the behavioral tab (table below); the 10-02 cut also removes the post-mortem tail |
| Merge | Each file scored on its own, windows removed, files joined per mouse: 83,025 bins (11.5 d) of treatment per mouse, last kept bin 10-02 13:59:48 |
| Coverage rule | A light or dark phase with < 6 h recorded is left out; only the 10-02 morning (5 h) falls under it |
| New table | `treatment_split.csv`: undisturbed vs handling + test days |
| Bug fixed | The actogram drew the 09-28 08:45–11:00 hatch only on the 09-27 row (by the window's start day), so 09:00–11:00 on 09-28 looked like rest. Now clipped to each row |
| Deliverables | `report.html`, `methods.html`, `.docx` × 2, `figures.pptx`, rebuilt from the HTML by `nanotag/report/build.sh` |
| NAS | Per-mouse folders (98 files), analysis folder, pilot data (19 files); all verified by cache-dropped read-back |

### What was removed

| Date | Window | Log |
|---|---|---|
| 09-26 | 14:00–16:00 | Handling Day −4, 14:14 (41) → 15:56 (48) |
| 09-27 | 16:00–18:00 | Handling Day −3, 16:00 (41) → 17:25 (50) |
| 09-28 | 08:45–11:00 | Tag reads from 08:30; 43 died ~10:00; first Run 2 hour of the SOD1 mice |
| 09-29 | 16:00–18:00 | Handling Day −1, 16:03 (41) → 17:15 (50) |
| 09-30 | 14:00–17:00 | Day 0 Y-maze, cages in the test room |
| 10-01 | 14:00–18:00 | Day 1 NOR habituation, test room 14:00 → back 17:25 |
| 10-02 | 14:00 → end | Day 2 NOR T1/T2, sampling, post-mortem tail |

## Run 1 only vs merged (treatment period, group means)

| Measure | Run 1 SOD1 | Run 1 water | p | Merged SOD1 | Merged water | p |
|---|---|---|---|---|---|---|
| Total sleep (min/day) | 763 | 750 | 0.81 | 793 | 768 | 0.61 |
| Light phase, % asleep | 74.1 | 72.0 | 0.41 | 74.3 | 72.0 | 0.34 |
| Dark phase, % asleep | 31.9 | 32.1 | 0.97 | 35.8 | 34.7 | 0.84 |
| Share of activity in dark | 0.866 | 0.823 | **0.04** | 0.852 | 0.810 | 0.09 |
| Interdaily stability | 0.72 | 0.68 | 0.52 | 0.61 | 0.60 | 0.93 |
| Total sleep change | +70 | +66 | 0.94 | +99 | +87 | 0.77 |
| RA change | +0.09 | +0.02 | 0.09 | +0.06 | −0.03 | **0.029** |

The added days raise dark-phase sleep and lower day-to-day stability in both groups. Light-phase sleep does not move. The one Run-1 treatment p below 0.05 (share of activity in the dark) is 0.09 with Run 2 added. The RA change goes from 0.09 to 0.029.

![[2026-10-05-HLBNSL-nanotag-daily-sleep.png]]
*Daily sleep by group (report Figure 1). Dark-phase sleep is flat at ~30% until 09-25 and climbs from the first handling day.*

![[2026-10-05-HLBNSL-nanotag-change-from-baseline.png]]
*Change from baseline, SOD1 vs water (report Figure 4). Every sleep interval crosses 0. RA (last column) separates completely, which with 3 vs 4 mice is p = 0.029.*

![[2026-10-05-HLBNSL-nanotag-rhythm.png]]
*Activity and daily rhythm (report Figure 5). The only * is RA at baseline, before treatment.*

![[2026-10-05-HLBNSL-nanotag-actograms.png]]
*Actograms (report Figure 6). Hatched = removed. The burst at ZT2–3 on 09-28 follows the morning's reads, in both groups.*

## Reading it

- **Group comparison:** valid. Every disturbance acted on both groups at the same times, and the windows were taken from the log, not from the data.
- **Absolute amounts:** not undisturbed values. Half the treatment period is handling and test days. Quote the undisturbed days (Table 3 of the report) for any home-cage estimate.
- **RA:** a target for NS-SD / NW-SD, not a finding. To make it testable, pre-register light-phase activity and RA as the primary rhythm readouts for the next batch.
- **Not done here:** an undisturbed-days-only version of every figure. Only the sleep-amount and rhythm splits were computed (report Table 3; RA split in the rhythm callout).

## Changed on 2026-10-05, beyond the merge

- `.nta` file times are **save** times, 30–80 min after the logged read. They were nearly used as read times for 47/48/50 ("PM Session" in the log); the report says only that those reads were in the morning.
- The 2026-10-01 report linked its methods page as a claude.ai artifact in another organisation, which this session cannot reach. The new report links `methods.html` in the same folder.

## History

> [!history]
> - **2026-10-05** — Analysis run and written up. Previous outputs kept as `previous_run1only_report_2026-10-01/` in the NAS analysis folder (locally `out/HLBNSL_run1only_2026-09-28/`).

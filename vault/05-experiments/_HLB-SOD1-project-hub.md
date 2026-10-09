---
tags: [hub, project, hlb, sod1, sleep, eeg, nanotag]
created: 2026-10-06
status: active
---

# HLB SOD1 project hub: what the project is, what was tried, where it stands

> [!abstract] TL;DR
> - **The project.** Sponsored by HLB (Korean proposal dated 2025-12-05). PI Kim Jakyung (KAIST); researchers Jung Dayeon (Diane) and Andrea Piazzola. Question: does **oral microbial superoxide dismutase (SOD1)** reduce oxidative stress in the hippocampus and cortex and protect **sleep structure** and **cognition** under **chronic sleep restriction**?
> - **Planned readouts:**
>   - sleep architecture (NREM, REM, wake) by EEG/EMG;
>   - open field, Y-maze and novel object recognition;
>   - tissue MDA, 8-isoprostane and SOD activity in cortex, hippocampus, liver and heart.
> - **What happened.**
>   - Gavage was replaced by voluntary drinking. That took March to July of bottle and dose work, and ended at **6.8 U/mL for 20.4 U/day** at about 3 mL/day.
>   - Four EEG/EMG batches followed (W-SD, S-SD, S-SL, W-SL; August to September). The rig lost most of its time to troubleshooting, and only a handful of mice are scoreable at both timepoints.
>   - **Since September, sleep is measured with implanted nanotags**: the first batch is NS-SL / NW-SL, the next is NS-SD / NW-SD.
> - **What the pivot costs.** Immobility-based sleep gives sleep amount, bouts and daily rhythm. It gives **no NREM/REM split and no EEG slow-wave activity**, the classic marker of sleep pressure after deprivation. The "sleep architecture" aim shrinks to sleep/wake amount and consolidation. Say so in the final report.
> - **Before NS-SD / NW-SD (surgery 2026-10-12):** four design points need a decision ([below](#before-ns-sd-nw-sd-four-decisions)). The most urgent: **record activity only**, so one 20-day run covers 10-19 → 11-06 with no read in the middle.

## Design: proposal vs what is running

| | Proposal (2025-12) | Mid-term plan (2026-07) | Running now (nanotag) |
|---|---|---|---|
| Groups | Normal sleep ± SOD, chronic sleep restriction ± SOD | same 4 | the same 4, one pair per batch: SL (sleep ad lib) and SD |
| n | 15 M + 15 F per group | 10 M + 10 F (rig limit: 8 at once) | 4–5 M per arm per batch |
| SOD | gavage 20 U/day, 5 days | drinking water, 3.4 → **6.8 U/mL** (20.4 U/day at ~3 mL) | 6.8 U/mL from 3 days after baseline |
| Sleep restriction | 4 h/day (09:00–13:00), 7 days, gentle handling + automated | same, CSD start on a Friday | gentle handling; length and hours to confirm (below) |
| Sleep readout | EEG/EMG, NREM/REM/wake | EEG/EMG | nanotag immobility, 12 s bins |
| Cognition | Y-maze, NOR (2 h retention) | + open field | Y-maze Day 0, NOR habituation Day 1, NOR T1/T2 + sampling Day 2 |
| Tissue | MDA, 8-isoprostane, SOD activity | same | same (sampled 2026-10-02 for HLBNSL) |
| Strain | C57BL/6J | 6JBomTac preferred (intact *Nnt*) | per registry |

Statistics in the proposal: two-way (repeated-measures) ANOVA with Tukey. The nanotag analysis uses exact permutation tests at its small n ([[2026-10-05-HLBNSL-nanotag-merged-analysis]]). Reconcile the two before the final report.

## Batches so far

| Batch | When | Sleep method | Outcome | Page |
|---|---|---|---|---|
| Intake trials ("failed batches") | 2026-03 → 07 | none | Bottle and dose work: 20 mL glass tube, bent ball-bearing nozzle, 6.8 U/mL | Drive sheet `SOD1_Mouse_Intake_Monitoring_failed_batches`; mid-term report |
| W-SD (HLBWSD) | 08-10 → 08-28 | EEG/EMG | Recovery comparison n = 1 at rung 3 | [[2026-08-28-W-SD-cohort-closeout]] |
| S-SD (HLBSSD) | 08-16 → 09-03 | EEG/EMG | n = 0 scoreable at any timepoint | [[2026-08-24-S-SD-first-hour-screen]] |
| S-SL (HLBSSL) | 08-31 → 09-18 | EEG/EMG | 3 scoreable at both timepoints (31, 33, 35) | memory `s-sl-has-sleep-data-n3` |
| W-SL (HLBWSL) | 09-03 → 09-21 | EEG/EMG | Scoreable at both timepoints: HLBWSL24 | [[2026-09-18-W-SL-light-phase-sleep]] |
| **NS-SL / NW-SL (HLBNSSL / HLBNWSL)** | 09-14 → 10-02 | **nanotag** | 4 SOD1 vs 5 water; no detectable sleep effect | [[2026-09-14-HLBNSL-nanotag-SOD1-sleep]] |
| **NS-SD / NW-SD (HLBNSSD51–55 / HLBNWSD56–60)** | surgery 10-12 → sampling 11-06 | nanotag | planned | below |

The EEG data are not wasted: the scoreable EEG mice are the only ones with NREM/REM, and they are SL/SD pairs too. Pooling across methods is not possible, but they can stand as a small EEG sub-study beside the nanotag batches.

**Did SOD1 change sleep? (2026-10-06, the four EEG batches as a 2x2: [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]])**
- **Without deprivation: no detectable effect.** SOD1 vs water after about a week on treatment: 61.1 vs 60.6 % of 24 h asleep, n = 3 vs 6, p = 0.96. With the EMG notch, 56.2 vs 53.7 %, n = 6 vs 8, p = 0.24.
- **After deprivation: n = 1 per arm, with an EMG rescue.** The official staging has no S-SD recovery. Measuring EMG between the 60 Hz harmonics from the raw 1000 Hz file rescues **HLBSSD15** at both timepoints; this was validated against the notched staging (κ 0.95). It rebounds +6.6 points from 13:00 to 09:00 against water HLBWSD08's +16.1, an interaction of −13.8 points, but HLBSSD15 had the highest baseline of all. A case, not a result: [[2026-10-06-S-SD-EMG-rescue-between-harmonics]].
- ⇒ From the EEG, the SOD1 × deprivation question stays open. The EEG and nanotag findings are reported separately, never pooled or used to confirm each other.

**Manual scoring of the scoreable EEG mice (started 2026-10-07).** The automatic staging above is being checked by hand in
SleepStager, which now opens the per-mouse CSV. First mouse: HLBSSL33 Recovery, epochs 1–840 scored ([[2026-10-07]]).
How: [[02-procedures/sleepstager-user-guide]]. What the calls rest on: [[06-references/sleep-scoring-handbook]].

## Before NS-SD / NW-SD: four decisions

From the sheet Registry (read 2026-10-06): surgery 10-12, single housing 10-17, **homecage baseline from 10-19**, SOD1 and recording from 10-22, **sleep deprivation from 11-02**, Y-maze 11-04, NOR 11-05, **sampling 11-06**.

1. **Tag settings: activity only (recommended).** From 10-19 to 11-06 is 18 days. At 12 s activity + 5 min temperature the memory holds 8 days, so the tags would stop around 10-27 and need reads around 10-27 and 11-04. **11-04 is the Y-maze day, and reads mean handling during SD week.** Activity alone holds **20 days**, so one run from 10-19 reaches 11-08 with no read until after sampling. The HLBNSL report already found the temperature channel adds little (59–79% of it is activity). The battery covers this either way (~60 days).
2. **The SD hours are the treatment, not noise.** The HLBNSL rule removes every handling window. For SD batches, the deprivation hours must instead be analysed as their own state:
   - **wakefulness during SD**: was the mouse actually kept awake? (Nagai et al. 2017 report 95% of 7 h);
   - **recovery sleep** after SD ends.
   
   `cohort.py` needs an `SD` window list alongside `EXCLUDE` before this batch is analysed.
3. **How long, and when, is the deprivation?** The master schedule says 7 days, 09:00–13:00. The 2026-09-28 handover says 09:00–15:00 for the next batch, with every mouse kept awake until the last has finished testing. The Registry gives SD from 11-02 with sampling on 11-06, which is 5 days. Settle the length, the hours, and whether the mice are kept awake through the 2 h NOR retention interval. The analysis windows follow from that.
4. **Read the tags at sampling, then stop them.** The HLBNSL tags kept logging post-mortem. Also log the read time per mouse (not "PM Session").

The baseline at surgery + 7 days (10-19) already meets the ≥ 7-day recovery the literature uses ([[nanotag-kissei-device-and-literature]]); HLBNSL's day +3 did not.

## What nanotag can and cannot answer for the project's aims

| Aim | Nanotag answers | Does not answer |
|---|---|---|
| Protect sleep structure | Total sleep, light/dark split, bout length and number (fragmentation), rhythm (IS/IV/RA), SD verification, recovery sleep amount | NREM vs REM, slow-wave activity, spindles; immobility counts quiet wake as sleep |
| Preserve cognition | — (Y-maze, NOR do) | |
| Reduce oxidative stress | — (tissue assays do) | |

Validating the nanotag in a few EEG/EMG mice on our own rig, scored over the same 24 h, would give the first mouse accuracy figure for this device. It would let nanotag results speak to "sleep" with a known error.

## Drive (HLB project folder)

`https://drive.google.com/drive/folders/1gwRlmVI0ieCXaXBpRGf6c_mjXsCFgR0n`
- **Top level:**
  - research proposal (Korean PDF; English translation as a Google Doc);
  - project plan (pptx/pdf);
  - `SOD1 Chronic Sleep Deprivation Master Schedule and Protocol`;
  - mid-term reports (2026-04 and 2026-07 for the professor);
  - intake trial decks and Prism files (Diane);
  - NOR protocol (JoVE).
- `SOD1 dosage and usage/`: the intake registry sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO`, the failed-batches sheet, the SOD dose calculator, the 2026-09-28 handover.
- `Nanotag/`: the 2026-10-01 Run-1-only report, methods and figures, plus the hand-habituation journals. **`Nanotag/HLBNSL_merged_Run1+Run2_2026-10-05/`** (uploaded 2026-10-06, 15 files, sizes checked) holds the merged report, methods and figures as docx/pptx/html, the sheet handover, and zips of the per-mouse data (Baseline and Treatment per batch, raw reads included), the figures, the tables and the pilot data. The same content is on the SKIM NAS, unzipped.
- `Experiments/`: `Acute_SD_Behavioral_Protocol.docx`, monthly planner.
- `Report HLB/`, `Staci prof progress meeting/`: progress decks (March to July 2026).

## History

> [!history]
> - **2026-10-06** — Hub created from the Drive project folder (proposal, master schedule, mid-term report 2026-07, intake sheet README) after the nanotag work moved into the vault.

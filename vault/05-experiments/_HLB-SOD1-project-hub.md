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
> - **NS-SD / NW-SD is running (surgery 2026-10-12, sampling 2026-11-02).** Schedule settled 10-12 ([below](#ns-sd-nw-sd-final-schedule-decided-2026-10-12)): SOD1 11 days from 10-22, 4-day SD 10-30 → 11-02, one tag read on 10-27 (the tag holds 9 days, not 20).

## Design: proposal vs what is running

| | Proposal (2025-12) | Mid-term plan (2026-07) | Running now (nanotag) |
|---|---|---|---|
| Groups | Normal sleep ± SOD, chronic sleep restriction ± SOD | same 4 | the same 4, one pair per batch: SL (sleep ad lib) and SD |
| n | 15 M + 15 F per group | 10 M + 10 F (rig limit: 8 at once) | 4–5 M per arm per batch |
| SOD | gavage 20 U/day, 5 days | drinking water, 3.4 → **6.8 U/mL** (20.4 U/day at ~3 mL) | 6.8 U/mL from 3 days after baseline |
| Sleep restriction | 4 h/day (09:00–13:00), 7 days, gentle handling + automated | same, CSD start on a Friday | gentle handling 09:00–15:00, 4 days (acute SD protocol, NS-SD) |
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
| **NS-SD / NW-SD (HLBNSSD51–55 / HLBNWSD56–60)** | surgery 10-12 → sampling 11-02 | nanotag | running | below |

The EEG data are not wasted: the scoreable EEG mice are the only ones with NREM/REM, and they are SL/SD pairs too. Pooling across methods is not possible, but they can stand as a small EEG sub-study beside the nanotag batches.

**Did SOD1 change sleep? (2026-10-06, the four EEG batches as a 2x2: [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]])**
- **Without deprivation: no detectable effect.** SOD1 vs water after about a week on treatment: 61.1 vs 60.6 % of 24 h asleep, n = 3 vs 6, p = 0.96. With the EMG notch, 56.2 vs 53.7 %, n = 6 vs 8, p = 0.24.
- **After deprivation: n = 1 per arm, with an EMG rescue.** The official staging has no S-SD recovery. Measuring EMG between the 60 Hz harmonics from the raw 1000 Hz file rescues **HLBSSD15** at both timepoints; this was validated against the notched staging (κ 0.95). It rebounds +6.6 points from 13:00 to 09:00 against water HLBWSD08's +16.1, an interaction of −13.8 points, but HLBSSD15 had the highest baseline of all. A case, not a result: [[2026-10-06-S-SD-EMG-rescue-between-harmonics]].
- ⇒ From the EEG, the SOD1 × deprivation question stays open. The EEG and nanotag findings are reported separately, never pooled or used to confirm each other.

**Manual scoring of the scoreable EEG mice (started 2026-10-07).** The automatic staging above is being checked by hand in
SleepStager, which now opens the per-mouse CSV. First mouse: HLBSSL33 Recovery, epochs 1–840 scored ([[2026-10-07]]).
How: [[02-procedures/sleepstager-user-guide]]. What the calls rest on: [[06-references/sleep-scoring-handbook]].

## NS-SD / NW-SD: final schedule (decided 2026-10-12)

> [!important] This replaces the 10-06 "four decisions" plan
> The 10-06 version of this section read the old Registry (SD 11-02, sampling 11-06) and recommended one 20-day activity-only run. **The 20 days was wrong**: it is a misprint in Kissei's English manual. The Japanese manual and nanotagViewer both give **9 days** at 12 s activity with no temperature ([[nanotag-kissei-device-and-literature]]). Andrea settled the plan below with the nanotag session on the SKIM workstation on 2026-10-12. The sheet was edited by an agent and checked clean (no `#REF!`) on 2026-10-13.
>
> Source: `~/Desktop/Andrea/nanotag/HANDOVER_sheet_NS-SD_NW-SD_batch_2026-10-12.md` on the workstation (corrected 10-13), and the workstation memory `nanotag-sd-batch`.

**What changed from the old Registry plan, and why:**
- **SOD1 / water and intake monitoring: 11 tracking days, 10-22 → 11-02** (was 15). The professor wanted this batch's timing to match the EEG mice's baseline. Andrea first asked for 10 days, then made it 11 so that 10-22 marks both the end of baseline and liquid Day 1.
- **Sampling Mon 11-02** (was 11-06). Andrea wrote "Monday 23rd"; Monday 2 November is the only date that fits 11 days from 10-22.
- **Sleep deprivation: 4 days, Fri 10-30 → Mon 11-02, gentle handling with a soft brush 09:00–15:00**, following `Acute_SD_Behavioral_Protocol.pdf` (Day −1 to Day 2). Registry `W = Z − 3`.
- **Single housing Fri 10-16** (was 10-17). Registry `R = S − 3`.
- **Tags: 12 s activity, no temperature, stop at full, threshold 170/170.** That holds 9 days, so the batch needs **two recordings and one read on a live mouse**. Andrea kept 12 s rather than 30 s: a simulation showed 30 s lowers sleep % by about 7 points.

| Date | Protocol day | Liquid day | Event |
|---|---|---|---|
| Mon 10-12 | | | Surgery, all 10 mice. Tags reused from HLBNSL: 51 = 20639 … 60 = 20648 |
| Fri 10-16 | | | Single housing, move to the recording room |
| Mon 10-19 09:00 | | | Tag recording 1 starts (reservation set at surgery). Homecage baseline, plain water |
| Thu 10-22 | −9 | 1 | Baseline ends; SOD1 / UV water starts |
| Sat 10-24 → Tue 10-27 | −7 → −4 | 3–6 | Hand habituation 14:00–16:00 (option A, chosen) |
| Tue 10-27 ~16:00 | −4 | 6 | **The only live read**: read + restart at the end of the session, mouse in a cupped hand, never on the grid (HLBNSSL43 died in grid restraint). Recording 2 fills ≈ 11-05 |
| Wed 10-28 → Fri 10-30 09:00 | −3, −2 | 7–8 | No handling at all: the clean pre-SD window |
| Fri 10-30 | −1 | 9 | SD 09:00–15:00 |
| Sat 10-31 | 0 | 10 | SD → Y-maze 15:00 |
| Sun 11-01 | 1 | 11 | SD → NOR habituation 15:00. Last fresh bottle |
| Mon 11-02 | 2 | Out weighed | SD → NOR T1 15:00 → T2 17:10 → sampling ~17:25. Final read after sampling with "Stop recording after reading data" |

- **The read must fall after 10-24 ~19:00 and before 10-28 09:00.** Recording 1 is full on 10-28 09:00, and recording 2 must still be running at sampling.
- **Interleave NS and NW mice** in every session (51, 56, 52, 57, …) so time of day is not a group difference.
- **Age at sampling 17.0 weeks** (protocol target 18). The sampling tab will show every mouse amber; the rule was left alone.
- SOD1 exposure at sampling is 11 days against the protocol's 13 ("Days −10 to 2"). Andrea's decision.

**Still open (Andrea, as of the 10-13 sheet check):**
- The **cracked tag** seen after the ethanol soak: which ID, and is it implanted?
- **Bottle swap time on SD days** (10-30 → 11-01). SD ends at 15:00 when testing starts; the README's "1 pm" was the EEG timing.
- Are mice **kept awake through the 2 h NOR retention interval** on 11-02? And the protocol's 14:30 holding-room acclimation overlaps SD, which runs to 15:00. Already agreed: every mouse stays awake until the last mouse of the day is tested.
- The sampling details copied from NS-SL ("40sec sampling", organ list): check they still apply.

**Still true from the 10-06 plan:**
- **The SD hours are the treatment, not noise.** The HLBNSL rule removes every handling window. Here the deprivation hours must be analysed as their own state: wakefulness during SD (was the mouse actually kept awake? Nagai et al. 2017 report 95% of 7 h) and recovery sleep after SD ends. `cohort.py` needs an `SD` window list alongside `EXCLUDE`, plus the usual new-batch `FOLDERS` / `TAG` / `SOD1` / `WATER` / `SURGERY` / `EXCLUDE` / `SOD1_START` blocks, before this batch is analysed.
- **Read the tags at sampling, then stop them**, and log the read time per mouse (not "PM Session").
- The baseline at surgery + 7 days (10-19) meets the ≥ 7-day recovery the literature uses; HLBNSL's day +3 did not.

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
> - **2026-10-16** — NS-SD / NW-SD section replaced with the final schedule decided on the workstation 2026-10-12 (sampling 11-02, 4-day SD 10-30 → 11-02, one tag read 10-27). The 10-06 "20-day activity-only run" recommendation was based on a misprint in the English manual.
> - **2026-10-06** — Hub created from the Drive project folder (proposal, master schedule, mid-term report 2026-07, intake sheet README) after the nanotag work moved into the vault.

---
type: experiment
area: hlb-sod1
status: active
created: 2026-10-22
summary: "Second nanotag batch: oral SOD1 vs water under 4 days of gentle-handling SD; tags from 2026-10-22, SOD1 12 days, sampling Thu 2026-11-05"
cohort: NS-SD + NW-SD (HLBNSSD51-55, HLBNWSD56-60)
tags: [experiment, nanotag, sod1, sleep-deprivation, ns-sd, nw-sd]
---

# NS-SD / NW-SD: oral SOD1 vs water under sleep deprivation, home-cage sleep by nanotag

> [!abstract] TL;DR
> - **Question.** Does oral SOD1 change home-cage sleep, the response to 4 days of sleep deprivation (SD), Y-maze / NOR
>   and tissue oxidative stress, against UV water? The SD pair of the first nanotag batch
>   [[2026-09-14-HLBNSL-nanotag-SOD1-sleep]] (NS-SL / NW-SL).
> - **Arms.** **NS-SD** = SOD1 6.8 U/mL in drinking water, HLBNSSD51-55. **NW-SD** = UV water, HLBNWSD56-60.
> - **Schedule (Andrea, re-planned 2026-10-19, sampling moved 2026-10-21):** tag Run 1 from **Thu 10-22 09:00**, 48 h
>   baseline to 10-24, **SOD1 / water from Sat 10-24 for 12 days**, one live tag read Fri 10-30 ~08:30-09:00,
>   **SD Mon 11-02 → Thu 11-05** 09:00-15:00, Y-maze 11-03, NOR habituation 11-04, NOR + **sampling Thu 11-05**.
> - **Status:** running. No data read yet. Answer: (fill in when done).
> - 🛑 **Report these results on their own.** Never pooled with the EEG batches, never "the nanotag agrees":
>   [[2026-10-06-eeg-and-nanotag-findings-reported-separately]].

## Setup
- **Mice:** 10 implanted on Mon 2026-10-12 (surgery). Single-housed and moved to the recording room on **Mon 10-19**
  (the 10-16 plan did not happen; [[2026-10-19]]). Age at sampling 17.4 weeks ([[2026-10-21]]).
- **Tags:** reused from HLBNSL, 51 = 20639 … 60 = 20648 (full map: the sheet's `NANOTAG registry`). **12 s activity, no
  temperature, stop at full, threshold 170/170.** That memory holds **9 days** (Kissei's English manual misprints 20;
  [[nanotag-kissei-device-and-literature]]), so the batch needs two recordings and one read on a live mouse.
  Andrea kept 12 s over 30 s: a simulation showed 30 s lowers sleep % by about 7 points ([[hlb-sod1-design]]).
- **Recordings:** all 10 tags re-set on 10-19. **Run 1** programmed 10-22 09:00 → 10-30 09:00. **Run 2** starts at the
  10-30 read, full ≈ 11-08 09:00, so sampling day is recorded ([[2026-10-21]]). Use dim red light when entering
  before lights-on (09:00).
- **Source of truth for dates:** the sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO`, `NANOTAG registry` rows 19-29.
  Changes to it go through [[sod1-sheet-change-log-workflow]].
- **Procedure:** [[nanotag-recording-and-analysis]].

## Schedule (as of 2026-10-21)

| Date | Event |
|---|---|
| Mon 10-12 | Surgery, all 10 mice |
| Mon 10-19 | Single housing + move to the recording room; all 10 tags re-set |
| Thu 10-22 09:00 → Sat 10-24 09:00 | 48 h homecage baseline, plain water. Tag Run 1 starts 10-22 09:00 |
| Sat 10-24 | SOD1 / UV water + liquid monitoring start (12 days to sampling) |
| — | No hand habituation (sheet: "SD batches: hand habituation not required") |
| Fri 10-30 ~08:30-09:00 | The single live read + Run 2 start (dim red light) |
| 10-30 → 11-02 09:00 | Undisturbed on treatment (clean 48 h window 10-31 09:00 → 11-02 09:00) |
| Mon 11-02 → Thu 11-05 | SD 09:00-15:00, gentle handling, 4 days (Day −1 to Day 2) |
| Tue 11-03 | Y-maze 15:00 |
| Wed 11-04 | NOR habituation 15:00 |
| Thu 11-05 | NOR T1 15:00 → 2 h rest, no SD (Andrea) → T2 17:10 → sampling straight after each T2 |

Interleave NS and NW mice in every session (51, 56, 52, 57, …) so time of day is not a group difference
(10-12 plan, [[hlb-sod1-design]]). Read the tags at sampling, then stop them, and log the read time per mouse.

## Prediction (write before looking)
Fixed before the data arrive (from [[hlb-sod1-design]], 2026-10-19):
- **Analysis windows:** baseline 10-22 09:00 → 10-24 09:00; SOD1 effect on undisturbed sleep = 10-31 09:00 → 11-02 09:00
  against baseline; SD efficacy = sleep 09:00-15:00 on each SD day plus 24 h totals; recovery = 11-02 15:00 → 11-03
  09:00 (the only SD day without a test) against the same hours undisturbed. Immobility sleep shows rebound as extra
  minutes only, not intensity.
- **The SD hours are the treatment, not noise.** Analyse wakefulness during SD and recovery sleep after it; do not
  remove them as HLBNSL removed its handling windows.
- **Risk, stated in advance:** 6-8 h gentle handling has not been shown to raise hippocampal MDA, so a null SOD1-vs-water
  MDA result is ambiguous; sleep (SD efficacy, rebound) and Y-maze / NOR have a better chance. Literature and PMIDs:
  [[hlb-sod1-design#NS-SD / NW-SD: current schedule (re-planned 2026-10-19)]].
- **Sampling** at the end of SD, before recovery sleep; NS-SL (sampled after NOR T2 at the same clock time) is the
  same-ZT reference. Run MDA for both batches on one plate.

## Result
(fill in when done)

## Deviations from the protocol, recorded
- **SOD1 for 12 days**, not NS-SL's 15: Andrea does no SD or behaviour at weekends, so sampling moved from Sun 11-08 to
  Thu 11-05 on 2026-10-21 ([[2026-10-21]]).
- **No hand habituation** (both arms equally; [[hlb-sod1-design]]).
- Age at sampling 17.4 weeks against NS-SL's 18.1.
- The 2 h NOR retention interval is rest, not SD (Andrea, 2026-10-19).

## Open
- [ ] `nanotag/analysis/cohort.py` has no NS-SD blocks yet (`FOLDERS`, `TAG`, `SOD1`, `WATER`, `SURGERY`, `EXCLUDE`,
  `SOD1_START`) and no `SD` window list. Checked in the repo 2026-10-22. Needed before analysis.
- [ ] Sheet requests CHG-005 → CHG-009 (sent 2026-10-21): review after Claude for Sheets applies them
  ([[sod1-sheet-change-log-workflow]]).
- [ ] Still open from the 10-13 sheet check (Andrea): which tag cracked after the ethanol soak, and is it implanted;
  bottle swap time on SD days; whether the sampling details copied from NS-SL ("40sec sampling", organ list) still apply.
- [ ] Tissue endpoints and MDA plate shared with HLBNSL.

## Data
- Raw reads: SKIM workstation `~/Desktop/Andrea/nanotag/` (as for HLBNSL). NAS: per-mouse folders under
  `02_Data_Sleep/andrea/` once exported ([[nanotag-recording-and-analysis]]).
- Code: repo `nanotag/analysis/` (`cohort.py`, `nta_qc.py`, `export_nas.py`).

## How the plan got here
- **2026-10-06:** first plan read the old Registry (SD 11-02, sampling 11-06) and recommended one 20-day activity-only
  run. Wrong: 12 s activity without temperature holds 9 days, not 20 ([[2026-10-16]]).
- **2026-10-12** (workstation, brought into the vault 2026-10-16): 11 liquid days 10-22 → 11-02, hand habituation
  10-24 → 10-27, one read 10-27, SD 10-30 → 11-02, sampling Mon 11-02. Full table: [[hlb-sod1-design]].
- **2026-10-19:** re-planned against the literature after single housing slipped to 10-19: tag Run 1 from 10-22,
  48 h baseline, SOD1 from 10-24 (15 days, to match NS-SL), read 10-30, SD 11-05 → 11-08, sampling Sun 11-08
  ([[2026-10-19]]).
- **2026-10-21:** sampling moved to **Thu 11-05** (SOD1 12 days, SD 11-02 → 11-05), sheet requests CHG-005 → CHG-009
  ([[2026-10-21]]).

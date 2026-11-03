---
type: hub
area: hlb-sod1
status: active
created: 2026-10-06
summary: "HLB-sponsored study of oral SOD1 vs water on sleep, cognition and oxidative stress: four EEG batches (closed) and two nanotag batches (HLBNSL done, NS-SD / NW-SD running)"
tags: [hub, project, hlb, sod1, sleep, eeg, nanotag]
---

# HLB SOD1

> [!abstract] What this is
> HLB-sponsored project (PI Kim Jakyung, KAIST): does oral microbial SOD1 in drinking water protect sleep, cognition and tissue oxidative stress under sleep restriction?
> Sleep was measured by EEG/EMG in four batches (W-SD, S-SD, W-SL, S-SL; Aug-Sep 2026) and since September by implanted nanotags (HLBNSL, NS-SD / NW-SD), which give sleep amount but no NREM/REM.
> Design, batch list, schedules, literature and the Drive map: [[hlb-sod1-design]]. The rig, Allego and the analysis code have their own areas.

## Current state
- 2026-11-03: EEG of the four batches re-scored with the professor's SleepStager rule on a mains-free EMG, agent-reviewed: 15 paired W/NR/R mice (W-SD 1, S-SD 1, W-SL 7, S-SL 6) instead of 3; no detectable SOD1 effect on baseline sleep (52.0 vs 52.5 %, n = 10 vs 11, MDE 6 points) or on the SL recovery change; SD arms still n = 1 each, and HLBSSD18's recovery gain depends on its artefact mask. Against Andrea's reviewed HLBSSL33 R epochs (light, early dark ZT12–15, late dark ZT18–21; 14,077 epochs, rule-anchored): κ 0.952 / 0.941 / 0.932, all 0.949; dark sleep % about 2 points high. [[hlb-eeg-sleep-overview]]
- 2026-11-02: Final report draft v0.1 for the professor, the working document of the report (design, nanotag, behaviour, tissue, statistics plan, interpretation, limits); pending: intake, NS-SD SD + Y-maze, EEG (Andrea scores). Storyline and design rationale, incl. why the SD arm runs the Y-maze only: [[2026-11-02-hlb-sod1-final-report-draft]] · [[2026-11-02-hlb-final-report-storyline]]
- 2026-11-02: Tissue of the EEG cohorts re-derived from the raw ODs with the kit methods: hippocampal total SOD no SOD1 effect; hippocampal MDA higher in the SD cohorts (p = 0.007), no SOD1 effect; heart SOD crossover (interaction p = 0.0006, per mL = per mg since buffer was fixed per mg). Group = cohort, nothing causal. Next test: the same assays on the stored nanotag tissue. [[2026-11-02-EEG-cohorts-tissue-SOD-MDA-reanalysis]]
- 2026-11-02: HLBNSL behaviour battery final (Y-maze, open field, NOR; why 2-day NOR with 2 h retention): no detectable SOD1 effect on cognition, SOD1 more active (trend), n = 4 vs 5. NOR pose scoring validated against blinded hand scoring (2 raters, kappa 0.76); 9/9 mice explore the novel object more, confounded with the blue prism and its side. [[2026-11-02-HLBNSL-behaviour-battery-summary]] · [[2026-11-02-HLBNSL-nor-hand-validation-and-calibration]]
- 2026-10-31: NS-SD / NW-SD tag Run 1 analysed (baseline 10-22 → 10-24 vs SOD1 / water days 1-6, 5 vs 5): no detectable SOD1 effect on sleep (total sleep change +18 vs +1 min/day, p = 0.39); HLBNSL's RA lead not repeated (p = 0.24); 59's shoulder tag doubles its dark counts. Run 2 (SD) not read yet. [[2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1]]
- 2026-10-30: NS-SD / NW-SD re-planned: SD only Tue 11-03 + Wed 11-04 09:00-15:00, Y-maze Wed 15:00 then sampling, NOR dropped, SOD1 11 days. Tags read 10-30 18:00-19:00, Run 2 from 19:00 to 11-04 19:00 (gap 09:00-19:00, light phase). HLBNWSD59's tag stayed at the shoulder; HLBNSSD53 sprayed urine in the cage. Sheet CHG-012 → CHG-017 applied 2026-10-31 (CHG-017 = the 53/59 notes in registry I21 / I28). [[2026-10-30-NS-SD-two-day-SD-y-maze-only]] · [[2026-10-19-NS-SD-NW-SD-nanotag-study]]
- 2026-10-26: SPF batches (HLBSSPF01-05 SOD1, HLBWSPF01-05 UV water) plan for Tue 2026-10-27, from Andrea: S-SPF drinking-water SOD1 bottles off, then oral gavage 09:00 (straight metal needle, 0.2 mL; S-SPF SOD1 = 20.4 U at 102 U/mL, W-SPF water vehicle), SD 6 h 09:00-15:00, sampling 15:00 at the end of SD. In the sheet as CHG-010 (Registry `Notes`). Gavage solution: water (mL) = powder (mg) × 2.94, so 3.0 mg → 8.82 mL; S-SPF Day 6 `Water to add` fixed to this in CHG-011. [[2026-10-26]] [[2026-10-27]]
- 2026-10-26: Claude Code edits the SOD1 sheet directly with the Google Sheets connector, keeping the change log; CHG-010 was the first. [[sod1-sheet-change-log-workflow]]
- 2026-10-25: HLBNSL behaviour videos all cut to the trial window on `kaist-bilab-win` (Y-maze 480 s, OFT / NOR-T1 / NOR-T2 600 s from Andrea's start times); OFT and NOR tracked with the labmate's YOLO pose models, not EthoVision. [[hlbnsl-oft-nor-pose-tracking]] · [[2026-10-25-nor-day1-oft-feature-set]]
- 2026-10-24: sheet round 2 (CHG-005 → CHG-009) verified on an export: sampling Thu 11-05, SD 11-02 → 11-05, behavioural read row on 10-30, clean window 10-31 → 11-02; all approved and moved to History. New, outside the log: tabs `S-SPF` / `W-SPF` and EEG `Registry` rows 50-61 (HLBSSPF01-05, HLBWSPF01-05), not yet described in the vault. [[2026-10-24]]
- 2026-10-08: HLBSSL33 Recovery scored to epoch 8441 of 21,600 (39 %). [[2026-10-08]] [[_sleep-scoring-hub]]
- 2026-10-07: manual scoring of the scoreable EEG mice started in SleepStager (HLBSSL33 Recovery, epochs 1-840). [[2026-10-07]]
- 2026-10-06: EEG, the four batches as a 2x2: no detectable SOD1 effect without deprivation; after deprivation one mouse per arm (HLBSSD15 vs HLBWSD08, via an EMG rescue), a case, not a result. [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]] · [[2026-10-06-S-SD-EMG-rescue-between-harmonics]]
- 2026-10-05: nanotag HLBNSL (4 SOD1 vs 5 water, Run 1 + Run 2 merged): no detectable effect of SOD1 on sleep. [[2026-10-05-HLBNSL-nanotag-merged-analysis]]
- 2026-09-30: EEG mice scoreable at both timepoints: W-SD 1, S-SD 0, W-SL 1 (2), S-SL 1 (3). [[2026-09-30-scoreable-mice-on-the-24h-windows]]

## Start here
- [[2026-11-02-hlb-sod1-final-report-draft]]: the final report, draft v0.1 (what it shows and why)
- [[hlb-sod1-design]]: proposal vs what ran, every batch, the NS-SD schedules and literature, the Drive folder
- [[2026-10-19-NS-SD-NW-SD-nanotag-study]]: the running batch
- [[hlb-eeg-sleep-overview]]: what the EEG says about SOD1 (2026-11 re-score, every mouse)
- [[2026-10-05-HLBNSL-nanotag-merged-analysis]]: what the first nanotag batch says

## Rules that must not be broken
- 🛑 EEG/EMG and nanotag findings on SOD1 and sleep are reported separately: never pooled, never "the nanotag agrees", no nanotag value as a plausibility reference for EEG. [[2026-10-06-eeg-and-nanotag-findings-reported-separately]]
- 🛑 Every run is new mice unless Andrea says otherwise; a rig position is not an animal. [[2026-08-18-every-run-is-new-mice]]
- EEG "baselines" are already on treatment: SOD1 / water starts at tethering, so baseline = SOD1 without deprivation, not pre-treatment. [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]]
- Every change to the SOD1 sheet goes through the `Pending changes instructions` log (request, apply, verify by read-back, HISTORY), with Andrea's OK on the exact cells first; Claude Code writes it with the Google Sheets connector since 2026-10-26. [[sod1-sheet-change-log-workflow]]
- Nanotag: the mouse comes from the header tag ID, not the file name; the `.nta` file time is the save time, not the read time. [[2026-10-05-HLBNSL-nanotag-merged-analysis]] · [[2026-10-05-HLBNSL-sheet-handover-run2]]
- NS-SD: the SD hours are the treatment; analyse them, do not remove them as handling windows. [[2026-10-19-NS-SD-NW-SD-nanotag-study]]

## Open items
- [x] 2026-11-02: HLBNSL NOR hand validation done (6 clips, 2 raters, kappa 0.76); open only for a batch 2: counterbalance object identity and side. [[2026-11-02-HLBNSL-nor-hand-validation-and-calibration]]
- [x] 2026-10-30: HLBNSD (batch 2) NOR counterbalancing: no longer needed, NOR dropped for NS-SD / NW-SD. [[2026-10-30-NS-SD-two-day-SD-y-maze-only]]
- [ ] NS-SD Y-maze 11-04: log each mouse's Y-maze start time (real SD length per mouse) and put a ruler in frame. [[2026-10-30-NS-SD-two-day-SD-y-maze-only]]
- [x] 2026-10-31: HLBNWSD59 compared with the other nine: dark counts about 2x, dark sleep 15-16 %; change from baseline in range, absolute values not comparable. [[2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1]]
- [x] 2026-11-02: Verify the Palchykova et al. 2006 citation: checked on PubMed (abstract), Neurobiol Learn Mem 85:263-71, doi:10.1016/j.nlm.2005.11.005; 6 h SD right after training abolished 24 h recognition, delayed SD did not. [[2026-10-30-NS-SD-two-day-SD-y-maze-only]]
- [ ] NS-SD analysis code: Run 1 done in `nanotag/analysis/cohort_sd.py` (2026-10-31); the `SD` window list and Y-maze start times are still needed for Run 2. [[2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1]]
- [ ] NS-SD Run 1 report + methods (`.docx`), deferred by Andrea 2026-10-31. [[2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1]]
- [ ] SOD1 bottle time on 10-24 not logged (Andrea). [[2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1]]
- [x] 2026-10-24: CHG-005 → CHG-009 reviewed and moved to History. [[2026-10-24]]
- [ ] NS-SD questions for Andrea: cracked tag ID, bottle swap time on SD days, sampling details. [[2026-10-19-NS-SD-NW-SD-nanotag-study]]
- [ ] HLBNSL Run 2 sheet edits: not confirmed applied. [[2026-10-05-HLBNSL-sheet-handover-run2]]
- [x] 2026-10-26: sheet request route redesigned: Claude Code writes through the Google Sheets connector, on Andrea's instruction. [[sod1-sheet-change-log-workflow]]
- [ ] Rows 2-6 of the sheet's `Pending changes instructions` tab still describe the Claude for Sheets route; rewrite them as a logged change if Andrea wants. [[sod1-sheet-change-log-workflow]]
- [x] 2026-11-02: ANOVA vs permutation reconciled: estimation with CIs leads, exact permutation tests support, the proposal's two-way ANOVA kept for the tissue (report section 8). [[2026-11-02-hlb-sod1-final-report-draft]]
- [x] 2026-10-23: Andrea keeps off-site copies of the nanotag raw data. [[2026-10-23]]
- [x] 2026-11-02: The nanotag pivot's cost (no NREM/REM, quiet wake counts as sleep) is in the report's limitations. [[2026-11-02-hlb-sod1-final-report-draft]]
- [ ] Decide with the professor: run heart SOD, heart MDA and hippocampal MDA on the stored HLBNSL and NS-SD tissue (one plate, interleaved, blind, protein-normalised). [[2026-11-02-EEG-cohorts-tissue-SOD-MDA-reanalysis]]
- [ ] Ask HLB: is the SOD powder coated, Cu/Zn or Mn-SOD, stability in water. [[2026-11-02-hlb-sod1-final-report-draft]]
- [ ] Final report: intake and body weight (sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO`), NS-SD Run 2 + Y-maze, EEG section after Andrea's scoring. [[2026-11-02-hlb-sod1-final-report-draft]]

## Everything here
![[area.base]]

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
- 2026-10-26: SPF batches (HLBSSPF01-05 SOD1, HLBWSPF01-05 UV water) plan for Tue 2026-10-27, from Andrea: S-SPF drinking-water SOD1 bottles off, then oral gavage 09:00 (straight metal needle, 0.2 mL; S-SPF SOD1 = 20.4 U at 102 U/mL, W-SPF water vehicle), SD 6 h 09:00-15:00, sampling 15:00 at the end of SD. In the sheet as CHG-010 (Registry `Notes`). Gavage solution: water (mL) = powder (mg) × 2.94, so 3.0 mg → 8.82 mL; S-SPF Day 6 `Water to add` fixed to this in CHG-011. [[2026-10-26]] [[2026-10-27]]
- 2026-10-26: Claude Code edits the SOD1 sheet directly with the Google Sheets connector, keeping the change log; CHG-010 was the first. [[sod1-sheet-change-log-workflow]]
- 2026-10-25: HLBNSL Y-maze, hand-scored (final): SA% SOD1 60.5 vs water 62.8, no detectable difference; SOD1 more arm entries (g 1.2, p = 0.06). n = 4 vs 5. [[2026-10-25-HLBNSL-ymaze-hand-scored-results]]
- 2026-10-25: HLBNSL NOR from pose, provisional until hand scoring: d2 water +0.30, SOD1 +0.24, no group difference; the novel object was lower-right in every T2, where the mice already went (T1 57 %), so most of d2 is side preference (T1 → T2 rise 7/9 mice, p = 0.07; model1 gives the novel object +6 s and 9/9, p = 0.004, so this depends on the model until hand scoring). [[2026-10-25-HLBNSL-nor-pose-results]]
- 2026-10-25: HLBNSL open field (NOR day 1), YOLO pose model2, cross-checked by model1 (r ≥ 0.995 per mouse): SOD1 more active (64 vs 51 m, g +1.7, p = 0.11; less immobility, p = 0.06), no difference in centre time or thigmotaxis, no arena side preference. n = 4 vs 5. Floor scale still to confirm with a ruler in frame. [[2026-10-25-HLBNSL-oft-day1-results]]
- 2026-10-25: HLBNSL behaviour videos all cut to the trial window on `kaist-bilab-win` (Y-maze 480 s, OFT / NOR-T1 / NOR-T2 600 s from Andrea's start times); OFT and NOR tracked with the labmate's YOLO pose models, not EthoVision. [[hlbnsl-oft-nor-pose-tracking]] · [[2026-10-25-nor-day1-oft-feature-set]]
- 2026-10-24: sheet round 2 (CHG-005 → CHG-009) verified on an export: sampling Thu 11-05, SD 11-02 → 11-05, behavioural read row on 10-30, clean window 10-31 → 11-02; all approved and moved to History. New, outside the log: tabs `S-SPF` / `W-SPF` and EEG `Registry` rows 50-61 (HLBSSPF01-05, HLBWSPF01-05), not yet described in the vault. [[2026-10-24]]
- 2026-10-30: NS-SD / NW-SD re-planned: SD only Tue 11-03 + Wed 11-04 09:00-15:00, Y-maze Wed 15:00 then sampling, NOR dropped, SOD1 11 days. Tags read 10-30 18:00-19:00, Run 2 from 19:00 to 11-04 19:00 (gap 09:00-19:00, light phase). HLBNWSD59's tag stayed at the shoulder; HLBNSSD53 sprayed urine in the cage. Sheet CHG-012 → CHG-017 applied 2026-10-31 (CHG-017 = the 53/59 notes in registry I21 / I28). [[2026-10-30-NS-SD-two-day-SD-y-maze-only]] · [[2026-10-19-NS-SD-NW-SD-nanotag-study]]
- 2026-10-21: sampling moved from Sun 11-08 to Thu 11-05 (no SD or tests at weekends); sheet requests CHG-005 → CHG-009 sent, review pending. [[2026-10-21]]
- 2026-10-08: HLBSSL33 Recovery scored to epoch 8441 of 21,600 (39 %). [[2026-10-08]] [[_sleep-scoring-hub]]
- 2026-10-07: manual scoring of the scoreable EEG mice started in SleepStager (HLBSSL33 Recovery, epochs 1-840). [[2026-10-07]]
- 2026-10-06: EEG, the four batches as a 2x2: no detectable SOD1 effect without deprivation; after deprivation one mouse per arm (HLBSSD15 vs HLBWSD08, via an EMG rescue), a case, not a result. [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]] · [[2026-10-06-S-SD-EMG-rescue-between-harmonics]]
- 2026-10-05: nanotag HLBNSL (4 SOD1 vs 5 water, Run 1 + Run 2 merged): no detectable effect of SOD1 on sleep. [[2026-10-05-HLBNSL-nanotag-merged-analysis]]
- 2026-09-30: EEG mice scoreable at both timepoints: W-SD 1, S-SD 0, W-SL 1 (2), S-SL 1 (3). [[2026-09-30-scoreable-mice-on-the-24h-windows]]

## Start here
- [[hlb-sod1-design]]: proposal vs what ran, every batch, the NS-SD schedules and literature, the Drive folder
- [[2026-10-19-NS-SD-NW-SD-nanotag-study]]: the running batch
- [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]]: what the EEG says about SOD1
- [[2026-10-05-HLBNSL-nanotag-merged-analysis]]: what the first nanotag batch says
- [[sod1-sheet-change-log-workflow]]: how to change the intake sheet

## Rules that must not be broken
- 🛑 EEG/EMG and nanotag findings on SOD1 and sleep are reported separately: never pooled, never "the nanotag agrees", no nanotag value as a plausibility reference for EEG. [[2026-10-06-eeg-and-nanotag-findings-reported-separately]]
- 🛑 Every run is new mice unless Andrea says otherwise; a rig position is not an animal. [[2026-08-18-every-run-is-new-mice]]
- EEG "baselines" are already on treatment: SOD1 / water starts at tethering, so baseline = SOD1 without deprivation, not pre-treatment. [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]]
- Every change to the SOD1 sheet goes through the `Pending changes instructions` log (request, apply, verify by read-back, HISTORY), with Andrea's OK on the exact cells first; Claude Code writes it with the Google Sheets connector since 2026-10-26. [[sod1-sheet-change-log-workflow]]
- Nanotag: the mouse comes from the header tag ID, not the file name; the `.nta` file time is the save time, not the read time. [[2026-10-05-HLBNSL-nanotag-merged-analysis]] · [[2026-10-05-HLBNSL-sheet-handover-run2]]
- NS-SD: the SD hours are the treatment; analyse them, do not remove them as handling windows. [[2026-10-19-NS-SD-NW-SD-nanotag-study]]

## Open items
- [ ] HLBNSL NOR: hand-score the blinded validation subset in BORIS (`NOR-blind`, 4 clips; rules and score sheet in [[2026-10-26-HLBNSL-nor-hand-scoring]]) and compare with the pose scoring; then decide the endpoint. [[2026-10-25-HLBNSL-nor-pose-results]]
- [x] 2026-10-30: HLBNSD (batch 2) NOR counterbalancing: no longer needed, NOR dropped for NS-SD / NW-SD. [[2026-10-30-NS-SD-two-day-SD-y-maze-only]]
- [ ] NS-SD Y-maze 11-04: log each mouse's Y-maze start time (real SD length per mouse) and put a ruler in frame. [[2026-10-30-NS-SD-two-day-SD-y-maze-only]]
- [ ] HLBNWSD59: compare its activity levels with the other nine before using its tag data (tag at the shoulder, not the flank). [[2026-10-19-NS-SD-NW-SD-nanotag-study]]
- [ ] Verify the Palchykova et al. 2006 citation (post-training SD impairs object recognition) before it goes to HLB. [[2026-10-30-NS-SD-two-day-SD-y-maze-only]]
- [ ] `nanotag/analysis/cohort.py` needs the NS-SD blocks and an `SD` window list before analysis. [[2026-10-19-NS-SD-NW-SD-nanotag-study]]
- [x] 2026-10-24: CHG-005 → CHG-009 reviewed and moved to History. [[2026-10-24]]
- [ ] NS-SD questions for Andrea: cracked tag ID, bottle swap time on SD days, sampling details. [[2026-10-19-NS-SD-NW-SD-nanotag-study]]
- [ ] HLBNSL Run 2 sheet edits: not confirmed applied. [[2026-10-05-HLBNSL-sheet-handover-run2]]
- [x] 2026-10-26: sheet request route redesigned: Claude Code writes through the Google Sheets connector, on Andrea's instruction. [[sod1-sheet-change-log-workflow]]
- [ ] Rows 2-6 of the sheet's `Pending changes instructions` tab still describe the Claude for Sheets route; rewrite them as a logged change if Andrea wants. [[sod1-sheet-change-log-workflow]]
- [ ] Reconcile the proposal's two-way ANOVA with the permutation tests used at small n before the final report. [[hlb-sod1-design]]
- [x] 2026-10-23: Andrea keeps off-site copies of the nanotag raw data. [[2026-10-23]]
- [ ] Say in the final report what the nanotag pivot costs: no NREM/REM split and no slow-wave activity. [[hlb-sod1-design]]

## Everything here
![[area.base]]

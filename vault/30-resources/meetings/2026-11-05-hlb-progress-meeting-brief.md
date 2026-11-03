---
type: meeting
area: hlb-sod1
status: active
created: 2026-11-03
summary: "Brief for the HLB progress meeting with the professor, Thu 2026-11-05: the story in order, what to say on each figure, the questions to expect, the decisions to ask for"
tags: [hlb, sod1, professor, meeting]
---

# 2026-11-05: HLB progress meeting, brief

The story and every number: [[2026-11-03-hlb-sod1-report-draft-v02]]. Figures and slide captions:
[[2026-11-05-hlb-progress-meeting-figures]]. Slides: white background, one figure each, short caption.

## The story in one minute
Customers say the SOD1 supplement helps them sleep. We asked whether oral SOD1 changes sleep, activity, cognition or
oxidative stress in mice, and whether it does any harm. Two ways of measuring sleep, three cohort types, one battery of
tests, two tissues. So far: well tolerated, no detectable change in sleep or memory, SOD1 mice a little more active,
hippocampus unchanged, one heart pattern that needs a within-cohort test. Tomorrow's NS-SD data answer the SD half.

## Slide order
1. Question and design (fig 01): why drinking water, why nanotags plus an EEG sub-study, why SD at ZT0.
2. Intake and body weight (`2026-11-03-hlb-intake-fig1-intake-weight.png`): did they drink it, did they lose weight.
3. Nanotag sleep, two cohorts (fig 02, 03): no change, and the size of change we could have seen.
4. EEG sleep stages (fig 04, 05): the re-score gave 15 paired mice instead of 3; no change at baseline; SD arms n = 1.
5. Behaviour with normal sleep (fig 06): memory unchanged, activity up.
6. The activity signal across cohorts (fig 07).
7. Tissue (fig 08): hippocampus no protection, heart crossover, why it is a cohort pattern.
8. NS-SD after SD (fig 10, 11): SD efficacy, recovery, Y-maze. ⬜ built on 11-04 evening.
9. Conclusions and next steps (text slide).

## Questions to expect, and the answer
- **"Why not gavage as in the proposal?"** Gavage stress changes sleep and behaviour, the very outcomes. Cost: dose
  depends on intake, which we measured.
- **"Why so few mice?"** Rig capacity (8 at once) and the EEG yield. We report what the n can detect (MDE) and never
  call a null "no effect".
- **"Are the EEG and nanotag results the same?"** They are separate readouts in separate mice and are never pooled.
  Both show no detectable change; each stands alone.
- **"Is the EEG re-score trustworthy?"** Rule + independent checks; κ 0.95 against Andrea's epoch review of one mouse
  over light and dark. Her review started from the rule's labels, so a blind check on another mouse is still owed.
- **"SOD1 mice were more active in the tests?"** HLBNSL ran all SOD1 mice first, then all water mice, so test order and
  time of day are confounded with arm. The only activity change seen in both nanotag cohorts is a quieter light phase.
- **"Is the heart result real?"** Each group is one cohort, so it may be a cohort difference. The stored nanotag tissue
  tests it within cohort, no new mice.
- **"Is the NOR valid with the prism always novel?"** No reliable side preference in training (7/9 above 50 %), and the spot share rose T1 → T2 in 9/9 mice; object identity not counterbalanced is listed as a limitation.
- **"Why only the Y-maze after SD?"** NOR would measure SD timing relative to training (Palchykova 2006), not SOD1.
- **"Did SD work?"** ⬜ answered by the NS-SD tags (sleep in 09:00-15:00 vs baseline).

## Decisions to ask the professor for
1. Run heart SOD, heart MDA and hippocampal MDA on the stored HLBNSL and NS-SD tissue (one plate, interleaved, blind,
   protein-normalised)?
2. Accept the EEG re-score (gap EMG, tier bars, review fixes) as the report's EEG method?
3. Which sections of the report go to HLB, and how technical?
4. Questions for HLB: coating, SOD isoform, stability in water.

## Before the meeting (Andrea, 11-04)
- Fill `nanotag/analysis/behavior/NSSD_ymaze_hand_scoring.csv`: each mouse's Y-maze start time and arm sequence; note
  which landmark is arm A in the new camera view. Then run the two commands in [[2026-11-03-NS-SD-run2-and-ymaze-runbook]].
- Note any per-mouse SD deviation on 11-03 / 11-04, bottle-weighing times on the SD days, and any room entry between
  11-03 15:00 and 11-04 09:00 (the recovery window).
- Sampling weights of NS-SD go in the sheet; the intake script picks them up.
- Answer: HLBSSL36 / 37, dead or left off a full plate? S-SL sampling date (09-21 or 09-22)? What water did HLBSSD17 get,
  and should it leave the S-SD tissue group? How were mice allocated to SOD1 or water in the nanotag cohorts, and were the
  SD handler and the Y-maze scorer blind to arm? Where does the "about 30 h" SOD1 stability figure come from?

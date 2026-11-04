---
type: meeting
area: hlb-sod1
status: active
created: 2026-11-03
summary: "Draft v0.2 of the HLB SOD1 report: one storyline (aim, design with verified rationale, intake, nanotag sleep and activity, EEG sleep stages, behaviour, tissue, conclusions for HLB); replaces v0.1; revised after an independent review the same day; NS-SD SD, recovery, Y-maze and sampling to add after 2026-11-04"
tags: [hlb, sod1, report, professor]
---

# Oral SOD1 in drinking water: sleep, activity, cognition and tissue oxidative stress in mice

Draft v0.2, 2026-11-03, for Prof. Kim before any version goes to HLB. Replaces [[2026-11-02-hlb-sod1-final-report-draft]].
Sections marked ⬜ wait for the NS-SD data of 2026-11-04. Word version: `nanotag/analysis/report/HLB_SOD1_report_v0.2.docx`.

## Summary

HLB sells a supplement containing microbial superoxide dismutase 1 (SOD1), and customers report that it helps them
sleep. We tested in male mice whether SOD1 in the drinking water changes sleep, activity, cognition or tissue
oxidative-stress markers, with normal sleep and after sleep deprivation (SD), and whether it shows any sign of harm.
The study was built to detect a change in either direction, not to confirm the claim. The answer so far, and what it
cannot exclude, is in section 7.

## 1. Aim

The question is whether the sleep benefit customers report has a measurable basis in mice. We split it into four
questions, each with the result that would support the claim:

1. **Sleep.** Does SOD1 increase or consolidate sleep, or improve recovery sleep after SD? Support: more total sleep,
   longer bouts, more NREM, or a larger rebound with SOD1.
2. **Activity and cognition.** Does SOD1 change waking activity, working memory or recognition memory, with normal
   sleep or after SD? Support: better memory, or a smaller deficit after SD.
3. **Oxidative stress.** Does SOD1 change SOD activity or lipid peroxidation (MDA) in brain or heart? Support: higher
   SOD activity, or less MDA after SD.
4. **Safety.** Any sign of harm: less drinking, weight loss, abnormal behaviour, more oxidative damage?

## 2. Design and why

### 2.1 Cohorts

| Cohort | When (2026) | Arms, n | Sleep readout | Sleep loss | Tests, tissue |
|---|---|---|---|---|---|
| W-SD, S-SD, W-SL, S-SL | Aug to Sep | one arm per cohort, 8-9 mice | EEG/EMG | SD cohorts: 4 h/day, 09:00-13:00, 7 days | heart and hippocampus SOD, hippocampus MDA |
| HLBNSL | Sep to Oct | SOD1 4, water 5 | nanotag | none | Y-maze, open field, NOR; tissue stored |
| NS-SD | Oct to Nov | SOD1 5, water 5 | nanotag | 09:00-15:00 on 11-03; 09:00 to the Y-maze (about 7 h) on 11-04 | Y-maze after SD; tissue 11-04 ⬜ |

All mice were male C57BL/6J, lights on 09:00 to 21:00 (ZT0 = 09:00). SOD1 was given at 6.8 U/mL, set for about
20 U/day at 3 mL/day. In the EEG cohorts SOD1 or water started 11 days before the first SD day (sheet registry).

![[2026-11-05-hlb-meeting-fig01-design-timeline.png]]
*Figure 1. The six cohorts on one time axis: treatment, sleep deprivation, EEG windows, tests and sampling.*

### 2.2 Choices, and the reason for each

1. **Drinking water instead of gavage.** Gavage is a recognised stressor in laboratory rodents (Balcombe et al. 2004;
   Hoggatt et al. 2010), and daily restraint would add to the outcomes we measure (one rat study found no
   corticosterone rise from water gavage; Brown et al. 2000). The cost is a dose that depends on drinking, so intake
   was measured daily. Bottle design and concentration took March to July 2026 to settle.
2. **Fresh solution every day.** The lab's earlier observation is that SOD1 loses activity in solution within about
   30 h (not measured in this study ⬜ source), so bottles were changed daily, except one weekend bottle in NS-SD
   (10-31 to 11-02).
3. **Nanotags for the main cohorts, EEG as a sub-study.** The EEG rig gave too few usable mice per cohort for group
   statistics, and records 8 mice at once, so each EEG cohort held one arm. Nanotags record activity in every mouse.
   Immobility-based sleep agrees with EEG/EMG in C57BL/6J mice when scored from beam breaks or video (92 % of epochs
   at a 40 s criterion; Pack et al. 2007; Fisher et al. 2012), but the implanted tag itself has not been validated
   against EEG, it cannot separate NREM from REM (McShane et al. 2012), and quiet wake counts as sleep. EEG and
   nanotag results are reported separately and never used to confirm each other.
4. **Both arms inside one cohort (nanotag cohorts).** SOD1 and water mice were operated, housed and handled together,
   so the comparison is fair within each cohort. The EEG-cohort comparisons are also comparisons between cohorts.
5. **Each mouse against its own baseline on plain water.** NS-SD had 48 h of baseline, the norm in mouse sleep
   studies (Huber et al. 2000; Baracchi and Opp 2008), starting 10 days after surgery (mice need 5 to 7 days to
   recover normal daily rhythms after an implant; Butz and Davisson 2001) and 72 h after single housing. HLBNSL, the
   first nanotag cohort, started its 3-day baseline 3 days after surgery (1 day for two mice).
6. **SD by gentle handling from lights on.** Mice sleep mostly in the light phase, and 6 h of gentle handling from
   light onset after a 48 h baseline is a standard mouse protocol (Huber et al. 2000; Baracchi and Opp 2008). Gentle
   handling is the established low-stress way to keep rodents awake; 5 to 6 h of it impairs hippocampal plasticity
   and memory in mice without raising corticosterone (Colavito et al. 2013; Palchykova et al. 2006; Vecsey et al.
   2009). The EEG cohorts followed the proposal's chronic restriction (4 h/day for 7 days). NS-SD was cut from 4 to
   2 SD days when NOR was dropped (item 8).
7. **NS-SD tissue at the end of SD.** SD-induced oxidative damage reversed within 24 h of recovery after 36 h of SD
   in mice (Hermann et al. 2025), and brain MDA varies with time of day, peaking around ZT5 (Sani et al. 2007), so
   sampling straight after the last SD and Y-maze catches the end of SD at a fixed time of day.
8. **Behaviour.** With normal sleep: Y-maze, open field, then NOR over 2 days with a 2 h retention. The 2-day NOR is
   a standard variant with one habituation day (Leger et al. 2013), here the open field; a 2 h retention tests
   short-term recognition (Lueptow 2017) and keeps post-training sleep out of the measurement. After SD: the Y-maze
   only. Spontaneous alternation needs no training and no retention interval (Kraeuter et al. 2019; we run one
   8 min session), so it reads working memory at the end of SD. NOR would instead read where SD fell relative to
   training: SD right after training abolishes object recognition in mice, the same SD 6 h later does not
   (Palchykova et al. 2006). With mice tested one after another, each would get a different SD-to-training interval,
   and sleepy mice explore less, so more would fail NOR's exploration minimum. Y-maze alternation reads SD deficits
   and their rescue by an oral probiotic in mice (Griffin et al. 2023), though not every SD protocol lowers it
   (Li et al. 2022). NS-SD mice were tested in alternating order (SOD1, water, SOD1, ...).
9. **Tissue markers.** Total SOD activity (Cayman 706002, which measures Cu/Zn-, Mn- and Fe-SOD together) and MDA,
   a lipid-peroxidation product (Abcam ab118970, TBA reaction). Hippocampus because SD targets it, heart because an
   oral enzyme is more likely to act in the periphery. Cortex, hypothalamus and (nanotag cohorts) liver were also
   collected and are stored at −80 °C; the proposal's 8-isoprostane has not been run.

### 2.3 Statistics

- **Unit.** The mouse. In the nanotag cohorts, the SOD1 effect is the difference between arms in each mouse's change
  from its own baseline. Comparisons between EEG cohorts, including the tissue, are read as cohort differences, not
  causal effects (Lazic et al. 2018).
- **Estimation first.** Differences with 95 % confidence intervals lead (Ho et al. 2019); exact permutation or
  Mann-Whitney tests support them, as they need no normality assumption at small n (Ludbrook 1994). The tissue also
  gets the proposal's two-way ANOVA (SOD1 × sleep) with Šidák comparisons.
- **Primary outcomes.** Total and dark-phase sleep (nanotag) and sleep % (EEG). These were fixed after the HLBNSL
  data were seen, not pre-registered; everything else is exploratory. With 4 vs 5 mice the smallest possible exact
  p is 0.016, so no correction across about 20 outcomes can be passed (Percie du Sert et al. 2020).
- **Wording.** A non-significant result is "no detectable difference, compatible with [CI]", never "no effect". At
  80 % power these cohorts detect only large effects (Cohen's d about 2.2 at 4 vs 5, 2.0 at 5 vs 5, 1.4 at 9 vs 9),
  and significant results at these n tend to overstate the true effect (Button et al. 2013).

## 3. Results

### 3.1 Intake, dose and body weight

Each mouse had its own 10 mL bottle, weighed at every change (1 g = 1 mL), with no control bottle for leaks or
evaporation: values are what left the bottle. Details: [[2026-11-03-hlb-intake-bodyweight-and-sampling]].

- **Dose.** SOD1 mice removed 3.2 to 4.1 mL/day on average per cohort, 22 to 28 U/day, 108 to 138 % of the 20.4 U/day
  target. The lowest single mouse averaged 94 %.
- **Volume.** SOD1 mice removed less than water mice in all four cohort pairs (−0.4 to −1.7 mL/day). Part of this is
  the bottle: in three pairs some water mice used a larger bottle type that read 0.5 to 2.4 mL/day higher in the same
  mice. The gap remains where that cannot explain it: W-SD vs S-SD, same bottles, −0.8 mL/day (95 % CI −1.7 to 0.0,
  p = 0.052); HLBNSL, large bottle on 5 of 75 water mouse-days, −1.1 mL/day (p = 0.024). SOD1 mice consistently drank
  somewhat less, a possible palatability effect.
- **Body weight.** No detectable difference in weight change (95 % CIs about ±3 points in the EEG cohorts, ±1.8 in
  HLBNSL). EEG mice lost 3 to 6 % in both arms. Two weights per mouse only. ⬜ NS-SD weights at sampling.
- **Health.** Two EEG mice could not drink from the nozzle: HLBWSD01 (water), and HLBSSD17 (SOD1), which was given an
  extra plain-water bottle, so its dose is unknown. HLBNSSL43 (SOD1) died in restraint during a tag read on 09-28.
  ⬜ HLBSSL36 and HLBSSL37 (SOD1) are marked dead in the sheet but recorded elsewhere as left off a full plate.

![[2026-11-03-hlb-intake-fig1-intake-weight.png]]
*Figure 2. Liquid removed per day (top) and body-weight change (bottom) per mouse, per cohort pair; dashed line 3 mL/day, the intake the dose was set for.*

### 3.2 Sleep and activity (nanotag)

**HLBNSL, normal sleep.** Change from baseline in total sleep, 3 vs 4 mice with a usable baseline: SOD1 +99, water
+87 min/day; SOD1 − water +11 min/day (95 % CI −130 to +156), the same at every immobility cutoff (24 to 60 s). Both
arms gained because the short baseline started soon after surgery and handling and testing raised dark-phase sleep
from 30 to about 40 %. Light/dark split and bout number and length: no detectable difference.

**NS-SD before SD, first 6 days on treatment, 5 vs 5.** SOD1 − water in the change of total sleep +16 min/day
(95 % CI about −18 to +58), the same for light, dark and bout length.

![[2026-11-05-hlb-meeting-fig02-nanotag-sleep.png]]
*Figure 3. Change in total sleep from each mouse's own baseline, nanotag; the two cohorts are shown apart, never pooled.*

![[2026-11-05-hlb-meeting-fig03-nanotag-24h-profile.png]]
*Figure 4. Hourly sleep on treatment, HLBNSL (mean ± SEM).*

**Activity and rhythm, both cohorts.** SOD1 mice were quieter in the light phase in both cohorts (NS-SD −113 vs
+77 counts/h, p = 0.17), which raised rhythm amplitude in HLBNSL (p = 0.029, but already different at baseline) and
not in NS-SD (p = 0.24). In the dark phase NS-SD SOD1 mice became more active in the first 6 days (+616 vs +265
counts/h, p = 0.040), but not on days 8 to 10, when dark activity fell in both arms (−423 vs −1,160 counts/h, p = 0.14).
Each is one of about 20 to 35 tests per cohort.

**NS-SD, SD and recovery, 5 vs 5** ([[2026-11-04-NS-SD-run2-sd-efficacy-and-recovery]]).
- **SD was effective and equal in both arms.** All 10 mice slept less than at baseline in 09:00-15:00 on both SD days.
  Day 1: 10 vs 8 % asleep, a drop of 58 vs 65 points (SOD1 − water +6.7, 95 % CI −3.5 to +16.6). Day 2 lasted until each
  mouse's Y-maze, 7.0 vs 7.2 h.
- **Recovery after SD day 1: no detectable SOD1 difference.** Both arms slept more than in the same hours at baseline,
  mostly in the dark: total rebound +188 vs +163 min, SOD1 − water +25 min (95 % CI −68 to +130). There is no recovery
  window after SD day 2 (Y-maze, then kept awake until sampling).
- **Undisturbed days 8 to 10 on treatment:** change in total sleep +75 vs +71 min/day (p = 0.94).

![[2026-11-04-NSSD-run2-sd-efficacy.png]]
*Figure 5. Sleep in 09:00-15:00 at baseline and on the two SD days, per mouse, and the change from baseline (NS-SD).*

![[2026-11-04-NSSD-run2-recovery.png]]
*Figure 6. Recovery sleep after SD day 1 against the same clock hours at baseline, and the rebound per mouse (NS-SD).*

### 3.3 Sleep stages (EEG/EMG)

All recordings were scored with the professor's SleepStager rule on an EMG measured between the 60 Hz mains
harmonics. Usability was screened in code and then by LLM agents reading the traces, which could only demote a
recording. One recording was checked against Andrea's epoch-by-epoch review: κ 0.95 over 14,077 epochs across light
and dark, but her review started from the rule's labels, so agreement is partly built in; no recording has been
scored blind. 15 mice have usable wake, NREM and REM at both timepoints (W-SD 1, S-SD 1, W-SL 7, S-SL 6). SOD1 started
before the first recording, so "baseline" means on treatment, without SD.

| Baseline, % of usable time | SOD1 (n = 10) | Water (n = 11) | Difference, 95 % CI | p |
|---|---|---|---|---|
| Sleep, 24 h | 52.0 | 52.5 | −0.5 (−4.7 to +3.6) | 0.81 |
| Sleep, light phase | 71.7 | 72.2 | −0.5 (−4.5 to +3.4) | 0.78 |
| Sleep, dark phase | 31.1 | 32.6 | −1.5 (−7.2 to +4.3) | 0.61 |
| NREM, 24 h | 45.8 | 46.5 | −0.6 (−4.4 to +3.2) | 0.75 |

- **Baseline: no detectable difference** in sleep or NREM. The smallest difference detectable here is about 6 points
  of sleep %. REM % is not reported because the scoring rule partly fixes it.
- **Second recording without SD: no detectable difference** in the change (S-SL +2.1 vs W-SL +0.1 points, 6 vs 7 mice,
  p = 0.52).
- **After SD: one mouse per arm, not interpretable.** The water mouse gained 9.3 points of sleep in recovery. The SOD1
  mouse gained 18.1, but 1.5 if its movement-artefact epochs (27 % of the recovery, mostly vigorous wake) count as
  wake. NREM slow-wave activity in the first 4 h of recovery was 114 % (water SD) and 117 % (SOD1 SD) of baseline,
  against 107 % (W-SL) and 93 % (S-SL) without SD.

![[2026-11-05-hlb-meeting-fig04-eeg-baseline.png]]
*Figure 7. EEG/EMG sleep at baseline (on treatment, before SD), % of usable time, per mouse.*

![[2026-11-05-hlb-meeting-fig05-eeg-recovery.png]]
*Figure 8. Change in sleep from baseline to the second recording; the SD arms are single mice, the open circle counts movement-artefact epochs as wake.*

### 3.4 Behaviour

**Normal sleep (HLBNSL, SOD1 4 vs water 5).** Mice were tested in blocks, the four SOD1 mice first and then the five
water mice, so every group difference here is also a difference in test order and time of day.

| Test | Measure | SOD1 | Water | SOD1 − water |
|---|---|---|---|---|
| Y-maze | spontaneous alternation (%) | 60.5 ± 2.4 | 62.8 ± 2.4 | −2.2 (95 % CI −10.3 to +5.8), p = 0.73 |
| Y-maze | arm entries | 48.3 | 38.4 | +9.9 (−4.0 to +23.7), p = 0.063 |
| Y-maze | distance (m) | | | +4.7 (−4.6 to +14.0), p = 0.41 |
| Open field | distance (m) | 63.9 | 51.1 | g = +1.66, p = 0.11 |
| Open field | immobility (s) | 66 | 135 | g = −1.59, p = 0.06 |
| Open field | centre time (%) | 18.6 | 15.9 | p = 0.73 |
| NOR | d2, pose model 1 (model 2) | +0.34 ± 0.13 (+0.25) | +0.37 ± 0.05 (+0.31) | 95 % CI about ±0.45; p = 0.73 (0.91) |

- **Working memory: no detectable difference.** Every mouse alternated above 50 %, but at n = 4 and 5 even that cannot
  reach p < 0.05 within an arm (SOD1 p = 0.125, water p = 0.062, the smallest possible).
- **Recognition memory: present in both arms, no detectable SOD1 difference.** The mice explored the novel object
  more (model 1: 9/9 mice, p = 0.004; model 2: 8/9, p = 0.020). Training showed no reliable side preference (7/9 mice
  above 50 % at the later novel spot), and the share at that spot still rose from training to test in 9/9 mice
  (model 1, p = 0.004).
- **Activity.** SOD1 mice entered more arms, moved more in the open field and stayed still less, with no difference
  in centre time. These readouts come from the same 9 mice, and Y-maze distance did not differ.
- **Scoring.** Y-maze by hand. Open field and NOR by pose tracking (two models; open-field distance r ≥ 0.995 between
  them). For NOR, pose d2 matched blinded hand scoring within 0.02 to 0.08 on the test clips, though pose counts
  10 to 25 % fewer seconds; the two hand raters agreed with κ 0.76 on the clips both scored.

**After SD (NS-SD)** ⬜: Y-maze on 11-04 straight after the second 6 h SD, then sampling.

![[2026-11-05-hlb-meeting-fig06-behaviour.png]]
*Figure 9. Behaviour with normal sleep, HLBNSL: Y-maze alternation and entries, open-field distance, NOR d2 (pose model 2).*

![[2026-11-05-hlb-meeting-fig07-activity-signal.png]]
*Figure 10. Activity readouts as standardised SOD1 − water differences (Hedges g, approximate 95 % CI; p values are the exact tests). The first two come from the same HLBNSL mice.*

### 3.5 Tissue (EEG cohorts)

Tissue came from the four EEG cohorts, sampled about a day after the last SD bout in the SD cohorts. Values were
recomputed from the raw absorbances with each kit's method.

| Measure | Water, normal sleep | SOD1, normal sleep | Water, SD | SOD1, SD |
|---|---|---|---|---|
| Hippocampal SOD (U/mL) | 28.0 (9) | 25.8 (8) | 29.6 (9) | 30.7 (9) |
| Hippocampal MDA (nmol/well) | 1.47 (6) | 1.41 (6) | 1.69 (6) | 1.80 (5) |
| Heart SOD (U/mL) | 21.6 (6) | 27.2 (6) | 30.0 (6) | 21.7 (6) |

Mean (n). Two-way ANOVA, SOD1 × sleep; Šidák comparisons within each sleep condition.

- **Hippocampal SOD: no detectable SOD1 difference** (normal sleep −2.3 U/mL, 95 % CI −6.1 to +1.6; SD +1.1, −2.6 to
  +4.8). The SD cohorts ran on a different plate, so their higher values are not read as a sleep effect.
- **Hippocampal MDA: no detectable SOD1 difference** (normal sleep −0.06, CI −0.36 to +0.23; SD +0.11, −0.19 to +0.42).
  The SD cohorts were higher overall (p = 0.007): +0.22 with water (p = 0.26) and +0.39 with SOD1 (p = 0.030).
- **Heart SOD: a crossover** (interaction p < 0.001). SOD1 − water was +5.6 U/mL with normal sleep (CI +0.6 to +10.6,
  Šidák p = 0.060) and −8.2 after SD (CI −13.3 to −3.2, p = 0.005). It depends on single mice.

⬜ HLBNSL and NS-SD tissue: stored at −80 °C, not yet assayed.

![[2026-11-05-hlb-meeting-fig08-tissue.png]]
*Figure 11. Tissue SOD activity and MDA in the four EEG cohorts, per mouse; each group is a separate cohort.*

## 4. What the results mean

- **Sleep.** Neither method found a change in sleep amount or structure with SOD1, and the confidence intervals,
  not the p values, set what can be excluded (section 7).
- **Hippocampus.** No detectable SOD1 difference is the expected result. Unprotected oral SOD is largely digested:
  plain melon SOD left blood and liver antioxidant enzymes unchanged in mice, while a gliadin-combined form, which
  delays digestion, raised circulating enzymes (Vouldoukis et al. 2004). Any enzyme absorbed would still have to reach
  the brain.
- **MDA and SD.** Whether SD raised hippocampal MDA is unresolved. The rise was not detectable within the water arm,
  SD and normal sleep were separate cohorts, and oxidative changes after SD can reverse within a day (section 2.2,
  item 7), while this tissue was taken a day after SD. Even 3 to 14 days of SD left brain lipid and protein oxidation
  unchanged in rats (Gopalakrishnan et al. 2004), so a null MDA result in NS-SD would not show that SD failed.
- **Heart.** The crossover is the one tissue pattern, and it rests on the interaction, since neither single
  comparison with normal sleep passes. A higher heart SOD with SOD1 would be in line with oral melon SOD raising
  cardiac SOD expression in hypertensive rats (Carillon et al. 2014). A lower value after SD could mean less oxidative
  load or a blunted adaptive response, as antioxidants blunt adaptation to exercise (Gomez-Cabrera et al. 2008; Ristow
  et al. 2009). But four groups from four cohorts can produce this pattern without any SOD1 effect.
- **Activity.** The light-phase quieting with SOD1 is the only activity change seen in both nanotag cohorts.   The
  other signals go towards more activity: in the dark phase (NS-SD, first 6 days only, gone by days 8 to 10) and in the
  tests (HLBNSL, confounded with test order). None passes the multiplicity the rhythm-amplitude lead was discounted for. It is a pattern to measure, not
  a finding.

## 5. Limitations

- **Small groups** (4 to 11 mice): only large effects are detectable.
- **Males only**, against the proposal's 15 males and 15 females per group.
- **Cohort confounding:** one arm per EEG cohort, so EEG-cohort sleep and tissue comparisons are also cohort
  comparisons (W-SD hippocampi also weighed about twice as much, a sign of a different dissection).
- **Behaviour order:** HLBNSL tested SOD1 mice first, then water mice.
- **Allocation and blinding** to arm, and blinding of the SD handlers and Y-maze scorer, are not recorded.
- **Nanotag sleep is immobility from a device not validated against EEG:** no NREM/REM, quiet wake counts as sleep.
- **HLBNSL baseline** was short and close to surgery; the change from baseline is valid between arms but not as an
  absolute value.
- **EEG scoring** has one rule-anchored human check and no blind scoring; usability review was by LLM agents.
- **Dose:** depends on intake; activity left in the bottle over the day, the coating and the isoform of the powder are
  unknown; HLBSSD17 had an extra water bottle and stays in the S-SD tissue group.
- **Tissue:** total SOD, not SOD1; no protein normalisation; hippocampal SOD plates split by sleep condition; EEG-cohort
  SD tissue taken a day after SD; the TBA assay is not fully specific for MDA; no damage marker in heart or liver.
- **NOR:** the novel object was always the same object on the same side, not counterbalanced across mice, as NOR protocols recommend
  (Antunes and Biala 2012; Denninger et al. 2018); a 2 h test does not cover overnight consolidation.
- **SD protocols differ** between the EEG cohorts and NS-SD, and NS-SD had no hand habituation before SD.

## 6. What a follow-up should change

1. **Assay the stored nanotag-cohort tissue first** (HLBNSL, NS-SD): heart SOD, heart MDA, liver SOD and hippocampal
   MDA on one plate, interleaved, coded blind, protein-normalised. Both arms share a cohort there, so this is the
   direct test of the heart pattern, with no new mice.
2. **Both arms, and SD and normal sleep, inside one cohort,** allocated at random by cage and surgery day, tested in
   alternating order, scorers blind.
3. **Size for a realistic effect:** about 17 mice per group for d = 1.0, about 9 for d = 1.5. Pre-register the
   primary sleep outcome (and light-phase activity), the primary tissue marker and the analysis.
4. **Counterbalance NOR objects and sides;** add a 24 h retention if consolidation matters.
5. **Ask HLB** whether the powder is coated, which SOD it is (Cu/Zn or Mn), whether a protected oral form exists, and
   for its stability in water.

## 7. Conclusions for HLB

1. **Safety: no signal of harm** in drinking, body weight, behaviour or the tissue markers measured. SOD1 mice reached
   the target dose and drank slightly less than water mice. Not covered: damage markers in heart or liver, and the
   two S-SL deaths still to confirm ⬜.
2. **Sleep amount with normal sleep: no detectable change.**
   - Nanotag: NS-SD excludes effects beyond about −20 to +60 min/day; HLBNSL is too variable to exclude even 2 h/day.
   - EEG/EMG: 21 mice exclude differences beyond about 5 points of sleep %.
3. **Sleep structure: no detectable change** in NREM (EEG/EMG), or in bout length and light/dark distribution (nanotag).
4. **Recovery after SD: no detectable change.** In NS-SD, SD removed the same amount of sleep in both arms, and the
   rebound after it did not differ (95 % CI about −1 h to +2 h). The EEG cohorts have one mouse per arm and cannot answer it.
5. **Cognition with normal sleep: no detectable change** in working memory or recognition memory; both were intact in
   both arms. ⬜ After SD (NS-SD Y-maze).
6. **Activity:** SOD1 mice were quieter in the light phase in both nanotag cohorts; other activity differences are
   inconsistent or confounded. A pattern to measure, not a finding.
7. **Oxidative stress:** no detectable SOD1 difference in hippocampal SOD or MDA. The heart crossover is the one tissue
   pattern; it needs the within-cohort assays before it can be attributed to SOD1.
8. **Overall:** in mice, at this dose and route, the data do not show a sleep-promoting effect of SOD1. They cannot
   exclude small effects, or an effect of a formulation protected for oral delivery.

## References
All checked on PubMed (abstracts) on 2026-11-03.

- Antunes M, Biala G. The novel object recognition memory: neurobiology, test procedure, and its modifications. Cogn Process 2012;13:93-110. doi:10.1007/s10339-011-0430-z
- Balcombe JP, Barnard ND, Sandusky C. Laboratory routines cause animal stress. Contemp Top Lab Anim Sci 2004;43(6):42-51. PMID 15669134
- Baracchi F, Opp MR. Sleep-wake behavior and responses to sleep deprivation of mice lacking both interleukin-1β receptor 1 and tumor necrosis factor-α receptor 1. Brain Behav Immun 2008;22:982-93. doi:10.1016/j.bbi.2008.02.001
- Brown AP, Dinger N, Levine BS. Stress produced by gavage administration in the rat. Contemp Top Lab Anim Sci 2000;39(1):17-21. PMID 11178310
- Butz GM, Davisson RL. Long-term telemetric measurement of cardiovascular parameters in awake mice: a physiological genomics tool. Physiol Genomics 2001;5:89-97. doi:10.1152/physiolgenomics.2001.5.2.89
- Button KS, et al. Power failure: why small sample size undermines the reliability of neuroscience. Nat Rev Neurosci 2013;14:365-76. doi:10.1038/nrn3475
- Carillon J, et al. Endogenous antioxidant defense induction by melon superoxide dismutase reduces cardiac hypertrophy in spontaneously hypertensive rats. Int J Food Sci Nutr 2014;65:602-9. doi:10.3109/09637486.2014.893286
- Colavito V, et al. Experimental sleep deprivation as a tool to test memory deficits in rodents. Front Syst Neurosci 2013;7:106. doi:10.3389/fnsys.2013.00106
- Denninger JK, Smith BM, Kirby ED. Novel object recognition and object location behavioral testing in mice on a budget. J Vis Exp 2018;(141):58593. doi:10.3791/58593
- Fisher SP, et al. Rapid assessment of sleep-wake behavior in mice. J Biol Rhythms 2012;27:48-58. doi:10.1177/0748730411431550
- Gomez-Cabrera MC, et al. Oral administration of vitamin C decreases muscle mitochondrial biogenesis and hampers training-induced adaptations in endurance performance. Am J Clin Nutr 2008;87:142-9. doi:10.1093/ajcn/87.1.142
- Gopalakrishnan A, Ji LL, Cirelli C. Sleep deprivation and cellular responses to oxidative stress. Sleep 2004;27:27-35. doi:10.1093/sleep/27.1.27
- Griffin SM, et al. Restorative effects of probiotics on memory impairment in sleep-deprived mice. Nutr Neurosci 2023;26:254-64 (online 2022). doi:10.1080/1028415X.2022.2042915
- Hermann R, et al. Effects of lithium on brain oxidative stress in C57BL/6 mice subjected to paradoxical sleep deprivation and different rest periods. J Psychiatr Res 2025;192:360-70. doi:10.1016/j.jpsychires.2025.10.024
- Ho J, et al. Moving beyond P values: data analysis with estimation graphics. Nat Methods 2019;16:565-6. doi:10.1038/s41592-019-0470-3
- Hoggatt AF, et al. A spoonful of sugar helps the medicine go down: a novel technique to improve oral gavage in mice. J Am Assoc Lab Anim Sci 2010;49:329-34. PMID 20587165
- Huber R, Deboer T, Tobler I. Topography of EEG dynamics after sleep deprivation in mice. J Neurophysiol 2000;84:1888-93. doi:10.1152/jn.2000.84.4.1888
- Kraeuter AK, Guest PC, Sarnyai Z. The Y-maze for assessment of spatial working and reference memory in mice. Methods Mol Biol 2019;1916:105-11. doi:10.1007/978-1-4939-8994-2_10
- Lazic SE, Clarke-Williams CJ, Munafò MR. What exactly is 'N' in cell culture and animal experiments? PLoS Biol 2018;16:e2005282. doi:10.1371/journal.pbio.2005282
- Leger M, et al. Object recognition test in mice. Nat Protoc 2013;8:2531-7. doi:10.1038/nprot.2013.155
- Li Y, et al. Comparison effects of chronic sleep deprivation on juvenile and young adult mice. J Sleep Res 2022;31:e13399. doi:10.1111/jsr.13399
- Ludbrook J. Advantages of permutation (randomization) tests in clinical and experimental pharmacology and physiology. Clin Exp Pharmacol Physiol 1994;21:673-86. doi:10.1111/j.1440-1681.1994.tb02570.x
- Lueptow LM. Novel object recognition test for the investigation of learning and memory in mice. J Vis Exp 2017;(126):55718. doi:10.3791/55718
- McShane BB, et al. Assessing REM sleep in mice using video data. Sleep 2012;35:433-42. doi:10.5665/sleep.1712
- Pack AI, et al. Novel method for high-throughput phenotyping of sleep in mice. Physiol Genomics 2007;28:232-8. doi:10.1152/physiolgenomics.00139.2006
- Palchykova S, et al. Sleep deprivation impairs object recognition in mice. Neurobiol Learn Mem 2006;85:263-71. doi:10.1016/j.nlm.2005.11.005
- Percie du Sert N, et al. The ARRIVE guidelines 2.0: updated guidelines for reporting animal research. PLoS Biol 2020;18(7):e3000410. doi:10.1371/journal.pbio.3000410
- Ristow M, et al. Antioxidants prevent health-promoting effects of physical exercise in humans. PNAS 2009;106:8665-70. doi:10.1073/pnas.0903485106
- Sani M, et al. Malondialdehyde content and circadian variations in brain, kidney, liver, and plasma of mice. Chronobiol Int 2007;24:671-85. doi:10.1080/07420520701535720
- Vecsey CG, et al. Sleep deprivation impairs cAMP signalling in the hippocampus. Nature 2009;461:1122-5. doi:10.1038/nature08488
- Vouldoukis I, et al. Supplementation with gliadin-combined plant superoxide dismutase extract promotes antioxidant defences and protects against oxidative stress. Phytother Res 2004;18:957-62. doi:10.1002/ptr.1542

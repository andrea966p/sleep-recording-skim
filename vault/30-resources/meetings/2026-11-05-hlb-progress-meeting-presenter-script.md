---
type: meeting
area: hlb-sod1
status: active
created: 2026-11-05
summary: "Presenter's script for the HLB progress meeting, Thu 2026-11-05: the concepts to know, how each readout is measured and analysed, how to read every figure, the results, what they mean and what they cannot show, and the questions to expect"
tags: [hlb, sod1, professor, meeting]
---

# 2026-11-05: HLB progress meeting, presenter's script

Something to read once before the meeting, not to read out. Every number comes from
[[2026-11-03-hlb-sod1-report-draft-v02]], [[hlb-eeg-sleep-overview]],
[[2026-11-04-NS-SD-run2-sd-efficacy-and-recovery]] and [[2026-11-05-NS-SD-ymaze-results]]. Slide order and the
decisions to ask for are in [[2026-11-05-hlb-progress-meeting-brief]]. The deck itself (24 slides, `build.js`) is on the
office PC in `~/hlb_meeting_deck/`, and its figure scripts are in `nanotag/analysis/report/labmtg/`.

> [!abstract] TL;DR: the story in one minute
> HLB's customers say the SOD1 supplement helps them sleep. I tested, in male mice, whether superoxide dismutase 1
> (SOD1) in the drinking water changes sleep, activity, memory or oxidative-stress markers, with normal sleep and
> after sleep deprivation (SD), and whether it does any harm. The mice drank it and got the target dose. With two
> independent sleep readouts (implanted nanotags and EEG/EMG) I see **no detectable change in sleep**, before or after
> SD. Memory is intact and unchanged, both with normal sleep and after SD. SOD1 mice may be quieter in the light
> phase, which is a pattern, not a finding. The hippocampus shows nothing. The heart shows a crossover that may just
> be a cohort difference, and the stored nanotag tissue can test that without new mice.

## Colours in the deck

Water is **blue and always on the left**, SOD1 is **orange and on the right** (Okabe-Ito colours, colour-blind
safe). After SD each colour becomes a light tint of itself, so the hue tells you treatment and the shade tells you
sleep condition. Each dot is one mouse; the bar or cross is the group mean, error bars are ± SEM unless the slide
says CI. (The 11-03 figure set in [[2026-11-05-hlb-progress-meeting-figures]] used dark grey and teal instead.)

## Part 1: concepts to have ready

### Time and design
- **ZT (zeitgeber time).** Hours since lights on. Lights 09:00 on, 21:00 off, so ZT0 = 09:00 and ZT12 = 21:00.
  Mice are nocturnal: they sleep most in the light phase (ZT0-12) and are active in the dark (ZT12-24).
- **Cohort.** A group of mice operated, housed and recorded together. There are six:
  - Four EEG/EMG cohorts, one arm each: W-SD (water + SD), S-SD (SOD1 + SD), W-SL and S-SL (water or SOD1, normal
    sleep). Any difference between them is also a difference between cohorts.
  - Two nanotag cohorts with both arms inside: HLBNSL (normal sleep, SOD1 4 vs water 5) and NS-SD (SOD1 5 vs water 5,
    sleep-deprived at the end). These are where SOD1 vs water is a fair comparison.
- **Dose.** SOD1 at 6.8 U/mL in the drinking water, set for about 20 U/day at 3 mL/day, fresh bottle every day.
  The EEG cohorts started treatment 11 days before the first SD day.
- **Why drinking water and not gavage.** Gavage is a stressor, and stress changes exactly what I measure (sleep,
  behaviour). The price is that the dose depends on how much each mouse drinks, so I weighed every bottle.
- **Sleep deprivation (SD) by gentle handling.** Someone keeps the mice awake by touching the cage or the mouse
  as soon as it settles, from lights on, when mice would normally sleep most. It is the standard low-stress way.
  EEG cohorts: 4 h a day (09:00-13:00) for 7 days, as in the proposal. NS-SD: 6 h on 11-03 (09:00-15:00), and on
  11-04 from 09:00 until each mouse's Y-maze (about 7 h).
- **Baseline and change from baseline.** Each nanotag mouse is recorded on plain water first. The SOD1 effect is
  then the difference between arms in each mouse's own change (treatment minus baseline). In the EEG cohorts SOD1
  had already started, so "baseline" there means on treatment, before SD.

### Sleep measured by nanotag
- **Nanotag.** A small implanted tag that counts movement in 12 s bins. It says nothing about brain state.
- **Immobility-based sleep.** Sleep = at least 4 consecutive 12 s bins with zero counts, so at least 48 s without
  moving. In mice, immobility scored from video or beam breaks matches EEG sleep in about 92 % of epochs (40 s rule,
  Pack 2007, Fisher 2012). But this tag itself has never been checked against EEG, quiet wake counts as sleep, and it
  cannot separate NREM from REM. That is why tag results and EEG results are **always reported separately**.
- **Bouts.** A run of consecutive sleep bins. Bout number and length show how consolidated sleep is.
- **Activity counts/h and rhythm amplitude.** The tag's movement counts per hour, and how big the day-night
  difference is.
- **Rebound (recovery sleep).** After SD, the extra sleep compared with the same clock hours at baseline.
- **HLBNWSD59** wears its tag at the shoulder, so its level reads differently. Read its change, not its level
  (hollow marker on the slides). Every NS-SD result was repeated without it and does not change.

### Sleep measured by EEG/EMG
- **EEG** (brain activity from implanted electrodes over the cortex) and **EMG** (neck muscle activity). Three
  states:
  - Wake: fast low-voltage EEG, EMG tone present.
  - NREM: slow, large EEG waves (delta, 1-4 Hz), low EMG.
  - REM: theta EEG (6-9 Hz), the muscle almost silent.
- **Epoch.** The 4 s window each label is given to.
- **SleepStager rule.** The professor's rule-based scorer, used unchanged: spectral EEG features plus EMG tone per
  4 s epoch, with every cut fitted on the recording itself. Validated at κ about 0.89 against seven human scorers.
- **The one change: EMG between the harmonics.** Our rig's EMG carries 60 Hz mains hum (Korea is 60 Hz), up to mV on
  open leads. So the EMG is read in 70-470 Hz with a notch at every multiple of 60 Hz. The old 10-124 Hz EMG was
  mostly hum, which is why so many mice were thrown away before.
- **Usability tiers.** Judged without the labels, hour by hour, from the mouse's own signals:
  - A: W/NREM/REM over the whole window.
  - B: W/NREM/REM on at least 6 light and 6 dark hours.
  - C: NREM from the EEG alone.
  - D: sleep vs wake from the EMG alone.
  - X: nothing usable.
  Only tier A and B go into the sleep-stage results.
- **Agent review.** LLM agents read the traces of every window and were only allowed to **demote** a recording,
  never promote one (7 were demoted, none promoted).
- **κ (Cohen's kappa).** Agreement between two scorers corrected for chance: 1 = perfect, 0 = chance.
- **Slow-wave activity (SWA).** NREM delta power in the first 4 h of recovery as a % of the same hours at baseline.
  It is the classic marker of sleep pressure: after SD it should go up.
- **Why I never show REM %.** The rule partly fixes it by construction, so it is not a free measurement.

### Behaviour
- **Y-maze, spontaneous alternation (SA %).** One 8 min session in a three-arm maze. A mouse that remembers where it
  just was tends to enter the arm it visited least recently. SA % = alternations (three different arms in a row)
  divided by (entries − 2). Chance is 50 %. It reads **working memory** and needs no training, so it can be run
  straight after SD. Arm entries count activity. Scored by hand from video, all four paws in, re-entries kept.
- **Open field (OFT).** 10 min in an empty box: distance moved and immobility (activity), centre time (anxiety-like).
  Scored by pose tracking.
- **Novel object recognition (NOR).** Day 1 open field (habituation), day 2 training with two identical objects, then
  a test 2 h later with one object replaced. **d2 (discrimination index)** = (novel − familiar) / (novel + familiar)
  exploration time. 0 = no preference, positive = remembers the old object. Scored by pose tracking, checked
  against blinded hand scoring (within 0.02 to 0.08 of d2).
- **Why no NOR after SD.** NOR after SD would measure when SD fell relative to training (SD right after training
  abolishes it, 6 h later does not, Palchykova 2006), not SOD1. Mice tested one after another would each get a
  different interval.

### Tissue
- **Total SOD activity** (Cayman kit): all SOD forms together (Cu/Zn, Mn, Fe), not SOD1 alone. Hippocampus because
  SD targets it, heart because an oral enzyme is more likely to act in the periphery.
- **MDA** (Abcam TBA kit): malondialdehyde, a product of lipid peroxidation, so a marker of oxidative damage.
- Values were recomputed from the raw absorbances with each kit's own method.

### Statistics
- **The mouse is the unit.** Never epochs or hours.
- **Estimation first.** I lead with the difference and its 95 % confidence interval (CI), and use p only as support.
  The CI is the range of true differences compatible with the data.
- **Exact permutation test / Mann-Whitney.** Shuffle the group labels over all possible ways and ask how often a
  difference this big appears. No normality assumption, so it suits n = 4 or 5.
- **The p floor.** With 4 vs 5 mice the smallest possible exact p is 0.016. Within one arm of 4 mice, even if every
  mouse alternates above chance, the best possible p is 0.125. So "not significant" at these n can be the maximum
  the design can give.
- **MDE (minimum detectable effect).** The smallest difference the sample had an 80 % chance to detect. At 80 %
  power these cohorts detect only large effects: Cohen's d about 2.2 at 4 vs 5, 2.0 at 5 vs 5, 1.4 at 9 vs 9. It is
  a sensitivity statement, never "observed power".
- **Hedges g.** The difference in standard-deviation units, corrected for small samples. 0.2 small, 0.5 medium,
  0.8 large, so the activity values of 1.2 to 1.7 are large but come with wide CIs.
- **Two-way ANOVA (SOD1 × sleep), interaction, Šidák.** Used for the tissue as the proposal asked. An
  **interaction** means the SOD1 effect goes in different directions with normal sleep and after SD. Šidák corrects
  the follow-up comparisons for being several.
- **Multiplicity.** About 20 to 35 tests per cohort. One p below 0.05 among them is expected by chance.
- **Wording.** "No detectable difference, compatible with [CI]", never "no effect". "A pattern to measure, not a
  finding" for anything that is suggestive but fragile.

## Part 2: section by section

### 1. Question and design
- **Shows:** the six cohorts on one time axis, with treatment, SD, EEG windows, tests and sampling.
- **Say:**
  - The EEG rig records 8 mice at once and gave too few usable mice per cohort for group statistics, so each EEG
    cohort held one arm.
  - The nanotag cohorts carry the fair SOD1 vs water comparison, with both arms in one cohort.
  - The EEG is a sub-study that adds sleep stages.
- **Trap:** someone reading S-SL vs W-SL as a clean SOD1 comparison. It is also a cohort comparison.

### 2. Intake and body weight
- **Shows:** liquid removed per day per mouse (top), body-weight change (bottom), dashed line at 3 mL/day.
- **Results:**
  - SOD1 mice got 22 to 28 U/day on average per cohort, 108 to 138 % of target; the lowest mouse 94 %.
  - SOD1 mice drank a little less than water mice in every pair. Part of that is the bottle type, but in the clean
    comparisons the gap remains (W-SD vs S-SD −0.8 mL/day, p = 0.052; HLBNSL −1.1 mL/day, p = 0.024). Possibly
    taste.
  - No detectable difference in weight change. EEG mice lost 3 to 6 % in both arms.
- **Meaning:** the dose reached the mice, and there is no sign of harm here. "Removed from the bottle" is not quite
  "drunk": there was no control bottle for leaks.

### 3. Nanotag sleep with normal sleep (HLBNSL and NS-SD before SD)
- **Shows:** each mouse's change in total sleep from its own baseline, the two cohorts side by side, never pooled.
  Plus the hourly sleep profile on treatment.
- **Results:**
  - HLBNSL: SOD1 − water +11 min/day (95 % CI −130 to +156), only 3 vs 4 mice with a usable baseline. 49 and 50
    had no usable baseline. Same at every immobility cutoff from 24 to 60 s.
  - NS-SD before SD: +16 min/day (CI about −18 to +58). Same for light, dark and bout length.
  - Undisturbed NS-SD days 8 to 10: +75 vs +71 min/day (p = 0.94).
  - Hourly profile: the two arms overlap at nearly every hour (light phase about 74 vs 72 % asleep).
- **Meaning:** no detectable change in sleep amount. NS-SD rules out effects beyond about −20 to +60 min/day.
  HLBNSL is too variable to rule out even 2 h/day.
- **Trap:** "both HLBNSL groups slept more". The short baseline came soon after surgery, and handling and test days
  raised dark-phase sleep from 30 to about 40 % in both arms. That is valid between arms, not as an absolute gain.

### 4. NS-SD: sleep deprivation and recovery
- **Shows:**
  - The protocol axis (light/dark shading and the analysis windows).
  - Sleep in 09:00-15:00 at baseline and on both SD days.
  - The rebound against the same clock hours at baseline.
  - Day-by-day and hour-by-hour courses, and the actograms (one row per day, movement as darkness).
- **Results:**
  - **SD worked, equally in both arms.** All 10 mice slept less than at baseline on both days.
    - Day 1: 10.3 vs 8.1 % asleep (SOD1 vs water), a drop of 58 vs 65 points. SOD1 − water +6.7 (CI −3.5 to +16.6).
    - Day 2: 16.4 vs 17.0 %. Real SD length to the Y-maze was 7.0 vs 7.2 h.
  - **Recovery after SD day 1: no detectable SOD1 difference.** Both arms rebounded, mostly in the dark: total
    +188 vs +163 min, SOD1 − water +25 min (CI −68 to +130, p = 0.60).
  - No recovery after day 2: Y-maze, then kept awake until sampling at about 20:00.
- **Meaning:** SOD1 neither protected sleep during SD nor changed the rebound, within about −1 h to +2 h.
- **How to read the actogram:** dark marks are movement. A clean SD day shows movement through the normally quiet
  light hours.

### 5. EEG/EMG sleep stages
- **Shows:**
  - Cohort flow (how many mice reached each tier).
  - Example traces.
  - The scoring check against my own epoch review.
  - Baseline sleep % per mouse, and recovery minus baseline.
- **Results:**
  - **Re-score:** 15 mice now have usable W/NREM/REM at both timepoints (W-SD 1, S-SD 1, W-SL 7, S-SL 6), against 3
    before. The gain is almost all in the normal-sleep cohorts. The SD cohorts lost their recoveries to dead EEG or
    technical EMG, not to the criteria.
  - **Scoring check:** κ 0.95 over 14,077 epochs of HLBSSL33 recovery, light and dark. My review started from the
    rule's labels, so the agreement is partly built in, and a blind check is still owed. The HMM, which never sees
    the rule, reaches κ 0.93 on the light phase.
  - **Baseline, 10 SOD1 vs 11 water:** sleep 52.0 vs 52.5 % of usable time (−0.5 points, CI −4.7 to +3.6,
    p = 0.81). Light 71.7 vs 72.2, dark 31.1 vs 32.6, NREM 45.8 vs 46.5. MDE about 6 points.
  - **Recovery minus baseline (ZT4-24):**
    - Without SD: S-SL +2.1 vs W-SL +0.1 points (6 vs 7, p = 0.52).
    - After SD, one mouse per arm: HLBWSD08 +9.3 points. HLBSSD18 +18.1, but only +1.5 (open circle) if its
      movement-artefact epochs (27 % of the recovery, mostly vigorous wake) count as wake.
    - SWA, first 4 h of recovery: 114 % (water SD) and 117 % (SOD1 SD) of baseline, against 107 % and 93 % without
      SD. SD raised sleep pressure as expected.
- **Meaning:** no detectable SOD1 change in sleep amount or NREM. The SD arms are two single cases and cannot be
  compared.
- **Trap:** the old 2026-10-06 quick compute said 61.1 vs 60.6 % of 24 h. The re-score (52.0 vs 52.5 % of usable
  time) replaces it. Report section 5 still quotes the old one.

### 6. Behaviour with normal sleep (HLBNSL, 4 vs 5)
- **Shows:** the test battery schematic, how each endpoint is computed, then Y-maze, open field and NOR per mouse.
- **Results:**
  - **Y-maze:** SA 60.5 vs 62.8 % (−2.2, CI −10.3 to +5.8, p = 0.73). Every mouse above 50 %. Arm entries 48.3 vs
    38.4 (p = 0.063).
  - **Open field:** distance 63.9 vs 51.1 m (g +1.66, p = 0.11), immobility 66 vs 135 s (p = 0.06), centre time
    no difference.
  - **NOR:** d2 +0.34 vs +0.37 (model 1, p = 0.73). Both arms prefer the novel object (9 of 9 mice, p = 0.004).
    No reliable side preference in training.
- **Meaning:** working and recognition memory are intact in both arms, with no detectable SOD1 difference. SOD1 mice
  look more active.
- **Trap:** test order. All four SOD1 mice were tested first, then the five water mice, so every group difference
  here is also a difference in test order and time of day. Say it before anyone asks.

### 7. Y-maze after SD (NS-SD, 5 vs 5, tested straight after SD day 2)
- **Shows:** SA % and arm entries after SD, next to the rested HLBNSL mice for context (different cohorts,
  descriptive only).
- **Results:**
  - SA 54.6 vs 55.3 % (SOD1 vs water), −0.7 points (CI −15.4 to +14.0, p = 1.00).
  - Arm entries 35.6 vs 35.2 (p = 0.55).
  - Neither group alternates above chance (Wilcoxon vs 50 %: water p = 0.44, SOD1 p = 0.31).
  - SA % does not follow each mouse's real SD length (r = +0.05), but the start times are 15 min slots, not clock
    reads.
- **Meaning:**
  - **SOD1 did not protect working memory after SD**, within a wide CI.
  - Rested HLBNSL mice were at 60 to 63 %, so the drop to chance is consistent with an SD effect, but that is a
    comparison between cohorts, not proof.
  - The extra arm entries of SOD1 mice in HLBNSL do not appear here, in a cohort tested in alternating order. That
    supports the idea that the HLBNSL activity gap came from test order.

### 8. Activity across cohorts (forest plot)
- **Shows:** SOD1 − water as Hedges g with an approximate 95 % CI per activity readout, against the MDE at that n.
- **Results:**
  - Y-maze entries +1.19 (p = 0.063) and open-field distance +1.66 (p = 0.11), both HLBNSL, the same 9 mice.
  - NS-SD dark-phase tag activity change +1.38 (p = 0.040), first 6 days only, gone by days 8 to 10.
  - The one change seen in **both** nanotag cohorts is a quieter light phase with SOD1 (NS-SD −113 vs +77 counts/h,
    p = 0.17).
- **Meaning:** a pattern to measure, not a finding. The CIs are a normal approximation, which is why one can exclude
  0 while its exact test does not.

### 9. Tissue (EEG cohorts)
- **Shows:** total SOD in hippocampus and heart, and hippocampal MDA, per mouse, four groups.
- **Results:**
  - **Hippocampal SOD:** no detectable SOD1 difference (normal sleep −2.3 U/mL, CI −6.1 to +1.6). The SD cohorts ran
    on a different plate, so their higher values are not read as a sleep effect.
  - **Hippocampal MDA:** no SOD1 difference. Higher in the SD cohorts overall (p = 0.007), but SD and normal sleep
    were separate cohorts, and tissue was taken about a day after the last SD bout.
  - **Heart SOD: a crossover** (interaction p < 0.001). SOD1 higher with normal sleep (+5.6 U/mL, Šidák
    p = 0.060), lower after SD (−8.2, p = 0.005). It depends on single mice.
- **Meaning:**
  - The hippocampus result is what I would expect: unprotected oral SOD is mostly digested (Vouldoukis 2004), and
    anything absorbed would still need to reach the brain.
  - The heart pattern is interesting (oral melon SOD raised cardiac SOD in hypertensive rats, Carillon 2014), but
    four groups from four cohorts can make this pattern with no SOD1 effect at all.
- **What would settle it:** assay the stored HLBNSL and NS-SD tissue, where both arms share a cohort.
- **Trap:** the heart percentages in report section 7 come from the sheet method, while the table uses the Cayman
  values (+39 %, −20 %, +26 %). Quote the table if asked.

### 10. Conclusions
1. **Safety:** no sign of harm in drinking, weight, behaviour or the markers measured. SOD1 mice drank slightly less.
2. **Sleep with normal sleep:** no detectable change by either method (EEG excludes differences beyond about 5
   points of sleep %).
3. **Sleep structure:** no detectable change in NREM, bout length or light/dark distribution.
4. **After SD:**
   - SD removed the same sleep in both arms.
   - The rebound did not differ.
   - Working memory fell to about chance in both arms, with no SOD1 protection.
5. **Activity:** quieter light phase with SOD1 in both nanotag cohorts, other signals inconsistent or confounded.
6. **Oxidative stress:** nothing in the hippocampus. The heart crossover needs the within-cohort assay.
7. **Overall:** at this dose and route, the data do not show a sleep-promoting effect of SOD1. They cannot exclude
   small effects, or an effect of a form protected for oral delivery.

## Part 3: questions to expect

- **"So SOD1 does nothing?"**
  - No detectable effect at sizes this study could see.
  - The CIs say how big an effect could still hide: NS-SD sleep about −20 to +60 min/day, EEG about ±5 points.
- **"Why so few mice?"** Rig capacity (8 at once), EEG yield, and nanotag cohorts sized for a first look. For a
  realistic effect (d = 1.0) it takes about 17 mice per group, about 9 for d = 1.5.
- **"Are EEG and nanotag saying the same thing?"** Each shows no detectable change on its own, in different mice with
  different methods. I do not use one to confirm the other.
- **"Is the nanotag a valid sleep measure?"** Immobility sleep agrees well with EEG in published mouse work, but this
  tag was not validated against EEG here. It cannot see NREM vs REM and counts quiet wake as sleep.
- **"How do you know the EEG scoring is right?"**
  - It is your rule, unchanged; only the EMG band moved away from the mains.
  - It was checked against my epoch review at κ 0.95, and an independent HMM agrees.
  - Still owed: a blind check on another mouse.
- **"Did SD actually work?"** Yes:
  - All 10 NS-SD mice were well below baseline on both days (about 8 to 17 % asleep against about 70 %).
  - There was a clear rebound afterwards.
  - EEG SWA rose after SD.
- **"Is the Y-maze drop after SD real?"** Plausible, since rested mice were at 60 to 63 % and these are at chance, but
  it is a comparison between cohorts. The within-cohort result is SOD1 vs water, which shows no difference.
- **"Why did SOD1 mice move more?"** In HLBNSL the SOD1 mice were all tested first, which confounds it. After SD, in a
  cohort tested in alternating order, arm entries were equal. The light-phase quieting is the only consistent
  activity signal.
- **"Is NOR valid if the novel object was always the same one on the same side?"** No side preference in training
  (7 of 9 above 50 %), and the share at the novel spot rose from training to test in 9 of 9 mice. Not
  counterbalancing is a listed limitation.
- **"Why total SOD and not SOD1?"** The kit measures all forms together. It answers "is antioxidant capacity higher",
  not "did the supplement's enzyme arrive".
- **"Why not gavage, as in the proposal?"** Gavage stress changes sleep and behaviour, the very outcomes. The cost is
  that the dose depends on intake, which I measured.

## Part 4: words to use and words to avoid

| say | do not say |
|---|---|
| no detectable difference, compatible with −X to +Y | no effect, SOD1 does not work |
| a pattern to measure | SOD1 increases activity |
| consistent with an SD effect (between cohorts) | SD impaired memory |
| a cohort difference | an SOD1 effect (for anything between EEG cohorts) |
| the nanotag result and, separately, the EEG result | the nanotag agrees with the EEG |
| n = 1 per arm, a case | the SD EEG arms show |
| REM is not reported | REM % was … |

## Still open
- Deck slides for the NS-SD Y-maze after SD: the deck was built before the result and needs `behaviour.py` and
  `build.js` rerun on the office PC.
- `ymaze_2x2.py` (rested vs deprived side by side) waits for the NS-SD pose distance.
- NS-SD and HLBNSL tissue at −80 °C, not yet assayed: decision 1 for the professor.
- A blind EEG scoring check on a second mouse.
- Two S-SL deaths to confirm in the sheet (HLBSSL36, HLBSSL37).
- Report v0.2 fixes listed in [[2026-11-05-hlb-progress-meeting-figures#Notes for checking the draft (found while making the figures, the draft is unchanged)]].

---
type: decision
area: hlb-sod1
status: active
created: 2026-11-02
summary: "Storyline for the English HLB report on oral SOD1: what we show, in what order, why each design choice was made (incl. why the SD arm runs the Y-maze only), what data are still missing; framing from Andrea 2026-11-02"
tags: [hlb, sod1, report, design]
---

# 2026-11-02: HLB final report, storyline and rationale

> [!abstract] TL;DR
> - **Framing (Andrea, 2026-11-02):** an exploratory characterisation, not a test of one expected result.
>   Does oral SOD1 in drinking water change sleep, activity or cognition, with or without sleep deprivation,
>   and is there any sign of harm? Expected overall message: **no abnormalities, no toxicity, nothing drastic.**
> - **Order:** tolerability and intake → sleep and activity (nanotag) → sleep architecture (EEG/EMG,
>   a small separate sub-study) → behaviour (rested battery; Y-maze under SD) → tissue (SOD activity, MDA)
>   → what it means and what it cannot show.
> - **Format:** English document for now. Sampling data come from Andrea later.
> - **Out of scope:** the SPF gavage batch (sampling only, for something else) and the planned final
>   EEG batch of 10 mice (later, new timeline).
> - **Missing before a draft:** NS-SD Run 2 (SD, recovery) and its Y-maze, intake and body-weight
>   analysis from the sheet, tissue assays, EEG manual scoring.

## What the report has to say, section by section
> [!note] 2026-11-02, later: the status column below is frozen at the time of writing. The live status of each
> section is in the draft, [[2026-11-02-hlb-sod1-final-report-draft]], which is now the working document.

Status: ✅ analysed · 🟡 partly · ⬜ not yet.

| # | Section | What we show | Status, source |
|---|---|---|---|
| 1 | Aim and what changed from the proposal | Proposal vs delivered: drinking water instead of gavage, nanotag instead of EEG for most mice, 2-day 6 h SD instead of 7-day 4 h restriction, n 4-5 per arm | ✅ [[hlb-sod1-design]] |
| 2 | Tolerability and dosing | Liquid intake per day (SOD1 vs water), body weight, health notes; dose actually received (U/day) | ⬜ sheet `HLB_SOD1_Intake_Monitoring_SDSLNANO`, never analysed in the vault |
| 3 | Sleep and activity, nanotag | Sleep amount (24 h, light, dark), fragmentation (bout number and length), daily rhythm (rhythm amplitude), activity counts; rested batch, then SD batch: baseline vs SOD1, SD days, recovery | 🟡 HLBNSL ✅ [[2026-10-05-HLBNSL-nanotag-merged-analysis]]; NS-SD Run 1 ✅ [[2026-10-31-NS-SD-run1-nanotag-baseline-vs-sod1]]; Run 2 ⬜ |
| 4 | Sleep architecture, EEG/EMG | NREM, REM, wake, rested and after SD; 1-3 scoreable mice per arm, so cases | 🟡 [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]]; manual scoring stopped at 39 % of one mouse (2026-10-08) |
| 5 | Behaviour, rested | Y-maze, open field, NOR (2-day, 2 h retention) | ✅ [[2026-11-02-HLBNSL-behaviour-battery-summary]] |
| 6 | Behaviour, after SD | Y-maze only, why (below); SA %, arm entries, distance, against each mouse's SD length | ⬜ runs 11-04 |
| 7 | Tissue | SOD activity: hippocampus no difference, heart some differences, liver to check; MDA: hippocampus, maybe liver or heart | ⬜ data from Andrea |
| 8 | Interpretation and limits | No harm detected; small n; delivery uncertainties; what a next study needs | ⬜ |

🛑 EEG/EMG and nanotag findings stay in separate sections, never pooled and never used to confirm
each other ([[2026-10-06-eeg-and-nanotag-findings-reported-separately]]).

## The threads the results already show
- **Sleep: no detectable change.** Rested nanotag batch: SOD1 effect +11 min/day (95 % CI −130 to +156).
  SD batch, first 6 days on treatment: +16 min/day (CI about −18 to +58). EEG without SD: 61.1 vs 60.6 %
  of 24 h asleep.
- **Activity: SOD1 mice a little more active, in three readouts, none conclusive.** Y-maze arm entries
  (p = 0.063) and open-field distance (p = 0.11) in HLBNSL; dark-phase tag activity in NS-SD (p = 0.040,
  one of about 20 tests). Same direction, different mice and methods, sleep unchanged. Present it as a
  consistent trend to watch, not a finding. It is also why every cognitive measure is shown next to an
  activity measure.
- **Cognition, rested: no detectable effect** on Y-maze alternation or NOR d2, both above chance.
- **Rhythm amplitude:** the HLBNSL lead (p = 0.029) did not repeat in NS-SD (p = 0.24). Report it as not
  replicated.

## Why each design choice was made (for the methods and for the professor)
1. **Drinking water instead of gavage.** No daily gavage stress, which would itself disturb sleep and
   behaviour. Cost: the dose depends on how much each mouse drinks, so intake must be shown (section 2).
2. **Fresh SOD1 every day.** SOD1 in solution degrades within about 30 h (Andrea), so bottles are changed
   daily. The real dose still depends on activity left in the bottle over the day; say so.
3. **Nanotag for most mice.** The EEG rig left too few scoreable mice. The tags give sleep amount,
   fragmentation, rhythm and activity in every mouse, but no NREM/REM, so the EEG mice are kept as a small
   separate sub-study for architecture.
4. **SD by gentle handling, 09:00-15:00 (6 h, ZT0-6).** The first hours of the light phase are when mice
   sleep most, so 6 h of SD there removes a large share of daily sleep. Gentle handling avoids the
   stress of automated devices. Our reasoning; add a citation before the report.
5. **Rested battery: Y-maze, open field, NOR over 2 days with 2 h retention.** Reasons in
   [[2026-11-02-HLBNSL-behaviour-battery-summary#Why NOR runs over 2 days with a 2 h retention interval]].
6. **SD arm: Y-maze only.** Below.
7. **Statistics.** The proposal planned two-way ANOVA with Tukey. At n = 4-5 per arm the analyses use exact
   permutation or Mann-Whitney tests and report effect sizes with confidence intervals. Decide which one the
   report leads with (question 4).

## Why the SD arm runs the Y-maze only
Decision 2026-10-30: [[2026-10-30-NS-SD-two-day-SD-y-maze-only]]. The argument for the professor:

1. **The Y-maze measures the state at the end of SD; NOR would measure SD timing.** Spontaneous
   alternation is one 8 min session with no training and no retention interval (Kraeuter et al. 2019). Each
   mouse is tested straight out of SD, so the test reads working memory under sleep loss. NOR needs
   habituation, training, a retention interval and a test. With 10 mice tested one after another, each
   mouse would get a different amount of SD before training and a different chance to sleep after it.
2. **Sleep after training is exactly what NOR memory depends on.** In mice, 6 h of SD right after training
   abolished object recognition 24 h later, while the same SD 6 h later did not (Palchykova et al. 2006).
   Brief SD also impairs hippocampal plasticity and memory through cAMP-PKA signalling
   (Vecsey et al. 2009). So in an SD design, NOR results would be driven by where SD falls relative to
   training, which varies per mouse. That confound could be larger than any SOD1 effect.
3. **Sleepy mice explore less.** NOR needs at least 20 s of object exploration per trial; deprived mice are
   more likely to fall below it, and with 5 mice per arm every exclusion costs a lot.
4. **One test, less handling, cleaner tissue.** Sampling follows each Y-maze directly, so the tissue for
   the oxidative-stress assays reflects the end of SD, not hours of further testing.
5. **Activity is measured in the same trial.** Arm entries, distance and speed come from the same 8 min, so
   a change in alternation can be separated from a change in activity. That matters because SOD1 mice tend
   to be more active.
6. **The same test ran in the rested arm,** so rested and deprived can be shown side by side
   (SOD1 x sleep on one measure). Caveat: rested vs deprived are different batches (mice, treatment length,
   date), so a difference is "consistent with" an SD effect, not proof of one.
7. **Precedent:** Y-maze alternation is used to read SD-induced working-memory deficits and their rescue by
   an oral supplement in mice (Griffin et al. 2022, probiotics with partial SD; they also ran NOR, within a
   nine-day test paradigm).

What we give up: recognition memory under SD. The rested arm's NOR stands as a characterisation of
normal-sleep mice.

## Data and analyses still to do
- [ ] Intake and body weight per mouse per day, SOD1 vs water, both nanotag batches (and EEG batches if
      logged): mL/day, U/day received, any day with low intake.
- [ ] NS-SD Run 2: SD efficacy (wake during SD, equal in both arms), recovery sleep 11-03 15:00 → 11-04 09:00.
- [ ] NS-SD Y-maze 11-04: hand-scored SA %, entries; plot against each mouse's SD length.
- [ ] Rested vs deprived Y-maze side by side (SOD1 x sleep).
- [ ] Tissue: SOD activity (hippocampus, heart, liver), MDA (hippocampus, maybe liver or heart).
- [ ] EEG: decide whether to finish manual scoring of the scoreable mice or report the automatic staging.

> [!note] 2026-11-02, later: answers from Andrea and next step
> Q1: tissue results arrived and are analysed in [[2026-11-02-EEG-cohorts-tissue-SOD-MDA-reanalysis]] (BBB written
> as one of two reasons, gut digestion first). Q2: activity left in the bottle is unknown and not ours to measure; a
> limitation. Q3: Andrea finishes the EEG manual scoring. Q4: estimation with CIs leads, the proposal's ANOVA kept for
> the tissue (section 8 of the draft). Q5: the document is for the professor to review and edit first, then trimmed for
> HLB. Draft: [[2026-11-02-hlb-sod1-final-report-draft]].

## Questions for Andrea
1. **Tissue reading.** No hippocampal SOD activity difference "because SOD1 does not cross the BBB": is that
   stated in the proposal or by HLB, or is it our interpretation? Oral SOD1 may also not be absorbed intact,
   so a heart difference would be the evidence that some activity reaches the body. Do we write it as a
   hypothesis?
2. **Intake.** Is the daily intake (and body weight) in the sheet complete for both nanotag batches, and
   do we have any measure of how much activity is left in a bottle after 24 h?
3. **EEG.** Finish manual scoring (HLBSSL33 is 39 % done) or report the automatic staging with its validation?
4. **Statistics.** Lead with the proposal's two-way ANOVA (SOD1 x sleep) on Y-maze and sleep, or with the
   permutation tests and effect sizes, the other in a supplement?
5. **Audience.** Is the document for the professor first, then HLB? How technical, and how long?

## References (checked on PubMed, abstracts only)
- Kraeuter AK, Guest PC, Sarnyai Z. The Y-maze for assessment of spatial working and reference memory in mice.
  Methods Mol Biol 2019;1916:105-111. doi:10.1007/978-1-4939-8994-2_10
- Palchykova S, et al. Sleep deprivation impairs object recognition in mice. Neurobiol Learn Mem 2006;85:263-71.
  doi:10.1016/j.nlm.2005.11.005
- Vecsey CG, et al. Sleep deprivation impairs cAMP signalling in the hippocampus. Nature 2009;461:1122-5.
  doi:10.1038/nature08488
- Griffin SM, et al. Restorative effects of probiotics on memory impairment in sleep-deprived mice. Nutr Neurosci
  2022;26:254-264. doi:10.1080/1028415X.2022.2042915
- NOR design: Leger et al. 2013, Lueptow 2017, in [[2026-11-02-HLBNSL-behaviour-battery-summary]].

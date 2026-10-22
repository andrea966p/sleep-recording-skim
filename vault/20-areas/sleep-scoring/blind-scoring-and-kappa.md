---
type: procedure
area: sleep-scoring
status: planned
status-note: "ready to run"
tags: [procedure, eeg, scoring, kappa, validation, pre-registration]
created: 2026-08-08
---

# Blind scoring and Cohen's kappa: how to run it, and what the answer will mean

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The pipeline has never been checked against a person. This is the procedure for
> scoring a few hundred epochs by hand, without being able to see what the computer decided, and
> then measuring how well the two agree.
>
> **Why it exists.** Everything else about the analysis is now measured except this. And the
> 2026-08-08 sensitivity sweep showed that the single threshold separating wake from sleep can move
> the headline result from 23% to 89%, so there is currently **no principled way to place it**. A
> human reference is the only thing that fixes that.
>
> **How to read this page.** §1 is how to do it. §2 is what the number means, **written before the
> scoring so it cannot be reinterpreted afterwards**. Big picture:
> [[2026-08-07-council-review-of-the-analysis-pipeline]].

## 1. Doing it

### 1.1 What is ready

| pack | animal | items | kind |
| --- | --- | --- | --- |
| `portD-slot2_..._SCORING/` | **D2 overnight** | 300 | stratified, equal n per automatic state |
| `portB-slot1_..._SCORING/` | B1 overnight | 300 | stratified |
| `portD-slot2_SCORING_random/` | D2 overnight | 299 | **unstratified**, prevalence matched |

All under `/home/skimlab/eeg-processed/2026-08-06/`.

> [!important] Score D2 first, and score the stratified pack first
> D2 is the animal whose circadian figure swings **65.9 points** across the threshold sweep, so it
> is where a human reference changes the most. Its 70.3% is also the number currently doing work in
> the professor handout.

### 1.2 The session

1. Open `score.html` from the pack folder in a browser.
2. Each item shows **20 seconds**. Score **only the shaded 4 second epoch in the middle**. That is
   the lab's normal viewing convention, five epochs at a time.
3. Keys: **1** WAKE, **2** NREM, **3** REM, **4** unsure. **Backspace** goes back.
4. Progress is stored in the browser, so you can stop and resume. Do not clear site data.
5. When finished press **save CSV** and put it in the pack folder as `scoresheet.csv`.
6. Then:
   ```bash
   python3 ~/Monitoring_project/eeg-emg-analysis/qc/score_kappa.py <SCORING_DIR>
   ```

### 1.3 Rules for the scorer

- **Use UNSURE freely.** Forcing a call on a genuinely ambiguous epoch manufactures agreement or
  disagreement out of nothing. UNSURE items are excluded from kappa and counted separately.
- **Do not open `_TRUTH_do_not_open.csv`** until you have finished and saved.
- **Do not score in one long sitting.** Fatigue produces drift, which looks like disagreement.
  Two or three sessions is better than one.
- Items are in **random order on purpose**, so bout structure cannot be followed between them.
  Do not try to reconstruct the timeline.

## 2. 🔴 What the answer will mean — written BEFORE any scoring

> [!danger] This section is a pre-registration
> Written 2026-08-08, before a single epoch was scored. Its purpose is to stop the result being
> reinterpreted after the fact. This project has already had one conclusion reversed by a
> measurement (the arm C tether harm), and the discipline is what caught it.

### 2.1 Overall kappa

| result | what it means | what we do |
| --- | --- | --- |
| **κ ≥ 0.80** | the automatic staging reproduces a human closely | report κ, keep the current staging, place the WAKE cut where Otsu puts it |
| **0.60 ≤ κ < 0.80** | usable but not interchangeable | report κ **with the confusion matrix**, and treat automatic architecture numbers as approximate. Prefer human scoring for any published architecture |
| **0.40 ≤ κ < 0.60** | the automatic staging is a screening tool only | **do not publish automatic architecture.** Use the pipeline for QC and hand-score anything reported |
| **κ < 0.40** | the staging does not reproduce a human | stop using automatic staging entirely and treat the pipeline as what it already demonstrably is, a **signal-provenance instrument** |

⚠️ **Landis and Koch bands are a reading aid, not a pass mark.** The bands above are our decision
rule, chosen in advance, not a standard.

### 2.2 The number that actually decides things: per-state kappa for REM

The pipeline **forces REM to 20% of sleep by construction** (80th percentile of theta/delta among
non-wake). We have said since 2026-08-03 that no REM share may be reported.

| REM κ | meaning | action |
| --- | --- | --- |
| **≥ 0.60** | REM is a real, separable state on this montage | **replace the percentile rule with the 2-cluster k-means split** used by the Japanese tool ([[sleepyscore-japan-scoring-tool-algorithm]]), re-run, and check kappa improves |
| **0.40 - 0.60** | marginal | swap to k-means anyway, but **still do not report a REM percentage** |
| **< 0.40** | REM is not separable with a single bipolar EEG plus EMG | **accept it permanently.** Report WAKE versus NREM only, and state in the methods that REM was not separable rather than quietly omitting it |

### 2.3 Placing the WAKE threshold

The Otsu sweep showed ±25% on the WAKE cut moves D2's "asleep in light" from 23% to 89%. With human
labels we can do better than guess.

**Procedure:** re-run `otsu_sensitivity` over the multipliers, and for each, compute agreement with
the human labels on the scored items. **Choose the multiplier that maximises agreement**, and report
both the chosen value and the curve.

> [!warning] 🛑 The one thing that must not be done
> **Do not choose the threshold that maximises `r@1min`.** B1's persistence peaks at the 0.9
> multiplier rather than at the Otsu cut, so it is tempting. `r@1min` is our independent validity
> statistic; tuning a parameter to maximise it makes it circular and destroys the only check we have
> that the states are real. Agreement with a human is an **external** criterion and is safe.

### 2.4 Prevalence

The stratified pack has equal numbers of each automatic state by design, so **its kappa is a
stratified kappa** and is not what you would get across a whole recording. The unstratified D2 pack
exists for the prevalence-matched value.

**Report both**, and say which is which. If they differ substantially, that difference is itself
informative about how the rare states behave.

### 2.5 What a good result does NOT license

- It does **not** make the circadian result threshold-independent. That was measured separately and
  the swing must still be quoted.
- It does **not** change the fact that four of the five physiology checks are forced.
- It does **not** turn n = 2 animals into a fleet-wide conclusion.

## 3. Afterwards

1. Write the numbers into [[2026-08-07-council-review-of-the-analysis-pipeline]] §6.
2. Apply §2.2 and §2.3 if their conditions are met, then **re-run and check kappa improves**. If it
   does not, revert — that is the whole point of having the number first.
3. The **selection-bias test** can then be strengthened: with human labels, rejection rate can be
   plotted against **human** state rather than inferred from EMG.
   ([[2026-08-07-council-review-of-the-analysis-pipeline]] §8.1 currently uses the EMG proxy.)

> [!quote] Paper-ready, once the number exists
> Automatic staging was validated against blind manual scoring of N randomly ordered 4 s epochs per
> animal, presented with 20 s of surrounding context and without access to the automatic labels.
> Agreement was κ = x (95% CI ...), with per-state values of ... Cohen's kappa is prevalence
> sensitive; epochs were sampled stratified by automatic state, and an unstratified estimate is
> reported alongside.

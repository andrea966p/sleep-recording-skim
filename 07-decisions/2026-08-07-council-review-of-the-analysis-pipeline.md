---
tags: [decision, council, eeg, analysis, methods, review]
created: 2026-08-07
status: current
---

# Council review of the analysis pipeline, its methods and its documentation

> [!abstract] TL;DR
> Five independent advisors reviewed the pipeline, then peer-reviewed each other anonymously.
> They converged hard on one thing: **the pipeline's accuracy has never been measured**, and
> several of the things we present as validation are **circular by construction**.
>
> The most damaging finding is one nobody in this project had named: **our quality gate selects
> epochs on electrode contact, contact is movement-driven, and movement is sleep state** — so the
> epochs we keep are non-randomly enriched for quiet states, and every downstream number inherits
> a bias that correlates with the thing we are measuring.
>
> The council also rejected the premise of the question that convened it. **"Modernise the
> staging" is the wrong move.** We do not have a staging problem, we have a signal-provenance
> instrument with one Otsu threshold bolted on. Adding an HMM or a deep scorer to channels whose
> signal existence we cannot assert makes failure *less* visible.

Reviewed: [[2026-08-07-rig-specification-and-analysis-method]], the four pipeline stages,
[[analysis-methods-and-justification]], and the way results are conveyed in
[[2026-08-07-staging-preregistration]] and [[2026-08-06-rig-status-for-professor]].

## 1. Findings, ordered by how much damage they do

### 1.1 🔴 Selection bias in the QC gate — the one that threatens publication

The gate rejects an epoch when the electrode is not in contact. **Contact on this rig is
movement-dependent, and movement is sleep state.** So the surviving epochs are enriched for quiet
states, and sleep percentage, bout lengths, `r@1min` and the circadian split all inherit a bias
**correlated with the dependent variable**.

**Test required:** plot epoch rejection rate as a function of scored state and show it is flat. If
it is not flat, the circadian result is partly an artefact of when the electrodes happened to
connect. Nothing in the vault currently addresses this.

### 1.2 🔴 Four of the five physiology checks cannot fail

Verified directly in `stage3_features.py`. The council said three; **it is worse than they
thought**.

| check | forced? | why |
| --- | --- | --- |
| `wake_has_highest_emg` | **forced** | WAKE *is* the Otsu split on EMG. This restates the definition |
| `rem_highest_theta_delta` | **forced** | REM *is* the top 20% of theta/delta |
| `rem_emg_low` | **forced** | REM ⊂ non-wake, and non-wake is by definition below the EMG cut |
| `nrem_has_most_delta` | near-forced | NREM is the residual after the high theta/delta epochs are removed |
| **`nrem_largest_amplitude`** | ✅ **genuinely informative** | nothing in the staging rule constrains amplitude |

⇒ **Stop reporting "physiology 5/5 PASS" as validation.** Report the one check that can fail, and
label the rest explicitly as consistency checks on the implementation.

The same objection applies to **"REM entered from NREM 73.9%"**: with REM fixed at 20% of a
residual that is mostly NREM, a high transition rate is close to forced. It needs a
**shuffle-with-persistence null** before it means anything.

### 1.3 "Threshold-independent" is false for the circadian claim

Otsu is **refit per animal**, so the two animals are not on a common scale and the cross-animal
comparison is unlicensed. **Required:** sweep the Otsu cut ±25% and publish how far 70.3% moves.

### 1.4 82.1% is not "about 70%"

We report 70.3% and 82.1% against a literature norm of ~70% and call both "consistent". **That is
one hit and one miss presented as two confirmations.** State the range that would have falsified
us, or drop the claim. We already flagged that B1's 82.1% is above the mean; the framing still
reads as two successes.

### 1.5 🔴 The 112 wire-free nulls are pseudoreplicated

All three peer reviewers, independently, and **nobody in the original round caught it**. The 112
channels share a board, a reference, a ground and a room, so their noise is correlated. **The
effective n is closer to the number of headstages or sessions than to 112**, and every threshold
we derive from that distribution has an unknown width.

**Fix:** cluster or bootstrap the null by session and by headstage rather than treating channels
as independent.

### 1.6 No minimum bout duration was enforced

Verified: nothing in `stage3_features.py` or `qc_thresholds.py` enforces one, and our own output
shows **median NREM and REM bouts of 4 s — single epochs**.

⭐ **This violates our own scoring SOP**, recorded here for the first time:

> **Our scoring convention.** The basic unit epoch is **4 seconds**. We view **5 epochs at once,
> a 20 second window**. After analysis at 4 s, **a stage is not counted if it is shorter than
> three consecutive epochs, 12 seconds.**

### 1.7 Only negative controls exist

Everything we have built is a negative control: wire-free inputs, an empty cable, a no-mouse slot.
**There is no positive control** — a resistor or signal generator of known spectrum pushed through
the whole pipeline to prove it *finds* signal rather than merely rejecting nothing.

### 1.8 Accuracy is unmeasured

Stage 4 exports EDF for blind human scoring and **no scorer has run**. There is no Cohen's kappa
and no confusion matrix. Until that number exists, the defensible claim is "the pipeline runs",
not "the pipeline is accurate".

### 1.9 The documentation

The **structure** was praised as better than most labs: pre-registrations written before data
exists, explicit retraction sections, provenance on every constant. The **prose** was not.
Sentences like *"the wire-free floor is not the quietest thing on the rig"* and *"impedance blocks
screen"* are insider shorthand that a collaborator cannot act on.

## 2. What the council rejected

> [!danger] "Update the pipeline to recent and popular EEG methods" is the wrong instruction
> Multitaper spectra, HMM or GMM state models, replacing Otsu, importing YASA or AccuSleep — the
> council called all of it **busywork at n=2 with zero ground truth**. You could not tell whether
> a new method were worse. Worse, sophisticated staging applied to channels whose signal existence
> is unverified **hides the failure mode we spent three weeks learning to see**.
>
> Validate first. Modernise later, if the validation says the current method is the limitation.

⚠️ The claim that "filtering an open input produces 69 µV of fake EEG" is novel was **challenged
in peer review**: it is plausibly known instrumentation behaviour, filter response to open-input
amplifier noise. It was asserted with **no literature check**. Do that check before building any
argument on its novelty.

## 3. The plan of record

Fixes, in dependency order. Each is applied only after explicit approval.

| # | fix | status |
| --- | --- | --- |
| 1 | **Minimum bout duration: 3 consecutive epochs, 12 s**, per our SOP | ✅ **done 2026-08-08**, see §4 |
| 2 | Blind scoring harness + Cohen's kappa against stage 3 | 🟡 **harness built and tested 2026-08-08; awaiting a human scorer — see §6** |
| 3 | Rejection rate as a function of scored state (the selection-bias test) | ⬜ |
| 4 | Otsu cut ±25% sensitivity sweep on the circadian result | ✅ **done 2026-08-08 — see §5. The result is BAD.** |
| 5 | Relabel the physiology checks honestly; add the persistence-shuffle null for REM order | ⬜ |
| 6 | Cluster the wire-free null by session and headstage | ⬜ |
| 7 | Positive control of known spectrum through the full pipeline | ⬜ |

> [!quote] The council's single first action
> **Score 300 stratified random epochs per animal yourself, blind, and compute Cohen's kappa.**
> Not contiguous hours. Shuffle the order, hide the automatic labels. Everything else on the list
> is unfalsifiable until that number exists — including the selection-bias test, which needs
> scored states to plot rejection rate against.


---

# 4. Fix 1 applied, 2026-08-08 — minimum bout duration

## 4.1 What was checked first

⭐ **The reference was consulted before the constant was written**, and it did not say what we
assumed. According to PubMed, the current IIIS Tsukuba method is **Nakata et al., SLEEP 2025**
([doi:10.1093/sleep/zsae279](https://doi.org/10.1093/sleep/zsae279)), from the Funato and
Yanagisawa group.

| IIIS rule | ours | |
| --- | --- | --- |
| **4 s epochs**, semiautomatic then **visual inspection** | 4 s, automatic only | ✅ epoch / ❌ no visual step |
| **Theta 6-9 Hz** | 6-9 Hz | ✅ exact |
| Delta **1-4 Hz** | 0.5-4 Hz | ❌ differs |
| EEG 0.5-100 Hz, EMG 5-300 Hz, digitised **250 Hz** | 0.5-30 / 10-300, decimated to 250 Hz | partial |
| Episode duration = total time ÷ episode count | same | ✅ |
| **Movement-artifact epochs INCLUDED in state totals** | we exclude them | ❌ opposite |
| For spectra only: exclude artifact epochs **and epochs whose neighbour is a different state** | not done | ❌ missing |
| Power as % of mean total power over **15-30 Hz** | not done | ❌ missing |
| **≥7 d recovery, then ≥9 d habituation on the tether** with counterbalanced arm | tethered day 8-10, ~1 d habituation | ❌ large gap |

> [!danger] 🔴 There is NO minimum bout rule in the IIIS method
> Not 3 epochs, not any value. They compute mean episode duration as total time divided by
> episode count with no minimum applied.
>
> **Our 12 s rule is therefore a house convention, not an IIIS standard**, and
> `qc_thresholds.MIN_BOUT_EPOCHS` records it that way. It is defensible and common in rodent
> work, but it must never be attributed to that reference.

## 4.2 What was implemented

`MIN_BOUT_EPOCHS = 3` in `qc_thresholds.py`; `enforce_min_bout()` in `stage3_features.py`.
Runs shorter than 3 epochs are **merged into the longer neighbouring state**, shortest run first,
iterated until stable, **within unbroken contact blocks only** — merging across a block boundary
would join epochs hours apart, the same class of error as the 2026-08-03 persistence bug.

⚠️ Merge-versus-exclude was an implementation choice, not a stated part of the convention. Merge
keeps the hypnogram continuous and matches SleepSign-style behaviour. It is a one-line switch.

## 4.3 Effect

| | before | after |
| --- | --- | --- |
| B1 bout counts, WAKE / NREM / REM | 1232 / 1672 / 971 | **205 / 258 / 98** |
| B1 bout medians | 12 / 4 / 4 s | **84 / 40 / 22 s** |
| B1 WAKE / NREM | 46.1 / 46.8% | 50.2 / 46.0% |
| epochs relabelled | — | **B1 9.78%, D2 12.64%** |

**The old bout statistics were mostly counting single-epoch flickers.** Counts fell six- to
tenfold.

✅ **The circadian result barely moved**, so it does not depend on this choice: B1 82.1 → 81.2%
asleep in the light phase, **D2 70.3 → 70.4%**.

## 4.4 🔴 The trap this exposed, and the split it forced

Applying the rule made **both of our validity statistics rise with no new information**:

| | unsmoothed | smoothed |
| --- | --- | --- |
| B1 `r@1min` | 0.603 | **0.742** |
| B1 REM entered from NREM | 73.9% | **82.7%** |

Smoothing a state sequence **raises its autocorrelation by construction**, and deleting isolated
single-epoch REM mechanically raises the fraction of REM entered from NREM. Worse, the calibration
in `qc_thresholds.py` — noise −0.035, 4 min bouts +0.510, pass at r > 0.30 — was derived on
**unsmoothed** labels, so it would no longer have applied.

> [!success] The fix: validity on RAW labels, architecture on SMOOTHED labels
> `stage3_features.py` now keeps `lab_raw` and computes **persistence and the REM-order check
> before the merge**, while architecture, bouts and the light/dark split are computed **after** it.
> Both REM-order numbers are reported, and the JSON carries a
> `validity_stats_computed_on` field saying which is which.
>
> This keeps the two jobs separate: *is the signal real* is answered on untouched data, *what is
> the architecture* is answered under the lab convention.

## 4.5 State after re-running all 16 files

| animal | verdict | r@1min (raw) | WAKE / NREM (smoothed) | REM order (raw) | merged | asleep in light |
| --- | --- | --- | --- | --- | --- | --- |
| **B1 overnight** | SCOREABLE | **0.603** | 50.2 / 46.0% | 73.9% | 9.78% | **81.2%** |
| **D2 overnight** | SCOREABLE | 0.499 | 43.4 / 50.0% | 79.5% | 12.64% | **70.4%** |
| B1 afternoon | SCOREABLE | 0.481 | 26.8 / 65.6% | 79.6% | 9.86% | 73.2% |
| other 13 | REJECT | — | — | — | — | — |

Stage 4 EDF packets regenerated; `by-mouse/` relinked, 13 artefacts per animal.
Backups: `qc_thresholds.py.bak`, `stage3_features.py.bak`. Pipeline version now `2026-08-08`.

## 4.6 The four IIIS alignment items — ALL APPLIED 2026-08-08

All four are sourced from Nakata et al., SLEEP 2025
([doi:10.1093/sleep/zsae279](https://doi.org/10.1093/sleep/zsae279)). Delta was applied **last and
alone**, so its effect is attributable rather than confounded with the normalisation change.

| # | item | implementation |
| --- | --- | --- |
| a | **Exclude transition epochs from spectra** | `steady_state_mask()`; an epoch counts only if the preceding **and** following epoch are the same state, evaluated **within blocks** so a block edge counts as a transition. Applies to the spectral summaries **only** — staging and state totals still use every epoch. **5.3-7.5% of epochs excluded.** |
| b | **Normalise power to 15-30 Hz** | `BAND_NORM = (15.0, 30.0)`; new per-state `delta_density` and `theta_density` = band power ÷ 15-30 Hz power, IIIS style. ⚠️ Our EEG filter is 0.5-30 Hz against their 0.5-100 Hz, so the top of the band sits on our roll-off: internally consistent, not numerically identical to theirs. |
| c | **State totals both ways** | `state_totals` reports `of_scored_epochs` **and** `of_whole_recording` plus `unscored_pct_of_recording`. |
| d | **Delta 1-4 Hz** | `BAND_DELTA` 0.5-4 → **1.0-4.0**. |

> [!warning] My first version of item (c) was degenerate and I replaced it
> I initially reported "percentage of epochs in blocks" as the second denominator. **Blocks
> contain only passing epochs by construction**, so that number is identical to "percentage of
> scored epochs" and can never differ. The informative denominator is the **whole recording**,
> which is what exposes how much was discarded: D2 **1.6% unscored**, C1 **100%**.

> [!success] ⭐ Delta 1-4 Hz also suits our hardware
> The acquisition high-pass sits at **1.10 Hz** and irreversibly attenuates 0.5-1.1 Hz before the
> data is written. A 0.5 Hz lower edge was integrating a band the hardware had already eaten.
> Aligning with IIIS removes that inconsistency as a side effect.

### Isolated effect of the delta change, B1

| | delta 0.5-4 | delta 1-4 |
| --- | --- | --- |
| WAKE / NREM | 50.2 / 46.0% | 50.2 / 46.2% |
| REM entered from NREM | 73.9% | 73.0% |
| `r@1min` (raw) | 0.603 | **0.603**, unchanged as expected — the WAKE split is Otsu on EMG |
| NREM delta density | 8.43 | 7.89 |
| **REM theta/delta** | 1.680 | **1.995** |
| NREM theta/delta | 0.369 | 0.399 |
| asleep in light | 81.2% | 81.0% |

⭐ **REM/NREM separation on theta/delta improved**, 4.55× to **5.00×**, because the narrower delta
band is a smaller denominator. Physiology still passes on every check.

## 4.7 State after all four alignment items

| animal | verdict | r@1min (raw) | WAKE / NREM | REM order (raw) | unscored | transitions excluded | asleep in light |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **B1 overnight** | SCOREABLE | 0.603 | 50.2 / 46.2% | 73.0% | 0.0% | 5.3% | **81.0%** |
| **D2 overnight** | SCOREABLE | 0.499 | 43.5 / 49.9% | 78.0% | 1.6% | 7.5% | **70.3%** |
| B1 afternoon | SCOREABLE | 0.481 | 26.6 / 65.5% | 80.0% | 0.0% | 6.0% | 73.4% |

**D2 is still at 70.3% asleep in the light phase against a literature ~70%**, through four method
changes. That number has now survived the minimum-bout rule, transition exclusion, renormalisation
and a delta band change without moving.

Stage 3 and stage 4 re-run on all 16 files; `by-mouse/` relinked. Pipeline version `2026-08-08`.

## 4.8 Still outstanding — fixes 2, 3, 5, 6, 7

The alignment work did **not** touch the council's most serious findings. Still owed:
**kappa against blind human scoring** (fix 2) · **rejection rate vs scored state**, the selection-bias
test (fix 3) · **relabel the physiology checks honestly** and add the persistence-shuffle null for
REM order (fix 5) · **cluster the wire-free null by session** (fix 6) · **a positive control** (fix 7).
Fix 4, the Otsu ±25% sweep, is the cheapest of these and would strengthen the circadian claim
immediately.


---

# 5. Fix 4 applied, 2026-08-08 — the Otsu sweep, and what it did to the circadian claim

## 5.1 What was swept, and how

The WAKE / non-WAKE split is an Otsu cut on **log10(EMG rms in µV), refit per animal**. "±25%" is
ambiguous in log units, so the sweep multiplies the threshold **in linear µV** by
0.75, 0.90, 1.00, 1.10 and 1.25 — in log10 that is ∓0.097. Five points, so the shape is visible
rather than just the endpoints. Architecture uses the smoothed labels and persistence the raw ones,
exactly as the headline pipeline does, so the rows are directly comparable to reported values.

`OTSU_SENSITIVITY_MULTIPLIERS` in `qc_thresholds.py`, `otsu_sensitivity()` in `stage3_features.py`.
Written into both the features JSON and the text summary.

## 5.2 🔴 The result

| animal | reported asleep-in-light | range across ±25% | **swing** |
| --- | --- | --- | --- |
| B1 afternoon | 73.4% | 60.9 - 82.8% | 21.9 pts |
| B1 overnight | 81.0% | 54.4 - 90.3% | 35.9 pts |
| **D2 overnight** | **70.3%** | **23.0 - 88.9%** | **65.9 pts** |

D2 in full:

```
  mult   thr uV   WAKE%  asleep light%   r@1min
  0.75    19.64    84.7           23.0    0.654
  0.90    23.57    62.4           52.0    0.601
  1.00    26.19    43.5           70.3    0.499
  1.10    28.80    27.1           81.7    0.455
  1.25    32.73    13.5           88.9    0.379
```

> [!danger] 🔴 The circadian validation is threshold-dependent, and severely so
> A ±25% change in a single per-animal threshold moves D2's headline number from **23% to 89%**
> asleep in the light phase. The literature value of ~70% is reachable from almost anywhere in
> that range.
>
> **The 70.3% agreement is therefore not the independent confirmation it was presented as.**
> The council said "threshold-independent is false". It is worse than false; the number is close
> to being determined by the cut.

> [!warning] ⚠️ This corrects something I wrote on 2026-08-08
> I described D2's 70.3% as "the cleaner number of the two" because it sat nearer the literature
> mean than B1's 81-82%. **That was wrong on this axis.** D2 is by far the *more* fragile animal:
> a 65.9 point swing against B1's 35.9. Proximity to the literature value said nothing about
> robustness, and I should not have used it as a quality ranking.

## 5.3 What it actually diagnoses

A ±0.097 log10 shift only moves the answer this much if **the EMG distribution has no clear
bimodal valley** — Otsu is placing a cut inside a continuum rather than in a gap. The ranking is
consistent with signal quality: B1's EMG hum was 15.2 µV with 0.0% unscored, D2's 26.6 µV with
1.6% unscored. **The sweep is measuring how well-separated wake and sleep muscle tone actually are,
and for D2 the answer is: not very.**

That is a more useful piece of information than the circadian agreement was.

> [!important] What must change in how this is reported
> - **Never describe the circadian check as threshold-independent or threshold-free.**
> - **Quote the swing next to the headline number**, e.g. "70.3%, range 23.0-88.9% across a ±25%
>   sweep of the WAKE threshold". The text summary now prints this automatically.
> - The claim that the result "survived four method changes" (§4.7) **still stands** — minimum
>   bout, transition exclusion, renormalisation and the delta band all left it near 70%. But those
>   four were the wrong things to stress-test. **The WAKE cut was the sensitive parameter all
>   along, and it was the one we had not varied.**

> [!note] A tempting fix that must be refused
> B1's persistence peaks at the 0.90 multiplier (r = 0.689) rather than at the Otsu cut
> (r = 0.603), so one could choose the threshold that maximises within-block persistence. **Do not.**
> `r@1min` is our validity statistic; tuning the threshold to maximise it would make it circular
> and destroy the only independent check we have that the states are real.

## 5.4 What this makes urgent

The sweep converts fix 2 from "good practice" into **the blocking item**. The only way to know
which multiplier is right is a **human-scored ground truth and a Cohen's kappa**; without it there
is no principled way to place the WAKE cut, and every architecture number inherits that.

An implementation bug was also caught and fixed during this work: `stage()` returns an empty
threshold dict for recordings with no usable epochs, which raised `KeyError: emg_otsu_log10` on all
13 rejected animals. Guarded; all 16 files re-run clean.


---

# 6. Fix 2, the kappa harness — built 2026-08-08, awaiting a scorer

Two scripts in `eeg-emg-analysis/qc/`. Both need `~/eeg-analysis-venv/bin/python`.

```bash
python3 make_scoring_set.py <npz> [--n 300] [--random] [--seed N]
python3 score_kappa.py <SCORING_DIR>
```

## 6.1 Design, and why each choice was made

| choice | reason |
| --- | --- |
| **20 s per item, score the shaded centre 4 s epoch** | matches the lab convention exactly: 4 s epochs viewed 5 at a time |
| **Items in RANDOM order** | scoring contiguous data lets a human follow bout structure, which inflates agreement for the wrong reason. Randomising forces each epoch to be judged on its own evidence, which is what a per-epoch classifier is being compared against |
| **Stratified, equal n per automatic state** | REM is only 4-7% of epochs, so a random 300 would yield too few to say anything about the state we most need to test |
| **Fixed y-axis across every item** | auto-scaling leaks state information — a quiet epoch autoscaled looks as large as a loud one |
| **Automatic label never shown, never in the filename** | truth lives in `_TRUTH_do_not_open.csv` |
| **UNSURE is an allowed answer** | forcing a guess on an ambiguous epoch manufactures agreement or disagreement. UNSURE items are excluded from kappa and counted separately |

⚠️ **Stratification makes this a stratified kappa.** Kappa is prevalence-sensitive, so it is **not**
the value you would get across the whole recording. The script prints this warning itself. Use
`--random` to build a prevalence-matched pack as well.

## 6.2 What it reports

Cohen's kappa with a **bootstrap 95% CI**; **per-state kappa** (each state against the rest);
the **confusion matrix** with the human as reference; raw agreement; and counts of blank and
UNSURE items.

Landis & Koch bands are printed as a reading aid, **not as a pass mark**.

> [!important] The number that actually matters is REM
> The pipeline **forces REM to 20% of sleep by construction**. If the human does not agree on REM,
> that is the measurement finally telling us what we have suspected since 2026-08-03 — and it is
> the only way to replace the percentile rule with a defensible absolute threshold.

## 6.3 Validation of the harness itself

Tested against a **simulated scorer with 15% injected disagreement and 3% UNSURE**, in a temporary
copy so no fake scoresheet could contaminate the real pack. Recovered 82.0% raw agreement,
**kappa 0.730, 95% CI [0.661, 0.791]**, with a confusion matrix showing the injected errors
symmetrically. The arithmetic is correct.

## 6.4 Packs ready

| pack | items | size |
| --- | --- | --- |
| `portB-slot1_..._SCORING/` (B1 overnight) | 300 | 27 MB |
| `portD-slot2_..._SCORING/` (D2 overnight) | 300 | 23 MB |

Both verified **unscored**. Open `score.html` in a browser: keys **1/2/3/4** for WAKE / NREM / REM /
unsure, backspace to go back, progress saved in the browser so it survives a reload, then
**save CSV** over `scoresheet.csv`.

> [!danger] Score D2 first
> D2 is the animal whose circadian result swings **65.9 points** across the Otsu sweep (§5). It is
> the one where a human reference will change the most, and the one whose 70.3% is currently
> load-bearing in the professor handout.

## 6.5 What the kappa unblocks

- Places the **WAKE threshold** on evidence instead of on Otsu, which §5 showed the circadian
  result depends on almost entirely.
- Lets the **percentile REM rule** be replaced with an absolute theta/delta threshold.
- Turns "the pipeline runs" into "the pipeline is accurate to κ = x", which is the claim a
  reviewer will actually ask for.
- Fix 3, the selection-bias test, **needs human-scored states** to plot rejection rate against, so
  it is gated behind this too.


---

# 7. The Japanese scoring tool's source code, read 2026-08-08

We were given `SleepyScoreApp_HM_260312_exported.m` and `sleepy_pipeline_refined.py`, the tool used
in Japan to score these recordings. Full algorithm and comparison:
[[sleepyscore-japan-scoring-tool-algorithm]].

> [!success] 🔴 It answers the worst open problem in our pipeline
> **They do not use a percentile for REM. Both their thresholds are 2-cluster k-means splits**,
> WAKE on the EMG integral and REM on the theta/delta ratio among sleep epochs, with the threshold
> taken as the mean of the two cluster centres.
>
> Our 80th-percentile rule **forces REM to 20% of sleep by construction** and has been unreportable
> since 2026-08-03. **The reference method removes that problem entirely**, and our existing
> `rem_measured` Otsu cross-check is already most of the implementation.

> [!note] Their WAKE rule and ours are near-equivalent
> k-means with k=2 on 1-D data and Otsu's method optimise the same split. **So our Otsu cut is a
> fair implementation of their approach** — and the ±25% sensitivity measured in §5 therefore
> applies to their tool as well, not just ours.

⚠️ **A conflict with a change made earlier the same day.** We moved `BAND_DELTA` to 1-4 Hz citing
the paper. The tool low-passes at **4.5 Hz** for staging. Both are right for different jobs: the
paper's 1-4 Hz is for **reporting spectra**, the tool's 0-4.5 Hz is for **staging**. We use one
constant for both and should split it.

⚠️ Their delta and theta features are **time-domain rectified integrals**, `sum(|filtered|)`, not
Welch band powers. Not comparable numerically, so **their threshold values cannot be transferred to
our features**.

✅ **Confirms the paper on the point that mattered: there is no minimum bout rule anywhere in the
code.** Our 12 s rule remains correctly documented as a house convention.

> [!danger] Nothing from this has been applied, deliberately
> Swapping the REM rule changes every REM number we have, and the council was explicit that method
> changes at n = 2 with no ground truth are unfalsifiable. **Score the blind packs first**, then
> make the change and measure whether kappa improves. That is now the ordering: kappa, then the
> k-means REM rule.

| # | fix | status |
| --- | --- | --- |
| 8 | **Replace the p80 REM rule with a 2-cluster split** (reference method) | ⬜ **gated behind the kappa** |
| 9 | Split `BAND_DELTA` into staging 0-4.5 Hz and reporting 1-4 Hz | ⬜ |
| 10 | Median fallback for degenerate recordings, as they do | ⬜ |

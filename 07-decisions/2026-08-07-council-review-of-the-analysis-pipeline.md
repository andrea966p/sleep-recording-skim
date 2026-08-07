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
| 2 | Blind scoring harness + Cohen's kappa against stage 3 | ⬜ |
| 3 | Rejection rate as a function of scored state (the selection-bias test) | ⬜ |
| 4 | Otsu cut ±25% sensitivity sweep on the circadian result | ⬜ |
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

## 4.6 Approved next, not yet applied

The four IIIS alignment items, all sourced from the paper above:
**exclude transition epochs from spectra** · **normalise power to 15-30 Hz** ·
**switch delta to 1-4 Hz** · **report state totals both ways**.

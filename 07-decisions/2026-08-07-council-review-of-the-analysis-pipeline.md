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
| 1 | **Minimum bout duration: 3 consecutive epochs, 12 s**, per our SOP | ⬜ |
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

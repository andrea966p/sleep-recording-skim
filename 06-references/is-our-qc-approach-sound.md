---
tags: [reference, eeg, methods, literature, qc]
created: 2026-08-21
status: active
---

# Is our QC approach sound, or are we doing something very wrong?

> [!abstract] TL;DR
> **The method is not wrong.** The in-file wire-free floor is a per-recording version of
> **shorted-input noise testing**, which is genuinely standard instrumentation practice. Grouping it
> per amplifier chip is physically correct, because each chip has its own reference and ground.
>
> **What is non-standard is using it as a live per-file criterion** rather than a one-off bench
> characterisation. No published method does this. That is a gap in the field, not an error in us —
> the standard literature handles the same question **by eye**.
>
> 🔴 **The real risk is not the method. It is effort allocation.** This rig's binding constraint is
> that 5 of 8 channels fail for HARDWARE reasons. No amount of analysis fixes that, and the project
> has never yet produced a hypnogram, which is the only currency the field actually reads.

## What the literature actually does

Searched 2026-08-21 across PubMed and (via web search) bioRxiv. Findings:

**1. The closest standard analogue to our floor is shorted-input noise testing.** You short all
channel inputs together at the connector and measure what the amplifier produces with no signal.
That is a recognised way to characterise an amplifier's noise floor. Our 14 unwired inputs per chip
are doing the same thing passively, and continuously.

**2. The field asks our question, but answers it qualitatively.** Standard rodent sleep methods
exclude animals "if data exceeds the dynamic range, is contaminated, or is compromised by
significant environmental noise" — judged by a person, by eye, with no stated threshold.
Source: *EEG Recording and Analysis for Sleep Research*, https://pmc.ncbi.nlm.nih.gov/articles/PMC2824445/

**3. Everything published downstream assumes the signal is already good.** The modern automated
staging tools all start from data a human has already judged usable:

| tool | performance | note |
|---|---|---|
| REST (transformer) | Cohen's κ **0.873** | trained on *"116 days of **artifact-free**, pre-labeled recordings"* — https://doi.org/10.1093/sleepadvances/zpag044 |
| Sleep Analyzer Complex | **97.4-98.1%** accuracy | benchmarked against human-scorer agreement of **97.3-97.8%** — https://doi.org/10.1038/s41598-024-74008-0 |
| MLS-Net | 90.4% accuracy | multimodal EEG+EMG+eye movement — https://doi.org/10.3390/bios14080406 |
| NT1 phenotype pipeline | 97% accuracy | states plainly: *"it is sensitive to artifacts"* — https://doi.org/10.1093/sleepadvances/zpaf025 |

⭐ **Note the common currency: every one of them reports agreement with human scorers.** That is what
the field reads. It is also the one thing this project does not yet have.

## So: is our direction correct?

### ✅ What is sound, and should not be second-guessed

- **The in-file floor.** Comparing a channel to unconnected inputs recorded through the same hardware
  at the same moment is a real measurement, not a heuristic.
- **Per-chip grouping.** Each RHD2216 has its own reference and ground. A comparator must share the
  noise physics of what it judges. This is physics, not a statistical preference.
- **The verdict ladder** — refusing to draw rung N when rung N-1 failed. This is better discipline
  than most published work, and it is what stopped a hypnogram being published for an unconnected
  amplifier input.
- **Refusing the slope criterion on EMG.** Correct. Muscle is broadband; a slope test calls a working
  EMG channel dead.
- **The falsification habit.** On 2026-08-21 it removed two of four apparent passes, including the
  animal with the best number on the rig. That is the system working.

### 🔴 Where time is genuinely at risk of being wasted

1. **The bottleneck is hardware, not analysis.** 5 of 8 channels fail: B1 is a floating chip (dead
   across two different animals), B2 has an open EMG electrode at 427 µV, D1 degraded mid-recording.
   **Fixing the ground connection on the B1 port is worth more than any refinement of the floor.**
2. **No hypnogram has ever been produced.** Weeks have gone into deciding which channels are usable,
   which is upstream of the actual result. The field's benchmark is κ against a human scorer.
3. **The QC metric is not the deliverable.** It is worth exactly as much as it protects a real result
   from being wrong, and no more.

### ⚠️ Where a WRONG ANSWER was actually possible — and one nearly happened

**The delta-ratio artefact, caught 2026-08-21.** State-dependence had been measured against the delta
*ratio*, which carries EMG-band power in its denominator. Muscle bleed into the EEG channel would
therefore drive the correlation negative **in a dead animal**. Recomputed against absolute delta
power, C1 — the strongest result on the rig — collapsed from -0.733 to -0.009.

🔑 **That is the class of error that produces a confidently wrong paper.** It was not a QC failure;
it was a physiology-arithmetic failure, and no amount of floor refinement would have caught it.
**Test state-dependence on absolute delta power, never on the ratio alone.**

Still open in the same class: the `r <= -0.30` bar is crossable by pure interference (16 of 112
wire-free channels reach it), and the per-chip floor rests on 14 samples with no confidence interval.

## The honest summary

**We are not doing something very wrong.** The method is a defensible, quantitative version of
something the field does informally, and the discipline around it is better than average.

**But the method is not the risk.** The risks are (a) spending analysis time while the yield problem
is a ground connection and an open electrode, and (b) arithmetic artefacts of the delta-ratio kind,
which look like great results and are invisible to QC.

**The corrective is not more QC. It is to produce a hypnogram on A1, A2 or D2 and get a second
human to score against it.** Everything else is preparation.

## Caveat on this search

bioRxiv's API offers no keyword search — category and date only — so preprints were sampled via web
search over biorxiv.org rather than swept systematically. This is enough to establish "no standard
method exists for this", which is all it is used for here. It is **not** a novelty search and must
not be cited as one.

Related: [[05-experiments/completed/2026-08-21-39h-run-score]] ·
[[02-procedures/eeg-data-analysis/animal-card-and-verdict-ladder]] ·
[[02-procedures/eeg-data-analysis/analysis-methods-and-justification]]

---
type: reference
area: eeg-analysis
status: active
tags: [procedure, eeg, qc, figures, cards]
created: 2026-08-09
---

# The animal card and the verdict ladder

> [!important] What this page is for
> This is the page to read before you check a new mouse, and before you make any
> figure. It replaces "run a script and squint at the output" with one artefact
> per animal-recording that says how far up the chain of questions that animal
> got, and why it stopped there.

## TL;DR

Every animal-recording goes through **six rungs, in the same order, forever**. The
result is an **ANIMAL CARD**: one A4 page plus a JSON file holding every number.
Eight cards collapse into one **COHORT SHEET**. Every figure you will ever want,
including anything the professor sees, is a filtered view of those cards rather
than a new script.

```bash
# 1. verdicts  ->  one JSON per animal-recording
~/eeg-analysis-venv/bin/python cards/ladder.py <recording> \
    --cohort HLB-fem-profsurgery-troubleshooting \
    --cache /home/skimlab/eeg-qc-cache/feat_<recording>.npz

# 2. the pages
~/eeg-analysis-venv/bin/python cards/render_card.py cards/out/<cohort>/
~/eeg-analysis-venv/bin/python cards/render_cohort_sheet.py cards/out/<cohort>/

# 3. the exports the professor opens
~/eeg-analysis-venv/bin/python cards/export_text.py /home/skimlab/eeg-processed/<day>/
```

All of it lives in `~/Monitoring_project/eeg-emg-analysis/`. Use
`~/eeg-analysis-venv/bin/python`, never the `/opt/neurosurveillance` venv.

## Why this exists

Every figure this project had produced was an **argument**: it lived inside a
dated experiment document and made one point. Not one of them answered the
question that actually gets asked about a new mouse, which is "is this animal, on
this day, any good". So checking an animal meant rebuilding the story by hand,
and the figures went stale the moment the animals changed. When the cohort was
replaced on 7 August, the entire nine-figure set became a description of animals
that no longer existed, with nothing to replace it.

Four more things were wrong underneath that:

1. **Panels of different rank sat side by side at equal visual weight.** A
   hypnogram is only meaningful if the connection test passed for that animal,
   and nothing on the page said so.
2. **Two codebases disagreed about the constants.** The epoch length was 4 s in
   one and 10 s in the other; the impedance pass mark was 2.0 MΩ in one and
   0.5 MΩ in the other; the rail voltage existed in four values. The
   usable-fraction loop existed in three copies and the filter chain in five.
3. **The hum and slope criteria are not comparable**, and nothing stopped anyone
   tabling one next to the other.
4. **No figure recorded which ANIMAL it was about.** Labels like "B1" are rig
   positions, and the B1 position held two different mice.

## The ladder

| Rung | Question | Verdicts | Decided by |
| --- | --- | --- | --- |
| **0 FILE** | Is the file physically sound? | PASS / FAIL | data samples equal timestamp samples, remainder 0 |
| **1 IDENTITY** | Which native channels are this animal's? | PASS / FAIL | layout derived from the file's own `sensors_by_port`, never assumed |
| **2 CONNECTION** | Is the electrode connected, judged against wire-free inputs in the SAME file? | PASS / FAIL / INSUFFICIENT | usable fraction and longest unbroken block against the in-file floor |
| **3 SCOREABILITY** | Can the sleep question even be asked? | PASS / FAIL / INSUFFICIENT | ≥15 min inside blocks ≥124 s, within-block `r@1min` > 0.30, wake 15 to 90% |
| **4 ARCHITECTURE** | What did the animal do? | **PROVISIONAL** | hypnogram, wake against NREM, ZT split, Otsu sensitivity |
| **5 EXPORT** | Can a human check us? | PASS / INSUFFICIENT | EDF, plain text, scorer README, kappa pack state |

> [!warning] The rule that makes the card work
> **A rung is not evaluated if the rung below it failed.** It reads BLOCKED and
> carries the reason, and NO PANEL IS DRAWN FOR IT. That is the whole point. A
> sleep architecture from an animal that failed the connection test is not a weak
> result, it is not a result.

> [!important] INSUFFICIENT is not FAIL
> **INSUFFICIENT means the question could not be asked.** An animal with eight
> minutes of usable data is not an animal that does not sleep. The two get a
> different colour, a different glyph and a different word, because they have
> been read as the same thing in this project before.

Verdicts are drawn as **glyph plus word plus colour**, so a card printed in
greyscale, or read by anyone with any colour vision, still says PASS or FAIL.
The status palette was checked with the `dataviz` skill's validator before use
and passes every all-pairs CVD check.

## The card

* **Identity bar** — animal id, sex, age in whole weeks at this recording, rig
  position, **tether arm**.
* **State line** — days post-surgery, days post-tether, body weight and which
  weighing it came from, duration, ZT span, criterion, QC epoch.
* **Life timeline** — the animal's whole history on an axis of **age in weeks,
  integer ticks**: arrival, surgery, tethering, every recording with this one
  highlighted, every intervention, sacrifice and sampling, with **body weight
  plotted on the same axis** wherever a weighing exists.
* **Verdict ladder** — six rungs, each with the deciding number and the threshold
  it was compared against.
* **Evidence panels** — drawn only for rungs that passed.
* **Footer** — provenance, and the animal's notes as footnotes.

**A missing field renders as "not recorded", never as blank.** Most of this
cohort's husbandry fields do read "not recorded", and the card will keep saying
so on every page until a husbandry sheet exists. That is deliberate.

## Adding a new mouse

1. Add the animal to the cohort manifest in
   `eeg-emg-analysis/cohorts/<cohort>.yaml`: identity, provenance, life events,
   and a dated `placements` entry giving its rig position and tether arm.
   Interventions and weighings are **lists of dated entries**, so a new
   experiment type never needs a schema change.
2. Or put it in a husbandry spreadsheet and join it:
   `cards/ladder.py ... --husbandry ~/mice.xlsx`. The sheet wins on any field it
   supplies, every value it supplies is stamped with the sheet's name, and the
   loader prints which columns it recognised and which it ignored.
3. Run the three commands at the top of this page.

**Impossible dates are refused, not drawn.** Arrival after surgery, a recording
before tethering, a body weight outside 5 to 80 g, or one rig position claimed by
two animals at once, all raise rather than producing a nonsense timeline.

## 🔴 Which floor the criteria are measured against (read this before the criteria)

Both criteria below compare a channel to "the 1st percentile of the wire-free floor". **Which
wire-free inputs go into that percentile is not a detail, and the code currently gets it wrong.**

`core/criteria.py::floor_stats()` **pools** all unwired inputs across all eight amplifier chips.
The `USABLE_FRACTION_DEFINITION` in that same file says the comparison is against inputs recorded
**"through the same chip"**. Measured on four recordings, the chips diverge every time — spreads of
0.74 to 1.54 in slope p1 — and the pooled value lands **too harsh for 7 of 8 chips and too lenient
for 1**, in all four.

On the 2026-08-19 run this is the whole answer, not a correction to it:

| position | usable EEG, per-chip | usable EEG, pooled | longest block per-chip | pooled |
|---|---|---|---|---|
| A1 | 99.9% | 41.5% | 457.5 min | 9.3 min |
| C1 | 97.7% | 21.6% | 211.2 min | 5.5 min |
| D2 | 98.5% | 29.4% | 86.2 min | 7.5 min |

**Under the pooled floor every position fails rung 2. Under a per-chip floor five pass.**

🔑 **The error has a direction.** Where pooled was harsher than a chip's own floor, a **FAIL is
suspect** and a **PASS is conservative and survives**. ⭐ **And it does not just inflate everything**
— re-running the 2026-08-08 EMG gate per-chip moves exactly one animal across the bar.

🛑 **`floor_stats()` is NOT fixed.** Until it is, compute the per-chip floor alongside it, as
`qc/score_2026-08-21/score.py` does. See [[2026-08-21-39h-run-score]].

## The two criteria, and why they must never be mixed

Both are computed on every run. You choose which is reported.

**SLOPE** is the safe one. The log-log spectral slope over 1 to 40 Hz, against
the 1st percentile of the wire-free floor. Real EEG is steep, an unwired input is
flat, and filtering cannot manufacture slope. The band carries no mains harmonic,
so it needs no notch.

**HUM** is 60 Hz amplitude against the same floor. It works only while connected
and open channels sit in two separated modes, which was true of this cohort by a
factor of about 100.

> [!danger] The hum criterion can be confidently wrong, and the code now refuses
> An animal recording with **no ground at all** scored 100.0% usable on hum and
> 0.0% on slope, on the same epochs, because a floating bipolar pair rejects
> mains as common mode and is therefore QUIET, and the hum criterion rewards
> quiet.
>
> The obvious guard, "check the floor is bimodal", DOES NOT WORK: the floor was
> loud in both cohorts. What changed was the animal side. So `core/criteria.py`
> tests the **disagreement between the two criteria** and refuses to return a hum
> number for any channel where hum calls ≥50% of epochs usable while slope calls
> ≤5%. The refusal is a hard error.

🛑 **Slope judges EEG, not EMG.** Real EMG and ECG are broadband and therefore
flat, so a slope test calls a working muscle channel dead. `usable()` raises if
you try it.

🛑 **A usable fraction at the 10 s QC epoch and one at the 4 s staging epoch are
different numbers.** So are a hum fraction and a slope fraction. The card records
which one it used, in the header and in the footer.

## What the card refuses to claim

* **Rung 4 is PROVISIONAL for every animal, permanently, until a blind-scoring
  Cohen kappa exists.** No human has scored any epoch of this project's data.
* **No REM percentage**, ever: the percentile rule and an independent Otsu cut
  disagree by roughly a factor of five on this montage.
* **The circadian agreement is not independent confirmation.** The card draws the
  ±25% Otsu sweep beside the number precisely so nobody can quote the number
  without the sweep.
* **Four of the five physiology checks restate the staging rule and cannot fail.**

## Files

| Path | What it is |
| --- | --- |
| `eeg-emg-analysis/core/qc_thresholds.py` | **THE** constants. Anything importing a threshold from anywhere else is a bug. |
| `eeg-emg-analysis/core/criteria.py` | **THE** connection criterion, floor derivation, filter chain. |
| `eeg-emg-analysis/cohorts/schema.py`, `load.py` | Animal identity, the husbandry join, date validation. |
| `eeg-emg-analysis/cards/ladder.py` | The verdict engine. No plotting, so verdicts are testable. |
| `eeg-emg-analysis/cards/render_card.py` | One A4 page per animal-recording. |
| `eeg-emg-analysis/cards/render_cohort_sheet.py` | One landscape page per cohort. |
| `eeg-emg-analysis/cards/export_text.py` | The TSV exports. |
| `eeg-emg-analysis/pipeline/` | Stages 1 to 4, moved here from this vault on 2026-08-09. |
| `eeg-emg-analysis/tests/` | The regression suite. |

## The regression test, and why it matters

Consolidating three copies of the criterion into one is only defensible if the
one reproduces what the three reported. It does, exactly:

```
~/eeg-analysis-venv/bin/python tests/test_criteria_regression.py
```

| check | consolidated engine | vault |
| --- | --- | --- |
| floor threshold | 415.02 µV | 415.0 µV |
| floor measurements | 953,904 | 953,904 |
| B1 both channels usable | 99.62% | 99.6% |
| B1 longest unbroken block | 215.80 min | 215.8 min |
| D2 both channels usable | 86.54% | 86.5% |
| D2 longest unbroken block | 87.30 min | 87.3 min |
| C1 EMG · A1 EMG · C2 EEG | 37.77 · 7.62 · 0.13% | 37.8 · 7.6 · 0.1% |
| wire-free floor controls | 0.00% | 0.00% |

**Any movement in that table is a bug, not an improvement.** Run it after
changing a constant.

## Related

* [[_eeg-analysis-hub]] — the analysis hub
* [[2026-08-07-rig-specification-and-analysis-method]] — the page to argue from
* [[eeg-artefact-and-railing-rejection-policy]] — epoch-level rejection
* [[blind-scoring-and-kappa]] — the pre-registered rules that gate rung 4
* [[figure-and-analysis-audit-2026-08-08]] — the audit these rules came from

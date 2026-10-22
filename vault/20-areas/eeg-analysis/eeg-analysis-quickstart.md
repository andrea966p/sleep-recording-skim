---
type: procedure
area: eeg-analysis
status: active
created: 2026-10-22
summary: "The four pipeline commands, the verdicts, the four rules and where outputs land, moved verbatim from the old analysis hub"
tags: [procedure, eeg, analysis, pipeline, onboarding, python]
---

# EEG analysis quickstart: raw recording to a scoreable file

> [!warning] Updated 2026-10-22: the commands below were moved verbatim from the old hub and their paths are stale.
> Checked read-only on e10 on 2026-10-22. The code is in `~/sleep-recording-skim/eeg-emg-analysis/`
> (`~/Monitoring_project` no longer exists). The stage scripts import `core`, so run from inside
> `pipeline/` they stop with `ModuleNotFoundError: No module named 'core'`. This form works
> (`--help` checked for all five scripts):
>
> ```bash
> cd ~/sleep-recording-skim/eeg-emg-analysis
> PYTHONPATH=. python3 pipeline/stage1_qc.py $REC --json qc.json
> PYTHONPATH=. python3 pipeline/stage2_split.py $REC
> PYTHONPATH=. python3 pipeline/stage3_features.py $DAY
> PYTHONPATH=. python3 pipeline/stage4_export_edf.py $DAY
> PYTHONPATH=. python3 pipeline/cohort_summary.py --out <dir> <day> [<day> ...]
> ```
>
> Rule 4's file is now `eeg-emg-analysis/core/qc_thresholds.py`; the archived `scripts/` folders are
> in `eeg-emg-analysis/archive/vault-scripts/`. The loader under `/home/skimlab/Desktop/andrea/` is
> not on e10. The pooled floor in the 2026-08-21 notice at the bottom was fixed on 2026-08-26 [[2026-08-26-per-chip-floor-fix]].
> Per-animal verdicts come from [[animal-card-and-verdict-ladder]] first.


> [!abstract] TL;DR — for non-technical readers
> **What this is.** The one entry point for everything that happens *after* a
> recording exists on disk. It takes you from the raw file Allego wrote to a
> file a person can score by hand, in four commands.
>
> **Why it exists.** There used to be three competing sets of instructions in
> this folder and two of them were wrong. This page is now the only one that
> describes what to actually run. Everything else here is either a deeper
> reference or an archive, and each is labelled as such at the bottom.
>
> **How to read this page.** Run *The four commands*. If something misbehaves,
> go to [[eeg-analysis-problems]]. If a word blocks you, go to
> [[eeg-analysis-glossary]]. Do not follow the archived pages unless you are
> reproducing a historical number.
>
> Big picture: [[nvr-system-overview]].
> Acquisition side, everything before the file exists:
> [[sleep-recording-operator-manual]].

---

## The map — four pages, and that is all

| I want to | Read |
| --- | --- |
| **run the analysis** | this page, then [[eeg-pipeline-manual]] for detail on each stage |
| **know why each step is done, and what a reviewer will ask** | [[analysis-methods-and-justification]] |
| **look up a term or parameter** (`nperseg`, `r@1min`, `DIRTY`, `ZT`) | [[eeg-analysis-glossary]] |
| **fix something that misbehaved** | [[eeg-analysis-problems]] |

---

## The mental model, in 30 seconds

```
Allego writes        <base>_data.xdat  +  _timestamp.xdat  +  .xdat.json
                     raw, wideband, 1000 Hz, microvolts, ALL 8 mice in one file
                                   |
  stage 1  QC        is each mouse scoreable at all?      -> verdict + reason
                                   |
  stage 2  split     one .npz per mouse, per day folder   -> 250 Hz, gated
                                   |
  stage 3  features  automatic hypnogram + sleep stats    -> SCOREABLE or not
                                   |
  stage 4  export    EDF+ for a HUMAN scorer              -> .edf + scorer note
```

Three facts that everything else follows from:

1. **The `.xdat` is the master. Never edit it.** Every output is re-derivable.
   All filtering happens offline, so nothing irreversible is ever baked in.
2. **One recording contains all 8 mice.** Splitting per mouse is stage 2's whole
   job, and which channel belongs to which mouse is *derived from the file's own
   metadata*, never assumed.
3. **Quality control comes first, not last.** Most of our recordings have no
   usable EEG, so asking "is this scoreable" before measuring anything is what
   stops us measuring noise.

---

## The four commands

Use the **system `python3`**, not the `/opt/neurosurveillance` virtual
environment. That one has a numpy and scipy version clash and fails with
`numpy.core.multiarray failed to import`.

```bash
cd ~/Monitoring_project/Monitoring_project_obsidian_vault/02-procedures/eeg-data-analysis/pipeline

REC=allego_1__uid0731-18-06-37          # the recording base name, no _data.xdat
DAY=/home/skimlab/eeg-processed/2026-07-31

# 1. is each mouse scoreable?           (one pass over the raw file, up to ~15 min)
python3 stage1_qc.py $REC --json qc.json

# 2. split into one file per mouse      (fast, reuses stage 1's cache)
python3 stage2_split.py $REC

# 3. automatic scoring + sleep features
python3 stage3_features.py $DAY

# 4. EDF+ export, so a person can score it by hand
python3 stage4_export_edf.py $DAY
```

Several recordings of the same animals together:

```bash
python3 cohort_summary.py --out /home/skimlab/eeg-processed/COHORT-2026-07 2026-07-31 2026-08-02
```

### What each command actually decides

| Stage | The question it answers | The output you read |
| --- | --- | --- |
| 1 | Is this mouse's electrode connected enough to score? | a **verdict** and a **reason** per mouse |
| 2 | Which samples belong to which mouse, and which are usable? | one `.npz` per mouse, `README.txt`, `qc_summary.csv` |
| 3 | When was it asleep, and is that believable? | `*_hypnogram.csv`, `*_summary.txt`, SCOREABLE or not |
| 4 | Can a human check our answer? | `*.edf` + `*_SCORER-README.txt` |

> [!important] Read the reason, not just the verdict
> Stage 1 prints why it decided what it decided. `DIRTY` and `OPEN` are very
> different situations and the word alone does not tell you which one you have.

### Useful flags

| Flag | Stage | Use it when |
| --- | --- | --- |
| `--force` | 1, 2 | you changed a threshold, or want to overwrite existing output |
| `--all-verdicts` | 2 | handing over a **complete** set of mice, failures included |
| `--clean-only` | 2 | almost never, see the warning below |
| `--json FILE` | 1 | you want the full QC output rather than the printed table |

---

## What the verdicts mean

| verdict | meaning | usable? |
| --- | --- | --- |
| `CLEAN` | ≥90% of epochs pass, most usable time in long blocks | yes |
| `DIRTY` | usable data exists, but fragmented or partly contaminated | **yes** |
| `OPEN` | electrode not electrically connected for >95% of the recording | no |
| `DEAD` | channel never carried EEG at all | no |
| `CLIPPED` | amplifier saturated for >95% of the recording | no |
| `INSUFFICIENT` | under 15 minutes of usable continuous data | no |

> [!warning] Two verdicts are routinely misread
> **`DIRTY` does not mean bad.** C1 on 2026-07-31 is the best animal in the
> project and it is `DIRTY`, because the surrounding 19 hours are open. Never
> default to `--clean-only`.
>
> **`INSUFFICIENT` is not a negative result.** It means the question could not
> be asked, not "this mouse did not sleep". Writing it up as a finding is a
> category error.

---

## The four rules you must not break

> [!danger] 1. The signals are already bipolar. Never subtract them.
> The RHD2216 chip subtracts each electrode pair internally, before the
> converter. `/1` is EEG (frontal minus parietal) and `/2` is EMG (left minus
> right neck), each **already a difference**. Do not subtract EMG from EEG and
> do not re-reference. The old `EEG = native0 − native1` rule computed
> EEG-minus-EMG, and it is why 24 working EMG implants were once recorded as
> failed surgeries. Canonical page: [[CANONICAL-allego-channel-selection]].

> [!danger] 2. Analyse inside blocks, never across them.
> A **block** is an unbroken run of passing epochs. Because contact is
> intermittent, two epochs that sit next to each other after the failing ones
> are dropped can be **hours apart in real time**. Anything with a time lag in
> it — autocorrelation, bout length, transition probability — must be computed
> inside one block and then averaged across blocks. Ignoring this produced this
> project's largest false positive, `r = +0.854` on 39 minutes of pure wake.

> [!danger] 3. Never report a REM percentage.
> REM is defined here as the top 20% of theta-over-delta among non-wake epochs,
> so its share is fixed by the rule rather than measured. The output field is
> deliberately named `rem_pct_CONSTRUCTED`. Report wake against non-REM, and
> report REM's **order**, that it is entered from non-REM rather than from wake.

> [!danger] 4. Every constant lives in one file.
> `pipeline/qc_thresholds.py`, each with its provenance written next to it.
> There are no magic numbers anywhere else in the pipeline. If you change one,
> re-run stage 1 with `--force`, or you will get the old verdicts back from
> cache and conclude the change did nothing.

---

## Where the outputs land

```
/home/skimlab/eeg-processed/2026-07-31/
├── portC-slot1_2026-07-31_180637_27h54m.npz      one mouse: eeg, emg, blocks, zt, meta
├── portC-slot1_..._hypnogram.csv                 automatic scoring, epoch by epoch
├── portC-slot1_..._features.json / _summary.txt  one number per mouse / plain English
├── portC-slot1_....edf                           for a human scorer
├── portC-slot1_..._SCORER-README.txt             which windows are worth scoring
├── impedance/                                    the sweeps for that day
├── qc/qc_summary.csv                             one row per animal
└── README.txt                                    verdicts + caveats, so they travel with the data
```

Filename is `port{PORT}-slot{SLOT}_{DATE}_{HHMMSS}_{DURATION}`. Slot is the
position on the splitter: slot 1 = `/1`,`/2`; slot 2 = `/33`,`/34`.

Opening an `.npz` in Python, and the meaning of every array inside it, is in
[[eeg-analysis-glossary]] section 5. There is a ready-made loader at
`/home/skimlab/Desktop/andrea/eeg-per-mouse/load_mouse.py`, with a companion
`HOW-TO-USE.md` written for a colleague receiving the data.

---

## Supporting pages in this folder

**Current:**
- [[eeg-pipeline-manual]] — the operating manual: every stage, every threshold, why
- [[analysis-methods-and-justification]] — standard versus ours, with citations.
  Read this before writing a methods section or presenting to the PI
- [[02-file-formats-reference]] — XDAT, CSV and EDF format specs, byte layouts, sizes
- [[01-environment-setup]] — the older dedicated analysis venv. Optional: the
  current pipeline needs only numpy and scipy, so system `python3` is enough

**Historical, do not follow:**
- [[03-scripts-and-usage]] — **superseded.** Describes the archived pre-sleep64
  scripts, which carry the wrong channel map
- [[04-processing-guidelines]] — the science behind the choices, still broadly
  correct, but its channel guidance is superseded by
  [[CANONICAL-allego-channel-selection]]
- `scripts/_archive_pre_sleep64/` — wrong channel map, wrong bipolar rule
- `scripts/contact-state-2026-07-31/` — contains `gate_and_score_all.py`, whose
  persistence statistic crossed contact gaps. Kept only to reproduce historical
  numbers
- `scripts/rescore-v2-2026-08-03/` — the corrected persistence statistic, since
  folded into `stage3_features.py`

> [!quote] Paper-ready
> Recordings were acquired wideband at 1 kilohertz and processed offline: each
> animal's channels were derived from the acquisition metadata, quality
> controlled per 4 second epoch, split into per-animal records, and scored into
> wake, non rapid eye movement and rapid eye movement sleep using delta power,
> the theta to delta ratio and electromyogram tone with per-animal thresholds.

## Related
- [[eeg-analysis-glossary]] — every term and parameter in plain words
- [[eeg-analysis-problems]] — symptom lookup for the analysis side
- [[CANONICAL-allego-channel-selection]] — which channel is which. If anything
  disagrees with that page, that page is right
- [[sleep-recording-operator-manual]] — the acquisition side
- [[eeg-emg-data-guide]] — reading EEG and EMG by eye, sleep stage signatures
- [[2026-08-03-data-quality-report-for-professor]] — what the analysis found

---

## Notices carried over from the old hub (2026-08-08 to 2026-08-21)

These sat at the top of the old hub. Moved verbatim.

> [!important] ⭐⭐⭐ 2026-08-09: THE CODE MOVED, AND THERE IS A NEW FIRST STEP
> **The pipeline no longer lives in this vault.** It is now at
> `~/Monitoring_project/eeg-emg-analysis/pipeline/`, next to the QC scripts, so that
> one file defines each constant. The two trees had disagreed on the epoch length,
> the impedance pass mark and the rail voltage. **Every constant is now in
> `eeg-emg-analysis/core/qc_thresholds.py` and nowhere else.**
>
> **Read [[animal-card-and-verdict-ladder]] first.** Checking an animal is now one
> command that produces one page: a six-rung verdict ladder saying how far up the
> chain of questions that animal got, and why it stopped there. Figures are
> filtered views of those cards, not separate scripts.
>
> The consolidation was proved by reproducing every published usable fraction
> exactly, including B1's 215.8 min block and the 415.0 µV floor threshold from
> 953,904 wire-free measurements. See the regression table on that page.

> [!note] Is this whole approach defensible? Checked against the literature 2026-08-21
> The in-file wire-free floor is a per-recording version of **shorted-input noise testing**, which is
> standard instrumentation practice; per-chip grouping is physically correct. **Using it as a live
> per-file criterion is non-standard, but the field handles the same question by eye.** The honest
> risk is not the method — it is that **the bottleneck here is hardware yield, and no hypnogram has
> ever been produced.** [[is-our-qc-approach-sound]]

> [!danger] 🔴🔴 2026-08-21: THE WIRE-FREE FLOOR IS POOLED ACROSS CHIPS, AND IT SHOULD NOT BE
> `core/criteria.py::floor_stats()` pools every unwired input across all **eight** amplifier chips
> into one threshold. The `USABLE_FRACTION_DEFINITION` string in that same file says the comparison
> is against inputs recorded **"through the same chip"**. The code and its own definition disagree,
> and the definition is right.
>
> **Measured on four recordings, the chips diverge every time**, and the pooled value came out
> **too harsh for 7 of 8 chips and too lenient for exactly 1** in all four:
>
> | recording | pooled p1 | per-chip range | spread |
> |---|---|---|---|
> | 2026-08-08 16.39 h | -1.328 | -1.540 .. -0.800 | 0.740 |
> | 2026-08-09 48 h control | -1.352 | -1.666 .. -0.840 | 0.826 |
> | 2026-08-18 1 h screen | -1.510 | -1.942 .. -0.407 | 1.535 |
> | 2026-08-19 39.7 h | -1.633 | -2.079 .. -0.676 | 1.403 |
>
> 🔑 **THE ERROR HAS A DIRECTION, SO READ OLD RESULTS ACCORDINGLY.** Where the pooled floor was
> harsher than a chip's own, a **FAIL is suspect** but a **PASS is conservative and survives**. Only
> the one chip per run that got a more lenient bar has suspect passes.
>
> ⭐ **It does NOT simply inflate everything.** Re-running the 2026-08-08 EMG gate per-chip moves
> exactly ONE animal across the bar (B2, -0.156 → -0.366). The 48 h control's passes are unchanged.
>
> 🛑 **`floor_stats()` IS NOT FIXED.** Scoring done on 2026-08-21 computes a per-chip floor alongside
> it. Fixing the library and re-checking what the pooled value affected is OPEN.
> Evidence and method: [[2026-08-21-39h-run-score]].

> [!danger] 🔴 2026-08-08: this hub no longer lists everything you need
> Three pages were added after this hub was written and they change how the pipeline must be read:
> - ⭐ [[2026-08-07-council-review-of-the-analysis-pipeline]] — **the review, the fixes applied, and
>   what may no longer be claimed.** Read before quoting any analysis number.
> - [[sleepyscore-japan-scoring-tool-algorithm]] — the reference tool's algorithm, read off its
>   source. **Their REM threshold is a 2-cluster split, not a percentile.**
> - [[per-animal-failure-signatures]] — telling apart the four failure modes hidden behind `OPEN`.
>
> The four commands below are still correct. The **interpretation** rules have changed.

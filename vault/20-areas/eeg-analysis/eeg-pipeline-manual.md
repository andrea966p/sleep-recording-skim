---
tags: [procedures, eeg, pipeline, scoring, qc]
created: 2026-08-03
status: active
---

# EEG analysis pipeline — raw recording to sleep features

> [!important] ⭐ 2026-08-09: THE CODE MOVED. This manual is still correct; the paths changed.
> The stage scripts now live in `~/sleep-recording-skim/eeg-emg-analysis/pipeline/`, and every
> constant lives in `eeg-emg-analysis/core/qc_thresholds.py` and nowhere else. Replace
> `cd ~/sleep-recording-skim/eeg-emg-analysis/pipeline` with `cd ~/sleep-recording-skim/eeg-emg-analysis/pipeline`
> in every command below. The old copies are archived verbatim at
> [[pipeline-moved-to-repo-readme|the pipeline archive]].
>
> **There is a new first step before these three commands:** [[animal-card-and-verdict-ladder]],
> which produces one page per animal-recording saying how far up the chain of questions that
> animal got, and why it stopped there.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The single path a recording takes from the raw file Allego
> writes to a per-mouse hypnogram. Three stages: decide whether a mouse's data
> is usable, split the recording into one file per mouse, then measure sleep.
>
> **Why it exists.** Before this, analysis was a pile of one-off scripts and
> two separate bugs survived in them for weeks. Every threshold now lives in
> one file with its justification attached, and every number a script prints
> can be traced back to a measurement or a paper.
>
> **How to read this page.** Run the three commands in *Quick start*. If a
> mouse is rejected, the reason is printed with the verdict — read the reason,
> not just the verdict.

Replaces the ad-hoc scripts in `scripts/`. Those remain only for reproducing
historical numbers. See [[2026-08-03-data-quality-report-for-professor]] for
the science; this page is the operating manual.

## Quick start

```bash
cd ~/sleep-recording-skim/eeg-emg-analysis/pipeline

# 1. is this mouse scoreable?
python3 stage1_qc.py allego_1__uid0731-18-06-37 --json qc.json

# 2. split into per-mouse files, organised by day, with impedance
python3 stage2_split.py allego_1__uid0731-18-06-37

# 3. sleep features for every mouse in that day folder
python3 stage3_features.py /home/skimlab/eeg-processed/2026-07-31

# 4. EDF+ export so a HUMAN can score it
python3 stage4_export_edf.py /home/skimlab/eeg-processed/2026-07-31
```

Stage 1 reads the raw file once (minutes to ~15 min) and caches per-epoch
features; stages 2 and 3 reuse the cache. Use system `python3`, **not** the
`/opt/neurosurveillance` venv — that venv has a numpy/scipy ABI mismatch and
fails with `numpy.core.multiarray failed to import`.

Environment overrides: `EEG_DATA_DIR`, `EEG_QC_CACHE`, `EEG_PROCESSED_ROOT`,
`EEG_IMPEDANCE_DIR`.

## Stage 1 — is the mouse scoreable?

`stage1_qc.py`. One sequential pass over the raw `.xdat`, computing per 4 s
epoch, per animal: EEG and EMG rms, 55–65 Hz mains amplitude, delta/theta/total
band power, and the fraction of railed samples.

### The gate — an epoch must pass all of these

| test | rule | what it catches |
| --- | --- | --- |
| OPEN | 55–65 Hz < **150 µV** on EEG *and* EMG | electrode not electrically connected |
| FLAT | EEG rms ≥ **11 µV** | momentary dropout |
| CLIPPED | **zero** railed samples (\|x\| ≥ 6376.8 µV) | amplifier saturation |
| FINITE | delta, theta, EMG rms all > 0 | degenerate epochs |

Plus one **channel-level** test applied before any of the above: median EEG rms
over the whole recording ≥ **20 µV**, else the channel is `DEAD` — it never
carried EEG at all, and no epoch-level test can rescue it.

### Verdicts

| verdict | meaning |
| --- | --- |
| `CLEAN` | ≥90% of epochs pass, ≥90% of usable time is in long blocks |
| `DIRTY` | usable data exists but fragmented or partly contaminated |
| `OPEN` | electrode open for >95% of the recording |
| `DEAD` | channel median rms below the floor; never carried EEG |
| `CLIPPED` | amplifier railed in >95% of epochs |
| `INSUFFICIENT` | <15 min inside blocks ≥124 s |

> [!warning] `INSUFFICIENT` is not a negative result
> It means the question could not be asked. Reporting it as "no sleep found"
> is a category error, and doing so is what made a chattering channel look
> like a scientific finding.

## Stage 2 — split, name, organise

`stage2_split.py`. Writes one file per mouse into a per-day folder. By default
both `CLEAN` and `DIRTY` animals are written — they differ in how much of the
recording is usable, not in whether any of it is. `--clean-only` narrows it.

> [!warning] Do not default to CLEAN-only
> C1 on 2026-07-31 is the best animal in the project — 8.73 h inside a single
> block whose median length is 4.4 h — and it is `DIRTY`, because the other
> 19 h of that recording is open. A `CLEAN`-only default silently drops it.
> `DIRTY` means "the recording is patchy", not "the data is bad".

```
/home/skimlab/eeg-processed/2026-07-31/
├── portC-slot1_2026-07-31_180637_27h54m.npz
├── portC-slot2_2026-07-31_180637_27h54m.npz
├── impedance/
│   ├── imp_8mice_corrected.csv          (copied verbatim)
│   └── impedance_summary.csv            (parsed: port, site, MΩ, phase, connected)
├── qc/
│   ├── qc_summary.csv                   (one row per animal, appendable)
│   └── qc_<recording>.json              (full stage 1 output)
└── README.txt                           (what is in this folder, verdicts, impedance)
```

**Filename** = `port{PORT}-slot{SLOT}_{DATE}_{HHMMSS}_{DURATION}.npz`, e.g.
`portC-slot1_2026-07-31_180637_27h54m.npz`. Slot is the position on a splitter
port: slot 1 = native offset 0 (`/1`,`/2`), slot 2 = offset 32 (`/33`,`/34`).

Each `.npz` contains `eeg`, `emg` (float32, µV, **250 Hz**), `epoch_ok`,
`blocks`, `zt`, `is_light`, and a `meta` JSON string.

> [!danger] The stored signals are already bipolar
> RHD2216 is a bipolar chip. `/1` is EEG and `/2` is EMG, each already a
> difference. **Do not subtract one from the other.** The old `EEG = n0 − n1`
> computed EEG-minus-EMG and is the reason 24 "failed EMG surgeries" were
> actually empty pads.

### Day folder date

Taken from the metadata UTC `start_time` converted to KST, not from the
filename. The `uidMMDD-HH-MM-SS` token is already local, so mixing the two puts
a recording in the wrong day folder. The source actually used is recorded as
`start_source` in the QC JSON.

### Impedance

Sweeps whose file date is within one day of the recording are copied in and
parsed. **Only `/1` and `/2` are read** — `/3` and `/4` are empty pads with no
wire, and including them is what produced the misleading early statistics.

## Stage 3 — sleep features

`stage3_features.py`. Per mouse:

- `*_hypnogram.csv` — epoch, t_s, ZT, light flag, state, EEG rms, delta, theta,
  theta/delta, EMG rms, in_block
- `*_features.json` and `*_summary.txt`

Staging: **WAKE** = high EMG (Otsu split of log EMG rms, *per animal*);
**NREM** = low EMG, low theta/delta; **REM** = low EMG, high theta/delta.

A mouse is **SCOREABLE** only if all four hold:

1. ≥15 min inside blocks ≥124 s
2. within-block `r@1min` > **0.30**
3. physiology passes — WAKE highest EMG; NREM most delta and largest
   amplitude; REM highest theta/delta with low EMG
4. wake fraction between 15% and 90%

Supporting evidence, not a gate: REM entered from NREM (expect >70%).

> [!danger] Never quote the REM percentage
> REM is defined as the top 20% of theta/delta among non-wake epochs, so its
> share is fixed by the rule, not measured. The field is deliberately named
> `rem_pct_CONSTRUCTED`. What *is* evidence is REM's **order** — that it is
> entered from NREM rather than from wake.

> [!danger] Persistence must be measured within unbroken blocks
> Computing autocorrelation across contact gaps pairs epochs that can be hours
> apart. That bug produced both the project's largest false positive (+0.854 on
> a stretch that is 39 min of pure wake) and a false negative (+0.078 on data
> that could not possibly have passed).
>
> Calibration of `r@1min` on synthetic data through this same code path:
> noise −0.035 | 30 s bouts +0.112 | 2 min +0.214 | 4 min +0.510 | 10 min +0.703.
> So `r > 0.30` means consolidated bouts of roughly **3 min or longer**.

## Stage 4 — EDF+ for the human scorer

`stage4_export_edf.py`. Writes a two-signal (EEG, EMG) **EDF+C** file per mouse,
plus a plain-language `_SCORER-README.txt` listing the windows worth scoring.

No third-party dependency — EDF is written directly. The archived
`xdat_to_edf.py` needed `pyedflib` **and** computed bipolar derivations, i.e. the
retracted pre-2026-08-01 model; do not resurrect it.

Physical range is pinned to the true ADC rail, **±6389.56 µV**, so the EDF
digital step equals the hardware LSB of 0.195 µV. Verified by round-trip:
maximum error **0.195 µV = exactly one LSB**, i.e. pure quantisation, no scaling
bug. (6389.56 rather than the exact 6389.565 because EDF header fields are 8
ASCII characters — `-6389.565` gets truncated while the positive field does not,
producing an asymmetric range and a fractional-LSB bias on every sample.)

> [!important] Three deliberate choices
> 1. **The automatic hypnogram is NOT written into the EDF.** A scorer who sees
>    our labels cannot un-see them. Score blind, then compare with
>    `*_hypnogram.csv`.
> 2. **Rejected epochs are left in place, not cut out.** Splicing discontinuous
>    time into a continuous file would destroy the scorer's sense of bout length
>    — the same class of error as the persistence bug.
> 3. **The scorer is told which windows to score**, with start/end times, so the
>    excluded stretches are not mistaken for flat physiology.

## Cohort packaging — several runs of the same animals, together

`cohort_summary.py`. The per-day folders are per *recording*; this builds one
view across a whole cohort.

```bash
python3 cohort_summary.py --out /home/skimlab/eeg-processed/COHORT-2026-07 \
    2026-07-31 2026-08-02
```

Produces:

```
COHORT-2026-07/
├── README.txt              per-animal-per-run table, what is scoreable, why the rest failed
├── cohort_animals.csv      one row per animal per run (QC + staging outcome)
├── cohort_impedance.csv    every sweep, per electrode, across all runs
└── to-score/               every EDF+, scorer note, hypnogram and summary in one place
```

The README carries the interpretation caveats with the data, so the numbers
cannot travel without them: the commissioning-test timeline, "signals are already
bipolar", "score only inside the listed windows", "do not report a REM
percentage".

## Thresholds and where they come from

All in `qc_thresholds.py`, each with its provenance. No magic numbers anywhere
else. Audited 2026-08-03 against 1,137,955 pooled epochs from 41
animal-recordings.

| constant | value | basis |
| --- | --- | --- |
| `RAIL_UV` | 6389.6 µV | `0.195 µV/LSB × 32767`. **Measured**: max\|sample\| is 6389.8 µV on all 8 channels — the 16-bit ADC full scale, a hardware ceiling |
| `OPEN_UV` | 150 µV | **Measured**: mains amplitude is bimodal in log space; connected mode 84 µV, open mode 3731 µV, valley at 134 µV |
| `FLAT_UV` | 11 µV | **Measured**: local minimum in the epoch rms distribution separating the amplifier noise floor from real signal |
| `DEAD_CHANNEL_UV` | 20 µV | channel-level median; a short is a channel property, not an epoch property |
| `CLIP_FRAC` | 0 | any railed sample makes band powers undefined. **Free**: results are identical for 0, 1e-3 and 1e-2 |
| `EPOCH_S` | 4 s | short end of the accepted rodent range; mouse NREM bouts are often <30 s |
| `NPERSEG` | 2048 | see the danger callout below |
| `R_THRESH` | 0.30 | calibrated against synthetic bouts through the identical code path |
| `IMP_CONNECTED_MOHM` | 2.0 | our open/closed separator (legs 5.2–8.7 MΩ open vs 5.233 MΩ no-wire control) |
| `IMP_GOOD_MOHM` | 0.10 | literature: epidural screws are 5–50 kΩ at 1 kHz, ≤10 kΩ confirms contact |

### What changed on 2026-08-03 and why

- **`OPEN_UV` 300 → 150.** 300 µV sat on the rising flank of the OPEN mode and
  was permissive. Verified by sensitivity sweep: tightening removes no
  scoreable animal.
- **The old single `SHORT_UV = 25 µV` split into `FLAT_UV = 11` (epoch) and
  `DEAD_CHANNEL_UV = 20` (channel).** This was the one constant whose exact
  value moved a verdict — at 13 µV an extra animal passed, at 40 µV C1's `r`
  fell from 0.74 to 0.43. Separating the channel-level question from the
  epoch-level question removes that sensitivity, because a dead *channel* is
  now caught by a statistic computed over the whole recording.
- **`RAIL` 6300 → 6376.8 µV** (99.8% of true full scale), now derived rather
  than guessed.

### Sensitivity — does the conclusion depend on the thresholds?

Swept every threshold across its plausible range (2026-08-03):

- **C1 is invariant.** `r = 0.74`, 8.7 h, in *every* variant tested.
- **C2 survives every variant** (`r` 0.31–0.72), though its usable duration
  moves between 1.3 and 4.2 h.
- Clipping is not load-bearing at all.

A conclusion that moved when a threshold moved would not be reportable. These
do not move.

> [!danger] `NPERSEG = 2048` — do not lower it
> `df = fs/nperseg = 0.49 Hz`. At `nperseg = 512`, `df = 1.95 Hz`, the 6–9 Hz
> theta band spans a single FFT bin, and `np.trapz` over one point returns
> **exactly zero** — silently destroying every REM measurement with no error.

## Light cycle

Lights **on 09:00**, **off 21:00 KST**, 12:12. **ZT0 = 09:00 KST.** Recorded in
`qc_thresholds.py` and stamped into every output. Stage 3 reports architecture
split by light and dark phase.

## Other gotchas

- **Otsu is per animal.** Never reuse one animal's EMG threshold on another —
  that is what wrongly passed D2 on 2026-08-01.
- **Animal names are positional.** `D2` in one recording is not necessarily the
  same animal as `D2` in another. Needs cage records to fix.
- **Layout is derived from `sensors_by_port`, never assumed.** Recordings exist
  at 32 ch/port, 64 ch/port and mixed (`A:64@0 B:32@64 C:64@96 D:64@160`).

---
tags: [procedure, eeg, analysis, hub, onboarding, python]
created: 2026-06-30
status: complete
---

# EEG Data Analysis — Hub

> [!danger] ⭐ SUPERSEDED AGAIN 2026-08-03 — go to [[pipeline/README]]
> The current analysis path is **`02-procedures/eeg-data-analysis/pipeline/`**,
> in this vault, and it replaces both the archived scripts below *and* the
> `eeg-emg-analysis/` codebase referenced in the next box.
>
> ```
> stage1_qc.py       raw .xdat -> CLEAN / DIRTY / OPEN / DEAD / CLIPPED / INSUFFICIENT
> stage2_split.py    -> /home/skimlab/eeg-processed/YYYY-MM-DD/ one file per mouse
> stage3_features.py -> hypnogram + sleep features
> qc_thresholds.py   every constant with its provenance
> ```
>
> Why it exists: two statistics bugs and three wrong QC thresholds survived in
> the older tooling for weeks. Everything is now in one place with the
> justification attached. **The science below (bands, filters, epoching) still
> holds** — it is the channel map, the thresholds and the persistence statistic
> that changed.
>
> Use the **system `python3`**, not the `/opt/neurosurveillance` venv (numpy/scipy
> ABI mismatch → `numpy.core.multiarray failed to import`).

> [!warning] Superseded 2026-07-18 — code moved out of the vault
> The runnable scripts here predate the **sleep64 8-headstage** rig and are
> **archived** under `scripts/_archive_pre_sleep64/`. The current, clean codebase
> lives in its own project folder: **`Monitoring_project/eeg-emg-analysis/`**
> (QC / convert / sleep, with the 8-mouse channel map derived-and-validated from
> metadata). Start at its `README.md`. Rationale + fact-check citations:
> `07-decisions/2026-07-18-eeg-emg-analysis-checkpoint.md`. The science below
> (bands, filters, referencing in `04-processing-guidelines`) still holds.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The start-here page for everything *after* a recording is made: where the files are, how to read them, how to filter/score-prep the EEG, and the Python scripts you run yourself. The acquisition side (plugging the mouse, Allego, grounding) lives elsewhere — this section begins the moment an XDAT recording exists on disk.
> **Why it exists.** The raw recording (`.xdat`) is not directly readable by eye or by most tools. You need a small, repeatable toolkit to turn it into clean EEG, summary features, and portable formats (CSV, EDF). This section is that toolkit, with every script already tested on a real recording.
> **How to read this page.** Do [[01-environment-setup]] once. Then the workflow below, top to bottom. Each script has a one-line command. Scoring-tool export (`.3eg`) is deliberately out of scope here.

The rig + acquisition side: [[sleep-recording-operator-manual]], [[signal-mapping-guide]], [[grounding-reference-noise-concepts]].

---

## The 30-second mental model

```
Allego  ->  <base>_data.xdat (+ _timestamp.xdat + .xdat.json)   = the MASTER (raw, 1 kHz, uV)
                                  |
                                  |  Python (analysis venv)
                                  v
        +----------------+----------------+------------------+
        | qc_report.py   | eeg_pipeline.py| xdat_to_edf.py   |
        | (is it good?)  | (features)     | xdat_to_csv.py   |
        +----------------+----------------+------------------+
        overview PNG      _features.csv     .edf / .csv  (share with others)
```

- The **XDAT is the master**. Never edit it. Everything is derived from it; you can always re-derive.
- All processing is **offline in Python**. Allego only acquires — it cannot re-process a saved file.
- Values are **microvolts (uV)** already (float32). No gain math needed.

---

## Workflow (in order)

| Step | Do | Script / doc | Output |
|---|---|---|---|
| 0 | Set up the venv (once) | [[01-environment-setup]] | `/home/skimlab/eeg-analysis-venv` |
| 1 | Know your file set | [[02-file-formats-reference]] | — |
| 2 | **QC** — is the recording good? | `qc_report.py` | `_qc_overview.png` + table |
| 3 | **Process** — clean + features | `eeg_pipeline.py` | `_features.csv` |
| 4 | **Export** — portable formats | `xdat_to_edf.py`, `xdat_to_csv.py` | `.edf`, `.csv` |
| — | Science guidelines (bands, filters, referencing) | [[04-processing-guidelines]] | — |
| — | Every script's options + examples | [[03-scripts-and-usage]] | — |

One-liners (analysis venv; scripts live in `02-procedures/eeg-data-analysis/scripts/`):

```bash
PY=/home/skimlab/eeg-analysis-venv/bin/python
cd ~/Monitoring_project/.../02-procedures/eeg-data-analysis/scripts   # for imports
REC=/home/skimlab/radix/data/allego_1__uid0629-12-05-09               # base, no _data.xdat

$PY qc_report.py    $REC                 # signal quality + overview plot
$PY eeg_pipeline.py $REC                 # filter -> 256 Hz -> 4s epochs -> band power
$PY xdat_to_edf.py  $REC                 # -> <base>.edf  (for EDFbrowser / EEG tools)
$PY xdat_to_csv.py  $REC --target-fs 256 --bipolar   # -> <base>_256hz.csv
```

---

## Channel guidelines (single-mouse config)

`D/n` (Allego UI) = native + 1. With the passthrough map, **native index = C3410 pad**.

| native | label | what it is | use |
|---|---|---|---|
| 0 | EEG_F_L | left frontal EEG (+) | **EEG = bipolar 0 − 1** |
| 1 | EEG_P_L | left parietal EEG (−) | (the pair) |
| 2 | EMG_L | neck EMG (+) | **EMG = bipolar 2 − 3** |
| 3 | EMG_R | neck EMG (−) | (the pair) |
| 4 | dura_FR | right-frontal dura | spare / re-reference |
| 6 | copper | cut cable shield | environmental-noise ref (NOT brain) |
| 5 | — | purple = nothing | DESELECT, never record |
| 7–31 | — | unwired | ignore |

- **The sleep EEG is the bipolar derivation `EEG_bip = native0 − native1`** (left frontal–parietal). Raw singles are kept too, but you score on the bipolar.
- The 2-mice-per-headstage map (`2mice32`) is also supported by every script via `--config 2mice32` (M1 = natives 0–3, M2 = natives 8–11). See [[signal-mapping-guide]].
- These maps are defined once in `scripts/xdat_io.py` (`CHANNEL_MAPS`) — edit there if the rig changes, and every script follows.

> [!warning] Allego saves ALL 32 primary channels, not just your 6 wired pads
> The XDAT always contains 32 `pri` channels (+ aux/din/dout = 38 total). The unwired ones are noise/float — the channel map tells the scripts which natives are real. Don't be alarmed by 32 channels in the file.

---

## Section contents
- [[01-environment-setup]] — the one analysis venv (numpy/scipy/matplotlib/pandas/pyedflib)
- [[02-file-formats-reference]] — XDAT (master), CSV, EDF; sizes; what opens what
- [[03-scripts-and-usage]] — all 5 scripts: purpose, options, tested example output
- [[04-processing-guidelines]] — bands, filters, referencing, decimation, artifacts, QC pass criteria

## Related
- [[eeg-emg-data-guide]] — earlier reference on reading EEG/EMG by eye + sleep-stage signatures
- [[sleep-recording-operator-manual]] — the acquisition side (everything before the XDAT exists)
- [[2026-06-29]] / [[2026-06-30]] — the first recording + first run of this toolkit

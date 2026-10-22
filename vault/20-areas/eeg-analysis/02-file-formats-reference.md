---
type: reference
area: eeg-analysis
status: active
status-note: "complete"
tags: [procedure, eeg, analysis, file-formats, xdat, edf, csv, onboarding]
created: 2026-06-30
---

# 02 — File Formats Reference

> [!abstract] TL;DR
> The recording is an **XDAT** 3-file set (the master, raw, microvolts). From it you make **CSV** (spreadsheet/Python) and **EDF** (EEG viewers / sleep tools). This page is the format spec + what-opens-what + size math. Hub: [[_eeg-analysis-hub]].

## XDAT — the master (NeuroNexus Allego native)

A recording is **three files sharing one base name** in `/home/skimlab/radix/data/`:

| File | Type | Contents |
|---|---|---|
| `<base>_data.xdat` | float32 LE | the signal, **already in uV**, interleaved **sample-major**: `[s0c0 s0c1 … s0cN][s1c0 …]` |
| `<base>_timestamp.xdat` | int64 LE | sample indices (0 … N−1) |
| `<base>.xdat.json` | JSON | metadata under `["status"]` |

Key metadata (`status`):
- `samp_freq` — acquisition rate (Hz). Ours = **1000**.
- `num_smpl` — samples per channel (N).
- `signals.total / .pri / .aux / .din / .dout` — channel counts. Ours = `38 / 32 / 2 / 2 / 2`.
- `start_time` — ISO wall-clock start (UTC, e.g. `2026-06-29T03:05:09.256Z` = 12:05:09 KST).

Channel order within each sample = `[32 pri][2 aux][2 din][2 dout]`. With a passthrough map, **pri index = C3410 pad = native index**.

Read it with `scripts/xdat_io.py` (numpy only):
```python
from xdat_io import load_xdat
rec = load_xdat("/home/skimlab/radix/data/allego_1__uid0629-12-05-09")
rec.data        # (38, N) float32, channel-first, uV
rec.fs, rec.n_samples, rec.start_time
```

> [!important] The XDAT is the source of truth
> Always keep it. CSV/EDF are derived and lossy-ish (CSV rounds, EDF quantises to int16). If anything looks wrong downstream, re-derive from the XDAT.

## CSV — for spreadsheets / pandas

Made by `xdat_to_csv.py`. Columns = `time_s` + one per channel (uV), optional bipolar.

> [!warning] Row-count limit
> A multi-hour 1 kHz recording is **millions of rows** and **will not open in Excel/LibreOffice** (1,048,576-row cap). Even decimated to 256 Hz, 4.5 h ≈ 4.2 M rows — still over the cap. For full recordings, **open CSV in Python/pandas**. CSV-in-Excel only works for short clips or heavily decimated data.

## EDF / EDF+ — for EEG viewers and sleep tools

Made by `xdat_to_edf.py` (via `pyedflib`). Stores int16 with per-channel physical range in uV. Includes the raw wired channels **and** the bipolar derivations (e.g. `EEG_bip`).

- Open in **EDFbrowser** — use the **2.14+** build. The Ubuntu-24.04 apt build (2.06) **crashes on launch** (`buffer overflow detected`); install `~/Downloads/edfbrowser-2.14-1.amd64-ubuntu-26.04.deb` instead.
- EDF pads the final data record to a whole second (a few zero samples at the very end) — harmless.

## Size math (per channel)

`bytes/channel = num_smpl × bytes_per_sample`, `num_smpl = fs × seconds`.

| rate | 1 hour | 3 days |
|---|---|---|
| 1000 Hz float32 (XDAT) | 14.4 MB/ch | 1.04 GB/ch |
| 625 Hz float32 | 9.0 MB/ch | 648 MB/ch |
| int16 (EDF/.3eg) | half the above | half |

Multiply by channel count. Remember Allego saves **all 32 pri** per headstage, so a single mouse still writes 32 ch unless you trim. Full storage planning: [[2026-06-29]].

## What opens what — quick table

| File | Open with |
|---|---|
| `.xdat` (master) | Python `xdat_io.py`; NeuroNexus Videre |
| `.csv` (full) | Python/pandas only (too big for Excel) |
| `.csv` (short/decimated) | LibreOffice / Excel / pandas |
| `.edf` | EDFbrowser 2.14+, MNE, pyedflib, most sleep tools |
| `_features.csv` | LibreOffice / Excel / pandas (small) |
| `_qc_overview.png` | any image viewer (`xdg-open`) |

## Related
- [[_eeg-analysis-hub]] · [[03-scripts-and-usage]] · [[04-processing-guidelines]]

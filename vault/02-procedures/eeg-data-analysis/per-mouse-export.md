---
tags: [procedure, eeg, export, matlab, analysis]
created: 2026-08-22
status: active
---

# Splitting a recording into one folder per mouse

> [!abstract] TL;DR
> `export/export_per_mouse.py` turns one `.xdat` recording into a folder per rig position, each
> holding the **full-rate raw signals as MATLAB and as text**, that position's **hypnogram**, and a
> plain-language **`_VERDICT.txt`** saying whether the hypnogram may be used.
> **Deliberately not EDF.**

## Run it

```bash
cd ~/Monitoring_project/eeg-emg-analysis
```
```bash
PYTHONPATH=. /usr/bin/python3 pipeline/stage1_qc.py <base> --json /tmp/qc.json
```
```bash
PYTHONPATH=. /usr/bin/python3 pipeline/stage2_split.py <base> --root ~/eeg-processed/ --all-verdicts
```
```bash
PYTHONPATH=. /usr/bin/python3 pipeline/stage3_features.py ~/eeg-processed/<YYYY-MM-DD>/
```
```bash
PYTHONPATH=. setsid nohup /usr/bin/python3 export/export_per_mouse.py <base> \
  --out ~/eeg-processed/per-mouse --hypno-dir ~/eeg-processed/<YYYY-MM-DD> &
```

`--all-verdicts` on stage 2 matters: without it, positions whose QC verdict is OPEN are skipped and
never get a folder. Use it whenever you want every position exported, not just the clean ones.

> [!warning] Use `setsid`, not bare `nohup`
> The export takes about 11 minutes per position — roughly 90 minutes for eight. `nohup` protects
> against SIGHUP but **not** against a SIGTERM sent to the process group, so if the launching shell
> is killed the export dies with it, leaving a **0-byte `.mat`**. That happened on 2026-08-21.
> `setsid` puts it in its own session and it survives.

## What you get

```
<recording>/
  README.md   manifest.json
  <POS>/
    <POS>_raw_1000Hz.mat     1.1 GB   full rate, MATLAB v5
    <POS>_raw_1000Hz.txt     3.1-3.5 GB   OPT IN, pass --txt
    <POS>_hypnogram_4s.csv   35,706 epochs
    <POS>_summary.txt        staging verdict and its caveats
    <POS>_features.json      per-position feature summary
    <POS>_info.json          provenance
    _VERDICT.txt             one line: is this usable, and why not
```

About **1.1 GB per position**, so ~9 GB for eight. With `--txt` it is 4.4 GB and
~35 GB, which is why the text file is no longer written by default.

> [!warning] The .txt is a LOSSY copy of the .mat, at three times the size
> It rounds to two decimals: 61.815 µV is written `61.81`. The `.mat` beside it
> holds the same signal at full float32 precision in a third of the space. Pass
> `--txt` only for a tool that genuinely cannot read MATLAB v5.
>
> Written unconditionally until 2026-09-23, which had put **27.6 GB** of rounded
> text on the rig for a single recording. Those files were deleted after checking
> that all eight `.mat` files load, agree on sample count, and match the text
> values. `--skip-text` is still accepted and ignored, so old callers do not
> break — they simply get the new default.

## Loading in MATLAB

```matlab
S = load('A1/A1_raw_1000Hz.mat');
t = (0:numel(S.eeg)-1)'/double(S.fs);
plot(t, S.eeg);
```

> [!note] The time vector is deliberately NOT stored in the .mat
> At 1000 Hz over ~40 h a float64 time column adds **1.14 GB** and pushes the file past MATLAB v5's
> **2 GB limit**. `h5py` is not installed here, so v7.3 is not available. The one line above
> rebuilds it exactly. The **text** file does carry timestamps.

⚠️ At 142.8 million rows MATLAB's `readmatrix` on the text file is slow and memory-hungry.
**Prefer the `.mat` unless you specifically need text.** The hypnogram CSV is small and loads fine
with `readtable`.

## Units and polarity

Microvolts. The signals are **already the bipolar difference** the RHD2216 produces.
🛑 **Never subtract EEG from EMG, or one channel from another.**

## Verify before trusting an export

The exporter does not check itself. After a run, confirm the folders hold the right channels:

- sample count per position equals the recording's `n_data_samples`
- channels sampled across the file are byte-identical to the source `.xdat`
- the text's first and last rows match the `.mat`
- the text has exactly **one line per sample plus a header**

All four were confirmed for `allego_1__uid0819-17-25-20` on 2026-08-21. The check is worth repeating
because a silent partial write looks exactly like a good one in a directory listing.

## Interpreting `_VERDICT.txt`

| verdict | meaning |
|---|---|
| SCOREABLE | hypnogram is usable |
| REJECT | hypnogram exists and **must not** be read as sleep architecture — check `r@1min` |
| NO STATES | EMG open, staging impossible; **EEG columns are still valid** |
| ANIMAL GONE | position vacated; raw kept for completeness |

🔑 **`r@1min` is the number that decides it.** It is how strongly a state predicts the next minute.
Good animals sit at **0.45-0.59** against a shuffled null near 0.00; the pipeline rejects below
**0.30**. A hypnogram with `r@1min` near zero is randomly-relabelled data with state names on it.

Related: [[animal-card-and-verdict-ladder]] ·
[[eeg-analysis-problems]] ·
[[2026-08-21-39h-run-score]]

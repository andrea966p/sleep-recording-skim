---
tags: [procedure, eeg, analysis, python, scripts, onboarding]
created: 2026-06-30
status: complete
---

# 03 — Scripts and Usage

> [!danger] SUPERSEDED TWICE — do not follow this page
> These scripts are **archived** (`scripts/_archive_pre_sleep64/`). They predate
> the sleep64 8-headstage rig, they carry the **wrong channel map**, and their
> bipolar rule computes EEG-minus-EMG. The replacement named here in July,
> `Monitoring_project/eeg-emg-analysis/`, is **also superseded**.
>
> **The current path is [[_eeg-analysis-hub]] → `pipeline/`.** Everything below
> is kept only to reproduce historical numbers.

> [!abstract] TL;DR
> Five Python scripts in `02-procedures/eeg-data-analysis/scripts/`. Run them with the analysis venv ([[01-environment-setup]]), from the scripts folder (so `import xdat_io` works). Every example below was run on the real 4.5 h recording `allego_1__uid0629-12-05-09`. Hub: [[_eeg-analysis-hub]].

```bash
PY=/home/skimlab/eeg-analysis-venv/bin/python
cd ~/Monitoring_project/Monitoring_project_obsidian_vault/02-procedures/eeg-data-analysis/scripts
REC=/home/skimlab/radix/data/allego_1__uid0629-12-05-09     # base path, NO _data.xdat
```

All scripts take the **recording base path** (path without the `_data.xdat` suffix) and a `--config` (`single_mouse` default, or `2mice32`).

---

## `xdat_io.py` — the shared reader (library + quick dump)

The core module every other script imports. Defines `load_xdat()`, the `CHANNEL_MAPS`, `bipolar()`. Numpy-only, so it never breaks on a scipy/matplotlib issue.

Run it directly for a quick channel dump:
```bash
$PY xdat_io.py $REC
```
```
fs=1000 Hz  samples=16370816 (272.8 min)
total signals=38  pri=32  start=2026-06-29T03:05:09.256Z
wired channel RMS (uV):
  EEG_F_L_n0     RMS=    95.0  pkpk=   5184.3
  EEG_P_L_n1     RMS=   109.6  pkpk=  12595.4
  EMG_L_n2       RMS=  4693.7  ...
  EEG_bip        RMS=   147.2  ...
```
Edit `CHANNEL_MAPS` / `BIPOLAR_DERIVATIONS` here if the rig wiring changes — all scripts follow.

---

## `qc_report.py` — is the recording good?

Per-channel table (RMS, pk-pk, % of samples at the ±6.4 mV amplifier rail) + a 3-panel overview PNG (delta power / theta-delta ratio / EEG RMS over the whole recording).

```bash
$PY qc_report.py $REC            # --config 2mice32 / --epoch 4
```
```
channel           RMS_uV   pkpk_uV  %@rail  read
  EEG_F_L_n0        95.0    5184.3     0.0  clean EEG
  EEG_P_L_n1       109.6   12595.4     0.0  clean EEG
  EMG_L_n2        4693.7   12451.7     4.2
  ...
wrote ..._qc_overview.png
```
Read it: EEG channels should be **tens-to-low-hundreds uV, ~0 % @rail**. A channel pinned at the rail (high %@rail) = **open electrode or floating animal** (see [[04-processing-guidelines]] QC criteria).

---

## `eeg_pipeline.py` — clean + per-epoch features

Bipolar → bandpass (EEG 0.5–30, EMG 10–300) → 60 Hz notch → decimate (default 256 Hz) → epoch (default 4 s) → band power (Welch) + EMG RMS + artifact flag. Writes `<base>_features.csv`.

```bash
$PY eeg_pipeline.py $REC                       # defaults
$PY eeg_pipeline.py $REC --epoch 8 --target-fs 128
```
```
loaded 16370816 samples @ 1000 Hz (272.8 min)
decimated to 256 Hz
epochs=4092 (4.0s)  artifact=12 (0.3%)
EEG RMS (clean): median=87.6 uV
theta/delta: median=0.54  range 0.01..11.12
wrote ..._features.csv  (4092 rows)
```
`_features.csv` columns: `epoch, t_s, delta, theta, sigma, total, theta_delta, eeg_rms_uv, emg_rms_uv, artifact`. This is the table you'd feed a hypnogram/scoring step (out of scope here).

---

## `xdat_to_edf.py` — export to EDF+

Wired raw channels + bipolar derivations → `<base>.edf` (int16, integer uV scaling).

```bash
$PY xdat_to_edf.py $REC
```
```
wrote ..._.edf  8 signals @ 1000 Hz  size=0.264 GB
channels: ['EEG_F_L_n0','EEG_P_L_n1','EMG_L_n2','EMG_R_n3','dura_FR_n4','copper_n6','EEG_bip','EMG_bip']
```
Open in EDFbrowser 2.14+ (the apt 2.06 build crashes — see [[02-file-formats-reference]]).

---

## `xdat_to_csv.py` — export to CSV

Wired channels (optionally + bipolar) → CSV. Optional decimation.

```bash
$PY xdat_to_csv.py $REC                         # full 1 kHz raw -> _raw.csv (~0.9 GB)
$PY xdat_to_csv.py $REC --target-fs 256 --bipolar   # -> _256hz.csv
```
```
wrote ..._256hz.csv  rows=4190929  cols=[time_s, EEG_F_L_n0, ... EEG_bip, EMG_bip]  size=0.288 GB  fs=256
NOTE: too many rows for Excel/LibreOffice -> open in pandas, or re-run with --target-fs 256
```
Reminder: full recordings exceed Excel's 1.05 M-row cap even at 256 Hz — **open in pandas**.

---

## Adding a new analysis

Import the reader and go:
```python
import sys; sys.path.insert(0, "<scripts dir>")
from xdat_io import load_xdat, bipolar
rec = load_xdat(REC)
eeg = bipolar(rec.data, 0, 1)            # uV, 1 kHz
# ... your scipy code ...
```

## Related
- [[_eeg-analysis-hub]] · [[01-environment-setup]] · [[02-file-formats-reference]] · [[04-processing-guidelines]]

---
tags: [procedure, eeg, data-format, nas, canonical]
created: 2026-09-29
status: active
---

# Per-mouse CSV: the format the analysis reads

> [!abstract] TL;DR
> Every recording started from the console ends up on the SKIM NAS as **one CSV per mouse**, with
> the recording's own timestamps in the same file:
>
>     02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSEID>_<B|R>/
>         <YYYYMMDD>_<MOUSEID>_<B|R>.csv
>         <YYYYMMDD>_<MOUSEID>_<B|R>.info.json
>
>     02_Data_Sleep/andrea/HLBSSL/Recovery/20260921_HLBSSL31_R/20260921_HLBSSL31_R.csv
>
> The analysis reads the CSV. The xdat is not used for analysis. The stripped xdat stays on e10,
> and the raw 262-channel file goes off-site to S3 and the bilab NAS
> ([[02-procedures/backup-architecture]]).

## The CSV

Comma-separated, one header row, 1000 Hz, one row per sample.

    timestamp_raw,timestamp_sec,datetime_kst,EEG,EMG
    57403264,0.000,2026-09-10 08:59:59.012,12.410,-3.020
    57403265,0.001,2026-09-10 08:59:59.013,11.870,-2.950

| column | what it is |
|---|---|
| `timestamp_raw` | int64 from `<base>_timestamp.xdat`, copied **verbatim**. This is Allego's device sample counter. It is **not zero-based**, because it counts from when the Allego server session started, not from this recording |
| `timestamp_sec` | `(timestamp_raw − first row's) / 1000`. It is 0.000 at the first row of the CSV (the window start, if trimmed). A gap in the counter shows up as a jump here and is **not hidden** |
| `datetime_kst` | `status.start_time` (UTC, ms) + (`timestamp_raw` − the file's first) / 1000, shown in KST. Absolute, so it stays right in a trimmed CSV. Allego writes `start_time` when recording begins, so the absolute time is good to **about a second**, not to a sample |
| `EEG`, `EMG` | µV, 3 decimals. One column per role in the layout, upper-cased, so `ECG` appears only for a layout that has it |

The column names follow the lab's reference MATLAB export
(`03_Data_Mouse/diane/20260816_H5A251F0209_A01__BSR.mat`, v7.3). It holds `timestamp_raw` (int64),
`timestamp_sec` (double, 0-based), `EEG`/`EMG`/`ECG` (single, µV), `samplingRate` 1000,
`startTime` as an ISO UTC string, and `mouseID` and `port`. It was read with h5py on 2026-09-29. The
CSV uses the same names so code written against the .mat carries over.

**Size.** About 55 bytes per row, so **~4.8 GB per mouse per 24 h**. A 36.7 h eight-mouse run is
about 58 GB of CSV.

## Analysis windows (the rebuilt canonical set)

The eight canonical recordings are cut to a window before export, set by Andrea 2026-09-29:

| | window | length |
|---|---|---|
| baseline, every batch | 09:00 → 09:00 next day | 24 h |
| recovery, ad libitum (W-SL, S-SL) | 09:00 → 09:00 next day | 24 h |
| recovery, sleep deprivation (W-SD, S-SD) | 13:00 → 09:00 next day | 20 h: both runs stopped at 09:05 |

A mouse folder is dated by its window's start. The W-SD baseline file began 08-19 17:25, so its
folders read `20260820_…_B`. Where a recording does not cover its whole window, the shortfall in
seconds is in `info.json` → `window`:

| recording | missing |
|---|---|
| S-SD recovery | 27 s at the start (the run began 13:00:27) |
| W-SL recovery | 9 s at the start |
| S-SL baseline | 47 s at the end (the run stopped 08:59:13) |

Live runs from the console export the whole recording. The window is set by the scheduled start
and stop.

## Pairing

What the analysis needs is the **same mice** in a batch's baseline and recovery. Each `info.json`
has `pairing`: `paired: true` with the partner folder, or `paired: false` with the reason. S-SD
position B1 is the one exception. HLBSSD13 has a baseline only: it was taken off the rig on 08-26
with a chewed tether. HLBSSD17, its replacement, has a recovery only. Both are on the NAS, and
neither can be compared within the animal. **S-SD is n = 7 paired; W-SD, W-SL and S-SL are n = 8.**

The S-SD rig positions come from the Registry only. They were checked on 2026-09-29 against the one
independent observation, the tether that failed on 08-27, which Andrea confirmed was C1. That
matches the damaged-EMG-conductor signature in C1's data, so the Registry map stands.

## The info.json

It is written **last**, and only after its CSV has verified on the NAS. If a folder has an
info.json, the folder is complete. It records:

- **the animal:** `mouseID`, `batch`, `condition`, `recording_type`, rig `position` (A1…D2) and
  `port`;
- **the channels:** which site label is which column (`{"eeg": "A/1", "emg": "A/2"}`);
- **the recording:** `samplingRate`, `startTime_utc`/`startTime_kst`, `n_samples`, `duration_h`,
  and the first and last `timestamp_raw`;
- **provenance:** `allego_base` (the join key to the raw file), the stripped `dataset_checksum`,
  the raw source hashes, the run id, and the exporter's git commit;
- **upload:** the CSV's sha256 at both ends and the read-back rate. A read-back of about 90 MB/s
  means the bytes really crossed the network; see [[02-procedures/installation/skim-nas-smb-and-upload]].
- **suffix_reason**, only when the folder has a `-2`: a folder for that mouse and date already
  held a different recording.

## The QC verdict inside info.json (added 2026-09-30)

The CSV contains EEG and EMG only. The **wire-free control inputs** that every channel is judged
against stayed in the 262-channel raw file, so the CSV alone cannot be QC'd. Each `info.json`
therefore carries `qc`, copied from the animal card and never recomputed:

| key | meaning |
|---|---|
| `qc.verdict` | `SCOREABLE` · `NOT SCOREABLE` (a rung failed) · `NO VERDICT` (the chip's wire-free control was unusable, **not** a failure of the animal) · `NOT ASSESSED` |
| `qc.why` | one sentence: the rung that decided it, and its headline |
| `qc.connection` | EEG-and-EMG-in-the-same-epoch %, longest unbroken block, EEG % and EMG % |
| `qc.floor` | that chip's wire-free inputs: grounded?, 60 Hz hum, slope threshold, valid?, and the problem if not |
| `qc.sleep_structure` | rung 3: r@1min, hours in blocks, wake % |
| `qc.stage3` | only when the ladder could not reach rung 3: stage 3's own staging result |
| `qc.card` | path to the card, thresholds hash, git rev, and **which hours were judged** |
| `pairing.scoreable_at_both` | this mouse AND its partner timepoint are SCOREABLE |
| `pairing.scoreable_at_both_incl_stage3` | the same, counting a NO VERDICT whose stage 3 is SCOREABLE |

- **The rebuilt 64:** `qc` comes from the **windowed** cards (`cards/out-windows/`), so it
  describes exactly the hours in the CSV. They were updated by
  `eeg-recorder/deploy/add_qc_to_nas_info.py`. The originals are backed up in
  `~/radix/per-mouse/info-json-backup-2026-09-30/`.
- **Live runs:** `qc` comes from the card the console's QC step writes for the whole recording
  (`judged_on: "whole recording"`).

Quick list of what's scoreable at both timepoints:

```bash
grep -l '"scoreable_at_both": true' /mnt/skimnas/02_Data_Sleep/andrea/*/*/*/*.info.json
```

## How a CSV is checked before it leaves e10

`eeg-emg-analysis/export/per_mouse_csv.py` refuses rather than guesses:

- It reads the **stripped** file, whose sidecar says which label is which column. A label that is
  missing or appears twice is refused, because a wrong-channel CSV is the one failure nobody
  downstream could see.
- After writing, it re-reads every CSV. The row count must equal the sample count, and the first
  and last `timestamp_raw` must match. It also compares about 1000 pre-chosen rows against the
  xdat (|Δ| ≤ 0.0005 µV, the rounding). A NaN on one side and a number on the other fails.
- The sha256 is taken while writing. The uploader re-hashes the file independently and refuses if
  the two disagree.
- `--require-idle`: it will not start, and it stops, while another recording is being written.

Tests: `PYTHONPATH=. python3 tests/test_per_mouse_csv.py` (17 cases, 7 of them refusals).

## Reading one

```python
import pandas as pd
df = pd.read_csv("20260921_HLBSSL31_R.csv")          # ~86 M rows per 24 h
df = pd.read_csv(path, usecols=["timestamp_sec", "EEG", "EMG"],
                 dtype={"EEG": "float32", "EMG": "float32"})   # ~1 GB RAM per 24 h
```

In MATLAB, `readmatrix(path, "NumHeaderLines", 1)` reads it but loses the `datetime_kst` text
column. `readtable` keeps it but is slow at this size.

## Related

- [[02-procedures/CANONICAL-recording-naming-and-inventory]]: every recording, and which is which
- [[02-procedures/eeg-recording-console]]: starting a run
- [[02-procedures/installation/skim-nas-smb-and-upload]]: the share, the guard, verification

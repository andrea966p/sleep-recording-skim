# Per-mouse export — allego_1__uid0819-17-25-20

Recording started **2026-08-19 17:25:20 KST**, stopped **2026-08-21 09:05:47 KST**.
**39.674 h**, 1000 Hz, 142,825,728 samples per channel, file verified byte-exact with
**zero dropped samples**.

## Layout

```
allego_1__uid0819-17-25-20/
  manifest.json            every position, its channels, QC and verdict
  <POS>/
    <POS>_raw_1000Hz.mat   MATLAB, 1.14 GB   <- use this one
    <POS>_raw_1000Hz.txt   text, 3.7 GB      <- time_s,eeg_uV,emg_uV
    <POS>_hypnogram_4s.csv per-epoch sleep stage      (stageable positions only)
    <POS>_summary.txt      staging verdict + caveats  (stageable positions only)
    <POS>_features.json    per-position feature summary
    <POS>_info.json        provenance
```

`<POS>` is the RIG POSITION (port letter + slot), not an animal identity.

## Loading in MATLAB

```matlab
S = load('A1/A1_raw_1000Hz.mat');
t = (0:numel(S.eeg)-1)'/double(S.fs);     % seconds from recording start
plot(t, S.eeg);
```

**The time vector is deliberately NOT stored.** At 1000 Hz a float64 time column
would add 1.14 GB per file and push it past MATLAB v5's 2 GB limit. The one line
above rebuilds it exactly.

The text file is provided as requested, but for 142.8 million rows MATLAB's
`readmatrix` is slow and memory-hungry. **Prefer the .mat unless you specifically
need text.**

```matlab
H = readtable('A1/A1_hypnogram_4s.csv');   % small, 35,706 rows
```

## Units and polarity

Values are **microvolts**. The signals are **already the bipolar difference** the
RHD2216 produces. ⚠️ **Do not subtract EEG from EMG or one channel from another.**

## Time base

- `time_s` = seconds from the first sample.
- `t0_local_iso` in the .mat and info.json gives the wall-clock start.
- `zt_h` in the hypnogram is Zeitgeber time; **ZT0 = 09:00 KST** (lights on 09:00,
  off 21:00). The recording starts at ZT8.42.

## Which positions are what

Every position below has a hypnogram CSV **except B1**. Read the verdict column before using any of
them — three of the six are not usable as sleep architecture.

| position | stage-1 QC | usable in blocks | WAKE | NREM | r@1min | verdict |
|---|---|---|---|---|---|---|
| **A1** | CLEAN 99.99% | 39.67 h, longest **1356 min** | 43.3% | 52.1% | **0.495** | ✅ **SCOREABLE** |
| **A2** | CLEAN 99.98% | 39.67 h, longest 655 min | 52.3% | 43.3% | **0.592** | ✅ **SCOREABLE** |
| **D2** | CLEAN 99.90% | 39.63 h, longest 324 min | 54.2% | 42.8% | **0.446** | ✅ **SCOREABLE** |
| C2 | DIRTY 38.3% | 12.32 h in 90 blocks, longest 61 min | 17.8% | 77.0% | **0.11** | 🔴 REJECT |
| D1 | DIRTY 10.0% | 1.92 h in 29 blocks, longest 8.7 min | 29.0% | 64.5% | **0.001** | 🔴 REJECT |
| B2 | OPEN (EMG) | **0.00 h** | — | — | — | 🔴 NO STATES |
| C1 | CLEAN 99.98% | 39.66 h | 45.7% | 53.0% | 0.544 | ⛔ **animal gone; withdrawn** |
| B1 | OPEN 0.13% | — | — | — | — | ⛔ animal gone; not staged |

### Why C2 and D1 must not be read as sleep architecture

Their numbers look like architecture and are not. **`r@1min` is the persistence of the labels** —
how much a state predicts the next minute. A1/A2/D2 sit at 0.446-0.592 against a shuffled null of
about 0.00. **C2 is 0.11 and D1 is 0.001**, i.e. barely distinguishable from randomly relabelled
data. The pipeline rejects below 0.3.

The architecture numbers give the same warning independently: **C2 reads 17.8% WAKE**, which is not
a plausible figure for a mouse over 39.7 h — the three good animals sit at 43-54%. That low wake
number is what fragmented contact looks like after staging, not a sleepy animal. **D1 contributes
1.92 h of the 39.67 h**, in blocks with a median length of seconds.

### B2 — good EEG, open EMG, and therefore no hypnogram

B2's **EEG is genuinely good**: 92.4% usable, longest unbroken block 261.5 min, mains 72.7 µV.
Its **EMG electrode is open** at 535.8 µV mains against a 150 µV limit.

Sleep staging on this rig separates WAKE from sleep by an Otsu split on **log EMG RMS**. With an
open EMG that cut measures amplifier noise, so the pipeline returns `states missing` and every epoch
is marked `EXCLUDED`. **That is the correct result, not a failure to try.**

What B2's CSV *does* contain, validly, for all 35,706 epochs: `eeg_rms_uv`, `delta`, `theta`,
`theta_delta`, `zt_h`. Those are EEG-derived and unaffected by the EMG. Use them for spectral work.

> [!note] If you want a hypnogram from B2 anyway
> Single-EEG (no EMG) sleep staging in mice is a published approach — see
> https://www.nature.com/articles/s41598-021-90332-1 — but this project has not implemented or
> validated it. Producing one here would mean inventing an unvalidated algorithm, which is exactly
> how a confidently wrong result gets made. It is a deliberate open item, not an oversight.

## Provenance

- QC and staging: `eeg-emg-analysis/pipeline/` stages 1-3.
- Staging rule: WAKE by Otsu split of log EMG RMS refit **per animal**; NREM/REM
  split on theta/delta.
- ⚠️ **The REM percentage in the summary is FIXED BY CONSTRUCTION** (top 20% of
  sleep) and must not be reported as a finding. The Otsu REM cut in
  `features.json` is the measurable one.
- 🛑 Sleep architecture from these hypnograms remains **PROVISIONAL** until a
  blind-scoring kappa exists. No hypnogram here has been checked by a human.

Full analysis: vault `05-experiments/completed/2026-08-21-39h-run-score.md`.

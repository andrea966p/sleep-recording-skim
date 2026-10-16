---
tags: [procedure, nanotag, sleep, activity, nas, analysis, canonical]
created: 2026-10-05
status: active
---

# Nanotag studies: recording, read-out, NAS upload and analysis

> [!abstract] TL;DR
> **What this is:** the nanotag workflow from implant to report. It was run for HLBNSL (NS-SL SOD1 vs NW-SL water, 2026-09) and will be reused for NS-SD / NW-SD (surgery 2026-10-12). **Why it exists:** nanotag studies are the project's second recording method, without EEG and without the rig. Until 2026-10-05 the code and data lived only on the workstation Desktop. **How to read it:** the five steps below are the whole job; the sections expand each one. Device facts: [[nanotag-kissei-device-and-literature]]. Study page: [[2026-09-14-HLBNSL-nanotag-SOD1-sleep]]. Big picture: [[01-infrastructure/system-overview]].
>
> 1. **Plan reads around the memory.** At 12 s activity + 5 min temperature the tag **stops itself after 8 days**; with no temperature, after **9 days** (not 20, see below). Read before that.
> 2. **Log every handling, read and test** with clock times in the sheet's `NANOTAG behavioral` tab. Each logged window is removed from the analysis: whole room, rounded out to the hour.
> 3. **Export the RAW CSV** from nanotagViewer, named after the **mouse** (`HLBNWSL45`, never `HLBNSSL_45` for a water mouse).
> 4. **Analysis** (repo `sleep-recording-skim`):
>
>        /usr/bin/python3 nanotag/analysis/cohort.py --demo
>        /usr/bin/python3 nanotag/analysis/cohort.py ~/Desktop/Andrea/nanotag/"nanotag recording data/HLBNSL"
>        nanotag/report/build.sh
>
> 5. **NAS** (SKIM, `02_Data_Sleep/andrea/<HLBNSSL|HLBNWSL>/<Baseline|Treatment>/<date>_<mouse>_<B|T>/`): stage, then verified copy, per batch:
>
>        /usr/bin/python3 nanotag/analysis/export_nas.py "<data dir>" STAGE [nanotag/analysis/out/HLBNSL]
>        /usr/bin/python3 eeg-emg-analysis/qc/nas_copy_verified.py STAGE/HLBNSSL /mnt/skimnas/02_Data_Sleep/andrea/HLBNSSL
>
> 🛑 The SKIM NAS is a **working copy, not a backup** ([[backup-architecture]]). As of 2026-10-05 nanotag raw data exists on the workstation Desktop and the SKIM NAS only; there is no off-site copy yet.

> [!quote] Paper-ready
> Activity loggers were implanted subcutaneously at the neck and recorded continuously in the home cage. Data were read out by NFC before the 8-day memory limit, and a new recording was started at each read. Periods of handling, data read-out and behavioural testing were logged with clock times and excluded from the start of the first animal's session to the end of the last animal's session, each rounded out to the full hour. Sleep was scored separately for each recording file, and the files were then joined per animal.

## 1. Before surgery: program the tag

- In nanotagViewer, set activity **12 s**, temperature **5 min** (or no temperature: **9 days** of memory. Kissei's English manual prints 20; the Japanese manual and nanotagViewer say 9. NS-SD uses no temperature), threshold **170/170**, and a **delayed start** at the planned recording time.
- `Using memory type`: Stop (default) ends the recording when memory is full. Loop overwrites the oldest data. Use Loop only if every read is guaranteed before 8 days.
- The battery runs from the moment of programming (~60 days with activity + temperature), so do not program weeks ahead.
- Note the **nanotag ID ↔ mouse** pairing in the registry. The analysis identifies mice by the tag ID in each file header (`TAG` in `cohort.py`), not by the file name.

## 2. Implant

- Under the skin, **antenna side (blank face) outward**, reachable by the reader (~1 cm).
- In HLBNSL every tag was inserted at the neck and pushed right, and **migrated to the right dorsolateral flank**. That site is not Kissei-validated. **Anchor the tag next time** (Hasegawa 2024: 5-0 nylon to the extramuscular membrane).
- Weigh before surgery. Every later body weight includes the ~2.7 g tag (sheet `Config` → `NANOTAG_MASS`).
- Start the baseline **≥ 7 days after surgery**. HLBNSL used day +3, which is too early; see the report's limits.

## 3. Reading a tag (NFC)

- Use the PaSoRi RC-S380 on the Windows PC with the viewer dongle. Hold the reader over the flank and follow the mouse. Avoid restraint where possible.
- 🛑 **HLBNSSL43 died on 2026-09-28 within 30 s of restraint on the metal grid**, after failing hand habituation. Read from the open hand, following the animal (as with 47/48/50), and stop if the mouse will not settle.
- Each read gives one `.nta` file. Export it as **CSV, raw (not summarized)**: the parser refuses summarized exports.
- At the read, set the next recording's start **≥ 1 h after the last read of the session**. On 2026-09-28 the SOD1 mice's Run 2 started at 10:00 while reads and 43's death were still going on, so its first hour is removed. A post-read activity burst (11:00–12:00) is still visible in both groups.
- Log the read time per mouse, not "PM Session". The `.nta` file time is when the file was **saved**, 30–80 min after the logged read, so it cannot stand in for the read time.
- After death or explant the tag keeps logging. The temperature goes `Out of range` as it cools. Everything from the moment the mouse leaves its home cage for the last time is cut (`EXCLUDE`).

## 4. Logging windows: the sheet is the source

Every handling session, read, test and sampling goes in `NANOTAG behavioral` with start and end times per mouse. `cohort.py` turns each day's entries into one room-wide window: first start rounded **down** to the hour, last end rounded **up**. The rest of the day is kept. Bottle swaps done without handling are left in.

## 5. Files on the workstation

    ~/Desktop/Andrea/nanotag/nanotag recording data/HLBNSL/
        260917_HLBNSSL_homecage_baseline/   20641_HLBNSSL41_bas.{nta,csv} ...
        260917_HLBNWSL_homecage_baseline/
        260927_HLBNSSL_8days_part1/         260928_HLBNSSL_41.{nta,csv} ...   Run 1
        260917_HLBNWSL_8days_part1/
        261002_HLBNSSL/                     261002_HLBNSSL_<n>.{nta,csv}      Run 2, all 9 mice

`FOLDERS` in `cohort.py` maps each subfolder to (period, run). **A new batch needs a new `FOLDERS`, `TAG`, `SOD1/WATER`, `SURGERY`, `EXCLUDE` and `SOD1_START` block.** Those constants are the cohort manifest. Turn them into a manifest file once a second cohort makes that worthwhile.

## 6. Analysis: what `cohort.py` does

Full rationale, with every choice checked against the manual and literature: `methods.html` (and `.docx`) in the analysis folder.

1. Parse each CSV (`nta_qc.parse`): header, 12 s activity, 5 min temperature (`Out of range` skipped and counted). Mouse from the header tag ID. A file with a gap is rejected.
2. Score sleep per file: ≥ 4 consecutive zero-count bins (48 s) = sleep (`nta_qc.sleep_score`, after Pack 2007).
3. Remove the `EXCLUDE` windows, then join the files of each mouse and period (baseline; treatment = Run 1 + Run 2).
4. Per ZT day (09:00 → 09:00), compute % asleep in the light and dark phases. A phase with < 6 h recorded is left out (`MIN_PHASE_H`).
5. Per mouse: means, sleep bouts (≤ 24 s wake bridged; never across a phase boundary or a removed window), rhythm (IS, IV, RA, M10, L5 on hourly counts), temperature vs activity.
6. Groups: exact permutation test; treatment effect = SOD1 change − water change; CI by inverting the same test.
7. Sensitivity: the 24/36/60 s cutoffs, and the undisturbed vs handling + test days split (`treatment_split.csv`).

**Self-checks:** `cohort.py --demo`, `nta_qc.py --demo`, `export_nas.py --demo`. **Regression:** with Run 2 withheld from `FOLDERS`, the code reproduces the 2026-10-01 Run-1-only tables exactly. Re-run that check after any change to the loader.

**Outputs:** `nanotag/analysis/out/HLBNSL/`, git-ignored. CSV tables, figures, `report.html`, `methods.html`; `nanotag/report/build.sh` rebuilds the `.docx` and `.pptx` from the two HTML pages. It needs node via nvm and installs `docx` and `pptxgenjs` from the lock file on first run.

## 7. NAS layout (SKIM NAS, `02_Data_Sleep/andrea/`)

    HLBNSSL/Baseline/20260914_HLBNSSL41_B/
        20260914_HLBNSSL41_B.csv          time_kst, cross_count, temperature_c, run, excluded, sleep
        20260914_HLBNSSL41_B.info.json    tag, runs + sha256, excluded windows with reasons, verdict
        raw/20641_HLBNSSL41_bas.{nta,csv}
    HLBNSSL/Treatment/20260920_HLBNSSL41_T/   (Run 1 + Run 2 joined; raw/ holds both reads)
    HLBNWSL/...                                (same; Run 2 raw files keep their HLBNSSL_<n> names)
    HLBNSL_nanotag_ANALYSIS_2026-10-05/        report, methods, docx, pptx, figures, tables, protocol
    nanotag-pilot/                             09-09 two-tag pilot, 09-29 NFC-speed test, Kissei sample data

- The CSV keeps **every** bin. `excluded = 1` marks removed windows, and `sleep` is blank there. Filter on `excluded == 0` to reproduce the analysis; the merged CSV matches `cohort.load` bin for bin.
- `info.json` `verdict`: `ANALYSED`; `NOT ANALYSED` (49, 50 baseline: 1 day only); `EXCLUDED` (43, all data).
- `nas_copy_verified.py` re-reads every file from the share with the page cache dropped, compares sha256, and writes `SHA256SUMS` per batch folder. Run it once per batch folder so each SHA256SUMS stays inside its batch.

## History

> [!history]
> - **2026-10-16** — Memory with no temperature corrected to 9 days (English manual misprints 20).
> - **2026-10-05** — Created when nanotag work moved into the repo and vault (code from `~/Desktop/Andrea/nanotag/analysis/`, now `nanotag/analysis/`, symlinked back). First NAS upload of HLBNSL (98 files, all verified) and the Run 1 + Run 2 merge.

---
tags: [decision, council, sleepstager, sleep-scoring, data-format]
date: 2026-10-06
created: 2026-10-07
type: council + decision
status: settled (2026-10-08)
sourced-from: 04-journal/2026-10/2026-10-06.md, 04-journal/2026-10/2026-10-07.md
---

# How SleepStager reads the rig's per-mouse CSV (council 2026-10-06, decided 2026-10-07)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The record of one choice: how the professor's scoring program, SleepStager,
> should open the rig's recordings. It could only open `.mat` and the old `.3eg` files, and the rig
> now delivers one CSV per mouse.
>
> **Why it exists.** A council of five advisors recommended a converter to `.mat`. Two facts the
> council did not have then changed the answer: Andrea works on **local copies** (the NAS is storage
> only), and the professor wants the program to open **several formats** anyway. So the CSV reader
> went into SleepStager itself, and was proven equal to the `.mat` route on real data.
>
> **How to read this page.** §1 the question, §2 the council, §3 what changed and the decision,
> §4 the evidence. Using the program: [[sleepstager-user-guide]]. Big picture:
> [[nvr-system-overview]].

## 1. The question

The rig's canonical output since 2026-09-29 is one CSV per mouse
(`timestamp_raw,timestamp_sec,datetime_kst,EEG,EMG`, 1 kHz, ~4.8 GB per 24 h, plus `info.json`;
[[per-mouse-csv-format]]). SleepStager read only `.3eg` and per-mouse `.mat` v7.3.

| Option | |
|---|---|
| **A** | a standalone CSV → `.mat` converter; SleepStager untouched (a ~1.4 GB second copy per mouse-day) |
| **B** | a CSV reader inside SleepStager with a binary cache beside the file |
| **C** | a plain CSV reader, slow on every open (1–2 min with pandas) |

## 2. The council (2026-10-06)

| Advisor | Position |
|---|---|
| Contrarian | **A.** B and C open the canonical file, and SleepStager *moves* a recording on its first save. B's cache is a hidden copy with weak invalidation (mtime over SMB). Derive the start time from the counter and assert it (the 9 h KST/UTC trap) |
| First Principles | **A, run once at the rig.** A deterministic `.mat` stamped with the CSV's sha256 cannot drift. Fix move-on-save regardless |
| Expansionist | **B.** Reading the canonical file directly makes SleepStager the front end of the pipeline; the cache build is where to validate |
| Outsider | **B,** but never move canonical files; cache locally, keyed on `info.json`, not mtime; mouse ID from `info.json` |
| Executor | **A this week** (about a day); B later by calling the converter on open |

**Peer review** (anonymous, 5 reviewers): First Principles strongest; Expansionist weakest (it ignored
the cache's failure modes). Missed by all: the rig can already make the `.mat` from the xdat; a
recording must be complete before anything reads it; labels must point to their source.

**Chairman:** option A at the rig, and first stop SleepStager from moving anything inside the NAS tree.

## 3. What changed, and the decision (2026-10-07)

1. **Andrea works on local copies; the NAS is storage only.** The move-on-save danger to the
   canonical tree disappears, and so do most objections to a reader in the program (SMB mtime,
   several writers, hidden copies on the share).
2. **The professor plans to open several formats in SleepStager anyway.** A converter would be thrown
   away; a reader is work she would need regardless.
3. **Measured, not assumed:** reading the CSV with pyarrow directly takes **~1.3 s and ~4.2 GB peak**
   for 24 h, against 0.85 s / 3.4 GB for the `.mat`. A cache is not needed. (pandas' own pyarrow
   engine peaked at 13.5 GB; the slow figure in the council's brief was the pandas C engine.)

**Decision: a native CSV reader in SleepStager (option B without the cache).** Start time from the
CSV, checked against `info.json` to 2 ms; breaks from the device counter; mouse ID from `info.json`;
a file in its rig folder is not moved on save. Details:
[[sleepstager-changes-and-backlog]].

## 4. The evidence

HLBSSL33 Recovery 2026-09-21 (24 h). The CSV, read by the new reader, against a `.mat` made
independently from the raw stripped xdat (`split_xdat.py`, taught the 16-channel layout):

| Check | Result |
|---|---|
| sample counter | the CSV's 86.4 M samples are `.mat` samples 31,345,728–117,745,727, exactly the `info.json` window |
| EEG / EMG | max difference **0.000000 µV** |
| clock | **0 µs** apart; first sample 2026-09-21 09:00:00.000 |
| the rule's cuts and all features | identical |
| stages | **21,600 / 21,600 identical** |

Script: `SleepStager/scripts/eval/compare_csv_mat.py <csv> <mat>`.

**Settled 2026-10-08** (Andrea), after the check was run again in front of them with the same result ([[2026-10-08]]). The
comparison `.mat` and the local xdat copy were deleted; the xdat stays on e10 (`~/radix/data/`, `~/radix/stripped/`).

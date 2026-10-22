# CANONICAL — recording names, and the inventory of every recording

> [!abstract] TL;DR
> A recording has **one** name: `allego_N__uidMMDD-HH-MM-SS`. Always write that,
> never `uid0910-09-00-00` and never `uid0910`. The `allego_N` half is not
> decoration — it is part of the filename on disk, and `N` changes between
> recordings on the same day.
>
> Everything else (NAS directory, S3 key, note title) is a *label pointing at*
> that name. This page says how each one is formed and gives the full inventory.

Written 2026-09-23, after 110 references across 17 notes were found written three
different ways for the same files.

## The canonical name

```
allego_0__uid0910-09-00-00
└──┬───┘  └─┬──┘ └───┬────┘
   │        │        └─ start time, HH-MM-SS, KST
   │        └────────── MMDD of the start date
   └─────────────────── Allego's per-session file index
```

This is the base name Allego writes. Three files share it:
`<base>_data.xdat`, `<base>_timestamp.xdat`, `<base>.xdat.json`.

> [!warning] `allego_N` is not always `allego_0`
> `N` is Allego's file index within a server session, so it restarts at 0 when
> Allego restarts and increments otherwise. 2026-08-28 alone produced
> `allego_3__`, `allego_4__` and `allego_5__`. **A bare `uid0828-...` does not
> identify a file** and cannot be pasted into any path.
>
> If you meet a bare uid in an old document, resolve it against the table below,
> or against `neurosurveillance/deploy/logs/radix-archive.manifest` for
> recordings no longer on e10.

## The other namespaces, and how each is formed

| Namespace | Form | Example |
|---|---|---|
| **On disk, e10** | `~/radix/data/<base>_data.xdat` | `allego_0__uid0910-09-00-00_data.xdat` |
| **Stripped, e10** | `~/radix/stripped/<base>_data.xdat` | same base, fewer channels |
| **S3** | `s3://…/radix/data/<base>_data.xdat` | base preserved exactly |
| **SKIM NAS, per mouse** (since 2026-09-29) | `02_Data_Sleep/<user>/<batch>/<Baseline\|Recovery>/<YYYYMMDD>_<MOUSEID>_<B\|R>/` | `HLBWSL/Baseline/20260910_HLBWSL21_B/` |
| **SKIM NAS, experiment** (until 2026-09-29) | `03_Data_Mouse/<user>/<YYYYMMDD>_<batch>_<type>/` | `20260910_HLBWSL_BSR/` |
| **SKIM NAS, screens and tests** | `03_Data_Mouse/<user>/<YYYY-MM-DD>_<base>/` | `2026-09-13_allego_0__uid0913-11-20-07/` |
| **QC bundle** | `<CACHE_ROOT>/<base>.npz` | `~/eeg-qc-cache/allego_0__uid0910-09-00-00.npz` |
| **Note title** | `recording-<YYYY-MM-DD>-<short label>.md` | a label, never an identifier |

> [!warning] The experiment NAS directory name does NOT contain the recording name
> `20260910_HLBWSL_BSR` says date, batch and condition. Nothing in it identifies
> which Allego file it holds. **Never match NAS directories to recordings by
> filename.** Read the `allego_base` key inside that directory's `UPLOAD.json`;
> it is there precisely for this.
>
> ⚠️ The four screen and test folders predate that key and do not carry it. For
> those, the directory name itself is the base. Anything walking the NAS has to
> handle both.

> [!important] 2026-09-29: the NAS is organised by MOUSE, in `02_Data_Sleep`, as CSV
> Each mouse of each recording is one folder holding one CSV + `info.json`. Its `allego_base` key
> is the join back to the rows below. **Match a mouse folder to a recording by that key**, never
> by the folder's date. Format: [[per-mouse-csv-format]].
>
> Why there were two folders for W-SD (`BSR` and `BSR-2`) and two for S-SD: W-SD's baseline was
> stopped at 17:16 on 08-19 when B1 chewed its tether and restarted 9 min later. S-SD's second
> folder is the 08-26 B1-swap re-record, a different recording. Only the canonical eight in
> "Which of these are the experiment" are rebuilt into the per-mouse tree
> (`eeg-recorder/deploy/rebuild_02_data_sleep.py`). ✅ Done 2026-09-30: 64 mouse folders, each
> cut to its analysis window ([[CANONICAL-recording-windows-and-protocol]]). S-SD B1
> is UNPAIRED by design: HLBSSD13 has a baseline only, HLBSSD17 a recovery only.

> [!history] All eleven experiment folders were renamed to registry naming on 2026-09-23
> Three shapes had accumulated: `HLBW_SL` from a run record where the batch was
> typed with an underscore, `HLBSSL` from ones where it was not, and
> `2026-09-10_allego_0__uid0910-09-00-00` for recordings with no run record at
> all. The batch stem now always follows the intake registry ids — `HLBWSD`,
> `HLBSSD`, `HLBWSL`, `HLBSSL`.
>
> Each was a **re-upload, not a `mv`**. `UPLOAD.json` is a verification record:
> sha256 at both ends, read back with the CIFS cache dropped so the read hits the
> wire. Renaming the folder and editing that file by hand would turn a
> measurement into a claim. The old folder was removed only after the new one
> verified.
>
> ✅ **`CACHE_ROOT` moved out of `/tmp` on 2026-09-23**, to `~/eeg-qc-cache`.
> `pipeline/stage1_qc.py` carried its own second `/tmp` default under
> `EEG_QC_CACHE`; it now derives from the same root, so the two cannot disagree.
> The nine surviving bundles were copied across and checksummed.
>
> 🔴 **Three QC bundles existed ONLY on the NAS** — `uid0910`, `uid0912`,
> `uid0917`. `CACHE_ROOT` was `/tmp/eeg_pipeline_cache` and the 2026-09-22 reboot
> emptied it. Each was copied back before anything was deleted. A rename that
> deleted first would have destroyed the only surviving record of those
> recordings' wire-free floor, and they could never have been QC'd again.
>
> ⚠️ **A directory listing of `/mnt/skimnas` can be stale right after a delete.**
> `ls` and `find` both kept returning a removed folder while `[ -d ]` said it was
> gone — a cached CIFS dentry. Verify with a stat, not a glob; touching the
> parent directory clears it.

## Every recording on e10

Generated from the `.xdat.json` headers, regenerated 2026-09-23 after
`allego_0__uid0904-08-55-25` and `allego_0__uid0829-08-34-39` were deleted.
**27 recordings.**
Start and end are KST. `pri ch` is primary amplifier channels; every surviving
recording is 256, the full eight-mouse rig. The only 128-channel file was
`allego_0__uid0904-08-55-25`, now deleted.

| recording | start KST | end KST | h | GB | pri ch |
|---|---|---|---|---|---|
| `allego_0__uid0818-18-56-33` | 2026-08-18 18:56 | 08-18 19:02 | 0.11 | 0.4 | 256 |
| `allego_1__uid0818-20-50-26` | 2026-08-18 20:50 | 08-18 21:50 | 1.00 | 3.8 | 256 |
| `allego_0__uid0819-09-00-00` | 2026-08-19 08:59 | 08-19 17:16 | 8.28 | 31.2 | 256 |
| `allego_1__uid0819-17-25-20` | 2026-08-19 17:25 | 08-21 09:05 | 39.67 | 149.7 | 256 |
| `allego_0__uid0824-17-56-51` | 2026-08-24 17:56 | 08-24 18:56 | 1.00 | 3.8 | 256 |
| `allego_0__uid0825-09-00-00` | 2026-08-25 08:59 | 08-26 09:16 | 24.28 | 91.6 | 256 |
| `allego_1__uid0826-12-50-16` | 2026-08-26 12:50 | 08-27 09:09 | 20.33 | 76.7 | 256 |
| `allego_2__uid0827-12-58-32` | 2026-08-27 12:58 | 08-28 09:05 | 20.12 | 75.9 | 256 |
| `allego_3__uid0828-09-26-12` | 2026-08-28 09:26 | 08-28 09:27 | 0.02 | 0.1 | 256 |
| `allego_4__uid0828-10-08-34` | 2026-08-28 10:08 | 08-28 11:56 | 1.80 | 6.8 | 256 |
| `allego_5__uid0828-19-10-50` | 2026-08-28 19:10 | 08-28 19:46 | 0.59 | 2.2 | 256 |
| `allego_0__uid0901-12-24-03` | 2026-09-01 12:24 | 09-01 12:25 | 0.03 | 0.1 | 256 |
| `allego_1__uid0901-12-38-53` | 2026-09-01 12:38 | 09-01 12:40 | 0.02 | 0.1 | 256 |
| `allego_2__uid0902-13-00-28` | 2026-09-02 13:00 | 09-03 09:05 | 20.08 | 75.7 | 256 |
| `allego_1__uid0909-21-17-52` | 2026-09-09 21:17 | 09-09 22:40 | 1.38 | 5.2 | 256 |
| `allego_0__uid0910-09-00-00` | 2026-09-10 08:59 | 09-11 09:23 | 24.39 | 92.0 | 256 |
| `allego_0__uid0911-22-32-22` | 2026-09-11 22:32 | 09-11 22:33 | 0.03 | 0.1 | 256 |
| `allego_0__uid0912-08-55-18` | 2026-09-12 08:55 | 09-13 08:59 | 24.07 | 90.8 | 256 |
| `allego_0__uid0913-11-20-07` | 2026-09-13 11:20 | 09-13 11:29 | 0.15 | 0.6 | 256 |
| `allego_0__uid0914-10-50-56` | 2026-09-14 10:50 | 09-14 10:56 | 0.09 | 0.3 | 256 |
| `allego_0__uid0914-11-50-43` | 2026-09-14 11:50 | 09-14 11:57 | 0.11 | 0.4 | 256 |
| `allego_0__uid0914-13-05-32` | 2026-09-14 13:05 | 09-14 13:09 | 0.06 | 0.2 | 256 |
| `allego_0__uid0914-14-03-06` | 2026-09-14 14:03 | 09-14 14:08 | 0.08 | 0.3 | 256 |
| `allego_0__uid0914-16-47-08` | 2026-09-14 16:47 | 09-14 16:51 | 0.07 | 0.2 | 256 |
| `allego_0__uid0917-09-00-09` | 2026-09-17 09:00 | 09-18 13:00 | 28.00 | 105.6 | 256 |
| `allego_0__uid0920-09-00-07` | 2026-09-20 09:00 | 09-21 00:08 | 15.14 | 57.1 | 256 |
| `allego_0__uid0921-00-17-34` | 2026-09-21 00:17 | 09-22 13:00 | 36.71 | 138.5 | 256 |

## Which of these are the experiment

Eight recordings carry the four batches' baseline and recovery. Everything else
in the table is a screen, a test, or an unexplained run.

| Batch | Baseline 24 h | Recovery |
|---|---|---|
| W-SD | `allego_0__uid0819-09-00-00` + `allego_1__uid0819-17-25-20` | `allego_2__uid0827-12-58-32` |
| S-SD | `allego_0__uid0825-09-00-00` | `allego_2__uid0902-13-00-28` |
| W-SL | `allego_0__uid0910-09-00-00` | `allego_0__uid0917-09-00-09` |
| S-SL | `allego_0__uid0912-08-55-18` | `allego_0__uid0920-09-00-07` + `allego_0__uid0921-00-17-34` |

⚠️ **The whole file is rarely the analysis window.** Which hours of each of these
to use, the protocol they are judged against, and the discard list live in
[[CANONICAL-recording-windows-and-protocol]].

Two of these are **split across two files**, with a real gap in the middle:

- W-SD baseline, gap 2026-08-19 17:16 → 17:25
- S-SL recovery, gap 2026-09-21 00:08 → 00:17

Both gaps are about nine minutes. Either side clears the 15 minute unbroken-block
bar for rung 2, so the data is scoreable, but no 24 h continuity claim survives
across them.

## Discrepancies on record

**The intake registry's two SL baseline dates are a day early.** It lists W-SL
baseline as 2026-09-09 and S-SL as 2026-09-11; the recordings ran on 09-10 and
09-12. Both registry values equal tethering + 7 exactly, so they read as planned
dates never corrected after the runs slipped. The SD batches match to the day.
The recordings are right; the registry is not.

**`allego_0__uid0829-08-34-39` was deleted on 2026-09-23.** 59.2 h, 223 GB, the
largest file the rig had ever produced, and an **ECG recording** — not part of
any sleep batch, which is why it had no registry row. It was also the one
recording flagged `is_live_recording` while idle, with a `num_smpl` 8.06 s behind
what its files actually held. Gone from e10 and from S3.

**`allego_0__uid0904-08-55-25` was deleted on 2026-09-23.** 30 h at 128 primary
channels, half the rig, recorded on the S-SL tethering day with no registry row.
Andrea identified it as belonging to something else entirely. Removed from e10 and from S3 —
the S3 versions had to go too, since versioning means a plain delete leaves a
marker and the version still billing.

**The 09-17 run record has a typo.** It lists D1 as `HLBWSL7`; no such animal
exists and the registry has HLBWSL27 there. Corrected in `cohorts/W-SL.yaml`,
left as-is in the run record.

**`_quarantine-2026-08-24-crashed-run/`** holds a real 13 min recording
(`allego_0__uid0824-17-23-21`, 822 MB) inside `~/radix/data`. The archiver used to
skip it, being a subdirectory, so it had no off-site copy at all while every file
beside it had two. **Fixed 2026-09-23** — the archiver recurses and it is in S3.

## Related

- [[backup-architecture]] — which copy lives where
- [[CANONICAL-allego-channel-selection]] — the channel map
- [[xdat-channel-stripping]] — how stripped files are made

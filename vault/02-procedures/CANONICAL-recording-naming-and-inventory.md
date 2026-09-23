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
| **SKIM NAS, older** | `03_Data_Mouse/<user>/<YYYY-MM-DD>_<base>/` | `2026-09-10_allego_0__uid0910-09-00-00/` |
| **SKIM NAS, newer** | `03_Data_Mouse/<user>/<YYYYMMDD>_<batch>_<type>/` | `20260917_HLBW_SL_RSR/` |
| **QC bundle** | `<CACHE_ROOT>/<base>.npz` | `/tmp/eeg_pipeline_cache/allego_0__uid0910-09-00-00.npz` |
| **Note title** | `recording-<YYYY-MM-DD>-<short label>.md` | a label, never an identifier |

> [!warning] The newer NAS directory name does NOT contain the recording name
> `20260917_HLBW_SL_RSR` is built from the run record's batch name, not from the
> Allego base. Two of them can differ in style for the same batch — the 09-17
> directory is `HLBW_SL` while 09-20 and 09-21 are `HLBSSL`. **Never match NAS
> directories to recordings by filename.** Read the `allego_base` key inside that
> directory's `UPLOAD.json`; it is there precisely for this.
>
> A recording with no run record gets the older `<date>_<base>` form instead,
> which is why `allego_0__uid0910-09-00-00` sits in a differently shaped
> directory from its own 09-17 partner.

## Every recording on e10

Generated from the `.xdat.json` headers, regenerated 2026-09-23 after
`allego_0__uid0904-08-55-25` was deleted. **28 recordings.**
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
| `allego_0__uid0829-08-34-39` | 2026-08-29 08:34 | 08-31 19:46 | 59.20 | 223.4 | 256 |
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
[[02-procedures/CANONICAL-recording-windows-and-protocol]].

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

**`allego_0__uid0829-08-34-39` has a short header.** Its `num_smpl` says
213,124,096 while both data and timestamp files hold 213,132,160 — they agree
with each other, so nothing is corrupt, but the header is 8.06 s behind the
files. It is also the one recording still flagged `is_live_recording` while idle,
i.e. it did not shut down cleanly. Anything trusting `num_smpl` silently drops
its last eight seconds. It has no registry row, and at 59.2 h / 223 GB it is the
largest file on the rig.

**`allego_0__uid0904-08-55-25` was deleted on 2026-09-23.** 30 h at 128 primary
channels, half the rig, recorded on the S-SL tethering day with no registry row.
Andrea identified it as belonging to something else entirely. Removed from e10;
its three S3 objects still need deleting with an identity that has delete rights,
because the `radix-s3-backup` user is explicitly denied that, by design.

**The 09-17 run record has a typo.** It lists D1 as `HLBWSL7`; no such animal
exists and the registry has HLBWSL27 there. Corrected in `cohorts/W-SL.yaml`,
left as-is in the run record.

**`_quarantine-2026-08-24-crashed-run/`** holds a real 13 min recording
(`allego_0__uid0824-17-23-21`, 822 MB) inside `~/radix/data`. Because it is a
subdirectory, the S3 archiver skips it, so it has no off-site copy.

## Related

- [[02-procedures/backup-architecture]] — which copy lives where
- [[02-procedures/CANONICAL-allego-channel-selection]] — the channel map
- [[02-procedures/installation/xdat-channel-stripping]] — how stripped files are made

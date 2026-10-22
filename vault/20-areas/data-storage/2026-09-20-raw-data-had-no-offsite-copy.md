---
type: incident
area: data-storage
status: done
created: 2026-09-20
summary: "On 2026-09-20 an audit found 83 percent of the raw archive (931 GB) had no raw backup; the NAS archiver had stood down by design and 'NAS-verified' meant the stripped file"
tags: [incident, backup, s3, archive, audit]
---

# 83 percent of the raw archive had no raw backup (measured 2026-09-20)

> [!abstract] TL;DR
> Measured 2026-09-20, before the first S3 run, over the 28 recordings then on e10 (1118 GB raw):
> **931 GB, 83 percent, had no raw copy anywhere else.** Closed by the S3 archive ([[radix-s3-archive]],
> [[backup-architecture]]). Promoted 2026-10-22 from the workspace memory file
> `raw-data-had-no-offsite-copy-since-aug19`; [[backup-architecture]] already holds the rules, this page holds
> the numbers and the root cause.

| | Recordings | Raw bytes | Protection |
|---|---|---|---|
| Raw on the bilab NAS | 4 | 186.5 GB | safe, all 2026-08-18 and 08-19 |
| Stripped copy only | 6 | 275.0 GB | 16 of 262 channels, about 6 percent |
| No copy anywhere | 18 | 656.0 GB | single copy |

## Root cause, and it is not a bug

`radix-archive-watchdog.sh` (line 25) stands down permanently once `radix-archive.state` reads `COMPLETE`; its own
comment says "nothing to do, ever again (delete the state file to re-arm)". It finished its backfill on 2026-08-21
([[raw-recording-archive-to-nas]]) and went quiet. It was a one-shot migration tool and nothing replaced it for raw data.
`cron-archive-watchdog.log` has been 0 bytes since 2026-08-19, which looks like a broken cron but is the script
exiting early by design.

## "NAS-verified" meant the stripped file

`nas_upload.py` uploads `radix/stripped/`, not `radix/data/`. `strip-report.json` shows
`n_channels_in: 262 -> n_channels_out: 16`; `uid0912` is 90.8 GB local against 5.5 GB on the NAS. Those verifications
are real and 16 channels is the analysed montage, but the 262-channel source never left e10. This affects
[[2026-09-17-W-SL-28h-run]] and the stripper workflow in [[skim-nas-smb-and-upload]].

The stripper renames remotely, so matching NAS directories by uid undercounts. `20260917_HLBW_SL_RSR` is
`allego_0__uid0917-09-00-09`; resolve through the `allego_base` key in each directory's `UPLOAD.json`.

> [!note] Re-arming the old NAS raw archiver was not done
> Deleting `radix-archive.state` would add a second raw copy on the bilab NAS. Not requested, not done; it is a
> decision, not a fix. The bilab NAS still holds the raw files of 2026-07 to 2026-08-19 (130 files, 944 GB on disk,
> checked 2026-10-22).

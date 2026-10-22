---
name: raw-data-had-no-offsite-copy-since-aug19
description: "83% of the raw archive had no raw backup — the NAS archiver retired itself by design and the stripper only ever copied 16 of 262 channels"
metadata:
  type: project
---

Measured **2026-09-20**, before the first S3 run. Of 28 recordings then on e10
(1118 GB raw):

| | Recordings | Raw bytes | Protection |
|---|---|---|---|
| Raw on bilab NAS | 4 | 186.5 GB | safe, all Aug 18-19 |
| **Stripped copy only** | 6 | 275.0 GB | **16 of 262 channels = 6%** |
| **No copy anywhere** | 18 | 656.0 GB | **single copy** |

**931 GB — 83% of the raw archive — had no raw backup anywhere.**

🔴 **ROOT CAUSE, and it is not a bug.** `radix-archive-watchdog.sh:25` stands down
**permanently** once `radix-archive.state` reads `COMPLETE`, as its own comment
says: *"nothing to do, ever again (delete the state file to re-arm)"*. It finished
its backfill **2026-08-21** and retired. It was a one-shot migration tool. Nothing
replaced it for RAW data, and `cron-archive-watchdog.log` has been 0 bytes since
Aug 19, which reads like a broken cron but is the script exiting early by design.

🔴🔴 **"NAS-verified" in the run notes means the STRIPPED file, not the raw.**
`nas_upload.py` uploads `radix/stripped/`, not `radix/data/`. `strip-report.json`
shows `n_channels_in: 262 -> n_channels_out: 16`; `uid0912` is **90.8 GB local vs
5.5 GB on the NAS**. Those verifications are real and the 16 channels are the
analysed montage — but the 262-channel source never left e10.
Affects [[recording-2026-09-17-HLBW_SL-28h]] and [[skim-nas-smb-and-channel-stripper]].

🔑 **The stripper RENAMES remotely**, so matching NAS dirs by `uid` undercounts.
`20260917_HLBW_SL_RSR` is `allego_0__uid0917-09-00-09` — resolve via the
`allego_base` key in each dir's `UPLOAD.json`, never by filename.

✅ Closed by [[radix-s3-offsite-archive]], whose first run uploads raw for all 28.
⚠️ Re-arming the NAS raw archiver (delete `radix-archive.state`) would add a
second raw copy; **not done**, not requested.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴🔴⭐⭐⭐ **[83% OF THE RAW ARCHIVE HAD NO RAW BACKUP — measured 2026-09-20](raw-data-had-no-offsite-copy-since-aug19.md).** 931 GB unprotected. `radix-archive-watchdog.sh` **retires itself on COMPLETE by design** (Aug 21) — 0-byte log looks broken, isn't. 🔴🔴 **"NAS-verified" = the STRIPPED file (16 of 262 ch, 6%)**, never the raw. Resolve NAS dirs via `UPLOAD.json` `allego_base`, not filenames.

---
name: raw-data-had-no-offsite-copy-since-aug19
description: "2026-09-20: 83 percent of the raw archive had no raw backup; the NAS raw archiver retires itself by design and 'NAS-verified' means the stripped file. Incident in the vault"
metadata:
  type: project
---

Measured 2026-09-20: of 28 recordings (1118 GB raw) only 4 had a raw NAS copy; 6 had the stripped copy only (16 of 262 channels) and 18 (656 GB) had none, so 931 GB (83 %) was unprotected. `radix-archive-watchdog.sh` retires itself once `radix-archive.state` reads COMPLETE (2026-08-21), by design: a 0-byte cron log looks broken but is not. Closed by the nightly S3 job.

Details: [[2026-09-20-raw-data-had-no-offsite-copy]] · [[radix-s3-archive]] · [[backup-architecture]]

- 🔴🔴 "NAS-verified" in run notes means the STRIPPED file (16 of 262 ch), never the raw.
- 🔑 The stripper RENAMES remotely: resolve NAS dirs through the `allego_base` key in each dir's `UPLOAD.json`, never by filename or uid.
- ⚠️ Re-arming the NAS raw archiver (delete `radix-archive.state`) adds a second raw copy: not done, not requested.

---
type: hub
area: data-storage
status: active
created: 2026-10-22
summary: "Where the lab's data lives and how it is backed up: bilab NAS (rebuild the rig), SKIM NAS (working copy, not a backup), S3 (off-site), raw archive, per-mouse CSV layout"
---

# Data storage hub

## What this is
The lab keeps its data in three places with one job each: the bilab NAS holds what is needed to rebuild the rig, the SKIM NAS is the working copy the lab uses today (not a backup), and AWS S3 is the off-site copy that survives a fire.
Raw Allego recordings (262 channels) live on e10 and in S3; the analysis reads one CSV per mouse from the SKIM NAS.
Alerts from all of these jobs go to ntfy through `nvr-notify.sh` ([[backup-architecture]]).

## Current state
- 2026-10-22: S3 archive holds 213 objects, 1.258 TB; the raw job last completed 2026-10-21 and the stripped job 2026-10-22 [[radix-s3-archive]]
- 2026-10-22: bilab NAS keeps three nightly tarballs of about 568 MB (2026-10-20 to 2026-10-22) [[nas-backup]]
- 2026-09-29: SKIM NAS holds one CSV plus `info.json` per mouse in `02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/` [[skim-nas-smb-and-upload]]
- 2026-09-23: every file under `~/radix/data` has an S3 copy, quarantined runs included [[backup-architecture]]
- 2026-09-20: audit found 931 GB (83 percent) of raw data without a raw backup; closed by the S3 archive [[2026-09-20-raw-data-had-no-offsite-copy]]
- 2026-08-21: old raw archive to the bilab NAS finished (130 files) and stood down by design [[raw-recording-archive-to-nas]] [[2026-09-20-raw-data-had-no-offsite-copy]]

## Start here
- [[backup-architecture]]: the three destinations and the "where does X live" table
- [[nas-backup]]: nightly project snapshot to the bilab NAS
- [[radix-s3-archive]]: nightly raw and stripped upload to S3
- [[skim-nas-smb-and-upload]]: mounting the SKIM NAS and the upload rules
- [[per-mouse-csv-format]]: what the analysis reads

## Rules that must not be broken
- The SKIM NAS is not a backup; a file only there has one copy. Evidence: [[backup-architecture]]
- Never hardcode a `100.x` address for a NAS; use the MagicDNS name. Evidence: [[2026-08-19-nas-backup-wrong-address]]
- "NAS-verified" in a run note means the stripped file (16 of 262 channels), never the raw. Evidence: [[2026-09-20-raw-data-had-no-offsite-copy]]
- Deleting a recording is a three-place job: `~/radix/data`, the S3 objects, and their S3 versions. Evidence: [[backup-architecture]]
- Never write to, move or delete anything in `~/radix/data`; work from `~/radix/stripped`. Evidence: [[skim-nas-smb-and-upload]]
- Never run heavy disk jobs during a live recording; `RIG BUSY` in a dry run means stop. Evidence: [[radix-s3-archive]]
- Read-back verification over CIFS needs the page cache dropped, and the sentinel file guards a failed mount. Evidence: [[skim-nas-smb-and-upload]]
- Use the plain ssh pipe to the bilab NAS, never rsync or scp. Evidence: [[nas-backup]]

## Open items
- Whether an AWS budget alert exists is unconfirmed: the S3 note says one is configured, the memory record says it was deleted on 2026-09-20 [[radix-s3-archive]]
- Video uploader to S3 is not built; the structure is decided and waits for the cameras [[backup-architecture]]
- Nothing yet watches AWS spend if no alert exists; ask Andrea to check the Budgets console

## Everything here
![[area.base]]

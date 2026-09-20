---
name: radix-s3-offsite-archive
description: "Nightly off-site S3 archive of the raw recordings from e10 — bucket, scoped IAM user, and the checksum/cron gotchas"
metadata:
  type: project
---

Set up **2026-09-20**. Third copy of `~/radix/data`: e10 NVMe is the working set,
the SKIM NAS is local backup, S3 is off-site. Procedure page:
`02-procedures/installation/radix-s3-archive.md`.

- Bucket **`skim-eeg-radix-archive-760396521414`**, `ap-northeast-2`, class
  **`GLACIER_IR`** (~$5.50/mo at 1.1 TB). Versioning + AES256 + public access blocked.
- Script `neurosurveillance/deploy/radix-s3-archive.sh`, **cron 01:30 nightly**,
  **stripped first then raw, sequential in one cron line** so they never contend.
  `RADIX_S3_JOB` (raw|stripped) picks SRC/PREFIX and keeps `logs/radix-s3-archive-$JOB.{log,lock,state}`
  distinct. Prefixes: `radix/data/` 1.1 TB, `radix/stripped/` 23 GB, `video/` planned.
  Reuses `radix-archive.sh`'s guards verbatim: `recording_active()` before every
  file, `past_hard_stop()` at 08:30, `ionice -c3 nice -n 19`.
- Skip logic is **one `head-object` per file, compare `ContentLength`** — a file
  already in S3 is never read off disk. No manifest needed, unlike the NAS script.
- ⚠️ **NO budget and NO spend alerts** — one was created then **deleted at the user's
  request** on 2026-09-20. Nothing watches spend on this account.

🔴 **`ChecksumSHA256` reads `null` unless you pass `--checksum-mode ENABLED`** to
`head-object`. That looks exactly like "S3 stored no checksum" and it is not.
Verified at setup: a `FULL_OBJECT` SHA256 matched local `sha256sum` byte for byte
(S3 returns base64, `sha256sum` prints hex — convert before comparing).

🔴 **e10 has NO passwordless sudo**, so: AWS CLI installed **user-local** at
`/home/skimlab/.local/bin/aws` (official installer, `-i`/`-b` flags), and
scheduling is **cron, not systemd** — system units would need root. This matches
`radix-archive-watchdog`, which was already on cron.

🔑 **The unattended job cannot use SSO.** It runs as IAM user **`radix-s3-backup`**,
profile `radix-backup` in `/home/skimlab/.aws/credentials` (0600). Its inline
policy carries an **explicit `Deny` on `s3:DeleteObject`/`DeleteObjectVersion`**,
verified by a real delete attempt returning `AccessDenied ... explicit deny`. A bug
here or a compromise of e10 cannot erase the off-site copy.

⚠️ Glacier IR has a **90-day minimum duration per object** and charges per GB
retrieved. Fine for an archive never deleted; it would bite on a prefix reorg.

🔴 Built the week it mattered: at setup **83% of the raw archive had no raw copy**
anywhere — see [[raw-data-had-no-offsite-copy-since-aug19]]. The first run closes it.

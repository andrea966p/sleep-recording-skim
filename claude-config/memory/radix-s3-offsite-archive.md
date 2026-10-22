---
name: radix-s3-offsite-archive
description: "Nightly off-site S3 archive of raw recordings from e10 (bucket, scoped IAM user, checksum and cron gotchas) is in the vault; keeps the no-budget user decision that the vault disputes"
metadata:
  type: project
---

Set up 2026-09-20: third copy of `~/radix/data` (NVMe = working set, SKIM NAS = working copy, S3 = off-site). Bucket `skim-eeg-radix-archive-760396521414`, `ap-northeast-2`, `GLACIER_IR`, cron 01:30 (stripped then raw), IAM user `radix-s3-backup` with an explicit Deny on delete. 2026-09-26: no-op nights exit in ~1 s; files modified < 30 min ago are left for the next night (`recording_active()` fails open).

Details: [[radix-s3-archive]] · [[2026-09-20-raw-data-had-no-offsite-copy]] · [[backup-architecture]]

- ⚠️ NO budget and NO spend alerts: one was created then DELETED at the user's request on 2026-09-20. The vault Cost section says a budget alert is configured, which conflicts (unconfirmed, needs Andrea). Do not recreate one unasked.
- 🔴 `ChecksumSHA256` reads null without `--checksum-mode ENABLED` (not "no checksum stored"). 🔴 e10 has NO passwordless sudo: user-local `aws` CLI and cron, not systemd. The unattended job never uses SSO.
- 🔴 A daytime `--dry-run` without `ARCHIVE_IGNORE_WINDOW=1` hits the HARD STOP and SENDS a real ntfy "paused" push. Glacier IR has a 90-day minimum per object.

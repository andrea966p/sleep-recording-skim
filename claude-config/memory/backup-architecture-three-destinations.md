---
name: backup-architecture-three-destinations
description: "The three backup destinations and their one job each, plus the ntfy switch — set 2026-09-20"
metadata:
  type: project
---

Settled **2026-09-20**. Full page: `02-procedures/backup-architecture.md` — the
"where does X live?" table lives there, not here.

| Destination | Its ONE job |
|---|---|
| **bilab NAS** (21 TB) | *how to rebuild the rig* — repo, settings, daemon state, Frigate config. **No bulk data.** Nightly 00:00, keep 3 tarballs. |
| **SKIM NAS** (7 TB) | *what the lab works on today* — stripped xdat, students, protocols. Written on recording stop. |
| **AWS S3** | *what survives the building burning down* — raw + stripped xdat, video later. Nightly 01:30. |

🔑 **The SKIM NAS is NOT a backup.** It is the working copy. A file only there has
one copy. [[raw-data-had-no-offsite-copy-since-aug19]]

🔴 **The premise "e10 lost access to the bilab NAS" was FALSE** — checked
2026-09-20: reachable, active direct Tailscale link, and the nightly backup had
succeeded that very morning. All three tailnets are already cross-shared into
e10's: `skimlab.kaist@` (e10), `bilab.kaist@` (bilab NAS), `sleepigene@` (SKIM NAS).
**Verify reachability before planning any "reconnect" work.**

✅ **`nvr-notify.sh` now pushes to ntfy, not Slack** — same topic Netdata and Uptime
Kuma use (`DEFAULT_RECIPIENT_NTFY` in `/etc/netdata/health_alarm_notify.conf`).
One file, **7 callers** benefit. `fail` uses priority `max` to bypass Do Not
Disturb. Still always `exit 0` — a broken notifier must never take down a backup.
`NVR_NOTIFY_SLACK=1` falls back to the still-live Slack webhook.
🔴 Recipient must be the **full URL**; a bare topic silently fails as a hostname lookup.
⚠️ `SEND_SLACK="NO"` in the netdata conf only disables *netdata's own* Slack path —
`nvr-notify.sh` read that URL directly, so Slack was never actually broken.

✅ `nas-backup.sh` had **zero** notifications for its whole life; now has 4 (tar
failed, NAS unreachable, upload corrupt, success).

⚠️ **Video will dominate everything**: measured **~0.32 GB/h/camera**, so 4 chambers
continuous = **~31 GB/day, ~930 GB/month**. Structure decided
(`video/<researcher>/<mouse>/<date>/`, source `/opt/neurosurveillance/exports/`,
never `/srv/frigate/storage/`), **uploader deliberately NOT built** until cameras
return. [[radix-s3-offsite-archive]]

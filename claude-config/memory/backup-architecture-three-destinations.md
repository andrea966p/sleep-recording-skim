---
name: backup-architecture-three-destinations
description: "Three backup destinations, one job each (settled 2026-09-20): bilab NAS = rebuild the rig, SKIM NAS = working copy NOT a backup, S3 = survive the fire; nvr-notify.sh pushes to ntfy."
metadata:
  type: project
---

**Settled 2026-09-20.** bilab NAS (21 TB) = how to rebuild the rig (repo, settings, daemon state, Frigate config, no bulk data; nightly 00:00, keep 3 tarballs, skips unchanged nights since 2026-09-26). SKIM NAS (7 TB) = what the lab works on today (stripped xdat, written on recording stop). AWS S3 = what survives the building burning down (raw + stripped xdat, nightly 01:30). 🔑 The SKIM NAS is NOT a backup. Video will dominate (~0.32 GB/h/camera, ~930 GB/month for 4 chambers); the video uploader is deliberately not built until cameras return.

Details: [[backup-architecture]] (also [[radix-s3-archive]], [[nas-backup]])

🔴 The premise "e10 lost access to the bilab NAS" was FALSE (checked 2026-09-20): verify reachability before planning any "reconnect" work. `nvr-notify.sh` pushes to ntfy (same topic as Netdata and Uptime Kuma), `fail` uses priority `max`, it always `exit 0`; the recipient must be the FULL URL (a bare topic silently fails as a hostname lookup).

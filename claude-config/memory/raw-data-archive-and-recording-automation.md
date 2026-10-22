---
name: raw-data-archive-and-recording-automation
description: "2026-08-19: all raw .xdat archived to the bilab NAS sha256-verified plus unattended scheduled recording and watchdogs; facts in the vault, keeps the never-delete-locally and ssh -n rules"
metadata:
  type: project
---

2026-08-19/21: 130 files / 1.01 TB of raw `.xdat` were copied to the bilab NAS (ssh pipe, sha256 on both ends, `.part` then rename, window 08:30-20:00, `ARCHIVE_IGNORE_WINDOW=1` bypasses the window but not the recording check) and scheduled unattended recording went live (`scheduled-recording.sh`, hourly watchdog, user crontab because no sudo). The archive is a one-shot; the NIGHTLY raw copy is now the S3 job.

Details: [[raw-recording-archive-to-nas]] · [[scheduled-recording-and-watchdogs]] · [[radix-s3-archive]]

- 🛑 NOTHING IS EVER DELETED LOCALLY: that stays a human decision. rsync still fails on this NAS: ssh pipe only.
- 🔴 `ssh` inside a `while read` loop eats the loop's stdin (a verifier reported ok=1 after one file): always `ssh -n`. `pgrep -f <script>` guards match their own command line: use the state file.
- 🔴 `radiens` lives ONLY in `/opt/neurosurveillance/venv/bin/python3` (plus `PYTHONPATH=~/sleep-recording-skim/eeg-emg-analysis`). Success = bytes growing on disk, nothing the client reports.
- 🔴 A run started by hand in Allego did not arm the watchdog (write `logs/current-recording.txt`, delete `watchdog-lastsize.txt`); console runs arm it since 2026-10-14. Compare file-byte sums, not `du` (directory inode).

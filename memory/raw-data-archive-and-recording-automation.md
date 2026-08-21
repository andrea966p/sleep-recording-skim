---
name: raw-data-archive-and-recording-automation
description: "2026-08-19: all 831 GB of raw .xdat archived to the NAS checksum-verified, plus unattended scheduled recording with Slack watchdogs"
metadata:
  type: project
---

**2026-08-19, overnight. Two systems built, both live. Scripts in `neurosurveillance/deploy/`.**

## Raw data archive (`radix-archive.sh`)
✅ **124 files / 831.2 GB copied to the NAS in 7.5 h at 31 MB/s, ZERO errors, retries or mismatches.**
Destination `/volume1/homes/Andrea/e10_radix_archive/data`. NAS `/volume1` = 21 TB, 13 TB free.
🔑 **Every file sha256-verified on BOTH ends; lands as `.part` and is only renamed after the hashes
match ⇒ a file present under its real name IS the proof it verified.** Byte-wise resume, manifest
keyed on name+size, `ionice -c3 nice -n 19`, hard stop 08:30, backs off 10 min if a recording is on.
🛑 **NOTHING IS EVER DELETED LOCALLY — that stays a human decision.**
🔴 **rsync STILL fails on this NAS (retested 2026-08-19, password fallback) — ssh pipe only.**
⚠️ **It is a ONE-SHOT, not a schedule.** New recordings are NOT copied; `rm logs/radix-archive.state`
to re-arm the 20-min watchdog.

## Scheduled recording (`scheduled-recording.sh` + `recording-watchdog-cron.sh`)
✅ **Started 8 mice at exactly 09:00:00 on 2026-08-19 unattended** (`allego_0__uid0819-09-00-00`, ZT0).
🔴🔴 **`radiens` lives ONLY in `/opt/neurosurveillance/venv/bin/python3`** — NOT in
`~/eeg-analysis-venv`, NOT system python. Also needs `PYTHONPATH=~/Monitoring_project/eeg-emg-analysis`.
🔑 **Success = "RECORDING CONFIRMED GROWING" (bytes on disk). Nothing the client reports counts.**
Preflight refuses if allegoserver is down, <150 GB free, or a recording is already running.
Hourly watchdog alerts on the R_ON-but-not-growing stall signature; self-disarms on stop.
⚠️ **No sudo available while the user sleeps ⇒ everything runs from the USER CRONTAB, not systemd.**
Cron one-shots need a date guard (`[ "$(date +\%Y-\%m-\%d)" = "..." ]`) because cron has no year, and
`%` must be escaped as `\%`.
⚠️ **The live start was never rehearsed** — a test recording was blocked as a real-world action, so
components were verified separately and the 09:00 run was the first real execution.

## Two bugs worth remembering
🔴 **`ssh` inside a `while read` loop EATS THE LOOP'S STDIN** — my verifier reported `ok=1` after
checking ONE file and would have given a false green light to deleting 831 GB. **Always `ssh -n`.**
⚠️ **The nightly `nas-backup.sh` never included `eeg-emg-analysis`** — the analysis code was
unbacked-up entirely. Added, with `~/radix/devices` + `workspace`. Tarball 198 MB → 242 MB.

Slack: `nvr-notify.sh`, reads the webhook at runtime from `/etc/netdata/health_alarm_notify.conf`
(world-readable) so there is no second copy of the secret. Verified HTTP 200.

Related: [[nas-backup-stale-address-outage]] · [[nas-backup]] · [[recording-2026-08-18-eight-new-mice]]


## 2026-08-19 evening revisions
🔴 **A HAND-STARTED RECORDING DOES NOT ARM THE WATCHDOG.** Only `scheduled-recording.sh` writes
`logs/current-recording.txt`. After starting a run by hand in Allego you MUST:
`echo "<basename>" > deploy/logs/current-recording.txt && rm -f deploy/logs/watchdog-lastsize.txt`.
**Deleting the lastsize file is not optional** — a stale baseline (30.4 GB vs a 126 MB new file)
reads as shrinkage and fires a FALSE STALL alarm, or the watchdog disarms and leaves the run unwatched.
✅ **Archive now DEFERS instead of churning during a recording** (~4 s exit, state `DEFERRED`), and the
watchdog stands down silently without counting a strike. The old code slept 600 s PER FILE and
skipped — ~21 h of sleeping per pass over 130 files, plus an "incomplete" Slack message every pass.
⚠️ **The archive will not run between 08:30 and 20:00** (protected window) even with no recording.


## 2026-08-21: everything archived + the 39.7 h run
✅ **130 files / 1.01 TB on the NAS, verified.** Cross-checked independently: counts 130=130, zero
`.part`, **file-byte sums identical (1,013,471,371,569)**, no per-file size diffs, fresh sha256 of the
149.7 GB run matches. ⚠️ **`du -sb` shows the NAS ~9.8 kB larger — that is the DIRECTORY INODE, not
data. Compare file-size sums, not `du`.**
⭐ **`allego_1__uid0819-17-25-20` = 39.674 h, 142,825,728 samples, timestamp steps `{1:...}` ⇒ ZERO
dropped samples, drift +9 ppm, byte-exact.** Cleanest long run this rig has made. **File integrity
only — signal quality NOT yet scored.**
✅ **The automation held 40 h unattended**: hourly watchdog `OK growing` every check, **zero false
alarms**, auto-disarmed on stop; archive stayed `DEFERRED` with no churn or strikes.
🔑 **`ARCHIVE_IGNORE_WINDOW=1`** bypasses the 08:30-20:00 window for a manual run; it does NOT bypass
the recording check.
🔴 **Perf fix: the manifest skip now runs BEFORE `recording_active()`** (which costs ~3.3 s spawning a
python client). Re-scanning 130 done files went ~7 min → **4.3 s**.
✅ **Both repos are on GitHub now (private): `neurosurveillance` (branch `ops/...`) and
`eeg-emg-analysis` (205 objects, 18.53 MiB, first push ever).**
⚠️ **My `pgrep -f <script>` guards keep matching my OWN command line — use the state file, not pgrep.**

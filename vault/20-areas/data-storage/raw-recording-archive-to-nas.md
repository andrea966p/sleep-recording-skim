---
type: procedure
area: data-storage
status: active
tags: [infrastructure, backup, nas, eeg, archive]
created: 2026-08-19
---

# Raw recording archive to the NAS

> [!warning] Updated 2026-10-22: the figures below are as of 2026-08-21 (the bilab NAS archive dir held 130 files, 944 GB on disk, on 2026-10-22). An off-site S3 archive was added on 2026-09-20 and covers raw data now, the nvr-notify.sh alerts go to ntfy instead of Slack, and Syncthing is retired [[backup-architecture]]

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A one-way, verified copy of every raw electrophysiology recording
> (`~/radix/data`, the `.xdat` files Allego writes) from the recording computer onto the lab NAS.
> **Why it exists.** Until 2026-08-19 those recordings existed in exactly one place: one solid-state
> drive in one computer. The nightly project backup deliberately excludes them because of their
> size, so months of animal data had no second copy at all. A drive failure would have ended the
> project.
> **What it does NOT do.** It never deletes anything locally. Deleting the local copy is always a
> human decision, taken after reading the verification report.

## Status

**Current as of 2026-08-21 18:07: 130 files, 1.01 terabytes, all verified on the NAS.**

- First run 2026-08-19: 124 files, 831.2 GB, 7.5 h, zero errors.
- Second run 2026-08-21: the remaining 182.3 GB (the 8.27 h run and the 39.7 h run), 1.4 h.

Independent cross-check after the second run: file counts 130 = 130, zero leftover `.part` files,
**sum of file bytes identical to the byte on both sides**, no per-file size differences, and a fresh
sha256 of the 149.7 GB run matching its manifest entry.

> [!note] `du -sb` will show a small difference and it is not a fault
> The directory inode differs in size between ext4 and the NAS filesystem — about 9.8 kilobytes.
> **Compare the sum of file sizes, not `du`.**

> [!tip] Running it by hand outside the protected window
> ```bash
> ARCHIVE_IGNORE_WINDOW=1 ./radix-archive.sh
> ```
> This skips the 08:30-20:00 window only. The recording check still applies, so the run still defers
> if the rig starts up.

## The files

| Path | Role |
|---|---|
| `neurosurveillance/deploy/radix-archive.sh` | the transfer engine |
| `neurosurveillance/deploy/radix-archive-watchdog.sh` | restarts a dead transfer (cron, every 20 min) |
| `neurosurveillance/deploy/radix-archive-verify.sh` | re-reads every file ON THE NAS and re-checks it |
| `neurosurveillance/deploy/nvr-notify.sh` | posts to Slack; used by all of the above |
| `deploy/logs/radix-archive.manifest` | the state: name, size, sha256, status, timestamp |
| `deploy/logs/radix-archive.state` | `COMPLETE` or `INCOMPLETE` + timestamp |

Destination on the NAS: `/volume1/homes/Andrea/e10_radix_archive/data`

## How it guarantees correctness

This matters more than speed, because the whole point is to be able to delete the local copy.

1. **Checksum on both ends, computed during the write.** The receiving side runs
   `tee <file> | sha256sum`, so the NAS hashes the bytes as it stores them, in a single pass. That
   hash is compared to a `sha256sum` of the local file.
2. **Nothing is named correctly until it is proven.** Every transfer lands as `<name>.part`. It is
   only renamed to `<name>` after the checksums match. **A file appearing under its real name on
   the NAS is itself the proof that it verified.**
3. **A mismatch destroys the remote copy and starts that file over**, up to three attempts.
4. **Resume is byte-wise.** On restart it asks the NAS how many bytes it already holds and sends
   only the remainder. A killed run costs seconds, not hours.
5. **The manifest is keyed on name AND size.** If a local file changes size it is re-transferred
   and re-verified rather than trusted.

> [!note] Why not rsync
> `rsync` fails against this NAS — it falls back to a password prompt and dies. This was retested on
> 2026-08-19 and still fails, so the long-standing note is confirmed, not inherited. The plain
> `ssh` pipe is the only reliable primitive here. **Do not "modernise" this to rsync or scp.**

## How it protects the rig

The archive reads the same disk the amplifiers write to, so it must never win a fight with a
recording.

- Before every file it asks Allego whether a recording is running. If it is, it **sleeps 10 minutes
  and re-checks** rather than competing.
- All disk reads run under `ionice -c3 nice -n 19`, the lowest possible priority.
- There is a **hard stop at 08:30**, so it is always out of the way before the usual 09:00 start.
  It reports the pause to Slack and resumes that evening.
- The watchdog will not start a run between 08:30 and 20:00.

## Self-healing

`radix-archive-watchdog.sh` runs every 20 minutes from cron. If the archive is not `COMPLETE` and
no run holds the lock, it starts one. That covers an SSH drop, a NAS reboot, this machine
rebooting, the process being killed, or a network fault — because the transfer is idempotent and
resumable, relaunching is always safe. It announces the first restart to Slack and then warns every
sixth, so a genuinely stuck loop becomes visible without spamming.

## Verifying before you delete anything

**Do not delete the local copy on the strength of matching file sizes.** Sizes match trivially;
content is the question. Run:

```bash
/home/skimlab/sleep-recording-skim/neurosurveillance/deploy/radix-archive-verify.sh
```

It re-reads every archived file **on the NAS** and compares its sha256 to the value recorded at
transfer time, then posts the verdict to Slack. It touches only the NAS side, so it is safe to run
during a live recording.

> [!warning] A BUG THAT WOULD HAVE GIVEN A FALSE GREEN LIGHT
> The first version of the verifier reported `ok=1` — it checked **one** file and declared victory.
> Cause: `ssh` inside a `while read` loop consumes the loop's standard input, swallowing the rest of
> the manifest. The fix is `ssh -n`. If you ever write a loop that runs `ssh` per item, **use
> `ssh -n` or the loop will silently process exactly one item.**

## Operations

```bash
# progress / result
tail -f /home/skimlab/sleep-recording-skim/neurosurveillance/deploy/logs/radix-archive.log
cat     /home/skimlab/sleep-recording-skim/neurosurveillance/deploy/logs/radix-archive.state

# how many files are verified
awk -F'\t' '$4=="DONE"' .../logs/radix-archive.manifest | sort -u | wc -l

# re-arm after adding new recordings (the state file stops the watchdog)
rm /home/skimlab/sleep-recording-skim/neurosurveillance/deploy/logs/radix-archive.state
```

## Still open

- **The archive is a one-shot, not a schedule.** New recordings are NOT copied automatically yet.
  After each run finishes, delete `radix-archive.state` and the watchdog will pick up the new files
  within 20 minutes. Turning that into a nightly job is the obvious next step and is not done.
- **The live recording is excluded by definition** — a file still being written cannot be verified.
  It gets archived on the next pass after it is stopped.
- The NAS has 13 terabytes free, so capacity is not a constraint for a long time.

Related: [[nas-backup]] ·
[[2026-08-19-nas-backup-wrong-address]] ·
[[scheduled-recording-and-watchdogs]]

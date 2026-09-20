# Off-site S3 archive of the raw recordings

Nightly, incremental copy of `~/radix/data` (raw Allego `.xdat`) from `e10ubuntu`
to Amazon S3. This is the **third** copy: e10 NVMe is the working set, the SKIM
NAS is the local backup, S3 is the off-site one. The animals were sampled, so
these recordings cannot be retaken; a fire or a theft in the building should not
end the project.

Set up 2026-09-20.

## What it is

| | |
|---|---|
| Script | `neurosurveillance/deploy/radix-s3-archive.sh` |
| Schedule | `crontab` entry for `skimlab` (no sudo on e10; matches `radix-archive-watchdog`) |
| Runs | 01:30 daily via cron — stripped first, then raw. Hard-stops at 08:30 |
| Bucket | `s3://skim-eeg-radix-archive-760396521414` |
| Prefixes | `radix/data/` (raw, 1.1 TB) · `radix/stripped/` (22 GB) · `video/` planned |
| Region | `ap-northeast-2` (Seoul) |
| Storage class | `GLACIER_IR` (Glacier Instant Retrieval) |
| AWS account | 760396521414, inside the Brain Repair Laboratory org |
| Credential | IAM user `radix-s3-backup`, profile `radix-backup` on e10 |

## The guards, and why each one is there

This script never gets to compete with the rig. Three independent brakes:

1. **`recording_active()`** — queries Allego for `recording.mode == R_ON`. Checked
   before the run starts and again before every single upload. A recording that
   starts mid-run stops the archive, it does not merely slow it.
2. **`past_hard_stop()`** — refuses to keep going after **08:30**, so the 09:00
   recording window always has the disk to itself. Note the `10#` base-10 forcing
   in that function: without it bash reads `08`/`09` as octal and the test errors
   out instead of firing, which is exactly how the NAS archiver's guard was left
   inoperative on 2026-08-19.
3. **`ionice -c3 nice -n 19`** on every read and every upload. The rig wins any
   contention for the NVMe.

`ARCHIVE_IGNORE_WINDOW=1` skips only the clock guard, for a deliberate manual run
with the rig idle. It does **not** skip the recording check.

## One script, several jobs

`RADIX_S3_JOB` names the run and keeps its log, lock and state files distinct, so
the raw and stripped jobs can never share a lock or clobber each other's state:

| Job | `RADIX_S3_SRC` | `RADIX_S3_PREFIX` |
|---|---|---|
| `raw` (default) | `/home/skimlab/radix/data` | `radix/data` |
| `stripped` | `/home/skimlab/radix/stripped` | `radix/stripped` |

```bash
RADIX_S3_JOB=stripped \
RADIX_S3_SRC=/home/skimlab/radix/stripped \
RADIX_S3_PREFIX=radix/stripped \
  neurosurveillance/deploy/radix-s3-archive.sh --dry-run
```

State lands in `logs/radix-s3-archive-<job>.{log,lock,state}`.

The stripped job runs **before** raw in the same cron line: it is only 22 GB, so it
finishes in minutes and gets protected immediately rather than waiting the two or
three nights the first raw pass takes. A missing `RADIX_S3_SRC` directory is a hard
failure with a notification, never a silent zero-file success.

⚠️ The stripped source is **e10-local**, so S3 covers only what e10 still holds
(22 GB), not the fuller history on the SKIM NAS (84 GB). Deliberate: it removes any
dependency on the CIFS mount being healthy at 01:30.

## How "skip what is already there" works

One `s3api head-object` per file. If the object exists at the same byte size, the
file is skipped without being read off disk at all. That is the entire mechanism,
and it is why a resumed run over a mostly-complete archive costs seconds.

The cheap checks come first deliberately: `recording_active()` spawns a python
client and costs ~3.3 s, so querying the rig about files that are already archived
wasted ~7 min per resumed run on the NAS archiver's backlog. A file we are going
to skip needs no rig query.

## Integrity

Every upload carries `--checksum-algorithm SHA256`. S3 verifies it server-side and
rejects a corrupted upload. This gives the same end-to-end guarantee as the NAS
script's two-sided `sha256sum` without a second full read of a 13 GB file.

After upload, the object's `ContentLength` is compared against the local size
before the file is counted as done.

To verify an archived file independently, at any time, without downloading it:

```bash
# S3 returns its stored checksum ONLY with --checksum-mode ENABLED.
# Without that flag ChecksumSHA256 reads null, which looks like "no checksum"
# but is not — it is a missing read flag.
aws s3api head-object --bucket skim-eeg-radix-archive-760396521414 \
  --key radix/data/<file> --checksum-mode ENABLED --query ChecksumSHA256 --output text

# compare against the local file (S3 stores it base64, sha256sum prints hex)
sha256sum <file> | cut -d' ' -f1 | \
  python3 -c 'import base64,binascii,sys; print(base64.b64encode(binascii.unhexlify(sys.stdin.read().strip())).decode())'
```

Verified at setup: a `FULL_OBJECT` SHA256 stored by S3 matched the local
`sha256sum` byte for byte.

## It cannot delete anything

The IAM user holds `s3:PutObject`, `s3:GetObject`, `s3:ListBucket` and the
multipart-upload actions, scoped to this one bucket. It does **not** hold
`s3:DeleteObject`. This is enforced by AWS, not merely by the script, so a bug
here or a compromise of e10 cannot erase the off-site copy.

The bucket also has versioning on, so even an overwrite of an existing key keeps
the previous version.

## Cost

Glacier Instant Retrieval at `$0.005/GB-month` in Seoul.

| Archive size | Monthly |
|---|---|
| 1.1 TB (at setup) | ~$5.50 |
| 2 TB | ~$10 |

Caveats that bite:

- **90-day minimum duration per object.** Deleting an object before 90 days still
  bills the remainder of the 90 days. Irrelevant for an archive you never delete.
- **Retrieval is charged per GB read.** Restores are instant but not free. This is
  a disaster copy, not a working share.
- **Incomplete multipart uploads bill as storage.** A lifecycle rule aborts them
  after 7 days. Without that rule, a few failed 13 GB uploads silently accrue
  charges forever.

The bill goes to the collaborating lab's consolidated account, so a budget alert
is configured on top of this.

## Operating it

```bash
# what would it do, without uploading anything
ssh e10 'neurosurveillance/deploy/radix-s3-archive.sh --dry-run'

# progress / last outcome
ssh e10 'tail -30 sleep-recording-skim/neurosurveillance/deploy/logs/radix-s3-archive-raw.log'
ssh e10 'cat  sleep-recording-skim/neurosurveillance/deploy/logs/radix-s3-archive-*.state'

# schedule + recent cron output
ssh e10 'crontab -l | grep s3-archive'
ssh e10 'tail -20 sleep-recording-skim/neurosurveillance/deploy/logs/cron-s3-archive.log'

# what is actually in the bucket
aws s3 ls s3://skim-eeg-radix-archive-760396521414/radix/data/ --summarize --human-readable
```

`RIG BUSY` in a dry run means a recording is live. Stop; do not override.

## Restoring

Glacier IR restores are instant, no thaw needed:

```bash
aws s3 cp s3://skim-eeg-radix-archive-760396521414/radix/data/<file> .
```

Budget for the retrieval charge on a large restore; pulling the whole 1.1 TB back
is not free.

## Notifications

Via the shared `nvr-notify.sh`, which pushes to **ntfy** (topic in
`DEFAULT_RECIPIENT_NTFY`, `/etc/netdata/health_alarm_notify.conf`). Failures use
priority `max` so they bypass Do Not Disturb. The notifier always exits 0 — it can
never take down a backup.

## Related

- [[02-procedures/backup-architecture]] — the whole picture, all three destinations

- `radix-archive.sh` — the NAS copy. Deliberately a separate script so either
  destination keeps working if the other's access is revoked.
- `nas-backup.sh` — the nightly project/config snapshot, which **excludes** bulk
  data by design.
- [[skim-nas-smb-and-channel-stripper]] — the newer stripper workflow that uploads
  to the NAS on recording stop.

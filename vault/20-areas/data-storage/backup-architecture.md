---
type: reference
area: data-storage
status: active
---
# Backup architecture — where everything goes

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The lab keeps three separate copies of its work, each in a
> different place and each with a different job. This page says which is which,
> so nobody has to guess where a file lives or whether it is safe.
>
> **Why it exists.** Backups grew one script at a time. On 2026-09-20 an audit
> found 83% of the raw electrophysiology had no second copy anywhere, because a
> one-off migration script had quietly retired itself in August and nothing
> replaced it. Nobody noticed because nobody could say what the rules were.
>
> **How to read this page.** Start at the three-line summary. Use the "where does
> X live?" table when you are looking for a specific file. The per-destination
> sections are only needed when something breaks. Big picture:
> [[nvr-system-overview]].

## The three destinations, in one line each

| Destination | Its one job |
|---|---|
| **bilab NAS** | *How to rebuild the rig.* Configuration, code, settings. No bulk data. |
| **SKIM NAS** | *What the lab works on today.* The active working copy. |
| **AWS S3** | *What must survive the building burning down.* Archive, rarely read. |

**No-op nights cost almost nothing, and a growing recording is never touched**
(2026-09-26): the bilab NAS job skips when nothing changed; the S3 jobs exit in ~1 s
when no file changed and never upload a file modified in the last 30 min; the SKIM
NAS only runs after a recording stops. Details on each procedure page.

If you only remember one thing: **the SKIM NAS is not a backup.** It is where work
happens. A file that exists only there is a file with one copy.

## Where does X live?

| Data | e10 local | bilab NAS | SKIM NAS | AWS S3 |
|---|---|---|---|---|
| Raw xdat (262 ch) | `~/radix/data` | until 2026-08-19 only | ❌ never | ✅ `radix/data/`, verified 1:1 |
| Stripped xdat (16 ch) | `~/radix/stripped` | ❌ | ✅ `03_Data_Mouse/<user>/` | ✅ `radix/stripped/` |
| Git repo + vault | `~/sleep-recording-skim` | ✅ nightly tarball | ❌ | ❌ (GitHub is the off-site copy) |
| e10 settings, daemon state, Frigate config | various | ✅ nightly tarball | ❌ | ❌ |
| Video MP4s | `/opt/neurosurveillance/exports/` | ❌ (sidecar JSONs only) | ❌ | 🔜 `video/` — planned |
| Frigate rolling segments | `/srv/frigate/storage` | ❌ | ❌ | ❌ regenerable, never backed up |

## bilab NAS — how to rebuild the rig

Synology at `bilab-syn.tail8808c0.ts.net`, shared into this tailnet from the
`bilab.kaist@` account. 21 TB, ~12 TB free. Reached over SSH on **port 53**, key
auth as user `Andrea`.

- **Script** `neurosurveillance/deploy/nas-backup.sh`, systemd timer, **00:00 daily**.
- **Holds** one dated tarball per run, `e10_backup_<YYYY-MM-DD>.tar.gz` (~350 MB),
  rolling **3-day** retention.
- **Contains** the whole workspace repo, Allego device/workspace config,
  `/opt/neurosurveillance` config + sessions + export sidecar JSONs, and the
  Frigate compose/config/mosquitto trees.
- **Deliberately excludes** all bulk data. Two separate exclude lines block
  `*/radix/data` and `*.xdat` so it cannot be undone by accident.
- **Notifies** on success and on all three failure modes (tar failed, NAS
  unreachable, upload corrupt) — see below.

Full page: [[nas-backup]].

## SKIM NAS — what the lab works on today

Synology at `skim-nas.tailec38b9.ts.net`, shared in from `sleepigene@`. Mounted
over CIFS at `/mnt/skimnas` (autofs, mounts on access). 7 TB, ~4.6 TB free.

- **Written by** `eeg-recorder/backend/nas_upload.py` when a recording stops.
- **Layout** `03_Data_Mouse/<user>/<YYYYMMDD>_<batch><condition>/`, one directory
  per recording, with the stripped xdat, its `strip-report.json`, a QC bundle,
  `run.json` and `UPLOAD.json`. Screens and tests keep `<YYYY-MM-DD>_<base>/`.
- **Holds the stripped data only** — 16 of 262 channels, roughly 6% of raw size.

> [!warning] "NAS-verified" in a run note means the STRIPPED file
> The verification is real, and 16 channels is the analysed montage. But the
> 262-channel original never went to this NAS. `allego_0__uid0912-08-55-18` is 90.8 GB on e10 and
> 5.5 GB here. If you need the other 246 channels, S3 is the only other copy.

> [!tip] The uploader renames remotely
> `20260917_HLBWSL_RSR` is `allego_0__uid0917-09-00-09`. Matching NAS directories
> by Allego uid undercounts. Resolve via the `allego_base` key in each directory's
> `UPLOAD.json`, never by filename.
>
> Two directory shapes exist. Every experiment folder is
> `<YYYYMMDD>_<batch><condition>` with the batch stem from the intake registry —
> all eleven were renamed to that on 2026-09-23. The four screen and test folders
> keep `<YYYY-MM-DD>_<allego base>`, which is right: they have no batch or
> condition to be named after. Only the experiment folders carry `allego_base` in
> their `UPLOAD.json`; for the older four the directory name IS the base.
> Naming rules and the full recording inventory:
> [[CANONICAL-recording-naming-and-inventory]].

## AWS S3 — what must survive the building burning down

Bucket `s3://skim-eeg-radix-archive-760396521414`, region `ap-northeast-2`,
class `GLACIER_IR`. Versioning on, AES256 on, public access blocked, and a
lifecycle rule aborts incomplete multipart uploads after 7 days.

| Prefix | Source on e10 | Job | Size |
|---|---|---|---|
| `radix/data/` | `~/radix/data` | `raw` | 84 objects, 1.018 TB, quarantine included |
| `radix/stripped/` | `~/radix/stripped` | `stripped` | 49 objects, 27.4 GB |
| `video/` | `/opt/neurosurveillance/exports/` | *planned* | — |

One script serves every prefix. `RADIX_S3_JOB` keeps each run's log, lock and
state file distinct so jobs never share a lock:

```bash
RADIX_S3_JOB=stripped \
RADIX_S3_SRC=/home/skimlab/radix/stripped \
RADIX_S3_PREFIX=radix/stripped \
  neurosurveillance/deploy/radix-s3-archive.sh --dry-run
```

Runs **01:30 nightly**, stripped first (small, finishes fast), then raw. Both
hard-stop at 08:30 for the morning recording window.

> [!success] The archive is real as of 2026-09-23
> **133 objects, 1.046 TB**, both jobs `COMPLETE`, every object SHA256-verified by
> S3 on upload. Before this the bucket held **zero bytes**: the job was installed
> on 09-20 and every scheduled run since had deferred, because a recording was
> live at 01:30 each night. A backup that has never once run is indistinguishable
> from a backup that works, unless somebody looks in the bucket.
>
> Two defects surfaced the first time it ran against a real directory, both fixed
> in `radix-s3-archive.sh`:
>
> - **It uploaded `*.part` files.** The first live run began sending a dead
>   24-channel partial from a crashed strip — bytes that were going to change,
>   into GLACIER_IR, under an IAM user explicitly denied `s3:DeleteObject`.
> - **It could never report COMPLETE.** `TOTAL_FILES` came from `ls -1`, which
>   counts subdirectories, while the upload loop skipped them. `done_files` stopped
>   one short forever, so every run took the INCOMPLETE branch and warned about
>   "0 file(s) failed". Both source directories contain exactly one such
>   subdirectory, so both jobs raised a false alarm on every successful run.
>
> ✅ **The archiver recurses as of 2026-09-23.** It used to stop at `-maxdepth 1`,
> which silently excluded `_quarantine-2026-08-24-crashed-run/` — a real 13 min
> recording that therefore had no off-site copy at all. A subdirectory under
> `~/radix/data` is a quarantined run, which is exactly what an archive is for.
> The relative path becomes the S3 key, so the tree is reproduced as it stands.
> **Everything in `~/radix/data` now has an off-site copy.**

> [!tip] Verify the mirror, do not assume it
> The archive matches e10 only if every local file has an object of the same size
> and nothing is orphaned the other way. Checked 2026-09-23 after two recordings
> were deleted:
>
> ```
> RAW: 81 local, 81 in S3
>    on e10 but NOT in S3 : none
>    in S3 but NOT on e10 : none
>    size mismatches      : none
> ```
>
> The stripped prefix legitimately lags: anything stripped after the last 01:30
> run waits for the next one. On 2026-09-23 that was 28 files, 40.73 GB. A lag is
> only a problem if it survives a night, which happens when a recording is live at
> 01:30 and the job defers.
>
> 🔴 **Deleting a recording is a THREE place job.** `~/radix/data`, the S3 objects,
> and — because versioning is on — the S3 **versions** behind them. A console
> delete with "Show versions" off writes a delete marker: the object leaves the
> listing and the version keeps billing. `radix-s3-backup` is explicitly denied
> `s3:DeleteObject`, so this is done from an identity that has delete rights,
> never by loosening that policy.
>
> ⚠️ GLACIER_IR bills a **90 day minimum** per object, so deleting something
> recently uploaded still costs the remainder of its 90 days.

Full page: [[radix-s3-archive]].

### Video — planned, not yet built

Cameras have been offline since 2026-08-04, so no uploader exists yet. The
structure is decided so that turning it on later is wiring, not design:

- **Prefix** mirrors the on-disk export tree exactly:
  `video/<researcher>/<mouse-id>/<YYYY-MM-DD>/YYMMDDHHMM_mouseID_type.mp4`
- **Source** is `/opt/neurosurveillance/exports/` — the stitched session MP4s.
  **Never** `/srv/frigate/storage/`, which holds regenerable rolling segments.
- **Sidecar JSONs** stay in the bilab NAS tarball as today; only MP4s go to S3.
- **Storage class** to be decided when volume is real.

> [!warning] Video will dominate the bill
> Measured from the one existing export: **~0.32 GB/h per camera**. Four chambers
> recording continuously is **~31 GB/day, ~930 GB/month** — roughly the entire
> current EEG archive every month. Revisit Deep Archive versus Glacier IR, and
> revisit spend monitoring, before switching this on.

## Reachability check, 2026-09-20: nothing needed reconnecting

The premise that e10 had lost access to the bilab NAS was false. Checked on 2026-09-20: the NAS was reachable over
an active direct Tailscale link and the nightly backup had succeeded that same morning. All three tailnets are already
cross-shared into e10's (`skimlab.kaist@` for e10, `bilab.kaist@` for the bilab NAS, `sleepigene@` for the SKIM NAS;
addresses in [[production-values]]). Verify reachability before planning any "reconnect" work. Source: the Claude
memory record of that date, promoted here on 2026-10-22; the nightly tarballs of 2026-10-20 to 2026-10-22 were still
arriving when checked on 2026-10-22. The audit that day that found the raw gap: [[2026-09-20-raw-data-had-no-offsite-copy]].

## Notifications

All scripts push to **ntfy** via the single shared notifier
`neurosurveillance/deploy/nvr-notify.sh`:

```bash
nvr-notify.sh <ok|warn|fail|info> "<title>" "<body>"
```

- Recipient is read from `DEFAULT_RECIPIENT_NTFY` in
  `/etc/netdata/health_alarm_notify.conf` — the same source of truth Netdata and
  Uptime Kuma use. One place to rotate.
- Level sets ntfy `Priority`: `fail` → `max`, which bypasses Do Not Disturb.
- **It never fails loudly.** Always exits 0, so a broken notifier cannot take down
  a backup. Trouble goes to stderr, which lands in the journal or the cron log.
- `NVR_NOTIFY_SLACK=1` falls back to the still-live Slack webhook.

> [!warning] The recipient must be a full URL
> A bare topic name makes curl treat it as a hostname and fail silently with no
> config error. Always `https://ntfy.sh/<topic>`. See
> [[monitoring-setup]] §8.3b.

## Verifying each path

```bash
# bilab NAS — did last night's tarball land?
ssh e10 'systemctl status nas-backup.service --no-pager | head -5'

# SKIM NAS — is it mounted, and what is the newest recording?
ssh e10 'findmnt /mnt/skimnas && ls -1t /mnt/skimnas/03_Data_Mouse/andrea | head -3'

# S3 — what is actually up there?
aws s3 ls s3://skim-eeg-radix-archive-760396521414/ --recursive --summarize | tail -3

# S3 jobs — last outcome of each
ssh e10 'cat sleep-recording-skim/neurosurveillance/deploy/logs/radix-s3-archive-*.state'

# notifier
ssh e10 'neurosurveillance/deploy/nvr-notify.sh info "test" "reachable"'
```

## Things that are deliberately NOT backed up

- **Frigate rolling segments** (`/srv/frigate/storage`) — regenerable buffer.
- **`node_modules`, Rust `target/`, venvs** — rebuildable.
- **`radiens.log`** — grows to gigabytes, no lasting value.
- **The raw xdat on the bilab NAS** — its archiver retired itself on 2026-08-21 by
  design (`radix-archive-watchdog.sh` stands down permanently once its state file
  reads `COMPLETE`). S3 now covers raw. Re-arming it with
  `rm logs/radix-archive.state` would add a second raw copy; that is a decision,
  not a fix.

## Related

- [[nas-backup]] · [[radix-s3-archive]]
- [[monitoring-setup]] — Netdata, Uptime Kuma, ntfy
- [[nvr-system-overview]] — the whole system

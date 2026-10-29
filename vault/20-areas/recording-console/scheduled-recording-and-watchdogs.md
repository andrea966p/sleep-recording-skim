---
type: procedure
area: recording-console
status: active
tags: [procedure, eeg, allego, recording, automation, monitoring]
created: 2026-08-19
---

# Starting a recording on a schedule, unattended, and knowing it worked

> [!warning] Updated 2026-10-22: script alerts moved from Slack to ntfy on 2026-09-20 (`nvr-notify.sh`), and the repo is now `~/sleep-recording-skim` (the old `~/Monitoring_project` paths on this page were corrected; the 2026-08-19 cron line is shown as an example only). Console runs are the normal way to record since 2026-09-11 and the watchdog arms itself on them since 2026-10-14. [[eeg-recording-console]]

> [!warning] 2026-10-28: the scripts on this page were ported to Allego 4 and `radiens-core`, and take `--ports` (`scheduled-recording.sh`, `qc/start_recording_at.py`). The recording watchdog now checks the growth of each recording port's newest file. The archive, S3 archive and archive-watchdog scripts used to treat an import or gRPC failure as "idle" (fail-open) and now defer. The "radiens client is broken" traps below are `radiens` 4.0.0 facts, and `radiens-core` is now in `/opt/neurosurveillance/venv` (2026-10-28). The old `radiens` 4.0.0 is still installed there but must not be imported: the two cannot load in one process (`duplicate file name common.proto`), and no code imports it any more. The services are not restarted yet, so the cron path still runs the old code until then. [[2026-10-28-per-port-console-port]]

> [!abstract] TL;DR
> How to make Allego start recording at an exact wall-clock time with nobody in the room, and get a
> Slack message telling you whether it actually worked. Used for the first time on 2026-08-19 to
> start eight mice at 09:00 (which is ZT0, lights-on) while everyone was asleep. It worked on the
> first attempt.
> **The whole design rests on one rule: a recording is "started" only when bytes are growing on
> disk. Nothing the software reports is accepted as evidence.**

## Why this is not just "call start_recording"

Two independent traps, both already documented on this rig:

1. **`set_recording_config()` in the radiens client is broken.** `ConfigRecording` has a required
   `recordingType` enum that the library never sets, so the message fails to serialise. The message
   has to be built directly. See `qc/start_recording_at.py`.
2. **`get_status().recording.path` LIES.** It reports the calling process's working directory, not
   the output directory. Trusting it will convince you a recording is running when it is not.

On top of that, this rig has already lost a 72-hour run to a recording that started and then
silently stopped. So "it started" is worth very little on its own.

## The pieces

| File | Role |
|---|---|
| `eeg-emg-analysis/qc/start_recording_at.py` | waits for the target instant, configures, starts, then watches the file grow |
| `neurosurveillance/deploy/scheduled-recording.sh` | preflight, runs the above, retries once, reports to Slack |
| `neurosurveillance/deploy/recording-watchdog-cron.sh` | hourly proof it is still writing; self-disarms on stop |
| `neurosurveillance/deploy/nvr-notify.sh` | Slack posting |

> [!warning] THE INTERPRETER IS NOT THE OBVIOUS ONE
> `radiens` is installed **only** in `/opt/neurosurveillance/venv/bin/python3`.
> It is NOT in `~/eeg-analysis-venv` and NOT in the system python. Using the wrong one fails with
> `ModuleNotFoundError: No module named 'radiens'`. Scripts must also set
> `PYTHONPATH=/home/skimlab/sleep-recording-skim/eeg-emg-analysis` so `core.paths` resolves.

## Scheduling a recording

```bash
crontab -e
```

```
50 8 19 8 * [ "$(date +\%Y-\%m-\%d)" = "2026-08-19" ] && /home/skimlab/sleep-recording-skim/neurosurveillance/deploy/scheduled-recording.sh 09:00:00 >> /home/skimlab/sleep-recording-skim/neurosurveillance/deploy/logs/cron-recording.log 2>&1
```

Three things about that line:

- **Fire it ten minutes EARLY.** The python script does its own waiting and configures the recorder
  ahead of the instant, so the only thing left at the target moment is the start call.
- **The date guard makes it a genuine one-shot.** Cron has no year field, so `50 8 19 8 *` would
  fire again next August. The `[ "$(date ...)" = ... ]` test prevents that.
- **Escape the percent signs as `\%`** in a crontab or cron truncates the line there.

Prefer **09:00 (ZT0)** as the start time for anything running over a day, so light and dark phases
come out equal. The light schedule is 09:00 ON / 21:00 OFF KST, so ZT0 = 09:00. See
[[2026-08-11-a2-control-48h-reference-profile]], where a 48-hour ZT0-to-ZT0
control run replicated on itself across two consecutive days.

## What preflight refuses to do

`scheduled-recording.sh` aborts and shouts on Slack rather than proceeding if:

- the radiens interpreter is missing
- `allegoserver` is not running
- there is less than 150 gigabytes free
- **a recording is ALREADY running** — it will never disturb a run in progress
- Allego cannot be queried at all

## What counts as success

Only this, from the python script's own on-disk check:

```
RECORDING CONFIRMED GROWING
```

It reads the file size, waits 40 seconds, reads it again. If it did not grow, the run is treated as
failed, retried once, and reported as a failure. A first run on 2026-08-19 looked like:

```
[08:50:01] free space: 917 GB
[08:50:04] current recording mode: R_OFF
[09:00:45] SUCCESS file=allego_0__uid0819-09-00-00 rate=2.86 GB/h
```

## The hourly watchdog

`recording-watchdog-cron.sh` runs at five past every hour and compares the file size to the
previous hour.

| Condition | What happens |
|---|---|
| growing | silence |
| mode is `R_ON` but size unchanged for an hour | **Slack alarm — this is the silent-failure signature** |
| mode is no longer `R_ON` | one "recording has stopped" message, then it disarms itself |
| free space under 150 gigabytes | a warning, run continues |

It is armed by `logs/current-recording.txt`, which `scheduled-recording.sh` writes. Deleting that
file disarms it, which is what a clean manual stop does.

## Stopping

You stop the recording yourself in Allego. The watchdog notices within the hour, sends one message
with the final file size, and goes quiet. No action needed.

## Still open

- **The live-start path has never been tested other than by using it for real.** A rehearsal was
  blocked as a real-world action on live-animal equipment, so the components were each verified
  separately (interpreter, allegoserver, status query, `ConfigRecording` construction, disk space,
  and both output-parsing paths) and the first genuine execution was the 09:00 run itself. It
  worked, but be aware the dress rehearsal never happened.
- **Recording start is not integrated with the session daemon**, which still has
  `sessions.auto_start: false`. This is a parallel path, deliberately.
- **No video.** Cameras were removed 2026-08-04, so these are electrophysiology-only runs.

Related: [[raw-recording-archive-to-nas]] ·
[[CANONICAL-allego-channel-selection]] ·
[[eeg-artefact-and-railing-rejection-policy]]

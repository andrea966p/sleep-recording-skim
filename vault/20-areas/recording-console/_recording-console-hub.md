---
type: hub
area: recording-console
status: active
created: 2026-10-22
summary: "The EEG recording console at 127.0.0.1:8600: runs, scheduling, watchdogs, stripping, NAS upload, naming and the inventory of recordings"
tags: [hub, recording, console]
---

# Recording console

> [!abstract] What this is
> The local service (`eeg-recorder`, `http://127.0.0.1:8600`) that starts and stops recordings, schedules them, strips and uploads the result to the SKIM NAS, and records who recorded which mouse. It is the normal way to record since 2026-09-11.
> It covers runs, scheduling, the watchdogs, stripping, uploads, naming and the inventory; the Allego software itself is in [[_allego-hub]], and the older crontab path is [[scheduled-recording-and-watchdogs]].

## Current state
- 2026-10-23: Andrea: recording stays global; what matters is that several people can queue schedules for different dates, which the console already accepts. Overlap refusal at booking is the open item. [[2026-10-23]]
- 2026-10-15: ahyeon's 3-mouse run was lost to hardware (port B dropped off the scan the night before) and the console had started without re-checking ports; since then a start with a missing port goes ahead, records the live enumeration, shows a red tag and sends an ntfy alert; the service has been running since 2026-10-15 09:56 KST, after the last edit of `scheduler.py` (09:45), so the check is live. [[2026-10-15]] [[eeg-recording-console]]
- 2026-10-14: the console gained a cancel button for reservations, the hourly watchdog arms itself on console runs, the strip passes the GPIO flag, and the unipolar map was corrected; a 10-minute scheduled rehearsal ran end to end. Overlapping reservations are still accepted at creation. [[2026-10-14]]
- 2026-09-30: output is one CSV per mouse in `02_Data_Sleep`; the first real run from the UI reached `DONE` unattended in 20 s after stop. [[2026-09-29]] [[per-mouse-csv-format]]
- 2026-09-23: a recording has one canonical name, `allego_N__uidMMDD-HH-MM-SS`, and the inventory of every recording is kept in one note. [[CANONICAL-recording-naming-and-inventory]]
- 2026-09-17: a 28 h unattended console run (schedule, stop, strip, verify, upload) worked end to end on live animals. [[2026-09-17-W-SL-28h-run]]
- 2026-09-11: the console became the normal way to record; its first real run verified the whole chain and exposed three retry defects, since fixed. [[eeg-recording-console]] [[recording-console-retry-was-a-dead-end]]

## Start here
- [[eeg-recording-console]]: set up a run, leave the room, find the data
- [[starting-the-rig-after-a-restart]]: one command says what is up
- [[pipeline-architecture]]: every program, what fires it, every failsafe
- [[rig-layout-and-recording-settings]]: splitters, headstages and recording settings
- [[CANONICAL-recording-naming-and-inventory]]: names and the inventory of recordings

## Rules that must not be broken
- 🛑 Do not strip or run any heavy disk job while the rig is recording; a console run strips itself on stop, and `RIG BUSY` in a dry run means stop. [[xdat-channel-stripping]]
- A recording is confirmed writing only when bytes grow on disk over a window longer than 35 s; the file size reads 0 for about 30 s after a healthy start, and the 40 s window in `start_recording_at.py` must not be shortened. [[2026-09-11-allego-control-bench-test]]
- Recording is global: one run owns the rig and there is no per-port recording [[multi-user-independent-recording-schedules]]; there is no default owner in the dropdown [[eeg-recording-console]].
- Check Allego mode (`XDAQ_ONE_REC`) and the measured rate before recording; the console checks only the label. [[allego-stream-30x-rate-label-lies]]
- Each animal needs its own ID (case does not make one different), or the run is unjudgeable. [[eeg-recording-console]]
- The QC bundle is a precondition of stripping: stripping deletes the wire-free floor. [[pipeline-architecture]]
- A recording started by hand in Allego does not arm the watchdog; console runs do since 2026-10-14. [[2026-08-19]]
- `radiens` exists only in `/opt/neurosurveillance/venv/bin/python3`, and `get_status().recording.path` lies. [[scheduled-recording-and-watchdogs]]
- Never restart `eeg-recorder` during a live recording without a reason; check `uptime -s` before believing "the PC crashed". [[starting-the-rig-after-a-restart]]
- Always write a recording as `allego_N__uidMMDD-HH-MM-SS`; match NAS folders by `allego_base`, never by date. [[CANONICAL-recording-naming-and-inventory]]

## Open items
- [ ] Refuse overlapping reservations at creation (the later one fails at its own start). Andrea, 2026-10-23: several people must be able to schedule their runs for following dates; that already works (any number of SCHEDULED runs is accepted), this item only makes an overlap fail when it is booked. [[2026-10-14]] [[2026-10-23]]
- [ ] `UPLOAD_PENDING` had no periodic retry when last checked; it waits for a restart or the retry button. [[2026-09-29]]
- [ ] Whether the Radiens reader accepts a stripped file is unproven. [[eeg-recording-console]]
- [ ] A measured-rate check in the pre-flight is not built. [[allego-stream-30x-rate-label-lies]]

## Everything here
![[area.base]]

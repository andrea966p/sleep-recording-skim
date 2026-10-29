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
- 2026-10-28: the console was ported to Allego 4 and per-port recording: one run per port, several runs at once, an overlapping booking is refused (409), impedance and restart need the whole rig idle, files are `allego_port<X>_<N>__uid...`. An isolated test console recorded ports A and B at once and both runs reached `DONE`. The review fixes are done, and since the restart of `eeg-recorder` and `neurosurveillance-session` on 2026-10-29 09:15 KST production runs the new code (console healthy, daemon connected, old-client token errors stopped). This replaces Andrea's 2026-10-23 "recording stays global". [[2026-10-28-per-port-console-port]] [[2026-10-28-per-port-recording-bench-test]] [[2026-10-23]]
- 2026-10-15: ahyeon's 3-mouse run was lost to hardware (port B dropped off the scan the night before) and the console had started without re-checking ports; since then a start with a missing port goes ahead, records the live enumeration, shows a red tag and sends an ntfy alert; the service has been running since 2026-10-15 09:56 KST, after the last edit of `scheduler.py` (09:45), so the check is live. [[2026-10-15]] [[eeg-recording-console]]
- 2026-10-14: the console gained a cancel button for reservations, the hourly watchdog arms itself on console runs, the strip passes the GPIO flag, and the unipolar map was corrected; a 10-minute scheduled rehearsal ran end to end. Overlapping reservations were still accepted at creation then; they are refused at booking since 2026-10-28. [[2026-10-14]]
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
- 🛑 Do not strip or run any heavy disk job while the rig is recording; a console run strips itself on stop, and `RIG BUSY` in a dry run means stop. [[xdat-channel-stripping]] One exception (Andrea, 2026-10-29): the console's own QC and strip of a per-port run may run while another port records, once that run's own files have stopped growing; the export, manual strips and the archive jobs still wait. [[2026-10-28-per-port-console-port]]
- A recording is confirmed writing only when bytes grow on disk over a window longer than 35 s; the file size reads 0 for about 30 s after a healthy start, and the 40 s window in `start_recording_at.py` must not be shortened. [[2026-09-11-allego-control-bench-test]]
- One run per port: a run owns only its ports, a stop names its port, and impedance and an Allego restart need the whole rig idle (no port recording, no run starting or stopping, no start due within 10 min). [[2026-10-28-per-port-console-port]] There is no default owner in the dropdown [[eeg-recording-console]].
- After every Allego launch or restart, enforce mode `XDAQ_CORE_REC`, 1000 Hz and `split_files_by_port`, and rescan the ports after a rate change; the shared recording settings change only when no port records. The ported console enforces and reports the measured rate. [[2026-10-28-allegoserver-death-and-fresh-launch-defaults]] [[allego-stream-30x-rate-label-lies]]
- Each animal needs its own ID (case does not make one different), or the run is unjudgeable. [[eeg-recording-console]]
- The QC bundle is a precondition of stripping: stripping deletes the wire-free floor. [[pipeline-architecture]]
- A recording started by hand in Allego does not arm the watchdog; console runs do since 2026-10-14. [[2026-08-19]]
- `radiens-core` lives in `/opt/neurosurveillance/venv/bin/python3`; the old `radiens` 4.0.0 is still installed there and must not be imported (no code does). Find a port's file by its name pattern and bytes on disk, never from `active_filename` or `get_status().recording.path`. [[scheduled-recording-and-watchdogs]] [[2026-10-28-per-port-console-port]]
- Never restart `eeg-recorder` during a live recording without a reason; check `uptime -s` before believing "the PC crashed". [[starting-the-rig-after-a-restart]]
- Always write a recording as `allego_port<X>_<N>__uidMMDD-HH-MM-SS` (the older `allego_N__uid...` form is still parsed); match NAS folders by `allego_base`, never by date. [[CANONICAL-recording-naming-and-inventory]] [[2026-10-28-per-port-console-port]]

## Open items
- [x] 2026-10-28: refuse overlapping reservations at creation: done in the ported console (HTTP 409 when the ports overlap in time); live since 2026-10-29 09:15 KST. [[2026-10-28-per-port-console-port]] [[2026-10-14]] [[2026-10-23]]
- [ ] `UPLOAD_PENDING` had no periodic retry when last checked; it waits for a restart or the retry button. [[2026-09-29]]
- [ ] Whether the Radiens reader accepts a stripped file is unproven. [[eeg-recording-console]]
- [x] 2026-10-28: the ported console enforces 1000 Hz and the split and reports the measured rate; live since 2026-10-29 09:15 KST. [[2026-10-28-per-port-console-port]] [[allego-stream-30x-rate-label-lies]]
- [x] 2026-10-29 09:15 KST: `eeg-recorder` and `neurosurveillance-session` restarted by Andrea on the new code. [[2026-10-28-per-port-console-port]] [[2026-10-29]]
- [x] 2026-10-29: Andrea: QC and strip of a per-port run may run while another port records; the export still waits for an idle rig. [[2026-10-28-per-port-console-port]]
- [ ] Splitter ports (64 channels) in per-port files are untested. [[2026-10-28-per-port-console-port]]
- [ ] A 24 to 72 h per-port run with several owners has not been run. [[2026-10-28-per-port-recording-bench-test]]
- [ ] Delete the stale `neurosurveillance-system/session-daemon` copy (it still imports the old `radiens`). [[2026-10-28-per-port-console-port]]
- [ ] The cause of the 2026-10-28 `allegoserver` death is unknown. [[2026-10-28-allegoserver-death-and-fresh-launch-defaults]]

## Everything here
![[area.base]]

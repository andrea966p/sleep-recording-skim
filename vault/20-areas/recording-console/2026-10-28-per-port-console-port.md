---
type: reference
area: recording-console
status: active
created: 2026-10-28
summary: "The recording console ported to Allego 4 and radiens-core: one run per port, several runs at once, overlapping bookings refused (409), rig-wide impedance and restart only when idle, per-port files and post-processing; tested end to end on an isolated console (port 8601); in production since 2026-10-29"
tags: [recording-console, allego, radiens-core, per-port]
---

# The console ported to per-port recording (2026-10-28)

> [!abstract] TL;DR
> - The console (`eeg-recorder`) now talks to Allego 4.1.2 through `radiens-core` 0.1.2. A run owns **ports**, not the whole rig, so several people can record at the same time on different ports.
> - Booking a run whose ports overlap another booked or active run in time is **refused with HTTP 409**. This closes the open item "refuse overlapping reservations at creation".
> - An isolated test console on port 8601 recorded ports A and B at the same time, stopped A while B kept going, and both runs reached `DONE` unattended (2026-10-28, 19:02 to 19:09 KST).
> - **In production since 2026-10-29 09:15 KST**, when Andrea restarted `eeg-recorder` and `neurosurveillance-session`. After the restart the console reported healthy (`XDAQ_CORE_REC`, 1000 Hz, split on), the session daemon connected (`Initial Radiens state: R_OFF`), and the old client's `VerifyJWT ... token is expired` errors stopped (0 lines, `radiens.log` 0 bytes growth in 65 s).
> - Why this is possible at all: [[2026-10-28-per-port-recording-bench-test]]. It retracts "recording is global", which was true only for radiens 4.0.0 on Allego 3.11.3.

## What the console does now

### Runs and ports

- One run per **port**. Several runs can record at once on disjoint ports.
- The Rig panel and the Ports panel (one card per port) show channels, recording state, owner, file, bytes, next reservation and an impedance button. Each active run has its own Stop, and that Stop stops only that run's ports.
- A stop always names its port. `stop_recording()` without a port would stop everyone, so the console never calls it that way ([[2026-10-28-per-port-recording-bench-test]]).
- `/api/state` carries per-port state, `active_runs` and `rig_busy`. New endpoints: `GET /api/ports`, `GET` and `POST /api/ports/<P>/impedance`, `POST /api/allego/restart`. A run carries its `ports` and `port_files`.

### Booking refusal

- Booking a run whose ports overlap another booked or active run in time is refused with HTTP 409. The web page shows the conflicting run.
- Andrea's earlier rule still holds: any number of scheduled runs is fine, as long as their ports do not overlap in time ([[2026-10-23]]).

### Rig-wide operations

Impedance (per port) and an Allego restart (in the same mode only) act on the whole box, so they need:

- no port recording,
- no run starting, recording or stopping,
- no scheduled start due within 10 minutes.

A single rig lock is shared by starts, stops, impedance and restart. The restart button asks for confirmation. Nothing licence-related was touched: no sign-in, plan or upgrade call, and the restart keeps the current mode.

### Shared settings

- Allego keeps one recording configuration for all ports: sample rate, folder, base name and split. It can be changed only when no port records.
- The console enforces `split_files_by_port=True` and 1000 Hz, and checks the expected mode, which is **`XDAQ_CORE_REC`** on Allego 4 (it was `XDAQ_ONE_REC` on Allego 3.11.3).
- It now reports the **measured rate** (stream time against wall clock, shown as a ratio), not only the label. A start measures it for about 5 s when it is not yet known and refuses outside 0.9 to 1.1x. See [[allego-stream-30x-rate-label-lies]].

### File names

The canonical name is now `allego_port<X>_<N>__uid<MMDD-HH-MM-SS>`, for example `allego_portA_0__uid1028-19-02-40`. The old `allego_<N>__uid...` names are still parsed, so old runs and the inventory still work ([[CANONICAL-recording-naming-and-inventory]]).

### Post-processing per port

- Each port file goes through the QC bundle, the strip, the per-mouse CSV and the NAS upload on its own. Old combined-file runs are unchanged ([[pipeline-architecture]], [[xdat-channel-stripping]], [[per-mouse-csv-format]]).
- Floors are now computed per port file, so the floor statistics on a new card are not directly comparable with the cards of old combined files.
- Allego 4 writes `start_time` with `+09:00`, where old files had `Z`. The CSV exporter converts it to UTC and keeps the raw text as `startTime_as_written`.
- 🔵 Andrea, 2026-10-29: the **QC bundle and the strip of a per-port run may run while another port is recording**, because per-port files are about 7.5 times smaller than the old combined file. They still wait until the run's own files have stopped growing, so a file is never read while it is written. The per-mouse CSV export still waits for an idle rig, and runs made before per-port recording (one combined file) keep the old rule. A run that waits alerts after about 12 h.

### Other programs ported

- The session daemon (`radiens_poller.py`) uses `radiens-core`. The global `record_mode` (ON if any port records) still triggers video sessions, and a new `port_modes` field carries the per-port modes. The cameras are disconnected, so no video session follows today.
- The recording watchdog checks the growth of each recording port's newest file.
- The archive, S3 archive and archive-watchdog scripts asked "is it recording?" in a **fail-open** way: an import error or a gRPC failure read as idle, so heavy disk work could start. They now defer instead.
- `scheduled-recording.sh` and `qc/start_recording_at.py` take `--ports` ([[scheduled-recording-and-watchdogs]]).
- The manual QC scripts were ported (`record_block`, `grab_stream`, `preflight_grab`, `remap_channels`, `allego_signal_metrics`, `sweep_block_ports`, `sweep_block_all_ports`). Signal metrics from `get_kpi_metrics` in STREAM mode are 2 s exponential moving average envelopes, so they are not comparable with the numbers from radiens 4.0.0.

### The Python package

`radiens-core` 0.1.2 is installed in `/opt/neurosurveillance/venv` (2026-10-28), next to `radiens` 4.0.0. The two cannot be imported in one process (`TypeError: Couldn't build proto file into descriptor pool: duplicate file name common.proto`). No code imports the old package any more, and it must not be imported. Details of the API: [[radiens-api-reference]].

## Live end-to-end test (isolated console, port 8601)

- When: 2026-10-28, 19:02 to 19:09 KST. Outputs under `~/radix/port-tests/console`, which is not a source of the S3 archive or the NAS backup. The test console had its own state database and upload manifest, so the production manifest and QC cache were not touched.
- Run `be311234a94d` on port A (19:02:40 to about 19:06) and run `c20f388f6b60` on port B (19:03:38 to about 19:07) recorded at the same time into `allego_portA_0__uid1028-19-02-40` and `allego_portB_0__uid1028-19-03-38`.
- A was stopped while B kept recording.
- An overlapping booking on port A was refused (409). Impedance and restart during the runs were refused (409).
- Both runs went through QC, strip, export and NAS upload to `DONE`, unattended. The NAS CSVs have 211,328 and 210,176 data rows, which equal the file durations (211.328 s and 210.176 s).
- The test uploads went to `02_Data_Sleep/andrea/PORTTESTA` and `PORTTESTB` and were deleted after the tests.

### Second live test, on the fixed code (21:23 to 21:30 KST)

- Run `d9a20a1943b6` held two ports, C and D (mice `PTC1`, `PTD1`), scheduled from 21:23:30 to 21:27:30. Run `ec47a21d83ea` on port A (mouse `PTA2`) was started with Start now and stopped by hand at about 21:24:40.
- The hand stop stopped port A only. C and D kept recording, and streaming stayed on.
- A draft with no stop time on port C was refused at booking (409), because an open-ended run overlaps everything after its start.
- Run `ec47a21d83ea` waited in `STOPPED` while C and D were still recording (`deferred_since` set), then went through strip, export and upload once the rig was idle. Both runs reached `DONE`; the NAS CSVs had 213,120 rows per mouse for C and D and 66,560 rows for A.

### Cleanup

- The four NAS test folders (`02_Data_Sleep/andrea/PORTTESTA`, `PORTTESTA2`, `PORTTESTB`, `PORTTESTCD`) were deleted. The NAS recycle bin (`#recycle`) is not readable from the rig account, so a NAS admin has to empty it if the copies there should go too.
- `~/radix/port-tests` (193 MB: bench files and the test console's raw, stripped, per-mouse, QC and state folders) was moved to `~/.local/share/Trash`. It frees nothing until the trash is emptied.
- No test file was ever written under `~/radix/data` or `~/radix/stripped`, so nothing went to S3.
- Allego's recording configuration was reset to `~/radix/data`, base name `allego`, split on.
- Console API checks the same evening: impedance on port A took 29.8 s and returned 32 channels (`A/1` to `A/32`, no splitter on today); one `get_intan_impedance` call returns all 128 channels and the console keeps the port it was asked for. Labels come from the site numbers in the channel metadata. A restart in the current mode took 38.8 s and ended in `XDAQ_CORE_REC`, 1000 Hz, split on, stream 0.998x.

## The review round

Three reviewers (Opus, Sonnet and Haiku) went through the port. They found the following, and every item was fixed the same evening with a regression test (182 console tests, 59 pytest and 63 analysis-script tests pass). A second live test then ran on the fixed code (below):

- a double-start race,
- a shared gRPC pool closed by one thread,
- `FAILED_STOP` not retryable,
- the boot rewind orphaning a port that had already started,
- the watchdog calling a run stopped after one gRPC blip,
- stored cross-site scripting in the web page,
- QC and strip idle checks,
- a restarted port's second file silently dropped,
- a +9 h error in three QC scripts when given `+09:00` times.

## What is not deployed or not tested yet

- Production restart done 2026-10-29 09:15 KST. The code is not committed yet.
- The backend review fixes are done: a double-start guard, the shared gRPC client is no longer closed, `FAILED_STOP` can be retried, startup adopts a port that really started instead of orphaning it, start measures the rate when it is unknown, a port that is not growing raises an alert, and stop requires explicit ports. They are not in production until the restart.
- Splitter ports (64 channels) in per-port files are untested.
- A 24 to 72 h per-port run with several owners has not been run ([[2026-10-28-per-port-recording-bench-test]]).
- The stale copy `neurosurveillance-system/session-daemon` still imports the old `radiens`. It is not deployed.
- Allego itself died once the same evening with no log line: [[2026-10-28-allegoserver-death-and-fresh-launch-defaults]].

## Still open

- [x] 2026-10-29: Andrea decided that QC and strip of a per-port run may run while another port records (export still waits). Code: `postprocess.may_share_disk`, `strip_channels.py --ignore-other-recordings`, `rig_is_busy(own_only=True)`; tests added. Live after the production restart.
- [x] 2026-10-29 09:15 KST: both services restarted in production.
- [ ] Delete the stale `neurosurveillance-system` copy of the session daemon.
- [ ] Run a 24 to 72 h per-port recording with several owners.
- [ ] Test splitter ports in per-port files.

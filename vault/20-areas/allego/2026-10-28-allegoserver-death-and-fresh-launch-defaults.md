---
type: incident
area: allego
status: active
created: 2026-10-28
summary: "2026-10-28: allegoserver (Allego 4.1.2) died at 18:46 with no trace, cause unknown; the old clients spammed token errors; a fresh launch came up at 30 kHz with split off; a rate change without a rescan leaves a dead stream (fix: scan_ports); recorded band-pass tracked in each file's provenance"
tags: [allego, incident, radiens-core, launch-defaults]
---

# 2026-10-28: allegoserver death and the fresh-launch defaults

> [!abstract] TL;DR
> - **Cause of the death is unknown.** `allegoserver` died between 18:46:53 and 18:47:00 KST with no log line, no core dump and no kernel message, during read-only calls. Andrea relaunched Allego.
> - **A fresh launch is not safe to record on.** It came up at 30000 Hz with `split_files_by_port=False`. Allego keeps neither the rate nor the split across launches. An earlier launch the same morning came up at 625 Hz.
> - **After any rate change, rescan before streaming.** Changing the rate and then streaming left a dead stream. The fix is: stop streaming, `scan_ports()`, start streaming.
> - Related: [[2026-10-28-per-port-recording-bench-test]], [[2026-10-28-per-port-console-port]], [[2026-10-28-radiens-4-tiers-and-legacy-licence]].

## The death at 18:46

- Time: 18:46:53 to 18:47:00 KST. Allego 4.1.2 on `e10ubuntu`, no recording running.
- Evidence: no line in the `allegoserver` log, no core dump, no kernel message.
- What was happening: only read-only calls (`get_status`, `get_config`, `get_recording_config`, `get_channel_metadata`). The last burst in the server log was `SpikeSorterGetParam`, `GetStimStep`, `GetStimParams`, `GetDSPGroup` and `GetConfigSampFreq`, which looks like the Allego GUI loading a panel.
- Videre was closed at 18:47:48, after the death, so closing Videre did not cause it.
- Afterwards the Allego GUI logged `ECONNREFUSED 127.0.0.1:50051` on every poll, which showed up as error notifications. Andrea relaunched Allego.
- Cause: unknown. Compare the Mesa crash of 2026-08-24 ([[allego-mesa-gpu-crash-and-log-storm]]) and the orphan case ([[allego-orphaned-server-blocks-the-rig]]); nothing here says which, if either, applies.

## The token spam from the old clients

Since the Allego 4 install, the old clients on `radiens` 4.0.0 kept calling the new server: the old console (PID 4014272, every 2 s while its page is open) and the session daemon (every 60 s). Each call produced `VerifyJWT: token rejected ... cognitoauth: token is expired` in `~/.local/state/radiens/logs/allegoserver.log` and grew `/opt/neurosurveillance/radiens.log` to 3.2 GB. The spam stops when the services run the new `radiens-core` code, which needs the production restart ([[2026-10-28-per-port-console-port]]).

## Fresh-launch defaults

- A fresh launch of Allego 4.1.2 came up at **30000 Hz** with `split_files_by_port=False`. The earlier launch that morning came up at 625 Hz ([[2026-10-28-radiens-4-tiers-and-legacy-licence]]).
- Rule: after every launch, set 1000 Hz and the split, then compare the measured stream rate with wall clock (about 1.0x). See [[allego-stream-30x-rate-label-lies]]. The console now enforces 1000 Hz and the split, and reports the measured rate.
- `restart()` with the current mode, through the console API, took 38.8 s and ended in `XDAQ_CORE_REC`, 1000 Hz, split on, measured 0.998x. The bench test saw that a plain `restart()` can reset the rate to 30000 Hz, so check the rate after every restart.

## A dead stream after a rate change

- What happened: `update_core_config(samp_freq=1000)` followed by `start_streaming` left the stream dead. `primary_cache_t_range` stayed `[0.0, 0.0]`, and `allegoserver` logged `raklib::getSignals API error: Too few amp signals allocated in stream_array` every 200 ms.
- Fix: stop streaming, `scan_ports()`, start streaming. The stream then measured 0.998x.
- Rule: after any rate change, call `scan_ports()` before streaming.

## Band-pass in the file provenance

The hardware band-pass is written into each file's `.xdat.json` provenance (`BANDPASS`).

- The bench junk files recorded on the afternoon launch, where the rate had been changed without a rescan, carry `fs 625` and **1.20 to 296.8 Hz**.
- After the rescan sequence, files carry `fs 1000` and **1.10 to 475.17 Hz**, the same as the old recordings (the vault figure 1.10 to 475 Hz, [[2026-08-07-rig-specification-and-analysis-method]]).
- So check the `BANDPASS` entry of a new file once after any launch or rate change. Only the bench junk files were affected.

## Videre and the old Curate libraries

Videre's log shows that it launches with `LD_LIBRARY_PATH=/opt/curate/resources/radix/allegoserver`, which is the old Curate 1.9.1 install. This was not investigated.

## Side note: two old KPI files rewritten

Two old `.kpi` files in `~/radix/data` (`allego_0__uid0921-00-17-34` and `allego_0__uid1020-09-00-07`) were rewritten after 18:00, probably by Videre computing KPIs when they were opened. They are not test data.

## Still open

- [ ] Find out why `allegoserver` died at 18:46 (cause unknown).
- [ ] Look at why Videre loads the Curate 1.9.1 library path.

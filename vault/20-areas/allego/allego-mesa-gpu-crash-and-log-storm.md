---
type: incident
area: allego
status: active
status-note: "the workaround (--disable-gpu) was dropped on 2026-09-16, so the crash risk is open again"
created: 2026-08-24
tags: [allego, gpu, mesa, incident, log-storm]
---

# 2026-08-24: Allego froze, then crashed and took the recording with it

> [!abstract] TL;DR
> **What broke.** The Allego GUI froze, then the whole app died at 13.59 min of a planned 60 min recording. Two independent faults stacked: a reproducible Mesa crash in the GPU process, and a multi-GB log storm from `autoScanWorker`.
> **Fix.** `--disable-gpu` stopped the crash, but it was removed again on 2026-09-16 because it blanks the Monitor ([[allego-blank-monitor-canvas-texture-limit]]). The log storm has a safe truncate.

> [!info] Promoted from a Claude memory file on 2026-10-22
> Written from the memory note `allego-mesa-gpu-crash-and-log-storm` (saved 2026-08-24). The recording that followed the crash is [[2026-08-24-S-SD-first-hour-screen]], which quarantines the crashed attempt; no other vault note held the crash facts.

> [!warning] Status of the workaround
> Launching with `--disable-gpu` is no longer the standing instruction. See [[allego-blank-monitor-canvas-texture-limit]]. Procedures that still say "use `--disable-gpu`" are stale; the open question is logged in `_meta/contradictions/allego-console`.

## Fault 1: the GPU process crashes in Mesa, reproducibly

```
17:10:43 traps: allego[4017855] trap divide error ip:7b1ddb87d167
         in libgallium-25.2.8-0ubuntu0.24.04.2.so
17:10:45 ERROR:gpu_process_host.cc(982) GPU process exited unexpectedly: exit_code=136
```

`exit_code=136` is 128+8, SIGFPE. The crash dump lands in `/var/crash/_opt_allego_allego.1000.crash`. It was not a one-off: a clean relaunch crashed the same way twice more (33 s and about 2 min after launch). Chromium respawns the GPU process each time, so the app looks alive while the renderer falls back to software raster.

✅ **Workaround that worked: launch `/opt/allego/allego --disable-gpu`.** After that: zero divide errors, the GPU process and renderer kept the same PIDs, the renderer used 402 MB and 7-14 % CPU against 6.3 GB and 178 % CPU in the wedged session, and package temperature fell from 67 to 60 °C. Launch it detached with the desktop session environment:

```bash
DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus XDG_RUNTIME_DIR=/run/user/1000 \
  setsid /opt/allego/allego --disable-gpu > /tmp/allego.log 2>&1 < /dev/null &
```

## Fault 2: `autoScanWorker` log storm, 6.5 GB in one file

```
level=error msg="autoScanWorker:UpdateConnectionState. Will resume scanning"
error="Backbone::Can't update connection state while streaming" module=backbone
```

Allego's own auto-scan fights the stream and retries in a tight loop, emitting thousands of identical lines within a second. `~/.local/state/radiens/logs/allego-ui.log` reached 6.97 GB, unrotated (the whole directory was 9.6 GB; the other 3.0 GB is rotated `.gz` back to February). The renderer ingests every line, which is the other half of the 6.3 GB RSS.

🔧 `truncate -s 0 ~/.local/state/radiens/logs/allego-ui.log` reclaimed 6.5 GB and is safe while Allego runs. Worth adding to the Kontex question batch next to the impedance-polarity and spike-sorter-filter questions: both the Mesa crash and this retry loop ([[2026-07-29-kontex-kc-call-prep-rig-finalization]]).

## What survived and what did not

✅ **A frozen GUI does not corrupt or interrupt the recording.** Measured during the freeze: gRPC answered instantly, mode `R_ON`, `dur_sec` advanced 4.0 s per 4.0 s, `hw_mem_level` 0.0001-0.0005 (buffer empty), bytes on disk at 97.6 % of wall clock and catching up at 151 % write rate. The signal was continuous: A/33 rms 104.3, 105.7, 108.5, 109.5 µV from t=60 s to t=775 s, zero all-zero rows. 🔑 **Judge a recording by bytes on disk and by the rms of a known channel across the event, never by whether the window responds.**

🔴 **When the app crashed wholesale, the recording stopped.** Closing the GUI leaves `allegoserver` alive (confirmed again: a `pkill` of the Electron GUI left allegoserver and pybridge running and port 50051 open, see [[allegoserver-runaway-thread-thermal]]), **but an allegoserver death ends the recording.** `R_OFF` was never issued; the file simply stops.

## Operational gotchas found

🔴 **`pkill -f '/opt/allego/allego'` kills your own shell.** The Bash-tool wrapper's command line contains the pattern, so the tool call dies with exit 144 and the relaunch never runs. Kill Allego by explicit PID. The same trap hits `pgrep -f rec1h.py`. See [[allego-orphaned-server-blocks-the-rig]].

⚠️ **A fresh Allego launch does not come up in the rig's configuration.** After relaunch, `sample_freq` was 30000.0 Hz (the rig runs 1000 Hz) and `system_mode` was `SMARTBOX_PRO` (the rig is `XDAQ_ONE_REC`), and the mode differed between two launches minutes apart. Always re-check `get_status()` for fs and system_mode before recording. Even the label is not enough: [[allego-stream-30x-rate-label-lies]].

🔑 **Impedance cannot be measured while acquiring.** `GetIntanImpedance` fails with `raklib set_status():: Z_measure attempted during data acq`. Streaming off is the only valid mode, so an impedance sweep can never be a within-recording control.

Related: [[starting-the-rig-after-a-restart]] · [[eeg-recording-console]]

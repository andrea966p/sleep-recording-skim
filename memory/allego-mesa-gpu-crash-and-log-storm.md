---
name: allego-mesa-gpu-crash-and-log-storm
description: "2026-08-24: Allego's GUI froze and then crashed the whole app mid-recording, caused by a reproducible Mesa divide-by-zero in its GPU process plus a multi-GB autoScanWorker log storm; --disable-gpu is the workaround"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-24T08:46:41.218Z
---

🔴⭐⭐ **2026-08-24: the Allego GUI froze, then the WHOLE APP DIED and took the recording with it
at 13.59 min of a planned 60 min.** Two independent faults stacked.

## FAULT 1 — the GPU process crashes in Mesa, REPRODUCIBLY
```
17:10:43 traps: allego[4017855] trap divide error ip:7b1ddb87d167
         in libgallium-25.2.8-0ubuntu0.24.04.2.so
17:10:45 ERROR:gpu_process_host.cc(982) GPU process exited unexpectedly: exit_code=136
```
`exit_code=136` = 128+8 = SIGFPE. Crash dump lands in `/var/crash/_opt_allego_allego.1000.crash`.
⭐ **NOT a one-off.** A clean relaunch crashed the same way twice more (33 s and ~2 min after
launch). Chromium respawns the GPU process each time, so the app looks alive while the renderer
falls back to software raster.

✅ **WORKAROUND THAT WORKED: launch `/opt/allego/allego --disable-gpu`.** After that: zero divide
errors, GPU process and renderer keep the SAME PIDs (no respawn), renderer **402 MB / 7-14% CPU**
against **6.3 GB / 178% CPU** in the wedged session, package temp 67 → 60 °C.
Launch it detached with the desktop session env:
```bash
DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus XDG_RUNTIME_DIR=/run/user/1000 \
  setsid /opt/allego/allego --disable-gpu > /tmp/allego.log 2>&1 < /dev/null &
```

## FAULT 2 — `autoScanWorker` log storm, 6.5 GB in one file
```
level=error msg="autoScanWorker:UpdateConnectionState. Will resume scanning"
error="Backbone::Can't update connection state while streaming" module=backbone
```
Allego's own auto-scan fights the stream and retries in a tight loop, emitting **thousands of
identical lines within a single second**. `~/.local/state/radiens/logs/allego-ui.log` reached
**6.97 GB, UNROTATED** (the whole dir was 9.6 GB; the other 3.0 GB is rotated `.gz` back to
February). The renderer ingests every line, which is the other half of the 6.3 GB RSS.
🔧 `truncate -s 0 ~/.local/state/radiens/logs/allego-ui.log` — reclaimed 6.5 GB, safe while running.
📤 **Worth adding to the Kontex batch** next to Q12/Q13: both the Mesa crash and this retry loop.

## WHAT SURVIVED AND WHAT DID NOT — the useful part
✅ **A frozen GUI does NOT corrupt or interrupt the recording.** Measured DURING the freeze:
gRPC answered instantly, `R_ON`, `dur_sec` advanced 4.0 s per 4.0 s, `hw_mem_level` 0.0001-0.0005
(buffer empty), bytes on disk at 97.6% of wall-clock and catching up at 151% write rate. The signal
itself was continuous — A/33 rms 104.3 → 105.7 → 108.5 → 109.5 µV across t=60 s to t=775 s, **zero
all-zero rows**. 🔑 **Judge a recording by bytes on disk and by rms of a known channel across the
event, never by whether the window responds.**
🔴 **But when the APP crashed wholesale, the recording stopped.** This extends
[[allegoserver-runaway-thread-thermal]]: closing the GUI leaves `allegoserver` alive (confirmed
again — a `pkill` of the Electron GUI left allegoserver + pybridge running and port 50051 open),
**but an allegoserver death ends the recording.** R_OFF was never issued; the file simply stops.

## OPERATIONAL GOTCHAS FOUND
🔴 **`pkill -f '/opt/allego/allego'` KILLS YOUR OWN SHELL** — the Bash-tool wrapper's command line
contains the pattern, so the tool call dies with exit 144 and the relaunch never runs. **Kill
Allego by explicit PID.** Same trap as `pgrep -f rec1h.py` matching the wrapper instead of the
python process.
⚠️ **A FRESH Allego launch does NOT come up in the rig's configuration.** After relaunch:
`sample_freq = 30000.0 Hz` (the rig runs **1000 Hz**) and `system_mode = SMARTBOX_PRO` (the rig is
**XDAQ_ONE_REC**) — and the mode differed between two launches minutes apart. **Always re-check
`get_status()` for fs and system_mode before recording.**
🔑 **Impedance cannot be measured while acquiring:** `GetIntanImpedance` fails with
`raklib set_status():: Z_measure attempted during data acq`. Streaming-off is the only valid mode,
so an impedance sweep can never be a within-recording control.

Related: [[allegoserver-runaway-thread-thermal]] · [[eeg-rig-current-state]] ·
[[recording-2026-08-18-eight-new-mice]]

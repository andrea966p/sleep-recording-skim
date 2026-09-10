---
tags: [troubleshooting, incident, frigate, neurosurveillance, daemon, export]
date: 2026-04-08
severity: medium
status: partially-resolved
affected: [e10ubuntu, frigate, neurosurveillance-session-daemon]
---

## Summary
- **Date/Time:** 2026-04-08 ~18:00–18:56 JST
- **Severity:** Medium — two distinct issues around Frigate recordings and the manual-session auto-export path
- **Status:** Workaround applied; root causes still open

Two related problems surfaced:
1. Stopping Frigate recordings manually for `pi_cam_2` / `pi_cam_3` at 18:02 produced **no auto-export** because the daemon never saw the ON-edge.
2. A later test with manual short recordings on `pi_cam_0` / `pi_cam_1` / `pi_cam_2` produced exports for cam_1 and cam_2, but cam_0's Frigate export hung `in_progress=true` forever with no ffmpeg worker, eventually timing out the daemon after 300s.

## Context

- Frigate container up since 2026-04-03 01:23 UTC, RestartCount=0 (no docker update).
- `pi_cam_0` / `pi_cam_1` recordings actually only *began* on 2026-04-06 ~07:02 UTC (first segments `2026-04-06/07/pi_cam_0/02.21.mp4`, `pi_cam_1/02.22.mp4`). Before that the Pi at `192.168.0.11` was unreachable (`Connection to tcp://192.168.0.11:8554 failed: No route to host` loop in frigate logs). The recordings resumed automatically once the Pi came back online — not a user action and not a docker update.
- Radiens / Allego has been down for days (journalctl shows `radiens_poller: Radiens poll failed (446110 consecutive)`). The session daemon (pid 4518) is still running and the **manual-session detection path is independent of Radiens**.

## Issue 1 — Manual export didn't trigger on 18:02 stop

### Symptoms
- User turned off recording for `pi_cam_2` and `pi_cam_3` from the Frigate UI at 18:02:19 / 18:02:23.
- No export file appeared under `/srv/frigate/storage/exports/manual/manual/2026-04-08/` (a.k.a. `/home/skimlab/Desktop/Frigate Exports/manual/manual/2026-04-08/`).
- `/api/exports` had no new entries.

### Root cause
The daemon's manual-detection path (`_handle_external_recording_change` in `backend/daemon.py:441`, using the MQTT topic `frigate/+/recordings/state`) only opens a `ManualSession` on an **OFF→ON transition**. For `pi_cam_2` / `pi_cam_3` today, **no "Turning on recordings" event appears anywhere in the current frigate log** — they were already ON when the daemon (re)started, or were enabled via a path the MQTT dispatcher didn't emit a state change for. So when they were turned OFF, the daemon looked up "is there an open manual session for pi_cam_2?" → no → nothing to export.

Compounding: at daemon startup, `daemon.py:199` calls `stop_all_recording()` then waits a grace period before arming the callback. If cameras were enabled before the daemon came up (or re-enabled in a way that didn't produce an MQTT edge after the callback was armed), the ON is invisible to the manual-session manager.

### Auto-export paths (reference)
1. **Radiens-driven** (`_handle_session_start` / `_handle_session_end`, daemon.py:265 / :310) — uses metadata from the Tauri GUI. Dead while Radiens is disconnected.
2. **Manual session detection** (`_handle_external_recording_change`, daemon.py:441) — MQTT state changes on `frigate/+/recordings/state`. Requires the daemon to observe BOTH the ON and OFF transitions while running. This is what failed today.

## Issue 2 — Frigate export stuck `in_progress` for pi_cam_0

### Symptoms
After a short manual test with cam_0, cam_1, cam_2 (all via Frigate UI), the daemon logged successful export + move for cam_1 and cam_2, but cam_0's export sat at `in_progress: true` in `/api/exports` with no output file in `/media/frigate/exports/`.

```
1775641099 pi_cam_0 in_progress=true  2604081838_manual_pi_cam_0   (id: pi_cam_0_nhjty7)
1775641105 pi_cam_1 in_progress=false 2604081838_manual_pi_cam_1
1775641110 pi_cam_2 in_progress=false 2604081838_manual_pi_cam_2
```

- Frigate accepted the POST at 18:46:07 (`POST /api/export/pi_cam_0/start/1775641099/end/1775641569 → 200`).
- `ps -ef` inside the container showed no ffmpeg export worker — only the 4 normal detect/record ffmpegs.
- The `nhjty7` output file never appeared in `/media/frigate/exports/`.
- The daemon polled `/api/exports` every 2 s for 300 s then timed out:
  ```
  18:51:08  frigate_controller: Export pi_cam_0_nhjty7 timed out after 300s
  18:51:08  neurosurveillance: Frigate export timed out for manual session 0bc3322d
  ```
  Session JSON `2604081838_manual_pi_cam_0_session.json` was written and the thread released cleanly. **No daemon restart needed.**

### Workaround applied
```bash
curl -X DELETE http://localhost:5000/api/export/pi_cam_0_nhjty7
curl -X POST http://localhost:5000/api/export/pi_cam_0/start/1775641099/end/1775641569 \
  -H 'Content-Type: application/json' \
  -d '{"name":"2604081838_manual_pi_cam_0_retry"}'
# → pi_cam_0_eau4a0
```

The retry finished in ~10 s (86 MB). Since this retry was triggered directly against Frigate (bypassing the daemon), the move step had to be done by hand:

```bash
sudo mv /srv/frigate/storage/exports/pi_cam_0_20260408_183819-20260408_184609_eau4a0.mp4 \
        /srv/frigate/storage/exports/manual/manual/2026-04-08/2604081838_manual_pi_cam_0.mp4
sudo chown skimlab:skimlab /srv/frigate/storage/exports/manual/manual/2026-04-08/2604081838_manual_pi_cam_0.mp4
```

Final state in `/srv/frigate/storage/exports/manual/manual/2026-04-08/`:
- `2604081838_manual_pi_cam_0.mp4` (86 MB, from retry)
- `2604081838_manual_pi_cam_1.mp4` (90 MB)
- `2604081838_manual_pi_cam_2.mp4` (85 MB)

## Open questions / follow-up

- **Frigate orphan exports:** Why did the first cam_0 POST register as in_progress but never spawn an ffmpeg worker? Need to check frigate logs around `18:46:07` for any silent spawn error, and whether `/tmp/cache` or the exports volume was momentarily full / contended with the parallel cam_1 / cam_2 exports. Possibly a race when 3 exports are requested back-to-back.
- **Manual-session ON-edge invisibility:** Daemon startup calls `stop_all_recording()` and then arms the MQTT callback after a grace period. If recording is enabled through the Frigate API/config rather than MQTT dispatcher, or before the grace period ends, the callback never sees the ON edge and auto-export can't fire on the eventual OFF. Possible mitigations:
  - On daemon startup, query Frigate `/api/config` (or `/api/stats`) for any already-enabled cameras and seed `ManualSessionManager` with synthetic "started" sessions using the earliest in-progress recording segment's timestamp as start.
  - Or: after the grace period, re-enable via MQTT any cameras that were on before the reset, so the ON-edge becomes visible.
- **Recording auto-resume behaviour:** when the Pi at `192.168.0.11` came back online on 2026-04-06 ~07:02 UTC, Frigate resumed recording for cam_0 / cam_1 without any user action. That's expected (`record.enabled=true` in config) but it's worth documenting so this isn't mistaken for a rogue start next time — already confused the user today. See also: Pi boot on this date.
- **Stale daemon log file:** `/opt/neurosurveillance/logs/daemon.log` is frozen at 2026-02-26 (MQTT reconnect loop). Current daemon logs only to journalctl. Either fix file logging or remove the stale file to avoid confusion.

## Reference commands used

```bash
# Frigate state
docker inspect frigate --format '{{.State.StartedAt}} {{.RestartCount}}'
docker logs frigate 2>&1 | grep -E "Turning (on|off) recordings"
curl -s http://localhost:5000/api/config | jq '.cameras | to_entries[] | {k:.key, rec:.value.record.enabled}'
curl -s http://localhost:5000/api/exports | jq '.[] | {id,camera,name,in_progress}'

# Daemon state
curl -s http://127.0.0.1:8585/api/status
journalctl -u neurosurveillance* --since "30 min ago" --no-pager | grep -viE "radiens|grpc|code: 14|UNAVAIL"

# Earliest recording segments for a camera
docker exec frigate sh -c 'find /media/frigate/recordings -path "*pi_cam_0*" -name "*.mp4" | sort | head -3'
```

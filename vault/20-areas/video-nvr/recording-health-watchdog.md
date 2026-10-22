---
tags: [procedure, implementation, monitoring, session-daemon, frigate]
created: 2026-05-18
completed: 2026-05-18
status: completed
deferred:
  - "MQTT-to-Netdata wiring (Step 5) — Slack alerts not yet routed"
  - "UI lag badge — frontend not yet consuming /api/health.recording_lag"
related-incident: 2026-05-11 export timeout
---

# Per-Camera Recording Health Watchdog — Implementation Guide

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The implementation history of the recording watchdog (`recording_watchdog.py`) shipped 2026-05-18 — a background thread that watches Frigate's database and raises an alert when an active recording stops getting new video segments.
>
> **Why it exists.** Frigate can silently stop writing segments (go2rtc disconnects, ffmpeg crashes, disk goes weird). Without the watchdog, the daemon would still think the recording is live and you'd lose hours before noticing. The watchdog catches it in ~60 seconds.
>
> **How to read this page.** Read "Purpose" for context. The implementation steps are historical record — the code is shipped and lives at `backend/recording_watchdog.py`. The reference architecture entry is at [[architecture#11. Recording Watchdog (`recording_watchdog.py`)|architecture §11]].

> [!quote] Paper-ready
> A background recording-health watchdog polls Frigate's recordings SQLite every 30 seconds for cameras with active sessions, raising an MQTT alert and a journal STALL event when the most recent segment is more than 60 seconds old; recovery is detected automatically when new segments resume.

## Purpose

Detect within ~30 seconds when Frigate's recording subsystem silently stalls on an actively-recording camera, so the operator can intervene before hours of experiment data are lost.

Triggered by the 2026-05-08 stall (see [[export-timeout-fix#related|export-timeout-fix]]): both Pi1 cameras (`pi_cam_0`, `pi_cam_1`) stopped producing segments at 02:04 KST on May 8, but the Pi host, go2rtc, Frigate container, and the session daemon all kept running. The session daemon never noticed because it tracks recording state via MQTT (`ON` is reasserted), not segment progress. Result: ~87 hours of intended recording vanished silently across two sessions.

## Detection signal

Frigate writes one row to its `recordings` SQLite table per 10-second segment, with `start_time` and `end_time` as Unix timestamps. For a healthy actively-recording camera, `MAX(end_time)` should be within ~10–15 s of wall clock. If it falls behind by more than ~60 s, the recording ffmpeg has stalled (or never started).

The watchdog polls this query every 30 s and emits an alert on first violation per camera.

```sql
SELECT camera, MAX(end_time)
FROM recordings
WHERE camera IN (<actively-recording cameras>)
GROUP BY camera;
```

DB path on the NVR: `/srv/frigate/storage/frigate.db` (mapped from `/media/frigate/frigate.db` inside the container).

### Why not the Frigate HTTP API?

Frigate exposes `/api/{camera_name}/recordings/summary` but it returns hourly aggregates, not per-segment freshness. Hitting SQLite read-only is faster (one query vs. four cameras × HTTP) and avoids contending with Frigate's request queue.

## What gets built

- New module: `neurosurveillance/backend/recording_watchdog.py` (~140 LOC)
- `daemon.py` wires it up in `__init__` and stops it in `shutdown()`
- Alerts publish to MQTT topic `neurosurveillance/watchdog/{camera}/stall` (payload: JSON with lag and last_segment_ts)
- Existing Netdata MQTT subscriber picks up the topic and routes to Slack via the existing webhook (no new infra)
- Daemon `/api/health` response gains a `recording_lag` block: `{ "pi_cam_0": 3.2, "pi_cam_1": 122.5, ... }` (seconds since last segment, or `null` if camera not actively recording)

Nothing in the frontend changes for the v1 ship. The header storage badge already turns red on health issues; adding a "recording stalled" badge is a follow-up (see [[#future-extensions]]).

## Architecture

```
        ┌──────────────┐ poll every 30s (READ ONLY)
        │  Watchdog    │─────────────────────────► frigate.db
        │  Thread      │ ◄─────────────────────────  MAX(end_time) per active camera
        └──────┬───────┘
               │ on stall:
               │  - logger.error
               │  - update self._lag (consumed by /api/health)
               │  - mqtt publish neurosurveillance/watchdog/{cam}/stall
               ▼
        ┌──────────────┐
        │  Mosquitto   │ ─► Netdata MQTT collector ─► Slack
        └──────────────┘
```

The watchdog is a daemon-thread on the session daemon. It reads the manual + Radiens session managers to know which cameras are "actively recording" — only those are checked. When no camera is active, the watchdog short-circuits.

## Step 1 — New module `recording_watchdog.py`

**File:** `neurosurveillance/backend/recording_watchdog.py` (new)

```python
"""Watchdog that detects stalled Frigate recordings on active cameras.

Polls Frigate's SQLite recordings table every POLL_INTERVAL seconds. For each
camera with an active manual or Radiens session, checks how recently a segment
was written. If lag exceeds STALL_THRESHOLD, emits an alert (log + MQTT) and
remembers that the camera is in alarm so we don't spam.
"""

import json
import logging
import sqlite3
import threading
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)

POLL_INTERVAL = 30.0          # seconds between checks
STALL_THRESHOLD = 60.0        # seconds — lag above this triggers alert
START_GRACE = 30.0            # seconds after recording starts where no alert fires
                              #   (Frigate needs to write at least one segment)


class RecordingWatchdog:
    """Background thread that alerts when Frigate stops writing segments
    for a camera that should be recording.

    Args:
        frigate_db_path: Path to Frigate's SQLite database on the host.
        active_cameras_provider: Callable returning {camera_id: started_at_unix}.
            Empty dict means nothing is being recorded.
        mqtt_publish: Callable (topic, payload_str) -> None. Used to publish
            alerts. May be None to disable MQTT alerts.
    """

    def __init__(
        self,
        frigate_db_path: str,
        active_cameras_provider: Callable[[], dict[str, float]],
        mqtt_publish: Optional[Callable[[str, str], None]] = None,
    ):
        self.db_path = frigate_db_path
        self._active = active_cameras_provider
        self._publish = mqtt_publish
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._alerted: set[str] = set()
        self._lag_lock = threading.Lock()
        self._lag: dict[str, float] = {}   # camera_id -> seconds since last segment

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="recording-watchdog",
        )
        self._thread.start()
        logger.info("Recording watchdog started (poll=%.0fs, threshold=%.0fs)",
                    POLL_INTERVAL, STALL_THRESHOLD)

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5.0)

    def get_lag_snapshot(self) -> dict[str, Optional[float]]:
        """Return current per-camera lag (s). None for cameras not actively recording."""
        with self._lag_lock:
            return dict(self._lag)

    def _loop(self):
        while not self._stop.wait(POLL_INTERVAL):
            try:
                self._check_once()
            except Exception as e:
                logger.exception("Watchdog tick failed: %s", e)

    def _check_once(self):
        active = self._active()
        if not active:
            if self._alerted:
                self._alerted.clear()
            with self._lag_lock:
                self._lag.clear()
            return

        now = time.time()
        cameras = list(active.keys())

        try:
            # sqlite3 with short timeout — never block daemon if DB is locked.
            conn = sqlite3.connect(self.db_path, timeout=2.0)
            try:
                placeholders = ",".join("?" * len(cameras))
                rows = conn.execute(
                    f"SELECT camera, MAX(end_time) FROM recordings "
                    f"WHERE camera IN ({placeholders}) GROUP BY camera",
                    cameras,
                ).fetchall()
            finally:
                conn.close()
        except sqlite3.OperationalError as e:
            logger.warning("Watchdog DB read failed (will retry): %s", e)
            return

        last_seen = {cam: ts for cam, ts in rows if ts is not None}
        new_lag: dict[str, float] = {}

        for cam, started_at in active.items():
            if (now - started_at) < START_GRACE:
                # Just started — give Frigate time to write the first segment.
                new_lag[cam] = 0.0
                continue

            last_ts = last_seen.get(cam)
            if last_ts is None:
                # No segments at all since recording began on this camera.
                lag = now - started_at
            else:
                lag = now - last_ts
            new_lag[cam] = lag

            if lag > STALL_THRESHOLD:
                if cam not in self._alerted:
                    self._alerted.add(cam)
                    self._emit_alert(cam, lag, last_ts)
            elif cam in self._alerted:
                self._alerted.discard(cam)
                logger.warning(
                    "Recording recovered on %s (lag now %.0fs)", cam, lag,
                )

        with self._lag_lock:
            self._lag = new_lag

    def _emit_alert(self, camera: str, lag: float, last_ts: Optional[float]):
        msg = (
            f"Recording STALLED on {camera}: lag={lag:.0f}s "
            f"({'no segments since recording started' if last_ts is None else 'last segment present'})"
        )
        logger.error(msg)
        if self._publish:
            payload = json.dumps({
                "camera": camera,
                "lag_seconds": round(lag, 1),
                "last_segment_ts": last_ts,
                "ts": time.time(),
            })
            try:
                self._publish(f"neurosurveillance/watchdog/{camera}/stall", payload)
            except Exception as e:
                logger.error("Failed to publish watchdog alert: %s", e)
```

## Step 2 — Wire into `daemon.py`

**Imports** (top of file):

```python
from recording_watchdog import RecordingWatchdog
```

**In `Daemon.__init__`**, after the session managers and `FrigateController` are created:

```python
def _active_recording_cameras() -> dict[str, float]:
    """Cameras the daemon currently considers actively recording."""
    out: dict[str, float] = {
        cam: rec.start_time_utc
        for cam, rec in self.manual_session_manager.active_recordings.items()
    }
    # Radiens-triggered session (if active) — extract its camera + start time.
    sm = self.session_manager
    if getattr(sm, "is_active", False):
        cam = getattr(sm, "current_camera", None)
        started = getattr(sm, "current_start_time_utc", None)
        if cam and started:
            out[cam] = started
    return out

self.watchdog = RecordingWatchdog(
    frigate_db_path=config["frigate"].get(
        "db_path", "/srv/frigate/storage/frigate.db"
    ),
    active_cameras_provider=_active_recording_cameras,
    mqtt_publish=self.frigate._mqtt_client.publish if self.frigate._mqtt_client else None,
)
self.watchdog.start()
```

(If `SessionManager` doesn't yet expose `is_active` / `current_camera` / `current_start_time_utc`, add thin properties. Checked at write time: properties don't exist — add them.)

**In `Daemon.shutdown()`**, before MQTT disconnect:

```python
if self.watchdog:
    self.watchdog.stop()
```

## Step 3 — Surface lag on `/api/health`

**File:** `neurosurveillance/backend/api.py`

In the `/api/health` handler, add:

```python
"recording_lag": daemon.watchdog.get_lag_snapshot() if daemon.watchdog else {},
```

Frontend already polls `/api/health` every 5 s; surfacing the data here means a follow-up UI change can read it without new endpoints.

## Step 4 — Config

**File:** `/opt/neurosurveillance/config.yaml` (and the in-repo reference at `neurosurveillance/config/config.yaml`)

Add under the existing `frigate:` block:

```yaml
frigate:
  # ... existing keys ...
  db_path: "/srv/frigate/storage/frigate.db"
```

Default in the watchdog matches this, so the key is optional, but explicit is better.

## Step 5 — Mosquitto → Netdata → Slack wiring

The existing Netdata MQTT collector (deployed 2026-03-27 per `01-infrastructure/netdata/nvr-alerts-config.md`) needs one new subscribed topic:

```
neurosurveillance/watchdog/+/stall
```

Add a custom alert rule in `/etc/netdata/health.d/nvr-alerts.conf`:

```
alarm: nvr_recording_stalled
   on: <mqtt_chart_id>     # whichever ID the MQTT collector assigns
warn: $this > 0
 info: A Frigate camera stopped producing recording segments while a session was active.
   to: slack
```

(Exact MQTT collector chart wiring depends on Netdata version — verify with `nvr-alerts-config.md`.)

If wiring through Netdata is too fiddly, the v1 fallback is to publish directly from Python to the existing Slack webhook (URL already stored on the NVR for Netdata). Slightly more code, less infra to align — judgement call.

## Step 6 — Restart and verify

```bash
sudo systemctl restart neurosurveillance-session.service
journalctl -u neurosurveillance-session.service -n 40 --no-pager
# Expect: "Recording watchdog started (poll=30s, threshold=60s)"
```

Verification matrix:

| Scenario | Expected |
| --- | --- |
| No active recording | `/api/health.recording_lag` returns `{}`, no alerts |
| Active recording, Frigate healthy | `recording_lag[cam]` shows < 15 s, no alerts |
| Recording just started (< 30s ago) | `recording_lag[cam]` shows `0.0` (grace period) |
| Frigate's recording ffmpeg killed for a camera | Within ~90 s: ERROR log, MQTT message, `recording_lag[cam]` shows growing value, Slack alert |
| Camera recovers | INFO log "Recording recovered", alarm clears, future stalls re-alert |
| Frigate's DB locked momentarily | WARNING log "DB read failed", retried next tick, no false alert |

**Synthetic stall test** (run only when no real session is active):

```bash
# Start a short manual recording on pi_cam_0 from the Tauri UI, then:
docker exec frigate sh -c 'pkill -f "rtsp://192.168.0.11:8554/pi_cam_0"'
# Frigate will restart the ffmpeg automatically, but there'll be a 60-120s gap.
# Watch journalctl for the watchdog alert + recovery within 2 minutes.
```

## Rollback

Stop the daemon, revert `daemon.py` + `api.py` edits, and delete `recording_watchdog.py`. No persistent state created; no DB schema changes. Restart the daemon.

## Limitations

- **Detects only segment-write stalls**, not stream-quality issues (e.g. corrupt H.264 frames go undetected — those would show up in playback).
- **Does not auto-remediate.** A follow-up could MQTT-toggle the camera OFF → ON to force Frigate to respawn its recording ffmpeg. Intentionally deferred: a heisenbug auto-restart can mask the root cause, and the May 8 incident's source is still unknown.
- **First-segment failure is detected only after START_GRACE (30 s).** Acceptable: it bounds the false-positive window without losing more than ~30 s of evidence on a real failure.

## Future extensions

1. **UI badge** — surface `recording_lag` in the ChamberSilo header (red dot when > threshold). Mirrors the existing camera-offline badge.
2. **Auto-recovery** — controlled OFF → ON MQTT toggle when stall persists ≥ 5 min. Only after we've seen the watchdog fire on a real stall and confirmed Frigate restarts the ffmpeg cleanly.
3. **Session-level summary** — when a manual session ends, compute `% of duration with lag > threshold` and store in the session JSON. Lets reviewers quickly see "this session had 14 % stall time" before opening the MP4.

## Related

- [[export-timeout-fix|export-timeout-fix]] — the export side of the May 8 / May 11 incident
- [[nvr-alerts-config|nvr-alerts-config]] — existing Netdata + Slack pipeline this hooks into
- 2026-05-08 02:04 KST incident — pi_cam_0/pi_cam_1 silently stopped producing segments; pi_cam_2 either kept recording or stalled too (can't determine — logs aged out). This watchdog would have alerted within ~90 s either way.

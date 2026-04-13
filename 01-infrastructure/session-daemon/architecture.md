---
tags: [infrastructure, session-daemon, architecture]
created: 2026-02-20
updated: 2026-04-13
status: production
version: "3.0"
---

# Session Daemon Architecture

The **NeuroSurveillance Session Daemon** synchronizes Frigate video recording with NeuroNexus Radiens EEG/EMG data acquisition. When a researcher starts or stops EEG recording in Radiens, the daemon automatically starts/stops video recording in Frigate, then exports and organizes the video files. A companion desktop UI (Tauri + React) provides metadata entry and live monitoring.

## Design Principles

1. **Autonomous core** -- the recording sync loop (Radiens poll -> Frigate toggle) runs independently and does not depend on the UI or API. If no metadata is set, the daemon uses safe defaults (`unknown` mouse ID, timestamp-based filenames). No data is ever lost.
2. **Fail-safe bias** -- if the daemon crashes mid-session with recording ON, that is safe (extra footage, not lost footage). On restart, the daemon resets recording to OFF.
3. **No Radiens control** -- the daemon only *observes* Radiens state. It never starts/stops EEG recording. The researcher controls Radiens directly.
4. **Metadata gates recording** -- the daemon only starts recording for chambers that have metadata set via the GUI/API. Chambers without metadata are skipped. If no chambers have metadata when Radiens starts, no video is recorded and a warning is logged.
5. **Multi-chamber independence** -- each chamber (camera) has its own pending metadata, active session state, and manual recording tracker. Chambers operate independently.

## System Overview

```
                                    ASUS Mini PC (192.168.0.50)
  ┌─────────────┐          ┌──────────────────────────────────────────────┐
  │  Pi 1        │  RTSP   │                                              │
  │  go2rtc      │────────>│  Frigate NVR (Docker, port 5000)             │
  │  192.168.0.11│         │    - Records pi_cam_0..3 (4 cameras)         │
  └─────────────┘         │    - MQTT-controlled recording on/off        │
  ┌─────────────┐         │    - Export API for named MP4 clips           │
  │  Pi 2        │  RTSP   │                                              │
  │  go2rtc      │────────>│                                              │
  │  192.168.0.12│         │                                              │
  └─────────────┘         │                                              │
                           │                                              │
                           │  Mosquitto MQTT (Docker, port 1883)          │
                           │    - frigate/<camera>/recordings/set ON/OFF  │
                           │                                              │
                           │  Radiens (NeuroNexus EEG/EMG software)       │
                           │    - AllegoClient Python API                 │
                           │    - get_status() -> R_ON / R_OFF            │
                           │                                              │
                           │  ┌──────────────────────────────────┐        │
                           │  │  SESSION DAEMON (this system)    │        │
                           │  │  /opt/neurosurveillance/         │        │
                           │  │                                  │        │
                           │  │  1. Polls Radiens (1s interval)  │        │
                           │  │  2. Detects R_OFF -> R_ON        │        │
                           │  │  3. Publishes ON to MQTT         │        │
                           │  │  4. Detects R_ON -> R_OFF        │        │
                           │  │  5. Publishes OFF to MQTT        │        │
                           │  │  6. Calls Frigate export API     │        │
                           │  │  7. Organizes MP4 + JSON sidecar │        │
                           │  │  8. StorageMonitor (30s poll)    │        │
                           │  │     - Blocks recordings if       │        │
                           │  │       disk < 200 GB EEG reserve  │        │
                           │  │                                  │        │
                           │  │  HTTP API on 127.0.0.1:8585      │        │
                           │  │  (metadata input from UI)        │        │
                           │  └──────────────────────────────────┘        │
                           │                                              │
                           │  ┌──────────────────────────────────┐        │
                           │  │  DESKTOP UI (Tauri + React)      │        │
                           │  │  Polls daemon API every 1.5s     │        │
                           │  │  Polls health every 5s           │        │
                           │  │  Polls storage every 10s         │        │
                           │  │  Camera snapshots every 1s       │        │
                           │  └──────────────────────────────────┘        │
                           └──────────────────────────────────────────────┘
                                          │
                                          │ Tailscale (future)
                                          v
                                    ┌──────────┐
                                    │ Synology  │
                                    │ NAS       │
                                    │ 100.120.  │
                                    │ 86.10     │
                                    └──────────┘
```

## Components

### 1. Radiens Poller (`radiens_poller.py`)

Polls the NeuroNexus Radiens software every 1 second to detect recording state changes.

| Detail | Value |
|--------|-------|
| **Library** | `radiens` v4.0.0 Python package (PyPI, installed in daemon venv) |
| **Class** | `AllegoClient` |
| **Method** | `client.get_status()` -> status object with `RecordingSpec` |
| **Key field** | `.recording.mode` -- values: `R_ON`, `R_OFF` |
| **Poll interval** | 1 second |
| **Connection** | Local (Radiens runs on same machine) |

**State machine:**

```
                get_status().recording.mode
                         │
              ┌──────────┴──────────┐
              v                     v
         ┌─────────┐          ┌─────────┐
         │  IDLE   │          │ ACTIVE  │
         │ (R_OFF) │          │ (R_ON)  │
         └────┬────┘          └────┬────┘
              │                    │
              │  R_OFF -> R_ON     │  R_ON -> R_OFF
              │  = SESSION START   │  = SESSION END
              │  (with metadata)   │  (active only)
              v                    v
         Start Frigate        Stop Frigate
         recording on         recording on
         chambers with        active chambers
         metadata set         Call export API
         Log start_ts
```

**Error handling:**
- If `get_status()` raises an exception (Radiens not running, connection lost), the poller logs a warning and retries on the next poll cycle. It does NOT change Frigate recording state.
- **Log spam suppression:** The first error is logged, then only every 5th consecutive failure. The counter resets when Radiens reconnects. This prevents log flooding during long outages.
- If Radiens was in `R_ON` when connection was lost and reconnects still in `R_ON`, no duplicate start is triggered (state tracking prevents this).
- If Radiens was in `R_ON` when connection was lost and reconnects in `R_OFF`, the daemon treats this as a session end and exports normally.

### 2. Frigate Controller (`frigate_controller.py`)

Controls Frigate recording via MQTT and handles video export via HTTP API. Also detects **external** recording state changes (e.g. Record button clicks in Frigate's web UI).

| Detail | Value |
|--------|-------|
| **MQTT broker** | `{NVR_IP}:1883` (Mosquitto, Docker) |
| **MQTT publish topic** | `frigate/{CAMERA_ID}/recordings/set` |
| **MQTT subscribe topic** | `frigate/+/recordings/state` |
| **MQTT payload** | `ON` or `OFF` |
| **Export API** | `POST http://{NVR_IP}:5000/api/export/{camera}/start/{start}/end/{end}` with JSON body `{"name": "<export_name>"}` (required by Frigate v0.16+) |
| **Export poll interval** | 2 seconds |
| **Export timeout** | 300 seconds (5 minutes) |
| **Frigate timezone** | Timestamps in UTC (system timezone `Asia/Seoul`, UTC+9) |

> [!warning] MQTT Recording Toggle Prerequisite
> `record.enabled: true` must be set in Frigate's `config.yml` for the MQTT toggle to work. If disabled in config, MQTT/UI toggle has no effect. The current production config already has this set -- see [[../frigate/config-yml|Frigate Config]].

**Recording control flow:**

1. **On startup:** Publish `OFF` to all camera recording topics (clean slate)
2. **On session start:** Publish `ON` to each chamber's camera topic
3. **On session end:** Publish `OFF`, then call the export API

**External change detection (two-stage filter):**

The controller subscribes to `frigate/+/recordings/state` and uses two guards to filter incoming state messages:

1. **`_expected_states` check:** Before publishing ON/OFF, the daemon records the expected state. When a matching state message arrives, it is consumed as a self-echo and ignored.
2. **`_last_known_state` check:** Even if Stage 1 passes, the message is ignored if it carries the **same state** as the previous one (no actual transition). This suppresses Frigate's periodic reassertion of `ON` from `config.yml record.enabled=true`, which would otherwise trigger false manual sessions.

Only messages that pass both filters (not self-initiated AND an actual state transition) fire the external change callback to the daemon.

**Export flow:**

1. Daemon records `start_timestamp` (Unix epoch, UTC) when session begins
2. On session end, records `end_timestamp`
3. Timestamps are padded +/-2 seconds to ensure Frigate's segment boundaries are fully included
4. Calls Frigate export API with `{"name": "<session_filename>"}` in the POST body -- Frigate uses this name as the export label
5. Waits for export to complete (polls `GET /api/exports` every 2s, timeout 5 min). Each poll checks the `in_progress` flag -- the export is only considered done when `in_progress` is absent or `false`. This is critical because Frigate lists exports immediately while `ffmpeg` is still multiplexing; moving the file prematurely corrupts the MP4 (the `moov` header atom is written last).
6. Export runs in a **background thread** so it does not block the main Radiens polling loop

**Timestamp handling:**
- All internal timestamps use UTC Unix epoch
- Frigate export API expects UTC timestamps
- Human-readable timestamps in session logs use `{TIMEZONE}` (`Asia/Seoul`)
- Filename timestamps (`YYMMDDHHMM`) use local time (`Asia/Seoul`)

### 3. Session Manager (`session_manager.py`)

Manages per-chamber session metadata and logging. State is keyed by `chamber_id` (string: `"0"`, `"1"`, `"2"`, `"3"`).

**Multi-chamber state model:**

```python
# Independent state per chamber
active_sessions: dict[str, SessionRecord]     # {"0": SessionRecord, "1": SessionRecord}
pending_metadata: dict[str, SessionMetadata]   # {"0": SessionMetadata, "1": SessionMetadata}
history: list[SessionRecord]                   # All completed sessions (both chambers)
```

**Data classes:**

```python
@dataclass
class SessionMetadata:
    mouse_id: str = "unknown"
    recording_type: str = "unknown"
    user_name: str = "unknown"
    chamber: Optional[int] = None

    def is_default(self) -> bool:
        # True if all fields == "unknown"

@dataclass
class SessionRecord:
    session_id: str
    source: str = "radiens"
    start_time_utc: float
    end_time_utc: float
    start_time_local: str
    end_time_local: str
    duration_seconds: float
    mouse_id: str
    recording_type: str
    user_name: str
    chamber: int
    camera: str
    radiens_xdat_filename: str
    radiens_xdat_path: str
    video_filename: str
    export_status: str = "pending"
    nas_transfer_status: str = "skipped"
```

**Session lifecycle:**

```
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. METADATA SET (optional, via HTTP API, per chamber)       │
  │    User sets: mouse_id, recording_type, user_name, chamber  │
  │    If not set: defaults to "unknown", "unknown", "unknown"  │
  │    Partial updates allowed (only provided fields change)    │
  └─────────────────────────┬───────────────────────────────────┘
                            v
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. SESSION START (automatic, triggered by Radiens R_ON)     │
  │    Starts independent session for EACH chamber              │
  │    Each session uses its own pending_metadata               │
  │    Captures: start_timestamp, camera, Radiens base_name     │
  └─────────────────────────┬───────────────────────────────────┘
                            v
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. SESSION END (automatic, triggered by Radiens R_OFF)      │
  │    Ends ALL active sessions                                 │
  │    Daemon records: end_timestamp, duration                  │
  │    Triggers: Frigate export (background), session log       │
  └─────────────────────────┬───────────────────────────────────┘
                            v
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. POST-SESSION (automatic, background thread per chamber)  │
  │    - Export MP4 from Frigate (±2s buffer on timestamps)     │
  │    - Move MP4 to organized directory (sudo mv)              │
  │    - Write _session.json sidecar                            │
  │    - Clear metadata for that chamber                        │
  └─────────────────────────────────────────────────────────────┘
```

**Filename format:** `YYMMDDHHMM_mouseID_type.mp4`

| Component | Example | Source |
|-----------|---------|--------|
| `YYMMDDHHMM` | `2602201430` | Session start time (local, `Asia/Seoul`) |
| `mouseID` | `HETCF3R1` | From metadata API (or `unknown`) |
| `type` | `basal` | From metadata API (or `unknown`) |

### 3b. Manual Session Manager (`manual_session_manager.py`)

Handles recordings triggered externally via Frigate's web UI (clicking the Record button on a camera). Each camera is tracked independently.

**Detection flow:**

```
User clicks Record in Frigate UI on pi_cam_0
  → Frigate publishes: frigate/pi_cam_0/recordings/state = ON
  → FrigateController detects: external ON (not self-initiated)
  → Daemon callback: _handle_external_recording_change("pi_cam_0", "ON")
  → ManualSessionManager.start_recording("pi_cam_0")
  → Inherits pending_metadata from SessionManager (mouse_id, recording_type, user_name)
  → Records start timestamp

User clicks Stop in Frigate UI
  → Frigate publishes: frigate/pi_cam_0/recordings/state = OFF
  → ManualSessionManager.stop_recording("pi_cam_0")
  → Records end timestamp
  → Background thread: calls Frigate export API → MP4 → JSON sidecar
```

**Key behaviors:**
- **Radiens priority:** If a Radiens session is active on a camera, external Record ON is ignored
- **Min duration filter:** Recordings shorter than `min_duration` (default 5s) are discarded (accidental clicks)
- **Per-camera:** cam_0 and cam_1 can have independent manual sessions
- **Metadata inheritance:** Manual sessions inherit `mouse_id`, `recording_type`, and `user_name` from the pending metadata set via the UI. If no metadata is set, defaults are used.
- **Naming:** Uses inherited metadata: `YYMMDDHHMM_mouseID_type.mp4` (or `YYMMDDHHMM_manual_pi_cam_0.mp4` if no metadata)
- **JSON sidecar:** Same format as Radiens sessions but with `"source": "manual"`

### 4. Session Utilities (`session_utils.py`)

Shared helper functions used by both `SessionManager` and `ManualSessionManager`.

| Function | Purpose |
|----------|---------|
| `generate_filename(start_time_utc, mouse_id, recording_type, tz, extension)` | Generates `YYMMDDHHMM_mouseID_type.mp4` filename using local time |
| `write_session_json(session, sessions_dir)` | Writes dataclass instance to `{video_filename}_session.json` sidecar |

### 5. HTTP API (`api.py`)

REST API on `127.0.0.1:{SESSION_DAEMON_PORT}` for the UI to set session metadata and monitor status.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/status` | GET | Daemon status: per-chamber sessions, per-chamber pending metadata, Radiens connection, recording states, active manual recordings |
| `/api/session/metadata?chamber_id=X` | POST | Set metadata for next session on a specific chamber (partial updates allowed, chamber validated against config) |
| `/api/session/metadata?chamber_id=X` | DELETE | Clear pending metadata for a chamber, reset to defaults |
| `/api/session/current` | GET | Current active session info (first active, for backward compatibility) |
| `/api/session/history?source=X&limit=N` | GET | List of past sessions, merged Radiens + manual, newest first |
| `/api/session/manual` | GET | Active and recent manual recording sessions |
| `/api/health` | GET | Health check -- 200 if Radiens + MQTT connected, 503 otherwise. Includes `storage_level` (`ok`/`warn`/`critical`) and `storage_used_percent` fields. |
| `/api/storage` | GET | Storage status snapshot (cached, instant). Returns disk usage, categories, EEG reserve, effective available, status level, can_record flag. |
| `/api/storage/estimate?cameras=N&hours=H` | GET | Server-side recording calculator. Returns estimated bytes, whether it fits, remaining space after. |
| `/api/storage/camera-bitrates` | GET | On-demand query to go2rtc APIs on each Pi. Returns per-camera bitrates parsed from `rpicam-vid` exec configs. |

**Multi-chamber status response structure:**

```json
{
  "daemon": "running",
  "radiens": {
    "connected": true,
    "recording_states": {"0": "R_OFF", "1": "R_OFF", "2": "R_OFF", "3": "R_OFF"}
  },
  "mqtt": {"connected": true},
  "sessions": {
    "0": {"session_id": "...", "mouse_id": "HETCF3R1", ...},
    "1": null
  },
  "pending_metadata": {
    "0": {"mouse_id": "HETCF3R1", "is_default": false, ...},
    "1": {"mouse_id": "unknown", "is_default": true, ...}
  },
  "manual_recordings": {}
}
```

> [!tip] Localhost Only
> The API binds to `127.0.0.1` only -- not accessible from the network. This is intentional: the UI runs on the same machine.

> [!tip] CORS Enabled
> The API returns CORS headers (`Access-Control-Allow-Origin: *`) so Tauri webview and browser development can call the localhost API successfully.

### 6. Export Pipeline

The export pipeline handles both Radiens-triggered and manual session exports. It runs in background threads to avoid blocking the main polling loop.

**Export sequence:**

```
Session ends (Radiens R_OFF or manual Stop)
  │
  ├─ 1. FrigateController.export_recording()
  │     POST /api/export/{camera}/start/{ts-2}/end/{ts+2}
  │     Body: {"name": "<session_filename>"}
  │     Returns: export_id
  │
  ├─ 2. FrigateController.wait_for_export(export_id)
  │     Polls GET /api/exports every 2s (timeout: 5 min)
  │     Skips if in_progress=true (ffmpeg still multiplexing)
  │     Waits up to 10s for file to appear on disk
  │     Returns: export metadata with video_path
  │
  ├─ 3. File organization (daemon._move_export_file)
  │     Source: {SESSION_EXPORT_DIR}/<frigate_export_file>  (Docker volume, root-owned)
  │     Target: {EXPORT_DIR}/{user}/{mouse}/{YYYY-MM-DD}/{filename}.mp4  (skimlab-owned)
  │     Commands:
  │       mkdir -p <target_dir>           (no sudo — EXPORT_DIR is skimlab-owned)
  │       sudo mv <source> <target>       (sudo needed — source is root-owned)
  │       sudo chown {NVR_USER}:{NVR_USER} <target>
  │
  └─ 4. Update session record
        Sets export_status = "completed" (or "failed")
        JSON sidecar already written at session end
```

**Sudoers policy:**

Because Frigate runs in Docker (files owned by root), the daemon needs `sudo` to move export files. A scoped sudoers policy limits this:

**File:** `{SUDOERS_POLICY}` (`/etc/sudoers.d/neurosurveillance-fs`)

```
skimlab ALL=(ALL) NOPASSWD: /usr/bin/mv, /usr/bin/chown
```

**Export directory structure:**

```
{EXPORT_DIR}/
└── {user_name}/
    └── {mouse_id}/
        └── YYYY-MM-DD/
            ├── 2602201430_HETCF3R1_basal.mp4
            └── 2602201430_HETCF3R1_basal_session.json
```

### 7. Storage Monitor (`storage_monitor.py`)

Monitors disk usage in a background thread and enforces EEG/EMG disk reservation. The 1.9 TB NVMe SSD is shared between Frigate video (~64 GB/day at 4 cameras, 1.7 Mbps each) and XDAQ EEG/EMG data. Without protection, long recording sessions could fill the disk and corrupt EEG data.

| Detail | Value |
|--------|-------|
| **Poll interval** | 30 seconds (configurable via `storage.poll_interval`) |
| **Disk check** | `os.statvfs("/")` — instant syscall |
| **Category scan** | `os.scandir` walk of configured paths, cached with 5-minute TTL |
| **Cache update** | Atomic dict reference swap (no locks) |
| **EEG reserve** | 200 GB (configurable via `storage.eeg_reserve_gb`) |
| **Warn threshold** | 75% disk used |
| **Critical threshold** | 90% disk used |

**Cap enforcement (fail-open):**

- Blocks **new** recordings only — never interrupts ongoing recordings
- EEG/EMG recording continues regardless (Radiens is uncontrolled)
- Recovery is automatic: when space is freed, the next session start succeeds
- If no cached data exists yet (e.g. daemon just started), recording is **allowed** (fail-open)

**Enforcement points in `daemon.py`:**

1. `_handle_session_start()` — only starts chambers with pending metadata set, then checks `can_start_recording(num_cameras)` before starting any Frigate recording. If denied, the entire session start is blocked.
2. `_handle_external_recording_on()` — checks before allowing a manual recording. If denied, publishes `OFF` to cancel the Frigate-initiated recording.

**Bitrate sync (`fetch_camera_bitrates`):**

On-demand function (called via `GET /api/storage/camera-bitrates`) that queries go2rtc APIs on the Pis to detect actual camera bitrates:

1. Fetches `GET http://{PI_IP}:1984/api/streams` from each Pi
2. Parses `--bitrate` from `rpicam-vid` exec commands in stream configs
3. Returns per-camera bitrate map + default fallback
4. Used by the frontend calculator for accurate storage estimates

**Status snapshot (`get_status()`):**

```json
{
  "total_bytes": 1920383410176,
  "used_bytes": 864172534579,
  "available_bytes": 1056210875597,
  "used_percent": 45.0,
  "categories": {
    "recordings": {"path": "/srv/frigate/storage/recordings", "bytes": 17179869184},
    "exports": {"path": "/srv/frigate/storage/exports", "bytes": 91268055040},
    "clips": {"path": "/srv/frigate/storage/clips", "bytes": 82837504},
    "sessions": {"path": "/opt/neurosurveillance/sessions", "bytes": 524288}
  },
  "eeg_reserve_bytes": 214748364800,
  "effective_available_bytes": 841462510797,
  "status_level": "ok",
  "camera_bitrate_mbps": 1.7,
  "can_record": true,
  "last_updated": 1743580800.0
}
```

### 8. Main Daemon (`daemon.py`)

Orchestrates all components. Entry point for the systemd service.

**Startup sequence:**

1. Load `config.yaml`
2. Initialize `StorageMonitor(config)` and start its background thread
3. Connect to MQTT broker (subscribes to `frigate/+/recordings/state`)
4. Publish `OFF` to all camera recording topics (clean slate)
5. If `manual_sessions.enabled`: wait **10 seconds** for Frigate to finish reasserting `record.enabled=true` from its config, drain stale `_expected_states`, then register the external recording change callback. This grace period prevents false manual sessions on every startup.
6. Connect to Radiens (`AllegoClient`) -- if unavailable, daemon continues and retries in the main loop
7. Start HTTP API server (background thread, passes `storage_monitor` to `init_api()`)
8. Enter main polling loop

**Threading model:**

The daemon uses Python threads (not asyncio):

| Thread | Purpose |
|--------|---------|
| **Main thread** | Radiens polling loop (1s interval) |
| **API thread** | Flask HTTP server (background, daemon=True) |
| **MQTT thread** | paho-mqtt `loop_start()` (background, daemon=True) |
| **Storage thread** | StorageMonitor polling (30s interval, daemon=True) |
| **Export threads** | One per export operation (background, short-lived) |

**Main loop (runs every 1 second):**

```python
while running:
    try:
        status = radiens_client.get_status()
        new_state = status.recording.mode  # R_ON or R_OFF

        if previous_state == "R_OFF" and new_state == "R_ON":
            _handle_session_start(status)  # starts sessions for chambers with metadata

        elif previous_state == "R_ON" and new_state == "R_OFF":
            _handle_session_end(status)    # ends ALL active sessions

        previous_state = new_state

    except RadiensConnectionError:
        log.warning("Radiens connection lost, retrying...")

    sleep(1.0)
```

**Shutdown sequence:**

1. Receive SIGTERM from systemd
2. Stop StorageMonitor background thread
3. If sessions are active: log warning, abort sessions, publish `OFF` to MQTT
4. Disconnect from MQTT
5. Exit cleanly

## Frontend Application

The desktop UI is a **Tauri v2** application with a **React 19** frontend, providing researchers with a visual interface for setting session metadata and monitoring recording status.

See [[frontend-reference|Frontend Reference]] for full component documentation, build commands, and hook details.

**Tech stack:**

| Layer | Technology | Version |
|-------|-----------|---------|
| Desktop shell | Tauri | v2 |
| Frontend framework | React + TypeScript | 19.1.0 / 5.8.3 |
| Build tool | Vite | 7.0.4 |
| Styling | Tailwind CSS + DaisyUI | 3.4.19 / 5.5.19 |

**Component architecture:**

```
App.tsx
├── Header
│   ├── Title, LiveClock, theme toggle, SettingsModal
│   ├── Storage badge (progress bar + %, color-coded from /api/health)
│   └── Critical storage / Daemon offline badges
├── ChamberSilo (one per configured camera, self-start grid items)
│   ├── Header bar (recording dot, camera offline badge, mouse ID)
│   ├── SessionSetup (metadata form)
│   ├── LiveStatus (recording state, session timer)
│   └── CameraPreview (Frigate snapshot embed, reports online/offline)
├── SystemHealth (MQTT, Radiens connection badges)
├── StoragePanel (disk usage, EEG reserve, inline calculator, bitrate sync)
└── SessionHistory (scrollable past sessions table)
```

**Polling architecture:**

| Hook | Endpoint | Interval | Purpose |
|------|----------|----------|---------|
| `useStatusPoll` | `GET /api/status` | 1.5s | Recording state, active sessions, pending metadata |
| `useHealthPoll` | `GET /api/health` | 5s | System health badges + header storage badge |
| `useStoragePoll` | `GET /api/storage` | 10s | StoragePanel disk usage, calculator data |
| `CameraPreview` | Frigate snapshot URL | 1s | Camera feed refresh + online/offline detection |

**Configuration:**

The `useSettings` hook manages user-configurable values in `localStorage`:
- Camera list (IDs, labels)
- Recording types (basal, recovery, sd, etc.)
- Lab members list
- Frigate base URL

## Security

| Measure | Implementation |
|---------|---------------|
| **Input sanitization** | `sanitize_input()` in `api.py` -- allows only `[a-zA-Z0-9_-]`, prevents path traversal and shell injection |
| **Scoped sudoers** | `/etc/sudoers.d/neurosurveillance-fs` -- limits `sudo` to specific `mkdir`, `mv`, `chown` commands under `{EXPORT_DIR}` |
| **Localhost-only API** | Flask binds to `127.0.0.1:8585` -- not accessible from the network |
| **No shell=True** | All `subprocess` calls use list syntax, never `shell=True` |
| **CORS** | Permissive (`*`) since API is localhost-only; needed for Tauri webview |

## Configuration

**File:** `/opt/neurosurveillance/config.yaml`

```yaml
# Session Daemon Configuration
# See production-values.md for actual values

daemon:
  poll_interval: 1.0          # seconds between Radiens polls
  timezone: "{TIMEZONE}"       # Asia/Seoul
  log_level: info              # debug, info, warning, error
  log_dir: "{SESSION_LOG_DIR}" # /opt/neurosurveillance/logs

api:
  host: "127.0.0.1"
  port: {SESSION_DAEMON_PORT}  # 8585

mqtt:
  host: "{NVR_IP}"             # 192.168.0.50 (localhost on ASUS PC)
  port: {MQTT_PORT}            # 1883

frigate:
  url: "http://localhost:{FRIGATE_WEB_PORT}"  # http://localhost:5000
  export_source_dir: "{SESSION_EXPORT_DIR}"   # /srv/frigate/storage/exports (Frigate Docker volume)
  export_dir: "{EXPORT_DIR}"                  # /opt/neurosurveillance/exports (skimlab-owned)

cameras:
  chamber_0: "{CAMERA_0_ID}"   # pi_cam_0
  chamber_1: "{CAMERA_1_ID}"   # pi_cam_1
  chamber_2: "{CAMERA_2_ID}"   # pi_cam_2
  chamber_3: "{CAMERA_3_ID}"   # pi_cam_3

sessions:
  data_dir: "{SESSION_DATA_DIR}"  # /opt/neurosurveillance/sessions

# Manual session auto-detection (Frigate UI Record button)
manual_sessions:
  enabled: true
  min_duration: 5              # Ignore recordings shorter than 5s

# NAS transfer (deferred -- not yet configured)
nas:
  enabled: false
  # host: "{NAS_TAILSCALE_IP}"
  # path: "/volume1/neurosurveillance"
  # method: "rsync"  # rsync or scp

storage:
  poll_interval: 30                    # Background disk check interval (seconds)
  paths:
    recordings: "/srv/frigate/storage/recordings"
    exports: "/srv/frigate/storage/exports"
    clips: "/srv/frigate/storage/clips"
    sessions: "/opt/neurosurveillance/sessions"
  eeg_reserve_gb: 200                  # Hard reserve for XDAQ EEG/EMG data
  warn_percent: 75                     # UI turns yellow
  critical_percent: 90                 # UI turns red, recordings may be blocked
  camera_bitrate_mbps: 1.7             # Measured actual bitrate (1.5 target + VBR overhead)
  go2rtc_apis:
    - "http://192.168.0.11:1984"       # Pi 1 (pi_cam_0, pi_cam_1)
    - "http://192.168.0.12:1984"       # Pi 2 (pi_cam_2, pi_cam_3)

lab_members:
  - andrea
```

> [!warning] Replace Variables
> Replace all `{VARIABLE}` placeholders with actual values from [[../../00-config/production-values|Production Values]] before deploying.

## Source Code Repository

All source code (backend + frontend) lives in a single git repo:

```
GitHub:  git@github.com:andrea966p/neurosurveillance.git (private)
Local:   /home/skimlab/Monitoring_project/neurosurveillance/
```

```
neurosurveillance/
├── backend/           # Python session daemon
│   ├── daemon.py
│   ├── api.py
│   ├── storage_monitor.py
│   ├── frigate_controller.py
│   ├── session_manager.py
│   ├── manual_session_manager.py
│   ├── session_utils.py
│   ├── radiens_poller.py
│   └── requirements.txt
├── frontend/          # Tauri + React desktop UI
│   ├── src/
│   ├── src-tauri/
│   └── package.json
└── config/            # Reference copies (not used by daemon directly)
    ├── config.yaml
    └── neurosurveillance-session.service
```

## Deployment Directory

The daemon runs from `/opt/neurosurveillance/`. The `session-daemon/` subdirectory is a **symlink** to the repo's `backend/` folder -- edits to the repo are live on next restart.

```
/opt/neurosurveillance/
├── config.yaml                # Production config (edited directly, not from repo)
├── session-daemon/ -> /home/skimlab/Monitoring_project/neurosurveillance/backend/
├── venv/                      # Python virtual environment
├── logs/                      # Daemon logs (rotating: 10MB x 5 files)
│   └── session-daemon.log
├── sessions/                  # Session JSON sidecars (both Radiens + manual)
│   ├── 2602201430_HETCF3R1_basal_session.json
│   └── 2602201430_manual_pi_cam_0_session.json
└── exports/                   # Organized MP4 exports
    └── andrea/
        └── HETCF3R1/
            └── 2026-02-20/
                └── 2602201430_HETCF3R1_basal.mp4
```

## Systemd Service

**File:** `/etc/systemd/system/neurosurveillance-session.service`

See [[session-service|Session Daemon Service]] for the full systemd unit file.

**Key properties:**
- `Restart=always` with 10s delay
- `After=docker.service` (Frigate and Mosquitto must be running)
- Runs as `{NVR_USER}` (not root)
- Working directory: `/opt/neurosurveillance`
- Environment: `PYTHONUNBUFFERED=1`, `HOME=/home/skimlab` (required so `radiens` can read `~/.config/radiens/session.json`)
- Resource limits: `MemoryMax=256M`, `MemorySwapMax=0`
- Kill signal: `SIGTERM` with 15s timeout

## Session Sidecar (`_session.json`)

Both Radiens and manual sessions produce JSON sidecars in `{SESSION_DATA_DIR}`.

**Radiens session example:**

```json
{
  "session_id": "uuid-here",
  "source": "radiens",
  "start_time_utc": 1771567800,
  "end_time_utc": 1771575000,
  "start_time_local": "2026-02-20T14:30:00+09:00",
  "end_time_local": "2026-02-20T16:30:00+09:00",
  "duration_seconds": 7200,
  "mouse_id": "HETCF3R1",
  "recording_type": "basal",
  "user_name": "andrea",
  "chamber": 0,
  "camera": "pi_cam_0",
  "radiens_xdat_filename": "HETCF3R1_basal_2026-02-20",
  "radiens_xdat_path": "/data/radiens/HETCF3R1_basal_2026-02-20.xdat",
  "video_filename": "2602201430_HETCF3R1_basal.mp4",
  "export_status": "completed",
  "nas_transfer_status": "skipped"
}
```

**Manual session example:**

```json
{
  "session_id": "uuid-here",
  "source": "manual",
  "start_time_utc": 1771567800,
  "end_time_utc": 1771575000,
  "start_time_local": "2026-02-20T14:30:00+09:00",
  "end_time_local": "2026-02-20T16:30:00+09:00",
  "duration_seconds": 7200,
  "mouse_id": "HETCF3R1",
  "recording_type": "basal",
  "user_name": "andrea",
  "camera": "pi_cam_0",
  "video_filename": "2602201430_HETCF3R1_basal.mp4",
  "export_status": "completed"
}
```

## Failure Modes

| Scenario | Behavior | Data Impact |
|----------|----------|-------------|
| **Daemon crashes mid-session** | Frigate keeps recording (MQTT state persists). On restart, daemon publishes OFF and exports what's available. | Extra footage, no loss |
| **Radiens disconnects** | Poller logs warning, retries every poll cycle. No Frigate state change. | None -- recording continues if it was ON |
| **MQTT broker down** | Daemon cannot toggle recording. Logs error. Radiens data is unaffected. | Video may not start/stop on time |
| **Frigate unreachable** | Export fails. Daemon logs error, retains session metadata for manual recovery. | Video exists in Frigate but export must be done manually |
| **No metadata set** | Daemon uses defaults: `unknown` mouse ID, `unknown` type. Session still runs and exports. | Researcher must rename files manually |
| **Export file move fails** | `sudo mv` fails (permissions, disk full). Daemon logs error, sets `export_status: "failed"`. Original file remains in Frigate exports. | File safe in Frigate exports dir |
| **Long export (large file)** | Frigate lists export immediately with `in_progress: true` while ffmpeg multiplexes. Daemon polls until `in_progress` clears before moving the file. | None -- daemon waits for completion |
| **Disk below EEG reserve** | New recordings blocked (cap enforcement). Existing recordings continue. EEG unaffected. Recovery automatic when space freed. | None -- fail-open design, EEG always protected |
| **Power failure** | Everything stops. On reboot, systemd restarts daemon, which resets to OFF. | Partial session -- manual Frigate export needed for the gap |

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `radiens` | 4.0.0 | NeuroNexus Radiens Python API (PyPI). Production auth mode uses Cognito session tokens from `~/.config/radiens/session.json`. |
| `paho-mqtt` | >= 2.0 | MQTT client library |
| `flask` | >= 3.0 | HTTP API framework |
| `requests` | >= 2.31 | Frigate HTTP API calls |
| `pyyaml` | >= 6.0 | Config file parsing |

## Related

- [[frontend-reference|Frontend Reference]] -- desktop UI component details
- [[../../00-config/production-values|Production Values]] -- all IPs, ports, paths
- [[../frigate/config-yml|Frigate Config]] -- recording settings, MQTT toggle prerequisite
- [[../frigate/docker-compose|Docker Compose]] -- Frigate + Mosquitto deployment
- [[../../02-procedures/session-recording-workflow|Session Recording Workflow]] -- user-facing procedure

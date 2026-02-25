---
tags: [infrastructure, session-daemon, architecture]
created: 2026-02-20
status: draft
version: "1.2"
---

# Session Daemon Architecture

The **NeuroSurveillance Session Daemon** synchronizes Frigate video recording with NeuroNexus Radiens EEG/EMG data acquisition. When a researcher starts or stops EEG recording in Radiens, the daemon automatically starts/stops video recording in Frigate, then exports and organizes the video files.

## Design Principles

1. **Autonomous core** -- the recording sync loop (Radiens poll -> Frigate toggle) runs independently and does not depend on the UI or API. If no metadata is set, the daemon uses safe defaults (`unknown` mouse ID, timestamp-based filenames). No data is ever lost.
2. **Fail-safe bias** -- if the daemon crashes mid-session with recording ON, that is safe (extra footage, not lost footage). On restart, the daemon resets recording to OFF.
3. **No Radiens control** -- the daemon only *observes* Radiens state. It never starts/stops EEG recording. The researcher controls Radiens directly.
4. **Metadata is optional** -- the HTTP API accepts session metadata (mouse ID, recording type, user) before a session. If not provided, the session still runs with fallback values.

## System Overview

```
                                    ASUS Mini PC (192.168.0.50)
  ┌─────────────┐          ┌──────────────────────────────────────────────┐
  │  Raspberry   │  RTSP   │                                              │
  │  Pi 5        │────────>│  Frigate NVR (Docker, port 5000)             │
  │  go2rtc      │         │    - Records pi_cam_0, pi_cam_1              │
  │  192.168.0.11│         │    - MQTT-controlled recording on/off        │
  └─────────────┘         │    - Export API for named MP4 clips           │
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
                           │  │  7. Names MP4, logs session      │        │
                           │  │  8. (Future) Transfers to NAS    │        │
                           │  │                                  │        │
                           │  │  HTTP API on 127.0.0.1:8585      │        │
                           │  │  (metadata input from UI)        │        │
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
              │                    │
              v                    v
         Start Frigate        Stop Frigate
         recording            recording
         Log start_ts         Call export API
                              Log session
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
| **Frigate timezone** | Timestamps in UTC (system timezone `Asia/Seoul`, UTC+9) |

> [!warning] MQTT Recording Toggle Prerequisite
> `record.enabled: true` must be set in Frigate's `config.yml` for the MQTT toggle to work. If disabled in config, MQTT/UI toggle has no effect. The current production config already has this set -- see [[../frigate/config-yml|Frigate Config]].

**Recording control flow:**

1. **On startup:** Publish `OFF` to all camera recording topics (clean slate)
2. **On session start:** Publish `ON` to the active chamber's camera topic
3. **On session end:** Publish `OFF`, then call the export API

**External change detection (two-stage filter):**

The controller subscribes to `frigate/+/recordings/state` and uses two guards to filter incoming state messages:

1. **`_expected_states` check:** Before publishing ON/OFF, the daemon records the expected state. When a matching state message arrives, it is consumed as a self-echo and ignored.
2. **`_last_known_state` check:** Even if Stage 1 passes, the message is ignored if it carries the **same state** as the previous one (no actual transition). This suppresses Frigate's periodic reassertion of `ON` from `config.yml record.enabled=true`, which would otherwise trigger false manual sessions.

Only messages that pass both filters (not self-initiated AND an actual state transition) fire the external change callback to the daemon.

**Export flow:**

1. Daemon records `start_timestamp` (Unix epoch, UTC) when session begins
2. On session end, records `end_timestamp`
3. Timestamps are padded ±2 seconds to ensure Frigate's segment boundaries are fully included
4. Calls Frigate export API with `{"name": "<session_filename>"}` in the POST body — Frigate uses this name as the export label
5. Waits for export to complete (polls `GET /api/exports` until the export ID appears)
6. Export runs in a **background thread** so it does not block the main Radiens polling loop

**Timestamp handling:**
- All internal timestamps use UTC Unix epoch
- Frigate export API expects UTC timestamps
- Human-readable timestamps in session logs use `{TIMEZONE}` (`Asia/Seoul`)
- Filename timestamps (`YYMMDDHHMM`) use local time (`Asia/Seoul`)

### 3. Session Manager (`session_manager.py`)

Manages session metadata and logging.

**Session lifecycle:**

```
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. METADATA SET (optional, via HTTP API)                    │
  │    User sets: mouse_id, recording_type, user_name, chamber  │
  │    If not set: defaults to "unknown", "unknown", "unknown"  │
  └─────────────────────────┬───────────────────────────────────┘
                            v
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. SESSION START (automatic, triggered by Radiens R_ON)     │
  │    Daemon records: start_timestamp, camera, chamber         │
  │    Captures: Radiens base_name (XDAT filename)              │
  └─────────────────────────┬───────────────────────────────────┘
                            v
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. SESSION END (automatic, triggered by Radiens R_OFF)      │
  │    Daemon records: end_timestamp, duration                  │
  │    Triggers: Frigate export (background), session log       │
  └─────────────────────────┬───────────────────────────────────┘
                            v
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. POST-SESSION (automatic, background thread)               │
  │    - Export MP4 from Frigate (±2s buffer on timestamps)     │
  │    - Frigate names export using session filename            │
  │    - Write _session.json sidecar                            │
  │    - (Future) Transfer to NAS                               │
  │    - Clear metadata for next session                        │
  └─────────────────────────────────────────────────────────────┘
```

**Filename format:** `YYMMDDHHMM_mouseID_type.mp4`

| Component | Example | Source |
|-----------|---------|--------|
| `YYMMDDHHMM` | `2602201430` | Session start time (local, `Asia/Seoul`) |
| `mouseID` | `HETCF3R1` | From metadata API (or `unknown`) |
| `type` | `basal` | From metadata API (or `unknown`) |

**Session sidecar (`_session.json`):**

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
  "video_filename": "2602201430_HETCF3R1_basal.mp4",
  "export_status": "completed",
  "nas_transfer_status": "skipped"
}
```

**Output file locations:**

| File | Location | Written by |
|------|----------|------------|
| Exported MP4 | `/srv/frigate/storage/exports/` | Frigate (via export API) |
| Session JSON sidecar | `/opt/neurosurveillance/sessions/` | Session daemon |
| Desktop shortcut | `~/Desktop/Frigate Exports` → `/srv/frigate/storage/exports/` | Symlink |

> [!note] The daemon does NOT move MP4 files. Frigate writes exports directly to its Docker volume. The `export_dir` in config.yaml is used only for JSON sidecars.

### 3b. Manual Session Manager (`manual_session_manager.py`)

Handles recordings triggered externally via Frigate's web UI (clicking the Record button on a camera). Each camera is tracked independently.

**Detection flow:**

```
User clicks Record in Frigate UI on pi_cam_0
  → Frigate publishes: frigate/pi_cam_0/recordings/state = ON
  → FrigateController detects: external ON (not self-initiated)
  → ManualSessionManager.start_recording("pi_cam_0")
  → Records start timestamp

User clicks Stop in Frigate UI
  → Frigate publishes: frigate/pi_cam_0/recordings/state = OFF
  → ManualSessionManager.stop_recording("pi_cam_0")
  → Records end timestamp
  → Background thread: calls Frigate export API → MP4 → JSON sidecar
  → MP4 appears in /srv/frigate/storage/exports/
```

**Key behaviors:**
- **Radiens priority:** If a Radiens session is active on a camera, external Record ON is ignored
- **Min duration filter:** Recordings shorter than `min_duration` (default 5s) are discarded (accidental clicks)
- **Per-camera:** cam_0 and cam_1 can have independent manual sessions
- **Naming:** `YYMMDDHHMM_manual_pi_cam_0.mp4` (no mouse metadata for manual sessions)
- **JSON sidecar:** Same as Radiens sessions but with `"source": "manual"`

**Manual session sidecar example:**

```json
{
  "session_id": "uuid-here",
  "source": "manual",
  "start_time_utc": 1771567800,
  "end_time_utc": 1771575000,
  "start_time_local": "2026-02-20T14:30:00+09:00",
  "end_time_local": "2026-02-20T16:30:00+09:00",
  "duration_seconds": 7200,
  "camera": "pi_cam_0",
  "video_filename": "2602201430_manual_pi_cam_0.mp4",
  "export_status": "completed"
}
```

### 4. HTTP API (`api.py`)

Lightweight REST API on `127.0.0.1:{SESSION_DAEMON_PORT}` for the UI to set session metadata.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /api/status` | GET | Daemon status, current session state, Radiens connection, active manual recordings |
| `POST /api/session/metadata` | POST | Set metadata for next session (mouse_id, type, user, chamber) |
| `GET /api/session/current` | GET | Current Radiens session info (if active) |
| `GET /api/session/history` | GET | List of past sessions (`?source=radiens\|manual` filter, `?limit=N`) |
| `GET /api/session/manual` | GET | Active and recent manual recording sessions |
| `GET /api/health` | GET | Health check (for systemd watchdog) |

> [!tip] Localhost Only
> The API binds to `127.0.0.1` only -- not accessible from the network. This is intentional: the UI runs on the same machine.
>
> [!tip] CORS Enabled
> The API returns CORS headers (`Access-Control-Allow-Origin: *`) so Tauri webview/browser development can call the localhost API successfully.

**Example: Set metadata before a session**

```bash
curl -X POST http://127.0.0.1:8585/api/session/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "mouse_id": "HETCF3R1",
    "recording_type": "basal",
    "user_name": "andrea",
    "chamber": 0
  }'
```

### 5. Main Daemon (`daemon.py`)

Orchestrates all components. Entry point for the systemd service.

**Startup sequence:**

1. Load `config.yaml`
2. Connect to MQTT broker (subscribes to `frigate/+/recordings/state`)
3. Publish `OFF` to all camera recording topics (clean slate)
4. If `manual_sessions.enabled`: wait **10 seconds** for Frigate to finish reasserting `record.enabled=true` from its config, drain stale `_expected_states`, then register the external recording change callback. This grace period prevents false manual sessions on every startup.
5. Connect to Radiens (`AllegoClient`) -- if unavailable, daemon continues and retries in the main loop
6. Start HTTP API server (background thread)
7. Enter main polling loop

**Main loop (runs every 1 second):**

```python
while running:
    try:
        status = radiens_client.get_status()
        new_state = status.recording.mode  # RecordingSpec.mode: R_ON or R_OFF

        if previous_state == "R_OFF" and new_state == "R_ON":
            start_session()

        elif previous_state == "R_ON" and new_state == "R_OFF":
            end_session()

        previous_state = new_state

    except RadiensConnectionError:
        log.warning("Radiens connection lost, retrying...")

    sleep(1.0)
```

**Shutdown sequence:**

1. Receive SIGTERM from systemd
2. If session is active: log warning, publish `OFF` to MQTT, write partial session log
3. Disconnect from MQTT
4. Exit cleanly

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
  export_dir: "{SESSION_EXPORT_DIR}"          # /srv/frigate/storage/exports

cameras:
  chamber_0: "{CAMERA_0_ID}"   # pi_cam_0
  chamber_1: "{CAMERA_1_ID}"   # pi_cam_1

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

lab_members:
  - andrea
  - add_more_here
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

The daemon runs from `/opt/neurosurveillance/`. The `session-daemon/` subdirectory is a **symlink** to the repo's `backend/` folder — edits to the repo are live on next restart.

```
/opt/neurosurveillance/
├── config.yaml                # Production config (edited directly, not from repo)
├── session-daemon/ -> /home/skimlab/Monitoring_project/neurosurveillance/backend/
├── venv/                      # Python virtual environment
├── logs/                      # Daemon logs
│   └── session-daemon.log
└── sessions/                  # Session JSON sidecars (both Radiens + manual)
    ├── 2602201430_HETCF3R1_basal_session.json
    └── 2602201430_manual_pi_cam_0_session.json
```

Exported MP4s are written by Frigate to `/srv/frigate/storage/exports/` (see [[#Output file locations]]).

## Systemd Service

**File:** `/etc/systemd/system/neurosurveillance-session.service`

See [[session-service|Session Daemon Service]] for the full systemd unit file.

**Key properties:**
- `Restart=always` with 10s delay
- `After=docker.service` (Frigate and Mosquitto must be running)
- Runs as `{NVR_USER}` (not root)
- Working directory: `/opt/neurosurveillance`
- Environment: `PYTHONUNBUFFERED=1`, `HOME=/home/skimlab` (required so `radiens` can read `~/.config/radiens/session.json`)

## Failure Modes

| Scenario | Behavior | Data Impact |
|----------|----------|-------------|
| **Daemon crashes mid-session** | Frigate keeps recording (MQTT state persists). On restart, daemon publishes OFF and exports what's available. | Extra footage, no loss |
| **Radiens disconnects** | Poller logs warning, retries every poll cycle. No Frigate state change. | None -- recording continues if it was ON |
| **MQTT broker down** | Daemon cannot toggle recording. Logs error. Radiens data is unaffected. | Video may not start/stop on time |
| **Frigate unreachable** | Export fails. Daemon logs error, retains session metadata for manual recovery. | Video exists in Frigate but export must be done manually |
| **No metadata set** | Daemon uses defaults: `unknown` mouse ID, `unknown` type. Session still runs and exports. | Researcher must rename files manually |
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

- [[../../00-config/production-values|Production Values]] -- all IPs, ports, paths
- [[../frigate/config-yml|Frigate Config]] -- recording settings, MQTT toggle prerequisite
- [[../frigate/docker-compose|Docker Compose]] -- Frigate + Mosquitto deployment
- [[../../02-procedures/session-recording-workflow|Session Recording Workflow]] -- user-facing procedure

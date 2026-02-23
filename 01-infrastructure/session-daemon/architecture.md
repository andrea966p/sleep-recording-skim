---
tags: [infrastructure, session-daemon, architecture]
created: 2026-02-20
status: draft
version: "1.0"
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
                           │  │  7. Renames MP4, logs session    │        │
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
- If Radiens was in `R_ON` when connection was lost and reconnects still in `R_ON`, no duplicate start is triggered (state tracking prevents this).
- If Radiens was in `R_ON` when connection was lost and reconnects in `R_OFF`, the daemon treats this as a session end and exports normally.

### 2. Frigate Controller (`frigate_controller.py`)

Controls Frigate recording via MQTT and handles video export via HTTP API.

| Detail | Value |
|--------|-------|
| **MQTT broker** | `{NVR_IP}:1883` (Mosquitto, Docker) |
| **MQTT topic** | `frigate/{CAMERA_ID}/recordings/set` |
| **MQTT payload** | `ON` or `OFF` |
| **Export API** | `POST http://{NVR_IP}:5000/api/export/{camera}/start/{start}/end/{end}` |
| **Frigate timezone** | Timestamps in UTC (system timezone `Asia/Seoul`, UTC+9) |

> [!warning] MQTT Recording Toggle Prerequisite
> `record.enabled: true` must be set in Frigate's `config.yml` for the MQTT toggle to work. If disabled in config, MQTT/UI toggle has no effect. The current production config already has this set -- see [[../frigate/config-yml|Frigate Config]].

**Recording control flow:**

1. **On startup:** Publish `OFF` to all camera recording topics (clean slate)
2. **On session start:** Publish `ON` to the active chamber's camera topic
3. **On session end:** Publish `OFF`, then call the export API

**Export flow:**

1. Daemon records `start_timestamp` (Unix epoch, UTC) when session begins
2. On session end, records `end_timestamp`
3. Calls Frigate export API: `POST /api/export/{camera}/start/{start_ts}/end/{end_ts}`
4. Waits for export to complete (poll export status)
5. Renames exported MP4 to session filename format

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
  │    Triggers: Frigate export, file rename, session log       │
  └─────────────────────────┬───────────────────────────────────┘
                            v
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. POST-SESSION (automatic)                                 │
  │    - Export MP4 from Frigate                                │
  │    - Rename to YYMMDDHHMM_mouseID_type.mp4                  │
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

### 4. HTTP API (`api.py`)

Lightweight REST API on `127.0.0.1:{SESSION_DAEMON_PORT}` for the UI to set session metadata.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /api/status` | GET | Daemon status, current session state, Radiens connection |
| `POST /api/session/metadata` | POST | Set metadata for next session (mouse_id, type, user, chamber) |
| `GET /api/session/current` | GET | Current session info (if active) |
| `GET /api/session/history` | GET | List of past sessions |
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
2. Connect to MQTT broker
3. Publish `OFF` to all camera recording topics (reset state)
4. Connect to Radiens (`AllegoClient`)
5. Start HTTP API server (background thread)
6. Enter main polling loop

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
  export_dir: "{SESSION_EXPORT_DIR}"          # /opt/neurosurveillance/exports

cameras:
  chamber_0: "{CAMERA_0_ID}"   # pi_cam_0
  chamber_1: "{CAMERA_1_ID}"   # pi_cam_1

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

## Directory Structure

```
/opt/neurosurveillance/
├── config.yaml              # Daemon configuration
├── session-daemon/          # Python source code
│   ├── daemon.py            # Main entry point
│   ├── radiens_poller.py    # Radiens state polling
│   ├── frigate_controller.py # MQTT + export control
│   ├── session_manager.py   # Session lifecycle + logging
│   ├── api.py               # HTTP REST API
│   └── requirements.txt     # Python dependencies
├── logs/                    # Daemon logs
│   └── session-daemon.log
├── exports/                 # Exported MP4s (staging area)
└── sessions/                # Session JSON logs
    └── 2026-02-20_HETCF3R1_basal_session.json
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

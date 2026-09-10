# NeuroSurveillance: Backend Architecture

This document provides a detailed overview of the Python daemon architecture that manages the NeuroSurveillance system.

## 1. Core Daemon (`daemon.py`)
The Python backend runs entirely as a background `systemd` service on the host Linux machine. The central `daemon.py` acts as the primary orchestrator, unifying the different internal modules via a threaded polling loop (`threading` + `time.sleep`).

Its primary responsibilities are:
- Loading configuration from `/opt/neurosurveillance/config.yaml`.
- Initializing the MQTT client to establish two-way communication with Frigate.
- Booting the Flask-based REST API onto a background thread to service the frontend UI.
- Running a constant polling loop (1Hz) to check for external triggers from both Radiens automation and Frigate manual recording buttons.

## 2. API Server (`api.py`)
The REST API provides the interface between the deeply nested backend controllers and the user-facing desktop application.
It provides explicit, chamber-specific endpoints to handle the multi-chamber recording model.

Key endpoints include:
- `GET /api/status`: Returns the active DaemonStatus (Radiens connections, active automated sessions, bounded pending metadata, and detected manual recordings).
- `POST /api/session/metadata`: Receives and bounds `{user_name, mouse_id, recording_type, chamber}` injected by the user before a session starts.
- `GET /api/session/history`: Parses all saved JSON session sidecars and returns a chronologically sorted history array to populate the UI tables.

## 3. Frigate Controller (`frigate_controller.py`)
This module is explicitly dedicated to interacting with the remote Frigate NVR HTTP API and MQTT broker.
- **Recording Automation**: Dynamically publishes `ON` or `OFF` to `frigate/camera_id/recordings/set` based on Radiens triggers.
- **Manual Detection**: Subscribes to the `state` topics to instantly alert the daemon when a user presses "Record" directly in the Frigate Web UI.
- **Video Exporting**: Exposes robust asynchronous methods (`wait_for_export`) to tell Frigate exactly which timestamps to extract into an MP4 clip once a session ends.

## 4. Session Managers
To cleanly isolate distinct logic sets, the backend tracks session persistence and sidecar logic via two dedicated managers.

### A. Radiens `SessionManager`
Responsible strictly for automated, EEG-triggered recordings. 
- Listens to the `RadiensPoller`.
- Tracks `SessionRecord` objects and saves `[timestamp]_metadata_session.json` sidecars flagged with `source: radiens`.

### B. `ManualSessionManager`
Responsible for manual recordings directly requested by researchers.
- Tracks `ManualSessionRecord` objects.
- Listens sequentially to the Frigate Controller's custom callback hooks.
- Tracks its own independent target directory paths.

## 5. Security & Sudo Integration
The daemon leverages tightly scoped Linux `sudoers` policies (`/etc/sudoers.d/neurosurveillance-fs`) to securely cross over permission boundaries.
Because the daemon runs as the `skimlab` user, but needs to manipulate files created by `root` (Frigate Docker), it intercepts Frigate's video drops via raw `subprocess.run(["sudo", "mv", ...])` calls. This guarantees flawless file handling without compromising the host machine's broader security.

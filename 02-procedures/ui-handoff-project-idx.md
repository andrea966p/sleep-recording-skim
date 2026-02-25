---
tags: [procedure, session-daemon, ui, handoff]
created: 2026-02-23
status: draft
---

# UI Handoff — Project IDX Build Prompt

> [!tip] How to Use This Document
> Copy the entire **BUILD PROMPT** section below and paste it into Google Project IDX (or any AI app-building tool) as the initial prompt. It contains everything the AI agent needs to build the frontend app.

---

## BUILD PROMPT

You are building a **Tauri desktop application** for a neuroscience lab. The app is a dashboard that lets researchers set up and monitor synchronized video + EEG recording sessions. It talks to a Python backend daemon via a REST API on `localhost:8585`.

### Project Overview

**What this app does:** Researchers record mouse sleep experiments using two systems simultaneously:
1. **NeuroNexus Radiens** — EEG/EMG brain signal recording (researcher controls this directly)
2. **Frigate NVR** — video recording (controlled automatically by a background daemon)

A Python daemon polls the Radiens EEG software every second. When the researcher starts/stops EEG recording, the daemon automatically starts/stops video recording in sync. The daemon exposes a REST API for the UI to:
- Set session metadata (mouse ID, recording type, chamber, user name) before a session
- Monitor real-time status (recording state, connection health, active session info)
- View history of past sessions

**The daemon is already built and running. You are only building the UI.**

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop shell | **Tauri** (latest stable) |
| Frontend framework | **React** + **TypeScript** |
| Styling | **Tailwind CSS** + **DaisyUI** |
| State management | React hooks (`useState`, `useEffect`), no external state library needed |
| Data fetching | `fetch` API with polling (no WebSocket) |
| Build tool | Vite |

### Target Platform

- **OS:** Ubuntu 24.04 LTS (x86_64)
- **Desktop environment:** GNOME (default Ubuntu)
- **Screen:** Standard 1920x1080 monitor
- **Users:** Researchers and students with no terminal/programming experience. The UI must be intuitive, clear, and require no documentation to use.

---

## Dashboard Layout

The app is a **single-window dashboard** with 5 panels. Use a responsive grid layout:

```
┌──────────────────────────────────────────────────────────────┐
│  NeuroSurveillance Session Controller            [_ □ ✕]    │
├──────────────────────┬───────────────────────────────────────┤
│                      │                                       │
│   SESSION SETUP      │        CAMERA PREVIEW                 │
│   (metadata form)    │   ┌─────────┐  ┌─────────┐           │
│                      │   │ Chamber │  │ Chamber │           │
│   Mouse ID: [____]   │   │    0    │  │    1    │           │
│   Type: [dropdown]   │   │         │  │         │           │
│   Chamber: [0] [1]   │   └─────────┘  └─────────┘           │
│   User: [dropdown]   │                                       │
│   [Submit] [Clear]   │                                       │
│                      ├───────────────────────────────────────┤
├──────────────────────┤                                       │
│                      │        SESSION HISTORY                │
│   LIVE STATUS        │   ┌───────────────────────────────┐   │
│                      │   │ Date  Mouse  Type  Dur  Stat  │   │
│   Recording: ● R_OFF │   │ ─────────────────────────────  │   │
│   Radiens: ✓ Conn.   │   │ 02/20 HETCF  basal 2h  done  │   │
│   MQTT: ✓ Conn.      │   │ 02/19 HETCF  sd    4h  done  │   │
│   Session: idle      │   │ ...                            │   │
│   Duration: --:--    │   └───────────────────────────────┘   │
│                      │                                       │
│   SYSTEM HEALTH      │                                       │
│   Daemon: ✓          │                                       │
│   Frigate: ✓         │                                       │
│                      │                                       │
└──────────────────────┴───────────────────────────────────────┘
```

### Panel 1: Session Setup (top-left)

A form for setting metadata before the researcher starts EEG recording.

**Fields:**

| Field | Input Type | Validation | Notes |
|-------|-----------|------------|-------|
| Mouse ID | Text input | Free text, 1-20 chars, alphanumeric + hyphens | e.g. `HETCF3R1` |
| Recording Type | Dropdown select | Options: `basal`, `recovery`, `sd` (sleep deprivation) | Default: `basal` |
| Chamber | Toggle buttons (0 / 1) | Must be 0 or 1 | Default: 0. Highlight the selected chamber. The corresponding camera preview should also get a highlight/border. |
| User Name | Dropdown select | Options come from lab members list (see below) | Default: first member |

**Lab members list:** `["andrea"]` (hardcode for now; this will grow)

**Buttons:**
- **"Set Metadata"** — `POST /api/session/metadata` with form values. Show success toast. Button should be disabled if form hasn't changed from current pending metadata.
- **"Clear"** — `DELETE /api/session/metadata`. Resets form to defaults. Show confirmation toast.

**Behavior:**
- On app load, fetch `GET /api/status` and populate the form with `pending_metadata` values.
- If a session is currently active (recording in progress), the form should be **read-only with a lock indicator** and show the active session's metadata. Display a message like "Session in progress — metadata locked".
- After a session ends, the form unlocks and is cleared (the daemon clears metadata automatically).

### Panel 2: Camera Preview (top-right)

Show live camera feeds from both chambers side by side.

**Camera feed URLs (Frigate snapshot API):**
- Chamber 0: `http://192.168.0.50:5000/api/pi_cam_0/latest.jpg`
- Chamber 1: `http://192.168.0.50:5000/api/pi_cam_1/latest.jpg`

**Implementation:**
- Use `<img>` tags that reload every 1 second (append `?t=<timestamp>` to bust cache)
- Each camera feed should be labeled: "Chamber 0 — pi_cam_0" and "Chamber 1 — pi_cam_1"
- The camera matching the currently selected chamber should have a colored border/highlight (e.g. green border when selected)
- If the image fails to load, show a placeholder with "Camera offline" text
- Camera resolution is 1024x768 — maintain aspect ratio when scaling

**Alternative (MJPEG stream):**
If snapshot polling looks choppy, you can use Frigate's MJPEG stream instead:
- Chamber 0: `http://192.168.0.50:5000/api/pi_cam_0` (continuous MJPEG)
- Chamber 1: `http://192.168.0.50:5000/api/pi_cam_1` (continuous MJPEG)

Use an `<img>` tag with `src` set to the MJPEG URL — the browser handles it natively as a continuous stream. MJPEG uses more bandwidth but is smoother.

### Panel 3: Live Status (bottom-left, upper section)

Real-time status display, updated by polling `GET /api/status` every 1.5 seconds.

**Status indicators:**

| Indicator | Source field | Display |
|-----------|-------------|---------|
| Recording State | `radiens.recording_state` | Large colored dot: **red pulsing** = `R_ON` (recording), **gray** = `R_OFF` (idle), **yellow** = `UNKNOWN` |
| Radiens Connection | `radiens.connected` | Green checkmark if `true`, red X if `false` |
| MQTT Connection | `mqtt.connected` | Green checkmark if `true`, red X if `false` |
| Active Session | `session` | If not null: show mouse_id, type, chamber, and a running duration timer. If null: show "No active session" |
| Pending Metadata | `pending_metadata.is_default` | If `true`: show subtle warning "No metadata set — defaults will be used" |

**Running duration timer:**
When `session` is not null, calculate elapsed time from `session.start_time_local` (ISO 8601 string) to now. Display as `HH:MM:SS`, updating every second client-side (don't poll for this — compute locally).

**Recording state change behavior:**
- When state transitions from `OFF` to `ON`: briefly flash the recording indicator, show a toast notification "Recording started"
- When state transitions from `ON` to `OFF`: show toast "Recording stopped — exporting video..."

### Panel 4: System Health (bottom-left, lower section)

Below the live status panel. Shows overall system health at a glance.

**Data source:** `GET /api/health` (poll every 5 seconds, not as frequent as status)

| Component | Source | Display |
|-----------|--------|---------|
| Daemon | Always "running" if API responds | Green badge |
| Radiens | `radiens_connected` | Green/red badge |
| MQTT | `mqtt_connected` | Green/red badge |
| Frigate | If camera snapshots load successfully | Green/red badge |

If `/api/health` returns HTTP 503, show an overall "Degraded" warning badge. If the fetch fails entirely (daemon is down), show "Daemon Offline" in red.

### Panel 5: Session History (bottom-right)

Scrollable table of past sessions, newest first.

**Data source:** `GET /api/session/history?limit=50` (fetch on app load and after each session ends)

**Table columns:**

| Column | Source field | Format |
|--------|-------------|--------|
| Date | `start_time_local` | `MM/DD HH:MM` |
| Mouse ID | `mouse_id` | As-is |
| Type | `recording_type` | As-is |
| Chamber | `chamber` | `0` or `1` |
| Duration | `duration_seconds` | `Xh Ym` or `Xm Ys` |
| Status | `export_status` | Badge: green "completed", yellow "pending", red "failed" |

**Click to expand:** When a row is clicked, expand it to show full session details:

| Detail | Source field |
|--------|-------------|
| Session ID | `session_id` |
| Start time | `start_time_local` |
| End time | `end_time_local` |
| Camera | `camera` |
| User | `user_name` |
| Video file | `video_filename` |
| EEG file | `radiens_xdat_filename` |
| Export status | `export_status` |
| NAS transfer | `nas_transfer_status` |

---

## REST API Specification

The daemon runs on `http://127.0.0.1:8585`. All endpoints return JSON. No authentication is required. API responses include CORS headers for Tauri/webview/browser compatibility.

### `GET /api/status`

Returns full daemon status overview. **This is the primary polling endpoint.**

**Response 200:**
```json
{
  "daemon": "running",
  "radiens": {
    "connected": true,
    "recording_state": "R_OFF"
  },
  "mqtt": {
    "connected": true
  },
  "session": null,
  "pending_metadata": {
    "mouse_id": "unknown",
    "recording_type": "unknown",
    "user_name": "unknown",
    "chamber": 0,
    "is_default": true
  },
  "manual_recordings": {}
}
```

**When a session is active (`session` is not null):**
```json
{
  "daemon": "running",
  "radiens": {
    "connected": true,
    "recording_state": "R_ON"
  },
  "mqtt": {
    "connected": true
  },
  "session": {
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "mouse_id": "HETCF3R1",
    "recording_type": "basal",
    "chamber": 0,
    "camera": "pi_cam_0",
    "start_time_local": "2026-02-20T14:30:00+09:00"
  },
  "pending_metadata": {
    "mouse_id": "HETCF3R1",
    "recording_type": "basal",
    "user_name": "andrea",
    "chamber": 0,
    "is_default": false
  },
  "manual_recordings": {
    "pi_cam_0": {
      "session_id": "...",
      "camera": "pi_cam_0",
      "start_time_local": "2026-02-20T14:30:00+09:00"
    }
  }
}
```

### `POST /api/session/metadata`

Set metadata for the next recording session. Partial updates are allowed — only provided fields are changed.

**Request body (JSON):**
```json
{
  "mouse_id": "HETCF3R1",
  "recording_type": "basal",
  "user_name": "andrea",
  "chamber": 0
}
```

All fields are optional. You can send just `{"mouse_id": "HETCF3R1"}` to update only that field.

**Validation:**
- `chamber` must be `0` or `1` (integer). Returns 400 if invalid.
- `user_name` is validated against the lab members list but only logs a warning (does not reject).

**Response 200:**
```json
{
  "status": "ok",
  "metadata": {
    "mouse_id": "HETCF3R1",
    "recording_type": "basal",
    "user_name": "andrea",
    "chamber": 0,
    "is_default": false
  }
}
```

**Error 400:**
```json
{
  "error": "Invalid chamber: 5. Must be 0 or 1."
}
```

### `DELETE /api/session/metadata`

Clear all pending metadata, resetting to defaults.

**Response 200:**
```json
{
  "status": "ok",
  "message": "Metadata cleared to defaults"
}
```

### `GET /api/session/current`

Get the currently active session details, if any.

**Response 200 (no active session):**
```json
{
  "session": null
}
```

**Response 200 (session active):**
```json
{
  "session": {
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "start_time_utc": 1771567800.0,
    "end_time_utc": 0.0,
    "start_time_local": "2026-02-20T14:30:00+09:00",
    "end_time_local": "",
    "duration_seconds": 0.0,
    "mouse_id": "HETCF3R1",
    "recording_type": "basal",
    "user_name": "andrea",
    "chamber": 0,
    "camera": "pi_cam_0",
    "radiens_xdat_filename": "HETCF3R1_basal_2026-02-20",
    "radiens_xdat_path": "/data/radiens/HETCF3R1_basal_2026-02-20.xdat",
    "video_filename": "",
    "export_status": "pending",
    "nas_transfer_status": "skipped"
  }
}
```

### `GET /api/session/history?limit=50`

List past completed sessions, newest first.

**Query parameters:**
- `limit` (int, optional): Max sessions to return. Default 50, max 500.
- `source` (string, optional): Filter by source — `"radiens"`, `"manual"`, or omit for all.

**Response 200:**
```json
{
  "count": 2,
  "total": 15,
  "sessions": [
    {
      "session_id": "a1b2c3d4-...",
      "start_time_utc": 1771567800.0,
      "end_time_utc": 1771575000.0,
      "start_time_local": "2026-02-20T14:30:00+09:00",
      "end_time_local": "2026-02-20T16:30:00+09:00",
      "duration_seconds": 7200.0,
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
    },
    {
      "session_id": "b2c3d4e5-...",
      "start_time_utc": 1771481400.0,
      "end_time_utc": 1771495800.0,
      "start_time_local": "2026-02-19T14:30:00+09:00",
      "end_time_local": "2026-02-19T18:30:00+09:00",
      "duration_seconds": 14400.0,
      "mouse_id": "HETCF3R1",
      "recording_type": "sd",
      "user_name": "andrea",
      "chamber": 1,
      "camera": "pi_cam_1",
      "radiens_xdat_filename": "HETCF3R1_sd_2026-02-19",
      "radiens_xdat_path": "/data/radiens/HETCF3R1_sd_2026-02-19.xdat",
      "video_filename": "2602191430_HETCF3R1_sd.mp4",
      "export_status": "completed",
      "nas_transfer_status": "skipped"
    }
  ]
}
```

### `GET /api/session/manual`

List currently active manual recordings (started via Frigate UI Record button).

**Response 200:**
```json
{
  "active": {
    "pi_cam_0": {
      "session_id": "m1n2o3p4-...",
      "camera": "pi_cam_0",
      "start_time_utc": 1771567800.0,
      "start_time_local": "2026-02-20T14:30:00+09:00"
    }
  },
  "count": 1
}
```

Returns `{"active": {}, "count": 0}` when no manual recordings are active.

### `GET /api/health`

Health check. Returns 200 if both Radiens and MQTT are connected, 503 otherwise.

**Response 200:**
```json
{
  "healthy": true,
  "radiens_connected": true,
  "mqtt_connected": true
}
```

**Response 503:**
```json
{
  "healthy": false,
  "radiens_connected": false,
  "mqtt_connected": true
}
```

---

## Polling Strategy

The UI uses HTTP polling (no WebSocket). Implement with `useEffect` + `setInterval`:

| Endpoint | Poll interval | Purpose |
|----------|--------------|---------|
| `GET /api/status` | 1500ms | Main status (recording state, connections, active session) |
| `GET /api/health` | 5000ms | System health badges |
| `GET /api/session/history` | On load + after each session ends (detect via status poll when `session` goes from non-null to null) | History table |
| Camera snapshots | 1000ms (if using snapshot mode) | Camera preview images |

**Error handling for polling:**
- If `fetch` fails (daemon is down), show "Daemon Offline" state across all panels
- Don't spam console with errors — log once, then suppress until reconnected
- When daemon reconnects (fetch succeeds after failure), show a "Reconnected" toast

---

## Theming and Visual Design

**Color scheme:** Dark theme (DaisyUI `dark` or `night` theme). This app runs in a dimly-lit experiment room.

**Key visual states:**

| State | Visual treatment |
|-------|-----------------|
| Idle (not recording) | Calm, neutral colors. Gray recording indicator. |
| Recording active | Red pulsing recording dot. Active session card with green left border. Session form locked. |
| Connection lost | Yellow/orange warning badges. "Reconnecting..." text. |
| Daemon offline | Red banner across top: "Daemon offline — check systemd service". All panels grayed out. |
| Metadata not set | Subtle yellow warning under the form: "No metadata set — files will use 'unknown' names" |

**Typography:** Use system fonts for performance. Monospace for session IDs, filenames, and timestamps.

**Window:**
- Title: "NeuroSurveillance Session Controller"
- Minimum size: 1024x700
- Default size: 1400x900

---

## Error Handling

| Scenario | UI behavior |
|----------|-------------|
| Daemon API unreachable | Show full-screen overlay: "Session daemon is not running. Start it with: `sudo systemctl start neurosurveillance-session`" |
| Metadata POST fails (400) | Show error message from response body in a toast |
| Metadata POST fails (503) | Show toast: "Session manager not ready" |
| Camera image fails to load | Show placeholder: gray box with "Camera offline" text. Don't break the layout. |
| Session history empty | Show "No sessions recorded yet" placeholder in the table |
| Health check returns 503 | Show degraded badges but don't block the UI |

---

## Data Constants (Hardcoded in App)

```typescript
// API base URL (daemon runs on same machine)
const API_BASE = "http://127.0.0.1:8585";

// Frigate camera URLs (for preview images)
const FRIGATE_BASE = "http://192.168.0.50:5000";
const CAMERAS = {
  0: { id: "pi_cam_0", label: "Chamber 0", snapshotUrl: `${FRIGATE_BASE}/api/pi_cam_0/latest.jpg` },
  1: { id: "pi_cam_1", label: "Chamber 1", snapshotUrl: `${FRIGATE_BASE}/api/pi_cam_1/latest.jpg` },
} as const;

// Recording types available
const RECORDING_TYPES = ["basal", "recovery", "sd"] as const;

// Lab members (will grow over time)
const LAB_MEMBERS = ["andrea"] as const;

// Polling intervals (milliseconds)
const STATUS_POLL_INTERVAL = 1500;
const HEALTH_POLL_INTERVAL = 5000;
const CAMERA_REFRESH_INTERVAL = 1000;
```

---

## File Structure (Suggested)

```
src/
├── App.tsx                 # Main layout grid
├── main.tsx                # Entry point
├── index.css               # Tailwind imports + custom styles
├── api/
│   └── client.ts           # API fetch functions (getStatus, setMetadata, etc.)
├── hooks/
│   ├── useStatusPoll.ts    # Polls /api/status at interval
│   ├── useHealthPoll.ts    # Polls /api/health at interval
│   └── useSessionTimer.ts  # Computes running session duration
├── components/
│   ├── SessionSetup.tsx    # Metadata form
│   ├── CameraPreview.tsx   # Dual camera feed
│   ├── LiveStatus.tsx      # Recording state + connection indicators
│   ├── SystemHealth.tsx    # Health badges
│   ├── SessionHistory.tsx  # History table with expandable rows
│   └── StatusBadge.tsx     # Reusable green/red/yellow badge
├── types/
│   └── api.ts              # TypeScript interfaces matching API responses
└── utils/
    └── format.ts           # Duration formatting, date formatting
```

---

## TypeScript Interfaces

```typescript
// GET /api/status response
interface DaemonStatus {
  daemon: string;
  radiens: {
    connected: boolean;
    recording_state: "R_ON" | "R_OFF" | "UNKNOWN";
  };
  mqtt: {
    connected: boolean;
  };
  session: ActiveSession | null;
  pending_metadata: PendingMetadata;
  manual_recordings: Record<string, {
    session_id: string;
    camera: string;
    start_time_local: string;
  }>;
}

interface ActiveSession {
  session_id: string;
  mouse_id: string;
  recording_type: string;
  chamber: number;
  camera: string;
  start_time_local: string; // ISO 8601
}

interface PendingMetadata {
  mouse_id: string;
  recording_type: string;
  user_name: string;
  chamber: number;
  is_default: boolean;
}

// POST /api/session/metadata request
interface SetMetadataRequest {
  mouse_id?: string;
  recording_type?: string;
  user_name?: string;
  chamber?: number;
}

// POST /api/session/metadata response
interface SetMetadataResponse {
  status: string;
  metadata: PendingMetadata;
}

// GET /api/session/history response
interface SessionHistoryResponse {
  count: number;
  total: number;
  sessions: SessionRecord[];
}

interface SessionRecord {
  session_id: string;
  start_time_utc: number;
  end_time_utc: number;
  start_time_local: string;
  end_time_local: string;
  duration_seconds: number;
  mouse_id: string;
  recording_type: string;
  user_name: string;
  chamber: number;
  camera: string;
  radiens_xdat_filename: string;
  radiens_xdat_path: string;
  video_filename: string;
  export_status: string;
  nas_transfer_status: string;
}

// GET /api/health response
interface HealthResponse {
  healthy: boolean;
  radiens_connected: boolean;
  mqtt_connected: boolean;
}
```

---

## Important Constraints

1. **Localhost only.** The daemon API is on `127.0.0.1:8585`. The Frigate camera feed is on `192.168.0.50:5000` (same LAN). Both are HTTP, no TLS.

2. **No authentication.** The daemon has no auth. The Frigate instance has an admin password but the camera snapshot API endpoints do not require authentication on the local network.

3. **Read-only toward the experiment.** The UI never starts/stops EEG recording — that is done by the researcher in the Radiens GUI. The UI only sets metadata and monitors status. The "Set Metadata" button is the only write operation.

4. **Metadata auto-clears.** After each session ends, the daemon automatically clears pending metadata to defaults. The UI should reflect this by clearing the form when it detects a session has ended (status poll shows `session` went from non-null to null).

5. **One session at a time.** The daemon supports only one active session. The form sets metadata for the next (or current single) session.

6. **Timezone:** All local timestamps are in `Asia/Seoul` (UTC+9). The daemon returns ISO 8601 strings with timezone offset.

7. **The app runs on Ubuntu 24.04 LTS.** Tauri v2 has Linux support. Ensure the build targets Linux (deb package preferred for easy install).

8. **No internet access required.** This runs on an air-gapped lab network. Do not use CDN-hosted fonts, icons, or assets. Bundle everything.

---

## Testing Without the Daemon

For development, create a mock API server or use hardcoded responses. Here are realistic test scenarios:

**Scenario 1: Idle (no session, no metadata)**
- `GET /api/status` returns `session: null`, `pending_metadata.is_default: true`, `recording_state: "R_OFF"`

**Scenario 2: Metadata set, waiting for recording**
- `POST /api/session/metadata` with `{"mouse_id": "HETCF3R1", "recording_type": "basal", "chamber": 0, "user_name": "andrea"}`
- `GET /api/status` returns `session: null`, `pending_metadata.is_default: false`

**Scenario 3: Recording active**
- `GET /api/status` returns `session: {...}` with `recording_state: "R_ON"`

**Scenario 4: Radiens disconnected**
- `GET /api/status` returns `radiens.connected: false`, `recording_state: "UNKNOWN"`

**Scenario 5: Daemon offline**
- All `fetch` calls fail with `TypeError: Failed to fetch`

---

## Deliverables

1. A working Tauri v2 desktop app that builds on Linux (Ubuntu 24.04)
2. All 5 dashboard panels implemented as described above
3. Dark theme using DaisyUI
4. Polling-based real-time updates
5. Camera preview with snapshot refresh
6. Toast notifications for state changes and errors
7. A mock API mode for development/testing (optional but helpful)

---

*End of build prompt.*

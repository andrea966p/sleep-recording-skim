---
tags: [infrastructure, session-daemon, frontend, reference]
created: 2026-03-05
status: production
version: "2.0"
updated: 2026-04-02
---

# Frontend Reference

Operational reference for the **NeuroSurveillance Session Controller** desktop application. This is the primary interface researchers use to set session metadata and monitor recording status.

## Tech Stack

| Layer | Package | Version |
|-------|---------|---------|
| Desktop shell | `@tauri-apps/cli` | v2 |
| Frontend framework | `react` | 19.1.0 |
| Language | `typescript` | 5.8.3 |
| Build tool | `vite` | 7.0.4 |
| Styling | `tailwindcss` | 3.4.19 |
| Component library | `daisyui` | 5.5.19 |

**Source:** `{SESSION_DAEMON_REPO}/frontend/`

## Build and Dev Commands

```bash
cd /home/skimlab/Monitoring_project/neurosurveillance/frontend

# Development (hot-reload with Tauri window)
npm run tauri dev

# Production build (creates .deb package)
npm run tauri build

# Vite dev server only (no Tauri window, browser access)
npm run dev

# TypeScript compile check
npx tsc --noEmit
```

## Component Map

```
App.tsx
│
├── Header
│   ├── Title: "NeuroSurveillance Session Controller"
│   ├── LiveClock (real-time clock display)
│   ├── Theme toggle (dark/light, persisted to localStorage)
│   ├── SettingsModal (gear icon)
│   ├── Storage badge (progress bar + %, color-coded from /api/health)
│   ├── "Disk Critical — Recording Blocked" badge (when critical)
│   └── "Daemon Offline" badge (when daemon unreachable)
│
├── ChamberSilo (one per configured camera, self-start grid items)
│   ├── Header bar (always visible)
│   │   ├── Recording dot (pulsing red when active, gray idle)
│   │   ├── Chamber label
│   │   ├── Manual recording badge (yellow, when active)
│   │   ├── Camera offline badge (red, when Pi unreachable)
│   │   └── Mouse ID badge (shown when collapsed + online + no manual rec)
│   ├── SessionSetup (expanded only)
│   │   ├── Mouse ID text input
│   │   ├── Recording Type dropdown
│   │   ├── User Name dropdown
│   │   ├── "Set Metadata" button → POST /api/session/metadata?chamber_id=X
│   │   └── "Clear" button → DELETE /api/session/metadata?chamber_id=X
│   ├── LiveStatus (expanded only)
│   │   ├── Recording state indicator (pulsing red / gray)
│   │   ├── Session timer (HH:MM:SS, computed client-side)
│   │   └── Active session details (mouse_id, type, camera)
│   └── CameraPreview (expanded only)
│       ├── Frigate snapshot <img> (refreshed every 1s)
│       └── Reports online/offline via onStatusChange callback
│
├── SystemHealth (footer, column 1)
│   ├── Daemon status badge
│   ├── Radiens connection badge
│   ├── MQTT connection badge
│   └── Frigate reachability badge
│
├── StoragePanel (footer, column 2)
│   ├── Progress bar (green/yellow/red by threshold)
│   ├── Two-column summary: Used, Total, EEG Reserve, Free
│   ├── "Recording blocked" alert (when can_record=false)
│   ├── Calculator: cameras dropdown + hours input → estimated size + fits/won't fit
│   ├── Sync button: fetches actual bitrates from go2rtc on each Pi
│   └── Bitrate info (tiny line: synced vs default Mbps/cam)
│
└── SessionHistory (footer, columns 3-4)
    └── Scrollable table of past sessions (newest first)
        ├── Date, Mouse ID, Type, Chamber, Duration, Status
        └── Expandable row for full session details
```

## Key Hooks

### `useStatusPoll` (1.5s interval)

Polls `GET /api/status` and returns the full daemon state. This is the primary data source for all components.

**Returns:** `{ status, error, isOffline }`

- `status.sessions` -- per-chamber active session data
- `status.pending_metadata` -- per-chamber pending metadata
- `status.radiens.recording_states` -- per-chamber recording state
- `status.mqtt.connected` -- MQTT connection status
- `status.manual_recordings` -- active manual recordings

### `useHealthPoll` (5s interval)

Polls `GET /api/health` for system health badges and header storage indicator.

**Returns:** `{ health, error }`

- `health.healthy` -- overall health (true if radiens + mqtt connected)
- `health.radiens_connected` -- Radiens connection
- `health.mqtt_connected` -- MQTT connection
- `health.storage_level` -- `"ok"` / `"warn"` / `"critical"` (used for header badge color)
- `health.storage_used_percent` -- disk usage percentage (used for header progress bar)

### `useStoragePoll` (10s interval)

Polls `GET /api/storage` for the StoragePanel footer card. Storage changes slowly so 10s is sufficient.

**Returns:** `{ storage, error }`

- Full `StorageStatus` object with disk usage, categories, EEG reserve, effective available, can_record flag, camera bitrate

### `useSessionTimer`

Computes running session duration client-side from `session.start_time_local` (ISO 8601). Updates every second via `setInterval`. Does not poll the API.

**Returns:** formatted duration string (`HH:MM:SS`)

### `useSettings` (localStorage)

Manages user-configurable settings persisted to `localStorage`. No server round-trip.

**Manages:**

| Setting | Default | Description |
|---------|---------|-------------|
| Cameras | `[{id: "pi_cam_0", label: "Chamber 0"}, ..., {id: "pi_cam_3", label: "Chamber 3"}]` | Camera list with IDs and labels (4 cameras) |
| Recording types | `["basal", "recovery", "sd"]` | Dropdown options |
| Lab members | `["andrea"]` | User name dropdown options |
| Frigate URL | `http://192.168.0.50:5000` | Base URL for camera snapshots |

## API Client

**File:** `src/api/client.ts`
**Base URL:** `http://127.0.0.1:8585`

| Function | Method | Endpoint |
|----------|--------|----------|
| `getStatus()` | GET | `/api/status` |
| `setMetadata(chamberId, data)` | POST | `/api/session/metadata?chamber_id={id}` |
| `clearMetadata(chamberId)` | DELETE | `/api/session/metadata?chamber_id={id}` |
| `getCurrentSession()` | GET | `/api/session/current` |
| `getSessionHistory(limit?, source?)` | GET | `/api/session/history` |
| `getHealth()` | GET | `/api/health` |
| `getStorage()` | GET | `/api/storage` |
| `getCameraBitrates()` | GET | `/api/storage/camera-bitrates` |

All functions use the `fetch` API. Errors throw exceptions caught by calling components and displayed as toast notifications.

## Layout Behavior

| Camera count | Layout |
|-------------|--------|
| 0 | Alert: "Configure cameras in Settings" |
| 1-3 | Single column of ChamberSilo cards |
| 4+ | Two-column grid of ChamberSilo cards (`self-start` items for independent expansion) |

**Footer grid:** 4 columns — SystemHealth (1 col) + StoragePanel (1 col) + SessionHistory (2 cols)

**Theme:** Dark mode default (DaisyUI `dark` theme). Toggle persisted to `localStorage`.

**Window:**
- Title: "NeuroSurveillance Session Controller"
- Minimum size: 1024x700
- Default size: 1400x900

## Visual States

| State | Appearance |
|-------|------------|
| Idle (not recording) | Gray recording indicator, neutral colors |
| Recording active | Red pulsing dot, green session border, form locked |
| Connection lost | Yellow/orange warning badges |
| Daemon offline | Red "Offline" badge in header, panels show error state |
| Camera offline | Red "Camera Offline" badge on ChamberSilo header (visible when collapsed) |
| No metadata set | Subtle warning: "defaults will be used" |
| Storage OK (<75%) | Green progress bar in header + StoragePanel |
| Storage warn (75-90%) | Yellow progress bar, warning color on header badge |
| Storage critical (>90%) | Red progress bar, "Disk Critical — Recording Blocked" badge in header |
| Recording blocked | Red alert in StoragePanel: "Recording blocked — disk below EEG reserve" |

## File Structure

```
frontend/
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── src-tauri/                     # Tauri Rust backend config
│   ├── Cargo.toml
│   └── tauri.conf.json
└── src/
    ├── App.tsx                    # Root layout
    ├── main.tsx                   # Vite entry
    ├── index.css                  # Tailwind imports
    ├── api/
    │   └── client.ts              # HTTP API client
    ├── types/
    │   └── api.ts                 # TypeScript interfaces
    ├── hooks/
    │   ├── useStatusPoll.ts       # Status polling (1.5s)
    │   ├── useHealthPoll.ts       # Health polling (5s)
    │   ├── useStoragePoll.ts      # Storage polling (10s)
    │   ├── useSessionTimer.ts     # Client-side timer
    │   └── useSettings.ts         # localStorage settings
    ├── components/
    │   ├── ChamberSilo.tsx        # Per-chamber card (with camera offline detection)
    │   ├── SessionSetup.tsx       # Metadata form
    │   ├── LiveStatus.tsx         # Recording state display
    │   ├── CameraPreview.tsx      # Frigate snapshot + online/offline reporting
    │   ├── StoragePanel.tsx       # Disk usage + calculator + bitrate sync
    │   ├── SettingsModal.tsx      # Configuration modal
    │   ├── SystemHealth.tsx       # Connection badges
    │   ├── SessionHistory.tsx     # Session list table
    │   ├── StatusBadge.tsx        # Reusable badge
    │   └── LiveClock.tsx          # Real-time clock
    └── utils/
        └── format.ts              # Date/duration/byte formatting
```

## Related

- [[architecture|Session Daemon Architecture]] -- backend design and API details
- [[../../02-procedures/session-recording-workflow|Session Recording Workflow]] -- user-facing procedure
- [[../../00-config/production-values|Production Values]] -- all IPs, ports, paths

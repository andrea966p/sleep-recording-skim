---
tags: [infrastructure, session-daemon, frontend, reference]
created: 2026-03-05
status: production
version: "1.0"
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
│   └── SettingsModal (gear icon)
│
├── ChamberSilo (one per configured camera)
│   ├── SessionSetup
│   │   ├── Mouse ID text input
│   │   ├── Recording Type dropdown
│   │   ├── User Name dropdown
│   │   ├── "Set Metadata" button → POST /api/session/metadata?chamber_id=X
│   │   └── "Clear" button → DELETE /api/session/metadata?chamber_id=X
│   ├── LiveStatus
│   │   ├── Recording state indicator (pulsing red / gray)
│   │   ├── Session timer (HH:MM:SS, computed client-side)
│   │   └── Active session details (mouse_id, type, camera)
│   └── CameraPreview
│       └── Frigate snapshot <img> (refreshed every 1s)
│
├── SystemHealth (footer, left column)
│   ├── Daemon status badge
│   ├── Radiens connection badge
│   ├── MQTT connection badge
│   └── Frigate reachability badge
│
└── SessionHistory (footer, right columns)
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

Polls `GET /api/health` for system health badges.

**Returns:** `{ health, error }`

- `health.healthy` -- overall health (true if radiens + mqtt connected)
- `health.radiens_connected` -- Radiens connection
- `health.mqtt_connected` -- MQTT connection

### `useSessionTimer`

Computes running session duration client-side from `session.start_time_local` (ISO 8601). Updates every second via `setInterval`. Does not poll the API.

**Returns:** formatted duration string (`HH:MM:SS`)

### `useSettings` (localStorage)

Manages user-configurable settings persisted to `localStorage`. No server round-trip.

**Manages:**

| Setting | Default | Description |
|---------|---------|-------------|
| Cameras | `[{id: "pi_cam_0", label: "Chamber 0"}, ...]` | Camera list with IDs and labels |
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

All functions use the `fetch` API. Errors throw exceptions caught by calling components and displayed as toast notifications.

## Layout Behavior

| Camera count | Layout |
|-------------|--------|
| 0 | Alert: "Configure cameras in Settings" |
| 1-3 | Single column of ChamberSilo cards |
| 4+ | Two-column grid of ChamberSilo cards |

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
| No metadata set | Subtle warning: "defaults will be used" |

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
    │   ├── useSessionTimer.ts     # Client-side timer
    │   └── useSettings.ts         # localStorage settings
    ├── components/
    │   ├── ChamberSilo.tsx        # Per-chamber card
    │   ├── SessionSetup.tsx       # Metadata form
    │   ├── LiveStatus.tsx         # Recording state display
    │   ├── CameraPreview.tsx      # Frigate snapshot
    │   ├── SettingsModal.tsx      # Configuration modal
    │   ├── SystemHealth.tsx       # Connection badges
    │   ├── SessionHistory.tsx     # Session list table
    │   ├── StatusBadge.tsx        # Reusable badge
    │   └── LiveClock.tsx          # Real-time clock
    └── utils/
        └── format.ts              # Date/duration formatting
```

## Related

- [[architecture|Session Daemon Architecture]] -- backend design and API details
- [[../../02-procedures/session-recording-workflow|Session Recording Workflow]] -- user-facing procedure
- [[../../00-config/production-values|Production Values]] -- all IPs, ports, paths

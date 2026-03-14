# NeuroSurveillance: Frontend Architecture

This document provides a detailed overview of the frontend application architecture, UI components, and state management used in the NeuroSurveillance Session Controller.

## 1. Tech Stack Overview
- **Framework**: React 19 with TypeScript
- **Desktop Environment**: Tauri v2
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + DaisyUI components
- **State Management**: React Hooks (Custom hooks pulling from a central REST/MQTT backend)

## 2. Core Application Structure (`App.tsx`)
The application is designed to handle an arbitrary number of simultaneous, independent recording chambers. 

The main `App.tsx` layout is dynamically generated based on the `config.yaml` loaded via the backend daemon. It fetches the available cameras and renders a multi-column grid of `ChamberSilo` components.

### Global Header
- Displays the overall Daemon daemon connection status (Healthy/Offline).
- Contains a globally active **Theme Toggle** (Light/Dark mode) that persists user preference using Tailwind/DaisyUI data-themes.

## 3. The `ChamberSilo` Component Architecture
To support multiple chambers without cluttering the screen, the UI is modularized into `ChamberSilo` components. 

### Collapsible UI
Each `ChamberSilo` is wrapped in a smooth, CSS-animated DaisyUI `collapse` module.
- **Collapsed State**: Shows a condensed pill-badge with the Camera Name, Live Recording Indicator (pulsing red or gray), and the currently bound Mouse ID. If a manual recording is running, it prioritizes a high-visibility Manual Recording badge.
- **Expanded State**: Reveals the full three-panel control interface for that specific chamber.

### Within the Silo
When expanded, a Silo contains three primary sub-components:

#### A. `SessionSetup.tsx` (Metadata Injection)
- A form allowing researchers to input `User Name`, `Mouse ID`, and `Protocol/Type`.
- Sends data to the backend via `POST /api/session/metadata` to queue up the next session.
- Locks the form inputs when a session (Automated or Manual) is actively recording to prevent data collisions.

#### B. `LiveStatus.tsx` (Real-time Telemetry)
- Tracks the active session timer using a custom `useSessionTimer` hook.
- Intelligently checks the backend state to display either the automated **Radiens** tracking data or the **Frigate UI Manual** recording metadata.
- Prioritizes displaying active recordings over pending metadata warnings.

#### C. `CameraPreview.tsx` (Live Video Feed)
- Uses an asynchronous snapshot loop to securely pull low-latency JPEGs from the Frigate API.
- Replaces heavy RTSP video streaming with a lightweight polling mechanism to keep the React CPU overhead minimal, especially when running 4+ chambers simultaneously.

## 4. History and Filtering (`SessionHistory.tsx`)
A dedicated sliding panel at the bottom of the screen provides a persistent log of completed sessions.

- **Data Fetching**: Pulls the chronological list of JSON sidecars from the daemon's `/api/session/history` securely.
- **Flexbox Grid**: Replaced legacy HTML tables with a modern CSS Flexbox grid layout to cleanly support nested expandable rows (revealing the precise file paths, durations, and export statuses).
- **Source Filtering**: Implements a 3-way toggle switch (`All`, `Radiens`, `Manual`) mapping cleanly to the `source` string tracked within the backend JSONs.

## 5. API Client (`api/client.ts`)
The `api/client.ts` acts as the strongly-typed translation layer between the React UI and the Python daemon. It defines the exact Typescript interfaces (`DaemonStatus`, `SessionRecord`, `PendingMetadata`, `ManualRecording`) ensuring that the frontend instantly catches any missing fields or undefined variables during development.

# UI Fixes — Frontend Alignment with Backend API

**Date:** 2026-02-25
**For:** Google Antigravity / Project IDX (v1.18.4, VSCode OSS 1.107.0)
**Repo:** `github.com:andrea966p/neurosurveillance` (private)
**Frontend path:** `frontend/`

The Tauri+React UI was built from the handoff doc but has some mismatches with the actual backend daemon API. All fixes are in the frontend only — the backend is correct and running in production.

---

## Fix 1: Metadata Endpoint Path (double request on every save)

**File:** `frontend/src/api/client.ts`

**Problem:** `setMetadata()` and `clearMetadata()` try `POST /api/metadata` first, get a 404, then fall back to `POST /api/session/metadata`. This causes a wasted 404 on every metadata save.

**Fix:** Remove the `/api/metadata` attempt. The backend only has `/api/session/metadata`.

```typescript
// setMetadata — change to:
export async function setMetadata(chamberId: string, data: SetMetadataRequest): Promise<SetMetadataResponse> {
    const res = await fetch(`${API_BASE}/api/session/metadata?chamber_id=${encodeURIComponent(chamberId)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json().catch(() => ({ status: "ok" }));
}

// clearMetadata — change to:
export async function clearMetadata(chamberId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/api/session/metadata?chamber_id=${encodeURIComponent(chamberId)}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to clear metadata");
}
```

---

## Fix 2: Add `manual_recordings` to DaemonStatus type

**File:** `frontend/src/types/api.ts`

**Problem:** The backend `/api/status` returns a `manual_recordings` field (active manual recordings from Frigate UI). The TypeScript interface doesn't include it, so the UI silently ignores it.

**Fix:** Add the field to `DaemonStatus`:

```typescript
export interface DaemonStatus {
    daemon: string;
    radiens: {
        connected: boolean;
        recording_states: { [chamber: string]: "R_ON" | "R_OFF" | "UNKNOWN" | string };
    };
    mqtt: {
        connected: boolean;
    };
    sessions: { [chamber: string]: ActiveSession | null };
    pending_metadata: { [chamber: string]: PendingMetadata | null };
    manual_recordings: { [camera: string]: ManualRecording };  // <-- ADD
}

// ADD this new interface:
export interface ManualRecording {
    session_id: string;
    camera: string;
    start_time_local: string;
}
```

---

## Fix 3: Show manual recording indicator in the UI

**File:** `frontend/src/components/ChamberSilo.tsx` (or new component)

**Problem:** When a researcher clicks Record in Frigate's web UI, the daemon tracks it and exports the video automatically. But the desktop UI shows no indication that a manual recording is active. This is confusing — a chamber could be recording video without the UI reflecting it.

**Fix:** When `status.manual_recordings` contains an entry for a chamber's camera, show a visual indicator. Suggested approach:

- In `ChamberSilo`, check if the chamber's camera has an active manual recording:
  ```typescript
  const cameraId = cam.id; // e.g. "pi_cam_0"
  const manualRec = status?.manual_recordings?.[cameraId];
  ```
- If `manualRec` exists, show a badge/banner like:
  ```
  Manual Recording (Frigate UI) — started 14:30
  ```
- Use a distinct color (e.g. `badge-warning` / amber) to differentiate from Radiens sessions (which are `badge-error` / red).

---

## Fix 4: Add `source` column to session history

**File:** `frontend/src/components/SessionHistory.tsx`

**Problem:** The history table shows all sessions but doesn't indicate whether they came from Radiens (EEG-synced) or manual Frigate recording. Manual sessions have `mouse_id: "manual"` and no EEG data, which can be confusing in the table.

**Fix:** The backend includes a `source` field in session records (`"radiens"` or `"manual"`). Add it to the type and display:

1. In `frontend/src/types/api.ts`, add to `SessionRecord`:
   ```typescript
   source: "radiens" | "manual";
   ```

2. In the history table, add a small badge or icon in the row to indicate source:
   - Radiens sessions: small "EEG" badge or brain icon
   - Manual sessions: small "Manual" badge or camera icon

3. Optionally add a filter dropdown above the table: "All / Radiens / Manual" — the backend supports `?source=radiens` and `?source=manual` query params on `GET /api/session/history`.

---

## Fix 5: History filter by source (optional enhancement)

**File:** `frontend/src/api/client.ts` + `frontend/src/components/SessionHistory.tsx`

**Problem:** No way to filter session history by source in the UI.

**Fix:** Update `getSessionHistory` to accept an optional source filter:

```typescript
export async function getSessionHistory(limit = 50, source?: string): Promise<SessionHistoryResponse> {
    let url = `${API_BASE}/api/session/history?limit=${limit}`;
    if (source) url += `&source=${encodeURIComponent(source)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("History fetch failed");
    return res.json();
}
```

Add a simple filter row above the history table with three toggle buttons: All | Radiens | Manual.

---

## Priority Order

| # | Fix | Impact | Effort |
|---|-----|--------|--------|
| 1 | Metadata endpoint path | Removes 404 noise from every save | 2 min |
| 2 | `manual_recordings` type | Type safety, no runtime change | 2 min |
| 3 | Manual recording indicator | Researchers see when video is recording from Frigate UI | 15 min |
| 4 | Source column in history | Distinguish Radiens vs manual sessions at a glance | 10 min |
| 5 | History source filter | Nice-to-have, low priority | 10 min |

---

## Backend API Reference

Actual `/api/status` response shape for reference:

```json
{
    "daemon": "running",
    "radiens": {
        "connected": true,
        "recording_states": { "0": "R_OFF", "1": "R_OFF" }
    },
    "mqtt": { "connected": true },
    "sessions": {},
    "pending_metadata": {},
    "manual_recordings": {}
}
```

When a manual recording is active on pi_cam_0:
```json
{
    "manual_recordings": {
        "pi_cam_0": {
            "session_id": "abc123...",
            "camera": "pi_cam_0",
            "start_time_local": "2026-02-25T14:30:00+09:00"
        }
    }
}
```

Additional endpoints:
- `GET /api/session/manual` — active manual recordings (detailed)
- `GET /api/session/history?source=manual` — filter history by source
- `GET /api/session/history?source=radiens` — filter history by source

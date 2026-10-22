---
tags: [troubleshooting, incident, session-daemon, radiens, auth, cors]
date: 2026-02-23
severity: medium
status: resolved
affected: [session-daemon, radiens, ui]
---

## Summary
- **Date:** 2026-02-23
- **Issue:** Session daemon initially failed to connect to Radiens and UI fetches were blocked in webview/browser mode.
- **Impact:** Daemon stayed degraded (`radiens_connected: false`), session state remained `UNKNOWN`, UI health panel showed degraded.
- **Status:** Resolved.

## Symptoms
- `/api/status` showed `radiens.connected: false`.
- Daemon logs showed repeated gRPC errors:
  - `StatusCode.UNAVAILABLE` (before Allego was running)
  - `StatusCode.UNAUTHENTICATED` with `failed verification via offline deviceUUID`
- Tauri/webview/browser API calls required CORS support.

## Investigation

### Root causes
1. **Auth mode mismatch:**
   - `RADIENS_OFFLINE=1` was enabled in systemd.
   - This triggered offline `deviceUUID` verification.
   - Offline license path was not activated on this host, so auth failed (`UNAUTHENTICATED`).
2. **Service environment pathing:**
   - `radiens` needed access to `~/.config/radiens/session.json` for Cognito session auth.
   - Explicit `HOME=/home/skimlab` was required in the systemd unit.
3. **State parsing bug in poller:**
   - `get_status().recording` returned a `RecordingSpec` object.
   - Poller originally stringified the full object and missed transitions.
   - Correct field is `get_status().recording.mode` (`R_ON` / `R_OFF`).
4. **CORS gap for UI path:**
   - API needed CORS headers for Tauri webview/browser fetch compatibility.

## Resolution
- Removed `RADIENS_OFFLINE=1` from systemd service.
- Added `Environment=HOME=/home/skimlab` to systemd service.
- Kept `Environment=PYTHONUNBUFFERED=1` for live logs.
- Added CORS headers in `api.py`:
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type`
- Fixed poller parsing to use `status.recording.mode`.
- Restarted service and revalidated endpoints.

## Validation
- `GET /api/status`:
  - `daemon: running`
  - `mqtt.connected: true`
  - `radiens.connected: true`
  - `radiens.recording_state: R_OFF` (idle)
- `GET /api/health`:
  - `healthy: true`
- UI (`npm run tauri dev`) connected successfully with healthy status panel and live camera preview.

## Prevention
- Keep auth mode documented in infrastructure docs and journals.
- If offline auth is needed later, request/activate NeuroNexus offline licensing before enabling `RADIENS_OFFLINE=1`.
- Keep a quick smoke test after changes:
  - `curl http://127.0.0.1:8585/api/status`
  - `curl http://127.0.0.1:8585/api/health`
  - `sudo systemctl status neurosurveillance-session.service`

## Related
- [[architecture|Session Daemon Architecture]]
- [[session-recording-workflow|Session Recording Workflow]]
- [[2026-02-23|Journal: 2026-02-23]]

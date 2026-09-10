---
name: Settings sync gap
description: Frontend SettingsModal saves to localStorage only — lab members, cameras, recording types never sync back to backend config.yaml
type: project
---

Frontend settings (lab members, cameras, recording types) are stored in localStorage via `useSettings.ts`, not synced to `config.yaml`. Users added via the UI only persist in that browser instance.

**Why this matters:** If the app is opened on a different machine or localStorage is cleared, all UI-added settings are lost. Backend validation (`api.py:210`) reads from `config.yaml` which stays stale.

**How to apply:** After storage management is done, implement a `POST /api/settings` endpoint that writes changes back to `config.yaml`, or have the frontend load settings from the backend on startup. This is a separate task from storage management.

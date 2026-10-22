---
name: Settings sync gap
description: "Frontend settings (lab members, cameras, recording types) live in localStorage only and never sync to backend config.yaml; deferred. Detail in the vault"
type: project
---

Frontend settings are stored in localStorage via `useSettings.ts`, not synced to `config.yaml`; UI-added users persist only in that browser, and backend validation (`api.py:210`) reads the stale `config.yaml`. Deferred since the 2026-05-01 council. Fix options: a `POST /api/settings` that writes back to `config.yaml`, or load settings from the backend at startup.

Details: [[settings-sync-gap]] · [[2026-05-01-llm-council-review]]

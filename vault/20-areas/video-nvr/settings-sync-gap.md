---
type: reference
area: video-nvr
status: active
created: 2026-10-22
tags: [frontend, session-daemon, settings]
summary: "The frontend settings (lab members, cameras, recording types) live in browser localStorage and never reach config.yaml; deferred since the 2026-05-01 council."
---

# Settings sync gap (frontend localStorage vs config.yaml)

Promoted 2026-10-22 from a Claude memory file. Evidence: [[2026-05-01-llm-council-review]] (the "Settings split" finding and the decision to skip it) and [[frontend-reference]].

- The frontend settings (lab members, cameras, recording types) are stored in browser localStorage through `useSettings.ts`. They are not synced to `config.yaml`. A user added in the UI persists only in that browser instance.
- If the app is opened on another machine, or localStorage is cleared, every UI-added setting is lost.
- Backend validation (`api.py:210`) reads `config.yaml`, which stays stale.
- Possible fix, not started: a `POST /api/settings` endpoint that writes changes back to `config.yaml`, or have the frontend load settings from the backend at startup. It is a separate task from storage management ([[storage-management-implementation]]).
- Status: deferred. The council marked it "annoying, not dangerous" for a single user.

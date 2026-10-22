---
tags: [archive, 2026-05-rehaul]
archived: 2026-05-24
superseded-by: "[[frontend-reference]]"
reason: "Session WAL journal (2026-05-23) and nightly reconciler (2026-05-24) added /api/journal, /api/reconciler/last, /api/reconciler/run endpoints; pre-change API table is preserved here"
---

*Archived from `01-infrastructure/session-daemon/frontend-reference.md` on 2026-05-24. See `superseded-by` for the current version.*

This file captures the pre-2026-05-23 API client table from the frontend reference. The stabilization sprint added three new endpoints — `/api/journal` (read the WAL session journal), `/api/reconciler/last` (last reconciler run's findings), and `/api/reconciler/run` (trigger an ad-hoc reconciler pass). The live doc now includes plain-language explanations of each.

## API Client — pre-2026-05-23

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

The pre-sprint table had 8 endpoints. The post-sprint table has 11 (3 new). The new endpoints were back-end-only at the moment of shipping — the frontend client wrapper functions for them are documented in the live `frontend-reference.md` as candidates for the next frontend sprint, not deployed yet.

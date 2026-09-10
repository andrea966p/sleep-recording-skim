---
name: project-phase-3-complete
description: Stabilization sprint Phase 3 shipped 2026-05-24 — Frigate restart LWT grace + STATE_DEFER ordering fix + nightly WAL reconciler + MQTT publish.
metadata: 
  node_type: memory
  type: project
  originSessionId: 5cbc6d77-6b1d-49ac-9f41-42050a74c3fc
---

Phase 3 of the [[2026-05-20]] stabilization sprint is complete (commit `3830dba` on `andrea966p/neurosurveillance`). Three previously-open items closed:

- **Council Stage 2.2 — Nightly reconciler.** New `backend/reconciler.py` background thread runs at 00:01 KST, joins WAL `events` with Frigate's `recordings` SQLite (both read-only). Emits four findings (ORPHAN, PARTIAL, STUCK, DEGRADED) on a 24h window. MQTT publish to `neurosurveillance/reconciler/findings`. HTTP at `GET /api/reconciler/last` + `POST /api/reconciler/run`. CLI for ad-hoc dry runs.
- **Council Stage 2.3 — `_last_known_state` lock.** Added explicit `threading.Lock` so MQTT-thread reads/writes of that map can't race under flapping availability. Folded into 3.1 as planned.
- **2026-05-20 daemon startup-guard regression — Frigate restart case.** `FrigateController` subscribes to `frigate/available` LWT; daemon registers a callback that runs the same 10s grace as startup whenever a non-initial `online` arrives. **Closes both occurrences** captured in `[[project_daemon_startup_guard_regression]]`.

**Why:** Phase 2 (yesterday) gave us the WAL — the reconciler needed a ground-truth event store to join against. Today closes the data-integrity loop. Council Outsider critique on bus-factor is partially addressed; full coverage waits on Phase 4 + runbook polish.

**How to apply:** When asked about Frigate restart safety, the daemon now handles it autonomously; no Diane-side coordination needed for ad-hoc docker restart frigate cycles (3× validated zero phantoms). When asked about session-level QC, the reconciler is the canonical source — query `/api/reconciler/last` rather than digging through journalctl. When asked about discrepancies between exports on disk and session metadata, point at PARTIAL/STUCK/DEGRADED counts first.

## Surprise of the day — Phase 3.1b ordering fix

The initial LWT wiring still produced 4 phantom `ManualSession`s per restart. Root cause: Frigate republishes its retained `recordings/state=ON` topics **before** its retained `frigate/available=online` payload. Fix: defer every external-state callback by `STATE_DEFER_SECONDS = 1.5` via `threading.Timer`; the availability handler calls `cancel_pending_state_actions()` from the same paho MQTT loop thread before the timer can fire. Belt-and-suspenders cancel also lives in the daemon's restart-grace handler. See [[pattern_frigate_mqtt_message_ordering]] for the reusable shape.

## What's next (Monday 2026-05-25)

Phase 4 items from the sprint plan:

- 4.1 Watchdog → Slack (same Netdata MQTT collector path the reconciler will use)
- 4.2 ffprobe duration sanity check on every export
- 4.3 `requirements.txt` radiens comment update
- 4.4 Flesh out the three runbooks Phase 0.4 sketched
- 4.5 Final commit + push + tag `stabilization-week-1`
- 4.6 NEW — wire Netdata MQTT collector to `neurosurveillance/reconciler/findings` for Slack alerts on `partial_count + stuck_count + degraded_count > 0`. ORPHAN suppressed (see [[pattern_frigate_record_enabled_orphan_noise]]).

Sprint plan status table lives at [[2026-05-20#Status snapshot]]; today's full journal entry is [[2026-05-24]]; reconciler golden-config reference is [[reconciler]] in the vault.

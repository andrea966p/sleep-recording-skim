---
tags: [infrastructure, session-daemon, session-journal, golden-config, wal]
created: 2026-05-23
updated: 2026-05-23
status: production
version: 1.0
related-sprint-phase: phase-2
related-plan: 2026-05-20
---

# Session Journal — Append-Only WAL

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A small SQLite database (`/opt/neurosurveillance/session_wal.db`) where the daemon records every step of every recording — when it started, when the video export began, when it finished, if it was aborted, if it stalled.
>
> **Why it exists.** Before 2026-05-23, all of that lived only in the daemon's RAM. A daemon crash or power loss would lose the session's metadata even though Frigate had already written the video segments to disk. Now the journal is the durable record; the daemon's RAM is just a cache.
>
> **How to read this page.** Skim the Schema and Event types tables to know what a row looks like. Read "Failure semantics" if you're debugging. Read [[reconciler]] to see what consumes the journal nightly.

> [!quote] Paper-ready
> Every session state transition (START, EXPORT_BEGIN, EXPORT_COMPLETE, ABORT, STALL) is appended to a SQLite write-ahead-log database with `synchronous=FULL`, fsyncing each event before the recording path proceeds; the manual-recording path is fail-closed, refusing the recording if the journal write fails.

The **session journal** is the daemon's crash-safe record of session lifecycle events. Every session state transition is appended to a SQLite WAL-mode database; the in-memory session managers are still the runtime truth, but the journal is the durable truth.

Shipped 2026-05-23 as council Stage 2.1 (see [[2026-05-23|2026-05-23 journal]]).

> [!info] Why it exists
> Before today, every session state transition existed in memory only. A daemon crash mid-session lost the metadata; MP4 chunks on disk became orphans with no record of which `mouse_id` they belonged to. Already seen on [[2026-05-18|2026-05-18 pi_cam_2]]. The journal closes that gap by writing each transition with `synchronous=FULL` before the recording path can proceed.

## File location

| Path | Owner | Notes |
|---|---|---|
| `/opt/neurosurveillance/session_wal.db` | `skimlab:skimlab` | Main DB file |
| `/opt/neurosurveillance/session_wal.db-wal` | `skimlab:skimlab` | Write-ahead log; checkpointed automatically |
| `/opt/neurosurveillance/session_wal.db-shm` | `skimlab:skimlab` | Shared-memory file used by WAL coordination |

All three files must be present and writable for the daemon to start. The daemon creates them on first boot via `SessionJournal._open()`.

## Schema

```sql
CREATE TABLE events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           REAL    NOT NULL,   -- Unix epoch seconds (float)
    event_type   TEXT    NOT NULL,   -- one of VALID_EVENT_TYPES
    session_id   TEXT,               -- UUID; same as ManualSessionRecord.session_id / SessionRecord.session_id
    camera       TEXT,               -- pi_cam_0 / pi_cam_1 / pi_cam_2 / pi_cam_3
    mouse_id     TEXT,               -- denormalized for fast filtering
    payload_json TEXT                -- JSON blob, schema varies per event_type (see below)
);

CREATE INDEX idx_events_ts        ON events(ts);
CREATE INDEX idx_events_session   ON events(session_id);
CREATE INDEX idx_events_type_ts   ON events(event_type, ts);
```

## SQLite PRAGMAs

Applied at open by `SessionJournal._open()`:

| PRAGMA | Value | Why |
|---|---|---|
| `journal_mode` | `WAL` | Multiple readers + one writer; survives crashes; better concurrency than rollback journal |
| `synchronous` | `FULL` | `fsync` the WAL on every commit. Council 2.1 explicitly required this — recording-integrity events must not vanish on power loss |
| `temp_store` | `MEMORY` | Avoids creating temp files for ORDER BY / aggregate sorting |

`isolation_level=None` is set on the Python `sqlite3.Connection`, so every `execute("INSERT …")` autocommits — one event per fsync. No batched commits.

## Event types

Defined in `backend/session_journal.py` as module-level constants. Treat any string outside this set as a bug; `log_event()` rejects unknown types.

| Constant | String | Emitted by | Payload fields |
|---|---|---|---|
| `EVENT_START` | `"START"` | `manual_session_manager.start_recording()` (manual), `session_manager.start_session()` (Radiens) | `source: "manual"\|"radiens"`, `recording_type`, `user_name`, `chamber?`, `radiens_xdat_filename?`, optionally `backfilled: true` |
| `EVENT_EXPORT_BEGIN` | `"EXPORT_BEGIN"` | `daemon._execute_export()`, immediately before `frigate.export_recording()` | `label`, `export_name`, `start_time_utc`, `end_time_utc`, `duration_seconds` |
| `EVENT_EXPORT_COMPLETE` | `"EXPORT_COMPLETE"` | `daemon._execute_export()`, after `_move_export_file()` returns | `label`, `export_id`, `video_filename`, `moved_to` (final disk path or null), `duration_seconds` |
| `EVENT_ABORT` | `"ABORT"` | `session_manager.abort_session()` (live); also backfill for sessions with `export_status` ≠ `"completed"` | `reason`, `duration_seconds` |
| `EVENT_STALL` | `"STALL"` | `recording_watchdog._emit_alert()` when lag > `STALL_THRESHOLD` (60 s) | `lag_seconds`, `last_segment_ts` (nullable) |

## Failure semantics

`log_event()` **never raises**. It returns `bool`:

- `True` — row committed and fsynced.
- `False` — invalid `event_type`, SQLite error, or connection closed. Logged at ERROR level.

This lets callers choose their own policy:

| Call site | Policy | Reason |
|---|---|---|
| `manual_session_manager.start_recording()` | **Fail-closed** — if `False`, return `None`; daemon publishes `OFF` to Frigate to undo the recording | We can refuse a manual recording; the journal-truth requirement outranks Frigate state |
| `session_manager.start_session()` | **Fail-open** — log the error and continue | Radiens already started; we cannot refuse a recording the EEG side has committed to |
| `session_manager.abort_session()` | **Fail-open** | Session already aborted; nothing to undo |
| `daemon._execute_export()` (`EXPORT_BEGIN` / `EXPORT_COMPLETE`) | **Fail-open** | Export has already happened or is happening; missing a journal row doesn't change the file on disk |
| `recording_watchdog._emit_alert()` | **Fail-open** | STALL is an observation, not a decision |

The fail-closed path on `START` is the one place the journal can refuse the recording. Everywhere else, the journal is an observer.

## Concurrency

- One `sqlite3.Connection` shared across threads, guarded by `threading.Lock`.
- `check_same_thread=False` lets the same connection serve the API thread, export threads, watchdog thread, and main loop.
- The lock is held only for the duration of one `INSERT` or one `SELECT` — measured in microseconds.
- SQLite WAL mode permits multiple readers (separate connections) while a writer holds its own lock; the reconciler (Phase 3.3) is expected to open its own short-lived `sqlite3.Connection` rather than borrowing the daemon's.

## API surface

### Python (`SessionJournal`)

```python
from session_journal import (
    SessionJournal,
    EVENT_START, EVENT_EXPORT_BEGIN, EVENT_EXPORT_COMPLETE,
    EVENT_ABORT, EVENT_STALL,
)

journal = SessionJournal(db_path="/opt/neurosurveillance/session_wal.db")

journal.log_event(
    EVENT_START,
    session_id="…",
    camera="pi_cam_3",
    mouse_id="HETCF3R1",
    payload={"source": "manual", "recording_type": "basal", "user_name": "andrea"},
)

events = journal.query(since=time.time() - 3600, event_type=EVENT_START, limit=100)
counts = journal.count_by_type(since=time.time() - 86400)

journal.close()
```

### HTTP (`GET /api/journal`)

| Param | Type | Default | Notes |
|---|---|---|---|
| `since` | float (epoch seconds) | — | inclusive lower bound on `ts` |
| `until` | float (epoch seconds) | — | inclusive upper bound on `ts` |
| `event_type` | string | — | one of the five constants |
| `session_id` | string | — | UUID |
| `limit` | int | 500 | capped at 5000 |

Response:

```json
{
  "count": 3,
  "counts_by_type": {"START": 1, "EXPORT_BEGIN": 1, "EXPORT_COMPLETE": 1},
  "events": [ /* newest first */ ]
}
```

`counts_by_type` honours `since` (but not the other filters) — gives "events in the last N hours grouped by type" with one call.

## Backfill

`backend/scripts/backfill_journal.py` replays historical `_session.json` sidecars into the WAL. Idempotent — skips any `session_id` already present.

```bash
# Dry-run on a throwaway DB
python3 scripts/backfill_journal.py --dry-run --db /tmp/scratch.db --days 90

# Real run against production WAL
cd /home/skimlab/Monitoring_project/neurosurveillance/backend
python3 scripts/backfill_journal.py --days 30
```

Behavior:

- Reads all `*_session.json` from `--sessions-dir` (default `/opt/neurosurveillance/sessions`).
- Filters by `start_time_utc >= now - days * 86400`.
- For each: emits synthetic `START` at `start_time_utc`, plus a closing event at `end_time_utc`:
  - `export_status == "completed"` → `EXPORT_COMPLETE`
  - anything else (`failed: …`, `aborted: …`) → `ABORT` with `reason = export_status`
- All backfilled rows carry `payload.backfilled: true`. The reconciler is expected to special-case these (no `EXPORT_BEGIN` exists for backfilled rows).

> [!warning] Backfill does not produce STALL events
> Historical sessions predate the watchdog. The reconciler should not infer historical stalls from backfilled data.

## Operational notes

### Inspecting the journal directly

```bash
# Last 20 events
sqlite3 /opt/neurosurveillance/session_wal.db \
  "SELECT datetime(ts,'unixepoch','localtime') AS local, event_type, substr(session_id,1,8) AS sid, camera, mouse_id FROM events ORDER BY ts DESC LIMIT 20"

# Per-day event counts
sqlite3 /opt/neurosurveillance/session_wal.db \
  "SELECT date(ts,'unixepoch','localtime') AS day, event_type, COUNT(*) FROM events GROUP BY day, event_type ORDER BY day DESC"

# Sessions that have START but no EXPORT_COMPLETE in the last 7 days
sqlite3 /opt/neurosurveillance/session_wal.db <<'SQL'
SELECT s.session_id, s.camera, datetime(s.ts,'unixepoch','localtime')
FROM events s
WHERE s.event_type='START'
  AND s.ts > strftime('%s','now') - 86400 * 7
  AND NOT EXISTS (
    SELECT 1 FROM events c
    WHERE c.session_id = s.session_id
      AND c.event_type IN ('EXPORT_COMPLETE','ABORT')
  );
SQL
```

### Manual reads must not block the daemon

When reading the WAL from a shell, use a **read-only** connection if you can — `sqlite3 'file:/opt/neurosurveillance/session_wal.db?mode=ro' …` — so the daemon's writer is never delayed by a forgotten `BEGIN` in another process.

### Backup

Use `sqlite3 .backup` rather than `cp`: the live `.db` plus `.db-wal` are not safe to copy with `cp` while the daemon is writing.

```bash
sqlite3 /opt/neurosurveillance/session_wal.db ".backup /path/to/backup/session_wal_$(date +%Y%m%d).db"
```

Currently un-automated. Off-machine durability (Syncthing-replicated WAL, NAS-side `sqlite3 .backup`) is a [[2026-05-23#Future considerations & optimizations|sprint follow-up]].

### Truncation / retention

The WAL is currently retention-unbounded. With ~5 events per session and present cadence this grows by a few hundred KB per month — harmless for years. No rotation is configured.

If rotation becomes necessary, prefer **truncation by date** (delete `WHERE ts < cutoff`) over `VACUUM` of the whole file — the reconciler's "ORPHAN" detection needs at least the retention window of Frigate's `recordings` table to be useful.

## Wiring summary

The following modules are journal-aware (touched 2026-05-23):

| Module | What it does with the journal |
|---|---|
| `backend/session_journal.py` | The module itself (new) |
| `backend/manual_session_manager.py` | Accepts `journal=…`; logs `START` fail-closed in `start_recording()` |
| `backend/session_manager.py` | Accepts `journal=…`; logs `START` in `start_session()`, `ABORT` in `abort_session()` (both fail-open) |
| `backend/recording_watchdog.py` | Accepts `journal=…` + `active_sessions_provider=…`; logs `STALL` with session-id annotation |
| `backend/daemon.py` | Owns the `SessionJournal` instance; passes it to all components; wires `EXPORT_BEGIN` / `EXPORT_COMPLETE` around `_execute_export()`; closes the journal in `stop()` |
| `backend/api.py` | Exposes `GET /api/journal` |
| `backend/scripts/backfill_journal.py` | Replays historical session JSONs |

## Failure scenarios

| Scenario | Behaviour |
|---|---|
| `START` write fails (DB full, fsync error) on a **manual** recording | `start_recording()` returns `None`, daemon publishes `OFF` to Frigate. ~1 Frigate segment may have already been written; the reconciler flags it as `ORPHAN`. Acceptable. |
| `START` write fails on a **Radiens** recording | Logged at ERROR; recording continues. Reconciler sees the MP4 with no `START` row → `ORPHAN`. Acceptable; Radiens is uncontrollable. |
| `EXPORT_BEGIN` succeeds but `EXPORT_COMPLETE` fails | Reconciler (24 h grace) flags as `STUCK`. The file may or may not exist; reconciler inspects disk to disambiguate. |
| Daemon crashes between `EXPORT_BEGIN` and `EXPORT_COMPLETE` | On restart, daemon does NOT re-attempt the export (no re-entry logic today). Reconciler picks it up at next nightly run. Phase 3.3 must implement the re-attempt or escalate. |
| Disk full | Both the journal and any new MP4 fail. Storage monitor already blocks new recordings below the 200 GB EEG reserve, so this is a degenerate case we don't expect during normal operation. |
| Journal file deleted manually | Daemon re-creates it on next start with an empty schema. All in-flight sessions become un-journaled (their `START` is gone); the reconciler treats their MP4s as `ORPHAN`. |

## See also

- [[architecture|Session Daemon Architecture]] — overall component map
- [[2026-05-23|2026-05-23 daily journal]] — Phase 2 implementation log
- [[2026-05-stabilization-sprint-week-1-plan|stabilization sprint plan]] — council Stage 2.1 spec (sprint execution)
- [[2026-05-01-llm-council-review|2026-05-01 LLM council review]] — original WAL recommendation
- [[2026-05-22|2026-05-22 journal]] — the regression that motivated the urgency
- Repo: `backend/session_journal.py`, `backend/scripts/backfill_journal.py` on `andrea966p/neurosurveillance` `main` after `7db66d2`

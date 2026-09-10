"""
Session Journal - Append-only durable log of session lifecycle events.

Provides a crash-safe SQLite WAL-mode database that records every session
state transition (START, EXPORT_BEGIN, EXPORT_COMPLETE, ABORT, STALL) so
that the in-memory session managers can be reconstructed or audited after
a daemon crash, container restart, or unexpected reboot.

Council Stage 2.1 (sprint 2026-05-23). The reconciler (Phase 3.3) joins
this journal against Frigate's recordings DB to surface ORPHAN / PARTIAL /
STUCK conditions.

Design:
- One table `events(ts, event_type, session_id, camera, mouse_id, payload_json)`.
- WAL mode + synchronous=FULL — every commit hits the WAL with fsync, so a
  power loss between log_event() and the next write cannot lose committed
  rows.
- A single Connection guarded by an internal lock. SQLite's serialized
  threading mode plus our own lock makes it safe to call log_event() from
  the API thread, watchdog thread, export thread, and main loop concurrently.
- Failures inside log_event() are logged but never raised. Council guidance:
  the journal must never take the daemon down.
"""

import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Event type constants — referenced from other modules to avoid string typos.
EVENT_START = "START"
EVENT_EXPORT_BEGIN = "EXPORT_BEGIN"
EVENT_EXPORT_COMPLETE = "EXPORT_COMPLETE"
EVENT_ABORT = "ABORT"
EVENT_STALL = "STALL"

VALID_EVENT_TYPES = frozenset({
    EVENT_START,
    EVENT_EXPORT_BEGIN,
    EVENT_EXPORT_COMPLETE,
    EVENT_ABORT,
    EVENT_STALL,
})

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    event_type TEXT NOT NULL,
    session_id TEXT,
    camera TEXT,
    mouse_id TEXT,
    payload_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(event_type, ts);
"""


class SessionJournal:
    """Append-only SQLite WAL journal for session lifecycle events."""

    def __init__(self, db_path: str = "/opt/neurosurveillance/session_wal.db"):
        self.db_path = Path(db_path)
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._open()

    def _open(self) -> None:
        """Open the SQLite connection and apply PRAGMAs / schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        # check_same_thread=False because we serialize writes ourselves with _lock.
        self._conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            isolation_level=None,  # autocommit; we issue BEGIN/COMMIT manually if needed
            timeout=5.0,
        )
        # WAL mode survives crashes; FULL syncs every commit (council 2.1 requirement).
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=FULL;")
        self._conn.execute("PRAGMA temp_store=MEMORY;")
        self._conn.executescript(_SCHEMA)
        logger.info("Session journal opened at %s (WAL, synchronous=FULL)", self.db_path)

    def log_event(
        self,
        event_type: str,
        session_id: Optional[str] = None,
        camera: Optional[str] = None,
        mouse_id: Optional[str] = None,
        payload: Optional[dict[str, Any]] = None,
        ts: Optional[float] = None,
    ) -> bool:
        """Append a single event row. Returns True on success, False on failure.

        Never raises — journal failures must not propagate up into the
        recording/export paths. Callers that need to fail-closed (Phase 2.2:
        START fail must abort session creation) should check the return value.
        """
        if event_type not in VALID_EVENT_TYPES:
            logger.error("Invalid journal event_type: %r (skipped)", event_type)
            return False

        ts = time.time() if ts is None else ts
        payload_str = json.dumps(payload, separators=(",", ":")) if payload else None

        with self._lock:
            if self._conn is None:
                logger.error("Journal connection is closed; cannot log %s", event_type)
                return False
            try:
                self._conn.execute(
                    "INSERT INTO events "
                    "(ts, event_type, session_id, camera, mouse_id, payload_json) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (ts, event_type, session_id, camera, mouse_id, payload_str),
                )
                return True
            except sqlite3.Error as e:
                logger.error(
                    "Journal write failed (event=%s session=%s): %s",
                    event_type, (session_id or "")[:8], e,
                )
                return False

    def query(
        self,
        since: Optional[float] = None,
        until: Optional[float] = None,
        event_type: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """Read events. Newest first. Bounded by `limit` (default 500, max 5000)."""
        limit = max(1, min(int(limit), 5000))
        clauses: list[str] = []
        params: list[Any] = []

        if since is not None:
            clauses.append("ts >= ?")
            params.append(float(since))
        if until is not None:
            clauses.append("ts <= ?")
            params.append(float(until))
        if event_type is not None:
            clauses.append("event_type = ?")
            params.append(event_type)
        if session_id is not None:
            clauses.append("session_id = ?")
            params.append(session_id)

        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = (
            "SELECT id, ts, event_type, session_id, camera, mouse_id, payload_json "
            f"FROM events{where} ORDER BY ts DESC LIMIT ?"
        )
        params.append(limit)

        with self._lock:
            if self._conn is None:
                return []
            try:
                rows = self._conn.execute(sql, params).fetchall()
            except sqlite3.Error as e:
                logger.error("Journal query failed: %s", e)
                return []

        out: list[dict[str, Any]] = []
        for row in rows:
            payload_json = row[6]
            try:
                payload = json.loads(payload_json) if payload_json else None
            except json.JSONDecodeError:
                payload = None
            out.append({
                "id": row[0],
                "ts": row[1],
                "event_type": row[2],
                "session_id": row[3],
                "camera": row[4],
                "mouse_id": row[5],
                "payload": payload,
            })
        return out

    def count_by_type(self, since: Optional[float] = None) -> dict[str, int]:
        """Return {event_type: count} aggregated over events since `since`."""
        clauses: list[str] = []
        params: list[Any] = []
        if since is not None:
            clauses.append("ts >= ?")
            params.append(float(since))
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT event_type, COUNT(*) FROM events{where} GROUP BY event_type"

        with self._lock:
            if self._conn is None:
                return {}
            try:
                rows = self._conn.execute(sql, params).fetchall()
            except sqlite3.Error as e:
                logger.error("Journal count_by_type failed: %s", e)
                return {}
        return {row[0]: row[1] for row in rows}

    def close(self) -> None:
        """Close the connection. Safe to call multiple times."""
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except sqlite3.Error as e:
                    logger.warning("Error closing journal: %s", e)
                finally:
                    self._conn = None
                    logger.info("Session journal closed")

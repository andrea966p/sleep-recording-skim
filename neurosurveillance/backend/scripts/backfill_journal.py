#!/usr/bin/env python3
"""
backfill_journal.py - Replay historical session JSONs into the session WAL.

Walks the sessions directory, reads each `*_session.json`, and emits a
synthetic START + EXPORT_COMPLETE/ABORT pair into the journal with each
event's original timestamp preserved (ts=start_time_utc / end_time_utc).

Idempotent: if any event already exists in the WAL for a given session_id,
that session is skipped.

Usage:
    python3 scripts/backfill_journal.py \\
        [--sessions-dir /opt/neurosurveillance/sessions] \\
        [--db /opt/neurosurveillance/session_wal.db] \\
        [--days 30] \\
        [--dry-run]
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Allow running from anywhere — add backend dir to path.
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from session_journal import (  # noqa: E402
    EVENT_ABORT,
    EVENT_EXPORT_COMPLETE,
    EVENT_START,
    SessionJournal,
)

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s",
)
logger = logging.getLogger("backfill_journal")


def classify_end(export_status: str) -> str:
    """Map a session's export_status string to a journal closing event type."""
    s = (export_status or "").strip().lower()
    if s == "completed":
        return EVENT_EXPORT_COMPLETE
    return EVENT_ABORT


def session_already_in_wal(journal: SessionJournal, session_id: str) -> bool:
    """True if the WAL already has any event for this session_id."""
    rows = journal.query(session_id=session_id, limit=1)
    return len(rows) > 0


def backfill_one(
    journal: SessionJournal, data: dict, dry_run: bool
) -> tuple[bool, str]:
    """Emit START + closing event for one session JSON.

    Returns (wrote_anything, reason_if_skipped).
    """
    session_id = data.get("session_id")
    if not session_id:
        return False, "no session_id"

    start_ts = data.get("start_time_utc")
    if not start_ts:
        return False, "no start_time_utc"

    if session_already_in_wal(journal, session_id):
        return False, "already in WAL"

    end_ts = data.get("end_time_utc") or start_ts
    export_status = data.get("export_status", "")
    close_event = classify_end(export_status)

    common = {
        "session_id": session_id,
        "camera": data.get("camera"),
        "mouse_id": data.get("mouse_id"),
    }

    if dry_run:
        return True, f"would write START+{close_event}"

    start_payload = {
        "source": data.get("source", "unknown"),
        "recording_type": data.get("recording_type"),
        "user_name": data.get("user_name"),
        "chamber": data.get("chamber"),
        "radiens_xdat_filename": data.get("radiens_xdat_filename"),
        "backfilled": True,
    }
    if not journal.log_event(EVENT_START, ts=start_ts, payload=start_payload, **common):
        return False, "journal write START failed"

    close_payload = {
        "video_filename": data.get("video_filename"),
        "duration_seconds": data.get("duration_seconds"),
        "export_status": export_status,
        "backfilled": True,
    }
    if close_event == EVENT_ABORT:
        close_payload["reason"] = export_status or "unknown end state"
    if not journal.log_event(close_event, ts=end_ts, payload=close_payload, **common):
        return False, f"journal write {close_event} failed"

    return True, close_event


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--sessions-dir",
        default="/opt/neurosurveillance/sessions",
        help="Directory holding *_session.json files",
    )
    p.add_argument(
        "--db",
        default="/opt/neurosurveillance/session_wal.db",
        help="Path to the session WAL SQLite database",
    )
    p.add_argument(
        "--days", type=int, default=30,
        help="Only backfill sessions started within this many days (default: 30)",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Report what would be written without modifying the WAL",
    )
    args = p.parse_args()

    sessions_dir = Path(args.sessions_dir)
    if not sessions_dir.is_dir():
        logger.error("Sessions dir not found: %s", sessions_dir)
        sys.exit(2)

    cutoff = time.time() - args.days * 86400.0

    json_files = sorted(sessions_dir.glob("*_session.json"))
    logger.info(
        "Scanning %d session JSON files in %s (cutoff: %d days)",
        len(json_files), sessions_dir, args.days,
    )

    journal = SessionJournal(db_path=args.db)
    try:
        seen = wrote = skipped_old = skipped_dup = errors = 0
        for jf in json_files:
            seen += 1
            try:
                with open(jf) as fh:
                    data = json.load(fh)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("Skipping %s: %s", jf.name, e)
                errors += 1
                continue

            start_ts = data.get("start_time_utc") or 0
            if start_ts < cutoff:
                skipped_old += 1
                continue

            ok, reason = backfill_one(journal, data, args.dry_run)
            if ok:
                wrote += 1
                logger.info(
                    "%s %s (%s): %s",
                    "Would write" if args.dry_run else "Wrote",
                    jf.name,
                    (data.get("session_id") or "")[:8],
                    reason,
                )
            elif reason == "already in WAL":
                skipped_dup += 1
            else:
                logger.warning("Skipped %s: %s", jf.name, reason)
                errors += 1

        logger.info(
            "Done. seen=%d wrote=%d skipped_old=%d skipped_dup=%d errors=%d (dry_run=%s)",
            seen, wrote, skipped_old, skipped_dup, errors, args.dry_run,
        )
    finally:
        journal.close()


if __name__ == "__main__":
    main()

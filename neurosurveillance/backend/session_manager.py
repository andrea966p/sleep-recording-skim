"""
Session Manager - Manages session lifecycle, metadata, filenames, and logging.

Handles:
- Session metadata (mouse ID, recording type, user, chamber)
- Filename generation (YYMMDDHHMM_mouseID_type.mp4)
- Session JSON sidecar file creation
- Session history tracking
"""

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from zoneinfo import ZoneInfo

from session_journal import EVENT_ABORT, EVENT_START, SessionJournal
from session_utils import generate_filename, write_session_json

logger = logging.getLogger(__name__)


@dataclass
class SessionMetadata:
    """User-provided metadata for a recording session."""
    mouse_id: str = "unknown"
    recording_type: str = "unknown"
    user_name: str = "unknown"
    chamber: Optional[int] = None

    def is_default(self) -> bool:
        """Returns True if no metadata was explicitly set."""
        return (
            self.mouse_id == "unknown"
            and self.recording_type == "unknown"
            and self.user_name == "unknown"
        )


@dataclass
class SessionRecord:
    """Complete record of a finished session."""
    session_id: str = ""
    source: str = "radiens"
    start_time_utc: float = 0.0
    end_time_utc: float = 0.0
    start_time_local: str = ""
    end_time_local: str = ""
    duration_seconds: float = 0.0
    mouse_id: str = ""
    recording_type: str = ""
    user_name: str = ""
    chamber: int = 0
    camera: str = ""
    radiens_xdat_filename: str = ""
    radiens_xdat_path: str = ""
    video_filename: str = ""
    export_status: str = "pending"
    nas_transfer_status: str = "skipped"


class SessionManager:
    """Manages session lifecycle, metadata, and logging.

    Args:
        sessions_dir: Directory for session JSON sidecar files.
        export_dir: Directory for exported MP4 files.
        tz_name: Timezone name for local timestamps (e.g. 'Asia/Seoul').
        cameras: Dict mapping chamber numbers to camera IDs.
    """

    def __init__(
        self,
        sessions_dir: str = "/opt/neurosurveillance/sessions",
        export_dir: str = "/opt/neurosurveillance/exports",
        tz_name: str = "Asia/Seoul",
        cameras: Optional[dict] = None,
        journal: Optional[SessionJournal] = None,
    ):
        self.sessions_dir = Path(sessions_dir)
        self.export_dir = Path(export_dir)
        self.tz = ZoneInfo(tz_name)
        self.journal = journal
        self.cameras = cameras or {
            "chamber_0": "pi_cam_0", "chamber_1": "pi_cam_1",
            "chamber_2": "pi_cam_2", "chamber_3": "pi_cam_3",
        }

        # Current pending metadata by chamber ID
        self._pending_metadata: dict[str, SessionMetadata] = {}

        # Active sessions by chamber ID
        self._active_sessions: dict[str, SessionRecord] = {}

        # History of completed sessions (in-memory, also persisted to disk)
        self._history: list[SessionRecord] = []

        # Ensure directories exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

        # Load existing session history from disk
        self._load_history()

    def set_metadata(
        self,
        chamber_id: str,
        mouse_id: Optional[str] = None,
        recording_type: Optional[str] = None,
        user_name: Optional[str] = None,
        chamber: Optional[int] = None,
    ) -> SessionMetadata:
        """Set metadata for the next session. Partial updates allowed."""
        if chamber_id not in self._pending_metadata:
            self._pending_metadata[chamber_id] = SessionMetadata()
            if chamber is not None:
                self._pending_metadata[chamber_id].chamber = chamber
            else:
                try:
                    self._pending_metadata[chamber_id].chamber = int(chamber_id)
                except ValueError:
                    pass

        meta = self._pending_metadata[chamber_id]
        if mouse_id is not None:
            meta.mouse_id = mouse_id
        if recording_type is not None:
            meta.recording_type = recording_type
        if user_name is not None:
            meta.user_name = user_name
        if chamber is not None:
            meta.chamber = chamber

        logger.info(
            "Session metadata updated for chamber %s: mouse=%s, type=%s, user=%s, chamber=%d",
            chamber_id, meta.mouse_id, meta.recording_type, meta.user_name, meta.chamber
        )
        return meta

    def clear_metadata(self, chamber_id: str):
        """Reset metadata to defaults for the next session."""
        if chamber_id in self._pending_metadata:
            del self._pending_metadata[chamber_id]
        logger.info("Session metadata cleared for chamber %s", chamber_id)

    def start_session(
        self,
        chamber_id: str,
        radiens_base_name: str = "",
        radiens_file_path: str = "",
    ) -> SessionRecord:
        """Start a new session. Called when Radiens R_OFF -> R_ON detected.

        Uses pending metadata (if set) and records start time.
        """
        now_utc = time.time()
        now_local = datetime.fromtimestamp(now_utc, tz=self.tz)

        meta = self._pending_metadata.get(chamber_id, SessionMetadata())
        camera_key = f"chamber_{chamber_id}"
        camera_id_str = self.cameras.get(camera_key, f"pi_cam_{chamber_id}")

        session = SessionRecord(
            session_id=str(uuid.uuid4()),
            start_time_utc=now_utc,
            start_time_local=now_local.isoformat(),
            mouse_id=meta.mouse_id,
            recording_type=meta.recording_type,
            user_name=meta.user_name,
            chamber=meta.chamber if meta.chamber is not None else (int(chamber_id) if chamber_id.isdigit() else 0),
            camera=camera_id_str,
            radiens_xdat_filename=radiens_base_name,
            radiens_xdat_path=radiens_file_path,
        )

        self._active_sessions[chamber_id] = session

        # Radiens sessions are fail-open: we can't refuse a recording that
        # Radiens already started. Log the failure and continue.
        if self.journal is not None:
            self.journal.log_event(
                EVENT_START,
                session_id=session.session_id,
                camera=session.camera,
                mouse_id=session.mouse_id,
                ts=now_utc,
                payload={
                    "source": "radiens",
                    "chamber": chamber_id,
                    "recording_type": session.recording_type,
                    "user_name": session.user_name,
                    "radiens_xdat_filename": radiens_base_name,
                },
            )

        if meta.is_default():
            logger.warning(
                "Session started for chamber %s WITHOUT metadata (using defaults). "
                "Files will be named with 'unknown' placeholders.", chamber_id
            )
        else:
            logger.info(
                "Session started for chamber %s: mouse=%s, type=%s, user=%s, camera=%s",
                chamber_id, session.mouse_id, session.recording_type,
                session.user_name, session.camera,
            )

        return session

    def end_session(self, chamber_id: str) -> Optional[SessionRecord]:
        """End the active session. Called when Radiens R_ON -> R_OFF detected."""
        if chamber_id not in self._active_sessions:
            logger.warning("end_session called for chamber %s but no active session", chamber_id)
            return None

        session = self._active_sessions.pop(chamber_id)
        now_utc = time.time()
        now_local = datetime.fromtimestamp(now_utc, tz=self.tz)

        session.end_time_utc = now_utc
        session.end_time_local = now_local.isoformat()
        session.duration_seconds = round(now_utc - session.start_time_utc, 1)
        session.video_filename = self._generate_filename(session)

        logger.info(
            "Session ended for chamber %s: duration=%.0fs, filename=%s",
            chamber_id, session.duration_seconds, session.video_filename,
        )

        # Write session sidecar JSON
        self._write_session_json(session)

        # Add to history
        self._history.append(session)

        # Clear metadata for next run
        self.clear_metadata(chamber_id)

        return session

    def abort_session(self, chamber_id: str, reason: str = "daemon shutdown") -> Optional[SessionRecord]:
        """Abort the active session for a chamber."""
        if chamber_id not in self._active_sessions:
            return None

        session = self._active_sessions.pop(chamber_id)
        now_utc = time.time()
        now_local = datetime.fromtimestamp(now_utc, tz=self.tz)

        session.end_time_utc = now_utc
        session.end_time_local = now_local.isoformat()
        session.duration_seconds = round(now_utc - session.start_time_utc, 1)
        session.video_filename = self._generate_filename(session)
        session.export_status = f"aborted: {reason}"

        logger.warning(
            "Session ABORTED for chamber %s: reason=%s, duration=%.0fs",
            chamber_id, reason, session.duration_seconds,
        )

        if self.journal is not None:
            self.journal.log_event(
                EVENT_ABORT,
                session_id=session.session_id,
                camera=session.camera,
                mouse_id=session.mouse_id,
                ts=now_utc,
                payload={
                    "reason": reason,
                    "duration_seconds": session.duration_seconds,
                },
            )

        self._write_session_json(session)
        self._history.append(session)
        self.clear_metadata(chamber_id)

        return session

    def update_export_status(self, session_id: str, status: str):
        """Update the export status of a session by ID."""
        for session in reversed(self._history):
            if session.session_id == session_id:
                session.export_status = status
                # Re-write the session JSON with updated status
                self._write_session_json(session)
                return
        logger.warning(
            "Cannot update export status: session %s not found",
            session_id[:8],
        )

    def _generate_filename(self, session: SessionRecord) -> str:
        """Generate filename: YYMMDDHHMM_mouseID_type.mp4"""
        return generate_filename(
            start_time_utc=session.start_time_utc,
            mouse_id=session.mouse_id,
            recording_type=session.recording_type,
            tz=self.tz,
        )

    def _write_session_json(self, session: SessionRecord):
        """Write session sidecar JSON to disk."""
        write_session_json(session, self.sessions_dir)

    def _load_history(self):
        """Load session history from existing JSON files on disk."""
        try:
            json_files = sorted(self.sessions_dir.glob("*_session.json"))
            for json_file in json_files:
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    
                    # Skip manual sessions, they are loaded by ManualSessionManager
                    if data.get("source") == "manual":
                        continue

                    record = SessionRecord(**{
                        k: v for k, v in data.items()
                        if k in SessionRecord.__dataclass_fields__
                    })
                    self._history.append(record)
                except Exception as e:
                    logger.warning("Failed to load session file %s: %s", json_file, e)

            if self._history:
                logger.info("Loaded %d session records from disk", len(self._history))
        except Exception as e:
            logger.warning("Failed to scan session history directory: %s", e)

    @property
    def active_sessions(self) -> dict[str, SessionRecord]:
        """The currently active sessions dict."""
        return self._active_sessions

    @property
    def pending_metadata(self) -> dict[str, SessionMetadata]:
        """The metadata set for the next sessions."""
        return self._pending_metadata

    @property
    def history(self) -> list[SessionRecord]:
        """All completed sessions."""
        return self._history

    @property
    def has_active_sessions(self) -> bool:
        return len(self._active_sessions) > 0

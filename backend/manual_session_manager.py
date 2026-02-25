"""
Manual Session Manager - Tracks per-camera manual recording sessions.

Handles recordings triggered externally (e.g. clicking Record in Frigate's
web UI) rather than by the Radiens poller. Each camera is tracked independently.

Manual sessions use source="manual" in their JSON sidecars and follow a
simplified naming convention when no metadata is set.
"""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from zoneinfo import ZoneInfo

from session_utils import generate_filename, write_session_json

logger = logging.getLogger(__name__)


@dataclass
class ManualSessionRecord:
    """Record of a manual (UI-triggered) recording session."""
    session_id: str = ""
    source: str = "manual"
    start_time_utc: float = 0.0
    end_time_utc: float = 0.0
    start_time_local: str = ""
    end_time_local: str = ""
    duration_seconds: float = 0.0
    camera: str = ""
    video_filename: str = ""
    export_status: str = "pending"


class ManualSessionManager:
    """Manages per-camera manual recording sessions.

    Args:
        sessions_dir: Directory for session JSON sidecar files.
        export_dir: Directory for exported MP4 files.
        tz_name: Timezone name for local timestamps.
        min_duration: Minimum recording duration in seconds to export.
    """

    def __init__(
        self,
        sessions_dir: str = "/opt/neurosurveillance/sessions",
        export_dir: str = "/opt/neurosurveillance/exports",
        tz_name: str = "Asia/Seoul",
        min_duration: float = 5.0,
    ):
        self.sessions_dir = Path(sessions_dir)
        self.export_dir = Path(export_dir)
        self.tz = ZoneInfo(tz_name)
        self.min_duration = min_duration

        # Per-camera active manual sessions: camera_id -> ManualSessionRecord
        self._active: dict[str, ManualSessionRecord] = {}

        # Completed manual sessions (in-memory + persisted to disk)
        self._history: list[ManualSessionRecord] = []

        # Ensure directories exist
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

        # Load existing manual session history from disk
        self._load_history()

    def start_recording(self, camera_id: str) -> ManualSessionRecord:
        """Start tracking a manual recording for a camera.

        Args:
            camera_id: Frigate camera name (e.g. 'pi_cam_0').

        Returns:
            The new ManualSessionRecord.
        """
        now_utc = time.time()
        now_local = datetime.fromtimestamp(now_utc, tz=self.tz)

        session = ManualSessionRecord(
            session_id=str(uuid.uuid4()),
            start_time_utc=now_utc,
            start_time_local=now_local.isoformat(),
            camera=camera_id,
        )

        self._active[camera_id] = session

        logger.info(
            "Manual recording started: camera=%s, session=%s",
            camera_id,
            session.session_id[:8],
        )
        return session

    def stop_recording(self, camera_id: str) -> Optional[ManualSessionRecord]:
        """Stop tracking a manual recording for a camera.

        Records end time, generates filename, writes JSON sidecar.
        Returns None if no active manual session for this camera,
        or if the duration is below min_duration (accidental click).

        Args:
            camera_id: Frigate camera name.

        Returns:
            The completed ManualSessionRecord, or None.
        """
        session = self._active.pop(camera_id, None)
        if session is None:
            logger.warning(
                "stop_recording called for %s but no active manual session",
                camera_id,
            )
            return None

        now_utc = time.time()
        now_local = datetime.fromtimestamp(now_utc, tz=self.tz)

        session.end_time_utc = now_utc
        session.end_time_local = now_local.isoformat()
        session.duration_seconds = round(now_utc - session.start_time_utc, 1)

        # Check minimum duration (filter accidental clicks)
        if session.duration_seconds < self.min_duration:
            logger.info(
                "Manual recording on %s too short (%.1fs < %.1fs), ignoring",
                camera_id,
                session.duration_seconds,
                self.min_duration,
            )
            return None

        # Generate filename: YYMMDDHHMM_manual_cameraID.mp4
        session.video_filename = generate_filename(
            start_time_utc=session.start_time_utc,
            mouse_id="manual",
            recording_type=camera_id,
            tz=self.tz,
        )

        logger.info(
            "Manual recording ended: camera=%s, duration=%.0fs, filename=%s",
            camera_id,
            session.duration_seconds,
            session.video_filename,
        )

        # Write session sidecar JSON
        write_session_json(session, self.sessions_dir)

        # Add to history
        self._history.append(session)

        return session

    def update_export_status(self, session_id: str, status: str):
        """Update the export status of a manual session by ID."""
        for session in reversed(self._history):
            if session.session_id == session_id:
                session.export_status = status
                write_session_json(session, self.sessions_dir)
                return
        logger.warning(
            "Cannot update export status: manual session %s not found",
            session_id[:8],
        )

    def has_active_recording(self, camera_id: str) -> bool:
        """Check if a camera has an active manual recording."""
        return camera_id in self._active

    def _load_history(self):
        """Load manual session history from existing JSON files on disk."""
        try:
            json_files = sorted(self.sessions_dir.glob("*_session.json"))
            for json_file in json_files:
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    # Only load manual sessions
                    if data.get("source") != "manual":
                        continue
                    record = ManualSessionRecord(**{
                        k: v for k, v in data.items()
                        if k in ManualSessionRecord.__dataclass_fields__
                    })
                    self._history.append(record)
                except Exception as e:
                    logger.warning(
                        "Failed to load manual session file %s: %s",
                        json_file, e,
                    )

            if self._history:
                logger.info(
                    "Loaded %d manual session records from disk",
                    len(self._history),
                )
        except Exception as e:
            logger.warning("Failed to scan manual session history: %s", e)

    @property
    def active_recordings(self) -> dict[str, ManualSessionRecord]:
        """All active manual recordings (camera_id -> session)."""
        return dict(self._active)

    @property
    def history(self) -> list[ManualSessionRecord]:
        """All completed manual sessions."""
        return self._history

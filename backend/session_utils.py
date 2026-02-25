"""
Session Utilities - Shared helper functions for session management.

Provides filename generation and JSON sidecar writing used by both
SessionManager (Radiens sessions) and ManualSessionManager (manual recordings).
"""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


def generate_filename(
    start_time_utc: float,
    mouse_id: str,
    recording_type: str,
    tz: ZoneInfo,
    extension: str = ".mp4",
) -> str:
    """Generate filename: YYMMDDHHMM_mouseID_type.mp4

    Uses local time for the timestamp portion.

    Args:
        start_time_utc: Unix epoch timestamp (UTC).
        mouse_id: Mouse identifier (spaces replaced with underscores).
        recording_type: Recording type (spaces replaced with underscores).
        tz: Timezone for local timestamp.
        extension: File extension (default .mp4).

    Returns:
        Formatted filename string.
    """
    start_local = datetime.fromtimestamp(start_time_utc, tz=tz)
    timestamp = start_local.strftime("%y%m%d%H%M")
    mouse = mouse_id.replace(" ", "_")
    rec_type = recording_type.replace(" ", "_")
    return f"{timestamp}_{mouse}_{rec_type}{extension}"


def write_session_json(session, sessions_dir: Path) -> None:
    """Write session sidecar JSON to disk.

    Args:
        session: A dataclass instance with a video_filename and session_id attribute.
        sessions_dir: Directory to write JSON files into.
    """
    base = (
        session.video_filename.rsplit(".", 1)[0]
        if session.video_filename
        else session.session_id
    )
    json_filename = f"{base}_session.json"
    json_path = sessions_dir / json_filename

    try:
        data = asdict(session)
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info("Session JSON written: %s", json_path)
    except Exception as e:
        logger.error("Failed to write session JSON to %s: %s", json_path, e)

"""
HTTP REST API - Lightweight Flask API for session metadata and status.

Binds to 127.0.0.1:8585 (localhost only). Provides endpoints for:
- Setting session metadata (mouse_id, recording_type, user_name, chamber)
- Querying daemon status, current session, and session history
- Health check for systemd watchdog

This API is consumed by the future UI (deferred to external app-building tool).
It can also be used directly via curl for testing and scripting.
"""

import logging
import re
from dataclasses import asdict
from typing import TYPE_CHECKING

from flask import Flask, jsonify, request

if TYPE_CHECKING:
    from session_manager import SessionManager
    from radiens_poller import RadiensPoller
    from frigate_controller import FrigateController
    from manual_session_manager import ManualSessionManager

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    """Allow requests from Tauri webview (tauri://localhost) and dev servers."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# These are set by daemon.py at startup via init_api()
_session_manager: "SessionManager | None" = None
_radiens_poller: "RadiensPoller | None" = None
_frigate_controller: "FrigateController | None" = None
_manual_session_manager: "ManualSessionManager | None" = None
_config: dict | None = None


def init_api(
    session_manager: "SessionManager",
    radiens_poller: "RadiensPoller",
    frigate_controller: "FrigateController",
    config: dict,
    manual_session_manager: "ManualSessionManager | None" = None,
):
    """Initialize the API with references to daemon components.

    Called once by daemon.py before starting the Flask server.
    """
    global _session_manager, _radiens_poller, _frigate_controller, _config
    global _manual_session_manager
    _session_manager = session_manager
    _radiens_poller = radiens_poller
    _frigate_controller = frigate_controller
    _manual_session_manager = manual_session_manager
    _config = config
    logger.info("API initialized")


def sanitize_input(value: str) -> str:
    """Sanitize string input to prevent path traversal and shell injection.
    Allows alphanumeric characters, dashes, and underscores.
    """
    if not isinstance(value, str):
        return ""
    return re.sub(r"[^a-zA-Z0-9\-_]", "", value)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.route("/api/status", methods=["GET"])
def get_status():
    """Daemon status overview.

    Returns:
        - daemon: running state
        - radiens: connection status, current recording state
        - mqtt: connection status
        - frigate: reachable or not
        - session: active session summary (if any)
        - pending_metadata: metadata set for next session
    """
    radiens_connected = _radiens_poller.connected if _radiens_poller else False
    radiens_state = (
        _radiens_poller.previous_state.value if _radiens_poller else "UNKNOWN"
    )

    mqtt_connected = (
        _frigate_controller.mqtt_connected if _frigate_controller else False
    )

    active = {}
    if _session_manager and _session_manager.has_active_sessions:
        for chamber_id, session in _session_manager.active_sessions.items():
            active[chamber_id] = {
                "session_id": session.session_id,
                "mouse_id": session.mouse_id,
                "recording_type": session.recording_type,
                "chamber": session.chamber,
                "camera": session.camera,
                "start_time_local": session.start_time_local,
            }

    pending = {}
    if _session_manager:
        for chamber_id, meta in _session_manager.pending_metadata.items():
            pending[chamber_id] = {
                "mouse_id": meta.mouse_id,
                "recording_type": meta.recording_type,
                "user_name": meta.user_name,
                "chamber": meta.chamber,
                "is_default": meta.is_default(),
            }

    # Manual recordings currently active
    manual = {}
    if _manual_session_manager:
        for cam_id, rec in _manual_session_manager.active_recordings.items():
            manual[cam_id] = {
                "session_id": rec.session_id,
                "camera": rec.camera,
                "start_time_local": rec.start_time_local,
            }

    # Send the same recording state to all configured chambers
    radiens_recording_states = {
        str(c_id).replace("chamber_", ""): radiens_state
        for c_id in _config.get("cameras", {})
    } if _config else {"0": radiens_state}

    return jsonify({
        "daemon": "running",
        "radiens": {
            "connected": radiens_connected,
            "recording_states": radiens_recording_states,
        },
        "mqtt": {
            "connected": mqtt_connected,
        },
        "sessions": active,
        "pending_metadata": pending,
        "manual_recordings": manual,
    })


@app.route("/api/session/metadata", methods=["POST"])
def set_metadata():
    """Set metadata for the next recording session.

    Accepts JSON body with any combination of:
        - mouse_id (str): Mouse identifier (e.g. "HETCF3R1")
        - recording_type (str): Recording type (e.g. "basal", "sd")
        - user_name (str): Researcher name (e.g. "andrea")
        - chamber (int): Chamber number (0 or 1)

    Partial updates are allowed -- only provided fields are changed.

    Returns:
        Updated metadata.

    Example:
        curl -X POST http://127.0.0.1:8585/api/session/metadata?chamber_id=0 \\
          -H "Content-Type: application/json" \\
          -d '{"mouse_id": "HETCF3R1", "recording_type": "basal", "chamber": 0}'
    """
    if not _session_manager:
        return jsonify({"error": "Session manager not initialized"}), 503

    chamber_id = request.args.get("chamber_id")
    if not chamber_id:
        # Backward compatibility / fallback
        chamber_id = "0"

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate chamber if provided
    if "chamber" in data:
        try:
            chamber = int(data["chamber"])
            valid_chambers = [
                int(c_id.replace("chamber_", ""))
                for c_id in _config.get("cameras", {})
            ] if _config else [0, 1, 2, 3]
            if chamber not in valid_chambers:
                return jsonify({
                    "error": f"Invalid chamber: {chamber}. Valid: {valid_chambers}"
                }), 400
            data["chamber"] = chamber
        except (ValueError, TypeError):
            return jsonify({
                "error": "chamber must be an integer"
            }), 400

    # Validate lab member if user_name provided
    if "user_name" in data and _config:
        lab_members = _config.get("lab_members", [])
        if lab_members and data["user_name"] not in lab_members:
            logger.warning(
                "user_name '%s' not in lab_members list: %s",
                data["user_name"],
                lab_members,
            )
            # Warning only -- don't reject the request

    # Sanitize string inputs to prevent path traversal
    safe_mouse_id = sanitize_input(data.get("mouse_id", "")) if "mouse_id" in data else None
    safe_recording_type = sanitize_input(data.get("recording_type", "")) if "recording_type" in data else None
    safe_user_name = sanitize_input(data.get("user_name", "")) if "user_name" in data else None

    updated = _session_manager.set_metadata(
        chamber_id=chamber_id,
        mouse_id=safe_mouse_id,
        recording_type=safe_recording_type,
        user_name=safe_user_name,
        chamber=data.get("chamber"),
    )

    return jsonify({
        "status": "ok",
        "metadata": {
            "mouse_id": updated.mouse_id,
            "recording_type": updated.recording_type,
            "user_name": updated.user_name,
            "chamber": updated.chamber,
            "is_default": updated.is_default(),
        },
    })


@app.route("/api/session/metadata", methods=["DELETE"])
def clear_metadata():
    """Clear pending metadata (reset to defaults)."""
    if not _session_manager:
        return jsonify({"error": "Session manager not initialized"}), 503

    chamber_id = request.args.get("chamber_id")
    if not chamber_id:
        chamber_id = "0"

    _session_manager.clear_metadata(chamber_id)
    return jsonify({"status": "ok", "message": f"Metadata cleared for chamber {chamber_id}"})


@app.route("/api/session/current", methods=["GET"])
def get_current_session():
    """Get the currently active session, if any.

    Returns:
        Session details if active, or {"session": null}.
    """
    if not _session_manager:
        return jsonify({"error": "Session manager not initialized"}), 503

    if _session_manager.has_active_sessions:
        # Return the first active session for compatibility, or check chamber_id
        session = next(iter(_session_manager.active_sessions.values()))
        return jsonify({"session": asdict(session)})

    return jsonify({"session": None})


@app.route("/api/session/history", methods=["GET"])
def get_session_history():
    """List past sessions.

    Query parameters:
        - limit (int): Max number of sessions to return (default 50, newest first)
        - source (str): Filter by source ("radiens", "manual", or omit for all)

    Returns:
        List of session records.
    """
    if not _session_manager:
        return jsonify({"error": "Session manager not initialized"}), 503

    limit = request.args.get("limit", 50, type=int)
    limit = max(1, min(limit, 500))  # Clamp between 1 and 500
    source_filter = request.args.get("source")

    # Combine Radiens and manual histories
    all_sessions = []

    if source_filter is None or source_filter == "radiens":
        all_sessions.extend(
            [asdict(s) for s in _session_manager.history]
        )

    if _manual_session_manager and (
        source_filter is None or source_filter == "manual"
    ):
        all_sessions.extend(
            [asdict(s) for s in _manual_session_manager.history]
        )

    # Sort by start_time_utc descending (newest first)
    all_sessions.sort(key=lambda s: s.get("start_time_utc", 0), reverse=True)

    # Apply limit
    recent = all_sessions[:limit]

    return jsonify({
        "count": len(recent),
        "total": len(all_sessions),
        "sessions": recent,
    })


@app.route("/api/session/manual", methods=["GET"])
def get_manual_sessions():
    """Get active and recent manual recording sessions.

    Returns:
        - active: Dict of camera_id -> active manual session info
        - recent: Last 10 completed manual sessions (newest first)
    """
    if not _manual_session_manager:
        return jsonify({"error": "Manual session manager not initialized"}), 503

    active = {}
    for cam_id, rec in _manual_session_manager.active_recordings.items():
        active[cam_id] = asdict(rec)

    history = _manual_session_manager.history
    recent = [asdict(s) for s in reversed(history[-10:])]

    return jsonify({
        "active": active,
        "recent_count": len(recent),
        "recent": recent,
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint.

    Returns 200 if the daemon is running and core services are connected.
    Returns 503 if critical services are down.

    Used by systemd watchdog and monitoring.
    """
    radiens_ok = _radiens_poller.connected if _radiens_poller else False
    mqtt_ok = _frigate_controller.mqtt_connected if _frigate_controller else False

    healthy = radiens_ok and mqtt_ok
    status_code = 200 if healthy else 503

    return jsonify({
        "healthy": healthy,
        "radiens_connected": radiens_ok,
        "mqtt_connected": mqtt_ok,
    }), status_code

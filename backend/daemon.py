"""
Session Daemon - Main entry point for the NeuroSurveillance Session Controller.

Orchestrates all components:
1. Loads config.yaml
2. Connects MQTT, connects Radiens
3. Publishes OFF to all cameras on startup (clean slate)
4. Starts Flask API in background thread
5. Main polling loop: poll Radiens every 1s, detect transitions
6. SIGTERM handler: abort active session, publish OFF, disconnect

Usage:
    python daemon.py [--config /path/to/config.yaml]
"""

import argparse
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import yaml

from radiens_poller import RadiensPoller, RadiensStatus
from frigate_controller import FrigateController
from session_manager import SessionManager
from manual_session_manager import ManualSessionManager
from recording_watchdog import RecordingWatchdog
from storage_monitor import StorageMonitor
from api import app, init_api

logger = logging.getLogger("neurosurveillance")

# ---------------------------------------------------------------------------
# Default config path
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH = "/opt/neurosurveillance/config.yaml"


def load_config(config_path: str) -> dict:
    """Load and validate config.yaml."""
    path = Path(config_path)
    if not path.exists():
        logger.error("Config file not found: %s", config_path)
        sys.exit(1)

    with open(path) as f:
        config = yaml.safe_load(f)

    if not config:
        logger.error("Config file is empty: %s", config_path)
        sys.exit(1)

    # Validate required sections
    required = ["daemon", "api", "mqtt", "frigate", "cameras"]
    for section in required:
        if section not in config:
            logger.error("Missing required config section: '%s'", section)
            sys.exit(1)

    return config


def setup_logging(config: dict):
    """Configure logging with console and rotating file output."""
    daemon_cfg = config.get("daemon", {})
    log_level_str = daemon_cfg.get("log_level", "info").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    log_dir = daemon_cfg.get("log_dir", "/opt/neurosurveillance/logs")

    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    # File handler (rotating, 10MB, keep 5 files)
    log_file = os.path.join(log_dir, "session-daemon.log")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logger.info("Logging configured: level=%s, file=%s", log_level_str, log_file)


class SessionDaemon:
    """Main daemon that orchestrates Radiens polling, Frigate control, and the API."""

    def __init__(self, config: dict):
        self.config = config
        self._running = False
        self._shutdown_event = threading.Event()

        daemon_cfg = config.get("daemon", {})
        self.poll_interval = daemon_cfg.get("poll_interval", 1.0)
        tz_name = daemon_cfg.get("timezone", "Asia/Seoul")

        cameras = config.get("cameras", {})
        sessions_dir = config.get("sessions", {}).get(
            "data_dir", "/opt/neurosurveillance/sessions"
        )

        # Initialize components
        self.session_manager = SessionManager(
            sessions_dir=sessions_dir,
            export_dir=config["frigate"].get(
                "export_dir", "/opt/neurosurveillance/exports"
            ),
            tz_name=tz_name,
            cameras=cameras,
        )

        # Manual session config
        manual_cfg = config.get("manual_sessions", {})
        self.manual_sessions_enabled = manual_cfg.get("enabled", True)
        manual_min_duration = manual_cfg.get("min_duration", 5)

        self.manual_session_manager = ManualSessionManager(
            sessions_dir=sessions_dir,
            export_dir=config["frigate"].get(
                "export_dir", "/opt/neurosurveillance/exports"
            ),
            tz_name=tz_name,
            min_duration=manual_min_duration,
        )

        self.export_source_dir = Path(
            config["frigate"].get("export_source_dir", "/srv/frigate/storage/exports")
        )

        self.frigate = FrigateController(
            mqtt_host=config["mqtt"].get("host", "127.0.0.1"),
            mqtt_port=config["mqtt"].get("port", 1883),
            frigate_url=config["frigate"].get("url", "http://127.0.0.1:5000"),
            cameras=cameras,
            mqtt_user=config["mqtt"].get("user"),
            mqtt_password=config["mqtt"].get("password"),
        )

        self.poller = RadiensPoller(
            poll_interval=self.poll_interval,
            on_session_start=self._handle_session_start,
            on_session_end=self._handle_session_end,
        )

        # Storage monitor
        self.storage_monitor = StorageMonitor(config)

        # Recording watchdog — detects stalled Frigate recordings on active cameras.
        self.watchdog = RecordingWatchdog(
            frigate_db_path=config["frigate"].get(
                "db_path", "/srv/frigate/storage/frigate.db"
            ),
            active_cameras_provider=self._active_recording_cameras,
            mqtt_publish=self.frigate.publish,
        )

        # Initialize the Flask API with references to components
        init_api(
            session_manager=self.session_manager,
            radiens_poller=self.poller,
            frigate_controller=self.frigate,
            config=config,
            manual_session_manager=self.manual_session_manager,
            storage_monitor=self.storage_monitor,
            recording_watchdog=self.watchdog,
        )

    def _active_recording_cameras(self) -> dict[str, float]:
        """Cameras the daemon currently considers actively recording, with start times."""
        out: dict[str, float] = {}
        for cam, rec in self.manual_session_manager.active_recordings.items():
            out[cam] = rec.start_time_utc
        for sess in self.session_manager.active_sessions.values():
            if sess and sess.camera:
                out[sess.camera] = sess.start_time_utc
        return out

    def start(self):
        """Start the daemon: connect services, reset state, run main loop."""
        logger.info("=" * 60)
        logger.info("NeuroSurveillance Session Daemon starting")
        logger.info("=" * 60)

        self._running = True

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # 1. Connect to MQTT
        logger.info("Connecting to MQTT broker...")
        if not self.frigate.connect_mqtt():
            logger.error(
                "Failed to connect to MQTT broker at %s:%d. "
                "Ensure Mosquitto is running (docker ps).",
                self.config["mqtt"].get("host"),
                self.config["mqtt"].get("port"),
            )
            sys.exit(1)

        # 2. Reset recording state (clean slate)
        logger.info("Resetting all camera recordings to OFF (clean slate)...")
        self.frigate.stop_all_recording()

        # 2b. Startup grace period: Frigate's config has record.enabled=true,
        # so it reasserts ON shortly after we publish OFF. We must wait for
        # that reassertion to pass before registering the external change
        # callback, otherwise we get false manual sessions on every startup.
        if self.manual_sessions_enabled:
            grace_seconds = 10
            logger.info(
                "Waiting %ds for Frigate recording state to settle...",
                grace_seconds,
            )
            time.sleep(grace_seconds)

            # Drain any pending state messages that arrived during grace period
            self.frigate.clear_expected_states()

            self.frigate.register_external_recording_callback(
                self._handle_external_recording_change
            )
            logger.info("Manual session detection enabled")

        # 3. Connect to Radiens
        logger.info("Connecting to Radiens...")
        if not self.poller.connect():
            logger.warning(
                "Could not connect to Radiens on startup. "
                "The daemon will keep retrying in the main loop. "
                "Ensure Radiens is running."
            )
            # Do NOT exit -- Radiens may start later

        # 4. Start storage monitoring
        self.storage_monitor.start()

        # 4b. Start recording watchdog
        self.watchdog.start()

        # 5. Start Flask API in background thread
        api_host = self.config["api"].get("host", "127.0.0.1")
        api_port = self.config["api"].get("port", 8585)
        api_thread = threading.Thread(
            target=self._run_api,
            args=(api_host, api_port),
            daemon=True,
            name="api-thread",
        )
        api_thread.start()
        logger.info("API server started on http://%s:%d", api_host, api_port)

        # 5. Main polling loop
        logger.info(
            "Entering main loop (poll interval: %.1fs)", self.poll_interval
        )
        self._main_loop()

    def _main_loop(self):
        """Poll Radiens continuously. Transitions trigger callbacks."""
        while self._running and not self._shutdown_event.is_set():
            # If Radiens is not connected, try to reconnect
            if not self.poller.connected:
                self.poller.connect()

            # Poll (handles transitions via callbacks)
            self.poller.poll()

            # Sleep with shutdown check
            self._shutdown_event.wait(timeout=self.poll_interval)

    def _handle_session_start(self, status: RadiensStatus):
        """Called when Radiens transitions R_OFF -> R_ON."""
        logger.info(">>> SESSION START detected")

        # For multi-chamber, we start a session for each configured chamber.
        # Currently leveraging the single global Radiens status.
        chambers_to_start = [
            str(c_id).replace("chamber_", "")
            for c_id in self.session_manager.cameras
        ]

        # Storage cap enforcement
        allowed, reason = self.storage_monitor.can_start_recording(
            num_cameras=len(chambers_to_start)
        )
        if not allowed:
            logger.error("SESSION START BLOCKED — storage cap: %s", reason)
            return

        for chamber_id in chambers_to_start:
            if chamber_id not in self.session_manager.active_sessions:
                # Start session in manager (uses pending metadata)
                session = self.session_manager.start_session(
                    chamber_id=chamber_id,
                    radiens_base_name=status.base_name,
                    radiens_file_path=status.file_path,
                )

                # Enable Frigate recording for this session's camera
                if not self.frigate.set_recording(session.camera, enabled=True):
                    logger.error(
                        "Failed to enable Frigate recording for %s. "
                        "Video may not be captured for this session!",
                        session.camera,
                    )

                logger.info(
                    "Session %s active for chamber %s: camera=%s, mouse=%s, type=%s",
                    session.session_id[:8],
                    chamber_id,
                    session.camera,
                    session.mouse_id,
                    session.recording_type,
                )

    def _handle_session_end(self, status: RadiensStatus):
        """Called when Radiens transitions R_ON -> R_OFF."""
        logger.info(">>> SESSION END detected")

        # End all active sessions
        active_chambers = list(self.session_manager.active_sessions.keys())
        for chamber_id in active_chambers:
            session = self.session_manager.end_session(chamber_id)
            if session is None:
                continue

            # Disable Frigate recording
            self.frigate.set_recording(session.camera, enabled=False)

            logger.info(
                "Session %s ended for chamber %s: duration=%.0fs, filename=%s",
                session.session_id[:8],
                chamber_id,
                session.duration_seconds,
                session.video_filename,
            )

            # Export video from Frigate (runs in a background thread)
            export_thread = threading.Thread(
                target=self._export_session,
                args=(session,),
                daemon=True,
                name=f"export-{session.session_id[:8]}",
            )
            export_thread.start()

    def _export_session(self, session):
        """Export video from Frigate. Runs in a background thread."""
        self._execute_export(
            session=session,
            manager=self.session_manager,
            label="session",
        )

    def _execute_export(self, session, manager, label: str):
        """Shared export logic for both Radiens and manual sessions.

        Args:
            session: The completed SessionRecord or ManualSessionRecord.
            manager: The session manager that owns this session (for status updates).
            label: Human-readable label for log messages ("session" or "manual session").
        """
        sid = session.session_id[:8]
        try:
            logger.info("Starting Frigate export for %s %s...", label, sid)

            export_name = session.video_filename.rsplit(".", 1)[0] if session.video_filename else ""
            export_id = self.frigate.export_recording(
                camera_id=session.camera,
                start_time=session.start_time_utc - 2,
                end_time=session.end_time_utc + 2,
                name=export_name,
            )

            if export_id is None:
                logger.error("Frigate export request failed for %s %s", label, sid)
                manager.update_export_status(session.session_id, "failed: export request rejected")
                return

            result = self.frigate.wait_for_export(export_id)
            if result is None:
                logger.error("Frigate export timed out for %s %s", label, sid)
                manager.update_export_status(session.session_id, "failed: export timed out")
                return

            manager.update_export_status(session.session_id, "completed")

            video_path = result.get("video_path")
            if video_path and session.video_filename:
                self._move_export_file(
                    video_path, session, self.export_source_dir, manager.export_dir, manager.tz
                )

            logger.info("Export completed for %s %s: %s", label, sid, session.video_filename)

        except Exception as e:
            logger.error("Export failed for %s %s: %s", label, sid, e, exc_info=True)
            manager.update_export_status(session.session_id, f"failed: {e}")

    def _move_export_file(self, video_path: str, session, export_source_dir: Path, export_dir: Path, tz):
        """Move a Frigate export to the organized user/mouse/date directory.

        Frigate writes exports as root-owned files into export_source_dir.
        This waits for the file to appear there, then moves it into the
        organized export_dir tree (user/mouse/date) with the session filename.
        """
        frigate_filename = os.path.basename(video_path)
        source_path = export_source_dir / frigate_filename

        if not self._wait_for_file(source_path):
            logger.warning("Export file not found on disk for renaming: %s", source_path)
            return

        local_date = datetime.fromtimestamp(session.start_time_utc, tz=tz).strftime("%Y-%m-%d")
        user_dir = session.user_name.replace(" ", "_")
        mouse_dir = session.mouse_id.replace(" ", "_")
        target_dir = export_dir / user_dir / mouse_dir / local_date
        target_path = target_dir / session.video_filename

        try:
            logger.info("Moving export (via sudo): %s -> %s", frigate_filename, target_path)
            subprocess.run(["sudo", "mkdir", "-p", str(target_dir)], check=True)
            subprocess.run(
                ["sudo", "chown", "-R", "skimlab:skimlab", str(export_dir / user_dir)],
                check=False,
            )
            proc = subprocess.run(
                ["sudo", "mv", str(source_path), str(target_path)],
                capture_output=True, text=True,
            )
            if proc.returncode == 0:
                subprocess.run(["sudo", "chown", "skimlab:skimlab", str(target_path)], check=False)
                logger.info("Successfully moved export %s -> %s", frigate_filename, target_path)
            else:
                logger.error("Failed to move export: %s", proc.stderr)
        except Exception as e:
            logger.error("Failed to execute move command: %s", e)

    @staticmethod
    def _wait_for_file(path: Path, timeout: int = 10) -> bool:
        """Wait up to timeout seconds for a file to appear on disk."""
        for _ in range(timeout):
            if path.exists():
                return True
            time.sleep(1.0)
        return False

    def _handle_external_recording_change(self, camera_id: str, state: str):
        """Handle an externally-triggered recording state change.

        Called by FrigateController when a recording state change is detected
        that was NOT initiated by this daemon (e.g. Frigate UI Record button).
        """
        if state == "ON":
            self._handle_external_recording_on(camera_id)
        elif state == "OFF":
            self._handle_external_recording_off(camera_id)

    def _handle_external_recording_on(self, camera_id: str):
        """Start a manual recording session when Frigate UI triggers Record ON."""
        if self._is_radiens_active_for(camera_id):
            return

        # Storage cap enforcement
        allowed, reason = self.storage_monitor.can_start_recording(num_cameras=1)
        if not allowed:
            logger.error(
                "MANUAL RECORDING BLOCKED for %s — storage cap: %s",
                camera_id, reason,
            )
            self.frigate.set_recording(camera_id, enabled=False)
            return

        mouse_id, recording_type, user_name = self._resolve_manual_metadata(camera_id)
        self.manual_session_manager.start_recording(
            camera_id,
            mouse_id=mouse_id,
            recording_type=recording_type,
            user_name=user_name,
        )

    def _handle_external_recording_off(self, camera_id: str):
        """Stop a manual recording and kick off export when Frigate UI triggers Record OFF."""
        session = self.manual_session_manager.stop_recording(camera_id)
        if session is None:
            return

        export_thread = threading.Thread(
            target=self._export_manual_session,
            args=(session,),
            daemon=True,
            name=f"manual-export-{session.session_id[:8]}",
        )
        export_thread.start()

    def _is_radiens_active_for(self, camera_id: str) -> bool:
        """Check if a Radiens session is already active for this camera."""
        if not self.session_manager.has_active_sessions:
            return False
        for chamber_id, active in self.session_manager.active_sessions.items():
            if active and active.camera == camera_id:
                logger.info(
                    "Ignoring external Record ON for %s: "
                    "Radiens session already active for chamber %s",
                    camera_id, chamber_id,
                )
                return True
        return False

    def _resolve_manual_metadata(self, camera_id: str) -> tuple:
        """Look up pending UI metadata for a camera, returning (mouse_id, recording_type, user_name).

        Falls back to ("manual", camera_id, "manual") if no metadata is queued.
        """
        chamber_id = self._camera_to_chamber(camera_id)
        if chamber_id is None:
            return "manual", camera_id, "manual"

        pending = self.session_manager.pending_metadata.get(chamber_id)
        if pending is None:
            return "manual", camera_id, "manual"

        mouse_id = pending.mouse_id or "manual"
        recording_type = pending.recording_type or camera_id
        user_name = pending.user_name or "manual"
        logger.info("Bound UI metadata to manual recording on %s: mouse=%s", camera_id, mouse_id)
        self.session_manager.clear_metadata(chamber_id)
        return mouse_id, recording_type, user_name

    def _camera_to_chamber(self, camera_id: str) -> str | None:
        """Map a camera ID (e.g. 'pi_cam_0') to its chamber number string (e.g. '0')."""
        for c_id, cam_str in self.config.get("cameras", {}).items():
            if cam_str == camera_id:
                return str(c_id).replace("chamber_", "")
        return None

    def _export_manual_session(self, session):
        """Export a manual recording from Frigate. Runs in a background thread."""
        self._execute_export(
            session=session,
            manager=self.manual_session_manager,
            label="manual session",
        )

    def _run_api(self, host: str, port: int):
        """Run the Flask API server. Called in a background thread."""
        # Suppress Flask/Werkzeug startup banner and request logs
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.WARNING)

        app.run(host=host, port=port, debug=False, use_reloader=False)

    def _signal_handler(self, signum, frame):
        """Handle SIGTERM/SIGINT for graceful shutdown."""
        sig_name = signal.Signals(signum).name
        logger.info("Received %s, shutting down...", sig_name)
        self.stop()

    def stop(self):
        """Graceful shutdown: abort active session, stop recording, disconnect."""
        self._running = False
        self._shutdown_event.set()

        # Stop storage monitor
        self.storage_monitor.stop()

        # Stop recording watchdog
        self.watchdog.stop()

        # Abort active sessions if any
        if self.session_manager.has_active_sessions:
            logger.warning("Aborting active sessions due to shutdown")
            active_chambers = list(self.session_manager.active_sessions.keys())
            for chamber_id in active_chambers:
                session = self.session_manager.abort_session(chamber_id, reason="daemon shutdown")
                if session:
                    # Try to stop recording for the aborted session's camera
                    self.frigate.set_recording(session.camera, enabled=False)

        # Stop all recording (safety net)
        logger.info("Stopping all camera recordings...")
        self.frigate.stop_all_recording()

        # Disconnect MQTT
        logger.info("Disconnecting MQTT...")
        self.frigate.disconnect_mqtt()

        logger.info("Session Daemon stopped")


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="NeuroSurveillance Session Daemon"
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to config.yaml (default: {DEFAULT_CONFIG_PATH})",
    )
    args = parser.parse_args()

    # Load config first (before logging, since config defines log settings)
    # Use basic logging until config is loaded
    logging.basicConfig(level=logging.INFO)
    config = load_config(args.config)

    # Set up proper logging from config
    setup_logging(config)

    # Create and start daemon
    daemon = SessionDaemon(config)
    try:
        daemon.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        daemon.stop()
    except Exception as e:
        logger.critical("Daemon crashed: %s", e, exc_info=True)
        daemon.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Watchdog that detects stalled Frigate recordings on active cameras.

Polls Frigate's SQLite recordings table every POLL_INTERVAL seconds. For each
camera with an active manual or Radiens session, checks how recently a segment
was written. If lag exceeds STALL_THRESHOLD, emits an alert (log + MQTT) and
remembers that the camera is in alarm so we don't spam.

See vault: 02-procedures/installation/recording-health-watchdog.md
"""

import json
import logging
import sqlite3
import threading
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)

POLL_INTERVAL = 30.0          # seconds between checks
STALL_THRESHOLD = 60.0        # seconds — lag above this triggers alert
START_GRACE = 30.0            # seconds after recording starts where no alert fires
                              #   (Frigate needs to write at least one segment)


class RecordingWatchdog:
    """Background thread that alerts when Frigate stops writing segments
    for a camera that should be recording.

    Args:
        frigate_db_path: Path to Frigate's SQLite database on the host.
        active_cameras_provider: Callable returning {camera_id: started_at_unix}.
            Empty dict means nothing is being recorded.
        mqtt_publish: Callable (topic, payload_str) -> None. Used to publish
            alerts. May be None to disable MQTT alerts.
    """

    def __init__(
        self,
        frigate_db_path: str,
        active_cameras_provider: Callable[[], dict[str, float]],
        mqtt_publish: Optional[Callable[[str, str], None]] = None,
    ):
        self.db_path = frigate_db_path
        self._active = active_cameras_provider
        self._publish = mqtt_publish
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._alerted: set[str] = set()
        self._lag_lock = threading.Lock()
        self._lag: dict[str, float] = {}   # camera_id -> seconds since last segment

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="recording-watchdog",
        )
        self._thread.start()
        logger.info(
            "Recording watchdog started (poll=%.0fs, threshold=%.0fs, db=%s)",
            POLL_INTERVAL, STALL_THRESHOLD, self.db_path,
        )

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5.0)

    def get_lag_snapshot(self) -> dict[str, float]:
        """Return current per-camera lag (s). Empty when nothing is recording."""
        with self._lag_lock:
            return dict(self._lag)

    def _loop(self):
        while not self._stop.wait(POLL_INTERVAL):
            try:
                self._check_once()
            except Exception as e:
                logger.exception("Watchdog tick failed: %s", e)

    def _check_once(self):
        active = self._active()
        if not active:
            if self._alerted:
                self._alerted.clear()
            with self._lag_lock:
                self._lag.clear()
            return

        now = time.time()
        cameras = list(active.keys())

        try:
            conn = sqlite3.connect(self.db_path, timeout=2.0)
            try:
                placeholders = ",".join("?" * len(cameras))
                rows = conn.execute(
                    f"SELECT camera, MAX(end_time) FROM recordings "
                    f"WHERE camera IN ({placeholders}) GROUP BY camera",
                    cameras,
                ).fetchall()
            finally:
                conn.close()
        except sqlite3.OperationalError as e:
            logger.warning("Watchdog DB read failed (will retry): %s", e)
            return

        last_seen = {cam: ts for cam, ts in rows if ts is not None}
        new_lag: dict[str, float] = {}

        for cam, started_at in active.items():
            if (now - started_at) < START_GRACE:
                new_lag[cam] = 0.0
                continue

            last_ts = last_seen.get(cam)
            if last_ts is None:
                lag = now - started_at
            else:
                lag = now - last_ts
            new_lag[cam] = lag

            if lag > STALL_THRESHOLD:
                if cam not in self._alerted:
                    self._alerted.add(cam)
                    self._emit_alert(cam, lag, last_ts)
            elif cam in self._alerted:
                self._alerted.discard(cam)
                logger.warning(
                    "Recording recovered on %s (lag now %.0fs)", cam, lag,
                )

        with self._lag_lock:
            self._lag = new_lag

    def _emit_alert(self, camera: str, lag: float, last_ts: Optional[float]):
        msg = (
            f"Recording STALLED on {camera}: lag={lag:.0f}s "
            f"({'no segments since recording started' if last_ts is None else 'last segment present'})"
        )
        logger.error(msg)
        if self._publish is None:
            return
        payload = json.dumps({
            "camera": camera,
            "lag_seconds": round(lag, 1),
            "last_segment_ts": last_ts,
            "ts": time.time(),
        })
        try:
            self._publish(f"neurosurveillance/watchdog/{camera}/stall", payload)
        except Exception as e:
            logger.error("Failed to publish watchdog alert: %s", e)

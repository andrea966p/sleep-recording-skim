"""
Frigate Controller - Controls Frigate NVR recording via MQTT and exports via HTTP.

Handles two operations:
1. Recording toggle: Publish ON/OFF to frigate/<camera>/recordings/set via MQTT
2. Video export: POST to Frigate HTTP API to create named MP4 clips

IMPORTANT: record.enabled must be true in Frigate config.yml for MQTT toggle
to work. If disabled in config, MQTT/UI toggle has no effect.
"""

import json
import logging
import re
import threading
import time
from typing import Callable, Optional

import paho.mqtt.client as mqtt
import requests

logger = logging.getLogger(__name__)

# Frigate export status polling.
# The wait is progress-driven: as long as Frigate reports the export as
# in_progress=True, we keep waiting. STALL_TIMEOUT only kicks in if Frigate
# stops responding or the export disappears from the list. MAX_TIMEOUT is
# a safety ceiling to prevent indefinite hangs.
EXPORT_POLL_INTERVAL = 5.0    # seconds between export status checks
EXPORT_STALL_TIMEOUT = 600.0  # 10 min grace if Frigate unreachable / export vanishes
EXPORT_MAX_TIMEOUT = 86400.0  # 24h hard ceiling (safety net)

# External recording state callback defer.
# On Frigate restart, Mosquitto republishes retained recordings/state topics
# BEFORE the frigate/available=online message arrives. If the daemon acted on
# state immediately, retained ON values would fire phantom ManualSessions
# before the availability handler could re-arm the grace window. We defer
# every external state callback by STATE_DEFER_SECONDS so an availability
# online arriving in that window can cancel the pending callbacks.
STATE_DEFER_SECONDS = 1.5


class FrigateController:
    """Controls Frigate recording via MQTT and exports via HTTP API.

    Args:
        mqtt_host: MQTT broker hostname.
        mqtt_port: MQTT broker port.
        frigate_url: Frigate HTTP API base URL (e.g. http://127.0.0.1:5000).
        cameras: Dict mapping chamber numbers to camera IDs.
    """

    def __init__(
        self,
        mqtt_host: str = "127.0.0.1",
        mqtt_port: int = 1883,
        frigate_url: str = "http://127.0.0.1:5000",
        cameras: Optional[dict] = None,
        mqtt_user: Optional[str] = None,
        mqtt_password: Optional[str] = None,
    ):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.frigate_url = frigate_url.rstrip("/")
        self.cameras = cameras or {
            "chamber_0": "pi_cam_0", "chamber_1": "pi_cam_1",
            "chamber_2": "pi_cam_2", "chamber_3": "pi_cam_3",
        }

        self._mqtt_client: Optional[mqtt.Client] = None
        self._mqtt_connected = False

        # External recording state detection:
        # Tracks expected state changes (self-initiated via set_recording)
        # so we can distinguish them from external changes (Frigate UI clicks).
        self._expected_states: dict[str, str] = {}  # camera_id -> "ON"/"OFF"
        self._expected_lock = threading.Lock()

        # Last known recording state per camera — used to detect actual
        # transitions (ON->OFF, OFF->ON) and ignore repeated state messages
        # (e.g. Frigate reasserting ON from config.yml record.enabled=true).
        # _last_known_state_lock guards reads/writes — MQTT thread mutates;
        # availability-grace path may also drain via clear_last_known_state().
        self._last_known_state: dict[str, str] = {}  # camera_id -> "ON"/"OFF"
        self._last_known_state_lock = threading.Lock()

        # Frigate availability tracking (frigate/available LWT topic).
        # The first retained "online" we receive on (re)subscribe is NOT a
        # restart event — _initial_available_seen guards against spurious grace.
        self._frigate_online_state: Optional[str] = None
        self._initial_available_seen: bool = False
        self._frigate_online_lock = threading.Lock()

        # Pending state-callback Timers keyed by camera_id. Adding to or
        # cancelling from this dict is guarded by _pending_state_lock.
        self._pending_state_actions: dict[str, threading.Timer] = {}
        self._pending_state_lock = threading.Lock()

        # Callback for external recording state changes: fn(camera_id, state_str)
        self._on_external_recording_change: Optional[
            Callable[[str, str], None]
        ] = None

        # Callback for Frigate availability transitions:
        #   fn(current_payload: str, previous_payload: Optional[str])
        # Fired on any "online" payload received AFTER the initial retained
        # message on subscribe (i.e. genuine Frigate restart / reconnect).
        self._on_frigate_available: Optional[
            Callable[[str, Optional[str]], None]
        ] = None

    def clear_expected_states(self):
        """Clear expected state transitions safely."""
        with self._expected_lock:
            self._expected_states.clear()

    def clear_last_known_state(self):
        """Clear cached last-known state for all cameras safely."""
        with self._last_known_state_lock:
            self._last_known_state.clear()

    def cancel_pending_state_actions(self) -> list[str]:
        """Cancel every deferred external-state callback in flight.

        Called from the availability handler and from the daemon's restart
        grace path so a Frigate-restart retained ``ON`` republish cannot
        graduate into a phantom ManualSession.

        Returns the camera IDs whose pending callbacks were cancelled.
        """
        with self._pending_state_lock:
            cancelled = list(self._pending_state_actions.keys())
            for timer in self._pending_state_actions.values():
                timer.cancel()
            self._pending_state_actions.clear()
        if cancelled:
            logger.info(
                "Cancelled deferred state callbacks for cameras: %s",
                ", ".join(cancelled),
            )
        return cancelled

    def connect_mqtt(self) -> bool:
        """Connect to the MQTT broker. Returns True if successful."""
        try:
            self._mqtt_client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id="neurosurveillance-session-daemon",
            )
            if self.mqtt_user:
                self._mqtt_client.username_pw_set(
                    self.mqtt_user, self.mqtt_password
                )
            self._mqtt_client.on_connect = self._on_connect
            self._mqtt_client.on_disconnect = self._on_disconnect
            self._mqtt_client.on_message = self._on_message
            self._mqtt_client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)
            self._mqtt_client.loop_start()

            # Wait briefly for connection callback
            deadline = time.time() + 5.0
            while not self._mqtt_connected and time.time() < deadline:
                time.sleep(0.1)

            if not self._mqtt_connected:
                logger.error("MQTT connection timed out after 5s")
                return False

            return True

        except Exception as e:
            logger.error("Failed to connect to MQTT broker: %s", e)
            return False

    def disconnect_mqtt(self):
        """Disconnect from the MQTT broker."""
        if self._mqtt_client:
            try:
                self._mqtt_client.loop_stop()
                self._mqtt_client.disconnect()
            except Exception as e:
                logger.warning("Error disconnecting MQTT: %s", e)
            finally:
                self._mqtt_connected = False

    def register_external_recording_callback(
        self, callback: Optional[Callable[[str, str], None]]
    ):
        """Register a callback for external recording state changes.

        The callback receives (camera_id: str, state: str) where state is
        "ON" or "OFF". It is called when a recording state change is detected
        that was NOT initiated by this daemon's set_recording() method.

        Pass ``None`` to suppress external-change notifications (e.g. during
        a startup or restart grace period).

        Args:
            callback: Function to call on external state changes, or None.
        """
        self._on_external_recording_change = callback
        if callback is None:
            logger.info("External recording change callback cleared")
        else:
            logger.info("External recording change callback registered")

    def register_frigate_availability_callback(
        self, callback: Optional[Callable[[str, Optional[str]], None]]
    ):
        """Register a callback for Frigate availability transitions.

        The callback receives (current_payload: str, previous_payload: Optional[str])
        whenever a non-initial message arrives on ``frigate/available``. The
        primary use is to re-arm the startup grace period when Frigate restarts
        while the daemon stays up — Frigate then republishes its retained
        ``state`` topic, which would otherwise look like an external user
        click and spawn a phantom ManualSession.

        Args:
            callback: Function to call on availability messages, or None to
                clear an existing registration.
        """
        self._on_frigate_available = callback
        if callback is None:
            logger.info("Frigate availability callback cleared")
        else:
            logger.info("Frigate availability callback registered")

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self._mqtt_connected = True
            logger.info("Connected to MQTT broker at %s:%d", self.mqtt_host, self.mqtt_port)
            # Reset initial-availability guard on every (re)subscribe so that
            # the first retained value Mosquitto delivers is treated as a
            # baseline read, not a Frigate restart event.
            with self._frigate_online_lock:
                self._initial_available_seen = False
            # Subscribe to recording state topics for external change detection.
            client.subscribe("frigate/+/recordings/state", qos=1)
            # Subscribe to Frigate availability (LWT) so we can detect a
            # Frigate-only restart and re-arm the recording-state grace window.
            client.subscribe("frigate/available", qos=1)
            logger.info(
                "Subscribed to frigate/+/recordings/state and frigate/available",
            )
        else:
            logger.error("MQTT connection failed with code: %s", reason_code)

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages (recording state + availability)."""
        topic = msg.topic
        payload = msg.payload.decode("utf-8", errors="replace").strip()

        # Branch on topic: availability LWT vs per-camera recording state.
        if topic == "frigate/available":
            self._handle_availability_message(payload)
            return

        # Parse camera ID from topic: frigate/{camera_id}/recordings/state
        match = re.match(r"^frigate/([^/]+)/recordings/state$", topic)
        if not match:
            return

        camera_id = match.group(1)

        # Check if this state change was self-initiated
        with self._expected_lock:
            expected = self._expected_states.pop(camera_id, None)

        if expected is not None and expected == payload:
            # This is the echo of our own set_recording() call — consume it
            with self._last_known_state_lock:
                self._last_known_state[camera_id] = payload
            logger.debug(
                "Consumed self-initiated state echo: %s -> %s",
                camera_id, payload,
            )
            return

        # Atomically read the previous value and write the new one so that
        # two near-simultaneous messages can't both observe the same `prev`.
        with self._last_known_state_lock:
            prev = self._last_known_state.get(camera_id)
            self._last_known_state[camera_id] = payload

        # Ignore if this is NOT an actual transition (same state repeated).
        # This filters out Frigate reasserting ON from config record.enabled=true.
        if prev == payload:
            logger.debug(
                "Ignoring repeated state (no transition): %s -> %s",
                camera_id, payload,
            )
            return

        # External state transition detected (Frigate UI or other client).
        # Defer the callback by STATE_DEFER_SECONDS so a near-simultaneous
        # frigate/available message (Frigate restart republishing retained
        # state) has a chance to cancel us before we spawn a phantom session.
        logger.info(
            "External recording state change: %s -> %s (was %s) — deferring %.1fs",
            camera_id, payload, prev, STATE_DEFER_SECONDS,
        )
        self._schedule_state_callback(camera_id, payload)

    def _schedule_state_callback(self, camera_id: str, payload: str):
        """Schedule the external-state callback to fire after STATE_DEFER_SECONDS.

        Replaces any previously-pending callback for the same camera, so a
        rapid ON→OFF→ON sequence only acts on the most recent payload.
        """
        def fire():
            # Remove ourselves from the pending dict so a future state change
            # is not falsely "already pending".
            with self._pending_state_lock:
                self._pending_state_actions.pop(camera_id, None)

            callback = self._on_external_recording_change
            if callback is None:
                logger.debug(
                    "Deferred state callback for %s (%s) suppressed — "
                    "callback cleared (likely Frigate restart grace)",
                    camera_id, payload,
                )
                return
            try:
                callback(camera_id, payload)
            except Exception as e:
                logger.error(
                    "Error in deferred external recording callback: %s", e,
                    exc_info=True,
                )

        with self._pending_state_lock:
            existing = self._pending_state_actions.pop(camera_id, None)
            if existing is not None:
                existing.cancel()
            timer = threading.Timer(STATE_DEFER_SECONDS, fire)
            timer.daemon = True
            self._pending_state_actions[camera_id] = timer
            timer.start()

    def _handle_availability_message(self, payload: str):
        """Process a message on ``frigate/available``.

        Frigate publishes ``online`` on connect and Mosquitto publishes the
        retained ``offline`` LWT when Frigate's MQTT session dies. The first
        retained payload we receive after subscribing is a baseline read,
        not a real transition — we record it but do not fire the callback.
        Every subsequent ``online`` payload indicates Frigate has (re)connected
        and any retained recording-state messages it republishes need to be
        absorbed by a grace window, not treated as external user clicks.
        """
        with self._frigate_online_lock:
            prev = self._frigate_online_state
            self._frigate_online_state = payload
            is_initial = not self._initial_available_seen
            self._initial_available_seen = True

        logger.info(
            "Frigate availability: %s (prev=%s, initial=%s)",
            payload, prev, is_initial,
        )

        if is_initial:
            # First message after subscribe — retained value, not a transition.
            return

        # Only fire on "online". An "offline" payload by itself is not
        # actionable (we cannot pre-emptively do anything); the grace window
        # is what matters and that runs when Frigate comes back.
        if payload != "online":
            return

        # Cancel any pending state-change callbacks RIGHT NOW. The retained
        # recordings/state messages from the (re)connecting Frigate are
        # already in flight via _schedule_state_callback — letting them fire
        # would create phantom ManualSessions before the daemon's grace
        # handler can clear the callback. Belt-and-suspenders with the
        # grace handler's own cancel.
        self.cancel_pending_state_actions()

        if self._on_frigate_available:
            try:
                self._on_frigate_available(payload, prev)
            except Exception as e:
                logger.error(
                    "Error in Frigate availability callback: %s", e,
                    exc_info=True,
                )

    def _on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        self._mqtt_connected = False
        if reason_code != 0:
            logger.warning("Unexpected MQTT disconnect (code: %s), will auto-reconnect", reason_code)

    def get_camera_id(self, chamber: int) -> str:
        """Get camera ID for a chamber number."""
        key = f"chamber_{chamber}"
        camera = self.cameras.get(key)
        if camera is None:
            raise ValueError(f"No camera configured for chamber {chamber} (key: {key})")
        return camera

    def set_recording(self, camera_id: str, enabled: bool) -> bool:
        """Toggle recording for a camera via MQTT.

        Args:
            camera_id: Frigate camera name (e.g. 'pi_cam_0').
            enabled: True to start recording, False to stop.

        Returns:
            True if the MQTT message was published successfully.
        """
        if not self._mqtt_connected or self._mqtt_client is None:
            logger.error("Cannot set recording: MQTT not connected")
            return False

        topic = f"frigate/{camera_id}/recordings/set"
        payload = "ON" if enabled else "OFF"

        # Record expected state BEFORE publishing so the echo is consumed
        with self._expected_lock:
            self._expected_states[camera_id] = payload

        try:
            result = self._mqtt_client.publish(topic, payload, qos=1)
            result.wait_for_publish(timeout=5.0)
            logger.info("Published %s to %s", payload, topic)
            return True
        except Exception as e:
            logger.error("Failed to publish MQTT message: %s", e)
            return False

    def stop_all_recording(self) -> bool:
        """Stop recording on all cameras. Used at daemon startup for clean slate."""
        success = True
        for key, camera_id in self.cameras.items():
            if not self.set_recording(camera_id, enabled=False):
                logger.error("Failed to stop recording for %s (%s)", key, camera_id)
                success = False
        return success

    def export_recording(
        self,
        camera_id: str,
        start_time: float,
        end_time: float,
        name: str = "",
    ) -> Optional[str]:
        """Export a recording clip from Frigate.

        Args:
            camera_id: Frigate camera name.
            start_time: Start timestamp (Unix epoch, UTC).
            end_time: End timestamp (Unix epoch, UTC).
            name: Export name (used by Frigate for the clip label).

        Returns:
            Export ID if successful, None on failure.
        """
        # Frigate export API expects integer timestamps
        start_ts = int(start_time)
        end_ts = int(end_time)

        url = f"{self.frigate_url}/api/export/{camera_id}/start/{start_ts}/end/{end_ts}"

        # Frigate v0.16+ requires a JSON body with at least a "name" field
        export_name = name or f"{camera_id}_{start_ts}"
        body = {"name": export_name}

        try:
            logger.info(
                "Requesting Frigate export: camera=%s, start=%d, end=%d (duration=%ds)",
                camera_id, start_ts, end_ts, end_ts - start_ts,
            )
            response = requests.post(url, json=body, timeout=30)
            response.raise_for_status()

            data = response.json()
            export_id = data.get("export_id") or data.get("id") or data.get("name")
            logger.info("Frigate export started: %s", export_id)
            return export_id

        except requests.exceptions.ConnectionError:
            logger.error("Cannot reach Frigate at %s", self.frigate_url)
            return None
        except requests.exceptions.HTTPError as e:
            logger.error("Frigate export API error: %s (response: %s)", e, e.response.text)
            return None
        except Exception as e:
            logger.error("Frigate export failed: %s", e)
            return None

    def wait_for_export(self, export_id: str) -> Optional[dict]:
        """Poll Frigate until the export completes, stalls, or hits the ceiling.

        Wait semantics:
          - As long as Frigate reports the export with in_progress=True, keep
            waiting. There is no per-recording timeout.
          - If Frigate becomes unreachable OR the export disappears from the
            list, allow EXPORT_STALL_TIMEOUT of grace before giving up.
          - EXPORT_MAX_TIMEOUT is a hard ceiling (default 24h) that should
            never be hit during normal operation.

        Args:
            export_id: The export ID returned by export_recording().

        Returns:
            Export metadata dict if completed, None on stall/ceiling/error.
        """
        url = f"{self.frigate_url}/api/exports"
        started = time.time()
        last_progress = started   # last time we confirmed in_progress=True
        logger.info("Waiting for export %s to complete...", export_id)

        while time.time() - started < EXPORT_MAX_TIMEOUT:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                exports = response.json()

                found = False
                for export in exports:
                    eid = export.get("id") or export.get("name")
                    if eid != export_id:
                        continue
                    found = True
                    if export.get("in_progress", False):
                        last_progress = time.time()
                        break
                    elapsed = time.time() - started
                    logger.info(
                        "Export %s completed after %.0fs", export_id, elapsed,
                    )
                    return export

                if not found:
                    # Export not (yet) in list — could be initializing, or
                    # finished+cleaned. Allow stall grace before giving up.
                    stalled_for = time.time() - last_progress
                    if stalled_for > EXPORT_STALL_TIMEOUT:
                        logger.error(
                            "Export %s vanished from Frigate's list for %.0fs",
                            export_id, stalled_for,
                        )
                        return None

                time.sleep(EXPORT_POLL_INTERVAL)

            except Exception as e:
                stalled_for = time.time() - last_progress
                logger.warning(
                    "Error checking export status (%.0fs since progress): %s",
                    stalled_for, e,
                )
                if stalled_for > EXPORT_STALL_TIMEOUT:
                    logger.error(
                        "Lost contact with Frigate for %.0fs while waiting for %s",
                        stalled_for, export_id,
                    )
                    return None
                time.sleep(EXPORT_POLL_INTERVAL)

        logger.error(
            "Export %s exceeded max wait of %.0fs",
            export_id, EXPORT_MAX_TIMEOUT,
        )
        return None

    def check_frigate_health(self) -> bool:
        """Check if Frigate is reachable."""
        try:
            response = requests.get(f"{self.frigate_url}/api/stats", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def publish(self, topic: str, payload: str, qos: int = 1) -> bool:
        """Publish an arbitrary message to MQTT. No-op if not connected."""
        if not self._mqtt_connected or self._mqtt_client is None:
            return False
        try:
            self._mqtt_client.publish(topic, payload, qos=qos)
            return True
        except Exception as e:
            logger.warning("MQTT publish to %s failed: %s", topic, e)
            return False

    @property
    def mqtt_connected(self) -> bool:
        return self._mqtt_connected

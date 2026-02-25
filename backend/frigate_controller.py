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

# Frigate export status polling
EXPORT_POLL_INTERVAL = 2.0   # seconds between export status checks
EXPORT_TIMEOUT = 300.0       # 5 minutes max wait for export


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
    ):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.frigate_url = frigate_url.rstrip("/")
        self.cameras = cameras or {"chamber_0": "pi_cam_0", "chamber_1": "pi_cam_1"}

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
        self._last_known_state: dict[str, str] = {}  # camera_id -> "ON"/"OFF"

        # Callback for external recording state changes: fn(camera_id, state_str)
        self._on_external_recording_change: Optional[
            Callable[[str, str], None]
        ] = None

    def connect_mqtt(self) -> bool:
        """Connect to the MQTT broker. Returns True if successful."""
        try:
            self._mqtt_client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id="neurosurveillance-session-daemon",
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
        self, callback: Callable[[str, str], None]
    ):
        """Register a callback for external recording state changes.

        The callback receives (camera_id: str, state: str) where state is
        "ON" or "OFF". It is called when a recording state change is detected
        that was NOT initiated by this daemon's set_recording() method.

        Args:
            callback: Function to call on external state changes.
        """
        self._on_external_recording_change = callback
        logger.info("External recording change callback registered")

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self._mqtt_connected = True
            logger.info("Connected to MQTT broker at %s:%d", self.mqtt_host, self.mqtt_port)
            # Subscribe to recording state topics for external change detection
            client.subscribe("frigate/+/recordings/state", qos=1)
            logger.info("Subscribed to frigate/+/recordings/state")
        else:
            logger.error("MQTT connection failed with code: %s", reason_code)

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages (recording state updates)."""
        topic = msg.topic
        payload = msg.payload.decode("utf-8", errors="replace").strip()

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
            self._last_known_state[camera_id] = payload
            logger.debug(
                "Consumed self-initiated state echo: %s -> %s",
                camera_id, payload,
            )
            return

        # Ignore if this is NOT an actual transition (same state repeated).
        # This filters out Frigate reasserting ON from config record.enabled=true.
        prev = self._last_known_state.get(camera_id)
        self._last_known_state[camera_id] = payload
        if prev == payload:
            logger.debug(
                "Ignoring repeated state (no transition): %s -> %s",
                camera_id, payload,
            )
            return

        # External state transition detected (Frigate UI or other client)
        logger.info(
            "External recording state change: %s -> %s (was %s)",
            camera_id, payload, prev,
        )

        if self._on_external_recording_change:
            try:
                self._on_external_recording_change(camera_id, payload)
            except Exception as e:
                logger.error(
                    "Error in external recording callback: %s", e,
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
        """Poll Frigate until the export is complete or times out.

        Args:
            export_id: The export ID returned by export_recording().

        Returns:
            Export metadata dict if completed, None on timeout or error.
        """
        url = f"{self.frigate_url}/api/exports"
        deadline = time.time() + EXPORT_TIMEOUT
        logger.info("Waiting for export %s to complete...", export_id)

        while time.time() < deadline:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                exports = response.json()

                # Find our export in the list
                for export in exports:
                    eid = export.get("id") or export.get("name")
                    if eid == export_id:
                        logger.info("Export %s completed", export_id)
                        return export

                # Export not in list yet -- still processing
                time.sleep(EXPORT_POLL_INTERVAL)

            except Exception as e:
                logger.warning("Error checking export status: %s", e)
                time.sleep(EXPORT_POLL_INTERVAL)

        logger.error("Export %s timed out after %ds", export_id, int(EXPORT_TIMEOUT))
        return None

    def check_frigate_health(self) -> bool:
        """Check if Frigate is reachable."""
        try:
            response = requests.get(f"{self.frigate_url}/api/stats", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    @property
    def mqtt_connected(self) -> bool:
        return self._mqtt_connected

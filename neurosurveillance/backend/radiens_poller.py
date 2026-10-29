"""
Radiens Poller - Polls NeuroNexus Radiens for EEG recording state changes.

Detects R_OFF -> R_ON (session start) and R_ON -> R_OFF (session end)
transitions by polling AllegoClient.get_status() at a configurable interval.

The poller only OBSERVES Radiens state. It never starts/stops EEG recording.

2026-10-28: ported from the old `radiens` 4.0.0 client to `radiens-core` 0.1.2
(Allego 4.1.2). The old client cannot even authenticate to Allego 4, and the two
packages cannot be loaded in one process, so nothing here may import `radiens`.
`record_mode` is an IntEnum (`str(RecordMode.ON) == "1"`), so we compare the enum
and map it to this module's own RecordingState values ("R_ON"/"R_OFF"), which the
daemon's API JSON exposes and must not change.

The trigger stays GLOBAL: `recording.record_mode` is ON if ANY port records. With
per-port recording (measured 2026-10-28) the per-port modes are also reported in
`RadiensStatus.port_modes` ({"A": "ON", ...}) for information only.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

# Exponential-backoff bounds for Radiens connection / poll failures.
# The daemon's main loop calls poll() once per `poll_interval` (default 1s).
# When Radiens is down (gRPC UNAVAILABLE), every call hits the wire and the
# radiens client library writes ~2 lines to its own `radiens.log`. With the
# default 1s loop that produced ~3 GB of log spam over a week and obscured
# the 2026-05-22 incident analysis. Backoff caps Radiens attempts at
# BACKOFF_MAX seconds while it's unreachable; the daemon's poll loop still
# ticks for everything else.
BACKOFF_BASE = 1.0      # first retry 1s after a failure
BACKOFF_FACTOR = 2.0
BACKOFF_MAX = 60.0      # cap at 60s between attempts when Radiens is down


class RecordingState(Enum):
    """Radiens recording states."""
    ON = "R_ON"
    OFF = "R_OFF"
    UNKNOWN = "UNKNOWN"


@dataclass
class RadiensStatus:
    """Snapshot of Radiens state from a single poll."""
    recording: RecordingState = RecordingState.UNKNOWN
    stream: str = ""
    base_name: str = ""
    file_path: str = ""
    connected: bool = False
    error: Optional[str] = None
    # Added 2026-10-28: per-port record modes by letter, "ON"/"OFF". Only ports the
    # server reports are present. Informational: the trigger is the global state.
    port_modes: Dict[str, str] = field(default_factory=dict)
    poll_time: float = field(default_factory=time.time)


class RadiensPoller:
    """Polls Radiens AllegoClient for recording state transitions.

    Args:
        poll_interval: Seconds between polls (default 1.0).
        on_session_start: Callback when R_OFF -> R_ON detected.
        on_session_end: Callback when R_ON -> R_OFF detected.
    """

    def __init__(
        self,
        poll_interval: float = 1.0,
        on_session_start: Optional[Callable[[RadiensStatus], None]] = None,
        on_session_end: Optional[Callable[[RadiensStatus], None]] = None,
    ):
        self.poll_interval = poll_interval
        self.on_session_start = on_session_start
        self.on_session_end = on_session_end

        self._client = None
        self._previous_state = RecordingState.UNKNOWN
        self._connected = False
        self._consecutive_errors = 0
        self._max_silent_errors = 5  # Log every Nth consecutive error

        # Exponential backoff state for connect/poll failures.
        self._next_attempt_at = 0.0
        self._backoff = BACKOFF_BASE

    def _on_success(self) -> None:
        """Reset backoff state after a successful Radiens call."""
        self._consecutive_errors = 0
        self._next_attempt_at = 0.0
        self._backoff = BACKOFF_BASE

    def _on_failure(self, now: float) -> None:
        """Advance backoff state after a Radiens call failed."""
        self._next_attempt_at = now + self._backoff
        self._backoff = min(self._backoff * BACKOFF_FACTOR, BACKOFF_MAX)

    def connect(self) -> bool:
        """Connect to Radiens. Returns True if successful.

        Honors the exponential backoff window: if the previous attempt failed
        recently, returns False without hitting the wire until
        `_next_attempt_at` has elapsed.
        """
        now = time.time()
        if now < self._next_attempt_at:
            return False
        try:
            from radiens_core import AllegoClient
            self._client = AllegoClient()
            # Test the connection with a status poll
            status = self._client.get_status()
            self._connected = True
            self._on_success()
            logger.info(
                "Connected to Radiens (recording: %s)",
                status.recording.record_mode.name,
            )
            return True
        except ImportError:
            logger.error(
                "radiens_core package not installed. "
                "Install radiens-core==0.1.2 into the daemon venv."
            )
            self._connected = False
            # No retry — module is structurally missing
            self._next_attempt_at = float("inf")
            return False
        except Exception as e:
            self._consecutive_errors += 1
            self._connected = False
            self._on_failure(now)
            if (
                self._consecutive_errors == 1
                or self._consecutive_errors % self._max_silent_errors == 0
            ):
                logger.warning(
                    "Radiens connect failed (%d consecutive, next attempt in %.0fs): %s",
                    self._consecutive_errors,
                    max(0.0, self._next_attempt_at - now),
                    e,
                )
            return False

    def poll(self) -> RadiensStatus:
        """Poll Radiens once and return current status.

        Detects state transitions and fires callbacks.
        If Radiens is unreachable, returns a status with connected=False
        and does NOT change internal state (fail-safe).

        Honors the backoff window: while backing off, returns immediately
        without calling get_status() (avoids gRPC log spam).
        """
        if self._client is None:
            return RadiensStatus(
                connected=False,
                error="Not connected (call connect() first)",
            )

        now = time.time()
        if now < self._next_attempt_at:
            return RadiensStatus(
                connected=False,
                error="Radiens backoff in effect",
            )

        try:
            allego_status = self._client.get_status()
            self._connected = True
            self._on_success()

            # Parse recording state. record_mode is a RecordMode IntEnum; compare the
            # NAME, never str() (str(RecordMode.ON) is "1"). Global: ON if any port records.
            rec = allego_status.recording
            mode_name = getattr(getattr(rec, "record_mode", None), "name", None)
            if mode_name == "ON":
                current_state = RecordingState.ON
            elif mode_name == "OFF":
                current_state = RecordingState.OFF
            else:
                current_state = RecordingState.UNKNOWN
                logger.warning("Unexpected recording state: %r", mode_name)

            # Per-port modes (None = not reported by the server).
            port_modes: Dict[str, str] = {}
            for letter in "abcdefgh":
                pm = getattr(rec, "record_mode_port_" + letter, None)
                if pm is not None:
                    port_modes[letter.upper()] = pm.name

            # Base name and directory live in the recording config, not in the status.
            # A failure here must not fail the poll: the state is what matters.
            base_name = ""
            file_path = ""
            try:
                cfg = self._client.get_recording_config()
                base_name = str(cfg.base_file_name)
                file_path = str(cfg.base_file_path)
            except Exception as cfg_err:
                logger.debug("get_recording_config failed: %s", cfg_err)
                base_name = str(getattr(rec, "active_filename", ""))

            status = RadiensStatus(
                recording=current_state,
                stream=getattr(getattr(allego_status.streaming, "stream_mode", None), "name", ""),
                base_name=base_name,
                file_path=file_path,
                connected=True,
                port_modes=port_modes,
            )

            # Detect transitions
            if (
                self._previous_state == RecordingState.OFF
                and current_state == RecordingState.ON
            ):
                logger.info(
                    "Recording STARTED (R_OFF -> R_ON), base_name=%s",
                    status.base_name,
                )
                if self.on_session_start:
                    self.on_session_start(status)

            elif (
                self._previous_state == RecordingState.ON
                and current_state == RecordingState.OFF
            ):
                logger.info("Recording STOPPED (R_ON -> R_OFF)")
                if self.on_session_end:
                    self.on_session_end(status)

            # On first successful poll, just record the state without
            # firing transitions (we don't know the "previous" state yet)
            if self._previous_state == RecordingState.UNKNOWN:
                logger.info("Initial Radiens state: %s", current_state.value)

            self._previous_state = current_state
            return status

        except Exception as e:
            self._consecutive_errors += 1
            self._connected = False
            self._on_failure(now)

            # Avoid log spam: log first error, then every Nth
            if (
                self._consecutive_errors == 1
                or self._consecutive_errors % self._max_silent_errors == 0
            ):
                logger.warning(
                    "Radiens poll failed (%d consecutive, next attempt in %.0fs): %s",
                    self._consecutive_errors,
                    max(0.0, self._next_attempt_at - now),
                    e,
                )

            # Do NOT change _previous_state on error (fail-safe)
            return RadiensStatus(
                connected=False,
                error=str(e),
            )

    @property
    def connected(self) -> bool:
        """Whether the last poll was successful."""
        return self._connected

    @property
    def previous_state(self) -> RecordingState:
        """The last known recording state."""
        return self._previous_state

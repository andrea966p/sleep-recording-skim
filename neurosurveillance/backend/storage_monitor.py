# =====================================================================
# RECOVERED FILE — best-effort reconstruction (2026-04-29)
#
# Originals were deleted in a Syncthing accident. This reconstruction is
# a merge of:
#   - first ~50 lines from a Claude Code transcript partial Read (clean)
#   - lines 51..end from pycdc decompiling __pycache__/storage_monitor.cpython-312.pyc
#
# THREE METHODS BELOW ARE INCOMPLETE because pycdc hit unsupported
# Python 3.12 opcodes. They are marked with TODO. Reconstruct them
# using the bytecode disassembly at:
#   /home/andrea/neurosurveillance-recovery/pyc_decompiled/storage_monitor.disassembly.txt
#
# Incomplete methods:
#   - get_status()              (returns cached status, with default skeleton if no cache)
#   - can_start_recording()     (checks disk space against eeg_reserve_bytes)
#   - fetch_camera_bitrates()   (queries go2rtc APIs for per-camera bitrates)
#
# Also clean up these pycdc artifacts when reviewing:
#   - method signatures with `self = None, x = None` should be `self, x`
#   - `import urllib.request as urllib` should be `import urllib.request`
#   - `_poll_loop` has odd `continue` / `return None` placement (the
#     "while not self._stop_event.is_set(): refresh(); wait()" pattern)
#   - the dict-build inside refresh() got mangled mid-way
# =====================================================================
"""
Storage monitoring for the NeuroSurveillance daemon.

Periodically samples disk usage via os.statvfs (single syscall, ~0ms)
and categorizes storage by directory. The cache is replaced atomically
so the API thread never reads partial data.
"""

import logging
import os
import re
import threading
import time
import urllib.request
import json as json_mod

logger = logging.getLogger(__name__)


class StorageMonitor:
    """Monitors disk usage and enforces EEG/EMG storage reservation."""

    def __init__(self, config: dict):
        self._config = config  # Full config (needed by fetch_camera_bitrates)
        storage_cfg = config.get("storage", {})

        self.poll_interval = storage_cfg.get("poll_interval", 30)
        self.paths = storage_cfg.get("paths", {})
        self.eeg_reserve_bytes = storage_cfg.get("eeg_reserve_gb", 200) * (1024 ** 3)
        self.warn_percent = storage_cfg.get("warn_percent", 75)
        self.critical_percent = storage_cfg.get("critical_percent", 90)
        self.camera_bitrate_mbps = storage_cfg.get("camera_bitrate_mbps", 1.5)

        # Cache: replaced atomically (dict reference swap)
        self._cache: dict | None = None
        self._category_cache: dict = {}
        self._category_cache_time: float = 0.0
        self._category_ttl: float = 300.0  # 5 minutes

        # Background thread
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Background polling (disk usage)
    # ------------------------------------------------------------------

    def start(self):
        """Start the background polling thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="storage-monitor"
        )
        self._thread.start()
        logger.info(
            "Storage monitor started: poll=%ds, reserve=%d GB, warn=%d%%, crit=%d%%",
            self.poll_interval,
            self.eeg_reserve_bytes // (1024 ** 3),
            self.warn_percent,
            self.critical_percent,
        )

    def stop(self):
        """Stop the background polling thread."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Storage monitor stopped")

    def _poll_loop(self):
        """Background loop: refresh cache every poll_interval seconds."""
        # NOTE: pycdc mis-rendered the loop. Standard pattern below.
        while not self._stop_event.is_set():
            self.refresh()
            self._stop_event.wait(timeout=self.poll_interval)

    def refresh(self):
        """Sample disk usage and update the cache."""
        try:
            stat = os.statvfs("/")
            total_bytes = stat.f_frsize * stat.f_blocks
            available_bytes = stat.f_frsize * stat.f_bavail
            used_bytes = total_bytes - stat.f_frsize * stat.f_bfree
            used_percent = (
                round((used_bytes / total_bytes) * 100, 1) if total_bytes > 0 else 0
            )

            now = time.time()
            if now - self._category_cache_time > self._category_ttl:
                categories = {}
                for name, path in self.paths.items():
                    size = self._get_dir_size(path)
                    categories[name] = {"path": path, "bytes": size}
                self._category_cache = categories
                self._category_cache_time = now
            categories = self._category_cache

            effective_available = max(0, available_bytes - self.eeg_reserve_bytes)
            can_record = available_bytes > self.eeg_reserve_bytes

            # NOTE: pycdc inverted this condition; reconstructed canonical form:
            if used_percent >= self.critical_percent:
                status_level = "critical"
            elif used_percent >= self.warn_percent:
                status_level = "warn"
            else:
                status_level = "ok"

            self._cache = {
                "total_bytes": total_bytes,
                "used_bytes": used_bytes,
                "available_bytes": available_bytes,
                "used_percent": used_percent,
                "categories": categories,
                "eeg_reserve_bytes": self.eeg_reserve_bytes,
                "effective_available_bytes": effective_available,
                "status_level": status_level,
                "camera_bitrate_mbps": self.camera_bitrate_mbps,
                "can_record": can_record,
                "last_updated": now,
            }
        except Exception:
            logger.exception("Storage monitor refresh failed")

    # ------------------------------------------------------------------
    # Disk-usage helpers
    # ------------------------------------------------------------------

    def _get_dir_size(self, path: str) -> int:
        """Sum file sizes in a directory tree using os.scandir (fast)."""
        total = 0
        if not os.path.isdir(path):
            return 0
        try:
            for entry in os.scandir(path):
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += self._get_dir_size(entry.path)
                except PermissionError:
                    continue
        except PermissionError:
            pass
        return total

    # ------------------------------------------------------------------
    # Public API surface
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Return cached storage status for the API. Instant (no disk I/O)."""
        # TODO: pycdc decompile incomplete — reconstruct from disassembly.
        # Logic per disassembly:
        #   if self._cache is None: self.refresh()
        #   return self._cache or {
        #     'total_bytes': 0, 'used_bytes': 0, 'available_bytes': 0,
        #     'used_percent': 0, 'categories': {},
        #     'eeg_reserve_bytes': self.eeg_reserve_bytes,
        #     'effective_available_bytes': 0, 'status_level': 'ok',
        #     'camera_bitrate_mbps': self.camera_bitrate_mbps,
        #     'can_record': True, 'last_updated': 0,
        #   }
        if self._cache is None:
            self.refresh()
        if self._cache is not None:
            return self._cache
        return {
            "total_bytes": 0,
            "used_bytes": 0,
            "available_bytes": 0,
            "used_percent": 0,
            "categories": {},
            "eeg_reserve_bytes": self.eeg_reserve_bytes,
            "effective_available_bytes": 0,
            "status_level": "ok",
            "camera_bitrate_mbps": self.camera_bitrate_mbps,
            "can_record": True,
            "last_updated": 0,
        }

    def can_start_recording(self, num_cameras: int) -> tuple[bool, str]:
        """Check if a new recording session is allowed.

        Returns:
            (allowed, reason) — reason is empty string if allowed.

        Fail-open: if no cache exists, returns (True, "") to avoid
        silently blocking science.
        """
        # TODO: pycdc decompile incomplete — reconstruct from disassembly.
        # Locals from disassembly: status, available, reserve, avail_gb, reserve_gb.
        # Constants: 'available_bytes', 'eeg_reserve_bytes', 1073741824 (1 GiB),
        # 'Insufficient disk space: ', '.1f', ' GB available, ', '.0f',
        # ' GB reserved for EEG/EMG. Free up space or reduce eeg_reserve_gb in config.'
        status = self._cache
        if status is None:
            return (True, "")
        available = status["available_bytes"]
        reserve = status["eeg_reserve_bytes"]
        if available <= reserve:
            avail_gb = available / (1024 ** 3)
            reserve_gb = reserve / (1024 ** 3)
            return (
                False,
                f"Insufficient disk space: {avail_gb:.1f} GB available, "
                f"{reserve_gb:.0f} GB reserved for EEG/EMG. "
                f"Free up space or reduce eeg_reserve_gb in config.",
            )
        return (True, "")

    def fetch_camera_bitrates(self) -> dict:
        """Query go2rtc APIs on each Pi to get actual per-camera bitrates.

        Takes two bytes_recv samples 1 second apart (per Pi, in parallel)
        and converts the delta to Mbps. User-triggered endpoint — 1s latency
        is acceptable.

        Returns:
            {
                "camera_bitrates": {"pi_cam_0": 1.73, "pi_cam_1": 1.71, ...},
                "default_mbps": 1.7,
                "source": "go2rtc" | "default",
                "errors": ["http://192.168.0.12:1984: Connection refused"]
            }
        """
        go2rtc_apis = self._config.get("storage", {}).get("go2rtc_apis", [])
        default_mbps = self.camera_bitrate_mbps
        camera_bitrates: dict[str, float] = {}
        errors: list[str] = []

        lock = threading.Lock()

        def sample_pi(base: str) -> None:
            url = f"{base.rstrip('/')}/api/streams"
            try:
                def fetch() -> dict:
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=2) as resp:
                        return json_mod.loads(resp.read().decode("utf-8"))

                s1 = fetch()
                time.sleep(1)
                s2 = fetch()

                for name, stream in s1.items():
                    if name not in s2:
                        continue
                    producers1 = stream.get("producers") or []
                    producers2 = (s2[name].get("producers") or [])
                    if not producers1 or not producers2:
                        continue
                    b1 = producers1[0].get("bytes_recv", 0)
                    b2 = producers2[0].get("bytes_recv", 0)
                    if b2 > b1:
                        mbps = round((b2 - b1) * 8 / 1_000_000, 2)
                        with lock:
                            camera_bitrates[name] = mbps
            except Exception as e:
                with lock:
                    errors.append(f"{base}: {e}")

        threads = [threading.Thread(target=sample_pi, args=(base,)) for base in go2rtc_apis]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        return {
            "camera_bitrates": camera_bitrates,
            "default_mbps": default_mbps,
            "source": "go2rtc" if camera_bitrates else "default",
            "errors": errors,
        }

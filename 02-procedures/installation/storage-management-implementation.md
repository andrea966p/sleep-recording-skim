---
tags: [procedure, implementation, storage, monitoring]
created: 2026-04-01
status: draft
---

# Storage Management System — Implementation Guide

## Purpose

Add real-time storage monitoring, a recording calculator, and EEG/EMG disk protection to the NeuroSurveillance system. This prevents video recordings from filling the 1.9 TB NVMe and interrupting critical XDAQ EEG/EMG data.

## What Gets Built

1. **Backend `StorageMonitor`** — background thread that samples disk usage every 30s
2. **Three new API endpoints** — `GET /api/storage`, `GET /api/storage/estimate`, `GET /api/storage/camera-bitrates`
3. **Recording cap enforcement** — blocks new video recordings when available space drops below 200 GB EEG reserve
4. **Storage header badge** — compact percentage indicator in the Tauri app header (always visible)
5. **StoragePanel footer card** — detailed breakdown + inline calculator with **refresh button** that syncs bitrates from go2rtc
6. **Health endpoint augmentation** — storage level piggybacked onto existing `/api/health`

## Architecture Overview

```
OS Kernel (statvfs)
    │  (every 30s, background thread)
    ▼
StorageMonitor._cache (Python dict, atomic swap)
    │  (on API request — instant, reads cache)
    ▼
GET /api/storage → JSON
    │  (every 10s, useStoragePoll hook)
    ▼
StoragePanel (footer) + Header badge (via /api/health every 5s)
```

Category directory scans (`os.scandir` walk) are the slow part — they run in the background thread with a **5-minute TTL**, not on every request.

## Prerequisites

- [x] Working NeuroSurveillance backend (`daemon.py` running) ✅ 2026-04-02
- [x] Working frontend (`npm run dev` or Tauri build) ✅ 2026-04-02
- [x] Access to `/srv/frigate/storage/` and `/opt/neurosurveillance/sessions/` ✅ 2026-04-02

---

## Step 1: Add Storage Config Section

**File:** `neurosurveillance/config/config.yaml`

Add this new top-level section after the existing `nas` section:

```yaml
storage:
  poll_interval: 30                    # How often to re-check disk (seconds)
  paths:
    recordings: "/srv/frigate/storage/recordings"
    exports: "/srv/frigate/storage/exports"
    clips: "/srv/frigate/storage/clips"
    sessions: "/opt/neurosurveillance/sessions"
  eeg_reserve_gb: 200                  # Hard reserve for XDAQ EEG/EMG data
  warn_percent: 75                     # UI turns yellow at this threshold
  critical_percent: 90                 # UI turns red, recordings may be blocked
  camera_bitrate_mbps: 1.5             # Default fallback for the calculator

  # go2rtc API endpoints on each Pi — used by the "Refresh Bitrates" button
  # to auto-detect actual camera bitrates from the running go2rtc config
  go2rtc_apis:
    - "http://192.168.0.11:1984"       # Pi 1 (pi_cam_0, pi_cam_1)
    - "http://192.168.0.12:1984"       # Pi 2 (pi_cam_2, pi_cam_3)
```

> [!tip] Config Values
> - `eeg_reserve_gb: 200` — chosen because XDAQ sessions can generate large `.xdat` files
> - `warn_percent` and `critical_percent` are for UI color coding only; the hard enforcement is `eeg_reserve_gb`
> - `camera_bitrate_mbps: 1.5` is the **default fallback**; the calculator prefers live bitrates fetched from go2rtc when the user clicks the refresh button
> - `go2rtc_apis` — the calculator queries these to read actual `--bitrate` values from the running stream configs

**Validation:**
```bash
# Restart the session daemon
sudo systemctl restart neurosurveillance-session

# Check that it started without config errors
sudo systemctl status neurosurveillance-session

# Tail the logs to verify config loaded cleanly (look for any KeyError or yaml errors)
journalctl -u neurosurveillance-session --since "1 min ago" --no-pager
```
No errors related to the `storage` section should appear. The daemon won't *use* the storage config yet (that comes in Step 4), but it should parse the YAML without crashing.

---

## Step 2: Create `storage_monitor.py`

**New file:** `neurosurveillance/backend/storage_monitor.py`

This is the core backend module. It has no external dependencies beyond Python stdlib.

### 2.1 Class Structure

```python
"""
Storage monitoring for the NeuroSurveillance daemon.

Periodically samples disk usage via os.statvfs (single syscall, ~0ms)
and categorizes storage by directory. The cache is replaced atomically
so the API thread never reads partial data.
"""

import logging
import os
import threading
import time

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

    def start(self):
        """Start the background polling thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="storage-monitor",
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
        # Do an immediate refresh on start
        self.refresh()
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self.poll_interval)
            if not self._stop_event.is_set():
                self.refresh()

    def refresh(self):
        """Sample disk usage and update the cache."""
        try:
            # 1. Filesystem-level stats (instant — single syscall)
            stat = os.statvfs("/")
            total_bytes = stat.f_frsize * stat.f_blocks
            available_bytes = stat.f_frsize * stat.f_bavail  # available to non-root
            used_bytes = total_bytes - (stat.f_frsize * stat.f_bfree)
            used_percent = round((used_bytes / total_bytes) * 100, 1) if total_bytes > 0 else 0

            # 2. Category breakdown (expensive — cached with TTL)
            now = time.time()
            if now - self._category_cache_time > self._category_ttl:
                categories = {}
                for name, path in self.paths.items():
                    size = self._get_dir_size(path)
                    categories[name] = {"path": path, "bytes": size}
                self._category_cache = categories
                self._category_cache_time = now
            categories = self._category_cache

            # 3. Compute status level
            effective_available = max(0, available_bytes - self.eeg_reserve_bytes)
            can_record = available_bytes > self.eeg_reserve_bytes

            if used_percent >= self.critical_percent or not can_record:
                status_level = "critical"
            elif used_percent >= self.warn_percent:
                status_level = "warn"
            else:
                status_level = "ok"

            # 4. Replace cache atomically
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
            # Keep the old cache — don't clear it on error

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
                    pass
        except PermissionError:
            pass
        return total

    def get_status(self) -> dict:
        """Return cached storage status for the API. Instant (no disk I/O)."""
        if self._cache is None:
            # No data yet — trigger a synchronous refresh
            self.refresh()
        return self._cache or {
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

    def can_start_recording(self, num_cameras: int = 4) -> tuple[bool, str]:
        """Check if a new recording session is allowed.

        Returns:
            (allowed, reason) — reason is empty string if allowed.

        Fail-open: if no cache exists, returns (True, "") to avoid
        silently blocking science.
        """
        status = self._cache
        if status is None:
            return True, ""

        available = status["available_bytes"]
        reserve = status["eeg_reserve_bytes"]

        if available <= reserve:
            avail_gb = available / (1024 ** 3)
            reserve_gb = reserve / (1024 ** 3)
            return False, (
                f"Insufficient disk space: {avail_gb:.1f} GB available, "
                f"{reserve_gb:.0f} GB reserved for EEG/EMG. "
                f"Free up space or reduce eeg_reserve_gb in config."
            )

        return True, ""
```

### 2.2 Add `fetch_camera_bitrates()` Method

This method is called on-demand (not in the background loop) when the user clicks "Refresh Bitrates" in the UI. It queries each Pi's go2rtc API and parses the actual bitrate from the stream exec commands.

Add this to the `StorageMonitor` class:

```python
    def fetch_camera_bitrates(self) -> dict:
        """Query go2rtc APIs on each Pi to get actual per-camera bitrates.

        Called on-demand via the /api/storage/camera-bitrates endpoint
        when the user clicks the "Refresh Bitrates" button.

        Returns:
            {
                "camera_bitrates": {"pi_cam_0": 1.5, "pi_cam_1": 1.5, ...},
                "default_mbps": 1.5,
                "source": "go2rtc" | "default",
                "errors": ["http://192.168.0.12:1984: Connection refused"]
            }
        """
        import re
        import urllib.request
        import json as json_mod

        go2rtc_apis = self._config.get("storage", {}).get("go2rtc_apis", [])
        default_mbps = self.camera_bitrate_mbps

        if not go2rtc_apis:
            # No go2rtc APIs configured — return defaults for all cameras
            cameras = self._config.get("cameras", {})
            return {
                "camera_bitrates": {
                    cam_id: default_mbps
                    for cam_id in cameras.values()
                },
                "default_mbps": default_mbps,
                "source": "default",
                "errors": [],
            }

        camera_bitrates = {}
        errors = []
        source = "go2rtc"

        for api_url in go2rtc_apis:
            try:
                url = f"{api_url.rstrip('/')}/api/streams"
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    streams = json_mod.loads(resp.read().decode())

                # go2rtc /api/streams returns: {"stream_name": {"producers": [...]}}
                # Each producer has a "url" field with the exec command
                for stream_name, stream_info in streams.items():
                    producers = stream_info.get("producers", [])
                    if not producers:
                        # No active producers — try to parse from config
                        # Fallback: check if there's a "url" at stream level
                        continue

                    for producer in producers:
                        cmd = producer.get("url", "")
                        # Parse --bitrate NNNNNN from the rpicam-vid command
                        match = re.search(r"--bitrate\s+(\d+)", cmd)
                        if match:
                            bitrate_bps = int(match.group(1))
                            camera_bitrates[stream_name] = round(
                                bitrate_bps / 1_000_000, 2
                            )
                            break
                    else:
                        # No bitrate found in any producer — use default
                        camera_bitrates[stream_name] = default_mbps

            except Exception as e:
                errors.append(f"{api_url}: {e}")
                logger.warning("Failed to fetch bitrates from %s: %s", api_url, e)

        # Fill in any configured cameras not found in go2rtc responses
        cameras = self._config.get("cameras", {})
        for cam_id in cameras.values():
            if cam_id not in camera_bitrates:
                camera_bitrates[cam_id] = default_mbps

        if not camera_bitrates:
            source = "default"

        return {
            "camera_bitrates": camera_bitrates,
            "default_mbps": default_mbps,
            "source": source,
            "errors": errors,
        }
```

> [!tip] How go2rtc API works
> `GET http://192.168.0.11:1984/api/streams` returns the configured streams.
> Each stream's producer has a `url` field containing the exec command:
> `exec:rpicam-vid ... --bitrate 1500000 ...`
> We parse `--bitrate NNNNNN` with a regex and convert to Mbps.
> If a Pi is unreachable (timeout 5s), we log the error and fall back to the default.

### 2.3 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| `os.statvfs("/")` every 30s | Single syscall, ~0ms. Reports the filesystem where all storage paths reside (single 1.9 TB partition). |
| Category scans cached 5 min | `os.scandir` walk over 100+ GB of recordings takes seconds. Running every 30s is wasteful; 5-min TTL is plenty since categories change slowly. |
| Atomic cache swap | `self._cache = new_dict` is atomic in CPython (GIL protects reference assignment). No locks needed. |
| Fail-open on no cache | If StorageMonitor hasn't populated yet, `can_start_recording()` returns `True`. Blocking science on a monitoring startup race is worse than allowing one unchecked session. |
| Background thread (not async) | The daemon is threaded, not async. Matches existing patterns (`threading.Thread` for exports). |

**Validation:**
```bash
# Quick test: import and run manually
cd /opt/neurosurveillance
python3 -c "
from backend.storage_monitor import StorageMonitor
sm = StorageMonitor({'storage': {'paths': {'recordings': '/srv/frigate/storage/recordings'}, 'eeg_reserve_gb': 200}})
sm.refresh()
import json; print(json.dumps(sm.get_status(), indent=2))
"
```

---

## Step 3: Add API Endpoints

**File:** `neurosurveillance/backend/api.py`

### 3.1 Add module-level variable

Near the existing `_config` variable (around line 45), add:

```python
_storage_monitor = None  # Set by init_api()
```

### 3.2 Update `init_api()` signature

Add `storage_monitor` parameter:

```python
def init_api(
    session_manager: "SessionManager",
    radiens_poller: "RadiensPoller",
    frigate_controller: "FrigateController",
    config: dict,
    manual_session_manager: "ManualSessionManager | None" = None,
    storage_monitor=None,  # <-- ADD THIS
):
    global _session_manager, _radiens_poller, _frigate_controller, _config
    global _manual_session_manager, _storage_monitor  # <-- ADD _storage_monitor
    _session_manager = session_manager
    _radiens_poller = radiens_poller
    _frigate_controller = frigate_controller
    _manual_session_manager = manual_session_manager
    _storage_monitor = storage_monitor  # <-- ADD THIS
    _config = config
    logger.info("API initialized")
```

### 3.3 Add `GET /api/storage` endpoint

Add after the existing `/api/health` endpoint:

```python
@app.route("/api/storage", methods=["GET"])
def get_storage():
    """Disk usage status, category breakdown, and recording feasibility.

    Returns cached storage metrics (updated every 30s by background thread).
    Response is instant — no disk I/O on request.
    """
    if not _storage_monitor:
        return jsonify({"error": "Storage monitor not initialized"}), 503
    return jsonify(_storage_monitor.get_status())
```

### 3.4 Add `GET /api/storage/estimate` endpoint

```python
@app.route("/api/storage/estimate", methods=["GET"])
def estimate_storage():
    """Calculate estimated storage for a planned recording.

    Query params:
        cameras (int): Number of cameras (1-4), default 4
        hours (float): Recording duration in hours, default 24

    Returns estimated bytes, whether it fits, and remaining space after.
    """
    if not _storage_monitor:
        return jsonify({"error": "Storage monitor not initialized"}), 503

    cameras = request.args.get("cameras", 4, type=int)
    hours = request.args.get("hours", 24, type=float)
    cameras = max(1, min(cameras, 4))
    hours = max(0.1, min(hours, 168))  # Cap at 1 week

    bitrate_mbps = _config.get("storage", {}).get("camera_bitrate_mbps", 1.5)
    estimated_bytes = int(cameras * bitrate_mbps * 1_000_000 / 8 * hours * 3600)

    status = _storage_monitor.get_status()
    effective_available = status["effective_available_bytes"]
    fits = estimated_bytes < effective_available

    return jsonify({
        "cameras": cameras,
        "hours": hours,
        "estimated_bytes": estimated_bytes,
        "effective_available_bytes": effective_available,
        "fits": fits,
        "remaining_after_bytes": effective_available - estimated_bytes,
    })
```

### 3.5 Add `GET /api/storage/camera-bitrates` endpoint

This is called when the user clicks "Refresh Bitrates" in the StoragePanel calculator. It queries the go2rtc APIs on each Pi and returns actual per-camera bitrates.

```python
@app.route("/api/storage/camera-bitrates", methods=["GET"])
def get_camera_bitrates():
    """Fetch actual camera bitrates from go2rtc APIs on the Pis.

    Called on-demand when the user clicks "Refresh Bitrates" in the UI.
    Queries each Pi's go2rtc API, parses --bitrate from stream configs.
    Falls back to the configured default if a Pi is unreachable.

    Returns:
        camera_bitrates: dict mapping camera_id to bitrate in Mbps
        default_mbps: the configured fallback bitrate
        source: "go2rtc" if any Pi was queried, "default" if none configured
        errors: list of error messages for unreachable Pis
    """
    if not _storage_monitor:
        return jsonify({"error": "Storage monitor not initialized"}), 503
    return jsonify(_storage_monitor.fetch_camera_bitrates())
```

### 3.6 Augment `GET /api/health`

Update the existing `health_check()` function to include storage level. This lets the header badge work without a separate fetch:

```python
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint (systemd watchdog + monitoring)."""
    radiens_ok = _radiens_poller.connected if _radiens_poller else False
    mqtt_ok = _frigate_controller.mqtt_connected if _frigate_controller else False

    healthy = radiens_ok and mqtt_ok
    status_code = 200 if healthy else 503

    response = {
        "healthy": healthy,
        "radiens_connected": radiens_ok,
        "mqtt_connected": mqtt_ok,
    }

    # Piggyback storage level onto health response
    if _storage_monitor:
        storage = _storage_monitor.get_status()
        response["storage_level"] = storage["status_level"]
        response["storage_used_percent"] = storage["used_percent"]

    return jsonify(response), status_code
```

**Validation:**
```bash
# After restarting the daemon:
curl -s http://127.0.0.1:8585/api/storage | python3 -m json.tool
curl -s "http://127.0.0.1:8585/api/storage/estimate?cameras=4&hours=24" | python3 -m json.tool
curl -s http://127.0.0.1:8585/api/health | python3 -m json.tool
# Health response should now include storage_level and storage_used_percent

# Test bitrate refresh (queries go2rtc on both Pis):
curl -s http://127.0.0.1:8585/api/storage/camera-bitrates | python3 -m json.tool
# Expected: {"camera_bitrates": {"pi_cam_0": 1.5, "pi_cam_1": 1.5, ...}, "source": "go2rtc", ...}
# If a Pi is off, "errors" will list the unreachable URL and that camera falls back to default_mbps
```

---

## Step 4: Wire StorageMonitor into the Daemon

**File:** `neurosurveillance/backend/daemon.py`

### 4.1 Import

Add at the top with the other imports:

```python
from storage_monitor import StorageMonitor
```

### 4.2 Initialize in `__init__()`

After the `RadiensPoller` initialization (around line 158), add:

```python
        # Storage monitor
        self.storage_monitor = StorageMonitor(config)
```

### 4.3 Start in `start()`

In the `start()` method, before the main loop begins, add:

```python
        # Start storage monitoring
        self.storage_monitor.start()
```

### 4.4 Pass to `init_api()`

Find the `init_api()` call (around line 226-236) and add the parameter:

```python
        init_api(
            session_manager=self.session_manager,
            radiens_poller=self.poller,
            frigate_controller=self.frigate,
            config=self.config,
            manual_session_manager=self.manual_session_manager,
            storage_monitor=self.storage_monitor,  # <-- ADD THIS
        )
```

### 4.5 Stop in shutdown handler

In `_signal_handler()` (around line 519), add before the existing cleanup:

```python
        self.storage_monitor.stop()
```

**Validation:**

Steps 2-4 together complete the backend storage monitor. Restart the daemon and verify:

```bash
# Restart
sudo systemctl restart neurosurveillance-session

# Check it started cleanly
sudo systemctl status neurosurveillance-session

# Look for the storage monitor startup log line
journalctl -u neurosurveillance-session --since "1 min ago" --no-pager | grep -i "storage monitor"
# Expected: "Storage monitor started: poll=30s, reserve=200 GB, warn=75%, crit=90%"

# Test the new API endpoints
curl -s http://127.0.0.1:8585/api/storage | python3 -m json.tool
# Expected: JSON with total_bytes, used_bytes, categories, etc.

curl -s "http://127.0.0.1:8585/api/storage/estimate?cameras=4&hours=24" | python3 -m json.tool
# Expected: estimated_bytes ~64,800,000,000, fits: true

curl -s http://127.0.0.1:8585/api/storage/camera-bitrates | python3 -m json.tool
# Expected: per-camera bitrates from go2rtc (or defaults if Pis are off)

curl -s http://127.0.0.1:8585/api/health | python3 -m json.tool
# Expected: now includes "storage_level" and "storage_used_percent" fields
```

---

## Step 5: Add Cap Enforcement

**File:** `neurosurveillance/backend/daemon.py`

### 5.1 Block Radiens-triggered sessions

In `_handle_session_start()` (around line 257), add **before** the chamber loop:

```python
    def _handle_session_start(self, status: RadiensStatus):
        """Called when Radiens transitions R_OFF -> R_ON."""
        logger.info(">>> SESSION START detected")

        chambers_to_start = [
            str(c_id).replace("chamber_", "")
            for c_id in self.session_manager.cameras
        ]

        # --- STORAGE CAP ENFORCEMENT ---
        allowed, reason = self.storage_monitor.can_start_recording(
            num_cameras=len(chambers_to_start)
        )
        if not allowed:
            logger.error(
                "SESSION START BLOCKED — storage cap: %s", reason
            )
            # Do NOT start Frigate recording.
            # Radiens EEG continues (we cannot stop it, and shouldn't).
            # Video won't be captured for this session.
            return
        # --- END CAP ENFORCEMENT ---

        for chamber_id in chambers_to_start:
            # ... existing code continues unchanged ...
```

> [!warning] Important
> This blocks the **video** recording only. The EEG/EMG (Radiens) recording continues unaffected — we cannot and should not interfere with the XDAQ system. The researcher will see a "critical" warning in the UI.

### 5.2 Block manual recordings

In `_handle_external_recording_on()` (around line 435), add before `start_recording`:

```python
    def _handle_external_recording_on(self, camera_id: str):
        """Start a manual recording session when Frigate UI triggers Record ON."""
        if self._is_radiens_active_for(camera_id):
            return

        # --- STORAGE CAP ENFORCEMENT ---
        allowed, reason = self.storage_monitor.can_start_recording(num_cameras=1)
        if not allowed:
            logger.error(
                "MANUAL RECORDING BLOCKED for %s — storage cap: %s",
                camera_id, reason,
            )
            # Cancel the Frigate-initiated recording
            self.frigate.set_recording(camera_id, enabled=False)
            return
        # --- END CAP ENFORCEMENT ---

        mouse_id, recording_type, user_name = self._resolve_manual_metadata(camera_id)
        self.manual_session_manager.start_recording(
            camera_id,
            mouse_id=mouse_id,
            recording_type=recording_type,
            user_name=user_name,
        )
```

### 5.3 Behavior Summary

| Scenario | What happens | EEG impact |
|----------|-------------|------------|
| Radiens starts + disk OK | Normal: all cameras start recording | None |
| Radiens starts + disk LOW | Video recording blocked, EEG continues | **None** — EEG is unaffected |
| Manual recording + disk LOW | Recording immediately cancelled via MQTT | None |
| Space freed up | Next session start succeeds automatically | None |
| Daemon restart needed? | **No** — recovery is automatic | N/A |

**Validation:**
```bash
# Test cap enforcement by temporarily setting a huge reserve:
# In config.yaml, change eeg_reserve_gb to 1800 (nearly fills the disk)
# Restart daemon (`sudo systemctl restart neurosurveillance-session`), then trigger a recording — check logs:
journalctl -u neurosurveillance-session -f
# You should see: "SESSION START BLOCKED — storage cap: Insufficient disk space..."
# Reset eeg_reserve_gb to 200 and restart to restore normal operation
```

---

## Step 6: Frontend — TypeScript Types

**File:** `neurosurveillance/frontend/src/types/api.ts`

### 6.1 Add StorageStatus interface

Add at the end of the file:

```typescript
export interface StorageStatus {
    total_bytes: number;
    used_bytes: number;
    available_bytes: number;
    used_percent: number;
    categories: Record<string, { path: string; bytes: number }>;
    eeg_reserve_bytes: number;
    effective_available_bytes: number;
    status_level: "ok" | "warn" | "critical";
    camera_bitrate_mbps: number;
    can_record: boolean;
    last_updated: number;
}

export interface StorageEstimate {
    cameras: number;
    hours: number;
    estimated_bytes: number;
    effective_available_bytes: number;
    fits: boolean;
    remaining_after_bytes: number;
}

export interface CameraBitratesResponse {
    camera_bitrates: Record<string, number>;  // camera_id -> Mbps
    default_mbps: number;
    source: "go2rtc" | "default";
    errors: string[];
}
```

### 6.2 Update HealthResponse

Add optional storage fields to the existing interface:

```typescript
export interface HealthResponse {
    healthy: boolean;
    radiens_connected: boolean;
    mqtt_connected: boolean;
    storage_level?: "ok" | "warn" | "critical";
    storage_used_percent?: number;
}
```

**Validation:** TypeScript compilation check:
```bash
cd /home/skimlab/Monitoring_project/neurosurveillance/frontend
npx tsc --noEmit 2>&1 | head -20
# Should have no errors related to StorageStatus, StorageEstimate, CameraBitratesResponse, or HealthResponse
```

---

## Step 7: Frontend — API Client

**File:** `neurosurveillance/frontend/src/api/client.ts`

### 7.1 Add imports

Update the import at the top to include the new types:

```typescript
import {
    DaemonStatus,
    SetMetadataRequest,
    SetMetadataResponse,
    SessionHistoryResponse,
    HealthResponse,
    ActiveSession,
    StorageStatus,              // <-- ADD
    CameraBitratesResponse,     // <-- ADD
} from "../types/api";
```

### 7.2 Add getStorage and getCameraBitrates functions

Add at the end of the file:

```typescript
export async function getStorage(): Promise<StorageStatus> {
    const res = await fetch(`${API_BASE}/api/storage`);
    if (!res.ok) throw new Error("Storage fetch failed");
    return res.json();
}

export async function getCameraBitrates(): Promise<CameraBitratesResponse> {
    const res = await fetch(`${API_BASE}/api/storage/camera-bitrates`);
    if (!res.ok) throw new Error("Camera bitrates fetch failed");
    return res.json();
}
```

**Validation:**
```bash
cd /home/skimlab/Monitoring_project/neurosurveillance/frontend
npx tsc --noEmit 2>&1 | head -20
# No errors related to getStorage or getCameraBitrates
```

---

## Step 8: Frontend — `useStoragePoll` Hook

**New file:** `neurosurveillance/frontend/src/hooks/useStoragePoll.ts`

Follows the exact same pattern as `useHealthPoll.ts`:

```typescript
import { useState, useEffect } from "react";
import { getStorage } from "../api/client";
import { StorageStatus } from "../types/api";

const STORAGE_POLL_INTERVAL = 10_000; // 10 seconds

export function useStoragePoll() {
    const [storage, setStorage] = useState<StorageStatus | null>(null);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        let mounted = true;

        const poll = async () => {
            try {
                const data = await getStorage();
                if (mounted) {
                    setStorage(data);
                    setError(null);
                }
            } catch (err: any) {
                if (mounted) {
                    setError(err);
                    setStorage(null);
                }
            }
        };

        poll(); // Immediate first fetch
        const interval = setInterval(poll, STORAGE_POLL_INTERVAL);
        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, []);

    return { storage, error };
}
```

**Validation:**
```bash
cd /home/skimlab/Monitoring_project/neurosurveillance/frontend
npx tsc --noEmit 2>&1 | head -20
# No errors related to useStoragePoll
```

---

## Step 9: Frontend — `formatBytes` Utility

**New file:** `neurosurveillance/frontend/src/utils/format.ts`

```typescript
/**
 * Format a byte count into a human-readable string.
 * Examples: "17.2 GB", "79.4 MB", "1.62 TB"
 */
export function formatBytes(bytes: number): string {
    if (bytes < 0) return "0 B";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
    if (bytes < 1024 ** 4) return `${(bytes / 1024 ** 3).toFixed(1)} GB`;
    return `${(bytes / 1024 ** 4).toFixed(2)} TB`;
}
```

**Validation:**
```bash
cd /home/skimlab/Monitoring_project/neurosurveillance/frontend
npx tsc --noEmit 2>&1 | head -20
# No errors related to formatBytes
```

---

## Step 10: Frontend — `StoragePanel` Component

**New file:** `neurosurveillance/frontend/src/components/StoragePanel.tsx`

This is the main footer card showing storage status and the inline calculator.

```tsx
import { useState } from "react";
import { useStoragePoll } from "../hooks/useStoragePoll";
import { getCameraBitrates } from "../api/client";
import { CameraBitratesResponse } from "../types/api";
import { formatBytes } from "../utils/format";

export function StoragePanel() {
    const { storage, error } = useStoragePoll();

    // Calculator state
    const [calcCameras, setCalcCameras] = useState(4);
    const [calcHours, setCalcHours] = useState(24);

    // Bitrate refresh state
    const [cameraBitrates, setCameraBitrates] = useState<CameraBitratesResponse | null>(null);
    const [bitrateLoading, setBitrateLoading] = useState(false);

    // Progress bar color based on status level
    const progressColor =
        !storage || storage.status_level === "ok"
            ? "progress-success"
            : storage.status_level === "warn"
              ? "progress-warning"
              : "progress-error";

    // Calculator: use per-camera bitrates if available, else default
    const getAvgBitrateMbps = (): number => {
        if (cameraBitrates && Object.keys(cameraBitrates.camera_bitrates).length > 0) {
            const values = Object.values(cameraBitrates.camera_bitrates);
            return values.reduce((sum, v) => sum + v, 0) / values.length;
        }
        return storage?.camera_bitrate_mbps ?? 1.5;
    };

    const avgBitrateMbps = getAvgBitrateMbps();
    const bitrateBytes = avgBitrateMbps * 1_000_000 / 8;
    const estimatedBytes = calcCameras * bitrateBytes * calcHours * 3600;
    const effectiveAvailable = storage?.effective_available_bytes ?? 0;
    const fits = estimatedBytes < effectiveAvailable;

    // Refresh bitrates from go2rtc APIs on the Pis
    const handleRefreshBitrates = async () => {
        setBitrateLoading(true);
        try {
            const data = await getCameraBitrates();
            setCameraBitrates(data);
        } catch {
            // Silently fail — keep using default or last known values
        } finally {
            setBitrateLoading(false);
        }
    };

    return (
        <div className="card bg-base-200 shadow-xl h-full border border-base-300">
            <div className="card-body p-4">
                <h2 className="card-title text-sm text-base-content/70 uppercase tracking-widest mb-2 font-bold">
                    Storage
                </h2>

                {error && (
                    <div className="alert alert-error text-sm p-2 mb-2 rounded-md">
                        <span>Storage data unavailable</span>
                    </div>
                )}

                {storage && (
                    <>
                        {/* Progress bar */}
                        <div className="flex items-center gap-2 mb-1">
                            <progress
                                className={`progress ${progressColor} flex-1 h-3`}
                                value={storage.used_percent}
                                max={100}
                            />
                            <span className="text-sm font-mono font-bold min-w-[3rem] text-right">
                                {storage.used_percent}%
                            </span>
                        </div>

                        {/* Summary */}
                        <p className="text-xs text-base-content/60 mb-3">
                            {formatBytes(storage.used_bytes)} used of {formatBytes(storage.total_bytes)}
                        </p>

                        {/* Category breakdown */}
                        <div className="text-xs space-y-1 mb-3">
                            {Object.entries(storage.categories).map(([name, cat]) => (
                                <div key={name} className="flex justify-between">
                                    <span className="capitalize text-base-content/70">{name}</span>
                                    <span className="font-mono">{formatBytes(cat.bytes)}</span>
                                </div>
                            ))}
                        </div>

                        {/* EEG Reserve & Effective Free */}
                        <div className="border-t border-base-300 pt-2 mb-3 text-xs space-y-1">
                            <div className="flex justify-between text-warning">
                                <span>EEG/EMG Reserve</span>
                                <span className="font-mono">{formatBytes(storage.eeg_reserve_bytes)}</span>
                            </div>
                            <div className="flex justify-between font-bold">
                                <span>Free for Recording</span>
                                <span className="font-mono">{formatBytes(storage.effective_available_bytes)}</span>
                            </div>
                        </div>

                        {/* Cannot record warning */}
                        {!storage.can_record && (
                            <div className="alert alert-error text-xs p-2 mb-3 rounded-md">
                                <span>Recording blocked — disk below EEG reserve</span>
                            </div>
                        )}

                        {/* Inline Calculator */}
                        <div className="border-t border-base-300 pt-3">
                            <div className="flex justify-between items-center mb-2">
                                <h3 className="text-xs text-base-content/50 uppercase tracking-wider font-semibold">
                                    Calculator
                                </h3>
                                <button
                                    className="btn btn-ghost btn-xs gap-1 text-base-content/50 hover:text-primary"
                                    onClick={handleRefreshBitrates}
                                    disabled={bitrateLoading}
                                    title="Sync bitrates from go2rtc on each Pi"
                                >
                                    {bitrateLoading ? (
                                        <span className="loading loading-spinner loading-xs" />
                                    ) : (
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-3.5 h-3.5">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182" />
                                        </svg>
                                    )}
                                    <span className="text-[10px]">Sync Bitrates</span>
                                </button>
                            </div>

                            {/* Bitrate source indicator */}
                            <div className="text-[10px] text-base-content/40 mb-2">
                                {cameraBitrates ? (
                                    <>
                                        <span className="text-success">Synced from go2rtc</span>
                                        {cameraBitrates.errors.length > 0 && (
                                            <span className="text-warning ml-1">
                                                ({cameraBitrates.errors.length} Pi unreachable)
                                            </span>
                                        )}
                                        <span className="ml-1">— avg {avgBitrateMbps.toFixed(1)} Mbps</span>
                                    </>
                                ) : (
                                    <span>Default: {avgBitrateMbps.toFixed(1)} Mbps/cam</span>
                                )}
                            </div>

                            {/* Per-camera bitrate breakdown (shown after refresh) */}
                            {cameraBitrates && Object.keys(cameraBitrates.camera_bitrates).length > 0 && (
                                <div className="text-[10px] space-y-0.5 mb-2 bg-base-300/50 rounded p-1.5">
                                    {Object.entries(cameraBitrates.camera_bitrates).map(([camId, mbps]) => (
                                        <div key={camId} className="flex justify-between">
                                            <span className="text-base-content/50">{camId}</span>
                                            <span className="font-mono">{mbps} Mbps</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="flex gap-2 mb-2">
                                <label className="flex flex-col text-xs flex-1">
                                    <span className="text-base-content/60 mb-1">Cameras</span>
                                    <select
                                        className="select select-bordered select-xs w-full"
                                        value={calcCameras}
                                        onChange={(e) => setCalcCameras(Number(e.target.value))}
                                    >
                                        {[1, 2, 3, 4].map((n) => (
                                            <option key={n} value={n}>{n}</option>
                                        ))}
                                    </select>
                                </label>
                                <label className="flex flex-col text-xs flex-1">
                                    <span className="text-base-content/60 mb-1">Hours</span>
                                    <input
                                        type="number"
                                        className="input input-bordered input-xs w-full"
                                        min={0.5}
                                        max={168}
                                        step={0.5}
                                        value={calcHours}
                                        onChange={(e) => setCalcHours(Number(e.target.value) || 1)}
                                    />
                                </label>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                                <span>
                                    Estimated: <span className="font-mono font-bold">{formatBytes(estimatedBytes)}</span>
                                </span>
                                <span className={fits ? "text-success font-bold" : "text-error font-bold"}>
                                    {fits ? "Fits" : "Won't fit"}
                                </span>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
```

> [!tip] Styling & UX Notes
> - The card uses the same `bg-base-200 shadow-xl border border-base-300` as `SystemHealth`
> - The header uses the same `text-sm uppercase tracking-widest font-bold` pattern
> - Calculator is inline (always visible) as requested — no modal or collapse
> - **"Sync Bitrates" button** queries go2rtc on each Pi (takes ~1-2s). Shows a spinner while loading.
> - After sync: per-camera bitrate breakdown appears and the calculator uses actual values
> - Before sync (or if Pis unreachable): falls back to `camera_bitrate_mbps` default from config
> - Bitrate state is local to the component — refreshed on demand, not polled

**Validation:**
```bash
cd /home/skimlab/Monitoring_project/neurosurveillance/frontend
npx tsc --noEmit 2>&1 | head -20
# No errors related to StoragePanel
```

---

## Step 11: Frontend — Update `App.tsx`

**File:** `neurosurveillance/frontend/src/App.tsx`

### 11.1 Add imports

```typescript
import { StoragePanel } from './components/StoragePanel';
import { useHealthPoll } from './hooks/useHealthPoll';
```

### 11.2 Add health poll to App (for header badge)

Inside the `App()` function, add the health hook:

```typescript
const { health } = useHealthPoll();
```

### 11.3 Add storage badge in header

In the header `<div className="flex items-center gap-6">` section, add **before** the `isOffline` badge (around line 112):

```tsx
{/* Storage indicator in header */}
{health?.storage_level && (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono font-bold ${
        health.storage_level === "critical"
            ? "bg-error/20 text-error"
            : health.storage_level === "warn"
              ? "bg-warning/20 text-warning"
              : "bg-success/10 text-success/70"
    }`}>
        <progress
            className={`progress w-16 h-2 ${
                health.storage_level === "critical"
                    ? "progress-error"
                    : health.storage_level === "warn"
                      ? "progress-warning"
                      : "progress-success"
            }`}
            value={health.storage_used_percent ?? 0}
            max={100}
        />
        <span>{health.storage_used_percent ?? 0}%</span>
    </div>
)}

{/* Critical storage warning — same style as Daemon Offline */}
{health?.storage_level === "critical" && (
    <div className="badge badge-error gap-2 p-3 font-bold shadow-lg shadow-error/20">
        Disk Critical — Recording Blocked
    </div>
)}
```

### 11.4 Update footer grid

Change the footer grid from 1+3 columns to 1+1+2:

**Before:**
```tsx
<div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-4 border-t border-base-300 pt-8">
    <div className="lg:col-span-1 min-h-[180px]">
        <SystemHealth />
    </div>
    <div className="lg:col-span-3 min-h-[300px]">
        <SessionHistory refreshTick={sessionEndedTick} />
    </div>
</div>
```

**After:**
```tsx
<div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-4 border-t border-base-300 pt-8">
    <div className="lg:col-span-1 min-h-[180px]">
        <SystemHealth />
    </div>
    <div className="lg:col-span-1 min-h-[180px]">
        <StoragePanel />
    </div>
    <div className="lg:col-span-2 min-h-[300px]">
        <SessionHistory refreshTick={sessionEndedTick} />
    </div>
</div>
```

**Validation:**

This is the final frontend step. Run the full TypeScript check and start the dev server:

```bash
cd /home/skimlab/Monitoring_project/neurosurveillance/frontend

# TypeScript compilation — should be zero errors
npx tsc --noEmit

# Start the Vite dev server
npm run dev
# Open the URL shown (usually http://localhost:1420 or http://localhost:5173)
```

Verify in the browser:
- Header shows a storage percentage badge with a mini progress bar (green at current ~11% usage)
- Footer now has 3 cards: SystemHealth | StoragePanel | SessionHistory
- StoragePanel shows the progress bar, category breakdown, EEG reserve, and calculator
- Calculator inputs (cameras, hours) update the estimate instantly
- "Sync Bitrates" button appears next to the Calculator heading

> [!tip] If the daemon is not running
> The StoragePanel will show "Storage data unavailable" — that's correct behavior.
> Start the daemon first (`sudo systemctl start neurosurveillance-session`) then the data will appear within 10 seconds.

---

## Step 12: Full Validation Checklist

After implementing all steps, validate end-to-end:

### Backend

- [ ] `curl -s http://127.0.0.1:8585/api/storage | python3 -m json.tool` — returns valid JSON with correct disk values
- [ ] `curl -s "http://127.0.0.1:8585/api/storage/estimate?cameras=4&hours=24" | python3 -m json.tool` — `estimated_bytes` ≈ 64,800,000,000 (~64.8 GB)
- [ ] `curl -s http://127.0.0.1:8585/api/health | python3 -m json.tool` — includes `storage_level` and `storage_used_percent`
- [ ] Daemon logs show: `Storage monitor started: poll=30s, reserve=200 GB, warn=75%, crit=90%`

### Cap Enforcement

- [ ] Temporarily set `eeg_reserve_gb: 1800` → restart daemon
- [ ] Trigger a recording → logs show `SESSION START BLOCKED`
- [ ] Reset to `eeg_reserve_gb: 200` → restart → recording works

### Frontend

- [ ] Header shows storage percentage bar (green at current ~11% usage)
- [ ] Footer shows `StoragePanel` card between `SystemHealth` and `SessionHistory`
- [ ] StoragePanel shows correct total, used, categories
- [ ] EEG reserve shows 200 GB
- [ ] Calculator: 4 cameras x 24 hours = ~64.8 GB, "Fits" in green
- [ ] Calculator: 4 cameras x 168 hours (1 week) = ~453.6 GB, should still "Fit" at current usage
- [ ] Click "Sync Bitrates" — spinner appears, then per-camera breakdown shows (e.g., `pi_cam_0: 1.5 Mbps`)
- [ ] If a Pi is off, "1 Pi unreachable" warning appears, offline cameras fall back to default
- [ ] Calculator estimate updates to use synced bitrate values

### Edge Cases

- [ ] Kill the daemon → frontend shows "Storage data unavailable" error in StoragePanel
- [ ] Restart daemon → data resumes within 10 seconds

---

## Files Summary

| File | Action | Lines Changed (approx) |
|------|--------|----------------------|
| `config/config.yaml` | Modify | +10 lines |
| `backend/storage_monitor.py` | **Create** | ~230 lines (includes `fetch_camera_bitrates()`) |
| `backend/api.py` | Modify | +60 lines (3 endpoints + health update + init) |
| `backend/daemon.py` | Modify | +25 lines (init + cap enforcement + shutdown) |
| `frontend/src/types/api.ts` | Modify | +20 lines |
| `frontend/src/api/client.ts` | Modify | +7 lines |
| `frontend/src/hooks/useStoragePoll.ts` | **Create** | ~40 lines |
| `frontend/src/utils/format.ts` | **Create** | ~12 lines |
| `frontend/src/components/StoragePanel.tsx` | **Create** | ~190 lines (includes bitrate refresh) |
| `frontend/src/App.tsx` | Modify | +30 lines |
| **Total** | 4 new + 6 modified | ~580 lines |

---

## Future: NAS Transfer Integration

When the Synology NAS (`100.120.86.10` via Tailscale) is ready:

1. Create `nas_transfer.py` — watches for `export_status == "completed"` sessions
2. Uses `rsync` over Tailscale to `100.120.86.10:/volume1/neurosurveillance/`
3. Updates `nas_transfer_status` in session records (`"skipped"` → `"transferring"` → `"completed"`)
4. Optionally deletes local exports after confirmed NAS transfer → frees space automatically
5. Add a "NAS" row to StoragePanel showing transfer queue and status
6. Config already has the `nas` section stub — just set `enabled: true` and fill in the host/path

The current architecture is fully compatible — no refactoring needed.

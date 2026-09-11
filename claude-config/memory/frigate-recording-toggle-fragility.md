---
name: frigate-recording-toggle-fragility
description: "Recording is gated behind a retained MQTT toggle, so any stray OFF silently ends capture — including on every daemon shutdown"
metadata: 
  node_type: memory
  type: project
  originSessionId: f0dd1ed7-2e3e-4d71-be58-c673d64cf0de
  modified: 2026-07-28T03:32:40.730Z
---

Frigate `config.yml` has `record.enabled: true`, but that is only the startup default. Actual capture is gated at runtime by retained MQTT topic `frigate/{cam}/recordings/set`. Runtime truth is `curl -s http://127.0.0.1:5000/api/config` → `cameras.{cam}.record.enabled`, NOT the YAML.

**Why this matters:** the topic is RETAINED, so an OFF survives reboots and container restarts. Recording can be off for hours with cameras streaming fine (`camera_fps` normal), disk healthy, and no error in any log. Nothing alerts on it. Frigate logs show no line at all when recording stops.

**The shutdown bug (still open):** on SIGTERM the daemon publishes OFF to all 4 cameras:
```
Stopping all camera recordings...
Published OFF to frigate/pi_cam_0/recordings/set
```
Retained → recording stays off after the reboot until someone manually toggles it back. Every daemon restart or host reboot silently ends capture. Confirmed 2026-07-14 19:09:59 (grub-fix reboot); pi_cam_2/pi_cam_3 never came back and lost everything after 19:14.

Log line `External recording state change: {cam} -> OFF (was ON)` means a **human clicked a UI toggle** ("external" = not daemon-initiated). Grep this to date any capture gap.

**Diagnostic gotcha:** recording directories `/media/frigate/recordings/YYYY-MM-DD/HH/` are **UTC**, not KST. A gap that looks like it starts at 00:xx is really 09:xx KST. File mtimes are the reliable clock.

**Toggling OFF also DESTROYS the last 10-20s of every session** (root-caused 2026-07-27). Not a segmentation rounding artifact — segmentation alone would yield MORE footage, not less. Frigate `frigate/record/maintainer.py:250` (in-container `/opt/frigate/`):
```python
# Just delete files if recordings are turned off
if (camera not in self.config.cameras
        or not self.config.cameras[camera].record.enabled):
    self.drop_segment(cache_path)   # unlink, NOT moved to disk
    return
```
ffmpeg closes a `/tmp/cache` segment every 10s; the maintainer flushes cache→disk only every 5s. Anything still in cache at the moment of OFF is UNLINKED. Leading edge is safe (pre-enable cache segments are kept).

Worked example, manual pi_cam_3 session 2026-07-27: ON 15:45:34, OFF 15:46:07, export window 37s, daemon warned `probed 19.0s of expected 32.6s (58%)`. Segments on disk were only `45.23/45.33/45.43` (cover 45:23-45:53); intersect with the export window = exactly 19.0s. Segments 45.53 and 46.03 were dropped. Daemon was NOT at fault — its ffprobe sanity check caught it correctly, it just cannot un-delete files.

**Verify a suspected tail loss:** `docker exec frigate ls -la /media/frigate/recordings/YYYY-MM-DD/HH/{cam}/` and check the last segment's timestamp against the OFF time in `session-daemon.log`.

**Measured again 2026-07-28** on a 14.97h run: ~11s lost (last segment 00:16:58 UTC vs OFF 00:17:14; export 53875s vs 53886s requested). That is 99.98% so the daemon's `<0.95×` check never fired. **The loss is FIXED-SIZE, not proportional** — invisible at 15h, ate 42% of a 37s test.

## FIX (written + 12/12 tests pass 2026-07-28; NOT yet active)

Refcounted **lease** model replaces the boolean: `enabled = (manual_lease OR session_lease)`.

- `frigate_controller.py`: `acquire_lease` / `release_lease` / `adopt_lease` / `has_lease` / `lease_holders` / `get_cameras_recording`, plus `DEFAULT_DRAIN_SECONDS = 30`. Nothing outside that section may call `set_recording(enabled=False)`.
- **30s drain** before the LAST release (worst case in flight = 10s segment + 5s flush = 15s; 30s is 2×, ~3MB/session, NOT a tuning knob). Runs inside the export thread, before the export.
- **FAIL-ON at shutdown**: `stop()` publishes nothing, no `stop_all_recording()`. A stuck-ON camera is recoverable; a lost tail or retained OFF is not. Shutdown mid-drain aborts the drain and leaves recording ON.
- **Startup ADOPTS** instead of stomping: reads `/api/config` runtime state, adopts already-recording cameras as manual leases. `recording.reset_on_start: true` restores the old publish-OFF clean slate.
- Config: `recording.{drain_seconds: 30, reset_on_start: false}`. Tests: `backend/tests/test_recording_leases.py`.

⚠️ **The drain CANNOT help manual UI stops** — the Frigate UI publishes OFF before the daemon observes it, so the segments are already dropped. Only the daemon-controlled (Radiens) path is drainable. Mitigation = operator habit, stop ~30s late.
⚠️ **Startup grace-period interaction is the least-tested part** (that logic assumed startup publishes OFF).

> [!warning] `/opt/neurosurveillance/session-daemon` is a SYMLINK to `~/sleep-recording-skim/neurosurveillance/backend`
> Editing the repo EDITS THE DEPLOYMENT; there is no copy step. The running process holds the old code in memory (up since 2026-07-17), so **the new code activates on ANY restart — crash, reboot, or apt included. The moment is not yours to pick.** Production `config.yaml` has no `recording:` block, which is fine: code defaults match it. Flip `sessions.auto_start: true` only AFTER a deliberate restart.

**Proposed fix (declined for now):** record 24/7 continuously with `retain.days`, never toggle, and use exports to carve out session spans after the fact. Removes the whole class of "did video record?" failures AND the tail loss. Budget as of 2026-07-27: measured 1.9MB/10s segment = 1.5 Mbps/cam, 4 cams = ~65 GB/day; `retain.days: 7` = ~455 GB; disk had 1.1 TB free (41% used), clears the 200 GB EEG reserve.

Related: [[frigate-exports-moved-out-of-frigate-dir]]

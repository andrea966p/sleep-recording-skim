---
name: project-daemon-startup-guard-regression
description: "The daemon's 10s startup grace period (designed to suppress Frigate's record.enabled=true reassertion) failed on 2026-05-20 — needs investigation"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b64ed9b-5689-4074-8603-f37b0836d899
---

The daemon's startup guard against Frigate's `record.enabled=true` reassertion has a regression. Per `01-infrastructure/session-daemon/architecture.md`, the daemon should:
1. Wait 10 seconds for Frigate to finish reasserting `ON` from config on startup
2. Drain stale `_expected_states`
3. Use `_last_known_state` check to suppress duplicate ON states

**On 2026-05-20 at 16:28, this failed.** A user-initiated `docker start frigate` triggered creation of 4 fresh "Manual recording started" sessions with new IDs (`1f9121b1`, `f36c755b`, `512a9a79`, plus one for pi_cam_0), producing 4 short MP4 exports (~8 MB each, 45-53s) and 4 session JSONs.

**Why:** The guard exists specifically to prevent false manual sessions on every startup. Its failure means any future Frigate restart (crash, manual restart, host reboot) will continue producing spurious session metadata and small exports — even though the docker-upgrade trigger is now blocked by `apt-mark hold`.

**How to apply:** When investigating spurious manual sessions on Frigate restart, start by reading `frigate_controller.py` and `manual_session_manager.py` for the grace-period / `_last_known_state` / `_expected_states` logic. Likely causes to check: (a) grace period too short for cold start, (b) `_last_known_state` not initialized before MQTT subscribe, (c) initial MQTT retained message arriving before grace period starts.

Related: [[feedback-record-enabled-false-off-limits]], [[project-docker-upgrade-recordings]]

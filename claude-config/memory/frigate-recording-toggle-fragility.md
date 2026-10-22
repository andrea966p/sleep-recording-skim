---
name: frigate-recording-toggle-fragility
description: "Frigate recording is gated by a retained MQTT toggle; any OFF silently ends capture and toggling OFF drops the last 10-20 s of a session. Lease/drain/fail-ON fix written 2026-07-28 and now loaded in the running daemon."
metadata: 
  node_type: memory
  type: project
  originSessionId: f0dd1ed7-2e3e-4d71-be58-c673d64cf0de
  modified: 2026-07-28T03:32:40.730Z
---

Runtime capture is gated by the retained MQTT topic `frigate/{cam}/recordings/set` (truth: `curl -s http://127.0.0.1:5000/api/config` -> `cameras.{cam}.record.enabled`, not the YAML); a stray OFF survives reboots and nothing alerts. Toggling OFF also unlinks the last 10-20 s still in `/tmp/cache` (`maintainer.py:250` `drop_segment`; fixed-size loss, 37 s test -> 19.0 s, 14.97 h run lost ~11 s). Fix (written + 12/12 tests 2026-07-28): refcounted lease model, 30 s drain before the last release, FAIL-ON at shutdown, startup ADOPTS runtime state. The original memory said "not yet active"; the running daemon has it loaded since the 2026-10-07 14:34 restart (vault VN-1, inferred from file + restart date, not tested live).

Details: [[2026-07-27-video-eeg-sync-recording-architecture]]

⚠️ The drain cannot help manual UI stops (the UI publishes OFF before the daemon sees it): stop ~30 s late. Diagnostic gotcha: `/media/frigate/recordings/YYYY-MM-DD/HH/` directories are UTC, not KST. `External recording state change: {cam} -> OFF (was ON)` in the daemon log means a human clicked a UI toggle. 🛑 Never propose `record.enabled: false` as a fix ([[feedback_record_enabled_false_off_limits]]). Flip `sessions.auto_start: true` only after a deliberate restart.

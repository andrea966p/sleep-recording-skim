---
name: project-daemon-startup-guard-regression
description: "2026-05-20 startup-guard regression: a manual docker start frigate made 4 spurious sessions; later fixed by the frigate/available grace. Incident in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b64ed9b-5689-4074-8603-f37b0836d899
---

2026-05-20 16:28: the daemon's 10 s startup grace failed and a manual `docker start frigate` created 4 spurious "Manual recording started" sessions and exports. Closed 2026-05-24 (Phase 3): the daemon now also runs the grace on every non-initial `frigate/available=online` and defers state callbacks 1.5 s.

Details: [[2026-05-20-docker-upgrade-and-startup-guard-regression]] · [[architecture]] (session-daemon) · [[reconciler]]

- When investigating spurious manual sessions on a Frigate restart, read `frigate_controller.py` / `manual_session_manager.py` (grace period, `_last_known_state`, `_expected_states`) first.
- Related: [[feedback_record_enabled_false_off_limits]] · [[pattern_frigate_mqtt_message_ordering]]

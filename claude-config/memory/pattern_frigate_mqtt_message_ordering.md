---
name: pattern-frigate-mqtt-message-ordering
description: "Frigate republishes retained topics in last-published order on reconnect: recordings/state arrives BEFORE frigate/available, so a grace window cannot be armed by availability; defer state callbacks 1.5 s"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5cbc6d77-6b1d-49ac-9f41-42050a74c3fc
---

On (re)connect Mosquitto replays retained topics in last-published order: `frigate/<cam>/recordings/state` reaches the daemon BEFORE `frigate/available=online`. Fix shipped 2026-05-24 (commit `3830dba`): defer state callbacks with `threading.Timer(STATE_DEFER_SECONDS = 1.5)`, cancel pending timers in the availability handler, skip the first retained `online` (`_initial_available_seen`).

Details: [[reconciler]] · [[2026-05-24]] (journal) · code `frigate_controller.py`

- 🛑 For any MQTT producer that republishes several retained topics, check its real order with `mosquitto_sub` before designing the receiver; do not assume "availability first".

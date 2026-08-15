---
name: pattern_netdata_no_mqtt_collector
description: "Netdata has no MQTT collector; MQTT alert topics reach Slack via the standalone nvr-mqtt-slack.service bridge, not Netdata"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1586510f-8585-4984-ab9c-4ab00319c308
---

Netdata (v2.10.3 on the NVR) ships **no MQTT collector** — the go.d plugin has a `mosquitto` module (broker `$SYS` stats only), but nothing that subscribes to arbitrary topics. So Netdata **cannot** turn an MQTT message into an alert. The 2026-05-20 sprint plan assumed a "Netdata MQTT collector subscribes to the stall topic" — that path does not exist.

**The actual mechanism (since 2026-05-25):** a standalone systemd service `nvr-mqtt-slack.service` bridges MQTT → Slack.
- Script: `neurosurveillance/backend/scripts/nvr-mqtt-slack.py` (runs at `/opt/neurosurveillance/session-daemon/scripts/...` via the symlink).
- Unit + env template + setup script: `neurosurveillance/deploy/` (NOT under the `session-daemon` symlink — reference by full repo path at install time).
- Secrets in `/etc/nvr-mqtt-slack.env` (mode 0600): `NVR_MQTT_PASSWORD` + `SLACK_WEBHOOK_URL` (the shared webhook).
- It `docker exec mosquitto mosquitto_sub` (mosquitto-clients not on host) and POSTs each message to Slack. `Restart=always` reconnects when the broker container restarts.
- Currently forwards `neurosurveillance/watchdog/+/stall`. The reconciler-findings topic is stubbed for 4.6 (enable after the 3-night dry-run; alert only when partial+stuck+degraded > 0, suppress orphan).

**How to apply:** For any future "MQTT event → Slack/alert" need, extend this bridge (add a topic + handler branch, restart), don't reach for a Netdata collector. Doc: vault [[watchdog-slack-bridge]]. Related: [[project_phase_4_complete]].

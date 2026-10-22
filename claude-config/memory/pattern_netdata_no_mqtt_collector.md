---
name: pattern_netdata_no_mqtt_collector
description: "Netdata has no MQTT collector; MQTT alert topics reach the alert channel via the standalone nvr-mqtt-slack.service bridge, not Netdata"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1586510f-8585-4984-ab9c-4ab00319c308
---

Netdata cannot turn an MQTT message into an alert (its go.d `mosquitto` module reads only broker `$SYS` stats). Since 2026-05-25 a standalone `nvr-mqtt-slack.service` bridges MQTT to the alert channel (`docker exec mosquitto mosquitto_sub`, secrets in `/etc/nvr-mqtt-slack.env`, forwards `neurosurveillance/watchdog/+/stall`). Slack delivery has since been partly replaced by ntfy (topic in MEMORY.md).

Details: [[watchdog-slack-bridge]] · [[2026-05-stabilization-sprint-week-1-plan]]

- For any new "MQTT event to alert" need, extend this bridge (topic + handler branch, restart); do not reach for a Netdata collector.

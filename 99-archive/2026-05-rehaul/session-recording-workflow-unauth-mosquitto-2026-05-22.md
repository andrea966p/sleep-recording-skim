---
tags: [archive, 2026-05-rehaul]
archived: 2026-05-24
superseded-by: "[[02-procedures/session-recording-workflow]]"
reason: "Mosquitto authentication added; troubleshooting commands now require -u nvr -P …"
---

*Archived from `02-procedures/session-recording-workflow.md` on 2026-05-24. See `superseded-by` for the current version.*

This file captures the pre-2026-05-22 unauthenticated MQTT examples in the session-recording workflow troubleshooting section. The current live doc adds `-u nvr -P "$NVR_MQTT_PASSWORD"` to every `mosquitto_pub` / `mosquitto_sub` invocation and adds a new "How to ask the journal what happened" section that points at `GET /api/journal` and `GET /api/reconciler/last`.

## Troubleshooting — Video not recording in Frigate — pre-2026-05-22

| Check | Command |
|-------|---------|
| MQTT broker running? | `docker ps \| grep mosquitto` |
| Frigate running? | `docker ps \| grep frigate` |
| Camera streams active? | Check Frigate UI at `http://192.168.0.50:5000` |
| MQTT messages flowing? | `docker exec mosquitto mosquitto_sub -t 'frigate/#' -v` |

The "MQTT messages flowing?" command above worked anonymously prior to 2026-05-22. Post-sprint, the same command returns `Connection error: Bad user name or password` without credentials.

## Pre-sprint troubleshooting envelope

The pre-sprint workflow file did not yet reference the session WAL journal or the nightly reconciler — those shipped 2026-05-23 and 2026-05-24 respectively. The pre-change troubleshooting section ended at the "Daemon crashed mid-session" subsection without any mention of journal queries or reconciler findings as diagnostic surfaces.

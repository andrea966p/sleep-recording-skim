---
tags: [archive, 2026-05-rehaul]
archived: 2026-05-24
superseded-by: "[[02-procedures/installation/frigate-setup]]"
reason: "Mosquitto authentication added; CLI examples now require -u nvr -P …"
---

*Archived from `02-procedures/installation/frigate-setup.md` on 2026-05-24. See `superseded-by` for the current version.*

This file captures the pre-2026-05-22 Mosquitto deployment step from the Frigate setup procedure. After the stabilization sprint, the broker requires authentication (user `nvr`), the validation `mosquitto_sub` command takes credentials, and the rationale "acceptable for an isolated lab LAN" is no longer the operating assumption.

## Step 4: Deploy Mosquitto Configuration — pre-2026-05-22

```bash
nano /srv/frigate/mosquitto/mosquitto.conf
```

Paste the following:

```ini
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest stdout
```

> [!tip] Security Note (historical — applied prior to 2026-05-22)
> `allow_anonymous true` is acceptable for an isolated lab LAN with no internet exposure. For networks with external access, configure authentication.

## Validation step — pre-2026-05-22

The validation block that exercised the MQTT broker did so without credentials:

```bash
# Verify Frigate is connected
docker exec mosquitto mosquitto_sub -t 'frigate/#' -C 1 -W 5
# Expected: receives at least one message within 5 seconds
```

The current live procedure substitutes `mosquitto_sub -u nvr -P "$NVR_MQTT_PASSWORD" -t 'frigate/#' -C 1 -W 5` and pulls the password from `[[00-config/production-values]]`.

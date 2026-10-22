---
tags: [archive, 2026-05-rehaul]
archived: 2026-05-24
superseded-by: "[[docker-compose]]"
reason: "Mosquitto allow_anonymous→false + nvr auth; SHA-pinning of Frigate/Mosquitto/Netdata images; Frigate Python log host volume"
---

*Archived from `01-infrastructure/frigate/docker-compose.md` on 2026-05-24. See `superseded-by` for the current version.*

This file captures the pre-2026-05-22 verbatim content of the sections that the stabilization sprint replaced. Three changes landed together:

1. Mosquitto switched from anonymous to authenticated (user `nvr`).
2. Frigate, Mosquitto, and Netdata images are now pinned by `image:tag@sha256:digest` so `docker compose pull` cannot silently upgrade them.
3. Frigate's Python process logs were previously tmpfs-only (in-container, ephemeral); they now live on the host at `/srv/frigate/logs/frigate/current`.

The pre-change content of the affected sections appears below.

## Production Configuration (v5.1) — pre-2026-05-22

```yaml
services:
  mosquitto:
    container_name: mosquitto
    image: eclipse-mosquitto:2
    restart: unless-stopped
    volumes:
      - ./mosquitto:/mosquitto/config:ro
    ports:
      - "1883:1883"

  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:0.16.1
    restart: unless-stopped
    stop_grace_period: 30s
    depends_on:
      - mosquitto
    cap_add:
      - CAP_PERFMON
    shm_size: "256mb"
    devices:
      - /dev/dri/renderD128:/dev/dri/renderD128
    group_add:
      - "992"   # render group (getent group render)
      - "44"    # video group (getent group video)
    environment:
      LIBVA_DRIVER_NAME: iHD
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./config:/config
      - ./storage:/media/frigate
      - type: tmpfs
        target: /tmp/cache
        tmpfs:
          size: 1G
    ports:
      - "5000:5000"    # Web UI
      - "8554:8554"    # RTSP restream
      - "8555:8555/tcp"  # WebRTC
      - "8555:8555/udp"
```

Notable absences (later additions): `mosquitto` had no `volumes` or `passwd` file mount, no `nvr` user; `frigate` had no `/srv/frigate/logs/frigate/current` bind mount; both images carried floating tags rather than `@sha256:` pins.

## Mosquitto Config — pre-2026-05-22

**Path:** `/srv/frigate/mosquitto/mosquitto.conf`

```
listener 1883
allow_anonymous true
persistence false
log_dest stdout
```

The rationale at the time: "acceptable for an isolated lab LAN with no internet exposure." Replaced 2026-05-22 with `allow_anonymous false` and a `password_file` directive (see current version of the live doc for the production replacement).

---
tags: [infrastructure, frigate, docker, golden-config]
created: 2026-02-05
updated: 2026-05-24
status: production
version: "5.2"
---

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The `docker-compose.yml` file that runs Frigate + Mosquitto on the NVR.
>
> **Why it exists.** Docker Compose is what brings these two containers up together with the right volumes, ports, and dependencies. If you ever rebuild the NVR from scratch, this file is the recipe.
>
> **How to read this page.** Scan the "Production Configuration" section to see what's deployed. Mosquitto requires authentication since 2026-05-22; the SHA-pinned image digest is what stops `docker compose pull` from silently swapping the broker version. Frigate's Python logs persist to `/srv/frigate/logs/frigate/` since 2026-05-22 so a container restart doesn't wipe them.
>
> See also [[../system-overview|System overview]] for the big picture.

> [!quote] Paper-ready
> The Frigate NVR runs as a Docker container alongside an authenticated Mosquitto MQTT broker; the broker image is pinned by SHA-256 digest, anonymous connections are disallowed, and Frigate's Python-side logs persist to a host-mounted volume so they survive container restarts and are available for post-mortem analysis.

## File Location

**Path:** `/srv/frigate/docker-compose.yml`

## Directory Structure

```
/srv/frigate/
├── docker-compose.yml
├── config/
│   └── config.yml          # Frigate config
├── storage/                 # Recordings (1.8TB available)
├── logs/                    # Persistent Frigate Python logs (since 2026-05-22)
│   └── frigate/
│       └── current
└── mosquitto/
    ├── mosquitto.conf       # MQTT broker config
    └── passwd               # bcrypt-hashed password for user `nvr` (since 2026-05-22)
```

## Production Configuration (v5.2)

```yaml
services:
  mosquitto:
    container_name: mosquitto
    image: eclipse-mosquitto:2@sha256:9cfdd46ad59f3e3e5f592f6baf57ab23e1ad00605509d0f5c1e9b179c5314d87
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
      - ./logs/frigate:/dev/shm/logs/frigate     # persistent Frigate Python logs (2026-05-22)
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

> [!info] Mosquitto image is SHA-pinned; Frigate is tag-pinned
> The Mosquitto image is pinned by digest (`@sha256:…`) because the upstream `eclipse-mosquitto:2` tag is a moving target and a `docker compose pull` could otherwise swap in a new minor version unexpectedly. The Frigate image stays at the explicit `:0.16.1` tag because Frigate publishes per-version tags reliably. If you want full SHA-pinning across the board, follow the [[../../99-archive/2026-05-rehaul/frigate-docker-compose-2026-05-22|pre-sprint version pattern]] (but on the Frigate side too).

### Mosquitto Config

**Path:** `/srv/frigate/mosquitto/mosquitto.conf`

```
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd
persistence false
log_dest stdout
```

The `password_file` directive points at `/srv/frigate/mosquitto/passwd` on the host (mounted into the container via the `:ro` config volume). The credentials live in [[../../00-config/production-values#Mosquitto MQTT Authentication (since 2026-05-22)|production-values.md]]; do not commit them to a public repo.

> [!history] Historical note — pre-2026-05-22
> Before 2026-05-22 the broker ran with `allow_anonymous true` and no password file. The rationale at the time was "acceptable for an isolated lab LAN with no internet exposure." Frigate, the session daemon, and any operator's `mosquitto_pub` / `mosquitto_sub` connected without credentials. Full pre-change text: [[../../99-archive/2026-05-rehaul/frigate-docker-compose-2026-05-22|archived docker-compose.md]].

## Critical Settings

| Setting | Value | Why |
|---------|-------|-----|
| `shm_size` | `256mb` | Prevents "out of memory" errors |
| `devices: renderD128` | Specific device | Intel QSV GPU access (not full `/dev/dri`) |
| `group_add: 992, 44` | render, video | GPU permissions |
| `LIBVA_DRIVER_NAME: iHD` | Intel driver | Hardware acceleration |
| `cap_add: CAP_PERFMON` | Replaces `privileged: true` | Minimal privileges for perf monitoring |
| `stop_grace_period: 30s` | Graceful shutdown | Allows Frigate to flush recordings before stopping |
| `depends_on: mosquitto` | Startup order | MQTT broker must be ready before Frigate |

## v5.0 → v5.1 Changes

| Change | Why |
|--------|-----|
| Added Mosquitto MQTT broker | Enables Frigate event system |
| Removed `privileged: true` | Security — use `cap_add: CAP_PERFMON` instead |
| `/dev/dri` → `/dev/dri/renderD128` | Minimal device access — only the render node needed |
| Added `stop_grace_period: 30s` | Prevent recording corruption on shutdown |
| Removed `FRIGATE_RTSP_PASSWORD` | Not needed for internal LAN restreaming |

## Commands

```bash
# Start everything (Mosquitto + Frigate)
cd /srv/frigate && docker compose up -d

# Stop everything
docker compose down

# Restart Frigate only
docker compose restart frigate

# View logs
docker compose logs -f frigate
docker compose logs -f mosquitto

# Container status
docker compose ps

# Resource usage
docker stats --no-stream frigate mosquitto

# API stats
curl -s http://localhost:5000/api/stats | python3 -m json.tool
```

## Related

- [[config-yml]] - Frigate configuration
- [[../../01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]

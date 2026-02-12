---
tags: [infrastructure, frigate, docker, golden-config]
created: 2026-02-05
updated: 2026-02-12
status: production
version: "5.1"
---

## File Location

**Path:** `/srv/frigate/docker-compose.yml`

## Directory Structure

```
/srv/frigate/
├── docker-compose.yml
├── config/
│   └── config.yml          # Frigate config
├── storage/                 # Recordings (1.8TB available)
└── mosquitto/
    └── mosquitto.conf       # MQTT broker config
```

## Production Configuration (v5.1)

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

### Mosquitto Config

**Path:** `/srv/frigate/mosquitto/mosquitto.conf`

```
listener 1883
allow_anonymous true
persistence false
log_dest stdout
```

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

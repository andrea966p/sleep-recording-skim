---
tags: [infrastructure, frigate, docker, golden-config]
created: 2026-02-05
status: production
version: "5.0"
---

## File Location

**Path:** `/srv/frigate/docker-compose.yml`

## Production Configuration (v5.0)

```yaml
services:
  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:0.16.1  # Pinned version
    restart: unless-stopped
    privileged: true
    shm_size: "256mb"
    devices:
      - /dev/dri:/dev/dri  # Intel GPU access
    group_add:
      - "992"   # render group (verify: getent group render)
      - "44"    # video group (verify: getent group video)
    environment:
      FRIGATE_RTSP_PASSWORD: "CHANGE_ME"
      LIBVA_DRIVER_NAME: iHD  # Intel media driver
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
      - "8554:8554"    # RTSP
      - "8555:8555/tcp"  # WebRTC
      - "8555:8555/udp"
```

## Critical Settings

| Setting | Value | Why |
|---------|-------|-----|
| `shm_size` | `256mb` | Prevents "out of memory" errors |
| `devices: /dev/dri` | Required | Intel QSV GPU access |
| `group_add: 992, 44` | render, video | GPU permissions |
| `LIBVA_DRIVER_NAME: iHD` | Intel driver | Hardware acceleration |

## Commands

```bash
# Start Frigate
docker compose up -d

# Stop Frigate
docker compose down

# Restart
docker compose restart frigate

# View logs
docker compose logs -f frigate

# Check resource usage
docker stats frigate
```

## Related

- [[config-yml]] - Frigate configuration
- [[../../00-config/production-values|Production Values]]

---
tags: [infrastructure, frigate, config, golden-config]
created: 2026-02-05
updated: 2026-02-24
status: production
version: "5.2"
---

## File Location

**Path:** `/srv/frigate/config/config.yml`

## Production Configuration (v5.2 - Recording Only)

```yaml
mqtt:
  enabled: true
  host: mosquitto
  port: 1883

database:
  path: /media/frigate/frigate.db

detect:
  enabled: false

ffmpeg:
  hwaccel_args: preset-intel-qsv-h264

record:
  enabled: true
  retain:
    days: 7
    mode: all
  expire_interval: 60

snapshots:
  enabled: false

cameras:
  pi_cam_0:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_0
          input_args:
            - -rtsp_transport
            - tcp
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
          roles:
            - record
    detect:
      enabled: false
      width: 1024
      height: 768
    record:
      enabled: true

  pi_cam_1:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_1
          input_args:
            - -rtsp_transport
            - tcp
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
          roles:
            - record
    detect:
      enabled: false
      width: 1024
      height: 768
    record:
      enabled: true

ui:
  timezone: Asia/Seoul

logger:
  default: info
```

## Critical Settings

| Setting | Value | Why |
|---------|-------|-----|
| `hwaccel_args` | `preset-intel-qsv-h264` | Global GPU decoding — inherited by all cameras (9-12% CPU vs 100%) |
| `-rtsp_transport tcp` | Required | Prevents frame drops over network |
| `buffer_size: 512000` | Network jitter handling | Large buffer for TCP transport |
| `detect.width/height` | `1024x768` on both cameras | Prevents aspect-ratio mismatch that can look zoomed in UI |
| `detect: false` | Stability | Recording-only mode |
| `mqtt.host: mosquitto` | Docker service name | Resolves to Mosquitto container via Docker networking |

## v5.1 → v5.2 Changes

| Change | Why |
|--------|-----|
| Added explicit `detect.width`/`detect.height` (`1024x768`) to `pi_cam_0` and `pi_cam_1` | Fixes occasional stream probe mismatch (`1280x720` on cam1) causing zoomed/cropped live view |

## Expected Performance

| Metric | Value |
|--------|-------|
| CPU Usage | 9-12% |
| GPU Usage | 3-4% |
| Memory | ~870MB |
| Storage (7 days) | ~225 GB (1.5Mbps × 2 cameras) |

## Related

- [[docker-compose]] - Docker setup + Mosquitto config
- [[../../01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]

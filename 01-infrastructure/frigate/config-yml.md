---
tags: [infrastructure, frigate, config, golden-config]
created: 2026-02-05
status: production
version: "5.0"
---

## File Location

**Path:** `/srv/frigate/config/config.yml`

## Production Configuration (v5.0 - Recording Only)

```yaml
# Frigate Recording-Only Config v5.0
mqtt:
  enabled: false

database:
  path: /media/frigate/frigate.db

detect:
  enabled: false  # Detection disabled for stability

# Intel QSV hardware acceleration
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
      hwaccel_args: preset-intel-qsv-h264
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_0
          input_args:
            - -rtsp_transport
            - tcp  # CRITICAL: TCP for reliability
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
          roles:
            - record
    detect:
      enabled: false
    record:
      enabled: true

  pi_cam_1:
    ffmpeg:
      hwaccel_args: preset-intel-qsv-h264
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_1
          input_args:
            - -rtsp_transport
            - tcp  # CRITICAL: TCP for reliability
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
          roles:
            - record
    detect:
      enabled: false
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
| `hwaccel_args` | `preset-intel-qsv-h264` | GPU decoding (9-12% CPU vs 100%) |
| `-rtsp_transport tcp` | Required | Prevents frame drops |
| `buffer_size: 512000` | Network jitter handling | |
| `detect: false` | Stability | Recording-only mode |

## Expected Performance

| Metric | Value |
|--------|-------|
| CPU Usage | 9-12% |
| GPU Usage | 3-4% |
| Memory | ~870MB |

## Related

- [[docker-compose]] - Docker setup
- [[../../01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]

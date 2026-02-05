---
tags: [infrastructure, raspberry-pi, go2rtc, golden-config]
created: 2026-02-04
status: production
version: "5.0"
---

# Golden go2rtc Configuration

> [!tip] Golden Configuration
> This is the battle-tested, production-stable configuration.
> **DO NOT MODIFY** without extensive testing.

## File Location

**Path:** `/opt/go2rtc/go2rtc.yaml`

## Production Configuration (v5.0)

```yaml
# GO2RTC v5.0 - Production Stable
# Path: /opt/go2rtc/go2rtc.yaml

streams:
  pi_cam_0:
    exec: >
      rpicam-vid
      --codec libav
      --libav-format h264
      --width 1024
      --height 768
      --framerate 15
      --bitrate 1500000
      --inline
      --timeout 0
      --camera 0
      --level 4.1
      --profile high
      -o -
      | ffmpeg -hide_banner -loglevel error
        -f h264 -i -
        -c copy
        -f rtsp rtsp://127.0.0.1:8554/pi_cam_0

  pi_cam_1:
    exec: >
      rpicam-vid
      --codec libav
      --libav-format h264
      --width 1024
      --height 768
      --framerate 15
      --bitrate 1500000
      --inline
      --timeout 0
      --camera 1
      --level 4.1
      --profile high
      -o -
      | ffmpeg -hide_banner -loglevel error
        -f h264 -i -
        -c copy
        -f rtsp rtsp://127.0.0.1:8554/pi_cam_1

rtsp:
  listen: ":8554"

api:
  listen: ":1984"

log:
  level: info
```

## Critical Rules

| Rule | Reason |
|------|--------|
| **H.264 ONLY** | H.265 causes kernel panics |
| **libav codec** | Direct hardware encoding |
| **ffmpeg pipe** | Stable RTSP wrapping |
| **No TCP localhost** | Proven unstable |

## Related Files

- [[golden-systemd-service]] - The systemd service
- [[golden-boot-config]] - Boot hardening
- [[../00-config/production-values|Production Values]]

## Quick Commands

```bash
# Service status
sudo systemctl status go2rtc.service

# Restart service
sudo systemctl restart go2rtc.service

# View logs
journalctl -u go2rtc.service -f

# Check streams
curl http://localhost:1984/api/streams
```

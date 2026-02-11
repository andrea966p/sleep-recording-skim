---
tags: [infrastructure, raspberry-pi, go2rtc, golden-config]
created: 2026-02-04
status: production
version: "5.1"
---

# Golden go2rtc Configuration

> [!tip] Golden Configuration
> This is the battle-tested, production-stable configuration.
> **DO NOT MODIFY** without extensive testing.

## File Location

**Path:** `/opt/go2rtc/go2rtc.yaml`

## Production Configuration (v5.1)

```yaml
streams:
  pi_cam_0: "exec:rpicam-vid -n --codec libav --libav-format h264 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --intra 15 --timeout 0 --camera 0 --level 4.1 --profile high --low-latency --output -"
  pi_cam_1: "exec:rpicam-vid -n --codec libav --libav-format h264 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --intra 15 --timeout 0 --camera 1 --level 4.1 --profile high --low-latency --output -"

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
| **libav codec** | Software H.264 encoding via libav/x264 (Pi 5 has no HW encoder) |
| **Single-line exec strings** | YAML multi-line blocks break go2rtc parsing |
| **No ffmpeg pipes** | Proven unstable for 24/7 operation |
| **Direct rpicam-vid output** | Stream directly to go2rtc, no intermediaries |
| **`-n` (no preview)** | Disable preview window on headless Pi |
| **`--low-latency`** | Suppress B-frames for streaming compatibility (Pi 5 specific) |
| **`--intra 15`** | 1-second keyframe interval (15 frames at 15fps) for fast stream startup |

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

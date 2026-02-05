---

---
# 📦 Archive - Old Configurations (Pre-v5.0)

> [!warning] ⚠️
> **DEPRECATED**: These configurations are kept for reference only. They contain known issues that caused system instability. DO NOT USE these configurations.

## Known Issues with These Configs

- Missing `KillMode=control-group` causing zombie processes
- Using `mpegts` format instead of direct h264 pipeline
- Missing hardware watchdog configuration
- No TCP transport enforcement in Frigate
- Incorrect buffer parameters

## Old go2rtc.yaml (PROBLEMATIC)

```yaml
# OLD CONFIG - DO NOT USE
streams:
  camera0:
    - exec:/usr/bin/rpicam-vid --camera 0 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format mpegts --libav-audio 0 --flush -o -
    - ffmpeg:rtsp
  camera1:
    - exec:/usr/bin/rpicam-vid --camera 1 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format mpegts --libav-audio 0 --flush -o -
    - ffmpeg:rtsp
```

## Old systemd service (MISSING CRITICAL SETTINGS)

```plain text
# OLD SERVICE - MISSING KillMode=control-group
[Service]
KillMode=mixed  # WRONG - causes zombie processes
```

Archived on: September 23, 2025

[[🗑️ DELETED Complete Configuration Reference (v5.0) - OLD DUPLICATE]]

[[🗑️ DELETED Troubleshooting Matrix (v5.0) - OLD DUPLICATE]]

[[📦 ARCHIVED Documentation Cleanup Summary]]

[[📦 ARCHIVED v5.0 Change Tracking & Audit Report]]
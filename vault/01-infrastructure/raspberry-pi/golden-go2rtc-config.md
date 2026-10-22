---
tags: [infrastructure, raspberry-pi, go2rtc, golden-config]
created: 2026-02-04
status: production
version: "5.2"
---

# Golden go2rtc Configuration

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The `go2rtc.yaml` config on each Raspberry Pi 5. It tells `go2rtc` how to capture the Pi camera with `rpicam-vid` and republish the H.264 stream as RTSP for Frigate to consume.
>
> **Why it exists.** Frigate doesn't talk to Pi cameras directly. `go2rtc` is the bridge: it spawns a `rpicam-vid` process per camera, takes the H.264 output, and serves it on port 8554. **H.264 only** — H.265 causes Pi kernel panics; do not change the codec.
>
> **How to read this page.** The config file itself is the reference; the warnings explain the load-bearing settings. The `KillMode=control-group` rule in the [[golden-systemd-service|companion systemd unit]] is what prevents zombie `rpicam-vid` processes; do not separate the two.

> [!quote] Paper-ready
> Each Raspberry Pi 5 camera node runs go2rtc as a thin H.264-only RTSP republisher; `rpicam-vid` is invoked directly with a single-line exec string (no ffmpeg pipe), and the systemd unit's `KillMode=control-group` directive ensures clean termination without zombie capture processes.

> [!tip] Golden Configuration
> This is the battle-tested, production-stable configuration.
> **DO NOT MODIFY** without extensive testing.

## File Location

**Path:** `/opt/go2rtc/go2rtc.yaml`

## Production Configuration (v5.2)

```yaml
streams:
  pi_cam_0: "exec:rpicam-vid -n --codec libav --libav-format mpegts --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --intra 15 --timeout 0 --camera 0 --level 4.1 --profile high --low-latency --output -"
  pi_cam_1: "exec:rpicam-vid -n --codec libav --libav-format mpegts --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --intra 15 --timeout 0 --camera 1 --level 4.1 --profile high --low-latency --output -"

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
| **`--libav-format mpegts`** | MPEG-TS container over raw H.264 bitstream — better framing, timestamps, stream recovery. Recommended by RPi camera docs for streaming. Tested stable 2026-02-19/20. |
| **Single-line exec strings** | YAML multi-line blocks break go2rtc parsing |
| **No ffmpeg pipes** | Proven unstable for 24/7 operation |
| **Direct rpicam-vid output** | Stream directly to go2rtc, no intermediaries |
| **`-n` (no preview)** | Disable preview window on headless Pi |
| **`--low-latency`** | Suppress B-frames for streaming compatibility (Pi 5 specific) |
| **`--intra 15`** | 1-second keyframe interval (15 frames at 15fps) for fast stream startup |

## Related Files

- [[golden-systemd-service]] - The systemd service
- [[golden-boot-config]] - Boot hardening
- [[production-values|Production Values]]

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

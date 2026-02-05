---

---
# 🎯 Frigate NVR Configuration (v5.0 - Stable)

> [!success] ✅
> **STABLE CONFIGURATION:** This configuration has been tested for 24/7 operation with Intel QSV hardware acceleration and TCP transport for maximum reliability.

## docker-compose.yml (v5.0)

```yaml
services:
  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:0.16.1  # Pinned version for stability
    restart: unless-stopped
    privileged: true
    shm_size: "256mb"
    devices:
      - /dev/dri:/dev/dri  # Intel GPU access
    group_add:
      - "992"   # render group (verify with: getent group render)
      - "44"    # video group (verify with: getent group video)
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
      - "5000:5000"
      - "8554:8554"
      - "8555:8555/tcp"
      - "8555:8555/udp"
```

## config.yml (v5.0 - Recording Only)

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
        - path: rtsp://192.168.0.11:8554/pi_cam_0  # Note: using new stream names
          input_args:
            - -rtsp_transport
            - tcp  # CRITICAL: TCP for reliability
            - -buffer_size
            - "512000"  # Quoted to avoid validation errors
            - -max_delay
            - "500000"  # Quoted to avoid validation errors
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
        - path: rtsp://192.168.0.11:8554/pi_cam_1  # Note: using new stream names
          input_args:
            - -rtsp_transport
            - tcp  # CRITICAL: TCP for reliability
            - -buffer_size
            - "512000"  # Quoted to avoid validation errors
            - -max_delay  
            - "500000"  # Quoted to avoid validation errors
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
  logs:
    frigate.video: info
```

## Key Changes in v5.0

### 1. Hardware Acceleration

- Uses `preset-intel-qsv-h264` for Intel GPU decoding
- Proper device mapping for `/dev/dri`
- Correct group permissions for render and video groups

### 2. Network Stability

- Forced TCP transport with `-rtsp_transport tcp`
- Buffer settings to handle network jitter
- Proper stream naming (pi_cam_0/pi_cam_1 matching go2rtc)

### 3. Performance Optimization

- Detection disabled for pure recording
- No snapshots (unnecessary without detection)
- 7-day retention for reasonable storage usage

## Expected Performance

With this configuration, you should see:

- **CPU Usage**: 9-12% (down from 100%)
- **GPU Usage**: 3-4% (intel-qsv active)
- **Memory**: ~870MB
- **Stable continuous recording** without drops
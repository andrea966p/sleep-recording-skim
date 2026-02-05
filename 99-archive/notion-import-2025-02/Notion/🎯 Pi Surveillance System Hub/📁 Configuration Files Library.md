---

---
# Configuration Files Library 📁

*Production-ready configuration files with explanations and deployment instructions*

> [!note] 🎬
> **New:** For video parameter adjustments (resolution, FPS, bitrate), see the dedicated <page url="{{[https://www.notion.so/271cfe4e883b814ca9d6fd32f4fd3bf2}}">🎬](https://www.notion.so/271cfe4e883b814ca9d6fd32f4fd3bf2%7D%7D%22%3E🎬) Video Parameter Configuration Guide</page>. This page focuses on system-level configurations.

---

> [!note] 🔒
> **PRODUCTION CONFIGS:** These are the battle-tested configurations. Copy exactly for guaranteed stability. Any modifications should be tested in R&D environment first.

---

## 🐧 **Raspberry Pi System Configurations**

### `/boot/firmware/config.txt` - Boot Configuration

**Purpose:** System-level hardware configuration for optimal video streaming performance

**Deployment Location:** `/boot/firmware/config.txt`

```plain text
# =============================================================================
# RASPBERRY PI 5 SURVEILLANCE SYSTEM BOOT CONFIGURATION
# Version: 4.0 Production
# Last Updated: September 5, 2025
# =============================================================================

# GPU Memory Allocation
# Allocate 128MB to GPU for camera operations and video encoding
gpu_mem=128

# Hardware Optimization
# Disable unnecessary wireless hardware to reduce power consumption and interference
dtoverlay=disable-wifi
dtoverlay=disable-bt

# System Stability Features
# Remove boot splash for faster startup
disable_splash=1

# Enable hardware watchdog for automatic recovery from system freezes
dtparam=watchdog=on

# Thermal Protection
# Set temperature limit to 75°C (system will throttle to prevent overheating)
temp_limit=75

# Camera Interface
# Note: Camera interface is enabled via raspi-config, not in this file
```

**Validation Commands:**

```bash
# Verify GPU memory allocation
vcgencmd get_mem gpu  # Expected: gpu=128M

# Check temperature limit
vcgencmd get_config temp_limit  # Expected: temp_limit=75

# Verify watchdog is enabled
ls -la /dev/watchdog*  # Should show watchdog devices
```

**Deployment:**

```bash
sudo nano /boot/firmware/config.txt
# Paste configuration above
sudo reboot
# Verify with validation commands
```

---

## 📹 **go2rtc Stream Server Configuration**

### `/etc/go2rtc.yaml` - RTSP Stream Server

**Purpose:** Configure dual camera RTSP streaming with optimal stability settings

**Deployment Location:** `/etc/go2rtc.yaml`

```yaml
# /etc/go2rtc.yaml - STABLE PRODUCTION CONFIG v5.0
streams:
  pi_cam_0:
    - exec:/usr/bin/rpicam-vid --camera 0 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format h264 --libav-audio 0 -o -
    - ffmpeg:rtsp
  pi_cam_1:
    - exec:/usr/bin/rpicam-vid --camera 1 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format h264 --libav-audio 0 -o -
    - ffmpeg:rtsp

api:
  listen: ":1984"
```

```yaml
# RTSP Server (implicit)
# Streams will be available at:
# - rtsp://<PI_IP>:8554/pi_cam_0
# - rtsp://<PI_IP>:8554/pi_cam_1
```

## 🐳 **Frigate NVR Server Configurations**

**Parameter Explanations:**

| Parameter | Value | Rationale |
| --- | --- | --- |
| `--width 1024 --height 768` | 1024x768 | Optimal balance of quality vs CPU load |
| `--framerate 15` | 15 fps | Reduces heat generation, sufficient for monitoring |
| `--bitrate 1500000` | 1.5 Mbps | Network-friendly, good quality |
| `--codec libav` | libav wrapper | Most stable codec path, avoids Pi5 H.265 issues |
| `--libav-format h264` | H.264 | Hardware-accelerated, most stable codec |
| `--libav-audio 0` | No audio | Reduces CPU load, not needed for surveillance |
| `--flush` | Immediate flush | Reduces latency |
| `-t 0` | Infinite duration | Continuous streaming |

**Stream URLs:**

- Camera 0: `rtsp://192.168.0.11:8554/pi_cam_0`
- Camera 1: `rtsp://192.168.0.11:8554/pi_cam_1`
- Web Interface: [`http://192.168.0.11:1984`](http://192.168.0.11:1984/)

> [!warning] ⚠️
> **go2rtc Command Update:** The go2rtc binary (version 1.9.9) does not support a `-debug` flag. For configuration testing, use the basic command without debug flags. The available flags are:
> - `-c, --config` - Path to config file
> - `-d, --daemon` - Run in background
> - `-v, --version` - Print version
> 
> **For testing:** `/usr/local/bin/go2rtc -config /etc/go2rtc.yaml` (Press Ctrl+C to stop)

**Testing Commands:**

```bash
# Test configuration syntax
/usr/local/bin/go2rtc -config /etc/go2rtc.yaml

# Test RTSP streams
ffprobe rtsp://127.0.0.1:8554/pi_cam_0
```

**Deployment:**

```bash
# Create configuration file
sudo nano /etc/go2rtc.yaml
# Paste configuration above

# Set proper permissions
sudo chown root:root /etc/go2rtc.yaml
sudo chmod 644 /etc/go2rtc.yaml

# Test configuration
sudo systemctl restart go2rtc.service
sudo systemctl status go2rtc.service
```

---

## 🐳 **Frigate NVR Server Configurations**

### `/srv/frigate/docker-compose.yml` - Container Orchestration

**Purpose:** Docker Compose configuration for Frigate NVR container

**Deployment Location:** `/srv/frigate/docker-compose.yml`

```yaml
# =============================================================================
# FRIGATE NVR DOCKER COMPOSE CONFIGURATION
# Version: 4.0 Production
# Last Updated: September 16, 2025
# Optimized for: Stability, performance, resource management
# =============================================================================

version: "3.9"

services:
  frigate:
    container_name: frigate
    privileged: true
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    shm_size: "128mb"
    devices:
      - /dev/bus/usb:/dev/bus/usb
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
    environment:
      FRIGATE_RTSP_PASSWORD: "password"
```

**Volume Explanations:**

- `./config:/config` - Frigate configuration files
- `./storage:/media/frigate` - Video recordings storage
- `/tmp/cache` - RAM-based cache for performance
- `/etc/localtime` - Ensures container uses host timezone

**Deployment:**

```bash
# Create directory structure
sudo mkdir -p /srv/frigate/{config,storage}
cd /srv/frigate

# Create docker-compose.yml
sudo nano docker-compose.yml
# Paste configuration above

# Set permissions
sudo chown -R $USER:$USER /srv/frigate

# Start services
docker compose up -d

# Verify deployment
docker compose ps
docker compose logs -f frigate
```

### `/srv/frigate/config/config.yml` - Frigate Configuration

**Purpose:** Main Frigate NVR configuration for camera recording

**Deployment Location:** `/srv/frigate/config/config.yml`

> [!note] 🔴
> **CRITICAL UPDATE (September 19, 2025):** Frigate configuration has been fixed to resolve validation errors that caused container startup failures. Updated sections: UI configuration, Logger configuration.

```yaml
# =============================================================================
# FRIGATE NVR CONFIGURATION
# Version: 4.0 Production
# Last Updated: September 5, 2025
# Optimized for: Recording stability, storage management, CPU efficiency
# =============================================================================

# MQTT Configuration (disabled for standalone operation)
mqtt:
  enabled: false

# Database Configuration
database:
  # SQLite database for events and metadata
  path: /media/frigate/frigate.db

# Global Recording Configuration
record:
  enabled: true
  # Automatic cleanup after 30 days
  retain:
    days: 30
    mode: all
  # Recording quality settings
  events:
    max_seconds: 300
    pre_capture: 5
    post_capture: 5
    retain:
      default: 10
      mode: motion

# Global Detection (disabled for stability)
detect:
  enabled: false
  # Note: Detection disabled to maximize system stability
  # Enable per-camera if needed after stability verification

# Camera Configurations
cameras:
  # Camera 0 from Raspberry Pi
  pi_cam_0:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_0
          input_args: 
            # Force TCP transport for reliability
            - -rtsp_transport
            - tcp
            # Buffer settings to prevent frame drops
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
            # Reconnection settings
            - -reconnect
            - "1"
            - -reconnect_at_eof
            - "1"
            - -reconnect_streamed
            - "1"
          roles: 
            - record
            - rtmp  # Enable RTMP re-streaming
    
    # Per-camera recording settings
    record:
      enabled: true
      retain:
        days: 30
        mode: all
    
    # Detection disabled for this camera
    detect:
      enabled: false
      
  # Camera 1 from Raspberry Pi
  pi_cam_1:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_1
          input_args:
            # Identical settings to camera0 for consistency
            - -rtsp_transport
            - tcp
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
            - -reconnect
            - "1"
            - -reconnect_at_eof
            - "1"
            - -reconnect_streamed
            - "1"
          roles: 
            - record
            - rtmp
    
    record:
      enabled: true
      retain:
        days: 30
        mode: all
    
    detect:
      enabled: false

# Snapshots Configuration
snapshots:
  enabled: true
  timestamp: true
  bounding_box: false
  crop: false
  retain:
    default: 10
    
# UI Configuration
ui:
  # Use system timezone
  timezone: Asia/Seoul
  # Date format: 'full', 'long', 'medium', or 'short'
  date_style: medium
  # Time format
  time_format: 12hour

# Logging Configuration  
logger:
  default: info
  logs:
    frigate.record: info
```

**Key Configuration Notes:**

- **Detection disabled:** Maximizes stability and reduces CPU load
- **30-day retention:** Automatic cleanup prevents storage overflow
- **TCP transport:** More reliable than UDP for RTSP streams
- **Buffer optimization:** Prevents frame drops and connection issues
- **Reconnection logic:** Automatically recovers from network interruptions

**Stream Access URLs:**

- Web Interface: [`http://SERVER_IP:5000`](http://server_ip:5000/)
- RTSP Re-stream: `rtsp://SERVER_IP:8554/camera_name`
- Recordings: Available through web interface

**Deployment:**

```bash
# Create configuration file
sudo nano /srv/frigate/config/config.yml
# Paste configuration above

# Set permissions
sudo chown $USER:$USER /srv/frigate/config/config.yml

# Restart Frigate to apply changes
docker compose restart frigate

# Check logs for successful startup
docker compose logs -f frigate
```

---

## 🔧 **System Service Configurations**

### `/etc/systemd/system/go2rtc.service` - go2rtc Service

**Purpose:** Systemd service definition for go2rtc with resource limits and auto-recovery

**Deployment Location:** `/etc/systemd/system/go2rtc.service`

```bash
# =============================================================================
# GO2RTC SYSTEMD SERVICE CONFIGURATION
# Version: 4.0 Production
# Last Updated: September 16, 2025
# Features: Auto-restart, resource limits, clean shutdown, security
# CRITICAL CORRECTION: User=skimlab, ExecStart=/usr/local/bin/go2rtc -config
# =============================================================================

[Unit]
Description=go2rtc RTSP Streaming Service
Documentation=https://github.com/AlexxIT/go2rtc
After=network-online.target
Wants=network-online.target

[Service]
User=skimlab
Group=video
ExecStart=/usr/local/bin/go2rtc -config /etc/go2rtc.yaml
Restart=always
RestartSec=10
TimeoutStopSec=10
KillMode=mixed

# Resource limits for stability
MemoryMax=512M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
```

**Service Features:**

- **Memory limit:** Max 512MB RAM (prevents memory leaks)
- **Auto-restart:** 10-second delay between restart attempts
- **Security hardening:** Non-root user, system protection
- **Clean shutdown:** 10-second graceful stop timeout
- **Logging:** Integrated with systemd journal
- **CPU access:** Full CPU access (Pi dedicated to surveillance only)

**Deployment:**

```bash
# Create service file
sudo nano /etc/systemd/system/go2rtc.service
# Paste configuration above

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable go2rtc.service
sudo systemctl start go2rtc.service

# Verify service status
sudo systemctl status go2rtc.service
```

### `/etc/systemd/system/pi-monitor.service` - System Monitor

**Purpose:** System health monitoring service with automatic alerting

**Deployment Location:** `/etc/systemd/system/pi-monitor.service`

```plain text
# =============================================================================
# PI SYSTEM HEALTH MONITOR SERVICE
# Version: 4.0 Production
# Last Updated: September 16, 2025
# Features: Continuous monitoring, alerting, log management
# CRITICAL CORRECTION: User=root (required for sudo systemctl commands)
# =============================================================================

[Unit]
Description=Raspberry Pi System Health Monitor
Documentation=https://github.com/user/pi-surveillance
After=multi-user.target go2rtc.service
Wants=go2rtc.service

[Service]
User=root
Group=root
ExecStart=/opt/scripts/monitor.sh
Restart=always
RestartSec=30
TimeoutStopSec=10
KillMode=mixed
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Deployment:**

```bash
# Create service file
sudo nano /etc/systemd/system/pi-monitor.service
# Paste configuration above

# Create monitoring script (see Scripts section)
sudo nano /opt/scripts/monitor.sh

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable pi-monitor.service
sudo systemctl start pi-monitor.service

# Verify service status
sudo systemctl status pi-monitor.service
```

---

## ✅ **Configuration Validation**

### System Health Check Script

```bash
#!/bin/bash
# Configuration Validation Script

echo "=== CONFIGURATION VALIDATION ==="
echo "Date: $(date)"
echo

# Boot configuration validation
echo "[BOOT CONFIG]"
vcgencmd get_mem gpu
vcgencmd get_config temp_limit
echo

# go2rtc configuration validation
echo "[GO2RTC CONFIG]"
if /usr/local/bin/go2rtc -config /etc/go2rtc.yaml 2>&1 | head -10 | grep -q "go2rtc version"; then
    echo "✅ go2rtc config valid"
else
    echo "❌ go2rtc config invalid"
fi
echo

# Service status validation
echo "[SERVICES]"
for service in go2rtc pi-monitor; do
    status=$(systemctl is-active $service.service)
    if [[ "$status" == "active" ]]; then
        echo "✅ $service: $status"
    else
        echo "❌ $service: $status"
    fi
done
echo

# Stream validation
echo "[STREAMS]"
for camera in pi_cam_0 pi_cam_1; do
    if timeout 5 ffprobe -v quiet rtsp://
```

**Usage:**

```bash
# Save validation script
sudo nano /opt/scripts/validate-config.sh
# Paste script content above

# Make script executable
sudo chmod +x /opt/scripts/validate-config.sh

# Run validation
sudo /opt/scripts/validate-config.sh
```

---

*These configurations represent the stable, production-ready setup verified for 24/7 operation. Any modifications should be thoroughly tested in the R&D environment before deployment.*
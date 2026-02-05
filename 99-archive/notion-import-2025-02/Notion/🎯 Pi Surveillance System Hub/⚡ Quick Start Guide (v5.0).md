---

---
# ⚡ Quick Start Guide (v5.0)

*Get your surveillance system running in 30 minutes*

> [!note] 🎯
> **Purpose:** This guide provides the MINIMUM steps to get a working system. For detailed explanations, see the Complete Setup Guide.

## 📦 Prerequisites Checklist

- [x] Raspberry Pi 5 with official 27W PSU ✅ 2026-02-05
- [x] 2x Raspberry Pi Camera Module (v2 or v3) ✅ 2026-02-05
- [x] Active cooling installed ✅ 2026-02-05
- [x] 64GB+ high-endurance microSD card ✅ 2026-02-05
- [x] Ethernet cable (NO WiFi) ✅ 2026-02-05
- [x] Ubuntu server for Frigate (separate machine) ✅ 2026-02-05

## 🎓 Part 1: Raspberry Pi Setup (15 min)

### 1️⃣ Flash & Boot

```bash
# Use Raspberry Pi Imager:
# - OS: Raspberry Pi OS Lite (64-bit)
# - Enable SSH, set hostname: pi5-1
# - Username: skimlab
# - Set your password
```

### 2️⃣ Initial Setup (SSH to your Pi)

```bash
# Update system
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y rpicam-apps ffmpeg curl wget
sudo rpi-eeprom-update -a

# Enable camera
sudo raspi-config
# Navigate: 3 Interface Options → I1 Camera → Enable
# IMPORTANT: If Legacy Camera is enabled, DISABLE it!
sudo reboot
```

### 3️⃣ Configure Boot Settings

```bash
# Add critical settings
sudo nano /boot/firmware/config.txt

# Add at the end:
gpu_mem=128
dtoverlay=disable-wifi
dtoverlay=disable-bt
dtparam=watchdog=on
temp_limit=75

sudo reboot
```

### 4️⃣ Install go2rtc

```bash
# Download and install
sudo mkdir -p /opt/go2rtc
cd /opt/go2rtc
sudo wget -O go2rtc https://github.com/AlexxIT/go2rtc/releases/download/v1.9.4/go2rtc_linux_arm64
sudo chmod +x go2rtc
```

### 5️⃣ Configure go2rtc (COPY EXACTLY)

```bash
sudo nano /opt/go2rtc/go2rtc.yaml
```

Paste this configuration:

```yaml
streams:
  pi_cam_0:
    exec: >
      rpicam-vid --codec libav --libav-format h264
      --width 1024 --height 768 --framerate 15
      --bitrate 1500000 --inline --timeout 0
      --camera 0 --level 4.1 --profile high -o -
      | ffmpeg -hide_banner -loglevel error
        -f h264 -i - -c copy
        -f rtsp rtsp://127.0.0.1:8554/pi_cam_0
  pi_cam_1:
    exec: >
      rpicam-vid --codec libav --libav-format h264
      --width 1024 --height 768 --framerate 15
      --bitrate 1500000 --inline --timeout 0
      --camera 1 --level 4.1 --profile high -o -
      | ffmpeg -hide_banner -loglevel error
        -f h264 -i - -c copy
        -f rtsp rtsp://127.0.0.1:8554/pi_cam_1

rtsp:
  listen: ":8554"
api:
  listen: ":1984"
```

### 6️⃣ Create systemd Service (CRITICAL CONFIG)

```bash
sudo nano /etc/systemd/system/go2rtc.service
```

Paste EXACTLY (KillMode=control-group is MANDATORY):

```plain text
[Unit]
Description=go2rtc RTSP Streaming Service
After=network-online.target

[Service]
User=skimlab
Group=video
WorkingDirectory=/opt/go2rtc
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml
Restart=always
RestartSec=5
KillMode=control-group
TimeoutStopSec=10
CPUQuota=70%
MemoryMax=512M

[Install]
WantedBy=multi-user.target
```

### 7️⃣ Start Services

```bash
# Set permissions
sudo chown -R skimlab:video /opt/go2rtc
sudo usermod -a -G video skimlab

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now go2rtc.service

# Verify it's running
sudo systemctl status go2rtc.service
```

### 8️⃣ Test Streams

```bash
# Test camera streams
ffprobe rtsp://localhost:8554/pi_cam_0
ffprobe rtsp://localhost:8554/pi_cam_1

# Check web interface
curl http://localhost:1984/api/streams
```

## 🐳 Part 2: Frigate Server Setup (10 min)

### 1️⃣ Install Docker (on Ubuntu server)

```bash
# Quick Docker install
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Log out and back in
```

### 2️⃣ Create Frigate Structure

```bash
sudo mkdir -p /srv/frigate/{config,storage}
sudo chown -R $USER:$USER /srv/frigate
cd /srv/frigate
```

### 3️⃣ Create docker-compose.yml

```bash
nano docker-compose.yml
```

Paste (adjust for Intel QSV if available):

```yaml
version: "3.9"
services:
  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:stable
    restart: unless-stopped
    privileged: true
    volumes:
      - ./config:/config
      - ./storage:/media/frigate
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "5000:5000"
      - "8554:8554"
    environment:
      - FRIGATE_RTSP_PASSWORD=password
    # For Intel QSV (if available):
    # devices:
    #   - /dev/dri:/dev/dri
```

### 4️⃣ Create Frigate Config

```bash
nano config/config.yml
```

Paste minimal config:

```yaml
mqtt:
  enabled: false

cameras:
  pi_cam_0:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_0
          roles:
            - record
          input_args:
            - -rtsp_transport
            - tcp
    record:
      enabled: true
      retain:
        days: 7
    detect:
      enabled: false
      
  pi_cam_1:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_1
          roles:
            - record
          input_args:
            - -rtsp_transport
            - tcp
    record:
      enabled: true
      retain:
        days: 7
    detect:
      enabled: false

record:
  enabled: true
  expire_interval: 60
```

### 5️⃣ Start Frigate

```bash
# Start container
docker-compose up -d

# Check logs
docker-compose logs -f frigate
# Press Ctrl+C to exit logs
```

### 6️⃣ Access Web Interface

- Open browser: [`http://192.168.0.50:5000`](http://192.168.0.50:5000/)
- You should see both camera feeds
- Recordings will start automatically

## ✅ Verification Checklist

### On Raspberry Pi:

```bash
# All should pass:
vcgencmd get_throttled           # Should show: throttled=0x0
vcgencmd measure_temp            # Should be under 65°C
systemctl is-active go2rtc       # Should show: active
ps aux | grep rpicam-vid | wc -l # Should show: 2
```

### On Frigate Server:

```bash
# All should pass:
docker ps                         # Should show frigate running
curl http://localhost:5000/api/config  # Should return JSON
ls -la /srv/frigate/storage/recordings # Should show directories
```

## 🚑 Quick Troubleshooting

### Cameras not working?

```bash
# On Pi:
rpicam-hello --list-cameras  # Should show 2 cameras
sudo systemctl restart go2rtc.service
journalctl -u go2rtc -n 50   # Check for errors
```

### Frigate not recording?

```bash
# On Frigate server:
ping 192.168.0.11  # Check network
ffprobe rtsp://192.168.0.11:8554/pi_cam_0  # Test stream
docker-compose restart frigate
```

### System freezing?

- **CHECK**: Is `KillMode=control-group` in the service file?
- **FIX**: Edit service file, ensure KillMode is correct, restart

## 📚 Next Steps

1. **Add Monitoring**: See Watchdog & Monitoring Setup
2. **Enable Intel QSV**: See Frigate v5.0 Configuration
3. **Adjust Quality**: See Video Parameter Guide
4. **Add More Cameras**: Repeat Pi setup with new IPs

---

> [!info] ℹ️
> **Remember**: This is the MINIMUM setup. For production use, implement:
> - Hardware watchdog
> - System monitoring
> - Backup procedures
> - Intel QSV acceleration

*Quick Start Guide v5.0 - Last Updated: September 24, 2025*
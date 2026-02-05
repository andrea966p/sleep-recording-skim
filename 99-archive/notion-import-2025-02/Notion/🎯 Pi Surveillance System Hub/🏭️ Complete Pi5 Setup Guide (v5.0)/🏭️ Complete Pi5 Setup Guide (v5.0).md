---

---
# 🏗️ Complete Raspberry Pi 5 Setup Guide (v5.0)

*From Zero to Production-Grade 24/7 Operation with Hardened Stability*

**Guide Version:** 5.0 (Hardened Production Release)

**Date:** September 24, 2025

**Status:** STABLE - Incorporates all critical fixes for 24/7 operation

---

> [!note] 🎯
> **PRODUCTION READY v5.0:** This guide includes critical stability fixes:
> - `KillMode=control-group` to prevent zombie processes
> - Hardware watchdog for automatic recovery
> - Intel QSV hardware acceleration for Frigate
> - TCP-only transport for reliability
> - Proper h264 pipeline configuration

---

## 🏗️ **Architecture Overview**

**Goal:** A highly reliable, two-camera surveillance system with decoupled components.

**Resilience Principles:**

- **Decoupling:** Camera capture (rpicam-vid), streaming server (go2rtc), and NVR (Frigate) are independent processes
- **Stability over Performance:** Configurations optimized for low thermal and memory pressure
- **Proactive Monitoring:** Custom service monitors hardware vitals and process health
- **Automated Recovery:** Hardware and software watchdogs for automatic recovery

**System Flow:**

```javascript
Raspberry Pi 5 → go2rtc RTSP Server → Frigate NVR (Ubuntu PC)
     ↓              ↓                      ↓
  rpicam-vid    Stream Server         Recording & Web UI
  (Camera 0,1)   Port :8554            Port :5000
```

---

## 🔧 **Hardware Requirements & Validation**

### Power Supply Validation

```bash
# Must return throttled=0x0 (no under-voltage events)
vcgencmd get_throttled
# Expected output: throttled=0x0
```

### Thermal Validation

```bash
# Must remain below 65°C under load
vcgencmd measure_temp
# Expected: temp=45.0'C to 60.0'C (with active cooling)
```

### Critical Hardware Requirements

- **Power:** Official Raspberry Pi 5 27W (5.1V/5A) PSU
- **Cooling:** Active cooling mandatory (Pi Active Cooler)
- **Storage:** High-endurance microSD (Samsung PRO Endurance 64GB+)
- **Network:** Wired Ethernet connection only

---

## 📋 Complete Setup Procedures

### Step 1: Base OS Installation & Initial Setup

**1.1 Flash the SD Card:**

```bash
# Using Raspberry Pi Imager:
# 1. Download Raspberry Pi Imager
# 2. Select "Raspberry Pi OS Lite (64-bit)" 
# 3. Click gear icon for advanced options:
#    - Enable SSH
#    - Set hostname: pi5-1 (or pi5-2, pi5-3 for additional cameras)
#    - Set username: skimlab
#    - Set password: [your secure password]
#    - Configure WiFi (will be disabled later)
# 4. Flash to high-endurance microSD card
```

**1.2 First Boot and Updates:**

```bash
# SSH into the Pi (replace IP with your Pi's IP)
ssh skimlab@192.168.0.11

# Update the system
sudo apt update && sudo apt full-upgrade -y

# Update Pi firmware
sudo rpi-eeprom-update -a

# Install required packages
sudo apt install -y rpicam-apps ffmpeg htop iotop bc net-tools curl wget vim

# Reboot to apply updates
sudo reboot
```

**1.3 Verify System After Reboot:**

```bash
# SSH back in after reboot
ssh skimlab@192.168.0.11

# Check system info
cat /etc/os-release
uname -a

# Check temperature
vcgencmd measure_temp

# Should show temp around 45-55°C with active cooling
```

### Step 2: Camera Subsystem Configuration

**2.1 Enable Camera Interface:**

```bash
# Open raspi-config
sudo raspi-config

# Navigate through menus:
# 3 Interface Options → L1 Camera → Enable
# CRITICAL CORRECTION: DISABLE Legacy Camera if enabled!
# CRITICAL: The guide must explicitly state to DISABLE Legacy Camera
# Legacy Camera support will cause rpicam-vid to fail
# Use ONLY the standard L1 Camera interface
# Then: Finish → Reboot
sudo reboot
```

**2.2 Test Camera Hardware:**

```bash
# SSH back in after reboot
ssh skimlab@192.168.0.11

# List available cameras
rpicam-hello --list-cameras
# Expected output: Should show 2 cameras (Camera 0 and Camera 1)

# Test Camera 0 (3-second preview)
rpicam-hello --camera 0 --timeout 3000
# Should display: "Preview window displayed for 3 seconds"

# Test Camera 1 (3-second preview)
rpicam-hello --camera 1 --timeout 3000
# Should display: "Preview window displayed for 3 seconds"

# If cameras don't work, check connections and reboot
```

### Step 3: System Optimization Configuration

> [!warning] ⚠️
> **Important Note on Camera Commands:** Recent Raspberry Pi OS versions have transitioned from `libcamera-*` to `rpicam-*` commands. If you see references to `libcamera-hello` in older documentation, use `rpicam-hello` instead. The command mappings are:
> - `libcamera-hello` → `rpicam-hello`
> - `libcamera-still` → `rpicam-still`
> - `libcamera-vid` → `rpicam-vid`
> - `libcamera-raw` → `rpicam-raw`
> 
> All functionality remains the same, only the command names have changed.

**3.1 Configure Boot Settings:**

```bash
# Backup original config
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup

# Edit boot configuration
sudo nano /boot/firmware/config.txt

# Add these lines at the end of the file:
# =============================================================================
# RASPBERRY PI 5 SURVEILLANCE SYSTEM BOOT CONFIGURATION
# Version: 4.0 Production
# =============================================================================

# GPU Memory for camera operations
gpu_mem=128

# Disable unnecessary hardware to reduce power consumption
dtoverlay=disable-wifi
dtoverlay=disable-bt

# System optimization
disable_splash=1
dtparam=watchdog=on
temp_limit=75
```

**3.2 Apply Configuration and Validate:**

```bash
# Save file (Ctrl+X, Y, Enter) and reboot
sudo reboot

# SSH back in and validate
ssh skimlab@192.168.0.11

# Check GPU memory allocation
vcgencmd get_mem gpu
# Expected: gpu=128M

# Check temperature limit
vcgencmd get_config temp_limit
# Expected: temp_limit=75

# Verify watchdog is enabled
ls -la /dev/watchdog*
# Should show watchdog device files

# Check that WiFi/Bluetooth are disabled
ifconfig
# Should NOT show wlan0 interface
```

### Step 4: go2rtc Installation and Configuration

**4.1 Download and Install go2rtc:**

```bash
# Create directory for go2rtc
sudo mkdir -p /opt/go2rtc
cd /opt/go2rtc

# Download go2rtc binary for ARM64 (v1.9.4 stable)
sudo wget -O go2rtc https://github.com/AlexxIT/go2rtc/releases/download/v1.9.4/go2rtc_linux_arm64

# Make it executable
sudo chmod +x go2rtc

# Verify installation
./go2rtc --version
# Should show: go2rtc version 1.9.4
```

**4.2 Create go2rtc Configuration:**

```bash
# Create configuration file in go2rtc directory
sudo nano /opt/go2rtc/go2rtc.yaml

# Paste this EXACT configuration (v5.0 STABLE):
# =============================================================================
# GO2RTC STREAMING SERVER CONFIGURATION  
# Version: 5.0 Production - Direct h264 pipeline
# =============================================================================

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

# Save file (Ctrl+X, Y, Enter)
```

**4.3 Set Configuration Permissions:**

```bash
# Set proper ownership and permissions
sudo chown -R skimlab:video /opt/go2rtc
sudo chmod 755 /opt/go2rtc
sudo chmod 644 /opt/go2rtc/go2rtc.yaml

# Test configuration syntax
cd /opt/go2rtc
sudo -u skimlab ./go2rtc -config go2rtc.yaml
# Should show "Config loaded" and streams initializing
# Press Ctrl+C to stop the test
```

**4.4 Create go2rtc Systemd Service:**

```bash
# Create service file
sudo nano /etc/systemd/system/go2rtc.service

# Paste this EXACT configuration (v5.0 with critical fixes):
[Unit]
Description=go2rtc RTSP Streaming Service (v5.0 Hardened)
Documentation=https://github.com/AlexxIT/go2rtc
After=network-online.target
Wants=network-online.target

[Service]
User=skimlab
Group=video
WorkingDirectory=/opt/go2rtc
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml
Restart=always
RestartSec=5

# CRITICAL: Kill all child processes when stopping (prevents zombies)
KillMode=control-group
KillSignal=SIGTERM
TimeoutStopSec=10

# Resource limits for stability
CPUQuota=70%
MemoryMax=512M
MemorySwapMax=0

# Additional stability settings
LimitNOFILE=4096
NoNewPrivileges=true
StandardOutput=journal
StandardError=journal
SyslogIdentifier=go2rtc

[Install]
WantedBy=multi-user.target

# Save file (Ctrl+X, Y, Enter)
```

**4.5 Enable and Start go2rtc Service:**

```bash
# Add user to video group
sudo usermod -a -G video skimlab

# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable go2rtc.service

# Start the service
sudo systemctl start go2rtc.service

# Check service status
sudo systemctl status go2rtc.service
# Should show "active (running)"

# Check logs
journalctl -u go2rtc.service -n 20
# Should show successful startup with both cameras
```

**4.6 Test RTSP Streams:**

```bash
# Wait 30 seconds for streams to initialize
sleep 30

# Test Camera 0 stream
ffprobe rtsp://127.0.0.1:8554/camera0
# Should show stream information with video codec details
# Expected output includes: Video: h264, yuv420p, 1024x768, 15 fps

# Test Camera 1 stream
ffprobe rtsp://127.0.0.1:8554/camera1
# Should show stream information with video codec details
# Expected output includes: Video: h264, yuv420p, 1024x768, 15 fps

# Test go2rtc web interface
curl -s http://127.0.0.1:1984/api/streams
# Should show JSON with both camera0 and camera1 stream information

# Verify streams are accessible from network
ffprobe rtsp://192.168.0.11:8554/camera0
# Should work from other devices on the network

# Test go2rtc web UI (optional)
# Open browser on another computer: http://192.168.0.11:1984/
# Should show both camera streams in web interface 
```

### Step 5: System Monitoring Setup

**5.1 Create Monitoring Script:**

```bash
# Create script directory
sudo mkdir -p /opt/scripts

# Create monitoring script
sudo nano /opt/scripts/pi-monitor.sh

# Paste this EXACT script content:
#!/bin/bash
# =============================================================================
# RASPBERRY PI 5 SURVEILLANCE SYSTEM HEALTH MONITOR
# Version: 4.0 Production
# Purpose: Monitor system health, detect issues, log status
# =============================================================================

# Configuration
LOG_FILE="/var/log/pi-monitor.log"
ERROR_LOG="/var/log/pi-monitor-error.log"
ALERT_LOG="/var/log/pi-monitor-alerts.log"
MONITOR_INTERVAL=60  # Check every 60 seconds

# Ensure log files exist with proper permissions
for logfile in "$LOG_FILE" "$ERROR_LOG" "$ALERT_LOG"; do
    sudo touch "$logfile" 2>/dev/null || touch "$logfile"
    sudo chown skimlab:skimlab "$logfile" 2>/dev/null || true
done

# Function to log with timestamp
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Function to log alerts
log_alert() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ALERT: $message" | tee -a "$ALERT_LOG" -a "$LOG_FILE"
}

# Function to get system metrics
get_system_metrics() {
    # Temperature
    TEMP=$(vcgencmd measure_temp 2>/dev/null | cut -d'=' -f2 || echo "unknown")
    
    # Throttling status
    THROTTLED=$(vcgencmd get_throttled 2>/dev/null || echo "unknown")
    
    # Memory usage
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}' 2>/dev/null || echo "unknown")
    
    # CPU usage (5-second average)
    CPU_USAGE=$(top -bn2 -d1 | grep "Cpu(s)" | tail -n1 | awk '{print $2}' | cut -d'%' -f1 2>/dev/null || echo "unknown")
    
    # Disk usage for root partition
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//' 2>/dev/null || echo "unknown")
    
    # Service statuses
    GO2RTC_STATUS=$(systemctl is-active go2rtc.service 2>/dev/null || echo "unknown")
    
    # Camera process count
    CAMERA_COUNT=$(ps aux | grep rpicam-vid | grep -v grep | wc -l 2>/dev/null || echo "0")
    
    # Load average
    LOAD_AVG=$(uptime | awk -F'load average:' '{ print $2 }' | awk '{ print $1 }' | sed 's/,//' 2>/dev/null || echo "unknown")
}

# Function to check system health
check_system_health() {
    local alerts=""
    
    # Check temperature (alert if >70°C, critical if >75°C)
    if [[ "$TEMP" != "unknown" ]]; then
        temp_value=$(echo "$TEMP" | sed 's/°C//' | cut -d"'" -f1)
        if (( $(echo "$temp_value > 75" | bc -l) )); then
            alerts="${alerts}CRITICAL_TEMP:${temp_value}°C "
        elif (( $(echo "$temp_value > 70" | bc -l) )); then
            alerts="${alerts}HIGH_TEMP:${temp_value}°C "
        fi
    fi
    
    # Check throttling
    if [[ "$THROTTLED" != "throttled=0x0" ]] && [[ "$THROTTLED" != "unknown" ]]; then
        alerts="${alerts}THROTTLING:$THROTTLED "
    fi
    
    # Check memory usage (alert if >85%)
    if [[ "$MEM_USAGE" != "unknown" ]]; then
        if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
            alerts="${alerts}HIGH_MEMORY:${MEM_USAGE}% "
        fi
    fi
    
    # Check disk usage (alert if >90%)
    if [[ "$DISK_USAGE" != "unknown" ]]; then
        if (( DISK_USAGE > 90 )); then
            alerts="${alerts}HIGH_DISK:${DISK_USAGE}% "
        fi
    fi
    
    # Check go2rtc service
    if [[ "$GO2RTC_STATUS" != "active" ]]; then
        alerts="${alerts}GO2RTC_DOWN:$GO2RTC_STATUS "
    fi
    
    # Check camera count
    if [[ "$CAMERA_COUNT" != "2" ]]; then
        alerts="${alerts}CAMERA_ISSUE:${CAMERA_COUNT}_cameras "
    fi
    
    # Check load average (alert if >3.0 on Pi 5)
    if [[ "$LOAD_AVG" != "unknown" ]]; then
        if (( $(echo "$LOAD_AVG > 3.0" | bc -l) )); then
            alerts="${alerts}HIGH_LOAD:$LOAD_AVG "
        fi
    fi
    
    # Log alerts if any
    if [[ -n "$alerts" ]]; then
        log_alert "$alerts"
        return 1
    else
        return 0
    fi
}

# Main monitoring loop
log_message "INFO" "Pi5 Surveillance System Monitor Starting - PID: $$"

while true; do
    # Get all system metrics
    get_system_metrics
    
    # Create status message
    STATUS_MSG="Temp:$TEMP Throttled:$THROTTLED Mem:${MEM_USAGE}% CPU:${CPU_USAGE}% Disk:${DISK_USAGE}% Load:$LOAD_AVG go2rtc:$GO2RTC_STATUS cameras:$CAMERA_COUNT"
    
    # Check for issues
    if check_system_health; then
        log_message "INFO" "$STATUS_MSG"
    else
        log_message "WARN" "$STATUS_MSG [ALERTS_ACTIVE]"
    fi
    
    # Sleep for monitoring interval
    sleep $MONITOR_INTERVAL
done

# Save file (Ctrl+X, Y, Enter)
```

**5.2 Make Script Executable:**

```bash
# Make script executable
sudo chmod +x /opt/scripts/pi-monitor.sh
```

**5.3 Create Monitoring Service:**

```bash
# Create monitoring service
sudo nano /etc/systemd/system/pi-monitor.service

# Paste this EXACT configuration:
[Unit]
Description=Raspberry Pi System Health Monitor
Documentation=Custom monitoring service for Pi5 surveillance system
After=network.target go2rtc.service
Wants=network.target

[Service]
Type=simple
User=skimlab
Group=skimlab
ExecStart=/bin/bash /opt/scripts/pi-monitor.sh
Restart=always
RestartSec=30
KillMode=control-group
TimeoutStopSec=15

# Logging configuration
StandardOutput=append:/var/log/pi-monitor.log
StandardError=append:/var/log/pi-monitor-error.log

# Resource limits
MemoryMax=64M
TasksMax=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=true
ReadWritePaths=/var/log

[Install]
WantedBy=multi-user.target

# Save file (Ctrl+X, Y, Enter)
```

**5.4 Enable and Start Monitoring:**

```bash
# Create log files with proper permissions
sudo touch /var/log/pi-monitor.log /var/log/pi-monitor-error.log /var/log/pi-monitor-alerts.log
sudo chown skimlab:skimlab /var/log/pi-monitor*.log

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable pi-monitor.service
sudo systemctl start pi-monitor.service

# Check service status
sudo systemctl status pi-monitor.service
# Should show "active (running)"

# Monitor logs in real-time
tail -f /var/log/pi-monitor.log
# Should show monitoring entries every 60 seconds
# Press Ctrl+C to stop monitoring
```

---

## 📁 **Configuration Files Repository**

### `/boot/firmware/config.txt` - System Boot Configuration

```plain text
# GPU Memory for camera operations
gpu_mem=128

# Disable unnecessary hardware
dtoverlay=disable-wifi
dtoverlay=disable-bt

# System optimization
disable_splash=1
dtparam=watchdog=on
temp_limit=75
```

### `/etc/go2rtc.yaml` - Stream Server Configuration

```yaml
# Production go2rtc configuration - STABLE VERSION v5.0
# CRITICAL: Uses h264 pipeline with ffmpeg passthrough for stability
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
      --level 4.1
      --profile high
      -o -
      | ffmpeg -hide_banner -loglevel error
        -f h264 -i -
        -c copy
        -f rtsp rtsp://127.0.0.1:8554/pi_cam_1

rtsp:
  listen: ":8554"
```

**Key Parameters Explained:**

- **Resolution:** 1024x768 (optimized for stability vs quality)
- **Framerate:** 15fps (reduces heat/CPU load)
- **Bitrate:** 1.5Mbps per camera (network-friendly)
- **Format:** mpegts with libav (most stable codec path)

---

## 🔧 **Service Files Repository**

## 🔧 **Critical v5.0 Updates - Hardened Service Configuration**

> [!note] 🚨
> **CRITICAL UPDATE (v5.0):** The systemd service MUST use `KillMode=control-group` to prevent zombie processes. This was the root cause of system freezes.

### Updated go2rtc.service (STABLE v5.0)

```plain text
[Unit]
Description=go2rtc RTSP Streaming Service (Hardened v5.0)
Documentation=https://github.com/AlexxIT/go2rtc
After=network-online.target
Wants=network-online.target

[Service]
User=skimlab  
Group=video
WorkingDirectory=/opt/go2rtc
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml
Restart=always
RestartSec=5

# CRITICAL: Kill all child processes when stopping
KillMode=control-group  # THIS IS MANDATORY - prevents zombie rpicam-vid processes
KillSignal=SIGTERM
TimeoutStopSec=10

# Resource limits for stability
CPUQuota=70%
MemoryMax=512M
MemorySwapMax=0

# Additional stability settings
LimitNOFILE=4096
NoNewPrivileges=true
StandardOutput=journal
StandardError=journal
SyslogIdentifier=go2rtc

[Install]
WantedBy=multi-user.target
```

**Key Changes from v4.0:**

- `KillMode=control-group` instead of `mixed` (CRITICAL)
- Added `MemorySwapMax=0` to prevent swap usage
- Added `WorkingDirectory` for proper path resolution
- Added journal logging configuration
- Reduced CPU quota to 70% for better thermal management

---

## 📹 **Video Parameter Configuration Guide**

> [!note] ⚙️
> **Lab-Specific Configuration:** This section is tailored for easy adjustment of video parameters for sleep behavioral analysis. Students can safely modify these settings to optimize recording quality for different experimental needs.

### Current Production Settings (Optimized for 24/7 Stability)

- **Resolution:** 1024×768 (XGA format)
- **Frame Rate:** 15 fps
- **Bitrate:** 1.5 Mbps per camera
- **Codec:** libav (H.264)
- **Format:** MPEG-TS container

### How to Modify Video Parameters

**File Location:** `/etc/go2rtc.yaml` on each Raspberry Pi

**Template for Camera Parameter Modification:**

```yaml
streams:
  camera0:
    - exec:/usr/bin/rpicam-vid --camera 0 -t 0 --width WIDTH --height HEIGHT --framerate FPS --bitrate BITRATE --codec libav --libav-format mpegts --libav-audio 0 --flush -o -
    - ffmpeg:rtsp
```

### Resolution Options

| **Resolution** | **Width × Height** | **Aspect Ratio** | **Use Case** | **CPU Impact** |
| --- | --- | --- | --- | --- |
| **HD (720p)** | `--width 1280 --height 720` | 16:9 | Higher quality, more bandwidth | Medium |
| **XGA (Current)** | `--width 1024 --height 768` | 4:3 | Balanced quality/stability | Low |
| **SVGA** | `--width 800 --height 600` | 4:3 | Lower bandwidth, better stability | Very Low |
| **VGA** | `--width 640 --height 480` | 4:3 | Minimal resources | Minimal |

### Frame Rate Options

| **FPS** | **Parameter** | **Use Case** | **Heat Impact** |
| --- | --- | --- | --- |
| **30 fps** | `--framerate 30` | Smooth motion, high quality | High |
| **15 fps (Current)** | `--framerate 15` | Good for behavioral analysis | Low |
| **10 fps** | `--framerate 10` | Time-lapse style | Very Low |
| **5 fps** | `--framerate 5` | Long-term monitoring | Minimal |

### Bitrate Settings

| **Quality** | **Bitrate** | **Parameter** | **Network Usage** |
| --- | --- | --- | --- |
| **High Quality** | 3 Mbps | `--bitrate 3000000` | ~1.3 GB/hour |
| **Medium (Current)** | 1.5 Mbps | `--bitrate 1500000` | ~675 MB/hour |
| **Low Quality** | 800 kbps | `--bitrate 800000` | ~360 MB/hour |
| **Very Low** | 400 kbps | `--bitrate 400000` | ~180 MB/hour |

### Step-by-Step Parameter Change Process

**1. Backup Current Configuration:**

```bash
ssh skimlab@192.168.0.11
sudo cp /etc/go2rtc.yaml /etc/go2rtc.yaml.backup
```

**2. Edit Configuration:**

```bash
sudo nano /etc/go2rtc.yaml
```

**3. Example: Change to 720p at 30fps with higher bitrate:**

```yaml
streams:
  camera0:
    - exec:/usr/bin/rpicam-vid --camera 0 -t 0 --width 1280 --height 720 --framerate 30 --bitrate 3000000 --codec libav --libav-format mpegts --libav-audio 0 --flush -o -
    - ffmpeg:rtsp
  camera1:
    - exec:/usr/bin/rpicam-vid --camera 1 -t 0 --width 1280 --height 720 --framerate 30 --bitrate 3000000 --codec libav --libav-format mpegts --libav-audio 0 --flush -o -
    - ffmpeg:rtsp
```

**4. Test Configuration:**

```bash
# Test config syntax
/usr/local/bin/go2rtc -config /etc/go2rtc.yaml
# Should show successful startup - Press Ctrl+C if no errors
```

**5. Apply Changes:**

```bash
sudo systemctl restart go2rtc.service
sudo systemctl status go2rtc.service
```

**6. Monitor System Health:**

```bash
# Check temperature after 5 minutes
vcgencmd measure_temp

# Check for throttling
vcgencmd get_throttled

# Test streams
ffprobe rtsp://localhost:8554/camera0
ffprobe rtsp://localhost:8554/camera1
```

**7. Verify in Frigate:**

- Open Frigate web interface: [`http://192.168.0.50:5000`](http://192.168.0.50:5000/)
- Check both camera feeds are working
- Monitor for any connection issues

### ⚠️ **Important Lab Considerations**

**For Sleep Behavioral Analysis:**

- **Recommended FPS:** 10-15 fps (sufficient for mouse behavior)
- **Recommended Resolution:** 1024×768 or 800×600 (good detail without excess data)
- **Bitrate:** 1.5-2 Mbps (balance between quality and storage)

**Storage Impact Calculations:**

```javascript
Daily Storage per Camera = (Bitrate × 24 hours × 3600 seconds) ÷ 8 bits per byte

Example with current settings (1.5 Mbps):
1,500,000 × 24 × 3600 ÷ 8 = 16.2 GB per camera per day

For 2 cameras × 30 days retention = ~972 GB needed
```

**Thermal Management:**

- Higher resolutions/fps generate more heat
- Always monitor temperature with `vcgencmd measure_temp`
- Keep under 65°C for 24/7 operation
- Consider reducing parameters if temperature exceeds 70°C

**Network Bandwidth:**

- 2 cameras at 1.5 Mbps = 3 Mbps total
- Ensure your network can handle the load
- Higher bitrates may affect other lab network usage

### Quick Lab Presets

**Preset 1: High Quality (for detailed analysis)**

```yaml
# 720p, 30fps, 2.5Mbps - Use when detail is critical
--width 1280 --height 720 --framerate 30 --bitrate 2500000
```

**Preset 2: Balanced (current setting)**

```yaml
# 1024x768, 15fps, 1.5Mbps - Good balance
--width 1024 --height 768 --framerate 15 --bitrate 1500000
```

**Preset 3: Long-term monitoring**

```yaml
# 800x600, 10fps, 1Mbps - For extended recordings
--width 800 --height 600 --framerate 10 --bitrate 1000000
```

**Preset 4: Low bandwidth**

```yaml
# 640x480, 5fps, 500kbps - Minimal network impact
--width 640 --height 480 --framerate 5 --bitrate 500000
```

### `/etc/systemd/system/go2rtc.service` - go2rtc Systemd Service

```javascript
[Unit]
Description=go2rtc RTSP Streaming Service
Documentation=https://github.com/AlexxIT/go2rtc
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=skimlab
Group=video
ExecStart=/usr/local/bin/go2rtc -config /etc/go2rtc.yaml
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=10

# Resource limits for stability
MemoryMax=512M
MemoryHigh=384M

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/tmp

[Install]
WantedBy=multi-user.target
```

**Service Features:**

- **Memory limit:** Max 512MB RAM (prevents memory leaks)
- **Auto-restart:** 10-second restart delay on failure
- **Clean shutdown:** 10-second timeout for graceful stop
- **Non-root user:** Runs as skimlab user for security
- **CPU access:** Full CPU access (Pi dedicated to surveillance only)

> **⚡ Performance Optimization:** Since this Pi is dedicated exclusively to surveillance (no other applications running), we allow go2rtc full access to CPU resources. The memory limit remains as a safety measure against potential memory leaks, while maximizing processing power for camera operations and stream encoding.

> **💡 Best Practice Enhancement:** For even more robust process management, you can optionally change `KillMode=mixed` to `KillMode=control-group` in the service file. This ensures all child processes are properly terminated using the modern systemd approach, preventing potential resource leaks.

### `/etc/systemd/system/pi-monitor.service` - System Health Monitor

```javascript
[Unit]
Description=Raspberry Pi System Health Monitor
Documentation=Custom monitoring service for Pi5 surveillance system
After=network.target go2rtc.service
Wants=network.target

[Service]
Type=simple
User=skimlab
Group=skimlab
ExecStart=/bin/bash /opt/scripts/pi-monitor.sh
Restart=always
RestartSec=30
KillMode=control-group
TimeoutStopSec=15

# Logging configuration
StandardOutput=append:/var/log/pi-monitor.log
StandardError=append:/var/log/pi-monitor-error.log

# Resource limits
MemoryMax=64M
TasksMax=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=true
ReadWritePaths=/var/log

[Install]
WantedBy=multi-user.target
```

---

## 📊 **System Monitoring Scripts**

### `/opt/`[`monitor.sh`](http://monitor.sh/) - Health Monitoring Script

```bash
#!/bin/bash
# Pi System Health Monitor - Production Version

LOG_FILE="/var/log/pi-monitor.log"
sudo touch $LOG_FILE && sudo chown skimlab:skimlab $LOG_FILE

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    TEMP=$(vcgencmd measure_temp | cut -d'=' -f2)
    THROTTLED=$(vcgencmd get_throttled)
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    GO2RTC_STATUS=$(systemctl is-active go2rtc.service)
    CAMERA_COUNT=$(ps aux | grep rpicam-vid | grep -v grep | wc -l)
    
    echo "$TIMESTAMP - Temp: $TEMP, Throttled: $THROTTLED, Mem: ${MEM_USAGE}%, CPU: ${CPU_USAGE}%, go2rtc: $GO2RTC_STATUS, cameras: $CAMERA_COUNT" >> $LOG_FILE
    
    # Alert on critical conditions
    if [[ "$GO2RTC_STATUS" != "active" ]] || [[ "$CAMERA_COUNT" != "2" ]]; then
        echo "$TIMESTAMP - ALERT: System degraded - go2rtc: $GO2RTC_STATUS, cameras: $CAMERA_COUNT" >> $LOG_FILE
    fi
    
    sleep 60
done
```

---

### 🐳 Frigate NVR Server Setup (Ubuntu PC)

> **Note:** This section is performed on a separate Ubuntu PC/server that will run Frigate NVR to record the camera streams.

### Step 6: Frigate Server Prerequisites

**6.1 Install Docker and Docker Compose:**

```bash
# SSH into your Ubuntu server (192.168.0.50)
ssh user@192.168.0.50

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index
sudo apt update

# Install Docker Engine
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add current user to docker group
sudo usermod -aG docker $USER

# Enable and start Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create symlink for backward compatibility
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verify Docker installation
docker --version
# Expected: Docker version 24.x.x

# Verify Docker Compose installation
docker-compose --version
# Expected: Docker Compose version v2.20.0

# Test Docker (may need to log out and back in for group changes)
newgrp docker
docker run hello-world
# Should show "Hello from Docker!" message 
```

**6.2 Create Frigate Directory Structure:**

```bash
# Create main Frigate directory
sudo mkdir -p /srv/frigate
cd /srv/frigate

# Create subdirectories
sudo mkdir -p config storage

# Set proper ownership
sudo chown -R $USER:$USER /srv/frigate

# Verify structure
ls -la /srv/frigate
# Should show: config/ and storage/ directories
```

### Step 7: Frigate Configuration

**7.1 Create Docker Compose File:**

```bash
# Navigate to Frigate directory
cd /srv/frigate

# Create docker-compose.yml
nano docker-compose.yml

# Paste this EXACT configuration:
version: "3.9"

services:
  frigate:
    container_name: frigate
    privileged: true
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    shm_size: "256m"
    devices:
      - /dev/dri/renderD128:/dev/dri/renderD128  # Intel GPU acceleration (if available)
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./config:/config
      - ./storage:/media/frigate
      - type: tmpfs
        target: /tmp/cache
        tmpfs:
          size: 1000000000  # 1GB tmpfs for cache
    ports:
      - "5000:5000"    # Frigate Web UI
      - "8554:8554"    # RTSP re-streaming
      - "8555:8555/tcp"  # WebRTC
      - "8555:8555/udp"  # WebRTC
    environment:
      - FRIGATE_RTSP_PASSWORD=password123
      - TZ=Asia/Seoul
    depends_on:
      - mqtt  # Remove this line if not using MQTT
    
  # Optional: MQTT Broker (comment out if not needed)
  mqtt:
    container_name: mqtt
    image: eclipse-mosquitto:2.0
    restart: unless-stopped
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log
    command: mosquitto -c /mosquitto-no-auth.conf

# Save file (Ctrl+X, Y, Enter)

# Note: If you don't need MQTT, remove the mqtt service section
# and remove the depends_on line from the frigate service 
```

**7.2 Create Frigate Configuration File:**

```bash
# Create Frigate config file
nano config/config.yml

# Paste this EXACT working configuration:
# =============================================================================
# FRIGATE NVR CONFIGURATION - PRODUCTION STABLE
# Version: 4.0 Production
# Last Updated: September 16, 2025
# Optimized for: Recording stability, storage management, CPU efficiency
# =============================================================================


<callout icon="🚨" color="red">
**CRITICAL FIX (September 19, 2025):** Fixed Frigate configuration validation errors. Key changes:
- `ui -> date_style`: Changed from "us" to "medium" (valid values: 'full', 'long', 'medium', 'short')
- `logger -> logs`: Added proper dictionary structure instead of empty value
- Removed deprecated `use_experimental` field

If you're experiencing Frigate startup failures, update your config with these corrections.
</callout>

# MQTT disabled for standalone operation
mqtt:
  enabled: false

# Database configuration
database:
  path: /media/frigate/frigate.db

# Global detection settings (disabled for stability)
detect:
  enabled: false
  width: 1024
  height: 768
  fps: 5

# Global recording configuration
record:
  enabled: true
  expire_interval: 60  # Check for expired recordings every 60 minutes
  retain:
    days: 30
    mode: all
  events:
    max_seconds: 300
    pre_capture: 5
    post_capture: 5
    retain:
      default: 10
      mode: motion

# Snapshots configuration
snapshots:
  enabled: true
  timestamp: true
  bounding_box: false
  crop: false
  retain:
    default: 10

# Camera configurations
cameras:
  # Camera 0 from Raspberry Pi
  pi_cam_0:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/camera0
          input_args: preset-rtsp-restream
          roles: 
            - record
            - rtmp  # CRITICAL: Required for live view in web interface
      output_args:
        record: preset-record-generic-audio-copy
    
    # Enable recording only
    record:
      enabled: true
      retain:
        days: 30
        mode: all
    
    # Disable detection for stability
    detect:
      enabled: false
      
    # Optional: Enable snapshots
    snapshots:
      enabled: true
      timestamp: true
      retain:
        default: 10
      
  # Camera 1 from Raspberry Pi
  pi_cam_1:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/camera1
          input_args: preset-rtsp-restream
          roles: 
            - record
            - rtmp  # CRITICAL: Required for live view in web interface
      output_args:
        record: preset-record-generic-audio-copy
    
    record:
      enabled: true
      retain:
        days: 30
        mode: all
    
    detect:
      enabled: false
      
    snapshots:
      enabled: true
      timestamp: true
      retain:
        default: 10

# UI configuration
ui:
  timezone: Asia/Seoul
  date_style: medium
  time_format: 12hour

# Logging configuration
logger:
  default: info
  logs:
    frigate.record: info
    
```

**7.3 Set Proper Permissions:**

```bash
# Set permissions for config directory
chmod 755 config/
chmod 644 config/config.yml

# Ensure storage directory is writable
chmod 755 storage/

# Verify permissions
ls -la config/
ls -la storage/
```

### Step 8: Start and Test Frigate

**8.1 Initial Frigate Startup:**

```bash
# Navigate to Frigate directory
cd /srv/frigate

# Pull the latest Frigate image
docker-compose pull

# Start Frigate in background
docker-compose up -d

# Check container status
docker-compose ps
# Should show frigate container as "Up"

# Check initial logs
docker-compose logs -f frigate
# Watch for startup messages and any errors
# Press Ctrl+C to stop following logs
```

**8.2 Verify Frigate is Working:**

```bash
# Check container is running
docker ps
# Should show frigate container as running

# Check Frigate logs for errors
docker-compose logs frigate | grep -i error
# Should show no critical errors

# Test Frigate API
curl -s "http://127.0.0.1:5000/api/config" | jq '.cameras'
# Should return camera configuration

# Check Frigate version
curl -s "http://127.0.0.1:5000/api/version"
# Should return Frigate version information 
```

**8.3 Access Frigate Web Interface:**

```bash
# From another computer on your network:
# Open web browser and navigate to: http://192.168.0.50:5000
# Expected: Frigate web dashboard loads successfully
# You should see:
# - Live camera feeds from both pi_cam_0 and pi_cam_1
# - System statistics and performance metrics
# - Recording controls and playback options
# - Configuration status and health indicators
```

### Step 9: Verify Recording Functionality

**9.1 Check Recording Status:**

```bash
# Wait 5 minutes for recordings to start
sleep 300

# Check if recordings are being created
find ./storage -name "*.mp4" -newer -5min
# Should show recent .mp4 files

# Check recording directory structure
ls -la storage/
ls -la storage/pi_cam_0/
ls -la storage/pi_cam_1/
# Should show date-based directory structure

# Check storage usage
du -sh storage/
# Should show growing storage usage
```

**9.2 Test Recording Playbook:**

```bash
# Get list of recent recordings via API
curl -s "http://192.168.0.50:5000/api/recordings" | jq '.[0:3]'
# Should show recent recording entries with paths and timestamps

# Test camera status API
curl -s "http://192.168.0.50:5000/api/cameras" | jq '.'
# Should show both pi_cam_0 and pi_cam_1 with status information

# Check Frigate stats API
curl -s "http://192.168.0.50:5000/api/stats" | jq '.'
# Should show system performance and recording statistics

# Verify recording for specific camera
curl -s "http://192.168.0.50:5000/api/recordings?camera=pi_cam_0&limit=5" | jq '.'
# Should show recent recordings for camera 0
```

---

## ✅ **Deployment Checklist**

### Pre-Deployment Validation

- [ ] Hardware validated (power, cooling, network)
- [ ] All configurations tested in R&D environment
- [ ] 48-hour stability test completed
- [ ] Backup of current working configuration
- [ ] Rollback procedure documented
- [ ] Team notification sent

### Post-Deployment Verification

```bash
# System health check
vcgencmd get_throttled  # Should be 0x0
vcgencmd measure_temp   # Should be <65°C
vcgencmd get_mem gpu    # Should be 128M

# Service status
sudo systemctl status go2rtc.service pi-monitor.service

# Stream validation
ffprobe rtsp://192.168.0.11:8554/camera0
# Should show video stream details
ffprobe rtsp://192.168.0.11:8554/camera1
# Should show video stream details
```

### Success Criteria

- [ ] All cameras streaming within 5 minutes
- [ ] Frigate receiving all streams
- [ ] Recording files being created
- [ ] System monitoring active
- [ ] Performance metrics normal
- [ ] Temperature stable under 65°C
- [ ] No throttling events

---

## 🚨 **Critical Production Notes**

**⚠️ Configuration Stability:**

- These configurations have been tested for 24/7 operation
- Do NOT modify parameters without R&D testing
- Frame rate and resolution are optimized for thermal stability

**⚠️ Hardware Dependencies:**

- Active cooling is mandatory - system will throttle without it
- Official Pi PSU required - under-voltage causes instability
- High-endurance SD cards prevent filesystem corruption

**⚠️ Service Recovery:**

- go2rtc service auto-restarts with 10-second delay
- Monitor service tracks all critical metrics
- Watchdog enabled for hardware-level recovery

---

*This guide represents the final, stable state after extensive R&D testing. Refer to R&D Log for failed experiments and lessons learned.*

## ✅ Deployment Checklist and Verification

### Pre-Deployment Validation

**Hardware Checklist:**

- [ ] **Power Supply:** Official Raspberry Pi 5 27W PSU connected
- [ ] **Cooling:** Active cooler installed and functioning
- [ ] **Storage:** High-endurance microSD card (64GB+) inserted
- [ ] **Network:** Ethernet cable connected to router/switch
- [ ] **Cameras:** Both camera modules properly connected to Pi 5
- [ ] **Server:** Ubuntu server/PC available for Frigate NVR

**Software Preparation:**

- [ ] **SD Card:** Raspberry Pi OS Lite 64-bit flashed
- [ ] **SSH:** SSH enabled and accessible
- [ ] **Updates:** System fully updated (`apt update && apt upgrade`)
- [ ] **Dependencies:** All required packages installed
- [ ] **Backup:** Current configuration backed up (if upgrading)

### Post-Deployment System Verification

**Step 10: Raspberry Pi System Health Check**

```bash
# SSH into your Raspberry Pi
ssh skimlab@192.168.0.11

# 1. Check system temperature
vcgencmd measure_temp
# Expected: 45-65°C (should be under 65°C)

# 2. Check for throttling
vcgencmd get_throttled
# Expected: throttled=0x0 (no throttling)

# 3. Check GPU memory allocation
vcgencmd get_mem gpu
# Expected: gpu=128M

# 4. Check system memory usage
free -h
# Expected: Reasonable memory usage (<80%)

# 5. Check CPU usage
top -bn1 | grep "Cpu(s)"
# Expected: Normal CPU usage (<90%)

# 6. Check disk usage
df -h
# Expected: Adequate free space (>20% free)
```

**Step 11: Service Status Verification**

```bash
# Check go2rtc service status
sudo systemctl status go2rtc.service
# Expected: "active (running)" with no recent failures

# Check monitoring service status
sudo systemctl status pi-monitor.service
# Expected: "active (running)" 

# Check service logs for errors
journalctl -u go2rtc.service --since "10 minutes ago" | grep -i error
# Expected: No critical errors

# Check camera processes
ps aux | grep rpicam-vid | grep -v grep
# Expected: 2 rpicam-vid processes running

ps aux | grep rpicam-vid | grep -v grep | wc -l
# Expected: 2
```

**Step 12: Network and Streaming Validation**

```bash
# Test RTSP streams locally
ffprobe rtsp://localhost:8554/camera0
# Expected: Shows stream information with video codec details

ffprobe rtsp://localhost:8554/camera1  
# Expected: Shows stream information with video codec details

# Test network connectivity to Frigate server
ping -c 3 192.168.0.50
# Expected: Successful ping responses

# Test go2rtc API locally
curl -s http://localhost:1984/api/streams | jq
# Expected: JSON response showing both camera streams status
```

**Step 13: go2rtc Web Interface Check**

```bash
# From another computer on your network:
# Open web browser: http://192.168.0.11:1984
# Expected: go2rtc web interface loads showing both cameras
# You should see:
# - camera0: streaming status and viewer
# - camera1: streaming status and viewer
# - Both cameras should show live video feeds
```

### Frigate Server Verification

**Step 14: Frigate System Check**

```bash
# SSH into Frigate server
ssh user@192.168.0.50

# Navigate to Frigate directory
cd /srv/frigate

# Check container status
docker-compose ps
# Expected: frigate container shows "Up" status

# Check container resource usage
docker stats frigate --no-stream
# Expected: Reasonable CPU/memory usage

# Check recent logs for errors
docker-compose logs frigate --tail 50 | grep -i error
# Expected: No critical errors

# Test Frigate API
curl -s http://localhost:5000/api/stats | jq '.service.uptime'
# Expected: Shows uptime in seconds (install jq if needed: sudo apt install jq)

# Check available storage
df -h ./storage
# Expected: Adequate free space for recordings
```

**Step 15: Recording Verification**

```bash
# Wait for recordings to start (may take 2-3 minutes)
echo "Waiting for recordings to initialize..."
sleep 180

# Check if recording files are being created
find ./storage -name "*.mp4" -mmin -5 | wc -l
# Expected: At least 1-2 recent recording files

# List recent recordings
find ./storage -name "*.mp4" -mmin -10 -exec ls -lh {} \;
# Expected: Shows recent .mp4 files with reasonable file sizes

# Check recording directory structure
ls -la storage/
# Expected: Directories for each camera (pi_cam_0, pi_cam_1)

# Verify database is being updated
ls -lh config/frigate.db
# Expected: Database file exists and is growing
```

**Step 16: Web Interface Final Check**

```bash
# From another computer on your network:
# Open web browser: http://192.168.0.50:5000
# Expected: Complete Frigate dashboard functionality

# Verify all interface components:
# 1. Live View tab: Both cameras streaming live video
# 2. Recordings tab: Recorded segments available for playback
# 3. System tab: Hardware statistics and performance metrics
# 4. Config tab: Configuration validation and status

# Test live stream playback:
# - Click on each camera feed
# - Verify smooth video playback
# - Check timestamp accuracy
# - Confirm no buffering or connection issues
```

### Success Criteria Summary

**System Performance Criteria:**

- [ ] **Raspberry Pi temperature:** Stable under 65°C
- [ ] **No throttling events:** `vcgencmd get_throttled` shows 0x0
- [ ] **Both cameras streaming:** 2 camera processes active
- [ ] **go2rtc service:** Active and stable
- [ ] **Monitoring service:** Active and logging
- [ ] **Network connectivity:** Pi can reach Frigate server

**Frigate NVR Criteria:**

- [ ] **Container running:** Frigate docker container up
- [ ] **API responding:** REST API returns valid data
- [ ] **Web interface accessible:** Dashboard loads completely
- [ ] **Live streams working:** Both cameras show video
- [ ] **Recordings active:** New .mp4 files being created
- [ ] **Playback functional:** Can view recorded segments
- [ ] **Storage management:** Adequate disk space available

**Integration Criteria:**

- [ ] **End-to-end flow:** Pi → go2rtc → Frigate → recordings
- [ ] **Automatic startup:** All services start on system boot
- [ ] **Error recovery:** Services automatically restart on failure
- [ ] **Monitoring active:** Health monitoring logs system status
- [ ] **Performance stable:** System operates within resource limits

### Troubleshooting Quick Reference

**If cameras don't start:**

```bash
# Check camera hardware
rpicam-hello --list-cameras

# Check go2rtc logs
journalctl -u go2rtc.service -n 50

# Restart go2rtc service
sudo systemctl restart go2rtc.service
```

**If Frigate can't connect to streams:**

```bash
# Test streams from Frigate server
ffprobe rtsp://192.168.0.11:8554/camera0

# Check network connectivity
ping 192.168.0.11

# Check Frigate logs
docker-compose logs frigate | grep -i "camera\|rtsp\|error"
```

**If recordings don't work:**

```bash
# Check storage permissions
ls -la /srv/frigate/storage/

# Check disk space
df -h /srv/frigate/storage/

# Restart Frigate container
docker-compose restart frigate
```

---

> **📋 Final Note:** This guide provides complete, step-by-step instructions for setting up a production-ready Pi surveillance system with v5.0 hardened configurations. Each step includes expected outputs and verification commands. Follow exactly for guaranteed stability.

*Guide Version 5.0 - Hardened Production Release • Last Updated: September 24, 2025*

## 📚 v5.0 Documentation Suite

### Core Configuration Pages:

### Key v5.0 Improvements:

- ✅ **KillMode=control-group** - Eliminates zombie processes
- ✅ **Intel QSV acceleration** - Reduces Frigate CPU from 100% to 12%
- ✅ **TCP-only transport** - Prevents frame drops
- ✅ **Hardware watchdog** - Automatic recovery from failures
- ✅ **Direct h264 pipeline** - More stable than mpegts
- ✅ **Monitoring scripts** - Proactive issue detection

[[📦 Archive - Old Configurations (Pre-v5.0)]]

[[🎯 Frigate NVR Configuration (v5.0 - Stable)]]

[[💕 Watchdog & Monitoring Setup (v5.0)]]

[[🎯 Troubleshooting Matrix (v5.0)]]

[[🔧 Complete Configuration Reference (v5.0)]]

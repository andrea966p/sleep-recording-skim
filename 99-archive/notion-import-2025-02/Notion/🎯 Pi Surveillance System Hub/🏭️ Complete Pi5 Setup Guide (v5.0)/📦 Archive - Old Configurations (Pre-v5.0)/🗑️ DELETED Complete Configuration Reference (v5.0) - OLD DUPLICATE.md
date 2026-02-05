---

---
# 🔧 Complete Configuration Reference (v5.0)

*All critical configurations with detailed explanations*

## 📝 Complete go2rtc.service (CRITICAL v5.0)

```plain text
[Unit]
Description=go2rtc RTSP Streaming Service (v5.0 Hardened)
Documentation=https://github.com/AlexxIT/go2rtc
After=network-online.target
Wants=network-online.target

[Service]
# User configuration
User=skimlab
Group=video

# Working directory (REQUIRED for proper path resolution)
WorkingDirectory=/opt/go2rtc

# Start command
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml

# Restart policy
Restart=always
RestartSec=5

# CRITICAL: Process termination (v5.0 FIX - prevents zombie processes)
KillMode=control-group  # MANDATORY - kills all child processes
KillSignal=SIGTERM      # Send terminate signal first  
TimeoutStopSec=10       # Wait 10 seconds before force kill

# Resource limits (prevent runaway processes)
CPUQuota=70%            # Limit CPU to prevent thermal issues
MemoryMax=512M          # Cap memory usage
MemorySwapMax=0         # Disable swap for this service

# Security and stability
LimitNOFILE=4096        # Increase file descriptor limit
NoNewPrivileges=true    # Security hardening

# Logging configuration
StandardOutput=journal  # Send stdout to systemd journal
StandardError=journal   # Send stderr to systemd journal
SyslogIdentifier=go2rtc # Easy log filtering with journalctl

[Install]
WantedBy=multi-user.target
```

### 🔑 Critical Settings Explained:

### `KillMode=control-group` (MOST IMPORTANT)

- **Purpose**: Ensures ALL child processes (rpicam-vid) are killed when service stops
- **Why Critical**: Without this, rpicam-vid processes become zombies and freeze the system
- **v4.0 Bug**: Used `KillMode=mixed` which only killed main process
- **Result**: Prevents SSH hangs and system freezes after days of operation

### `WorkingDirectory=/opt/go2rtc`

- **Purpose**: Sets the working directory for relative path resolution
- **Why Critical**: go2rtc needs this to find config file properly
- **Without it**: Service may fail to start or find streams

### `CPUQuota=70%`

- **Purpose**: Limits CPU usage to prevent thermal throttling
- **Why 70%**: Leaves headroom for system processes and prevents overheating
- **Temperature Impact**: Keeps Pi under 65°C during continuous operation

### `MemoryMax=512M` & `MemorySwapMax=0`

- **Purpose**: Prevents memory leaks from crashing system
- **Why these values**: go2rtc typically uses 200-300MB, 512MB provides buffer
- **No Swap**: Prevents SD card wear from swap usage

## 📝 Complete pi-monitor.service

```plain text
[Unit]
Description=Raspberry Pi System Health Monitor
Documentation=Custom monitoring service for Pi5 surveillance system
After=network.target go2rtc.service

[Service]
Type=simple
User=skimlab
Group=skimlab

# Script execution
ExecStart=/opt/scripts/monitor.sh

# Restart policy
Restart=always
RestartSec=10

# Process management
KillMode=process
TimeoutStopSec=5

# Resource limits
CPUQuota=5%
MemoryMax=50M

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pi-monitor

[Install]
WantedBy=multi-user.target
```

## 📝 Complete [monitor.sh](http://monitor.sh/) Script

```bash
#!/bin/bash
# Pi System Health Monitor - v5.0 Production
# Purpose: Monitor system health and alert on issues

# Log file configuration
LOG_FILE="/var/log/pi-monitor.log"
ALERT_FILE="/var/log/pi-monitor-alerts.log"

# Thresholds
MAX_TEMP=70          # Alert if temperature exceeds 70°C
MAX_MEM_PERCENT=85   # Alert if memory usage exceeds 85%
MAX_CPU_PERCENT=90   # Alert if CPU usage exceeds 90%
EXPECTED_CAMERAS=2   # Expected number of camera processes

# Create log files if they don't exist
[[ ! -f "$LOG_FILE" ]] && sudo touch "$LOG_FILE" && sudo chown skimlab:skimlab "$LOG_FILE"
[[ ! -f "$ALERT_FILE" ]] && sudo touch "$ALERT_FILE" && sudo chown skimlab:skimlab "$ALERT_FILE"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Function to log alerts
log_alert() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $1"
    echo "$message" >> "$ALERT_FILE"
    echo "$message" >> "$LOG_FILE"
}

# Main monitoring loop
while true; do
    # Get system metrics
    TEMP=$(vcgencmd measure_temp | grep -o '[0-9]*' | head -1)
    THROTTLED=$(vcgencmd get_throttled | cut -d'=' -f2)
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d' ' -f2)
    GO2RTC_STATUS=$(systemctl is-active go2rtc.service)
    CAMERA_COUNT=$(ps aux | grep rpicam-vid | grep -v grep | wc -l)
    
    # Log current status
    log_message "Temp: ${TEMP}°C, Throttled: $THROTTLED, Mem: ${MEM_USAGE}%, CPU: ${CPU_USAGE}%, go2rtc: $GO2RTC_STATUS, Cameras: $CAMERA_COUNT/$EXPECTED_CAMERAS"
    
    # Check for critical conditions
    if [[ "$GO2RTC_STATUS" != "active" ]]; then
        log_alert "go2rtc service is not running! Status: $GO2RTC_STATUS"
        # Attempt recovery
        sudo systemctl restart go2rtc.service
        log_alert "Attempted go2rtc service restart"
    fi
    
    if [[ "$CAMERA_COUNT" -ne "$EXPECTED_CAMERAS" ]]; then
        log_alert "Camera count mismatch! Expected: $EXPECTED_CAMERAS, Found: $CAMERA_COUNT"
    fi
    
    if [[ "$TEMP" -gt "$MAX_TEMP" ]]; then
        log_alert "Temperature critical! Current: ${TEMP}°C, Max: ${MAX_TEMP}°C"
    fi
    
    if [[ "$THROTTLED" != "0x0" ]]; then
        log_alert "System throttling detected! Code: $THROTTLED"
    fi
    
    if (( $(echo "$MEM_USAGE > $MAX_MEM_PERCENT" | bc -l) )); then
        log_alert "Memory usage high! Current: ${MEM_USAGE}%, Max: ${MAX_MEM_PERCENT}%"
    fi
    
    # Check for zombie processes
    ZOMBIES=$(ps aux | grep defunct | grep -v grep | wc -l)
    if [[ "$ZOMBIES" -gt 0 ]]; then
        log_alert "Zombie processes detected: $ZOMBIES"
    fi
    
    # Sleep for 60 seconds
    sleep 60
done
```

## 📝 Complete boot configuration (/boot/firmware/config.txt)

```plain text
# =============================================================================
# RASPBERRY PI 5 SURVEILLANCE SYSTEM BOOT CONFIGURATION
# Version: 5.0 Production Hardened
# Last Updated: September 24, 2025
# =============================================================================

# GPU Memory allocation (required for camera operation)
gpu_mem=128              # 128MB for GPU (optimal for dual cameras)

# Disable unnecessary hardware (save power & reduce heat)
dtoverlay=disable-wifi   # WiFi not needed for wired operation
dtoverlay=disable-bt     # Bluetooth not used

# System optimization
disable_splash=1         # Faster boot without splash screen
dtparam=watchdog=on      # Enable hardware watchdog
temp_limit=75            # Throttle at 75°C to prevent damage

# Camera configuration (implicit)
# camera_auto_detect=1   # Default enabled, detects CSI cameras
# display_auto_detect=1  # Default enabled, but no display connected
```

## 📝 Complete go2rtc.yaml (v5.0 stable)

```yaml
# =============================================================================
# GO2RTC STREAMING SERVER CONFIGURATION  
# Version: 5.0 Production - Direct h264 pipeline
# Path: /opt/go2rtc/go2rtc.yaml
# =============================================================================

# Stream definitions
streams:
  # Camera 0 - Primary camera
  pi_cam_0:
    # Direct h264 pipeline (more stable than mpegts)
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
        
  # Camera 1 - Secondary camera  
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

# RTSP server configuration
rtsp:
  listen: ":8554"        # RTSP port

# API configuration
api:
  listen: ":1984"        # Web interface and API port

# Logging (optional)
log:
  level: info            # info, debug, trace
```

### 🔑 Pipeline Parameters Explained:

- `--codec libav`: Use hardware encoder
- `--libav-format h264`: Direct h264 output (NOT mpegts)
- `--inline`: Include SPS/PPS in stream
- `--timeout 0`: Run indefinitely
- `--level 4.1`: H.264 level for compatibility
- `--profile high`: Better compression
- `-o -`: Output to stdout
- `| ffmpeg ...`: Pipe to ffmpeg for RTSP wrapping
- `-f h264 -i -`: Input raw h264 from stdin
- `-c copy`: No re-encoding (passthrough)
- `-f rtsp`: Output as RTSP stream

## 📝 Version Comparison Table

| Setting | v4.0 (Broken) | v5.0 (Fixed) | Impact |
| --- | --- | --- | --- |
| KillMode | mixed | control-group | Prevents zombies |
| Pipeline | mpegts | h264 | More stable |
| CPU Limit | 100% | 70% | Prevents overheating |
| Working Dir | Missing | /opt/go2rtc | Proper paths |
| Memory Swap | Unlimited | 0 | No SD wear |
| Stream names | camera0/1 | pi_cam_0/1 | Consistency |
| Watchdog | Optional | Enabled | Auto-recovery |
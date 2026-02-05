---

---
# 💕 Watchdog & Monitoring Setup (v5.0)

> [!note] 🔒
> **STABILITY ASSURANCE:** Hardware watchdog and monitoring scripts ensure automatic recovery from any system issues.

## Hardware Watchdog Configuration

### Step 1: Install Watchdog Package

```bash
# Install watchdog daemon
sudo apt-get update
sudo apt-get install -y watchdog
```

### Step 2: Configure Watchdog

```bash
# Edit watchdog configuration
sudo nano /etc/watchdog.conf

# Uncomment/add these lines:
watchdog-device = /dev/watchdog
max-load-1 = 24
min-memory = 1
watchdog-timeout = 15
```

### Step 3: Configure Systemd Watchdog

```bash
# Edit system configuration
sudo nano /etc/systemd/system.conf

# Add or uncomment:
RuntimeWatchdogSec=30s
ShutdownWatchdogSec=10min
```

### Step 4: Enable Watchdog Service

```bash
sudo systemctl enable watchdog
sudo systemctl start watchdog
sudo systemctl status watchdog
```

## Monitoring Script ([watchdog.sh](http://watchdog.sh/))

Create this script on the Raspberry Pi:

```bash
#!/bin/bash
# Watchdog script for go2rtc stability
# Location: /home/skimlab/watchdog.sh

LOG_FILE="/home/skimlab/watchdog.log"
MAX_CPU=50
MAX_MEM_MB=600

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if go2rtc is running
if ! systemctl is-active --quiet go2rtc; then
    log_message "WARNING: go2rtc is not running, starting it..."
    sudo systemctl start go2rtc
    exit 0
fi

# Check CPU usage of rpicam-vid processes
for pid in $(pgrep rpicam-vid); do
    cpu_usage=$(ps -p $pid -o %cpu= | tr -d ' ')
    cpu_int=${cpu_usage%.*}
    
    if [ "$cpu_int" -gt "$MAX_CPU" ]; then
        log_message "WARNING: rpicam-vid PID $pid using $cpu_usage% CPU, restarting go2rtc..."
        sudo systemctl restart go2rtc
        break
    fi
done

# Check memory usage of go2rtc
go2rtc_pid=$(pgrep -x go2rtc)
if [ -n "$go2rtc_pid" ]; then
    mem_kb=$(ps -p $go2rtc_pid -o rss= | tr -d ' ')
    mem_mb=$((mem_kb / 1024))
    
    if [ "$mem_mb" -gt "$MAX_MEM_MB" ]; then
        log_message "WARNING: go2rtc using ${mem_mb}MB memory, restarting..."
        sudo systemctl restart go2rtc
    fi
fi

# Check if streams are accessible
if ! curl -s http://localhost:1984/api/streams > /dev/null 2>&1; then
    log_message "ERROR: go2rtc API not responding, restarting..."
    sudo systemctl restart go2rtc
fi
```

### Make Script Executable and Add to Crontab

```bash
# Make executable
chmod +x ~/watchdog.sh

# Test the script
./watchdog.sh

# Add to crontab (run every 5 minutes)
crontab -e

# Add these lines:
*/5 * * * * /home/skimlab/watchdog.sh
0 */4 * * * sudo systemctl restart go2rtc  # Safety restart every 4 hours
```

## Health Check Script

Create this on the Ubuntu/Frigate server:

```bash
#!/bin/bash
# Health check for entire surveillance system
# Location: /srv/frigate/health_check.sh

OUT_DIR="/srv/frigate/health"
mkdir -p "$OUT_DIR"
STAMP=$(date +%Y%m%d_%H%M%S)
OUT_FILE="$OUT_DIR/health_${STAMP}.log"

{
    echo "=== TIMESTAMP ==="
    date
    echo
    echo "=== SYSTEM LOAD ==="
    uptime
    echo
    echo "=== DOCKER STATS ==="
    docker stats frigate --no-stream
    echo
    echo "=== GPU USAGE ==="
    curl -s http://localhost:5000/api/stats | python3 -c 'import sys,json;d=json.load(sys.stdin);print(json.dumps(d.get("gpu_usages",{}),indent=2))'
    echo
    echo "=== FFMPEG PROCESSES ==="
    docker exec frigate ps aux | grep ffmpeg | wc -l
    echo
    echo "=== RECENT RECORDINGS ==="
    find /srv/frigate/storage/recordings -type f -mmin -10 | wc -l
    echo
    echo "=== PI TEMPERATURE ==="
    ssh -o ConnectTimeout=3 skimlab@192.168.0.11 "vcgencmd measure_temp"
} >> "$OUT_FILE"

echo "Health check saved to: $OUT_FILE"
```

### Schedule Health Checks

```bash
# On Ubuntu server
crontab -e

# Add:
*/15 * * * * /srv/frigate/health_check.sh
30 2 * * * find /srv/frigate/health -type f -mtime +14 -delete  # Clean old logs
```

## Validation Script

Complete system validation:

```bash
#!/bin/bash
# Full system validation
set -euo pipefail

PASS=()
FAIL=()

check() {
    local DESC="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        PASS+=("$DESC")
    else
        FAIL+=("$DESC")
    fi
}

echo "=== VALIDATING SYSTEM ==="

# Check Pi connectivity
check "Ping Pi" ping -c1 -W1 192.168.0.11

# Check RTSP streams
check "RTSP cam0" ffprobe -v error -rtsp_transport tcp rtsp://192.168.0.11:8554/pi_cam_0
check "RTSP cam1" ffprobe -v error -rtsp_transport tcp rtsp://192.168.0.11:8554/pi_cam_1

# Check Frigate
check "Frigate running" docker ps --filter name=frigate --format '{{.Names}}' | grep -q '^frigate$'
check "Frigate API" curl -sf http://localhost:5000/api/stats
check "QSV active" bash -c "curl -s http://localhost:5000/api/stats | grep -q 'intel-qsv'"

# Check recordings
check "Recent recordings" bash -c "find /srv/frigate/storage/recordings -type f -mmin -10 | head -1"

echo
echo "=== RESULTS ==="
for p in "${PASS[@]}"; do
    echo "[✅] $p"
done
for f in "${FAIL[@]}"; do
    echo "[❌] $f"
done

if [ "${#FAIL[@]}" -eq 0 ]; then
    echo
    echo "ALL CHECKS PASSED! System is healthy."
    exit 0
else
    echo
    echo "Some checks FAILED. Investigate above items."
    exit 1
fi
```

## Expected Monitoring Results

With proper monitoring in place:

- **Automatic recovery** from frozen processes
- **No more SSH freezes** on the Raspberry Pi
- **Continuous recording** without gaps
- **System health logs** every 15 minutes
- **Proactive restarts** before issues occur
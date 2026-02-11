---
tags: [infrastructure, raspberry-pi, watchdog, monitoring]
created: 2026-02-05
status: production
---

## Hardware Watchdog

### Enable in Boot Config

Already in [[golden-boot-config]]:
```ini
dtparam=watchdog=on
```

### Install Watchdog Package

```bash
sudo apt-get update
sudo apt-get install -y watchdog
```

### Configure `/etc/watchdog.conf`

```ini
watchdog-device = /dev/watchdog
max-load-1 = 24
min-memory = 1
watchdog-timeout = 15
```

### Configure Systemd Watchdog

Edit `/etc/systemd/system.conf`:
```ini
RuntimeWatchdogSec=30s
RebootWatchdogSec=10min
```

> [!tip] Parameter Name
> Older systemd versions use `RebootWatchdogSec` (shown commented as `#RebootWatchdogSec=10min` in the default file). Newer versions renamed it to `ShutdownWatchdogSec`. Both work — use whichever matches your system's default file.

### Enable Service

```bash
sudo systemctl enable watchdog
sudo systemctl start watchdog
```

---

## Monitoring Script

**Location:** `/home/skimlab/watchdog.sh`

```bash
#!/bin/bash
# Watchdog script for go2rtc stability

LOG_FILE="/home/skimlab/watchdog.log"
MAX_CPU=50
MAX_MEM_MB=600

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if go2rtc is running
if ! systemctl is-active --quiet go2rtc; then
    log_message "WARNING: go2rtc not running, starting..."
    sudo systemctl start go2rtc
    exit 0
fi

# Check CPU usage of rpicam-vid processes
for pid in $(pgrep rpicam-vid); do
    cpu_usage=$(ps -p $pid -o %cpu= | tr -d ' ')
    cpu_int=${cpu_usage%.*}

    if [ "$cpu_int" -gt "$MAX_CPU" ]; then
        log_message "WARNING: rpicam-vid PID $pid using $cpu_usage% CPU"
        sudo systemctl restart go2rtc
        break
    fi
done

# Check memory usage
go2rtc_pid=$(pgrep -x go2rtc)
if [ -n "$go2rtc_pid" ]; then
    mem_kb=$(ps -p $go2rtc_pid -o rss= | tr -d ' ')
    mem_mb=$((mem_kb / 1024))

    if [ "$mem_mb" -gt "$MAX_MEM_MB" ]; then
        log_message "WARNING: go2rtc using ${mem_mb}MB, restarting..."
        sudo systemctl restart go2rtc
    fi
fi

# Check API response
if ! curl -s http://localhost:1984/api/streams > /dev/null 2>&1; then
    log_message "ERROR: go2rtc API not responding, restarting..."
    sudo systemctl restart go2rtc
fi
```

### Setup Crontab

```bash
chmod +x ~/watchdog.sh

crontab -e
# Add:
*/5 * * * * /home/skimlab/watchdog.sh
```

> [!warning] No Periodic Restarts
> Do **NOT** add a periodic `systemctl restart go2rtc` cron job. Each restart kills camera streams for ~60 seconds (due to the `ExecStartPre=/bin/sleep 60` IR LED safety delay). This system runs **continuous 24/7 video recording** alongside EEG/EMG data acquisition — any stream gap means lost experimental data that cannot be recovered. Crash recovery is already handled by systemd `Restart=always`, and the monitoring script above handles anomalous conditions.

---

## Quick Health Check

```bash
echo "Temperature: $(vcgencmd measure_temp)"
echo "Throttled: $(vcgencmd get_throttled)"
echo "go2rtc: $(systemctl is-active go2rtc)"
echo "Cameras: $(ps aux | grep rpicam-vid | grep -v grep | wc -l)/2"
echo "Memory: $(free -h | grep Mem | awk '{print $3"/"$2}')"
```

## Related

- [[golden-systemd-service]] - Service configuration
- [[golden-boot-config]] - Boot hardening

---

## Notes

- The monitoring script (`watchdog.sh`) only restarts go2rtc when something is actually wrong — it does not do blind periodic restarts
- Hardware watchdog (`/dev/watchdog`) only reboots the Pi on kernel hangs — video is already lost in that scenario, so a reboot is the correct recovery
- systemd `Restart=always` in the go2rtc service handles process crashes automatically

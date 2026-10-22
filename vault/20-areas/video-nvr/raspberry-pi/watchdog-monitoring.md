---
type: reference
area: video-nvr
status: active
tags: [infrastructure, raspberry-pi, watchdog, monitoring]
created: 2026-02-05
---

# Pi Hardware Watchdog & Monitoring

> [!abstract] TL;DR — for non-technical readers
> **What this is.** How each Raspberry Pi 5 self-recovers from a kernel hang via the BCM2712 hardware watchdog, managed by systemd.
>
> **Why it exists.** The Pi 5 has a hardware watchdog timer. If systemd stops feeding it (e.g. kernel hang), the chip resets the board after ~15 seconds. Without this, a hung Pi requires a physical reset trip to the lab.
>
> **How to read this page.** Skim "Hardware Watchdog (systemd)" — the configuration is two lines, and the test is to forcibly hang the kernel and confirm reboot. The other sections explain when the watchdog has actually fired in production.

> [!quote] Paper-ready
> Each Raspberry Pi 5 camera node is monitored by the BCM2712 hardware watchdog (15-second timeout), driven by systemd's `RuntimeWatchdogSec=15` and enabled at boot via `dtparam=watchdog=on`. The Pi self-recovers from kernel hangs without operator intervention; observed recovery latency in production is ~12–18 seconds.

## Hardware Watchdog (systemd)

The hardware watchdog is managed by **systemd directly** — not the `watchdog` daemon package. systemd claims `/dev/watchdog` exclusively, so the two cannot run simultaneously.

### Enable in Boot Config

Already in [[golden-boot-config]]:
```ini
dtparam=watchdog=on
```

### Configure Systemd Watchdog

Edit `/etc/systemd/system.conf`, uncomment and set:
```ini
RuntimeWatchdogSec=30s
RebootWatchdogSec=10min
```

> [!tip] Parameter Name
> Older systemd versions use `RebootWatchdogSec` (shown commented as `#RebootWatchdogSec=10min` in the default file). Newer versions renamed it to `ShutdownWatchdogSec`. Both work — use whichever matches your system's default file.

Apply without reboot:
```bash
sudo systemctl daemon-reexec
```

> [!warning] Do NOT use the `watchdog` daemon package
> The `watchdog` apt package (`/usr/sbin/watchdog`) conflicts with systemd's built-in watchdog — both try to claim `/dev/watchdog`, resulting in `errno 16 (Device or resource busy)`. If installed, disable it:
> ```bash
> sudo systemctl stop watchdog
> sudo systemctl disable watchdog
> ```
> systemd's `RuntimeWatchdogSec` provides the same kernel-hang protection without the conflict.

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

## Known Issues

### VSCode Remote CPU Exhaustion

> [!danger] Critical Warning
> **DO NOT use VSCode Remote on the Pi camera node.** VSCode Remote's background file indexing (`rg --files`) consumes 300%+ CPU, starving system services and causing complete unresponsiveness.

**Symptoms:**
- Pi responds to ping but sshd refuses new connections
- All CPU cores at 100%
- Existing SSH sessions remain alive but system is unusable

**Cause:** VSCode Remote spawns recursive `rg` (ripgrep) processes for workspace indexing. Combined with dual camera software H.264 encoding, this exhausts all available CPU on the 4-core Pi 5.

**Solution:** Use lightweight editors only:
- Terminal editors: `nano`, `vim`
- Remote editing via MCP filesystem server (from another machine)
- Edit locally, deploy via `scp`/`rsync`

Full incident: [[2026-02-11-vscode-remote-cpu-exhaustion|VSCode Remote CPU Exhaustion]]

---

## NVR-Side Pi Health Monitor

**Location:** `/opt/neurosurveillance/pi-monitor.sh` (on ASUS NVR at `192.168.0.50`)
**Added:** 2026-02-27

A ping-based monitor that runs every 2 minutes via cron on the NVR. Detects Pi outages from the network side — critical since PoE power failures leave the Pi silently dead with no self-reporting capability.

```bash
#!/bin/bash
# Pi health monitor — runs on NVR, pings Raspberry Pi every 2 minutes via cron
# Cron entry: */2 * * * * /opt/neurosurveillance/pi-monitor.sh

PI_IP="192.168.0.11"
LOG="/opt/neurosurveillance/logs/pi-monitor.log"
STATE_FILE="/opt/neurosurveillance/logs/.pi-monitor-state"
MAX_LOG_SIZE=2097152  # 2MB

# Rotate log if too large
if [ -f "$LOG" ] && [ "$(stat -c%s "$LOG" 2>/dev/null)" -gt "$MAX_LOG_SIZE" ]; then
    mv "$LOG" "$LOG.old"
fi

# Read previous state (up/down)
PREV_STATE="up"
if [ -f "$STATE_FILE" ]; then
    PREV_STATE=$(cat "$STATE_FILE")
fi

# Ping check: 2 pings, 3 second timeout
if ping -c 2 -W 3 "$PI_IP" > /dev/null 2>&1; then
    CURR_STATE="up"
else
    CURR_STATE="down"
fi

TIMESTAMP="[$(date '+%Y-%m-%d %H:%M:%S')]"

# Log on state transitions + periodic down reminders
if [ "$CURR_STATE" = "down" ] && [ "$PREV_STATE" = "up" ]; then
    echo "$TIMESTAMP ALERT: Pi ($PI_IP) is UNREACHABLE" >> "$LOG"
elif [ "$CURR_STATE" = "down" ] && [ "$PREV_STATE" = "down" ]; then
    echo "$TIMESTAMP STILL DOWN: Pi ($PI_IP) remains unreachable" >> "$LOG"
elif [ "$CURR_STATE" = "up" ] && [ "$PREV_STATE" = "down" ]; then
    echo "$TIMESTAMP RECOVERED: Pi ($PI_IP) is reachable again" >> "$LOG"
fi

echo "$CURR_STATE" > "$STATE_FILE"
```

**Behavior:**
- Logs only on state transitions (up→down, down→up) and periodic down reminders
- No log spam when Pi is healthy (up→up = silent)
- State tracked in `/opt/neurosurveillance/logs/.pi-monitor-state`
- Log rotation at 2MB

**Cron entry** (NVR):
```bash
*/2 * * * * /opt/neurosurveillance/pi-monitor.sh
```

---

## Crash Canary

**Location:** `/home/skimlab/crash-canary.sh` (on Pi)

Logs system vitals every 30 seconds to catch the pre-crash state. Uses `printf` with key=value format for parseable output.

**Cron entries** (Pi):
```bash
* * * * * /home/skimlab/crash-canary.sh
* * * * * sleep 30 && /home/skimlab/crash-canary.sh
```

**Log format** (single line):
```
[2026-02-27 07:08:01] temp=47.7'C throttle=0x0 load=0.54 0.42 0.43 mem_free=7253M mem_avail=7624M go2rtc=active rpicam=2 rpicam_cpu= 16.5% 16.4% go2rtc_mem=27632kB oom_kills=0 uptime="up 2 days, 5 hours, 17 minutes"
```

**Log location:** `/home/skimlab/crash-canary.log` (5MB max, auto-rotates)

> [!info] Bug Fix (2026-02-27)
> Fixed two issues: (1) `OOM_KILLS` variable produced duplicate values due to `grep -c` exit code 1 when count=0 triggering the `|| echo 0` fallback, splitting the log line. (2) `uptime` field had no label. Both fixed by switching to `printf` format and using `|| true` instead of `|| echo 0`.

---

## Eeprom Power Configuration

**Applied:** 2026-02-19 (after 6-day PMIC latch-up incident)

| Setting | Value | Purpose |
|---------|-------|---------|
| `PSU_MAX_CURRENT` | `5000` | Tells PMIC the PoE HAT can deliver 5A |
| `POWER_OFF_ON_HALT` | `1` | On halt, cuts PMIC power — PoE auto-reboots |

**Verify:**
```bash
vcgencmd bootloader_config | grep -E "PSU_MAX|POWER_OFF"
```

> [!warning] Double-crash limitation
> The eeprom fix enables auto-reboot after a single power event. However, if the Pi crashes again during the reboot (e.g., PoE power still unstable), the PMIC enters latch-up and requires manual power cycle. See [[2026-02-24-pi-unreachable-no-route|Feb 24 incident]].

---

## Notes

- The monitoring script (`watchdog.sh`) only restarts go2rtc when something is actually wrong — it does not do blind periodic restarts
- Hardware watchdog (`/dev/watchdog`) only reboots the Pi on kernel hangs — video is already lost in that scenario, so a reboot is the correct recovery
- systemd `Restart=always` in the go2rtc service handles process crashes automatically
- NVR-side `pi-monitor.sh` catches outages that the Pi cannot self-report (PoE death, PMIC latch-up)

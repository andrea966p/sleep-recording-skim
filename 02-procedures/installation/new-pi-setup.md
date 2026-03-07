---
tags: [procedure, installation, raspberry-pi]
created: 2026-02-04
updated: 2026-03-07
status: production
---

# New Raspberry Pi Camera Node Setup

This procedure sets up a Raspberry Pi 5 as a dual-camera streaming node for the NeuroSurveillance system. It covers system hardening, go2rtc installation, PoE EEPROM configuration, monitoring scripts, and Frigate integration.

> [!tip] Template Procedure
> This guide is a template for deploying multiple Pi nodes. Replace the placeholder values below with the actual values for your specific Pi. After deployment, add the Pi's details to [[00-config/production-values|Production Values]].

## Per-Node Values

Fill in before starting:

| Variable | Value | Notes |
|----------|-------|-------|
| `{PI_IP}` | *(e.g. `192.168.0.12`)* | Static IP via DHCP reservation |
| `{PI_HOSTNAME}` | *(e.g. `pi2`)* | Set during OS flash |
| `{PI_USER}` | `skimlab` | Same across all nodes |
| `{CAM_0_NAME}` | *(e.g. `pi_cam_2`)* | Must be unique across all Pis |
| `{CAM_1_NAME}` | *(e.g. `pi_cam_3`)* | Must be unique across all Pis |

> [!warning] Unique Camera Stream Names
> Camera stream names must be globally unique. If Pi 1 uses `pi_cam_0`/`pi_cam_1`, the next Pi must use `pi_cam_2`/`pi_cam_3`, etc. These names propagate to Frigate config, MQTT topics, and session daemon camera mappings.

## Prerequisites Checklist

- [ ] Raspberry Pi 5 with official power supply or PoE HAT
- [ ] Raspberry Pi Camera Module(s) connected
- [ ] Ethernet cable connected (Cat6 recommended for PoE)
- [ ] Static IP assigned via DHCP reservation on router
- [ ] Raspberry Pi OS Lite 64-bit flashed to SD card (with hostname and SSH enabled)

---

## Part 1: Base System

### 1. Copy SSH Key (from NVR)

Run this on the **NVR** (`192.168.0.50`), not on the Pi:

```bash
ssh-copy-id {PI_USER}@{PI_IP}
```

Enter the password once. All future SSH connections will be key-based.

**Validation:**
```bash
ssh {PI_USER}@{PI_IP} 'hostname'
# Expected: {PI_HOSTNAME} (no password prompt)
```

### 2. Fix Terminal for Ghostty Users

If you use Ghostty terminal and get `Error opening terminal: xterm-ghostty` when running `nano` or other curses apps over SSH, add this permanently to the Pi's bashrc:

```bash
ssh {PI_USER}@{PI_IP} 'echo "export TERM=xterm-256color" >> ~/.bashrc'
```

Then reconnect for the fix to take effect.

### 3. System Update

SSH into the Pi and run:

```bash
sudo apt update && sudo apt full-upgrade -y
```

### 4. Install Dependencies

```bash
sudo apt install -y git curl wget ffmpeg
```

### 5. Install Camera Software

```bash
# Install FULL rpicam-apps (not lite — lite lacks libav codec)
sudo apt install -y rpicam-apps
```

**Validation:**
```bash
rpicam-vid --version
# Must show: libav:1
```

**Expected output:**
```
rpicam-apps capabilites: egl:1 qt:1 drm:1 libav:1
```

> [!warning] Critical Prerequisite
> The full `rpicam-apps` package is **required**. The `rpicam-apps-lite` package lacks libav codec support and will cause go2rtc to fail with "Unrecognised codec libav" error.

---

## Part 2: go2rtc Streaming

### 6. Download go2rtc

```bash
sudo mkdir -p /opt/go2rtc
cd /opt/go2rtc
sudo wget https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_arm64
sudo mv go2rtc_linux_arm64 go2rtc
sudo chmod +x go2rtc
sudo chown -R {PI_USER}:video /opt/go2rtc
```

**Validation:**
```bash
/opt/go2rtc/go2rtc --version
```

### 7. Create go2rtc Configuration

```bash
nano /opt/go2rtc/go2rtc.yaml
```

Paste the following, with your Pi's unique camera names (see [[01-infrastructure/raspberry-pi/golden-go2rtc-config|Golden go2rtc Config]] for reference):

```yaml
streams:
  {CAM_0_NAME}: "exec:rpicam-vid -n --codec libav --libav-format mpegts --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --intra 15 --timeout 0 --camera 0 --level 4.1 --profile high --low-latency --output -"
  {CAM_1_NAME}: "exec:rpicam-vid -n --codec libav --libav-format mpegts --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --intra 15 --timeout 0 --camera 1 --level 4.1 --profile high --low-latency --output -"

rtsp:
  listen: ":8554"

api:
  listen: ":1984"

log:
  level: info
```

> [!warning] Critical Encoding Rules
> - **H.264 only** — H.265 causes kernel panics on Pi 5
> - **MPEG-TS container** (`--libav-format mpegts`) — better framing and stream recovery than raw H.264
> - **Single-line exec strings** — YAML multi-line blocks break go2rtc parsing
> - **No ffmpeg pipes** — proven unstable for 24/7 operation

### 8. Create systemd Service

```bash
sudo nano /etc/systemd/system/go2rtc.service
```

Paste the following (identical across all Pis — see [[01-infrastructure/raspberry-pi/golden-systemd-service|Golden systemd Service]]):

```ini
[Unit]
Description=go2rtc RTSP Streaming Service (v5.0 Hardened)
Documentation=https://github.com/AlexxIT/go2rtc
After=network-online.target
Wants=network-online.target

[Service]
User=skimlab
Group=video
WorkingDirectory=/opt/go2rtc
# IR LED power spike prevention — wait for boot power draw to settle
ExecStartPre=/bin/sleep 60
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml

# Restart policy
Restart=always
RestartSec=5

# CRITICAL: Kills ALL child processes (rpicam-vid) when service stops
KillMode=control-group
KillSignal=SIGTERM
TimeoutStopSec=10

# Resource limits
CPUQuota=70%
MemoryMax=512M
MemorySwapMax=0

# Security
LimitNOFILE=4096
NoNewPrivileges=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=go2rtc

[Install]
WantedBy=multi-user.target
```

> [!warning] KillMode=control-group is MANDATORY
> Without it, `rpicam-vid` child processes become zombies on service restart, eventually causing system freezes.

### 9. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable go2rtc.service
sudo systemctl start go2rtc.service
```

**Validation:**
```bash
sudo systemctl status go2rtc.service
# Expected: active (running) in green

# Wait ~65 seconds (60s ExecStartPre + startup), then:
ps aux | grep rpicam-vid | grep -v grep | wc -l
# Expected: 2 (one per camera)

curl http://localhost:1984/api/streams
# Expected: JSON listing both camera streams
```

---

## Part 3: System Hardening

### 10. Harden Boot Configuration

```bash
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d)
sudo nano /boot/firmware/config.txt
```

Add these lines to the **end** of the file (see [[01-infrastructure/raspberry-pi/golden-boot-config|Golden Boot Config]]):

```ini
# ========================================
# SURVEILLANCE SYSTEM HARDENING
# ========================================

# Disable WiFi (using Ethernet only)
dtoverlay=disable-wifi

# Disable Bluetooth (not needed)
dtoverlay=disable-bt

# GPU memory for dual camera operation
# NOTE: Ignored on Pi 5 (uses dynamic allocation). Kept for Pi 4 compatibility.
gpu_mem=128

# Enable hardware watchdog (auto-reboot on freeze)
dtparam=watchdog=on
```

### 11. Configure EEPROM for PoE HAT

> [!warning] Required for PoE-Powered Pis
> Skip this step **only** if the Pi is powered by a standard USB-C power supply (not PoE). Without these settings, a PoE power glitch will brick the Pi until manually power-cycled. We lost Pi 1 for **6 days** due to this — see [[03-troubleshooting/incidents/2026-02-19-pmic-fault-poe-death|Feb 19 PMIC incident]].

```bash
sudo rpi-eeprom-config --edit
```

Add these lines:

```
PSU_MAX_CURRENT=5000
POWER_OFF_ON_HALT=1
```

| Setting | Purpose |
|---------|---------|
| `PSU_MAX_CURRENT=5000` | Tells the PMIC the PoE HAT can deliver 5A. Without this, the PMIC blocks reboot after a power glitch ("insufficient PSU"). |
| `POWER_OFF_ON_HALT=1` | On halt, fully cuts PMIC power. PoE then auto-restores power, rebooting the Pi automatically. |

> [!info] Double-Crash Limitation
> The EEPROM fix handles a single power event. If the Pi crashes again *during* the reboot (e.g. PoE still unstable), the PMIC enters latch-up and requires a manual power cycle. See [[03-troubleshooting/incidents/2026-02-24-pi-unreachable-no-route|Feb 24 incident]].

### 12. Configure systemd Hardware Watchdog

The hardware watchdog auto-reboots the Pi if the kernel hangs. It is managed by **systemd directly** — do NOT install the `watchdog` apt package (it conflicts).

```bash
sudo nano /etc/systemd/system.conf
```

Find and uncomment these lines (remove the leading `#`), setting them to:

```ini
RuntimeWatchdogSec=30s
RebootWatchdogSec=10min
```

Apply without reboot:

```bash
sudo systemctl daemon-reexec
```

**Validation:**
```bash
cat /sys/class/watchdog/watchdog0/state
# Expected: active
```

### 13. Reboot

```bash
sudo reboot
```

---

## Part 4: Monitoring Scripts

After rebooting and reconnecting via SSH, deploy the monitoring scripts. These run via cron and provide three layers of protection:

| Script | Runs on | Interval | Purpose |
|--------|---------|----------|---------|
| `watchdog.sh` | Pi | Every 5 min | Restarts go2rtc if CPU/memory anomaly or API unresponsive |
| `crash-canary.sh` | Pi | Every 30 sec | Logs system vitals to catch pre-crash state |
| `pi-monitor.sh` | NVR | Every 2 min | Pings Pi from network side — catches PoE death, PMIC latch-up |

### 14. Deploy watchdog.sh (on Pi)

This script monitors go2rtc health and restarts it only when something is actually wrong (high CPU, excessive memory, API not responding).

```bash
nano ~/watchdog.sh
```

Paste:

```bash
#!/bin/bash
# Watchdog script for go2rtc stability
# Cron entry: */5 * * * * /home/skimlab/watchdog.sh

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

Make executable and add to cron:

```bash
chmod +x ~/watchdog.sh

crontab -e
```

Add this line:

```
*/5 * * * * /home/skimlab/watchdog.sh
```

> [!warning] No Periodic Restarts
> Do **NOT** add a blind periodic `systemctl restart go2rtc` cron job. Each restart kills camera streams for ~60 seconds (due to the `ExecStartPre=/bin/sleep 60` IR LED delay). This system runs **continuous 24/7 recording** — any stream gap means lost experimental data.

### 15. Deploy crash-canary.sh (on Pi)

Logs system vitals every 30 seconds to catch the state just before a crash. Critical for post-mortem analysis when the Pi dies silently (PoE power loss).

```bash
nano ~/crash-canary.sh
```

Paste:

```bash
#!/bin/bash
# Crash canary — logs vitals every 30s to catch pre-crash state
# Cron entries:
#   * * * * * /home/skimlab/crash-canary.sh
#   * * * * * sleep 30 && /home/skimlab/crash-canary.sh

LOG="/home/skimlab/crash-canary.log"
MAX_SIZE=5242880  # 5MB max

# Rotate if too big
if [ -f "$LOG" ] && [ "$(stat -f%z "$LOG" 2>/dev/null || stat -c%s "$LOG")" -gt "$MAX_SIZE" ]; then
    mv "$LOG" "$LOG.old"
fi

TEMP=$(vcgencmd measure_temp | cut -d= -f2)
THROTTLE=$(vcgencmd get_throttled | cut -d= -f2)
UPTIME=$(uptime -p)
MEM_FREE=$(free -m | awk '/Mem:/{print $4}')
MEM_AVAIL=$(free -m | awk '/Mem:/{print $7}')
LOAD=$(cat /proc/loadavg | cut -d' ' -f1-3)
GO2RTC=$(systemctl is-active go2rtc)
RPICAM_COUNT=$(pgrep -c rpicam-vid 2>/dev/null || echo 0)
RPICAM_CPU=""
for pid in $(pgrep rpicam-vid); do
    cpu=$(ps -p $pid -o %cpu= 2>/dev/null | tr -d ' ')
    RPICAM_CPU="$RPICAM_CPU ${cpu}%"
done
GO2RTC_MEM=""
go2rtc_pid=$(pgrep -x go2rtc)
if [ -n "$go2rtc_pid" ]; then
    GO2RTC_MEM="$(ps -p $go2rtc_pid -o rss= | tr -d ' ')kB"
fi
OOM_KILLS=$(dmesg 2>/dev/null | grep -c "Out of memory" || true)
OOM_KILLS=${OOM_KILLS:-0}

printf "[%s] temp=%s throttle=%s load=%s mem_free=%sM mem_avail=%sM go2rtc=%s rpicam=%s rpicam_cpu=%s go2rtc_mem=%s oom_kills=%s uptime=\"%s\"\n" \
    "$(date '+%Y-%m-%d %H:%M:%S')" "$TEMP" "$THROTTLE" "$LOAD" "$MEM_FREE" "$MEM_AVAIL" "$GO2RTC" "$RPICAM_COUNT" "$RPICAM_CPU" "$GO2RTC_MEM" "$OOM_KILLS" "$UPTIME" >> "$LOG"
```

Make executable and add to cron:

```bash
chmod +x ~/crash-canary.sh

crontab -e
```

Add these two lines (runs every minute + 30-second offset = every 30 seconds):

```
* * * * * /home/skimlab/crash-canary.sh
* * * * * sleep 30 && /home/skimlab/crash-canary.sh
```

**Final crontab should look like:**

```
*/5 * * * * /home/skimlab/watchdog.sh
* * * * * /home/skimlab/crash-canary.sh
* * * * * sleep 30 && /home/skimlab/crash-canary.sh
```

**Validation (wait ~60 seconds, then):**

```bash
cat ~/crash-canary.log
# Expected: one or two log lines with vitals
```

**Example output:**
```
[2026-03-07 14:30:01] temp=47.7'C throttle=0x0 load=0.54 0.42 0.43 mem_free=7253M mem_avail=7624M go2rtc=active rpicam=2 rpicam_cpu= 16.5% 16.4% go2rtc_mem=27632kB oom_kills=0 uptime="up 5 minutes"
```

---

## Part 5: NVR Integration

These steps are run on the **NVR** (`192.168.0.50`), not on the Pi.

### 16. Post-Reboot Validation (from NVR)

```bash
# Verify SSH
ssh {PI_USER}@{PI_IP} 'hostname'

# Check streams via go2rtc API
curl -s http://{PI_IP}:1984/api/streams

# Test RTSP streams (grab 1 frame each)
curl -m 5 "http://{PI_IP}:1984/api/stream.mp4?src={CAM_0_NAME}" -o /dev/null && echo "cam0 OK"
curl -m 5 "http://{PI_IP}:1984/api/stream.mp4?src={CAM_1_NAME}" -o /dev/null && echo "cam1 OK"
```

Run the full health check on the Pi:

```bash
ssh {PI_USER}@{PI_IP} 'echo "Temp: $(vcgencmd measure_temp) | Throttle: $(vcgencmd get_throttled) | Cams: $(ps aux | grep rpicam-vid | grep -v grep | wc -l)/2 | Mem: $(free -m | awk "/Mem/{printf \"%d/%dMB\", \$3, \$2}") | Watchdog: $(cat /sys/class/watchdog/watchdog0/state)"'
```

Verify EEPROM settings (PoE only):

```bash
ssh {PI_USER}@{PI_IP} 'vcgencmd bootloader_config | grep -E "PSU_MAX|POWER_OFF"'
# Expected: PSU_MAX_CURRENT=5000, POWER_OFF_ON_HALT=1
```

### 17. Update NVR-Side Pi Health Monitor

The NVR runs a ping monitor that detects Pi outages from the network side. You need to add the new Pi to it.

**Option A: Separate monitor per Pi (recommended)**

Copy the existing monitor and create one for the new Pi:

```bash
sudo cp /opt/neurosurveillance/pi-monitor.sh /opt/neurosurveillance/pi2-monitor.sh
```

Edit the new file and change the IP and state file:

```bash
sudo nano /opt/neurosurveillance/pi2-monitor.sh
```

Change these three lines:

```bash
PI_IP="192.168.0.12"                                          # was 192.168.0.11
LOG="/opt/neurosurveillance/logs/pi2-monitor.log"              # was pi-monitor.log
STATE_FILE="/opt/neurosurveillance/logs/.pi2-monitor-state"    # was .pi-monitor-state
```

Make executable and add to cron:

```bash
sudo chmod +x /opt/neurosurveillance/pi2-monitor.sh
crontab -e
```

Add this line (alongside the existing Pi 1 monitor):

```
*/2 * * * * /opt/neurosurveillance/pi2-monitor.sh
```

**Validation:**

```bash
# Wait ~2 minutes, then check
cat /opt/neurosurveillance/logs/pi2-monitor.log
# Should be empty (no log = Pi is up, which is the normal state)

# Force a test by checking state file
cat /opt/neurosurveillance/logs/.pi2-monitor-state
# Expected: up
```

### 18. Add to Frigate Config on NVR

Edit Frigate config to add the new cameras:

```bash
nano /srv/frigate/config/config.yml
```

Add camera entries pointing to the new Pi's RTSP streams. Copy the configuration from existing cameras and update the paths:

```yaml
  {CAM_0_NAME}:
    ffmpeg:
      inputs:
        - path: rtsp://{PI_IP}:8554/{CAM_0_NAME}
          input_args: preset-rtsp-restream
          roles: [record]
    detect:
      enabled: false
      width: 1024
      height: 768
    record:
      enabled: true
    snapshots:
      enabled: true

  {CAM_1_NAME}:
    ffmpeg:
      inputs:
        - path: rtsp://{PI_IP}:8554/{CAM_1_NAME}
          input_args: preset-rtsp-restream
          roles: [record]
    detect:
      enabled: false
      width: 1024
      height: 768
    record:
      enabled: true
    snapshots:
      enabled: true
```

> [!tip] Copy from Existing
> Check the existing `pi_cam_0`/`pi_cam_1` entries in `config.yml` for the exact settings being used. The above is a minimal template — your production config may have additional options (hardware acceleration, retain settings, etc.).

Restart Frigate:

```bash
cd /srv/frigate && docker compose restart frigate
```

**Validation:**

```bash
# Check Frigate sees the new cameras
curl -s http://localhost:5000/api/stats | python3 -m json.tool | grep -A2 "{CAM_0_NAME}\|{CAM_1_NAME}"

# Or open Frigate UI in browser: http://192.168.0.50:5000
# Both new cameras should appear with live feeds
```

### 19. Update Session Daemon Config

If the new cameras should be managed by the session daemon (Radiens-triggered recording), add them to the daemon config:

```bash
nano /opt/neurosurveillance/config.yaml
```

Add the new chamber-to-camera mappings under `cameras:`:

```yaml
cameras:
  chamber_0: "pi_cam_0"
  chamber_1: "pi_cam_1"
  chamber_2: "pi_cam_2"    # Pi 2, camera 0
  chamber_3: "pi_cam_3"    # Pi 2, camera 1
```

Restart the daemon:

```bash
sudo systemctl restart neurosurveillance-session
```

### 20. Update Production Values

Add the new Pi's details to [[00-config/production-values|Production Values]]:

- Network: `{PI2_IP}`, `{PI2_HOSTNAME}`
- Cameras: `{CAMERA_2_ID}`, `{CAMERA_3_ID}`
- Quick Access Card: go2rtc API URL, RTSP URLs

---

## Completion Checklist

### On the Pi
- [ ] SSH key-based access working (no password prompt)
- [ ] System updated (`apt full-upgrade`)
- [ ] `rpicam-apps` installed (full, not lite — shows `libav:1`)
- [ ] go2rtc downloaded and executable
- [ ] go2rtc config created with unique camera names
- [ ] systemd service created, enabled, started
- [ ] Both camera streams active (2 rpicam-vid processes)
- [ ] Boot config hardened (WiFi/BT disabled, watchdog enabled)
- [ ] EEPROM PoE settings applied (if PoE-powered)
- [ ] systemd watchdog configured (`RuntimeWatchdogSec=30s`)
- [ ] watchdog.sh deployed and in crontab
- [ ] crash-canary.sh deployed and in crontab
- [ ] No throttling (`vcgencmd get_throttled` = `0x0`)
- [ ] Temperature acceptable (<70C)

### On the NVR
- [ ] Streams reachable from NVR (`curl` test passes)
- [ ] Pi monitor script created and in crontab
- [ ] Added to Frigate config, cameras visible in Frigate UI
- [ ] Session daemon config updated (if applicable)
- [ ] Production values updated in vault

---

**Deployed by:**
**Date:**
**Pi Hostname:**
**Pi IP:**
**Camera names:**

---

## Deployment History

| Pi | Hostname | IP | Cameras | Date | Notes |
|----|----------|----|---------|------|-------|
| Pi 1 | `skimlab` | `192.168.0.11` | `pi_cam_0`, `pi_cam_1` | 2026-02-09 | Original deployment |
| Pi 2 | `pi2` | `192.168.0.12` | `pi_cam_2`, `pi_cam_3` | 2026-03-07 | Second node |

## Related

- [[01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]] — stream config reference
- [[01-infrastructure/raspberry-pi/golden-systemd-service|systemd Service]] — service file reference
- [[01-infrastructure/raspberry-pi/golden-boot-config|Boot Hardening]] — boot config reference
- [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog & Monitoring]] — monitoring details, known issues, VSCode warning
- [[00-config/production-values|Production Values]] — all IPs, ports, paths

---
tags: [procedure, installation, raspberry-pi]
created: 2026-02-04
updated: 2026-03-07
status: production
---

# New Raspberry Pi Camera Node Setup

This procedure sets up a Raspberry Pi 5 as a dual-camera streaming node for the NeuroSurveillance system. It covers system hardening, go2rtc installation, PoE EEPROM configuration, and monitoring scripts.

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
- [ ] Ethernet cable connected
- [ ] Static IP assigned via DHCP reservation on router
- [ ] Raspberry Pi OS Lite 64-bit flashed to SD card (with hostname and SSH enabled)

---

## Installation Steps

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

If you use Ghostty terminal and get `Error opening terminal: xterm-ghostty` when running `nano` or other curses apps over SSH, run this on the Pi (or add to `~/.bashrc`):

```bash
export TERM=xterm-256color
```

### 3. System Update

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
sudo nano /opt/go2rtc/go2rtc.yaml
```

Paste the configuration from [[01-infrastructure/raspberry-pi/golden-go2rtc-config]], **replacing the stream names** with your Pi's unique camera names:

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

### 8. Create systemd Service

```bash
sudo nano /etc/systemd/system/go2rtc.service
```

Paste the configuration from [[01-infrastructure/raspberry-pi/golden-systemd-service]]. No changes needed — the service file is identical across all Pis.

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
```

### 10. Harden Boot Configuration

```bash
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d)
sudo nano /boot/firmware/config.txt
```

Add the settings from [[01-infrastructure/raspberry-pi/golden-boot-config]] to the end of the file.

### 11. Configure EEPROM for PoE HAT

> [!warning] Required for PoE-Powered Pis
> Skip this step only if the Pi is powered by a standard USB-C power supply (not PoE). Without these settings, a PoE power glitch will brick the Pi until manually power-cycled. We lost Pi 1 for **6 days** due to this — see [[03-troubleshooting/incidents/2026-02-19-pmic-fault-poe-death|Feb 19 PMIC incident]].

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

**Validation (after reboot):**
```bash
vcgencmd bootloader_config | grep -E "PSU_MAX|POWER_OFF"
# Expected:
# PSU_MAX_CURRENT=5000
# POWER_OFF_ON_HALT=1
```

> [!info] Double-Crash Limitation
> The EEPROM fix handles a single power event. If the Pi crashes again *during* the reboot (e.g. PoE still unstable), the PMIC enters latch-up and requires a manual power cycle. See [[03-troubleshooting/incidents/2026-02-24-pi-unreachable-no-route|Feb 24 incident]].

### 12. Configure systemd Watchdog

Edit `/etc/systemd/system.conf`, uncomment and set:

```ini
RuntimeWatchdogSec=30s
RebootWatchdogSec=10min
```

Apply without reboot:
```bash
sudo systemctl daemon-reexec
```

See [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog & Monitoring]] for the full monitoring setup (watchdog script, crash canary, NVR-side pi-monitor).

### 13. Reboot

```bash
sudo reboot
```

### 14. Post-Reboot Validation

```bash
ssh {PI_USER}@{PI_IP}

# Check streams
curl http://localhost:1984/api/streams

# Check temperature
vcgencmd measure_temp

# Check for throttling
vcgencmd get_throttled
# Expected: 0x0

# Check GPU memory (Pi 5 uses dynamic allocation — 4M is normal)
vcgencmd get_mem gpu
# Expected: gpu=4M

# Check process count
ps aux | grep rpicam-vid | grep -v grep | wc -l
# Expected: 2 (one per camera)

# Check watchdog is active
cat /sys/class/watchdog/watchdog0/state
# Expected: active

# Check no WiFi/BT interfaces
ip link show | grep -E "wlan|bluetooth"
# Expected: no output

# Check EEPROM settings (PoE only)
vcgencmd bootloader_config | grep -E "PSU_MAX|POWER_OFF"
# Expected: PSU_MAX_CURRENT=5000, POWER_OFF_ON_HALT=1
```

### 15. Verify Streams from NVR

Run on the **NVR** (or any machine on `192.168.0.x`):

```bash
# Check go2rtc API
curl -s http://{PI_IP}:1984/api/streams

# Test RTSP stream (grab 1 frame)
curl -m 5 "http://{PI_IP}:1984/api/stream.mp4?src={CAM_0_NAME}" -o /dev/null && echo "cam0 OK"
curl -m 5 "http://{PI_IP}:1984/api/stream.mp4?src={CAM_1_NAME}" -o /dev/null && echo "cam1 OK"
```

### 16. Add to Frigate Config on NVR

Edit Frigate config on the NVR to add the new cameras:

```bash
nano /srv/frigate/config/config.yml
```

Add camera entries pointing to the new Pi's RTSP streams:
```yaml
  {CAM_0_NAME}:
    ffmpeg:
      inputs:
        - path: rtsp://{PI_IP}:8554/{CAM_0_NAME}
          roles: [record]
    # ... (copy settings from existing camera entries)

  {CAM_1_NAME}:
    ffmpeg:
      inputs:
        - path: rtsp://{PI_IP}:8554/{CAM_1_NAME}
          roles: [record]
```

Restart Frigate:
```bash
cd /srv/frigate && docker compose restart frigate
```

### 17. Post-Deployment Updates

After successful deployment:

1. **Add Pi to [[00-config/production-values|Production Values]]** — IP, hostname, camera IDs
2. **Add camera entries to session daemon `config.yaml`** — map new chambers to new camera IDs
3. **Update NVR-side pi-monitor** — add new Pi IP to monitoring (see [[01-infrastructure/raspberry-pi/watchdog-monitoring#NVR-Side Pi Health Monitor|Pi Health Monitor]])
4. **Deploy monitoring scripts on Pi** — watchdog.sh, crash-canary.sh (see [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog & Monitoring]])

---

## Completion Checklist

- [x] SSH key-based access working ✅ 2026-03-07
- [x] go2rtc service running ✅ 2026-03-07
- [x] Both camera streams active (2 rpicam-vid processes) ✅ 2026-03-07
- [x] No throttling (`0x0`) ✅ 2026-03-07
- [x] Temperature acceptable (<70C) ✅ 2026-03-07
- [x] Watchdog active ✅ 2026-03-07
- [x] EEPROM PoE settings applied (if PoE-powered) ✅ 2026-03-07
- [ ] Streams visible from NVR
- [ ] Added to Frigate config on NVR
- [ ] Added to production-values.md
- [ ] Pi-monitor updated on NVR

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

- [[01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]
- [[01-infrastructure/raspberry-pi/golden-systemd-service|systemd Service]]
- [[01-infrastructure/raspberry-pi/golden-boot-config|Boot Hardening]]
- [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog & Monitoring]]
- [[00-config/production-values|Production Values]]

---
tags: [procedure, installation, raspberry-pi]
created: 2026-02-04
status: production
---

# New Raspberry Pi Camera Node Setup

## Prerequisites Checklist

- [x] Raspberry Pi 5 with official power supply (5V/5A) ✅ 2026-02-09
- [x] Raspberry Pi Camera Module(s) connected ✅ 2026-02-09
- [x] Ethernet cable connected ✅ 2026-02-09
- [x] Static IP assigned via DHCP reservation ✅ 2026-02-09
- [x] Raspberry Pi OS Lite 64-bit flashed to SD card ✅ 2026-02-09
- [x] SSH enabled (create empty `ssh` file in boot partition) ✅ 2026-02-09

## Your Values (from [[00-config/production-values]])

| Variable | Value |
|----------|-------|
| `{PI_IP}` | `192.168.0.11` |
| `{PI_USER}` | `skimlab` |
| `{PI_HOME}` | `/home/skimlab` |

---

## Installation Steps

### 1. Initial SSH Connection

```bash
ssh skimlab@192.168.0.11
```

**Expected:** Login prompt, then shell access

### 2. System Update

```bash
sudo apt update && sudo apt full-upgrade -y
```

**Expected:** Updates install without errors

### 3. Install Dependencies

```bash
sudo apt install -y git curl wget ffmpeg
```

### 4. Install Camera Software

```bash
# Install FULL rpicam-apps (not lite - lite lacks libav codec)
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

### 5. Download go2rtc

```bash
sudo mkdir -p /opt/go2rtc
cd /opt/go2rtc
sudo wget https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_arm64
sudo mv go2rtc_linux_arm64 go2rtc
sudo chmod +x go2rtc
sudo chown -R skimlab:video /opt/go2rtc
```

**Validation:**
```bash
/opt/go2rtc/go2rtc --version
```

### 6. Create Configuration

```bash
sudo nano /opt/go2rtc/go2rtc.yaml
```

Paste the configuration from [[01-infrastructure/raspberry-pi/golden-go2rtc-config]]

### 7. Create systemd Service

```bash
sudo nano /etc/systemd/system/go2rtc.service
```

Paste the configuration from [[01-infrastructure/raspberry-pi/golden-systemd-service]]

### 8. Enable and Start Service

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

### 9. Harden Boot Configuration

```bash
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup
sudo nano /boot/firmware/config.txt
```

Add settings from [[01-infrastructure/raspberry-pi/golden-boot-config]]

### 10. Reboot

```bash
sudo reboot
```

### 11. Post-Reboot Validation

```bash
ssh skimlab@192.168.0.11

# Check streams
curl http://localhost:1984/api/streams

# Check temperature
vcgencmd measure_temp

# Check for throttling
vcgencmd get_throttled
# Expected: 0x0

# Check GPU memory
vcgencmd get_mem gpu
# Expected: gpu=128M

# Check process count
ps aux | grep rpicam-vid | grep -v grep | wc -l
# Expected: 2 (one per camera)
```

---

## Completion Checklist

- [x] SSH access working ✅ 2026-02-09
- [x] go2rtc service running ✅ 2026-02-09
- [x] Both camera streams active ✅ 2026-02-09
- [ ] No throttling (0x0)
- [ ] GPU memory correct (128M)
- [ ] Temperature acceptable (<70C)
- [ ] Added to Frigate config on NVR

## Notes

*Add any deployment-specific notes here*

---

**Deployed by:**
**Date:**
**Pi Serial/ID:**

---
tags: [procedure, installation, raspberry-pi]
created: 2026-02-04
status: production
---

# New Raspberry Pi Camera Node Setup

## Prerequisites Checklist

- [ ] Raspberry Pi 5 with official power supply (5V/5A)
- [ ] Raspberry Pi Camera Module(s) connected
- [ ] Ethernet cable connected
- [ ] Static IP assigned via DHCP reservation
- [ ] Raspberry Pi OS Lite 64-bit flashed to SD card
- [ ] SSH enabled (create empty `ssh` file in boot partition)

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

### 4. Download go2rtc

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

### 5. Create Configuration

```bash
sudo nano /opt/go2rtc/go2rtc.yaml
```

Paste the configuration from [[01-infrastructure/raspberry-pi/golden-go2rtc-config]]

### 6. Create systemd Service

```bash
sudo nano /etc/systemd/system/go2rtc.service
```

Paste the configuration from [[01-infrastructure/raspberry-pi/golden-systemd-service]]

### 7. Enable and Start Service

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

### 8. Harden Boot Configuration

```bash
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup
sudo nano /boot/firmware/config.txt
```

Add settings from [[01-infrastructure/raspberry-pi/golden-boot-config]]

### 9. Reboot

```bash
sudo reboot
```

### 10. Post-Reboot Validation

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

- [ ] SSH access working
- [ ] go2rtc service running
- [ ] Both camera streams active
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

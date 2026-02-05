---
tags: [troubleshooting, symptom, raspberry-pi]
created: 2026-02-05
severity: critical
---

## Description

- SSH sessions freeze after hours/days
- Cannot connect to Pi via SSH
- System appears to hang randomly

## Root Cause

**Zombie rpicam-vid processes** due to incorrect systemd `KillMode`

## Quick Diagnosis

```bash
# Check for zombie processes
ps aux | grep defunct

# Check KillMode in service file
grep KillMode /etc/systemd/system/go2rtc.service
```

## Solution

### Fix systemd service:

```bash
sudo nano /etc/systemd/system/go2rtc.service
```

**Ensure this line exists:**
```ini
KillMode=control-group  # NOT 'mixed' or 'process'
```

**Apply changes:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart go2rtc.service
```

## Emergency Recovery

If system is partially responsive:
```bash
sudo systemctl stop go2rtc
sudo pkill -9 rpicam-vid
sudo systemctl start go2rtc
```

If nothing works:
```bash
# Hard reboot required
# After reboot, verify KillMode is set correctly
```

## Prevention

- Always use `KillMode=control-group` in service file
- Enable hardware watchdog (auto-reboots on freeze)
- See [[../../01-infrastructure/raspberry-pi/golden-systemd-service|golden systemd service]]

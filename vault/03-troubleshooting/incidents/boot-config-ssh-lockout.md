---
tags: [troubleshooting, ssh, boot-config, raspberry-pi]
created: 2026-02-09
severity: high
status: resolved
---

# SSH Lockout After Boot Config Changes

## Problem

After editing `/boot/firmware/config.txt` to disable WiFi and adding surveillance hardening settings, the Raspberry Pi became completely unreachable via SSH. Required physical access to unplug/replug the power to recover.

## Root Cause

**Disabled WiFi while still connected via WiFi** - The boot config change `dtoverlay=disable-wifi` was applied before verifying that Ethernet was connected and working. After reboot, the Pi had no network connectivity.

## Boot Config Changes Applied

```ini
# ========================================
# SURVEILLANCE SYSTEM HARDENING
# Added: 2026-02-09
# ========================================

# Disable WiFi (using Ethernet only)
dtoverlay=disable-wifi

# Disable Bluetooth (not needed)
dtoverlay=disable-bt

# GPU memory for dual camera operation
gpu_mem=128  # NOTE: Ignored on Pi 5 (uses dynamic allocation)

# Enable hardware watchdog (auto-reboot on freeze)
dtparam=watchdog=on
```

## Solution

### 1. Verify Ethernet Connection FIRST

Before disabling WiFi, always verify Ethernet is working:

```bash
# Check Ethernet interface status
ip addr show eth0

# Verify you can reach the Pi via Ethernet IP
ping <ethernet-ip>

# Check which interface is currently active
ip -br addr show | grep -E 'eth0|wlan0'
```

### 2. Reduce Boot Power Spike

With 2 cameras + 4 IR LEDs, power spike during boot may cause issues. Added startup delay to go2rtc service:

**Modified `/etc/systemd/system/go2rtc.service`:**

```ini
[Service]
User=skimlab
Group=video
WorkingDirectory=/opt/go2rtc
# Wait 60 seconds after boot before starting cameras
ExecStartPre=/bin/sleep 60
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml
```

**Apply changes:**
```bash
sudo systemctl daemon-reload
```

### 3. Apply Boot Config Safely

```bash
# Backup current config
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup

# Edit config
sudo nano /boot/firmware/config.txt

# (Optional) Set safety timer - auto-reboot in 10 minutes if you get locked out
sudo shutdown -r +10

# Reboot
sudo reboot

# After successful reboot, cancel safety timer if set
sudo shutdown -c
```

## Prevention Checklist

Before applying boot config hardening:

- [ ] Ethernet cable physically connected
- [ ] Ethernet interface shows UP with valid IP: \`ip addr show eth0\`
- [ ] Can ping Pi via Ethernet IP from another machine
- [ ] Boot config backup created
- [ ] go2rtc service has startup delay (if using cameras)
- [ ] (Optional) Safety reboot timer set: \`sudo shutdown -r +10\`

## Verification After Reboot

```bash
# Check Ethernet is active, WiFi is gone
ip -br addr show | grep -E 'eth0|wlan0'
# Expected: eth0 UP with IP, no wlan0

# Check GPU memory (Pi 5 shows 4M, uses dynamic allocation)
vcgencmd get_mem gpu

# Check for throttling
vcgencmd get_throttled
# Expected: 0x0

# Check go2rtc service started
systemctl status go2rtc.service

# Check camera streams
curl http://localhost:1984/api/streams
```

## Notes

- **Raspberry Pi 5**: The \`gpu_mem=128\` parameter is ignored. Pi 5 uses dynamic GPU memory allocation automatically.
- **Startup delay**: 60-second delay prevents power spike issues with multiple cameras during boot
- **Watchdog**: \`dtparam=watchdog=on\` enables automatic reboot if system freezes

## Related

- [[new-pi-setup]]
- [[golden-boot-config]]
- [[2026-02-09-go2rtc-setup-troubleshooting]] - Related go2rtc configuration issues from same day

---

**Resolved by:** Claude Code
**Date:** 2026-02-09
**Pi affected:** pi1 (192.168.0.11)

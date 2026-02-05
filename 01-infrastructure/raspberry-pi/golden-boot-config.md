---
tags: [infrastructure, raspberry-pi, boot, hardening, golden-config]
created: 2026-02-04
status: production
---

# Raspberry Pi Boot Configuration

> [!tip] Stability Hardening
> These settings disable unused features and enable hardware watchdog for auto-recovery.

## Configuration File Location

**On Raspberry Pi:** `/boot/firmware/config.txt`

## Required Additions

Add these lines to the END of config.txt:

```ini
# ========================================
# SURVEILLANCE SYSTEM HARDENING
# Added: 2026-02-04
# ========================================

# Disable WiFi (using Ethernet only)
dtoverlay=disable-wifi

# Disable Bluetooth (not needed)
dtoverlay=disable-bt

# GPU memory for dual camera operation
gpu_mem=128

# Enable hardware watchdog (auto-reboot on freeze)
dtparam=watchdog=on
```

## Why These Settings

| Setting | Purpose |
|---------|---------|
| `disable-wifi` | Reduces interference, saves power, improves stability |
| `disable-bt` | Removes unused service, frees resources |
| `gpu_mem=128` | Required for dual camera operation |
| `watchdog=on` | Pi auto-reboots if system freezes (critical for 24/7 operation) |

## Backup Before Editing

```bash
# ALWAYS backup first
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d)

# Edit
sudo nano /boot/firmware/config.txt

# Reboot required for changes
sudo reboot
```

## Validation After Reboot

```bash
# Check GPU memory
vcgencmd get_mem gpu
# Expected: gpu=128M

# Check watchdog is active
cat /sys/class/watchdog/watchdog0/state
# Expected: active

# Verify no WiFi/BT interfaces
ip link show | grep -E "wlan|bluetooth"
# Expected: no output
```

## Related

- [[golden-go2rtc-config]] - go2rtc configuration
- [[golden-systemd-service]] - systemd service

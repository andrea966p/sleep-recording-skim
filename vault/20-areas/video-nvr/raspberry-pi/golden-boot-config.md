---
type: reference
area: video-nvr
status: active
tags: [infrastructure, raspberry-pi, boot, hardening, golden-config]
created: 2026-02-04
---

# Raspberry Pi Boot Configuration

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The boot-time settings on each Raspberry Pi 5 camera node — enables the hardware watchdog, disables unused features, sets the minimum reliable config for 24/7 camera streaming.
>
> **Why it exists.** Without the hardware watchdog enabled at boot, a kernel hang would require a physical reset. With it enabled the Pi self-recovers after ~15 seconds. The other knobs trade unused features (Bluetooth, audio, etc.) for a more deterministic system.
>
> **How to read this page.** Most readers only need to know the file exists (`/boot/firmware/config.txt`) and that the watchdog line must stay. Look up specific settings here only if you're rebuilding a Pi from scratch or debugging boot.

> [!quote] Paper-ready
> Each Raspberry Pi 5 camera node is boot-hardened with the BCM2712 hardware watchdog enabled, so the system self-recovers from a kernel hang within ~15 seconds without operator intervention.

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
# NOTE: Ignored on Pi 5 (uses dynamic allocation, vcgencmd shows gpu=4M).
# Kept for Pi 4 compatibility. Harmless on Pi 5.
gpu_mem=128

# Enable hardware watchdog (auto-reboot on freeze)
dtparam=watchdog=on
```

## Why These Settings

| Setting | Purpose |
|---------|---------|
| `disable-wifi` | Reduces interference, saves power, improves stability |
| `disable-bt` | Removes unused service, frees resources |
| `gpu_mem=128` | GPU memory allocation (Pi 4); **ignored on Pi 5** (dynamic allocation) |
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
# Expected: gpu=4M (Pi 5 uses dynamic allocation, 4M is the minimum reserve)

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

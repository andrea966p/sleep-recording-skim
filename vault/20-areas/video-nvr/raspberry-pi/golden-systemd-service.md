---
type: reference
area: video-nvr
status: active
tags: [infrastructure, raspberry-pi, systemd, golden-config]
created: 2026-02-04
version: "5.1"
---

# Golden systemd Service

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The systemd unit file on each Raspberry Pi 5 that runs `go2rtc` as a managed service — auto-starts at boot, restarts on crash.
>
> **Why it exists.** Without it, `go2rtc` would have to be started manually after every Pi reboot. With it, the camera streams come back automatically after a power blip or kernel watchdog reset.
>
> **How to read this page.** The unit file is short. The one line that **must not** be changed is `KillMode=control-group` — it ensures `rpicam-vid` child processes are killed when go2rtc restarts. Without it, zombie processes pile up and eventually freeze the Pi.

> [!quote] Paper-ready
> The go2rtc service runs under systemd on each Raspberry Pi camera node with `KillMode=control-group` to ensure all child capture processes are terminated atomically with the parent, preventing zombie-process accumulation and the system freezes that follow.

> [!warning] CRITICAL SETTING
> `KillMode=control-group` is **MANDATORY**.
> Without it, zombie rpicam-vid processes cause system freezes.

## File Location

**Path:** `/etc/systemd/system/go2rtc.service`

## Production Configuration (v5.1)

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
# IR LED power spike prevention -- wait for boot power draw to settle
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

## Why These Settings Matter

| Setting | Purpose | Consequence if Wrong |
|---------|---------|---------------------|
| `KillMode=control-group` | Kills rpicam-vid children | Zombie processes, system freeze |
| `WorkingDirectory` | Proper path resolution | Service fails to start |
| `CPUQuota=70%` | Prevents thermal throttling | Overheating, shutdowns |
| `MemorySwapMax=0` | No swap usage | SD card wear |

## Commands

```bash
# After editing
sudo systemctl daemon-reload

# Enable at boot
sudo systemctl enable go2rtc.service

# Start/stop/restart
sudo systemctl start go2rtc.service
sudo systemctl restart go2rtc.service

# Check status
sudo systemctl status go2rtc.service

# View logs
journalctl -u go2rtc.service -n 50
```

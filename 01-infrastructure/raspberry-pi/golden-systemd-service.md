---
tags: [infrastructure, raspberry-pi, systemd, golden-config]
created: 2026-02-04
status: production
version: "5.0"
---

# Golden systemd Service

> [!warning] CRITICAL SETTING
> `KillMode=control-group` is **MANDATORY**.
> Without it, zombie rpicam-vid processes cause system freezes.

## File Location

**Path:** `/etc/systemd/system/go2rtc.service`

## Production Configuration (v5.0)

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
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml

# Restart policy
Restart=always
RestartSec=5

# CRITICAL: Process termination
KillMode=control-group    # MANDATORY - kills ALL child processes
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

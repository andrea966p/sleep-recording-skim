---
tags: [index, navigation, home]
---

# NeuroSurveillance System Documentation

> [!info] Quick Access
> | Service | URL |
> |---------|-----|
> | **Frigate** | http://192.168.0.50:5000 |
> | **go2rtc (Pi 1)** | http://192.168.0.11:1984 |
> | **go2rtc (Pi 2)** | http://192.168.0.12:1984 |
> | **Session Daemon** | http://127.0.0.1:8585 (NVR localhost) |
> | **Netdata (NVR)** | http://192.168.0.50:19999 |
> | **Uptime Kuma** | http://192.168.0.50:3001 |
> | **Status Page** | http://192.168.0.50:3001/status/neurosurveillance |
> | **Config** | [[00-config/production-values]] |
> | **Tasks** | [[00-config/task-dashboard]] |

---

## Documentation Map

### [[00-config/production-values|Configuration]]
Production IPs, usernames, paths, and settings.

### Infrastructure

**Raspberry Pi:**
- [[01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]
- [[01-infrastructure/raspberry-pi/golden-systemd-service|systemd Service]]
- [[01-infrastructure/raspberry-pi/golden-boot-config|Boot Hardening]]
- [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog & Monitoring]]

**Frigate NVR:**
- [[01-infrastructure/frigate/docker-compose|Docker Compose]]
- [[01-infrastructure/frigate/config-yml|config.yml]]

**Hardware Sync (XDAQ GPIO):**
- [[01-infrastructure/hardware-sync/overview|Overview & Architecture]]
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide & BOM]]
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service (Golden Config)]]
- [[01-infrastructure/hardware-sync/radiens-api-reference|Radiens API — Digital I/O Reference]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]

**Session Daemon:**
- [[01-infrastructure/session-daemon/architecture|Architecture & Design]]
- [[01-infrastructure/session-daemon/session-journal|Session Journal — WAL (added 2026-05-23)]]
- [[01-infrastructure/session-daemon/reconciler|Reconciler — nightly WAL ↔ Frigate cross-check (added 2026-05-24)]]
- [[01-infrastructure/session-daemon/frontend-reference|Frontend Reference]]
- [[01-infrastructure/session-daemon/session-service|Systemd Service]]

**Monitoring & Alerting:**
- [[01-infrastructure/netdata/nvr-alerts-config|Netdata NVR Alerts (Golden Config)]]
- [[02-procedures/installation/monitoring-setup|Monitoring Setup Procedure]]

### Procedures
- [[02-procedures/installation/new-pi-setup|New Pi Setup]]
- [[02-procedures/session-recording-workflow|Session Recording Workflow]]
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]
- [[02-procedures/installation/storage-management-implementation|Storage Management System]] ✅

### Troubleshooting

**By Symptom:**
- [[03-troubleshooting/symptoms/no-frames-received|No frames received]]
- [[03-troubleshooting/symptoms/system-freeze-ssh-hang|System freeze / SSH hang]]
- [[03-troubleshooting/symptoms/frigate-high-cpu|Frigate 100% CPU]]
- [[03-troubleshooting/symptoms/docker-memory-crash|Docker memory crash]]

**Incident Log:**
- [[03-troubleshooting/incidents/|Incidents]]
- [[03-troubleshooting/incidents/2026-02-23-session-daemon-radiens-auth-cors|2026-02-23 Session Daemon Auth + CORS]]

### Journal
- [[04-journal/|Daily Notes]]

### Experiments
- [[05-experiments/completed/h265-encoding-failure|H.265 Failure (DO NOT USE)]]
- [[05-experiments/completed/2026-02-11-mpegts-container-test|MPEG-TS Container Test (adopted v5.2)]]
- [[05-experiments/active/|Active Experiments]]

### References
- [[06-references/monitoring-diagnostics|Monitoring Diagnostics]] — Netdata/Uptime Kuma query commands for troubleshooting
- [[06-references/command-cheatsheet|Command Cheatsheet]]
- [[06-references/video-parameters|Video Parameters]]

### Archive
- [[99-archive/notion-import-2025-02/|Notion Import]]

---

## System Status

| Component | IP | Status |
|-----------|------|--------|
| **Pi 1** | 192.168.0.11 | Online |
| **Pi 2** | 192.168.0.12 | Online |
| **go2rtc (Pi 1)** | :1984 | Online |
| **go2rtc (Pi 2)** | :1984 | Online |
| **Frigate** | 192.168.0.50:5000 | Online |
| **Session Daemon** | 127.0.0.1:8585 | Healthy (daemon + MQTT + Radiens connected) |
| **Netdata (NVR)** | 192.168.0.50:19999 | Active (16 NVR alerts, Slack notifications) |
| **Netdata (Pi 1)** | 192.168.0.11:19999 | Active |
| **Netdata (Pi 2)** | 192.168.0.12:19999 | Active |
| **Uptime Kuma** | 192.168.0.50:3001 | Active (7 monitors, Slack alerting) |

---

## Quick Commands

```bash
# Pi health check
ssh skimlab@192.168.0.11 'vcgencmd measure_temp && systemctl status go2rtc'

# Frigate logs
ssh skimlab@192.168.0.50 'docker logs frigate --tail 20'

# Stream test
ffprobe rtsp://192.168.0.11:8554/pi_cam_0
```

---

## Emergency

1. Check [[03-troubleshooting/symptoms/|Symptom Index]]
2. Run: `sudo systemctl restart go2rtc.service`
3. See [[06-references/command-cheatsheet|Command Cheatsheet]]

---

*Last updated: 2026-05-24*

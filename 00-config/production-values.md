---
tags: [config, production, sensitive]
created: 2026-02-04
updated: 2026-03-07
status: active
---

# Production Configuration Values

> [!warning] SENSITIVE INFORMATION
> This file contains actual production values. Do NOT commit to public Git repositories.
> For parameterized templates (with `{VARIABLES}`), see the Claude skill or GitHub repo.

## Quick Access Card

| Service | URL | Status |
|---------|-----|--------|
| **Frigate NVR** | http://192.168.0.50:5000 | |
| **go2rtc API (Pi 1)** | http://192.168.0.11:1984 | |
| **go2rtc API (Pi 2)** | http://192.168.0.12:1984 | |
| **Mosquitto MQTT** | mqtt://192.168.0.50:1883 | |
| **Camera 0 RTSP** | rtsp://192.168.0.11:8554/pi_cam_0 | |
| **Camera 1 RTSP** | rtsp://192.168.0.11:8554/pi_cam_1 | |
| **Camera 2 RTSP** | rtsp://192.168.0.12:8554/pi_cam_2 | |
| **Camera 3 RTSP** | rtsp://192.168.0.12:8554/pi_cam_3 | |
| **Session Daemon** | http://127.0.0.1:8585 | |
| **Netdata (NVR)** | http://192.168.0.50:19999 | planned |
| **Netdata (Pi 1)** | http://192.168.0.11:19999 | planned |
| **Netdata (Pi 2)** | http://192.168.0.12:19999 | planned |
| **Uptime Kuma** | http://192.168.0.50:3001 | planned |

---

## Network Configuration

| Variable           | Production Value | Notes                         |
| ------------------ | ---------------- | ----------------------------- |
| `{PI1_IP}`         | `192.168.0.11`   | Raspberry Pi 5 #1 static IP   |
| `{PI1_HOSTNAME}`   | `skimlab`        | Pi 1 hostname                 |
| `{PI2_IP}`         | `192.168.0.12`   | Raspberry Pi 5 #2 static IP   |
| `{PI2_HOSTNAME}`   | `pi2`            | Pi 2 hostname                 |
| `{NVR_IP}`         | `192.168.0.50`   | ASUS Mini PC (Frigate server) |
| `{NVR_HOSTNAME}`   | `e10ubuntu`      | ASUS NUC 14 Pro hostname      |
| `{NETWORK_SUBNET}` | `192.168.0.0/24` | Lab network                   |

### Tailscale IPs (for remote access) bilab.kaist@gmail.com tailnet

| Device                | Tailscale IP    |
| --------------------- | --------------- |
| PC 1 (Office)         | `100.117.204.8` |
| PC 2 (Experiment/NVR) | `100.85.191.25` |
| Synology NAS          | `100.120.86.10` |

---

## User Accounts

| Variable | Production Value | Notes |
|----------|------------------|-------|
| `{PI_USER}` | `skimlab` | Raspberry Pi username |
| `{NVR_USER}` | `skimlab` | Ubuntu NVR username |

---

## Ports

| Variable | Value | Service |
|----------|-------|---------|
| `{RTSP_PORT}` | `8554` | go2rtc RTSP server |
| `{GO2RTC_API_PORT}` | `1984` | go2rtc web interface |
| `{FRIGATE_WEB_PORT}` | `5000` | Frigate web UI |
| `{FRIGATE_RTSP_PORT}` | `8554` | Frigate RTSP restream |
| `{FRIGATE_WEBRTC_PORT}` | `8555` | Frigate WebRTC |
| `{MQTT_PORT}` | `1883` | Mosquitto MQTT broker |
| `{SESSION_DAEMON_PORT}` | `8585` | Session daemon REST API |
| `{NETDATA_PORT}` | `19999` | Netdata dashboard (planned) |
| `{UPTIME_KUMA_PORT}` | `3001` | Uptime Kuma dashboard (planned) |
| `{DB_PORT}` | `5432` | PostgreSQL (planned) |

---

## Camera Configuration

| Variable | Value | Notes |
|----------|-------|-------|
| `{CAMERA_0_ID}` | `pi_cam_0` | Pi 1, camera 0 |
| `{CAMERA_1_ID}` | `pi_cam_1` | Pi 1, camera 1 |
| `{CAMERA_2_ID}` | `pi_cam_2` | Pi 2, camera 0 |
| `{CAMERA_3_ID}` | `pi_cam_3` | Pi 2, camera 1 |
| `{CAMERA_WIDTH}` | `1024` | Resolution width |
| `{CAMERA_HEIGHT}` | `768` | Resolution height |
| `{CAMERA_FPS}` | `15` | Framerate |
| `{CAMERA_BITRATE}` | `1500000` | 1.5 Mbps |

---

## Directory Paths

### Raspberry Pi Paths
| Variable | Value |
|----------|-------|
| `{PI_HOME}` | `/home/skimlab` |
| `{GO2RTC_DIR}` | `/opt/go2rtc` |
| `{GO2RTC_CONFIG}` | `/opt/go2rtc/go2rtc.yaml` |
| `{SCRIPTS_DIR}` | `/opt/scripts` |

### NVR Server Paths
| Variable | Value |
|----------|-------|
| `{NVR_HOME}` | `/home/skimlab` |
| `{FRIGATE_DIR}` | `/srv/frigate` |
| `{FRIGATE_CONFIG_DIR}` | `/srv/frigate/config` |
| `{FRIGATE_MEDIA_DIR}` | `/srv/frigate/storage` |
| `{SESSION_DAEMON_DIR}` | `/opt/neurosurveillance` |
| `{SESSION_DAEMON_REPO}` | `/home/skimlab/Monitoring_project/neurosurveillance` |
| `{SESSION_DAEMON_GITHUB}` | `git@github.com:andrea966p/neurosurveillance.git` (private) |
| `{SESSION_LOG_DIR}` | `/opt/neurosurveillance/logs` |
| `{SESSION_EXPORT_DIR}` | `/srv/frigate/storage/exports` |
| `{SESSION_DATA_DIR}` | `/opt/neurosurveillance/sessions` |
| `{EXPORT_DIR}` | `/opt/neurosurveillance/exports` |
| `{SUDOERS_POLICY}` | `/etc/sudoers.d/neurosurveillance-fs` |

---

## NVR Hardware (ASUS NUC 14 Pro — NUC14RVH-B)

| Component | Detail |
|-----------|--------|
| CPU | Intel Core Ultra 5 125H (Meteor Lake, 14 cores) |
| GPU | Intel Arc Graphics (integrated) — QSV H.264 decode confirmed |
| RAM | 30.6 GB |
| Storage | 1.9 TB NVMe |
| OS | Ubuntu 24.04 LTS |
| Kernel | `6.17.0-14-generic` (HWE) |
| VA-API Driver | `iHD` (Intel Media Driver) |
| Docker CE | `29.3.0` (pinned — excluded from unattended-upgrades) |
| Docker Compose | `v5.1.0` |
| Frigate | `0.16.1` (pinned in docker-compose.yml) |

---

## Hardware Settings

| Variable | Value | Notes |
|----------|-------|-------|
| `{GPU_MEM}` | `128` | GPU memory for dual cameras |
| `{CPU_QUOTA}` | `70%` | go2rtc CPU limit |
| `{MEMORY_MAX}` | `512M` | go2rtc memory limit |
| `{TIMEZONE}` | `Asia/Seoul` | System timezone |

### Docker Group IDs (for Frigate)
| Group | GID | Verify Command |
|-------|-----|----------------|
| render | `992` | `getent group render` |
| video | `44` | `getent group video` |

---

## Recording Settings

| Variable | Value | Notes |
|----------|-------|-------|
| `{RETENTION_DAYS}` | `7` | Video retention |
| `{STORAGE_PER_CAM_DAY}` | `~45GB` | Estimated storage |
| `{MANUAL_SESSION_MIN_DURATION}` | `5` | Min seconds for manual recording export (filters accidental clicks) |

---

## Database Configuration (PLANNED - Not Yet Deployed)

| Variable | Value | Notes |
|----------|-------|-------|
| `{DB_NAME}` | `neurosurveillance` | Database name |
| `{DB_USER}` | `researcher` | Database username |
| `{DB_PASSWORD}` | *use .env file* | NEVER store here |

---

## Frigate Authentication

| Field | Value |
|-------|-------|
| Admin user | `admin` |
| Admin password | *(changed from auto-generated default — check Frigate UI)* |

> [!tip] Password Management
> The admin password was changed from the auto-generated default on 2026-02-12.
> If you need to reset it, delete the Frigate database and restart the container.

---

## How to Use This File

1. **When Claude shows a template** with `{VARIABLE}`:
   - Look up the value in this file
   - Replace `{VARIABLE}` with the actual value (remove curly braces!)

2. **Example:**
   ```yaml
   # Template:
   path: rtsp://{PI_IP}:{RTSP_PORT}/{CAMERA_0_ID}

   # Your actual file:
   path: rtsp://192.168.0.11:8554/pi_cam_0
   ```

3. **Keep updated** when infrastructure changes

---

## Quick Validation Commands

```bash
# SSH to Pi
ssh skimlab@192.168.0.11

# SSH to NVR
ssh skimlab@192.168.0.50

# Test go2rtc streams
curl http://192.168.0.11:1984/api/streams

# Test Frigate
curl http://192.168.0.50:5000/api/stats

# Test Session Daemon
curl http://127.0.0.1:8585/api/health
```

---

**Last validated:** 2026-02-23
**System status:** Operational (Pi streaming + Frigate recording + MQTT + Session daemon deployed; daemon + MQTT + Radiens healthy)

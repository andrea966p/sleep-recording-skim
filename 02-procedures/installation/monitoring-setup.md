---
tags: [procedure, installation, monitoring, netdata, uptime-kuma]
created: 2026-03-24
updated: 2026-03-24
status: planned
---

# Centralized Monitoring Setup (Netdata + Uptime Kuma)

This procedure deploys two monitoring tools across the NeuroSurveillance infrastructure:

- **Netdata** — real-time system & service metrics on all 3 machines (CPU, RAM, disk, Docker, systemd, processes)
- **Uptime Kuma** — service health checks with alerting (Slack/email when something goes down)

> [!info] Why These Tools?
> Ansible was considered but is a deployment tool, not a monitoring tool. Netdata + Uptime Kuma provide a proper single-dashboard experience with ~1 hour total setup. Netdata uses 88% less RAM than Prometheus+Grafana and auto-discovers Docker containers and systemd services.

## What Gets Monitored

| Target | Tool | Check Type |
|--------|------|-----------|
| CPU, RAM, disk, network (all machines) | Netdata | Real-time metrics |
| Temperature, throttling (Pis) | Netdata | Real-time metrics |
| Docker containers (Frigate, Mosquitto) | Netdata | Auto-discovered |
| systemd services (go2rtc, session daemon) | Netdata | Auto-discovered |
| `rpicam-vid` processes | Netdata | Process monitoring |
| Flask API `/api/health` | Uptime Kuma | HTTP check, 60s |
| Frigate `/api/stats` | Uptime Kuma | HTTP check, 60s |
| MQTT broker `:1883` | Uptime Kuma | TCP check, 60s |
| go2rtc Pi 1 `:1984` | Uptime Kuma | HTTP check, 60s |
| go2rtc Pi 2 `:1984` | Uptime Kuma | HTTP check, 60s |
| Pi 1 reachability | Uptime Kuma | Ping, 30s |
| Pi 2 reachability | Uptime Kuma | Ping, 30s |

## Access URLs (After Setup)

| Service | URL |
|---------|-----|
| Netdata (NVR) | `http://192.168.0.50:19999` |
| Netdata (Pi 1) | `http://192.168.0.11:19999` |
| Netdata (Pi 2) | `http://192.168.0.12:19999` |
| Uptime Kuma | `http://192.168.0.50:3001` |

---

## Prerequisites Checklist

- [x] All 3 machines online and accessible via SSH ✅ 2026-03-27
- [x] Internet access on all machines (for downloading packages) ✅ 2026-03-27
- [x] `sudo` access on all machines ✅ 2026-03-27
- [x] Docker running on NVR (`docker ps` works) ✅ 2026-03-27
- [x] (Optional) Slack webhook URL for alerting ✅ 2026-03-27

---

## Part 1: Install Netdata on NVR (`192.168.0.50`)

### 1.1 Install Netdata

```bash
ssh skimlab@192.168.0.50
```

```bash
# Download and run the official installer (stable channel)
curl https://get.netdata.cloud/kickstart.sh > /tmp/netdata-kickstart.sh
sh /tmp/netdata-kickstart.sh --stable-channel
```

The installer will:
- Add the Netdata apt repository
- Install the Netdata agent as a systemd service
- Start it automatically

### 1.2 Verify Installation

```bash
# Check the service is running
systemctl status netdata

# Check the web UI responds
curl -s http://localhost:19999/api/v1/info | head -5
```

### 1.3 Verify Auto-Discovery

Open `http://192.168.0.50:19999` in a browser. Confirm you can see:

- [x] System Overview (CPU, RAM, disk, network) ✅ 2026-03-27
- [x] Docker containers section (Frigate, Mosquitto should appear) ✅ 2026-03-27
- [x] systemd services section (neurosurveillance-session should appear) ✅ 2026-03-27

> [!tip] Docker Metrics
> Netdata auto-discovers Docker containers via the Docker socket. If Docker containers don't appear, check that the `netdata` user has access to `/var/run/docker.sock`:
> ```bash
> sudo usermod -aG docker netdata
> sudo systemctl restart netdata
> ```

### 1.4 Record Version

```bash
netdata -v
# Record this in the table below
```

| Machine               | Netdata Version | Install Date |
| --------------------- | --------------- | ------------ |
| NVR (`192.168.0.50`)  | 2.9.0           | 2026-XX-XX   |
| Pi 1 (`192.168.0.11`) | *(fill in)*     | 2026-XX-XX   |
| Pi 2 (`192.168.0.12`) | *(fill in)*     | 2026-XX-XX   |

---

## Part 2: Install Netdata on Pi 1 (`192.168.0.11`)

### 2.1 Install Netdata

```bash
ssh skimlab@192.168.0.11
```

```bash
curl https://get.netdata.cloud/kickstart.sh > /tmp/netdata-kickstart.sh
sh /tmp/netdata-kickstart.sh --stable-channel
```

> [!warning] Pi Resource Usage
> Netdata is lightweight but monitor its impact on the Pi during the first hour. Check with:
> ```bash
> systemctl status netdata
> top -p $(pgrep -d, netdata)
> ```
> Expected: ~50-100MB RAM, <5% CPU on Pi 5. If it's too heavy, you can disable unused collectors (see Part 5).

### 2.2 Verify Installation

```bash
systemctl status netdata
curl -s http://localhost:19999/api/v1/info | head -5
```

Open `http://192.168.0.11:19999` and confirm:

- [x] System Overview (CPU, RAM, disk, temperature) ✅ 2026-03-27
- [x] Processes section (go2rtc, rpicam-vid should appear) ✅ 2026-03-27
- [x] systemd services section (go2rtc.service should appear) ✅ 2026-03-27

### 2.3 Verify Temperature Monitoring

Netdata auto-detects Pi temperature sensors. The Pi 5 uses these chart names:

```bash
# CPU temperature (main sensor)
curl -s "http://localhost:19999/api/v1/data?chart=sensors.temperature_cpu_thermal-virtual-0_temp1_input&points=1"

# RP1 ADC temperature (RP1 chip on Pi 5)
curl -s "http://localhost:19999/api/v1/data?chart=sensors.temperature_rp1_adc-isa-0000_temp1_input&points=1"
```

To discover all sensor chart names on any machine:
```bash
curl -s "http://localhost:19999/api/v1/charts" | grep -i "temp\|thermal" | grep '"id"'
```

---

## Part 3: Install Netdata on Pi 2 (`192.168.0.12`)

Repeat the exact same steps as Part 2:

```bash
ssh skimlab@192.168.0.12
```

```bash
curl https://get.netdata.cloud/kickstart.sh > /tmp/netdata-kickstart.sh
sh /tmp/netdata-kickstart.sh --stable-channel
```

Verify:

```bash
systemctl status netdata
```

Open `http://192.168.0.12:19999` and confirm:

- [x] System Overview ✅ 2026-03-27
- [x] go2rtc + rpicam-vid processes visible ✅ 2026-03-27
- [x] Temperature monitoring working ✅ 2026-03-27

---

## Part 4: Deploy Uptime Kuma on NVR

### 4.1 Create Data Directory

```bash
ssh skimlab@192.168.0.50
```

```bash
sudo mkdir -p /opt/uptime-kuma/data
sudo chown skimlab:skimlab /opt/uptime-kuma/data
```

### 4.2 Create Docker Compose File

Create `/opt/uptime-kuma/docker-compose.yml`:

```yaml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    volumes:
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock:ro
    network_mode: host
    restart: unless-stopped
```

> [!important] Use `network_mode: host`
> Do NOT use `ports: "3001:3001"`. The session daemon binds to `127.0.0.1:8585` (localhost only). With bridge networking, Docker containers cannot reach host localhost services. `network_mode: host` gives Uptime Kuma full access to the host network so all localhost services are reachable. The dashboard remains at port 3001.

> [!note] Separate from Frigate
> Uptime Kuma gets its own compose file in `/opt/uptime-kuma/` rather than being added to the Frigate compose file in `/srv/frigate/`. This keeps monitoring independent — if Frigate's compose stack has issues, Uptime Kuma still runs and can detect the problem.

### 4.3 Start Uptime Kuma

```bash
cd /opt/uptime-kuma
docker compose up -d
```

### 4.4 Verify

```bash
# Check container is running
docker ps | grep uptime-kuma

# Check web UI
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001
# Should return 200
```

### 4.5 Initial Configuration (Web UI)

Open `http://192.168.0.50:3001` in a browser.

1. **Create admin account** — set username and password (record securely)
2. **Add monitors** (click "Add New Monitor" for each):

#### Monitor 1: Session Daemon (Flask API)

| Setting | Value |
|---------|-------|
| Monitor Type | HTTP(s) |
| Friendly Name | Session Daemon |
| URL | `http://127.0.0.1:8585/api/health` |
| Heartbeat Interval | 60 seconds |
| Retries | 3 |
| Accepted Status Codes | 200 |

#### Monitor 2: Frigate NVR

| Setting | Value |
|---------|-------|
| Monitor Type | HTTP(s) |
| Friendly Name | Frigate NVR |
| URL | `http://127.0.0.1:5000/api/stats` |
| Heartbeat Interval | 60 seconds |
| Retries | 3 |
| Accepted Status Codes | 200 |

#### Monitor 3: Mosquitto MQTT

| Setting | Value |
|---------|-------|
| Monitor Type | TCP Port |
| Friendly Name | Mosquitto MQTT |
| Hostname | `127.0.0.1` |
| Port | `1883` |
| Heartbeat Interval | 60 seconds |

#### Monitor 4: go2rtc Pi 1

| Setting | Value |
|---------|-------|
| Monitor Type | HTTP(s) |
| Friendly Name | go2rtc Pi 1 |
| URL | `http://192.168.0.11:1984/api/streams` |
| Heartbeat Interval | 60 seconds |
| Retries | 3 |

#### Monitor 5: go2rtc Pi 2

| Setting | Value |
|---------|-------|
| Monitor Type | HTTP(s) |
| Friendly Name | go2rtc Pi 2 |
| URL | `http://192.168.0.12:1984/api/streams` |
| Heartbeat Interval | 60 seconds |
| Retries | 3 |

#### Monitor 6: Pi 1 Ping

| Setting | Value |
|---------|-------|
| Monitor Type | Ping |
| Friendly Name | Pi 1 Network |
| Hostname | `192.168.0.11` |
| Heartbeat Interval | 30 seconds |

#### Monitor 7: Pi 2 Ping

| Setting | Value |
|---------|-------|
| Monitor Type | Ping |
| Friendly Name | Pi 2 Network |
| Hostname | `192.168.0.12` |
| Heartbeat Interval | 30 seconds |

### 4.6 Configure Alerting (Optional)

In Uptime Kuma, go to **Settings > Notifications**:

**For Slack:**
1. Create a Slack incoming webhook at `https://api.slack.com/apps` → Incoming Webhooks
2. In Uptime Kuma: Add notification → Type: Slack → paste webhook URL
3. Set as default notification for all monitors

**For Email:**
1. Add notification → Type: SMTP
2. Fill in your SMTP server details
3. Set recipient email

> [!tip] Alert Timing
> With 60s heartbeat and 3 retries, an alert fires after ~3 minutes of downtime. For critical services, reduce heartbeat to 30s and retries to 2 (~1 minute detection).

---

## Part 5: Tuning (Optional)

### 5.1 Reduce Netdata Resource Usage on Pis

If Netdata uses too much CPU/RAM on the Pis, disable unused collectors:

```bash
sudo nano /etc/netdata/netdata.conf
```

Add under `[plugins]`:

```ini
[plugins]
    # Disable collectors not needed on Pi camera nodes
    apps = no          # Per-process resource tracking (CPU intensive)
    python.d = no      # Python-based collectors (if not needed)
```

Then restart:

```bash
sudo systemctl restart netdata
```

### 5.2 Reduce Netdata Retention (Save Disk on Pi)

Default retention is several days. To reduce to 1 day:

```bash
sudo nano /etc/netdata/netdata.conf
```

```ini
[db]
    mode = dbengine
    storage tiers = 1
    dbengine tier 0 disk space MB = 256
```

```bash
sudo systemctl restart netdata
```

### 5.3 Create Uptime Kuma Status Page

In Uptime Kuma web UI (`http://192.168.0.50:3001`):

1. Click **"Status Pages"** in the left sidebar
2. Click **"New Status Page"**
3. Name: `NeuroSurveillance`, Slug: `neurosurveillance` → click **Next**
4. Click **"Add Group"** → name it `NVR Services`
5. Click **"+"** inside the group → add: Session Daemon, Frigate NVR, Mosquitto MQTT
6. Click **"Add Group"** again → name it `Camera Nodes`
7. Click **"+"** → add: go2rtc Pi 1, go2rtc Pi 2, Pi 1 Network, Pi 2 Network
8. Click **"Save"**

Status page URL: `http://192.168.0.50:3001/status/neurosurveillance` ✅ 2026-03-30

---

## Part 6: Verification Checklist

After completing all parts, verify everything works:

- [x] `http://192.168.0.50:19999` — NVR Netdata dashboard loads, Docker containers visible ✅ 2026-03-30
- [x] `http://192.168.0.11:19999` — Pi 1 Netdata dashboard loads, go2rtc process visible ✅ 2026-03-30
- [x] `http://192.168.0.12:19999` — Pi 2 Netdata dashboard loads, go2rtc process visible ✅ 2026-03-30
- [x] `http://192.168.0.50:3001` — Uptime Kuma loads, all 7 monitors green ✅ 2026-03-30
- [x] Slack notifications configured ✅ 2026-03-30
- [x] Status page at `http://192.168.0.50:3001/status/neurosurveillance` ✅ 2026-03-30
- [ ] Stop go2rtc on Pi 1 (`sudo systemctl stop go2rtc`), confirm Uptime Kuma alert fires within ~3 minutes
- [ ] Restart go2rtc (`sudo systemctl start go2rtc`), confirm Uptime Kuma shows recovery
- [ ] Netdata survives machine reboot: `sudo reboot` on a Pi, confirm Netdata auto-starts

---

## Part 7: Maintenance

### Updating Netdata

Netdata auto-updates by default. To update manually:

```bash
sudo /usr/libexec/netdata/netdata-updater.sh
```

### Updating Uptime Kuma

```bash
cd /opt/uptime-kuma
docker compose pull
docker compose up -d
```

### Uninstalling Netdata

If you need to remove it from a machine:

```bash
sudo /usr/libexec/netdata/netdata-uninstaller.sh --yes --env /etc/netdata/.environment
```

### Removing the Apt Pin on WebKitGTK

> [!note] Related Issue
> WebKitGTK `2.50.4` is pinned to `2.44.0-2` due to a bug — see [[03-troubleshooting/incidents/2026-03-24-webkit-internal-error-tauri]]. When Ubuntu ships `2.52+`, test removing the pin:
> ```bash
> sudo rm /etc/apt/preferences.d/pin-webkitgtk
> sudo apt upgrade
> npm run tauri dev  # test the GUI
> ```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Lab Network (192.168.0.0/24)                  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           NVR (192.168.0.50)                            │    │
│  │                                                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────────┐     │    │
│  │  │ Frigate   │  │Mosquitto │  │ Session Daemon    │     │    │
│  │  │ :5000     │  │ :1883    │  │ :8585 (localhost) │     │    │
│  │  └──────────┘  └──────────┘  └───────────────────┘     │    │
│  │                                                         │    │
│  │  ┌──────────────┐  ┌──────────────────┐                │    │
│  │  │ Netdata      │  │ Uptime Kuma      │                │    │
│  │  │ :19999       │  │ :3001            │                │    │
│  │  │ (system +    │  │ (service alerts  │                │    │
│  │  │  Docker)     │  │  + status page)  │                │    │
│  │  └──────────────┘  └───────┬──────────┘                │    │
│  └─────────────────────────────┼───────────────────────────┘    │
│                                │ checks                         │
│  ┌─────────────────────┐      │      ┌─────────────────────┐   │
│  │  Pi 1 (192.168.0.11)│◄─────┼─────►│  Pi 2 (192.168.0.12)│   │
│  │                     │      │      │                     │   │
│  │  go2rtc :8554,:1984 │      │      │  go2rtc :8554,:1984 │   │
│  │  pi_cam_0, pi_cam_1 │             │  pi_cam_2, pi_cam_3 │   │
│  │  Netdata :19999     │             │  Netdata :19999     │   │
│  └─────────────────────┘             └─────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Browser access:
  Netdata NVR:  http://192.168.0.50:19999
  Netdata Pi1:  http://192.168.0.11:19999
  Netdata Pi2:  http://192.168.0.12:19999
  Uptime Kuma:  http://192.168.0.50:3001
```

---
tags: [procedure, installation, monitoring, netdata, uptime-kuma]
created: 2026-03-24
updated: 2026-04-01
status: production
---

# Centralized Monitoring Setup (Netdata + Uptime Kuma)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A procedure for installing Netdata on all 3 machines (NVR + 2 Pis) and Uptime Kuma on the NVR for service-level health checks with Slack alerts.
>
> **Why it exists.** Without it, the first sign of a problem is usually a researcher reporting failed recordings hours later. With it, the right people get a Slack ping within ~3 minutes of anything going down.
>
> **How to read this page.** Parts 1-3 install Netdata on each machine; Part 4 installs Uptime Kuma; Part 8 configures the 16 NVR-specific Netdata alerts. The "Persistent Frigate Python Logs" section (added 2026-05-22) explains how to read the persistent log file under `/srv/frigate/logs/frigate/`.

> [!quote] Paper-ready
> Centralized monitoring is provided by Netdata (real-time system and Docker metrics on all 3 machines) and Uptime Kuma (HTTP/TCP/ping checks for 7 service endpoints), with all alerts routed to a shared Slack webhook for ~3-minute incident detection.

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
- [x] Stop go2rtc on Pi 1 (`sudo systemctl stop go2rtc`), confirm Uptime Kuma alert fires within ~3 minutes ✅ 2026-04-01
- [x] Restart go2rtc (`sudo systemctl start go2rtc`), confirm Uptime Kuma shows recovery ✅ 2026-04-01
- [x] Netdata survives machine reboot: `sudo reboot` on a Pi, confirm Netdata auto-starts ✅ 2026-04-01

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

### Persistent Frigate Python Logs (since 2026-05-22)

Frigate's Python-side process logs were previously tmpfs-only inside the container — every `docker restart` wiped them, so post-mortem debugging required catching the logs live with `docker compose logs -f frigate`. Since 2026-05-22 a host volume mount makes them persistent:

```bash
# Tail the current Frigate log (host path, persistent across container restarts)
sudo tail -f /srv/frigate/logs/frigate/current

# Find the most recent stall or error
sudo grep -iE "error|stall|exception" /srv/frigate/logs/frigate/current | tail -20

# Disk usage of the persistent log dir (rotates roughly daily)
sudo du -sh /srv/frigate/logs/frigate/
```

The mount is declared in `/srv/frigate/docker-compose.yml` as `./logs/frigate:/dev/shm/logs/frigate`. The container's internal tmpfs at `/dev/shm/logs/frigate` is now backed by the host directory, so the rotation pattern stays the same — just the location is durable.

No `docker compose` action required after a fresh checkout: the volume is part of the compose file. If you ever rebuild from scratch, follow [[frigate-setup|the Frigate setup procedure]] and the `./logs/frigate` directory is created on first `docker compose up -d`.

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

---

## Part 8: NVR Netdata Alert Configuration

> [!info] Why Custom Alerts?
> Netdata ships with **227 default alerts** — most irrelevant for an NVR (Ceph, Kubernetes, Redis, etc.). Rather than receiving noise, we silence all defaults and define only what matters for video surveillance.

See [[01-infrastructure/netdata/nvr-alerts-config|NVR Alerts Golden Config]] for the full configuration reference and management guide.

### 8.1 Silence Default Alerts

Edit `/etc/netdata/netdata.conf`:

```ini
[health]
    enabled alarms = nvr_*
```

This single line filters all 227 defaults. Only alerts prefixed with `nvr_` are loaded.

### 8.2 Create NVR-Specific Alerts

Create `/etc/netdata/health.d/nvr-alerts.conf` with 9 alert definitions covering:

| Category | Alerts | What it catches |
|----------|--------|-----------------|
| CPU | `nvr_cpu_high`, `nvr_cpu_iowait` | Frigate ffmpeg overload, disk I/O bottleneck |
| Memory | `nvr_ram_usage`, `nvr_swap_usage` | OOM risk, memory pressure |
| Disk | `nvr_disk_space`, `nvr_disk_inodes` | Recording storage filling up |
| Docker | `nvr_container_unhealthy`, `nvr_container_down` | Frigate/Mosquitto/Uptime Kuma failures |
| Temperature | `nvr_cpu_temperature` | NUC thermal throttling |

These 9 definitions expand to **16 active alert instances** (disk alerts instantiate per mount point, Docker alerts per container).

### 8.3 Configure Slack Notifications

Create `/etc/netdata/health_alarm_notify.conf`:

```bash
SEND_EMAIL="NO"
# ... (disable all other methods)

SEND_SLACK="YES"
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
DEFAULT_RECIPIENT_SLACK="#"
role_recipients_slack[sysadmin]="#"
```

> [!history] Historical note (pre-2026-09-14)
> Both tools posted to the same Slack webhook/channel — Uptime Kuma for up/down events, Netdata for threshold alerts. Replaced 2026-09-14 with ntfy (below) to stop cluttering a private Slack DM; the webhook itself is left in the config, commented off via `SEND_SLACK="NO"`, in case Slack is ever wanted again.

### 8.3b Switched to ntfy (2026-09-14)

Netdata alerts and Uptime Kuma alerts now both push to a phone via [ntfy](https://ntfy.sh) (public server, no self-hosting — a self-hosted container was tried first and abandoned because it only worked over Tailscale, not off-network) instead of Slack.

Topic: `nvr-b39a24e80833bb95` (generated with `openssl rand -hex 8` — long and random on purpose, since ntfy.sh topics have no auth and anyone who knows the name can publish/read it).

`/etc/netdata/health_alarm_notify.conf`:

```bash
SEND_EMAIL="NO"
# ... (disable all other methods)

SEND_NTFY="YES"
DEFAULT_RECIPIENT_NTFY="https://ntfy.sh/nvr-b39a24e80833bb95"
role_recipients_ntfy[sysadmin]="https://ntfy.sh/nvr-b39a24e80833bb95"
role_recipients_ntfy[nvr]="https://ntfy.sh/nvr-b39a24e80833bb95"

SEND_SLACK="NO"
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
DEFAULT_RECIPIENT_SLACK="#"
```

> [!warning] `DEFAULT_RECIPIENT_NTFY` must be the FULL URL, not just the topic
> This Netdata build (v2.11.0) has no `NTFY_SERVER` variable — despite that name appearing in some online examples/older docs. `send_ntfy()` in `/usr/libexec/netdata/plugins.d/alarm-notify.sh` passes `${recipient}` straight to curl as the request URL. Setting `DEFAULT_RECIPIENT_NTFY` to just the topic name (e.g. `nvr-b39a24e80833bb95`) makes curl try to resolve it as a bare hostname — `curl: (6) Could not resolve host` — with **no visible config error**, it just silently fails every send. Always use the full `https://ntfy.sh/<topic>` (or self-hosted server URL) as the recipient value.

Uptime Kuma: Settings → Notifications → Add → type `ntfy` → server `https://ntfy.sh`, topic `nvr-b39a24e80833bb95` → apply to all monitors. No equivalent gotcha there — Kuma has separate server/topic fields.

Phone: ntfy app → subscribe → topic `nvr-b39a24e80833bb95` → server `ntfy.sh` (default, no need to override).

- [x] Netdata → ntfy tested via `alarm-notify.sh test`, all 3 (WARNING/CRITICAL/CLEAR) `httpcode 200` ✅ 2026-09-14
- [x] Uptime Kuma → ntfy notification added and applied to all monitors ✅ 2026-09-14

### 8.4 Apply and Verify

```bash
sudo systemctl restart netdata
```

Wait 10-15 seconds, then verify 16 alerts are active:

```bash
curl -s http://localhost:19999/api/v1/alarms?all | python3 -c "
import sys,json
d=json.load(sys.stdin)
alarms=d.get('alarms',{})
print(f'Total alerts: {len(alarms)}')
for k in sorted(alarms.keys()):
    a=alarms[k]
    print(f'  [{a[\"status\"]}] {k}')
"
```

### 8.5 Test Slack Integration

```bash
sudo /usr/libexec/netdata/plugins.d/alarm-notify.sh test
```

Should send 2 test messages (WARNING + CRITICAL) to your Slack channel.

### 8.6 Real-World Validation

Stop a container to trigger an actual alert:

```bash
docker stop mosquitto
# Wait ~30 seconds → Slack WARNING notification
docker start mosquitto
# Wait ~1 minute → Slack CLEAR (recovery) notification
```

- [x] Netdata alert config deployed (16 alerts, 227 silenced) ✅ 2026-04-01
- [x] Slack notifications tested via `alarm-notify.sh test` ✅ 2026-04-01
- [x] Real-world test: Mosquitto stop → Slack alert → restart → recovery ✅ 2026-04-01

---
type: procedure
area: video-nvr
status: active
tags: [procedure, installation, frigate, docker]
created: 2026-02-12
---

# Frigate NVR + Mosquitto MQTT Setup

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The step-by-step deployment procedure for Frigate + Mosquitto on the NVR machine. Used when bringing up a fresh NVR or rebuilding after a hardware swap.
>
> **Why it exists.** Reproducibility. If the NVR fails, this procedure restores the recording stack in ~1 hour.
>
> **How to read this page.** Top to bottom, ticking each prerequisite first. Step 4 (Mosquitto auth) requires the password from [[production-values|production-values.md]] — fetch it before you start. The Validation section confirms everything works end-to-end.

> [!quote] Paper-ready
> The Frigate NVR and Mosquitto MQTT broker are deployed as Docker Compose services on the NVR machine via a reproducible 8-step procedure covering prerequisites, directory structure, authenticated MQTT configuration, Frigate config, container deployment, hardware-acceleration verification, recording test, and MQTT integration verification.

## Purpose

Deploy Frigate NVR with Mosquitto MQTT broker on the NUC for recording RTSP camera streams from Raspberry Pi nodes. This procedure was validated on `e10ubuntu` (`192.168.0.50`) on 2026-02-12.

## Prerequisites Checklist

- [ ] Ubuntu 24.04 LTS (or compatible) on NUC
- [ ] Docker and Docker Compose v2 installed
- [ ] User in `docker` group (`sudo usermod -aG docker $USER`)
- [ ] User in `render` group (`sudo usermod -aG render $USER`)
- [ ] `/dev/dri/renderD128` exists with `render` group permissions
- [ ] VA-API working: `vainfo` shows `VAProfileH264High: VAEntrypointVLD`
- [ ] At least one Pi camera node streaming via go2rtc (see [[new-pi-setup|New Pi Setup]])
- [ ] Static IP assigned (currently `{NVR_IP}` = `192.168.0.50`)

## Your Values (from [[production-values|Production Values]])

| Variable | Value |
|----------|-------|
| `{NVR_IP}` | `192.168.0.50` |
| `{NVR_USER}` | `skimlab` |
| `{PI_IP}` | `192.168.0.11` |
| `{FRIGATE_DIR}` | `/srv/frigate` |
| `{MQTT_PORT}` | `1883` |
| `{FRIGATE_WEB_PORT}` | `5000` |

---

## Steps

### 1. Verify Prerequisites

```bash
ssh skimlab@192.168.0.50

# Check Docker
docker compose version
# Expected: Docker Compose version v2.x.x

# Check GPU access
ls -la /dev/dri/renderD128
# Expected: crw-rw---- 1 root render ...

# Check group membership
groups
# Expected: includes 'docker' and 'render'

# Check VA-API
vainfo 2>&1 | grep -i "h264.*VAEntrypointVLD"
# Expected: VAProfileH264High : VAEntrypointVLD
```

### 2. Verify Pi Streams Are Accessible

```bash
# Test RTSP connectivity from NUC to Pi
curl -s http://192.168.0.11:1984/api/streams | python3 -m json.tool
# Expected: JSON with pi_cam_0 and pi_cam_1 entries
```

### 3. Create Directory Structure

```bash
sudo mkdir -p /srv/frigate/{config,storage,mosquitto}
sudo chown -R skimlab:skimlab /srv/frigate
```

### 4. Deploy Mosquitto Configuration

```bash
nano /srv/frigate/mosquitto/mosquitto.conf
```

Paste the following:

```ini
listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd
persistence false
log_dest stdout
```

Then create the password file. The plaintext password is in [[production-values#Mosquitto MQTT Authentication (since 2026-05-22)|production-values.md]]; never put it into a public repo.

```bash
# Start mosquitto once so we can use mosquitto_passwd from inside the container.
cd /srv/frigate && docker compose up -d mosquitto

# Create the passwd file (replace <PLAINTEXT> with the value from production-values.md).
docker exec mosquitto mosquitto_passwd -c -b /tmp/passwd nvr <PLAINTEXT>
docker exec mosquitto cat /tmp/passwd | sudo tee /srv/frigate/mosquitto/passwd > /dev/null

# Restart mosquitto so it picks up the new auth config + password file.
docker compose restart mosquitto
```

> [!history] Historical note — pre-2026-05-22
> Before 2026-05-22 this step used `allow_anonymous true` and no `password_file`; the rationale was "acceptable for an isolated lab LAN with no internet exposure." The current step requires auth so a compromised LAN device cannot inject Frigate state changes (which would create phantom sessions or stop recordings). Full pre-change text: [[frigate-setup-mosquitto-2026-05-22|archived setup step]].

### 5. Deploy Frigate Configuration

```bash
nano /srv/frigate/config/config.yml
```

Paste the configuration from [[config-yml|Frigate Config v5.1]]

> [!warning] Replace Variables
> Replace all `{VARIABLE}` placeholders with actual values from [[production-values|Production Values]] before deploying.

### 6. Deploy Docker Compose

```bash
nano /srv/frigate/docker-compose.yml
```

Paste the configuration from [[docker-compose|Docker Compose v5.1]]

### 7. Start Services

```bash
cd /srv/frigate
docker compose up -d
```

**Expected:** Both containers start without errors.

```bash
docker compose ps
# Expected: mosquitto (healthy), frigate (healthy)
```

> [!tip] First Launch
> Frigate auto-generates an admin user and random password on first launch. Check the container logs to find it:
> ```bash
> docker compose logs frigate 2>&1 | grep -i password
> ```
> **Change this password immediately** via the Frigate web UI at `http://192.168.0.50:5000`.

### 8. Wait for Initialization

Frigate needs ~30 seconds to initialize ffmpeg processes for all cameras.

```bash
# Watch logs for stream connections
docker compose logs -f frigate 2>&1 | grep -E "(started|error|camera)" | head -20
```

---

## Validation

### Camera Streams

```bash
# Check Frigate stats
curl -s http://localhost:5000/api/stats | python3 -m json.tool
```

Verify:
- Both cameras show `"camera_fps"` > 0
- `"detection_fps"` is 0 (detection disabled — this is correct)
- Process CPU/memory are reasonable

### QSV Hardware Acceleration

```bash
curl -s http://localhost:5000/api/stats | python3 -m json.tool | grep -A5 gpu
```

**Expected:** GPU usage > 0% confirms QSV is active.

Also verify ffmpeg is using QSV:

```bash
docker exec frigate ps aux | grep ffmpeg
# Expected: -hwaccel qsv -qsv_device /dev/dri/renderD128 -c:v h264_qsv
```

### Recording

1. Open Frigate UI at `http://192.168.0.50:5000`
2. Navigate to a camera
3. Enable recording via the UI toggle
4. Wait >10 seconds
5. Check recordings appear: `ls -la /srv/frigate/storage/recordings/`

### Export

```bash
# Export a time range (replace timestamps with actual unix timestamps)
curl -X POST "http://localhost:5000/api/export/pi_cam_0/start/{START_TS}/end/{END_TS}"
# Check exports
ls -la /srv/frigate/storage/exports/
```

### MQTT

```bash
docker compose logs mosquitto | tail -5
# Expected: "mosquitto version X.X.X running" with no errors

# Verify Frigate is connected. NVR_MQTT_PASSWORD is in production-values.md.
docker exec mosquitto mosquitto_sub \
    -u nvr -P "$NVR_MQTT_PASSWORD" \
    -t 'frigate/#' -C 1 -W 5
# Expected: receives at least one message within 5 seconds
```

> [!warning] Auth required since 2026-05-22
> `mosquitto_sub` and `mosquitto_pub` without `-u nvr -P …` will fail with `Connection error: Bad user name or password`. If you see that error, you forgot the credentials, not a bug.

---

## Performance Baseline (2-camera setup)

| Metric | Expected |
|--------|----------|
| Frigate CPU | ~10% |
| Frigate Memory | ~900 MB |
| GPU (QSV) | ~1.5% |
| Mosquitto CPU | ~0.03% |
| Mosquitto Memory | ~2.5 MB |
| Detect FPS (per camera) | ~5 fps |
| Recording FPS | 15 fps (pass-through, `-c:v copy`) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `gpu` shows 0% in stats | QSV not active. Check `/dev/dri/renderD128` permissions, `render` group membership, and `vainfo` output |
| Camera shows 0 fps | RTSP source unreachable. Verify Pi go2rtc is running: `curl http://192.168.0.11:1984/api/streams` |
| Container exits immediately | Check logs: `docker compose logs frigate`. Common: YAML syntax error in `config.yml` |
| "Permission denied" on `/dev/dri` | Add user to `render` group and restart: `sudo usermod -aG render skimlab && newgrp render` |
| Meteor Lake GPU lockup | Fallback to CPU-only: set `hwaccel_args: " "` in Frigate config (removes all QSV) |
| High CPU without QSV | Expected ~40-50% CPU for 2 cameras without hardware decode. Re-enable QSV. |
| MQTT connection refused | Check Mosquitto is running: `docker compose ps mosquitto`. Check port 1883 is not blocked. |
| Recording segments missing | Verify `record: enabled: true` in config. Check storage permissions on `/srv/frigate/storage/` |

---

## Related

- [[new-pi-setup|New Pi Setup]] — prerequisite Pi camera node deployment
- [[docker-compose|Docker Compose Golden Config]]
- [[config-yml|Frigate Config Golden Config]]
- [[production-values|Production Values]]
- [[golden-go2rtc-config|go2rtc Config]] — Pi-side streaming

---

**First deployed:** 2026-02-12
**Deployed by:** Andrea
**Target host:** `e10ubuntu` (`192.168.0.50`)

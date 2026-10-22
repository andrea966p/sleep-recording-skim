---
type: reference
area: computing
status: active
tags: [config, production, sensitive]
created: 2026-02-04
updated: 2026-04-02
---

# Production Configuration Values

> [!warning] Updated 2026-10-22: Netdata and Uptime Kuma alerts moved from Slack to ntfy on 2026-09-14, and the deploy scripts (`nvr-notify.sh`) on 2026-09-20 [[monitoring-setup]]. Recording-stall and reconciler alerts still go to Slack through `nvr-mqtt-slack.service` (active 2026-10-22), so `{MQTT_SLACK_ENV}` is still live. All cameras were removed on 2026-08-04, so the camera rows below do not point at running streams [[nvr-alerts-config]]

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
| **Netdata (NVR)** | http://192.168.0.50:19999 | ✅ active |
| **Netdata (Pi 1)** | http://192.168.0.11:19999 | ✅ active |
| **Netdata (Pi 2)** | http://192.168.0.12:19999 | ✅ active |
| **Uptime Kuma** | http://192.168.0.50:3001 | ✅ active |
| **Status Page** | http://192.168.0.50:3001/status/neurosurveillance | ✅ active |

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

### Tailscale (rewritten 2026-08-19 — the old table was six months stale and caused a multi-day misdiagnosis)

> [!warning] There are FOUR tailnets. A machine belongs to exactly one at a time.
> Every address below changes if a machine is moved between tailnets. **Never hardcode a
> `100.x` literal in a script — use the MagicDNS name.** Stale literals have now caused three
> separate outages here. See [[2026-08-19-nas-backup-wrong-address]].

| Tailnet | MagicDNS suffix | What lives there |
|---|---|---|
| `skimlab.kaist@gmail.com` | `tail706d43.ts.net` | the NVR and the lab laptops — **this is the NVR's tailnet** |
| `bilab.kaist@gmail.com`   | `tail8808c0.ts.net` | the Synology NAS and the office PC's LAN |
| `andrea.piazzola4@gmail.com` | `tail9039f9.ts.net` | home tailnet (Raspberry Pi, Home Assistant) |
| `sleepigene@` | `tailec38b9.ts.net` | the **SKIM Lab** Synology (`SKIM_NAS`) — added 2026-09-11 |

**Members of the NVR's tailnet (`skimlab.kaist@gmail.com`), as of 2026-08-19:**

| Device | Tailscale IP | MagicDNS name | Owner |
|---|---|---|---|
| `e10ubuntu` (NVR) | `100.82.250.62` | `e10ubuntu.tail706d43.ts.net` | skimlab.kaist@ |
| `thinkpadubuntu` | `100.66.98.20` | `thinkpadubuntu.tail706d43.ts.net` | andrea.piazzola4@ |
| `Andrea-KAIST-PC-ubuntu` | `100.125.44.24` | `andrea-kaist-pc-ubuntu.tail706d43.ts.net` | andrea.piazzola4@ |
| `Skim` | `100.107.145.68` | `skim.tail706d43.ts.net` | skimlab.kaist@ |
| `sleepi-BOOK` | `100.72.151.79` | `sleepi-book.tail706d43.ts.net` | skimlab.kaist@ |

**Shared INTO the NVR's tailnet (not members):**

| Device | Tailscale IP | MagicDNS name | Shared from |
|---|---|---|---|
| `Bilab_Syn` (the NAS) | `100.120.86.9` | `bilab-syn.tail8808c0.ts.net` | bilab.kaist@ |
| `SKIM_NAS` (the SKIM Lab NAS) | `100.85.231.100` | `skim-nas.tailec38b9.ts.net` | sleepigene@ |

> [!tip] The SKIM_NAS path is DIRECT, not relayed
> Measured 2026-09-11: `CurAddr 143.248.26.53:49231`, **1 ms RTT**, both ends on the KAIST
> campus network. The first `tailscale ping` reported `via DERP(tok)` only because
> hole-punching had not completed — wait and re-ping before concluding a peer is relayed.
> Real throughput over CIFS: **write 94 MB/s, read 90 MB/s.**

> [!note] Why `andrea.piazzola4@gmail.com` appears twice
> That one Google account is **both** a member user of the skimlab tailnet **and** the owner of
> the separate home tailnet whose devices are shared in. Tailscale shows them under two different
> user IDs. This dual role is the single biggest source of confusion when debugging access — always
> ask *which* of the two roles a given device is using.

> [!danger] Retired addresses — do not use, they belong to nothing now
> `100.85.191.25` was the NVR **in the bilab tailnet**. `100.117.204.8` was the office PC in the
> same. `100.120.86.10` was the NAS's old address. All three appear in older vault pages and in
> `~/.config/rustdesk/RustDesk2.toml`; none of them resolve today.

---

## SKIM Lab NAS — EEG recording archive (since 2026-09-11)

The destination for channel-stripped Allego recordings. A **different NAS** from the
`Bilab_Syn` one used by the nightly project backup below; do not confuse the two.

| Variable | Production Value | Notes |
|----------|------------------|-------|
| `{SKIMNAS_HOST}` | `skim-nas.tailec38b9.ts.net` | Synology `SKIM_NAS`, currently `100.85.231.100`, shared in from `sleepigene@`. **Use the name, never the IP.** |
| `{SKIMNAS_SHARE}` | `SKIM_DATA` | SMB share |
| `{SKIMNAS_ROOT}` | `02_Data_Sleep` | per-user folders: `andrea`, `diane`, `ahyeon`, `hyunmin`, `staci`. Was `03_Data_Mouse` until 2026-09-29; set by `nas.root` in `eeg-recorder/config/users.yaml`. Takes effect when `eeg-recorder.service` restarts |
| `{SKIMNAS_USER}` | `skim.data` | read/write confirmed |
| `{SKIMNAS_MOUNT}` | `/mnt/skimnas` | `mnt-skimnas.automount`, mounts on access, unmounts after 600 s idle |
| `{SKIMNAS_DSM}` | `https://skim-nas.tailec38b9.ts.net:50011` | DSM web UI (`:80`/`:443` redirect to `:50000`/`:50011`) |
| Auth | `/etc/skim-nas.cred` | 0600 root:root, written by a human. **SSH is CLOSED on this NAS** (22, 53, 222, 2022, 2222, 5022, 8022, 22022 all tried) — SMB is the only data path. |
| Dialect | `vers=3.1.1` | worked first try on DSM 7 |
| Capacity | 7.0 TB, **1.3 TB free** (82% used) as of 2026-09-11 | the whole stripped corpus is ~78 GB; 843 GB of raw would fit but leave ~450 GB |

> [!danger] The mount guard is not optional
> A failed CIFS mount leaves `/mnt/skimnas` as an ordinary empty directory **on the recording
> machine's own NVMe — the same filesystem the amplifiers write to**. An uploader that cannot
> tell the difference will quietly fill it. `mountpoint` alone does NOT catch this, because an
> empty local directory is a valid mountpoint. Hence the sentinel
> `/mnt/skimnas/{SKIMNAS_ROOT}/.skim-nas-share` (so `02_Data_Sleep/.skim-nas-share` since 2026-09-29), which exists only on the share: the uploader
> refuses to write unless it can read that file. Observed to refuse while unmounted, 2026-09-11.

> [!danger] Read-back verification is VACUOUS unless the page cache is dropped
> Measured 2026-09-11: reading a just-written 200 MB file back over the mount ran at
> **1538 MB/s** — entirely from the local page cache, verifying our own memory rather than
> anything on the NAS. After `os.posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED)` the same read
> ran at **89.8 MB/s**, the real network rate, and the hash matched. Any verification that
> skips the fadvise is a gate that cannot fail.

---

## NAS Backup (daily project snapshot, since 2026-05-26)

| Variable | Production Value | Notes |
|----------|------------------|-------|
| `{NAS_HOST}` | `bilab-syn.tail8808c0.ts.net` | Synology NAS (`Bilab_Syn`, currently `100.120.86.9`, LAN `192.168.0.21` on the **office** network — not reachable from the NVR's LAN). **Use the name, never the IP.** |
| `{NAS_SSH_PORT}` | `53` | non-default SSH port |
| `{NAS_USER}` | `Andrea` | NAS account (≠ NVR user `skimlab`) |
| `{NAS_BACKUP_DIR}` | `e10_setup_backups` | relative to NAS user home |
| Auth | key-based | `skimlab`'s `~/.ssh/id_ed25519` → NAS `Andrea` |
| Schedule | `00:00` daily | `nas-backup.timer` |
| Retention | 3 snapshots | rolling, oldest deleted each run |
| Excludes | videos / build artifacts / `radiens.log` | see procedure |

Setup + ops: [[nas-backup|NAS Backup procedure]].

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
| `{NETDATA_PORT}` | `19999` | Netdata dashboard |
| `{UPTIME_KUMA_PORT}` | `3001` | Uptime Kuma dashboard |
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
| `{CAMERA_BITRATE}` | `1500000` | 1.5 Mbps target (actual measured: 1.7 Mbps due to VBR + container overhead) |

---

## Directory Paths

### EEG recording paths (on the NVR / rig)
| Variable | Value | Notes |
|----------|-------|-------|
| `{RAW_ROOT}` | `/home/skimlab/radix/data` | where Allego writes recordings. **Read-only to tooling**: nothing may write, move or delete here. Env override `EEG_RAW_ROOT` |
| `{STRIPPED_ROOT}` | `/home/skimlab/radix/stripped` | channel-stripped copies. Deliberately a **SIBLING** of `{RAW_ROOT}`, never inside it, so stripped twins stay out of `radix-archive.sh`'s `ls -1 "$SRC"` and every pipeline glob. Env override `EEG_STRIPPED_ROOT` |
| `{CACHE_ROOT}` | `/home/skimlab/eeg-qc-cache` | per-recording QC feature caches. Env override `EEG_CACHE_ROOT` |
| `{RECORDER_STATE}` | `~/.local/state/eeg-recorder` | the recording console's run database (`runs.db`, SQLite WAL). Env override `EEG_RECORDER_STATE` |
| `{ALLEGO_DEVICES}` | `/home/skimlab/radix/devices` | headstage/probe maps (`.hstg`, YAML). Backed up nightly |
| `{ALLEGO_WORKSPACE}` | `/home/skimlab/radix/workspace` | Allego workspace settings. Backed up nightly |

> [!warning] `~/radix/data` IS READ-ONLY TO EVERY TOOL
> Standing instruction, 2026-09-11: tooling reads recordings from `{RAW_ROOT}` and writes derived
> copies elsewhere. Raw recordings are moved to the NAS by a human. The stripper, the uploader and
> the recording console all obey this.

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
| `{SESSION_DAEMON_REPO}` | `/home/skimlab/sleep-recording-skim/neurosurveillance` |
| `{SESSION_DAEMON_GITHUB}` | `git@github.com:andrea966p/neurosurveillance.git` (private) |
| `{UPTIME_KUMA_DIR}` | `/opt/uptime-kuma` |
| `{NETDATA_CONFIG_DIR}` | `/etc/netdata` |
| `{NETDATA_ALERTS_FILE}` | `/etc/netdata/health.d/nvr-alerts.conf` |
| `{NETDATA_NOTIFY_FILE}` | `/etc/netdata/health_alarm_notify.conf` |
| `{SESSION_LOG_DIR}` | `/opt/neurosurveillance/logs` |
| `{SESSION_EXPORT_DIR}` | `/srv/frigate/storage/exports` | Frigate Docker volume — raw exports (root-owned) |
| `{SESSION_DATA_DIR}` | `/opt/neurosurveillance/sessions` |
| `{EXPORT_DIR}` | `/opt/neurosurveillance/exports` | Organized exports (skimlab-owned, user-deletable) |
| `{SUDOERS_POLICY}` | `/etc/sudoers.d/neurosurveillance-fs` |
| `{MQTT_SLACK_ENV}` | `/etc/nvr-mqtt-slack.env` (mode 0600 — secrets for `nvr-mqtt-slack.service`: `NVR_MQTT_PASSWORD` + `SLACK_WEBHOOK_URL`) |

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
| Docker CE | `29.3.1` (needs `apt-mark hold` — see [[2026-04-01\|2026-04-01 journal]]) |
| Docker Compose | `v5.1.1` |
| Frigate | `0.16.1` (pinned in docker-compose.yml) |
| Netdata | `2.9.0` (installed 2026-03-27, 16 custom NVR alerts) |
| Uptime Kuma | `louislam/uptime-kuma:1` (Docker, 7 monitors) |

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

## Recording & Storage Settings

| Variable | Value | Notes |
|----------|-------|-------|
| `{RETENTION_DAYS}` | `7` | Video retention |
| `{STORAGE_PER_CAM_DAY}` | `~18GB` | Measured: 1.7 Mbps × 86400s / 8 ≈ 18.4 GB per camera per day |
| `{MANUAL_SESSION_MIN_DURATION}` | `5` | Min seconds for manual recording export (filters accidental clicks) |
| `{EEG_RESERVE_GB}` | `200` | Hard disk reserve for XDAQ EEG/EMG data — recording blocked below this |
| `{STORAGE_WARN_PERCENT}` | `75` | UI turns yellow at this disk usage |
| `{STORAGE_CRITICAL_PERCENT}` | `90` | UI turns red, recordings may be blocked |
| `{CAMERA_ACTUAL_BITRATE_MBPS}` | `1.7` | Measured from actual recordings (configured 1.5 + VBR/container overhead) |

---

## Hardware Sync Variables

> [!check] 2026-06-21 — gate moved `DAQ_ON` (pin 13) → `DO 03` (pin 22)
> Recording gate = **`DO 03`** (DB25 pin 22, Allego "Gated" mode + "BNC Breakout Board" toggle), **not** `DAQ_ON` (which tracks streaming + emits idle pulses). Pi input pin unchanged (GPIO 17). Variable renamed `{GPIO_DAQ_ON}` → `{GPIO_GATE}`; `{XDAQ_DAQ_ON_PIN}` retained as an optional streaming-flag reference only. See [[wiring-guide|wiring-guide]].

| Variable | Value | Notes |
|----------|-------|-------|
| `{GPIO_GATE}` | `17` | Pi GPIO pin receiving XDAQ `DO 03` recording gate (physical pin 11). Was `{GPIO_DAQ_ON}`. |
| `{GPIO_FRAME}` | `27` | Pi GPIO pin sending frame sync pulses to XDAQ DIN (physical pin 13) |
| `{XDAQ_DIN_CHANNEL}` | `DI 03` | XDAQ digital input channel (DB25 Pin 2); DI 04–06 = pins 15/3/16 for Pis 2–4 |
| `{XDAQ_GATE_PIN}` | `22` | ★ DB25 pin number for `DO 03` recording gate (HIGH while recording, "Gated" mode) |
| `{XDAQ_DAQ_ON_PIN}` | `13` | DB25 pin for `DAQ_ON` — streaming indicator only (idle ~0.5 s pulses); NOT the gate |
| `{XDAQ_GND_PIN}` | `14` | DB25 pin number for SYS GND (star-ground hub) |
| `{MQTT_SYNC_TOPIC}` | `neurosurveillance/hardware_sync` | MQTT topic for GPIO sync events |
| `{GPIO_SYNC_SERVICE}` | `gpio-sync.service` | systemd service name on Pi |
| `{GPIO_SYNC_SCRIPT}` | `/opt/neurosurveillance/gpio_sync.py` | Script path on Pi |

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

## Mosquitto MQTT Authentication (since 2026-05-22)

| Field | Value |
|-------|-------|
| Broker | `mqtt://192.168.0.50:1883` |
| Username | `nvr` |
| Password | `VBwzGOQSnUqHkMV9qEwksygU8KzZiQPU` |
| `allow_anonymous` | `false` |
| `password_file` | `/mosquitto/config/passwd` (inside container) = `/srv/frigate/mosquitto/passwd` (host) |
| passwd perms | `0600`, owned `1883:1883` (mosquitto's UID; locked down 2026-05-25) |

Hash on disk is mosquitto's `$7$` format generated via `docker exec mosquitto mosquitto_passwd -c -b /tmp/passwd nvr <plaintext>`.

**Consumers of these credentials:**
- Frigate — `/srv/frigate/config/config.yml` → `mqtt.user` / `mqtt.password`
- Session daemon — `/opt/neurosurveillance/config.yaml` → `mqtt.user` / `mqtt.password`
- `nvr-mqtt-slack.service` — `/etc/nvr-mqtt-slack.env` → `NVR_MQTT_PASSWORD` (subscribes to alert topics via `docker exec mosquitto mosquitto_sub`)

**Rotating the password:** generate new value, update both consumer configs + `passwd` file, restart Mosquitto + Frigate + daemon in dependency order (see [[emergency-runbook|emergency-runbook]] Symptom D for the restart order).

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

# Test Storage Monitor
curl http://127.0.0.1:8585/api/storage
```

---

**Last validated:** 2026-04-02
**System status:** Operational (Pi streaming + Frigate recording + MQTT + Session daemon + Storage monitoring + Netdata alerts + Uptime Kuma monitoring + Slack alerting)

## ✅ Animal room light cycle (recorded 2026-08-03)

- Lights ON time: `09:00 KST`
- Lights OFF time: `21:00 KST`
- Cycle: `12:12 LD`
- ZT0 (= lights on) corresponds to clock time: `09:00 KST`

Light phase = ZT0–ZT12 = 09:00–21:00. Dark phase = ZT12–ZT24 = 21:00–09:00.
A normal mouse sleeps most in the LIGHT phase.

Encoded in `02-procedures/eeg-data-analysis/pipeline/qc_thresholds.py`
(`LIGHTS_ON_HOUR`, `LIGHTS_OFF_HOUR`, `TZ_OFFSET_HOURS`) and stamped into every
pipeline output. Stage 3 reports sleep architecture split by light and dark phase.

> [!warning] Allego timestamps are UTC; the filename is not
> The `start_time` field in `*.xdat.json` is **UTC**. The `uidMMDD-HH-MM-SS`
> token in the filename is already **local (KST)**. Converting one and not the
> other puts a recording in the wrong day folder and shifts every ZT value by
> 9 hours. The pipeline uses the metadata UTC value and records which source it
> used as `start_source`.

Was blank from 2026-08-01 to 2026-08-03; analyses written in that window label
recordings by clock time only. See [[2026-08-01-channel-mapping-correction-first-sleep]].

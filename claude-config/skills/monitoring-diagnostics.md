---
name: monitoring-diagnostics
description: Query Netdata and Uptime Kuma to diagnose system issues on the NeuroSurveillance NVR and Pis
---

# Monitoring Diagnostics

You are on the NVR machine (`e10ubuntu`, `192.168.0.50`). Use these tools to diagnose system issues.

## Architecture

- **NVR** `192.168.0.50` — Netdata `:19999`, Uptime Kuma `:3001` (Docker)
- **Pi 1** `192.168.0.11` — Netdata `:19999`, go2rtc `:1984` (pi_cam_0, pi_cam_1)
- **Pi 2** `192.168.0.12` — Netdata `:19999`, go2rtc `:1984` (pi_cam_2, pi_cam_3)
- Slack webhook shared by both Netdata and Uptime Kuma

## Netdata API (localhost:19999)

### Quick reads

```bash
# Current CPU usage
curl -s "http://localhost:19999/api/v1/data?chart=system.cpu&points=1&after=-10&format=json" | python3 -c "
import json,sys; d=json.load(sys.stdin); row=d['data'][0]
total=sum(v for v in row[1:] if v); print(f'CPU: {total:.1f}%')
"

# Current temperature
curl -s "http://localhost:19999/api/v1/data?chart=sensors.temperature_coretemp-isa-0000_temp1_Package_id_0_input&points=1&after=-10&format=json" | python3 -c "
import json,sys; print(f'CPU: {json.load(sys.stdin)[\"data\"][0][1]:.1f} C')
"

# Available RAM
curl -s "http://localhost:19999/api/v1/data?chart=mem.available&points=1&after=-10&format=json" | python3 -c "
import json,sys; print(f'RAM avail: {json.load(sys.stdin)[\"data\"][0][1]:.0f} MiB')
"
```

### History queries

Use `after=-N` (seconds): `-3600` = 1h, `-21600` = 6h, `-86400` = 24h. Set `points` for resolution.

```bash
# Temperature history (6h, 1-min resolution)
curl -s "http://localhost:19999/api/v1/data?chart=sensors.temperature_coretemp-isa-0000_temp1_Package_id_0_input&after=-21600&points=360&format=json" | python3 -c "
import json,sys,datetime
for row in json.load(sys.stdin)['data']:
    v=row[1]; dt=datetime.datetime.fromtimestamp(row[0])
    if v and v>75: print(f'{dt}: {v:.1f} C <<<')
"
```

### Alarm status

```bash
# All alarms with status
curl -s "http://localhost:19999/api/v1/alarms?all" | python3 -c "
import json,sys,datetime
for name,a in sorted(json.load(sys.stdin).get('alarms',{}).items()):
    s=a.get('status','?'); v=a.get('value')
    dt=datetime.datetime.fromtimestamp(a.get('last_status_change',0))
    print(f'{s:8s} {name}  val={v}  changed={dt}')
"

# Only active (non-CLEAR) alarms
curl -s "http://localhost:19999/api/v1/alarms" | python3 -c "
import json,sys
alarms=json.load(sys.stdin).get('alarms',{})
if not alarms: print('No active alarms')
for name,a in alarms.items(): print(f'{a[\"status\"]:8s} {name}  val={a.get(\"value\")}')
"
```

### Remote machine (Pi)

Replace IP for Pi 1 (`192.168.0.11`) or Pi 2 (`192.168.0.12`):

```bash
curl -s "http://192.168.0.12:19999/api/v1/info" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Version: {d.get(\"version\")}  Alarms: {d.get(\"alarms\")}')
"
```

## Uptime Kuma (SQLite)

No unauthenticated REST API. Query the DB at `/opt/uptime-kuma/data/kuma.db`.

```bash
# All monitors — current status (1=UP, 0=DOWN)
docker exec uptime-kuma sqlite3 /app/data/kuma.db "
SELECT m.name, h.status, h.msg, h.time
FROM monitor m JOIN heartbeat h ON h.monitor_id=m.id
WHERE h.time=(SELECT MAX(h2.time) FROM heartbeat h2 WHERE h2.monitor_id=m.id)
ORDER BY m.id;
"

# Last failure per monitor
docker exec uptime-kuma sqlite3 /app/data/kuma.db "
SELECT m.name, h.time, h.msg FROM monitor m
JOIN heartbeat h ON h.monitor_id=m.id
WHERE h.status=0 AND h.time=(SELECT MAX(h2.time) FROM heartbeat h2 WHERE h2.monitor_id=m.id AND h2.status=0)
ORDER BY m.id;
"

# 24h uptime percentages
docker exec uptime-kuma sqlite3 /app/data/kuma.db "
SELECT m.name, ROUND(100.0*SUM(CASE WHEN h.status=1 THEN 1 ELSE 0 END)/COUNT(*),2) AS pct
FROM monitor m JOIN heartbeat h ON h.monitor_id=m.id
WHERE h.time>=datetime('now','-24 hours') GROUP BY m.id ORDER BY pct;
"
```

### Monitor IDs

| ID | Name | Type | Target |
|----|------|------|--------|
| 1 | Session Daemon | HTTP | `127.0.0.1:8585/api/health` |
| 2 | Frigate NVR | HTTP | `127.0.0.1:5000/api/stats` |
| 3 | Mosquitto MQTT | TCP | `127.0.0.1:1883` |
| 4 | go2rtc Pi 1 | HTTP | `192.168.0.11:1984/api/streams` |
| 5 | go2rtc Pi 2 | HTTP | `192.168.0.12:1984/api/streams` |
| 6 | Pi 1 Network | PING | `192.168.0.11` |
| 7 | Pi 2 Network | PING | `192.168.0.12` |

## NVR Alert Thresholds

| Alert | Warning | Critical |
|-------|---------|----------|
| `nvr_cpu_high` | >85% (stays >75%) | >95% (stays >85%) |
| `nvr_cpu_iowait` | >40% (stays >20%) | — |
| `nvr_ram_usage` | <10% avail (stays <15%) | <5% (stays <10%) |
| `nvr_swap_usage` | >50% (stays >40%) | — |
| `nvr_disk_space` | >90% (stays >80%) | >95% (stays >90%) |
| `nvr_disk_inodes` | >90% (stays >80%) | >98% (stays >90%) |
| `nvr_container_unhealthy` | unhealthy > 0 | — |
| `nvr_container_down` | exited > 0 | — |
| `nvr_cpu_temperature` | >85 C (stays >75 C) | >95 C (stays >85 C) |

## Key Services

| Service | Check | Restart |
|---------|-------|---------|
| Netdata | `systemctl status netdata` | `sudo systemctl restart netdata` |
| Frigate | `docker ps \| grep frigate` | `cd /opt/frigate && docker compose restart frigate` |
| Mosquitto | `docker ps \| grep mosquitto` | `cd /opt/frigate && docker compose restart mosquitto` |
| Uptime Kuma | `docker ps \| grep uptime-kuma` | `cd /opt/uptime-kuma && docker compose restart` |
| go2rtc (Pi) | `ssh skimlab@{IP} systemctl status go2rtc` | `ssh skimlab@{IP} sudo systemctl restart go2rtc` |
| Session Daemon | `curl -s http://127.0.0.1:8585/api/health` | `sudo systemctl restart neurosurveillance` |
| CPU Power Cap | `cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw` (expect 20000000) | `sudo systemctl restart cpu-power-cap` |

## Key config files

- Netdata config: `/etc/netdata/netdata.conf`
- NVR alerts: `/etc/netdata/health.d/nvr-alerts.conf`
- Slack notify: `/etc/netdata/health_alarm_notify.conf`
- Uptime Kuma compose: `/opt/uptime-kuma/docker-compose.yml`
- Frigate compose: `/opt/frigate/docker-compose.yml`
- RAPL cap service: `/etc/systemd/system/cpu-power-cap.service`

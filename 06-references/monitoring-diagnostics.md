---
tags: [reference, monitoring, netdata, uptime-kuma, diagnostics]
created: 2026-04-03
status: production
---

# Monitoring Diagnostics Reference

Quick-reference for querying the NeuroSurveillance monitoring stack. For setup procedures see [[02-procedures/installation/monitoring-setup|Monitoring Setup]]. For alert config details see [[01-infrastructure/netdata/nvr-alerts-config|NVR Alerts Config]].

---

## Architecture

| Machine | IP | Netdata | Monitors | Other |
|---------|------|---------|----------|-------|
| **NVR** (e10ubuntu) | `192.168.0.50` | `:19999` | CPU, RAM, disk, temp, Docker (frigate/mosquitto/uptime-kuma) | Uptime Kuma `:3001` |
| **Pi 1** | `192.168.0.11` | `:19999` | CPU, RAM, disk, go2rtc, pi_cam_0 + pi_cam_1 | — |
| **Pi 2** | `192.168.0.12` | `:19999` | CPU, RAM, disk, go2rtc, pi_cam_2 + pi_cam_3 | — |

- **Netdata**: v2.9.0 on all machines, custom `nvr_*` alerts on NVR only (227 defaults silenced)
- **Uptime Kuma**: v1.23.17 (Docker), 7 service monitors, SQLite DB
- **Alerting**: both systems share the same Slack webhook
- **NVR config**: `/etc/netdata/netdata.conf` (minimal — just `enabled alarms = nvr_*`)
- **NVR alerts**: `/etc/netdata/health.d/nvr-alerts.conf`
- **Uptime Kuma compose**: `/opt/uptime-kuma/docker-compose.yml`
- **Uptime Kuma data**: `/opt/uptime-kuma/data/kuma.db`

---

## Netdata API Commands

Base URL: `http://localhost:19999` (NVR), or substitute Pi IP for remote queries.

### Current system readings

```bash
# CPU, RAM, temperature — single snapshot
curl -s "http://localhost:19999/api/v1/data?chart=system.cpu&points=1&after=-10&format=json" | python3 -c "
import json,sys; d=json.load(sys.stdin); row=d['data'][0]
labels=d['labels'][1:]; vals=row[1:]
total=sum(v for v in vals if v)
print(f'CPU: {total:.1f}%')
for l,v in zip(labels,vals):
    if v and v > 1: print(f'  {l}: {v:.1f}%')
"

# Temperature (current)
curl -s "http://localhost:19999/api/v1/data?chart=sensors.temperature_coretemp-isa-0000_temp1_Package_id_0_input&points=1&after=-10&format=json" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'CPU Package: {d[\"data\"][0][1]:.1f} C')
"

# Available RAM
curl -s "http://localhost:19999/api/v1/data?chart=mem.available&points=1&after=-10&format=json" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Available RAM: {d[\"data\"][0][1]:.0f} MiB')
"

# Disk usage (all mount points)
curl -s "http://localhost:19999/api/v1/charts" | python3 -c "
import json,sys
charts=json.load(sys.stdin).get('charts',{})
for k in sorted(charts):
    if k.startswith('disk_space.'):
        print(k.replace('disk_space.',''))
"
```

### Historical data (last N hours)

```bash
# Temperature history — last 6 hours, 1-minute resolution
curl -s "http://localhost:19999/api/v1/data?chart=sensors.temperature_coretemp-isa-0000_temp1_Package_id_0_input&after=-21600&points=360&format=json" | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin)
for row in d['data']:
    dt=datetime.datetime.fromtimestamp(row[0])
    v=row[1]
    marker=' <<<' if v and v > 75 else ''
    print(f'{dt}: {v:.1f} C{marker}')
"

# CPU history — last 2 hours, 1-minute resolution
curl -s "http://localhost:19999/api/v1/data?chart=system.cpu&after=-7200&points=120&format=json" | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin)
for row in d['data']:
    total=sum(v for v in row[1:] if v)
    dt=datetime.datetime.fromtimestamp(row[0])
    marker=' <<<' if total > 60 else ''
    print(f'{dt}: {total:.1f}%{marker}')
"
```

> [!tip] Adjust time range
> `after=-N` is seconds. Common values: `-3600` (1h), `-21600` (6h), `-86400` (24h).
> For absolute ranges use Unix timestamps: `after=EPOCH&before=EPOCH`.

### Alarm status

```bash
# All alarms — current status
curl -s "http://localhost:19999/api/v1/alarms?all" | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin)
for name,a in sorted(d.get('alarms',{}).items()):
    status=a.get('status','?')
    val=a.get('value')
    lsc=a.get('last_status_change',0)
    dt=datetime.datetime.fromtimestamp(lsc) if lsc else '?'
    print(f'{status:8s} {name}  val={val}  changed={dt}')
"

# Only active (non-CLEAR) alarms
curl -s "http://localhost:19999/api/v1/alarms" | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin)
alarms=d.get('alarms',{})
if not alarms: print('No active alarms')
for name,a in alarms.items():
    print(f'{a[\"status\"]:8s} {name}  val={a.get(\"value\")}')
"

# Check a specific alarm by name
curl -s "http://localhost:19999/api/v1/alarms?all" | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin)
for name,a in d.get('alarms',{}).items():
    if 'nvr_cpu_temperature' in name:
        for k in ['status','value','last_status_change','last_updated']:
            v=a.get(k)
            if k.endswith('change') or k.endswith('updated'):
                v=datetime.datetime.fromtimestamp(v) if v else v
            print(f'  {k}: {v}')
"
```

### Query a remote machine (Pi)

```bash
# Pi 2 system info
curl -s "http://192.168.0.12:19999/api/v1/info" | python3 -c "
import json,sys; d=json.load(sys.stdin)
print(f'Hostname: {d.get(\"mirrored_hosts\",[\"\"])}')
print(f'Version: {d.get(\"version\")}')
print(f'Alarms: {d.get(\"alarms\")}')
"

# Pi 2 CPU temperature
curl -s "http://192.168.0.12:19999/api/v1/data?chart=sensors.temperature_thermal_thermal_zone0_thermal_zone0_input&points=1&after=-10&format=json" 2>/dev/null | python3 -c "
import json,sys; d=json.load(sys.stdin); print(f'Pi2 temp: {d[\"data\"][0][1]:.1f} C')
" 2>/dev/null || echo "Pi2 unreachable or chart name differs — check available charts first"
```

### List available charts on a machine

```bash
# Useful when you don't know the exact chart name
curl -s "http://localhost:19999/api/v1/charts" | python3 -c "
import json,sys
charts=json.load(sys.stdin).get('charts',{})
for k in sorted(charts):
    if any(term in k for term in ['temp','cpu','mem','disk','docker']):
        print(k)
"
```

---

## Uptime Kuma Commands

Database: `/opt/uptime-kuma/data/kuma.db` (SQLite3). Uptime Kuma has no unauthenticated REST API — query the DB directly.

```bash
# List all monitors with type and URL
sqlite3 /opt/uptime-kuma/data/kuma.db "SELECT id, name, type, url, interval FROM monitor WHERE active=1;"

# Current status of all monitors (1=UP, 0=DOWN, 2=PENDING, 3=MAINTENANCE)
sqlite3 /opt/uptime-kuma/data/kuma.db "
SELECT m.name, h.status, h.msg, h.time
FROM monitor m
JOIN heartbeat h ON h.monitor_id = m.id
WHERE h.time = (SELECT MAX(h2.time) FROM heartbeat h2 WHERE h2.monitor_id = m.id)
ORDER BY m.id;
"

# Recent heartbeats for a specific monitor (last 10)
sqlite3 /opt/uptime-kuma/data/kuma.db "
SELECT time, status, msg, ping
FROM heartbeat
WHERE monitor_id = (SELECT id FROM monitor WHERE name LIKE '%Frigate%')
ORDER BY time DESC LIMIT 10;
"

# Last failure per monitor
sqlite3 /opt/uptime-kuma/data/kuma.db "
SELECT m.name, h.time, h.msg
FROM monitor m
JOIN heartbeat h ON h.monitor_id = m.id
WHERE h.status = 0
AND h.time = (SELECT MAX(h2.time) FROM heartbeat h2 WHERE h2.monitor_id = m.id AND h2.status = 0)
ORDER BY m.id;
"

# Uptime percentage (last 24h)
sqlite3 /opt/uptime-kuma/data/kuma.db "
SELECT m.name,
  ROUND(100.0 * SUM(CASE WHEN h.status=1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS uptime_pct,
  COUNT(*) AS checks
FROM monitor m
JOIN heartbeat h ON h.monitor_id = m.id
WHERE h.time >= datetime('now', '-24 hours')
GROUP BY m.id
ORDER BY uptime_pct;
"
```

### Uptime Kuma monitors (current config)

| ID | Name | Type | Target | Interval |
|----|------|------|--------|----------|
| 1 | Session Daemon | HTTP | `http://127.0.0.1:8585/api/health` | 60s |
| 2 | Frigate NVR | HTTP | `http://127.0.0.1:5000/api/stats` | 60s |
| 3 | Mosquitto MQTT | TCP | `127.0.0.1:1883` | 60s |
| 4 | go2rtc Pi 1 | HTTP | `http://192.168.0.11:1984/api/streams` | 60s |
| 5 | go2rtc Pi 2 | HTTP | `http://192.168.0.12:1984/api/streams` | 60s |
| 6 | Pi 1 Network | PING | `192.168.0.11` | 30s |
| 7 | Pi 2 Network | PING | `192.168.0.12` | 30s |

---

## Diagnostic Scenarios

### Temperature alert

```bash
# 1. Current reading
sensors | grep "Package id"

# 2. History (last 6h) — look for spikes
curl -s "http://localhost:19999/api/v1/data?chart=sensors.temperature_coretemp-isa-0000_temp1_Package_id_0_input&after=-21600&points=360&format=json" | python3 -c "
import json,sys,datetime
for row in json.load(sys.stdin)['data']:
    v=row[1]; dt=datetime.datetime.fromtimestamp(row[0])
    if v and v>75: print(f'{dt}: {v:.1f} C <<<')
"

# 3. What's using CPU?
ps aux --sort=-%cpu | head -15

# 4. Check RAPL power cap (should be 20000000)
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
```

### Service down

```bash
# 1. Which service? Check Uptime Kuma
sqlite3 /opt/uptime-kuma/data/kuma.db "
SELECT m.name, h.status, h.msg, h.time FROM monitor m
JOIN heartbeat h ON h.monitor_id=m.id
WHERE h.time=(SELECT MAX(h2.time) FROM heartbeat h2 WHERE h2.monitor_id=m.id)
AND h.status != 1;
"

# 2. Docker containers
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 3. Container logs (last 50 lines)
docker logs frigate --tail 50 2>&1 | tail -30
docker logs mosquitto --tail 50 2>&1 | tail -30

# 4. Netdata container alerts
curl -s "http://localhost:19999/api/v1/alarms" | python3 -c "
import json,sys
for name,a in json.load(sys.stdin).get('alarms',{}).items():
    if 'container' in name: print(f'{a[\"status\"]} {name}')
"
```

### Disk space alert

```bash
# 1. Current usage
df -h / /media/frigate-recordings 2>/dev/null || df -h /

# 2. What's taking space
du -sh /opt/frigate/storage/recordings/ /opt/frigate/storage/clips/ 2>/dev/null
du -sh /media/frigate-recordings/* 2>/dev/null | sort -rh | head -10

# 3. Netdata disk history (last 24h)
curl -s "http://localhost:19999/api/v1/data?chart=disk_space./&after=-86400&points=96&format=json" | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin); labels=d['labels']
for row in d['data'][-5:]:
    dt=datetime.datetime.fromtimestamp(row[0])
    used=row[1] if len(row)>1 else 0
    avail=row[2] if len(row)>2 else 0
    pct=used*100/(used+avail) if (used+avail)>0 else 0
    print(f'{dt}: {pct:.1f}% used')
"
```

### Camera offline

```bash
# 1. Which camera? Check Uptime Kuma Pi monitors
sqlite3 /opt/uptime-kuma/data/kuma.db "
SELECT m.name, h.status, h.msg, h.time FROM monitor m
JOIN heartbeat h ON h.monitor_id=m.id
WHERE m.name LIKE '%Pi%'
AND h.time=(SELECT MAX(h2.time) FROM heartbeat h2 WHERE h2.monitor_id=m.id);
"

# 2. Ping the Pi
ping -c 3 192.168.0.11  # Pi 1
ping -c 3 192.168.0.12  # Pi 2

# 3. Check go2rtc streams (if Pi reachable)
curl -s http://192.168.0.12:1984/api/streams | python3 -m json.tool

# 4. Check Frigate camera status
curl -s http://localhost:5000/api/stats | python3 -c "
import json,sys
stats=json.load(sys.stdin)
for cam,data in stats.items():
    if cam not in ['detectors','service']:
        fps=data.get('camera_fps',0)
        print(f'{cam}: {fps} fps {\"OK\" if fps>0 else \"<<< NO FRAMES\"} ')
"
```

### High CPU

```bash
# 1. Top processes
ps aux --sort=-%cpu | head -15

# 2. CPU breakdown from Netdata (last 10 min)
curl -s "http://localhost:19999/api/v1/data?chart=system.cpu&after=-600&points=10&format=json" | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin); labels=d['labels'][1:]
for row in d['data']:
    dt=datetime.datetime.fromtimestamp(row[0])
    total=sum(v for v in row[1:] if v)
    top=max(zip(labels,row[1:]), key=lambda x: x[1] if x[1] else 0)
    print(f'{dt}: {total:.1f}% (top: {top[0]} {top[1]:.1f}%)')
"

# 3. Check RAPL cap
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
```

### Container unhealthy

```bash
# 1. Docker health details
docker inspect --format='{{.Name}} {{.State.Health.Status}} {{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{end}}' frigate mosquitto uptime-kuma 2>/dev/null

# 2. Recent container logs
docker logs frigate --since 10m 2>&1 | grep -iE "error|warn|fatal|crash" | tail -20

# 3. Container resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

---

## Alert Thresholds

| Alert | Metric | Warning | Critical | Eval | Delay Down |
|-------|--------|---------|----------|------|-----------|
| `nvr_cpu_high` | 10m avg CPU % | >85% (hysteresis 75%) | >95% (hysteresis 85%) | 1m | 15m |
| `nvr_cpu_iowait` | 10m avg iowait % | >40% (hysteresis 20%) | — | 1m | 15m |
| `nvr_ram_usage` | 5m avg available % | <10% (hysteresis 15%) | <5% (hysteresis 10%) | 1m | 15m |
| `nvr_swap_usage` | swap used % | >50% (hysteresis 40%) | — | 1m | 15m |
| `nvr_disk_space` | used % per mount | >90% (hysteresis 80%) | >95% (hysteresis 90%) | 1m | 15m |
| `nvr_disk_inodes` | used % per mount | >90% (hysteresis 80%) | >98% (hysteresis 90%) | 1m | 15m |
| `nvr_container_unhealthy` | health status | unhealthy > 0 | — | 10s | 1m |
| `nvr_container_down` | container state | exited > 0 | — | 10s | 1m |
| `nvr_cpu_temperature` | CPU package C | >85 C (hysteresis 75 C) | >95 C (hysteresis 85 C) | 30s | 5m |

> [!warning] Hysteresis
> "Warning >85 (hysteresis 75)" means: fires at 85, but once in WARNING, stays warned until it drops below 75. This prevents rapid flapping.

---

## Service Management

| Service | Check | Restart |
|---------|-------|---------|
| **Netdata** (NVR) | `systemctl status netdata` | `sudo systemctl restart netdata` |
| **Netdata** (Pi) | `ssh skimlab@{PI_IP} systemctl status netdata` | `ssh skimlab@{PI_IP} sudo systemctl restart netdata` |
| **Frigate** | `docker ps \| grep frigate` | `cd /opt/frigate && docker compose restart frigate` |
| **Mosquitto** | `docker ps \| grep mosquitto` | `cd /opt/frigate && docker compose restart mosquitto` |
| **Uptime Kuma** | `docker ps \| grep uptime-kuma` | `cd /opt/uptime-kuma && docker compose restart` |
| **go2rtc** (Pi) | `ssh skimlab@{PI_IP} systemctl status go2rtc` | `ssh skimlab@{PI_IP} sudo systemctl restart go2rtc` |
| **Session Daemon** | `curl -s http://127.0.0.1:8585/api/health` | `sudo systemctl restart neurosurveillance` |
| **CPU Power Cap** | `cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw` | `sudo systemctl restart cpu-power-cap` |

---

## Related

- [[02-procedures/installation/monitoring-setup|Monitoring Setup Procedure]]
- [[01-infrastructure/netdata/nvr-alerts-config|NVR Alerts Golden Config]]
- [[00-config/production-values|Production Values]]
- [[01-infrastructure/raspberry-pi/watchdog-monitoring|Pi Watchdog & Monitoring]]
- [[03-troubleshooting/incidents/2026-04-02-allegoserver-thermal-spikes|Thermal Incident 2026-04-02]]

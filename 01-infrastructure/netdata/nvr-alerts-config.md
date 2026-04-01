---
tags: [infrastructure, netdata, golden-config, monitoring, alerting]
created: 2026-04-01
status: production
version: "1.0"
---

# NVR Netdata Alert Configuration

> [!tip] Golden Configuration
> This is the production-stable Netdata alert configuration for the NVR server.
> **DO NOT MODIFY** without testing. Changes require `sudo systemctl restart netdata`.

## Overview

Netdata ships with **227 default alerts** covering every possible system metric. For our NVR use case, most are irrelevant noise. This configuration:

1. **Silences all 227 defaults** via `netdata.conf` → `enabled alarms = nvr_*`
2. **Defines 16 NVR-specific alerts** in `nvr-alerts.conf`
3. **Routes all alerts to Slack** via `health_alarm_notify.conf`

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Main config | `/etc/netdata/netdata.conf` | Filters alerts to `nvr_*` prefix only |
| Alert definitions | `/etc/netdata/health.d/nvr-alerts.conf` | 9 alert templates = 16 active alerts |
| Notification config | `/etc/netdata/health_alarm_notify.conf` | Slack webhook, disables all other channels |

---

## Active Alerts (16 total)

### System Resources

| Alert | Chart | Condition | Severity |
|-------|-------|-----------|----------|
| `nvr_cpu_high` | `system.cpu` | 10min avg >85% (warn), >95% (crit) | Warning/Critical |
| `nvr_cpu_iowait` | `system.cpu` | 10min avg iowait >40% | Warning |
| `nvr_ram_usage` | `mem.available` | Available RAM <10% (warn), <5% (crit) | Warning/Critical |
| `nvr_swap_usage` | `mem.swap` | Swap usage >50% | Warning |

### Disk (per mount point — generates multiple instances)

| Alert | Chart | Condition | Severity |
|-------|-------|-----------|----------|
| `nvr_disk_space` | `disk.space` | Usage >90% (warn), >95% (crit) | Warning/Critical |
| `nvr_disk_inodes` | `disk.inodes` | Usage >90% (warn), >98% (crit) | Warning/Critical |

Currently monitors 3 mounts: `/`, `/boot/efi`, `/run`

### Docker Containers

| Alert | Chart | Condition | Severity |
|-------|-------|-----------|----------|
| `nvr_container_unhealthy` | `docker.container_health_status` | Any container unhealthy | Warning |
| `nvr_container_down` | `docker.container_state` | Frigate/Mosquitto/Uptime Kuma exited | Warning |

Monitors: `frigate`, `mosquitto`, `uptime-kuma`

### Temperature

| Alert | Chart | Condition | Severity |
|-------|-------|-----------|----------|
| `nvr_cpu_temperature` | `sensors.temperature_coretemp-isa-0000_temp1_Package_id_0_input` | >85°C (warn), >95°C (crit) | Warning/Critical |

> [!info] Why Package Temperature Only?
> The NUC has 14+ core temperature sensors. We monitor only the **Package ID 0** sensor (overall CPU package temperature) because it's the thermal throttling trigger. Individual core temps fluctuate but package temp determines actual throttling behavior.

---

## Configuration Files

### `/etc/netdata/netdata.conf`

```ini
[health]
    enabled alarms = nvr_*
```

> [!warning] Critical Setting
> This single line is what silences all 227 default alerts. Only alerts whose name starts with `nvr_` are loaded. If this line is removed or changed, you will be flooded with irrelevant Slack notifications.

### `/etc/netdata/health.d/nvr-alerts.conf`

Full production config (9 alert definitions → 16 instances):

```conf
# =============================================================================
# NVR Server Alerts - Frigate NVR on ASUS NUC
# Only alerts relevant to video surveillance operations
# =============================================================================

# --- CPU (10min average) ---
   template: nvr_cpu_high
         on: system.cpu
      class: Utilization
       type: System
  component: CPU
host labels: _os=linux
     lookup: average -10m unaligned of user,system,softirq,irq,guest
      units: %
      every: 1m
       warn: $this > (($status >= $WARNING)  ? (75) : (85))
       crit: $this > (($status == $CRITICAL) ? (85) : (95))
      delay: down 15m multiplier 1.5 max 1h
    summary: NVR CPU utilization high
       info: Average CPU utilization over the last 10 minutes is ${this}%
         to: sysadmin

# --- CPU IO Wait (disk bottleneck indicator) ---
   template: nvr_cpu_iowait
         on: system.cpu
      class: Utilization
       type: System
  component: CPU
host labels: _os=linux
     lookup: average -10m unaligned of iowait
      units: %
      every: 1m
       warn: $this > (($status >= $WARNING)  ? (20) : (40))
      delay: up 5m down 15m multiplier 1.5 max 1h
    summary: NVR high IO wait
       info: Average CPU IO wait over the last 10 minutes is ${this}% - possible disk bottleneck
         to: sysadmin

# --- RAM ---
   template: nvr_ram_usage
         on: mem.available
      class: Utilization
       type: System
  component: Memory
     lookup: average -5m unaligned of avail
       calc: ($this) * 100 / ($system_ram_total)
      units: %
      every: 1m
       warn: $this < (($status >= $WARNING)  ? (15) : (10))
       crit: $this < (($status == $CRITICAL) ? (10) : (5))
      delay: down 15m multiplier 1.5 max 1h
    summary: NVR available RAM low
       info: Available RAM is ${this}%
         to: sysadmin

# --- Swap ---
   template: nvr_swap_usage
         on: mem.swap
      class: Utilization
       type: System
  component: Memory
        calc: ($used) * 100 / ($used + $free)
       units: %
       every: 1m
        warn: $this > (($status >= $WARNING)  ? (40) : (50))
       delay: up 5m down 15m multiplier 1.5 max 1h
     summary: NVR swap usage high
        info: Swap usage is ${this}% - system may be under memory pressure
          to: sysadmin

# --- Disk Space ---
    template: nvr_disk_space
          on: disk.space
       class: Utilization
        type: System
   component: Disk
        calc: $used * 100 / ($avail + $used)
       units: %
       every: 1m
        warn: $this > (($status >= $WARNING ) ? (80) : (90))
        crit: $this > (($status == $CRITICAL) ? (90) : (95))
       delay: up 1m down 15m multiplier 1.5 max 1h
     summary: Disk ${label:mount_point} space at ${this}%
        info: Disk ${label:mount_point} usage is ${this}%
          to: sysadmin

# --- Disk Inodes ---
    template: nvr_disk_inodes
          on: disk.inodes
       class: Utilization
        type: System
   component: Disk
        calc: $used * 100 / ($avail + $used)
       units: %
       every: 1m
        warn: $this > (($status >= $WARNING)  ? (80) : (90))
        crit: $this > (($status == $CRITICAL) ? (90) : (98))
       delay: up 1m down 15m multiplier 1.5 max 1h
     summary: Disk ${label:mount_point} inodes at ${this}%
        info: Disk ${label:mount_point} inode usage is ${this}%
          to: sysadmin

# --- Docker container health ---
    template: nvr_container_unhealthy
          on: docker.container_health_status
       class: Errors
        type: Containers
   component: Docker
       units: status
       every: 10s
      lookup: average -10s of unhealthy
        warn: $this > 0
       delay: down 1m multiplier 1.5 max 5m
     summary: Docker ${label:container_name} unhealthy
        info: Docker container ${label:container_name} is unhealthy
          to: sysadmin

# --- Docker container exited ---
    template: nvr_container_down
          on: docker.container_state
       class: Errors
        type: Containers
   component: Docker
 chart labels: container_name=frigate mosquitto uptime-kuma
       units: status
       every: 10s
      lookup: average -10s of exited
        warn: $this > 0
       delay: down 1m multiplier 1.5 max 5m
     summary: Docker ${label:container_name} is down
        info: Docker container ${label:container_name} has exited
          to: sysadmin

# --- CPU Package Temperature ---
      alarm: nvr_cpu_temperature
         on: sensors.temperature_coretemp-isa-0000_temp1_Package_id_0_input
      class: System
       type: System
  component: Temperature
       calc: $input
      units: Celsius
      every: 30s
       warn: $this > (($status >= $WARNING)  ? (75) : (85))
       crit: $this > (($status == $CRITICAL) ? (85) : (95))
      delay: down 5m multiplier 1 max 10m
    summary: NVR CPU temperature ${this}°C
       info: CPU package temperature is ${this}°C
         to: sysadmin
```

### `/etc/netdata/health_alarm_notify.conf`

```bash
# Disable all notification methods except Slack
SEND_EMAIL="NO"
SEND_PUSHOVER="NO"
SEND_TELEGRAM="NO"
SEND_DISCORD="NO"
SEND_TWILIO="NO"
SEND_MESSAGEBIRD="NO"
SEND_KAVENEGAR="NO"
SEND_PUSHBULLET="NO"
SEND_FLOCK="NO"
SEND_ALERTA="NO"
SEND_MSTEAMS="NO"
SEND_OPSGENIE="NO"
SEND_GOTIFY="NO"
SEND_NTFY="NO"

# Slack configuration
SEND_SLACK="YES"
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/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"
DEFAULT_RECIPIENT_SLACK="#"

# Route all roles to Slack
role_recipients_slack[sysadmin]="#"
role_recipients_slack[nvr]="#"
```

> [!warning] Slack Webhook
> The `DEFAULT_RECIPIENT_SLACK="#"` sends to the default channel configured in the Slack webhook. This is the same webhook used by Uptime Kuma.

---

## How Alerting Works

### Alert Lifecycle

```
CLEAR → WARNING → CRITICAL → WARNING → CLEAR
  ↑         ↑          ↑          ↑         ↑
  │    Slack msg   Slack msg  Slack msg  Slack msg
  │   (warning)   (critical) (warning)  (recovery)
  │
  └── Normal state, no notifications
```

### Hysteresis (Prevents Flapping)

Alerts use different thresholds for triggering vs. clearing to avoid rapid on/off cycling:

| Alert | Triggers at | Clears at |
|-------|-------------|-----------|
| `nvr_cpu_high` (warn) | >85% | <75% |
| `nvr_cpu_high` (crit) | >95% | <85% |
| `nvr_disk_space` (warn) | >90% | <80% |

This means if CPU hits 86% → WARNING fires. It stays WARNING until CPU drops below 75% (not 85%).

### Delay System

The `delay` directive prevents premature alerts and excessive recovery notifications:

- `down 15m` — after condition clears, wait 15 minutes before sending recovery (prevents flapping)
- `up 5m` — after condition triggers, wait 5 minutes before alerting (prevents transient spikes)
- `multiplier 1.5 max 1h` — if alert keeps cycling, increase delay up to 1 hour

---

## How to Manage

### Check Current Alert Status

```bash
# Quick summary
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

### Check Active (Non-CLEAR) Alerts Only

```bash
curl -s http://localhost:19999/api/v1/alarms?active | python3 -c "
import sys,json
d=json.load(sys.stdin)
alarms=d.get('alarms',{})
if not alarms:
    print('All clear - no active alerts')
else:
    for k,v in alarms.items():
        print(f'[{v[\"status\"]}] {k}: {v[\"info\"]}')
"
```

### View Alert History (Web UI)

Open `http://192.168.0.50:19999` → click **Alerts** in the left sidebar → **Alert Transitions** tab shows recent state changes.

### Test Slack Notifications

```bash
sudo /usr/libexec/netdata/plugins.d/alarm-notify.sh test
```

Sends test WARNING and CRITICAL messages to Slack. You should receive 2 messages.

### Add a New Alert

1. Edit `/etc/netdata/health.d/nvr-alerts.conf`
2. Add a new `template:` or `alarm:` block (must start with `nvr_` prefix)
3. Restart: `sudo systemctl restart netdata`
4. Verify: check the API for the new alert name

> [!info] Template vs Alarm
> - **`template`** — matches all charts with the same context (e.g., `disk.space` matches every mount point)
> - **`alarm`** — matches one specific chart by ID (e.g., the CPU package temperature sensor)
> Use `template` when you want per-instance alerts (per disk, per container). Use `alarm` for unique resources.

### Modify Alert Thresholds

Edit `/etc/netdata/health.d/nvr-alerts.conf`, change the `warn:` or `crit:` values, then restart Netdata.

Example — change CPU warning from 85% to 80%:
```
warn: $this > (($status >= $WARNING)  ? (70) : (80))
```

### Temporarily Silence Alerts

To silence alerts without removing them (e.g., during maintenance):

```bash
# Silence all alerts for 1 hour
curl -X POST "http://localhost:19999/api/v1/manage/health?cmd=SILENCE&duration=3600"

# Re-enable
curl -X POST "http://localhost:19999/api/v1/manage/health?cmd=RESET"
```

### Discover Available Charts

To find chart names for new alerts:

```bash
# List all charts
curl -s http://localhost:19999/api/v1/charts | python3 -c "
import sys,json
d=json.load(sys.stdin)
for k in sorted(d.get('charts',{}).keys()):
    print(k)
" | grep -i "keyword"

# Get details for a specific chart
curl -s "http://localhost:19999/api/v1/chart?chart=CHART_NAME" | python3 -m json.tool
```

---

## Relationship to Uptime Kuma

| Concern | Netdata | Uptime Kuma |
|---------|---------|-------------|
| **What** | System metrics (CPU, RAM, disk, temp) | Service reachability (up/down) |
| **How** | Threshold-based alerts on metrics | HTTP/TCP/Ping health checks |
| **Where** | Runs on NVR locally | Runs on NVR, checks all machines |
| **Alerts** | Slack (via `alarm-notify.sh`) | Slack (via webhook) |
| **Use case** | "Disk is 92% full", "CPU at 96%" | "Frigate is down", "Pi 1 unreachable" |

Both tools send to the **same Slack channel** using the same webhook URL. They are complementary:
- Uptime Kuma tells you **something is down**
- Netdata tells you **why it might go down** (or why it went down)

---

## Troubleshooting

### No Slack notifications received

1. Test the notification script:
   ```bash
   sudo /usr/libexec/netdata/plugins.d/alarm-notify.sh test
   ```
2. Check the webhook URL is correct in `/etc/netdata/health_alarm_notify.conf`
3. Check Netdata logs:
   ```bash
   journalctl -u netdata --since "10 minutes ago" | grep -i "alarm\|notify\|slack"
   ```

### Alert not appearing

1. Verify the alert name starts with `nvr_` (required by `enabled alarms = nvr_*`)
2. Check chart name exists:
   ```bash
   curl -s "http://localhost:19999/api/v1/chart?chart=CHART_NAME"
   ```
3. Check for config syntax errors in Netdata logs after restart

### Too many alerts from a specific check

Add `delay: up 10m` to the alert definition to require the condition to persist for 10 minutes before firing.

---

## Version History

| Date | Change | Notes |
|------|--------|-------|
| 2026-04-01 | Initial configuration | 227 defaults silenced, 16 NVR alerts, Slack notifications |

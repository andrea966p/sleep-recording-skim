---
tags: [troubleshooting, incident, nvr, thermal, cpu, allegoserver]
date: 2026-04-02
severity: high
status: identified - fix pending
affected: [e10ubuntu, nvr-server]
---

## Summary
- **Date/Time:** 2026-04-02 ~16:52–18:00 GMT
- **Duration:** Recurring — spikes every ~35–40 minutes, each lasting ~2.5 minutes
- **Severity:** High — CPU package reaching 87–92°C
- **Status:** Root cause identified, fix pending application

## Symptoms

Netdata/Uptime Kuma alerts on `sensors.temperature_coretemp-isa-0000_temp1_Package_id_0_input`:
- 16:54 — 92°C → recovered after 2m30s
- 17:34 — 87°C → recovered after 2m30s
- 17:47 — 90°C → (ongoing)

Pattern: spike → recovery → spike (not a steady thermal climb → not a cooling failure).

## Investigation

### Diagnostic Commands

```bash
top -bn1 | head -30
sudo intel_gpu_top -s 1 -o - | head -20
vainfo 2>&1 | grep -E "vainfo|error|VA-API"
docker logs frigate --since 2h 2>&1 | grep -E "error|warn|cpu|ffmpeg|detect" | tail -50
ps aux --sort=-%cpu | head -20
sensors
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
cat /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_max_power_uw
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort -u
```

### Key Findings

**`allegoserver` at 109% CPU with nothing connected and no recording active:**
```
3327251 skimlab  109%  /opt/allego/resources/radix/allegoserver/allegoserver hardware
```
- Started at 16:52 (matches first alert at 16:54)
- Actively scanning `/sys/bus/usb/devices` in a tight polling loop
- 77+ minutes of CPU time accumulated
- No EEG/EMG devices plugged in, no recording in progress

**Frigate/FFmpeg are NOT the cause:**
- All 4 camera streams using QSV hardware acceleration correctly
- VA-API 1.20 / Intel iHD driver working
- Each FFmpeg process: ~2% CPU

**System thermal state:**
- CPU package: 76°C at baseline (already elevated)
- Core 8: 88°C
- Fan: 2500 RPM, BIOS-controlled (no software override)
- Governor: `powersave` ✓
- CPU power limit: **200W** (effectively uncapped — should be 20W)
- CPU TDP spec: 28W

**Combined load causing thermal pressure:**
- `allegoserver` busy-polling (109%)
- 4× FFmpeg QSV streams
- GNOME desktop + RustDesk + Claude sessions
- containerd + dockerd

## Root Cause

**`allegoserver` (Allego EEG/EMG software) performs a busy-wait USB polling loop** (`/sys/bus/usb/devices`) even when idle with no devices connected. This is a software design issue in Allego — it should use udev events instead of tight-loop polling.

Combined with the NUC Pro 15's single small fan and the baseline load from Frigate + desktop environment, the CPU package hits 87–92°C during the polling bursts.

**Secondary factor:** The CPU RAPL power limit is set to 200W (uncapped), allowing unconstrained boost. Capping it to 20W would keep temperatures under 80°C.

## Resolution (Pending)

**1. Cap CPU power via Intel RAPL (most effective):**
```bash
echo 20000000 | sudo tee /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw
```

Make persistent at boot:
```bash
sudo tee /etc/systemd/system/cpu-power-cap.service << 'EOF'
[Unit]
Description=Intel RAPL CPU power cap
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo 20000000 > /sys/class/powercap/intel-rapl/intel-rapl:0/constraint_0_power_limit_uw'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable --now cpu-power-cap.service
```

**2. Throttle allegoserver when idle:**
```bash
sudo apt-get install -y cpulimit
cpulimit -p <PID> -l 20 &   # Limit to 20% CPU when not recording
```

**3. Long-term:** Report busy-poll issue to Allego — idle hardware detection should use udev events, not a tight scanning loop.

## Notes
- ASUS NUC Pro 15 fan is fully BIOS-controlled — no `/sys/class/hwmon/hwmon*/fan*_max` available
- `pwmconfig` returns nothing — no fan control via software
- Hardware acceleration for video is confirmed working; thermal issue is unrelated to Frigate

## Related
- [[01-infrastructure/nvr/frigate|Frigate NVR Setup]]
- [[01-infrastructure/netdata|Netdata Monitoring]]

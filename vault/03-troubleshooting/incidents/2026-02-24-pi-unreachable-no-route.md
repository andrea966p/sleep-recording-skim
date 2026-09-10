---
tags: [troubleshooting, incident, raspberry-pi, network, poe, pmic]
date: 2026-02-24
severity: high
status: resolved
affected: [raspberry-pi, frigate, network]
---

# Raspberry Pi Sudden Death + Failed Auto-Reboot — 2026-02-24

## Summary

- **Date/Time:** 2026-02-24 ~22:45 KST (13:45 GMT)
- **Severity:** High (camera ingest loss, ~12 hours unrecoverable)
- **Status:** Resolved (manual power cycle); root cause confirmed as PoE power transient
- **Impact:** Frigate lost both camera streams for ~12 hours overnight
- **Recovery:** Manual on-site power cycle at ~10:50 KST Feb 25

## Timeline (all times KST = GMT+9)

| Time | Event |
|------|-------|
| ~14:00 Feb 24 | User shuts down Pi (`sudo shutdown now`) to physically relocate it |
| ~14:54 Feb 24 | Second clean shutdown after relocation adjustments |
| 14:54 Feb 24 | Boot -1 starts — Pi running stable |
| 22:45 Feb 24 | **Sudden death.** Journal stops mid-cron, no panic/OOM/shutdown logged |
| 22:44:56 Feb 24 | `POWER_OFF_ON_HALT=1` triggers auto-reboot (boot 0 begins) |
| 22:45:04 Feb 24 | Auto-reboot reaches go2rtc service start... then **dies again** |
| 22:45 Feb 24 → 10:50 Feb 25 | **Pi stuck dead for ~12 hours** (PMIC latch-up on second crash) |
| ~10:50 Feb 25 | User manual power cycle on-site |
| 10:51 Feb 25 | Pi boots, go2rtc active, both cameras streaming within 90 seconds |

## Root Cause Analysis

### Evidence from crash canary (last healthy entry at 13:44:32 GMT / 22:44 KST)

```
temp=49.4°C  throttle=0x0  load=0.17  mem_free=7364M
go2rtc=active  rpicam=2  rpicam_cpu=16.4% 16.8%
go2rtc_mem=25472kB  oom_kills=0
```

**Every metric was perfectly healthy at time of death.** No thermal, memory, CPU, or software issue.

### Evidence from persistent journal

- `journalctl --list-boots` recorded 7 boots (journal is persistent and working)
- Boot -1 (the stable 8-hour boot): journal ends abruptly at 13:45:01 GMT with cron entries — **no panic, no OOM, no shutdown sequence logged**
- Boot 0 (auto-reboot): kernel boots at 13:44:56 GMT, starts go2rtc at 13:45:04 GMT, then **12-hour gap** until user's power cycle at 01:50:45 GMT Feb 25
- `grep -i "panic|oops|oom|undervolt|pmic"` on boot -1: **zero matches**

### Evidence from current boot

- `vcgencmd get_throttled` = `0x0` (clean — no undervoltage history in current boot)
- `PSU_MAX_CURRENT=5000` and `POWER_OFF_ON_HALT=1` intact in eeprom
- Hardware watchdog active (1 min timeout)
- `dmesg` clean — no PMIC/PSU/undervolt messages

### Conclusion

**Same failure class as Feb 13 and Feb 19: PoE power transient.** The crash happens too fast for the kernel to log anything — consistent with a sudden power loss, not a software bug.

**What's new this time:** The eeprom fix (`POWER_OFF_ON_HALT=1`) worked — the Pi did auto-reboot within seconds. But it crashed again immediately during boot (got only as far as starting go2rtc) and then got stuck in PMIC latch-up for 12 hours. This suggests:

1. The initial PoE transient caused the first crash
2. The auto-reboot happened, but PoE power was still unstable
3. The Pi crashed again during boot under the same unstable power
4. The second crash stuck the PMIC despite the eeprom fix (the fix helps with single-event recovery, not repeated rapid crashes)

## Symptoms Observed

- From ASUS NVR (`192.168.0.50`):
  - `ping 192.168.0.11` → `Destination Host Unreachable`
  - `curl http://192.168.0.11:1984/api/streams` → connection failed
  - ARP neighbor state → `INCOMPLETE` (L2 unreachable — not a software issue)
- Frigate logs: `Error opening input file`, `No route to host`

## Context

Earlier that afternoon, the Pi was physically moved (two intentional shutdowns at ~14:00 and ~14:54 KST). It ran stable for 8 hours after relocation before crashing. The physical move may have created a marginal cable connection that later failed.

## What Worked

- **Persistent journal** — captured full boot history across all reboots
- **Crash canary** — pinpointed exact time of death and confirmed software was healthy
- **`POWER_OFF_ON_HALT=1`** — Pi did auto-reboot (unlike Feb 19 where it was stuck for 6 days)
- **Hardware watchdog** — active and running (but powerless against sudden power loss)

## What Didn't Work

- **Auto-reboot recovery** — the Pi rebooted but crashed again immediately, entering PMIC latch-up. A single `POWER_OFF_ON_HALT=1` cycle is not enough when the power source itself is unstable.

## Prevention: Actionable Options

### 1. Check the physical setup after relocation (immediate)

The Pi was moved yesterday. Verify:
- Ethernet cable firmly seated at both ends (Pi and switch)
- PoE HAT seated properly on GPIO pins (may have loosened during move)
- No strain on cable

### 2. Add a PoE power buffer (recommended)

A small UPS HAT or supercapacitor module between the PoE HAT and the Pi would buffer brief power transients, preventing the PMIC from seeing the voltage drop. Options:
- PiJuice HAT (battery-backed UPS for Pi)
- Supercapacitor-based UPS module (handles brief <5s outages)

### 3. Replace the Waveshare PoE HAT (consider)

The Waveshare PoE HAT has known PMIC compatibility issues with Pi 5. The official **Raspberry Pi PoE+ HAT** may have better voltage regulation and PMIC handling since it's designed by the same team.

### 4. External Pi monitoring from ASUS NVR (implement)

A simple cron on the ASUS NVR that pings the Pi and alerts (email/file/log) if it's unreachable. This wouldn't prevent crashes but would catch them immediately instead of discovering hours later.

```bash
# Example: /opt/neurosurveillance/pi-monitor.sh (on ASUS NVR)
# Run every 2 minutes via cron
if ! ping -c 2 -W 3 192.168.0.11 > /dev/null 2>&1; then
    echo "[$(date)] Pi UNREACHABLE" >> /opt/neurosurveillance/logs/pi-monitor.log
    # Future: send notification
fi
```

### 5. Bootloader retry delay (consider)

Configure the Pi 5 bootloader to wait before retrying after a failed boot. This would let PoE power stabilize before the second boot attempt, possibly avoiding the double-crash → PMIC latch-up pattern.

## Related

- [[2026-02-19-pmic-fault-poe-death|PMIC Fault PoE Death (Feb 19)]] — same failure class, but no auto-reboot (pre-eeprom fix)
- [[../../01-infrastructure/raspberry-pi/golden-boot-config|Boot Config]] — eeprom settings
- [[../../01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog Monitoring]] — monitoring stack
- [[../../04-journal/2026-02/2026-02-24|Journal: 2026-02-24]]

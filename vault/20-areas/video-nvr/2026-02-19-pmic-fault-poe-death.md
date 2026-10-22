---
type: incident
area: video-nvr
status: done
status-note: "resolved"
tags: [troubleshooting, incident, raspberry-pi, poe, power, pmic]
created: 2026-02-19
severity: high
affected: [raspberry-pi]
---

## Summary
- **Date/Time:** 2026-02-13 10:40 GMT (discovered 2026-02-19)
- **Duration:** ~6 days (Pi dead from Feb 13 10:40 until manual power cycle Feb 19 04:03)
- **Severity:** High — complete system death, no automatic recovery
- **Status:** Resolved (eeprom fixes applied)

## Symptoms

- Pi completely unresponsive — no ping, no SSH
- Found with **red LED on, green/yellow LED off** — power present but kernel not running
- Hardware watchdog (1-min timeout) did not recover the system
- Pi required manual power cycle to come back

## Investigation

### Timeline

| Time | Event |
|------|-------|
| Feb 13 10:40:01 | **Last crash canary entry** — all metrics normal |
| Feb 13 10:40:31 | Next canary never ran — Pi dead |
| Feb 19 04:03 | Manual power cycle, Pi boots successfully |

### Last Known State (crash-canary.log)

```
[2026-02-13 10:40:01] temp=50.5°C throttle=0x0 load=0.21
mem_free=7378M mem_avail=7620M go2rtc=active rpicam=2
rpicam_cpu=17.0% 17.0% go2rtc_mem=25920kB oom_kills=0
```

All metrics perfectly healthy at the moment of death.

### Key Finding: Missing Eeprom Configuration

The Pi 5 eeprom had **no `PSU_MAX_CURRENT` setting**. Without this, the PMIC doesn't know the PoE HAT can deliver adequate current. Known issue with Waveshare PoE HATs on Pi 5 — see [geerlingguy/raspberry-pi-pcie-devices#597](https://github.com/geerlingguy/raspberry-pi-pcie-devices/issues/597).

Users report: Pi gets stuck on reboot with "insufficient PSU" notice, PMIC refuses to boot.

## Root Cause

**PMIC fault/latch-up, compounded by missing eeprom power configuration.**

1. PoE HAT delivered a brief voltage fluctuation
2. PMIC entered fault/shutdown state (red LED on, green LED off)
3. Without `PSU_MAX_CURRENT`, PMIC blocked reboot ("insufficient PSU")
4. `POWER_OFF_ON_HALT=0` (default) prevented PoE auto-recovery
5. Pi sat dead for 6 days

## Resolution

Eeprom updated:

| Setting | Before | After | Purpose |
|---------|--------|-------|---------|
| `PSU_MAX_CURRENT` | *(unset)* | `5000` | Tells PMIC the PoE HAT can deliver 5A |
| `POWER_OFF_ON_HALT` | `0` | `1` | On halt, cuts PMIC power — PoE auto-reboots |
| Firmware | May 2025 | Dec 2025 | Includes PMIC fixes |

Verified: no PSU warnings, no orphan cleanup, clean boot.

## Prevention

- `PSU_MAX_CURRENT=5000` — critical for any PoE-powered Pi 5
- `POWER_OFF_ON_HALT=1` — enables auto-recovery via PoE
- Consider managed PoE switch for remote port cycling (current: unmanaged NEXT-POE3008GF)
- Consider external ping monitoring from NVR (`192.168.0.50`)

## Related
- [[2026-02-13|Journal: Feb 13]] — ethernet cable incident that preceded the crash
- [[2026-02-11-vscode-remote-cpu-exhaustion|VSCode Remote CPU Exhaustion]] — previous Pi crash incident
- [Waveshare PoE HAT Pi 5 issue](https://github.com/geerlingguy/raspberry-pi-pcie-devices/issues/597)

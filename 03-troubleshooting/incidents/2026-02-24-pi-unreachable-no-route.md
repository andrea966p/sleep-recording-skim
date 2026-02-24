---
tags: [troubleshooting, incident, raspberry-pi, network, poe]
date: 2026-02-24
severity: high
status: investigating
affected: [raspberry-pi, frigate, network]
---

# Raspberry Pi Unreachable (`No route to host`) - 2026-02-24

## Summary

- **Date/Time:** 2026-02-24 (evening, KST)
- **Severity:** High (camera ingest loss)
- **Status:** Investigating (remote-only session, no physical access)
- **Impact:** Frigate cannot receive streams from Pi (`pi_cam_0`, `pi_cam_1`)

## Symptoms

- Frigate logs repeatedly show:
  - `Error opening input file rtsp://192.168.0.11:8554/pi_cam_0`
  - `Error opening input file rtsp://192.168.0.11:8554/pi_cam_1`
  - `No route to host`
- From ASUS NVR host (`192.168.0.50`):
  - `ping 192.168.0.11` -> `Destination Host Unreachable`
  - `curl http://192.168.0.11:1984/api/streams` -> connection failed
  - ARP/neighbor state for `192.168.0.11` -> `INCOMPLETE`
- Frigate container itself is healthy and config-valid, but upstream streams are unavailable

## Context (same session)

- Earlier today, Frigate detect pipeline mismatch was fixed (`pi_cam_1` had `1280x720` while `pi_cam_0` had `1024x768`)
- Both cameras were pinned to explicit detect dimensions (`1024x768`) and verified
- Label-related experiments were attempted and then fully reverted at user request
- Current outage persisted after revert, confirming a Pi reachability problem rather than a Frigate parse/start failure

## Investigation So Far

### Confirmed Working on NVR/Frigate side

- `/srv/frigate/config/config.yml` validates
- Frigate container is healthy and starts normally
- Frigate API responds

### Confirmed Failing on Pi reachability side

- No ICMP reachability to `192.168.0.11`
- No TCP reachability to Pi go2rtc ports (`1984`, `8554`)
- Neighbor table cannot resolve Pi MAC (`INCOMPLETE`)

## Working Hypotheses

1. **PoE/power path failure** (Pi powered via Ethernet, link or power interruption)
2. **Physical cable/port issue** (bad seating, transient switch port issue)
3. **Pi not booted/latched in fault state** (similar class to previous PMIC incidents)

## Immediate Recovery Plan (on-site required)

1. Check Pi LEDs and PoE/switch link LEDs
2. Reseat Ethernet cable both ends (Pi and switch)
3. Power cycle Pi (or PoE port cycle if available)
4. Verify from ASUS host:
   - `ping 192.168.0.11`
   - `curl http://192.168.0.11:1984/api/streams`
   - `ffprobe rtsp://192.168.0.11:8554/pi_cam_0`
5. Verify Frigate ingest recovery (`/api/stats`, Live view)

## Prevention / Follow-up

- Add external ping alert from ASUS to detect Pi loss quickly
- Consider managed PoE switch for remote port-cycle recovery
- If recurrence continues, collect Pi bootloader/eeprom diagnostics after recovery and compare with Feb 19 PMIC incident

## Related

- [[2026-02-19-pmic-fault-poe-death|PMIC Fault PoE Death (Feb 19)]]
- [[../../04-journal/2026-02/2026-02-24|Journal: 2026-02-24]]
- [[../symptoms/system-freeze-ssh-hang|Symptom: System Freeze / SSH Hang]]

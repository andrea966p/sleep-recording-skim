---
tags: [infrastructure, hardware-sync, golden-config, gpio]
created: 2026-04-13
status: planned
---

# Hardware Synchronization — XDAQ GPIO ↔ Raspberry Pi

> [!tip] Upgrade Summary
> Replace ~1 s software polling with <1 ms hardware-level TTL synchronization between the NeuroNexus XDAQ Core and the Raspberry Pi camera nodes via GPIO wiring.

## Current State vs. Planned

| Aspect | Current (Software Sync) | Planned (Hardware Sync) |
|--------|------------------------|------------------------|
| **Trigger source** | `AllegoClient.get_status()` poll every 1 s | XDAQ `DAQ_ON` signal on DB25 Pin 13 |
| **Latency** | ~1 s (poll interval) | <1 ms (GPIO edge detection) |
| **Frame alignment** | None (±2 s export buffer only) | Per-frame markers via XDAQ DIN channel |
| **Clock drift** | Independent clocks (Radiens vs. Frigate) | Same electrical pulse in both timelines |
| **Failure mode** | Daemon crash → Frigate keeps recording (MQTT) | Same — GPIO listener is additive, not load-bearing |

## Architecture

Two-wire bidirectional sync between the XDAQ Core and each Raspberry Pi node:

```
┌────────────────────┐                        ┌──────────────────────┐
│  XDAQ Core (DB25)  │                        │  Raspberry Pi 5      │
│                    │                        │  GPIO Header          │
│                    │                        │                      │
│  Pin 13: DAQ_ON ───┼──► Voltage Divider ──► │  GPIO {GPIO_DAQ_ON}  │
│  (3.6V when ON)    │    (3.6V → 3.3V)       │  (Input)              │
│                    │                        │                      │
│  Pin 2: DIN 03  ◄──┼──── Direct wire ◄───── │  GPIO {GPIO_FRAME}   │
│  (accepts 2.2-5.5V)│    (3.3V is fine)      │  (Output)             │
│                    │                        │                      │
│  Pin 14: SYS GND ──┼──── Shared ground ──── │  GND (Pin 14)        │
│                    │                        │                      │
└────────────────────┘                        └──────────────────────┘
```

### Wire 1: XDAQ `DAQ_ON` → Pi GPIO (Recording Gate)

- **Signal:** `DAQ_ON` on DB25 Pin 13 goes HIGH (3.6V) whenever XDAQ acquisition is running.
- **Purpose:** Replaces software polling for start/stop detection.
- **Voltage:** Requires a voltage divider (3.6V → ~2.4V) because Pi 5 GPIO max is 3.3V.
- **Result:** Pi detects recording start/stop within <1 ms via `gpiod` edge interrupt.

### Wire 2: Pi GPIO → XDAQ `DIN 03` (Frame Sync Markers)

- **Signal:** Pi sends a 1 ms pulse on each video recording start/stop (Phase 1), optionally every frame at 15 Hz (Phase 2).
- **Purpose:** Embeds video timing markers into the EEG data stream.
- **Voltage:** Pi outputs 3.3V, XDAQ DIN accepts 2.2–5.5V — direct connection, no level shifting.
- **Result:** Each pulse is recorded at the headstage sampling rate (e.g., 20 kHz = 50 μs precision).

## Voltage Divider Design

```
XDAQ DAQ_ON (3.6V) ────┬──── 1kΩ ──── Pi GPIO {GPIO_DAQ_ON}
                        │
                       2kΩ
                        │
                       GND (shared)

Output voltage: 3.6V × 2kΩ / (1kΩ + 2kΩ) ≈ 2.4V
Pi HIGH threshold: ~1.8V ✓
Pi max input: 3.3V ✓
```

## XDAQ Core DB25 Pinout (Relevant Pins)

| DB25 Pin | Signal | Direction | Use in Our System |
|----------|--------|-----------|-------------------|
| 2 | DI 03 | Input to XDAQ | Frame sync markers from Pi |
| 13 | DAQ_ON | Output from XDAQ | HIGH when acquisition running |
| 14 | SYS GND | Ground | Shared ground reference |
| 25 | Sample_CLK | Output from XDAQ | Pulse train at headstage sampling rate (future use) |

> [!warning] Voltage Compatibility
> XDAQ DOUT is 3.6V. Pi 5 GPIO (RP1 chip) is 3.3V. The DAQ_ON → Pi direction **requires** a voltage divider or level shifter. The Pi → XDAQ DIN direction is safe (3.3V is within 2.2–5.5V input range).

## XDAQ LED Indicators for Debugging

| LED | Meaning |
|-----|---------|
| S1 | ON = Acquisition running (matches DAQ_ON signal) |
| S2 | Flashing = Activity on DIN1/DIN2 (confirms our frame sync pulses are arriving) |
| S3 | Flashing = Activity on DOUT1/DOUT2 |

## Software Integration

The GPIO sync layer publishes to MQTT topic `{MQTT_SYNC_TOPIC}` on the NVR broker. The session daemon subscribes to this topic as the **primary** recording trigger, with the existing `radiens_poller.py` software poll as a **fallback**.

```
GPIO edge event (Pi)
    │
    ▼
MQTT publish → neurosurveillance/hardware_sync
    │
    ▼
Session Daemon (NVR) subscribes
    │
    ├─ EEG_START → Start Frigate recording (same as R_OFF→R_ON)
    └─ EEG_STOP  → Stop Frigate recording + export (same as R_ON→R_OFF)
```

## What Does NOT Change

| Component | Changes? | Notes |
|-----------|----------|-------|
| go2rtc on Pi | **NO** | Golden config untouched |
| go2rtc systemd service | **NO** | Golden service untouched |
| Pi boot config | **NO** | Watchdog, WiFi disable, etc. all stay |
| Frigate on NVR | **NO** | Same Docker config, RTSP/TCP |
| MQTT broker | **NO** | Just a new topic subscription |
| Radiens poller | **Kept as fallback** | Still polls every 1 s, demoted to secondary trigger |

## Related

- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]]
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]
- [[01-infrastructure/session-daemon/architecture|Session Daemon Architecture]]
- [[00-config/production-values|Production Values]]

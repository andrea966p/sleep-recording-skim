---
tags: [infrastructure, hardware-sync, golden-config, gpio]
created: 2026-04-13
status: planned
---

# Hardware Synchronization — XDAQ GPIO ↔ Raspberry Pi

> [!danger] 2026-05-29 — our actual unit is a **Gen-1 XDAQ Core (Opal Kelly USB)**, NOT the Core2 this page assumes. Linux/driver + host-interface content here is **superseded by [[xdaq-core-gen1-ubuntu-driver]]** (verified working). DB25 pinout / voltage / recording-gate details below are **Core2-derived and UNVERIFIED for our unit** — do not wire from them until confirmed for the Gen-1 Core.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A planned upgrade (not yet deployed) that replaces the current 1-second software polling of Radiens with a hardware TTL pulse from the XDAQ DB25 connector directly to a Raspberry Pi GPIO pin.
>
> **Why it exists.** The current polling can miss the exact start moment by up to ~1 s — fine for most sleep work but not for tight cross-modal synchronization. A hardware TTL pulse drops latency below 1 ms.
>
> **How to read this page.** This overview is the entry point. [[wiring-guide|Wiring]] tells you the physical hookup; [[gpio-sync-service|GPIO Sync Service]] tells you the software listener; [[literature-review|Literature Review]] tells you why this approach is the field standard.

> [!quote] Paper-ready
> Multi-modal synchronization between the NeuroNexus XDAQ electrophysiology system and the Raspberry Pi video nodes is provided by a TTL pulse on the XDAQ DB25 digital output, wired to a GPIO pin on each Raspberry Pi and read by a lightweight Python listener service.

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

### Wire 1: XDAQ recording gate → Pi GPIO

> [!danger] 2026-05-28 — recording gate moves OFF `DAQ_ON` (pin 13) → use `DO 03` (pin 22, "Gated" mode)
> Jeffrey (NeuroNexus) tested pin 13 ([[neuronexus-inquiry-email#Reply — round 2 received 2026-05-28 (Jeffrey)|round-2 reply]]):
> - **`DAQ_ON` (pin 13) tracks STREAMING, not recording** — HIGH whenever the DAQ streams data (Allego + XDAQ-RHX), like DO 01. It is **not** a recording gate.
> - **It is dirty when idle:** in Allego, `DAQ_ON` emits **short pulses every ~0.5s while streaming is OFF** (Allego scans GPIOs when idle). That would throw false edges at the Pi.
> - **True recording gate = `DO 03` (DB25 pin 22)**: toggle the **"BNC Breakout Board"** slider (System tab) + set Digital Out Control to **"Gated"** mode → DO 03 reports **"Recording status"** (~15–20s to populate).
>
> **So Wire 1 should land on DB25 pin 22 (`DO 03`), not pin 13.** `DAQ_ON` (pin 13) / front `DIGITAL OUT 1` (DO-01) can be kept as an optional *streaming* indicator. The DB25 pinout table + diagram below still show the old pin-13 plan and need updating once the redesign is finalized (voltage of pin 22 pending — see below).

- **Signal (planned):** `DO 03` on DB25 **Pin 22** goes HIGH for the whole recording session ("Gated" mode + BNC Breakout Board toggle). *(Old plan: `DAQ_ON` pin 13 — streaming only, idle-noisy.)*
- **Purpose:** Replaces software polling for recording start/stop detection.
- **Voltage:** **3.3 V fixed** — confirmed by KC + Jeffrey 2026-05-28 ([[neuronexus-inquiry-email#Reply — round 3 received 2026-05-28 (Jeffrey)|round-3 reply]]): DB25 `DO 03`–`DO 08` and `DAQ_ON` are 3.3 V logic only; only `DO 01`/`DO 02` (BNC) switch 3.3 ↔ 5 V (and Radiens can't toggle that). **Voltage divider NOT needed** — direct wire into Pi GPIO. DMM check at first wiring is sanity only.
- **Result:** Pi detects recording start/stop within <1 ms via `gpiod` edge interrupt.

### Wire 2: Pi GPIO → XDAQ `DIN 03` (Frame Sync Markers)

- **Signal:** Pi sends a 1 ms pulse on each video recording start/stop (Phase 1), optionally every frame at 15 Hz (Phase 2).
- **Purpose:** Embeds video timing markers into the EEG data stream.
- **Voltage:** Pi outputs 3.3V, XDAQ DIN accepts 2.2–5.5V — direct connection, no level shifting.
- **Result:** Each pulse is recorded at the headstage sampling rate (e.g., 20 kHz = 50 μs precision).

## Voltage — no divider needed

> [!check] Resolved 2026-05-28 (KC + Jeffrey)
> All Core2 DB25 digital outputs `DO 03`–`DO 08` and `DAQ_ON` (pin 13) are **3.3 V fixed**. Only the BNC `DO 01`/`DO 02` outputs are 3.3/5 V switchable, and Radiens can't toggle that anyway. **Wire `DO 03` (pin 22) directly to the Pi GPIO** — no level shifter, no resistive divider. Pin 22 sits at 3.3 V = Pi GPIO ceiling exactly. Sanity DMM check at first plug-in only.

## XDAQ Core DB25 Pinout (Relevant Pins)

> [!info] Authoritative pinout + specs → [[xdaq-core2-manual-reference|XDAQ Core2 Manual Reference]]
> Pins below match the KONTEX Core2 manual (figures archived there). `DI 03`=Pin 2 (Pin 22 is `DO 03`), `DAQ_ON`=Pin 13, `GND`=Pin 14, `Sample_CLK`=Pin 25. The manual confirms `DAQ_ON` is on the DB25 ("logic high at onset of a recording session"). **Voltage: 3.3 V on all DB25 DOs + `DAQ_ON`** (KC + Jeffrey, 2026-05-28).

| DB25 Pin | Signal | Direction | Use in Our System |
|----------|--------|-----------|-------------------|
| 2 | DI 03 | Input to XDAQ | Frame sync marker from Pi (Pi 1); DI 04–06 = pins 15/3/16 for Pis 2–4 at scale |
| 13 | DAQ_ON | Output from XDAQ | **STREAMING** indicator (HIGH while streaming; ~0.5s idle pulses in Allego). Optional streaming flag only — NOT the recording gate. |
| 22 | **DO 03** | Output from XDAQ | **★ Recording gate** — reports "Recording status" in "Gated" mode w/ BNC Breakout Board toggle (per 2026-05-28 reply). HIGH for whole recording session. |
| 14 | SYS GND | Ground | Shared ground reference |
| 25 | Sample_CLK | Output from XDAQ | Pulse train at headstage sampling rate (future use) |

> [!warning] Allego "BNC Breakout Board" toggle is now a hard dependency
> Both the recording gate (`DO 03`, pin 22) and the multi-Pi return inputs (`DI 03`–`DI 06`) only appear/function in Allego when the **"BNC Breakout Board"** slider (System tab) is toggled ON. The DI/DO channels then show in the System + Monitor tabs and are synced + stored alongside neural data. Document this in the [[02-procedures/hardware-sync-setup|Setup Procedure]].

> [!check] Voltage Compatibility — resolved (2026-05-28)
> Core2 DB25 digital outputs `DO 03`–`DO 08` and `DAQ_ON` (pin 13) are **3.3 V fixed** — confirmed by KC + Jeffrey ([[neuronexus-inquiry-email#Reply — round 3 received 2026-05-28 (Jeffrey)|round-3 reply]]). Only the BNC `DO 01`/`DO 02` outputs are 3.3/5 V switchable, and Radiens can't toggle that. **Wire DB25 outputs directly to Pi 5 GPIO** — no divider, no level shifter. 3.3 V sits at Pi GPIO ceiling exactly (within spec, zero headroom — fine for clean digital signals). DMM sanity check at first wiring only. See [[xdaq-core2-manual-reference|Manual Reference]].
>
> Pi → XDAQ DIN direction: safe (Pi 3.3 V within 2.2–5.5 V input range; vendor empirically registers DIs down to 1.7 V).

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
- [[01-infrastructure/hardware-sync/references-and-justification|Design Justification & References]]
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]
- [[01-infrastructure/hardware-sync/xdaq-core2-manual-reference|XDAQ Core2 Manual Reference]]
- [[01-infrastructure/hardware-sync/kontex-developer-portal-notes|Kontex Developer Portal Notes]] — libxdaq / pylibxdaq / Linux Thunderbolt
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]
- [[01-infrastructure/session-daemon/architecture|Session Daemon Architecture]]
- [[00-config/production-values|Production Values]]

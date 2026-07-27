---
tags: [infrastructure, hardware-sync, golden-config, gpio]
created: 2026-04-13
status: planned
---

# Hardware Synchronization — XDAQ GPIO ↔ Raspberry Pi

> [!check] 2026-06-05 — Gen-1 confirmed by KC Kong: **DB25 pinout Gen1 = Gen2** ([[neuronexus-inquiry-email#Reply — round 3b received 2026-06-05 (KC Kong)|round-3b reply]]). All DB25 pinout / 3.3 V output / `DO 03` Gated recording-gate details below apply to our Gen-1 XDAQ Core (Opal Kelly USB, serial 0C006218) — prior "UNVERIFIED for Gen-1" hold cleared. Linux/driver + host-interface content here is **superseded by [[xdaq-core-gen1-ubuntu-driver]]** (verified working). Fan-out: single `DO 03` star-wires to ≥4 Pi GPIO (driver SN74LVC2G17, ~20 mA, no buffer). Grounding: **star ground, Core = hub**. See [[wiring-guide#Multi-Pi fan-out and star grounding|Wiring Guide]].

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

Two-wire bidirectional sync per Pi, **one gate fanned out to all Pis**; everything referenced to a single star-ground at the Core (DB25 pin 14). All voltages 3.3 V — no level shift, no divider.

```
        XDAQ Core (Gen-1, DB25)                              Raspberry Pi 5 nodes
┌──────────────────────────────────┐
│ Pin 22  DO 03 (recording gate) ───┼──●──220Ω──► Pi1 GPIO 17 (in)  [+10kΩ pulldown]
│  3.3V, "Gated" mode,              │  ●──220Ω──► Pi2 GPIO 17 (in)  [+10kΩ pulldown]
│  BNC Breakout Board ON            │  ●──220Ω──► Pi3 GPIO 17 (in)  [+10kΩ pulldown]
│  driver SN74LVC2G17 ~20mA         │  ●──220Ω──► Pi4 GPIO 17 (in)  [+10kΩ pulldown]
│                                   │  (star node — fan-out, no buffer)
│                                   │
│ Pin 2   DI 03 (frame ret. Pi1) ◄──┼──────────── Pi1 GPIO 27 (out)   direct, 3.3V
│ Pin 15  DI 04 (frame ret. Pi2) ◄──┼──────────── Pi2 GPIO 27 (out)
│ Pin 3   DI 05 (frame ret. Pi3) ◄──┼──────────── Pi3 GPIO 27 (out)
│ Pin 16  DI 06 (frame ret. Pi4) ◄──┼──────────── Pi4 GPIO 27 (out)
│                                   │
│ Pin 14  GND (star-ground hub) ────┼──┬───────── Pi1 GND   (home-run)
│                                   │  ├───────── Pi2 GND   (home-run)
│                                   │  ├───────── Pi3 GND   (home-run)
│                                   │  └───────── Pi4 GND   (home-run)
└──────────────────────────────────┘   no Pi-to-Pi GND ties (star, not daisy-chain)
```

### Wire 1: XDAQ recording gate → Pi GPIO

> [!check] Gate = `DO 03` (DB25 pin 22), "Gated" mode — diagram above redrawn 2026-06-05
> Resolved across the vendor thread ([[neuronexus-inquiry-email#Reply — round 2 received 2026-05-28 (Jeffrey)|round-2]] + [[neuronexus-inquiry-email#Reply — round 3b received 2026-06-05 (KC Kong)|round-3b]]):
> - **`DAQ_ON` (pin 13) tracks STREAMING, not recording** — HIGH whenever the DAQ streams (Allego + XDAQ-RHX), like DO 01; **not** a recording gate.
> - **Dirty when idle:** in Allego, `DAQ_ON` emits **short pulses every ~0.5s while streaming is OFF** (Allego scans GPIOs idle) → false edges at the Pi.
> - **Recording gate = `DO 03` (DB25 pin 22)**: toggle **"BNC Breakout Board"** slider (System tab) + Digital Out Control = **"Gated"** → DO 03 reports **"Recording status"** (~15–20s to populate). 3.3 V fixed, driver SN74LVC2G17 ~20 mA.
>
> Wire 1 lands on **pin 22 (`DO 03`)**, direct to Pi GPIO (no divider), star-fanned to all Pis. `DAQ_ON` (pin 13) / front `DIGITAL OUT 1` (DO-01) optional *streaming* flag. Architecture diagram above + DB25 table below reflect this.

- **Signal (planned):** `DO 03` on DB25 **Pin 22** goes HIGH for the whole recording session ("Gated" mode + BNC Breakout Board toggle). *(Old plan: `DAQ_ON` pin 13 — streaming only, idle-noisy.)*
- **Purpose:** Replaces software polling for recording start/stop detection.
- **Voltage:** **3.3 V fixed** — confirmed by KC + Jeffrey 2026-05-28 ([[neuronexus-inquiry-email#Reply — round 3 received 2026-05-28 (Jeffrey)|round-3 reply]]): DB25 `DO 03`–`DO 08` and `DAQ_ON` are 3.3 V logic only; only `DO 01`/`DO 02` (BNC) switch 3.3 ↔ 5 V (and Radiens can't toggle that). **Voltage divider NOT needed** — direct wire into Pi GPIO. DMM check at first wiring is sanity only.
- **Result:** Pi detects recording start/stop within <1 ms via `gpiod` edge interrupt.

### Wire 2: Pi GPIO → XDAQ `DIN 03` (Frame Sync Markers)

- **Signal:** Pi sends a 1 ms pulse on each video recording start/stop (Phase 1), optionally every frame at 15 Hz (Phase 2). **⚠ 2026-07-27: Phase 1 alone is NOT sufficient — two pulses per session leave clock drift unrecoverable. Prefer a periodic train (~1 pulse / 10 s). See Software Integration below.**
- **Purpose:** Embeds video timing markers into the EEG data stream. **This wire, not Wire 1, is what actually delivers synchronization.**
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

> [!warning] 2026-07-27 — CORRECTED. Wire 1 must NOT drive the recording toggle.
> The flow below originally ended in `EEG_START → Start Frigate recording` / `EEG_STOP → Stop Frigate recording`, i.e. it fed the sub-millisecond `DO 03` edge straight back into the MQTT recording toggle. **That discards the precision in the last step** and contradicts the "Frame alignment" and "Clock drift" rows of the Current State vs Planned table above.
>
> Two hard reasons, both source-confirmed 2026-07-27:
> - **Toggling OFF DELETES the tail.** Frigate `frigate/record/maintainer.py:250` calls `drop_segment()` and unlinks any `/tmp/cache` segment not yet flushed when it sees recording disabled. ffmpeg closes a segment every 10 s, the maintainer flushes every 5 s, so **every toggled session permanently loses 10 to 20 seconds off its end.** Measured live: a 37 s window yielded 19.0 s.
> - **Toggling ON does not start capture at the toggle.** Capture begins at whatever cache segment boundary is in flight, up to 10 s away, and the offset is uniform random per session rather than constant, so it CANNOT be calibrated out.
>
> Full analysis, storage budget, and the decision → [[07-decisions/2026-07-27-video-eeg-sync-recording-architecture|Video-EEG Sync — The Recording Toggle Is Not Sync-Capable]].

The GPIO sync layer publishes to MQTT topic `{MQTT_SYNC_TOPIC}` on the NVR broker. The session daemon subscribes to this topic as the **primary** session-boundary signal, with the existing `radiens_poller.py` software poll as a **fallback**.

Frigate records **continuously**. The gate marks session boundaries as METADATA and drives the export cut, it does not start or stop capture.

```
GPIO edge event (Pi)
    │
    ├──► Wire 2 pulse → XDAQ DI 03  ★ THIS is what actually delivers sync
    │      (digitized at headstage rate, 50 µs @ 20 kHz;
    │       independent of Frigate, of container timestamps,
    │       and of network latency)
    │
    ▼
MQTT publish → neurosurveillance/hardware_sync
    │
    ▼
Session Daemon (NVR) subscribes
    │
    ├─ EEG_START → journal session start; Frigate ALREADY recording (no toggle)
    └─ EEG_STOP  → journal session end; export the [start, end] window
                   (footage stays on disk, a sloppy cut can be re-cut)
```

> [!warning] Wire 2 as currently specced CANNOT measure clock drift
> [[gpio-sync-service]] emits a pulse only on the gate's rising and falling edge, i.e. **two pulses per session** (Phase 1). That pins the two endpoints and says nothing about what the free-running camera clock did in between. Over a 12 h run a 0.1 % camera clock error is ~43 s of skew, and two pulses cannot tell you whether it accrued linearly, in a step, or not at all.
>
> **Recommended: a periodic pulse train, e.g. 1 pulse per 10 s** (~4,300 pulses per 12 h). Recovers the drift curve at negligible cost. Phase 2 per-frame 15 Hz (~648k pulses per 12 h per Pi) only if a specific analysis needs single-frame attribution. **Decide this before the listener is written.**

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

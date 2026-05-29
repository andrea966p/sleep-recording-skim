---
tags: [infrastructure, hardware-sync, wiring, gpio]
created: 2026-04-13
status: planned
---

# XDAQ ↔ Raspberry Pi Wiring Guide

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Physical wiring instructions for connecting the XDAQ DB25 digital-output connector to a Raspberry Pi 5 GPIO pin.
>
> **Why it exists.** This is the cable that carries the synchronization TTL pulse. Wrong pin, wrong polarity, or wrong ground reference and the planned hardware-sync upgrade either does nothing or damages the Pi.
>
> **How to read this page.** Read top to bottom before touching wires. The BOM lists every part needed; the wiring diagram tells you which DB25 pin goes to which GPIO. Always power off both ends before working on the connection.

> [!quote] Paper-ready
> Hardware synchronization between the XDAQ DB25 digital output and the Raspberry Pi GPIO header is established via a level-shifted TTL line with shared ground reference; the cable carries a single rising-edge DAQ_ON signal per recording session.

> [!warning] Safety First
> Always power off both the XDAQ and the Raspberry Pi before connecting or disconnecting any wires to GPIO pins or the DB25 connector. Verify all connections with a multimeter before powering on.

## Bill of Materials

> [!info] BOM revised 2026-05-28 (rev-b) — voltage Q now resolved; KC Kong reply still pending on fan-out / grounding / Ubuntu drivers
> The revised list assumes:
> - **2 Raspberry Pi 5 nodes currently** (Pi1 + Pi2), wiring designed to extend to **4 Pi 5** without re-purchase.
> - **Voltage Q CLOSED** — KC + Jeffrey ([[neuronexus-inquiry-email#Reply — round 3 received 2026-05-28 (Jeffrey)|round-3 reply]]) confirm DB25 `DO 03`–`DO 08` and `DAQ_ON` are **3.3 V fixed**. **No divider needed.** Resistor assortment kit kept as cheap shop stock (pull-downs, spares) — not load-bearing.
> - **KC Kong still pending** on (a) fan-out: star wiring vs buffer for 1× `DO 03` → 4× Pi GPIO inputs (depends on DB25 DO drive current), (b) grounding 4 devices on `SYS GND` without ground loops, (c) Ubuntu 24.04 Core2 drivers / Thunderbolt-auth. The 74HCT244 buffer stays in the BOM as a $2 contingency — sits in the drawer if KC says "star wiring OK".
> - **BNC Breakout Board from NeuroNexus is no longer in the BOM.** Allego's software "BNC Breakout Board" toggle exposes `DO 03` + extra DIs directly on the DB25; no physical breakout from the vendor is required ([[neuronexus-inquiry-email#Reply — round 2 received 2026-05-28 (Jeffrey)|round-2 reply]]).

### Order-now set ("safe to buy ahead of KC Kong's reply")

| Item                                                     | Qty | Purpose                                                                                                                                                                              | ~Cost                        |
| -------------------------------------------------------- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| DB25 **male** screw-terminal breakout board              | 1   | Plugs into the Core2 rear DB25 (chassis = female receptacle — eyeball before ordering)                                                                                               | $5–10                        |
| Dupont jumper wires **F–F**, 20 cm, 40-pack              | 1   | DB25 breakout ↔ Pi GPIO header                                                                                                                                                       | ~$5                          |
| Dupont jumper wires **M–F**, 20 cm, 40-pack              | 1   | Breadboard ↔ Pi GPIO or breakout                                                                                                                                                     | ~$5                          |
| Mini solderless breadboard (400-tie)                     | 2   | Mount divider and/or buffer near Core2 (or one near each Pi)                                                                                                                         | ~$4                          |
| Resistor assortment kit (incl. 220 Ω, 1 kΩ, 10 kΩ)        | 1   | Series safety resistor (220 Ω) on direct `DO 03` → Pi line, pull-downs (10 k) on Pi GPIO inputs, generic lab stock. *Divider no longer needed (3.3 V fixed).*                       | $6–8                         |
| **74HCT244** octal buffer/line driver (DIP-20)           | 2   | Drives `DO 03` fan-out to ≥4 Pi GPIO inputs if KC recommends a buffer; one spare. Powered from 3.3 V on the Pi side (HCT input is 5 V-tolerant, output is rail-to-rail)              | ~$2 ea                       |
| DIP-20 IC socket                                         | 2   | Hot-swap the 74HCT244 without resoldering                                                                                                                                            | ~$0.50 ea                    |
| Small perfboard / stripboard                             | 2   | Permanent mount for the divider + optional buffer once design is final                                                                                                               | ~$3                          |
| Heat-shrink tubing assortment                            | 1   | Insulate Dupont → solder joints if going beyond pure breadboard                                                                                                                      | ~$5                          |
| **USB logic analyzer** (Saleae clone, Cypress FX2 8-ch)  | 1   | **Mandatory** for the "level vs idle-pulse" check on `DO 03` (pin 22) in Gated mode — a DMM averages can hide ~0.5 s idle pulses. Also useful for capturing Pi → DI 03 frame markers | $10–15                       |
| (Lab-supplied) Digital multimeter, DC volts              | 1   | Continuity + pin-22 voltage check before powering the Pi                                                                                                                             | $0 if available, ~$20 if not |

**Sub-total (without DMM):** ~$40–55.

### Hold-until-answers

| Item | Trigger to buy |
|------|----------------|
| Additional 74HCT244 buffer(s) at scale | KC confirms buffer needed for 4-Pi fan-out + lab decides to keep more spares |
| DB25 **M–F extension cable** (1–2 m) | Core2 not colocated with the Pi rack — extend reach without dangling the breakout off the connector |
| Pi 5 + PoE HAT (nodes 3–4) | Separate scale-up purchase, not in this wiring BOM |

### Removed / not needed

- ~~BNC Breakout Board from NeuroNexus~~ — Allego software toggle exposes the DB25 DIs / `DO 03` directly; no physical breakout required.
- ~~Voltage divider (1 kΩ + 2 kΩ)~~ — `DO 03` (pin 22) is **3.3 V fixed** (confirmed by KC + Jeffrey 2026-05-28); direct wire from DB25 → Pi GPIO 17 is safe. Assortment kit still bought for series/pull-down resistors, not divider.
- ~~Fixed-value 1 % divider resistor pair~~ — same reason; voltage Q closed at 3.3 V.

## Wiring Diagram

> [!danger] 2026-05-28 — Wire 1 recording gate moves from pin 13 to pin 22 + voltage divider DROPPED (diagrams below not yet redrawn)
> NeuroNexus tested `DAQ_ON` ([[neuronexus-inquiry-email#Reply — round 2 received 2026-05-28 (Jeffrey)|round-2 reply]]): **pin 13 `DAQ_ON` indicates STREAMING, not recording**, and emits **~0.5s idle pulses in Allego** (false edges). The real recording gate is **`DO 03` = DB25 pin 22**, exposed by toggling the **"BNC Breakout Board"** slider (System tab) + Digital Out Control = **"Gated"** mode.
> **Wire 1 should land on pin 22 (`DO 03`), not pin 13.** Optionally keep `DAQ_ON` (pin 13) / front `DIGITAL OUT 1` (DO-01) as a *streaming* flag.
> **Voltage Q CLOSED 2026-05-28** ([[neuronexus-inquiry-email#Reply — round 3 received 2026-05-28 (Jeffrey)|round-3 reply]]): KC + Jeffrey confirm DB25 `DO 03`–`DO 08` and `DAQ_ON` are **3.3 V fixed**. **Voltage divider is no longer needed** — wire `DO 03` (pin 22) directly to Pi GPIO 17 with shared GND. The Wire 1 diagram + validation steps below still show the old pin-13 + divider plan; redraw pending.

> [!check] Pin numbers + voltage verified against the manual + vendor
> DB25 pins (manual + Jeffrey confirm): `DI 03`=**Pin 2**, `DAQ_ON`=Pin 13, `DO 03`=**Pin 22** (★ recording gate), `GND`=Pin 14, `SAMPLE CLK`=Pin 25. Voltage on **`DO 03`–`DO 08` + `DAQ_ON` = 3.3 V fixed** (KC + Jeffrey 2026-05-28). Only `DO 01`/`DO 02` (BNC) switch 3.3 ↔ 5 V. **Direct wire DB25 → Pi GPIO** (3.3 V = Pi GPIO ceiling).

### Wire 1: DAQ_ON → Pi GPIO (with voltage divider)

```
XDAQ DB25                    Breadboard                Pi 5 GPIO Header
Pin 13 (DAQ_ON) ──────────── 1kΩ resistor ──────────── Pin 11 (GPIO 17)
                               │
                              2kΩ resistor
                               │
XDAQ DB25 Pin 14 (GND) ───── GND bus ────────────────── Pin 14 (GND)
```

### Wire 2: Pi GPIO → XDAQ DIN (direct connection)

```
Pi 5 GPIO Header              XDAQ DB25
Pin 13 (GPIO 27) ──────────── Pin 2 (DI 03)

(GND already shared from Wire 1)
```

### Physical Pin Reference — Raspberry Pi 5 GPIO Header

```
                    Pi 5 GPIO Header (top view, USB ports facing down)
                    ┌────────────────────────┐
            3.3V  1 │ ●  ●  │ 2   5V
  (SDA)   GPIO 2  3 │ ●  ●  │ 4   5V
  (SCL)   GPIO 3  5 │ ●  ●  │ 6   GND
          GPIO 4  7 │ ●  ●  │ 8   GPIO 14
             GND  9 │ ●  ●  │ 10  GPIO 15
 ► DAQ_ON GPIO 17 11│ ●  ●  │ 12  GPIO 18
 ► FRAME  GPIO 27 13│ ●  ●  │ 14  GND  ◄── Shared GND
          GPIO 22 15│ ●  ●  │ 16  GPIO 23
            3.3V  17│ ●  ●  │ 18  GPIO 24
                   ... (remaining pins not used)
                    └────────────────────────┘

► = pins used by hardware sync
```

## Pre-Power Validation (Multimeter)

Before powering on, verify with a continuity test:

1. **Wire 1 path:** DB25 Pin 13 → through 1kΩ → to Pi GPIO 17 (Pin 11). Should show ~1kΩ resistance.
2. **Wire 2 path:** Pi GPIO 27 (Pin 13) → to DB25 Pin 2. Should show near-zero resistance (direct wire).
3. **Ground path:** DB25 Pin 14 → to Pi GND (Pin 14). Should show near-zero resistance.
4. **No shorts:** Check that GPIO 17 and GPIO 27 are NOT shorted to each other, to 3.3V, or to 5V.

## Post-Power Validation (Multimeter)

With XDAQ powered on and Radiens software **not** recording (BNC Breakout Board toggle ON, Digital Out Control = "Gated"):

1. Measure DB25 Pin 22 (`DO 03`) to Pin 14 (GND): should read **~0 V** (gate LOW, no recording).
2. Start a **recording** session in Radiens (recording, not just streaming — wait ~15–20 s for the gate to populate after first toggling BNC Breakout Board).
3. Measure DB25 Pin 22 to Pin 14: should read **~3.3 V** (gate HIGH, recording).
4. Stop recording. Voltage should drop back to ~0 V.

Optional cross-check on pin 13 (`DAQ_ON`, streaming indicator only):

- Streaming ON, recording OFF: pin 13 = ~3.3 V steady.
- Streaming OFF: pin 13 emits short pulses every ~0.5 s in Allego (idle scan — expected, do NOT use as gate).

With Pi powered on:

6. Set GPIO 27 as output HIGH temporarily:
   ```bash
   gpioset gpiochip4 27=1
   ```
7. Measure DB25 Pin 2 to Pin 14: should read **~3.3V**.
8. Set back to LOW:
   ```bash
   gpioset gpiochip4 27=0
   ```

> [!tip] GPIO Chip on Pi 5
> The Pi 5 uses `gpiochip4` for the main 40-pin GPIO header (RP1 chip). Older Pis use `gpiochip0`. Verify with `gpioinfo gpiochip4`.

## ⭐ Pin 22 (`DO 03`) sanity check — run at first plug-in

> [!abstract] Why this step exists (post 2026-05-28)
> Voltage Q is closed on paper: KC + Jeffrey ([[neuronexus-inquiry-email#Reply — round 3 received 2026-05-28 (Jeffrey)|round-3 reply]]) confirm `DO 03` and all DB25 DO-03…08 + `DAQ_ON` = **3.3 V fixed**. This check is **sanity only** — confirm pin 22 actually swings 0 ↔ 3.3 V cleanly in Gated mode with BNC Breakout Board ON, with no spurious idle pulses, before committing the direct wire and starting trials.

> [!danger] Pi disconnected during first measurement
> Pi 5 GPIO has no over-voltage protection. First-time check with Pi unplugged — DMM only.

**You need:** DMM (DC volts), optional USB logic analyzer (better — catches idle pulses a DMM averages out), access to DB25 pins 22 + 14 via the screw-terminal breakout. XDAQ host running Radiens with the **BNC Breakout Board** slider ON and **Digital Out Control = "Gated"**.

1. **Identify the pins.** DB25 pin **22** (`DO 03`) + pin **14** (`GND`). Connector housing prints pin 1 and pin 25 — count from there; cross-check [[xdaq-core2-manual-reference#DB25 IO Connector Pinout|pinout figure]]. Bottom row L→R = 1…13; top row = 14…25.
2. **Set meter** to DC volts, 20 V range (or autorange). Black probe → pin 14, red probe → pin 22.
3. **Baseline (idle).** XDAQ powered on, Radiens **not recording**. Expect **~0 V** (gate LOW). Note: pin 22 may take 15–20 s after first BNC-Breakout-Board toggle to populate.
4. **Start a RECORDING session** in Radiens. Expect pin 22 → **~3.3 V** within ~1 s.
5. **Read + record the exact number.** Goes in the methods record. Expect 3.2–3.4 V.
6. **Stop recording.** Voltage should fall back to **~0 V** cleanly. **Logic-analyzer cross-check (recommended):** capture pin 22 for 30 s of idle (no streaming, no recording) — should be **flat 0 V, no pulses**. If pulses appear, the "BNC Breakout Board" toggle or "Gated" mode is misconfigured; do NOT wire to Pi until clean.
7. **Optional `DAQ_ON` pin 13 cross-check** (if planning to use it as streaming flag): streaming-on → ~3.3 V; streaming-off → short pulses every ~0.5 s (expected idle scan, not a fault).

> [!note] Record for publication
> Log measured `DO 03` (pin 22) voltage, whether it stays HIGH for the entire recording session (level), and idle behavior (logic-analyzer trace if available), in the session journal / methods notes.

## Related

- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]]
- [[01-infrastructure/hardware-sync/xdaq-core2-manual-reference|XDAQ Core2 Manual Reference]] — authoritative pinout + the 3.3 V finding behind this check
- [[01-infrastructure/hardware-sync/references-and-justification|Design Justification & References]] — datasheet sources for this BOM and pinout
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]]
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]

- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]]
- [[01-infrastructure/hardware-sync/references-and-justification|Design Justification & References]] — datasheet sources for this BOM and pinout
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]]
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]

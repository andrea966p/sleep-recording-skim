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

| Item                                          | Purpose                                           | Approx. Cost       | Source                        |
| --------------------------------------------- | ------------------------------------------------- | ------------------ | ----------------------------- |
| DB25 male screw-terminal breakout board       | Access XDAQ DB25 pins without soldering           | ~$5–10             | Amazon / electronics supplier |
| 1kΩ resistor (1/4W, through-hole)             | Voltage divider upper leg                         | ~$0.10             | Any electronics supplier      |
| 2kΩ resistor (1/4W, through-hole)             | Voltage divider lower leg                         | ~$0.10             | Any electronics supplier      |
| Dupont jumper wires (female-to-female, 20 cm) | Connect breakout board to Pi GPIO header          | ~$3                | Amazon                        |
| (Optional) BNC Breakout Board for XDAQ        | Professional-grade DB25 access via BNC connectors | Contact NeuroNexus | NeuroNexus                    |
| (Optional) Small breadboard                   | Mounting voltage divider                          | ~$2                | Any electronics supplier      |

**Total cost: ~$10–15** (excluding optional BNC breakout)

## Wiring Diagram

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

With XDAQ powered on and Radiens software **not** acquiring:

1. Measure DB25 Pin 13 to Pin 14: should read **~0V** (DAQ_ON is LOW).
2. Start acquisition in Radiens.
3. Measure DB25 Pin 13 to Pin 14: should read **~3.6V** (DAQ_ON is HIGH).
4. Measure after voltage divider (at Pi GPIO 17 input): should read **~2.4V**.
5. Stop acquisition. Voltage should drop back to ~0V.

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

## Related

- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]]
- [[01-infrastructure/hardware-sync/references-and-justification|Design Justification & References]] — datasheet sources for this BOM and pinout
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]]
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]

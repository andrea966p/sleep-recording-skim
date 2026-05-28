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

> [!danger] 2026-05-28 — Wire 1 recording gate changes from pin 13 to pin 22 (diagrams below not yet redrawn)
> NeuroNexus tested `DAQ_ON` ([[neuronexus-inquiry-email#Reply — round 2 received 2026-05-28 (Jeffrey)|round-2 reply]]): **pin 13 `DAQ_ON` indicates STREAMING, not recording**, and emits **~0.5s idle pulses in Allego** (false edges). The real recording gate is **`DO 03` = DB25 pin 22**, exposed by toggling the **"BNC Breakout Board"** slider (System tab) + Digital Out Control = **"Gated"** mode.
> **Wire 1 should land on pin 22 (`DO 03`), not pin 13.** Optionally keep `DAQ_ON` (pin 13) / front `DIGITAL OUT 1` (DO-01) as a *streaming* flag. Pin-22 logic-high voltage is pending the vendor (likely 3.3 V — Allego can't set 5 V; divider likely unneeded). The Wire 1 diagram + validation steps below still show the old pin-13 plan; finalize once pin-22 voltage is measured. Extend the [[#⭐ Pin 13 (DAQ_ON) Voltage Check — run this BEFORE building/buying the divider|voltage check]] below to pin 22.

> [!info] Pin numbers verified against the manual
> The DB25 pins below are confirmed in [[xdaq-core2-manual-reference|XDAQ Core2 Manual Reference]]: `DAQ_ON`=Pin 13, `DI 03`=**Pin 2** (Pin 22 is `DO 03` — do not wire there), `GND`=Pin 14, `SAMPLE CLK`=Pin 25. ⚠️ The voltage divider here assumes a 3.6 V output; the Core2 manual states **DB25 outputs are 3.3 V** — if `DAQ_ON` measures 3.3 V at pin 13, the divider can be dropped (direct wire). Measure before finalizing. See manual reference + [[references-and-justification#Open Items — confirm before purchase|Design Justification → Open Items]].

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

## ⭐ Pin 13 (DAQ_ON) Voltage Check — run this BEFORE building/buying the divider

> [!abstract] Why this step exists
> The [[xdaq-core2-manual-reference|Core2 manual]] says DB25 digital **outputs are 3.3 V** (not the 3.6 V the divider was designed around) — but it does **not** tabulate `DAQ_ON`'s own voltage. So measure pin 13 directly. The result decides the wiring:
> - **≤ 3.3 V** → no divider needed; wire `DAQ_ON` (pin 13) **straight** to the Pi GPIO (with shared GND).
> - **> 3.3 V** (e.g. 3.6 V) → keep the 1 kΩ/2 kΩ divider from the BOM.

> [!danger] Do NOT connect the Raspberry Pi until this measurement is done
> The Pi 5 GPIO has **no over-voltage protection** and a hard 3.3 V ceiling. Confirm the actual `DAQ_ON` voltage first, with the Pi disconnected.

**You need:** a digital multimeter (DC volts) and access to DB25 pins 13 + 14 (via the screw-terminal breakout, or careful probing on the connector). The XDAQ host running Radiens.

1. **Identify the pins.** On the DB25, locate pin **13** (`DAQ_ON`) and pin **14** (`GND`). The connector/housing prints pin 1 and pin 25 — count from there; cross-check against the [[xdaq-core2-manual-reference#DB25 IO Connector Pinout|pinout figure]]. (Bottom row left→right = 1…13; top row = 14…25.)
2. **Set the meter** to DC voltage, 20 V range (or autorange).
3. **Baseline (idle).** XDAQ powered on, Radiens **not recording**. Black probe → pin 14 (GND), red probe → pin 13. Expect **~0 V**.
4. **Start a RECORDING session in Radiens** (not just streaming — `DAQ_ON` = "logic high at onset of a *recording* session"). If unsure whether streaming alone asserts it, test both: note the reading while *streaming-only*, then while *recording*.
5. **Read and record the voltage** while recording. **Write the exact number down** (this is the deciding value, and it goes in the methods record). Expect a logic-high in the 3.3–3.6 V range.
6. **Stop recording.** Voltage should fall back to **~0 V**. Note whether it stays high for the whole session (level) or only pulses at the start (one-shot) — a level signal is what the design assumes.
7. **Decide:**
   - Measured **≤ 3.3 V** → update [[references-and-justification#Open Items — confirm before purchase|Open Item #2]]: drop the divider, wire pin 13 → Pi GPIO 17 directly. Skip the 1 kΩ/2 kΩ resistors from the BOM.
   - Measured **> 3.3 V** → keep the divider as drawn in [Wire 1](#wire-1-daq_on-→-pi-gpio-with-voltage-divider).

> [!note] Record for publication
> Log the measured `DAQ_ON` voltage, whether it is level or pulsed, and whether it tracks *streaming* vs *recording*, in the session journal / methods notes. These three facts close the last open hardware questions ([[neuronexus-inquiry-email|inquiry note]] Q3/Q4).

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

---
tags: [infrastructure, hardware-sync, wiring, gpio]
created: 2026-04-13
status: planned
---

# XDAQ ↔ Raspberry Pi Wiring Guide

> [!check] 2026-06-05 — Gen-1 confirmed by KC Kong: **DB25 pinout for Gen1 = Gen2** ([[neuronexus-inquiry-email#Reply — round 3b received 2026-06-05 (KC Kong)|round-3b reply]]). The DB25 pin numbers, 3.3 V output, and "BNC Breakout Board / Gated DO 03" recording-gate mechanism below all apply to our Gen-1 XDAQ Core (Opal Kelly USB, serial 0C006218). **Cleared the prior "UNVERIFIED for Gen-1" hold.** Output driver = TI **SN74LVC2G17 (~20 mA)** → single `DO 03` star-wires to ≥4 Pi GPIO inputs with no buffer. Grounding = **star ground, Core = hub**. Driver/connectivity already solved: [[xdaq-core-gen1-ubuntu-driver]]. Remaining = bench validation only.

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

> [!info] BOM rev-c (2026-06-05) — KC Kong round-3b closed ALL vendor items; buffer dropped, star wiring + star ground confirmed
> The list now assumes:
> - **2 Raspberry Pi 5 nodes currently** (Pi1 + Pi2), wiring designed to extend to **4 Pi 5** without re-purchase.
> - **Voltage CLOSED** — DB25 `DO 03`–`DO 08` and `DAQ_ON` = **3.3 V fixed** (KC + Jeffrey). **No divider needed.** Resistor assortment kit kept as cheap shop stock (pull-downs, spares) — not load-bearing.
> - **Fan-out CLOSED → no buffer** — KC round-3b ([[neuronexus-inquiry-email#Reply — round 3b received 2026-06-05 (KC Kong)|round-3b reply]]): Gen-1 DB25 output driver = TI **SN74LVC2G17, ~20 mA**. Pi 5 GPIO inputs are high-impedance (≈2.6 mA worst-case for 8 Pis w/ 10 kΩ pull-downs) → 20 mA ≫ load. **Single `DO 03` star-wires directly to all Pi GPIO inputs. 74HCT244 buffer dropped** (moved to "removed / not needed").
> - **Grounding CLOSED → star ground** — KC: XDAQ Core = ground hub; each Pi GND home-runs to Core `GND` (pin 14), no daisy-chain, no Pi-to-Pi GND. See [[#Multi-Pi fan-out and star grounding]] below.
> - **Ubuntu drivers** — resolved ourselves earlier ([[xdaq-core-gen1-ubuntu-driver]]); not a BOM item.
> - **BNC Breakout Board from NeuroNexus is no longer in the BOM.** Allego's software "BNC Breakout Board" toggle exposes `DO 03` + extra DIs directly on the DB25; no physical breakout from the vendor is required ([[neuronexus-inquiry-email#Reply — round 2 received 2026-05-28 (Jeffrey)|round-2 reply]]).

### Order-now set ("safe to buy ahead of KC Kong's reply")

> [!info] Part numbers are concrete starting points, not stock-verified
> MPNs below are common, in-production parts chosen for the final 4-Pi star design. Confirm live availability before ordering. Korea (KAIST) sourcing: **DigiKey/Mouser KR** for the Yageo resistors + breakout; **Devicemart / Eleparts / IC뱅크** (Korean hobby shops) or **Coupang** for jumpers, breadboard, perfboard, heat-shrink, logic analyzer. Quantities sized for **4 Pi nodes + spares**.

| Item                                                     | Qty | Suggested part / MPN                                                                 | Purpose                                                                                                                              | ~Cost  |
| -------------------------------------------------------- | --- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------ |
| DB25 **male** D-SUB → screw-terminal breakout            | 1   | **Winford BRKMB25M** (DB25 male) — alt: DSD TECH / DTECH DB25-M breakout             | Plugs into the Gen-1 Core rear DB25 (chassis = female receptacle — eyeball before ordering)                                          | $8–12  |
| Dupont jumper wires **F–F**, 20 cm, 40-pack              | 1   | EDGELEC / generic 2.54 mm F–F, 20 cm                                                 | DB25 breakout ↔ Pi GPIO header / star node                                                                                           | ~$5    |
| Dupont jumper wires **M–F**, 20 cm, 40-pack              | 1   | EDGELEC / generic 2.54 mm M–F, 20 cm                                                 | Perfboard/breadboard ↔ Pi GPIO or breakout                                                                                           | ~$5    |
| Mini solderless breadboard (400-tie)                     | 1   | **BB400** (generic 400-point)                                                        | Prototype the star fan-out node + pulldowns before soldering                                                                         | ~$3    |
| Resistor **220 Ω**, 1/4 W, 1 % metal-film                | 8   | **Yageo MFR-25FBF52-220R** (4 branches + 4 spare)                                    | Series safety resistor on each `DO 03` → Pi GPIO 17 branch                                                                           | ~$2    |
| Resistor **10 kΩ**, 1/4 W, 1 % metal-film                | 8   | **Yageo MFR-25FBF52-10K0** (4 pulldowns + 4 spare)                                   | Pull-down GPIO 17 → GND at each Pi (holds LOW when Core off)                                                                          | ~$2    |
| Perfboard / stripboard (5×7 cm FR4)                      | 1   | Generic 5×7 cm 2.54 mm FR4 prototype board                                           | Permanent star-node + series/pulldown resistor mount                                                                                 | ~$2    |
| Heat-shrink tubing assortment (2:1, 2–6 mm)              | 1   | Generic assortment                                                                   | Insulate Dupont → solder joints beyond pure breadboard                                                                               | ~$5    |
| **USB logic analyzer**, 8-ch 24 MHz                      | 1   | **Cypress CY7C68013A (FX2LP)** Saleae-clone — alt: genuine Saleae Logic 8            | **Mandatory** idle-pulse check on `DO 03` (pin 22) in Gated mode — DMM averaging hides ~0.5 s pulses. Also captures Pi → DI markers  | $10–15 |
| (Lab-supplied) Digital multimeter, DC volts              | 1   | any                                                                                  | Continuity + pin-22 voltage check before powering the Pi                                                                             | $0–20  |

**Sub-total (without DMM):** ~$45.

### Hold-until-answers

| Item | Trigger to buy |
|------|----------------|
| DB25 **M–F extension cable** (1–2 m) | Core not colocated with the Pi rack — extend reach without dangling the breakout off the connector |
| Pi 5 + PoE HAT (nodes 3–4) | Separate scale-up purchase, not in this wiring BOM |

### Removed / not needed

- ~~74HCT244 octal buffer / DIP-20 socket~~ — **dropped 2026-06-05.** KC round-3b: Gen-1 DB25 driver = SN74LVC2G17 (~20 mA) ≫ high-Z Pi GPIO input load → single `DO 03` star-wires to ≥4 (≥8) Pi inputs directly, no buffer. ([[neuronexus-inquiry-email#Reply — round 3b received 2026-06-05 (KC Kong)|round-3b reply]])
- ~~BNC Breakout Board from NeuroNexus~~ — Allego software toggle exposes the DB25 DIs / `DO 03` directly; no physical breakout required.
- ~~Voltage divider (1 kΩ + 2 kΩ)~~ — `DO 03` (pin 22) is **3.3 V fixed** (confirmed by KC + Jeffrey 2026-05-28); direct wire from DB25 → Pi GPIO 17 is safe. Only discrete 220 Ω (series) + 10 kΩ (pulldown) bought now — no divider pair.
- ~~Fixed-value 1 % divider resistor pair~~ — same reason; voltage Q closed at 3.3 V.

## Wiring Diagram

> [!check] Diagrams redrawn 2026-06-05 — gate = `DO 03` (pin 22), no divider, star fan-out
> Settled across the vendor thread: **`DAQ_ON` (pin 13) = STREAMING only** (idle ~0.5s pulses → false edges, [[neuronexus-inquiry-email#Reply — round 2 received 2026-05-28 (Jeffrey)|round-2]]); recording gate = **`DO 03` (DB25 pin 22)** in **"Gated"** mode + **"BNC Breakout Board"** slider ON. Output **3.3 V fixed** ([[neuronexus-inquiry-email#Reply — round 3 received 2026-05-28 (Jeffrey)|round-3]]), driver SN74LVC2G17 ~20 mA → direct wire to Pi GPIO, **no divider**, star-fanned to all Pis with no buffer ([[neuronexus-inquiry-email#Reply — round 3b received 2026-06-05 (KC Kong)|round-3b]]). Diagrams below reflect this. Optionally keep `DAQ_ON` (pin 13) / front `DIGITAL OUT 1` (DO-01) as a *streaming* flag.

> [!check] Pin numbers + voltage verified against the manual + vendor
> DB25 pins (manual + Jeffrey confirm): `DI 03`=**Pin 2**, `DAQ_ON`=Pin 13, `DO 03`=**Pin 22** (★ recording gate), `GND`=Pin 14, `SAMPLE CLK`=Pin 25. Voltage on **`DO 03`–`DO 08` + `DAQ_ON` = 3.3 V fixed** (KC + Jeffrey 2026-05-28). Only `DO 01`/`DO 02` (BNC) switch 3.3 ↔ 5 V. **Direct wire DB25 → Pi GPIO** (3.3 V = Pi GPIO ceiling).

### Wire 1: `DO 03` recording gate → Pi GPIO (direct, no divider, star fan-out)

`DO 03` (pin 22) is 3.3 V fixed → wire straight to the Pi's 3.3 V GPIO input. One gate fans out to every Pi from a star node (220 Ω series per branch for safety, 10 kΩ pull-down at each Pi to hold LOW when the Core is off). No divider, no buffer.

```
XDAQ DB25                 star node (perfboard)        Pi 5 GPIO Headers
Pin 22 (DO 03, 3.3V) ──●──── 220Ω ──────────────────── Pin 11 (GPIO 17) — Pi1
   "Gated" mode         ●──── 220Ω ──────────────────── Pin 11 (GPIO 17) — Pi2
   BNC Breakout ON      ●──── 220Ω ──────────────────── Pin 11 (GPIO 17) — Pi3
                        ●──── 220Ω ──────────────────── Pin 11 (GPIO 17) — Pi4
                                    each branch: 10kΩ pulldown GPIO17→GND at the Pi

Pin 14 (GND) ──── star-ground hub ──┬───────────────── Pin 14 (GND) — Pi1  (home-run)
                                    ├───────────────── Pin 14 (GND) — Pi2
                                    ├───────────────── Pin 14 (GND) — Pi3
                                    └───────────────── Pin 14 (GND) — Pi4
                                    (no Pi-to-Pi GND ties — star, not daisy-chain)
```

### Wire 2: Pi GPIO → XDAQ DIN frame-sync return (one DI per Pi, direct)

Pi outputs 3.3 V; XDAQ DIs accept 2.2–5.5 V (register down to 1.7 V) → direct wire, no shift. One dedicated DI per Pi; all appear in Allego with "BNC Breakout Board" ON.

```
Pi 5 GPIO Header              XDAQ DB25
Pin 13 (GPIO 27) — Pi1 ─────── Pin 2  (DI 03)
Pin 13 (GPIO 27) — Pi2 ─────── Pin 15 (DI 04)
Pin 13 (GPIO 27) — Pi3 ─────── Pin 3  (DI 05)
Pin 13 (GPIO 27) — Pi4 ─────── Pin 16 (DI 06)

(GND already shared via the Wire 1 star-ground at pin 14)
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
 ► GATE   GPIO 17 11│ ●  ●  │ 12  GPIO 18   (DO 03 pin 22 in, via 220Ω)
 ► FRAME  GPIO 27 13│ ●  ●  │ 14  GND  ◄── Star-ground home-run to DB25 pin 14
          GPIO 22 15│ ●  ●  │ 16  GPIO 23
            3.3V  17│ ●  ●  │ 18  GPIO 24
                   ... (remaining pins not used)
                    └────────────────────────┘

► = pins used by hardware sync
```

## Multi-Pi fan-out and star grounding

> [!check] Confirmed 2026-06-05 by KC Kong ([[neuronexus-inquiry-email#Reply — round 3b received 2026-06-05 (KC Kong)|round-3b reply]])
> Gen-1 XDAQ Core DB25 output driver = TI **SN74LVC2G17**, sources **~20 mA**. Recommended grounding = **star scheme with the XDAQ Core as the center**, fanning in each device's GND.

### Gate fan-out — direct star wiring, no buffer

The single recording-gate output `DO 03` (pin 22) drives **all** Pi GPIO inputs in parallel. No 74HCT244 buffer is needed:

- Pi 5 GPIO inputs are high-impedance CMOS (leakage ~µA). With a 10 kΩ pull-down per line each Pi draws ~0.33 mA; **8 Pis ≈ 2.6 mA worst-case** — well under the SN74LVC2G17's ~20 mA.
- Put a **220 Ω series resistor** on each branch (near the Pi) for short-circuit/ESD safety; it does not meaningfully load the gate.
- Optional **10 kΩ pull-down** at each Pi GPIO holds the line LOW when the Core is off / between sessions (avoids a floating input reading false edges).

```
XDAQ DB25 pin 22 (DO 03, 3.3 V gate)
        │
        ●──220Ω──► Pi1 GPIO 17   (+10kΩ pulldown to GND)
        │
        ●──220Ω──► Pi2 GPIO 17   (+10kΩ pulldown to GND)
        │
        ●──220Ω──► Pi3 GPIO 17   (+10kΩ pulldown to GND)
        │
        ●──220Ω──► Pi4 GPIO 17   (+10kΩ pulldown to GND)
   (star node on perfboard near the Core)
```

### Grounding — star scheme (Core = hub)

KC: *"use the XDAQ CORE as the center of the Ground and fan in the other devices' GND following the star grounding scheme."*

- **XDAQ Core `GND` (DB25 pin 14) = single common reference.** Run **one dedicated GND wire from each Pi back to pin 14** (home-run / star), meeting only at the Core.
- **Do NOT daisy-chain** Pi-to-Pi grounds, and do not tie the Pi grounds to each other anywhere except at the Core hub — that creates ground loops.
- Keep the gate-signal return and the frame-sync DI returns referenced to this same pin-14 star point.
- PoE supplies: each Pi's PoE GND is isolated through its HAT; the digital-sync GND star is a separate low-current reference and should be the only galvanic tie between the Core and the Pi GPIO domain.

> [!note] Scale note
> Fan-out (1 gate → N Pis) and the N return DIs (`DI 03`–`DI 08`, pins 2/15/3/16/…) both terminate at the same DB25. Six DB25 DIs support up to 6 Pi return lines; beyond that, use the EXP ports / breakout for more channels.

## Pre-Power Validation (Multimeter)

Before powering on, verify with a continuity test:

1. **Wire 1 path (per Pi):** DB25 Pin 22 (`DO 03`) → through 220 Ω → to Pi GPIO 17 (Pin 11). Should show ~220 Ω resistance. Repeat for each Pi branch off the star node.
2. **Pull-down:** Pi GPIO 17 → 10 kΩ → Pi GND. Should show ~10 kΩ.
3. **Wire 2 path:** Pi GPIO 27 (Pin 13) → to its DB25 DI (Pi1=Pin 2, Pi2=15, Pi3=3, Pi4=16). Should show near-zero resistance (direct wire).
4. **Ground path:** DB25 Pin 14 → each Pi GND (Pin 14), home-run. Should show near-zero resistance. Confirm Pi grounds meet **only** at the Core (no Pi-to-Pi continuity that bypasses pin 14).
5. **No shorts:** Check that GPIO 17 and GPIO 27 are NOT shorted to each other, to 3.3V, or to 5V.

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

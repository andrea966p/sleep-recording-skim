---
tags: [infrastructure, hardware-sync, reference, justification, bom]
created: 2026-05-25
status: complete
---

# XDAQ ↔ Raspberry Pi Sync — Design Justification & References

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The evidence behind every purchase and every wiring choice in the hardware-sync plan. Each part we buy and each pin we connect is traced to a manufacturer datasheet, an official spec, or a peer-reviewed paper.
>
> **Why it exists.** So the plan can be presented to the professor (and later a methods section) without any "trust me" choices. Every decision has a citation.
>
> **How to read this page.** Two reference layers: (B) *why each part* in the bill of materials — datasheets; (C) *why each pin and resistor value* — manufacturer electrical specs. The *scientific* "why TTL at all" case lives in its own page — see (A) below. The "Open items" section lists the two things that must be confirmed before money is spent. Big-picture context: [[01-infrastructure/system-overview|System Overview]].

> [!quote] Paper-ready
> Component selection and wiring for the XDAQ-to-Raspberry-Pi synchronization link were derived directly from the NeuroNexus XDAQ digital-I/O electrical specification (logic-high 3.6 V output, 2.2–5.5 V input) and the Raspberry Pi RP1 GPIO 3.3 V logic specification; a 1 kΩ/2 kΩ resistive divider reconciles the 3.6 V source with the 3.3 V-maximum GPIO input.

> [!warning] Two items must be confirmed before purchasing — see [[#Open Items — confirm before purchase|Open Items]] below
> 1. The exact **DB25 pin numbers** are not printed in the XDAQ User Manual (only signal *labels* are). Confirm against the KONTEX DB25 breakout pinout.
> 2. Decide whether to keep the **DIY resistor divider** or buy a logic-level-shifter board.

---

## A. Why hardware TTL sync at all (scientific literature)

The scientific case — that a TTL pulse over digital I/O, **not** software polling, is the field-standard method for video↔electrophysiology sync — is made in full in **[[01-infrastructure/hardware-sync/literature-review|Literature Review]]** (7 annotated papers: Syntalos, SyncGenie, Nakamura, Hasegawa, LSL review, OpenVEEG, Rodriguez-Santiago). **That page is the single source for the paper citations.** This page covers only the *engineering* references (parts and electrical values) in §B and §C below.

> [!note] Before any of those papers go into a manuscript bibliography, re-verify each DOI resolves — they were transcribed, not fetched.

---

## B. Bill of Materials — why each part

| Part | Why this part | Reference |
|------|---------------|-----------|
| **DB25 male screw-terminal breakout** | XDAQ exposes digital I/O on a DB25 connector; a breakout gives solderless access to individual pins | XDAQ User Manual §3.4.8 "Each XDAQ … includes several IO ports within the DB25 connector" (p.18) [^xdaq] |
| **1 kΩ + 2 kΩ resistors (¼ W)** | Form a voltage divider that drops the 3.6 V DAQ_ON output to ~2.4 V, safely under the Pi's 3.3 V GPIO limit | Divider math (§C) + XDAQ output 3.6 V [^xdaq] + Pi GPIO 3.3 V max [^rpi-gpio] |
| **Dupont F-F jumper wires** | Connect breakout terminals to the Pi 40-pin header pins | Standard 0.1″ (2.54 mm) header — Pi 5 mechanical spec [^rpi-mech] |
| **Small breadboard** (optional) | Mounts the two divider resistors without soldering | — (convenience) |
| **KONTEX DB25 BNC Breakout Board** (optional, professional) | Vendor's own board breaks the same DB25 out to labelled BNC jacks (DI 3–8, DO 3–8, SAMPLE CLK OUT, MARK OUT, GND) — cleaner than DIY | XDAQ User Manual §3.4.8, panel photo p.18 [^xdaq]; product page [^kontex-bnc] |
| **Raspberry Pi Pico** (only if jitter measured too high) | Dedicated TTL pulse generator, the exact mitigation Syntalos used | Klumpp et al. 2025 (ref A-1) |

---

## C. Wiring & electrical decisions — why each pin and value

### C.1 XDAQ digital output (DAQ_ON) is 3.6 V — **confirmed**
> XDAQ User Manual §3.4.2, p.15, verbatim:
> - "+ 24 Digital Inputs: Logic high 2.2 - 5.5V"
> - "+ 24 Digital Outputs: Logic high 3.6V"

This is the manufacturer's own number. It is why a level adjustment is mandatory in the DAQ_ON → Pi direction. [^xdaq]

### C.2 Pi 5 GPIO is 3.3 V logic and **not** 5 V tolerant — **confirmed**
Official Raspberry Pi guidance: *"A GPIO pin should never be connected to a voltage source greater than 3.3 V or less than 0 V … prompt damage to the chip may occur."* The GPIO pins are CMOS 3.3 V with **no over-voltage protection**. [^rpi-gpio]

> [!warning] Correcting a common misconception
> Some secondary web sources claim the Pi 5 / RP1 GPIO is "5 V tolerant." The official documentation does **not** support this — do not rely on it. Treat 3.3 V as the hard ceiling. This is exactly why the divider exists.

### C.3 The 1 kΩ / 2 kΩ divider — value justification
Standard resistive voltage divider (Ohm's law / Art of Electronics §1.2.3 [^aoe]):

```
V_out = V_in × R2 / (R1 + R2) = 3.6 V × 2kΩ / (1kΩ + 2kΩ) = 2.4 V
```

- 2.4 V **>** Pi V_IH high-threshold (~1.8 V on 3.3 V CMOS) → reads as logic HIGH ✓ [^rpi-gpio]
- 2.4 V **<** 3.3 V GPIO maximum → safe ✓ [^rpi-gpio]
- Divider draws 3.6 V / 3 kΩ = 1.2 mA from DAQ_ON — negligible for a digital output rated to drive a 5 V load.

### C.4 Pi → XDAQ DIN direction needs **no** level shift — **confirmed**
XDAQ digital input logic-high range is **2.2–5.5 V** (§C.1). The Pi outputs 3.3 V, which sits inside that range → direct wire, no divider. [^xdaq] [^rpi-gpio]

### C.5 Signals used (DAQ_ON, DI/DO, SAMPLE CLK, GND) — **confirmed present**
The XDAQ DB Adapter / BNC breakout panel (User Manual p.18) is labelled with `DI 3…DI 8`, `DO 3…DO 8`, `SAMPLE CLK OUT`, `MARK OUT`, and `GND`. KONTEX confirms `DAQ_ON` is "high whenever XDAQ acquisition is running." [^xdaq] [^kontex]

### C.6 Software: `gpiod` edge detection on `gpiochip4`
- Edge-interrupt reads (not polling) via **libgpiod** — the modern Linux GPIO userspace API that replaced sysfs. [^libgpiod]
- Pi 5 routes the 40-pin header through the **RP1** I/O controller, which enumerates as `gpiochip4` (older Pis: `gpiochip0`). [^rp1]

---

## Open Items — confirm before purchase

> [!danger] 1. Exact DB25 pin numbers are NOT verified
> The [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]] assigns specific pins — **Pin 13 = DAQ_ON, Pin 2 = DI 03, Pin 14 = GND, Pin 25 = Sample_CLK**. The XDAQ User Manual confirms these *signals exist* but prints only BNC **labels**, not DB25 **pin numbers (1–25)**. Confirm the numbering against the KONTEX DB25 pinout (`docs.kontex.io/System-Adpt/SAdpt-XDAQ-BNC/` [^kontex-docs]) or by emailing NeuroNexus support before wiring. A wrong pin number = no signal or possible damage.

> [!warning] 2. DIY divider vs. level-shifter board
> The manual states DOUT = 3.6 V (fixed). The KONTEX website separately claims the output is "configurable to 3.3 or 5 V." [^kontex] If it can be set to **3.3 V**, the divider becomes unnecessary (direct wire). Confirm the firmware/config option. If unsure, the divider is the safe default and works either way (3.3 V → 2.2 V, still a valid HIGH).

---

## Citations

[^xdaq]: **NeuroNexus, XDAQ™ User Manual**, March 2024. Digital I/O voltages: §3.4.2 (IO Expander), p.15. DB25 breakout signal labels: §3.4.8, p.18. <https://solutions.neuronexus.com/hubfs/NNX_XDAQ_USER%20MANUAL_202403%20(1).pdf>
[^kontex]: **KONTEX, XDAQ™ product page.** DAQ_ON behaviour and digital-output voltage configurability. <https://www.kontex.io/xdaq>
[^kontex-bnc]: **KONTEX, XDAQ™ DB25 BNC Breakout Board.** <https://www.kontex.io/product/xdaq-db25-bnc-breakout-board>
[^kontex-docs]: **KONTEX docs, XDAQ-BNC system adapter** (DB25 pinout — access was blocked at time of writing; open in browser). <https://docs.kontex.io/System-Adpt/SAdpt-XDAQ-BNC/>
[^rpi-gpio]: **Raspberry Pi — GPIO documentation / community guidance:** GPIO is CMOS 3.3 V, not 5 V tolerant, no over-voltage protection; never exceed 3.3 V on an input. <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html>
[^rp1]: **Raspberry Pi RP1 Peripherals Datasheet** (the I/O controller on Pi 5; GPIO bank operates at 3.3 V). <https://datasheets.raspberrypi.com/rp1/rp1-peripherals.pdf>
[^rpi-mech]: **Raspberry Pi 5** 40-pin header = standard 2.54 mm pitch. <https://www.raspberrypi.com/documentation/computers/raspberry-pi.html>
[^libgpiod]: **libgpiod** — Linux kernel GPIO character-device userspace library (replaces deprecated sysfs). <https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git/about/>
[^aoe]: Horowitz & Hill, *The Art of Electronics*, 3rd ed., §1.2.3 (voltage divider) — for the divider derivation.

## Related
- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]]
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]] (the BOM and pinout this page justifies)
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]] (full paper annotations)
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]

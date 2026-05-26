---
tags:
  - infrastructure
  - hardware-sync
  - vendor
  - email
  - draft
created: '2026-05-26T00:00:00.000Z'
status: draft
---

# NeuroNexus / KONTEX Inquiry — XDAQ Core2 Digital I/O

> [!abstract] TL;DR
> Draft email to send NeuroNexus (or KONTEX) **before any purchase**, to close the open items in [[01-infrastructure/hardware-sync/references-and-justification|Design Justification]]. Goal: confirm how our **XDAQ Core2** exposes digital I/O so we can wire `DAQ_ON` → Raspberry Pi without buying the optional BNC Breakout Board.
>
> Fill the `[bracketed]` fields (model serial, contact name) before sending. From: `andrea96p@kaist.ac.kr`.

> [!warning] Why we ask
> Manual prints signal **labels** only, not DB25 **pin numbers**, and the website/manual disagree on output voltage. We need vendor confirmation, not a guess, before wiring 3.6 V into a 3.3 V Pi GPIO.

---

## Items NeuroNexus must assess

1. **Digital-I/O connector on Core2** — onboard DB25 vs. System Adapter required.
2. **DB25 pin numbers (1–25)** for `DAQ_ON`, `DI 03`, `GND`, `SAMPLE CLK OUT`.
3. **Digital-output logic-high voltage** — 3.6 V fixed (manual §3.4.2) vs. "configurable 3.3/5 V" (website). If configurable, how.
4. **`DAQ_ON` behavior** — confirm HIGH for full duration of acquisition, one edge per session.
5. **If adapter needed** — which plain DB25/screw-terminal adapter (so we skip the pricier BNC Breakout Board).

---

## Email draft

> **To:** NeuroNexus support / KONTEX
> **From:** andrea96p@kaist.ac.kr
> **Subject:** XDAQ Core2 — digital I/O DB25 pinout & output voltage confirmation

Hello,

We operate an **XDAQ Core2** [serial / order ref: `[FILL IN]`] in a neuroscience sleep-research lab. We are adding a hardware synchronization link between the XDAQ digital I/O and a Raspberry Pi 5 (TTL `DAQ_ON` pulse marking acquisition start/stop). Before wiring, we need to confirm a few electrical and mechanical details that the User Manual states only as signal labels.

Could you confirm the following for the **Core2** specifically:

1. **Digital-I/O access.** Does the Core2 expose the digital I/O on a DB25 connector directly on the unit, or is a separate System Adapter / DB Adapter board required to reach it? If an adapter is required, which part do you recommend for plain pin access (screw-terminal), as opposed to the BNC Breakout Board?

2. **DB25 pin numbers (1–25).** The User Manual (§3.4.8, p.18) lists the signal labels but not the physical DB25 pin numbers. Please confirm the pin number for each of:
   - `DAQ_ON`
   - `DI 03` (a digital input we will drive from the Pi)
   - `GND`
   - `SAMPLE CLK OUT`

3. **Digital-output logic-high voltage.** Manual §3.4.2 states digital outputs are logic-high **3.6 V**, but the product website mentions the output is "configurable to 3.3 or 5 V." Which applies to the Core2, and if it is configurable, how do we set it (firmware/Radiens setting)? We need this to decide whether a 3.3 V level shift is required on the Pi side.

4. **`DAQ_ON` signal behavior.** Please confirm `DAQ_ON` is asserted HIGH for the entire duration that acquisition is running (one rising edge at start, one falling edge at stop), and that it is a clean TTL-level output suitable for driving a GPIO input.

5. **Input logic range.** Please confirm the digital-input logic-high range (we read 2.2–5.5 V); the Pi drives 3.3 V into `DI 03` and we want to confirm that is a valid HIGH with no level shift.

For context: we plan a 1 kΩ / 2 kΩ resistive divider on the `DAQ_ON` → Pi line to drop 3.6 V to ~2.4 V (safely under the Pi's 3.3 V GPIO ceiling). If the output can be set to 3.3 V, the divider becomes unnecessary — hence question 3.

Thank you. A datasheet or pinout drawing for the Core2 digital I/O would also be very helpful.

Best regards,
Andrea
[lab / affiliation]
andrea96p@kaist.ac.kr

---

## After reply — update these

- [[01-infrastructure/hardware-sync/references-and-justification|Design Justification]] — close both Open Items (pin numbers, divider-vs-shifter).
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]] — correct DB25 pin numbers if they differ; drop BNC board line if confirmed unneeded; drop divider if output set to 3.3 V.

## Related
- [[01-infrastructure/hardware-sync/references-and-justification|Design Justification & References]] (source of these open items)
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]]
- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]]

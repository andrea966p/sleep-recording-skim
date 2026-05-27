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

---

## Reply received — 2026-05-27

> [!info] Vendor replied by interleaving answers into the original email. Logged verbatim-summary below.
> **Update 2026-05-27 (later):** cross-checked against the KONTEX Core2 manual — see [[xdaq-core2-manual-reference|XDAQ Core2 Manual Reference]] (authoritative pinout + specs, with figures archived). The manual **corrects the vendor email on Q2** (DI 03 = Pin 2, not 22) and resolves Q3/Q4 below.

| # | Question | Status | Vendor answer |
|---|----------|--------|---------------|
| 1 | Connector access / adapter | ✅ confirmed | DB25 directly accessible (no mandatory adapter); OR use Kontex breakout boards. DB25 = **6 DI + 6 DO**. More channels → breakout via **EXP1/EXP2 µHDMI** ports on rear. Analog GPIO → **XDAQ GPIO Expander**. Pinout: <https://docs.kontex.io/XDAQ/CORE2/#xdaqtm-db25-io-connector-pinout> |
| 2 | DB25 pin numbers | ✅ resolved via manual | Jeffrey gave `DAQ_ON`=13, `GND`=14, `SAMPLE CLK`=25 (all correct), and `DI 03`=22 — **but 22 is `DO 03`; he transposed DI/DO.** [[xdaq-core2-manual-reference\|Manual]] is authoritative: **`DI 03` = Pin 2.** Vault was already correct. |
| 3 | Output 3.6 V vs configurable 3.3/5 V | ⚠️ resolved via manual (await dev team on CLI) | Vendor: not in Radiens UI; maybe CLI. **Manual:** DB25 outputs (DO-03…08) = **3.3 V fixed**; the configurable 3.3/5 V applies to the **BNC** DO-01/DO-02, not DB25. So "3.6 V" was wrong for Core2 → divider likely unneeded (measure pin 13 first). See [[xdaq-core2-manual-reference\|Manual]]. |
| 4 | `DAQ_ON` behavior | ⚠️ resolved via manual (confirm level/scope) | Vendor deferred to Kontex (suspected front-panel DO1/DO2). **Manual:** `DAQ ON` is on the **DB25 (pin 13)** — "logic high at onset of a recording session" — directly accessible, so the Pin-13 design holds. Confirm level-vs-pulse + exact voltage on a scope at validation. |
| 5 | DIN logic-high range / 3.3 V valid | ✅ confirmed | "I can register a pulse on the DIs with a voltage as low as **1.7 V** with no level shifts." → Pi 3.3 V → DIN is fine, no shifter. |

### Action items from this reply

> Pinout + specs now captured authoritatively in [[xdaq-core2-manual-reference|XDAQ Core2 Manual Reference]] (figures archived). Remaining items:

- [x] **Q2 — pins verified against manual.** `DI 03 = Pin 2` (vendor's "Pin 22" was the `DO 03` pin — transposed). `DAQ_ON`=13, `GND`=14, `SAMPLE CLK`=25 all correct. Vault pin values already match — **no pin change needed** in [[wiring-guide|Wiring Guide]] / [[overview|Overview]] / [[radiens-api-reference|API ref]] / [[02-procedures/hardware-sync-setup|Setup Procedure]].
- [ ] **Q3 + divider decision** — manual says DB25 output = **3.3 V** (not 3.6 V). Divider likely unnecessary. Before dropping it: measure `DAQ_ON` (pin 13) voltage during acquisition (DAQ_ON's own level isn't tabulated). Then update [[references-and-justification|Design Justification]] §C + BOM. Still awaiting dev team on whether the BNC voltage is CLI-settable (not relevant to DB25).
- [ ] **Q4 — confirm `DAQ_ON` is level (not a pulse)** on a scope at wiring validation. Manual confirms it's on DB25 pin 13 ("logic high at onset of a recording session"), so the Pin-13 design stands — but verify it stays HIGH for the whole session and drops at stop.
- [ ] **Q1 correction** — update [[radiens-api-reference|API ref]] "7 channels" DI/DO → DB25 exposes **6 DI + 6 DO** (onboard total = 7 DI incl. BNC); EXP ports = **MicroHDMI**.
- [ ] Update [[references-and-justification|Design Justification]] Open Items: #1 (pins) **CLOSED** (verified, DI 03 = Pin 2); #2 (divider) — reframed around the 3.3 V finding above. Replace citation link `[^kontex-docs]` with [[xdaq-core2-manual-reference|the Core2 reference]].

---

## Reply draft — round 2 (2026-05-27)

> [!abstract] What this round must assess
> After Jeffrey's reply + reading the [[xdaq-core2-manual-reference|Core2 manual]], three things still need vendor confirmation, plus a new ask:
> 1. **Pin correction** — manual figure shows `DI 03 = Pin 2` (Jeffrey's reply said Pin 22, which is `DO 03`). Confirm.
> 2. **`DAQ_ON` voltage** — manual gives DB25 outputs as 3.3 V but does not list `DAQ_ON`'s own level. Confirm pin-13 voltage (decides level-shift). *We will also measure it — see [[wiring-guide#⭐ Pin 13 (DAQ_ON) Voltage Check — run this BEFORE building/buying the divider|Pin 13 Voltage Check]].*
> 3. **`DAQ_ON` timing** — level for the whole recording session vs one-shot pulse; tracks *recording* vs *streaming*.
> 4. **NEW: XDAQ Core2 hardware drivers on Ubuntu 24.04 LTS.** Radiens suite (Allego+Curate+Videre) + `radiens` Python pkg already installed on the Ubuntu 24.04 acquisition host; remaining gap is the *device-level* connectivity (USB/Thunderbolt drivers, udev rules, kernel) for the Core2 itself.

> **To:** Jeffrey @ NeuroNexus / KONTEX support
> **From:** andrea96p@kaist.ac.kr
> **Subject:** Re: XDAQ Core2 — digital I/O DB25 pinout & output voltage confirmation

Hi Jeffrey,

Thank you for the detailed reply and the Core2 documentation link — the DB25 pinout figure there was exactly what we needed. It confirms `DAQ_ON` = pin 13, `GND` = pin 14, and `SAMPLE CLK` = pin 25, matching your answer.

A few follow-ups to fully close this out:

1. **DI 03 pin number.** Your reply listed `DI 03` at pin 22, but the Core2 pinout figure shows pin 22 as `DO 03` and `DI 03` at **pin 2**. Could you confirm `DI 03` = **pin 2** on the Core2? This is the input we'll drive from the Raspberry Pi, so we want to be certain before wiring.

2. **`DAQ_ON` output voltage (pin 13).** The Core2 spec lists the DB25 digital outputs (DO-03…DO-08) as 3.3 V logic-high, with the software-configurable 3.3/5 V option applying only to the BNC outputs (DO-01/DO-02). The spec doesn't separately state the `DAQ_ON` pin's logic-high voltage. Is `DAQ_ON` (pin 13) also 3.3 V? We need this to decide whether any level adjustment is required driving a 3.3 V Raspberry Pi GPIO input. (We also plan to measure pin 13 directly with a multimeter during a recording session to confirm.)

3. **`DAQ_ON` timing/behavior.** The manual states `DAQ_ON` is "logic high at onset of a recording session." Could you confirm whether it stays **HIGH for the entire duration of the recording** (one rising edge at start, one falling edge at stop), or is a brief pulse at onset only? And does it track **recording** specifically, as opposed to streaming/acquisition? (You mentioned Radiens commonly uses front-panel DO1/DO2 for streaming/recording sync — we'd like to understand how the DB25 `DAQ_ON` relates to those.)

4. **XDAQ Core2 hardware drivers on Ubuntu 24.04 LTS.** Our acquisition host runs **Ubuntu 24.04 LTS**, and we already have the Radiens suite (Allego + Curate + Videre) and the `radiens` Python package installed and running there. What remains is the device-level connection to the Core2 hardware on Linux. Could you confirm, for Ubuntu 24.04:
   - any required device drivers or kernel modules to connect the Core2 (over USB and/or Thunderbolt), and the supported kernel versions;
   - any `udev` rules, group membership, or Thunderbolt-authorization steps needed for Allego to detect and stream from the Core2 without running as root;
   - any known Linux-specific limitations vs. Windows for the Core2 (e.g. Thunderbolt throughput, NP-mode support).

A Core2 datasheet PDF, if available, would also be appreciated.

Thanks again for the help.

Best regards,
Andrea
andrea96p@kaist.ac.kr

---

> [!todo] Before sending
> - Confirmed 2026-05-27: Radiens runs on the Ubuntu 24.04 box; suite + Python pkg already installed. Item 4 reframed to device-level driver/connectivity only.
> - Fill the Core2 serial / order ref in the first round's draft if the vendor asks to identify the unit.

> [!check] Package name — verified 2026-05-27
> Installed package is **`radiens` v4.0.0** in `/opt/neurosurveillance/venv` (`from radiens import AllegoClient` works). The brochure was right; [[radiens-api-reference|Radiens API Reference]] had it wrong as `radiens-core` — now corrected. Docs: <https://neuronexus.github.io/intro.html>, <https://nnx.mcoutput.com/1376106/Content/Home-Radiens.htm>.

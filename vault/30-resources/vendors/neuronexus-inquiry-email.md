---
type: reference
area: video-nvr
status: done
status-note: "draft"
tags:
  - infrastructure
  - hardware-sync
  - vendor
  - email
  - draft
created: 2026-05-26
---

# NeuroNexus / KONTEX Inquiry — XDAQ Core2 Digital I/O

> [!warning] Updated 2026-10-22: this thread was written for an XDAQ Core2 (Thunderbolt). Our unit is a Gen-1 XDAQ Core (Opal Kelly USB); KC Kong confirmed the Gen-1 DB25 pinout in round 3b (2026-06-05). [[xdaq-core-gen1-ubuntu-driver]]

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[_rig-expansion-hub]]** (decision, vendor correspondence, wiring, open items).

> [!abstract] TL;DR
> Draft email to send NeuroNexus (or KONTEX) **before any purchase**, to close the open items in [[references-and-justification|Design Justification]]. Goal: confirm how our **XDAQ Core2** exposes digital I/O so we can wire `DAQ_ON` → Raspberry Pi without buying the optional BNC Breakout Board.
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

- [[references-and-justification|Design Justification]] — close both Open Items (pin numbers, divider-vs-shifter).
- [[wiring-guide|Wiring Guide]] — correct DB25 pin numbers if they differ; drop BNC board line if confirmed unneeded; drop divider if output set to 3.3 V.

## Related
- [[references-and-justification|Design Justification & References]] (source of these open items)
- [[wiring-guide|Wiring Guide]]
- [[overview|Hardware Sync Overview]]

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

- [x] **Q2 — pins verified against manual.** `DI 03 = Pin 2` (vendor's "Pin 22" was the `DO 03` pin — transposed). `DAQ_ON`=13, `GND`=14, `SAMPLE CLK`=25 all correct. Vault pin values already match — **no pin change needed** in [[wiring-guide|Wiring Guide]] / [[overview|Overview]] / [[radiens-api-reference|API ref]] / [[hardware-sync-setup|Setup Procedure]].
- [ ] **Q3 + divider decision** — manual says DB25 output = **3.3 V** (not 3.6 V). Divider likely unnecessary. Before dropping it: measure `DAQ_ON` (pin 13) voltage during acquisition (DAQ_ON's own level isn't tabulated). Then update [[references-and-justification|Design Justification]] §C + BOM. Still awaiting dev team on whether the BNC voltage is CLI-settable (not relevant to DB25).
- [ ] **Q4 — confirm `DAQ_ON` is level (not a pulse)** on a scope at wiring validation. Manual confirms it's on DB25 pin 13 ("logic high at onset of a recording session"), so the Pin-13 design stands — but verify it stays HIGH for the whole session and drops at stop.
- [ ] **Q1 correction** — update [[radiens-api-reference|API ref]] "7 channels" DI/DO → DB25 exposes **6 DI + 6 DO** (onboard total = 7 DI incl. BNC); EXP ports = **MicroHDMI**.
- [ ] Update [[references-and-justification|Design Justification]] Open Items: #1 (pins) **CLOSED** (verified, DI 03 = Pin 2); #2 (divider) — reframed around the 3.3 V finding above. Replace citation link `[^kontex-docs]` with [[xdaq-core2-manual-reference|the Core2 reference]].

---

## Reply — round 2 (finalized by Andrea, 2026-05-27)

> [!check] This is Andrea's final wording (greeting, "I clearly missed it", and the closing note are hers). Spelling normalized (equivalent, suite, your). Ready to send.

> [!abstract] What this round must assess
> After Jeffrey's reply + reading the [[xdaq-core2-manual-reference|Core2 manual]] + the [[xdaq-core2-manual-reference#Front & Rear Panel Layout|front/rear panel figure]]:
> 1. **Pin correction** — manual figure shows `DI 03 = Pin 2` (Jeffrey's reply said Pin 22, which is `DO 03`). Confirm.
> 2. **Recording-gate signal.** Jeffrey's DO1 (streaming) / DO2 (recording) front BNCs are an **XDAQ ONE+** feature (`docs.kontex.io/XDAQ/ONE/` — two digital-out BNCs DO-01/DO-02); the **Core2 has only DO-01**. So on the Core2 the recording gate = DB25 `DAQ_ON` (pin 13). Ask: does DAQ_ON track recording like DO2 (level HIGH for the whole session, not a pulse)? Is there a Core2 streaming indicator like DO1 (can front DO-01 be set HIGH while streaming)?
> 3. **Output voltage** — rear IO-SPEC label = D OUT 3.3/5 V. Acknowledge his dev-team CLI follow-up. Need logic-high of pin-13 `DAQ_ON` + front `DIGITAL OUT 1` (decides level-shift into 3.3 V Pi GPIO). *We'll also measure pin 13 — see [[wiring-guide#⭐ Pin 13 (DAQ_ON) Voltage Check — run this BEFORE building/buying the divider|Pin 13 Voltage Check]].*
> 4. **Scale: 4× Pi 5 / 8 cameras.** Fan-out of one gate signal to 4 Pi GPIO inputs (buffer?), 4 separate DB25 DIs (`DI 03`–`06`) for the 4 return lines, grounding for 4 devices on `SYS GND`. **The current vault wiring/overview/gpio-sync docs are single-Pi — this scale is not yet designed in.**
> 5. **XDAQ Core2 hardware drivers on Ubuntu 24.04 LTS.** Radiens suite (Allego+Curate+Videre) + `radiens` Python pkg already installed on the Ubuntu 24.04 acquisition host; remaining gap is *device-level* connectivity (USB/Thunderbolt drivers, udev rules, kernel) for the Core2 itself.

> **To:** Jeffrey @ NeuroNexus / KONTEX support
> **From:** andrea96p@kaist.ac.kr
> **Subject:** Re: XDAQ Core2 — digital I/O DB25 pinout & output voltage confirmation

Dear Jeffrey,

Thank you for the detailed reply and the Core2 documentation link (I clearly missed it) — the DB25 pinout figure there was exactly what we needed. It confirms `DAQ_ON` = pin 13, `GND` = pin 14, and `SAMPLE CLK` = pin 25, matching your answer.

A few follow-ups to fully close this out:

1. **DI 03 pin number.** Your reply listed `DI 03` at pin 22, but the Core2 pinout figure shows pin 22 as `DO 03` and `DI 03` at **pin 2**. Could you confirm `DI 03` = **pin 2** on the Core2? This is the input we'll drive from the Raspberry Pi, so we want to be certain before wiring.

2. **Confirming the recording-gate signal on the Core2.** Thanks for explaining the DO1 (streaming) / DO2 (recording) sync method. We understand the dual digital-output BNCs (DO-01 *and* DO-02) are a feature of the XDAQ **ONE+**; our unit is the **Core2**, which has a single digital-output BNC (DO-01) plus the DB25. So on the Core2 we plan to use DB25 `DAQ_ON` (pin 13) as the recording gate. Could you confirm:
   - Does DB25 `DAQ_ON` (pin 13) track **recording** the same way DO2 does on the ONE+ — i.e. asserted HIGH for the **entire recording session** (one rising edge at start, one falling edge at stop), rather than a brief pulse at onset?
   - Is there a **Core2-accessible streaming indicator** equivalent to DO1 — e.g. can the front-panel `DIGITAL OUT 1` (DO-01) be configured to go HIGH while Radiens is streaming? We'd like to capture both states if possible, but recording is the must-have.

3. **Output logic-high voltage.** Thanks for checking with your dev team on whether the output voltage is CLI-configurable. The Core2 rear-panel IO SPEC label shows digital outputs as 3.3/5 V. To finalize wiring we just need the logic-high voltage of the specific signals we'll use, to decide on any level adjustment for a 3.3 V Raspberry Pi GPIO input:
   - **DB25 `DAQ_ON` (pin 13)** — is it 3.3 V (the DB25 outputs DO-03…08 are listed as 3.3 V, but `DAQ_ON`'s level isn't stated separately)? We'll also measure pin 13 during a recording session.
   - **Front-panel `DIGITAL OUT 1` (BNC)** — if we use it, how do we set it to 3.3 V vs 5 V?

4. **Driving multiple Raspberry Pis (scale).** Our setup will use **at least four Raspberry Pi 5 nodes** (eight cameras total), each needing the recording-gate signal and each returning a frame-sync pulse to the XDAQ. Could you advise:
   - Can a single XDAQ digital output (e.g. DB25 `DAQ_ON`) safely **fan out to four Pi GPIO inputs** in parallel, or do you recommend a buffer/driver between the XDAQ and the Pis?
   - For the return direction, we'd assign **four separate DB25 digital inputs** (e.g. `DI 03`–`DI 06`, pins 2/15/3/16) — one per Pi. Is that the right approach, and are all six DB25 DIs (DI-03…08) independently usable as Radiens trigger/marker channels at the headstage sample rate?
   - Any grounding guidance for tying four external devices to the XDAQ `SYS GND` (pin 14) without ground loops?

5. **XDAQ Core2 hardware drivers on Ubuntu 24.04 LTS.** Our acquisition host runs **Ubuntu 24.04 LTS**, and we already have the Radiens suite and the `radiens` Python package installed and running there. What remains is the device-level connection to the Core2 hardware on Linux. Could you confirm, for Ubuntu 24.04:
   - any required device drivers or kernel modules to connect the Core2 (over USB and/or Thunderbolt), and the supported kernel versions;
   - any `udev` rules, group membership, or Thunderbolt-authorization steps needed for Allego to detect and stream from the Core2 without running as root;
   - any known Linux-specific limitations vs. Windows for the Core2 (e.g. Thunderbolt throughput, NP-mode support).

A Core2 datasheet PDF, if available, would also be appreciated.

As a PhD student working alone on this project approaching graduation, I found myself with many questions, therefore I appreciate your care and patience.

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

---

## Reply — round 2 received 2026-05-28 (Jeffrey)

> [!info] Jeffrey's reply to the round-2 follow-up. Logged verbatim-summary below.
> **Headline:** `DAQ_ON` (pin 13) tracks **streaming, not recording**, and is **dirty when idle** — the true recording gate is **`DO 03` (pin 22) in "Gated" mode** with the "BNC Breakout Board" slider toggled on. This changes Wire 1. See [[wiring-guide|Wiring Guide]] / [[overview|Overview]] 2026-05-28 callouts.

| # | Question | Status | Jeffrey's answer |
|---|----------|--------|-------------------|
| 1 | `DI 03` = pin 2? | ✅ **confirmed** | "Yes — DI 03 is 2, whereas DO 03 is 22." Vault was right all along. |
| 2a | Does `DAQ_ON` (pin 13) track recording (level HIGH whole session)? | ⚠️ **No — tracks STREAMING** | Tested pin 13: goes logic-HIGH when DAQ is **streaming** data (both Allego and XDAQ-RHX) — behaves "almost the same as DO 01" (both HIGH while streaming). **Caveat:** in Allego, `DAQ_ON` shows **short pulses every ~0.5s when streaming is OFF** (Allego constantly scans headstage ports/GPIOs while idle). DAQ_ON "wasn't on the development radar" — Andrea may be first customer to ask. |
| 2b | Core2 streaming/recording indicator? | ✅ **recording gate found = DO 03** | No DO 02 on Core2 (only AIO + ONE+ have it — confirmed Jeffrey's earlier mistake). **But** the DO 02 "recording status" function **falls to `DO 03` (pin 22)** when you toggle the **"BNC Breakout Board"** slider (top of System tab) **and** set Digital Out Control to **"Gated"** mode → DO 03 then reports **"Recording status"** (~15–20s to populate). Lets you sync recording status to any device on that pin. |
| 3 | Output logic-high voltage (DAQ_ON / front DO-01) | ⏳ **pending manufacturer** | DAQ_ON voltage: unknown, **asking manufacturer** — assumes in line with the other DOs (i.e. 3.3 V) per the doc wording; will report back. Allego currently has **no option** to change DO voltage 3.3 V → 5 V. |
| 4a | Multiple Pis on discrete DB25 DIs? | ✅ **yes (with toggle)** | Radiens can record + synchronize pulses received on **multiple inputs** alongside recorded neural data. To **show the extra GPIOs** in Allego you must toggle the **"BNC Breakout Board"** option (same slider as 2b). Channels appear in both **System** and **Monitor** tabs, synced + stored alongside neural channels. |
| 4b | Fan-out buffer + grounding for 4 Pis | ➡️ **referred to Kontex** | Deferred to **KC Kong `KC@kontex.io`** (Kontex design/dev). |
| 5 | Ubuntu 24.04 Core2 drivers / udev / Thunderbolt | ➡️ **referred to Kontex** | Deferred to **KC Kong `KC@kontex.io`**. |

### Action items from round-2 reply

- [x] **Q1 — `DI 03` = pin 2 confirmed by vendor** (matches manual + vault). Wire 2 lands on pin 2. No change.
- [ ] **⭐ Wire 1 redesign — recording gate moves to `DO 03` (pin 22), Gated mode.** `DAQ_ON` (pin 13) only indicates *streaming* and emits ~0.5s idle pulses in Allego → unsuitable as a clean recording gate (false edges). Use **`DO 03` pin 22** with "BNC Breakout Board" toggle ON + Digital Out Control = "Gated". Update [[wiring-guide|Wiring Guide]] Wire 1 + diagrams + [[overview|Overview]] DB25 pinout/architecture. **Re-check: does this collide with the multi-Pi return-DI plan? No — returns use DIs (pin 2/15/3/16); DO 03 is an output.**
- [ ] **Allego config dependency now baked in:** the multi-Pi DI returns **and** the DO 03 recording gate both require the **"BNC Breakout Board"** slider ON in Allego's System tab. Document in [[hardware-sync-setup|Setup Procedure]] + [[gpio-sync-service|GPIO Sync Service]].
- [ ] **Optional streaming indicator:** keep `DAQ_ON` (pin 13) or front `DIGITAL OUT 1` (DO-01) as a *streaming* flag if both states wanted (recording is the must-have). Note pin-13 idle-pulse noise if used.
- [ ] **Q3 voltage — still open.** Await Jeffrey's manufacturer answer for DAQ_ON / DO 03 logic-high. Likely 3.3 V (Allego can't set 5 V) → divider unneeded, but **measure pin 22 (and pin 13) during a recording session** before finalizing. Feeds [[wiring-guide#⭐ Pin 13 (DAQ_ON) Voltage Check — run this BEFORE building/buying the divider|voltage check]] (extend to pin 22).
- [ ] **Q4b + Q5 — email KC Kong (`KC@kontex.io`)** for: (a) fan-out of one gate to 4 Pi GPIO inputs (buffer/driver?), (b) grounding 4 devices on SYS GND without ground loops, (c) Ubuntu 24.04 Core2 drivers/kernel/udev/Thunderbolt-authorization. New round-3 inquiry, different recipient.

### Reply verbatim (archived)

> Dear Andrea,
>
> Yes, you are correct – DI 03 is 2, whereas DO 03 is 22.
>
> This is also true, my mistake – only the XDAQ AIO and One+ have a DO 02. I just tested pin #13 DAQ_ON and can confirm that it switches to logic high when the DAQ is streaming data in both Allego and XDAQ-RHX. In this regard and when using the Core2 system, it behaves almost the same as DO 01. They both send a high signal when data is streaming.
> That said, the behavior of DO 01 and DAQ_ON are slightly different when compared while using Allego. They both will show a high signal while streaming is active, however DAQ_ON will show short pulses every 0.5s or so when streaming is off. This is because Allego is constantly scanning headstage ports and GPIOs for changes when streaming is off, and also because the DAQ_ON pin wasn't on the development radar and I think you may have been our first customer to inquire on it.
> Even though the Core2 does not have a DO 02 connector, I found that this function will fall to DO 03 when you toggle on the "BNC Breakout Board" slider at the top of the System tab. When the Digital Out Control section is set to "Gated" mode and the BNC Breakout Board option is toggled on, it will show DO 03 as indicating "Recording status". It took about 15-20 seconds for it to populate, but it did appear and that should allow you to sync recording status with any device connected to that pin which can receive a pulse.
>
> Voltage of DAQ_ON: I don't know, but I'm asking the manufacturer. Considering the wording of the doc, I'd assume that the voltage would be in line with the rest of the DOs, but I'll let you know what I find. Allego does not currently have an option to change the DO voltage from 3.3 V to 5 V.
>
> For question 4 regarding using four Raspberry Pi units with discrete DI pins in the DB25, yes, Radiens can record and synchronize pulses received on multiple inputs with recorded neural data. In order to show the extra GPIOs in Allego, you'll need to toggle the option "BNC Breakout Board" on that I mentioned above. These channels will all appear in both the System and Monitor tabs and will be synced and stored in recorded data alongside the neural channels.
>
> For the remaining questions in 4 & 5, I'll refer you to my contact at Kontex, KC Kong (KC@kontex.io). He is directly involved in the design and development of the XDAQ systems and can answer those parts better than I can with the materials I've been provided.
>
> Best regards,
> Jeff

---

## Reply to Jeffrey — round 3 (draft 2026-05-28)

> [!note] Quick acknowledgement closing out Jeffrey's thread. Scale + driver questions go to KC Kong in the separate inquiry below.

> **To:** Jeffrey @ NeuroNexus
> **From:** andrea96p@kaist.ac.kr
> **Subject:** Re: XDAQ Core2 — digital I/O DB25 pinout & output voltage confirmation

Dear Jeffrey,

This is really helpful — thank you for actually testing pin 13 and digging into the Gated-mode behavior.

To confirm I've understood the plan for our Core2:

- I'll use **DB25 `DO 03` (pin 22)** as the recording gate — toggling on "BNC Breakout Board" in the System tab and setting Digital Out Control to "Gated" so DO 03 reports recording status.
- I'll treat **`DAQ_ON` (pin 13)** as a streaming indicator only, and not rely on it as a clean gate, given the ~0.5 s idle pulses you saw while streaming is off.
- **`DI 03` = pin 2** confirmed — the Pi's frame-sync return will land there.

I'll scope `DO 03` (pin 22) logic-high during a recording session before finalizing the wiring, but your note that Allego can't switch the DOs to 5 V already tells me to expect 3.3 V. I'd still appreciate the manufacturer's confirmation of the DO logic-high voltage whenever you hear back.

I'll follow up with KC Kong on the multi-Pi fan-out, grounding, and the Ubuntu driver questions.

Thanks again for the patient, detailed help.

Best regards,
Andrea
andrea96p@kaist.ac.kr

---

## New inquiry — KC Kong @ Kontex (draft 2026-05-28)

> [!abstract] Why this email
> Jeffrey referred the hardware/Linux questions to **KC Kong (`KC@kontex.io`)**, Kontex design/dev. Covers the deferred round-2 items: gate fan-out to 4 Pis (buffer?), grounding 4 devices on SYS GND, DB25 DO logic-high voltage, DI independence, and Ubuntu 24.04 Core2 device drivers/udev/Thunderbolt. Fill `[lab / affiliation]` before sending.

> **To:** KC Kong <KC@kontex.io>
> **From:** andrea96p@kaist.ac.kr
> **Subject:** XDAQ Core2 — multi-device digital sync wiring & Ubuntu 24.04 driver setup

Dear KC,

Jeffrey at NeuroNexus kindly referred me to you for the hardware and Linux side of an XDAQ Core2 setup. I'm a neuroscience PhD student building a synchronized video + electrophysiology rig: a Core2 for neural data, and several Raspberry Pi 5 camera nodes that I want to hardware-sync to the Core2's recording state over the DB25 digital I/O.

The plan so far (confirmed with Jeffrey): use DB25 `DO 03` (pin 22) in "Gated" mode as a recording-status gate out to the Pis, and dedicate separate DB25 digital inputs (`DI 03`–`DI 06`, pins 2/15/3/16) for a frame-sync pulse returning from each Pi, all referenced to `SYS GND` (pin 14). I'd value your guidance on the parts Jeffrey said you'd know best:

1. **Gate fan-out.** We'll have at least four Raspberry Pi 5 nodes (scaling toward eight), each needing the `DO 03` recording-gate signal on a GPIO input. Can a single Core2 DB25 digital output safely drive four Pi GPIO inputs in parallel (star wiring), or do you recommend a buffer / line driver (e.g. 74HCT244) between the Core2 and the Pis? What is the output drive current / fan-out limit on the DB25 DOs?

2. **Logic levels.** Can you confirm the logic-high voltage of the DB25 digital outputs (`DO 03` in particular) on the Core2? The rear IO-SPEC label reads "D OUT 3.3/5 V" and Allego has no setting to change it, so I'm assuming 3.3 V fixed on the DB25 — I want to be certain before wiring into the Pi's 3.3 V GPIO, which has no over-voltage tolerance.

3. **Grounding for multiple devices.** Any guidance on tying four (or more) external devices to the Core2 `SYS GND` (pin 14) without creating ground loops between the Core2, the Pis, and their PoE supplies? Single-point/star ground, series resistors per line — whatever you'd recommend.

4. **DI independence.** Are all six DB25 digital inputs (`DI 03`–`DI 08`) independently usable as Radiens trigger/marker channels, sampled at the headstage rate, when "BNC Breakout Board" is enabled? We'd assign one DI per Pi.

5. **Ubuntu 24.04 LTS driver / connectivity.** Our acquisition host runs Ubuntu 24.04 LTS with the Radiens suite and the `radiens` Python package already installed and working; what remains is the device-level link to the Core2 hardware. Could you confirm, for Ubuntu 24.04:
   - required drivers / kernel modules to connect the Core2 (USB and/or Thunderbolt) and the supported kernel versions;
   - any `udev` rules, group membership, or Thunderbolt-authorization steps so Allego can detect and stream from the Core2 without running as root;
   - any known Linux-specific limitations vs. Windows (Thunderbolt throughput, NP-mode support, etc.).

A Core2 datasheet/PDF and any reference wiring for multi-device digital sync would be very welcome.

Thank you for your time.

Best regards,
Andrea
[lab / affiliation]
andrea96p@kaist.ac.kr

---

## Reply — round 3 received 2026-05-28 (Jeffrey)

> [!info] Jeffrey's quick reply to the round-3 acknowledgement. **Closes Q3 voltage:** Core2 DB25 `DO 03`–`DO 08` and `DAQ_ON` (pin 13) are **3.3 V fixed** (confirmed with KC). Only `DO 01`/`DO 02` (BNC) can switch 3.3 ↔ 5 V, and Radiens can't toggle that anyway.

| # | Item | Status | Jeffrey's answer |
|---|------|--------|------------------|
| 0 | Plan confirmation (`DO 03` pin 22 = recording gate, `DAQ_ON` = streaming only, `DI 03` = pin 2) | ✅ **all correct** | "Yes, these are all correct." |
| 3 | DO logic-high voltage | ✅ **resolved — 3.3 V fixed** | Re-read the manual: **only `DO 01` + `DO 02` can switch between 3.3 V and 5 V** (and Radiens can't do it anyway). **`DO 03` – `DO 08` are 3.3 V logic only.** KC confirmed this. **KC also confirmed `DAQ_ON` is 3.3 V only.** |

### Action items from round-3 reply

- [x] **Q3 CLOSED — voltage divider definitively NOT needed.** `DO 03` (pin 22) = 3.3 V fixed → direct wire to Pi GPIO is safe (at-ceiling, no headroom but Pi 5 GPIO tolerates 3.3 V exactly).
- [x] **`DAQ_ON` (pin 13) = 3.3 V** confirmed (if ever used as optional streaming flag, no divider needed there either).
- [ ] Update [[wiring-guide|Wiring Guide]] BOM — move fixed-value resistors out of "Hold-until-answers" (no longer needed); resistor assortment kit can be downgraded from "order-now" to optional (still useful for pull-downs / generic lab stock).
- [ ] Update [[overview|Overview]] — drop the "Voltage Divider Design" section + the ⚠️ Voltage Compatibility callout (resolved).
- [ ] Update [[xdaq-core2-manual-reference|Manual Reference]] — note that **KC + Jeffrey (2026-05-28) confirm DB25 DO-03…08 + DAQ_ON = 3.3 V fixed** (resolves the earlier `DAQ_ON` "not tabulated" caveat).
- [ ] Still pending pin-22 scope/DMM check at first plug-in (sanity verification, not gating any purchase).
- [ ] KC round-3 (fan-out / grounding / Ubuntu drivers) still **awaiting reply** — sent 2026-05-28.

### Reply verbatim (archived)

> Dear Andrea,
>
> Yes, these are all correct.
>
> Upon reviewing the verbiage in the manual about the DB25 again, I see that it actually states that only DO 1 and DO 2 can be switched between 3.3 V and 5 V (and again, not something Radiens can do). DO 3 – DO 8 are designed only for 3.3 V logic. KC confirmed this and also that DAQ_ON is designed only to send a 3.3 V signal.

---

## ⚠️ Model correction — unit is an "XDAQ Core" (Gen-1?), NOT a Core2 (discovered 2026-05-29)

> [!danger] The whole thread above assumed a Core2. The physical unit on the bench does not match.
> On inspecting the hardware (2026-05-29), the chassis badge reads **"KONTEX XDAQ Core"**, serial **`0C006218`** — *not* "Core2 / Gen2". The rear panel disagrees with the [[xdaq-core2-manual-reference|Core2 manual reference]] on multiple points:
>
> | Feature | Core2 docs (what we assumed) | This unit (observed) |
> |---|---|---|
> | Power input | `USB PD 20 V ⎓ 3 A` | **`USB PD 12 V ⎓ 3 A`** |
> | Host link | Thunderbolt (`Computer` / `Peripheral`) | a **USB-C port labelled "USB data"** |
> | EXP1 / EXP2 | micro-HDMI | **USB-C** |
> | Ground terminals | 2× banana (SYS GND + Chassis GND) | **single GND pin** |
> | IO Port | female DB25 | female DB25 (matches) |
>
> Power brick that shipped: KONTEX USB-C **PD/PPS, 65 W** (5/9/12/15/20 V fixed + PPS 3.3–21 V). PD auto-negotiates → the `12 V` port pulls 12 V; **safe, no fixed-voltage risk.**

> [!warning] What this potentially invalidates (all Core2-specific answers)
> If this is the **Gen-1 XDAQ Core (Opal Kelly USB)** rather than the Thunderbolt Core2, the following from the thread above may NOT transfer and must be re-confirmed for this model:
> - **Driver path.** Core2 = Thunderbolt (`boltctl enroll`, `thor` manager). Gen-1 Core = **Opal Kelly USB → FrontPanel API + `60-opalkelly.rules` udev + `ok` manager** ([[kontex-developer-portal-notes|portal notes §1]]). This is the biggest unknown.
> - **DB25 pinout** (`DAQ_ON`=13, `DI 03`=2, `DO 03`=22, `GND`=14, `SAMPLE CLK`=25) — transcribed from the Core2 manual; may differ on Gen-1.
> - **`DO 03` (pin 22) "Gated" recording-status gate + "BNC Breakout Board" toggle** — Jeffrey verified this on a Core2; existence on Gen-1 unconfirmed.
> - **DB25 DO logic-high = 3.3 V fixed** — Core2 spec; re-confirm for this unit.
> - EXP-port type, channel counts.

> [!check] Model confirmed 2026-05-29 — Gen-1 XDAQ Core, Opal Kelly USB
> Plugged the **"USB data"** USB-C port into the NVR. `lsusb` reports **`ID 151f:0130 Opal Kelly Incorporated XEM7310-A75`** (VID `0x151f` = Opal Kelly); `boltctl list` empty (no Thunderbolt). → **Gen-1 USB, not Core2/Thunderbolt, confirmed.** Email ¶2 updated with this evidence; ready to send (fill `[lab / affiliation]`). Cabling: with a good USB-C cable the device enumerates at **USB 3.0 SuperSpeed (5 Gbps)** on Bus 002 — full streaming bandwidth confirmed. (An earlier poor cable enumerated at USB 2.0; swapped 2026-05-29.) `Driver=[none]` is normal — FrontPanel is a userspace libusb driver.

### Correction email to KC — round 3b (✅ SENT 2026-06-01)

> [!check] **Sent 2026-06-01** into the same KC Kong round-3 thread (KC silent since round-3 send 2026-05-28). Doubles as a follow-up **and** a model correction (Gen-1 XDAQ Core, not Core2). Driver question downgraded to a one-line sanity check (resolved ourselves). Open asks awaiting KC: Gen-1 DB25 pinout/gate/voltage re-confirm + fan-out buffer + grounding.

> **To:** KC Kong <KC@kontex.io>
> **From:** andrea96p@kaist.ac.kr
> **Subject:** Re: XDAQ Core2 — correction: our unit is a Gen-1 "XDAQ Core" (serial 0C006218), not a Core2

Dear KC,

Following up on my earlier note, and with one important correction before you spend time on it: my previous emails — and Jeffrey's answers — assumed our unit is an XDAQ **Core2**. On inspecting the hardware, it is actually a **first-generation XDAQ Core** with an Opal Kelly USB interface (chassis labelled **"XDAQ Core"**, serial **0C006218**). On our Ubuntu 24.04 host `lsusb` reports it as **`ID 151f:0130 Opal Kelly Incorporated XEM7310-A75`** and `boltctl list` is empty (no Thunderbolt), confirming the Gen-1 USB interface. The rear panel also differs from the Core2 docs (12 V USB-C PD not 20 V; a "USB data" port not Thunderbolt; USB-C EXP ports not micro-HDMI; a single GND terminal).

**On drivers — resolved, no action needed.** Allego already detects and streams from the unit on Ubuntu 24.04 (`SMARTBOX_PRO`, 30 kHz, USB-3 SuperSpeed). Allego bundles the Opal Kelly FrontPanel runtime and we added a `plugdev` udev rule for VID `151f` so `allegoserver` opens it without root. I mention it only in case you'd flag a different recommended approach.

Because the rest of what we settled was Core2-specific, could you confirm the following for **this Gen-1 unit (serial 0C006218)**:

1. **DB25 pinout + recording gate.** On the Core2, Jeffrey confirmed `DAQ_ON` = pin 13, `DI 03` = pin 2, `DO 03` = pin 22 (used as the recording gate in "Gated" mode with the "BNC Breakout Board" slider), `GND` = 14, `SAMPLE CLK` = 25, and DB25 outputs at **3.3 V fixed**. **Do those same pin assignments, the Gated / BNC-Breakout-Board recording-gate mechanism, and the 3.3 V output level all apply to the Gen-1 Core?** If anything differs, which signal tracks recording (HIGH for the whole session), and at what logic-high voltage? I'm wiring into a 3.3 V Raspberry Pi GPIO with no over-voltage tolerance, so the output level matters. A Gen-1 Core DB25 pinout / datasheet would be ideal.

2. **Gate fan-out.** We'll have at least four Raspberry Pi 5 nodes (scaling toward eight), each needing the recording-gate signal on a GPIO input. Can a single DB25 digital output safely drive four Pi GPIO inputs in parallel (star wiring), or do you recommend a buffer / line driver (e.g. 74HCT244)? What is the DB25 output drive-current / fan-out limit?

3. **Grounding for multiple devices.** Any guidance on tying four (or more) external devices to the unit's GND without creating ground loops between it, the Pis, and their PoE supplies?

Apologies for the moving target — I'd taken "Core2" from our paperwork. A datasheet for this specific model, and any reference wiring for multi-device digital sync, would be very welcome.

Thank you for your patience.

Best regards,
Andrea
andrea96p@kaist.ac.kr

---

## Reply — round 3b received 2026-06-05 (KC Kong)

> [!success] **KC's reply closes the last vendor open items.** Gen-1 DB25 pinout = Gen-2 (Core2) → all transcribed pins valid for our unit (serial 0C006218). Output 3.3 V fixed, driver TI SN74LVC2G17 (~20 mA). Star-grounding scheme given (XDAQ Core = hub). **Nothing left to ask the vendor — remaining work is bench/wiring only.**

| # | Question | Status | KC's answer |
|---|----------|--------|-------------|
| 1 | Gen-1 DB25 pinout + recording gate + 3.3 V | ✅ **pinout confirmed (Gen1 = Gen2)** | "DB25 pinout for Gen1 and Gen2 are the same." → `DAQ_ON`=13, `DI 03`=2, `DO 03`=22, `GND`=14, `SAMPLE CLK`=25 all valid for our Gen-1 unit. Pinout fig: <https://docs.kontex.io/XDAQ/CORE2/#xdaqtm-db25-io-connector-pinout>. *(Allego Gated-mode / BNC-Breakout-Board → DO 03 = recording-status mechanism is software, Jeffrey-verified, gen-independent — validate at bench.)* |
| 2 | Gate fan-out / drive limit | ✅ **resolved → star wiring, no buffer** | "For Gen1 CORE, the output is set at 3.3 V. The output driver is TI **SN74LVC2G17**, which can supply about **20 mA**." → 20 mA ≫ load of 4–8 high-Z Pi GPIO inputs (≈2.6 mA worst-case w/ 10 kΩ pull-downs). **74HCT244 buffer NOT needed** — single `DO 03` star-wires to all Pis. |
| 3 | Grounding 4+ devices, no ground loops | ✅ **resolved → star ground** | "Use the XDAQ CORE as the center of the Ground and fanning in the other devices' GND following the **star grounding** scheme." → each Pi GND home-runs to Core `GND` (pin 14); no daisy-chain, no Pi-to-Pi GND ties. |

### Action items from round-3b reply

- [x] **Pinout — Gen-1 = Gen-2 confirmed by KC.** Cleared all "UNVERIFIED for Gen-1" danger callouts in [[wiring-guide|Wiring Guide]] + [[overview|Overview]].
- [x] **Fan-out decision — star wiring, no buffer.** SN74LVC2G17 ~20 mA ≫ Pi high-Z input load. 74HCT244 moved from BOM "order-now"/"hold" → **removed** (star-wiring confirmed sufficient).
- [x] **Grounding — star ground (Core = hub).** Star-grounding section + diagram added to [[wiring-guide|Wiring Guide]] (was single-Pi only).
- [ ] **Bench validation (only remaining work):** scope/DMM `DO 03` (pin 22) → expect clean 0 ↔ 3.3 V in Gated mode w/ BNC Breakout Board ON; logic-analyzer idle check (no stray pulses); then star-wire DB25 → 4× Pi GPIO 17 direct (no divider), each Pi GND home-run to pin 14.
- [ ] Order the BOM "order-now" set (~$40) — safe to buy; no contingency items left pending.

### Reply verbatim (archived)

> Hi Andrea,
>
> Regarding your questions:
>
> 1. DB25 pinout for Gen1 and Gen2 are the same. You may find the detail at: https://docs.kontex.io/XDAQ/CORE2/#xdaqtm-db25-io-connector-pinout.
>
> 2. For Gen1 CORE, the output is set at 3.3V. The output driver used is TI SN74LVC2G17 which can supply about 20mA.
>
> 3. We recommend using the XDAQ CORE as the center of the Ground and fanning in the other devices' GND following the star grounding scheme.
>
> Please let me know if you have any questions. Have a great weekend!
>
> Best,
> KC

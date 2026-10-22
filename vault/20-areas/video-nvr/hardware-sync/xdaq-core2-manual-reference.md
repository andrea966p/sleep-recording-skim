---
tags:
  - infrastructure
  - hardware-sync
  - reference
  - manual
  - xdaq
  - pinout
created: 2026-05-27T00:00:00.000Z
status: complete
source: https://docs.kontex.io/XDAQ/CORE2/#xdaqtm-db25-io-connector-pinout
---

# XDAQ™ Core2 — Digital I/O Manual Reference (authoritative)

> [!danger] 2026-05-29 — this page documents the **Core2**, but our physical unit is a **Gen-1 XDAQ Core (Opal Kelly USB, serial 0C006218)**. Treat every pinout/voltage/gate detail here as **Core2 reference only — UNVERIFIED for our unit** until KC confirms the Gen-1 Core DB25. Verified host/driver state: [[xdaq-core-gen1-ubuntu-driver]].

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The single authoritative source for the XDAQ Core2 DB25 connector — exact pin numbers, signal labels, and the electrical specs (input/output voltages) — transcribed verbatim from the KONTEX Core2 online manual on 2026-05-27, with the original manual figures embedded so this note survives even if the website goes down.
>
> **Why it exists.** Every other hardware-sync note (wiring, overview, design justification) needs *one* correct pinout to point at. Earlier docs cited only signal labels (manual prints labels, not always pin numbers) and a vendor email got one pin wrong. This page is the ground truth; the others link here.
>
> **How to read this page.** The pinout table is the part you wire from. The electrical-specs table tells you the voltages. The "Discrepancies this resolves" section records what was previously wrong and why. Big picture: [[overview|Hardware Sync Overview]].

> [!quote] Paper-ready
> Digital I/O pin assignments and logic levels for the synchronization link were taken from the KONTEX XDAQ Core2 manual: the DB25 connector exposes six digital inputs (DI-03…DI-08, 2.2–5.5 V logic-high) and six digital outputs (DO-03…DO-08, 3.3 V logic-high), with a DAQ_ON system signal (pin 13) asserted logic-high at the onset of a recording session and a SAMPLE CLK output (pin 25) at the headstage sampling rate.

> [!info] Source
> KONTEX, **XDAQ™ Core2 documentation**, "XDAQ™ DB25 IO Connector Pinout" + "Technical Specifications" + "I/O Ports", retrieved 2026-05-27.
> <https://docs.kontex.io/XDAQ/CORE2/#xdaqtm-db25-io-connector-pinout>
> Manual figures archived locally (in case the site changes): `attachments/xdaq-core2-db25-pinout.png`, `attachments/xdaq-core2-tech-specs.png`.

---

## DB25 IO Connector Pinout

![[xdaq-core2-db25-pinout.png]]

Transcribed from the manual figure above (DB25 front view; pin 1 bottom-left, pin 25 top-right):

| Pin | Signal | Pin | Signal |
|-----|--------|-----|--------|
| 1 | — (unused) | 14 | **GND** (Sys GND) |
| 2 | **DI 03** | 15 | DI 04 |
| 3 | DI 05 | 16 | DI 06 |
| 4 | DI 07 | 17 | DI 08 |
| 5 | — | 18 | — |
| 6 | — | 19 | — |
| 7 | — | 20 | — |
| 8 | — | 21 | — |
| 9 | — | 22 | **DO 03** |
| 10 | DO 04 | 23 | DO 05 |
| 11 | DO 06 | 24 | DO 07 |
| 12 | DO 08 | 25 | **SAMPLE CLK** |
| 13 | **DAQ ON** | | |

**Digital inputs (6):** DI 03=pin 2, DI 04=15, DI 05=3, DI 06=16, DI 07=4, DI 08=17.
**Digital outputs (6):** DO 03=pin 22, DO 04=10, DO 05=23, DO 06=11, DO 07=24, DO 08=12.
**System signals:** DAQ ON=pin 13, SAMPLE CLK=pin 25, GND=pin 14.

> [!tip] Signals used by our sync link
> - **`DAQ_ON` → pin 13** — recording gate into the Pi (Wire 1).
> - **`DI 03` → pin 2** — frame-sync marker from the Pi (Wire 2). ⚠️ **Pin 2, not Pin 22.** Pin 22 is `DO 03` (an output) — do not wire the Pi's output into it.
> - **`GND` → pin 14** — shared ground.
> - **`SAMPLE CLK` → pin 25** — headstage sampling clock (future per-sample alignment).

---

## Electrical Specifications (Synchronized GPIO)

![[xdaq-core2-tech-specs.png]]

Verbatim from the Core2 spec table + I/O-ports text:

| Spec | Value (Core2) |
|------|---------------|
| **Digital In** | **2.2 – 5.5 V logic high**; 7 ch onboard (DI-01 BNC + DI-03…08 DB25), 31 ch expandable. Compatible with both 3.3 V and 5 V signals. |
| **Digital Out** | **Core2 BNC: DO-01 only — 3.3 V or 5 V, software-configurable** (the dual DO-01/DO-02 BNCs are an XDAQ **ONE+** feature, not Core2). **DB25 (DO-03…DO-08): 3.3 V logic high (fixed).** 7 ch onboard, 31 ch expandable. |
| **ADC** | 1 ch onboard (AI-01, BNC), ±10 V, 16-bit; 7 ch expandable |
| **DAC** | 1 ch onboard (AO-01, BNC), ±10 V, 16-bit; 7 ch expandable |
| **GPIO connectors** | 4× BNC + 1× D-Sub25 |
| **IO Expansion** | **2× MicroHDMI ports** (EXP1, EXP2 — for I/O Expander accessory) |
| **Ground terminals** | 1× Chassis GND, 1× Digital GND |

### Signal behavior (from manual text)
- **DAQ ON:** "Logic high at onset of a recording session." → asserted on the DB25 (pin 13), directly accessible; goes HIGH when a recording session starts. (Confirm level-vs-pulse and exact voltage on a scope/DMM at wiring validation.)
- **SAMPLE CLK:** "the sampling clock used to drive the X-Headstage™" (pulse train at headstage rate).
- **Sys GND:** digital ground shared by internal circuitry. **Chassis GND:** enclosure / HDMI shield / earth via PSU.
- **More than 6 DI / 6 DO:** requires breakout via the EXP1/EXP2 MicroHDMI ports (I/O Expander). Additional analog GPIO requires the XDAQ GPIO Expander.

---

## Front & Rear Panel Layout

![[xdaq-core2-panels.png]]

**Front panel (left → right):**
- **Mode LEDs:** XR, XSR, NP, S1. **Port LEDs:** P1–P4 (per-headstage status).
- **REC & STIM HEADSTAGES:** 4× micro-HDMI (ports 1–4 = P1–P4).
- **Neuropixels:** 2× USB-C (1, 2).
- **ANALOG:** `IN 1` + `OUT 1` (2× BNC) = AI-01, AO-01.
- **DIGITAL:** `IN 1` + `OUT 1` (2× BNC) = **DI-01 and DO-01 only — one digital-in BNC and one digital-out BNC.**

**Rear panel:**
- **`IO Port` = the DB25** — this is where `DAQ_ON` (13), `DI 03` (2), `DO 03…08`, `SAMPLE CLK` (25), `GND` (14) are. (Confirms DB25 is on the rear.)
- **IO SPEC printed on the chassis** (authoritative): `D IN` High = **3.3–5 V**, `D OUT` High = **3.3/5 V**, `A IN`/`A OUT` ±10 V; all Low = 0 V (digital) / −10 V (analog).
- `EXP 1` + `EXP 2` (micro-HDMI). `Audio` (3.5 mm). `Peripheral` + `Computer` (Thunderbolt-style; `Computer` → host, `Peripheral` → daisy-chain). `USB PD 20 V⎓3 A` (power). `SYS GND` + `Chassis GND` (banana jacks).

> [!info] Host interface — Core2 is Thunderbolt-only
> Confirmed by the libxdaq Introduction page (`developer.kontex.io/libxdaq-docs/introduction.html`): **Core Gen 2 → Thunderbolt** (Kontex's custom solution); only Gen-1 Core/One use Opal Kelly USB. On Linux the Core2 driver is the standard `thunderbolt` kernel module + `boltd` authorization (`boltctl enroll <uuid>`) — **no Opal Kelly USB udev rules needed.** Per Kontex, Thunderbolt latency is `<0.5 ms` with `~GB/s` throughput. libxdaq's `thor` device manager (`libthor_device_manager.so`) is the Linux library; sits underneath Allego/Radiens. Full notes on the Linux/libxdaq/pylibxdaq side in [[kontex-developer-portal-notes|Kontex Developer Portal Notes]].

> [!warning] DO1/DO2 sync = XDAQ ONE+, not Core2
> NeuroNexus described syncing via **DO1 (streaming HIGH) / DO2 (recording HIGH)** front BNCs. Those **dual digital-output BNCs (DO-01 + DO-02) belong to the XDAQ ONE+** (`docs.kontex.io/XDAQ/ONE/`: "two pairs of digital input (DI-01, DI-02) and output (DO-01, DO-02)"). The **Core2 has only one digital-out BNC, `DIGITAL OUT 1` = DO-01** — the panel confirms it (4× BNC = AI-01 + AO-01 + DI-01 + DO-01). The "BNC DO-01, DO-02" line on the Core2 page is boilerplate shared with the ONE+ doc. **On the Core2, the recording gate we can reach is DB25 `DAQ_ON` (pin 13)** ("logic high at onset of a recording session"); a DO1-style *streaming* indicator may be available via front DO-01 — open vendor Q ([[neuronexus-inquiry-email|round-2 email]] item 2).

---

## Discrepancies this resolves

> [!danger] 1. `DI 03` is Pin 2, not Pin 22
> The NeuroNexus email reply (2026-05-27, [[neuronexus-inquiry-email|inquiry note]]) gave `DI 03 = Pin 22`. The manual figure shows **Pin 2 = DI 03** and **Pin 22 = DO 03** — the reply transposed a digital input with an output. The original vault pinout ([[radiens-api-reference|API ref]], [[wiring-guide|Wiring Guide]]) was **correct**: DI 03 = Pin 2. Wire 2 lands on **Pin 2**. (DAQ_ON=13, GND=14, SAMPLE CLK=25 in the reply were correct.)

> [!check] 2. DB25 digital outputs (incl. `DAQ_ON`) are 3.3 V fixed — confirmed by vendor 2026-05-28
> The XDAQ User Manual §3.4.2 (IO Expander) states "Digital Outputs: Logic high 3.6 V", which had us building a 1 kΩ/2 kΩ divider. The Core2 spec said **DB25 digital outputs (DO-03…08) are 3.3 V** and "configurable 3.3 / 5 V" applies only to BNC `DO-01`/`DO-02`. **`DAQ_ON`'s own voltage was the only gap** — closed 2026-05-28 by **KC + Jeffrey** ([[neuronexus-inquiry-email#Reply — round 3 received 2026-05-28 (Jeffrey)|round-3 reply]]): "DO 3 – DO 8 are designed only for 3.3 V logic. KC confirmed this and also that DAQ_ON is designed only to send a 3.3 V signal." Radiens cannot toggle DO voltage 3.3 ↔ 5 V anyway. → **Voltage divider is unnecessary**; wire DB25 outputs (incl. the new recording gate `DO 03` pin 22) directly to Pi GPIO. 3.3 V = Pi GPIO ceiling exactly (within spec).

> [!note] 3. DB25 = 6 DI + 6 DO (onboard total = 7 DI)
> The DB25 exposes six DI (DI-03…08) and six DO (DO-03…08). The spec's "7 ch onboard" digital-in count includes the BNC DI-01. [[radiens-api-reference|API ref]] previously said "7 channels" without the DB25-vs-onboard distinction.

---

## Related
- [[overview|Hardware Sync Overview]] — wiring architecture (pins should match this reference)
- [[wiring-guide|Wiring Guide]] — physical hookup (pin numbers sourced here)
- [[radiens-api-reference|Radiens API Reference]] — DB25 pinout table (sourced here)
- [[references-and-justification|Design Justification & References]] — divider rationale (3.6 V → 3.3 V correction above)
- [[neuronexus-inquiry-email|NeuroNexus Inquiry & Reply]] — vendor Q&A (pin-22 error noted here)
- [[kontex-developer-portal-notes|Kontex Developer Portal Notes]] — libxdaq / pylibxdaq / Linux Thunderbolt driver path

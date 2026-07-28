---
tags:
  - decision
  - research
  - xdaq
  - kontex
  - open-ephys
  - intan
  - scale-up
  - 32-mice
  - corrections
created: 2026-07-28
status: live
method: 5 parallel research agents, primary sources only, verbatim quotes
---
# DAQ Research Findings, 2026-07-28 — Primary Sources, and What They Overturn

> [!tip] Part of the rig expansion program
> Front door: **[[RIG-EXPANSION-HUB]]**. This note feeds [[2026-07-24-daq-32-mouse-final-comparison]] and the professor-facing `DAQ-comparison-32-mice.docx`.

> [!abstract] What this is
> Findings from five parallel research passes over PRIMARY sources only (vendor manuals, datasheets, API docs, peer-reviewed papers), commissioned because the earlier comparison rested partly on our own bench experience and on documents we had only partially read. **Several previously-held claims did not survive.** Every claim below carries a verbatim quote and a source.
>
> The headline: **a NeuroNexus XDAQ user manual we had never read** (`NNX_XDAQ_USER MANUAL_202403`) contains the model-comparison and grounding detail that the docs.kontex.io website omits.

---

## 1. 🔴 CORRECTIONS — claims that did NOT survive

| Previously held | Corrected finding | Source |
|---|---|---|
| "Our 8 mice sit in 4 shared-ground pairs" | **Worse.** XDAQ Core spec: **"Signal Isolation: No"**, **"Headstage Power Circuits: 1"**. All 8 mice share ONE headstage power/ground circuit across all four ports | NNX XDAQ manual p.9 |
| "The Port Expander is an optional isolation upgrade" | **Mandatory for 16 per box.** Model table lists ONE at "16 X3R32*" with footnote **"* Requires Port Expander"** | NNX XDAQ manual p.9 |
| "Port Expander is USB-PD/AC powered" | **It has an internal battery.** "The Port Expander **is battery powered** to ensure a noise free communication"; "can be used solely on the built-in battery or plugged in" | NNX manual §3.4.3, §4.7 |
| "The radiens API gives per-ANIMAL start/stop" | **Per-PORT only, and ports max out at 8** (`"a"`–`"h"`). ONE+ has **4** physical ports; 16 animals hang off Port Expanders. **16 independently schedulable animals is unreachable in any package.** Worse: port args are "Only meaningful in **split-ports mode**", and that mode is **documented nowhere** | Radiens API docs |
| "Intan ports are isolated ✅" | **Overstated.** Verbatim is "isolated from the controller and from earth ground" — names neither other ports. Strongly implied port-to-port (word "independent" ×3, contrast vs old board's "4, non-isolated", ground-loop rationale) but **no isolation voltage, no barrier capacitance, no leakage spec, no schematic** | Intan Rec Controller User Guide p.3 |
| "Intan direct" | **Intan sells nothing directly since Feb 2026.** Sole worldwide distributor = **White Mountain Systems**. No Korea distributor. **Closed 22 Jul – 2 Aug 2026.** 90-day warranty | intantech.com/pricing.html, WMS_partnership.html |
| "Open Ephys board = 4 animals (per Margarida)" | **"Maximum 4 animals" is NOT documented anywhere official.** Board is rated **"up to 8 RHD headstages on 4 tethers"**; GUI exposes 8 slots (4 rows × 2). BUT 8 separate ANIMALS has never been published — we would be first | open-ephys.org/acq-board, GUI docs |
| "XDAQ's edge = proven 72h on our bench" | **Dropped as a differentiator** at Andrea's direction. All three products are built for this | — |

---

## 2. ✅ NEW FINDINGS THAT HELP US

**The ONE+ has grounding tools the Gen-1 Core entirely lacks.** Verbatim, NNX manual p.22:

> "SYS GND node is the common ground used by the primary electronics circuitry... Two additional ground nodes are available: **P1 and P2-4 nodes, which are the actual animal grounds at the headstages.** Each node in the SYS ground and animal grounds (P1 and P2-4) can be connected to the Earth ground node by activating... the **ESD DIP switches** in the back panel. DIP #1 of each corresponding node... ties a **1nF** capacitive discharge path to Earth ground. Similarly, DIP #2... adds an additional 1nF in parallel to a **1MOhm** resistor to Earth ground."

Given our 60 Hz work concluded the rig is **floating with zero earth references**, this is a systematic, switchable tool for exactly that. Note also: even on a ONE+ *without* an expander, ports 2-4 share one animal-ground node.

**The vendor hedges its own isolation claim.** NNX manual §4.3:

> "**In theory**, having isolated animal grounds should offer the best recording quality. **However, due to the potential grounding inconsistency or environment noise interference, it is best for users to experiment with various ground settings.**"

**Intan endorses our foil decision.** Noise Reduction app note:

> "The GND terminal on the Intan headstage should be connected to the tissue via a ground electrode or skull screw, but **this should not be connected to the Faraday cage or to any external ground.**"

Confirms dropping foil grounding on 2026-07-16 was right ([[eeg-60hz-saga]]).

**🔴 Intan's own analog-run spec, and we are far over it.** Same app note:

> "**Minimize the length of the wires between the headstage and electrodes (ideally less than 10 cm).** Long wires pick up AC magnetic fields."

This is the **analog electrode-to-headstage** run, NOT the digital SPI tether. KonteX independently flagged our run as too long. **Two vendors now agree, and this costs nothing to fix.** ⚠️ Confirm which run the 2026-07-28 shortening to 22.5 cm applied to.

**Only Open Ephys can synchronise multiple Intan controllers.** Intan RHX is one controller per instance, and **there is no clock input on the controller** — two controllers free-run and drift. But an OE `rhd-recording-controller` plugin exists (Windows/Linux/macOS) with a documented Record Node synchroniser. So even on Intan hardware we would end up in the Open Ephys GUI.

---

## 3. 📚 LITERATURE ON SHARED GROUNDS

**The key measurement, and it argues AGAINST paying for isolation.** eNeuro 2022, PMC9581574 — 4 mice, ONE Open Ephys board, 48 h chronic, one shared board ground:

> "**Simultaneous multi-animal recordings with one Open Ephys acquisition system has not been reported previously to our knowledge**, therefore we wanted to verify that there was no bleed-through across channels"
> "signals recorded simultaneously from different mice had **negligible near zero correlation (1.35×10⁻⁵ ± 0.16×10⁻⁵)**, which was similar in magnitude to chance correlation"

⚠️ Caveats: **referential montage, not bipolar**; correlation detects signal bleed-through but says **nothing about shared 60 Hz hum**.

**Counter-evidence.** OpBox (eNeuro 2020), **12 subjects**, chose one **battery-powered** amplifier per animal, explicitly "to reduce power line noise", ~$497/subject.

**Our "2 mice per headstage failed" folklore is UNVERIFIED.** No rodent literature exists either way. The human equivalent — two subjects, one amplifier, shared ground via a Y-distributor — is **peer-reviewed and worked** (PMC9945774), with the manufacturer caveat that it works "in cases in which the noise levels between the two participants are pretty much equal". Our documented 53× impedance imbalance and over-long analog run explain a failed attempt without needing shared ground as the cause.

**No published measurement exists** of how many µV of hum per-animal isolation removes, in any species. Also **no published 16- or 32-mouse parallel sleep rig** with documented grounding architecture. That precedent simply does not exist.

**Intan has published NO multi-animal guidance at all.** The C3442 datasheet never uses the word "animal"; every stated use case is high channel count on ONE animal. So two animals per port is **reasonable but undocumented** — neither endorsed nor prohibited.

---

## 4. THE CABLE-LEVEL FACT, IDENTICAL ACROSS ALL THREE

> "Each RHD SPI cable contains 12 conductors: **two thicker wires for power and ground**, and ten thinner wires arranged in five twisted pairs"

One ground conductor per cable. **Two headstages on one C3442 share it. No isolation is possible within a port, on ANY of the three systems.** This is an Intan Rhythm cable fact, not a vendor difference.

⚠️ Gotcha for paired configs: with daisy-chained cables over 6 ft, Intan requires **removing R1/R2/R3 from one of the two amplifier boards**, which then degrades that board for standalone use.

---

## 5. OPEN EPHYS SPECIFICS

**Isolation: none, in any configuration.** Verbatim: *"The Acquisition Board is **referenced to your PC ground circuitry via the USB cable**."* Grounding is board-wide screw terminals, not per-port. **So buying one mouse per port on Open Ephys buys nothing** — there is no isolated configuration to buy.

**RHD2216 handling:** the plugin cannot auto-detect a 16-channel bipolar chip; **each slot must be manually toggled** 32 → 16 channel mode. With 32 animals that is 32 settings to get right and re-check after updates.

**Open bugs relevant to 72 h runs** (github.com/open-ephys/plugin-GUI): #692 recording stops on a spurious disk-space warning; #643 recording stops after ~1 min; #676 external TTL triggers cause repeated start/stop cycles (**directly relevant to our pulse-train plan**); #695 HTTP API crashes GUI. Radiens has **no public issue tracker**, so its defect history cannot be audited — a difference in visibility, not necessarily quality.

**Pricing, retrieved 2026-07-28**, EUR only (no USD published), at **1 EUR = 1.137 USD** (xe.com):

| Item | Part | EUR | USD |
|---|---|---|---|
| Acquisition Board 3rd gen | OEPS-9029 | €3,385 | $3,849 |
| SPI Headstage 16ch bipolar | OEPS-6577-6574 | €780 | $887 |
| I/O Board | OEPS-6501/6502 | €13 | $15 |
| Torque-free SPI commutator | OEPS-7761 | €2,595 | $2,951 |

---

## 6. INTAN PRICING (retrieved 2026-07-28, unchanged under WMS)

| Part | Item | Price |
|---|---|---|
| C3004 | RHD 512ch controller (4 ports → 8 mice) | $9,950 |
| C3008 | RHD 1024ch controller (8 ports → 16 mice) | $14,250 |
| C3203 | 3 ft standard SPI cable | $215 |
| C3206 | 6 ft standard SPI cable | $295 |
| C3213 | 3 ft ultra-thin SPI cable | $415 |
| C3216 | 6 ft ultra-thin SPI cable | $595 |
| C3442 | Dual headstage adapter (splitter) | $345 |
| **C3430** | **SPI cable adapter board, for slip rings** | **$111** ← previously unpriced |
| C3410 | 36-pin electrode adapter board | $255 |
| — | Intan RHX software | **free, open source** |

Headstage prices deliberately omitted.

---

## 7. WHAT TO DO WITH THIS

**For the 2026-07-29 KonteX call** ([[2026-07-29-kontex-kc-call-prep-rig-finalization]]):
- Port Expander **battery life over 72 h**, and whether mains operation forfeits the isolation benefit ← NEW
- Confirm Port Expander is **required** for 16/box, so it cannot be value-engineered out
- Ask about the **ESD DIP switch** grounding strategy for our 60 Hz problem ← NEW
- Report the **XDAQ-OE v0.4.4 packaging bug** and ask for a fixed build

**For Intan, if it stays a candidate:** email support@intantech.com for **port-to-port isolation and barrier capacitance**; start **White Mountain Systems vendor registration at KAIST now**, since that is the critical path.

**For us, costing nothing:**
- **Shorten the analog electrode-to-headstage run toward 10 cm** — two vendors agree, and by our own measurements this attacks the dominant term
- Do **not** buy the Allego licence (§1); it does not deliver the capability that justified it
- Retire the "2 mice per headstage is a no-go" folklore as unverified

## Related
[[RIG-EXPANSION-HUB]] · [[2026-07-24-daq-32-mouse-final-comparison]] · [[xdaq-32-mouse-wiring-and-channel-law]] · [[eeg-60hz-saga]] · [[2026-07-29-kontex-kc-call-prep-rig-finalization]]

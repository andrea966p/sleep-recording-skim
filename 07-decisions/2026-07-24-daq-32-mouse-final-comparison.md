---
tags:
  - decision
  - hardware
  - comparison
  - xdaq
  - open-ephys
  - intan
  - acquisition
  - scale-up
created: 2026-07-24
status: open
supersedes: "[[2026-07-23-daq-ecosystem-comparison-xdaq-vs-openephys]]"
---
# DAQ Ecosystem Comparison, FINAL, 3-Way for 32 Mice — XDAQ vs Open Ephys vs Intan

> [!warning] CONFIDENTIAL PRICING, VAULT-ONLY
> This doc contains Kontex quote 262024 pricing, which carries a do-not-publicly-disclose clause, plus Open Ephys and Intan list prices. Keep it inside the vault. DO NOT publish it as a web Artifact, paste it into a public repo, or share the pricing outside the lab.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The finalized head-to-head for the acquisition box (the DAQ) that will drive our next rig, scaled all the way to **32 mice recorded at once** (one mouse = one Intan RHD2216 bipolar headstage). Three ecosystems now, not two: **XDAQ / NeuroNexus (Kontex)** — what we already run; **Open Ephys** — open hardware, free software; and **Intan direct** — the company that makes the amplifier chips all three use, selling its own big recording controllers.
> **What changed since the 2026-07-23 version.** (1) The Kontex quote landed, so XDAQ adapter prices are real numbers now. (2) Open Ephys prices are on their web store, so they are pulled in. (3) We added the whole Intan column with a full priced parts list. (4) We SETTLED the confusing "two headstages per port" question from the Open Ephys email, using Intan's own datasheets.
> **The big finding.** A splitter (the dual-headstage adapter) really does let you put **two SEPARATE animals on one port**, it is NOT stuck to two headstages on one animal like the Open Ephys email implied. The catch is that those two animals then share one ground wire. For our BIPOLAR recordings that shared ground is mostly cancelled out by the amplifier, so it is tolerable. That splits every ecosystem into two cost scenarios: **isolation-first** (one mouse per port, pricier) vs **density-first** (two mice per port, cheaper, shared ground).
> **How to read it.** §1 = the port-scenario finding (the new core). §2 = the master 3-way table. §3 = the priced 32-mouse parts lists for each ecosystem, both scenarios. §4 = what is still owed. §5 = the current reading (not a final decision, that goes to a council once the last prices land).

> [!quote] Paper-ready
> Three acquisition ecosystems were costed for a chronic 32-animal mouse EEG/EMG rig, all interfacing the same Intan RHD2216 bipolar amplifier over SPI: the XDAQ system (Kontex, running NeuroNexus Allego/Radiens), the open-source Open Ephys Acquisition Board (Open Ephys GUI), and Intan's own RHD Recording Controller (Intan RHX). Because one RHD chip occupies one SPI MISO data line irrespective of channel count, animal capacity is set by MISO-line count, not channel count. A dual-headstage adapter places two independent chips on the two MISO lines of a single SPI cable, permitting two separate animals per port at the cost of a shared cable ground and supply; for differential bipolar montages this shared ground is rejected as common mode, so per-port headstage doubling is electrically acceptable, whereas one-headstage-per-port preserves true per-animal ground isolation at higher hardware cost.

Companion docs: [[2026-07-23-daq-ecosystem-comparison-xdaq-vs-openephys]] (the 16-mouse 2-way predecessor, now superseded), [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] (XDAQ/Kontex thread + quote 262024), [[2026-07-21-openephys-acquisition-board-scale-up-option]] (Open Ephys option), [[openephys-inquiry-email]] (OE email + Margarida reply), [[intan-rhd-spi-wiring-and-headstage-limits]] (MISO physics), [[kontex-xdaq-hardware-reference]] (Kontex primary-source), [[eeg-60hz-saga]] (the grounding history that makes isolation matter).

---

## 1. The two-headstages-per-port question, SETTLED

This was the confusing bit in Margarida's Open Ephys reply. She framed the dual-headstage adapter as "two headstages in the SAME animal," and therefore called the board "a maximum of four animals." Andrea's read was that the splitter gives two SEPARATE animals. **Andrea is right, with one grounding caveat.** Here is the resolution, straight from Intan's SPI cable and dual-headstage-adapter datasheets (transcribed in [[intan-rhd-spi-wiring-and-headstage-limits]]).

**The data side (good news):**
- An Intan RHD SPI cable carries 5 LVDS twisted pairs: CS, SCLK, MOSI, **MISO1, MISO2**. Two data-return lines.
- The dual-headstage adapter (Intan part **C3442**) wires each chip's data output to its OWN MISO line. MISO1 and MISO2 are electrically independent, each with its own termination resistor in the FPGA.
- So two chips on one cable = **two independent data streams**, sampled on the SAME clock (perfectly time-aligned), appended in software as separate channel blocks. This is NOT two headstages fused into one 32-channel stream on one animal. Intan's "128 channels on one animal" example is a USE-CASE CONVENTION (high-density probes), not an electrical rule.
- CONCLUSION: two separate animals per port is real. Margarida's "same animal only / max 4 animals" was **grounding conservatism, not a hardware limit.**

**The grounding side (the caveat):**
- That same cable has only ONE power and ONE ground conductor. Both headstages draw from the single supply and share the single ground. On the RHD chip, that ground IS the system reference.
- So two animals on one port = **two animals galvanically tied at a common ground/reference node.** This is exactly the inter-animal coupling we have been fighting in [[eeg-60hz-saga]].
- BUT our montage is **bipolar RHD2216**: every channel is a true differential pair (independent in+ and in- electrodes, both on the same animal). A shared system ground shows up as COMMON MODE and is largely rejected by the differential amplifier (RHD2216 balanced inputs, CMRR ~82 dB at 50/60 Hz WHEN electrode impedances are matched). So for us the shared ground is TOLERABLE.
- WARNING: this only holds for bipolar. On monopolar chips (RHD2132/2164), every channel is measured against that shared reference, so two animals on one port cross-contaminate. Do NOT do two-per-port on monopolar.
- WARNING: "tolerable" is not "isolated." Residuals remain: a real galvanic tie between the two animals, any ground artifact couples into both as common mode (rejected, not infinitely), and matched-impedance CMRR falls apart the moment one electrode goes open, which is precisely our frontal-electrode failure mode. So if a run is fighting hum, one-per-port is the safer topology.

**So every ecosystem gets TWO scenarios:**

| | **Scenario A — isolation-first** | **Scenario B — density-first** |
|---|---|---|
| Headstages per SPI port | 1 | 2 (via C3442 splitter) |
| Ports needed for 32 mice | 32 | 16 |
| Per-animal ground | dedicated per mouse | shared within each pair |
| Good for | fighting 60 Hz, open-electrode risk, monopolar | bipolar, budget, port-count-limited |
| Cost | higher (more boxes/ports) | lower (half the ports) |

**Isolation is NOT equal across the three ecosystems, even in Scenario A** — this is the make-or-break nuance:

| Ecosystem | Does Scenario A give TRUE per-animal isolation? | Mechanism |
|---|---|---|
| **Intan Recording Controller** | ✅ YES | Each SPI port is "electrically isolated from the controller and from earth ground" (Intan User Guide, verbatim). One mouse per port = one isolated ground domain per mouse. |
| **XDAQ / Kontex** | ✅ YES, via add-on | The **Port Expander (XDAQ-Port-EXP)** gives "isolated and dedicated electrical systems to each connected headstage... ground and reference nodes from each animal's headstage do not interfere." Costs extra ($1,525/port-expander). |
| **Open Ephys** | ⚠️ WEAKEST | NO isolation product exists ("depends on your design," docs + Discord only). The acquisition board's ports are NOT confirmed galvanically isolated from each other, so even one-per-port may share the board's common ground. Its 4 ports likely sit in one ground domain. |

That last row is the single biggest strike against Open Ephys for OUR rig, given the [[eeg-60hz-saga]].

---

## 2. Master 3-way comparison table (scoped to 32 mice)

Legend: ✅ confirmed strength · ⚠️ conditional · ❌ confirmed gap · ⏳ still owed (see §4). Prices tagged in §3.

| # | Dimension | **XDAQ / NeuroNexus (Kontex)** | **Open Ephys** | **Intan direct** |
|---|---|---|---|---|
| 1 | **Animals per single box** (1 hs/mouse) | Core **8**, ONE/ONE+ **16** | Acq Board **8** (4 ports × 2) | C3004 **8**, C3008 **16** (8 ports × 2) |
| 2 | **Native path to 32** | 2× ONE+ + 2× SyncLink (shared clock) | 4× Acq Board synced via I/O boards + TTL | 4× C3008 (or 2× if 2-per-port) |
| 3 | **Boxes to hit 32** | 2 | 4 | 4 (Scenario A) / 2 (Scenario B) |
| 4 | **Per-animal ground isolation** (our 60 Hz wall) | ✅ **Port Expander** (isolated ground/ref per animal) | ❌ **no product**, ports not confirmed isolated | ✅ **port-level isolated** by design (1 hs/port) |
| 5 | **RHD2216 bipolar support** | ✅ (SAdpt-XDAQ-OM12 path) | ✅ vendor-confirmed, "optimal for EMG/EEG" | ✅ native (it is Intan's own chip) |
| 6 | **Software + license** | Allego/Radiens **~$2.5-5k/seat**, OR $0 on XDAQ-RHX/OE | **$0** Open Ephys GUI | **$0** Intan RHX |
| 7 | **Reuses our Allego pipeline** (sleep64 map, `eeg-emg-analysis`, XDAT) | ✅ **fully** (if we stay on Allego) | ❌ rebuild | ⚠️ partial (RHX/Intan family, not XDAT/Allego) |
| 8 | **Video-sync (Phase 0a)** | ✅ already scoped (Allego Gated, DO 03 / DB25 pin 22) | ✗ re-implement on I/O-board digital in | ✗ re-implement on controller digital in |
| 9 | **Multi-box clock sync** | ✅ **SyncLink** (shared Harp clock, productized) | ⚠️ no sync box, route one TTL to all boards, clock-drift risk | ⚠️ **unconfirmed** for 4 controllers (biggest Intan risk) |
| 10 | **One PC or many** | **2 PCs** (SyncLink: each XDAQ → own PC) + 2 Allego licenses | **1 strong PC** (all boards, one GUI) | ⏳ likely multiple (RHX historically 1 controller/instance) |
| 11 | **Long-run reliability (24-72 h)** | ✅ **PROVEN on our rig** (72 h byte-perfect) | ⏳ multi-board multi-day track record unknown | ⏳ unknown to us at 4-controller scale |
| 12 | **32-mouse hardware price** | **EST ~$63-77k** hardware + license + 2 PCs (ONE+ unit price = estimate, quote owed) | **~€38-51k+** (EUR list; USD not published) + cables | **~$79-116k** (all PUBLISHED list) |
| 13 | **Openness / customization** | Closed, productized | **Open hardware** + Atlanta custom team | Closed, productized |
| 14 | **Maturity / risk for 32** | **Low** on reliability, ⏳ on price | **Higher** (multi-board sync homebrew, weak isolation) | **Medium** (turnkey boxes, but 4-controller sync unproven) |
| 15 | **Independent per-mouse record: separate FILE / independent START-STOP** (see record-control note below) | file: ✅ **`split_files_by_port`** (API) · start-stop: ✅ **`start_recording(port)`** (API, radiens v4.0) — UNVALIDATED on our Gen-1 · GUI: ❌ one global file+button | file: ✅ **Record Nodes** (per-animal dir+channels) · start-stop: ❌ **global** (`PUT /api/status` RECORD) | ⏳ RHX not yet doc-checked |

Legend applies as above. **Row 15 was our long-standing "Allego is flatly global" belief — it is now doc-overturned; see the callout.**

> [!important] Record control (Row 15) — DOC-VERIFIED 2026-07-24, overturns our old "single global R_ON/R_OFF" note
> Two SEPARATE questions were being conflated. Splitting them, verified against PRIMARY docs (raw HTML pulled 2026-07-24, not paraphrased):
>
> **Q1 — separate FILE per animal (not one big recording):**
> - **Open Ephys: ✅ native.** Multiple Record Nodes, one per source/animal, each with its own recording directory and channel selection (`PUT /api/recording/<record_node_id>` sets `parent_directory`/`record_engine`; `/api/processors/<id>/config` sets channels). This is exactly what the OE Discord reply described, and it is correct. Source: [OE Record Node docs](https://open-ephys.github.io/gui-docs/User-Manual/Plugins/Record-Node.html).
> - **Allego GUI: ❌** — Radiens manual p29: one Record button, one recording-file name/location → one file, all selected channels.
> - **Allego Python API (radiens v4.0.0): ✅** — `RecordingConfig` field **`split_files_by_port: bool` — "True to create separate files for each port. Defaults to False."** (verbatim). Source: [Radiens RecordingConfig](https://neuronexus.github.io/radiens-core-python/latest/reference/radiens_core/models/status/).
>
> **Q2 — independent START/STOP per animal (different schedules, e.g. mouse A 9am + mouse B 9pm):**
> - **Open Ephys: ❌ GLOBAL.** The only start/stop is `PUT /api/status` mode `RECORD` = whole-GUI mode switch; per-node endpoints are CONFIG only, not start/stop. All Record Nodes start/stop together. Source: [OE Remote-control](https://open-ephys.github.io/gui-docs/User-Manual/Remote-control.html).
> - **Allego GUI: ❌** single global Record button (manual p29).
> - **Allego Python API (radiens v4.0.0): ✅ DOCUMENTED per-port.** **`start_recording(*, port=None)`** / **`stop_recording(*, port=None)`** — verbatim: *"Optional port to start/stop recording on. Accepts Port enum, single-letter string ("a"–"h"), or int (0–7). If omitted, applies system-level control."* Source: [Radiens AllegoClient](https://neuronexus.github.io/radiens-core-python/latest/reference/radiens_core/).
>
> **WARNING — documented ≠ validated on OUR hardware.** Both Allego API wins are radiens v4.0.0 API features. They are **NOT yet bench-tested on our Gen-1 XDAQ Core** (Opal Kelly USB, known crash-on-sensor/channel-churn history). Two things still need a live test on our box: (1) `split_files_by_port` actually writes clean per-port XDAT, (2) `start_recording(port=...)` truly isolates one port's start/stop from the others without disturbing the running ports. Until then, treat as "documented, plausible, unproven here." The GUI-only path (no SDK) stays global on both systems.
>
> **Net:** Open Ephys wins separate-files-natively-in-the-GUI; Allego (via SDK only) potentially wins BOTH per-port files AND per-port timing — the capability our vault previously called impossible. Neither GUI alone does independent scheduling.

---

## 3. Priced 32-mouse bills of materials

> [!note] Price tags
> **PUBLISHED** = list price on the vendor's public page. **QUOTE** = from Kontex quote 262024 (confidential). **ESTIMATE** = our guess where no price is published; flagged so it is never mistaken for a real number. Currencies are as published: Kontex/Intan in USD, Open Ephys in EUR (Open Ephys does NOT publish USD; they invoice USD on request).

### A) XDAQ / NeuroNexus (Kontex)

32 mice = **2× XDAQ ONE+** (16 each) **+ 2× SyncLink** (shared clock) **+ 2 acquisition PCs + 2 Allego licenses** (or $0 if we leave Allego for XDAQ-RHX/OE). MISO physics: ONE+ = 4 MISO pairs/port × 4 ports = 16 headstages ([[intan-rhd-spi-wiring-and-headstage-limits]]).

**Scenario A — isolation-first (Port Expander, one mouse per EXP port):** ONE+ + Port Expander = 4 animals/HDMI port (EXP A-D) × 4 ports = 16 isolated mice/box.

| Item | Part | Unit | Qty | Ext | Tag |
|---|---|---|---|---|---|
| XDAQ ONE+ (1024 spike ch, 4 headstage ports) | ONE+ | ~$18,000-25,000 | 2 | ~$36k-50k | **ESTIMATE** (not published, quote owed) |
| XDAQ Port Expander (isolated ground/ref, one per HDMI port) | XDAQ-Port-EXP | $1,525 | 8 | $12,200 | **QUOTE** |
| Per-mouse Intan/OM12 interface | SAdpt-XDAQ-OM12(1) | $275 | 32 | $8,800 | **QUOTE** |
| ONE+ HDMI → OM12 port bridge (ONE+ analog of SAdpt-CORE-OM12) | (ONE+ bridge) | ~$350 | 8 | ~$2,800 | **ESTIMATE** |
| SyncLink synchronization unit (one per XDAQ) | SyncLink | ~$1,000-2,000 | 2 | ~$2k-4k | **ESTIMATE** |
| Allego/Radiens software license (perpetual, per seat) | — | $2,500-5,000 | 2 | ~$5k-10k | **ESTIMATE** (or **$0** on XDAQ-RHX/OE) |
| Acquisition PC | — | (lab spec) | 2 | — | — |
| RHD2216 headstages | C3313 | (we own 32) | — | $0 reuse | — |
| Commutators / SPI cables | — | ⏳ | 32 | ⏳ | **owed** |
| | | | **Hardware EST** | **~$63k-77k** (+ license + 2 PCs + commutators) | |

**Scenario B — density-first (2 hs/port via splitter, NO Port Expander, shared ground per pair):** drop the 8× Port Expander ($12,200) and the 8× bridge (~$2,800); add dual-headstage adapters. Roughly **$12-15k cheaper**, but this THROWS AWAY the Port Expander, which is XDAQ's one real isolation advantage and the whole reason we are looking at it for the [[eeg-60hz-saga]]. Doing XDAQ without the Port Expander makes little sense for us. If we are going density-first, Intan or Open Ephys are cheaper for the same shared-ground compromise.

**Why XDAQ despite the highest software cost:** it is the ONLY option that reuses our entire Allego / sleep64 / `eeg-emg-analysis` / video-sync-Phase-0a pipeline as-is, it has a PROVEN 72 h byte-perfect endurance run on our own rig, and the Port Expander is the only vendor product that directly answers per-animal ground isolation. Reuse the 32 RHD2216 headstages we already own ($0).

> [!warning] XDAQ price is an ESTIMATE
> The ONE+ unit price and SyncLink price are NOT published by Kontex, they quote on request. The ~$63-77k hardware figure is our estimate. The real Kontex quote for the 16-mouse ONE+ build (let alone 32) is STILL OWED. Quote 262024 ($10,002.89) is only the Port-Expander grounding retrofit for the CURRENT 8-mouse Core, NOT this build.

### B) Open Ephys

32 mice = **4× Acquisition Board** (8 mice each, Scenario B) or **8× Acquisition Board** (4 mice each, Scenario A), synced by routing one TTL trigger to all boards via cheap I/O boards. No sync-box product exists. All prices EUR (USD not published).

**Scenario A — isolation-first (1 hs/port, 4 mice/board → 8 boards):**

| Item | Part | Unit (EUR) | Qty | Ext (EUR) | Tag |
|---|---|---|---|---|---|
| Acquisition Board (3rd gen) | OEPS-9029 | €3,245 | 8 | €25,960 | **PUBLISHED** |
| SPI Headstage 16ch bipolar (RHD2216) | OEPS-6574 | from €780 | 32 | €24,960 | **PUBLISHED** |
| I/O Board (for TTL sync distribution) | — | from €12.50 | ~4-8 | ~€50-100 | **PUBLISHED** |
| Intan SPI cables + any adapters | Intan C-series | not on OE store, buy from Intan | 32 | see Intan §C | **not published (OE)** |
| Open Ephys GUI software | — | €0 | — | €0 | **PUBLISHED (free)** |
| | | | **Subtotal** | **~€51,000+** (+ cables) | |

CAVEAT: even Scenario A on Open Ephys may NOT give true per-animal isolation, since the board's 4 ports are not confirmed galvanically isolated from each other. Its isolation story is the weakest of the three.

**Scenario B — density-first (2 hs/port, 8 mice/board → 4 boards):**

| Item | Part | Unit | Qty | Ext | Tag |
|---|---|---|---|---|---|
| Acquisition Board (3rd gen) | OEPS-9029 | €3,245 | 4 | €12,980 | **PUBLISHED** |
| SPI Headstage 16ch bipolar (RHD2216) | OEPS-6574 | from €780 | 32 | €24,960 | **PUBLISHED** |
| Intan dual-headstage adapter (splitter) | C3442 | $345 (Intan) | 16 | ~$5,520 | **PUBLISHED (Intan)** |
| I/O Board (sync) | — | from €12.50 | ~4 | ~€50 | **PUBLISHED** |
| Software | — | €0 | — | €0 | **free** |
| | | | **Subtotal** | **~€38,000+** (+ cables) | |

Notes: The `extension-board` single-board route to 16/board is DEAD (unfinished prototype, vendor disowns it, "this is not a finished or tested design yet!"). Open Ephys's real upside = $0 software + open hardware + the Atlanta custom-design team (could quote a custom 16-headstage board). Its downsides for us = weakest isolation, homebrew multi-board sync with clock-drift risk over multi-day runs, and a full pipeline rebuild off Allego.

### C) Intan direct

32 mice = **4× RHD 1024ch Recording Controller (C3008)**, 8 SPI ports each × 1 hs/port = 32 isolated ports. Ports are individually isolated by design, so Scenario A gives GENUINE per-animal isolation with no add-on. All prices PUBLISHED on intantech.com/pricing.html.

**Scenario A — isolation-first (1 hs/port, full per-animal isolation) — RECOMMENDED for isolation:**

| Item | Part | Unit | Qty | Ext | Tag |
|---|---|---|---|---|---|
| RHD 1024ch Recording Controller (8 ports, incl USB + power cord) | C3008 | $14,250 | 4 | $57,000 | **PUBLISHED** |
| RHD 16ch bipolar headstage (RHD2216) | C3313 | $820 | 32 | $26,240 | **PUBLISHED** |
| RHD 6ft (1.8 m) ultra-thin SPI cable | C3216 | $595 | 32 | $19,040 | **PUBLISHED** |
| RHX acquisition software | — | $0 | — | $0 | **PUBLISHED (free)** |
| | | | **TOTAL (1.8 m reach)** | **≈ $102,280** | |
| Add: 3ft ultra-thin cable, daisy-chained for ~2.7 m reach | C3213 | $415 | 32 | +$13,280 | **PUBLISHED** |
| | | | **TOTAL (~2.7 m reach)** | **≈ $115,560** | |

Options: swap C3313 → **C3323 ($880)** for an onboard 3-axis accelerometer (posture/movement for sleep staging), +$1,920 total. Standard (non-ultra-thin) 6ft cable C3206 = $295 saves $300/mouse (−$9,600) but is heavier on a tethered mouse. Optional electrode breakout: C3410 electrode adapter board ($255) or C3420 wire adapter ($230) per mouse.

**Scenario B — density-first (2 hs/port via C3442, shared ground per pair):**

| Item | Part | Unit | Qty | Ext | Tag |
|---|---|---|---|---|---|
| RHD 1024ch Recording Controller | C3008 | $14,250 | 2 | $28,500 | **PUBLISHED** |
| RHD dual-headstage adapter | C3442 | $345 | 16 | $5,520 | **PUBLISHED** |
| RHD 16ch bipolar headstage | C3313 | $820 | 32 | $26,240 | **PUBLISHED** |
| SPI cables (6ft ultra-thin) | C3216 | $595 | ~16-32 | ~$9.5k-19k | **PUBLISHED** |
| Software | — | $0 | — | $0 | **free** |
| | | | **TOTAL** | **≈ $79,000** | |

> [!warning] Intan's biggest risk = multi-controller sync
> 4× C3008 = 4 USB3 connections. Intan RHX historically runs ONE controller per software instance. Synchronizing 4 controllers needs shared sample-clock / digital-in wiring or separate acquisition PCs, and is NOT confirmed for our case. CONFIRM multi-controller synchronization with Intan (support@intantech.com) BEFORE committing. Lead times not published (~2-6 wk estimate; controllers likely longer for a 4-unit batch).

Note: the smaller RHD USB Interface Board (C3100, 256ch, 4 ports = 8 mice) is DISCONTINUED (Feb 2022) and caps at 8 mice anyway. Not viable for 32.

### Rough 32-mouse cost ranking (hardware, same-scenario)

| Scenario | Open Ephys | Intan | XDAQ |
|---|---|---|---|
| **A (isolation, 1 hs/port)** | ~€51k+ (but weak real isolation) | **~$102-116k** (true isolation) | **~$63-77k EST** (true isolation via Port Expander) + license + 2 PCs |
| **B (density, 2 hs/port, shared ground)** | **~€38k+** (cheapest) | ~$79k | XDAQ-without-PortExp not sensible for us |

Read carefully: Open Ephys is cheapest on paper but buys the weakest isolation and a homebrew sync; Intan is the priciest but buys turnkey boxes and genuine port isolation; XDAQ sits in the middle on hardware but adds license + 2-PC cost AND is the only one that reuses our whole software pipeline. Cheap hardware that forces a pipeline rebuild is not actually cheap.

---

## 4. What is still owed (to fully close the table)

**XDAQ / Kontex:**
- ⏳ Real quote for the **16-mouse ONE+ build** and the **32-mouse plan** (2× ONE+ + 2× SyncLink + Port Expanders + OM12 interfaces + commutators/cables). The ONE+ and SyncLink unit prices above are ESTIMATES.
- ⏳ Confirm the ONE+ HDMI → Port Expander bridge adapter part + price (the ONE+ analog of SAdpt-CORE-OM12).
- ⏳ Confirm Port Expander accepts our Intan RHD2216 (via SAdpt-XDAQ-OM12 / Omnetics), not only Kontex XR headstages.

**Open Ephys:**
- ⏳ USD pricing (store lists EUR only; they invoice USD on request).
- ⏳ Whether the acquisition board's 4 ports are galvanically isolated from each other (decides if Scenario A gives any real per-animal isolation).
- ⏳ Multi-day continuous reliability references for 4 synced boards; clock-drift magnitude over 72 h.
- ⏳ Atlanta custom-team scope + price for a 16-headstage board.
- ⏳ Independent per-mouse/subset record start-stop (native vs GUI API/SDK).

**Intan:**
- ⏳ **Multi-controller synchronization for 4× C3008** (the biggest design risk) — confirm with support@intantech.com.
- ⏳ Lead times for a 4-controller / 32-headstage batch; name a Korea/KAIST distributor for import + VAT.

---

## 5. Current reading (NOT the final decision)

- **If per-animal isolation is the priority** (and given the [[eeg-60hz-saga]], it is), the honest options are **Intan Scenario A** (~$102-116k, genuine port isolation, turnkey boxes, but confirm 4-controller sync) or **XDAQ Scenario A** (~$63-77k EST + license + 2 PCs, Port Expander isolation, PROVEN 72 h endurance, full pipeline reuse). Open Ephys does NOT credibly deliver per-animal isolation at any price, so it drops out when isolation is the deciding axis.
- **If budget/density is the priority and shared-ground-per-pair is acceptable for bipolar**, the cheapest real build is **Open Ephys Scenario B (~€38k+)** or **Intan Scenario B (~$79k)**. XDAQ without the Port Expander is not sensible (you pay the Allego premium for nothing).
- **XDAQ's decisive non-price edge** = it reuses our ENTIRE existing pipeline (Allego, sleep64 map, `eeg-emg-analysis` XDAT reader, impedance workflow, video-sync Phase 0a) and has the only proven multi-day endurance record on our own hardware. Every other path forces a pipeline rebuild.
- **DECISION GATE:** do NOT decide until (a) the real Kontex ONE+ quote lands (replaces the XDAQ estimate), (b) Intan confirms 4-controller sync, and (c) Open Ephys answers USD + port isolation. THEN take the DAQ/software choice to a **council**. And remember: this whole scale-up is still gated behind **surgical yield** (open frontal electrodes) — no acquisition box fixes an open electrode ([[eeg-60hz-saga]]). Buy the box that fits the science, after the science works.

## Related
- [[2026-07-23-daq-ecosystem-comparison-xdaq-vs-openephys]] (superseded predecessor) · [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] · [[2026-07-21-openephys-acquisition-board-scale-up-option]] · [[openephys-inquiry-email]]
- [[intan-rhd-spi-wiring-and-headstage-limits]] · [[kontex-xdaq-hardware-reference]] · [[eeg-60hz-saga]] · [[project_multiuser_recording_schedules]]

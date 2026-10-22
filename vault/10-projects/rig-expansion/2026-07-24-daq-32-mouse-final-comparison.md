---
type: decision
area: rig-expansion
status: active
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
updated: 2026-07-28
supersedes: "[[daq-ecosystem-comparison-xdaq-vs-openephys]]"
---
# DAQ Ecosystem Comparison, FINAL, 3-Way for 32 Mice — XDAQ vs Open Ephys vs Intan

> [!warning] 🔴 CORRECTION 2026-09-30 — our Gen-1 XDAQ Core DOES have a chassis GND terminal
> Andrea confirmed on the rig on 2026-09-30 that the Gen-1 Core has a chassis GND, and that it is wired to the building earth through the wall socket (continuity tested with a DMM; see [[2026-09-30-xdaq-noise-series]]). Every line on this page saying the Gen-1 has "no Chassis GND" or "no chassis ground terminal" is **wrong**. What the 07-15/16 work MEASURED still stands (foil cut the mains floor; the residual hum tracked electrode impedance). What rested on "there is nothing to wire" does not. Still unverified: whether a separate Sys GND exists on the Gen-1 and how it relates to chassis.

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[_rig-expansion-hub]]** (decision, vendor correspondence, wiring, open items).

> [!warning] CONFIDENTIAL PRICING, VAULT-ONLY
> Contains Kontex quote 262024 pricing (do-not-publicly-disclose clause), plus Open Ephys and Intan list prices. Keep inside the vault. DO NOT publish as a web Artifact, paste into a public repo, or share the pricing outside the lab.

> [!danger] REVISED 2026-07-28 — FOUR GROUND RULES CHANGED, READ THIS FIRST
> Andrea reset the scope of this comparison. The 2026-07-24 version is superseded by the rules below, and the conclusions moved as a result.
>
> 1. **NO Allego/Radiens license will be purchased.** All three ecosystems get driven by the **Open Ephys GUI**, which is free and which Kontex officially supports on XDAQ. Software cost is now **$0 on every column** and stops being a comparison axis at all.
> 2. **The comparison is priced for a COMPLETE 32-mouse rig**, not just the acquisition box: headstages, SPI cables, commutators, adapters, tether hardware, sync wiring, PC and storage.
> 3. **Does each XDAQ need its own PC?** Answered below (§2.3): **almost certainly NO.** The 2-PC line in the old version was an Allego-licensing artifact, not a hardware requirement.
> 4. **Our own software is EXCLUDED from the evaluation.** The daemon, `eeg-emg-analysis`, the sleep64 map, the XDAT reader, the Frigate video pipeline: none of it scores. Code can be rewritten, a rig cannot. Anything code-related below is marked NON-SCORING and is there only so we know what work follows the purchase.
>
> **What moved because of these rules:** XDAQ lost its single biggest advantage (pipeline reuse was worth a lot and is now worth zero), but also lost its single biggest cost (the license) and half its PC cost. Open Ephys lost its "free software" advantage, because now everybody has free software. Multi-box sync stopped being a differentiator, because under one GUI all three sync the same way. What is LEFT standing is a much shorter list, and it is dominated by **per-animal ground isolation** and **cost of the complete tether chain**.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The head-to-head for the acquisition box (the DAQ) driving our next rig, scaled to **32 mice recorded at once** (one mouse = one Intan RHD2216 bipolar headstage). Three ecosystems: **XDAQ / KonteX** (what we already run), **Open Ephys** (open hardware), and **Intan direct** (the company making the amplifier chips all three use).
> **The big finding, unchanged.** A splitter (dual-headstage adapter) really does put **two SEPARATE animals on one port**. The catch is that those two animals then sit in the same ground domain. (We place the splitter at the XDAQ port, so each animal still gets its own cable; what they share is the port's ground node, not a wire.) For our BIPOLAR recordings that shared ground is mostly cancelled by the amplifier, so it is tolerable. So every ecosystem has two cost scenarios: **isolation-first** (one mouse per port, pricier) and **density-first** (two per port, cheaper, shared ground).
> **The NEW big finding.** Once you stop paying for Allego and price the WHOLE rig, **the acquisition box is no longer the dominant cost.** The per-mouse tether chain (commutator plus cables) is. A premium commutator at ~€2,600 each times 32 mice is roughly €83,000, which is more than any of the three DAQ options costs. That single line item deserves more attention than the DAQ choice does, and it is IDENTICAL across all three ecosystems, so it does not change the ranking, only the budget.
> **The NEW big loss.** Dropping Allego kills the only documented way to start and stop each mouse on its own schedule. See the warning in §2.4. If independent per-user recording schedules matter, that is the price of the decision, and it should be a conscious one.
> **How to read it.** §1 = the port/isolation finding. §2 = the master table plus the four questions Andrea raised. §3 = complete priced parts lists, split into DAQ block, per-mouse tether block, and shared infrastructure. §4 = what is still owed. §5 = current reading.

> [!quote] Paper-ready
> Three acquisition ecosystems were costed for a chronic 32-animal mouse EEG/EMG rig, all interfacing the same Intan RHD2216 bipolar amplifier over SPI and all operated under the open-source Open Ephys GUI: the XDAQ system (KonteX), the Open Ephys Acquisition Board, and the Intan RHD Recording Controller. Because one RHD chip occupies one SPI MISO data line irrespective of channel count, animal capacity is set by MISO-line count, not channel count. A dual-headstage adapter placed at the acquisition port drives two independent chips over the port's two MISO lines, each on its own interface cable, permitting two separate animals per port at the cost of a common port-level ground and reference domain; for differential bipolar montages this shared ground is rejected as common mode, so per-port headstage doubling is electrically acceptable, whereas port-level galvanic isolation of each headstage preserves true per-animal grounding at higher hardware cost. With acquisition software held constant and free across all three systems, the dominant capital cost of the complete rig is the per-animal tether chain (commutator and SPI cabling) rather than the acquisition hardware itself.

Companion docs: [[daq-ecosystem-comparison-xdaq-vs-openephys]] (16-mouse 2-way predecessor, superseded), [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] (XDAQ/Kontex thread + quote 262024), [[2026-07-21-openephys-acquisition-board-scale-up-option]], [[openephys-inquiry-email]], [[intan-rhd-spi-wiring-and-headstage-limits]] (MISO physics), [[kontex-xdaq-hardware-reference]], [[eeg-60hz-saga]] (the grounding history that makes isolation matter).

---

## 1. The two-headstages-per-port question, SETTLED

This was the confusing bit in Margarida's Open Ephys reply. She framed the dual-headstage adapter as "two headstages in the SAME animal," and therefore called the board "a maximum of four animals." Andrea's read was that the splitter gives two SEPARATE animals. **Andrea is right, with one grounding caveat.** Straight from Intan's SPI cable and dual-headstage-adapter datasheets (transcribed in [[intan-rhd-spi-wiring-and-headstage-limits]]).

**The data side (good news):**
- An Intan RHD SPI cable carries 5 LVDS twisted pairs: CS, SCLK, MOSI, **MISO1, MISO2**. Two data-return lines.
- The dual-headstage adapter (Intan **C3442**) wires each chip's data output to its OWN MISO line. MISO1 and MISO2 are electrically independent, each with its own termination resistor in the FPGA.
- Two chips on one cable = **two independent data streams**, sampled on the SAME clock (perfectly time-aligned), appended in software as separate channel blocks. NOT two headstages fused into one stream on one animal. Intan's "128 channels on one animal" example is a USE-CASE CONVENTION (high-density probes), not an electrical rule.
- CONCLUSION: two separate animals per port is real. The "same animal only / max 4 animals" framing was **grounding conservatism, not a hardware limit** — and ✅ **Open Ephys confirmed this in writing on 2026-07-28**: *"if your current setup is working reliably and you have not experienced any issues using the dual headstage adapter that way, I don't see a reason why you should not continue using it."* **One board = 8 separate mice.**

**The grounding side (the caveat):**
> [!warning] CORRECTED 2026-07-28 — where the splitter physically sits changes the mechanism
> Earlier versions of this note said the two animals "share one SPI cable" and therefore its single ground conductor. **That describes Intan's canonical placement of the C3442, at the animal end with one long cable running back to the controller. It is NOT how we build it.**
>
> **We put the splitter at the XDAQ port, so each animal has its own SPI cable.** (Our SAdpt-XDAQ-OM12 already does exactly this at the box, presenting two Omnetics sockets, P1 and P2.) There is **no shared cable and no shared return conductor between the two animals**, and therefore none of the shared-return coupling that would imply.
>
> **The isolation conclusion is unchanged, but the mechanism is different:** both cables' grounds originate at the **same XDAQ port ground node**, so the two animals still sit in one common ground/reference domain. That domain is precisely what the Port Expander subdivides.

- On the RHD chip, the cable ground IS the system reference. Two animals on one XDAQ port therefore sit in **one common ground/reference domain**, even with separate cables. That is the inter-animal coupling we fight in [[eeg-60hz-saga]].
- Severity is **lower than the shared-cable case** (separate return conductors, so no common-return IR drop between the two animals) but it is still **not isolation**.
- BUT our montage is **bipolar RHD2216**: every channel is a true differential pair (independent in+ and in- electrodes, both on the same animal). A shared system ground appears as COMMON MODE and is largely rejected (RHD2216 balanced inputs, CMRR ~82 dB at 50/60 Hz WHEN electrode impedances are matched). For us the shared ground is TOLERABLE.
- WARNING: holds for bipolar ONLY. On monopolar chips (RHD2132/2164) every channel is measured against that shared reference, so two animals on one port cross-contaminate. Do NOT do two-per-port on monopolar.
- WARNING: "tolerable" is not "isolated." A real galvanic tie remains between the two animals, ground artifact couples into both as common mode (rejected, not infinitely), and matched-impedance CMRR collapses the moment one electrode goes open, which is precisely our frontal-electrode failure mode. If a run is fighting hum, one-per-port is the safer topology.

**So every ecosystem gets TWO scenarios:**

| | **Scenario A — isolation-first** | **Scenario B — density-first** |
|---|---|---|
| Headstages per SPI port | 1 | 2 (via C3442 splitter) |
| Ports needed for 32 mice | 32 | 16 |
| Per-animal ground | dedicated per mouse | shared within each pair |
| Good for | fighting 60 Hz, open-electrode risk, monopolar | bipolar, budget, port-count-limited |
| Cost | higher (more boxes/ports) | lower (half the ports) |

**Isolation is NOT equal across the three, even in Scenario A** — the make-or-break nuance, and now the single most important row in the whole document:

| Ecosystem | TRUE per-animal isolation in Scenario A? | Mechanism |
|---|---|---|
| **Intan Recording Controller** | ✅ YES, built in | Each SPI port is "electrically isolated from the controller and from earth ground" (Intan User Guide, verbatim). One mouse per port = one isolated ground domain per mouse. No add-on, no extra cost. |
| **XDAQ / KonteX** | ✅ YES, via paid add-on | **Port Expander (XDAQ-Port-EXP)** gives "isolated and dedicated electrical systems to each connected headstage... ground and reference nodes from each animal's headstage do not interfere." $1,525 each. ⚠️ NEW OPEN ITEM: confirm the Port Expander is exposed and usable under the **Open Ephys GUI plugin**, not only under Radiens (§4). |
| **Open Ephys** | ⚠️ WEAKEST | NO isolation product exists ("depends on your design," docs and Discord only). The board's ports are NOT confirmed galvanically isolated from each other, so even one-per-port may share the board's common ground. Its 4 ports likely sit in one ground domain. |

That last row is the single biggest strike against Open Ephys hardware for OUR rig, given [[eeg-60hz-saga]]. Note the irony introduced by the no-Allego decision: we will run **Open Ephys SOFTWARE** on top of hardware chosen partly because it is **not Open Ephys HARDWARE**. Those are separate purchases and separate arguments, and conflating them would be a mistake.

---

## 2. Master 3-way comparison (scoped to 32 mice, Open Ephys GUI everywhere)

### 2.1 What still counts, and what got struck

With Allego gone and our code excluded, several rows from the 2026-07-24 version no longer decide anything. Kept below for transparency, struck through, marked NON-SCORING.

| Struck row | Why it no longer scores |
|---|---|
| ~~Software license cost~~ | $0 on all three now. Dead axis. |
| ~~Reuses our Allego pipeline (sleep64, `eeg-emg-analysis`, XDAT)~~ | Our code, excluded by rule 4. Also moot: leaving Allego means rebuilding regardless of which box we buy. |
| ~~Video-sync Phase 0a already scoped~~ | Our code plus a wiring job. The wiring (a TTL out to the Pi cameras) exists on all three boxes. NON-SCORING. |
| ~~One PC or many~~ | Was an Allego-license artifact. See §2.3, it collapses to "one PC, probably, for all three." |

### 2.2 The surviving table

Legend: ✅ confirmed strength · ⚠️ conditional · ❌ confirmed gap · ⏳ still owed (§4).

| # | Dimension (all scoring, all rig-level) | **XDAQ / KonteX** | **Open Ephys** | **Intan direct** |
|---|---|---|---|---|
| 1 | **Animals per single box** (1 hs/mouse) | Core **8**, ONE+ **16** | Acq Board **8** (4 ports × 2) | C3004 **8**, C3008 **16** (8 ports × 2) |
| 2 | **Boxes to hit 32** | **2** (ONE+) | **4** (Scen. B) / **8** (Scen. A) | **4** (Scen. A) / **2** (Scen. B) |
| 3 | **Per-animal ground isolation** (our 60 Hz wall) | ✅ Port Expander, paid add-on, ⏳ OE-GUI support unconfirmed | ❌ no product, ports not confirmed isolated | ✅ **port-level isolated by design, included** |
| 4 | **RHD2216 bipolar support** | ✅ (SAdpt-XDAQ-OM12 path) | ✅ vendor-confirmed, "optimal for EMG/EEG" | ✅ native (Intan's own chip) |
| 5 | **Open Ephys GUI support** | ✅ **officially supported, free**, Gen1 and Gen2, plugin via Plugin Installer (kontex.io/software) | ✅ native, it is their GUI | ✅ via the Rhythm/Intan source plugin |
| 6 | **Adapter chain depth per mouse** (fewer = fewer failure points) | **deepest**: HDMI → SAdpt-CORE/ONE+-OM12 → Port-EXP → SAdpt-XDAQ-OM12 → RHD2216 | shallow: board port → OE SPI cable → OE headstage | **shallowest**: controller port → Intan SPI cable → RHD2216. No adapters. |
| 7 | **Multi-box clock sync under OE GUI** | ⚠️ equalized (see §2.5); SyncLink exists but ⏳ unconfirmed under OE | ⚠️ equalized | ⚠️ equalized |
| 8 | **Host interface** | **Thunderbolt 3** (60 W bus-powered on ONE+) | USB 3 | USB 3 |
| 9 | **Long-run reliability (24-72 h)** | ✅ **PROVEN on our rig** (72 h byte-perfect, Gen-1 Core under Allego) ⚠️ that proof is under Allego, not under the OE plugin | ⏳ multi-board multi-day track record unknown to us | ⏳ unknown to us at 4-controller scale |
| 10 | **Price transparency** | ❌ quote-only, ONE+ price STILL not quoted | ✅ public store, EUR only | ✅ fully published USD list |
| 11 | **Independent per-mouse record: separate FILE / independent START-STOP** | file ✅ (OE Record Nodes) · start-stop ❌ **global** | file ✅ · start-stop ❌ **global** | file ✅ · start-stop ❌ **global** |
| 12 | **32-mouse DAQ-block price** (box + isolation + adapters, Scen. A, excludes headstages/tether) | **EST ~$51-65k** (ONE+ price is a guess) | **~€27k** (weak isolation) | **$57,000** (published, true isolation) |
| 13 | **Openness / customization** | closed, productized | **open hardware** + Atlanta custom team | closed, productized |
| 14 | **Korea import / distributor** | ⏳ (Kontex quotes us directly, USD) | ⏳ EUR invoicing, USD on request | ⏳ no named KAIST distributor yet |

Row 11 collapsed to a single answer across all three columns. That is the direct consequence of dropping Allego, and it deserves its own warning.

### 2.3 Andrea's question: does every XDAQ need its own PC?

**Almost certainly NO, and the old "2 PCs" line was an Allego artifact.**

The reasoning, source by source:

- The 2-PC claim came from the Kontex call: a second XDAQ meant a second **Allego license**, seat-based. That is a SOFTWARE-LICENSING statement, not a hardware one. Remove Allego and the reason evaporates.
- The Open Ephys GUI explicitly supports **multiple acquisition devices in one GUI instance on one PC**: you add one source node per board and each binds to a different device. Verbatim from the Open Ephys developers: *"you can add two Rhythm nodes to the Open Ephys GUI and each will use a different board."* ([Open Ephys forum thread](https://groups.google.com/g/open-ephys/c/Cz0YjSBm494))
- The XDAQ plugin is an Open Ephys **source plugin**, so it inherits that architecture. ⏳ NOT yet confirmed that the XDAQ plugin specifically enumerates and binds two XDAQ devices cleanly. This is the one thing to ask Kontex (§4). It is a plugin question, not a physics question.

Three real caveats, all solvable:

1. **Board identity is arbitrary.** Verbatim: *"Board order is somewhat arbitrary, as it depends on some USB descriptors."* You must verify which source node maps to which physical box BEFORE every recording, or mouse identities silently swap. For a 32-animal chronic study that is a data-integrity hazard, and it needs a written pre-run check in the SOP.
2. **The two boxes are asynchronous.** Verbatim: *"The two boards will act as independent, asynchronous devices. Their internal clocks are not synchronized."* Fixed by a shared TTL sync line, see §2.5.
3. **Host ports.** XDAQ is **Thunderbolt 3**, so two ONE+ boxes need two TB3 ports on the acquisition PC, each supplying up to 60 W. That is a real spec to check when buying the PC, and TB3 ports are scarcer than USB3 ports. Intan and Open Ephys use USB3, which is easier.

**Bandwidth is not a constraint for one PC.** 32 mice × 16 ch = 512 channels, 2 bytes per sample:

| Sample rate | Throughput | Per day | 72 h run |
|---|---|---|---|
| 30 kS/s | 30.7 MB/s | 2.65 TB | ~8.0 TB |
| 20 kS/s | 20.5 MB/s | 1.77 TB | ~5.3 TB |
| 1 kS/s (RHD minimum) | 1.0 MB/s | 88 GB | ~265 GB |

One modern PC on an NVMe drive handles any of these. **Storage, not bandwidth, is the real design question**, and it is the same for all three ecosystems. For sleep scoring we do not need 30 kS/s on EEG; dropping the acquisition rate is worth a deliberate decision, because it is a 30x storage difference. (Caveat: EMG benefits from higher rates than EEG, and the RHD samples all channels at one global rate, so the rate is set by the EMG requirement, not the EEG one.)

**Answer: budget ONE acquisition PC, for any of the three.** Confirm the XDAQ plugin's multi-device support before committing to a 2-box XDAQ build.

### 2.4 The cost of dropping Allego: independent per-mouse start/stop is GONE

> [!danger] This is the real price of the no-Allego decision, and it is a RIG-level capability, not a code problem
> Two capabilities that get confused constantly:
> - **Q1 = FILE SEPARATION.** Do animals land in separate files? (data layout)
> - **Q2 = INDEPENDENT RECORDING CONTROL.** Can you start and stop each animal on its OWN schedule (mouse A at 9am, mouse B at 9pm) without disturbing the others? (timing)
>
> | System | Q1: separate file per animal | Q2: independent start/stop per animal |
> |---|---|---|
> | **Open Ephys GUI** (our new universal front end) | ✅ Record Nodes, per-animal directory and channel selection | ❌ **GLOBAL.** One Record button drives every node. |
> | ~~Allego radiens Python API~~ (NOT BEING PURCHASED) | ~~✅ `split_files_by_port`~~ | ~~✅ `start_recording(port=...)`~~ |
>
> The radiens Python API was the **ONLY documented per-animal start/stop across all three ecosystems**, and it dies with the license. Under the Open Ephys GUI, on ANY of the three boxes, **recording start and stop is global.** Verbatim from the OE docs: the only start/stop is `PUT /api/status` with mode `RECORD`, a whole-GUI mode switch; the per-node endpoints are CONFIG only. ([OE Remote-control docs](https://open-ephys.github.io/gui-docs/User-Manual/Remote-control.html), [OE Record Node docs](https://open-ephys.github.io/gui-docs/User-Manual/Plugins/Record-Node.html))
>
> **What this means operationally for a 32-mouse multi-user rig:** if user 1 wants mouse 1-8 recorded Monday and user 2 wants mouse 9-16 recorded Wednesday, you cannot serve both independently. Options, all of them rig-level:
> - **Record everything continuously and slice offline per user.** Simplest, and it is what the storage table above should be sized for. At 1 kS/s this is cheap (~88 GB/day for all 32); at 30 kS/s it is 2.65 TB/day and needs a serious array.
> - **Batch users onto a common schedule.** Administrative, free, annoying.
> - **Physically split into independent rigs** (separate boxes on separate PCs running separate GUI instances), which restores independent start/stop at the cost of a second PC and losing cross-rig sync. This is the ONE case where "a PC per box" would actually buy something.
>
> **Recommendation: accept it and record continuously at a modest sample rate.** But it should be an explicit decision, not a surprise discovered after the purchase order. Also worth one email: ask Open Ephys whether per-Record-Node start/stop is on their roadmap (§4). This overturns [[project_multiuser_recording_schedules]], which was written on the assumption that we would keep Allego.

### 2.5 Multi-box sync is now EQUALIZED, and better than we thought

The old version scored XDAQ up for **SyncLink** and scored Open Ephys down for "homebrew multi-board sync with clock-drift risk." Under one GUI both of those judgements soften considerably.

The Open Ephys GUI does **online, automatic** stream synchronization inside the Record Node, using a shared hardware sync line ([OE Data-Synchronization docs](https://open-ephys.github.io/gui-docs/Tutorials/Data-Synchronization.html)):
- All devices share ONE digital sync line carrying regular pulses (at least one every 30 s recommended).
- The GUI detects low-to-high transitions per stream and **recomputes relative sample rates every 10 seconds**, so it tracks drift continuously rather than assuming a fixed offset.
- Stated tolerance when properly configured: **well below 1 ms.**

Sub-millisecond is far tighter than sleep-staging needs (4 s or 10 s epochs), and it is achieved with a TTL line rather than a proprietary sync box. So:

- **This is not homebrew.** It is a documented, supported, first-class GUI feature, and it works the same on XDAQ, Open Ephys and Intan boxes.
- **SyncLink becomes optional** rather than a decisive XDAQ advantage. It may still deliver a genuinely shared hardware clock (better than software resampling), but ⏳ whether the OE plugin exposes it is unconfirmed, and we do not need it for sleep.
- **The same TTL line also serves the video sync** we already scoped for the cameras. One pulse train, fanned out to every DAQ box and every Pi. That simplifies the wiring rather than complicating it. (The Frigate-side implementation is NON-SCORING, but the BNC and buffer hardware is in the BOM at §3.3.)

Caveat worth stating: the OE docs' <1 ms figure is a same-family claim; the sentence *"synchronization in software is accurate to within a few milliseconds, but is not precise enough for synchronizing electrophysiological signals acquired at tens of kilohertz"* also appears in their material and refers to sample-level alignment. For spike-timing work across boxes that distinction matters. For sleep EEG/EMG it does not.

---

## 3. Complete 32-mouse rig, priced

> [!note] Price tags
> **PUBLISHED** = list price on the vendor's public page (pulled 2026-07-28). **QUOTE** = Kontex quote 262024 (confidential). **ESTIMATE** = our guess where nothing is published, flagged so it is never mistaken for a real number. Currencies as published: Kontex and Intan USD, Open Ephys EUR (they invoice USD on request).

The rig splits into three blocks. **Only Block 1 differs between ecosystems.** Blocks 2 and 3 are essentially identical, which is exactly why they were the missing piece: they are large, and they were previously invisible.

### 3.1 BLOCK 1 — the DAQ block (differs by ecosystem)

**Scenario A, isolation-first, 32 independent ports.**

**A) XDAQ / KonteX**

2× XDAQ ONE+ (16 mice each) + Port Expanders for per-animal isolation. ONE+ = 4 MISO pairs/port × 4 HDMI ports = 16 headstages ([[intan-rhd-spi-wiring-and-headstage-limits]]). With a Port Expander per HDMI port you get 4 isolated animals per port × 4 ports = 16 isolated mice per box.

| Item | Part | Unit | Qty | Ext | Tag |
|---|---|---|---|---|---|
| XDAQ ONE+, **1024ch tier — must be R1024, NOT R512** | **ONE-R1024-SR64** | ~$18,000-25,000 | 2 | ~$36k-50k | **ESTIMATE** (quote still owed) |
| Port Expander (isolated ground/ref per animal), 4 per box | SAdpt-Port-EXP | $1,525 | 8 | $12,200 | **QUOTE** |
| Per-mouse Intan/OM12 interface (⏳ only if PE drives Intan) | SAdpt-XDAQ-OM12(1) | $275 | 32 | $8,800 | **QUOTE** |
| KonteX HDMI cable, XDAQ port → Port Expander | KonteX | ⏳ | 8 | ⏳ | **owed** — non-KonteX cables can DAMAGE the system |
| ~~ONE+ HDMI → Port-EXP bridge~~ | — | — | 0 | **$0** | **REMOVED** — docs show a plain KonteX HDMI cable, no bridge adapter |
| ~~Allego/Radiens license~~ | — | **$0** | — | **$0** | **DROPPED, using OE GUI** |
| SyncLink | SyncLink | ⏳ | 0-2 | $0 (omitted) | **OPTIONAL**, superseded by TTL sync (§2.5) |
| | | | **Block 1** | **~$57k-71k** | |

> [!danger] Verified 2026-07-28 against Kontex docs — see [[xdaq-32-mouse-wiring-and-channel-law]]
> - **32 mice on XDAQ is 2 boxes, always.** No model reaches 32 in one box, and the SPI splitter cannot exceed a box's ceiling (three independent blocks; see that note §4).
> - **Max animals = XR recording channels ÷ 64.** CORE2 512→8 (exactly our current rig), ONE+ R512→8, **ONE+ R1024→16**, AIO→16. Our 16-channel RHD2216 still burns a full 64-channel slot; 60 of 64 channels per mouse are structurally wasted.
> - ⚠️ **ORDERING TRAP: ONE+ ships in a 512ch tier that records only 8 mice**, same as the Core we own. Headstage ports are licence-gated ("other ports may be unavailable depending on the license purchased"). The part must read **R1024**.
> - ✅ **RESOLVED 2026-07-28 — KC Kong confirms Intan headstages CAN be used with the Port Expander.** The doc's compatibility table lists only KonteX XR headstages, but the vendor says otherwise. **The XDAQ column is un-blocked**: per-animal isolation reaches our animals, and we do not have to buy 32 KonteX headstages. Exact part-by-part chain to be pinned down on the 2026-07-29 call ([[2026-07-29-kontex-kc-call-prep-rig-finalization]]).
> - ✅ **The ONE+ has Sys GND + Chassis GND 4 mm terminals** and Kontex documents bonding them to ground a Faraday cage. Our Gen-1 Core has no such terminal, which is why foil grounding was abandoned on 2026-07-16 ([[eeg-60hz-saga]]).

**B) Open Ephys**

8× Acquisition Board at 4 mice each (1 hs/port). Note the board price rose since the 2026-07-24 pull: €3,245 → **€3,385**.

| Item | Part | Unit (EUR) | Qty | Ext (EUR) | Tag |
|---|---|---|---|---|---|
| Acquisition Board (3rd gen) | OEPS-9029 | €3,385 | 8 | €27,080 | **PUBLISHED** |
| I/O Board (TTL sync distribution) | OEPS-IO Board | from €13 | 8 | ~€104 | **PUBLISHED** |
| Per-animal isolation hardware | — | **does not exist** | — | — | ❌ |
| Open Ephys GUI | — | €0 | — | €0 | **free** |
| | | | **Block 1** | **~€27,200** | |

CAVEAT: even Scenario A here may NOT give true per-animal isolation, since the board's 4 ports are not confirmed galvanically isolated from each other. Cheapest box, weakest answer to the problem that motivated the whole exercise.

**C) Intan direct**

4× RHD 1024ch Recording Controller (C3008), 8 SPI ports each × 1 hs/port = 32 isolated ports. Ports are individually isolated by design, so Scenario A gives GENUINE per-animal isolation with **no add-on and no adapter chain**. All prices PUBLISHED on intantech.com/pricing.html.

| Item | Part | Unit | Qty | Ext | Tag |
|---|---|---|---|---|---|
| RHD 1024ch Recording Controller (8 isolated ports, incl. USB + power cord) | C3008 | $14,250 | 4 | $57,000 | **PUBLISHED** |
| Isolation add-on | — | **not needed, built in** | — | $0 | ✅ |
| Adapters | — | **none needed** | — | $0 | ✅ |
| Open Ephys GUI (or Intan RHX, also free) | — | $0 | — | $0 | **free** |
| | | | **Block 1** | **$57,000** | |

**Block 1, Scenario B (density-first, 2 hs/port, shared ground per pair):** halve the box count. Intan drops to 2× C3008 = $28,500 plus 16× C3442 splitter at $345 = $5,520, so **~$34,000**. Open Ephys drops to 4 boards = €13,540 plus 16× C3442 ~$5,520, so **~€18,500**. XDAQ Scenario B means dropping the Port Expanders, which throws away XDAQ's only isolation advantage; if we are going density-first, XDAQ stops making sense and the choice is Intan vs Open Ephys.

### 3.2 BLOCK 2 — the per-mouse tether chain (IDENTICAL across ecosystems, and it DOMINATES)

This is what was missing from the previous version, and it changes the shape of the budget completely.

Per mouse, the chain from skull to box is: **implant → headstage (RHD2216) → short SPI cable → commutator → long SPI cable → (adapter, XDAQ only) → DAQ port.**

| Item | Part | Unit | Qty | Ext | Tag |
|---|---|---|---|---|---|
| RHD 16 ch bipolar headstage | Intan **C3313** | $820 | 32 | $26,240 | **PUBLISHED** |
| ↳ or with 3-axis accelerometer (posture/movement, useful for sleep staging) | Intan **C3323** | $880 | 32 | $28,160 | **PUBLISHED** |
| ↳ or Open Ephys equivalent | OEPS-6577-6574 | from €780 | 32 | €24,960 | **PUBLISHED** |
| SPI cable, headstage → commutator, 3 ft ultra-thin (light on a tethered mouse) | Intan **C3213** | $415 | 32 | $13,280 | **PUBLISHED** |
| SPI cable, commutator → DAQ, 6 ft standard (weight irrelevant above the commutator) | Intan **C3206** | $295 | 32 | $9,440 | **PUBLISHED** |
| SPI cable adapter board, breaks the 12 SPI wires out to 0.1" solder holes, 2 per commutator | Intan **C3430** | ⏳ not on price list | 64 | ⏳ | **owed** |
| **Commutator, 1 per mouse — SEE THE THREE OPTIONS BELOW** | | | 32 | **€10k-83k** | |
| Electrode adapter / wire adapter at the implant (if used) | C3410 $255 / C3420 $230 | $230-255 | 32 | $7,360-8,160 | **PUBLISHED**, optional |
| Tether strain relief, chamber mounts, cable management | — | ~$50-150 | 32 | ~$1,600-4,800 | **ESTIMATE** |
| | | | **Block 2 subtotal, excl. commutator** | **~$50,500-55,000** | |

> [!danger] The commutator is the biggest single line in the entire rig, and it is ecosystem-neutral
> One commutator per mouse × 32 mice. Three routes, an order of magnitude apart:
>
> | Route | Unit | ×32 | Notes |
> |---|---|---|---|
> | **Open Ephys torque-free SPI commutator** (OEPS-7761) | **€2,595** | **€83,040** | **PUBLISHED.** Active, torque-free, takes any 3D-capable SPI headstage. Best-in-class, and more expensive than any DAQ option in Block 1. |
> | **Commercial Intan-ready motorized** (Doric with Intan adapter; Alpha Omega AlphaComm-I) | ⏳ | ⏳ | Intan names both as Intan-ready. Prices not published, **quotes owed**. Expect low thousands each. |
> | **Open-MAC, open-source motorized commutator** (Kaetzel Lab, Ulm) | ~$300-600 | **~$10k-19k** | **ESTIMATE.** Published open-source design, explicitly Intan-headstage compatible. Build cost only; add lab build time × 32 units. |
> | **Passive slip ring + Intan C3430 breakout** | few hundred | ~$10k-15k | Intan publishes an application note for adapting SPI cables to any basic commutator. Since SPI is purely digital, Intan states operation with commutators is "typically robust and free of movement-induced noise." |
>
> **This one decision moves the total budget by ~€65,000-70,000, more than the choice between XDAQ, Open Ephys and Intan does.** It deserves its own investigation, and it should probably start with a question we have not answered: **what are the 8 mice on the current rig using right now, how many of those units do we already own, and are they reusable at 32?** The vault records slip-ring rotation being tested and exonerated as a 60 Hz source in [[eeg-60hz-saga]], so commutators of some kind are already in service. That inventory check comes before any commutator quote.
>
> Because SPI is a digital link, the expensive torque-free unit buys **animal welfare and cable longevity**, not signal quality. That is a real argument for a 72 h chronic sleep study, but it is a welfare and reliability argument, and it should be made on those terms rather than assumed.

> [!warning] VERIFY: how many headstages do we actually own?
> The 2026-07-24 version claimed "we own 32" RHD2216 headstages and credited $0 for them. That looks wrong. The current rig is 8 mice with an 8-headstage hard ceiling on the Gen-1 Core, so the plausible number is **8, not 32**. If it is 8, Block 2 carries 24 new headstages, ~$19,680, not $0. **Count them before this number goes in a budget.**

### 3.3 BLOCK 3 — shared infrastructure (IDENTICAL across ecosystems)

| Item | Spec | Est. cost | Notes |
|---|---|---|---|
| Acquisition PC | 1 unit. **2× Thunderbolt 3 ports if XDAQ** (60 W each); USB 3 suffices for Intan/OE. 64 GB RAM, fast NVMe scratch. | ~$2,500-4,000 | ONE PC for all three ecosystems, see §2.3 |
| Recording storage array | sized from §2.3: 88 GB/day at 1 kS/s up to 2.65 TB/day at 30 kS/s, all 32 mice | ~$1,500-8,000 | **Set the sample rate first**, it is a 30x swing |
| UPS | must ride out a mains blip on a 72 h live-animal run | ~$500-1,500 | Not optional for chronic work |
| TTL sync distribution: BNC cabling, buffer/fan-out to every DAQ box + every Pi camera | per the §2.5 shared sync line, 220 Ω series + 10 kΩ pulldown per branch | ~$100-300 | Same line serves DAQ sync and video sync |
| Rack, chamber mounting, cable trays | 32 chambers | ⏳ | **owed**, depends on room layout |
| Acquisition software | Open Ephys GUI | **$0** | All three ecosystems |

### 3.4 Rough complete-rig totals (Scenario A, isolation-first)

| Block | XDAQ | Open Ephys | Intan |
|---|---|---|---|
| **1. DAQ block** | ~$60k-74k **EST** | ~€27,200 (weak isolation) | **$57,000** published |
| **2. Tether chain excl. commutator** | ~$50k-55k | ~$50k-55k | ~$50k-55k |
| **2b. Commutators × 32** | €10k-83k | €10k-83k | €10k-83k |
| **3. Infrastructure** | ~$5k-14k | ~$5k-14k | ~$5k-14k |
| **Complete rig** | **~$127k-226k** | **~€94k-186k** | **~$124k-209k** |

Read this carefully, because it reframes the whole decision:

- **The three ecosystems are far closer together than the old comparison suggested.** Removing the Allego license and the second PC pulled XDAQ down; adding the full tether chain, identical everywhere, compressed the relative gaps. The DAQ block is now roughly **25-45% of the rig**, not the whole story.
- **The commutator choice swings the total by more than the ecosystem choice does.** €10k versus €83k for the same 32 mice.
- **Open Ephys is cheapest only in Block 1, and buys the weakest isolation there.** Since Blocks 2 and 3 are identical, its entire advantage is roughly €30k on the DAQ block, in exchange for the one property we most need.
- **Intan is now the cleanest hardware story**: fully published pricing, per-port isolation included at no extra cost, zero adapters in the chain, and it is no longer the most expensive option once the license and second PC come off XDAQ's side.

---

## 4. What is still owed

**XDAQ / Kontex** (ask in one email):
- ⏳ Real quote for **2× ONE+ for 32 mice**, with Port Expanders, OM12 interfaces and the ONE+ HDMI bridge adapter. The ONE+ unit price is still an ESTIMATE and it is the single largest uncertainty in the XDAQ column.
- ⏳ **NEW, and now critical: is the Port Expander fully supported under the Open Ephys GUI plugin, with per-animal isolation intact?** If the Port Expander only works under Radiens, XDAQ's entire isolation advantage disappears the moment we drop Allego, and the XDAQ column collapses.
- ⏳ **NEW: does the Open Ephys XDAQ plugin support TWO XDAQ devices in one GUI instance on one PC?** (§2.3)
- ⏳ Confirm the Port Expander accepts our Intan RHD2216 via SAdpt-XDAQ-OM12/Omnetics, not only Kontex XR headstages.
- ⏳ Is the 72 h endurance result expected to hold under the OE plugin rather than Allego?

**Open Ephys:**
- ⏳ Are the acquisition board's 4 ports galvanically isolated from each other? (decides whether Scenario A buys anything at all)
- ⏳ USD pricing.
- ⏳ Multi-day continuous reliability references for 4-8 synced boards.
- ⏳ Is per-Record-Node start/stop on the roadmap? (§2.4)
- ⏳ Atlanta custom-team scope and price for a 16-headstage board.

**Intan:**
- ⏳ Multi-controller operation for 4× C3008 **under the Open Ephys GUI** (the old question was about RHX; with OE GUI as the front end it becomes the same multi-source-node question as §2.3, and probably easier).
- ⏳ C3430 SPI cable adapter board price (64 units needed).
- ⏳ Lead times for a 4-controller / 32-headstage batch; name a Korea/KAIST distributor for import and VAT.

**Rig-wide, ecosystem-neutral, and arguably the highest-value items on this whole list:**
- ⏳ **Commutator inventory and decision.** What is on the current 8-mouse rig, how many we own, whether they scale to 32, and quotes for Doric/Alpha Omega versus building Open-MAC units. This swings the budget more than the DAQ choice.
- ⏳ **Headstage inventory.** 8 or 32? (§3.2 warning)
- ⏳ **Sample rate decision.** Sets storage cost across a 30x range and gates the continuous-recording workaround in §2.4.

---

## 5. Current reading (NOT the final decision)

- **The no-Allego decision was the right call financially, and it moved the ranking.** It removes $5k-10k of license, removes a second PC, and removes SyncLink from the required list. It also removes XDAQ's biggest non-price advantage, since pipeline reuse is worth nothing once the pipeline is being rebuilt anyway.
- **On the surviving axes, Intan direct now looks strongest**, which is a change from the 2026-07-24 reading. It has true per-animal isolation included at zero extra cost, the shortest adapter chain (fewest connectors is fewest failure points on a 72 h run), fully published pricing with no quote to chase, and it is no longer the most expensive path once XDAQ's license and second PC come off. Its one open risk, 4-controller coordination, gets easier under the Open Ephys GUI rather than harder.
- **XDAQ stays credible but is now quote-gated and support-gated.** It is the only box with a PROVEN 72 h byte-perfect run on our own bench, which is worth real money for a chronic instrument. But that proof was under Allego, and two unanswered questions (Port Expander under OE, two XDAQ devices in one GUI) could each independently sink the column. Get those answers before anything else.
- **Open Ephys hardware remains the weakest fit for OUR specific problem**, despite being cheapest in Block 1. We are buying isolation, and it is the one vendor that does not sell it. Its GUI, however, is now the front end for whatever we buy, which is the correct use of that ecosystem.
- **Budget attention is misallocated if it goes to the DAQ.** The commutator line is €10k-83k for the same 32 animals, larger than the spread between ecosystems. Start the commutator investigation now, in parallel, not after the DAQ decision.
- **Accept that per-mouse independent scheduling is gone** (§2.4), and plan for continuous recording at a deliberately chosen sample rate with offline slicing per user. Decide the sample rate early, it sets the storage budget.
- **DECISION GATE:** do NOT decide until (a) Kontex answers Port-Expander-under-OE and two-devices-per-PC and sends a real ONE+ quote, (b) Open Ephys answers port isolation, (c) the commutator inventory and quotes land, (d) the headstage count is verified. THEN take it to a **council**. And remember: this whole scale-up is still gated behind **surgical yield** (open frontal electrodes). No acquisition box fixes an open electrode ([[eeg-60hz-saga]]). Buy the box that fits the science, after the science works.

---

## 6. ONE-PAGE SUMMARY FOR THE DECISION MEETING

> Everything below assumes the four ground rules at the top: **no Allego licence, Open Ephys GUI on all three systems, complete rig priced, our own software excluded.**

### 6.1 The three facts that matter most

1. **A "channel" is really a mouse slot.** Every one of these systems reserves **64 channels per animal**, no matter that our headstage only has 16 and we use 4. So **animals = channels ÷ 64**. Our 512-channel box gives 8 mice, which is what we run. A 1024-channel box gives 16, not 64. **32 mice always means two boxes, in every ecosystem.**
2. **The acquisition box is not the big cost any more.** Once the licence is gone and the whole rig is priced, the DAQ is only **25-45%** of the budget. The **commutators are the biggest single line: €10k to €83k for the same 32 mice**, depending only on which model we pick, and identical across all three vendors.
3. **We are buying ONE thing: per-animal ground isolation.** That is the answer to the 60 Hz problem that has cost us the year. It is the axis on which the three systems genuinely differ.

### 6.2 The comparison, stripped to what differs

| | **XDAQ / KonteX** | **Open Ephys** | **Intan direct** |
|---|---|---|---|
| Boxes for 32 mice | 2 × ONE+ **R1024** | 4-8 boards | 4 × C3008 |
| **Per-animal isolation** | ✅ via Port Expander (paid add-on, $1,525/port) | ❌ **no product exists** | ✅ **built into every port, free** |
| Adapters between box and mouse | **3 layers** (HDMI cable → Port Expander → interface) | 1 | **0 — plugs straight in** |
| Drives our existing Intan RHD2216 | ✅ **CONFIRMED by KC 2026-07-28** | ✅ (their own equivalent) | ✅ native, it is their chip |
| Software (Open Ephys GUI) | ✅ free, officially supported | ✅ free | ✅ free |
| Pricing | ❌ quote-only, **still not quoted** | ✅ public (EUR) | ✅ **fully published (USD)** |
| Proven on our bench | ✅ **72 h byte-perfect** (under Allego) | ✗ | ✗ |
| **DAQ block cost** | ~$57-71k **estimate** | ~€27k | **$57,000 published** |
| **Complete rig** | ~$127-226k | ~€94-186k | ~$124-209k |

### 6.3 Recommendation — UPDATED 2026-07-28

**XDAQ moved back into the lead** once KC Kong confirmed the Port Expander drives our Intan RHD2216 headstages. That was the question that could have eliminated it, and it landed in XDAQ's favour. XDAQ now offers per-animal isolation, reuse of our existing headstages, the **only proven 72 h byte-perfect run on our own bench**, the chassis-ground terminal our current box lacks (directly relevant to the 60 Hz problem), and a lower DAQ-block cost than Intan. Its remaining weaknesses are the deepest adapter chain of the three and a price that is **still an estimate**.

**Intan direct remains the strong alternative** and the benchmark to hold the Kontex quote against: isolation included free, zero adapters, and every price published. If the Kontex quote comes in near the top of the estimate range, Intan is competitive again on cost while being simpler to wire.

**Open Ephys hardware stays out** on isolation grounds. Its GUI is still the software for whichever box we buy.

**Decision posture: XDAQ, pending the 2026-07-29 call and a written quote.** See [[2026-07-29-kontex-kc-call-prep-rig-finalization]].

**Open Ephys hardware is cheapest and does not solve our problem.** Its GUI, however, is now the software for whichever box we buy.

### 6.4 What must happen before we commit

| # | Blocker | Who | Why it matters |
|---|---|---|---|
| 1 | ~~Does the XDAQ Port Expander drive our Intan RHD2216?~~ | ~~Kontex~~ | ✅ **CLOSED 2026-07-28 — KC confirms YES** |
| 2 | Formal quote: 2× ONE-**R1024** + 8× Port Expander + all cables | Kontex, **call 2026-07-29** | The XDAQ price is still a guess; now the top blocker |
| 2b | Linux driver, cable lengths for our 36 cm chamber geometry, one PC or two, SyncLink needed or not | Kontex, **call 2026-07-29** | Each changes the build, not just the price. Full list: [[2026-07-29-kontex-kc-call-prep-rig-finalization]] |
| 3 | Are the Open Ephys board's 4 ports isolated from each other? | Open Ephys | Decides whether their cheaper option is viable at all |
| 4 | **Commutators: what do our current 8 mice use, how many do we own, do they scale?** | us, internally | Swings the budget by ~€70k, more than the vendor choice does |
| 5 | **How many RHD2216 headstages do we actually own?** (believed 8, an earlier note claimed 32) | us, internally | ±$20k |
| 6 | **What sample rate do we need?** | us, scientific | 1 kHz vs 30 kHz is a 30× storage difference (88 GB vs 2.65 TB per day) |

Items 4, 5 and 6 are ours to answer and cost nothing but an afternoon. They should not wait on any vendor.

### 6.5 One consequence to accept knowingly

Dropping Allego removes the only documented way to **start and stop each mouse on its own schedule**. Under the Open Ephys GUI, on any of the three systems, recording start/stop is global. Separate files per animal still work. The plan is to **record continuously and slice per user offline**, which is why the sample-rate decision above matters. (Buying two acquisition PCs instead of one would restore independent control for each group of 16.)

### 6.6 The standing caveat

None of this is the current bottleneck. **The frontal electrodes are open on every mouse, and there is still zero scoreable data.** No acquisition box fixes an open electrode ([[eeg-60hz-saga]]). This decision should be made deliberately and unhurriedly, in parallel with fixing surgical yield, not instead of it.

---

## Related
- ⭐ [[xdaq-32-mouse-wiring-and-channel-law]] — **the deep XDAQ wiring note (power supply → mouse), the channel law, and why the splitter cannot reach 32**
- [[daq-ecosystem-comparison-xdaq-vs-openephys]] (superseded predecessor) · [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] · [[2026-07-21-openephys-acquisition-board-scale-up-option]] · [[openephys-inquiry-email]]
- [[intan-rhd-spi-wiring-and-headstage-limits]] · [[kontex-xdaq-hardware-reference]] · [[eeg-60hz-saga]] · [[project_multiuser_recording_schedules]] (⚠️ overturned by §2.4)

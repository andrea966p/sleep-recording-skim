---
name: xdaq-channel-law-and-32-mouse-wiring
description: THE CHANNEL LAW (animals = XR channels ÷ 64) + complete XDAQ 32-mouse wiring power-supply→mouse; splitter CANNOT exceed 16/box; ONE+ R512 ordering trap
metadata: 
  node_type: memory
  type: project
  modified: 2026-07-28T03:47:47.816Z
  originSessionId: a71f4126-a668-426f-b904-b7936fd73591
---

Vault ⭐ `10-projects/rig-expansion/xdaq-32-mouse-wiring-and-channel-law.md`. Sourced from docs.kontex.io pulled 2026-07-28 via curl+browser-UA. **⚠️ The decisive compatibility/model tables on those pages are PNG IMAGES, not HTML — any text-only scrape MISSES them.** (`SAdpt_Port_EXP-10.png` = XR compat, `-12.png` = topology, `ONE_P -27/-28.png` = ONE+ specs + model comparison.)

**🔑 THE CHANNEL LAW: max animals = XR recording channels ÷ 64.** System reserves a fixed 64-ch slot per headstage/MISO line (sized for RHD2164) regardless of actual chip. Verified 2 independent Kontex figures agreeing:
- CORE2 512ch → **8** (= exactly our lived Gen-1 rig, 128ch/port ÷64 = 2/port × 4)
- ONE+ Base **R512 → 8** ⚠️ · ONE+ Max **R1024 → 16** (256ch/port ÷64 = 4/port × 4)
- AIO 1024 → **16** (adds 4ch integrated video processor + 4ch optogenetics LED driver)
→ **Our RHD2216 is 16ch, uses 4, but BURNS A FULL 64-CH SLOT. 60/64 wasted per mouse, structurally, unrecoverable. "1024 channels" = 16 MICE, not 64.** Never reason from channels; reason from animals.

**⚠️ ORDERING TRAP: ONE+ sold in 2 tiers. R512 records only 8 mice = no better than the Core we own.** Ports are LICENSE-GATED, verbatim: *"Always use Port 1, as other ports may be unavailable depending on the license purchased with the XDAQ."* Order **ONE-R1024-SR64** (SR = stim ch, irrelevant to us, cheaper SR64 fine). Tiers appear field-upgradable by firmware (*"Additional capabilities may be enabled if they were not selected in the initial purchase"*) → ⏳ ask if R512→R1024 is a paid unlock.

**🔴 SPI SPLITTER CANNOT REACH 32 IN ONE BOX. Three blocks:** (1) ✅ **slot ceiling, DOC-SOURCED and binds ALONE** — R1024 has 16 slots, no 17th; (2) ⚠️ **INFERRED, NOT a vendor quote**: one EXP port = ONE MISO line but C3442 needs TWO → can't attach. **Kontex publishes NO EXP-port pin map.** Inference chain = MISO pairs/port (Core 2, ONE+ 4; vendor EMAILS from Jeff/KC, not docs) + animals/port (Core EXP A+B=2, ONE+ EXP A-D=4; Kontex PE figure) + 1 chip = 1 MISO (Intan datasheet verbatim); counts match exactly + channel law agrees (256÷64=4, 128÷64=2). NOT ruled out: EXP port may physically carry both MISO with Kontex using one. **Block 1 unaffected → conclusion survives either way**; (3) splitter puts both animals back in ONE port ground domain → destroys the isolation the Port Expander exists to provide.

⚠️ **SPLITTER TOPOLOGY, CORRECTED 2026-07-28 by Andrea:** we place the C3442 **AT THE XDAQ PORT**, so **each animal gets its OWN SPI cable**. NOT 2 animals hanging off one cable (that's Intan's canonical animal-end placement, not ours; SAdpt-XDAQ-OM12 already presents 2 Omnetics sockets P1/P2 right at the box). → **no shared cable, no shared return conductor**. What they DO share = **the XDAQ port's ground/reference NODE** (both cable grounds originate there). Still a common ground domain, still NOT isolation, but LESS severe than shared-cable (no common-return IR drop between the two animals). PortExp exists to subdivide exactly that domain. **Splitter FILLS a box, never exceeds it**: on Core, SAdpt-XDAQ-OM12 + 1 C3442 = 2/port × 4 = 8 (our current rig); on ONE+ R1024, 2 sockets × C3442 = 4/port × 4 = 16 (same ceiling as PortExp route, but shared ground per pair). **32 mice = 2× ONE+ R1024, mandatory, no single-box option at any price.**

**Port Expander (SAdpt-Port-EXP):** 1 per XDAQ headstage port → **4 per box**. Own **USB-PD AC adapter** (NOT powered by XDAQ), 350g, Mode switch → **XR** (EXP A/B LEDs stay dark in XR = normal). Ports EXP A-D; **C/D DEAD on any 512ch system**. 1 EXP port = 1 animal = 1 MISO = 1 slot.

**✅ RESOLVED 2026-07-28 — KC Kong CONFIRMS Intan headstages usable with Port Expander.** XDAQ column UN-BLOCKED: isolation reaches our animals, no need to buy 32 KonteX headstages, XDAQ back in the LEAD. Exact part-by-part chain + isolation-survives-adapter still to pin down on the 2026-07-29 call. Original doc-derived concern (kept, explains why we asked): **PortExp XR compat table lists "X3R32 or XeR64" = KONTEX headstages ONLY, Intan RHD2216 NOT listed.** Kontex commutator pages also list only KonteX headstages. KonteX XR line has NO 16ch bipolar part (closest X3R32=32ch; bipolar equivalence UNKNOWN — our whole CMRR/shared-ground argument rests on bipolar). Plausible-but-undocumented bridge: EXP ports are HDMI and SAdpt-XDAQ-OM12 is HDMI-male→Omnetics, so it may mate (only P1 live, 1 MISO). **If PE can't drive Intan: either buy 32 new headstages, or XDAQ's isolation advantage doesn't reach our animals → Intan direct wins.**

**WIRING, wall→mouse (per box, ×2):** mains → **1× DC-IN 200W universal adapter** → ONE+ power port (NOT bus-powered) · **Computer Port TB3 → PC** with SUPPLIED Thunderbolt cable (**USB-C data cable will NOT work**; ≤3m; Intel/Apple-certified only; *"Retrofitting a PC with a Thunderbolt add-on card is generally impractical"* → **2-box-1-PC needs 2 NATIVE TB3 ports, unbolt-on-able**). 2nd TB3 = Peripheral Port 15W (can host TB storage); XDAQ supplies 60W back to PC · **4× X-Headstage HDMI ports P1-P4 → 4× KonteX HDMI cable → 4× Port Expander** (⚠️ *"non-KonteX cables... can interfere with XDAQ communication and potentially damage the XDAQ or X-Headstage"*) · EXP A-D → cable → **commutator** → headstage → mouse (animal GND green → headstage GND pad).

**✅ GROUNDING WIN: ONE+ back panel has Sys GND + Chassis GND 4mm banana terminals.** Chassis GND = *"connected to the metal enclosure, the outer shield of the HDMI cable, and earth ground via the power supply."* Kontex recommends **bonding both and using that node to ground the Faraday cage shielding**. **Our Gen-1 Core has NO chassis terminal — that's exactly why foil grounding was dropped 2026-07-16** ([[eeg-60hz-saga]]). SyncLink has the same terminal pair.

**Sync I/O:** 8× BNC (DI/DO-01/02 3.3or5V, AI/AO-01/02 16bit ±10V) + DB25 (DI-03..08, DO-03..08 **3.3V only**) carrying **`DAQ ON` (logic high at recording-session onset)** and **`Sample CLK`** — both CLEANER primitives than the gated `DO 03` scoped for Gen-1 → revisit sync design if ONE+ bought. Breakout board available. 8ch DI/DO onboard, 32ch via IO Expander on EXP1/2 microHDMI.

**Box-to-box sync:** SyncLink (230g, 1 per XDAQ, EXP1/2 microHDMI to box, **daisy-chain SyncLinks OUT→IN with standard Ethernet**, Harp Clock 3.5mm port). ⚠️ Kontex verbatim: *"connect each XDAQ to its corresponding PC. Each SyncLink operates as the synchronization interface for its associated XDAQ–PC pair"* = **documented topology is 2 PCs**. BUT OE GUI runs multi-device in one instance and ONE+ needs only **6-core/16GB/1× TB3** (ref configs: **Mac Mini M4 Pro 16GB, MSI Cubi i7+**) → **recommend shared-TTL sync instead of SyncLink** (OE Record Node <1ms, 4000× tighter than a sleep epoch). ⏳ ask if OE XDAQ plugin binds 2 devices.

**ONE+ acquisition specs (methods section):** 16-bit, 1-30 kHz, input ±5mV, **noise 2.4 µV RMS typ**, HW filter lower 0.1-500Hz / upper 100Hz-20kHz, latency <1ms, **headstage ports "electrically isolated"**, Win/macOS/Linux, XR software = **OpenEphys XDAQ plugin / XDAQ-RHX / Radiens**. Weight 2810g, 226.5×160×93.71mm.

**SAdpt-XDAQ-OM12** = tiny dongle 27.45×21.46×10.8mm, **HDMI Type-A MALE** (into XDAQ) → **2× Omnetics Polarized NANO 12-pin (P1,P2)**. Don't confuse with **SAdpt-HDMI-OM12** (HDMI FEMALE, opposite direction: KonteX XR headstage → Intan Recording Controller).

**KonteX sells commutators too:** Commutator **STD** (passive, redesigned, integrated animal-side cable management, XR up to 256ch/cable) and **PRO** (motorized, low-noise, onboard µP + gyroscope or Hall torque sensing). PortExp *"compatible with all KonteX cable and commutator solutions"*, recommends same model on every animal. ⏳ prices.

Related: [[daq-ecosystem-comparison]], [[acquisition-device-16-32-mice]], [[eeg-60hz-saga]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ⭐ [XDAQ channel law](xdaq-channel-law-and-32-mouse-wiring.md) — animals = channels ÷ 64. Order ONE-R1024. 32 mice = 2 boxes.

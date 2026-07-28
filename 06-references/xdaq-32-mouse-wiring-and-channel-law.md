---
tags:
  - reference
  - xdaq
  - kontex
  - wiring
  - port-expander
  - scale-up
  - channel-limits
  - one-plus
created: 2026-07-28
status: complete
source: docs.kontex.io retrieved 2026-07-28 via curl + doc figure images
  (compatibility tables are IMAGES, not HTML text)
---
# XDAQ 32-Mouse Wiring, End to End — and the Channel Law that Decides Everything

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The complete, vendor-sourced answer to three questions: (1) exactly what cables and boxes are needed to run 32 mice on XDAQ, from the wall socket to the animal's head; (2) which XDAQ model can actually do it; and (3) whether the SPI splitter can push one box past 16 mice.
> **The one rule to remember, "the channel law."** XDAQ's advertised channel count is not a channel count in any useful sense. It is a **mouse count in disguise**: the box reserves a fixed **64-channel slot per headstage**, regardless of how few channels that headstage actually uses. So **max mice = advertised recording channels ÷ 64.** Our 512-channel Core gives 512 ÷ 64 = 8 mice, which is exactly the 8 we run today. Our RHD2216 headstage uses only 16 of its 64-channel slot and the other 48 are simply thrown away. Buying "more channels" buys mice, not channels.
> **Can the splitter get one box to 32? NO.** Three independent reasons, any one of which is fatal (§4). 32 mice on XDAQ means **two boxes, and they must be the 1024-channel tier.**
> **The trap to avoid when ordering.** "XDAQ ONE+" is sold in two tiers, 512ch and 1024ch. The **512 tier records only 8 mice**, same as the Core we already own. Ordering the wrong tier halves the rig. The part must be specified as **ONE-R1024**.
> **The unresolved risk.** Kontex's own compatibility table lists the Port Expander as working with **KonteX XR headstages (X3R32 / XeR64)**. It does **not** list Intan RHD2216, which is what all our mice use. If the Port Expander cannot drive our Intan headstages, XDAQ's per-animal ground isolation, the entire reason we are considering it, does not reach our animals. This is the single most important question to put to Kontex (§8).

> [!quote] Paper-ready
> The XDAQ acquisition system allocates a fixed 64-channel data slot per recording headstage, so the maximum number of simultaneously monitored animals equals the system's nominal recording-channel capacity divided by 64, independent of the channel count of the headstage used. A 512-channel XDAQ CORE2 therefore supports eight animals and a 1024-channel XDAQ ONE+ supports sixteen, each headstage occupying one SPI MISO return line. Because the Intan RHD dual-headstage adapter consumes both MISO lines of a single SPI cable rather than creating additional ones, per-port headstage splitting cannot raise a system above its slot ceiling; scaling to 32 animals requires two 1024-channel units synchronised by a shared clock.

> [!info] Sources, all retrieved 2026-07-28
> - `docs.kontex.io/XDAQ/ONE/` — ONE+ manual: setup, power, ports, PC requirement, DB25, grounds, software, **Model Comparison table (figure `ONE_P -28.png`)** and **Technical Specifications table (figure `ONE_P -27.png`)**
> - `docs.kontex.io/System-Adpt/SAdpt-Port-EXP/` — Port Expander manual + **XR/XSR compatibility tables (figures `SAdpt_Port_EXP-10.png` XR, `-11.png` XSR)** + **system topology figure (`-12.png`)**
> - `docs.kontex.io/System-Adpt/SAdpt-XDAQ-OM12/` — XDAQ→Intan RHD adapter, incl. wiring figure `SAdpt_XDAQ_OM12-03.png`
> - `docs.kontex.io/System-Adpt/SAdpt-HDMI-OM12/` — the reverse adapter (XR headstage → Intan controller)
> - `docs.kontex.io/System-Adpt/SyncLink/` — multi-box sync
> - `docs.kontex.io/Commutator/` — KonteX Standard + PRO commutators
> - ⚠️ **The decisive compatibility and model-comparison tables are published as PNG images, not HTML.** Any text-only scrape of these pages silently misses them. That is why earlier passes over these same pages produced an incomplete picture.
>
> Companion: [[intan-rhd-spi-wiring-and-headstage-limits]] (the MISO physics from Intan's side), [[kontex-xdaq-hardware-reference]] (2026-07-21 pass), [[2026-07-24-daq-32-mouse-final-comparison]] (the buying decision), [[eeg-60hz-saga]] (why isolation matters).

---

## 1. THE CHANNEL LAW — what "1024 channels" actually buys

This is the heart of the whole question, and it is counter-intuitive enough that it has misled us twice.

**Max animals = XR-mode recording channels ÷ 64.**

Verified two independent ways from two different Kontex figures that agree exactly:

| XDAQ model / tier | XR recording channels | Channels per headstage port | **Max animals per box** | Cross-check |
|---|---|---|---|---|
| **CORE2** (our Gen-1 class) | 512 | 128 | **8** | 512÷64 = 8 · 128÷64 = 2/port × 4 ports = 8 ✅ |
| **ONE+ Base (R512)** | 512 | 256 | **8** | 512÷64 = 8 ⚠️ **not 16** |
| **ONE+ Max (R1024)** | 1024 | 256 | **16** | 1024÷64 = 16 · 256÷64 = 4/port × 4 ports = 16 ✅ |
| **AIO** | 1024 | 256 | **16** | same as ONE+ R1024 |

Both source tables state these animal counts directly. The Model Comparison figure gives "# of Animal Monitored, Recording Only Experiment" as CORE2 = 8, ONE+ = 8 (Base column), AIO = 16. The Port Expander compatibility figure gives the same numbers per tier and makes the ONE+ split explicit: **ONE-R512 → 8 animals total, ONE-R1024 → 16 animals total.**

**Why 64?** The system reserves one 64-channel slot per SPI MISO return line, sized for the largest RHD chip in the family (the 64-channel RHD2164). One chip = one MISO line = one 64-channel slot = one mouse.

> [!danger] The consequence for us, stated plainly
> Our **RHD2216 is a 16-channel chip. It still consumes a full 64-channel slot.** We use 4 of those channels (bipolar EEG + bipolar EMG). **60 of 64 channels per mouse are wasted, and that waste is structural and unrecoverable.**
>
> So "1024 channels" does NOT mean 1024 ÷ 16 = 64 mice, and it does not mean 1024 ÷ 4 = 256 mice. **It means 16 mice.** Any budget conversation that reasons from channel counts will be wrong by a factor of 4 to 16. Reason from animals.
>
> This also confirms, from the vendor side, what we already learned the hard way: **our Gen-1 Core's 8-mouse ceiling is arithmetic, not a defect and not a firmware lock.** 512 ÷ 64 = 8. It was never going to be more. See [[intan-rhd-spi-wiring-and-headstage-limits]] for the same conclusion derived from Intan's cable datasheet.

---

## 2. ⚠️ THE ORDERING TRAP: ONE+ is sold in two tiers and one of them is useless to us

Verbatim from the ONE+ manual, in the headstage setup instructions:

> *"Connect the Type-A HDMI connector to one of the XDAQ™ Headstage Ports. **Always use Port 1, as other ports may be unavailable depending on the license purchased with the XDAQ™.**"*

**Headstage ports are licence-gated.** The physical box has four, but how many are enabled, and how many channels the box will process, depends on what was purchased. The Port Expander table names the tiers explicitly: `ONE-R512-SR64`, `ONE-R512-SR128`, `ONE-R1024-SR64`, `ONE-R1024-SR128`.

| Tier | Animals | Fit for a 32-mouse build |
|---|---|---|
| ONE-R512-* | **8** | ❌ **No better than the Core we already own.** Would need 4 boxes for 32. |
| **ONE-R1024-*** | **16** | ✅ **This is the part to order.** 2 boxes = 32. |

The `-SR64` / `-SR128` suffix is the **stimulation** channel count, which we do not use (we are record-only, XR mode). It does not change the animal count: R1024-SR64 and R1024-SR128 both give 16 animals. So the cheaper SR64 variant is fine for us, provided the R**1024** part is correct.

Good news on flexibility, verbatim from the firmware section: *"Additional capabilities may be enabled if they were not selected in the initial purchase (e.g. adding the SR128 capability or Neuropixels support)."* So tiers appear to be **field-upgradable by firmware licence**. Worth asking whether R512 → R1024 is likewise a paid unlock, since that would de-risk ordering (§8).

**AIO vs ONE+:** identical for our purposes (both 16 animals, 1024ch, 4 ports, same I/O). AIO adds an **integrated video processor (4 channels)** and a **4-channel optogenetics LED driver**. The integrated video capture is worth a look given the effort our camera-sync work has taken, but it is a different architecture from our Frigate/Pi cameras and would be a separate evaluation, not a reason to prefer AIO by default.

---

## 3. What the Port Expander actually is

Verbatim: *"It allows each HDMI headstage port in the XDAQ to support up to four animals with XR Headstages or up to two animals with XSR headstages."* And: *"conditions the control signal and provides **isolated and dedicated electrical systems to each connected headstage. As a result, the ground and reference nodes from each animal's headstage do not interfere with one another.**"*

- One Port Expander per XDAQ headstage port. Four ports per box → **4 Port Expanders per box**.
- Front panel: Power button, Mode switch (XR / XSR), VStim LEDs (XSR only), and **4 HDMI ports EXP A, EXP B, EXP C, EXP D**.
- Powered **separately** from its own **USB-PD AC adapter** (included). It is not powered by the XDAQ. Weight 350 g.
- **Mode switch must be set to XR** for us. In XR mode the EXP A/B LEDs stay dark; that is normal, not a fault.
- **EXP C and EXP D are dead on 512-channel systems.** On the CORE and on ONE-R512, only EXP A and EXP B are active (2 animals per XDAQ port). All four are active on ONE-R1024 and AIO.
- Kontex's own topology figure shows exactly the target build: **one XDAQ → 4 HDMI cables → 4 Port Expanders → 16 mice.**

**One EXP port = one animal = one MISO line = one 64-channel slot.** That 1:1 mapping is what makes the next section's answer unambiguous.

**It does not add capacity.** It is the productised, *isolated* breakout of the MISO lines a port already has. Its value is entirely in the isolation, which is precisely what our [[eeg-60hz-saga]] needs.

---

## 4. Can the SPI splitter take one box past 16? **NO.** Three independent blocks

Andrea's question. The answer is no, and it fails three separate ways, so there is no clever workaround hiding behind any one of them.

**Block 1 — The slot ceiling.** ONE+ R1024 has 1024 ÷ 64 = **16 slots**. The FPGA has no seventeenth. A splitter cannot conjure a slot that the licensed channel budget does not contain. This alone is decisive.

**Block 2 — The splitter needs two MISO lines; an EXP port has one.** The Intan dual-headstage adapter (C3442) works by putting one chip on MISO1 and the other on MISO2 of a single SPI cable ([[intan-rhd-spi-wiring-and-headstage-limits]]). But a Port Expander EXP port is *already* the breakout of exactly **one** MISO line, which is why 4 EXP ports consume the port's 4 MISO lines and yield 4 animals. **There is no second MISO line at an EXP port for the splitter to use.** Hanging a C3442 off EXP A cannot work.

**Block 3 — It would destroy the only reason to buy the Port Expander.** Even setting aside blocks 1 and 2, two headstages on one SPI cable **share that cable's single ground and single supply conductor**. That is the shared-ground compromise documented in [[2026-07-24-daq-32-mouse-final-comparison]] §1. Using a splitter downstream of an isolator re-couples the two animals and throws away the isolation you paid $1,525 per port to get.

> [!important] So where DOES the splitter belong?
> The splitter is how you **fill** a box, not how you **exceed** it. It is the *no-Port-Expander* path:
>
> `XDAQ HDMI port → SAdpt-XDAQ-OM12 (2 Omnetics sockets, P1 + P2) → Intan SPI cable → C3442 splitter → 2× RHD2216`
>
> - On the **CORE** (2 MISO/port): only one socket is live, so 1 splitter = 2 mice/port × 4 ports = **8**. **This is exactly our current rig.**
> - On the **ONE+ R1024** (4 MISO/port): both sockets live, 2 splitters = 4 mice/port × 4 ports = **16**. Same ceiling as the Port Expander route, reached with cheaper parts, **but with shared ground within each splitter pair and no per-animal isolation.**
>
> Both routes land on 16. They differ only in isolation and cost. **Neither reaches 32 in one box.**

**Therefore: 32 mice on XDAQ = 2 × XDAQ ONE+ (R1024). There is no single-box option, in any XDAQ model, at any price.**

---

## 5. Complete wiring, wall socket to mouse — 32 mice, ONE+ + Port Expander (isolation build)

Everything below is per-box unless stated. **Two identical boxes** make 32.

### 5.1 Power

| # | Link | Detail |
|---|---|---|
| 1 | Mains → XDAQ | **1× DC-IN, 200 W universal adapter** (supplied). Plugs into the ONE+ power input port. The ONE+ is **not** bus-powered. |
| 2 | Mains → each Port Expander | **USB-PD AC adapter** (supplied), one per Port Expander → **4 per box, 8 total.** Each has its own power button and Power LED. |
| 3 | Mains → PC, and mains → UPS | See §6. A 72 h live-animal run should be on a UPS. |

Power budget per box: 200 W adapter for the XDAQ, plus 4 × USB-PD bricks. The XDAQ can *supply* 60 W back to the host PC over Thunderbolt, and its second Thunderbolt port ("Peripheral Port") supplies 15 W and can host a Thunderbolt storage device visible to the PC.

### 5.2 XDAQ to computer

| # | Link | Detail |
|---|---|---|
| 4 | XDAQ **Computer Port** → PC | **Thunderbolt 3**, using the **supplied Thunderbolt cable** (marked with a lightning-bolt symbol). |

⚠️ Three hard constraints, all verbatim from the manual:
- *"A USB-C data cable cannot substitute for the supplied Thunderbolt cable."* Same connector, different protocol.
- Cables up to **3 m**; substitutes must be Intel/Apple-certified TB3 or higher.
- *"Retrofitting a PC with a Thunderbolt add-on card is generally impractical, as these cards are model-specific... users should verify that their PC includes **native** Thunderbolt support."* **For two boxes on one PC this means buying a PC with two native TB3 ports. It cannot be bolted on later.**

### 5.3 XDAQ to Port Expanders

| # | Link | Detail |
|---|---|---|
| 5 | XDAQ **X-Headstage ports P1–P4** (HDMI Type A) → Port Expander input | **4× KonteX HDMI cable per box, 8 total.** |

⚠️ Verbatim: *"Using non-KonteX HDMI cables is possible but not recommended. Many commercial cables contain active electronics that can interfere with XDAQ™ communication and **potentially damage the XDAQ™ system or the X-Headstage™**."* Budget genuine KonteX cables; this is not a place to save money.

Set each Port Expander's **Mode switch to XR**.

### 5.4 Port Expander to the animal — the per-mouse chain (×32)

| # | Link | Detail |
|---|---|---|
| 6 | **EXP A/B/C/D** (HDMI) → commutator | One EXP port per mouse. 4 per Port Expander, 16 per box. |
| 7 | Commutator → headstage | **32 commutators.** KonteX sells two: **Commutator STD** (passive, redesigned, integrated animal-side cable management, supports XR up to 256 ch/cable) and **Commutator PRO** (motorised, low-noise, onboard microprocessor with gyroscope or Hall torque sensing, actively cancels cable twist). The Port Expander manual states it is *"compatible with all KonteX cable and commutator solutions"* and recommends **using the same cable configuration and commutator model on every animal**. |
| 8 | Headstage → implant | The headstage plugs to the electrode/EIB. Animal ground = green wire → headstage `GND` pad, one dedicated skull/dura ground pin per mouse (our surgical SOP). |

⏳ **Step 6→7 is the open question for Intan headstages — see §8.** With KonteX X3R32/XeR64 headstages the chain is fully documented and vendor-supported. With our Intan RHD2216 it is not.

### 5.5 The Intan-headstage route (what we actually own today)

Documented and vendor-supported **without** the Port Expander:

`XDAQ HDMI port → SAdpt-XDAQ-OM12 → Intan SPI cable → (optional C3442 splitter) → Intan RHD2216`

The **SAdpt-XDAQ-OM12** is a small dongle, **27.45 × 21.46 × 10.8 mm**, that plugs directly into the XDAQ front-panel HDMI port. Connectors: **HDMI Type A male** (system side) and **two Omnetics Polarized NANO 12-pin sockets, P1 and P2** (headstage side). Verbatim: *"The HDMI slot on the board allows the adaptor to be plugged directly into the XDAQ acquisition box. Both the P1 and P2 connectors on the adaptor can also be used with SPI cable to extend the connection to the acquisition system."*

Note the family also contains **SAdpt-HDMI-OM12**, which is the *reverse* adapter (HDMI Type A **female** → Omnetics), whose stated purpose is connecting a KonteX XR headstage **to an Intan Recording Controller**. Useful to know so the two part numbers are not confused on a quote; it is not the part we need.

### 5.6 Grounding (directly relevant to the 60 Hz saga)

The ONE+ **back panel carries two 4 mm banana ground terminals**:
- **Sys GND** — the digital ground shared by the internal circuitry.
- **Chassis GND** — *"connected to the metal enclosure, the outer shield of the HDMI cable, and earth ground via the power supply."*

Verbatim recommendation: *"As a starting point, we recommend **bonding the two ground ports together and using this common node to ground the Faraday cage shielding.** Since environmental conditions can vary significantly, users should test and adjust the grounding configuration to determine the most effective setup for their specific environment."*

> [!important] This is a real upgrade over our current box
> Our Gen-1 Core has **no chassis ground terminal**, which is exactly why the foil shielding could not be properly grounded and the attempt was dropped on 2026-07-16 ([[eeg-60hz-saga]]). **The ONE+ provides the terminal the Gen-1 lacks, and Kontex explicitly documents using it to ground a Faraday cage.** The SyncLink has the same pair of 4 mm terminals with the same recommendation.
>
> Combined with the Port Expander's per-animal isolated ground/reference, a ONE+ build addresses both halves of our grounding problem at once: **common-mode floor** (cage bonded to a proper chassis earth) and **per-animal coupling** (isolated EXP ports). Neither fixes an open frontal electrode, which remains the actual wall.

BOM: 4 mm banana leads, 2 per box plus the cage bond.

### 5.7 Sync I/O (video sync, Phase 0a)

Per box, XR mode, all sampled at the headstage sample rate:
- **8 × BNC**: DI-01/02, DO-01/02 (digital, DI accepts 3.3 V and 5 V; DO software-selectable 3.3 V or 5 V), AI-01/02, AO-01/02 (16-bit, ±10 V).
- **1 × DB25**: **DI-03…DI-08** and **DO-03…DO-08** (DB25 digital outputs are **3.3 V logic high only**), plus system signals — notably **`DAQ ON` (logic high at the onset of a recording session)** and **`Sample CLK` (the sampling clock driving the headstages)**. A **breakout board** is available to bring these out to BNC.
- Onboard 8 ch DI / 8 ch DO, expandable to 32 ch each via the **IO Expander** on the EXP1/EXP2 micro-HDMI ports.
- 3.5 mm stereo audio monitor (AO-01 → left, AO-02 → right) for listening to two amplifier channels.

`DAQ ON` and `Sample CLK` are both directly useful to the camera-sync plan and are cleaner primitives than the gated `DO 03` approach scoped for the Gen-1 Core. Worth revisiting the sync design if a ONE+ is purchased.

⚠️ Repeated twice in the manual: *"Do not connect ports to unintended signal type. Permanent damage may occur."*

### 5.8 Box-to-box synchronisation (2 boxes → 32 mice)

Two options:

**Option A — SyncLink (Kontex product).** 230 g, one per XDAQ.
- SyncLink ↔ XDAQ via the **EXP1/EXP2 micro-HDMI** ports.
- SyncLink ↔ SyncLink via **standard Ethernet cable**, **Sync OUT → Sync IN**, daisy-chained; add more units the same way.
- Also has a 3.5 mm **Harp Clock** port and an Expansion Port for the IO Expander.
- Its stated primary purpose is *"precise time-step synchronization between multiple XDAQ systems... especially critical when performing simultaneous XR and XSR experiments on the same subject."* Note that motivating use case is stim-plus-record on one animal, which is not ours.
- ⚠️ **Verbatim: *"Connect one SyncLink to one XDAQ, and connect each XDAQ to its corresponding PC. Each SyncLink operates as the synchronization interface for its associated XDAQ–PC pair."*** See §7.

**Option B — shared TTL line, no SyncLink.** Fan one pulse train into a digital input on both boxes and let the Open Ephys GUI's Record Node do online drift-tracked alignment (it recomputes relative sample rates every 10 s, stated tolerance well under 1 ms). The same pulse train already needs to reach the Pi cameras. For sleep staging on 4 s or 10 s epochs this is comfortably sufficient, and it removes two boxes and their cabling from the build.

**Recommendation: Option B, unless Kontex demonstrates that SyncLink is required for two-box operation under the Open Ephys plugin.** Sub-millisecond is 4,000× tighter than a sleep epoch needs.

---

## 6. Full 32-mouse XDAQ parts list (isolation build)

| # | Item | Part | Qty | Notes |
|---|---|---|---|---|
| 1 | XDAQ acquisition box | **ONE-R1024**-SR64 | **2** | ⚠️ **must be R1024**, not R512 (§2). SR64 sufficient (we do not stimulate). |
| 2 | 200 W DC power adapter | supplied | 2 | included with box |
| 3 | Thunderbolt 3 cable | supplied | 2 | ≤3 m; USB-C will not work |
| 4 | Port Expander | **SAdpt-Port-EXP** | **8** | 4 per box, one per headstage port. $1,525 ea (quote 262024) = **$12,200** |
| 5 | USB-PD AC adapter for Port Expander | supplied | 8 | included with each Port Expander |
| 6 | KonteX HDMI cable, XDAQ → Port Expander | KonteX | **8** | ⚠️ genuine KonteX only |
| 7 | Per-mouse cable, EXP → commutator | KonteX | **32** | ⏳ price |
| 8 | Commutator | **Commutator STD** or **PRO** | **32** | ⏳ price. Use one model across all animals. Compare against Open Ephys OEPS-7761 €2,595 and the Open-MAC DIY route. **Largest single line in the rig.** |
| 9 | Headstage | X3R32 / XeR64 **or** Intan RHD2216 | **32** | ⏳ **gated by §8.** We own ~8 Intan RHD2216 (VERIFY). |
| 10 | Intan interface (only if using Intan headstages) | **SAdpt-XDAQ-OM12(1)** | 32 | $275 ea = $8,800 (quote 262024) |
| 11 | Intan SPI cable (only on the Intan route) | Intan C3213 / C3206 | 32-64 | $415 / $295 |
| 12 | SyncLink | SyncLink | **0 or 2** | ⏳ price. Omit if using shared-TTL sync (§5.8) |
| 13 | Ethernet cable, SyncLink chain | standard | 1 | only with SyncLink |
| 14 | 4 mm banana ground leads | generic | ~6 | Sys↔Chassis bond per box + Faraday cage bond |
| 15 | DB25 breakout board | KonteX | 1-2 | for `DAQ ON` / `Sample CLK` / DI/DO to BNC |
| 16 | Acquisition PC | see §7 | **1 or 2** | **6-core CPU, 16 GB RAM min**; needs **2 native TB3 ports if one PC** |
| 17 | Storage array | see §7 | 1 | sized by sample rate |
| 18 | UPS | — | 1 | 72 h live-animal runs |

Not needed on this build: the Intan C3442 splitter (§4), and the Allego/Radiens licence (we are on the Open Ephys GUI).

---

## 7. The PC question, answered with both sides

**Kontex's documented topology is one PC per XDAQ**, but only in the SyncLink context: *"connect each XDAQ to its corresponding PC. Each SyncLink operates as the synchronization interface for its associated XDAQ–PC pair."*

**Against that**, three facts point to one PC being sufficient when SyncLink is not used:
1. The Open Ephys GUI runs **multiple acquisition devices in one instance**, one source node per device.
2. The ONE+'s own PC requirement is modest: **6-core CPU, 16 GB RAM, at least one Thunderbolt 3 port.** Reference configurations named by Kontex: **Apple Mac Mini M4 Pro 16 GB**, **MSI Cubi with i7 or above**. Two boxes do not need a workstation.
3. Data rate is trivial: 32 mice × 16 ch × 2 bytes = 1.0 MB/s at 1 kS/s, 30.7 MB/s at 30 kS/s.

**The real constraint is Thunderbolt ports, not compute.** One PC needs **two native TB3 ports**, and the manual warns add-in cards are impractical. A Mac Mini M4 Pro has several Thunderbolt ports and is a reference configuration, so this is buyable, just not retrofittable.

⏳ **Ask Kontex whether the Open Ephys XDAQ plugin enumerates and binds two XDAQ devices in one GUI instance.** This is a plugin question, not a physics question.

> [!note] Two PCs is not a disaster, and has one real upside
> Two Mac-Mini-class machines add roughly $2.5-4k, and the Open Ephys GUI is free on both. More interestingly, **two independent PCs restore independent start/stop for each group of 16 mice**, which the move off Allego otherwise removed entirely ([[2026-07-24-daq-32-mouse-final-comparison]] §2.4). If per-user scheduling matters, two PCs are a feature rather than a cost.

**Sample rate sets the storage budget** and is a decision to make before buying disks. XR mode supports **1 to 30 kHz**; at 16-bit across all 32 mice that spans **88 GB/day to 2.65 TB/day**, a 30× swing.

Other ONE+ acquisition specs worth recording for the methods section: 16-bit, input range ±5 mV, input-referred noise **2.4 µV RMS typical**, hardware filter lower cutoff 0.1-500 Hz and upper cutoff 100 Hz-20 kHz, round-trip latency <1 ms, headstage ports **electrically isolated**, OS support Windows/macOS/Linux, XR-mode software **Open Ephys XDAQ plugin, XDAQ-RHX, or Radiens**.

---

## 8. ✅ RESOLVED 2026-07-28 — Intan headstages ARE supported

> [!success] KC Kong (Kontex) confirmed 2026-07-28: **we can use our Intan headstages.**
> This was the single question that could have eliminated the XDAQ column, and it is now answered in XDAQ's favour. The Port Expander path works with Intan RHD2216, so **we do not have to buy 32 KonteX XR headstages**, and XDAQ's per-animal ground isolation does reach our animals.
>
> **The XDAQ column is un-blocked and back to full strength**, since it now combines per-animal isolation, reuse of our existing headstages, the only proven 72 h byte-perfect run on our own bench, and the chassis-ground terminal our Gen-1 Core lacks.
>
> **Still to nail down on the 2026-07-29 call** (see [[2026-07-29-kontex-kc-call-prep-rig-finalization]]): the exact part-by-part chain from an EXP port to an Intan RHD2216, whether isolation is preserved on that path, and whether only P1 of the SAdpt-XDAQ-OM12 is live when it hangs off a single-MISO EXP port.
>
> The doc-derived concern below is retained for the record, since it explains why the question was asked and what to verify against the quote.

**The original concern (now answered, kept for the record):**

- The Port Expander's XR compatibility table names **"X3R32 or XeR64"** as the compatible headstages. Both are **KonteX** parts. **Intan RHD is not listed.**
- The KonteX commutator pages likewise list only KonteX headstages (X3R / X3SR / X6R / XeR / XeSR).
- KonteX's XR headstage line has **no 16-channel bipolar** part. The closest is X3R32 (32 ch). Whether a KonteX XR headstage offers a true **bipolar** differential montage equivalent to the RHD2216 is unknown, and it matters: our entire montage, our CMRR argument, and our shared-ground tolerance all rest on bipolar inputs ([[intan-rhd2216-reference]]).
- A plausible bridge exists on paper — the EXP ports are HDMI, and SAdpt-XDAQ-OM12 is an HDMI-male → Omnetics adapter, so it may physically mate with an EXP port and yield one Intan headstage per isolated EXP port (which is the topology we want anyway). **But no Kontex document shows or endorses this**, and one EXP port carries a single MISO line while the adapter exposes two Omnetics sockets, so at best only P1 would be live.

**Outcome: the first row.** ✅ Reuse our headstages, get per-animal isolation, XDAQ stays fully competitive.

All remaining open questions have moved to the call-prep sheet: **[[2026-07-29-kontex-kc-call-prep-rig-finalization]]**.

## Related
- [[intan-rhd-spi-wiring-and-headstage-limits]] · [[kontex-xdaq-hardware-reference]] · [[2026-07-24-daq-32-mouse-final-comparison]] · [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] · [[eeg-60hz-saga]] · [[intan-rhd2216-reference]] · [[eight-mouse-acquisition-setup]]

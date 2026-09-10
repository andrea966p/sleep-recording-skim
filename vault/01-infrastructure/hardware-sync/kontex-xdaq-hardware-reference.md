---
tags: [reference, kontex, xdaq, hardware, port-expander, synclink, sadpt, scale-up]
created: 2026-07-21
status: complete
source: docs.kontex.io (retrieved 2026-07-21 via curl; raw HTML archived in attachments/kontex-docs-20260721/)
---

# Kontex XDAQ Hardware Reference (models, Port Expander, SyncLink, SAdpt)

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[RIG-EXPANSION-HUB]]** (decision, vendor correspondence, wiring, open items).

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The real, from-the-vendor facts about the XDAQ models and the two accessories that decide how many mice we can record: the **Port Expander** (breaks one port into up-to-4 isolated animal ports) and **SyncLink** (locks multiple XDAQs to one clock). Transcribed straight from docs.kontex.io on 2026-07-21, with the raw HTML archived locally so this survives if the site changes.
> **Why it exists.** We were reasoning from guesses and vendor emails and got the headstage-count logic wrong twice. This is the primary-source correction. Pairs with the physics note [[intan-rhd-spi-wiring-and-headstage-limits]] and the decision [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]].
> **How to read this page.** §1 = the model channel ceilings. §2 = the Port Expander (the big one — it caps animals-per-port AND gives per-animal isolated ground). §3 = SyncLink for scaling past one box. §4 = the SAdpt Intan adapter. §5 = open questions for KC.

> [!info] Sources (retrieved 2026-07-21)
> - `docs.kontex.io/XDAQ/` (index: AIO / ONE+ / CORE2)
> - `docs.kontex.io/XDAQ/ONE/` (ONE+)
> - `docs.kontex.io/System-Adpt/SAdpt-Port-EXP/` (Port Expander)
> - `docs.kontex.io/System-Adpt/SyncLink/`
> - `docs.kontex.io/System-Adpt/SAdpt-XDAQ-OM12/` (Intan RHD adapter)
> - Raw HTML archived: `attachments/kontex-docs-20260721/`. (These pages 403 to automated fetchers; retrieved via curl with a browser user-agent.)

---

## 1. XDAQ model channel ceilings (from the XDAQ index page)

| Model | Max spike channels | XSR (stim-record) | Neuropixels probes | Headstage HDMI ports |
|---|---|---|---|---|
| **CORE2** | **512** | 32 | 2 | 4 (our Gen-1 Core is this class) |
| **ONE+** | **1024** | 128 | 4 | **4 (P1–P4)** |
| **AIO** (top-tier, "OneBox" superset) | **1024** | 128 | 4 | (port count not stated — see §5) |

- ONE+ front panel confirms **4 X-Headstage ports (P1–P4)**, 2× analog BNC (AI/AO-01/02, ±10V 16-bit), 2× digital BNC (DI/DO-01/02, 3.3/5V SW-selectable), DB25 (DI-03…08 + DO-03…08, **DO 3.3V logic**), EXP1/2, 3.5mm audio monitor. Weight 2810 g.

> [!quote] Paper-ready
> The XDAQ ONE+ supports up to 1024 spike-recording channels across four X-Headstage ports; with the Port Expander each port drives up to four single-chip recording headstages, giving a ceiling of 16 independently-grounded animals per ONE+ unit.

---

## 2. Port Expander (SAdpt-Port-EXP) — THE animals-per-port device ⭐

Verbatim: *"designed for researchers looking to maximize the number of animals monitored by the XDAQ system. It allows **each HDMI headstage port in the XDAQ to support up to four animals with XR Headstages** or up to two animals with XSR headstages."*

And crucially for us: *"conditions the control signal and provides **isolated and dedicated electrical systems to each connected headstage. As a result, the ground and reference nodes from each animal's headstage do not interfere with one another.**"*

- Ports **EXP A–D**. *"Depending on the XDAQ model, port EXP C and EXP D might not be available."* → gated by the model's MISO-pair count.
- USB-PD powered, 350 g, Mode switch XR/XSR, XSR adds per-port VStim level select.

> [!important] How this maps to our headstage-count limit (reconciled with [[intan-rhd-spi-wiring-and-headstage-limits]])
> The Port Expander does NOT beat the MISO-pair count — it **is the productized breakout** of a port's MISO pairs into separate, electrically-isolated animal ports.
> - **Core (2 MISO pairs/port):** only EXP A + EXP B available → **2 animals/port × 4 ports = 8.** (Matches the hard Core ceiling.)
> - **ONE+ (4 MISO pairs/port):** EXP A–D → **4 animals/port × 4 ports = 16.**
> Its real value: it gives **independent ground + reference per animal**, directly addressing the inter-animal crosstalk risk from our [[eeg-60hz-saga]] grounding history. This is why KC recommended it unprompted.

---

## 3. SyncLink — scaling past one XDAQ (for 32 mice)

Verbatim purpose: *"enable precise time-step synchronization between multiple XDAQ systems."*

- **One SyncLink per XDAQ.** Connects to its XDAQ via the EXP1/2 HDMI ports; **each XDAQ connects to its own PC** ("Each SyncLink operates as the synchronization interface for its associated XDAQ–PC pair").
- SyncLinks are **daisy-chained with standard Ethernet cables**, Sync **OUT → IN** between units; chain more to add units. Also has a **Harp Clock** 3.5mm port.
- So a **32-mouse rig = 2× ONE+ + 2× SyncLink**, Ethernet-linked, on a shared clock. NOTE the "each XDAQ → its own PC" wording — whether one PC can host both Allego instances is an open question (see §5).

---

## 4. SAdpt-XDAQ-OM12 (XDAQ → Intan RHD adapter)

*"XDAQ to Intan RHD Headstage Adapter... interface the XDAQ acquisition system with Intan's RHD headstages via SPI cables."*

- **HDMI Type A male → XDAQ**; **Omnetics Polarized NANO 12-pin → Intan/Open Ephys** headstage.
- Two connectors **P1 and P2**, both usable with SPI cable to extend/position the headstage. (This is the "bottom/top socket" from our thread; the exact HDMI→MISO pin map is published only as an image.)
- Confirms our Intan RHD2216 path is a supported Kontex-blessed interface.

---

## 5. Open questions for KC (must confirm before quoting)

1. **Does the Port Expander accept our Intan RHD2216 headstages** (via SAdpt-XDAQ-OM12 or an Omnetics path), or only Kontex XR headstages? The 4-animals-per-port + isolation is only useful to us if it drives Intan RHD.
2. **16-mouse ONE+ build of materials:** 1× ONE+ + 4× Port Expander (one per HDMI port) + 16× headstage interface + commutators/cables — confirm exact parts + count.
3. **32-mouse:** confirm 2× ONE+ + 2× SyncLink. **Does it need two PCs, or can one PC run both** XDAQ/Allego instances? How do the two units appear in Allego/Radiens?
4. **Does the AIO reach 32 animals in a single box** (more headstage ports), or is 32 always two units?

## Related
- [[intan-rhd-spi-wiring-and-headstage-limits]] — why 1 chip = 1 MISO line (the physics)
- [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] — the decision + email log
- [[xdaq-core2-manual-reference]] — Core2 DB25 pinout (sync GPIO)
- [[hdmi-spi-adapter-top-socket-vendor-inquiry]] — dead-top-socket root cause
- [[eeg-60hz-saga]] — grounding history (why per-animal isolation matters)

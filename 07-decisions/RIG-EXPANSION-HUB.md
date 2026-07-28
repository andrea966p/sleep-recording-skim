---
tags:
  - hub
  - moc
  - decision
  - scale-up
  - 32-mice
  - xdaq
  - kontex
  - acquisition
  - procurement
created: 2026-07-28
status: live
note_type: map-of-content
---
# ⭐ RIG EXPANSION HUB — 8 → 32 Mice

> [!abstract] START HERE
> **The single entry point for everything about scaling the EEG/EMG rig from 8 mice to 32**: the hardware decision, the three-way vendor comparison, all correspondence with NeuroNexus, Kontex and Open Ephys, the wiring, and what is still open.
>
> This work had spread across 5 folders and ~20 documents with no front door. This page is the front door. **Nothing here is original content**; every section points at the document that owns the detail. If a fact and this page disagree, the owning document wins and this page should be corrected.
>
> **If you read one other page**, make it [[2026-07-24-daq-32-mouse-final-comparison]] (the decision) or [[xdaq-32-mouse-wiring-and-channel-law]] (the physics).

---

## 1. Status right now

| | |
|---|---|
| **Goal** | 32 mice recorded simultaneously, chronic sleep EEG/EMG, 72 h continuous runs |
| **Current rig** | **8 mice**, XDAQ Core Gen-1, fully maxed (8 × 64 = 512 ch) |
| **Leading choice** | **XDAQ: 2× ONE+ (R1024 tier) + 8× Port Expander + our Intan RHD2216 headstages** |
| **Software decision** | ✅ **No Allego licence.** Open Ephys GUI on whatever we buy |
| **Decision state** | 🟡 **Not committed.** Gated on a Kontex quote and the 2026-07-29 call |
| **Next action** | 📞 **Call with KC Kong, 2026-07-29, 11:30 Taipei / 12:30 Korea.** Email sent 2026-07-28 |
| **⚠️ Overriding caveat** | **Surgical yield is still the real bottleneck.** Frontal electrodes open on every mouse, zero scoreable data to date ([[eeg-60hz-saga]]). No acquisition box fixes an open electrode. Buy deliberately, in parallel with fixing the surgery, not instead of it |

---

## 2. The three findings that drive everything

1. **The channel law: animals = recording channels ÷ 64.** Every system reserves a fixed 64-channel slot per headstage regardless of how few channels the chip has. Our 16-channel RHD2216 burns a full slot and wastes 60 of 64. So "1024 channels" means **16 mice**, not 64. Our Core's 8-mouse ceiling is arithmetic (512 ÷ 64), not a defect. → [[xdaq-32-mouse-wiring-and-channel-law]]
2. **32 mice always means two boxes**, in every ecosystem, at any price. The SPI splitter fills a box, it cannot exceed one. → [[xdaq-32-mouse-wiring-and-channel-law]] §4
3. **The acquisition box is not the biggest cost.** Once the licence is gone and the whole rig is priced, the DAQ is only **25-45%** of the budget. **Commutators are the largest single line: €10k to €83k for the same 32 mice**, identical across all three vendors. → [[2026-07-24-daq-32-mouse-final-comparison]] §3.2

---

## 3. The decision, in one table

Everything below assumes the Open Ephys GUI on all three, so software cost is $0 everywhere and stops being a comparison axis.

| | **XDAQ / KonteX** | **Open Ephys** | **Intan direct** |
|---|---|---|---|
| Boxes for 32 | 2× ONE+ **R1024** | 4-8 boards | 4× C3008 |
| **Per-animal isolation** | ✅ Port Expander (paid) | ❌ no product | ✅ built in, free |
| Adapter layers | 3 | 1 | **0** |
| Drives our RHD2216 | ✅ (KC, 2026-07-28) | ✅ own equivalent | ✅ native |
| Pricing | ❌ **still not quoted** | ✅ public (EUR) | ✅ published (USD) |
| Proven on our bench | ✅ **72 h byte-perfect** | ✗ | ✗ |
| DAQ block | ~$57-71k **est** | ~€27k | **$57,000** |
| Complete rig | ~$127-226k | ~€94-186k | ~$124-209k |

**Reading:** XDAQ leads on proven reliability and headstage reuse; Intan is the clean, fully-priced, zero-adapter alternative and the benchmark to hold the Kontex quote against; Open Ephys hardware is out on isolation, though its GUI is what we will run. Full reasoning and the professor-facing summary: [[2026-07-24-daq-32-mouse-final-comparison]] §6.

---

## 4. Document map — what to read for what

### 4.1 Decisions and comparisons (`07-decisions/`)

| Doc | What it owns | Status |
|---|---|---|
| ⭐⭐ [[2026-07-28-daq-research-findings-primary-sources]] | **NEWEST. Primary-source research + 8 CORRECTIONS** to claims below. Read before relying on the older docs | live |
| ⭐ [[2026-07-24-daq-32-mouse-final-comparison]] | 3-way comparison, priced BOMs, professor summary (§6). ⚠️ **partly superseded** by the 2026-07-28 findings | live |
| ⭐ [[2026-07-29-kontex-kc-call-prep-rig-finalization]] | **Tomorrow's call.** 45 questions, live build checklist (§9) | live |
| [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] | Where the 16→32 question started + the full Kontex email thread | open |
| [[2026-07-21-openephys-acquisition-board-scale-up-option]] | The Open Ephys option, standalone | open |
| [[2026-07-21-kontex-kc-call-prep]] | Prep for the **first** KC call (2026-07-21) | historical |
| [[2026-07-23-daq-ecosystem-comparison-xdaq-vs-openephys]] | 2-way, 16-mouse predecessor | 🚫 **superseded** by the 2026-07-24 doc |

### 4.2 Physics and hardware references (`06-references/`)

| Doc | What it owns |
|---|---|
| ⭐ [[xdaq-32-mouse-wiring-and-channel-law]] | **The channel law**, complete wall-socket-to-mouse wiring, why the splitter cannot reach 32, the ONE+ ordering trap |
| [[intan-rhd-spi-wiring-and-headstage-limits]] | Why 1 chip = 1 MISO line, from Intan's datasheets. The ruled-out ideas |
| [[intan-rhd2216-reference]] | The chip itself: bipolar, 16 ch, no reference pin |

### 4.3 Vendor hardware docs (`01-infrastructure/hardware-sync/`)

| Doc | What it owns |
|---|---|
| [[kontex-xdaq-hardware-reference]] | Kontex primary-source pass (models, Port Expander, SyncLink, SAdpt), 2026-07-21 |
| [[kontex-developer-portal-notes]] | **libxdaq, Thunderbolt, and the Linux story.** Relevant to the ONE+ (see §6) |
| [[xdaq-core-gen1-ubuntu-driver]] | Our **current** Gen-1 Core driver path (FrontPanel + `plugdev` udev) |
| [[xdaq-core2-manual-reference]] | Core2 DB25 pinout and specs |

### 4.4 Vendor correspondence (`01-infrastructure/vendor-correspondence/`)

| Doc | Thread |
|---|---|
| ⭐ [[kontex-call-confirmation-email-2026-07-29]] | **Sent 2026-07-28.** Confirms the call + 5 advance questions |
| [[neuronexus-inquiry-email]] | NeuroNexus / Kontex, multi-round: DB25 sync, then Linux/driver routed to KC |
| [[hdmi-spi-adapter-top-socket-vendor-inquiry]] | The dead top SPI socket. **Resolved: by design on the Core, not a defect, do NOT RMA** |
| [[openephys-inquiry-email]] | Open Ephys thread + Margarida's reply (extension board dead, no isolation product) |

### 4.5 Procedures affected by the expansion (`02-procedures/`)

| Doc | Relevance |
|---|---|
| [[eight-mouse-acquisition-setup]] | The **current** 8-mouse topology the expansion replaces |
| [[openephys-gui-setup-xdaq-sleep-eeg]] | **OE GUI on XDAQ, already validated on our Core.** See §6 |
| [[multi-user-independent-recording-schedules]] | ⚠️ **Partly invalidated** by dropping Allego. See §7 |
| [[allego-electrode-setup-sleep64]] | The electrode SOP. Survives the box change; the software half does not |

---

## 5. Vendor timeline

| Date | Event |
|---|---|
| 2026-05-28 | Linux/driver questions routed to KC Kong at Kontex ([[kontex-developer-portal-notes]]) |
| 2026-07-14 | Dead top SPI socket raised → **by design, MISO3/4 absent on the Core** ([[hdmi-spi-adapter-top-socket-vendor-inquiry]]) |
| 2026-07-18 | Jeff (NeuroNexus) confirms the 8-headstage Core ceiling is a hard wire-count limit |
| **2026-07-21** | **First KC Kong call.** Custom 4-socket adapter impossible; Port Expander recommended for per-mouse grounding; 2nd XDAQ = 2nd Allego seat; ~40 cm headstage run too long |
| 2026-07-23 | Kontex **quote 262024, $10,002.89** — Port Expander retrofit for the **current 8-mouse Core only**, NOT the 32-mouse build. Valid to 2026-08-20, confidential |
| 2026-07-23 | Open Ephys reply (Margarida): extension board dead, no isolation product, software free |
| 2026-07-28 | ✅ **KC confirms Intan headstages work with the Port Expander** → XDAQ un-blocked |
| 2026-07-28 | Email sent confirming tomorrow's call + 5 advance questions |
| **2026-07-29** | 📞 **Finalization call, 11:30 Taipei / 12:30 Korea** |

---

## 6. 🔎 Two things already in the vault that answer tomorrow's questions

Found while consolidating. Both narrow questions we were about to ask cold.

> [!success] Open Ephys GUI on XDAQ is ALREADY VALIDATED on our own hardware
> [[openephys-gui-setup-xdaq-sleep-eeg]], 2026-07-23: OE **fully enumerates and controls our XDAQ Core**, one headstage on port B detected, 32 channels. A working signal chain is documented.
>
> **But there is a real packaging bug worth raising with KC:** XDAQ-OE **v0.4.4-API10** is built for a non-versioned `shared/` folder while GUI **1.1.0** uses `shared-api10/`. The plugin fails to load until two symlinks are created, and the fix must be re-applied after every plugin reinstall. Ask Kontex for a fixed build.
>
> **Consequence for the call:** "will the OE GUI work" is answered for one box. The genuinely open part is **two boxes, Port Expanders, and per-animal stream identification.**

> [!success] Linux support: a driver path already exists, so ask a narrower question
> [[kontex-developer-portal-notes]]: **ONE+ / Core2 / AIO are Thunderbolt**, and the driver is the **standard Linux `thunderbolt` kernel module plus the `boltd` authorisation daemon**, not a proprietary blob. libxdaq's tested toolchain is **Ubuntu 24.04 + GCC 14.2.0**, which our host matches. (Our current Gen-1 Core is different: Opal Kelly USB, FrontPanel + `plugdev` udev, per [[xdaq-core-gen1-ubuntu-driver]].)
>
> **Consequence for the call:** do not ask "is there a Linux driver". Ask the narrow, still-open question: **what is the exact Ubuntu 24.04 enrolment procedure for a ONE+** (group membership, udev rules for the Thunderbolt char devices, headless `boltd` setup), which was routed to KC back in May and never fully closed.

---

## 7. Open items

**Blocking the purchase, for Kontex (all on tomorrow's call → [[2026-07-29-kontex-kc-call-prep-rig-finalization]]):**
- ⏳ **A written package quote**, volume-discounted, delivered to KAIST. The XDAQ price is still an estimate and this is now the top blocker
- ⏳ **The exact EXP-port-to-Intan-RHD2216 chain**, part by part
- ⏳ **Two PCs, SyncLink, and how either behaves under the Open Ephys GUI**
- ⏳ **Commutator pricing with a volume discount**, STD versus PRO, and Intan compatibility
- ⏳ Ubuntu 24.04 enrolment procedure for the ONE+ (narrowed, see §6)
- ⏳ Whether R512 → R1024 is a field firmware upgrade

**Ours to answer, costing nothing but an afternoon, and blocking the budget:**
- ⏳ **Commutator inventory.** What do the current 8 mice use, how many do we own, do they scale? Swings the budget by ~€70k, more than the vendor choice does
- ⏳ **Headstage count.** Believed 8; an earlier note claimed 32. Worth ±$20k
- ⏳ **Sample rate.** 1 kHz versus 30 kHz is a 30× storage difference (88 GB versus 2.65 TB per day, all 32 mice)

**Consequences to accept knowingly:**
- ⚠️ **Per-mouse independent start/stop is gone** with Allego. Under the Open Ephys GUI, start/stop is global on all three systems; separate files per animal still work. Plan: record continuously, slice per user offline. This partly invalidates [[multi-user-independent-recording-schedules]]. Two acquisition PCs would restore independent control per group of 16
- ⚠️ **Leaving Allego means rebuilding the analysis pipeline** (sleep64 map, XDAT reader, `eeg-emg-analysis`) regardless of which box we buy. Excluded from the vendor evaluation by decision, since code can be rewritten and a rig cannot

---

## 8. Superseded or corrected, so nobody re-chases it

- 🚫 [[2026-07-23-daq-ecosystem-comparison-xdaq-vs-openephys]] — the 2-way 16-mouse comparison. Use the 2026-07-24 3-way doc.
- 🚫 **"More channels means more mice."** No: channels ÷ 64 = mice. A 1024-channel box records 16.
- 🚫 **"A splitter can double a Port Expander to 32 per box."** No, on the slot ceiling alone. (The supporting MISO-line argument is our inference, not a vendor statement; the slot ceiling is doc-sourced and binds independently.)
- 🚫 **"Two mice per port share one SPI cable."** Corrected 2026-07-28: we place the splitter **at the XDAQ port**, so **each animal has its own cable**. They share the port's ground *domain*, not a conductor.
- 🚫 **"The dead top SPI socket is a defect."** By design on the Core, MISO3/4 physically absent. Do NOT RMA.
- 🚫 **"A second XDAQ needs a second PC because of Allego licensing."** That was a licence artifact. Under the Open Ephys GUI the question is entirely different, and still open.
- 🚫 **"Open Ephys multi-board sync is homebrew and drift-prone."** Their Record Node does online sync off a shared TTL, recomputing rates every 10 s, under 1 ms — but only **within a single GUI instance**.

---

## 9. Related outside the expansion

[[eeg-60hz-saga]] (why isolation matters, and the real bottleneck) · [[2026-07-27-video-eeg-sync-recording-architecture]] (camera sync, which shares the TTL pulse train) · [[eight-mouse-acquisition-setup]] (what we run today) · [[2026-07-02-eeg-recording-checkpoint]] (the 72 h endurance proof)

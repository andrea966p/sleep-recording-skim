---
type: reference
area: rig-expansion
status: active
status-note: "complete"
tags: [reference, intan, spi, headstage, xdaq, miso, channel-limits, datasheet]
created: 2026-07-21
source: 06-references/datasheets/Intan_RHD2000_SPI_cable.pdf, Intan_RHD2000_dual_headstage_adapter.pdf
---

# Intan RHD SPI Wiring & the Headstage-Count Limit (why Core = 8, One+ = 16)

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[RIG-EXPANSION-HUB]]** (decision, vendor correspondence, wiring, open items).

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The physical reason a given data acquisition box can only record so many mice at once, taken straight from the Intan cable and adapter datasheets (page-cited). This is the note to read before anyone proposes "clever" ways to squeeze more animals onto our XDAQ.
> **Why it exists.** We kept confusing ourselves (and nearly emailed the vendor a wrong argument) by reasoning about *channels*. The real limit is **MISO lines**, i.e. physical wires. This note fixes that once, so we stop re-chasing it. See the vendor thread in [[hdmi-spi-adapter-top-socket-vendor-inquiry]] and the device decision in [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]].
> **How to read this page.** §1 is the one hard fact. §2 says why small headstages don't help. §3 maps it to our XDAQ. §4 lists the ideas we ruled out so nobody re-proposes them.

> [!quote] Paper-ready
> Each Intan RHD SPI interface cable carries five LVDS twisted pairs — chip-select, serial clock, MOSI, and **two independent MISO return lines** — so a single cable supports at most **two RHD2000 chips**, which share command signals but each drive their own MISO line. The number of simultaneously recorded headstages is therefore set by the number of MISO lines the acquisition system exposes, independent of the channel count of each chip.

> [!info] Sources
> - `06-references/datasheets/Intan_RHD2000_SPI_cable.pdf` — "RHD SPI Interface Cable/Connector Specification" (28 Feb 2013; upd. 27 May 2021), p1 + p3 table + p4 pinout.
> - `06-references/datasheets/Intan_RHD2000_dual_headstage_adapter.pdf` — "RHD Dual Headstage Adapter" (C3442), p1–p2.
> - XDAQ MISO-pairs-per-port mapping: vendor-authoritative, from Jeff (NeuroNexus) and KC Kong (Kontex) emails, logged in [[hdmi-spi-adapter-top-socket-vendor-inquiry]] and [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]].

---

## 1. The one hard fact — a SPI cable = 2 MISO lines = 2 chips

From the SPI cable spec (p1, verbatim):

> "Each RHD SPI cable contains 12 conductors: two thicker wires for power and ground, and ten thinner wires arranged in **five twisted pairs** for five LVDS digital signals. The five LVDS signal paths in the cable allow for **two MISO lines so that two RHD chips may send data over one cable** provided they both receive the same commands from the single MOSI line."

The five LVDS pairs are: **CS, SCLK, MOSI, MISO1, MISO2**.

- **CS, SCLK, MOSI are shared** — broadcast identically to both chips.
- **MISO1 and MISO2 are separate return lines** — one chip drives MISO1, the other drives MISO2.
- Spec table (p3), verbatim: **"Number of Intan RHD2000 chips supported per cable = 2 — Two chips supported, provided they receive identical command sequences."**

The **RHD Dual Headstage Adapter (C3442)** is exactly this: it lets "two RHD headstages... be connected to a single SPI interface cable... using **both MISO lines** (MISO1 and MISO2)." Each amplifier board's MISO goes to one of the two lines (adapter datasheet p2).

> [!danger] It is NOT dual-data-rate (DDR)
> There is no trick where two chips share one MISO line on rising/falling clock edges. MISO1 and MISO2 are **two physically separate LVDS twisted pairs**, each with its own 100 Ω termination resistor inside the controller FPGA (adapter datasheet p3). **One chip = one MISO line. Full stop.**

---

## 2. Why channel count does NOT change the limit

The limit counts **chips / MISO lines**, not channels.

- One chip = one MISO line, whether it is a **16ch RHD2216** or a **64ch RHD2164**.
- Our RHD2216 uses only ~4 of its 16 channels (bipolar EEG + bipolar EMG + optional ECG/LFP), yet it **still occupies a whole MISO line**.
- You **cannot** pack two 16ch chips onto one MISO line to "use the spare 48 channels." The MISO line carries one chip's serial stream, period.

> [!warning] So "small headstages → more animals per port" is FALSE
> Our low per-mouse channel count buys us tiny data/storage and lots of unused per-chip channel headroom — it buys us **zero extra headstages**. Scaling animals = adding MISO lines = a bigger DAQ.

---

## 3. Mapping to our XDAQ (vendor-authoritative)

Kontex/NeuroNexus call one MISO LVDS line a **"MISO pair."** One MISO pair = one chip = one mouse headstage.

| DAQ | MISO pairs / HDMI port | Chips / port | HDMI ports | **Max headstages (mice)** |
|---|---|---|---|---|
| **XDAQ Core (our Gen-1)** | 2 (MISO1, MISO2) = 128ch | 2 | 4 | **8 — HARD** |
| **XDAQ One / One+** | 4 (MISO1–4) = 256ch | 4 | 4 | **16** |
| 2× One+ + SyncLink | 4 | 4 | 8 total | **32** |

- The **SAdpt-HDMI-OM12** (a.k.a. SAdpt-XDAQ-OM12) top SPI socket is wired to **MISO3/MISO4**. Those exist on the One/One+ (4 pairs) but are **physically absent on the Core** (only MISO1/2). That is why the top socket is dead on the Core **by design** — not a defect, do NOT RMA. See [[hdmi-spi-adapter-top-socket-vendor-inquiry]].
- Our validated 8-mouse rig = 4 ports × 1 C3442 (2 chips) on the bottom socket = 8. That already **fully uses all 8 of the Core's MISO lines.** There is no spare MISO line hiding anywhere.

---

## 4. Ideas we RULED OUT (logged so nobody re-chases them)

> [!danger] All three of these are physically impossible on the Core
> - ❌ **"DDR — 2 chips on one MISO pair, so 8 pairs × 2 = 16 on the Core."** (Claude's 2026-07-21 hypothesis.) WRONG — it is not DDR; MISO1/MISO2 are two separate wires, one chip each. The C3442's two chips already consume **both** MISO lines of one cable.
> - ❌ **"4 SPI sockets per HDMI port at 32ch each, using the double-64 capacity."** (Professor's idea.) WRONG — the "double 64" IS the 2 MISO lines, which IS the 2 chips. You cannot subdivide a MISO line into two 32ch chip slots.
> - ❌ **"$75 re-routing adapter gets the Core to 16."** The re-router only reshuffles the Core's two real MISO pairs (MISO1, MISO2) between the two SPI sockets; it cannot conjure MISO3/MISO4, which the Core hardware does not have. Net Core ceiling stays **8**.
>
> **The Core absolute maximum is 8 mice. This is a wire-count limit, not a firmware limit — it cannot be unlocked.**

## What actually scales

- **16 mice** → 1× **XDAQ One / One+** (4 MISO pairs/port).
- **32 mice** → **2× One+ + SyncLink** (Gen2 sync, shared clock).
- **Independent per-animal ground/reference** → **Port Expander (SAdpt-Port-EXP)**. Vendor docs (retrieved 2026-07-21, [[kontex-xdaq-hardware-reference]]): it breaks one HDMI port into **up to 4 isolated animal ports (EXP A–D) with XR headstages** — EXP C/D unavailable on the Core, so **2/port on Core = 8, 4/port on ONE+ = 16.** It does NOT beat the MISO-pair count; it productizes the breakout AND gives each animal its own ground/reference so they don't interfere. Directly relevant to our grounding/60 Hz history ([[eeg-60hz-saga]]).

## Related
- [[kontex-xdaq-hardware-reference]] — Kontex primary-source docs (models, Port Expander, SyncLink, SAdpt)
- [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] — the device decision + full Kontex email thread
- [[hdmi-spi-adapter-top-socket-vendor-inquiry]] — dead-top-socket root cause (MISO3/4 absent on Core)
- [[intan-rhd2216-reference]] — the chip itself (bipolar, 16ch, no reference pin)
- [[eight-mouse-acquisition-setup]] — the current 8-mouse bottom-socket + C3442 topology
- [[first-headstage-connection]] — bring-up log

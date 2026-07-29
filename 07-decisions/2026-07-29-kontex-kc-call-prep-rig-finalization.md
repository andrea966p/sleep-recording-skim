---
tags:
  - decision
  - kontex
  - xdaq
  - call-prep
  - scale-up
  - 32-mice
  - rig-finalization
created: 2026-07-28
updated: 2026-07-29
status: live
call_date: 2026-07-29
counterpart: KC Kong (KonteX Neuroscience)
attendees: Andrea, Prof. Kim Staci Jakyong, KC Kong
---
# 📞 KONTEX CALL — 2026-07-29, 11:30 Taipei / 12:30 Korea

> [!important] THIS IS THE ONLY DOCUMENT YOU NEED IN THE CALL.
> Self-contained on purpose. Nothing here requires opening another note.
> **§A** brief the professor · **§B** what is already settled, do not spend call time on it · **§C** the 11 questions that matter · **§D** the build and the money · **§E** what we must leave with · **§F** notes.
> Everything we know and how we learned it is in the appendix (§G), not in the call flow.

---

## §A. BRIEF THE PROFESSOR (send before the call)

**What we are buying.** An acquisition system to record **32 mice simultaneously** for chronic sleep EEG/EMG in continuous 72-hour runs. We record 8 today and that rig is completely full.

**Proposed build.** 2 × XDAQ ONE+ at the 1024-channel tier + 8 × Port Expander, reusing the Intan RHD2216 headstages we already own.

**Three facts that frame everything:**

1. **A "channel" is really a mouse slot.** Every system reserves 64 channels per animal no matter how few we use. **Mice = channels ÷ 64.** A 1024-channel box records **16 mice, not 64**. Our 8-mouse ceiling is 512 ÷ 64 = 8. It was arithmetic all along.
2. **32 mice always means two boxes.** No splitter, adapter or configuration changes this, in any ecosystem, at any price.
3. **The Port Expander is mandatory to reach 16 mice per box** — it is not an optional extra we can drop to save money.

**Decisions already taken:**
- **No Allego software licence** ($2,500–5,000/seat). It does not deliver the per-animal scheduling that justified it. The free Open Ephys GUI replaces it.
- **No commutators in this purchase.** We keep our slip rings. At 32 units they would have been the single largest line in the budget.
- **Recording start/stop will be global**, not per-mouse. No system offers per-animal scheduling at 16 animals. We record continuously and separate each user's data afterwards.

**The caveat, stated honestly.** This purchase is **not** our current bottleneck. Frontal electrodes are open on every mouse implanted so far and we have no scoreable data yet. No acquisition box fixes an open electrode. Decide carefully, **in parallel with** fixing surgical yield.

**Full written comparison:** `~/Downloads/DAQ-comparison-32-mice.docx`

---

## §B. SETTLED — DO NOT SPEND CALL TIME ON THESE

| Fact | How we know |
|---|---|
| Mice = XR channels ÷ 64. Core 512→8, ONE+ R1024→**16**, AIO→16 | Two independent Kontex figures |
| 32 mice = 2 boxes. Splitter fills a box, never exceeds it | Kontex + Intan datasheets |
| **Intan RHD2216 headstages work with the Port Expander** | **KC confirmed 28 Jul** |
| Port Expander = **$1,525/unit** | Kontex quote 262024 |
| SAdpt-XDAQ-OM12 = **$275/unit** | Kontex quote 262024 |
| Port Expander is **mandatory** for 16/box | NNX manual: "16 X3R32*", footnote "* Requires Port Expander" |
| Kontex officially supports the **Open Ephys GUI** for XR mode | kontex.io/software |
| **Open Ephys GUI already runs on our XDAQ Core** (1 headstage, 32 ch, 23 Jul) | Our own bench |
| A **Linux driver path exists** — Thunderbolt + stock `boltd`, libxdaq tested on Ubuntu 24.04 | Kontex developer portal |
| ONE+ has **Sys GND + Chassis GND** with per-node ESD DIP earth-coupling switches | NNX manual p.22 |
| Tether at 22.5 cm is fine on the digital side | KC's own 40 cm guidance |
| Global recording start/stop | Confirmed by **both** Kontex and Open Ephys |

---

## §C. THE 11 QUESTIONS THAT MATTER

### 🔴 Money — ask first, everything else is secondary

**Q1. ⭐ The package quote.** Itemised, volume-discounted, delivered to KAIST Daejeon:
`2 × ONE-R1024-SR64` · `8 × SAdpt-Port-EXP` · `32 × SAdpt-XDAQ-OM12` · `8 × KonteX HDMI cable` · optional `2 × SyncLink` · `DB25 breakout`.
**We have Port Expander ($1,525) and OM12 ($275). What we do not have is the ONE+ unit price — that is the single biggest unknown in the whole decision.** Lead time, shipping, import duty and VAT handling.

**Q2. Can the purchase be phased?** One ONE+ and 4 Port Expanders now for 16 mice, the second set later. Does phasing forfeit the volume discount?

**Q3. Commutators — price and discount only.** We are keeping our slip rings, so this is opportunistic: what would Standard and PRO cost at 32 units with a discount? Do they work with an Intan RHD2216 headstage?

### 🟠 What changes the build

**Q4. ⭐⭐ What does the Port Expander's ground isolation buy us, in microvolts?**
Open Ephys confirmed in writing (28 Jul) that with a **bipolar** montage *"this would already be independent referencing per animal, because each electrode is referenced to a local electrode on the same animal."* Our RHD2216 has no reference pin, so **we already have per-animal referencing for free**. That leaves the Port Expander adding **ground** isolation only. Our own bench cleared the shared port ground as a 60 Hz source, and a published 4-mouse shared-ground study measured inter-animal contamination at chance level.
**Is there a measured figure? Or is the honest answer that we buy it as a port multiplier and treat isolation as a bonus?**
Related: your figure says **SYS GND should be bonded to the XDAQ HDMI ground**, so isolation must sit downstream, per EXP port. Where exactly is the barrier, and what is its capacitance?

**Q5. ⭐ Why two PCs, and is SyncLink actually needed?**
Three parts, and the first may dissolve the other two:
- **(a)** Mice 1-16 on box A and 17-32 on box B are **different animals in different chambers**. Nothing in sleep scoring compares them sample-by-sample. What we need is each mouse aligned to its own video, which we already do with a TTL pulse train. **Do the two boxes need to be sample-locked at all?** If not, SyncLink comes out of the build.
- **(b)** If two PCs are genuinely required, **why**? Is it the Open Ephys plugin enumerating one device per instance, or the driver, or Thunderbolt? Data rate is not the reason (31 MB/s at 30 kHz for all 32 mice).
- **(c)** If SyncLink is bought, **how does it behave under the Open Ephys GUI, and what appears in the recorded data?** Do the two boxes share a sample clock so that sample N on box A equals sample N on box B? Open Ephys synchronises within a single GUI instance, so with two PCs the GUI cannot sync across them.

**Q6. Ordering tier.** Confirm **ONE-R1024**, since R512 gives only 8 mice. Is **SR64 vs SR128** irrelevant to us (we never stimulate)? Is **R512 → R1024 a field firmware upgrade** or must it be specified at purchase?

**Q7. Exact part chain and quantities**, EXP port → Intan RHD2216, so we can put it on a purchase order without guessing. Can we reuse our existing 8 headstages and existing SAdpt-XDAQ-OM12 units?

### 🟡 Operational

**Q8. Ubuntu 24.04 headless setup.** A driver path exists; what we need is the **enrolment procedure** — group membership, udev rules for the Thunderbolt character devices, headless `boltd`. Which kernel and `boltd` versions does Kontex test against?

**Q9. Open Ephys plugin specifics.** Does it (a) bind **two XDAQ devices** in one instance, (b) enumerate a **Port Expander** so the 4 animals on a port appear as separately identifiable streams, (c) expose the **DB25 signals** (`DAQ ON`, `Sample CLK`, DI/DO) for our camera sync?
Also report: **XDAQ-OE v0.4.4-API10 has a packaging bug** — built for `shared/` while GUI 1.1.0 uses `shared-api10/`, so it fails to load until two symlinks are made by hand, and the fix must be re-applied after every reinstall. Is a fixed build coming?

**Q10. Our 36 cm analog run.** The electrode-to-headstage run is still ~36 cm against Intan's "ideally under 10 cm". Headstages sit at the chamber top and our slip ring is on the **analog** side, before the headstage. **What does Kontex recommend for this topology? Is there a head-mountable preamp option?**

**Q11. Physical layout.** With 2 boxes + 8 mains-powered Port Expanders + 32 chambers, the long run is rack-to-chamber. Our default is Port Expanders at the rack (short HDMI to the box, long run to the animal). **Which does Kontex recommend, and what is the maximum supported length on the long link?** What KonteX HDMI cable lengths exist?

### ⚪ Only if time allows
AIO vs ONE+ — what is the integrated video processor, does it hardware-timestamp frames against the neural clock, and what is the price delta? · Can our Gen-1 Core serve as a third unit (+8 mice), or is there a trade-in? · Any customer running 16+ animals continuously for multiple days? · Warranty and RMA turnaround from Korea.

---

## §D. THE BUILD AND THE MONEY — fill in live

| # | Item | Part | Qty | Unit | Extended | ✓ |
|---|---|---|---|---|---|---|
| 1 | XDAQ ONE+, 1024 tier | ONE-R1024-SR64 | **2** | **⏳ THE UNKNOWN** | ⏳ | ☐ |
| 2 | Port Expander | SAdpt-Port-EXP | **8** | **$1,525** | **$12,200** | ☐ |
| 3 | Intan interface adapter | SAdpt-XDAQ-OM12(1) | **32** | **$275** | **$8,800** | ☐ |
| 4 | KonteX HDMI cable, box → Port Expander | ⏳ | **8** | ⏳ | ⏳ | ☐ length? |
| 5 | SyncLink | SyncLink | **0 or 2** | ⏳ | ⏳ | ☐ needed? |
| 6 | DB25 breakout board | ⏳ | 1–2 | ⏳ | ⏳ | ☐ |
| 7 | 200 W PSU + Thunderbolt cable | supplied | — | incl | — | ☐ |
| 8 | Acquisition PC | — | **1 or 2** | — | — | ☐ spec? |
| — | **PACKAGE PRICE, discounted** | — | — | — | **⏳ GET IN WRITING** | ☐ |

**Known so far: $21,000** (items 2 + 3). Everything else hinges on the ONE+ unit price.

**Not buying:** commutators (keeping slip rings) · Allego licence · C3442 splitters (cannot exceed the box ceiling and would undo the isolation).

---

## §E. WHAT WE MUST LEAVE WITH

1. ⭐ **The ONE+ unit price and a written package quote** to KAIST, with lead time
2. **Whether SyncLink is needed**, and if so how it behaves under the Open Ephys GUI
3. **Why two PCs**, and each machine's specification
4. **The exact part chain** EXP → RHD2216, with quantities
5. **Confirmation of the R1024 tier** and whether it is field-upgradable
6. **An answer on what the ground isolation is worth**, even if the answer is "unmeasured"
7. **Ubuntu headless enrolment procedure**
8. **A recommendation for the 36 cm analog run**

---

## §F. NOTES DURING THE CALL

*(blank — fill live)*

---

## §G. APPENDIX — what we learned, and when

Kept out of the call flow deliberately. This is the audit trail, not the agenda.

| Date | Learned | Source |
|---|---|---|
| 2026-05-28 | Linux/driver questions routed to KC; ONE+/Core2/AIO are Thunderbolt, driver = stock `thunderbolt` + `boltd` | Kontex developer portal |
| 2026-07-14 | Dead top SPI socket is **by design** on the Core (MISO3/4 absent). Not a defect, do not RMA | NeuroNexus |
| 2026-07-18 | The 8-headstage Core ceiling is a hard wire-count limit | Jeff, NeuroNexus |
| **2026-07-21** | **First KC call.** Custom 4-socket adapter impossible · Port Expander recommended for per-mouse grounding · 2nd XDAQ = 2nd Allego seat · ~40 cm headstage run too long | KC Kong |
| 2026-07-23 | **Quote 262024, $10,002.89** — Port Expander retrofit for the **current 8-mouse Core only**. Port Expander $1,525, SAdpt-XDAQ-OM12 $275, SAdpt-CORE-OM12 $350. Valid to 2026-08-20, confidential | Kontex |
| 2026-07-23 | Open Ephys GUI **validated on our own XDAQ Core** (1 headstage, 32 ch). Found XDAQ-OE v0.4.4 packaging bug | Our bench |
| 2026-07-23 | Open Ephys reply 1: extension board **dead**; framed board as "max 4 animals"; RHD2216 supported; software free; **no isolation product** | Margarida, Open Ephys |
| **2026-07-28** | **KC confirms Intan headstages work with the Port Expander** → XDAQ un-blocked | KC Kong |
| 2026-07-28 | **The channel law**: mice = channels ÷ 64. ONE+ sold in R512 (8 mice) and R1024 (16 mice) tiers; ports are licence-gated. **Port Expander mandatory for 16/box** | NNX manual (not on the Kontex website) |
| 2026-07-28 | **Our Core has NO isolation at all** — "Signal Isolation: No", one power circuit for all 8 mice. Even ONE+ without an expander commons ports 2-4 | NNX manual p.9, p.22 |
| 2026-07-28 | Vendor **hedges** its own isolation claim: *"In theory... however... it is best for users to experiment with various ground settings"* | NNX manual §4.3 |
| 2026-07-28 | **Allego cannot schedule 16 animals independently** — per-port only, ports cap at 8, ONE+ has 4. "Split-ports mode" is documented nowhere → **do not buy the licence** | Radiens API docs |
| 2026-07-28 | Intan **no longer sells directly**; White Mountain Systems is sole distributor, no Korea presence, closed until 2 Aug, 90-day warranty | intantech.com |
| 2026-07-28 | Intan's isolation claim is **unspecified** — "isolated from the controller and from earth ground" names neither other ports; no barrier capacitance published | Intan user guide |
| 2026-07-28 | Literature: 4 mice on one **shared-ground** Open Ephys board, 48 h chronic, inter-animal correlation **at chance** | eNeuro 2022 |
| 2026-07-28 | Intan: analog electrode-to-headstage run **ideally under 10 cm**; headstage GND must **not** connect to the Faraday cage | Intan noise app note |
| **2026-07-28** | **Open Ephys reply 2: bipolar already gives independent per-animal REFERENCING.** Port Expander therefore adds **ground** isolation only → justify it as a **port multiplier**, not the 60 Hz fix. Also: 8 animals per board confirmed; per-animal ground isolation impossible on their hardware; global start/stop confirmed | Open Ephys support |
| 2026-07-29 | Port Expander is **mains powered** (5 V 1 A USB-C). The March 2024 manual's "battery powered" line describes an earlier revision | Kontex front-panel figure |

### Corrections we made to our own earlier beliefs
- ~~"Our 8 mice sit in isolated pairs"~~ → they share **one** power circuit across all four ports
- ~~"The radiens API gives per-animal scheduling"~~ → per **port**, and 16 animals do not map onto 4 ports
- ~~"Intan ports are confirmed isolated"~~ → implied, never stated port-to-port, no specification
- ~~"The Port Expander is battery powered"~~ → mains powered on the current revision
- ~~"Open Ephys board maxes at 4 animals"~~ → 8, vendor-confirmed in writing
- ~~"Shortening the analog run is free"~~ → lid-mounting is a published design; the real fix is head-mounted amplification, a rig redesign
- ~~"Proven on our own bench is a differentiator"~~ → dropped; all three products are built for this

---
tags: [decision, hardware, xdaq, kontex, acquisition, scale-up, email-log]
created: 2026-07-21
status: open
---

# Acquisition Device for 16 (→32) Mice + Kontex Email Thread (Jul 2026)

> [!abstract] TL;DR
> We want a rig that records **at least 16 mice simultaneously**, and ideally scales to **32** later. Question was framed as Intan vs Open Ephys, but for us the real fork is which **DAQ** drives our existing Intan RHD2216 headstages. The physics is now nailed (see [[intan-rhd-spi-wiring-and-headstage-limits]]): **our XDAQ Core is hard-capped at 8 mice — a wire-count limit, not firmware.** No adapter, splitter, re-route, or "small-headstage" trick beats it. Path to 16 = one **XDAQ One+**; path to 32 = **two One+ linked by SyncLink**. Add the **Port Expander** for independent per-animal grounding.
>
> **Still open:** get an official quote (One+ config for 16, plus 32-mouse plan, plus Port Expander), and a video call with KC that Prof. Kim Staci Jakyong will join.

> [!warning] Two wrong ideas were killed here — do not revive them
> - Claude's "DDR → 16 on the Core" argument: WRONG.
> - Professor's "4 sockets/port at 32ch, using the double-64" idea: WRONG.
> Both die on the same fact: **1 RHD chip = 1 MISO line, and channel count is irrelevant.** Full reasoning in [[intan-rhd-spi-wiring-and-headstage-limits]].

---

## The goal

- **Minimum: 16 mice recorded at once.** Future: **32.**
- Per mouse: one Intan **RHD2216** bipolar headstage, but only ~4–6 channels used (bipolar EEG pair + bipolar EMG pair + one optional ECG or LFP). Channel budget is trivial; **physical headstage count is the only constraint.**
- New rig, likely another building. Video exists but hardware video-sync is NOT a concern for this decision. Primary driver: **reliability + reuse** of our existing Intan/Allego pipeline.

## Why it's really "which DAQ," not "Intan vs Open Ephys"

Both ecosystems run the **same Intan RHD chips**. Our RHD2216 headstages, tethers, slip-rings work on either. The real differences are the DAQ box, the software, and how many MISO lines (= headstages) it exposes. Raw single-box ceilings for individual 16ch mice:

| Box | Max headstages / box |
|---|---|
| Single Open Ephys Acquisition Board | 8 (4 tethers × 2) |
| Intan RHD Recording Controller 512 (C3004) | 8 (4 ports × 2) |
| Intan RHD Recording Controller 1024 (C3008) | 16 (8 ports × 2) |
| XDAQ Core (ours) | **8** |
| XDAQ One / One+ | **16** |

Reliability + reuse points at staying in the **XDAQ + Allego/Radiens** world we already run (our sensor maps, analysis code, SOPs all carry over). So: **XDAQ One+.**

## The Kontex (KC Kong) email thread — Jul 2026

Continuation of the dead-top-socket thread in [[hdmi-spi-adapter-top-socket-vendor-inquiry]].

1. **KC's re-routing-adapter offer.** After our top-socket questions, KC offered to design a **$75/ea** adapter that sits between the XDAQ and the SAdpt-HDMI-OM12 and re-routes so "RHD Port 1 receives MISO1 + MISO3, RHD Port 2 receives MISO2 + MISO4," enabling the top socket. (On the Core, MISO3/4 don't exist, so this only reshuffles the two real pairs — no capacity gain.)

2. **Prof. Kim's counter-idea (relayed via Andrea).** Ask Kontex to build an adapter exposing **4 SPI sockets per HDMI port** — Port1:MISO1, Port2:MISO2, Port3:MISO3, Port4:MISO4 — at **32ch per socket, using the "double 64" of every XDAQ port**; then "order 8 additional headstages" to reach 16 on the existing Core.

3. **KC's answers (authoritative):**
   - **1+2:** "The CORE will support only up to **8 RHD headstages: 2 per port, up to 128ch per port.** You will not need C3442 (for CORE you can only drive 2 RHD headstages per port)."
   - **3:** "With **XDAQ ONE/ONE+** you can drive up to **16 animals/headstages**. For Gen2 XDAQs we offer a **synchronization unit (SyncLink)** so multiple XDAQs run on the same clock — link multiple to run together." (https://docs.kontex.io/System-Adpt/SyncLink/)
   - **Extra, unprompted:** consider the **Port Expander (SAdpt-Port-EXP)** — gives each headstage **independent grounding and references**; without it, animals' grounds tie together at the DAQ and may cause **inter-animal interference**. (https://docs.kontex.io/System-Adpt/SAdpt-Port-EXP/)
   - Offered a **video call**.

## The technical resolution (why KC is right)

Verified directly against the Intan datasheets in `06-references/datasheets/` (full note: [[intan-rhd-spi-wiring-and-headstage-limits]]):

- One RHD SPI cable = 5 LVDS pairs = CS + SCLK + MOSI (shared) + **MISO1 + MISO2** → **max 2 chips per cable**, one chip per MISO line.
- **A chip = one MISO line regardless of channel count.** 16ch RHD2216 eats a full MISO line just like a 64ch chip. Cannot subdivide.
- XDAQ Core = **2 MISO pairs/port × 4 ports = 8 MISO lines = 8 headstages, HARD** (wire count, not firmware). Our current 8-mouse rig already uses all 8.
- XDAQ One/One+ = **4 MISO pairs/port × 4 ports = 16.**

So the professor's "double-64 → 4 sockets/port" and Claude's "DDR → 16 on Core" are both impossible. The $75 re-router can't help either (can't create MISO3/4 on the Core).

## Decision

- **Do NOT** buy Core adapters/headstages hoping for 16 — the Core is maxed at 8.
- **16 mice → one XDAQ ONE+.** Native 16 headstages, stays fully inside our Allego/Radiens + analysis pipeline.
- **32 mice (future) → two ONE+ units + SyncLink** (shared clock).
- **Include the Port Expander (SAdpt-Port-EXP)** for independent per-animal ground/reference. High value for us given the [[eeg-60hz-saga]] grounding history — 16 animals on a shared DAQ ground is exactly the crosstalk risk we've been fighting.

## Kontex docs retrieved (2026-07-21) — key confirmations

Pulled the actual Kontex docs (full transcription + archived HTML in [[kontex-xdaq-hardware-reference]]):
- **ONE+ = 1024 spike ch, 4 headstage ports (P1–P4), 4 Neuropixels.** CORE2 = 512ch/2 probes. AIO = 1024ch top-tier.
- **Port Expander (SAdpt-Port-EXP):** "each HDMI port supports **up to 4 animals with XR headstages**" with **isolated ground/reference per animal** (EXP C/D unavailable on lower models → 2/port on Core, 4/port on ONE+). Confirms 8-on-Core / 16-on-ONE+ AND is the fix for inter-animal ground crosstalk.
- **SyncLink:** one per XDAQ, **each XDAQ → its own PC**, SyncLinks daisy-chained via Ethernet (OUT→IN). 32 mice = 2× ONE+ + 2× SyncLink.

## Reply SENT to KC (2026-07-21)

Accepted the video call (Prof. Kim Staci Jakyong joining, KST but flexible to KC's timezone). Asked, ahead of the call:
1. **Custom re-routing adapter — usage:** how is it used in practice, does it let both SAdpt-XDAQ-OM12 sockets run at once (each with its own SPI cable + C3442 dual)?
2. **Prof. Kim's variant:** could the adapter instead be built with **a single MISO per socket = 4 sockets per adapter, one MISO each** — is that feasible?
3. **Port Expander price** — flagged as the most valuable option for our current Core, tied to our ongoing grounding/earth/noise struggles at 8 mice; want the per-animal isolated ground/reference. **Price requested.**
4. **Confirm: a second XDAQ = second PC + second software license?**
Framed everything as discussion points to plan our **simultaneous circadian multi-mouse rig**, centered on the **current Core Gen-1** (not a new-unit purchase).

**Awaiting:** KC's reply — call date/time, adapter usage + 1-MISO-per-socket feasibility, Port Expander price + Intan RHD2216 compatibility, 2nd-PC/2nd-license confirmation.

## Still open / next steps

- [ ] KC reply: schedule call + answers to the 4 questions above.
- [ ] **Confirm the Port Expander accepts our Intan RHD2216 headstages** (via SAdpt-XDAQ-OM12 / Omnetics), not only Kontex XR headstages — the whole 4/port + isolation benefit hinges on this.
- [ ] Ask KC for an **official quote**: 16-mouse ONE+ build (1× ONE+ + 4× Port Expander + 16× headstage interface + commutators/cables), the 32-mouse plan (2× ONE+ + 2× SyncLink), with lead time.
- [ ] **32-mouse: one PC or two?** SyncLink docs say "each XDAQ → its own PC" — confirm whether one PC can host both Allego instances, and how the two units appear in Allego/Radiens.
- [ ] Ask whether the **AIO reaches 32 animals single-box** (more headstage ports) vs always needing two units.
- [ ] Intan-vs-Open-Ephys only matters if we ever leave the XDAQ path — parked; reuse/reliability keeps us on XDAQ ONE+.

## Related
- [[kontex-xdaq-hardware-reference]] — Kontex primary-source docs (models, Port Expander, SyncLink, SAdpt)

## Related
- [[intan-rhd-spi-wiring-and-headstage-limits]] — the physics (why 8 / 16 / 32)
- [[hdmi-spi-adapter-top-socket-vendor-inquiry]] — earlier NeuroNexus/VIVO/Jeff + KC thread, dead-top-socket root cause
- [[eight-mouse-acquisition-setup]] — current 8-mouse topology
- [[eeg-60hz-saga]] — grounding history (why the Port Expander matters)

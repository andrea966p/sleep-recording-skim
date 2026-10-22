---
type: decision
area: rig-expansion
status: done
status-note: "open"
tags: [ decision, hardware, xdaq, kontex, acquisition, scale-up, email-log ]
created: 2026-07-21
---

# Acquisition Device for 16 (→32) Mice + Kontex Email Thread (Jul 2026)

> [!warning] Updated 2026-10-22: thread record. The XDAQ route was never committed (last activity: the 2026-07-29 call sheet). A separate Pinnacle wireless 16-mouse plan was settled 2026-10-19; see [[2026-10-16-pinnacle-wireless-16-mice-evaluation]]

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[_rig-expansion-hub]]** (decision, vendor correspondence, wiring, open items).

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

Reliability + reuse points at staying in the **XDAQ + Allego/Radiens** world we already run (our sensor maps, analysis code, SOPs all carry over). So: **XDAQ One+** — but see the full 3-way comparison below, which adds the software / license / openness dimensions surfaced 2026-07-21.

## 3-WAY COMPARISON — the real 16-mouse candidates (updated 2026-07-21)

Full Open Ephys write-up + sources: [[2026-07-21-openephys-acquisition-board-scale-up-option]]. Software/license findings from the post-call research.

| Dimension | **XDAQ ONE+** (Kontex) | **Intan RHD Rec. Controller 1024** (C3008) | **Open Ephys Acq. Board** |
|---|---|---|---|
| Reaches 16 mice? | ✅ native (4 ports × 4 MISO) | ✅ native (8 ports × 2) | ⚠️ 8 today; 16 only via **unvalidated `extension-board`** |
| Reaches 32? | 2× ONE+ + SyncLink | 2× controllers (sync TBD) | multi-board sync (ask) |
| Hardware | closed, productized | closed, productized | **open-source, customizable** |
| Software | Allego/Radiens **or** free OE/RHX | RHX (free) or Allego | **Open Ephys GUI (free)** |
| Software license | **~$2.5–5k/seat Allego** (or $0 on OE/RHX) | $0 on RHX | **$0** |
| Per-animal ground isolation | ✅ via **Port Expander** | not built-in (confirm) | **ask OE** (our 60 Hz concern) |
| Reuse of our pipeline | ✅ full (sleep64 / XDAT / Allego) | partial (Intan-family) | ✗ rebuild (XDAT→OE format) |
| Maturity / risk | **Low — turnkey** | **Low — turnkey** | **High — 16-path is a concept** |
| Reuses our RHD2216 headstages | ✅ | ✅ | ✅ (confirm bipolar) |

> [!note] The software "license" clarification (post-call)
> The license KC flagged for a 2nd XDAQ = **NeuroNexus Allego/Radiens paid software** (~$2.5–5k perpetual/seat), NOT an XDAQ hardware entitlement. **Open Ephys GUI, the XDAQ-OE plugin, and XDAQ-RHX are all free/open-source** — so a new XDAQ (or an OE board, or an Intan controller) can run **license-free** if we leave Allego. The catch: leaving Allego means rebuilding our whole pipeline (sleep64 map, `eeg-emg-analysis` XDAT reader, impedance workflow, video-sync Phase 0a gate). ⚠️ Still worth confirming with KC that the license he meant is the Allego software, not something baked into the XDAQ.

**Reading:** turnkey/reliable 16 = **XDAQ ONE+** or **Intan 1024 Controller**. **Open Ephys** = the open / low-cost / custom wildcard — cheapest on paper + no license, but its 16-mouse path is unvalidated. Facts being gathered via [[openephys-inquiry-email]]; final call → council once both vendors reply.

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

---

## ✅ VIDEO CALL HELD — KC Kong + Prof. Kim (2026-07-21)

Journal: [[2026-07-21]]. Prep: [[2026-07-21-kontex-kc-call-prep]].

### Confirmed on the call
1. **Custom "4-socket, 1-MISO-per-socket" adapter = NOT possible.** Prof. Kim's variant (one MISO per socket → 4 mice/HDMI port on the Core) is dead from the vendor's mouth. Closes question #2 of the sent email. The MISO-pair count is fixed by the box.
2. **Port Expander (SAdpt-Port-EXP) — KC recommends we TRY it**, specifically because it **handles each mouse's grounding separately** (isolated ground/reference per animal). This is the isolation we want for the [[eeg-60hz-saga]].
3. **Second-XDAQ license limitation ACKNOWLEDGED** — 2× XDAQ = 2× software license (and per SyncLink docs, each XDAQ → its own PC). Closes question #4.
4. **Headstage must be as CLOSE to the mouse as possible.** Our ~**40 cm analog run** is **a stretch** per KC. Rig-redesign action: shorten it. Directly supports the 60 Hz/impedance-noise fight (shorter analog antenna).
5. **2 mice per Intan adapter board = NOT possible, not even with the Port Expander.** One adapter board = one mouse. ⚠️ Clarify which board he meant (C3410 electrode board vs C3442 dual adapter).
6. KC **proposed several parts on the Kontex website** to complete the rig.

### 🔧 THE MAIN OPEN ITEM — wiring 4 Port Expanders to the Core Gen-1
Buying 4× Port Expander for the **current Core** needs **extra adapters** to complete the chain — it does not drop in. Must work out the full wiring order + BOM from the Kontex site:
```
Core HDMI port → [extra adapter?] → Port Expander (SAdpt-Port-EXP) → per-EXP-port Intan adapter → RHD2216 headstage
```

> [!important] Port Expander on the CORE does NOT increase mouse count
> Core = 2 MISO pairs/port → only **EXP A + B** available per port → **2 animals/port × 4 ports = 8**, same hard ceiling. 4× Port Expander on the Core = **per-animal grounding isolation on the existing 8-mouse rig** (a 60 Hz-hum test), NOT a route to 16. 16 still requires the ONE+.

### Revised plan (post-call)
- **Step 1 (cheaper, testable now):** Port-Expander-on-Core **grounding trial** at 8 mice — does per-animal isolation reduce the 60 Hz hum? Needs the 4× Port Expander + the extra Core adapters (BOM TBD from Kontex site).
- **Step 2 (scale-up):** XDAQ **ONE+** for 16 mice, once the isolation benefit is proven and surgical yield (open frontal electrodes) is fixed.
- **Step 3 (future):** 2× ONE+ + SyncLink + 2nd PC + 2nd license for 32.

### Next steps (updated)
- [ ] Work out the **Core + 4× Port Expander wiring + full BOM** from the parts KC proposed on the Kontex website (the "extra adapters").
- [ ] Clarify #5 — which adapter board is "one mouse only."
- [ ] Quote from KC: (a) Port-Expander grounding kit for the current Core, (b) 16-mouse ONE+ build.
- [ ] Rig redesign: shorten the ~40 cm analog headstage→animal run.
- [ ] Still gated by surgical yield — no box fixes open frontal electrodes ([[eeg-60hz-saga]]).

---

## Open Ephys reply folded in (2026-07-23)

Reply from Margarida (OE Support) — full log [[openephys-inquiry-email#✅ REPLY RECEIVED 2026-07-23 — Margarida (Open Ephys Support)]], analysis [[2026-07-21-openephys-acquisition-board-scale-up-option#REPLY RECEIVED 2026-07-23 — Open Ephys answers]]. Updates the OE column of the 3-way table above:

- **"Reaches 16 mice?"** — the `extension-board` route is **DEAD** (OE disowns it, not developed). 16 is now only **4 boards synced via I/O boards** OR a **paid custom Atlanta build**. Was already the highest-risk column; single-board dream is gone.
- **"Reaches 32?"** — same multi-board sync, just more boards + I/O boards + a strong PC.
- **RHD2216 reuse** → ✅ **CONFIRMED** by vendor (no longer "confirm").
- **Per-animal ground isolation** → ❌ **no OE product** (docs/Discord only). Kontex **Port Expander still the only vendor with a real isolation answer** — reinforces XDAQ for our [[eeg-60hz-saga]].
- **Software $0** → ✅ confirmed.

**Standings after both vendors replied:** turnkey/reliable 16 = **XDAQ ONE+** (or Intan 1024). OE = open/license-free but its 16-path degraded to multi-board-or-custom, and it has **no per-animal isolation** — a real minus for us. XDAQ ONE+ still leads on reliability + pipeline reuse + Port Expander isolation. **Ready to council the DAQ/software decision** once OE prices (multi-board build vs Atlanta custom) are pulled.

---

## 💵 KONTEX QUOTE 262024 received (2026-07-23) — Port-Expander-on-Core grounding kit

Quote No. **262024**, prepared by KC Kong (kc@kontex.io), issued 2026-07-21, **valid through 2026-08-20**, USD. PDF in `~/Downloads/Quotation - 262024.pdf`.

> [!important] What this quote IS and IS NOT
> This is the **Step-1 per-animal grounding retrofit for our CURRENT 8-mouse Core** — NOT the 16-mouse ONE+ scale-up. It also **resolves the main open BOM item** ("wiring 4× Port Expander to the Core needs extra adapters"): the extra adapter is the **SAdpt-CORE-OM12** (×4, one per Core HDMI port). The 16-mouse ONE+ build quote is still ⏳ owed.

| Item | Part | Unit | Qty | Ext |
|---|---|---|---|---|
| XDAQ CORE to OM12 Adapter (the "extra adapter" per port) | **SAdpt-CORE-OM12** | $350.00 | 4 | $1,400.00 |
| XDAQ HDMI to Single OM12 (per-mouse Intan/OM12 interface) | **SAdpt-XDAQ-OM12(1)** | $275.00 | 8 | $2,200.00 |
| XDAQ Port Expander (isolated ground/ref, one per port) | **XDAQ-Port-EXP** | $1,525.00 | 4 | $6,100.00 |
| | | | Subtotal | **$9,700.00** |
| | | | Shipping | $252.89 |
| | | | Fees | $50.00 |
| | | | **Total** | **$10,002.89** |

**BOM logic (confirms Core = 8, EXP A+B only):** 4 Core ports × 1 Port Expander each; each Port Expander drives **2 animals (EXP A + B)** on the Core → **8 mice**; 8× SAdpt-XDAQ-OM12(1) = one single-OM12 interface per mouse (the Intan RHD2216 path); 4× SAdpt-CORE-OM12 = the Core-HDMI→OM12 bridge feeding each Port Expander. Full chain now known:
```
Core HDMI port → SAdpt-CORE-OM12 → XDAQ-Port-EXP → SAdpt-XDAQ-OM12(1) ×2 (EXP A/B) → RHD2216 headstage ×2
```

**Warranty (Schedule A):** Systems & Instrumentation 12 mo (**24 mo if registered within 30 days**); Commutators 6/12 mo; **Headstages 90 days; Adapters/EIBs/Cables 90 days**. KonteX Care Extended → 48 mo (buy within 60 days). All sales final; prepayment in full before shipment; RUO only; governed by Taiwan law. Confidentiality clause = **do not publicly disclose pricing**.

**Notes / still open:**
- ⚠️ Quote does **not** itemize a commutator/slip-ring or the RHD2216 headstages themselves (we already own those) — it's purely the grounding-isolation adapter chain.
- ⏳ Does **SAdpt-XDAQ-OM12(1)** accept our exact Intan RHD2216 (Omnetics) headstage? Implied yes (OM12 = Intan interface) but confirm.
- ⏳ Still need the separate **16-mouse ONE+ build** quote (1× ONE+ + 4× Port Expander + 16× OM12 interface + commutators/cables) and the 32-mouse plan (2× ONE+ + 2× SyncLink).
- This $10k retrofit buys the **60 Hz per-animal isolation trial on the existing rig** ([[eeg-60hz-saga]]), Step 1 of the revised plan — not more mice.

---
type: decision
area: rig-expansion
status: superseded
tags:
  - decision
  - hardware
  - comparison
  - xdaq
  - open-ephys
  - acquisition
  - scale-up
created: 2026-07-23
superseded-by: "[[2026-07-24-daq-32-mouse-final-comparison]]"
---
# DAQ Ecosystem Comparison — XDAQ/NeuroNexus vs Open Ephys (16 → 32 mice)

> [!warning] 2026-10-28: VAULT-ONLY, never publish. Row 15 (XDAQ record start and stop is global) is true for `radiens` 4.0.0 on Allego 3.11.3 only; on Allego 4.1.2 with `radiens-core` the XDAQ records per port ([[2026-10-28-per-port-recording-bench-test]]). Nothing else on this page was changed.

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[_rig-expansion-hub]]** (decision, vendor correspondence, wiring, open items).

> [!history] SUPERSEDED 2026-07-24 → [[2026-07-24-daq-32-mouse-final-comparison]]
> This is the 16-mouse, 2-way (XDAQ vs Open Ephys) snapshot. The FINAL comparison is now 3-way (adds **Intan direct**), scoped to **32 mice**, with **priced bills of materials** for every ecosystem and the **two-headstages-per-port question SETTLED** from Intan datasheets. Read [[2026-07-24-daq-32-mouse-final-comparison]] instead. This doc is kept for its 16-mouse snapshot and the original per-row vendor-quote notes.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The head-to-head decision table for the acquisition box that will drive our next rig: **at least 16 mice recorded at once, scalable to 32 later**, reusing our Intan **RHD2216** bipolar headstages (one headstage = one mouse). Two ecosystems: **XDAQ / NeuroNexus (Kontex)** — what we already run and know — versus **Open Ephys** — open hardware, free software.
> **Where it stands.** Both vendors have now replied (Kontex/KC on 2026-07-21, Open Ephys/Margarida on 2026-07-23). The physics and capabilities are nailed; the two big blanks left are **prices** (quotes open on both sides) and a couple of Open Ephys specifics (8-vs-4 animals per board, per-animal ground isolation). Those blanks are marked ⏳ in the table so this doc completes itself as answers arrive.
> **How to read it.** §1 = the master table. §2 = per-row notes with the vendor quotes. §3 = what's still owed by whom. §4 = the current reading (not yet a final decision — that goes to a council once prices land).

> [!quote] Paper-ready
> Two acquisition ecosystems were evaluated for a chronic multi-animal mouse EEG/EMG rig scalable from 16 to 32 animals: the XDAQ system (Kontex) running NeuroNexus Allego/Radiens software, and the open-source Open Ephys Acquisition Board running the Open Ephys GUI. Both interface the same Intan RHD amplifier chips over SPI; they differ in headstage-count ceiling per box, per-animal grounding isolation, software licensing, data format, and hardware openness.

Companion docs: [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] (XDAQ/Kontex thread), [[2026-07-21-openephys-acquisition-board-scale-up-option]] (Open Ephys option), [[openephys-inquiry-email]] (OE email + reply), [[intan-rhd-spi-wiring-and-headstage-limits]] (MISO physics), [[kontex-xdaq-hardware-reference]] (Kontex primary-source), [[eeg-60hz-saga]] (grounding history).

---

## 1. Master comparison table

| # | Dimension | **XDAQ / NeuroNexus (Kontex)** | **Open Ephys** |
|---|---|---|---|
| 1 | **Animals per single box** (1 headstage/mouse) | Core (ours) **8**, ONE+ **16** — MISO-pair proven | **⏳ 8 or 4?** OE reply framed board as "max 4 animals" (dual adapter = 2 hs same animal); by MISO physics it should be **8** single-hs mice. Clarify. |
| 2 | **Native path to 16** | ✅ **1× XDAQ ONE+** — native, turnkey (4 MISO pairs × 4 ports) | ⚠️ **2–4 boards synced** via I/O boards, OR **paid custom Atlanta build**. The `extension-board` (16-on-1) is **DEAD** (vendor disowns it) |
| 3 | **Path to 32** (future) | 2× ONE+ + **SyncLink** (shared clock) + **2nd PC + 2nd Allego license** | more boards + I/O-board sync, likely **1 PC** — **⏳ practical ceiling + PC spec** |
| 4 | **Per-animal ground/ref isolation** (our 60 Hz wall) | ✅ **Port Expander (SAdpt-Port-EXP)** — "ground and reference nodes from each animal's headstage do not interfere" | ❌ **no product** — "depends on your design", punted to docs + Discord. **⏳ any hardware/wiring option?** |
| 5 | **RHD2216 bipolar support** | ✅ (SAdpt-XDAQ-OM12 blessed path) | ✅ vendor-confirmed — "optimal for paired differential EEG/EMG" |
| 6 | **Software + license cost** | Allego/Radiens **~$2.5–5k/seat** (perpetual) — OR $0 if run on XDAQ-RHX/OE plugin | **$0** — Open Ephys GUI, open-source |
| 7 | **Data format / pipeline reuse** | ✅ **XDAT** → our `sleep64` map + `eeg-emg-analysis` reused as-is | ✗ rebuild — **⏳ what format does OE GUI write; Intan-compatible export?** |
| 8 | **Video-sync (Phase 0a)** | ✅ already scoped — Allego "Gated" mode, DO 03 / DB25 pin 22 → Pi GPIO | ✗ re-implement via I/O-board digital input |
| 9 | **Buildability / wiring** | Turnkey native 16 on ONE+ (Core+4×PortExp BOM still open) | Multi-board + I/O-board sync cabling + **⏳ commutators/tethering for chronic mice** |
| 10 | **Long-run reliability (24–72 h)** | ✅ **PROVEN on our rig** — 72 h byte-perfect, endurance validated | **⏳ track record for multi-day continuous on synced boards?** |
| 11 | **Hardware price + lead time** | **Partial:** Quote 262024 = **$10,002.89** for the Port-Expander grounding retrofit **on the current 8-mouse Core** (4× Port-EXP + 4× SAdpt-CORE-OM12 + 8× OM12). ⏳ still owed: **16-mouse ONE+ build** + 32-mouse plan | ⏳ webstore/quote: board + I/O board + SPI 16ch bipolar headstage (**in stock**) |
| 12 | **Support + warranty** | Vendor (Kontex + NeuroNexus), direct email/call | 1-yr warranty + repairs + Discord community + **paid Training** |
| 13 | **Openness / customization** | Closed hardware — limited to what Kontex sells | **Open hardware** (public design files) + **Atlanta custom-design team** |
| 14 | **Maturity / risk** | **Low** — fully turnkey, we already run it | **Higher** — 16-path is multi-board or unbuilt custom |
| 15 | **Independent per-mouse/group record start-stop** | ❌ **global** — one XDAQ = one R_ON/R_OFF for the whole box ([[multi-user-independent-recording-schedules\|project_multiuser_recording_schedules]]); workaround = union+slice offline | **⏳** all-or-nothing on Record? per-animal/subset via GUI API/SDK/plugins, or hardware limit? (email Q3) |

Legend: ✅ confirmed strength · ⚠️ conditional · ❌ confirmed gap · ⏳ answer still owed (see §3).

---

## 2. Per-row notes (with vendor quotes)

- **Row 1 (animals/box).** MISO physics is settled ([[intan-rhd-spi-wiring-and-headstage-limits]]): 1 RHD chip = 1 MISO line = 1 mouse, channel count irrelevant. XDAQ Core = 8, ONE+ = 16 (vendor-authoritative). Open Ephys reply framed the board as *"a maximum of four animals"* because it treats the dual-headstage adapter as *"two headstages in the same animal... not to record from animals that are physically separated."* For our 1-headstage-per-mouse use this should still be **8 MISO lines = 8 mice** — but the vendor's own framing conflicts, so it is the #1 clarification (email Q1). Decides 2 vs 4 boards for 16. **Key counter-evidence: we already run the SPI splitter / dual-headstage adapter with 2 SEPARATE animals per port on our current Intan/NeuroNexus rig (8 mice), reliably** — so "same animal only" is not a hard rule for us. **Likely root of Margarida's framing = the two headstages on one dual adapter SHARE ground/reference**; fine within one animal, but for 2 separate animals it couples their grounds — which is exactly our [[eeg-60hz-saga]] inter-animal coupling risk. So Row 1 and Row 4 are the same question; email Q1 asks directly whether the dual adapter shares ground/ref.
- **Row 2 (path to 16).** XDAQ ONE+ reaches 16 natively. Open Ephys's cheap single-board route (the repo `extension-board`, "up to 16 RHD chips / 1024 channels") is **dead**: OE Support — *"I'm not familiar with the extension board design... not something the Open Ephys team is currently developing."* Real OE routes to 16 = **4 boards synchronized via I/O boards** or a **paid custom Atlanta build**.
- **Row 3 (path to 32).** XDAQ: 2× ONE+ + SyncLink, and per SyncLink docs *"each XDAQ connects to its own PC"* → 2nd PC + 2nd Allego license (KC acknowledged). OE: more synced boards on (likely) one PC — ceiling + PC spec unconfirmed (email Q6).
- **Row 4 (isolation — the make-or-break).** This is our #1 historical wall ([[eeg-60hz-saga]]). Kontex **Port Expander** gives *"isolated and dedicated electrical systems to each connected headstage... ground and reference nodes from each animal's headstage do not interfere"* — exactly our need; KC recommended it unprompted. Open Ephys offered **no product** — *"depends on your specific experimental design"*, docs + Discord only. Big differentiator in XDAQ's favour unless OE surfaces a hardware answer (email Q2).
- **Row 5 (RHD2216).** Both confirmed. OE: *"fully supports your Intan RHD2216 bipolar headstages... independent in+ and in− inputs... optimal for paired differential recordings such as surface EMG and EEG."*
- **Row 6 (software/license).** The Allego license (~$2.5–5k/seat) is **NeuroNexus paid software**, not an XDAQ hardware entitlement — XDAQ can run license-free on XDAQ-RHX/OE plugin. Open Ephys GUI is $0. Real money at 16→32 seats, but "free software" on the XDAQ side means leaving Allego = the same pipeline-rebuild cost as going to OE (row 7).
- **Row 7 (format/pipeline).** Staying XDAQ+Allego reuses everything (XDAT reader, sleep64 map, `eeg-emg-analysis`, impedance workflow). Any move off Allego (to OE, or to XDAQ-RHX) forces a rebuild — need the OE GUI's record format + whether an Intan-compatible export exists (email Q6).
- **Row 8 (video-sync).** Our Phase 0a hardware sync is built on Allego "Gated" mode + BNC breakout (DO 03 / DB25 pin 22 → Pi GPIO). On OE this re-implements on an I/O-board digital input — extra work.
- **Row 9 (buildability).** XDAQ ONE+ = one box, native 16, minimal cabling (Core+PortExpander wiring BOM is a separate open item). OE = 2–4 boards + I/O boards + inter-board sync cabling; plus commutator/tethering for chronic freely-moving mice still to confirm (email — optional commutator question).
- **Row 10 (reliability).** XDAQ has a **proven** 72 h byte-perfect run on our own rig — huge weight for a live-animal instrument. OE multi-day-continuous track record on synced boards is unknown to us (email Q5).
- **Rows 11–14.** **XDAQ price partial:** Kontex Quote 262024 (2026-07-23) = **$10,002.89** — but this is the **Port-Expander grounding retrofit for the existing 8-mouse Core** (4× XDAQ-Port-EXP @ $1,525 + 4× SAdpt-CORE-OM12 @ $350 + 8× SAdpt-XDAQ-OM12(1) @ $275, + ship/fees), **NOT the 16-mouse ONE+ build** (still ⏳). It resolves the "extra adapters for Port-EXP on Core" BOM item (= SAdpt-CORE-OM12). Full breakdown in [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread#💵 KONTEX QUOTE 262024 received (2026-07-23) — Port-Expander-on-Core grounding kit]]. OE prices ⏳ still owed. Support: XDAQ = vendor direct (warranty: Systems 12/24 mo, headstages+adapters 90 days); OE = warranty + repairs + Discord + paid Training. Openness/custom: OE's real edge (open files + Atlanta team). Maturity: XDAQ low-risk turnkey, OE higher-risk on the 16-path.
- **Row 15 (independent record control).** Operationally important — animals run on different schedules. **XDAQ is also limited: one box = one global R_ON/R_OFF** ([[multi-user-independent-recording-schedules|project_multiuser_recording_schedules]]), current workaround = record the union of windows and slice offline. OE unknown: does the GUI Record button start/stop ALL connected animals, or can a single mouse/subset be controlled — and if not native, is it doable via the GUI API/SDK/plugins or is it a board hardware limit (email Q3)? A per-animal-control win here would favour whichever system offers it.

---

## 3. What's still owed (so the table can complete)

**Open Ephys (via follow-up email 2026-07-23, [[openephys-inquiry-email]]):**
- ⏳ Row 1 — 8 vs 4 separate animals per board (1 headstage/mouse); **does the dual adapter share ground/ref between its two headstages?**
- ⏳ Row 4 — any hardware/wiring for per-animal ground+reference isolation.
- ⏳ Row 15 — independent per-mouse/subset record start-stop; native, API/SDK, or hardware limit?
- ⏳ Row 3/9 — path to 32 ceiling + recommended host-PC spec.
- ⏳ Row 7 — GUI record format + Intan-compatible export.
- ⏳ Row 10 — multi-day continuous reliability references.
- ⏳ Row 11 — itemized quote (boards + I/O boards + SPI 16ch headstages + cables), academic pricing, lead time.
- ⏳ Row 2/13 — Atlanta custom-team scope for a 16-headstage board.

**XDAQ / Kontex (quote request still open with KC, [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]]):**
- ⏳ Row 11 — quote: 16-mouse ONE+ build (ONE+ + 4× Port Expander + 16× headstage interface + commutators/cables) and the 32-mouse plan (2× ONE+ + 2× SyncLink).
- ⏳ Port Expander accepts our Intan RHD2216 (not only Kontex XR headstages).
- ⏳ Core + 4× Port Expander wiring BOM (the "extra adapters").
- ⏳ 32-mouse: one PC or two for both Allego instances.

---

## 4. Current reading (not the final decision)

- **Turnkey / reliable 16 today = XDAQ ONE+.** Native 16, full reuse of our Allego/sleep64/`eeg-emg-analysis`/video-sync pipeline, a **proven 72 h** endurance record, and the **Port Expander** — the only vendor product that directly answers our 60 Hz per-animal ground isolation problem.
- **Open Ephys = the open, $0-software, customizable wildcard** — but its reply made the 16-mouse story **worse**: no single-board route (extension board dead), no per-animal isolation product, and a full pipeline rebuild. Its live wins are **free software** and **confirmed RHD2216 support**; its real upside is the **Atlanta custom team** if they'll build/validate a 16-headstage board at a good price.
- **Decision gate:** don't decide until **both price columns fill** and OE answers the isolation + 8-vs-4 questions. Then **council** the DAQ/software choice. Also still gated by surgical yield (open frontal electrodes) — no box fixes that ([[eeg-60hz-saga]]).

## Related
- [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] · [[2026-07-21-openephys-acquisition-board-scale-up-option]] · [[openephys-inquiry-email]]
- [[intan-rhd-spi-wiring-and-headstage-limits]] · [[kontex-xdaq-hardware-reference]] · [[eeg-60hz-saga]]

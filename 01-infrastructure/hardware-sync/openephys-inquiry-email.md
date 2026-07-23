---
tags:
  - infrastructure
  - hardware-sync
  - open-ephys
  - email
  - inquiry
  - scale-up
created: 2026-07-21
status: replied
sent: 2026-07-22
replied: 2026-07-23
---
# Open Ephys Inquiry — Acquisition Board scale-up to 16 (→32) mice

> [!abstract] TL;DR
> Draft email to Open Ephys to get the facts we are missing about the **Acquisition Board** and the **extension-board** design (16 headstages / 1024ch): status, price, lead time, Intan RHD2216 compatibility, per-animal grounding, multi-board sync, custom-build options, and a call. Context/decision doc: [[2026-07-21-openephys-acquisition-board-scale-up-option]].

**Where to send it** (pick one / cc):
- Sales/general: `sales@open-ephys.org` (Open Ephys Production Site store) — confirm on https://open-ephys.org/contact
- Technical/design: their **GitHub** (`open-ephys/acquisition-board` issues) or **Discord** community — the extension-board README author is reachable there.
- Recommend: email sales first for price/lead-time; raise the extension-board technical status as a GitHub issue in parallel.

**Fill before sending:** sender name/role, lab + PI (Prof. Kim Staci Jakyong, KAIST), rough timeline, budget ceiling if you want a scoped quote.

---

> [!success] SENT 2026-07-22 — awaiting Open Ephys reply (extension-board status, price, RHD2216 compat, per-animal isolation, multi-board sync, custom build, call).

## EMAIL (as sent)

**Subject:** Acquisition Board for 16-animal simultaneous EEG/EMG — scale-up + extension-board question

Hello Open Ephys team,

I am writing from a sleep-neuroscience lab at KAIST (PI: Prof. Kim Staci Jakyong). We run chronic multi-animal mouse EEG/EMG recordings for sleep research, and we are planning a new rig to record **at least 16 mice simultaneously, ideally scalable to 32 later**.

**Our current setup (for context):**
- One Intan **RHD2216** bipolar headstage per mouse (16-channel, but we use only ~4–6 channels: a bipolar EEG pair + a bipolar EMG pair). One headstage = one animal.
- We currently record 8 mice at once on a **NeuroNexus system** (XDAQ + Allego/Radiens), and we have a full analysis pipeline built around the Intan data.
- Recordings are long-duration (24–72 h continuous), so **reliability is critical** — this is a live-animal instrument.

We are on NeuroNexus today, but **for this expansion we are interested in switching to Open Ephys** — it uses the same Intan RHD chips we already own, its software is open-source, and its hardware is open, which is very attractive for a lab that wants to reuse hardware and avoid per-seat software licenses. We would like to understand whether the Open Ephys Acquisition Board is a solid path to a reliable 16-animal (→32) rig.

We understand from your documentation that a single Acquisition Board supports up to **8 headstages (4 ports × 2) / 512 channels**. We also found the **`extension-board`** design in your `acquisition-board` GitHub repository, whose README describes adding 4 more SPI connectors for **up to 16 RHD chips / 1024 channels**, while noting it is "not a finished or tested design yet."

That 16-headstage capability is exactly our target, so we would like to understand it properly. Could you help us with the following?

**About the extension board (our main interest):**
1. What is the current status of the extension board — is it in active development, buildable today, on your roadmap, or purely a concept?
2. Can it realistically drive **16 RHD headstages / 16 animals** on one board? Have the CMOS-to-LVDS bridges and bandwidth been validated, or is that still open?
3. If it is buildable, can we **purchase it, have you fabricate it, or commission it as a custom job**? What would that involve?

**About the base board and hardware:**
4. Price and lead time for the current Acquisition Board (and any 16-headstage configuration/option).
5. Does the board fully support our **Intan RHD2216 bipolar** headstages (16-channel, differential inputs, no dedicated reference pin)? Any caveats with bipolar chips vs the more common 32/64-ch unipolar headstages?
6. **Grounding/isolation:** when many headstages record on one board, are the animals' grounds/references tied together at the board, or can each animal be electrically isolated? We have a history of 60 Hz mains-hum and inter-animal grounding sensitivity, so per-animal isolated ground/reference matters a lot to us.

**About scaling and software:**
7. As an alternative to the extension board, can **multiple Acquisition Boards be hardware-synchronized** to record 16 (and later 32) animals on a shared clock? If so, how, and does each board need its own PC?
8. Is acquisition fully covered by the free **Open Ephys GUI**, or is any paid component involved? What does support look like for a setup this size?
9. Do you offer **custom hardware design/build services** if we need a validated 16-animal board?

**Logistics:**
10. Could we arrange a **video call** to discuss the 16→32-animal plan? We are in Korea (KST) but flexible to your timezone.
11. Any **academic pricing** or guidance for a multi-board / multi-animal order.

Thank you very much — we are excited about the open, reusable approach and want to understand whether the Acquisition Board (with or without the extension board) is a solid path to a reliable 16-animal rig.

Best regards,
[Your name]
[Role] — Prof. Kim Staci Jakyong lab, KAIST
[email] · [phone/timezone]

---

## Why each question (internal notes — do NOT send)
- **Q1–3 (extension board):** the whole reason this option exists. The README says "not tested" — we need to know if it is real or vapor, and whether they will build/validate it. This is the make-or-break.
- **Q4:** cost/lead-time vs XDAQ ONE+ and Intan 1024 Controller — feeds the 3-way comparison.
- **Q5:** RHD2216 is **bipolar with no reference pin** ([[intan-rhd-spi-wiring-and-headstage-limits]]); most OE users run unipolar 32/64ch headstages, so confirm no surprises.
- **Q6:** direct tie to [[eeg-60hz-saga]] — Kontex's answer was the Port Expander (per-animal isolated ground); we need OE's equivalent answer.
- **Q7:** multi-board sync is the productized alternative to the risky extension board (mirrors XDAQ SyncLink).
- **Q8:** confirms the "free software, no license" advantage over Allego.
- **Q9:** if the extension board is only a concept, a paid custom build might still beat XDAQ on cost/openness.
- **Q10–11:** logistics + budget.

## Related
- [[2026-07-21-openephys-acquisition-board-scale-up-option]] — the option write-up + sources
- [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] — the XDAQ/Kontex side of the decision
- [[neuronexus-inquiry-email]] — the parallel Kontex/NeuroNexus inquiry thread (same format)
- [[intan-rhd-spi-wiring-and-headstage-limits]] — MISO physics

---

## ✅ REPLY RECEIVED 2026-07-23 — Margarida (Open Ephys Support)

> [!success] Answered. Verdict: base board = 8 headstages BUT OE frames it as **4 animals**; **extension board is DEAD** (not developed); 16-path = **4 boards synced** OR **custom build (Atlanta team)**; **RHD2216 fully supported**; software free; **NO productized per-animal ground isolation** (punted to docs/Discord). Analysis folded into [[2026-07-21-openephys-acquisition-board-scale-up-option#REPLY RECEIVED 2026-07-23 — Open Ephys answers]].

### Answers, question by question

- **Extension board (Q1–3): DEAD.** Verbatim: *"I'm not familiar with the extension board design you mentioned... this is not something the Open Ephys team is currently developing, so we're unable to provide any further details."* → the 16-chip/1024ch-on-one-board README idea is **vapor from the vendor's side.** Kills the cheap single-board route to 16.
- **Board capacity (context):** 4 ports × 2 RHD chips = **512ch, 30 kSps.** BUT OE frames the dual-headstage adapter as **"two headstages in the SAME animal"** (probe-positioning flexibility), so *"the acquisition board can be used to record from a **maximum of four animals**."* ⚠️ **DISCREPANCY vs our MISO physics** ([[intan-rhd-spi-wiring-and-headstage-limits]]): 8 chips = 8 MISO lines = 8 single-headstage mice for us. Her "4 animals" is a usage framing, not obviously a hard limit — **must clarify (see follow-ups).**
- **16 mice (Q7):** *"use four acquisition boards simultaneously... connect multiple acquisition boards to the same computer and also use them in the same GUI, and have the data streams synchronized."* Sync done via the **I/O boards** (8 analog + 8 digital in, 8 analog + 8 digital out per board). This is OE's SyncLink equivalent. Note: **four** boards for 16 tracks HER "4 animals/board" number, not our "8/board" — the discrepancy above decides whether 16 needs **2 boards or 4**.
- **RHD2216 (Q5): ✅ FULLY SUPPORTED.** *"fully supports your Intan RHD2216 bipolar headstages... independent in+ and in- inputs on each amplifier channel... optimal for paired differential recordings with electrodes that have similar impedances, such as surface EMG and EEG."*
- **Grounding/isolation (Q6): NO productized answer.** *"depends on your specific experimental design"* → pointed to docs (Grounding your system, Troubleshooting Noise) + Discord. **No hardware equivalent of the Kontex Port Expander** (per-animal isolated ground) was offered. Weak spot for our [[eeg-60hz-saga]].
- **Software (Q8): ✅ FREE.** Open Ephys GUI, open-source, no paid component.
- **Custom build (Q9): YES — Atlanta team.** *"Our team in Atlanta does custom designs and could potentially help you... for a 16-headstage board. They would be the main point of contact."* → the real (non-vapor) path to 16-on-one-board is a **paid custom job**, not the extension board.
- **Price/lead time (Q4):** on the webstore, or formal quote on request. Acq board + SPI 16ch bipolar headstage **in stock, immediate shipment.** (No numbers given — pull from store / request quote.)
- **Extras:** recommends a **powerful PC** (all boards on one machine — data + storage demands for long sessions). Offers **paid Training** (setup help). **1-yr warranty** + repair service. Discord community for grounding/referencing advice.

### Follow-ups needed
- [ ] **THE key question:** confirm whether one board records **8 separate animals** (our 1-headstage-per-mouse use, 8 MISO lines) or is genuinely capped at **4 animals** — decides 2 vs 4 boards for 16. Raise on Discord / GitHub.
- [ ] Per-animal ground **isolation**: is there any OE hardware for it, or is shared-board-ground unavoidable (our 60 Hz risk)? Ask Discord/developers.
- [ ] Pull **prices** (acq board, SPI 16ch bipolar headstage, I/O boards) from webstore or request formal quote for a 16-mouse multi-board config.
- [ ] If multi-board is messy → get a scope + rough price from the **Atlanta custom team** for a 16-headstage board.

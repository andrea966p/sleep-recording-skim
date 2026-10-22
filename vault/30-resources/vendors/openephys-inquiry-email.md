---
type: reference
area: rig-expansion
status: done
status-note: "replied"
tags:
  - infrastructure
  - hardware-sync
  - open-ephys
  - email
  - inquiry
  - scale-up
created: 2026-07-21
sent: 2026-07-22
replied: 2026-07-23
followup_drafted: 2026-07-23
followup_final: 2026-07-23
followup_replied: 2026-07-28
---
# Open Ephys Inquiry — Acquisition Board scale-up to 16 (→32) mice

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[RIG-EXPANSION-HUB]]** (decision, vendor correspondence, wiring, open items).

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

> [!done] Mostly closed by the 2026-07-28 reply — see §"REPLY 2 RECEIVED 2026-07-28" below
> The 8-vs-4-animals question and the isolation question are both answered there. Prices and the custom board are still open.

- [x] **THE key question:** confirm whether one board records **8 separate animals** (our 1-headstage-per-mouse use, 8 MISO lines) or is genuinely capped at **4 animals** — decides 2 vs 4 boards for 16. Raise on Discord / GitHub.
- [ ] Per-animal ground **isolation**: is there any OE hardware for it, or is shared-board-ground unavoidable (our 60 Hz risk)? Ask Discord/developers.
- [ ] Pull **prices** (acq board, SPI 16ch bipolar headstage, I/O boards) from webstore or request formal quote for a 16-mouse multi-board config.
- [ ] If multi-board is messy → get a scope + rough price from the **Atlanta custom team** for a 16-headstage board.

---

## FOLLOW-UP EMAIL (drafted 2026-07-23 — reply to Margarida)

> [!info] Purpose
> Tight, table-driven reply that fills the ⏳ Open Ephys cells in [[daq-ecosystem-comparison-xdaq-vs-openephys]]. **OE-facing only — deliberately does NOT mention Kontex/NeuroNexus or that we are comparing vendors.** User sends it; not yet marked sent.

**Subject:** Re: Acquisition Board for 16-animal EEG/EMG — clarifications + Atlanta custom team

Hi Margarida,

Thank you, this is really helpful. A few focused follow-ups so we can plan properly.

**1. Animals per board (our configuration).** We run **one RHD2216 headstage per mouse** — each animal is a separate headstage on its own SPI/MISO line (we use only ~4–6 of the 16 channels: a bipolar EEG pair + a bipolar EMG pair). So rather than two headstages in one animal, can a single Acquisition Board record **8 physically separate mice** (4 ports × 2 single-headstage animals)? This decides whether we need 2 boards or 4 for 16 mice.

**2. Per-animal grounding isolation.** Our hardest recording problem is **60 Hz mains hum and ground coupling between animals**. When several headstages share one board, are the animals' grounds/references tied together at the board, or is there a hardware option or wiring scheme to keep **each animal electrically isolated (independent ground + reference)**? This is a major factor for us — a clear hardware answer would help a lot (we'll also ask on Discord).

**3. Custom 16-headstage board / Atlanta team.** Understood the extension board isn't in active development — for reference it's the design in your repo: https://github.com/open-ephys/acquisition-board/tree/master/extension-board . A single, reliable 16-animal board would be far preferable to synchronizing four boards. Could you please **connect us with the Atlanta team** to scope a custom or validated 16-headstage board (feasibility, timeline, cost)?

**4. Multi-board route — formal quote.** In parallel, please send an **itemized quote** for the multi-board path to 16 animals: Acquisition Boards + the I/O boards needed to synchronize them + your SPI 16-ch bipolar headstages + required cables. **Academic pricing and lead time** appreciated.

**5. Long-duration reliability + host PC.** Our recordings run **24–72 h continuous**, so reliability is critical. Do you have experience or references for multi-day continuous recording on multiple synchronized boards, and what **host-PC spec** would you recommend for the data + storage load at 16 (and later 32) animals on one machine?

**6. Scaling to 32 + data format.** Longer term we'd like to reach **32 animals** — can more boards be synchronized on one PC to get there, and is there a practical ceiling? Also, what **file format does the Open Ephys GUI record**, and is there an Intan-compatible export? (We have an existing analysis pipeline and want to understand the migration.)

A short video call to go over the 16→32-animal plan would be very welcome — we're in Korea (KST) but flexible.

Thanks again,
[Your name]
Prof. Kim Staci Jakyong lab, KAIST

### Internal — question → comparison-table cell (do NOT send)
Q1 → row 1 (animals/box) · Q2 → row 4 (isolation) · Q3 → rows 2/13/14 (custom/openness) · Q4 → row 11 (price) · Q5 → row 10 (reliability) + row 9 (host PC) · Q6 → row 3 (scale to 32) + row 7 (data format). Optional commutator question → row 9. Table: [[daq-ecosystem-comparison-xdaq-vs-openephys]].

---

## FOLLOW-UP EMAIL v2 — FINAL (2026-07-23, supersedes the v1 draft above)

> [!important] Changes from v1
> Added two high-value questions that outrank some v1 points: **(a) independent per-mouse/per-group record start-stop** (all-or-nothing? customizable via GUI API/SDK? or hardware limit?) — note XDAQ has the SAME global-R_ON limit ([[project_multiuser_recording_schedules]]); **(b) the SPI splitter for 2 SEPARATE animals** — we already do this on our Intan/NeuroNexus rig (8 mice), so we push back on Margarida's "dual adapter = 2 headstages same animal" framing. Key insight folded in: her framing likely = **the two headstages on one dual adapter SHARE ground/reference**, which for 2 separate animals is exactly our [[eeg-60hz-saga]] inter-animal coupling risk → splitter Q and isolation Q are the same question. Also de-duplicated Q7 (dropped the "can boards share one PC" half she already answered; kept ceiling + data format).

**Subject:** Re: Acquisition Board for 16 animal EEG/EMG: clarifications and Atlanta custom team

Hi Margarida,

Thank you, this is really helpful. A few focused questions so we can plan properly.

**1. Animals per board: we already record 2 separate animals per port today.** We run **one RHD2216 headstage per mouse** (about 4 to 6 of the 16 channels: a bipolar EEG pair plus a bipolar EMG pair). On our current Intan based system we already use the **SPI splitter (dual headstage adapter) to record two *separate* animals on one port**, 8 mice across 4 ports, and it works reliably. You mentioned the dual adapter is intended for two headstages in the *same* animal; could you clarify the reason? Specifically, **do the two headstages on one dual adapter share a common ground or reference at the board?** If they do, that would be our concern for two separate animals (see question 2). Assuming isolation is handled, can one Acquisition Board record **8 physically separate mice** (4 ports × 2)?

**2. Per animal grounding isolation.** Our hardest recording problem is **60 Hz mains hum and ground coupling between animals**. You pointed us to the docs and Discord; to be concrete: when multiple headstages share one board (and especially two headstages on one dual adapter), are the animals' grounds and references **tied together at the board**, or is there a hardware option or wiring scheme to keep **each animal electrically isolated with independent ground and reference**? A clear hardware answer is a major factor for us.

**3. Independent recording control per mouse.** With multiple animals on one board (and across synchronized boards), can we **start and stop recording for a single mouse or a subset independently**, or does pressing Record start and stop **all connected animals together**? If it is all or nothing, is per animal or per group control achievable through the **Open Ephys GUI's API, SDK, or plugins**, or is it a **hardware constraint** of the Acquisition Board? This matters for us because different animals run on different experimental schedules.

**4. Custom 16 headstage board and the Atlanta team.** Understood the extension board is not in active development; for reference it is the design in your repo: https://github.com/open-ephys/acquisition-board/tree/master/extension-board . A single, reliable 16 animal board would be far preferable to synchronizing four boards, mainly to reduce clutter in the recording room. Could you please **connect us with the Atlanta team** to scope a custom or validated 16 headstage board (feasibility, timeline, cost)?

**5. Multi board route and a formal quote.** In parallel, please send an **itemized quote** for the multi board path to 16 animals: Acquisition Boards, the I/O boards needed to synchronize them, your SPI 16 channel bipolar headstages, and required cables. **Academic pricing and lead time** appreciated.

**6. Long duration reliability and host PC.** Our recordings run **24 to 72 h continuous**, so reliability is critical. Do you have experience or references for **multi day continuous recording** on multiple synchronized boards, and what **host PC spec** would you recommend for the data and storage load at 16 (and later 32) animals on one machine?

**7. Ceiling to 32 and data format.** You noted multiple boards can share one PC and be synchronized; for planning to **32 animals**, is there a **practical ceiling** on how many boards sync together, and does 32 change the sync or PC setup? Also, what **file format does the Open Ephys GUI record**, and is there an **Intan compatible export**? (We have an existing analysis pipeline and want to understand the migration.)

A short video call to go over the plan for 16 to 32 animals would be very welcome; we are in Korea (KST) but flexible.

Thanks again,
[Your name]
Prof. Kim Staci Jakyong lab, KAIST

### Internal — question → comparison-table cell (do NOT send)
Q1 → row 1 (animals/box) + row 4 (shared-ground on dual adapter) · Q2 → row 4 (isolation) · Q3 → **row 15 NEW (independent record control)** · Q4 → rows 2/13/14 · Q5 → row 11 (price) · Q6 → row 10 (reliability) + row 9 (host PC) · Q7 → row 3 (32 ceiling) + row 7 (data format). Table: [[daq-ecosystem-comparison-xdaq-vs-openephys]].

---

## ✅ REPLY 2 RECEIVED 2026-07-28 — Open Ephys Support (answer to follow-up v2)

> [!success] Answered 4 of 7. Verdict: **2 separate animals per dual adapter is fine** ("no reason not to continue") → the "maximum 4 animals per board" framing is retired, one board = 8 mice. **Per-animal ground isolation is impossible, stated verbatim.** BUT the genuinely new fact: **our bipolar RHD2216 configuration is ALREADY independent referencing per animal.** Recording start/stop confirmed **global**. Custom 16-headstage board punted to Jon Newman with a capacity hedge. **Silently dropped: the itemized quote, multi-day reliability references, the 32-animal ceiling, the file format and Intan export question.**
>
> Attachment received: `Support Andrea Piazzola.docx` (grounding / unipolar vs bipolar explainer, 3 diagrams). Local copy: `~/Downloads/Support Andrea Piazzola.docx`. Its full text is transcribed in §"Attachment" below.

### Answers, question by question

- **Q1 — two separate animals on one dual adapter: ✅ SOFT GREEN LIGHT.** Verbatim: *"The dual headstage adapter was designed to allow two RHD headstages to share a single SPI interface cable and to position the headstages in different configurations, and not to run two animals from the same port."* Then, crucially: *"That said, if your current setup is working reliably and you have not experienced any issues using the dual headstage adapter that way, I don't see a reason why you should not continue using it."*
  → **No engineering objection, only a statement of design intent.** This retires the 2026-07-23 *"maximum of four animals"* framing as a usage convention, not a hardware limit, and confirms the vault's own correction in [[daq-research-findings-primary-sources]] §1. **One board = 8 separate mice → 16 mice needs 2 boards, not 4.**
- **⚠️ NEW BENCH ITEM — dual adapter orientation.** They specify the Intan-recommended wiring, with a diagram: **the SPI cable plugs into the CENTER connector, and the headstages connect to the LEFT and RIGHT connectors.** Referred to the Intan dual headstage adapter datasheet. **Our own C3442 orientation is not documented anywhere in this vault — verify it on the bench.**
- **Q2 — per-animal ground isolation: ❌ IMPOSSIBLE, now first-party verbatim.** *"It is not possible to have an electrically isolated ground for each individual animal within the same acquisition system as the same ground is shared by all the components of the acquisition system."* And specifically for the splitter: *"the SPI tether (and headstage port) has one common ground wire for both headstages, which is in turn connected to the acquisition board ground when the cable is connected."*
  → Confirms the cable-level fact in [[daq-research-findings-primary-sources]] §4 (12 conductors, one ground) and §5 (OE has no isolation in any configuration). Nothing new in substance, but it is now stated by the vendor rather than inferred by us.
- **🔑 Q2, THE ACTUALLY NEW PART — bipolar is already per-animal referencing.** Verbatim: *"Although the acquisition system uses a common ground for all connected headstages, **each headstage can use its own independent reference electrode**, depending on the configuration you choose."* And for our configuration: *"**Essentially, this would already be independent referencing per animal, because each electrode is referenced to a local electrode on the same animal.**"*
  The unipolar caveat does **not** apply to us: in unipolar headstages REF and GND are tied by an **R0 0-ohm jumper** that must be physically removed for independent per-animal referencing. The RHD2216 has no REF pin at all ([[intan-rhd2216-reference]]), so there is nothing to cut.
  → **Consequence for the purchase:** the reference half of "per-animal isolation" is already ours for free. Any Port Expander buys **ground** isolation only. Set against our own measurement that `differential_60Hz ≈ common_mode(floor) × electrode_Z_imbalance` with a measured 53× impedance ratio ([[eeg-60hz-saga]]), and against eNeuro 2022's negligible bleed-through on a shared board ground ([[daq-research-findings-primary-sources]] §3), **the Port Expander should be justified as a port multiplier (mandatory for 16/box, NNX manual p.9) and NOT priced as the 60 Hz fix.**
- **Q3 — independent recording control: ❌ GLOBAL, confirmed.** *"Acquisition and recording start at the same time for all connected headstages. While it is possible to record only a selected subset of channels, there is currently no flexible way to change this dynamically. If you require more advanced or customized recording settings, this would need to be implemented by modifying the plugin, which is fully customizable."* Referred to `gui@open-ephys.org` for customization guidance.
  → Subset selection is **static**, not per-session schedulable. Per-animal start/stop = a plugin fork. **Same answer as XDAQ** (radiens' per-port arguments are "only meaningful in split-ports mode", a mode documented nowhere). **Independent per-mouse scheduling is now dead on both vendors** → the "record continuously, slice per user offline" plan in [[RIG-EXPANSION-HUB]] §7 stands, confirmed from both sides.
- **Q4 — custom 16-headstage board: 🟡 PUNTED, with a capacity hedge.** *"I'm not sure whether the team currently has the capacity to take on a custom design like this, but you're welcome to contact **Jon Newman (jpn@open-ephys.org)** directly."* Jon is named as the main point of contact for custom design requests; they ask for as much detail as possible on requirements. **Second vendor-side hedge on the same idea** (after the extension board being dead). Treat the single-board 16-animal route as vapor unless Jon says otherwise.
- **Q6 — host PC: partial.** Referred to the **Hardware Requirements** page of their documentation; *"depends on your setup and the number of channels you plan to acquire simultaneously"*; *"you should use a fast SSD with sufficient capacity to handle the expected recording data."* **No multi-day continuous-recording references given** — the reliability half of Q6 was not answered.
- **Q5 (itemized quote), Q7 (32-animal ceiling, file format, Intan-compatible export): ❌ NOT ANSWERED.** Silently dropped. Q5 is the second round in which no pricing has been produced.
- **Also unanswered across both rounds:** the video call request.

### Bearing on the decision

**No change to the leading choice** (2× ONE+ R1024 + 8× Port Expander + our RHD2216 headstages, Open Ephys GUI). Open Ephys *hardware* was already out on isolation before this reply; this closes it more politely. Open Ephys *software* remains the decided GUI on whatever box we buy, and that decision never depended on this thread.

What did move:
1. **Board capacity framing corrected in our favour** (8 animals/board, not 4) — matters only if OE hardware is ever reconsidered.
2. **The Port Expander's justification narrows to capacity**, because bipolar already gives us independent per-animal referencing. → carry into [[2026-07-29-kontex-kc-call-prep-rig-finalization]].
3. **Global start/stop is now confirmed by both vendors**, so it stops being a comparison axis.

Still open on OE, if anyone pursues it: itemized quote, 32-animal ceiling, recorded file format and Intan-compatible export path, multi-day reliability references, and Jon Newman on the custom board.

### Attachment — `Support Andrea Piazzola.docx`, transcribed

> [!note] Diagrams not reproduced
> The document carries three images: the SPI tether / common ground wire, the bipolar amplifier input stage (independent in+ and in− per channel), and the unipolar headstage with a single common reference. Only the text is transcribed here; the source file is at `~/Downloads/Support Andrea Piazzola.docx`.

**Ground.** *"It is not possible to have an electrically isolated ground for each individual animal within the same acquisition system as the same ground is shared by all the components of the acquisition system. Specifically, since you are asking about two headstages on one dual adapter, you can see the SPI tether (and headstage port) has one common ground wire for both headstages, which is in turn connected to the acquisition board ground when the cable is connected."*

**Reference.** *"Although the acquisition system uses a common ground for all connected headstages, each headstage can use its own independent reference electrode, depending on the configuration you choose."*

**Bipolar.** *"In the bipolar configuration you intend to use, each recording channel measures the difference between two electrodes, usually pairs of electrodes of similar impedances. You can see each amplifier channel has independent in+ and in- inputs... Essentially, this would already be independent referencing per animal, because each electrode is referenced to a local electrode on the same animal."*

**Unipolar (for contrast, not our case).** *"In a unipolar configuration, activity in each recording electrode is measured against one shared reference electrode... the headstage has a single common reference that is used by all channels. Additionally, in this headstage, REF and GND are tied together using the R0 0-ohm jumper resistor. This resistor can be removed to disconnect the reference electrode from ground, which is what you would need if you wanted to use individual referencing per animal in this case."*

**Grounding your system.** *"Since you mentioned you are dealing with 60 Hz hum, I would suggest troubleshooting the ground connection:"*
- *"Check all GND connections, including GND terminals and the BNC connector shield"*
- *"Use a Faraday cage and verify shield connections"*
- *"Ensure you have a good GND screw making good contact with the animal. You could even attempt to measure the impedance of the ground screw to ensure it is low"*

> [!warning] Their grounding advice conflicts with Intan's, and with our own bench result
> "Use a Faraday cage and verify shield connections" reads as *ground the foil*. **We tested that and dropped it on 2026-07-16** — no headroom left, and the Gen-1 Core has no chassis terminal. Intan's own Noise Reduction app note says the headstage GND *"should not be connected to the Faraday cage or to any external ground"* ([[daq-research-findings-primary-sources]] §2). Earth was exonerated as a source in [[eeg-60hz-saga]]. **Do not re-chase this.**
>
> The last bullet is the one worth keeping: **measure the impedance of the animal ground screw.** That is cheap, and it is the same impedance-imbalance term that dominates our hum.

### Follow-ups still needed
- [ ] **Bench: verify C3442 dual adapter orientation** — SPI cable in the CENTER connector, headstages left and right, per Intan's datasheet and their diagram.
- [ ] Decide whether to pursue **Jon Newman (jpn@open-ephys.org)** on a custom 16-headstage board, or close the OE hardware track entirely.
- [ ] If OE hardware stays alive: chase the **itemized quote** (unanswered twice), the **32-animal ceiling**, the **recorded file format + Intan export**, and **multi-day reliability references**.
- [ ] Carry the **bipolar-already-is-per-animal-referencing** finding into the 2026-07-29 KonteX call → ask KC what the Port Expander's ground isolation buys us **in µV**, given we have no shared reference to isolate.
- [ ] Retire the **"maximum 4 animals per Open Ephys board"** claim wherever it still appears.

---
type: reference
area: rig-expansion
status: done
status-note: "open"
tags:
  - decision
  - hardware
  - open-ephys
  - acquisition
  - scale-up
  - option
created: 2026-07-21
---
# Open Ephys Acquisition Board — a Possible Scale-Up Path (16 mice)

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[_rig-expansion-hub]]** (decision, vendor correspondence, wiring, open items).

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A third candidate for our 16-mouse (→32) recording rig, alongside the XDAQ ONE+ and the Intan RHD Recording Controller. The **Open Ephys Acquisition Board** is fully open-source hardware that runs the same Intan RHD chips we already use, with **free** software (Open Ephys GUI) instead of the paid Allego license.
> **Why it exists.** While checking whether Open Ephys could drive a new XDAQ license-free, we found that Open Ephys also sells its OWN acquisition board, and their repo contains a design for an **extension board** that could in principle reach 16 headstages / 1024 channels. That is exactly our scale-up target, at low cost and with no software license — so it is worth chasing down properly.
> **How to read this page.** §1 = what the board actually does today (8 mice). §2 = the extension-board idea (16 mice, but unvalidated). §3 = why "open hardware" is the real structural advantage. §4 = the honest risk picture. §5 = open questions we are emailing Open Ephys about. See [[intan-rhd-spi-wiring-and-headstage-limits]] for the MISO physics that governs all of this.

> [!quote] Paper-ready
> The Open Ephys Acquisition Board is an open-source data-acquisition system that interfaces with standard Intan RHD headstages over SPI, supporting up to eight headstages (four ports, two headstages per port) and 512 recording channels per board, with the Open Ephys GUI providing free, open-source acquisition software.

Companion email: [[openephys-inquiry-email]]. Sits beside the XDAQ decision in [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]].

---

## 1. What the board does TODAY (verified)

- **Latest (3rd-gen) Open Ephys Acquisition Board = 8 headstages max**, exactly like our XDAQ Core: **4 headstage ports × 2 headstages/port** (2nd headstage per port via a dual adapter). `[src: https://open-ephys.org/acq-board]`
- **512 channels** total (8 × 64ch Intan chips). `[src: https://github.com/open-ephys/acquisition-board]`
- Uses **standard Intan RHD chips** — auto-detects 32- vs 64-ch chips and whether the headstage has an IMU. Our **RHD2216** (bipolar, 16ch) is an Intan RHD chip, so it is in-family (compatibility to confirm — see §5).
- Same governing physics as everything else: **1 chip = 1 MISO line = 1 mouse** ([[intan-rhd-spi-wiring-and-headstage-limits]]). Out of the box the board does **not** reach 16.

## 2. The extension-board idea (16 mice — but UNVALIDATED)

Open Ephys's `acquisition-board` GitHub repo contains an **`extension-board/`** folder with a README describing a board that would add capacity. Verbatim quotes (`[src: https://github.com/open-ephys/acquisition-board/blob/master/extension-board/README.md]`):

> "an additional 4 SPI headstone connectors for a total capacity of up to 16 RHD chips for a maximum number of 1024 channels of neural data."

> "with a few cmos<>lvds bridges (because we dont have enough pins for straight lvds - and this is assuming that the bandwidth of these is not destroyed by the board layout etc) we can **theoretically** throw in a 2nd row of 4 ports, which would get us to 1024 chs per board."

> "an additional 8 channels of digital inputs via a 2nd HDMI connector for a total of 16 channels of digital input."

> **"this is not a finished or tested design yet!"**

**How it would reach 16 (and why it's physics-legit):** it adds **CMOS-to-LVDS bridges** to create **more physical MISO lines** — the only real way to add animals. On open hardware you CAN add the wires; on the sealed XDAQ Core you cannot (that is why the XDAQ Core "get to 16" tricks were all impossible). So the concept does not violate the MISO rule — it obeys it by physically adding MISO lines.

> [!danger] Read this before getting excited
> The extension board is a **speculative design note, NOT a product and NOT a validated board.** The author's own words: "theoretically," "assuming the bandwidth is not destroyed by the board layout," "not a finished or tested design yet." The 16-chip / 1024ch figure is an **aspiration**, not a spec you can order or reliably build today.

## 3. The real structural advantage — OPEN hardware

- **All design files are public.** Custom expansion is genuinely on the table — the extension board itself is proof of concept that the community/Open Ephys can build custom boards.
- We (or a collaborator, or Open Ephys as a paid job) could fabricate/modify boards to our exact 16-mouse need.
- **This is impossible with XDAQ** — Kontex hardware is closed; we are limited to what they sell (Core = 8, ONE+ = 16).
- **Software is free** (Open Ephys GUI, GPL) — no Allego per-seat license (~$2.5–5k). At 16→32 mice that is real money saved. See the software comparison work in [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]].

## 4. Honest risk picture (why this is a candidate, not yet a decision)

**In favour:**
- Cheapest 16-mouse route on paper + no software license.
- Same Intan headstages we already own — reuse.
- Open hardware = custom expansion possible; strong plugin ecosystem; large community.

**Against / risks:**
- The 16-mouse path (extension board) is **unfinished and untested** — betting a live-animal 72h instrument on it stacks engineering risk on top of our existing 60 Hz + surgical-yield problems.
- Switching off Allego/Radiens means **rebuilding our whole pipeline**: `sleep64` sensor map, the `eeg-emg-analysis/` code (assumes XDAT format), impedance workflow, SOPs, and the **video-sync Phase 0a** gate (built on Allego "Gated" mode + BNC breakout, DO 03 / DB25 pin 22 → would need re-implementing in Open Ephys).
- Community support vs vendor support.

**Where it fits:** the credible turnkey 16-mouse routes stay **XDAQ ONE+** or **Intan RHD Recording Controller 1024**. Open Ephys is the **open/low-cost/custom** option — worth pricing and talking to them about, especially if the extension board is further along than the README suggests, or if they will build/validate it for us.

## 5. Open questions → emailing Open Ephys ([[openephys-inquiry-email]])

- Status of the **extension board** — is it real / in progress / buildable / on any roadmap? Can it actually reach **16 headstages**?
- Price + lead time: base Acquisition Board, and any 16-headstage option.
- Does it drive our **Intan RHD2216 bipolar (16ch)** headstages, including reading them correctly (they are bipolar, no reference pin)?
- **Per-animal grounding/isolation** — does the board tie all animals' grounds together, or can each be isolated? (Our 60 Hz history — this is why the Kontex Port Expander exists.)
- Can **multiple boards be synchronized** to reach 16/32 (as an alternative to the extension board)?
- Do they offer **custom hardware work** (paid) to build a validated 16-mouse board?
- Software/support model; is a call possible?

## Next steps
- [ ] Send the [[openephys-inquiry-email|Open Ephys inquiry email]].
- [ ] Feed their answers back into the 3-way comparison (XDAQ ONE+ vs Intan 1024 Controller vs Open Ephys) in [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]].
- [ ] Once facts are in from both vendors → council the "which DAQ / which software" decision.

## Related
- [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] — the main DAQ decision + Kontex thread
- [[openephys-inquiry-email]] — the email we are sending Open Ephys
- [[intan-rhd-spi-wiring-and-headstage-limits]] — the MISO physics (why 8 / 16)
- [[kontex-xdaq-hardware-reference]] — the XDAQ side
- [[eeg-60hz-saga]] — grounding history (why per-animal isolation matters)

---

## REPLY RECEIVED 2026-07-23 — Open Ephys answers

Reply from **Margarida (Open Ephys Support)**. Full log + verbatim quotes: [[openephys-inquiry-email#✅ REPLY RECEIVED 2026-07-23 — Margarida (Open Ephys Support)]]. Net effect on this option:

> [!danger] The extension board (§2) is DEAD
> OE Support: *"I'm not familiar with the extension board design you mentioned... this is not something the Open Ephys team is currently developing, so we're unable to provide any further details."* The `extension-board/` repo folder is a **stale, abandoned concept the vendor won't stand behind.** The single-board route to 16/1024ch is off the table. §2 of this doc is now historical.

**Revised picture of the OE option (post-reply):**

| Item | Answer |
|---|---|
| Base board | 4 ports × 2 RHD chips, 512ch, 30 kSps |
| Animals per board | ✅ **RESOLVED 2026-07-28 = 8 separate animals.** The earlier "max 4 animals" framing is RETIRED. Vendor verbatim: *"if your current setup is working reliably... I don't see a reason why you should not continue using it."* Board is rated "up to 8 RHD headstages on 4 tethers". → 16 mice needs **2 boards, not 4**. See [[openephys-inquiry-email]] §REPLY 2. |
| Extension board (16 on one board) | **DEAD** — not developed, vendor disowns it |
| Real path to 16 | **(a)** 4 acq boards synced via **I/O boards** (their SyncLink equiv), all on one PC/one GUI; **(b)** **custom 16-headstage board** built by OE **Atlanta team** (paid) |
| RHD2216 support | ✅ **Fully supported** — bipolar in+/in−, "optimal for paired differential EEG/EMG" |
| Software | ✅ Free open-source Open Ephys GUI, no paid component |
| Per-animal ground isolation | ❌ **No productized answer** — "depends on your design," punted to docs + Discord. **No Port-Expander equivalent.** |
| Price | On webstore / formal quote; base board + SPI 16ch bipolar headstage **in stock** |
| Support | Paid Training; 1-yr warranty + repairs; Discord community |

**Bottom line:** OE stays the **open / license-free** option but its 16-mouse story got **worse, not better** — the cheap single-board dream (extension board) is vapor. Real 16-mouse routes are now **multi-board (2–4 boards + I/O boards + strong PC)** or a **paid custom Atlanta build** — neither is obviously cheaper or less risky than XDAQ ONE+ once you add boards, I/O sync boards, and a rebuilt pipeline. Its two genuine wins remain: **$0 software** and **confirmed RHD2216 support.** Its two genuine gaps: **no per-animal ground isolation product** (bad for our [[eeg-60hz-saga]]) and **full pipeline rebuild** (XDAT→OE format, sleep64 map, video-sync Phase 0a).

**Open before this can be councilled against XDAQ ONE+ / Intan 1024:**
- [ ] Resolve the **4-vs-8 animals per board** question (decides 2 vs 4 boards for 16) — Discord/GitHub.
- [ ] Per-animal isolation: any OE hardware, or shared board ground only?
- [ ] Prices: board + I/O board + SPI 16ch headstage, for a 16-mouse multi-board build; OR Atlanta custom-build scope + price.

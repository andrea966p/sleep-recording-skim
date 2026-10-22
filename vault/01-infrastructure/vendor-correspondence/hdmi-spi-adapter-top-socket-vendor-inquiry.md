---
tags:
  - procedure
  - vendor
  - email
  - draft
  - hardware
  - intan
  - sadpt
  - headstage
created: 2026-07-14
status: resolved
resolved: 2026-07-18
---

# HDMI/SPI Dual-Socket Adapter — TOP Socket Dead — Vendor Inquiry Drafts

> [!tip] Part of the rig expansion program
> Front door for all of this: **[[RIG-EXPANSION-HUB]]** (decision, vendor correspondence, wiring, open items).

> [!success] RESOLVED 2026-07-18 — NeuroNexus (Jeff) replied. TOP SOCKET DEAD BY DESIGN, NOT A DEFECT. DO NOT RMA.
> **Root cause (vendor, authoritative):** The HDMI port carries max 19 conductors. Intan neural channels are digitized+multiplexed in the chip, then grouped into blocks of up to 64ch transmitted over one **MISO pair** of wires. The **top socket of the SAdpt-XDAQ-OM12 has 4 wires wired to the MISO3 + MISO4 pairs** in the HDMI connector.
> - **XDAQ Core (our Gen-1)** HDMI ports support only **2 MISO pairs = 128ch** (MISO1/MISO2). MISO3/MISO4 lines are **physically absent** in the Core's headstage ports → a headstage on the top socket has nothing to talk on → never detected. Correct, expected behavior for the Core.
> - One+ and AIO support **4 MISO pairs = 256ch** — those DAQs *would* use the top socket. The adapter is built for the higher-end DAQs; the Core simply doesn't wire MISO3/4.
> - Jeff hit this himself at product launch, needed clarification from Kontex — "seems like it should work but doesn't" is a Core hardware limitation, from Intan's architecture + Kontex's DAQ design choices.
> **Consequence:** The **8-headstage ceiling is a hard hardware limit of the XDAQ Core** (4 ports × bottom socket × C3442 dual-headstage cable = 8). Top sockets stay unused forever on the Core. To go past 8 you need a One+/AIO-class DAQ, not more adapters. Kontex draft below no longer needs sending.

> [!abstract] TL;DR
> Draft emails to NeuroNexus (Jeffrey) and Kontex (KC Kong) asking why the **top SPI socket** of our SAdpt-XDAQ-OM12 HDMI↔SPI bridge adapter never detects a headstage, on **both** units we own. Root cause isolated 2026-06-18→07-01 (see [[first-headstage-connection]] and [[2026-07-01]]). Not currently blocking — we scaled around it with the bottom socket + C3442 splitter — but leaves capacity on the table and is worth an RMA/fix ask.
>
> **New thread, not a reply** — separate topic from the DB25/GPIO-sync thread in [[neuronexus-inquiry-email|neuronexus-inquiry-email]].

---

## Background (for whoever sends this)

- Adapter: **SAdpt-XDAQ-OM12** — HDMI male (→ XDAQ Core) + 2× Intan SPI female sockets (top + bottom).
- Symptom: headstage on **top** socket → `priSigs=0`, `port_num_channels={}`, never enumerates. **Bottom** socket, same cable/headstage/port → instant detection.
- Isolation (2026-06-18 → 2026-07-01): 2 SAdpt units (both dead top), 2 headstages (Intan RHD2216/C3313), 2 SPI cables (C3026), all 4 XDAQ HDMI ports, power cycle, daemon restart, Allego mode confirmed correct (`XDAQ_ONE_REC`) — top socket failed every time, bottom worked every time. Fully repeatable swap test.
- Current state: standardized on **bottom-socket-only**, scaling mice per port with the **Intan C3442 dual-headstage adapter** on that bottom socket (2 headstages/port × 4 ports = 8 mice). Stress-tested clean for 72 h ([[2026-07-13]] audit — endurance proven, unrelated EEG-hum issue is a separate earthing problem, see [[earthing-60hz-hum-fix]]).
- Not gating current work, but half the adapter's capacity (top socket) is unused. Worth asking before buying more C3442s / scaling further.

---

## Email draft — NeuroNexus (Jeffrey / support)

**Subject:** HDMI/SPI dual-socket adapter — TOP socket never detects a headstage (both units, all ports, all headstages/cables) — bottom socket works fine

Hi Jeffrey,

Different topic from the DB25/GPIO sync thread — this is about the **SAdpt-XDAQ-OM12 HDMI/SPI bridge adapter** (the block with two Intan SPI sockets, top and bottom, feeding one XDAQ HDMI port).

**Symptom:** a headstage plugged into the **top** SPI socket is never detected by Allego (`priSigs=0`, `port_num_channels={}`), while the **bottom** socket on the same adapter, same port, works immediately.

**Isolation done (2026-06-18 to 2026-07-01):** this was originally mistaken for a dead headstage / wrong Allego mode and cost us several days before we isolated it to the socket itself. We swapped every other variable and the top socket failed every time:
- 2 different SAdpt-XDAQ-OM12 units — **both** have a dead top socket
- 2 different headstages (Intan RHD2216, C3313)
- 2 different C3026 SPI cables
- All 4 XDAQ HDMI ports (1, 3, 4, plus the one under test)
- Allego mode confirmed correct (`XDAQ One (G1) with XR Headstage` / `XDAQ_ONE_REC`)
- Power cycle, daemon restart, 3-min firmware-boot wait — no change

Moving the exact same cable+headstage from top socket → bottom socket on the same adapter, same port: instant detection, clean enumeration, streams fine. This is fully repeatable.

**Current workaround:** we standardized on bottom-socket-only and are now scaling with the **Intan C3442 dual-headstage adapter** instead — one C3442 per XDAQ port on its bottom socket, carrying 2 headstages (2 mice) per port, 4 ports = 8 mice. That's working (validated in a 14 h and later a 72 h stress run). So this isn't blocking us operationally anymore, but we're leaving capacity on the table — we'd like the top sockets working too, especially since we're scaling further.

**Questions:**
1. Is the top SPI socket on SAdpt-XDAQ-OM12 known to be unreliable, or does it need something we're missing (a different cable orientation, a licensing/port-pairing step, firmware)?
2. Is this a manufacturing defect specific to our two units, or a known design issue?
3. Worth an RMA on both adapters, or is there a fix/setting we haven't tried?
4. Does the C3442 dual-headstage adapter (which we now use on the bottom socket) also have top/bottom-socket-equivalent issues we should test for, or is the dead-top-socket issue specific to the SAdpt-XDAQ-OM12 bridge itself?

Happy to send serials/photos and the full allegoserver logs from the isolation sessions if useful.

Thanks,
Andrea

---

## Email draft — Kontex (KC Kong, KC@kontex.io)

**Subject:** XDAQ Core (Gen-1) — HDMI/SPI dual-socket adapter, TOP socket never detects headstage on either unit we own

Hi KC,

New topic from the DB25/digital-sync thread — a hardware question about the **HDMI↔SPI bridge adapter** (NeuroNexus part SAdpt-XDAQ-OM12: HDMI male into the XDAQ Core, two Intan SPI female sockets — top and bottom — out to headstages).

**Symptom:** any headstage on the **top** SPI socket never enumerates (`priSigs=0` in the allegoserver logs, `AMP=0`, `port_num_channels={}`), on every combination we've tried, while the **bottom** socket on the identical adapter works immediately with the same cable and headstage.

**What we ruled out (2026-06-18 to 2026-07-01 isolation), all still failing on the top socket:**
- Both SAdpt-XDAQ-OM12 adapters we own (2 units — identical fault on both)
- 2 headstages (Intan RHD2216 / C3313), 2 SPI cables (Intan C3026)
- All 4 HDMI ports on the XDAQ Core (1, 3, 4)
- Power cycle / daemon restart / Allego restart / multi-minute firmware-boot wait
- Allego system mode (confirmed `XDAQ_ONE_REC` correct — separate, resolved issue)

Swapping only top→bottom on the same physical setup is 100% repeatable: bottom = instant detection, top = nothing.

**Where we landed:** we now run bottom-socket-only, and scale mice per port with the **Intan C3442 dual-headstage adapter** on that bottom socket (2 headstages/port × 4 ports = 8 mice), which we've since stress-tested clean for 72 h. So this isn't gating us today, but we're not using half the adapter's capacity and would like to understand/fix it, especially since we're planning to scale further.

**Questions:**
1. Any known failure mode on the SAdpt-XDAQ-OM12 top socket — manufacturing tolerance, a pin that needs specific seating, firmware/port-pairing requirement?
2. Since it's 2-for-2 on our end, does this look like a batch/design issue worth flagging, or should we treat both units as individually defective and RMA?
3. Is there a way to bench-test/diagnose the top socket independently (continuity/pinout) before shipping back, in case it's something we can fix on our end?
4. Do you have a Gen-1-specific pinout for the SAdpt-XDAQ-OM12's two SPI sockets, so we can DMM-check pin-for-pin which line(s) are actually dead on top vs. live on bottom?

Can share full allegoserver logs, photos of the two adapters on request.

Thanks,
Andrea

---

## Before sending

- [x] Pick recipients / confirm addresses (Jeffrey's NeuroNexus address, `KC@kontex.io`) ✅ 2026-07-14
- [ ] Attach or reference allegoserver logs from the isolation sessions if wanted
- [ ] Send as two separate new threads (not replies to the GPIO-sync thread)

## Related
- [[first-headstage-connection]] — full bring-up log, top-socket false-trail-turned-real-fault section §3–§4
- [[2026-07-01]] — root cause day: "HDMI top SPI socket is dead" (§2), dual-headstage validated
- [[eight-mouse-acquisition-setup]] — current bottom-socket + C3442 8-mouse topology
- [[neuronexus-inquiry-email|neuronexus-inquiry-email]] — the other (DB25/GPIO-sync) vendor thread, contact pattern reference
- [[intan-headstage-troubleshooting]]

---

## Reply — 2026-07-18 (SolutionsKR VIVO, Korean distributor) — CONFIRMS top-socket-dead-by-design

> [!info] Distributor (vivosolkr@gmail.com) forwarded + endorsed Jeff/NeuroNexus's message. Same finding as the RESOLVED callout at top — **independent confirmation from the seller of record**. Nothing new technically; closes the RMA question with the distributor too (no RMA — working as designed).

**Part-number note:** VIVO/Jeff call the adapter **`SAdpt-HDMI-OM12`**; our vault has been calling it **`SAdpt-XDAQ-OM12`**. Same part (HDMI↔dual-Intan-SPI bridge). Treat the two names as aliases.

### Verbatim (archived)

> Dear Andrea
>
> Thanks for the detailed explanation about your requirement in using your XDAQ-Core system with Intan's product.
>
> Unfortunately, it seems that only one connector of the adapter for SPI cable (SAdpt-HDMI-OM12) will work at the same time with the XDAQ-Core. And so, the 8 headstages will be the maximum number that your XDAQ-Core can support when you use those headstages with the RHD dual headstage adapter (Part #C3442). Please understand this situation and let us know if you need more information or support in setting up your experiment set.
>
> For your reference, I additionally share Jeff of NeuroNexus' original message as below. (I think he replied to you directly also.)
>
> #1. Regarding the SAdpt-HDMI-OM12, only one of the two 12-pin polarized connectors will work on the XDAQ Core system. This is due to restrictions based on how the Intan RHD chip design works, and differences between the XDAQ Core and higher models like the XDAQ One+ and AIO. While the One+ and AIO systems support up to 4 Intan chips per HDMI port (up to 256ch), the Core can only support up to two (128ch max).
>
> The digitization and multiplexing of neural signals transmit the signal over two wires, called a MISO pair. Each pair can handle up to 64ch. Since the Core only has two MISO pairs per HDMI port, it is hardwired to pairs 1 & 2. When the SAdpt-HDMI-OM12 in plugged into the Core, these two pairs are directly connected to one of the Intan polarized connectors as your customer noted. Since the Core system does not have MISO pairs 3 & 4 in the HDMI ports, nothing happens when connecting an Intan headstage to the second Intan polarized connector.
>
> To use a second Intan headstage with the Core system, another SAdpt-HDMI-OM12 will need to be used on a different port.
>
> #2. One other detail I forgot to include – Intan's own RHD dual headstage adapter will work in this customer's situation with headstages up to 64ch with a single SAdpt-HDMI-OM12 on an XDAQ Core.
> https://intantech.com/RHD_SPI_cables.html?tabSelect=RHDdual&yPos=0

**Takeaway (unchanged):** 8-headstage ceiling on the Core is a hard limit (4 ports × bottom socket × C3442 dual). Past 8 needs a One+/AIO DAQ. Top sockets stay unused forever on the Core.

---

## Follow-up to VIVO — round 2 (✅ SENT 2026-07-18) — permanent chassis-earth connector + EEG noise from nearby gear

> [!abstract] Why this email
> Two new asks in the same VIVO thread: (1) a **proper earth/chassis-ground connector for our Gen-1 XDAQ Core** — right now the earth is a wire *taped* to the chassis and run to the wall earth, we want something permanent/stable; (2) whether the **physical placement** of the XDAQ + Intan headstages next to 2 PCs, a WiFi router, 2 Raspberry Pi, an Ethernet switch, HDMI cables and a power multitap **adds noise to the mouse EEG**.
>
> ⚠️ **Reality check for us (not for the vendor):** per [[eeg-60hz-saga]] / [[headstage-shielding-faraday-foil]], **earth has been EXONERATED as the 60 Hz root cause** — the real wall is open frontal electrodes (nonphysical impedance). A better earth connector is good hygiene + mechanical stability, NOT expected to move the 60 Hz floor. Frame the ask as "we want a permanent, stable earth" not "this will fix our hum." KC already gave the *signal* star-ground scheme (Core = hub, each device GND home-runs to DB25 pin 14, see [[neuronexus-inquiry-email#Reply — round 3b received 2026-06-05 (KC Kong)|round-3b]]); this new ask is specifically the **chassis→wall-earth** path, which the Gen-1 Core lacks a dedicated terminal for (Core2 has 2 banana terminals SYS GND + Chassis GND; our Gen-1 has only a single GND pin).

> **To:** SolutionsKR VIVO <vivosolkr@gmail.com> — VIVO ONLY (Jeff gets a separate email, see below)
> **From:** andrea96p@kaist.ac.kr
> **Subject:** Re: XDAQ Core + Intan — permanent earth-ground connector, and EEG noise from nearby equipment

Dear VIVO,

Thank you, and thank you Jeff — that fully explains the single-connector behavior of the SAdpt-HDMI-OM12 on the XDAQ Core, and confirms the 8-headstage ceiling for our system. That's clear now.

Two follow-up questions on our Gen-1 XDAQ Core (serial 0C006218):

1. **A permanent earth-ground connector for the XDAQ Core.** For noise reasons we tie the XDAQ to building earth. Right now this is literally a wire taped to the chassis and run to the wall earth, which is neither mechanically stable nor reliable. Our Gen-1 Core has only a single small GND pin, not the dedicated banana ground terminals of the larger units. Is there a proper, permanent way to earth-ground this chassis — a screw-terminal, a grounding lug, a designated chassis screw, or an accessory/adapter you sell — so we can make a solid, stable earth connection rather than a taped wire? If there's a recommended grounding point on the enclosure, a photo or diagram would help.

2. **Effect of nearby equipment on the EEG recordings.** The XDAQ and the Intan headstages (analog cable running ~36 cm down to the animal) sit close to a fair amount of other equipment: two PCs, a WiFi router, two Raspberry Pi camera nodes, an Ethernet switch, several HDMI cables, and a power multitap. In your experience, can the proximity of any of these — mains-powered devices, the WiFi router, the switched-mode supplies, the digital cabling — couple noise into the mouse EEG? If so, which items tend to matter most, and what separation distances or layout/shielding practices do you recommend for a low-noise Intan recording setup (e.g. keeping the analog headstage run away from power/HDMI, distance from the router/PSUs, cable routing, whether to shield the headstage or the analog cable)? And if you have any advice on how to properly place the Intan headstages, the SPI cables, the surrounding environment and such, I would really appreciate you sharing it.

For context, we do see 60 Hz mains pickup in some recordings and are working through it on the electrode side; I'd like to make sure the bench layout and grounding aren't quietly making it worse.

Thank you again for the clear explanations and the help.

Best regards,
Andrea
andrea96p@kaist.ac.kr

---

### Sent (round 2) — awaiting VIVO reply
- [x] Sent to VIVO only 2026-07-18. Awaiting reply on: permanent chassis-earth connector for Gen-1 Core + noise from nearby gear + placement advice.

---

## Follow-up to Jeff (NeuroNexus) — round 2 (✅ SENT 2026-07-18) — general noise-reduction tips beyond the manual

> [!abstract] Why this email
> Separate email from the VIVO one above. Asks Jeff (who answers the technical/experience side directly) for **general noise-reduction tips for the recording rig that aren't in the manual** — his own bench experience for a low-noise Intan setup. Gives him the rig specifics that matter for noise: **custom-made tether attached to an 8-pin rotary slip ring** (freely-moving mouse), RHD2216 bipolar headstage, ~6 ft C3026 analog SPI run (~36 cm down to the animal), Faraday-foil around the headstage already tried, copper-coil cable shield landed on a recorded channel as a noise reference.

> **To:** Jeff / NeuroNexus support
> **From:** andrea96p@kaist.ac.kr
> **Subject:** XDAQ Core + Intan RHD2216 — general noise-reduction tips for a freely-moving mouse EEG rig?

Dear Jeff,

Thanks again for the clear explanation on the SAdpt adapter and the MISO-pair limits — that settled it for us.

A more open-ended question, if you have a moment: beyond what's in the manual, do you have any general noise-reduction tips from your own experience for keeping a low-noise Intan recording, specifically for a freely-moving mouse EEG/EMG setup?

Some details of our rig that may be relevant:

- **XDAQ Core Gen-1**, **Intan RHD2216** bipolar headstage (one 16-ch chip per mouse), bipolar left-hemisphere EEG (frontal + parietal) plus neck EMG, animal ground on a dedicated dura pin.
- The animal is **freely moving**: a **custom-made tether** connects the implant to an **8-pin rotary slip ring** (commutator) that lets the mouse rotate without twisting the wires, then out to the headstage. The slip ring and the custom tether are both in the signal path before the headstage.
- The headstage sits at the top of the chamber with roughly a **36 cm analog run** down to the animal, then a **6 ft C3026 SPI cable** back to the XDAQ.
- We already wrap the **headstage in Faraday foil**, which helped, and we land the **cable's copper-coil shield on a spare recorded channel** as an environmental-noise reference rather than on ground.

We do see 60 Hz mains pickup in some recordings and are chasing it primarily on the electrode side, but I'd value any hardware/layout wisdom you have — things like: does a slip ring / custom tether commonly add noise and how to mitigate it, grounding of the tether or slip-ring body, cable routing and separation from mains/digital lines, whether shielding the analog run (not just the headstage) is worth it, filtering/referencing choices in Allego, or anything else you've found matters in practice.

Thank you for your time and patience.

Best regards,
Andrea
andrea96p@kaist.ac.kr

### Sent (Jeff round 2) — awaiting reply
- [x] Sent to Jeff only 2026-07-18. Awaiting general noise-reduction tips (slip-ring/custom-tether/analog-run/shielding/referencing).

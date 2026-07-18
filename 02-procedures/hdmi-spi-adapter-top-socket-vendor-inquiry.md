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

> [!success] RESOLVED 2026-07-18 — NeuroNexus (Jeff) replied. TOP SOCKET DEAD BY DESIGN, NOT A DEFECT. DO NOT RMA.
> **Root cause (vendor, authoritative):** The HDMI port carries max 19 conductors. Intan neural channels are digitized+multiplexed in the chip, then grouped into blocks of up to 64ch transmitted over one **MISO pair** of wires. The **top socket of the SAdpt-XDAQ-OM12 has 4 wires wired to the MISO3 + MISO4 pairs** in the HDMI connector.
> - **XDAQ Core (our Gen-1)** HDMI ports support only **2 MISO pairs = 128ch** (MISO1/MISO2). MISO3/MISO4 lines are **physically absent** in the Core's headstage ports → a headstage on the top socket has nothing to talk on → never detected. Correct, expected behavior for the Core.
> - One+ and AIO support **4 MISO pairs = 256ch** — those DAQs *would* use the top socket. The adapter is built for the higher-end DAQs; the Core simply doesn't wire MISO3/4.
> - Jeff hit this himself at product launch, needed clarification from Kontex — "seems like it should work but doesn't" is a Core hardware limitation, from Intan's architecture + Kontex's DAQ design choices.
> **Consequence:** The **8-headstage ceiling is a hard hardware limit of the XDAQ Core** (4 ports × bottom socket × C3442 dual-headstage cable = 8). Top sockets stay unused forever on the Core. To go past 8 you need a One+/AIO-class DAQ, not more adapters. Kontex draft below no longer needs sending.

> [!abstract] TL;DR
> Draft emails to NeuroNexus (Jeffrey) and Kontex (KC Kong) asking why the **top SPI socket** of our SAdpt-XDAQ-OM12 HDMI↔SPI bridge adapter never detects a headstage, on **both** units we own. Root cause isolated 2026-06-18→07-01 (see [[first-headstage-connection]] and [[2026-07-01]]). Not currently blocking — we scaled around it with the bottom socket + C3442 splitter — but leaves capacity on the table and is worth an RMA/fix ask.
>
> **New thread, not a reply** — separate topic from the DB25/GPIO-sync thread in [[01-infrastructure/hardware-sync/neuronexus-inquiry-email|neuronexus-inquiry-email]].

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
- [[01-infrastructure/hardware-sync/neuronexus-inquiry-email|neuronexus-inquiry-email]] — the other (DB25/GPIO-sync) vendor thread, contact pattern reference
- [[intan-headstage-troubleshooting]]

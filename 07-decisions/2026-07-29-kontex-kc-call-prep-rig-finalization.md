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
status: open
call_date: 2026-07-29
counterpart: KC Kong (KonteX Neuroscience)
---
# Kontex Call Prep — KC Kong, 2026-07-29 — FINALIZING the 32-Mouse Rig

> [!abstract] TL;DR — what this call is for
> This is the **finalization call**. The last blocking unknown (can the Port Expander drive our Intan headstages) was answered YES by KC on 2026-07-28, so the XDAQ path is un-blocked. The goal tomorrow is to walk out with **every part number, quantity and cable length pinned down**, plus the answers to a handful of questions that change the build rather than just the price.
>
> **Target build: 32 mice = 2× XDAQ ONE+ (R1024 tier) + 8× Port Expander + our existing Intan RHD2216 headstages.**
>
> Priorities, in order: **(A) the exact EXP-port-to-mouse chain** and whether isolation survives it · **(D+E) the two-PC and SyncLink tangle**, now the main unresolved topic · **(F) commutator pricing with a volume discount**, the biggest money question on the call · **(C) Linux driver**, a hard requirement we run on today · **(B) cable lengths**, now mostly solved · **(G) the package quote**.
>
> **Two things changed on 2026-07-28:** the tether was shortened to **22.5 cm including the slip ring**, comfortably under the ~40 cm KC flagged, so cable length is no longer a design risk. And **KC confirmed two PCs are needed** — but not why, whether it is truly unavoidable, or how SyncLink is supposed to work once everything runs under the Open Ephys GUI. §6 attacks that.
>
> Print §9 and use it as the live checklist during the call.

Background docs: ⭐ [[xdaq-32-mouse-wiring-and-channel-law]] (the deep wiring + channel law), [[2026-07-24-daq-32-mouse-final-comparison]] (the 3-way decision), [[intan-rhd-spi-wiring-and-headstage-limits]] (MISO physics), [[kontex-xdaq-hardware-reference]], [[eeg-60hz-saga]] (why isolation matters), [[2026-07-21-kontex-kc-call-prep]] (the previous call).

---

## 1. Where we stand going in

**Settled, do not re-litigate:**

| Fact | Status |
|---|---|
| **Animals = XR recording channels ÷ 64** (64 ch reserved per headstage slot) | ✅ vendor docs, two independent figures |
| CORE2 = 8 mice, ONE+ **R512 = 8**, ONE+ **R1024 = 16**, AIO = 16 | ✅ vendor docs |
| **32 mice = 2 boxes.** No single-box option in any model | ✅ derived + vendor docs |
| **SPI splitter (C3442) cannot exceed a box's ceiling** — slot limit, EXP port carries 1 MISO, and it re-shares ground | ✅ Intan + Kontex docs |
| **Intan RHD2216 headstages ARE usable with the Port Expander** | ✅ **KC confirmed 2026-07-28** |
| We are dropping Allego and running the **Open Ephys GUI** (free, Kontex-supported for XR mode) | ✅ our decision |
| ONE+ has **Sys GND + Chassis GND** terminals; Kontex documents bonding them to ground a Faraday cage | ✅ vendor docs |

**Our situation, for context when KC asks:**
- Chronic mouse **sleep** EEG/EMG. Bipolar montage, RHD2216, ~4 channels used per mouse. Record-only (XR), never stimulation.
- Runs are **72 hours continuous**, live animals. Reliability outranks features.
- Currently 8 mice on a Gen-1 XDAQ Core, fully maxed (8 × 64 = 512 ch).
- Tether is now **22.5 cm including the slip ring** (shortened 2026-07-28), comfortably under the ~40 cm KC flagged as too long.
- Long-running **60 Hz** problem; per-animal ground isolation is the main thing we are buying.
- Host PC runs **Ubuntu Linux**.

---

## 2. 🅐 The EXP-port-to-mouse chain (highest priority)

KC has confirmed Intan headstages work. What we need now is the chain, part by part, so it can go on a quote and be wired without guesswork.

1. **What is the exact chain from a Port Expander EXP port to an Intan RHD2216?** Part numbers in order. Is it `EXP port (HDMI) → SAdpt-XDAQ-OM12 → Intan SPI cable → RHD2216`, or a different adapter?
2. **Is the per-animal ground/reference isolation preserved all the way to the Intan headstage?** The Port Expander's value to us is entirely this. If isolation stops at the adapter, we need to know.
3. The SAdpt-XDAQ-OM12 has **two Omnetics sockets, P1 and P2**. An EXP port should carry only **one MISO line**. **When the adapter hangs off an EXP port, is only P1 live?** Confirm one mouse per EXP port.
4. **Is one mouse per EXP port correct**, giving 4 per Port Expander and 16 per ONE+ R1024? (Sanity-check against the channel law: 1024 ÷ 64 = 16.)
5. **Can we reuse our existing 8 RHD2216 headstages and existing SAdpt-XDAQ-OM12 units** on the new build, or are different revisions required?
6. Does anything change electrically when **all 4 EXP ports are populated**, versus one? Any per-port power budget to respect?

---

## 3. 🅑 Cable lengths and physical layout — ✅ MOSTLY SOLVED, confirm and move on

> [!success] Update 2026-07-28: **the tether is now 22.5 cm including the slip ring.** Comfortably under the ~40 cm KC flagged as too long. The animal-side run is no longer a design risk, so this section is now a quick confirmation rather than a problem to solve.

7. **Confirm 22.5 cm (tether including slip ring) is well within spec** on the Port Expander → Intan RHD2216 path.
8. The remaining long run is **rack to chamber**. Which link should carry it, and what length is supported? Two candidate layouts:
   - **(a) Port Expanders at the rack, next to the XDAQ:** short KonteX HDMI cables from box to Port Expander, and a **long run from EXP port to the commutator**.
   - **(b) Port Expanders up at the chamber tops:** a **long KonteX HDMI cable from XDAQ to Port Expander**, short runs below.
   Layout (a) keeps 8 mains-powered Port Expanders together and tidy, so it is our default. **Which does Kontex recommend, and what is the maximum supported length on the link that has to be long?**
9. **What KonteX HDMI cable lengths are available**, and what is the longest still specified for reliable operation?
10. Any guidance on **Intan SPI cable length and gauge** on the Port Expander path?
11. With **32 animals**, we have 2 boxes + 8 Port Expanders + 32 commutators. **Any recommended rack layout?** Specifically, keeping 8 separately-powered Port Expanders tidy and their grounds clean.

---

## 4. 🅒 Linux, software, and record control

We run Ubuntu. The ONE+ manual lists driver downloads for Windows and macOS, and for Linux it says only **"Contact us."** This is a hard requirement, not a nice-to-have.

12. **Is there a supported Linux driver for the ONE+?** Which distributions and kernel versions, and how is it distributed and updated?
13. **Is the Open Ephys XDAQ plugin fully supported on Linux**, with the same feature set as Windows?
14. Our current Gen-1 Core needed FrontPanel plus a `plugdev` udev rule on Ubuntu. **Does the ONE+ need equivalent setup?**
15. **Does the Open Ephys XDAQ plugin correctly enumerate a Port Expander**, showing the 4 isolated animals on a port as separate, identifiable streams? How are animals labelled so we can map stream → mouse reliably?
16. **Does the plugin expose the DB25 signals** — `DAQ ON`, `Sample CLK`, DI-03…08, DO-03…08 — for our camera synchronisation?
17. Open Ephys GUI has a **global** record start/stop. **Does the XDAQ plugin add any per-port or per-animal record control**, or is continuous recording plus offline slicing the only option?
18. Any known limitations of the Open Ephys plugin **compared with Radiens** that we should know about before committing to it?

---

## 5+6. 🅓🅔 Two PCs and SyncLink — THE MAIN UNRESOLVED TOPIC

> [!warning] Status after 2026-07-28: **KC confirmed we need 2 PCs**, but it is not clear *why*, whether it is genuinely unavoidable, or how SyncLink fits once everything runs under the Open Ephys GUI. These three questions are entangled and should be worked as one topic.

### 6.1 First, the question that may dissolve the whole problem

> [!important] Do we actually need the two boxes sample-locked at all?
> Worth putting to KC directly, because the answer may make SyncLink unnecessary and 2 PCs harmless.
>
> **Mice 1-16 sit on box A and mice 17-32 on box B. They are different animals in different chambers.** There is no scientific requirement to align mouse 3 to mouse 20 at sub-millisecond precision. Nothing in sleep staging compares two animals sample-by-sample.
>
> What we genuinely need is:
> 1. **Each mouse aligned to its own video**, which is a per-chamber TTL problem already solved by our camera pulse train, not a box-to-box problem.
> 2. **A common wall-clock notion of "which mouse was recorded when"** for the session journal, which is a seconds-level requirement satisfied by NTP.
>
> If that reading is right, **SyncLink is optional for us**, the two boxes may free-run, and the 2-PC requirement stops mattering. **Ask KC to sanity-check this reasoning** — if he agrees, it removes 2 units, their cabling and their cost from the build, and closes the topic.

### 6.2 If two PCs really are required

19. **Why exactly?** Is the limit that the **Open Ephys XDAQ plugin enumerates only one XDAQ device per GUI instance**, or is it something in the driver, the Thunderbolt stack, or the firmware? Knowing which tells us whether it might change in a future plugin release.
20. Data rate is not the reason: 32 mice × 16 ch × 2 bytes is about **1 MB/s at 1 kHz** and **31 MB/s at 30 kHz**. **Confirm bandwidth is not the constraint.**
21. If two PCs: **what specification does each need?** Is the **Mac Mini M4 Pro** reference configuration adequate for one box and 16 animals? Only one native Thunderbolt 3 port is then needed per machine, which widens our choices considerably.
22. Is the *"each XDAQ to its own PC"* wording in the SyncLink manual a **SyncLink-specific** requirement, or general to two-box operation?
23. If we ever did run both on one PC, is there a **stable serial number or persistent device ID** to bind each box to? (Open Ephys warns board ordering can depend on USB descriptors. For a 32-animal chronic study, mice silently swapping identity between sessions would be a serious data-integrity failure.)

### 6.3 SyncLink under the Open Ephys GUI — how would it even work?

This is the part that does not currently make sense to us, and it should be spelled out concretely.

24. **Does the Open Ephys XDAQ plugin support SyncLink at all, or is SyncLink a Radiens-only feature?** If the plugin cannot see it, we would be buying hardware whose output never reaches our data.
25. **With SyncLink fitted, what actually appears in the recorded data?** Concretely: do the two boxes share a sample clock such that **sample N on box A is simultaneous with sample N on box B**? If so, offline alignment becomes trivial indexing. If not, what does SyncLink give us that a shared TTL does not?
26. Open Ephys performs its own online sync inside the Record Node using a shared TTL line, but **that only works within a single GUI instance**. With two PCs running two independent instances, **the GUI cannot sync anything across them** and alignment must happen offline. **Does KC agree?** If yes, then under the Open Ephys GUI the practical choice is: SyncLink for hardware-locked clocks, or a shared TTL recorded into both files and aligned offline.
27. If we go the **shared-TTL** route: which input should carry the pulse train, a **BNC DI** or a **DB25 DI-03…08** line? Confirm the digital input is sampled at the headstage rate and lands in the recorded data on both boxes.
28. Can **`DAQ ON`** (logic high at recording onset) and **`Sample CLK`** be used to cross-check alignment between the two boxes and our cameras? Is `Sample CLK` free-running or gated to acquisition?
29. **Without SyncLink, what clock drift should we expect between the two boxes over a 72-hour run?** (For calibration: our cameras drift about **204 ppm**, which is roughly 8.8 s per 12 h, so we know to take drift seriously and measure rather than assume.)

> [!note] One upside of two PCs, worth stating on the call
> The Open Ephys GUI has a **single global record start/stop**. Two independent PCs therefore restore **independent start/stop for each group of 16 mice**, which a single-PC build would not have. For a multi-user rig that is a feature, not just a cost.

---

## 7. 🅕 Commutators, grounding, reliability

> [!important] ⭐ COMMUTATOR PRICING IS THE BIGGEST MONEY QUESTION ON THIS CALL
> At **32 units** the commutators are the **largest single line in the entire rig**, plausibly larger than both XDAQ boxes combined. For reference, the Open Ephys torque-free SPI commutator lists at **€2,595 each, which is €83,040 for 32**. The STD-versus-PRO choice and the volume discount together move the budget more than the DAQ decision does.

30. **List price for Commutator STD and Commutator PRO**, each, and lead time.
31. ⭐ **What volume discount applies at 32 units?** Ask explicitly, and ask for it **as part of the full 32-mouse package** (2 boxes + 8 Port Expanders + 32 adapters + 32 commutators + all cabling) rather than line by line. **A package price for the whole build is what we want on paper.**
32. Is there a **mixed option** — for example STD on most animals and PRO only where torque proves to be a problem — without losing the volume price?
33. **Do KonteX commutators work with an Intan RHD2216 headstage?** The commutator pages list only KonteX headstages. If not, what does Kontex recommend for the Intan path?
34. For **chronic 72-hour mouse sleep recording** with our **22.5 cm tether including slip ring**: is the passive **STD sufficient**, or is the motorised **PRO** genuinely needed? What is the breakaway torque, and what does the animal-side end weigh? (Our tether is short, which should favour the STD.)
35. We already run slip rings on the current 8-mouse rig. **Is there any reason not to reuse them**, or a concrete reason the KonteX units would be better?
36. **Grounding:** the ONE+ has Sys GND and Chassis GND terminals and the docs recommend bonding them and grounding the Faraday cage from that node. **With 8 Port Expanders providing per-animal isolation, does that recommendation still hold, or does it change?** We have a long-running 60 Hz problem and our current Gen-1 Core has no chassis terminal at all, which is why we could never properly ground our foil shielding.
37. **Any customer running 16 or 32 animals continuously for multiple days on ONE+?** We need a reliability reference, ideally someone we can ask.
38. Our Gen-1 Core has a history of **crashing on sensor/channel reconfiguration**. **Is that resolved on ONE+?**
39. What is the **warranty and support arrangement in Korea**, and what are typical RMA turnaround times from KAIST?

---

## 8. 🅖 Commercial and model questions

40. **Confirm the tier: we need ONE-R1024 for 16 animals; R512 gives only 8.** Is **SR64 versus SR128** irrelevant to us given that we never stimulate?
41. **Is R512 → R1024 a field firmware upgrade**, or must the 1024 tier be specified at purchase? Same question for headstage-port licensing.
42. **AIO versus ONE+:** both give 16 animals. AIO adds an integrated 4-channel video processor and a 4-channel optogenetics LED driver. **What exactly is the video processor** — what cameras, what format, and does it hardware-timestamp frames against the neural sample clock? We currently solve video sync with our own camera rig and a TTL pulse train, so if AIO does this natively it could be worth the difference. Price delta?
43. **Can our existing Gen-1 Core be used as a third unit** alongside two ONE+ boxes, adding 8 more animals for 40 total? Or is there a **trade-in or upgrade path**?
44. **Can the purchase be phased** — one ONE+ plus 4 Port Expanders now for 16 animals, the second set later — with no penalty and no compatibility risk between batches? If phasing costs us the volume discount, say so explicitly.
45. ⭐ **Formal PACKAGE quote** for the full build (§9 table), delivered to **KAIST, Daejeon, Korea**: **whole-package price with volume discount**, plus unit prices for the record, lead time, shipping, import duty and VAT handling, and whether we buy direct or through a Korean distributor.

---

## 9. THE BUILD — confirm every line on the call

Print this. Fill in the blanks live.

| #   | Item                                                     | Part number         | Qty                  | Unit                  | Confirmed?                           |
| --- | -------------------------------------------------------- | ------------------- | -------------------- | --------------------- | ------------------------------------ |
| 1   | XDAQ ONE+, **1024ch tier**                               | ONE-R1024-SR64      | **2**                | ⏳                     | ☐                                    |
| 2   | 200 W DC power adapter                                   | supplied            | 2                    | incl                  | ☐                                    |
| 3   | Thunderbolt 3 cable                                      | supplied            | 2                    | incl                  | ☐                                    |
| 4   | Port Expander                                            | SAdpt-Port-EXP      | **8**                | $1,525 (quote 262024) | ☐                                    |
| 5   | USB-PD adapter for Port Expander                         | supplied            | 8                    | incl                  | ☐                                    |
| 6   | KonteX HDMI cable, XDAQ → Port Expander                  | ⏳                   | **8**                | ⏳                     | ☐ length?                            |
| 7   | EXP → Intan interface adapter                            | SAdpt-XDAQ-OM12(1)? | **32**               | $275                  | ☐ **chain confirmed?**               |
| 8   | Intan SPI cable, adapter → headstage                     | Intan C3213 / C3206 | 32                   | $415 / $295           | ☐ length?                            |
| 9   | Commutator                                               | STD or PRO          | **32**               | ⏳                     | ☐ **STD vs PRO?**                    |
| 10  | Intan RHD2216 headstage                                  | C3313               | **32**               | $820                  | ☐ we own 8, need ~24                 |
| 11  | SyncLink                                                 | SyncLink            | **0 or 2**           | ⏳                     | ☐ **needed at all? works under OE?** |
| 12  | DB25 breakout board                                      | ⏳                   | 1-2                  | ⏳                     | ☐                                    |
| 13  | 4 mm banana ground leads                                 | generic             | ~6                   | —                     | ☐                                    |
| 14  | Acquisition PC                                           | ⏳                   | **2** (KC confirmed) | ⏳                     | ☐ spec each? truly unavoidable?      |
| —   | ⭐ **PACKAGE PRICE, all of the above, volume discounted** | —                   | 1                    | ⏳                     | ☐ **get this in writing**            |

**Not on this build:** Intan C3442 splitter (cannot exceed the slot ceiling, and it defeats isolation) · Allego/Radiens licence (we are on the Open Ephys GUI).

---

## 10. What we must leave the call with

1. ✅ The **exact EXP → Intan RHD2216 chain**, with part numbers, and confirmation that isolation survives it.
2. ✅ **Whether SyncLink is needed at all** — and if the two boxes do not need sample-locking (§6.1), drop it from the build.
3. ✅ **If SyncLink is bought: exactly how it works under the Open Ephys GUI, and what appears in the recorded data.** We must not buy hardware whose output the software cannot see.
4. ✅ **Why two PCs**, whether it is truly unavoidable, and the specification each needs.
5. ✅ ⭐ **Commutator pricing with the volume discount at 32 units**, STD and PRO, plus Intan-headstage compatibility.
6. ✅ A **yes or no on Linux** driver and Open Ephys plugin support.
7. ✅ Confirmation the long rack-to-chamber run is within spec, and which link carries it.
8. ✅ ⭐ A **written package quote** for the full 32-mouse build, discounted, delivered to KAIST.

## 11. Notes to take during the call

*(leave blank, fill live)*

## Related
- ⭐ [[xdaq-32-mouse-wiring-and-channel-law]] · [[2026-07-24-daq-32-mouse-final-comparison]] · [[2026-07-21-kontex-kc-call-prep]] · [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] · [[intan-rhd-spi-wiring-and-headstage-limits]] · [[eeg-60hz-saga]]

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
> Priorities, in order: **(A) the exact EXP-port-to-mouse chain** and whether isolation survives it · **(B) cable lengths**, which is the one thing that can break the build physically · **(C) Linux driver**, which is a hard requirement we run on today · **(D) one PC or two** · **(E) sync** · **(F) commutators** · **(G) the quote**.
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
- Headstages sit at the **top of the chamber**, roughly **36 cm** of run down to the animal. KC previously flagged ~40 cm as too long — this must be solved properly this time.
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

## 3. 🅑 Cable lengths and physical layout (the thing that can break the build)

This is where our rig is unusual and where a wrong assumption costs real money. KC previously said a ~40 cm headstage run was too long, and our chambers need roughly 36 cm.

7. **Maximum supported length for each link:** XDAQ → Port Expander (KonteX HDMI cable); Port Expander EXP → commutator; commutator → headstage (Intan SPI cable).
8. **What KonteX HDMI cable lengths are available**, and what is the longest that is still specified for reliable operation?
9. Our geometry: headstages at chamber top, **~36 cm down to the animal**. **What is the recommended topology for this?** Specifically, does the commutator sit at the chamber top with a short tether below it?
10. On the Intan side we would use ultra-thin SPI cable for the animal-side run. **Any Kontex guidance on Intan SPI cable length and gauge on the Port Expander path?**
11. With **32 animals**, we have 2 boxes + 8 Port Expanders + 32 commutators. **Is there a recommended rack or physical layout?** Any guidance on keeping 8 separately-powered Port Expanders tidy and their grounds clean?

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

## 5. 🅓 One PC or two

Kontex's SyncLink documentation says *"connect each XDAQ to its corresponding PC. Each SyncLink operates as the synchronization interface for its associated XDAQ–PC pair."* We would prefer one PC, but we need this settled because it also decides the PC purchase (Thunderbolt ports cannot be added later).

19. **Can one PC host two XDAQ ONE+ units in a single Open Ephys GUI instance**, with two source nodes? Or is one PC per box genuinely required?
20. If one PC: confirm it needs **two native Thunderbolt 3 ports**, and confirm a recommended machine. Is the **Mac Mini M4 Pro** reference configuration adequate for **two** boxes and 32 animals?
21. If one PC: how do the two boxes get **identified and distinguished** in the GUI? (The Open Ephys project warns that board ordering can be arbitrary and depends on USB descriptors. For a 32-animal chronic study, mice silently swapping identity between sessions would be a serious data-integrity problem.) **Is there a stable serial number or persistent device ID we can bind to?**
22. Is the "each XDAQ to its own PC" wording a **SyncLink-specific** requirement, or a general one?

---

## 6. 🅔 Synchronisation

23. **Is SyncLink required to run two ONE+ boxes together**, or can we simply feed a shared TTL pulse train into a digital input on both and align in software? For **sleep staging on 4-second epochs**, sub-millisecond alignment is far more than we need.
24. **Does SyncLink work under the Open Ephys GUI**, or is it Radiens-only?
25. If we skip SyncLink: which input should carry the shared pulse — a **BNC DI**, or a **DB25 DI-03…08** line?
26. Can **`DAQ ON`** (logic high at recording onset) and **`Sample CLK`** be used to cross-check alignment between the two boxes and our cameras? Is `Sample CLK` free-running or gated to acquisition?
27. Do the **two boxes free-run independently** without SyncLink, and what clock drift should we expect between them over a 72-hour run?

---

## 7. 🅕 Commutators, grounding, reliability

28. **Price and lead time for Commutator STD and Commutator PRO.** This is the largest single line in the whole rig at 32 units, so the STD-versus-PRO decision matters more than the DAQ choice.
29. **Do KonteX commutators work with an Intan RHD2216 headstage?** The commutator pages list only KonteX headstages. If not, what does Kontex recommend for the Intan path?
30. For **chronic 72-hour mouse sleep recording**: is the passive STD sufficient, or is the motorised PRO genuinely needed? What is the breakaway torque, and what does the animal-side end weigh?
31. **Grounding:** the ONE+ has Sys GND and Chassis GND terminals and the docs recommend bonding them and grounding the Faraday cage from that node. **With 8 Port Expanders providing per-animal isolation, does that recommendation still hold, or does it change?** We have a long-running 60 Hz problem and our current Gen-1 Core has no chassis terminal at all, which is why we could never properly ground our foil shielding.
32. **Any customer running 16 or 32 animals continuously for multiple days on ONE+?** We need a reliability reference, ideally someone we can ask.
33. Our Gen-1 Core has a history of **crashing on sensor/channel reconfiguration**. **Is that resolved on ONE+?**
34. What is the **warranty and support arrangement in Korea**, and what are typical RMA turnaround times from KAIST?

---

## 8. 🅖 Commercial and model questions

35. **Confirm the tier: we need ONE-R1024 for 16 animals; R512 gives only 8.** Is **SR64 versus SR128** irrelevant to us given that we never stimulate?
36. **Is R512 → R1024 a field firmware upgrade**, or must the 1024 tier be specified at purchase? Same question for headstage-port licensing.
37. **AIO versus ONE+:** both give 16 animals. AIO adds an integrated 4-channel video processor and a 4-channel optogenetics LED driver. **What exactly is the video processor** — what cameras, what format, and does it hardware-timestamp frames against the neural sample clock? We currently solve video sync with our own camera rig and a TTL pulse train, so if AIO does this natively it could be worth the difference. Price delta?
38. **Can our existing Gen-1 Core be used as a third unit** alongside two ONE+ boxes, adding 8 more animals for 40 total? Or is there a **trade-in or upgrade path**?
39. **Can the purchase be phased** — one ONE+ plus 4 Port Expanders now for 16 animals, the second set later — with no penalty and no compatibility risk between batches?
40. **Formal quote** for the full build (§9 table), delivered to **KAIST, Daejeon, Korea**: unit prices, lead time, shipping, import duty and VAT handling, and whether we buy direct or through a Korean distributor.

---

## 9. THE BUILD — confirm every line on the call

Print this. Fill in the blanks live.

| # | Item | Part number | Qty | Unit | Confirmed? |
|---|---|---|---|---|---|
| 1 | XDAQ ONE+, **1024ch tier** | ONE-R1024-SR64 | **2** | ⏳ | ☐ |
| 2 | 200 W DC power adapter | supplied | 2 | incl | ☐ |
| 3 | Thunderbolt 3 cable | supplied | 2 | incl | ☐ |
| 4 | Port Expander | SAdpt-Port-EXP | **8** | $1,525 (quote 262024) | ☐ |
| 5 | USB-PD adapter for Port Expander | supplied | 8 | incl | ☐ |
| 6 | KonteX HDMI cable, XDAQ → Port Expander | ⏳ | **8** | ⏳ | ☐ length? |
| 7 | EXP → Intan interface adapter | SAdpt-XDAQ-OM12(1)? | **32** | $275 | ☐ **chain confirmed?** |
| 8 | Intan SPI cable, adapter → headstage | Intan C3213 / C3206 | 32 | $415 / $295 | ☐ length? |
| 9 | Commutator | STD or PRO | **32** | ⏳ | ☐ **STD vs PRO?** |
| 10 | Intan RHD2216 headstage | C3313 | **32** | $820 | ☐ we own 8, need ~24 |
| 11 | SyncLink | SyncLink | **0 or 2** | ⏳ | ☐ needed? |
| 12 | DB25 breakout board | ⏳ | 1-2 | ⏳ | ☐ |
| 13 | 4 mm banana ground leads | generic | ~6 | — | ☐ |
| 14 | Acquisition PC | ⏳ | **1 or 2** | ⏳ | ☐ **2× TB3?** |

**Not on this build:** Intan C3442 splitter (cannot exceed the slot ceiling, and it defeats isolation) · Allego/Radiens licence (we are on the Open Ephys GUI).

---

## 10. What we must leave the call with

1. ✅ The **exact EXP → Intan RHD2216 chain**, with part numbers, and confirmation that isolation survives it.
2. ✅ **Cable lengths** for every link, validated against our ~36 cm chamber-top geometry.
3. ✅ A **yes or no on Linux** driver and Open Ephys plugin support.
4. ✅ **One PC or two**, and if one, the exact machine specification.
5. ✅ **SyncLink: needed or not.**
6. ✅ **Commutator STD versus PRO**, with prices and Intan-headstage compatibility.
7. ✅ A **written quote** for the full 32-mouse build, delivered to KAIST.

## 11. Notes to take during the call

*(leave blank, fill live)*

## Related
- ⭐ [[xdaq-32-mouse-wiring-and-channel-law]] · [[2026-07-24-daq-32-mouse-final-comparison]] · [[2026-07-21-kontex-kc-call-prep]] · [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] · [[intan-rhd-spi-wiring-and-headstage-limits]] · [[eeg-60hz-saga]]

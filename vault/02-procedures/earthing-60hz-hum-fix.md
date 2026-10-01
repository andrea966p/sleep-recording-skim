---
tags:
  - procedure
  - grounding
  - earthing
  - eeg
  - signal-quality
  - 60hz
  - radiens
  - allego
  - xdaq
created: 2026-07-13
updated: 2026-07-16
status: RETRACTED-2026-07-16 — wrong device, unvalidated, superseded
---

# Earthing Fix for the 60 Hz Hum (Float-to-Earth)

> [!warning] 🔴 CORRECTION 2026-09-30 — our Gen-1 XDAQ Core DOES have a chassis GND terminal
> Andrea confirmed on the rig on 2026-09-30 that the Gen-1 Core has a chassis GND, and that it is wired to the building earth through the wall socket (continuity tested with a DMM; see [[2026-09-30-xdaq-noise-series]]). Every line on this page saying the Gen-1 has "no Chassis GND" or "no chassis ground terminal" is **wrong**. What the 07-15/16 work MEASURED still stands (foil cut the mains floor; the residual hum tracked electrode impedance). What rested on "there is nothing to wire" does not. Still unverified: whether a separate Sys GND exists on the Gen-1 and how it relates to chassis.

> [!danger] 🛑 RETRACTED 2026-07-16 — READ THIS BEFORE ANY OTHER LINE ON THIS PAGE
> **This page describes a device we do not own.** Our rig is a **Gen-1 XDAQ Core**, which has **NO rear-panel Chassis GND port and NO Sys GND port**. Every instruction below that says "wire Chassis GND → earth" or "bond Chassis GND to Sys GND" refers to the **KonteX CORE2**, a different product. Those steps are **not executable on our hardware** and must not be attempted or cited.
>
> **The "VALIDATED 2026-07-14" claim that used to sit here is also withdrawn.** It rested on a single ~42 s single-electrode clip with no controlled before/after, and the `phys%`-style metrics it quoted are now known to be denominator-confounded (see [[eeg-qc-tooling]] reasoning in [[2026-07-15]]). It was never a validation.
>
> **What actually turned out to be true (2026-07-15 → 16):** earthing was NOT the binding variable. The mains floor was killed by **shielding** ([[headstage-shielding-faraday-foil]]), and the remaining hum is set entirely by **per-electrode contact impedance**. A leg at 0.206 MΩ picks up 80 µV of 60 Hz while its neighbour at 7.641 MΩ — *same mouse, same foil, same headstage* — picks up 4262 µV and rails the amplifier. See [[2026-07-16]].
>
> **Kept for the physics only** (the float/common-mode/imbalance reasoning in §2 is still sound and still useful). **Do not follow the procedure.**

> [!danger] 🔴 CORRECTED 2026-07-14 — earth the XDAQ, NOT the animal
> The first draft of this page (2026-07-13) told me to run a wire from the animal's adapter board `GND` pad to an earthed PC case. That is WRONG and I have replaced it. Both Intan and KonteX (the company that makes our XDAQ) are explicit: the animal must have NO ground path other than the headstage leads, and must not touch external earth or grounded metal. The earth reference belongs at the ACQUISITION SYSTEM (the XDAQ), which reaches Protective Earth through its own AC/DC power adapter. The diagnosis (whole system floating) stays the same, only the injection point for earth changes. See the corrected steps below.

> [!danger] 🔴 This is the leading fix for BOTH multi-day recordings being unusable
> The Jul 10 to Jul 13 2026 run (`allego_0__uid0710-08-53-31`, 72h, 4 mice) and yesterday's Jul 13 to Jul 14 run (`allego_0__uid0713-12-59-49`, 20h, 8 slots) were both unscoreable, every channel swamped by ~60 Hz mains hum at 2 to 5 mV. The hum survives both the 60 Hz notch AND the bipolar subtraction, which means it is partly DIFFERENTIAL, not pure common-mode. Cause: the WHOLE recording system is FLOATING (nothing is tied to earth). This page is how to earth it. Audits in [[2026-07-13]], [[2026-07-14]], and [[60hz-mains-hum-discovery]].

> [!abstract] TL;DR — for non-technical readers (rewritten 2026-07-16)
> **What this is:** the 2026-07-13 theory that our 60 Hz hum came from the whole rig not being connected to the building's earth. The physics write-up is good. The proposed fix was for the wrong machine and the claimed validation did not hold up.
>
> **The idea:** the recording chain touches nothing earthed, so it floats, and the mains field swings the whole thing up and down. Because the two legs of an electrode pair have different contact resistance, part of that common swing turns into real differential hum that no filter can remove. That mechanism is REAL and still explains our data.
>
> **Why the fix failed:** it told us to plug earth into a "Chassis GND port" on the back of the XDAQ. Our Gen-1 XDAQ Core has no such port — that port is on the CORE2, a different product. We also tried the nearest available substitute (an earthed power brick) on 2026-07-15 and it changed nothing.
>
> **What was actually the answer:** the swing gets in through the air, so we blocked it with aluminium foil around the headstages ([[headstage-shielding-faraday-foil]]) — 60 Hz dropped up to 450×. What's left is not an earth problem at all: it's electrodes that never touched brain ([[2026-07-16]]).
>
> **How to read this page:** §2 for the physics. Ignore §3 onward.

---

## 1. Our actual wiring (as of 2026-07-14)

- **One mouse per headstage.** 1 slip ring, 1 mouse, 1 headstage plus its adapter board. NO brass bus.
- **Ground path per mouse:** right parietal / dura ground pin, through the slip ring, straight to the `GND` pad on that mouse's adapter board. Each mouse has its own board `GND`.
- **SPI splitter:** each headstage plugs into an SPI splitter, so 2 headstages (2 mice) share one XDAQ port.
- **XDAQ** = Opal Kelly XEM7310-A75 on the KonteX carrier, USB to the mini-PC (`ASUS NUC14RVH-B`, Ultra 5 125H, external 2-prong DC brick).

Full signal-ground chain for any mouse:

```
mouse ground (dura pin) -> slip ring -> adapter board GND pad
     -> headstage -> SPI splitter -> XDAQ port -> XDAQ system ground -> USB -> mini-PC
```

> [!warning] The animal ground is ALREADY correct — do not add to it
> Dura pin -> slip ring -> board GND -> headstage is the intended and ONLY ground path the animal should have. Do NOT solder a second wire from that board `GND` pad to earth, a PC case, or the rack. That is the mistake the first draft made. A second ground path on the animal is exactly what Intan and KonteX warn against.

## 2. Why the hum is there (root cause) — unchanged, still correct

Nothing in the chain reaches earth. The XDAQ's system ground is supposed to be earth-referenced through its AC/DC adapter, but if that adapter is a 2-prong isolated brick (or the XDAQ is USB-powered only), Sys GND never reaches earth. The mini-PC is a 2-prong brick too. So the entire island (animals, boards, headstages, XDAQ, mini-PC) floats.

A floating system sits in the building's 60 Hz field and bobs up and down at 60 Hz. That is a large COMMON-MODE voltage on every input at once. Bipolar recording rejects most of it, but rejection is imperfect and the two legs of each pair never have equal impedance, so a big common-mode voltage across two unequal impedances is partly converted to real DIFFERENTIAL voltage:

```
differential hum  ~=  common-mode voltage  x  (impedance mismatch / source impedance)
```

That leftover is the 0.5 to 1.9 mV of hum we measured AFTER notch and AFTER bipolar. It is uniform across every mouse and every port, the fingerprint of a SYSTEM-level reference problem, not many bad surgeries.

> [!warning] This is NOT a ground-loop problem
> We have too FEW earth connections (zero effective), not too many. The fix is to ADD exactly one earth reference at the XDAQ. Adding a second earth (e.g. also on the animal) creates a loop and the hum returns.

## 3. ~~Our XDAQ = CORE2, powered by the 2-prong USB-PD brick~~ 🛑 WRONG DEVICE — DO NOT FOLLOW

> [!danger] Everything from here to the end of the page is for a **KonteX CORE2**, not our **Gen-1 XDAQ Core**.
> Our unit has no Chassis GND port and no Sys GND port. There is nothing to wire, nothing to bond, and nothing to star-ground to. Left in place unedited as a record of what we believed on 2026-07-14 and why it was wrong. Retracted 2026-07-16.

### Original text (wrong device, retained for the record)

Our CORE2 is powered by the KonteX USB-C USB-PD brick (2-prong, into the multitap). Per the CORE2 manual, the USB-PD brick is a valid power option and carries NO earth by design. That is exactly why the CORE2 has a dedicated **Chassis GND (Earth GND) port** on the rear panel:

> CORE2 manual — Chassis GND "provides grounding access to the earth ground IF POWERED BY THE USB-PD ADAPTER, or when the AC plug's ground is not truly grounded."
> Sys GND "is referenced (not directly bonded) to Protective Earth via AC/DC adapter." Chassis GND "when bonded to PE (or to system ground at a single point), serves as an RF shield and shunts high-frequency common-mode noise away from the signal path."

So the 2-prong brick being what KonteX ships does NOT mean earthing is unnecessary. It means earth is a SEPARATE wire we add at the rear-panel Chassis GND port. Both **Chassis GND and Sys GND terminals are on the rear panel by the power input.** NO soldering needed anywhere.

### The fix (uses existing rear-panel ports)
1. Run a wire from the CORE2 **Chassis GND** port to a VERIFIED earth (multitap earth, if real — see Step 1).
2. **Bond Chassis GND to Sys GND** at that single point.
3. **Star-ground** the Faraday cage / aluminium rack / slip-ring commutator body to that same Sys GND point.
4. **Animal ground stays only on the headstage.** Keep the animal off all grounded metal (frame, bite bar, cage mesh, heating pad).
5. **Short unused headstage channels to headstage ground.** We have many unused channels, so this matters.

## 4. Steps

### Step 1 — confirm you actually HAVE an earth (multimeter, once)
The multitap is 2-prong-ish with side earth clips. Those only carry earth if the multitap's own plug reaches an earthed wall socket. Continuity / resistance:
- Multitap earth clip -> wall-outlet round earth pin: near 0 Ω = real earth, usable. Open = the multitap earth is fake, get a real earthed socket or ask facilities.
- CORE2 **Sys GND** -> that verified earth: open = floating (expected, this is the bug).
- CORE2 Sys GND -> Chassis GND: tells you if they are already bonded.

### Step 2 — LIVE TEST before making anything permanent
In Allego live view, mouse connected, 60 Hz hum visible:
1. Clip a lead from the CORE2 **Chassis GND port** to the verified earth. NOTE: earth goes on the XDAQ Chassis GND port, NOT on the animal's board GND.
2. Watch the trace.
- Hum **collapses** the instant you touch it -> floating-system diagnosis CONFIRMED, go to Step 3.
- Hum **barely changes** -> it is electrode impedance mismatch, not the system reference. Stop and look at contact quality / impedances ([[signal-quality-and-grounding]]).

### Step 3 — make it permanent
Wire CORE2 Chassis GND -> verified earth with a ring terminal, and bond Chassis GND to Sys GND at that one point (per the CORE2 manual).

### Step 4 — star-ground the rig
From that ONE bonded Sys GND point, run wires to: the Faraday cage / aluminium rack, and the slip-ring / commutator body. Single central point only (star), never a second earth. Once earthed, the rack acts as a partial Faraday shield around the chambers.

### Step 5 — short unused headstage channels to headstage ground
Reduces stray pickup on the many unwired inputs.

## 5. The one rule: single earth point at the XDAQ

Everything earths through ONE point, the bonded XDAQ Sys+Chassis GND. Faraday cage, rack, and commutator all star to it. Do NOT also earth the animal, and do NOT add a second wall-earth elsewhere. Two earth points = a ground loop = the hum comes back a different way.

## 6. Wiring picture

```
mouse gnd (dura) - slip ring -> board GND -> headstage -> SPI splitter -> XDAQ port
                                                                              |
power: 2-prong USB-PD brick (NO earth) --> CORE2                              |
                                                                              |
CORE2 rear panel:  Chassis GND port <--- wire ---> VERIFIED EARTH (multitap earth pin)
                        |
                        +===== bonded at ONE point =====> Sys GND port
                                                            |  star ground
                                        Faraday cage / aluminium rack / commutator body

ANIMAL: grounded ONLY through the headstage. Never wired to earth or grounded metal.
```

## 7. Still open / needs bench test

- HYPOTHESIS until the Step 2 live test (2 minutes, non-destructive). Do it first.
- Confirm the XDAQ power adapter: 2-prong vs 3-prong, and whether Sys GND reads earth. This is the most likely root cause.
- After earthing, re-check with a fresh short recording and re-run `eeg-data-analysis/scripts/multimouse_scan.py`: the 60 Hz PSD peak should drop by orders of magnitude and the post-notch residual should fall well below ~50 µV (physio-band fraction above ~70%).
- If earthing alone is not enough: lower / match electrode impedances, short unused channels, full Faraday enclosure.

## Related
- [[2026-07-14]] — QC of both runs + this correction
- [[2026-07-13]] — original 72h audit
- [[60hz-mains-hum-discovery]] — Korea mains is 60 Hz
- [[signal-quality-and-grounding]] — signal evaluation and older grounding notes
- [[signal-mapping-guide]] — channel map
- KonteX, "Reducing Interference During Electrophysiology Recording Sessions" (Sys GND / Chassis GND bonding, star ground)
- Intan noise reduction techniques (animal grounded only via headstage, short unused channels)

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
updated: 2026-07-14
status: draft-needs-bench-test
---

# Earthing Fix for the 60 Hz Hum (Float-to-Earth)

> [!danger] 🔴 CORRECTED 2026-07-14 — earth the XDAQ, NOT the animal
> The first draft of this page (2026-07-13) told me to run a wire from the animal's adapter board `GND` pad to an earthed PC case. That is WRONG and I have replaced it. Both Intan and KonteX (the company that makes our XDAQ) are explicit: the animal must have NO ground path other than the headstage leads, and must not touch external earth or grounded metal. The earth reference belongs at the ACQUISITION SYSTEM (the XDAQ), which reaches Protective Earth through its own AC/DC power adapter. The diagnosis (whole system floating) stays the same, only the injection point for earth changes. See the corrected steps below.

> [!danger] 🔴 This is the leading fix for BOTH multi-day recordings being unusable
> The Jul 10 to Jul 13 2026 run (`allego_0__uid0710-08-53-31`, 72h, 4 mice) and yesterday's Jul 13 to Jul 14 run (`allego_0__uid0713-12-59-49`, 20h, 8 slots) were both unscoreable, every channel swamped by ~60 Hz mains hum at 2 to 5 mV. The hum survives both the 60 Hz notch AND the bipolar subtraction, which means it is partly DIFFERENTIAL, not pure common-mode. Cause: the WHOLE recording system is FLOATING (nothing is tied to earth). This page is how to earth it. Audits in [[2026-07-13]], [[2026-07-14]], and [[60hz-mains-hum-discovery]].

> [!abstract] TL;DR
> Our recording chain touches nothing connected to the building's ground, so the whole thing floats and the 60 Hz mains field swings it up and down. Because the two legs of each electrode pair have slightly different contact resistance, a fraction of that big common-mode swing turns into real differential hum that no filter can remove. THE FIX: get a true earth reference INTO THE XDAQ, either by powering it from its earthed 3-prong AC/DC adapter or by bonding the XDAQ Sys GND to a real earth point, then bond XDAQ Sys GND to Chassis GND and star-ground the Faraday cage and rig metal to that one point. The animal stays grounded ONLY through the headstage. One earth point only. Test it live before making it permanent.

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

## 3. The fix: earth the XDAQ, star-ground the rig (KonteX method)

The XDAQ has two ground ports:
- **Sys GND** — referenced to Protective Earth via the XDAQ AC/DC adapter.
- **Chassis GND** — the enclosure, acts as RF shield.

KonteX recipe (their own hardware, authoritative):
1. Make sure Sys GND actually reaches earth (power the XDAQ from its earthed 3-prong adapter into an earthed socket, or bond Sys GND to a verified earth point).
2. **Short (bond) Sys GND and Chassis GND** together.
3. **Star-ground** the Faraday cage and the rest of the rig metal (rack, slip-ring / commutator body) to that ONE bonded point.
4. **Animal ground stays only on the headstage.** Keep the animal off all grounded metal (frame, bite bar, cage mesh, heating pad).
5. **Short unused headstage channels to headstage ground** to kill stray pickup. We have many unused channels, so this matters.

## 4. Steps

### Step 0 — check the XDAQ power adapter first (this is probably the whole bug)
Look at the XDAQ's own power adapter.
- Is it a **3-prong** (earthed) AC/DC adapter, plugged into an **earthed** socket? If it is 2-prong, or the XDAQ is USB-powered with no adapter, Sys GND is NOT earthed — that alone explains the float.

### Step 1 — confirm what is and isn't earthed (multimeter, once)
Continuity / resistance:
- XDAQ **Sys GND** to the multitap round earth pin (or a verified earthed metal): near 0 Ω = earthed, open = floating (expected, this is the bug).
- Multitap earth pin to a wall-outlet earth pin: near 0 Ω confirms the multitap earth is real.
- XDAQ Sys GND to Chassis GND: tells you if they are already bonded.

### Step 2 — LIVE TEST before making anything permanent
In Allego live view, mouse connected, 60 Hz hum visible:
1. Clip a lead from **XDAQ Sys GND (or its chassis)** to the multitap earth pin (or earthed metal). NOTE: earth goes on the XDAQ, NOT on the animal's board GND.
2. Watch the trace.
- Hum **collapses** the instant you touch it -> floating-system diagnosis CONFIRMED, go to Step 3.
- Hum **barely changes** -> it is electrode impedance mismatch, not the system reference. Stop and look at contact quality / impedances ([[signal-quality-and-grounding]]).

### Step 3 — make the earth connection permanent
Preferred: power the XDAQ from its earthed 3-prong adapter into an earthed socket so Sys GND is earthed by design. If that is not possible, bond XDAQ Sys GND to a verified earth point with a ring terminal. Then bond Sys GND to Chassis GND per KonteX.

### Step 4 — star-ground the rig
From that ONE bonded XDAQ ground point, run wires to: the Faraday cage / aluminium rack, and the slip-ring / commutator body. Single central point only (star), never a second earth. Once earthed, the rack acts as a partial Faraday shield around the chambers.

### Step 5 — short unused headstage channels to headstage ground
Reduces stray pickup on the many unwired inputs.

## 5. The one rule: single earth point at the XDAQ

Everything earths through ONE point, the bonded XDAQ Sys+Chassis GND. Faraday cage, rack, and commutator all star to it. Do NOT also earth the animal, and do NOT add a second wall-earth elsewhere. Two earth points = a ground loop = the hum comes back a different way.

## 6. Wiring picture

```
mouse gnd (dura) - slip ring -> board GND -> headstage -> SPI splitter -> XDAQ port
                                                                              |
                                    XDAQ Sys GND <---(earth via 3-prong adapter
                                        |               OR bond wire to earth)
                                        +== bonded ==> XDAQ Chassis GND
                                                          |  star ground
                                        Faraday cage / rack / commutator body

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

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
created: 2026-07-13
status: draft-needs-bench-test
---

# Earthing Fix for the 60 Hz Hum (Float-to-Earth)

> [!danger] 🔴 This is the leading fix for the 72h 4-mouse recording being unusable
> The Jul 10 to Jul 13 2026 recording (`allego_0__uid0710-08-53-31`) was byte-perfect as a file but 0 of 4 mice were scoreable, every channel swamped by ~60 Hz mains hum at 2 to 4.5 mV. The hum survived both the 60 Hz notch AND the bipolar subtraction, which means it is partly DIFFERENTIAL, not pure common-mode. The most likely cause is that the WHOLE recording system is FLOATING (nothing is tied to earth). This page is how to earth it. Full audit in the journal and [[60hz-mains-hum-discovery]].

> [!abstract] TL;DR
> Our recording chain touches nothing that is connected to the building's ground, so the whole thing floats and the 60 Hz mains field swings it up and down. Because the two legs of each electrode pair have slightly different contact resistance, a fraction of that big common-mode swing turns into real differential hum that no filter can remove. THE FIX: run ONE thin wire from the adapter board GND to a single earth point (the metal case of an earthed desktop PC is easiest and safest), and bond the aluminium rack to the same point. One earth point only, never two. Test it live before making it permanent.

---

## 1. Our actual wiring (as of 2026-07-13)

This corrects earlier notes that said "two mice into one headstage." Current setup is:

- **One mouse per headstage.** 1 slip ring, 1 mouse, 1 headstage plus its adapter board. NO brass bus anymore.
- **Ground path per mouse:** right parietal ground pin, through the slip ring, straight to the `GND` pad on that mouse's adapter board. Each mouse has its own board `GND`, no shared bus bar.
- **SPI splitter:** each headstage plugs into an SPI splitter, so **2 headstages (2 mice) share one XDAQ port**.
- **Channel map per port:** channels **1, 2, 3, 4 = mouse A**; channels **33, 34, 35, 36 = mouse B** (second headstage sits at native +32). See [[signal-mapping-guide]].

So the full ground chain for any mouse is:

```
mouse ground (right parietal) -> slip ring -> adapter board GND pad
     -> headstage -> SPI splitter -> XDAQ port -> USB -> mini-PC
```

## 2. Why the hum is there (root cause)

Nothing in that chain connects to earth. The mini-PC that anchors the ground almost certainly runs off a 2-prong power brick (no earth pin), and the router, PoE switch, and XDAQ are all 2-prong or USB-powered too. So the entire island (animals, boards, headstages, XDAQ, mini-PC) floats.

A floating system sits in the building's 60 Hz electric field and bobs up and down at 60 Hz. That is a large COMMON-MODE voltage, often volts, on every input at once. Bipolar recording (the `n0 - n1` subtraction) rejects most of it, but the amplifier's rejection is not perfect, and the two legs of each pair never have exactly equal impedance. A big common-mode voltage across two unequal impedances gets partly converted into a real DIFFERENTIAL voltage:

```
differential hum  ~=  common-mode voltage  x  (impedance mismatch / source impedance)
```

That leftover is the 200 to 475 µV of hum we measured AFTER notch and AFTER bipolar subtraction. It is uniform across all 4 mice on all 4 ports, which is the fingerprint of a SYSTEM-level reference problem, not four separate bad surgeries.

> [!warning] This is NOT a ground-loop problem
> An earlier memory note said "hunt a ground loop." That is the OPPOSITE of our situation. We have too FEW earth connections (zero), not too many. The fix is to ADD exactly one earth reference. Adding two would create the loop.

## 3. The fix: give the system ONE earth point

### What "earth" means
The round/earth pin of a wall outlet connects to the building's grounding system and ultimately a rod in the ground. It is a rock-stable 0 V reference. "Earthing" our system means running one thin wire from the board `GND` to that point. The wire carries no power and no normal current, it is only a reference drain, so thin wire is fine.

### Easiest and safest earth point: an earthed desktop PC case
The full desktop PC (3-prong plug, metal case) is already earthed through its own power cord. Its metal chassis IS earth. Use it, so you never touch a mains pin.

## 4. Steps

### Step 1 — confirm the desktop PC is earthed (multimeter, once)
Set a multimeter to continuity / resistance. One probe on a bare screw of the desktop PC metal case, the other on the round earth pin of a wall outlet.
- Near 0 Ω = the case is earthed. Use it.
- Open / high = not earthed, try a different device or use the earth-plug method in Step 5.

Also check the mini-PC case, XDAQ case, and aluminium rack the same way. They will almost certainly read open (floating), which confirms the diagnosis.

### Step 2 — LIVE TEST before making anything permanent
In Allego live view, with a mouse connected and the 60 Hz hum visible:
1. Hold a clip lead from the adapter board `GND` pad to a bare screw on the earthed desktop PC case.
2. Watch the trace.
- If the 60 Hz **collapses** the instant you touch it, the floating-system diagnosis is CONFIRMED. Go to Step 3 and make it permanent.
- If the hum **barely changes**, then it is electrode impedance mismatch, not the system reference. STOP here and look at contact quality / impedances instead (see [[signal-quality-and-grounding]]).

### Step 3 — make the earth connection permanent
Run one wire from a spare adapter board `GND` pad (or piggyback where the slip-ring grounds land) to a metal chassis screw on the earthed desktop PC. Use a ring terminal under a loosened case screw, then retighten.

Because all the mice share the same board `GND` net through the boards and XDAQ, this single wire earths every mouse at once. You do NOT need a separate earth wire per mouse.

### Step 4 — earth the aluminium rack too (bonus shield)
Run a second wire from the SAME earth point (the PC chassis screw) to a bolt on the aluminium rack. Once earthed, the metal rack acts as a partial Faraday shield around the chambers and blocks mains field from reaching the mice. Nearly free, big help.

### Step 5 — ONLY if there is no earthed PC: an earth plug
Make a mains plug wired to ONLY the earth pin, with the live and neutral pins left disconnected. Plug it into any socket, and the wire coming out is earth, clip it to board `GND`.
> [!danger] MAINS SAFETY
> Wire ONLY the EARTH pin. NEVER the live or neutral pin. If you are not 100% certain which pin is earth and confident wiring a plug, do NOT do this, use the PC-chassis method or ask facilities staff to make the earth lead. Connecting live or neutral instead of earth is dangerous and will destroy the headstage.

## 5. The one rule: single earth point

Everything goes to ONE earth point. Board `GND` to PC chassis, and rack to PC chassis. Do NOT also earth to a wall plug at the same time. Two earth points = a ground loop = the hum comes back a different way.

## 6. Wiring picture

```
mouse A gnd (parietal) - slip ring -> board A GND -+
mouse B gnd (parietal) - slip ring -> board B GND -+-> (shared via boards/XDAQ) -> mini-PC
                                                    |
                                                    |  ONE thin earth wire
aluminium rack -----------------------------------> +--> screw on EARTHED desktop PC metal case
                                                            (PC power cord -> wall earth pin -> building ground)
```

## 7. Still open / needs bench test

- The whole thing is a HYPOTHESIS until the Step 2 live test. Do that test first, it is 2 minutes and non-destructive.
- Confirm the mini-PC really is on a 2-prong (unearthed) brick, that is the assumption behind "the system floats."
- After earthing, re-check with a fresh short recording, look at 60 Hz peak power in the PSD (should drop by orders of magnitude) and the post-notch / post-bipolar residual (should fall well below 50 µV).
- If earthing alone is not enough, next levers are lowering / matching electrode impedances and full Faraday enclosure.

## Related
- [[60hz-mains-hum-discovery]] — the original discovery that Korea mains is 60 Hz
- [[signal-quality-and-grounding]] — signal evaluation and the older grounding notes (NOTE: its "two mice per headstage" framing is superseded, we now run one mouse per headstage)
- [[signal-mapping-guide]] — channel map (1-4 mouse A, 33-36 mouse B per port)
- [[allego-settings-save-restore]] — keeping the acquisition config from getting lost

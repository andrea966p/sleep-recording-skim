---
tags:
  - experiment
  - todo
  - eeg
  - 60hz
  - grounding
  - crosstalk
  - signal-quality
  - B1
created: 2026-07-22
status: TO DO — not yet run
priority: high
---

# EXPERIMENT TO DO — ground pad 7 floating input on B1, does the clean-leg 60 Hz floor drop?

> [!warning] STATUS: NOT YET RUN. This is a planned experiment, not a result. Marked as a to do 2026-07-22.

## TL;DR

On our Intan C3322 adapter board (RHD2216), mouse B1's tether has an EMPTY slip ring wire plugged into board **pad 7**, which is a live AMPLIFIER INPUT (single ended input 7, not a ground pad). The far end of that wire is open at the slip ring, so it is a long floating antenna feeding straight into an amplifier input. This is exactly the failure an OpenEphys admin warned about (a floating input becomes an antenna, gets amplified inside the Intan chip, and leaks into the neighbouring channels you actually record).

**Hypothesis:** that floating pad 7 input is lifting the 60 Hz floor on B1's GOOD leg (parietal) via on chip crosstalk. **Test:** ground pad 7, re measure B1 parietal single ended 60 Hz, see if it drops.

## Why B1 is the right mouse to test on

B1 is the perfect test case because it has BOTH the floating pad 7 wire AND the project's single best electrode, and its clean leg sits at a suspiciously high floor:

- B1 parietal = 0.206 MΩ, physiological phase +1.1, the BEST electrode contact this project has ever had (see [[2026-07-16]], [[headstage-shielding-faraday-foil]]).
- Post foil, B1 parietal reads **79 to 80 µV** of 60 Hz. That is the HIGHEST of any good leg on the rig:

| leg | 60 Hz post foil |
|---|---|
| A2 parietal | 12 µV |
| D2 parietal | 46 µV |
| D1 frontal | 89 µV |
| **B1 parietal** | **79 to 80 µV** ← top of the pack, both foil clips |

That extra roughly 40 to 70 µV of floor on the exact mouse that carries the floating pad 7 wire is the FINGERPRINT you would expect from antenna crosstalk. Not proof, other explanations exist (contact variation, 0.206 MΩ is not the lowest Z on the rig), but B1 being the reproducible high floor outlier is consistent with the pad 7 mechanism.

## The board (confirmed from photo, 2026-07-22)

Intan **C3322**, RHD2216 chip, Omnetics 2415 + 2346. Left column of electrode pads runs top to bottom **0, 1, 2, 3, 4, 5, 6, 7**, then a separate **GND** pad below pad 7 (REF is bottom right). The 9 socket header on B1 spans pads 0 to 7 plus GND.

- Pads 0 to 31 = the 32 single ended amplifier inputs (16 bipolar pairs). Pad 7 IS an amplifier input, NOT ground.
- Wiring today: 4 data wires to pads 0, 1, 2, 3 (EEG frontal, EEG parietal, EMG, EMG). Green animal ground to GND pad. A 2 pin connector holds green on GND for rigidity, and its neighbour pin (an OPEN slip ring wire) lands on **pad 7**, floating.

## Procedure

Foil ON. Streaming, not recording (Stream drives no video session). One mouse (B1) is enough.

1. Record a short baseline clip (30 to 60 s) of B1 with the empty wire STILL seated on pad 7. Log single ended 60 Hz on B1 parietal (the good leg) in absolute µV.
2. Ground pad 7. Easiest way that keeps the 2 pin structural anchor: solder bridge / jumper the empty pin to the green (GND) net, so both pins sit on GND. A grounded amplifier input is quiet, this is the admin's "ground the unused inputs at the headstage" done right. (Alternative: just unseat the empty pin so pad 7 is open at the board, but grounding is cleaner and is the real fix.)
3. Record a second short clip, same everything.
4. Compare B1 parietal single ended 60 Hz, before vs after.

## Predicted outcomes

- **Drops from ~80 µV toward ~10 to 40 µV** → pad 7 floating input WAS leaking crosstalk. Confirmed. Then apply the same fix (ground the spare pad 7 wire) on EVERY mouse, and add "no floating wire on an amplifier input pad" to the electrode SOP.
- **Stays ~80 µV** → pad 7 is innocent, B1's floor is set by contact or something else. Cross it off.

Use `state_scan.py` or a single ended 60 Hz decomposition (same method as the 2026-07-16 leg breakdown) for the numbers. Absolute µV per leg, not `60Hz%raw`.

## Honest ceiling, do not expect a rescue

Even if pad 7 grounding works perfectly, it does NOT make B1 scoreable:

- B1 frontal is OPEN (7.641 MΩ, nonphysical phase, surgical / frontal sinus hypothesis) → no working bipolar EEG pair. Fixed only in the next surgical cohort.
- B1 EMG is likely DEAD (floor 28 µV on 07-15, 45 µV on 07-16) → no REM / atonia read.

So this experiment is a MECHANISM check plus clean leg headroom for FUTURE good mice, NOT a way to get data out of B1. The real wall is still open frontal electrodes, next cohort.

## Where this sits in the bigger picture

This is the SECOND term of the council equation `differential_60Hz ≈ common_mode(floor) × electrode_Z_imbalance`, seen from a new angle. Foil already crushed the common mode floor. Pad 7 crosstalk, if real, is a small ADDITIVE contribution on top of the floor, only visible on the legs that are already clean (the dirty legs are dominated by their own open electrode Z and would swamp any crosstalk). That is why B1 parietal (clean) is where you look, not B1 frontal (open, screaming 4262 µV).

## Still open

- **Run it.** Not done yet.
- If it confirms, check the OTHER mice for the same floating pad 7 wire (D1 frontal also reads a high 89 µV, possible second candidate).
- Fold the result into [[allego-electrode-setup-sleep64]] and the wiring SOP.

## Related

- [[2026-07-16]] — the impedance / leg decomposition that found every frontal open and gave the 53× Z to hum proportionality.
- [[headstage-shielding-faraday-foil]] — the foil floor, and the clean leg µV table this experiment builds on.
- [[2026-07-15-earth-and-sleep-council]] — the root cause equation.
- [[signal-mapping-guide]] — pad to native to channel mapping.

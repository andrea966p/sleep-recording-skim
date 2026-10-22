---
name: impedance-negative-electrode-unmeasurable
description: "Only the positive input (inX+) of each bipolar pair has ever been impedance-measured; Open Ephys cannot measure the negative electrode either (XDAQ-OE setZcheckPolarity has 0 call sites). Do not propose switching software; DMM per pad is the fix."
metadata: 
  node_type: memory
  type: project
  originSessionId: 73d8f40f-8fe5-4e49-9c74-3b734c900c35
  modified: 2026-08-03T14:49:57.898Z
---

**2026-08-03:** Radiens exposes no polarity (one `zMag/zPhase` per channel) and the XDAQ-OE v0.4.4 plugin compiles `Rhd2000Registers::setZcheckPolarity` but never calls it (0 call sites, verified in the binary; its own XML export has one magnitude/phase per amp). Both Allego and Open Ephys are blind to the NEGATIVE electrode (a software gap, not a chip limit). Fix hierarchy: (1) DMM each C3410 pad vs the GND pad (free, DC continuity, sees both sides); (2) patch the open-source plugin to run the pass twice; (3) ask Kontex (cheapest supported fix).

Details: [[impedance-sweep-register]] (last section, with the call-site table)

🛑 Do NOT propose switching acquisition software to solve this. Every "EEG impedance" quoted so far is the frontal / `inX+` electrode only.

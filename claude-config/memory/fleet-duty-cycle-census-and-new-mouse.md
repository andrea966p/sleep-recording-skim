---
name: fleet-duty-cycle-census-and-new-mouse
description: "2026-08-06 fleet census: only 1.8 of 8 animals had EEG+EMG connected per sweep; an empty cut tether read 'connected' 22 % of the time at 2 MOhm, hence the 0.5 MOhm criterion; a single low impedance is never evidence of contact."
metadata: 
  node_type: memory
  type: project
  originSessionId: 3430655c-999e-4bb1-abaa-9187f41c99d5
  modified: 2026-08-06T08:08:59.201Z
---

**2026-08-06:** 4 ports + C3442 splitters = 256 ch, 8 animals enumerate cleanly (capacity YES, yield NO: mean 1.80 of 8 animals connected per sweep). The A2 slot held a cut tether attached to nothing and read < 2 MOhm in 22 % of channel-sweeps, so the old 2 MOhm "connected" criterion has a 22 % false-positive rate; teardown ladder showed the false positives come from the amplifier, not our cabling. A mouse implanted 21 Jul and left untethered until 16 d post-op read 40/40 with zero flips on the 19.5 cm soldered + resin tether (n = 1, two variables at once: do not claim either cause). Duty cycle reproduces across days (D2 27.5 % -> 30 %).

Details: [[2026-08-06-fleet-duty-cycle-census]] (teardown: [[2026-08-06-unloaded-chain-interference]]; professor handout [[2026-08-06-rig-status-for-professor]])

🔑 Use |Z| < 0.5 MOhm (control falls to 2.5 %); the real floor control is the unwired inputs in every sweep (08-06 layout `/3`-`/16`, `/35`-`/48`; EXCLUDE `/17`-`/32`, `/49`-`/64`, which are internally tied). 🔴 A single low impedance reading is NOT evidence of contact, ever (the unwired floor reached 0.051 MOhm). Always remap after unplugging a headstage. Never pool single sweeps into a block folder.

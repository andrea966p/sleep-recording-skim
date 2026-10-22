---
name: recording-2026-08-25-24h-zt0-s-sd
description: "2026-08-25 24 h ZT0-to-ZT0 S-SD run: only D2 passes strict rung 2, EEG usability falls 15-34 points in the dark, B slot 1 floating (later a chewed tether). Facts in the vault; 1 h snapshots overstate"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-10-22T00:00:00.000Z
---

`allego_0__uid0825-09-00-00`, 2026-08-25 09:00 to 08-26 09:16, 24.28 h, rung 0 PASS, 726 watchdog checks with zero stalls. D2 (HLBSSD18) is the only strict rung-2 pass; EEG usability collapses in the dark phase (A2 -32, C2 -34 points); A1 has excellent EMG but failing EEG (EMG dark/light 4.29x). B slot 1 read floating after correct seating; the cause was later found to be a chewed tether, not the port.

Details: [[2026-08-25-S-SD-24h-ZT0-run]] · [[b-slot1-was-the-tether-not-the-port]] · [[2026-08-27-B1-swap-baseline-20h-run]]

- 🛑 A 24 h run does NOT give 24 h of scoreable data (loss is biased to the dark phase, where most WAKE lives) and 1 h snapshots badly overstate it (A2/C2 ~100 % at 1 h, 79.5 / 48.8 % at 24 h). Quote the vault note's recomputed figures, not these.
- 🔑 A floating CHIP and an open ELECTRODE look nothing alike: separate them with the chip's own wire-free floor before blaming anything.
- Watchdog pattern worth reusing: check bytes on disk every 120 s and log the write rate as a % of `262*4*fs` (the script lived in a session scratchpad, not the repo).
- 🛑 Still NOT a sleep result — the kappa remains the gate.
- 🛑 A1 has EXCELLENT EMG and failing EEG: do not describe it as a working animal without saying which role. The EMG dark/light ratio (A1 4.29x) is descriptive and NOT a sleep result: the kappa remains the gate.

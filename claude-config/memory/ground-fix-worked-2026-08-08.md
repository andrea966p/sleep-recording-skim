---
name: ground-fix-worked-2026-08-08
description: "2026-08-08 ground re-pin restored EEG on 6 of 7 ECG-cohort mice; A1 left un-grounded stayed flat. The hum criterion is dead (use SLOPE, never for EMG); impedance sweep no longer screens, screen on the stream."
metadata: 
  node_type: memory
  type: project
  originSessionId: ad1ca725-35bc-44d8-b02a-ed707ae385f9
  modified: 2026-08-08T07:21:21.600Z
---

**2026-08-08, pre-registered and controlled:** after the cerebellum ground re-pin nine of 21 new-mouse channels went from slope > -0.35 to steeper than -0.9; usable-by-slope after 5.5 h: B2 57.5 %, C2 71.6 %, D1 70.3 %, D2 63.7 %, control A2 87.8 %; A1 (could not be re-pinned = no-ground control, n = 1) 0.0 % on all three sites; B1 and C1 still fail (ordinary intermittent contact). Impedance got much worse on the repaired mice and did not move on A1 (predictions 1, 3, 5 hit; 2 and 4 failed: longest block 13 min, still no heartbeat). EMG validated on the control only; ECG dead on 7 of 7 against an unwired-floor control and retired 2026-08-11.

Details: [[2026-08-08-ground-fix-post-repin-night]]

🔴 THE HUM CRITERION IS DEAD on this setup (a floating bipolar channel is QUIET: A1 scored 100 % "usable" by it): use SLOPE, and the slope criterion is a CATEGORY ERROR for EMG (broadband). A LOW, STABLE, ZERO-FLIP impedance can mean the animal has NO ground. Now that the ground works the sweep no longer screens: SCREEN ON THE STREAM, NOT THE SWEEP. 🛑 Do NOT loosen the slope threshold to lengthen blocks (circular tuning, banned in `blind-scoring-and-kappa`). Hum- and slope-criterion fractions are NOT comparable. (The original's "dark phase unscored" is stale for EMG.)

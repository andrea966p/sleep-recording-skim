---
name: a2-control-48h-reference-profile
description: "A2 control 48 h run (2026-08-09 to 08-11) is a historical single animal, NOT a standing reference; 47.09/48.19 h usable; method (ZT0 start, EMG state-dependence, threshold sweep) transfers, the animal does not."
metadata: 
  node_type: memory
  type: project
  originSessionId: ad1ca725-35bc-44d8-b02a-ed707ae385f9
  modified: 2026-08-11T00:49:42.389Z
---

🛑 **THAT MOUSE IS GONE. THIS IS A HISTORICAL SINGLE ANIMAL, NOT A STANDING REFERENCE.** Every run has new mice unless the user says otherwise, and a rig position is not an animal ([[cohort-identity-every-run-is-new-mice]]). **Do NOT carry these numbers, or the label "the A2 control", into a later cohort**: judge each file against the wire-free floor inside that same file. What still transfers is the METHOD (ZT0 start, the EMG state-dependence test, the threshold sweep), never the animal.

`allego_0__uid0809-09-00-00`, 2026-08-09 09:00 to 08-11 09:11, 48.19 h, 181.8 GB, intact; 47.09 h usable (97.7 %), zero railed epochs of 17,349; EMG state dependence r(delta, EMG rms) = -0.645; light beats dark at every Otsu threshold (25.5-42.7 pts); replicates cycle 1 vs 2.

Details: [[2026-08-11-a2-control-48h-reference-profile]] (and [[rig-bringup-lessons]] for the no-carry-over rule)

📌 Make a ZT0 start the default for any run over a day (helper `eeg-emg-analysis/qc/start_recording_at.py HH:MM:SS`). 🔴 The absolute asleep-in-light % is threshold-dependent and must NOT be quoted as fact. 🛑 Never pick the threshold row that matches the literature ~70 % (circular, banned in `blind-scoring-and-kappa`).

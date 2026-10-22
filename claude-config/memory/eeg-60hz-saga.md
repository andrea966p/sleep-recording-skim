---
name: eeg-60hz-saga
description: "The 60 Hz / earth / contact investigation, 2026-07-05 to 08-02 (now a dated vault record). Rules kept here: never suggest reseating an electrode, never schedule surgeries, reject clipped epochs, never reuse one animal's threshold."
metadata: 
  node_type: memory
  type: project
  originSessionId: 01d67996-fc6d-445a-b14a-bb600afc0cf8
  modified: 2026-07-22T01:20:41.006Z
---

The full dated record (root-cause equation, foil win, refuted causes, channel-map correction of 2026-08-01, 2026-07-16 retraction, run 1/2 results) is in the vault; it carries a box on what changed afterwards (08-04, 08-05, 08-07/08, 09-30, 10-07).

Details: [[eeg-60hz-saga]]

🛑 **"RESEAT THE HEAD CONNECTOR" IS NOT A THING. NEVER SUGGEST IT.** You CANNOT reseat an implanted electrode or EMG wire. The only animal-side option is to change the tether, which needs ISOFLURANE, stresses the animal and RUINS THE BATCH. Intervention hierarchy: (1) FREE, no animal contact = anything rig-side of the slip ring (swap headstage/port, inspect and resolder C3410 pads, DMM the slip-ring wires, swap boards between animals); (2) EXPENSIVE = change tether, needs a pre-argued reason; (3) IMPOSSIBLE = implanted wires/electrodes. The run-2 "reseat recommended and not done" line in the old record is void.
🛑 "Frontal electrodes are open on every mouse, so make new mice" is NOT supported: DO NOT SCHEDULE SURGERIES on it.
🛑 The 2026-07-15 "first sleep biology" (td_sep -0.65) was a CLIPPING ARTIFACT and is retracted: never verdict a channel before rejecting clipped epochs, and report `keep%` (fraction of clean epochs), not just median rail %.
🛑 NEVER reuse a threshold derived from one animal on another (D2 passed only on C1's hand-picked 25 uV EMG threshold). 🔑 An implausible result is a bug report about your own method: audit the channel map FIRST (the 08-01 breakthrough). The Allego 60 Hz notch is display-only (never reaches .xdat).

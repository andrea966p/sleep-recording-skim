---
name: noise-hunt-verdict-2026-10-06
description: "2026-10-06 verdict: with per-mouse faults set aside, room electrical noise is mostly a ghost. EEG mains outside the 0.5-30 Hz staging band; EMG mains is the only real noise and the validated 60/120 Hz notch removes it (not adopted). Electrician: isolated-earth socket + foil busbar coming; lab moving to E7."
metadata:
  node_type: memory
  type: project
  originSessionId: 4a168599-dde7-46f9-bc71-dedddc8528c6
  modified: 2026-10-06T07:35:45.017Z
---

Andrea asked (2026-10-06): once the per-mouse faults are removed, is the noise hunt chasing a ghost? The per-mouse faults are dura contact,
cement on the pin, misplaced EMG wires, a failing tether and a wrong ground. She worried she was "destroying a whole lab with my directions".
**Answer logged: mostly yes.** The verdict page is vault `10-projects/noise-hunt/2026-10-06-noise-hunt-verdict.md`.
- EEG mains 2-9 µV peak is outside the staging band (`FILT_EEG` = `BAND_TOTAL` = 0.5-30 Hz, NOT 0.5-45; I said 45 once, wrong).
- EMG 60 Hz is the only noise that hurts: A2 13-33 µV, B1 3.6-5.7 µV, a median 68 % of the stage 3 wake measure. The notch is validated:
  44 → 69/100 scoreable, shuffle 0/100, dark>light 47/49. Still NOT adopted: [[emg-mains-corrupts-sleep-staging]].
- Building spikes: the light timer (09-22 lights-ON put EEG up to 1056 µV) plus ~6 unexplained in 24 h. Handled by epoch rejection.
- NOT every EEG recording is clean: before the 08-08 ground re-pin the hum was in mV ([[ground-fix-worked-2026-08-08]]). Never say "all EEG clean".

Electrician visit, same day (noise series Entry 10):
- The rig socket will be replaced with an **isolated-earth socket**. The electricians cut the breaker themselves, which kills e10 and the XDAQ.
  We pay for the part only, and the lab arranges the date.
- The headstage foils go onto **one earth busbar**. Andrea can add or remove each foil herself for A/B/A tests.
- The lab is moving to **E7** (delayed), so he advises spending little here.

**Why:** Andrea's directions steer a lab. The evidence says the remaining environmental noise is cheap to handle in post-processing.
Per-mouse faults (surgery, ground pin, tethers) are what has limited the data.
**How to apply:**
- Do NOT propose new environmental-noise trials or spending: the plan's Phase 2 boxes and Faraday cage, T3, and the electrician's expensive earthing.
- Push the notch decision (pre-register, falsification suite, re-score) and per-mouse reliability.
- Judge each recording by its QC verdict.

Related: [[recording-2026-10-01-noise-4mice-overnight]] · [[xdaq-gen1-has-chassis-gnd]] · [[animal-card-verdict-ladder]]

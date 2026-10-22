---
name: unipolar-run-2026-10-15-ahyeon
description: "ahyeon's 3 unipolar mice (A B C): corrected unipolar map (old 08-05 map was a typo), 10-14 prep and 10-min rehearsal PASSED, 10-15 run LOST to hardware (B off the SPI scan, C reference lost). Detail in the vault"
metadata:
  node_type: memory
  type: project
  originSessionId: d4e35d3a-d8bb-4d52-b115-b0c9c407aedc
  modified: 2026-10-22T00:00:00.000Z
---

Owner `ahyeon` (not Andrea's mice), 3 unipolar RHD2132, one per port A B C, layout `4mice_unipolar_lfp`, `qc: none` (info.json `NOT ASSESSED`). The ONLY correct unipolar map is `/18 emg_l, /19 lfp_tgt, /20 lfp_ref, /21 emg_r, /22 eeg_p, /23 eeg_f` (the 08-05 role names were a typo). The 10-minute scheduled rehearsal (run `901e16ee8bf8`, 10-14) PASSED end to end. The 10-15 run `dca84de0cc7a` (30 h, 09:00 to 10-16 15:00) was LOST to hardware: port B dropped off the SPI scan at 10-14 23:54 and port C lost its reference; the console started without re-checking ports.

Details: [[2026-10-15-unipolar-lfp-run-ahyeon]] · [[_unipolar-lfp-hub]] · [[2026-08-05-unipolar-lfp-mouse-reference]]

- 🛑 Mouse A carries about 3.5-4 mV of 60 Hz on all channels (a known surgical mistake; ahyeon knows): do NOT troubleshoot it.
- 🔴 `AllegoClient.get_signals()` returns the VISUALIZATION-FILTERED stream (a live grab with the 10-300 Hz EMG viz filter looked "awake"): for a live quality check ask whether a Software Stage 2 filter is on, or analyse the recorded file.
- To ask "did the hardware drop?" grep `allegoserver.log` for `Scanned ports` over time. A run snapshots its roles at creation: `./skim pull` + `sudo systemctl restart eeg-recorder` BEFORE creating it.
- Related: [[partial-rig-qc-and-unjudgeable-presets]] · [[grounding-fix-2026-10-07-mains-collapsed]]

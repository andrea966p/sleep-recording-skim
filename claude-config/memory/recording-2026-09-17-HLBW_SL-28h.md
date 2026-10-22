---
name: recording-2026-09-17-HLBW_SL-28h
description: "28 h HLBW_SL run 2026-09-17/18 (ZT0 to ZT4, 8 mice): the unattended workflow ran clean, 7 of 8 rung 2 clean (A1 EEG dead), 3 scoreable, only B2 pairs. Facts in the vault"
metadata:
  node_type: memory
  type: project
---

Console run `6255ffcf2575` (batch `HLBW_SL`), 2026-09-17 09:00 to 09-18 13:00, 28.0 h: stop 5 s late, strip 262 to 16 channels bit-exact on every sample, sha256-verified on the NAS in 13 minutes with the QC bundle, no Mesa crash (the crash risk was knowingly accepted by keeping hardware GL). Rung 2: 7 of 8 clean, A1 EEG dead. Scoreable: B1, B2, D2 (grounded chips); A2, C1, D1 UNJUDGEABLE. Only B2 pairs with the 09-10 baseline, so n = 1.

Details: [[2026-09-17-W-SL-28h-run]] · [[2026-09-18-W-SL-light-phase-sleep]] · [[allego-mesa-gpu-crash-and-log-storm]] · [[animal-card-verdict-ladder]]

- The recorder backend runs at PPID 1 with no systemd unit and `START_GRACE_S = 180`: if it dies the run FAILS rather than starting late.
- Wake 33-42 % over a full cycle is normal; do not compare it with light-phase-only 22-23 %. The vault holds the current D2 figures (the memory's old 0.503 is superseded).

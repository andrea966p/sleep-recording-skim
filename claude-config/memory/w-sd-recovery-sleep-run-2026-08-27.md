---
name: w-sd-recovery-sleep-run-2026-08-27
description: "W-SD recovery sleep, window after the penultimate CSD day (Thu 2026-08-27 13:00 to Fri 09:00): only D2 usable so the paired comparison is n = 1, B1's ground decayed, A1/A2 were a tether fault and recoverable. Detail in the vault"
metadata:
  node_type: memory
  type: project
---

`allego_2__uid0827-12-58-32`, 2026-08-27 12:58 to 08-28 09:05, 20.12 h, rung 0 PASS, protocol STILL running (not a post-protocol endpoint), sampled straight afterwards so it cannot be repeated. Position map = registry XDAQ position (A1 CSD01 ... D2 CSD08). Only D2 is usable (73.0 % both roles, 45 min block), so the paired comparison is n = 1 (baseline had A1, A2, D2). A1/A2 EMG worked all run (dark/light 2.73x) so their EEG loss was a tether/ground fault, not the implant; the re-mate was confirmed on 50 min (`allego_4__uid0828-10-08-34`). B1's ground decayed 825 to 469 uV over 20 h (first recorded decay, a conductor working loose).

Details: [[2026-08-27-W-SD-recovery-sleep]] · [[weak-chip-ground-hides-as-electrode-failure]] · [[w-sd-batch-closeout-2026-08-28]]

- 🔑 To tell "channel died" from "animal left", read the chip FLOOR and the OTHER role, never the channel alone (at minute 50 of `uid0828-10-08-34` both roles on two chips opened AND the floors stepped down: animals unplugged, not a relapse).
- 🛑 Report it as a case, never as a group result.
- 🛑 From an 8-epoch file quote only the lf/hf separation. `allego_5__uid0828-19-10-50` is an EMPTY rig, not ours. C2 enters no result (threshold-fragile); D2 is threshold-proof.
- Longest block 10.7 min in `allego_4__uid0828-10-08-34`: nothing passes rung 2; it is a connection check, not a scoring file.

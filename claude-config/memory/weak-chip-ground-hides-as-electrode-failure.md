---
name: weak-chip-ground-hides-as-electrode-failure
description: "A WEAK (not absent) chip ground reads as a dead electrode: discriminator is the EEG 60 Hz divided by its own chip floor; the 800 uV gate is suspect and the 2000 proposal was falsified 2026-10-01. Detail in the vault"
metadata:
  node_type: memory
  type: project
---

"No EEG" is at least five faults; the one that HIDES is a chip ground that is weak rather than absent. Discriminator: EEG channel 60 Hz divided by ITS OWN chip floor: about 0.03 = proportionally normal (a working and a weak-ground channel look identical), 0.1-0.5 with about 0 % railing = damaged conductor, 1.0 or more = open input. A weak ground scales the WHOLE chip down 3-4x, so real EEG arrives at 50-70 uV and flat. Check order: chip floor 60 Hz, then the ratio, then the EMG on the same position, then |r| between the position's own channels (0.06-0.09 working, 0.5-0.75 shared path), and only then talk about the electrode. Gate replacement is still open.

Details: [[weak-chip-ground-vs-open-electrode]] · [[floor-threshold-fixed-per-chip]] · [[w-sd-recovery-sleep-run-2026-08-27]] · [[recording-2026-10-01-noise-4mice-overnight]]

- 🛑 Do NOT apply the proposed 2000 uV floor gate: falsified 2026-10-01/02 (B2 1820 and B1 742 on the gate's PEAK scale carried working EEG); the floor scale is geometry-dependent, and the 800 gate can err in BOTH directions. Gate reads the 59-61 Hz line PEAK, never band rms (sqrt 2).
- EMG cross-check: EMG working while EEG is flat means implant and cable are fine; the converse is INVALID (a quiet EMG passing the hum criterion may itself be floating). UNJUDGEABLE means "bench connector re-mate", FAIL means "tether change under isoflurane": never call a chip FAIL on a weak ground.

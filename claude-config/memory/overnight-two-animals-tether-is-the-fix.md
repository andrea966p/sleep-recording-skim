---
name: overnight-two-animals-tether-is-the-fix
description: "2026-08-07: a 23.66 h recording gave two working animals (B1, D2); the tether chain, not recovery time, fixed signal quality; arm C 'harm' retracted. Impedance screens, only a multi-hour recording is an outcome"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3430655c-999e-4bb1-abaa-9187f41c99d5
  modified: 2026-10-22T00:00:00.000Z
---

Recording `allego_1__uid0806-16-57-38`, 23.66 h, 2026-08-06/07: B1 and D2 are the first two working animals (B1 one unbroken 23.66 h block, D2 EEG 87.9 % usable). The swap to a soldered, resin-encapsulated tether fixed D2; the earlier "arm C harmed D2" claim is RETRACTED, and the recovery-time confound is resolved (the tether chain, not time).

Details: [[2026-08-07-overnight-recording-two-animals-work]] · [[2026-08-05-tether-comparison]] (retraction in section 14) · [[2026-08-07-rig-specification-and-analysis-method]]

- 🔑 IMPEDANCE BLOCKS SCREEN, ONLY A MULTI-HOUR RECORDING IS AN OUTCOME: state a block's duration next to its duty cycle; never conclude harm or benefit from a block alone (a 21-min block gave p = 8.4e-08 for a backwards conclusion).
- 🛑 Still no surgeries (do not schedule any): the fix is an engineering change on every animal, applicable without new surgery.
- Quote the PIPELINE numbers for scoreability (4 s epochs, inherited gate), not the 10 s floor-derived ones. After any `stage2_split.py` run check `impedance/` (it once copied 44 wrong sweeps). Never sweep from the GUI: use `eeg-emg-analysis/qc/sweep_block_all_ports.py` (the final pre-disconnect sweep of this run was lost).
- Related: [[recording-usable-fraction-analysis]] · [[fleet-duty-cycle-census-and-new-mouse]] · [[tether-soldered-duty-cycle-result]]

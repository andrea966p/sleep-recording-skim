---
name: recording-usable-fraction-analysis
description: "The pre-registered per-mouse data quality analysis of an Allego recording (score each channel against the wire-free amplifier inputs in the same file) and its 2026-08-06 run; method, XDAT layout and result are in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3430655c-999e-4bb1-abaa-9187f41c99d5
  modified: 2026-10-22T00:00:00.000Z
---

Method (pre-registered 2026-08-06): each mouse uses 2 of 16 amp inputs, so `/3`-`/16` and `/35`-`/48` are 112 wire-free floor channels recorded in the same file; threshold = 60 Hz below the 1st percentile of the floor; usable fraction + LONGEST UNBROKEN BLOCK per mouse (the block matters more than the total). XDAT = float32, 262 interleaved channels, already in uV; the hardware band-pass 1.10-475.17 Hz reaches the saved file. The 2026-08-06 interim (1.66 h) found exactly one scoreable mouse; the engine is now `core/criteria.py` via `cards/ladder.py` (the original script was deleted 2026-08-11).

Details: [[2026-08-06-recording-data-quality-preregistration]] · [[2026-08-07-rig-specification-and-analysis-method]] · [[radiens-software-reference]] · [[eeg-analysis-pipeline]] · [[fleet-duty-cycle-census-and-new-mouse]]

- 🛑 NEVER include `/17`-`/32` or `/49`-`/64` in the floor (inactive, internally tied). An empty slot (A2) is a second control: if it scores usable the analysis is broken.
- 🔴 Filtering MANUFACTURES a convincing 69 uV trace from a wire-free input: "the filtered trace looks good" is never evidence of contact; only spectral shape vs the floor survives. Plot traces on one fixed +-400 uV scale.
- Never change the Allego Hardware stage for display (it reaches the file; Data and Visualization stages do not).
- ⚠️ Vault gap: spectral scripts (`qc/spectral_shape_vs_floor.py`) need `~/eeg-analysis-venv/bin/python`; `/opt/neurosurveillance/venv` cannot import scipy (numpy 2 vs scipy built for numpy 1), yet only that venv has `radiens`.

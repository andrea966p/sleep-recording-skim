---
name: partial-rig-qc-and-unjudgeable-presets
description: "Pre-2026-09-13 QC bundles for a partly loaded rig hold fabricated UNKNOWN@slot cards (3 read PASS); unipolar_lfp has no QC verdict by design; a stale VERIFIED upload row skips real files. Detail in the vault"
metadata:
  type: project
---

Found 2026-09-13. QC bundles made BEFORE then for a rig with fewer than 8 mice contain `UNKNOWN@<slot>` cards built from floating inputs; three read PASS at rung 2. Fixed by passing `--positions` from the occupied slots. `unipolar_lfp` has `qc: none` (run records `qc_not_applicable`, not `qc_bundle_skipped`): no wire-free floor exists for its layout.

Details: [[eeg-recording-console]] (sections 2.4-2.5) · [[pipeline-architecture]] · [[skim-nas-smb-and-upload]]

- 🔴 Ignore every `UNKNOWN@` row in an older bundle; never read a card for a slot nobody loaded.
- 🔴 A stale `VERIFIED` row in `eeg-recorder/deploy/uploads.jsonl` makes the uploader SKIP a real file (key = folder/filename + size): every folder it names must exist on the share.
- 🔑 A guard that can never be satisfied is a guard people learn to click past.
- Related: [[cohort-identity-every-run-is-new-mice]] · [[animal-card-verdict-ladder]]

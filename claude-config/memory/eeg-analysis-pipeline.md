---
name: eeg-analysis-pipeline
description: "The canonical 3-stage (+ EDF export) EEG pipeline built 2026-08-03 and its re-derived thresholds; manual now in the vault. Rules: never say 'we deliberately differ from the literature'; r@1min is ours; day-folder date from UTC start_time."
metadata: 
  node_type: memory
  type: project
  originSessionId: 21a6d0c8-6c66-4695-9945-f1f3d834eb58
  modified: 2026-08-03T03:21:40.412Z
---

Built 2026-08-03: stage1 QC -> stage2 per-mouse split (`port{P}-slot{S}_{date}_{time}_{NNhNNm}.npz`, 250 Hz, uV, bipolar) -> stage3 features/hypnogram -> stage4 EDF+ export (physical range pinned to +-6389.56 uV; EDF header fields are 8 ASCII chars); `qc_thresholds.py` is the single source of truth. Thresholds re-derived from 1,137,955 pooled epochs: RAIL 6389.6 uV (16-bit full scale), OPEN 150 uV (bimodal valley 134), `FLAT_UV` 11 / `DEAD_CHANNEL_UV` 20 (old `SHORT_UV` 25 was wrong); sweeps showed the conclusions do not depend on them. Use system `python3`, not the `/opt/neurosurveillance` venv.

Details: [[eeg-pipeline-manual]]; the standard-vs-ours table for the professor is [[analysis-methods-and-justification]]

🛑 FRAMING CORRECTION (Andrea pushed back, was right): we are NOT deviating from the standard method. NEVER say "we deliberately differ from the literature": recording wideband and filtering offline IS standard, our analysis DOES remove 60 Hz (the 0.5-30 Hz band-pass excludes it), line-noise bad-channel rejection is standard. The ONE non-standard piece is `r@1min` persistence, a VALIDITY CHECK, not a scoring rule: label it as ours. ⚠️ Day-folder date comes from the metadata UTC `start_time` converted to KST; the `uidMMDD-HH-MM-SS` token is ALREADY local KST (mixing them shifts every ZT by 9 h). The Allego notch is display-only.

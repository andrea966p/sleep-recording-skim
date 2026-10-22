---
type: reference
area: eeg-analysis
status: superseded
superseded-by: "[[eeg-pipeline-manual]]"
---
# ARCHIVED — pre-sleep64 analysis scripts (retired 2026-07-18)

> [!warning] Updated 2026-10-22: Paths mentioning ~/Monitoring_project are stale: the repo is now ~/sleep-recording-skim. These scripts are in `eeg-emg-analysis/archive/vault-scripts/_archive_pre_sleep64/`, and the `sleep/` half of the July codebase named below was deleted on 2026-08-11. [[2026-08-11-analysis-stack-consolidation]]

These scripts predate the canonical **sleep64 8-headstage** rig and are kept for
reference only. **Do not run them on new recordings.**

They defaulted to the stale `single_mouse` map, `--config 2mice32` now raises
`KeyError`, and `multimouse_scan.py` had four known bugs (hardcoded layout,
denominator-confounded `60Hz%raw`, overlapping-window variance inflation, EMG
never gating the verdict). `eeg_pipeline.py` also collapsed the EMG band to
10–127 Hz by decimating EMG to 256 Hz.

**Current codebase:** `sleep-recording-skim/eeg-emg-analysis/` (QC / convert / sleep,
8-mouse map derived-and-validated from metadata). See its `README.md` and the
checkpoint in `90-archive/2026-07-18-eeg-emg-analysis-checkpoint.md`.

The good parts that carried forward: the XDAT reader (`xdat_io.py`),
`state_scan.py`'s metadata-derived layout + biology tests, and the filter
conventions in `04-processing-guidelines.md`.

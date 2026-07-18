# ARCHIVED — pre-sleep64 analysis scripts (retired 2026-07-18)

These scripts predate the canonical **sleep64 8-headstage** rig and are kept for
reference only. **Do not run them on new recordings.**

They defaulted to the stale `single_mouse` map, `--config 2mice32` now raises
`KeyError`, and `multimouse_scan.py` had four known bugs (hardcoded layout,
denominator-confounded `60Hz%raw`, overlapping-window variance inflation, EMG
never gating the verdict). `eeg_pipeline.py` also collapsed the EMG band to
10–127 Hz by decimating EMG to 256 Hz.

**Current codebase:** `Monitoring_project/eeg-emg-analysis/` (QC / convert / sleep,
8-mouse map derived-and-validated from metadata). See its `README.md` and the
checkpoint in `07-decisions/2026-07-18-eeg-emg-analysis-checkpoint.md`.

The good parts that carried forward: the XDAT reader (`xdat_io.py`),
`state_scan.py`'s metadata-derived layout + biology tests, and the filter
conventions in `04-processing-guidelines.md`.

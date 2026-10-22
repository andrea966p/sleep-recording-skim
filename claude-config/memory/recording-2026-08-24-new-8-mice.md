---
name: recording-2026-08-24-new-8-mice
description: "2026-08-24 one-hour screen of the 8 S-SD mice (first cohort with real ids HLBSSD11-19): only D2 passes strict rung 2; surgical notes do not predict signal; a per-chip floor can be contaminated. Facts in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-10-22T00:00:00.000Z
---

`allego_0__uid0824-17-56-51`, 2026-08-24 17:56-18:56, 1.0 h, rung 0 PASS. Batch S-SD (SOD1 + CSD), real ids HLBSSD11-19 from the registry (manifest `eeg-emg-analysis/cohorts/S-SD.yaml`; HLBSSD17 had no XDAQ position, HLBSSD20 excluded). Only D2 passes the strict gate; A1 and D1 are intermittent contact, B1 and B2 open. B1 was first read as a port fault, then RETRACTED by the 08-26 swap test.

Details: [[2026-08-24-S-SD-first-hour-screen]] · [[b-slot1-was-the-tether-not-the-port]] · [[animal-card-verdict-ladder]] · [[emg-gate-passes-and-floor-bug]]

- 🛑 Surgical bleeding notes do NOT predict signal quality: never triage animals on them. A midway or 1 h reading overstates a flickering channel (A1 98.3 % at 27 min, 35.3 % over the hour): never report it as the outcome.
- 🔑 A chip's own wire-free floor can be contaminated (3 of 8 chips): one quiet-steep site sets the threshold at `FLOOR_PERCENTILE = 1`.
- ⚠️ Vault gap (tooling): in the exported channel table `feat.col(site)` indexes the FEATURE SUBSET, not the 262-channel matrix; use `labels.index(site)` from `C.open_xdat` and check `is_selected`. The registry header is on row 5 and `openpyxl` lives only in `~/eeg-analysis-venv`.
- 🛑 The floor-sensitivity rule (drop floor sites with own median slope < -1.0) is MINE, NOT the project criterion: do not quote it as a headline; it needs writing up and pre-registering before anything goes to the professor. ALWAYS look at the per-10-min time course to separate "intermittent" from "dead" (A1 and D1 are intermittent, B1 and B2 flat zero).

---
name: eeg-analysis-codebase
description: "New clean EEG+EMG analysis codebase (eeg-emg-analysis/), 8-mouse naming, channel enumeration, filter order"
metadata: 
  node_type: memory
  type: project
  originSessionId: 87b56c60-b78e-4a98-83a2-e0bd910a1986
---

**Strong checkpoint 2026-07-18.** New standalone analysis codebase at
`Monitoring_project/eeg-emg-analysis/` (Python-only, VSCode/MATLAB-openable), replacing the
stale vault scripts under `02-procedures/eeg-data-analysis/scripts/` (those archived to
`_archive_pre_sleep64/`). Three modules over a shared `core/`: **qc/** (scorability quick check),
**convert/** (EDF+/.mat/CSV), **sleep/** (features + first-pass NON-validated hypnogram).

**Mouse naming = `M` + port + slot** (user convention): `MA1 MA2 MB1 MB2 MC1 MC2 MD1 MD2`.
Slot 1 = HS-A (`+0`), slot 2 = HS-B (`+32`). Both mice per port ALWAYS present (8 headstages
is the hard invariant). Global base rows `[0,32,64,96,128,160,192,224]`.
Per mouse 4 rows: `+0` EEG frontal-L (red,+), `+1` EEG parietal-L (black,−), `+2` EMG (yellow,+),
`+3` EMG (blue,−). Green = animal ground → GND bus, NOT recorded; REF empty (RHD2216 bipolar).
EEG/EMG differenced OFFLINE.

**Channel map is DERIVED from metadata, never hardcoded:** `sapiens_base` is TOP-LEVEL in the
`.xdat.json` (not under `status`). Per port: `slots = num_channels // 32`, `base =
connection_ntv_idx + 32*slot`. 8-mouse runs = 4 ports × 64ch. Verified files:
`allego_0__uid0713-12-59-49` (8-slot), `allego_0__uid0710-08-53-31` (8 enumerated, ~4 live),
`allego_1__uid0629-12-05-09` (single port D, 32ch).

**Filter/bipolar ORDER (decided):** bipolar difference FIRST → filter → decimate. EEG 0.5–30Hz
Butterworth zero-phase (NO notch, LP<60 already kills mains). EMG 60Hz notch+harmonics THEN
10–100Hz, keep ≥500Hz (do NOT decimate EMG to 256 — old `eeg_pipeline.py` bug collapsed EMG to
10–127Hz). Mains = 60Hz (Korea). QC deliberately UNDER-filters so hum/rail/clip stay visible.

**Fixed old bugs:** stale `single_mouse` default + `2mice32` KeyError; `multimouse_scan.py` 4 bugs
(hardcoded layout, `60Hz%raw` confounded denominator, overlapping windows, EMG never gated).
`state_scan.py` was the good successor (metadata-derived layout, biology tests td_sep/bimod/
persist/circ) — its pattern reused.

Fact-checked vs Iwasaki 2021 (montage, 4s epoch), SPINDLE 2019 (θ6-9/δ0.5-4, θ/δ+EMG RMS),
AccuSleep, IntelliSleepScorer, REST. venv `/home/skimlab/eeg-analysis-venv` (numpy 2.5, scipy 1.18,
pyedflib). Related: [[eeg-60hz-saga]] [[eeg-qc-tooling]].

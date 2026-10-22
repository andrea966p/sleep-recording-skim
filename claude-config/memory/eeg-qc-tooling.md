---
name: eeg-qc-tooling
description: "July 2026 QC tooling lessons (state_scan.py, multimouse_scan.py defects); scripts archived in the vault. Rules: reject clipped epochs before any metric, report keep%, never GetIntanImpedance while streaming."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 01d67996-fc6d-445a-b14a-bb600afc0cf8
---

The July 2026 QC scripts (`state_scan.py`, `multimouse_scan.py`, td_sep, keep% vs median rail %) are archived in `eeg-emg-analysis/archive/vault-scripts/_archive_pre_sleep64/`; their lessons are in the journals of 2026-07-15/16/18 and the earth-and-sleep council.

Details: [[scripts-archive-pre-sleep64-readme]]

🛑 REJECT CLIPPED EPOCHS BEFORE ANY METRIC (a railed amp is non-linear, clipping covaries with EMG and manufactured a fake td_sep that flipped sign from -0.65 to +0.63). ALWAYS report `keep%` (fraction of clean epochs), not just median rail %. `persist` and `bimod` alone are false-positive generators; never verdict on variance. Never use a `phys%` metric whose denominator runs to Nyquist; never concatenate windows then Welch. NEVER call SDK `GetIntanImpedance` while streaming (crashes allegoserver, port 50051 refused): impedance only via the GUI with the stream paused. Allego forgets mode/rate/channel selection on EVERY re-enumeration. Hardcoded 8/4-mouse layouts mis-map slots when a port's channel count varies: derive from `sensors_by_port`. (The original's "scripts in vault 02-procedures", "not under git" and "numpy 1.26, use np.trapz" lines are stale.)

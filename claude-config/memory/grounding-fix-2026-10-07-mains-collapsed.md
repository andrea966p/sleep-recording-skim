---
name: grounding-fix-2026-10-07-mains-collapsed
description: "2026-10-07: isolated-earth socket + XDAQ bonded to the earthed rack collapsed the mains on every channel (floors x12-60, A2 EMG 60 Hz 26-33 -> 1.0-1.4 uV; confirmed over 29.5 h). The 800 uV ground gate now calls EVERY chip UNJUDGEABLE: Andrea's decision pending."
metadata:
  type: project
---

**2026-10-07 (e10 rebooted 14:34 on 7.0.0-28):** the rig wall socket was replaced by an isolated-earth socket and the XDAQ now sits screwed to the earthed top rack shelf (chassis GND wired to it); the two changes landed together and cannot be split. Result on the same 4 mice: chip floors at 60 Hz 700-2900 -> 36-235 uV, EEG 60 Hz ~2 uV, A2 EMG 60 Hz 26-33 -> 1.0-1.4 uV, A2 mains share of the EMG measure 93-97 % -> 12 %. 29.5 h confirmation (10-07/09): hourly hum PASS, A2 scores WITHOUT the notch (r@1min 0.615, was REJECT), light-switch spikes NOT smaller. Open EMGs A1/B2 no longer rail but are still not EMG.

Details: [[2026-09-30-xdaq-noise-series]] (entries 11 and 12; gate review in journal [[2026-10-14]])

🔴 The ground gate `FLOOR_MIN_HUM_UV = 800` (`core/qc_thresholds.py`, still 800 on 2026-10-22) now calls ALL chips UNJUDGEABLE, so any new official QC rejects every mouse at rung 2 until the gate is replaced: raise it before the next real run. Recommended option (c), an era-dated gate (800 before 2026-10-07 14:34, none after, with "ground unverified"), is 🛑 ANDREA'S DECISION, pending. No automatic ground detector is supportable post-fix; the slope-validity gate keeps A1, A2, B2 UNJUDGEABLE (recovering A2 = criterion redesign).
- 2026-10-23, Andrea: replace the 800 µV gate by measuring the current (post-fix) grounds; redesign the −1.90 slope cut. Vault: `_eeg-analysis-hub`.

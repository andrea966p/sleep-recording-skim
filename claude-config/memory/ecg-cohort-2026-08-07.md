---
name: ecg-cohort-2026-08-07
description: "2026-08-07 evening: 7 new EEG+EMG+ECG mice; best-ever impedance but no biology on the live stream (cause found same night: ground on the wrong pin). Radiens set_recording_config() is broken; recording.path lies."
metadata: 
  node_type: memory
  type: project
  originSessionId: a13e9044-6cc6-4f21-b8d5-7413872da116
  modified: 2026-08-07T10:17:39.667Z
---

**2026-08-07:** 7 new mice with 3 bipolar channels each (EEG /1, EMG /2, ECG /3; second mouse per port /33 /34 /35), 22 cm 8-conductor unsoldered tether, cerebellum ground; port A slot 2 = old B1 mouse kept as positive control. 19 of 21 new channels beat the floor by impedance (best the rig had ever looked) yet 22 of 24 live channels were amplifier noise and no ECG had a heartbeat; the "shorted pairs in the 8co tether" hypothesis was WITHDRAWN the same evening (root cause: [[2026-08-07-ecg-cohort-baseline]], ground on the wrong pin). Floor control channels that day: `/4`-`/16` and `/36`-`/48`, never `/17`-`/32` or `/49`-`/64`. Pre-fix recording `allego_0__uid0807-19-14-58`.

Details: [[2026-08-07-ecg-cohort-baseline]]

🔴 Radiens bug: `AllegoClient.set_recording_config()` is BROKEN (`Exception serializing request!`, `recordingType` never set); a failed config silently leaves the old path, and `get_status().recording.path` is USELESS (reports the calling process's cwd): the only proof is to `ls` the destination and watch `_data.xdat` grow. `client.get_signals()` returns ONLY the GUI-selected channels. ⚠️ The 0.5 MOhm criterion is NOT an absolute measure of contact. `radiens` lives only in `/opt/neurosurveillance/venv`.

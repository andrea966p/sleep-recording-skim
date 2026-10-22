---
name: ecg-cohort-ground-miswired
description: "2026-08-07 root cause: the cerebellum ground of the 7 new ECG mice went to the wrong pin (orange instead of brown), leaving every animal floating; explains the hum collapse and the perfect stable impedance; fixed by a connector re-mate, no surgery."
metadata: 
  node_type: memory
  type: project
  originSessionId: a13e9044-6cc6-4f21-b8d5-7413872da116
  modified: 2026-08-07T13:02:29.001Z
---

**Andrea's root cause, 2026-08-07 22:00:** the cerebellum ground was mated to the orange wire (floating at the far end) instead of the brown wire to the headstage GND pad, so all 7 new mice recorded with NO ground (the control, old tether, was untouched). Explains both oddities: no ground = mains is common mode and a bipolar pair REJECTS it, so hum goes DOWN ("lose the ground, get huge hum" is true only for single-ended recording); and the injected impedance current returns through the paired electrode, giving a stable resistive 100-360 kohm. 🔑 Zero flips at 100 % duty is the tell: real failures on this rig are intermittent, wiring errors are not. The phase column of every sweep CSV is useful (resistive ~0/180, electrode ~-20 to -60, capacitive ~-90).

Details: [[2026-08-07-ecg-cohort-baseline]] (ground section); the fix night is [[2026-08-08-ground-fix-post-repin-night]]

🛑 The fix needs NO anaesthesia (connector re-mate, not the implanted electrode); the earlier "short in the tether" and "fluid under the cement" ideas were WITHDRAWN: do NOT schedule an isoflurane episode to move a mouse to an old tether. A continuity beeper fires only below ~30-50 ohm, so a tens-of-kohm leak is silent on a DMM.

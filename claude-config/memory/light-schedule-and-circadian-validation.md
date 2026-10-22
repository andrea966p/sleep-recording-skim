---
name: light-schedule-and-circadian-validation
description: "Animal room light cycle 09:00 ON / 21:00 OFF KST (ZT0 = 09:00); xdat.json start_time is UTC while the uid filename token is local KST. REM is not reliably separable: never report a REM share."
metadata: 
  node_type: memory
  type: project
  originSessionId: 21a6d0c8-6c66-4695-9945-f1f3d834eb58
  modified: 2026-08-03T01:42:13.415Z
---

**Lights ON 09:00, OFF 21:00 KST (12:12 LD), ZT0 = 09:00** (recorded 2026-08-03; `LIGHTS_ON_HOUR = 9` in `core/qc_thresholds.py`). Literature norm (C57BL/6): ~70 % asleep in the light phase. First circadian check of C1 (07-31): asleep-in-light 66.9 % (C2 52.5 %, D2 41.0 %, D1 4.9 % = first-tethering recording, entirely in the light phase).

Details: [[production-values]] (schedule); the C1 table is in [[2026-08-03-two-8-mouse-runs]]; the UTC/KST warning and the no-REM rule are in [[analysis-methods-and-justification]]

⚠️ Allego `start_time` in `*.xdat.json` is UTC; the `uidMMDD-HH-MM-SS` filename token is ALREADY local KST: converting only one shifts every ZT by 9 h and files the recording under the wrong day. 🔴 REM IS NOT RELIABLY SEPARABLE with this montage (the p80 rule forces 20 % of sleep, Otsu gives 24-48 %, literature < 10 %): STOP REPORTING IT, report WAKE vs NREM and REM-entry-from-NREM (> 70 %) only.

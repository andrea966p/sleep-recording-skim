---
name: nanotag-sod1-hlbnsl
description: "Nanotag SOD1 studies (no EEG): HLBNSL merged 2026-10-05, NS-SD/NW-SD re-planned 2026-10-19/21. Facts in the vault; keeps the mouse-ID, .nta-mtime and weekend rules"
metadata:
  node_type: memory
  type: project
  originSessionId: e2600516-6345-49e5-8408-ebb49c468481
  modified: 2026-10-22T00:00:00.000Z
---

Nanotag (Kissei VSMN 210, 12 s activity, no EEG, workstation only) is now THE sleep readout of the HLB SOD1 project. HLBNSL (NS-SL vs NW-SL, sampled 2026-10-02) was merged Run 1 + Run 2 on 2026-10-05: no detectable SOD1 sleep effect. NS-SD / NW-SD (HLBNSSD51-55 vs HLBNWSD56-60) was re-planned 2026-10-19/21: baseline 10-22 to 10-24, SOD from 10-24 (12 d), one read 10-30, SD Mon 11-02 to Thu 11-05, sampling Thu 11-05.

Details: [[2026-10-19-NS-SD-NW-SD-nanotag-study]] (NS-SD) · [[2026-09-14-HLBNSL-nanotag-SOD1-sleep]] and [[2026-10-05-HLBNSL-nanotag-merged-analysis]] (HLBNSL) · [[_nanotag-hub]].

- 🔴 Mouse = header tag ID (Run 2 files are all named `HLBNSSL_<n>`, water mice too). `.nta` mtime = SAVE time, 30-80 min after the read: never use it as read time. Get windows from the sheet's NANOTAG behavioral tab, never from the data.
- 🛑 Andrea does NO SD or behavioural tests at weekends (why sampling moved from Sun 11-08 to Thu 11-05). 12 s activity-only = 9 days (the English manual's 20 is a misprint). SD hours are analysed, not excluded.
- Off-site copies of the nanotag raw data exist (Andrea, 2026-10-23). Re-run the Run-2-withheld regression after any loader change.
- Related: [[backup-architecture-three-destinations]]

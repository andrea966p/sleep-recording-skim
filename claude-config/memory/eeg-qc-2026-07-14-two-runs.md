---
name: eeg-qc-2026-07-14-two-runs
description: "2026-07-14 QC of the 72h run and yesterday's 8-headstage run — both unusable, same 60Hz floating hum; multimouse_scan.py tool"
metadata: 
  node_type: memory
  type: project
  originSessionId: b09f2ba3-d823-4258-b11c-cbced541c54f
---

> **STALE (2026-10-22), DELETION PROPOSED.** The last paragraph ("VALIDATED same day, fix CONFIRMED") was withdrawn: it rested on one ~42 s single-electrode clip, not a controlled before/after ([[2026-07-15-earth-and-sleep-council]], [[earthing-60hz-hum-fix]] retracted entirely as the wrong device; vault contradiction RB-3). The facts and the `multimouse_scan.py` tool are in journal [[2026-07-14]]; the tool's defects are in [[scripts-archive-pre-sleep64-readme]]. "Which mouse = which cable" is UNANSWERABLE from that data.

Post-processed two recordings on 2026-07-14. Both UNUSABLE, NOT scoreable, same floating-ground 60 Hz disease as the [[eeg-72h-4mouse-2026-07-10]] audit. Earthing fix STILL not applied before either run.

**Files** (both 1000 S/s, 262 sig = 256 pri (4 ports×64) + aux/din/dout):
- `allego_0__uid0710-08-53-31` = the 72h run (72.22h, Fri Jul10 → Mon Jul13). 4 mice, one per port: rows A=0-3, B=64-67, C=128-131, D=192-195.
- `allego_0__uid0713-12-59-49` = yesterday (20.05h, Mon Jul13 13:00 → Tue Jul14 09:02). 8 slots armed, only 4 mice physically connected. Port A={0-3,32-35} B={64-67,96-99} C={128-131,160-163} D={192-195,224-227}. Slot = native+0 EEG_F, +1 EEG_P, +2 EMG_L, +3 EMG_R.

**Result:** every channel 60Hz-dominated (53-88% raw power). After comb-notch, residual EEG still 0.5-1.9 mV (clean mouse EEG cleaned = <300µV), physio-band fraction only 4-31% (want >70%). Hum partly DIFFERENTIAL → bipolar+notch can't rescue. Faint sleep/wake structure survives on 72h slots B(strong)/A(weak), and yesterday's B1/B2/D1 → those electrodes DO make real contact, just buried.

**"Which mouse = which cable" (8-headstage): UNANSWERABLE from data.** Because system floats, OPEN unconnected inputs hum just as loud (2-5mV) as connected electrodes → no signature separates them. Must trace cables physically. Soft ranking by surviving structure: B1,B2,D1 > A1,D2 > A2,C1,C2 (DO NOT trust as animal map).

**Metadata trick:** channel layout / which slots armed comes straight from `.xdat.json` → `sapiens_base.biointerface_map` (chan_type='ai0', port, ntv_chan_idx, sys_chan_idx==data-row, is_selected). No guessing the map.

**New tool:** `02-procedures/eeg-data-analysis/scripts/multimouse_scan.py` — memmap-based (files too big for 30GB RAM: 272GB/75GB), scans ALL mouse-slots across huge multi-headstage files, comb-notches 60Hz+harmonics, classifies DEAD/HUM/MARGINAL/USABLE, emits per-slot overview PNG (PSD + theta/delta over time + EMG). Layouts `four` and `eight`. Use this instead of `qc_report.py` for multi-headstage or oversized files (qc_report loads whole file → OOM, assumes single_mouse map).

Report: vault `04-journal/2026-07/2026-07-14.md`. PNGs: `02-procedures/attachments/qc-2026-07-14/`. **Blocker: apply + live-test earthing fix (`20-areas/eeg-rig/earthing-60hz-hum-fix.md`) before ANY next recording.**

**FIX CORRECTED same day (2026-07-14):** earth the XDAQ, NOT the animal. My board-GND→PC-case advice was WRONG. Per Intan + KonteX (XDAQ maker): animal grounded ONLY via headstage leads, never to external earth/grounded metal. Earth enters at XDAQ Sys GND (via its own 3-prong AC/DC adapter → Protective Earth); bond Sys GND↔Chassis GND; star-ground Faraday cage/rack/commutator to that one point; short unused headstage chans to headstage GND. Likely root cause = XDAQ on 2-prong isolated brick or USB-only → Sys GND never earthed. Mini-PC (ASUS NUC14RVH-B, 2-prong) irrelevant to earth path. Live-test = clip XDAQ Sys GND to earth, watch hum collapse.

**✅ VALIDATED same day ~17:00:** electrician bonded dedicated wall earth conductor → CORE2 Chassis GND (permanent). Port-A clip `allego_0__uid0714-16-58-16` mouse rows 32-35: 60Hz 88%→**11.8%**, resid 1-2mV→**135µV**, phys→**97%** = clean scoreable. Fix CONFIRMED. NEW limiting factor = per-electrode contact (flips clean→open in minutes; check raw EEG_F vs EEG_P RMS asymmetry to find bad leg; reseat + impedance 0.1-1MΩ).

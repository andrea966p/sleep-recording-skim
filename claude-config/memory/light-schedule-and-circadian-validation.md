---
name: light-schedule-and-circadian-validation
description: "Animal room light cycle (09:00-21:00 KST, ZT0=09:00) and the threshold-independent circadian validation of C1 against published mouse norms"
metadata: 
  node_type: memory
  type: project
  originSessionId: 21a6d0c8-6c66-4695-9945-f1f3d834eb58
  modified: 2026-08-03T01:42:13.415Z
---

🔑 **ANIMAL ROOM LIGHT CYCLE (recorded 2026-08-03): lights ON 09:00, OFF 21:00
KST. 12:12 LD. ZT0 = 09:00 KST.** Light phase = 09:00-21:00. Was blank in the
vault from 2026-08-01 to 2026-08-03. In `00-config/production-values.md` and
`pipeline/qc_thresholds.py`.

⚠️ **Allego `start_time` in `*.xdat.json` is UTC; the `uidMMDD-HH-MM-SS`
filename token is ALREADY LOCAL KST.** Converting one and not the other shifts
every ZT by 9 h and files the recording under the wrong day.

⭐⭐ **THIS GAVE THE FIRST THRESHOLD-INDEPENDENT VALIDATION OF C1.** Nothing in
the QC gate or the persistence statistic knows about the clock, so the circadian
check is external evidence.

| animal | light-phase wake | dark-phase wake | asleep in light |
| --- | --- | --- | --- |
| **C1 (07-31)** | 33.1% | 82.2% | **66.9%** |
| C2 (07-31) | 47.5% | 99.3% | 52.5% |
| D2 (07-31) | 59.0% | 83.9% | 41.0% (outside normal) |
| D1 (06-29) | 95.1% | n/a | **4.9%** (wildly outside) |

**LITERATURE NORM (C57BL/6): ~70% asleep in the LIGHT phase, NREM 62.0 ± 7.8
%/12 h. REM is <10% of total sleep.** C1 lands within 1 SD, with the light/dark
contrast in the correct direction. Three independent lines (persistence,
physiology, circadian) rank the animals identically: C1 strong, C2 real, D2 fails.

✅ **06-29/D1 EXPLAINED.** That recording sits entirely in the LIGHT phase
(ZT9.1-13.6), when a mouse should be ~70% asleep; it was 95% awake on
technically flawless data (9 µV hum, 100% gate pass). Not an artefact — an
animal that was not sleeping. Consistent with first-tethering acclimatisation.

🔴 **REM IS NOT RELIABLY SEPARABLE with this montage — STOP REPORTING IT.** The
80th-percentile rule forces REM to 20% of sleep; an independent Otsu cut on
theta/delta gives 24-48%; literature is <10%. Both land far above, so neither is
a measurement. Report **WAKE vs NREM** and REM's **ORDER** (entered from NREM,
expect >70%) only. See [[eeg-analysis-pipeline]], [[eeg-60hz-saga]].

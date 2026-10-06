---
name: nanotag-sod1-hlbnsl
description: "Second experiment type since 2026-09: Kissei nanotag implants (activity/temp, no EEG) for HLB SOD1; HLBNSL batch merged Run1+Run2 2026-10-05; code in repo nanotag/, data on SKIM NAS andrea/HLBN*"
metadata:
  node_type: memory
  type: project
  originSessionId: e2600516-6345-49e5-8408-ebb49c468481
  modified: 2026-10-05T10:47:59.949Z
---

The HLB SOD1 project also runs **nanotag** studies (Kissei VSMN 210 implant: 12 s activity cross counts + 5 min tag temperature, read by NFC on a Windows PC with the viewer dongle). There is no EEG and no rig involvement: everything runs on the SKIM workstation.

- **HLBNSL** = NS-SL (SOD1 6.8 U/mL in water: HLBNSSL41, 42, 43†, 44, 49) vs NW-SL (water: HLBNWSL45-48, 50). Sampled 2026-10-02. 43 died 2026-09-28 in restraint for the tag read; all its data discarded. 49 and 50 have a 1-day baseline, left out of the baseline.
- **2026-10-05:** Run 2 is MERGED with Run 1 (reversing the 09-28 "Run 2 discarded"), cutting the logged windows (whole room, rounded out to the hour; 10-02 cut from 14:00). Result: no detectable SOD1 sleep effect. Handling and test days raise dark sleep ~10 pts in both groups. RA change p = 0.029 = hypothesis only.
- 🔴 Run 2 files are ALL named `HLBNSSL_<n>`, water mice too ⇒ the mouse comes from the header tag ID (`TAG` in cohort.py). 🔴 `.nta` file mtime = save time, 30-80 min after the read: never use it as the read time. 🔴 The tags log post-mortem; `Out of range` temperature then follows.
- Code: repo `nanotag/analysis/` (cohort.py, nta_qc.py, export_nas.py; Desktop path symlinked) and `nanotag/report/build.sh` (docx/pptx from the HTML). Raw data: `~/Desktop/Andrea/nanotag/nanotag recording data/HLBNSL/`. NAS: `02_Data_Sleep/andrea/HLBNSSL|HLBNWSL/<Baseline|Treatment>/`, `HLBNSL_nanotag_ANALYSIS_2026-10-05/`, `nanotag-pilot/`. ⚠️ There is no off-site copy of the nanotag raw data.
- Vault: `05-experiments/active/2026-09-14-HLBNSL-nanotag-SOD1-sleep.md`, `02-procedures/nanotag-recording-and-analysis.md`, `06-references/nanotag-kissei-device-and-literature.md`. Sheet edits for Run 2 are OPEN: `05-experiments/active/2026-10-05-HLBNSL-sheet-handover-run2.md`.
- Next batch NS-SD / NW-SD (HLBNSSD51-55, HLBNWSD56-60): surgery 2026-10-12, recording 10-22, sampling 11-06. It needs new FOLDERS/TAG/EXCLUDE blocks in cohort.py.

- **Project context (2026-10-06):** `vault/05-experiments/_HLB-SOD1-project-hub.md`. HLB-sponsored, PI Kim Jakyung. Oral microbial SOD (6.8 U/mL → 20.4 U/day) vs chronic sleep restriction; aims = oxidative stress, sleep, cognition. EEG/EMG (4 batches, Aug–Sep) failed through constant troubleshooting ⇒ **nanotag is now THE sleep readout** (no NREM/REM). Drive folder `1gwRlmVI0ieCXaXBpRGf6c_mjXsCFgR0n`. 🔴 For NS-SD: recommend activity-only tags (one 20-day run, no read during SD week); SD hours must be analysed, not excluded.

**Why:** the work lived only on one Desktop until 2026-10-05, and the cohort facts that change results (tag IDs, windows, the merge decision) are easy to lose.
**How to apply:** for any nanotag question, start from the study page. Get windows from the sheet's NANOTAG behavioral tab, never from the data. Re-run the Run-2-withheld regression after any loader change. Related: [[skim-nas-per-mouse-csv-layout]], [[backup-architecture-three-destinations]].

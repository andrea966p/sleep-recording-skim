---
name: skim-nas-per-mouse-csv-layout
description: Since 2026-09-29 the recorder exports one CSV per mouse to 02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSEID>_<B|R>/; rebuild of old data and service restart pending
metadata:
  node_type: memory
  type: project
  originSessionId: 533bb1b2-75c7-42ef-bdb1-704e3dd70a51
  modified: 2026-09-29T04:58:45.886Z
---

Andrea asked (2026-09-29) for the SKIM NAS to be organised BY MOUSE: `02_Data_Sleep/<user>/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSEID>_<B|R>/` holding `<same>.csv` + `<same>.info.json`. The analysis reads the CSV, never the xdat. Types are only basal→B/Baseline and recovery→R/Recovery. `sd` was dropped because the batch id carries it. A batch name is now REQUIRED.

CSV columns follow Diane's reference `.mat` (`03_Data_Mouse/diane/20260816_H5A251F0209_A01__BSR.mat`): `timestamp_raw,timestamp_sec,datetime_kst,EEG,EMG`.
- `timestamp_raw` is Allego's device counter, not zero-based.
- `timestamp_sec` is 0-based.
- Values are µV, 3 decimals.
- Size is about 4.8 GB per mouse per 24 h.

The chain is QC → STRIP → EXPORT (`eeg-emg-analysis/export/per_mouse_csv.py`) → UPLOAD. After every CSV of a run verifies, the local CSVs are deleted.

Decided 2026-09-29, rebuild only:
- Each canonical CSV is TRIMMED. Baseline runs 09:00→09:00 (24 h). SL recovery runs 09:00→09:00. SD recovery runs 13:00→09:00 (20 h, because both SD recoveries stopped at 09:05).
- Folders are dated by the window start, so the W-SD baseline is `20260820_…_B`.
- S-SD B1 is unpaired: HLBSSD13 has a baseline only, HLBSSD17 a recovery only. Both go up flagged. S-SD n=7 paired; the other batches n=8.
- The S-SD Registry positions were confirmed by Andrea: the failed tether was C1.

**Why:** people could not tell run folders apart (`BSR` vs `BSR-2`). The W-SD split came from the 08-19 B1 tether chew and restart; the second S-SD folder is the 08-26 B1-swap re-record.

**State 2026-09-30:**
- ✅ Rebuild DONE: 64 mouse folders, 291 GB. An independent info.json audit was clean.
- ✅ The window re-check is done. Cards are in `eeg-emg-analysis/cards/out-windows/`; results in vault `05-experiments/completed/2026-09-30-scoreable-mice-on-the-24h-windows.md`.
- Scoreable at both timepoints: **HLBWSD08, HLBWSL24, HLBSSL33**. HLBSSL31 and HLBSSL35 are scoreable at stage 3 only, because their recovery rung 2 is UNJUDGEABLE (contaminated floor). HLBWSL23 is borderline (baseline r 0.289). S-SD: none.
- ⚠️ Stage 3 and the ladder must run under `/usr/bin/python3`: the recorder venv's NumPy 2 breaks the system SciPy.

**How to apply:**
- Done 2026-09-30:
  - console restarted, and it writes to `02_Data_Sleep`;
  - `03_Data_Mouse/andrea` emptied by Andrea;
  - every info.json carries `qc`, the ladder verdict vs the chip's wire-free floor, via `backend/qc_info.py`. `pairing.scoreable_at_both` is set in each.
- Still pending:
  1. a 2-minute real UI run with headstages connected;
  2. nothing committed yet, so `./skim push`.
- Related: [[backup-architecture-three-destinations]], [[skim-nas-smb-and-channel-stripper]], [[contaminated-floor-rejects-good-eeg]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- ✅🔴⭐⭐⭐ **[SKIM NAS = ONE CSV PER MOUSE in 02_Data_Sleep, 24 h WINDOWS — 2026-09-30](skim-nas-per-mouse-csv-layout.md). NEWEST.** Rebuild DONE, 64 folders verified. Scoreable at both timepoints: **HLBWSD08, HLBWSL24, HLBSSL33** (+31, 35 stage 3 only); S-SD none. info.json carries the `qc` verdict (the CSV has no wire-free floor). ⏳ A real UI test run and the commit are pending.

---
name: sleepstager-csv-reader-branch
description: "State of our SleepStager changes (branch csv-reader, PR #1 and PR #2 to somnocode open since 2026-10-08, local-only tone row and rules card) and the open decisions; detail in the vault backlog"
metadata:
  type: project
---

SleepStager is a nested git repo `~/sleep-recording-skim/SleepStager` (in the workspace `.gitignore`, NOT synced by `./skim`, needs its own push). Branch `csv-reader` (commit 7feb666, rig CSV reader, no-move for rig folders, `split_xdat`, display notch `n` cycling off/50/60 Hz) is PR #1 to `somnocode/SleepStager`; the resume-marks fix is PR #2. LOCAL ONLY, kept out of both PRs: the dossier "tone (spike-proof)" row, the "scoring rules" card, `scripts/eval/compare_csv_mat.py` (backup `~/sleep-data/sleepstager-local-changes.patch`, copy in `vault/_attachments/`). Open: the EMG notch is 50 Hz but Korean mains is 60 Hz (the professor decides), and `batch_stage.py` does not find CSVs.

Details: [[sleepstager-changes-and-backlog]] · [[scoring-working-method]] · [[sleep-scoring-vault-pages]]

- 🛑 Never push to `main` of `somnocode/SleepStager` (unprotected, Andrea has write access): push only the branch, the professor merges. Run all 3 smoke tests before committing under `sleepstager/` (on this machine use a copy of `~/Desktop/Andrea/200221_FSIK14SL0701_B_11.3eg` with the mouse name swapped into temp script copies).
- Rules card must fit Andrea's window (2334x1362): 338 px available, card needs 320 (about 16 px a line); measure offscreen before adding lines. Refresh both patch copies after local edits.

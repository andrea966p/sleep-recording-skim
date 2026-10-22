---
name: sleepstager-csv-reader-branch
description: State of our SleepStager changes (branch csv-reader, PR #1 to somnocode open since 2026-10-08) and the open decisions
metadata:
  type: project
---
SleepStager (nested git repo ~/sleep-recording-skim/SleepStager, NOT synced by ./skim) has branch `csv-reader` with UNCOMMITTED
changes on the SKIM workstation (2026-10-07): rig CSV reader (read_rig_csv), no-move for rig folders, split_xdat for stripped xdat,
dossier "tone (spike-proof)" row, "● not saved" header marker, pyarrow dependency. Installed in ~/.venvs/sleepstager (uv, py3.11).
Verified: HLBSSL33 R CSV vs xdat-split .mat identical (21,600/21,600 stages), re-run 2026-10-08; CSV route SETTLED, the .mat and local xdat copy deleted (xdat still on e10 ~/radix).

2026-10-08: `n` display notch now cycles off/50/60 Hz (Andrea OK, goes in PR). The dossier "tone (spike-proof)" row is LOCAL ONLY:
keep it in the working tree, exclude it from the PR (viewer.py: _pfmt emg_tone_med, _DOSSIER_ROWS row, footer _ec/_cut text).
Upstream origin/main gained a35945f CLAUDE.md: run all 3 smoke tests before committing sleepstager/; on this machine use a copy of
~/Desktop/Andrea/200221_FSIK14SL0701_B_11.3eg with the mouse name sed-swapped into temp script copies (_raw_smoke has 3 data-specific
FAILs, identical on unmodified code).
2026-10-08: committed 7feb666 (rebased on origin/main a35945f), pushed, PR https://github.com/somnocode/SleepStager/pull/1 opened
on Andrea's go. Tone row (uncommitted) and scripts/eval/compare_csv_mat.py (untracked) stay local, out of the PR (backup now in sleepstager-local-changes.patch). main is UNPROTECTED
and Andrea has write access: never push to main, only the branch; the professor merges.
2026-10-08 later: fixed resume bug in _maybe_resume (cleared rule marks came back; save now replaces marks on epochs it covers). Bug is in main (not CSV); sent as PR #2 (branch fix-resume-marks off origin/main). Locally still uncommitted on csv-reader with the tone row.
2026-10-08: LOCAL-ONLY "scoring rules" card (_RulesCard in viewer.py, under the feature sliders) mirrors handbook §3-§4; keep both in
sync. All local changes (tone row, resume fix, card) backed up in ~/sleep-data/sleepstager-local-changes.patch (regenerate after edits).
Open: (1) EMG notch is 50 Hz but Korean mains is 60 Hz (60 Hz = 18 % NREM EMG power in HLBSSL33 R) - professor decides before more
mice are scored; (2) batch_stage.py does not find CSVs yet; (3) PR #1 waits for the professor's review.
Andrea's HLBSSL33 R pass: HLBSSL33_R_AN_261007-2034, last epoch 8441 (2026-10-08 evening; save lives only on the workstation, not in any repo).
2026-10-08: SleepStager/ added to the workspace .gitignore (./skim push does `git add -A`, which would have embedded the nested repo).
Patch copy for other machines: vault/_attachments/sleepstager-local-changes.patch (against csv-reader 7feb666); refresh both copies after local edits.
Rules card must fit Andrea's window 2334x1362: 338 px available, card needs 320 (each line ~16 px); measure offscreen before adding lines. Details: vault 01-infrastructure/sleepstager/sleepstager-changes-and-backlog.md.
Related: [[sleep-scoring-vault-pages]].

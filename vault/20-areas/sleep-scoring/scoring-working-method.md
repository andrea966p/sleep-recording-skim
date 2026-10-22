---
type: reference
area: sleep-scoring
status: active
created: 2026-10-22
tags: [reference, sleep-scoring, sleepstager, working-method]
---

# How we work on manual sleep scoring: roles, local copies, conventions, the SleepStager repo

> [!abstract] TL;DR
> Andrea scores mouse sleep by hand in the professor's program (SleepStager) and wants to become very good at it.
> Every scoring question is also a question for the professor. This page holds the working rules that grew out of
> the first scoring sessions (2026-10-07, 2026-10-08) and that were, until 2026-10-22, held only in Claude's memory.
> The how-to is [[sleepstager-user-guide]]; the knowledge is [[sleep-scoring-handbook]].

## 1. Roles

- **Andrea** (git `andrea966p`) is a PhD student on the HLB SOD1 sleep project. On 2026-10-07 the goal was stated as
  "to become very good at sleep scoring" ([[2026-10-07]]). She scores HLB mice by hand and sends screenshots of hard epochs.
- **The professor** owns SleepStager and the scoring conventions. Every scoring question is also a question for the
  professor, who explains the lab's conventions; the running list is handbook §8 ([[sleep-scoring-handbook]]).
- **Claude** explains a call epoch by epoch with the dossier numbers (EMG, spike-proof tone, δ, θ/δ, σ, γ) against the
  mouse's own W / NR / R medians, and prefers at-a-glance tables.

## 2. Logging a case

For each hard epoch, write into that day's journal (not into a chat): the screenshot, the question, the reading, the
call, and the question for the professor. Examples: [[2026-10-07]] (nine cases), [[2026-10-08]] (cases 1008, 1314-1326,
2240 / 2002 / 2137, the REM-onset lag). The recurring patterns go to the handbook's case library (§5).

## 3. Andrea's own conventions

Andrea defines her own conventions from her calls (stated 2026-10-08, carried over from Claude memory; the rules themselves are in handbook §4). After a session:

1. read the save and compare her final stages with what the rule suggested;
2. write the rule she actually applied into handbook §4, marked "decided by Andrea" (C3, C11, C12 are marked "decided by Andrea");
3. point out inconsistencies between her own calls instead of silently choosing one. Open example from 2026-10-08:
   epoch 1317 is NR but epoch 2971 is W, with the same pattern (tone just under the cut, EEG awake): either 2971 is NR
   under C12 or C12 needs a δ threshold ([[2026-10-08]]).

All conventions stay drafts until the professor confirms them.

## 4. Local copies, never the NAS

Recordings are copied from `/mnt/skimnas/02_Data_Sleep/...` to `~/sleep-data/<batch>/<Baseline|Recovery>/<YYYYMMDD>_<MOUSE>_<B|R>/`
and staged there; the NAS is storage only (Andrea, 2026-10-07).

- **Why:** SleepStager writes its outputs beside a recording (and used to move loose files), and the NAS CSV is the
  declared single source of truth; working on it risks the canonical tree ([[2026-10-06-sleepstager-csv-ingestion]]).
- **How:** copy, compare the CSV's sha256 with `upload.sha256_remote` in the `info.json`, then work locally
  ([[sleepstager-user-guide#Where the files are]]). 🛑 Never open or stage a file straight from `/mnt/skimnas`.
- **Not decided yet:** where finished scorings (the `4-sec sleepstager/` save folder) go back on the NAS. Until then
  the save exists only on the machine that scored it (for HLBSSL33 R: the SKIM workstation, [[2026-10-08]]).

## 5. The SleepStager repository

- It is a separate git repo inside the workspace (`SleepStager/`, remote `somnocode/SleepStager`), ignored by `./skim`
  since 2026-10-08, so it has its own `git push` ([[sleepstager-changes-and-backlog]]).
- `main` there has no branch protection and Andrea has write access, so a direct push would skip the professor's review.
  🛑 **Never push to `main`; push only a branch and open a PR. The professor merges** ([[2026-10-08]]).
- Before committing under `sleepstager/` run all three smoke tests; on the workstation use a copy of a `.3eg`
  (`200221_FSIK14SL0701_B_11.3eg`) with the mouse name swapped into temporary copies of the scripts. `_raw_smoke.py`
  shows 3 FAILs that are identical on the unmodified code ([[2026-10-08]]).
- Local-only changes (tone row, rules card, `scripts/eval/compare_csv_mat.py`) stay out of the PRs; the patch that
  carries them between machines is `sleepstager-local-changes.patch` ([[sleepstager-changes-and-backlog]]).

---
type: hub
area: sleep-scoring
status: active
created: 2026-10-22
summary: "Manual mouse sleep scoring: the handbook and conventions, the SleepStager program and our changes to it, the CSV reader, blind scoring and kappa"
tags: [hub, sleep-scoring, sleepstager]
---

# Sleep scoring

## What this is

How we stage mouse sleep by hand and defend each call: the handbook of states, measures and draft conventions, the
SleepStager program (the professor's, with our CSV reader and fixes), and the plan to measure agreement with a human (kappa).
Andrea is learning to score; every scoring question is also a question for the professor.
The rig's CSV, the analysis and the verdict ladder live in [[_eeg-analysis-hub]]; the nanotag method in [[_nanotag-hub]].

## Current state

- 2026-10-23: Andrea: the SleepStager 60 Hz notch is our own modification and needs no professor approval; C12 (one-sided arousal in NREM) is still undecided. [[2026-10-23]]
- 2026-10-22: PR #1 (CSV reader, display notch 50/60 Hz, unsaved marker) and PR #2 (resume fix) on `somnocode/SleepStager` are both still open and unmerged; read-only GitHub check on 2026-10-22, both last updated 2026-10-08. [[sleepstager-changes-and-backlog]]
- 2026-10-08: HLBSSL33 Recovery scored to epoch 8441 of 21,600 (235 epochs re-staged); conventions C11 and C12 drafted, and 1317 (NR) vs 2971 (W) is an unsettled inconsistency. [[sleep-scoring-handbook]]
- 2026-10-08: CSV reading was declared settled (21,600 of 21,600 stages identical to the `.mat` route); the display notch now cycles off, 50 Hz, 60 Hz, while the feature notch is still 50 Hz. [[2026-10-06-sleepstager-csv-ingestion]]
- 2026-10-07: First scoring session (HLBSSL33 R, epochs 1-840); SleepStager opens the rig's per-mouse CSV from this day. [[sleepstager-user-guide]]
- 2026-08-08: The blind-scoring packs for kappa were built; no later entry records any epoch scored, so no human-scored kappa exists. [[blind-scoring-and-kappa]]

## Start here

1. [[sleep-scoring-handbook]]: states, measures, units, draft conventions C1-C12, case library, literature, questions for the professor
2. [[sleepstager-user-guide]]: open, save, keys, how to read the rule's marks
3. [[sleepstager-changes-and-backlog]]: every change we made to SleepStager, the PRs, the backlog
4. [[scoring-working-method]]: roles, logging cases, local copies, the repo rules
5. [[blind-scoring-and-kappa]]: the agreement test and what its result will mean (also [[2026-10-06-sleepstager-csv-ingestion]], [[sleepyscore-japan-scoring-tool-algorithm]])

## Rules that must not be broken

- 🛑 Work on local copies under `~/sleep-data`; never open or stage a recording straight from the NAS. [[sleepstager-user-guide#Where the files are]]
- 🛑 Never push to `main` of `somnocode/SleepStager`; push a branch and open a PR, the professor merges. [[scoring-working-method]]
- Our scoring conventions are drafts until the professor confirms them. [[sleep-scoring-handbook]]
- Scoring questions go to the professor; log each hard case in that day's journal. [[scoring-working-method]]
- Never choose a threshold by what raises agreement with the human scorer (circular tuning). [[blind-scoring-and-kappa]]

## Open items

- Professor to review and merge PR #1 and PR #2. [[sleepstager-changes-and-backlog]]
- ✅ 2026-10-23: the 60 Hz mains notch is our own modification of our SleepStager fork; it does not need the professor's approval (Andrea). Epochs up to 8441 of HLBSSL33 R were scored with 50 Hz. [[sleepstager-changes-and-backlog]] [[2026-10-23]]
- Continue HLBSSL33 R from epoch 8441 (check 763 first) and settle 1317 vs 2971 (C12; Andrea not sure yet, 2026-10-23). [[2026-10-08]]
- The running list of questions for the professor (handbook §8). [[sleep-scoring-handbook]]
- Blind-score a pack and compute kappa. [[blind-scoring-and-kappa]]
- Decide where finished scorings go back on the NAS. [[scoring-working-method]]

## Everything here

![[area.base]]

# Contradictions: scoring-nanotag (2026-10-22)

Found while rebuilding `20-areas/sleep-scoring` and `20-areas/nanotag`. Settled = decided from primary evidence or a later dated entry; open = needs a person. No record note was reworded.

| id | claim A (note) | claim B (note) | evidence checked | proposed resolution | needs-Andrea? |
|---|---|---|---|---|---|
| SC-1 | [[sleepstager-changes-and-backlog]] (tip box): `git apply ../vault/01-infrastructure/sleepstager/sleepstager-local-changes.patch` | The patch is at `vault/_attachments/sleepstager-local-changes.patch`; `01-infrastructure/` no longer exists | `find vault -name "*.patch"`, 2026-10-22 | SETTLED: pre-rehaul path. Command in the backlog note (a reference) corrected to the `_attachments` path | no |
| SC-2 | Old vault index and the Claude memory file sleepstager-csv-reader-branch: the `csv-reader` changes are "uncommitted" | [[sleepstager-changes-and-backlog]] and journal [[2026-10-08]]: commit 7feb666 pushed, PR #1 open; PR #2 open | GitHub API (read-only), 2026-10-22: both PRs `state: open`, `merged: false`, last updated 2026-10-08 | SETTLED: the index and the memory opening line are stale; hub states the PRs as open. Memory file should lose the "UNCOMMITTED" sentence | no |
| SC-3 | [[_hlb-sod1-hub]] and [[hlb-sod1-design]]: "First mouse: HLBSSL33 Recovery, epochs 1-840 scored ([[2026-10-07]])" | [[2026-10-08]]: the same mouse was scored to epoch 8441 (235 epochs re-staged) | Both journals; handbook header says epochs 840-8441 | SETTLED: the hlb-sod1 line is a dated statement of 2026-10-07 that is now incomplete. Not edited (other folder); owner of hlb-sod1 may add "to 8441 on 2026-10-08" | no |
| SC-4 | [[sleep-scoring-handbook]] C12 (as written): one-sided arousals inside NREM stay NR | Same note, open note on C12 and [[2026-10-08]]: epoch 2971 was scored W with the same pattern as 1317 (NR) | Handbook table row C12, journal 2026-10-08 tasks | OPEN: Andrea settles one way, or C12 gets a δ threshold; then the professor confirms | yes |
| SC-5 | [[sleepstager-changes-and-backlog]], backlog 1: the feature notch is 50 Hz, the mains is 60 Hz; "decide before scoring more mice" | Scoring continued on 2026-10-08 (epochs 840-8441) with the 50 Hz feature notch; no entry records the professor's decision | Journal 2026-10-08, backlog | OPEN: the professor decides; epochs scored before the decision used 50 Hz features | yes (ask the professor) |
| SC-6 | [[nanotag-recording-and-analysis]] TL;DR: NS-SD / NW-SD "surgery 2026-10-12", reuse of the workflow | [[2026-10-19-NS-SD-NW-SD-nanotag-study]]: schedule re-planned 2026-10-19 (single housing 10-19, tag Run 1 10-22, sampling 11-05) | Both notes; the surgery date is the same, only the later schedule changed | SETTLED: no conflict on the surgery date; the procedure carries no schedule. Schedule lives in the study note | no |
| SC-7 | [[nanotag-recording-and-analysis]]: "no off-site copy yet" for nanotag raw data (2026-10-05) | [[backup-architecture]] lists no nanotag row; S3 holds `radix/` only | Both notes; no later entry about a nanotag copy | OPEN, low stakes: confirm nanotag raw has still no off-site copy; hub lists it as an open item | yes |

## Andrea's answers, 2026-10-23

Settled unless marked still open. [[2026-10-23]]

- **SC-4**: Not sure yet: stays open.
- **SC-5**: The 60 Hz mains notch is our own modification of the fork; no professor approval needed.
- **SC-7**: Off-site copies of the nanotag raw data exist.

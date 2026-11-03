# Vault log

Append-only. One entry per vault-wide change. Newest at the bottom.

## [2026-10-22] rehaul | area/project skeleton

- Folders by area/project instead of document type: `10-projects/`, `20-areas/`,
  `30-resources/`, `90-archive/`, flat `_attachments/`, `00-inbox/`. Journal unchanged.
- Type and status moved into frontmatter (schema in [[CLAUDE]]). Hubs per area/project.
- 892 path links rewritten to note names before any move; Obsidian's own link graph was
  compared before and after every step (tools/vault/compare_dumps.py).
- Front door [[HOME]] replaces `_INDEX.md` (now in `90-archive/`).
- Map of every move: `_meta/move-map.tsv`.

## [2026-10-22] rehaul | hubs, truth pass, memory, audits

- 14 hubs written by one agent per area; dated banners on outdated notes; per-area
  contradiction logs in `_meta/contradictions/`.
- Claude memory archived verbatim (`90-archive/claude-memory-2026-10-22/`), then reduced to
  rules and pointers; 37 links to memory slugs repointed (`retarget-memory-links-2026-10-22.tsv`).
- Independent audits: hub claims 174/204 supported, 30 corrected; records 0 changed beyond
  added callouts; promoted notes' dropped facts restored. Usability test from HOME: 7/7.
- Open questions: [[decisions-needed-2026-10-22]].

## [2026-10-23] cleanup | stale memory deleted, journal index archived

- Six stale memory files deleted (copies in `90-archive/claude-memory-2026-10-22/`); MEMORY.md
  says so in its last section.
- `04-journal/_JOURNAL-INDEX.md` moved to `90-archive/`; [[journal.base]] is the journal index.

## [2026-11-03] add | HLB EEG re-score section

- New folder `10-projects/hlb-sod1/eeg-sleep/`: [[hlb-eeg-sleep-overview]] (results, every mouse), [[hlb-eeg-scoring-method-2026-11]], [[hlb-eeg-data-backbone]], [[hlb-eeg-compute-runbook]], and `mice/` with one note per mouse (33, `hlb-eeg-<mouse>`).
- Dated callouts on [[2026-09-30-scoreable-mice-on-the-24h-windows]] and [[2026-10-06-SOD1-sleep-EEG-2x2-quick-compute]]; pointer bullets in [[_eeg-analysis-hub]] and [[_sleep-scoring-hub]].
- Figures `_attachments/2026-11-03-hlb-eeg-*` (5 cohort figures, 64 per-window overviews).

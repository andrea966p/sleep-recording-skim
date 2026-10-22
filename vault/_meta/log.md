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

# _meta — records about the vault itself

| File | What |
|---|---|
| `log.md` | append-only log of vault-wide changes (restructures, renames, rules) |
| `move-map.tsv` | the 2026-10-22 rehaul: every pre-rehaul path and where it went (reviewed, approved) |
| `move-map-P6.tsv` | hub renames made during the rehaul |
| `move-map-summary.md` | the move map as the readable page approved on 2026-10-22 |
| `relink-repairs-P3b.tsv` | links that were broken before the rehaul and were repaired |
| `contradictions/<key>.md` | per area or project: disagreements between notes, how each was settled or why it needs Andrea |
| `memory-promotion/<key>.tsv` | which Claude memory file went to which vault note (2026-10-22) |
| `path-map-2026-10-22.tsv` | every pre-rehaul path and where it is now |
| `retarget-memory-links-2026-10-22.tsv` | memory-slug links repointed to vault notes |
| `lint-allow.tsv` | broken links that are deliberately kept (one per line: source, link) |

The scripts that use these live in `tools/vault/` (repo root). `./skim lint` is the
health check.

# _meta — records about the vault itself

| File | What |
|---|---|
| `log.md` | append-only log of vault-wide changes (restructures, renames, rules) |
| `move-map.tsv` | the 2026-10-22 rehaul: every pre-rehaul path and where it went (reviewed, approved) |
| `move-map-P6.tsv` | hub renames made during the rehaul |
| `move-map-summary.md` | the move map as the readable page approved on 2026-10-22 |
| `relink-repairs-P3b.tsv` | links that were broken before the rehaul and were repaired |
| `contradictions.md` | disagreements between notes, how each was settled or why it needs Andrea |
| `lint-allow.tsv` | broken links that are deliberately kept (one per line: source, link) |

The scripts that use these live in `tools/vault/` (repo root). `./skim lint` is the
health check.

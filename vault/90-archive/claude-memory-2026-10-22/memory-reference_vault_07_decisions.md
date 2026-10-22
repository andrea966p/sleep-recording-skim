---
name: reference-vault-07-decisions
description: "Vault filing rule: 07-decisions/ is for CHOICES ONLY (councils, sprint plans, ADRs) — trimmed 26→9 on 2026-08-03; results/literature/procedures/symptoms each have their own section"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1229f108-e030-412f-9fe5-4c65bfe6feea
  modified: 2026-08-03T09:43:11.829Z
---

The vault (`sleep-recording-skim/vault/`) gained a `07-decisions/` top-level section on 2026-05-28. It holds long-lived strategic artifacts so they stop rotting inside daily journals and become citable.

Current contents:
- `07-decisions/2026-05-01-llm-council-review.md` — full LLM council output (5 advisor responses, 5 peer reviews, chairman synthesis, staged plan, status appendix). Extracted from `04-journal/2026-05/2026-05-01.md`.
- `07-decisions/2026-05-stabilization-sprint-week-1-plan.md` — Phase 0-6 plan + **live status snapshot table** (the table that gets edited every time a sprint item ships). Extracted from `04-journal/2026-05/2026-05-20.md`.

**Rule.** When the user asks "what was the council verdict" / "what's left from the sprint" / "what shipped this week", the answer is in `07-decisions/`, not scattered across `04-journal/`. Daily journals link forward to these; decision docs link back. New strategic content (future council reviews, new sprint plans, ADRs) goes here — not in dailies.

⭐ **FILING RULE, enforced 2026-08-03 (user asked for it: "in decisions I think we have a bit too much").** `07-decisions/` had drifted to 26 files, most not decisions. Trimmed to **9**. A doc belongs there ONLY if it records **a choice between options**. Otherwise:

| doc is… | goes in |
|---|---|
| choice between options, council, sprint plan | `07-decisions/` |
| a run, audit, result, data report | `05-experiments/completed/` |
| literature, vendor/product comparison, spec, glossary | `06-references/` |
| steps someone follows | `02-procedures/` |
| symptom + fix | `03-troubleshooting/symptoms/` |
| a dated failure that happened | `03-troubleshooting/incidents/` |
| vendor emails, call prep, quotes | `01-infrastructure/vendor-correspondence/` |
| done, no longer followed | `99-archive/` |

**"It is important" is NOT a reason to file under `07-decisions/`** — add an `_INDEX.md` line instead; that is what makes a doc findable. Rule is also written into vault `CLAUDE.md`. Renames from that pass: `2026-08-03-analysis-methods-procedure` → `02-procedures/eeg-data-analysis/analysis-methods-and-justification`, `2026-08-03-literature-check-impedance-and-electrode-failure` → `06-references/electrode-failure-and-impedance-literature`, the two `daq-*` docs → `06-references/` (dates dropped). See [[eeg-analysis-pipeline]].

Related convention also added 2026-05-28: every daily journal in `04-journal/` has a `created: YYYY-MM-DD` frontmatter field matching its filename date. This stabilizes the sort-by-created-property view in Obsidian (filesystem ctime drifts every time an old daily gets edited). The `_templates/Daily Journal.md` template was updated to include the field for future entries.

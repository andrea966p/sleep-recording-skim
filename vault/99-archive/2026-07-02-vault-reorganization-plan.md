---
tags:
  - decision
  - plan
  - vault-maintenance
created: 2026-07-02
status: awaiting-approval
audience: team
---

# Vault Reorganization Plan (Tier 1 + 2) — 2026-07-02

> [!warning] Status: AWAITING APPROVAL — nothing has been moved yet.
> This is the written plan only (user asked to plan first, not execute). Every file move and every reference update is listed below so it can be reviewed before anything changes. **No file is deleted; misfiled content is moved, not removed.** Execute only after sign-off.

## Why

Two folders drifted out of purpose (survey 2026-07-02):
- `02-procedures/` top level = 18 loose files, ~12 of them EEG/rig acquisition docs mixed with video/general docs → hard to scan.
- `06-references/` holds an 8-file lab-meeting/presentation set + a progress-meeting + a misfiled troubleshooting doc → references should be reference material only.
- `02-procedures/emergency/` is an empty dead folder.
- `radiens.log` (runtime log, not a note) sits in the vault root.

## Link-safety principle (why this is low-risk)

Obsidian `[[wikilinks]]` resolve by **filename**, not path — so moving a file to another folder (keeping its name) does **not** break the 248 bare-wikilink references found. Only **path-qualified** references break:
- path-qualified wikilinks: `[[06-references/progress-meeting-2026-03-12|…]]`
- markdown/text path refs: `02-procedures/signal-mapping-guide.md`

Those are individually listed in the "References to update" tables below and are the complete set (grep-verified across the vault + the external `~/.claude` memory). **No filename is renamed** (renaming would break wikilinks) — files only change folder.

Rollback: vault is Syncthing-synced + NAS-backed nightly (00:00); all moves are reversible by moving back.

---

## TIER 1 — safest (misc/misfiled out of references)

### 1a. Remove empty folder
- `02-procedures/emergency/` — empty, delete the folder. (No files, no refs.)

### 1b. New folder `08-meetings/` — move the meeting/presentation set out of `06-references/`
| From (`06-references/`) | To (`08-meetings/`) | Tool |
|---|---|---|
| lab-meeting-2026-04-10-final-script.md | 08-meetings/ | move_note |
| lab-meeting-2026-04-10-presentation-brief.md | 08-meetings/ | move_note |
| lab-meeting-2026-04-10-presentation-plan.md | 08-meetings/ | move_note |
| lab-meeting-2026-04-10-presentation-revisions.md | 08-meetings/ | move_note |
| lab-meeting-2026-04-10-speaker-notes.md | 08-meetings/ | move_note |
| lab-meeting-2026-04-10-presentation.html | 08-meetings/ | **move_file** (non-note) |
| lab-meeting-2026-04-10-presentation.pptx | 08-meetings/ | **move_file** (non-note) |
| progress-meeting-2026-03-12.md | 08-meetings/ | move_note |

### 1c. Move misfiled troubleshooting doc
| From | To | Tool |
|---|---|---|
| 06-references/storage-troubleshooting.md | 03-troubleshooting/storage-troubleshooting.md | move_note |

### Tier 1 — references to update (path-qualified only; all else is by-name and safe)
| File : line | Current ref | Change to |
|---|---|---|
| 07-decisions/2026-05-stabilization-sprint-week-1-plan.md : 85 | `06-references/storage-troubleshooting.md` | `03-troubleshooting/storage-troubleshooting.md` (or bare `[[storage-troubleshooting]]`) |
| 04-journal/2026-05/2026-05-21.md : 63 | `06-references/storage-troubleshooting` | `[[storage-troubleshooting]]` (bare) |
| 03-troubleshooting/emergency-runbook.md : 25 | `06-references/storage-troubleshooting` | `[[storage-troubleshooting]]` (bare) |
| 01-infrastructure/hardware-sync/literature-review.md : 167 | `[[06-references/progress-meeting-2026-03-12\|…]]` | `[[progress-meeting-2026-03-12\|…]]` (bare) |
| 06-references/lab-meeting-2026-04-10-presentation-plan.md : 103,126,193,205 | `06-references/progress-meeting-2026-03-12.md` | `08-meetings/progress-meeting-2026-03-12.md` (moves with it) |
| 06-references/lab-meeting-2026-04-10-presentation-brief.md : 561,852,853 | `06-references/progress-meeting-2026-03-12.md` / `06-references/lab-meeting-2026-04-10*` | `08-meetings/…` (all move together) |

> [!note] Simplest robust rule for Tier 1: rewrite every affected ref as a **bare `[[wikilink]]`** (drop the folder prefix). Bare wikilinks never break again on future moves. Only keep explicit paths where the doc is deliberately quoting a filesystem path.

### Tier 1 — external memory (`~/.claude`, edited outside the vault)
| File : line | Ref | Action |
|---|---|---|
| memory/project_phase_4_complete.md : 15 | `storage-troubleshooting` (bare mention) | update prose location note (optional; not a link) |

---

## TIER 2 — declutter `02-procedures/` (EEG acquisition docs → subfolder)

### 2a. New folder `02-procedures/eeg-recording/` — move the 12 acquisition/rig docs
(Leaves at `02-procedures/` top: `camera-roi-framing`, `session-recording-workflow`, `new-researcher-onboarding`, `bus-factor-runbook`, `hardware-sync-setup`, `hardware-sync-bench-test-do03`. Keeps the existing sibling `02-procedures/eeg-data-analysis/` = offline analysis, distinct from acquisition.)

| Move to `02-procedures/eeg-recording/` |
|---|
| allego-monitor-guide.md |
| allego-presets-workspace.md |
| allego-sampling-rate.md |
| eeg-emg-data-guide.md |
| first-headstage-connection.md |
| grounding-reference-noise-concepts.md |
| intan-headstage-troubleshooting.md |
| multimeter-guide.md |
| rig-assembly-guide.md |
| signal-mapping-guide.md |
| signal-quality-and-grounding.md |
| sleep-recording-operator-manual.md |

All via `move_note` (all are notes).

### Tier 2 — references to update (path-qualified only)
| File : line(s) | Current ref | Change to |
|---|---|---|
| `_INDEX.md` : 45, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58 | `02-procedures/<doc>` (12 links in the operator-docs section) | `02-procedures/eeg-recording/<doc>` — or bare `[[<doc>]]` |
| `_INDEX.md` : 168 | `02-procedures/sleep-recording-operator-manual`, `02-procedures/first-headstage-connection` | `02-procedures/eeg-recording/…` or bare wikilinks |

(No other in-vault path-qualified refs to these 12 exist — the remaining ~240 references are bare `[[wikilinks]]` and survive automatically.)

### Tier 2 — external references to update (outside the vault)
| File : line | Ref | Change to |
|---|---|---|
| `~/.claude/.../memory/MEMORY.md` : (Vault Key Files) | `02-procedures/signal-mapping-guide.md`, `02-procedures/signal-quality-and-grounding.md` | `02-procedures/eeg-recording/…` |
| `~/.claude/.../memory/project_first_headstage_bringup.md` : 18 | `02-procedures/first-headstage-connection.md` | `02-procedures/eeg-recording/first-headstage-connection.md` |
| Vault `CLAUDE.md` / `AI-INSTRUCTIONS.md` | none found referencing these by path (grep-clean) | — |

> [!important] The `06-references/radiens-software-reference.md` and `06-references/tsukuba-sleep-recording-method.md` stay in `06-references` (they ARE reference material). Vault `CLAUDE.md` §"Critical Files" references golden configs / production-values only — none of the moved files — so `CLAUDE.md` needs no edit.

---

## Separate item — `radiens.log`
Decision: **add to `.gitignore`, keep in place** (do not move). Append `radiens.log` to the vault-root `.gitignore` if not already present. (grep `.gitignore` first.)

---

## Execution order (when approved)
1. `.gitignore` += `radiens.log` (verify not already listed).
2. Tier 1: create `08-meetings/`; move 8 meeting files; move `storage-troubleshooting.md` → `03-troubleshooting/`; delete empty `02-procedures/emergency/`.
3. Tier 1 ref-updates (6 in-vault lines → prefer bare wikilinks).
4. Tier 2: create `02-procedures/eeg-recording/`; move the 12 acquisition docs.
5. Tier 2 ref-updates: `_INDEX.md` (13 links) + 3 external `~/.claude` memory refs.
6. Verify: re-grep for `06-references/(storage-troubleshooting|lab-meeting|progress-meeting)` and `02-procedures/(allego|signal|grounding|…)` path refs → expect zero stale; open `_INDEX.md` and confirm links resolve.
7. Note the reorg in [[2026-07-02]] journal "Still open" → done.

## Not touched (deliberately)
- All golden configs, `00-config/production-values.md`, journals (except the 2 ref lines), `CLAUDE.md`, `AI-INSTRUCTIONS.md`, `_templates/`.
- `05-experiments/` `active.md`+`active/` / `templates.md`+`templates/` duplication — needs a read first; **out of scope** for this pass.
- `hardware-sync-*` procedures — left in `02-procedures/` top (video-sync, not EEG acquisition).

## Related
- [[2026-07-02-eeg-recording-checkpoint]], [[2026-07-02]]

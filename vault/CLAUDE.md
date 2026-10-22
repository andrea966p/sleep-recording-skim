# CLAUDE.md — rules for this vault

This is the SKIM sleep lab's knowledge base (KAIST): mouse sleep EEG/EMG recording,
its analysis, the HLB SOD1 study, nanotag activity loggers, the video NVR, and the
machines behind them. It is an Obsidian vault inside the git repo `sleep-recording-skim`.
Humans read it in Obsidian; agents read and write the markdown. **The vault is the single
source of truth.** Claude's memory files only point here and hold behaviour rules.

Start every session at [[HOME]]. Rebuilt 2026-10-22; the old index is in `90-archive/`.

## Layout

| Folder | Holds |
|---|---|
| `HOME.md` | front door: areas, projects, where to put things |
| `00-inbox/` | anything not yet filed. New notes land here by default |
| `04-journal/YYYY-MM/YYYY-MM-DD.md` | one note per working day |
| `10-projects/<key>/` | time-bound efforts with a goal and an end: `hlb-sod1`, `rig-expansion`, `rig-bringup`, `noise-hunt`, `unipolar-lfp` |
| `20-areas/<key>/` | systems we keep running: `eeg-rig`, `allego`, `recording-console`, `eeg-analysis`, `sleep-scoring`, `nanotag`, `data-storage`, `computing`, `video-nvr` |
| `30-resources/` | `literature/`, `vendors/` (emails, call preps, quotes), `meetings/` (lab meetings, reports for the professor), `datasheets/` (PDFs, sensor maps) |
| `90-archive/` | pre-2026-10-22 navigation pages and content archived before the rehaul |
| `_attachments/` | every image and figure file, flat. Never overwrite one: date-prefix new names |
| `_templates/`, `_bases/`, `_meta/` | templates, Bases views, rehaul and lint records |

Every project and area folder has one hub, `_<key>-hub.md`. A folder never encodes status:
a finished project stays where it is with `status: done`.

`video-nvr` is an **active** area: the cameras were disconnected on 2026-08-04 and the work
will resume. Never call it retired.

## Where does a new thing go?

| I have… | Put it in | type |
|---|---|---|
| what happened today | `04-journal/YYYY-MM/YYYY-MM-DD.md` | journal |
| a run, a result, an analysis, a pre-registration, an audit | the project or area it is about | experiment |
| steps someone follows | the area the steps operate | procedure |
| a fact sheet, spec, concept, glossary, how something works | its area | reference |
| a choice between options (incl. council reviews) | the project or area it decides | decision |
| something that broke, or a symptom and its fix | the area that broke | incident |
| a meeting, slides, a report for the professor | `30-resources/meetings/` | meeting |
| a vendor email, quote, call prep | `30-resources/vendors/` | reference |
| a paper summary used across areas | `30-resources/literature/` | reference |
| not sure | `00-inbox/` | (any) |

A new area or project is a new folder plus its hub, and a line in [[HOME]].

## Frontmatter

```yaml
type: experiment          # hub | procedure | reference | experiment | decision | incident | meeting | journal
area: hlb-sod1            # the folder key; resources name the most related key
status: done              # planned | active | done | superseded
created: 2026-10-22
summary: "one line"       # required for journal notes and hubs
superseded-by: "[[note]]" # required when status is superseded
canonical: true           # only on a page that wins every disagreement
tags: [eeg, w-sd]         # few, lowercase
```

- `active` = in use, current, still followed, or still running. `done` = finished, the record
  stays valid. `superseded` = replaced or retracted; say by what.
- Keep every other key a note already has (`cohort`, `recordings`, `status-note`, …).
- `status-note` holds the old free-text status from before the rehaul. Do not delete it.

## Names and links

- File names: lowercase kebab-case; dated notes start `YYYY-MM-DD-`. Never rename a
  file casually: code, memory and other notes cite names. `CANONICAL-*` names stay.
- Every file name is unique in the vault (lint enforces it), so links are bare names:
  `[[per-mouse-csv-format]]`, `[[per-mouse-csv-format#Columns|the columns]]`. No folder
  paths, no `../`, never a link to a Claude memory file.
- In a table cell, escape the alias pipe: `[[note\|alias]]`.
- Images: `![[2026-10-22-fig01-name.png]]`, the file in `_attachments/`.

## Hubs

Plain markdown first (agents cannot see Bases views), in this order:
1. What this area/project is — three lines.
2. **Current state** — dated bullets, each with a link. The only place in the vault
   that may say "current", "latest", "newest" or "now". Replace a bullet when it changes;
   do not stack "NEWEST" markers.
3. Start here — at most five links.
4. Rules that must not be broken — each with a link to its evidence.
5. Open items.
6. `![[area.base]]` views.

## The journal

Title `# YYYY-MM-DD: headline`, `summary:` in frontmatter, a short TL;DR, then sections.
The journal records what happened and **links out**; detail lives in the area/project
note. When a day produces a result, a decision or a procedure, write that note and link it.

## Operations (for agents)

- **INGEST** — new information arrives (a run ended, a vendor replied, a decision was made):
  1. write or update the note in its project/area (template from `_templates/`);
  2. update that hub's Current state (date + link);
  3. add a line to today's journal linking the note;
  4. if it contradicts an older note, add a dated callout to the older note pointing at
     the newer one and set `superseded-by` when it is replaced.
- **CLOSE-OUT** — a run or project ends: `status: done`, write the result note, update the hub.
- **TRIAGE** — file everything in `00-inbox/` using the table above.
- **LINT** — `./skim lint` (read-only). Zero errors before you stop.
- **LOG** — vault-wide changes (renames, restructures) get a line in `_meta/log.md`.

## Accuracy rules

- Experiment, result and decision notes are records. Never rewrite their claims or numbers.
  Add a dated callout instead: `> [!warning] 2026-10-22: superseded by [[newer-note]] …`.
- Scientific numbers change only with Andrea's say-so.
- When two notes disagree, settle it only from primary evidence (the code, a read-only check
  of the live system, a later dated measurement). Otherwise log it in
  `_meta/contradictions.md` as `needs-Andrea`.
- Write dates as `YYYY-MM-DD`. Times are KST unless stated.

## Things code depends on

- `eeg-emg-analysis` writes figures to `vault/_attachments/` (`core/paths.py`).
- Code comments, `eeg-recorder/config/users.yaml` and systemd units cite note names.
  If you rename a note, grep the repo for its old name.
- `_meta/path-map-2026-10-22.tsv` maps every pre-rehaul path to its new one.

## Sync

Nothing syncs or commits by itself. `./skim pull` before editing, `./skim push "message"`
after; a human types both. Obsidian Git plugin timers are off.

## Video system rules (still in force)

- H.264 only on the Raspberry Pi 5 (H.265 causes kernel panics). No ffmpeg pipes in go2rtc;
  exec streams are single-line strings. systemd comments go on their own line;
  `KillMode=control-group` is mandatory.
- Files tagged `golden-config` are production-stable: change only after testing on the
  hardware, with Andrea's approval.
- [[production-values]] holds real IPs and usernames. The repo is private; keep it that way.

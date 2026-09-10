# AI Instructions

General-purpose reference for any AI agent working in this Obsidian vault. For Claude Code specifics, see `CLAUDE.md`.

## Vault Purpose

This vault documents a **neuroscience video surveillance system** — a Raspberry Pi 5 + Frigate NVR setup for 24/7 monitoring of research experiments. It tracks infrastructure configs, procedures, incidents, experiments, and daily work.

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `00-config/` | Production values (IPs, paths, credentials) — single source of truth |
| `01-infrastructure/` | Golden configs for go2rtc, systemd, Frigate, boot settings |
| `01-infrastructure/raspberry-pi/` | Pi-specific configs (H.264 only) |
| `01-infrastructure/frigate/` | Frigate Docker/config files |
| `02-procedures/` | Step-by-step operational guides |
| `03-troubleshooting/` | Symptom lookup and incident reports |
| `04-journal/` | Daily work logs, organized by month (`YYYY-MM/`) |
| `05-experiments/` | Experiment documentation (`active/`, `completed/`) |
| `06-references/` | Cheatsheets and parameter references |
| `99-archive/` | Old content (Notion import) |
| `_templates/` | Templater plugin templates |

## Key Files to Read First

- [[00-config/production-values|production-values.md]] — all production IPs, ports, paths, credentials
- [[_INDEX|_INDEX.md]] — vault home page with quick links and system status
- [[01-infrastructure/raspberry-pi/golden-go2rtc-config|golden-go2rtc-config.md]] — production go2rtc config
- [[01-infrastructure/raspberry-pi/golden-systemd-service|golden-systemd-service.md]] — systemd unit file
- [[01-infrastructure/raspberry-pi/golden-boot-config|golden-boot-config.md]] — Pi boot config
- [[01-infrastructure/frigate/config-yml|config-yml.md]] — Frigate configuration
- [[01-infrastructure/frigate/docker-compose|docker-compose.md]] — Frigate Docker Compose

## Frontmatter Patterns

Every document has YAML frontmatter. Fields vary by type:

### Journal
```yaml
tags: [journal, daily]
date: YYYY-MM-DD
```

### Incident Report
```yaml
tags: [troubleshooting, incident]
date: YYYY-MM-DD
severity: low/medium/high/critical
status: investigating/resolved/workaround
affected: [raspberry-pi, frigate, network]
```

### Experiment
```yaml
tags: [experiment]
date: YYYY-MM-DD
status: planned/active/completed
subjects:
chambers:
```

### Procedure
```yaml
tags: [procedure]
created: YYYY-MM-DD
status: draft/review/production
```

### Symptom
```yaml
tags: [troubleshooting, symptom]
created: YYYY-MM-DD
```

### Meeting Notes
```yaml
tags: [meeting]
date: YYYY-MM-DD
attendees:
```

### Infrastructure
```yaml
tags: [infrastructure, golden-config]
```
Additional topic tags: `go2rtc`, `systemd`, `boot`, `raspberry-pi`, `frigate`, `docker`

## Tag Taxonomy

| Category | Tags |
|----------|------|
| Document type | `journal`, `daily`, `incident`, `symptom`, `procedure`, `experiment`, `meeting`, `reference`, `dashboard`, `index` |
| Infrastructure | `infrastructure`, `raspberry-pi`, `frigate`, `docker`, `go2rtc`, `systemd`, `boot-config` |
| Status markers | `golden-config`, `production`, `archive` |
| Topics | `ssh`, `tailscale`, `rustdesk`, `watchdog`, `monitoring`, `configuration`, `hardening` |
| Sensitivity | `sensitive` (contains real credentials/IPs) |

## Writing Conventions

### Links
Use wikilinks with relative paths and aliases:
```
[[01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]
[[00-config/production-values|Production Values]]
```

### Formatting
- **Bold** for emphasis and labels
- `` `backticks` `` for IPs, ports, paths, commands, config values, and filenames
- Code blocks always use language hints: `` ```bash ``, `` ```yaml ``, `` ```ini ``
- Tables for config values, troubleshooting matrices, and quick reference
- Callout syntax for warnings and tips:
  ```
  > [!warning] Title
  > Content

  > [!tip] Title
  > Content
  ```

### Heading Hierarchy
- `# Title` — document title (one per file, matches filename)
- `## Section` — major sections (Summary, Steps, Notes, etc.)
- `### Subsection` — details within sections

### Variable Notation
Use `{VARIABLE}` placeholders referencing `production-values.md`:
```yaml
path: rtsp://{PI_IP}:{RTSP_PORT}/{CAMERA_0_ID}
# Resolves to: rtsp://192.168.0.11:8554/pi_cam_0
```
Always define new variables in `production-values.md`.

## Templates & Auto-Apply

### Available Templates (`_templates/`)

| Template | Auto-applies to | Key sections |
|----------|----------------|--------------|
| `Daily Journal.md` | `04-journal/` | Due Today (tasks query), Tasks, Focus, Work Log, Issues, Notes |
| `Incident Report.md` | `03-troubleshooting/incidents/` | Summary, Symptoms, Investigation, Root Cause, Resolution, Prevention |
| `Experiment.md` | `05-experiments/active/` | Overview, Protocol, Recording Setup, Data Files, Notes, Results |
| `Procedure.md` | — (manual) | Purpose, Prerequisites, Steps, Validation, Troubleshooting |
| `Symptom.md` | — (manual) | Description, Quick Diagnosis, Common Causes, Solutions |
| `Meeting Notes.md` | — (manual) | Agenda, Discussion, Decisions, Action Items |

## Daily Journal Format

Filename: `YYYY-MM-DD.md` in `04-journal/YYYY-MM/`

### Sections
1. **Due Today** — auto-populated tasks query (Tasks plugin)
2. **Tasks** — new tasks for the day
3. **Focus** — priorities
4. **Work Log** — detailed notes, uses `### Subsection` headings per topic
5. **Issues** — problems encountered
6. **Notes** — general notes

### Task Syntax
```
- [ ] Task description 📅 YYYY-MM-DD
- [x] Completed task 📅 YYYY-MM-DD ✅ YYYY-MM-DD
```

## Critical Rules

1. **Golden configs** — files tagged `golden-config` are production-stable. Do not modify without testing on the actual hardware first.

2. **H.264 only** — never use H.265/HEVC on the Raspberry Pi 5. It causes kernel panics.

3. **No ffmpeg pipes in go2rtc** — `rpicam-vid` streams directly to go2rtc via exec source. ffmpeg pipe chains are unstable for 24/7 operation.

4. **systemd files** — comments must be on separate lines. Inline comments (`Value # comment`) break systemd parsing.

5. **go2rtc exec streams** — must be single-line quoted strings. No YAML multi-line syntax (`|`, `>`).

6. **`{VARIABLE}` notation** — placeholders always reference `production-values.md`. Replace with actual values before deploying.

7. **Sensitive data** — `production-values.md` contains real IPs and credentials. Never commit to public repositories.

## Repository Setup

| Repo | Scope | Sync |
|------|-------|------|
| `neurosurveillance-vault` (private) | This entire Obsidian vault | Auto-backup every 10 min via Obsidian Git plugin |
| `neurosurveillance-system` (public) | Curated deployment docs and configs | Manual push only — no sensitive data |

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an **Obsidian vault** for documenting a neuroscience surveillance system. It tracks configuration, procedures, and operational knowledge for a Raspberry Pi 5 + Frigate NVR video monitoring setup used in neuroscience research.

**Key Infrastructure:**
- **Raspberry Pi 5** (`192.168.0.11`) running go2rtc (dual camera RTSP streaming)
- **ASUS Mini PC** (`192.168.0.50`) running Frigate NVR (Docker-based video processing)
- **One git repository** (`sleep-recording-skim`) holds this vault and all the code; every machine clones it and syncs by hand with `./skim`. Syncthing is RETIRED.
- **Tailscale** for remote access

## Documentation Architecture

### Folder Structure
```
00-config/              # Production values (IPs, paths, credentials)
01-infrastructure/      # Golden configs (go2rtc, systemd, boot settings)
  raspberry-pi/         # Pi-specific configs (H.264 only, no H.265!)
  frigate/              # Frigate Docker configs
02-procedures/          # Step-by-step operational guides
03-troubleshooting/     # Incident reports and symptom lookup
04-journal/            # Daily work logs (organized by month)
05-experiments/        # Research experiment documentation
06-references/          # Cross-cutting patterns + cheatsheets
07-decisions/           # Architectural reviews, council outputs, sprint plans (live status)
_templates/            # Templater plugin templates
99-archive/            # Old content (Notion import)
```

**`07-decisions/`** holds long-lived strategic artifacts that should not rot in daily journals:
- LLM council reviews (full advisor responses, peer reviews, chairman synthesis)
- Sprint plans with rolling status tables (single source of truth for "what's done vs open")
- Architectural decision records

Daily journals link forward to these; the decision docs link back. When the user asks "what was the council verdict" or "what's left from the sprint", the answer is in `07-decisions/`, not scattered across `04-journal/`.

> **Filing rule, enforced 2026-08-03.** `07-decisions/` had grown to 26 files, most of which were not decisions. It was trimmed to 9. A document belongs there only if it records **a choice between options**. Everything else goes where it belongs:
>
> | If the document is… | It goes in |
> |---|---|
> | a choice between options, a council, a sprint plan | `07-decisions/` |
> | a run, an audit, a result, a report on data | `05-experiments/completed/` |
> | literature, a vendor/product comparison, a spec, a glossary | `06-references/` |
> | steps someone follows to do a thing | `02-procedures/` |
> | a symptom and its fix | `03-troubleshooting/symptoms/` |
> | a failure that already happened, with a date | `03-troubleshooting/incidents/` |
> | vendor emails, call prep, quotes | `01-infrastructure/vendor-correspondence/` |
> | done and no longer followed | `99-archive/` |
>
> "It is important" is not a reason to file something under `07-decisions/`. Add an `_INDEX.md` line instead — that is what makes a document findable.

### Critical Files

- **`00-config/production-values.md`**: Single source of truth for all production values
  - Contains actual IPs, usernames, paths, camera settings
  - Uses `{VARIABLE}` notation that maps to deployed configs
  - **NEVER modify** without updating deployed systems

- **`01-infrastructure/raspberry-pi/golden-go2rtc-config.md`**: Production go2rtc config
  - **CRITICAL**: H.264 only (H.265 causes kernel panics on Pi5)
  - Uses `rpicam-vid` streaming directly to go2rtc (single-line exec strings, no ffmpeg pipes)
  - `KillMode=control-group` in systemd is mandatory (prevents zombie processes)

- **`_INDEX.md`**: Vault home page with quick links and system status

## Working with This Vault

### Variable System
Templates use `{VARIABLE}` placeholders that reference `production-values.md`:
```yaml
# Template:
path: rtsp://{PI_IP}:{RTSP_PORT}/{CAMERA_0_ID}

# Actual value (from production-values.md):
path: rtsp://192.168.0.11:8554/pi_cam_0
```

**When creating new docs**: Always use `{VARIABLE}` notation, define variables in `production-values.md`.

### Templates (Templater Plugin)
Located in `_templates/`, using Templater syntax:
- Date: `2026-02-04`
- Filename: `CLAUDE`

**Folder auto-templates configured:**
- `04-journal/` → Daily Journal
- `03-troubleshooting/incidents/` → Incident Report
- `05-experiments/active/` → Experiment

### SSH Access Commands
```bash
# Pi
ssh skimlab@192.168.0.11

# NVR
ssh skimlab@192.168.0.50

# Check go2rtc streams
curl http://192.168.0.11:1984/api/streams

# Check Frigate
curl http://192.168.0.50:5000/api/stats
```

## Critical Rules

1. **Golden Configs**: Files tagged `golden-config` are production-stable. Do NOT modify without extensive testing and user approval.

2. **H.264 Only**: Never suggest H.265/HEVC for Raspberry Pi (causes kernel panics).

3. **Sync Awareness**: Nothing syncs automatically. This vault lives inside the `sleep-recording-skim` repo; run `./skim pull` before editing and `./skim push "message"` after. Mention sync implications for infrastructure changes.

4. **Configuration Variables**: When showing configs with `{VARIABLES}`, remind user to replace with actual values from `production-values.md`.

5. **Sensitive Data**: `production-values.md` contains real IPs and usernames. Never suggest committing to public repos.

6. **Markdown Formatting**: Use backticks for values (`` `192.168.0.11` ``) for visual distinction.

## System Context

**Hardware:**
- Raspberry Pi 5 with dual camera modules (1024x768 @ 15fps)
- ASUS Mini PC (Ubuntu, Docker)
- Synology NAS for storage

**Software Stack:**
- go2rtc v5.0 (RTSP streaming)
- Frigate NVR (Docker)
- Obsidian with Templater plugin
- PostgreSQL (planned, not deployed)

**Use Case:** 24/7 video monitoring for neuroscience experiments with EEG/EMG data correlation.

## Claude Skill Integration

User has a `neurosurveillance-expert` skill on claude.ai containing parameterized configurations. This vault contains the **production values** that fill those parameters.

## Vault conventions (added 2026-05-24)

The 2026-05-24 rehaul introduced three reusable Obsidian callout patterns. When editing or creating new docs under `01-infrastructure/` or `02-procedures/`, preserve them.

- **`> [!abstract] TL;DR — for non-technical readers`** at the top of every major doc, after the frontmatter and H1. Three short paragraphs: "What this is," "Why it exists," "How to read this page." Always include a cross-link to [[nvr-system-overview]] for the big picture.
- **`> [!quote] Paper-ready`** at load-bearing technical claims. Present-tense active voice, 1-2 sentences, written so a user can paste it directly into a paper's methods section. Aim for 1-3 per major doc.
- **`> [!history] Historical note (pre-YYYY-MM-DD)`** inline where the doc replaces older behavior. Links forward to a verbatim pre-change archive in `99-archive/2026-05-rehaul/` (or a date-stamped sub-folder for future sprints). The archive file's `superseded-by` frontmatter links back. Bidirectional.

Two new entry-point files exist:
- `SYSTEM-OVERVIEW.md` (vault root) — ~250-word elevator pitch.
- `01-infrastructure/system-overview.md` — full Q&A overview + durability matrix + glossary.

Files under `03-troubleshooting/`, `04-journal/`, `05-experiments/`, and `06-references/` are the historical work log and are intentionally not rehauled. Do not retrofit TL;DR blocks into journal entries or incident reports; those represent the state of knowledge at the time of writing.

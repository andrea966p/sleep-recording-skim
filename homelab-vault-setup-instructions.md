# Homelab Obsidian Vault Setup Instructions

> **For Claude Code on the laptop** — Execute each section in order.
> **Target:** `/home/andrea/Projects/Homelab`
> **Source (read-only reference):** `/home/andrea/Monitoring Project Obsidian Vault`

---

## Section 1: Overview & Prerequisites

This sets up a new Obsidian vault for homelab + Home Assistant documentation. Settings, themes, and plugins are carried over from the monitoring vault with homelab-appropriate adaptations.

**What gets created:**
- Vault directory structure at `/home/andrea/Projects/Homelab`
- `.obsidian/` config with Obsidian Nord theme, hotkeys, editor prefs
- 7 community plugins (pre-installed from monitoring vault)
- 5 templates (3 adapted, 2 new)
- CLAUDE.md for Claude Code integration
- Index page

**Prerequisites:**
- Obsidian installed on the laptop
- The monitoring vault accessible at `/home/andrea/Monitoring Project Obsidian Vault` (for copying plugin files)

---

## Section 2: Create Directory Structure

```bash
mkdir -p /home/andrea/Projects/Homelab/{00-inventory,01-infrastructure/{pi5-services,home-assistant,network},02-procedures,03-troubleshooting/{incidents,symptoms},04-journal,05-automations,_templates,attachments,.obsidian/{themes,plugins}}
```

---

## Section 3: Obsidian Core Config Files

### `.obsidian/app.json`

```json
{
  "alwaysUpdateLinks": true,
  "attachmentFolderPath": "attachments",
  "livePreview": true,
  "showUnsupportedFiles": true
}
```

### `.obsidian/appearance.json`

```json
{
  "cssTheme": "Obsidian Nord",
  "accentColor": "#e78c36",
  "theme": "obsidian"
}
```

### `.obsidian/hotkeys.json`

```json
{
  "insert-template": [
    {
      "modifiers": ["Alt"],
      "key": "T"
    }
  ],
  "omnisearch:show-modal": [
    {
      "modifiers": ["Mod"],
      "key": "O"
    }
  ],
  "switcher:open": [],
  "periodic-notes:open-daily-note": [
    {
      "modifiers": ["Mod"],
      "key": "D"
    }
  ],
  "editor:delete-paragraph": []
}
```

### `.obsidian/core-plugins.json`

```json
{
  "file-explorer": true,
  "global-search": true,
  "switcher": true,
  "graph": true,
  "backlink": true,
  "canvas": true,
  "outgoing-link": true,
  "tag-pane": true,
  "footnotes": false,
  "properties": true,
  "page-preview": true,
  "daily-notes": true,
  "templates": true,
  "note-composer": true,
  "command-palette": true,
  "slash-command": false,
  "editor-status": true,
  "bookmarks": true,
  "markdown-importer": false,
  "zk-prefixer": false,
  "random-note": false,
  "outline": true,
  "word-count": true,
  "slides": false,
  "audio-recorder": false,
  "workspaces": false,
  "file-recovery": true,
  "publish": false,
  "sync": true,
  "bases": true,
  "webviewer": false
}
```

### `.obsidian/community-plugins.json`

```json
[
  "templater-obsidian",
  "periodic-notes",
  "settings-search",
  "obsidian-paste-image-rename",
  "omnisearch",
  "obsidian-tasks-plugin",
  "obsidian-local-rest-api"
]
```

---

## Section 4: Themes & Plugins

### Copy themes from monitoring vault

```bash
cp -r "/home/andrea/Monitoring Project Obsidian Vault/.obsidian/themes/Obsidian Nord" "/home/andrea/Projects/Homelab/.obsidian/themes/Obsidian Nord"
cp -r "/home/andrea/Monitoring Project Obsidian Vault/.obsidian/themes/AnuPpuccin" "/home/andrea/Projects/Homelab/.obsidian/themes/AnuPpuccin"
```

### Copy plugin files from monitoring vault

Copy the actual plugin code (manifest.json, main.js, styles.css) from the monitoring vault. This pre-installs them so Obsidian doesn't need to download anything.

```bash
# Plugins to copy
for plugin in templater-obsidian periodic-notes settings-search obsidian-paste-image-rename omnisearch obsidian-tasks-plugin obsidian-local-rest-api; do
  cp -r "/home/andrea/Monitoring Project Obsidian Vault/.obsidian/plugins/$plugin" "/home/andrea/Projects/Homelab/.obsidian/plugins/$plugin"
done
```

### Override plugin configs with homelab-specific settings

After copying, overwrite the `data.json` files with homelab-adapted configs.

#### `plugins/templater-obsidian/data.json`

```json
{
  "command_timeout": 5,
  "templates_folder": "_templates",
  "templates_pairs": [["", ""]],
  "trigger_on_file_creation": true,
  "auto_jump_to_cursor": false,
  "enable_system_commands": false,
  "shell_path": "",
  "user_scripts_folder": "",
  "enable_folder_templates": true,
  "folder_templates": [
    {
      "folder": "04-journal",
      "template": "_templates/Daily Journal.md"
    },
    {
      "folder": "03-troubleshooting/incidents",
      "template": "_templates/Incident Report.md"
    },
    {
      "folder": "02-procedures",
      "template": "_templates/Procedure.md"
    },
    {
      "folder": "03-troubleshooting/symptoms",
      "template": "_templates/Symptom.md"
    },
    {
      "folder": "01-infrastructure/pi5-services",
      "template": "_templates/Docker Service.md"
    },
    {
      "folder": "05-automations",
      "template": "_templates/HA Automation.md"
    }
  ],
  "enable_file_templates": false,
  "file_templates": [{"regex": ".*", "template": ""}],
  "syntax_highlighting": true,
  "syntax_highlighting_mobile": false,
  "enabled_templates_hotkeys": [""],
  "startup_templates": [""],
  "intellisense_render": 1
}
```

#### `plugins/periodic-notes/data.json`

```json
{
  "showGettingStartedBanner": false,
  "hasMigratedDailyNoteSettings": true,
  "hasMigratedWeeklyNoteSettings": false,
  "daily": {
    "format": "YYYY-MM/YYYY-MM-DD",
    "folder": "04-journal",
    "template": "_templates/Daily Journal.md",
    "enabled": true
  },
  "weekly": {
    "format": "",
    "template": "",
    "folder": ""
  },
  "monthly": {
    "format": "",
    "template": "",
    "folder": "",
    "enabled": false
  },
  "quarterly": {
    "format": "",
    "template": "",
    "folder": ""
  },
  "yearly": {
    "format": "",
    "template": "",
    "folder": ""
  }
}
```

#### `plugins/obsidian-tasks-plugin/data.json`

```json
{
  "presets": {
    "this_file": "path includes {{query.file.path}}",
    "this_folder": "folder includes {{query.file.folder}}",
    "this_folder_only": "filter by function task.file.folder === query.file.folder",
    "this_root": "root includes {{query.file.root}}",
    "hide_date_fields": "# Hide any values for all date fields\nhide due date\nhide scheduled date\nhide start date\nhide created date\nhide done date\nhide cancelled date",
    "hide_non_date_fields": "# Hide all the non-date fields, but not tags\nhide id\nhide depends on\nhide recurrence rule\nhide on completion\nhide priority",
    "hide_query_elements": "# Hide postpone, edit and backinks\nhide postpone button\nhide edit button\nhide backlinks",
    "hide_everything": "# Hide everything except description and any tags\npreset hide_date_fields\npreset hide_non_date_fields\npreset hide_query_elements"
  },
  "globalQuery": "",
  "globalFilter": "",
  "removeGlobalFilter": false,
  "taskFormat": "tasksPluginEmoji",
  "setCreatedDate": true,
  "setDoneDate": true,
  "setCancelledDate": true,
  "autoSuggestInEditor": true,
  "autoSuggestMinMatch": 0,
  "autoSuggestMaxItems": 20,
  "provideAccessKeys": true,
  "useFilenameAsScheduledDate": true,
  "filenameAsScheduledDateFormat": "YYYY-MM-DD",
  "filenameAsDateFolders": ["04-journal"],
  "recurrenceOnNextLine": false,
  "removeScheduledDateOnRecurrence": false,
  "statusSettings": {
    "coreStatuses": [
      {"symbol": " ", "name": "Todo", "nextStatusSymbol": "x", "availableAsCommand": true, "type": "TODO"},
      {"symbol": "x", "name": "Done", "nextStatusSymbol": " ", "availableAsCommand": true, "type": "DONE"}
    ],
    "customStatuses": [
      {"symbol": "/", "name": "In Progress", "nextStatusSymbol": "x", "availableAsCommand": true, "type": "IN_PROGRESS"},
      {"symbol": "-", "name": "Cancelled", "nextStatusSymbol": " ", "availableAsCommand": true, "type": "CANCELLED"}
    ]
  },
  "features": {"INTERNAL_TESTING_ENABLED_BY_DEFAULT": true},
  "generalSettings": {},
  "headingOpened": {"Core Statuses": true, "Custom Statuses": true},
  "debugSettings": {"ignoreSortInstructions": false, "showTaskHiddenData": false, "recordTimings": false},
  "loggingOptions": {
    "minLevels": {
      "": "info", "tasks": "info", "tasks.Cache": "info", "tasks.Events": "info",
      "tasks.File": "info", "tasks.Query": "info", "tasks.Task": "info"
    }
  }
}
```

#### `plugins/obsidian-local-rest-api/data.json`

> **Note:** Do NOT copy the monitoring vault's API key/certs. Obsidian will generate fresh ones on first launch.

```json
{
  "port": 27124,
  "insecurePort": 27123,
  "enableInsecureServer": false
}
```

#### `plugins/obsidian-paste-image-rename/data.json`

No custom config needed — defaults work fine. Delete the copied data.json so it uses defaults:

```bash
rm -f "/home/andrea/Projects/Homelab/.obsidian/plugins/obsidian-paste-image-rename/data.json"
```

---

## Section 5: Templates

### `_templates/Daily Journal.md`

```markdown
---
tags: [journal, daily]
date: 2026-02-22
---

## Due Today

` ` `tasks
not done
due on 2026-02-22
` ` `

## Tasks
- [ ]

## Focus
-

## Homelab Work


## Home Assistant


## Issues


## Notes

```

> **Note:** Remove the spaces between the backticks in the tasks code fence — they are escaped here to prevent rendering issues.

### `_templates/Incident Report.md`

```markdown
---
tags: [troubleshooting, incident]
date: 2026-02-22
severity: low/medium/high/critical
status: investigating/resolved/workaround
affected: [pi5, home-assistant, docker, network, cloudflare]
---

## Summary
- **Date/Time:** 2026-02-22 14:26
- **Duration:**
- **Severity:**
- **Status:**

## Symptoms
What was observed:
-

## Investigation

` ` `bash
# Commands run
` ` `

## Root Cause


## Resolution
1.

## Prevention
-

## Related
- Links to related docs
```

### `_templates/Procedure.md`

```markdown
---
tags: [procedure]
created: 2026-02-22
status: draft/review/production
---

## Purpose


## Prerequisites
- [ ]

## Steps

### 1.

` ` `bash
# Commands
` ` `

**Expected result:**

### 2.

` ` `bash
# Commands
` ` `

**Expected result:**

## Validation

` ` `bash
# Verification commands
` ` `

## Troubleshooting

| Issue | Solution |
|-------|----------|
| | |

## Related
-
```

### `_templates/Symptom.md`

```markdown
---
tags: [troubleshooting, symptom]
created: 2026-02-22
services: [pi5, home-assistant, docker, network]
---

## Symptom


## Possible Causes
1.

## Diagnostic Steps

` ` `bash
# Commands to diagnose
` ` `

## Solutions

### If cause is...
1.

## Related Incidents
-
```

### `_templates/Docker Service.md` *(new)*

```markdown
---
tags: [infrastructure, docker]
created: 2026-02-22
service:
host: pi5
status: running/stopped/planned
ports: []
---

## Overview


## Docker Compose

` ` `yaml
# docker-compose snippet for this service
` ` `

## Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| | | |

## Volumes / Mounts

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| | | |

## Networking
- **Ports:**
- **Network:**

## Maintenance

### Updating
` ` `bash
# Update commands
` ` `

### Backup
` ` `bash
# Backup commands
` ` `

### Logs
` ` `bash
# How to check logs
` ` `

## Related
-
```

### `_templates/HA Automation.md` *(new)*

```markdown
---
tags: [home-assistant, automation]
created: 2026-02-22
trigger:
entity:
status: active/disabled/draft
---

## Purpose


## Trigger


## Conditions
-

## Actions
1.

## YAML

` ` `yaml
# Home Assistant automation YAML
` ` `

## Testing
- [ ] Trigger fires correctly
- [ ] Actions execute as expected
- [ ] Edge cases handled

## Notes

```

---

## Section 6: CLAUDE.md

Write this file to `/home/andrea/Projects/Homelab/CLAUDE.md`:

````markdown
# CLAUDE.md

This file provides guidance to Claude Code when working in this vault.

## Repository Overview

This is an **Obsidian vault** for documenting a homelab and Home Assistant setup. It tracks device inventory, Docker services, Home Assistant automations, network configuration, and operational procedures.

**Key Infrastructure:**
- **Raspberry Pi 5** — Docker host running homelab services (migrated to SSD boot)
- **Home Assistant** — home automation platform
- **Cloudflare Tunnel** — secure external access (no port forwarding)
- **Tailscale** — mesh VPN for remote access

## Documentation Architecture

### Folder Structure
```
00-inventory/              # Device inventory, network maps
01-infrastructure/         # Configs and documentation
  pi5-services/            # Docker services on Pi5
  home-assistant/          # HA configs, integrations, dashboards
  network/                 # Network topology, DNS, Cloudflare
02-procedures/             # Step-by-step operational guides
03-troubleshooting/        # Incident reports and symptom lookup
  incidents/               # Post-mortem style reports
  symptoms/                # Symptom-based lookup docs
04-journal/                # Daily work logs (YYYY-MM/ subfolders)
05-automations/            # HA automations and scripts
_templates/                # Templater plugin templates
attachments/               # Images and file attachments
```

### Key Files

- **`00-inventory/homelab-inventory.md`**: Master inventory of all devices, IPs, and services
- **`_INDEX.md`**: Vault home page with quick links and status

## Working with This Vault

### Templates (Templater Plugin)
Located in `_templates/`, using Templater syntax.

**Folder auto-templates configured:**
- `04-journal/` → Daily Journal
- `03-troubleshooting/incidents/` → Incident Report
- `03-troubleshooting/symptoms/` → Symptom
- `02-procedures/` → Procedure
- `01-infrastructure/pi5-services/` → Docker Service
- `05-automations/` → HA Automation

### Hotkeys
- `Alt+T` — Insert template
- `Ctrl+O` — Omnisearch
- `Ctrl+D` — Open daily note

## Critical Rules

1. **Markdown Formatting**: Use backticks for values (e.g., `192.168.0.x`) for visual distinction.

2. **Docker Service Docs**: When documenting a new Docker service, use the Docker Service template. Include the compose snippet, environment variables, volumes, and port mappings.

3. **HA Automations**: Document automations with the HA Automation template. Always include the YAML source.

4. **Procedures**: Step-by-step guides should include verification commands and a troubleshooting table.

5. **Sensitive Data**: Be careful with API keys, passwords, and tokens. Never include them in plain text — use placeholders like `{API_KEY}` or reference a `.env` file.

## System Context

**Hardware:**
- Raspberry Pi 5 (SSD boot, Docker host)
- Home network equipment

**Software Stack:**
- Docker / Docker Compose
- Home Assistant
- Cloudflare Tunnel
- Tailscale
- Various self-hosted services

**Obsidian Plugins:**
- Templater (folder auto-templates)
- Periodic Notes (daily journal)
- Omnisearch (enhanced search)
- Tasks (task tracking with custom statuses)
- Local REST API (MCP integration)
````

---

## Section 7: _INDEX.md

Write this file to `/home/andrea/Projects/Homelab/_INDEX.md`:

```markdown
# Homelab Vault

## Quick Links

| Area | Link |
|------|------|
| Device Inventory | [[00-inventory/homelab-inventory]] |
| Pi5 Services | [[01-infrastructure/pi5-services/]] |
| Home Assistant | [[01-infrastructure/home-assistant/]] |
| Network | [[01-infrastructure/network/]] |
| Procedures | [[02-procedures/]] |
| Incidents | [[03-troubleshooting/incidents/]] |
| Automations | [[05-automations/]] |
| Daily Journal | [[04-journal/]] |

## Recent

```tasks
not done
sort by created reverse
limit 10
```

## System Status

| Service | Host | Status |
|---------|------|--------|
| Docker | Pi5 | |
| Home Assistant | Pi5 | |
| Cloudflare Tunnel | Pi5 | |
| Tailscale | Pi5 | |
```

---

## Section 8: Import Existing Docs

The homelab docs (`homelab-inventory.md` and `pi5-ssd-migration.md`) were not found in the monitoring vault. They may be located elsewhere on the system or need to be created.

**If the files exist somewhere else**, copy them:

```bash
# Adjust source paths as needed
cp /path/to/homelab-inventory.md "/home/andrea/Projects/Homelab/00-inventory/homelab-inventory.md"
cp /path/to/pi5-ssd-migration.md "/home/andrea/Projects/Homelab/02-procedures/pi5-ssd-migration.md"
```

**If they don't exist yet**, create placeholder files:

### `00-inventory/homelab-inventory.md`

```markdown
---
tags: [inventory, homelab]
updated: 2026-02-22
---

# Homelab Inventory

## Network

| Device | IP | MAC | Role | Notes |
|--------|----|-----|------|-------|
| Raspberry Pi 5 | | | Docker host | SSD boot |
| Router | | | Gateway | |

## Pi5 Docker Services

| Service | Port | Status | Notes |
|---------|------|--------|-------|
| | | | |

## Home Assistant Integrations

| Integration | Status | Notes |
|-------------|--------|-------|
| | | |
```

### `02-procedures/pi5-ssd-migration.md`

```markdown
---
tags: [procedure, pi5]
created: 2026-02-22
status: draft
---

## Purpose
Document the Raspberry Pi 5 SSD boot migration process.

## Prerequisites
- [ ] SSD connected to Pi5
- [ ] Backup of SD card

## Steps

### 1. Prepare SSD

```bash
# Commands
```

**Expected result:**

## Validation

```bash
# Verification commands
lsblk
```

## Related
- [[00-inventory/homelab-inventory]]
```

---

## Section 9: MCP Setup (Obsidian Local REST API)

The `obsidian-local-rest-api` plugin is pre-installed from Section 4. To connect Claude Code to the vault:

### Step 1: Get the API key (manual — requires Obsidian open)

1. Open Obsidian and point it at `/home/andrea/Projects/Homelab`
2. Go to **Settings → Community Plugins → Local REST API**
3. Copy the **API key** shown in the plugin settings

### Step 2: Add the MCP server to Claude Code

```bash
claude mcp add-json obsidian-rest-api '{
  "command": "npx",
  "args": [
    "-y",
    "obsidian-mcp"
  ],
  "env": {
    "OBSIDIAN_API_KEY": "<PASTE_API_KEY_HERE>",
    "OBSIDIAN_API_URL": "https://127.0.0.1:27124",
    "VERIFY_SSL": "false"
  }
}'
```

> Replace `<PASTE_API_KEY_HERE>` with the actual API key from Step 1.

### Step 3: Verify

```bash
claude mcp list
```

You should see `obsidian-rest-api` in the output.

---

## Section 10: Post-Setup Checklist

After Claude Code executes all the above:

- [ ] Open Obsidian, select "Open folder as vault" → `/home/andrea/Projects/Homelab`
- [ ] **Settings → Community Plugins** → Turn off "Restricted mode" if prompted
- [ ] Verify all 7 plugins appear and are enabled in Settings → Community Plugins
- [ ] Verify Obsidian Nord theme is active (Settings → Appearance)
- [ ] Test `Ctrl+D` — should create a daily note in `04-journal/YYYY-MM/`
- [ ] Test `Alt+T` — should show template picker
- [ ] Create a test note in `01-infrastructure/pi5-services/` — should auto-apply Docker Service template
- [ ] Create a test note in `05-automations/` — should auto-apply HA Automation template
- [ ] Check Local REST API plugin is running (Settings → Community Plugins → Local REST API)
- [ ] Copy API key and run the `claude mcp add-json` command from Section 9
- [ ] Verify with `claude mcp list`

---

## Notes

- **No git** was set up per user preference
- **Syncthing** is not configured — this vault is laptop-only for now
- The monitoring vault at `/home/andrea/Monitoring Project Obsidian Vault` was **not modified**
- Plugin files were copied from the monitoring vault to avoid needing to download them
- The Local REST API plugin will generate its own API key and certificates on first launch — the monitoring vault's credentials were intentionally not copied
- Template backtick escaping: the tasks code fences in templates use spaced backticks (`` ` ` ` ``) in this document to avoid rendering conflicts — Claude Code should write them as normal triple backticks when creating the actual files

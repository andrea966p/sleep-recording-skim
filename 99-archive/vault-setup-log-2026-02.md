---
tags: [archive, setup, log]
created: 2026-02-04
completed: 2026-02-05
---

# Obsidian Vault Setup Log

Session with Claude Code (claude-opus-4-5-20250101) on 2026-02-04 to 2026-02-05.

## Initial State

- Empty Obsidian vault at `/home/andrea/Monitoring Project Obsidian Vault`
- Notion import folder with previous documentation
- Syncthing configured to sync to PC 2

## Tasks Completed

### 1. Folder Structure Created
```
00-config/
01-infrastructure/raspberry-pi/, frigate/, network/
02-procedures/installation/, maintenance/, emergency/
03-troubleshooting/incidents/, symptoms/
04-journal/2026-02/
05-experiments/templates/, active/, completed/
06-references/neuronexus/, datasheets/
99-archive/notion-import-2025-02/
_templates/
```

### 2. Existing Content Archived
- Moved Notion import to `99-archive/notion-import-2025-02/`
- Preserved original structure for reference

### 3. Core Configuration Files Created
- `00-config/production-values.md` - All production IPs, paths, settings
- `00-config/task-dashboard.md` - Task overview (Tasks plugin)
- `00-config/weekly-view.md` - Weekly task view

### 4. Infrastructure Documentation
**Raspberry Pi:**
- `golden-go2rtc-config.md` - v5.0 go2rtc.yaml with ffmpeg pipe
- `golden-systemd-service.md` - KillMode=control-group (critical)
- `golden-boot-config.md` - Watchdog, WiFi/BT disabled, GPU mem
- `watchdog-monitoring.md` - Monitoring scripts and cron

**Frigate NVR:**
- `docker-compose.md` - Docker setup with Intel QSV
- `config-yml.md` - Recording-only config with TCP transport

### 5. Troubleshooting Guides
Created symptom-based lookup:
- `no-frames-received.md` - Camera offline troubleshooting
- `system-freeze-ssh-hang.md` - Zombie process fix
- `frigate-high-cpu.md` - QSV acceleration fix
- `docker-memory-crash.md` - Storage/memory issues

### 6. Templates Created (Templater syntax)
- Daily Journal
- Incident Report
- Experiment
- Procedure
- Symptom
- Meeting Notes

All templates use `2026-02-05` and `vault-setup-log-2026-02` syntax.

### 7. Reference Documentation
- `command-cheatsheet.md` - All Pi and Frigate commands
- `video-parameters.md` - Resolution/FPS/bitrate options

### 8. Experiments Archive
- `h265-encoding-failure.md` - Documented H.265 kernel panic failure

### 9. Plugin Configuration Guidance
- **Periodic Notes** - Daily notes with `04-journal/YYYY-MM` folder structure
- **Templater** - Folder templates for auto-apply
- **Tasks** - Task management with `📅 YYYY-MM-DD` syntax
- Discussed Full Calendar vs Tasks plugin workflow

### 10. Index and Navigation
- `_INDEX.md` - Home page with all links
- `CLAUDE.md` - Instructions for future AI agents

## Key Configuration Values Documented

| Item | Value |
|------|-------|
| Pi IP | 192.168.0.11 |
| NVR IP | 192.168.0.50 |
| Username | skimlab (both) |
| Cameras | pi_cam_0, pi_cam_1 |
| Resolution | 1024x768 @ 15fps |
| go2rtc path | /opt/go2rtc/ |
| Frigate path | /srv/frigate/ |

## Critical Rules Established

1. **H.264 ONLY** - H.265 causes kernel panics
2. **KillMode=control-group** - Prevents zombie processes
3. **TCP transport** - Required for RTSP reliability
4. **Golden configs** - Do not modify without testing

## Files Count

| Folder | Files Created |
|--------|---------------|
| 00-config | 3 |
| 01-infrastructure | 6 |
| 02-procedures | 1 |
| 03-troubleshooting | 5 |
| 04-journal | 1 |
| 05-experiments | 1 |
| 06-references | 2 |
| _templates | 6 |
| Root | 2 (_INDEX, CLAUDE.md) |
| **Total** | **27 files** |

## Next Steps

- [ ] Initialize Git repository
- [ ] Configure Obsidian Git plugin for auto-commits
- [ ] Fill in remaining placeholder values
- [ ] Create procedures as system is deployed

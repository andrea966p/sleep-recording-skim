# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This system is being prepared as a **Frigate NVR server** for scientific sleep research video surveillance. The full preparation guide is in `Frigate NVR Server Preparation.md`.

## Target System

- **Hardware:** ASUS NUC Pro 15 (Intel Ultra 7)
- **OS:** Ubuntu 24.04 LTS
- **Username:** `sleepigene`
- **Hostname:** `frigate-server`
- **Static IP:** `192.168.0.50`

## Critical Constraints

1. **Stability is paramount** - use only LTS packages
2. **HWE kernel required** - for Intel Ultra 7 optimization (must be 6.11.x+, NOT 6.8.x)
3. **All steps must be validated** before proceeding
4. **Record all version numbers** for scientific publication

## Key Commands

### System Validation
```bash
/opt/frigate/system-check.sh          # Run full system validation
cat /opt/frigate/SYSTEM_INFO.md       # View system documentation
```

### Intel Quick Sync Video
```bash
vainfo                                # Verify hardware acceleration
sudo intel_gpu_top                    # Monitor GPU usage
getent group render                   # Get render group GID (needed for Frigate)
```

### Docker
```bash
docker ps                             # List running containers
docker compose up -d                  # Start Frigate (from /opt/frigate)
docker stats frigate                  # Monitor Frigate resource usage
docker logs -f frigate                # View Frigate logs
```

### Network
```bash
ip addr show                          # Check IP configuration
```

## Directory Structure

```
/opt/frigate/
├── config/              # Frigate configuration files
├── storage/
│   ├── recordings/      # Short-term recordings cache
│   └── clips/           # Event clips

/media/frigate-recordings/  # Long-term recording storage
```

## Preparation Phases

Execute phases from `Frigate NVR Server Preparation.md` sequentially:
1. Base System Update
2. Hardware Enablement Kernel Installation
3. Network Configuration (static IP)
4. Docker Installation
5. Intel Quick Sync Video Setup
6. Storage Preparation
7. System Optimization
8. System Documentation
9. Final Validation

## Development Tools

### Node.js
- Managed via **nvm** (Node Version Manager)
- Default version: `lts/*`
- Switch versions: `nvm use <version>`

## Working from a machine other than e10ubuntu

The rig, the NVR, Allego/Radiens, Docker, Frigate and the EEG data all live on
`e10ubuntu` (Tailscale `100.82.250.62`). Only that machine can run those commands.

From the ThinkPad laptop or the office PC, run them over SSH instead:

```bash
ssh e10 'docker ps'
ssh e10 'vainfo'
```

For anything long running, use tmux so an SSH drop does not kill it:

```bash
ssh e10 -t 'tmux new -As rig'
```

tmux was MISSING on `e10ubuntu` until 2026-08-19 even though this line had promised it since
2026-08-16, so anything long running started that way before then died with the connection.
Installed now: `tmux 3.4` on e10ubuntu, `3.6` on the ThinkPad.

The Obsidian vault is synced to every machine by Syncthing, so vault files are local
and need no SSH. `.git` is deliberately NOT synced: the vault's git repository and
its backup timer exist on `e10ubuntu` only.

Full setup and the vault safety rules:
`Monitoring_project_obsidian_vault/01-infrastructure/multi-machine-work-setup.md`

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

Four machines share this workspace: `e10ubuntu` (the rig), the **SKIM office workstation**
(`/home/skim`, added 2026-09-16), the **ThinkPad** (`thinkpadubuntu`, user `andrea`, live on
the workflow 2026-09-19), and the office PC (`Andrea-KAIST-PC-ubuntu`, still on the old
tree). The table in `vault/01-infrastructure/multi-machine-work-setup.md` has the paths and
memory slugs.

To drive the ThinkPad from here: `tailscale ssh andrea@thinkpadubuntu '<command>'`. It has
no sshd, so ordinary `ssh` will not reach it. 🛑 Do not enable Tailscale SSH on `e10ubuntu`
— it hijacks port 22 for tailnet peers and breaks the laptops' key based `ssh e10`.

From any machine that is not `e10ubuntu`, run rig commands over SSH instead:

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

The whole workspace is ONE git repository, `sleep-recording-skim`, cloned on every
machine: the Obsidian vault, the recording software, the analysis code and this Claude
configuration. Vault files are local everywhere, so they need no SSH.

Sync is MANUAL and is one command:

```bash
./skim status          # am I behind? what have I not committed?
./skim pull            # before you start editing
./skim push "message"  # when you stop
```

Nothing commits or pushes by itself. `skim status` is read-only and runs at session
start; every writing verb is typed by a human.

> [!warning] Syncthing is RETIRED for this workspace
> Syncthing and git both syncing one directory, with a live `.git` replicated and no
> file versioning, destroyed the vault on 2026-04-29. `./skim check` fails if Syncthing
> is ever pointed back at this repository. **Gone from every machine** as of 2026-09-19.

> [!tip] A machine can pass every check and still be unable to push
> `machine/check.sh` and `./skim status` do not look at the git identity, and `./skim push`
> commits before it pushes. On a new machine set
> `git config --global user.name "andrea966p"` and
> `git config --global user.email "andrea96p@kaist.ac.kr"`.

> [!tip] On a new machine, `bootstrap.sh` success is not the whole story
> It KEEPS an existing `~/.claude/settings.json` and only prints `KEPT ... differs from
> the template`. Diff it: a machine that used Claude Code before this repo can end up with
> no hooks and therefore no `skim status` at SessionStart. See `machine/README.md`.

Full setup and the workspace rules: `vault/01-infrastructure/multi-machine-work-setup.md`
and `machine/README.md`.

<!-- BEGIN AWS Agent Toolkit rules -->

# AWS Guidance

- Where these AWS rules conflict with the project's own instructions, the
  project's instructions take precedence.
- Prefer the AWS MCP Server for AWS interactions — it provides sandboxed
  execution, observability, and audit logging. If unavailable, use the
  AWS CLI directly.
- Before starting a task, check whether a relevant AWS skill is available.
  Load the skill with `retrieve_skill` and prefer its guidance over
  general knowledge.
- When uncertain about specific AWS details (API parameters, permissions,
  limits, error codes), verify against documentation rather than guessing.
  State uncertainty explicitly if you cannot confirm.
- When creating infrastructure, prefer infrastructure-as-code (AWS CDK or
  CloudFormation) over direct CLI commands.
- When working with infrastructure, follow AWS Well-Architected Framework
  principles.
- Do not use em dashes in AWS resource names or descriptions. Use
  hyphens instead.

## Secret Safety

- MUST load the `aws-secrets-manager` skill first for any secret,
  credential, API key, token, or password task. MUST NOT call
  `secretsmanager get-secret-value` or `batch-get-secret-value`, and MUST
  NOT hit the Secrets Manager Agent daemon directly. MUST use
  `{{resolve:secretsmanager:secret-id:SecretString:json-key}}` with
  `asm-exec` so the secret resolves at runtime without entering context.

<!-- END AWS Agent Toolkit rules -->

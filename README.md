# claude-portable

Shared Claude Code configuration for every machine used on the NeuroSurveillance /
EEG project: `e10ubuntu` (the NVR and recording machine), `thinkpadubuntu` (personal
laptop) and, later, the office Ubuntu PC.

The point is that Claude Code behaves identically wherever you start it: same
memory, same skills, same hooks, same settings.

## Setup on a new machine

```
git clone <remote> ~/claude-portable
~/claude-portable/bootstrap.sh ~/Monitoring_project
~/claude-portable/check.sh ~/Monitoring_project
```

`bootstrap.sh` never deletes. Anything already at a target path is moved to
`<target>.pre-bootstrap`, and the script aborts rather than overwrite an existing
backup.

## What is shared, and why by symlink

| Path in repo | Linked from |
|---|---|
| `memory/` | `~/.claude/projects/<slug>/memory` |
| `skills/` | `~/.claude/skills` |
| `hooks/` | `~/.claude/hooks` |
| `project-skills/` | `<project>/.claude/skills` |
| `agent-skills/` | `<project>/.agents/skills` |
| `skills-lock.json` | `<project>/skills-lock.json` |
| `settings.json` | `~/.claude/settings.json` |
| `statusline-command.sh` | `~/.claude/statusline-command.sh` |
| `CLAUDE.md` | `~/CLAUDE.md` |

`<slug>` is the project's absolute path with every non-alphanumeric character
replaced by a dash, e.g. `/home/skimlab/Monitoring_project` becomes
`-home-skimlab-Monitoring-project`. It differs per machine because the username
differs. Each machine symlinks *its own* slug directory at the same shared
`memory/`, which is precisely what makes the username difference irrelevant.

## What is deliberately NOT here

Anything machine-specific or secret:

- `~/.claude.json` (holds MCP server definitions with local paths, and session state)
- `.credentials.json`, `history.jsonl`, `sessions/`, `shell-snapshots/`
- `projects/*/` session transcripts
- `plugins/` — not needed. `settings.json` carries `enabledPlugins` and
  `extraKnownMarketplaces`, so Claude Code reinstalls `superpowers`, `caveman` and
  `rust-analyzer-lsp` by itself on a new machine.
- `settings.local.json` — this is the right place for per-machine permissions, e.g.
  pre-allowing `Bash(ssh e10:*)` on the laptop.

## Portability notes

`settings.json` here is the portable rewrite. The version that lived on
`e10ubuntu` hardcoded `/home/skimlab/.nvm/versions/node/v24.12.0/bin/node` in both
hook commands, which would fail on any other machine. They now run through
`bash -lc 'node ...'` so a login shell resolves `node` through whatever nvm the
machine has.

## Keeping machines in sync

Commit and push after a working session; pull before starting one. Memory files
change often, so this is the file set most worth pushing.

If something looks stale, run `check.sh`. Some tools rewrite a config file by
renaming a temp file over it, which replaces a symlink with a regular file and
silently ends the sharing. `check.sh` detects exactly that; `bootstrap.sh` repairs it.

## Related

- Vault sync, SSH access and the vault deletion-safety rules:
  `Monitoring_project_obsidian_vault/01-infrastructure/multi-machine-work-setup.md`

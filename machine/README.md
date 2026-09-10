# Per-machine setup

Everything in this directory is about making one Ubuntu machine able to work on this
repository. Nothing here is synced state; it is instructions and reference copies.

## What each machine needs

| Thing | Why |
|---|---|
| git, an SSH key on GitHub | to clone and push this repo |
| Obsidian | to read and write `vault/` |
| Claude Code | `./machine/bootstrap.sh` wires it to `claude-config/` |
| Tailscale | to reach `e10ubuntu` as `e10` |
| tmux | long-running work over SSH that must survive a dropped connection |

Python virtual environments, `node_modules`, Rust build output and Docker are NOT
shared. They are per-machine and gitignored. Only `e10ubuntu` runs the rig.

## Bootstrap

```bash
./machine/bootstrap.sh
./machine/check.sh
```

`bootstrap.sh` symlinks Claude Code's memory, skills, hooks and `CLAUDE.md` at
`claude-config/`, and **copies** `settings.template.json` to `~/.claude/settings.json`.

The copy matters. Claude Code rewrites `settings.json` at runtime, so a symlink into
the repo leaves the working tree permanently dirty. `git rebase` refuses to start on a
dirty tree, which is exactly how the previous shared config repo deadlocked on
2026-08-22 and stayed stuck for 19 days: it could neither push nor pull, silently.

The Claude memory slug is derived from the workspace's absolute path, so it differs
per machine (`-home-skimlab-sleep-recording-skim` vs `-home-andrea-sleep-recording-skim`).
`bootstrap.sh` computes it, which is why a different username on another machine does
not matter.

## systemd/

Reference copies of the units that run on `e10ubuntu` only. They are here so the
configuration is readable from any machine. Copying them onto another machine is not
part of any normal workflow.

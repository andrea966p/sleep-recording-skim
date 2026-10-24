---
type: reference
area: computing
status: active
created: 2026-10-22
summary: "The live multi-machine workflow: one git repo sleep-recording-skim, synced by hand with ./skim; machines, SSH routes and the lessons that came from real damage"
tags: [computing, git, tailscale, workflow]
---

# Multi-machine workflow (live): one repo, `./skim`, four machines

> [!abstract] TL;DR
> The whole workspace (vault, recording software, analysis code, Claude configuration) is ONE
> private git repository, `sleep-recording-skim`, cloned on every machine. Nothing syncs by
> itself. A human types `./skim status`, `./skim pull`, `./skim push "message"`.
> Only `e10ubuntu` runs the rig; from any other machine use `ssh e10 '<command>'`.
> Written 2026-10-22 from the repo's `machine/README.md`, the root `CLAUDE.md` and the
> workspace memory record of 2026-09-10 to 2026-10-05. The machine table and the full
> migration story stay in [[multi-machine-work-setup]] (historical for the Syncthing parts).

## The commands

```bash
./skim status          # am I behind? what have I not committed? (read-only, runs at session start)
./skim pull            # before you start editing (git pull --rebase --autostash)
./skim push "message"  # when you stop (commits everything, then pushes)
./skim check           # Claude links intact, Syncthing not pointed at the repo, git identity set
./skim lint            # vault health, read-only
```

## Machines

| Machine | Host / user | Workspace | Reach it from e10 |
|---|---|---|---|
| `e10ubuntu` (the rig) | `192.168.0.50`, Tailscale `100.82.250.62`, user `skimlab`, Core Ultra 5 125H | `~/sleep-recording-skim` | local |
| SKIM office workstation | `skimworkstation`, user `skim` | `/home/skim/sleep-recording-skim` | Tailscale SSH, check mode: capture the approval URL with `script -qfc "tailscale ssh skim@skimworkstation …"` and give it to Andrea |
| ThinkPad | `thinkpadubuntu`, user `andrea` | `/home/andrea/sleep-recording-skim` | `tailscale ssh andrea@thinkpadubuntu '<cmd>'` (tag `tag:thinkpad`) |
| Office PC | `Andrea-KAIST-PC-ubuntu`, user `andrea` | still the old `~/Monitoring_project` tree | not on the workflow |
| KAIST BIlab PC, **Windows** side (2026-10-24) | `kaist-bilab-win`, Tailscale `100.88.120.75`, user `andrea` (admin) | `C:\Users\Andrea\sleep-recording-skim` (Git Bash: `~/sleep-recording-skim`) | `ssh andrea@100.88.120.75` (Windows OpenSSH server, key only, tailnet only) |

The other direction (laptop to e10) is ordinary sshd with a key and a `Host e10` block in
`~/.ssh/config`. `~/.ssh/config` is deliberately not in the repo. Why e10 must not run
Tailscale SSH, and how the tag rule works: [[multi-machine-work-setup]], section
"Reaching a machine FROM e10".

## Setting up a new machine

1. git, an SSH key on GitHub, Obsidian, Claude Code, Tailscale, tmux.
2. `./machine/bootstrap.sh` then `./machine/check.sh`.
3. 🔴 Set the git identity (`user.name andrea966p`, `user.email andrea96p@kaist.ac.kr`). `check.sh` and
   `skim status` both pass without one and `skim push` then fails. `./skim check` tests for it since 2026-09-19.
4. 🔴 If `bootstrap.sh` prints `KEPT ... differs from the template`, that is not a clean result.
   Diff `~/.claude/settings.json` against `claude-config/settings.template.json`; a machine can end
   up with no hooks and so no `skim status` at SessionStart. Detail in the repo's `machine/README.md`.
5. On a machine that ran the old `claude-portable` bootstrap, `bootstrap.sh` aborts on an existing
   `~/.claude/skills.pre-bootstrap`; the blockers are only symlinks (workspace memory, 2026-09-10).

## Lessons that cost something

- **Never put a runtime-rewritten file in a shared repo.** `settings.json` is copied from the template
  and gitignored. Its old tracked form kept the tree dirty, `git rebase` refused to start, and memory
  sync was dead 2026-08-22 to 2026-09-10. Never use `git rebase` in an automated script without `--autostash`.
- **Never let a second sync system touch the repo.** [[2026-04-29-syncthing-deletion-and-recovery]] is why.
  Syncthing is gone from every machine (2026-09-16 on e10 and the office PC, confirmed on the ThinkPad 2026-09-19).
- **A path move is never just a rename** (cron jobs, scripts, the gitignored `deploy/logs/`, the MCP server path):
  see the 2026-09-11 cutover section of [[multi-machine-work-setup]].
- **Renaming the workspace orphans every Claude Code session**: `claude --resume` is scoped to the working
  directory, and transcripts live in `~/.claude/projects/<slug-of-abs-path>/`. On 2026-09-11 the 22 old
  transcripts were copied across with `cp -rn` (`-n` so the live session is not clobbered).
- **Before deleting an old workspace, diff it for files git never saw.** On 2026-09-11 the one real
  casualty was `.claude/settings.local.json`, the project permission allow-list (270 rules since February), which
  existed only in the old tree. It is now carried as `claude-config/settings.local.template.json`.
- **`apt purge` does not stop a running daemon, and `apt autoremove` has no fixed blast radius**
  (13 libraries on e10, 52 packages and the NVIDIA stack on the office PC, 2026-09-16). Read the list on the
  machine you are sitting at: [[2026-09-16]].
- **The workstation is analysis-capable but not identical to e10** (2026-10-05): apt numpy 2.3.5 and scipy 1.16.3
  on Python 3.14, while e10 is numpy 1.26 and scipy 1.11. Check numbers before mixing machines.
- All six Docker packages are `apt-mark hold` on e10, so installs elsewhere cannot disturb Frigate.
- The Claude memory index has a size limit and is silently truncated above it; keep each entry a hook and
  put detail in topic files (workspace memory, 2026-09-11).
- Tailnet policy cannot be edited with the tailscale CLI (1.102.4): use the console or the API (GET /api/v2/tailnet/-/acl with Accept: application/hujson, then POST with If-Match on the ETag). Keep the API token in a 0600 file, never on a command line; deleting the file does not revoke it.
- On e10 the git identity is repo-local (.git/config), not ~/.gitconfig.
- Do not paste a large heredoc into someone's shell; it is mangled into a quote continuation. Use printf or an editor, then verify.
- An archived GitHub repo is read-only: to change its visibility, unarchive, flip, re-archive (403 otherwise). `neurosurveillance-system` was made private on 2026-09-11.

## The Windows machine (`kaist-bilab-win`, set up 2026-10-24)

Dual boot Windows/Ubuntu. The **Windows** side is on the workflow because EthoVision XT 11.5
(nanotag behaviour videos) and Office only run there; the Ubuntu side is not set up yet.
Only one OS runs at a time: `./skim push` before rebooting into the other, `./skim pull` after.
Everything below was checked live on 2026-10-24.

- **Run `./skim` from Git Bash**, not PowerShell. Git for Windows 2.56.0, Python 3.12.10
  (`~/bin/python3` is a shim, because `python3` otherwise hits the Microsoft Store alias),
  Node 24.22.1, jq 1.8.2, all via `winget`. Lint needs `markdown-it-py 3.0.0` and `pyyaml 6.0.1`
  (`pip install --user`, same versions as e10).
- **Global git config is not optional on Windows**: `core.autocrlf false` (the repo has no
  `.gitattributes`; CRLF breaks the bash scripts), `core.symlinks true` and Developer Mode on
  (66 tracked symlinks, verified as real `<SYMLINK>` entries), `core.longpaths true`.
- **Claude Code memory slug** is derived from the native path, `C--Users-Andrea-sleep-recording-skim`,
  not `/c/Users/...`. `bootstrap.sh` and `check.sh` use `cygpath -w` since 2026-10-24, and force
  `MSYS=winsymlinks:nativestrict`, because Git Bash's `ln -s` otherwise silently COPIES.
- **SSH in**: OpenSSH Server, `PasswordAuthentication no`, firewall rule `sshd-tailnet`
  (remote `100.64.0.0/10` only); the default `OpenSSH-Server-In-TCP` rule is disabled.
  e10's key is in `C:\ProgramData\ssh\administrators_authorized_keys` (admin account: the user
  `authorized_keys` is ignored). The PC's own key `andrea@kaist-bilab-win` is on GitHub and in
  e10's `authorized_keys`; `Host e10` is in `~/.ssh/config`.
- It first joined Tailscale in Andrea's home tailnet and showed up on e10 only as
  `device-of-shared-to-user` (no SSH, no route to e10). It must be logged in to the
  `skimlab.kaist@gmail.com` tailnet.

## Long-running work over SSH

```bash
ssh e10 -t 'tmux new -As rig'
```

tmux was missing on e10 until 2026-08-19, so anything started that way before then died with the connection.
Installed: tmux 3.4 on e10, 3.6 on the ThinkPad. Fallback with no multiplexer:
`ssh e10 'setsid nohup <cmd> > ~/logs/<n>.log 2>&1 < /dev/null &'`.

## Related

[[production-values]] (addresses and tailnets) · [[multi-machine-work-setup]] (history and machine table) ·
[[2026-08-19-laptop-workflow-alignment-task]] (old brief, Syncthing era)

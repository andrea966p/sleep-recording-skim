---
name: workspace-single-repo-sleep-recording-skim
description: "The whole workspace is ONE private git repo, sleep-recording-skim; Syncthing and claude-portable are retired and sync is manual via ./skim. Migration, machine table and gotchas are in the vault"
metadata:
  type: project
---

Built 2026-09-10; `~/sleep-recording-skim` (remote `andrea966p/sleep-recording-skim`, PRIVATE) holds `vault/`, `neurosurveillance/`, `neurosurveillance-system/`, `eeg-emg-analysis/`, `claude-config/`, `machine/`. Sync is MANUAL: `./skim status|pull|push "msg"|check`. Four machines (e10ubuntu, SKIM workstation, ThinkPad, office PC still on the old tree); e10 cutover done 2026-09-11, ThinkPad live 2026-09-19. `git log -- vault/` shows one commit: normal (subtree history).

Details: [[multi-machine-workflow]] (commands, machine table, new-machine checklist) · [[multi-machine-work-setup]] (migration, 19-day deadlock root cause) · [[multi-machine-setup-and-vault-safety]]

Rules:
- 🛑 Syncthing is RETIRED for this workspace (never remove a folder with "delete on disk"); two sync systems on one directory destroyed the vault on 2026-04-29.
- 🛑 On a machine that already has working key-based SSH, LEAVE TAILSCALE SSH OFF: `tailscale set --ssh` takes over port 22 and breaks `ssh e10` (`--ssh=false` gives it back). Reach a laptop from e10 with Tailscale SSH + a TAG (`dst` can only be `autogroup:self` or a tag; check mode OFF).
- Never put a runtime-rewritten file in a shared repo, and never use `git rebase` in an automated script without `--autostash`.
- `KEPT ... differs from the template` from `bootstrap.sh` IS NOT A CLEAN RESULT: diff `~/.claude/settings.json` (hooks, statusLine, effortLevel; drop any `autoMode.environment` block). A new machine needs a git identity (`check.sh` and `skim status` pass without one).
- A path move is never just a rename (cron jobs, deploy scripts, `nas-backup.sh` relative paths, gitignored `deploy/logs/`, MCP path in `~/.claude.json`); renaming the workspace orphans `claude --resume` (copy transcripts with `cp -rn`). Before deleting any old workspace diff it for never-tracked files (`settings.local.json` was the casualty).
- Index entries in MEMORY.md are hooks, not content (~200 chars each); the file was silently truncated at 24.4 KB once.
- Vault gap: paste a large heredoc into the user's shell with care (it mangles): use `printf` for a few lines, an editor for a file, and verify. The Tailscale policy API needs `Accept: application/hujson` (plain JSON blanks comments) and `If-Match` on the ETag; the `tailscale` CLI cannot edit policy. Keep an API token in a 0600 file, never on a command line (deleting the file does not revoke it).

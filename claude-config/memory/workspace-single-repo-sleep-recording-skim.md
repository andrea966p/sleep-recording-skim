---
name: workspace-single-repo-sleep-recording-skim
description: The whole workspace is now ONE git repo, sleep-recording-skim; Syncthing and claude-portable are retired and sync is manual via ./skim
metadata:
  type: project
---

Built 2026-09-10. **`~/sleep-recording-skim`, remote
`git@github.com:andrea966p/sleep-recording-skim.git` (PRIVATE), is the whole workspace**:
`vault/`, `neurosurveillance/`, `neurosurveillance-system/`, `eeg-emg-analysis/`,
`claude-config/`, `machine/`. Each of the first five came in with `git subtree` so their
full history is in the log (578 commits; the vault's 503 are reachable through the subtree
merge's second parent). ⚠️ **`git log -- vault/` shows only ONE commit — that is normal.**
Historical commits carry the pre-prefix paths, so a path-limited log cannot see them; judge
by total commit count and reachability instead.

**Four commands, nothing automatic:** `./skim status` (read-only, runs from a SessionStart
hook, exits non-zero when behind), `./skim pull`, `./skim push "msg"`, `./skim check`
(verifies the Claude symlinks AND that Syncthing is not pointed at the repo). The user
chose **fully manual** — no hook commits, no timer pushes.

🔑 **ROOT CAUSE OF THE 19-DAY MEMORY DEADLOCK (2026-08-22 → 2026-09-10).** `sync.sh` never
committed `settings.json` on purpose, so the tree was permanently dirty, and **`git rebase`
refuses to start on a dirty tree**. The log said `REBASE CONFLICT` but the real error was
`error: cannot rebase: You have unstaged changes`. The moment the laptop pushed one commit,
push AND pull both locked, silently. GitHub was missing ~14 memory files. Fixed by merging
(not rebasing) and pushing; then structurally prevented: **`settings.json` is now COPIED
from `claude-config/settings.template.json` by `machine/bootstrap.sh` and is gitignored.**

⭐ **Never put a runtime-rewritten file in a shared repo, and never use `git rebase` in an
automated script without `--autostash`.** Both `skim` rebase paths use it.

🛑 **Syncthing is RETIRED for this workspace** (removal is part of the cutover, never with
"delete on disk"). Two sync systems on one directory is what destroyed the vault on
2026-04-29. Retiring it also ends the dormant live-`.git` replication hazard with the
office PC.

⚠️ **CUTOVER ON e10ubuntu IS NOT DONE YET** and must wait for the live recording to end:
`/opt/neurosurveillance/session-daemon` is a **symlink into
`~/Monitoring_project/neurosurveillance/backend`**, so the daemon runs out of the OLD
workspace until that symlink is re-pointed. Also owed at cutover: re-run
`machine/bootstrap.sh` (the Claude memory slug changes to
`-home-skimlab-sleep-recording-skim`), retire `vault-git-backup.timer` (a SYSTEM timer, not
a user one, contrary to the old vault guide), remove the three Syncthing folders, and
rename the old tree rather than delete it.

**Why:** three sync mechanisms meant three things to forget, and the one that failed did so
without a single visible symptom for nineteen days.

**How to apply:** on any machine, `./skim status` before starting and `./skim push "msg"`
before stopping. Full write-up in the vault at
`01-infrastructure/multi-machine-work-setup.md`, final section. See also
[[multi-machine-setup-and-vault-safety]] (the superseded Syncthing-era setup).

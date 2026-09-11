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

✅ **THE THINKPAD IS LIVE ON THE NEW REPO, 2026-09-10** — cloned (140.93 MiB, 1737 files),
`check.sh` all nine links healthy, `settings.json` a real file, 78 memory files, `skim
status` clean and in sync. Syncthing disabled there with
`systemctl --user disable --now syncthing`.

🔑 **On any machine that ran the OLD `claude-portable` bootstrap, `machine/bootstrap.sh`
ABORTS**: `a backup already exists at ~/.claude/skills.pre-bootstrap` (from 2026-08-16).
The blocker is only a symlink, never real data. Delete the five symlinks first —
`~/.claude/{skills,hooks,statusline-command.sh,settings.json}` and `~/CLAUDE.md` — then
re-run. The `.pre-bootstrap` backups and `~/claude-portable` itself stay untouched.

🔴 **`bootstrap.sh` creates three symlinks INSIDE the workspace** (`.claude/skills`,
`.agents/skills`, `skills-lock.json`) that hold ABSOLUTE machine paths. They are gitignored
as of 2026-09-10; if they ever get committed, every other machine gets a path that does not
exist there.

✅ **CUTOVER DONE ON e10ubuntu, 2026-09-11** (after the 24.4 h run `allego_0__uid0910-09-00-00`
ended, 86 GB). Daemon symlink re-pointed and the daemon is `healthy: true` with MQTT and
Radiens connected; e10 bootstrapped (9/9 links, `settings.json` a real copy); all three
Syncthing folders removed from the config and the service disabled on BOTH machines;
`vault-git-backup.timer` disabled; NAS backup re-pointed and verified end to end (325 MB,
uploaded, byte-verified, rotation kept 3).

🔴 **A PATH MOVE IS NEVER JUST A RENAME. Five hidden references, all silent failures:**
(1) three **cron jobs** including the hourly recording watchdog and the 20-minute radix
archive watchdog; (2) the **deploy scripts carried the old path inside them**, so the copies
in the new repo were wrong too; (3) 🔑 **`nas-backup.sh` writes paths WITHOUT a leading
slash** (`home/skimlab/...`, because `tar -C /` needs them relative) — a grep for
`/home/skimlab/Monitoring_project` MISSES it; (4) **`deploy/logs/` is gitignored**, so it did
not exist in the clone at all, and it holds `radix-archive.state` + the manifest = the record
of what is already on the NAS (copied by hand with `cp -a`); (5) the **`obsidian-vault` MCP
server path in `~/.claude.json`**.

⭐ **NAS backup now takes the WHOLE workspace path** (one entry, so it also gets
`claude-config/` and `machine/`) and **explicitly excludes the raw EEG and video**:
`*/radix/data`, `*.xdat`, `*.mp4`, `storage`. Measured 325 MB / 2503 files / zero xdat / zero
mp4. Raw data goes to the NAS separately via `deploy/radix-archive.sh`.

⏳ **STILL OWED (post-session, Claude Code must be CLOSED for the second one):**
`mv ~/Monitoring_project ~/Monitoring_project.RETIRED-2026-09-11` — deferred because the
session's shell resets into that directory after every command — and
`sed -i 's|/home/skimlab/Monitoring_project/Monitoring_project_obsidian_vault|/home/skimlab/sleep-recording-skim/vault|g' ~/.claude.json`
for the MCP server. Also owed: archive the five source repos on GitHub, and fix the cosmetic
`Documentation=` line in `/etc/systemd/system/nas-backup.service`.
⚠️ A stale `watchdog2.py` from a 2026-08-26 session scratchpad has been running 15 days at 0%
CPU with its cwd in the old tree. Left alone, not killed.

🔑 **RENAMING THE WORKSPACE ORPHANS EVERY CLAUDE CODE SESSION.** `claude --resume` is scoped
to the CURRENT WORKING DIRECTORY: transcripts live in
`~/.claude/projects/<slug-of-abs-path>/`, so after the rename the old sessions were intact
but unreachable from anywhere you could now `cd`. **Fix: copy the transcripts across**
(`cp -rn ~/.claude/projects/-home-skimlab-Monitoring-project/* ~/.claude/projects/-home-skimlab-sleep-recording-skim/`)
— 22 sessions, 22 MB, done 2026-09-11. `-n` matters: it must not clobber the live session's
own `.jsonl`. The transcript still records the OLD cwd internally; harmless, resume uses the
process cwd.

✅ **CLAUDE CODE VERIFIED ON THE NEW PATH 2026-09-11:** 9/9 links healthy, `settings.json` a
real file outside the repo, hooks firing (caveman + `skim status` at SessionStart), plugins
loaded, the `obsidian-vault` MCP server reading `~/sleep-recording-skim/vault` (293 notes),
and 22 resumable sessions. `~/claude-portable` carries a `RETIRED.md` so nothing writes there
again.

🔴 **MEMORY.md WAS SILENTLY TRUNCATED** — 26.5 KB against a 24.4 KB limit meant the last 7
lines (Working Preferences, Operational patterns) never loaded. Fixed 2026-09-11 by trimming
the four longest index entries to one line each, after appending their full text to the topic
files they link to. Now 23.8 KB. ⭐ **Index entries are hooks, not content: keep each under
~200 chars and put the detail in the topic file.**

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

🏁 **MIGRATION CLOSED 2026-09-11.** All five source repos ARCHIVED on GitHub and verified
read-only (a probe push to `claude-portable` was refused): `neurosurveillance-vault`,
`neurosurveillance`, `neurosurveillance-system`, `eeg-emg-analysis`, `claude-portable`.
**`sleep-recording-skim` is the only live repo, and it is private.**
✅ `neurosurveillance-system` was public; made PRIVATE 2026-09-11. 🔑 An archived repo is READ-ONLY, so visibility cannot be changed directly — the API returns `403 Repository was archived so is read-only`; unarchive, flip, re-archive. Scanned before the change: no real
credentials, only private LAN IPs `192.168.0.11/.12/.50` and the dead Tailscale address
`100.120.86.10`.
⭐ `gh` 2.45.0 installed from the Ubuntu repos 2026-09-11 and authenticated (scopes: repo,
workflow, read:org, gist). All six Docker packages remain `apt-mark hold`, so the install
could not disturb Frigate.

🧹 **OLD TREES DELETED 2026-09-11** — `~/Monitoring_project.RETIRED-2026-09-11` (4.0 GB) and
`~/claude-portable` (19 MB). Verified first: no stashes, no unpushed branches, nothing dirty
in any of the four retired repos, and every file unique to the old tree was junk
(Syncthing sync-conflict copies, `.trash`, `.obsidian/workspace*.json`, egg-info, pytest
cache, tauri `gen/schemas`, a chrome `.deb`) or an identical `.pre-bootstrap` skills backup
(52 = 52, nothing unique).

🔴 **THE ONE REAL CASUALTY, CAUGHT IN TIME: `.claude/settings.local.json`** — the project
permission allow-list, **270 rules accumulated since February**, existed ONLY in the old
tree. Deleting it would have meant re-approving every command from scratch. Rescued, paths
repointed, and now carried in the repo as `claude-config/settings.local.template.json`,
which `machine/bootstrap.sh` copies into place on a machine that lacks it. The live file is
gitignored for the same reason as `settings.json`: Claude Code appends to it at runtime.
⭐ **Before deleting any old workspace, diff it against the new one for files that were
never tracked — the valuable ones are exactly the ones git never saw.**

✅ **FOURTH MACHINE: THE SKIM OFFICE WORKSTATION, 2026-09-16.** `/home/skim/sleep-recording-skim`,
Unix user `skim`, slug `-home-skim-sleep-recording-skim`, on the tailnet. Clone →
`machine/bootstrap.sh` → `machine/check.sh`, 8/8 links healthy first try. ⚠️ **It is NOT the
office PC** — that is a different box (`Andrea-KAIST-PC-ubuntu`, user `andrea`) still on the
old `~/Monitoring_project` tree.

🔴⭐⭐ **`bootstrap.sh` CAN REPORT SUCCESS AND LEAVE A MACHINE WITH NO HOOKS.** It KEEPS an
existing `~/.claude/settings.json` (correct — it is runtime-rewritten) and only prints
`KEPT ... differs from the template`. On the workstation that line hid a file with **no
`hooks` block and no `statusLine`** ⇒ no caveman hook, no statusline, and **no `skim status`
at SessionStart**, the one thing that tells you the clone is behind. `effortLevel` missing,
`caveman@caveman` not enabled. **`KEPT ... differs` IS NOT A CLEAN RESULT — DIFF IT.** Merge
`hooks` + `statusLine` + `effortLevel` from the template, keep the machine's own `model`,
`theme` and already-installed plugins, and DROP any `autoMode.environment` block (stale the
moment the workspace path changes — this one still described `/home/skim` with 0 tracked
files and no remote). Validate with `python3 -m json.tool` before restarting.

🔑 **`~/.ssh/config` is deliberately NOT in the repo**, so the `e10` alias is per-machine by
hand (`Host e10` / `HostName 100.82.250.62` / `User skimlab` / `ForwardAgent yes`), then
`ssh-copy-id e10` — possible because password auth on e10 is left enabled on purpose.
⚠️ **Pasting a large heredoc into the user's shell mangles it** (prompt left in quote
continuation). Use `printf` for a few lines, an editor for a file, and verify after.

✅⭐⭐ **THE THINKPAD IS ON THE PUSH/PULL WORKFLOW, 2026-09-19** — set up remotely from e10,
nobody sat at the laptop. `thinkpadubuntu` / `100.66.98.20`, user `andrea`,
`/home/andrea/sleep-recording-skim`, slug `-home-andrea-sleep-recording-skim`, kernel
6.17.0-1017-oem, tmux 3.6, git 2.53.0, node v22.22.1. 9/9 links, `settings.json` a real file
**WITH hooks + statusLine** (unlike the workstation), 84 memory files. Was 51 commits behind;
pulled.

🔴⭐⭐ **ITS ONLY REAL GAP WAS A MISSING GIT IDENTITY** — `user.name`/`user.email` empty at
every level. **`machine/check.sh` and `./skim status` BOTH PASS without one**, and `./skim
push` commits before it pushes, so the first attempt to send work back would have failed.
Set per machine. ✅ **`./skim check` now tests for it** (third section, exits non-zero when
missing). ⚠️ On e10 the identity is REPO-LOCAL in `.git/config`, not `~/.gitconfig`.

🔑⭐⭐ **REACHING A LAPTOP FROM e10 = TAILSCALE SSH + A TAG.** The laptops have NO sshd
(always clients). Enabling `--ssh` is not enough: default policy only allows
`autogroup:self`, and our machines have two different tailnet owners
(`skimlab.kaist@gmail.com` vs `andrea.piazzola4@gmail.com`). **A Tailscale SSH rule's `dst`
can ONLY be `autogroup:self` or a TAG** — the API rejects a cross-owner user with
`400 users in dst are only allowed from the same user`. So: tag the target
(`tag:thinkpad`), rule = src `skimlab.kaist@gmail.com` → dst `tag:thinkpad`, users
`autogroup:nonroot`, **check mode OFF** ("check" forces a browser re-auth per session and
blocks all unattended use). Then `tailscale ssh andrea@thinkpadubuntu '<cmd>'`.
⚠️ **Tagging MOVES the device's ownership to the tag**: it leaves every `autogroup:self`
rule, its keys stop expiring, and applying the tag can force a re-auth — do it while you can
still reach that machine.

🔴🔴⭐⭐⭐ **TAILSCALE SSH TAKES OVER PORT 22, IT DOES NOT ADD TO IT.** `sudo tailscale set
--ssh` run on **e10 by mistake** made `tailscaled` intercept port 22 for tailnet peers and
BYPASS the real sshd ⇒ the ThinkPad's key-based `ssh e10`, working for weeks, started
returning `tailnet policy does not permit you to SSH to this node` (compounded because the
ThinkPad had just become tag-owned, so `autogroup:member` no longer matched it).
**`sudo tailscale set --ssh=false` gives port 22 back.** 🛑 On a machine that already has
working key-based SSH, LEAVE TAILSCALE SSH OFF.

⚠️ **`tailscale` CLI CANNOT EDIT TAILNET POLICY** (no acl/policy subcommand in 1.102.4; node
auth ≠ admin auth). Only the console or the HTTP API, and the API token is minted in the
console. API route: `GET /api/v2/tailnet/-/acl` with `Accept: application/hujson` (plain
`application/json` blanks every comment to whitespace), edit, `POST` back with `If-Match` on
the ETag. Keep the token in a 0600 file, never on a command line; deleting the file does NOT
revoke it.

**SSH now: e10 → ThinkPad = Tailscale SSH via `tag:thinkpad`. ThinkPad → e10 = ordinary sshd
+ ed25519 key, `Host e10` in `~/.ssh/config`.** Different machinery each way.

**2026-10-05 workstation:** analysis-capable now (apt numpy 2.3.5 / scipy 1.16.3 on Python 3.14; e10 is numpy 1.26 / scipy 1.11, so check numbers before mixing machines) and SKIM NAS mounted via e10's automount units. Before 10-05 it had NO numpy and NO NAS mount. Tailscale SSH there is check mode: capture the approval URL with `script -qfc "tailscale ssh skim@skimworkstation ..."` and give it to Andrea.

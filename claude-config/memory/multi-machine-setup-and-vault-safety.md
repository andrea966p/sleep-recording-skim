---
name: multi-machine-setup-and-vault-safety
description: Work moved off e10ubuntu onto the ThinkPad laptop; the Syncthing settings that let the vault be deleted before are fixed; claude-portable shares memory and skills across machines
metadata:
  type: project
---

Set up 2026-08-16. `e10ubuntu` is needed for live recordings, so day to day work moves
to the ThinkPad laptop (`thinkpadubuntu`, `100.66.98.20`) and later the office PC.
`e10ubuntu` is `100.82.250.62`, reachable over Tailscale.

**FOUND THE VAULT DELETION CAUSE.** The Syncthing folder had **no file versioning**
(a delete anywhere propagated everywhere with ZERO undo) **and no `.stignore`**, so
the live 114 MB `.git` directory was replicated between machines while obsidian-git
committed into it on both ends. Both fixed: staggered versioning with 365 day
retention, and `/.git` excluded via `<vault>/.stignore`.

**Sync baseline, use it to verify any new device: 489 files, 153,935,853 bytes**
(excludes `.git`). ✅ **VERIFIED END TO END 2026-08-16:** laptop pulled to an exact
byte match as receive-only, then flipped to send-receive; create synced in ~5 s both
directions; **a delete on the laptop propagated in ~5 s AND left the full file
recoverable in `<vault>/.stversions/` on e10** — the exact operation that killed the
vault before is now survivable.

🔴 **THE OFFICE PC IS PAUSED AND UNSHARED FROM THE VAULT FOLDER.** The moment its
address was fixed to `dynamic` it reconnected **through a public Syncthing relay,
even though Tailscale reports it offline**, and started announcing its whole `.git`
into the shared index (global jumped to 4719 items / 260 MB). ⚠️ **Pausing a device
does NOT remove what it already announced** — the entries persist in the stored global
index. Fix was `.stignore` on the laptop plus removing the office PC from the folder's
device list. **Before letting it back: put `.stignore` on its copy FIRST**, then
unpause, re-share, verify counts. Never just unpause it.

**Non negotiable rules:** never remove a Syncthing folder with "delete on disk";
never point Syncthing at a directory that already holds another copy of the vault
(new device = empty dir, RECEIVE ONLY first, verify counts, then send-receive);
versioning mandatory on every device; `.git` stays excluded; cold `tar` snapshot to
`~/vault-snapshots/` before any Syncthing config change.

**Two Syncthing config dirs existed on e10ubuntu.** Live one is `~/.config/syncthing`
(device `2LNSMIM…`, web UI `127.0.0.1:8080`). The dead one is renamed to
`~/.local/state/syncthing.STALE-DO-NOT-USE`. Syncthing ≥1.28 moves the default config
dir there, so the live path is pinned in
`~/.config/systemd/user/syncthing.service.d/10-pin-home.conf`. It is a **user** unit,
not a system one, so no sudo is needed to manage it.

**Git backup no longer comes from Obsidian.** `.git` exists only on `e10ubuntu`;
`/home/skimlab/.local/bin/vault-git-backup.sh` runs from `vault-git-backup.timer`
every 15 min. obsidian-git auto intervals set to `0`.

**`~/claude-portable`** is the shared Claude Code config repo (memory, skills, hooks,
`skills-lock.json`, `CLAUDE.md`, portable `settings.json`). `bootstrap.sh <project>`
symlinks a machine into it, `check.sh` verifies. Claude keys memory on a slug from
the project's absolute path, so each machine symlinks **its own** slug dir at the one
shared `memory/` — that is what makes differing usernames irrelevant. The old
`settings.json` hardcoded an nvm node path and was not portable.

⚠️ **THE LAPTOP HAS TWO VAULT DIRECTORIES. Only one is live.**
`~/Monitoring_project/Monitoring_project_obsidian_vault` is the Syncthing folder and the
only one to work in. `~/Projects/Monitoring_project_obsidian_vault` is a **git clone of
`andrea966p/neurosurveillance-vault`, NOT synced by anything** — Syncthing's config lists
only `~/Sync` and the first path. On 2026-08-16 both were open in Obsidian at once, which
is pure confusion bait: `diff -rq` showed the trees **content-identical**, so the clone
holds nothing unique and edits made there would go nowhere and be silently lost. Fixed by
removing the clone from Obsidian's vault list (`~/.config/obsidian/obsidian.json`, backup
`.bak-20260816`, edited with Obsidian CLOSED so it could not rewrite the file on quit) and
deleting its leftover `.stfolder` marker. **The clone's files were left on disk.** Its
`.stignore` is git-tracked so it reappears in any clone; that is harmless.
⚠️ **A's `.stfolder` must never be deleted** — that is the live folder marker.

✅ **`claude-portable` SYNCS ITSELF from 2026-08-16** — `sync.sh` runs from a **`SessionEnd`
hook**, committing, rebasing and pushing once per Claude Code session. 🛑 **Do NOT copy the
vault's timer pattern here**: the vault's `.git` lives on ONE machine, but this repo has a
clone on EVERY machine all pushing one branch with `MEMORY.md` edited from both ends, so
races are normal. Script fails safe: `flock`, rebases only when behind, on conflict runs
`rebase --abort` + verifies HEAD returned and exits non-zero **without pushing**, `timeout 25`
on network calls, never deletes or force-pushes, logs to `~/.cache/claude-portable-sync.log`.
⚠️ **`settings.json` is NEVER auto-committed** — Claude Code rewrote `"model"` opus→sonnet by
itself on 2026-08-16, and the file is shared, so an unattended commit changes the model
everywhere; it is logged and left for a manual commit. `./sync.sh --status` = dry run.
⚠️ **Each machine needs a git identity in the clone** or the script refuses; both set to
`andrea966p <andrea96p@kaist.ac.kr>`.

✅ **RESOLVED 2026-08-19, see [[nas-backup-stale-address-outage]] — the text below is the
stale diagnosis, kept only for the history.** ~~🔴 **The Synology NAS backup has been FAILING since 2026-08-14** — the NAS is not in
the current tailnet at all (`tailscale ping 100.120.86.10` → `no matching peer`).
Same root cause as everything else here: the switch to the `skimlab.kaist@gmail.com`
tailnet left dead IPs hardcoded. Needs hands on the Synology. Last good backup
2026-08-13.~~ (Wrong on the fix: no hands on the Synology were needed; the cause was a hardcoded
`100.120.86.10` vs the real `100.120.86.9`, now the MagicDNS name.)

**Why:** the previous vault loss was not bad luck, it was a missing undo path plus
`.git` being synced. Both are now structurally prevented rather than remembered.

**How to apply:** when working from the laptop, run rig and NVR commands with
`ssh e10 '<cmd>'`, and `ssh e10 -t 'tmux new -As rig'` for anything long running.
Before changing anything in Syncthing, take the tar snapshot first. Full guide is in
the vault at `01-infrastructure/multi-machine-work-setup.md`. See also
[[nas-backup]] and [[feedback_verify_operational_details]].

⭐⭐ **2026-08-19: `claude-portable` now ALSO pulls at `SessionStart`** (`sync.sh --pull-only`), not
only at `SessionEnd`. 🔴 **Before this, a session on a second machine started by reading STALE
memory and only caught up at the END of a session that had already reasoned without it.**
`--pull-only` never commits, never pushes, and **refuses to rebase over a dirty tree**.
🛑 **BOOTSTRAP IS MANUAL, ONCE PER MACHINE — the hook that pulls is inside the commit you have not
pulled yet.** And `settings.json` is tracked but never auto-committed (Claude Code rewrites it, incl.
an `autoMode.environment` block with machine-specific absolute paths), so it is ALWAYS locally dirty
and **blocks `git pull --rebase`**: `git checkout -- settings.json` first, then pull.

🔴⭐⭐ **2026-08-19, MEASURED FROM THE LAPTOP: the two CODE folders still replicate a live
`.git` with NO versioning — the vault-killer combination, un-fixed by choice.**
`neurosurveillance-private` (`~/Monitoring_project/neurosurveillance`) has a `.stignore` that
covers only build artefacts, **no `/.git` line**; `neurosurveillance-system` has **no `.stignore`
at all**; **both have `versioning: NONE`**; `db/browse` lists `.git` at top level on both, so it
really is in the synced index (1.4 MB and 676 KB).
🔴 **CORRECTION: this does NOT involve the laptop.** The laptop's Syncthing has exactly two
folders, `default` (0 files) and the vault. Both code folders are shared **e10ubuntu ↔ office PC
(`TP5LGIP`) only**, and that device reads `connected=False paused=True` ⇒ **the hazard is DORMANT
and arms the instant the office PC is unpaused.** ⚠️ Unlike the vault, the office PC was **paused
but NEVER UNSHARED** from these two. **Precondition for any bring-back: tar snapshot to
`~/vault-snapshots/`, add `/.git` to both `.stignore`s ON BOTH MACHINES (`.stignore` is per-device
and never itself synced), consider staggered versioning.** Adding an ignore deletes nothing.
User decision 2026-08-19: **document only, do not touch e10ubuntu** (a recording was live).
Written up in the vault at the end of `01-infrastructure/multi-machine-work-setup.md`.
⚠️ **The laptop's Syncthing config is `~/.local/state/syncthing/config.xml`, web UI
`127.0.0.1:8384`** — the `~/.config/syncthing` + port 8080 above is the **e10ubuntu** layout only.
✅ Verified same day: vault `state=idle needFiles=0 errors=0`, **498 local = 498 global on BOTH
machines** (raw `find` on the laptop counts 501: +`.stignore` +`.stfolder` +`.obsidian/workspace.json`,
all deliberately per-machine). ⚠️ **The 489-file baseline above is STALE, it is 498 now.**
The clone `~/Projects/Monitoring_project_obsidian_vault` is still absent from `obsidian.json`
(only `Projects/Homelab` + the synced vault are listed) ⇒ still de-listed.
Laptop↔e10 Syncthing runs as a **direct LAN tcp connection on the KAIST network**, not Tailscale,
not a relay.

⚠️ **2026-08-19: `tmux` was NEVER INSTALLED on e10ubuntu**, though CLAUDE.md and the vault page
had told you to run `ssh e10 -t 'tmux new -As rig'` since 2026-08-16 ⇒ **anything long running
started that way in between died with its SSH connection.** No `screen`/`zellij`/`byobu`/`dtach`
either. Fixed: `sudo apt install tmux` ⇒ **tmux 3.4 on e10ubuntu, 3.6 on the ThinkPad**; docker is
`apt-mark hold` so the install could not touch it, live recording unaffected.
🔑 **A command written into a guide is not a validated command** — see [[feedback_verify_operational_details]].
Fallback with no multiplexer: `ssh e10 'setsid nohup <cmd> > ~/logs/<n>.log 2>&1 < /dev/null &'`
(survives a drop, no reattach).

⚠️ **Facts recovered from the laptop's 2026-08-22 commit when the two histories were
merged on 2026-09-10:** the vault sync baseline is **498 files, not 489**; the laptop's
Syncthing config lives at `~/.local/state/syncthing` with its web UI on `127.0.0.1:8384`
(the `~/.config/syncthing` + port 8080 layout is e10ubuntu's only); and as of 2026-08-19
the two CODE folders `neurosurveillance` and `neurosurveillance-system` still replicate a
live `.git` with NO versioning, shared with the PAUSED office PC only, never with the
laptop — dormant, and it arms the moment that machine is unpaused.

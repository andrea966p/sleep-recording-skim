# Multi machine work setup: laptop and office PC alongside e10ubuntu

Created 2026-08-16.

## TL;DR

The NVR machine `e10ubuntu` is increasingly needed for live recordings, so I moved
day to day work off it and onto my personal ThinkPad laptop, with the office Ubuntu
PC to follow. Three things had to be true for that to work: the Obsidian vault has
to sync to the laptop, Claude Code has to have the same memory and skills there, and
I have to be able to run commands on `e10ubuntu` from the laptop without opening a
remote desktop session.

While setting it up I found and fixed the thing that almost certainly destroyed the
vault the last time. **The Syncthing folder had NO FILE VERSIONING, so any delete on
any device propagated everywhere with no undo whatsoever. It also had NO IGNORE
RULES, which meant the 114 MB live `.git` directory was being replicated between
machines while the obsidian-git plugin was committing into it on both ends.** That is
a well known way to corrupt a git index and produce phantom deletions. Both are now
fixed.

I also found that **the nightly backup to the Synology network attached storage has
been failing since 2026-08-14** for the same underlying reason as everything else in
this note: the Tailscale account switch left old, dead IP addresses hardcoded in
several places.

## What was actually wrong

The tailnet was switched to `skimlab.kaist@gmail.com`. Several things still pointed
at addresses from the old tailnet, and nobody noticed because they fail silently:

| Thing | Stale value | Effect |
|---|---|---|
| Syncthing peer, office PC | `tcp://100.117.204.8:22000` (DEAD — bilab-era address) | Office PC could never reconnect |
| Network attached storage backup script | `bilab-syn.tail8808c0.ts.net` port 53 | FIXED 2026-08-19; was failing since 08-14 |

On top of that there were two separate Syncthing configuration directories on
`e10ubuntu` with two different device identities. The live one is
`~/.config/syncthing` (device `2LNSMIM...`, web interface on port 8080). A dead one
sat at `~/.local/state/syncthing` (device `WFNJNUT...`). **This mattered because
Syncthing version 1.28 and later changes its DEFAULT configuration directory to
`~/.local/state/syncthing`. A routine package upgrade would have silently switched
identity and made every synced folder look brand new.**

## What is now in place

### Vault safety, the part that must never fail again

1. **File versioning is ON** for the vault folder: staggered, 365 day retention.
   Deleted and overwritten files land in `<vault>/.stversions/`. This is the undo
   button that did not exist before.
2. **`<vault>/.stignore` now excludes `/.git`**, plus Obsidian workspace files,
   `.stversions` and `.trash`. The `.git` exclusion is what removes the corruption
   risk. The file carries a comment explaining why, so nobody removes it later.
3. Syncthing's configuration directory is **pinned** via a systemd drop in at
   `~/.config/systemd/user/syncthing.service.d/10-pin-home.conf`, so no upgrade can
   move it.
4. The dead configuration directory was **renamed, not deleted**, to
   `~/.local/state/syncthing.STALE-DO-NOT-USE`.

Sync baseline after these changes, useful as the acceptance number when adding a
device: **489 files, 153,935,853 bytes**. That excludes `.git`. With `.git` the
vault is about 4386 files and 260 MB. Recompute it when files are added, the point
is that a new device must match the other devices exactly before it is trusted.

### The office PC surprise, and why it is now paused

The moment I corrected the office PC's Syncthing address to `dynamic`, **it
reconnected**, through a public Syncthing relay at `218.236.76.26:22067`. Tailscale
still reports that machine as offline, so it had been reachable to Syncthing all
along and simply could not resolve the dead hardcoded address.

That was a problem, because the office PC has no `.stignore`, so it immediately began
announcing its entire `.git` directory into the shared index. The global index jumped
to 4719 items and 260 MB against this machine's 489 items and 154 MB, and the laptop,
which was mid sync, would have pulled all of it.

**WARNING WORTH REMEMBERING: pausing a device does NOT remove what it has already
announced.** The `.git` entries stayed in the stored global index after the pause. Two
things fixed it: putting `.stignore` on the laptop so it ignores them regardless, and
removing the office PC from the folder's device list, which dropped its contribution
from the index and returned it to a clean 489 items.

So the office PC is currently **paused AND unshared from the vault folder**. Before it
is allowed back it needs `.stignore` in place on its own copy, following the same
receive-only bootstrap as the laptop.

### Git backup moved off the Obsidian plugin

Because `.git` is no longer synced, only `e10ubuntu` holds a repository. Git backup
used to come from the obsidian-git plugin, which only runs while Obsidian is open
and which raced with a second copy of the plugin on the other machine.

Now: `/home/skimlab/.local/bin/vault-git-backup.sh`, driven by
`vault-git-backup.timer` every 15 minutes. It uses `flock` so runs cannot overlap,
commits only when the working tree is dirty, rebases before pushing, and never
force pushes. The obsidian-git plugin's auto intervals are all set to `0` (its
previous settings are saved next to it as `data.json.pre-timer-backup`).

### Passwordless access from the laptop

Standard OpenSSH with an ed25519 key, over Tailscale. Password authentication is
deliberately LEFT ENABLED so that no lab member gets locked out of this machine.

**SECURITY NOTE, worth knowing: `sshd` on `e10ubuntu` listens on `0.0.0.0:22` with
password authentication enabled, so it is reachable from the lab network by anyone
who has the password, not only over Tailscale.** That is unchanged, by choice. If we
ever want to close it without locking anyone out, the low risk move is a `ufw` rule
allowing port 22 only from `100.64.0.0/10` (Tailscale) plus the lab subnet, leaving
password authentication alone.

Long running rig commands must not die when the connection drops. Use
`ssh e10 -t 'tmux new -As rig'` for interactive work.

### Claude Code parity across machines

New repository at `~/claude-portable`, cloned onto every machine. It holds the
memory files, the personal and project skills, the hooks, `skills-lock.json`,
`CLAUDE.md`, the status line script and a portable `settings.json`. `bootstrap.sh`
symlinks each machine's paths at it, and `check.sh` verifies the links are intact.

The interesting detail: Claude Code stores per project memory under a slug derived
from the project's absolute path, so `/home/skimlab/Monitoring_project` becomes
`-home-skimlab-Monitoring-project`. A different username on the laptop yields a
different slug. Each machine therefore symlinks ITS OWN slug directory at the one
shared `memory/` folder, which is what makes the username difference stop mattering.

The old `settings.json` hardcoded `/home/skimlab/.nvm/versions/node/v24.12.0/bin/node`
in both hook commands and would have failed on any other machine. The portable
version runs the hooks through `bash -lc 'node ...'` instead.

Secrets and per machine state are deliberately excluded: `~/.claude.json`,
`.credentials.json`, `history.jsonl`, session transcripts, and `plugins/`. Plugins do
not need syncing because `settings.json` carries `enabledPlugins` and
`extraKnownMarketplaces`, so Claude Code reinstalls them by itself.

### The config repo syncs itself now (added 2026-08-16)

Having the repo on every machine is only half the job. Memory written on the laptop
stayed invisible to `e10ubuntu` until somebody remembered to commit, push and pull, and
that gap is silent: on 2026-08-16 `e10ubuntu` held a stale sync baseline for nine hours
without a single warning.

`~/claude-portable/sync.sh` now runs from a **`SessionEnd` hook**, so it fires once per
Claude Code session on whichever machine you were using. It commits, rebases and pushes.

> [!warning] This is NOT the same situation as the vault, do not copy the vault's pattern
> The vault gets away with an unattended 15 minute timer because its `.git` exists on
> **exactly one machine**. `claude-portable` has a working clone on **every** machine, all
> pushing the same branch, and `MEMORY.md` is a single file edited from both ends. Races
> are normal here, not exceptional. That is why this is a per session hook rather than a
> timer, and why the script is written to fail safe.

What the script guarantees:

- `flock` serialises runs, so a second one skips instead of fighting the first.
- It rebases **only when actually behind**, and on conflict it runs `git rebase --abort`,
  verifies `HEAD` returned to where it started, and exits non-zero **without pushing**. It
  never leaves a half finished rebase sitting in the repository that holds the memory.
- Network calls are wrapped in `timeout 25`, so a dead network cannot hang the end of a
  session. A failed fetch or push leaves the commit safely local for the next run.
- It never deletes, never force pushes, never resets.
- Everything is appended to `~/.cache/claude-portable-sync.log`, because hook output is
  invisible in normal use and a silent failure would defeat the point.

> [!warning] `settings.json` is deliberately NEVER auto committed
> Claude Code rewrites that file at runtime. On 2026-08-16 it flipped `"model"` from
> `opus` to `sonnet` on its own. The file is shared by every machine, so an unattended
> commit would silently change the model everywhere. Changes to it are reported in the log
> and left for you to commit by hand.

`./sync.sh --status` shows what would be committed and what is being held back, and
changes nothing.

**Each machine needs a git identity in that clone**, or the script refuses to run and
tells you the two commands. Both machines are set to
`andrea966p <andrea96p@kaist.ac.kr>` as of 2026-08-16.

## STANDING RULES, do not break these

- **NEVER remove a Syncthing folder using the "delete on disk" option. NEVER use
  Obsidian's "delete vault".**
- **NEVER point Syncthing at a directory that already holds a different copy of the
  vault.** Adding a device means: brand new EMPTY directory, set the folder to
  RECEIVE ONLY, wait for the full sync, verify the file count and byte size against
  the baseline above, and only then switch it to send and receive.
- **File versioning is mandatory on every device that holds the vault.** If a device
  shows versioning "None", it is misconfigured, fix it before syncing anything.
- **`.git` stays excluded from Syncthing.** Git backup exists on `e10ubuntu` ONLY.
- **Before any change to Syncthing configuration, take a cold snapshot first:**
  `tar -czf /home/skimlab/vault-snapshots/vault-$(date +%Y%m%d-%H%M).tar.gz -C /home/skimlab/Monitoring_project Monitoring_project_obsidian_vault`
  then verify it with `tar -tzf <archive> | grep -v '/$' | wc -l`.
  `/home/skimlab/vault-snapshots/` is deliberately outside every synced folder.
- The live Syncthing configuration on `e10ubuntu` is `~/.config/syncthing`, device
  `2LNSMIM...`, web interface `http://127.0.0.1:8080`.
  `~/.local/state/syncthing.STALE-DO-NOT-USE` is dead, do not edit it.

## Reference values

| Item | Value |
|---|---|
| `e10ubuntu` Tailscale address | `100.82.250.62` |
| `thinkpadubuntu` Tailscale address | `100.66.98.20` |
| Office PC (`Andrea-KAIST-PC-ubuntu`) | `100.125.44.24`, offline since roughly 2026-01 |
| Syncthing device, `e10ubuntu` | `2LNSMIM-T2IHNXN-CYC34M7-QIB2MRT-HHQ5UKZ-EFLAPIW-WZ2SCSC-SBA5WQP` |
| Syncthing device, office PC | `TP5LGIP-Q6DWZUV-NUQ7SOI-O3WHCDT-PZEIQY7-IBKF6H4-FZBNHX4-TKSE4QY` |
| Syncthing folder identifier | `monitoring_project_obsidian_vault` |
| Vault git remote | `git@github.com:andrea966p/neurosurveillance-vault.git` |

## Proof that it works

Ran end to end on 2026-08-16, laptop paired and verified:

- Laptop pulled the vault into a brand new empty directory as RECEIVE ONLY and landed
  on exactly **489 files, 153,935,853 bytes, 0 needed, 0 errors**, matching e10ubuntu
  to the byte. Only then did I flip it to send and receive.
- **No `.git` on the laptop**, confirmed. Git backup stays on `e10ubuntu` alone.
- Created a file on the laptop, it reached `e10ubuntu` in about 5 seconds.
- Edited it on `e10ubuntu`, the change reached the laptop.
- **Deleted it on the laptop. The delete propagated in about 5 seconds AND the full
  file, both lines, was sitting recoverable in `<vault>/.stversions/` on e10ubuntu.**
  That is the exact operation that destroyed the vault last time, and it is now
  survivable.
- `claude-portable` cloned onto the laptop and `check.sh` reported all nine links
  healthy. The laptop's slug is `-home-andrea-Monitoring-project` versus e10ubuntu's
  `-home-skimlab-Monitoring-project`, which is the whole reason the symlink
  indirection exists.
- Passwordless SSH from the laptop works, and the host key fingerprint
  `SHA256:ADQlu52SqlujF7Qz80/oPpMbgfTopAP47Fc9c2LxsbQ` matches this machine's real
  key, so the connection is not being intercepted.

## STILL OPEN

> [!warning] DEFERRED 2026-08-16, by choice
> The first two items below both need me to be **physically at a machine that is not the
> laptop**, so they were deliberately postponed on 2026-08-16 rather than forgotten. See
> [[04-journal/2026-08/2026-08-16]]. ✅ **The backup gap is CLOSED as of 2026-08-19** — see below.

- ✅ **RESOLVED 2026-08-19 — the Synology backup works again, and the fix was not what this
  page predicted.** I did not have to touch the Synology, and it did not need to be logged into
  `skimlab.kaist@gmail.com`. Two things were needed: **(a)** share the NAS node from the
  `bilab.kaist@gmail.com` tailnet to `skimlab.kaist@gmail.com` and accept it, and **(b)** fix the
  address, which was the actual cause — `nas-backup.sh` had `100.120.86.10` hardcoded and the NAS
  answers on `100.120.86.9`.
  🔴 **`NAS_HOST` is now the MagicDNS name `bilab-syn.tail8808c0.ts.net` and must stay a name.**
  The 08-11/12/13 tarballs had indeed survived, exactly as predicted here, because pruning only
  runs after a verified upload.
  ⚠️ **Do not trust `tailscale ping` as the test** — it answered `pong` while every TCP port was
  dead, and it kept answering on the wrong address until the peer map refreshed. That single
  measurement produced two wrong diagnoses. Full write-up:
  [[03-troubleshooting/incidents/2026-08-19-nas-backup-wrong-address]].
- ✅ **All 831 GB of raw recordings are now on the NAS too**, checksum-verified, which was never
  true before. See [[01-infrastructure/raw-recording-archive-to-nas]].
- **The office PC is PAUSED and UNSHARED from the vault folder.** To bring it back:
  put `.stignore` on its copy of the vault FIRST, then unpause, then re-share the
  folder, then verify its file count matches before trusting it. Do not simply
  unpause it. It is reachable through the Syncthing relay even while Tailscale
  reports it offline, so it will reconnect the instant it is allowed to.
- The office PC is also still on the OLD tailnet. Worth logging it into
  `skimlab.kaist@gmail.com` while I am there, same as the Synology.
- Obsidian is now installed on the ThinkPad. **Expect obsidian-git to complain there**:
  `.obsidian/community-plugins.json` is synced so the plugin loads on the laptop, but
  the laptop deliberately has no `.git`. Its auto intervals are already `0` so it does
  nothing, it just may show a "not a git repository" notice. Harmless. If I disable the
  plugin to silence it, note that the toggle syncs and it will switch off on e10ubuntu
  too, which is fine because `vault-git-backup.timer` does the backups now.
- Claude Code is v2.1.227 on the ThinkPad and v2.1.233 on e10ubuntu. Not a problem,
  worth keeping roughly aligned.

## Continuing work on the laptop (added 2026-08-19)

`~/claude-portable` shares memory, skills, hooks and settings between machines over git.
**Until 2026-08-19 it only synced on `SessionEnd`.** That meant a session on the laptop began by
reading whatever memory happened to be on the laptop's disk, which could be days behind e10ubuntu —
and only caught up at the *end* of a session that had already been reasoning without it.

`sync.sh --pull-only` now runs on **`SessionStart`** as well. It fetches and fast-forwards, never
commits, never pushes, and **leaves a dirty tree strictly alone** rather than rebasing over
uncommitted memory edits.

### One-time bootstrap on each other machine

> [!warning] THE HOOK THAT PULLS IS INSIDE THE COMMIT YOU HAVE NOT PULLED YET
> So the first pull has to be done by hand, once, per machine. After that it maintains itself.

`settings.json` is tracked but deliberately **never auto-committed**, because Claude Code rewrites it
at runtime (it has flipped `model` by itself, and it writes an `autoMode.environment` block full of
machine-specific absolute paths). On any machine that has been used, `settings.json` will therefore
be locally modified, and that **blocks a plain `git pull --rebase`**.

```bash
cd ~/claude-portable && git status --short
```

If `settings.json` shows as modified, set it aside first. Its contents are machine-specific and
regenerate on their own, so dropping the local edit costs nothing:

```bash
cp ~/claude-portable/settings.json /tmp/settings.local.bak
```
```bash
cd ~/claude-portable && git checkout -- settings.json
```
```bash
cd ~/claude-portable && git pull --rebase
```

Expected: it fast-forwards and `settings.json` now contains **two** `SessionStart` hooks — the
caveman one and `sync.sh --pull-only`. Confirm:

```bash
grep -c 'pull-only' ~/claude-portable/settings.json
```
Expected: `1`.

From then on every session starts with current memory, and `--status` shows what any sync would do
without changing anything:

```bash
~/claude-portable/sync.sh --status
```

### What still is NOT shared, by design

| Thing | Why | How the laptop gets it |
|---|---|---|
| `settings.json` local edits | machine-specific paths; Claude Code rewrites it | regenerates itself |
| The vault's `.git` | single repository on e10ubuntu only | Syncthing syncs the files, not `.git` |
| The rig, Allego, Docker, the EEG data | they physically live on e10ubuntu | `ssh e10` |
| `neurosurveillance` branches | committed locally on e10ubuntu, not pushed by default | `ssh e10`, or push the branch deliberately |

> [!note] The laptop cannot run the rig
> Anything touching Allego, radiens, Docker, Frigate or `~/radix/data` only works on e10ubuntu.
> From the laptop use `ssh e10 '<command>'`, and `ssh e10 -t 'tmux new -As rig'` for anything long
> running so an SSH drop does not kill it.

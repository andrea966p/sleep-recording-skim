# Multi machine work setup: laptop and office PC alongside e10ubuntu

Created 2026-08-16.

> [!warning] SUPERSEDED 2026-09-10. HISTORICAL, DO NOT FOLLOW THE WORKFLOW BELOW.
> Everything on this page that describes **Syncthing** is retired. The whole
> workspace is now ONE git repository, `sleep-recording-skim`, cloned on every
> machine, and it syncs by hand with `./skim status`, `./skim pull`, `./skim push`.
> Nothing syncs by itself any more.
>
> **Syncthing is gone from every machine.** Uninstalled from `e10ubuntu` and the office PC
> on 2026-09-16 — packages, units, configuration directories and all, with each machine's
> device identity parked at `~/syncthing-config-retired-2026-09-16` on that machine. The
> ThinkPad was confirmed clean on 2026-09-19: no binary, no `~/.local/state/syncthing`, no
> `~/.config/syncthing`. See [[../04-journal/2026-09/2026-09-16|2026-09-16]] and
> [[../04-journal/2026-09/2026-09-19|2026-09-19]].
>
> **Read this page for WHY, not for HOW.** The diagnosis of what destroyed the vault
> on 2026-04-29 (no file versioning, a live `.git` replicated between machines) is
> the reason the current setup looks the way it does, and the Tailscale address
> findings further down are still correct. The Syncthing folder inventories, the
> configuration directory pin and the device identifiers below are now dead
> reference.

## The machines, as of 2026-09-16

This part is current, unlike the Syncthing material below.

| Machine | Host / user | Workspace | Claude memory slug | Role |
|---|---|---|---|---|
| `e10ubuntu` | `100.82.250.62`, user `skimlab` | `~/sleep-recording-skim` | `-home-skimlab-sleep-recording-skim` | **the rig.** Allego, Docker, Frigate, the EEG data. Only this machine runs them |
| SKIM office workstation | `skimworkstation`, `100.111.139.53`, user `skim` | `/home/skim/sleep-recording-skim` | `-home-skim-sleep-recording-skim` | day to day work, added 2026-09-16. Tailscale SSH ON, in **check** mode, so e10 can SSH in |
| ThinkPad | `thinkpadubuntu`, `100.66.98.20`, user `andrea` | `/home/andrea/sleep-recording-skim` | `-home-andrea-sleep-recording-skim` | day to day work. Tagged `tag:thinkpad` so e10 can SSH in |
| Office PC | `Andrea-KAIST-PC-ubuntu`, user `andrea` | old tree only, at `~/Monitoring_project` | — | **not yet on the one repo.** Holds uncommitted work, see the 2026-09-16 journal |

Every machine needs the same six things: git with an SSH key on GitHub, **a git identity**,
Obsidian, Claude Code wired by `machine/bootstrap.sh`, Tailscale, and tmux.

> [!warning] A machine can pass every check and still be unable to push
> The ThinkPad had no `user.name` or `user.email` at any level on 2026-09-19, while
> `machine/check.sh` reported all nine links healthy and `skim status` reported clean and
> in sync. Neither command looks at the git identity, and `./skim push` commits before it
> pushes, so the first attempt to send work back would have failed. Set it per machine:
> `git config --global user.name "andrea966p"` and
> `git config --global user.email "andrea96p@kaist.ac.kr"`.
>
> `./skim check` tests for this as of 2026-09-19 and exits non-zero when it is missing, so
> running it on a new machine is now enough to catch it. Only `e10ubuntu` runs
the rig; from anywhere else use `ssh e10 '<command>'`, and `ssh e10 -t 'tmux new -As rig'`
for anything long running.

`~/.ssh/config` is deliberately NOT in the repository, so the `e10` alias is set up by
hand once per machine:

```
Host e10
  HostName 100.82.250.62
  User skimlab
  ForwardAgent yes
```

Then `ssh-copy-id e10`. Password authentication on `e10ubuntu` is left enabled on purpose
so no lab member is locked out, which is what makes that first copy possible.

> [!note] SKIM office workstation, verified 2026-09-28
> Checked from e10 over Tailscale SSH (`tailscale ssh skim@skimworkstation`). Ubuntu 26.04.1,
> kernel 7.0.0-31, login shell **zsh** (nvm loads from `.zshrc`, so Claude Code's node hooks work
> when it is started from a terminal).
> - ✅ Repo clean, `./skim pull` fast-forwarded 44 commits, `./skim status` in sync, `./skim check`
>   all links healthy, Syncthing not running.
> - ✅ Git identity set; GitHub accepts `~/.ssh/id_ed25519_github`; `git push --dry-run` authenticates.
> - ✅ `ssh e10` works on a DEDICATED key, `~/.ssh/id_ed25519_e10` (no passphrase), named in the
>   workstation's `Host e10` block; its public half is the third line of e10's `authorized_keys`.
>   Backups: `~/.ssh/config.bak-2026-09-28` on the workstation, `~/.ssh/authorized_keys.bak-2026-09-28`
>   on e10.
> - ⚠️ Tailscale SSH is in **check** mode: the first connection from e10 in each check period needs a
>   browser approval by `skimlab.kaist@gmail.com`.
> - ✅ tmux 3.6 installed 2026-09-28 (session create/detach tested).
> - ✅ Obsidian 1.13.7 installed 2026-09-28 from the official `.deb` (`/opt/Obsidian/obsidian`,
>   covered by Ubuntu's shipped AppArmor profile; `kernel.apparmor_restrict_unprivileged_userns = 1`
>   here, so an AppImage would need `--no-sandbox`). Vault opened with the author trusted: all 12
>   community plugins loaded, REST API on `127.0.0.1:27124` only, and **the working tree stayed
>   clean**. obsidian-git has every auto interval at 0 and pull-on-boot off, so it never syncs by
>   itself. ⚠️ e10 runs the Flatpak (`md.obsidian.Obsidian`), not the `.deb`.
> - ℹ️ The Local REST API key and certificate are tracked in `vault/.obsidian/plugins/
>   obsidian-local-rest-api/data.json` (private repo, localhost only). Reviewed 2026-09-28 and
>   accepted as is by Andrea.
>
> **The workstation is ready for the manual `./skim pull` / `./skim push` workflow.**

### Reaching a machine FROM e10, which is the harder direction

The laptops have no sshd; they were only ever clients. To drive one from `e10ubuntu`, as
was done to set the ThinkPad up on 2026-09-19, the route is Tailscale SSH:

1. On the target: `sudo tailscale set --ssh`
2. Tag the target, because a Tailscale SSH rule's **destination can only be
   `autogroup:self` or a tag, never another user's login**. Our machines belong to two
   different tailnet users, so the tag is unavoidable. The API rejects the alternative
   outright: `400 users in dst are only allowed from the same user`.
3. Add the rule in the console's visual SSH editor: source `skimlab.kaist@gmail.com`,
   destination `tag:thinkpad`, as destination user `autogroup:nonroot`, **check mode Off**.

Then `tailscale ssh andrea@thinkpadubuntu '<command>'` from `e10ubuntu`.

Two things that cost time, both worth knowing before repeating this:

> [!warning] Tagging moves a device's ownership
> A tagged device belongs to the tag, not to the person. It drops out of every
> `autogroup:self` rule, its keys stop expiring, and applying the tag can force it to
> re-authenticate. Do it while you can still physically reach that machine.

> [!warning] Tailscale SSH takes over port 22, it does not add to it
> Turning it on makes `tailscaled` intercept port 22 for tailnet peers and bypass the real
> sshd, so existing `authorized_keys` stop being consulted. On 2026-09-19 it was enabled on
> `e10ubuntu` by mistake and silently broke `ssh e10` from the ThinkPad, which had worked on
> a key for weeks. `sudo tailscale set --ssh=false` gives port 22 back. **On a machine that
> already has working key based SSH, leave Tailscale SSH off.**

Note also that `tailscale` has no ACL or policy subcommand. Tailnet policy can only be
changed in the admin console or through the HTTP API, and the API needs an access token
minted in that same console. Being logged in on a node grants no admin authority.

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

> [!warning] tmux did not exist on e10ubuntu until 2026-08-19
> This page and `CLAUDE.md` had promised that command since 2026-08-16, but the binary was
> never there. Neither was `screen`, `zellij`, `byobu` or `dtach`, so **every long running
> command run this way since then died with its SSH connection**. Installed 2026-08-19 with
> `sudo apt install tmux`, now `tmux 3.4` on e10ubuntu and `3.6` on the ThinkPad. Docker is
> `apt-mark hold` so the install could not disturb it, and the live recording was unaffected.
> LESSON: an instruction written into a guide is not a validated instruction. If a fallback
> is ever needed again, `ssh e10 'setsid nohup <cmd> > ~/logs/<name>.log 2>&1 < /dev/null &'`
> survives a drop, but gives you no reattach.

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
- 🔴 **The two code folders replicate a live `.git` with NO versioning, and the office PC is
  still SHARED on both of them** (paused, but not unshared the way the vault was). Measured
  2026-08-19, deliberately NOT fixed. `.stignore` on both machines is a PRECONDITION for the
  bring-back above. Details and the exact fix: the last section of this page.
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

## The live `.git` replication hazard on the two code folders (measured 2026-08-19, NOT fixed, deliberate)

> [!warning] DORMANT, NOT SAFE. It arms the moment the office PC is unpaused.
> `neurosurveillance` and `neurosurveillance-system` are Syncthing folders that DO
> replicate a live `.git`, with NO file versioning, so there is no undo. That is exactly
> the combination that destroyed the vault on 2026-04-29. Nothing was changed on
> 2026-08-19 because the only peer for both folders is the office PC and it is paused,
> so today the replication goes nowhere. **The fix below is a PRECONDITION for bringing
> the office PC back, alongside the vault `.stignore` step already listed in STILL OPEN.**

### What I actually measured, from the laptop

Everything here came from the Syncthing REST application programming interface on both
machines on 2026-08-19, not from memory.

| Syncthing folder | Path on e10ubuntu | Peers | Excludes `/.git`? | Versioning |
|---|---|---|---|---|
| `monitoring_project_obsidian_vault` | `~/Monitoring_project/Monitoring_project_obsidian_vault` | laptop + e10ubuntu | YES | staggered |
| `neurosurveillance-private` | `~/Monitoring_project/neurosurveillance` | **office PC** + e10ubuntu | **NO** | **NONE** |
| `neurosurveillance-system` | `~/Monitoring_project/neurosurveillance-system` | **office PC** + e10ubuntu | **no `.stignore` file at all** | **NONE** |

- `db/browse` on both code folders lists `.git` at the top level, so `.git` really is in
  the synced index, it is not merely un-ignored on disk. Sizes are 1.4 MB and 676 KB.
- `neurosurveillance-private` does have a `.stignore`, but it only covers build
  artefacts, editor files and logs. There is no `/.git` line in it.
- Office PC device `TP5LGIP` reads `connected=False, paused=True` on e10ubuntu, and both
  code folders still list it as a device. So it is PAUSED but, unlike the vault folder,
  it was never UNSHARED from these two.
- All three folders were `state=idle`, `needFiles=0`, `errors=0`. Vault is 498 local and
  498 global on both machines, `neurosurveillance-private` 242, `neurosurveillance-system` 121.

### 🔴 Correction to what this page said before

The laptop does **not** have either code folder. Its Syncthing has exactly two folders,
`default` (empty, 0 files) and the vault. Any claim that a live `.git` is replicating
between e10ubuntu and the ThinkPad is WRONG. The exposure is e10ubuntu to office PC only.

### The fix, when it is done

Run it on e10ubuntu, and on the office PC's own copy before that machine is unpaused,
because **`.stignore` is per device and is itself never synced**.

1. Tar snapshot both folders into `~/vault-snapshots/` first. Standing rule.
2. Add `/.git` to `~/Monitoring_project/neurosurveillance/.stignore`.
3. Create `~/Monitoring_project/neurosurveillance-system/.stignore` containing `/.git`.
4. Consider turning on staggered versioning for both folders, matching the vault.

Adding an ignore rule deletes nothing. Syncthing simply stops syncing that path. But
note the lesson from the vault: **pausing or ignoring does NOT retract what a device has
already announced into the global index**, so if the office PC ever does announce its
`.git`, removing it from the folder's device list is what cleans the index.

### Other small corrections from the same session

- The laptop's Syncthing config is `~/.local/state/syncthing/config.xml` and its web
  interface is on `127.0.0.1:8384`. The `~/.config/syncthing` plus port 8080 written
  elsewhere on this page is the **e10ubuntu** layout, not a universal one.
- Laptop to e10ubuntu Syncthing is currently a DIRECT local network transmission control
  protocol connection on the KAIST network, not Tailscale and not a relay.

---

# 2026-09-10: everything moved into ONE repository, `sleep-recording-skim`

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The vault, the recording software, the analysis code and the Claude
> Code configuration now live in a single git repository called `sleep-recording-skim`.
> Every computer clones that one repository. There is nothing else to set up.
>
> **Why it exists.** The old arrangement synced the same workspace three different ways
> at once: Syncthing for the vault, a second git repository for Claude's memory, four
> separate repositories for the code. Three mechanisms meant three things to forget, and
> one of them failed silently for nineteen days.
>
> **How to read this page.** Everything above this line describes the OLD setup and is
> kept for the record. This section is what is true now.

## What was actually wrong with the old setup

**The memory sync had been deadlocked since 2026-08-22 and nobody could tell.** On
2026-09-10 `e10ubuntu` was 7 commits ahead and 1 behind `claude-portable`, and GitHub was
missing roughly fourteen memory files: every EEG finding from 08-24 to 09-09. A session
started on the laptop read memory from three weeks earlier.

The cause was one design decision colliding with one git rule. `sync.sh` deliberately
never committed `settings.json`, because Claude Code rewrites that file at runtime and an
unattended commit would change the model on every machine. That left the working tree
permanently dirty. **`git rebase` refuses to start on a dirty tree.** The log said
`REBASE CONFLICT`, but the real error underneath was:

```
error: cannot rebase: You have unstaged changes.
```

So the moment the laptop pushed one commit, both directions locked: the push path could
not rebase, and neither could the pull path. The safety rule protecting the model setting
is what disabled the sync.

> [!quote] Paper-ready
> A file rewritten by the application at runtime must not live inside a shared
> repository. It keeps the working tree permanently dirty, which blocks rebase and
> therefore blocks both push and pull.

## What is in place now

One private repository, `git@github.com:andrea966p/sleep-recording-skim.git`, cloned to
`~/sleep-recording-skim` on every machine:

| Directory | Came from | How |
|---|---|---|
| `vault/` | `neurosurveillance-vault` | `git subtree`, full history |
| `neurosurveillance/` | `neurosurveillance`, branch `ops/nas-archive-and-scheduled-recording` | `git subtree`, full history |
| `neurosurveillance-system/` | `neurosurveillance-system` | `git subtree`, full history |
| `eeg-emg-analysis/` | `eeg-emg-analysis`, branch `master` | `git subtree`, full history |
| `claude-config/` | `claude-portable` | `git subtree`, full history |
| `machine/` | new | bootstrap, check, systemd reference copies |

`git subtree` rather than submodules: submodules pin a dependency at a commit for
reproducible builds, which is not the problem here, and they buy detached heads and
two-step commits in exchange. Nothing is pinned and there is one author, so the files
simply live in the repository.

## The only four commands

```bash
./skim status          # am I behind? what have I not committed?
./skim pull            # get the other machine's work
./skim push "message"  # commit everything and push
./skim check           # Claude links intact, and Syncthing really gone
```

**Nothing syncs by itself, by choice.** `skim status` is read-only and runs from a
`SessionStart` hook so a stale machine says so out loud. Everything that writes is typed
by a human.

`skim pull` and the pull inside `skim push` both use `git pull --rebase --autostash`.
The autostash is not decoration: its absence is the entire bug described above.

## Two rules that came out of real damage

1. **Never let a second sync mechanism touch this repository.** Syncthing plus git on one
   directory, replicating a live `.git` with no file versioning, is what destroyed the
   vault on 2026-04-29. `./skim check` fails loudly if Syncthing is ever pointed back at
   the workspace.
2. **Never put a runtime-rewritten file in the repository.** `settings.json` is generated
   from `claude-config/settings.template.json` by `machine/bootstrap.sh`, as a COPY, and
   is gitignored. That removes the deadlock's cause rather than remembering to avoid it.

## What Syncthing was retired from

All three folders, on every machine, **removed without "delete on disk"**:
`monitoring_project_obsidian_vault`, `neurosurveillance-private`,
`neurosurveillance-system`. This also permanently ends the dormant hazard documented in
the previous section: the two code folders that still replicated a live `.git` with no
versioning to the paused office PC.

## What has NOT changed

The rig still exists only on `e10ubuntu`. Allego, radiens, XDAQ, Docker, Frigate and
`~/radix/data` are physically there, and from any other machine you drive them with
`ssh e10 '<command>'`, or `ssh e10 -t 'tmux new -As rig'` for anything long running.

## Cutover completed on e10ubuntu, 2026-09-11

Done after the 24.4 h run `allego_0__uid0910-09-00-00` finished (86 GB, stopped 09:23).

| Step | Result |
|---|---|
| Cold tar snapshot of the old vault | `~/vault-snapshots/vault-20260911-0924.tar.gz`, 4725 files |
| `/opt/neurosurveillance/session-daemon` | re-pointed to `~/sleep-recording-skim/neurosurveillance/backend` |
| Daemon | `active`, `/api/health` `healthy: true`, MQTT and Radiens connected, all 4 ports `R_OFF` |
| Claude Code wiring on e10 | `machine/bootstrap.sh`, all 9 links healthy, `settings.json` a real copy |
| Syncthing | all three folders removed from the config (files untouched), service disabled on both machines |
| `vault-git-backup.timer` | disabled; the vault is backed up by `skim push` and the nightly NAS job |
| NAS backup | unit re-pointed, run verified: 325 MB, uploaded and byte-verified, rotation kept 3 |

### The trap this nearly walked into

The rename was NOT just a rename. Five things still hardcoded the old path and every one
of them fails silently:

- **three cron jobs** — the recording watchdog (hourly) and the radix archive watchdog
  (every 20 min) among them;
- **the deploy scripts themselves**, which carried `/home/skimlab/Monitoring_project`
  inside them and therefore carried it into the new repository too;
- **`nas-backup.sh`, which writes its paths WITHOUT a leading slash** (`home/skimlab/...`,
  because `tar -C /` wants them relative), so a search for `/home/skimlab/Monitoring_project`
  does not find it;
- **`deploy/logs/`**, which is gitignored and so did not exist in the clone at all. It holds
  `radix-archive.state` and the archive manifest — the record of what is already on the NAS;
- **the `obsidian-vault` MCP server** in `~/.claude.json`.

> [!quote] Paper-ready
> Moving a working directory is only complete when every hardcoded reference to it has been
> found, including those written without a leading slash and those inside files the version
> control system ignores.

### What the NAS backup now contains

The include list is the single workspace path rather than four named repositories, so it
also captures `claude-config/` and `machine/`. **The raw EEG recordings and the video are
deliberately excluded** — `~/radix/data` is absent from the includes, and `*/radix/data`,
`*.xdat`, `*.mp4` and `storage` are explicit excludes. Raw data is archived separately by
`deploy/radix-archive.sh`. Measured: 325 MB, 2503 files, zero `.xdat`, zero `.mp4`.

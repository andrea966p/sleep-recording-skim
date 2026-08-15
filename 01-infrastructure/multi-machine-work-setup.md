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
| Syncthing peer, office PC | `tcp://100.117.204.8:22000` | Office PC could never reconnect |
| Network attached storage backup script | `100.120.86.10` port 53 | Nightly backup failing since 08-14 |

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
device: **486 files, 153,921,657 bytes**. That excludes `.git`. With `.git` the
vault is 4383 files and about 260 MB.

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

## STILL OPEN

- **The Synology network attached storage backup is BROKEN and needs me to act on the
  Synology itself.** The box is not in the current tailnet at all, `tailscale ping
  100.120.86.10` answers `no matching peer`. I have to log the Tailscale package on
  the Synology into `skimlab.kaist@gmail.com`, then update `NAS_HOST` in
  `neurosurveillance/deploy/nas-backup.sh`. Last good backup was 2026-08-13. Retention
  is 3 days, and pruning only happens on a successful run, so the 08-11, 08-12 and
  08-13 copies should still be on the box.
- The laptop side is not done yet: Syncthing pairing, the SSH key, and cloning
  `claude-portable`.
- The office PC has not been touched. Its Syncthing address is already corrected to
  `dynamic`, so it should find its way back once it is powered on and in the tailnet.
- `claude-portable` has no remote yet. It contains the research memory files, so it
  needs to be a PRIVATE repository.

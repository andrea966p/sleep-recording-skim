---
tags: [procedure, installation, backup, nas, systemd]
created: 2026-05-26
status: active
---

# NAS Backup — Daily Project Snapshot

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A daily automatic backup of everything this project keeps on the NVR — the Obsidian vault, the code, the daemon's config and session records, and the Frigate config — pushed to the lab NAS over Tailscale at midnight. It deliberately **excludes the recorded videos** (they are far too large and live elsewhere).
>
> **Why it exists.** Council item 2.4 and the "human bus factor = 1" warning: today the only copy of the daemon config, the session WAL, and the vault lives on one NVMe in one machine. A disk failure or an accidental wipe (it happened on 2026-04-29) would lose months of provenance and documentation. This makes a recoverable off-machine copy, automatically, with no human in the loop.
>
> **How to read this page.** The backup is a dated tarball kept on the NAS, newest 3 retained. The one-time setup is an SSH key + a systemd timer. Big-picture context: [[01-infrastructure/system-overview|System Overview]].

> [!quote] Paper-ready
> Project state on the NVR (documentation vault, daemon source and configuration, append-only session journal, and Frigate configuration; recorded video excluded) is snapshotted nightly to an off-site network-attached store over an authenticated Tailscale link, with a rolling three-day retention, providing an automated recovery point independent of the acquisition host.

## What it does

- **When:** every day at `00:00` (systemd timer, `Persistent=true` → a missed midnight runs at next boot).
- **What:** one compressed dated tarball `e10_backup_YYYY-MM-DD.tar.gz` (~50 MB).
- **Where:** NAS `Andrea@100.120.86.10:53` → `~/e10_setup_backups/`.
- **Retention:** newest **3** kept; the 4th-oldest is deleted each run.
- **Runs as:** user `skimlab` (every backed-up path is `skimlab`-owned, so no root is needed), key-based SSH with `~/.ssh/id_ed25519`.

> [!note] Transfer uses an ssh pipe, not rsync/scp
> Upload is `ssh … 'cat > file.part && mv …' < tarball` with a byte-count verify. This NAS rejects **rsync** (forced-command/`-e` parsing → password fallback) and OpenSSH-9 **scp** (SFTP backend → `No such file or directory`). The plain ssh pipe is the only reliable primitive here — don't "modernise" it back to rsync/scp.

### Included
| Path | Why |
|------|-----|
| `Monitoring_project_obsidian_vault/` | the documentation vault |
| `neurosurveillance/` (code repo) | backend + frontend source, `.git` history |
| `neurosurveillance-system/` | legacy/aux session-daemon copy |
| `/opt/neurosurveillance/config.yaml` | production daemon config |
| `/opt/neurosurveillance/sessions/` | per-session metadata JSONs |
| `/opt/neurosurveillance/session_wal.db` | append-only session journal (consistent snapshot via SQLite online backup) |
| `/opt/neurosurveillance/exports/**/*.json` | export sidecar provenance (MP4s stripped) |
| `/srv/frigate/{docker-compose.yml,config,mosquitto}` | Frigate + broker config |

### Excluded (bulk / regenerable)
`*.mp4` (132 GB of exports) · `/srv/frigate/storage` (137 GB Frigate cache) · `radiens.log` (3.2 GB) · `frontend/node_modules` + `src-tauri/target` + `venv` (build artifacts) · `__pycache__`/`*.pyc` · SQLite `-wal`/`-shm` sidecars (replaced by the consistent snapshot) · `mosquitto/passwd` (`0600 1883:1883`, unreadable as `skimlab`; the MQTT secret is recoverable from `production-values.md` via `mosquitto_passwd`).

> [!note] Why not `/etc` configs?
> Netdata alert rules and the systemd unit files live under `/etc` (root-owned, not readable as `skimlab`). They are already captured as **golden configs in this vault** (`01-infrastructure/netdata/nvr-alerts-config.md`, the various `deploy/` units), which *are* in the backup. If a future need arises to snapshot raw `/etc`, switch the service to `User=root` and add those paths.

## Files

| Path | Role |
|------|------|
| `neurosurveillance/deploy/nas-backup.sh` | the backup script (builds tarball, uploads, rotates) |
| `neurosurveillance/deploy/nas-backup.service` | systemd oneshot, `User=skimlab` |
| `neurosurveillance/deploy/nas-backup.timer` | daily `00:00` schedule |

## One-time setup

### 1. Install the SSH key on the NAS (interactive — enter the NAS password once)

```bash
ssh-copy-id -p 53 -i ~/.ssh/id_ed25519.pub Andrea@100.120.86.10
```

> [!warning] Synology key-auth gotcha
> Synology DSM only honours key auth if **User Home service** is enabled (Control Panel → User & Group → Advanced → User Home) and the permissions are exact: home dir `0755`, `~/.ssh` `0700`, `~/.ssh/authorized_keys` `0644`. If step 2 still prompts for a password, fix perms on the NAS:
> ```bash
> ssh -p 53 Andrea@100.120.86.10
> chmod 0755 ~ && chmod 0700 ~/.ssh && chmod 0644 ~/.ssh/authorized_keys
> ```

### 2. Verify passwordless SSH + the target folder

```bash
ssh -p 53 -o BatchMode=yes Andrea@100.120.86.10 'echo KEY_OK; ls -d e10_setup_backups'
```
Expected: `KEY_OK` then `e10_setup_backups` — no password prompt.

### 3. Install + enable the timer (sudo)

```bash
sudo cp /home/skimlab/Monitoring_project/neurosurveillance/deploy/nas-backup.service /etc/systemd/system/
```
```bash
sudo cp /home/skimlab/Monitoring_project/neurosurveillance/deploy/nas-backup.timer /etc/systemd/system/
```
```bash
sudo systemctl daemon-reload
```
```bash
sudo systemctl enable --now nas-backup.timer
```

### 4. First run, on demand

```bash
sudo systemctl start nas-backup.service
```
```bash
journalctl -u nas-backup.service -n 30 --no-pager
```
Expected tail: `tarball OK (… MB)` → `uploaded e10_backup_…` → `remaining: e10_backup_…` → `done`.

## Operations

```bash
# next scheduled run
systemctl list-timers nas-backup.timer

# last run result
systemctl status nas-backup.service

# what's on the NAS right now
ssh -p 53 Andrea@100.120.86.10 'ls -lh e10_setup_backups'
```

### Restore
```bash
# pull a snapshot back — use the ssh pipe, NOT scp/rsync (Synology SFTP/rsync quirks)
ssh -p 53 Andrea@100.120.86.10 'cat e10_setup_backups/e10_backup_YYYY-MM-DD.tar.gz' > /tmp/e10_backup_YYYY-MM-DD.tar.gz
# inspect without extracting
tar tzf /tmp/e10_backup_YYYY-MM-DD.tar.gz | less
# extract (paths are relative to /, so extract from a staging dir and copy back deliberately)
mkdir -p /tmp/restore && tar xzf /tmp/e10_backup_YYYY-MM-DD.tar.gz -C /tmp/restore
```
`node_modules`, the Rust `target/`, and the Python `venv` are **not** in the backup — regenerate them with `npm install` / `cargo build` / `python -m venv` + `pip install -r requirements.txt`.

> [!tip] Syncthing
> `deploy/nas-backup.sh` and the unit files live in the synced repo, so they replicate to PC 2. Harmless — PC 2 won't run them unless its own timer is installed.

## Related
- [[01-infrastructure/system-overview|System Overview]]
- [[00-config/production-values|Production Values]] — NAS host/port/user
- [[07-decisions/2026-05-01-llm-council-review|2026-05-01 LLM council review]] — origin of backup item 2.4
- [[07-decisions/2026-05-stabilization-sprint-week-1-plan|stabilization sprint plan]] — sprint that delivered it
- [[02-procedures/installation/watchdog-slack-bridge|watchdog-slack-bridge]] — sibling systemd-bridge deploy pattern

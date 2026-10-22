---
tags: [infrastructure, session-daemon, systemd, production]
created: 2026-02-23
status: production
version: "1.1"
---

# Session Daemon Service

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The systemd unit file that makes the daemon start automatically and keeps it alive across reboots and crashes.
>
> **Why it exists.** Without systemd, the daemon would not survive an NVR reboot — and would not restart if it crashed mid-day. This is the "supervisor" that keeps the daemon up.
>
> **How to read this page.** Skim "Key Configuration" to see the install commands. The two notes (Radiens auth, symlink deployment, and the WAL journal) explain what's safe to touch and what isn't.

> [!quote] Paper-ready
> The session daemon runs as a systemd-managed service under the unprivileged user `skimlab`, restarted automatically on failure with a 10-second backoff and capped at 256 MB resident memory; deployment is via a symlink so repository edits take effect on `systemctl restart`.

## Unit File

- **Path:** `/etc/systemd/system/neurosurveillance-session.service`
- **Service name:** `neurosurveillance-session.service`
- **Runs as:** `skimlab`
- **Working directory:** `/opt/neurosurveillance`

## Key Configuration

- `ExecStart=/opt/neurosurveillance/venv/bin/python /opt/neurosurveillance/session-daemon/daemon.py --config /opt/neurosurveillance/config.yaml`
- `After=docker.service`
- `Restart=always`
- `RestartSec=10`
- `MemoryMax=256M`
- `MemorySwapMax=0`

## Environment

- `PYTHONUNBUFFERED=1`
- `HOME=/home/skimlab`

> [!note] Radiens Auth Mode
> Production uses Cognito session auth via `~/.config/radiens/session.json`.
> `HOME=/home/skimlab` is required so the service can find that session file.
>
> `RADIENS_OFFLINE=1` is **not** enabled in production on this host.

> [!note] Symlink Deployment
> `/opt/neurosurveillance/session-daemon/` is a symlink to the repo at
> `/home/skimlab/Monitoring_project/neurosurveillance/backend/`.
> Edits to the repo's `backend/*.py` files take effect on next daemon restart.

> [!note] WAL Journal at `/opt/neurosurveillance/session_wal.db` (since 2026-05-23)
> The daemon owns a SQLite write-ahead-log database at `/opt/neurosurveillance/session_wal.db` (plus `-wal` and `-shm` companion files). Every session lifecycle event (`START / EXPORT_BEGIN / EXPORT_COMPLETE / ABORT / STALL`) is appended with `synchronous=FULL`, so a `systemctl restart` mid-write loses at most the very last in-flight statement. The file is in WAL mode — leave the three files in place across restarts; do not delete the `-wal`/`-shm` files manually or you risk truncating recent events. Backups: read-only access via `sqlite3 file:/opt/neurosurveillance/session_wal.db?mode=ro` is safe to take while the daemon is running. Full reference: [[session-journal]].

## Install / Reload Commands

```bash
# If updating the service file from the repo:
sudo cp /home/skimlab/Monitoring_project/neurosurveillance/config/neurosurveillance-session.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable neurosurveillance-session.service
sudo systemctl restart neurosurveillance-session.service
```

## Verification

```bash
sudo systemctl status neurosurveillance-session.service
curl http://127.0.0.1:8585/api/status
curl http://127.0.0.1:8585/api/health
```

Expected healthy state:
- `daemon: running`
- `mqtt.connected: true`
- `radiens.connected: true`
- `radiens.recording_state: R_OFF` (idle) or `R_ON` (recording)
- `/api/health` returns `healthy: true`

## Related

- [[architecture|Session Daemon Architecture]]
- [[2026-02-23-session-daemon-radiens-auth-cors|2026-02-23 Radiens Auth + CORS Incident]]

---
tags: [infrastructure, session-daemon, systemd, production]
created: 2026-02-23
status: production
version: "1.1"
---

# Session Daemon Service

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
- [[../../03-troubleshooting/incidents/2026-02-23-session-daemon-radiens-auth-cors|2026-02-23 Radiens Auth + CORS Incident]]

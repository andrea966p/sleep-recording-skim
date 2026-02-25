# NeuroSurveillance

Session recording system for neuroscience sleep research. Synchronizes Frigate NVR video recording with NeuroNexus Radiens EEG/EMG data, and supports manual video recording via Frigate's web UI.

## Repository Structure

```
backend/          Python session daemon (runs on NVR as systemd service)
frontend/         Tauri + React desktop UI (session controller app)
config/           Reference copies of production config and systemd unit
docs/             Development notes
```

## Backend (Session Daemon)

Python service that:
- Polls Radiens for EEG recording state (`R_ON`/`R_OFF`)
- Controls Frigate recording via MQTT
- Auto-detects manual recordings from Frigate UI
- Exports video clips via Frigate HTTP API
- Serves a REST API for the frontend (`127.0.0.1:8585`)

### Deployment

The daemon runs from `/opt/neurosurveillance/session-daemon/` which is a **symlink** to this repo's `backend/` directory:

```
/opt/neurosurveillance/
├── session-daemon -> /home/skimlab/Monitoring_project/neurosurveillance/backend/
├── config.yaml          # Production config (not symlinked)
├── venv/                # Python virtual environment
├── sessions/            # Session JSON sidecars
└── logs/                # Daemon logs
```

Edits to `backend/*.py` take effect on next daemon restart:

```bash
sudo systemctl restart neurosurveillance-session
journalctl -u neurosurveillance-session -f
```

### Dependencies

```bash
source /opt/neurosurveillance/venv/bin/activate
pip install -r backend/requirements.txt
```

## Frontend (Desktop UI)

Tauri v2 + React + TypeScript + TailwindCSS + DaisyUI.

```bash
cd frontend
npm install
npm run dev          # Dev server (hot reload)
npm run tauri dev    # Dev with Tauri window
npm run build        # Production build
```

Requires the backend daemon running at `127.0.0.1:8585`.

## Config

`config/` contains **reference copies** of production files. The actual production config lives at `/opt/neurosurveillance/config.yaml` -- edit that directly on the NVR, not the repo copy.

| File | Production location |
|------|-------------------|
| `config.yaml` | `/opt/neurosurveillance/config.yaml` |
| `neurosurveillance-session.service` | `/etc/systemd/system/neurosurveillance-session.service` |

## Key Paths on NVR

| Path | Contents |
|------|----------|
| `/srv/frigate/storage/exports/` | Exported MP4 video clips |
| `/opt/neurosurveillance/sessions/` | Session JSON sidecars |
| `/opt/neurosurveillance/logs/` | Daemon logs |
| `~/Desktop/Frigate Exports` | Desktop shortcut to exports |

## API Quick Reference

```bash
curl http://127.0.0.1:8585/api/status          # Daemon status
curl http://127.0.0.1:8585/api/health           # Health check
curl http://127.0.0.1:8585/api/session/current   # Active session
curl http://127.0.0.1:8585/api/session/history    # Past sessions
curl http://127.0.0.1:8585/api/session/manual     # Active manual recordings
```

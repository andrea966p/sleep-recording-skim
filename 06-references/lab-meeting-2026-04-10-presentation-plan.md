# Lab Meeting Presentation Outline — NeuroSurveillance System

**Presenter**: Andrea
**Date**: Friday 2026-04-10 (lab meeting)
**Audience**: Lab members
**Duration target**: ~20–25 min + Q&A

## Context

Andrea is presenting progress on the neuroscience surveillance system (Raspberry Pi 5 + Frigate NVR + Python session daemon) to lab members. The system is now production-operational: 4 cameras across 2 Pis, Radiens-synchronized recording, Tauri desktop UI, Netdata+Uptime Kuma monitoring with Slack alerts, storage management with 200 GB EEG reserve, and NAS transfer stubbed pending Tailscale. The talk should cover the 8 topics Andrea listed, grounded only in what is documented in the vault — no fabrication.

This plan is a **structured ladder** for preparing slides and talking points, with file references for every claim so Andrea can back up each statement during Q&A.

---

## Suggested Slide Ladder

### 0. Title & One-Slide Summary (1 min)
- Title: "NeuroSurveillance: an open, low-cost, EEG-synchronized video monitoring system for long circadian recordings"
- One-line pitch: "~$1,174 reproducible 4-chamber system that auto-syncs video to NeuroNexus Radiens EEG, runs 24/7, and is fully monitored."
- Status badge: production-operational as of 2026-04-06.

### 1. Current State of the Setup (3–4 min)
Anchor: `_INDEX.md`, `00-config/production-values.md`, `01-infrastructure/`

- **Hardware**:
  - 2× Raspberry Pi 5 (`192.168.0.11`, `192.168.0.12`), each with dual CSI cameras → 4 cameras total, 1024×768 @ 15fps H.264
  - Waveshare PoE HAT (EEPROM tuned: `PSU_MAX_CURRENT=5000`, `POWER_OFF_ON_HALT=1`)
  - ASUS NUC 14 Pro (`192.168.0.50`): Intel Core Ultra 5 125H, 30.6 GB RAM, 1.9 TB NVMe, Intel Arc iGPU (QSV)
- **Software stack**:
  - go2rtc v1.9.14 on each Pi (RTSP, `rpicam-vid` direct exec — no ffmpeg pipes)
  - Frigate 0.16.1 in Docker, Intel QSV H.264 decode
  - Mosquitto MQTT broker
  - NeuroSurveillance session daemon (Python 3.12 / Flask)
  - Tauri + React 19 desktop UI
- **Hard rules learned the hard way**: H.264 only (H.265 → kernel panics on Pi 5, `05-experiments/completed/`), `KillMode=control-group` mandatory.
- Visual suggestion: network topology diagram (Pi1+Pi2 → NVR → Synology NAS, with Tailscale overlay).

### 2. Alerts & Resource Monitoring (3 min)
Anchor: `01-infrastructure/netdata/nvr-alerts-config.md`, `06-references/monitoring-diagnostics.md`, `04-journal/2026-04/2026-04-03.md`

- **Netdata** on the NVR with **16 custom alerts** (`/etc/netdata/health.d/nvr-alerts.conf`):
  - CPU >85/95%, iowait >40%, RAM <10/5% available, swap >50%, disk >90/95%, inodes >90/98%, Docker container unhealthy/down, CPU package temp >85/95°C.
  - Hysteresis + 15-min recovery delays to suppress flapping.
- **Uptime Kuma**: 7 monitors (go2rtc ×2, Frigate, Mosquitto, Session Daemon, Netdata, Kuma self), status page at `http://192.168.0.50:3001/status/neurosurveillance`. Slack alerting on up + down.
- **Pi-side watchdog**: hardware `RuntimeWatchdogSec=30s` + crash-canary script logging vitals every 30s.
- **NVR-initiated Pi health check**: `/opt/neurosurveillance/pi-monitor.sh` every 2 min — catches silent PoE deaths.
- **Real incident to show impact**: 2026-04-02 thermal spikes (87–92°C) traced to `allegoserver` busy-polling USB — fixed with Intel RAPL 20 W power cap (systemd service). Post-fix baseline: ~58°C. (`03-troubleshooting/incidents/2026-04-02-allegoserver-thermal-spikes.md`)

### 3. Python Session Daemon — Backend / API (3–4 min)
Anchor: `01-infrastructure/session-daemon/architecture.md`

- **Role**: the glue between NeuroNexus Radiens (EEG) and Frigate (video).
- **Architecture** (modules, each with one-line purpose):
  - `daemon.py` — orchestrator + 1 s poll loop
  - `radiens_poller.py` — detects R_OFF↔R_ON transitions via `AllegoClient.get_status()`
  - `frigate_controller.py` — MQTT ON/OFF + Frigate export API with ±2 s buffer
  - `session_manager.py` / `manual_session_manager.py` — per-chamber state, filename generation, JSON sidecars
  - `storage_monitor.py` — background disk sampling, 200 GB EEG reserve enforcement
  - `api.py` — Flask REST on `127.0.0.1:8585`
- **Key design decisions** (worth emphasizing — these are the "why it won't lose your data" points):
  1. **Autonomous core**: if the daemon crashes mid-session, Frigate keeps rolling.
  2. **Metadata optional**: missing metadata → `unknown`, no data lost.
  3. **Multi-chamber independent state** (4 chambers run in parallel).
  4. **Daemon only observes Radiens** — never controls it, researcher stays in charge.
- **Sync latency**: ~1 s (poll interval); ±2 s export buffer guarantees segment capture.
- Mention API surface briefly (`/api/status`, `/api/session/metadata`, `/api/storage`, `/api/health`, `/api/storage/estimate`, `/api/storage/camera-bitrates`).

### 4. Frontend & GUI — How to Use It (3–4 min)
Anchor: `01-infrastructure/session-daemon/frontend-reference.md`, `02-procedures/session-recording-workflow.md`

- **Stack**: Tauri v2 + React 19 + TypeScript + Vite + Tailwind/DaisyUI, dark mode, min 1024×700.
- **Key components**: `ChamberSilo`, `SessionSetup`, `LiveStatus`, `CameraPreview` (1 s Frigate snapshot refresh), `StoragePanel`, `SystemHealth`, `SessionHistory`.
- **Polling hooks**: status 1.5 s, health 5 s, storage 10 s.
- **User workflow (this is the demo slide)**:
  1. Open the desktop app
  2. For each chamber: enter Mouse ID, pick Recording Type, pick Your Name → *Set Metadata*
  3. Start EEG in Radiens → video auto-starts on all 4 cameras
  4. Run experiment (daemon is silent)
  5. Stop EEG in Radiens → video auto-stops and exports
  6. Check `SessionHistory` panel
- **Manual override path**: Frigate UI Record button → daemon detects, inherits pending metadata, 5 s min duration filter.
- **Settings modal**: cameras, recording types, lab members, Frigate URL (localStorage).
- Suggested: one live screenshot of the Tauri window with all 4 ChamberSilos visible.

### 5. Storage Management & NAS Transfer (2–3 min)
Anchor: `02-procedures/installation/storage-management-implementation.md`

- **Layout**:
  - `/srv/frigate/storage/recordings` — raw Frigate segments
  - `/srv/frigate/storage/exports` — temp Frigate exports
  - `/opt/neurosurveillance/exports/{user}/{mouseID}/{YYYY-MM-DD}/YYMMDDHHMM_mouseID_type.mp4` (+ JSON sidecar)
- **StorageMonitor**: `os.statvfs()` every 30 s, category scan with 5-min TTL, atomic dict swap.
- **Hard EEG reserve**: 200 GB protected — `can_start_recording()` returns False below the line.
- **Capacity math** (be explicit — lab will ask):
  - ~1.7 Mbps actual per camera (target 1.5 Mbps + VBR overhead)
  - ~18 GB/camera/day → ~72 GB/day for 4 cams
  - 1.9 TB NVMe ÷ 7-day retention ≈ ~504 GB used, ~26 days of headroom
- **Bitrate sync button**: queries go2rtc `/api/streams` on both Pis and parses actual `--bitrate` from `rpicam-vid` exec.
- **NAS transfer**: **configured, NOT yet deployed** — Synology at `100.120.86.10`, pending Tailscale VPN setup. Be transparent about this.

### 6. Strengths vs. Recent Publications (3 min)
Anchor: `06-references/progress-meeting-2026-03-12.md`

Comparison table from the progress meeting — show on one slide:

| System | Cost | EEG sync | Open source |
|---|---|---|---|
| **NeuroSurveillance (ours)** | ~$1,174 | Radiens API, ~1 s, ±2 s buffer | Yes |
| MouseVUER (2024, Nature Sci Rep) | $2–3k | none | Yes |
| OpenVEEG (2018) | $5–10k | ms-level, OpenEphys | Partial |
| Noldus EthoVision | $15–20k | limited | No |
| Clever Sys HomeCageScan | $10–15k | none | No |
| SIESTA (2025) | — | ECoG/EMG only, no video | research code |

**Novel contributions to highlight**:
1. First open-source Frigate ↔ NeuroNexus Radiens auto-sync via AllegoClient.
2. Multi-chamber independent metadata (4 mice, 4 contexts, one app).
3. MQTT pub/sub → loose coupling, fail-safe recording.
4. Full operational documentation (38+ vault pages incl. incidents).
5. ~$1.2 k vs. $5–20 k commercial systems, fully reproducible.

Key citations (all in progress meeting doc): MouseVUER 2024, OpenVEEG 2018, SIESTA 2025, SAGER 2025, Spyglass 2024, FERAL 2025, Lightning Pose 2024.

### 7. Future: EEG↔Video Hardware Sync via XDAQ (2–3 min)
Anchor: `06-references/progress-meeting-2026-03-12.md` (next-steps section)

- **Current sync**: software-level, ~1 s latency, ±2 s export buffer — good enough for behavior, not for ms-level spike alignment.
- **Planned upgrade**: wire the Pis' GPIO to the XDAQ digital I/O → hardware-triggered frame markers, enabling **per-frame temporal alignment** between video and EEG/EMG.
- **Preparatory work already done**:
  - 200 GB EEG reserve enforced in storage monitor
  - Session daemon architecture is Radiens-agnostic (observer only)
  - Export API buffered ±2 s so no frames are lost at the edges
- **Validation to-dos** (from 2026-03-12 meeting):
  - Post-export `ffprobe` integrity check (prompted by 2026-03-06 19 GB corruption incident)
  - Measure actual Radiens R_ON → first Frigate frame latency
  - Long-term stability data from multi-day runs
- **Longer term**: PostgreSQL session DB, NWB export for DANDI, dual-modality (EEG/EMG + FERAL video) sleep scoring.

### 8. Why This Matters for Long / Circadian Recordings (2–3 min)
Anchor: `01-infrastructure/raspberry-pi/watchdog-monitoring.md`, `03-troubleshooting/incidents/*`

Frame it as: **circadian studies = multi-day continuous runs where a single crash ruins a week of data**. This system is engineered for that failure mode.

Stability features for 24/7 operation:
- Hardware watchdog (`RuntimeWatchdogSec=30s`) auto-reboots hung Pis.
- Crash-canary logging vitals every 30 s (temperature, throttle, CPU, memory) → pre-crash forensics.
- NVR-initiated ping every 2 min detects PoE power failures (silent Pi deaths).
- `apt-mark hold` on Docker packages → no surprise Frigate restarts from GUI updater (lesson from 2026-04-01 unexpected-recording incident).
- `systemd Restart=always` on go2rtc and session daemon.
- Fail-safe video: MQTT recording state persists ON if daemon crashes.
- Thermal headroom: RAPL 20 W cap gives 17°C margin before alerts (lesson from 2026-04-02).
- **Track record**: 30+ day continuous uptime achieved in Feb 2026 MPEG-TS test; stable since 2026-02-19 after PMIC/EEPROM hardening.
- Storage math supports it: 1.9 TB NVMe ≈ 26 days of 4-cam recording before hitting retention.

### 9. Roadmap & Next Steps (1–2 min)
From the 2026-03-12 progress meeting:

- **Short-term (2–4 wk)**: `ffprobe` post-export validation; finish Tailscale NAS transfer deploy.
- **Medium-term (1–3 mo)**: automated sleep scoring (collab w/ Prof. Kim Daewook lab), FERAL video classifier, video-EEG latency measurement, PostgreSQL session DB, multi-headstage support.
- **Long-term (3–6 mo)**: NWB export → DANDI archive, dual-modality sleep scoring pipeline, replication guide + methods paper (target: *J. Neurosci. Methods* or *HardwareX*).

### 10. Q&A + Backup Slides (as needed)
Keep these ready but don't show by default:

- **Incident gallery** (proves robustness): PMIC PoE death 2026-02-19, MP4 corruption 2026-03-06, Radiens auth 2026-02-23, thermal spikes 2026-04-02, unexpected recordings 2026-04-01, zombie `rpicam-vid` 2026-02-11.
- **Full API endpoint table**.
- **config.yaml storage section**.
- **Full Netdata alert list with thresholds**.
- **Frigate config.yml highlights** (retention, QSV, record.enabled).

---

## Additional Things Worth Mentioning (Andrea asked for suggestions)

1. **Operational documentation as a deliverable** — 38+ vault pages including golden configs, incident reports, and procedures. Lab members can reproduce/repair the system without Andrea. Worth a single slide.
2. **Cost transparency** — ~$1,174 BOM vs. $5–20k commercial; good slide for a lab meeting audience thinking about their own rigs.
3. **Failure-mode honesty** — briefly acknowledge: NAS transfer not yet deployed; ms-level sync not yet hardware; no PostgreSQL yet. Being upfront builds trust more than glossing.
4. **Demo if logistics allow** — live open the Tauri UI on the projector showing the 4 ChamberSilos + storage panel. Much stronger than screenshots.
5. **Acknowledgments slide** — lab collaborators (Prof. Kim Daewook's lab for sleep scoring), any funding.

---

## Critical Files to Reference While Preparing

- `_INDEX.md` — vault home, quick status
- `00-config/production-values.md` — IPs, paths, camera IDs
- `01-infrastructure/session-daemon/architecture.md` — daemon internals
- `01-infrastructure/session-daemon/frontend-reference.md` — UI reference
- `01-infrastructure/netdata/nvr-alerts-config.md` — alert definitions
- `02-procedures/session-recording-workflow.md` — user-facing workflow
- `02-procedures/installation/storage-management-implementation.md` — storage details
- `06-references/progress-meeting-2026-03-12.md` — roadmap, citations, comparisons
- `06-references/monitoring-diagnostics.md` — monitoring query commands
- `03-troubleshooting/incidents/2026-04-02-allegoserver-thermal-spikes.md` — most recent incident (good story)
- `04-journal/2026-04/2026-04-03.md` — latest status snapshot

## Verification (how to sanity-check before the talk)

- Open the Tauri UI and confirm all 4 ChamberSilos are green (System Health badges).
- `curl http://192.168.0.50:5000/api/stats` — Frigate stats for the live-demo backup.
- `curl http://192.168.0.11:1984/api/streams` and `http://192.168.0.12:1984/api/streams` — confirm both Pis healthy.
- Check Uptime Kuma status page: `http://192.168.0.50:3001/status/neurosurveillance`.
- `curl http://127.0.0.1:8585/api/health` on the NVR — 200 OK means daemon + Radiens + MQTT all connected.
- Re-skim `06-references/progress-meeting-2026-03-12.md` the night before — most of slide 6 and 9 come from it verbatim.
3e54r6ty7ert
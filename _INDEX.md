---
tags: [index, navigation, home]
---

# NeuroSurveillance System Documentation

> [!abstract] Start here
> New to this vault? Read [[SYSTEM-OVERVIEW|the one-page system overview]] first — it explains what NeuroSurveillance is, what changed in the recent stabilization sprint, and where to read more.
> For a deeper Q&A walkthrough with durability guarantees and a glossary: [[01-infrastructure/system-overview|the deeper overview]].
> Onboarding a new lab member: [[02-procedures/new-researcher-onboarding|new-researcher-onboarding]].

> [!info] Quick Access
> | Service | URL |
> |---------|-----|
> | **Frigate** | http://192.168.0.50:5000 |
> | **go2rtc (Pi 1)** | http://192.168.0.11:1984 |
> | **go2rtc (Pi 2)** | http://192.168.0.12:1984 |
> | **Session Daemon** | http://127.0.0.1:8585 (NVR localhost) |
> | **Netdata (NVR)** | http://192.168.0.50:19999 |
> | **Uptime Kuma** | http://192.168.0.50:3001 |
> | **Status Page** | http://192.168.0.50:3001/status/neurosurveillance |
> | **Config** | [[00-config/production-values]] |
> | **Tasks** | [[00-config/task-dashboard]] |

---

## Documentation Map

### [[00-config/production-values|Configuration]]
Production IPs, usernames, paths, and settings.

### Infrastructure

**Raspberry Pi:**
- [[01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]
- [[01-infrastructure/raspberry-pi/golden-systemd-service|systemd Service]]
- [[01-infrastructure/raspberry-pi/golden-boot-config|Boot Hardening]]
- [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog & Monitoring]]

**Frigate NVR:**
- [[01-infrastructure/frigate/docker-compose|Docker Compose]]
- [[01-infrastructure/frigate/config-yml|config.yml]]

**Radiens / Allego software:**
- [[06-references/radiens-software-reference|⭐ Radiens Software — PRIMARY Reference (Allego + Videre)]] — **main software reference; embeds the full 177-page NeuroNexus manual + our load-bearing facts (mode, channel select, no in-GUI rename)**
- [[02-procedures/first-headstage-connection|First Headstage Connection — bring-up + channel map]] ✅ resolved 2026-06-19
- [[02-procedures/signal-mapping-guide|⭐ Signal Mapping Guide — which channel is which electrode (EEG/EMG, step-by-step for any operator)]]
- [[02-procedures/signal-quality-and-grounding|⭐ Signal Quality & Grounding — fix the ground, then decide if the signal is good enough to record]]

**Hardware Sync (XDAQ GPIO):**
- [[01-infrastructure/hardware-sync/xdaq-core-gen1-ubuntu-driver|⭐ XDAQ Core (Gen-1) — Ubuntu Driver Setup + Verified State (2026-05-29)]] — **current source of truth; supersedes Core2 assumptions below**
- [[01-infrastructure/hardware-sync/overview|Overview & Architecture]] ⚠️ Core2-era
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide & BOM]]
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service (Golden Config)]]
- [[01-infrastructure/hardware-sync/radiens-api-reference|Radiens API — Digital I/O Reference]]
- [[01-infrastructure/hardware-sync/xdaq-core2-manual-reference|XDAQ Core2 Manual Reference (authoritative pinout + specs)]]
- [[01-infrastructure/hardware-sync/neuronexus-inquiry-email|NeuroNexus / Kontex Inquiry & Replies]]
- [[01-infrastructure/hardware-sync/kontex-developer-portal-notes|Kontex Developer Portal Notes (libxdaq / pylibxdaq / Linux Thunderbolt)]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]

**Session Daemon:**
- [[01-infrastructure/system-overview|System Overview — Q&A and glossary]]
- [[01-infrastructure/session-daemon/architecture|Architecture & Design]]
- [[01-infrastructure/session-daemon/session-journal|Session Journal — WAL (added 2026-05-23)]]
- [[01-infrastructure/session-daemon/reconciler|Reconciler — nightly WAL ↔ Frigate cross-check (added 2026-05-24)]]
- [[01-infrastructure/session-daemon/frontend-reference|Frontend Reference]]
- [[01-infrastructure/session-daemon/session-service|Systemd Service]]

**Monitoring & Alerting:**
- [[01-infrastructure/netdata/nvr-alerts-config|Netdata NVR Alerts (Golden Config)]]
- [[02-procedures/installation/monitoring-setup|Monitoring Setup Procedure]]
- [[02-procedures/installation/watchdog-slack-bridge|Watchdog → Slack Bridge (added 2026-05-25)]]
- [[03-troubleshooting/emergency-runbook|Emergency Runbook — first 10 min]]

### Procedures
- [[02-procedures/installation/new-pi-setup|New Pi Setup]]
- [[02-procedures/session-recording-workflow|Session Recording Workflow]]
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]
- [[02-procedures/installation/storage-management-implementation|Storage Management System]] ✅
- [[02-procedures/new-researcher-onboarding|New Researcher Onboarding]] — day-0 access + first-recording walkthrough
- [[02-procedures/bus-factor-runbook|Bus-Factor Runbook]] — "Andrea is unreachable" emergency operator guide (added 2026-05-28)

### Troubleshooting

**By Symptom:**
- [[03-troubleshooting/symptoms/no-frames-received|No frames received]]
- [[03-troubleshooting/symptoms/system-freeze-ssh-hang|System freeze / SSH hang]]
- [[03-troubleshooting/symptoms/frigate-high-cpu|Frigate 100% CPU]]
- [[03-troubleshooting/symptoms/docker-memory-crash|Docker memory crash]]

**Incident Log:**
- [[03-troubleshooting/incidents/|Incidents]]
- [[03-troubleshooting/incidents/2026-02-23-session-daemon-radiens-auth-cors|2026-02-23 Session Daemon Auth + CORS]]

### Journal
- [[04-journal/|Daily Notes]]

### Experiments
- [[05-experiments/completed/h265-encoding-failure|H.265 Failure (DO NOT USE)]]
- [[05-experiments/completed/2026-02-11-mpegts-container-test|MPEG-TS Container Test (adopted v5.2)]]
- [[05-experiments/active/|Active Experiments]]

### References
- [[06-references/monitoring-diagnostics|Monitoring Diagnostics]] — Netdata/Uptime Kuma query commands for troubleshooting
- [[06-references/command-cheatsheet|Command Cheatsheet]]
- [[06-references/video-parameters|Video Parameters]]

### Decisions & Reviews
- [[07-decisions/2026-05-01-llm-council-review|2026-05-01 LLM Council Review]] — full advisor responses, peer reviews, chairman synthesis, staged plan
- [[07-decisions/2026-05-stabilization-sprint-week-1-plan|2026-05 Stabilization Sprint Week 1 — Plan + live status]] — single source of truth for sprint-item status

### Archive
- [[99-archive/notion-import-2025-02/|Notion Import]]

---

## System Status

| Component | IP | Status |
|-----------|------|--------|
| **Pi 1** | 192.168.0.11 | Online |
| **Pi 2** | 192.168.0.12 | Online |
| **go2rtc (Pi 1)** | :1984 | Online |
| **go2rtc (Pi 2)** | :1984 | Online |
| **Frigate** | 192.168.0.50:5000 | Online |
| **Session Daemon** | 127.0.0.1:8585 | Healthy (daemon + MQTT + Radiens connected) |
| **Netdata (NVR)** | 192.168.0.50:19999 | Active (16 NVR alerts, Slack notifications) |
| **Netdata (Pi 1)** | 192.168.0.11:19999 | Active |
| **Netdata (Pi 2)** | 192.168.0.12:19999 | Active |
| **Uptime Kuma** | 192.168.0.50:3001 | Active (7 monitors, Slack alerting) |
| **nvr-mqtt-slack** | systemd (NVR) | Active (watchdog stalls → Slack; added 2026-05-25) |

---

## Quick Commands

```bash
# Pi health check
ssh skimlab@192.168.0.11 'vcgencmd measure_temp && systemctl status go2rtc'

# Frigate logs
ssh skimlab@192.168.0.50 'docker logs frigate --tail 20'

# Stream test
ffprobe rtsp://192.168.0.11:8554/pi_cam_0
```

---

## Emergency

1. Check [[03-troubleshooting/symptoms/|Symptom Index]]
2. Run: `sudo systemctl restart go2rtc.service`
3. See [[06-references/command-cheatsheet|Command Cheatsheet]]

---

*Last updated: 2026-06-19 (🎉 **first headstage detected — electrophysiology first light.** Intan RHD2216 enumerates on the XDAQ Core Gen-1, streaming shows signal. Root cause of the prior block was a wrong Allego system mode (`SMARTBOX_PRO`); correct = **"XDAQ One (G1) with XR Headstage"** / `XDAQ_ONE_REC` — see [[02-procedures/first-headstage-connection]]. No hardware fault, no RMA). Prev 2026-05-29 (XDAQ unit identified as Gen-1 Core / Opal Kelly USB — NOT Core2; Ubuntu driver solved via plugdev udev rule, Allego detects device; new authoritative doc `xdaq-core-gen1-ubuntu-driver`, Core2 docs banner-flagged, KC email trimmed). Prev 2026-05-28 (Phase 4.6 reconciler→Slack enabled in bridge; vault restructure — `07-decisions/` section added; council + sprint plan extracted out of `04-journal/2026-05-01.md` and `2026-05-20.md` into their own decision docs; daily journals get `created:` frontmatter for stable sort; bus-factor runbook shipped — Phase 6 council Stage 3.4 closed)*

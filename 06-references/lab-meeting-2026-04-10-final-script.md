---
tags: [presentation, lab-meeting, script]
date: 2026-04-10
---

# Lab Meeting Script — 2026-04-10

Terse talking points per slide. You do the talking.

## Slide 1 — Title
- Greet, name, date
- Pitch: open, low-cost, EEG-synced video for long circadian recordings
- Status: production-operational since 2026-04-06

## Slide 2 — At a Glance
- ~$1,174 total hardware (PC included)
- 4 cams across 2 Pi nodes, 24/7
- ~1 s sync, 16 alerts, 38+ doc pages
- Frame the four words: reproducible, open-source, modular, scalable
- "Limit is budget, not architecture"

## Slide 3 — Hardware Recap
- Quick read: Pi 5 specs (Cortex-A76, RP1 I/O)
- OV5647 cam: 5 MP, NoIR, IR LEDs, ~1–3 m range
- Don't dwell — this is reference

## Slide 4–6 — (blank/visual)
- Show photos / let visuals breathe, no script

## Slide 7 — Agenda
- 8 sections; ~25 min + Q&A

## Slide 8 — Section 1: Current State
- Transition slide

## Slide 9 — System Topology
- Walk left→right: chambers → 2 Pis (.11, .12) → NUC NVR (.50) → NAS (Tailscale pending)
- RTSP H.264 from each Pi
- Frigate + Mosquitto + daemon + monitoring all on one NUC
- Slack alerts on the side

## Slide 10 — Hardware
- 2× Pi 5 + dual CSI = 4 cams, 1024×768@15fps, PoE HAT, EEPROM hardened
- ASUS NUC: Core Ultra 5, Arc iGPU for QSV decode, 30 GB RAM, 1.9 TB NVMe
- NeuroNexus xDAQ + Radiens, AllegoClient SDK, ~1 s sync via daemon
- Synology NAS — long-term tier, Tailscale pending

## Slide 11 — Software Stack
- go2rtc on each Pi: RTSP via rpicam-vid direct exec
- Frigate dockerized w/ QSV
- Mosquitto = pub/sub broker
- Daemon = Python/Flask glue
- Tauri+React UI
- Netdata+Kuma → Slack
- Punchline: containerized or systemd-managed, nothing ad-hoc

## Slide 12 — Hard Rules
- Each rule = scar tissue from a real incident
- H.264 only — H.265 → kernel panics
- KillMode=control-group — zombie rpicam-vid fighting for camera
- rpicam-vid direct exec — single point of failure, no cascade
- apt-mark hold — GUI updater silently restarted Frigate
- MPEG-TS — MP4 lost 19 GB on mid-stream failure; TS = chunked, recoverable
- Result: 30+ day uptime

## Slide 13 — Section 2: Alerts & Monitoring
- Transition

## Slide 14 — Why Instrument
- Silent failures > loud ones (2 AM crash = 8 h lost)
- Pre-crash forensics need continuous logs, not reactive
- Multiple failure modes = multiple sensors

## Slide 15/16 — Netdata 16 Alerts
- All clear as of 2026-04-06
- Quick categories: CPU, iowait, RAM, swap, disk, inodes, temp, containers
- Hysteresis + 15-min recovery delays = zero flapping

## Slide 17/18 — Uptime Kuma
- 7 monitors: 2 go2rtc + Frigate + Mosquitto + Daemon + Netdata + self
- Public status page URL on screen
- Slack on up AND down

## Slide 19 — What is a Watchdog
- Define: code that notices when something stopped and acts
- Four of them — each catches a different silent failure class
- Kernel hang / thermal slow-death / PoE latch / process crash

## Slide 20 — The Four Layers
- HW watchdog: kernel timer, reboots if kernel itself hangs
- crash-canary.sh: temp/throttle/load/mem every 30 s — pre-crash forensics
- pi-monitor.sh: NVR pings each Pi every 2 min — only layer that catches PoE death
- systemd Restart=always: fine-grained per-process recovery
- Need all 4 — different failure classes

## Slide 21 — Thermal Spike Incident
- Symptom: 87–92°C, spikes to 100°C every 35–40 min
- Investigation: journalctl + htop + RAPL + Netdata
- Found: allegoserver busy-polling USB at 109% CPU
- Fix: cpu-power-cap.service, RAPL 20 W cap
- Result: baseline 58°C, 17°C headroom
- Punchline: caught BEFORE data loss — that's the point

## Slide 22 — Section 3: Daemon
- Transition

## Slide 23 — The Glue
- Start EEG in Radiens → daemon notices in 1 s → Frigate records the right cam
- Stop EEG → cams stop, exports w/ JSON sidecar
- Runs as systemd service on NVR
- Python 3.12, paho-mqtt, AllegoClient
- Flask API on localhost:8585

## Slide 24 — Architecture Diagram
- Walk modules: poller → manager → controller → storage → API
- Orchestrator = 1 s loop
- Outputs: Frigate recordings, exports w/ sidecars, UI

## Slide 25 — 4 Design Decisions
- Autonomous core: daemon dies → Frigate keeps recording (MQTT state sticks)
- Metadata optional: forget Mouse ID → "unknown", rename later, no data lost
- Multi-chamber independent: 4 parallel state machines
- Daemon only OBSERVES Radiens — researcher stays in charge

## Slide 26 — Module Table
- Read briefly, emphasize one-job-each
- Highlight manual_session_mgr (5 s min duration filter — accidental click protection)

## Slide 27 — Sync Tightness
- 1 s poll, ±2 s buffer, 4 channels
- HONEST: good for behavior (locomotion, sleep posture, grooming)
- NOT good for spike-to-frame alignment — that's the XDAQ upgrade later

## Slide 28 — REST API
- Brief tour: status, metadata, history, health, storage
- All localhost — UI talks to it

## Slide 29 — Section 4: GUI
- Transition — say you'll show live demo if time

## Slide 30 — Tauri Stack
- Tauri v2 + React 19 + TS + Vite
- Tailwind/DaisyUI, dark mode
- Cross-platform .deb build

## Slide 31 — 7-Step Workflow
- Walk steps 1→7
- Stress: researcher does normal Radiens workflow, daemon is silent
- Verification = SessionHistory panel

## Slide 32 — UI Components
- Name each silo: ChamberSilo, SessionSetup, LiveStatus, Preview, Storage, Health, History
- Polling cadences at bottom

## Slide 33 — Manual Override
- Frigate UI → Record button → daemon detects in 1 s
- Inherits pending metadata
- Same filename convention regardless of trigger
- 5 s min duration filter

## Slide 34 — Section 5: Storage
- Transition

## Slide 35 — Where Data Lives
- Two trees: /srv/frigate (raw) and /opt/neurosurveillance (organized)
- Filename: YYMMDDHHMM_mouseID_type.mp4
- Organized by user/mouse/date

## Slide 36 — Capacity Math
- 1.7 Mbps measured per cam
- 18 GB/cam/day → 72 GB/day @ 4 cams
- 1.9 TB NVMe → ~26 days headroom
- 200 GB hard reserve
- 7-day retention → ~504 GB working set

## Slide 37 — StorageMonitor
- Cheap statvfs every 30 s
- Background category tally — knows what's filling disk
- HARD rule: no recording starts below 200 GB (EEG protected)
- Sync Bitrates button: queries Pis for actual bandwidth, not estimate
- Punchline: video can never starve EEG

## Slide 38 — NAS Honest Status
- Configured, not live
- Blocker: Tailscale to NAS
- 2–4 wk roadmap
- Be transparent — builds trust

## Slide 39 — Section 6: Lit Comparison
- Transition

## Slide 40 — MouseVUER Table
- Walk row by row
- Their advantage: depth/3D posture (RealSense)
- Our advantages: any rack, no cage modification, no fabrication, fewer SBCs, monitoring, reliability data, retention policy, cost transparency
- Their cost: not published. Ours: ~$76/chamber edge

## Slide 41 — Sync & Openness Honest
- OpenVEEG sub-ms sync IS tighter — concede it
- BUT: NI DAQ + BlackMagic PCIe + C++ extension = high friction
- Ours: hardware-agnostic observer, modern tooling
- MouseVUER: Python 3.4 + VS 2010 on Windows
- Edge isn't openness — it's modern tooling + production wrapper

## Slide 42 — Six Novel Contributions
- Acquisition-agnostic: swap radiens_poller.py for OpenEphys/Intan/Blackrock — rest unchanged
- First open Frigate↔Radiens auto-sync
- Per-chamber independent metadata
- MQTT loose coupling
- Production wrapper (16 alerts, 7 monitors, Slack, vault) — none of 4 papers have this
- Cost: $1.2 k vs $5–20 k commercial

## Slide 43 — Key References
- Quick name-drops, don't read in full
- Mention Salem is same first author for both 2020 + 2024 papers
- Spyglass is the DANDI angle for the roadmap

## Slide 44 — Section 7: Hardware Sync
- Transition

## Slide 45 — From Polling to Triggering
- Current: ~1 s software polling, ±2 s buffer — behavior-grade
- Planned: Pi GPIO → XDAQ digital I/O → per-frame markers
- One step beyond OpenVEEG's LSL approach

## Slide 46 — Why Upgrade Is Easy
- 200 GB reserve already in place
- Daemon already observer-only
- Export already buffered ±2 s
- Sidecar JSON schema already reserves hw-sync fields
- Per-chamber state already scales to more headstages

## Slide 47 — Validation TODOs
- ffprobe post-export integrity check (lesson from 19 GB corruption)
- Measure real R_ON → first-frame latency
- Multi-day stability data
- Longer horizon: PostgreSQL, NWB/DANDI, dual-modality sleep scoring

## Slide 48 — Section 8: Circadian
- Transition

## Slide 49 — Why It Matters
- One crash = a week of data
- Silent failure is worse than loud failure
- System optimizes BOTH uptime AND observability
- "Research demo vs research instrument"

## Slide 50 — What Keeps It Running
- Run through 7 tiles: HW watchdog, canary, ping, apt-mark hold, Restart=always, MQTT fail-safe, RAPL thermal margin
- Each maps to a real incident

## Slide 51 — Track Record
- 30+ day uptime in Feb MPEG-TS test
- 0 active alerts as of 2026-04-06
- ~26 days storage headroom
- Stable since 2026-02-19 PMIC fix; thermal stable since 2026-04-03

## Slide 52 — Solved Failures Table
- Don't read all — pick 2–3 to narrate
- Suggested: H.265 panic, PMIC latch, 19 GB corruption, thermal spike
- Frame as: every row hardened the system

## Slide 53 — Section 9: Roadmap
- Transition

## Slide 54 — What's Next
- Short (2–4 wk): ffprobe, NAS Tailscale, apt-mark verify
- Medium (1–3 mo): FERAL classifier, latency validation, PostgreSQL, multi-headstage
- Long (3–6 mo): NWB→DANDI, sleep scoring, replication guide, methods paper

## Slide 55 — Documentation as Deliverable
- 38+ pages: configs, procedures, incidents, references
- Lab can repair without me in the room
- Every hard rule → traceable incident
- Single source of truth via {VARIABLE} system

## Slide 56 — Summary
- Production-operational, fail-safe, monitored, documented, ~$1,174
- Built for multi-day runs
- Roadmap: ms-level hw sync + sleep scoring
- Reproducible methods

## Slide 57 — Thanks / Q&A
- Thank lab, invite questions
- Have backup: incident details, full API table, Frigate config, full alert list

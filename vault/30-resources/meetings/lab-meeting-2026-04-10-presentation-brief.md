---
type: meeting
area: video-nvr
status: done
---
# NeuroSurveillance — Lab Meeting Presentation Brief

> **Purpose of this document.** A detailed, slide-by-slide briefing intended to be fed to an AI presentation generator (Gamma, Tome, Beautiful.ai, etc.). It follows the structure of `lab-meeting-2026-04-10-presentation-plan.md` but expands every section with full talking points, numbers, citations, and visual suggestions. Source of all facts: this Obsidian vault — no fabrication.
>
> **Audience.** Lab members at the Friday 2026-04-10 lab meeting. Mixed: some are wet-lab neuroscientists, some have technical/engineering background. Assume zero familiarity with Frigate, MQTT, or Tauri.
>
> **Tone.** Confident but honest. Lead with what works. Acknowledge what's not yet deployed. Use concrete numbers and incident stories — they are more persuasive than abstract claims.
>
> **Total target.** ~25–30 slides, 20–25 minutes + Q&A.
>
> **Visual style.** White background, default sans-serif fonts, blue accent (#1F6FEB), minimal decoration. Diagrams over bullet walls wherever possible.

---

## SLIDE 0 — Title

**Title:** NeuroSurveillance
**Subtitle:** An open, low-cost, EEG-synchronized video monitoring system for long circadian recordings
**Footer:** Andrea · Lab Meeting · Friday 2026-04-10
**Status badge:** Production-operational as of 2026-04-06

**Visual:** Centered title, accent-color status badge above the title. No logo. Optional: small monochrome icon set (camera + brain wave) at the bottom.

**Speaker note:** Open by saying this is a progress update on a system that started as troubleshooting a broken Pi setup in February and has become a reproducible, production-grade research instrument.

---

## SLIDE 1 — At a Glance (one-slide pitch)

**Headline:** What I built and why it matters

**Six big-number stats (grid layout):**
| Stat | Label |
|------|-------|
| **~$1,174** | Total hardware cost |
| **4** | Cameras across 2 Pi nodes |
| **24/7** | Continuous operation |
| **~1 s** | EEG ↔ video sync latency |
| **16** | Custom monitoring alerts |
| **38+** | Vault documentation pages |

**One-line pitch:** "A reproducible 4-chamber video system that auto-syncs to NeuroNexus Radiens EEG, runs 24/7, alerts on Slack, and is fully documented and open-sourceable."

**Speaker note:** Resist the urge to dive into details. This slide answers "what is it?" in 30 seconds.

---

# § 1 — Current State of the Setup

## SLIDE 2 — Section divider: Current State

**Visual:** Large "§ 1" in accent color, "Current State of the Setup" as title.

---

## SLIDE 3 — System Topology (DIAGRAM SLIDE)

**Headline:** System Topology

**Visual:** Network diagram (left → right):
- Left: two Pi 5 boxes stacked vertically
  - Pi 1 (`192.168.0.11`) — pi_cam_0, pi_cam_1
  - Pi 2 (`192.168.0.12`) — pi_cam_2, pi_cam_3
- Center: ASUS NUC 14 Pro (`192.168.0.50`) labeled "NVR" — contains Frigate, Mosquitto, Session Daemon, Netdata, Uptime Kuma, 1.9 TB NVMe
- Right: Synology NAS (`100.120.86.10`) drawn dashed with "Tailscale pending" caption
- Arrows: Pis → NVR labeled "RTSP H.264" · NVR → NAS labeled "rsync (planned)"
- Top-right: small cloud labeled "Slack" with arrow from NVR (alerts)
- Top-right: small icon labeled "Tailscale" overlaying for remote access

**Caption under diagram:** 1024×768 @ 15 fps · H.264 only · 4 cameras · 2 Pi nodes → 1 NVR → NAS

---

## SLIDE 4 — Hardware Detail

**Headline:** Hardware

**Bullets (with sub-bullets):**
- **2× Raspberry Pi 5** with dual CSI cameras → 4 cameras total
  - Pi 1: `192.168.0.11` — user `skimlab` — cameras `pi_cam_0`, `pi_cam_1`
  - Pi 2: `192.168.0.12` — user `pi2` — cameras `pi_cam_2`, `pi_cam_3`
  - Resolution: 1024×768 @ 15 fps, H.264 baseline profile
  - Powered by Waveshare PoE HAT
  - EEPROM hardened: `PSU_MAX_CURRENT=5000`, `POWER_OFF_ON_HALT=1` (after 2026-02-19 PMIC death incident)
- **ASUS NUC 14 Pro (NUC14RVH-B)**
  - IP `192.168.0.50`, hostname `e10ubuntu`
  - CPU: Intel Core Ultra 5 125H (Meteor Lake, 14 cores)
  - GPU: Intel Arc Graphics iGPU with QSV H.264 hardware decode
  - RAM: 30.6 GB
  - Storage: 1.9 TB NVMe
  - OS: Ubuntu 24.04 LTS, kernel 6.17.0-14-generic
- **Synology NAS** (storage tier, not yet wired in via Tailscale)

**Visual:** Photo or icons of each device on the left, specs as bullets on the right.

---

## SLIDE 5 — Software Stack (CARD GRID)

**Headline:** Software Stack

**Six cards, 2×3 grid:**

| Card | Detail |
|------|--------|
| **go2rtc v1.9.14** | RTSP streaming on each Pi via `rpicam-vid` direct exec — no ffmpeg pipes |
| **Frigate 0.16.1** | Dockerized NVR with Intel QSV H.264 hardware decode |
| **Mosquitto MQTT** | Pub/sub broker for recording control (`frigate/{camera}/recordings/set`) |
| **Session Daemon** | Python 3.12 / Flask — glue between Radiens and Frigate |
| **Desktop UI** | Tauri v2 + React 19 + TypeScript |
| **Netdata + Uptime Kuma** | Metrics, alerts, Slack notifications, public status page |

**Caption:** Everything is containerized or systemd-managed; nothing runs ad-hoc.

---

## SLIDE 6 — Hard Rules Learned the Hard Way

**Headline:** Hard rules — every one traces to a real incident

**Rule cards (each with the incident it came from):**

| Rule | Why |
|------|-----|
| **H.264 ONLY** | H.265 hardware encode caused kernel panics on Pi 5 (experiment 2026-02-05). Permanently abandoned. |
| **`KillMode=control-group` in systemd** | Without it, parent restart left zombie `rpicam-vid` processes (incident 2026-02-11) |
| **`rpicam-vid` direct exec, no ffmpeg pipes** | Pipes broke under network jitter; direct exec is one process, no broken-pipe cascades |
| **`apt-mark hold` on Docker packages** | GUI auto-updater silently restarted Frigate, causing surprise auto-recordings (incident 2026-04-01) |
| **MPEG-TS container for stream** | TS achieved 30+ day continuous uptime in Feb 2026 stress test |

**Speaker note:** These five rules are the entire difference between "research demo that works for an afternoon" and "production system you trust with a 3-day circadian run."

---

# § 2 — Alerts & Resource Monitoring

## SLIDE 7 — Section divider

**Visual:** Large "§ 2" + "Alerts & Resource Monitoring"

---

## SLIDE 8 — Why Monitor (framing)

**Headline:** Why instrument everything

**Three points:**
1. **Silent failures are worse than loud ones.** A Pi that dies at 2 AM during a circadian run is invisible until you check on it the next morning — by which time you've lost 8 hours of data.
2. **Pre-crash forensics matter.** When something does break, you need to know what the system looked like in the minutes before. That requires continuous logging, not reactive debugging.
3. **Multiple failure modes.** Network, power, thermal, disk, software — each needs a different sensor. One monitoring tool isn't enough.

**Visual:** Three icons (eye / clock / network) with each principle.

---

## SLIDE 9 — Netdata: 16 NVR Alerts (CARD GRID)

**Headline:** Netdata — 16 custom alerts on the NVR

**Path:** `/etc/netdata/health.d/nvr-alerts.conf`
**Status as of 2026-04-06:** All CLEAR

**9 alert cards in 3×3 grid (color-coded by severity):**

| Alert | Threshold | Color |
|-------|-----------|-------|
| `nvr_cpu_high` | >85% warn / >95% crit, 10 min avg | warn |
| `nvr_cpu_iowait` | >40% warn (disk bottleneck) | warn |
| `nvr_ram_usage` | <10% avail warn / <5% crit | warn |
| `nvr_swap_usage` | >50% warn | warn |
| `nvr_disk_space` | >90% warn / >95% crit per mount | warn |
| `nvr_disk_inodes` | >90% warn / >98% crit per mount | warn |
| `nvr_cpu_temperature` | >85°C warn / >95°C crit (Package ID 0) | warn |
| `nvr_container_unhealthy` | Any unhealthy | crit |
| `nvr_container_down` | Frigate / Mosquitto / Kuma exited | crit |
| (+8 more) | | accent |

**Caption:** 15-min recovery delays + split trigger/clear thresholds → zero alert flapping.

**Slack integration:** Same channel as Uptime Kuma. Email/Telegram/Discord/Teams disabled.

---

## SLIDE 10 — Uptime Kuma: 7 Service Monitors

**Headline:** Uptime Kuma — service-level monitoring

**Bulleted list with IPs:**
- **go2rtc · Pi 1** — `192.168.0.11:1984/api/streams`
- **go2rtc · Pi 2** — `192.168.0.12:1984/api/streams`
- **Frigate NVR** — `192.168.0.50:5000/api/stats`
- **Mosquitto MQTT** broker
- **NeuroSurveillance Session Daemon** — `127.0.0.1:8585/api/health`
- **Netdata** (NVR self-monitor)
- **Uptime Kuma** self-check

**Callout:** Public status page → `http://192.168.0.50:3001/status/neurosurveillance`
**Slack:** both downs AND recoveries notified (so you know when something self-healed)

---

## SLIDE 11 — Pi-Side & NVR-Side Watchdogs

**Headline:** Watchdogs at every layer

**4 cards:**

| Layer | What | How often |
|-------|------|-----------|
| **Kernel** | systemd hardware watchdog (`RuntimeWatchdogSec=30s`) | every 30 s — auto-reboots hung Pi |
| **Pi-side script** | `crash-canary.sh` logs temp · throttle · CPU · RAM | every 30 s → pre-crash forensics |
| **NVR-initiated ping** | `/opt/neurosurveillance/pi-monitor.sh` from NVR cron | every 2 min → catches silent PoE death |
| **systemd `Restart=always`** | go2rtc + session daemon | continuous |

**Speaker note:** Catches three different silent-death modes: (1) kernel hang, (2) thermal slow-death, (3) PoE power latch.

---

## SLIDE 12 — Real Incident (storytelling slide)

**Headline:** A real incident: 2026-04-02 thermal spikes

**Story arc as 4 cards (color-graded red → green):**

1. **Symptom (red).** CPU package temperature 87–92°C, recurring every 35–40 minutes. Netdata fired `nvr_cpu_temperature` warning.
2. **Investigation (orange).** Used `journalctl`, `htop`, `intel_rapl`, and Netdata charts to trace it. Found `allegoserver` (Radiens EEG software) busy-polling USB at 109% CPU.
3. **Fix (yellow).** Created systemd service `/etc/systemd/system/cpu-power-cap.service` applying Intel RAPL 20 W power cap.
4. **Result (green).** Baseline dropped to ~58°C — now have **17°C of headroom** before the 75°C alert threshold fires again.

**Callout:** "Monitoring caught it BEFORE it became a data-loss incident. That's the whole point of investing in this layer."

**Reference:** `03-troubleshooting/incidents/2026-04-02-allegoserver-thermal-spikes.md`

---

# § 3 — Python Session Daemon

## SLIDE 13 — Section divider

**Visual:** Large "§ 3" + "Python Session Daemon — Backend & API"

---

## SLIDE 14 — Daemon's Role in One Sentence

**Headline:** The glue between Radiens and Frigate

**Big centered text:**
> When you start an EEG recording in Radiens, the daemon notices within 1 second and tells Frigate to start recording all 4 cameras. When you stop the EEG, it stops the cameras and exports the matching video clips with metadata sidecars.

**Below in a small block:**
- Runs as `neurosurveillance-session.service` on the NVR
- Python 3.12 · paho-mqtt · radiens AllegoClient SDK
- Flask REST API on `127.0.0.1:8585`
- Source: private GitHub repo `neurosurveillance` (deployed at `/home/skimlab/Monitoring_project/neurosurveillance`)

---

## SLIDE 15 — Architecture & Data Flow (DIAGRAM SLIDE)

**Headline:** Daemon architecture

**Visual: data-flow diagram, left to right:**
- Far left: "Radiens (AllegoClient)"
- Center box (dashed accent border, "Session Daemon Python 3.12"):
  - Inside top: `radiens_poller` (1 s poll, R_OFF↔R_ON detection)
  - Inside middle: `session_manager` + `manual_session_manager` (per-chamber state)
  - Inside bottom: `storage_monitor` (200 GB EEG reserve)
  - Right side of box: `frigate_controller` (MQTT + Export API ±2s buffer)
  - Right side of box: `Flask API` (`127.0.0.1:8585`)
- Far right (3 outputs):
  - Frigate (recordings on disk)
  - Desktop UI (Tauri + React, polls API)
  - `/opt/neurosurveillance/exports/` (MP4 + JSON sidecars)

**Caption:** Each module has one job. The orchestrator (`daemon.py`) is a 1-second poll loop running them all.

---

## SLIDE 16 — Module-by-Module

**Headline:** Module breakdown

**Table:**

| Module | Purpose |
|--------|---------|
| `daemon.py` | Orchestrator: loads config, connects MQTT/Radiens, runs Flask in background thread, 1 s main loop |
| `radiens_poller.py` | Polls `AllegoClient.get_status()` every 1 s; detects R_OFF→R_ON and R_ON→R_OFF transitions |
| `frigate_controller.py` | MQTT publish/subscribe for recording ON/OFF; Frigate export API calls with ±2 s timestamp buffer; export polling until `in_progress: false` |
| `session_manager.py` | Tracks per-chamber session state, generates filenames (`YYMMDDHHMM_mouseID_type.mp4`), writes JSON sidecars, manages 4-chamber metadata |
| `manual_session_manager.py` | Handles external Frigate Record button clicks, inherits pending metadata, applies 5 s minimum duration filter |
| `session_utils.py` | Shared helpers (filenames, sidecars) |
| `storage_monitor.py` | Background thread, samples disk every 30 s, blocks recordings below 200 GB EEG reserve, provides bitrate calculator |
| `api.py` | Flask REST endpoints — all on `localhost:8585` |

---

## SLIDE 17 — Key Design Decisions (CARD GRID, "why you won't lose data")

**Headline:** Why you won't lose data — 4 design decisions

**4 cards:**

1. **Autonomous core.** If the daemon crashes mid-session, Frigate keeps recording. MQTT state persists ON. On daemon restart, it publishes OFF only after the next clean boundary. **No data loss.**
2. **Metadata is optional.** If you forget to set Mouse ID before starting EEG, the session uses `unknown` and still exports. You can rename the file later. **No blocking dialogs.**
3. **Multi-chamber independent state.** All 4 chambers run their own state machines in parallel, with separate pending metadata. You can record different mice in different chambers simultaneously.
4. **Daemon only OBSERVES Radiens.** It never controls it. The researcher stays in charge of EEG acquisition; the daemon is a passive listener.

**Speaker note:** These four together are the design philosophy: the system fails open, never closed.

---

## SLIDE 18 — Synchronization (BIG NUMBERS)

**Headline:** How tight is the sync?

**Three big stats:**
| Stat | Label |
|------|-------|
| **1 s** | Radiens poll interval |
| **±2 s** | Export timestamp buffer |
| **4 ch** | Independent state machines |

**Honest callout (orange):**
> Software-level sync. Good enough for behavioral analysis (locomotion, sleep posture, grooming). **Not** sufficient for ms-level spike-to-frame alignment. See § 7 for the planned hardware upgrade.

---

## SLIDE 19 — REST API Surface

**Headline:** Flask REST API — `127.0.0.1:8585`

**Table:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/status` | GET | Full daemon state: sessions, pending metadata, Radiens state, MQTT, manual recordings |
| `/api/session/metadata?chamber_id=X` | POST | Set session metadata (mouse_id, recording_type, user_name) |
| `/api/session/metadata?chamber_id=X` | DELETE | Clear metadata to defaults |
| `/api/session/current` | GET | Active session info (first active, backward-compat) |
| `/api/session/history?source=X&limit=N` | GET | Past sessions (Radiens + manual, newest first) |
| `/api/session/manual` | GET | Active and recent manual recordings |
| `/api/health` | GET | 200 if Radiens+MQTT connected, 503 otherwise; includes storage |
| `/api/storage` | GET | Disk usage, categories, can_record flag, EEG reserve |
| `/api/storage/estimate?cameras=N&hours=H` | GET | Recording size calculator |
| `/api/storage/camera-bitrates` | GET | Live query go2rtc on each Pi for actual bitrates |

---

# § 4 — Desktop GUI

## SLIDE 20 — Section divider

**Visual:** Large "§ 4" + "Desktop GUI — How to Use It"

---

## SLIDE 21 — Stack & Layout

**Headline:** Tauri desktop app

**Specs block:**
- **Stack:** Tauri v2 + React 19 + TypeScript 5.8 + Vite 7
- **Styling:** Tailwind CSS + DaisyUI
- **Theme:** Dark mode by default
- **Window:** min 1024×700, default 1400×900
- **Build:** `npm run tauri build` produces a `.deb` package; `npm run tauri dev` for hot reload

**Suggested visual:** Screenshot of the window showing all 4 ChamberSilos (replace with real screenshot when preparing).

---

## SLIDE 22 — User Workflow (NUMBERED STEPS)

**Headline:** Normal recording workflow — 7 steps

**Numbered step cards:**
1. Open the **NeuroSurveillance Session Controller** (desktop app)
2. For each chamber: enter **Mouse ID** · pick **Recording Type** · pick **Your Name** → click **Set Metadata**
3. **Start EEG recording in Radiens** (your normal Radiens workflow — daemon doesn't touch it)
4. Video **auto-starts on all 4 cameras** (daemon detects R_OFF→R_ON within 1 s)
5. Run the experiment — **the daemon is silent**
6. **Stop EEG in Radiens** → video auto-stops and exports with the metadata you set
7. Check the **Session History** panel for completion + file paths

**Caption:** Same muscle memory whether you're recording 1 chamber or 4.

---

## SLIDE 23 — GUI Components

**Headline:** What's on the screen

**6 component cards:**

| Component | What it does |
|-----------|--------------|
| **ChamberSilo** | Per-camera card: metadata form + live status + camera preview, collapsible |
| **SessionSetup** | Mouse ID input · Recording Type dropdown · User Name dropdown |
| **LiveStatus** | Pulsing red indicator when recording · session timer · session details |
| **CameraPreview** | Frigate snapshot refreshed every 1 s · reports camera online/offline |
| **StoragePanel** | Disk usage progress bar · EEG reserve indicator · recording size calculator · bitrate sync button |
| **SystemHealth** | Daemon · Radiens · MQTT · Frigate connection badges |
| **SessionHistory** | Table of past sessions (newest first), expandable rows |

**Polling intervals:** status 1.5 s · health 5 s · storage 10 s · camera snapshot 1 s

---

## SLIDE 24 — Manual Override Path

**Headline:** Recording without Radiens (rare, but supported)

**Steps:**
1. Open Frigate UI directly: `http://192.168.0.50:5000`
2. Click the **Record** button on the desired camera
3. Daemon auto-detects within 1 s; inherits pending metadata if you set it in the NeuroSurveillance UI first
4. Click Stop in Frigate → daemon exports with the same filename convention
5. **5-second minimum duration filter** prevents accidental clicks from polluting the export folder

**Callout:** Same filename convention, same organization — whether session was Radiens-triggered or manual.

---

## SLIDE 25 — Settings Modal

**Headline:** Settings (per-workstation)

**Bullets:**
- **Cameras:** list of camera IDs and labels (4 pre-configured)
- **Recording types:** dropdown options (`basal`, `recovery`, `sd`, extensible)
- **Lab members:** user name dropdown list
- **Frigate URL:** base URL for camera snapshots (default `http://192.168.0.50:5000`)
- **Persistence:** localStorage — survives reloads, scoped per workstation

---

# § 5 — Storage & NAS Transfer

## SLIDE 26 — Section divider

**Visual:** Large "§ 5" + "Storage Management & NAS Transfer"

---

## SLIDE 27 — Directory Layout

**Headline:** Where the data lives

**Tree-style block (mono font):**
```
/srv/frigate/storage/
├── recordings/    ← raw Frigate segments (internal)
├── exports/       ← temporary Frigate exports
└── clips/         ← Frigate event clips

/opt/neurosurveillance/
├── sessions/      ← JSON session sidecars
└── exports/       ← organized: user/mouse/YYYY-MM-DD/*.mp4
```

**Example filename:**
`exports/andrea/HETCF3R1/2026-04-06/2604061430_HETCF3R1_basal.mp4`
+ `2604061430_HETCF3R1_basal_session.json` (sidecar)

**Filename format:** `YYMMDDHHMM_mouseID_type.mp4` (local time, Asia/Seoul)

---

## SLIDE 28 — Capacity Math (BIG NUMBERS)

**Headline:** How much can we record?

**6 stat cards:**
| Stat | Label |
|------|-------|
| **1.7 Mbps** | Per camera (measured; 1.5 Mbps target + VBR overhead) |
| **18 GB** | Per camera per day |
| **72 GB** | Per day, 4 cameras |
| **1.9 TB** | NVMe capacity |
| **~26 days** | 4-camera headroom before hitting retention |
| **200 GB** | EEG hard reserve (always protected) |

**Caption:** 7-day retention window → ~504 GB typical working set

---

## SLIDE 29 — How the Reserve Is Enforced

**Headline:** `StorageMonitor` — the safety net

**Bullets:**
- Background thread samples disk every 30 s via `os.statvfs()` (single syscall, ~0 ms cost)
- **Atomic dict swap** → API thread never reads partial data
- Category scans (exports / recordings / clips) cached with 5-min TTL (expensive, run in background)
- **`can_start_recording()`** returns False if available < 200 GB → recording blocks before disk is exhausted
- **Bitrate sync button** queries go2rtc `/api/streams` on both Pis live and parses `--bitrate` from the `rpicam-vid` exec command — replaces the 1.5 Mbps default with measured values

**Caption:** The reserve guarantees EEG/EMG data acquisition can never be starved by a runaway video session.

---

## SLIDE 30 — NAS Transfer — Honest Status

**Headline:** NAS transfer — configured but not yet deployed

**Orange callout:**
> **Configured but NOT yet live.**
> - Target: Synology NAS at `100.120.86.10`
> - Blocker: Tailscale VPN setup to NAS
> - Stub: `nas:` section in `config.yaml` ready to fill in
> - Short-term roadmap item (next 2–4 weeks)

**Smaller note:** "Being upfront about what's done and what's not builds trust more than glossing it over."

---

# § 6 — Strengths vs. Recent Publications

## SLIDE 31 — Section divider

**Visual:** Large "§ 6" + "Strengths vs. Recent Publications"

---

## SLIDE 32 — Comparison Table

**Headline:** How we compare

**Table (highlight our row in accent color):**

| System | Cost | EEG Sync | Open Source |
|--------|------|----------|-------------|
| **NeuroSurveillance (ours)** | **~$1,174** | **Radiens API, ~1 s, ±2 s buffer** | **Yes** |
| MouseVUER (Nat. Sci. Rep., 2024) | $2–3k | none | Yes |
| OpenVEEG (2018) | $5–10k | ms-level, OpenEphys | Partial |
| Noldus EthoVision | $15–20k | limited | No |
| Clever Sys HomeCageScan | $10–15k | none | No |
| SIESTA (2025) | — | ECoG/EMG only, no video | research code |

**Speaker note:** Lead with cost, then sync. Most commercial systems don't even offer EEG sync — that's our differentiation.

---

## SLIDE 33 — Novel Contributions

**Headline:** Five novel contributions

**Numbered list:**
1. **First open-source Frigate ↔ NeuroNexus Radiens auto-sync** via AllegoClient API
2. **Multi-chamber independent metadata** — 4 mice, 4 contexts, one app
3. **MQTT pub/sub orchestration** → loose coupling, fail-safe recording
4. **Full operational documentation** — 38+ vault pages including incident reports
5. **~$1.2 k vs. $5–20 k commercial** — fully reproducible

---

## SLIDE 34 — Key References

**Headline:** Key references (all in `06-references/progress-meeting-2026-03-12.md`)

**Card grid:**
- **MouseVUER** · Nature Sci. Rep. 2024 · home-cage video monitoring
- **OpenVEEG** · 2018 · ms-level video-EEG sync
- **SIESTA** · 2025 · ECoG/EMG sleep staging
- **SAGER** · Sensors 2025 · EEG vigilance state classification
- **Spyglass** · eLife 2024 · reproducible neuroscience data management
- **FERAL** · bioRxiv 2025 · video → behavior without pose estimation (Rockefeller)
- **Lightning Pose** · Nature Methods 2024 · semi-supervised pose estimation

**Publication target for our methods paper:** *Journal of Neuroscience Methods* (primary) / *HardwareX* (alternative)

---

# § 7 — Future: Hardware Sync via XDAQ

## SLIDE 35 — Section divider

**Visual:** Large "§ 7" + "Future: Hardware Sync via XDAQ"

---

## SLIDE 36 — Software → Hardware Sync (BEFORE/AFTER)

**Headline:** From software polling to hardware triggering

**Two-card comparison:**

| Current (orange) | Planned (green) |
|------------------|-----------------|
| Software polling via Radiens API | Wire Pi GPIOs to XDAQ digital I/O |
| ~1 s latency · ±2 s export buffer | Hardware-triggered frame markers |
| Good for behavior, **not** for spikes | Per-frame ms-level alignment |

**Callout:** Unlocks ms-level correlation between spike events and individual video frames — the analytical bottleneck for causal behavioral questions.

---

## SLIDE 37 — Preparatory Work Already in Place

**Headline:** Why this upgrade is straightforward

**Bullets:**
- 200 GB EEG reserve already enforced in `storage_monitor.py`
- Session daemon architecture is **Radiens-agnostic** — it's an observer, not a controller
- Frigate export API already buffered ±2 s → no edge frames lost during transitions
- Config schema ready to accept hardware sync metadata (extra fields in JSON sidecars)
- Per-chamber independent state → scales to more headstages without code rewrites

---

## SLIDE 38 — Validation Plan

**Headline:** What we still need to validate

**Bullets:**
- **Post-export `ffprobe` integrity check** (lesson from 2026-03-06 19 GB MP4 corruption incident — race condition in `wait_for_export()`, since fixed)
- **Measure actual sync latency:** Radiens R_ON → first Frigate frame timestamp
- **Long-term stability data** from multi-day sessions (currently rely on Feb 2026 30-day stress test)

**Longer horizon:**
- PostgreSQL session DB → replace JSON sidecars with structured queries
- NWB (Neurodata Without Borders) export → DANDI archive submission
- Dual-modality (EEG/EMG + FERAL video) sleep scoring pipeline

---

# § 8 — Why This Matters for Circadian Studies

## SLIDE 39 — Section divider

**Visual:** Large "§ 8" + "Why This Matters for Circadian Studies"

---

## SLIDE 40 — The Failure Mode We Engineer Against

**Headline:** Circadian studies = multi-day continuous runs

**Big red callout:**
> A single crash can ruin a week of data.
> A **silent** failure (no alert) is even worse.

**Below:** "Every design choice in this system optimizes for **uptime AND observability** — the two things that turn a research demo into a research instrument."

---

## SLIDE 41 — Stability Features (CARD GRID)

**Headline:** What keeps it running for days

**6 cards (all green):**

| Feature | What it protects against |
|---------|--------------------------|
| **Hardware watchdog** (`RuntimeWatchdogSec=30s`) | Kernel hangs |
| **Crash-canary logging** (vitals every 30 s) | Silent slow-deaths (thermal, memory leak) |
| **NVR-initiated Pi ping** (every 2 min) | PoE power failures, network drops |
| **`apt-mark hold` Docker** | Surprise auto-restarts from GUI updater |
| **`Restart=always`** systemd | Single-process crashes |
| **Fail-safe MQTT recording state** | Daemon crashes mid-session |
| **Thermal margin** (RAPL 20 W cap) | CPU thermal runaway |

---

## SLIDE 42 — Track Record (BIG NUMBERS)

**Headline:** What the system has actually done

**3 stat cards:**
| Stat | Label |
|------|-------|
| **30+ days** | Continuous uptime in Feb 2026 MPEG-TS stress test |
| **0** | Active alerts as of 2026-04-06 |
| **~26 days** | Storage headroom @ 4 cameras |

**Caption:** Stable since 2026-02-19 (PMIC hardening) · Thermal regime stable since 2026-04-03

---

## SLIDE 43 — Incident Gallery (storytelling)

**Headline:** A short history of solved failures

**Compact table:**

| Date | Incident | Resolution |
|------|----------|------------|
| 2026-02-05 | H.265 kernel panics | Reverted to H.264 (permanent rule) |
| 2026-02-09 | go2rtc instability | Switched to MPEG-TS container |
| 2026-02-11 | Zombie `rpicam-vid` | `KillMode=control-group` in systemd |
| 2026-02-19 | Pi dead after 6-day holiday (PoE PMIC latch) | EEPROM hardening (`PSU_MAX_CURRENT=5000`) |
| 2026-02-23 | Session daemon Radiens auth failure | Cognito session tokens |
| 2026-02-24 | Pi unreachable, no auto-reboot | Hardware watchdog enabled |
| 2026-03-06 | 19 GB MP4 export corruption | Race condition fix (poll until `in_progress: false`) |
| 2026-04-01 | Unexpected auto-recordings | `apt-mark hold` Docker packages |
| 2026-04-02 | Thermal spikes (87–92°C) | Intel RAPL 20 W power cap |

**Speaker note:** Don't dwell on this slide — it's a backup if anyone asks "but is it actually robust?" Each row is a documented incident report in `03-troubleshooting/incidents/`.

---

# § 9 — Roadmap

## SLIDE 44 — Section divider

**Visual:** Large "§ 9" + "Roadmap & Next Steps"

---

## SLIDE 45 — Roadmap (3 horizons)

**Headline:** What's next

**3 horizon cards stacked vertically:**

**Short-term · 2–4 weeks**
- ffprobe post-export validation (prevent silent corruption)
- Finish Tailscale NAS transfer deploy
- Confirm `apt-mark hold` is effective end-to-end

**Medium-term · 1–3 months**
- Automated sleep scoring (collaboration with Prof. Kim Daewook's lab)
- FERAL video classifier — train on labeled sleep/wake frames
- Video-EEG temporal alignment validation
- PostgreSQL session database
- Multi-headstage support (independent Radiens per chamber)

**Long-term · 3–6 months**
- NWB export → DANDI archive submission
- Dual-modality sleep scoring pipeline (EEG/EMG + FERAL video)
- System replication guide
- Methods paper submission (target: *J. Neurosci. Methods* / *HardwareX*)

---

## SLIDE 46 — Documentation as a Deliverable

**Headline:** Documentation is part of the system

**Bullets:**
- 38+ vault pages: golden configs, procedures, incident reports, references
- Lab members can reproduce or repair the system **without me in the room**
- Every "hard rule" traces to a specific incident report — no folklore
- Variable system (`{VARIABLE}` notation) means production values are versioned in one place: `00-config/production-values.md`

**Speaker note:** This is unusual for a research project and is a meaningful contribution in itself. Worth a slide.

---

## SLIDE 47 — Summary

**Headline:** Summary

**5 bullets:**
- Production-operational 4-chamber EEG-synchronized video system
- **Fail-safe · fully monitored · fully documented · ~$1,174**
- Engineered for **multi-day circadian recordings**
- Roadmap: **ms-level hardware sync** + automated sleep scoring
- Open-sourceable → **reproducible methods paper** in sight

---

## SLIDE 48 — Acknowledgments

**Headline:** Thanks to

**Bullets:**
- Lab PI and lab members
- Prof. Kim Daewook's lab — sleep scoring collaboration
- Open-source projects: Frigate, go2rtc, Mosquitto, Netdata, Uptime Kuma, Tauri, NeuroNexus Radiens

---

## SLIDE 49 — Thank You

**Big centered text:** Thank you
**Subtitle:** Questions?
**Footer:** Andrea · 2026-04-10
**(Optional)** QR code linking to the GitHub repo

---

## BACKUP SLIDES (only if asked)

### B1 — Full API endpoint table
(See SLIDE 19, but without truncation.)

### B2 — Full Netdata alert list
All 16 alerts with exact thresholds, lookup periods, and clear conditions.

### B3 — Frigate `config.yml` highlights
- `record.enabled: true`
- Retention rules
- QSV decoder config
- 4-camera definitions

### B4 — Daemon `config.yaml` storage section
```yaml
storage:
  poll_interval: 30
  eeg_reserve_gb: 200
  warn_percent: 75
  critical_percent: 90
  camera_bitrate_mbps: 1.5
  go2rtc_apis:
    - "http://192.168.0.11:1984"
    - "http://192.168.0.12:1984"
```

### B5 — Recent thermal incident detail
Full timeline from Netdata first warning → root-cause → systemd RAPL fix → post-fix steady state.

### B6 — PMIC PoE death incident detail
6-day holiday → Pi dead → EEPROM tuning → 2+ weeks stable.

---

## VISUAL DESIGN GUIDANCE FOR THE AI GENERATOR

- **Background:** white, no gradients
- **Accent color:** `#1F6FEB` (blue), used sparingly for headings, dividers, highlighted table rows, accent cards
- **Secondary colors:** green `#16A34A`, orange `#D97706`, red `#DC2626` — used only for status (ok/warn/crit cards)
- **Font:** default sans-serif (system / Segoe UI / Inter), no decorative fonts
- **Diagrams:** clean line work, white nodes with thin accent borders, grey arrows
- **Tables:** thin borders, accent header row, alternate-row neutral background
- **No icons unless they reinforce meaning** — avoid decorative clipart
- **No animation other than incremental bullet reveal**
- **Per-slide density:** maximum 5 bullets, prefer cards/tables/diagrams to walls of text
- **Footer on all content slides:** "NeuroSurveillance · Lab Meeting 2026-04-10 · Andrea"

---

## SOURCE FILES (for the AI generator's reference / verification)

- `_INDEX.md`
- `00-config/production-values.md`
- `01-infrastructure/raspberry-pi/golden-go2rtc-config.md`
- `01-infrastructure/raspberry-pi/golden-systemd-service.md`
- `01-infrastructure/raspberry-pi/golden-boot-config.md`
- `01-infrastructure/raspberry-pi/watchdog-monitoring.md`
- `01-infrastructure/frigate/docker-compose.md`
- `01-infrastructure/frigate/config-yml.md`
- `01-infrastructure/session-daemon/architecture.md`
- `01-infrastructure/session-daemon/frontend-reference.md`
- `01-infrastructure/netdata/nvr-alerts-config.md`
- `02-procedures/installation/new-pi-setup.md`
- `02-procedures/session-recording-workflow.md`
- `02-procedures/installation/storage-management-implementation.md`
- `06-references/monitoring-diagnostics.md`
- `06-references/progress-meeting-2026-03-12.md`
- `06-references/lab-meeting-2026-04-10-presentation-plan.md`
- `03-troubleshooting/incidents/2026-04-02-allegoserver-thermal-spikes.md`
- `03-troubleshooting/incidents/2026-02-19-pmic-fault-poe-death.md`
- `03-troubleshooting/incidents/2026-02-23-session-daemon-radiens-auth-cors.md`
- `03-troubleshooting/incidents/2026-02-24-pi-unreachable-no-route.md`
- `04-journal/2026-04/2026-04-03.md`

---
tags: [presentation, revisions]
date: 2026-04-08
related: [[lab-meeting-2026-04-10-presentation-brief]]
---

# Presentation Revisions — Batch 1 (2026-04-08)

> **Purpose.** Targeted revision instructions for the AI pptx generator. Only the slides that need changes are listed here. Each entry identifies the slide by **topic** (not just number) because the number offset differs slightly between the brief, the .pptx, and the .html. Apply these on top of `lab-meeting-2026-04-10-presentation-brief.md`.

---

## Revision 1 — System Topology: improve the graphic

**Slide identifier:** "System Topology" diagram slide (§ 1, early — brief SLIDE 3, pptx ~slide 4)

**Current state.** Simple box-and-arrow diagram: Pi 1 + Pi 2 → NVR → NAS with RTSP/rsync labels.

**Revision instructions.**
- Replace the generic box diagram with a **richer architectural graphic**:
  - Group the two Pis inside a "Recording Room" zone (dashed container)
  - Put the NVR inside an "Office / Server Rack" zone
  - Put the NAS in a "Storage Tier" zone
  - Show the data flow as **labeled lanes** (RTSP streams solid, MQTT control dashed, rsync planned dotted)
  - Include small **camera icons** at the Pi nodes (4 cameras total)
  - Include small **chip/GPU icon** on the NVR to emphasize Intel QSV hardware decode
  - Overlay a Tailscale cloud icon covering all three zones to show remote access
  - Add a Slack cloud icon with an arrow from the NVR (alerts)
- Color palette stays the same (white bg, blue #1F6FEB accent)
- Diagram should fill ~80% of the slide width

**Speaker note to add.** "Everything on the left is in the experiment room; the NVR lives in the server rack. The only traffic leaving the recording room is compressed H.264 over RTSP."

---

## Revision 2 — Watchdogs slide: explain more

**Slide identifier:** "Pi-Side & NVR-Side Watchdogs" (§ 2 — brief SLIDE 11, pptx ~slide 12)

**Current state.** 4 cards listing watchdog layers with one-line descriptions.

**Revision instructions.**
- Keep the 4 cards but **add a short prose block above the cards** (2–3 sentences):
  > "A watchdog is a piece of code whose only job is to notice when something else has stopped working and take action. This system has four of them, each catching a different class of silent failure — kernel hangs, thermal slow-deaths, PoE power latches, and single-process crashes."
- Expand each card's description:
  - **Hardware watchdog:** "A kernel-level timer that reboots the Pi if the kernel itself stops responding to the hardware — catches total lock-ups that would otherwise need someone to physically power-cycle the box."
  - **Crash-canary:** "A small bash script that logs CPU temperature, throttle status, CPU load, and free memory every 30 seconds. If the Pi dies later, we have the last 30 seconds of vitals on disk to figure out why."
  - **NVR-initiated ping:** "The NVR pings each Pi every 2 minutes from cron. If a Pi stops responding, it fires a Slack alert. This is the only layer that catches PoE failures, because a Pi with no power can't report its own death."
  - **systemd `Restart=always`:** "If go2rtc or the session daemon crashes, systemd restarts them within seconds. This is the fine-grained single-process recovery layer."
- Add a callout at the bottom: "Three independent layers + one fine-grained layer. You need all four because each catches a different failure class."

---

## Revision 3 — § 3 Session Daemon: add speaker-note footnotes throughout

**Slide identifiers.** The entire Session Daemon section (§ 3) — brief SLIDES 14–19, pptx ~slides 15–20. Especially the **REST API slide** (last one of the section, pptx ~slide 20).

**Problem.** Andrea doesn't feel confident enough on the daemon internals to present them live. Needs richer speaker notes / footer notes so the slides are self-explanatory without memorization.

**Revision instructions.** For each of these slides, add an **explicit speaker-note block** (PowerPoint "Notes" pane, or a small italic footer in ~10pt grey text at the bottom of the slide if the generator supports it):

### "The glue between Radiens and Frigate" (Role slide)
**Speaker note:**
> "The daemon is a Python 3.12 process that runs as a systemd service on the NVR. It has three external connections: (1) it polls Radiens every second to know when EEG recording is on or off, (2) it publishes MQTT messages to Frigate to start/stop video recording, and (3) it exposes a REST API that the desktop GUI uses to show status. It has no database — session state is kept in memory and written to JSON files on disk at export time."

### "Daemon Architecture" (Diagram slide)
**Speaker note:**
> "Read this diagram left-to-right. The radiens poller is the only thing that talks to Radiens. When it sees a state transition, it hands off to session_manager, which decides what to do per chamber, then tells frigate_controller to act on it — either publishing an MQTT message or calling the Frigate export API. Everything the GUI sees goes through the Flask API on the right. The storage monitor runs on its own thread and can veto new recordings if disk is low."

### "Module-by-Module" (Table)
**Speaker note:**
> "The design principle here is single-responsibility: each module has one job, and if I need to change how we talk to Radiens, I only touch radiens_poller.py. The orchestrator daemon.py is deliberately thin — maybe 80 lines of code — because all the logic is pushed into the modules below it."

### "Key Design Decisions" (4 cards)
**Speaker note:**
> "All four of these decisions have the same underlying principle: **fail open, never closed**. The worst outcome in a research setting is silently losing data, so every code path defaults to 'keep recording' rather than 'stop and wait for human intervention.'"

### "Synchronization" (big numbers)
**Speaker note:**
> "The 1-second polling interval is the fundamental limit — we can't detect a Radiens transition faster than that. The ±2 second export buffer is a safety margin on top: when we ask Frigate to export the video corresponding to a session, we tell it to grab 2 seconds before the EEG start and 2 seconds after the EEG stop, so even if our clocks drift slightly we capture the full window. This is deliberately conservative."

### "REST API Surface" (the slide Andrea is most anxious about)
**Speaker note (expanded):**
> "Nothing on this table is exposed to the network — everything binds to 127.0.0.1:8585, so only the GUI running on the same machine can talk to it. The three endpoints you actually use day-to-day are (1) POST /api/session/metadata when you set the mouse ID and recording type, (2) GET /api/status which the GUI polls every 1.5 seconds to show the live state, and (3) GET /api/storage which powers the disk usage widget. Everything else is either internal bookkeeping or health checks for Uptime Kuma to probe."

> "The main point to convey to the audience: this is a clean separation between the daemon (which does the work) and the GUI (which is just a thin client). If I replace the GUI tomorrow with a web dashboard or a CLI tool, the daemon doesn't change at all."

---

## Revision 4 — Slide 22: replace with a LIVE DEMO transition

**Slide identifier:** First GUI slide in § 4 — currently "Stack & Layout" (brief SLIDE 21) or "User Workflow" (brief SLIDE 22) depending on count; this is where Andrea wants to close the deck and switch to a live demo.

**Revision instructions.**
- **Replace** the current slide content with a clean **"LIVE DEMO"** transition slide:
  - Large centered text: **"Live Demo"**
  - Subtitle: "Closing the slides — switching to the desktop GUI"
  - Small checklist below (for Andrea's own reference on-slide):
    - Open NeuroSurveillance Session Controller
    - Show all 4 ChamberSilos + SystemHealth badges
    - Walk through setting metadata for one chamber
    - Show the StoragePanel + bitrate sync button
    - Show SessionHistory with a past session expanded
    - Close and return to the deck
  - Bottom note: "Duration target: 3–4 minutes"
- **Flow consequence:** after this live-demo slide, the GUI walkthrough slides become redundant:
  - "GUI Components" card grid → **move to backup appendix**
  - "Manual Override Path" → **move to backup appendix**
  - "Settings Modal" → **move to backup appendix**
- **Add a "Resume" marker slide** after the backup-moved slides to cleanly reconnect: large centered text "Back to the slides · § 5 Storage Management" — this is just a visual cue for Andrea after the demo, optional.

**Speaker note on the LIVE DEMO slide:**
> "Stop presenter mode here. Open the NeuroSurveillance Session Controller from the dock. Walk through steps 1–6 of the recording workflow on a dummy chamber. Deliberately show the storage panel so the next section flows naturally."

---

## Revision 5 — "How the Reserve Is Enforced": simplify jargon

**Slide identifier:** Storage section, StorageMonitor explanation (§ 5 — brief SLIDE 29, pptx ~slide 30)

**Problem.** Sentences like "Background thread samples disk every 30 s via `os.statvfs()` (single syscall, ~0 ms cost)" and "atomic dict swap → API thread never reads partial data" are too technical for lab members outside the software world.

**Revision instructions.** Rewrite the bullets in plain language:

**New bullets:**
- Every 30 seconds, the daemon checks how much free space is left on the NVR's disk — this check is cheap enough to run continuously without slowing anything down.
- A separate background process keeps a running tally of how much space recordings, exports, and clips are each using — so we can tell you not just "disk is 80% full" but *which category* is filling it up.
- The hard rule: **recording cannot start if free space drops below 200 GB**. That 200 GB is reserved for the EEG/EMG data stream and is never touched by video, no matter what.
- There is a **Sync Bitrates** button in the GUI: press it and the daemon asks each Pi directly how much bandwidth its cameras are actually using right now. The storage calculator then uses the real measured value instead of an estimate.

**Callout (plain language):**
> "In short: the system guarantees that a runaway video recording can never eat into the space your EEG data needs."

---

## Revision 6 — Comparison Table (Slide 32): deeper comparisons

**Slide identifier:** "How We Compare" table in § 6 — brief SLIDE 32

**Problem.** MouseVUER has visible weaknesses that the current table doesn't expose. Need harder comparisons with Salem et al. and OpenVEEG. Andrea will do the literature search — this file should just clarify *what to compare*.

**Revision instructions.**
- Expand the comparison table from 4 columns to **6 columns**:
  1. System (name + citation)
  2. **Camera architecture** (USB vs CSI/IP streaming)
  3. **Cost per chamber** (total ÷ number of chambers supported)
  4. **Max chambers per host PC** (bandwidth ceiling)
  5. **EEG sync** (none / software / hardware)
  6. **Open source** (yes / partial / no)
- Highlight the "ours" row in accent color
- **Data sourced from** `Comparative Analysis of Behavioral Research Acquisition Systems.md` (2026-04-08).

**Proposed expanded table:**

| System | Camera architecture | Cost/chamber | Max chambers per host | EEG sync | Open source |
|---|---|---|---|---|---|
| **NeuroSurveillance (ours)** | **CSI → H.264 → RTSP, no intermediate ffmpeg** | **~$294** | **Unlimited (add Pi nodes)** | **Software ~1 s + ±2 s buffer; XDAQ hardware sync planned** | **Yes** |
| Salem 2020 | Pi cameras, custom UDP/TCP master–slave protocol (not RTSP) | ~$86 (24-cam build, $2,073 total) | 24 on one master PC | Frame sync within 33 ms; ~170 ms preview latency; no EEG coupling | Yes (Python) |
| OpenVEEG (2018) | USB webcams or analog SDI via BlackMagic PCIe cards | ~$400 for storage alone; "~1/5 of commercial" | Limited by DAQ + capture card inputs on one workstation | Sub-ms via LSL/NTP (≤33 ms video↔EEG); **hardcoded** to National Instruments DAQ | Yes (C++/Python) |
| MouseVUER (2024) | USB 3.0 Intel RealSense D435 depth cameras | ~$200+ camera **+ dedicated mini-PC or custom SBC module per enclosure** | 1 camera per compression unit (hard ceiling) | NTP clock over RTSP aligns depth ↔ RGB only, no EEG | Yes (SDK + CAD) |
| SIESTA (2025) | Post-hoc only — reads `.edf` files | N/A | N/A | No live acquisition | Yes (Python web app) |

**Callouts to place below the table:**

> **MouseVUER scales poorly.** Each camera needs its own USB 3.0 bus + dedicated SBC or mini-PC to handle compression before handing off to a server. Scaling to 4+ chambers = 4+ PCs. Our architecture runs 4 chambers off a single NUC at 9–12% CPU — the Pi nodes just stream, the NVR does the work.

> **Salem 2020 is cheaper per chamber (~$86 vs our ~$294) but tightly coupled.** Custom Python master/slave protocol over raw sockets — no standard RTSP, no loose coupling, no EEG integration. Metadata is global to the whole rig, not per-chamber.

> **OpenVEEG has tighter sync (sub-ms via LSL) but is hardcoded to National Instruments DAQs.** Our observer pattern is hardware-agnostic — swap one module to support any acquisition API.

**Papers referenced** (source: `Comparative Analysis of Behavioral Research Acquisition Systems.md`):
- **Salem et al. 2020** — https://www.sciencedirect.com/science/article/pii/S2468067220300699
- **OpenVEEG** — https://www.sciencedirect.com/science/article/pii/S0920121118301244
- **MouseVUER** — https://www.nature.com/articles/s41598-024-52788-9
- **SIESTA** — https://journals.sagepub.com/doi/10.1177/07487304251336649

---

## Revision 7 — Novel Contributions (Slide 33): expand

**Slide identifier:** "Novel Contributions" list in § 6 — brief SLIDE 33

**Current list (5 items).** Keep all 5, **add these new items** as contribution #1 (most important):

**New contribution to prepend:**
1. **Acquisition-system agnostic sync pattern.** The auto-sync is currently implemented against the NeuroNexus Radiens AllegoClient API, but the *pattern* is general: any EEG acquisition system that exposes an API (OpenEphys, Intan, Blackrock, Plexon) can be plugged into the same daemon by swapping out a single module (`radiens_poller.py`). The daemon, Frigate, MQTT bus, export logic, and GUI all stay unchanged. This makes the system **flexible enough to adopt to each lab's existing EEG stack** rather than forcing a new one.

**Optional extra contributions** (Andrea to decide whether to include):
- **Observer-only integration** — unlike systems that take over the acquisition software, this daemon only reads Radiens state. The researcher keeps full control of their acquisition workflow.
- **Per-chamber independent session metadata** — rare in existing tools, which typically assume one experiment at a time per rig.
- **Hot-pluggable recording types and users** — Recording type / user list is configurable from the GUI settings, no code changes or daemon restarts.

---

## Revision 8 — Preparatory Work (Slide 37): explain "Config schema ready"

**Slide identifier:** "Preparatory Work Already in Place" in § 7 — brief SLIDE 37

**Problem.** The bullet "Config schema ready to accept hardware sync metadata" is cryptic. Need a speaker note explaining what this means concretely.

**Revision instructions.** Add this speaker note to the slide:

**Speaker note:**
> "When the hardware sync upgrade lands, each video export will need to carry additional information: which XDAQ digital line triggered the start frame, the hardware timestamp of that trigger, and the offset between the Pi's clock and the XDAQ master clock. Rather than redesigning the JSON sidecar format later, I've already left those fields in the schema as optional — they're currently ignored, but when the hardware is wired up, we just start populating them and existing tooling keeps working. Zero breaking changes."

**Optional on-slide rewording of the bullet itself:**
- **Old:** "Config schema ready to accept hardware sync metadata"
- **New:** "JSON sidecar schema already reserves fields for hardware sync metadata — zero breaking changes when XDAQ triggers are wired in"

---

## Flow suggestions from Andrea's revisions

These are adjustments I'd recommend to keep the deck flowing naturally after the edits above:

1. **§ 4 GUI section shrinks** to just the Live Demo transition slide (Revision 4). The 3 removed slides (GUI Components, Manual Override, Settings Modal) move to the appendix as backup slides — **keep them available for Q&A**, don't delete them.

2. **Add a "Resume" transition** immediately after the live demo, right before § 5 opens. This gives Andrea a clean visual anchor when returning to the deck: large "← Back from live demo — § 5 Storage" text.

3. **Section § 3 (Session Daemon) now has expanded speaker notes on every slide.** This means Andrea can rely on the notes pane during presentation instead of memorizing details. Make sure the generator outputs proper PowerPoint speaker notes, not just footer text.

4. **Comparison table (Revision 6)** goes from 4 columns to 6 columns — the slide will feel denser. Consider splitting into two slides if it gets cramped: one "Architecture & Cost" comparison, one "Sync & Openness" comparison.

5. **Novel Contributions (Revision 7)** now has 6+ bullets with the new "acquisition-agnostic" item. If that feels like too many, move the original "38+ vault pages documentation" bullet to a separate "Documentation as a deliverable" slide later in the deck (which already exists as SLIDE 46 in the brief).

6. **Watchdogs slide (Revision 2)** becomes wordier with the prose intro + expanded card descriptions. If it feels crowded, consider **splitting into two slides**: "What is a watchdog, and why four of them?" (intro + principle) → "The four layers" (cards).

---

## Comparison axes — completed (2026-04-08)

Populated from `Comparative Analysis of Behavioral Research Acquisition Systems.md`. Each axis shows what our system delivers and what each published system does on the same axis.

### 1. Camera architecture
- **Ours:** CSI cameras on headless Pi 5, H.264 bitstream piped over MPEG-TS through stdout to go2rtc, RTSP over LAN, no ffmpeg middleman.
- **MouseVUER:** USB 3.0 Intel RealSense D435 depth cameras.
- **Salem 2020:** Raspberry Pi cameras, but custom Python master/slave protocol over raw UDP/TCP sockets (not RTSP).
- **OpenVEEG:** generic USB webcams or analog SDI cameras routed through BlackMagic PCIe capture cards.

### 2. Cost per chamber
- **Ours:** ~$294/chamber ($1,174 ÷ 4).
- **Salem 2020:** ~$86/chamber ($2,073.52 total for a 24-camera build) — **cheaper** than ours.
- **OpenVEEG:** "~1/5 of commercial", ~$400 just for 8 TB of storage.
- **MouseVUER:** >$200 for the RealSense alone, **plus** a dedicated HP EliteDesk mini-PC or a custom Power & Control Module housing multiple SBCs per enclosure.

### 3. Chambers per host PC (scalability ceiling)
- **Ours:** 4 chambers on a single NUC at 9–12% CPU (Intel QSV hardware decode). Scales by adding Pi nodes — the NVR handles them all.
- **Salem 2020:** 24 cameras on one master PC.
- **MouseVUER:** **one dedicated SBC or client PC per camera** for compression before the server — hard scalability ceiling.
- **OpenVEEG:** limited by physical DAQ/capture card inputs on one workstation.

### 4. EEG acquisition coupling
- **Ours:** observer pattern — daemon polls Radiens via the AllegoClient API but **never controls it**; hardware-agnostic, swap `radiens_poller.py` to support any acquisition API.
- **OpenVEEG:** **hardcoded** to National Instruments DAQ via specific Python/C++ bindings.
- **SIESTA:** post-hoc only, reads `.edf` files — no live acquisition coupling at all.

### 5. Sync mechanism and tightness
- **Ours:** software sync ~1 s latency + ±2 s export buffer; **XDAQ hardware sync planned** (per-frame alignment).
- **OpenVEEG:** sub-ms software sync via NTP + LabStreamingLayer (LSL); ≤33 ms video↔EEG alignment — **tightest** of the group.
- **Salem 2020:** frame sync within 33 ms; ~170 ms preview latency; no EEG coupling.
- **MouseVUER:** NTP clock over RTSP to align depth ↔ RGB frames; no EEG sync.
- **None of the four papers** use hardware TTL / PTP / GPIO sync — same limitation we have today.

### 6. Multi-chamber independent metadata
- **Ours:** 4 independent per-chamber state machines; mouse ID, recording type, user set **per chamber** in the UI; truly parallel experiments.
- **Salem 2020:** cameras can be bundled and named, but experiment start/end + metadata are **global** to the whole rig.
- No other paper even addresses multi-chamber metadata per experiment.

### 7. Fail-safe / failure-mode design
- **Ours:** fail-open bias — recording persists if the daemon crashes; metadata is optional with fallbacks; 200 GB hard storage reserve for EEG.
- **None of the papers** feature disk-reserve fail-safes for parallel data streams.
- **Salem 2020** and **MouseVUER** rely on their respective client/server software staying up — no published evidence of camera-side fail-open behavior if the master software crashes.

### 8. Long-term stability (multi-day / circadian)
- **Ours:** Pi EEPROM hardening (PMIC latch protection), hardware watchdog, crash-canary every 30 s, documented 30+ day stress test.
- **OpenVEEG:** claims continuous capability **up to 80 days** but documents no watchdogs or crash-recovery scripts.
- **MouseVUER:** emphasizes 24-hour cycles; no uptime-focused hardening published.
- **Salem 2020:** used for 24-hour fruit fly monitoring, but timing validation only explicitly tested "a 2-minute period".
- **SIESTA:** designed for multiday/circadian data (e.g., 3-week jetlag experiments) but handles **post-acquisition** analysis only.

### 9. Monitoring and alerting
- **Ours:** 16 Netdata alerts (thermal, Docker, I/O), 7 Uptime Kuma monitors, Slack webhook, public status page.
- **None of the four papers** describe any operational monitoring story. No thermal tracking, no heartbeats, no automated alerts. **This is a clean differentiation.**

### 10. Documentation & reproducibility
- **Ours:** 38+ page Obsidian vault — golden configs, variable deployment values, step-by-step install guides, **rigorous post-mortem incident reports**.
- **Salem 2020:** BOM + standard install commands only.
- **MouseVUER:** SolidWorks CAD files + GitHub assembly instructions.
- **None offer** incident documentation or failure-mode analysis at the depth we maintain.

### 11. Orchestration pattern
- **Ours:** loose coupling via MQTT pub/sub (Mosquitto). Frigate, daemon, and cameras restart/update independently.
- **Salem 2020:** tightly coupled custom Python master/slave over UDP/TCP — host PC is an active dictator.
- **OpenVEEG:** monolithic application using LSL to actively tie video + DAQ streams together.

### 12. Hardware sync upgrade path
- **Ours:** JSON sidecar schema already reserves fields for hardware sync metadata; direct XDAQ GPIO wiring path exists.
- **Neither OpenVEEG nor Salem 2020** has a documented GPIO/TTL/PTP upgrade path — both are locked to their respective software-clock approaches.

### 13. Open-source status and licensing
- **Ours:** Python daemon + React/Tauri frontend, built on open-source tools; currently private but public-ready.
- **All four papers are fully open-source:** OpenVEEG (C++/Python), Salem 2020 (Python), MouseVUER (SDK + CAD), SIESTA (Python web app on Zenodo/GitHub).
- **Honest framing:** the advantage isn't "ours is open, theirs isn't" — it's what's bundled *around* the open code (documentation, incident reports, operational monitoring).

### 14. Storage management and retention policy
- **Ours:** automated 7-day rolling retention, 200 GB hard reserve enforced every 30 s, NAS offload via Tailscale (pending).
- **MouseVUER:** lossy/lossless split compression (9×–21× on depth files) — clever but no retention logic.
- **Salem 2020:** chunks videos into time segments for manageability — no automated cleanup.
- **OpenVEEG:** "just buy an 8 TB drive" — no retention logic at all.

---

## Slide-use summary — what to lead with

After reading the full comparison, the sharpest differentiators to foreground in the presentation (in this order):

1. **Monitoring & alerting** — *nobody else does this*. Unique position.
2. **Documentation depth** — incident reports, post-mortems, golden configs. Unique position.
3. **Fail-open design** — no other paper has storage reserve or crash-persistent recording.
4. **Acquisition-agnostic observer pattern** — only OpenVEEG couples to EEG, and it's hardcoded to NI DAQs.
5. **Loose-coupled MQTT orchestration** — everyone else is tightly coupled or monolithic.
6. **Multi-chamber independent metadata** — only Salem even supports multi-camera, and it's global metadata.
7. **Scalability without PC-per-camera** — MouseVUER's hard ceiling is a clean talking point.

**Honest concessions to acknowledge in the talk** (don't hide them):
- **Salem 2020 is cheaper per chamber** ($86 vs $294). Frame this as a design tradeoff — we chose standard RTSP over a custom protocol.
- **OpenVEEG has tighter sync** (sub-ms via LSL). Frame this as the reason for the XDAQ hardware upgrade path.
- **All four papers are already open-source.** Our edge is what's *around* the code, not the code itself.

**Source file:** `/home/andrea/Downloads/Organized/Documents/Text/Comparative Analysis of Behavioral Research Acquisition Systems.md` (imported 2026-04-08)

---

## Sharpest framing — use as transition into § 6

Use this as the spoken transition when opening the comparisons section. It reframes the whole table from "are we better on every axis" (we're not) to "are we solving a problem they aren't" (clearly yes).

> "Four published systems handle pieces of this problem. Salem is cheaper. OpenVEEG syncs tighter. MouseVUER captures depth. SIESTA scores sleep. **None of them is production-operational the way a neuroscience lab actually needs** — no monitoring, no incident response, no fail-open design, no documentation you can hand to a new lab member. That gap is where this system lives."

**Where to put it:** add as a speaker-note on the § 6 section divider slide, OR as a quoted callout under the comparison table on the next slide. Either works.

---

## What we can learn from them — ideas to steal (footnote material)

This is too much detail for the slides themselves. Recommend embedding as **speaker notes on Slide 33 (Novel Contributions)** or as a single backup appendix slide titled *"Ideas we can borrow from prior work"*. If presenting verbally, mention 2–3 of these during Q&A if anyone asks "what's still missing".

| Idea | Source | Why it matters for us |
|---|---|---|
| **LabStreamingLayer (LSL)** for sub-ms software sync | OpenVEEG | Cheaper interim step toward ms-level sync **before** the XDAQ hardware path ships. Add an LSL outlet to the daemon and pull it in from Radiens/XDAQ without touching anything else. |
| **Frame-level sync validation via a blinking LED in-frame** | Salem 2020 (common technique) | Cheap way to **measure** the actual Radiens→first-frame latency without waiting for XDAQ wiring. This is the concrete answer to the validation TODO in § 7. |
| **Per-chamber video chunking into named segments** | Salem 2020 | Frigate already chunks at the segment level — could expose chunk boundaries to the export API for partial-session recovery. |
| **Lossy/lossless split compression (9–21× on depth files)** | MouseVUER | If we ever add depth/IR cameras, their compression pipeline is state-of-the-art for cheap long-term storage. Worth citing as prior art in the methods paper. |
| **Depth / 3D posture cameras (RealSense D435)** | MouseVUER | For the sleep-posture scoring goal with Prof. Kim Daewook's lab, a cheap depth module on one chamber could unlock posture-based vigilance classification on animals without EEG/EMG. |
| **SIESTA-compatible `.edf` export** | SIESTA | Our NWB export plan gets us most of the way. Explicitly target SIESTA compatibility so the data is analyzable with their open sleep-scoring tool for free. |
| **Public status page as a methods-paper figure** | (our own — none of them have one) | Worth a literal screenshot in the methods paper. "This is what operational reproducibility looks like." |

---

## What to put on slides vs. what to keep in speaker notes

**On Slide 32 (Comparison Table):**
- The 6-column table itself
- The 3 callouts under the table (MouseVUER scaling, Salem cheaper-but-tightly-coupled, OpenVEEG hardcoded to NI)

**On Slide 33 (Novel Contributions):**
- The 6 contribution bullets (with the new acquisition-agnostic one prepended)
- **In speaker notes:** the "Ideas we can borrow" table above + the sharp framing quote

**On Slide 34 (References) or a new backup slide:**
- The 4 papers as proper citations
- Each paper with its **single most distinctive feature** in one line so the audience remembers what each one *does*:
  - **Salem 2020** — cheapest per-chamber, custom UDP/TCP master/slave protocol
  - **OpenVEEG (2018)** — sub-ms LSL/NTP sync, hardcoded to National Instruments DAQ
  - **MouseVUER (2024)** — RGB-D depth cameras + 9–21× compression, one SBC per camera
  - **SIESTA (2025)** — post-hoc EEG/EMG sleep scoring on `.edf` files (no acquisition)

**Speaker notes on Slide 38 (Validation Plan, § 7):**
- Add: "Salem 2020 used an in-frame blinking LED to measure their ~33 ms frame sync. We can do the same on one chamber: hook an LED to a Pi GPIO, blink it on a known Radiens trigger, count frames between Radiens R_ON and the first lit-LED frame in the export. Gives us a real latency number without waiting for XDAQ wiring."

**Honest concessions — where to surface them:**
- **Slide 32 callout:** "Salem 2020 reaches ~$86/chamber by amortizing one master PC across 24 cameras with a custom socket protocol. We chose standard RTSP and hardware QSV decode — different design tradeoff."
- **Slide 36 (Software→Hardware Sync):** add to the "Current" card — "OpenVEEG already does sub-ms via LSL/NTP. Our XDAQ upgrade brings us to per-frame hardware alignment, one step beyond LSL." Reframes our roadmap as ambitious, not catching up.
- **Slide 33 speaker note:** "All four papers are open-source. Our edge isn't openness — it's what's *bundled around* the code: monitoring, incident reports, golden configs, fail-open engineering."

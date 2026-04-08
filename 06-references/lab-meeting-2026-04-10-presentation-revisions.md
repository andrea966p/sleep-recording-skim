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
- MouseVUER-specific notes to include **as a callout below the table** (Andrea's own observations, 2026-04-08):
  > "MouseVUER uses USB cameras, which means a PC must physically sit next to the cage. USB bandwidth limits how many cameras one PC can drive — typically 2–3 before the motherboard's USB controller saturates. Scaling to 4+ chambers requires multiple PCs. Storage requirements are also high, installation documentation is minimal, and several software dependencies are outdated."
- Placeholder for Andrea's own lit-research findings — leave empty rows for Salem et al. and OpenVEEG to be filled in after Andrea searches the literature.

**Papers to research (Andrea will do this, not the AI):**
- **Salem et al.** — [https://www.sciencedirect.com/science/article/pii/S2468067220300699](https://www.sciencedirect.com/science/article/pii/S2468067220300699)
- **OpenVEEG** (2018)
- **MouseVUER** — [https://www.nature.com/articles/s41598-024-52788-9](https://www.nature.com/articles/s41598-024-52788-9)

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

## Comparison points for literature research

You asked for the **axes of comparison** between this system and published ones, so you can drive your own lit search efficiently. For each axis, the value this system delivers is listed; find papers and compare:

1. **Camera architecture** — CSI / IP streaming vs USB
   - Ours: CSI cameras on Pi 5, RTSP over LAN, no PC required per cage
   - Compare against: USB-based systems (MouseVUER), IP-camera systems, GigE Vision systems
2. **Cost per chamber**
   - Ours: ~$294/chamber (at 4 chambers; $1,174 total ÷ 4)
   - Compare against: per-cage cost in each paper
3. **Chambers per host PC** (scalability ceiling)
   - Ours: 4 current, architecture scales to 8+ by adding Pi nodes; single NVR PC handles all of them
   - Compare against: systems that need a PC per cage or per few cages
4. **EEG acquisition coupling**
   - Ours: API-based, observer pattern, acquisition-system agnostic (swap one module)
   - Compare against: systems hardcoded to specific acquisition hardware or requiring EEG software modifications
5. **Sync mechanism and tightness**
   - Ours: software, ~1 s latency, ±2 s buffer (hardware sync via XDAQ planned)
   - Compare against: none / software timestamps / hardware triggers / TTL sync / PTP
6. **Multi-chamber independent metadata**
   - Ours: 4 independent per-chamber state machines, metadata per chamber, parallel experiments supported
   - Compare against: single-experiment-per-rig assumption in most tools
7. **Fail-safe / failure-mode design**
   - Ours: recording persists ON if daemon crashes; metadata optional; storage reserve guarantees EEG never starved
   - Compare against: systems that abort on any subsystem failure
8. **Long-term stability (multi-day / circadian)**
   - Ours: 30+ day stress test passed; hardware watchdog + crash canary + ping-monitor; documented incidents
   - Compare against: systems tested only for hours, or with no published uptime data
9. **Monitoring and alerting**
   - Ours: 16 Netdata alerts + 7 Uptime Kuma monitors + Slack integration + public status page
   - Compare against: systems with no operational monitoring story
10. **Documentation & reproducibility**
    - Ours: 38+ vault pages including golden configs, incident reports, step-by-step procedures, variable system for production values
    - Compare against: papers with minimal setup documentation, GitHub repos with only code
11. **Orchestration pattern**
    - Ours: MQTT pub/sub → loose coupling, components can be restarted independently
    - Compare against: monolithic or tightly-coupled control software
12. **Hardware sync upgrade path**
    - Ours: planned XDAQ GPIO wiring → per-frame alignment; JSON sidecar schema already reserves the fields
    - Compare against: systems with no upgrade path or requiring full rewrites
13. **Open-source status and licensing**
    - Ours: Python daemon + React frontend on GitHub (private now, public-ready)
    - Compare against: closed-source commercial, partial-source research code, fully open
14. **Storage management and retention policy**
    - Ours: 7-day rolling retention, 200 GB hard reserve, automatic NAS offload (pending Tailscale)
    - Compare against: manual cleanup, no retention logic, no offload

**Papers to start with:**
- MouseVUER — https://www.nature.com/articles/s41598-024-52788-9
- Salem et al. — https://www.sciencedirect.com/science/article/pii/S2468067220300699
- OpenVEEG (2018) — https://www.sciencedirect.com/science/article/pii/S0920121118301244
- SIESTA (2025), SAGER (2025), Spyglass (2024), FERAL (2025) — already referenced in `06-references/progress-meeting-2026-03-12.md`
  https://journals.sagepub.com/doi/10.1177/07487304251336649?url_ver=Z39.88-2003&rfr_id=ori:rid:crossref.org&rfr_dat=cr_pub%20%200pubmed
  

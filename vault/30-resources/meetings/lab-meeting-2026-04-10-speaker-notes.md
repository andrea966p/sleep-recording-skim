---
type: meeting
area: video-nvr
status: done
tags: [presentation, speaker-notes, preparation]
created: 2026-04-09
related: ["[[lab-meeting-2026-04-10-presentation-brief]]", "[[lab-meeting-2026-04-10-presentation-revisions]]"]
---

# Speaker Notes & Background Knowledge — Lab Meeting 2026-04-10

> Everything compiled from the 2026-04-09 prep session. Organized by slide. Each section has **what to say** (out loud) and **background knowledge** (for your own understanding — don't read this off the slide).

---

## § 1 — Software Stack

### What to say — one line per component

- **go2rtc:** "This is the streaming server on each Pi. It takes the raw camera feed and makes it available over the network as a standard video stream that any player or recorder can consume."
- **Frigate:** "This is the recorder. It pulls the streams from both Pis and writes video to disk. Think of it as the DVR of the system."
- **Mosquitto MQTT:** "This is the messenger. When the daemon needs to tell Frigate to start or stop recording, it sends a message through Mosquitto — a lightweight pub/sub protocol, like a walkie-talkie channel any component can listen to."
- **Session Daemon:** "This is the brain. It watches Radiens, and the moment you start an EEG recording it tells Frigate to start video. When you stop, it stops video and exports the clips automatically."
- **Desktop UI:** "This is the only thing a lab member needs to touch. Set the mouse ID and recording type, then forget about it."
- **Netdata + Uptime Kuma:** "These are the watchmen. Netdata tracks hardware health — temperature, CPU, disk. Kuma checks that every service is alive and sends a Slack message if something goes down."

### What is Tauri (if anyone asks)
Tauri is the framework that turns the React web UI into a native desktop app — so it opens as a proper installed window, not a browser tab. If asked: *"it's the desktop app framework, like Electron but much lighter."*

### Background knowledge — MQTT & Mosquitto
MQTT is a messaging protocol built around a shared "board" called a **broker**. Components don't talk to each other directly — they post messages to the broker and anyone subscribed to that topic reacts. **Mosquitto** is the software running that broker on the NVR. Every message has a **topic** (address) and **payload** (content). The daemon posts to `frigate/pi_cam_0/recordings/set` with payload `ON` or `OFF`. Frigate subscribes and reacts. If the daemon crashes, the broker still holds the last message — which is why recording persists ON if the daemon dies. Analogy: a lab group chat. You post "start recording", everyone who cares acts on it.

### Bridge from Software Stack → Hard Rules slide
> "So that's the stack on paper. In practice, getting all of these to work together reliably took a few months and a number of failures — and those failures produced some rules that are now baked into every deployment decision I make."

---

## § 1 — Hard Rules

### What to say (~75 seconds total)

**Opening:**
> "Every rule on this slide is the result of something breaking in production. I didn't read these in a blog post — each one is a lesson paid for with a failed experiment or a 2 AM debugging session."

**H.264 only:**
> "When I tried H.265 hardware encoding on the Pi 5, it caused full kernel panics — the Pi would freeze and need a power cycle. Not a software crash, a kernel crash. H.265 is permanently off the table."

**KillMode=control-group:**
> "Without this setting, when systemd restarts go2rtc, the parent process dies but the child rpicam-vid processes stay alive as zombies — duplicate camera processes fighting over the hardware. Control-group mode kills the whole process tree together."

**rpicam-vid direct exec:**
> "I tried the ffmpeg pipe version first. It broke under network jitter because a broken pipe at one end cascades through the whole chain. One process, one failure point, much more robust."

**apt-mark hold Docker:**
> "The GUI software updater on Ubuntu silently upgraded Docker in the background, restarted Frigate, which re-read its config and started recording all four cameras — even though no experiment was running. I found hours of junk footage the next morning. Now Docker is pinned."

**MPEG-TS:**
> "MPEG-TS is resilient to mid-stream interruptions — it's what broadcast TV uses. Once I switched, I got my first 30+ day continuous uptime run."

**Close:**
> "These aren't arbitrary choices. Every one is documented in an incident report with the symptom, the root cause, and the fix — so nobody in the lab has to rediscover any of this."

*If running long: drop rpicam-vid and MPEG-TS. H.264, zombies, and Docker are the memorable three. Docker story is the audience-grabber — slow down there.*

### Background knowledge — Kernel
The kernel is the deepest layer of the OS — the code that talks directly to hardware. All software sits on top of it. A **kernel panic** means the kernel itself crashed, not just a program — the whole computer freezes, requires a power cycle. Nothing running on the system can fix it because the kernel is what everything else depends on. When you say "H.265 caused kernel panics," the audience should understand: not a software error, the *entire machine froze*.

### Background knowledge — MPEG-TS vs MP4
MP4-style containers write a table of contents at the very end of the file (called the `moov` atom). If the stream drops mid-recording, the table never gets written and the whole file is unreadable. This is exactly what happened in the March 6th incident — a 19 GB unplayable file. MPEG-TS is structured in self-contained chunks, so losing a few seconds just drops those frames — the rest of the file is still perfectly readable.

### Background knowledge — rpicam-vid exec vs ffmpeg pipe
A **pipe** connects two processes: process A writes to stdout, process B reads from stdin. If either end breaks (network jitter, crash), the pipe breaks and both fail. With `rpicam-vid` going directly into go2rtc as an exec command, go2rtc manages the process directly — it can restart it without breaking the stream chain.

---

## § 6 — Key References

### What to say
> "Before the comparison — let me quickly place each paper. Salem's group at NIH built MouseVUER, a depth-camera home-cage system for mice — the most direct comparison to what we do. OpenVEEG is the only other system that couples video with EEG acquisition in real time. SIESTA is a sleep scoring tool, not an acquisition system — it takes EEG files you already recorded and classifies sleep stages. FERAL is a very recent Rockefeller preprint that extracts behavior from video without pose estimation — relevant to where we want to go analytically. Spyglass is a data management framework relevant to our NWB and DANDI reproducibility roadmap."

### Background knowledge — each paper
- **MouseVUER (Salem et al. 2024):** Same first author (Ghadi Salem, NIH) as the 2020 DVR paper — MouseVUER is the evolution: mice instead of fruit flies, Intel RealSense D435 depth cameras instead of Pi cameras. Published Nature Scientific Reports. Full details below in § 6 comparison section.
- **OpenVEEG (2018):** Uses LabStreamingLayer (LSL) — a neuroscience synchronization library that aligns multiple data streams using a shared clock, achieving sub-millisecond alignment. Hardcoded to National Instruments DAQ hardware. Achieves ~33 ms video↔EEG sync.
- **SIESTA (2025):** Post-hoc only. Give it a standard `.edf` EEG file → it classifies sleep stages automatically. Never touches live acquisition. Relevant because if our NWB/edf exports are compatible, our data can be scored by SIESTA for free.
- **FERAL (2025, Rockefeller):** Feature Extraction for Rodent Activity and Locomotion. Uses pixel-level statistics from video — no pose estimation, no labeled training data — to classify behavior. Sidesteps the DeepLabCut labeling overhead entirely.
- **Spyglass (eLife 2024):** Python framework built at UCSF for managing neuroscience datasets reproducibly. Wraps NWB files, tracks analysis provenance, integrates with DataJoint. Directly relevant to our long-term DANDI archive goal.

---

## § 6 — Six Novel Contributions

### What to say
> "The first and most important: the sync pattern is acquisition-agnostic. The code that watches Radiens is isolated in one Python module. Swap that module and the entire rest of the system — recorder, messaging bus, GUI, export logic — stays identical. Any EEG system with an API can be integrated."

> "Second: to my knowledge this is the first open-source implementation of Frigate coupled to NeuroNexus Radiens via the AllegoClient API. Nobody has published this before."

> "Third: each of the four chambers maintains its own independent state. You can record a different mouse with a different protocol in each chamber simultaneously — each gets its own metadata, its own export. MouseVUER, the closest competitor, has no per-chamber independence."

> "Fourth: everything goes through MQTT, which means any component can crash or restart without taking the others down. If the daemon dies mid-experiment, Frigate doesn't notice and keeps recording."

> "Fifth, and I think most underappreciated: none of the four published systems have any operational monitoring. No thermal alerts, no service heartbeats, no Slack. Ours does. For circadian recordings running unattended for days, this isn't a nice-to-have."

> "And sixth: ~$1.2k versus $5–20k commercial, fully documented and reproducible."

### Background knowledge — AllegoClient API
The AllegoClient is NeuroNexus's Python SDK for Radiens — normally used to pull electrophysiology data programmatically. Using it to detect recording state transitions (R_OFF → R_ON) as a video trigger is unconventional — the API wasn't designed for this. That's why no one has published this integration before.

### Background knowledge — fail-safe via MQTT
MQTT is a **stateful** protocol: the broker stores the last message on each topic even after the publisher disconnects. When the daemon publishes `ON` and then crashes, the broker still holds that state — Frigate keeps reading it and keeps recording. This is not an accident; it's a deliberate architectural choice.

### Background knowledge — "monitoring as a contribution"
Unusual to claim in a methods paper, but the gap is real and documented. None of the four papers describe what happens when a component fails during a 72-hour circadian run. This system does — and has the incident reports to prove it.

---

## § 6 — Literature Comparison: Architecture & Cost

### What to say
> "On architecture and cost. **We drop Salem 2020 from the direct comparison** — that paper is a fruit fly monitoring system using a custom socket protocol; different animal model, different use case. The relevant head-to-head is MouseVUER."

> "MouseVUER uses Intel RealSense D435 depth cameras — RGB plus infrared depth — mounted over cages. Each camera has its own dedicated Auvidea TX2 SBC for compression, housed in a custom enclosure called the Power and Control Module. Three cameras = three dedicated computers. For four chambers that's four extra computing units before you even count the storage PC."

> "Our four chambers run off a single NUC at 9 to 12 percent CPU. The Pis stream, the NVR handles everything centrally. Adding more chambers means adding cheap Pi nodes — nothing else changes."

> "There's also a physical constraint MouseVUER doesn't advertise prominently: the system only works with Allentown NexGen ventilated racks. If your facility uses a different rack, you'd need to redesign the entire enclosure, which itself requires a 3D printer and laser cutter to reproduce. And installing it cuts your cage mouse capacity from 5 down to 3, and halves your rack storage capacity because the camera enclosure occupies the slot above the monitored cage."

> "Our system mounts anywhere, doesn't modify the cage, and doesn't touch the rack."

### Background knowledge — Intel RealSense D435
The D435 is a USB 3.0 depth camera. It works by projecting infrared dots onto the scene (structured light + stereo IR) and computing the distance of every pixel — producing a 2D + depth frame simultaneously. This enables 3D posture reconstruction without multi-camera triangulation. The tradeoff: it requires its own dedicated compute for the depth compression (hence the Auvidea TX2 SBC per unit), and the uncompressed data is enormous (~1 GB/min from all 3 streams per cage).

### Background knowledge — Auvidea TX2 SBC
Based on NVIDIA Jetson TX2 — a powerful embedded AI/compute board (~$200–400). MouseVUER uses it as a dedicated compression unit per camera. This is why their system is polished but expensive and hard to scale: a custom AI compute board per camera is overkill for simple H.264 video. Your Pi 5 + Pi camera module approach offloads H.264 encoding to the Pi's hardware block (essentially free) and streams standard RTSP. No special hardware needed at the camera end.

### Background knowledge — Intel QSV
Intel Quick Sync Video is a dedicated hardware decode/encode engine in Intel iGPUs. Frigate uses it on the NVR to decode the incoming H.264 streams from all 4 cameras without using CPU cycles. That's why the NUC sits at 9–12% CPU — the processor barely participates in video decoding.

### MouseVUER limitations — from the paper directly
- Only compatible with Allentown NexGen racks
- Cage mouse capacity: 5 → 3 (cage space lost to modified hopper)
- Rack storage capacity halved (camera enclosure occupies cage slot above)
- Requires 3D printer + laser cutter to reproduce
- No cost breakdown published
- No EEG integration, not even mentioned as future work (only LED lighting)
- No monitoring or alerting
- No long-term reliability data or uptime figures
- No retention policy for storage
- DeepLabCut analysis present but authors note "currently lacks open-source scalable enclosure design with associated video analysis methods"

---

## § 6 — Literature Comparison: Sync & Openness

### What to say
> "On synchronization — we're honest. Our software sync is about one second, good enough for behavioral analysis, not for correlating individual spikes with specific video frames. OpenVEEG achieves sub-millisecond sync using LSL, purpose-built for neuroscience data alignment. That's genuinely better than what we have today."

> "But OpenVEEG is architecturally locked to National Instruments DAQ hardware. Our system is hardware-agnostic by design — swap one module to support a different acquisition system. The XDAQ hardware sync on our roadmap goes beyond LSL precision without sacrificing that flexibility."

> "On openness: all four papers are open-source, so that's not our differentiator. The real difference is what's around the code. Salem's 2020 DVR requires Python 3.4 and Visual Studio 2010 — a 15-year-old toolchain, effectively unmaintainable today. OpenVEEG is a monolithic C++ app. Our stack is React 19, Tauri v2, Docker, MQTT — modern, modular, each piece replaceable. The edge isn't that we're open. It's that we're open *and* operational."

### Background knowledge — LSL (LabStreamingLayer)
Open-source system built specifically for neuroscience data acquisition. Every data sample (EEG sample, video frame) gets a timestamp from a shared network clock. LSL continuously measures and corrects clock offsets between devices, achieving sub-millisecond alignment. Post-hoc, you can align any two streams by their timestamps. OpenVEEG achieves ≤33 ms video↔EEG alignment this way. Your system doesn't use LSL — Radiens and Frigate have independent clocks, and the only alignment is the ~1 s polling boundary. Adding an LSL outlet to the daemon is a realistic intermediate step before XDAQ GPIO wiring.

### Background knowledge — the sync hierarchy
1. **Our current:** software poll, ~1 s latency — good for behavioral segments
2. **LSL/NTP (OpenVEEG):** software sync, ≤33 ms — good for event-level alignment
3. **XDAQ GPIO wiring (our roadmap):** hardware sync, <1 ms — per-frame spike alignment

When asked "is the sync good enough?": *"Good enough for behavioral analysis — we can say what the animal was doing during a recording. For spike-to-frame alignment we have a hardware upgrade planned, and the architecture is already designed to accommodate it without rewriting anything."*

### Background knowledge — monolithic vs modular
OpenVEEG is monolithic: video capture, EEG acquisition, and sync are one program. Change one part, risk breaking the others. Our system is modular: daemon, Frigate, MQTT, and GUI are four separate processes communicating through defined interfaces. Each can be updated, restarted, or replaced independently.

### Background knowledge — "modern toolchain" argument
Python 3.4 (Salem 2020 DVR) reached end-of-life in 2019. Installing it on Ubuntu 24.04 requires manual workarounds. A lab trying to adopt that system in 2026 spends hours just on dependencies. React 19 and Tauri v2 are current as of today. This is a practical reproducibility argument, not a cosmetic one.

---

## Salem 2020 vs MouseVUER 2024 — clarification

**Same first author.** Ghadi Salem at NIH CIT is first author on both. MouseVUER is the same group's evolution.

- **Salem 2020** (HardwareX): Multi-camera DVR on Raspberry Pis, demonstrated on **fruit flies**, custom UDP/TCP protocol. Relevant only as a cost benchmark — drop from the direct comparison for the presentation.
- **MouseVUER 2024** (Nature Sci. Rep.): Depth cameras, **mice**, home cage, full enclosure engineering — this is the relevant comparison for your lab.

**Do not compare against Salem 2020 in the talk.** It's a different animal model and a fundamentally different scope.

---

## Sharpest line — use as transition into § 6

> "Four published systems handle pieces of this problem. OpenVEEG syncs tighter. MouseVUER captures depth. SIESTA scores sleep. FERAL classifies behavior. None of them is production-operational the way a neuroscience lab actually needs — no monitoring, no incident response, no fail-open design, no documentation you can hand to a new lab member. That gap is where this system lives."

---

## Updated head-to-head: NeuroSurveillance vs MouseVUER

| Axis | MouseVUER 2024 | NeuroSurveillance |
|---|---|---|
| Camera type | Intel RealSense D435 (RGB-D) | Pi CSI module (RGB only) |
| Depth / 3D posture | Yes — key advantage | No |
| EEG integration | None, not planned | Radiens API; XDAQ hw sync roadmap |
| Rack dependency | Allentown NexGen only | Any cage, any rack |
| Cage modification | Cuts 5 → 3 mice per cage | No cage modification |
| Rack storage impact | Halved (camera occupies slot above) | None |
| Compute per camera | 1 Auvidea TX2 SBC | 2 cameras per Pi, 1 NUC for all |
| Fabrication required | 3D printer + laser cutter | No custom fabrication |
| Monitoring/alerting | None | 16 Netdata + 7 Kuma + Slack |
| Long-term reliability | No data published | 30+ day stress test documented |
| Storage retention | No policy published | 7-day automated rolling retention |
| Cost | Not published | Full BOM in vault |
| Uptime hardening | None described | EEPROM, watchdog, crash-canary |

**What MouseVUER does better:**
- RGB-D depth → 3D pose estimation without multi-camera triangulation
- Polished enclosure with CAD files
- DeepLabCut integration out of the box
- Nature Sci. Rep. publication — high visibility

**What we do better (all sourced):**
- EEG integration (only system in comparison that has it)
- Rack and cage agnostic
- No fabrication requirement
- Full operational monitoring stack
- Documented uptime and reliability
- Automated storage management
- Hardware sync upgrade path

---

## Technical concepts — personal reference

### REST API
Two programs talking over a network through defined request/response URLs. GET = asking for data. POST = sending data. Your Flask API on `127.0.0.1:8585` is what the desktop UI talks to. Analogy: a waiter (API) carrying orders between the dining room (UI) and the kitchen (daemon). The kitchen doesn't need to know what the dining room looks like.

### JSON, sidecars, metadata
JSON is a human-readable text format for structured data (`{"mouse_id": "HETCF3R1", "type": "basal"}`). **Metadata** = data about data (the experimental context, not the video itself). A **sidecar file** is a companion file that lives next to the main file — for every `.mp4` export there's a `_session.json` right beside it. Analogy: a histology slide (video) and the label on the slide (sidecar JSON).

### RTSP, ffmpeg, MPEG-TS
- **RTSP:** the network protocol for live video streaming. Like a URL for a video stream — `rtsp://192.168.0.11:8554/pi_cam_0`. Standard protocol used by all IP cameras and NVR software.
- **ffmpeg:** a command-line tool that can encode, decode, and convert any video format. Extremely powerful but fragile in pipes. You deliberately excluded it from the critical streaming path.
- **MPEG-TS:** a container format resilient to interruptions — self-contained chunks, if you lose some frames the rest is still readable. What broadcast TV uses. Alternative (MP4) writes its table of contents at the very end — if the stream drops, the whole file is unreadable (the March 6th 19 GB corruption incident).

### Flask API
Flask is a Python library for building web servers. You write functions that respond to URLs; Flask handles all the networking. It runs in a background thread so the main daemon loop (polling Radiens) and the API (serving the UI) run in parallel without interfering.

### LSL and per-frame ms-level alignment
LSL (LabStreamingLayer) synchronizes data streams from different devices using a shared clock. Every EEG sample and every video frame gets a timestamp in the same coordinate system. Post-hoc alignment to sub-millisecond precision. Our current setup doesn't use LSL — sync latency is ~1 s. Adding LSL is a realistic intermediate step. XDAQ GPIO wiring (hardware pulse into both Pi and XDAQ simultaneously) is the full solution — same electrical event triggers both, zero clock-drift ambiguity, per-frame alignment.

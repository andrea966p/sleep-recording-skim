---
type: meeting
area: video-nvr
status: done
tags: [presentation, lab-meeting, script]
created: 2026-04-10
---

# Lab Meeting Transcript — 2026-04-10

Spoken transcript per slide. Read it as written, adapt as you go.

---

## Slide 1 — Title

"Good morning everyone, thanks for being here. Today I'm going to walk you through NeuroSurveillance, the video monitoring system I've been building for our chambers. The pitch in one sentence: it's an open, low-cost, EEG-synchronized video system designed specifically for long circadian recordings. As of this past Monday, April 6th, it's been running in full production."

---

## Slide 2 — At a Glance

"Before I get into the details, here are the numbers that matter. The total hardware cost, including the recording PC, is about eleven hundred and seventy-four dollars. It currently runs four cameras spread across two Raspberry Pi nodes, twenty-four hours a day, seven days a week. The synchronization between the EEG and the video is around one second, and I'll explain later why that's a deliberate choice and not a limitation. The system has sixteen custom monitoring alerts watching it constantly, and the whole thing is documented across more than thirty-eight pages in an Obsidian vault that lives in a GitHub repo.

Four words I want you to keep in mind for the rest of the talk: it's reproducible, because the documentation is exhaustive enough that anyone in the lab can rebuild it; it's open-source, meaning nothing in the stack requires a license or a subscription; it's modular, so when something fails I can swap or fix that single piece without touching the rest; and it's scalable, because the only real ceiling is budget, not architecture."

---

## Slide 3 — Hardware Recap

"Quick recap of the hardware for anyone who hasn't seen the previous talks. The brain of each edge node is a Raspberry Pi 5, which has a quad-core ARM Cortex-A76 running at 2.4 GHz, LPDDR4X memory, and the new RP1 I/O controller. The cameras are the OV5647 module — five megapixels, a wide-angle 160 degree fisheye lens, and they're the NoIR variant with built-in infrared LEDs at 850 nanometers, which is invisible to the mice but gives us clean night-time footage out to about three meters. That's why we can record continuously through the dark phase without disturbing the animals."

---

## Slides 4–6 — (visual / blank)

*No script — let the visuals or photos speak. If they're empty, skip past quickly.*

---

## Slide 7 — Agenda

"Here's where we're going. I'll cover the current state of the setup, then the alerting and monitoring layer, then the Python session daemon that ties everything together, then the desktop GUI you'd actually use as a researcher, then how storage is managed, then how this compares to recent published systems, then what's coming next on the hardware-sync side, and finally why all of this matters specifically for circadian work. About twenty-five minutes, then questions."

---

## Slide 8 — Section 1

"Let's start with the current state of the setup."

---

## Slide 9 — System Topology

"This is the topology of the whole system, and it's worth taking thirty seconds on. On the left you have the mouse chambers themselves. Each chamber has a camera, and the cameras are wired directly into one of two Raspberry Pi 5 nodes — Pi number one at 192.168.0.11, and Pi number two at 192.168.0.12. Each Pi handles two cameras. Those Pis stream H.264 video over RTSP across the lab network to the recording PC, which is the ASUS NUC at 192.168.0.50. That NUC is running Frigate inside Docker, with Intel QuickSync doing the hardware H.264 decoding, alongside the Mosquitto MQTT broker, the session daemon, and the monitoring stack. From there, the plan is to push long-term storage onto the Synology NAS over Tailscale — that link is configured but not yet live, and I'll come back to that. Slack alerts come off the side of the NVR for both downtime and recovery events.

The whole thing is four cameras, recording 1024x768 at fifteen frames per second, H.264 only, going through two Pi nodes into one NVR and eventually out to the NAS."

---

## Slide 10 — Hardware

"Going one level deeper on hardware. The two Pi 5s each handle dual CSI cameras, so four cameras total. They're powered over Ethernet through Waveshare PoE HATs, which means a single cable per Pi handles both data and power, and the EEPROMs on those Pis have been hardened with custom power settings to survive PoE transients — that's a fix that came out of an incident I'll talk about later.

The recording PC is an ASUS NUC 14 Pro with the Intel Core Ultra 5 125H, fourteen cores total, and an Intel Arc integrated GPU which is what gives us the QuickSync hardware decode. Thirty gigs of RAM, a 1.9 terabyte NVMe, running Ubuntu 24.04 LTS.

The EEG side is the NeuroNexus xDAQ Core, sixteen to thirty-two channels, controlled by the Radiens software with the AllegoClient SDK. The session daemon is what synchronizes the video to the EEG with about a one-second latency.

And finally the Synology NAS, which is the long-term storage tier. As I mentioned, the Tailscale tunnel to it is still pending."

---

## Slide 11 — Software Stack

"On the software side, six pieces. On each Pi, there's go2rtc — that's a lightweight RTSP server that takes the camera feed directly from rpicam-vid and exposes it on the network, with no ffmpeg pipe in between. On the NVR there's Frigate, which is a Dockerized open-source NVR that does the actual recording, and it's using Intel QSV for hardware decoding. Mosquitto is the MQTT broker — that's the pub/sub message bus that lets the daemon and Frigate talk to each other in a loosely coupled way. The session daemon itself is Python 3.12 with Flask, and that's the glue between Radiens and Frigate. The desktop UI is Tauri version 2 with React 19 and TypeScript. And the monitoring is Netdata for metrics and alerts plus Uptime Kuma for service heartbeats, both wired into Slack.

The important point: every single one of these pieces is either inside a Docker container or managed by systemd. Nothing runs ad-hoc, nothing is started by hand, nothing is at the mercy of someone forgetting to launch it."

---

## Slide 12 — Hard Rules

"Now I want to spend a moment on this slide because it's not just a list of rules — every single one of these traces back to a real incident that I had to debug at some point in the last two months.

First, H.264 only. We tried H.265 hardware encoding on the Pi 5 because it would have given us better compression. It caused kernel panics. Permanently abandoned, and now it's a written rule in the vault.

Second, KillMode=control-group in systemd. Without that flag, when systemd restarts the parent process, the child rpicam-vid processes don't get killed — they stay alive as zombies, and the next instance can't grab the camera because the old one is still holding it. Took me hours to figure out the first time.

Third, rpicam-vid runs as a direct exec, not piped through ffmpeg. The earlier setup had a pipeline of camera into ffmpeg into go2rtc, and any tiny network jitter would tear that pipeline apart. Direct exec means one process, one failure point, no cascading.

Fourth, apt-mark hold on the Docker packages. The Ubuntu GUI updater silently restarted Frigate one night, which kicked off a wave of unexpected recordings and started filling the disk. Now the Docker packages are locked.

And fifth, MPEG-TS as the container format instead of MP4. There was an incident where I lost a 19 GB file because MP4 puts its metadata at the end, the moov atom — and if the recording dies before that's written, the entire file is unrecoverable. MPEG-TS is chunked: lose a few frames at the end, you keep everything before. After all of these fixes, the system has hit thirty-plus days of continuous uptime."

---

## Slide 13 — Section 2

"Alright, second section: alerts and resource monitoring."

---

## Slide 14 — Why Instrument

"Why bother instrumenting this so heavily? Three reasons.

First, silent failures are worse than loud ones. If a Pi dies at two in the morning during a circadian recording and there's no alert, nobody finds out until they walk in the next morning, and by then you've lost eight hours of data. A loud failure that pages me at 2 AM is annoying; a silent one ruins an experiment.

Second, when something does break, you can't just react after the fact. You need to know what the system looked like in the seconds and minutes before the crash. That means continuous logging, not waiting until something goes wrong and then trying to figure out what happened.

And third, there are many different failure modes here — network, power, thermal, disk, software — and each one needs a different sensor. No single monitoring tool covers all of them, which is why there are multiple layers."

---

## Slides 15 / 16 — Netdata 16 Alerts

"This is the Netdata side. Netdata is running on the NVR with sixteen custom alert rules that I wrote, and as of last Monday they're all clear. The alerts cover the full operational surface: CPU usage with separate warning and critical thresholds at 85 and 95 percent, CPU iowait above 40 percent, RAM availability dropping below 10 or 5 percent, swap usage above 50 percent, disk space, inode exhaustion, CPU package temperature, and the health of the Docker containers — Frigate, Mosquitto, and Kuma. There are seven more alerts beyond what's shown.

The detail that took the longest to get right is the bottom line: every alert has a 15-minute recovery delay and split trigger and clear thresholds. Without that, you get alert flapping — the metric crosses the line, fires an alert, drops back, fires a recovery, crosses again, and you end up with a hundred Slack notifications for one event. With hysteresis, you get exactly one alert per real incident."

---

## Slides 17 / 18 — Uptime Kuma

"Uptime Kuma is the second monitoring layer, and it does something different from Netdata. Instead of watching metrics on the NVR, it actively pings each service to confirm it's reachable and responsive. There are seven monitors: go2rtc on Pi one, go2rtc on Pi two, the Frigate API, the Mosquitto broker, the session daemon's health endpoint, Netdata itself, and Kuma's own self-check.

All of this rolls up into a public status page at the URL on the screen, and Slack gets pinged on both downs and recoveries, so you always see the full lifecycle of an incident."

---

## Slide 19 — What is a Watchdog

"A few of you have asked me what a watchdog is, so let me define it once. A watchdog is a piece of code whose only job is to notice when something has stopped working and take action. That's it. It doesn't do anything useful in normal operation — it just sits there waiting for something to break.

This system has four of them, and the reason there are four and not one is that each watchdog catches a different class of silent failure. A kernel hang, where the entire Pi is frozen. A thermal slow-death, where the temperature creeps up over hours until something gives. A PoE power latch, where the Pi loses power and goes silent. And single-process crashes, where go2rtc or the daemon exits but the rest of the OS is fine. Each of those needs a different mechanism, and that's why there are four layers."

---

## Slide 20 — The Four Layers

"Going through them one by one.

The hardware watchdog is the deepest layer. It's a kernel-level timer with a 30-second runtime budget. If the kernel itself stops responding — meaning even the operating system has hung — the timer expires and triggers a hardware reset. This is the only thing that catches total lock-ups, because anything running in software can't help you when the software itself is frozen.

The crash-canary is a small bash script I wrote that logs CPU temperature, throttle status, CPU load, and free memory every 30 seconds to a file on disk. It does nothing useful while the Pi is healthy. But if the Pi dies, the last 30 seconds of vitals are sitting on disk, and I can figure out exactly what was happening in the moments before the crash. It's pre-crash forensics.

The pi-monitor script runs on the NVR, not on the Pi. Every two minutes, the NVR pings each Pi over the network. If a Pi stops responding, the NVR fires a Slack alert. This is the only layer that catches PoE failures, because a Pi with no power obviously can't report its own death — somebody else has to notice.

And the fourth layer is systemd's Restart=always policy on go2rtc and the session daemon. If either of those crashes, systemd restarts them within seconds. This is the fine-grained recovery for single processes.

You need all four because each one catches a failure class the others miss."

---

## Slide 21 — Thermal Spike Incident

"I want to walk through one real incident from a week and a half ago because it's a good example of why all of this monitoring exists.

The symptom was that the NVR's CPU package temperature was hitting 87 to 92 degrees Celsius, with sudden spikes up to about 100, and it was happening on a regular cycle every 35 to 40 minutes. Netdata caught it and fired the temperature warning alert.

I went in with journalctl, htop, intel_rapl, and the Netdata charts, and I traced it back to allegoserver — that's the Radiens server process — busy-polling on a USB endpoint at 109 percent CPU. So the EEG software was thermally beating up the recording PC.

The fix was to create a small systemd service called cpu-power-cap.service that uses Intel RAPL to cap the CPU package power at 20 watts. After the fix, the baseline dropped to about 58 degrees, which gives me 17 degrees of headroom before the alert fires again.

The point of the story is this: the monitoring caught the problem before it became a data-loss incident. That's the whole reason all of this instrumentation exists."

---

## Slide 22 — Section 3

"Third section, and probably the meat of the talk: the Python session daemon."

---

## Slide 23 — The Glue

"The daemon is the glue between Radiens, which controls the EEG, and Frigate, which controls the cameras. The way it works in practice is this: when you start an EEG recording in Radiens through your normal workflow, the daemon notices within one second and tells Frigate to start recording from the cameras attached to the chamber you're using. When you stop the EEG recording, the daemon stops the cameras and exports the matching video clips, each one wrapped with a JSON metadata sidecar that captures everything about the session.

It runs as a systemd service called neurosurveillance-session on the NVR. It's Python 3.12, using paho-mqtt for the messaging and the Radiens AllegoClient SDK to talk to the EEG software. And it exposes a Flask REST API on localhost port 8585. The source lives in a private GitHub repo called neurosurveillance."

---

## Slide 24 — Architecture Diagram

"Here's the internal architecture. On the left, Radiens via AllegoClient. On the right, Frigate writing recordings to disk and the Tauri desktop UI. In the middle, the daemon, broken into modules.

The radiens_poller hits AllegoClient.get_status every second and watches for transitions between recording-off and recording-on. The session_manager keeps the per-chamber state — which mouse is in which chamber, what type of recording it is, when it started. The storage_monitor enforces the 200 GB EEG reserve in the background. The frigate_controller does the MQTT publish and subscribe and the export API calls. And the Flask API is the front door for the desktop UI.

Each module has exactly one job. The orchestrator, daemon.py, is just a one-second poll loop that runs all of them."

---

## Slide 25 — 4 Design Decisions

"Four design decisions that explain why this system won't lose your data, and they're all deliberate.

First, the autonomous core. If the daemon crashes mid-session, Frigate keeps recording. The MQTT recording state persists in the broker, so even though the orchestrator is dead, the cameras don't stop. You get a Slack alert that the daemon is down, but no data is lost.

Second, metadata is optional. If you forget to set the Mouse ID before starting Radiens, the session is recorded anyway with the metadata field set to 'unknown'. You can rename the file afterwards. The system never refuses to record because of missing metadata.

Third, multi-chamber independence. Each of the four chambers has its own state machine running in parallel. You can record four different mice, in four different experiments, with four different metadata blocks, simultaneously, and they don't interfere with each other.

And fourth — this is maybe the most important one philosophically — the daemon only OBSERVES Radiens. It never controls it. The researcher stays in charge of the EEG acquisition. The daemon polls passively and reacts. It will never touch your EEG workflow."

---

## Slide 26 — Module Table

"This is just a more detailed breakdown of the modules I showed in the diagram. The one I'd flag specifically is manual_session_mgr — that's the module that handles the case where you press the Record button directly in Frigate without going through Radiens, and it has a five-second minimum duration filter, which exists specifically to prevent accidental clicks from creating empty exports."

---

## Slide 27 — Sync Tightness

"Now I want to be honest about sync tightness because this is the question I expect to get. The Radiens poll interval is one second. The export timestamp buffer is plus or minus two seconds. There are four independent state machines, one per chamber.

This is software-level synchronization. It is good enough for behavioral analysis — locomotion, sleep posture, grooming, anything where the relevant timescale is hundreds of milliseconds or longer. It is NOT good enough for spike-to-frame alignment, where you'd want millisecond precision. That's the upgrade I'll come back to in section seven, with the XDAQ hardware sync."

---

## Slide 28 — Flask REST API

"The Flask API on localhost. Quick tour: there's a status endpoint that returns the full daemon state, endpoints to set and clear session metadata, endpoints to query the current and historical sessions, a manual sessions endpoint, a health endpoint that returns 200 if everything is connected and 503 if not, and storage endpoints — including a size estimator and a live bitrate query that asks the cameras directly how much bandwidth they're using. All of this is bound to localhost, so the only thing talking to it is the desktop UI on the same machine."

---

## Slide 29 — Section 4

"Fourth section: the desktop GUI. This is the part you would actually interact with as a researcher."

---

## Slide 30 — Tauri Stack

"On the technology side, the desktop app is built with Tauri version 2, React 19, TypeScript 5.8, and Vite 7. The styling uses Tailwind CSS with the DaisyUI component library, and dark mode is the default. Minimum window size is 1024 by 700, default opens at 1400 by 900. And the build pipeline produces a Debian package, so installing it is as simple as a dpkg install."

---

## Slide 31 — 7-Step Workflow

"Here's the full workflow you'd follow as a researcher. Seven steps.

Step one, open the NeuroSurveillance Session Controller — that's the desktop app. Step two, for each chamber you're using, fill in the Mouse ID, pick the recording type from the dropdown, pick your name from the lab member dropdown, and click Set Metadata. Step three, start the EEG recording in Radiens — your normal workflow, the daemon doesn't touch it. Step four happens automatically: the video starts on all four cameras within one second, because the daemon detected the Radiens transition. Step five, run your experiment — the daemon is silent, you don't have to do anything. Step six, stop the EEG in Radiens, and the video automatically stops and exports with the metadata you set. Step seven, check the Session History panel in the app to confirm everything completed and to see the file paths.

The whole point of this design is that in the normal case, you do exactly what you would have done anyway with Radiens, and the video happens for free."

---

## Slide 32 — UI Components

"Quick tour of what's actually on the screen. The ChamberSilo is a per-camera card that contains the metadata form, the live status, and the camera preview. SessionSetup is the metadata form itself with the dropdowns. LiveStatus is a pulsing red recording indicator with a session timer. CameraPreview is a Frigate snapshot that refreshes every second. StoragePanel shows disk usage, the EEG reserve, and the size calculator. SystemHealth shows badges for the daemon, Radiens, MQTT, and Frigate. And SessionHistory is the past sessions table with expandable rows.

The polling cadences at the bottom are tuned to what's reasonable: status every 1.5 seconds, health every 5 seconds, storage every 10 seconds, camera previews every second."

---

## Slide 33 — Manual Override

"There's also a manual override path for the cases where you want to record without using Radiens at all. You open the Frigate UI directly in the browser, click the Record button on whichever camera you want, and the daemon detects that within one second. If you've already filled in metadata in the desktop app, the manual session inherits that metadata automatically. When you click Stop, the daemon exports the file with the same naming convention as a normal Radiens-driven session. And the five-second minimum duration filter I mentioned earlier prevents accidental clicks from creating empty exports.

The point is that whether the recording is triggered by Radiens or manually, the filename convention and the organization on disk are identical."

---

## Slide 34 — Section 5

"Section five: storage management and the NAS transfer."

---

## Slide 35 — Where Data Lives

"Two directory trees on the NVR. The first is /srv/frigate/storage, which contains Frigate's raw recording segments, its temporary exports, and its event clips — that's Frigate's working area. The second is /opt/neurosurveillance, which contains the JSON session sidecars and the organized exports.

The organized exports are laid out as user, then mouse ID, then date. So a typical file path looks like exports/andrea/HETCF3R1/2026-04-06/2604061430_HETCF3R1_basal.mp4. The filename itself encodes the local time as YYMMDDHHMM, then the mouse ID, then the recording type. That naming convention is consistent across the whole system."

---

## Slide 36 — Capacity Math

"Some numbers because this is the question that always comes up. The actual measured bitrate per camera is 1.7 megabits per second. That works out to 18 gigabytes per camera per day, or 72 gigabytes per day across all four cameras. The NVMe is 1.9 terabytes, which gives roughly 26 days of headroom with all four cameras running. Two hundred gigabytes are reserved as a hard floor for EEG data — I'll come back to that in a second. And with the seven-day retention window, the typical working set on disk is about 504 gigabytes."

---

## Slide 37 — StorageMonitor

"This is the safety net. Every 30 seconds, the daemon checks how much free space is left on the NVR's disk. The check is cheap enough to run continuously without slowing anything else down. In parallel, a background process keeps a running tally of how much space recordings, exports, and clips are each consuming, so you can understand not just 'the disk is 80% full' but specifically which category is filling it up.

The hard rule is this: a new recording cannot start if free space is below 200 gigabytes. That 200 GB is reserved for the EEG and EMG data stream and is never touched by video, no matter what.

There's also a Sync Bitrates button in the GUI: when you click it, the daemon asks each Pi directly how much bandwidth its cameras are actually using right now, and the storage calculator uses the real measured value instead of an estimate.

The guarantee, in one sentence: a runaway video recording can never eat into the space the EEG data needs."

---

## Slide 38 — NAS Honest Status

"And I want to be transparent about this one. The NAS transfer is configured but it is not yet live. The target is the Synology NAS at 100.120.86.10. The blocker is that I haven't finished the Tailscale VPN setup to the NAS yet. The configuration stub is already in the daemon's config file, ready to be filled in once the tunnel is up. This is on the short-term roadmap, the next two to four weeks."

---

## Slide 39 — Section 6

"Section six, and this is the part where I compare what I built against what's already in the literature."

---

## Slide 40 — Literature Comparison Table

"This table compares the system to MouseVUER, which is the most relevant published system — it's a 2024 paper in Nature Scientific Reports, and it's a video monitoring rig for mice, very close to what I've built.

Their key advantage is right at the top: they use Intel RealSense D435 cameras, which give them depth information and three-dimensional posture estimation. We use plain RGB Pi cameras, so we don't have depth — though the FERAL video classifier I'll mention later is one path to recovering some of that information.

Beyond that, the comparison is mostly in our favor. They have no EEG integration and don't even mention it as future work; we have the Radiens API integration today and the XDAQ hardware sync planned. Their rig is locked to the Allentown NexGen rack — if your lab uses a different rack, you can't use their system. Ours doesn't care: any cage, any rack. Their cage modification cuts the per-cage mouse capacity from five down to three and halves the rack's storage capacity. Ours requires no cage modification at all. Building their system requires a 3D printer, a laser cutter, and a waterjet — actual fabrication infrastructure. Ours requires none of that. They need one Auvidea TX2 single-board computer per camera; we run two cameras per Pi 5 and one NUC for the entire installation. They describe no monitoring or alerting; we have sixteen Netdata alerts plus seven Kuma monitors plus Slack. They publish no long-term reliability data; we have a documented thirty-plus day stress test. They have no retention policy; we have automated seven-day rolling retention plus the 200 GB reserve. And their cost is not published in the paper; ours is roughly seventy-six dollars per chamber on the edge hardware, with the full bill of materials in the vault."

---

## Slide 41 — Sync & Openness

"There are two areas where I want to be honest about the comparison.

The first is OpenVEEG, a 2018 system, which has genuinely tighter sync than mine — sub-millisecond, achieved via the LabStreamingLayer protocol over NTP. Mine is one second software polling. So OpenVEEG wins on raw sync precision today. But their approach has costs: it requires a National Instruments DAQ board and a BlackMagic PCIe video card, the codebase is C++ and Python tightly coupled to those specific hardware APIs, and extending it to a different EEG system means rewriting C++. My architecture is hardware-agnostic — the daemon is an observer with no DAQ-specific dependencies — and the planned XDAQ upgrade bypasses software sync entirely by using hardware triggers, which is one step beyond what LSL does.

The second honest concession is that all four of these systems are open-source, so 'open-source' by itself isn't the differentiator. But MouseVUER requires Python 3.4 and Visual Studio 2010 on Windows. OpenVEEG requires NI DAQ bindings and the BlackMagic API in C++. My stack is React 19, Tauri version 2, Docker, and MQTT. The edge isn't openness — the edge is modern tooling and the production wrapper around it."

---

## Slide 42 — Six Novel Contributions

"Six things I think are genuinely novel about this work.

One: the acquisition-agnostic synchronization pattern. Because the daemon only observes the EEG software through one well-isolated module, you can swap radiens_poller.py for an OpenEphys poller, an Intan poller, a Blackrock poller, a Plexon poller — and the daemon, Frigate, MQTT, and the GUI all stay unchanged. That's a portable design pattern, not just a specific implementation.

Two: as far as I can find, this is the first open-source Frigate-to-NeuroNexus-Radiens auto-sync via the AllegoClient API.

Three: multi-chamber independent metadata. Four mice, four contexts, one application, in parallel. None of the comparison systems do this.

Four: MQTT pub/sub orchestration, which gives the loose coupling that makes the fail-safe recording possible.

Five: the production-operational wrapper. Sixteen Netdata alerts, seven Uptime Kuma monitors, Slack webhooks, a 38+ page vault with incident reports. None of the four published systems I compared against describe ANY operational monitoring whatsoever. This is the thing I'm most proud of and the thing that's most invisible in an academic paper.

And six: roughly twelve hundred dollars total versus five to twenty thousand for commercial systems, fully reproducible from documentation."

---

## Slide 43 — Key References

"Quick name-drops on the references. MouseVUER, Salem et al. 2024, Nature Scientific Reports — that's the one we just compared against. Worth noting that the same first author, Ghadi Salem, also published a 2020 paper on a fruit fly monitoring rig, so you'll see his name twice in the literature. OpenVEEG, Raghavan et al. 2018 in Epilepsy Research, the sub-millisecond LSL system. SIESTA, Beck et al. 2025 in the Journal of Biological Rhythms, which is a post-hoc EEG/EMG sleep scorer that takes EDF files as input. FERAL from Rockefeller, 2025 on bioRxiv, which is the video-to-behavior pipeline I'd like to integrate downstream — it sidesteps the DeepLabCut pose-labeling overhead. And Spyglass, eLife 2024, which is the reproducible neuroscience data management framework based on NWB and DataJoint, and that's the relevant one for our DANDI archive roadmap."

---

## Slide 44 — Section 7

"Section seven, briefly: the next big upgrade, hardware sync via XDAQ."

---

## Slide 45 — Polling to Triggering

"Today, sync is software polling against the Radiens API, with about a one-second latency and a plus-or-minus two-second export buffer. As I said, that's good for behavior, not for spike alignment.

The plan is to wire the Pis' GPIO pins directly to the XDAQ's digital I/O, so that EEG hardware events generate frame markers in the video stream itself. That gives per-frame, millisecond-level alignment between the EEG and the video, which is one architectural step beyond what OpenVEEG does with LSL — they're still doing software clock alignment, just very tight. Hardware triggers skip that entirely."

---

## Slide 46 — Why Easy

"And the upgrade is straightforward because the system was designed with it in mind from day one. The 200 GB EEG reserve is already enforced in storage_monitor.py. The session daemon is already Radiens-agnostic — it observes, it doesn't control. The Frigate export API is already buffered plus or minus two seconds, so no edge frames get lost. The JSON sidecar schema already has reserved fields for hardware sync metadata, so adding XDAQ trigger timestamps is a zero-breaking-change update. And the per-chamber independent state already scales to more headstages without rewrites.

In short, when the XDAQ wiring goes in, very little software has to change."

---

## Slide 47 — Validation TODOs

"What I still need to validate before I'd call this scientifically rigorous. First, an ffprobe-based post-export integrity check on every recording, which is a direct lesson from the 19 GB MP4 corruption incident in March. Second, I need to actually measure the latency between Radiens R_ON and the first Frigate frame timestamp, end to end. And third, I need more multi-day stability data than I currently have.

On the longer horizon: replacing JSON sidecars with a PostgreSQL session database for structured queries; NWB export and submission to the DANDI archive; and the dual-modality sleep scoring pipeline that combines EEG/EMG with FERAL video classification."

---

## Slide 48 — Section 8

"Last technical section: why this matters specifically for circadian work."

---

## Slide 49 — Why It Matters

"Circadian studies are multi-day continuous runs, by definition. A single crash can ruin a week of data. And a silent failure — one with no alert — is even worse, because by the time you discover it, you've lost more data than you would have if it had crashed loudly on day one and you'd noticed immediately.

Every design choice in this system optimizes for two things at the same time: uptime, and observability. Those are the two things that turn a research demo into a research instrument. A demo runs for an afternoon when somebody's watching it. An instrument runs for weeks while nobody's watching it, and tells you afterwards exactly what happened."

---

## Slide 50 — What Keeps It Running

"Concretely, here are the seven mechanisms keeping it running for days at a time. The 30-second hardware watchdog catches kernel hangs. The crash-canary logging catches silent slow-deaths from thermal or memory issues. The two-minute NVR-initiated Pi ping catches PoE power failures and network drops. The apt-mark hold on Docker prevents surprise auto-restarts from the Ubuntu updater. The systemd Restart=always policy catches single-process crashes. The fail-safe MQTT recording state means a daemon crash mid-session doesn't lose data. And the Intel RAPL 20-watt thermal cap from the allegoserver incident keeps the CPU 17 degrees below its alert threshold.

Each of those traces back to a real failure I had to debug."

---

## Slide 51 — Track Record

"The numbers that show this works in practice. Thirty-plus days of continuous uptime in the February MPEG-TS stress test. Zero active alerts as of last Monday, April 6th. Twenty-six days of storage headroom at the current four-camera load. The system has been stable since the PMIC EEPROM hardening on February 19th, and the thermal regime has been stable since the RAPL fix on April 3rd."

---

## Slide 52 — Solved Failures

"And rather than read this whole table, I want to point out three rows in particular because they're representative.

February 5th, H.265 kernel panics, fixed by reverting permanently to H.264. That's where the H.264-only rule came from.

February 19th, a Pi died due to a PoE PMIC power latch. The fix was hardening the EEPROM with custom power settings — that's the PSU_MAX_CURRENT line I mentioned earlier.

And March 6th, the 19 GB MP4 corruption I keep referring to. That was a race condition in the recording shutdown path, fixed by polling until the file finalized properly. That's also where the MPEG-TS rule and the future ffprobe validation TODO both come from.

Every row in this table made the system harder to break in a specific, traceable way."

---

## Slide 53 — Section 9

"Last section: the roadmap."

---

## Slide 54 — What's Next

"Three time horizons. In the next two to four weeks: ffprobe post-export validation, finishing the Tailscale NAS deployment, and confirming the apt-mark hold end to end. In the next one to three months: the FERAL video classifier integration, validating the actual video-EEG temporal alignment, the PostgreSQL session database, and multi-headstage support. And in the next three to six months: NWB export to the DANDI archive, the dual-modality sleep scoring pipeline, a system replication guide so other labs can build it, and a methods paper — I'm targeting either the Journal of Neuroscience Methods or HardwareX."

---

## Slide 55 — Documentation as Deliverable

"One thing I want to emphasize before I close: I think of the documentation as part of the system, not as something separate from it. The vault has more than thirty-eight pages of golden configurations, step-by-step procedures, incident reports, and references. The reason this matters is that anyone in the lab can reproduce or repair this system without me being in the room. Every hard rule I described earlier traces back to a specific incident report you can read. And the variable system — the curly-brace notation — means that all the production values, the IPs, the paths, the credentials, are versioned in exactly one place, so when something changes, it changes everywhere consistently."

---

## Slide 56 — Summary

"To wrap up. What we have today is a production-operational, four-chamber, EEG-synchronized video monitoring system. It is fail-safe by design, fully monitored, fully documented, and the total hardware cost is about eleven hundred and seventy-four dollars. It is engineered specifically for the multi-day circadian recordings that are the hardest case for these kinds of systems. The roadmap takes it to millisecond-level hardware sync and an automated sleep scoring pipeline. And because the whole stack is open and the documentation is exhaustive, it is reproducible as a methods contribution."

---

## Slide 57 — Thanks / Q&A

"Thank you for listening — I'm happy to take questions, and I have backup slides on the incident details, the full API table, the Frigate config, and the full alert list if anyone wants to go deeper on any specific piece."

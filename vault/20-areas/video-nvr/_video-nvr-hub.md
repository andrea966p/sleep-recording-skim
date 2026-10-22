---
type: hub
area: video-nvr
status: active
created: 2026-10-22
summary: "Video side of the lab: Raspberry Pi cameras, go2rtc, Frigate, Mosquitto, the session daemon and its UI, storage, watchdogs, and the planned video-EEG hardware sync. Cameras disconnected since 2026-08-04; work resumes soon."
---

# Video NVR (NeuroSurveillance) hub

## What this is
Raspberry Pi 5 camera nodes stream H.264 through go2rtc to Frigate and Mosquitto on the NVR (`e10ubuntu`); a Flask session daemon and Tauri UI start, export and check recordings.
Sleep-study video is exported per session and stored under `/opt/neurosurveillance/exports/`, with watchdogs and a nightly reconciler guarding it.
An ACTIVE area, not retired: the cameras are unplugged until the next video run, and a XDAQ-to-Pi hardware sync is planned.

## Current state
- 2026-10-22: Cameras physically disconnected since 2026-08-04 (room stripped), so no video is being recorded. [[nvr-system-overview]]
- 2026-10-22: Checked read-only: containers `frigate`, `mosquitto`, `uptime-kuma` up (about 2 weeks); services `neurosurveillance-session` and `nvr-mqtt-slack` active; docker packages held with `apt-mark`. [[docker-compose]] [[session-service]]
- 2026-10-22: `sessions.auto_start: false` in `/opt/neurosurveillance/config.yaml` (daemon auto video start/stop disabled since 2026-07-03). [[2026-07-27-video-eeg-sync-recording-architecture]]
- 2026-10-07: Session daemon last restarted; the live code contains the lease and 30 s drain stop-path fix written 2026-07-28, so it is now loaded (auto start still off). [[2026-07-27-video-eeg-sync-recording-architecture]]
- 2026-09-20: Netdata and Uptime Kuma alerts moved to ntfy 2026-09-14 and deploy scripts 2026-09-20; recording-stall and reconciler alerts still go to Slack via `nvr-mqtt-slack`. [[watchdog-slack-bridge]]
- 2026-07-28: Hardware sync design final: pulse from the camera frame-capture callback, per-camera fit; first measured camera drift +204 ppm; bench validation of DO 03 still owed. [[2026-07-27-video-eeg-sync-recording-architecture]] [[overview]]

## Start here
- [[nvr-system-overview]] (what everything is)
- [[emergency-runbook]] (something is wrong)
- [[session-recording-workflow]] (running a recording)
- [[architecture]] (session daemon internals)
- [[overview]] (hardware sync)

## Rules that must not be broken
- H.264 only on the Raspberry Pi 5; H.265 causes kernel panics. [[h265-encoding-failure]]
- Never propose `record.enabled: false` in Frigate `config.yml`; it was investigated and is off the table. [[2026-05-20-docker-upgrade-and-startup-guard-regression]] [[config-yml]]
- Pin Docker images by SHA digest and keep `apt-mark hold` on the docker packages (aptdaemon upgrades fired recordings on all cameras). [[docker-compose]] [[2026-05-20-docker-upgrade-and-startup-guard-regression]]
- No ffmpeg pipes in go2rtc; `KillMode=control-group` is mandatory; `golden-config` notes change only after hardware testing and Andrea's approval. [[golden-go2rtc-config]] [[golden-systemd-service]]
- Frigate recording is gated by a retained MQTT topic; check runtime state, not the YAML. [[2026-07-27-video-eeg-sync-recording-architecture]]
- Check `/opt/neurosurveillance/exports/` before declaring an export failed. [[exports-move-out-of-frigate-dir]]

## Open items
- Bench-validate the DO 03 gate and build the pulse train (about 40 USD of parts). [[hardware-sync-bench-test-do03]] [[wiring-guide]]
- Decide when to flip `sessions.auto_start` to true; not before a deliberate daemon restart check. [[2026-07-27-video-eeg-sync-recording-architecture]]
- Frame-integrity and drift checks still to repeat on pi_cam_0, 1 and 3; NTP/chrony on the Pis never addressed. [[2026-07-27-video-eeg-sync-recording-architecture]]
- Camera scale-up to 8 cameras, approved pending validation. [[2026-07-16-camera-node-scale-up]]
- Settings sync gap (localStorage vs config.yaml), deferred. [[settings-sync-gap]]
- Stale and conflicting claims are listed in `_meta/contradictions/video-nvr.md`.

## Everything here
![[area.base]]

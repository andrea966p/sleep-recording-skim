---
tags: [overview, entry-point]
audience: anyone
updated: 2026-05-24
---

# NeuroSurveillance — system overview

> [!abstract] Read this first
> One-page entry point for anyone opening this vault — advisors, lab members, paper reviewers, future you. For the full Q&A, durability guarantees, and glossary, jump to [[01-infrastructure/system-overview|the deeper overview]].

## What this system is

NeuroSurveillance is a four-chamber video-monitoring system for mouse sleep experiments. Two Raspberry Pi 5 cameras stream H.264 video over the lab network to an Ubuntu Mini-PC running Frigate NVR. A Python session daemon on the Mini-PC watches the NeuroNexus Radiens electrophysiology recorder over gRPC; whenever Radiens starts recording, the daemon tells Frigate to start a synchronized video session and writes every step into a crash-safe SQLite journal. When Radiens stops, the daemon exports an MP4 clip covering exactly that window and files it under `/opt/neurosurveillance/exports/<researcher>/<mouse>/<date>/`.

Researchers interact through a Tauri desktop UI: enter mouse ID, recording type, and your name in the chamber tile, then run Radiens as usual. The system handles the rest.

> [!quote] Paper-ready summary
> NeuroSurveillance synchronizes four-camera 1024×768@15fps H.264 video recording with a NeuroNexus Radiens electrophysiology session via MQTT and gRPC, persisting session lifecycle events to a fsync'd SQLite write-ahead-log database and reconciling video segments against session metadata nightly.

## What the stabilization sprint changed (2026-05-22 → 2026-05-24)

- **2026-05-22** — Mosquitto MQTT now requires authentication; Docker images SHA-pinned; Frigate Python logs persist to disk.
- **2026-05-23** — Every session state transition (START / EXPORT / ABORT / STALL) is written to a crash-safe SQLite journal; Radiens connection failures now back off exponentially instead of spamming the log.
- **2026-05-24** — Frigate restarts no longer create phantom sessions (LWT detection + 1.5 s state-callback defer); a nightly reconciler at 00:01 KST cross-checks intended sessions against the video that actually landed on disk.

## Where to read more

| Topic | Document |
|---|---|
| Full Q&A overview + glossary | [[01-infrastructure/system-overview]] |
| Day-one walkthrough for a new lab member | [[02-procedures/new-researcher-onboarding]] |
| Session daemon architecture | [[01-infrastructure/session-daemon/architecture]] |
| Session journal (WAL) details | [[01-infrastructure/session-daemon/session-journal]] |
| Nightly reconciler details | [[01-infrastructure/session-daemon/reconciler]] |
| Recording workflow (researcher view) | [[02-procedures/session-recording-workflow]] |
| Index of every doc | [[_INDEX]] |

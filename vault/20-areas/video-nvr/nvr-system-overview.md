---
type: reference
area: video-nvr
status: active
tags: [overview, infrastructure, q-and-a]
audience: anyone
updated: 2026-05-24
---

# System overview — Q&A and glossary

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Plain-language reference for the whole NeuroSurveillance system, organized as Q&A so you can scan it.
>
> **Why it exists.** Most other vault pages are technical references. This page exists so you (or an advisor, or a lab member you're handing off to) can understand the system without reading code.
>
> **How to read this page.** Skim the section headings — they're questions. Read the answer if the question matches what you need. The **paper-ready callouts** are lift-into-methods-section phrasing; the **glossary** at the bottom defines every acronym used on this page.
>
> Short version: [[SYSTEM-OVERVIEW|the one-page elevator pitch]].

## What does the system actually do?

> [!quote] Paper-ready
> A four-camera H.264 video monitoring system synchronizes per-mouse video clips with NeuroNexus Radiens electrophysiology sessions; a Python orchestrator listens to Radiens over gRPC, controls the Frigate NVR over MQTT, and writes every session lifecycle event to a fsync'd SQLite write-ahead log, ensuring that no recording metadata is lost across process or power failure.

Four chambers, each with a single Raspberry Pi camera (1024×768 at 15 frames per second, H.264). The cameras stream RTSP to **go2rtc** running on two Raspberry Pi 5 boards. **Frigate NVR**, in a Docker container on an Ubuntu Mini-PC, pulls those streams and stores rolling 10-second segments on the NVR's NVMe disk. A **session daemon** (Python, running as a systemd service on the same Mini-PC) polls Radiens once per second; when Radiens transitions from "off" to "on" (`R_OFF → R_ON`), the daemon picks up the pending metadata you entered in the desktop UI, tells Frigate to flag the recording window for that camera, and writes a `START` event to the session journal. When Radiens stops, the daemon asks Frigate to export an MP4 covering exactly that window, writes `EXPORT_BEGIN`, waits for Frigate, then writes `EXPORT_COMPLETE` with the final filename. The MP4 lands in `/opt/neurosurveillance/exports/<your-name>/<mouse-id>/<YYYY-MM-DD>/`.

There is also a "manual" recording path for chambers where Radiens isn't running: you press the **Record** button in Frigate's web UI directly, and the daemon detects the state change over MQTT and creates a `ManualSession` instead.

## What kinds of experiments does it support?

| Experiment type | What the system handles | What you still do manually |
|---|---|---|
| Single-mouse Radiens session, one chamber | Detects start/stop, records video, exports MP4, files it under your name | Set metadata before pressing Record on Radiens |
| Multi-chamber Radiens session (1 chamber per researcher) | Same as above, but per chamber; chambers are independent | Set metadata for each chamber you're using |
| Manual / non-electrophysiology session | Records and exports based on Frigate UI Record button | Set metadata first; otherwise the recording is named `manual_<camera>_<timestamp>` |
| Long-running observation (hours to days) | Continuous segment writing; storage cap prevents disk-full crashes | Make sure ≥ 200 GB is reserved for EEG before starting |

Continuous monitoring outside of any session (e.g. nighttime baseline) is **also** recorded by Frigate because `record.enabled: true` is set in Frigate's config — but these segments aren't tied to any session metadata. The nightly reconciler accounts for this; see "What is the reconciler" below.

## How do researcher actions map to system behavior?

| You do this | …and the system does this |
|---|---|
| Open the Tauri desktop UI (Session Controller) | The UI polls `GET /api/status` every 1.5 s — you see green/red badges per chamber |
| Type a mouse ID + recording type + your name in the chamber tile, click **Set Metadata** | `POST /api/session/metadata` stores the values in the daemon's pending-metadata slot for that chamber. Nothing is recorded yet. |
| Start a Radiens recording as you normally would | Within ~1 s the daemon's poller sees `R_ON`, picks up the pending metadata, tells Frigate to mark the recording window for the chamber's camera, writes `START` to the journal |
| Pulsing red dot appears in the chamber tile | The UI is showing the live recording state coming back over MQTT |
| Stop the Radiens recording | Daemon sees `R_OFF`, asks Frigate to export an MP4 from start-ts to end-ts, writes `EXPORT_BEGIN`, waits for Frigate (usually 5–60 s), then writes `EXPORT_COMPLETE` and moves the MP4 to `/opt/neurosurveillance/exports/<you>/<mouse>/<date>/`|
| Open the storage panel in the footer | The UI is showing `GET /api/storage` results — you can see disk usage, EEG reserve, and the bitrate calculator |

## What's guaranteed and what isn't?

> [!quote] Paper-ready
> Five failure modes are explicitly handled: power loss before export (journal entry survives via fsync), daemon crash mid-session (session JSON sidecar + journal record survive), Frigate restart (LWT subscription re-arms the 10 s grace window, retained state messages are deferred 1.5 s and cancelled), Pi unreachable (chamber tile flags offline; existing recording continues if Frigate has the stream), Radiens disconnect (exponential backoff, 1 s → 60 s, prevents log flooding).

**Durability matrix** — what survives what:

| Failure | What survives | What might be lost |
|---|---|---|
| **Power loss** during a recording | Every journal event written before the crash (fsync'd to SQLite WAL). Frigate's already-written 10 s video segments. | Anything in flight: the last partial segment, any pending export. |
| **Daemon crash** mid-session | The session JSON sidecar (atomically written) + every journal event (fsync'd). The nightly reconciler will detect the missing `EXPORT_COMPLETE` and flag the session as STUCK. | The export will not auto-resume — re-run manually if needed. |
| **Frigate restart** (docker restart) | All sessions in flight — the daemon's LWT subscription detects the restart and runs a 10 s grace window that ignores Frigate's retained "ON" state messages so they don't fire phantom recordings (this was a bug fixed 2026-05-24). | A tiny window (~1.5 s) of recording state visibility — the daemon defers acting on state changes during this period. |
| **Pi unreachable** (network, PoE crash) | Sessions on other chambers (independent). The Frigate-side recording for cameras on the affected Pi may have gaps. The recording watchdog raises a STALL alert if no new video segments arrive within 60 s. | New segments from the offline Pi until it returns. |
| **Disk fills** below the 200 GB EEG reserve | Existing in-flight recordings continue; new ones are refused by the storage cap. | New recordings until disk is freed. |
| **Mosquitto MQTT down** | Daemon's MQTT client auto-reconnects with keepalive=60s. Existing in-memory state is preserved across the reconnect. | MQTT-driven state changes (Frigate UI Record clicks) until the broker is back. |
| **Radiens down** | Backoff prevents log flooding; daemon reconnects when Radiens returns. Existing manual recordings (not Radiens-driven) are unaffected. | Auto-detected Radiens sessions during the downtime — but Radiens isn't running, so nothing was recorded anyway. |

## What did the stabilization sprint (2026-05-22 → 2026-05-24) change?

In plain language, the system went from "works for the happy path" to "survives the unhappy ones."

- **2026-05-22 — Mosquitto authentication.** Before: any device on the LAN could publish or read MQTT topics. After: only authenticated clients with the `nvr` user can talk to the broker. Practical effect: a researcher running `mosquitto_sub` on their laptop must now use `-u nvr -P …`; an attacker on the LAN can no longer trivially impersonate Frigate.
- **2026-05-22 — Docker images SHA-pinned.** Before: an `apt` upgrade or a `docker compose pull` could silently swap Frigate, Mosquitto, or Netdata for a new version that breaks something. After: the version is locked to a specific SHA-256 image digest. Updates are deliberate.
- **2026-05-22 — Persistent Frigate Python logs.** Before: Frigate's process logs lived in a tmpfs mount inside the container and vanished on restart. After: they're on the host at `/srv/frigate/logs/frigate/current` and survive container restarts — debugging post-mortems are now possible.
- **2026-05-23 — Session WAL journal.** Before: session lifecycle existed only in the daemon's RAM. A crash mid-session would lose all metadata about that session. After: every state transition (`START / EXPORT_BEGIN / EXPORT_COMPLETE / ABORT / STALL`) is appended to `/opt/neurosurveillance/session_wal.db` with fsync. A crash now loses, at worst, the very last event being written.
- **2026-05-23 — Radiens exponential backoff.** Before: when Radiens was off, the daemon hammered Radiens once per second forever, writing ~2 error lines per second into `radiens.log`. The log grew to 3.2 GB before anyone noticed. After: failures back off 1 s → 60 s. Idle days produce a handful of log lines.
- **2026-05-24 — Frigate restart grace via LWT.** Before: restarting Frigate (docker restart, container crash, upgrade) caused 4 phantom `ManualSession` records (one per camera) because Frigate's retained `recordings/state=ON` topics replayed on reconnect and the daemon thought a researcher had clicked Record on every camera. After: the daemon subscribes to Frigate's `frigate/available` LWT topic, detects the restart, re-arms a 10 s grace window, and ignores the replayed state messages. Plus a 1.5 s defer on every state-change callback so even a slightly out-of-order MQTT delivery is safe.
- **2026-05-24 — Nightly reconciler.** Before: there was no automated check that the daemon's intended sessions matched the videos that landed on disk. After: a background thread runs every night at 00:01 KST, joins the WAL journal against Frigate's `recordings` SQLite, and flags four kinds of problems: **ORPHAN** (Frigate recorded but no session was tracked), **PARTIAL** (session existed but coverage was poor), **STUCK** (export started 24h+ ago and never finished), **DEGRADED** (session completed but had at least one mid-recording stall).

## What are the system's known limitations?

- **`lab_members` is a hardcoded list with one entry — `["andrea"]`.** Settings UI accepts more, but the production `config.yaml` is the source of truth. Add new researchers manually.
- **NAS off-machine backup is stubbed.** A Tailscale-connected NAS is planned but not wired. All exports live on the NVR's NVMe drive; lose the NVR and you lose the videos (Frigate retention is 7 days; session exports are kept indefinitely until the disk fills).
- **Frigate records 24/7.** `record.enabled: true` in Frigate's config means every camera writes 10 s segments continuously, whether or not a session is active. This is by design (safety net — captures sleep events even if the daemon is down) but it means the nightly reconciler's `ORPHAN` finding is structurally noisy. The reconciler suppresses ORPHAN runs shorter than 6 h to filter routine background recording; Slack alerts will skip ORPHAN entirely. Only `PARTIAL / STUCK / DEGRADED` are alertable.
- **Single Radiens instance assumed.** The system polls one `RadiensClient` and assumes one electrophysiology session at a time. Multi-Radiens, multi-rig setups would need multiple daemons.
- **Pi 5 PoE HAT instability.** Three Pi crashes attributed to the Waveshare PoE HAT's PMIC latch-up have occurred (Feb 13, 19, 24). Mitigation: physical reset; replacement hardware is on order.
- **MQTT auth password lives in `00-config/production-values.md`.** That file must not be committed to a public repo — `production-values.md` is already in the repo's `.gitignore`. Confirm before any public-facing publication.

## Where to read more

| If you want to know… | Read this |
|---|---|
| Day-one walkthrough for a new researcher | [[new-researcher-onboarding]] |
| Step-by-step session recording workflow | [[session-recording-workflow]] |
| Full daemon architecture (10 components + frontend) | [[architecture]] |
| Session journal (WAL) design + schema | [[session-journal]] |
| Nightly reconciler (findings categories + tuning) | [[reconciler]] |
| Recording stall detection (watchdog) | [[recording-health-watchdog]] |
| Storage cap + EEG reserve | [[storage-management-implementation]] |
| Frigate Docker compose (Mosquitto auth, SHA pins) | [[docker-compose]] |
| Frigate config.yml (recording, cameras, MQTT) | [[config-yml]] |
| Raspberry Pi camera streaming setup | [[golden-go2rtc-config]] |
| Hardware-sync (planned XDAQ GPIO trigger) | [[overview]] |
| Netdata alerts | [[nvr-alerts-config]] |
| Original sprint plan + status table | [[2026-05-20]] |
| Daily journals during the sprint | [[2026-05-22]], [[2026-05-23]], [[2026-05-24]] |

## Glossary

- **chamber** — A physical mouse-housing enclosure with one camera. The system has 4 (numbered 0–3). Each chamber is independent; a session in one doesn't affect the others.
- **silo** — The collapsible UI tile representing one chamber. Stacks vertically in the desktop app.
- **headstage** — The NeuroNexus electrode interface that plugs into the mouse and feeds Radiens.
- **Radiens / AllegoClient** — NeuroNexus's electrophysiology acquisition software. The daemon polls its `AllegoClient` gRPC interface to know when recording is on or off.
- **`R_ON` / `R_OFF`** — The two states the daemon watches Radiens for. Transitions trigger session start/end.
- **session daemon** — The Python systemd service that orchestrates everything. Source: `~/Monitoring_project/neurosurveillance/backend/`, deployed at `/opt/neurosurveillance/session-daemon/` (symlink).
- **sidecar JSON** — A `<session_id>_session.json` file written next to each session, containing the metadata (mouse_id, recording_type, user_name, start_time, end_time, export_status, etc.). Atomic write — never half-written.
- **WAL (write-ahead log)** — A SQLite journaling mode where writes go to a separate `.db-wal` file before being merged. `synchronous=FULL` means `fsync()` is called on every commit, so a power loss can lose at most the very last in-flight statement.
- **fsync** — A Unix system call that forces the OS to flush buffered file changes to physical disk. Without fsync, "the write succeeded" only means "the OS has it in RAM" — a power loss can lose it.
- **MQTT** — A publish/subscribe messaging protocol. Frigate publishes recording state changes; the daemon subscribes. Broker is Mosquitto running in Docker on the NVR.
- **retained MQTT message** — A message the broker remembers and re-delivers to any new subscriber. Frigate uses retained messages for `recordings/state` and `frigate/available`, which is why those topics replay on subscriber reconnect.
- **LWT (Last Will and Testament)** — An MQTT feature where a client tells the broker, "if I disconnect uncleanly, publish this message for me." Frigate's LWT is `frigate/available: offline`. When Frigate's MQTT session dies, the broker publishes `offline`; when Frigate reconnects, it publishes `online`.
- **`record.enabled`** — A Frigate config setting. `true` means Frigate always records every camera; `false` means it only records on demand. We use `true` for a safety net — investigated `false` and it breaks Frigate's segment writing.
- **ORPHAN / PARTIAL / STUCK / DEGRADED** — The four reconciler finding categories. ORPHAN: Frigate had segments but no daemon session covered them. PARTIAL: session existed but coverage was poor. STUCK: an export started but never finished. DEGRADED: session completed but had at least one mid-recording stall.
- **STATE_DEFER_SECONDS** — A 1.5 s delay applied to every external recording-state callback. Exists because Frigate republishes retained state messages BEFORE its availability topic on reconnect; the defer + cancel pattern makes the daemon robust to that ordering.
- **stability-week-1** — Git tag planned for the end of the 2026-05 stabilization sprint, after Phase 4 (Monday) lands.

## See also

- [[SYSTEM-OVERVIEW|One-page elevator pitch]] — vault-root entry point
- [[_INDEX|Index of all docs]] — by folder
- [[2026-05-20|2026-05-20 sprint plan]] — full status table of what shipped during the sprint

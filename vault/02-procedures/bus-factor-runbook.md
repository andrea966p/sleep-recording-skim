---
tags: [procedure, runbook, bus-factor, escalation, continuity]
date: 2026-05-28
created: 2026-05-28
status: active
sourced-from: 07-decisions/2026-05-01-llm-council-review#Stage 3 — Before TTL cutover (council's emergent insight)
audience: anyone in the lab who is NOT Andrea
---

# Bus-Factor Runbook — "Andrea is unreachable"

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A short guide for keeping the video-monitoring rig running when Andrea is unreachable (sick, sabbatical, on a plane — or unavailable for any reason). It is deliberately written for someone who is *not* a software engineer and has never SSH'd into the system before.
>
> **Why it exists.** Right now Andrea is the only person who knows the system end-to-end. That is the single biggest risk on the [[2026-05-01-llm-council-review#Blind Spots the Council Caught|council's blind-spot list]] (Reviewer 1). This runbook is the human side of that fix.
>
> **How to read this page.** [[#First 30 seconds — is the system OK?]] tells you whether anything is broken right now. [[#I need to find my data]] and [[#I want to start or stop a recording]] cover the two things you most likely came here to do. [[#Something is broken]] points to the operational runbooks. [[#What NOT to do]] is short and load-bearing — read it before changing anything.

> [!quote] Paper-ready
> "The NeuroSurveillance system is operated by one researcher; a written bus-factor runbook covering daily checks, recording lifecycle, data location, recovery procedures, and explicit do-not-touch rules is maintained in the project vault so the recording instrument can be kept running by other lab members in the operator's absence."

> [!warning] Read this once before you act
> The system can record a 24/7 video stream for multiple animals at once. Any restart of Frigate, the daemon, or the broker **interrupts whatever recording is currently in flight**. If a recording is active (`curl -s http://127.0.0.1:8585/api/status | jq .manual_recordings` returns something other than `{}`), do not restart anything until the researcher running it confirms it is OK. This rule is non-negotiable.

---

## First 30 seconds — is the system OK?

You're at the NVR machine (`e10ubuntu`, IP `192.168.0.50`, logged in as `skimlab`). Run these three commands in order:

```bash
# 1. Are the cameras streaming?
curl -s http://127.0.0.1:8585/api/health | python3 -m json.tool

# 2. Is anything actively recording right now?
curl -s http://127.0.0.1:8585/api/status | python3 -m json.tool

# 3. Has Slack received any alerts in the last day? (open #nvr-alerts in Slack)
```

What "healthy" looks like:
- `/api/health` returns `{"status": "healthy", ...}` and `mqtt_connected: true`, `radiens_connected: true`.
- `/api/status` shows `"sessions": {}` and `"manual_recordings": {}` when nobody is recording (this is the normal idle state), or named entries when someone is.
- Slack `#nvr-alerts` is silent or contains only resolved alerts from earlier days.

If all three pass: the system is fine; you don't need to do anything. Move on to whatever you came here for.

If any of those fail, jump to [[#Something is broken]].

> [!tip] The status page also works in a browser
> Open `http://192.168.0.50:5000` from any laptop on the lab network — that's the Frigate UI; live camera previews + a green/red status per camera. Easier than reading JSON.

---

## I want to start or stop a recording

You have two ways to record:

### Method 1 — Automatic, driven by the EEG rig (Radiens)

When the EEG acquisition rig (Radiens / AllegoServer) starts recording on its end, the session daemon detects that within ~1 second and starts video recording for all 4 cameras automatically. When EEG recording stops, video recording stops automatically too. Nothing to click on the NVR side.

This is the normal experiment workflow. If you started the EEG rig and don't see video recording starting (`/api/status` still shows `"sessions": {}` after 10s), check `/api/health` for `radiens_connected: true`. If it's `false`, the daemon lost the connection to Radiens — Andrea has to restart the daemon, or you can do it yourself if you're confident (see [[#Restart the session daemon]]).

### Method 2 — Manual, via the Frigate UI

For ad-hoc recording without Radiens:

1. Open `http://192.168.0.50:5000` in a browser (Frigate UI).
2. Click into the camera you want to record (`pi_cam_0`, `pi_cam_1`, `pi_cam_2`, or `pi_cam_3`).
3. Use the "Record" toggle to start. To stop, toggle it off.

> [!warning] Don't start a manual recording while an automatic Radiens session is running on that camera — the two paths will fight over Frigate's `recordings/state` topic and produce broken metadata.

After you stop, the session daemon takes ~30 seconds to **export** the clip (mux from Frigate's circular buffer into a real MP4 in `/opt/neurosurveillance/exports/`). Wait for that to finish — `/api/status` will show the export in flight and then clear it. The exported file is what you should reference in your paper, not Frigate's internal segments.

### How to verify the recording landed cleanly

```bash
# What sessions have completed in the last day?
curl -s 'http://127.0.0.1:8585/api/journal?event_type=EXPORT_COMPLETE&limit=10' | python3 -m json.tool

# Are there any sessions stuck without a terminal event?
curl -s 'http://127.0.0.1:8585/api/reconciler/last' | python3 -m json.tool
```

A healthy session has both a `START` and an `EXPORT_COMPLETE` event in the journal. The reconciler's `partial / stuck / degraded` counts should all be 0 for the windows where you recorded. (`orphan_count` will be ~4 in any 24h window — that is **expected noise** from Frigate's 24/7 background recording, not a problem.)

---

## I need to find my data

Three places hold session data; they cover different time windows.

| Where | What's in it | Time window |
|---|---|---|
| `/srv/frigate/storage/recordings/<date>/<hour>/<camera>/` | Raw Frigate segments (10s `.mp4` chunks), continuous | Last ~7 days (`{RETENTION_DAYS}`) |
| `/opt/neurosurveillance/exports/` | Stitched, named session MP4s — **this is what you want** | Indefinite (until manually deleted) |
| `/opt/neurosurveillance/sessions/` | Session metadata JSON sidecars (per session: mouse ID, start/end, status) | Indefinite |

To find a specific session by date or mouse:

```bash
# All sessions for a given day
ls -la /opt/neurosurveillance/sessions/2026-05-*

# Show metadata for one session (replace <session-id> with the prefix from the filename)
cat /opt/neurosurveillance/sessions/<session-id>.json | python3 -m json.tool

# Where the actual video is
ls -la /opt/neurosurveillance/exports/<session-id>/
```

The session daemon's WAL journal (`/opt/neurosurveillance/session_wal.db`, append-only SQLite) is the **authoritative event log** — every recording's `START`, `EXPORT_BEGIN`, `EXPORT_COMPLETE`, `ABORT`, `STALL` is in there, with `fsync` per write. Querying it directly is safe (read-only):

```bash
sqlite3 -readonly /opt/neurosurveillance/session_wal.db \
  "SELECT datetime(ts,'unixepoch','localtime'), event_type, camera, mouse_id
   FROM events WHERE ts > strftime('%s','now','-2 days') ORDER BY ts"
```

> [!warning] Do not write to `session_wal.db` by hand
> The append-only guarantee is the foundation of the chain-of-custody fix shipped 2026-05-23. Editing or deleting rows breaks the reconciler's ability to detect missing data.

---

## Something is broken

The first-10-minutes guide for specific symptoms lives in [[emergency-runbook|emergency-runbook]]. Match your symptom to one of these and follow that section:

| If you see | Symptom | Where |
|---|---|---|
| Disk almost full | A | [[emergency-runbook#Symptom A — Disk full / nearly full]] |
| `curl http://127.0.0.1:8585/...` connection refused | B | [[emergency-runbook#Symptom B — Session daemon down]] |
| Frigate UI doesn't load / `docker ps` shows it unhealthy | C | [[emergency-runbook#Symptom C — Frigate down or unhealthy]] |
| `mqtt_connected: false` in `/api/health` | D | [[emergency-runbook#Symptom D — MQTT broker (Mosquitto) down]] |
| A camera shows offline in the Frigate UI | E | [[emergency-runbook#Symptom E — Pi unreachable / camera offline]] |
| All cameras started recording without you doing anything | F | [[emergency-runbook#Symptom F — Unexpected recording fired (all cameras started without command)]] |
| Slack STALL alert in `#nvr-alerts` | G | [[emergency-runbook#Symptom G — Watchdog STALL alert fired]] |
| Disk died, machine wiped, config gone | H | [[emergency-runbook#Symptom H — Disk died / data lost / config wiped → restore from NAS]] |

### Restart the session daemon

Only after confirming `/api/status` is `{}` for `manual_recordings` and `sessions`:

```bash
sudo systemctl restart neurosurveillance-session
journalctl -u neurosurveillance-session -n 30 --no-pager   # wait for "started", check no errors
curl -s http://127.0.0.1:8585/api/health | python3 -m json.tool   # back to healthy?
```

Since 2026-05-23 the WAL preserves any in-flight session through the restart, so the nightly reconciler will flag anything that was actually lost.

### Restart Frigate

```bash
cd /srv/frigate && docker compose restart frigate
docker ps --filter name=frigate                # wait for "(healthy)"
```

Since 2026-05-24 the daemon's LWT defer guard prevents phantom manual sessions on restart (Phase 3.1b).

### Restore from the daily NAS snapshot

If something catastrophic happened (disk failure, accidental wipe), the last 3 days of project state are on the Synology NAS over Tailscale. Full procedure in [[nas-backup|NAS Backup procedure]] and [[emergency-runbook#Symptom H — Disk died / data lost / config wiped → restore from NAS]].

**Videos are not in the NAS snapshot.** Recorded MP4s live on the NVR's NVMe only. The snapshot covers config + code + vault + session WAL, which is what you need to bring the system back up — but historical videos older than the latest cache cycle are gone if the NVMe died.

---

## Where everything lives

Quick reference card. Full detail in [[production-values|production-values]] (sensitive — do not share publicly).

### Machines

| Name | IP | Role | User |
|---|---|---|---|
| **NVR** (`e10ubuntu`) | `192.168.0.50` | Frigate + session daemon + Mosquitto + Netdata | `skimlab` |
| **Pi 1** | `192.168.0.11` | go2rtc for `pi_cam_0` + `pi_cam_1` | `skimlab` |
| **Pi 2** | `192.168.0.12` | go2rtc for `pi_cam_2` + `pi_cam_3` | `skimlab` |
| **Synology NAS** | `bilab-syn.tail8808c0.ts.net` (Tailscale only; the IP moves, the name does not) | Nightly backups, port `53` | `Andrea` (not `skimlab`) |

### Key URLs

| Service | URL |
|---|---|
| Frigate UI (camera previews, manual record) | http://192.168.0.50:5000 |
| Session daemon API | http://127.0.0.1:8585 (local only) |
| Netdata dashboard | http://192.168.0.50:19999 |
| Uptime Kuma | http://192.168.0.50:3001 |
| Public status page | http://192.168.0.50:3001/status/neurosurveillance |

### Key files & dirs

| Path | Purpose |
|---|---|
| `/opt/neurosurveillance/config.yaml` | Session daemon config |
| `/opt/neurosurveillance/session_wal.db` | Append-only WAL (authoritative event log) |
| `/opt/neurosurveillance/sessions/` | Session metadata JSONs |
| `/opt/neurosurveillance/exports/` | Final session MP4s (this is your data) |
| `/srv/frigate/docker-compose.yml` | Frigate + Mosquitto + Netdata stack |
| `/srv/frigate/config/config.yml` | Frigate camera config |
| `/srv/frigate/storage/recordings/` | Frigate's raw 10s segments (7-day retention) |
| `/srv/frigate/mosquitto/passwd` | MQTT auth (mode `0600`, owned `1883:1883`) |
| `/home/skimlab/Monitoring_project/neurosurveillance/` | Daemon source code (live; symlinked into `/opt/neurosurveillance/session-daemon`) |
| `/home/skimlab/Monitoring_project/Monitoring_project_obsidian_vault/` | This vault |

### Systemd services on the NVR

| Service | Purpose | Restart command |
|---|---|---|
| `neurosurveillance-session` | The session daemon | `sudo systemctl restart neurosurveillance-session` |
| `docker` (manages `frigate`, `mosquitto`, `netdata` containers) | The container runtime | Don't restart this; restart the container instead |
| `nvr-mqtt-slack` | MQTT → Slack alert bridge | `sudo systemctl restart nvr-mqtt-slack` |
| `nas-backup.timer` | Daily 00:00 NAS snapshot | `sudo systemctl status nas-backup.timer` |
| `netdata` | Monitoring agent | `sudo systemctl restart netdata` |

### Code repository

`git@github.com:andrea966p/neurosurveillance.git` (private). The NVR's working tree is at `/home/skimlab/Monitoring_project/neurosurveillance/`. Commits typically push directly to `main`.

---

## What NOT to do

Short, load-bearing. **Do not** do any of the following without explicit confirmation from a senior lab member:

1. **Do not restart Frigate, the daemon, or Mosquitto while a recording is in flight.** Check `curl -s http://127.0.0.1:8585/api/status | jq .manual_recordings` first — must be `{}`. A restart mid-recording will produce broken or partial exports.
2. **Do not set `record.enabled: false` in Frigate's `config.yml`.** Andrea investigated this — it breaks Frigate's pipeline. The flag stays `true`; recording is gated at the daemon/MQTT layer, not the config layer.
3. **Do not click "Install" on the GNOME Update Manager popup** if it shows `docker-ce` or `containerd` in the list. Those packages are held with `apt-mark hold` (since 2026-05-20) because docker auto-upgrade restarts Frigate, which silently starts recording on all 4 cameras (see [[2026-05-20|the 2026-05-20 incident]]). If the popup shows them anyway, **cancel** and tell a senior lab member.
4. **Do not `rm -rf` inside `/srv/frigate/storage/recordings/`** without stopping Frigate first — Frigate's SQLite DB will become inconsistent with disk.
5. **Do not edit or delete rows in `/opt/neurosurveillance/session_wal.db`.** It is append-only by design (the chain-of-custody fix). Read-only queries (`sqlite3 -readonly ...`) are fine.
6. **Do not commit `production-values.md`, `/etc/nvr-mqtt-slack.env`, `/srv/frigate/mosquitto/passwd`, or anything under `/srv/frigate/config/secrets/` to a public repo.** They contain real credentials.
7. **Do not change Mosquitto from authenticated back to `allow_anonymous true` permanently.** Anyone on the lab LAN could then publish recording-control messages to the broker and toggle recordings. Temporary fallback during a recovery is acceptable (see [[emergency-runbook#Symptom D — MQTT broker (Mosquitto) down]]); restore auth as soon as the password is recovered from production-values.
8. **Do not power-cycle a Pi while it is recording for an active experiment.** Wait for the session to end, or use the Frigate UI to stop recording first, then power-cycle. Power-cycling the Pi cuts the RTSP stream — the watchdog will detect a STALL within ~90s and alert Slack.

---

## Escalation contacts

In order:

1. **Andrea** — primary operator and original author. Try email + Slack DM + phone.
2. **Lab PI** — for institutional decisions (rerouting cohort schedules, postponing experiments, contacting IT).
3. **KAIST IT helpdesk** — for network / Tailscale / Synology NAS issues beyond the lab's reach.

Lab Slack channels:
- `#nvr-alerts` — automated alerts from Netdata + Uptime Kuma + watchdog + reconciler. Quiet = healthy.
- (lab general channel) — for asking other lab members operationally.

---

## Glossary (insider terms decoded)

These show up in vault docs, logs, and Slack alerts. None of them are obvious if you didn't build the system.

| Term | Meaning |
|---|---|
| **Session** | One animal recording event (e.g. mouse #47 from 14:00 → 22:00). NOT an HTTP session, NOT a tmux session. Has a UUID, a mouse ID, a start/end, and one MP4 per camera. |
| **Chamber** | The physical box one animal is in. Currently 4 chambers map 1-to-1 to 4 cameras (`pi_cam_0..3`). Planned to scale up. |
| **Chamber silo** | Frontend UI term — the collapsible card per camera that bundles its preview + session controls + status. |
| **R_ON / R_OFF** | Radiens (the EEG/EMG acquisition software) starts (`R_ON`) and stops (`R_OFF`) a recording. The session daemon polls Radiens 1× per second; when it sees `R_ON`, it tells Frigate to start recording video for the configured cameras. |
| **EEG reserve** | A fixed 200 GB chunk of the NVR's disk that the storage manager refuses to write video into. It guarantees the XDAQ EEG rig always has room for its own data on the same disk. |
| **Manual session** | A recording started from the Frigate UI by a human (vs an automatic Radiens-triggered session). |
| **WAL** (in `session_wal.db`) | "Write-Ahead Log" — SQLite mode where every change is fsync'd to a journal file before being applied. Crash-safe. The session daemon also uses "WAL" loosely to mean the append-only event log itself. |
| **Reconciler** | The nightly 00:01 KST job that cross-checks the WAL events against Frigate's actual recorded segments and flags discrepancies (orphan / partial / stuck / degraded). Slack-alerts when finding anything other than orphan. |
| **Watchdog** | A daemon thread that polls Frigate's segment timestamps every few seconds; if a camera that *should* be recording stops producing new segments for ~90s, it publishes a STALL event to MQTT (and from there to Slack). |
| **LWT** | "Last Will and Testament" — Frigate's MQTT mechanism for announcing its own crash. The daemon subscribes to `frigate/available` to know when Frigate is *actually* online vs just republishing its retained state on reconnect. |
| **Stage 1 / Stage 2 / Stage 3** | Phases of the [[../07-decisions/2026-05-stabilization-sprint-week-1-plan|stabilization sprint]]. Stage 1 = "stop the bleeding". Stage 2 = "chain of custody". Stage 3 = "before TTL pulse cutover" (hardware-sync upgrade, not yet deployed). |
| **TTL pulse** | The planned hardware-sync upgrade. EEG rig will emit a TTL voltage edge on every recording start/stop, the Pis' GPIO pins will pick it up, eliminating the 1-second polling jitter. Not deployed yet. |
| **Council** | The 2026-05-01 LLM Council review that produced the sprint plan. Full output: [[2026-05-01-llm-council-review]]. |

---

## Related

- [[emergency-runbook]] — first 10 minutes per-symptom playbook (this runbook references its sections)
- [[2026-05-stabilization-sprint-week-1-plan]] — sprint that built the chain-of-custody safety net this runbook depends on
- [[2026-05-01-llm-council-review#Blind Spots the Council Caught]] — why this doc exists (Reviewer 1's bus-factor point)
- [[nas-backup]] — daily project snapshot to NAS (restore source for catastrophic recovery)
- [[production-values]] — IPs, ports, paths, credentials (sensitive)
- [[nvr-system-overview]] — deeper architectural overview with the durability matrix
- [[new-researcher-onboarding]] — day-0 access + first-recording walkthrough (the version of this doc you give to a new lab member who *isn't* in an emergency)

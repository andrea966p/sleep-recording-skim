---
type: procedure
area: video-nvr
status: active
tags: [procedure, session-daemon, experiment]
created: 2026-02-20
updated: 2026-04-13
---

# Session Recording Workflow

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The most-read procedure in the vault — what a researcher does, step by step, to record a synchronized video + EEG session.
>
> **Why it exists.** Recording is the system's core use case. This page is the canonical instructions for any lab member running an experiment.
>
> **How to read this page.** Skim Quick Reference for the 6-step overview. Then go to Steps 1-5 for the detail. If something goes wrong, the "How to ask the journal what happened" troubleshooting section (added 2026-05-24) tells you the two API calls that diagnose 90 % of issues.

> [!quote] Paper-ready
> The session recording workflow is fully automatic from the researcher's perspective: per-chamber metadata is set in the desktop UI; the session daemon detects the Radiens R_OFF→R_ON transition within ~1 s and starts Frigate recording on chambers with metadata; the R_ON→R_OFF transition triggers MP4 export and filing under `/opt/neurosurveillance/exports/<user>/<mouse>/<date>/`.

## Purpose

Synchronize Frigate video recording with NeuroNexus Radiens EEG/EMG recording for mouse sleep experiments. The session daemon automates the video side -- the researcher only needs to set metadata and operate Radiens as normal.

## Prerequisites Checklist

- [ ] Session daemon running: `sudo systemctl status neurosurveillance-session`
- [ ] Frigate NVR running: open `http://192.168.0.50:5000` in browser
- [ ] All camera streams visible in Frigate (pi_cam_0 through pi_cam_3)
- [ ] Radiens software open and connected to headstage
- [ ] Mouse prepared and connected to EEG/EMG headstage in the correct chamber
- [ ] NeuroSurveillance Session Controller app open (optional but recommended)

## Your Values (from [[production-values|Production Values]])

| Variable | Value |
|----------|-------|
| `{NVR_IP}` | `192.168.0.50` |
| `{SESSION_DAEMON_PORT}` | `8585` |
| Chamber 0 camera | `pi_cam_0` |
| Chamber 1 camera | `pi_cam_1` |

---

## Quick Reference

| Step | Who | Action |
|------|-----|--------|
| 1 | Researcher | Set session metadata in the UI (mouse ID, type, user) per chamber |
| 2 | Researcher | Start EEG recording in Radiens GUI |
| 3 | **Daemon** | *Automatically* starts Frigate video recording on chambers with metadata set |
| 4 | Researcher | Run experiment (daemon monitors silently) |
| 5 | Researcher | Stop EEG recording in Radiens GUI |
| 6 | **Daemon** | *Automatically* stops video, exports MP4s, organizes files |

---

## Steps

### 1. Set Session Metadata

Before starting the EEG recording, set the session metadata so the daemon knows how to name and organize the video files. **Each chamber has independent metadata** -- set metadata for each chamber you are using.

**Using the UI (recommended):**

Open the **NeuroSurveillance Session Controller** app. Each camera has its own **ChamberSilo** card with a metadata form:

| Field | Description | Example |
|-------|-------------|---------|
| **Mouse ID** | 6-8 character alphanumeric identifier | `HETCF3R1` |
| **Recording Type** | `basal`, `recovery`, or `sd` (sleep deprivation) | `basal` |
| **Your Name** | Select from lab member list | `andrea` |

Click **"Set Metadata"** to submit. A toast notification confirms success. Repeat for each chamber in use.

**Using the command line (alternative):**

```bash
# Set metadata for chamber 0
curl -X POST "http://127.0.0.1:8585/api/session/metadata?chamber_id=0" \
  -H "Content-Type: application/json" \
  -d '{
    "mouse_id": "HETCF3R1",
    "recording_type": "basal",
    "user_name": "andrea",
    "chamber": 0
  }'

# Set metadata for chamber 1 (if using both chambers)
curl -X POST "http://127.0.0.1:8585/api/session/metadata?chamber_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "mouse_id": "HETCF7L2",
    "recording_type": "recovery",
    "user_name": "andrea",
    "chamber": 1
  }'
```

> [!warning] Metadata is Required
> The daemon **only records chambers that have metadata set**. If you start Radiens without setting metadata for any chamber, no video will be recorded. Always set metadata before starting EEG recording.

> [!tip] Partial Updates
> You can update individual fields without resetting others. For example, send just `{"mouse_id": "HETCF3R1"}` to update only the mouse ID.

### 2. Start EEG Recording in Radiens

Start recording in the Radiens GUI as you normally would. The daemon polls Radiens every second and detects the `R_OFF -> R_ON` transition automatically.

**What happens behind the scenes:**
1. Daemon detects Radiens recording state changed to `R_ON`
2. Daemon checks which chambers have pending metadata set
3. For each chamber **with metadata**, daemon starts a session and publishes `ON` to `frigate/{camera}/recordings/set`
4. Frigate starts recording only the cameras tied to chambers with metadata
5. Chambers without metadata are skipped (not recorded)
6. Daemon logs the session start timestamp per active chamber

> [!warning] Wait for Confirmation
> After starting EEG recording, verify the daemon detected it:
> - **In the UI:** Each ChamberSilo shows a pulsing red "Recording" indicator and a running timer
> - **Via CLI:**
> ```bash
> curl http://127.0.0.1:8585/api/status | python3 -m json.tool
> ```
> You should see active sessions in the `"sessions"` object.

### 3. Run the Experiment

Proceed with your experiment normally. The daemon monitors silently in the background. You do not need to interact with it.

**During the session:**
- Video is being recorded continuously by Frigate on all cameras
- EEG/EMG data is being recorded by Radiens
- The daemon is tracking timestamps for each chamber's export
- The UI shows a live running timer per chamber

### 4. Stop EEG Recording in Radiens

Stop recording in the Radiens GUI when the experiment is complete. The daemon detects the `R_ON -> R_OFF` transition automatically.

**What happens behind the scenes:**
1. Daemon detects Radiens recording state changed to `R_OFF`
2. Daemon ends **all** active sessions
3. Daemon publishes `OFF` to all camera MQTT topics
4. For each chamber, a background thread:
   - Calls Frigate export API to create a named MP4 (+/-2s buffer)
   - Moves the MP4 to the organized export directory
   - Writes a session JSON sidecar
   - Clears pending metadata for that chamber

### 5. Verify the Session

After stopping, verify the sessions completed successfully:

**In the UI:** Check the **Session History** panel at the bottom. Completed sessions appear with green "completed" badges.

**Via CLI:**

```bash
# Check session history (most recent first)
curl http://127.0.0.1:8585/api/session/history | python3 -m json.tool
```

**Check the output files:**

| File | Location | Description |
|------|----------|-------------|
| Exported MP4 | `{EXPORT_DIR}/{user}/{mouse}/{YYYY-MM-DD}/` | Organized video clip |
| Session JSON | `{SESSION_DATA_DIR}/` | Session metadata sidecar |

**Export path example:**

```
/opt/neurosurveillance/exports/
└── andrea/
    └── HETCF3R1/
        └── 2026-02-20/
            ├── 2602201430_HETCF3R1_basal.mp4
            └── 2602201430_HETCF3R1_basal_session.json
```

---

## Multi-Chamber Recording

Only chambers with metadata set will record when Radiens starts. Each chamber maintains **independent metadata**, so you can record different mice in different chambers at the same time -- or record only a subset of chambers.

**Setup workflow (2 mice):**

1. Set metadata for **chamber 0** (Mouse A, basal)
2. Set metadata for **chamber 1** (Mouse B, recovery)
3. Start EEG recording in Radiens
4. Both cameras start recording automatically (chambers 2-3 are skipped)
5. Stop EEG recording -- both exports run independently

**Setup workflow (1 mouse):**

1. Set metadata for **chamber 0** only (Mouse A, basal)
2. Start EEG recording in Radiens
3. Only `pi_cam_0` records (all other chambers skipped)

**In the UI:** Each ChamberSilo card has its own form, status indicator, and timer. Set metadata independently for each. Only chambers with a green "Metadata Set" indicator will record.

**Via CLI:**

```bash
# Chamber 0
curl -X POST "http://127.0.0.1:8585/api/session/metadata?chamber_id=0" \
  -H "Content-Type: application/json" \
  -d '{"mouse_id": "HETCF3R1", "recording_type": "basal", "user_name": "andrea"}'

# Chamber 1
curl -X POST "http://127.0.0.1:8585/api/session/metadata?chamber_id=1" \
  -H "Content-Type: application/json" \
  -d '{"mouse_id": "HETCF7L2", "recording_type": "recovery", "user_name": "andrea"}'
```

> [!info] Single Radiens Instance
> The current design uses one Radiens instance controlling one headstage. Radiens provides a single global R_ON/R_OFF signal -- the daemon uses metadata presence to determine which chambers to include. If two headstages need independent control, additional Radiens instances and daemon configuration would be required.

---

## Manual Recording (Without Radiens)

If you need to record video **without** an active Radiens EEG session (e.g. setup verification, behavioral observation), you can use Frigate's built-in Record button. The daemon auto-detects this and exports the video.

### Metadata Inheritance

Manual recordings **inherit pending metadata** from the UI. If you set metadata (mouse ID, recording type, user name) before clicking Record in Frigate, the manual recording uses those values for naming and organization.

If no metadata is set, the recording uses defaults (`manual` mouse ID, camera name in filename).

### Steps

1. **(Optional)** Set metadata in the NeuroSurveillance UI for the relevant chamber
2. Open Frigate UI: `http://192.168.0.50:5000`
3. Navigate to the camera you want to record (pi_cam_0 or pi_cam_1)
4. Click the **Record** button on the camera
5. When done, click **Stop** on the camera
6. The daemon auto-detects the stop and exports the video

**Output files (with metadata set):**
- Video: `{EXPORT_DIR}/andrea/HETCF3R1/2026-02-20/2602201430_HETCF3R1_basal.mp4`
- Sidecar: `{SESSION_DATA_DIR}/2602201430_HETCF3R1_basal_session.json`

**Output files (without metadata):**
- Video: `{EXPORT_DIR}/unknown/manual/2026-02-20/2602201430_manual_pi_cam_0.mp4`
- Sidecar: `{SESSION_DATA_DIR}/2602201430_manual_pi_cam_0_session.json`

### Check manual recording status

```bash
# See active manual recordings
curl http://127.0.0.1:8585/api/session/manual | python3 -m json.tool

# See all history (both Radiens and manual)
curl http://127.0.0.1:8585/api/session/history | python3 -m json.tool

# Filter to manual only
curl "http://127.0.0.1:8585/api/session/history?source=manual" | python3 -m json.tool
```

### Important notes

- **Radiens takes priority:** If a Radiens EEG session is active on a camera, clicking Record in Frigate UI is ignored by the daemon (the Radiens session controls that camera).
- **Min duration:** Recordings shorter than 5 seconds are ignored (accidental clicks).
- **Both cameras:** You can record cam_0 and cam_1 independently at the same time.
- **JSON sidecar:** Same format as Radiens sessions but with `"source": "manual"`.

---

## Troubleshooting

### Daemon not detecting Radiens recording

| Check | Command |
|-------|---------|
| Is daemon running? | `sudo systemctl status neurosurveillance-session` |
| Daemon logs | `sudo journalctl -u neurosurveillance-session -f` |
| Is Radiens running? | Check Radiens GUI on desktop |
| Daemon health | `curl http://127.0.0.1:8585/api/health` |

### Video not recording in Frigate

| Check | Command |
|-------|---------|
| MQTT broker running? | `docker ps \| grep mosquitto` |
| Frigate running? | `docker ps \| grep frigate` |
| Camera streams active? | Check Frigate UI at `http://192.168.0.50:5000` |
| MQTT messages flowing? | `docker exec mosquitto mosquitto_sub -u nvr -P "$NVR_MQTT_PASSWORD" -t 'frigate/#' -v` |

> [!history] Historical note — pre-2026-05-22
> Before 2026-05-22 the same `mosquitto_sub` command worked without `-u nvr -P …`. Authentication is now required on the broker; any unauthenticated subscriber gets `Connection error: Bad user name or password`. Pre-change examples: [[session-recording-workflow-unauth-mosquitto-2026-05-22|archived workflow]].

### How to ask the journal what happened

Since 2026-05-23 every session lifecycle event (`START`, `EXPORT_BEGIN`, `EXPORT_COMPLETE`, `ABORT`, `STALL`) is written to a crash-safe SQLite WAL at `/opt/neurosurveillance/session_wal.db`. When a researcher reports "the recording didn't work," check the journal first — it tells you whether the daemon ever knew about the session and where it got stuck.

| Question | One-line answer |
|---|---|
| "Did the session even start?" | `curl 'http://127.0.0.1:8585/api/journal?event_type=START&limit=20' \| python3 -m json.tool` |
| "Did the export ever complete?" | `curl 'http://127.0.0.1:8585/api/journal?event_type=EXPORT_COMPLETE&limit=20' \| python3 -m json.tool` |
| "Is anything stuck right now?" | `curl 'http://127.0.0.1:8585/api/reconciler/last' \| python3 -m json.tool` (returns the most recent nightly run's findings) |
| "Force a reconciler check now" | `curl -X POST 'http://127.0.0.1:8585/api/reconciler/run?window_hours=24' \| python3 -m json.tool` |

If `/api/journal` shows a `START` but no `EXPORT_COMPLETE`, the export hung or the daemon crashed mid-export. The nightly reconciler will flag the session as `STUCK` after 24 h. To unstick it manually, follow the "Export failed" recipe below. Full reference: [[session-journal|session-journal]] and [[reconciler|reconciler]].

### Export failed

If the Frigate export fails (e.g., Frigate was briefly unreachable), the session log will show `"export_status": "failed"`. You can manually export from Frigate:

1. Open Frigate UI: `http://192.168.0.50:5000`
2. Navigate to the camera's recording timeline
3. Select the time range matching the session
4. Click Export

### Daemon crashed mid-session

If the daemon crashes while recording is active:

1. **Video is safe** -- Frigate continues recording (MQTT state persists as ON)
2. **On restart**, the daemon publishes OFF and resets
3. **Manual export needed** -- check the daemon logs for the start timestamp, then export from Frigate UI for that time range

---

## NAS Transfer (Future)

When NAS connectivity is configured via Tailscale, the daemon will automatically transfer exports to the Synology NAS. Until then, exported files remain in `{EXPORT_DIR}` on the ASUS PC.

---

## Related

- [[architecture|Session Daemon Architecture]] -- technical details and failure modes
- [[frontend-reference|Frontend Reference]] -- desktop UI component details
- [[config-yml|Frigate Config]] -- recording settings
- [[production-values|Production Values]] -- all IPs and ports

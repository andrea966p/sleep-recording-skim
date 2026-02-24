---
tags: [procedure, session-daemon, experiment]
created: 2026-02-20
status: draft
---

# Session Recording Workflow

## Purpose

Synchronize Frigate video recording with NeuroNexus Radiens EEG/EMG recording for mouse sleep experiments. The session daemon automates the video side -- the researcher only needs to set metadata and operate Radiens as normal.

## Prerequisites Checklist

- [ ] Session daemon running: `sudo systemctl status neurosurveillance-session`
- [ ] Frigate NVR running: open `http://192.168.0.50:5000` in browser
- [ ] Both camera streams visible in Frigate (pi_cam_0, pi_cam_1)
- [ ] Radiens software open and connected to headstage
- [ ] Mouse prepared and connected to EEG/EMG headstage in the correct chamber

## Your Values (from [[00-config/production-values|Production Values]])

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
| 1 | Researcher | Set session metadata in the UI (mouse ID, type, chamber, name) |
| 2 | Researcher | Start EEG recording in Radiens GUI |
| 3 | **Daemon** | *Automatically* starts Frigate video recording |
| 4 | Researcher | Run experiment (daemon monitors silently) |
| 5 | Researcher | Stop EEG recording in Radiens GUI |
| 6 | **Daemon** | *Automatically* stops video, exports MP4, logs session |

---

## Steps

### 1. Set Session Metadata

Before starting the EEG recording, set the session metadata so the daemon knows how to name and organize the video files.

**Using the UI (when available):**

Open the session controller app and fill in:

| Field | Description | Example |
|-------|-------------|---------|
| **Mouse ID** | 6-8 character alphanumeric identifier | `HETCF3R1` |
| **Recording Type** | `basal` or `recovery` | `basal` |
| **Chamber** | `0` or `1` (maps to pi_cam_0 / pi_cam_1) | `0` |
| **Your Name** | Select from lab member list | `andrea` |

**Using the command line (temporary, until UI is built):**

```bash
curl -X POST http://127.0.0.1:8585/api/session/metadata \
  -H "Content-Type: application/json" \
  -d '{
    "mouse_id": "HETCF3R1",
    "recording_type": "basal",
    "user_name": "andrea",
    "chamber": 0
  }'
```

> [!tip] Metadata is Optional
> If you forget to set metadata, the daemon still records video. Files will be named with `unknown` placeholders (e.g., `2602201430_unknown_unknown.mp4`). You can rename them manually afterward.

### 2. Start EEG Recording in Radiens

Start recording in the Radiens GUI as you normally would. The daemon polls Radiens every second and detects the `R_OFF -> R_ON` transition automatically.

**What happens behind the scenes:**
1. Daemon detects Radiens recording state changed to `R_ON`
2. Daemon publishes `ON` to MQTT topic `frigate/pi_cam_X/recordings/set`
3. Frigate starts recording the camera stream
4. Daemon logs the session start timestamp

> [!warning] Wait for Confirmation
> After starting EEG recording, verify the daemon detected it by checking the session status:
> ```bash
> curl http://127.0.0.1:8585/api/session/current
> ```
> You should see `"state": "active"` with your metadata. In the future UI, this will show as a green "Recording" indicator.

### 3. Run the Experiment

Proceed with your experiment normally. The daemon monitors silently in the background. You do not need to interact with it.

**During the session:**
- Video is being recorded continuously by Frigate
- EEG/EMG data is being recorded by Radiens
- The daemon is tracking timestamps for the export

### 4. Stop EEG Recording in Radiens

Stop recording in the Radiens GUI when the experiment is complete. The daemon detects the `R_ON -> R_OFF` transition automatically.

**What happens behind the scenes:**
1. Daemon detects Radiens recording state changed to `R_OFF`
2. Daemon publishes `OFF` to MQTT topic `frigate/pi_cam_X/recordings/set`
3. Daemon records the session end timestamp
4. Daemon calls Frigate export API to create a named MP4
5. MP4 is renamed to `YYMMDDHHMM_mouseID_type.mp4`
6. Session sidecar JSON is written with full metadata
7. (Future) Files are transferred to NAS

### 5. Verify the Session

After stopping, verify the session completed successfully:

```bash
# Check session history (most recent first)
curl http://127.0.0.1:8585/api/session/history | python3 -m json.tool
```

**Check the output files:**

| File | Location | Description |
|------|----------|-------------|
| `YYMMDDHHMM_mouseID_type.mp4` | `/opt/neurosurveillance/exports/` | Exported video clip |
| `YYMMDDHHMM_mouseID_type_session.json` | `/opt/neurosurveillance/sessions/` | Session metadata sidecar |

**Example filenames for a session started at 2:30 PM on Feb 20, 2026:**
- `2602201430_HETCF3R1_basal.mp4`
- `2602201430_HETCF3R1_basal_session.json`

---

## Multiple Chambers

To run experiments in both chambers simultaneously:

1. Set metadata for **chamber 0** via the API
2. Start EEG recording for chamber 0 in Radiens
3. The daemon tracks each chamber independently

> [!warning] Current Limitation
> The current design assumes one Radiens instance controlling one headstage. If two headstages are recorded simultaneously via separate Radiens instances, the daemon needs to be configured to poll both. This is a future enhancement.

---

## Troubleshooting

### Daemon not detecting Radiens recording

| Check | Command |
|-------|---------|
| Is daemon running? | `sudo systemctl status neurosurveillance-session` |
| Daemon logs | `journalctl -u neurosurveillance-session -f` |
| Is Radiens running? | Check Radiens GUI on desktop |
| Daemon health | `curl http://127.0.0.1:8585/api/health` |

### Video not recording in Frigate

| Check | Command |
|-------|---------|
| MQTT broker running? | `docker ps \| grep mosquitto` |
| Frigate running? | `docker ps \| grep frigate` |
| Camera streams active? | Check Frigate UI at `http://192.168.0.50:5000` |
| MQTT messages flowing? | `docker exec mosquitto mosquitto_sub -t 'frigate/#' -v` |

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

## Manual Recording (Without Radiens)

If you need to record video **without** an active Radiens EEG session (e.g. setup verification, behavioral observation), you can use Frigate's built-in Record button. The daemon will auto-detect this and export the video.

### Steps

1. Open Frigate UI: `http://192.168.0.50:5000`
2. Navigate to the camera you want to record (pi_cam_0 or pi_cam_1)
3. Click the **Record** button on the camera
4. When done, click **Stop** on the camera
5. The daemon auto-detects the stop and exports the video

**Output files:**
- Video: `YYMMDDHHMM_manual_pi_cam_0.mp4` in `/opt/neurosurveillance/exports/`
- Sidecar: `YYMMDDHHMM_manual_pi_cam_0_session.json` in `/opt/neurosurveillance/sessions/`

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
- **No metadata:** Manual recordings don't use mouse ID metadata. The filename uses `manual` + camera name instead.

---

## NAS Transfer (Future)

When NAS connectivity is configured via Tailscale, the daemon will automatically transfer exports to:

```
/volume1/neurosurveillance/{username}/{YYYY-MM-DD}/YYMMDDHHMM_mouseID_type.mp4
/volume1/neurosurveillance/{username}/{YYYY-MM-DD}/YYMMDDHHMM_mouseID_type_session.json
```

Until then, exported files remain in `/opt/neurosurveillance/exports/` on the ASUS PC.

---

## Related

- [[01-infrastructure/session-daemon/architecture|Session Daemon Architecture]] -- technical details and failure modes
- [[01-infrastructure/frigate/config-yml|Frigate Config]] -- recording settings
- [[00-config/production-values|Production Values]] -- all IPs and ports

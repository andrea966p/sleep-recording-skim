---
tags: [procedure, onboarding]
created: 2026-05-21
updated: 2026-05-24
status: production
audience: new-lab-member
---

# New Researcher Onboarding

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Day-one walkthrough for a new lab member who has never used the NeuroSurveillance system before.
>
> **Why it exists.** So you can run your first recording without anyone hovering over you, and so you know what to do if something looks wrong.
>
> **How to read this page.** Read it top to bottom once before your first recording. Then keep it open during the recording — every UI element you'll see is explained in "What's behind every button."

> [!quote] Paper-ready
> A standardized onboarding procedure introduces new lab members to the NeuroSurveillance recording workflow, the desktop session controller, common failure modes, and escalation paths within a single session, enabling researchers to operate the system independently from day one.

> [!info] Before you start
> Read [[../SYSTEM-OVERVIEW|the one-page system overview]] first (90 seconds). It explains what the system is and what it does. This page covers *how you actually use it*.

## Before your first day

Checklist — ask Andrea to do these for you before you arrive:

- [ ] **Slack access** to `#nvr-alerts` so you see when the system pages someone.
- [ ] **LAN or Tailscale access** — confirm your laptop reaches `192.168.0.50` (NVR), `192.168.0.11` (Pi 1), `192.168.0.12` (Pi 2). Open `http://192.168.0.50:3001/status/neurosurveillance` in your browser — should show 7 green services.
- [ ] **Added to `lab_members`** in `/opt/neurosurveillance/config.yaml`. Currently the list is `["andrea"]`. Andrea has to edit the config file directly (it's intentional — not auto-add — so we know who's recording). Restart of the daemon required after the edit; do it together so the timing is yours, not in the middle of someone else's recording.
- [ ] **Frigate web UI account** at `http://192.168.0.50:5000`. Andrea creates the user. The first-login password is sent via Slack DM.
- [ ] **NeuroSurveillance Session Controller** desktop app installed on your laptop. If Andrea hasn't already built you a `.deb`, ask — it's a 30-second Tauri build (`npm run tauri build` in the frontend folder).

## What the system is, in 90 seconds

Four mouse chambers, four cameras (`pi_cam_0` through `pi_cam_3`), one Radiens electrophysiology rig. The cameras stream video over Wi-Fi/Ethernet to an Ubuntu mini-PC (the "NVR"). When you start an EEG recording in Radiens, a Python service on the NVR notices within ~1 second and tells the video recorder (Frigate) to mark the video window for the chamber you're recording. When you stop Radiens, the service exports a single MP4 covering exactly that window and files it under your name + the mouse ID + today's date.

You interact with one app: the **NeuroSurveillance Session Controller**. It looks like a wall of chamber tiles. You enter the mouse ID, the recording type, and your name into the tile for the chamber you're using, click **Set Metadata**, and you're ready. Start Radiens as normal. Stop Radiens when done. Wait 30 seconds for the export. The MP4 appears in `/opt/neurosurveillance/exports/<your-name>/<mouse-id>/<today's-date>/`.

For the architecture details: [[../01-infrastructure/system-overview|System overview with Q&A and glossary]].

## Day-one walkthrough — your first recording

This assumes Radiens is already running and you've connected a mouse to a headstage. The video side is what we're walking through.

1. **Open the Session Controller app** on your laptop. You'll see 4 chamber tiles ("ChamberSilo" in the code), one per chamber.
2. **Find the tile for your chamber.** If the chamber is online, the tile has a gray dot and the camera preview shows the chamber. If it shows a red "Camera offline" badge, the Pi or the camera is down — page Andrea.
3. **Click on the tile to expand it.** Three sections appear: metadata form, live status, camera preview.
4. **Fill in the metadata form**:
   - **Mouse ID** — 6-8 character alphanumeric (e.g. `HETCF3R1`).
   - **Recording Type** — pick from the dropdown: `basal`, `recovery`, `sd` (sleep deprivation).
   - **Your Name** — your name from the dropdown. If your name isn't there, your `lab_members` registration didn't complete — page Andrea before continuing.
5. **Click "Set Metadata."** A green "Metadata Set" indicator appears. A toast notification confirms success.
6. **Start the Radiens recording** as you normally would.
7. **Watch the tile's dot.** Within ~1 second it turns into a pulsing red dot and a session timer starts ticking (`HH:MM:SS`). This is your confirmation that video is recording for your chamber.
8. **Run the experiment.** The Session Controller polls every 1.5 s — keep an eye on the dot but don't worry about it.
9. **Stop the Radiens recording.** The pulsing dot returns to gray. The session timer freezes.
10. **Wait ~30 seconds.** Frigate is exporting the MP4. The header's storage badge will tick up by however many MB your recording took. The Session History panel at the bottom of the app shows your session with a "completed" badge once the export is done.
11. **Verify the file landed.** SSH to the NVR (`ssh skimlab@192.168.0.50`) and run:
    ```bash
    ls /opt/neurosurveillance/exports/<your-name>/<mouse-id>/$(date +%Y-%m-%d)/
    ```
    You should see one MP4 and one `_session.json` sidecar.

That's it. You don't need to touch Frigate's web UI for normal recordings.

## What's behind every button you click

| What you see | What's happening underneath |
|---|---|
| **Green "Metadata Set" indicator** | The daemon has your mouse ID + recording type + your name in memory for that chamber. When Radiens starts, this metadata is consumed and the recording is labeled. The indicator clears after the recording ends. |
| **Pulsing red dot in a chamber tile** | Frigate is actively recording that camera. The dot comes from MQTT — Frigate publishes `recordings/state=ON` and the UI reflects it. |
| **Yellow "Manual recording" badge** | Someone pressed the **Record** button in Frigate's web UI instead of using Radiens. Counts as a `ManualSession`. The MP4 will still file under your name if you set metadata first; otherwise it falls back to `manual/manual/`. |
| **Red "Camera offline" badge in a tile** | The Pi hosting that camera is unreachable. Check the network, check Pi power. Recordings on other chambers continue unaffected. |
| **Yellow / red header storage badge** | Yellow = disk is over 75% full. Red = over 90% full **or** below the 200 GB EEG reserve (recordings refused below the reserve). Stop new recordings and ask Andrea about freeing space. |
| **"Daemon Offline" badge in the header** | The session daemon (the Python service on the NVR) isn't reachable on `http://127.0.0.1:8585`. Either the daemon crashed and didn't restart, or your laptop is on the wrong network. Run `sudo systemctl restart neurosurveillance-session` on the NVR; page Andrea if it returns. |
| **"Recording Blocked" badge** | The storage cap is engaged. New recordings will be refused until the EEG reserve is restored. In-flight recordings continue. |
| **Session History panel showing "failed" sessions** | The export hit a problem. Use the troubleshooting recipes below or ask the journal what happened: `curl http://127.0.0.1:8585/api/journal?session_id=<id> | python3 -m json.tool`. |
| **Footer: SystemHealth panel green/red dots** | Daemon, Radiens connection, MQTT connection, Frigate reachability — at a glance. All four should be green during a healthy day. |
| **Footer: StoragePanel calculator** | "If I record N cameras for X hours, how big?" — converts go2rtc's actual measured bitrate (refresh button) into an estimated MP4 size and tells you whether the recording fits within the EEG-reserve budget. |

## When something looks wrong — escalation tree

**No jargon.** If you can't follow a step, page Andrea.

| Symptom | First thing to try | If that didn't work |
|---|---|---|
| Recording didn't start (no red dot after Radiens start) | Check that "Metadata Set" indicator is green for the chamber. If not, set metadata and retry. | Page Andrea. The daemon may not be seeing Radiens. |
| MP4 didn't appear in the export folder after stop | Wait 60 seconds. Long recordings take longer to export. | Run `curl http://127.0.0.1:8585/api/journal?event_type=EXPORT_COMPLETE&limit=5 \| python3 -m json.tool` — if the most recent `EXPORT_COMPLETE` is older than your session's stop time, the export didn't finish. Page Andrea. |
| Storage badge is red and won't clear | Stop any new recordings; in-flight ones continue. Talk to Andrea about which old exports can be moved off the NVR. | Do not delete anything from `/srv/frigate/storage/recordings/` manually — Frigate's database will get out of sync. |
| "Daemon Offline" badge won't go away | `ssh skimlab@192.168.0.50` then `sudo systemctl restart neurosurveillance-session`. Wait 15 seconds, refresh the app. | Page Andrea. If it returns offline, something's deeper. |
| Camera Offline badge on a tile | Check the Pi: `ssh skimlab@192.168.0.11` (or `.12`) — if SSH works, run `sudo systemctl restart go2rtc`. | Physical check — is the PoE cable seated? Has the Pi crashed? Power cycle as a last resort. |
| Frigate web UI shows wrong number of cameras | Don't touch — page Andrea. Editing Frigate's config is a one-way trip without backups. |

> [!important] Before doing anything: write down the time
> Note the wall-clock time when you noticed the problem. The session journal can be queried by time, so a 2-second timestamp turns a 30-minute investigation into a 30-second one.

## Where to find stuff

| Thing | Location |
|---|---|
| Your exported MP4s | `/opt/neurosurveillance/exports/<your-name>/<mouse-id>/<YYYY-MM-DD>/` |
| Session metadata sidecars (JSON) | `/opt/neurosurveillance/sessions/` (one per session) |
| Daemon log (live) | `ssh skimlab@192.168.0.50 'sudo journalctl -u neurosurveillance-session -f'` |
| Frigate log (persistent since 2026-05-22) | `ssh skimlab@192.168.0.50 'sudo tail -f /srv/frigate/logs/frigate/current'` |
| System health page | `http://192.168.0.50:3001/status/neurosurveillance` |
| Netdata real-time dashboard (NVR) | `http://192.168.0.50:19999` |
| Frigate web UI | `http://192.168.0.50:5000` |
| Session Controller app | Desktop launcher on your laptop |
| Recording timeline in Frigate | Frigate web UI → pick a camera → scroll the timeline |

## Things NOT to do

- **Never** `docker restart frigate` or `sudo systemctl restart neurosurveillance-session` during someone else's recording without checking. Either action interrupts the live session. (For Frigate restarts in particular: since 2026-05-24 the daemon detects the restart and ignores the retained "ON" state messages, so no phantom session is created — but the live recording is still interrupted while Frigate boots.)
- **Never** click "Install" on Ubuntu's Update Manager popup for Docker or kernel updates on the NVR. The `apt-mark hold` should block it but the popup is misleading. Ask Andrea.
- **Never** delete files under `/srv/frigate/storage/recordings/` while Frigate is running — Frigate's database will diverge from what's on disk.
- **Never** edit `/srv/frigate/config/config.yml` without testing first. A typo crashes Frigate on next restart, taking out all four cameras at once.
- **Never** publish to MQTT without `-u nvr -P "$NVR_MQTT_PASSWORD"`. Since 2026-05-22 the broker rejects anonymous publishers — your `mosquitto_pub` will silently fail.
- **Never** commit `production-values.md` or any file containing the Mosquitto password to a public repository. That file is in the repo's `.gitignore` for a reason.

## Reference: equivalent CLI

For users who prefer the terminal over the desktop app. All API calls hit the daemon's local HTTP server on `127.0.0.1:8585`.

```bash
# Set metadata for chamber 0
curl -X POST 'http://127.0.0.1:8585/api/session/metadata?chamber_id=0' \
    -H 'Content-Type: application/json' \
    -d '{"mouse_id":"HETCF3R1","recording_type":"basal","user_name":"andrea"}'

# Check what the daemon is doing right now
curl http://127.0.0.1:8585/api/status | python3 -m json.tool

# Check overall system health
curl http://127.0.0.1:8585/api/health | python3 -m json.tool

# Check storage status (incl. can_record flag)
curl http://127.0.0.1:8585/api/storage | python3 -m json.tool

# Ask the journal what happened to a session
curl 'http://127.0.0.1:8585/api/journal?session_id=<UUID>' | python3 -m json.tool

# See the most recent nightly reconciler findings
curl http://127.0.0.1:8585/api/reconciler/last | python3 -m json.tool

# Trigger an ad-hoc reconciler pass (returns findings synchronously)
curl -X POST 'http://127.0.0.1:8585/api/reconciler/run?window_hours=24' | python3 -m json.tool

# Subscribe to live MQTT traffic from Frigate (needs nvr credentials since 2026-05-22)
docker exec mosquitto mosquitto_sub -u nvr -P "$NVR_MQTT_PASSWORD" -t 'frigate/#' -v
```

For more recipes: [[session-recording-workflow#How to ask the journal what happened|session-recording-workflow's troubleshooting section]].

## References

- [[../SYSTEM-OVERVIEW|System overview — one page]]
- [[../01-infrastructure/system-overview|System overview — Q&A and glossary]]
- [[../00-config/production-values|production-values.md]] — IPs, paths, credentials (do not commit publicly)
- [[session-recording-workflow|Session recording workflow]] — the detailed procedure
- [[../01-infrastructure/session-daemon/architecture|Session daemon architecture]] — how the daemon works internally
- [[../01-infrastructure/session-daemon/session-journal|Session journal (WAL)]] — what events get logged when
- [[../01-infrastructure/session-daemon/reconciler|Reconciler]] — what the nightly self-audit catches
- [[../_INDEX|Index of every doc]]

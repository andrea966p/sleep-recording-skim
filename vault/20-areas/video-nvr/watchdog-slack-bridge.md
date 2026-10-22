---
tags:
  - procedure
  - installation
  - alerting
  - watchdog
created: '2026-05-25'
updated: '2026-05-25'
status: active
---

# Watchdog → Slack Bridge (`nvr-mqtt-slack.service`)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A tiny background service on the NVR that watches for "recording stalled" alerts and posts them to the `#nvr-alerts` Slack channel within ~90 seconds.
>
> **Why it exists.** The recording-health watchdog (added 2026-05-18) detects when a camera stops writing video mid-session, but until now that alert only went to MQTT and the logs — nobody saw it. Netdata, which sends our other Slack alerts, has no way to read MQTT, so this small bridge fills the gap.
>
> **How to read this page.** If you just want it working, run the **Install** steps top to bottom. The **End-to-end test** proves the whole chain works. See [[nvr-system-overview|system overview]] for where this fits.

> [!quote] Paper-ready
> Recording-stall events published to MQTT by the session daemon's health watchdog are forwarded to a Slack channel by a standalone systemd bridge service, giving operators a ≤90-second notification when a camera stops writing video during an active session.

## Why a bridge (and not Netdata)

Netdata v2.10.3 ships no MQTT collector, so it cannot subscribe to `neurosurveillance/watchdog/+/stall` directly. The bridge subscribes for it — via `docker exec mosquitto mosquitto_sub` (mosquitto-clients is not installed on the host) — and forwards each message to the same Slack incoming-webhook Netdata and Uptime Kuma already use. It runs as a separate service, not inside the daemon, so a daemon crash (itself an alert condition) does not silence alerting.

The same service is the chosen path for reconciler → Slack (sprint task 4.6), which stays disabled until the 3-night reconciler dry-run (≈2026-05-27) establishes a noise floor.

## Files (version-controlled in the repo)

| Path (repo) | Purpose |
|---|---|
| `backend/scripts/nvr-mqtt-slack.py` | The bridge. Subscribes, formats, POSTs to Slack. |
| `deploy/nvr-mqtt-slack.service` | systemd unit. Runs as `skimlab` (docker group), `Restart=always`. |
| `deploy/nvr-mqtt-slack.env.example` | Template for the secrets env file. |
| `deploy/nvr-mqtt-slack-setup-env.py` | Generates `/etc/nvr-mqtt-slack.env` from existing configs (no hand-typed secrets). |

`/opt/neurosurveillance/session-daemon` is a symlink to the repo `backend/`, so the running bridge's `ExecStart` path (`session-daemon/scripts/nvr-mqtt-slack.py`) tracks the repo automatically. The one-time install files live in the repo's `deploy/` (a sibling of `backend/`, **not** under the symlink), so the install commands below reference them by full repo path.

## Install

Run in order. Stop if any step errors.

**1. Create the secrets env file** (reads MQTT password from `config.yaml` + webhook from Netdata; prints only a success line):
```bash
sudo python3 /home/skimlab/Monitoring_project/neurosurveillance/deploy/nvr-mqtt-slack-setup-env.py
```
Expect: `wrote /etc/nvr-mqtt-slack.env (mode 0600)`

**2. Install the unit:**
```bash
sudo cp /home/skimlab/Monitoring_project/neurosurveillance/deploy/nvr-mqtt-slack.service /etc/systemd/system/
```

**3. Reload systemd:**
```bash
sudo systemctl daemon-reload
```

**4. Enable + start:**
```bash
sudo systemctl enable --now nvr-mqtt-slack.service
```

**5. Verify running + subscribed:**
```bash
systemctl is-active nvr-mqtt-slack.service && journalctl -u nvr-mqtt-slack -n 5 --no-pager
```
Expect: `active`, then `nvr-mqtt-slack: subscribing to ['neurosurveillance/watchdog/+/stall']`

**6. Synthetic Slack smoke test** (fake stall message; no Pi disruption):
```bash
docker exec mosquitto mosquitto_pub -u nvr -P "$(python3 -c "import yaml;print(yaml.safe_load(open('/opt/neurosurveillance/config.yaml'))['mqtt']['password'])")" -t 'neurosurveillance/watchdog/pi_cam_0/stall' -m '{"camera":"pi_cam_0","lag_seconds":123,"last_segment_ts":null,"session_id":"test1234","ts":0}'
```
Expect: no terminal output, and a Slack message in `#nvr-alerts`:
`🚨 NVR recording STALL — pi_cam_0 lag=123s (session test1234) — no segments since recording started. Check the Pi / go2rtc for that camera.`

## End-to-end test (real stall)

Validates the full chain: watchdog detection → MQTT → bridge → Slack. Disruptive (briefly kills both Pi1 camera streams) — only run when no research recording is active (`curl -s http://127.0.0.1:8585/api/status | jq .manual_recordings` returns `{}`).

Watchdog timing: polls every 30s, fires when a camera's last segment is >60s stale, with a 30s start-grace. So the recording must run >30s before the test, and the alert lands within ~60–90s of stopping the stream.

1. Start a recording on a Pi1 camera (`pi_cam_0` or `pi_cam_1`) via the Frigate UI; let it run >30s.
2. Stop the stream:
   ```bash
   ssh skimlab@192.168.0.11 'sudo systemctl stop go2rtc'
   ```
3. Wait ≤90s — expect a Slack STALL alert for the camera.
4. Restore the stream:
   ```bash
   ssh skimlab@192.168.0.11 'sudo systemctl start go2rtc'
   ```
5. Stop the test recording. Frigate resumes writing segments on its own once the stream returns.

## Operations

- **Logs:** `journalctl -u nvr-mqtt-slack -f`
- **Restart:** `sudo systemctl restart nvr-mqtt-slack.service` (also auto-restarts if the mosquitto container restarts).
- **Rotate the webhook or MQTT password:** re-run step 1, then `sudo systemctl restart nvr-mqtt-slack.service`.
- **Enable reconciler alerts (4.6):** uncomment the reconciler topic + handler branch in `nvr-mqtt-slack.py`, then restart. Alert only when `partial_count + stuck_count + degraded_count > 0` (suppress `orphan_count`).

## References

- [[emergency-runbook#Symptom G — Watchdog STALL alert fired|emergency-runbook — Symptom G]] — how to act on a stall alert
- [[architecture|Session daemon architecture]]
- [[2026-05-stabilization-sprint-week-1-plan#Phase 4 — Monday: code quality + remaining ops|sprint plan — Phase 4.1]]
- [[production-values|production-values.md]] — MQTT credentials, Slack webhook (do not commit publicly)

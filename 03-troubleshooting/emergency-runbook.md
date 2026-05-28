---
tags:
  - troubleshooting
  - runbook
  - emergency
created: '2026-05-21'
updated: '2026-05-25'
status: active
---
First 10 minutes when something is wrong on the NVR. Each section: how to confirm the symptom, the safest immediate action, where to look next. **Do not restart Frigate or the daemon while a recording is active unless the recording is already broken.**

> [!warning] Active recording check (do this first, every time)
> ```bash
> curl -s http://127.0.0.1:8585/api/status | jq .manual_recordings
> ```
> Non-empty result = someone is recording. Any restart will create unwanted exports + may interrupt their data. Coordinate with the researcher before acting.

## Symptom A — Disk full / nearly full

**Confirm:**
```bash
df -h /srv/frigate/storage /opt/neurosurveillance/exports
curl -s http://127.0.0.1:8585/api/storage | jq
```
**Safe immediate action:** see [[../06-references/storage-troubleshooting|storage-troubleshooting]] — the storage system has a 200 GB EEG reserve cap that already blocks new recordings when free space < reserve. Most likely you need to either delete old exports or raise the cap.

**Do NOT** `rm -rf` inside `/srv/frigate/storage/recordings/` without stopping Frigate first — Frigate's DB will get confused. If recording is active, leave it and move old exports off-machine instead.

## Symptom B — Session daemon down

**Confirm:**
```bash
systemctl status neurosurveillance-session
curl -s http://127.0.0.1:8585/api/status     # connection refused?
journalctl -u neurosurveillance-session -n 50 --no-pager
```
**Safe immediate action:** if no active recording, `sudo systemctl restart neurosurveillance-session`. If a recording IS active, the recording continues in Frigate but the daemon's *in-memory* session metadata for that camera is lost on restart. Since 2026-05-23 the [[../01-infrastructure/session-daemon/session-journal|append-only WAL]] persists every session's lifecycle events (`START`, `EXPORT_BEGIN`, `EXPORT_COMPLETE`, `ABORT`, `STALL`) to `/opt/neurosurveillance/session_wal.db`, so the session can be reconstructed after the restart and the [[../01-infrastructure/session-daemon/reconciler|nightly reconciler]] will flag anything orphaned. Coordinate with the researcher first.

**Common causes:**
- Radiens disconnected → daemon logs `ERROR:radiens_poller: ... 446110 consecutive` but should NOT crash the daemon. If it did, it's a regression.
- MQTT broker down → see Symptom D.
- Config typo in `/opt/neurosurveillance/config.yaml` → check `journalctl` for `KeyError` / `yaml` errors.

## Symptom C — Frigate down or unhealthy

**Confirm:**
```bash
docker ps --filter name=frigate
docker logs --tail 100 frigate
curl -s http://127.0.0.1:5000/api/stats | jq .service.uptime
```
**Safe immediate action:** if no active recording, `cd /srv/frigate && docker compose restart frigate`. Since 2026-05-24 (Phase 3.1) the daemon subscribes to `frigate/available` and defers every external recording-state callback by `STATE_DEFER_SECONDS = 1.5`, so a Frigate restart **no longer spawns phantom manual sessions** — the retained `recordings/state=ON` that Frigate republishes on reconnect is cancelled before it can fire. A restart still interrupts any live recording while Frigate boots, so coordinate first. Sanity-check after restart:
```bash
journalctl -u neurosurveillance-session --since "2 min ago" | grep -c "Manual recording started"   # expect 0
```
If that count is **not** 0, the LWT/defer guard regressed — treat it as the [[../04-journal/2026-05/2026-05-20|2026-05-20]] pattern (Symptom F) and stop the spurious sessions via the Frigate UI.

**Common causes:**
- Pi unreachable → Frigate's ffmpeg can't pull RTSP → eventual stall. See Symptom E.
- Docker upgrade restarted Frigate → check `/var/log/apt/history.log` (`apt-mark hold` since 2026-05-20 should prevent this).
- Disk full → Frigate refuses to start when storage path is full.

## Symptom D — MQTT broker (Mosquitto) down

**Confirm:**
```bash
docker ps --filter name=mosquitto
mosquitto_sub -h 127.0.0.1 -t 'frigate/#' -C 1 -W 5     # post-Phase 1.3: needs -u/-P
```
**Effect:** Frigate can't publish recording state, daemon can't toggle recording, no MQTT-driven alerts.

**Safe immediate action:** `cd /srv/frigate && docker compose restart mosquitto`. Frigate auto-reconnects within ~10s, daemon auto-reconnects (see `frigate_controller: Unexpected MQTT disconnect ... will auto-reconnect` log).

**If the broker is up but every client is rejected** (`Connection Refused: not authorised`): this is the 2026-05-22 auth layer, not an outage. Since then `mosquitto.conf` has `allow_anonymous false` + `password_file /mosquitto/config/passwd`, and Frigate + the daemon both authenticate as user `nvr`. Check, in order:
```bash
docker exec mosquitto ls -l /mosquitto/config/passwd          # exists, owned 1883:1883, mode 0700
docker exec mosquitto cat /mosquitto/config/mosquitto.conf | grep -E "allow_anonymous|password_file"
```
If `passwd` is missing or empty (e.g. wiped by a bad redeploy), recreate it and restart only Mosquitto — credentials are in [[../00-config/production-values#Mosquitto MQTT Authentication (since 2026-05-22)|production-values]]:
```bash
mosquitto_passwd -c /srv/frigate/mosquitto/passwd nvr        # prompts for the password
sudo chown 1883:1883 /srv/frigate/mosquitto/passwd
sudo chmod 0700 /srv/frigate/mosquitto/passwd
docker compose restart mosquitto
```
**Emergency fallback only** (recording is blocked and you cannot find the password): set `allow_anonymous true` in `mosquitto.conf`, restart Mosquitto, restore auth as soon as the password is recovered. Never leave the broker anonymous — anything on the LAN can then toggle recordings.

## Symptom E — Pi unreachable / camera offline

**Confirm:**
```bash
ping -c 3 192.168.0.11    # Pi1 (pi_cam_0, pi_cam_1)
ping -c 3 192.168.0.12    # Pi2 (pi_cam_2, pi_cam_3)
curl -s http://192.168.0.11:1984/api/streams | jq    # go2rtc still running?
```
**Effect:** Frigate's ffmpeg loops on `Connection refused`, no segments written for that camera. The recording-health watchdog (2026-05-18) detects this within ~90s and emits MQTT STALL.

**Safe immediate action:** if the Pi is up but go2rtc is down → `ssh skimlab@192.168.0.1{1,2} 'sudo systemctl restart go2rtc'`. If the Pi is down → check power (Waveshare PoE HAT has known PMIC latch-up issue per [[incidents/2026-02-19-pmic-fault-poe-death]]). Power-cycle by unplugging the network cable for 30s.

## Symptom F — Unexpected recording fired (all cameras started without command)

**This is the [[../04-journal/2026-05/2026-05-20|2026-05-20]] pattern.** Confirm:
```bash
journalctl -u neurosurveillance-session --since "10 min ago" | grep "Manual recording started"
docker ps --filter name=frigate --format "{{.Names}}\t{{.Status}}"   # restarted recently?
tail -50 /var/log/apt/history.log    # docker upgrade?
```
**Safe immediate action:** stop recordings via Frigate UI (one click per camera). Then investigate the trigger using [[incidents/2026-05-20-docker-upgrade-and-startup-guard-regression|the 2026-05-20 incident note]] as a template — check apt history, docker logs, host uptime to distinguish power-blip vs upgrade vs manual restart.

## Symptom G — Watchdog STALL alert fired

You got a Slack `#nvr-alerts` message about a recording stall (or you see a `STALL` event in the journal). The recording-health watchdog (2026-05-18) polls Frigate's segment timestamps for cameras that *should* be recording; if a camera's newest segment stops advancing for longer than the threshold it publishes `neurosurveillance/watchdog/{camera}/stall`. Since 2026-05-25 (Phase 4.1) the Netdata MQTT collector forwards that to Slack within ~90s.

**What a STALL means:** Frigate itself is alive and the daemon thinks that camera is in an active session, but no new video is hitting disk for it. Almost always the cause is **upstream of Frigate** — the Pi or its go2rtc stream died, or the network dropped. It is *not* a daemon bug.

**Confirm + locate:**
```bash
# What the watchdog is publishing right now
docker exec mosquitto mosquitto_sub -u nvr -P "$NVR_MQTT_PASSWORD" -t 'neurosurveillance/watchdog/+/stall' -v -W 5

# Is the camera's newest segment actually stale? (epoch seconds; compare to `date +%s`)
sqlite3 /srv/frigate/storage/frigate.db \
  "SELECT camera, MAX(end_time) FROM recordings GROUP BY camera"

# Recent STALL events in the WAL
curl -s 'http://127.0.0.1:8585/api/journal?event_type=STALL&limit=5' | python3 -m json.tool
```

**Safe immediate action:** treat it as Symptom E for the affected camera — check the Pi (`192.168.0.11` = pi_cam_0/1, `192.168.0.12` = pi_cam_2/3), restart go2rtc if the Pi is up, power-cycle if it's down. The watchdog **does not auto-restart anything** (auto-recovery was deferred by council until ≥1 organic stall is observed), so the camera will stay stalled until you act. Once the upstream stream returns, Frigate resumes writing segments on its own; no daemon restart needed.

## Symptom H — Disk died / data lost / config wiped → restore from NAS

The nightly NAS backup ([[../02-procedures/installation/nas-backup|NAS Backup procedure]]) holds the last **3 days** of the vault, daemon code, daemon config + session WAL, and Frigate config. **Recorded videos are NOT in it** (too large — they live on the NVMe/Frigate cache only).

```bash
# 1. See what snapshots exist on the NAS
ssh -p 53 Andrea@100.120.86.10 'ls -lh e10_setup_backups'

# 2. Pull the newest snapshot back (ssh pipe — NOT scp/rsync; this NAS rejects both)
ssh -p 53 Andrea@100.120.86.10 'cat e10_setup_backups/e10_backup_YYYY-MM-DD.tar.gz' > /tmp/restore.tar.gz

# 3. Inspect before extracting (archive paths are relative to /)
tar tzf /tmp/restore.tar.gz | less

# 4. Extract to a staging dir, then copy back deliberately (do NOT blind-extract to /)
mkdir -p /tmp/restore && tar xzf /tmp/restore.tar.gz -C /tmp/restore
```

After restore, **regenerate** what was deliberately excluded: `npm install` (frontend), `cargo build` (Tauri), `python -m venv venv && pip install -r requirements.txt` (daemon), and `mosquitto_passwd` to rebuild `/srv/frigate/mosquitto/passwd` from the secret in [[../00-config/production-values#Mosquitto MQTT Authentication (since 2026-05-22)|production-values]]. Full step-by-step + what-is/isn't-included: [[../02-procedures/installation/nas-backup|NAS Backup procedure]].

## Where to look next

- `journalctl -u neurosurveillance-session -f` — live daemon log
- `docker logs -f frigate` — live Frigate log
- `/srv/frigate/logs/frigate/` — Frigate Python log (post-Phase 1.2 mount; before that, `/dev/shm/logs/` and lost on restart)
- `http://localhost:19999` — Netdata dashboard, system metrics + custom NVR alerts
- `http://localhost:3001` — Uptime Kuma, service availability + Slack alerts
- [[incidents/|incident archive]] — past patterns

## Escalation

If symptom doesn't match the above and you can't reach Andrea, see [[../02-procedures/bus-factor-runbook|bus-factor-runbook]] — written specifically for non-Andrea operators (where data lives, how to start/stop a session, what NOT to touch, escalation contacts, glossary of insider terms).

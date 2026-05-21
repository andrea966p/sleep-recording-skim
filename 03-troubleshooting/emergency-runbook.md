---
tags:
  - troubleshooting
  - runbook
  - emergency
created: '2026-05-21'
status: draft
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
**Safe immediate action:** if no active recording, `sudo systemctl restart neurosurveillance-session`. If a recording IS active, the recording continues in Frigate but the session metadata for that camera is lost on restart (this is the gap the [[../04-journal/2026-05/2026-05-01#Stage 2.1|append-only WAL]] in the stabilization sprint addresses). Coordinate with the researcher first.

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
**Safe immediate action:** if no active recording, `cd /srv/frigate && docker compose restart frigate`. **The 2026-05-20 startup-guard regression means any Frigate restart triggers spurious manual sessions** until Phase 3 fix ships — watch `journalctl -u neurosurveillance-session` for "Manual recording started" lines and immediately stop any unwanted session via Frigate UI.

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

## Where to look next

- `journalctl -u neurosurveillance-session -f` — live daemon log
- `docker logs -f frigate` — live Frigate log
- `/srv/frigate/logs/frigate/` — Frigate Python log (post-Phase 1.2 mount; before that, `/dev/shm/logs/` and lost on restart)
- `http://localhost:19999` — Netdata dashboard, system metrics + custom NVR alerts
- `http://localhost:3001` — Uptime Kuma, service availability + Slack alerts
- [[incidents/|incident archive]] — past patterns

## Escalation

If symptom doesn't match the above and you can't reach Andrea, the **bus-factor runbook** (currently TBD per [[../04-journal/2026-05/2026-05-01#Stage 3|council Stage 3]]) should go here.

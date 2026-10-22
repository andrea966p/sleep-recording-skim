---
type: incident
area: video-nvr
status: done
status-note: "partially-resolved"
tags:
  - troubleshooting
  - incident
  - frigate
  - docker
  - daemon
  - neurosurveillance
created: '2026-05-20'
severity: medium
affected:
  - e10ubuntu
  - frigate
  - neurosurveillance-session-daemon
---
## Summary
- **Date/Time:** 2026-05-20 11:46–16:34 KST
- **Duration:** Issue 1 ~4h 25min (11:46→16:11); Issue 2 ~45s (16:28→16:29)
- **Severity:** Medium — no data loss to scientific work (no active experiment), but ~13 GB of unwanted recordings created and required manual cleanup
- **Status:** Trigger blocked (`apt-mark hold`); underlying daemon guard regression still open

Two related issues surfaced during the same investigation:

1. **Trigger recurrence** — `aptdaemon` upgrading `docker-ce` restarted Frigate, which auto-enabled recording on all 4 cameras for **4h 25min**. This is the **third occurrence** of the 2026-04-01 pattern, despite the `50unattended-upgrades` blacklist in place since 2026-03-09 — because the GUI Update Manager uses `aptdaemon`, which bypasses the blacklist.
2. **Daemon startup-guard regression** — When Frigate was restarted again at 16:28 (manually, via `docker start frigate` during cleanup), the daemon's manual-session-manager created **4 fresh `ManualSession` records with new IDs** and produced 4 short auto-exports. This should have been suppressed by the 10s startup grace period and `_last_known_state` check documented in `01-infrastructure/session-daemon/architecture.md`.

## Context
- Frigate container had been up since 2026-02-12 (RestartCount low). System uptime 2 days 3:52 — no host reboot today.
- No active experiment running. Radiens was disconnected (daemon log full of `radiens_poller: Failed to connect to Radiens`).
- User noticed the unwanted recording ~4h after it began (no alert fired — see [[#Prevention]]).

## Issue 1 — Docker upgrade restarted Frigate, all 4 cameras auto-recorded

### Symptoms
- All 4 cameras (`pi_cam_0..3`) recording simultaneously, beginning at 11:46:43.
- ~13 GB of continuous segments under `/srv/frigate/storage/recordings/2026-05-20/02..07/`.
- 4 manual auto-exports created by the daemon: `2605201146_manual_pi_cam_{0,1,2,3}.mp4` (3.0–3.6 GB each) plus 4 session JSONs.
- `docker ps` showed `frigate`, `mosquitto`, `uptime-kuma` all with matching `Up 4 hours` status.

### Investigation
```bash
# Confirm host did NOT reboot
uptime                                    # 2 days 3:52
last -x reboot | head                     # last reboot was 2 days prior

# Confirm only Docker restarted
docker ps --format "table {{.Names}}\t{{.Status}}"

# Find what triggered the docker restart
tail -100 /var/log/apt/history.log
journalctl --since "5 hours ago" --until "3 hours ago" -p info \
  | grep -iE "docker|frigate|apt|unattended|upgrade"

# Confirm daemon saw the auto-recording start
journalctl -u neurosurveillance-session --since "today" \
  | grep -iE "state change|manual recording"
```

### Root cause
At **11:46:07**, `aptdaemon` (invoked by GNOME `update-manager`, running as `skimlab` uid 1000 — seen in journal: `update-notifier.desktop[3542727]`, `Activating service name='org.debian.apt'`) committed `docker-ce 29.5.0 → 29.5.1` plus `docker-ce-cli`, `docker-ce-rootless-extras`.

`systemd` stopped `docker.service` at 11:46:12. `docker.service` came back at 11:46:35 (running 29.5.1). Containers restarted via their `unless-stopped` policy at 11:46:36. Frigate loaded `record.enabled: true` from `/srv/frigate/config/config.yml` and published `ON` for all 4 cameras on `frigate/{cam}/recordings/state` at **11:46:43**.

The daemon's `_handle_external_recording_change` (in `backend/daemon.py`, see [[2026-04-08-frigate-export-stuck-and-missing-on-edges]]) saw the OFF→ON edges and created `ManualSession` records:
```
11:46:43  frigate_controller: External recording state change: pi_cam_0 -> ON (was OFF)
11:46:43  manual_session_manager: Manual recording started: camera=pi_cam_0, session=...
[same for pi_cam_1..3]
```

The `50unattended-upgrades` `Package-Blacklist` only applies to `unattended-upgrade`. **`aptdaemon` (which backs both GNOME Software Center and the Update Manager popup) bypasses it entirely.**

> [!warning] Recurrence pattern
> | Date | Versions | Window | Investigation |
> |---|---|---|---|
> | 2026-03-30 11:05 | docker-ce 29.3.0 → 29.3.1 | unknown | [[2026-04-01]] |
> | 2026-05-18 12:17 | docker-ce 29.4.1 → 29.5.0 | likely recorded but not investigated; ~430 MB residue in `recordings/2026-05-18/` | — |
> | 2026-05-20 11:46 | docker-ce 29.5.0 → 29.5.1 | 4h 25min | this incident |

### Resolution
```bash
sudo apt-mark hold docker-ce docker-ce-cli docker-ce-rootless-extras \
                   docker-buildx-plugin docker-compose-plugin containerd.io
apt-mark showhold | grep -E "docker|containerd"
```

All 6 packages held. **`aptdaemon` respects `apt-mark hold`** — this is the only known mechanism that does (the unattended-upgrades blacklist does not).

User stopped recordings via Frigate UI at 16:11:22–31 (clean OFF transitions in MQTT). Auto-exports completed cleanly (session JSONs written, MP4s moved into place).

Cleanup (in this order, with Frigate stopped to avoid Frigate touching files mid-delete):
```bash
# Stop Frigate
docker stop frigate

# Continuous segments (root-owned)
sudo rm -rf /srv/frigate/storage/recordings/2026-05-20/

# Manual auto-exports + session JSONs (skimlab-owned)
rm /opt/neurosurveillance/exports/manual/manual/2026-05-20/2605201146_manual_pi_cam_*.mp4
rm /opt/neurosurveillance/sessions/2605201146_manual_pi_cam_*_session.json
rmdir /opt/neurosurveillance/exports/manual/manual/2026-05-20

# Restart Frigate
docker start frigate
```

## Issue 2 — Daemon startup guard failed on cold `docker start frigate`

### Symptoms
When `docker start frigate` ran at 16:28:21 (during Issue 1 cleanup), the daemon log at **16:28:24** shows:
```
External recording state change: pi_cam_2 -> ON (was OFF)
Manual recording started: camera=pi_cam_2, session=f36c755b
[same for pi_cam_0, pi_cam_1, pi_cam_3 — new session IDs each]
```

Four new session JSONs (`2605201628_manual_pi_cam_*_session.json`) and four short MP4 auto-exports (`2605201628_manual_pi_cam_*.mp4`, 45–53 s each, ~8 MB each) were created before the user stopped them at 16:29:10–17.

### Why this should NOT have happened
Per [[architecture|session-daemon/architecture.md]], on daemon startup the manual-session detection path:

1. Calls `stop_all_recording()`.
2. **Waits 10 seconds** for Frigate to finish reasserting `record.enabled=true` from its config.
3. **Drains stale `_expected_states`** so the reassertion is ignored.
4. **Then** arms `_handle_external_recording_change` and tracks transitions via `_last_known_state`.

This guard was added specifically to prevent false `ManualSession` creation on every Frigate / daemon startup. On 2026-05-20 16:28 it did not fire — possibly because:
- The daemon was already running and only **Frigate** restarted (the guard runs on **daemon** startup, not Frigate startup).
- `_last_known_state` for each camera was `OFF` (from the user's manual stop at 16:11). Frigate's fresh `ON` after restart is a genuine OFF→ON edge from the daemon's perspective.

This means the guard's premise is wrong: it protects against **daemon** restart with Frigate already recording, but does nothing for **Frigate** restart with the daemon already running. Any Frigate-only restart (crash, manual restart, upgrade) will continue to produce spurious manual sessions.

### Resolution (interim)
No code change yet. Cleanup of the 16:28 artefacts:
```bash
sudo rm -rf /srv/frigate/storage/recordings/2026-05-20/      # 33 MB segments
rm /opt/neurosurveillance/exports/manual/manual/2026-05-20/2605201628_manual_pi_cam_*.mp4
rm /opt/neurosurveillance/sessions/2605201628_manual_pi_cam_*_session.json
```

## Prevention

### Done
- [x] `apt-mark hold` on all 6 Docker packages — blocks the GUI-driven upgrade trigger
- [x] Memory + vault note linking the recurrence pattern

### Open
- [ ] **Fix the daemon startup guard so it also handles Frigate-only restarts.** Options:
  - Subscribe to Frigate's `frigate/available` MQTT LWT topic; when it transitions `offline → online`, re-arm the same 10s grace period.
  - Tag in-flight `ON` transitions with a "config-reassertion" flag derived from frigate's startup timestamp (visible via `/api/stats` `service.uptime`).
- [ ] **`record.enabled: false` in Frigate config is OFF THE TABLE** — already investigated and rejected ([[2026-03-09|2026-03-09 journal]]: "would solve the restart issue but loses fail-safe if daemon crashes mid-session"; user has confirmed this breaks Frigate in practice).
- [ ] **Add monitoring alert for unexpected Docker container restarts.** Netdata + Slack already wired; need a rule on `docker.service` restart count or container `RestartCount` jumps so the next occurrence is caught in minutes, not hours.
- [ ] **Investigate 2026-05-18 residue** in `/srv/frigate/storage/recordings/2026-05-18/` (~430 MB) — likely from the docker 29.4.1 → 29.5.0 upgrade earlier this month.

> [!tip] How to distinguish a power-blip restart from a Docker-upgrade restart
> Both restart all containers simultaneously, but:
> - **Power blip / reboot:** `uptime` resets, `last -x reboot` shows a fresh entry, kernel logs start over.
> - **Docker upgrade:** host uptime intact, only `docker.service` shows stop/start in `journalctl`, `/var/log/apt/history.log` has a matching `aptdaemon role='role-commit-packages'` transaction.

## Related
- [[2026-04-01|2026-04-01 journal]] — first occurrence of this pattern, root-cause investigation
- [[2026-03-09|2026-03-09 journal]] — `record.enabled: false` considered and deferred; `50unattended-upgrades` blacklist added (now known insufficient)
- [[2026-04-08-frigate-export-stuck-and-missing-on-edges]] — same `_handle_external_recording_change` path, different failure mode
- [[architecture|session-daemon/architecture.md]] — describes the startup guard that failed here

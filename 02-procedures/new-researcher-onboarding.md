---
tags:
  - procedure
  - onboarding
created: '2026-05-21'
status: draft
---
Skeleton — fleshed out in Phase 4.4 of the [[../04-journal/2026-05/2026-05-20#Stabilization sprint plan|stabilization sprint]].

## Day 0 — accounts and access

- [ ] Add researcher to the lab members list in `/opt/neurosurveillance/config.yaml` (`lab_members: [...]`) — currently only `["andrea"]`, see [[../04-journal/2026-05/2026-05-20]] open item.
- [ ] Slack channel: `#nvr-alerts` for Netdata + Uptime Kuma notifications.
- [ ] LAN / Tailscale access — confirm researcher's laptop can reach `192.168.0.50` (NVR).
- [ ] Show how to launch the Tauri app on their laptop and reach the daemon API at `http://192.168.0.50:8585`.

## First recording walkthrough

- [ ] Demonstrate Frigate UI at `http://192.168.0.50:5000` — login, navigate to cameras, start/stop recording from the camera card.
- [ ] Show where exports land: `/opt/neurosurveillance/exports/manual/manual/YYYY-MM-DD/` (manual sessions, no Radiens) or `/opt/neurosurveillance/exports/{researcher}/{mouse_id}/YYYY-MM-DD/` (Radiens-driven sessions).
- [ ] Show how to read session JSONs — the source of truth for what a session contains.
- [ ] Explain naming convention: `YYMMDDhhmm_{label}_{camera}.mp4` for manual, mouse_id-based for Radiens.

## What to do if a recording goes wrong

- [ ] Walk through [[../03-troubleshooting/emergency-runbook|emergency-runbook]] symptom-by-symptom.
- [ ] Stress test together: stop go2rtc on Pi1 mid-recording, observe watchdog STALL, restart go2rtc, confirm recovery.
- [ ] Show where to find evidence after the fact (journal entries in [[../04-journal/]], incident reports in [[../03-troubleshooting/incidents/]]).

## Storage hygiene

- [ ] How to check disk usage: `/api/storage`, header storage badge, [[../06-references/storage-troubleshooting|storage-troubleshooting]] reference.
- [ ] The 200 GB EEG reserve cap and what happens when storage runs low.
- [ ] How to move old exports off-machine when needed (NAS / external drive).

## Things NOT to do

- Never `docker restart frigate` or `systemctl restart neurosurveillance-session` during someone else's recording without coordinating first — interrupts their data.
- Never click "Install" on Ubuntu's Update Manager popup for Docker / kernel updates — the apt-mark hold should block this but the popup is misleading. Ask Andrea.
- Never delete from `/srv/frigate/storage/recordings/` while Frigate is running — Frigate's DB will diverge.
- Never edit `/srv/frigate/config/config.yml` without testing first — invalid config crashes Frigate on next restart.

## References

- [[../00-config/production-values|production-values.md]] — IPs, paths, credentials
- [[../_INDEX|_INDEX.md]] — vault home
- [[../03-troubleshooting/emergency-runbook|emergency-runbook.md]] — first 10 min when something breaks
- [[../06-references/storage-troubleshooting|storage-troubleshooting.md]] — disk space + reserve cap
- [[../01-infrastructure/session-daemon/architecture|session-daemon/architecture.md]] — how the daemon talks to Frigate

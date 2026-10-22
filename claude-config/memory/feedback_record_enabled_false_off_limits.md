---
name: feedback-record-enabled-false-off-limits
description: "Never suggest setting Frigate's record.enabled to false to fix restart-triggered recordings — user has ruled this out"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0b64ed9b-5689-4074-8603-f37b0836d899
---

Do not propose setting `record.enabled: false` in Frigate's config.yml as a fix for "Frigate restart triggers unwanted recordings."

**Why:** User stated this was already investigated and breaks Frigate. The vault documentation (`04-journal/2026-03/2026-03-09.md`) records it as "considered but deferred — would solve the restart issue but loses fail-safe if daemon crashes mid-session." User's recollection is stronger ("breaks Frigate") — there is additional context not in the vault. Either way: not on the table.

**How to apply:** When investigating "Frigate restart causes unwanted recordings," skip the obvious `record.enabled: false` suggestion. Look instead at:
1. Preventing the restart trigger (e.g., `apt-mark hold` on docker packages — done 2026-05-20)
2. Strengthening the daemon's existing startup guard (10s grace period + `_last_known_state` check documented in `20-areas/video-nvr/session-daemon/architecture.md`) — this guard failed on 2026-05-20 16:28 cold start (see [[project-daemon-startup-guard-regression]])

Related: [[project-docker-upgrade-recordings]]

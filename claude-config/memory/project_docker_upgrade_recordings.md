---
name: project-docker-upgrade-recordings
description: "Docker upgrades through GNOME update-manager (aptdaemon) bypass the unattended-upgrades blacklist, restart Frigate and fire recordings on all cameras; apt-mark hold is the fix. Incident in the vault"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b64ed9b-5689-4074-8603-f37b0836d899
---

Recurring (2026-03-30, 2026-05-18, 2026-05-20: 4 h 25 min of unwanted recording): aptdaemon (GNOME update-manager, uid 1000) upgrades docker-ce, docker.service restarts, Frigate returns with `record.enabled: true` and flips MQTT recording state ON on every camera. The `50unattended-upgrades` blacklist does not apply to aptdaemon; the only mechanism it respects is `apt-mark hold` on `docker-ce docker-ce-cli docker-ce-rootless-extras docker-buildx-plugin docker-compose-plugin containerd.io` (applied 2026-05-20; `apt-mark showhold` re-checked 2026-10-22).

Details: [[2026-05-20-docker-upgrade-and-startup-guard-regression]] · [[_video-nvr-hub]]

- When all cameras fire at once: check `docker ps` uptime FIRST, then `/var/log/apt/history.log` for an aptdaemon docker upgrade.
- Related: [[project_docker_sha_pin_pattern]]
- Verify the next docker security advisory does NOT auto-install (hold is in place).

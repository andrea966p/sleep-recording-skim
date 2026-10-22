---
name: project-docker-upgrade-recordings
description: "Recurring incident — Docker upgrades (via aptdaemon/GNOME update-manager, bypassing unattended-upgrades blacklist) restart Frigate which fires unwanted recordings on all cameras"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0b64ed9b-5689-4074-8603-f37b0836d899
---

Docker package upgrades trigger unwanted simultaneous recordings on all 4 cameras. Pattern: aptdaemon (invoked by GNOME `update-manager` GUI as uid 1000) → docker-ce upgrade → docker.service restart → restart-policy brings frigate back up → frigate's `record.enabled: true` config flips MQTT `frigate/{cam}/recordings/state` to ON for pi_cam_0..3 simultaneously.

**Why:** `/etc/apt/apt.conf.d/50unattended-upgrades` blacklist only affects `unattended-upgrade`. The GUI update-manager uses aptdaemon, which bypasses the blacklist entirely.

**How to apply:** When user reports "all recordings fired at the same time" or sees simultaneous MQTT ON events across all cameras, FIRST check `docker ps` for matching container uptime, then `/var/log/apt/history.log` for aptdaemon docker upgrades. The fix is `apt-mark hold` on `docker-ce docker-ce-cli docker-ce-rootless-extras docker-buildx-plugin docker-compose-plugin containerd.io` — this is the only mechanism aptdaemon respects.

**Occurrences:**
- 2026-03-30: docker-ce 29.3.0 → 29.3.1 (investigated Apr 1)
- 2026-05-18 12:17: docker-ce 29.4.1 → 29.5.0 (likely also caused unwanted recordings; never investigated)
- 2026-05-20 11:46: docker-ce 29.5.0 → 29.5.1 (4h 25min of unwanted recording before user stopped it at 16:11)

After 2026-05-20: user applied `apt-mark hold` on docker packages. Verify next docker security advisory does NOT auto-install.

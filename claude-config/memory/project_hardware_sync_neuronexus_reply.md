---
name: project_hardware_sync_neuronexus_reply
description: "Hardware sync XDAQ DO 03 to Pi GPIO: unit is a Gen-1 XDAQ Core (Opal Kelly USB), vendor items closed 2026-06-05, only bench validation left; Wire 2 delivers sync, continuous recording rejected. Detail in the vault"
metadata:
  node_type: memory
  type: project
  originSessionId: fd8990d6-5f4c-44ea-8ebc-31ce903b77dc
  modified: 2026-10-22T00:00:00.000Z
---

Our unit is a Gen-1 XDAQ Core (Opal Kelly USB `151f:0130`), not a Core2. KC's round-3b reply (2026-06-05) closed all vendor items: Gen-1 DB25 pinout = Gen-2, 3.3 V fixed outputs (TI SN74LVC2G17, ~20 mA), star grounding with the Core as hub, so one `DO 03` (pin 22, Allego "Gated" + "BNC Breakout Board" slider ON) star-wires to 4+ Pi GPIO with NO buffer. `DAQ_ON` (pin 13) is a streaming indicator and dirty when idle: do not use it as the gate. Remaining work = bench validation.

Details: [[overview]] (hardware-sync) · [[wiring-guide]] · [[xdaq-core2-manual-reference]] · [[xdaq-core-gen1-ubuntu-driver]] · [[neuronexus-inquiry-email]] · [[2026-07-27-video-eeg-sync-recording-architecture]] · [[hardware-sync-bench-test-do03]]

- 🔴 Wire 1 (the gate) buys trigger latency, not synchronisation; Wire 2 (periodic ~1 pulse/10 s into DI 03, pin 2) is what delivers sync. Frigate's toggle drops the last 10-20 s of every session: stop recording ~30 s after the EEG, start ~30 s before.
- 🛑 24/7 continuous recording was rejected by Andrea (about 455 GB for a 14 s problem): do not re-propose it. In-frame LED rejected 2026-07-28.
- After any Allego or host restart the session daemon needs `systemctl restart neurosurveillance-session.service` (UNAUTHENTICATED client-UUID error).
- `overview.md`'s Current State table still says DAQ_ON pin 13 (stale, vault note VN-3); the correct gate is `DO 03` pin 22.
- 🛑 Design rules (full text in the 2026-07-27 architecture note): fire the Wire 2 pulse from the camera's FRAME-CAPTURE CALLBACK, NOT a timer (a timer is circular); use cumulative frame counts, NEVER PTS (Frigate `-c:v copy`, `-reset_timestamps 1`); the daemon must drain ~30 s then release a lease, NEVER publish OFF; cameras are an INDEPENDENT instrument (the gate is annotation only, never a capture switch) and EEG-session video is started by a human or the daemon, not gated on the EEG signal.

---
name: project_phase_4_complete
description: "Phase 4 of the stabilization sprint shipped 2026-05-25 (commit b5485ee, tag stabilization-week-1) — sprint week 1 closed"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1586510f-8585-4984-ab9c-4ab00319c308
---

Phase 4 ("code quality + remaining ops") of the [[2026-05-20]] stabilization sprint shipped **2026-05-25**, commit `b5485ee`, tag **`stabilization-week-1`** on `andrea966p/neurosurveillance`. Closes sprint week 1 (Phases 1–4).

What shipped:
- **4.1 Watchdog → Slack** via the `nvr-mqtt-slack.service` bridge (the planned Netdata collector doesn't exist — see [[pattern_netdata_no_mqtt_collector]]). Full E2E validated (stopped go2rtc on Pi1 mid-recording → Slack STALL ≤90s; WAL captured the STALL).
- **4.2 ffprobe export sanity check** in `daemon._execute_export` (plan wrongly said `frigate_controller._move_export_file`). `<0.95×` requested duration ⇒ `export_status="completed (partial: Xh of Yh)"` + `probe_duration_seconds`/`duration_ok` in the EXPORT_COMPLETE payload. Deployed via daemon restart.
- **4.4** fleshed `emergency-runbook` (new Symptom G watchdog interpretation, Mosquitto auth recovery, post-Phase-3 restart-safety fixes) + `storage-troubleshooting`; new vault [[watchdog-slack-bridge]] install doc.
- **Mosquitto passwd** locked to `0600` + `1883:1883` (plan said 0700; data file needs no exec bit).
- **4.3** (requirements radiens comment) + **"suppressed (was None)" log** were already done in earlier phases.

Still open / next:
- **4.6 reconciler → Slack** deferred until the 3-night dry-run (May 25/26/27) sets a noise floor; bridge topic stubbed for a one-line enable. NOTE: tonight's 00:01 run shows partial=1/degraded=1 from the E2E test session `554cd949` (teststall) — ages out of the 24h window by the May 27 run. WAL was deliberately not edited (append-only).
- **Phase 5 burn-in** Tuesday 2026-05-26. Stage 2.4 USB backup still deferred.
- 3.2 GB `/opt/neurosurveillance/radiens.log` carry-over still on disk.

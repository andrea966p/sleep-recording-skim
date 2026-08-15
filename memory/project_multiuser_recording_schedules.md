---
name: project_multiuser_recording_schedules
description: "One XDAQ = one global R_ON/R_OFF, no native per-port start/stop timing; workaround + TODO list for multi-user overlapping-schedule recording"
metadata: 
  node_type: memory
  type: project
  originSessionId: 078f71a9-9428-4207-8d58-9d7959424972
---

Came up 2026-07-14: user wants to start their 4 mice Monday 9am (48h) while another lab member starts their 4 mice Monday 9pm (48h), same shared rig/XDAQ.

**Confirmed constraint:** Allego Record button = ONE global R_ON/R_OFF for the whole XDAQ box (all 4 ports, one file). Vault `session-recording-workflow.md`: "Radiens provides a single global R_ON/R_OFF signal." Per-port channel SELECTION exists but that's not per-port timing. Multiple Allego GUI windows do NOT help — all windows are clients of the same `allegoserver` backend (same one the Python SDK talks to over gRPC/50051), so state is shared, not per-window (architectural inference, not yet bench-tested).

**Workaround for now (zero new code/risk):** union the recording window (press Record once at the earliest start), pre-wire+select both users' channels from the start, delay only the ANIMAL-side slip-ring connection for the later user (no Allego/hardware re-touch, no crash risk), stop once at the latest end, then slice the one master XDAT file per user by sample index offline using existing `xdat_io.py`/`multimouse_scan.py` tooling.

**Open TODO (real fix):** bench-test whether SDK's `start_recording(port)`/`stop_recording(port)` (see [[radiens-api-reference]] in vault) actually isolates one port's recording — untested, daemon has only ever polled state not called these. Ask NeuroNexus/KonteX directly. Or get a second physical XDAQ/acquisition box for true independence (vault already flags this as the fallback: "additional Radiens instances and daemon configuration would be required").

Full writeup + TODO checklist: vault `02-procedures/multi-user-independent-recording-schedules.md`.

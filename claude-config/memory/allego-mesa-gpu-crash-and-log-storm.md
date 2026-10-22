---
name: allego-mesa-gpu-crash-and-log-storm
description: "2026-08-24: Allego GPU process crashed in Mesa (divide error) and a 6.5 GB autoScanWorker log storm; app death ended the recording. --disable-gpu workaround dropped 2026-09-16."
metadata: 
  node_type: memory
  type: project
  originSessionId: aa023ba0-4d68-4842-9819-c574f4dde34b
  modified: 2026-08-24T08:46:41.218Z
---

**2026-08-24:** the Allego GUI froze, then the whole app died at 13.59 min of a planned 60 min and took the recording with it. Fault 1: GPU process SIGFPE in libgallium (reproducible); `--disable-gpu` cured it (since dropped 2026-09-16, see [[allego-blank-monitor-canvas-texture-limit]]). Fault 2: `autoScanWorker` retry loop wrote a 6.97 GB unrotated `~/.local/state/radiens/logs/allego-ui.log` (`truncate -s 0` is safe while running). A frozen GUI does NOT interrupt the recording; an allegoserver/app death DOES.

Details: [[allego-mesa-gpu-crash-and-log-storm]]

🔴 `pkill -f '/opt/allego/allego'` KILLS YOUR OWN SHELL (the tool wrapper's command line matches): kill Allego by explicit PID. ⚠️ A FRESH Allego launch comes up at `sample_freq = 30000` and a wrong `system_mode` (rig runs 1000 Hz, XDAQ_ONE_REC): always re-check `get_status()` before recording. 🔑 Judge a recording by bytes on disk and the rms of a known channel across the event, never by whether the window responds. Impedance cannot be measured while acquiring (`Z_measure attempted during data acq`).

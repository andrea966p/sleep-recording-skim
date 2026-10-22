---
name: allego-stop-works-and-the-30s-size-lag
description: "Bench-tested 2026-09-11: set_recording('off') works; Allego updates the .xdat file SIZE only every ~30 s, so any byte-growth check under ~35 s is a false negative. Stop in a finally."
metadata:
  type: reference
---

**2026-09-11 bench test:** `set_recording('off')` works (R_ON -> R_OFF on the first call). The trap: `os.path.getsize()` of the .xdat stays 0 for the first 30 s and then jumps (31,657,984 B = 30.2 s at 1 kHz), so data is never missing, only invisible.

Details: [[2026-09-11-allego-control-bench-test]]

🔴 Any "is it growing?" check with a window shorter than ~35 s reports a HEALTHY recording as dead. Verify in TWO stages: started = file created + `mode == R_ON` (immediate); confirmed growing = size increased, only after >= 35 s. Any script that asserts on growth MUST stop the recording in a `finally`, or a false negative leaves the amplifiers running. `qc/start_recording_at.py` waits 5 s then measures across 40 s: do not "optimise" that window down.

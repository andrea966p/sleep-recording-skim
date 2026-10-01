---
name: allego-stream-30x-rate-label-lies
description: Allego reported sample_freq 1000 while the XDAQ streamed at 30 kHz (stream time 30x wall clock); Monitor froze. Label check is not enough.
metadata:
  node_type: memory
  type: project
  originSessionId: 533bb1b2-75c7-42ef-bdb1-704e3dd70a51
  modified: 2026-09-30T10:32:16.527Z
---

2026-09-30 ~15:20 KST, after a fresh Allego launch: `get_status().sample_freq == 1000.0`, XDAQ_ONE_REC,
ports A/B 64 ch — yet `stream.time_range` advanced **150 s per 5 s of wall clock (30x)**, i.e. the box
was still at the fresh-launch 30 kHz ([[allego-mesa-gpu-crash-and-log-storm]]). Symptom Andrea saw:
Monitor draws, then freezes. By 19:06 (after Andrea re-streamed) rate was 1.0x and a 15 min console run
gave 898,688 samples in 898 s.

**Why:** the eeg-recorder `allego.py` pre-flight checks only the `sample_freq` label, so it would pass
a 30x stream and record a file with a wrong-rate header.

**How to apply:** before any recording after an Allego launch, stream ~10 s and compare
`time_range[1]` delta to wall clock (must be ~1.0x). If 30x: stop stream, set another rate, set 1 kHz
again, restream; else relaunch Allego and set 1 kHz + XDAQ ONE REC before Stream. A rate check in the
console pre-flight is not built yet.

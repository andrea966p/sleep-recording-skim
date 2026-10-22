---
name: allego-stream-30x-rate-label-lies
description: "2026-09-30: Allego reported sample_freq 1000 while the XDAQ streamed at 30 kHz (stream time 30x wall clock); Monitor froze. Measure stream.time_range vs wall clock before recording."
metadata:
  node_type: memory
  type: project
  originSessionId: 533bb1b2-75c7-42ef-bdb1-704e3dd70a51
  modified: 2026-09-30T10:32:16.527Z
---

**2026-09-30:** after a fresh Allego launch `get_status().sample_freq == 1000.0` (XDAQ_ONE_REC, ports A/B 64 ch) while `stream.time_range` advanced 150 s per 5 s of wall clock (30x): the box was still at the fresh-launch 30 kHz. Symptom: Monitor draws, then freezes. The console's `allego.py` pre-flight compared only the label, so it would have passed a 30x stream and written a wrong-rate header (a rate check in the console pre-flight was not built as of 2026-09-30).

Details: [[allego-stream-30x-rate-label-lies]]

How to apply: before any recording after an Allego launch, stream ~10 s and compare the `time_range[1]` delta to wall clock (must be ~1.0x). If 30x: stop stream, set another rate, set 1 kHz again, restream; otherwise relaunch Allego and set 1 kHz + XDAQ ONE REC before Stream.

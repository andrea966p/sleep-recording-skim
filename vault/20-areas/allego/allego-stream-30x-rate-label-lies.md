---
type: incident
area: allego
status: active
status-note: "the console pre-flight still checks only the sample_freq label; a measured-rate check is not built"
created: 2026-09-30
tags: [allego, sampling-rate, incident, preflight]
---

# Allego said 1000 Hz while the XDAQ streamed at 30 kHz

> [!abstract] TL;DR
> **What broke.** On 2026-09-30 about 15:20 KST, after a fresh Allego launch, `get_status().sample_freq` was `1000.0`, yet `stream.time_range` advanced 150 s per 5 s of wall clock (30x). The box was still at the fresh-launch 30 kHz. The Monitor drew, then froze.
> **Fix.** Before any recording after an Allego launch, stream about 10 s and compare the `time_range[1]` delta with wall clock. It must be about 1.0x.

> [!info] Promoted from a Claude memory file on 2026-10-22
> Written from the memory note `allego-stream-30x-rate-label-lies` (saved 2026-09-30) and the open item in [[2026-09-29]] (the console's first real run from the UI). The fresh-launch 30 kHz default is first recorded in [[allego-mesa-gpu-crash-and-log-storm]].

## Symptoms and evidence

Ports A and B 64 channels each, `XDAQ_ONE_REC`, label 1000 Hz. After Andrea re-streamed, at 19:06 the rate was 1.0x and a 15 minute console run gave 898,688 samples in 898 s.

## Root cause

The rate change reached the label, not the box. The `eeg-recorder` pre-flight (`allego.py`) checks only the `sample_freq` label, so it would pass a 30x stream and record a file with a wrong-rate header.

## Fix and how to apply it

Before any recording after an Allego launch, stream about 10 s and compare the `time_range[1]` delta with wall clock (must be about 1.0x). If it is 30x: stop the stream, set another rate, set 1 kHz again and restream; otherwise relaunch Allego and set 1 kHz and `XDAQ_ONE_REC` before Stream.

## Prevention

A rate check in the console pre-flight is not built yet (checked 2026-10-22: `eeg-recorder/backend/allego.py` compares only `sample_freq` with the expected value, and nothing reads `time_range`). Until it is, the label check in [[eeg-recording-console]] section 5 is necessary but not sufficient. Related: [[starting-the-rig-after-a-restart]] · [[radiens-api-reference]]

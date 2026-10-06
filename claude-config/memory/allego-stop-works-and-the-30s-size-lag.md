---
name: allego-stop-works-and-the-30s-size-lag
description: Bench-tested 2026-09-11 - set_recording('off') works fine, and Allego only updates the .xdat file SIZE every ~30 s, so any byte-growth check shorter than that reports a false negative.
metadata:
  type: reference
---

Measured on the live rig 2026-09-11, output redirected to a scratch dir so nothing
landed in `~/radix/data`.

**✅ `set_recording('off')` WORKS.** `R_ON -> R_OFF` on the first call, file stops growing,
`set_streaming('off')` follows cleanly. I had flagged it as "never called in this repo" —
true of the code, but it is not a risky call. Do not treat stopping as the hard part.

**🔴 THE REAL TRAP: the file SIZE updates only every ~30 s.**

| t after `set_recording('on')` | file exists | `os.path.getsize()` |
|---|---|---|
| 0.5 s | yes | **0** |
| 3.5 s .. 27.5 s | yes | **0** |
| **30.0 s** | yes | **31,657,984** (jumps in one step) |

31,657,984 / (262 ch x 4 B) = 30,208 samples = 30.2 s at 1 kHz, so the data was never
missing — only invisible to `stat`. Allego flushes metadata in ~30 s blocks.

⇒ **Any "is it growing?" check with a window shorter than ~35 s reports a HEALTHY recording
as dead.** I wrote an 11 s check and it fired a false negative, which then left the rig in
`R_ON` because the script asserted out before its stop call.

- `qc/start_recording_at.py` is safe: it waits 5 s, then measures across 40 s, so at least one
  flush has happened. **Do not "optimise" that window down.**
- A control service should verify in TWO STAGES: *started* = file created + `mode == R_ON`
  (immediate), *confirmed growing* = size increased, only after >= 35 s.
- Any script that asserts on growth MUST stop the recording in a `finally`, or a false
  negative leaves the amplifiers running.

Context: [[skim-nas-smb-and-channel-stripper]], [[radiens-4-has-no-per-port-recording]].
The start path and its gRPC `ConfigRecording` workaround are in
`eeg-emg-analysis/qc/start_recording_at.py`; `set_recording_config()` is still broken.


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐⭐ **[ALLEGO STOP WORKS; FILE SIZE LAGS ~30 s](allego-stop-works-and-the-30s-size-lag.md).** `getsize()` reads 0 for a full 30 s ⇒ any growth check under ~35 s is a FALSE NEGATIVE. Stop in a `finally`.

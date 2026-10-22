---
type: experiment
area: allego
status: done
tags: [experiment, allego, radiens, recording, control, measurement]
created: 2026-09-11
---

# Bench test: can we stop Allego from Python, and can we tell a recording is alive?

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A twenty-minute test on the live rig, with no animals connected, to settle two
> questions before building software that starts and stops recordings by itself: does the "stop"
> command actually work, and how do we know a recording is really writing data?
>
> **Why it exists.** We were about to hand a machine the power to start and stop the amplifiers
> unattended. Every previous recording here was stopped by a person clicking a button in the Allego
> window. Nothing in our code had ever issued a stop instruction, so nobody could say from evidence
> whether it worked. Guessing was not acceptable for a tool that will run overnight with animals
> attached.
>
> **How to read this page.** Section 1 is the two answers. Section 2 is the surprise, which turned
> out to matter far more than the question we set out to ask. Section 3 is what changed in the code
> because of it. Background on the rig is in [[nvr-system-overview]].

## 1. The two answers

**Stopping works.** `set_recording('off')` moved the recorder from `R_ON` to `R_OFF` on the first
call, the file stopped growing, and `set_streaming('off')` followed cleanly. Repeated twice.

This closes a question that had been open only because of an absence: `grep` across every `.py` and
`.sh` in the workspace finds **no call to `set_recording('off')`, `RecordMode.OFF` or
`set_record_state` anywhere**, while `set_recording('on')` appears once. The vault documents the
start sequence repeatedly and never mentions stopping through the API. Recording durations are also
ragged — 20.326 h, 20.121 h, 20.078 h, 1.802 h, 0.592 h — which is what a person clicking Stop when
they arrive looks like, not a programmatic stop. So the absence was real, but it was an absence of
*use*, not evidence of a problem. **Stopping is not the hard part and should not be treated as risky.**

**Telling a recording is alive is the hard part.** See section 2.

> [!quote] Paper-ready
> Recording control is exercised through the Radiens Python API. The recorder is configured by
> constructing the `ConfigRecording` message directly, because the client library omits a required
> enumeration field; recording is then started and stopped with `set_recording`. Because the
> acquisition software updates the data file's reported size only in approximately 30-second
> blocks, a recording is confirmed as live in two stages: the file's existence and the recorder's
> reported state give immediate confirmation that acquisition began, and an increase in file size
> measured over a window longer than the flush interval confirms that data are reaching disk.

## 2. The surprise: the file size lags THIRTY SECONDS behind reality

The test was written to start a recording, wait 11 s, and assert that the file had grown. It
asserted, failed, and **left the rig recording**, because the assertion fired before the stop call.
The recording was completely healthy.

Polling the file every 500 ms from the moment of `set_recording('on')`:

| t after start | file exists | `os.path.getsize()` |
|---|---|---|
| 0.5 s | yes | **0** |
| 3.5 s | yes | **0** |
| 6.5 s … 27.5 s | yes | **0** |
| **30.0 s** | yes | **31,657,984** |
| 33.0 s | yes | 31,657,984 |

31,657,984 bytes ÷ (262 channels × 4 bytes) = **30,208 samples = 30.2 s at 1 kHz.** The data were
never missing. Allego creates the file immediately and then flushes its metadata in roughly 30-second
blocks, so `stat` reports zero for the whole first block and then jumps.

After the stop, the size held steady across a further 4 s — the file really had stopped.

> [!danger] ANY GROWTH CHECK SHORTER THAN ~35 SECONDS REPORTS A HEALTHY RECORDING AS DEAD
> This is the single easiest way to get recording control wrong on this rig, and it is invisible:
> the failure looks exactly like a broken recording. An 11-second check produced a false negative
> on a recording that was writing perfectly.
>
> `eeg-emg-analysis/qc/start_recording_at.py` is **safe** — it waits 5 s, then measures across 40 s,
> so at least one flush has always happened. **Do not "optimise" that window down.** It is not
> generous, it is barely sufficient.

> [!danger] A SCRIPT THAT ASSERTS ON GROWTH MUST STOP THE RECORDER IN A `finally`
> Our test did not, and a false negative therefore left the amplifiers running with nobody watching.
> On a rig that writes 90 GB/day that is not a harmless mistake.

## 3. What changed because of this

| Finding | Change |
|---|---|
| stop works | `eeg-recorder/backend/allego.py::stop()` — plain `set_recording('off')`, verified, safe to call when idle so error paths can use it |
| size lags ~30 s | verification split in two: `start()` returns when the file exists and the mode is `R_ON`; `confirm_growing()` is separate and **refuses a window shorter than 35 s** rather than silently lying |
| a false negative left the rig recording | `start()` stops the recorder in an exception handler before re-raising |
| users would see "0 bytes" and panic | the console displays "0 bytes is normal at first" for the first 90 seconds |

## 4. How it was run, and what it touched

Run from `/opt/neurosurveillance/venv/bin/python3` — the only interpreter with `radiens`.

- Output was redirected to a scratch directory by setting `ConfigRecording.baseFilePath`, so
  **nothing was written to `{RAW_ROOT}`**, confirmed afterwards with `find -newermt`.
- No animals were connected. Recording is passive and stimulates nothing, so the test could not have
  harmed an animal in any case.
- Rig state before and after: `R_OFF`, `S_OFF`, `XDAQ_ONE_REC`, 1000 Hz, four ports × 64 channels.
- **A side effect that had to be undone:** `ConfigRecording` is persistent. The test left Allego
  pointed at a scratch directory that was then deleted, so a person pressing Record in the GUI would
  have written to a missing path. The configuration was restored to `{RAW_ROOT}` with
  `baseFileName=allego` immediately. ⚠️ **Any future test that redirects the recording path must
  restore it**, and `get_status().recording.path` cannot be used to check, because it reports the
  calling process's working directory rather than the output directory.

## 5. Related

- [[eeg-recording-console]] — the tool this was built for
- [[scheduled-recording-and-watchdogs]] — the existing unattended start path, whose
  40-second window this validates
- [[multi-user-independent-recording-schedules]] — carries the retraction of the
  per-port recording claim, measured the same day

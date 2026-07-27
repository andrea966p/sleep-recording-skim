---
tags: [decision, hardware-sync, frigate, recording, video-eeg-sync]
created: 2026-07-27
status: open
---

# Video-EEG Sync — The Recording Toggle Is Not Sync-Capable

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Today's short export was not a bug in our software. Frigate DELETES the last 10 to 20 seconds of video every single time recording is switched off, on purpose, in its own source code. That led to a bigger realization: switching Frigate recording on and off cannot ever give us frame-accurate alignment between video and EEG, no matter how precise the trigger is. The planned hardware sync upgrade does NOT fix this on its own, because it feeds its sub-millisecond trigger straight back into the same on/off switch.
>
> **What we decided.** The cameras stay a fully independent instrument, recorded manually, never gated by the EEG system. Recording continuously was considered and REJECTED, because it would cost about 455 GB of permanent disk to solve a 14 second problem. Instead the operator starts recording about 30 seconds early and stops about 30 seconds late, so the deleted tail falls in the padding rather than in the data. Real alignment comes later, from sync pulses written into the EEG data stream, and possibly from an infrared LED visible in frame so that the marker survives even if we swap out the recording software.

> [!quote] Paper-ready
> Video acquisition was operator-initiated and independent of the electrophysiology system, with recording started and stopped outside the electrophysiology session boundaries to avoid truncation at the recorder's segment cache. Video-to-electrophysiology alignment was established from transistor-transistor logic (TTL) sync pulses emitted by the Raspberry Pi camera nodes and digitized on the XDAQ digital input at the headstage sampling rate, rendering alignment independent of video container timestamps.

## Constraints (set by Andrea, 2026-07-27) — these are REQUIREMENTS, not preferences

> [!important] The cameras are an INDEPENDENT instrument. Nothing may gate them.
> 1. **Cameras must stay flexible and always ready.** They get moved, re-aimed, switched on and off at will, including with no EEG session running at all.
> 2. **They may be driven by other systems entirely**, not only Frigate and not only this daemon.
> 3. **EEG-session recordings will ALWAYS be started manually**, by a human, even after hardware sync is built.
> 4. **Storage is finite and is not to be spent on idle footage.**
>
> Consequence: any design that makes video capture a slave of the EEG gate, or that assumes Frigate is the recorder, is INVALID regardless of how precise it is. The gate may observe and annotate. It may not control.

## What happened (the trigger for this doc)

Manual recording of `pi_cam_3` on 2026-07-27, started and stopped from the Frigate web interface directly, with no daemon metadata. `/opt/neurosurveillance/logs/session-daemon.log:26255`:

```
15:45:34  External recording state change: pi_cam_3 -> ON  (was OFF)
15:46:07  External recording state change: pi_cam_3 -> OFF (was ON)
15:46:09  Requesting Frigate export: start=1785134734, end=1785134771 (duration=37s)
15:46:19  WARNING: Export ... is short: probed 19.0s of expected 32.6s (58%)
```

Segments that actually reached disk, via `docker exec frigate ls /media/frigate/recordings/2026-07-27/06/pi_cam_3/`:

```
45.23.mp4    45.33.mp4    45.43.mp4     <- nothing after
```

Those cover 45:23 to 45:53. Intersected with the export window 45:34 to 46:11 that is **exactly 19.0 seconds**. The arithmetic closes completely, there is no unexplained residue.

## Root cause (CONFIRMED in Frigate source)

`frigate/record/maintainer.py:250`, inside the container at `/opt/frigate/`:

```python
# Just delete files if recordings are turned off
if (camera not in self.config.cameras
        or not self.config.cameras[camera].record.enabled):
    self.drop_segment(cache_path)   # unlink, NOT moved to disk
    return
```

ffmpeg closes a `/tmp/cache` segment every 10 seconds. The recording maintainer flushes cache to disk only every 5 seconds. Anything still sitting in cache at the instant recording goes disabled is UNLINKED rather than written.

> [!warning] EVERY toggled session PERMANENTLY LOSES 10 TO 20 SECONDS OFF ITS TAIL
> This is not a rounding artifact of segmentation. Segmentation alone would give us MORE footage than requested, not less, because the export would round outward to a segment boundary. The loss is a deliberate delete. It applies to every camera, every session, and has done so for the entire life of the system.

Leading edge is safe. Frigate keeps cache segments that predate the enable, which is why `45.23.mp4` survived even though it starts 11 seconds before the toggle.

The session daemon is NOT at fault here. It exported 2 seconds after the OFF and its ffprobe sanity check caught the shortfall correctly. It simply cannot un-delete files.

## The bigger problem: three independent reasons the toggle can never sync

Tail deletion is only one of three, and fixing it alone would not be enough.

| # | Failure | Magnitude | Calibratable? |
|---|---------|-----------|---------------|
| 1 | Tail deletion on stop (`drop_segment`) | 10 to 20 s | No, data is gone |
| 2 | Start lands on a cache segment boundary, not on the toggle | up to 10 s | **No**, it is uniform random over the segment period, not a fixed offset |
| 3 | Frigate timestamps are packet ARRIVAL at the NVR, not capture instant | tens to hundreds of ms, jittering | No, and it drifts |

Failure 2 is the one people underestimate. Because the offset is random per session rather than constant, you cannot measure it once and subtract it.

Failure 3 survives even if you fix 1 and 2. The clock written into the mp4 reflects when the Real Time Streaming Protocol (RTSP) packet reached the Network Video Recorder (NVR) after Raspberry Pi encode, go2rtc, and the network. On top of that the Pi camera clock free-runs, so nominal 15 frames per second is not exactly 15.000, and the error accumulates across a 12 hour night with nothing in the current stack measuring it.

## The hole in the planned hardware sync

[[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]], Software Integration section, as written before today:

```
EEG_START → Start Frigate recording (same as R_OFF→R_ON)
EEG_STOP  → Stop Frigate recording + export (same as R_ON→R_OFF)
```

> [!warning] WIRE 1 ALONE BUYS TRIGGER LATENCY, NOT SYNCHRONIZATION
> `DO 03` delivers an edge accurate to under 1 millisecond, and the plan then hands that edge to the Message Queuing Telemetry Transport (MQTT) recording toggle, which quantizes it to a ~10 second segment boundary and deletes the tail. The sub-millisecond precision is discarded in the final step. The "Current State vs Planned" table in that same document already claims per-frame alignment and shared-clock drift immunity, which the Software Integration block immediately below it contradicts.

## What actually delivers sync: Wire 2

Wire 2 is Pi GPIO 27 to XDAQ `DI 03`, DB25 pin 2 (`DI 04` to `DI 06` on pins 15, 3, 16 for Pis 2 to 4). Each pulse is digitized into the EEG stream at the headstage sampling rate, so at 20 kHz it lands in the neural timeline with 50 microsecond resolution.

The decisive property: **Wire 2 does not care what Frigate does.** It does not care when the file starts, how the container is timestamped, what the network latency was, or whether recording was toggled at all. Alignment is carried in the EEG data itself.

### Second hole: Wire 2 as currently specced cannot measure drift

[[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]] `gpio_sync.py` emits a pulse only inside the rising-edge and falling-edge branches:

```python
frame_sync_line.set_value(1)
time.sleep(0.001)  # 1 ms pulse
frame_sync_line.set_value(0)
```

That is two pulses per session, one at start and one at stop. [[01-infrastructure/hardware-sync/overview|Overview]] labels this Phase 1, with per-frame 15 Hz pulses as an optional Phase 2.

> [!warning] TWO PULSES PER SESSION GIVES OFFSET BUT LEAVES DRIFT UNRECOVERABLE
> Start and stop markers pin the two endpoints. They tell you nothing about what the camera clock did in between. For a 12 hour sleep run, a camera clock error of only 0.1 percent is about 43 seconds of accumulated skew, and with two pulses you cannot tell whether it accrued linearly, in a step, or not at all. You need a pulse train to recover the drift curve.

## Rejected: continuous recording

> [!failure] REJECTED 2026-07-27 by Andrea. Do not re-propose without new information.
> The first draft of this document recommended leaving `record.enabled` true permanently and treating sessions as export windows. **Rejected on storage grounds and on constraint 1**, and the rejection is correct. It would spend ~455 GB of permanent disk to solve a 14 second problem, and it makes footage exist when nobody asked for it. It was never a sync PREREQUISITE, it was a convenience. Recorded here so the reasoning is not lost.

The load objection raised alongside it does not survive measurement, and the numbers are worth keeping because they will come up again:

| Claim | Verdict | Evidence (2026-07-27) |
|---|---|---|
| Constant load on the **Pi** | **FALSE, zero change** | `rpicam-vid` + go2rtc stream 24/7 regardless; the toggle never reaches the Pi. The Pi is already at full duty cycle. |
| Constant load on the **PC** | **FALSE, near-zero change** | With all 4 cameras at `record.enabled=False`, Frigate was still encoding and writing 10 s segments to `/tmp/cache` and rotating them, then deleting. Container at 5.17 % CPU. |
| Constant **storage** cost | **TRUE** | ~65 GB/day for 4 cameras (1.9 MB per 10 s segment = ~1.5 Mbps/camera). At `retain.days: 7` that is ~455 GB steady state. |

Observed cache rotation with recording OFF everywhere:

```
t=1: 1572912 pi_cam_3@20260727171343+0900.mp4
t=2:  524336 pi_cam_3@20260727171353+0900.mp4
t=3: 1572912 pi_cam_3@20260727171353+0900.mp4
```

So the marginal cost of continuous recording is the difference between `unlink()` and `rename()`, plus retention. It is purely a **storage** decision. Encode, detect, RTSP pull and cache write are already being paid today.

## Decision

### 1. Recording stays MANUAL and camera-independent (per constraints 1 to 3)

No change to how recording is started. A human turns it on. The cameras remain a standalone instrument usable with or without EEG, and usable with recorders other than Frigate.

### 2. The gate ANNOTATES, it never CONTROLS

`DO 03` marks session boundaries into the session journal and can drive an export cut. **It must never start or stop capture.** This was originally argued from precision loss; under constraint 1 it is now a hard requirement independent of precision.

### 3. Operator procedure absorbs the tail loss (no code, no storage)

Because recording is manual anyway, the 10 to 20 second tail deletion is handled by the operator, not by the system:

> [!tip] SOP: start recording ~30 s BEFORE the EEG session, stop it ~30 s AFTER.
> The deleted tail then lands in the trailing pad instead of in the data, and the up-to-10 s random start offset lands in the leading pad. Cost is about 60 seconds of extra footage per session, roughly **6 MB**. This removes failures 1 and 2 for the price of a habit.

What padding does NOT give you is the ability to re-cut later, since footage outside the pad is still gone. Acceptable for planned sessions, which is all of them under constraint 3.

### 4. Wire 2 needs a pulse train, not two pulses (unchanged, still open)

| Option | Drift recoverable? | Cost |
|---|---|---|
| Start/stop only (current spec, Phase 1) | **No** | free |
| Periodic, e.g. 1 pulse per 10 s | Yes, to within one interval | cheap, ~4300 pulses per 12 h |
| Per frame at 15 Hz (Phase 2) | Yes, per frame | ~648k pulses per 12 h per Pi |

Periodic remains the recommendation.

### 5. NEW, raised by constraint 2: the marker must survive a change of recorder

If the cameras may be recorded by other systems, then any sync marker that lives in Frigate metadata, in the session journal, or in Pi-side frame logs is worthless the moment the recorder changes. The marker has to be recoverable from the video ITSELF.

[[01-infrastructure/hardware-sync/literature-review]] line 62 already notes the option and dismisses it:

> Alternative method: LED visible to camera for systems without GPIO input (lower precision)

> [!note] Constraint 2 promotes the in-frame LED from fallback to serious contender
> An LED in the camera's field of view, driven from the same GPIO line that pulses XDAQ `DI 03`, appears in ANY recording, from any software, in any container format, at any time. Precision is bounded by the frame interval, ~67 ms at 15 fps, which is worse than the 50 µs of the digital-input path. But it is the only marker that satisfies constraint 2, and the two are not exclusive: run both, and the LED becomes the recorder-agnostic fallback that also validates the digital path.
>
> NOT yet evaluated. Needs a decision on whether ~67 ms is good enough for the intended analyses, and an infrared LED would be required so as not to disturb sleeping animals.

## Consequences of the decision

Video and EEG stay alignable only to roughly plus or minus 10 seconds until Wire 2 exists, with unmeasured drift on top. With the padding SOP in place the tail loss stops costing data immediately, at no storage cost. That is fine for scoring vigilance states in 4 or 10 second epochs. It remains insufficient for event-locked analysis until the Wire 2 pulse train is built.

## Still open

- **Wire 2 cadence** per the table above. Determines whether drift is recoverable at all. Decide before the listener is written.
- **In-frame LED**, per item 5. New question raised by constraint 2. Infrared, and is ~67 ms adequate?
- Bench validation of Phase 0a, scope on DB25 pin 22, ~$40 bill of materials. Unchanged, still owed.
- Nobody has measured the actual Pi camera clock error, so the 0.1 percent figure used above is illustrative, not measured. The pulse train is what would measure it.
- The padding SOP is not written into any procedure doc yet.

## Related

- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]] — Software Integration section amended 2026-07-27 to match this doc
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]] — Phase 1 drift limitation flagged 2026-07-27
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]
- [[01-infrastructure/session-daemon/architecture|Session Daemon Architecture]]

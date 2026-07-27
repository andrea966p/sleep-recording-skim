---
tags: [decision, hardware-sync, frigate, recording, video-eeg-sync]
created: 2026-07-27
status: open
---

# Video-EEG Sync — The Recording Toggle Is Not Sync-Capable

> [!abstract] TL;DR — for non-technical readers
> Today's short export was not a bug in our software. Frigate DELETES the last 10 to 20 seconds of video every single time recording is switched off, on purpose, in its own source code. That led to a bigger realization: the whole approach of switching Frigate recording on and off cannot ever give us frame-accurate alignment between video and EEG, no matter how precise the trigger is. The planned hardware sync upgrade does NOT fix this on its own, because it feeds its sub-millisecond trigger straight back into the same on/off switch. The fix is to record video continuously and get alignment from sync pulses written into the EEG data stream instead.

> [!quote] Paper-ready
> Video acquisition was run continuously rather than gated on session boundaries, and video-to-electrophysiology alignment was established from transistor-transistor logic (TTL) sync pulses emitted by the Raspberry Pi camera nodes and digitized on the XDAQ digital input at the headstage sampling rate, rendering alignment independent of video container timestamps.

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

## Decision

Three changes, none of them yet implemented.

### 1. Record continuously, stop toggling (PREREQUISITE for sync)

Leave `record.enabled` true at runtime permanently. Sessions become pure export windows carved out of always-present footage. This removes failures 1 and 2 outright, and removes the entire "did video actually record?" class of incidents documented in the recording-toggle fragility notes.

Storage budget, measured 2026-07-27, so this is not hand waving:

| Quantity | Value | Source |
|---|---|---|
| Segment size | 1.9 MB per 10 s | `ls` of the cache segments above |
| Per camera | ~1.5 Mbps | derived |
| 4 cameras | **~65 GB/day** | derived |
| `retain.days` | 7 (already configured, `mode: all`) | `/config/config.yml` |
| 7 day steady state | **~455 GB** | derived |
| Disk free | **1.1 TB** (1.9 TB total, 41 percent used) | `df -h` |

That clears the 200 GB EEG reserve enforced by `storage_monitor.py` with room to spare.

> [!note] This is NOT the forbidden `record.enabled: false`
> The standing rule against setting `record.enabled: false` in the configuration file is untouched, and in fact this change moves further away from it. `/config/config.yml` already has `record.enabled: true` with `retain.days: 7`. The change is to stop the RUNTIME MQTT toggle from flipping it back off.

### 2. Demote the gate from a capture switch to metadata

`DO 03` keeps marking session boundaries, and those boundaries go into the session journal and drive the export cut. It no longer starts or stops capture. If a cut comes out sloppy you re-cut it, because the underlying footage is still on disk.

### 3. Wire 2 needs a pulse train, not two pulses

Decide the cadence before the bench build, because it changes the code and possibly the digital input budget:

| Option | Drift recoverable? | Cost |
|---|---|---|
| Start/stop only (current spec, Phase 1) | **No** | free |
| Periodic, e.g. 1 pulse per 10 s | Yes, to within one interval | cheap, ~4300 pulses per 12 h |
| Per frame at 15 Hz (Phase 2) | Yes, per frame | ~648k pulses per 12 h per Pi |

Periodic is the recommendation. It pins the drift curve at negligible cost, and per-frame can be added later if a specific analysis demands single-frame attribution.

## Consequences if we do nothing

Video and EEG stay alignable only to roughly plus or minus 10 seconds, with an unmeasured drift on top, and every session keeps losing its last 10 to 20 seconds. That is survivable for scoring vigilance states in 4 second or 10 second epochs. It is NOT survivable for anything event-locked, such as aligning video to a specific EEG transient, twitch, or arousal onset.

## Still open

- Bench validation of Phase 0a, scope on DB25 pin 22, ~$40 bill of materials. Unchanged, still owed.
- Wire 2 cadence decision, per the table above. **This is the decision that determines whether drift is recoverable at all**, and it should be made before the listener is written.
- Whether continuous recording is adopted. It is now a sync PREREQUISITE, not just an operational nicety.
- Nobody has measured the actual Pi camera clock error yet, so the 0.1 percent figure above is illustrative, not measured. The pulse train is what would measure it.

## Related

- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]] — Software Integration section amended 2026-07-27 to match this doc
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]] — Phase 1 drift limitation flagged 2026-07-27
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]
- [[01-infrastructure/session-daemon/architecture|Session Daemon Architecture]]

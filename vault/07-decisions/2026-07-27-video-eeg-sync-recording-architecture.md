---
tags: [decision, hardware-sync, frigate, recording, video-eeg-sync]
created: 2026-07-27
status: open
---

# Video-EEG Sync — The Recording Toggle Is Not Sync-Capable

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Today's short export was not a bug in our software. Frigate DELETES the last 10 to 20 seconds of video every single time recording is switched off, on purpose, in its own source code. That led to a bigger realization: switching Frigate recording on and off cannot ever give us frame-accurate alignment between video and EEG, no matter how precise the trigger is. The planned hardware sync upgrade does NOT fix this on its own, because it feeds its sub-millisecond trigger straight back into the same on/off switch.
>
> **What we decided.** Video still starts automatically with the EEG, which is the behaviour we want. The fix is that the daemon must now WAIT about 30 seconds before switching recording off, so the chunk Frigate would have deleted gets written first. Recording continuously was considered and REJECTED: it would cost around 455 GB of permanent disk to solve a 14 second problem.
>
> **How video and brain data get lined up.** Each Raspberry Pi sends an electrical pulse the moment it captures a specific video frame, and that pulse is recorded straight into the brain-signal file. Matching "frame number" to "brain-signal sample number" then needs no clocks at all, just counting on both sides, and the relationship between the two counts directly measures how far the camera clock has drifted. A council of advisors argued we would also need a light blinking inside each chamber; that turned out to be avoidable, because Frigate copies the video without re-encoding it, so no frames are lost in transit. One script still has to confirm that.

> [!quote] Paper-ready
> Video acquisition was operator-initiated and independent of the electrophysiology system, with recording started and stopped outside the electrophysiology session boundaries to avoid truncation at the recorder's segment cache. Video-to-electrophysiology alignment was established from transistor-transistor logic (TTL) sync pulses emitted by the Raspberry Pi camera nodes and digitized on the XDAQ digital input at the headstage sampling rate, rendering alignment independent of video container timestamps.

## Constraints (set by Andrea, 2026-07-27) — these are REQUIREMENTS, not preferences

> [!important] Final constraint set, superseding two earlier drafts in this same document
> 1. **24/7 continuous recording is DEPRECATED and rejected outright.** Storage is finite and it is the root of many downstream problems. Do not re-propose it in any form.
> 2. **Video recording MUST start automatically when EEG recording starts.** The user enters camera and chamber metadata in the web interface beforehand; pressing "start recording" for EEG makes video go along with it. The daemon already supports this via `sessions.auto_start`, currently `false`.
> 3. **Frigate + go2rtc is PERMANENT.** Do not propose swapping the recorder. Recorder-agnostic concerns are out of scope.
> 4. **Cameras must remain independently usable at will** (moved, re-aimed, switched on and off) when no EEG session is running.

> [!history] Two constraints in earlier drafts of this doc were WRONG and are retracted
> An earlier revision recorded "cameras may be driven by other systems entirely" and "EEG-session recordings will ALWAYS be started manually." Both were my misreading, corrected by Andrea 2026-07-27. Frigate is permanent, and auto-start on EEG start is the DESIRED behaviour, not something to be avoided. The recorder-agnostic argument that followed from the first of those (which promoted an in-frame LED to a requirement) collapses with it. Kept visible because the LED question survives on completely different grounds, see the council verdict below.

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
| 2 | ~~Start lands on a cache segment boundary~~ | up to 10 s | **NOT A FAILURE — see correction** |
| 3 | Frigate timestamps are packet ARRIVAL at the NVR, not capture instant | tens to hundreds of ms, jittering | No, and it drifts |

> [!check] Correction: "failure" 2 is FREE MARGIN, not a loss
> An earlier revision listed the start-side segment boundary as a second data-loss failure. That is wrong, and measurement settled it: enabling recording RETAINS cache segments that predate the enable. Recording was enabled at 45:34 and segment `45.23.mp4`, starting 11 s earlier, was written and kept. **Enabling gives you MORE footage than requested, never less.** The export cut trims the surplus. Only the STOP side loses data.

Failure 3 survives even if you fix 1 and 2. The clock written into the mp4 reflects when the Real Time Streaming Protocol (RTSP) packet reached the Network Video Recorder (NVR) after Raspberry Pi encode, go2rtc, and the network. On top of that the Pi camera clock free-runs, so nominal 15 frames per second is not exactly 15.000, and the error accumulates across a 12 hour night with nothing in the current stack measuring it.

## The hole in the planned hardware sync

[[overview|Hardware Sync Overview]], Software Integration section, as written before today:

```
EEG_START → Start Frigate recording (same as R_OFF→R_ON)
EEG_STOP  → Stop Frigate recording + export (same as R_ON→R_OFF)
```

> [!warning] WIRE 1 ALONE BUYS TRIGGER LATENCY, NOT SYNCHRONIZATION
> `DO 03` delivers an edge accurate to under 1 millisecond, and the plan then hands that edge to the Message Queuing Telemetry Transport (MQTT) recording toggle, which quantizes it to a ~10 second segment boundary and deletes the tail. The sub-millisecond precision is discarded in the final step. The "Current State vs Planned" table in that same document already claims per-frame alignment and shared-clock drift immunity, which the Software Integration block immediately below it contradicts.

## Wire 2 — necessary but NOT sufficient on its own

> [!warning] SUPERSEDED by the council round. This section was headed "What actually delivers sync: Wire 2" and that claim was WRONG.
> Wire 2 alone is CIRCULAR: the pulse leaves the Pi GPIO and is digitized by the XDAQ, so both ends sit in the XDAQ clock and nothing ever touches the camera's sensor clock. See the council section below. The resolution is to fire the pulse from the camera's FRAME-CAPTURE CALLBACK, which ties it to a specific frame rather than to a moment in the Pi's CPU clock. Wire 2 remains essential; it just needed that one change to mean anything.

Wire 2 is Pi GPIO 27 to XDAQ `DI 03`, DB25 pin 2 (`DI 04` to `DI 06` on pins 15, 3, 16 for Pis 2 to 4). Each pulse is digitized into the EEG stream at the headstage sampling rate, so at 20 kHz it lands in the neural timeline with 50 microsecond resolution.

The decisive property: **Wire 2 does not care what Frigate does.** It does not care when the file starts, how the container is timestamped, what the network latency was, or whether recording was toggled at all. Alignment is carried in the EEG data itself.

### Second hole: Wire 2 as currently specced cannot measure drift

[[gpio-sync-service|GPIO Sync Service]] `gpio_sync.py` emits a pulse only inside the rising-edge and falling-edge branches:

```python
frame_sync_line.set_value(1)
time.sleep(0.001)  # 1 ms pulse
frame_sync_line.set_value(0)
```

That is two pulses per session, one at start and one at stop. [[overview|Overview]] labels this Phase 1, with per-frame 15 Hz pulses as an optional Phase 2.

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

## The recording pipeline, as actually configured (measured 2026-07-27)

Everything below depends on these flags. They were read off the live `ffmpeg` process, not assumed.

Pi side, `/opt/go2rtc/go2rtc.yaml` on Pi2:

```
exec:rpicam-vid -n --codec libav --libav-format mpegts --width 1024 --height 768
  --framerate 15 --bitrate 1500000 --inline --intra 15 --timeout 0 --camera 1
  --level 4.1 --profile high --low-latency --output -
```

NVR side, Frigate's record-role ffmpeg:

```
... -i rtsp://192.168.0.12:8554/pi_cam_3 -f segment -segment_time 10
    -segment_format mp4 -reset_timestamps 1 -strftime 1 -c:v copy ...
    /tmp/cache/pi_cam_3@%Y%m%d%H%M%S%z.mp4
```

Three consequences that decide the whole design:

| Flag | Consequence |
|---|---|
| `rpicam-vid` on the Pi | **Encoding happens at the camera.** Frame timing originates at the sensor, not at the NVR. |
| `-c:v copy` | **Frigate never re-encodes.** Every frame the Pi sent lands in the file untouched, so FRAME COUNT is an exact quantity on both ends. |
| `-reset_timestamps 1` | **PTS is zeroed at every 10 s segment boundary.** PTS is valid only WITHIN a segment. Absolute position across segments must come from cumulative frame counts, never from PTS. |

> [!warning] Do not regress on PTS in this pipeline
> A reviewer in the council round recommended regressing on PTS rather than frame index, which is correct advice in general and WRONG here. `-reset_timestamps 1` makes PTS restart per segment. Use cumulative frame counts.

## Decision (post-council, 2026-07-27)

### 1. Auto-start stays, and is the point

EEG start triggers video start, exactly as Andrea wants. Flip `sessions.auto_start` to `true` when the stop path below is fixed. The leading edge is FREE MARGIN: enabling retains cache segments that predate the enable, so you get up to ~10 s MORE footage than requested, never less. Measured: enabled at 45:34, segment `45.23.mp4` retained.

### 2. Fix the stop path — this is the whole tail bug

`daemon.py:447` disables recording immediately on `R_ON -> R_OFF`, then exports. Worst-case unflushed data is one 10 s segment plus one 5 s flush interval = **15 s**, so:

> [!tip] Drain 30 s before disabling. 2x margin over the 15 s worst case. Do not tune it.

### 3. Fail-ON, never fail-OFF

On SIGTERM or crash, publish NOTHING and leave recording ON.

> [!important] A stuck-ON camera is recoverable. A dropped tail is not.
> The daemon currently publishes OFF to all cameras on SIGTERM, and because the MQTT topic is RETAINED that OFF survives the reboot. This is the failure that made a 72 h run record ZERO video. Deleting the SIGTERM-publishes-OFF path removes the entire class.

### 4. Recording is a refcounted lease, not a boolean

```
enabled = (manual_lease OR session_lease)
```

The daemon never publishes OFF; it RELEASES its lease and publishes the OR. This resolves, in one model:

- constraint 4, manual users become structurally impossible to stomp
- back-to-back sessions, no OFF between them
- the SIGTERM bug, since there is no OFF path to fire

Log any preemption or overlap into the session journal as provenance.

### 5. Alignment uses NO CLOCKS AT ALL — frame N to sample S

This is the council's central correction and it replaces the earlier Wire-2-only plan.

> [!quote] Paper-ready
> Each Raspberry Pi emitted a transistor-transistor logic (TTL) pulse from its camera frame-capture callback, recording the corresponding frame index locally; the pulse was digitized on the XDAQ digital input alongside the neural data at the headstage sampling rate. Video-to-electrophysiology registration was therefore obtained by linear fit of video frame index against electrophysiology sample index, with the fitted slope providing a direct measurement of camera clock drift, and required no reference to system clocks or video container timestamps.

- The Pi pulses **from the frame-capture callback, NOT from a wall-clock timer.** Each pulse then means "frame N exists", and the Pi logs N.
- XDAQ digitizes that pulse at sample S, 50 µs resolution at 20 kHz, INSIDE the neural file.
- Analysis pairs **frame N ↔ sample S** and fits a line. The SLOPE is the measured drift.

No clock appears anywhere in that chain. Not the NVR clock, not RTSP arrival time, not the Pi wall clock. Two counters and a wire.

> [!warning] Pulsing off a timer instead of the capture callback breaks this
> A timer-driven pulse measures the Pi's CPU clock, which nobody cares about. The whole scheme rests on the pulse being tied to a specific FRAME.

**Cadence: 1 pulse per 10 s, plus one double-width pulse every 60 s** as an unambiguous re-anchor after a dropout. Rejected: Manchester coding and full counter codecs, per the Executor, "you will never debug it." Rejected: per-frame 15 Hz, unnecessary once the fit is linear.

**Drift is measured per CAMERA, not per session.** Four to eight sensors free-run independently; a single fit is wrong at n > 1.

### 6. In-frame LED: NOT chamber furniture

The council reached "optical marker or don't publish" because it assumed the video timeline was recoverable only through NVR timestamps. `-c:v copy` breaks that assumption: every frame survives, so frame COUNTING is a valid timeline, and the LED is not fundamental.

> [!failure] Permanent in-chamber LED REJECTED 2026-07-27 by Andrea, on logistics
> Chambers get moved, cleaned, and swapped. An LED in every chamber is hardware to mount, clean around, and keep aligned, multiplied by 4 and later 8 to 32. The logistics cost is real and the benefit is conditional.

The LED survives only as a **one-time bench instrument** to validate the frame-counting method, then it comes out. It is needed permanently ONLY if frames turn out to be dropped between Pi and file, because a marker in the pixels is self-locating whereas a frame count silently shifts.

**That condition is testable for free, with no hardware.** See below.

### 7. Per-session sync manifest

Written automatically at session close: pulse table (frame index, sample index), measured effective fps, fitted drift coefficients, segment boundaries and per-segment frame counts, export window. Without this the mapping exists only as something a person reconstructs later, which is not reproducible and a reviewer can break it.

The per-segment frame counts double as the integrity record: a break becomes DETECTABLE offline rather than silently corrupting the fit.

## Precision budget, stated honestly

| Quantity | Value |
|---|---|
| Scoring epochs | 4 to 10 s |
| Frame interval at 15 fps | 67 ms |
| Alignment needed | ~±0.5 s |
| Achievable via frame ↔ sample fit | one frame, ~67 ms |
| Achievable via timestamps alone (no sync) | ~±10 s plus unmeasured drift |

> [!warning] Video CANNOT support true sub-frame event-locked analysis
> The floor is one frame interval. State this in the methods rather than implying a precision the medium does not have.

## The test that settles the LED question

`neurosurveillance/backend/scripts/frame_integrity_check.py` (written 2026-07-27, not yet run on real data).

Checks two things per segment, straight from the recorded files:

1. **Frame count.** `-segment_time 10` at 15 fps means a healthy segment holds exactly 150 frames. Any deviation is a deficit.
2. **Timestamp gaps.** Packet PTS deltas within a segment should be a constant 1/15 s under `-c:v copy`; a delta over 1.5x nominal means frames vanished from the stream itself.

```bash
python3 frame_integrity_check.py --camera pi_cam_3 --minutes 220
```

Exit codes: `0` clean, `1` drops found, `2` no segments (recording was off), `3` error. All access is via `docker exec frigate`, so **no sudo**, and it is **READ-ONLY** (`ls` and `ffprobe` only), therefore safe to run during a live recording.

> [!note] Run it over a REAL multi-hour session, ideally one spanning a Pi wobble
> RTSP reconnects are the plausible drop source, so a short clean window proves nothing. The script refuses to give a firm verdict under 30 minutes for this reason. Run it across all four cameras.
>
> **Clean over hours → frame counting is sound, LED permanently off the table.**
> **Any deficit → per-segment frame counts in the manifest, or the LED comes back.**

First run 2026-07-27 covered only the 20 s of footage that existed and returned CLEAN but flagged PROVISIONAL. That is a smoke test of the tool, not evidence about the pipeline.

## RESULT: 14.97 h overnight run, 2026-07-27/28 — the LED question is SETTLED

`pi_cam_2`, 18:19:13 to 09:17:14, 14.97 h, 10.5 GB exported, export completed in 40 s, no errors.

```
Segments analysed : 5388 complete
Total frames      : 808365
Wall span         : 53880s
Effective fps     : 15.0031

    150 frames : 5377 segments  <-- EXPECTED
    165 frames :   11 segments  <-- LONG (+15 frames, keyframe-boundary cut, harmless)

VERDICT: NO FRAME LOSS.
No short segments, no timestamp gaps, across 5388 segments.
```

> [!check] ZERO frames lost across 15 hours. Frame counting IS a valid timeline.
> The 11 deviant segments are LONG, not short: 165 frames = 11 s, exactly one extra GOP given `--intra 15` (one keyframe per second). That is the segment muxer cutting on a later keyframe, which re-partitions frames without losing any. No PTS gaps anywhere. The export's own `nb_frames` is 808365, matching the segment total exactly, so nothing was lost in the export step either.
>
> **The in-frame LED is therefore PERMANENTLY off the table**, on evidence rather than argument. The frame N ↔ sample S pairing will hold.

> [!bug] The script's first verdict was WRONG and was fixed before this result was accepted
> It computed a single net deficit as `sum(expected - actual)`, which went negative on a surplus and printed "FRAMES ARE BEING LOST". Worse, netting meant 11 long segments could have cancelled 11 genuinely short ones and read as clean. Corrected so only SHORT segments and PTS gaps count as loss, and long segments are reported separately as a harmless muxer artifact.

### First real measurement of camera clock drift

```
Camera vs NVR wall clock: +204 ppm (+8.8s over 12h)
```

808365 frames delivered over 53880 s of wall time is **15.0031 fps, not 15.000**. The camera runs FAST.

> [!warning] +8.8 SECONDS PER 12 HOUR NIGHT, roughly 18x over the ±0.5 s alignment budget
> Every drift figure written in this vault before now used an illustrative 0.1 percent. **This one is measured.** It confirms that drift correction is not a refinement, it is the whole requirement: without the pulse train, a night's video and EEG end the session nearly nine seconds apart, which is one to two entire scoring epochs.

Caveats, both in the script's own output: the figure absorbs any NVR clock error, and the span is quantised to whole seconds by the segment filenames (±37 ppm over this window). It is a calibrated preview, not the final number. The real quantity is camera versus XDAQ sample clock, and only Wire 2 can measure that.

### Tail loss recurred exactly as predicted

Last segment on disk starts `00:16:58` UTC; OFF was published `00:17:14`. Export container duration 53875 s against 53886 s requested, so **~11 s lost**, inside the predicted 10 to 20 s band.

That is 99.98 percent of the window, so the daemon's `<0.95x` sanity check never fired.

> [!important] The loss is a FIXED 10 to 20 s regardless of session length
> It is invisible on a 15 h run and catastrophic on a 37 s one. Do not let the clean-looking percentage on long sessions argue against fixing `daemon.py:447`.

## Council round, 2026-07-27

Five advisors independently, then three anonymized peer reviews, then synthesis. Convened before any wiring, at Andrea's request, to check the concept was solid.

**Unanimous, and the central finding:** the original Wire-2-only plan was **circular**. The pulse leaves the Pi GPIO and is digitized by the XDAQ; both ends live in the XDAQ clock. Nothing in that path ever touches the camera's sensor clock, which is the clock that actually drifts. It would have produced beautifully drift-corrected markers with no defensible relationship to any video frame, leaving the alignment floor at RTSP arrival jitter of roughly ±200 ms regardless of pulse count.

The council's fix was an optical marker. **The accepted fix instead is pulsing from the frame-capture callback**, per decision item 5, which supplies the missing link (a specific FRAME, rather than a moment in the Pi's CPU clock) without any hardware in the chamber. The council did not have the `-c:v copy` and `-reset_timestamps 1` flags in front of it.

Also unanimous, and adopted: fail-ON over fail-OFF, refcounted leases over booleans, drain before disable, per-camera rather than per-session drift fits, and the priority ordering that the free daemon fixes vastly outrank the ~$40 bill of materials, because the one-line stop bug and the retained-OFF class destroyed 72 h and 23 h of recordings while the tail costs 20 s.

**Rejected from the council:** a Manchester-coded counter with session-ID preamble (over-engineered, undebuggable, and all three reviewers named it the weakest response); an exclusive EEG lease that preempts manual recording (violates constraint 4; the OR-lease is correct).

> [!bug] The council proposed something physically impossible and no reviewer caught it
> Two advisors recommended a fixed **60 s pre-roll** before each session. On the auto-start path the EEG start IS the trigger, so the daemon cannot begin recording 60 s before an event it has not yet observed. **The lag is controllable; the lead is not.** The only lead available is the ~10 s of accidental cache overshoot, which is free but not extensible. Do not design around a pre-roll that cannot exist.

Open questions the reviewers raised that remain unresolved and are recorded here so they are not lost, even though the LED is now out of scope: whether the Pi camera modules are NoIR or carry an IR-cut filter (would gate any future optical work), whether a blinking marker would inflate Frigate's motion detection and bitrate, whether Frigate retention could prune a pre-roll before export runs, and the observation that **NTP/chrony discipline on the Pis and NVR is unmentioned anywhere in this vault** and is free.

## Consequences of the decision

Until the pulse train exists, video and EEG stay alignable only to roughly ±10 s with unmeasured drift on top. Fixing the stop path (items 2 to 4) stops the tail loss immediately at zero storage cost and removes the silent-no-capture class, independently of any wiring. Once the pulse train exists, alignment reaches one frame, ~67 ms, which covers 4 to 10 s epoch scoring with wide margin and still will not support sub-frame event-locked work.

## Still open

- ✅ **DONE 2026-07-28: `frame_integrity_check.py` over the 14.97 h overnight run. ZERO frame loss across 5388 segments → LED permanently rejected, frame counting confirmed valid.** Still worth repeating on `pi_cam_0/1/3` and on a run that spans a Pi wobble, since RTSP reconnects remain the plausible drop source and Pi1 was down during this one.
- 🆕 **Drift is MEASURED and it is big: +204 ppm, +8.8 s per 12 h, ~18x over the ±0.5 s budget.** Confirms the pulse train is mandatory, not a refinement.
- ✅ **DONE 2026-07-28 (code written + unit tested, NOT DEPLOYED): the daemon stop-path fix.** Lease model in `frigate_controller.py` (`acquire_lease`/`release_lease`/`adopt_lease`), 30 s drain before the last release, fail-ON at shutdown, non-stomping startup. 12/12 behavioural tests pass in `backend/tests/test_recording_leases.py`. Journal: [[04-journal/2026-07/2026-07-28]].
- ⏳ **DEPLOY that fix** — copy to `/opt/neurosurveillance/` and restart the service. Until then production still has the bug.
- **Flip `sessions.auto_start` to `true`** once the fix is DEPLOYED. Not before, or you auto-start into the same stop bug.
- Bench validation of Phase 0a, scope on DB25 pin 22, ~$40 bill of materials. Unchanged, still owed.
- ~~Nobody has measured the actual camera clock drift.~~ **Measured 2026-07-28: +204 ppm vs the NVR clock, +8.8 s per 12 h.** Illustrative 0.1 percent figures elsewhere in this document predate that and should be read as placeholders. Camera vs XDAQ still needs Wire 2.
- **Is +204 ppm stable or does it wander?** A single fit over one night cannot tell a constant rate offset (trivially correctable with one slope) from a temperature-dependent wander (needs the dense pulse train to track). This matters for how often the fit must be re-estimated.
- **Per-camera drift spread is unknown.** Only `pi_cam_2` has been measured. If the four sensors differ materially, that settles the per-camera-fit requirement with data.
- NTP/chrony discipline on Pis and NVR, raised in peer review, never addressed.
- `pi_cam_2` did not appear in `/tmp/cache` across several samples on 2026-07-27 while `pi_cam_3` did, despite both having the `record` role and Pi2 responding to ping. Unexplained, unrelated to this decision, worth a look.

## Related

- [[overview|Hardware Sync Overview]] — Software Integration section amended 2026-07-27 to match this doc
- [[gpio-sync-service|GPIO Sync Service]] — pulse cadence and capture-callback requirement amended 2026-07-27
- [[wiring-guide|Wiring Guide]]
- [[literature-review|Literature Review]] — line 62 notes the in-frame LED option
- [[architecture|Session Daemon Architecture]]
- `neurosurveillance/backend/scripts/frame_integrity_check.py` — the test that gates the LED question

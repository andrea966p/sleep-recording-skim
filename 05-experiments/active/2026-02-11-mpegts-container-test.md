---
tags: [experiment]
date: 2026-02-11
status: planned
subjects:
chambers:
---

# MPEG-TS Container Format Test

## Overview

- **Hypothesis:** Using `--libav-format mpegts` instead of `h264` will improve stream robustness (better framing, timestamping, and recovery from partial reads)
- **Prerequisite:** v5.1 golden config changes (`--low-latency`, `--intra 15`, `-n`) must be deployed and stable for 24h+ before running this test

## Background

The RPi camera documentation recommends MPEG-TS for streaming:

> "Support for unencapsulated H.264 can generally be quite poor so it is often better to send an MPEG-2 Transport Stream instead."

The official go2rtc + Pi 5 example in the RPi docs uses `--libav-format mpegts`:

```yaml
streams:
  cam:
    - exec:rpicam-vid -n -t 0 --width 1280 --height 720 --codec libav --libav-format mpegts --low-latency -o -
```

go2rtc's exec pipe transport supports MPEG-TS natively.

The current production config uses `--libav-format h264` (raw H.264 bitstream), which works but lacks container-level framing and timestamps.

## Protocol

### Test Configuration

Change only the `--libav-format` parameter:

```yaml
# Current (production):
pi_cam_0: "exec:rpicam-vid -n --codec libav --libav-format h264 ... --output -"

# Test:
pi_cam_0: "exec:rpicam-vid -n --codec libav --libav-format mpegts ... --output -"
```

### Test Steps

1. Record baseline metrics with current `h264` format (CPU, memory, temperature, stream latency)
2. Switch **one camera only** (`pi_cam_0`) to `mpegts`
3. Monitor for 2 hours:
   - Stream playback in Frigate UI
   - `journalctl -u go2rtc.service -f` for errors
   - CPU/memory usage comparison
   - Stream startup time (how fast does Frigate pick up the stream after go2rtc restart?)
4. If stable, switch both cameras to `mpegts`
5. Monitor for 24 hours

### Success Criteria

- [ ] Both streams play correctly in Frigate UI
- [ ] No increase in CPU usage (>5% delta)
- [ ] No stream disconnections
- [ ] Stream startup time equal or faster than `h264`
- [ ] Recordings save correctly (verify playback of recorded segments)

### Failure Criteria

- Stream fails to play in Frigate
- go2rtc logs show parsing errors
- CPU usage increases significantly
- Recording corruption

## Recording Setup

No changes to Frigate config needed -- Frigate receives RTSP from go2rtc regardless of the underlying pipe format.

## Baseline Metrics

**Captured: 2026-02-19, h264 format, both cameras active**

| Metric | Value |
|--------|-------|
| Pi temperature | 48.8°C |
| Pi throttled | `0x0` (none) |
| Pi memory used | 460 MB / 8062 MB |
| Pi load avg (1/5/15m) | 0.36 / 0.55 / 0.50 |
| rpicam-vid cam 0 CPU | ~17% |
| rpicam-vid cam 1 CPU | ~17% |
| Frigate cam 0 fps | 5.1 fps |
| Frigate cam 1 fps | 5.0 fps |
| Frigate ffmpeg CPU (QSV) | 2.5–2.6% per camera |
| Stream startup time | (not yet measured) |
| Frigate recording playback | working |

## Results

### Phase 2 — cam 0 switched to mpegts (2026-02-19 07:43 UTC)

**Config change:** `pi_cam_0` only: `--libav-format h264` → `--libav-format mpegts`
**pi_cam_1** left on `h264` as comparison.

**go2rtc streams API confirms:**
- `pi_cam_0`: `format_name: mpegts`, producing `H264` video — Frigate connected via RTSP+TCP ✓
- `pi_cam_1`: `format_name: h264`, producing `H264` video — Frigate connected via RTSP+TCP ✓

**Post-switch metrics (07:45 UTC, ~2 min after go2rtc started serving streams):**

| Metric | Baseline (h264 both) | Post-switch (cam0=mpegts, cam1=h264) | Delta |
|--------|---------------------|--------------------------------------|-------|
| Pi temperature | 48.8°C | 49.4°C | +0.6°C |
| Pi throttled | `0x0` | `0x0` | none |
| Pi memory used | 460 MB | 438 MB | -22 MB |
| Pi load avg (1m) | 0.36 | 0.48 | +0.12 |
| rpicam-vid cam 0 CPU | ~17% | ~16.6% | -0.4% |
| rpicam-vid cam 1 CPU | ~17% | ~16.8% | -0.2% |
| Frigate cam 0 fps | 5.1 fps | 5.1 fps | 0 |
| Frigate cam 1 fps | 5.0 fps | 5.1 fps | +0.1 |
| Frigate ffmpeg CPU | 2.5–2.6% | 2.2–2.3% | -0.2–0.3% |

**Journal:** Zero errors, zero warnings after restart. Clean startup.

**go2rtc startup time:** ExecStartPre 60s + ~1s startup = ~61s to serving streams.

### Phase 3 — 2h monitoring window (cam 0 mpegts, cam 1 h264)

**Window: 2026-02-19 07:45 UTC → 09:28 UTC (~1h43m active recording)**

**Frigate logs (relevant entries only):**
- `16:47 KST` — `Turning on recordings for pi_cam_0` (user-initiated) ✓
- `17:27 KST` — `Turning off recordings for pi_cam_0` (user-initiated) ✓
- `17:28 KST` — Export error: `Invalid duration for option ss: 00:-43:27` — **Frigate bug with preview clip negative timestamp, unrelated to mpegts**
- `17:28, 17:30 KST` — `No motion data found` — expected, detection is disabled
- go2rtc journal: **zero errors, zero warnings** throughout

**Recording files:** 245 × 10-second mp4 segments for pi_cam_0, clean
- Path inside container: `/media/frigate/recordings/2026-02-19/HH/pi_cam_0/MM.SS.mp4`
- Segment integrity (ffprobe): `duration=9.997982s`, `size=2186614 bytes`, `nb_streams=1` ✓
- Export playback: **confirmed good** by user

**End-of-Phase 3 Pi metrics:**

| Metric | Baseline | Phase 3 end | Delta |
|--------|----------|-------------|-------|
| Pi temperature | 48.8°C | 48.8°C | 0 |
| Pi throttled | `0x0` | `0x0` | none |
| Pi memory used | 460 MB | 446 MB | -14 MB |
| Pi load avg (1m) | 0.36 | 0.32 | -0.04 |
| rpicam-vid cam 0 CPU | ~17% | ~16.6% | -0.4% |
| rpicam-vid cam 1 CPU | ~17% | ~16.7% | -0.3% |
| Frigate cam 0 fps | 5.1 fps | 5.1 fps | 0 |
| Frigate ffmpeg CPU | 2.5–2.6% | 2.1–2.2% | -0.3–0.4% |

**Phase 3 verdict: PASS** — proceeding to Phase 4 (both cameras mpegts)

## Decision

- [ ] **Adopt mpegts** -- update golden config to v5.2
- [ ] **Keep h264** -- document why mpegts didn't improve things
- [ ] **Needs more testing** -- specify what

## Notes

- Do NOT run this until v5.1 changes are deployed and stable for at least 24 hours
- Rollback is simple: change `mpegts` back to `h264` and restart go2rtc

## Related

- [[01-infrastructure/raspberry-pi/golden-go2rtc-config|Golden go2rtc Config]]
- [[06-references/video-parameters|Video Parameters]]

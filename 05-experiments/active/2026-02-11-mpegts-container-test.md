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

- [ ] Pi CPU usage: __%
- [ ] Pi memory usage: __MB
- [ ] Pi temperature: __C
- [ ] Stream startup time: __s
- [ ] Frigate recording playback: working/broken

## Results

<!-- Fill after testing -->

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

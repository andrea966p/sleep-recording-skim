---
tags: [experiment, completed, failure]
date: 2026-02-05
status: completed
outcome: failure
---

## Overview

- **Hypothesis:** H.265 encoding will reduce storage by 50% with minimal performance impact
- **Outcome:** FAILURE - Critical system instability

## Configuration Tested

```yaml
streams:
  pi_cam_0:
    - exec:rpicam-vid --camera 0 -t 0 --width 1280 --height 720 --framerate 30 --codec h265 -o -
  pi_cam_1:
    - exec:rpicam-vid --camera 1 -t 0 --width 1280 --height 720 --framerate 30 --codec h265 -o -
```

## Results

- Initial encoding worked for ~15 minutes
- System became unresponsive
- Required hard reboot
- Multiple kernel panics in dmesg
- rpicam-vid process consuming 90%+ CPU

## Error Log

```
Kernel panic: Out of memory
rpicam-vid process consuming 90%+ CPU
```

## Key Learning

**H.265 hardware encoding on Pi 5 is unstable and causes resource exhaustion.**

The libav wrapper for H.264 MUST be used for production stability.

## Recommendation

**NEVER use H.265 codec on Raspberry Pi 5 for this system.**

Use only:
```
--codec libav --libav-format h264
```

## Related

- [[../../01-infrastructure/raspberry-pi/golden-go2rtc-config|Golden go2rtc Config]]
- [[../../06-references/video-parameters|Video Parameters]]

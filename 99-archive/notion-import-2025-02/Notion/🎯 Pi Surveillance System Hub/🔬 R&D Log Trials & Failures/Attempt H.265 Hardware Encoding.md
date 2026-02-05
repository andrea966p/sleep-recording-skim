---
base: "[[🔬 R&D Log Trials & Failures.base]]"
Impact: 🔥 Critical Failure
Hypothesis: H.265 encoding will reduce storage by 50% with minimal performance impact
Outcome: ❌ FAILURE
Key Error Log: "Kernel panic: Out of memory, rpicam-vid process consuming 90%+ CPU"
Conclusion & Learning: H.265 hardware encoding on Pi 5 is unstable and causes resource exhaustion. The libav wrapper for H.264 must be used for production stability.
Configuration Changes: Modified go2rtc.yaml to use --codec h265 instead of --codec libav --libav-format h264
---
**Detailed Documentation:**

Attempted to implement H.265 encoding to reduce storage requirements by approximately 50% while maintaining video quality.

**Configuration Applied:**

```yaml
# Modified go2rtc.yaml
streams:
  pi5_1_cam0:
    - exec:rpicam-vid --camera 0 -t 0 --width 1280 --height 720 --framerate 30 --codec h265 -o -
  pi5_1_cam1:
    - exec:rpicam-vid --camera 1 -t 0 --width 1280 --height 720 --framerate 30 --codec h265 -o -
```

**Results:**

- Initial encoding worked for ~15 minutes
- System became unresponsive
- Required hard reboot
- Multiple kernel panics in dmesg

**Key Learning:**

H.265 hardware encoding on Pi 5 is unstable and causes resource exhaustion. The libav wrapper for H.264 must be used for production stability.
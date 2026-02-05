---
base: "[[🔬 R&D Log Trials & Failures.base]]"
Impact: 📊 Performance Impact
Hypothesis: Single camera motion detection will provide useful alerts without significant performance impact
Outcome: ✅ SUCCESS
Key Error Log: None - successful test
Conclusion & Learning: Motion detection is viable for single camera monitoring with acceptable performance impact. Could be useful for lab security.
Configuration Changes: Enabled detect in Frigate config.yml for one camera with reduced resolution
---
**Detailed Documentation:**

Tested enabling Frigate's motion detection on a single camera to evaluate system impact and usefulness for lab monitoring.

**Configuration Applied:**

```yaml
# Modified config.yml
detect:
  enabled: true
  width: 640
  height: 360
  fps: 5

cameras:
  pi5_1_cam0:
    detect:
      enabled: true
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/pi5_1_cam0
          roles:
            - detect
            - record
```

**Results:**

- Motion detection worked as expected
- CPU usage increased by ~15% on Frigate server
- Generated useful alerts for lab activity
- No system instability observed over 72-hour test

**Key Learning:**

Motion detection is viable for single camera monitoring with acceptable performance impact. Could be useful for lab security.
---
type: incident
area: video-nvr
status: active
tags: [troubleshooting, symptom, frigate]
created: 2026-02-05
severity: critical
---

## Description

Frigate dashboard shows "No frames received" for one or both camera streams.

## Quick Diagnosis

```bash
# On Pi - Check service
sudo systemctl status go2rtc.service

# Check camera processes (should be 2)
ps aux | grep rpicam-vid | grep -v grep | wc -l

# Check temperature
vcgencmd measure_temp

# Test RTSP stream
ffprobe rtsp://192.168.0.11:8554/pi_cam_0
```

## Common Causes

| Cause | Likelihood | Check |
|-------|------------|-------|
| go2rtc service stopped | High | `systemctl status go2rtc` |
| rpicam-vid crashed | High | `ps aux \| grep rpicam-vid` |
| Camera disconnected | Medium | `rpicam-hello --list-cameras` |
| Network issue | Medium | `ping 192.168.0.11` |
| Camera overheating | Low | `vcgencmd measure_temp` |

## Solutions

### If go2rtc stopped:
```bash
sudo systemctl restart go2rtc.service
```

### If camera processes missing:
```bash
# Check hardware
rpicam-hello --list-cameras

# Restart service
sudo systemctl restart go2rtc.service
```

### If network issue:
```bash
# Check connectivity from NVR
ping 192.168.0.11
curl http://192.168.0.11:1984/api/streams
```

## Prevention

- Enable [[watchdog-monitoring|watchdog monitoring]]
- Use TCP transport in Frigate config
- Check logs regularly: `journalctl -u go2rtc.service -f`

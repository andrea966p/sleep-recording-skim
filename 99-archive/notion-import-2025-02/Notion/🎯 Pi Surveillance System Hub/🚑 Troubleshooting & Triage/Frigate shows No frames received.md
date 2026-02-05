---
base: "[[🚑 Troubleshooting & Triage.base]]"
Solution Notes: Restart go2rtc service - usually resolves camera process issues
Priority: 🔥 Critical
System: Raspberry Pi
Status: 🟢 Solved
---
## 😨 Initial Observation

Frigate dashboard shows "No frames received" for one or both camera streams.

## 🩺 First-Level Diagnostics

- [ ] Check Pi Status: `sudo systemctl status go2rtc.service`
- [ ] Check Camera Processes: `ps aux | grep rpicam-vid | grep -v grep | wc -l` (Should be 2)
- [ ] Check Frigate Logs: `docker logs frigate --tail 50`
- [ ] Check Monitor Log: `tail -20 /var/log/pi-monitor.log`
- [ ] Test direct RTSP: `ffprobe rtsp://192.168.0.11:8554/pi5_1_cam0`

## 🧠 Known Causes

- Pi camera hardware disconnected
- rpicam-vid process crashed
- go2rtc service stopped
- Network connectivity issues
- Camera module overheating

## ✅ Solution

```bash
# Restart go2rtc service
sudo systemctl restart go2rtc.service

# If that fails, check camera hardware
rpicam-hello --list-cameras

# Verify camera processes
ps aux | grep rpicam-vid

# Check system temperature
vcgencmd measure_temp
```
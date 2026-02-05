---
tags: [reference, commands, cheatsheet]
created: 2026-02-05
---

## Raspberry Pi Commands

### Health Checks
```bash
vcgencmd measure_temp          # Temperature
vcgencmd get_throttled         # Throttling (0x0 = OK)
free -h                        # Memory usage
rpicam-hello --list-cameras    # Camera hardware
```

### Service Management
```bash
sudo systemctl status go2rtc.service
sudo systemctl restart go2rtc.service
sudo systemctl stop go2rtc.service
journalctl -u go2rtc.service -f    # Live logs
journalctl -u go2rtc.service -n 50 # Last 50 lines
```

### Process Monitoring
```bash
# Camera processes (should be 2)
ps aux | grep rpicam-vid | grep -v grep | wc -l

# Kill stuck processes
sudo pkill rpicam-vid
```

### Network Testing
```bash
# Test RTSP locally
ffprobe rtsp://localhost:8554/pi_cam_0

# Test go2rtc API
curl -s http://localhost:1984/api/streams
```

---

## Frigate Server Commands

### Container Management
```bash
docker compose up -d           # Start
docker compose down            # Stop
docker compose restart frigate # Restart
docker ps -a                   # List containers
```

### Logs & Monitoring
```bash
docker compose logs -f frigate     # Live logs
docker logs frigate --tail 100     # Last 100 lines
docker stats frigate               # Resource usage
```

### Storage
```bash
df -h                                    # Disk usage
du -sh /srv/frigate/storage/             # Recordings size

# Clean old recordings (>7 days)
find /srv/frigate/storage/recordings/ -name "*.mp4" -mtime +7 -delete
```

---

## Quick Diagnostics

### Pi Health Check (one-liner)
```bash
echo "Temp: $(vcgencmd measure_temp) | Throttle: $(vcgencmd get_throttled) | Cams: $(ps aux | grep rpicam-vid | grep -v grep | wc -l)/2"
```

### Full System Validation
```bash
# Test everything
ping -c1 192.168.0.11 && \
ffprobe -v error rtsp://192.168.0.11:8554/pi_cam_0 && \
curl -sf http://192.168.0.50:5000/api/stats && \
echo "ALL OK"
```

---

## Emergency Procedures

### Pi Emergency Restart
```bash
sudo systemctl stop go2rtc
sudo pkill -9 rpicam-vid
sudo systemctl start go2rtc
```

### Frigate Emergency Restart
```bash
docker compose down
docker compose up -d
```

### Full System Recovery
```bash
# On Pi:
sudo systemctl stop go2rtc
sudo pkill -9 rpicam-vid go2rtc ffmpeg
sudo systemctl daemon-reload
sudo systemctl start go2rtc

# On NVR:
docker compose down && docker compose up -d
```

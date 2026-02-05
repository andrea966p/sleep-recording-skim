---

---
# Asset Library & Command Reference 🧰

*Your quick-reference cheat sheet for all system commands, configurations, and procedures*

---

## 📁 **Key Configuration Files**

▶️ **Production go2rtc.yaml**

```yaml
# /etc/go2rtc.yaml - STABLE PRODUCTION CONFIG v4.0
streams:
  camera0:
    - exec:/usr/bin/rpicam-vid --camera 0 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format mpegts --libav-audio 0 --flush -o -
    - ffmpeg:rtsp
  camera1:
    - exec:/usr/bin/rpicam-vid --camera 1 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format mpegts --libav-audio 0 --flush -o -
    - ffmpeg:rtsp

api:
  listen: ":1984"
```

▶️ **Production Frigate config.yml**

```yaml
# config.yml - BATTLE TESTED
mqtt:
  enabled: false

database:
  path: /media/frigate/frigate.db

detect:
  enabled: false

record:
  enabled: true
  retain:
    days: 30
    mode: all

cameras:
  pi_cam_0:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/camera0
          input_args:
            - -rtsp_transport
            - tcp
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
            - -reconnect
            - "1"
            - -reconnect_at_eof
            - "1"
            - -reconnect_streamed
            - "1"
          roles: [record, rtmp]
    record:
      enabled: true
    detect:
      enabled: false
      
  pi_cam_1:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/camera1
          input_args:
            - -rtsp_transport
            - tcp
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
            - -reconnect
            - "1"
            - -reconnect_at_eof
            - "1"
            - -reconnect_streamed
            - "1"
          roles: [record, rtmp]
    record:
      enabled: true
    detect:
      enabled: false
```

▶️ **Production docker-compose.yml**

```yaml
version: "3.9"
services:
  frigate:
    container_name: frigate
    restart: unless-stopped
    image: ghcr.io/blakeblackshear/frigate:stable
    privileged: true
    shm_size: "64mb"
    
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./config:/config
      - ./storage:/media/frigate
      - type: tmpfs
        target: /tmp/cache
        tmpfs:
          size: 1000000000
    
    ports:
      - "5000:5000"
      - "8554:8554"
      - "8555:8555/tcp"
      - "8555:8555/udp"
    
    environment:
      - TZ=Asia/Seoul
```

---

## 🐧 **Raspberry Pi Commands**

▶️ **Health Checks**

```bash
# System temperature
vcgencmd measure_temp

# Throttling status (should return 0x0)
vcgencmd get_throttled

# Memory usage
free -h

# System performance
htop

# Check camera hardware check
rpicam-hello --list-cameras
```

▶️ **Service Management**

```bash
# Check service status
sudo systemctl status go2rtc.service

# Start/stop/restart service
sudo systemctl start go2rtc.service
sudo systemctl stop go2rtc.service
sudo systemctl restart go2rtc.service

# Enable/disable service
sudo systemctl enable go2rtc.service
sudo systemctl disable go2rtc.service
```

▶️ **Log Viewing**

```bash
# Real-time service logs
journalctl -u go2rtc.service -f

# Last 50 log entries
journalctl -u go2rtc.service -n 50

# System log
tail -f /var/log/syslog

# Monitor script log (if implemented)
tail -f /var/log/pi-monitor.log
```

▶️ **Process Monitoring**

```bash
# Check camera processes (should be 2)
ps aux | grep rpicam-vid | grep -v grep | wc -l

# View camera processes
ps aux | grep rpicam-vid | grep -v grep

# Kill stuck camera processes
sudo pkill rpicam-vid
```

▶️ **Network Testing**

```bash
# Test RTSP stream locally
ffprobe rtsp://localhost:8554/camera0
ffprobe rtsp://localhost:8554/camera1

# Test go2rtc API
curl -s http://localhost:1984/api/streams

# Check network connectivity to Frigate
ping -c 3 192.168.0.50
telnet 192.168.0.50 5000
```

---

## 🖥️ **Frigate Server Commands**

▶️ **Container Management**

```bash
# Start system
docker compose up -d

# Stop system
docker compose down

# Restart Frigate
docker compose restart frigate

# View all containers
docker ps -a
```

▶️ **Logging & Monitoring**

```bash
# Real-time Frigate logs
docker compose logs -f frigate

# Last 100 log entries
docker logs frigate --tail 100

# Check container resource usage
docker stats frigate
```

▶️ **Storage Management**

```bash
# Check storage usage
df -h

# Check recording directory size
du -sh /srv/frigate/storage/

# Clean old recordings (older than 30 days)
find /srv/frigate/storage/recordings/ -name "*.mp4" -mtime +30 -delete

# Check database size
ls -lh ./config/frigate.db
```

---

## 🔍 **Diagnostic Procedures**

▶️ **Complete System Health Check**

```bash
#!/bin/bash
# Run on Raspberry Pi
echo "=== Pi System Health ==="
echo "Temperature: $(vcgencmd measure_temp)"
echo "Throttling: $(vcgencmd get_throttled)"
echo "Memory: $(free -h | grep Mem:)"
echo "go2rtc Status: $(systemctl is-active go2rtc.service)"
echo "Camera Processes: $(ps aux | grep rpicam-vid | grep -v grep | wc -l)"
echo "RTSP Port: $(ss -tulpn | grep :8554 | wc -l)"
```

▶️ **Frigate Health Check**

```bash
#!/bin/bash
# Run on Frigate server
echo "=== Frigate System Health ==="
echo "Container Status: $(docker inspect frigate --format='{{.State.Status}}')"
echo "CPU Usage: $(docker stats frigate --no-stream --format 'table {{.CPUPerc}}')"
echo "Memory Usage: $(docker stats frigate --no-stream --format 'table {{.MemUsage}}')"
echo "Storage: $(df -h | grep recordings)"
echo "Recent Recordings: $(find ./recordings -name '*.mp4' -mmin -5 | wc -l)"
```

---

## 🎆 **Emergency Procedures**

▶️ **Complete System Restart**

```bash
# On Raspberry Pi:
sudo systemctl stop go2rtc.service
sudo systemctl start go2rtc.service

# On Frigate Server:
docker compose down
docker compose up -d

# Wait 2 minutes, then verify all streams in Frigate UI
```

▶️ **Factory Reset Procedure**

```bash
# Backup current configs first!
cp /etc/go2rtc.yaml /home/skimlab/go2rtc.yaml.backup

# Reset go2rtc
sudo systemctl stop go2rtc.service
sudo systemctl disable go2rtc.service

# Reinstall from production configs
# (Use Production Runbooks & Guides)
```

---

*Keep this reference handy for quick troubleshooting and system management.*
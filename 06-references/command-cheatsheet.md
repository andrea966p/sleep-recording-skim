---
tags: [reference, commands, cheatsheet]
created: 2026-02-05
updated: 2026-02-10
---

# Command Cheatsheet

Quick copy-paste blocks for common operations. All values match [[00-config/production-values|production-values.md]].

## Raspberry Pi (`192.168.0.11`)

### SSH Access
```bash
ssh skimlab@192.168.0.11
```

### Health Check
```bash
vcgencmd measure_temp
vcgencmd get_throttled
# 0x0 = OK, 0x50005 = undervoltage detected
uptime
free -m
df -h /
```

### Camera Hardware
```bash
rpicam-hello --list-cameras
# Both OV5647 should appear at 10-0036 and 11-0036

# Check camera device nodes
ls /dev/video*

# Quick single-camera test (5s, no output)
rpicam-vid --codec libav --libav-format h264 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --timeout 5000 --camera 0 --level 4.1 --profile high --output /dev/null
```

### go2rtc Service
```bash
sudo systemctl status go2rtc.service
sudo systemctl restart go2rtc.service
sudo systemctl stop go2rtc.service

# Live logs
journalctl -u go2rtc.service -f

# Last 50 lines
journalctl -u go2rtc.service -n 50

# Check stream definitions
curl -s http://localhost:1984/api/streams

# Count active rpicam-vid processes (2 = both cameras streaming)
ps aux | grep rpicam-vid | grep -v grep | wc -l
```

### Trigger a Stream (for testing)
```bash
# Trigger cam 0 for 10 seconds
curl -m 10 "http://localhost:1984/api/stream.mp4?src=pi_cam_0" -o /dev/null

# Trigger cam 1 for 10 seconds
curl -m 10 "http://localhost:1984/api/stream.mp4?src=pi_cam_1" -o /dev/null
```

### Boot Configuration
```bash
# View current boot config
cat /boot/firmware/config.txt

# Backup before editing
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup.$(date +%Y%m%d)

# Edit
sudo nano /boot/firmware/config.txt

# Reboot required for changes
sudo reboot
```

### Watchdog Status
```bash
# Check hardware watchdog is active
cat /sys/class/watchdog/watchdog0/state

# Check systemd is using it (should show "Using hardware watchdog")
systemctl show -p WatchdogDevice
journalctl -b | grep -i watchdog
```

### systemd Config Editing
```bash
# Edit go2rtc service
sudo nano /etc/systemd/system/go2rtc.service

# MUST reload after any .service file change
sudo systemctl daemon-reload
sudo systemctl restart go2rtc.service

# Verify the active config
systemctl cat go2rtc.service
```

### Journal / Logs
```bash
# Live system log
journalctl -f

# Previous boot logs (requires persistent journal)
journalctl -b -1 --no-pager | tail -100

# Search for crashes in previous boot
journalctl -b -1 --no-pager | grep -i -E "panic|oops|oom|killed|error" | tail -30

# Current boot kernel messages
dmesg | tail -50

# Watch dmesg live (for debugging)
dmesg -w

# List all boots
journalctl --list-boots

# Disk usage of journal
journalctl --disk-usage

# Journal config
cat /etc/systemd/journald.conf
```

### Network
```bash
# Check ethernet link
ip addr show eth0
ip link show eth0

# Check connections to this Pi
ss -tnp

# DNS / gateway
ip route show default
resolvectl status
```

---

## Frigate NVR (`192.168.0.50`)

### SSH Access
```bash
ssh skimlab@192.168.0.50
```

### Docker / Frigate
```bash
# Status
docker ps -a
docker stats frigate --no-stream

# Start / stop / restart
cd /srv/frigate
docker compose up -d
docker compose down
docker compose restart frigate

# Live logs
docker compose logs -f frigate

# Last 100 lines
docker logs frigate --tail 100

# Frigate API
curl -s http://localhost:5000/api/stats
curl -s http://localhost:5000/api/config
```

### Storage
```bash
df -h /srv/frigate/storage
du -sh /srv/frigate/storage/recordings/
du -sh /srv/frigate/storage/clips/
```

### Frigate Config
```bash
# Edit config
nano /srv/frigate/config/config.yml

# Restart to apply
cd /srv/frigate && docker compose restart frigate
```

---

## Cross-System Validation

### Full System Check (run from NVR or any machine on `192.168.0.x`)
```bash
# Ping Pi
ping -c 2 192.168.0.11

# Check go2rtc API
curl -s http://192.168.0.11:1984/api/streams

# Check Frigate API
curl -s http://192.168.0.50:5000/api/stats

# Test RTSP stream (grab 1 frame)
curl -m 5 "http://192.168.0.11:1984/api/stream.mp4?src=pi_cam_0" -o /dev/null && echo "cam0 OK"
curl -m 5 "http://192.168.0.11:1984/api/stream.mp4?src=pi_cam_1" -o /dev/null && echo "cam1 OK"
```

### Pi One-Liner Health (run on Pi)
```bash
echo "Temp: $(vcgencmd measure_temp) | Throttle: $(vcgencmd get_throttled) | Cams: $(ps aux | grep rpicam-vid | grep -v grep | wc -l)/2 | Mem: $(free -m | awk '/Mem/{printf "%d/%dMB", $3, $2}')"
```

---

## Tailscale

### Status
```bash
tailscale status
tailscale ip -4
tailscale ping <hostname-or-ip>
```

### Connectivity
```bash
# Check if using direct or relayed connection
tailscale ping --c 5 100.85.191.25

# Network check
tailscale netcheck
```

---

## Emergency Procedures

### Pi — Kill Stuck Streams
```bash
sudo systemctl stop go2rtc.service
sudo pkill -9 rpicam-vid
sudo systemctl start go2rtc.service
```

### Pi — Full Service Reset
```bash
sudo systemctl stop go2rtc.service
sudo pkill -9 rpicam-vid
sudo systemctl daemon-reload
sudo systemctl start go2rtc.service
sudo systemctl status go2rtc.service
```

### Frigate — Full Restart
```bash
cd /srv/frigate
docker compose down
docker compose up -d
docker ps
```

### Pi — Force Reboot (if SSH works but system is hung)
```bash
sudo reboot
```

---

## Config File Locations

| File | Path | Machine |
|------|------|---------|
| go2rtc config | `/opt/go2rtc/go2rtc.yaml` | Pi |
| go2rtc service | `/etc/systemd/system/go2rtc.service` | Pi |
| Boot config | `/boot/firmware/config.txt` | Pi |
| Journal config | `/etc/systemd/journald.conf` | Pi |
| Frigate config | `/srv/frigate/config/config.yml` | NVR |
| Docker Compose | `/srv/frigate/docker-compose.yml` | NVR |
| RustDesk config | `~/.config/rustdesk/RustDesk2.toml` | PCs |

---

---
# 🎯 Troubleshooting Matrix (v5.0)

> [!note] 🔍
> **QUICK DIAGNOSIS:** Find your issue in the matrix below for immediate solutions based on real production experience.

## Critical Issues & Solutions

### 🔴 System Freeze / SSH Hangs

**Symptoms:**

- SSH sessions freeze after running for hours/days
- Cannot connect to Pi via SSH
- System appears to hang randomly

**Root Cause:** Zombie rpicam-vid processes due to incorrect systemd KillMode

**Solution:**

```bash
# Fix the systemd service
sudo nano /etc/systemd/system/go2rtc.service

# Ensure this line is present:
KillMode=control-group  # NOT 'mixed' or 'process'

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart go2rtc.service
```

### 🔴 Frigate CPU at 100%

**Symptoms:**

- Frigate container using 100% CPU
- Recordings dropping frames
- Web interface sluggish

**Root Cause:** No hardware acceleration enabled

**Solution:**

```yaml
# In docker-compose.yml, add:
devices:
  - /dev/dri:/dev/dri

# In config.yml, add:
ffmpeg:
  hwaccel_args: preset-intel-qsv-h264
```

### 🔴 "No frames received" in Frigate

**Symptoms:**

- Frigate shows camera as offline
- "No frames have been received" error
- Intermittent connection drops

**Root Cause:** Using UDP transport or incorrect stream names

**Solution:**

```yaml
# In Frigate config.yml:
cameras:
  pi_cam_0:  # Must match go2rtc stream name
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/pi_cam_0
          input_args:
            - -rtsp_transport
            - tcp  # Force TCP
            - -buffer_size
            - "512000"
            - -max_delay
            - "500000"
```

## Common Issues Matrix

| Symptom | Likely Cause | Quick Fix | Prevention |
| --- | --- | --- | --- |
| Camera not detected | Legacy camera enabled | Disable in raspi-config | Never enable legacy camera |
| High temperature (>70°C) | Poor cooling or high settings | Reduce FPS/resolution | Use active cooler |
| Recordings have gaps | Network instability | Use TCP transport | Wired ethernet only |
| Memory leak in go2rtc | Old version | Update to v1.9.4+ | Set MemoryMax in service |
| Stream delays | Buffer settings | Adjust buffer_size | Use recommended values |
| Kernel panic with H.265 | Hardware limitation | Use H.264 only | Never use H.265 codec |
| Zombie processes | Wrong KillMode | Set control-group | Check service file |
| QSV not working | Missing GPU groups | Add render/video groups | Check group IDs |

## Diagnostic Commands

### Quick Health Check

```bash
#!/bin/bash
# Run this for instant system diagnosis

echo "=== SYSTEM HEALTH CHECK ==="
echo
echo "Temperature: $(vcgencmd measure_temp)"
echo "Throttled: $(vcgencmd get_throttled)"
echo "go2rtc: $(systemctl is-active go2rtc)"
echo "Cameras: $(ps aux | grep rpicam-vid | grep -v grep | wc -l)/2"
echo "Memory: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo
echo "=== STREAM STATUS ==="
curl -s http://localhost:1984/api/streams | python3 -c "import sys,json;d=json.load(sys.stdin);print('\n'.join([f'{k}: {\"ACTIVE\" if v else \"DEAD\"}' for k,v in d.items()]))"
```

### Process Investigation

```bash
# Check for zombie processes
ps aux | grep defunct

# Check rpicam-vid CPU usage
ps aux | grep rpicam-vid | grep -v grep | awk '{print $2, $3"%", $11}'

# Check go2rtc memory
ps aux | grep go2rtc | grep -v grep | awk '{print $2, $4"%", $6"KB"}'
```

### Network Diagnostics

```bash
# Test RTSP connectivity
for i in 0 1; do
  echo "Testing camera $i..."
  timeout 5 ffprobe -v error -rtsp_transport tcp \
    rtsp://localhost:8554/pi_cam_$i 2>&1 | \
    grep -q "Stream #0" && echo "  ✅ OK" || echo "  ❌ FAIL"
done

# Check network drops
netstat -s | grep -i drop
```

## Recovery Procedures

### Emergency Restart

```bash
# When system is partially responsive
sudo systemctl stop go2rtc
sudo pkill -9 rpicam-vid
sudo systemctl start go2rtc
```

### Full System Recovery

```bash
# When nothing else works
sudo systemctl stop go2rtc pi-monitor
sudo pkill -9 rpicam-vid go2rtc ffmpeg
sudo rm -f /tmp/go2rtc.lock  # Clear any lock files
sudo systemctl daemon-reload
sudo systemctl start go2rtc pi-monitor
```

### Rollback Procedure

```bash
# If new config causes issues
sudo cp /opt/go2rtc/go2rtc.yaml.backup /opt/go2rtc/go2rtc.yaml
sudo cp /etc/systemd/system/go2rtc.service.backup /etc/systemd/system/go2rtc.service
sudo systemctl daemon-reload
sudo systemctl restart go2rtc
```

## Performance Tuning

### Expected Performance Metrics

**Raspberry Pi 5 (with proper config):**

- CPU: 20-30% average
- Memory: 400-500MB
- Temperature: 55-60°C
- Network: 3-4 Mbps constant

**Frigate Server (with QSV):**

- CPU: 9-12% (was 100% without QSV)
- GPU: 3-4% utilization
- Memory: ~870MB
- Disk I/O: 3-4 MB/s write

### Optimization Tips

1. **Thermal Management**
```bash
# If running hot, reduce quality
# Change from 1024x768@15fps to 800x600@10fps
# Saves ~10°C
```
2. **Memory Optimization**
```bash
# Add to /etc/sysctl.conf
vm.swappiness=10
vm.vfs_cache_pressure=50
```
3. **Network Optimization**
```bash
# Add to /etc/sysctl.conf
net.core.rmem_max=134217728
net.core.wmem_max=134217728
net.ipv4.tcp_rmem=4096 87380 134217728
net.ipv4.tcp_wmem=4096 65536 134217728
```

## Known Limitations

### Hardware Constraints

- **H.265/HEVC:** Causes kernel panics - DO NOT USE
- **4K Resolution:** Not stable for 24/7 operation
- **WiFi:** Too unreliable for RTSP streaming
- **USB Cameras:** Not compatible with rpicam-vid

### Software Constraints

- **Detection + Recording:** Choose one for stability
- **Multiple Frigates:** One NVR per network segment
- **go2rtc versions < 1.9:** Memory leaks present

## Validation Checklist

Run after any configuration change:

```bash
#!/bin/bash
# Complete validation script

FAIL=0

# Check services
for svc in go2rtc pi-monitor watchdog; do
  systemctl is-active --quiet $svc || { echo "❌ $svc not running"; FAIL=1; }
done

# Check processes
[ $(pgrep rpicam-vid | wc -l) -eq 2 ] || { echo "❌ Wrong number of cameras"; FAIL=1; }
[ $(pgrep -c defunct) -eq 0 ] || { echo "❌ Zombie processes detected"; FAIL=1; }

# Check streams
for i in 0 1; do
  curl -sf http://localhost:1984/api/streams | grep -q "pi_cam_$i" || 
    { echo "❌ Stream pi_cam_$i not found"; FAIL=1; }
done

# Check system
temp=$(vcgencmd measure_temp | grep -o '[0-9]*' | head -1)
[ $temp -lt 70 ] || { echo "❌ Temperature too high: ${temp}°C"; FAIL=1; }

throttle=$(vcgencmd get_throttled | cut -d= -f2)
[ "$throttle" = "0x0" ] || { echo "❌ Throttling detected: $throttle"; FAIL=1; }

if [ $FAIL -eq 0 ]; then
  echo "✅ ALL CHECKS PASSED - System healthy"
else  
  echo "⚠️ VALIDATION FAILED - Review errors above"
  exit 1
fi
```

## Contact for Critical Issues

If the above solutions don't resolve your issue:

4. Check the R&D Log for similar experiments
5. Review the Archive section for old configs
6. Run the diagnostic script and save output
7. Document the issue with logs for future reference
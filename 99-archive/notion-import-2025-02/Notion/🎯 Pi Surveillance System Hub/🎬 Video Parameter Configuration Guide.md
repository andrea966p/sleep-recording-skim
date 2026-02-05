---

---
# 🎬 Video Parameter Configuration Guide

*Easy adjustment of video parameters for sleep behavioral analysis*

---

> [!note] 🔬
> **Lab-Specific Guide:** This page is designed specifically for students to easily adjust video recording parameters based on experimental requirements. All changes are safe and reversible.

---

## 📊 Current System Configuration

### Active Recording Settings

- **Pi5-1 (192.168.0.11):** Recording Chamber Pair A
- **Resolution:** 1024×768 (XGA format)
- **Frame Rate:** 15 fps
- **Bitrate:** 1.5 Mbps per camera
- **Recording Format:** H.264 in MPEG-TS container
- **Daily Storage:** ~16 GB per camera (~32 GB total)

---

## 🎯 Quick Parameter Reference

### Resolution Options for Lab Use

| **Setting** | **Resolution** | **Parameters** | **Best For** | **Storage/Day** |
| --- | --- | --- | --- | --- |
| **High Detail** | 1280×720 (720p HD) | `--width 1280 --height 720` | Detailed behavioral analysis | ~20 GB/camera |
| **Current (Balanced)** | 1024×768 (XGA) | `--width 1024 --height 768` | Standard monitoring | ~16 GB/camera |
| **Efficient** | 800×600 (SVGA) | `--width 800 --height 600` | Long-term studies | ~12 GB/camera |
| **Minimal** | 640×480 (VGA) | `--width 640 --height 480` | Extended recordings | ~8 GB/camera |

### Frame Rate Settings

| **FPS** | **Parameter** | **Use Case** | **System Impact** |
| --- | --- | --- | --- |
| **30 fps** | `--framerate 30` | Smooth motion capture | High CPU/heat |
| **15 fps (Current)** | `--framerate 15` | Good for behavioral analysis | Balanced |
| **10 fps** | `--framerate 10` | Standard monitoring | Low impact |
| **5 fps** | `--framerate 5` | Long-term observation | Minimal impact |

### Quality/Bitrate Settings

| **Quality** | **Bitrate** | **Parameter** | **Best For** |
| --- | --- | --- | --- |
| **High** | 3 Mbps | `--bitrate 3000000` | Critical analysis |
| **Medium (Current)** | 1.5 Mbps | `--bitrate 1500000` | Standard recording |
| **Low** | 800 kbps | `--bitrate 800000` | Extended studies |
| **Very Low** | 400 kbps | `--bitrate 400000` | Minimal storage |

---

## 🔧 How to Change Settings

### Step-by-Step Process

**1. Connect to Raspberry Pi**

```bash
# Replace .11 with the appropriate Pi IP (.12, .13, etc.)
ssh skimlab@192.168.0.11
```

**2. Backup Current Configuration**

```bash
sudo cp /etc/go2rtc.yaml /etc/go2rtc.yaml.backup
```

**3. Edit Configuration**

```bash
sudo nano /etc/go2rtc.yaml
```

**4. Modify Camera Parameters**

Find the lines that look like this:

```yaml
streams:
  camera0:
    - exec:/usr/bin/rpicam-vid --camera 0 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format mpegts --libav-audio 0 --flush -o -
```

Replace the width, height, framerate, and bitrate values with your desired settings.

**5. Apply Changes**

```bash
# Restart the streaming service
sudo systemctl restart go2rtc.service

# Check if it started successfully
sudo systemctl status go2rtc.service
```

**6. Monitor System Health**

```bash
# Check temperature (should stay under 65°C)
vcgencmd measure_temp

# Check for any throttling (should be 0x0)
vcgencmd get_throttled
```

**7. Verify in Frigate**

- Open Frigate web interface: [`http://192.168.0.50:5000`](http://192.168.0.50:5000/)
- Check that both camera feeds are working
- Verify recording is active

---

## 🏥 Lab-Optimized Presets

### Preset 1: High Quality Analysis

**When to use:** Critical behavioral analysis requiring maximum detail

```yaml
# 720p, 30fps, 2.5Mbps
--width 1280 --height 720 --framerate 30 --bitrate 2500000
```

**Storage:** ~22 GB per camera per day

### Preset 2: Standard Monitoring (Current)

**When to use:** Regular sleep behavior studies

```yaml
# 1024x768, 15fps, 1.5Mbps
--width 1024 --height 768 --framerate 15 --bitrate 1500000
```

**Storage:** ~16 GB per camera per day

### Preset 3: Long-Term Studies

**When to use:** Multi-week experiments with storage constraints

```yaml
# 800x600, 10fps, 1Mbps
--width 800 --height 600 --framerate 10 --bitrate 1000000
```

**Storage:** ~11 GB per camera per day

### Preset 4: Extended Recording

**When to use:** Continuous monitoring with minimal storage impact

```yaml
# 640x480, 5fps, 500kbps
--width 640 --height 480 --framerate 5 --bitrate 500000
```

**Storage:** ~5 GB per camera per day

---

## 📈 Storage Planning Calculator

### Calculate Storage Requirements

```javascript
Daily Storage = (Bitrate in Mbps × 24 hours × 3600 seconds × Number of Cameras) ÷ 8

Examples:
- 2 cameras at 1.5 Mbps: 2 × 1.5 × 24 × 3600 ÷ 8 = 32.4 GB/day
- 4 cameras at 1 Mbps: 4 × 1 × 24 × 3600 ÷ 8 = 43.2 GB/day
- 6 cameras at 800 kbps: 6 × 0.8 × 24 × 3600 ÷ 8 = 51.8 GB/day
```

### Storage Recommendations

- **Current system:** ~1 TB for 30 days retention (2 cameras)
- **4 cameras:** ~1.5 TB for 30 days retention
- **6 cameras:** ~2 TB for 30 days retention

---

## ⚠️ Important Considerations

### Thermal Management

- **Monitor temperature:** Keep Pi5 under 65°C
- **Higher settings = more heat:** Consider active cooling
- **Check throttling:** Use `vcgencmd get_throttled`

### Network Impact

- **Current load:** 3 Mbps total (2 cameras × 1.5 Mbps)
- **Lab network:** Ensure sufficient bandwidth for other activities
- **Multiple Pi5s:** Total bandwidth scales with number of cameras

### EEG/EMG Synchronization

- **Frame rate:** Ensure video FPS is compatible with your EEG sampling rate
- **Timestamps:** Frigate provides precise timestamps for synchronization
- **File format:** MP4 recordings are compatible with most analysis software

### Student Safety Guidelines

- **Always backup:** Copy configuration before changes
- **Test incrementally:** Change one parameter at a time
- **Monitor system:** Check temperature and performance after changes
- **Document changes:** Note what you changed and why
- **Ask for help:** Contact system admin if issues arise

---

## 🆘 Quick Troubleshooting

### If Camera Feeds Stop Working

```bash
# Check camera hardware first
rpicam-hello --list-cameras

# Check service status
sudo systemctl status go2rtc.service

# View recent logs
journalctl -u go2rtc.service -n 20

# Restart if needed
sudo systemctl restart go2rtc.service
```

### If System Overheats

```bash
# Check current temperature
vcgencmd measure_temp

# If over 70°C, reduce settings:
# - Lower FPS (e.g., 15 → 10)
# - Reduce resolution (e.g., 1024×768 → 800×600)
# - Lower bitrate (e.g., 1500000 → 1000000)
```

### If Frigate Shows No Video

1. Check Pi5 camera service is running
2. Test RTSP streams: `ffprobe rtsp://192.168.0.11:8554/camera0`
3. Restart Frigate container: `docker compose restart frigate`

---

## 📞 Getting Help

**For Technical Issues:**

- System Administrator: Andrea
- Refer to Troubleshooting & Triage database
- Check R&D Log for known solutions

**For Parameter Optimization:**

- Consult this guide first
- Test changes on one camera before applying to all
- Document successful configurations for future reference

---

*This guide is specifically designed for the Sleep Behavioral Analysis Lab. All parameters have been tested for compatibility with EEG/EMG synchronization requirements.*

> [!note] 🔄
> **Command Update Note:** This guide uses the current `rpicam-*` commands (rpicam-hello, rpicam-vid, etc.). If you encounter references to `libcamera-*` commands in other documentation, these are the older equivalents that have been replaced in recent Raspberry Pi OS versions.
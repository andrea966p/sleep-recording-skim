---

---
# **Presentation Concept Notes**

Detailed explanations for each section of the presentation skeleton.

---

## **1. Introduction & Context**

### Lab Surveillance Problem

- **Problem**: Need to monitor 10-16 mice simultaneously for sleep behavioral studies
- **Requirements**: 24/7 continuous recording, synchronized with EEG/EMG data, multiple chambers
- **Challenge**: Must be reliable for multi-day experiments (no data loss tolerated)
- **Student Access**: Multiple researchers need to start/stop recordings independently

### Budget Constraints

- **Commercial NVR Systems**: 2,600K-5,200K KRW for 10 cameras
- **Research Budget Reality**: Limited funding for equipment
- **Need**: Professional-grade reliability at research-budget pricing
- **Goal**: Match commercial performance at 50% cost

---

## **2. System Architecture Overview**

### Two-Machine Architecture

- **Machine 1 (Raspberry Pi)**: Dedicated camera streamer at 192.168.0.11
- **Machine 2 (Ubuntu Server)**: Network Video Recorder at 192.168.0.50
- **Why Separate**: Distributed processing, fault isolation, scalability

### Raspberry Pi Role

- **Function**: ONLY streaming (not recording)
- **Hardware**: 2 cameras per Pi via dual CSI ports
- **Software**: Raspberry Pi OS Lite + go2rtc
- **Output**: RTSP streams on port 8554

### Ubuntu Server Role

- **Function**: Recording, storage, web interface
- **Software**: Frigate NVR in Docker
- **Input**: Receives RTSP streams via network
- **Storage**: Local drives + NAS backup

### Why Physical Separation Matters

- **Stability**: Pi focuses only on streaming (no heavy recording workload)
- **Performance**: Server uses Intel GPU for hardware acceleration
- **Reliability**: Component failures are isolated (one Pi failure ≠ total system failure)
- **Maintenance**: Can restart/update components independently

### Network Design

- **Fixed IPs**: 192.168.0.11 (Pi), 192.168.0.50 (Server)
- **RTSP Port**: 8554 (standard RTSP)
- **TCP vs UDP**: TCP for reliability (UDP causes frame drops)
- **Why Static IPs**: Prevents stream URLs from breaking on DHCP renewal

### PoE+ Switch Role

- **Power**: Delivers 15.4W-30W per port (IEEE 802.3at)
- **Data**: 1 Gbps per camera (no bandwidth bottleneck)
- **Single Cable**: Power + data in one Ethernet cable
- **Budget**: 153W total (supports 6 Pi boards = 12 cameras)

### Ethernet Cable Requirements

- **Category**: Cat6 minimum (supports PoE+ power delivery)
- **Certification**: PoE-certified cables (some cheap cables fail under power load)
- **Length**: <100m per cable (standard Ethernet limit)

### Network Topology

```javascript
[Pi #1] ──┐
[Pi #2] ──┤
[Pi #3] ──┼──[PoE+ Switch]──[Ubuntu Server]──[NAS]
[Pi #4] ──┤
[Pi #5] ──┘
```

### Data Flow

1. **Camera** → Captures raw video
2. **rpicam-vid** → Hardware H.264 encoding
3. **go2rtc** → RTSP server (streams encoded video)
4. **Network** → TCP transport to server
5. **Frigate** → Records streams to disk
6. **Storage** → Local storage + NAS backup

---

## **3. Why Not Commercial Solutions**

### Cost Comparison

- **Commercial IP Cameras**: 200K-400K KRW each × 10 = 2,000K-4,000K KRW
- **Commercial NVR**: 500K-1,000K KRW
- **Total**: 2,600K-5,200K KRW
- **Our Solution**: 1,380K KRW (47% savings)

### Flexibility Limitations

- **Vendor Lock-in**: Proprietary software, specific camera brands required
- **Limited Customization**: Can't modify recording parameters freely
- **No API Access**: Difficult to integrate with EEG systems
- **Closed System**: Can't add custom analysis pipelines

### Privacy Concerns

- **Cloud Storage**: Many commercial systems require cloud accounts
- **Data Location**: Research data leaves your control
- **Compliance Issues**: May violate institutional data policies
- **Internet Dependency**: System fails if internet connection drops

### Cloud Storage Costs

- **Typical Pricing**: $10-50/month per camera
- **Our Data Volume**: ~16GB/camera/day = 480GB/day for 10 cameras
- **Monthly Cost**: ~$100-500/month = 1,200K-6,000K KRW annually
- **On-Premises**: One-time hardware cost, no recurring fees

---

## **4. Alternative Architectures Evaluated**

### USB Camera Systems

- **Concept**: Multiple USB cameras connected to single PC
- **Bandwidth Problem**: USB 2.0 = 480 Mbps shared across ALL cameras
    - 1080p @ 30fps = ~80 Mbps per camera
    - Only 1-2 cameras work at full quality
- **Single Point of Failure**: PC or USB hub dies → all cameras lost
- **Hidden Costs**: Need PCIe USB controller cards (150K-300K KRW)
- **Verdict**: Fundamentally doesn't work for 10 cameras

### Raspberry Pi Zero 2 W

- **Concept**: Ultra-cheap ($15) boards for 10 cameras
- **Heat Issues**: No heatsink → thermal throttling under load
- **Maintenance Complexity**: 10 separate boards to manage (no PoE)
- **Power Delivery**: Need 10 separate power supplies
- **Reliability**: Not rated for 24/7 operation
- **Verdict**: Too unstable for production use

### Raspberry Pi 4

- **Concept**: Previous generation Pi
- **Single CSI Port**: Only 1 camera per board → need 10 boards
- **Cost**: Same as Pi 5 but half the cameras
- **No PoE HAT**: Official PoE HAT has cooling issues
- **Verdict**: Pi 5 dual CSI ports make it obsolete

### All-in-One Pi + Frigate

- **Concept**: Run Frigate on Raspberry Pi (no separate server)
- **Resource Constraints**:
    - Recording 2 cameras = high CPU/memory usage
    - Pi 5 can't handle Frigate + 2 cameras simultaneously
- **Storage Limitations**: SD card or USB drive not suitable for 24/7 writes
- **Verdict**: Works for 1-2 cameras, not scalable

---

## **5. Raspberry Pi 5 Deep Dive**

### Hardware Specifications

- **CPU**: Broadcom BCM2712 (Quad-core Cortex-A76 @ 2.4GHz)
- **GPU**: VideoCore VII (hardware H.264 encoder)
- **RAM**: 8GB LPDDR4X (we use 8GB model)
- **CSI Ports**: 2× (KEY FEATURE - dual cameras per board)
- **PoE Support**: Official PoE+ HAT available
- **Power**: 25W with PoE+ (sufficient for 2 cameras + encoding)

### Dual CSI Port Advantage

- **5 Boards = 10 Cameras** (vs 10 boards with Pi 4)
- **Cost Savings**: 50% reduction in board costs
- **Cabling Reduction**: 5 Ethernet cables vs 10
- **Management**: 5 boards to maintain vs 10
- **PoE Budget**: 5× 25W = 125W (fits in 153W switch budget)

### PoE+ Integration

- **Official HAT**: Designed for 24/7 operation
- **Active Cooling**: Built-in fan (temperature-controlled)
- **Power Delivery**: 25.5W (sufficient for dual cameras + encoding)
- **Single Cable**: Eliminates need for separate power supplies

### Cost-Benefit Analysis

- **Pi 5 (8GB)**: ~120K KRW × 5 = 600K KRW
- **Camera Modules**: ~35K KRW × 10 = 350K KRW
- **PoE HATs**: ~20K KRW × 5 = 100K KRW
- **PoE Switch**: ~180K KRW
- **Cables + SD Cards**: ~150K KRW
- **Total**: ~1,380K KRW for 10 cameras
- **Per Camera**: ~138K KRW (vs 260K-520K for commercial)

---

## **6. Camera Hardware**

### Camera Module Options

- **Camera v2 (OV5647)**: 5MP, older sensor, discontinued
- **Camera v3 (IMX708)**: 12MP, modern sensor, HDR support
- **HQ Camera (IMX477)**: 12.3MP, C/CS lens mount, expensive
- **Global Shutter Camera**: No rolling shutter artifacts, very expensive

### Resolution and FPS Considerations

- **Our Choice**: 1024×768 @ 15fps
- **Why Not 1080p**: Higher bitrate = more bandwidth + storage
- **Why Not 30fps**: Sleep studies don't need high frame rate
- **Storage Impact**: 1024×768@15fps = ~16GB/day vs 1080p@30fps = ~40GB/day

### Camera v3 Selection Justification

- **Cost**: ~35K KRW (affordable for 10 cameras)
- **Quality**: 12MP sensor (more than sufficient for mice monitoring)
- **IR Performance**: Works well with external IR illumination
- **Availability**: Currently produced (v2 discontinued)
- **Support**: Full rpicam-vid support

---

## **7. rpicam-vid**

### What is rpicam-vid

- **Definition**: Official Raspberry Pi camera application
- **Purpose**: Direct hardware encoder access
- **Replaces**: Old raspivid (deprecated)
- **Advantages**: Modern, maintained, optimized for Pi 5

### Hardware Encoder Access

- **Direct Path**: Camera → ISP → Hardware H.264 encoder
- **No CPU Encoding**: Hardware encoder is separate silicon
- **Low CPU Usage**: <10% CPU for dual cameras
- **Low Latency**: <100ms encode latency
- **Quality**: Hardware encoder is optimized, better than software

### Alternatives Comparison

- **libcamera-vid**: Old name for rpicam-vid (renamed in 2023)
- **ffmpeg**: Software encoding only (high CPU, not feasible)
- **v4l2**: Low-level interface (complex, no benefits)
- **Verdict**: rpicam-vid is the only practical choice

### Command Structure

```bash
rpicam-vid \
  --camera 0 \              # Camera index (0 or 1)
  -t 0 \                    # Timeout (0 = infinite)
  --width 1024 \            # Resolution width
  --height 768 \            # Resolution height
  --framerate 15 \          # FPS
  --bitrate 1500000 \       # 1.5 Mbps
  --codec libav \           # Use libav wrapper
  --libav-format h264 \     # H.264 output
  --inline \                # Inline headers (important!)
  --nopreview \             # No display preview
  -o -                      # Output to stdout
```

### Key Parameters

- **--codec libav**: Uses libavcodec wrapper (stable)
- **--inline**: Embeds SPS/PPS headers (required for streaming)
- **-o -**: Outputs raw H.264 to stdout (piped to go2rtc)

---

## **8. go2rtc: The Streaming Engine**

### What is go2rtc

- **Definition**: Lightweight RTSP server
- **Language**: Written in Go
- **Size**: Single 15MB binary
- **Purpose**: Converts H.264 stream → RTSP for network distribution

### Role in System

- **Input**: H.264 from rpicam-vid (via stdin)
- **Processing**: Wraps H.264 in RTSP protocol
- **Output**: RTSP stream on port 8554
- **Bonus**: Web interface on port 1984 for testing

### Alternatives Comparison

- **MediaMTX**: Similar but larger, more complex
- **FFmpeg Server**: Heavy, not optimized for RTSP
- **VLC**: Not designed for 24/7 operation
- **Verdict**: go2rtc is lightweight, stable, perfect for embedded

### Architecture: rpicam-vid → go2rtc → RTSP

```javascript
rpicam-vid (stdout) → go2rtc (stdin) → RTSP network stream
```

- **Pipe**: Direct process pipe (no network overhead)
- **Efficiency**: No re-encoding, just protocol wrapping
- **Latency**: <50ms additional latency

### Configuration Structure

```yaml
streams:
  camera0:
    - exec:rpicam-vid [parameters] -o -
  camera1:
    - exec:rpicam-vid [parameters] -o -

api:
  listen: ":1984"    # Web interface
rtsp:
  listen: ":8554"    # RTSP server
```

---

## **8.5 go2rtc Installation Steps**

### Download Binary

```bash
# Download latest release
wget https://github.com/AlexxIT/go2rtc/releases/download/v1.9.0/go2rtc_linux_arm64
```

### Install to System

```bash
# Option 1: System-wide
sudo mv go2rtc_linux_arm64 /usr/local/bin/go2rtc
sudo chmod +x /usr/local/bin/go2rtc

# Option 2: Dedicated directory (preferred)
sudo mkdir -p /opt/go2rtc
sudo mv go2rtc_linux_arm64 /opt/go2rtc/go2rtc
sudo chmod +x /opt/go2rtc/go2rtc
```

### Directory Structure

```javascript
/opt/go2rtc/
├── go2rtc           # Binary
└── go2rtc.yaml      # Configuration
```

### File Permissions

```bash
# Set ownership
sudo chown -R skimlab:video /opt/go2rtc

# Set permissions
sudo chmod 755 /opt/go2rtc
sudo chmod 644 /opt/go2rtc/go2rtc.yaml
```

### Create Configuration Location

```bash
# Create empty config file
sudo touch /opt/go2rtc/go2rtc.yaml
sudo chown skimlab:video /opt/go2rtc/go2rtc.yaml
```

---

## **9. Frigate: The NVR**

### What is Frigate

- **Definition**: Open-source Network Video Recorder
- **Language**: Python (backend) + JavaScript (frontend)
- **Purpose**: Record, store, and playback RTSP streams
- **Special Features**: AI object detection (we don't use), hardware acceleration

### Alternatives Comparison

- **MotionEye**: Older, less maintained, no hardware acceleration
- **Shinobi**: Complex setup, resource-heavy
- **ZoneMinder**: Very old, designed for 2000s-era systems
- **Verdict**: Frigate is modern, actively developed, best hardware acceleration

### Docker Deployment Benefits

- **Isolation**: Frigate runs in container (doesn't affect host system)
- **Easy Updates**: docker compose pull to update
- **Portability**: Move to different server easily
- **Dependencies**: All dependencies bundled in container

### Manual Recording Feature

- **On-Demand**: Start/stop recording via web interface
- **No AI Detection**: We disabled object detection (not needed)
- **Simple Control**: Click button to record, click to stop
- **Perfect for Experiments**: Start recording when experiment starts

### Hardware Acceleration

- **Intel QSV**: Uses Intel GPU for decoding/encoding
- **CPU Savings**: 90% reduction in CPU usage
- **Our Hardware**: Intel Arc GPU (very fast)
- **Why Important**: 10 cameras = massive CPU load without acceleration

### Web Interface

- **Access**: [http://192.168.0.50:5000](http://192.168.0.50:5000/)
- **Features**:
    - Live view (all cameras in grid)
    - Recording controls
    - Playback with timeline
    - Download recordings
    - System statistics
- **Multi-User**: Multiple students can access simultaneously

---

## **9.5 Frigate Installation Steps**

### Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin
```

### Create docker-compose.yml

```bash
# Create directory
mkdir -p ~/frigate
cd ~/frigate

# Create docker-compose.yml
nano docker-compose.yml
```

### Set Up Volume Mounts

```yaml
volumes:
  - /media/frigate:/media/frigate    # Recordings
  - ./config:/config                  # Configuration
```

- **Recordings**: Large storage drive
- **Config**: Frigate configuration files

### Configure Device Access

```yaml
devices:
  - /dev/dri:/dev/dri    # Intel GPU for hardware acceleration
```

- **Why**: Gives container access to Intel GPU
- **Required**: For hardware-accelerated encoding/decoding

### Deploy Container

```bash
# Start Frigate
docker compose up -d

# Watch logs
docker compose logs -f frigate
```

### Verify Container

```bash
# Check status
docker compose ps

# Should show: frigate   Up

# Test web interface
curl http://localhost:5000
```

---

## **10. The "Golden" Configurations**

### Complete go2rtc.yaml

```yaml
streams:
  camera0:
    - exec:/usr/bin/rpicam-vid --camera 0 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format h264 --libav-audio 0 --inline --nopreview --flush -o -
    
  camera1:
    - exec:/usr/bin/rpicam-vid --camera 1 -t 0 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --codec libav --libav-format h264 --libav-audio 0 --inline --nopreview --flush -o -

api:
  listen: ":1984"
rtsp:
  listen: ":8554"
webrtc:
  listen: ":8555"
log:
  level: info
```

### rpicam-vid stdout → go2rtc stdin

- **exec Command**: go2rtc launches rpicam-vid as child process
- **Pipe**: stdout of rpicam-vid → stdin of go2rtc
- **Efficient**: No intermediate files or network sockets
- **Fast**: Direct memory pipe

### H.264 Choice: --codec libav --libav-format h264

- **libav Wrapper**: Stable codec interface
- **H.264**: Universally supported, efficient
- **Hardware Accelerated**: Pi 5 has H.264 encoder in silicon

### Why NOT H.265

- **Kernel Panics**: H.265 caused system crashes on Pi 5
- **Driver Issues**: H.265 encoder drivers are immature
- **Testing**: Ran for 2 hours → system frozen
- **Verdict**: H.264 is stable, H.265 is experimental (FORBIDDEN)

### Why NOT TCP Streaming Architecture

- **Old Design**: rpicam-vid → [localhost](http://localhost/):port → go2rtc reads from port
- **Problem**: Network layer adds complexity and failure points
- **Instability**: Streams dropped after 12-24 hours
- **Versions 1-3**: All used TCP streaming, all failed
- **Verdict**: Direct pipe (exec) is much more stable

### Complete systemd Service File

```plain text
[Unit]
Description=go2rtc streaming server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=skimlab
WorkingDirectory=/opt/go2rtc
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml

# CRITICAL SETTINGS
KillMode=control-group
TimeoutStopSec=10

# Resource limits
CPUQuota=70%
MemoryMax=512M

# Restart policy
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### KillMode=control-group Explanation

- **Problem**: rpicam-vid runs as child process of go2rtc
- **Without control-group**: When go2rtc restarts, rpicam-vid becomes zombie
- **With control-group**: systemd kills ALL processes in the group
- **Result**: No zombie processes accumulate
- **Impact**: THE SINGLE MOST IMPORTANT SETTING FOR STABILITY

### Resource Limits

- **CPUQuota=70%**: Limits to 70% of one CPU core
- **MemoryMax=512M**: Hard limit on RAM usage
- **Why**: Prevents runaway processes from freezing the Pi
- **Testing**: Without limits, system froze after 3-4 days

### Frigate Camera Input Configuration

```yaml
cameras:
  lab_cam_0:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.11:8554/camera0
          input_args:
            - -rtsp_transport
            - tcp
            - -buffer_size
            - 512000
            - -max_delay
            - 500000
          roles:
            - record
```

### -rtsp_transport tcp (not UDP)

- **TCP**: Reliable, retransmits lost packets
- **UDP**: Fast but drops packets (causes glitches)
- **Our Network**: Wired Ethernet (TCP overhead negligible)
- **Verdict**: Reliability > Speed for research data

### Buffering: -buffer_size 512000 -max_delay 500000

- **Buffer Size**: 512KB buffer for incoming stream
- **Max Delay**: Tolerate up to 500ms delay
- **Purpose**: Smooth out network jitter
- **Result**: No frame drops during network fluctuations

### Intel QSV Hardware Acceleration

```yaml
ffmpeg:
  hwaccel_args: preset-intel-qsv-h264
```

- **QSV**: Quick Sync Video (Intel's hardware encoder/decoder)
- **Preset**: Pre-configured settings for Intel GPUs
- **CPU Usage**: Drops from 400% to 40% with 10 cameras
- **Required**: Without this, CPU is overwhelmed

---

## **10.5 Configuration File Locations & Structure**

### Raspberry Pi Files

```javascript
/opt/go2rtc/
├── go2rtc              # Binary
└── go2rtc.yaml         # Streaming config

/etc/systemd/system/
└── go2rtc.service      # Service definition

/boot/firmware/
└── config.txt          # System hardening

/etc/
└── dhcpcd.conf         # Static IP
```

### Ubuntu Server Files

```javascript
~/frigate/
├── docker-compose.yml  # Container definition
└── config/
    └── config.yml      # Frigate configuration

/media/frigate/
└── recordings/         # Video storage
```

### Directory Structure Explanation

- **Raspberry Pi**: Minimal files (streamer only)
- **Ubuntu Server**: Frigate config + storage
- **Why Separate**: Clear separation of concerns

---

## **11. System Hardening**

### /boot/firmware/config.txt Modifications

```plain text
# Disable unnecessary peripherals
dtoverlay=disable-wifi
dtoverlay=disable-bt

# Enable hardware watchdog
dtparam=watchdog=on

# Allocate GPU memory
gpu_mem=128
```

### Hardware Watchdog

- **Purpose**: Automatically reboots Pi if system hangs
- **Mechanism**: Hardware timer must be reset every N seconds
- **If Frozen**: Watchdog not reset → automatic reboot
- **Critical**: For 24/7 unattended operation

### Disable WiFi/Bluetooth

- **WiFi**: Not needed (using Ethernet)
- **Bluetooth**: Not needed
- **Benefits**:
    - Reduced power consumption
    - Reduced interference
    - Freed resources
    - Security (fewer attack surfaces)

### GPU Memory Allocation (gpu_mem=128)

- **Purpose**: Reserve memory for hardware H.264 encoder
- **Default**: 76MB (insufficient for dual cameras)
- **Our Setting**: 128MB
- **Why**: Prevents encoding failures due to memory pressure

### Static IP Configuration

**Method 1: /etc/dhcpcd.conf (Raspberry Pi OS)**

```bash
interface eth0
static ip_address=192.168.0.11/24
static routers=192.168.0.1
static domain_name_servers=8.8.8.8 8.8.4.4
```

**Method 2: Netplan (Ubuntu)**

```yaml
network:
  version: 2
  ethernets:
    eth0:
      addresses: [192.168.0.50/24]
      gateway4: 192.168.0.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

### Why Static IPs

- **RTSP URLs**: Hardcoded with IP addresses
- **DHCP Renewal**: Could change IP → broken streams
- **Reliability**: Fixed IPs = no connectivity issues

### Justification for Each Measure

- **Watchdog**: Prevents multi-day experiments failing due to freeze
- **Disable WiFi/BT**: Stability (fewer drivers/processes)
- **GPU Memory**: Hardware encoder reliability
- **Static IP**: Stream URL consistency

---

## **11.5 System Verification & Testing**

### Test go2rtc Web Interface

```bash
# From any computer on network
open http://192.168.0.11:1984
```

- **Expected**: Web page with stream list
- **Check**: Both camera0 and camera1 should be listed
- **Test**: Click stream to watch live preview

### Verify RTSP Streams with ffprobe

```bash
# On Raspberry Pi or any device
ffprobe rtsp://192.168.0.11:8554/camera0

# Expected output:
Input #0, rtsp, from 'rtsp://192.168.0.11:8554/camera0':
  Duration: N/A, start: 0.000000, bitrate: N/A
  Stream #0:0: Video: h264, yuv420p, 1024x768, 15 fps
```

- **Success**: Shows H.264 stream info
- **Failure**: Connection refused or timeout

### Check systemd Service Status

```bash
sudo systemctl status go2rtc.service

# Expected:
● go2rtc.service - go2rtc streaming server
   Loaded: loaded (/etc/systemd/system/go2rtc.service)
   Active: active (running) since...
```

- **Green "active (running)"**: Good
- **Red "failed"**: Check logs

### Monitor Logs

```bash
# Real-time log monitoring
journalctl -u go2rtc -f

# Expected:
go2rtc[1234]: INF [rtsp] listen addr=:8554
go2rtc[1234]: INF [api] listen addr=:1984
go2rtc[1234]: INF [streams] camera0 exec:rpicam-vid...
```

- **Look for**: No errors, streams starting successfully
- **Red flags**: "ERROR", "FATAL", "failed"

### Test Frigate Web Interface

```bash
# From any computer
open http://192.168.0.50:5000
```

- **Expected**: Frigate dashboard
- **Check**: Can see live camera feeds

### Verify Recordings Being Saved

```bash
# On Ubuntu Server
ls -lh /media/frigate/recordings/

# Should show:
drwxr-xr-x 2 user user 4.0K Oct 23 12:00 lab_cam_0
drwxr-xr-x 2 user user 4.0K Oct 23 12:00 lab_cam_1
```

- **Check**: Directories exist, files being created

### Check Hardware Acceleration Working

```bash
# On Ubuntu Server
intel_gpu_top

# Expected:
Video Engine: 30-60% utilization
```

- **If 0%**: Hardware acceleration not working
- **If 30-60%**: Working correctly (10 cameras)

### Confirm Low CPU Usage

```bash
# On Raspberry Pi
top

# Expected:
CPU: 15-25% (for 2 cameras)

# On Ubuntu Server
top

# Expected:
CPU: 40-60% (for 10 cameras with QSV)
```

- **High CPU**: Hardware acceleration not working

---

## **12. Critical Stability Lessons (Iteration History)**

### Version 1-2: H.265 Codec Kernel Panics

- **Attempt**: Used --libav-format h265 for better compression
- **Result**: System frozen after 2-3 hours
- **Diagnosis**: Kernel panic in H.265 encoder driver
- **Evidence**: dmesg showed GPU driver crash
- **Lesson**: H.265 encoder is UNSTABLE on Pi 5 (as of 2025)
- **Action**: **FORBIDDEN** to use H.265

### Version 3: TCP Streaming Architecture Instability

- **Attempt**: rpicam-vid streams to [localhost](http://localhost/):port, go2rtc reads from port
- **Configuration**:
```bash
rpicam-vid ... --listen --port 8000
```
- **Result**: Streams dropped after 12-24 hours
- **Diagnosis**: TCP socket connection issues, buffer overflows
- **Lesson**: Network layer adds unnecessary complexity
- **Action**: Switch to direct exec pipe

### Version 4: Missing KillMode → Zombie Processes

- **Attempt**: systemd service without KillMode setting
- **Result**: Pi froze after 3-4 days
- **Diagnosis**:
```bash
ps aux | grep rpicam-vid
# Showed 20-30 zombie rpicam-vid processes
```
- **Cause**: When go2rtc restarted, rpicam-vid child processes not killed
- **Lesson**: systemd doesn't kill child processes by default
- **Action**: Add KillMode=control-group

### Version 4: No Resource Limits → Memory Exhaustion

- **Attempt**: No CPUQuota or MemoryMax settings
- **Result**: Pi occasionally froze, oom-killer triggered
- **Diagnosis**: go2rtc memory leak under certain conditions
- **Lesson**: Resource limits prevent one process from crashing system
- **Action**: Add CPUQuota=70%, MemoryMax=512M

### Version 5: exec + libav + KillMode → Stable 30+ Days

- **Configuration**: Current "golden" configuration
- **Results**:
    - 30+ days continuous uptime
    - Zero manual interventions
    - Zero zombie processes
    - Stable memory usage
- **What Changed**:
    1. exec command (not TCP streaming)
    2. H.264 only (not H.265)
    3. KillMode=control-group
    4. Resource limits
    5. Hardware watchdog

### Importance of Iteration Process

- **Failures Are Learning**: Each failure revealed a weakness
- **Systematic Testing**: Changed one variable at a time
- **Documentation**: Kept notes on what failed and why
- **Patience**: Took 3 months to reach stable v5.0

### How Each Failure Informed Next Version

7. **H.265 panics** → Use only H.264
8. **TCP streaming drops** → Use direct exec pipe
9. **Zombie processes** → Add KillMode
10. **Memory exhaustion** → Add resource limits
11. **Random freezes** → Enable hardware watchdog

---

## **13. Distributed Architecture Advantages**

### Elimination of USB Bandwidth Bottleneck

- **USB Problem**: 480 Mbps shared across all devices
- **Our Solution**: 1 Gbps per camera (dedicated Ethernet)
- **Math**:
    - USB: 480 Mbps ÷ 10 cameras = 48 Mbps per camera (insufficient)
    - Ethernet: 1000 Mbps per camera (20× more bandwidth)
- **Result**: No quality degradation, no bandwidth contention

### Fault Tolerance: Isolated Node Failures

- **USB System**: PC fails → all 10 cameras lost
- **Our System**: 1 Pi fails → only 2 cameras lost (other 8 continue)
- **Scenario**: Pi #3 fails during experiment
    - Impact: Cameras 5-6 lost
    - Mitigation: Cameras 1-4, 7-10 still recording
    - Recovery: Restart Pi #3, minimal data loss

### Local Processing Power Per Node

- **USB System**: Central PC encodes all 10 cameras (CPU bottleneck)
- **Our System**: Each Pi encodes its own 2 cameras
- **Distribution**:
    - 5 Pis × 2 cameras = 10 total
    - Each Pi uses 15-25% CPU
    - No single bottleneck

### Hardware-Level EEG Synchronization

- **GPIO Pins**: Pi 5 has GPIO pins
- **Trigger**: EEG system sends pulse → GPIO pin
- **Timestamp**: rpicam-vid can timestamp on GPIO trigger
- **Precision**: Microsecond-level synchronization
- **Future**: Enables frame-accurate EEG-video correlation

### Cabling Simplicity

- **USB System**:
    - 10× USB cables
    - 10× Power cables
    - Total: 20 cables
- **Our System**:
    - 5× Ethernet cables (PoE carries power + data)
    - Total: 5 cables
- **Cleanliness**: 75% reduction in cable clutter

---

## **14. System Reliability**

### Uptime Metrics

- **Current**: 30+ days continuous operation (Version 5.0)
- **Uptime %**: 99.9% (only downtime = planned maintenance)
- **Manual Interventions**: Zero in 30 days
- **Crashes**: Zero since v5.0 deployment

### Performance Data

- **CPU Usage**:
    - Raspberry Pi: 15-25% (2 cameras)
    - Ubuntu Server: 40-60% (10 cameras with QSV)
- **Memory Usage**:
    - Raspberry Pi: 200-300MB / 8GB (stable)
    - Ubuntu Server: 4-6GB / 32GB (stable)
- **Network**: 1.5 Mbps per camera × 10 = 15 Mbps total (minimal)
- **Storage**: ~160 GB per day (10 cameras)

### Self-Healing Capabilities

- **Hardware Watchdog**: Auto-reboot if frozen (never triggered yet)
- **systemd Restart**: Auto-restart go2rtc if crashes (Restart=always)
- **Frigate Auto-Restart**: Docker restart policy (unless-stopped)
- **Network Recovery**: Services reconnect automatically after network blip

### Resource Monitoring

- **systemd Journal**: All logs centralized
- **Frigate Web Interface**: System health dashboard
- **Command**: `systemctl status go2rtc` for quick health check
- **Storage**: Automatic monitoring via Frigate retention policies

### Failure Recovery Mechanisms

- **Single Pi Failure**:
    1. Other 4 Pis continue operating
    2. Ssh to failed Pi
    3. `sudo systemctl restart go2rtc`
    4. Back online in 30 seconds
- **Network Failure**:
    1. Frigate shows "No connection"
    2. Fix network
    3. Streams auto-reconnect (TCP retry mechanism)
- **Server Failure**:
    1. Pis continue streaming (not dependent on server)
    2. Fix server
    3. Frigate resumes recording from live streams

---

## **15. Data Storage & Management**

### Storage Location

- **Path**: `/media/frigate/recordings/`
- **Mount**: Dedicated 4TB HDD on Ubuntu server
- **Structure**:
```javascript
/media/frigate/recordings/
├── lab_cam_0/
│   ├── 2025-10-23/
│   │   ├── 00/  # Hour 00
│   │   ├── 01/
│   │   └── ...
│   └── 2025-10-24/
└── lab_cam_1/
```

### Frigate Retention Policies

```yaml
record:
  enabled: true
  retain:
    days: 30
    mode: all
```

- **30 Days**: Automatically deletes recordings older than 30 days
- **Mode: all**: Keeps all recordings (not just motion events)
- **Automatic**: No manual cleanup needed

### Storage Requirements

- **Per Camera**: ~16 GB per day
    - Calculation: 1.5 Mbps × 86400 seconds = ~16 GB
- **10 Cameras**: ~160 GB per day
- **30 Days Retention**: 160 GB × 30 = ~4.8 TB
- **Our Storage**: 4TB HDD (sufficient for 25 days)

### How to Export/Download Recordings

12. **Via Web Interface**:
    - Navigate to date/time
    - Click "Download" button
    - Saves as MP4 file
13. **Via SCP**:
```bash
scp sleepigene@192.168.0.50:/media/frigate/recordings/lab_cam_0/2025-10-23/14/30.mp4 ./
```
14. **Via Network Share** (if configured):
    - Mount Frigate recordings folder
    - Copy files directly

### Backup Strategy to NAS

- **Method**: rsync to Synology NAS
- **Frequency**: Daily
- **Command**:
```bash
rsync -avz /media/frigate/recordings/ nas:/backup/frigate/
```
- **Retention**: 60 days on NAS (longer than Frigate)

### Disk Space Monitoring

```bash
# Check available space
df -h /media/frigate

# Expected output:
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdb1       4.0T  2.8T  1.2T  70% /media/frigate
```

- **Alert Threshold**: 80% full
- **Action**: Delete older recordings or expand storage

---

## **16. Scalability**

### Current Setup

- **5 Pi Boards**: pi5-1 through pi5-5
- **10 Cameras**: 2 per Pi
- **Switch**: TP-Link TL-SG2210MP (8× PoE+ ports)
- **Power Budget**: 153W total

### Ethernet Switch Capacity

- **PoE Budget**: 153W
- **Per Pi**: 25W
- **Calculation**: 153W ÷ 25W = 6.1 Pis maximum
- **Current Usage**: 5 Pis × 25W = 125W (82% utilized)

### Maximum Capacity with Current Switch

- **Maximum Pis**: 6 boards
- **Maximum Cameras**: 12 cameras (6 boards × 2)
- **Remaining Capacity**: 1 Pi board (2 cameras)
- **Power Headroom**: 153W - 125W = 28W (enough for 1 more Pi)

### Expansion Strategy for Future Growth

**Scenario 1: Expand to 12 Cameras**

- Add 1× Raspberry Pi 5
- Add 2× Camera modules
- Use existing switch (within power budget)
- Cost: ~160K KRW

**Scenario 2: Expand Beyond 12 Cameras**

- Add second PoE+ switch
- Add more Pi boards
- Frigate can handle 20+ cameras with QSV acceleration
- Cost: ~180K KRW (switch) + ~160K KRW per 2 cameras

**Scenario 3: Second Lab Setup**

- Duplicate entire setup
- Second Frigate server OR share existing server
- Independent network (different IP range)
- Cost: ~1,400K KRW for complete duplicate

---

## **17. Practical Operations**

### Student Access Requirements

- **Network**: Must be on lab network (192.168.0.x)
- **No Login**: Frigate web interface is open (no password)
- **Training**: 10-minute walkthrough sufficient

### Training Requirements

15. Open web browser
16. Navigate to [http://192.168.0.50:5000](http://192.168.0.50:5000/)
17. Identify correct camera
18. Click "Start Recording" / "Stop Recording"
19. Download recordings if needed

### Starting Recordings

20. Access Frigate: [http://192.168.0.50:5000](http://192.168.0.50:5000/)
21. Click camera name (e.g., "lab_cam_0")
22. Verify live stream is visible
23. *Optional*: Start manual recording if not continuous
24. Note start time for later retrieval

### Stopping Recordings

25. Access Frigate
26. Navigate to camera
27. *If manual recording*: Click "Stop Recording"
28. *If continuous*: No action needed (automatic 30-day retention)

### Accessing Footage

29. Click "Recordings" tab in Frigate
30. Select camera
31. Select date range
32. Timeline shows recorded segments
33. Click segment to play
34. Click "Download" to save

### System Monitoring Procedures

- **Daily**: Check Frigate dashboard (all cameras green)
- **Weekly**: Check disk space (`df -h /media/frigate`)
- **Monthly**: Review logs for errors

### Routine Maintenance Tasks

- **Weekly**: Visually verify all cameras streaming
- **Monthly**: Check for system updates
- **Quarterly**: Clean Pi heatsinks/fans
- **Yearly**: Review storage capacity, expand if needed

### Common Troubleshooting Commands

**Check if streams are running:**

```bash
# On Raspberry Pi
sudo systemctl status go2rtc
curl http://localhost:1984/api/streams
```

**Check Frigate status:**

```bash
# On Ubuntu Server
docker compose ps
docker compose logs -f frigate
```

**Restart services:**

```bash
# Restart Pi streaming
ssh skimlab@192.168.0.11
sudo systemctl restart go2rtc

# Restart Frigate
ssh sleepigene@192.168.0.50
cd ~/frigate
docker compose restart
```

### Where to Check Logs

**Raspberry Pi logs:**

```bash
journalctl -u go2rtc -n 100
journalctl -u go2rtc -f  # Follow live
```

**Frigate logs:**

```bash
docker compose logs frigate -n 100
docker compose logs -f  # Follow live
```

---

## **18. Future Capabilities**

### On-Board Real-Time Video Analysis

- **Current**: Only recording
- **Future**: Pi 5 GPU can run ML models
- **Possible**:
    - Motion detection
    - Behavior classification (grooming, sleeping, active)
    - Posture analysis
- **Advantage**: Processing at source (reduced server load)

### AI/ML Behavior Tracking Integration

- **Current**: Manual video review
- **Future**: Automated behavior annotation
- **Technologies**:
    - DeepLabCut for pose estimation
    - Custom CNN for sleep stage classification
    - Integration with SLEAP or similar
- **Output**: Timestamped behavior events synchronized with EEG

### Precise EEG-Video Synchronization

- **Current**: Separate start times (manual alignment)
- **Future**: Hardware GPIO triggering
- **Implementation**:
    1. EEG system sends pulse to Pi GPIO pin
    2. rpicam-vid timestamps frame on GPIO trigger
    3. Microsecond-precision synchronization
- **Benefit**: Frame-accurate correlation of brain activity and behavior

### Remote Monitoring Dashboard

- **Current**: Local network only
- **Future**: HTTPS access from anywhere
- **Implementation**:
    - Tailscale VPN OR
    - Nginx reverse proxy with Let's Encrypt SSL
- **Use Case**: Check experiments from home

### Automated Analysis Pipeline

- **Current**: Manual export → analysis
- **Future**: Automated pipeline
- **Workflow**:
    1. Experiment ends → trigger analysis
    2. Extract video clips
    3. Run ML models
    4. Generate summary report
    5. Email to researcher
- **Saves**: Hours of manual work per experiment

---

## **19. Cost Analysis**

### USB Setup Costs: ~1,100-1,200K KRW

**Components:**

- 10× USB IR cameras: ~800K KRW (80K each)
- 2× Powered USB hubs: ~60K KRW
- 3-5× PCIe USB controller cards: ~150-300K KRW
- **Total**: 1,010-1,160K KRW

**Hidden Costs:**

- PC powerful enough to encode 10 cameras: 1,500K+ KRW
- Extra PCIe slots required
- Higher power consumption

**Verdict**: "Cheap" but doesn't actually work at scale

### Pi Zero 2 W Costs: ~650K KRW

**Components:**

- 10× Pi Zero 2 W: ~200K KRW (20K each)
- 10× Camera modules: ~350K KRW
- 10× Power supplies: ~100K KRW
- **Total**: ~650K KRW

**Hidden Costs:**

- 10× MicroSD cards
- 20 cables (10 USB power + 10 Ethernet)
- Maintenance nightmare (10 boards to manage)
- Unreliable (not rated for 24/7)

**Verdict**: Cheap but high maintenance, unreliable

### Pi 5 Setup Costs: ~1,380K KRW

**Components:**

- 5× Raspberry Pi 5 (8GB): ~600K KRW (120K each)
- 10× Camera v3 modules: ~350K KRW (35K each)
- 5× PoE+ HAT: ~100K KRW (20K each)
- 1× PoE+ Switch (8-port): ~180K KRW
- 5× Ethernet cables: ~25K KRW
- 5× MicroSD cards (128GB): ~75K KRW
- **Total**: ~1,380K KRW

**Per Camera**: ~138K KRW

**Advantages:**

- Production-grade reliability
- Professional architecture
- Easy maintenance (5 boards vs 10)
- Scalable

### Commercial CCTV Costs: ~2,600-5,200K KRW

**Components:**

- 10× IP cameras (budget): ~2,000K KRW (200K each)
- 10× IP cameras (quality): ~4,000K KRW (400K each)
- NVR system: ~500-1,000K KRW
- Installation: ~100-200K KRW
- **Total**: 2,600-5,200K KRW

**Advantages:**

- Plug-and-play
- Professional support
- Warranty

**Disadvantages:**

- 2-4× more expensive
- Vendor lock-in
- No customization

### Total Cost of Ownership

**5-Year TCO:**

*USB System:*

- Hardware: 1,200K KRW
- PC: 1,500K KRW
- Power (high consumption): ~300K KRW
- **Total**: ~3,000K KRW
- **Problem**: Doesn't work reliably

*Pi 5 System:*

- Hardware: 1,380K KRW
- Power (low consumption): ~100K KRW
- SD card replacements: ~50K KRW
- **Total**: ~1,530K KRW

*Commercial CCTV:*

- Hardware: 3,000K-5,000K KRW
- Power (moderate): ~150K KRW
- Support contracts: ~500K KRW
- **Total**: ~3,650-5,650K KRW

**Winner**: Pi 5 system (best value, reliability, flexibility)

---

## **20. Lessons Learned**

### What Failed (Versions 1-4)

**Version 1: H.265 Encoding**

- **Approach**: Use HEVC for better compression
- **Failure**: Kernel panics after 2-3 hours
- **Lesson**: Bleeding-edge codecs are unstable

**Version 2: High-Resolution Streaming**

- **Approach**: 1080p @ 30fps
- **Failure**: Bandwidth saturation, dropped frames
- **Lesson**: Higher isn't always better

**Version 3: TCP Streaming Architecture**

- **Approach**: rpicam-vid → TCP port → go2rtc
- **Failure**: Streams dropped after 12-24 hours
- **Lesson**: Simpler is better (direct pipe)

**Version 4: No Process Management**

- **Approach**: Basic systemd service
- **Failure**: Zombie processes accumulated, system froze
- **Lesson**: KillMode=control-group is mandatory

**Version 4: No Resource Limits**

- **Approach**: Assumed processes would behave
- **Failure**: Memory leaks caused OOM killer
- **Lesson**: Always set resource limits

### What Worked (Version 5)

**exec Command:**

- Direct pipe from rpicam-vid to go2rtc
- No intermediate network/files
- Rock-solid stable

**H.264 Codec:**

- Mature, well-tested
- Hardware encoder fully supported
- Never crashed

**KillMode=control-group:**

- Kills all child processes
- No zombie processes
- Single most important stability fix

**Resource Limits:**

- Prevents runaway processes
- System remains responsive

**Hardware Watchdog:**

- Safety net for complete freezes
- Never triggered (but good to have)

### Key Decisions and Trade-offs

**Decision 1: 1024×768 vs 1080p**

- **Trade-off**: Slightly lower resolution for stability + storage
- **Justification**: Mice don't need 1080p, 768p is sufficient

**Decision 2: 15fps vs 30fps**

- **Trade-off**: Half frame rate for half storage
- **Justification**: Sleep behaviors are slow-moving

**Decision 3: TCP vs UDP**

- **Trade-off**: Slightly higher latency for reliability
- **Justification**: Research needs 100% data integrity

**Decision 4: Separate NVR vs All-in-One**

- **Trade-off**: Extra hardware for better performance
- **Justification**: Distributed architecture scales better

**Decision 5: DIY vs Commercial**

- **Trade-off**: Setup time for cost savings + flexibility
- **Justification**: Research budget + need for customization

### Importance of Iteration

- **Not Failure, Learning**: Each "failed" version taught something
- **Systematic**: Changed one variable at a time
- **Documentation**: Detailed notes on what worked/failed
- **Time Investment**: 3 months to reach v5.0 (worth it)
- **Result**: Production-grade system for research budget

### Technical Debt and Future Improvements

- **Configuration Management**: Currently manual (could use Ansible)
- **Monitoring Dashboard**: Basic (could add Grafana)
- **Alerting**: None (could add email/Slack alerts)
- **Backup Automation**: Manual rsync (could automate)
- **Documentation**: Notion-based (could generate from code)

---

## **21. Resources & Documentation**

### Notion Workspace

- **URL**: [https://notion.so/andrea96p/](https://notion.so/andrea96p/)
- **Pages**:
    - 🎯 Pi Surveillance System Hub (main)
    - 🏗️ Complete Pi5 Setup Guide
    - 🔧 Configuration Reference
    - 🎯 Troubleshooting Matrix
    - ⚡ Quick Start Guide

### Configuration Files

- **GitHub** (if published): Repository with all configs
- **Notion**: Configuration Files Library page
- **Local**: Backed up in `/opt/backups/` on each machine

### Student Onboarding Materials

- **Quick Start PDF**: 2-page guide for new students
- **Video Tutorial**: Screen recording of basic operations
- **FAQ Document**: Common questions and answers

### Community Resources

**Raspberry Pi:**

- Forums: [https://forums.raspberrypi.com/](https://forums.raspberrypi.com/)
- Documentation: [https://www.raspberrypi.com/documentation/](https://www.raspberrypi.com/documentation/)

**go2rtc:**

- GitHub: [https://github.com/AlexxIT/go2rtc](https://github.com/AlexxIT/go2rtc)
- Discussions: GitHub issues page

**Frigate:**

- Documentation: [https://docs.frigate.video/](https://docs.frigate.video/)
- Discord: Active community support
- GitHub: [https://github.com/blakeblackshear/frigate](https://github.com/blakeblackshear/frigate)

### Support Channels

- **Internal**: Lab Slack channel #surveillance-system
- **External**: Frigate Discord, Raspberry Pi forums
- **Vendor**: Raspberry Pi official support (for hardware issues)

---

# **End of Concept Notes**

*This document provides detailed explanations for every point in the presentation skeleton. Use these as speaker notes or reference material when preparing slides.*
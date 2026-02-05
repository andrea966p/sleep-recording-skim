---

---
# 🔬 Sleep Behavioral Analysis Lab - Surveillance System Hub 📹

**Mission:** To maintain a 100% stable, 24/7 video recording system for mice sleep behavioral analysis research. This system records synchronized video data for EEG/EMG analysis in multiple chambers. Reliability and easy expansion are the #1 priorities.

**Lab Usage:**

- **Purpose:** Record mice behavior in individual chambers for sleep analysis
- **Users:** Multiple students accessing Frigate interface for manual recording control
- **Data:** Video recordings synchronized with EEG/EMG data for behavioral analysis
- **Architecture:** Central Frigate NVR with expandable Pi5 camera nodes (1 Pi5 = 2 chambers)

---

## Dashboard 🚀

| **Project Status** | **Last Checked** | **Lead** |
| --- | --- | --- |
| 🟢 **Operational** | September 16, 2025 | Andrea |

> [!note] 🎯
> **Mission:** To maintain a 100% stable, 24/7 video recording system for lab research. This page documents the final, hardened configuration and all related procedures. **Reliability is the #1 priority.**

---

<!-- Column 1 -->





### Quick Navigation 🔗


<!-- Column 2 -->





### System Components 🖥️

**🐳 Frigate NVR (Ubuntu PC)**

- **IP:** `192.168.0.50`
- **Status:** 🟢 Online
- **Services:** Docker, Frigate
- **Web UI:** [http://192.168.0.50:5000](http://192.168.0.50:5000/)

**🍓 Camera Pi 1 (skimlab)**

- **IP:** `192.168.0.11`
- **Status:** 🟢 Online
- **Services:** go2rtc, Monitor
- **RTSP Streams:** Port 8554
- **API:** [http://192.168.0.11:1984](http://192.168.0.11:1984/)

---

## 📚 Documentation Structure

### 🏗️ Complete Pi5 Setup Guide (v5.0)

> *From zero to production-grade 24/7 operation*

- Step-by-step installation procedures
- Hardware requirements and validation
- System tuning and optimization
- Service configuration and deployment
- Complete deployment checklist

### 📁 Configuration Files Library

> *All production configurations with explanations*

- Boot configuration (`config.txt`)
- go2rtc streaming server configuration
- Frigate NVR configuration
- System service definitions
- Validation scripts and deployment instructions

### 🛠️ Scripts & Utilities

> *Production scripts for monitoring and maintenance*

- System health monitoring script
- Automated installation scripts
- Log cleanup and maintenance
- Configuration backup utilities
- Safe system update procedures

### 🚑 Troubleshooting Database

> *Interactive problem-solving knowledge base*

- Common issues and solutions
- Diagnostic procedures
- Step-by-step troubleshooting guides
- Board view organized by status

### 🔬 R&D Experiment Log

> *Record of trials, failures, and lessons learned*

- Failed H.265 encoding attempt
- Successful motion detection test
- Configuration change documentation
- Performance impact analysis

---

## 📊 Lab System Status

### 🎖️ Current Recording Setup

**Pi5-1 (192.168.0.11)** - **Chamber Pair A**

- Camera 0: 🜢 Recording (Chamber A1) - 1024×768@15fps
- Camera 1: 🜢 Recording (Chamber A2) - 1024×768@15fps
- Storage: 30-day retention, ~45GB per camera per day
- Status: 🜢 **Operational** - Ready for student access

### 📋 Lab Expansion Plan

**IP Address Allocation Scheme:**

| **Pi5 Node** | **IP Address** | **Chamber Pair** | **Individual Chambers** | **Status** |
| --- | --- | --- | --- | --- |
| **Pi5-1 (skimlab)** | `192.168.0.11` | Chamber Pair A | A1 (Camera 0), A2 (Camera 1) | 🟢 **Active** |
| **Pi5-2** | `192.168.0.12` | Chamber Pair B | B1 (Camera 0), B2 (Camera 1) | 🟡 Ready to Deploy |
| **Pi5-3** | `192.168.0.13` | Chamber Pair C | C1 (Camera 0), C2 (Camera 1) | 🟡 Ready to Deploy |
| **Pi5-4** | `192.168.0.14` | Chamber Pair D | D1 (Camera 0), D2 (Camera 1) | 🟡 Ready to Deploy |
| **Pi5-5** | `192.168.0.15` | Chamber Pair E | E1 (Camera 0), E2 (Camera 1) | 🟡 Ready to Deploy |

**Scaling Pattern:** Each Pi5 = 2 chambers, sequential IP addresses starting from .11

**Router Configuration:** Reserve IP addresses `192.168.0.11` through `192.168.0.25` for Pi5 nodes

### 🏗️ Adding New Pi5 Nodes (Quick Guide)

---

## 🎬 **Video Parameter Configuration**

> [!note] 🎬
> **New for Students:** Easy-to-use video parameter adjustment guide specifically designed for sleep behavioral analysis. Change resolution, frame rate, and bitrate safely without affecting system stability.

**Quick Access:**

- **Video Parameter Guide:** [[🎬 Video Parameter Configuration Guide]]
- **Current Settings:** 1024×768 @ 15fps, 1.5Mbps per camera
- **Lab Presets:** High Quality, Standard, Long-term, Extended Recording
- **Storage Calculator:** Plan storage requirements for different settings

**Common Adjustments:**

- **Higher Quality:** 720p @ 30fps for detailed analysis
- **Lower Storage:** 800×600 @ 10fps for extended studies
- **Minimal Impact:** 640×480 @ 5fps for continuous monitoring

---

**Step 1: Prepare New Pi5**

1. Flash SD card with hostname `pi5-X` (where X = next number)
2. Set static IP to next available address (e.g., `192.168.0.12`)
3. Follow Complete Pi5 Setup Guide (v5.0) exactly

**Step 2: Update Frigate Configuration**

Add new cameras to `/srv/frigate/config/config.yml`:

```yaml
cameras:
  # Existing cameras...
  
  # New Pi5-2 cameras
  pi5_2_cam_0:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.12:8554/camera0
          input_args: preset-rtsp-restream
          roles: [record, rtmp]
    record:
      enabled: true
    detect:
      enabled: false
  
  pi5_2_cam_1:
    ffmpeg:
      inputs:
        - path: rtsp://192.168.0.12:8554/camera1
          input_args: preset-rtsp-restream
          roles: [record, rtmp]
    record:
      enabled: true
    detect:
      enabled: false
```

**Step 3: Restart Frigate**

```bash
cd /srv/frigate
docker compose restart frigate
```

**Step 4: Verify in Web Interface**

- Open [`http://192.168.0.50:5000`](http://192.168.0.50:5000/)
- Confirm new cameras appear in the dashboard
- Test live view and recording functionality

**Camera Naming Convention:**

- Pi5-1: `pi_cam_0`, `pi_cam_1` (legacy names, keep as-is)
- Pi5-2: `pi5_2_cam_0`, `pi5_2_cam_1`
- Pi5-3: `pi5_3_cam_0`, `pi5_3_cam_1`
- Pattern continues for additional nodes

### 🎥 Recording Operations

- **Manual Control:** Students start/stop recordings via Frigate web interface
- **Multi-user Access:** Multiple students can access [http://192.168.0.50:5000](http://192.168.0.50:5000/) simultaneously
- **Data Integration:** Video files ready for EEG/EMG synchronization analysis

### Key Performance Metrics

- **Uptime Target:** 99.9% (8.76 hours/year downtime budget)
- **Storage Rate:** ~45GB per camera per day
- **Network Load:** <30% of available bandwidth
- **Recovery Time:** <30 seconds for automatic restart
- **Temperature:** Optimized for <65°C under load

### 🏢 Lab Network Architecture

```javascript
         💻 Central Frigate NVR (192.168.0.50)
                    │
                    │ 🌐 Lab Network 
                    │
    ┌──────────────┴─────────────────┐
    │                                         │
 🍏 Pi5-1           🍏 Pi5-2         🍏 Pi5-3...
(.11) Chambers A1+A2  (.12) Chambers B1+B2  (.13) Chambers C1+C2
      │                    │                  │
   📹📹 Dual Cameras    📹📹 Dual Cameras   📹📹 Dual Cameras
   RTSP :8554          RTSP :8554         RTSP :8554
```

**Key Design Principles:**

- **Scalable:** Add Pi5 nodes without disrupting existing chambers
- **Reliable:** Each Pi5 operates independently with monitoring
- **Student-Friendly:** Single Frigate interface for all cameras
- **Research-Ready:** Manual recording control for experiment timing

---

## ⚡ Quick Health Check Commands

**On Raspberry Pi:**

```bash
# Service status
sudo systemctl status go2rtc.service pi-monitor.service

# Camera processes (should be 2)
ps aux | grep rpicam-vid | grep -v grep | wc -l

# System health
vcgencmd measure_temp    # Should be <65°C
vcgencmd get_throttled   # Should be 0x0

# Stream test
ffprobe rtsp://127.0.0.1:8554/pi_cam_0
ffprobe rtsp://127.0.0.1:8554/pi_cam_1
```

**On Frigate Server:**

```bash
# Container status
docker ps | grep frigate

# API health check
curl -s http://localhost:5000/api/stats | jq '.service.uptime' 
```

**Automated Health Check:**

```bash
# Run comprehensive system diagnostic
/opt/scripts/system-health-check.sh --verbose

# Monitor system in real-time
tail -f /var/log/pi-monitor.log
```

---

## 🚨 Emergency Procedures

### ⚡ Quick System Restart

```bash
# Raspberry Pi
sudo systemctl restart go2rtc.service

# Frigate Server
cd /srv/frigate
docker compose restart frigate
```

### 📞 Emergency Contacts & Escalation

- **System Administrator:** Andrea
- **Backup Contact:** [To be defined]
- **Documentation:** All procedures documented in sub-pages
- **Backup Location:** `/home/skimlab/backups/`

### 🆘 Critical Issue Protocol

4. 🔍 Check **Troubleshooting Database** for known solutions
5. 📊 Run [`system-health-check.sh`](http://system-health-check.sh/) for diagnostics
6. 📝 Document new issues in **R&D Log** if unknown
7. 📧 Contact system administrator if unresolved
8. 🔄 Use **Configuration Backup** for rollback if needed

---

## 📋 Latest Updates (v5.0)

### ✅ Recent Changes

- **🚨 CRITICAL FIX:** Corrected Frigate configuration validation errors (UI date_style, logger structure)
- Complete Notion documentation structure implemented
- Production-ready scripts deployed
- **UPDATED:** All `libcamera-*` commands replaced with current `rpicam-*` commands
- **FIXED:** Removed invalid `-debug` flag from go2rtc configuration testing commands
- Added comprehensive Video Parameter Configuration Guide for students
- Enhanced lab expansion planning with clear IP addressing scheme
- Troubleshooting database populated with known issues
- R&D log includes H.265 failure and motion detection results
- Configuration files organized with deployment instructions
- Automated maintenance procedures established

### 🎯 Key Improvements

- **Stability Focus:** All configurations optimized for 24/7 operation
- **Comprehensive Monitoring:** Automated health checks and alerting
- **Documentation:** Complete setup procedures with validation steps
- **Maintenance:** Automated log cleanup and configuration backup
- **Troubleshooting:** Searchable database of known issues and solutions

---

## 🎯 Quick Actions

### 📅 Daily Operations

- 📊 [View system health dashboard](http://192.168.0.50:5000/)
- 📹 [Check camera streams](http://192.168.0.11:1984/)
- 📈 Monitor system logs: `tail -f /var/log/pi-monitor.log`

### 🗓️ Weekly Maintenance

- 🛠️ Run health check: `/opt/scripts/`[`system-health-check.sh`](http://system-health-check.sh/)` --verbose`
- 💾 Create backup: `/opt/scripts/`[`backup-config.sh`](http://backup-config.sh/)
- 🧹 Clean logs: `/opt/scripts/`[`cleanup-logs.sh`](http://cleanup-logs.sh/)

### 🗓️ Monthly Tasks

- 🔄 Safe system update: `sudo /opt/scripts/`[`update-system.sh`](http://update-system.sh/)
- 📋 Review R&D log for system improvements
- 📈 Analyze performance trends and optimize if needed

---

> This is your **mission-critical surveillance system hub**. All sub-pages contain detailed procedures and battle-tested configurations. The Complete Pi5 Setup Guide provides step-by-step installation instructions, while the Configuration Files Library contains all production-ready configs. Use the Scripts & Utilities for automated maintenance, and refer to the Troubleshooting Database for quick problem resolution.

[[🏭️ Complete Pi5 Setup Guide (v5.0)]]

![[🚑 Troubleshooting & Triage.base]]

[[📁 Configuration Files Library]]

[[🚀 Future Roadmap & Ideas]]

![[🔬 R&D Log Trials & Failures.base]]

[[🧰 Asset Library & Commands]]

[[🎬 Video Parameter Configuration Guide]]

[[⚡ Quick Start Guide (v5.0)]]

[[📚 Documentation Index (v5.0)]]

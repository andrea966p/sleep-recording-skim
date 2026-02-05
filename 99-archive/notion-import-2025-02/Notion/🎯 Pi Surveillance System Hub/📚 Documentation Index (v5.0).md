---

---
*Organized navigation for all surveillance system documentation*

## 🆕 Start Here

### ⚡ For Quick Setup (30 minutes)

→ [Quick Start Guide](https://www.notion.so/278cfe4e883b8160b22dc3a649ed5f8f) - Minimal steps to get running

### 📖 For Complete Understanding

→ [Complete Setup Guide](https://www.notion.so/270cfe4e883b81cbb6e0e4307f97c962) - Detailed instructions with explanations

### 🔧 For Configuration Reference

→ [Configuration Reference](https://www.notion.so/278cfe4e883b81b6a9d9d0c502e0750e) - All configs with explanations

## 📦 Core Documentation

### Setup & Installation

- 🎯 [Complete Pi5 Setup Guide v5.0](https://www.notion.so/270cfe4e883b81cbb6e0e4307f97c962) - Main comprehensive guide
- ⚡ [Quick Start Guide](https://www.notion.so/278cfe4e883b8160b22dc3a649ed5f8f) - Fast track setup
- 🔧 [Complete Configuration Reference](https://www.notion.so/278cfe4e883b81b6a9d9d0c502e0750e) - All configs in one place

### System Components

- 🎯 [Frigate NVR Configuration v5.0](https://www.notion.so/278cfe4e883b816d8692f36f2c35049e) - Intel QSV setup
- 💕 [Watchdog & Monitoring Setup](https://www.notion.so/278cfe4e883b811d972edbc8d2e1bb0d) - Health monitoring
- 🎬 [Video Parameter Configuration](https://www.notion.so/271cfe4e883b814ca9d6fd32f4fd3bf2) - Adjust quality settings

### Troubleshooting & Support

- 🎯 [Troubleshooting Matrix v5.0](https://www.notion.so/278cfe4e883b81d4b0a4f7e3ef6fcd15) - Common issues & solutions
- 🧰 [Asset Library & Commands](https://www.notion.so/270cfe4e883b81d19477c1a0de690cdb) - Useful commands reference
- 📁 [Configuration Files Library](https://www.notion.so/270cfe4e883b8168bde4ca4e8538258a) - Config templates

### Historical & Archive

- 📦 [Archive - Old Configurations](https://www.notion.so/278cfe4e883b81d19e9fdc189c4e79c7) - Pre-v5.0 configs (DO NOT USE)
- 🔬 [R&D Log: Trials & Failures](https://www.notion.so/630515724ed54133b9febdbeed2f119a) - What didn't work and why

## 📊 System Overview

### Architecture

```javascript
Raspberry Pi 5 (192.168.0.11)
├── rpicam-vid (Camera capture)
├── go2rtc (RTSP server :8554)
└── Monitoring (Health checks)
          ↓
Ubuntu Server (192.168.0.50)
├── Docker
├── Frigate (NVR :5000)
└── Intel QSV (Hardware acceleration)
```

### Critical v5.0 Changes

| Component | What Changed | Why | Impact |
| --- | --- | --- | --- |
| systemd service | `KillMode=control-group` | Prevents zombie processes | No more SSH freezes |
| Pipeline | h264 direct instead of mpegts | More stable | Fewer stream drops |
| Frigate | Intel QSV enabled | Hardware acceleration | CPU: 100% → 12% |
| Transport | TCP-only | Reliability | No frame drops |
| Watchdog | Hardware enabled | Auto-recovery | System self-heals |

## 🚀 Quick Decision Tree

```javascript
Need to...
├── Set up new system? → Quick Start Guide
├── Understand details? → Complete Setup Guide  
├── Fix an issue? → Troubleshooting Matrix
├── Check a config? → Configuration Reference
├── Adjust video quality? → Video Parameter Guide
├── Add monitoring? → Watchdog Setup
└── See what failed? → R&D Log
```

## ⚠️ Critical Warnings

> [!note] 🚨
> **NEVER USE:**
> - H.265/HEVC codec (causes kernel panics)
> - `KillMode=mixed` (creates zombie processes)
> - UDP transport (drops frames)
> - WiFi connection (unreliable for RTSP)
> - Legacy camera interface (incompatible)

> [!success] ✅
> **ALWAYS USE:**
> - H.264 codec with libav
> - `KillMode=control-group`
> - TCP transport only
> - Wired Ethernet
> - Standard camera interface

## 📈 Performance Metrics

### Expected Performance (v5.0 Config)

**Raspberry Pi 5:**

- CPU: 20-30% average
- Memory: 400-500MB
- Temperature: 55-60°C
- Network: 3-4 Mbps constant

**Frigate Server (with QSV):**

- CPU: 9-12% (was 100% without QSV)
- GPU: 3-4% utilization
- Memory: ~870MB
- Storage: ~32GB/day for 2 cameras

## 🔄 Version History

- **v5.0** (Sept 24, 2025) - Production hardened, all critical fixes
- **v4.0** - Had zombie process issues
- **v3.0** - Used H.265 (caused panics)
- **v2.0** - Initial dual camera support
- **v1.0** - Single camera prototype

## 📞 Support Information

- **System Admin:** Andrea
- **Documentation:** This Notion workspace
- **Backups:** `/home/skimlab/backups/`
- **Logs:** `/var/log/pi-monitor.log`

---

*Documentation Index v5.0 - Last Updated: September 24, 2025*
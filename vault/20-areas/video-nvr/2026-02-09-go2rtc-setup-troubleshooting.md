---
type: incident
area: video-nvr
status: done
status-note: "resolved"
tags: [troubleshooting, incident, go2rtc, raspberry-pi, configuration]
created: 2026-02-09
severity: high
---

# go2rtc Setup Troubleshooting — 2026-02-09

## Summary

Fresh Raspberry Pi 5 setup failed to produce working RTSP camera streams. Three separate issues were found and fixed before streams worked. This document records every problem, what caused it, and the exact working configuration.

---

## Issue #1: `rpicam-vid` Missing libav Codec Support

### Symptom

```
ERROR: *** Unrecognised codec libav ***
```

When running:
```bash
rpicam-vid --codec libav --width 640 --height 480 --framerate 15 --timeout 2000 -o /dev/null
```

Also confirmed by version output showing `libav:0`:
```
rpicam-apps capabilites: egl:0 qt:0 drm:1 libav:0
```

### Root Cause

Raspberry Pi OS Lite ships with `rpicam-apps-lite`, which is a stripped-down package that does **not** include the libav codec wrapper. The golden go2rtc config requires `--codec libav --libav-format h264`, which depends on this missing capability.

### What Was Installed (Broken)

```
rpicam-apps-lite    (transitional/stripped package)
rpicam-apps-core    (base framework only)
librpicam-app1      (shared library)
```

### Fix

Install the full `rpicam-apps` package, which replaces the lite version:

```bash
sudo apt install -y rpicam-apps
```

### Verification

```bash
rpicam-vid --version
# Must show: libav:1
```

After fix:
```
rpicam-apps capabilites: egl:1 qt:1 drm:1 libav:1
```

### Lesson

**Always install `rpicam-apps` (full), never `rpicam-apps-lite`** on surveillance Pis. Add this as the first step in the new Pi setup procedure, before configuring go2rtc.

---

## Issue #2: systemd Service — Inline Comments Break KillMode

### Symptom

```
Feb 09 06:57:45 pi1 systemd[1]: /etc/systemd/system/go2rtc.service:20: Failed to parse kill mode specification, ignoring: control-group    # MANDATORY - kills ALL child processes
```

The most critical setting in the entire service file (`KillMode=control-group`) was silently ignored.

### Root Cause

systemd does **NOT** support inline comments. This line:

```ini
KillMode=control-group    # MANDATORY - kills ALL child processes
```

systemd reads the entire string after `=` as the value, including `# MANDATORY - kills ALL child processes`. It fails to parse that as a valid kill mode and **falls back to the default**, which does NOT kill child processes.

### Why This Is Dangerous

Without `KillMode=control-group`:
- When go2rtc restarts, `rpicam-vid` child processes are **not terminated**
- Zombie `rpicam-vid` processes accumulate
- After several restarts, the system freezes completely
- SSH becomes unresponsive
- Only a hard power cycle recovers the Pi

### The Broken Config

```ini
KillMode=control-group    # MANDATORY - kills ALL child processes
```

### The Fixed Config

```ini
# CRITICAL: Kills ALL child processes (rpicam-vid) when service stops
KillMode=control-group
```

### Rule

**In systemd unit files, comments MUST be on their own line. Never put comments after a value on the same line.**

```ini
# ✅ CORRECT — comment on its own line
KillMode=control-group

# ❌ WRONG — inline comment breaks the value
KillMode=control-group    # this breaks it
```

---

## Issue #3: go2rtc YAML Config — Wrong `exec` Format

### Symptom

```
streams: unknown error
```

In go2rtc logs when requesting a stream. RTSP requests returned 404.

Streams showed `producers: null`:
```json
{"pi_cam_0":{"producers":null,"consumers":null},"pi_cam_1":{"producers":null,"consumers":null}}
```

### Root Cause

The go2rtc config used YAML multi-line block syntax (`exec:` as a key with `>` folding), which go2rtc does not correctly parse as an exec source:

```yaml
# ❌ BROKEN — go2rtc cannot parse this format
streams:
  pi_cam_0:
    exec: >
      rpicam-vid
      --codec libav
      --libav-format h264
      --width 1024
      --height 768
      ...
      --output -
```

go2rtc expects exec streams as a **single string value** prefixed with `exec:`:

```yaml
# ✅ WORKING — single-line string with exec: prefix
streams:
  pi_cam_0: "exec:rpicam-vid --codec libav --libav-format h264 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --timeout 0 --camera 0 --level 4.1 --profile high --output -"
```

### Additional Context

The previous (also broken) config piped rpicam-vid through ffmpeg:

```yaml
# ❌ ALSO BROKEN — forbidden ffmpeg pipe architecture
exec: >
  rpicam-vid ... -o -
  | ffmpeg -hide_banner -loglevel error
    -f h264 -i -
    -c copy
    -f rtsp rtsp://127.0.0.1:8554/pi_cam_0
```

This ffmpeg pipe approach is explicitly forbidden in the project constraints because it was proven unstable for 24/7 operation.

### Rule

**go2rtc exec streams must be a single quoted string starting with `exec:` — never use YAML multi-line blocks, and never pipe through ffmpeg.**

---

## The Working Configuration Files

### go2rtc.yaml (VERIFIED WORKING)

**Location:** `/opt/go2rtc/go2rtc.yaml`

```yaml
streams:
  pi_cam_0: "exec:rpicam-vid --codec libav --libav-format h264 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --timeout 0 --camera 0 --level 4.1 --profile high --output -"
  pi_cam_1: "exec:rpicam-vid --codec libav --libav-format h264 --width 1024 --height 768 --framerate 15 --bitrate 1500000 --inline --timeout 0 --camera 1 --level 4.1 --profile high --output -"

rtsp:
  listen: ":8554"

api:
  listen: ":1984"

log:
  level: info
```

### go2rtc.service (VERIFIED WORKING)

**Location:** `/etc/systemd/system/go2rtc.service`

```ini
[Unit]
Description=go2rtc RTSP Streaming Service (v5.0 Hardened)
Documentation=https://github.com/AlexxIT/go2rtc
After=network-online.target
Wants=network-online.target

[Service]
User=skimlab
Group=video
WorkingDirectory=/opt/go2rtc

# Wait 60 seconds after boot before starting cameras
ExecStartPre=/bin/sleep 60
ExecStart=/opt/go2rtc/go2rtc -config /opt/go2rtc/go2rtc.yaml

# Restart policy
Restart=always
RestartSec=5

# CRITICAL: Kills ALL child processes (rpicam-vid) when service stops
KillMode=control-group
KillSignal=SIGTERM
TimeoutStopSec=10

# Resource limits
CPUQuota=70%
MemoryMax=512M
MemorySwapMax=0

# Security
LimitNOFILE=4096
NoNewPrivileges=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=go2rtc

[Install]
WantedBy=multi-user.target
```

### Boot Config Additions (VERIFIED WORKING)

**Location:** Appended to `/boot/firmware/config.txt`

```ini
# Disable WiFi (using Ethernet only)
dtoverlay=disable-wifi

# Disable Bluetooth (not needed)
dtoverlay=disable-bt

# GPU memory for dual camera operation
gpu_mem=128

# Enable hardware watchdog (auto-reboot on freeze)
dtparam=watchdog=on
```

**Note:** `gpu_mem=128` is ignored on Pi 5 (uses dynamic allocation), but including it doesn't cause harm and maintains compatibility with Pi 4 if ever needed.

---

## Verification Commands (Run After Any Config Change)

```bash
# 1. Service is running without errors
sudo systemctl status go2rtc.service
# Expected: active (running), NO "Failed to parse" warnings

# 2. Both cameras streaming
ps aux | grep rpicam-vid | grep -v grep | wc -l
# Expected: 2

# 3. Streams accessible locally
curl http://localhost:1984/api/streams
# Expected: producers should NOT be null when streams are active

# 4. Streams accessible from NVR (run on e10)
ffmpeg -rtsp_transport tcp -i rtsp://192.168.0.11:8554/pi_cam_0 -frames:v 1 -f null - 2>&1 | tail -5
# Expected: "frame= 1" line, no errors

# 5. Temperature OK
vcgencmd measure_temp
# Expected: < 70°C

# 6. No throttling
vcgencmd get_throttled
# Expected: 0x0
```

---

## Three Rules to Never Break Again

1. **Install `rpicam-apps` (full), not `rpicam-apps-lite`** — lite lacks the libav codec required for H.264 streaming
2. **Never put comments on the same line as values in systemd files** — they break the value silently
3. **go2rtc exec streams must be single-line quoted strings** — YAML multi-line blocks and ffmpeg pipes both fail

---

## Related

- [[new-pi-setup|New Pi Setup]] - Updated with rpicam-apps installation step
- [[golden-go2rtc-config|Golden go2rtc Config]] - Fixed to use single-line exec format
- [[golden-systemd-service|Golden systemd Service]] - Fixed inline comment issue
- [[boot-config-ssh-lockout]] - Related incident from same day

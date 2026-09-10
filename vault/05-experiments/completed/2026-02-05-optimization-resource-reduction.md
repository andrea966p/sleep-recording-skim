---
date: 2026-02-05
status: testing
type: optimization
components:
  - raspberry-pi
  - frigate
  - monitoring
---

# Resource Reduction Optimization

## Context

Used AI coding agent (Cursor/Antigravity) to optimize the public repository configurations. Goal: reduce Raspberry Pi CPU/memory usage, improve stability, and streamline data flow.

Primary focus: eliminate redundant processing on Pi 5 camera nodes.

## Changes Made

### 1. go2rtc.yaml - Remove ffmpeg intermediate process

**Location:** `/opt/go2rtc/go2rtc.yaml` on Pi (192.168.0.11)

**Current architecture:**
```
rpicam-vid → ffmpeg → RTSP push to localhost → go2rtc
```

**New architecture:**
```
rpicam-vid → stdout → go2rtc (direct consumption)
```

**Expected benefit:** Eliminate one ffmpeg process per camera, saving ~5-10% CPU and memory per camera.

**Risk:** Significant architectural change. Relies on go2rtc's ability to consume rpicam-vid output directly from stdout.

### 2. frigate-config.yml - Buffer documentation

**Location:** `/srv/frigate/config/config.yml` on NVR (192.168.0.50)

**Change:** Added detailed comments explaining the 512KB buffer_size rationale for TCP transport stability.

**Expected benefit:** Better configuration documentation, validation that large buffers are intentional for jitter handling.

### 3. watchdog.sh - Enhanced monitoring

**Location:** `~/watchdog.sh` on Pi (192.168.0.11)

**Changes:**
- **Precision logging:** Changed timestamps to ISO 8601 format for better debugging
- **Resiliency:** Added 3-retry mechanism for API availability checks
- **False positive prevention:** Prevents restart during temporary glitches

**Expected benefit:** More reliable monitoring, fewer false alarms, better debugging capability.

## Baseline Metrics (Before Changes)

Record before deploying:

- [ ] Pi CPU usage: __%
- [ ] Pi memory usage: __MB / 8GB
- [ ] Pi temperature: __°C
- [ ] Number of rpicam-vid processes: __
- [ ] Number of ffmpeg processes: __
- [ ] NVR CPU usage: __%
- [ ] NVR memory usage: __MB
- [ ] Stream latency: __ seconds
- [ ] Watchdog false restarts (last 24h): __

## Deployment Steps

### On Raspberry Pi (192.168.0.11)

```bash
# Backup current configs
sudo cp /opt/go2rtc/go2rtc.yaml /opt/go2rtc/go2rtc.yaml.backup-2026-02-05
cp ~/watchdog.sh ~/watchdog.sh.backup-2026-02-05

# Deploy new configs
sudo cp /path/to/new/go2rtc.yaml /opt/go2rtc/go2rtc.yaml
cp /path/to/new/watchdog.sh ~/watchdog.sh

# Restart services
sudo systemctl restart go2rtc

# Verify streams
curl http://localhost:1984/api/streams
```

### On NVR (192.168.0.50)

```bash
# Backup current config
cp /srv/frigate/config/config.yml /srv/frigate/config/config.yml.backup-2026-02-05

# Deploy new config
cp /path/to/new/frigate-config.yml /srv/frigate/config/config.yml

# Restart Frigate
docker compose restart frigate
```

## Testing Plan

### Immediate Checks (0-1 hour)
- [ ] Streams appear online at http://192.168.0.11:1984/api/streams
- [ ] Frigate UI shows both cameras active
- [ ] No ffmpeg processes visible on Pi: `ps aux | grep ffmpeg`
- [ ] rpicam-vid processes running: `ps aux | grep rpicam-vid`
- [ ] Video playback works in Frigate UI
- [ ] Temperature stable: `vcgencmd measure_temp`

### Short-term Monitoring (24 hours)
- [ ] No unexpected restarts in `journalctl -u go2rtc`
- [ ] No stream disconnections in Frigate
- [ ] Watchdog log clean: `tail -f ~/watchdog.log`
- [ ] Recordings successfully saved

### Long-term Validation (7 days)
- [ ] System stability maintained
- [ ] No data loss
- [ ] Performance improvement confirmed

## Results (After 24 hours)

**Outcome:** The direct stdout architecture (rpicam-vid → go2rtc, no ffmpeg) was adopted as the production configuration in golden-go2rtc-config v5.0. The ffmpeg intermediate process was successfully eliminated.

**Performance Metrics:**
- ffmpeg processes eliminated: 2 (was 2, now 0)
- Architecture simplified to direct pipe from rpicam-vid to go2rtc

**Stability:**
- System has been running on this architecture since 2026-02-09
- No ffmpeg-related instability observed

**Issues encountered:**
- None related to the direct stdout change itself
- Separate boot-crash incident (2026-02-10) was unrelated to this architecture change

## Decision

- [x] **Keep all changes** → Golden configs updated, experiment completed

The direct stdout architecture is now the production standard documented in [[golden-go2rtc-config]] v5.1.

## Lessons Learned

- The ffmpeg intermediate process was unnecessary overhead. rpicam-vid's `--output -` pipes H.264 bitstream directly to go2rtc's pipe transport.
- Architectural simplification (fewer processes) improves reliability for 24/7 operation.
- Always validate that the "new" architecture isn't already what you're running before creating an experiment.

## Links

- [[golden-go2rtc-config]]
- [[golden-systemd-service]]
- [[docker-compose]]
- [[config-yml]]
- [[Daily Journal/2026-02/2026-02-05]]
- Public repo: https://github.com/andrea966p/neurosurveillance-system

## Tags

#experiment #optimization #performance #raspberry-pi #go2rtc #frigate

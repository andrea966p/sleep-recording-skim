---
tags: [meeting, progress, professor]
date: 2026-03-12
status: draft
---

# NeuroSurveillance — Progress Meeting Brief

**Date:** March 12, 2026
**Prepared by:** Andrea

---

## 1. System Overview — What We Built

An automated, multi-camera video surveillance system for neuroscience sleep research that **synchronizes video recording with EEG/EMG acquisition** — fully open-source, low-cost, and reproducible.

### Architecture

```
┌─────────────────┐    ┌─────────────────┐
│  Raspberry Pi 1 │    │  Raspberry Pi 2 │
│  192.168.0.11   │    │  192.168.0.12   │
│  pi_cam_0       │    │  pi_cam_2       │
│  pi_cam_1       │    │  pi_cam_3       │
│  go2rtc v1.9.14 │    │  go2rtc v1.9.14 │
└───────┬─────────┘    └───────┬─────────┘
        │  RTSP H.264          │  RTSP H.264
        │  1024x768 @15fps     │  1024x768 @15fps
        └──────────┬───────────┘
                   │
        ┌──────────▼──────────┐
        │   ASUS NUC 14 Pro   │
        │   192.168.0.50      │
        │                     │
        │  Frigate NVR 0.16.1 │ ← Intel QSV HW accel
        │  Mosquitto MQTT     │ ← Message broker for recording control
        │  Session Daemon     │ ← Python 3.12, Flask
        │  Desktop UI (Tauri) │ ← React 19, TypeScript
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  NeuroNexus Radiens │
        │  (AllegoClient API) │
        │  EEG/EMG headstage  │
        └─────────────────────┘
```

### Key Capabilities

| Feature | Detail |
|---------|--------|
| **Cameras** | 4 cameras across 2 Raspberry Pi 5 nodes (2 per Pi) |
| **Resolution** | 1024x768 @ 15fps, H.264 encoding |
| **Storage** | ~45 GB/camera/day, 7-day retention on 1.9 TB NVMe |
| **Automation** | Daemon polls Radiens every 1s; detects R_ON/R_OFF transitions |
| **Synchronization** | Video start/stop locked to EEG recording start/stop (~1s latency, ±2s buffer on export) |
| **Multi-chamber** | Independent metadata per chamber (mouse ID, recording type, user) |
| **File organization** | Auto-named exports: `{timestamp}_{mouseID}_{type}.mp4` organized by user/mouse/date |
| **Manual recording** | Frigate UI click → daemon auto-detects, exports, organizes |
| **Desktop UI** | Tauri app with live status, session setup, camera preview per chamber |
| **Hardware acceleration** | Intel Arc iGPU (QSV) for H.264 decode on NVR |

### Hardware Cost Estimate

| Component                                    | Unit Cost | Qty | Subtotal |
| -------------------------------------------- | --------- | --- | -------- |
| Raspberry Pi 5 (8 GB)                        | $100      | 2   | $200     |
| Camera modules                               | $7        | 4   | $28      |
| PoE HAT (Waveshare)                          | $18       | 2   | $36      |
| Ethernet cables                              | $5        | 2   | $10      |
| ASUS NUC 14 Pro (Intel Ultra 5, 32 GB, 2 TB) | $800      | 1   | $800     |
| Network switch + cabling                     | $100      | 1   | $100     |
| **Total**                                    |           |     | **~$1,174** |

Compare: commercial lab video systems (Noldus EthoVision, Clever Sys) cost $5,000–$20,000+ per setup.

---

## 2. Development Timeline

| Date       | Milestone                                                                 |
| ---------- | ------------------------------------------------------------------------- |
| **Feb 4**  | Obsidian vault setup, Notion migration                                    |
| **Feb 5**  | First streaming config; H.265 failure discovered (kernel panics)          |
| **Feb 9**  | go2rtc config stabilized; repo workflow established                       |
| **Feb 11** | MPEG-TS container adopted (v5.2); watchdog monitoring deployed            |
| **Feb 12** | Frigate NVR deployed on ASUS NUC; first recording test successful         |
| **Feb 19** | Pi found dead after 6-day holiday — PMIC fault diagnosed, EEPROM hardened |
| **Feb 20** | Session daemon architecture designed and coded                            |
| **Feb 23** | Desktop UI built (Tauri + React); daemon deployed as systemd service      |
| **Mar 6**  | Export corruption bug fixed (race condition in MP4 write)                 |
| **Mar 7**  | Second Pi deployed — system expanded to 4 cameras                         |
| **Mar 8**  | Full 4-camera support verified across all layers                          |
| **Mar 9**  | Docker packages pinned to prevent unintended Frigate restarts             |

**Total development time: ~5 weeks** (part-time, single developer)

---

## 3. Struggles & Challenges Encountered

### 3.1 Hardware Failures — Raspberry Pi 5 PoE Instability

**The biggest operational challenge.** Three separate incidents of Pi becoming completely unresponsive:

| Date | Incident | Root Cause |
|------|----------|-----------|
| Feb 13 | Pi went offline after physical cable disturbance | PoE HAT power transient |
| Feb 19 | Pi found dead after 6 days (Lunar New Year) | PMIC latch-up fault — `PSU_MAX_CURRENT` at default 5000 mA too aggressive for Waveshare PoE HAT |
| Feb 24 | Pi unreachable again, auto-reboot failed | Double-crash scenario — PMIC latched off, watchdog couldn't recover |

**Resolution:** EEPROM boot config hardened (`PSU_MAX_CURRENT=5000`, `POWER_OFF_ON_HALT=1`), crash-canary monitoring scripts deployed, persistent journaling enabled for post-mortem analysis. **Since applying the EEPROM fix, no further PoE incidents have occurred (stable for 2+ weeks as of March 12).**

**Lesson:** Consumer-grade PoE HATs for Pi 5 require EEPROM tuning for reliable operation. The default power negotiation settings are too aggressive for the Waveshare PoE HAT.

### 3.2 H.265 Encoding — Complete Failure on Pi 5

Attempted H.265 for 50% storage savings. Result: kernel panics, 90%+ CPU, system freeze within 15 minutes. **H.265 hardware encoding on Pi 5 is fundamentally unstable** — the `rpicam-vid` H.265 codec causes resource exhaustion. Reverted to H.264 (`--codec libav --libav-format h264`). This is now a hard rule in all documentation.

### 3.3 MP4 Export Corruption — Race Condition

A 19-hour (15 GB) recording was exported as a corrupted, unplayable MP4. Root cause: the daemon's `wait_for_export()` method wasn't checking Frigate's `in_progress` flag — files were moved while `ffmpeg` was still writing the MP4 `moov` atom (the file index stored at the end of the file). **Data was unrecoverable.** Fixed by polling until `in_progress: False`.

### 3.4 Zombie Processes & SSH Hangs

`rpicam-vid` child processes survived parent go2rtc restarts, creating zombie processes that locked the camera device. SSH sessions would freeze when connecting to an affected Pi. Fixed with `KillMode=control-group` in systemd (kills all processes in the cgroup, not just the main PID).

### 3.5 Docker/Frigate Restart Behavior

System-wide `apt upgrade` updated Docker, which restarted Frigate, which immediately started recording all 4 cameras (Frigate's config default is `record.enabled: true`). Wasted storage with orphaned recordings. Solved by pinning Docker packages in `/etc/apt/apt.conf.d/50unattended-upgrades`.

### 3.6 Session Daemon Integration

- **Radiens authentication:** AllegoClient changed auth behavior between versions, causing connection failures. Required careful mode detection.
- **CORS issues:** Tauri desktop app (localhost origin) was blocked by Flask's default CORS policy. Required `flask-cors` configuration.
- **Manual recording detection:** Distinguishing daemon-initiated vs. user-initiated recording state changes in MQTT required a two-stage filter (expected state tracking + transition detection) plus a 10-second startup grace period.

---

## 4. Current System Status

**Fully operational** as of March 9, 2026.

- 4 cameras streaming across 2 Raspberry Pi nodes
- Frigate recording with Intel QSV hardware acceleration
- Session daemon: MQTT connected, Radiens polling active
- Desktop UI deployed and functional
- All monitoring scripts active (watchdog, crash-canary, pi-monitor)
- 38 vault documentation pages covering procedures, incidents, and architecture

---

## 5. What's Next

### Short-term (Next 2-4 Weeks)

| Priority | Task | Rationale |
|----------|------|-----------|
| **High** | Post-export file integrity check (`ffprobe` validation) | Prevent silent corruption — learned from the Mar 6 incident |
| **Done** | ~~NAS transfer via Tailscale~~ | Automated export transfer to Synology NAS configured and operational |
| **Done** | ~~Add more lab members to the system~~ | Lab member list updated with additional users |

### Medium-term (1-3 Months)

| Task | Detail |
|------|--------|
| **Automated sleep scoring (EEG/EMG)** | Collaboration with Prof. Kim Daewook's lab — automated sleep stage scoring model from EEG and EMG signals |
| **Video-based sleep/wake classification** | Apply [FERAL](https://github.com/Skovorp/feral) (Skovorodnikov et al., 2025, bioRxiv) — a video-understanding system that maps raw video directly to behavioral labels without pose estimation. Train on labeled sleep/wake frames for simple binary classification from video alone — non-invasive, no surgery required; complements EEG-based scoring |
| **Video-EEG temporal alignment validation** | Measure actual synchronization latency between Radiens R_ON and first Frigate frame |
| **PostgreSQL session database** | Replace JSON sidecar files with structured database for querying across experiments |
| **Multi-headstage support** | Enable independent Radiens instances per chamber for true independent recording control |

### Long-term (3-6 Months)

| Task | Detail |
|------|--------|
| **NWB (Neurodata Without Borders) export** | Package video + EEG/EMG into NWB format for DANDI archive submission |
| **Dual-modality sleep scoring pipeline** | Combine EEG/EMG scoring (Kim lab collaboration) with FERAL video classification for cross-validated sleep staging — ultimately enabling surgery-free sleep assessment for cohorts without EEG implants |
| **System replication guide** | Package the full setup as a reproducible methods paper |

---

## 6. Future Applications

### 6.1 Within the Lab

- **Expanded sleep studies:** Scale to 8+ chambers by adding more Pi nodes (system architecture already supports dynamic camera counts)
- **Surgery-free sleep screening:** Train FERAL on labeled sleep/wake video to classify directly from raw footage — no pose estimation, no EEG implants. Ideal for large-scale phenotyping or pre-screening cohorts before committing to surgery
- **Sleep deprivation monitoring:** Real-time video analysis could detect sleep onset for gentle handling protocols
- **Circadian rhythm studies:** Continuous multi-day video + EEG with automated sleep/wake scoring
- **Drug studies:** Before/after video behavioral analysis correlated with EEG biomarkers

### 6.2 Beyond Sleep Research

- **General rodent behavior phenotyping:** Home-cage monitoring without the disruptions of specialized test setups
- **Seizure detection:** Video + EEG correlation for epilepsy models
- **Pain behavior assessment:** Automated grimace scale scoring from video
- **Social behavior:** Multi-animal interaction tracking in shared chambers
- **Any lab needing synchronized multi-modal recording:** The Radiens-triggered architecture generalizes to any "start video when acquisition starts" use case

### 6.3 Community Impact

- **Cost democratization:** ~$1,174 vs. $15,000+ commercial systems
- **Reproducibility:** Fully documented, open-source, version-controlled
- **Modularity:** Swap cameras, NVR software, or acquisition system independently

---

## 7. Publication Angle — How This Fits in the Literature

### 7.1 The Gap

Current approaches to synchronized video-EEG in rodent sleep research fall into three categories:

1. **Commercial systems** (Noldus EthoVision, Clever Sys HomeCageScan, Pinnacle Technology):
   - Expensive ($5K–$20K+), closed-source, vendor lock-in
   - Limited customization for lab-specific workflows

2. **Custom-built academic systems:**
   - [MouseVUER](https://www.nature.com/articles/s41598-024-52788-9) (2024, Scientific Reports): open-source home-cage monitoring with depth cameras, but no EEG synchronization
   - [OpenVEEG](https://pmc.ncbi.nlm.nih.gov/articles/PMC6087497/) (2018, PMC): millisecond-synchronized video-EEG, but requires custom hardware and specific camera models
   - [SIESTA](https://pmc.ncbi.nlm.nih.gov/articles/PMC12263331/) (2025): automated sleep staging from ECoG/EMG, but no video integration
   - [SAGER](https://www.mdpi.com/1424-8220/25/3/921) (2025): single-channel EEG sleep scoring, no video

3. **General-purpose open-source NVR:**
   - Frigate NVR: powerful but designed for home security, not scientific use
   - No existing integration with electrophysiology acquisition systems

**Our system fills the gap** between expensive commercial solutions and DIY academic rigs by combining commodity hardware (Raspberry Pi, consumer NVR software) with a custom integration layer (session daemon) that bridges video recording to electrophysiology acquisition.

### 7.2 Novel Contributions

| Contribution | Significance |
|-------------|-------------|
| **Radiens API-triggered video synchronization** | First open-source system to automatically synchronize Frigate NVR recording with NeuroNexus electrophysiology sessions via the AllegoClient Python API |
| **Multi-chamber independent metadata** | Each recording chamber maintains its own experimental context (mouse ID, recording type), enabling parallel experiments |
| **MQTT-based recording orchestration** | Lightweight pub/sub control of multiple cameras without complex coupling |
| **Fail-safe design** | Recording defaults to ON — if the daemon crashes, Frigate keeps recording (extra footage, never data loss) |
| **Complete operational documentation** | 38-page Obsidian vault with incident reports, golden configs, and replication procedures — unusual level of transparency for methods papers |
| **Cost reduction** | ~$1,174 total vs. $5K–$20K for comparable commercial systems |
| **Reproducibility** | Fully version-controlled code + configs + documentation; designed for replication by other labs |

### 7.3 Suggested Publication Format

**Methods/Technical Note paper** in one of:

| Journal | Fit | Impact Factor |
|---------|-----|---------------|
| **Journal of Neuroscience Methods** | Primary target — methods papers for neuroscience | 2.7 |
| **HardwareX** (Elsevier) | Open-source scientific hardware; includes build instructions | 2.8 |
| **Scientific Reports** (Nature) | Broad audience; MouseVUER published here | 3.8 |
| **Frontiers in Neuroscience** | Methods & tools section | 3.2 |
| **eLife** (Tools & Resources) | High visibility; Spyglass framework published here | 6.4 |
| **JOSS** (Journal of Open Source Software) | Software-focused; peer-reviewed, citable | — |

### 7.4 Suggested Paper Structure

1. **Introduction:** The need for affordable, synchronized video-EEG in rodent sleep research
2. **System Design:** Architecture, hardware, software components (with cost table)
3. **Implementation:** Streaming pipeline, MQTT orchestration, session management, export workflow
4. **Validation:**
   - Synchronization latency measurement (Radiens R_ON → first video frame)
   - Export integrity verification
   - Long-term stability data (uptime logs, incident recovery)
   - Storage efficiency metrics (actual GB/camera/day)
5. **Case Study:** Example sleep recording session with EEG + video correlation
6. **Discussion:** Limitations (~1s sync latency vs. OpenVEEG's ms-level, PoE EEPROM tuning required), scalability, comparison to commercial systems
7. **Data & Code Availability:** GitHub repo, Obsidian documentation vault, NWB export (future)

### 7.5 Key References

- [MouseVUER (2024)](https://www.nature.com/articles/s41598-024-52788-9) — Open-source home-cage monitoring (video only, no EEG sync)
- [OpenVEEG (2018)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6087497/) — Millisecond-synchronized video-EEG (custom hardware required)
- [SIESTA (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12263331/) — Automated rodent sleep staging from ECoG/EMG
- [SAGER (2025)](https://www.mdpi.com/1424-8220/25/3/921) — Single-channel EEG vigilance state classification
- [Spyglass (2024, eLife)](https://pubmed.ncbi.nlm.nih.gov/38328074/) — Reproducible neuroscience data management framework
- [Lightning Pose (2024, Nature Methods)](https://www.nature.com/articles/s41592-024-02319-1) — Semi-supervised animal pose estimation
- [FERAL (2025, bioRxiv)](https://www.biorxiv.org/content/10.1101/2025.11.16.688666v1) — Video-understanding system for direct video-to-behavior mapping without pose estimation (Skovorodnikov et al., Rockefeller University)
- [High-throughput visual sleep staging (2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8842275/) — ML-based sleep scoring from video in mice

---

## 8. Discussion Points for Professor

1. **Publication timing:** Should we publish the infrastructure paper now, or wait until we have validation data (sync latency, long-term stability metrics)?
2. **Scope:** Methods paper (system description) vs. full research paper (system + sleep study results)?
3. **Kim lab collaboration scope:** How tightly should the EEG/EMG sleep scoring model be integrated with our video infrastructure for the paper?
4. **FERAL integration:** Video-based sleep/wake classification without surgery — should this be part of the methods paper or a separate follow-up study?
5. **NWB integration priority:** Should we invest in Neurodata Without Borders export for data sharing before publishing?


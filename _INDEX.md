---
tags: [index, navigation, home]
---

# NeuroSurveillance System Documentation

> [!abstract] Start here
> New to this vault? Read [[SYSTEM-OVERVIEW|the one-page system overview]] first — it explains what NeuroSurveillance is, what changed in the recent stabilization sprint, and where to read more.
> For a deeper Q&A walkthrough with durability guarantees and a glossary: [[01-infrastructure/system-overview|the deeper overview]].
> Onboarding a new lab member: [[02-procedures/new-researcher-onboarding|new-researcher-onboarding]].

> [!info] Quick Access
> | Service | URL |
> |---------|-----|
> | **Frigate** | http://192.168.0.50:5000 |
> | **go2rtc (Pi 1)** | http://192.168.0.11:1984 |
> | **go2rtc (Pi 2)** | http://192.168.0.12:1984 |
> | **Session Daemon** | http://127.0.0.1:8585 (NVR localhost) |
> | **Netdata (NVR)** | http://192.168.0.50:19999 |
> | **Uptime Kuma** | http://192.168.0.50:3001 |
> | **Status Page** | http://192.168.0.50:3001/status/neurosurveillance |
> | **Config** | [[00-config/production-values]] |
> | **Tasks** | [[00-config/task-dashboard]] |

---

## Documentation Map

### [[00-config/production-values|Configuration]]
Production IPs, usernames, paths, and settings.

### Infrastructure

**Raspberry Pi:**
- [[01-infrastructure/raspberry-pi/golden-go2rtc-config|go2rtc Config]]
- [[01-infrastructure/raspberry-pi/golden-systemd-service|systemd Service]]
- [[01-infrastructure/raspberry-pi/golden-boot-config|Boot Hardening]]
- [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog & Monitoring]]

**Frigate NVR:**
- [[01-infrastructure/frigate/docker-compose|Docker Compose]]
- [[01-infrastructure/frigate/config-yml|config.yml]]

**Sleep recording (Intan RHD2216 + Allego) — operator docs:**
- [[02-procedures/sleep-recording-operator-manual|⭐ Sleep-Recording Operator Manual — START HERE, ordered phases from assembly to EEG/EMG analysis]]
- [[06-references/radiens-software-reference|⭐ Radiens Software — PRIMARY Reference (Allego + Videre)]] — **main software reference; embeds the full 177-page NeuroNexus manual + our load-bearing facts (mode, channel select, no in-GUI rename)**
- [[06-references/intan-rhd2216-reference|⭐ Intan RHD2216 Chip Reference — bipolar, ±5 mV rail, filters (datasheet-cited)]]
- ⭐⭐ [[02-procedures/CANONICAL-allego-channel-selection|CANONICAL — which Allego channels to select. SETTLED.]] — **select `/1`,`/2`,`/33`,`/34` per port. 16 channels for 8 mice.** Proven from the datasheet, the recorded metadata, and a measurement of all 64 slots on all 4 ports. **If any other page disagrees, this one wins.**
- [[02-procedures/signal-mapping-guide|⭐ Signal Mapping Guide — which channel is which electrode (EEG/EMG, step-by-step)]]
- [[02-procedures/signal-quality-and-grounding|⭐ Signal Quality & Grounding — fix the ground, then judge the signal]]
- [[02-procedures/grounding-reference-noise-concepts|Grounding vs Reference vs Tissue/Environmental Noise — concepts + slip-ring color defect]]
- [[02-procedures/eeg-emg-data-guide|EEG/EMG Data Guide — read by eye first, then analyze in Python]]
- [[02-procedures/rig-assembly-guide|Rig Assembly Guide — connect the full recording chain]]
- [[02-procedures/multimeter-guide|Multimeter Guide (Harden 661002) — power/continuity/short tests]]
- ⏳⭐ [[02-procedures/dmm-eeg-path-continuity-test|DMM continuity test on the EEG path — THE FREE TIER-1 BENCH TEST]] — **owed since 2026-08-02, run it before concluding anything about the implants.** No animal contact. Pads 2/3 (EMG) are the built-in control; includes the **slip-ring rotation test** that a static probe cannot replace
- [[02-procedures/allego-monitor-guide|Allego Monitor Tab Guide]]
- [[02-procedures/allego-sampling-rate|Allego Sampling Rate — 1 kHz min; 128–256 Hz = offline decimate]]
- [[02-procedures/allego-presets-workspace|Allego Presets & Save Workspace]]
- [[02-procedures/intan-headstage-troubleshooting|Intan Headstage Troubleshooting — symptom → cause → fix]]
- [[02-procedures/first-headstage-connection|First Headstage Connection — bring-up + channel map]] ✅ resolved 2026-06-19

**EEG data analysis (everything AFTER the recording exists):**
- ⭐⭐ [[02-procedures/eeg-data-analysis/_eeg-analysis-hub|START HERE — EEG data analysis]] — the four commands, what each stage decides, the four rules you must not break. **The only page that says what to run.**
- ⭐ [[02-procedures/eeg-data-analysis/pipeline/README|Pipeline operating manual]] — every stage in detail, every threshold with its provenance
- ⭐ [[02-procedures/eeg-data-analysis/analysis-methods-and-justification|Methods and justification]] — what is standard practice and what we added, with citations. **The one to hand to the professor.**
- 📖 [[06-references/eeg-analysis-glossary|Analysis glossary — every term and parameter in plain words]] — `nperseg`, `r@1min`, `Wn`, `DIRTY`, `ZT`, Otsu, block, rms, EDF. Search it when a word blocks you.
- 🔧 [[03-troubleshooting/symptoms/eeg-analysis-problems|Analysis troubleshooting — symptom lookup]] — including the failures that are **silent** (theta zeroed by `nperseg`, persistence measured across contact gaps)

**Hardware Sync (XDAQ GPIO):**
- [[01-infrastructure/hardware-sync/xdaq-core-gen1-ubuntu-driver|⭐ XDAQ Core (Gen-1) — Ubuntu Driver Setup + Verified State (2026-05-29)]] — **current source of truth; supersedes Core2 assumptions below**
- [[01-infrastructure/hardware-sync/overview|Overview & Architecture]] ⚠️ Core2-era
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide & BOM]]
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service (Golden Config)]]
- [[01-infrastructure/hardware-sync/radiens-api-reference|Radiens API — Digital I/O Reference]]
- [[01-infrastructure/hardware-sync/xdaq-core2-manual-reference|XDAQ Core2 Manual Reference (authoritative pinout + specs)]]
- [[01-infrastructure/hardware-sync/kontex-developer-portal-notes|Kontex Developer Portal Notes (libxdaq / pylibxdaq / Linux Thunderbolt)]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]

**Vendor Correspondence:**
- [[01-infrastructure/vendor-correspondence/kontex-call-confirmation-email-2026-07-29|Kontex — 2026-07-29 call confirmation + advance questions (SENT 2026-07-28)]]
- [[01-infrastructure/vendor-correspondence/neuronexus-inquiry-email|NeuroNexus / Kontex Inquiry & Replies]]
- [[01-infrastructure/vendor-correspondence/openephys-inquiry-email|Open Ephys Inquiry & Reply (Margarida)]]

**Session Daemon:**
- [[01-infrastructure/system-overview|System Overview — Q&A and glossary]]
- [[01-infrastructure/session-daemon/architecture|Architecture & Design]]
- [[01-infrastructure/session-daemon/session-journal|Session Journal — WAL (added 2026-05-23)]]
- [[01-infrastructure/session-daemon/reconciler|Reconciler — nightly WAL ↔ Frigate cross-check (added 2026-05-24)]]
- [[01-infrastructure/session-daemon/frontend-reference|Frontend Reference]]
- [[01-infrastructure/session-daemon/session-service|Systemd Service]]

**Monitoring & Alerting:**
- [[01-infrastructure/netdata/nvr-alerts-config|Netdata NVR Alerts (Golden Config)]]
- [[02-procedures/installation/monitoring-setup|Monitoring Setup Procedure]]
- [[02-procedures/installation/watchdog-slack-bridge|Watchdog → Slack Bridge (added 2026-05-25)]]
- [[03-troubleshooting/emergency-runbook|Emergency Runbook — first 10 min]]

### Procedures
- 🔴⭐ [[02-procedures/electrode-connection-state-test|Electrode connection state test — OPEN vs SHORTED vs WORKING]] — **the no-wire control method (2026-07-31).** Read before judging any electrode by impedance again.
- [[02-procedures/installation/new-pi-setup|New Pi Setup]]
- [[02-procedures/session-recording-workflow|Session Recording Workflow]]
- [[02-procedures/hardware-sync-setup|Hardware Sync Setup Procedure]]
- [[02-procedures/installation/storage-management-implementation|Storage Management System]] ✅
- [[02-procedures/new-researcher-onboarding|New Researcher Onboarding]] — day-0 access + first-recording walkthrough
- [[02-procedures/bus-factor-runbook|Bus-Factor Runbook]] — "Andrea is unreachable" emergency operator guide (added 2026-05-28)

### Troubleshooting

**By Symptom:**
- [[03-troubleshooting/symptoms/no-frames-received|No frames received]]
- [[03-troubleshooting/symptoms/system-freeze-ssh-hang|System freeze / SSH hang]]
- [[03-troubleshooting/symptoms/frigate-high-cpu|Frigate 100% CPU]]
- [[03-troubleshooting/symptoms/docker-memory-crash|Docker memory crash]]
- [[03-troubleshooting/symptoms/allego-iir-filter-design-errors|Allego IIR filter design errors on Monitor band change]] — cosmetic, DEFERRED, does not affect recording
- ⭐ [[03-troubleshooting/symptoms/eeg-analysis-problems|EEG analysis problems — symptom lookup]] — wrong Python, missing mice, wrong day folder, blank EDF, **plus the two SILENT failures**: `nperseg` zeroing theta, and persistence measured across contact gaps

**Incident Log:**
- [[03-troubleshooting/incidents/|Incidents]]
- [[03-troubleshooting/incidents/2026-02-23-session-daemon-radiens-auth-cors|2026-02-23 Session Daemon Auth + CORS]]

### 📓 Daily Journal
- ⭐ [[04-journal/_JOURNAL-INDEX|Journal Index — chronological master navigator]] — **every day in date order.** The journal records what happened and links down into the detail notes. Start here to navigate by time rather than by topic.

### Experiments
**EEG runs and results — read these for the current scientific picture:**
- 📄 [[05-experiments/completed/2026-08-06-rig-status-for-professor|2026-08-06 — RIG STATUS FOR THE PROFESSOR]] — **the handout.** Part 0 is a paste-ready short version; the rest is capacity vs yield, the method and why it changed, figures, statistics, interpretation, and what is still open.
- ⭐⭐⭐ [[05-experiments/completed/2026-08-06-fleet-duty-cycle-census|2026-08-06 — WE FINALLY GOT A NEGATIVE CONTROL, AND OUR PASS MARK WAS TOO GENEROUS]] — **START HERE, newest.** The A2 position holds a **cut cable with no mouse**; it passed the 2 MΩ test **22%** of the time, and so do 2,240 readings from **wire-free amplifier inputs** (`/3`-`/16`, `/35`-`/48`). Pass mark moved to **0.5 MΩ** (floor 3.1%). Re-scored, **only 4 of 14 channels beat an empty cable ⇒ the rig records 1 animal of 8.** ⭐ A mouse given **16 days of recovery** before tethering scored **40/40 with zero flips**, but it also got a new soldered tether, so **two variables changed at once**. ✅ Duty cycle **reproduces across days** (D2 27.5% → 30%).
- ⭐⭐⭐ [[05-experiments/active/2026-08-06-recording-data-quality-preregistration|2026-08-06 — THE RECORDING AGREES: ONE MOUSE OF EIGHT HAS EEG]] — pre-registered before the data existed. **B1 99.7% usable, everyone else 0.0% EEG.** 🔴 **Filtering a bare wire yields a median 69 µV of convincing fake EEG**, so trace appearance is never evidence; classify by **spectral slope** instead (B1 −2.15 vs a floor range of −1.10 to −0.04). §10 and §11 are a **plain-language walkthrough of the whole method and both figures**.
- ⭐⭐ [[02-procedures/eeg-artefact-and-railing-rejection-policy|artefact and railing rejection policy]] — reject at **epoch** level, never animal level, **but only after checking the surviving clean epochs still have real spectral shape**. 🔴 On this rig **railing is the open-electrode signature, not movement** — the no-mouse position rails 100% of the time. Always state **samples vs epochs**.
- ⭐⭐⭐ [[05-experiments/active/2026-08-05-tether-comparison|2026-08-05 — A SOLDERED TETHER TOOK THE DUTY CYCLE FROM 45% TO 100%]] — **START HERE, newest.** B1's EEG went 9/20 → **20/20** connected (p = 0.0001) and its EMG 20% → 75%, with zero flips and a worst reading of 1.341 MΩ against 9.089. Concurrent controls in a second animal did **not** improve, so it is not drift. ⚠️ The swap bundled tether construction, connector re-seating and anaesthesia, so **the cause is not isolated**. 🔴 **B1 died under isoflurane the same evening; colony n = 7 and the slip-ring comparison is permanently lost.** Sweeps are now **automated** and the unit of measurement is a **duty cycle**, never a single reading.
- ⭐ [[05-experiments/completed/2026-08-05-unipolar-lfp-mouse-reference|2026-08-05 — the unipolar LFP mouse, a working reference prep]] — different surgery, no tether, no slip ring: **six live sites at once**, scorable EEG/EMG/LFP, first unambiguous EMG on the project. ⚠️ Changes five variables at once, so it assigns no cause. Also: impedance thresholds do **not** transfer between preps.
- ⭐⭐⭐ [[05-experiments/completed/2026-08-04-movement-dependent-contact|2026-08-04 — THE ELECTRODES ARE GOOD. THE CONTACT IS INTERMITTENT. The trigger is unknown]] — **START HERE.** B1's EEG hit **0.052 MΩ**, the best ever recorded here and inside the published 10-50 kΩ band, and **D2 recovered completely from fully open**, so the electrodes and implants are **good** and **NO SURGERY** is warranted. But B1's EEG read 6.236, 0.052, 8.649 and 0.177 MΩ across 23 minutes, so **a single sweep cannot rank or screen a channel**. ⚠️ A movement explanation was proposed and **disproved the same day**. (Superseded as the entry point by the 2026-08-05 tether result above; still the reference for why the electrodes are exonerated.)
- ⭐⭐ [[02-procedures/dmm-eeg-path-continuity-test|the DMM continuity test]] — ✅ **CLOSED 2026-08-04**, passed **fleet-wide**: pads, joints, shorts and 360° rotation all clean. Boards and solder exonerated. Do not run it again.
- [[06-references/impedance-sweep-register|impedance sweep register]] — all 14 sweeps, foldered by date, with the full 2026-08-04 session timeline
- ⭐⭐🔴 [[05-experiments/completed/2026-08-03-two-8-mouse-runs|2026-08-03 — THE TWO 8-MOUSE RUNS — Run 1 is everything we have, Run 2 is a total loss]] — C1 8.73 h + C2 2.34 h scoreable, validated against circadian norms; Run 2 = 0/8. ⚠️ Its "EEG degradation is directional (8/8 worse)" conclusion is **OVERTURNED** by the 2026-08-04 result above — that was a sampling artefact, not degradation.
- ⭐⭐🔴 [[05-experiments/completed/2026-08-01-channel-mapping-correction-first-sleep|2026-08-01 ⭐ CHANNEL MAP WAS WRONG — EMG always worked, FIRST REAL SLEEP ARCHITECTURE]] — `/1`=EEG `/2`=EMG already bipolar, `/3`,`/4` empty pads. Read before trusting any earlier EEG/EMG analysis.
- ⭐ [[05-experiments/completed/2026-08-03-data-quality-report-for-professor|2026-08-03 — data quality report for the professor]] — the full rescore of every recording
- 🔴⭐ [[05-experiments/completed/2026-07-31-contact-intermittency-no-wire-control|2026-07-31 — Legs are OPEN, not high-impedance, and state FLIPS on its own]] — **overturns "make new mice". DO NOT schedule surgeries on the old conclusion.**
- 🔴⭐ [[05-experiments/completed/2026-08-01-28h-contact-duty-cycle-and-c1-negative|2026-08-01 — 27.9 h run: duty cycle, grounds perfect, two failure modes]] — ⚠️ **its title and its "C1 has NO sleep" conclusion are RETRACTED** (C1 is the project's best result); read for the no-wire method and the grounds data only
- [[05-experiments/completed/2026-07-13-72h-4mouse-recording-audit|2026-07-13 — 72 h 4-mouse recording audit]]
- [[05-experiments/completed/2026-07-02-eeg-recording-checkpoint|2026-07-02 — EEG recording checkpoint]]
- ⏳⭐ [[05-experiments/active/2026-08-02-run2-preregistration|RUN 2 — pre-registered predictions]] — predictions written before the data

**Video / encoding:**
- [[05-experiments/completed/h265-encoding-failure|H.265 Failure (DO NOT USE)]]
- [[05-experiments/completed/2026-02-11-mpegts-container-test|MPEG-TS Container Test (adopted v5.2)]]
- [[05-experiments/active/|Active Experiments]]

### References
- 📖 [[06-references/eeg-analysis-glossary|⭐ EEG analysis glossary]] — every term and parameter in plain words (`nperseg`, `r@1min`, `Wn`, `DIRTY`, `ZT`, Otsu, block, rms, EDF)
- ⭐⭐🔴 [[06-references/electrode-failure-and-impedance-literature|Electrode failure + impedance literature — 82% of epidural electrodes fail in 3 weeks]] — six primary papers vs our data. **Weakens the "EMG works so it must be our solder" argument**; our best channel is poor by published standards; drops the frontal-sinus hypothesis.
- 🔴⭐ [[06-references/daq-research-findings-primary-sources|DAQ research findings — primary sources]] — 8 corrections; read before trusting older DAQ notes
- [[06-references/daq-ecosystem-comparison-xdaq-vs-openephys|DAQ ecosystem comparison — XDAQ vs Open Ephys vs Intan]] — priced BOMs (confidential, vault only)
- [[06-references/monitoring-diagnostics|Monitoring Diagnostics]] — Netdata/Uptime Kuma query commands for troubleshooting
- [[06-references/command-cheatsheet|Command Cheatsheet]]
- [[06-references/video-parameters|Video Parameters]]

### Rig Expansion (8 → 32 mice)
- ⭐ [[07-decisions/RIG-EXPANSION-HUB|RIG EXPANSION HUB — 8 → 32 Mice]] — **START HERE.** Single entry point: the decision, all vendor correspondence, wiring, open items, superseded claims
- [[07-decisions/2026-07-24-daq-32-mouse-final-comparison|DAQ 3-way comparison, 32 mice (XDAQ vs Open Ephys vs Intan)]] — the decision doc + professor summary
- [[06-references/xdaq-32-mouse-wiring-and-channel-law|XDAQ 32-mouse wiring + the channel law]] — animals = channels ÷ 64; full power-to-mouse wiring
- [[01-infrastructure/vendor-correspondence/2026-07-29-kontex-kc-call-prep-rig-finalization|Kontex call prep, 2026-07-29 — rig finalization]] — 45 questions + live build checklist

### Decisions & Reviews
`07-decisions/` holds **decisions only** — architecture choices, council reviews,
sprint plans. Trimmed 2026-08-03 from 26 files to 9; results moved to
`05-experiments/completed/`, literature and comparisons to `06-references/`,
procedures to `02-procedures/`, vendor call prep to
`01-infrastructure/vendor-correspondence/`.

- ⭐ [[07-decisions/RIG-EXPANSION-HUB|RIG EXPANSION HUB — 8 → 32 mice]] — the entry point for the expansion decision
- [[07-decisions/2026-07-27-video-eeg-sync-recording-architecture|2026-07-27 — video/EEG sync + recording architecture]] — the alignment plan; no clocks, pulse train mandatory
- [[07-decisions/2026-07-24-daq-32-mouse-final-comparison|2026-07-24 — DAQ 3-way comparison, 32 mice]]
- [[07-decisions/2026-07-21-acquisition-device-16-32-mice-and-kontex-thread|2026-07-21 — acquisition device for 16-32 mice]]
- [[07-decisions/2026-07-21-openephys-acquisition-board-scale-up-option|2026-07-21 — Open Ephys scale-up option]]
- [[07-decisions/2026-07-16-camera-node-scale-up|2026-07-16 — camera node scale-up]]
- [[07-decisions/2026-07-15-earth-and-sleep-council|2026-07-15 — earth and sleep council]] ⚠️ its "first sleep biology" result is **RETRACTED** (clipping artefact)
- [[07-decisions/2026-05-01-llm-council-review|2026-05-01 LLM Council Review]] — full advisor responses, peer reviews, chairman synthesis, staged plan
- [[07-decisions/2026-05-stabilization-sprint-week-1-plan|2026-05 Stabilization Sprint Week 1 — Plan + live status]] — single source of truth for sprint-item status

### Archive
- [[99-archive/notion-import-2025-02/|Notion Import]]

---

## System Status

| Component | IP | Status |
|-----------|------|--------|
| **Pi 1** | 192.168.0.11 | Online |
| **Pi 2** | 192.168.0.12 | Online |
| **go2rtc (Pi 1)** | :1984 | Online |
| **go2rtc (Pi 2)** | :1984 | Online |
| **Frigate** | 192.168.0.50:5000 | Online |
| **Session Daemon** | 127.0.0.1:8585 | Healthy (daemon + MQTT + Radiens connected) |
| **Netdata (NVR)** | 192.168.0.50:19999 | Active (16 NVR alerts, Slack notifications) |
| **Netdata (Pi 1)** | 192.168.0.11:19999 | Active |
| **Netdata (Pi 2)** | 192.168.0.12:19999 | Active |
| **Uptime Kuma** | 192.168.0.50:3001 | Active (7 monitors, Slack alerting) |
| **nvr-mqtt-slack** | systemd (NVR) | Active (watchdog stalls → Slack; added 2026-05-25) |

---

## Quick Commands

```bash
# Pi health check
ssh skimlab@192.168.0.11 'vcgencmd measure_temp && systemctl status go2rtc'

# Frigate logs
ssh skimlab@192.168.0.50 'docker logs frigate --tail 20'

# Stream test
ffprobe rtsp://192.168.0.11:8554/pi_cam_0
```

---

## Emergency

1. Check [[03-troubleshooting/symptoms/|Symptom Index]]
2. Run: `sudo systemctl restart go2rtc.service`
3. See [[06-references/command-cheatsheet|Command Cheatsheet]]

---

*Last updated: 2026-06-27 (📚 **sleep-recording operator documentation set shipped** — new [[02-procedures/sleep-recording-operator-manual|operator manual]] (start-here hub) + 8 new docs: Intan RHD2216 chip reference (datasheet-cited), rig-assembly, multimeter, Allego Monitor/sampling-rate/presets, headstage troubleshooting, EEG/EMG data guide. Verified finding: **128–256 Hz acquisition impossible; Allego min = 1 kHz → decimate offline**. Earlier 2026-06-19 (🎉 **first headstage detected — electrophysiology first light.** Intan RHD2216 enumerates on the XDAQ Core Gen-1, streaming shows signal. Root cause of the prior block was a wrong Allego system mode (`SMARTBOX_PRO`); correct = **"XDAQ One (G1) with XR Headstage"** / `XDAQ_ONE_REC` — see [[02-procedures/first-headstage-connection]]. No hardware fault, no RMA). Prev 2026-05-29 (XDAQ unit identified as Gen-1 Core / Opal Kelly USB — NOT Core2; Ubuntu driver solved via plugdev udev rule, Allego detects device; new authoritative doc `xdaq-core-gen1-ubuntu-driver`, Core2 docs banner-flagged, KC email trimmed). Prev 2026-05-28 (Phase 4.6 reconciler→Slack enabled in bridge; vault restructure — `07-decisions/` section added; council + sprint plan extracted out of `04-journal/2026-05-01.md` and `2026-05-20.md` into their own decision docs; daily journals get `created:` frontmatter for stable sort; bus-factor runbook shipped — Phase 6 council Stage 3.4 closed)*

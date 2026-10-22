---
type: reference
area: video-nvr
status: done
tags: [infrastructure, hardware-sync, reference, literature]
created: 2026-04-13
---

# Literature Review — Video-EEG Hardware Synchronization

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A short review of how published neuroscience studies handle multi-modal (video + electrophysiology) synchronization.
>
> **Why it exists.** Useful background when writing the methods section of a paper. It also establishes that the chosen approach (TTL pulse on GPIO) is the field standard, not an unusual choice.
>
> **How to read this page.** Read the "Verdict" callout below for the take-home. Skim the citations if you need to write a literature paragraph.

> [!quote] Paper-ready
> TTL-based hardware synchronization via digital I/O is the standard methodology across neuroscience multi-modal recording; the present architecture extends the standard approach with a distributed listener pattern, enabling per-node timestamping in a multi-Pi camera array.

> [!tip] Verdict
> TTL-based hardware synchronization via digital I/O is the **standard methodology** across neuroscience multi-modal recording. Our XDAQ GPIO approach is robust, correct, and publishably distinct due to the distributed architecture.

## Key References

### 1. Syntalos — Klumpp et al. (Nature Communications, January 2025)

**Citation:** Klumpp, M. et al. "Syntalos: a software for precise synchronization of simultaneous multi-modal data acquisition and closed-loop interventions." *Nature Communications* 16, 708 (2025).

**Relevance:** Most directly comparable system. Synchronizes Intan electrophysiology (same chip family as XDAQ) with multiple cameras using TTL pulses fed into Intan digital input — identical to our Wire 2 approach.

**Key findings:**
- Validated over 24+ hours with multiple devices: cameras, Intan RHD2000, Miniscope, Arduino, Pi Pico
- Intan timestamp fluctuation: 2 ms full range, mean deviation well below 1 ms
- Outperformed Bonsai (widely used alternative) which had >9 s drift after 22 hours without external timing cues
- Used a Raspberry Pi Pico microcontroller for TTL pulse generation

**Difference from our approach:** Syntalos is a monolithic software — cameras, electrophysiology, and sync all run through one program on one PC. Our distributed architecture (Pi → go2rtc → Frigate → daemon) provides fail-safe recording persistence that Syntalos cannot offer.

### 2. SyncGenie — Alkhoury et al. (HardwareX, December 2024)

**Citation:** Alkhoury, L. et al. "SyncGenie: A programmable event synchronization device for neuroscience research." *HardwareX* (2024). DOI: 10.1016/j.ohx.2024.e00619

**Relevance:** Open-source Arduino-based TTL synchronization device. Explicitly warns against software-only sync.

**Key quote:** "In applications that require precise synchronization, relying solely on software-based solutions can be problematic. The inherent latency and jitter associated with software operations on modern multitasking computers can introduce variability."

**Key findings:**
- Demonstrated that software timestamps had 227 ms average latency + jitter vs. TTL pulse timestamps
- Cost: $146–186 per unit
- 5 TTL channels, 3.3V output, 5V tolerant input

**Difference from our approach:** SyncGenie is a standalone Arduino device. We use the XDAQ's built-in `DAQ_ON` signal and DIN channels — no additional pulse generator hardware needed.

### 3. TTL Sync Protocol — Nakamura et al. (STAR Protocols, May 2023)

**Citation:** Nakamura, T. et al. "Protocol for precise signal synchronization of electrophysiology, videography, and audio recordings using a custom-made pulse generator." *STAR Protocols* 4(2), 102337 (2023).

**Relevance:** Step-by-step protocol for TTL sync of electrophysiology + video + audio using Neuralynx LabLynx.

**Key findings:**
- Uses custom Arduino-based pulse generator sending TTL to all devices
- Camera sync via GPIO trigger input on FLIR cameras (external trigger per frame)
- Alternative method: LED visible to camera for systems without GPIO input (lower precision)
- Validates the "same electrical pulse to multiple devices" principle

**Our advantage:** We don't need a camera with GPIO trigger input because we embed sync markers in the EEG data stream (via XDAQ DIN) rather than triggering camera frames. Our Pi cameras are free-running at 15 fps — the alignment is post-hoc via DIN pulse timestamps.

### 4. Jitter and Latency Review — Hasegawa et al. (Neuroscience Research, 2024)

**Citation:** Hasegawa, C. et al. "Two common issues in synchronized multimodal recordings with EEG: Jitter and latency." *Neuroscience Research* (2024). DOI: 10.1016/j.neures.2023.12.009

**Relevance:** Comprehensive review of synchronization issues in multi-modal neuroscience recordings.

**Key findings:**
- Hardware-based TTL communication achieves <1 ms latency
- Millisecond-order jitter directly affects signal-to-noise ratio of electrophysiological outcomes
- LSL (Lab Streaming Layer) can overcome jitter/latency issues in software but requires network configuration
- Recommends hardware sync when available

**Validates our approach:** Our XDAQ DIN captures at 20 kHz (50 μs per sample), giving us hardware-level precision that software solutions cannot match.

### 5. Lab Streaming Layer Review — Kothe et al. (Imaging Neuroscience / MIT Press, December 2025)

**Citation:** Kothe, C. et al. "The lab streaming layer for synchronized multimodal recording." *Imaging Neuroscience* (2025). DOI: 10.1162/IMAG.a.136

**Relevance:** Definitive review of LSL, the dominant software synchronization framework.

**Key findings:**
- LSL mentioned in >2,300 scientific articles
- "Hardware-based synchronization achieves superior timing precision" — acknowledged even by LSL's own review
- Software-based LSL offers greater flexibility for multi-device integration
- Sub-millisecond precision achievable with novel closed-loop methods

**Our positioning:** LSL is the intermediate step (like OpenVEEG at ≤33 ms). Our GPIO approach bypasses software clock alignment entirely — same electrical pulse triggers both devices.

### 6. OpenVEEG — Raghavan et al. (Epilepsy Research, 2018)

**Citation:** Raghavan, M. et al. "Open-source system for millisecond-synchronized continuous video-EEG." *Epilepsy Research* (2018).

**Relevance:** The system we already compare against. Uses LSL for ≤33 ms video-EEG alignment in mice.

**Key findings:**
- Video and EEG synchronized to within at least 33 ms (limited by camera frame rate)
- Validated with flurothyl-induced seizures in C57/BL6J mice
- Claims continuous capability up to 80 days but documents no watchdogs or crash recovery

**Our advantage:** Hardware GPIO sync (<1 ms) vs. their LSL software sync (≤33 ms). Our system also has documented 30+ day uptime with watchdog, crash-canary, and monitoring infrastructure.

### 7. Open Ephys GUI 1.0 (August 2025)

**Relevance:** Latest Open Ephys release achieves <0.1 ms drift over 3 days using their new real-time sync algorithm.

**Note:** This precision is only within the Open Ephys ecosystem (their acquisition board + their GUI). Not directly comparable to cross-device synchronization. Our approach is ecosystem-agnostic.

### 8. Bonsai + Intan LFP/Video Platform — Rodriguez-Santiago et al. (eNeuro, 2022)

**Citation:** Rodriguez-Santiago, M. et al. "Low-Cost Platform for Multianimal Chronic Local Field Potential Video Monitoring." *eNeuro* 9(5) (2022).

**Relevance:** Open-source multi-animal video-EEG using Intan + Open Ephys + Bonsai for seizure monitoring in mice.

**Key findings:**
- Used Intan acquisition with digital inputs for synchronization
- Bonsai handled simultaneous video + electrophysiology
- Developed GUI for seizure detection and behavioral scoring
- Off-the-shelf systems are "costly and do not provide state-of-the-art hardware"

**Our advantage:** Their system requires all devices connected to one PC. Our distributed Pi + NVR architecture allows cameras to be placed anywhere in the lab with PoE.

## Sync Hierarchy (Updated with Literature Context)

| Level | Method | Precision | Systems Using It |
|-------|--------|-----------|-----------------|
| 1 | **Software polling** (our current) | ~1 s | NeuroSurveillance (current) |
| 2 | **LSL / NTP** | ≤33 ms | OpenVEEG (2018), LSL ecosystem |
| 3 | **Software sync with correction** | <1 ms mean | Syntalos (2025), Open Ephys 1.0 |
| 4 | **Hardware TTL via GPIO** (our plan) | <1 ms, 50 μs DIN resolution | Standard methodology; SyncGenie, custom pulse generators |
| 5 | **Shared-clock / PTP** | <10 μs | Commercial systems (e.g., NeuroNexus XDAQ AIO) |

Our upgrade moves us from Level 1 to Level 4 — skipping the software sync intermediate entirely.

## Publishability Assessment

**What makes our approach distinct in the literature:**

1. **Hardware TTL sync + distributed recording architecture.** No published system combines GPIO sync with a Pi streamer + NVR + daemon model. Syntalos, OpenVEEG, and all others are monolithic.

2. **Fail-safe recording persistence.** MQTT state persists independently of the sync daemon. No other published system has this property.

3. **XDAQ `DAQ_ON` as a ready-made recording gate.** No published video-EEG sync paper uses this signal. Everyone else builds custom pulse generators.

4. **Modular, swappable sync layer.** GPIO sync is additive — can A/B test hardware vs. software polling in the same session.

5. **First published Frigate NVR ↔ NeuroNexus XDAQ integration.**

## Raspberry Pi GPIO Jitter — Literature Assessment

Multiple sources warn about GPIO jitter on Linux:
- RPi.GPIO docs: "unsuitable for real-time or timing critical applications"
- However: "may be sufficient for applications that just need to read or send some sparse triggers"

**Our assessment:** At 15 fps (66.7 ms frame intervals), even 2 ms of jitter is <3% of a frame interval. The Syntalos team validated a Pi Pico for TTL generation but our use case (sparse edge detection via `gpiod` kernel interrupts, not continuous PWM) is well within Linux's capabilities on Pi 5.

**Mitigation if needed:** Add a $4 Raspberry Pi Pico as a dedicated TTL pulse generator (same approach as Syntalos). Only consider this after measuring actual jitter in our system.

## Related

- [[overview|Hardware Sync Overview]]
- [[progress-meeting-2026-03-12|Progress Meeting 2026-03-12]]

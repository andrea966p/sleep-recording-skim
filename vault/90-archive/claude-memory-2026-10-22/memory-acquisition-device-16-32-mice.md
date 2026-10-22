---
name: acquisition-device-16-32-mice
description: Device decision to record 16 (→32) mice; XDAQ Core hard-capped at 8 by MISO-line count; buy One+
metadata: 
  node_type: memory
  type: project
  originSessionId: 0f0de6a5-55d5-4402-8180-cf30b24d90ae
  modified: 2026-07-21T09:15:43.046Z
---

Goal = record **min 16 mice simultaneously, future 32**, new rig (likely another building). Per mouse = 1 Intan RHD2216 bipolar headstage, only ~4-6 ch used (bipolar EEG + bipolar EMG + optional ECG/LFP). **Channel count is irrelevant; physical headstage count is the only limit.**

**THE HARD FACT (datasheet-verified 2026-07-21):** 1 RHD SPI cable = 5 LVDS pairs = CS+SCLK+MOSI (shared) + **MISO1 + MISO2** → **max 2 chips per cable, one chip per MISO line.** A chip = a whole MISO line regardless of channel count (16ch RHD2216 eats a full line same as 64ch). NOT DDR — two separate wires. Can't subdivide a MISO line.
- XDAQ **Core = 2 MISO pairs/port × 4 ports = 8 headstages, HARD** (wire count, NOT firmware, cannot unlock). Current 8-mouse rig already uses all 8 MISO lines.
- XDAQ **One/One+ = 4 MISO pairs/port × 4 ports = 16 headstages.**

**Decision:** 16 mice → **1× XDAQ One+** (1024ch, 4 headstage ports P1-P4; stays in Allego/Radiens pipeline). 32 → **2× One+ + SyncLink** (each XDAQ→own PC per docs; daisy-chain Ethernet). **Port Expander (SAdpt-Port-EXP)** = breaks each HDMI port into **up to 4 isolated animal ports (EXP A-D)** w/ XR headstages, **independent ground/ref per animal** — C/D unavailable on Core (→2/port=8), all 4 on One+ (→4/port=16). Confirms 8/16 AND fixes inter-animal ground crosstalk ([[eeg-60hz-saga]]).

**Kontex docs RETRIEVED 2026-07-21** (curl+browser-UA; docs.kontex.io 403s WebFetch). Full transcription + archived HTML → vault [[kontex-xdaq-hardware-reference]] (`01-infrastructure/hardware-sync/`, raw in `attachments/kontex-docs-20260721/`). **🔴 KEY OPEN Q:** does Port Expander accept our **Intan RHD2216** headstages (via SAdpt-XDAQ-OM12/Omnetics) or only Kontex XR headstages? Whole 4/port+isolation benefit hinges on it. Also: 32-mouse = 1 PC or 2? AIO single-box 32?

**RULED OUT — do not revive (both physically impossible on Core):** (1) Claude's "DDR = 2 chips/MISO pair → 16 on Core" — WRONG. (2) Prof. Kim's "4 sockets/port at 32ch using double-64 + order 8 more headstages → 16 on Core" — WRONG. (3) KC's $75 re-routing adapter → 16 on Core — can't create MISO3/4, Core stays 8.

**Kontex thread (KC Kong):** offered $75/ea re-router (no capacity gain on Core); confirmed Core=8, One/One+=16, SyncLink for multi-unit; flagged Port Expander unprompted; offered video call.

**✅ CALL HELD 2026-07-21** (KC + Prof. Kim). Outcomes: (1) **custom 4-socket/1-MISO-per-socket adapter = NOT possible** — Prof. Kim's variant dead from vendor. (2) **KC recommends TRYING the Port Expander** — handles each mouse's grounding separately (per-animal isolated ground/ref). (3) **2nd-XDAQ license limit ACKNOWLEDGED** (2 XDAQ = 2 licenses). (4) **Headstage must be as CLOSE to mouse as possible — our ~40cm analog run is a STRETCH** per KC → rig redesign to shorten it (helps 60Hz/impedance). (5) **2 mice per Intan adapter board = NOT possible, not even w/ Port Expander** — 1 board = 1 mouse (⚠️ clarify which board: C3410 vs C3442). (6) KC proposed several parts on kontex site.
**🔧 MAIN OPEN ITEM:** wiring **4× Port Expander to Core Gen-1 needs EXTRA adapters** (doesn't drop in) — build full BOM/wiring from Kontex site. NOTE: 4× PortExp on Core = per-animal grounding isolation on existing 8-mouse rig (60Hz test), **NOT a route to 16** (Core still EXP A+B only = 8). **Revised plan:** Step1 = PortExp-on-Core grounding trial (cheap, now); Step2 = ONE+ for 16 once isolation proven + surgical yield fixed; Step3 = 2×ONE+/SyncLink/2nd-PC/2nd-license for 32. Still gated by open frontal electrodes ([[eeg-60hz-saga]]) — no box fixes surgery.

Full docs: vault [[intan-rhd-spi-wiring-and-headstage-limits]] (physics, `06-references/`) + [[2026-07-21-acquisition-device-16-32-mice-and-kontex-thread]] (decision + email log, `07-decisions/`). Intan datasheets already in vault `06-references/datasheets/`. Kontex online docs 403 to WebFetch. Supersedes nothing in [[eeg-60hz-saga]]; the "8-headstage ceiling" durable fact is now datasheet-proven.

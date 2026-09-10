---
tags:
  - procedure
  - hardware-sync
  - allego
  - radiens
  - headstage
  - intan
  - first-light
created: 2026-06-18
status: resolved
system: XDAQ Core Gen-1 (XDAQ_ONE_REC mode) + 32-ch RHD XR headstage + SAdpt-XDAQ-OM12 + C3026
---

# First Headstage Connection — Mouse → Intan/XDAQ → Allego (Bring-up & Troubleshooting)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The record of the first-ever attempt to connect a live recording headstage to our XDAQ and see signal in Allego.
>
> **Why it exists.** It's our bring-up log and troubleshooting trail. **RESOLVED 2026-06-19** — the headstage is detected and streaming signal. Root cause was a **wrong Allego system mode** (`SMARTBOX_PRO` instead of "XDAQ One (G1) with XR Headstage"), **not** a hardware fault. The long teardown below (cabling, headstages, DMM, ports) was a false trail — but it proved the hardware healthy.
>
> **How to read this page.** Status banner = the answer. §0–§2 = what we built. §3–§7 = the (false-trail) hardware evidence. §8 = the **working Allego config + channel map**. §9–§11 = the DMM plan + unsent escalation emails, kept for the record. Software how-to: [[radiens-software-reference]]. Big picture: [[01-infrastructure/system-overview]].

> [!success] STATUS: RESOLVED — headstage detected (2026-06-19) — root cause = wrong Allego system mode
> **Headstage enumerates: `port_num_channels = {<Port.D: 3>: 32}`, `priSigs=32`, `mode=XDAQ_ONE_REC`, streaming shows signal.** Root cause was NOT hardware — Allego was in the wrong **system mode** (`SMARTBOX_PRO`). Correct mode = **"XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`). Hardware was healthy the whole time (DMM 3.56 V, both headstages, both SAdpt, all ports). **Escalation emails (§11) NOT sent — no RMA needed.** The "SPI signaling fault" hypothesis was wrong: `priSigs=0` meant wrong instrument profile, not a signaling fault.

---

## 0. System under test

| Item | Value |
|---|---|
| DAQ | **XDAQ Core (Gen-1)**, "NeuroNexus X series / Powered by KONTEX", Opal Kelly USB `151f:0130` (XEM7310-A75), serial `0C006218` — see [[xdaq-core-gen1-ubuntu-driver]] |
| Front panel | **REC & STIM HEADSTAGE**: Port 1 (HDMI, in use) + Port 3 / Port 4 (HDMI). BNC: ANALOG IN 1 / OUT 1, DIGITAL IN 1 / OUT 1. LEDs: `SYS S1 S2 S3` + `P1 P2 P3 P4`. Rear: EXP1/EXP2 (micro-HDMI), Audio Out, USB DMA, USB-PD (12 V⎓3 A, amber lit) |
| Allego | v3.11.3, mode **"XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`), 30 kHz — *(was wrongly set to SmartBox Pro during the block)* |
| Headstage | Intan **C3313** RHD 16-ch bipolar — chip **`intan RHD2216 V0S22`** (confirmed genuine in photos) |
| Electrode adapter | Intan **C3410** 36-pin electrode adapter board |
| Splitter | Intan **C3442** RHD dual headstage adapter (1 SPI → 2 headstages; removed during isolation) |
| SPI cable | **C3026** RHD SPI interface cable, 6 ft (Omnetics PZN-12, standard 2.9 mm) ×2 |
| Bridge adapter | **SAdpt-XDAQ-OM12** — HDMI male (→ XDAQ port) + 2× Intan SPI female (← C3026) |
| Subjects | 2 mice, 6-wire tether each (4× EEG skull screws + 2× EMG neck) |
| Channel map | Mouse 1 → bipolar ch 0,1,2 (C3410 holes 0–5); Mouse 2 → ch 4,5,6 (holes 8–13) — per `wiring 2 mice.pdf` |
| REF / GND | **SKIPPED this bring-up** (REF disconnected+insulated; GND not bridged) |

**Full chain (intended):**
```
mouse tether → slip-ring → C3410 (electrode side)
RHD2216 (C3313) ──SPI──► C3026 ──► [C3442 if dual] ──► SAdpt-XDAQ-OM12 ──HDMI──► XDAQ Core Port 1
```

---

## 1. Goal of this bring-up & the GND/REF skip

Objective: confirm the **physical chain and headstage detection** — *not* clean data. GND/REF deliberately skipped this round.

> [!info] Two independent questions — never conflate
> | Question | Depends on electrode side / GND? | Today's expectation |
> |---|---|---|
> | Headstage **enumerates** (SPI handshake) | **No** — bus-powered SPI chip-ID read | should PASS |
> | Channels carry *any* signal (tether continuity) | partly | informative |
> | Signal is **clean** | **Yes** (needs GND bridge) | not expected this round |

> [!check] Hard fact established this session
> RHD headstage detection is a **bus-powered SPI chip-ID read** that runs **continuously** (stream or not) and is **completely independent of the electrode/GND/REF side**. A headstage with empty electrode inputs still reports 16 channels. **Never debug detection via the mouse wiring.** (Proven here by the bare-headstage test, §3 #9.)

---

## 2. The failure

**Symptom:** Allego System view shows **Port A–D = 0 available channels**; only onboard I/O enumerated (Analog In ×2, Digital In ×2, Digital Out ×2). Headless probe returns `port_num_channels = {}` on every attempt.

**Decisive log evidence** — `/home/skimlab/.local/state/radiens/logs/allegoserver.log`:
```
msg="Auto-detecting headstages connected in the plug-and-play ports"
msg="Scanned ports..." portA=0 portB=0 portC=0 portD=0 portE=0 portF=0 portG=0 portH=0 priSigs=0
msg=IsHardwareConnected connectionValid=true instrument=IntanUSB3Instrument
AMP=0
```
Reading: the XDAQ is **healthy and actively sweeping the SPI bus**, but **no RHD chip answers on any of the 8 ports** (`priSigs=0`). Onboard GPIO (`GPIO-AIN/DIN/DOUT=2`) enumerates fine. → fault is the **headstage-end SPI/power path**, not Allego or the XDAQ core.

**Headless probe (repeatable):**
```bash
/opt/neurosurveillance/venv/bin/python -c \
"from radiens import AllegoClient; print(AllegoClient().get_status().port_num_channels)"
# observed every time: {}
```

---

## 3. Troubleshooting timeline (2026-06-18)

| # | Action | Result |
|---|---|---|
| 1 | Baseline before headstage: XDAQ on USB (SuperSpeed), allegoserver up, daemon `radiens_connected:true` | `port_num_channels={}` (expected, empty) |
| 2 | Plugged both mice into C3410, "chain secured", streamed | `{}` — no detection |
| 3 | Realized C3410/mouse side is irrelevant to enumeration | (lesson) |
| 4 | Confirmed bridge present: **SAdpt-XDAQ-OM12** (HDMI male + 2 SPI female) | topology valid |
| 5 | Removed C3442; single headstage → single C3026 → SAdpt → XDAQ | `{}` |
| 6 | Reseated HDMI; tried **both C3026** cables; tried **both SAdpt sockets** (Port A + B) | `{}` each |
| 7 | Inspected Omnetics pins — all intact | no mechanical fault |
| 8 | Read allegoserver.log → `priSigs=0` on all ports while scanning | isolates to SPI/power path |
| 9 | **Bare headstage** (Omnetics electrode connectors separated, only SPI→C3026→SAdpt→XDAQ) | `{}` — **electrode side ruled out** |
| 10 | Confirmed C3026 on headstage **SPI** connector (not the OMNETICS electrode connectors) | correct |
| 11 | Bare headstage on **Port 2** | `{}` *(later found Port 2 may be license-locked — invalid test)* |
| 12 | **Power cycle**: removed 12 V PD + USB 15 s, replug, relaunch Allego, restart daemon | `{}` — rules out SW state / FPGA-init glitch; daemon re-paired clean |
| 13 | Reconnected both mice + SPI cable | `{}` |
| 14 | Deep doc read (Intan SPI cable, dual adapter, Kontex CORE2, Radiens SDK) | see §4 findings |
| 15 | Confirmed on **Port 1**; mode dropdown question (SmartBox vs Intan RHD USB2) | keep SmartBox Pro (USB2 = wrong/legacy HW) |

LED note: `SYS S1 S2 S3` + `P1–P4` reported **all dark** through testing — but the system is provably alive (log: HAL alive, streaming, USB-PD amber lit). On Gen-1 the LED scheme may be unpopulated/firmware-gated; **treat LEDs as non-authoritative.** Per Kontex CORE2 docs, P-LEDs *should* light only after a headstage is detected (consistent with our dark P1).

---

## 4. Key reference findings (vendor docs, read 2026-06-18)

- **Bus power over SPI:** RHD2216 is powered **3.2–3.6 V via the SPI cable**; "the RHD USB interface board and RHD recording controller provide a **3.5 V** supply to their SPI ports." (Intan *RHD SPI Interface Cable/Connector Spec*, p5.) → no power on that line = `priSigs=0`. **Testable with a DMM.**
- **SPI connector self-aligning/polarized** (Omnetics PZN-12), signals pass straight through to an inverted connector → cable is symmetric, **cannot be mis-mated**. Orientation ruled out. (Same doc, p4–5.)
- **Dual-adapter (C3442) termination:** two headstages' R1/R2/R3 parallel to 50 Ω → only **corrupts data on >6 ft** cables; 6 ft with both headstages tested fine by Intan. Our single bare headstage = correct 100 Ω. **Ruled out.** (Intan *RHD Dual Headstage Adapter*, p3.)
- **Kontex CORE2:** "**Always use Port 1**, as other ports may be unavailable depending on the license." Firmware mode **boots when prompted by software — "may take a few minutes"**, then the mode LED lights; **P1–P4 light only after the headstage is detected.** Troubleshooting: "verify an XR-type headstage is connected; restart the app or rescan ports." (docs.kontex.io/XDAQ/CORE2)
- **Radiens SDK:** `AllegoClient` exposes `get_status, get_available_sensors, set_sensor, set_sampling_freq, set_streaming, set_recording, restart, signal_metrics, …` — **no system-mode switch or rescan**; mode is fixed at Allego launch. Log shows `IntanUSB3Instrument`+`SMARTBOX_PRO` scanning RHD ports. **⚠️ CORRECTION 2026-06-19: SmartBox Pro was the WRONG mode** — it shares the `IntanUSB3Instrument` USB3 backend (so it connects + scans + enumerates GPIO), but the headstage profile is wrong, so it reports `priSigs=0`. **Correct mode for this unit = "XDAQ One (G1) with XR Headstage" (`XDAQ_ONE_REC`)** — selecting it gave instant detection (32 ch on Port D). The mode list visible in early logs (SMARTBOX_PRO / INTAN_USB2 / KPI) was incomplete — it only showed modes that had *ever been selected*; `XDAQ_ONE_REC` wasn't there until first chosen. **Intan RHD USB2** mode = legacy USB2 eval board (not our hardware) — confirmed wrong (`raklib::cmd1 API error: Device not connected`).

---

## 5. Eliminated causes

✅ Electrode side / mouse wiring / GND / REF (bare-headstage test) · ✅ C3410 board + its messy solder (bare test) · ✅ C3026 cable (both swapped) · ✅ SPI cable orientation (self-aligning) · ✅ C3442 dual-adapter termination (removed, single = 100 Ω) · ✅ SAdpt socket A vs B · ✅ Software/Allego state + stale client (power cycle + daemon restart) · ✅ FPGA init glitch (power cycle) · ✅ Allego mode (SmartBox Pro correct; controller connects + scans) · ✅ XDAQ core health (onboard I/O enumerates, USB SuperSpeed, 12 V PD)

---

## 6. Root-cause hypotheses (ranked)

1. **SAdpt-XDAQ-OM12 not delivering SPI bus power/signals** — single first-use part present in *every* test; if it doesn't pass the 3.5 V rail (or CS/SCLK/MOSI), result is exactly `priSigs=0`. **DMM power test catches this.**
2. **XDAQ Port-1 headstage subsystem** — never exercised before (first headstage ever on this unit); core is healthy but the SPI-over-HDMI block is unproven.
3. **Headstage DOA** — new, but never enumerated; DOA happens. **Spare-headstage swap catches this.**
4. **Firmware-mode / timing** — Kontex says detection can lag minutes after stream while firmware boots; needs Port 1 + patience + rescan. *(Cheap to retry; lower likelihood since many minutes of scans showed no state change.)*

---

## 7. Side issue to fix before real recordings (not the current blocker)
**C3410 solder quality** (photo, 2026-06-18): joints show bridges / icicles / cold joints on the **electrode side**. Irrelevant to enumeration, but **will wreck signal quality and risks shorts** — **reflow before any real recording.** Also verify no bridge to the VDD/GND pads.

---

## 8. Allego config (for when the headstage DOES enumerate)

> [!danger] Use `Stream`, not `Record`, for checks
> Allego **`Record` drives our session daemon** → starts a Frigate video session (same path as a real Radiens R_ON). For a connection check use **`Stream` only**.

1. **Dashboard → System** view. Mode = **"XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`) — **NOT** SmartBox Pro (that reports `priSigs=0`). **30000** sample rate (mode-switch resets it to 1000 — restore 30 kHz). Port-status (bottom bar) green = port in use.
2. **Probe/electrode mapping** → **Passthrough** (`hstg__passthrough_32`, identity 1:1) — **NOT** a geometric probe layout (our wiring is a custom 1:1 solder map). Verified loaded: `headstage_id='hstg__passthrough_32'`, native names `pri_0…pri_31`.
3. **Signal Processing** tab → **Common Average Reference / software referencing OFF** (bipolar montage; CAR would cross-contaminate the +/− pairs). *(Confirm exact toggle label on screen — record in run log.)*
4. **Monitor** view → watch channels. Expect saturation/hum this round (GND skipped) — that's fine.

> [!tip] Doing your own mapping? Follow the step-by-step
> For a plain-language, operator-friendly walkthrough of signal mapping (real-world ↔ Allego, EEG/EMG, csv2sensor, verification), use [[signal-mapping-guide]]. The table below is this rig's specific result.

### 8.1 Channel map (2 mice on one 32-ch headstage) — per `~/Downloads/wiring 2 mice.pdf`

> [!info] Physical map is fixed by the solder; this is the **Allego label/select** step
> The detected headstage is the **32-channel** type (`passthrough_32` → 32 ch on Port D). Each mouse uses **6 single-ended channels = three bipolar pairs**. Allego native channel `pri_N` = headstage labeled channel **N** (passthrough is identity). Channel **naming is GUI-only** — the Radiens SDK `ChannelMetadata.table` exposes `chan_name` read-only, no setter; do it in the Allego channel table.

| Native | Suggested label | Signal | Tether wire | Slip-ring wire |
|---|---|---|---|---|
| `pri_0` | `M1_EEG+` | EEG + | Red | Red |
| `pri_1` | `M1_EEG−` | EEG − | Black | Black |
| `pri_2` | `M1_EMG+` | EMG + | Yellow | Yellow |
| `pri_3` | `M1_EMG−` | EMG − | Blue | Orange |
| `pri_4` | `M1_unused` | 3rd pair + — **wired but unused** | White | Brown |
| `pri_5` | `M1_GND` | ground (3rd −), wired | green | green |
| `pri_8` | `M2_EEG+` | EEG + | Red | Red |
| `pri_9` | `M2_EEG−` | EEG − | Black | Black |
| `pri_10` | `M2_EMG+` | EMG + | Yellow | Yellow |
| `pri_11` | `M2_EMG−` | EMG − | Blue | Orange |
| `pri_12` | `M2_unused` | 3rd pair + — **wired but unused** | White | Brown |
| `pri_13` | `M2_GND` | ground (3rd −), wired | green | green |

**Selection — record only the 4 signal channels per mouse:** enable `pri_0,1,2,3` (M1 EEG±/EMG±) and `pri_8,9,10,11` (M2 EEG±/EMG±). **Deselect** the 3rd pair (`pri_4,5,12,13` — wired but unused / ground) and all unwired (`pri_6,7,14…31`). The green/ground wires (`pri_5,13`) stay physically connected as the headstage GND/REF — they're functional ground, just not recorded channels.

**Bipolar pairing is logical, not hardware** — on the 32-ch headstage ch0/ch1 are *separate single-ended* channels. EEG = `EEG+ − EEG−`, EMG = `EMG+ − EMG−`, computed in analysis (or a live Allego referencing/montage). Keep **CAR OFF**. Green/ground wires (`pri_5`, `pri_13`) tie to headstage GND/REF.

> [!warning] No in-Allego channel rename (per manual, 2026-06-19)
> Allego's **Signal Map is read-only** and XDAT files sort by preamp channel (`pri_N`) — you **cannot rename channels to `M1_EEGp` etc. in the GUI**. Apply those labels in **offline analysis by channel index** (this table is the source of truth).

> [!success] Custom sensor loaded (csv2sensor, 2026-06-19)
> Built `hstg__usrdef_2mice` + `probe__usrdef_2mice_probe` via NeuroNexus **`csv2sensor`** so the 8 used channels map to logical **site numbers** + grouped geometry (M1 = sites 1–4, M2 = sites 5–8). No text labels (the tool has no name field), but the Signal Map + wireframe now reflect our real 2-mice layout. Workflow, CSVs, and load steps: [[radiens-software-reference]] → "Custom sensor maps". Site mapping: native 0,1,2,3 → sites 1,2,3,4 (M1 EEG+,EEG−,EMG+,EMG−); native 8,9,10,11 → sites 5,6,7,8 (M2 EEG+,EEG−,EMG+,EMG−).

**3rd pair resolved (2026-06-19):** the 3rd pair is **wired but unused** — `pri_4`/`pri_12` (white, `2+`) carry no recorded signal; `pri_5`/`pri_13` (green, `2−`) are the animal ground. So **2 recorded signals per mouse: EEG + EMG** (4 amp channels each, 8 total).

---

## 9. TOMORROW — decisive test plan

> [!todo] Ordered; stop when resolved. **All tests on Port 1, streaming.**

### A. DMM power test (do FIRST — settles power vs no-power)
1. DMM → **DC volts**, 20 V range.
2. Black probe → headstage **GND** pad; red probe → headstage **VDD** pad (both labelled on the RHD2216 board).
3. **Stream** in Allego (Port 1).
4. Read:

| Reading | Meaning | Action |
|---|---|---|
| **~3.2–3.6 V** | Chip IS powered → fault is SPI signaling or dead chip | go to Test B (spare) |
| **~0 V** (or ≪3 V) | SAdpt/XDAQ **not delivering bus power** | **SAdpt RMA** — escalate, done |

5. *(Optional localization)* measure the **power pin at the SAdpt SPI socket** and at the **C3026 ends** to pinpoint where 3.5 V drops out.

### B. Bare spare headstage (isolates the headstage)
- Spare RHD headstage, electrode side empty → SPI → C3026 → SAdpt → **Port 1**, stream.
- **Enumerates** → original RHD2216 DOA. **Still 0** → SAdpt or XDAQ port.

### C. Port-1 firmware/patience (cheap retry)
- Stream on Port 1, **wait several minutes**; try Allego restart / port rescan; watch P1 LED + channel count.

### D. (Optional) XDAQ-RHX cross-check
- If Intan's **XDAQ-RHX** software is installed, try detecting there. Detects in RHX but not Allego ⇒ Allego config; fails in both ⇒ hardware.

**After tests:** record DMM reading + spare result in the run log, then escalate to Kontex/KC Kong if hardware-confirmed (evidence summary §10).

---

## 10. Vendor escalation — evidence summary (email-ready)
If DMM/spare confirm a hardware fault, send to KC Kong / Kontex:
- Unit: XDAQ Core Gen-1, serial `0C006218`, Opal Kelly `151f:0130`, Ubuntu 24.04, Allego 3.11.3, SmartBox Pro mode, 30 kHz.
- Symptom: first-ever headstage (Intan RHD2216 / C3313) via SAdpt-XDAQ-OM12 + C3026 (6 ft) on **Port 1** — **never detected**; allegoserver scans all 8 ports → `priSigs=0`, `AMP=0`; onboard Analog/Digital I/O enumerate normally.
- Eliminated: electrode side, both C3026, both SAdpt sockets, C3442 removed, Ports 1/2, power cycle, daemon restart, Allego mode.
- DMM at headstage VDD/GND during stream = **<reading>** (expected 3.2–3.6 V per Intan SPI-cable spec).
- Spare headstage on same rig = **<result>**.
- Ask: is the **SAdpt-XDAQ-OM12** or the **Port-1 headstage subsystem** faulty? Any required firmware-mode/license step for Port-1 RHD detection on a Gen-1 Core?

---

## 11. Escalation emails — ⛔ NOT SENT (issue resolved 2026-06-19)

> [!success] DO NOT SEND — root cause was wrong Allego mode, not hardware. Kept for the record only. Headstage detected fine in `XDAQ_ONE_REC` mode. No RMA, no vendor escalation needed.



> [!note] Two emails, split by ownership. **NeuroNexus** = Allego/Radiens software, license, SAdpt-XDAQ-OM12 adapter, RHD2216 headstage. **Kontex** (`KC@kontex.io`) = XDAQ Core hardware + SPI-over-HDMI subsystem + Linux RHX build. Q2 (SAdpt Gen-1 compatibility) is in **both** on purpose — whoever owns the adapter answers fastest.

### 11.1 — NeuroNexus (Jeffrey / support)

**Subject:** RHD2216 headstage never detected in Allego on XDAQ Core Gen-1 — `priSigs=0`, 3.56 V bus power confirmed

Hi Jeffrey,

We're bringing up our first recording headstage on the XDAQ Core Gen-1 and Allego never detects it on any port. We've exhausted bench isolation and would like your help on the software/license/adapter side before we treat it as a hardware RMA.

**Setup**
- XDAQ Core Gen-1, serial `0C006218`, Opal Kelly `151f:0130` (XEM7310-A75)
- Host: Ubuntu 24.04, Allego 3.11.3, **SmartBox Pro** mode, 30 kHz
- License: **Radiens Analytical Suite**
- Chain: Intan **RHD2216 (C3313)** → **C3026** 6 ft SPI cable → **SAdpt-XDAQ-OM12** (HDMI male + 2 SPI female) → XDAQ HDMI port

**Symptom**
- `port_num_channels = {}` (headless Radiens probe)
- allegoserver scans all 8 ports → `portA–H = 0`, **`priSigs = 0`**, `AMP = 0`
- Onboard I/O enumerates normally: `GPIO-AIN/DIN/DOUT = 2`
- Controller connects fine: `connectionValid=true`, `IntanUSB3Instrument`, USB SuperSpeed, 12 V PD lit
- Acquisition runs under `Feat_NoLicenseRequired`; no license denial/expiry in logs

**Eliminated by substitution — every case still `priSigs=0`**
- 2 headstages (original RHD2216 + brand-new spare) → not DOA
- 2× C3026 SPI cables
- 2× SAdpt-XDAQ-OM12 adapters (original + brand-new)
- 3 HDMI ports (1, 3, 4), incl. 3-min firmware-boot wait + Allego restart
- Electrode/GND/REF side (bare-headstage test), C3442 removed, full power-cycle, daemon restart, Allego mode

**Key measurement**
DMM at the headstage VDD↔GND pads while streaming = **3.56 V** (rests at 0, jumps to 3.56 on contact; top of the Intan 3.2–3.6 V SPI-bus spec). **SPI bus power is present and correct** — the chip is powered but never answers the SPI chip-ID scan. Not a power-rail fault.

**Questions for you**
1. Does live RHD headstage acquisition / channel detection require an **entitlement beyond the Analytical Suite**? Logs show acquisition under `Feat_NoLicenseRequired` and no denial, but we want to rule out a silent channel-count cap producing `priSigs=0`.
2. Is **SAdpt-XDAQ-OM12** validated for the **Gen-1** Core pinout, or is it a Gen-2/Core2 part? A signal-pin (not power) mismatch would pass the 3.5 V rail but break SCLK/CS/MISO/MOSI — exactly our symptom.
3. Is there a **Linux build of XDAQ-RHX** (or a recommended diagnostic) so we can cross-check detection outside Allego? Releases only ship mac/win binaries.
4. Any Allego SmartBox-Pro setting we may have wrong for first-time RHD detection on a Gen-1 Core?

Full allegoserver logs available on request. Thanks,
Andrea

---

### 11.2 — Kontex (KC Kong, `KC@kontex.io`)

**Subject:** XDAQ Core Gen-1 (SN 0C006218) — RHD headstage `priSigs=0` despite 3.56 V bus power — SPI subsystem?

Hi KC,

First headstage bring-up on our XDAQ Core Gen-1 — never detected on any port. Bench isolation is exhausted and the evidence points at the SPI signaling path in the core. Requesting your diagnosis.

**Setup**
- XDAQ Core Gen-1, serial `0C006218`, Opal Kelly `151f:0130` (XEM7310-A75)
- Ubuntu 24.04, Allego 3.11.3, SmartBox Pro mode, 30 kHz
- Chain: Intan **RHD2216 (C3313)** → **C3026** 6 ft SPI → **SAdpt-XDAQ-OM12** (HDMI male + 2 SPI female) → XDAQ HDMI port

**Symptom**
- allegoserver scans all 8 ports → `portA–H = 0`, **`priSigs = 0`**, `AMP = 0`
- Onboard I/O enumerates fine: `GPIO-AIN/DIN/DOUT = 2`
- Controller connects: `connectionValid=true`, `IntanUSB3Instrument`, USB SuperSpeed, 12 V PD lit
- Host OS/driver confirmed working (FrontPanel + udev; GPIO + USB + power all enumerate)

**Eliminated — all still `priSigs=0`**
- 2 headstages (orig + new spare), 2× C3026, 2× SAdpt-XDAQ-OM12
- 3 HDMI ports (1, 3, 4) + 3-min firmware wait + Allego restart
- Electrode side, C3442 removed, power-cycle, daemon restart, Allego mode

**Key measurement**
DMM at headstage VDD↔GND while streaming = **3.56 V** (validated on-pad, top of Intan spec). **Bus power is present** — chip powered, but no SPI chip-ID response. Not a power-rail fault.

**Questions**
1. With confirmed 3.56 V bus power but `priSigs=0` across 2 headstages / 2 cables / 2 adapters / 3 ports, does this indicate a fault in the **XDAQ core SPI signaling subsystem** (SCLK/CS/MOSI/MISO over the HDMI port)?
2. Is **SAdpt-XDAQ-OM12** pin-compatible with the **Gen-1** Core, or is it a Gen-2/Core2 adapter? Want to rule out a signal-pin mapping mismatch.
3. Is there a required **firmware-mode / license / init step** for RHD detection on a Gen-1 Core?
4. Is there a **Linux XDAQ-RHX** binary (releases ship mac/win only) for an Allego-independent cross-check?

Happy to share full allegoserver logs and the `ScanPorts` output. Thanks,
Andrea

---

## Run log (raw)
- **2026-06-18 ~14–19 KST** — full session above. Ended BLOCKED, awaiting DMM test. Daemon healthy post-power-cycle (`radiens_connected:true`). Photos archived: `Downloads/drive-download-20260618T090029Z-3-001/`.
- **2026-06-19** — Swapped to **brand-new SAdpt-XDAQ-OM12** (HDMI bridge), original headstage + C3410, streaming → `port_num_channels={}`, log `priSigs=0`. **Hypothesis #1 (SAdpt) ELIMINATED.**
- **2026-06-19** — **Bare spare (brand-new) headstage** on new SAdpt, streaming → `{}`, `priSigs=0`. **Headstage DOA eliminated** (2 headstages both fail).
- **2026-06-19** — Moved SAdpt to **front-panel Port 3**, streaming → `{}`, `priSigs=0`. Not Port-1-specific.
- **2026-06-19 — DMM (HARDEN 661002, V⎓ 20 range) at headstage VDD↔GND, streaming = `3.56 V` (validated).** Probe rests at 0, jumps to 3.56 on pad contact — real reading, top of Intan 3.2–3.6 V spec. *(First attempt misread an air-float phantom 3.33 V with probes open; the cheap DMM drifts near 3.3 V on open DC leads — disregard that, 3.56 on-pad is the real datum.)* Bus power PRESENT → "no power" hypothesis dead; fault is **SPI signaling**, not the rail.
- **2026-06-19** — **Port 4** + 3-min firmware-boot wait + **Allego restart** → `{}`, `priSigs=0`. Patience + all 3 HDMI ports (1/3/4) exhausted.
- **2026-06-19 ✅ RESOLVED** — switched Allego system mode from `SMARTBOX_PRO` → **"XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`). Headstage immediately detected: `port_num_channels={<Port.D:3>:32}`, `priSigs=32`, `portD=32`, streaming shows signal. **Root cause = wrong instrument profile, NOT hardware.** All prior hardware suspicion (SPI fault, SAdpt, XDAQ port) was a false trail — `priSigs=0` is what SMARTBOX_PRO reports when the actual hardware is an XDAQ One G1 + XR headstage. Lesson: SMARTBOX_PRO *connects* (IntanUSB3Instrument backend shared) and scans, but reports 0 because the headstage profile is wrong — controller-connects ≠ correct-mode. Kontex's "verify an XR-type headstage" hint pointed here.
- ~~**2026-06-19 CONCLUSION (SUPERSEDED — was wrong, see RESOLVED above):**~~ power good + 2 headstages + 2 C3026 + 2 SAdpt + 2 ports all `priSigs=0`, plus Port 4 + 3-min wait + Allego restart also `0` ⇒ fault is **XDAQ core SPI signaling subsystem** OR **SAdpt-XDAQ-OM12 pinout mismatch for Gen-1 core**. Bench isolation FULLY exhausted (all 3 HDMI ports + patience + restart) → escalate Kontex/KC. Email drafted, ready to send.
- _<exact CAR/referencing toggle label, once a headstage enumerates>_ —

---

## Sources
- Intan — *RHD SPI Interface Cable/Connector Specification* (bus power 3.2–3.6 V, Omnetics PZN-12, pinout) — local `Downloads/Intan_RHD2000_SPI_cable.pdf`
- Intan — *RHD Dual Headstage Adapter* (C3442 termination) — local `Downloads/Intan_RHD2000_dual_headstage_adapter.pdf`
- Intan — RHD2000 series datasheet; RHD2164 datasheet; Recording Controller user guide — local `Downloads/`
- Kontex — XDAQ CORE docs: <https://docs.kontex.io/XDAQ/CORE2/> (Port 1, firmware mode, LEDs)
- NeuroNexus Radiens — [Allego User Guide](https://manuals.plus/neuronexus/radiens-allego-software-manual) · [Quick Start](https://device.report/manuals/radiens-allego-software-quick-start-guide) · [SDK docs](https://neuronexus.github.io/radiens-core-python/latest/)

## Related
- [[xdaq-core-gen1-ubuntu-driver|XDAQ Core Gen-1 Ubuntu Driver & Device Verification]] — driver + headless probe + daemon-restart gotcha
- [[radiens-api-reference|Radiens AllegoClient API Reference]]
- [[overview|Hardware Sync Overview]] · [[wiring-guide|Wiring Guide]] — TTL sync (separate track)
- [[../03-troubleshooting/incidents/2026-04-02-allegoserver-thermal-spikes|allegoserver thermal spikes]]

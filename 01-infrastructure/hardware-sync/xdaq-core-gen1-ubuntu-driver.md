---
tags:
  - infrastructure
  - hardware-sync
  - driver
  - opal-kelly
  - ubuntu
  - golden-config
created: '2026-05-29'
status: complete
supersedes: >-
  Core2/Thunderbolt assumption in overview, wiring-guide, manual-reference,
  kontex-developer-portal-notes
---
# XDAQ Core (Gen-1) — Ubuntu 24.04 Driver Setup & Device Verification

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The record of getting our actual XDAQ unit talking to the Ubuntu acquisition host. **The unit is a first-generation XDAQ Core (Opal Kelly USB) — NOT the Thunderbolt Core2** that every earlier hardware-sync note assumed. The fix was a single Linux permission rule. It now works.
>
> **Why it exists.** Most of the older hardware-sync docs ([[overview]], [[wiring-guide]], [[xdaq-core2-manual-reference]], [[kontex-developer-portal-notes]]) were written for the Core2 and are **wrong about the host interface and possibly the DB25 details**. This page is the authoritative, verified state as of 2026-05-29. Where it conflicts with those pages, **this page wins.**

> [!quote] Paper-ready
> The acquisition host (Ubuntu 24.04 LTS) connects to a first-generation XDAQ Core over its Opal Kelly USB 3.0 (SuperSpeed) interface (USB ID 151f:0130, XEM7310-A75). Device access from the non-root acquisition process is granted by a udev rule assigning the Opal Kelly vendor ID (0x151f) to the `plugdev` group; the Allego server bundles the Opal Kelly FrontPanel runtime and detects the device under system mode `SMARTBOX_PRO` at 30 kHz.

---

## 1. Model correction — what we actually have

| | Earlier assumption (WRONG) | Verified 2026-05-29 |
|---|---|---|
| Model | XDAQ **Core2** (Gen-2) | **XDAQ Core (Gen-1)**, chassis badge "KONTEX XDAQ Core", serial **`0C006218`** |
| Host interface | Thunderbolt (`boltd` / `thor` mgr) | **Opal Kelly USB 3.0** (`ok` mgr) |
| USB ID | — | **`151f:0130 Opal Kelly Incorporated XEM7310-A75`** |
| Power input | USB-PD 20 V | USB-PD **12 V** / 3 A (auto-negotiated by the Kontex 65 W PD/PPS brick — safe) |
| EXP1 / EXP2 | micro-HDMI | **USB-C** |
| Ground terminals | SYS GND + Chassis GND (2×) | **single GND pin** |

**Evidence:**
```
$ lsusb
... Bus 002 Device 00x: ID 151f:0130 Opal Kelly Incorporated XEM7310-A75
$ boltctl list
(empty — no Thunderbolt device)
$ lsusb -t
... Port 004: Dev x, If 0, Class=Vendor Specific Class, Driver=[none], 5000M   # USB 3.0 SuperSpeed
```
`Driver=[none]` is **normal** — Opal Kelly FrontPanel is a userspace (libusb) driver; no kernel module binds. SuperSpeed (5000M) requires a good USB-C cable — an earlier poor cable fell back to USB 2.0 (480M).

---

## 2. The driver fix (✅ done, verified)

Allego **already ships** the Opal Kelly FrontPanel runtime — no separate install:
```
/opt/allego/resources/radix/allegoserver/libokFrontPanel.so
```
`allegoserver` runs as the login user (`skimlab`), not root. The only gap was USB device-node **write** permission: the raw node defaults to `crw-rw-r-- root root` (others = read-only), and FrontPanel needs write (FPGA bitfile upload + control transfers). No vendor `60-opalkelly.rules` was present.

**Fix — one udev rule** (`skimlab` is already in `plugdev`, GID 46, so no relogin needed):

`/etc/udev/rules.d/60-opalkelly.rules`:
```
SUBSYSTEM=="usb", ATTR{idVendor}=="151f", MODE="0664", GROUP="plugdev"
```

Apply:
```bash
sudo udevadm control --reload-rules
# then physically unplug/replug the XDAQ USB-C cable
```

**Verification (all passed 2026-05-29):**
```bash
# node now group-plugdev, group-writable:
$ ls -l /dev/bus/usb/002/00x
crw-rw-r-- 1 root plugdev ...

# allegoserver (non-root) holds the device open:
$ sudo lsof /dev/bus/usb/002/00x
allegoserver  <pid>  skimlab  ...  /dev/bus/usb/002/00x
```

> [!check] This answers KC Kong's open driver question (round-3 Q5) ourselves
> Gen-1 XDAQ Core on Ubuntu 24.04 needs **no Thunderbolt/boltd, no separate FrontPanel install, no root** — just the `plugdev` udev rule for VID `151f`. We still want KC's confirmation of the DB25 hardware details (below), but the Linux connectivity question is **closed**.

---

## 3. Allego reports the device healthy (no headstage attached)

Queried via the `radiens` `AllegoClient` (`/opt/neurosurveillance/venv`) — headless, no GUI guessing:

```python
from radiens import AllegoClient
s = AllegoClient().get_status()
```

| Field | Value | Meaning |
|---|---|---|
| `system_mode` | **`SystemMode.SMARTBOX_PRO`** | Real hardware, **not Demo/Simulation**. In the Allego **System tab** the system shows as **SmartBox Pro** |
| `connected` | `True` | DAQ linked |
| `sample_freq` | `30000.0` | 30 kHz |
| `port_num_channels` | `{}` | No headstage on any port (correct — no mouse) |
| `cable_length_ft` | Ports A–H all `None` | 8 ports, all empty |
| `get_available_sensors()` | full library | Allego healthy (incl. mouse EEG sensors `g_mouse_1x30`, `XDAQ_X3R-H32EEG_Mouse30`) |

**Where to check in the UI:** **System tab** → system = SmartBox Pro, ports A–H = "no headstage". Empty ports are expected with no animal connected.

> [!tip] Digital-out control is programmable (relevant to the sync gate)
> `get_digital_out_states()` returned `{'digital_outs_mode': 'GATED', 'states': [{chan 0: False}, {chan 1: False}]}` — DOs are **already in GATED mode**, and the API exposes `get_digital_out_states()` / `set_digital_out_manual()`. So the recording-gate signal can be **driven and read from Python**, not just measured on a DMM. Note: only **2** DO channels appeared via this API (chan_idx 0,1) — this may differ from the Core2's 6 DB25 DOs; map chan_idx → physical pin before wiring.

---

## 4. Next steps — clear, non-overlapping

### ✅ Done (verified 2026-05-29)
- Model identified (Gen-1 Core, Opal Kelly USB).
- Ubuntu driver/permission solved (udev rule); allegoserver opens device non-root.
- USB 3.0 SuperSpeed confirmed (good cable).
- Device detected in Allego (`SMARTBOX_PRO`, 30 kHz, connected).

### ⏳ Still open — hardware/wiring (re-scoped to the Gen-1 Core)
> [!danger] The DB25 pinout, recording-gate pin, and DO voltage in the older Core2 docs are NOT confirmed for this Gen-1 unit
> Pins `DAQ_ON=13 / DI 03=2 / DO 03=22`, "3.3 V fixed", and the "BNC Breakout Board toggle → DO 03 Gated" mechanism were all **Core2-specific** (Jeffrey tested a Core2). They may differ on the Gen-1 Core. Do **not** wire from the old diagrams until confirmed for this model.

1. **Confirm Gen-1 Core DB25 pinout + recording gate** with KC Kong (see trimmed email in [[neuronexus-inquiry-email#Correction email to KC — round 3b (draft 2026-05-29)]]). Cross-check against the API: `get_digital_out_states()` shows 2 DO channels in GATED mode — establish which physical DB25 pin each `chan_idx` maps to.
2. **DO logic-high voltage** on the Gen-1 Core DB25 — confirm before wiring into a 3.3 V Pi GPIO (no over-voltage tolerance).
3. **Fan-out + grounding** for ≥4 Pi 5 nodes (single GND pin on this unit) — KC.
4. **Bench check** once pinout confirmed: drive the gate via `set_digital_out_manual()` / start a recording, DMM + logic-analyzer the gate pin (clean level, no idle pulses).
5. **Live signal test** — connect a headstage (mouse) and confirm streaming/recording end-to-end (today verified link + detection only, no neural data).

---

## Related
- [[overview|Hardware Sync Overview]] — ⚠️ Core2-era; host interface section superseded by this page
- [[wiring-guide|Wiring Guide]] — ⚠️ DB25/voltage = Core2-derived, unconfirmed for Gen-1
- [[xdaq-core2-manual-reference|Core2 Manual Reference]] — Core2 pinout; this unit is Gen-1, verify before trusting
- [[kontex-developer-portal-notes|Kontex Developer Portal Notes]] — Thunderbolt/libxdaq path does NOT apply to this Opal Kelly unit
- [[neuronexus-inquiry-email|Vendor inquiry chain]] — KC round-3b correction email
- [[radiens-api-reference|Radiens API Reference]] — `AllegoClient` used for the verification above

---
tags:
  - reference
  - radiens
  - allego
  - neuronexus
  - manual
created: 2026-06-19
status: complete
role: PRIMARY reference for the Radiens / Allego software
source: NeuroNexus — Radiens Technical Documentation (©2025, 177 pp)
---

# Radiens Software — Primary Reference (Allego / Videre)

> [!abstract] TL;DR
> **What this is.** The authoritative reference for operating the **NeuroNexus Radiens** software (Allego acquisition + Videre offline) on our XDAQ rig. The full vendor manual (177 pp) is embedded below; this page is the index + the facts that apply to *our* setup.
>
> **Why it exists.** During the first-headstage bring-up we lost two sessions to guessed UI behavior. This page is the "read the manual, don't guess" source. **This is THE main Radiens software reference for the vault** — point here first for any Allego/Videre question.
>
> **How to read this page.** §"For our setup" first (the load-bearing facts). Then the section map to jump into the embedded PDF by page. Big picture: [[01-infrastructure/system-overview]].

> [!quote] Paper-ready
> Acquisition and online visualization were performed in NeuroNexus Radiens Allego; recordings were saved in the open XDAT format (raw signals plus metadata) for offline analysis in Python/MATLAB.

## Embedded manual

![[Radiens-Technical-Documentation.pdf]]

> File: `06-references/neuronexus/Radiens-Technical-Documentation.pdf`. Page numbers below are the manual's printed page numbers.

---

## For our setup — load-bearing facts (verified 2026-06-19)

> [!important] Mode (the thing that blocked us for 2 days)
> Correct Allego **system mode** for our XDAQ Core Gen-1 + Intan RHD XR headstage = **"XDAQ One (G1) with XR Headstage"** (`XDAQ_ONE_REC`). **Naming trap:** the chassis is badged XDAQ **Core**, but the mode that detects is "XDAQ **One** (G1)…" — the dropdown *also* has "XDAQ Core (G1)…" which does **not** work for us. Pick the mode that yields `priSigs > 0`, not the one matching the chassis label (`XSR` = a different headstage; we use `XR`). `SMARTBOX_PRO` reports `priSigs=0` (connects + scans but wrong headstage profile); `INTAN_USB2` = legacy eval board. Manual: **Mode, p33**. Full story: [[first-headstage-connection]].

> [!warning] Channel naming — NOT editable in Allego
> The **Signal Map** (p37) is a **read-only** routing visualization — it shows site → amplifier-channel (`pri_N`) → port, and updates in real time, but you **cannot rename channels** there (no double-click edit). **XDAT data files are sorted by preamplifier channel (`pri_N`), not by site.** Custom per-channel labels come only from **loading a probe map**; custom probe maps are **built by NeuroNexus** (FAQ p176: "if your electrode is customized... contact us"), not editable in-GUI.
> **→ Our approach:** keep the channel **selection**, treat the [[first-headstage-connection#8.1 Channel map|§8.1 channel map]] as source of truth (Data Channel Index 0 = `pri_0` = `D/1` = M1 EEG+, … index 11 = `pri_11` = `D/12` = M2 EMG−), and apply EEG/EMG names in **offline analysis** by index. Optionally request a custom mouse-EEG probe map from NeuroNexus for in-software labels.

**Channel selection (System tab → Signals, p38):** the **Available Channels** per port auto-populate on headstage detection. Use each port row's `SELECT ALL` / `DESELECT ALL` and the `Select More` checklist to pick channels. UI is **1-indexed `D/n`**; `D/n` = Data Channel Index `n−1` = `pri_(n−1)`. Our recorded set = `D/1,2,3,4` (M1 EEG±/EMG±) + `D/9,10,11,12` (M2 EEG±/EMG±) = 8 channels.

**Electrodes tab (p60):** sets Headstage + Probe per port (dropdowns auto-generate the probe map). Ours = `hstg__passthrough_32` + a passthrough probe (custom 1:1 solder, not a geometric NeuroNexus probe). Probe wireframe / Site Selection / Order tools live here (p64–65).

**Referencing (Signal Processing → Reference Types, p70):** keep **CAR / software common-average OFF** for our bipolar EEG/EMG montage (would cross-contaminate the +/− pairs). EEG = `EEG+ − EEG−` computed offline.

**Recording vs Streaming:** **`Record` drives our session daemon** (→ Frigate video session, same path as a real Radiens R_ON). For connection/signal checks use **`Stream` only**. Recording file name/location set in **Settings** (p29).

**Cable Length (p38):** most modes (incl. ours) auto-calibrate cable delay; the manual notes adjusting it can also *help headstage detection* — worth remembering if a headstage ever fails to enumerate.

**Offline viewing:** recorded XDAT data is viewed in **Videre** (FAQ p177) — Data Sources tab → replay button → Monitor. File formats: open/non-proprietary, NeuroExplorer + kilosort2 + MATLAB/Python/R friendly (p177).

---

## Custom sensor maps — `csv2sensor` (our 2-mice map)

Allego can't rename channels, but you **can** load a **custom sensor** so the 8 used channels map to logical **site numbers + grouped geometry** (closest thing to labels). NeuroNexus's **`csv2sensor`** CLI builds the `.hstg` + `.prb` files from CSV.

- **Tool + source CSVs** stored in `06-references/neuronexus/sensor-maps/` (`csv2sensor-linux-x86_64`, `csv2sensor-README.md`, `2mice32.csv`, `2mice32_probe.csv`, plus the `mouse1_*` single-mouse test pair).
- **Output dir** (where Allego reads devices): `/home/skimlab/radix/devices/`. Generated: `hstg__usrdef_2mice32.hstg`, `probe__usrdef_2mice32_probe.prb`.
- **CSV format:** headstage = `ntv_chan, site_num` (native amp channel → site); probe = `site_num, center_x, center_y, radius, shape` (+ optional `wfx/wfy` wireframe outline). No name/label column exists — identity is site number + position. csv2sensor scales positions ~÷10 (25 µm → 2.5); relative layout preserved. Output filename = `usrdef_<input-csv-name>`, so name the CSV what you want the device called.

> [!warning] Gotcha — map ALL native channels of the headstage
> csv2sensor sets headstage **size = number of CSV rows**, and native indices must be **0…(size−1)**. A partial file listing non-contiguous natives (e.g. only `0–3, 8–11` in an 8-row file) makes Allego treat `8–11` as out-of-range → every channel shows `Site Number -23` / `no-site`. **Fix:** map **all 32** native channels (used → sites 1–8, the rest → sites 9–32 parked off-grid); the probe must define all 32 sites too. Our `2mice32` files do this. (The `mouse1` 4-row file worked only because its natives `0–3` happened to be contiguous from 0.)

**Regenerate:**

    cd 06-references/neuronexus/sensor-maps
    ./csv2sensor-linux-x86_64 -type headstage 2mice32.csv        # -> /home/skimlab/radix/devices/hstg__usrdef_2mice32.hstg
    ./csv2sensor-linux-x86_64 -type probe    2mice32_probe.csv    # -> .../probe__usrdef_2mice32_probe.prb

**Load in Allego:** Electrodes tab -> Port D -> **check "Use local devices"** (toggle off/on to force a re-scan if a just-generated device is missing from the dropdown) -> Headstage = `Usrdef 2mice32`, Probe = `Usrdef-2mice32-Probe` -> **Apply**. Then System -> Signals -> Port D -> select **D/1,2,3,4,9,10,11,12** (= native 0–3 + 8–11).

**Our 2-mice map** (built 2026-06-19; M1-only test first, then full-32): native `0-3` -> sites `1-4` (M1 EEG±/EMG±), native `8-11` -> sites `5-8` (M2 EEG±/EMG±), other 24 natives parked at sites `9-32`. Full site/signal table: [[first-headstage-connection]] §8.1.

## Section map (jump into the embedded PDF by page)

| Topic | Page | Topic | Page |
|---|---|---|---|
| Checking Hardware Connection | 20 | **Mode** | **33** |
| Interface Overview / Module Drawer | 25 | Sample Rate | 35 |
| Configuration (System/Electrodes/SigProc) | 26 | **Signal Map** (read-only) | **37** |
| Monitor | 27 | Cable Length | 38 |
| Impedance | 27 | **Signals (channel select)** | **38** |
| Signal Metrics / Spike Grid / Sorter | 27–28 | Stimulation | 40, 46 |
| Settings (rec file name/location) | 29 | Analog/Digital Out Control | 41–44 |
| Save Workspace & User Profile | 29 | Digital In Triggering | 45 |
| **Electrodes** (headstage/probe) | **60** | Probe Wireframe / Site / Order tools | 64–65 |
| Headstage / Probe dropdowns | 60, 62 | **Signal Processing / Reference Types** | **68–70** |
| Probe spans multiple ports | 63 | Preset Filters | 71 |
| FAQ — probe map not found | 176 | FAQ — file formats / Videre | 177 |

---

## Related
- [[signal-mapping-guide]] — ⭐ step-by-step signal-mapping guide for any operator (real-world ↔ Allego, EEG/EMG, csv2sensor)
- [[first-headstage-connection]] — bring-up + §8.1 channel map (the rename workaround)
- [[radiens-api-reference]] — the Python `AllegoClient` SDK (sits on top of this software)
- [[xdaq-core-gen1-ubuntu-driver]] — device/driver layer beneath Allego
- [[01-infrastructure/system-overview]]

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

**Channel selection (System tab → Signals, p38):** the **Available Channels** per port auto-populate on headstage detection. Use each port row's `SELECT ALL` / `DESELECT ALL` and the `Select More` checklist to pick channels. UI is **1-indexed `D/n`**; `D/n` = Data Channel Index `n−1` = `pri_(n−1)`. ⚠️ **The `D/1,2,3,4` + `D/9,10,11,12` set below is the JUNE TWO-MOUSE ERA and is superseded.** Since the eight-position cohorts we record **all four ports**, with each port carrying two animal slots: **`/1` electroencephalogram and `/2` electromyogram for slot 1, `/33` and `/34` for slot 2**, and everything else on the chip left as wire-free floor. Canonical map: `02-procedures/CANONICAL-allego-channel-selection.md`.

**Electrodes tab (p60):** sets Headstage + Probe per port (dropdowns auto-generate the probe map). Probe wireframe / Site Selection / Order tools live here (p64–65). **Current setting, verified in the metadata of every recording since 2026-07-14: `hstg__passthrough_64` + `probe__default_8x8` on all four ports.** The `hstg__passthrough_32` in the June notes belongs to the two-mouse era and is no longer in use. **Passthrough is the CORRECT entry for us**, and the manual says so on p62: passthrough entries are the generic 1:1 pinout, intended for exactly our case, "an EIB/breakout board where the site numbers and their locations on the substrate are not necessary".

**Referencing (Signal Processing → Reference Types, p70):** keep **Common Average, Virtual and Paired referencing ALL OFF**. Common average would mix all 256 channels, **including the wire-free amplifier inputs that are the control our whole connection test depends on**, into every animal channel.

> [!danger] CORRECTED 2026-08-18 — this line used to say "EEG = `EEG+ − EEG−` computed offline"
> **THAT WAS WRONG AND IT IS THE PROJECT'S MOST EXPENSIVE MISREADING.** The signals reaching the file are **ALREADY BIPOLAR**: each is a difference computed in hardware, on the chip, before the analog-to-digital converter. `/1` **is** the electroencephalogram and `/2` **is** the electromyogram. **NEVER subtract one saved channel from another.**
> A whole second analysis pipeline was built on the old sentence and survived until 2026-08-10, producing "EEG" that was actually EEG minus EMG and "EMG" that was one empty pad minus another. It was deleted. See `eeg-emg-analysis/README.md` § "Things that are true on this rig and cost weeks to learn".

**Recording vs Streaming:** **`Record` drives our session daemon** (→ Frigate video session, same path as a real Radiens R_ON). For connection/signal checks use **`Stream` only**. Recording file name/location set in **Settings** (p29).

**Cable Length (p38):** most modes (incl. ours) auto-calibrate cable delay; the manual notes adjusting it can also *help headstage detection* — worth remembering if a headstage ever fails to enumerate.

---

## Signal Processing tab — the filters (added 2026-08-18)

The tab does two unrelated jobs: **filter stages** and **reference types**. Reference types are covered above, and the answer there is "all off".

### The three stages (p68–69)

| stage | where it runs | touches the SAVED file? | undoable offline? |
|---|---|---|---|
| **Hardware** | on the Intan preamplifier chip, before the analog-to-digital converter | **YES** | **NO, EVER** |
| **Data** (Software Stage 1) | in Allego, after acquisition | **YES** | no |
| **Visualization** (Software Stage 2) | display only, Monitor tab | **no** | not applicable |

### What our rig actually has, read from the recordings

Straight out of `sig_proc_spec` in the `.xdat.json` of **every recording from 2026-07-14 to 2026-08-18**, unchanged:

```
HW BANDPASS (1.09766971131144, 475.173812170515) Hz   ports A B C D
HW BANDPASS (1, 475)                             Hz   ports E F G H
software_stage_1 = []
```

✅ **`software_stage_1` is empty in all of them, so no software filter has ever touched our recorded data.** The saved file is raw apart from the chip. **Keep it that way.**

⭐ **Why the numbers look odd and "automatic".** Ports E to H have no headstage attached and report exactly `1` and `475`, which is the **requested** value. Ports A to D have real chips and report `1.0977` and `475.17`, which is what the Intan RHD chip could actually **realize** from its internal register settings. You ask for 1 Hz, the chip answers with the nearest value it can build. Allego is not choosing a filter for you; it is echoing back the achieved value of a setting made once. The 1 Hz request itself comes from the manual, p70: *"While the headstages in Allego support frequencies as low as 0.1 Hz, it is recommended to set a minimum of 1 Hz to correct for low-frequency amplifier noise."*

### How you change one (p71–72)

**Configure → select the stage (Hardware / Software Stage 1 / Software Stage 2) → choose the filter type → fill in the frequency fields → Add Filter.** Filters already in a group each carry three buttons: **edit** properties, **arrow** to reorder (filters apply in displayed order), **remove**. If you are only looking at the applied-filter list you cannot edit anything; the editing lives in Configure.

Valid ranges the manual allows: **lowpass 1–300 Hz · highpass 300–5000 Hz · bandpass 0.1 Hz–20 kHz · bandstop 1 Hz–20 kHz · notch 50–60 Hz** with a default notch bandwidth of 2, so a 60 Hz notch attenuates 59–61 Hz.

⚠️ The manual documents a "streaming must be off" lock **only for stimulation parameters** (p50), not for filters. If the hardware fields are greyed out, stop the stream and try again. There is also **no filter setter anywhere in the radiens 4.0 Python API** — `AllegoClient` exposes `set_sampling_freq`, `set_sensor`, `set_recording`, `set_recording_config`, `set_analog_out_high_pass` (that one is the audio monitor output, not the data), and nothing for the filter stages. So this is a graphical-interface-only setting either way.

### 🛑 NEVER ADD A 60 Hz NOTCH, AT ANY STAGE

Our connection test measures **60 Hz amplitude against wire-free amplifier inputs recorded in the same file**, and a per-chip collapse in that 60 Hz is how a floating headstage ground is detected at all (2026-08-07, and again 2026-08-18). **A notch erases that evidence permanently and silently.** The same goes for any bandstop covering mains.

### Does the hardware filter matter if we do all the analysis offline from raw? Partly.

**The saved file IS the hardware-filtered data.** A filter applied before the analog-to-digital converter cannot be undone by any amount of offline processing.

- **The 475 Hz upper edge is harmless and useful.** We sample at 1000 Hz, so the Nyquist limit is 500 Hz and this is doing necessary anti-alias work. Nothing in our analysis looks above 300 Hz.
- 🔴 **The 1.0977 Hz lower edge is real and we have already paid for it.** It irreversibly attenuates 0.5 to 1.1 Hz, the bottom of the delta band. This is why `BAND_DELTA` was moved from 0.5 to 1.0 Hz on 2026-08-08. The staging band `BAND_DELTA_STAGING` is still 0.5 to 4.5 Hz, and **between 4.7 % and 16.1 % of its power comes from that attenuated region** (measured per animal on 2026-08-10, deliberately left unchanged because moving it re-scores every recording). Full reasoning lives in `eeg-emg-analysis/core/qc_thresholds.py`.
- ✅ **It does not break the connection criterion.** The falsification suite tested the acquisition high-pass explicitly against the scale-free guard and it lands within ±0.11, so it does not trip the band-limit refusal that a real band-pass would.

📌 **Recommendation: leave the hardware band-pass at 1 Hz.** Dropping to 0.1 Hz would recover genuine 0.5 to 1 Hz delta, but chronically implanted electrodes drift, and slow wander would spend amplifier headroom against a ±6377 µV rail. It would also make new recordings non-comparable with every earlier one. **That is a pre-registered scientific decision with a re-score attached, not a settings tweak.** The 1.1 Hz corner belongs in the methods section of the paper as a stated limitation.

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

> [!danger] A custom sensor map CHANGES `site_num`, and the analysis is written in site numbers
> `eeg-emg-analysis/core/criteria.py:open_xdat` builds every channel label from the file's own `biointerface_map`, as `port` + **`site_num`**. Every `A/1`, every `A/33`, the wire-free floor definition `/3`–`/16` and `/35`–`/48`, and the whole `CohortSpec` are expressed in site numbers. **Load a custom map mid-cohort and the analysis silently reads different channels, with no error raised.** If a custom map is ever adopted: do it **between cohorts**, keep the native-to-site identity written down, and re-run all four test suites before trusting a single number.

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
- [[live-signal-quality-terms]] — ⭐ what every Signal Metrics control and column means, and which ones are useless for field potentials
- [[signal-mapping-guide]] — ⭐ step-by-step signal-mapping guide for any operator (real-world ↔ Allego, EEG/EMG, csv2sensor)
- [[first-headstage-connection]] — bring-up + §8.1 channel map (the rename workaround)
- [[radiens-api-reference]] — the Python `AllegoClient` SDK (sits on top of this software)
- [[xdaq-core-gen1-ubuntu-driver]] — device/driver layer beneath Allego
- [[01-infrastructure/system-overview]]

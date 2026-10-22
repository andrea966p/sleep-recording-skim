---
tags:
  - procedure
  - open-ephys
  - xdaq
  - eeg
  - emg
  - sleep
  - acquisition
  - setup
created: 2026-07-23
status: draft-validated-1-headstage
---
# Open Ephys GUI Setup for the XDAQ Core (Sleep EEG/EMG)

> [!abstract] TL;DR — for non-technical readers
> **What this is.** Step by step for driving our existing NeuroNexus/Kontex **XDAQ Core** from the free, open-source **Open Ephys GUI** instead of paid Allego, for chronic sleep EEG/EMG with our Intan **RHD2216** headstages. We validated on 2026-07-23 that OE fully enumerates and controls the Core (one headstage on port B detected, 32 channels), so this is a real license-free path.
> **Why it exists.** Part of the 16→32 mouse DAQ decision ([[daq-ecosystem-comparison-xdaq-vs-openephys]]). OE software is $0 and could give us per-animal record control we cannot get in Allego. This guide is the hands-on setup so anyone can rebuild the workflow.
> **How to read it.** §1 install + the one-time fix that makes the plugin load. §2 build the signal chain. §3 configure the source for sleep. §4 impedance check. §5 recording (and the per-animal-record win). §6 the 60 Hz reality check. §7 gotchas.

> [!warning] Only one program can own the XDAQ at a time
> Allego and Open Ephys both grab the Opal Kelly USB (`151f:0130`). **Close Allego completely before launching OE**, and vice versa. Running both = device-open failure or crash.

Related: [[2026-07-21-openephys-acquisition-board-scale-up-option]], [[eeg-60hz-saga]], [[allego-electrode-setup-sleep64]] (the Allego equivalent), [[intan-rhd2216-reference]].

---

## 1. Install + the one-time plugin-load fix

- OE GUI installed from `open-ephys-gui-v1.1.0.deb` → binary at `/usr/local/bin/open-ephys`. Plugin API = **api10**.
- XDAQ plugin = **XDAQ-OE v0.4.4-API10**, installed via the GUI's **Plugin Installer** (File → Plugin Installer → search "XDAQ" → Install).

> [!danger] The plugin does NOT work out of the box on GUI 1.1.0 — packaging path bug
> The XDAQ plugin is built for a non-versioned `shared/` folder, but GUI 1.1.0 uses `shared-api10/`. Symptoms in order: first "***ERROR*** libxdaq_device.so: cannot open shared object file" (won't appear in Processor List), then after that "XDAQ appears but cannot be used / device dead" (managers directory not found). **Root cause + fix:** create two symlinks so the plugin's `shared/XDAQ-OE` path resolves to the real `shared-api10`:
> ```
> cd ~/.config/open-ephys
> ln -sfn shared-api10 shared
> ln -sfn ../libxdaq_device.so shared-api10/XDAQ-OE/libxdaq_device.so
> ```
> After this, launch normally (`/usr/local/bin/open-ephys`) — no `LD_LIBRARY_PATH` needed. Re-apply if you reinstall/upgrade the plugin (installer overwrites the dirs). Report the packaging bug to Kontex/OE so a fixed build removes the need.

Verify the plugin resolves (no env var): `ldd ~/.config/open-ephys/plugins-api10/XDAQ-OE.so | grep xdaq` should show `libxdaq_device.so => .../shared/XDAQ-OE/libxdaq_device.so`, not "not found".

---

## 2. Build the signal chain

Drag plugins from the **Processor List** (left panel) into the **Signal Chain** (bottom). Order = source → filters → sinks. A **Record Node** records everything to the plugin immediately to its **left**. Play button = **Acquire** (stream, no save); Record button = acquire **and** save.

Recommended sleep chain:

```
XDAQ  →  Record Node (RAW)  →  Channel Map  →  Bandpass Filter  →  LFP Viewer
                                                      └─ (optional) Common Avg Reference / Notch
```

- **XDAQ** (source) — the Core. See §3.
- **Record Node (RAW)** right after the source — saves the unprocessed data (best practice: keep raw, filter only for viewing/QC). See §5.
- **Channel Map** — drop the empty-floor channels. Our RHD2216 enumerates as **32 channels**; **CH1–CH16 are real amplifiers, CH17–CH32 are the empty floor** (quiet=grounded / all-rail=float, same as Allego). Right-click each unwanted channel → "Disable input channel N". **CH1 must stay enabled** or nothing passes downstream. Narrow to the channels your montage actually uses (bipolar EEG pair + neck EMG per [[allego-electrode-setup-sleep64]]).
- **Bandpass Filter** — for viewing/scoring. Set `low_cut`/`high_cut` per band (e.g. EEG ~0.3–40 Hz). Recording upstream stays wideband.
- **LFP Viewer** — live waveforms (the sink). Add **Spectrum Viewer** too if you want a live 60 Hz check.

To reduce a stream to a subset for a viewer, use the Channel Map (drag to reorder, right-click to disable). Channel Map keeps separate config per stream (click the vertical bars on the **right** of its editor to pick the stream).

---

## 3. Configure the XDAQ source for sleep

XDAQ editor controls (top of the source plugin):

- **Rescan** (circular-arrow) — re-scan SPI ports for headstages. **Run this every time you plug/unplug a headstage** (that's how we got port B to show).
- **Sample Rate** dropdown — 1–30 kHz. **1 kHz is the floor and is plenty for sleep** EEG/EMG (what we used).
- **Bandwidth** (low/high cut) — analog filters on the Intan chip; the chip snaps to nearest legal value. Keep wide for recording (e.g. low ~0.1–1 Hz, high left at default) and do sleep-band filtering in the Bandpass Filter processor.
- **DSP** button (yellow = on) — DSP offset removal (digital high-pass) to kill electrode drift; set cutoff ~1 Hz for sleep.
- **Fast Settle** — ties a digital input to amplifier reset; leave off unless you need artifact blanking.
- **AUDIO OUT** — monitor up to 2 channels on the board's audio jack.

Port naming in OE: **P1=port A, P2=port B, P3=C, P4=D**; slots 1–4 per port (Core uses 2 real per port).

---

## 4. Impedance check (replaces Allego GetIntanImpedance)

- Open the impedance interface via the **window/tab button** at the top of the XDAQ editor.
- Measure **while NOT acquiring** (same rule as Allego — never measure impedance mid-stream).
- This is our pre-recording electrode QC: confirm the bipolar EEG + EMG channels are in physiological range and catch the open-frontal-electrode failure ([[eeg-60hz-saga]]) before wasting a run.

---

## 5. Recording + the per-animal control win

**Record Node basics:**
- Set the save directory via the **button at top-right** of the Record Node editor (shows a live disk-space monitor).
- Channel select: click the **vertical bars on the left** (stream buffer monitor) → `ALL` / `NONE` / `RANGE` ("1:16" Matlab-style). **Channels not selected when recording starts cannot be recovered.**
- **Format:** default **Binary**; **Open Ephys** and **NWB** formats installable via Plugin Installer. (Only one NWB Record Node at a time.) Binary is the simplest for our analysis migration — see the format question in [[daq-ecosystem-comparison-xdaq-vs-openephys]].

> [!tip] Independent per-animal recording (the thing Allego cannot do)
> Each headstage = its own **data stream**. With multiple headstages you can either (a) use **one Record Node and enable/disable per stream**, or (b) drop **one Record Node per animal**, each to its own directory, started/stopped independently. That is the per-mouse start/stop control our current Allego + daemon setup can't do (one global R_ON, see [[project_multiuser_recording_schedules]]). This is a genuine reason OE could beat Allego for staggered multi-mouse schedules — validate it when we have 2+ headstages.

---

## 6. The 60 Hz reality check

Two software tools exist, but be honest about limits:
- **Common Average Reference (CAR)** processor — pick **Reference channels** (their average is subtracted) and **Affected channels**, with a **gain %** slider; works within one stream only. CAR helps when many channels share the SAME common-mode noise. With only a couple of bipolar channels per mouse it has little to average, so expect modest benefit. Place it **after the RAW Record Node** so raw stays intact.
- **Notch Filter** processor — add for a 60 Hz notch to clean the live view.

> [!important] Software will not fix our 60 Hz — the electrodes will
> Our differential 60 Hz ≈ common-mode floor × electrode-Z imbalance, driven by **open EEG electrodes** (the `/1` channel — *not* a frontal-vs-parietal distinction; corrected 2026-08-01). A notch/CAR is cosmetic for viewing; it does not recover a bad electrode. OE does not change that physics.
>
> **The hum amplitude IS the contact measurement** and is more useful than an
> impedance snapshot: connected channels sit at **9–90 µV** in the 55–65 Hz
> band, open ones at **1000–4700 µV**, cleanly bimodal with the valley at
> 134 µV. Impedance predicts *which channel is connected*, never *for how long*.
> The real fix is electrical contact; **the free rig-side checks come before any
> surgical conclusion.** See [[2026-08-03-two-8-mouse-runs]].

---

## 7. Gotchas

- **Close Allego before OE** (device ownership) — the big one.
- **Rescan** after any headstage change, or channels stay 0.
- Re-apply the §1 symlinks after any plugin reinstall/upgrade.
- Keep the RAW Record Node first; put filters/reference AFTER it so you never lose unprocessed data.
- Sleep sample rate 1 kHz is fine; don't crank to 30 kHz (needless data for sleep).

## Validation status (2026-07-23) — END-TO-END VALIDATED

> [!success] OE fully drives our XDAQ Core, license-free — proven end to end
> Acquire (live waveforms, no crash) → impedance QC (XML export) → **recorded 42 s, 16 ch, Binary format, µV units, no railing/clipping, reads straight into numpy.** License-free control of our existing Core is real.

- ✅ Plugin loads (after §1 symlink fix); managers + FPGA resources resolve.
- ✅ XDAQ source enumerates the Core; **1 headstage on port B (P2-1) = 32 ch**, matching Allego's 16 real + 16 floor.
- ✅ **Acquire** streams live; no crash (the earlier crash was the stale saved Acquisition-Board config).
- ✅ **Impedance** interface works, exports XML (`~/Downloads/OE imp with mouse split ground`). CH1–16 real, CH17–32 floor. C0/CH1 best (~0.585 MΩ); most others 2–6 MΩ — interpret against the montage map ([[allego-electrode-setup-sleep64]]); pattern echoes [[eeg-60hz-saga]].
- ✅ **Recording** = Open Ephys **Binary** format: `structure.oebin` (JSON meta) + `continuous/<stream>/continuous.dat` (int16, ×`bit_volts`=0.195 → µV) + `timestamps.npy`/`sample_numbers.npy` + `events/`. Trivially readable in Python (`np.fromfile(dtype='<i2').reshape(-1, nch)`).

> [!warning] Two caveats found in the first recording — fix before real runs
> 1. **Sample rate did NOT stick at 1 kHz — it recorded at 10 kHz** (`structure.oebin: sample_rate 10000`). That is **~28 GB/day/mouse** vs ~2.8 GB at 1 kHz. Set the rate AND confirm `structure.oebin` reads `1000` before trusting a run.
> 2. **Record Node was at the END of the chain → recorded bandpass-FILTERED data** (channel `history: XDAQ → Channel Map → Bandpass Filter → LFP Viewer → Record Node`). Put a Record Node **immediately after XDAQ** to keep raw.

- ⏳ Still to do: montage-mapped impedance read; **multi-headstage per-animal record test** (the Allego-beating feature); confirm 1 kHz sticks; firmware "Legacy" warning follow-up with Kontex (do NOT reflash the production Core without checking KC); decide OE-Binary vs XDAT for the analysis pipeline ([[daq-ecosystem-comparison-xdaq-vs-openephys]]).

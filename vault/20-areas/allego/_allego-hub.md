---
type: hub
area: allego
status: active
created: 2026-10-22
summary: "Allego / Radiens software on e10ubuntu: channel selection, Monitor, presets, sensor maps, Python client limits and the launch gotchas"
tags: [hub, allego, radiens]
---

# Allego

> [!abstract] What this is
> The acquisition software (Allego, built on Radiens, by NeuroNexus/Kontex) that talks to the XDAQ on `e10ubuntu`: which channels to select, the Monitor, workspaces and presets, sensor maps, and the Python client.
> It covers how the software behaves and fails; the electrodes and grounding are in [[_eeg-rig-hub]], and the console that starts runs is in [[_recording-console-hub]].
> The Open Ephys route for the XDAQ is [[openephys-gui-setup-xdaq-sleep-eeg]].

## Current state
- 2026-10-23: Andrea: keep Allego without `--disable-gpu` (`rig-check.sh` now warns if the flag is present); the switch to the Open Ephys GUI is for later. [[2026-10-23]]
- 2026-10-22: read-only check: Allego launches without `--disable-gpu` (launcher `Exec` line has no flag), kernel 7.0.0-28 is pinned and held, and `allegoserver` has the GUI as its parent (not orphaned). The flag-vs-Mesa-crash trade-off is still open. [[allego-blank-monitor-canvas-texture-limit]]
- 2026-09-30: after a fresh launch the stream ran 30x real time while Allego said 1000 Hz; the console pre-flight still checks only the label. [[allego-stream-30x-rate-label-lies]]
- 2026-09-16: the Monitor drew nothing because the 262-signal canvas exceeded the software renderer's 8192 px texture limit; fixed by dropping `--disable-gpu`. An orphaned `allegoserver` can make a healthy rig look dead. [[allego-blank-monitor-canvas-texture-limit]] [[allego-orphaned-server-blocks-the-rig]]
- 2026-09-11: bench test: `set_recording('off')` works, the file size lags about 30 s, and radiens 4.0.0 has no per-port recording. [[2026-09-11-allego-control-bench-test]] [[radiens-api-reference]]
- 2026-08-24: the Allego app crashed in Mesa mid-recording and a 6.5 GB log storm followed; app death ends the recording, a frozen GUI does not. [[allego-mesa-gpu-crash-and-log-storm]]
- 2026-08-23: `allegoserver` left a thread spinning a core after the GUI closed (+10 W, +11 °C); seen again 2026-09-29. [[allegoserver-runaway-thread-thermal]]
- 2026-08-03: channel selection settled by measurement: `/1`, `/2`, `/33`, `/34` on every port for the bipolar layout. [[CANONICAL-allego-channel-selection]]

## Start here
- [[CANONICAL-allego-channel-selection]]: which channels to select
- [[allego-electrode-setup-sleep64]]: electrode setup and the `sleep64` map
- [[radiens-software-reference]]: the primary software reference, page by page
- [[live-signal-quality-terms]]: reading the live numbers
- [[starting-the-rig-after-a-restart]]: relaunching Allego and checking mode and rate

## Rules that must not be broken
- Launch Allego without `--disable-gpu` (confirmed by Andrea 2026-10-23), on kernel 7.0.0-28; do not move the kernel (the hold is deliberate). [[allego-blank-monitor-canvas-texture-limit]] [[2026-10-23]]
- After any launch, check `XDAQ_ONE_REC` and 1000 Hz, then stream about 10 s and compare `stream.time_range` with wall clock (about 1.0x). [[allego-stream-30x-rate-label-lies]]
- Before any other theory for "no data", check the `allegoserver` parent PID; kill an orphan by PID, relaunch, and verify exactly one instance exists. [[allego-orphaned-server-blocks-the-rig]]
- 🛑 Never `pkill -f /opt/allego/allego`: it kills your own shell and `pkill -f "^/opt/allego/allego"` creates an orphan. [[allego-mesa-gpu-crash-and-log-storm]]
- A frozen GUI is not lost data: judge a recording by bytes on disk and the rms of a known channel. App death does end the recording. [[allego-mesa-gpu-crash-and-log-storm]]
- Any "is it growing?" check shorter than about 35 s is a false negative, and a script that asserts on growth must stop the recorder in a `finally`. [[2026-09-11-allego-control-bench-test]]
- Recording is global (one box, one record button, one file). radiens 4.0.0 is installed; PyPI has 4.0.1 (seen 2026-10-22, untested here), so do not upgrade to fix it without a bench test. [[radiens-api-reference]]
- For the bipolar EEG/EMG layout the signals are already bipolar: select `/1`, `/2`, `/33`, `/34` and never subtract EEG from EMG. The unipolar layout selects `/18` to `/23`. [[CANONICAL-allego-channel-selection]] [[rig-layout-and-recording-settings]]
- The Allego 60 Hz notch is display only; the saved data are raw. [[eeg-60hz-saga]]
- Impedance cannot be measured while streaming. [[allego-mesa-gpu-crash-and-log-storm]]

## Open items
- [x] 2026-10-23: no Chan-height test needed; Allego stays without the flag (Andrea). [[2026-10-23]]
- [ ] Later (Andrea, 2026-10-23): move acquisition from Allego to the Open Ephys GUI with our XDAQ. A big switch for the recorder code and the session daemon; not scheduled. [[openephys-gui-setup-xdaq-sleep-eeg]] [[2026-10-23]]
- [ ] Build a measured-rate check (`time_range` against wall clock) into the console pre-flight. [[allego-stream-30x-rate-label-lies]]
- [ ] Report the Mesa crash and the `autoScanWorker` retry loop to Kontex. [[allego-mesa-gpu-crash-and-log-storm]]
- [ ] The IIR filter-design error when changing the Monitor band is deferred (display only). [[allego-iir-filter-design-errors]]
- [ ] Whether Save Workspace survives a full hardware re-enumeration is untested. [[allego-settings-save-restore]]

## Everything here
![[area.base]]

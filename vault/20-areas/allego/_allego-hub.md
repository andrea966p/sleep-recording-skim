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
- 2026-10-28: e10 runs Allego/Videre 4.1.2 (installed and held; NeuroNexus moved to Radiens 4, Standard free vs Pro $2,000/yr, Legacy offer unanswered) and `radiens-core` 0.1.2 is in the production venv. **Per-port recording works** (two ports at once, separate files, mode `XDAQ_CORE_REC`) and the console was ported to it and runs in production since 2026-10-29 09:15 KST. Allego does not keep its rate or split across launches (a fresh launch came up at 30 kHz, split off), and `allegoserver` died at 18:46 with the cause unknown. [[2026-10-28-per-port-recording-bench-test]] [[2026-10-28-per-port-console-port]] [[2026-10-28-allegoserver-death-and-fresh-launch-defaults]] [[2026-10-28-radiens-4-tiers-and-legacy-licence]]
- 2026-10-23: Andrea: keep Allego without `--disable-gpu` (`rig-check.sh` now warns if the flag is present); the switch to the Open Ephys GUI is for later. [[2026-10-23]]
- 2026-10-22: read-only check: Allego launches without `--disable-gpu` (launcher `Exec` line has no flag), kernel 7.0.0-28 is pinned and held, and `allegoserver` has the GUI as its parent (not orphaned). The flag-vs-Mesa-crash trade-off is still open. [[allego-blank-monitor-canvas-texture-limit]]
- 2026-09-30: after a fresh launch the stream ran 30x real time while Allego said 1000 Hz; the console pre-flight still checks only the label. [[allego-stream-30x-rate-label-lies]]
- 2026-09-16: the Monitor drew nothing because the 262-signal canvas exceeded the software renderer's 8192 px texture limit; fixed by dropping `--disable-gpu`. An orphaned `allegoserver` can make a healthy rig look dead. [[allego-blank-monitor-canvas-texture-limit]] [[allego-orphaned-server-blocks-the-rig]]
- 2026-09-11: bench test: `set_recording('off')` works, the file size lags about 30 s, and radiens 4.0.0 had no per-port recording (retracted for Allego 4.1.2 on 2026-10-28). [[2026-09-11-allego-control-bench-test]] [[radiens-api-reference]]
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
- After every launch and every restart, check mode `XDAQ_CORE_REC` (`XDAQ_ONE_REC` on Allego 3.11.3), set 1000 Hz and `split_files_by_port` again (a fresh launch comes up at 30 kHz with the split off, a restart can reset the rate), and after any rate change call `scan_ports()` before streaming. Then stream about 10 s and compare `stream.time_range` with wall clock (about 1.0x). [[allego-stream-30x-rate-label-lies]] [[2026-10-28-allegoserver-death-and-fresh-launch-defaults]] [[2026-10-28-per-port-recording-bench-test]]
- Before any other theory for "no data", check the `allegoserver` parent PID; kill an orphan by PID, relaunch, and verify exactly one instance exists. [[allego-orphaned-server-blocks-the-rig]]
- 🛑 Never `pkill -f /opt/allego/allego`: it kills your own shell and `pkill -f "^/opt/allego/allego"` creates an orphan. [[allego-mesa-gpu-crash-and-log-storm]]
- A frozen GUI is not lost data: judge a recording by bytes on disk and the rms of a known channel. App death does end the recording. [[allego-mesa-gpu-crash-and-log-storm]]
- Any "is it growing?" check shorter than about 35 s is a false negative, and a script that asserts on growth must stop the recorder in a `finally`. [[2026-09-11-allego-control-bench-test]]
- One run per port: several ports can record at once into separate files, a stop must name its port (`stop_recording()` with no port stops everyone), and the recording configuration is shared and locked while any port records. Impedance and `restart()` are rig-wide and need the whole rig idle (no port recording, streaming off). 🛑 Never install `radiens` 4.0.1 (deprecated, broken); the old `radiens` 4.0.0 stays installed but must not be imported next to `radiens-core`. [[2026-10-28-per-port-recording-bench-test]] [[radiens-api-reference]]
- For the bipolar EEG/EMG layout the signals are already bipolar: select `/1`, `/2`, `/33`, `/34` and never subtract EEG from EMG. The unipolar layout selects `/18` to `/23`. [[CANONICAL-allego-channel-selection]] [[rig-layout-and-recording-settings]]
- The Allego 60 Hz notch is display only; the saved data are raw. [[eeg-60hz-saga]]
- Impedance cannot be measured while streaming. [[allego-mesa-gpu-crash-and-log-storm]]

## Open items
- [x] 2026-10-23: no Chan-height test needed; Allego stays without the flag (Andrea). [[2026-10-23]]
- [ ] Later (Andrea, 2026-10-23): move acquisition from Allego to the Open Ephys GUI with our XDAQ. A big switch for the recorder code and the session daemon; not scheduled. [[openephys-gui-setup-xdaq-sleep-eeg]] [[2026-10-23]]
- [x] 2026-10-28: the ported console enforces 1000 Hz and the split and reports the measured rate (ratio to wall clock); live since 2026-10-29 09:15 KST. [[2026-10-28-per-port-console-port]] [[allego-stream-30x-rate-label-lies]]
- [ ] Find out why `allegoserver` died at 18:46 on 2026-10-28 (cause unknown: no log line, no core dump, no kernel message). [[2026-10-28-allegoserver-death-and-fresh-launch-defaults]]
- [ ] Run a per-port recording over 24 to 72 h with several owners. [[2026-10-28-per-port-recording-bench-test]]
- [ ] Report the Mesa crash and the `autoScanWorker` retry loop to Kontex. [[allego-mesa-gpu-crash-and-log-storm]]
- [ ] The IIR filter-design error when changing the Monitor band is deferred (display only). [[allego-iir-filter-design-errors]]
- [ ] Whether Save Workspace survives a full hardware re-enumeration is untested. [[allego-settings-save-restore]]

## Everything here
![[area.base]]

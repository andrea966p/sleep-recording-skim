---
name: radiens-4-has-no-per-port-recording
description: "Per-port recording WORKS on Allego 4.1.2 + radiens-core 0.1.2 (measured 2026-10-28); it did not exist in radiens 4.0.0 on Allego 3.11.3. Old radiens must never be imported. Rules for stop, shared config, launch defaults. Detail in the vault"
metadata:
  type: reference
---

History: radiens 4.0.0 on Allego 3.11.3 had only a global `set_recording(mode)` (measured 2026-09-11). Since 2026-10-28 e10 runs Allego 4.1.2 and `radiens-core` 0.1.2 (in `/opt/neurosurveillance/venv`), and per-port recording works: two ports at once, one file per port (`allego_port<X>_<N>__uid...`), and a stop on one port leaves the others recording. The console books one run per port. Detail: [[2026-10-28-per-port-recording-bench-test]] · [[2026-10-28-per-port-console-port]] · [[2026-10-28-allegoserver-death-and-fresh-launch-defaults]]

- 🛑 Never `import radiens` (old): it cannot authenticate to Allego 4, and it breaks `radiens_core` in the same process (`duplicate file name common.proto`). Never install `radiens` 4.0.1.
- 🛑 `stop_recording()` with no port stops EVERY port, which ends other users' runs. Always name the port.
- 🛑 Licence: `restart()` only with the mode already in use (`XDAQ_CORE_REC`); no sign-in, plan or upgrade calls (NeuroNexus has not replied).
- 🔑 The recording config (folder, base name, `split_files_by_port`) is shared and locked while any port records. Impedance and restart need the whole rig idle.
- 🔑 After every launch or restart, re-set 1000 Hz and the split (a fresh launch came up at 30 kHz with the split off), and call `scan_ports()` after a rate change, or the stream stays dead at `[0.0, 0.0]`.
- Enums are IntEnum: compare `.name`, never `"R_ON"` strings.

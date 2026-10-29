---
type: experiment
area: allego
status: done
created: 2026-10-28
summary: "Bench test on Allego 4.1.2 + radiens-core 0.1.2: per-port recording works (two ports at once, separate files, one stops while the other keeps writing); shared config locked while any port records; impedance and restart need the whole rig idle; restart resets the rate to 30 kHz"
tags: [allego, radiens, recording, per-port]
---

# Per-port recording bench test (Allego 4.1.2, radiens-core 0.1.2)

> [!abstract] TL;DR
> - **Per-port recording works.** Ports A and B recorded at the same time into separate files. Stopping A froze A's file while B kept growing. This retracts "recording is global", which was true only for radiens 4.0.0 on Allego 3.11.3 ([[2026-09-11-allego-control-bench-test]]).
> - With "record ports in separate files" (`split_files_by_port=True`) each port gets its own file: `<base>_port<X>_<N>__uid<MMDD-HH-MM-SS>`. Andrea, 2026-10-28: keep that setting on permanently.
> - The recording configuration (folder, base name, split) is shared by all ports, and Allego refuses to change it while any port records.
> - Impedance and `restart()` both need the whole rig idle (no port recording, streaming off).
> - `restart()` with the same mode works but **resets the sample rate to 30000 Hz**. Set 1000 Hz again after every restart.

## Setup

- e10ubuntu, Allego 4.1.2-1455 (installed and held the same day, see [[2026-10-28-radiens-4-tiers-and-legacy-licence]]), server version `(5, 8, 0)`, mode `XDAQ_CORE_REC`, 1000 Hz, ports A to D enumerating 32 channels each.
- Client `radiens-core` 0.1.2 from `~/radiens-core-venv`. Scripts and logs were kept in the Claude session scratchpad. The data were junk from whatever was plugged in.
- Output went to `~/radix/port-tests/bench-20261028/`, which is not a source of the S3 or NAS archive jobs. The recording configuration was restored at the end of each script.
- Nothing licence-related was touched: no sign-in change, no plan or upgrade call. `restart()` was called only with the mode already in use.

## Results

### Test 1: two ports, staggered

| Time (s) | Action | Port A file `_data.xdat` | Port B file `_data.xdat` |
|---|---|---|---|
| 3 | start A | 0 B (size lags about 30 s, as on Allego 3) | none |
| 46 | config change while A records | refused: `recorder::No setting file name while recording is on` | |
| 46 | start B | 4,229,120 B | created, 0 B |
| 89 | both recording | 10,268,160 B | 4,229,120 B |
| 89 | stop A | final 12,060,160 B | |
| 132 | B alone | +0 B in 40 s | +4,229,120 B in 40 s |
| 132 | impedance on C while B records | refused: `Z_measure attempted during data acq`; B unaffected | keeps growing |
| 174 | stop B | | final 17,920,000 B |

- The global `record_mode` is ON while any port records. Per-port modes are in `record_mode_port_a` to `_h`.
- `recording.active_filename` showed only the first file's name, so it cannot identify a port's file.
- File names: `porttest_portA_0__uid1028-18-36-08` and `porttest_portB_0__uid1028-18-36-51`, each with `_data.xdat`, `_timestamp.xdat` and `.xdat.json`.

### Test 2: integrity, repeats, impedance, restart

- Both files have int64 timestamps with step 1 throughout (86,144 and 128,000 samples) and exactly 35 float32 channels: `port_X_0` to `port_X_31`, `aux_1`, `din_1`, `dout_1`.
- Stopping port A and starting it again made a new file, `_portA_1__uid…`.
- A second `start_recording(port="c")` while C was already recording was accepted silently and made no new file.
- Impedance with streaming off took 30.9 s and returned 128 values.
- `restart(mode=XDAQ_CORE_REC)` took 12.4 s and kept the mode and the four ports. It changed the rate from 1000 Hz to **30000 Hz** and left the recording configuration as it was. The rate was then set back with `update_core_config(samp_freq=1000.0)` (streaming off). The measured stream was 9.98 s per 10 s of wall clock.

## What this means for the console

- Several people can record on different ports at the same time. The console has to lock per port, not per rig.
- All ports share one folder and one base name, so the console keeps the configuration fixed (`~/radix/data`, `allego`, split on). It may set it only when the rig is idle, and otherwise it checks it.
- The console finds a port's file by name pattern, never from `active_filename`.
- A stop must name its port. `stop_recording()` with no port stops everyone.
- Impedance sweeps and restarts are rig-wide. They are allowed only when no port is recording.

## Still open

- [ ] Gen-1 XDAQ support on Allego 4 is still unconfirmed by NeuroNexus, though everything above worked on our Gen-1 Core.
- [ ] Per-port recording over many hours (24 to 72 h) with several owners has not been run yet.

---
tags: [infrastructure, hardware-sync, reference, radiens, api]
created: 2026-04-13
status: complete
---

# Radiens AllegoClient API — Digital I/O Reference

> [!abstract] TL;DR — for non-technical readers
> **What this is.** A reference for the parts of the NeuroNexus Radiens Python SDK that the daemon talks to — `AllegoClient`, digital I/O, recording state.
>
> **Why it exists.** Radiens is the electrophysiology recorder; everything the daemon does flows from polling this client. This page is the map.
>
> **How to read this page.** Look up the specific call you need (start recording, read DIO, get status). The package name + import path are at the top.

> [!quote] Paper-ready
> The session daemon interacts with the NeuroNexus Radiens acquisition system via the `radiens` Python SDK's `AllegoClient` interface, polling recording state once per second over gRPC and consuming digital-I/O channel state for hardware synchronization events.

> [!tip] Package Info
> Package: **`radiens`** (PyPI) — **v4.0.0** installed in `/opt/neurosurveillance/venv` (verified 2026-05-27). Import: `from radiens import AllegoClient`.
> Requires: Python 3.12+; an active Radiens license + the Radiens system (Allego) running alongside.
> Docs: <https://neuronexus.github.io/intro.html> · <https://nnx.mcoutput.com/1376106/Content/Home-Radiens.htm>
> (Earlier vault revisions called this `radiens-core` / `from radiens_core import …` — that was wrong; the package is `radiens`.)

> [!important] Verified live against the installed SDK (2026-06-19) — supersedes stale names below
> Introspected `AllegoClient` on the running system. **Correct system mode for our hardware** (XDAQ Core Gen-1 + Intan RHD2216 **XR-type** headstage) = **`SystemMode.XDAQ_ONE_REC`** — the Allego UI label is **"XDAQ One (G1) with XR Headstage"**. Using `SMARTBOX_PRO` reports `priSigs=0` (wrong headstage profile, even though it connects + scans); `INTAN_USB2` = legacy eval board, errors `raklib::cmd1 API error: Device not connected`. See [[first-headstage-connection]] for the full bring-up.
>
> **Actual method names** (the tables further down use older/aspirational names — these are what v4.0.0 exposes): `get_status`, `get_signals`, `signal_metrics`, `get_channel_metadata`, `get_available_sensors`, `set_sensor`, `set_sampling_freq`, `set_streaming`, `set_recording`, `set_recording_config`, `get_digital_out_states`, `set_digital_out_manual`, `set_analog_out_high_pass`, `set_stim_params`, `restart`, `spikes`, `spike_sorter`, `workspace`.
>
> **Status object** = `AllegoState`: `.system_mode` (→ `SystemMode.XDAQ_ONE_REC`), `.port_num_channels` (`{<Port.D:3>:32}`), `.connected`, `.recording` (`RecordingSpec(mode='R_OFF'|'R_ON', …)`), `.stream` (`StreamSpec(mode='S_ON'|'S_OFF', time_range, hw_mem_level)`), `.sample_freq`, `.cable_delay_spec` (per-port auto cable-delay; a non-zero `delay` with `is_auto=True` confirms a real headstage SPI handshake).
>
> **Detection probe (headless):** `python -c "from radiens import AllegoClient; print(AllegoClient().get_status().port_num_channels)"` → `{<Port.D:3>:32}` when detected, `{}` when not.
>
> **Signal samples:** `get_signals()` returns `(ndarray[channels×samples], list)` but the headless slice often returns **0 samples** (the cache is bound to the GUI cache head) — for live signal-quality (RMS/hum/saturation) use the Allego **Monitor** view, not a headless pull. `get_status().stream.time_range` advancing + low `hw_mem_level` confirms data is flowing.

## Key Methods for Hardware Sync

### Digital Output Control

| Method | Purpose |
|--------|---------|
| `get_dio_reg()` | Get current DIO register state (mode, per-channel config) |
| `set_dio_manual(chan_idx, state)` | Manually set a DOUT channel HIGH/LOW (mode must be MANUAL) |
| `set_dio_pulse(interval_sec, duration_sec, chan_idx)` | Configure a DOUT channel for periodic pulse mode |
| `set_dio_events(chan_idx, threshold, polarity)` | Configure DOUT to trigger on analog threshold crossings |
| `set_dio_gated(polarity)` | Set DIO gated mode polarity |

### Recording Triggers

| Method | Purpose |
|--------|---------|
| `enable_trigger(channel, port)` | Enable a DIN channel as a recording start/stop trigger |
| `disable_trigger(channel, port)` | Disable a trigger channel |
| `disable_all_triggers()` | Clear all trigger assignments |
| `get_trigger_state()` | Get current trigger configuration |

### Recording Control

| Method | Purpose |
|--------|---------|
| `get_status()` | Get system status including `status.recording.record_mode` |
| `start_recording(port)` | Start recording (we use this via poll, NOT via API control) |
| `stop_recording(port)` | Stop recording |

### Status Check

```python
from radiens import AllegoClient

with AllegoClient() as client:
    # Check DIO state
    dio_reg = client.get_dio_reg()
    print(dio_reg)

    # Check trigger config
    trigger_state = client.get_trigger_state()
    print(trigger_state)

    # Check overall status
    status = client.get_status()
    print(f"Recording: {status.recording.record_mode}")
    print(f"Streaming: {status.streaming.stream_mode}")
```

## XDAQ Core Hardware I/O Specifications

> [!info] Authoritative source — read this for the Core2
> Pin numbers and Core2-specific voltages are confirmed in [[xdaq-core2-manual-reference|XDAQ Core2 Manual Reference]] (manual figures archived). Core2 specifics that differ from the generic table below: the **DB25** exposes **6 DI (DI-03…08) + 6 DO (DO-03…08)** (onboard total = 7 DI incl. the BNC DI-01), and **DB25 digital outputs are 3.3 V** (the "3.6 V" below is the manual's generic/IO-Expander figure; the BNC DO-01/DO-02 are 3.3/5 V software-configurable). The DB25 pinout table further down matches the manual.

| Feature | XDAQ Core (generic — see Core2 note above) |
|---------|-----------|
| Digital IN | 7 channels, 2.2–5.5V logic |
| Digital OUT | 7 channels, 3.6V logic |
| Analog IN | 1 channel, 16-bit, ±10V |
| Analog OUT | 1 channel, 16-bit, ±10V |
| I/O sample rate | Same as headstage sampling rate |
| DB25 connector | Rear panel, see pinout below |

### DB25 Pinout

| Pin | Signal | Notes |
|-----|--------|-------|
| 2 | DI 03 | ← Our frame sync input from Pi |
| 3 | DI 05 | Available |
| 4 | DI 07 | Available |
| 10 | DO 04 | Available |
| 13 | **DAQ_ON** | **HIGH when acquisition running** → Our recording gate |
| 14 | **SYS GND** | **Shared ground** |
| 15 | DI 04 | Available |
| 16 | DI 06 | Available |
| 17 | DI 08 | Available |
| 22 | DO 03 | Available |
| 25 | **Sample_CLK** | Pulse train at headstage sampling rate (future use) |

## Optional: IO Expander

The XDAQ IO Expander adds 24 more digital I/O and 6 analog I/O channels. Connects via HDMI cable to EXP1/EXP2 ports. Not needed for our basic sync setup but available for future expansion.

## Related

- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]]
- [[01-infrastructure/session-daemon/architecture|Session Daemon Architecture]]

---
tags: [infrastructure, hardware-sync, reference, radiens, api]
created: 2026-04-13
status: complete
---

# Radiens AllegoClient API — Digital I/O Reference

> [!tip] Package Info
> Package: `radiens-core` (PyPI, replaces older `radiens` package)
> Requires: Python 3.12+
> Docs: https://neuronexus.github.io/radiens-core-python/latest/

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
from radiens_core import AllegoClient

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

| Feature | XDAQ Core |
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

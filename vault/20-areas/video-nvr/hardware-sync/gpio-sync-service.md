---
type: reference
area: video-nvr
status: planned
tags: [infrastructure, hardware-sync, gpio, systemd, golden-config]
created: 2026-04-13
---

# GPIO Sync Listener — Service Configuration

> [!check] 2026-06-21 — corrected: gate = `DO 03`, not `DAQ_ON`
> This page originally watched `DAQ_ON` (DB25 pin 13). The vendor thread settled on the **`DO 03` recording gate** (DB25 **pin 22**, Allego "Gated" mode + "BNC Breakout Board" toggle) instead — `DAQ_ON` tracks *streaming* and emits ~0.5 s idle pulses (false edges). The Pi-side input pin is unchanged (**GPIO 17**); only the *source* and *semantics* change (streaming→recording, pin 13→22). See [[wiring-guide]] / [[overview]]. SDK cross-check confirmed 2026-06-21: `AllegoClient.get_digital_out_states()` reports `{'digital_outs_mode':'GATED', ...}` live.

> [!warning] 2026-07-27 — this listener is NOT sufficient for video-EEG synchronization as written
> Two corrections, both source-confirmed. Full analysis → [[2026-07-27-video-eeg-sync-recording-architecture|Video-EEG Sync — The Recording Toggle Is Not Sync-Capable]].
>
> 1. **Auto-start is WANTED. The STOP path is the bug.** Video must start automatically on EEG start; that is the desired UX and the leading edge is free margin, because enabling retains cache segments predating the enable. The damage is entirely on stop: `daemon.py:447` disables recording immediately, and Frigate `frigate/record/maintainer.py:250` then unlinks any unflushed `/tmp/cache` segment, costing **10 to 20 s off the end of every session**. Required behaviour: **drain 30 s, then RELEASE a lease — never publish OFF.** Recording state is `enabled = (manual_lease OR session_lease)`, and on SIGTERM or crash the daemon publishes NOTHING and leaves recording ON (a stuck-ON camera is recoverable; a dropped tail is not). Continuous 24/7 recording was considered and REJECTED on storage grounds.
> 2. **The frame-sync pulse block below fires only twice per session** (rising edge, falling edge). That pins the endpoints and leaves the free-running camera clock's drift in between unmeasured and unrecoverable. **Needs a periodic pulse train, ~1 pulse / 10 s.** See "Wire 2 cadence" below.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The planned Python listener that runs on each Raspberry Pi, watches a GPIO pin for the XDAQ `DO 03` recording-gate TTL level, and publishes MQTT sync events.
>
> **Why it exists.** The gate level comes in on the Pi side; something has to translate "pin went high (recording started)" into "session began at timestamp T" and tell the rest of the system over MQTT.
>
> **How to read this page.** Skim the service unit + config to know what's planned. Cross-link: [[overview]] for context, [[wiring-guide]] for the physical side.

> [!quote] Paper-ready
> A dedicated Python systemd service on each Raspberry Pi monitors the XDAQ `DO 03` recording-gate GPIO line via interrupt-driven edge detection, translating rising/falling edges into MQTT messages timestamped to the edge with sub-millisecond accuracy.

> [!tip] Role
> A lightweight Python service on each Raspberry Pi that monitors the XDAQ `DO 03` recording gate via GPIO and publishes MQTT sync events. Runs independently from go2rtc — does NOT interfere with camera streaming. **Shadow-first:** publishes for jitter logging; the Radiens 1 s poll stays the real trigger until jitter is proven.

## Service File

**File:** `/etc/systemd/system/gpio-sync.service`

```ini
[Unit]
Description=NeuroSurveillance GPIO Sync Listener
Documentation=https://github.com/your-repo/neurosurveillance
After=network-online.target
Wants=network-online.target

[Service]
User={PI_USER}
Group=gpio
ExecStart=/usr/bin/python3 /opt/neurosurveillance/gpio_sync.py

# Same hardening philosophy as go2rtc
Restart=always
RestartSec=5

# CRITICAL: Ensures clean shutdown of GPIO resources
KillMode=control-group
KillSignal=SIGTERM
TimeoutStopSec=10

# Lighter resource limits than go2rtc (this is a lightweight listener)
CPUQuota=10%
MemoryMax=64M
MemorySwapMax=0

# Security
NoNewPrivileges=true

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=gpio-sync

[Install]
WantedBy=multi-user.target
```

## Script

**File:** `/opt/neurosurveillance/gpio_sync.py`

```python
#!/usr/bin/env python3
"""
NeuroSurveillance GPIO Sync Listener
Monitors the XDAQ DO 03 recording gate (DB25 pin 22, "Gated" mode) and
publishes MQTT sync events. Sends frame-sync pulses back to XDAQ DIN on
recording transitions.
"""

import gpiod
import json
import time
import signal
import sys
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# --- Configuration ---
CHIP = "/dev/gpiochip4"       # Pi 5 uses gpiochip4 for main GPIO header
GATE_PIN = {GPIO_GATE}        # GPIO 17 — receives XDAQ DO 03 recording gate (input).
                              # DO 03 in "Gated" mode is a clean level (HIGH while
                              # recording), no idle pulses — unlike the old DAQ_ON.
FRAME_SYNC_PIN = {GPIO_FRAME} # GPIO 27 — sends sync pulses to XDAQ DIN (output)

MQTT_BROKER = "{NVR_IP}"      # NVR IP (Mosquitto broker)
MQTT_PORT = 1883
MQTT_TOPIC_SYNC = "{MQTT_SYNC_TOPIC}"

# Debounce: ignore transitions shorter than this (ms)
DEBOUNCE_MS = 50

# --- Global state ---
running = True


def signal_handler(sig, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def main():
    # Connect to MQTT
    client = mqtt.Client(client_id="pi1_gpio_sync")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    # Open GPIO chip
    chip = gpiod.Chip(CHIP)

    # Configure the DO 03 recording gate as input with pull-down
    gate_line = chip.get_line(GATE_PIN)
    gate_line.request(
        consumer="neurosurveillance_sync",
        type=gpiod.LINE_REQ_EV_BOTH_EDGES,
        flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_DOWN,
    )

    # Configure FRAME_SYNC as output (initially LOW)
    frame_sync_line = chip.get_line(FRAME_SYNC_PIN)
    frame_sync_line.request(
        consumer="neurosurveillance_sync",
        type=gpiod.LINE_REQ_DIR_OUT,
        default_val=0,
    )

    print(f"GPIO sync listener started. Monitoring DO 03 recording gate on GPIO {GATE_PIN}...")

    last_transition_time = 0

    while running:
        # Wait for edge event with 1 s timeout
        if gate_line.event_wait(sec=1):
            event = gate_line.event_read()
            now = time.monotonic()

            # Debounce
            if (now - last_transition_time) < (DEBOUNCE_MS / 1000.0):
                continue
            last_transition_time = now

            timestamp = datetime.now(timezone.utc).isoformat()

            if event.type == gpiod.LineEvent.RISING_EDGE:
                # EEG recording started — publish MQTT event
                payload = json.dumps(
                    {
                        "event": "EEG_START",
                        "source": "hardware_gpio",
                        "timestamp": timestamp,
                        "gpio_pin": GATE_PIN,
                        "pi_hostname": "{PI_HOSTNAME}",
                    }
                )
                client.publish(MQTT_TOPIC_SYNC, payload, qos=1)

                # Send a sync pulse to XDAQ DIN (marks video start in EEG timeline)
                frame_sync_line.set_value(1)
                time.sleep(0.001)  # 1 ms pulse
                frame_sync_line.set_value(0)

                print(f"[{timestamp}] DO 03 RISING -> EEG_START published")

            elif event.type == gpiod.LineEvent.FALLING_EDGE:
                # EEG recording stopped — publish MQTT event
                payload = json.dumps(
                    {
                        "event": "EEG_STOP",
                        "source": "hardware_gpio",
                        "timestamp": timestamp,
                        "gpio_pin": GATE_PIN,
                        "pi_hostname": "{PI_HOSTNAME}",
                    }
                )
                client.publish(MQTT_TOPIC_SYNC, payload, qos=1)

                # Send a sync pulse to XDAQ DIN (marks video stop in EEG timeline)
                frame_sync_line.set_value(1)
                time.sleep(0.001)  # 1 ms pulse
                frame_sync_line.set_value(0)

                print(f"[{timestamp}] DO 03 FALLING -> EEG_STOP published")

    # Cleanup
    frame_sync_line.set_value(0)
    frame_sync_line.release()
    gate_line.release()
    chip.close()
    client.loop_stop()
    client.disconnect()
    print("GPIO sync listener stopped cleanly.")


if __name__ == "__main__":
    main()
```

## Wire 2 cadence — OPEN DECISION, blocks writing the final listener

The script above emits its 1 ms `FRAME_SYNC_PIN` pulse inside the rising-edge and falling-edge branches only, so **two pulses per session**. That is Phase 1 in [[overview]]. It is not enough.

> [!warning] TWO PULSES PER SESSION GIVES OFFSET BUT NOT DRIFT
> Start and stop markers pin the two endpoints of the recording. They say nothing about what the free-running Pi camera clock did in between. Nominal 15 fps is not exactly 15.000, and over a 12 h run a 0.1 % error is ~43 s of accumulated skew. With only two pulses you cannot tell whether that skew accrued linearly, in a step, or not at all, so **you cannot correct it.**

| Option | Drift recoverable? | Pulses per 12 h per Pi | Verdict |
|---|---|---|---|
| Start/stop only (current script, Phase 1) | **No** | 2 | insufficient |
| **Periodic, 1 pulse / 10 s, + double-width every 60 s** | Yes | ~4,300 | **ADOPTED 2026-07-27** |
| Per frame @ 15 Hz (Phase 2) | Yes, per frame | ~648,000 | unnecessary once the fit is linear |
| Manchester / counter codec | Yes | ~4,300 | **rejected** — undebuggable at 3am |

The double-width pulse every 60 s is an unambiguous re-anchor after a dropout, giving just enough identity without a codec.

> [!warning] DECISIVE: fire the pulse from the FRAME-CAPTURE CALLBACK, never from a timer
> A monotonic-timer implementation (what an earlier revision of this page recommended) measures the **Pi's CPU clock**, which nobody cares about. Worse, both ends of the measurement then sit inside the XDAQ clock and nothing ever touches the camera's sensor clock, making the whole scheme circular.
>
> Fire from the capture callback and **log the frame index each pulse fired on**. Each pulse then means "frame N exists". The XDAQ records it at sample S. Analysis pairs **frame N ↔ sample S** and fits a line whose SLOPE is the measured drift. No clock appears anywhere: two counters and a wire.
>
> This depends on frame counting being valid end to end, which holds because Frigate records with `-c:v copy` and never re-encodes. Confirm with `neurosurveillance/backend/scripts/frame_integrity_check.py` before relying on it.

**Fit drift PER CAMERA, not per session.** Four to eight sensors free-run independently; a single fit is wrong at n > 1.

**Write a per-session sync manifest at session close:** pulse table (frame index, sample index), measured effective fps, fitted coefficients, segment boundaries with per-segment frame counts, export window. Without it the mapping is not reproducible, and the per-segment counts double as the integrity record that makes a break detectable offline.

> [!note] The pulse train should run whether or not a session is active
> The camera clock free-runs continuously, so drift accrues continuously, whether or not anyone is recording. Gating the train on the session would reintroduce exactly the blind spot it exists to remove. The train is cheap and the Pi is already at full duty cycle, so there is no reason to gate it.

## Dependencies

```bash
sudo apt install -y python3-gpiod gpiod python3-paho-mqtt
```

If `python3-paho-mqtt` is not available via apt:

```bash
pip3 install paho-mqtt --break-system-packages
```

## Deployment

```bash
# Copy script to Pi
scp gpio_sync.py {PI_USER}@{PI_IP}:/opt/neurosurveillance/gpio_sync.py

# Copy service file
sudo cp gpio-sync.service /etc/systemd/system/gpio-sync.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable gpio-sync.service
sudo systemctl start gpio-sync.service
```

## Validation

```bash
# Check service status
sudo systemctl status gpio-sync.service
# Expected: active (running) in green

# Check logs
journalctl -u gpio-sync.service -f

# On the NVR, subscribe to sync topic
mosquitto_sub -h {NVR_IP} -t "{MQTT_SYNC_TOPIC}"
# Then start an EEG recording in Radiens — should see EEG_START message within ~1 ms
```

## Monitoring

Add to Uptime Kuma:
- **Monitor name:** GPIO Sync Listener (Pi 1)
- **Type:** Docker/systemd (or simple ping to MQTT)

Add to Netdata:
- systemd service state alert for `gpio-sync.service`

## Related

- [[overview|Hardware Sync Overview]]
- [[wiring-guide|Wiring Guide]]
- [[golden-systemd-service|Golden systemd Service (go2rtc)]]

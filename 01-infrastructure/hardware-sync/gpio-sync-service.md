---
tags: [infrastructure, hardware-sync, gpio, systemd, golden-config]
created: 2026-04-13
status: planned
---

# GPIO Sync Listener — Service Configuration

> [!check] 2026-06-21 — corrected: gate = `DO 03`, not `DAQ_ON`
> This page originally watched `DAQ_ON` (DB25 pin 13). The vendor thread settled on the **`DO 03` recording gate** (DB25 **pin 22**, Allego "Gated" mode + "BNC Breakout Board" toggle) instead — `DAQ_ON` tracks *streaming* and emits ~0.5 s idle pulses (false edges). The Pi-side input pin is unchanged (**GPIO 17**); only the *source* and *semantics* change (streaming→recording, pin 13→22). See [[wiring-guide]] / [[overview]]. SDK cross-check confirmed 2026-06-21: `AllegoClient.get_digital_out_states()` reports `{'digital_outs_mode':'GATED', ...}` live.

> [!warning] 2026-07-27 — this listener is NOT sufficient for video-EEG synchronization as written
> Two corrections, both source-confirmed. Full analysis → [[07-decisions/2026-07-27-video-eeg-sync-recording-architecture|Video-EEG Sync — The Recording Toggle Is Not Sync-Capable]].
>
> 1. **The MQTT events must NOT drive the Frigate recording toggle — they are ANNOTATION ONLY.** Two reasons, and the second is decisive. (a) Frigate `frigate/record/maintainer.py:250` unlinks unflushed cache segments when recording is disabled, so **every toggled session permanently loses 10 to 20 s off its end**, and enabling starts capture at a random point up to 10 s away, so a sub-millisecond `DO 03` edge is wasted on it. (b) **Requirement, Andrea 2026-07-27: the cameras are an independent instrument.** They are moved and switched on and off at will with no EEG running, they may be driven by non-Frigate software, and EEG-session recordings are **always started manually by a human** even after sync exists. So the gate may never control capture, regardless of precision. Continuous recording was considered and REJECTED on storage grounds; the tail loss is absorbed by an operator SOP of padding ~30 s either side of the session.
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
| **Periodic, 1 pulse / 10 s** | Yes, to within one interval | ~4,300 | **recommended** |
| Per frame @ 15 Hz (Phase 2) | Yes, per frame | ~648,000 | only if single-frame attribution is needed |

Periodic pins the drift curve at negligible cost. Implementation is a monotonic-clock timer in the main loop alongside `gate_line.event_wait()`, emitting the same 1 ms pulse and logging the Pi-side timestamp of each so the two timelines can be regressed against each other offline.

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

- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]]
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]]
- [[01-infrastructure/raspberry-pi/golden-systemd-service|Golden systemd Service (go2rtc)]]

---
tags: [infrastructure, hardware-sync, gpio, systemd, golden-config]
created: 2026-04-13
status: planned
---

# GPIO Sync Listener — Service Configuration

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The planned Python listener that runs on each Raspberry Pi, watches a GPIO pin for the XDAQ `DAQ_ON` TTL signal, and publishes MQTT sync events.
>
> **Why it exists.** The GPIO pulse comes in on the Pi side; something has to translate "pin went high" into "session began at timestamp T" and tell the rest of the system over MQTT.
>
> **How to read this page.** Skim the service unit + config to know what's planned. Cross-link: [[overview]] for context, [[wiring-guide]] for the physical side.

> [!quote] Paper-ready
> A dedicated Python systemd service on each Raspberry Pi monitors the XDAQ DAQ_ON GPIO pin via interrupt-driven `lgpio`, translating rising-edge events into MQTT messages timestamped to the rising edge with sub-millisecond accuracy.

> [!tip] Role
> A lightweight Python service on each Raspberry Pi that monitors the XDAQ `DAQ_ON` signal via GPIO and publishes MQTT sync events. Runs independently from go2rtc — does NOT interfere with camera streaming.

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
Monitors XDAQ DAQ_ON signal and publishes MQTT sync events.
Sends frame-sync pulses back to XDAQ DIN on recording transitions.
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
DAQ_ON_PIN = {GPIO_DAQ_ON}    # GPIO pin receiving XDAQ DAQ_ON signal (input)
FRAME_SYNC_PIN = {GPIO_FRAME} # GPIO pin sending sync pulses to XDAQ DIN (output)

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

    # Configure DAQ_ON as input with pull-down
    daq_on_line = chip.get_line(DAQ_ON_PIN)
    daq_on_line.request(
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

    print(f"GPIO sync listener started. Monitoring DAQ_ON on GPIO {DAQ_ON_PIN}...")

    last_transition_time = 0

    while running:
        # Wait for edge event with 1 s timeout
        if daq_on_line.event_wait(sec=1):
            event = daq_on_line.event_read()
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
                        "gpio_pin": DAQ_ON_PIN,
                        "pi_hostname": "{PI_HOSTNAME}",
                    }
                )
                client.publish(MQTT_TOPIC_SYNC, payload, qos=1)

                # Send a sync pulse to XDAQ DIN (marks video start in EEG timeline)
                frame_sync_line.set_value(1)
                time.sleep(0.001)  # 1 ms pulse
                frame_sync_line.set_value(0)

                print(f"[{timestamp}] DAQ_ON RISING -> EEG_START published")

            elif event.type == gpiod.LineEvent.FALLING_EDGE:
                # EEG recording stopped — publish MQTT event
                payload = json.dumps(
                    {
                        "event": "EEG_STOP",
                        "source": "hardware_gpio",
                        "timestamp": timestamp,
                        "gpio_pin": DAQ_ON_PIN,
                        "pi_hostname": "{PI_HOSTNAME}",
                    }
                )
                client.publish(MQTT_TOPIC_SYNC, payload, qos=1)

                # Send a sync pulse to XDAQ DIN (marks video stop in EEG timeline)
                frame_sync_line.set_value(1)
                time.sleep(0.001)  # 1 ms pulse
                frame_sync_line.set_value(0)

                print(f"[{timestamp}] DAQ_ON FALLING -> EEG_STOP published")

    # Cleanup
    frame_sync_line.set_value(0)
    frame_sync_line.release()
    daq_on_line.release()
    chip.close()
    client.loop_stop()
    client.disconnect()
    print("GPIO sync listener stopped cleanly.")


if __name__ == "__main__":
    main()
```

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

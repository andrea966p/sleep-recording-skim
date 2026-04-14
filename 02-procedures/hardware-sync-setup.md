---
tags: [procedure, hardware-sync, installation]
created: 2026-04-13
status: planned
---

# Hardware Sync Setup Procedure

> [!warning] Prerequisites
> - XDAQ Core powered off
> - Raspberry Pi powered off
> - All materials from [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]] BOM procured
> - Multimeter available

## Phase 0: Physical Wiring

### 1. Prepare the DB25 Breakout Board

Attach the DB25 male screw-terminal breakout board to the XDAQ Core's DB25 connector on the rear panel. Do NOT power on yet.

### 2. Build the Voltage Divider

On a small breadboard or directly with resistors:

- Connect a 1kΩ resistor from the DB25 Pin 13 screw terminal.
- Connect the other end of the 1kΩ resistor to a Dupont jumper wire (this goes to Pi GPIO {GPIO_DAQ_ON}).
- At the junction between the 1kΩ resistor and the jumper wire, connect a 2kΩ resistor to ground.
- Connect the ground leg of the 2kΩ resistor to DB25 Pin 14 (SYS GND).

### 3. Wire the Connections

| From | To | Wire Color (suggestion) |
|------|----|------------------------|
| DB25 Pin 13 → through 1kΩ → junction | Pi GPIO {GPIO_DAQ_ON} (Pin 11) | **Yellow** (signal) |
| Junction → through 2kΩ → GND | DB25 Pin 14 / Pi Pin 14 | (part of divider) |
| Pi GPIO {GPIO_FRAME} (Pin 13) | DB25 Pin 2 (DI 03) | **Blue** (signal) |
| DB25 Pin 14 (SYS GND) | Pi Pin 14 (GND) | **Black** (ground) |

### 4. Pre-Power Multimeter Checks

See [[01-infrastructure/hardware-sync/wiring-guide#Pre-Power Validation|Wiring Guide — Pre-Power Validation]].

### 5. Power On and Validate Voltages

See [[01-infrastructure/hardware-sync/wiring-guide#Post-Power Validation|Wiring Guide — Post-Power Validation]].

## Phase 1: GPIO Listener Software

### 6. Install Dependencies on Pi

```bash
ssh {PI_USER}@{PI_IP}
sudo apt install -y python3-gpiod gpiod
pip3 install paho-mqtt --break-system-packages
```

**Validation:**
```bash
python3 -c "import gpiod; print(gpiod.Chip('/dev/gpiochip4').num_lines())"
# Expected: a number (e.g., 54)

python3 -c "import paho.mqtt.client; print('OK')"
# Expected: OK
```

### 7. Deploy GPIO Sync Script

```bash
sudo mkdir -p /opt/neurosurveillance
sudo cp gpio_sync.py /opt/neurosurveillance/gpio_sync.py
sudo chmod +x /opt/neurosurveillance/gpio_sync.py
```

### 8. Deploy and Start systemd Service

```bash
sudo cp gpio-sync.service /etc/systemd/system/gpio-sync.service
sudo systemctl daemon-reload
sudo systemctl enable gpio-sync.service
sudo systemctl start gpio-sync.service
```

**Validation:**
```bash
sudo systemctl status gpio-sync.service
# Expected: active (running) in green

journalctl -u gpio-sync.service -n 10
# Expected: "GPIO sync listener started. Monitoring DAQ_ON on GPIO ..."
```

### 9. End-to-End MQTT Validation

On the NVR:
```bash
mosquitto_sub -h {NVR_IP} -t "{MQTT_SYNC_TOPIC}" -v
```

In a separate terminal, start an EEG recording in Radiens.

**Expected:** A JSON message appears in the subscriber within ~1 ms:
```json
{"event": "EEG_START", "source": "hardware_gpio", "timestamp": "2026-04-13T...", "gpio_pin": 17, "pi_hostname": "pi1"}
```

Stop the EEG recording.

**Expected:** A second message:
```json
{"event": "EEG_STOP", "source": "hardware_gpio", "timestamp": "2026-04-13T...", "gpio_pin": 17, "pi_hostname": "pi1"}
```

### 10. Verify XDAQ DIN Reception

While the EEG is recording, check the XDAQ front panel:
- **S2 LED should flash** — this indicates activity on DIN1/DIN2, confirming the Pi's sync pulse arrived.

In Radiens, check the digital input channel data — you should see a brief pulse at the recording start timestamp.

## Phase 2: Session Daemon Integration

### 11. Update Session Daemon

Modify `daemon.py` to subscribe to `{MQTT_SYNC_TOPIC}` and handle `EEG_START` / `EEG_STOP` messages as the primary trigger, with `radiens_poller.py` as fallback.

### 12. Update JSON Sidecar Schema

Add to the session sidecar:
```json
{
    "sync_source": "hardware_gpio",
    "sync_latency_ms": "<1",
    "gpio_start_timestamp": "...",
    "gpio_stop_timestamp": "..."
}
```

## Phase 3: Validation Recording

### 13. 24-Hour Validation Run

Run a 24-hour continuous recording with EEG + video to validate:
- Zero missed start/stop events
- DIN pulse timestamps align with video start/stop times
- No GPIO service crashes
- No interference with go2rtc camera streaming

### 14. Jitter Measurement

Write a post-hoc script to:
1. Load XDAQ `.xdat` file via `radiens-core` `VidereClient`
2. Extract DIN channel rising edges → timestamps
3. Compare against MQTT `EEG_START` / `EEG_STOP` timestamps
4. Compute: mean offset, max jitter, drift rate over 24 h

**Target metrics for publication:**
- Mean offset: <1 ms
- Max jitter: <5 ms
- Drift over 24 h: <10 ms

## Related

- [[01-infrastructure/hardware-sync/overview|Hardware Sync Overview]]
- [[01-infrastructure/hardware-sync/wiring-guide|Wiring Guide]]
- [[01-infrastructure/hardware-sync/gpio-sync-service|GPIO Sync Service]]
- [[01-infrastructure/hardware-sync/literature-review|Literature Review]]

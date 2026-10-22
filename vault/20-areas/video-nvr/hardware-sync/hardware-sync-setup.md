---
tags: [procedure, hardware-sync, installation]
created: 2026-04-13
status: planned
---

# Hardware Sync Setup Procedure

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The deployment procedure for the planned hardware-sync upgrade — wiring the XDAQ DB25 to a Raspberry Pi GPIO pin and installing the listener service.
>
> **Why it exists.** When the lab moves to the TTL pulse sync (replacing 1-second software polling), this is the recipe. Not yet deployed.
>
> **How to read this page.** Prerequisites first — power off everything before touching wires. Then follow each phase in order. Cross-link: [[wiring-guide|wiring details]], [[gpio-sync-service|listener service]], [[overview|why and how]].

> [!quote] Paper-ready
> The XDAQ-to-Raspberry-Pi hardware synchronization is deployed via a staged procedure covering physical wiring (with safety power-off requirements), GPIO listener service installation on each Pi, daemon-side MQTT subscription, and end-to-end TTL pulse validation.

> [!warning] Prerequisites
> - XDAQ Core powered off
> - Raspberry Pi powered off
> - All materials from [[wiring-guide|Wiring Guide]] BOM procured
> - Multimeter available

## Phase 0: Physical Wiring

### 1. Prepare the DB25 Breakout Board

Attach the DB25 male screw-terminal breakout board to the XDAQ Core's DB25 connector on the rear panel. Do NOT power on yet.

> [!check] 2026-06-21 — no voltage divider; gate = `DO 03` (pin 22) direct
> `DO 03` (DB25 pin 22) is **3.3 V fixed** (KC + Jeffrey) = Pi GPIO ceiling exactly → **wire direct, no divider**. The old 1kΩ+2kΩ divider on `DAQ_ON` (pin 13) is removed. Use the **220 Ω series + 10 kΩ pull-down star node** from [[wiring-guide#Multi-Pi fan-out and star grounding|wiring-guide]]. Requires Allego "BNC Breakout Board" toggle ON + Digital Out Control = "Gated".

### 2. Build the Star-Node Fan-Out (no divider)

On a small perfboard / breadboard near the Core:

- From the DB25 **Pin 22 (`DO 03`)** screw terminal, run to a common star node.
- Per Pi branch: a **220 Ω** series resistor from the star node → Dupont jumper → Pi GPIO {GPIO_GATE} (Pin 11).
- At each Pi, a **10 kΩ** pull-down from GPIO {GPIO_GATE} → Pi GND (holds LOW when the Core is off).
- No resistor divider anywhere — `DO 03` is already at the 3.3 V Pi-safe level.

### 3. Wire the Connections

| From | To | Wire Color (suggestion) |
|------|----|------------------------|
| DB25 Pin 22 (`DO 03` gate) → 220 Ω star branch | Pi GPIO {GPIO_GATE} (Pin 11) | **Yellow** (signal) |
| Pi GPIO {GPIO_GATE} → 10 kΩ pull-down | Pi GND (Pin 14) | (holds line LOW when Core off) |
| Pi GPIO {GPIO_FRAME} (Pin 13) | DB25 Pin 2 (DI 03) | **Blue** (signal) |
| DB25 Pin 14 (SYS GND) | Pi Pin 14 (GND) — home-run / star | **Black** (ground) |

### 4. Pre-Power Multimeter Checks

See [[wiring-guide#Pre-Power Validation (Multimeter)|Wiring Guide — Pre-Power Validation]].

### 5. Power On and Validate Voltages

See [[wiring-guide#Post-Power Validation (Multimeter)|Wiring Guide — Post-Power Validation]].

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
# Expected: "GPIO sync listener started. Monitoring DO 03 recording gate on GPIO ..."
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

- [[overview|Hardware Sync Overview]]
- [[wiring-guide|Wiring Guide]]
- [[gpio-sync-service|GPIO Sync Service]]
- [[literature-review|Literature Review]]

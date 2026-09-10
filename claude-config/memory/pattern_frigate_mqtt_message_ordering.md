---
name: pattern-frigate-mqtt-message-ordering
description: "Frigate republishes retained topics in last-published order on (re)connect — recordings/state arrives BEFORE frigate/available, breaking naive grace-window logic."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5cbc6d77-6b1d-49ac-9f41-42050a74c3fc
---

When Frigate (re)connects to Mosquitto it republishes its retained MQTT topics. Empirically, `frigate/<cam>/recordings/state` payloads arrive on the daemon subscriber **before** `frigate/available=online`. This means any guard that wants to absorb the state republish (e.g. a restart grace window) cannot be armed by the availability message — by the time the availability handler fires, the state messages have already been processed.

**Why:** Mosquitto stores retained values per topic and replays them in the order they were last published. Frigate publishes `recordings/state` early in its boot (config-driven init) and `frigate/available=online` after MQTT session establishment, so the natural order is state-then-availability. Mosquitto preserves that order on resubscribe.

**How to apply:** For any callback that reacts to `frigate/<...>/state` and needs to be silenced on Frigate restart:

1. **Defer the callback** via `threading.Timer(STATE_DEFER_SECONDS, fire)` instead of firing inline. `STATE_DEFER_SECONDS = 1.5` is empirically safe — the messages arrive within ~100 ms of each other but the timer adds a comfortable margin.
2. **Cancel pending timers** in the `frigate/available=online` handler. Both paho's MQTT loop thread (paho processes messages sequentially) and the daemon's grace handler should call `cancel_pending_state_actions()` — belt-and-suspenders.
3. **Use `_initial_available_seen`** to skip the very first retained `online` payload that arrives on subscribe (it's a baseline read, not a restart).

The same pattern would apply to any MQTT producer that republishes multiple retained topics in a fixed order on reconnect. Document the producer's actual order via `mosquitto_sub` before designing the receiver — don't assume "availability first".

Reference implementation: `frigate_controller.py` `_schedule_state_callback` / `_handle_availability_message` / `cancel_pending_state_actions`. Shipped 2026-05-24 (commit `3830dba`); full design in [[2026-05-24]] vault note.

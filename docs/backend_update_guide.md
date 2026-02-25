# Python Backend Daemon Updates (Multi-Chamber)

The NeuroSurveillance frontend UI now supports multiple independent recording sessions (Chambers) simultaneously. To make this work, the Python backend daemon (located at `/opt/neurosurveillance/session-daemon/daemon.py`) must be updated to track and return state dictionaries keyed by the `chamber_id` instead of a single global variable.

## 1. Update State Variables
In your `daemon.py` or state manager class, replace the global `session` and `pending_metadata` variables with dictionaries.

```python
# OLD
current_session = None
pending_metadata = None
recording_state = "OFF"

# NEW
sessions = {}           # dict[str, SessionState]
pending_metadata = {}   # dict[str, dict]
recording_states = {}   # dict[str, str]
```

## 2. Update the `/api/status` Endpoint
The frontend now expects the `/api/status` endpoint to return these dictionaries. 

```python
# Inside your HTTP/FastAPI status route:
@app.get("/api/status")
def get_status():
    return {
        "radiens": {
            # Previously this was a string: "R_ON"
            # Now it must be a dict: {"0": "R_ON", "1": "R_OFF"}
            "recording_states": get_all_radiens_recording_states(), 
            "connected": is_radiens_connected()
        },
        "mqtt": {"connected": is_mqtt_connected()},
        "healthy": is_system_healthy(),
        
        # These are now dictionaries keyed by chamber ID (e.g. "0", "1")
        "sessions": sessions,
        "pending_metadata": pending_metadata
    }
```

## 3. Update the `/api/metadata` Endpoint
The frontend now sends a `chamber_id` query parameter when setting or clearing metadata.

```python
# Example FastAPI POST shape
@app.post("/api/metadata")
def set_metadata(chamber_id: str, metadata: MetadataModel):
    # Store it specifically for this chamber
    pending_metadata[chamber_id] = metadata.dict()
    return {"status": "success"}

@app.delete("/api/metadata")
def clear_metadata(chamber_id: str):
    if chamber_id in pending_metadata:
        del pending_metadata[chamber_id]
    return {"status": "success"}
```

## 4. Update the Recording Loop
When the daemon checks the Radiens API for a recording trigger, it needs to know *which* chamber triggered the recording, and spawn a session strictly for that `chamber_id`. 

```python
def check_radiens_and_start_session(chamber_id: str):
    state = check_radiens_state(chamber_id)
    
    if state == "R_ON" and chamber_id not in sessions:
        # 1. Grab metadata for THIS chamber
        meta = pending_metadata.get(chamber_id, get_default_metadata())
        
        # 2. Start the Frigate Video Recording 
        start_frigate_recording(chamber_id)
        
        # 3. Create the active session
        sessions[chamber_id] = Session(
            start_time=time.time(),
            mouse_id=meta["mouse_id"],
            # ...
        )
```

**Restart the Daemon:**
Once you have modified the backend script to use dictionaries, restart the service:
`sudo systemctl restart neurosurveillance-session.service`

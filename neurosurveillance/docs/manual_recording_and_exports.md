# NeuroSurveillance: Manual Recording and Export Architecture

This document provides a detailed overview of the system architecture changes and additions made to support robust manual recording sessions and dynamic, metadata-driven video exports.

## 1. Overview
The NeuroSurveillance system has been extended beyond automated Radiens-triggered sessions to strictly manage and track **Manual Camera Recordings**. These manual sessions are initiated directly from the Frigate UI or other external triggers, while still capturing full metadata (User, Mouse ID, Protocol) from the NeuroSurveillance Frontend. 

Crucially, the system now automatically organizes exported video files into deeply nested, human-readable directory structures based on this metadata, bypassing Frigate's rigid default file naming and Docker permission limitations.

## 2. Metadata Injection and State Management
The system relies on a central Python daemon to manage state across the frontend UI, Frigate backend, and Radiens automation.

- **Pending Metadata**: When a user selects a User, Mouse ID, and Protocol in the UI (e.g., in a Chamber Silo), the frontend calls the `/api/session/metadata` endpoint. This stores the state in `pending_metadata[chamber]`.
- **Session Binding**: If a manual recording starts, the daemon immediately locks this pending metadata into an `ActiveSession` (or `ManualSessionRecord`), clearing the pending state so the next session can be queued.
- **Independent Tracking**: The frontend UI now tracks independent global states for both automated Radiens sessions and manual recordings, ensuring components like the `LiveStatus` panel and `SessionSetup` forms reflect the exact source of truth.

## 3. Manual Recording Detection (Frigate Controller)
Because Frigate operates independently, the Daemon subscribes to Frigate's MQTT topics to accurately track recording states.

- **Detection**: The daemon listens to `frigate/<camera_id>/recordings/state`.
- **Trigger**: When Frigate broadcasts `ON` for a camera that is *not* currently running an automated Radiens session, the daemon registers this as a **Manual Recording**.
- **Metadata Association**: The daemon pairs the locked metadata with the `ManualSessionRecord`. A session JSON sidecar (`<timestamp>_<mouse_id>_<type>_session.json`) is immediately written to disk to preserve the record.
- **End of Recording**: When Frigate broadcasts `OFF`, the runtime duration is calculated, and the export sequence initiates.

## 4. The Frigate Export Edge Case
Frigate provides an API to extract video clips from its internal 24/7 continuous storage, but it has significant limitations:
1. **Hardcoded Filenames**: Frigate violently forces exports into its own random naming schema (e.g., `pi_cam_0_20260226_192211...p1xxyz.mp4`). It does not accept custom filename requests.
2. **Docker Root Permissions**: Frigate runs inside an isolated Docker container. Any file it drops into the `exports` volume mount is rigidly owned by the Linux `root` user, preventing standard user accounts (like `skimlab`) from modifying or moving them.

## 5. Dynamic Export Intercept Logic
To solve Frigate's limitations, an asynchronous background intercept process was built into the daemon.

### The Polling Loop
When a session ends, the daemon tells Frigate to begin parsing the recorded timeframe into a standalone MP4. `frigate.wait_for_export()` waits for Frigate to return a `completed` status.
Because Frigate's API often returns `completed` milliseconds *before* the MP4 is fully flushed to the Linux disk, the daemon uses a 10-second polling loop (`if source_path.exists(): break`) to ensure the file is physically present before attempting to move it.

### Dynamic Folder Construction
Based on the bound metadata, the daemon dynamically strings together the target path:
`exports/{User_Name}/{Mouse_ID}/{YYYY-MM-DD}/<custom_filename>.mp4`
*(e.g., `exports/andrea/5xfadt3/2026-02-26/2602261916_5xfadt3_sd.mp4`)*

### Sudo Privilege Escalation (`sudo mv`)
To bypass Frigate's rigid `root` ownership, the daemon executes raw terminal commands with elevated privileges:
1. `sudo mkdir -p [target_dir]`: Creates the deeply nested `user_name/mouse_id/date` path.
2. `sudo chown -R skimlab:skimlab [user_dir]`: Reassigns permissions of the entire new folder structure to the `skimlab` user, allowing normal interaction via the OS UI.
3. `sudo mv [frigate_file] [target_path]`: Pulls the hardcoded Frigate MP4 and drops it perfectly renamed into the nested directory.
4. `sudo chown skimlab:skimlab [target_path]`: Fixes the permissions of the `.mp4` file itself.

*(Note: The `neurosurveillance-session.service` achieves this seamlessly via a targeted `/etc/sudoers.d/neurosurveillance-fs` policy that allows the `skimlab` user to run `mkdir`, `chown`, and `mv` as root without interactive password prompts).*

## 6. Retention Policies
As an added benefit of this architecture:
- **Clips/Recordings**: Frigate's internal 24/7 storage (`record -> retain -> days: 7`) strictly deletes rolling background footage after 7 days to conserve hard drive space.
- **Exports**: Because we extract the manual recordings into the completely isolated `exports` folder structure, these preserved MP4 files are safe from Frigate's cleanup sweeps. They are permanent artifacts owned by `skimlab` and will exist until manually deleted.

## 7. Session History Filtering
The frontend's History panel now fetches the complete history of saved JSON sidecars and strictly categorizes them by their `source` parameter (`radiens` vs `manual`). New toggle buttons allow researchers to fluidly filter their view of historic sessions based on how they were recorded.

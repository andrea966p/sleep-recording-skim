---
name: Storage Management Feature
description: "Storage monitoring, calculator and 200 GB EEG reserve cap, implemented 2026-04-02 (30 s poll, warn 75 %, critical 90 %, 1.7 Mbps per camera). Detail in the vault"
type: project
---

Implemented 2026-04-02: `backend/storage_monitor.py` (30 s poll), `/api/storage*` endpoints, recording cap in `daemon.py` that blocks new recordings when disk < 200 GB EEG reserve, StoragePanel + header badge. Warn 75 %, critical 90 %; real camera bitrate 1.7 Mbps (not 1.5). 1.9 TB NVMe is shared by Frigate video (~64 GB/day at 4 cameras) and EEG data.

Details: [[storage-management-implementation]] · [[storage-troubleshooting]]

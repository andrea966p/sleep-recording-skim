---
name: Storage Management Feature
description: Storage monitoring, calculator, and EEG reserve cap — fully implemented and deployed Apr 2, 2026
type: project
---

Storage management system implemented Apr 2, 2026. Guide at `sleep-recording-skim/vault/20-areas/video-nvr/storage-management-implementation.md` (status: completed).

**What was built:**
- `backend/storage_monitor.py` — background thread, 30s disk poll, 5-min category cache TTL
- 3 API endpoints: `GET /api/storage`, `GET /api/storage/estimate`, `GET /api/storage/camera-bitrates`
- Recording cap enforcement in `daemon.py` — blocks new recordings when disk < 200 GB EEG reserve
- `StoragePanel` footer card with inline calculator + go2rtc bitrate sync button
- Header storage badge (progress bar + percentage, color-coded by threshold)
- `GET /api/health` augmented with `storage_level` and `storage_used_percent`

**Key values:**
- Actual camera bitrate: 1.7 Mbps (not 1.5 target — VBR + container overhead)
- EEG reserve: 200 GB hard cap
- Warn at 75%, critical at 90%

**Bug fixes during implementation (Apr 2):**
- ChamberSilo linked expansion: fixed with `self-start` on grid items in App.tsx
- Camera offline detection: CameraPreview reports status via callback, ChamberSilo shows red "Camera Offline" badge in header

**Why:** 1.9 TB NVMe shared between Frigate video (~64 GB/day @ 4 cams) and XDAQ EEG/EMG data. Without cap, long sessions could fill disk and interrupt EEG.

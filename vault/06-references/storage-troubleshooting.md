---
tags:
  - reference
  - troubleshooting
  - storage
created: '2026-05-21'
updated: '2026-05-25'
status: active
---
Quick reference for disk-space issues on the NVR.

## Storage layout

```
/srv/frigate/storage/         # Frigate-managed (root-owned)
├── recordings/YYYY-MM-DD/HH/{camera}/MM.SS.mp4    # continuous segments, 7-day retention
├── exports/                                        # Frigate auto-exports (root-owned, daemon moves these)
├── clips/                                          # event clips
└── frigate.db                                      # SQLite — recordings index

/opt/neurosurveillance/        # daemon-managed (skimlab-owned)
├── exports/                   # session exports moved here from Frigate
│   ├── manual/manual/YYYY-MM-DD/    # manual sessions (no metadata)
│   └── {researcher}/{mouse_id}/YYYY-MM-DD/   # Radiens-driven
├── sessions/                  # session JSON sidecars
└── config.yaml                # daemon production config
```

## The 200 GB EEG reserve

The daemon's `StorageMonitor` enforces a 200 GB free-space reserve so EEG / Allego data has guaranteed writeable space. When `df -h /srv/frigate/storage` reports `Avail < 200 GB`, new recordings are blocked.

Check current state:
```bash
curl -s http://127.0.0.1:8585/api/storage | jq
```
Fields to watch: `free_bytes`, `eeg_reserve_bytes`, `can_start_recording`, `status_level`.

If `status_level: "blocked"` and you need to record now, choices in order of preference:
1. Move old exports off-machine (NAS, external drive, USB).
2. Delete oldest `2026-MM-DD/` recordings from `/srv/frigate/storage/recordings/` — but only when Frigate is stopped and Diane / Andrea are aware.
3. Raise the reserve cap (last resort — defeats the safety net): edit `eeg_reserve_gb` in `/opt/neurosurveillance/config.yaml`, restart daemon.

## Sizing rules of thumb

- **Continuous Frigate recording:** ~1.7 Mbps measured (was 1.5 Mbps target). 7 days × 4 cameras × 24 h × 1.7 Mbps ≈ **600 GB**.
- **Per-session exports:** raw H.264 multiplexed, basically same bitrate. A 24h export ≈ 18 GB per camera.
- **Session JSONs:** negligible (~500 bytes each).
- Frigate's 7-day retention prunes `recordings/` automatically; exports never auto-prune (researcher decides what to keep).

## Common symptoms

### "Storage full" but disk shows space

The reserve cap is taking effect. The daemon is doing exactly what it's supposed to do. See the Apr 2 storage system rollout (no journal entry was written for that day) for design rationale.

### `df` shows space but Frigate stops recording

Check Frigate's own storage maintainer — it auto-prunes when its mount fills. Look in `docker logs frigate | grep -i 'storage\\|maintainer'`.

### Inode exhaustion (file count, not bytes)

```bash
df -i /srv/frigate/storage
```
Frigate generates ~360 small `MM.SS.mp4` files per camera per hour. 4 cameras × 24 h × 7 days × 360 ≈ 240k files. Should not exhaust ext4 inodes on a modern disk, but check if `IUse%` is near 100%.

### Lots of root-owned files in `/srv/frigate/storage/exports/`

Frigate writes export MP4s as root. The daemon then `_move_export_file()` moves them to `/opt/neurosurveillance/exports/`. If exports pile up here, the daemon's move path is failing — check `journalctl -u neurosurveillance-session | grep -i 'move\\|export'`.

## Off-machine backup (status: WIRED via NAS over Tailscale)

Originally [[../07-decisions/2026-05-01-llm-council-review#Stage 2 — One free afternoon (~3–4 h, the chain-of-custody fix)|council Stage 2.4]] specced a USB backup via systemd timer + rsync. Superseded 2026-05-26 once the Tailscale NAS became reachable — see [[../02-procedures/installation/nas-backup|nas-backup]]. Daily 00:00 snapshot, 3-day rolling retention. **Single NVR is still the SPOF for recordings between snapshots**; daily snapshots cover only config + vault + daemon state, not MP4s.

Workaround: manually rsync to a local external drive after each cohort:
```bash
rsync -av --progress /opt/neurosurveillance/exports/ /mnt/external/nvr-exports/
```

## Storage commands cheat sheet

```bash
# Per-day breakdown of recordings
du -sh /srv/frigate/storage/recordings/2026-05-*

# Per-day breakdown of exports
du -sh /opt/neurosurveillance/exports/*/

# Largest 10 files in exports
find /opt/neurosurveillance/exports -name "*.mp4" -printf '%s %p\n' \
  | sort -rn | head -10 | awk '{printf "%.2f GB  %s\n", $1/1e9, $2}'

# What Frigate's DB thinks is on disk
sqlite3 /srv/frigate/storage/frigate.db \
  "SELECT camera, COUNT(*) AS segments, ROUND(SUM(end_time - start_time)/3600.0, 1) AS hours FROM recordings WHERE start_time > strftime('%s','now','-7 days') GROUP BY camera"
```

## References

- 2026-04-02 — storage management system rollout. No journal entry exists for that date
- [[../02-procedures/installation/storage-management-implementation|storage-management-implementation]] — full implementation guide
- [[../03-troubleshooting/emergency-runbook|emergency-runbook]] (Symptom A) — first 10 min for disk full

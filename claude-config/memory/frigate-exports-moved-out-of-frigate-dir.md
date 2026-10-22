---
name: frigate-exports-moved-out-of-frigate-dir
description: "Session exports are moved by the daemon to /opt/neurosurveillance/exports/ and Frigate's DB row becomes a dead ghost; always check that directory before concluding an export failed."
metadata: 
  node_type: memory
  type: project
  originSessionId: f0dd1ed7-2e3e-4d71-be58-c673d64cf0de
  modified: 2026-08-14T00:14:18.764Z
---

On session stop `daemon.py` exports via the Frigate API, then `sudo mv`s the file from `/srv/frigate/storage/exports/` to `/opt/neurosurveillance/exports/{user}/{experiment}/{YYYY-MM-DD}/{YYMMDDHHMM}_{experiment}_{label}.mp4` (unset names land under `manual/manual/` or `unknown/unknown/`). Frigate's DB row still points at the old path, so the UI lists a dead export and deleting it frees 0 bytes ("ghost rows": 70 rows vs 17 real files on 2026-08-14, purged; fixed at the source in `delete_export()` guarded on `moved_to is not None`). Direct API exports are NOT moved. `/srv/frigate/storage/exports/` was `root:root`, so skimlab got Permission denied on old files.

Details: [[exports-move-out-of-frigate-dir]]

Always check `/opt/neurosurveillance/exports/` before concluding an export failed. `/opt/neurosurveillance/session-daemon/*.py` are hardlinks/symlinks to the repo: editing the repo IS deploying, only a `systemctl restart neurosurveillance-session` is needed. The sandbox classifier blocks `sudo chown -R skimlab:skimlab /srv/frigate/storage/exports`: the user must run it. A stuck pi_cam_1 export (in_progress forever) was an open, silent bug.

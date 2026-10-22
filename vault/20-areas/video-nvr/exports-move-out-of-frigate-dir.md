---
type: reference
area: video-nvr
status: active
created: 2026-10-22
tags: [frigate, exports, session-daemon]
summary: "Session exports are moved out of Frigate's export folder; where they land, why the Frigate UI shows dead rows, and why old exports could not be deleted."
---

# Exports move out of the Frigate directory

Promoted 2026-10-22 from a Claude memory file. The incident record is [[2026-08-14]] (journal); related: [[2026-04-08-frigate-export-stuck-and-missing-on-edges]], [[export-timeout-fix]], [[storage-troubleshooting]].

**Rule: always check `/opt/neurosurveillance/exports/` before concluding an export failed.**

- On a manual or auto session stop, `daemon.py` exports through the Frigate API, then `sudo mv`s the file out of `/srv/frigate/storage/exports/` to `/opt/neurosurveillance/exports/{user}/{experiment}/{YYYY-MM-DD}/{YYMMDDHHMM}_{experiment}_{label}.mp4`.
- With user and experiment unset it lands under `manual/manual/` or `unknown/unknown/`. The doubled segment is a path-construction quirk, not a bug to chase.
- Frigate's DB row still points at the original path, so the Frigate UI lists the export but it is unplayable, and `ls /srv/frigate/storage/exports/` looks empty of recent work.
- Confirmed 2026-07-15 for the 2026-07-14 15:10 to 16:29 manual session: `2607141510_manual_pi_cam_0.mp4` (906 MB) was in `/opt/neurosurveillance/exports/manual/manual/2026-07-14/` the whole time.
- Still open: the pi_cam_1 export of that session (`pi_cam_1_0gguz7`) hung with `in_progress: true` and was never moved. A stuck export is silent. Its sibling finished in 10 s; cause unknown.
- Direct API exports (curl to `/api/export/...`) are not moved: no session, so the daemon ignores them.

## Why exports could not be deleted (2026-08-14)

1. Ghost rows: deleting an orphan row in the Frigate UI returns HTTP 200 and frees zero bytes. 70 rows existed for only 17 real files; the 53 ghosts were purged through `DELETE /api/export/{id}` with 0 failures. Fixed at the source 2026-08-14: `frigate_controller.delete_export()` plus a call in `daemon.py:_execute_export()`, guarded on `moved_to is not None` (deleting the row after a failed move would strand the file). Tests: `backend/tests/test_export_row_cleanup.py`, 9/9.
2. `/srv/frigate/storage/exports/` is `root:root drwxr-xr-x`, so skimlab gets Permission denied on the 18 pre-fix files (39 G, Feb to Mar). The 2026-04-13 fix redirected only new exports. Frigate's container runs as uid 0, so `sudo chown -R skimlab:skimlab /srv/frigate/storage/exports` is safe; the sandbox classifier blocks it, so the user must run it.

- `/opt/neurosurveillance/session-daemon/*.py` are hardlinks to the repo files (same inode): editing the repo is deploying, and only `systemctl restart neurosurveillance-session` is needed. For the symlink case see [[2026-07-27-video-eeg-sync-recording-architecture]].
- The 2026-04-13 journal entry is wrong about the code: `daemon.py:665,667` still call `sudo mkdir -p` and `sudo chown -R`, and sudoers still has `mkdir`/`chown` NOPASSWD (correction callout added there, per the memory file).

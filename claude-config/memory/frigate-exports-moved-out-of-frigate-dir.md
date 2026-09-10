---
name: frigate-exports-moved-out-of-frigate-dir
description: "Why exports \"disappear\" from the Frigate UI — the daemon moves them to /opt/neurosurveillance/exports/ and leaves an orphan DB row"
metadata: 
  node_type: memory
  type: project
  originSessionId: f0dd1ed7-2e3e-4d71-be58-c673d64cf0de
  modified: 2026-08-14T00:14:18.764Z
---

Session exports do NOT stay in Frigate's export folder. On manual/auto session stop, `daemon.py` exports via the Frigate API, then **`sudo mv`s the file** out of `/srv/frigate/storage/exports/` to:

`/opt/neurosurveillance/exports/{user}/{experiment}/{YYYY-MM-DD}/{YYMMDDHHMM}_{experiment}_{label}.mp4`

When user/experiment are unset it lands under `manual/manual/` or `unknown/unknown/` (doubled segment is a path-construction quirk, not a bug to chase).

**Why this matters:** Frigate's DB row still points at the ORIGINAL `/srv/frigate/storage/exports/...` path, which no longer exists. So the Frigate UI lists the export but it is dead/unplayable, and `ls /srv/frigate/storage/exports/` looks empty of recent work. This reads as "my exports vanished" when the files are fine. **Always check `/opt/neurosurveillance/exports/` before concluding an export failed.**

Confirmed 2026-07-15 investigating "no exports" for the 2026-07-14 15:10→16:29 manual session: `2607141510_manual_pi_cam_0.mp4` (906MB) was present at `/opt/neurosurveillance/exports/manual/manual/2026-07-14/` the whole time.

**Separate real bug, still open:** the pi_cam_1 export from that same session (`pi_cam_1_0gguz7`) hung with `in_progress: true` forever and was never moved — so that camera's file genuinely never landed. A stuck export is silent; nothing alerts. Sibling camera succeeded in 10s. Cause unknown.

Direct API exports (curl to `/api/export/...`) are NOT moved — no session, so the daemon ignores them. They stay in `/srv/frigate/storage/exports/`.

**2026-08-14 — the two reasons "I can't delete exports":**

1. **Ghost rows.** The orphan DB row above means deleting in the Frigate UI returns HTTP 200 and frees **zero bytes**. Found 70 rows / only 17 real files; purged the 53 ghosts via `DELETE /api/export/{id}` (0 failures). **The delete path was never broken** — no non-200 export delete in the whole log window. **FIXED at the source 2026-08-14**: `frigate_controller.delete_export()` + a call in `daemon.py:_execute_export()`, guarded on `moved_to is not None` (deleting the row after a FAILED move would strand the file — the row is its only handle). Tests `backend/tests/test_export_row_cleanup.py` 9/9. **`/opt/neurosurveillance/session-daemon/*.py` are HARDLINKS to the repo files (same inode)** — editing the repo IS deploying; only a `systemctl restart neurosurveillance-session` is needed.
2. **`/srv/frigate/storage/exports/` is `root:root drwxr-xr-x`** ⇒ skimlab gets Permission denied on all 18 pre-fix files (39 G, Feb–Mar). The 2026-04-13 fix only redirected NEW exports; it never chowned this dir and its step-6 migration missed these files. Frigate's container runs as **uid 0**, so `sudo chown -R skimlab:skimlab /srv/frigate/storage/exports` is safe — Frigate keeps writing there. ⚠️ The sandbox classifier BLOCKS that chown; the user must run it.

⚠️ **The 2026-04-13 journal entry is wrong about the code**: `daemon.py:665,667` still call `sudo mkdir -p` and `sudo chown -R`, and sudoers still has `mkdir`/`chown` NOPASSWD. Correction callout added there; full writeup in vault `04-journal/2026-08/2026-08-14.md`.

Related: [[frigate-recording-toggle-fragility]]

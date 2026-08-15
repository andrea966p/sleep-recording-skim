---
name: nas-backup
description: "The nightly NAS backup excludes *.mp4 — no exported video is backed up anywhere, and expired Frigate recordings make exports unrecreatable"
metadata: 
  node_type: memory
  type: project
  originSessionId: 94760afa-443c-4306-b462-cc84db0c61f9
  modified: 2026-08-14T00:25:07.879Z
---

`neurosurveillance/deploy/nas-backup.sh` (systemd `nas-backup.timer`, daily 00:00:15 KST, ssh-pipe to Synology) has **`--exclude='*.mp4'`** at line 46. It backs up `/opt/neurosurveillance/exports` for the **sidecar JSONs only**. Same for `--exclude='storage'`, so Frigate's recording cache is out too.

**Consequence: exported video has ZERO backup. The copy on the NVR is the only copy.**

And it cannot be regenerated: Frigate `record.retain.days: 7`, `/srv/frigate/storage/recordings/` is empty (recording off since 2026-07-03, cameras removed 2026-08-04). Once an export is deleted, that footage is gone for good.

**2026-08-14:** acted on this — cleared all exports and emptied `~/.local/share/Trash` (192 G). That permanently destroyed **Diane's 106 G** (`h5-251awt`/`amut`/`amix` 32 G each from 2026-05-20, `H5S251A_WT`/`MIX` from 2026-05-07) plus the andrea trial clips. User was warned about the no-backup/no-regeneration situation beforehand and chose to proceed. Disk went 91% → 80% (362 G free). Survivors: 56 G of `manual/` + `unknown/` exports.

⚠️ **GUI deletes land in `~/.local/share/Trash` and free NOTHING until emptied** — that trash lives on the same `/` filesystem as everything else. Check it before concluding a cleanup failed: `du -sh ~/.local/share/Trash`.

Related: [[frigate-exports-moved-out-of-frigate-dir]] · [[project_storage_management]]

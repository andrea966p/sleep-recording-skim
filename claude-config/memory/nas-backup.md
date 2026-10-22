---
name: nas-backup
description: "The nightly NAS backup excludes *.mp4, so exported video has no backup; GUI deletes sit in ~/.local/share/Trash and free nothing until emptied"
metadata: 
  node_type: memory
  type: project
  originSessionId: 94760afa-443c-4306-b462-cc84db0c61f9
  modified: 2026-10-22T00:00:00.000Z
---

`nas-backup.sh` (daily 00:00:15 KST) excludes `*.mp4` and `storage`, so exported video has ZERO backup and cannot be regenerated (Frigate retention 7 d, recording off since 2026-07-03). On 2026-08-14 all exports were cleared (192 G incl. Diane's 106 G), after the user was warned.

Details: [[nas-backup]] · journal 2026-08-14 · [[frigate-exports-moved-out-of-frigate-dir]]

- ⚠️ GUI deletes land in `~/.local/share/Trash` on the same `/` filesystem and free NOTHING until emptied: `du -sh ~/.local/share/Trash` before concluding a cleanup failed.

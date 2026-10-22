---
name: skim-nas-smb-and-channel-stripper
description: "The SKIM lab NAS is SMB-only over a direct tailscale path (fourth tailnet), and the XDAT channel stripper that feeds it; detail in the vault; keeps the never-touch ~/radix/data rule"
metadata:
  type: project
---

Set up 2026-09-11. `skim-nas.tailec38b9.ts.net` (Synology `SKIM_NAS`, a FOURTH tailnet), share `SKIM_DATA`, SMB only (SSH closed), mounted at `/mnt/skimnas` by `mnt-skimnas.automount`, direct path ~94 MB/s. The stripper `eeg-emg-analysis/convert/strip_channels.py` turns 262 channels into 16 (93.2 % smaller) into `~/radix/stripped`, a sibling of the raw root.

Details: [[skim-nas-smb-and-upload]] · [[xdat-channel-stripping]] · [[pipeline-architecture]] (Gate E: does Radiens read a stripped file, unproven)

- 🛑 Do NOT write to, move or delete anything in `~/radix/data` (the user moves raw recordings to the NAS themselves); work from `~/radix/stripped`.
- 🔴 A failed CIFS mount leaves `/mnt/skimnas` as a plain directory on the rig's own NVMe (`mountpoint` does not catch it): the sentinel file `03_Data_Mouse/.skim-nas-share` is the guard. CIFS read-back verification is vacuous without `posix_fadvise(DONTNEED)`.
- 🔴 Stripping DELETES the in-file wire-free floor: the QC bundle is a precondition and originals are never auto-deleted. Presets must be labels (`port/site_num`), never indices. `is_live_recording` is not a liveness signal: use data-file mtime. Re-ping before concluding a peer is relayed.

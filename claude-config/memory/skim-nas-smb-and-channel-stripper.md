---
name: skim-nas-smb-and-channel-stripper
description: The SKIM Lab NAS is SMB-only over a DIRECT tailscale path, and the XDAT channel stripper that feeds it; includes three measurements that invalidate obvious designs.
metadata:
  type: project
---

Set up 2026-09-11. Destination for channel-stripped Allego recordings, so the rig stops
accumulating 90 GB/day with one copy.

**The NAS.** `skim-nas.tailec38b9.ts.net` (`100.85.231.100`), Synology `SKIM_NAS`, shared
into our tailnet from `sleepigene@` — a **FOURTH tailnet**, `tailec38b9`; the vault's
"three tailnets" table was incomplete and that incompleteness already caused one multi-day
misdiagnosis. Share `SKIM_DATA`, data under `03_Data_Mouse/<user>/` for
`andrea, diane, ahyeon, hyunmin, staci`. User `skim.data`, creds `/etc/skim-nas.cred`
(0600 root:root, written by a human). Mounted by `mnt-skimnas.automount` at `/mnt/skimnas`,
`vers=3.1.1`, on-access, 600 s idle unmount. **7.0 TB, 1.3 TB free.**

- 🔴 **SSH is CLOSED** on this NAS (22, 53, 222, 2022, 2222, 5022, 8022, 22022 all tried).
  SMB is the only data path. This is NOT the `bilab-syn` NAS, which does have SSH on port 53
  and still handles the nightly project backup — see [[nas-backup-stale-address-outage]].
- ⭐ **The path is DIRECT, 1 ms, write 94 MB/s / read 90 MB/s.** The first `tailscale ping`
  said `via DERP(tok)` only because hole-punching had not finished. **Re-ping before
  concluding a peer is relayed** — I built a whole throughput risk analysis on that false
  reading and had to throw it away.
- 🔴 **A failed CIFS mount leaves `/mnt/skimnas` as an ordinary directory on the rig's own
  NVMe**, the disk the amplifiers write to. `mountpoint` does NOT catch it (an empty local
  dir is a valid mountpoint). Guard = sentinel file `03_Data_Mouse/.skim-nas-share` that
  exists only on the share. Observed to refuse while unmounted.
- 🔴 **Read-back verification over CIFS is VACUOUS unless you drop the page cache first.**
  Measured: plain read-back 1538 MB/s (local cache, verifying our own memory); after
  `os.posix_fadvise(fd,0,0,POSIX_FADV_DONTNEED)`, 89.8 MB/s and a real hash. This is why
  `SYNO.FileStation.MD5` is NOT needed — cache-dropped read-back gives the same sha256 the
  manifest uses, with no second credential.

**The stripper.** `eeg-emg-analysis/convert/strip_channels.py`, numpy+stdlib only, 27-test
suite (`tests/test_strip_channels.py`, 15 of them refusals). 262 ch -> 16 ch = 93.2% smaller.
Output goes to `EEG_STRIPPED_ROOT` (`~/radix/stripped`), a **sibling** of `RAW_ROOT` so
stripped twins fall outside `radix-archive.sh`'s `ls -1 "$SRC"` and every pipeline glob.

- ⭐ **`status.dataset_checksum` == `sha256(data_file || timestamp_file)`.** Verified
  byte-for-byte on two recordings; reversed order does not match.
- 🔴 **`sys_chan_idx` and `absolute_idx` MUST be renumbered to range(k)**; they address a row
  of the data record. `ntv_chan_idx`/`port`/`site_num`/`chan_name` MUST be preserved — those
  are identity, and `open_xdat` builds labels from `port`+`site_num`. Renumbering the wrong
  half silently resolves every CohortSpec lookup to the wrong mouse.
- 🔴 **Stripping DELETES the in-file wire-free floor**, so `compute_features` hard-exits on a
  stripped file ("N expected sites are not in this file's biointerface_map"). Demonstrated,
  not assumed. **The QC bundle is a PRECONDITION of stripping**, and originals are never
  auto-deleted. See [[animal-card-verdict-ladder]].
- 🔴 **`np.memmap` made peak RSS 9.26 GB on a 5.26 GB file** — every touched page is resident.
  Chunked `np.fromfile(offset=)` instead: 186 MB, and 25% faster.
- 🔴 **`is_live_recording` is NOT a liveness signal** — a recording that dies abnormally never
  gets its sidecar rewritten, so it stays `true` forever (`allego_0__uid0829-08-34-39`, ten
  days stale). Use data-file mtime. The flag is useful as a *crash marker* instead.
- 🔴 **Layout is not universal**: `allego_0__uid0904-08-55-25` is **134 channels**, ports of
  32, sites /18../23, and selects all six GPIO. An index list reused across recordings reads
  aux rows and runs off the end. **Presets must be labels (`port/site_num`), never indices.**
- ⚠️ **Gate E (does the Radiens reader accept a stripped file?) is UNPROVEN** — it needs a
  Videre hub and there is no Videre binary under `/opt/allego`, only `videre_man.md`.

**Standing instruction from the user:** do not write to, move or delete anything in
`~/radix/data`. They move raw recordings to the NAS themselves. Work from the copies in
`~/radix/stripped`.

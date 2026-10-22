---
name: usb-hdd-ntfs-dirty-bit
description: "A WD My Passport USB HDD that will not auto-mount on e10ubuntu is the NTFS dirty bit, not a dying drive; fix is ntfsfix -d (never bare ntfsfix). Incident in the vault"
metadata:
  type: project
---

2026-08-29: the WD My Passport 2 TB (`/dev/sda1`, NTFS) refused to mount ("volume is dirty and force flag is not set", `ntfs3`); SMART was clean (0 CRC errors), so it was an unclean removal, not a failing drive. Inspect read-only with `sudo mount -t ntfs3 -o ro,force /dev/sda1 /mnt/wd`, dry run `sudo ntfsfix -n`, fix `sudo ntfsfix -d /dev/sda1`, then mount WITHOUT `force`. `smartctl` needs `-d sat`; eject with `udisksctl unmount` before unplugging.

Details: [[usb-hdd-ntfs-dirty-bit]]

- 🛑 NEVER run bare `ntfsfix` with no flags: it SETS the dirty bit to force a Windows chkdsk.
- Installing `smartmontools` starts and enables `smartd` immediately; unwanted on this recording box: `sudo systemctl disable --now smartmontools.service`.

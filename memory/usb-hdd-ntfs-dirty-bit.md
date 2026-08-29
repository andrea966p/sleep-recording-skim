---
name: usb-hdd-ntfs-dirty-bit
description: WD My Passport 2TB failing to auto-mount on e10ubuntu is the NTFS dirty bit, not a dying drive; fix is ntfsfix -d
metadata:
  type: project
---

The WD My Passport 2 TB USB HDD (`WDC WD20SDRW-11VUUS0`, serial `WD-WX82EC027M1T`,
`/dev/sda1`, NTFS, 1.3 TB used) refused to mount on every plug-in on 2026-08-29.
Kernel log said:

```
ntfs3(sda1): volume is dirty and "force" flag is not set!
```

Cause: NTFS dirty bit from unclean removal. Ubuntu 24.04 auto-mounts NTFS with the
in-kernel `ntfs3` driver, and `ntfs3` HARD-REFUSES a dirty volume. No hibernation file
was present, so this was a yanked cable, not Windows Fast Startup.

**Why:** this reads exactly like a dying drive but is not one. SMART on 2026-08-29 was
clean: Reallocated_Sector_Ct 0, Current_Pending_Sector 0, Offline_Uncorrectable 0,
**UDMA_CRC_Error_Count 0** (so cable and enclosure are innocent too), no errors logged,
996 power-on hours, overall PASSED, and a `smartctl -t short` self-test `Completed without error`
with no LBA reported (so the platters were exercised directly, not merely self-reported). `ntfsfix -n` found `$MFT`, `$MFTMirr` and the
alternate boot sector all intact. Power-Off_Retract_Count 51 against 127 power cycles
is consistent with repeated abrupt unplugging, though that attribute is not proof on
a USB bridge.

**How to apply:**
- Inspect read-only first, this writes nothing: `sudo mount -t ntfs3 -o ro,force /dev/sda1 /mnt/wd`
- Dry run: `sudo ntfsfix -n /dev/sda1`
- Fix: `sudo ntfsfix -d /dev/sda1` (`-d` = clear dirty). Verify by mounting `ntfs3` WITHOUT `force`.
- 🛑 NEVER run bare `ntfsfix` with no flags: that SETS the dirty bit to force a Windows chkdsk.
- `smartctl` needs `-d sat` to reach the drive through the USB-SATA bridge.
- Recurrence prevention is operational, not technical: eject before unplugging
  (`udisksctl unmount -b /dev/sda1`). `found.000` in the volume root is debris from an
  earlier chkdsk, so this had happened at least once before.
- Installing `smartmontools` starts `smartmontools.service` (smartd) immediately AND enables
  it at boot. Unwanted on this box, which runs 72 h live-animal recordings: `sudo systemctl disable --now smartmontools.service`.

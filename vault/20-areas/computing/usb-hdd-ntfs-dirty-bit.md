---
type: incident
area: computing
status: done
created: 2026-08-29
summary: "WD My Passport USB HDD that would not mount on e10 was an NTFS dirty bit, not a dying drive; fix is ntfsfix -d"
tags: [usb, ntfs, storage, troubleshooting]
---

# The USB HDD would not mount: NTFS dirty bit, not a dying drive

> [!abstract] TL;DR
> The WD My Passport 2 TB USB disk (`WDC WD20SDRW-11VUUS0`, `/dev/sda1`, NTFS, 1.3 TB used) refused to mount on
> every plug-in on 2026-08-29. Kernel log: `ntfs3(sda1): volume is dirty and "force" flag is not set!`.
> Fix: `sudo ntfsfix -d /dev/sda1`. 🛑 **Never run bare `ntfsfix` with no flags: it SETS the dirty bit** to force a
> Windows chkdsk. Promoted 2026-10-22 from the workspace memory file `usb-hdd-ntfs-dirty-bit`. The drive was in use
> that day to copy recordings off e10 ([[2026-08-29]]).

## Cause

An NTFS dirty bit left by unclean removal. Ubuntu 24.04 auto-mounts NTFS with the in-kernel `ntfs3` driver, which
hard-refuses a dirty volume. No hibernation file was present, so this was a pulled cable, not Windows Fast Startup.
It reads exactly like a dying drive and is not one.

## Evidence the drive was healthy (2026-08-29)

SMART: Reallocated_Sector_Ct 0, Current_Pending_Sector 0, Offline_Uncorrectable 0, `UDMA_CRC_Error_Count` 0 (so cable
and enclosure are innocent too), no logged errors, 996 power-on hours, overall PASSED, `smartctl -t short` completed
without error. `ntfsfix -n` found `$MFT`, `$MFTMirr` and the alternate boot sector intact. Power-Off_Retract_Count 51
against 127 power cycles is consistent with repeated abrupt unplugging (not proof on a USB bridge). `found.000` in the
volume root is debris from an earlier chkdsk, so this had happened before.

## Procedure

1. Inspect read-only first (writes nothing): `sudo mount -t ntfs3 -o ro,force /dev/sda1 /mnt/wd`
2. Dry run: `sudo ntfsfix -n /dev/sda1`
3. Fix: `sudo ntfsfix -d /dev/sda1` (`-d` clears the dirty bit). Verify by mounting with `ntfs3` WITHOUT `force`.
4. `smartctl` needs `-d sat` to reach the drive through the USB-SATA bridge.
5. Prevention is operational: eject before unplugging (`udisksctl unmount -b /dev/sda1`).

> [!warning] Do not leave smartd running on the rig
> Installing `smartmontools` starts `smartmontools.service` (smartd) immediately and enables it at boot. Unwanted on
> a box that runs 72 h live-animal recordings: `sudo systemctl disable --now smartmontools.service`.

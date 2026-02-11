---
tags: [troubleshooting, incident, raspberry-pi, systemd]
date: 2026-02-11
severity: medium
status: resolved
affected: [raspberry-pi]
---

## Summary
- **Date/Time:** 2026-02-11 ~13:00 GMT
- **Duration:** 2 days (2026-02-09 → 2026-02-11)
- **Severity:** Medium — prevented crash diagnosis
- **Status:** Resolved

## Symptoms
After enabling persistent journal on 2026-02-09 by setting `Storage=persistent` in `/etc/systemd/journald.conf`, logs were still lost on reboot. Every crash left no diagnostic data.

```bash
journalctl -b -1
# "no persistent journal was found"

journalctl --list-boots
# Only shows current boot, no history
```

## Investigation

### Discovery
```bash
systemd-analyze cat-config systemd/journald.conf | grep Storage
# Output showed BOTH:
Storage=persistent
Storage=volatile
  Storage=persistent
```

The config was being loaded multiple times with conflicting values.

### Root Cause
Raspberry Pi OS ships with a drop-in config that overrides the main `journald.conf`:

```bash
/usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf
[Journal]
Storage=volatile
```

This is intentional by Raspberry Pi OS to protect SD cards from wear. The `40-` drop-in loaded **after** `/etc/systemd/journald.conf`, so its `Storage=volatile` won.

Drop-in configs are merged in ASCII sort order:
1. `/etc/systemd/journald.conf` (Storage=persistent)
2. `/usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf` (Storage=volatile) ← **WINS**

Systemd uses the **last value** for each setting, so volatile storage was active despite the main config saying persistent.

## Resolution

Created a drop-in with higher priority (sorted after `40-`):

```bash
sudo mkdir -p /etc/systemd/journald.conf.d/
echo "[Journal]
Storage=persistent
SystemMaxUse=500M" | sudo tee /etc/systemd/journald.conf.d/99-persistent-journal-fix.conf

sudo systemctl restart systemd-journald
```

Now the merge order is:
1. `/etc/systemd/journald.conf` (Storage=persistent)
2. `/usr/lib/systemd/journald.conf.d/40-rpi-volatile-storage.conf` (Storage=volatile)
3. `/etc/systemd/journald.conf.d/99-persistent-journal-fix.conf` (Storage=persistent) ← **WINS**

### Verification
```bash
systemd-analyze cat-config systemd/journald.conf | grep Storage
# Shows persistent last

journalctl --disk-usage
# Archived and active journals take up 8M in the file system.

ls -la /var/log/journal/
# Directory now has subdirectory with journal files
```

## Prevention

**Always use drop-in configs** in `/etc/systemd/<service>.conf.d/` with `99-` prefix to override system defaults, rather than editing the main config file.

**Why `SystemMaxUse=500M`?** Caps journal at 500MB to prevent SD card filling. Default is 10% of filesystem (~6GB on a 64GB card), which is excessive for a 24/7 camera node.

## Related
- [[2026-02-10-post-boot-stream-crash|Post-Boot Stream Crash]]
- [[01-infrastructure/raspberry-pi/watchdog-monitoring|Watchdog Monitoring]]

---
tags:
  - troubleshooting
  - incident
  - go2rtc
  - raspberry-pi
date: 2026-02-10
severity: high
status: workaround
affected:
  - raspberry-pi
---

## Summary
- **Date/Time:** 2026-02-09 ~23:00
- **Duration:** ~30 minutes (until manual power cycle + reboot)
- **Severity:** High — Pi became completely unreachable
- **Status:** Workaround (not fully diagnosed — no persistent journal at time of crash)

## Symptoms
What was observed:
- During post-boot validation (step 11 of [[new-pi-setup|new Pi setup]]), checking camera streams caused the Pi to crash
- SSH connection dropped and could not reconnect (`Connection refused`)
- Pi was pingable (slowly, 1400ms+ RTT) but sshd never came back up
- After manual power cycle, same behavior — SSH refused for extended period

## Investigation

### System state after recovery
```bash
# go2rtc running but no rpicam-vid processes (streams not consumed yet)
ps aux | grep rpicam-vid | grep -v grep | wc -l
# 0

# GPU memory shows 4M — normal for Pi 5 (dynamic allocation, ignores gpu_mem=128)
vcgencmd get_mem gpu
# gpu=4M

# No throttling
vcgencmd get_throttled
# throttled=0x0

# Temperature normal
vcgencmd measure_temp
# temp=47.2'C
```

### No previous boot logs available
```bash
journalctl -b -1 --no-pager
# "no persistent journal was found"
```

Persistent journaling was **not enabled** at the time of the crash. Fixed immediately after recovery:
```bash
sudo mkdir -p /var/log/journal
# Set Storage=persistent in /etc/systemd/journald.conf
sudo systemctl restart systemd-journald
```

### Controlled camera test (post-recovery)
After enabling persistent journal, ran controlled tests:

| Test | Result |
|------|--------|
| Camera 0 alone (10s) | Pass — ~183 KB/s, no throttling |
| Camera 1 alone (10s) | Pass — ~165 KB/s, no throttling |
| Both cameras simultaneously (10s) | Pass — no issues |
| `get_throttled` after all tests | `0x0` |
| Memory after both cameras | 1602 MB / 8062 MB used |
| Temperature after tests | 48.3°C |

Both cameras stream correctly through go2rtc with no crashes.

## Root Cause
**Unknown** — insufficient diagnostic data (no persistent journal, no dmesg capture from crashed boot).

Likely candidates:
1. **Transient power issue during first boot** after applying boot config changes — the `ExecStartPre=/bin/sleep 60` delay (added to prevent power spikes from dual cameras + IR LEDs during boot) may not have been active during the crash
2. **One-time hardware glitch** — first boot after config.txt modifications
3. **Resource contention** — go2rtc + sshd + other boot services competing before the 60s delay was in effect

## Resolution
1. Manual power cycle of the Pi
2. System came back up normally after reboot
3. All streams verified working through controlled testing

## Prevention
- **Persistent journal enabled** — future crashes will have full logs in `/var/log/journal`
- **`ExecStartPre=/bin/sleep 60`** in go2rtc.service delays camera startup to avoid boot-time power spikes
- If crash recurs, check `journalctl -b -1` immediately for previous boot logs

## Related
- [[new-pi-setup|New Pi Setup]] — step 11 (post-boot validation)
- [[2026-02-09-go2rtc-setup-troubleshooting|go2rtc Setup Troubleshooting]]
- [[boot-config-ssh-lockout|Boot Config SSH Lockout]]

---
tags: [troubleshooting, incident, tailscale, rustdesk, remote-access]
created: 2026-02-09
severity: medium
resolved: true
---

## Incident Summary

Lost all remote access (SSH and RustDesk) to `e10ubuntu` (`192.168.0.50`). Screen appeared black and unresponsive. Required physical access to recover.

## Timeline

| Time | Event |
|------|-------|
| 14:47:38 | Connected via Tailscale SSH |
| 14:48:43 | Ran `sudo systemctl restart rustdesk` |
| **14:50:24** | Ran `sudo systemctl restart tailscaled` |
| 14:50:24 | SSH session terminated (Tailscale restarted) |
| 14:51:19 | Physical power button pressed (thought system frozen) |
| 14:52:20 | Orderly shutdown completed |

## Root Cause

**User error**: Restarted `tailscaled` while connected via Tailscale SSH, which immediately terminated the SSH session. Unable to reconnect because:

1. Tailscale was restarting (temporary unavailability)
2. RustDesk was configured to connect via Tailscale P2P
3. Screen was in power-saving mode (appeared "black/frozen")

**The system was NOT frozen** - logs showed continuous activity until power button was pressed.

## Symptoms

- SSH connection drops immediately
- RustDesk shows orange dot (peer visible but unreachable)
- Screen appears black (power saving, not crash)
- Cannot reconnect remotely

## Lessons Learned

1. **Never restart `tailscaled` via Tailscale SSH** - it will disconnect you immediately
2. **Black screen ≠ frozen system** - check power saving settings before assuming crash
3. **RustDesk P2P over Tailscale** requires both ends to have Tailscale running

## Safe Way to Restart Tailscale Remotely

If you must restart Tailscale remotely:

```bash
# Option 1: Use screen/tmux to detach the restart
screen -d -m sudo systemctl restart tailscaled

# Option 2: Use at/nohup with delay
echo "sudo systemctl restart tailscaled" | at now + 1 minute

# Option 3: Connect via local network SSH first (if available)
ssh user@192.168.0.50  # Use LAN IP, not Tailscale IP
```

## RustDesk Configuration Fix

RustDesk was configured with LAN IP instead of Tailscale IP:

**Before (broken for remote P2P):**
```toml
[options]
local-ip-addr = '192.168.0.50'
```

**After (works for Tailscale P2P):**
```toml
[options]
local-ip-addr = '100.85.191.25'
```

**Config file location:** `~/.config/rustdesk/RustDesk2.toml`

**Apply fix:**
```bash
sed -i "s/local-ip-addr = '192.168.0.50'/local-ip-addr = '100.85.191.25'/" ~/.config/rustdesk/RustDesk2.toml
sudo systemctl restart rustdesk
```

## Verification Commands

```bash
# Check Tailscale connectivity
tailscale status
ping 100.117.204.8  # Remote PC Tailscale IP

# Check RustDesk status
systemctl status rustdesk
cat ~/.config/rustdesk/RustDesk2.toml | grep local-ip

# Check if RustDesk is listening
ss -tulnp | grep rustdesk
```

## Prevention

1. Always use LAN IP (`192.168.0.50`) for SSH when modifying network services
2. Keep a terminal session open via LAN as backup
3. Consider setting up a secondary access method (VNC over LAN, etc.)

## Related

- [[system-freeze-ssh-hang|System Freeze SSH Hang]] - different issue (zombie processes)
- RustDesk docs: P2P connection requires both peers advertising correct IPs

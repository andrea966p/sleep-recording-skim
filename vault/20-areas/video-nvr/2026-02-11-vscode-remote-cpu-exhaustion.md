---
tags: [troubleshooting, incident, raspberry-pi, vscode, cpu]
date: 2026-02-11
severity: high
status: resolved
affected: [raspberry-pi]
---

## Summary
- **Date/Time:** 2026-02-11 ~16:40 GMT
- **Duration:** 3 days (2026-02-09 → 2026-02-11) — multiple crashes
- **Severity:** High — caused complete system unresponsiveness
- **Status:** Resolved

## Symptoms

Two crashes on consecutive days (2026-02-10, 2026-02-11) with identical pattern:
- Pi responds to ping but with high latency (~200ms)
- sshd refuses new connections ("Connection refused")
- Existing SSH connections remain alive
- System recovers after power cycle
- No hardware throttling (`vcgencmd get_throttled` shows `0x0`)
- Cameras stream correctly after recovery

Final trigger: With v5.1 deployed and both camera streams active in browser, all CPU cores maxed at 100%. System became unresponsive again.

## Investigation

### Initial Hypothesis
Suspected rpicam-vid software encoding was consuming excessive CPU (Pi 5 has no hardware H.264 encoder).

### Diagnostic Commands

```bash
# Check CPU usage
top -b -n 1 -o %CPU | head -n 20

# Output revealed:
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 2527 skimlab   20   0  169820  94564  36428 R 190.9   2.3   8:28.97 rg
 2528 skimlab   20   0  169820  94388  36352 R 181.8   2.3   8:15.09 rg
 2407 rpicam+   20   0  222068  87932  20620 S  12.8   2.2   0:29.67 rpicam-vid
 2412 rpicam+   20   0  220568  85808  20004 S  12.7   2.1   0:30.02 rpicam-vid

# Check process tree
ps aux | grep -E 'rg|vscode'
# skimlab   2527  190.9  2.3  169820  94564 ?  R    16:31   8:28 /home/skimlab/.vscode-server/.../rg --files --hidden --no-require-git
# skimlab   2528  181.8  2.3  169820  94388 ?  R    16:31   8:15 /home/skimlab/.vscode-server/.../rg --files --hidden --no-require-git
```

### Key Finding

**VSCode Remote was running background file indexing via ripgrep (`rg --files --hidden --no-require-git`).**

CPU breakdown:
- Two `rg` processes: **372% CPU combined** (190.9% + 181.8%)
- Two `rpicam-vid` processes: **25% CPU combined** (12.8% + 12.7%)

The Pi 5 has 4 cores. VSCode Remote's indexing consumed nearly all available CPU (~93%), leaving almost nothing for system services like sshd.

## Root Cause

**VSCode Remote's automatic workspace indexing** triggered recursive file scanning with ripgrep. On the Pi with:
- Dual camera streaming (software H.264 encoding)
- Limited 4-core CPU (ARM Cortex-A76)
- Possibly large filesystem to index

...the indexing starved all other processes, including sshd's ability to accept new connections.

**Why existing SSH connections stayed alive:** The SSH protocol maintains connections via keepalive packets on already-established sockets. But sshd's main listening socket couldn't accept new connections because the process had no CPU time to handle `accept()` calls.

**Why ping still worked:** ICMP echo reply is handled at the kernel level (doesn't require CPU scheduler time for a userspace process).

## Resolution

User closed VSCode Remote session. The `rg` processes terminated automatically (parent process exit). System immediately recovered:

```bash
top - 04:44:46 up 28 min, 3 users, load average: 4.11, 7.21, 5.15
%Cpu(s):  7.0 us,  0.0 sy,  0.0 ni, 93.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 2407 rpicam+   20   0  222524  88292  20692 S  18.2   2.2   1:04.81 rpicam-vid
 2412 rpicam+   20   0  220764  86052  20056 S  18.2   2.1   1:05.48 rpicam-vid
```

- CPU usage: 7% user, 93% idle
- Camera processes: 18.2% each (~36% combined) — **expected and healthy**
- Temperature: 58.2°C (well under 70°C threshold)
- No throttling

## Prevention

**Do NOT use VSCode Remote on resource-constrained camera nodes.** For editing on the Pi, use:
1. Lightweight terminal editors: `nano`, `vim`
2. Remote editing via MCP filesystem server (from another machine)
3. Edit configs locally, deploy via scp/rsync

**If VSCode Remote is absolutely required:**
- Exclude large directories via `.vscode/settings.json`:
  ```json
  {
    "files.watcherExclude": {
      "/var/**": true,
      "/opt/**": true,
      "/usr/**": true
    },
    "search.exclude": {
      "/var/**": true,
      "/opt/**": true,
      "/usr/**": true
    }
  }
  ```
- Disable extensions that do background indexing
- Limit to single-file edits without opening workspace folders

## Related
- [[2026-02-10-post-boot-stream-crash|Post-Boot Stream Crash]] — first occurrence
- [[2026-02-11-persistent-journal-fix|Persistent Journal Fix]] — attempted to capture logs
- [[golden-go2rtc-config|Golden go2rtc Config]] — v5.1 camera config (not the cause)
- [[watchdog-monitoring|Watchdog Monitoring]] — system monitoring setup

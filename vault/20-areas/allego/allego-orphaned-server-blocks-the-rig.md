---
type: incident
area: allego
status: active
status-note: "standing diagnostic: check the allegoserver parent before any other theory"
created: 2026-09-16
tags: [allego, allegoserver, incident, diagnostics]
---

# An orphaned allegoserver makes a healthy rig look dead

> [!abstract] TL;DR
> **What broke.** Closing or crashing the Allego GUI can leave `allegoserver` alive, reparented to `systemd --user`. It keeps listening on ports 50051-50054, so every GUI launched afterwards connects to that server instead of starting its own. If the XDAQ re-enumerated in the meantime, the orphan holds no USB handle and no samples ever arrive.
> **Fix.** Check the parent PID first; kill the orphan by PID; relaunch; verify exactly one instance exists.

> [!info] Promoted from a Claude memory file on 2026-10-22
> Written from the memory note `allego-orphaned-server-blocks-the-rig` (saved 2026-09-16, from the 2026-09-16 debugging of the blank Monitor, [[allego-blank-monitor-canvas-texture-limit]]). Read-only check on 2026-10-22: the running `allegoserver hardware` has the Allego GUI as its parent, which is the healthy case.

## Symptoms

- The GUI shows Connected, ports scan, `IsHardwareConnected=true` (stale cached state).
- The STREAMING toggle responds and the timer counts up.
- Zero samples ever arrive.

## The check, before any other theory

```bash
ps -o pid,ppid,cmd -p $(pgrep -f 'allegoserver hardware')
```

PPID `1` or the `systemd --user` pid means orphaned. A healthy server's parent is an `/opt/allego/allego` GUI process. Also useful:

```bash
fuser -v /dev/bus/usb/002/*      # which pid actually holds the XDAQ
ss -ltn | grep 5005              # who owns the gRPC ports
```

🔴 **Kill it by PID and relaunch.** `pkill -f "^/opt/allego/allego"` matches only the Electron processes, not `.../radix/allegoserver/allegoserver`, so it creates the orphan it was meant to clear. 🛑 And a bare `pkill -f /opt/allego/allego` also kills your own shell ([[allego-mesa-gpu-crash-and-log-storm]]).

## Two failure modes this explains

- The pre-reboot `Failed to claim USB interface: Device or resource busy (error 16)` followed by a SIGSEGV in raklib: a fresh server could not claim the XDAQ because an orphan still held it.
- `raklib_c_api err: RAK_CI::instrument not connected` repeating forever in `allego-ui.log` after that crash.

An orphaned server can also spin a core with nothing connected: [[allegoserver-runaway-thread-thermal]].

## 🛑 Restarting Allego repeatedly is not free

During the 2026-09-16 debugging, repeated launch and kill cycles left three GUI windows, several orphaned servers and about 8 stray `pybridge` processes running at once. The operator was then clicking in dead windows while diagnostics read a different instance, which invalidated several tests and wasted a lot of time. **If you restart Allego, verify exactly one instance exists before trusting anything you see.**

⚠️ Switching the instrument mode (`Restart` / `SystemMode`) resets the channel selection to all channels on every port. Re-select the montage afterwards: the 8-mouse map is A/1, A/2, A/33, A/34 on each of ports A-D ([[CANONICAL-allego-channel-selection]]).

Related: [[starting-the-rig-after-a-restart]]

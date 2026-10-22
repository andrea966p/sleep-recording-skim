---
name: allego-orphaned-server-blocks-the-rig
description: "Closing the Allego GUI can leave allegoserver orphaned to systemd --user, still holding ports 50051-50054 and sometimes no USB handle; every new GUI then connects to that hollow backend and silently gets no data. Check PPID before anything else."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6ac52e19-d272-4acf-9208-5e857b939775
  modified: 2026-09-16T11:49:07.827Z
---

# An orphaned allegoserver makes a healthy rig look dead

Closing (or crashing) the Allego GUI can leave
`/opt/allego/resources/radix/allegoserver/allegoserver hardware` alive and **reparented
to `systemd --user`**. It keeps listening on **50051-50054**, so every Allego you launch
afterwards connects to THAT server instead of spawning its own.

If the XDAQ re-enumerated in the meantime, the orphan holds **no USB handle at all** —
and then:

- the GUI shows Connected, ports scan, `IsHardwareConnected=true` (stale cached state)
- the STREAMING toggle responds and the timer counts up
- **zero samples ever arrive**

## The check, before any other theory

```bash
ps -o pid,ppid,cmd -p $(pgrep -f 'allegoserver hardware')
```

**PPID `1` or the `systemd --user` pid = orphaned.** A healthy server's parent is an
`/opt/allego/allego` GUI process. Also worth a look:

```bash
fuser -v /dev/bus/usb/002/*      # which pid actually holds the XDAQ
ss -ltn | grep 5005              # who owns the gRPC ports
```

🔴 **Kill it by PID and relaunch.** `pkill -f "^/opt/allego/allego"` matches only the
Electron processes, NOT `.../radix/allegoserver/allegoserver`, so it *creates* the
orphan it was meant to clear. 🛑 And per [[allego-mesa-gpu-crash-and-log-storm]], a bare
`pkill -f /opt/allego/allego` also kills your own shell.

## Two failure modes this explains

- The pre-reboot `Failed to claim USB interface: Device or resource busy (error 16)`
  followed by a **SIGSEGV in raklib** — a fresh server could not claim the XDAQ because
  an orphan still held it.
- `raklib_c_api err: RAK_CI::instrument not connected` repeating forever in
  `allego-ui.log` after that crash.

## 🛑 Restarting Allego repeatedly is not free

During 2026-09-16 debugging, repeated launch/kill cycles left **three GUI windows and
several orphaned servers plus ~8 stray `pybridge` processes** running at once. The
operator was then clicking in dead windows while diagnostics read a different instance,
which invalidated several tests and wasted a lot of time. **If you restart Allego, verify
exactly one instance exists before trusting anything you see.**

⚠️ Switching the instrument mode (`Restart` / `SystemMode`) **resets the channel
selection** to all channels on every port. Re-select the montage afterwards
(8-mouse map = A/1, A/2, A/33, A/34 on each of ports A-D).


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐⭐ **[ORPHANED allegoserver MAKES A HEALTHY RIG LOOK DEAD](allego-orphaned-server-blocks-the-rig.md).** Reparented to `systemd --user`, holds ports 50051-4, maybe no USB ⇒ stream toggles, zero samples. Check PPID first.

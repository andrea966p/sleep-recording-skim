---
name: allego-orphaned-server-blocks-the-rig
description: "Closing the Allego GUI can leave allegoserver orphaned to systemd --user, holding ports 50051-50054 with no USB handle: new GUIs connect to a hollow backend and get no data. Check PPID first."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6ac52e19-d272-4acf-9208-5e857b939775
  modified: 2026-09-16T11:49:07.827Z
---

Closing or crashing the Allego GUI can leave `/opt/allego/resources/radix/allegoserver/allegoserver hardware` reparented to `systemd --user`, still holding ports 50051-50054. Every new Allego then connects to that orphan, which (if the XDAQ re-enumerated) holds no USB handle: GUI says Connected, stream toggles, timer counts, ZERO samples.

Details: [[allego-orphaned-server-blocks-the-rig]]

Check first: `ps -o pid,ppid,cmd -p $(pgrep -f 'allegoserver hardware')`. PPID 1 or the systemd --user pid = orphaned; a healthy server's parent is an `/opt/allego/allego` GUI.
🔴 Kill it BY PID and relaunch (`pkill -f "^/opt/allego/allego"` misses the server and creates the orphan; a bare `pkill -f /opt/allego/allego` kills your own shell).
🛑 Restarting Allego repeatedly is not free: after any restart verify EXACTLY ONE instance exists (no extra GUI windows, orphaned servers or stray `pybridge`) before trusting anything you see.
⚠️ Switching instrument mode (`Restart` / `SystemMode`) resets channel selection to all channels: re-select the montage (8-mouse map = A/1, A/2, A/33, A/34 per port).

Rules:
🛑 And per [[allego-mesa-gpu-crash-and-log-storm]], a bare
`pkill -f /opt/allego/allego` also kills your own shell.

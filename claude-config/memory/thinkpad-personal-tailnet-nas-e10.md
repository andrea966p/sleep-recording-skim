---
name: thinkpad-personal-tailnet-nas-e10
description: "ThinkPad reaches SKIM NAS + e10 from Andrea's PERSONAL tailnet (profile b888); a share lands in the tailnet where it was accepted; Tailscale SSH on e10 blocked shared users (disabled 2026-10-23)"
metadata:
  node_type: memory
  type: project
  originSessionId: 79b90fa9-7e66-46d4-a0ba-c9f2b023d1cf
  modified: 2026-10-23T09:57:39.523Z
---

Set up 2026-10-23. The ThinkPad has two Tailscale profiles:
- `b888` = personal tailnet `andrea.piazzola4@gmail.com`. Sees `skim-nas` (100.85.231.100, shared from sleepigene@) AND `e10ubuntu` (100.82.250.62, shared from the lab tailnet). Use this one.
- `10df` = lab tailnet `skimlab.kaist@gmail.com`, logged in as andrea.piazzola4@. Sees e10 but NOT the NAS: in the lab tailnet the NAS share belongs to the `skimlab.kaist@` user only.

**A share lands in the tailnet the browser was on when the invite was accepted, for the user who clicked.** Same user, other tailnet = invisible (no peer in netmap, `no matching peer`). Same diagnosis for the collaborator (anode0, user tcn.lab): `tailscale status | grep skim-nas` empty ⇒ wrong tailnet/user, not a CIFS problem.

🔴 Tailscale SSH was ON on e10 despite the CLAUDE.md 🛑, and refused shared-in users ("tailnet policy does not permit you to SSH"). Disabled 2026-10-23 (`tailscale set --ssh=false`, RunSSH false); plain key `ssh e10` works from b888.

Automount installed on the ThinkPad 2026-10-23 (same two units as e10, rw, `What=//skim-nas.tailec38b9.ts.net/SKIM_DATA`; the name resolves in the personal tailnet), WRITE OK verified.

Shares are one way: e10 cannot initiate to the ThinkPad while it is on b888 (e10→ThinkPad needs `tailscale switch 10df`). `tailscale set --operator=$USER` is per profile; re-pass `--operator` on each `login`. Creds `/etc/skim-nas.cred` (user andrea), share `SKIM_DATA`, `vers=3.1.1`. See [[skim-nas-smb-and-channel-stripper]], [[workspace-single-repo-sleep-recording-skim]].

---
name: nas-backup-stale-address-outage
description: "NAS backup died 2026-08-14..19 on a hardcoded wrong IP; use the MagicDNS name. A tailscale ping pong proves nothing. Detail in the vault incident note"
metadata:
  type: project
---

`nas-backup.sh` hardcoded `100.120.86.10`; the NAS answers on `100.120.86.9`. Fixed 2026-08-19 by using the MagicDNS name `bilab-syn.tail8808c0.ts.net`. Never hardcode a `100.x` literal for this NAS (third stale-address failure).

Details: [[2026-08-19-nas-backup-wrong-address]] · [[nas-backup]] · [[multi-machine-work-setup]]

- 🛑 Two confident wrong diagnoses (Tailscale ACL, a Synology firewall rule) cost real work. `tailscale ping` answering does NOT mean traffic works, and a pong proves only that something answers at that address: test the actual TCP port and re-read the address from `tailscale status`, never from a literal in a script or a vault doc.

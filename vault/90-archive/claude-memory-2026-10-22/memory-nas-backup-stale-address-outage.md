---
name: nas-backup-stale-address-outage
description: "NAS backup died 2026-08-14..08-19 because nas-backup.sh hardcoded 100.120.86.10 and the NAS answers on 100.120.86.9 — now uses the MagicDNS name"
metadata:
  type: project
---

**2026-08-19: fixed a 6-day NAS backup outage. Cause was a wrong IP, nothing else.**

`nas-backup.sh` hardcoded `NAS_HOST="100.120.86.10"`. The NAS actually answers on
**`100.120.86.9`** (`bilab-syn.tail8808c0.ts.net`, hostname `Bilab_Syn`, LAN `192.168.0.21`,
ssh port 53, user `Andrea`). Every run 08-14..08-18 died at `connect: Connection timed out`.

🔴 **Fixed by replacing the literal with the MagicDNS name `bilab-syn.tail8808c0.ts.net`.
Never hardcode a `100.x` literal for this NAS — this was the THIRD stale-address failure here.**

🛑 **TWO WRONG DIAGNOSES were reached with high confidence before the real one. Both cost real work:**
1. *"Tailscale ACL `autogroup:member` excludes shared users."* Plausible (it HAD just caused the
   laptop's lockout) but the bilab policy is `{"src":["*"],"dst":["*"],"ip":["*"]}` — refuted.
2. *"Stale Synology firewall rule pinned to e10's old bilab IP 100.85.191.25."* Reached by grepping
   the vault for old IPs and matching a story. **No such rule exists**; rule index 7 already allowed
   the whole `100.64.0.0/10` for ssh above the catch-all deny. Refuted by an agent on the office PC.

⭐⭐ **THE METHOD LESSON: `tailscale ping` answering does NOT mean traffic works** (disco runs below
ACLs and below iptables) — but worse, **a pong proves only that *something* answers at that address.**
The pong that anchored both wrong theories was measured while the netmap still showed `.10`; once it
refreshed to `.9`, `.10` became `no matching peer`. **Test the actual TCP port, and re-read the
address from `tailscale status` rather than trusting a literal in a script or a vault doc.**

⚠️ **Stale vault docs actively caused misdiagnosis 2:** `00-config/production-values.md` still lists
the bilab-era addresses (PC1 office `100.117.204.8`, PC2/NVR `100.85.191.25`) as current, and
`02-procedures/installation/nas-backup.md` still says the target is `Andrea@100.120.86.10:53`.

✅ Verified after the fix: `uploaded e10_backup_2026-08-19.tar.gz (207529856 bytes verified)`,
rotation kept 08-19/08-13/08-12. NAS `/volume1` = 21 TB, 8.2 TB used, **13 TB free** ⇒ the 775 GB of
raw `~/radix/data` recordings would fit easily; they are still backed up NOWHERE.

Related: [[nas-backup]] · [[multi-machine-setup-and-vault-safety]]


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐⭐ **[NAS BACKUP: 6-DAY OUTAGE WAS A WRONG IP](nas-backup-stale-address-outage.md)** — use MagicDNS `bilab-syn.tail8808c0.ts.net`. A `tailscale ping` pong proves nothing. NAS has 13 TB free. [[nas-backup]]

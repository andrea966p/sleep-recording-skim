---
tags: [infrastructure, nas, tailscale, superseded]
created: 2026-08-19
status: superseded
---

> [!danger] SUPERSEDED — THE DIAGNOSIS IN THIS BRIEF WAS WRONG. DO NOT ACT ON IT.
> This brief sent an agent to the office PC to fix a stale Synology firewall rule. **No such rule
> existed.** The firewall already allowed the whole Tailscale range for SSH, above the deny.
> The agent correctly refused to change anything and reported back — that refusal is the only
> reason a working rule did not get edited.
>
> **The real cause was a wrong IP address in `nas-backup.sh`** (`100.120.86.10`; the NAS answers on
> `100.120.86.9`). Fixed 2026-08-19 by switching to the MagicDNS name.
> Read [[2026-08-19-nas-backup-wrong-address]] instead.
>
> **Kept only as a record of how a plausible wrong theory got built and how it was caught.**
> The useful part is §2 (the safety rules) and §6 (report back rather than improvise), which are
> good practice for any hands-on infrastructure task and are what made the failure recoverable.

# Task brief: restore NAS reachability from the NVR

**For:** an AI agent running on the office PC (`andrea-kaist-pc-ubuntu`), which has
direct LAN SSH access to the Synology NAS.
**Written by:** the agent running on the NVR (`e10ubuntu`), 2026-08-19.
**Estimated time:** 15 minutes, most of it read-only.

---

## 1. Situation

A Synology NAS receives a nightly 198 MB backup of a neuroscience project
(documentation vault, analysis code, daemon config, session database) pushed
from an Ubuntu box called `e10ubuntu`. **That backup has failed every night
since 2026-08-13.** Last verified good upload: `e10_backup_2026-08-13.tar.gz`,
207,354,280 bytes.

### Root cause, already diagnosed. Do not re-investigate from scratch.

`e10ubuntu` used to live in the `bilab.kaist@gmail.com` tailnet, where its
Tailscale address was **`100.85.191.25`**. It was deliberately moved to a
different tailnet (`skimlab.kaist@gmail.com`) because the machine belongs to a
collaborator's lab. Its address is now **`100.82.250.62`**.

The NAS is reachable again at the Tailscale layer (a node share from `bilab` to
`skimlab` was accepted on 2026-08-19). But **a firewall rule on the NAS itself
still allows only the old address**, so all real traffic from `e10ubuntu` is
dropped.

Measured from `e10ubuntu` on 2026-08-19, after the share was accepted:

```
tailscale status  | 100.120.86.10  bilab-syn.tail8808c0.ts.net  idle; offers exit node
tailscale ping    | pong from bilab-syn (100.120.86.10) via DERP(tok) in 65ms
TCP 22            | blocked/closed
TCP 53            | blocked/closed      <-- this is the SSH port the backup uses
TCP 80            | blocked/closed
TCP 443           | blocked/closed
TCP 5000          | blocked/closed
TCP 5001          | blocked/closed
```

Every port dead, including 80/443/5000 which a Synology always serves. That is a
blanket drop, not a per-service problem. `tailscale ping` still answers because
it is handled by `tailscaled` below the host firewall, so **it is not evidence
that traffic works** — ignore it as a success signal.

Two candidate causes were considered. The Tailscale ACL was **ruled out**: the
`bilab` policy file was inspected and its rule is `{"src": ["*"], "dst": ["*"],
"ip": ["*"]}`, which does cover shared-in users. The NAS host firewall is the
remaining cause, and the NAS owner has confirmed they configured one.

### Reference values

| Thing | Value |
|---|---|
| NAS Tailscale name / IP | `bilab-syn.tail8808c0.ts.net` / `100.120.86.10` |
| NAS LAN IP | **unknown to me — you have it, you SSH over LAN** |
| NAS SSH port | `53` (non-standard, deliberate) |
| NAS SSH user | `Andrea` |
| Backup directory | `~/e10_setup_backups` on the NAS |
| NVR new address (must be allowed) | `100.82.250.62` |
| NVR old address (stale rule, likely present) | `100.85.191.25` |
| Office PC old bilab address | `100.117.204.8` |
| Tailscale CGNAT range | `100.64.0.0/10` |

---

## 2. Safety rules. Read before doing anything.

1. **Do not remove or modify any rule that permits LAN access.** Your SSH session
   arrives over the LAN. Deleting a LAN allow rule will lock you out of the NAS
   instantly and the only recovery is physical access to the machine.
2. **Do not disable the firewall wholesale** as a shortcut, even temporarily. It
   is a NAS holding research data.
3. **Synology firewall rules evaluate top-down, first match wins.** A new allow
   rule placed *below* a deny-all rule does nothing. Placement is the single most
   common way this task is done wrong.
4. **Do not edit `/usr/syno/etc/firewall.d/` files by hand.** That format is
   undocumented and unsupported, and a malformed file can brick the firewall
   service. Use the DSM web UI to make the change. Use SSH only for the
   read-only diagnosis in step 3 and the verification in step 5.
5. **Stop and report back rather than improvising** if: the firewall turns out to
   be disabled, no stale-IP rule exists, the ports are open when you test them,
   or anything contradicts the situation described above. The diagnosis would
   then be wrong and further changes would be guesswork.
6. Do not touch anything else on the NAS. In particular do not delete any file in
   `e10_setup_backups` — those three tarballs are currently the only off-machine
   copy of this project.

---

## 3. Read-only diagnosis (SSH over LAN)

Confirm the situation before changing anything. Replace `<NAS_LAN_IP>` throughout.

```bash
ssh -p 53 Andrea@<NAS_LAN_IP> 'hostname; uname -a; cat /etc/VERSION'
```

```bash
ssh -p 53 Andrea@<NAS_LAN_IP> 'ls -lh e10_setup_backups'
```
Expected: three files, `e10_backup_2026-08-11/12/13.tar.gz`, ~198-207 MB each.
**Record the exact names and sizes in your report.** If they are missing, say so
loudly — it changes the risk picture completely.

```bash
ssh -p 53 Andrea@<NAS_LAN_IP> 'df -h'
```
**Record total and free space.** This feeds a separate decision about whether the
NAS can hold 775 GB of raw recordings that are currently backed up nowhere.

```bash
ssh -p 53 Andrea@<NAS_LAN_IP> 'sudo iptables -L INPUT -n --line-numbers | head -60'
```
This shows the live rules the DSM firewall compiled. Look for an ACCEPT naming
`100.85.191.25` (the stale NVR address) and for the final policy or a catch-all
DROP/REJECT. **Paste this output verbatim into your report** — it is the evidence
that confirms or refutes the diagnosis.

```bash
ssh -p 53 Andrea@<NAS_LAN_IP> 'sudo synofirewall --get-status 2>&1 || echo "no synofirewall cli"'
```

---

## 4. The change (DSM web UI)

Open `http://<NAS_LAN_IP>:5000` (or `https://<NAS_LAN_IP>:5001`) and log in.

Go to **Control Panel → Security → Firewall**, select the active profile, and
**Edit Rules**.

Locate the rule allowing `100.85.191.25`. Preferred action: **edit that rule in
place**, changing its source. Editing in place preserves its position in the
ordering, which sidesteps mistake #3 above. If you instead create a new rule, you
must drag it **above** the deny-all rule.

Set the rule to:

| Field | Value |
|---|---|
| Ports | Custom → **TCP 53** |
| Source IP | Specific IP → **Subnet** → `100.64.0.0/10` |
| Action | **Allow** |

### Why the `/10` range and not `100.82.250.62/32`

The owner chose the range deliberately. `100.64.0.0/10` is the whole Tailscale
CGNAT space, so the rule survives future tailnet moves — the stale-address
failure this task exists to fix has now happened three times in this setup. It
remains tightly scoped because it opens exactly one port, and any host in that
range has already had to be admitted to a tailnet with a route to the NAS.

**If the owner has told you they prefer the single address**, use
`100.82.250.62/32` instead and note it in your report so it can be documented.

Save. Changes take effect within seconds; no restart, no reboot.

**Immediately re-confirm your own SSH session still works** before you close the
browser.

---

## 5. Verification

From the office PC (this only proves the NAS is alive, not that the fix worked):

```bash
ssh -p 53 Andrea@<NAS_LAN_IP> 'echo NAS_STILL_REACHABLE'
```

The real test must run **from `e10ubuntu`**, which you cannot reach. Report back
instead — the NVR-side agent will run:

```bash
for p in 22 53 443 5000; do timeout 6 bash -c "cat < /dev/null > /dev/tcp/100.120.86.10/$p" \
  && echo "$p OPEN" || echo "$p blocked"; done
ssh -i ~/.ssh/id_ed25519 -p 53 -o BatchMode=yes Andrea@100.120.86.10 'echo KEY_OK; ls -d e10_setup_backups'
sudo systemctl start nas-backup.service
```

Expected after the fix: `53 OPEN` (22/443/5000 should stay blocked — that is the
scoping working as intended), then `KEY_OK`.

---

## 6. Report back

1. The `iptables -L INPUT` output, verbatim.
2. `ls -lh e10_setup_backups` — names and sizes of the three tarballs.
3. `df -h` — NAS total and free space.
4. Exactly what you changed: which rule, old source value, new source value, and
   its position relative to the deny rule.
5. Anything that contradicted this brief.

Do **not** report the task as complete on the basis of `tailscale ping`
succeeding, or on the basis of the DSM UI accepting the rule. Neither proves
packets flow. Completion is `53 OPEN` plus `KEY_OK` measured from `e10ubuntu`,
and only the NVR-side agent can measure that.

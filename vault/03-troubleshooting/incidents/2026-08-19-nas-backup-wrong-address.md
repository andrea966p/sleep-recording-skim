---
tags: [incident, backup, nas, tailscale, troubleshooting]
created: 2026-08-19
status: resolved
---

# The NAS backup was dead for six days because of one wrong digit

> [!abstract] TL;DR
> The nightly backup to the NAS failed every night from 2026-08-14 to 2026-08-19. The cause was
> that `nas-backup.sh` had the NAS's address hardcoded as `100.120.86.10`, and the NAS actually
> answers on `100.120.86.9`. Nothing else was wrong. The firewall was fine, the Tailscale access
> policy was fine, the SSH key was fine.
> **Two confident wrong diagnoses were reached and acted on before the real one.** That is the part
> worth reading.
> Fixed by using the MagicDNS name `bilab-syn.tail8808c0.ts.net` instead of any IP address.

## What actually broke

Every run died the same way:

```
ssh: connect to host 100.120.86.10 port 53: Connection timed out
```

The tarball built fine each night (198 megabytes). Only the upload failed. Last good backup was
`e10_backup_2026-08-13.tar.gz`, so six days of vault edits, analysis code and session records had
no off-machine copy at all.

## The two wrong diagnoses, and why they were convincing

I am writing these down because both were *reasonable* and both were *wrong*, and the pattern is
what will bite next time.

### Wrong diagnosis 1: the Tailscale access policy

The NVR had recently been moved from the `bilab.kaist@gmail.com` tailnet to
`skimlab.kaist@gmail.com`, and the NAS was shared in from `bilab`. Around the same time, the
laptop had genuinely been locked out by a Tailscale access rule using `autogroup:member`, which
does **not** include users who are shared in. That was a real, freshly-confirmed failure of exactly
this shape, so it was very tempting.

It was wrong. The `bilab` policy is `{"src": ["*"], "dst": ["*"], "ip": ["*"]}`, and `*` does cover
shared-in users.

### Wrong diagnosis 2: a stale Synology firewall rule

Searching the vault for old addresses turned up `100.85.191.25` listed as the NVR, eight times.
That is the NVR's **old** address from when it lived in the bilab tailnet. The story assembled
itself: the NAS firewall must still allow the old address, so the new one is dropped.

An AI agent was sent to the office PC with a detailed brief to go fix that rule. It correctly
**refused to change anything** and reported back that no such rule exists — the firewall already
allowed the whole Tailscale range `100.64.0.0/10` for SSH, above the catch-all deny. Good call by
that agent; a less careful one would have "fixed" a rule that was never broken.

## The measurement that misled me

This is the real lesson.

```
tailscale ping 100.120.86.10   ->   pong from bilab-syn (100.120.86.10) via DERP in 65ms
TCP 53, 80, 443, 5000, 5001    ->   all blocked
```

A pong with every TCP port dead looks exactly like a filtering problem, and that is what anchored
both wrong theories.

> [!warning] TWO SEPARATE TRAPS IN ONE MEASUREMENT
> 1. **`tailscale ping` runs below the access policy and below the host firewall.** A pong never
>    proves that ordinary traffic will flow. Always test a real TCP port.
> 2. **Worse: a pong does not even prove you have the right address.** That pong was measured while
>    the peer map still listed the NAS at `.10`. Once it refreshed to `.9`, the same command
>    answered `no matching peer` — and the mistake became visible.

The fix was found by simply re-reading `tailscale status` and noticing the address had changed
under me, rather than trusting the literal in the script.

## The fix

```bash
NAS_HOST="bilab-syn.tail8808c0.ts.net"   # NOT an IP address
```

Verified immediately after:

```
uploaded e10_backup_2026-08-19.tar.gz (207529856 bytes verified)
remaining: e10_backup_2026-08-19 / 2026-08-13 / 2026-08-12
```

The three older tarballs had survived, because rotation only ever runs after a verified upload and
every failed run died before reaching it.

## Rules that come out of this

1. **NEVER hardcode a `100.x` Tailscale address in a script or a vault page.** Use the MagicDNS
   name. This was the **THIRD** stale-address outage in this setup.
2. **A `tailscale ping` pong is not evidence.** Test the actual TCP port you care about.
3. **Re-read the current address before believing any stored one**, including one in this vault.
4. **Stale documentation is an active hazard, not just untidiness.** `production-values.md` listing
   six-month-old addresses as current is what produced wrong diagnosis 2. That page has been
   rewritten.
5. **When you send someone (or some agent) to change infrastructure, tell them to stop and report
   if the evidence contradicts the brief.** That instruction is the only reason a working firewall
   rule did not get edited.

## Still open

- Nothing on this incident. The backup runs nightly and now also includes `eeg-emg-analysis` and
  the Allego config directories, which had never been backed up at all.

Related: [[nas-backup]] · [[production-values]] ·
[[raw-recording-archive-to-nas]] · [[multi-machine-work-setup]]

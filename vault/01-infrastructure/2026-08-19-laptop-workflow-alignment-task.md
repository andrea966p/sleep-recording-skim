---
tags: [infrastructure, handoff, syncthing, claude-portable, laptop]
created: 2026-08-19
status: active
---

# Task brief: finalize and align the laptop workflow

**For:** an AI agent running on the ThinkPad (`thinkpadubuntu`, user `andrea`).
**Written by:** the agent on the NVR (`e10ubuntu`), 2026-08-19 11:30 KST.
**Time:** ~25 minutes. Most of it is verification; one item is genuinely risky and is marked.

---

## 0. Read this first

A previous brief from me sent an agent to change a firewall rule that was never broken. That agent
was right to stop and report instead of acting. **Do the same here.** Everything below that I have
actually measured is marked *verified*; everything I could not see from the NVR is marked
*unverified — check it*. I could not reach your machine at all (`ssh andrea@100.66.98.20` →
`Connection refused`, no sshd), so **every statement about the laptop is unverified by me.**

If what you find contradicts this brief, **stop and report rather than improvise.**

---

## 1. What happened on the NVR overnight (context, all verified)

- The nightly NAS backup had been dead six days. Cause: a hardcoded IP in `nas-backup.sh`
  (`100.120.86.10`; the NAS answers on `100.120.86.9`). Fixed by using the MagicDNS name
  `bilab-syn.tail8808c0.ts.net`. Backup verified working.
- All raw recordings were archived to the NAS: **124 files, 831.2 GB, zero errors**, then re-read
  on the NAS and re-checksummed: **`ok=124 corrupt=0 missing=0`**. The local copy has NOT been
  deleted; that is the user's decision.
- An 8-mouse recording started at exactly 09:00:00 and is still running
  (`allego_0__uid0819-09-00-00`). **Do not touch it.**
- `eeg-emg-analysis` got its first ever git commit. It has **no remote** — it exists on the NVR's
  disk and inside the nightly NAS tarball, nowhere else.

---

## 2. Reference facts

| Thing | Value | Status |
|---|---|---|
| NVR | `e10ubuntu`, `100.82.250.62`, `e10ubuntu.tail706d43.ts.net` | verified |
| Laptop | `thinkpadubuntu`, `100.66.98.20`, member of the `skimlab.kaist@gmail.com` tailnet | verified from the NVR side |
| Laptop → NVR | `ssh e10` (the NVR's sshd is on 0.0.0.0:22) | verified |
| NVR → laptop | **impossible**, laptop refuses port 22 | verified |
| NAS | `bilab-syn.tail8808c0.ts.net` (`100.120.86.9`), ssh port **53**, user `Andrea` | verified |
| Vault files on the NVR | **511 files / 154,096,936 bytes** excluding `.git` and `.stversions` | verified |
| `claude-portable` | in sync with `origin/main`, all work pushed | verified |
| Syncthing peers | `thinkpadubuntu` connected; `Andrea-ubuntu-desktop` (office PC) **paused** | verified |

---

## 3. Safety rules

1. **Do not run anything that touches the rig.** Allego, radiens, `~/radix/data`, Docker and Frigate
   live on the NVR and a recording is live. Nothing in this brief requires them.
2. **Take a tar snapshot before any Syncthing change** (§6). This is the user's standing rule and it
   exists because a vault was destroyed on 2026-04-29.
3. **Never "delete on disk"** in the Syncthing UI.
4. **Do not unpause or re-share the office PC** (`Andrea-ubuntu-desktop`). It is paused deliberately;
   bringing it back has its own ordered procedure in `multi-machine-work-setup.md`.
5. Stop and report if anything contradicts §2.

---

## 4. Bootstrap the shared Claude config (do this first)

`claude-portable` shares memory between machines. It used to sync only at `SessionEnd`, so a laptop
session began by reading whatever memory was on the laptop's disk — possibly days stale. A
`SessionStart` pull hook now exists.

> [!warning] THE HOOK THAT PULLS IS INSIDE THE COMMIT YOU HAVE NOT PULLED YET
> So the first pull is manual, once. After that it maintains itself.

```bash
cd ~/claude-portable && git status --short
```

`settings.json` will almost certainly show as modified — Claude Code rewrites it at runtime with
machine-specific absolute paths. That **blocks `git pull --rebase`**. Its contents regenerate, so
dropping the local edit costs nothing:

```bash
cp ~/claude-portable/settings.json /tmp/settings.laptop.bak
```
```bash
cd ~/claude-portable && git checkout -- settings.json
```
```bash
cd ~/claude-portable && git pull --rebase
```

Verify:

```bash
grep -c 'pull-only' ~/claude-portable/settings.json
```
Expected: `1`.

```bash
ls ~/claude-portable/memory/ | grep -E 'raw-data-archive|stale-address'
```
Expected: both `raw-data-archive-and-recording-automation.md` and
`nas-backup-stale-address-outage.md`. If they are missing, the pull did not work — stop and report.

```bash
~/claude-portable/sync.sh --status
```
Changes nothing; shows what a sync would do.

---

## 5. Verify the vault actually matches

Syncthing syncs the vault files but **not** `.git`. Compare against the NVR's verified counts:

```bash
cd ~/Monitoring_project/Monitoring_project_obsidian_vault && find . -type f -not -path './.git/*' -not -path './.stversions/*' | wc -l
```
Expected: roughly **505-515** (see the note below).

```bash
cd ~/Monitoring_project/Monitoring_project_obsidian_vault && find . -type f -not -path './.git/*' -not -path './.stversions/*' -printf '%s\n' | awk '{s+=$1} END {print s}'
```
Expected: close to **154096936** (within a few kilobytes).

> [!note] A DIFFERENCE OF A FEW FILES IS NORMAL AND IS NOT A FAULT
> That `find` counts some paths Syncthing deliberately does not sync — `.obsidian/workspace*.json`
> (per-machine window layout) and `.trash`. Syncthing's own view on the NVR is **498 files**, versus
> 511 from `find`. So expect roughly 505-515, not exactly 511.
> **What actually matters is Syncthing reporting `needFiles: 0` and state `idle`.** A difference of
> tens or hundreds of files, or a stuck non-zero `needFiles`, is a real problem — report it rather
> than "fixing" it.

Confirm the new pages from last night arrived:

```bash
ls ~/Monitoring_project/Monitoring_project_obsidian_vault/01-infrastructure/raw-recording-archive-to-nas.md ~/Monitoring_project/Monitoring_project_obsidian_vault/02-procedures/scheduled-recording-and-watchdogs.md ~/Monitoring_project/Monitoring_project_obsidian_vault/04-journal/2026-08/2026-08-19.md
```

> [!warning] THERE ARE TWO VAULT DIRECTORIES ON THIS LAPTOP
> Only `~/Monitoring_project/Monitoring_project_obsidian_vault` is synced.
> `~/Projects/Monitoring_project_obsidian_vault` is a git clone that is **NOT** synced; edits made
> there vanish from everyone else's view. It was de-listed from Obsidian on 2026-08-16. **Confirm it
> is still not open in Obsidian, and do not edit it.**

---

## 6. ⚠️ THE RISKY ONE — live `.git` is being replicated between two machines

**This is the highest-value item in this brief and it needs the user's agreement before you act.**

Verified on the NVR:

| Syncthing folder | `.stignore` excludes `/.git`? | Versioning |
|---|---|---|
| `Monitoring_project_obsidian_vault` | **yes** | staggered |
| `neurosurveillance` | **NO** | **NONE** |
| `neurosurveillance-system` | **no `.stignore` at all** | **NONE** |

So `neurosurveillance/.git` and `neurosurveillance-system/.git` replicate live between the NVR and
this laptop, with **no file versioning and therefore no undo**.

That is the exact combination that destroyed the vault on 2026-04-29: a live `.git` replicated while
git ran on more than one machine. It corrupts the index and can propagate phantom deletions. Three
commits were made into `neurosurveillance` on the NVR this morning, which raises the stakes.

**`.stignore` is local to each device and is not itself synced, so the fix must be applied on BOTH
machines.**

Proposed fix, to be confirmed with the user first:

1. Snapshot first, on **both** machines:
   ```bash
   mkdir -p ~/vault-snapshots && tar czf ~/vault-snapshots/neurosurveillance-$(date +%F-%H%M).tar.gz -C ~/Monitoring_project neurosurveillance neurosurveillance-system
   ```
2. Add `/.git` to `~/Monitoring_project/neurosurveillance/.stignore` (it already exists — add the
   line, do not replace the file).
3. Create `~/Monitoring_project/neurosurveillance-system/.stignore` containing `/.git`.
4. Do the same on the NVR via `ssh e10`.
5. Consider enabling staggered versioning on both folders, as the vault has.

> [!note] Adding an ignore does NOT delete anything
> Syncthing stops syncing ignored paths; it does not remove them from other devices. The risk of
> this change is low. The risk of leaving it is a corrupted repository with no undo.

**If the user does not want this done now, say so in your report and leave it. Do not do it
silently.**

---

## 7. Confirm the laptop can drive the NVR

```bash
ssh e10 'hostname; uptime'
```

```bash
ssh e10 'tail -3 /home/skimlab/Monitoring_project/neurosurveillance/deploy/logs/radix-archive-verify.log'
```
Expected to include: `done: ok=124 corrupt=0 missing=0`

```bash
ssh e10 'stat -c %s /home/skimlab/radix/data/allego_0__uid0819-09-00-00_data.xdat | numfmt --to=iec'
```
Expected: a size that grows between runs — the recording is live.

For anything long running use tmux so an SSH drop does not kill it:
```bash
ssh e10 -t 'tmux new -As rig'
```

---

## 8. Report back

1. Did the `claude-portable` bootstrap work — is `pull-only` present and are both memory files there?
2. The two vault counts, against the expected 511 / 154096936.
3. Whether `~/Projects/Monitoring_project_obsidian_vault` is still de-listed from Obsidian.
4. **Your recommendation on §6**, and whether the user agreed. If you applied it, say exactly what
   you changed on which machine.
5. Anything that contradicted §2.

**Do not report success on the basis of commands having run.** Report the actual numbers.

---

## Decisions that are NOT yours to make

- **Deleting the local 831 GB of raw recordings.** The verification is green so it is safe, but the
  user said explicitly they would do it themselves.
- **Pushing `neurosurveillance` or `eeg-emg-analysis` to GitHub.** Both are deliberately local; the
  branch `ops/nas-archive-and-scheduled-recording` is unpushed on purpose.
- **Stopping the recording.** The user stops it by hand.

Related: [[01-infrastructure/multi-machine-work-setup]] ·
[[01-infrastructure/raw-recording-archive-to-nas]] ·
[[03-troubleshooting/incidents/2026-08-19-nas-backup-wrong-address]] ·
[[03-troubleshooting/incidents/2026-04-29-syncthing-deletion-and-recovery]]

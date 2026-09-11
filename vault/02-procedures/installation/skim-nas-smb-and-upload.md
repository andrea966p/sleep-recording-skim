---
tags: [procedure, installation, nas, smb, cifs, tailscale, synology, backup]
created: 2026-09-11
status: active
---

# The SKIM Lab NAS: mounting it, and uploading recordings to it safely

> [!abstract] TL;DR — for non-technical readers
> **What this is.** How the recording computer reaches the SKIM Lab's network storage, and the rules
> the upload software follows so that a file is never reported as saved unless it really is.
>
> **Why it exists.** The rig produces about 90 GB of data every day, and until now all of it lived on
> one disk inside one computer. This is the second copy. It is also the route by which each lab
> member's own recordings reach their own folder, so they can work with their data without touching
> the recording machine.
>
> **How to read this page.** Section 1 is the one-time setup. Sections 2 and 3 are two dangers that
> are not obvious and that the software is specifically built to avoid — worth reading even if you
> never touch the setup. Section 5 is what to do when something is wrong. Background:
> [[01-infrastructure/system-overview]].

> [!warning] THIS IS NOT THE SAME NAS AS THE NIGHTLY BACKUP
> Two different Synology units, two different tailnets, two different jobs, and confusing them will
> waste a day:
>
> | | purpose | host | access |
> |---|---|---|---|
> | `Bilab_Syn` | nightly snapshot of vault + code + config, and the raw `.xdat` archive | `{NAS_HOST}` | **SSH on port 53** |
> | `SKIM_NAS` | **channel-stripped recordings, per lab member** | `{SKIMNAS_HOST}` | **SMB only — SSH is closed** |
>
> See [[02-procedures/installation/nas-backup]] for the other one.

## 1. One-time setup

All values come from [[00-config/production-values]]; nothing below hardcodes an address.

**1.1 Install the client.**

    sudo apt-get install -y cifs-utils smbclient

**1.2 A human writes the credentials.** Nobody should paste this password into a chat window, a
commit, or a script.

    sudo install -m 600 -o root -g root /dev/null /etc/skim-nas.cred
    read -rsp 'skim.data password: ' P && printf 'username=%s\npassword=%s\n' "{SKIMNAS_USER}" "$P" \
      | sudo tee /etc/skim-nas.cred >/dev/null && unset P

> [!danger] DO NOT USE A `<<'EOF'` HEREDOC FOR THIS
> Bash records multi-line heredocs in `~/.bash_history`, so typing the password that way leaves it
> in cleartext on disk. `read -rsp` does not echo it and does not store it. If a password has already
> gone into history, remove that entry.

The file is `0600 root:root` on purpose, which is also why **a graphical file manager cannot open
it** — that is not a fault, it is the point. Edit it with `sudo nano /etc/skim-nas.cred`.

**1.3 Install the mount units.** From `neurosurveillance/deploy/`:

    sudo cp mnt-skimnas.mount mnt-skimnas.automount /etc/systemd/system/
    sudo mkdir -p {SKIMNAS_MOUNT}
    sudo systemctl daemon-reload
    sudo systemctl enable --now mnt-skimnas.automount

> [!info] Why an `.automount` and not a line in `/etc/fstab` or a `mount` in the script
> `sudo mount` **requires a password on this host**; `sudo systemctl` does not. So an unattended
> uploader could never mount the share directly, but it can touch the path and let systemd do it.
> Idle-unmount after 600 s also means nothing is holding a network share open across a 24-hour
> recording.

**1.4 Place the sentinel** (see section 2) at `{SKIMNAS_MOUNT}/{SKIMNAS_ROOT}/.skim-nas-share`.

**1.5 Per-user folders** live at `{SKIMNAS_ROOT}/<name>` — currently `andrea`, `diane`, `ahyeon`,
`hyunmin`, `staci`. A user in `eeg-recorder/config/users.yaml` **must** have a folder here, and the
uploader refuses any name not on the list rather than creating one.

## 2. 🔴 The mount guard, and why `mountpoint` is not enough

> [!danger] A FAILED MOUNT TURNS THE DESTINATION INTO THE RIG'S OWN SYSTEM DISK
> If the CIFS mount fails — NAS off, password changed, network down — `{SKIMNAS_MOUNT}` does not
> disappear. It remains an ordinary empty directory **on `/dev/nvme0n1p2`, the same filesystem the
> amplifiers record to**. An uploader that could not tell the difference would write tens of
> gigabytes into it and could take the rig down mid-recording.
>
> **`mountpoint -q` does not catch this**, because an empty local directory is a perfectly valid
> mountpoint.

The fix is a **sentinel file that exists only on the share**:

    {SKIMNAS_MOUNT}/{SKIMNAS_ROOT}/.skim-nas-share

Every write is gated on being able to read it. Both conditions must hold — mounted **and** sentinel
readable — or the uploader logs a warning, transfers nothing, and exits cleanly.

Verified on 2026-09-11 by stopping the automount and attempting an upload: it refused, and **nothing
was written to the bare local directory**. A guard that has never been seen to fire is not a guard.

## 3. 🔴 Verifying an upload: read it back, but drop the cache first

The uploader copies to `<name>.part`, hashes the copy **on the NAS**, and renames into place only on
a match. The subtlety is in the middle step.

> [!danger] READING A FILE BACK OVER CIFS NORMALLY VERIFIES YOUR OWN MEMORY
> Measured 2026-09-11 on a just-written 200 MB file:
>
> | read | rate | what it actually read |
> |---|---|---|
> | plain read-back | **1538 MB/s** | the local page cache — proves nothing about the NAS |
> | after `posix_fadvise(…, POSIX_FADV_DONTNEED)` | **89.8 MB/s** | the network, i.e. the real file |
>
> A verification that skips the `fadvise` is a gate that cannot fail.

`nas_upload.sha256_uncached()` drops the cache first and **reports the achieved rate**, so a figure
in the hundreds or thousands of MB/s is visible evidence that the check was weak. It warns above
400 MB/s.

This was tested adversarially: a byte was flipped **in the file on the NAS**, and the next run
detected the mismatch and re-uploaded. That is the property that matters, and it only works because
of the cache drop.

> [!info] Why not Synology's server-side MD5
> `SYNO.FileStation.MD5` is available on `{SKIMNAS_DSM}` and would hash the file on the NAS's own
> disks at zero network cost. It was **deliberately not used**: it needs a second credential file for
> the DSM API, and it returns MD5 while the manifest's authority is SHA-256. At 90 MB/s a 6 GB
> stripped run verifies by read-back in about a minute, which is cheap enough that the extra
> dependency earns nothing. It remains the fallback if read-back ever becomes too slow.

## 4. Status vocabulary — a size check is not a verification

`eeg-recorder/deploy/uploads.jsonl` records one line per file:

| status | meaning |
|---|---|
| `VERIFIED` | bytes were read back **from the share with the cache dropped** and the SHA-256 matched |
| `SIZE_ONLY` | the sizes agree and **nothing else was checked**. Never counted as done; reported separately |
| `FAILED` | hash mismatch. The `.part` is left in place for inspection |

> [!quote] Paper-ready
> Each stripped recording is transferred to institutional network storage and verified by reading
> the stored copy back and comparing its SHA-256 digest with that of the local file. The read is
> performed after explicitly invalidating the local page cache, so that the comparison reflects the
> bytes held by the storage system rather than a cached copy; the achieved read rate is recorded
> alongside the digest as evidence that the verification traversed the network. A file is recorded
> as verified only when both digests agree, and is otherwise retained locally for retransfer.

## 5. When something is wrong

| Symptom | Meaning | Fix |
|---|---|---|
| `mount error(13)` | wrong password | rewrite `/etc/skim-nas.cred` (section 1.2) |
| `mount error(2)` / `BAD_NETWORK_NAME` | wrong share name | check `smbclient -L //{SKIMNAS_HOST} -A /etc/skim-nas.cred` |
| uploader says "sentinel missing" | the share is not really mounted, or the sentinel was deleted | `systemctl start mnt-skimnas.mount`, then restore the sentinel |
| runs pile up in `UPLOAD_PENDING` | the NAS is unreachable | **this is the designed behaviour, not a fault.** They drain in order when it returns |
| read-back rate in the hundreds of MB/s | the cache drop did not take | treat that verification as weak and investigate |

**Never** hardcode `100.85.231.100`. Use `{SKIMNAS_HOST}`. Stale literal addresses have caused three
outages on this setup already — see
[[03-troubleshooting/incidents/2026-08-19-nas-backup-wrong-address]].

## 6. Measured performance

Path is **direct, not DERP-relayed**: `CurAddr 143.248.26.53`, **1 ms RTT**, both ends on the KAIST
campus network. An initial `tailscale ping` reported `via DERP(tok)` purely because hole-punching had
not finished — **re-ping before concluding a peer is relayed.**

| operation | rate |
|---|---|
| write to the share | **94 MB/s** |
| read back (cache dropped) | **90 MB/s** |
| one stripped 24 h run (~6 GB) | ~65 s up, ~67 s to verify |

Capacity: 7.0 TB total, **1.3 TB free** (82% used) as of 2026-09-11.

## 7. Related

- [[02-procedures/installation/xdat-channel-stripping]] — what is uploaded, and why it is smaller
- [[02-procedures/eeg-recording-console]] — the tool that drives this
- [[02-procedures/installation/nas-backup]] — the **other** NAS, over SSH

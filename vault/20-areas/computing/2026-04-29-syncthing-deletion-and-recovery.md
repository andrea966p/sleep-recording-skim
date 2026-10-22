---
type: incident
area: computing
status: done
status-note: "resolved"
tags: [troubleshooting, incident, syncthing, git, neurosurveillance, recovery, claude-code]
created: 2026-04-29
severity: critical
affected: [Andrea-KAIST-PC-ubuntu, e10ubuntu, neurosurveillance-private-repo, syncthing]
---

## Summary
- **Date/Time:** 2026-04-29 ~16:30–17:55 KST (~1h25m)
- **Severity:** Critical — entire working tree of the private `neurosurveillance` git repo wiped on `e10ubuntu`, including `.git/` and uncommitted WIP (10 modified + 3 untracked files).
- **Status:** Resolved. Both PCs restored to a working state byte-identical between them; WIP changes recovered for ~95% of the lost content (one file partially decompiled from `.pyc`, awaiting manual cleanup).
- **Trigger:** Operator action while consolidating project folders into `~/Monitoring_project/` and bringing the private repo into Syncthing for the first time.

> [!warning] Working tree of `~/Monitoring_project/neurosurveillance/` on **e10ubuntu** was deleted by an unintended Syncthing deletion-propagation. Surviving fragments: `backend/__pycache__/` and items inside `frontend/` that matched `.stignore` (build artifacts only). Production at `/opt/neurosurveillance/` was **not** affected — daemon kept running off compiled bytecode in memory.

## Context

Goal of the session was to consolidate everything under one parent folder on each PC (`~/Monitoring_project/`) and to bring **all three** project pieces (Obsidian vault, public repo, private repo) into Syncthing instead of just the vault. See plan: `~/.claude/plans/i-want-you-to-transient-gem.md`.

Pre-incident, only the vault was Syncthing-synced between `Andrea-KAIST-PC-ubuntu` and `e10ubuntu`. The private repo `neurosurveillance` (the Tauri/Python monorepo for the daemon, sensitive — not the public `neurosurveillance-system`) lived only on `e10ubuntu` at `~/Monitoring_project/neurosurveillance/` with a dirty working tree:

- 10 modified: `backend/api.py`, `backend/daemon.py`, `backend/session_manager.py`, `config/config.yaml`, and 6 `frontend/src/...` files
- 3 untracked: `backend/storage_monitor.py`, `frontend/src/components/StoragePanel.tsx`, `frontend/src/hooks/useStoragePoll.ts`

## Timeline

| KST | Event |
|---|---|
| ~16:30 | Plan approved. Vault rename + Syncthing path update on `Andrea-KAIST-PC-ubuntu` succeeded. |
| ~16:50 | Public repo (`neurosurveillance-system`) added to Syncthing — clean, no issues. |
| ~16:54 | Private repo `neurosurveillance` shared from `e10ubuntu` → `Andrea-KAIST-PC-ubuntu`. |
| ~16:58 | First sync exposed 5.1 GB total — most of it `frontend/src-tauri/target/` (Rust build) and `frontend/node_modules/`. Both `.gitignore`-listed — should not sync. |
| ~16:59 | **Mistake committed.** To clear partial sync data on `Andrea-KAIST-PC-ubuntu` before adding `.stignore`, ran `find … -mindepth 1 ! -name .stfolder -exec rm -rf` on its (1.6 GB partial) copy of `~/Monitoring_project/neurosurveillance/`. Folder was paused. Then **resumed** sync on this side after the wipe. |
| ~17:00 | Resume caused `Andrea-KAIST-PC-ubuntu` to announce all files as deleted. `.stignore` (just set on `e10ubuntu`) blocked deletion of dirs containing ignored content (so `frontend/src-tauri/target/` survived because of nested ignored files), but **non-ignored source files were deleted on `e10ubuntu`**, including the entire `.git/` and all `backend/*.py` / `frontend/src/...` source. |
| 17:01 | Detected via Syncthing puller errors `delete dir: directory has been deleted on a remote device but contains ignored files`. Both folders paused immediately. |
| 17:02–17:25 | Recovery-vector inventory + extraction (read-only on `e10ubuntu`). |
| 17:25–17:45 | Transcript replay reconstructed 51 files. `pylingual` patched + run on `storage_monitor.cpython-312.pyc` (failed control-flow). `pycdc` built from source and run successfully (188 lines, 3 methods incomplete). |
| 17:45–17:55 | Other-PC restoration: removed corrupt Syncthing folder configs, `rm -rf` broken dir, fresh `git clone` from GitHub, overlaid 11 recovered files, set ordered `.stignore`, re-shared. Both sides Up to Date, byte-identical, 0 errors. |

## Root Cause

The error chain that produced the deletion:

1. **Two clones of the same repo joined into a sendreceive Syncthing folder.** The fresh-but-stale clone on `Andrea-KAIST-PC-ubuntu` (5 commits behind HEAD) and the dirty live clone on `e10ubuntu` were both treated by Syncthing as one folder. Syncthing has no concept of git history — it sees files and merges based on mtime/version vector, not commit graphs.

2. **`.stignore` set on `e10ubuntu` only, after sync had begun.** The `.stignore` rules excluded build artifacts (`frontend/src-tauri/target/`, `frontend/node_modules/`, etc.) but not the actual source files. So the source remained sync-eligible.

3. **`rm -rf` on a *member* of a sendreceive folder, even paused, is a logical deletion.** Pausing prevents transmission; it does **not** prevent indexing. When the folder was unpaused, Syncthing's local scanner saw "all files gone" → emitted `delete` events for every previously-known file. The peer applied them.

4. **`.stignore`'s only protective effect was indirect:** when Syncthing tried to delete a directory that contained ignored files (e.g., `frontend/src-tauri/` with `target/` inside), it refused with the error "directory has been deleted on a remote device but contains ignored files". This kept those dirs from being fully wiped — but every non-ignored *file* under them was still deleted before the dir-delete failed. **`.stignore` is not a backup mechanism.**

The right pre-condition for the wipe-then-resync would have been to **remove the folder from Syncthing's config first** (so Syncthing forgets about the path entirely), then `rm -rf`, then re-add as a fresh sendreceive folder. Wipe-while-still-a-member is what propagated.

## Damage and Recovery Sources

What was lost on `e10ubuntu`:

- `.git/` (entire local repo metadata) — recoverable from GitHub remote (HEAD was pushed at `40b0330`).
- Every committed source file — recoverable from GitHub HEAD.
- The 10 modified + 3 untracked WIP files — **only place they existed on disk**; primary recovery target.

What survived on disk because of `.stignore`:

| Path | Reason | Useful? |
|---|---|---|
| `backend/__pycache__/*.pyc` | matched `backend/__pycache__` ignore | **Yes** — Apr 2 bytecode of `api.py`, `daemon.py`, `session_manager.py`, `storage_monitor.py` etc. |
| `frontend/src-tauri/target/` | matched ignore | No (build artifacts only) |
| `frontend/node_modules/` | matched ignore | No |
| `frontend/dist/` | matched ignore | No |
| `frontend/.vscode/` | matched `.vscode/*` (extensions.json was the negation but order was wrong) | Marginal |

External recovery vectors checked, in order of yield:

1. **Claude Code project transcripts** at `~/.claude/projects/-home-skimlab-Monitoring-project/` and its subagent jsonl files.
   - Every WIP file we needed was Read or Edited via Claude Code at some point.
   - Subagent transcripts (under `<session>/subagents/agent-*.jsonl`) had **full Reads** of the entire backend on 2026-04-01 — these were the most valuable.
   - `frontend/src/components/StoragePanel.tsx` had a `Write` tool call (full content captured at creation, 2026-04-02 09:00).
   - `frontend/src/hooks/useStoragePoll.ts` had a full Read on 2026-04-02 09:42.
   - **Outcome:** 51 files reconstructed, including all 10 modified + 2 of 3 untracked.

2. **Antigravity local history** at `/home/skimlab/.config/Antigravity/User/History/`.
   - Snapshots dated late Feb / early Mar — predate the recent WIP. Useful only as a sanity-check baseline.

3. **`/opt/neurosurveillance/`** production deploy.
   - `session-daemon` is a symlink → `~/Monitoring_project/neurosurveillance/backend`, so it followed the deletion. **Not a recovery source.**
   - `/opt/neurosurveillance/config.yaml` (Apr 13) was an additional independent copy — confirmed config recovery.
   - **The running daemon (PID 2198159, started Apr 13) kept running** — Python had its modules already loaded into memory. Source isn't recoverable from `/proc/<pid>/maps` (Python doesn't keep `.py` mmapped after import) but the process stayed alive.

4. **`pylingual`** (LLM-assisted decompiler, supports Python 3.12) — installed in venv, required a one-line patch to `pylingual/editable_bytecode/PYCFile.py` because newer `xdis` returns 8 values from `load_module` instead of 7. Crashed mid-run on `storage_monitor.cpython-312.pyc` with `NetworkXError: edge MetaTemplate[start]-MetaTemplate[start] not in graph` during control-flow reconstruction. **No usable output.**

5. **`pycdc`** (Decompyle++, C++) — built from source from `https://github.com/zrax/pycdc`. Successfully decompiled `storage_monitor.cpython-312.pyc` to 188 lines. Three methods incomplete due to unsupported Python 3.12 opcodes (`POP_JUMP_IF_NOT_NONE`, `LOAD_FAST_AND_CLEAR`): `get_status`, `can_start_recording`, `fetch_camera_bitrates`. The class skeleton, `__init__`, `start`, `stop`, `_poll_loop`, `refresh`, `_get_dir_size` were all clean.

6. **Python `dis`** disassembly of the same `.pyc` — gave the locals (`status`, `available`, `reserve`, `avail_gb`, `reserve_gb`), constants (format strings, sentinel values), and used names per method. With this, the three TODO methods were reconstructed best-effort with annotations pointing back to the disassembly file at `storage_monitor.disassembly.txt`.

Recovery quality:

| File | Source | Status |
|---|---|---|
| `backend/api.py` | transcript full Read 2026-04-01 + Edits | **Second-order gap found post-restart.** Transcript was from Apr 1; storage endpoints were added Apr 2 and not captured. Edits replayed by the recovery script were all to pre-existing code — no new endpoint additions. Gap detected when daemon crashed on restart with `TypeError: init_api() got an unexpected keyword argument 'storage_monitor'`. Recovered by reconstructing from StorageMonitor interface + captured live response shape (commit `423e8f5`). |
| `backend/daemon.py` | transcript full Reads + Edits | 35-line WIP diff vs HEAD recovered |
| `backend/session_manager.py` | transcript full Reads | identical to GitHub HEAD |
| `backend/storage_monitor.py` | partial transcript Read + pycdc + disassembly | ~75% clean, 3 methods marked `TODO` for manual review; `get_status` and `can_start_recording` confirmed correct by live polling; `fetch_camera_bitrates` parses go2rtc reachability only — bitrate extraction still returns `default_mbps` for all cameras (deferred) |
| `config/config.yaml` | transcript full Read + Edits | recovered |
| `frontend/src/utils/format.ts` | transcript replay | duplicate `formatBytes` (overlapping reads merged) — caught by `tsc --noEmit`, removed before commit |
| All other frontend WIP files | transcript full Reads + Edits + one Write | recovered |

## Resolution

### Restoration sequence executed

```bash
# 1. Drop the corrupted Syncthing folder from BOTH instances (Syncthing's view only — files left alone)
curl -X DELETE -H "X-API-Key: …" http://127.0.0.1:8384/rest/config/folders/neurosurveillance-private  # this PC
ssh skimlab@100.85.191.25 'curl -X DELETE … http://127.0.0.1:8080/rest/config/folders/neurosurveillance-private'

# 2. Wipe broken dir on e10ubuntu (and the empty placeholder on this PC)
ssh skimlab@100.85.191.25 'rm -rf /home/skimlab/Monitoring_project/neurosurveillance'
rm -rf /home/andrea/Monitoring_project/neurosurveillance

# 3. Fresh clone on e10ubuntu (the source-of-truth side)
ssh skimlab@100.85.191.25 'cd /home/skimlab/Monitoring_project && git clone git@github.com:andrea966p/neurosurveillance.git'

# 4. scp the recovered WIP files on top of the fresh clone (8 modified + 3 untracked + storage_monitor best-effort)
# (See /home/andrea/neurosurveillance-recovery/from_transcripts/ for source files.)

# 5. Re-add the folder to Syncthing on e10ubuntu, then immediately set .stignore via API
#    BEFORE the first scan announces files. Stignore order matters — ! includes must come BEFORE matching wildcards.

# 6. Trigger rescan, accept the share on this PC, set matching .stignore here too.
```

### Final state (verified 2026-04-29 17:55 KST)

```
~/Monitoring_project/   (both PCs)
├── Monitoring_project_obsidian_vault/   [Syncthing — id: monitoring_project_obsidian_vault]
├── neurosurveillance-system/             [Syncthing — id: neurosurveillance-system, public repo b1ff2b9]
└── neurosurveillance/                    [Syncthing — id: neurosurveillance-private, private repo 40b0330 + WIP]
```

All three Syncthing folders: `localBytes` matches `globalBytes`, `needBytes=0`, `errors=0`.

Private repo working tree (matching across both PCs, byte-identical sha256 spot-check):

```
 M backend/daemon.py
 M config/config.yaml
 M frontend/src/App.tsx
 M frontend/src/api/client.ts
 M frontend/src/components/CameraPreview.tsx
 M frontend/src/components/ChamberSilo.tsx
 M frontend/src/types/api.ts
 M frontend/src/utils/format.ts
?? .stignore
?? backend/storage_monitor.py
?? frontend/src/components/StoragePanel.tsx
?? frontend/src/hooks/useStoragePoll.ts
```

Production daemon `neurosurveillance-session.service` and Frigate / mosquitto / uptime-kuma containers — **untouched throughout**.

### Outstanding manual cleanup

1. ~~Review and patch the three TODO methods in `backend/storage_monitor.py`~~ — `get_status` and `can_start_recording` verified correct by live `_poll_loop` (confirmed advancing `last_updated`). `fetch_camera_bitrates` connects to go2rtc but returns `default_mbps` for all cameras (bitrate extraction not yet implemented — deferred, noted in commit `423e8f5`).
2. ~~Compare recovered `backend/api.py` and `backend/session_manager.py`~~ — `api.py` had a second-order gap (see Recovery Quality table); restored in `423e8f5`. `session_manager.py` confirmed identical to HEAD.
3. ~~Add `.stignore` to `.gitignore`~~ — done in commit `fd5e48b`.
4. The recovery staging dir `/home/andrea/neurosurveillance-recovery/` (~5 MB) can be deleted. Contains GitHub clone, Antigravity history, full Claude Code transcripts, pyc + disassemblies, and from_transcripts replay output.
5. Implement actual bitrate parsing in `fetch_camera_bitrates()`. The go2rtc `/api/streams` payload has no ready-made bitrate field — options: (a) two `bytes_recv` samples with 1s sleep (accurate, slow), or (b) parse `--bitrate <N>` from the `source` exec string (gives configured target, not measured).

## Prevention

> [!tip] Rules for combining Syncthing with git repos
>
> **Never `rm -rf` files inside an active Syncthing folder.** "Pausing" the folder does not protect against deletion announcements when sync resumes. Either:
> - Remove the folder from Syncthing's config (`DELETE /rest/config/folders/<id>`) **before** wiping files locally; or
> - Use `--delete` operations only on the side that should propagate them.
>
> **`.stignore` is not a safety net.** It hides files from sync, it does not preserve them against incoming deletions of their parent dirs. Don't treat ignore patterns as durable backups.
>
> **`.stignore` rules apply top-down — first match wins.** Negation includes (`!path`) **must come before** the wildcard exclude that would otherwise match. Concretely, write `!.vscode/extensions.json` *before* `.vscode/*`, not after. Verify expansion via `GET /rest/db/ignores?folder=<id>`.
>
> **Set `.stignore` on the source side and trigger a rescan *before* adding the folder on the receiver side.** Otherwise the receiver indexes everything (build artifacts included) before the ignore takes effect.
>
> **Two independent git clones of the same repo are not a Syncthing folder.** Decide one canonical side, delete the other's clone, then add to Syncthing — let it create the second copy. Syncthing has no awareness of git's history; merging two `.git/` directories via mtime races corrupts both.

> [!tip] Git inside Syncthing
>
> Acceptable trade-off only if you treat git operations as exclusive: never `commit`/`pull`/`checkout`/`merge` simultaneously on both PCs. If you need sustained git work on one side, **pause Syncthing for that folder on the other side** first. Otherwise expect `.stignore` collisions inside `.git/objects/`.

> [!tip] Recovery checklist (file these mentally for next time)
>
> 1. **Don't reboot or write to disk on the affected machine.** Filesystem-level recovery via `extundelete`/`testdisk` requires the deleted blocks not to be reallocated.
> 2. **Check `~/.claude/projects/<project>/...jsonl` for transcripts.** Every Read/Write/Edit captured the file contents. Subagent dirs under `<session-id>/subagents/` are gold — Explore-style agents do full Reads.
> 3. **Cross-check `.pyc` mtime against transcript baseline.** The transcript replay logic anchors on the most recent full Read of each file, then applies subsequent Edits — but it silently misses *new code added after the last transcript read*. For every recovered Python file, run `stat __pycache__/<file>.cpython-312.pyc` and compare the mtime to your transcript baseline date. If the `.pyc` is newer, the source was edited after the transcript captured it — decompile the `.pyc` to recover the delta. In this incident: `api.pyc` was Apr 2 but the transcript baseline was Apr 1 → storage endpoints (added Apr 2) were missed, only caught on daemon restart.
> 4. **Editor history** (Antigravity, VS Code, JetBrains) under `~/.config/<editor>/User/History/`.
> 5. **Production deploys / `/opt/`** if separate from working tree.
> 6. **`__pycache__/*.pyc`** for Python files. `pycdc` works for most of 3.12 except a few opcodes; `pylingual` is pickier but better quality where it works.

> [!warning] If you ever need to combine an existing project folder with Syncthing, follow this order:
> 1. **First** decide which side is the source of truth. Delete the other side's local copy.
> 2. **Set `.stignore` on the source side** before sharing.
> 3. Add to Syncthing on the source. Let it scan with the ignores already in place.
> 4. Share with the receiver. The receiver gets a clean tree, ignores in place from the start.

## Related

- Plan that triggered this work: `/home/andrea/.claude/plans/i-want-you-to-transient-gem.md`
- Recovery staging area on `Andrea-KAIST-PC-ubuntu`: `/home/andrea/neurosurveillance-recovery/`
- Storage-monitor disassembly reference: `/home/skimlab/storage_monitor.disassembly.txt`
- Public repo (unaffected): `https://github.com/andrea966p/neurosurveillance-system`
- Private repo (recovered to HEAD `40b0330` + WIP overlay): `https://github.com/andrea966p/neurosurveillance`
- See also: [[production-values|production-values.md]] for system identifiers used here.

## Closing note, 2026-09-16

The root cause of this incident stopped existing today. **Syncthing was uninstalled
from `e10ubuntu`**, so nothing on this machine can propagate a deletion any more. It
had already been dead since 2026-09-10, when the whole workspace became ONE git
repository (`sleep-recording-skim`) that syncs by hand with `./skim pull` and
`./skim push`.

The lesson this incident taught is the one that shaped the replacement, so it is
worth restating: **two sync systems on one directory, with a live `.git` replicated
and no file versioning, is how a vault dies.** Git alone has none of those three
properties. Every change is a commit, a delete is reversible, and nothing moves
unless a human types a verb.

> [!warning] Syncthing is still installed on the office PC and on the ThinkPad.
> Everything below still applies on those two machines until they are cleaned up the
> same way. In particular: **never remove a folder with the "delete on disk" option**,
> and check which configuration directory is live first — on the ThinkPad it is
> `~/.local/state/syncthing`, not `~/.config/syncthing`.

`./skim check` still carries a Syncthing tripwire and it is deliberately NOT being
removed. If anyone ever reinstalls Syncthing and points it at this repository, the
check fails loudly.

See [[2026-09-16|the 2026-09-16 journal]] for the removal
itself and for what was kept.

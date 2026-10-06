---
name: feedback-never-strip-during-a-live-recording
description: "Do not run channel stripping, or any heavy disk job, while the rig is recording. A run started through the recording console strips itself automatically on stop."
metadata:
  node_type: memory
  type: feedback
---

# Do not strip anything while the rig is recording

**2026-09-18.** Andrea stopped a `convert/strip_channels.py` run mid-request with
"do not strip or touch the ongoing recording". The target was actually a finished
file from a previous day, not the live one — but the instruction is about the
RIG, not the file: **while a recording is in progress, do not start stripping or
any other heavy read/write on that disk.**

**Why:** a run started through the recording console at `127.0.0.1:8600` is
stripped and uploaded automatically by `eeg-recorder/backend/postprocess.py` when
the scheduler stops it. Doing it by hand is redundant, and competing for the same
NVMe with a live 8-animal recording risks the thing that cannot be repeated.
`strip_channels.py --dry-run` prints `RIG BUSY` for exactly this reason; treat
that line as a stop, not a warning. `--require-idle` makes it a hard refusal.

**How to apply:** if stripping is asked for while `api/state` shows
`active_run: RECORDING`, say the run will strip itself on stop and offer to do
any manual strip after it finishes. A dry run is fine; the real thing waits.

⚠️ The automatic strip keeps only the run's frozen `keep_labels` — the 16 wired
channels — so the stripped copy has **no wire-free floor** and can never be QC'd
by this project's own criterion. The original on the rig is the record of truth.
See [[skim-nas-smb-and-channel-stripper]].


## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🛑 **[NEVER strip or run heavy disk jobs while the rig is recording](feedback-never-strip-during-a-live-recording.md).** A console-started run strips itself on stop; `RIG BUSY` in a dry run = stop.

---
name: radiens-4-has-no-per-port-recording
description: "Measured 2026-09-11: radiens 4.0.0 AllegoClient has no per-port recording (only global set_recording); 4.0.0 is the latest stable, do not upgrade; restart() is broken. Detail in the vault"
metadata:
  type: reference
---

The installed radiens 4.0.0 `AllegoClient` (25 public methods) has only global `set_recording(mode)` (`RecordMode` OFF/ON); `start_recording(port=)`, `stop_recording(port=)` and `split_files_by_port` exist only in the protobuf. One recording, all four ports, one file: per-user slicing after the fact is the only route. 4.0.0 IS the latest stable on PyPI (only `5.0.0.dev1` is newer).

Details: [[radiens-api-reference]] (Known gaps in radiens 4.0.0) · [[multi-user-independent-recording-schedules]] (retraction) · [[2026-09-11-allego-control-bench-test]] · [[skim-nas-smb-and-upload]]

- 🛑 Do NOT "fix" this by upgrading radiens, least of all to a dev build under a live-animal instrument.
- 🔑 `set_recording('off')` exists but no repo code had called it as of 2026-09-11: bench-test on a junk recording before any animal run.
- ⚠️ `AllegoClient.restart()` is broken (`mode.enum`): call the `Restart` gRPC with `mode.value` (reported 2026-09, not re-run).

---
name: radiens-4-has-no-per-port-recording
description: "Measured 2026-09-11: radiens 4.0.0 AllegoClient has no per-port recording (only global set_recording); 4.0.1 (10-06) is deprecated + broken wheel; successor radiens-core targets Allego 4; restart() is broken. Detail in the vault"
metadata:
  type: reference
---

The installed radiens 4.0.0 `AllegoClient` (25 public methods) has only global `set_recording(mode)` (`RecordMode` OFF/ON); `start_recording(port=)`, `stop_recording(port=)` and `split_files_by_port` exist only in the protobuf. One recording, all four ports, one file: per-user slicing after the fact is the only route. Update 2026-10-28: `radiens` 4.0.1 is deprecated, code identical, wheel lacks gRPC stubs: never install. Successor `radiens-core` 0.1.2 (Py ≥ 3.12) has per-port `start_recording(port=)` and working `restart(mode=)`, but pairs with Allego 4 (e10 runs 3.11.3): a rewrite project, see [[2026-10-28-radiens-4-tiers-and-legacy-licence]].

Details: [[radiens-api-reference]] (Known gaps in radiens 4.0.0) · [[multi-user-independent-recording-schedules]] (retraction) · [[2026-09-11-allego-control-bench-test]] · [[skim-nas-smb-and-upload]]

- 🛑 Do NOT "fix" this by upgrading radiens, least of all to a dev build under a live-animal instrument.
- 🔑 `set_recording('off')` exists but no repo code had called it as of 2026-09-11: bench-test on a junk recording before any animal run.
- ⚠️ `AllegoClient.restart()` is broken (`mode.enum`): call the `Restart` gRPC with `mode.value` (reported 2026-09, not re-run).

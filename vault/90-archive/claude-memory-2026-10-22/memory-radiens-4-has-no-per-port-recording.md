---
name: radiens-4-has-no-per-port-recording
description: Measured 2026-09-11 - the installed radiens 4.0.0 AllegoClient has no start_recording(port=) at all, so per-user recording is impossible and only post-hoc slicing works.
metadata:
  type: reference
---

`vault/02-procedures/multi-user-independent-recording-schedules.md` records
`start_recording(*, port=...)` / `stop_recording(*, port=...)` and
`RecordingConfig.split_files_by_port` as "DOC-VERIFIED against raw API HTML" (2026-07-24).

**Those methods do not exist in the installed client.** Measured 2026-09-11 by introspecting
`radiens.AllegoClient` in `/opt/neurosurveillance/venv`: 25 public methods, and the only
recording control is **global `set_recording(mode)`** with `RecordMode` = `{OFF:0, ON:1}`.
`grep` over the whole installed package finds `splitFilesByPort` **only** in
`grpc_radiens/allegoserver_pb2.pyi`, i.e. in the protobuf, never in the client.

⭐ **radiens 4.0.0 IS the latest stable on PyPI.** Only `5.0.0.dev1` (a Jan-2026 dev
pre-release) is newer, and its PyPI description mentions none of these methods. So this is
not a case of being behind — do not "fix" it by upgrading, especially not to a dev build
under a live-animal instrument.

⇒ **One recording, all four ports, one file.** Per-user *recording* is impossible on this rig;
per-user *slicing after the fact* is the only route. That is what
[[skim-nas-smb-and-channel-stripper]] implements.

🔑 `set_recording('off')` DOES exist (resolves to `api_allego.set_record_state(...,
RecordMode.OFF)`) but **no code in this repo has ever called it** — bench-test on a junk
recording before it goes near an animal run.

⚠️ `AllegoClient.restart()` is also broken (`mode.enum`); call the `Restart` gRPC with `mode.value` instead. (Moved here from the MEMORY.md index, 2026-10-06.)

## From the memory index, trimmed there 2026-10-06 (kept here verbatim)

- 🔴⭐⭐ **[radiens 4.0.0 HAS NO PER-PORT RECORDING](radiens-4-has-no-per-port-recording.md).** Recording is GLOBAL. 4.0.0 IS latest stable — don't upgrade to fix it. ⚠️ `AllegoClient.restart()` is also broken (`mode.enum`); call the `Restart` gRPC with `mode.value`.

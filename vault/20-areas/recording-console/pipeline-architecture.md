---
type: reference
area: recording-console
status: active
tags: [infrastructure, eeg, recording, architecture, pipeline, allego, nas]
created: 2026-09-13
---

# The recording pipeline: what runs, what fires it, and what stops it going wrong

> [!warning] 2026-10-28: the console was ported to Allego 4 and `radiens-core`, with one run per port ([[2026-10-28-per-port-console-port]]). Where this page says recording is global, one run owns the rig, the mode is `XDAQ_ONE_REC`, or `set_recording_config()` is broken, that was true for `radiens` 4.0.0 on Allego 3.11.3 ([[2026-10-28-per-port-recording-bench-test]]). The two services still run the old code until they are restarted (pending); the guard table in 3.1 is updated to the new rules.

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The machinery behind the recording console: every program involved,
> what starts each one, what each refuses to do, and what happens when something breaks
> halfway through. The console page tells you which buttons to press; this page tells you
> what happens after you press them, and is the page to read before changing any of it.
>
> **Why it exists.** The system now starts and stops amplifiers with animals attached,
> reads 90 GB files, deletes channels permanently and copies data off the machine. Every
> one of those can go wrong quietly. The design is mostly refusals, and a refusal nobody
> can find the reason for gets deleted by the next person — so the reasons live here.
>
> **How to read this page.** §1 is the shape of the whole thing in one diagram. §2 walks a
> single run from button to NAS. §3 is the failsafes, which is the part that matters. §4 is
> what happens when things break. §5 is the list of defects this system has already had,
> because every one of them is now a rule. Operator instructions:
> [[eeg-recording-console]]. Background:
> [[nvr-system-overview]].

## 1. The shape of it

```
   browser (localhost only)
        │  poll /api/state every 2 s
        ▼
   ┌────────────────────────────────────────────────────────┐
   │  eeg-recorder.service      Flask, 127.0.0.1:8600       │
   │                                                        │
   │   app.py ── presets.py ── config/users.yaml            │
   │      │                                                 │
   │      ├── runs.py        SQLite WAL, the state machine  │
   │      │                                                 │
   │      ├── scheduler.py   one thread, ticks every 5 s    │
   │      │        │                                        │
   │      │        └── allego.py ──gRPC──► allegoserver     │
   │      │                                                 │
   │      └── postprocess.py one worker thread, one run     │
   │               │              at a time                 │
   │               ├─► cards/ladder.py      (subprocess)    │
   │               ├─► convert/strip_channels.py (subprocess)│
   │               ├─► naming.py     what it is called      │
   │               ├─► layout.py     what the rig IS          │
   │               └─► nas_upload.py ──CIFS──► SKIM_NAS     │
   └────────────────────────────────────────────────────────┘
```

Two threads and two subprocesses. The scheduler and the worker never touch each other
directly; they communicate only through the run store, which is the single source of truth
about what is happening.

**The subprocesses are subprocesses on purpose.** Stripping reads 90 GB and hashes it twice;
the ladder holds a 21 MB feature array and runs for minutes. Neither belongs in the address
space of the service that must keep answering "is the rig recording?" while they run. A
crash in either is a non-zero exit code, not a dead API.

## 2. One run, end to end

| # | What happens | Who does it | Fired by |
|---|---|---|---|
| 0 | declare the rig: setting + a splitter per port | the page | a human |
| 0b | **refuse if that disagrees with what Allego enumerated** | `layout.py` → `app.py` | creating the run |
| 1 | operator fills in owner, batch name, slots, times | the page | a human |
| 2 | `POST /api/runs` validates and stores a run | `app.py` → `runs.py` | the Start/Schedule button |
| 3 | at the instant: preflight, configure, stream, record | `scheduler.py` → `allego.py` | the 5 s tick |
| 4 | file exists + `R_ON` ⇒ **RECORDING** | `scheduler.py` | immediately |
| 5 | 40 s later: bytes grew ⇒ growth confirmed | background thread | a timer |
| 6 | at the stop instant: `set_recording('off')` | `scheduler.py` | the 5 s tick |
| 7 | **STOPPED**, and handed to the worker | `on_stopped` callback | step 6 |
| 8 | QC bundle: use it, or compute it | `postprocess.py` → `ladder.py` | the worker queue |
| 9 | strip to the operator's channels, verify bit-exact | `strip_channels.py` | the worker queue |
| 9b | resolve the NAS folder name, once, and freeze it on the run | `naming.py` → `runs.py` | the worker queue |
| 10 | upload under that name, verify by cache-dropped read-back | `nas_upload.py` | the worker queue |
| 11 | **DONE** | `runs.py` | step 10 |

### The state machine

```
DRAFT ─► SCHEDULED ─► STARTING ─► RECORDING ─► STOPPING ─► STOPPED
                                                              │
     DONE ◄─ UPLOADING ◄─ UPLOAD_PENDING ◄─ STRIPPED ◄─ STRIPPING ◄─ QC
```

Any non-terminal state may record a `FAILED_*`; only forward progress is checked. Retries
rewind through `runs.RETRY_TARGET`, which is **the single definition** — the API imports it
rather than keeping a copy, and a test asserts every entry is a legal transition.

## 3. The failsafes, and what each one is for

This is the part worth reading. Each entry is a refusal, and each exists because of a
specific way this rig can hurt you.

### 3.1 Before a recording starts

| Guard | Refuses when | Why |
|---|---|---|
| preflight: server | `allegoserver` is not running | gRPC-reachable and process-alive are different failures |
| preflight: mode | not `XDAQ_CORE_REC` (`XDAQ_ONE_REC` on Allego 3.11.3) | a freshly launched Allego comes up in `SMARTBOX_PRO` |
| preflight: rate | not 1000 Hz (since 2026-10-28 the console also reports the measured stream rate as a ratio to wall clock) | a fresh launch comes up at 30 kHz ([[2026-10-28-allegoserver-death-and-fresh-launch-defaults]]) |
| preflight: already on | `R_ON` | never disturb a running recording |
| preflight: space | < 150 GB free | a 24 h run is ~90 GB |
| one run per port | another booked or active run uses one of the same ports at the same time (refused with HTTP 409 at booking, since 2026-10-28) | two runs on one port would put two people's animals in one file. Before 2026-10-28 the rule was "one run owns the rig", because recording was global |
| mouse id | anything outside `[A-Za-z0-9_-]{1,32}` | it becomes part of a filesystem and NAS path |
| owner | not in `users.yaml` | an unknown name would have no folder, or the wrong one |
| no default owner | — | the API returns users alphabetically; a default silently files one person's run under another's name |

### 3.2 While recording

> [!info] 2026-10-28: the next three paragraphs are radiens 4.0.0 facts. The console now uses `radiens-core`, and it finds a port's file by name pattern, never from `active_filename` (which shows only the first file's name). `radiens-core` 0.1.2 is now in `/opt/neurosurveillance/venv` (2026-10-28). The old `radiens` 4.0.0 is still installed there but must not be imported: the two cannot load in one process (`duplicate file name common.proto`), and no code imports it any more. Whether `radiens-core` fixes `set_recording_config()` and the `recording.path` report was not re-measured here. [[2026-10-28-per-port-console-port]]

**Configuration is verified, not assumed.** `set_recording_config()` in radiens 4.0.0 is
broken — `ConfigRecording` has a required `recordingType` enum the library never sets — and a
failed config **silently leaves the previous path in place**. `allego.configure()` builds the
protobuf directly and raises rather than returning a status.

🔴 **`get_status().recording.path` LIES.** It reports the calling process's working
directory, not the output directory. It is never used to check anything.

🔴 **The file size lags ~30 seconds.** Measured: after a healthy start the file exists
immediately and `getsize()` returns **0 for a full 30 s**, then jumps to ~31 MB. Verification
is therefore two-stage — *started* (file exists + `R_ON`, immediate) and *growing* (size
increased, only after ≥ 35 s) — and `confirm_growing()` **refuses a window shorter than
35 s rather than lying**. The console tells the operator that 0 bytes is normal at first.
See [[2026-09-11-allego-control-bench-test]].

**Anything that asserts on growth stops the recorder in a `finally`.** A false negative that
leaves the amplifiers running is worse than the false negative.

### 3.3 Around the strip — the irreversible step

| Gate | Checks | On failure |
|---|---|---|
| source guards | integrity, no second layout table, array lengths, byte alignment | refuse, nothing written |
| **A** bit-exactness | every kept column vs the original, on raw `uint32` (not a tolerance, so NaN and −0.0 cannot pass) | quarantine |
| **B** dropped `din` | ≥ 4 transitions, or off-resting > 1 s | quarantine |
| **C** integrity | output `INTACT`, right channel count, sample counts match | quarantine |
| **D** round trip | `open_xdat` returns exactly the expected labels, `fs`, sample count | quarantine |
| **E** Radiens parse | optional | **unprovable here — no Videre hub**, so it *skips* and records the question as open |

A failed output is renamed `<dst>.REJECTED.<utc>.*` so it can never be mistaken for good
data. A partial run leaves only `.part` files, which nothing in this project opens.

🔴 **The QC bundle is a precondition, not a follow-up.** Stripping deletes the wire-free
floor that every verdict on this rig is measured against, after which `compute_features` can
never run on that recording again. The chain therefore **computes the bundle itself** before
stripping, and the waiver — when someone genuinely wants it for a test — is recorded **on
that run** and applies to that run alone.

### 3.4 Around the upload

🔴 **A failed CIFS mount leaves `/mnt/skimnas` as an ordinary directory on the rig's own
NVMe** — the disk the amplifiers write to. `mountpoint` does **not** catch this, because an
empty local directory is a valid mountpoint. Every write is gated on reading a sentinel file
that exists only on the share.

🔴 **Read-back over CIFS verifies your own page cache.** Measured on a fresh 200 MB file:
1538 MB/s cached versus 89.8 MB/s after `posix_fadvise(POSIX_FADV_DONTNEED)`. The uploader
drops the cache before hashing and **reports the achieved rate**, so a weak check is visible;
it warns above 400 MB/s.

**`VERIFIED` means a receiving-side hash matched.** A size check records as `SIZE_ONLY` and
is never counted as done. Files land as `.part` and are renamed only on a match.

**Nothing is ever deleted locally.** The original stays where Allego wrote it.

### 3.5 Across restarts and outages

| Situation | Behaviour |
|---|---|
| service restarts mid-recording | the run is untouched; Allego is a separate process and keeps writing |
| service restarts mid-strip or mid-upload | in-flight states rewind to the last actionable one; the worker's boot sweep re-queues |
| NAS unreachable | the run rests in `UPLOAD_PENDING` and drains in order when it returns — **a resting state, not an error** |
| missed scheduled start, < 3 min | starts, lateness recorded |
| missed scheduled start, > 3 min | **`FAILED_START`** — a sleep recording that begins hours from ZT0 is not the experiment that was designed |
| missed scheduled stop | **always stops**, however late; overrun recorded. Stopping late costs a longer file, not stopping costs 90 GB/day |

## 4. Where to look when something is wrong

```bash
journalctl -u eeg-recorder -f                  # the service
curl -s localhost:8600/api/state | python3 -m json.tool
curl -s localhost:8600/api/runs/<run_id> | python3 -m json.tool   # includes the event log
```

Every run carries its own event log with a timestamp and a reason for every transition. That
log, not the service journal, is the record of what happened to a recording.

State lives at `{RECORDER_STATE}/runs.db`; upload bookkeeping at
`eeg-recorder/deploy/uploads.jsonl`. Neither is versioned — both are per-machine.

## 5. Every defect this system has had, and the rule it produced

Fourteen defects, four provenances, and the mix is the point:

- **Seven were found by running it** (1-6, 10). No test caught them. Number 10 is the sharpest: it had been latent on every real run, passing only because an unrelated stage happened to be slow enough.
- **Two were found by asking one question nobody had asked** (7-8) — *what does this do with
  four mice instead of eight?* Cheaper than running it, and the method that scales.
- **One was found by writing a test** (9), which in the process wrote eight false `VERIFIED`
  rows into the live upload manifest. A test that touches production state is a production
  action; this one was caught the same hour, and the rule it produced is in the table.
- **Four were found by an operator using it** (11-14). Three of those were reported in the
  plainest possible terms — "failed QC label again", "i have no way to select the allego
  channels" — and each took minutes to find once someone had actually tried to do the thing.
  Number 14 was found by listing what still needed bench testing, before anyone hit it.

| # | Defect | Rule it produced |
|---|---|---|
| 1 | the API's retry map disagreed with the state machine's table; two of three retry paths returned HTTP 500 | **two copies of one rule in different files will drift** — one definition, and a test that binds them |
| 2 | waiving the QC bundle flipped a flag on the *shared* worker, disabling the guard for every later run, invisibly | **an override applies to one run and is recorded on it** |
| 3 | a new mouse id blocked a 24 h recording, because QC demanded a hand-written cohort manifest for a two-element role list the console already knew | **never require a human to restate something the system already has** |
| 4 | Gate B refused a 90 GB strip over a single 1 ms blip on an unconnected input | **count the evidence; "not constant" cannot tell a signal from a speck** |
| 5 | a *scheduled* stop halted the rig and then stranded the run — `worker.submit` existed only on the HTTP endpoint | **every path that ends a recording goes through one handoff** |
| 6 | dates came from UTC on a rig that runs on KST, filing a 09-12 recording as 09-11 | **the uid in the filename is already local; use it** |
| 7 | a four-mouse run was graded on **eight** positions: `cards/ladder.py` falls back to `spec.positions()`, so five cards came back labelled `UNKNOWN@<slot>` and three of those read **PASS at rung 2** | **grade what the operator filled in, not what the layout could hold** — an empty slot's card is built from a floating amplifier input, and `UNKNOWN@B2 PASS` reads like an animal somebody forgot to name |
| 8 | `unipolar_lfp` could not finish the pipeline *at all*: no floor model describes its sites, so the chain asked for a manual override on **every** run | **a guard that can never be satisfied is a guard people learn to click past** — declare "no criterion applies" in the config, and keep it distinguishable from "a person waived the check" |
| 9 | a test wrote eight `VERIFIED` rows into the **real** upload manifest for files never uploaded, because `manifest_load(path=MANIFEST)` bound the path at import time and overriding the module constant did nothing | **a default argument is not a hook** — anything a test must redirect is read at call time; and a manifest the uploader *skips* on is a claim about the world, not a log |
| 10 | the strip REFUSED the file it was asked to strip: `--require-idle` uses mtime, which cannot tell "stopped four seconds ago" from "being written right now", and every strip follows a stop by seconds | **a guard must test the thing it means, not a proxy that usually correlates** — and note it had never fired because QC runs first and on a 24 h file takes long enough for the mtime to age out BY ACCIDENT, so the protection on every real run was incidental |
| 11 | the same mouse id in six slots was accepted, recorded for six minutes, and only then failed: the cohort schema refuses duplicate animal_ids, so no QC bundle could be computed | **check what makes a run unjudgeable while the form is still on screen** — and fold case, because `HLBSSL31` and `hlbssl31` are one mouse to everyone except a string comparison |
| 12 | "Custom" was a selectable dropdown entry whose handler was `if (!t) return;` — it did nothing, and there was no way anywhere to choose channels at the point of use | **a control that does nothing is worse than no control**; and the picker that replaced it seeded from whichever headstage sorted first alphabetically, which gave the wrong floor and a failing rig check |
| 13 | after extracting one shared validator to stop the config file and the console diverging, the role-NAME rule was left behind in the settings panel — so it refused `trial 2` while the inline picker accepted it, and a real run reached the NAS with spaces in its role names | **extracting a shared rule is not finished until the old copies are gone**; and validate on INPUT, not on REPLAY, or tightening a rule makes yesterday's data unopenable |
| 14 | a port with no headstage enumerates 0, the check refused it, and the page had no way to say "I am not using that port" — `ports_used` existed in the backend and the UI never sent it | **a refusal must name its escape**, or a correct guard reads as a broken feature |

> [!quote] Paper-ready
> Acquisition is controlled by a local service that records, for each run, the responsible
> investigator, the animal identifier and condition assigned to each amplifier position, and
> the electrode sites in use. Recording state is held in a write-ahead-logged database so
> that a run survives restarts of the controlling process. After acquisition, per-epoch
> quality measures are computed on the complete recording, the recording is reduced to the
> electrode sites in use and verified bit-exact against its source, and the reduced copy is
> transferred to institutional storage and verified by a checksum computed on the stored
> bytes. The complete original recording is retained unmodified.

## 6. What is still not true

- **Gate E is unproven.** Whether the Radiens reader accepts a stripped file cannot be
  tested here — `FileSystemClient` needs a Videre hub and there is no Videre binary under
  `/opt/allego`. Our own reader accepts it.
- **No unattended overnight run has completed yet.** Scheduling is verified on a 9-minute
  bench run (2026-09-13): started 3 s after the instant, stopped 0.5 s late, full chain
  afterwards. A real overnight is the next step.
- **`unipolar_lfp` has never recorded anything.** Its label→index resolution and its strip are
  proven against the one real 134-channel file on disk (2026-09-13: 30 channels out, gate A
  exact), but no unipolar headstage has ever been connected to this rig, so nothing has
  exercised it from a live amplifier. It also produces **no QC bundle by design** — see
  defect 8 — so a unipolar recording carries no quality verdict from this project at all.
- **`8mice_eeg_emg_ecg` has never been run through the console.** The strip is proven on a
  real three-role recording; start→stop→upload for it is not.
- **The console does not know whether electrodes are connected.** It reports that bytes are
  landing. [[pre-flight-connection-screen]] still gates any recording whose
  timepoint dies with the animals.

## 7. Related

- [[eeg-recording-console]] — how to use it
- [[xdat-channel-stripping]] — the strip contract and its gates
- [[skim-nas-smb-and-upload]] — the NAS and how uploads are verified
- [[2026-09-11-allego-control-bench-test]] — the 30 s size lag
- [[recording-console-retry-was-a-dead-end]] — defects 1–3
- [[multi-user-independent-recording-schedules]] — why recording was global (retracted 2026-10-28, see [[2026-10-28-per-port-recording-bench-test]] and [[2026-10-28-per-port-console-port]])

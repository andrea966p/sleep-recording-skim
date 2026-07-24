---
tags: [procedure, todo, radiens, allego, multi-user, scheduling, xdaq]
created: 2026-07-14
status: open-todo
---

# Multi-User Independent Recording Schedules — TODO

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The rig has one XDAQ box. Right now, pressing Record in Allego starts recording for the WHOLE box, every port, at once — there is no way to give two lab members two different start/stop times on the same physical rig. This page documents the problem, the workaround to use TODAY, and the open engineering questions for a real fix.
> **Why it exists.** Came up 2026-07-14: I want to start my 4 mice Monday 9am for 48h, another lab member needs their 4 mice Monday 9pm for 48h, same rig. Allego can't do that natively.
> **How to read this page.** Section 1 is the constraint. Section 2 is the workaround to use now (safe, zero new code). Section 3 is the TODO list of things to investigate/build for a real fix.

---

> [!important] UPDATE 2026-07-24 — the "GUI-only" constraint holds, but the Radiens PYTHON API overturns "no per-port control". DOC-VERIFIED.
> The section below is correct **for the Allego GUI**. It is NOT correct as a blanket statement: the current **Radiens Python API (radiens v4.0.0) documents per-port recording**, which is exactly the fix this TODO was chasing. Verified 2026-07-24 against the raw API HTML (not paraphrased):
> - **`start_recording(*, port=None)`** / **`stop_recording(*, port=None)`** — verbatim: *"Optional port to start/stop recording on. Accepts Port enum, single-letter string ("a"–"h"), or int (0–7). If omitted, applies system-level control."* (`set_record_state` is now DEPRECATED in favour of these.) Source: https://neuronexus.github.io/radiens-core-python/latest/reference/radiens_core/
> - **`RecordingConfig.split_files_by_port: bool`** — verbatim: *"True to create separate files for each port. Defaults to False."* Source: https://neuronexus.github.io/radiens-core-python/latest/reference/radiens_core/models/status/
> - So per-port **independent start/stop** AND per-port **separate files** are both DOCUMENTED API features — no longer "just a label / untested / impossible".
> - ⚠️ **Documented ≠ validated on our Gen-1 XDAQ Core.** Still needs the bench test in §3 (crash-on-churn risk on the Opal Kelly Gen-1). Treat as "documented, plausible, unproven on our box." The GUI-only facts below remain true.
> - Cross-ref: [[2026-07-24-daq-32-mouse-final-comparison#2. Master 3-way comparison table]] Row 15 record-control callout (also compares Open Ephys, whose GUI gives separate files per animal but only GLOBAL start/stop).

## 1. The constraint (GUI-only; API updated above)

- **In the Allego GUI**, the Record button drives ONE global `R_ON`/`R_OFF` signal for the entire XDAQ box, all 4 ports at once, one output file. Confirmed in [[session-recording-workflow]]: "Radiens provides a single global R_ON/R_OFF signal." (Radiens manual p29: single Record button, one recording file name/location.) **The Python API is NOT limited this way — see the update callout above.**
- Per-port CHANNEL SELECTION exists (which channels get recorded, [[eight-mouse-acquisition-setup]] §6), but in the GUI that is not per-port START/STOP TIMING. Selection changes what's in the file; the GUI can't give one port a different start time than another. (The API's `start_recording(port)` + `split_files_by_port` can — pending validation.)
- **Opening multiple Allego GUI windows does NOT solve it.** Reasoned from architecture (not yet bench-tested): all GUI windows are clients of the SAME backend process (`allegoserver`, the same thing the Python SDK talks to over gRPC). Channel selection and record state live server-side, not per-window. Two outcomes if tried: (a) second window shares the same state, so pressing Record anywhere fires the one global signal everyone sees, or (b) second window fails to attach to the XDAQ hardware entirely (Gen-1 XDAQ = Opal Kelly USB, likely single-connection lock). Either way, no independent control.

## 2. Workaround for now — union the window, slice offline

No new code beyond what already exists (`xdat_io.py` / `multimouse_scan.py`). No restart risk, no crash risk.

1. Before the EARLIEST start time, wire and Allego-configure BOTH users' headstages (all mice's channels ticked in the Signals tab). Do this once, don't touch Allego mid-run.
2. Press Record ONCE at the earliest start time (e.g. Monday 9am).
3. User 1's mice connect to the slip ring at 9am as normal.
4. User 2's mice stay OFF the slip ring (headstage stays plugged into its port, already selected, just not clipped to an animal) until their actual start time (e.g. Monday 9pm). Their channels read floor/hum until then — harmless, ignored in analysis. Connecting the slip ring at 9pm is a physical animal-side action only, does NOT touch Allego, does NOT re-enumerate the port, does NOT risk the known sensor-reload/channel-churn crash.
5. Stop recording once when the LAST user's window ends (e.g. Wednesday 9pm if user 2 = 9pm Mon + 48h).
6. Offline, slice the one master XDAT file per user by sample index: `t=0` in the file = the single Record press. User 1's window = samples `0` to `48h*fs`. User 2's window = samples `12h*fs` to `60h*fs` (the 12h offset between the two starts). Trivial with the existing memmap-based tooling.

## 3. TODO — open items for a real per-port fix

- [ ] **Bench-test the radiens API per-port recording on our Gen-1 Core.** ✅ DOC-CONFIRMED 2026-07-24 (raw API HTML): `start_recording(*, port="a".."h"|0..7)` / `stop_recording(*, port=...)` exist and are documented to control a single port (omit port = system-level), and `RecordingConfig.split_files_by_port=True` writes separate files per port. So it is NOT "just a label" — the vendor documents genuine per-port control. What remains is VALIDATION ON OUR HARDWARE: (a) does `start_recording(port=C)` start ONLY port C without disturbing ports already recording, and (b) does `split_files_by_port` produce clean per-port XDAT. The daemon has only ever POLLED Radiens state, never called these — so still untested ON OUR BOX. Test on a junk/no-animal recording first — Allego's backend is known to crash under fast sensor-reload/channel churn ([[eight-mouse-acquisition-setup]] §8), so treat as a live-fire risk, not a routine call. (Note: `[[radiens-api-reference]]` does not yet exist as a vault note — create it from https://neuronexus.github.io/radiens-core-python/latest/ when writing this up.)
- [ ] **If per-port SDK control works:** write a small script (candidate location: alongside `multimouse_scan.py` in `02-procedures/eeg-data-analysis/scripts/`, or a new `session_manager` hook) that lets a user request "start recording port C+D at 9pm" without touching the GUI or other ports' state.
- [ ] **Ask NeuroNexus/KonteX directly** (existing contact thread, [[neuronexus-inquiry-email]]) whether independent per-port recording control is supported at all, officially, and how. One email probably settles the `start_recording(port)` question faster than bench-testing blind.
- [ ] **Evaluate a second physical acquisition box** (second XDAQ, or repurpose an old Intan RHD2000 USB interface board if the lab has one) as the fully independent, zero-shared-state option. [[session-recording-workflow]] already flags this: "If two headstages need independent control, additional Radiens instances and daemon configuration would be required." This is the most robust option if multi-user overlapping-but-different-schedule recording becomes routine rather than a one-off. Costs hardware; worth it if this keeps happening.
- [ ] **Confirm (don't just infer) that multiple Allego GUI windows share state / can't attach twice to Gen-1 XDAQ hardware.** Currently architectural inference, not observed. Low priority since the workaround in §2 already avoids needing this, but worth a 2-minute check if idle time allows.
- [ ] Once any of the above is resolved, extend `multimouse_scan.py` with a `--window start_h end_h` slice-and-export option so the §2 workaround's offline split step is one command instead of manual indexing.

## Related
- [[session-recording-workflow]] — confirms the single global R_ON/R_OFF
- [[radiens-api-reference]] — SDK method names, incl. `start_recording(port)`/`stop_recording(port)`
- [[eight-mouse-acquisition-setup]] — per-port channel selection, known crash gotchas
- [[eeg-data-analysis/scripts/multimouse_scan.py]] — existing memmap-based multi-headstage scan tool, base for the future slice-export option
- [[neuronexus-inquiry-email]] — existing KonteX/NeuroNexus contact thread to ask the per-port question

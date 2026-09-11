---
tags: [troubleshooting, symptom, eeg, recording, console, bug]
created: 2026-09-11
status: resolved
---

# The console's retry button did nothing — three defects, found by the first real run

> [!abstract] TL;DR — for non-technical readers
> **What this is.** The first time a person used the recording console for real, their recording
> stopped, was held back for a missing quality-control step, and the "retry" button did nothing at
> all. This is what was wrong: three separate faults, one of which was worse than the visible
> symptom.
>
> **Why it exists.** All three had passed every automated test. They were found within minutes of a
> human using the tool for a one-minute test recording, which is the argument for doing that early.
>
> **How to read this page.** Each defect has its symptom, its cause and its fix. Defect 2 is the one
> to read if you read only one. Background: [[02-procedures/eeg-recording-console]].

**Trigger:** a manual 1-minute run on 2026-09-11 (`allego_0__uid0911-22-32-22`). The recording
itself worked perfectly — started on time, growth confirmed at 2.86 GB/h, stopped cleanly. Everything
after it was broken.

## Defect 1 — the retry was not a legal state transition (the visible symptom)

**Symptom.** Press retry on a `FAILED_QC` run, nothing happens, an error toast appears.

**Cause.** The API kept its own private map of where a retry rewinds a failed run to, and it
**disagreed with the state machine's own table**:

    retry says   FAILED_QC   -> STOPPED
    LEGAL says   FAILED_QC   -> {QC, STRIPPING, ABORTED}     ← STOPPED not allowed

So the transition raised `IllegalTransition` and the endpoint returned HTTP 500.
`FAILED_STRIP → QC` was illegal too, so **two of the three retry paths were dead**.

**Why no test caught it.** The suite exercised the store's transitions directly, and the scheduler
against a fake rig. Nothing ever checked the API's retry map *against* the legal table. Two maps of
the same thing, in different files, with no test binding them.

**Fix.** One definition, `runs.RETRY_TARGET`, which the API imports rather than copying, plus the
missing rewinds added to `LEGAL`, plus `test_retry_targets_are_legal` which asserts every retry the
API offers is legal **and then drives each one through the store for real**.

> [!warning] TWO COPIES OF THE SAME RULE IN DIFFERENT FILES WILL DRIFT
> The generalisable lesson. It is not enough for both to be individually reasonable; something has
> to fail if they stop agreeing.

## Defect 2 — 🔴 waiving the QC bundle disabled the guard for EVERYONE

**Symptom.** None. This one is invisible, which is what makes it the serious one.

**Cause.** The override was implemented as `worker.require_qc_bundle = False` on the **shared worker
object**. That worker is a single long-lived instance serving every run, so one person waiving the
QC requirement once, for one test recording, would have **silently disabled the requirement for every
subsequent run by every user until the service was restarted** — and left no record that it had
happened.

Stripping permanently destroys the in-file wire-free floor
([[02-procedures/installation/xdat-channel-stripping]] §2). A guard against that which one click can
switch off for the whole lab, invisibly, is not a guard.

**Fix.** The override now lives in the **run's own record** (`results.skip_qc_bundle`), so it applies
to exactly one recording, and the run's event log says
`no QC bundle -- EXPLICITLY OVERRIDDEN for this run`. Covered by
`test_qc_override_is_per_run_not_global`, which waives it on one run and asserts it did not leak to
another.

> [!quote] Paper-ready
> Quality-control prerequisites may be waived for an individual recording, for instance a short
> instrument test, but never globally: the waiver is recorded in that recording's own provenance and
> applies to it alone, so any dataset processed without its quality-control record is identifiable
> as such after the fact.

## Defect 3 — the button offered no way forward

**Symptom.** Even with defect 1 fixed, retrying a `FAILED_QC` run just fails the same way again,
because nothing about the run has changed.

**Cause.** The API supported a `skip_qc_bundle` flag; the button never sent it. So the only escape
from `FAILED_QC` was a `curl` command.

**Fix.** Retry on a `FAILED_QC` run now asks, and states what is being given up — that the recording
can never be quality-checked again — with "strip it anyway" and "leave it alone" as the two options.
The history table shows `no QC bundle` for runs processed that way.

## What was right

Worth recording, because the same run demonstrated it:

- the recording control chain itself worked end to end on the first real attempt
- the two-stage growth check behaved: `0 → 31,792,128` bytes, confirmed at 40 s, with no false alarm
  from the 30-second size lag
- `FAILED_QC` was **correct behaviour**, not a bug. The tool refused to destroy the wire-free floor
  of a recording that had never been QC'd. It was the escape route that was missing
- after the fixes, the same run completed: 93.18% smaller, 4 files verified on the NAS

## Related

- [[02-procedures/eeg-recording-console]]
- [[02-procedures/installation/xdat-channel-stripping]] — why the QC bundle is a precondition
- [[05-experiments/completed/2026-09-11-allego-control-bench-test]]

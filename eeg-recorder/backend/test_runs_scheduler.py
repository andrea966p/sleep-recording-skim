#!/usr/bin/env python3
"""Contract for runs.py and scheduler.py.

Drives the scheduler against a FAKE Allego, so none of this touches the rig. The
point is the decisions -- what gets started, what gets refused, what happens after
a restart -- not the gRPC calls, which were bench-tested separately on 2026-09-11.

Half the cases are refusals, for the same reason as the stripper's suite: a state
machine that accepts every transition is just a mutable string, and the failure it
produces (a run that claims to be RECORDING when nothing is) is silent.

    python3 test_runs_scheduler.py
"""
from __future__ import annotations

import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import runs as R
import scheduler as S
import allego

PASS, FAIL = [], []


def check(name, fn):
    try:
        fn()
    except Exception:
        FAIL.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}")
    else:
        PASS.append(name)
        print(f"  ok    {name}")


def expect(name, fn, exc=Exception, want=""):
    def run():
        try:
            fn()
        except exc as e:
            if want and want.lower() not in str(e).lower():
                raise AssertionError(f"wrong reason: {e}\nwanted {want!r}")
            return
        raise AssertionError("NOT REFUSED")
    check(name, run)


# --------------------------------------------------------------------------- #
# a fake rig
# --------------------------------------------------------------------------- #
class FakeAllego:
    def __init__(self):
        self.recording = False
        self.starts = 0
        self.stops = 0
        self.fail_start = False
        self.grew = True
        self.n = 0

    def start(self, dest, **kw):
        if self.fail_start:
            raise allego.PreflightFailed("fake preflight failure")
        self.starts += 1
        self.n += 1
        self.recording = True
        name = f"allego_{self.n}__uidTEST"
        return {"base_name": name, "base_path": f"{dest}/{name}",
                "data_path": f"{dest}/{name}_data.xdat", "mode": "R_ON",
                "started_at": 0.0, "dest": str(dest)}

    def stop(self, **kw):
        self.stops += 1
        was = "R_ON" if self.recording else "R_OFF"
        self.recording = False
        return {"before": was, "after": "R_OFF"}

    def confirm_growing(self, path, **kw):
        return {"growing": self.grew, "bytes_start": 0,
                "bytes_end": 1 if self.grew else 0, "window_s": 40.0,
                "gb_per_h": 1.05 if self.grew else 0.0}


def mkstore(tmp) -> R.RunStore:
    return R.RunStore(Path(tmp) / "runs.db")


def mkrun(store, *, owner="andrea", start=None, stop=None, slots=None):
    return store.create(
        owner=owner, preset="8mice_eeg_emg",
        slots=slots or {"A1": {"mouse_id": "M1", "recording_type": "basal"},
                        "B1": {"mouse_id": "M2", "recording_type": "basal"}},
        keep_labels=["A/1", "A/2", "B/1", "B/2"],
        scheduled_start=start, scheduled_stop=stop, dest_dir="/tmp/fake-dest")


def iso(dt): return dt.replace(microsecond=0).isoformat()


# --------------------------------------------------------------------------- #
# runs.py
# --------------------------------------------------------------------------- #
def t_create_and_states(tmp):
    s = mkstore(tmp)
    r = mkrun(s)
    assert r.state == R.DRAFT
    assert r.occupied == ["A1", "B1"]
    assert r.mice == {"A1": "M1", "B1": "M2"}
    r2 = mkrun(s, start=iso(datetime.now().astimezone()))
    assert r2.state == R.SCHEDULED, r2.state


def t_legal_transition_path(tmp):
    s = mkstore(tmp)
    r = mkrun(s)
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED,
               R.QC, R.STRIPPING, R.STRIPPED, R.UPLOAD_PENDING, R.UPLOADING, R.DONE):
        r = s.transition(r.run_id, st, detail="walk")
    assert r.state == R.DONE
    ev = s.events(r.run_id)
    assert len(ev) == 12, len(ev)      # create + 11 moves


def t_results_accumulate(tmp):
    s = mkstore(tmp)
    r = mkrun(s)
    s.transition(r.run_id, R.SCHEDULED, results={"a": 1})
    r = s.transition(r.run_id, R.STARTING, results={"b": 2})
    assert r.results == {"a": 1, "b": 2}, r.results


def t_active_is_single(tmp):
    s = mkstore(tmp)
    a = mkrun(s); b = mkrun(s)
    assert s.active() is None
    s.transition(a.run_id, R.SCHEDULED); s.transition(a.run_id, R.STARTING)
    assert s.active().run_id == a.run_id


def t_rewind_in_flight(tmp):
    s = mkstore(tmp)
    r = mkrun(s)
    s.transition(r.run_id, R.SCHEDULED); s.transition(r.run_id, R.STARTING)
    moved = s.rewind_in_flight()
    assert moved == [r.run_id], moved
    assert s.get(r.run_id).state == R.SCHEDULED
    # and an in-flight upload rewinds to the resting state, not to an error
    s.transition(r.run_id, R.STARTING); s.transition(r.run_id, R.RECORDING)
    for st in (R.STOPPING, R.STOPPED, R.QC, R.STRIPPING, R.STRIPPED,
               R.UPLOAD_PENDING, R.UPLOADING):
        s.transition(r.run_id, st)
    s.rewind_in_flight()
    assert s.get(r.run_id).state == R.UPLOAD_PENDING


def t_retry_targets_are_legal(tmp):
    """Every retry the API offers must actually be a legal transition.

    THE TEST THAT WAS MISSING. The API kept its own retry map, it disagreed with
    LEGAL, and two of the three retry buttons raised IllegalTransition and
    returned HTTP 500. Nothing caught it until a real run failed QC and the retry
    did nothing.
    """
    s = mkstore(tmp)
    for failed, target in R.RETRY_TARGET.items():
        allowed = R.LEGAL.get(failed, set())
        assert target in allowed, (
            f"retry sends {failed} -> {target}, which LEGAL forbids "
            f"(allowed: {sorted(allowed)})")

    # and drive each one for real, end to end through the store
    for failed, target in R.RETRY_TARGET.items():
        r = mkrun(s)
        for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED):
            s.transition(r.run_id, st)
        if failed in ("FAILED_STRIP", "FAILED_UPLOAD"):
            s.transition(r.run_id, R.QC)
        if failed == "FAILED_UPLOAD":
            s.transition(r.run_id, R.STRIPPING)
            s.transition(r.run_id, R.STRIPPED)
            s.transition(r.run_id, R.UPLOAD_PENDING)
        s.transition(r.run_id, failed, detail="simulated failure")
        got = s.transition(r.run_id, target, detail="retry")
        assert got.state == target, (failed, got.state)


def t_qc_override_is_per_run_not_global(tmp):
    """Waiving the QC bundle must apply to ONE run and be recorded on it.

    An earlier version flipped a flag on the shared worker, which disabled the
    guard for every later run until the service restarted, with no trace.
    """
    s = mkstore(tmp)
    a, b = mkrun(s), mkrun(s)
    for r in (a, b):
        for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED):
            s.transition(r.run_id, st)
        s.transition(r.run_id, "FAILED_QC", detail="no bundle")
    # waive it for `a` only
    s.transition(a.run_id, R.RETRY_TARGET["FAILED_QC"],
                 results={"skip_qc_bundle": True})
    assert s.get(a.run_id).results.get("skip_qc_bundle") is True
    assert not s.get(b.run_id).results.get("skip_qc_bundle"), \
        "waiving the bundle on one run leaked to another"


def t_upload_pending_is_a_resting_state(tmp):
    """A NAS outage must leave runs waiting, not failed."""
    s = mkstore(tmp)
    r = mkrun(s)
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED,
               R.QC, R.STRIPPING, R.STRIPPED, R.UPLOAD_PENDING):
        s.transition(r.run_id, st)
    # retryable, repeatedly, without ever becoming terminal
    for _ in range(3):
        s.transition(r.run_id, R.UPLOADING)
        s.transition(r.run_id, R.UPLOAD_PENDING, detail="NAS unreachable")
    assert s.get(r.run_id).state == R.UPLOAD_PENDING
    assert R.UPLOAD_PENDING not in R.TERMINAL


# --------------------------------------------------------------------------- #
# scheduler
# --------------------------------------------------------------------------- #
def t_start_on_time(tmp):
    s = mkstore(tmp); fake = FakeAllego()
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    r = mkrun(s, start=iso(now - timedelta(seconds=5)))
    sch.tick(now)
    r = s.get(r.run_id)
    assert r.state == R.RECORDING, r.state
    assert r.base_name and fake.starts == 1


def t_missed_start_fails_loudly(tmp):
    s = mkstore(tmp); fake = FakeAllego()
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    r = mkrun(s, start=iso(now - timedelta(hours=3)))
    sch.tick(now)
    r = s.get(r.run_id)
    assert r.state == "FAILED_START", r.state
    assert "grace" in (r.error or "").lower()
    assert fake.starts == 0, "a badly-late run must NOT quietly start"


def t_second_run_blocked(tmp):
    s = mkstore(tmp); fake = FakeAllego()
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    a = mkrun(s, owner="andrea", start=iso(now - timedelta(seconds=5)))
    b = mkrun(s, owner="diane", start=iso(now - timedelta(seconds=4)))
    sch.tick(now)
    a, b = s.get(a.run_id), s.get(b.run_id)
    started = [x for x in (a, b) if x.state == R.RECORDING]
    blocked = [x for x in (a, b) if x.state == "FAILED_START"]
    assert len(started) == 1 and len(blocked) == 1, (a.state, b.state)
    assert "global" in (blocked[0].error or "").lower()
    assert fake.starts == 1


def t_stop_fires_even_when_late(tmp):
    s = mkstore(tmp); fake = FakeAllego()
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    r = mkrun(s, start=iso(now - timedelta(seconds=5)),
              stop=iso(now - timedelta(hours=6)))
    sch.tick(now)                       # starts
    sch.tick(now)                       # stop is 6 h late and must STILL fire
    r = s.get(r.run_id)
    assert r.state == R.STOPPED, r.state
    assert fake.stops == 1
    assert r.results.get("stop_late_s", 0) > 3600


def t_scheduled_stop_hands_off_to_postprocessing(tmp):
    """A SCHEDULED stop must enqueue the run, exactly like a manual one.

    THE TEST THAT WAS MISSING. The worker only ever learned about a run from the
    HTTP stop endpoint, so an unattended scheduled stop halted the rig and then
    stranded the run at STOPPED -- no QC, no strip, no upload -- until the
    service happened to restart. Found on the first scheduled run on the real
    rig, 2026-09-13. Every stop path must go through on_stopped.
    """
    s = mkstore(tmp); fake = FakeAllego()
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing
    handed: list[str] = []
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None,
                      on_stopped=handed.append)
    now = datetime.now().astimezone()
    r = mkrun(s, start=iso(now - timedelta(seconds=5)),
              stop=iso(now - timedelta(seconds=1)))
    sch.tick(now)          # start
    sch.tick(now)          # scheduled stop
    assert s.get(r.run_id).state == R.STOPPED, s.get(r.run_id).state
    assert handed == [r.run_id], f"scheduled stop did not hand off: {handed}"

    # and the manual path must hand off through the same callback
    handed.clear()
    r2 = mkrun(s)
    sch.start_now(r2.run_id)
    sch.stop_now(r2.run_id)
    assert handed == [r2.run_id], f"manual stop did not hand off: {handed}"


def t_start_failure_is_recorded(tmp):
    s = mkstore(tmp); fake = FakeAllego(); fake.fail_start = True
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    r = mkrun(s, start=iso(now - timedelta(seconds=5)))
    sch.tick(now)
    r = s.get(r.run_id)
    assert r.state == "FAILED_START", r.state
    assert "preflight" in (r.error or "").lower()


# --------------------------------------------------------------------------- #
# refusals
# --------------------------------------------------------------------------- #
def refusals(tmp):
    s = mkstore(tmp)
    expect("refuse: run with no mouse in any slot",
           lambda: s.create(owner="andrea", preset="p",
                            slots={"A1": {"mouse_id": "", "recording_type": "basal"}},
                            keep_labels=["A/1"]),
           R.RunError, "occupied")
    expect("refuse: run with nothing to keep",
           lambda: s.create(owner="andrea", preset="p",
                            slots={"A1": {"mouse_id": "M1"}}, keep_labels=[]),
           R.RunError, "strip to nothing")

    r = mkrun(s)
    expect("refuse: DRAFT -> RECORDING (skips STARTING)",
           lambda: s.transition(r.run_id, R.RECORDING),
           R.IllegalTransition, "not a legal transition")
    expect("refuse: DRAFT -> DONE",
           lambda: s.transition(r.run_id, R.DONE),
           R.IllegalTransition)
    s.transition(r.run_id, R.SCHEDULED); s.transition(r.run_id, R.STARTING)
    s.transition(r.run_id, R.RECORDING)
    expect("refuse: RECORDING -> DONE without stopping",
           lambda: s.transition(r.run_id, R.DONE), R.IllegalTransition)
    expect("refuse: unknown run id",
           lambda: s.get("nope"), R.RunError, "no such run")

    done = mkrun(s)
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED,
               R.QC, R.STRIPPING, R.STRIPPED, R.UPLOAD_PENDING, R.UPLOADING, R.DONE):
        s.transition(done.run_id, st)
    expect("refuse: anything out of DONE (terminal)",
           lambda: s.transition(done.run_id, R.RECORDING), R.IllegalTransition)

    fake = FakeAllego()
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    expect("refuse: start_now while another run owns the rig",
           lambda: sch.start_now(mkrun(s).run_id), R.RunError, "owns the rig")
    expect("refuse: stop_now on a run that is not recording",
           lambda: sch.stop_now(done.run_id), R.RunError, "not recording")

    # The growth-window guard. Imported fresh under a private name so the
    # monkeypatched module globals above are not disturbed.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_allego_pristine", Path(__file__).resolve().parent / "allego.py")
    pristine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pristine)
    expect("refuse: growth window shorter than the 30 s size flush",
           lambda: pristine.confirm_growing("/tmp/nope", window_s=11.0,
                                            progress=None),
           ValueError, "size-flush")


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="runs-test-")
    print("RUNS + SCHEDULER")
    for fn in (t_create_and_states, t_legal_transition_path, t_results_accumulate,
               t_active_is_single, t_rewind_in_flight,
               t_upload_pending_is_a_resting_state,
               t_retry_targets_are_legal, t_qc_override_is_per_run_not_global,
               t_start_on_time, t_missed_start_fails_loudly, t_second_run_blocked,
               t_stop_fires_even_when_late, t_start_failure_is_recorded,
               t_scheduled_stop_hands_off_to_postprocessing):
        d = tempfile.mkdtemp(dir=tmp)
        check(fn.__name__, lambda fn=fn, d=d: fn(d))
    print("\nMUST REFUSE")
    refusals(tempfile.mkdtemp(dir=tmp))
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

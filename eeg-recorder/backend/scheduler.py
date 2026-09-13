#!/usr/bin/env python3
"""scheduler.py -- fire a run's start and stop at absolute wall-clock instants.

DESIGN, AND THE FAILURE IT IS BUILT AROUND

    A schedule is stored as two ABSOLUTE INSTANTS, not as a delay. A delay is
    lost the moment the process dies; an instant survives a restart, a reboot,
    and a person closing the laptop the service was started from. On boot the
    scheduler re-reads every SCHEDULED run and re-arms it, so "I set it up
    yesterday and the machine rebooted overnight" is not a silent loss.

    A MISSED START IS REPORTED, NEVER SILENTLY SKIPPED. If the service was down
    across the instant, the run does not quietly begin late -- a sleep experiment
    that starts three hours after ZT0 is not the experiment anyone designed, and
    an unexplained "it's recording now" is worse than a clear failure. Past the
    grace window the run goes to FAILED_START with the reason, and a human
    decides. Within the grace window it starts, and the lateness is recorded.

    A MISSED STOP IS DIFFERENT AND JUST STOPS. Stopping late costs nothing but a
    slightly longer file; leaving the amplifiers running costs disk at 90 GB/day
    and can silently eat the next person's slot. So a stop is always honoured,
    however late, and the overrun is recorded.

    ONE RUN OWNS THE RIG. Recording is global on this box, so the scheduler
    refuses to start a run while another is STARTING/RECORDING/STOPPING. Two
    concurrent runs would put two people's animals in one file with nothing
    saying whose is whose.

    CONFIGURATION IS EARLY, THE START IS ON TIME. `allego.start()` sets the path
    and turns streaming on ahead of the instant so the amplifiers are settled,
    which is what `qc/start_recording_at.py` does and why it does it.

    GROWTH IS CONFIRMED LATE, NOT AT THE START. The .xdat size does not move for
    ~30 s after a healthy start (measured 2026-09-11), so the scheduler marks a
    run RECORDING as soon as the file exists and the mode is R_ON, then confirms
    growth in the background once the flush interval has passed. Checking sooner
    reports a working rig as broken.
"""
from __future__ import annotations

import threading
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import allego
import runs as R

# How late a start may be and still be honoured. Past this, the run FAILS rather
# than beginning at the wrong time.
START_GRACE_S = 180.0

TICK_S = 5.0


def parse_instant(s: str) -> datetime:
    """Accept an ISO instant; treat a naive one as LOCAL time.

    Local, deliberately: people schedule against the light cycle
    (09:00 ON / 21:00 OFF KST, ZT0 = 09:00), and asking a biologist to convert
    ZT0 into UTC at setup time is how a run ends up twelve hours out.
    """
    s = str(s).strip().replace("Z", "+00:00")
    d = datetime.fromisoformat(s)
    return d.astimezone() if d.tzinfo is None else d


def _now() -> datetime:
    return datetime.now().astimezone()


class Scheduler:
    """One background thread. Start it once; it re-arms itself from the store."""

    def __init__(self, store: R.RunStore, *, dest_dir: str | Path,
                 on_event: Callable[[str], None] | None = None,
                 on_stopped: Callable[[str], None] | None = None,
                 min_free_gb: float = 150.0):
        self.store = store
        self.dest_dir = Path(dest_dir)
        self.min_free_gb = min_free_gb
        self.log = on_event or (lambda m: print(f"[scheduler] {m}", flush=True))
        # Called with a run_id once a recording has stopped, by EITHER path.
        # Without this a scheduled stop halts the rig and then strands the run at
        # STOPPED forever: the post-processing worker only ever learned about a
        # run from the HTTP stop endpoint, so an unattended stop never reached QC,
        # strip or upload until the service happened to restart. Found on the
        # first scheduled run on the real rig, 2026-09-13, which is what a bench
        # test is for.
        self.on_stopped = on_stopped or (lambda _run_id: None)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._confirming: set[str] = set()

    # ---- lifecycle ------------------------------------------------------ #
    def start(self) -> None:
        moved = self.store.rewind_in_flight()
        if moved:
            self.log(f"rewound {len(moved)} in-flight run(s) after restart: "
                     f"{', '.join(moved)}")
        self._thread = threading.Thread(target=self._loop, name="scheduler",
                                        daemon=True)
        self._thread.start()
        self.log(f"armed; destination {self.dest_dir}")

    def stop(self, timeout: float = 5.0) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout)

    # ---- the loop ------------------------------------------------------- #
    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.tick()
            except Exception:
                self.log("tick raised:\n" + traceback.format_exc())
            self._stop.wait(TICK_S)

    def tick(self, now: datetime | None = None) -> None:
        """One pass. Separated from the loop so tests can drive it directly."""
        now = now or _now()
        self._tick_stops(now)
        self._tick_starts(now)

    # ---- stops come first: freeing the rig can let a start proceed ------- #
    def _tick_stops(self, now: datetime) -> None:
        for run in self.store.list(states=(R.RECORDING,), limit=10):
            if not run.scheduled_stop:
                continue
            due = parse_instant(run.scheduled_stop)
            if now < due:
                continue
            late = (now - due).total_seconds()
            self.log(f"{run.run_id}: stop due {due:%Y-%m-%d %H:%M:%S}"
                     + (f" (late by {late:.0f} s)" if late > 5 else ""))
            self.store.transition(run.run_id, R.STOPPING,
                                  detail=f"scheduled stop, late by {late:.0f}s")
            try:
                res = allego.stop()
                self.store.transition(
                    run.run_id, R.STOPPED,
                    detail=f"stopped ({res['before']} -> {res['after']})",
                    actual_stop=R.utcnow(),
                    results={"stop": res, "stop_late_s": round(late, 1)})
                self.log(f"{run.run_id}: STOPPED")
                self.on_stopped(run.run_id)      # hand to QC -> strip -> upload
            except Exception as exc:
                self.store.fail(run.run_id, "STOP", f"{type(exc).__name__}: {exc}")
                self.log(f"{run.run_id}: STOP FAILED -- {exc}. The rig may still "
                         "be recording; this needs a human.")

    # ---- starts --------------------------------------------------------- #
    def _tick_starts(self, now: datetime) -> None:
        due_runs = []
        for run in self.store.list(states=(R.SCHEDULED,), limit=50):
            if not run.scheduled_start:
                continue
            if now >= parse_instant(run.scheduled_start):
                due_runs.append(run)
        if not due_runs:
            return

        active = self.store.active()
        for run in sorted(due_runs, key=lambda r: r.scheduled_start or ""):
            due = parse_instant(run.scheduled_start)
            late = (now - due).total_seconds()

            if late > START_GRACE_S:
                reason = (
                    f"scheduled start was {due:%Y-%m-%d %H:%M:%S} and it is now "
                    f"{now:%Y-%m-%d %H:%M:%S} -- {late / 60:.0f} min late, past the "
                    f"{START_GRACE_S / 60:.0f} min grace. NOT started: beginning a "
                    "sleep recording at the wrong point in the light cycle is not "
                    "the experiment that was designed. Re-schedule it deliberately.")
                self.store.fail(run.run_id, "START", reason)
                self.log(f"{run.run_id}: MISSED -- {reason}")
                continue

            if active is not None:
                reason = (f"run {active.run_id} ({active.owner}) is already using "
                          f"the rig in state {active.state}. Recording is global on "
                          "this box, so two runs cannot overlap.")
                self.store.fail(run.run_id, "START", reason)
                self.log(f"{run.run_id}: BLOCKED -- {reason}")
                continue

            self._start_run(run, late)
            active = self.store.active()

    def _start_run(self, run: R.Run, late: float) -> None:
        self.log(f"{run.run_id}: starting ({run.owner}, {len(run.occupied)} mice)")
        self.store.transition(run.run_id, R.STARTING,
                              detail=f"late by {late:.0f}s")
        try:
            info = allego.start(run.dest_dir or self.dest_dir,
                                settle_s=3.0, min_free_gb=self.min_free_gb,
                                progress=lambda m: self.log(f"  {m}"))
        except Exception as exc:
            self.store.fail(run.run_id, "START", f"{type(exc).__name__}: {exc}")
            self.log(f"{run.run_id}: START FAILED -- {exc}")
            return
        self.store.transition(
            run.run_id, R.RECORDING, detail=f"file {info['base_name']}",
            actual_start=R.utcnow(), base_name=info["base_name"],
            base_path=info["base_path"], data_path=info["data_path"],
            dest_dir=info["dest"], results={"start_late_s": round(late, 1)})
        self.log(f"{run.run_id}: RECORDING -> {info['base_name']}")
        self._confirm_later(run.run_id, info["data_path"])

    # ---- growth confirmation, after the ~30 s flush ---------------------- #
    def _confirm_later(self, run_id: str, data_path: str) -> None:
        """Confirm bytes are landing, in the background.

        Deliberately NOT inline: the size does not move for ~30 s after a healthy
        start, so a check here would block the scheduler and then lie.
        """
        if run_id in self._confirming:
            return
        self._confirming.add(run_id)

        def work():
            try:
                res = allego.confirm_growing(data_path, progress=lambda m: None)
                run = self.store.get(run_id)
                if run.state != R.RECORDING:
                    return                      # stopped before we could confirm
                self.store.transition(run_id, R.RECORDING,
                                      detail=("growth confirmed" if res["growing"]
                                              else "NOT GROWING"),
                                      results={"growth": res})
                if res["growing"]:
                    self.log(f"{run_id}: growth confirmed, {res['gb_per_h']} GB/h")
                else:
                    self.log(f"{run_id}: 🔴 R_ON but NOT GROWING after "
                             f"{res['window_s']:.0f} s -- needs a human")
            except Exception as exc:
                self.log(f"{run_id}: growth check raised {exc}")
            finally:
                self._confirming.discard(run_id)

        threading.Thread(target=work, name=f"confirm-{run_id}", daemon=True).start()

    # ---- manual paths --------------------------------------------------- #
    def start_now(self, run_id: str) -> R.Run:
        run = self.store.get(run_id)
        if run.state not in (R.DRAFT, R.SCHEDULED):
            raise R.RunError(f"run {run_id} is {run.state}, not startable")
        active = self.store.active()
        if active is not None:
            raise R.RunError(
                f"run {active.run_id} ({active.owner}) already owns the rig "
                f"({active.state}); recording is global on this box")
        if run.state == R.DRAFT:
            self.store.transition(run_id, R.SCHEDULED,
                                  detail="started manually",
                                  scheduled_start=R.utcnow())
        self._start_run(self.store.get(run_id), 0.0)
        return self.store.get(run_id)

    def stop_now(self, run_id: str) -> R.Run:
        run = self.store.get(run_id)
        if run.state != R.RECORDING:
            raise R.RunError(f"run {run_id} is {run.state}, not recording")
        self.store.transition(run_id, R.STOPPING, detail="stopped manually")
        try:
            res = allego.stop()
        except Exception as exc:
            self.store.fail(run_id, "STOP", f"{type(exc).__name__}: {exc}")
            raise
        out = self.store.transition(run_id, R.STOPPED, detail="stopped manually",
                                    actual_stop=R.utcnow(), results={"stop": res})
        self.on_stopped(run_id)                  # same handoff as the scheduled path
        return out

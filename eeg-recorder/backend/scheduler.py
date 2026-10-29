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

    ONE RUN PER PORT, NOT PER RIG (since 2026-10-28). Until then recording was
    global (radiens 4.0.0) and ONE RUN OWNED THE RIG: two concurrent runs would
    have put two people's animals in one file. On 2026-10-28, on Allego 4.1.2,
    ports A and B recorded concurrently into separate files and stopping A froze
    A's file while B kept growing. So a run starts if none of ITS ports is used
    by another STARTING/RECORDING/STOPPING run, and a stop stops only that run's
    ports. Overlapping bookings are refused at creation (app.py, HTTP 409); the
    check here is the last line for anything that got past that.

    THE RIG LOCK. Impedance and restart need the whole rig idle (streaming off),
    and the recording config can only change while no port records, so every
    Allego state change -- a start, a stop, an impedance measurement, a restart
    -- takes `rig_lock`. A start that finds it held WAITS up to RIG_LOCK_WAIT_S
    (longer than an impedance ~31 s or a restart ~25 s, measured 2026-10-28) and
    then FAILS with the holder's reason; it never starts beside a rig-wide
    operation. A stop that cannot get the lock in that time stops anyway: a stop
    is always honoured, and nothing rig-wide can be running while a run records,
    because rig-wide operations refuse unless every run is idle and no start is
    due within RIG_IDLE_LEAD_S.

    CONFIGURATION IS EARLY, THE START IS ON TIME. `allego.start()` sets the path
    and turns streaming on ahead of the instant so the amplifiers are settled,
    which is what `qc/start_recording_at.py` does and why it does it. If another
    port is already recording, streaming is already on and is left alone.

    GROWTH IS CONFIRMED LATE, NOT AT THE START. The .xdat size does not move for
    ~30 s after a healthy start (measured 2026-09-11), so the scheduler marks a
    run RECORDING as soon as each port's file exists and its mode is ON, then
    confirms growth of every port file in the background once the flush interval
    has passed. Checking sooner reports a working rig as broken.

    A MISSING HEADSTAGE WARNS, IT NEVER BLOCKS. A loosened connector can drop a
    port off the SPI bus hours after the run was set up (port B, 2026-10-14
    23:54, found only after the 09:00 start had recorded A and C). At the start
    the live per-port enumeration is compared with the layout's expected
    channels for the occupied slots; a mismatch is recorded on the run
    (results.start_enumeration / start_warning) and pushed to ntfy, and the
    ports that ARE present keep recording. Refusing would lose every other
    animal to save one.
"""
from __future__ import annotations

import subprocess
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import allego
import runs as R

# Same notifier the recording watchdog uses; it reads the ntfy URL itself.
NOTIFY_SH = (Path(__file__).resolve().parents[2]
             / "neurosurveillance" / "deploy" / "nvr-notify.sh")

# How late a start may be and still be honoured. Past this, the run FAILS rather
# than beginning at the wrong time.
START_GRACE_S = 180.0

TICK_S = 5.0

# See THE RIG LOCK above.
RIG_LOCK_WAIT_S = 90.0
RIG_IDLE_LEAD_S = 600.0


class RigBusy(R.RunError):
    """A rig-wide operation was refused because the rig is not idle, or the lock
    is held. Maps to HTTP 409."""


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


def port_mismatch(run: R.Run, ports: dict) -> list[str]:
    """Occupied ports whose live enumeration differs from the layout.

    Only ports that hold an animal count: an empty port is nobody's loss. A run
    without `expected_channels` in its layout (made before layouts existed) is
    not judged.
    """
    expected = (run.layout or {}).get("expected_channels") or {}
    if not expected:
        return []
    out = []
    for port in sorted({slot[0] for slot in run.occupied}):
        want = int(expected.get(port, 0) or 0)
        got = int((ports or {}).get(port, 0) or 0)
        if got != want:
            mice = ", ".join(m for sl, m in run.mice.items() if sl[0] == port)
            out.append(f"port {port} ({mice}): expected {want} channels, "
                       f"Allego enumerates {got}")
    return out


# A booking holds its ports from its start (actual, else scheduled, else now) to
# its scheduled stop; no stop means open-ended. Closes the vault open item
# "refuse overlapping reservations at creation" (2026-10-28). Used by app.py at
# creation and scheduling, and by start_now.
BOOKED = (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING)


def overlap(store: R.RunStore, ports, start_at, stop_at,
            exclude: str | None = None) -> str | None:
    """Why a booking of `ports` over [start_at, stop_at) clashes, or None."""
    now = _now()
    s0 = parse_instant(start_at) if start_at else now
    e0 = parse_instant(stop_at) if stop_at else None
    for r in store.list(states=BOOKED, limit=500):
        shared = sorted(set(ports) & set(r.ports))
        if r.run_id == exclude or not shared:
            continue
        st = r.actual_start or r.scheduled_start
        s1 = parse_instant(st) if st else now
        e1 = parse_instant(r.scheduled_stop) if r.scheduled_stop else None
        if e1 is not None and r.state != R.SCHEDULED:
            e1 = max(e1, now)            # a late stop still holds the port until it happens
        if (e1 is None or s0 < e1) and (e0 is None or s1 < e0):
            return (f"port(s) {', '.join(shared)} are booked by run {r.run_id} "
                    f"({r.owner}, {r.state}) from {s1:%Y-%m-%d %H:%M} to "
                    + (f"{e1:%Y-%m-%d %H:%M}" if e1 else "an open-ended stop")
                    + ". One run per port: pick other ports or another window.")
    return None


def _ntfy(level: str, title: str, body: str) -> None:
    """Fire and forget; a broken notifier must not touch the start path."""
    def work():
        try:
            subprocess.run([str(NOTIFY_SH), level, title, body],
                           capture_output=True, timeout=90)
        except Exception as exc:
            print(f"[scheduler] ntfy failed: {exc}", flush=True)
    threading.Thread(target=work, name="ntfy", daemon=True).start()


class Scheduler:
    """One background thread. Start it once; it re-arms itself from the store."""

    def __init__(self, store: R.RunStore, *, dest_dir: str | Path,
                 on_event: Callable[[str], None] | None = None,
                 on_stopped: Callable[[str], None] | None = None,
                 notify: Callable[[str, str, str], None] | None = None,
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
        self.notify = notify or _ntfy           # (level, title, body)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._confirming: set[str] = set()
        # Shared with app.py's impedance and restart endpoints. `rig_reason` says
        # who holds it, for /api/state rig_busy.
        self.rig_lock = threading.Lock()
        self.rig_reason: str | None = None

    # ---- the rig lock --------------------------------------------------- #
    def rig_busy(self) -> dict:
        return {"busy": self.rig_lock.locked(),
                "reason": self.rig_reason if self.rig_lock.locked() else None}

    def idle_problem(self, now: datetime | None = None) -> str | None:
        """Why a rig-wide operation may not run now, or None."""
        now = now or _now()
        for r in self.store.active_runs():
            return (f"run {r.run_id} ({r.owner}) is {r.state} on port(s) "
                    f"{', '.join(r.ports)}")
        for r in self.store.list(states=(R.SCHEDULED,), limit=50):
            if r.scheduled_start:
                due = parse_instant(r.scheduled_start)
                if (due - now).total_seconds() < RIG_IDLE_LEAD_S \
                        and (now - due).total_seconds() <= START_GRACE_S:
                    return (f"run {r.run_id} ({r.owner}) is scheduled to start at "
                            f"{due:%H:%M:%S}, within {RIG_IDLE_LEAD_S / 60:.0f} min")
        return None

    @contextmanager
    def rig_exclusive(self, reason: str):
        """Hold the rig for a rig-wide operation. Raises RigBusy, never waits:
        a person pressed a button and should hear why at once."""
        if not self.rig_lock.acquire(blocking=False):
            raise RigBusy(f"the rig is busy: {self.rig_reason}")
        try:
            self.rig_reason = reason
            why = self.idle_problem()        # checked UNDER the lock
            if why:
                raise RigBusy(f"the rig is not idle: {why}")
            yield
        finally:
            self.rig_reason = None
            self.rig_lock.release()

    def _locked(self, reason: str) -> bool:
        """Take the lock for a start/stop, waiting at most RIG_LOCK_WAIT_S."""
        if not self.rig_lock.acquire(timeout=RIG_LOCK_WAIT_S):
            return False
        self.rig_reason = reason
        return True

    def _unlock(self) -> None:
        self.rig_reason = None
        self.rig_lock.release()

    # ---- lifecycle ------------------------------------------------------ #
    def start(self) -> None:
        self._adopt_on_boot()
        moved = self.store.rewind_in_flight()
        if moved:
            self.log(f"rewound {len(moved)} in-flight run(s) after restart: "
                     f"{', '.join(moved)}")
        self._thread = threading.Thread(target=self._loop, name="scheduler",
                                        daemon=True)
        self._thread.start()
        self.log(f"armed; destination {self.dest_dir}")

    def _adopt_on_boot(self) -> None:
        """A STARTING run whose ports are really ON is RECORDING, not SCHEDULED.

        If the service died between start_recording() and the RECORDING write,
        rewinding it to SCHEDULED would orphan ports that record for hours with
        no run behind them (no stop, no strip, no upload). So before the rewind,
        read the per-port modes (read-only): ON ports adopt their newest files
        since STARTING was written and the run goes to RECORDING, with an ntfy.
        Anything else rewinds as before.
        """
        starting = self.store.list(states=(R.STARTING,), limit=50)
        if not starting:
            return
        try:
            live = allego.status()
        except Exception as exc:
            live = {"reachable": False, "error": f"{type(exc).__name__}: {exc}"}
        if not live.get("reachable"):
            self.log(f"cannot read Allego at boot ({live.get('error')}); rewinding "
                     f"{len(starting)} STARTING run(s) without checking their ports")
            return
        for run in starting:
            on = [p for p in run.ports
                  if ((live.get("ports") or {}).get(p) or {}).get("recording")]
            if not on:
                continue
            dest = run.dest_dir or str(self.dest_dir)
            since = parse_instant(run.updated_utc).timestamp() - 5
            pf = allego.newest_port_files(dest, on, since)
            lost = [p for p in on if p not in pf]
            if lost:
                msg = (f"port(s) {', '.join(lost)} of run {run.run_id} are ON after a "
                       f"service restart but no new file was found in {dest}; the run "
                       "is rewound and those ports have NO OWNER. Check Allego.")
                self.log(f"{run.run_id}: 🔴 {msg}")
                self.notify("fail", f"EEG run {run.run_id}: recording port with no run", msg)
                continue
            first = pf[on[0]]
            try:
                self.store.transition(
                    run.run_id, R.RECORDING, from_state=R.STARTING,
                    detail=("service restarted while STARTING; port(s) "
                            f"{', '.join(on)} were ON, so adopted their files "
                            "(STARTING -> RECORDING) instead of rewinding"),
                    actual_start=run.updated_utc, base_name=first["base_name"],
                    base_path=first["data_path"][:-len("_data.xdat")],
                    data_path=first["data_path"], port_files=pf, dest_dir=dest,
                    results={"adopted_on_boot": True,
                             "skipped_ports": [p for p in run.ports if p not in on]})
            except R.IllegalTransition:
                continue
            self.log(f"{run.run_id}: adopted after restart, port(s) {', '.join(on)}")
            self.notify("warn", f"EEG run {run.run_id} adopted after a service restart",
                        f"{run.owner}'s run was STARTING when the console restarted; "
                        f"port(s) {', '.join(on)} were recording and are now tracked "
                        "again. Check its files.")
            self._confirm_later(run.run_id, pf)

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
        for run in self.store.list(states=(R.RECORDING,), limit=50):
            if not run.scheduled_stop:
                continue
            due = parse_instant(run.scheduled_stop)
            if now < due:
                continue
            late = (now - due).total_seconds()
            self.log(f"{run.run_id}: stop due {due:%Y-%m-%d %H:%M:%S}"
                     + (f" (late by {late:.0f} s)" if late > 5 else ""))
            try:
                self.store.transition(run.run_id, R.STOPPING, from_state=R.RECORDING,
                                      detail=f"scheduled stop, late by {late:.0f}s")
            except R.IllegalTransition:
                continue                        # stopped meanwhile (Stop pressed): theirs
            try:
                res = self._stop_ports(run)
                self.store.transition(
                    run.run_id, R.STOPPED,
                    detail=f"stopped ({res['before']} -> {res['after']})",
                    actual_stop=R.utcnow(),
                    results={"stop": res, "stop_late_s": round(late, 1)})
                self.log(f"{run.run_id}: STOPPED")
                self.on_stopped(run.run_id)      # hand to QC -> strip -> upload
            except Exception as exc:
                self.store.fail(run.run_id, "STOP", f"{type(exc).__name__}: {exc}")
                self.log(f"{run.run_id}: STOP FAILED -- {exc}. Port(s) "
                         f"{', '.join(run.ports)} may still be recording; this "
                         "needs a human.")

    def _stop_ports(self, run: R.Run) -> dict:
        """Stop ONLY this run's ports. Never `stop_recording()` without a port."""
        got = self._locked(f"stopping run {run.run_id}")
        if not got:
            self.log(f"{run.run_id}: rig lock held by {self.rig_reason!r} for "
                     f"{RIG_LOCK_WAIT_S:.0f} s; stopping anyway")
        try:
            return allego.stop(run.ports)
        finally:
            if got:
                self._unlock()

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

        for run in sorted(due_runs, key=lambda r: parse_instant(r.scheduled_start)):
            due = parse_instant(run.scheduled_start)
            late = (now - due).total_seconds()

            if late > START_GRACE_S:
                reason = (
                    f"scheduled start was {due:%Y-%m-%d %H:%M:%S} and it is now "
                    f"{now:%Y-%m-%d %H:%M:%S} -- {late / 60:.0f} min late, past the "
                    f"{START_GRACE_S / 60:.0f} min grace. NOT started: beginning a "
                    "sleep recording at the wrong point in the light cycle is not "
                    "the experiment that was designed. Re-schedule it deliberately.")
                self._fail_if(run.run_id, R.SCHEDULED, f"MISSED -- {reason}")
                continue

            clash = self._port_clash(run)
            if clash:
                self._fail_if(run.run_id, R.SCHEDULED, clash)
                continue

            self._start_run(run, late)

    def _port_clash(self, run: R.Run) -> str | None:
        """Another active run on any of this run's ports, as a reason, or None."""
        for other in self.store.active_runs():
            shared = sorted(set(other.ports) & set(run.ports))
            if other.run_id != run.run_id and shared:
                return (f"port(s) {', '.join(shared)} are in use by run "
                        f"{other.run_id} ({other.owner}, {other.state}). One run "
                        "per port: two runs cannot record the same port.")
        return None

    def _fail_if(self, run_id: str, from_state: str, reason: str) -> None:
        """FAILED_START, but only if the run is still `from_state`. A run another
        caller already moved on (to STARTING or RECORDING) is not this caller's
        to fail: failing it would mark a recording run FAILED_START while its
        ports keep recording."""
        try:
            self.store.transition(run_id, "FAILED_START", from_state=from_state,
                                  detail=reason, error=reason)
        except R.IllegalTransition:
            return
        self.log(f"{run_id}: START FAILED -- {reason}")

    def _start_run(self, run: R.Run, late: float, *, from_state: str = R.SCHEDULED,
                   **fields) -> None:
        self.log(f"{run.run_id}: starting ({run.owner}, {len(run.occupied)} mice)")
        if not self._locked(f"starting run {run.run_id}"):
            self._fail_if(run.run_id, from_state,
                          f"RigBusy: the rig lock was held by {self.rig_reason!r} for "
                          f"{RIG_LOCK_WAIT_S:.0f} s at the start instant; NOT started")
            return
        try:
            # Re-checked UNDER the lock: two starts (scheduler tick + a manual
            # Start now) can pass their first check at the same moment.
            clash = self._port_clash(run)
            if clash:
                self._fail_if(run.run_id, from_state, clash)
                return
            # Only ONE caller may move it to STARTING. The loser returns without
            # touching the run, so it never fails a run that is recording.
            try:
                self.store.transition(run.run_id, R.STARTING, from_state=from_state,
                                      detail=f"late by {late:.0f}s, port(s) "
                                             f"{', '.join(run.ports)}", **fields)
            except R.IllegalTransition:
                self.log(f"{run.run_id}: already being started elsewhere; skipped")
                return
            try:
                info = allego.start(run.dest_dir or self.dest_dir, run.ports,
                                    settle_s=3.0, min_free_gb=self.min_free_gb,
                                    progress=lambda m: self.log(f"  {m}"))
            except Exception as exc:
                self.store.fail(run.run_id, "START", f"{type(exc).__name__}: {exc}")
                self.log(f"{run.run_id}: START FAILED -- {exc}")
                return
        finally:
            self._unlock()
        # Persisted so postprocess knows these ports have no file on purpose.
        results = {"start_late_s": round(late, 1),
                   "skipped_ports": info.get("skipped_ports") or []}
        missing = []
        if "ports" in info:
            results["start_enumeration"] = info["ports"]
            missing = port_mismatch(run, info["ports"])
            if missing:
                results["start_warning"] = (
                    "started with a port mismatch, recording what is present: "
                    + "; ".join(missing))
        self.store.transition(
            run.run_id, R.RECORDING, detail=f"file {info['base_name']}"
            + (" -- PORT MISMATCH" if missing else ""),
            actual_start=R.utcnow(), base_name=info["base_name"],
            base_path=info["base_path"], data_path=info["data_path"],
            port_files=info.get("port_files") or {},
            dest_dir=info["dest"], results=results)
        self.log(f"{run.run_id}: RECORDING -> {info['base_name']}")
        if missing:
            self.log(f"{run.run_id}: 🔴 {results['start_warning']}")
            self.notify(
                "fail", f"EEG run {run.run_id} started with a headstage missing",
                f"{run.owner}'s run is recording, but: " + "; ".join(missing)
                + ". Those animals are NOT being recorded. The other ports "
                "continue. Check the headstage connector.")
        self._confirm_later(run.run_id, info.get("port_files")
                            or {"".join(run.ports): {"data_path": info["data_path"]}})

    # ---- growth confirmation, after the ~30 s flush ---------------------- #
    def _confirm_later(self, run_id: str, port_files: dict) -> None:
        """Confirm bytes are landing in EVERY port file, in the background.

        Deliberately NOT inline: the size does not move for ~30 s after a healthy
        start, so a check here would block the scheduler and then lie. The port
        files are checked in parallel (one ~40 s window, not one per port), and
        results.growth keeps its old shape -- growing is True only if every port
        grew -- with the per-port detail under growth.ports.
        """
        if run_id in self._confirming:
            return
        self._confirming.add(run_id)

        def work():
            try:
                with ThreadPoolExecutor(max_workers=len(port_files) or 1) as ex:
                    per = dict(zip(port_files, ex.map(
                        lambda f: allego.confirm_growing(f["data_path"],
                                                         progress=lambda m: None),
                        port_files.values())))
                res = {"growing": bool(per) and all(r["growing"] for r in per.values()),
                       "window_s": max((r["window_s"] for r in per.values()), default=0),
                       "gb_per_h": round(sum(r["gb_per_h"] for r in per.values()), 2),
                       "ports": per}
                try:
                    self.store.transition(run_id, R.RECORDING, from_state=R.RECORDING,
                                          detail=("growth confirmed" if res["growing"]
                                                  else "NOT GROWING"),
                                          results={"growth": res})
                except R.IllegalTransition:
                    return                      # stopped before we could confirm
                if res["growing"]:
                    self.log(f"{run_id}: growth confirmed, {res['gb_per_h']} GB/h")
                else:
                    dead = [p for p, r in per.items() if not r["growing"]]
                    self.log(f"{run_id}: 🔴 port(s) {', '.join(dead)} ON but NOT "
                             f"GROWING after {res['window_s']:.0f} s -- needs a human")
                    self.notify("fail", f"EEG run {run_id}: port(s) {', '.join(dead)} "
                                "not growing",
                                f"Allego says ON but no bytes landed in "
                                f"{res['window_s']:.0f} s. The run is not producing "
                                "data on those ports; this needs a person.")
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
        # Starting now books [now, scheduled_stop): it must not run into anyone
        # else's reservation on these ports, active or still to come.
        clash = overlap(self.store, run.ports, None, run.scheduled_stop, exclude=run_id)
        if clash:
            raise R.RunError(clash)
        extra = {"scheduled_start": R.utcnow()} if run.state == R.DRAFT else {}
        self._start_run(run, 0.0, from_state=run.state, **extra)
        return self.store.get(run_id)

    def stop_now(self, run_id: str) -> R.Run:
        run = self.store.get(run_id)
        # A failed stop or recording may still have ports ON: Stop must work on it.
        if run.state not in (R.RECORDING, "FAILED_STOP", "FAILED_RECORDING"):
            raise R.RunError(f"run {run_id} is {run.state}, not recording")
        try:
            self.store.transition(run_id, R.STOPPING, from_state=run.state,
                                  detail="stopped manually")
        except R.IllegalTransition as exc:
            raise R.RunError(f"run {run_id} is already being stopped: {exc}") from exc
        try:
            res = self._stop_ports(run)
        except Exception as exc:
            self.store.fail(run_id, "STOP", f"{type(exc).__name__}: {exc}")
            raise
        out = self.store.transition(run_id, R.STOPPED, detail="stopped manually",
                                    actual_stop=R.utcnow(), results={"stop": res})
        self.on_stopped(run_id)                  # same handoff as the scheduled path
        return out

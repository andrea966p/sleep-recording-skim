#!/usr/bin/env python3
"""runs.py -- the durable record of what the rig was asked to do, and what happened.

A "run" is one press of Record, from the moment a person sets it up to the moment
its stripped copy is verified on the NAS. Because recording on this box is GLOBAL
(one XDAQ, one R_ON for all four ports -- radiens 4.0.0 has no per-port control),
a run owns the WHOLE RIG for its duration, and the per-animal detail it carries is
what makes the single resulting file separable afterwards.

WHY SQLITE AND NOT A JSON FILE
    A 24 h recording outlives any process that started it. The service will be
    restarted, the machine will be rebooted, and a run must survive both and be
    picked up in the right stage. The existing daemon already learned this the
    hard way and settled on WAL + synchronous=FULL in `session_journal.py`; the
    same choices are made here for the same reason.

THE STATE MACHINE

    DRAFT ──► SCHEDULED ──┐
      │                   ├──► STARTING ──► RECORDING ──► STOPPING ──► STOPPED
      └───────────────────┘                                              │
                                                                         ▼
                            DONE ◄── UPLOADING ◄── UPLOAD_PENDING ◄── STRIPPED ◄── STRIPPING ◄── QC

    Any stage can go to FAILED_<stage>, and DRAFT/SCHEDULED can be ABORTED.

    UPLOAD_PENDING IS A RESTING STATE, NOT AN ERROR. If the NAS is unreachable --
    unmounted, wrong password, someone unplugged the office switch -- finished runs
    accumulate there and drain in order when it comes back. That turns a NAS outage
    into a delay instead of a data-handling incident, and it is the difference
    between "the upload failed" and "the data is gone".

    Transitions are CHECKED. An illegal one raises rather than being recorded,
    because a state machine that accepts anything is just a mutable string.

WHAT A RUN CARRIES
    Rig positions are the unit of meaning: A1..D2 for the two eight-mouse presets,
    A..D for the unipolar one. Each occupied slot has a mouse id and a recording
    type. `keep_labels` is frozen AT SETUP TIME, in site labels rather than file
    indices, so what gets stripped is what the person agreed to before they left
    the room -- not whatever a preset file says a month later.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

STATE_DIR = Path(os.environ.get(
    "EEG_RECORDER_STATE", Path.home() / ".local" / "state" / "eeg-recorder"))
DB_PATH = STATE_DIR / "runs.db"

DRAFT = "DRAFT"
SCHEDULED = "SCHEDULED"
STARTING = "STARTING"
RECORDING = "RECORDING"
STOPPING = "STOPPING"
STOPPED = "STOPPED"
QC = "QC"
STRIPPING = "STRIPPING"
STRIPPED = "STRIPPED"
UPLOAD_PENDING = "UPLOAD_PENDING"
UPLOADING = "UPLOADING"
DONE = "DONE"
ABORTED = "ABORTED"

# Stages a restart can safely re-enter, and where it should resume from.
# STARTING/STOPPING/STRIPPING/UPLOADING are "in flight": nobody is driving them
# after a restart, so they are rewound to the last stable state rather than left
# looking active forever.
REWIND_ON_BOOT = {STARTING: SCHEDULED, STOPPING: RECORDING,
                  STRIPPING: QC, UPLOADING: UPLOAD_PENDING}

LEGAL = {
    DRAFT: {SCHEDULED, STARTING, ABORTED},
    SCHEDULED: {STARTING, ABORTED, DRAFT},
    STARTING: {RECORDING, "FAILED_START", SCHEDULED},
    RECORDING: {STOPPING, "FAILED_RECORDING"},
    STOPPING: {STOPPED, "FAILED_STOP", RECORDING},
    STOPPED: {QC, STRIPPING, "FAILED_QC"},
    QC: {STRIPPING, "FAILED_QC"},
    STRIPPING: {STRIPPED, "FAILED_STRIP", QC},
    STRIPPED: {UPLOAD_PENDING},
    UPLOAD_PENDING: {UPLOADING, "FAILED_UPLOAD"},
    UPLOADING: {DONE, UPLOAD_PENDING, "FAILED_UPLOAD"},
    DONE: set(),
    ABORTED: set(),
}
TERMINAL = {DONE, ABORTED}


def _failed(stage: str) -> str:
    return f"FAILED_{stage}"


# every FAILED_* may be retried back into its own stage
for _s in (STARTING, RECORDING, STOPPING, QC, STRIPPING, UPLOADING):
    LEGAL.setdefault(_failed(_s.replace("ING", "")), set())
LEGAL["FAILED_START"] = {SCHEDULED, DRAFT, ABORTED}
LEGAL["FAILED_RECORDING"] = {STOPPING, STOPPED, ABORTED}
LEGAL["FAILED_STOP"] = {STOPPING, STOPPED, ABORTED}
LEGAL["FAILED_QC"] = {QC, STRIPPING, ABORTED}
LEGAL["FAILED_STRIP"] = {STRIPPING, ABORTED}
LEGAL["FAILED_UPLOAD"] = {UPLOAD_PENDING, UPLOADING, ABORTED}


class RunError(RuntimeError):
    pass


class IllegalTransition(RunError):
    pass


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id           TEXT PRIMARY KEY,
    state            TEXT NOT NULL,
    owner            TEXT NOT NULL,
    preset           TEXT NOT NULL,
    created_utc      TEXT NOT NULL,
    updated_utc      TEXT NOT NULL,
    scheduled_start  TEXT,
    scheduled_stop   TEXT,
    actual_start     TEXT,
    actual_stop      TEXT,
    base_name        TEXT,
    base_path        TEXT,
    data_path        TEXT,
    dest_dir         TEXT,
    slots_json       TEXT NOT NULL,
    keep_labels_json TEXT NOT NULL,
    with_gpio        INTEGER NOT NULL DEFAULT 0,
    note             TEXT,
    results_json     TEXT NOT NULL DEFAULT '{}',
    error            TEXT
);
CREATE INDEX IF NOT EXISTS runs_state ON runs(state);
CREATE INDEX IF NOT EXISTS runs_sched ON runs(scheduled_start);

CREATE TABLE IF NOT EXISTS events (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id    TEXT NOT NULL,
    utc       TEXT NOT NULL,
    from_state TEXT,
    to_state  TEXT,
    detail    TEXT
);
CREATE INDEX IF NOT EXISTS events_run ON events(run_id);
"""


@dataclass
class Run:
    run_id: str
    state: str
    owner: str
    preset: str
    created_utc: str
    updated_utc: str
    slots: dict                      # slot -> {mouse_id, recording_type}
    keep_labels: list
    with_gpio: bool = False
    scheduled_start: str | None = None
    scheduled_stop: str | None = None
    actual_start: str | None = None
    actual_stop: str | None = None
    base_name: str | None = None
    base_path: str | None = None
    data_path: str | None = None
    dest_dir: str | None = None
    note: str | None = None
    results: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def occupied(self) -> list[str]:
        return [s for s, v in self.slots.items() if v.get("mouse_id")]

    @property
    def mice(self) -> dict:
        return {s: v["mouse_id"] for s, v in self.slots.items() if v.get("mouse_id")}

    def to_dict(self) -> dict:
        d = asdict(self)
        d["occupied"] = self.occupied
        return d


class RunStore:
    """Every read and write of run state. Thread-safe; the scheduler and the API
    both touch it."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else DB_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        with self._conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def _conn(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            c = sqlite3.connect(self.path, timeout=30, isolation_level=None)
            try:
                c.row_factory = sqlite3.Row
                # WAL so a reader never blocks the scheduler; synchronous=FULL
                # because a run record that survives the process but not a power
                # cut is not durable in the way a 24 h recording needs.
                c.execute("PRAGMA journal_mode=WAL")
                c.execute("PRAGMA synchronous=FULL")
                c.execute("BEGIN")
                yield c
                # executescript() commits implicitly, so the transaction we opened
                # may already be gone by now; committing again raises "no
                # transaction is active". Ask rather than assume.
                if c.in_transaction:
                    c.execute("COMMIT")
            except Exception:
                try:
                    if c.in_transaction:
                        c.execute("ROLLBACK")
                except Exception:
                    pass
                raise
            finally:
                c.close()

    # ---- reads ---------------------------------------------------------- #
    @staticmethod
    def _row(r: sqlite3.Row) -> Run:
        return Run(
            run_id=r["run_id"], state=r["state"], owner=r["owner"],
            preset=r["preset"], created_utc=r["created_utc"],
            updated_utc=r["updated_utc"],
            slots=json.loads(r["slots_json"]),
            keep_labels=json.loads(r["keep_labels_json"]),
            with_gpio=bool(r["with_gpio"]),
            scheduled_start=r["scheduled_start"], scheduled_stop=r["scheduled_stop"],
            actual_start=r["actual_start"], actual_stop=r["actual_stop"],
            base_name=r["base_name"], base_path=r["base_path"],
            data_path=r["data_path"], dest_dir=r["dest_dir"], note=r["note"],
            results=json.loads(r["results_json"] or "{}"), error=r["error"])

    def get(self, run_id: str) -> Run:
        with self._conn() as c:
            r = c.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not r:
            raise RunError(f"no such run: {run_id}")
        return self._row(r)

    def list(self, *, states: Iterable[str] | None = None, limit: int = 100) -> list[Run]:
        q = "SELECT * FROM runs"
        args: list = []
        if states:
            states = list(states)
            q += f" WHERE state IN ({','.join('?' * len(states))})"
            args += states
        q += " ORDER BY created_utc DESC LIMIT ?"
        args.append(int(limit))
        with self._conn() as c:
            rows = c.execute(q, args).fetchall()
        return [self._row(r) for r in rows]

    def active(self) -> Run | None:
        """The run that owns the rig right now, if any.

        At most one: recording is global, so a second concurrent run is not a
        scheduling inconvenience, it is two people's data in one file with no
        record of whose is whose.
        """
        for r in self.list(states=(STARTING, RECORDING, STOPPING), limit=5):
            return r
        return None

    def events(self, run_id: str, limit: int = 200) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT utc, from_state, to_state, detail FROM events "
                "WHERE run_id=? ORDER BY id ASC LIMIT ?", (run_id, limit)).fetchall()
        return [dict(r) for r in rows]

    # ---- writes --------------------------------------------------------- #
    def create(self, *, owner: str, preset: str, slots: dict, keep_labels: list,
               with_gpio: bool = False, scheduled_start: str | None = None,
               scheduled_stop: str | None = None, note: str | None = None,
               dest_dir: str | None = None) -> Run:
        if not any(v.get("mouse_id") for v in slots.values()):
            raise RunError(
                "a run with no occupied slot records nothing about which animal "
                "is which, and its file could never be attributed afterwards")
        if not keep_labels:
            raise RunError("a run with no channels to keep would strip to nothing")
        run_id = uuid.uuid4().hex[:12]
        now = utcnow()
        state = SCHEDULED if scheduled_start else DRAFT
        with self._conn() as c:
            c.execute(
                "INSERT INTO runs (run_id,state,owner,preset,created_utc,updated_utc,"
                "scheduled_start,scheduled_stop,slots_json,keep_labels_json,with_gpio,"
                "note,dest_dir,results_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'{}')",
                (run_id, state, owner, preset, now, now, scheduled_start,
                 scheduled_stop, json.dumps(slots), json.dumps(keep_labels),
                 int(with_gpio), note, dest_dir))
            c.execute("INSERT INTO events (run_id,utc,from_state,to_state,detail) "
                      "VALUES (?,?,?,?,?)",
                      (run_id, now, None, state, f"created by {owner}"))
        return self.get(run_id)

    def transition(self, run_id: str, to_state: str, *, detail: str = "",
                   **fields) -> Run:
        """Move a run to a new state, refusing illegal moves.

        `fields` updates columns in the same transaction, so a state and the
        facts that justify it can never disagree.
        """
        with self._conn() as c:
            row = c.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                raise RunError(f"no such run: {run_id}")
            frm = row["state"]
            allowed = LEGAL.get(frm, set())
            # A FAILURE may be recorded from ANY non-terminal state. A start can
            # fail while still SCHEDULED (missed its instant, or another run owns
            # the rig) and an upload can fail while UPLOAD_PENDING; refusing to
            # record that would force the caller either to lie about the state or
            # to swallow the failure. Only FORWARD progress is strict.
            if to_state.startswith("FAILED_") and frm not in TERMINAL:
                allowed = allowed | {to_state}
            if to_state != frm and to_state not in allowed:
                raise IllegalTransition(
                    f"run {run_id}: {frm} -> {to_state} is not a legal transition; "
                    f"from {frm} you may go to {sorted(allowed) or 'nowhere'}")
            now = utcnow()
            sets, args = ["state=?", "updated_utc=?"], [to_state, now]
            for k, v in fields.items():
                if k == "results":
                    prev = json.loads(row["results_json"] or "{}")
                    prev.update(v)
                    sets.append("results_json=?")
                    args.append(json.dumps(prev))
                elif k in ("slots", "keep_labels"):
                    sets.append(f"{k}_json=?")
                    args.append(json.dumps(v))
                else:
                    sets.append(f"{k}=?")
                    args.append(v)
            args.append(run_id)
            c.execute(f"UPDATE runs SET {','.join(sets)} WHERE run_id=?", args)
            c.execute("INSERT INTO events (run_id,utc,from_state,to_state,detail) "
                      "VALUES (?,?,?,?,?)", (run_id, now, frm, to_state, detail))
        return self.get(run_id)

    def fail(self, run_id: str, stage: str, reason: str) -> Run:
        return self.transition(run_id, _failed(stage), detail=reason, error=reason)

    def rewind_in_flight(self) -> list[str]:
        """Called once at startup. Nothing is driving an in-flight run after a
        restart, so rewind it to the last state a human or the scheduler can act
        on. Returns the run ids that moved."""
        moved = []
        for state, back in REWIND_ON_BOOT.items():
            for r in self.list(states=(state,), limit=50):
                self.transition(
                    r.run_id, back,
                    detail=f"service restarted while {state}; rewound to {back}")
                moved.append(r.run_id)
        return moved


if __name__ == "__main__":
    s = RunStore()
    print(f"db: {s.path}")
    for r in s.list(limit=20):
        print(f"  {r.run_id}  {r.state:16s} {r.owner:8s} {r.preset:18s} "
              f"{len(r.occupied)} mice  {r.created_utc}")

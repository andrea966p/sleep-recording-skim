#!/usr/bin/env python3
"""Contract for the console's HTTP layer: per-port bookings and rig-wide operations.

Booking a port that another run holds in an overlapping window must be refused
at creation (HTTP 409), not discovered at the start instant; impedance and
restart must be refused (409) unless the whole rig is idle. Allego is faked at
the module boundary, and every path is redirected to a temp dir through the same
env vars the coordinator's second console uses, so nothing touches the rig, the
real state DB or ~/radix/data.

    python3 test_app.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="app-test-"))
os.environ["EEG_RECORDER_STATE"] = str(TMP / "state")
os.environ["EEG_RAW_ROOT"] = str(TMP / "data")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import allego                      # noqa: E402
import app as A                    # noqa: E402
import runs as R                   # noqa: E402

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


RECORDING: set[str] = set()


def fake_status():
    return {"reachable": True, "server_running": True, "system_mode": "XDAQ_CORE_REC",
            "sample_freq": 1000.0, "measured_rate": 1.0, "streaming": "ON",
            "recording": "ON" if RECORDING else "OFF", "split_files_by_port": True,
            "base_path": str(TMP / "data"), "base_name": "allego",
            "recording_type": "CONTINUOUS", "server_version": "5.8.0",
            "ports": {p: {"channels": 64, "recording": p in RECORDING, "run_id": None,
                          "owner": None, "file": None, "bytes": None} for p in "ABCD"},
            "problems": [], "healthy": True, "error": None}


allego.status = fake_status
allego.selected_counts = lambda: {"A": 4}
allego.impedance = lambda port: {"port": port, "measured_utc": "2026-10-28T10:00:00Z",
                                 "duration_s": 30.9,
                                 "channels": [{"ntv_chan_idx": 0, "label": f"{port}/1",
                                               "kohm": 186.0, "phase_deg": -10.0}]}
allego.restart = lambda: {"before": {}, "after": {}, "duration_s": 25.0}
A.nas_upload.nas_status = lambda: {"ok": False}
client = A.app.test_client()


def iso(dt):
    return dt.replace(microsecond=0).isoformat()


def book(slots, start=None, stop=None):
    body = {"owner": "andrea", "batch_name": "TEST", "ignore_layout_mismatch": True,
            "slots": {s: {"mouse_id": m, "recording_type": "basal"} for s, m in slots.items()}}
    if start:
        body["start_at"] = start
    if stop:
        body["stop_at"] = stop
    return client.post("/api/runs", json=body)


NOW = datetime.now().astimezone()
T = lambda h: iso(NOW + timedelta(hours=h))


def t_paths_follow_env():
    assert A.store.path == TMP / "state" / "runs.db", A.store.path
    assert A.IMPEDANCE_DIR == TMP / "state" / "impedance"
    assert A.RAW_ROOT == TMP / "data"


def t_overlapping_booking_is_409():
    r = book({"A1": "M1", "B1": "M2"}, T(1), T(3))
    assert r.status_code == 201, r.get_json()
    run = r.get_json()
    assert run["ports"] == ["A", "B"] and run["port_files"] == {}
    r = book({"B2": "M3"}, T(2), T(4))                   # port B, overlapping
    assert r.status_code == 409 and "port(s) B" in r.get_json()["error"], r.get_json()
    assert book({"C1": "M4"}, T(2), T(4)).status_code == 201, "disjoint ports must book"
    assert book({"A2": "M5"}, T(3), T(5)).status_code == 201, "[start, stop): back-to-back is fine"
    r = book({"D1": "M6"}, T(10))                        # open-ended on D
    assert r.status_code == 201
    r = book({"D2": "M7"}, T(30), T(31))                 # after an open-ended start
    assert r.status_code == 409, "a run with no stop overlaps everything after its start"
    assert book({"D2": "M7"}, T(8), T(9)).status_code == 201, "before it is fine"


def t_reschedule_onto_a_booked_port_is_409():
    r = book({"C2": "M8"})                               # open-ended draft on C, now..
    assert r.status_code == 409, "open-ended from now overlaps C's later booking"
    r = book({"C2": "M8"}, stop=T(0.5))                  # a draft on port C, now..+30 min
    rid = r.get_json()["run_id"]
    r = client.post(f"/api/runs/{rid}/schedule", json={"start_at": T(3), "stop_at": T(5)})
    assert r.status_code == 409 and "port(s) C" in r.get_json()["error"], r.get_json()
    r = client.post(f"/api/runs/{rid}/schedule", json={"start_at": T(50), "stop_at": T(51)})
    assert r.status_code == 200, r.get_json()


def t_state_and_ports_shape():
    d = client.get("/api/state").get_json()
    assert d["active_runs"] == [] and d["active_run"] is None
    assert d["rig_busy"] == {"busy": False, "reason": None}
    assert d["allego"]["ports"]["A"]["channels"] == 64
    d = client.get("/api/ports").get_json()
    a = d["ports"]["A"]
    assert a["next_reservation"]["start"] and a["selected_channels"] == 4, a
    assert d["ports"]["B"]["selected_channels"] == 0
    assert d["recording_config"] == {"base_file_path": str(TMP / "data"),
                                     "base_file_name": "allego",
                                     "split_files_by_port": True,
                                     "recording_type": "CONTINUOUS"}, d["recording_config"]
    assert d["system_mode"] == "XDAQ_CORE_REC" and d["sample_freq"] == 1000.0


def t_active_run_fills_its_ports():
    r = book({"A1": "M9"}, T(100), T(101)).get_json()
    pf = {"A": {"base_name": "allego_portA_0__uid1028-09-00-00",
                "data_path": str(TMP / "data" / "allego_portA_0__uid1028-09-00-00_data.xdat")}}
    Path(pf["A"]["data_path"]).parent.mkdir(parents=True, exist_ok=True)
    Path(pf["A"]["data_path"]).write_bytes(b"x" * 10)
    A.store.transition(r["run_id"], R.STARTING)
    A.store.transition(r["run_id"], R.RECORDING, port_files=pf)
    try:
        d = client.get("/api/state").get_json()
        run = d["active_runs"][0]
        assert run["bytes_on_disk"] == {"A": 10} and d["active_run"]["run_id"] == r["run_id"]
        a = d["allego"]["ports"]["A"]
        assert (a["run_id"], a["file"], a["bytes"]) == (r["run_id"], pf["A"]["base_name"], 10), a
        assert d["allego"]["ports"]["B"]["run_id"] is None
        # rig-wide operations are refused while it records
        for url in ("/api/ports/B/impedance", "/api/allego/restart"):
            resp = client.post(url)
            assert resp.status_code == 409 and r["run_id"] in resp.get_json()["error"], \
                (url, resp.get_json())
    finally:
        A.store.transition(r["run_id"], R.STOPPING)
        A.store.transition(r["run_id"], R.STOPPED)


def t_impedance_saved_and_served():
    # rig idle: nothing active, but bookings within 10 min would refuse; none here
    assert client.get("/api/ports/D/impedance").status_code == 404
    r = client.post("/api/ports/d/impedance")
    assert r.status_code == 200, r.get_json()
    assert r.get_json()["channels"][0]["label"] == "D/1"
    saved = TMP / "state" / "impedance" / "portD.json"
    assert json.loads(saved.read_text())["port"] == "D"
    assert client.get("/api/ports/D/impedance").get_json()["duration_s"] == 30.9
    assert client.post("/api/ports/Z/impedance").status_code == 404
    assert client.post("/api/allego/restart", json={"mode": "SMARTBOX_PRO"}).status_code == 200


def t_impedance_refused_before_a_due_start():
    r = book({"B1": "M10"}, iso(datetime.now().astimezone() + timedelta(minutes=5)),
             iso(datetime.now().astimezone() + timedelta(minutes=6)))
    assert r.status_code == 201, r.get_json()
    resp = client.post("/api/ports/C/impedance")
    assert resp.status_code == 409 and "scheduled to start" in resp.get_json()["error"]


def t_stop_before_start_is_refused():
    """Review fix 8: an inverted window could never overlap anything, so it
    slipped past the 409 check; refuse it at creation."""
    r = book({"C2": "M11"}, T(200), T(199))
    assert r.status_code == 400 and "stop_at must be after" in r.get_json()["error"], r.get_json()
    r = book({"C2": "M11"}, None, T(-1))              # no start = now; stop in the past
    assert r.status_code == 400, r.get_json()


def main() -> int:
    print("APP (fake Allego)")
    for fn in (t_paths_follow_env, t_overlapping_booking_is_409,
               t_reschedule_onto_a_booked_port_is_409, t_state_and_ports_shape,
               t_active_run_fills_its_ports, t_impedance_saved_and_served,
               t_impedance_refused_before_a_due_start, t_stop_before_start_is_refused):
        check(fn.__name__, fn)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

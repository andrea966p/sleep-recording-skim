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

import json
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
    """Per-port, like Allego 4.1.2 (2026-10-28): each port records on its own."""
    def __init__(self):
        self.on: set[str] = set()               # ports recording now
        self.starts = 0
        self.stops = 0
        self.started_ports: list[list[str]] = []
        self.stopped_ports: list[list[str]] = []
        self.fail_start = False
        self.grew = True
        self.dead: set[str] = set()             # port files that do not grow
        self.n = 0
        self.ports = None                       # live enumeration, when set
        self.skipped: list[str] = []            # ports start() reports as skipped

    @property
    def recording(self):
        return bool(self.on)

    def start(self, dest, ports=None, **kw):
        if self.fail_start:
            raise allego.PreflightFailed("fake preflight failure")
        ports = sorted(ports or "ABCD")
        busy = self.on & set(ports)
        if busy:                                # allego.preflight refuses this too
            raise allego.PreflightFailed(f"port {sorted(busy)[0]} is ALREADY recording")
        self.starts += 1
        self.started_ports.append(ports)
        self.on |= set(ports)
        pf = {}
        for p in ports:
            self.n += 1
            name = f"allego_port{p}_{self.n}__uid1028-09-00-00"
            pf[p] = {"base_name": name, "data_path": f"{dest}/{name}_data.xdat"}
        first = pf[ports[0]]
        out = {"port_files": pf, "base_name": first["base_name"],
               "base_path": f"{dest}/{first['base_name']}",
               "data_path": first["data_path"], "mode": "ON",
               "started_at": 0.0, "dest": str(dest)}
        if self.ports is not None:
            out["ports"] = dict(self.ports)
        out["skipped_ports"] = list(self.skipped)
        return out

    def stop(self, ports=None, **kw):
        assert ports, "the scheduler must never stop without naming its ports"
        self.stops += 1
        self.stopped_ports.append(sorted(ports))
        before = {p: "ON" if p in self.on else "OFF" for p in ports}
        self.on -= set(ports)
        return {"ports": sorted(ports), "before": before,
                "after": {p: "OFF" for p in ports}}

    def confirm_growing(self, path, **kw):
        grew = self.grew and not any(f"_port{p}_" in str(path) for p in self.dead)
        return {"growing": grew, "bytes_start": 0,
                "bytes_end": 1 if grew else 0, "window_s": 40.0,
                "gb_per_h": 1.05 if grew else 0.0}


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
               R.QC, R.STRIPPING, R.STRIPPED, R.EXPORTING, R.EXPORTED,
               R.UPLOAD_PENDING, R.UPLOADING, R.DONE):
        r = s.transition(r.run_id, st, detail="walk")
    assert r.state == R.DONE
    ev = s.events(r.run_id)
    assert len(ev) == 14, len(ev)      # create + 13 moves


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
    # and an export cut off by a restart goes back to STRIPPED, whose handler
    # re-runs it -- not left looking active forever
    r2 = mkrun(s)
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED, R.QC,
               R.STRIPPING, R.STRIPPED, R.EXPORTING):
        s.transition(r2.run_id, st)
    s.rewind_in_flight()
    assert s.get(r2.run_id).state == R.STRIPPED, s.get(r2.run_id).state


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


def t_qc_scores_only_occupied_slots(tmp):
    """A four-mouse run must not be graded on eight positions.

    cards/ladder.py defaults to `spec.positions()` -- every slot the LAYOUT has,
    not every slot the OPERATOR filled. Measured 2026-09-13 on the 24 h S-SL run:
    dropping five animals from the manifest still produced eight cards, five of
    them `UNKNOWN@<slot>`, and three of those read PASS at rung 2. A card built
    from an amplifier input with nothing plugged into it, labelled UNKNOWN and
    marked PASS, is exactly the kind of output someone later reads as a real
    animal. So the occupied slots are passed explicitly.
    """
    import postprocess as PP
    s = mkstore(tmp)
    r = mkrun(s, slots={"A1": {"mouse_id": "M1", "recording_type": "basal"},
                        "C2": {"mouse_id": "M2", "recording_type": "basal"},
                        "D1": {"mouse_id": "M3", "recording_type": "basal"}})
    s.transition(r.run_id, R.SCHEDULED)
    r = s.transition(r.run_id, R.STARTING, base_name="allego_9__uidTEST",
                     base_path=str(Path(tmp) / "allego_9__uidTEST"))

    seen = {}
    real_run, real_cache = PP.subprocess.run, PP.qc_cache_path

    class Done:
        returncode = 0
        stdout = stderr = ""

    cache = Path(tmp) / "fake.npz"
    try:
        PP.subprocess.run = lambda cmd, **kw: (seen.update(cmd=cmd),
                                               cache.write_bytes(b"x"), Done())[-1]
        PP.qc_cache_path = lambda base: cache
        ok, detail = PP.compute_qc_bundle(r)
    finally:
        PP.subprocess.run, PP.qc_cache_path = real_run, real_cache

    assert ok, detail
    cmd = seen["cmd"]
    assert "--positions" in cmd, f"ladder invoked without --positions: {cmd}"
    assert cmd[cmd.index("--positions") + 1] == "A1,C2,D1", cmd


def t_qc_none_preset_needs_no_override(tmp):
    """A layout this project cannot judge must not demand a waiver every run.

    `4mice_unipolar_lfp` records /18../23 on 32-channel ports. CohortSpec derives its
    wire-free floor as base+n../16 on a 64-channel chip, so no floor exists for
    those sites and the bundle can never be computed. Until 2026-09-13 the chain
    asked the operator to override the missing-bundle guard on EVERY such run.
    A guard that can never be satisfied is a guard people learn to click past,
    including on the runs where it is load-bearing.

    The two outcomes stay distinguishable in the record: `qc_not_applicable`
    (no criterion exists) is not `qc_bundle_skipped` (a person waived one).
    """
    import postprocess as PP
    s = mkstore(tmp)
    r = s.create(owner="andrea", preset="4mice_unipolar_lfp",
                 slots={"A": {"mouse_id": "M1", "recording_type": "basal"}},
                 keep_labels=["A/18", "A/19"], dest_dir=str(tmp))
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING):
        s.transition(r.run_id, st)
    r = s.transition(r.run_id, R.STOPPED, base_name="allego_9__uidNOBUNDLE")

    w = PP.Worker(s, require_qc_bundle=True, auto_compute_qc=True,
                  on_event=lambda m: None)
    out = w._qc(r)
    assert out.state == R.QC, f"qc:none run stalled at {out.state}"
    assert out.results.get("qc_not_applicable") is True, out.results
    assert not out.results.get("qc_bundle_skipped"), \
        "a layout with no criterion was recorded as a waived guard"

    # and the opposite still refuses: a role-based preset with no bundle, whose
    # auto-computation cannot run here, must NOT walk through this door.
    r2 = mkrun(s)
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING):
        s.transition(r2.run_id, st)
    r2 = s.transition(r2.run_id, R.STOPPED, base_name="allego_8__uidNOBUNDLE")
    w2 = PP.Worker(s, require_qc_bundle=True, auto_compute_qc=False,
                   on_event=lambda m: None)
    held = w2._qc(r2)
    assert held.state == "FAILED_QC", \
        f"a judgeable preset walked through the qc:none door ({held.state})"


def t_empty_gpio_header_lets_the_strip_finish(tmp):
    """Run ee0263bffeaa (2026-10-08) went FAILED_STRIP on 6 single-ms glitches
    on a floating din_1, and the retry could not pass --gpio-never-connected.
    The rig config now says whether the header is wired; absent means wired, so
    Gate B stays enforced unless someone declared otherwise. --with-gpio wins:
    a run that KEEPS the GPIO channels drops nothing for Gate B to judge."""
    import types
    import postprocess as PP
    import presets as P
    import nas_upload as NU
    s = mkstore(tmp)
    r = s.create(owner="andrea", preset="4mice_unipolar_lfp",
                 slots={"A": {"mouse_id": "M1", "recording_type": "basal"}},
                 keep_labels=["A/18", "A/19"], dest_dir=str(tmp))
    r = s.transition(r.run_id, r.state, base_path=str(Path(tmp) / "allego_0__uidX"))

    seen = []

    class Fail:
        returncode, stdout, stderr = 1, "", "fake"

    real = PP.subprocess.run
    try:
        PP.subprocess.run = lambda cmd, **kw: (seen.append(cmd), Fail())[-1]
        for connected, gpio in ((False, False), (True, False), (False, True)):
            r.with_gpio = gpio
            try:
                PP.strip(r, cfg=types.SimpleNamespace(gpio_header_connected=connected))
            except PP.PostprocessError:
                pass
    finally:
        PP.subprocess.run = real
    flags = ["--gpio-never-connected" in c for c in seen]
    assert flags == [True, False, False], flags

    # the config key: absent = connected; a quoted "false" is refused, not guessed
    assert P.load().gpio_header_connected in (True, False)
    base = Path(__file__).resolve().parent.parent / "config" / "users.yaml"
    txt = "\n".join(l for l in base.read_text().splitlines()
                    if not l.startswith(("rig:", "  gpio_header_connected")))
    for val, want in (("", True), ("rig: {gpio_header_connected: false}\n", False)):
        p = Path(tmp) / f"u{want}.yaml"
        p.write_text(txt + "\n" + val)
        assert P.load(p).gpio_header_connected is want, val
    p = Path(tmp) / "quoted.yaml"
    p.write_text(txt + "\nrig: {gpio_header_connected: 'false'}\n")
    try:
        P.load(p)
        raise AssertionError("a quoted 'false' was accepted")
    except P.PresetError:
        pass

    # nas_upload's user list follows the config, not a second hand-kept copy
    keep = NU.USERS
    try:
        NU.set_root(NU.ROOT, ["andrea", "Newperson"])
        assert NU.user_dir("newperson").name == "newperson"
    finally:
        NU.USERS = keep


def _stripped_run(s, tmp, *, slots=None, state=R.STRIPPED, **fields):
    r = s.create(owner="andrea", preset="8mice_eeg_emg",
                 slots=slots or {"A1": {"mouse_id": "HLBSSL31", "recording_type": "recovery"},
                                 "A2": {"mouse_id": "HLBSSL32", "recording_type": "basal"}},
                 keep_labels=["A/1", "A/2", "A/33", "A/34"], batch_name="HLBSSL",
                 dest_dir=str(tmp))
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED, R.QC,
               R.STRIPPING, R.STRIPPED):
        s.transition(r.run_id, st)
    r = s.transition(r.run_id, R.STRIPPED, base_name="allego_0__uid0921-00-17-34",
                     actual_start="2026-09-20T15:17:37Z",
                     layout={"setting": "eeg_emg", "roles": {"eeg": 1, "emg": 2},
                             "headstage": "rhd2216_bipolar"},
                     results={"strip": {"dst_base": str(Path(tmp) / "x")},
                              **fields.pop("results", {})}, **fields)
    if state != R.STRIPPED:
        for st in (R.EXPORTING, R.EXPORTED, R.UPLOAD_PENDING):
            r = s.transition(r.run_id, st)
            if st == state:
                break
    return r


def t_export_spec_maps_each_slot_to_its_own_sites(tmp):
    """The wrong-channel guard on the recorder side: slot 2 is /33, not /3.

    Also: each mouse is filed by ITS OWN recording type, so a mixed run sends one
    animal to Baseline and the other to Recovery -- no joined `BSR-RSR` code.
    """
    import postprocess as PP
    s = mkstore(tmp)
    r = _stripped_run(s, tmp, slots={
        "A1": {"mouse_id": "HLBSSL31", "recording_type": "recovery"},
        "A2": {"mouse_id": "HLBSSL32", "recording_type": "basal"},
        "B": {"mouse_id": "HLBSSL33", "recording_type": "recovery"}})
    spec = PP.export_spec(r)
    got = {m["slot"]: (m["columns"], m["file_base"], m["condition"], m["position"])
           for m in spec["mice"]}
    want = {
        "A1": ({"eeg": "A/1", "emg": "A/2"}, "20260921_HLBSSL31_R", "Recovery", "A1"),
        "A2": ({"eeg": "A/33", "emg": "A/34"}, "20260921_HLBSSL32_B", "Baseline", "A2"),
        "B": ({"eeg": "B/1", "emg": "B/2"}, "20260921_HLBSSL33_R", "Recovery", "B1"),
    }
    assert got == want, f"\n got {got}\nwant {want}"


def t_frozen_mouse_dirs_are_reused_on_retry(tmp):
    """A retried upload goes back into the SAME per-mouse folders.

    The collision rule picks the next free name (`..._R-2`). If it ran on every
    attempt, an interrupted upload would walk into a fresh folder each time and
    scatter partial copies behind it. So the names are resolved once and frozen.
    Also checks: info.json content, and that local CSVs go only once ALL verified.
    """
    import postprocess as PP
    import naming as N
    import presets as P
    s = mkstore(tmp)
    out = Path(tmp) / "pm"; out.mkdir()
    cfg = P.load()
    entries = {}
    rows = []
    spec_mice = []
    for slot, mid, code, cond in (("A1", "HLBSSL31", "recovery", "Recovery"),
                                  ("A2", "HLBSSL32", "basal", "Baseline")):
        e = N.mouse_entry(date_yyyymmdd="20260921", batch="HLBSSL", mouse_id=mid,
                          rtype=code, cfg=cfg, suffix=2 if slot == "A1" else 1)
        entries[slot] = {"slot": slot, "mouse_id": mid, "recording_type": code, **e}
        fb = f"20260921_{mid}_{cfg.type_code(code)}"
        (out / f"{fb}.csv").write_text("timestamp_raw,timestamp_sec,datetime_kst,EEG,EMG\n")
        rows.append({"file_base": fb, "csv": f"{fb}.csv", "roles": ["EEG", "EMG"],
                     "sha256": "abc", "bytes": 49, "verify": {"rows": 0}})
        spec_mice.append({"slot": slot, "position": slot, "mouse_id": mid,
                          "recording_type": code, "condition": cond, "batch": "HLBSSL",
                          "file_base": fb, "columns": {"eeg": "A/1", "emg": "A/2"}})
    (out / "unrelated.csv").write_text("keep me")
    rep = {"samplingRate": 1000.0, "startTime_utc": "2026-09-20T15:17:34.272Z",
           "startTime_kst": "2026-09-21 00:17:34.272", "n_samples": 0, "duration_h": 0,
           "timestamp_raw_first": 1, "timestamp_raw_last": 1, "allego_base": "allego_0__uid0921-00-17-34",
           "stripped_dataset_checksum": "d", "source": {}, "meta": {"run_id": "x"},
           "tool": "t", "version": "v", "git_commit": None, "utc": "u", "mice": rows}
    (out / "r.json").write_text(__import__("json").dumps(rep))
    (out / "spec.json").write_text(__import__("json").dumps({"mice": spec_mice}))
    r = _stripped_run(s, tmp, state=R.UPLOAD_PENDING,
                      results={"export": {"report": str(out / "r.json"), "out_dir": str(out)},
                               "nas_mouse_dirs": entries})

    seen = []
    real = (PP.nas_upload.nas_status, PP.nas_upload.upload_mouse,
            PP.nas_upload.free_mouse_folder, PP.nas_upload.user_dir)

    def boom(*a, **k):
        raise AssertionError("free_mouse_folder called for a run whose folders are frozen")

    try:
        PP.nas_upload.nas_status = lambda: {"ok": True}
        PP.nas_upload.free_mouse_folder = boom
        PP.nas_upload.user_dir = lambda u: Path(tmp) / "nas" / u
        PP.nas_upload.upload_mouse = lambda csv, user, entry, info, **k: (
            seen.append((Path(csv).name, entry["rel"], info)),
            {**info, "upload": {"status": "VERIFIED", "bytes": 49}})[-1]
        w = PP.Worker(s, on_event=lambda m: None)
        done = w._upload(s.get(r.run_id))
    finally:
        (PP.nas_upload.nas_status, PP.nas_upload.upload_mouse,
         PP.nas_upload.free_mouse_folder, PP.nas_upload.user_dir) = real

    rels = sorted(x[1] for x in seen)
    assert rels == ["HLBSSL/Baseline/20260921_HLBSSL32_B",
                    "HLBSSL/Recovery/20260921_HLBSSL31_R-2"], rels
    info = [x[2] for x in seen if x[0] == "20260921_HLBSSL31_R.csv"][0]
    assert info["mouseID"] == "HLBSSL31" and info["condition"] == "Recovery", info
    assert info["csv_columns"] == ["timestamp_raw", "timestamp_sec", "datetime_kst", "EEG", "EMG"]
    assert info["allego_base"] == "allego_0__uid0921-00-17-34"
    assert done.state == R.DONE, (done.state, done.error)
    assert sorted(p.name for p in out.glob("*.csv")) == ["unrelated.csv"], \
        "the local CSVs were not removed, or something else was"


def t_info_json_carries_the_ladder_verdict(tmp):
    """The CSV has no wire-free inputs, so the verdict must travel in info.json.

    Real cards, one of each kind: a PASS, a FAIL, and a chip whose floor carries
    signal (NO VERDICT, which must never read as NOT SCOREABLE).
    """
    import qc_info
    import postprocess as PP
    cards = Path(__file__).resolve().parents[2] / "eeg-emg-analysis" / "cards" / "out-windows"
    good = qc_info.qc_block(json.loads((cards / "W-SD" / "allego_1__uid0819-17-25-20__D2_card.json").read_text()))
    assert good["verdict"] == "SCOREABLE", good["verdict"]
    assert good["connection"]["eeg_and_emg_usable_pct"] > 90 and good["floor"]["n_wire_free_inputs"] == 14
    assert good["sleep_structure"]["r_1min"] > 0.30
    bad = qc_info.qc_block(json.loads((cards / "W-SD" / "allego_1__uid0819-17-25-20__B2_card.json").read_text()))
    assert bad["verdict"] == "NOT SCOREABLE" and "CONNECTION" in bad["why"], bad["why"]
    nov = qc_info.qc_block(json.loads((cards / "S-SL" / "allego_0__uid0921-00-17-34__A1_card.json").read_text()),
                           stage3={"verdict": "SCOREABLE", "persistence": {"1min": {"r": 0.647}}})
    assert nov["verdict"] == "NO VERDICT", nov["verdict"]
    assert nov["floor"]["slope_valid"] is False and nov["stage3"]["r_1min"] == 0.647
    # a live run with no card says so, rather than inventing a verdict
    s = mkstore(tmp)
    r = _stripped_run(s, tmp)
    q = PP.mouse_qc(r, "A1")
    assert q["verdict"] == "NOT ASSESSED" and "no card" in q["why"], q


def t_a_run_left_upload_pending_by_the_old_service_is_exported(tmp):
    """A run sitting in UPLOAD_PENDING with no export must be exported, not
    uploaded -- there is nothing per-mouse to upload yet."""
    import postprocess as PP
    s = mkstore(tmp)
    r = _stripped_run(s, tmp)
    r = s.transition(r.run_id, R.UPLOAD_PENDING)
    called = []
    real = PP.export_csv
    try:
        def fake(run, **k):
            called.append(run.run_id)
            raise PP.PostprocessError("fake export failure")
        PP.export_csv = fake
        w = PP.Worker(s, on_event=lambda m: None)
        out = w.process(r.run_id)
    finally:
        PP.export_csv = real
    assert called == [r.run_id], called
    assert out.state == "FAILED_EXPORT", out.state
    assert R.RETRY_TARGET["FAILED_EXPORT"] == R.STRIPPED


def t_two_slots_cannot_hold_the_same_animal(tmp):
    """A duplicate mouse id is refused AT SETUP, not seven minutes later.

    REPORTED 2026-09-14: a trial run had the same id typed into six slots. The
    console accepted it, recorded for six minutes, and only then failed --
    cohorts/schema.py refuses duplicate animal_ids, so no QC bundle could be
    computed, so the chain held at FAILED_QC. The operator had already left.

    Everything downstream is keyed on that id: the cohort record, every QC card,
    the per-animal export. It cannot be waved through, so it is caught while the
    form is still on screen.
    """
    import presets as _P
    import layout as _L

    cfg = _P.load()
    lay = _L.from_template(cfg, "8mice_eeg_emg")
    dup = {"A1": {"mouse_id": "dfdf", "recording_type": "basal"},
           "A2": {"mouse_id": "dfdf", "recording_type": "basal"},
           "B1": {"mouse_id": "other", "recording_type": "basal"},
           "B2": {"mouse_id": "dfdf", "recording_type": "basal"}}
    try:
        _L.validate_slots(lay, dup, cfg.recording_types)
    except ValueError as e:
        msg = str(e)
        assert "more than one slot" in msg, msg
        # it must name every clashing slot, not just say "duplicate"
        for slot in ("A1", "A2", "B2"):
            assert slot in msg, f"{slot} not named: {msg}"
        assert "B1" not in msg.split(".")[0], "an innocent slot was blamed"
    else:
        raise AssertionError("NOT REFUSED")

    # CASE IS FOLDED. "HLBSSL31" and "hlbssl31" are one animal to everyone
    # except a string comparison, and letting both through makes two QC cards
    # for one mouse -- the same failure, spelled differently. Slipped through
    # the first version of this check; caught 2026-09-14.
    try:
        _L.validate_slots(lay, {
            "A1": {"mouse_id": "HLBSSL31", "recording_type": "basal"},
            "A2": {"mouse_id": "hlbssl31", "recording_type": "basal"}},
            cfg.recording_types)
    except ValueError as e:
        assert "differing only in case" in str(e), str(e)
    else:
        raise AssertionError("case-only duplicate NOT REFUSED")

    # distinct ids pass, and one id may repeat across DIFFERENT runs
    ok = {k: {"mouse_id": f"M{i}", "recording_type": "basal"}
          for i, k in enumerate(dup)}
    assert len(_L.validate_slots(lay, ok, cfg.recording_types)) == 4
    # ...and the typed form is preserved, not folded
    kept = _L.validate_slots(lay, {
        "A1": {"mouse_id": "HLBSSL31", "recording_type": "basal"}},
        cfg.recording_types)
    assert kept["A1"]["mouse_id"] == "HLBSSL31"


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
    assert "one run per port" in (blocked[0].error or "").lower(), blocked[0].error
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


def t_missing_port_warns_but_still_records(tmp):
    """A headstage that dropped off the bus must be REPORTED at the start, never
    block it. Run dca84de0cc7a, 2026-10-15: declared A/B/C x 32, port B fell to
    0 at 23:54 the night before, and the 09:00 start recorded A + C with no word
    to anyone.
    """
    s = mkstore(tmp); fake = FakeAllego()
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing
    sent: list[tuple] = []
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None,
                      notify=lambda *a: sent.append(a))
    now = datetime.now().astimezone()
    lay = {"ports_used": ["A", "B", "C"],
           "expected_channels": {"A": 32, "B": 32, "C": 32, "D": 0}}

    def mk(start):
        return s.create(owner="ahyeon", preset="unipolar",
                        slots={p: {"mouse_id": f"U{p}", "recording_type": "basal"}
                               for p in "ABC"},
                        keep_labels=["A/18"], layout=lay,
                        scheduled_start=iso(start), dest_dir="/tmp/fake-dest")

    # positive control: everything present -> no warning, no alert
    fake.ports = {"A": 32, "B": 32, "C": 32}
    ok = mk(now - timedelta(seconds=5))
    sch.tick(now)
    ok = s.get(ok.run_id)
    assert ok.state == R.RECORDING and "start_warning" not in ok.results, ok.results
    assert ok.results["start_enumeration"] == fake.ports
    assert sent == [], sent
    sch.stop_now(ok.run_id)

    # port B gone: still RECORDING, mismatch recorded, one alert naming B
    fake.ports = {"A": 32, "B": 0, "C": 32}
    r = mk(now - timedelta(seconds=4))
    sch.tick(now)
    r = s.get(r.run_id)
    assert r.state == R.RECORDING, f"must still record A + C, got {r.state}"
    assert fake.starts == 2
    assert r.results["start_enumeration"] == {"A": 32, "B": 0, "C": 32}
    w = r.results.get("start_warning", "")
    assert "port B" in w and "UB" in w and "port A" not in w and "port C" not in w, w
    assert len(sent) == 1 and "port B" in sent[0][2], sent


# --------------------------------------------------------------------------- #
# per-port runs (2026-10-28): one run per PORT, not per rig
# --------------------------------------------------------------------------- #
def _patch(fake):
    allego.start, allego.stop, allego.confirm_growing = fake.start, fake.stop, fake.confirm_growing


def _wait(pred, timeout=5.0):
    import time
    t = time.time() + timeout
    while time.time() < t:
        if pred():
            return True
        time.sleep(0.02)
    return False


def t_disjoint_ports_record_concurrently(tmp):
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    a = mkrun(s, owner="andrea", start=iso(now - timedelta(seconds=5)),
              slots={"A1": {"mouse_id": "M1", "recording_type": "basal"}})
    b = mkrun(s, owner="diane", start=iso(now - timedelta(seconds=4)),
              slots={"B1": {"mouse_id": "M2", "recording_type": "basal"},
                     "C1": {"mouse_id": "M3", "recording_type": "basal"}})
    sch.tick(now)
    a, b = s.get(a.run_id), s.get(b.run_id)
    assert a.state == b.state == R.RECORDING, (a.state, b.state)
    assert fake.started_ports == [["A"], ["B", "C"]], fake.started_ports
    assert sorted(b.port_files) == ["B", "C"] and b.ports == ["B", "C"]
    assert b.data_path == b.port_files["B"]["data_path"], "data_path = first port's file"
    assert [r.run_id for r in s.active_runs()] and len(s.active_runs()) == 2
    d = b.to_dict()
    assert d["ports"] == ["B", "C"] and d["port_files"] == b.port_files


def t_stop_stops_only_own_ports(tmp):
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    a = mkrun(s, slots={"A1": {"mouse_id": "M1", "recording_type": "basal"},
                        "A2": {"mouse_id": "M4", "recording_type": "basal"}})
    b = mkrun(s, owner="diane", slots={"B1": {"mouse_id": "M2", "recording_type": "basal"}})
    sch.start_now(a.run_id); sch.start_now(b.run_id)
    sch.stop_now(a.run_id)
    assert fake.stopped_ports == [["A"]], fake.stopped_ports
    assert fake.on == {"B"}, f"B must keep recording, on={fake.on}"
    assert s.get(b.run_id).state == R.RECORDING
    # and a SCHEDULED stop names its ports too
    now = datetime.now().astimezone()
    c = mkrun(s, slots={"D1": {"mouse_id": "M5", "recording_type": "basal"}},
              start=iso(now - timedelta(seconds=5)), stop=iso(now - timedelta(seconds=1)))
    sch.tick(now); sch.tick(now)
    assert s.get(c.run_id).state == R.STOPPED
    assert fake.stopped_ports[-1] == ["D"] and fake.on == {"B"}, (fake.stopped_ports, fake.on)


def t_growth_is_confirmed_per_port_file(tmp):
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake); fake.dead = {"C"}
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    r = mkrun(s, slots={"B1": {"mouse_id": "M2", "recording_type": "basal"},
                        "C1": {"mouse_id": "M3", "recording_type": "basal"}})
    sch.start_now(r.run_id)
    assert _wait(lambda: "growth" in s.get(r.run_id).results), "growth never recorded"
    g = s.get(r.run_id).results["growth"]
    assert g["growing"] is False, "one dead port file must make the run NOT growing"
    assert g["ports"]["B"]["growing"] and not g["ports"]["C"]["growing"], g
    assert s.get(r.run_id).state == R.RECORDING


def t_growth_check_cannot_rewind_a_stop(tmp):
    """The growth write must not turn STOPPING back into RECORDING."""
    s = mkstore(tmp)
    r = mkrun(s)
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING):
        s.transition(r.run_id, st)
    try:
        s.transition(r.run_id, R.RECORDING, from_state=R.RECORDING, results={"growth": {}})
    except R.IllegalTransition:
        pass
    else:
        raise AssertionError("a stale RECORDING write was accepted")
    assert s.get(r.run_id).state == R.STOPPING


def t_port_files_column_is_migrated(tmp):
    """A runs.db from before 2026-10-28 has no port_files_json column."""
    import sqlite3
    db = Path(tmp) / "old.db"
    old_schema = R.SCHEMA.replace(
        "    port_files_json  TEXT,      -- {port: {base_name, data_path}}; "
        "empty for pre-2026-10-28 runs\n", "")
    assert "port_files_json" not in old_schema, "test did not remove the column"
    c = sqlite3.connect(db); c.executescript(old_schema)
    c.execute("INSERT INTO runs (run_id,state,owner,preset,created_utc,updated_utc,"
              "slots_json,keep_labels_json,data_path,base_name,results_json) VALUES "
              "('old1','DONE','andrea','p','2026-09-01T00:00:00Z','2026-09-01T00:00:00Z',"
              "'{\"A1\": {\"mouse_id\": \"M1\"}}','[\"A/1\"]','/x/allego_0__uid0901-09-00-00_data.xdat',"
              "'allego_0__uid0901-09-00-00','{}')")
    c.commit(); c.close()
    s = R.RunStore(db)
    old = s.get("old1")
    assert old.port_files == {} and old.data_path.endswith("_data.xdat"), old
    assert old.to_dict()["ports"] == ["A"]
    r = mkrun(s)
    pf = {"A": {"base_name": "allego_portA_0__uid1028-09-00-00", "data_path": "/x/a"}}
    for st in (R.SCHEDULED, R.STARTING):
        s.transition(r.run_id, st)
    assert s.transition(r.run_id, R.RECORDING, port_files=pf).port_files == pf
    assert R.RunStore(db).get(r.run_id).port_files == pf, "port_files not persisted"


def t_rewind_several_concurrent_runs(tmp):
    s = mkstore(tmp)
    a = mkrun(s, slots={"A1": {"mouse_id": "M1", "recording_type": "basal"}})
    b = mkrun(s, slots={"B1": {"mouse_id": "M2", "recording_type": "basal"}})
    c = mkrun(s, slots={"C1": {"mouse_id": "M3", "recording_type": "basal"}})
    for st in (R.SCHEDULED, R.STARTING):
        s.transition(a.run_id, st)
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING):
        s.transition(b.run_id, st)
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING):
        s.transition(c.run_id, st)
    moved = s.rewind_in_flight()
    assert sorted(moved) == sorted([a.run_id, b.run_id]), moved
    assert s.get(a.run_id).state == R.SCHEDULED
    assert s.get(b.run_id).state == R.RECORDING
    assert s.get(c.run_id).state == R.RECORDING, "a RECORDING run is not in flight"


def t_rig_lock(tmp):
    """Impedance/restart need the rig idle; a start never runs beside them."""
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()

    with sch.rig_exclusive("impedance measurement on port A"):        # idle: allowed
        assert sch.rig_busy() == {"busy": True,
                                  "reason": "impedance measurement on port A"}
    assert sch.rig_busy() == {"busy": False, "reason": None}

    # a start due at an instant while the lock is held FAILS, clearly, without starting
    old_wait, S.RIG_LOCK_WAIT_S = S.RIG_LOCK_WAIT_S, 0.05
    try:
        r = mkrun(s, start=iso(now - timedelta(seconds=5)))
        # (rig_exclusive itself would refuse here, a start is due; hold the lock
        # the way a restart that began just before the booking would)
        sch.rig_lock.acquire(); sch.rig_reason = "restarting Allego"
        try:
            sch.tick(now)
        finally:
            sch.rig_reason = None; sch.rig_lock.release()
        r = s.get(r.run_id)
        assert r.state == "FAILED_START" and "restarting allego" in r.error.lower(), \
            (r.state, r.error)
        assert fake.starts == 0
    finally:
        S.RIG_LOCK_WAIT_S = old_wait

    # a run recording -> rig-wide operations refused
    a = mkrun(s, slots={"A1": {"mouse_id": "M1", "recording_type": "basal"}})
    sch.start_now(a.run_id)
    try:
        with sch.rig_exclusive("impedance measurement on port B"):
            raise AssertionError("impedance allowed while a run records")
    except S.RigBusy as exc:
        assert a.run_id in str(exc), exc
    assert not sch.rig_lock.locked(), "a refused rig op must release the lock"
    sch.stop_now(a.run_id)

    # a start due within 10 minutes -> refused too
    mkrun(s, start=iso(datetime.now().astimezone() + timedelta(minutes=5)))
    try:
        with sch.rig_exclusive("restarting Allego"):
            raise AssertionError("restart allowed 5 min before a scheduled start")
    except S.RigBusy as exc:
        assert "scheduled to start" in str(exc), exc


# --------------------------------------------------------------------------- #
# regressions from the 2026-10-28 review
# --------------------------------------------------------------------------- #
def t_a_second_start_never_fails_a_recording_run(tmp):
    """Review fix 1: start_now and the tick both waited on the lock; the loser
    used to mark the RECORDING run FAILED_START while its ports kept recording."""
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    r = mkrun(s, start=iso(datetime.now().astimezone() - timedelta(seconds=5)))
    stale = s.get(r.run_id)                          # what the second waiter holds
    sch._start_run(stale, 0.0)
    assert s.get(r.run_id).state == R.RECORDING
    sch._start_run(stale, 0.0)                       # the loser, after the lock frees
    assert s.get(r.run_id).state == R.RECORDING, s.get(r.run_id).state
    assert fake.starts == 1
    old_wait, S.RIG_LOCK_WAIT_S = S.RIG_LOCK_WAIT_S, 0.01
    sch.rig_lock.acquire()
    try:
        sch._start_run(stale, 0.0)                   # lock timeout must not fail it either
    finally:
        sch.rig_lock.release(); S.RIG_LOCK_WAIT_S = old_wait
    assert s.get(r.run_id).state == R.RECORDING and not s.get(r.run_id).error


def t_stop_now_retries_a_failed_stop(tmp):
    """Review fix 3: Stop must work on FAILED_STOP / FAILED_RECORDING."""
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    for failed in ("FAILED_STOP", "FAILED_RECORDING"):
        r = mkrun(s)
        sch.start_now(r.run_id)
        s.transition(r.run_id, failed, detail="simulated")
        assert sch.stop_now(r.run_id).state == R.STOPPED, failed


def t_boot_adopts_a_start_that_really_started(tmp):
    """Review fix 4: a service death between start_recording and the RECORDING
    write must not orphan the port by rewinding to SCHEDULED."""
    import os
    import time as _t
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sent: list[tuple] = []
    dest = Path(tmp) / "raw"; dest.mkdir()
    sch = S.Scheduler(s, dest_dir=dest, on_event=lambda m: None,
                      notify=lambda *a: sent.append(a))
    mk = lambda slots: s.create(owner="andrea", preset="p", slots=slots,
                                keep_labels=["A/1"], dest_dir=str(dest),
                                scheduled_start=iso(datetime.now().astimezone()))
    a = mk({"A1": {"mouse_id": "M1", "recording_type": "basal"}})
    b = mk({"B1": {"mouse_id": "M2", "recording_type": "basal"}})
    for r in (a, b):
        s.transition(r.run_id, R.STARTING)
    old = dest / "allego_portA_0__uid1027-09-00-00_data.xdat"
    old.write_bytes(b""); os.utime(old, (_t.time() - 3600,) * 2)
    new = dest / "allego_portA_1__uid1028-09-00-00_data.xdat"; new.write_bytes(b"")
    orig = allego.status
    allego.status = lambda: {"reachable": True, "ports": {
        "A": {"channels": 32, "recording": True}, "B": {"channels": 32, "recording": False}}}
    try:
        sch._adopt_on_boot()
        s.rewind_in_flight()
    finally:
        allego.status = orig
    a, b = s.get(a.run_id), s.get(b.run_id)
    assert a.state == R.RECORDING, a.state
    assert a.port_files == {"A": {"base_name": new.name[:-len("_data.xdat")],
                                  "data_path": str(new)}}, a.port_files
    assert a.results.get("adopted_on_boot") is True
    assert any("adopted" in (e["detail"] or "") and e["to_state"] == R.RECORDING
               for e in s.events(a.run_id)), s.events(a.run_id)
    assert b.state == R.SCHEDULED, "ports OFF: rewound as before"
    assert any("adopted" in x[1] for x in sent), sent


def t_skipped_ports_are_persisted_and_not_orphans(tmp):
    """Review fix 6: a port that enumerated nothing is skipped, not an error."""
    import postprocess as PP
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake); fake.skipped = ["B"]
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    r = mkrun(s, slots={"A1": {"mouse_id": "M1", "recording_type": "basal"}})
    sch.start_now(r.run_id)
    assert s.get(r.run_id).results["skipped_ports"] == ["B"]
    run = s.get(r.run_id)
    pf = {"A": {"base_name": "allego_portA_0__uid1028-09-00-00",
                "data_path": "/x/allego_portA_0__uid1028-09-00-00_data.xdat"}}
    run.port_files, run.slots = pf, {"A1": {"mouse_id": "M1"}, "B1": {"mouse_id": "M2"}}
    run.keep_labels = ["A/1", "B/1"]
    run.results = {"skipped_ports": ["B"]}
    assert [x["port"] for x in PP.port_sources(run)] == ["A"]
    run.results = {}
    try:
        PP.port_sources(run)
    except PP.PostprocessError:
        pass
    else:
        raise AssertionError("a port with a mouse and no file, NOT skipped, must still refuse")


def t_start_now_respects_a_future_booking(tmp):
    """Review fix 7: Start now books [now, stop) and must not eat a reservation."""
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    mkrun(s, owner="diane", start=iso(now + timedelta(hours=2)), stop=iso(now + timedelta(hours=3)),
          slots={"A1": {"mouse_id": "M9", "recording_type": "basal"}})
    r = mkrun(s, slots={"A2": {"mouse_id": "M1", "recording_type": "basal"}})
    try:
        sch.start_now(r.run_id)
    except R.RunError as exc:
        assert "booked by run" in str(exc), exc
    else:
        raise AssertionError("an open-ended Start now ran into a later booking")
    assert fake.starts == 0 and s.get(r.run_id).state == R.DRAFT
    ok = mkrun(s, stop=iso(now + timedelta(hours=1)),
               slots={"A2": {"mouse_id": "M1", "recording_type": "basal"}})
    assert sch.start_now(ok.run_id).state == R.RECORDING, "ends before the booking: fine"


def t_a_double_stop_is_skipped_not_raised(tmp):
    """Review fix 9: a stop pressed while the tick stops must not run twice."""
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    r = mkrun(s, start=iso(now - timedelta(seconds=5)), stop=iso(now - timedelta(seconds=1)))
    sch.tick(now)
    stale = s.get(r.run_id)
    s.transition(r.run_id, R.STOPPING, detail="Stop pressed")      # the other path wins
    orig = s.list
    s.list = lambda **kw: [stale] if kw.get("states") == (R.RECORDING,) else orig(**kw)
    try:
        sch._tick_stops(now)                          # must skip, not raise
    finally:
        s.list = orig
    assert fake.stops == 0 and s.get(r.run_id).state == R.STOPPING
    expect_raise = False
    try:
        sch.stop_now(r.run_id)
    except R.RunError:
        expect_raise = True
    assert expect_raise, "stop_now on a STOPPING run must refuse"


def t_not_growing_alerts(tmp):
    """Review fix 10: a port that does not grow goes to ntfy, not only the log."""
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake); fake.dead = {"A"}
    sent: list[tuple] = []
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None,
                      notify=lambda *a: sent.append(a))
    r = mkrun(s, slots={"A1": {"mouse_id": "M1", "recording_type": "basal"}})
    sch.start_now(r.run_id)
    assert _wait(lambda: sent), "no alert for a port that does not grow"
    assert sent[0][0] == "fail" and "not growing" in sent[0][1], sent


def t_due_starts_sort_by_instant_not_string(tmp):
    """Review fix 12: '...T10:13+09:00' is EARLIER than '...T02:13+00:00'."""
    from datetime import timezone
    s = mkstore(tmp); fake = FakeAllego(); _patch(fake)
    sch = S.Scheduler(s, dest_dir="/tmp/fake-dest", on_event=lambda m: None)
    now = datetime.now().astimezone()
    kst = timezone(timedelta(hours=9))
    first = mkrun(s, start=(now - timedelta(seconds=60)).astimezone(kst).replace(microsecond=0).isoformat())
    second = mkrun(s, start=(now - timedelta(seconds=30)).astimezone(timezone.utc).replace(microsecond=0).isoformat())
    assert second.scheduled_start < first.scheduled_start, "test needs string order reversed"
    sch.tick(now)
    assert s.get(first.run_id).state == R.RECORDING, s.get(first.run_id).state
    assert s.get(second.run_id).state == "FAILED_START"


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
    expect("refuse: start_now on a port another run is recording",
           lambda: sch.start_now(mkrun(s).run_id), R.RunError, "booked by run")
    expect("refuse: stop_now on a run that is not recording",
           lambda: sch.stop_now(done.run_id), R.RunError, "not recording")

    # The growth-window guard. Imported fresh under a private name so the
    # monkeypatched module globals above are not disturbed.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_allego_pristine", Path(__file__).resolve().parent / "allego.py")
    import naming as _N
    import presets as _P0
    _s = mkstore(tmp)
    _r = _stripped_run(_s, tmp)
    _r = _s.transition(_r.run_id, _r.state, batch_name=None)
    expect("refuse: a run with no batch name has no NAS folder",
           lambda: _N.mouse_folders(_s.get(_r.run_id), _P0.load()), _N.NamingError, "required")

    # A setting whose sites cannot be described by the floor rule, with no
    # `qc: none`, would reach the chain and stall there on an override nobody
    # can satisfy. Refuse it at load instead.
    import presets as _P
    head = """
nas: {share: S, root: R}
recording_types: [basal]
recording_type_codes: {basal: B}
recording_type_folders: {basal: Baseline}
users: {}
headstages:
  hs: {label: H, slots_per_chip: 32, real_channels: 32}
recording_settings:
"""
    bad = Path(tmp) / "bad.yaml"
    bad.write_text(head + "  s: {label: S, headstage: hs, roles: {a: 18, b: 19}}\n")
    expect("refuse: a setting the floor rule cannot describe, without `qc: none`",
           lambda: _P.load(bad), _P.PresetError, "declare `qc: none`")

    ok = Path(tmp) / "ok.yaml"
    ok.write_text(head + "  s: {label: S, headstage: hs, roles: {a: 18, b: 19}, "
                         "qc: none, qc_reason: 'never characterised'}\n")
    check("declaring qc: none makes the same setting load",
          lambda: (_ for _ in ()).throw(AssertionError("qc flag lost"))
          if _P.load(ok).setting("s").qc_applies else None)

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
               t_qc_scores_only_occupied_slots, t_qc_none_preset_needs_no_override,
               t_empty_gpio_header_lets_the_strip_finish,
               t_export_spec_maps_each_slot_to_its_own_sites,
               t_frozen_mouse_dirs_are_reused_on_retry,
               t_a_run_left_upload_pending_by_the_old_service_is_exported,
               t_info_json_carries_the_ladder_verdict,
               t_two_slots_cannot_hold_the_same_animal,
               t_start_on_time, t_missed_start_fails_loudly, t_second_run_blocked,
               t_stop_fires_even_when_late, t_start_failure_is_recorded,
               t_scheduled_stop_hands_off_to_postprocessing,
               t_missing_port_warns_but_still_records,
               t_disjoint_ports_record_concurrently, t_stop_stops_only_own_ports,
               t_growth_is_confirmed_per_port_file, t_growth_check_cannot_rewind_a_stop,
               t_port_files_column_is_migrated, t_rewind_several_concurrent_runs,
               t_rig_lock, t_a_second_start_never_fails_a_recording_run,
               t_stop_now_retries_a_failed_stop, t_boot_adopts_a_start_that_really_started,
               t_skipped_ports_are_persisted_and_not_orphans,
               t_start_now_respects_a_future_booking, t_a_double_stop_is_skipped_not_raised,
               t_not_growing_alerts, t_due_starts_sort_by_instant_not_string):
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

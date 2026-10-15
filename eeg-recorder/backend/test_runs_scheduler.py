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
    def __init__(self):
        self.recording = False
        self.starts = 0
        self.stops = 0
        self.fail_start = False
        self.grew = True
        self.n = 0
        self.ports = None                       # live enumeration, when set

    def start(self, dest, **kw):
        if self.fail_start:
            raise allego.PreflightFailed("fake preflight failure")
        self.starts += 1
        self.n += 1
        self.recording = True
        name = f"allego_{self.n}__uidTEST"
        out = {"base_name": name, "base_path": f"{dest}/{name}",
               "data_path": f"{dest}/{name}_data.xdat", "mode": "R_ON",
               "started_at": 0.0, "dest": str(dest)}
        if self.ports is not None:
            out["ports"] = dict(self.ports)
        return out

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
               t_missing_port_warns_but_still_records):
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

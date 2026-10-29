#!/usr/bin/env python3
"""Contract for postprocess.py on PER-PORT runs (Allego 4, since 2026-10-28).

A run now leaves one recording per port (`run.port_files`), and every stage --
QC bundle, strip, per-mouse export, upload -- runs once per file. What these
cases pin down:

  - each port file is processed with ITS OWN slots and labels, never another
    port's (a wrong-port label is a wrong-channel CSV),
  - the QC manifest for a port file names only that port, so the floor comes
    from that file,
  - the run advances only when every port's file is done, a finished port is
    not redone on a retry, and per-file results are keyed by port,
  - a strip that meets another run's live recording WAITS instead of failing,
  - a run made before 2026-10-28 (no port_files) takes the old single-file path.

No subprocess is really started and nothing touches the NAS: the tools are
stubbed at the subprocess boundary, as in test_runs_scheduler.py.

    python3 test_postprocess_ports.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import traceback
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import runs as R            # noqa: E402
import presets as P         # noqa: E402
import layout as L          # noqa: E402
import postprocess as PP    # noqa: E402

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


class Done:
    returncode = 0
    stdout = stderr = ""


class Busy:
    returncode = 1
    stdout = ""
    stderr = ("REFUSED: the rig looks busy: other_portC_0__uid1028-19-00-00_data.xdat "
              "was written 3 s ago. Refusing to compete with a live recording for the "
              "same disk.")


NAMES = {"A": "allego_portA_0__uid1028-18-36-08", "B": "allego_portB_0__uid1028-18-36-08"}


def per_port_run(tmp, slots=None):
    """A two-port run (A, B, no splitter), left in STOPPED."""
    s = R.RunStore(Path(tmp) / "runs.db")
    cfg = P.load()
    lay = L.resolve(cfg, "eeg_emg", {"A": False, "B": False}, ports_used=("A", "B"))
    slots = slots or {"A": {"mouse_id": "MA", "recording_type": "basal"},
                      "B": {"mouse_id": "MB", "recording_type": "recovery"}}
    r = s.create(owner="andrea", preset="8mice_eeg_emg", slots=slots,
                 keep_labels=lay.labels(sorted(slots)), batch_name="PPTEST",
                 dest_dir=str(tmp))
    for st in (R.SCHEDULED, R.STARTING, R.RECORDING, R.STOPPING, R.STOPPED):
        s.transition(r.run_id, st)
    pf = {p: {"base_name": NAMES[p], "data_path": f"{tmp}/{NAMES[p]}_data.xdat"}
          for p in sorted({sl[0] for sl in slots})}
    first = sorted(pf)[0]
    r = s.transition(r.run_id, R.STOPPED, base_name=NAMES[first],
                     base_path=f"{tmp}/{NAMES[first]}", data_path=pf[first]["data_path"],
                     port_files=pf, actual_start="2026-10-28T09:36:08Z",
                     actual_stop="2026-10-28T09:38:00Z", layout=lay.to_dict())
    return s, r


# --------------------------------------------------------------------------- #
def t_port_sources_split_slots_and_labels(tmp):
    s, r = per_port_run(tmp)
    srcs = PP.port_sources(r)
    assert [x["port"] for x in srcs] == ["A", "B"]
    a, b = srcs
    assert a["slots"] == ["A"] and b["slots"] == ["B"], (a["slots"], b["slots"])
    assert a["keep_labels"] == ["A/1", "A/2"] and b["keep_labels"] == ["B/1", "B/2"]
    assert a["base_path"] == f"{tmp}/{NAMES['A']}" and a["base_name"] == NAMES["A"]
    # an old run is ONE source with port None and everything in it
    old = s.create(owner="andrea", preset="8mice_eeg_emg",
                   slots={"A1": {"mouse_id": "X", "recording_type": "basal"}},
                   keep_labels=["A/1", "A/2"], dest_dir=str(tmp))
    old = s.transition(old.run_id, old.state, base_name="allego_0__uid0921-00-17-34",
                       base_path=f"{tmp}/allego_0__uid0921-00-17-34")
    (one,) = PP.port_sources(old)
    assert one["port"] is None and one["keep_labels"] == ["A/1", "A/2"]
    assert PP._single([one])


def t_port_sources_refuse_a_mouse_without_a_file(tmp):
    s, r = per_port_run(tmp)
    r.port_files = {"A": r.port_files["A"]}        # B's file is missing
    try:
        PP.port_sources(r)
    except PP.PostprocessError as e:
        assert "B" in str(e) and "no recording file" in str(e), e
    else:
        raise AssertionError("a mouse on a port with no file was not refused")


def t_manifest_names_only_its_own_port(tmp):
    import yaml
    s, r = per_port_run(tmp)
    a = PP.port_sources(r)[0]
    path = PP.write_run_manifest(r, ("eeg", "emg"), Path(tmp) / "coh", src=a)
    doc = yaml.safe_load(path.read_text())
    assert path.name == f"auto-{r.run_id}-portA.yaml", path.name
    assert doc["ports"] == {"A": 1}, doc["ports"]
    assert [x["animal_id"] for x in doc["animals"]] == ["MA"], doc["animals"]
    assert doc["recordings"] == [{"base": NAMES["A"], "date": "2026-10-28"}], doc["recordings"]


def t_qc_bundle_per_port_uses_that_file(tmp):
    s, r = per_port_run(tmp)
    b = PP.port_sources(r)[1]
    seen = {}
    cache = Path(tmp) / "b.npz"
    real = PP.subprocess.run, PP.qc_cache_path, PP.write_run_manifest
    try:
        PP.subprocess.run = lambda cmd, **kw: (seen.update(cmd=cmd), cache.write_bytes(b"x"), Done())[-1]
        PP.qc_cache_path = lambda base: cache
        PP.write_run_manifest = lambda run, roles, out_dir=None, **kw: Path(tmp) / "m.yaml"
        ok, detail = PP.compute_qc_bundle(r, src=b)
    finally:
        PP.subprocess.run, PP.qc_cache_path, PP.write_run_manifest = real
    assert ok, detail
    cmd = seen["cmd"]
    assert cmd[2] == f"{tmp}/{NAMES['B']}", cmd
    assert cmd[cmd.index("--positions") + 1] == "B1", cmd
    assert cmd[cmd.index("--out") + 1].endswith(f"auto-{r.run_id}"), cmd


def t_strip_per_port_labels_siblings_and_report_name(tmp):
    s, r = per_port_run(tmp)
    a, b = PP.port_sources(r)
    out = Path(tmp) / "stripped"
    out.mkdir()
    seen = []

    def fake(cmd, **kw):
        seen.append(cmd)
        (out / f"{NAMES['A']}.strip-report.json").write_text(json.dumps(
            {"dst_base": str(out / NAMES["A"]), "plan": {"saving_pct": 90.0}}))
        return Done()

    real = PP.subprocess.run
    try:
        PP.subprocess.run = fake
        rep = PP.strip(r, out_dir=out, src=a, siblings=[b["base_path"]],
                       cfg=types.SimpleNamespace(gpio_header_connected=False))
        PP.subprocess.run = lambda cmd, **kw: Busy()
        try:
            PP.strip(r, out_dir=out, src=b, cfg=types.SimpleNamespace(gpio_header_connected=False))
        except PP.RigBusy:
            pass
        else:
            raise AssertionError("a busy-rig refusal was not raised as RigBusy")
    finally:
        PP.subprocess.run = real
    cmd = seen[0]
    assert cmd[3] == a["base_path"], cmd
    assert cmd[cmd.index("--keep-labels") + 1] == "A/1,A/2", cmd
    assert cmd[cmd.index("--also-source") + 1] == b["base_path"], cmd
    assert rep["dst_base"].endswith(NAMES["A"])


def t_state_advances_only_when_every_port_is_stripped(tmp):
    s, r = per_port_run(tmp)
    r = s.transition(r.run_id, R.QC)
    calls = []
    fail_b = {"on": True}

    def fake_strip(run, *, src, siblings=(), **kw):
        calls.append(src["port"])
        if src["port"] == "B" and fail_b["on"]:
            raise PP.PostprocessError("GATE B: fake")
        dst = Path(tmp) / f"{src['base_name']}"
        Path(str(dst) + ".xdat.json").write_text("{}")
        return {"dst_base": str(dst), "plan": {"saving_pct": 90.0, "bytes_in": 1000,
                                               "bytes_out": 100}}

    real = PP.strip
    w = PP.Worker(s, on_event=lambda m: None)
    try:
        PP.strip = fake_strip
        out = w._strip(s.get(r.run_id))
        assert out.state == "FAILED_STRIP", out.state
        assert "port B" in (out.error or ""), out.error
        assert set(out.results["strip"]["ports"]) == {"A"}, out.results["strip"]
        # retry: A is not redone, B now passes, and only now is the run STRIPPED
        s.transition(r.run_id, R.RETRY_TARGET["FAILED_STRIP"])
        fail_b["on"] = False
        out = w._strip(s.get(r.run_id))
    finally:
        PP.strip = real
    assert calls == ["A", "B", "B"], calls
    assert out.state == R.STRIPPED, out.state
    st = out.results["strip"]
    assert set(st["ports"]) == {"A", "B"} and st["saving_pct"] == 90.0, st
    assert "dst_base" not in st, "a top-level dst_base would name one port as the run"


def t_busy_rig_waits_instead_of_failing(tmp):
    s, r = per_port_run(tmp)
    r = s.transition(r.run_id, R.QC)
    deferred = []
    real = PP.strip
    w = PP.Worker(s, on_event=lambda m: None)
    w._defer = lambda rid: deferred.append(rid)
    try:
        PP.strip = lambda run, **kw: (_ for _ in ()).throw(PP.RigBusy(Busy.stderr))
        out = w._strip(s.get(r.run_id))
    finally:
        PP.strip = real
    assert out.state == R.QC, f"a busy rig failed the run: {out.state}"
    assert deferred == [r.run_id], deferred


def t_export_and_upload_per_port(tmp):
    s, r = per_port_run(tmp)
    for st in (R.QC, R.STRIPPING):
        s.transition(r.run_id, st)
    r = s.transition(r.run_id, R.STRIPPED, results={"strip": {"ports": {
        p: {"dst_base": f"{tmp}/stripped/{NAMES[p]}"} for p in "AB"}}})
    spec_a = PP.export_spec(r, src=PP.port_sources(r)[0])
    assert [m["slot"] for m in spec_a["mice"]] == ["A"], spec_a["mice"]
    assert spec_a["meta"]["port"] == "A" and spec_a["meta"]["raw_base_path"].endswith(NAMES["A"])

    seen = []

    def fake_run(cmd, **kw):
        seen.append(cmd)
        out = Path(cmd[cmd.index("--out") + 1])
        spec = json.loads(Path(cmd[cmd.index("--spec") + 1]).read_text())
        name = Path(cmd[3]).name
        rows = []
        for m in spec["mice"]:
            (out / f"{m['file_base']}.csv").write_text("x\n")
            rows.append({"file_base": m["file_base"], "csv": f"{m['file_base']}.csv",
                         "roles": ["EEG", "EMG"], "sha256": "s", "bytes": 2,
                         "verify": {"rows": 1}})
        (out / f"{name}.per-mouse-report.json").write_text(json.dumps({
            "samplingRate": 1000.0, "startTime_utc": "2026-10-28T09:36:08.644Z",
            "startTime_kst": "2026-10-28 18:36:08.644", "n_samples": 1, "duration_h": 0,
            "timestamp_raw_first": 1, "timestamp_raw_last": 1, "allego_base": name,
            "stripped_dataset_checksum": "d", "source": {}, "meta": spec["meta"],
            "tool": "t", "version": "v", "git_commit": None, "utc": "u", "mice": rows}))
        return Done()

    real = (PP.subprocess.run, PP.PER_MOUSE_ROOT, PP.nas_upload.nas_status,
            PP.nas_upload.upload_mouse, PP.nas_upload.free_mouse_folder,
            PP.nas_upload.user_dir)
    uploaded = []
    w = PP.Worker(s, on_event=lambda m: None)
    try:
        PP.subprocess.run = fake_run
        PP.PER_MOUSE_ROOT = Path(tmp) / "pm"
        out = w._export(s.get(r.run_id))
        assert out.state == R.EXPORTED, (out.state, out.error)
        ex = out.results["export"]
        assert set(ex["ports"]) == {"A", "B"} and ex["n_mice"] == 2, ex
        for c in seen:
            # every raw file of the run is named for the idle check
            assert c.count("--source-base") == 2, c
        out = s.transition(r.run_id, R.UPLOAD_PENDING)
        PP.nas_upload.nas_status = lambda: {"ok": True}
        PP.nas_upload.user_dir = lambda u: Path(tmp) / "nas" / u
        PP.nas_upload.free_mouse_folder = lambda user, e: dict(e)
        PP.nas_upload.upload_mouse = lambda csv, user, entry, info, **k: (
            uploaded.append((Path(csv).parent.name, info["allego_base"], info["port"])),
            {**info, "upload": {"status": "VERIFIED", "bytes": 2}})[-1]
        out = w._upload(s.get(r.run_id))
    finally:
        (PP.subprocess.run, PP.PER_MOUSE_ROOT, PP.nas_upload.nas_status,
         PP.nas_upload.upload_mouse, PP.nas_upload.free_mouse_folder,
         PP.nas_upload.user_dir) = real
    assert out.state == R.DONE, (out.state, out.error)
    assert sorted(uploaded) == [(NAMES["A"], NAMES["A"], "A"), (NAMES["B"], NAMES["B"], "B")], uploaded
    assert len(out.results["upload"]["local_csvs_removed"]) == 2


def t_card_path_follows_the_port_file(tmp):
    s, r = per_port_run(tmp)
    assert PP.card_path(r, "B1").name == f"{NAMES['B']}__B1_card.json"
    assert PP.card_path(r, "A1").name == f"{NAMES['A']}__A1_card.json"


# ---- review fixes, 2026-10-28 --------------------------------------------- #
def t_qc_waits_for_an_idle_rig(tmp):
    """Computing a bundle reads the whole file: it waits while the run's own
    files still grow. For a per-port run, other ports' recordings do not count
    (Andrea, 2026-10-29), so the check is asked with own_only=True."""
    s, r = per_port_run(tmp)
    deferred, computed, asked = [], [], []
    real = PP.rig_busy, PP.compute_qc_bundle, PP.has_qc_bundle
    w = PP.Worker(s, on_event=lambda m: None)
    w._defer = lambda rid: deferred.append(rid)
    try:
        PP.rig_busy = lambda srcs, own_only=False: asked.append(own_only) or (
            f"{NAMES['A']}_data.xdat is STILL GROWING (1 -> 2 bytes over 5 s)")
        PP.has_qc_bundle = lambda base: False
        PP.compute_qc_bundle = lambda *a, **k: computed.append(1) or (True, "")
        out = w._qc(s.get(r.run_id))
    finally:
        PP.rig_busy, PP.compute_qc_bundle, PP.has_qc_bundle = real
    assert out.state == R.STOPPED, out.state
    assert deferred == [r.run_id] and not computed, (deferred, computed)
    assert asked == [True], asked


def t_per_port_runs_may_share_the_disk_old_runs_may_not(tmp):
    """QC and strip of a per-port run ignore other ports' recordings; the strip
    is told so with --ignore-other-recordings. An old combined-file run keeps
    the full idle rule (Andrea, 2026-10-29)."""
    s, r = per_port_run(tmp)
    old = types.SimpleNamespace(port_files={})
    assert PP.may_share_disk(r) and not PP.may_share_disk(old)
    a, b = PP.port_sources(r)
    out = Path(tmp) / "stripped2"
    out.mkdir()
    seen = []

    def fake(cmd, **kw):
        seen.append(cmd)
        (out / f"{NAMES['A']}.strip-report.json").write_text(json.dumps(
            {"dst_base": str(out / NAMES["A"]), "plan": {"saving_pct": 90.0}}))
        return Done()

    real = PP.subprocess.run
    try:
        PP.subprocess.run = fake
        PP.strip(r, out_dir=out, src=a, siblings=[b["base_path"]],
                 cfg=types.SimpleNamespace(gpio_header_connected=False))
    finally:
        PP.subprocess.run = real
    assert "--require-idle" in seen[0] and "--ignore-other-recordings" in seen[0], seen[0]


def _xdat(path_base: Path, start_time: str):
    Path(str(path_base) + "_data.xdat").write_bytes(b"")
    Path(str(path_base) + ".xdat.json").write_text(json.dumps({"status": {"start_time": start_time}}))


def t_a_second_file_for_a_port_fails_the_run(tmp):
    s, r = per_port_run(tmp)
    _xdat(Path(tmp) / NAMES["A"], "2026-10-28T18:36:08.6+09:00")
    _xdat(Path(tmp) / NAMES["B"], "2026-10-28T18:36:08.6+09:00")
    # A from an EARLIER run on the same port: outside the window, not counted
    _xdat(Path(tmp) / "allego_portB_3__uid1027-09-00-00", "2026-10-27T09:00:00+09:00")
    w = PP.Worker(s, on_event=lambda m: None)
    assert PP.extra_port_files(r, PP.port_sources(r)) == {}
    # port A restarted mid-run
    _xdat(Path(tmp) / "allego_portA_1__uid1028-18-37-10", "2026-10-28T18:37:10.1+09:00")
    extra = PP.extra_port_files(r, PP.port_sources(r))
    assert extra == {"A": [f"{NAMES['A']}_data.xdat",
                           "allego_portA_1__uid1028-18-37-10_data.xdat"]}, extra
    out = w._qc(s.get(r.run_id))
    assert out.state == "FAILED_QC", out.state
    assert "allego_portA_1__uid1028-18-37-10_data.xdat" in out.error, out.error


def t_export_skip_needs_csvs_and_the_same_window(tmp):
    s, r = per_port_run(tmp)
    a = PP.port_sources(r)[0]
    out = Path(tmp) / "pm"
    out.mkdir()
    (out / "m.csv").write_text("abc")
    (out / "rep.json").write_text(json.dumps({"mice": [{"csv": "m.csv", "bytes": 3}]}))
    (out / "spec.json").write_text(json.dumps({"mice": []}))
    prev = {"report": str(out / "rep.json"), "out_dir": str(out)}
    assert PP._export_still_valid(r, a, prev)
    (out / "spec.json").write_text(json.dumps({"window": {"start_kst": "2026-10-28 09:00",
                                                          "end_kst": "2026-10-29 09:00"}}))
    assert not PP._export_still_valid(r, a, prev), "a different window was reused"
    (out / "spec.json").write_text(json.dumps({"mice": []}))
    (out / "m.csv").write_text("ab")
    assert not PP._export_still_valid(r, a, prev), "a CSV of the wrong size was reused"
    (out / "m.csv").unlink()
    assert not PP._export_still_valid(r, a, prev), "a missing CSV was reused"


def t_upload_refuses_done_with_a_slot_missing(tmp):
    s, r = per_port_run(tmp)
    out = Path(tmp) / "pm"
    out.mkdir()
    (out / "a.csv").write_text("x\n")
    rep = {"samplingRate": 1000.0, "startTime_utc": "u", "startTime_kst": "k",
           "n_samples": 1, "duration_h": 0, "timestamp_raw_first": 1,
           "timestamp_raw_last": 1, "allego_base": NAMES["A"], "stripped_dataset_checksum": "d",
           "source": {}, "meta": {}, "tool": "t", "version": "v", "git_commit": None,
           "utc": "u", "mice": [{"file_base": "a", "csv": "a.csv", "roles": ["EEG", "EMG"],
                                 "sha256": "s", "bytes": 2, "verify": {}}]}
    (out / "r.json").write_text(json.dumps(rep))
    spec = {"mice": [{"slot": "A", "position": "A1", "mouse_id": "MA",
                      "recording_type": "basal", "file_base": "a",
                      "columns": {"eeg": "A/1", "emg": "A/2"}}]}
    (out / "spec.json").write_text(json.dumps(spec))
    entry = {"batch": "PPTEST", "condition_dir": "Baseline", "folder": "f", "rel": "r",
             "file_base": "a"}
    for st in (R.QC, R.STRIPPING, R.STRIPPED, R.EXPORTING, R.EXPORTED, R.UPLOAD_PENDING):
        s.transition(r.run_id, st)
    s.transition(r.run_id, R.UPLOAD_PENDING, results={
        "export": {"ports": {"A": {"report": str(out / "r.json"), "out_dir": str(out)}}},
        "nas_mouse_dirs": {"A": entry, "B": dict(entry, folder="g")}})
    real = PP.nas_upload.nas_status, PP.nas_upload.upload_mouse
    try:
        PP.nas_upload.nas_status = lambda: {"ok": True}
        PP.nas_upload.upload_mouse = lambda csv, user, e, info, **k: {
            **info, "upload": {"status": "VERIFIED", "bytes": 2}}
        done = PP.Worker(s, on_event=lambda m: None)._upload(s.get(r.run_id))
    finally:
        PP.nas_upload.nas_status, PP.nas_upload.upload_mouse = real
    assert done.state == "FAILED_UPLOAD", done.state
    assert (out / "a.csv").exists(), "local CSVs were removed on an incomplete upload"


def t_deferral_is_stamped_alerted_once_and_clamped(tmp):
    import importlib
    import os
    s, r = per_port_run(tmp)
    sent = []
    w = PP.Worker(s, on_event=lambda m: None, notify=lambda *a: sent.append(a))
    w._stop.set()                                  # bookkeeping only, no timers
    w._defer(r.run_id)
    since = s.get(r.run_id).results["deferred_since"]
    w._defer(r.run_id)
    assert s.get(r.run_id).results["deferred_since"] == since and not sent
    s.transition(r.run_id, R.STOPPED, results={"deferred_since": "2026-01-01T00:00:00Z"})
    w._defer(r.run_id)
    w._defer(r.run_id)
    assert len(sent) == 1 and sent[0][0] == "warn", sent
    old = os.environ.get("EEG_PP_DEFER_S")
    try:
        os.environ["EEG_PP_DEFER_S"] = "0"
        assert importlib.reload(PP).DEFER_S == 30.0
    finally:
        if old is None:
            os.environ.pop("EEG_PP_DEFER_S", None)
        else:
            os.environ["EEG_PP_DEFER_S"] = old
        importlib.reload(PP)


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="pp-ports-test-")
    print("POSTPROCESS, PER-PORT RUNS")
    for fn in (t_port_sources_split_slots_and_labels,
               t_port_sources_refuse_a_mouse_without_a_file,
               t_manifest_names_only_its_own_port,
               t_qc_bundle_per_port_uses_that_file,
               t_strip_per_port_labels_siblings_and_report_name,
               t_state_advances_only_when_every_port_is_stripped,
               t_busy_rig_waits_instead_of_failing,
               t_export_and_upload_per_port,
               t_card_path_follows_the_port_file,
               t_qc_waits_for_an_idle_rig,
               t_per_port_runs_may_share_the_disk_old_runs_may_not,
               t_a_second_file_for_a_port_fails_the_run,
               t_export_skip_needs_csvs_and_the_same_window,
               t_upload_refuses_done_with_a_slot_missing,
               t_deferral_is_stamped_alerted_once_and_clamped):
        d = tempfile.mkdtemp(dir=tmp)
        check(fn.__name__, lambda fn=fn, d=d: fn(d))
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

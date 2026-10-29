#!/usr/bin/env python3
"""Contract for Allego 4 PER-PORT recordings (split_files_by_port=True, 2026-10-28).

Since 2026-10-28 a run is one file per port, `<base>_port<X>_<N>__uid<...>`,
holding that port's 32 amplifier channels plus aux_1, din_1, dout_1. Every tool
on the post-recording path reads such a file through the same code it uses for
a combined 262-channel recording, so these cases check that the shared code
still means the same thing on the new shape:

  - `open_xdat` labels a port-B file `B/1`..`B/32` although its ntv names and
    sys_chan_idx are rig-wide (`port_B_32`.., 32..63, aux at 128),
  - the QC floor of a per-port file comes from that port alone, and a cohort
    spec that names other ports is REFUSED rather than silently judged,
  - the stripper and the per-mouse exporter accept the file, keep the right
    columns and convert Allego 4's local start_time correctly,
  - the idle check judges the run's other port files by growth, not mtime,
  - the old `radiens` package is never imported.

The files are synthetic (tests/synth.py `write_port_file`), built in the exact
shape measured on the bench files `porttest_port{A,B}_0__uid1028-...`.

Run as a script (this repo's convention):
    PYTHONPATH=. python3 tests/test_per_port_files.py
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from convert import strip_channels as SC      # noqa: E402
from core import criteria as C                # noqa: E402
from export import per_mouse_csv as E         # noqa: E402
from tests import synth                       # noqa: E402

FS = synth.FS
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


def expect(name, fn, exc, want=""):
    def run():
        try:
            fn()
        except exc as e:
            if want and want.lower() not in str(e).lower():
                raise AssertionError(f"refused for the wrong reason: {e}")
            return
        raise AssertionError("NOT REFUSED -- the guard did not fire")
    check(name, run)


def port_file(tmp: Path, port: str = "B", seconds: int = 60, **kw) -> str:
    rng = np.random.default_rng(5)
    n = seconds * FS
    eeg = synth.connected_eeg(n, rng)
    emg = synth.scale_to_epoch_rms(synth.white(n, rng), 40.0)
    return synth.write_port_file(tmp / f"rec_port{port}_0__uid1028-18-36-51", port,
                                 {1: eeg, 2: emg}, **kw)


def one_port_spec(port: str) -> C.CohortSpec:
    """The spec postprocess.write_run_manifest produces for one port file:
    `ports: {port: 1}` on a bipolar eeg+emg layout."""
    from cohorts.schema import Cohort
    return Cohort.from_obj({"cohort_id": "t", "roles": ["eeg", "emg"],
                            "ports": {port: 1}, "criterion": "slope"}).to_spec()


# --------------------------------------------------------------------------- #
# MUST PASS
# --------------------------------------------------------------------------- #

def t_open_xdat_labels_a_port_b_file(tmp: Path):
    base = port_file(tmp, "B", seconds=20)
    x, labels, fs, n = C.open_xdat(base)
    assert x.shape == (20 * FS, 35), x.shape
    assert fs == FS and n == 20 * FS
    assert labels[:2] == ["B/1", "B/2"] and labels[31] == "B/32", labels[:3]
    assert labels[32:] == ["GPIO-AIN/0", "GPIO-DIN/0", "GPIO-DOUT/0"], labels[32:]
    meta = json.loads(Path(base + ".xdat.json").read_text())
    bm = meta["sapiens_base"]["biointerface_map"]
    # the fixture really has the rig-wide numbering the bench files have
    assert bm["ntv_chan_name"][0] == "port_B_32" and bm["sys_chan_idx"][32] == 128
    integ = C.file_integrity(base)
    assert integ["verdict"] == "INTACT", integ
    ts = np.fromfile(base + "_timestamp.xdat", dtype=np.int64)
    assert ts[0] == 964352 and np.all(np.diff(ts) == 1)


def t_qc_floor_comes_from_its_own_port(tmp: Path):
    base = port_file(tmp, "B", seconds=60)
    spec = one_port_spec("B")
    assert spec.positions() == ["B1"], spec.positions()
    assert spec.floor_sites() == [f"B/{i}" for i in range(3, 17)], spec.floor_sites()
    feat = C.compute_features(base, spec, progress=None)
    assert feat.n_epochs == 6, feat.n_epochs
    assert set(feat.sites) == {f"B/{i}" for i in range(1, 17)}, feat.sites
    fl = C.floor_stats(feat, "B1")
    assert fl.n_sites == 14, fl


def t_strip_per_port_file(tmp: Path):
    base = port_file(tmp, "B", seconds=12)
    out = tmp / "stripped"
    meta = SC.read_meta(base)
    keep = SC.resolve_keep(meta, labels=["B/1", "B/2"])
    assert keep == [0, 1], keep
    rep = SC.strip(base, str(out / os.path.basename(base)), keep,
                   progress=None, min_free_gb=0.0)
    assert rep["status"] == "verified", rep
    dst = rep["dst_base"]
    assert os.path.basename(dst) == os.path.basename(base), dst
    _x, labels, fs, n = C.open_xdat(dst)
    assert labels == ["B/1", "B/2"] and n == 12 * FS
    prov = json.loads(Path(dst + ".xdat.json").read_text())["status"]["dataset_provenance"][-1]
    # the rig-wide source rows are recorded, so the renumbering stays reversible
    assert prov["kept_orig_sys_chan_idx"] == [32, 33], prov["kept_orig_sys_chan_idx"]
    hood = json.loads(Path(dst + ".xdat.json").read_text())["sapiens_base"]["neighborhoods"]["site_hood"]
    assert sorted(hood) == ["32", "33"], sorted(hood)
    # gate B judged the port's own din_1 (flat) and dout_1 (constant 1)
    assert [d["chan_name"] for d in rep["dropped_gpio"]] == ["aux_1", "din_1", "dout_1"]


def t_export_per_port_file_converts_local_start_time(tmp: Path):
    base = port_file(tmp, "A", seconds=12)
    out = tmp / "stripped"
    meta = SC.read_meta(base)
    rep = SC.strip(base, str(out / os.path.basename(base)),
                   SC.resolve_keep(meta, labels=["A/1", "A/2"]),
                   progress=None, min_free_gb=0.0)
    spec = {"mice": [{"slot": "A", "mouse_id": "FAKE", "file_base": "20261028_FAKE_B",
                      "columns": {"eeg": "A/1", "emg": "A/2"}}]}
    r = E.export(rep["dst_base"], spec, tmp / "pm", progress=None, min_free_gb=0.0)
    assert r["startTime_utc"] == "2026-10-28T09:36:08.644Z", r["startTime_utc"]
    assert r["startTime_kst"] == "2026-10-28 18:36:08.644", r["startTime_kst"]
    assert r["startTime_as_written"].endswith("+09:00")
    x, _l, _fs, _n = C.open_xdat(base)
    with open(tmp / "pm" / "20261028_FAKE_B.csv") as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == ["timestamp_raw", "timestamp_sec", "datetime_kst", "EEG", "EMG"]
    assert rows[1][:3] == ["964352", "0.000", "2026-10-28 18:36:08.644"], rows[1]
    assert abs(float(rows[1][3]) - float(x[0, 0])) <= 0.0005
    assert abs(float(rows[-1][4]) - float(x[-1, 1])) <= 0.0005
    assert len(rows) - 1 == 12 * FS


def t_old_utc_start_time_is_kept_verbatim(tmp: Path):
    """A combined Allego 3 file's `...Z` start_time must not change by a
    character in the report, so old exports stay byte-comparable."""
    from datetime import datetime
    t = "2026-09-20T15:17:34.272Z"
    assert E._utc_text(t, datetime.fromisoformat(t.replace("Z", "+00:00"))) == t


def t_siblings_of_the_same_run_are_judged_by_growth(tmp: Path):
    d = tmp / "raw"
    d.mkdir()
    a = synth.write_port_file(d / "run_portA_0__uid1028-18-36-08", "A",
                              {1: np.zeros(2000)})
    b = synth.write_port_file(d / "run_portB_0__uid1028-18-36-08", "B",
                              {1: np.zeros(2000)})
    # both just written, i.e. a two-port run that stopped seconds ago
    busy = SC.rig_is_busy(d, source_base=a, settle_s=0.2)
    assert busy and "run_portB_0" in busy, \
        f"the sibling should look recent when not named: {busy}"
    assert SC.rig_is_busy(d, source_base=[a, b], settle_s=0.2) is None
    # a file of ANOTHER run that is recent still makes the rig busy
    c = synth.write_port_file(d / "other_portC_0__uid1028-18-40-00", "C",
                              {1: np.zeros(2000)})
    busy = SC.rig_is_busy(d, source_base=[a, b], settle_s=0.2)
    assert busy and "other_portC_0" in busy, busy
    del c


def t_own_only_ignores_other_runs_but_not_its_own_growth(tmp: Path):
    """own_only (Andrea, 2026-10-29): another port's live file does not make the
    rig busy, but this run's own file still growing does."""
    import threading
    d = tmp / "raw"
    d.mkdir()
    a = synth.write_port_file(d / "run_portA_0__uid1028-18-36-08", "A",
                              {1: np.zeros(2000)})
    synth.write_port_file(d / "other_portC_0__uid1028-18-40-00", "C",
                          {1: np.zeros(2000)})
    assert SC.rig_is_busy(d, source_base=[a], settle_s=0.2), \
        "without own_only the other run's fresh file must still count"
    assert SC.rig_is_busy(d, source_base=[a], settle_s=0.2, own_only=True) is None

    def grow():
        time.sleep(0.05)
        with open(str(a) + "_data.xdat", "ab") as fh:
            fh.write(b"\0" * 4096)
    t = threading.Thread(target=grow)
    t.start()
    busy = SC.rig_is_busy(d, source_base=[a], settle_s=0.4, own_only=True)
    t.join()
    assert busy and "STILL GROWING" in busy, busy


def t_stale_live_flag_read_from_session_metadata(tmp: Path):
    d = tmp / "raw"
    d.mkdir()
    synth.write_port_file(d / "x_portA_0__uid1028-18-36-08", "A",
                          {1: np.zeros(1000)}, live=True)
    old = time.time() - 3600
    for f in d.iterdir():
        os.utime(f, (old, old))
    assert SC.stale_live_flags(d) == ["x_portA_0__uid1028-18-36-08.xdat.json"]


def t_radiens_probe_never_imports_old_radiens(tmp: Path):
    sys.modules.pop("radiens", None)
    r = SC._radiens_probe(str(tmp / "nothing"), expect_channels=2, expect_fs=FS)
    assert r["skipped"] is True and r["ok"] is None, r
    assert "radiens" not in sys.modules, "the old radiens package was imported"


def t_strip_stops_when_a_recording_starts_and_resume_keeps_gate_b(tmp: Path):
    """Review 2026-10-28: the idle check is repeated DURING the strip. A strip
    stopped that way resumes from its .part, and Gate B must still see a din
    pulse train that sat only in the part written before the stop."""
    n = 20 * FS
    din = np.zeros(n, dtype=np.float32)
    din[:4000][np.arange(4000) % 500 < 5] = 1.0         # pulses in the first 4 s only
    base = synth.write_port_file(tmp / "rec_portA_0__uid1028-18-36-08", "A",
                                 {1: np.zeros(n), 2: np.zeros(n)}, din=din)
    keep = SC.resolve_keep(SC.read_meta(base), labels=["A/1", "A/2"])
    dst = str(tmp / "out" / os.path.basename(base))
    calls = {"n": 0}

    def fake_busy(*a, **k):
        calls["n"] += 1
        return None if calls["n"] == 1 else "other_portB_0_data.xdat was written 1 s ago"

    real = SC.rig_is_busy, SC.IDLE_RECHECK_CHUNKS
    try:
        SC.rig_is_busy, SC.IDLE_RECHECK_CHUNKS = fake_busy, 1
        try:
            SC.strip(base, dst, keep, progress=None, min_free_gb=0.0,
                     chunk_samples=5000, require_idle=True)
        except SC.StripRefused as e:
            assert "rig looks busy" in str(e), e
        else:
            raise AssertionError("a recording that started mid-strip did not stop it")
    finally:
        SC.rig_is_busy, SC.IDLE_RECHECK_CHUNKS = real
    part = Path(dst + "_data.xdat.part")
    assert part.exists() and 0 < part.stat().st_size < n * 2 * 4, "no partial to resume"
    assert not Path(dst + ".xdat.json").exists()
    try:
        SC.strip(base, dst, keep, progress=None, min_free_gb=0.0, chunk_samples=5000)
    except SC.StripFailed as e:
        assert "GATE B" in str(e), e
    else:
        raise AssertionError("the resumed strip forgot the din pulses written before the stop")


def t_first_row_and_report_agree_to_the_ms(tmp: Path):
    """Review 2026-10-28: Allego 4 start times carry nanoseconds. Row 1's
    datetime_kst and the report's startTime_kst are both TRUNCATED to the ms."""
    base = synth.write_port_file(tmp / "rec_portA_0__uid1028-18-36-08", "A",
                                 {1: np.zeros(3000), 2: np.zeros(3000)},
                                 start_time="2026-10-28T18:36:08.644999999+09:00")
    rep = SC.strip(base, str(tmp / "s" / os.path.basename(base)),
                   SC.resolve_keep(SC.read_meta(base), labels=["A/1", "A/2"]),
                   progress=None, min_free_gb=0.0)
    spec = {"mice": [{"slot": "A", "file_base": "f", "columns": {"eeg": "A/1", "emg": "A/2"}}]}
    r = E.export(rep["dst_base"], spec, tmp / "pm", progress=None, min_free_gb=0.0)
    with open(tmp / "pm" / "f.csv") as fh:
        next(fh)
        first = next(fh).split(",")[2]
    assert first == r["startTime_kst"] == "2026-10-28 18:36:08.644", (first, r["startTime_kst"])
    assert r["startTime_utc"] == "2026-10-28T09:36:08.644Z", r["startTime_utc"]


def t_qc_scripts_convert_local_start_times(tmp: Path):
    """Review 2026-10-28: three scripts added 9 h to start_time as if it were
    always UTC. Both forms must give the same local time."""
    import datetime as dt
    from qc.emg_state_dependence import local_start
    for st in ("2026-10-28T09:36:08.644Z", "2026-10-28T18:36:08.644028952+09:00"):
        b = tmp / f"x{len(st)}"
        Path(str(b) + ".xdat.json").write_text(json.dumps({"status": {"start_time": st}}))
        got = local_start(str(b))
        assert got.replace(microsecond=0) == dt.datetime(2026, 10, 28, 18, 36, 8), (st, got)
    for f in ("qc/allchip_scan_file.py", "qc/night_spikes.py"):
        src = (Path(__file__).resolve().parent.parent / f).read_text()
        assert "+ dt.timedelta(hours=9)" not in src and ".astimezone(" in src, f


# --------------------------------------------------------------------------- #
# MUST REFUSE
# --------------------------------------------------------------------------- #

def refusals(tmp: Path):
    base = port_file(tmp, "B", seconds=20)
    # A four-port spec on a one-port file: the floor sites of A, C, D are not in
    # it. Judging B against whatever is present would be a different criterion.
    expect("refuse: a cohort spec naming ports this file does not hold",
           lambda: C.compute_features(base, C.CohortSpec(roles=("eeg", "emg")),
                                      progress=None),
           SystemExit, "not in this file")
    expect("refuse: keep label from another port",
           lambda: SC.resolve_keep(SC.read_meta(base), labels=["A/1"]),
           SC.StripRefused, "not in this file")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="per-port-test-"))
    try:
        print("PER-PORT FILES: MUST PASS")
        for fn in (t_open_xdat_labels_a_port_b_file, t_qc_floor_comes_from_its_own_port,
                   t_strip_per_port_file,
                   t_export_per_port_file_converts_local_start_time,
                   t_old_utc_start_time_is_kept_verbatim,
                   t_siblings_of_the_same_run_are_judged_by_growth,
                   t_own_only_ignores_other_runs_but_not_its_own_growth,
                   t_stale_live_flag_read_from_session_metadata,
                   t_radiens_probe_never_imports_old_radiens,
                   t_strip_stops_when_a_recording_starts_and_resume_keeps_gate_b,
                   t_first_row_and_report_agree_to_the_ms,
                   t_qc_scripts_convert_local_start_times):
            d = Path(tempfile.mkdtemp(dir=tmp))
            check(fn.__name__, lambda fn=fn, d=d: fn(d))
        print("\nMUST REFUSE")
        refusals(Path(tempfile.mkdtemp(dir=tmp)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for name, tb in FAIL:
        print(f"\n--- {name} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

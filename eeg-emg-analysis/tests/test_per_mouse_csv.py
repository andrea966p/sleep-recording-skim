#!/usr/bin/env python3
"""Contract for export/per_mouse_csv.py.

Every value is checked against the stripped xdat it came from, not against the
exporter's own idea of what it wrote, and every guard gets a case that makes it
fire. A wrong-channel CSV is the failure that matters here, so the label-mapping
refusals are not optional.

Run as a script (this repo's convention):
    PYTHONPATH=. python3 tests/test_per_mouse_csv.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from convert import strip_channels as SC
from export import per_mouse_csv as E
from tests import synth

FS = synth.FS
PASS, FAIL = [], []
KST = timezone(timedelta(hours=9))


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


# --------------------------------------------------------------------------- #

def stripped_recording(tmp: Path, *, seconds: int = 12, ts_offset: int = 57_403_264):
    """Two ports, two mice each, stripped to 8 channels like the real rig.

    The timestamp file is rewritten to start at a large non-zero counter, as a
    real one does, so a tool that assumed zero-based timestamps would fail.
    """
    rng = np.random.default_rng(3)
    n = seconds * FS
    items = []
    for p in ("A", "B"):
        for s in range(1, 49):
            items.append((f"{p}/{s}", synth.scale_to_epoch_rms(synth.pink(n, rng), 50.0)))
    raw = synth.write_full_sidecar(tmp / "allego_0__uid0921-00-17-34", items,
                                   start_time_utc="2026-09-20T15:17:34.272Z")
    ts = np.arange(ts_offset, ts_offset + n, dtype=np.int64)
    ts.tofile(raw + "_timestamp.xdat")
    # the checksum covers the timestamps, so refresh it
    h = hashlib.sha256()
    for suf in ("_data.xdat", "_timestamp.xdat"):
        h.update(Path(raw + suf).read_bytes())
    meta = json.loads(Path(raw + ".xdat.json").read_text())
    meta["status"]["dataset_checksum"] = h.hexdigest()
    meta["status"]["timestamp_range"] = [int(ts[0]), int(ts[-1]) + 1]
    Path(raw + ".xdat.json").write_text(json.dumps(meta))

    assert not any(np.isnan(v).any() for _, v in items), "synthetic signal has NaN"
    labels = ["A/1", "A/2", "A/33", "A/34", "B/1", "B/2", "B/33", "B/34"]
    keep = SC.resolve_keep(SC.read_meta(raw), labels=labels)
    out = tmp / "stripped"
    out.mkdir()
    dst = str(out / os.path.basename(raw))
    SC.strip(raw, dst, keep, progress=None, min_free_gb=0.0)
    return raw, dst, n


def spec_for(slots=("A1", "A2", "B1", "B2")):
    base = {"A1": ("A", 1), "A2": ("A", 33), "B1": ("B", 1), "B2": ("B", 33)}
    mice = []
    for i, s in enumerate(slots):
        p, b = base[s]
        mice.append({"slot": s, "mouse_id": f"HLBSSL3{i + 1}",
                     "file_base": f"20260921_HLBSSL3{i + 1}_R",
                     "columns": {"eeg": f"{p}/{b}", "emg": f"{p}/{b + 1}"}})
    return {"mice": mice, "meta": {"run_id": "test"}}


def run_export(stripped, out, spec=None, **kw):
    return E.export(stripped, spec or spec_for(), out, progress=None,
                    min_free_gb=0.0, chunk=kw.pop("chunk", 1000), **kw)


def read_csv(path: Path):
    with open(path) as fh:
        r = csv.reader(fh)
        header = next(r)
        rows = list(r)
    return header, rows


# --------------------------------------------------------------------------- #
# MUST PASS
# --------------------------------------------------------------------------- #

def t_columns_and_rows(tmp):
    _, st, n = stripped_recording(tmp)
    rep = run_export(st, tmp / "out")
    assert len(rep["mice"]) == 4
    h, rows = read_csv(tmp / "out" / "20260921_HLBSSL31_R.csv")
    assert h == ["timestamp_raw", "timestamp_sec", "datetime_kst", "EEG", "EMG"], h
    assert len(rows) == n, (len(rows), n)


def t_values_are_the_right_channels(tmp):
    """Every mouse, every row, against the stripped xdat -- the wrong-channel test."""
    _, st, n = stripped_recording(tmp)
    run_export(st, tmp / "out")
    data = np.fromfile(st + "_data.xdat", dtype=np.float32).reshape(n, 8)
    col = {"A/1": 0, "A/2": 1, "A/33": 2, "A/34": 3, "B/1": 4, "B/2": 5, "B/33": 6, "B/34": 7}
    for m in spec_for()["mice"]:
        _, rows = read_csv(tmp / "out" / f"{m['file_base']}.csv")
        eeg = np.array([float(r[3]) for r in rows])
        emg = np.array([float(r[4]) for r in rows])
        assert np.max(np.abs(eeg - data[:, col[m["columns"]["eeg"]]])) <= 0.0005 + 1e-6
        assert np.max(np.abs(emg - data[:, col[m["columns"]["emg"]]])) <= 0.0005 + 1e-6
        # and NOT some other mouse's channel
        other = data[:, col["B/33"] if m["columns"]["eeg"] != "B/33" else 0]
        assert np.max(np.abs(eeg - other)) > 1.0


def t_timestamps(tmp):
    _, st, n = stripped_recording(tmp)
    run_export(st, tmp / "out")
    ts = np.fromfile(st + "_timestamp.xdat", dtype=np.int64)
    _, rows = read_csv(tmp / "out" / "20260921_HLBSSL32_R.csv")
    raw = np.array([int(r[0]) for r in rows])
    assert (raw == ts).all(), "timestamp_raw is not verbatim"
    assert rows[0][1] == "0.000" and rows[1][1] == "0.001" and rows[-1][1] == f"{(n - 1) / FS:.3f}"
    t0 = datetime(2026, 9, 20, 15, 17, 34, 272000, tzinfo=timezone.utc).astimezone(KST)
    assert rows[0][2] == "2026-09-21 00:17:34.272", rows[0][2]
    last = (t0 + timedelta(milliseconds=n - 1)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    assert rows[-1][2] == last, (rows[-1][2], last)


def t_a_gap_in_the_counter_shows_as_a_jump(tmp):
    _, st, n = stripped_recording(tmp)
    ts = np.fromfile(st + "_timestamp.xdat", dtype=np.int64)
    ts[3000:] += 250                      # 250 samples never delivered
    ts.tofile(st + "_timestamp.xdat")
    run_export(st, tmp / "out")
    _, rows = read_csv(tmp / "out" / "20260921_HLBSSL31_R.csv")
    assert rows[2999][1] == "2.999" and rows[3000][1] == "3.250", (rows[2999][1], rows[3000][1])


def t_report_and_sha(tmp):
    _, st, n = stripped_recording(tmp)
    rep = run_export(st, tmp / "out")
    on_disk = json.loads((tmp / "out" / f"{os.path.basename(st)}.per-mouse-report.json").read_text())
    assert on_disk["n_samples"] == n and on_disk["samplingRate"] == FS
    assert on_disk["startTime_kst"] == "2026-09-21 00:17:34.272"
    assert on_disk["source"]["kept_labels"][:2] == ["A/1", "A/2"]
    for m in rep["mice"]:
        p = tmp / "out" / m["csv"]
        assert hashlib.sha256(p.read_bytes()).hexdigest() == m["sha256"]
        assert m["verify"]["rows"] == n and m["verify"]["spot_rows"] > 100


def t_rerun_is_a_noop(tmp):
    _, st, _ = stripped_recording(tmp)
    run_export(st, tmp / "out")
    p = tmp / "out" / "20260921_HLBSSL31_R.csv"
    mt = p.stat().st_mtime_ns
    time.sleep(0.01)
    rep = run_export(st, tmp / "out")
    assert p.stat().st_mtime_ns == mt, "a verified CSV was rewritten"
    assert len(rep["mice"]) == 4


def t_a_tampered_csv_is_rewritten(tmp):
    _, st, _ = stripped_recording(tmp)
    run_export(st, tmp / "out")
    p = tmp / "out" / "20260921_HLBSSL33_R.csv"
    b = bytearray(p.read_bytes()); b[200] = ord("9") if b[200] != ord("9") else ord("8")
    p.write_bytes(bytes(b))
    rep = run_export(st, tmp / "out")
    m = [x for x in rep["mice"] if x["csv"] == p.name][0]
    assert hashlib.sha256(p.read_bytes()).hexdigest() == m["sha256"]


def t_subset_of_mice(tmp):
    _, st, n = stripped_recording(tmp)
    rep = run_export(st, tmp / "out", spec=spec_for(("A2",)))
    assert [m["slot"] for m in rep["mice"]] == ["A2"]
    assert sorted(p.name for p in (tmp / "out").glob("*.csv")) == ["20260921_HLBSSL31_R.csv"]


def t_window_trims_to_the_requested_times(tmp):
    """Recording starts 00:17:34.272 KST; window 00:17:36 -> 00:17:40 is 4000 rows."""
    _, st, n = stripped_recording(tmp)
    sp = spec_for(("A1",)); sp["window"] = {"start_kst": "2026-09-21 00:17:36",
                                            "end_kst": "2026-09-21 00:17:40"}
    rep = run_export(st, tmp / "out", spec=sp)
    _, rows = read_csv(tmp / "out" / "20260921_HLBSSL31_R.csv")
    assert len(rows) == 4000, len(rows)
    assert rows[0][2] == "2026-09-21 00:17:36.000" and rows[-1][2] == "2026-09-21 00:17:39.999", \
        (rows[0][2], rows[-1][2])
    assert rows[0][1] == "0.000", "timestamp_sec must restart at 0 in a trimmed CSV"
    assert int(rows[0][0]) == 57_403_264 + 1728, rows[0][0]
    data = np.fromfile(st + "_data.xdat", dtype=np.float32).reshape(n, 8)
    eeg = np.array([float(r[3]) for r in rows])
    assert np.max(np.abs(eeg - data[1728:5728, 0])) <= 0.0005 + 1e-6
    w = rep["window"]
    assert w["missing_at_start_s"] == 0 and w["missing_at_end_s"] == 0, w
    assert rep["n_samples"] == 4000 and rep["file"]["n_samples"] == n


def t_window_shortfall_is_recorded_not_hidden(tmp):
    """A window starting before the recording exports what exists and says so."""
    _, st, n = stripped_recording(tmp)
    sp = spec_for(("A1",)); sp["window"] = {"start_kst": "2026-09-21 00:17:30",
                                            "end_kst": "2026-09-21 00:17:40"}
    rep = run_export(st, tmp / "out", spec=sp)
    assert rep["window"]["missing_at_start_s"] == 4.272, rep["window"]
    assert rep["n_samples"] == 5728, rep["n_samples"]


def t_window_is_found_by_the_counter_across_a_gap(tmp):
    _, st, n = stripped_recording(tmp)
    ts = np.fromfile(st + "_timestamp.xdat", dtype=np.int64)
    ts[3000:] += 1000                     # one second never delivered
    ts.tofile(st + "_timestamp.xdat")
    sp = spec_for(("A1",)); sp["window"] = {"start_kst": "2026-09-21 00:17:40",
                                            "end_kst": "2026-09-21 00:17:42"}
    run_export(st, tmp / "out", spec=sp)
    _, rows = read_csv(tmp / "out" / "20260921_HLBSSL31_R.csv")
    assert rows[0][2] == "2026-09-21 00:17:40.000", rows[0][2]
    assert len(rows) == 2000, len(rows)


def t_a_changed_window_is_re_exported(tmp):
    _, st, _ = stripped_recording(tmp)
    sp = spec_for(("A1",)); sp["window"] = {"start_kst": "2026-09-21 00:17:36",
                                            "end_kst": "2026-09-21 00:17:40"}
    run_export(st, tmp / "out", spec=sp)
    sp["window"]["end_kst"] = "2026-09-21 00:17:38"
    rep = run_export(st, tmp / "out", spec=sp)
    _, rows = read_csv(tmp / "out" / "20260921_HLBSSL31_R.csv")
    assert len(rows) == 2000, "a CSV for the old window was kept as if it were the new one"


def t_verify_catches_a_nan_mismatch(tmp):
    _, st, n = stripped_recording(tmp)
    run_export(st, tmp / "out")
    p = tmp / "out" / "20260921_HLBSSL31_R.csv"
    with open(p, "rb") as fh:
        fh.readline(); off = fh.tell()
    ts0 = 57_403_264
    try:
        E.verify_csv(p, n=n, first_raw=ts0, last_raw=ts0 + n - 1, roles=["EEG", "EMG"],
                     spot={0: off}, expect={0: [float("nan"), 0.0]})
    except E.ExportFailed:
        return
    raise AssertionError("a NaN in the xdat was accepted against a number in the CSV")


def t_verify_catches_a_corrupt_row(tmp):
    _, st, n = stripped_recording(tmp)
    run_export(st, tmp / "out")
    p = tmp / "out" / "20260921_HLBSSL31_R.csv"
    lines = p.read_text().splitlines(keepends=True)
    lines.insert(10, lines[10])           # one duplicated row
    p.write_text("".join(lines))
    try:
        E.verify_csv(p, n=n, first_raw=57_403_264, last_raw=57_403_264 + n - 1,
                     roles=["EEG", "EMG"], spot={}, expect={})
    except E.ExportFailed:
        return
    raise AssertionError("an extra row was not caught")


# --------------------------------------------------------------------------- #
# MUST REFUSE
# --------------------------------------------------------------------------- #

def refusals(tmp):
    raw, st, _ = stripped_recording(tmp)
    bad = spec_for(); bad["mice"][0]["columns"]["eeg"] = "C/1"
    expect("a label not in the file is refused", lambda: run_export(st, tmp / "o1", spec=bad),
           E.ExportRefused, "C/1")
    dup = spec_for(); dup["mice"][1]["file_base"] = dup["mice"][0]["file_base"]
    expect("two mice with one file base are refused",
           lambda: run_export(st, tmp / "o2", spec=dup), E.ExportRefused, "share")
    expect("a raw (unstripped) recording is refused",
           lambda: run_export(raw, tmp / "o3"), E.ExportRefused, "provenance")
    sp = spec_for(("A1",)); sp["window"] = {"start_kst": "2026-09-25 09:00",
                                            "end_kst": "2026-09-26 09:00"}
    expect("a window the recording does not touch is refused",
           lambda: run_export(st, tmp / "o8", spec=sp), E.ExportRefused, "overlap")
    expect("no mice is refused", lambda: run_export(st, tmp / "o4", spec={"mice": []}),
           E.ExportRefused, "no mice")
    expect("not enough disk is refused",
           lambda: E.export(st, spec_for(), tmp / "o5", progress=None, min_free_gb=1e9),
           E.ExportRefused, "free")

    # a recording still being written must not be exported alongside
    live = Path(raw).parent / "allego_1__uid0930-09-00-00_data.xdat"
    live.write_bytes(b"x")
    expect("--require-idle refuses while another recording is being written",
           lambda: run_export(st, tmp / "o6", require_idle=True, source_base=raw),
           E.ExportRefused, "busy")
    live.unlink()

    # a sidecar whose kept_labels disagree with the column count
    m = json.loads(Path(st + ".xdat.json").read_text())
    m["status"]["dataset_provenance"][-1]["kept_labels"] = m["status"]["dataset_provenance"][-1]["kept_labels"][:-1]
    Path(st + ".xdat.json").write_text(json.dumps(m))
    expect("kept_labels that disagree with the file are refused",
           lambda: run_export(st, tmp / "o7"), E.ExportRefused, "kept_labels")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="csv-test-"))
    old_raw = SC.PATHS.RAW_ROOT
    try:
        print("MUST PASS")
        for fn in (t_columns_and_rows, t_values_are_the_right_channels, t_timestamps,
                   t_a_gap_in_the_counter_shows_as_a_jump, t_report_and_sha,
                   t_rerun_is_a_noop, t_a_tampered_csv_is_rewritten, t_subset_of_mice,
                   t_window_trims_to_the_requested_times,
                   t_window_shortfall_is_recorded_not_hidden,
                   t_window_is_found_by_the_counter_across_a_gap,
                   t_a_changed_window_is_re_exported,
                   t_verify_catches_a_nan_mismatch, t_verify_catches_a_corrupt_row):
            d = Path(tempfile.mkdtemp(dir=tmp))
            check(fn.__name__, lambda fn=fn, d=d: fn(d))
        print("\nMUST REFUSE")
        d = Path(tempfile.mkdtemp(dir=tmp))
        SC.PATHS.RAW_ROOT = d             # rig_is_busy looks here
        refusals(d)
    finally:
        SC.PATHS.RAW_ROOT = old_raw
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for name, tb in FAIL:
        print(f"\n--- {name} ---\n{tb}")
    return 1 if FAIL or not PASS else 0


if __name__ == "__main__":
    raise SystemExit(main())

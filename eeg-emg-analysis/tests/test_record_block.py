"""qc/record_block.py must refuse before touching Allego, and must never stop a recording it did not start.

Why: a start or stop with no port acts on every port (Allego 4, radiens-core 0.1.2). A trial block that overlaps a console run, or that calls stop()
after its own start was refused, would end someone else's recording (2026-10-02).
"""
import datetime as dt
import io
import json
import sys
import types
import urllib.error

import pytest

from qc import record_block as RB

KST = RB.KST
NOW = dt.datetime(2026, 10, 3, 10, 0, tzinfo=KST)


def test_console_time_spellings():
    assert RB.parse_when("2026-10-02T00:16:55Z") == dt.datetime(2026, 10, 2, 9, 16, 55, tzinfo=KST)
    assert RB.parse_when("2026-10-02T21:02:00+09:00") == dt.datetime(2026, 10, 2, 21, 2, tzinfo=KST)
    assert RB.parse_when("2026-09-30T19:15") == dt.datetime(2026, 9, 30, 19, 15, tzinfo=KST)
    assert RB.parse_when(None) is None


@pytest.mark.parametrize("state", sorted(RB.BUSY))
def test_any_unfinished_run_blocks(state):
    assert RB.console_conflicts([{"run_id": "x", "state": state}], NOW, 10)


@pytest.mark.parametrize("state", ["DONE", "ABORTED", "DRAFT", "FAILED_UPLOAD"])
def test_finished_runs_do_not_block(state):
    assert RB.console_conflicts([{"run_id": "x", "state": state}], NOW, 10) == []


def test_scheduled_run_blocks_only_inside_block_plus_margin():
    soon = {"run_id": "s", "state": "SCHEDULED", "scheduled_start": "2026-10-03T10:20:00+09:00"}
    later = {"run_id": "l", "state": "SCHEDULED", "scheduled_start": "2026-10-03T13:00:00+09:00"}
    unknown = {"run_id": "u", "state": "SCHEDULED", "scheduled_start": None}
    assert RB.console_conflicts([soon], NOW, 10)          # 10 + 15 min margin reaches 10:25
    assert RB.console_conflicts([later], NOW, 10) == []
    assert RB.console_conflicts([unknown], NOW, 10)       # unknown start: refuse


def test_dest_inside_radix_data_refused(tmp_path):
    with pytest.raises(SystemExit, match="refusing"):
        RB.check_dest(RB.DATA_ROOT / "trial")
    assert RB.check_dest(tmp_path) == tmp_path.resolve()


def _console(monkeypatch, runs=None, fail=False):
    def fake_urlopen(url, timeout=0):
        if fail:
            raise urllib.error.URLError("connection refused")
        return io.BytesIO(json.dumps({"runs": runs or []}).encode())
    monkeypatch.setattr(RB.urllib.request, "urlopen", fake_urlopen)


def test_refuses_on_live_console_run_before_importing_allego(monkeypatch, tmp_path):
    monkeypatch.delitem(sys.modules, "allego", raising=False)
    _console(monkeypatch, [{"run_id": "8f84", "state": "RECORDING"}])
    with pytest.raises(SystemExit, match="8f84 is RECORDING"):
        RB.main([str(tmp_path), "T1-A1_test", "5"])
    assert "allego" not in sys.modules


def test_refuses_when_console_unreachable(monkeypatch, tmp_path):
    monkeypatch.delitem(sys.modules, "allego", raising=False)
    _console(monkeypatch, fail=True)
    with pytest.raises(SystemExit, match="cannot ask the recording console"):
        RB.main([str(tmp_path), "T1-A1_test", "5"])
    assert "allego" not in sys.modules


class FakeAllego(types.ModuleType):
    """Stands in for eeg-recorder/backend/allego.py; records what was called."""

    class PreflightFailed(RuntimeError):
        pass

    def __init__(self, stream_step=10.0, start_raises=False):
        super().__init__("allego")
        self.calls, self.stream_step, self.start_raises, self.t = [], stream_step, start_raises, 100.0

    def preflight(self, dest, min_free_gb=0):
        self.calls.append("preflight")
        return {"free_gb": 600, "status": {"system_mode": "XDAQ_CORE_REC", "sample_freq": 1000.0}}

    def _client(self):
        outer = self

        class C:
            def start_streaming(self):
                outer.calls.append("start_streaming")

            def get_status(self):
                outer.t += outer.stream_step
                return types.SimpleNamespace(streaming=types.SimpleNamespace(primary_cache_t_range=[0.0, outer.t]))
        return C()

    def start(self, dest, base_name="", settle_s=0, min_free_gb=0):
        self.calls.append("start")
        if self.start_raises:
            raise self.PreflightFailed("a recording is ALREADY running (ON) -- refusing to disturb it")
        name = base_name + "_portA_0__uid1003-10-00-00"
        return {"base_name": name, "base_path": f"{dest}/{name}",
                "data_path": f"{dest}/{name}_data.xdat",
                "port_files": {"A": {"base_name": name, "data_path": f"{dest}/{name}_data.xdat"}}}

    def confirm_growing(self, path, window_s=40):
        self.calls.append("confirm"); return {"growing": True, "gb_per_h": 0.48}

    def stop(self, ports, stop_streaming=True):
        # allego.stop() requires explicit ports (2026-10-28): only the ones this block started
        assert ports == ["A"], ports
        self.calls.append("stop"); return {"before": {"A": "ON"}, "after": {"A": "OFF"}}


def _fake(monkeypatch, **kw):
    fake = FakeAllego(**kw)
    monkeypatch.setitem(sys.modules, "allego", fake)
    monkeypatch.setattr(RB.time, "sleep", lambda s: None)
    clock = iter([0.0, 10.0])                                  # stream_rate: 10 s of wall clock
    monkeypatch.setattr(RB.time, "monotonic", lambda: next(clock))
    _console(monkeypatch, [{"run_id": "old", "state": "DONE"}])
    return fake


def test_start_refused_midway_never_stops_someone_elses_recording(monkeypatch, tmp_path):
    fake = _fake(monkeypatch, start_raises=True)
    with pytest.raises(FakeAllego.PreflightFailed):
        RB.main([str(tmp_path), "T1-A1_test", "5"])
    assert "start" in fake.calls and "stop" not in fake.calls
    assert "PreflightFailed" in (tmp_path / "TRIAL_LOG.tsv").read_text()


def test_normal_block_records_stops_and_logs(monkeypatch, tmp_path):
    fake = _fake(monkeypatch)
    assert RB.main([str(tmp_path), "T1-A1_test", "5", "--note", "direct USB"]) == 0
    assert fake.calls[-3:] == ["start", "confirm", "stop"]
    rows = (tmp_path / "TRIAL_LOG.tsv").read_text().splitlines()
    assert rows[0].startswith("start\tstop\tname") and "direct USB" in rows[1] and "\t1.000\t" in rows[1]


def test_stream_running_30x_is_refused_before_recording(monkeypatch, tmp_path):
    fake = _fake(monkeypatch, stream_step=300.0)
    with pytest.raises(SystemExit, match="30.00x"):
        RB.main([str(tmp_path), "T1-A1_test", "5"])
    assert "start" not in fake.calls

#!/usr/bin/env python3
"""Contract for allego.py on Allego 4.1.2 / radiens-core 0.1.2 (2026-10-28).

Drives allego.py against a FAKE AllegoClient that behaves the way the rig was
measured to behave on 2026-10-28 (per-port start/stop, config refused while any
port records, a second start on an ON port silently accepted, impedance refused
while streaming, restart resets the rate to 30 kHz). It uses the real
radiens_core enums and RecordingConfig, so an IntEnum compared as a string, or a
frozen model mutated in place, fails here instead of on the rig. Nothing here
touches the live server, and the clock is virtual, so the suite runs in seconds.

    python3 test_allego.py
"""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parent))

import allego
from radiens_core.models.ports import Port, PortChannelCount
from radiens_core.models.signals import SignalType
from radiens_core.models.status import (BackboneMode, DataRecordingType,
                                        RecordingConfig, RecordMode, StreamMode)

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
# a virtual clock, and a fake Allego 4.1.2
# --------------------------------------------------------------------------- #
class Clock:
    def __init__(self):
        self.t = 1000.0

    def sleep(self, s):
        self.t += s

    def monotonic(self):
        return self.t

    def time(self):
        return self.t


CLOCK = Clock()
allego.time = NS(sleep=CLOCK.sleep, monotonic=CLOCK.monotonic, time=CLOCK.time)
allego.server_running = lambda: True


class FakeClient:
    def __init__(self, dest: Path):
        self.calls: list[str] = []
        self.on: set[str] = set()
        self.streaming = True
        self.fs = 1000.0
        self.mode = BackboneMode.XDAQ_CORE_REC
        self.rate = 1.0                      # stream seconds per wall second
        self.pos, self.last = 0.0, CLOCK.t   # stream time, accumulated at self.rate
        self.counts = {"A": 32, "B": 32, "C": 32, "D": 32}
        self.n = {}
        self.cfg = RecordingConfig(base_file_name="allego", base_file_path=str(dest),
                                   split_files_by_port=False)
        self.make_files = True
        self.server_version = (5, 8, 0)

    # -- reads
    def get_status(self):
        rec = {f"record_mode_port_{p.lower()}": RecordMode.ON if p in self.on else RecordMode.OFF
               for p in "ABCD"}
        if self.streaming:
            self.pos += (CLOCK.t - self.last) * self.rate
        self.last = CLOCK.t
        end = self.pos if self.streaming else 0.0
        return NS(streaming=NS(stream_mode=StreamMode.ON if self.streaming else StreamMode.OFF,
                               primary_cache_t_range=[max(0.0, end - 10), end]),
                  recording=NS(record_mode=RecordMode.ON if self.on else RecordMode.OFF,
                               active_filename="allego_0__uid", duration=0.0, error="", **rec),
                  ports=[PortChannelCount(port=Port[p], channel_count=n)
                         for p, n in self.counts.items()])

    def get_core_config(self):
        return NS(backbone_mode=self.mode, base_samp_freq=self.fs)

    def get_recording_config(self):
        return self.cfg

    def get_channel_metadata(self):
        ntv = list(range(128))
        return NS(sig_map={SignalType.AMP: NS(ntv=ntv)},
                  selected_sig_map={SignalType.AMP: NS(ntv=[0, 1, 32, 33])},
                  ports={SignalType.AMP: [Port(i // 32) for i in ntv]},
                  site_nums={SignalType.AMP: [i % 32 + 1 for i in ntv]})

    # -- writes
    def update_recording_config(self, cfg):
        self.calls.append("update_recording_config")
        if self.on:
            raise RuntimeError("SetConfigRecording: recorder::No setting file name "
                               "while recording is on")
        self.cfg = cfg

    def start_streaming(self):
        self.calls.append("start_streaming")
        if not self.streaming:                # clears the live cache
            self.streaming, self.pos, self.last = True, 0.0, CLOCK.t

    def stop_streaming(self):
        self.calls.append("stop_streaming")
        if self.on:
            raise RuntimeError("recording is on")
        self.streaming = False

    def start_recording(self, *, port=None):
        assert port is not None, "start_recording() without a port records EVERY port"
        p = port.upper()
        self.calls.append(f"start_recording({p})")
        if p in self.on:
            return                            # measured: silently accepted, no new file
        self.on.add(p)
        if self.make_files:
            n = self.n.get(p, -1) + 1
            self.n[p] = n
            name = f"{self.cfg.base_file_name}_port{p}_{n}__uid1028-18-{n:02d}-00_data.xdat"
            (Path(self.cfg.base_file_path) / name).write_bytes(b"")

    def stop_recording(self, *, port=None):
        assert port is not None, "stop_recording() without a port stops EVERY port"
        self.calls.append(f"stop_recording({port.upper()})")
        self.on.discard(port.upper())

    def get_intan_impedance(self, port):
        self.calls.append(f"get_intan_impedance({port})")
        if self.streaming:
            raise RuntimeError("Z_measure attempted during data acq")
        return NS(measurements=[NS(ntv_chan_idx=i, magnitude_ohm=1000.0 * (i + 1),
                                   phase_deg=-10.0) for i in range(128)])

    def restart(self, *, mode):
        self.calls.append(f"restart({mode.name})")
        if self.streaming:
            raise RuntimeError("streaming is on")
        self.mode, self.fs = mode, 30000.0    # measured: restart resets to 30 kHz

    def update_core_config(self, *, samp_freq=None):
        self.calls.append(f"update_core_config({samp_freq})")
        if self.streaming:
            raise RuntimeError("streaming is on")
        self.fs = samp_freq

    def scan_ports(self):
        self.calls.append("scan_ports")
        if self.streaming:
            raise RuntimeError("streaming is on")

    def close(self):
        pass


def fresh(tmp) -> FakeClient:
    dest = Path(tempfile.mkdtemp(dir=tmp))
    c = FakeClient(dest)
    allego._CLIENT = c
    allego._RATE.clear()
    return c


def quiet(**kw):
    return dict(settle_s=0.0, min_free_gb=0.0, progress=None, **kw)


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #
def t_status_shape_and_rate(tmp):
    c = fresh(tmp)
    st = allego.status()
    assert st["reachable"] and st["system_mode"] == "XDAQ_CORE_REC", st
    assert st["sample_freq"] == 1000.0 and st["streaming"] == "ON" and st["recording"] == "OFF"
    assert st["ports"]["A"] == {"channels": 32, "recording": False, "run_id": None,
                                "owner": None, "file": None, "bytes": None}, st["ports"]
    assert allego.port_counts(st) == {"A": 32, "B": 32, "C": 32, "D": 32}
    assert st["measured_rate"] is None, "one poll cannot measure a rate"
    assert any("split_files_by_port is False" in p for p in st["problems"])
    assert st["healthy"] is False
    c.cfg = c.cfg.model_copy(update={"split_files_by_port": True})
    CLOCK.sleep(6)
    st = allego.status()
    assert st["measured_rate"] == 1.0 and st["problems"] == [] and st["healthy"], st
    # the rate label lies (2026-09-30): 30x
    c.rate = 30.0
    CLOCK.sleep(6)
    st = allego.status()
    assert st["measured_rate"] > 20 and any("real time" in p for p in st["problems"]), st
    # a dead stream (2026-10-28): ON, t_range stuck
    c.rate = 0.0
    CLOCK.sleep(6)
    st = allego.status()
    assert st["measured_rate"] == 0.0
    assert any("not advancing" in p for p in st["problems"]), st["problems"]


def t_status_flags_fresh_launch(tmp):
    """A fresh Allego 4.1.2 launch: 30 kHz, split False (2026-10-28)."""
    c = fresh(tmp)
    c.fs = 30000.0
    st = allego.status()
    probs = " ".join(st["problems"])
    assert "30000.0 Hz" in probs and "split_files_by_port is False" in probs, probs


def t_status_unreachable(tmp):
    class Dead:
        def get_status(self):
            raise ConnectionError("failed to connect to all addresses")
        def close(self):
            pass
    allego._CLIENT = Dead()
    st = allego.status()
    assert st["reachable"] is False and "failed to connect" in st["error"]
    assert allego._CLIENT is None, "a failed client must be dropped so the next poll reconnects"


# --------------------------------------------------------------------------- #
# config, start, stop
# --------------------------------------------------------------------------- #
def t_ensure_config_sets_when_idle(tmp):
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path) / "run1"
    allego.ensure_config(dest, "allego")
    assert c.cfg.base_file_path == str(dest) and c.cfg.split_files_by_port is True
    assert c.cfg.recording_type == DataRecordingType.CONTINUOUS and dest.is_dir()


def t_ensure_config_verifies_when_busy(tmp):
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path)
    allego.ensure_config(dest)
    c.on.add("B")                                     # someone else records B
    allego.ensure_config(dest)                        # same config: fine, unchanged
    assert c.calls.count("update_recording_config") == 1, c.calls
    try:
        allego.ensure_config(dest / "elsewhere")
    except allego.PreflightFailed as exc:
        assert "cannot be changed" in str(exc) and "base path" in str(exc), exc
    else:
        raise AssertionError("a different path was accepted while B records")
    assert c.calls.count("update_recording_config") == 1, "must not even try to set it"


def t_start_discovers_each_new_port_file(tmp):
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path)
    # an old file of the same port must not be mistaken for the new one
    (dest / "allego_portA_7__uid1027-09-00-00_data.xdat").write_bytes(b"old")
    info = allego.start(dest, ["A", "C"], **quiet())
    pf = info["port_files"]
    assert sorted(pf) == ["A", "C"], pf
    assert pf["A"]["base_name"] == "allego_portA_0__uid1028-18-00-00", pf
    assert Path(pf["C"]["data_path"]).exists() and "_portC_" in pf["C"]["data_path"]
    assert info["data_path"] == pf["A"]["data_path"] and info["mode"] == "ON"
    assert info["ports"] == {"A": 32, "B": 32, "C": 32, "D": 32}
    assert "start_streaming" not in c.calls, "streaming was on: must not be touched"
    assert c.cfg.split_files_by_port is True


def t_start_beside_a_recording_port(tmp):
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path)
    allego.start(dest, ["B"], **quiet())
    c.calls.clear()
    info = allego.start(dest, ["A"], **quiet())
    assert sorted(c.on) == ["A", "B"] and list(info["port_files"]) == ["A"]
    assert "update_recording_config" not in c.calls, "config is verified, not set, while B records"
    assert "start_streaming" not in c.calls and "stop_streaming" not in c.calls


def t_start_skips_a_port_that_enumerates_nothing(tmp):
    c = fresh(tmp)
    c.counts["B"] = 0
    info = allego.start(Path(c.cfg.base_file_path), ["A", "B"], **quiet())
    assert list(info["port_files"]) == ["A"] and info["skipped_ports"] == ["B"], info
    assert c.on == {"A"}


def t_failed_start_stops_only_its_own_ports(tmp):
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path)
    allego.start(dest, ["B"], **quiet())              # another run's port
    c.make_files = False                              # the new files never appear
    c.calls.clear()
    try:
        allego.start(dest, ["A", "C"], **quiet())
    except allego.AllegoError as exc:
        assert "no new" in str(exc), exc
    else:
        raise AssertionError("start without files was accepted")
    assert c.on == {"B"}, f"B must still record, on={c.on}"
    stops = [x for x in c.calls if x.startswith("stop_recording")]
    assert sorted(stops) == ["stop_recording(A)", "stop_recording(C)"], c.calls
    assert "stop_streaming" not in c.calls, "B still records: streaming must stay on"


def t_stop_streaming_only_when_last_port_stops(tmp):
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path)
    allego.start(dest, ["A"], **quiet()); allego.start(dest, ["B"], **quiet())
    r = allego.stop(["A"])
    assert r["before"] == {"A": "ON"} and r["after"] == {"A": "OFF"}
    assert c.streaming and not r["streaming_stopped"]
    r = allego.stop(["B"])
    assert not c.streaming and r["streaming_stopped"]
    allego.stop(["B"])                                # already stopped: safe, no call
    assert c.calls.count("stop_recording(B)") == 1, c.calls


# --------------------------------------------------------------------------- #
# impedance, restart
# --------------------------------------------------------------------------- #
def t_impedance_labels_and_streaming_restored(tmp):
    c = fresh(tmp)
    res = allego.impedance("b")
    assert res["port"] == "B" and len(res["channels"]) == 32, len(res["channels"])
    first = res["channels"][0]
    # ntv 32 is port_B_32, site 1 -> B/1 (live metadata read 2026-10-28)
    assert first == {"ntv_chan_idx": 32, "label": "B/1", "kohm": 33.0,
                     "phase_deg": -10.0}, first
    assert res["channels"][-1]["label"] == "B/32"
    assert c.streaming, "streaming was on before; it must be on after"
    assert c.calls.index("stop_streaming") < c.calls.index("get_intan_impedance(b)")


def t_impedance_and_restart_refused_while_recording(tmp):
    c = fresh(tmp)
    allego.start(Path(c.cfg.base_file_path), ["A"], **quiet())
    c.calls.clear()
    for fn in (lambda: allego.impedance("C"), allego.restart):
        try:
            fn()
        except allego.PreflightFailed as exc:
            assert "recording" in str(exc), exc
        else:
            raise AssertionError("rig-wide operation allowed while a port records")
    assert c.on == {"A"} and c.calls == [], c.calls


def t_restart_keeps_mode_and_restores_1000hz(tmp):
    c = fresh(tmp)
    c.mode = BackboneMode.XDAQ_CORE_REC
    res = allego.restart()
    order = [x for x in c.calls if not x.startswith("start_recording")]
    assert order == ["stop_streaming", "restart(XDAQ_CORE_REC)",
                     "update_core_config(1000.0)", "scan_ports",
                     "update_recording_config", "start_streaming"], order
    assert res["before"]["system_mode"] == res["after"]["system_mode"] == "XDAQ_CORE_REC"
    assert res["after"]["sample_freq"] == 1000.0 and res["after"]["measured_rate"] == 1.0
    assert res["after"]["split_files_by_port"] is True


def t_restart_fails_loudly_on_a_dead_stream(tmp):
    c = fresh(tmp)
    c.rate = 0.0
    try:
        allego.restart()
    except allego.AllegoError as exc:
        assert "real time" in str(exc), exc
    else:
        raise AssertionError("a dead stream after restart was accepted")


# --------------------------------------------------------------------------- #
# regressions from the 2026-10-28 review
# --------------------------------------------------------------------------- #
def t_a_failed_poll_never_closes_a_shared_client(tmp):
    """Review fix 2: closing the pool broke every other thread holding it."""
    closed = []

    class Flaky:
        def get_status(self):
            raise ConnectionError("blip")
        def close(self):
            closed.append(1)
    held = Flaky()
    allego._CLIENT = held
    allego.status()
    assert allego._CLIENT is None and closed == [], "the shared client was closed"


def t_stop_tries_every_port_then_raises_once(tmp):
    """Review fix 3: one bad port must not leave the others recording."""
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path)
    allego.start(dest, ["A", "B"], **quiet())
    real = c.stop_recording

    def bad(*, port=None):
        if port.upper() == "A":
            raise RuntimeError("A refused")
        real(port=port)
    c.stop_recording = bad
    try:
        allego.stop(["A", "B"])
    except allego.AllegoError as exc:
        assert "port A" in str(exc), exc
    else:
        raise AssertionError("an error on A was swallowed")
    assert "B" not in c.on, "B was never tried after A failed"


def t_a_port_that_goes_on_after_preflight_is_not_touched(tmp):
    """Review fix 5: a port someone else started since preflight is refused
    without being engaged, so the cleanup cannot stop their recording."""
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path)
    allego.ensure_config(dest)
    orig = allego.preflight

    def pf(*a, **kw):
        out = orig(*a, **kw)
        c.on.add("C")                                 # another start wins the race
        return out
    allego.preflight = pf
    try:
        allego.start(dest, ["A", "C"], **quiet())
    except allego.PreflightFailed as exc:
        assert "port C" in str(exc), exc
    else:
        raise AssertionError("a port that went ON was engaged")
    finally:
        allego.preflight = orig
    assert "C" in c.on, "someone else's port C was stopped"
    assert "stop_recording(C)" not in c.calls and "start_recording(C)" not in c.calls, c.calls
    assert "A" not in c.on, "A was engaged by this call and must be stopped"


def t_start_measures_the_rate_when_the_poll_has_none(tmp):
    """Review fix 10: no measured_rate yet -> measure ~5 s, refuse if not ~1.0x."""
    c = fresh(tmp)
    c.rate = 30.0
    try:
        allego.start(Path(c.cfg.base_file_path), ["A"], **quiet())
    except allego.PreflightFailed as exc:
        assert "30.00x" in str(exc), exc
    else:
        raise AssertionError("recorded on a 30x stream")
    assert not any(x.startswith("start_recording") for x in c.calls), c.calls
    c.rate = 1.0
    allego._RATE.clear()                              # the poll's cached 30x reading
    info = allego.start(Path(c.cfg.base_file_path), ["A"], **quiet())
    assert info["measured_rate"] == 1.0, info


def t_stop_requires_ports(tmp):
    """Review fix 11: there is no 'stop every port' default any more."""
    fresh(tmp)
    for bad in (None, []):
        try:
            allego.stop(bad)
        except ValueError:
            continue
        raise AssertionError(f"stop({bad!r}) was accepted")


def refusals(tmp):
    c = fresh(tmp)
    dest = Path(c.cfg.base_file_path)
    allego.start(dest, ["A"], **quiet())
    n_files = len(list(dest.glob("*_data.xdat")))
    expect("refuse: a second start on a port that is already ON",
           lambda: allego.start(dest, ["A"], **quiet()),
           allego.PreflightFailed, "ALREADY recording")
    assert len(list(dest.glob("*_data.xdat"))) == n_files
    c.mode = BackboneMode.XDAQ_ONE_REC
    expect("refuse: the old XDAQ_ONE_REC mode",
           lambda: allego.preflight(dest, ["B"], min_free_gb=0),
           allego.PreflightFailed, "expected XDAQ_CORE_REC")
    c.mode, c.fs = BackboneMode.XDAQ_CORE_REC, 30000.0
    expect("refuse: 30 kHz",
           lambda: allego.preflight(dest, ["B"], min_free_gb=0),
           allego.PreflightFailed, "30000.0 Hz")
    c.fs = 1000.0
    c.counts = {"A": 32, "B": 0, "C": 0, "D": 0}
    expect("refuse: no requested port enumerates",
           lambda: allego.preflight(dest, ["B", "C"], min_free_gb=0),
           allego.PreflightFailed, "enumerates any channels")


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="allego-test-")
    print("ALLEGO (fake client)")
    for fn in (t_status_shape_and_rate, t_status_flags_fresh_launch, t_status_unreachable,
               t_ensure_config_sets_when_idle, t_ensure_config_verifies_when_busy,
               t_start_discovers_each_new_port_file, t_start_beside_a_recording_port,
               t_start_skips_a_port_that_enumerates_nothing,
               t_failed_start_stops_only_its_own_ports,
               t_stop_streaming_only_when_last_port_stops,
               t_impedance_labels_and_streaming_restored,
               t_impedance_and_restart_refused_while_recording,
               t_restart_keeps_mode_and_restores_1000hz,
               t_restart_fails_loudly_on_a_dead_stream,
               t_a_failed_poll_never_closes_a_shared_client,
               t_stop_tries_every_port_then_raises_once,
               t_a_port_that_goes_on_after_preflight_is_not_touched,
               t_start_measures_the_rate_when_the_poll_has_none, t_stop_requires_ports):
        check(fn.__name__, lambda fn=fn: fn(tmp))
    print("\nMUST REFUSE")
    refusals(tmp)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

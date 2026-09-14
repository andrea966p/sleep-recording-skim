#!/usr/bin/env python3
"""Contract for settings_store.py -- what the web form is allowed to change.

A recording setting says which site carries which signal. A wrong one records the
wrong channels and is discovered after the animals are done, so this module is
mostly refusals and they are what gets tested.

TWO PROPERTIES MATTER MOST, and each has a test that would fail loudly:
  - a change that would not load NEVER reaches disk, so the service cannot be
    left unable to start by a form submission
  - the curated config is never written, so the hand-written provenance in
    users.yaml survives every UI action

    python3 test_settings_store.py
"""
from __future__ import annotations

import functools
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import presets as P
import settings_store as SS

PASS, FAIL = [], []
CURATED = P.CONFIG.read_text()          # the file that must never change


def check(name, fn):
    try:
        fn()
    except Exception:
        FAIL.append((name, traceback.format_exc()))
        print(f"  FAIL  {name}")
    else:
        PASS.append(name)
        print(f"  ok    {name}")


def expect(name, fn, want=""):
    def run():
        try:
            fn()
        except (SS.SettingsRefused, P.PresetError) as e:
            if want and want.lower() not in str(e).lower():
                raise AssertionError(f"wrong reason: {e}\nwanted {want!r}")
            return
        raise AssertionError("NOT REFUSED")
    check(name, run)


class FakeStore:
    """Just the two methods settings_store asks about."""
    def __init__(self, runs=()):
        self._runs = list(runs)

    def active(self):
        for r in self._runs:
            if r.state in ("STARTING", "RECORDING", "STOPPING"):
                return r
        return None

    def list(self, limit=100, states=None):
        return self._runs


class FakeRun:
    def __init__(self, run_id, state, setting="", preset=""):
        self.run_id, self.state, self.preset = run_id, state, preset
        self.layout = {"setting": setting} if setting else {}


def sandbox(fn):
    """Run with CUSTOM and the audit log pointed at a throwaway directory."""
    @functools.wraps(fn)                 # keep the name, or the output reads "run"
    def run():
        d = Path(tempfile.mkdtemp(prefix="settings-"))
        old_c, old_a, old_n = P.CUSTOM, SS.AUDIT, set(P.CUSTOM_NAMES)
        P.CUSTOM = d / "custom.yaml"
        SS.AUDIT = d / "audit.jsonl"
        try:
            fn(d)
        finally:
            P.CUSTOM, SS.AUDIT = old_c, old_a
            P.CUSTOM_NAMES.clear()
            P.CUSTOM_NAMES.update(old_n)
    return run


# --------------------------------------------------------------------------- #
@sandbox
def t_add_a_setting_and_use_it(d):
    cfg = SS.add_setting(name="eeg_only", label="EEG only",
                         headstage="rhd2216_bipolar", roles={"eeg": 1},
                         store=FakeStore(), who="andrea")
    s = cfg.setting("eeg_only")
    assert s.label == "EEG only" and s.roles == {"eeg": 1}
    assert s.qc_applies
    assert P.CUSTOM.exists()
    # and it resolves into a real layout
    import layout as L
    lay = L.resolve(cfg, "eeg_only", {p: True for p in P.PORTS})
    assert lay.labels_for_slot("A2") == ["A/33"]


@sandbox
def t_the_curated_file_is_never_written(d):
    SS.add_setting(name="x_one", label="X", headstage="rhd2216_bipolar",
                   roles={"a": 1, "b": 2}, store=FakeStore())
    SS.save_layout(name="x_layout", label="XL", setting="x_one",
                   splitters={"A": True}, store=FakeStore())
    SS.delete_layout("x_layout", store=FakeStore())
    SS.delete_setting("x_one", store=FakeStore())
    assert P.CONFIG.read_text() == CURATED, "users.yaml was modified"


@sandbox
def t_a_change_that_would_not_load_never_reaches_disk(d):
    """THE PROPERTY THAT KEEPS THE SERVICE STARTABLE.

    A setting whose sites the floor rule cannot describe, claiming qc: auto, is
    invalid. The validation runs on a candidate file; the real one must be
    untouched afterwards.
    """
    SS.add_setting(name="good_one", label="G", headstage="rhd2216_bipolar",
                   roles={"a": 1}, store=FakeStore())
    before = P.CUSTOM.read_text()
    try:
        SS.add_setting(name="bad_one", label="B", headstage="rhd2216_bipolar",
                       roles={"a": 5, "b": 6}, qc="auto", store=FakeStore())
    except SS.SettingsRefused:
        pass
    else:
        raise AssertionError("NOT REFUSED")
    assert P.CUSTOM.read_text() == before, "a rejected change was written anyway"
    assert P.load().setting("good_one")          # still loads


@sandbox
def t_a_previous_version_is_kept(d):
    SS.add_setting(name="one_a", label="A", headstage="rhd2216_bipolar",
                   roles={"a": 1}, store=FakeStore())
    SS.add_setting(name="two_b", label="B", headstage="rhd2216_bipolar",
                   roles={"a": 1, "b": 2}, store=FakeStore())
    backups = list((P.CUSTOM.parent / SS.BACKUPS).glob("custom.*.yaml"))
    assert backups, "no backup of the replaced version"


@sandbox
def t_every_change_is_audited(d):
    SS.add_setting(name="aud_one", label="A", headstage="rhd2216_bipolar",
                   roles={"a": 1}, store=FakeStore(), who="diane")
    h = SS.history()
    assert h and h[0]["action"] == "add_setting"
    assert h[0]["who"] == "diane" and h[0]["name"] == "aud_one"
    assert h[0]["utc"].endswith("Z")


@sandbox
def t_unipolar_shaped_setting_needs_a_reason(d):
    """Non-contiguous sites are addable -- with `qc: none` and a reason."""
    cfg = SS.add_setting(name="uni_like", label="U", headstage="intan_unipolar_32",
                         roles={"a": 18, "b": 19, "c": 20}, qc="none",
                         qc_reason="unused inputs never characterised",
                         store=FakeStore())
    s = cfg.setting("uni_like")
    assert not s.qc_applies and "characterised" in s.qc_reason


@sandbox
def t_save_and_delete_a_layout(d):
    SS.add_setting(name="lay_s", label="S", headstage="rhd2216_bipolar",
                   roles={"a": 1}, store=FakeStore())
    cfg = SS.save_layout(name="two_split", label="A and C split", setting="lay_s",
                         splitters={"A": True, "C": True}, store=FakeStore())
    t = cfg.template("two_split")
    assert t.splitters == {"A": True, "B": False, "C": True, "D": False}
    cfg = SS.delete_layout("two_split", store=FakeStore())
    assert "two_split" not in cfg.templates


@sandbox
def refusals(d):
    store = FakeStore()
    SS.add_setting(name="base_s", label="S", headstage="rhd2216_bipolar",
                   roles={"a": 1, "b": 2}, store=store)

    expect("refuse: a name that is not a safe key",
           lambda: SS.add_setting(name="No Spaces!", label="x",
                                  headstage="rhd2216_bipolar", roles={"a": 1},
                                  store=store), "lower-case letters")
    expect("refuse: shadowing a curated setting",
           lambda: SS.add_setting(name="eeg_emg", label="x",
                                  headstage="rhd2216_bipolar", roles={"a": 1},
                                  store=store), "already exists")
    expect("refuse: an unknown headstage",
           lambda: SS.add_setting(name="hs_bad", label="x", headstage="nope",
                                  roles={"a": 1}, store=store), "not defined")
    expect("refuse: no roles at all",
           lambda: SS.add_setting(name="empty_s", label="x",
                                  headstage="rhd2216_bipolar", roles={},
                                  store=store), "selects nothing")
    expect("refuse: a site beyond the chip's real channels",
           lambda: SS.add_setting(name="far_s", label="x",
                                  headstage="rhd2216_bipolar", roles={"a": 30},
                                  store=store), "real channels")
    expect("refuse: two roles on one site",
           lambda: SS.add_setting(name="dup_s", label="x",
                                  headstage="rhd2216_bipolar",
                                  roles={"a": 1, "b": 1}, store=store),
           "share a site")
    expect("refuse: qc: none with no reason",
           lambda: SS.add_setting(name="nr_s", label="x",
                                  headstage="intan_unipolar_32",
                                  roles={"a": 18, "b": 19}, qc="none",
                                  store=store), "qc_reason")
    expect("refuse: a role name that would not label a channel",
           lambda: SS.add_setting(name="rn_s", label="x",
                                  headstage="rhd2216_bipolar",
                                  roles={"a b/c": 1}, store=store),
           "letters, digits")

    # --- in-flight guards ---------------------------------------------- #
    recording = FakeStore([FakeRun("r1", "RECORDING")])
    expect("refuse: any change while a run is recording",
           lambda: SS.add_setting(name="mid_s", label="x",
                                  headstage="rhd2216_bipolar", roles={"a": 1},
                                  store=recording), "in flight")
    pending = FakeStore([FakeRun("r2", "UPLOAD_PENDING")])
    expect("refuse: a change while a run is still uploading",
           lambda: SS.add_setting(name="up_s", label="x",
                                  headstage="rhd2216_bipolar", roles={"a": 1},
                                  store=pending), "have not finished")

    # --- deletion guards ------------------------------------------------ #
    expect("refuse: deleting a curated setting",
           lambda: SS.delete_setting("eeg_emg", store=store),
           "curated config")
    expect("refuse: deleting a setting that never existed",
           lambda: SS.delete_setting("ghost_s", store=store), "no recording setting")

    SS.save_layout(name="uses_base", label="L", setting="base_s",
                   splitters={"A": True}, store=store)
    expect("refuse: deleting a setting a layout still uses",
           lambda: SS.delete_setting("base_s", store=store), "uses")

    using = FakeStore([FakeRun("r3", "STOPPED", setting="base_s")])
    expect("refuse: deleting a setting an unfinished run used",
           lambda: SS.delete_setting("base_s", store=using), "have not finished")

    expect("refuse: deleting a curated layout",
           lambda: SS.delete_layout("8mice_eeg_emg", store=store), "curated config")
    expect("refuse: a layout naming an unknown setting",
           lambda: SS.save_layout(name="bad_l", label="x", setting="ghost",
                                  splitters={}, store=store), "unknown recording setting")
    expect("refuse: a duplicate layout name",
           lambda: SS.save_layout(name="uses_base", label="x", setting="base_s",
                                  splitters={}, store=store), "already exists")


def main() -> int:
    print("SETTINGS STORE")
    for fn in (t_add_a_setting_and_use_it, t_the_curated_file_is_never_written,
               t_a_change_that_would_not_load_never_reaches_disk,
               t_a_previous_version_is_kept, t_every_change_is_audited,
               t_unipolar_shaped_setting_needs_a_reason,
               t_save_and_delete_a_layout):
        check(fn.__name__.removeprefix("t_").replace("_", " "), fn)
    print("\nMUST REFUSE")
    refusals()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    assert P.CONFIG.read_text() == CURATED, "users.yaml changed during the suite"
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

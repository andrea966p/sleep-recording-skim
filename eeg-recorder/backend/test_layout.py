#!/usr/bin/env python3
"""Contract for layout.py -- what the rig is declared as, and whether it is true.

A wrong declaration is not a cosmetic error. It decides which channels survive
the strip, and it is discovered after the animals are done. So the enumeration
check must refuse, and the slot maths must be exact.

🔑 WHAT VARIES AND WHAT DOES NOT. Andrea, 2026-09-14: mice on this rig always
share one configuration; what changes is how many are connected and which ports
carry splitters. These tests pin that: one setting per run, per-port splitters,
free occupancy.

    python3 test_layout.py
"""
from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import presets as P
import layout as L

PASS, FAIL = [], []
CFG = P.load()


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


def lay(setting="eeg_emg", **spl) -> L.RigLayout:
    s = {p: spl.get(p, True) for p in L.PORTS}
    return L.resolve(CFG, setting, s)


# --------------------------------------------------------------------------- #
def t_the_three_templates_reproduce_the_old_presets():
    """Nothing an operator does today may get harder or different."""
    a = L.from_template(CFG, "8mice_eeg_emg")
    assert a.slots == ["A1", "A2", "B1", "B2", "C1", "C2", "D1", "D2"]
    assert a.labels() == ["A/1", "A/2", "A/33", "A/34", "B/1", "B/2", "B/33",
                          "B/34", "C/1", "C/2", "C/33", "C/34", "D/1", "D/2",
                          "D/33", "D/34"]
    b = L.from_template(CFG, "8mice_eeg_emg_ecg")
    assert len(b.labels()) == 24 and "A/3" in b.labels() and "A/35" in b.labels()
    c = L.from_template(CFG, "4mice_unipolar_lfp")
    assert c.slots == ["A", "B", "C", "D"]
    assert len(c.labels()) == 24
    assert c.labels()[:6] == ["A/18", "A/19", "A/20", "A/21", "A/22", "A/23"]


def t_splitters_decide_the_slot_grid():
    """The real variable. Splitters on A and C only -> six slots, mixed names."""
    m = lay(A=True, B=False, C=True, D=False)
    assert m.slots == ["A1", "A2", "B", "C1", "C2", "D"], m.slots
    assert m.expected_channels("A") == 64
    assert m.expected_channels("B") == 32
    none = lay(A=False, B=False, C=False, D=False)
    assert none.slots == ["A", "B", "C", "D"]
    assert all(none.expected_channels(p) == 32 for p in L.PORTS)


def t_the_plus32_trap():
    """The second animal on a split port is at /33, never /29."""
    a = lay()
    assert a.labels_for_slot("A1") == ["A/1", "A/2"]
    assert a.labels_for_slot("A2") == ["A/33", "A/34"]
    assert "A/29" not in a.labels()
    ecg = lay("eeg_emg_ecg")
    assert ecg.labels_for_slot("C2") == ["C/33", "C/34", "C/35"]


def t_bare_letter_translates_to_a_position_once():
    """`A` is the operator's name; `A1` is what the analysis side indexes."""
    assert L.RigLayout.to_position("A") == "A1"
    assert L.RigLayout.to_position("A1") == "A1"
    assert L.RigLayout.to_position("D2") == "D2"
    assert L.RigLayout.base_of("A") == 1
    assert L.RigLayout.base_of("A1") == 1
    assert L.RigLayout.base_of("A2") == 33
    # a single-slot port's animal keeps the base-1 sites
    assert lay(A=False).labels_for_slot("A") == ["A/1", "A/2"]


def t_occupancy_is_free():
    """Any number of mice, any slots. This is what actually changes run to run."""
    a = lay()
    assert a.labels(["A1", "C2", "D1"]) == ["A/1", "A/2", "C/33", "C/34",
                                            "D/1", "D/2"]
    assert a.labels(["B2"]) == ["B/33", "B/34"]
    assert len(a.labels(["A1"])) == 2


def t_one_setting_for_every_animal():
    """THE PIN. A layout carries a single setting; no per-port variation exists."""
    m = lay(A=True, B=False, C=True, D=False)
    assert isinstance(m.setting, P.RecordingSetting)
    roles = {tuple(sorted(
        r for r in (m.role_of(s, l) for l in m.labels_for_slot(s)) if r))
        for s in m.slots}
    assert len(roles) == 1, f"slots disagree on roles: {roles}"
    # and the cohort it produces has one role list across every chip
    ports = m.cohort_ports()
    assert ports == {"A": 2, "B": 1, "C": 2, "D": 1}, ports


def t_the_enumeration_check_both_ways():
    real = {"A": 64, "B": 64, "C": 64, "D": 64}
    ok = lay().check(real)
    assert ok["ok"] is True, ok["problems"]

    # declaring no splitter on C when the hardware says 64
    wrong = lay(C=False).check(real)
    assert wrong["ok"] is False
    assert wrong["ports"]["C"]["ok"] is False
    assert wrong["ports"]["A"]["ok"] is True
    msg = " ".join(wrong["problems"])
    assert "port C" in msg and "32" in msg and "64" in msg, msg


def t_a_port_with_nothing_connected_is_named():
    r = lay().check({"A": 64, "B": 64, "C": 64, "D": 0})
    assert r["ok"] is False
    assert "nothing is connected" in " ".join(r["problems"])


def t_unused_ports_are_exempt():
    """Recording on two ports must not be blocked by two empty ones."""
    two = L.resolve(CFG, "eeg_emg", {p: True for p in L.PORTS},
                    ports_used=("A", "B"))
    assert two.slots == ["A1", "A2", "B1", "B2"]
    r = two.check({"A": 64, "B": 64, "C": 0, "D": 0})
    assert r["ok"] is True, r["problems"]
    assert two.cohort_ports() == {"A": 2, "B": 2}


def t_unverified_combination_is_refused_until_confirmed():
    """A splitter with two unipolar headstages has never been recorded here."""
    u = L.resolve(CFG, "eeg_emg_lfp", {p: True for p in L.PORTS})
    r = u.check({"A": 64, "B": 64, "C": 64, "D": 64})
    assert r["ok"] is False
    assert "never been recorded" in " ".join(r["problems"])
    # without splitters the same setting is fine
    v = L.resolve(CFG, "eeg_emg_lfp", {p: False for p in L.PORTS})
    assert v.check({"A": 32, "B": 32, "C": 32, "D": 32})["ok"] is True


def t_cohort_extras_only_for_non_contiguous():
    assert lay().cohort_extras() == {}
    assert lay("eeg_emg_ecg").cohort_extras() == {}
    uni = L.resolve(CFG, "eeg_emg_lfp", {p: False for p in L.PORTS})
    e = uni.cohort_extras()
    assert e["real_channels"] == 32
    assert e["floor"] == "none"
    assert "never recorded" in e["floor_reason"]
    assert e["role_sites"]["eeg_f"] == 21


def refusals():
    expect("refuse: an unknown recording setting",
           lambda: L.resolve(CFG, "nope", {}), P.PresetError, "unknown recording setting")
    expect("refuse: an unknown port in the splitter map",
           lambda: L.resolve(CFG, "eeg_emg", {"Z": True}), L.LayoutError, "unknown port")
    expect("refuse: no port in use",
           lambda: L.resolve(CFG, "eeg_emg", {}, ports_used=()), L.LayoutError, "records nothing")
    expect("refuse: a slot this layout does not have",
           lambda: lay(A=False).labels_for_slot("A2"), L.LayoutError, "not a slot")
    expect("refuse: keeping channels for an unknown slot",
           lambda: lay().labels(["A1", "Q7"]), L.LayoutError, "unknown slot")
    expect("refuse: a slot name that is not a port",
           lambda: L.RigLayout.to_position("Z"), L.LayoutError, "does not name a port")
    expect("refuse: a third slot on a port",
           lambda: L.RigLayout.base_of("A3"), L.LayoutError, "at most two slots")

    # config-level refusals: each must name its fix
    def bad_cfg(body):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(body)
            return f.name

    base = """
nas: {share: S, root: R}
recording_types: [basal]
recording_type_codes: {basal: BSR}
users: {}
headstages:
  hs: {label: H, slots_per_chip: 32, real_channels: 16}
recording_settings:
"""
    expect("refuse: a setting whose sites are not contiguous but claims qc: auto",
           lambda: P.load(bad_cfg(base + "  s: {label: S, headstage: hs, roles: {a: 5, b: 6}, qc: auto}\n")),
           P.PresetError, "declare `qc: none`")
    expect("refuse: qc: none with no reason",
           lambda: P.load(bad_cfg(base + "  s: {label: S, headstage: hs, roles: {a: 5, b: 6}, qc: none}\n")),
           P.PresetError, "qc_reason")
    expect("refuse: two roles on one site",
           lambda: P.load(bad_cfg(base + "  s: {label: S, headstage: hs, roles: {a: 1, b: 1}}\n")),
           P.PresetError, "share a site")
    expect("refuse: a site beyond the chip's real channels",
           lambda: P.load(bad_cfg(base + "  s: {label: S, headstage: hs, roles: {a: 1, b: 20}}\n")),
           P.PresetError, "real channels")
    expect("refuse: a setting naming an unknown headstage",
           lambda: P.load(bad_cfg(base + "  s: {label: S, headstage: nope, roles: {a: 1}}\n")),
           P.PresetError, "not defined")
    expect("refuse: more real channels than slots",
           lambda: P.load(bad_cfg("""
nas: {share: S, root: R}
recording_types: [basal]
recording_type_codes: {basal: BSR}
users: {}
headstages:
  hs: {label: H, slots_per_chip: 16, real_channels: 32}
""")), P.PresetError, "cannot expose more")
    expect("refuse: a layout naming an unknown setting",
           lambda: P.load(bad_cfg(base + """  s: {label: S, headstage: hs, roles: {a: 1}}
layout_templates:
  t: {label: T, setting: nope, splitters: {A: true}}
""")), P.PresetError, "not defined")
    with_user = base.replace("users: {}",
                             "users: {andrea: {default_layout: gone}}")
    expect("refuse: a user whose default layout does not exist",
           lambda: P.load(bad_cfg(with_user + """  s: {label: S, headstage: hs, roles: {a: 1}}
layout_templates:
  t: {label: T, setting: s, splitters: {A: true}}
""")), P.PresetError, "default_layout")


def main() -> int:
    print("RIG LAYOUT")
    for fn in (t_the_three_templates_reproduce_the_old_presets,
               t_splitters_decide_the_slot_grid, t_the_plus32_trap,
               t_bare_letter_translates_to_a_position_once,
               t_occupancy_is_free, t_one_setting_for_every_animal,
               t_the_enumeration_check_both_ways,
               t_a_port_with_nothing_connected_is_named,
               t_unused_ports_are_exempt,
               t_unverified_combination_is_refused_until_confirmed,
               t_cohort_extras_only_for_non_contiguous):
        check(fn.__name__, fn)
    print("\nMUST REFUSE")
    refusals()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

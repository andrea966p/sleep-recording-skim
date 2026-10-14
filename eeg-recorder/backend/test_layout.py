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


def t_a_port_with_nothing_connected_is_named_and_offers_the_way_out():
    """An unplugged headstage must not be a dead end.

    FOUND 2026-09-14 while listing what to bench test. A port with no headstage
    enumerates 0, the check refused, and the page had NO control to say "I am
    not recording on that port" -- `ports_used` existed in the backend and the
    UI never sent it. So the refusal was correct and unescapable.

    ⚠️ The half of this that needs hardware -- Allego actually reporting 0 --
    cannot be exercised on the rig without unplugging a headstage, so it is
    tested here and nowhere else. What WAS verified live is the other half:
    marking a port unused exempts it and drops its slots.
    """
    r = lay().check({"A": 64, "B": 64, "C": 64, "D": 0})
    assert r["ok"] is False
    msg = " ".join(r["problems"])
    assert "nothing is connected" in msg
    # the message must name the escape, or it is a wall
    assert "In use" in msg, msg
    assert "port D" in msg

    # ...and taking that escape works
    three = L.resolve(CFG, "eeg_emg", {p: True for p in L.PORTS},
                      ports_used=("A", "B", "C"))
    ok = three.check({"A": 64, "B": 64, "C": 64, "D": 0})
    assert ok["ok"] is True, ok["problems"]
    assert three.slots == ["A1", "A2", "B1", "B2", "C1", "C2"]
    assert "D" not in three.cohort_ports()
    # an unused port contributes no channels to the strip
    assert not any(l.startswith("D/") for l in three.labels())


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
    assert e["role_sites"]["eeg_f"] == 23        # map corrected 2026-10-14


def t_custom_channels_for_one_run():
    """Channels chosen for a single run, not saved to the config.

    REPORTED 2026-09-14: "when i select custom, i have no way to select the
    allego channels". There genuinely was none -- the only paths were three
    fixed entries or a form in a collapsed panel. A per-run selection goes
    through the SAME validator as a stored one, so it cannot be looser.
    """
    lay = L.resolve(CFG, "", {p: True for p in L.PORTS},
                    custom={"headstage": "rhd2216_bipolar",
                            "roles": {"eeg": 1, "emg": 2, "ecg": 3}})
    assert lay.setting.name == L.CUSTOM
    assert lay.labels_for_slot("A1") == ["A/1", "A/2", "A/3"]
    assert lay.labels_for_slot("A2") == ["A/33", "A/34", "A/35"]
    assert lay.setting.qc == "auto"

    # non-contiguous is allowed WITH a reason, and the +32 shift still applies
    uni = L.resolve(CFG, "", {p: True for p in L.PORTS},
                    custom={"headstage": "rhd2216_bipolar",
                            "roles": {"eeg": 1, "emg": 2, "lfp": 9},
                            "qc": "none", "qc_reason": "never characterised"})
    assert uni.labels_for_slot("A2") == ["A/33", "A/34", "A/41"]
    assert not uni.setting.qc_applies


def t_a_run_carries_its_own_roles():
    """A run must stay readable after its setting is renamed or deleted.

    `to_dict` records the role map, not just a name to look up later -- and for
    a custom selection there is no config entry to look up at all.
    """
    lay = L.resolve(CFG, "", {"A": True}, ports_used=("A",),
                    custom={"headstage": "rhd2216_bipolar",
                            "roles": {"a": 1, "b": 2}})
    d = lay.to_dict()
    assert d["roles"] == {"a": 1, "b": 2}
    back = L.from_dict(CFG, d)
    assert back.labels() == lay.labels()
    assert back.setting.roles == lay.setting.roles

    # a stored layout naming a setting that no longer exists still resolves,
    # because the roles travelled with it
    d["setting"] = "deleted_setting"
    assert L.from_dict(CFG, d).labels() == lay.labels()


def t_role_names_are_checked_on_input_but_not_on_replay():
    """One rule for role names -- and yesterday's data must still open.

    FOUND 2026-09-14 by a real scheduled run. Extracting make_setting was meant
    to stop the inline picker and the settings panel from disagreeing, but the
    role-NAME rule was left behind in settings_store, so the panel refused
    "trial 2" while the picker accepted it. A run reached the NAS carrying role
    names with spaces.

    🔑 THE SUBTLETY. `layout.from_dict` rebuilds a stored run through the same
    function. Validating names there too would make that already-recorded run
    unreadable -- so the rule applies to INPUT and not to REPLAY. Tightening a
    rule must never make yesterday's data unopenable.
    """
    bad = {"headstage": "rhd2216_bipolar", "roles": {"trial 2": 5},
           "qc": "none", "qc_reason": "x"}
    try:
        L.resolve(CFG, "", {"A": True}, custom=bad)
    except P.PresetError as e:
        assert "role name" in str(e), str(e)
    else:
        raise AssertionError("a role name with a space was accepted")

    # the same names, REPLAYED from a stored run, must still resolve
    stored = {"setting": "custom", "headstage": "rhd2216_bipolar",
              "roles": {"trial1": 4, "trial 2": 5, "trial 3": 6},
              "qc": "none", "qc_reason": "x",
              "splitters": {p: True for p in L.PORTS}}
    lay = L.from_dict(CFG, stored)
    assert lay.labels_for_slot("A1") == ["A/4", "A/5", "A/6"]
    assert lay.labels_for_slot("A2") == ["A/36", "A/37", "A/38"]


def refusals():
    expect("refuse: custom channels the floor rule cannot describe, with qc auto",
           lambda: L.resolve(CFG, "", {"A": True},
                             custom={"headstage": "rhd2216_bipolar",
                                     "roles": {"a": 1, "b": 9}}),
           P.PresetError, "do not run 1..2")
    expect("refuse: custom qc none with no reason",
           lambda: L.resolve(CFG, "", {"A": True},
                             custom={"headstage": "rhd2216_bipolar",
                                     "roles": {"a": 1, "b": 9}, "qc": "none"}),
           P.PresetError, "qc_reason")
    expect("refuse: custom naming an unknown headstage",
           lambda: L.resolve(CFG, "", {"A": True},
                             custom={"headstage": "nope", "roles": {"a": 1}}),
           P.PresetError, "unknown headstage")
    expect("refuse: custom with a site beyond the chip",
           lambda: L.resolve(CFG, "", {"A": True},
                             custom={"headstage": "rhd2216_bipolar",
                                     "roles": {"a": 1, "b": 30}}),
           P.PresetError, "real channels")

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
recording_type_codes: {basal: B}
recording_type_folders: {basal: Baseline}
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
recording_type_codes: {basal: B}
recording_type_folders: {basal: Baseline}
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
               t_a_port_with_nothing_connected_is_named_and_offers_the_way_out,
               t_unused_ports_are_exempt,
               t_unverified_combination_is_refused_until_confirmed,
               t_cohort_extras_only_for_non_contiguous,
               t_custom_channels_for_one_run,
               t_a_run_carries_its_own_roles,
               t_role_names_are_checked_on_input_but_not_on_replay):
        check(fn.__name__, fn)
    print("\nMUST REFUSE")
    refusals()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Ports may differ in HOW MANY CHIPS they carry. They may not differ in roles.

THE RULE THIS PINS, from Andrea on 2026-09-14:

    "there will never be mice connected to the rig with different configuration
     at the same time. When someone records, the mice have all the same settings.
     What changes is just the amount of mice connected."

So a run varies in two ways and no others:
  - which ports carry a C3442 SPI splitter (2 chips, 64 channels) and which do
    not (1 chip, 32 channels)
  - which slots have an animal in them

Every animal in a run carries the same roles. `core.criteria.CohortSpec` CAN
express differing roles per port -- the data model needed per-chip `floor` and
`real_channels` for the unipolar case, and per-port roles came along free. That
capability is deliberately latent: nothing the console or a manifest produces may
reach it, because nothing has ever been recorded that way and an untested path
that can be entered by accident is worse than one that cannot.

Half these cases are refusals.

    PYTHONPATH=. python3 tests/test_port_chip_counts.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cohorts.schema import Cohort
from core import criteria as C

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


def coh(**kw) -> Cohort:
    base = {"cohort_id": "t", "roles": ["eeg", "emg"]}
    base.update(kw)
    return Cohort.from_obj(base)


# --------------------------------------------------------------------------- #
def t_a_manifest_without_ports_is_the_old_spec():
    """THE BACKWARD-COMPAT HINGE. Every manifest written before 2026-09-14.

    Not "equivalent" -- identical, on all three accessors, as lists.
    """
    got = coh().to_spec()
    want = C.CohortSpec(roles=("eeg", "emg"))
    assert got.positions() == want.positions()
    assert got.floor_sites() == want.floor_sites()
    assert got.animal_sites() == want.animal_sites()
    assert len(got.floor_sites()) == 8 * 14

    three = coh(roles=["eeg", "emg", "ecg"]).to_spec()
    assert three.floor_sites() == C.CohortSpec(
        roles=("eeg", "emg", "ecg")).floor_sites()
    assert len(three.floor_sites()) == 8 * 13


def t_splitters_on_some_ports_only():
    """The real variable: A and C split, B and D not. Six slots, not eight.

    The OLD model could not express this at all -- slot_bases was global, so
    every port had the same number of slots. That is why per-port chip counts
    were needed even though roles never vary.
    """
    spec = coh(ports={"A": 2, "B": 1, "C": 2, "D": 1}).to_spec()
    assert spec.positions() == ["A1", "A2", "B1", "C1", "C2", "D1"]
    assert len(spec.floor_sites()) == 6 * 14
    # each animal's floor is on its own chip, and never on another port
    for pos in spec.positions():
        for site in C.floor_sites_of(spec, pos):
            assert site.startswith(pos[0] + "/")


def t_no_splitters_anywhere():
    spec = coh(ports={"A": 1, "B": 1, "C": 1, "D": 1}).to_spec()
    assert spec.positions() == ["A1", "B1", "C1", "D1"]
    assert len(spec.floor_sites()) == 4 * 14


def t_roles_are_the_same_on_every_chip():
    """THE PIN. No manifest may produce a rig with differing roles per port."""
    for ports in ({"A": 2, "B": 1, "C": 2, "D": 1},
                  {"A": 1, "B": 1, "C": 1, "D": 1},
                  {"A": 2, "B": 2, "C": 2, "D": 2},
                  {"A": 2}):
        spec = coh(ports=ports).to_spec()
        role_sets = {c.roles for p in spec.layout for c in p.chips}
        assert len(role_sets) == 1, f"{ports} produced mixed roles: {role_sets}"
        assert spec.is_uniform or len({len(p.chips) for p in spec.layout}) > 1


def t_animal_and_floor_sites_never_overlap():
    for ports in ({"A": 2, "B": 1}, {"A": 1}, {"A": 2, "B": 2, "C": 1, "D": 1}):
        for roles in (["eeg", "emg"], ["eeg", "emg", "ecg"]):
            spec = coh(ports=ports, roles=roles).to_spec()
            animals = {s for r in spec.animal_sites().values() for s in r.values()}
            assert not (animals & set(spec.floor_sites()))


def t_unipolar_shifts_with_the_chip_base():
    """A second chip's explicit sites shift by base-1, like every other role."""
    uni = coh(roles=["emg1", "lfp_ref", "lfp_tgt", "eeg_f", "eeg_p", "emg2"],
              ports={"A": 2}, real_channels=32,
              role_sites={"emg1": 18, "lfp_ref": 19, "lfp_tgt": 20,
                          "eeg_f": 21, "eeg_p": 22, "emg2": 23},
              floor="none",
              floor_reason="unused inputs tied to ground, never characterised")
    spec = uni.to_spec()
    assert spec.animal_sites()["A1"]["eeg_f"] == "A/21"
    assert spec.animal_sites()["A2"]["eeg_f"] == "A/53"   # 21 + 32
    assert spec.floor_sites() == []


def refusals():
    expect("refuse: a port with three chips",
           lambda: coh(ports={"A": 3}).to_spec(), C.LayoutError, "one, or two")

    expect("refuse: a port with no chips",
           lambda: coh(ports={"A": 0}).to_spec(), C.LayoutError, "one, or two")

    expect("refuse: floor none with no reason",
           lambda: coh(ports={"A": 1}, floor="none").to_spec(),
           C.LayoutError, "floor_reason")

    expect("refuse: explicit sites that the derivation cannot describe",
           # /18../23 with no `floor: none` -- the unipolar trap. A derived floor
           # would be /24../32: real inputs nobody characterised.
           lambda: coh(roles=["a", "b"], ports={"A": 1}, real_channels=32,
                       role_sites={"a": 18, "b": 19}).to_spec(),
           C.LayoutError, "does not describe it")

    expect("refuse: a role beyond the chip's real channels",
           lambda: coh(roles=["a", "b"], ports={"A": 1},
                       role_sites={"a": 1, "b": 30},
                       floor="none", floor_reason="x").to_spec(),
           C.LayoutError, "outside this chip")

    expect("refuse: an unknown position from --positions",
           lambda: coh(ports={"A": 1}).to_spec().site_of("D2", "eeg"),
           C.LayoutError, "not a position")

    expect("refuse: asking for a role this layout does not carry",
           lambda: coh().to_spec().site_of("A1", "ecg"),
           C.LayoutError, "no role")

    expect("refuse: a pooled floor when chip counts differ",
           lambda: C.floor_stats(
               type("F", (), {"spec": coh(ports={"A": 2, "B": 1}).to_spec()})(),
               None),
           C.LayoutError, "not uniform")


def main() -> int:
    print("PER-PORT CHIP COUNTS, SHARED ROLES")
    for fn in (t_a_manifest_without_ports_is_the_old_spec,
               t_splitters_on_some_ports_only, t_no_splitters_anywhere,
               t_roles_are_the_same_on_every_chip,
               t_animal_and_floor_sites_never_overlap,
               t_unipolar_shifts_with_the_chip_base):
        check(fn.__name__, fn)
    print("\nMUST REFUSE")
    refusals()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

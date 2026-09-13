#!/usr/bin/env python3
"""The oracle: CohortSpec's four accessors must not move for a uniform rig.

WHAT THIS IS FOR. `CohortSpec` is being generalised so that the four XDAQ ports
can be configured differently -- a splitter on one, none on another, three roles
here and two there. The generalisation is only safe if the UNIFORM case it
replaces comes out bit-identical, because the wire-free floor those accessors
define is the in-file control behind every verdict this project has published.
Silently widening or narrowing it by one site would not break anything visibly;
it would just quietly change what "usable" has meant since August.

So this file holds VERBATIM COPIES of the pre-change function bodies, taken from
core/criteria.py on 2026-09-13 at commit 64df8b5, and asserts the live code still
agrees with them. The copies are the point. Do not "simplify" them to call the
live implementation -- that would make this file agree with itself and prove
nothing, which is the exact failure mode `test_ladder_verdicts` already has.

🔑 EQUALITY IS ON LISTS, NOT SETS. `floor_threshold_ci` draws
`rng.integers(0, n_sites, n_sites)` against a fixed seed and indexes the floor
site list BY POSITION. A reordering that preserved the set would leave every
published confidence interval different while a set comparison passed.

    PYTHONPATH=. python3 tests/test_cohortspec_compat.py
"""
from __future__ import annotations

import itertools
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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


# --------------------------------------------------------------------------- #
# VERBATIM pre-change implementations. core/criteria.py @ 64df8b5.
# --------------------------------------------------------------------------- #
LEGACY_CHIP_REAL_CHANNELS = 16


def _legacy_positions(roles, ports, slot_bases):
    return [f"{p}{slot}" for p in ports
            for slot in range(1, len(slot_bases) + 1)]


def _legacy_animal_sites(roles, ports, slot_bases):
    out: dict[str, dict[str, str]] = {}
    for p in ports:
        for slot_i, base in enumerate(slot_bases, start=1):
            out[f"{p}{slot_i}"] = {
                role: f"{p}/{base + k}" for k, role in enumerate(roles)}
    return out


def _legacy_floor_sites(roles, ports, slot_bases):
    n = len(roles)
    return [f"{p}/{i}"
            for p in ports
            for base in slot_bases
            for i in range(base + n, base + LEGACY_CHIP_REAL_CHANNELS)]


def _legacy_floor_sites_of(roles, slot_bases, position):
    port = position[0]
    slot_i = int(position[1:])
    base = slot_bases[slot_i - 1]
    n = len(roles)
    return [f"{port}/{i}"
            for i in range(base + n, base + LEGACY_CHIP_REAL_CHANNELS)]


# --------------------------------------------------------------------------- #
# the cross product
# --------------------------------------------------------------------------- #
ROLE_SETS = [("eeg", "emg"), ("eeg", "emg", "ecg")]
PORT_SETS = ["ABCD", "A", "AC"]
BASE_SETS = [(1,), (1, 33)]

CASES = [
    (roles, ports, bases)
    for roles, ports, bases in itertools.product(ROLE_SETS, PORT_SETS, BASE_SETS)
]


def t_positions():
    for roles, ports, bases in CASES:
        spec = C.CohortSpec(roles=roles, ports=ports, slot_bases=bases)
        want = _legacy_positions(roles, ports, bases)
        assert spec.positions() == want, (roles, ports, bases, spec.positions(), want)


def t_animal_sites():
    for roles, ports, bases in CASES:
        spec = C.CohortSpec(roles=roles, ports=ports, slot_bases=bases)
        want = _legacy_animal_sites(roles, ports, bases)
        got = spec.animal_sites()
        assert got == want, (roles, ports, bases, got, want)
        # key order matters too: animal_sites feeds `wanted` in compute_features
        assert list(got) == list(want), "position ORDER changed"
        for pos in want:
            assert list(got[pos]) == list(want[pos]), f"role ORDER changed at {pos}"


def t_floor_sites_is_list_equal():
    """LIST equality. A reordering moves every bootstrap CI, silently."""
    for roles, ports, bases in CASES:
        spec = C.CohortSpec(roles=roles, ports=ports, slot_bases=bases)
        want = _legacy_floor_sites(roles, ports, bases)
        got = spec.floor_sites()
        assert got == want, (roles, ports, bases, got[:6], want[:6])
        assert set(got) == set(want)          # redundant, kept as documentation


def t_floor_sites_of_every_position():
    for roles, ports, bases in CASES:
        spec = C.CohortSpec(roles=roles, ports=ports, slot_bases=bases)
        for pos in _legacy_positions(roles, ports, bases):
            want = _legacy_floor_sites_of(roles, bases, pos)
            got = C.floor_sites_of(spec, pos)
            assert got == want, (roles, ports, bases, pos, got, want)


def t_site_of():
    for roles, ports, bases in CASES:
        spec = C.CohortSpec(roles=roles, ports=ports, slot_bases=bases)
        want = _legacy_animal_sites(roles, ports, bases)
        for pos, rr in want.items():
            for role, site in rr.items():
                assert spec.site_of(pos, role) == site


def t_the_pinned_integers():
    """The numbers the rest of the project quotes. These ARE the regression.

    953,904 = 8 positions x 14 floor sites x 8,517 epochs, asserted in
    test_criteria_regression.py:143. One site added to or removed from the 2-role
    floor moves it by 8,517, which is why that test is the single best proof that
    this change did not touch the control group.
    """
    two = C.CohortSpec(roles=("eeg", "emg"))
    assert len(two.floor_sites()) == 8 * 14, len(two.floor_sites())
    assert len(two.positions()) == 8

    # The 3-role cohort had no pinned number. It does now: 13 floor sites per
    # chip, 8 chips. criteria.py's own docstring quotes the 14-to-104 range.
    three = C.CohortSpec(roles=("eeg", "emg", "ecg"))
    assert len(three.floor_sites()) == 8 * 13 == 104, len(three.floor_sites())

    # And the invariant that makes both true: animal sites and floor sites are
    # disjoint. An overlap would put a real animal in its own control group.
    for spec in (two, three):
        animals = {s for rr in spec.animal_sites().values() for s in rr.values()}
        assert not (animals & set(spec.floor_sites())), "animal site in the floor"


def t_floor_never_reaches_the_inactive_slots():
    """No floor site may land in /17../32 or /49../64.

    criteria.py:80 -- those are inactive, internally tied slots on an RHD2216.
    They read low almost always, so a floor containing them would FLATTER the
    control and condemn every real animal. This is the most dangerous direction
    of silent widening, so it gets its own assertion rather than riding along.
    """
    for roles, ports, bases in CASES:
        spec = C.CohortSpec(roles=roles, ports=ports, slot_bases=bases)
        for s in spec.floor_sites():
            n = int(s.split("/")[1])
            within = any(base <= n < base + LEGACY_CHIP_REAL_CHANNELS
                         for base in bases)
            assert within, f"{s} is outside every chip's real-channel window"


def main() -> int:
    print("COHORTSPEC BACKWARD COMPATIBILITY")
    print(f"  {len(CASES)} specs x 4 accessors, list equality against frozen copies\n")
    for fn in (t_positions, t_animal_sites, t_floor_sites_is_list_equal,
               t_floor_sites_of_every_position, t_site_of,
               t_the_pinned_integers, t_floor_never_reaches_the_inactive_slots):
        check(fn.__name__, fn)
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    for n, tb in FAIL:
        print(f"\n--- {n} ---\n{tb}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())

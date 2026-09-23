#!/usr/bin/env python3
"""Tests for the cohort identity layer.

Run:  ~/eeg-analysis-venv/bin/python tests/test_cohort_schema.py
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

from cohorts.load import load_cohort  # noqa: E402
from cohorts.schema import (          # noqa: E402
    Animal, Cohort, RigPlacement, moment_from_base, weeks_between,
)

FAILURES: list[str] = []


def check(label: str, got, want) -> None:
    if got != want:
        FAILURES.append(f"{label}: got {got!r}, want {want!r}")
        print(f"  FAIL  {label}: got {got!r}, want {want!r}")
    else:
        print(f"  ok    {label} = {got!r}")


def check_raises(label: str, fn) -> None:
    try:
        fn()
    except SystemExit:
        print(f"  ok    {label} raised as required")
        return
    except Exception as exc:                     # noqa: BLE001
        print(f"  ok    {label} raised {type(exc).__name__}")
        return
    FAILURES.append(f"{label}: did NOT raise")
    print(f"  FAIL  {label}: did NOT raise")


# --------------------------------------------------------------------------- #
print("\nage arithmetic: nearest whole week, half rounding UP, no decimals")
# 24 days = 3.43 weeks -> 3 ;  25 days = 3.57 -> 4 ;  24.5 days is impossible in
# whole days, so the half case is tested at exactly 3.5 weeks = 24.5 -> use 7*n+3.5
check("0 days",   weeks_between(dt.date(2026, 1, 1), dt.date(2026, 1, 1)), 0)
check("24 days",  weeks_between(dt.date(2026, 1, 1), dt.date(2026, 1, 25)), 3)
check("25 days",  weeks_between(dt.date(2026, 1, 1), dt.date(2026, 1, 26)), 4)
check("70 days",  weeks_between(dt.date(2026, 1, 1), dt.date(2026, 3, 12)), 10)
check("unknown end", weeks_between(dt.date(2026, 1, 1), None), None)

print("\ndate of birth derived from arrival + age at arrival")
a = Animal(animal_id="X", arrival_date=dt.date(2026, 6, 1), age_at_arrival_weeks=8)
dob, derived = a.dob_effective
check("derived dob", dob, dt.date(2026, 4, 6))
check("marked derived", derived, True)
check("age at a later date", a.age_weeks_at("2026-08-06"), (17, True))  # 122 d = 17.4 wk

a2 = Animal(animal_id="Y", dob=dt.date(2026, 4, 6),
            arrival_date=dt.date(2026, 6, 1), age_at_arrival_weeks=99)
check("recorded dob beats derived", a2.dob_effective, (dt.date(2026, 4, 6), False))

check("age unknowable", Animal(animal_id="Z").age_weeks_at("2026-08-06"), (None, False))

print("\ndays post-surgery and post-tether")
b = Animal(animal_id="B", surgery_date=dt.date(2026, 7, 21),
           tether_date=dt.date(2026, 8, 6))
check("days post surgery", b.days_post_surgery("2026-08-06"), 16)
check("days post tether", b.days_post_tether("2026-08-06"), 0)
check("unknown surgery", Animal(animal_id="Q").days_post_surgery("2026-08-06"), None)

print("\nvalidation refuses impossible dates")
bad = Animal(animal_id="bad", arrival_date=dt.date(2026, 8, 1),
             surgery_date=dt.date(2026, 7, 1))
check("out-of-order flagged", len(bad.validate()) >= 1, True)
heavy = Animal(animal_id="heavy")
heavy.weighings.append(type(heavy.weighings)and __import__("cohorts.schema", fromlist=["Weighing"]).Weighing(
    date=dt.date(2026, 8, 1), grams=2400.0, occasion="surgery"))
check("weight unit error flagged", any("5-80 g" in p for p in heavy.validate()), True)

print("\none rig position may hold only one animal at a time")
c = Cohort(cohort_id="t")
c.animals = [
    Animal(animal_id="one", placements=[RigPlacement(from_date=dt.date(2026, 7, 30), position="B1")]),
    Animal(animal_id="two", placements=[RigPlacement(from_date=dt.date(2026, 7, 30), position="B1")]),
]
check("collision detected", any("claimed by 2 animals" in p for p in c.validate()), True)

# --------------------------------------------------------------------------- #
print("\nthe real manifest: which mouse was in the B1 position, and when")
cohort = load_cohort("HLB-fem-profsurgery-troubleshooting", verbose=False)
check("animals loaded", len(cohort.animals), 9)
check("B1 on 2026-07-31", cohort.animal_at("B1", "2026-07-31").animal_id, "HLB-B1a")
check("B1 on 2026-08-06", cohort.animal_at("B1", "2026-08-06").animal_id, "HLB-B1b")
check("D2 arm on 2026-07-31", cohort.animal_at("D2", "2026-07-31").placement_at("2026-07-31").tether_arm, "A")

# The tether swap happened at 16:27 on 2026-08-06, BETWEEN two recordings made
# that same day. A date-only lookup lands before it and must say arm A; the
# overnight recording started at 16:57 and must say arm C. Getting this wrong
# attributes the afternoon's failure to the tether that actually fixed it.
d2 = cohort.by_id("HLB-D2")
check("D2 arm at 2026-08-06 00:00 (date only)",
      d2.placement_at("2026-08-06").tether_arm, "A")
check("D2 arm at 2026-08-06 12:45 (afternoon recording)",
      d2.placement_at("2026-08-06 12:45").tether_arm, "A")
check("D2 arm at 2026-08-06 16:57 (overnight recording)",
      d2.placement_at("2026-08-06 16:57").tether_arm, "C")
check("B1b days post-surgery at overnight",
      cohort.by_id("HLB-B1b").days_post_surgery("2026-08-06"), 16)
check("B1a is sacrificed", cohort.by_id("HLB-B1a").is_alive, False)
check("A2 holds no mouse",
      cohort.by_id("HLB-A2-NO-MOUSE").recordings[0].role, "no-mouse control")

print("\nmissing husbandry data reports as unknown rather than as a number")
check("B1b arrival unknown", cohort.by_id("HLB-B1b").arrival_date, None)
check("B1b age unknown", cohort.by_id("HLB-B1b").age_weeks_at("2026-08-06"), (None, False))
check("B1b weight unknown", cohort.by_id("HLB-B1b").weight_at_or_before("2026-08-06"), None)

print("\na manifest with impossible dates is refused, not drawn")
bad_yaml = ROOT / "tests" / "_tmp_bad_cohort.yaml"
bad_yaml.write_text(
    "cohort_id: bad\nanimals:\n"
    "  - animal_id: m1\n    surgery_date: 2026-08-01\n    tether_date: 2026-07-01\n")
check_raises("strict load of a bad manifest", lambda: load_cohort(bad_yaml, verbose=False))
bad_yaml.unlink()

# --------------------------------------------------------------------------- #
print("\nidentity resolves at the recording's START MOMENT, not at midnight")
# REGRESSION, 2026-09-23. build_card resolved a recording at its DATE whenever
# stage 2 had not run, i.e. at 00:00. On 2026-08-26 that named HLBSSD13 in B1:
# its 10:00 move OFF-RIG had not happened yet at midnight and HLBSSD17's 12:00
# arrival was still in the future. The card named a mouse already off the rig.
ssd = load_cohort("S-SD", verbose=False)
check("B1 at midnight is the outgoing animal",
      ssd.animal_at("B1", "2026-08-26").animal_id, "HLBSSD13")
check("B1 at the real 12:50 start is the incoming animal",
      ssd.animal_at("B1", moment_from_base("allego_1__uid0826-12-50-16")).animal_id,
      "HLBSSD17")
check("moment_from_base reads the uid token",
      moment_from_base("allego_1__uid0826-12-50-16"),
      dt.datetime(2026, 8, 26, 12, 50, 16))
check("moment_from_base declines a name without one",
      moment_from_base("not-a-recording"), None)

print("\nDATE-ONLY placements still resolve: the <= comparison is load-bearing")
# 16 animal-recordings in W-SL and S-SL have a placement whose `from` is the
# DATE of the recording, with no time. They resolve only because the comparison
# in placement_at is inclusive. Anyone tightening it to `<` to "fix" the case
# above breaks every one of them, so both facts are asserted together.
wsl = load_cohort("W-SL", verbose=False)
for pos, want in (("A1", "HLBWSL21"), ("D1", "HLBWSL27"), ("D2", "HLBWSL29")):
    check(f"W-SL {pos} resolves on its own placement date",
          wsl.animal_at(pos, "2026-09-10").animal_id, want)
ssl = load_cohort("S-SL", verbose=False)
for pos, want in (("A1", "HLBSSL31"), ("C2", "HLBSSL39"), ("D1", "HLBSSL40")):
    check(f"S-SL {pos} resolves on its own placement date",
          ssl.animal_at(pos, "2026-09-12").animal_id, want)

print("\na recordings row that contradicts the placements is refused")
clash = ROOT / "tests" / "_tmp_clash_cohort.yaml"
clash.write_text(
    "cohort_id: clash\nanimals:\n"
    "  - animal_id: m1\n    placements: [{from: 2026-08-01, position: B1}]\n"
    "  - animal_id: m2\n    recordings: [{base: allego_0__uid0805-09-00-00, "
    "date: 2026-08-05, position: B1, role: animal}]\n")
check_raises("strict load of a manifest whose row and placements disagree",
             lambda: load_cohort(clash, verbose=False))
clash.unlink()

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S)")
    for f in FAILURES:
        print("  " + f)
    sys.exit(1)
print("all cohort schema tests pass")

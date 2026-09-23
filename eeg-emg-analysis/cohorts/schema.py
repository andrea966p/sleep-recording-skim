#!/usr/bin/env python3
"""Animal and cohort records: the identity layer that every figure hangs off.

WHY THIS EXISTS
---------------
Until now every figure in this project was labelled by RIG POSITION ("B1",
"D2"). A rig position is not an animal. The animal in the B1 position changed on
2026-08-06 because the original was sacrificed on 2026-08-05, so two different
mice share one label across the figures currently in the vault. Nothing in the
codebase recorded which mouse was which, when it arrived, when it was operated
on, or which tether it was wearing.

This module fixes that by making the ANIMAL the primary key and the position a
dated attribute of the animal, not the other way round.

DESIGN RULES
------------
1. EVERY FIELD IS OPTIONAL. A missing field renders as "not recorded" on the
   card rather than vanishing. Implant and tethering dates are currently logged
   nowhere in this project, and the card must keep saying so until they are.
2. ANYTHING WITH A DATE IS A LIST OF DATED ENTRIES, not a fixed column. A new
   experiment type (SOD1, water administration, Y maze, NOR, ...) must never
   require a schema change.
3. EVERY VALUE CARRIES ITS SOURCE. `source` on a dated entry says where the
   value came from: "husbandry-sheet", "journal 2026-08-06", "inferred". A
   number whose provenance is unknown is reported as unknown, not as fact.
4. DATES ARE VALIDATED FOR ORDER. arrival <= surgery <= tether <= recordings <=
   sacrifice. An out-of-order manifest raises rather than silently drawing a
   nonsense timeline.

AGE ARITHMETIC, stated once so it is never argued about again
-------------------------------------------------------------
If `dob` is recorded it is used directly. If not, dob is derived as
`arrival_date - age_at_arrival_weeks`, and every age computed from it is marked
`derived=True` so the card can say so.

    age_weeks = round(days / 7)   nearest whole week, half rounding UP

No decimals anywhere. Age printed on an animal card is AGE AT THAT RECORDING,
never age today. Age today appears only on the cohort sheet, and only for an
animal that has not been sacrificed.
"""
from __future__ import annotations

import datetime as _dt
import re as _re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable

# --------------------------------------------------------------------------- #
# date helpers
# --------------------------------------------------------------------------- #

DateLike = _dt.date | _dt.datetime | str | None


def as_date(value: DateLike) -> _dt.date | None:
    """Coerce anything date-ish to a date. None stays None (= not recorded)."""
    if value is None or value == "":
        return None
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y", "%Y%m%d"):
        try:
            return _dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    # last resort: ISO datetime with a time part
    try:
        return _dt.datetime.fromisoformat(text).date()
    except ValueError as exc:
        raise ValueError(f"unparseable date: {value!r}") from exc


def as_time(value: Any) -> _dt.time | None:
    """Pull a time out of a datetime or an ISO string. None when date-only."""
    if value is None or value == "":
        return None
    if isinstance(value, _dt.datetime):
        return value.time()
    if isinstance(value, _dt.time):
        return value
    if isinstance(value, _dt.date):
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M", "%H:%M:%S", "%H:%M"):
        try:
            return _dt.datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return None


def moment_from_base(base: str) -> _dt.datetime | None:
    """The LOCAL start moment encoded in an Allego base name, or None.

    `allego_1__uid0826-12-50-16` started at 12:50:16 on 08-26. Resolving that
    recording at its DATE means midnight, and midnight names whichever animal
    held the position the night before -- which is how a card came to name a
    mouse that had already been pulled from the rig. The year is not in the
    token; recordings here are 2026 and a wrong year would only ever widen the
    search, never pick a different animal within the day.
    """
    m = _re.search(r"uid(\d{2})(\d{2})-(\d{2})-(\d{2})-(\d{2})", base or "")
    if not m:
        return None
    mo, da, hh, mi, ss = (int(x) for x in m.groups())
    try:
        return _dt.datetime(2026, mo, da, hh, mi, ss)
    except ValueError:
        return None


def as_moment(value: Any) -> _dt.datetime | None:
    """A date, or a date and time, as a naive datetime. None when unknown."""
    d = as_date(value)
    if d is None:
        return None
    return _dt.datetime.combine(d, as_time(value) or _dt.time.min)


def weeks_between(start: _dt.date | None, end: _dt.date | None) -> int | None:
    """Whole weeks, nearest, half rounding up. None if either end is unknown."""
    if start is None or end is None:
        return None
    days = (end - start).days
    return int((Decimal(days) / Decimal(7)).quantize(Decimal("1"),
                                                     rounding=ROUND_HALF_UP))


def days_between(start: _dt.date | None, end: _dt.date | None) -> int | None:
    if start is None or end is None:
        return None
    return (end - start).days


# --------------------------------------------------------------------------- #
# dated entries
# --------------------------------------------------------------------------- #

@dataclass
class Weighing:
    """One body weight, at one moment, with a reason it was taken."""
    date: _dt.date | None = None
    grams: float | None = None
    occasion: str = ""          # "arrival" | "surgery" | "tethering" | "sacrifice" | free text
    source: str = ""

    @classmethod
    def from_obj(cls, obj: dict[str, Any]) -> "Weighing":
        return cls(date=as_date(obj.get("date")),
                   grams=_as_float(obj.get("grams", obj.get("weight_g"))),
                   occasion=str(obj.get("occasion", "") or ""),
                   source=str(obj.get("source", "") or ""))


@dataclass
class Intervention:
    """Anything done TO the animal that is not surgery, tethering or recording.

    Kind is free text on purpose: chronic sleep deprivation, SOD1, water
    administration, Y maze, NOR, and whatever comes next.
    """
    kind: str = ""
    start: _dt.date | None = None
    end: _dt.date | None = None
    notes: str = ""
    source: str = ""

    @classmethod
    def from_obj(cls, obj: dict[str, Any]) -> "Intervention":
        start = as_date(obj.get("start", obj.get("date")))
        return cls(kind=str(obj.get("kind", "") or ""),
                   start=start,
                   end=as_date(obj.get("end")) or start,
                   notes=str(obj.get("notes", "") or ""),
                   source=str(obj.get("source", "") or ""))


@dataclass
class RigPlacement:
    """Where the animal sat and what it was wearing, FROM a moment.

    Both change. D2 wore arm A, then arm C. The B1 position held two different
    animals. Neither is a property of the animal for all time, so both are
    dated.

    ⚠️ THE MOMENT NEEDS A TIME, NOT JUST A DATE. D2's arm C swap happened at
    16:27 on 2026-08-06, between two recordings made on the same day: the 12:45
    afternoon run was on arm A and the 16:57 overnight run was on arm C. With
    date-only placements the card labelled both "arm C", which is precisely the
    mislabelling this whole identity layer exists to prevent. Write
    `from: 2026-08-06 16:27` when the swap time is known.
    """
    from_date: _dt.date | None = None
    from_time: _dt.time | None = None      # optional; None means "from 00:00"
    position: str = ""          # "A1".."D2", a RIG POSITION not an animal
    tether_arm: str = ""        # "A" original | "B" short soldered | "C" long direct, no slip ring
    tether_notes: str = ""
    source: str = ""

    @property
    def from_moment(self) -> _dt.datetime | None:
        if self.from_date is None:
            return None
        return _dt.datetime.combine(self.from_date, self.from_time or _dt.time.min)

    @classmethod
    def from_obj(cls, obj: dict[str, Any]) -> "RigPlacement":
        raw = obj.get("from", obj.get("from_date"))
        return cls(from_date=as_date(raw),
                   from_time=as_time(raw) or as_time(obj.get("from_time")),
                   position=str(obj.get("position", "") or ""),
                   tether_arm=str(obj.get("tether_arm", obj.get("arm", "")) or ""),
                   tether_notes=str(obj.get("tether_notes", "") or ""),
                   source=str(obj.get("source", "") or ""))


@dataclass
class RecordingRef:
    """A recording this animal took part in.

    `base` is the Allego file stem, e.g. allego_1__uid0806-16-57-38, which is
    the join key to everything on disk.
    """
    base: str = ""
    date: _dt.date | None = None
    position: str = ""          # position DURING this recording
    role: str = ""              # "animal" | "no-mouse control" | "positive control"
    notes: str = ""

    @classmethod
    def from_obj(cls, obj: dict[str, Any]) -> "RecordingRef":
        return cls(base=str(obj.get("base", "") or ""),
                   date=as_date(obj.get("date")),
                   position=str(obj.get("position", "") or ""),
                   role=str(obj.get("role", "animal") or "animal"),
                   notes=str(obj.get("notes", "") or ""))


# --------------------------------------------------------------------------- #
# the animal
# --------------------------------------------------------------------------- #

# Field order on the card, and the reasoning:
#   who is this -> where did it come from -> what was done to it -> what am I
#   looking at. Groups 1 and 2 go in the identity bar, group 3 goes on the life
#   timeline, group 4 comes from the recording rather than from the animal.
FIELD_GROUPS = {
    "identity":   ("project_id", "batch_id", "animal_id", "sex"),
    "provenance": ("vendor", "strain", "arrival_date", "age_at_arrival_weeks", "dob"),
    "life":       ("surgery_date", "surgery_notes", "surgeon",
                   "tether_date", "interventions", "recordings",
                   "sacrifice_date", "sampling_date", "sampling_notes"),
}


@dataclass
class Animal:
    # --- group 1, identity -------------------------------------------------
    animal_id: str = ""
    project_id: str = ""
    batch_id: str = ""
    sex: str = ""                       # "F" | "M" | ""

    # --- group 2, provenance ----------------------------------------------
    vendor: str = ""                    # e.g. HLB
    strain: str = ""
    arrival_date: _dt.date | None = None
    age_at_arrival_weeks: int | None = None
    dob: _dt.date | None = None         # if absent, derived from the two above

    # --- group 3, life events ---------------------------------------------
    surgery_date: _dt.date | None = None
    surgeon: str = ""
    surgery_notes: str = ""
    tether_date: _dt.date | None = None
    sacrifice_date: _dt.date | None = None
    sampling_date: _dt.date | None = None
    sampling_notes: str = ""

    weighings: list[Weighing] = field(default_factory=list)
    interventions: list[Intervention] = field(default_factory=list)
    placements: list[RigPlacement] = field(default_factory=list)
    recordings: list[RecordingRef] = field(default_factory=list)

    notes: str = ""
    sources: dict[str, str] = field(default_factory=dict)

    # ---------------------------------------------------------------- derived
    @property
    def dob_effective(self) -> tuple[_dt.date | None, bool]:
        """(date_of_birth, was_it_derived). (None, False) when unknowable."""
        if self.dob is not None:
            return self.dob, False
        if self.arrival_date is not None and self.age_at_arrival_weeks is not None:
            return self.arrival_date - _dt.timedelta(weeks=self.age_at_arrival_weeks), True
        return None, False

    def age_weeks_at(self, when: DateLike) -> tuple[int | None, bool]:
        """Age in WHOLE WEEKS at a given date. (age, derived_flag)."""
        dob, derived = self.dob_effective
        return weeks_between(dob, as_date(when)), derived

    def days_post_surgery(self, when: DateLike) -> int | None:
        return days_between(self.surgery_date, as_date(when))

    def days_post_tether(self, when: DateLike) -> int | None:
        return days_between(self.tether_date, as_date(when))

    def placement_at(self, when: DateLike) -> RigPlacement | None:
        """The placement in force at a moment: the latest one starting at or
        before it.

        Pass a full datetime when you have one. Two recordings made on the same
        day can sit either side of a tether swap, and passing only the date puts
        both of them on the wrong side of it half the time.
        """
        target = as_moment(when)
        if target is None:
            return None
        candidates = [p for p in self.placements
                      if p.from_moment is not None and p.from_moment <= target]
        return max(candidates, key=lambda p: p.from_moment) if candidates else None

    def weight_at_or_before(self, when: DateLike) -> Weighing | None:
        """Most recent weighing on or before a date, so the card can say WHICH."""
        target = as_date(when)
        if target is None:
            return None
        candidates = [w for w in self.weighings
                      if w.date is not None and w.grams is not None and w.date <= target]
        return max(candidates, key=lambda w: w.date) if candidates else None

    @property
    def is_alive(self) -> bool:
        return self.sacrifice_date is None

    # ---------------------------------------------------------------- loading
    @classmethod
    def from_obj(cls, obj: dict[str, Any]) -> "Animal":
        a = cls(
            animal_id=str(obj.get("animal_id", "") or ""),
            project_id=str(obj.get("project_id", "") or ""),
            batch_id=str(obj.get("batch_id", "") or ""),
            sex=str(obj.get("sex", "") or ""),
            vendor=str(obj.get("vendor", "") or ""),
            strain=str(obj.get("strain", "") or ""),
            arrival_date=as_date(obj.get("arrival_date")),
            age_at_arrival_weeks=_as_int(obj.get("age_at_arrival_weeks")),
            dob=as_date(obj.get("dob")),
            surgery_date=as_date(obj.get("surgery_date")),
            surgeon=str(obj.get("surgeon", "") or ""),
            surgery_notes=str(obj.get("surgery_notes", "") or ""),
            tether_date=as_date(obj.get("tether_date")),
            sacrifice_date=as_date(obj.get("sacrifice_date")),
            sampling_date=as_date(obj.get("sampling_date")),
            sampling_notes=str(obj.get("sampling_notes", "") or ""),
            notes=str(obj.get("notes", "") or ""),
            sources=dict(obj.get("sources", {}) or {}),
        )
        a.weighings = [Weighing.from_obj(w) for w in obj.get("weighings", []) or []]
        a.interventions = [Intervention.from_obj(i) for i in obj.get("interventions", []) or []]
        a.placements = [RigPlacement.from_obj(p) for p in obj.get("placements", []) or []]
        a.recordings = [RecordingRef.from_obj(r) for r in obj.get("recordings", []) or []]
        return a

    # ------------------------------------------------------------- validation
    def validate(self) -> list[str]:
        """Return a list of problems. Empty list means the record is coherent."""
        problems: list[str] = []
        if not self.animal_id:
            problems.append("animal has no animal_id")

        # Date ordering. Only compare pairs where BOTH dates are recorded, so a
        # sparse manifest is never penalised for what it does not yet know.
        chain = [("arrival", self.arrival_date),
                 ("surgery", self.surgery_date),
                 ("tether", self.tether_date),
                 ("sacrifice", self.sacrifice_date),
                 ("sampling", self.sampling_date)]
        known = [(n, d) for n, d in chain if d is not None]
        for (n1, d1), (n2, d2) in zip(known, known[1:]):
            if d1 > d2:
                problems.append(
                    f"{self.animal_id}: {n1} {d1} is after {n2} {d2}")

        for r in self.recordings:
            if r.date is None:
                continue
            if self.tether_date and r.date < self.tether_date:
                problems.append(
                    f"{self.animal_id}: recording {r.base} on {r.date} precedes "
                    f"tethering on {self.tether_date}")
            if self.sacrifice_date and r.date > self.sacrifice_date:
                problems.append(
                    f"{self.animal_id}: recording {r.base} on {r.date} is after "
                    f"sacrifice on {self.sacrifice_date}")

        for w in self.weighings:
            if w.grams is not None and not (5.0 <= w.grams <= 80.0):
                problems.append(
                    f"{self.animal_id}: body weight {w.grams} g on {w.date} is "
                    "outside 5-80 g, check the units")

        dob, _ = self.dob_effective
        if dob is not None:
            for label, d in known:
                age = weeks_between(dob, d)
                if age is not None and age < 0:
                    problems.append(
                        f"{self.animal_id}: {label} {d} precedes date of birth {dob}")
        return problems


# --------------------------------------------------------------------------- #
# the cohort
# --------------------------------------------------------------------------- #

@dataclass
class Cohort:
    cohort_id: str = ""
    title: str = ""
    description: str = ""
    project_id: str = ""
    # Which channel roles each animal carries, and therefore which native-index
    # offsets are this animal's and which are wire-free floor. Set per cohort
    # because the ECG cohort added a third role and moved the floor.
    roles: tuple[str, ...] = ("eeg", "emg")
    # HOW MANY AMPLIFIER CHIPS EACH PORT CARRIES. A C3442 SPI splitter puts two
    # on a port (64 enumerated channels, animals at bases 1 and 33); without one
    # a port carries one (32 channels, base 1 only).
    #
    # Empty means the historical assumption: four ports, two chips each. That is
    # the backward-compatibility hinge -- every manifest written before
    # 2026-09-14 omits this key and must keep producing exactly the old spec.
    #
    # 🔑 ROLES ARE RIG-WIDE, NOT PER PORT. Mice on this rig always share one
    # configuration; what changes between runs is how many are connected and
    # which ports carry splitters. core.criteria.CohortSpec can express differing
    # roles per port, and nothing here may produce that -- see
    # tests/test_port_chip_counts.py.
    ports: dict[str, int] = field(default_factory=dict)
    # For a layout whose roles do not sit contiguously from the chip base -- the
    # unipolar prep at /18../23. Absent for every bipolar cohort.
    role_sites: dict[str, int] = field(default_factory=dict)
    real_channels: int = 0          # 0 = the RHD2216 default of 16
    floor: str = ""                 # "none" = this layout has no wire-free control
    floor_reason: str = ""
    criterion: str = "slope"        # "slope" | "hum"; see core/criteria.py
    animals: list[Animal] = field(default_factory=list)
    recordings: list[RecordingRef] = field(default_factory=list)
    notes: str = ""

    def by_id(self, animal_id: str) -> Animal | None:
        for a in self.animals:
            if a.animal_id == animal_id:
                return a
        return None

    def animal_at(self, position: str, when: DateLike) -> Animal | None:
        """WHICH MOUSE was in this rig position on this date.

        This is the lookup that the current figures cannot do, and the reason
        two different animals are both labelled B1 in the vault.
        """
        target = as_moment(when)
        best: tuple[_dt.datetime, Animal] | None = None
        for a in self.animals:
            p = a.placement_at(target)
            if p is not None and p.position == position:
                if best is None or p.from_moment > best[0]:
                    best = (p.from_moment, a)
        return best[1] if best else None

    def validate(self) -> list[str]:
        problems: list[str] = []
        if not self.cohort_id:
            problems.append("cohort has no cohort_id")
        seen: set[str] = set()
        for a in self.animals:
            if a.animal_id in seen:
                problems.append(f"duplicate animal_id {a.animal_id}")
            seen.add(a.animal_id)
            problems.extend(a.validate())

        # One rig position may hold only one animal at a time. Catching this is
        # the whole point: it is the B1 collision, made loud.
        by_pos: dict[tuple[str, _dt.date], list[str]] = {}
        for a in self.animals:
            for p in a.placements:
                if p.position and p.from_date:
                    by_pos.setdefault((p.position, p.from_date), []).append(a.animal_id)
        for (pos, d), ids in sorted(by_pos.items()):
            if len(ids) > 1:
                problems.append(
                    f"position {pos} claimed by {len(ids)} animals from {d}: {', '.join(ids)}")

        # A recordings row and the placement timeline must name the SAME animal.
        # When they disagree the card generator has to pick one, and until
        # 2026-09-23 it silently picked the placement -- which named the animal
        # that had already been pulled from B1 before the 2026-08-26 run. The
        # row is the operator's explicit word and needs no timestamp, so a
        # disagreement is a manifest bug and is reported rather than resolved.
        for a in self.animals:
            for r in a.recordings:
                if not r.position or r.date is None:
                    continue
                held = self.animal_at(r.position, moment_from_base(r.base) or r.date)
                if held is not None and held.animal_id != a.animal_id:
                    problems.append(
                        f"{a.animal_id}: recordings row puts it at {r.position} on "
                        f"{r.date} ({r.base}), but placements put {held.animal_id} "
                        f"there. One of the two is wrong.")
        return problems

    def to_spec(self):
        """The CohortSpec this manifest describes. THE ONLY place that mapping lives.

        BACKWARD COMPATIBILITY IS THE FIRST BRANCH. A manifest with no `ports:`
        key -- which is every manifest written before 2026-09-14 -- returns
        exactly `CohortSpec(roles=...)`, the same object the old code built, so
        the whole historical corpus keeps producing identical sites. Proven in
        tests/test_cohortspec_compat.py.
        """
        from core import criteria as C

        uniform = not self.ports and not self.role_sites
        if uniform:
            return C.CohortSpec(roles=tuple(self.roles))

        real = self.real_channels or C.CHIP_REAL_CHANNELS
        no_floor = self.floor.strip().lower() == "none"
        if no_floor and not self.floor_reason.strip():
            raise C.LayoutError(
                f"cohort {self.cohort_id!r} declares floor: none but gives no "
                "floor_reason. A missing control must say why it is missing.")

        def chip(base: int):
            if self.role_sites:
                # explicit sites: the unipolar case. Offsets are absolute within
                # the chip, so a second chip on a splitter shifts them by base-1.
                rs = tuple((r, base - 1 + n) for r, n in self.role_sites.items())
            else:
                rs = tuple((r, base + k) for k, r in enumerate(self.roles))
            return C.ChipSpec(
                base=base, role_sites=rs, real_channels=real,
                floor=() if no_floor else None,
                floor_reason=self.floor_reason if no_floor else "")

        ports = self.ports or {p: 2 for p in C.PORTS_DEFAULT}
        specs = []
        for port in sorted(ports):
            n_chips = ports[port]
            if n_chips not in (1, 2):
                raise C.LayoutError(
                    f"port {port} declares {n_chips} chips. An XDAQ port carries "
                    "one, or two behind a C3442 splitter -- nothing else.")
            bases = C.SLOT_BASES_DEFAULT[:n_chips]
            specs.append(C.PortSpec(port=port,
                                    chips=tuple(chip(b) for b in bases)))
        return C.CohortSpec(roles=tuple(self.roles), ports_spec=tuple(specs))

    @classmethod
    def from_obj(cls, obj: dict[str, Any]) -> "Cohort":
        c = cls(
            cohort_id=str(obj.get("cohort_id", "") or ""),
            title=str(obj.get("title", "") or ""),
            description=str(obj.get("description", "") or ""),
            project_id=str(obj.get("project_id", "") or ""),
            roles=tuple(obj.get("roles", ("eeg", "emg")) or ("eeg", "emg")),
            ports={str(k).upper(): int(v)
                   for k, v in (obj.get("ports") or {}).items()},
            role_sites={str(k): int(v)
                        for k, v in (obj.get("role_sites") or {}).items()},
            real_channels=int(obj.get("real_channels", 0) or 0),
            floor=str(obj.get("floor", "") or ""),
            floor_reason=str(obj.get("floor_reason", "") or ""),
            criterion=str(obj.get("criterion", "slope") or "slope"),
            notes=str(obj.get("notes", "") or ""),
        )
        c.animals = [Animal.from_obj(a) for a in obj.get("animals", []) or []]
        c.recordings = [RecordingRef.from_obj(r) for r in obj.get("recordings", []) or []]
        # A cohort-level project_id is inherited by animals that do not set one.
        for a in c.animals:
            if not a.project_id:
                a.project_id = c.project_id
            if not a.batch_id:
                a.batch_id = c.cohort_id
        return c


# --------------------------------------------------------------------------- #
# small coercions
# --------------------------------------------------------------------------- #

def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    f = _as_float(value)
    return None if f is None else int(round(f))


NOT_RECORDED = "not recorded"


def show(value: Any, unit: str = "", *, decimals: int | None = None) -> str:
    """Render a value for a card. A missing value SAYS SO rather than vanishing."""
    if value is None or value == "":
        return NOT_RECORDED
    if isinstance(value, float) and decimals is not None:
        return f"{value:.{decimals}f}{unit}"
    if isinstance(value, _dt.date):
        return value.isoformat()
    return f"{value}{unit}"


def iter_timeline(animal: Animal) -> Iterable[tuple[_dt.date, str, str]]:
    """(date, kind, label) for every dated event, sorted. Drives the timeline strip."""
    events: list[tuple[_dt.date, str, str]] = []
    if animal.arrival_date:
        events.append((animal.arrival_date, "arrival", "arrival"))
    if animal.surgery_date:
        events.append((animal.surgery_date, "surgery", "surgery"))
    if animal.tether_date:
        events.append((animal.tether_date, "tether", "tethered"))
    for p in animal.placements:
        if p.from_date and p.tether_arm:
            events.append((p.from_date, "tether-arm", f"arm {p.tether_arm}"))
    for r in animal.recordings:
        if r.date:
            events.append((r.date, "recording", r.base))
    for i in animal.interventions:
        if i.start:
            events.append((i.start, "intervention", i.kind))
    if animal.sacrifice_date:
        events.append((animal.sacrifice_date, "sacrifice", "sacrifice"))
    if animal.sampling_date:
        events.append((animal.sampling_date, "sampling", "sampling"))
    return sorted(events, key=lambda e: e[0])

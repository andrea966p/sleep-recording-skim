#!/usr/bin/env python3
"""layout.py -- what the rig is set up as right now, and whether that is true.

A run declares a layout: one recording setting shared by every animal, plus which
ports carry a C3442 SPI splitter. From that this module derives the slot grid,
the strip's keep-set, the cohort spec for QC, and -- the point of the whole
exercise -- HOW MANY CHANNELS EACH PORT SHOULD ENUMERATE.

    expected on a port = (2 if splitter else 1) * headstage.slots_per_chip

Allego already reports what each port actually enumerated. Comparing the two
turns a wrong declaration from something discovered after the animals are done
into a refusal before the recording starts. That check is the reason this file
exists; everything else here is bookkeeping.

SLOT NAMES: `A1`/`A2` on a split port, bare `A` on an unsplit one (Andrea's
choice, 2026-09-13, over the alternative of always A1..D2).

🔴 THE BARE LETTER MUST NEVER REACH THE ANALYSIS SIDE. `cards/ladder.py`'s
find_processed and figs_common.pos_to_file both parse `position[1]` to build
`portA-slot1`, and CohortSpec.positions() always yields A1..D2. So a single-slot
port is `A` to the operator and `A1` to everything downstream. `to_position` is
the one place that translation happens, and `run.json` records both names so
nobody has to infer the mapping later.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import presets as P

PORTS = P.PORTS
SLOT_BASES = (1, 33)          # site of the first channel of each chip on a port


class LayoutError(ValueError):
    """A rig declaration that cannot be honoured. Never guessed around."""


@dataclass(frozen=True)
class RigLayout:
    """One recording setting, and which ports are split."""
    setting: P.RecordingSetting
    headstage: P.Headstage
    splitters: dict                      # port -> bool
    ports_used: tuple = PORTS            # ports the operator is using at all

    # ---- slots ---------------------------------------------------------- #
    def slots_on(self, port: str) -> list[str]:
        """Operator-facing slot names for one port. `A1`,`A2` or bare `A`."""
        if port not in self.ports_used:
            return []
        return [f"{port}1", f"{port}2"] if self.splitters.get(port) else [port]

    @property
    def slots(self) -> list[str]:
        return [s for p in PORTS for s in self.slots_on(p)]

    @staticmethod
    def to_position(slot: str) -> str:
        """Operator slot name -> the analysis side's position. `A` -> `A1`.

        THE ONLY TRANSLATION POINT. See the module docstring for why it exists.
        """
        if not slot or slot[0] not in PORTS:
            raise LayoutError(f"{slot!r} does not name a port on this rig")
        return slot if len(slot) > 1 else f"{slot}1"

    @staticmethod
    def base_of(slot: str) -> int:
        """The site number the animal's chip starts at: 1 for slot 1, 33 for 2."""
        pos = RigLayout.to_position(slot)
        idx = int(pos[1:])
        if idx not in (1, 2):
            raise LayoutError(f"{slot!r}: a port has at most two slots")
        return SLOT_BASES[idx - 1]

    # ---- channels ------------------------------------------------------- #
    def labels_for_slot(self, slot: str) -> list[str]:
        if slot not in self.slots:
            raise LayoutError(
                f"{slot!r} is not a slot in this layout; it has "
                f"{', '.join(self.slots)}")
        return self.setting.labels_for(slot[0], self.base_of(slot))

    def labels(self, occupied: list[str] | None = None) -> list[str]:
        """Every label to keep, sorted into file order.

        `strip_channels` refuses a keep set whose type sections are out of order,
        so this sorts by (port, site) rather than by slot.
        """
        slots = self.slots if occupied is None else list(occupied)
        unknown = [s for s in slots if s not in self.slots]
        if unknown:
            raise LayoutError(
                f"unknown slot(s) {unknown}; this layout has "
                f"{', '.join(self.slots)}")
        out = []
        for s in slots:
            out.extend(self.labels_for_slot(s))
        return sorted(set(out), key=lambda l: (l.split("/")[0], int(l.split("/")[1])))

    def role_of(self, slot: str, label: str) -> str | None:
        return self.setting.role_of(slot[0], self.base_of(slot), label)

    # ---- the enumeration check ------------------------------------------ #
    def expected_channels(self, port: str) -> int:
        if port not in self.ports_used:
            return 0
        chips = 2 if self.splitters.get(port) else 1
        return chips * self.headstage.slots_per_chip

    def check(self, enumerated: dict) -> dict:
        """Compare the declaration against what Allego actually enumerated.

        Returns {ok, ports: {port: {...}}, problems: [...]}. A problem is a
        refusal, not a warning: declaring the rig wrong means the strip keeps the
        wrong channels, and that is found out after the animals are done.
        """
        ports, problems = {}, []

        # A combination nobody has ever recorded should not be discovered by
        # trusting it. Say so and let a human confirm it once.
        if not self.headstage.splitter_verified and any(
                self.splitters.get(p) for p in self.ports_used):
            split = ", ".join(p for p in self.ports_used if self.splitters.get(p))
            problems.append(
                f"a splitter carrying two {self.headstage.label} headstages "
                f"(ports {split}) has never been recorded on this rig. Expected "
                f"{2 * self.headstage.slots_per_chip} channels at bases 1 and 33, "
                "UNVERIFIED. Set `splitter_verified: true` on the headstage once "
                "someone has seen it enumerate.")

        for p in PORTS:
            want = self.expected_channels(p)
            got = int(enumerated.get(p, 0) or 0)
            used = p in self.ports_used
            row = {"expected": want, "enumerated": got, "used": used, "ok": True}
            if not used:
                row["ok"] = True
            elif got == 0:
                row["ok"] = False
                problems.append(
                    f"port {p}: nothing is connected (Allego enumerates 0 "
                    f"channels), but the layout expects {want}.")
            elif got != want:
                row["ok"] = False
                chips = 2 if self.splitters.get(p) else 1
                problems.append(
                    f"port {p}: declared {'a splitter' if chips == 2 else 'no splitter'} "
                    f"with {self.headstage.label}, which enumerates {want} "
                    f"channels -- but Allego reports {got}. Either the splitter "
                    "state is wrong or the headstage is not the one declared.")
            ports[p] = row
        return {"ok": not problems, "ports": ports, "problems": problems}

    # ---- what QC needs -------------------------------------------------- #
    def cohort_ports(self) -> dict:
        """`{port: chips}` for the cohort manifest's `ports:` key."""
        return {p: (2 if self.splitters.get(p) else 1) for p in self.ports_used}

    def cohort_extras(self) -> dict:
        """The manifest keys a non-contiguous layout needs. Empty for bipolar."""
        if self.setting.contiguous_from_one:
            return {}
        return {"role_sites": dict(self.setting.roles),
                "real_channels": self.headstage.real_channels,
                "floor": "none" if not self.setting.qc_applies else "",
                "floor_reason": self.setting.qc_reason}

    def to_dict(self) -> dict:
        return {"setting": self.setting.name,
                "setting_label": self.setting.label,
                "headstage": self.headstage.name,
                "headstage_label": self.headstage.label,
                "splitters": dict(self.splitters),
                "ports_used": list(self.ports_used),
                "qc": self.setting.qc,
                "slots": self.slots,
                "expected_channels": {p: self.expected_channels(p) for p in PORTS}}


def resolve(cfg: P.Config, setting: str, splitters: dict,
            ports_used=None) -> RigLayout:
    """Build a layout from what the operator declared. Refuses on anything odd."""
    s = cfg.setting(setting)
    hs = cfg.headstage(s.headstage)
    spl = {str(k).upper(): bool(v) for k, v in (splitters or {}).items()}
    unknown = [k for k in spl if k not in PORTS]
    if unknown:
        raise LayoutError(f"unknown port(s) {unknown}; this rig has {', '.join(PORTS)}")
    # `ports_used or PORTS` was WRONG: an empty tuple is falsy, so declaring NO
    # ports in use silently expanded to all four -- and with every port then
    # "in use", the enumeration check compared against ports nobody had touched.
    # Absent (None) means all; empty means empty, and empty is refused below.
    used = tuple(str(p).upper()
                 for p in (PORTS if ports_used is None else ports_used))
    bad = [p for p in used if p not in PORTS]
    if bad:
        raise LayoutError(f"unknown port(s) {bad}; this rig has {', '.join(PORTS)}")
    if not used:
        raise LayoutError("no port is in use, so this layout records nothing")
    return RigLayout(setting=s, headstage=hs,
                     splitters={p: spl.get(p, False) for p in PORTS},
                     ports_used=used)


def from_template(cfg: P.Config, name: str) -> RigLayout:
    t = cfg.template(name)
    return resolve(cfg, t.setting, t.splitters)


if __name__ == "__main__":
    cfg = P.load()
    for name in cfg.templates:
        lay = from_template(cfg, name)
        print(f"\n{name}  ({lay.setting.label})")
        print(f"  slots    : {', '.join(lay.slots)}")
        print(f"  keep     : {len(lay.labels())} ch  {', '.join(lay.labels()[:8])}"
              f"{' ...' if len(lay.labels()) > 8 else ''}")
        print(f"  expects  : " + "  ".join(
            f"{p}={lay.expected_channels(p)}" for p in PORTS))

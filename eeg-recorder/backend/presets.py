#!/usr/bin/env python3
"""presets.py -- who records, and which channels their layout uses.

A preset answers one question: given a rig layout and which slots are occupied,
WHICH CHANNELS should survive the strip? It answers in SITE LABELS (`A/1`,
`D/33`), never in file indices, because indices are not portable between
recordings on this rig -- `allego_0__uid0904-08-55-25` has 134 channels with
32-channel ports, so index 160 does not exist in it and index 128 is an aux
channel rather than an electrode. `convert.strip_channels` resolves labels
against each file's own biointerface_map and refuses on any miss.

Two preset shapes:
  role-based  (`roles: {eeg: 1, emg: 2}`) -- site = slot base + role offset.
              Eight slots, two animals per 64-channel splitter port.
  site-based  (`sites: [18..23]`)         -- site = slot base + site, roles unnamed.
              Four slots, one animal per 32-channel port.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG = Path(os.environ.get(
    "EEG_RECORDER_CONFIG",
    Path(__file__).resolve().parent.parent / "config" / "users.yaml"))


class PresetError(ValueError):
    """A preset or slot request that cannot be honoured. Never guessed around."""


@dataclass(frozen=True)
class Preset:
    name: str
    label: str
    slots: dict                       # slot -> {port, base}
    roles: dict = field(default_factory=dict)    # role -> site offset
    sites: tuple = ()                 # bare site offsets, when roles are unnamed
    with_gpio: bool = False

    @property
    def slot_names(self) -> list[str]:
        return list(self.slots)

    @property
    def channels_per_animal(self) -> int:
        return len(self.roles) if self.roles else len(self.sites)

    def labels_for_slot(self, slot: str) -> list[str]:
        """The site labels this slot contributes, in file order."""
        if slot not in self.slots:
            raise PresetError(
                f"{slot!r} is not a slot in preset {self.name!r}; "
                f"slots are {', '.join(self.slots)}")
        s = self.slots[slot]
        offsets = (sorted(self.roles.values()) if self.roles else list(self.sites))
        return [f"{s['port']}/{s['base'] + o}" for o in offsets]

    def role_of(self, slot: str, label: str) -> str | None:
        """Which role a label plays, or None for a site-based preset."""
        if not self.roles:
            return None
        s = self.slots[slot]
        for role, off in self.roles.items():
            if label == f"{s['port']}/{s['base'] + off}":
                return role
        return None

    def labels(self, occupied: list[str] | None = None) -> list[str]:
        """Every label to keep, for the occupied slots, in file order.

        Sorted by (port, site) so the keep set matches the order the channels
        appear in the file -- `strip_channels` refuses a keep set whose sections
        are out of order, and an unsorted preset would trip that for no reason.
        """
        slots = list(self.slots) if occupied is None else list(occupied)
        unknown = [s for s in slots if s not in self.slots]
        if unknown:
            raise PresetError(
                f"unknown slot(s) {unknown} for preset {self.name!r}; "
                f"slots are {', '.join(self.slots)}")
        out = []
        for slot in slots:
            out.extend(self.labels_for_slot(slot))
        return sorted(set(out), key=lambda l: (l.split("/")[0], int(l.split("/")[1])))


@dataclass(frozen=True)
class Config:
    users: dict
    presets: dict
    recording_types: tuple
    nas_share: str
    nas_root: str

    def preset(self, name: str) -> Preset:
        if name not in self.presets:
            raise PresetError(
                f"unknown preset {name!r}; known presets are "
                f"{', '.join(self.presets)}")
        return self.presets[name]

    def preset_for_user(self, user: str) -> Preset:
        if user not in self.users:
            raise PresetError(
                f"unknown user {user!r}; known users are {', '.join(self.users)}")
        return self.preset(self.users[user]["default_preset"])


def load(path: Path | str | None = None) -> Config:
    p = Path(path) if path else CONFIG
    raw = yaml.safe_load(p.read_text())

    presets = {}
    for name, d in (raw.get("presets") or {}).items():
        roles = dict(d.get("roles") or {})
        sites = tuple(d.get("sites") or ())
        if bool(roles) == bool(sites):
            raise PresetError(
                f"preset {name!r} must define EXACTLY ONE of `roles` or `sites`; "
                "a preset with both is ambiguous about what each channel is, and "
                "a preset with neither selects nothing")
        slots = d.get("slots") or {}
        if not slots:
            raise PresetError(f"preset {name!r} defines no slots")
        for slot, s in slots.items():
            if "port" not in s or "base" not in s:
                raise PresetError(
                    f"preset {name!r} slot {slot!r} needs both `port` and `base`")
        presets[name] = Preset(name=name, label=d.get("label", name), slots=slots,
                               roles=roles, sites=sites,
                               with_gpio=bool(d.get("with_gpio", False)))

    users = raw.get("users") or {}
    for u, d in users.items():
        dp = d.get("default_preset")
        if dp not in presets:
            raise PresetError(
                f"user {u!r} names default_preset {dp!r}, which is not defined")

    nas = raw.get("nas") or {}
    return Config(users=users, presets=presets,
                  recording_types=tuple(raw.get("recording_types") or ()),
                  nas_share=nas.get("share", "SKIM_DATA"),
                  nas_root=nas.get("root", "03_Data_Mouse"))


if __name__ == "__main__":
    cfg = load()
    print(f"users:   {', '.join(cfg.users)}")
    print(f"types:   {', '.join(cfg.recording_types)}")
    print(f"nas:     {cfg.nas_share}/{cfg.nas_root}")
    for name, p in cfg.presets.items():
        labs = p.labels()
        print(f"\n{name}  ({p.label})")
        print(f"  {len(p.slot_names)} slots x {p.channels_per_animal} ch "
              f"= {len(labs)} channels, gpio={p.with_gpio}")
        for slot in p.slot_names:
            per = p.labels_for_slot(slot)
            roles = [p.role_of(slot, l) for l in per]
            shown = ", ".join(f"{l}" + (f" ({r})" if r else "") for l, r in zip(per, roles))
            print(f"    {slot:3s}  {shown}")

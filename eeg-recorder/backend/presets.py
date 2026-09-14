#!/usr/bin/env python3
"""presets.py -- the rig configuration, in three layers of decreasing stability.

    headstages          chip physics. YAML only. Changes when hardware changes.
    recording_settings  which site carries which signal. Guided form in the UI.
    layout_templates    one-click starting points. Freely savable.

WHY THREE. Each is a different kind of truth with a different blast radius. A
wrong `slots_per_chip` silently breaks the enumeration check that every other
guard leans on; a wrong role offset silently records the wrong channels; a wrong
template only costs a click. They get correspondingly different editing rights.

🔑 A RUN HAS ONE RECORDING SETTING, SHARED BY EVERY ANIMAL. Andrea, 2026-09-14:
"there will never be mice connected to the rig with different configuration at
the same time. When someone records, the mice have all the same settings. What
changes is just the amount of mice connected."

So what varies between runs is exactly two things: which ports carry a C3442 SPI
splitter (2 chips, 64 enumerated channels; without one, 1 chip and 32), and which
slots hold an animal. `layout.py` resolves those into slots and keep-labels.

CHANNELS ARE ALWAYS SITE LABELS, NEVER FILE INDICES. A keep list written as
indices is not portable: allego_0__uid0904-08-55-25 has 134 channels with
32-channel ports, so index 160 does not exist in it and index 128 is an aux
channel rather than an electrode. `convert.strip_channels` resolves labels
against each file's own biointerface_map and refuses on any miss.

Site numbering: `D/n` is native index n-1. The second animal on a splitter port
starts at slot 32, so its EEG is /33 and not /29 -- the "+32 trap" in
02-procedures/eight-mouse-acquisition-setup.md section 6.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CONFIG = Path(os.environ.get(
    "EEG_RECORDER_CONFIG",
    Path(__file__).resolve().parent.parent / "config" / "users.yaml"))

# 🔑 TWO FILES, AND THE SERVICE ONLY EVER WRITES THE SECOND.
#
# `users.yaml` is curated by hand and carries the provenance this project runs
# on: which recording the layout was measured from, why the unipolar floor is
# absent, what the 2026-08-05 page says about ground-tied inputs. A machine
# rewriting it would strip every one of those comments, because no YAML dumper
# in the standard library round-trips them.
#
# So additions made through the web form land in `custom.yaml`, which is
# machine-written and expected to be comment-free. The curated file stays
# readable, a UI bug cannot corrupt it, and `git diff` shows at a glance what a
# person wrote versus what a form generated.
CUSTOM = Path(os.environ.get(
    "EEG_RECORDER_CUSTOM",
    Path(__file__).resolve().parent.parent / "config" / "custom.yaml"))

PORTS = ("A", "B", "C", "D")


class PresetError(ValueError):
    """A configuration that cannot be honoured. Never guessed around."""


@dataclass(frozen=True)
class Headstage:
    """One amplifier chip. Physics, not preference."""
    name: str
    label: str
    slots_per_chip: int      # native slots it consumes in the RHD2000 stream
    real_channels: int       # ...of which this many are real amplifiers
    bipolar_in_hardware: bool = True
    splitter_verified: bool = True
    source: str = ""


@dataclass(frozen=True)
class RecordingSetting:
    """Which site number carries which signal, within one chip."""
    name: str
    label: str
    headstage: str
    roles: dict              # role -> site offset within the chip
    qc: str = "auto"         # "auto" = this project's ladder applies
    qc_reason: str = ""
    seen_in: str = ""

    @property
    def qc_applies(self) -> bool:
        """Whether core/criteria.py's verdict ladder means anything here.

        False is not a waiver. It says the layout was never judgeable by this
        project's criterion, which is a different claim from "we chose to skip
        the check", and the run record keeps them apart.
        """
        return self.qc == "auto"

    @property
    def sites(self) -> tuple[int, ...]:
        return tuple(sorted(self.roles.values()))

    @property
    def contiguous_from_one(self) -> bool:
        """True when the floor rule `base+n .. base+real` describes this layout."""
        return self.sites == tuple(range(1, len(self.roles) + 1))

    def labels_for(self, port: str, base: int) -> list[str]:
        """Site labels for one animal on `port`, whose chip starts at `base`."""
        return [f"{port}/{base - 1 + off}" for off in self.sites]

    def role_of(self, port: str, base: int, label: str) -> str | None:
        for role, off in self.roles.items():
            if label == f"{port}/{base - 1 + off}":
                return role
        return None


@dataclass(frozen=True)
class LayoutTemplate:
    """A one-click starting point: a setting plus which ports are split."""
    name: str
    label: str
    setting: str
    splitters: dict          # port -> bool


@dataclass(frozen=True)
class Config:
    users: dict
    recording_types: tuple
    nas_share: str
    nas_root: str
    recording_type_codes: dict = field(default_factory=dict)
    headstages: dict = field(default_factory=dict)
    settings: dict = field(default_factory=dict)
    templates: dict = field(default_factory=dict)

    def type_code(self, rtype: str) -> str:
        if rtype not in self.recording_type_codes:
            raise PresetError(
                f"recording type {rtype!r} has no code in `recording_type_codes`; "
                f"known types are {', '.join(self.recording_type_codes)}")
        return self.recording_type_codes[rtype]

    def setting(self, name: str) -> RecordingSetting:
        if name not in self.settings:
            raise PresetError(
                f"unknown recording setting {name!r}; known settings are "
                f"{', '.join(self.settings) or '(none)'}")
        return self.settings[name]

    def headstage(self, name: str) -> Headstage:
        if name not in self.headstages:
            raise PresetError(
                f"unknown headstage {name!r}; known headstages are "
                f"{', '.join(self.headstages) or '(none)'}")
        return self.headstages[name]

    def template(self, name: str) -> LayoutTemplate:
        if name not in self.templates:
            raise PresetError(
                f"unknown layout {name!r}; known layouts are "
                f"{', '.join(self.templates) or '(none)'}")
        return self.templates[name]

    def template_for_user(self, user: str) -> LayoutTemplate:
        if user not in self.users:
            raise PresetError(
                f"unknown user {user!r}; known users are {', '.join(self.users)}")
        return self.template(self.users[user]["default_layout"])


CUSTOM_NAMES: set = set()


def load(path: Path | str | None = None,
         custom: Path | str | None = None) -> Config:
    """Read and VALIDATE the configuration. Refuses rather than guessing.

    Every refusal names the fix, because the person reading it is looking at the
    file. The alternative is a config that loads and produces a wrong folder or a
    wrong keep-set at 09:00 on the morning of a 24 h run.
    """
    p = Path(path) if path else CONFIG
    raw = yaml.safe_load(p.read_text()) or {}

    # Overlay the machine-written additions. A custom entry may NOT shadow a
    # curated one: silently replacing `eeg_emg` from a web form, with the
    # curated definition still sitting in the file looking authoritative, is a
    # way to record the wrong channels and never find out why.
    custom_path = Path(custom) if custom else (CUSTOM if not path else None)
    if custom_path and custom_path.exists():
        cus = yaml.safe_load(custom_path.read_text()) or {}
        for block in ("headstages", "recording_settings", "layout_templates"):
            added = cus.get(block) or {}
            clash = sorted(set(added) & set(raw.get(block) or {}))
            if clash:
                raise PresetError(
                    f"{custom_path.name} redefines {block} {clash}, which "
                    f"{p.name} already defines. A custom entry may not shadow a "
                    "curated one -- rename it, or edit the curated file by hand.")
            raw.setdefault(block, {}).update(added)
            for name in added:
                CUSTOM_NAMES.add(name)

    # ---- layer 1: headstages ------------------------------------------- #
    headstages = {}
    for name, d in (raw.get("headstages") or {}).items():
        for key in ("slots_per_chip", "real_channels"):
            if not isinstance(d.get(key), int) or d[key] <= 0:
                raise PresetError(
                    f"headstage {name!r} needs a positive integer `{key}`. It "
                    "decides how many channels a port is expected to enumerate, "
                    "and the console refuses to record when the declaration and "
                    "the hardware disagree.")
        if d["real_channels"] > d["slots_per_chip"]:
            raise PresetError(
                f"headstage {name!r} claims {d['real_channels']} real channels "
                f"in {d['slots_per_chip']} slots. A chip cannot expose more "
                "amplifiers than it occupies slots.")
        headstages[name] = Headstage(
            name=name, label=d.get("label", name),
            slots_per_chip=d["slots_per_chip"], real_channels=d["real_channels"],
            bipolar_in_hardware=bool(d.get("bipolar_in_hardware", True)),
            splitter_verified=bool(d.get("splitter_verified", True)),
            source=str(d.get("source", "")))

    # ---- layer 2: recording settings ----------------------------------- #
    settings = {}
    for name, d in (raw.get("recording_settings") or {}).items():
        roles = dict(d.get("roles") or {})
        if not roles:
            raise PresetError(f"recording setting {name!r} defines no roles")
        hs_name = d.get("headstage")
        if hs_name not in headstages:
            raise PresetError(
                f"recording setting {name!r} names headstage {hs_name!r}, which "
                f"is not defined. Known: {', '.join(headstages) or '(none)'}")
        hs = headstages[hs_name]

        offs = list(roles.values())
        if len(set(offs)) != len(offs):
            raise PresetError(
                f"recording setting {name!r}: two roles share a site number "
                f"{sorted(offs)}. One site cannot carry two signals.")
        bad = [o for o in offs if not (1 <= o <= hs.real_channels)]
        if bad:
            raise PresetError(
                f"recording setting {name!r}: site(s) {sorted(bad)} are outside "
                f"headstage {hs_name!r}'s {hs.real_channels} real channels. On a "
                "bipolar chip the slots beyond that are inactive and internally "
                "tied -- recording them captures nothing.")

        qc = str(d.get("qc", "auto")).lower()
        if qc not in ("auto", "none"):
            raise PresetError(
                f"recording setting {name!r} has qc: {qc!r}; it must be `auto` "
                "(this project's verdict ladder applies) or `none` (it does not)")

        s = RecordingSetting(
            name=name, label=d.get("label", name), headstage=hs_name, roles=roles,
            qc=qc, qc_reason=str(d.get("qc_reason", "")),
            seen_in=str(d.get("seen_in", "")))

        # The floor rule in core/criteria.py derives base+n .. base+real_channels,
        # which only describes roles sitting contiguously from site 1. Anything
        # else cannot be judged by this project's criterion, and saying so here
        # is how `unipolar_lfp` stopped demanding an impossible override on every
        # single run.
        if qc == "auto" and not s.contiguous_from_one:
            raise PresetError(
                f"recording setting {name!r} has sites {list(s.sites)}, which do "
                f"not run 1..{len(roles)}, so this project's floor model does not "
                "describe it and its QC bundle can never be computed. Declare "
                "`qc: none` with a `qc_reason`, or use contiguous sites.")
        if qc == "none" and not s.qc_reason.strip():
            raise PresetError(
                f"recording setting {name!r} declares `qc: none` but gives no "
                "`qc_reason`. A missing control must say WHY it is missing: "
                "'no characterised control exists' and 'the shape does not fit' "
                "lead the next reader to opposite actions.")
        settings[name] = s

    # ---- layer 3: layout templates -------------------------------------- #
    templates = {}
    for name, d in (raw.get("layout_templates") or {}).items():
        sname = d.get("setting")
        if sname not in settings:
            raise PresetError(
                f"layout {name!r} names recording setting {sname!r}, which is "
                f"not defined. Known: {', '.join(settings) or '(none)'}")
        spl = {str(k).upper(): bool(v) for k, v in (d.get("splitters") or {}).items()}
        unknown = [k for k in spl if k not in PORTS]
        if unknown:
            raise PresetError(
                f"layout {name!r} names port(s) {unknown}; this rig has "
                f"{', '.join(PORTS)}")
        templates[name] = LayoutTemplate(
            name=name, label=d.get("label", name), setting=sname,
            splitters={p: spl.get(p, False) for p in PORTS})

    # ---- users ---------------------------------------------------------- #
    users = raw.get("users") or {}
    for u, d in users.items():
        dl = (d or {}).get("default_layout")
        if dl not in templates:
            raise PresetError(
                f"user {u!r} names default_layout {dl!r}, which is not defined. "
                f"Known: {', '.join(templates) or '(none)'}")

    # ---- recording types ------------------------------------------------ #
    types = tuple(raw.get("recording_types") or ())
    codes = {k: str(v).strip() for k, v in (raw.get("recording_type_codes") or {}).items()}
    missing = [t for t in types if not codes.get(t)]
    if missing:
        raise PresetError(
            f"recording type(s) {missing} have no entry in `recording_type_codes`; "
            "every type must have one, because it becomes part of the NAS folder name")
    unknown = [t for t in codes if t not in types]
    if unknown:
        raise PresetError(
            f"`recording_type_codes` names {unknown}, which are not in "
            f"`recording_types` ({', '.join(types)})")

    nas = raw.get("nas") or {}
    return Config(users=users, recording_types=types,
                  nas_share=nas.get("share", "SKIM_DATA"),
                  nas_root=nas.get("root", "03_Data_Mouse"),
                  recording_type_codes=codes, headstages=headstages,
                  settings=settings, templates=templates)


if __name__ == "__main__":
    cfg = load()
    print(f"users:   {', '.join(cfg.users)}")
    print("types:   " + ", ".join(f"{t} -> {cfg.type_code(t)}"
                                  for t in cfg.recording_types))
    print(f"nas:     {cfg.nas_share}/{cfg.nas_root}")
    print("\nheadstages")
    for n, h in cfg.headstages.items():
        print(f"  {n:20s} {h.slots_per_chip} slots, {h.real_channels} real, "
              f"{'bipolar' if h.bipolar_in_hardware else 'UNIPOLAR'}")
    print("\nrecording settings")
    for n, s in cfg.settings.items():
        print(f"  {n:20s} {len(s.roles)} ch on {s.headstage}, qc={s.qc}")
        print(f"  {'':20s} {', '.join(f'{r}=/{o}' for r, o in s.roles.items())}")
    print("\nlayouts")
    for n, t in cfg.templates.items():
        split = ", ".join(p for p in PORTS if t.splitters[p]) or "none"
        print(f"  {n:20s} {t.setting}, splitters: {split}")

#!/usr/bin/env python3
"""settings_store.py -- the only thing allowed to change the configuration.

A recording setting says which site number carries which signal. Get it wrong and
the strip keeps the wrong channels, which is found out after the animals are
done. So every write goes through here, and here refuses a lot.

THE GUARDS, AND WHAT EACH IS FOR

  validate before replacing   the candidate config is loaded and validated in
                              full BEFORE the file is swapped. A config that
                              fails validation never reaches disk, so the service
                              cannot be left unable to start.
  atomic swap                 write to a temp file in the same directory, fsync,
                              os.replace. A power cut leaves either the old file
                              or the new one, never half of one.
  timestamped backup          every previous version is kept. Reverting is a copy,
                              not an archaeology exercise.
  audit log                   who changed what, when, appended never rewritten.
  no writes while recording   a change mid-run would make the run's own layout
                              disagree with the config it was created from.
  no deleting what is in use  a setting referenced by a run that has not finished
                              stays until that run does.
  headstages are not writable chip physics. A wrong slots_per_chip silently
                              breaks the enumeration check every other guard
                              leans on, and it changes only when hardware does.

🔑 CURATED CONFIG IS NEVER TOUCHED. Writes go to `custom.yaml`; `users.yaml` and
its hand-written provenance are read-only to this module. See presets.CUSTOM.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

import presets as P

NAME_RE = re.compile(r"^[a-z0-9_]{2,40}$")
AUDIT = Path(os.environ.get(
    "EEG_RECORDER_AUDIT",
    Path.home() / ".local" / "state" / "eeg-recorder" / "config-audit.jsonl"))
BACKUPS = "backups"


class SettingsRefused(ValueError):
    """A configuration change that will not be made. Always says why."""


# --------------------------------------------------------------------------- #
def _read_custom() -> dict:
    if P.CUSTOM.exists():
        return yaml.safe_load(P.CUSTOM.read_text()) or {}
    return {}


def _audit(action: str, detail: dict) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT, "a") as fh:
        fh.write(json.dumps({
            "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "action": action, **detail}) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _commit(doc: dict, action: str, detail: dict) -> None:
    """Validate the candidate, back up the current file, then swap atomically."""
    body = ("# WRITTEN BY THE RECORDING CONSOLE. Do not hand-edit while the\n"
            "# service is running -- it is replaced wholesale on every change.\n"
            "# Curated definitions and their provenance live in users.yaml.\n"
            "# Previous versions: config/backups/\n\n"
            + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))

    # 1. Would the merged configuration still load? Do this BEFORE touching the
    #    real file, or a bad form submission leaves a service that cannot start.
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tf:
        tf.write(body)
        probe = Path(tf.name)
    try:
        P.load(custom=probe)          # raises PresetError on anything invalid
    except P.PresetError as exc:
        raise SettingsRefused(str(exc)) from None
    finally:
        probe.unlink(missing_ok=True)

    # 2. Keep the version being replaced.
    if P.CUSTOM.exists():
        bdir = P.CUSTOM.parent / BACKUPS
        bdir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(P.CUSTOM, bdir / f"custom.{stamp}.yaml")

    # 3. Atomic: same filesystem, fsync, replace.
    P.CUSTOM.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(P.CUSTOM.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(body)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, P.CUSTOM)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise
    _audit(action, detail)


def _guard_quiet(store) -> None:
    """No configuration change while anything is in flight."""
    if store is None:
        return
    active = store.active()
    if active is not None:
        raise SettingsRefused(
            f"run {active.run_id} is {active.state}. The configuration cannot "
            "change while a run is in flight: the run was created against the "
            "current config and its layout would stop matching it.")
    busy = [r for r in store.list(limit=200)
            if r.state not in ("DONE", "ABORTED") and not r.state.startswith("FAILED_")]
    if busy:
        raise SettingsRefused(
            "these runs have not finished: "
            + ", ".join(f"{r.run_id} ({r.state})" for r in busy[:5])
            + ". They still have to strip and upload against the layout they "
            "were created with.")


def _in_use(store, *, setting: str = "", template: str = "") -> list[str]:
    if store is None:
        return []
    out = []
    for r in store.list(limit=500):
        if r.state in ("DONE", "ABORTED"):
            continue
        lay = getattr(r, "layout", None) or {}
        if setting and lay.get("setting") == setting:
            out.append(r.run_id)
        if template and r.preset == template:
            out.append(r.run_id)
    return sorted(set(out))


# --------------------------------------------------------------------------- #
def add_setting(*, name: str, label: str, headstage: str, roles: dict,
                qc: str = "auto", qc_reason: str = "", seen_in: str = "",
                store=None, who: str = "") -> P.Config:
    """Add a recording setting. Every field is checked before anything is written."""
    _guard_quiet(store)
    name = str(name or "").strip().lower()
    if not NAME_RE.match(name):
        raise SettingsRefused(
            f"{name!r}: lower-case letters, digits and underscore, 2 to 40 "
            "characters. It becomes a key in a config file and a value in the "
            "run record.")
    cfg = P.load()
    if name in cfg.settings:
        raise SettingsRefused(
            f"a recording setting called {name!r} already exists"
            + (" in the curated config" if name not in P.CUSTOM_NAMES else "")
            + ". Pick another name rather than shadowing it.")

    clean: dict = {}
    for role, site in (roles or {}).items():
        # The NAME rule now lives in presets.make_setting, which _commit runs via
        # a full config load -- one rule, one place. Only the site has to be a
        # number before it gets there.
        try:
            clean[str(role).strip()] = int(site)
        except (TypeError, ValueError):
            raise SettingsRefused(
                f"role {role!r} has site {site!r}, which is not a number")
    if not clean:
        raise SettingsRefused("a recording setting with no roles selects nothing")

    doc = _read_custom()
    doc.setdefault("recording_settings", {})[name] = {
        "label": str(label or name).strip() or name,
        "headstage": str(headstage),
        "roles": clean,
        "qc": str(qc or "auto").lower(),
        **({"qc_reason": qc_reason.strip()} if qc_reason.strip() else {}),
        **({"seen_in": seen_in.strip()} if seen_in.strip() else {}),
        "added_by": who or "console",
        "added_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _commit(doc, "add_setting",
            {"name": name, "who": who, "roles": clean, "headstage": headstage,
             "qc": qc})
    return P.load()


def delete_setting(name: str, *, store=None, who: str = "") -> P.Config:
    _guard_quiet(store)
    cfg = P.load()
    if name not in cfg.settings:
        raise SettingsRefused(f"no recording setting called {name!r}")
    doc = _read_custom()
    if name not in (doc.get("recording_settings") or {}):
        raise SettingsRefused(
            f"{name!r} is defined in the curated config, which this console does "
            "not edit. Its comments record where the layout was measured; remove "
            "it by hand if that is really what you want.")
    used = _in_use(store, setting=name)
    if used:
        raise SettingsRefused(
            f"{name!r} is still used by {', '.join(used)}, which have not "
            "finished. They have to strip and upload against it first.")
    for t, tpl in cfg.templates.items():
        if tpl.setting == name:
            raise SettingsRefused(
                f"layout {t!r} uses {name!r}. Delete that layout first.")
    doc["recording_settings"].pop(name)
    _commit(doc, "delete_setting", {"name": name, "who": who})
    return P.load()


def save_layout(*, name: str, label: str, setting: str, splitters: dict,
                store=None, who: str = "") -> P.Config:
    """Save the current declaration as a named template.

    Safe by construction: a template is only a reference to a validated setting
    plus four booleans, so it cannot invent a site number.
    """
    _guard_quiet(store)
    name = str(name or "").strip().lower()
    if not NAME_RE.match(name):
        raise SettingsRefused(
            f"{name!r}: lower-case letters, digits and underscore, 2 to 40 chars")
    cfg = P.load()
    if name in cfg.templates:
        raise SettingsRefused(
            f"a layout called {name!r} already exists. Pick another name.")
    cfg.setting(setting)                      # refuses if unknown
    doc = _read_custom()
    doc.setdefault("layout_templates", {})[name] = {
        "label": str(label or name).strip() or name,
        "setting": setting,
        "splitters": {p: bool((splitters or {}).get(p)) for p in P.PORTS},
        "added_by": who or "console",
        "added_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _commit(doc, "save_layout",
            {"name": name, "who": who, "setting": setting,
             "splitters": doc["layout_templates"][name]["splitters"]})
    return P.load()


def delete_layout(name: str, *, store=None, who: str = "") -> P.Config:
    _guard_quiet(store)
    cfg = P.load()
    if name not in cfg.templates:
        raise SettingsRefused(f"no layout called {name!r}")
    doc = _read_custom()
    if name not in (doc.get("layout_templates") or {}):
        raise SettingsRefused(
            f"{name!r} is defined in the curated config, which this console does "
            "not edit.")
    for u, d in cfg.users.items():
        if d.get("default_layout") == name:
            raise SettingsRefused(
                f"{name!r} is {u}'s default layout. Change that first, in "
                "users.yaml.")
    used = _in_use(store, template=name)
    if used:
        raise SettingsRefused(
            f"{name!r} is still used by {', '.join(used)}, which have not finished.")
    doc["layout_templates"].pop(name)
    _commit(doc, "delete_layout", {"name": name, "who": who})
    return P.load()


def history(limit: int = 50) -> list[dict]:
    if not AUDIT.exists():
        return []
    rows = [json.loads(l) for l in AUDIT.read_text().splitlines() if l.strip()]
    return rows[-limit:][::-1]
